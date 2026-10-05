from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ai_analysis import PersistedAIAnalysisResult
from app.services.ticket_service import TicketService
from app.services.ai_analysis_service import (
    AIAnalysisConfigurationError,
    AIAnalysisResponseError,
    AIAnalysisService,
    AIAnalysisUnavailableError,
)

router = APIRouter(prefix="/tickets", tags=["AI analysis"])
ticket_service = TicketService()


def get_ai_analysis_service() -> AIAnalysisService:
    return AIAnalysisService()


@router.post(
    "/{ticket_id}/ai-analysis",
    response_model=PersistedAIAnalysisResult,
    responses={
        404: {"description": "Ticket does not exist."},
        502: {"description": "AI provider returned an unusable response."},
        503: {"description": "AI analysis is not configured or is unavailable."},
    },
)
def analyze_ticket_with_ai(
    ticket_id: int,
    db: Session = Depends(get_db),
    service: AIAnalysisService = Depends(get_ai_analysis_service),
) -> PersistedAIAnalysisResult:
    ticket = ticket_service.get_ticket(ticket_id, db)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")

    try:
        analysis = service.analyze(ticket.message)
        return ticket_service.save_ai_analysis(ticket.id, analysis, db)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except AIAnalysisConfigurationError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "AI analysis is unavailable because the backend OpenAI configuration "
                "is missing or invalid. Standard triage is still available."
            ),
        ) from exc
    except AIAnalysisUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail="AI analysis is currently unavailable. Standard triage is still available.",
        ) from exc
    except AIAnalysisResponseError as exc:
        raise HTTPException(
            status_code=502,
            detail="AI analysis returned an unexpected response. Standard triage is still available.",
        ) from exc