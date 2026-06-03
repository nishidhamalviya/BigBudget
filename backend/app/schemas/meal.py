"""Meal generation & listing Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    """Single ingredient with quantity, unit, and optional cost."""

    name: str
    quantity: str
    unit: str
    estimatedCost: float | None = None


class MealGenerateRequest(BaseModel):
    """Payload sent by the client to generate a new meal."""

    budget: float | None = None
    cuisine: str | None = None
    mealType: str = "lunch"
    servings: int = Field(default=1, ge=1, le=20)
    dietaryPrefs: list[str] | None = None
    specificIngredients: list[str] | None = None
    additionalNotes: str | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "budget": 150.0,
                    "cuisine": "South Indian",
                    "mealType": "lunch",
                    "servings": 2,
                    "dietaryPrefs": ["vegetarian"],
                }
            ]
        }
    }


class MealResponse(BaseModel):
    """Full meal object returned after generation or from history."""

    id: str
    title: str
    description: str | None = None
    cuisine: str | None = None
    mealType: str
    servings: int
    prepTime: int | None = None
    cookTime: int | None = None
    ingredients: list[IngredientItem] = []
    instructions: list[str] = []
    calories: float | None = None
    protein: float | None = None
    carbs: float | None = None
    fat: float | None = None
    fiber: float | None = None
    estimatedCost: float | None = None
    budgetRange: str | None = None
    createdAt: datetime

    model_config = {"from_attributes": True}


class MealListResponse(BaseModel):
    """Paginated list of meals."""

    meals: list[MealResponse]
    total: int
    page: int
    pageSize: int
