# funcs/jwt_auth.py
from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, WebSocket
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "changeme-set-in-env")
ALGORITHM  = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES  = 30
REFRESH_TOKEN_EXPIRE_DAYS    = 30

bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": username, "exp": expire, "type": "access"},
        SECRET_KEY, algorithm=ALGORITHM
    )


def create_refresh_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": username, "exp": expire, "type": "refresh"},
        SECRET_KEY, algorithm=ALGORITHM
    )


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> str:
    """
    Dependency для защищённых эндпоинтов.
    Поддерживает Bearer токен.
    Использование: user = Depends(get_current_user)
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    payload = decode_token(credentials.credentials)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Expected access token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return username


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)
) -> Optional[str]:
    """Та же проверка но не падает если токена нет — для смешанных роутов"""
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return payload.get("sub")
    except HTTPException:
        return None


def get_user_from_websocket(websocket: WebSocket) -> str:
    """
    Достаёт токен из query param для WebSocket.
    ws://host/chat/ws/anna?token=eyJ...
    """
    token = websocket.query_params.get("token")
    if not token:
        raise HTTPException(status_code=401, detail="Token required")

    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Expected access token")

    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    return username