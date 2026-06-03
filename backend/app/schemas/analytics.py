"""Dashboard & analytics Pydantic schemas."""

from __future__ import annotations

from pydantic import BaseModel


class DashboardStats(BaseModel):
    """Top-level dashboard summary statistics."""

    totalMeals: int
    avgCalories: float | None = None
    avgCost: float | None = None
    totalSpent: float
    budgetRemaining: float | None = None
    recentMeals: list[dict] = []


# ── Nutrition ────────────────────────────────────────────────


class NutritionDataPoint(BaseModel):
    """Single day's aggregated nutrition data."""

    date: str
    calories: float
    protein: float
    carbs: float
    fat: float


class NutritionAnalytics(BaseModel):
    """Nutrition time-series and averages."""

    data: list[NutritionDataPoint] = []
    avgDaily: dict = {}


# ── Budget ───────────────────────────────────────────────────


class BudgetDataPoint(BaseModel):
    """Single day's spending summary."""

    date: str
    amount: float
    mealCount: int


class BudgetAnalytics(BaseModel):
    """Spending time-series with weekly/monthly aggregates."""

    daily: list[BudgetDataPoint] = []
    weeklyTotal: float
    monthlyTotal: float
    monthlyBudget: float | None = None
    utilizationPercent: float | None = None


# ── Weight ───────────────────────────────────────────────────


class WeightDataPoint(BaseModel):
    """Single weight log entry."""

    date: str
    weight: float
    unit: str


class WeightAnalytics(BaseModel):
    """Weight history with optional trend analysis."""

    data: list[WeightDataPoint] = []
    currentWeight: float | None = None
    trend: str | None = None
