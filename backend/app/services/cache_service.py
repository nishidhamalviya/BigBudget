"""Redis caching helper service.

Provides a thin wrapper around ``redis.asyncio`` with JSON serialisation,
key-prefixing, and pattern-based invalidation.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class CacheService:
    """Centralised caching operations backed by Redis."""

    # ── Read ────────────────────────────────────────────────

    async def get(self, redis: aioredis.Redis, key: str) -> dict | list | None:
        """Fetch *key* from Redis and JSON-deserialise it.

        Returns ``None`` on cache-miss or deserialisation failure.
        """
        try:
            raw = await redis.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError, aioredis.RedisError) as exc:
            logger.warning("cache get failed for %s: %s", key, exc)
            return None

    # ── Write ───────────────────────────────────────────────

    async def set(
        self,
        redis: aioredis.Redis,
        key: str,
        value: Any,
        ttl: int = 300,
    ) -> None:
        """JSON-serialise *value* and store it in Redis with a TTL (seconds)."""
        try:
            serialised = json.dumps(value, default=str)
            await redis.setex(key, ttl, serialised)
        except (TypeError, aioredis.RedisError) as exc:
            logger.warning("cache set failed for %s: %s", key, exc)

    # ── Delete ──────────────────────────────────────────────

    async def delete(self, redis: aioredis.Redis, key: str) -> None:
        """Remove a single key from the cache."""
        try:
            await redis.delete(key)
        except aioredis.RedisError as exc:
            logger.warning("cache delete failed for %s: %s", key, exc)

    async def delete_pattern(self, redis: aioredis.Redis, pattern: str) -> None:
        """Scan for all keys matching *pattern* and delete them.

        Uses ``SCAN`` (cursor-based) to avoid blocking Redis with ``KEYS``.
        """
        try:
            cursor: int | bytes = 0
            while True:
                cursor, keys = await redis.scan(cursor=cursor, match=pattern, count=100)
                if keys:
                    await redis.delete(*keys)
                if cursor == 0:
                    break
        except aioredis.RedisError as exc:
            logger.warning("cache delete_pattern failed for %s: %s", pattern, exc)

    # ── Key builder ─────────────────────────────────────────

    @staticmethod
    def make_key(*parts: str) -> str:
        """Build a namespaced cache key.

        >>> CacheService.make_key("meals", "user123", "page1")
        'bb:meals:user123:page1'
        """
        return "bb:" + ":".join(parts)


cache_service = CacheService()
