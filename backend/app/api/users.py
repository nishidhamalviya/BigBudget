"""User profile endpoints: view, update, and delete."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from prisma import Prisma

from app.core.dependencies import get_current_user, get_db
from app.schemas.auth import MessageResponse
from app.schemas.user import UserProfile, UserProfileUpdate

router = APIRouter(prefix="/users", tags=["Users"])


# ── GET /users/profile ───────────────────────────────────────────────────────


@router.get(
    "/profile",
    response_model=UserProfile,
    summary="Get the authenticated user's profile",
)
async def get_profile(
    current_user: dict = Depends(get_current_user),
) -> UserProfile:
    """Return the full profile of the currently authenticated user."""

    return UserProfile.model_validate(current_user)


# ── PUT /users/profile ───────────────────────────────────────────────────────


@router.put(
    "/profile",
    response_model=UserProfile,
    summary="Update profile fields",
)
async def update_profile(
    body: UserProfileUpdate,
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> UserProfile:
    """Partially update the authenticated user's profile.

    Only non-``None`` fields in the request body are written to the database.
    """

    update_data = body.model_dump(exclude_unset=True)
    if not update_data:
        # Nothing to update – return current profile as-is
        return UserProfile.model_validate(current_user)

    updated_user = await db.user.update(
        where={"id": current_user.id},
        data=update_data,
    )
    return UserProfile.model_validate(updated_user)


# ── DELETE /users/profile ────────────────────────────────────────────────────


@router.delete(
    "/profile",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete the authenticated user's account",
)
async def delete_profile(
    current_user: dict = Depends(get_current_user),
    db: Prisma = Depends(get_db),
) -> MessageResponse:
    """Permanently delete the user account and all associated data.

    Prisma cascading deletes will remove related meal plans, chat history,
    and any other child records.
    """

    await db.user.delete(where={"id": current_user.id})
    return MessageResponse(message="Account deleted successfully")
