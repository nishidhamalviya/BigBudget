"""Meal generation and history endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import MessageResponse
from app.schemas.meal import MealGenerateRequest, MealListResponse, MealResponse
from app.services.meal_service import meal_service

router = APIRouter(prefix="/meal", tags=["Meals"])


# ── POST /meal/generate ──────────────────────────────────────────────────────


@router.post(
    "/generate",
    response_model=MealResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a new AI-powered meal",
)
async def generate_meal(
    body: MealGenerateRequest,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> MealResponse:
    """Use the AI meal service to generate a meal based on user preferences,
    budget, and dietary constraints.  The generated meal is persisted to the
    database and returned.
    """

    result = await meal_service.generate_meal(
        user=current_user,
        request=body,
        db=db,
    )
    return result


# ── GET /meal/history ─────────────────────────────────────────────────────────


@router.get(
    "/history",
    response_model=MealListResponse,
    summary="List meal history (paginated)",
)
async def get_history(
    page: int = Query(default=1, ge=1, description="Page number"),
    pageSize: int = Query(default=10, ge=1, le=100, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> MealListResponse:
    """Return the authenticated user's meal history, newest first."""

    result = await meal_service.get_history(
        user_id=current_user.id,
        page=page,
        page_size=pageSize,
        db=db,
    )
    return result


# ── GET /meal/{id} ────────────────────────────────────────────────────────────


@router.get(
    "/{id}",
    response_model=MealResponse,
    summary="Get a single meal by ID",
)
async def get_meal(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> MealResponse:
    """Retrieve a specific meal belonging to the authenticated user."""

    result = await meal_service.get_meal(
        meal_id=id,
        user_id=current_user.id,
        db=db,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )
    return result


# ── DELETE /meal/{id} ─────────────────────────────────────────────────────────


@router.delete(
    "/{id}",
    response_model=MessageResponse,
    summary="Delete a meal",
)
async def delete_meal(
    id: str,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> MessageResponse:
    """Delete a meal from the authenticated user's history."""

    deleted = await meal_service.delete_meal(
        meal_id=id,
        user_id=current_user.id,
        db=db,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal not found",
        )
    return MessageResponse(message="Meal deleted successfully")
