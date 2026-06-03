"""AI nutrition coach chat endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.chat import ChatHistoryResponse, ChatRequest, ChatResponse
from app.services.chat_service import chat_service

router = APIRouter(prefix="/chat", tags=["AI Coach"])


# ── POST /chat/ ──────────────────────────────────────────────────────────────


@router.post(
    "/",
    response_model=ChatResponse,
    summary="Send a message to the AI nutrition coach",
)
async def send_message(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> ChatResponse:
    """Send a user message to the AI coach and receive a contextual
    nutrition / budget / meal-planning response.  Both the user message
    and the assistant reply are persisted to the chat history.
    """

    result = await chat_service.send_message(
        user=current_user,
        request=body,
        db=db,
    )
    return result


# ── GET /chat/history ─────────────────────────────────────────────────────────


@router.get(
    "/history",
    response_model=ChatHistoryResponse,
    summary="Get chat history (paginated)",
)
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=50, ge=1, le=200, description="Messages per page"),
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> ChatHistoryResponse:
    """Return the authenticated user's chat history, ordered oldest → newest,
    with pagination.
    """

    result = await chat_service.get_history(
        user_id=current_user.id,
        page=page,
        page_size=pageSize,
        db=db,
    )
    return result
