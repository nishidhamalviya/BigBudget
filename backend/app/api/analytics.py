"""Analytics dashboard, nutrition, budget, and weight tracking endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.analytics import (
    BudgetAnalytics,
    DashboardStats,
    NutritionAnalytics,
    WeightAnalytics,
)
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


# ── GET /analytics/dashboard ─────────────────────────────────────────────────


@router.get(
    "/dashboard",
    response_model=DashboardStats,
    summary="Get top-level dashboard statistics",
)
async def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> DashboardStats:
    """Return an at-a-glance summary: total meals, average calories,
    average cost, total spending, remaining budget, and recent meals.
    """

    return await analytics_service.get_dashboard(
        user=current_user,
        db=db,
    )


# ── GET /analytics/nutrition ─────────────────────────────────────────────────


@router.get(
    "/nutrition",
    response_model=NutritionAnalytics,
    summary="Get nutrition analytics over a period",
)
async def get_nutrition(
    days: int = Query(default=30, ge=1, le=365, description="Look-back window in days"),
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> NutritionAnalytics:
    """Return daily macro-nutrient time-series and averages for the specified
    number of past days.
    """

    return await analytics_service.get_nutrition(
        user=current_user,
        days=days,
        db=db,
    )


# ── GET /analytics/budget ────────────────────────────────────────────────────


@router.get(
    "/budget",
    response_model=BudgetAnalytics,
    summary="Get budget / spending analytics",
)
async def get_budget(
    days: int = Query(default=30, ge=1, le=365, description="Look-back window in days"),
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> BudgetAnalytics:
    """Return daily spending time-series, weekly and monthly totals,
    and budget utilisation percentage.
    """

    return await analytics_service.get_budget(
        user=current_user,
        days=days,
        db=db,
    )


# ── GET /analytics/weight ────────────────────────────────────────────────────


@router.get(
    "/weight",
    response_model=WeightAnalytics,
    summary="Get weight history and trend",
)
async def get_weight(
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> WeightAnalytics:
    """Return the user's weight history entries and an optional trend
    indicator (gaining / losing / stable).
    """

    return await analytics_service.get_weight(
        user=current_user,
        db=db,
    )
