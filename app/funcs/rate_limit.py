from fastapi import Request, HTTPException
from collections import defaultdict
from datetime import datetime, timedelta
import asyncio
import time
from typing import Dict, List
import json
from datetime import timezone

# Хранилище запросов
_request_log: Dict[str, List[datetime]] = defaultdict(list)
_lock = asyncio.Lock()

# Статистика для мониторинга
_stats = {
    "total_blocked": 0,
    "total_requests": 0,
    "by_endpoint": defaultdict(lambda: {"requests": 0, "blocked": 0}),
    "by_ip": defaultdict(lambda: {"requests": 0, "blocked": 0}),
}


async def rate_limit(
    request: Request, 
    max_requests: int = 10, 
    window_seconds: int = 60,
    endpoint_name: str = None
):
    """
    Dependency для защиты эндпоинтов от брутфорса.
    """
    ip = request.client.host
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    window_start = now - timedelta(seconds=window_seconds)
    
    # Для статистики
    endpoint = endpoint_name or request.url.path
    
    async with _lock:
        # Обновляем статистику
        _stats["total_requests"] += 1
        _stats["by_endpoint"][endpoint]["requests"] += 1
        _stats["by_ip"][ip]["requests"] += 1
        
        # Чистим старые записи
        _request_log[ip] = [t for t in _request_log[ip] if t > window_start]
        
        # Проверяем лимит
        if len(_request_log[ip]) >= max_requests:
            # Считаем блокировки
            _stats["total_blocked"] += 1
            _stats["by_endpoint"][endpoint]["blocked"] += 1
            _stats["by_ip"][ip]["blocked"] += 1
            
            # Вычисляем когда можно будет снова
            oldest = _request_log[ip][0]
            retry_after = (oldest + timedelta(seconds=window_seconds) - now).seconds
            
            raise HTTPException(
                status_code=429,
                headers={"Retry-After": str(retry_after)},
                detail={
                    "error": "Too many requests",
                    "retry_after": retry_after,
                    "limit": max_requests,
                    "window_seconds": window_seconds
                }
            )
        
        _request_log[ip].append(now)


def make_rate_limiter(max_requests: int = 10, window_seconds: int = 60, endpoint: str = None):
    """
    Фабрика для создания лимитеров с разными настройками.
    """
    async def limiter(request: Request):
        await rate_limit(
            request, 
            max_requests=max_requests, 
            window_seconds=window_seconds,
            endpoint_name=endpoint
        )
    return limiter


# Эндпоинт для мониторинга (добавить в main.py или отдельный роутер)
async def get_rate_limit_stats(request: Request):
    """
    Возвращает статистику rate limiter'а.
    Защити этот эндпоинт паролем или IP-ограничением!
    """
    # Простая защита - только localhost
    if request.client.host not in ["127.0.0.1", "::1", "localhost"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    async with _lock:
        # Топ-10 самых активных IP
        top_ips = sorted(
            _stats["by_ip"].items(),
            key=lambda x: x[1]["requests"],
            reverse=True
        )[:10]
        
        # Топ-10 самых блокируемых IP
        top_blocked_ips = sorted(
            [(ip, data["blocked"]) for ip, data in _stats["by_ip"].items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Статистика по эндпоинтам
        endpoints_stats = []
        for endpoint, data in _stats["by_endpoint"].items():
            block_rate = (data["blocked"] / data["requests"] * 100) if data["requests"] > 0 else 0
            endpoints_stats.append({
                "endpoint": endpoint,
                "requests": data["requests"],
                "blocked": data["blocked"],
                "block_rate_percent": round(block_rate, 2)
            })
        
        # Текущая нагрузка (последние 5 минут)
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        five_min_ago = now - timedelta(minutes=5)
        current_load = 0
        for times in _request_log.values():
            current_load += len([t for t in times if t > five_min_ago])
        
        return {
            "summary": {
                "total_requests": _stats["total_requests"],
                "total_blocked": _stats["total_blocked"],
                "global_block_rate_percent": round(
                    _stats["total_blocked"] / _stats["total_requests"] * 100 
                    if _stats["total_requests"] > 0 else 0, 2
                ),
                "active_ips": len(_request_log),
                "current_load_5min": current_load,
                "timestamp": now.isoformat()
            },
            "top_active_ips": [
                {"ip": ip, "requests": data["requests"], "blocked": data["blocked"]}
                for ip, data in top_ips
            ],
            "top_blocked_ips": [
                {"ip": ip, "blocked": blocked}
                for ip, blocked in top_blocked_ips if blocked > 0
            ],
            "endpoints": sorted(endpoints_stats, key=lambda x: x["requests"], reverse=True)
        }


# Периодическая очистка старых данных
async def cleanup_old_stats():
    """Очищает старые записи раз в час"""
    while True:
        await asyncio.sleep(3600)  # час
        async with _lock:
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            hour_ago = now - timedelta(hours=1)
            
            # Очищаем лог запросов
            for ip in list(_request_log.keys()):
                _request_log[ip] = [t for t in _request_log[ip] if t > hour_ago]
                if not _request_log[ip]:
                    del _request_log[ip]
            
            # Сбрасываем статистику по IP раз в сутки (оставляем только агрегированную)
            if now.hour == 3:  # в 3 ночи
                _stats["by_ip"].clear()


# Готовые лимитеры для роутов
login_rate_limit    = make_rate_limiter(max_requests=5,  window_seconds=60, endpoint="login")
register_rate_limit = make_rate_limiter(max_requests=3,  window_seconds=300, endpoint="register")
token_rate_limit    = make_rate_limiter(max_requests=10, window_seconds=60, endpoint="token")
forgot_rate_limit   = make_rate_limiter(max_requests=3,  window_seconds=300, endpoint="forgot")