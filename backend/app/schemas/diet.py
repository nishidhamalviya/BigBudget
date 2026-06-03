"""Diet analysis & comparison Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class NutritionBreakdown(BaseModel):
    """Macro- and micro-nutrient summary."""

    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float | None = None
    sugar: float | None = None
    sodium: float | None = None


class DietAnalyzeRequest(BaseModel):
    """Request to analyse a free-text food log."""

    foodLog: str
    mealType: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [{"foodLog": "2 roti, dal fry, rice 1 cup, salad", "mealType": "lunch"}]
        }
    }


class DietAnalysisResponse(BaseModel):
    """Result of a diet analysis."""

    id: str
    nutrition: NutritionBreakdown
    healthScore: float
    insights: list[str] = []
    suggestions: list[str] = []
    warnings: list[str] | None = None


class DietCompareRequest(BaseModel):
    """Request to compare two meals side by side."""

    mealA: str
    mealB: str


class DietComparisonResponse(BaseModel):
    """Side-by-side comparison result."""

    mealANutrition: NutritionBreakdown
    mealBNutrition: NutritionBreakdown
    winner: str
    comparison: list[str] = []
    costAnalysis: str | None = None
