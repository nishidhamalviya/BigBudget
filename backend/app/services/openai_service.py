import os
import json
from openai import OpenAI

# Attempt to load from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy-key"))

def is_configured() -> bool:
    key = os.getenv("OPENAI_API_KEY")
    return key is not None and key != "" and key != "dummy-key"

def generate_meal_plan(budget: float, goal: str, diet: str, meals_count: int) -> dict:
    if not is_configured():
        # Return mock data if no real key is set so frontend can be tested without errors
        return {
            "total_calories": 2100,
            "total_protein": 140,
            "total_cost": budget * 0.9,
            "meals": [
                {"name": "Oatmeal & Eggs", "calories": 400, "protein": 25, "cost": 40},
                {"name": "Chicken Rice Bowl", "calories": 700, "protein": 50, "cost": 100},
                {"name": "Lentil Soup", "calories": 500, "protein": 20, "cost": 50},
                {"name": "Greek Yogurt", "calories": 500, "protein": 45, "cost": 35}
            ][:meals_count]
        }
    
    # Real logic
    prompt = f"""
    Create a highly nutritional meal plan for a {diet} diet within a daily budget of {budget} INR.
    Goal: {goal}. Number of meals: {meals_count}.
    Output strictly in JSON format matching this structure:
    {{
      "total_calories": int,
      "total_protein": int,
      "total_cost": float,
      "meals": [
        {{"name": str, "calories": int, "protein": int, "cost": float}}
      ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}

def analyze_food_order(restaurant: str, items: str, cost: float) -> dict:
    if not is_configured():
        return {
            "calories": 1250,
            "protein": 45,
            "fat": 65,
            "carbs": 120,
            "healthScore": 4.2,
            "costEfficiency": 3.5,
            "alternatives": ["Make it at home for ₹120", "Order a healthy bowl instead for ₹180"],
            "savings": 150
        }
    
    prompt = f"""
    Analyze the following food order from '{restaurant}'.
    Items: {items}. Total Cost: {cost} INR.
    Provide nutritional estimates and budget efficiency score (1-10).
    Output strictly in JSON format:
    {{
      "calories": int,
      "protein": int,
      "fat": int,
      "carbs": int,
      "healthScore": float,
      "costEfficiency": float,
      "alternatives": ["string"],
      "savings": int
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"error": str(e)}
