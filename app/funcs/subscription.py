"""
app/funcs/subscription.py

Утилиты для работы с подписками.
Используется в роутерах и как FastAPI Depends().
"""
from __future__ import annotations

import os
import psycopg2
from datetime import datetime, timezone
from functools import lru_cache
from fastapi import HTTPException, Request, Depends
from funcs.jwt_auth import get_current_user_flexible as get_current_user

DATABASE_URL = os.environ.get("DATABASE_URL", "")


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


# ── Базовые операции ─────────────────────────────────────────────────

def get_user_plan(username: str) -> str:
    """
    Вернуть план пользователя: 'free' | 'premium'.
    Если записи нет — считаем free.
    """
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.plan
            FROM subscriptions s
            JOIN users u ON u.id = s.user_id
            WHERE u.username = %s
              AND s.is_active = TRUE
              AND (s.expires_at IS NULL OR s.expires_at > NOW())
            ORDER BY s.started_at DESC
            LIMIT 1
            """,
            (username,),
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "free"
    except Exception:
        return "free"


def is_premium(username: str) -> bool:
    return get_user_plan(username) == "premium"


def activate_premium(username: str, days: int = 30, payment_id: str | None = None) -> bool:
    """Активировать Premium на N дней."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        # Деактивируем старые подписки
        cur.execute(
            "UPDATE subscriptions SET is_active = FALSE FROM users u WHERE u.username = %s AND subscriptions.user_id = u.id",
            (username,),
        )
        # Вставляем новую
        cur.execute(
            """
            INSERT INTO subscriptions (user_id, plan, is_active, expires_at, payment_id)
            SELECT id, 'premium', TRUE,
                   NOW() + INTERVAL '%s days',
                   %s
            FROM users WHERE username = %s
            """,
            (days, payment_id, username),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False


def ensure_free_subscription(username: str):
    """Создать free-подписку если её нет. Вызывать при регистрации."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO subscriptions (user_id, plan, is_active)
            SELECT id, 'free', TRUE FROM users WHERE username = %s
            ON CONFLICT DO NOTHING
            """,
            (username,),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


# ── Просмотры профилей ───────────────────────────────────────────────

def record_profile_view(viewer_username: str, target_username: str):
    """Записать просмотр профиля. Дубли в течение суток игнорируются."""
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO profile_views (viewer_id, target_id)
            SELECT v.id, t.id
            FROM users v, users t
            WHERE v.username = %s AND t.username = %s
            ON CONFLICT (viewer_id, target_id, (viewed_at::date)) DO NOTHING
            """,
            (viewer_username, target_username),
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def get_profile_viewers(username: str, limit: int = 20) -> list[dict]:
    """
    Кто смотрел профиль — только для Premium.
    Возвращает список просмотров за последние 30 дней.
    """
    try:
        conn = _get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT u.username, u.name, u.avatar,
                   pv.viewed_at
            FROM profile_views pv
            JOIN users t ON t.id = pv.target_id
            JOIN users u ON u.id = pv.viewer_id
            WHERE t.username = %s
              AND pv.viewed_at > NOW() - INTERVAL '30 days'
            ORDER BY pv.viewed_at DESC
            LIMIT %s
            """,
            (username, limit),
        )
        rows = cur.fetchall()
        conn.close()
        return [
            {
                "username": r[0],
                "name": r[1],
                "avatar": r[2],
                "viewed_at": r[3].isoformat() if r[3] else None,
            }
            for r in rows
        ]
    except Exception:
        return []


# ── FastAPI Dependencies ─────────────────────────────────────────────

async def require_premium(current_user: str = Depends(get_current_user)):
    """
    Dependency: endpoint доступен только Premium-пользователям.

    Использование:
        @router.get("/premium-feature")
        async def feature(user = Depends(require_premium)):
            ...
    """
    if not is_premium(current_user):
        raise HTTPException(
            status_code=403,
            detail={
                "error": "premium_required",
                "message": "Эта функция доступна только пользователям Premium",
                "upgrade_url": "/subscription",
            },
        )
    return current_user


async def get_subscription_info(current_user: str = Depends(get_current_user)):
    """Dependency: возвращает план текущего пользователя."""
    return {
        "username": current_user,
        "plan": get_user_plan(current_user),
        "is_premium": is_premium(current_user),
    }