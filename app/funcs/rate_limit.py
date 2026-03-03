# funcs/rate_limit.py
from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio

# { ip: [timestamp, timestamp, ...] }
_request_log: dict[str, list] = defaultdict(list)
_lock = asyncio.Lock()


async def rate_limit(request: Request, max_requests: int = 10, window_seconds: int = 60):
    """
    Dependency для защиты эндпоинтов от брутфорса.

    Использование:
        @router.post("/login")
        async def login(request: Request, _=Depends(login_rate_limit)):
            ...
    """
    ip = request.client.host
    now = datetime.utcnow()
    window_start = now - timedelta(seconds=window_seconds)

    async with _lock:
        # Чистим старые записи
        _request_log[ip] = [t for t in _request_log[ip] if t > window_start]

        if len(_request_log[ip]) >= max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Try again in {window_seconds} seconds."
            )

        _request_log[ip].append(now)


def make_rate_limiter(max_requests: int = 10, window_seconds: int = 60):
    """
    Фабрика для создания лимитеров с разными настройками.

    Пример:
        login_rate_limit    = make_rate_limiter(max_requests=5,  window_seconds=60)
        register_rate_limit = make_rate_limiter(max_requests=3,  window_seconds=300)
        token_rate_limit    = make_rate_limiter(max_requests=10, window_seconds=60)
    """
    async def limiter(request: Request):
        await rate_limit(request, max_requests=max_requests, window_seconds=window_seconds)

    return limiter


# Готовые лимитеры для роутов
login_rate_limit    = make_rate_limiter(max_requests=5,  window_seconds=60)   # 5 попыток в минуту
register_rate_limit = make_rate_limiter(max_requests=3,  window_seconds=300)  # 3 регистрации в 5 минут
token_rate_limit    = make_rate_limiter(max_requests=10, window_seconds=60)   # 10 запросов токена в минуту
forgot_rate_limit   = make_rate_limiter(max_requests=3,  window_seconds=300)  # 3 попытки сброса в 5 минут