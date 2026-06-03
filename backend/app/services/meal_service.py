"""Meal generation, history, and CRUD service."""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from prisma import Prisma

from app.schemas.meal import MealGenerateRequest
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class MealService:
    """Handles meal generation, retrieval, listing, and deletion."""

    # ── Generate ─────────────────────────────────────────────

    async def generate_meal(
        self,
        db: Prisma,
        redis: aioredis.Redis,
        user: dict[str, Any],
        request: MealGenerateRequest,
    ) -> dict[str, Any]:
        """Build constraints from the user profile + request, call AI, persist, and return."""
        constraints: dict[str, Any] = {
            "budget": request.budget,
            "cuisine": request.cuisine,
            "mealType": request.mealType,
            "servings": request.servings,
            "dietaryPrefs": request.dietaryPrefs or user.get("dietaryPrefs", []),
            "specificIngredients": request.specificIngredients,
            "additionalNotes": request.additionalNotes,
            "allergies": user.get("allergies", []),
            "activityLevel": user.get("activityLevel"),
        }

        ai_meal = await ai_service.generate_meal(constraints)

        # Persist to database
        meal_record = await db.meal.create(
            data={
                "userId": user["id"],
                "title": ai_meal.get("title", "Untitled Meal"),
                "description": ai_meal.get("description"),
                "cuisine": ai_meal.get("cuisine"),
                "mealType": ai_meal.get("mealType", request.mealType),
                "servings": ai_meal.get("servings", request.servings),
                "prepTime": ai_meal.get("prepTime"),
                "cookTime": ai_meal.get("cookTime"),
                "ingredients": json.dumps(ai_meal.get("ingredients", [])),
                "instructions": ai_meal.get("instructions", []),
                "calories": ai_meal.get("calories"),
                "protein": ai_meal.get("protein"),
                "carbs": ai_meal.get("carbs"),
                "fat": ai_meal.get("fat"),
                "fiber": ai_meal.get("fiber"),
                "estimatedCost": ai_meal.get("estimatedCost"),
                "budgetRange": ai_meal.get("budgetRange"),
            },
        )

        # Invalidate meal-history cache for this user
        await cache_service.delete_pattern(
            redis, cache_service.make_key("meals", user["id"], "*")
        )

        return self._to_dict(meal_record)

    # ── History (paginated) ──────────────────────────────────

    async def get_history(
        self,
        db: Prisma,
        redis: aioredis.Redis,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Return paginated meal history, checking cache first."""
        cache_key = cache_service.make_key("meals", user_id, f"p{page}s{page_size}")
        cached = await cache_service.get(redis, cache_key)
        if cached is not None:
            return cached

        skip = (page - 1) * page_size

        total = await db.meal.count(where={"userId": user_id})
        meals = await db.meal.find_many(
            where={"userId": user_id},
            order={"createdAt": "desc"},
            take=page_size,
            skip=skip,
        )

        result = {
            "meals": [self._to_dict(m) for m in meals],
            "total": total,
            "page": page,
            "pageSize": page_size,
        }

        await cache_service.set(redis, cache_key, result, ttl=300)
        return result

    # ── Single meal ──────────────────────────────────────────

    async def get_meal(
        self,
        db: Prisma,
        user_id: str,
        meal_id: str,
    ) -> dict[str, Any]:
        """Return a single meal, verifying ownership."""
        meal = await db.meal.find_unique(where={"id": meal_id})
        if meal is None or meal.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal not found",
            )
        return self._to_dict(meal)

    # ── Delete ───────────────────────────────────────────────

    async def delete_meal(
        self,
        db: Prisma,
        redis: aioredis.Redis,
        user_id: str,
        meal_id: str,
    ) -> None:
        """Delete a meal after verifying ownership, and invalidate cache."""
        meal = await db.meal.find_unique(where={"id": meal_id})
        if meal is None or meal.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal not found",
            )
        await db.meal.delete(where={"id": meal_id})
        await cache_service.delete_pattern(
            redis, cache_service.make_key("meals", user_id, "*")
        )

    # ── Private helpers ──────────────────────────────────────

    @staticmethod
    def _to_dict(meal: Any) -> dict[str, Any]:
        """Convert a Prisma Meal record to a plain dict for serialisation."""
        ingredients_raw = meal.ingredients
        if isinstance(ingredients_raw, str):
            try:
                ingredients_raw = json.loads(ingredients_raw)
            except (json.JSONDecodeError, TypeError):
                ingredients_raw = []

        return {
            "id": meal.id,
            "title": meal.title,
            "description": meal.description,
            "cuisine": meal.cuisine,
            "mealType": meal.mealType,
            "servings": meal.servings,
            "prepTime": meal.prepTime,
            "cookTime": meal.cookTime,
            "ingredients": ingredients_raw if isinstance(ingredients_raw, list) else [],
            "instructions": meal.instructions or [],
            "calories": meal.calories,
            "protein": meal.protein,
            "carbs": meal.carbs,
            "fat": meal.fat,
            "fiber": meal.fiber,
            "estimatedCost": meal.estimatedCost,
            "budgetRange": meal.budgetRange,
            "createdAt": meal.createdAt.isoformat() if meal.createdAt else None,
        }


meal_service = MealService()
