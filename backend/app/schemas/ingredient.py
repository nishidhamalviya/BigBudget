"""Ingredient scanning & detection Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DetectedIngredient(BaseModel):
    """A single ingredient identified by the AI vision model."""

    name: str
    confidence: float | None = None
    quantity: str | None = None
    category: str | None = None


class ScanResponse(BaseModel):
    """Response from scanning a food label image."""

    ingredients: list[DetectedIngredient] = []
    rawText: str | None = None


class DetectResponse(BaseModel):
    """Response from detecting food items in a pantry photo."""

    items: list[DetectedIngredient] = []
    suggestedMeals: list[str] | None = None
