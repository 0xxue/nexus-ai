"""
Health Check Endpoints

- /health          → Docker/K8s liveness probe
- /api/v1/health   → Detailed dependency checks
- /metrics         → Prometheus (auto-mounted)
"""

import time
from fastapi import APIRouter

router = APIRouter()
START_TIME = time.time()


@router.get("/health")
async def liveness():
    return {"status": "ok"}


@router.get("/health/detailed")
async def detailed_health():
    from app.services.database import check_db
    from app.services.cache import check_redis

    db_ok = await check_db()
    redis_ok = await check_redis()

    return {
        "status": "ok" if (db_ok and redis_ok) else "degraded",
        "uptime_seconds": int(time.time() - START_TIME),
        "version": "3.0.0",
        "dependencies": {
            "postgresql": "healthy" if db_ok else "unhealthy",
            "redis": "healthy" if redis_ok else "unhealthy",
        },
    }


@router.get("/stats")
async def system_stats():
    """Real system stats from database for Dashboard."""
    from app.services.database import _session_factory
    from sqlalchemy import text

    stats = {
        "total_users": 0,
        "total_conversations": 0,
        "total_messages": 0,
        "total_documents": 0,
        "total_collections": 0,
        "system_health": "healthy",
        "uptime_seconds": int(time.time() - START_TIME),
    }

    if not _session_factory:
        return stats

    try:
        async with _session_factory() as session:
            for table, key in [
                ("users", "total_users"),
                ("conversations", "total_conversations"),
                ("messages", "total_messages"),
                ("kb_documents", "total_documents"),
                ("kb_collections", "total_collections"),
            ]:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                stats[key] = result.scalar() or 0
    except Exception:
        pass

    return stats
