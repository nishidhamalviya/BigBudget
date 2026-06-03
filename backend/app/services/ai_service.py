"""OpenAI wrapper service for all AI-powered features.

Every public method handles prompt engineering, calls the API, and parses the
structured JSON response.  All calls use ``AsyncOpenAI`` so they are fully
non-blocking inside FastAPI's event loop.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Singleton wrapper around the OpenAI async client."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    # ── helpers ──────────────────────────────────────────────

    async def _chat(
        self,
        messages: list[dict[str, str]],
        *,
        model: str = "gpt-4o",
        json_mode: bool = True,
        temperature: float = 0.7,
    ) -> dict[str, Any] | str:
        """Internal helper that calls the chat-completions API.

        When *json_mode* is ``True`` the raw response text is parsed into a
        ``dict``; otherwise the plain string is returned.
        """
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        try:
            response = await self._client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content or ""
            if json_mode:
                return json.loads(content)
            return content
        except json.JSONDecodeError as exc:
            logger.error("Failed to parse AI JSON response: %s", exc)
            raise ValueError("AI returned invalid JSON") from exc
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            raise

    # ── Meal Generation ──────────────────────────────────────

    async def generate_meal(self, constraints: dict[str, Any]) -> dict[str, Any]:
        """Generate a single budget-conscious meal based on *constraints*.

        Expected constraint keys (all optional):
        ``budget``, ``cuisine``, ``mealType``, ``servings``,
        ``dietaryPrefs``, ``specificIngredients``, ``additionalNotes``,
        ``allergies``, ``activityLevel``.

        Returns a structured dict with keys: title, description, cuisine,
        mealType, servings, prepTime, cookTime, ingredients, instructions,
        calories, protein, carbs, fat, fiber, estimatedCost.
        """
        budget = constraints.get("budget")
        cuisine = constraints.get("cuisine", "Indian")
        meal_type = constraints.get("mealType", "lunch")
        servings = constraints.get("servings", 1)
        dietary_prefs = constraints.get("dietaryPrefs") or []
        specific_ingredients = constraints.get("specificIngredients") or []
        additional_notes = constraints.get("additionalNotes", "")
        allergies = constraints.get("allergies") or []

        budget_instruction = (
            f"The total cost MUST be within ₹{budget}." if budget else "Optimise for the lowest reasonable cost."
        )

        system_prompt = (
            "You are a professional nutritionist and chef creating budget-conscious "
            "meals for Indian households. You specialise in nutritious, tasty meals "
            "that are affordable and easy to prepare.\n\n"
            "Respond ONLY with a single JSON object using exactly these keys:\n"
            "{\n"
            '  "title": "string",\n'
            '  "description": "string (1-2 sentence summary)",\n'
            '  "cuisine": "string",\n'
            '  "mealType": "string",\n'
            '  "servings": number,\n'
            '  "prepTime": number (minutes),\n'
            '  "cookTime": number (minutes),\n'
            '  "ingredients": [\n'
            '    {"name": "string", "quantity": "string", "unit": "string", "estimatedCost": number}\n'
            "  ],\n"
            '  "instructions": ["step 1", "step 2", ...],\n'
            '  "calories": number,\n'
            '  "protein": number (grams),\n'
            '  "carbs": number (grams),\n'
            '  "fat": number (grams),\n'
            '  "fiber": number (grams),\n'
            '  "estimatedCost": number (total in INR)\n'
            "}\n\n"
            "All costs are in Indian Rupees (₹). Provide realistic Indian market prices."
        )

        user_prompt_parts = [
            f"Generate a {meal_type} recipe for {servings} serving(s).",
            f"Cuisine preference: {cuisine}.",
            budget_instruction,
        ]
        if dietary_prefs:
            user_prompt_parts.append(f"Dietary preferences: {', '.join(dietary_prefs)}.")
        if allergies:
            user_prompt_parts.append(f"Allergies / restrictions (MUST avoid): {', '.join(allergies)}.")
        if specific_ingredients:
            user_prompt_parts.append(f"Must use these ingredients: {', '.join(specific_ingredients)}.")
        if additional_notes:
            user_prompt_parts.append(f"Additional notes: {additional_notes}")

        user_prompt = " ".join(user_prompt_parts)

        result = await self._chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if not isinstance(result, dict):
            raise ValueError("AI did not return a valid meal object")
        return result

    # ── Image Analysis ───────────────────────────────────────

    async def analyze_image(self, image_base64: str, mode: str = "scan") -> dict[str, Any]:
        """Analyse an image using GPT-4o vision.

        Parameters
        ----------
        image_base64:
            Base-64 encoded image data (jpeg/png).
        mode:
            ``"scan"`` — extract ingredients from a food label.
            ``"detect"`` — identify food items in a pantry/fridge photo.
        """
        if mode == "scan":
            system_prompt = (
                "You are an expert food-label reader. Analyse the image of a food "
                "product label and extract all ingredients with their quantities.\n\n"
                "Respond ONLY with a JSON object:\n"
                "{\n"
                '  "ingredients": [\n'
                '    {"name": "string", "confidence": 0.0-1.0, "quantity": "string or null", "category": "string or null"}\n'
                "  ],\n"
                '  "rawText": "string (the raw text visible on the label)"\n'
                "}"
            )
            user_text = "Please scan this food label and extract the ingredients."
        else:
            system_prompt = (
                "You are a kitchen inventory expert. Look at this photo of a "
                "kitchen, pantry, or fridge and identify all visible food items.\n\n"
                "Respond ONLY with a JSON object:\n"
                "{\n"
                '  "items": [\n'
                '    {"name": "string", "confidence": 0.0-1.0, "quantity": "string or null", "category": "string or null"}\n'
                "  ],\n"
                '  "suggestedMeals": ["meal idea 1", "meal idea 2", ...]\n'
                "}"
            )
            user_text = "Please identify the food items visible in this photo and suggest meals."

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    },
                ],
            },
        ]

        result = await self._chat(messages, model="gpt-4o")
        if not isinstance(result, dict):
            raise ValueError("AI did not return a valid analysis object")
        return result

    # ── Diet Analysis ────────────────────────────────────────

    async def analyze_diet(
        self,
        food_log: str,
        user_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Analyse a free-text food log and return structured nutrition data.

        Returns dict with keys: nutrition, healthScore, insights, suggestions, warnings.
        """
        ctx_block = ""
        if user_context:
            ctx_parts: list[str] = []
            if user_context.get("age"):
                ctx_parts.append(f"Age: {user_context['age']}")
            if user_context.get("weight"):
                ctx_parts.append(f"Weight: {user_context['weight']} kg")
            if user_context.get("height"):
                ctx_parts.append(f"Height: {user_context['height']} cm")
            if user_context.get("activityLevel"):
                ctx_parts.append(f"Activity level: {user_context['activityLevel']}")
            if user_context.get("dietaryPrefs"):
                ctx_parts.append(f"Dietary prefs: {', '.join(user_context['dietaryPrefs'])}")
            if ctx_parts:
                ctx_block = "\n\nUser context:\n" + "\n".join(ctx_parts)

        system_prompt = (
            "You are a certified nutritionist. Analyse the food log below and "
            "provide a detailed nutritional breakdown.\n\n"
            "Respond ONLY with a JSON object:\n"
            "{\n"
            '  "nutrition": {\n'
            '    "calories": number,\n'
            '    "protein": number,\n'
            '    "carbs": number,\n'
            '    "fat": number,\n'
            '    "fiber": number or null,\n'
            '    "sugar": number or null,\n'
            '    "sodium": number or null\n'
            "  },\n"
            '  "healthScore": number (0-100),\n'
            '  "insights": ["insight 1", ...],\n'
            '  "suggestions": ["suggestion 1", ...],\n'
            '  "warnings": ["warning 1", ...] or []\n'
            "}\n\n"
            "All nutrient values are in grams (or mg for sodium). "
            "Be accurate with Indian food portions and preparations."
        )

        user_prompt = f"Food log:\n{food_log}{ctx_block}"

        result = await self._chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if not isinstance(result, dict):
            raise ValueError("AI did not return a valid diet analysis")
        return result

    # ── Meal Comparison ──────────────────────────────────────

    async def compare_meals(self, meal_a: str, meal_b: str) -> dict[str, Any]:
        """Compare two meals side by side on nutrition, cost, and health.

        Returns dict with keys: mealANutrition, mealBNutrition, winner,
        comparison, costAnalysis.
        """
        system_prompt = (
            "You are a nutritionist comparing two meals. Provide a detailed "
            "side-by-side nutritional comparison.\n\n"
            "Respond ONLY with a JSON object:\n"
            "{\n"
            '  "mealANutrition": {"calories": n, "protein": n, "carbs": n, "fat": n, "fiber": n or null, "sugar": n or null, "sodium": n or null},\n'
            '  "mealBNutrition": {"calories": n, "protein": n, "carbs": n, "fat": n, "fiber": n or null, "sugar": n or null, "sodium": n or null},\n'
            '  "winner": "Meal A or Meal B",\n'
            '  "comparison": ["point 1", "point 2", ...],\n'
            '  "costAnalysis": "string comparing estimated costs in INR"\n'
            "}\n\n"
            "Use realistic Indian food portions and prices."
        )

        result = await self._chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Meal A: {meal_a}\n\nMeal B: {meal_b}"},
            ],
        )
        if not isinstance(result, dict):
            raise ValueError("AI did not return a valid comparison")
        return result

    # ── Grocery List Generation ──────────────────────────────

    async def generate_grocery_list(
        self,
        meals_data: list[dict[str, Any]],
        budget: float | None = None,
    ) -> dict[str, Any]:
        """Aggregate ingredients from multiple meals into a grocery list.

        Returns dict with keys: items (list of {name, quantity, unit,
        estimatedPrice, category}), totalEstCost.
        """
        budget_note = f" Total budget: ₹{budget}." if budget else ""

        system_prompt = (
            "You are a smart grocery-list planner for Indian households. "
            "Given the meal ingredients below, produce an aggregated, "
            "de-duplicated grocery list with realistic Indian market prices.\n\n"
            "Respond ONLY with a JSON object:\n"
            "{\n"
            '  "title": "string",\n'
            '  "items": [\n'
            '    {"name": "string", "quantity": "string", "unit": "string", '
            '"estimatedPrice": number, "category": "string"}\n'
            "  ],\n"
            '  "totalEstCost": number\n'
            "}\n\n"
            "Categories: Vegetables, Fruits, Dairy, Grains, Spices, Protein, "
            "Oils & Fats, Beverages, Other.\n"
            "All prices are in Indian Rupees (₹)."
        )

        meals_text = json.dumps(meals_data, default=str, indent=2)
        user_prompt = f"Create a grocery list from these meals:{budget_note}\n\n{meals_text}"

        result = await self._chat(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        if not isinstance(result, dict):
            raise ValueError("AI did not return a valid grocery list")
        return result

    # ── Chat Completion (AI Coach) ───────────────────────────

    async def chat_completion(
        self,
        messages: list[dict[str, str]],
        user_context: dict[str, Any] | None = None,
    ) -> str:
        """Run a multi-turn conversation with the BudgetBites AI Coach.

        Parameters
        ----------
        messages:
            Conversation history in ``[{"role": …, "content": …}, …]`` format.
        user_context:
            Optional user profile snippet to personalise advice.
        """
        ctx_block = ""
        if user_context:
            ctx_parts: list[str] = []
            if user_context.get("name"):
                ctx_parts.append(f"Name: {user_context['name']}")
            if user_context.get("age"):
                ctx_parts.append(f"Age: {user_context['age']}")
            if user_context.get("weight"):
                ctx_parts.append(f"Weight: {user_context['weight']} kg")
            if user_context.get("dietaryPrefs"):
                ctx_parts.append(f"Diet: {', '.join(user_context['dietaryPrefs'])}")
            if user_context.get("monthlyBudget"):
                ctx_parts.append(f"Monthly budget: ₹{user_context['monthlyBudget']}")
            if ctx_parts:
                ctx_block = "\n\nCurrent user profile:\n" + "\n".join(ctx_parts)

        system_message = (
            "You are BudgetBites AI Coach — a friendly nutrition and budget expert "
            "specialising in Indian cuisine and healthy eating on a budget. "
            "You provide practical, culturally relevant advice on meal planning, "
            "grocery shopping, nutrition, and cooking techniques. "
            "Keep responses concise, warm, and actionable. "
            "Use ₹ (INR) for all prices." + ctx_block
        )

        full_messages = [{"role": "system", "content": system_message}, *messages]

        result = await self._chat(
            full_messages,
            model="gpt-4o-mini",
            json_mode=False,
            temperature=0.8,
        )
        if isinstance(result, dict):
            return json.dumps(result)
        return result


ai_service = AIService()
