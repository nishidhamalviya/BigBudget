"""User profile Pydantic schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """Full user profile returned by the API."""

    id: str
    email: EmailStr
    name: str | None = None
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    activityLevel: str | None = None
    dietaryPrefs: list[str] = []
    allergies: list[str] = []
    monthlyBudget: float | None = None
    currency: str = "INR"
    avatarUrl: str | None = None
    createdAt: datetime

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Partial update payload — every field is optional."""

    name: str | None = None
    age: int | None = None
    weight: float | None = None
    height: float | None = None
    activityLevel: str | None = None
    dietaryPrefs: list[str] | None = None
    allergies: list[str] | None = None
    monthlyBudget: float | None = None
    currency: str | None = None
    avatarUrl: str | None = None

    model_config = {"json_schema_extra": {"examples": [{"name": "Ravi Kumar", "monthlyBudget": 5000.0}]}}
