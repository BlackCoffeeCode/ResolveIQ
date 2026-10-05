from sqlalchemy.orm import Session, selectinload

from app.analyzer.ticket_analyzer import TicketAnalyzer
from app.models.ai_analysis import TicketAIAnalysis
from app.models.ticket import Ticket
from app.schemas.ai_analysis import AIAnalysisResult


class TicketService:
    def __init__(self) -> None:
        self.analyzer = TicketAnalyzer()

    def analyze_and_save(self, message: str, db: Session) -> Ticket:
        analysis = self.analyzer.analyze(message)
        ticket = Ticket(
            message=message,
            category=analysis["category"],
            priority=analysis["priority"],
            urgency=analysis["urgency"],
            confidence_score=analysis["confidence_score"],
            signals=analysis["signals"],
            keywords=analysis["keywords"],
            is_security_escalated=analysis["is_security_escalated"],
        )

        try:
            db.add(ticket)
            db.commit()
            db.refresh(ticket)
            return ticket
        except Exception:
            db.rollback()
            raise

    def get_recent_tickets(self, db: Session, limit: int = 50) -> list[Ticket]:
        return (
            db.query(Ticket)
            .options(selectinload(Ticket.ai_analysis))
            .order_by(Ticket.created_at.desc(), Ticket.id.desc())
            .limit(limit)
            .all()
        )

    def get_ticket(self, ticket_id: int, db: Session) -> Ticket | None:
        return db.query(Ticket).filter(Ticket.id == ticket_id).first()

    def save_ai_analysis(
        self,
        ticket_id: int,
        analysis: AIAnalysisResult,
        db: Session,
    ) -> TicketAIAnalysis:
        record = (
            db.query(TicketAIAnalysis)
            .filter(TicketAIAnalysis.ticket_id == ticket_id)
            .one_or_none()
        )
        analysis_fields = analysis.model_dump()

        try:
            if record is None:
                record = TicketAIAnalysis(ticket_id=ticket_id, **analysis_fields)
                db.add(record)
            else:
                for field, value in analysis_fields.items():
                    setattr(record, field, value)

            db.commit()
            db.refresh(record)
            return record
        except Exception:
            db.rollback()
            raise
