"""Redis cache service - multi-layer caching + pub/sub."""

import json
from typing import Optional
import redis.asyncio as aioredis
from app.core.config import get_settings

_redis = None


async def init_redis():
    global _redis
    settings = get_settings()
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)


async def close_redis():
    global _redis
    if _redis:
        await _redis.close()


async def check_redis() -> bool:
    try:
        return await _redis.ping()
    except Exception:
        return False


async def cache_get(key: str) -> Optional[dict]:
    if not _redis:
        return None
    try:
        val = await _redis.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None


async def cache_set(key: str, value: dict, ttl: int = None):
    if not _redis:
        return
    try:
        settings = get_settings()
        await _redis.setex(key, ttl or settings.cache_ttl, json.dumps(value, ensure_ascii=False))
    except Exception:
        pass


async def cache_delete(key: str):
    if not _redis:
        return
    try:
        await _redis.delete(key)
    except Exception:
        pass
