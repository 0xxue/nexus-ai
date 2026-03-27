"""
RBAC (Role-Based Access Control) Middleware

Roles:
  - admin: Full access (all endpoints + management)
  - user: Standard access (QA + knowledge base + own data)
  - readonly: View only (no create/delete/upload)

Usage:
    @app.get("/admin/users")
    async def list_users(user=Depends(require_role("admin"))):
        ...
"""

from fastapi import Depends, HTTPException
from app.services.auth import get_current_user


ROLE_HIERARCHY = {
    "admin": 3,
    "user": 2,
    "readonly": 1,
}

# Permission matrix: role → allowed actions
PERMISSIONS = {
    "admin": {"qa_ask", "qa_stream", "kb_upload", "kb_delete", "kb_search",
              "data_read", "report_generate", "admin_users", "admin_audit",
              "admin_config", "feedback"},
    "user": {"qa_ask", "qa_stream", "kb_upload", "kb_delete", "kb_search",
             "data_read", "report_generate", "feedback"},
    "readonly": {"qa_ask", "kb_search", "data_read"},
}


def require_role(min_role: str):
    """
    Dependency: require minimum role level.
    Usage: user = Depends(require_role("admin"))
    """
    min_level = ROLE_HIERARCHY.get(min_role, 0)

    async def check(user=Depends(get_current_user)):
        user_level = ROLE_HIERARCHY.get(user.role, 0)
        if user_level < min_level:
            raise HTTPException(
                status_code=403,
                detail=f"Requires {min_role} role. Your role: {user.role}",
            )
        return user

    return check


def require_permission(permission: str):
    """
    Dependency: require specific permission.
    Usage: user = Depends(require_permission("kb_upload"))
    """
    async def check(user=Depends(get_current_user)):
        user_permissions = PERMISSIONS.get(user.role, set())
        if permission not in user_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied: {permission}. Your role: {user.role}",
            )
        return user

    return check
