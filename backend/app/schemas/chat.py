"""Chat / AI coach Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ChatRequest(BaseModel):
    """User message sent to the AI coach."""

    message: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"message": "What's a cheap high-protein breakfast?"}]
        }
    }


class ChatResponse(BaseModel):
    """Single chat message (user or assistant)."""

    id: str
    role: str
    content: str
    createdAt: datetime

    model_config = {"from_attributes": True}


class ChatHistoryResponse(BaseModel):
    """Paginated chat history."""

    messages: list[ChatResponse]
    total: int
