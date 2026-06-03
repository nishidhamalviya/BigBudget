"""Grocery list Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class GroceryItem(BaseModel):
    """Single grocery list item."""

    name: str
    quantity: str
    unit: str
    estimatedPrice: float | None = None
    category: str | None = None
    checked: bool = False


class GroceryGenerateRequest(BaseModel):
    """Request to generate a grocery list from meals or custom items."""

    mealIds: list[str] | None = None
    customItems: list[str] | None = None
    budget: float | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "mealIds": ["meal-uuid-1", "meal-uuid-2"],
                    "budget": 800.0,
                }
            ]
        }
    }


class GroceryListResponse(BaseModel):
    """Generated grocery list with items and cost summary."""

    id: str
    title: str | None = None
    items: list[GroceryItem] = []
    totalEstCost: float | None = None
    mealIds: list[str] = []
    createdAt: datetime

    model_config = {"from_attributes": True}
