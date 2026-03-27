"""
Authentication Endpoints

JWT-based auth with access + refresh tokens.
"""

from fastapi import APIRouter, Depends, HTTPException
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest
from app.services.auth import authenticate_user, create_tokens, refresh_access_token

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    user = await authenticate_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    tokens = create_tokens(user)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(request: RefreshRequest):
    tokens = await refresh_access_token(request.refresh_token)
    if not tokens:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    return tokens
