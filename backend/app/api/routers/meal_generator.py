from fastapi import APIRouter
from pydantic import BaseModel
from app.services.openai_service import generate_meal_plan

router = APIRouter()

class MealPlanRequest(BaseModel):
    budget: float
    goal: str
    diet: str
    meals_count: int

@router.post("/generate")
def create_meal_plan(request: MealPlanRequest):
    plan = generate_meal_plan(
        budget=request.budget,
        goal=request.goal,
        diet=request.diet,
        meals_count=request.meals_count
    )
    return plan
