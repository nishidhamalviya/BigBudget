"""Grocery list generation, PDF export, and CSV export service."""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime
from typing import Any

import redis.asyncio as aioredis
from fastapi import HTTPException, status
from prisma import Prisma
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.schemas.grocery import GroceryGenerateRequest
from app.services.ai_service import ai_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class GroceryService:
    """Generate, persist, and export grocery lists."""

    # ── Generate ─────────────────────────────────────────────

    async def generate_list(
        self,
        db: Prisma,
        redis: aioredis.Redis,
        user_id: str,
        request: GroceryGenerateRequest,
    ) -> dict[str, Any]:
        """Build a grocery list from meal IDs and/or custom items via AI.

        Steps:
        1. Fetch meals by ID (if any) and collect their ingredients.
        2. Append custom free-text items.
        3. Call the AI service to aggregate and price the list.
        4. Persist to the ``GroceryList`` table.
        """
        meals_data: list[dict[str, Any]] = []

        if request.mealIds:
            for meal_id in request.mealIds:
                meal = await db.meal.find_unique(where={"id": meal_id})
                if meal and meal.userId == user_id:
                    ingredients_raw = meal.ingredients
                    if isinstance(ingredients_raw, str):
                        try:
                            ingredients_raw = json.loads(ingredients_raw)
                        except (json.JSONDecodeError, TypeError):
                            ingredients_raw = []
                    meals_data.append(
                        {
                            "title": meal.title,
                            "ingredients": ingredients_raw if isinstance(ingredients_raw, list) else [],
                        }
                    )

        if request.customItems:
            meals_data.append(
                {
                    "title": "Custom Items",
                    "ingredients": [
                        {"name": item, "quantity": "1", "unit": "unit", "estimatedCost": None}
                        for item in request.customItems
                    ],
                }
            )

        if not meals_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least one meal ID or custom item",
            )

        ai_result = await ai_service.generate_grocery_list(meals_data, budget=request.budget)

        grocery_record = await db.grocerylist.create(
            data={
                "userId": user_id,
                "title": ai_result.get("title", "Grocery List"),
                "items": json.dumps(ai_result.get("items", [])),
                "totalEstCost": ai_result.get("totalEstCost"),
                "mealIds": request.mealIds or [],
            },
        )

        return self._to_dict(grocery_record)

    # ── PDF Export ───────────────────────────────────────────

    async def export_pdf(self, db: Prisma, user_id: str) -> bytes:
        """Generate a professionally styled PDF for the latest grocery list."""
        grocery = await db.grocerylist.find_first(
            where={"userId": user_id},
            order={"createdAt": "desc"},
        )
        if grocery is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No grocery list found",
            )

        items = self._parse_items(grocery.items)

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
            fontSize=20,
            spaceAfter=6,
            textColor=colors.HexColor("#2E7D32"),
        )
        subtitle_style = ParagraphStyle(
            "GrocerySubtitle",
            parent=styles["Normal"],
            fontSize=10,
            textColor=colors.grey,
            spaceAfter=14,
        )

        elements: list[Any] = []

        # Title & date
        elements.append(Paragraph("BudgetBites Grocery List", title_style))
        date_str = grocery.createdAt.strftime("%d %B %Y, %I:%M %p") if grocery.createdAt else datetime.utcnow().strftime("%d %B %Y, %I:%M %p")
        elements.append(Paragraph(f"Generated on {date_str}", subtitle_style))
        elements.append(Spacer(1, 4 * mm))

        # Table
        header = ["#", "Item", "Qty", "Unit", "Est. Price (₹)", "Category"]
        table_data = [header]

        for idx, item in enumerate(items, 1):
            table_data.append([
                str(idx),
                item.get("name", "—"),
                item.get("quantity", "—"),
                item.get("unit", "—"),
                f"₹{item['estimatedPrice']:.2f}" if item.get("estimatedPrice") else "—",
                item.get("category", "—"),
            ])

        total_cost = grocery.totalEstCost or sum(
            i.get("estimatedPrice", 0) or 0 for i in items
        )
        table_data.append(["", "", "", "", f"₹{total_cost:.2f}", "TOTAL"])

        col_widths = [25, 150, 50, 50, 80, 100]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(
            TableStyle([
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                # Body
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("ALIGN", (0, 1), (0, -1), "CENTER"),
                ("ALIGN", (4, 1), (4, -1), "RIGHT"),
                # Total row
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E8F5E9")),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDBDBD")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F5F5F5")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(table)

        doc.build(elements)
        return buffer.getvalue()

    # ── CSV Export ────────────────────────────────────────────

    async def export_csv(self, db: Prisma, user_id: str) -> str:
        """Generate a CSV string for the latest grocery list."""
        grocery = await db.grocerylist.find_first(
            where={"userId": user_id},
            order={"createdAt": "desc"},
        )
        if grocery is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No grocery list found",
            )

        items = self._parse_items(grocery.items)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Item", "Quantity", "Unit", "Estimated Price (INR)", "Category", "Checked"])

        for item in items:
            writer.writerow([
                item.get("name", ""),
                item.get("quantity", ""),
                item.get("unit", ""),
                item.get("estimatedPrice", ""),
                item.get("category", ""),
                item.get("checked", False),
            ])

        total_cost = grocery.totalEstCost or sum(
            i.get("estimatedPrice", 0) or 0 for i in items
        )
        writer.writerow(["TOTAL", "", "", f"{total_cost:.2f}", "", ""])

        return output.getvalue()

    # ── Private helpers ──────────────────────────────────────

    @staticmethod
    def _parse_items(raw: Any) -> list[dict[str, Any]]:
        """Safely parse the JSON items field from a GroceryList record."""
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @staticmethod
    def _to_dict(grocery: Any) -> dict[str, Any]:
        """Convert a Prisma GroceryList record to a plain dict."""
        items_raw = grocery.items
        if isinstance(items_raw, str):
            try:
                items_raw = json.loads(items_raw)
            except (json.JSONDecodeError, TypeError):
                items_raw = []

        return {
            "id": grocery.id,
            "title": grocery.title,
            "items": items_raw if isinstance(items_raw, list) else [],
            "totalEstCost": grocery.totalEstCost,
            "mealIds": grocery.mealIds or [],
            "createdAt": grocery.createdAt.isoformat() if grocery.createdAt else None,
        }


grocery_service = GroceryService()
