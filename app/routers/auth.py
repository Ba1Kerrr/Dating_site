# routers/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from database.database import info_user
from funcs.hash import verify_password
from funcs.jwt_auth import (
    create_access_token, create_refresh_token, decode_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


class TokenRequest(BaseModel):
    username: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
async def get_token(data: TokenRequest):
    """
    Получить JWT токены по логину и паролю.
    Используется для API клиентов (мобилка, Postman и т.д.)
    """
    user = info_user(data.username)
    if user is None or not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return TokenResponse(
        access_token=create_access_token(data.username),
        refresh_token=create_refresh_token(data.username),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest):
    """
    Обновить access токен по refresh токену.
    Вызывать когда access истёк (401).
    """
    payload = decode_token(data.refresh_token)

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Expected refresh token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Проверяем что пользователь ещё существует
    user = info_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(username),
        refresh_token=create_refresh_token(username),
    )


@router.get("/me")
async def get_me(username: str = Depends(__import__("funcs.jwt_auth", fromlist=["get_current_user"]).get_current_user)):
    """Проверить токен и получить данные текущего пользователя"""
    user = info_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # не возвращаем пароль
    return {k: v for k, v in user.items() if k != "password"}