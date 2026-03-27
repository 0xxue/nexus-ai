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
