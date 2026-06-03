"""AI coach chat service with conversation history."""

from __future__ import annotations

import logging
from typing import Any

from prisma import Prisma

from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class ChatService:
    """Multi-turn conversational AI coach backed by persistent history."""

    # ── Send Message ─────────────────────────────────────────

    async def send_message(
        self,
        db: Prisma,
        user_id: str,
        message: str,
    ) -> dict[str, Any]:
        """Process a user message through the AI coach.

        Steps:
        1. Load the last 20 messages from the database for context.
        2. Build the conversation-history list.
        3. Call the AI chat completion.
        4. Persist both user and assistant messages.
        5. Return the assistant's response.
        """
        # 1. Load recent history for context
        recent_messages = await db.chatmessage.find_many(
            where={"userId": user_id},
            order={"createdAt": "asc"},
            take=20,
        )

        # 2. Build conversation history
        conversation: list[dict[str, str]] = [
            {"role": msg.role, "content": msg.content}
            for msg in recent_messages
        ]
        conversation.append({"role": "user", "content": message})

        # 3. Optionally enrich with user context
        user = await db.user.find_unique(where={"id": user_id})
        user_context: dict[str, Any] | None = None
        if user:
            user_context = {
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "dietaryPrefs": user.dietaryPrefs or [],
                "monthlyBudget": user.monthlyBudget,
            }

        # 4. Call AI
        assistant_content = await ai_service.chat_completion(
            conversation, user_context=user_context
        )

        # 5. Persist user message
        await db.chatmessage.create(
            data={
                "userId": user_id,
                "role": "user",
                "content": message,
            },
        )

        # 6. Persist assistant response
        assistant_record = await db.chatmessage.create(
            data={
                "userId": user_id,
                "role": "assistant",
                "content": assistant_content,
            },
        )

        return {
            "id": assistant_record.id,
            "role": "assistant",
            "content": assistant_content,
            "createdAt": assistant_record.createdAt.isoformat()
            if assistant_record.createdAt
            else None,
        }

    # ── History (paginated) ──────────────────────────────────

    async def get_history(
        self,
        db: Prisma,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Return paginated chat history for a user.

        Messages are ordered chronologically (oldest first) so the client
        can render them in conversation order.
        """
        skip = (page - 1) * page_size

        total = await db.chatmessage.count(where={"userId": user_id})
        messages = await db.chatmessage.find_many(
            where={"userId": user_id},
            order={"createdAt": "asc"},
            take=page_size,
            skip=skip,
        )

        return {
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "createdAt": msg.createdAt.isoformat() if msg.createdAt else None,
                }
                for msg in messages
            ],
            "total": total,
        }


chat_service = ChatService()
