"""BudgetBites FastAPI application entry point.

Start with:
    uvicorn app.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dependencies import db_client
from app.core import dependencies
from app.core.exceptions import register_exception_handlers
from app.api.routers import meal_generator
from app.api.routers import analyzer


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application-wide startup and shutdown events.

    Startup:
        1. Connect the Prisma database client.
        2. Initialise the async Redis connection pool.

    Shutdown:
        1. Disconnect from the database.
        2. Close the Redis connection pool.
    """

    # ── Startup ───────────────────────────────────────────────────
    # await db_client.connect()
    # dependencies.redis_client = aioredis.from_url(
    #     settings.REDIS_URL,
    #     decode_responses=True,
    # )

    yield

    # ── Shutdown ──────────────────────────────────────────────────
    # await db_client.disconnect()
    # if dependencies.redis_client is not None:
    #     await dependencies.redis_client.aclose()


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="AI-powered budget-conscious meal planning API",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

register_exception_handlers(app)


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

from app.api import analytics, auth, chat, diet, grocery, ingredients, meals, users  # noqa: E402

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meals.router)
app.include_router(ingredients.router)
app.include_router(grocery.router)
app.include_router(diet.router)
app.include_router(chat.router)
app.include_router(analytics.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Lightweight liveness probe for load balancers and container orchestrators."""
    return {"status": "healthy", "service": settings.APP_NAME}
