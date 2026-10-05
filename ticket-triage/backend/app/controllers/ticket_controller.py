from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ticket import TicketAnalysisResult, TicketCreate, TicketListResponse
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["tickets"])
service = TicketService()


@router.post("/analyze", response_model=TicketAnalysisResult)
def analyze_ticket(payload: TicketCreate, db: Session = Depends(get_db)) -> TicketAnalysisResult:
    try:
        ticket = service.analyze_and_save(payload.message, db)
        return ticket
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("", response_model=TicketListResponse)
def get_tickets(
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
) -> TicketListResponse:
    tickets = service.get_recent_tickets(db=db, limit=limit)
    return TicketListResponse(tickets=tickets, total=len(tickets))
