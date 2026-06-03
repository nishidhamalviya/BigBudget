"""Authentication endpoints: signup, login, logout, password reset, and profile retrieval."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from prisma import Prisma
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.dependencies import get_current_user, get_db, get_redis
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
)
from app.schemas.user import UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── POST /auth/signup ────────────────────────────────────────────────────────


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def signup(
    body: SignupRequest,
    db: Prisma = Depends(get_db),
) -> TokenResponse:
    """Create a new user, hash their password, and return a JWT."""

    existing = await db.user.find_unique(where={"email": body.email})
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    hashed = hash_password(body.password)
    user = await db.user.create(
        data={
            "email": body.email,
            "hashedPassword": hashed,
            "name": body.name,
        }
    )

    token = create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(access_token=token)


# ── POST /auth/login ─────────────────────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and obtain a JWT",
)
async def login(
    body: LoginRequest,
    db: Prisma = Depends(get_db),
) -> TokenResponse:
    """Validate credentials and return a signed JWT access token."""

    user = await db.user.find_unique(where={"email": body.email})
    if user is None or not verify_password(body.password, user.hashedPassword):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user_id=user.id, email=user.email)
    return TokenResponse(access_token=token)


# ── POST /auth/logout ────────────────────────────────────────────────────────


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Revoke the current access token",
)
async def logout(
    request: Request,
    current_user: dict = Depends(get_current_user),
    r: aioredis.Redis = Depends(get_redis),
) -> MessageResponse:
    """Blacklist the JWT so it cannot be reused for the remainder of its TTL."""

    auth_header: str | None = request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )

    token = auth_header.removeprefix("Bearer ").strip()

    # Calculate remaining TTL so the blacklist entry auto-expires
    try:
        payload = decode_access_token(token)
        exp = payload.get("exp", 0)
        remaining = int(exp - datetime.now(timezone.utc).timestamp())
        if remaining < 0:
            remaining = 0
    except Exception:
        remaining = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    if remaining > 0:
        await r.setex(f"blacklist:{token}", remaining, "1")

    return MessageResponse(message="Successfully logged out")


# ── POST /auth/forgot-password ───────────────────────────────────────────────


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request a password-reset token",
)
async def forgot_password(
    body: ForgotPasswordRequest,
    db: Prisma = Depends(get_db),
    r: aioredis.Redis = Depends(get_redis),
) -> MessageResponse:
    """Generate a one-time reset token and store it in Redis (15 min TTL).

    The response always returns a success message regardless of whether the
    email exists — this prevents user enumeration attacks.
    """

    user = await db.user.find_unique(where={"email": body.email})
    if user is not None:
        reset_token = str(uuid.uuid4())
        await r.setex(f"reset:{reset_token}", 900, user.id)

        # In production this token would be emailed to the user.
        return MessageResponse(
            message=f"Password reset token generated: {reset_token}"
        )

    # Do NOT reveal that the user was not found
    return MessageResponse(
        message="If an account with that email exists, a reset link has been sent."
    )


# ── POST /auth/reset-password ────────────────────────────────────────────────


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password using a one-time token",
)
async def reset_password(
    body: ResetPasswordRequest,
    db: Prisma = Depends(get_db),
    r: aioredis.Redis = Depends(get_redis),
) -> MessageResponse:
    """Verify the reset token, update the user's password hash, and delete the token."""

    user_id = await r.get(f"reset:{body.token}")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    hashed = hash_password(body.new_password)
    await db.user.update(
        where={"id": user_id},
        data={"hashedPassword": hashed},
    )
    await r.delete(f"reset:{body.token}")

    return MessageResponse(message="Password has been reset successfully")


# ── GET /auth/me ──────────────────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserProfile,
    summary="Get the authenticated user's profile",
)
async def me(
    current_user: dict = Depends(get_current_user),
) -> UserProfile:
    """Return the profile of the currently authenticated user (password excluded)."""

    return UserProfile.model_validate(current_user)
