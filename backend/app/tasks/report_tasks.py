"""Celery tasks for report generation (nutrition reports and grocery PDFs).

All async DB / AI operations are wrapped with ``asyncio.run()`` because
Celery workers execute tasks synchronously.
"""

from __future__ import annotations

import asyncio
import io
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task 1: Generate a weekly nutrition report
# ---------------------------------------------------------------------------


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_weekly_nutrition_report(
    self: Any,
    user_id: str,
) -> dict:
    """Aggregate the past 7 days of meal data and produce a nutrition summary.

    The summary is stored in Redis for quick retrieval by the analytics
    endpoints and returned as the task result.

    Args:
        user_id: UUID of the user.

    Returns:
        A summary dict containing daily averages, totals, and highlights.
    """
    try:
        return asyncio.run(_generate_weekly_report_async(user_id))
    except Exception as exc:
        logger.exception(
            "generate_weekly_nutrition_report failed for user=%s", user_id
        )
        raise self.retry(exc=exc)


async def _generate_weekly_report_async(user_id: str) -> dict:
    """Async implementation of the weekly nutrition report."""

    from prisma import Prisma
    import redis.asyncio as aioredis

    from app.core.config import settings

    db = Prisma()
    await db.connect()
    r: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)

        meal_plans = await db.mealplan.find_many(
            where={
                "userId": user_id,
                "createdAt": {"gte": seven_days_ago},
            },
            include={"meals": True},
            order={"createdAt": "desc"},
        )

        if not meal_plans:
            summary = {
                "user_id": user_id,
                "period": "7d",
                "total_meals": 0,
                "total_calories": 0,
                "total_protein": 0.0,
                "total_carbs": 0.0,
                "total_fat": 0.0,
                "total_cost": 0.0,
                "avg_daily_calories": 0,
                "avg_daily_cost": 0.0,
                "generated_at": now.isoformat(),
                "highlights": ["No meals recorded in the past 7 days."],
            }
        else:
            total_calories = sum(mp.totalCals for mp in meal_plans)
            total_protein = sum(mp.totalProtein for mp in meal_plans)
            total_carbs = sum(mp.totalCarbs for mp in meal_plans)
            total_fat = sum(mp.totalFat for mp in meal_plans)
            total_cost = sum(mp.totalCost for mp in meal_plans)
            total_meals = sum(len(mp.meals) if mp.meals else 0 for mp in meal_plans)

            days_with_data = len(meal_plans)
            avg_daily_calories = total_calories / days_with_data if days_with_data else 0
            avg_daily_cost = total_cost / days_with_data if days_with_data else 0.0

            highlights: list[str] = []
            if avg_daily_calories > 2500:
                highlights.append(
                    "Your average daily calorie intake is above 2 500 kcal. "
                    "Consider lighter meals."
                )
            if avg_daily_calories < 1200:
                highlights.append(
                    "Your average daily calorie intake is below 1 200 kcal. "
                    "Make sure you're eating enough."
                )
            if total_protein / days_with_data < 50:
                highlights.append("Your protein intake is below recommended levels.")
            if not highlights:
                highlights.append("Great job! Your nutrition looks balanced this week.")

            summary = {
                "user_id": user_id,
                "period": "7d",
                "total_meals": total_meals,
                "total_calories": total_calories,
                "total_protein": round(total_protein, 1),
                "total_carbs": round(total_carbs, 1),
                "total_fat": round(total_fat, 1),
                "total_cost": round(total_cost, 2),
                "avg_daily_calories": round(avg_daily_calories),
                "avg_daily_cost": round(avg_daily_cost, 2),
                "generated_at": now.isoformat(),
                "highlights": highlights,
            }

        # Cache the report in Redis for 24 hours
        cache_key = f"report:nutrition:weekly:{user_id}"
        await r.setex(cache_key, 86400, json.dumps(summary))

        return summary

    finally:
        await db.disconnect()
        await r.aclose()


# ---------------------------------------------------------------------------
# Task 2: Generate a grocery list PDF (for large lists)
# ---------------------------------------------------------------------------


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def generate_grocery_pdf_async(
    self: Any,
    grocery_list_id: str,
) -> dict:
    """Generate a PDF for a grocery list and store it in Redis for download.

    This task is used when the grocery list is large enough that synchronous
    PDF generation would time out the HTTP request.

    Args:
        grocery_list_id: Identifier of the grocery list (could be a cache key
            or a database ID, depending on how grocery lists are stored).

    Returns:
        A dict with ``pdf_cache_key`` pointing to the Redis key where the PDF
        bytes are stored, and the ``page_count``.
    """
    try:
        return asyncio.run(_generate_grocery_pdf(grocery_list_id))
    except Exception as exc:
        logger.exception(
            "generate_grocery_pdf_async failed for grocery_list=%s",
            grocery_list_id,
        )
        raise self.retry(exc=exc)


async def _generate_grocery_pdf(grocery_list_id: str) -> dict:
    """Async implementation of the grocery PDF generator."""

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    import redis.asyncio as aioredis

    from app.core.config import settings

    r: aioredis.Redis = aioredis.from_url(settings.REDIS_URL, decode_responses=False)

    try:
        # Attempt to retrieve the grocery list data from Redis (stored as JSON)
        raw = await r.get(f"grocery:{grocery_list_id}")
        if raw is None:
            return {
                "error": "Grocery list not found",
                "grocery_list_id": grocery_list_id,
            }

        grocery_data = json.loads(raw.decode("utf-8") if isinstance(raw, bytes) else raw)
        items: list[dict] = grocery_data.get("items", [])

        # ── Build PDF ─────────────────────────────────────────────────
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
            leftMargin=15 * mm,
            rightMargin=15 * mm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "GroceryTitle",
            parent=styles["Heading1"],
            fontSize=18,
            spaceAfter=12,
            textColor=colors.HexColor("#2E7D32"),
        )

        elements: list[Any] = []
        elements.append(Paragraph("🛒 BudgetBites Grocery List", title_style))
        elements.append(Spacer(1, 8 * mm))

        # Table header + rows
        table_data: list[list[str]] = [
            ["#", "Item", "Qty", "Unit", "Est. Cost (₹)", "Category"]
        ]
        for idx, item in enumerate(items, start=1):
            table_data.append([
                str(idx),
                item.get("name", "—"),
                str(item.get("quantity", "")),
                item.get("unit", ""),
                f"₹{item.get('estimatedPrice', item.get('estimatedCost', 0)):.2f}",
                item.get("category", "—"),
            ])

        col_widths = [20 * mm, 55 * mm, 20 * mm, 20 * mm, 30 * mm, 35 * mm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F5F5F5")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F5F5")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ])
        )
        elements.append(table)

        # Total cost footer
        total_cost = grocery_data.get(
            "totalEstCost",
            sum(
                item.get("estimatedPrice", item.get("estimatedCost", 0))
                for item in items
            ),
        )
        elements.append(Spacer(1, 6 * mm))
        elements.append(
            Paragraph(
                f"<b>Total Estimated Cost: ₹{total_cost:.2f}</b>",
                styles["Heading3"],
            )
        )

        doc.build(elements)

        pdf_bytes = buffer.getvalue()
        pdf_cache_key = f"grocery:pdf:{grocery_list_id}"

        # Store PDF bytes in Redis for 1 hour
        await r.setex(pdf_cache_key, 3600, pdf_bytes)

        return {
            "grocery_list_id": grocery_list_id,
            "pdf_cache_key": pdf_cache_key,
            "size_bytes": len(pdf_bytes),
            "item_count": len(items),
            "status": "completed",
        }

    finally:
        await r.aclose()
