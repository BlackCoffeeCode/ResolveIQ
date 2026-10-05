from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.database import Base


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        CheckConstraint(
            "category IN ('Billing', 'Technical', 'Account', 'Feature Request', 'Other', 'Security')",
            name="ck_ticket_category_valid",
        ),
        CheckConstraint(
            "priority IN ('P0', 'P1', 'P2', 'P3')",
            name="ck_ticket_priority_valid",
        ),
    )

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    priority = Column(String(5), nullable=False)
    urgency = Column(Boolean, nullable=False)
    confidence_score = Column(Float, nullable=False)
    signals = Column(JSON, nullable=False)
    keywords = Column(JSON, nullable=False)
    is_security_escalated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ai_analysis = relationship(
        "TicketAIAnalysis",
        back_populates="ticket",
        cascade="all, delete-orphan",
        uselist=False,
    )
