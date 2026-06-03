"""Diet analysis and meal comparison endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.diet import (
    DietAnalysisResponse,
    DietAnalyzeRequest,
    DietCompareRequest,
    DietComparisonResponse,
)
from app.services.diet_service import diet_service

router = APIRouter(prefix="/diet", tags=["Diet Analysis"])


# ── POST /diet/analyze ───────────────────────────────────────────────────────


@router.post(
    "/analyze",
    response_model=DietAnalysisResponse,
    summary="Analyse a food log for nutritional content",
)
async def analyze_diet(
    body: DietAnalyzeRequest,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> DietAnalysisResponse:
    """Accept a free-text food log and return a detailed nutritional breakdown,
    health score, and actionable suggestions.
    """

    result = await diet_service.analyze(
        user=current_user,
        request=body,
        db=db,
    )
    return result


# ── POST /diet/compare ───────────────────────────────────────────────────────


@router.post(
    "/compare",
    response_model=DietComparisonResponse,
    summary="Compare two meals side-by-side",
)
async def compare_meals(
    body: DietCompareRequest,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> DietComparisonResponse:
    """Compare the nutritional profiles of two meals and highlight which one
    better suits the user's dietary goals.
    """

    result = await diet_service.compare(
        user=current_user,
        request=body,
        db=db,
    )
    return result
