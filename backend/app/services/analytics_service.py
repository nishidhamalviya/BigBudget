"""Dashboard and analytics service.

Aggregates meal, nutrition, budget, and weight data for the user's dashboard
with Redis caching for expensive queries.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

import redis.asyncio as aioredis
from prisma import Prisma

from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Read-only analytics aggregations across meals, budget, and weight."""

    # ── Dashboard ────────────────────────────────────────────

    async def get_dashboard(
        self,
        db: Prisma,
        redis: aioredis.Redis,
        user_id: str,
    ) -> dict[str, Any]:
        """Return top-level dashboard stats (cached for 5 min).

        Includes: totalMeals, avgCalories, avgCost, totalSpent,
        budgetRemaining, recentMeals (last 5).
        """
        cache_key = cache_service.make_key("dashboard", user_id)
        cached = await cache_service.get(redis, cache_key)
        if cached is not None:
            return cached

        # Total meals
        total_meals = await db.meal.count(where={"userId": user_id})

        # All meals for aggregation
        all_meals = await db.meal.find_many(where={"userId": user_id})

        calories_list = [m.calories for m in all_meals if m.calories is not None]
        cost_list = [m.estimatedCost for m in all_meals if m.estimatedCost is not None]

        avg_calories = sum(calories_list) / len(calories_list) if calories_list else None
        avg_cost = sum(cost_list) / len(cost_list) if cost_list else None
        total_spent = sum(cost_list)

        # Budget remaining (monthly)
        user = await db.user.find_unique(where={"id": user_id})
        monthly_budget = user.monthlyBudget if user else None

        # Calculate this month's spending
        now = datetime.now(timezone.utc)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_meals = await db.meal.find_many(
            where={
                "userId": user_id,
                "createdAt": {"gte": month_start},
            },
        )
        month_spent = sum(m.estimatedCost for m in month_meals if m.estimatedCost is not None)
        budget_remaining = (monthly_budget - month_spent) if monthly_budget is not None else None

        # Recent meals (last 5)
        recent = await db.meal.find_many(
            where={"userId": user_id},
            order={"createdAt": "desc"},
            take=5,
        )
        recent_meals = [
            {
                "id": m.id,
                "title": m.title,
                "mealType": m.mealType,
                "calories": m.calories,
                "estimatedCost": m.estimatedCost,
                "createdAt": m.createdAt.isoformat() if m.createdAt else None,
            }
            for m in recent
        ]

        result: dict[str, Any] = {
            "totalMeals": total_meals,
            "avgCalories": round(avg_calories, 1) if avg_calories is not None else None,
            "avgCost": round(avg_cost, 2) if avg_cost is not None else None,
            "totalSpent": round(total_spent, 2),
            "budgetRemaining": round(budget_remaining, 2) if budget_remaining is not None else None,
            "recentMeals": recent_meals,
        }

        await cache_service.set(redis, cache_key, result, ttl=300)
        return result

    # ── Nutrition Analytics ──────────────────────────────────

    async def get_nutrition(
        self,
        db: Prisma,
        user_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Aggregate daily nutrition data for the last *days* days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        meals = await db.meal.find_many(
            where={
                "userId": user_id,
                "createdAt": {"gte": cutoff},
            },
            order={"createdAt": "asc"},
        )

        daily: dict[str, dict[str, float]] = defaultdict(
            lambda: {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
        )

        for m in meals:
            date_key = m.createdAt.strftime("%Y-%m-%d") if m.createdAt else "unknown"
            daily[date_key]["calories"] += m.calories or 0.0
            daily[date_key]["protein"] += m.protein or 0.0
            daily[date_key]["carbs"] += m.carbs or 0.0
            daily[date_key]["fat"] += m.fat or 0.0

        data = [
            {
                "date": date,
                "calories": round(vals["calories"], 1),
                "protein": round(vals["protein"], 1),
                "carbs": round(vals["carbs"], 1),
                "fat": round(vals["fat"], 1),
            }
            for date, vals in sorted(daily.items())
        ]

        num_days = len(data) or 1
        avg_daily = {
            "calories": round(sum(d["calories"] for d in data) / num_days, 1),
            "protein": round(sum(d["protein"] for d in data) / num_days, 1),
            "carbs": round(sum(d["carbs"] for d in data) / num_days, 1),
            "fat": round(sum(d["fat"] for d in data) / num_days, 1),
        }

        return {"data": data, "avgDaily": avg_daily}

    # ── Budget Analytics ─────────────────────────────────────

    async def get_budget(
        self,
        db: Prisma,
        user_id: str,
        days: int = 30,
    ) -> dict[str, Any]:
        """Aggregate daily spending for the last *days* days."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        meals = await db.meal.find_many(
            where={
                "userId": user_id,
                "createdAt": {"gte": cutoff},
            },
            order={"createdAt": "asc"},
        )

        daily_spending: dict[str, dict[str, float | int]] = defaultdict(
            lambda: {"amount": 0.0, "mealCount": 0}
        )

        for m in meals:
            date_key = m.createdAt.strftime("%Y-%m-%d") if m.createdAt else "unknown"
            daily_spending[date_key]["amount"] += m.estimatedCost or 0.0
            daily_spending[date_key]["mealCount"] += 1

        daily_list = [
            {
                "date": date,
                "amount": round(float(vals["amount"]), 2),
                "mealCount": int(vals["mealCount"]),
            }
            for date, vals in sorted(daily_spending.items())
        ]

        total_amount = sum(d["amount"] for d in daily_list)

        # Weekly total (last 7 days)
        week_cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        week_cutoff_str = week_cutoff.strftime("%Y-%m-%d")
        weekly_total = sum(d["amount"] for d in daily_list if d["date"] >= week_cutoff_str)

        # Monthly budget info
        user = await db.user.find_unique(where={"id": user_id})
        monthly_budget = user.monthlyBudget if user else None
        utilization = (
            round((total_amount / monthly_budget) * 100, 1)
            if monthly_budget and monthly_budget > 0
            else None
        )

        return {
            "daily": daily_list,
            "weeklyTotal": round(weekly_total, 2),
            "monthlyTotal": round(total_amount, 2),
            "monthlyBudget": monthly_budget,
            "utilizationPercent": utilization,
        }

    # ── Weight Analytics ─────────────────────────────────────

    async def get_weight(
        self,
        db: Prisma,
        user_id: str,
    ) -> dict[str, Any]:
        """Return weight history with trend analysis."""
        logs = await db.weightlog.find_many(
            where={"userId": user_id},
            order={"createdAt": "asc"},
        )

        data = [
            {
                "date": log.createdAt.strftime("%Y-%m-%d") if log.createdAt else "unknown",
                "weight": log.weight,
                "unit": log.unit,
            }
            for log in logs
        ]

        current_weight: float | None = data[-1]["weight"] if data else None

        # Determine trend from last 5 entries
        trend: str | None = None
        if len(data) >= 2:
            recent_weights = [d["weight"] for d in data[-5:]]
            first_half_avg = sum(recent_weights[: len(recent_weights) // 2]) / max(
                len(recent_weights) // 2, 1
            )
            second_half_avg = sum(recent_weights[len(recent_weights) // 2 :]) / max(
                len(recent_weights) - len(recent_weights) // 2, 1
            )
            diff = second_half_avg - first_half_avg
            if diff > 0.5:
                trend = "gaining"
            elif diff < -0.5:
                trend = "losing"
            else:
                trend = "stable"

        return {
            "data": data,
            "currentWeight": current_weight,
            "trend": trend,
        }


analytics_service = AnalyticsService()
