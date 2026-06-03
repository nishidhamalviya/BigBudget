"""User-related Pydantic schemas."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr


class UserProfile(BaseModel):
    """Public user profile — never includes the password hash."""

    id: str
    email: str
    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activityLevel: Optional[str] = None
    fitnessGoal: Optional[str] = None
    dietPreference: Optional[str] = None
    dailyBudget: Optional[float] = None
    weeklyBudget: Optional[float] = None

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    """Fields that a user may update on their profile."""

    name: Optional[str] = None
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    gender: Optional[str] = None
    activityLevel: Optional[str] = None
    fitnessGoal: Optional[str] = None
    dietPreference: Optional[str] = None
    dailyBudget: Optional[float] = None
    weeklyBudget: Optional[float] = None
