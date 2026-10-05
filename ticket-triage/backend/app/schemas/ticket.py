from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.ai_analysis import PersistedAIAnalysisResult


class TicketCreate(BaseModel):
    message: str = Field(..., min_length=10, max_length=2000)

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, value: str) -> str:
        stripped = value.strip()
        if len(stripped) < 10 or len(stripped) > 2000:
            raise ValueError("Message must be between 10 and 2000 characters")
        return stripped


class TicketAnalysisResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    message: str
    category: str
    priority: str
    urgency: bool
    confidence_score: float
    signals: list[str]
    keywords: list[str]
    is_security_escalated: bool
    created_at: datetime


class TicketListResponse(BaseModel):
    tickets: list["TicketWithAIAnalysis"]
    total: int


class TicketWithAIAnalysis(TicketAnalysisResult):
    ai_analysis: PersistedAIAnalysisResult | None = None
