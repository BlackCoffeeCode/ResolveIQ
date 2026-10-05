import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import pytest
from openai import APIConnectionError

from app.config.settings import Settings
from app.controllers.ai_analysis_controller import get_ai_analysis_service
from app.main import app
from app.schemas.ai_analysis import AIAnalysisResult
from app.services.ai_analysis_service import (
    AIAnalysisConfigurationError,
    AIAnalysisResponseError,
    AIAnalysisService,
    AIAnalysisUnavailableError,
)

VALID_ANALYSIS = {
    "category": "VPN / Network Authentication",
    "priority": "High",
    "summary": "The user cannot access the corporate VPN due to authentication errors.",
    "likely_cause": "A possible account lockout or MFA issue.",
    "suggested_resolution": [
        "Verify the user's VPN sign-in status.",
        "Check the account lock status and MFA configuration.",
        "Check whether the VPN gateway is available.",
    ],
    "explanation": "The user reports losing access to a corporate connectivity service.",
}


class FakeResponses:
    def __init__(self, output_text):
        self.output_text = output_text
        self.request = None

    def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_text=self.output_text)


class FakeClient:
    def __init__(self, responses):
        self.responses = responses


def configured_service(output_text=None):
    responses = FakeResponses(json.dumps(output_text or VALID_ANALYSIS))
    client = FakeClient(responses)
    service = AIAnalysisService(
        client_factory=lambda **kwargs: client,
        settings_provider=lambda: Settings(
            openai_api_key="test-key",
            openai_model="test-model",
        ),
    )
    return service, responses


def test_service_parses_structured_response_without_network_call():
    service, responses = configured_service()

    result = service.analyze("The corporate VPN rejects my MFA code every time")

    assert result == AIAnalysisResult(**VALID_ANALYSIS)
    assert responses.request["model"] == "test-model"
    assert responses.request["text"]["format"]["strict"] is True
    assert responses.request["input"][0]["role"] == "system"


def test_service_rejects_empty_or_short_message():
    service, _ = configured_service()

    with pytest.raises(ValueError):
        service.analyze("   ")


def test_service_reports_missing_api_key():
    service = AIAnalysisService(
        settings_provider=lambda: Settings(openai_api_key=""),
    )

    with pytest.raises(AIAnalysisConfigurationError):
        service.analyze("The corporate VPN rejects my MFA code every time")


def test_service_handles_openai_connection_failure():
    failure = APIConnectionError(
        request=httpx.Request("POST", "https://api.openai.com/v1/responses")
    )
    client = SimpleNamespace(responses=SimpleNamespace(create=Mock(side_effect=failure)))
    service = AIAnalysisService(
        client_factory=lambda **kwargs: client,
        settings_provider=lambda: Settings(openai_api_key="test-key"),
    )

    with pytest.raises(AIAnalysisUnavailableError):
        service.analyze("The corporate VPN rejects my MFA code every time")


def test_service_rejects_unexpected_model_response():
    service, _ = configured_service({"category": "Technical"})

    with pytest.raises(AIAnalysisResponseError):
        service.analyze("The corporate VPN rejects my MFA code every time")


def test_ai_endpoint_persists_separate_result_and_preserves_standard_triage(client):
    normal = client.post(
        "/tickets/analyze",
        json={"message": "The corporate VPN rejects my MFA code every time"},
    ).json()
    service, _ = configured_service()
    app.dependency_overrides[get_ai_analysis_service] = lambda: service

    response = client.post(f"/tickets/{normal['id']}/ai-analysis")

    assert response.status_code == 200
    response_body = response.json()
    assert {**VALID_ANALYSIS, "analyzed_at": response_body["analyzed_at"]} == response_body

    recent_ticket = client.get("/tickets").json()["tickets"][0]
    assert {field: recent_ticket[field] for field in normal} == normal
    assert recent_ticket["ai_analysis"]["category"] == VALID_ANALYSIS["category"]
    assert recent_ticket["ai_analysis"]["suggested_resolution"] == VALID_ANALYSIS[
        "suggested_resolution"
    ]


def test_ai_endpoint_updates_existing_analysis_for_ticket(client):
    normal = client.post(
        "/tickets/analyze",
        json={"message": "The corporate VPN rejects my MFA code every time"},
    ).json()
    first_service, _ = configured_service()
    app.dependency_overrides[get_ai_analysis_service] = lambda: first_service
    client.post(f"/tickets/{normal['id']}/ai-analysis")

    updated_analysis = {**VALID_ANALYSIS, "category": "VPN Access"}
    updated_service, _ = configured_service(updated_analysis)
    app.dependency_overrides[get_ai_analysis_service] = lambda: updated_service
    response = client.post(f"/tickets/{normal['id']}/ai-analysis")

    assert response.status_code == 200
    recent_ticket = client.get("/tickets").json()["tickets"][0]
    assert recent_ticket["ai_analysis"]["category"] == "VPN Access"
    assert recent_ticket["category"] == normal["category"]


def test_ai_endpoint_returns_not_found_for_missing_ticket(client):
    response = client.post("/tickets/999/ai-analysis")
    assert response.status_code == 404


def test_ai_endpoint_reports_missing_key_without_affecting_standard_triage(
    client, monkeypatch
):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    normal = client.post(
        "/tickets/analyze",
        json={"message": "The corporate VPN rejects my MFA code every time"},
    ).json()

    response = client.post(f"/tickets/{normal['id']}/ai-analysis")

    assert response.status_code == 503
    assert "Standard triage is still available" in response.json()["detail"]
    recent_ticket = client.get("/tickets").json()["tickets"][0]
    assert recent_ticket["ai_analysis"] is None
    assert {field: recent_ticket[field] for field in normal} == normal


def test_ai_endpoint_reports_provider_failure(client):
    class FailedService:
        def analyze(self, message):
            raise AIAnalysisUnavailableError("provider details are not exposed")

    normal = client.post(
        "/tickets/analyze",
        json={"message": "The corporate VPN rejects my MFA code every time"},
    ).json()
    app.dependency_overrides[get_ai_analysis_service] = lambda: FailedService()

    response = client.post(f"/tickets/{normal['id']}/ai-analysis")

    assert response.status_code == 503
    assert "Standard triage is still available" in response.json()["detail"]
    recent_ticket = client.get("/tickets").json()["tickets"][0]
    assert recent_ticket["ai_analysis"] is None
    assert {field: recent_ticket[field] for field in normal} == normal


def test_ai_endpoint_is_documented_in_openapi(client):
    schema = client.get("/openapi.json").json()
    operation = schema["paths"]["/tickets/{ticket_id}/ai-analysis"]["post"]

    assert "requestBody" not in operation
    assert "404" in operation["responses"]
    assert "200" in operation["responses"]
    assert "503" in operation["responses"]