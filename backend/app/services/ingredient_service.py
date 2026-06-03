"""Ingredient scanning and detection service.

Wraps the AI vision capabilities for food-label scanning (OCR-style) and
pantry/fridge item detection.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)


class IngredientService:
    """Image-based ingredient extraction powered by GPT-4o Vision."""

    # ── Label Scan ───────────────────────────────────────────

    async def scan_image(self, image_bytes: bytes) -> dict[str, Any]:
        """Scan a food-label image and extract structured ingredients.

        Parameters
        ----------
        image_bytes:
            Raw bytes of the uploaded image (JPEG/PNG).

        Returns
        -------
        dict with keys ``ingredients`` (list) and ``rawText`` (str | None).
        """
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        result = await ai_service.analyze_image(image_b64, mode="scan")

        ingredients = result.get("ingredients", [])
        raw_text = result.get("rawText")

        return {
            "ingredients": [
                {
                    "name": ing.get("name", "Unknown"),
                    "confidence": ing.get("confidence"),
                    "quantity": ing.get("quantity"),
                    "category": ing.get("category"),
                }
                for ing in ingredients
            ],
            "rawText": raw_text,
        }

    # ── Pantry / Fridge Detection ────────────────────────────

    async def detect_items(self, image_bytes: bytes) -> dict[str, Any]:
        """Detect food items in a pantry/fridge photo and suggest meals.

        Parameters
        ----------
        image_bytes:
            Raw bytes of the uploaded image (JPEG/PNG).

        Returns
        -------
        dict with keys ``items`` (list) and ``suggestedMeals`` (list[str] | None).
        """
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        result = await ai_service.analyze_image(image_b64, mode="detect")

        items = result.get("items", [])
        suggested_meals = result.get("suggestedMeals")

        return {
            "items": [
                {
                    "name": item.get("name", "Unknown"),
                    "confidence": item.get("confidence"),
                    "quantity": item.get("quantity"),
                    "category": item.get("category"),
                }
                for item in items
            ],
            "suggestedMeals": suggested_meals,
        }


ingredient_service = IngredientService()
