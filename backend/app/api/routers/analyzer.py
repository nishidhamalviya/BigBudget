from fastapi import APIRouter
from pydantic import BaseModel
from app.services.openai_service import analyze_food_order

router = APIRouter()

class AnalyzeRequest(BaseModel):
    restaurant: str
    items: str
    cost: float

@router.post("/analyze-order")
def analyze_order(request: AnalyzeRequest):
    analysis = analyze_food_order(
        restaurant=request.restaurant,
        items=request.items,
        cost=request.cost
    )
    return analysis
