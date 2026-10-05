from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import relationship

from app.database import Base


class TicketAIAnalysis(Base):
    __tablename__ = "ticket_ai_analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ticket_id = Column(
        Integer,
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    category = Column(String(120), nullable=False)
    priority = Column(String(20), nullable=False)
    summary = Column(Text, nullable=False)
    likely_cause = Column(Text, nullable=False)
    suggested_resolution = Column(JSON, nullable=False)
    explanation = Column(Text, nullable=False)
    analyzed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    ticket = relationship("Ticket", back_populates="ai_analysis")