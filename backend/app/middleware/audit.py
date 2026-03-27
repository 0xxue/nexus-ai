"""
Audit Log Middleware — Records all QA interactions for compliance

Every question asked and answer generated is logged with:
- Who asked (user_id)
- What they asked (query)
- What AI answered (preview)
- Which model was used
- How many tokens consumed
- Confidence score
- IP address
"""

import structlog
from datetime import datetime
from typing import Optional

logger = structlog.get_logger()

# In-memory audit store (replace with DB in production)
_audit_logs: list[dict] = []


async def log_audit(
    user_id: int,
    action: str,
    query: str = "",
    answer_preview: str = "",
    model_used: str = "",
    tokens_consumed: int = 0,
    confidence: float = 0,
    ip_address: str = "",
):
    """Record an audit log entry."""
    entry = {
        "id": len(_audit_logs) + 1,
        "user_id": user_id,
        "action": action,
        "query": query,
        "answer_preview": answer_preview[:500],
        "model_used": model_used,
        "tokens_consumed": tokens_consumed,
        "confidence": round(confidence, 2),
        "ip_address": ip_address,
        "created_at": datetime.now().isoformat(),
    }
    _audit_logs.append(entry)
    logger.info("Audit logged", action=action, user_id=user_id)


async def get_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """Query audit logs with filters."""
    filtered = _audit_logs

    if user_id:
        filtered = [l for l in filtered if l["user_id"] == user_id]
    if action:
        filtered = [l for l in filtered if l["action"] == action]

    total = len(filtered)
    filtered = sorted(filtered, key=lambda x: x["created_at"], reverse=True)
    page = filtered[offset:offset + limit]

    return {"total": total, "logs": page}


async def get_usage_stats() -> dict:
    """Aggregate usage statistics from audit logs."""
    total_queries = len([l for l in _audit_logs if l["action"] == "qa_ask"])
    total_tokens = sum(l.get("tokens_consumed", 0) for l in _audit_logs)
    avg_confidence = 0
    confidence_logs = [l for l in _audit_logs if l.get("confidence", 0) > 0]
    if confidence_logs:
        avg_confidence = sum(l["confidence"] for l in confidence_logs) / len(confidence_logs)

    # Model distribution
    model_counts = {}
    for l in _audit_logs:
        model = l.get("model_used", "unknown")
        model_counts[model] = model_counts.get(model, 0) + 1

    # Action distribution
    action_counts = {}
    for l in _audit_logs:
        action = l.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1

    return {
        "total_queries": total_queries,
        "total_tokens": total_tokens,
        "avg_confidence": round(avg_confidence, 2),
        "model_distribution": model_counts,
        "action_distribution": action_counts,
        "total_users": len(set(l["user_id"] for l in _audit_logs)),
    }
