"""Celery tasks for asynchronous meal generation.

Because Celery workers are synchronous, all async database / AI calls are
wrapped with ``asyncio.run()``.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task 1: Generate a full weekly meal plan (7 days × 3 meals)
# ---------------------------------------------------------------------------


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_weekly_meal_plan(
    self: Any,
    user_id: str,
    constraints: dict,
) -> dict:
    """Generate a 7-day meal plan with 3 meals per day.

    Args:
        user_id: UUID of the user requesting the plan.
        constraints: Dict with optional keys ``budget``, ``dietType``,
            ``calories``, ``allergies``, ``cuisinePrefs``, etc.

    Returns:
        A summary dict with ``plan_id``, ``days_generated``, and ``total_cost``.
    """
    try:
        return asyncio.run(
            _generate_weekly_meal_plan_async(user_id, constraints)
        )
    except Exception as exc:
        logger.exception("generate_weekly_meal_plan failed for user=%s", user_id)
        raise self.retry(exc=exc)


async def _generate_weekly_meal_plan_async(
    user_id: str,
    constraints: dict,
) -> dict:
    """Async implementation of the weekly meal plan generator."""

    from openai import AsyncOpenAI
    from prisma import Prisma

    from app.core.config import settings

    db = Prisma()
    await db.connect()
    try:
        user = await db.user.find_unique(where={"id": user_id})
        if user is None:
            return {"error": "User not found", "user_id": user_id}

        budget = constraints.get("budget", user.dailyBudget or 300)
        diet_type = constraints.get("dietType", user.dietPreference or "balanced")
        calories = constraints.get("calories", 2000)

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = (
            f"Generate a 7-day meal plan with 3 meals per day (Breakfast, Lunch, Dinner).\n"
            f"Daily budget: ₹{budget}. Diet type: {diet_type}. Daily calories: ~{calories} kcal.\n"
            f"For each meal provide: name, type, calories, protein(g), carbs(g), fat(g), "
            f"cost(₹), and ingredients list.\n"
            f"Return valid JSON with structure: "
            f'{{ "days": [ {{ "date_offset": 0, "meals": [ {{ "type": "Breakfast", '
            f'"name": "...", "calories": 300, "protein": 15.0, "carbs": 40.0, '
            f'"fat": 10.0, "cost": 50.0, "ingredients": ["item1", "item2"] }} ] }} ] }}'
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content or "{}"
        plan_data = json.loads(raw_content)
        days = plan_data.get("days", [])

        total_cost = 0.0
        days_generated = 0

        for day_info in days:
            meals_in_day = day_info.get("meals", [])
            day_cost = sum(m.get("cost", 0) for m in meals_in_day)
            day_cals = sum(m.get("calories", 0) for m in meals_in_day)
            day_protein = sum(m.get("protein", 0) for m in meals_in_day)
            day_carbs = sum(m.get("carbs", 0) for m in meals_in_day)
            day_fat = sum(m.get("fat", 0) for m in meals_in_day)

            meal_plan = await db.mealplan.create(
                data={
                    "userId": user_id,
                    "totalCost": day_cost,
                    "totalCals": day_cals,
                    "totalProtein": day_protein,
                    "totalCarbs": day_carbs,
                    "totalFat": day_fat,
                }
            )

            for meal_info in meals_in_day:
                await db.meal.create(
                    data={
                        "mealPlanId": meal_plan.id,
                        "type": meal_info.get("type", "Lunch"),
                        "name": meal_info.get("name", "Unnamed Meal"),
                        "calories": int(meal_info.get("calories", 0)),
                        "protein": float(meal_info.get("protein", 0)),
                        "carbs": float(meal_info.get("carbs", 0)),
                        "fat": float(meal_info.get("fat", 0)),
                        "cost": float(meal_info.get("cost", 0)),
                        "ingredients": meal_info.get("ingredients", []),
                    }
                )

            total_cost += day_cost
            days_generated += 1

        return {
            "user_id": user_id,
            "days_generated": days_generated,
            "total_cost": total_cost,
            "status": "completed",
        }

    finally:
        await db.disconnect()


# ---------------------------------------------------------------------------
# Task 2: Generate meal suggestions from a list of ingredients
# ---------------------------------------------------------------------------


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_meal_suggestions_from_ingredients(
    self: Any,
    user_id: str,
    ingredients: list[str],
) -> dict:
    """Generate 3-5 meal suggestions using the provided ingredients.

    Args:
        user_id: UUID of the requesting user.
        ingredients: List of ingredient names the user has on hand.

    Returns:
        A dict with ``suggestions`` (list of meal dicts) and ``count``.
    """
    try:
        return asyncio.run(
            _generate_suggestions_async(user_id, ingredients)
        )
    except Exception as exc:
        logger.exception(
            "generate_meal_suggestions_from_ingredients failed for user=%s",
            user_id,
        )
        raise self.retry(exc=exc)


async def _generate_suggestions_async(
    user_id: str,
    ingredients: list[str],
) -> dict:
    """Async implementation of ingredient-based meal suggestion."""

    from openai import AsyncOpenAI
    from prisma import Prisma

    from app.core.config import settings

    db = Prisma()
    await db.connect()
    try:
        user = await db.user.find_unique(where={"id": user_id})
        if user is None:
            return {"error": "User not found", "user_id": user_id}

        diet_pref = user.dietPreference or "any"
        ingredients_str = ", ".join(ingredients)

        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        prompt = (
            f"I have these ingredients: {ingredients_str}.\n"
            f"Suggest 3-5 meals I can make. Diet preference: {diet_pref}.\n"
            f"For each meal provide: name, type (Breakfast/Lunch/Dinner/Snack), "
            f"calories, protein(g), carbs(g), fat(g), estimated cost(₹), "
            f"and the subset of given ingredients used.\n"
            f"Return valid JSON with structure: "
            f'{{ "suggestions": [ {{ "name": "...", "type": "Lunch", '
            f'"calories": 400, "protein": 20.0, "carbs": 50.0, "fat": 12.0, '
            f'"cost": 80.0, "ingredients": ["item1"] }} ] }}'
        )

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content or "{}"
        result = json.loads(raw_content)
        suggestions = result.get("suggestions", [])

        # Persist each suggestion as a MealPlan + Meal for reference
        for suggestion in suggestions:
            meal_plan = await db.mealplan.create(
                data={
                    "userId": user_id,
                    "totalCost": float(suggestion.get("cost", 0)),
                    "totalCals": int(suggestion.get("calories", 0)),
                    "totalProtein": float(suggestion.get("protein", 0)),
                    "totalCarbs": float(suggestion.get("carbs", 0)),
                    "totalFat": float(suggestion.get("fat", 0)),
                }
            )
            await db.meal.create(
                data={
                    "mealPlanId": meal_plan.id,
                    "type": suggestion.get("type", "Lunch"),
                    "name": suggestion.get("name", "Unnamed Meal"),
                    "calories": int(suggestion.get("calories", 0)),
                    "protein": float(suggestion.get("protein", 0)),
                    "carbs": float(suggestion.get("carbs", 0)),
                    "fat": float(suggestion.get("fat", 0)),
                    "cost": float(suggestion.get("cost", 0)),
                    "ingredients": suggestion.get("ingredients", []),
                }
            )

        return {
            "user_id": user_id,
            "suggestions": suggestions,
            "count": len(suggestions),
            "status": "completed",
        }

    finally:
        await db.disconnect()
