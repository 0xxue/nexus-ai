"""
Admin API — Management endpoints (admin role required)

GET  /admin/audit-logs     → Query audit logs
GET  /admin/stats          → Usage statistics
GET  /admin/users          → User list (placeholder)
PUT  /admin/model-config   → Model configuration (placeholder)
POST /admin/feedback       → Submit feedback on QA answer
"""

import structlog
from fastapi import APIRouter, Depends, Query
from typing import Optional

from app.middleware.rbac import require_role, require_permission
from app.middleware.audit import get_audit_logs, get_usage_stats
from app.services.auth import get_current_user

router = APIRouter()
logger = structlog.get_logger()

# In-memory feedback store
_feedback: list[dict] = []


# ========== Audit Logs ==========

@router.get("/audit-logs")
async def list_audit_logs(
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin=Depends(require_role("admin")),
):
    """Query audit logs. Admin only."""
    return await get_audit_logs(user_id=user_id, action=action, limit=limit, offset=offset)


# ========== Usage Statistics ==========

@router.get("/stats")
async def usage_stats(admin=Depends(require_role("admin"))):
    """Aggregated usage statistics. Admin only."""
    return await get_usage_stats()


# ========== Feedback ==========

@router.post("/feedback")
async def submit_feedback(
    message_id: int,
    rating: int,  # 1 = thumbs up, -1 = thumbs down
    comment: str = "",
    user=Depends(get_current_user),
):
    """Submit feedback on a QA answer. Any authenticated user."""
    entry = {
        "id": len(_feedback) + 1,
        "message_id": message_id,
        "user_id": int(user.id),
        "rating": rating,
        "comment": comment,
    }
    _feedback.append(entry)
    logger.info("Feedback submitted", message_id=message_id, rating=rating)
    return {"status": "ok", "feedback_id": entry["id"]}


@router.get("/feedback")
async def list_feedback(
    limit: int = Query(50),
    admin=Depends(require_role("admin")),
):
    """List all feedback. Admin only."""
    sorted_fb = sorted(_feedback, key=lambda x: x["id"], reverse=True)
    return {"total": len(_feedback), "feedback": sorted_fb[:limit]}
