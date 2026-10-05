def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_ticket_valid(client):
    payload = {"message": "My credit card was charged twice and I need a refund quickly"}
    response = client.post("/tickets/analyze", json=payload)
    body = response.json()

    assert response.status_code == 200
    for field in [
        "id",
        "message",
        "category",
        "priority",
        "urgency",
        "confidence_score",
        "signals",
        "keywords",
        "is_security_escalated",
        "created_at",
    ]:
        assert field in body


def test_analyze_ticket_short_message(client):
    response = client.post("/tickets/analyze", json={"message": "short"})
    assert response.status_code == 422


def test_analyze_ticket_empty_message(client):
    response = client.post("/tickets/analyze", json={"message": ""})
    assert response.status_code == 422


def test_analyze_ticket_too_long(client):
    response = client.post("/tickets/analyze", json={"message": "a" * 2001})
    assert response.status_code == 422


def test_get_tickets_empty(client):
    response = client.get("/tickets")
    assert response.status_code == 200
    assert response.json() == {"tickets": [], "total": 0}


def test_get_tickets_after_create(client):
    client.post(
        "/tickets/analyze",
        json={"message": "My subscription payment failed and invoice is missing"},
    )

    response = client.get("/tickets")
    body = response.json()

    assert response.status_code == 200
    assert body["total"] == 1
    assert len(body["tickets"]) == 1


def test_analyze_returns_correct_schema(client):
    response = client.post(
        "/tickets/analyze",
        json={"message": "The endpoint returns 500 and crashes repeatedly"},
    )
    data = response.json()

    required_fields = {
        "id",
        "message",
        "category",
        "priority",
        "urgency",
        "confidence_score",
        "signals",
        "keywords",
        "is_security_escalated",
        "created_at",
    }
    assert required_fields.issubset(data.keys())


def test_security_ticket_escalation_via_api(client):
    response = client.post(
        "/tickets/analyze",
        json={"message": "There is a SQL injection vulnerability and unauthorized access"},
    )
    data = response.json()

    assert response.status_code == 200
    assert data["is_security_escalated"] is True
    assert data["priority"] == "P0"


def test_tickets_ordered_latest_first(client):
    client.post(
        "/tickets/analyze",
        json={"message": "First ticket for billing issue and refund request"},
    )
    client.post(
        "/tickets/analyze",
        json={"message": "Second ticket reporting timeout and performance issue"},
    )
    client.post(
        "/tickets/analyze",
        json={"message": "Third ticket about account login and password reset"},
    )

    response = client.get("/tickets")
    data = response.json()

    assert response.status_code == 200
    assert data["total"] == 3

    ids = [ticket["id"] for ticket in data["tickets"]]
    assert ids == sorted(ids, reverse=True)
