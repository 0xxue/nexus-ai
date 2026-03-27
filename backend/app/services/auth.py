"""Auth service - JWT token management."""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import get_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def create_tokens(user) -> dict:
    settings = get_settings()
    access = jwt.encode(
        {"sub": str(user.id), "role": user.role, "exp": datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)},
        settings.jwt_secret, algorithm=settings.jwt_algorithm,
    )
    refresh = jwt.encode(
        {"sub": str(user.id), "exp": datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)},
        settings.jwt_secret, algorithm=settings.jwt_algorithm,
    )
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        # In production: fetch user from database
        from types import SimpleNamespace
        return SimpleNamespace(id=user_id, role=payload.get("role", "user"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def authenticate_user(username: str, password: str):
    # TODO: Fetch from database and verify
    return None


async def refresh_access_token(refresh_token: str):
    # TODO: Validate refresh token and issue new pair
    return None
