"""Meal-related Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MealGenerateRequest(BaseModel):
    """Request body for AI meal generation."""

    preferences: Optional[str] = None
    budget: Optional[float] = None
    calories: Optional[int] = None
    dietType: Optional[str] = None
    ingredients: list[str] = Field(default_factory=list)
    mealType: Optional[str] = None


class MealItem(BaseModel):
    """A single meal entry."""

    id: str
    type: str
    name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    cost: float
    ingredients: list[str] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MealPlanSummary(BaseModel):
    """Summary of a meal plan."""

    id: str
    date: datetime
    totalCost: float
    totalCals: int
    totalProtein: float
    totalCarbs: float
    totalFat: float
    meals: list[MealItem] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class MealResponse(BaseModel):
    """Single meal plan response."""

    mealPlan: MealPlanSummary


class MealListResponse(BaseModel):
    """Paginated list of meal plans."""

    mealPlans: list[MealPlanSummary]
    total: int
    page: int
    pageSize: int
