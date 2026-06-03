"""Diet analysis and meal comparison service."""

from __future__ import annotations

import json
import logging
from typing import Any

from prisma import Prisma

from app.schemas.diet import DietAnalyzeRequest, DietCompareRequest
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class DietService:
    """Analyse food logs and compare meals via AI, persisting results."""

    # ── Analyse ──────────────────────────────────────────────

    async def analyze(
        self,
        db: Prisma,
        user_id: str,
        request: DietAnalyzeRequest,
    ) -> dict[str, Any]:
        """Analyse a free-text food log and persist the result.

        Returns a dict matching the ``DietAnalysisResponse`` schema.
        """
        # Optionally enrich with user context
        user = await db.user.find_unique(where={"id": user_id})
        user_context: dict[str, Any] | None = None
        if user:
            user_context = {
                "age": user.age,
                "weight": user.weight,
                "height": user.height,
                "activityLevel": user.activityLevel,
                "dietaryPrefs": user.dietaryPrefs or [],
            }

        ai_result = await ai_service.analyze_diet(request.foodLog, user_context=user_context)

        nutrition = ai_result.get("nutrition", {})
        health_score = ai_result.get("healthScore", 0)
        insights = ai_result.get("insights", [])
        suggestions = ai_result.get("suggestions", [])
        warnings = ai_result.get("warnings", [])

        record = await db.dietanalysis.create(
            data={
                "userId": user_id,
                "foodLog": request.foodLog,
                "mealType": request.mealType,
                "nutrition": json.dumps(nutrition),
                "healthScore": float(health_score),
                "insights": insights,
                "suggestions": suggestions,
                "warnings": warnings,
            },
        )

        return {
            "id": record.id,
            "nutrition": nutrition,
            "healthScore": float(health_score),
            "insights": insights,
            "suggestions": suggestions,
            "warnings": warnings,
        }

    # ── Compare ──────────────────────────────────────────────

    async def compare(
        self,
        db: Prisma,
        user_id: str,
        request: DietCompareRequest,
    ) -> dict[str, Any]:
        """Compare two meals side-by-side and persist the comparison.

        Returns a dict matching the ``DietComparisonResponse`` schema.
        """
        ai_result = await ai_service.compare_meals(request.mealA, request.mealB)

        meal_a_nutrition = ai_result.get("mealANutrition", {})
        meal_b_nutrition = ai_result.get("mealBNutrition", {})
        winner = ai_result.get("winner", "Tie")
        comparison = ai_result.get("comparison", [])
        cost_analysis = ai_result.get("costAnalysis")

        record = await db.dietcomparison.create(
            data={
                "userId": user_id,
                "mealA": request.mealA,
                "mealB": request.mealB,
                "mealANutrition": json.dumps(meal_a_nutrition),
                "mealBNutrition": json.dumps(meal_b_nutrition),
                "winner": winner,
                "comparison": comparison,
                "costAnalysis": cost_analysis,
            },
        )

        return {
            "mealANutrition": meal_a_nutrition,
            "mealBNutrition": meal_b_nutrition,
            "winner": winner,
            "comparison": comparison,
            "costAnalysis": cost_analysis,
        }


diet_service = DietService()
