from typing import Literal

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AIAnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(description="The most likely IT incident category.")
    priority: Literal["Critical", "High", "Medium", "Low"] = Field(
        description="Suggested impact-based priority."
    )
    summary: str = Field(description="A concise summary of facts stated in the ticket.")
    likely_cause: str = Field(description="A clearly labeled, tentative likely cause.")
    suggested_resolution: list[str] = Field(
        description="Safe troubleshooting steps for an IT support person."
    )
    explanation: str = Field(
        description="Reasoning for the suggested category and priority."
    )


class PersistedAIAnalysisResult(AIAnalysisResult):
    model_config = ConfigDict(from_attributes=True)

    analyzed_at: datetime