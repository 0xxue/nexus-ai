"""QA request/response schemas."""

from pydantic import BaseModel, Field
from typing import Optional


class QARequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="User question")
    conversation_id: Optional[str] = Field(None, description="For multi-turn conversations")


class QAResponse(BaseModel):
    answer: str
    sources: list[str] = []
    chart: Optional[dict] = None
    confidence: float = Field(0.0, ge=0, le=1)
    trace_id: str = ""
