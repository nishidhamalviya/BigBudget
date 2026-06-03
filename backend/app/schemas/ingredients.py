"""Ingredient scanning / detection Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class IngredientItem(BaseModel):
    """A single detected ingredient."""

    name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    quantity: str | None = None
    unit: str | None = None


class ScanResponse(BaseModel):
    """Response after scanning an image for ingredient text."""

    ingredients: list[IngredientItem]
    rawText: str | None = None


class DetectResponse(BaseModel):
    """Response after detecting ingredient objects in an image."""

    items: list[IngredientItem]
    totalDetected: int
