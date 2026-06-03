"""
Core dependency injection for FastAPI.

Provides reusable ``Depends(...)`` callables for:
- Prisma database client
- Redis async connection
- JWT-authenticated current user
"""

from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from prisma import Prisma

from app.core.config import settings

# ── OAuth2 scheme ────────────────────────────────────────────
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Prisma singleton ────────────────────────────────────────
_db: Prisma | None = None


async def get_db() -> AsyncGenerator[Prisma, None]:
    """Yield a connected Prisma client, creating one on first call."""
    global _db
    if _db is None:
        _db = Prisma()
        await _db.connect()
    yield _db


# ── Redis pool ───────────────────────────────────────────────
_redis_pool: aioredis.Redis | None = None


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """Yield a Redis connection from the shared pool."""
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = aioredis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    yield _redis_pool


# ── Current authenticated user ───────────────────────────────

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Prisma = Depends(get_db),
) -> dict:
    """Decode the JWT and return the corresponding user record.

    Raises ``401`` if the token is invalid or the user no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.user.find_unique(where={"id": user_id})
    if user is None:
        raise credentials_exception

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "age": user.age,
        "weight": user.weight,
        "height": user.height,
        "activityLevel": user.activityLevel,
        "dietaryPrefs": user.dietaryPrefs or [],
        "allergies": user.allergies or [],
        "monthlyBudget": user.monthlyBudget,
        "currency": user.currency,
        "avatarUrl": user.avatarUrl,
    }
