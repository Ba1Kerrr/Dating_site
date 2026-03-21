"""
app/routers/subscription.py

Эндпоинты подписок:
  GET  /api/subscription/me          — текущий план
  POST /api/subscription/activate    — активировать (заглушка оплаты)
  GET  /api/subscription/viewers     — кто смотрел профиль [Premium]
  GET  /api/feed/premium             — приоритетная лента [Premium]
  GET  /api/users/filter             — расширенные фильтры [Premium]
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from funcs.jwt_auth import get_current_user_flexible as get_current_user
from funcs.subscription import (
    get_user_plan,
    is_premium,
    activate_premium,
    get_profile_viewers,
    require_premium,
    get_subscription_info,
)
from database.database import get_filtered_users

router = APIRouter(prefix="/api/subscription", tags=["subscription"])


# ── Текущий план ─────────────────────────────────────────────────────

@router.get("/me")
async def my_subscription(
    sub: dict = Depends(get_subscription_info),
):
    """Информация о текущей подписке пользователя."""
    return sub


# ── Активация Premium (заглушка — без реального эквайринга) ──────────

class ActivateRequest(BaseModel):
    plan: str = "premium"          # пока только premium
    days: int = 30
    promo_code: Optional[str] = None  # для тестов: TESTPREMIUM


PROMO_CODES = {"TESTPREMIUM", "SOULMATES2026", "BA1KERRR"}  # тестовые промокоды

@router.post("/activate")
async def activate_subscription(
    body: ActivateRequest,
    current_user: str = Depends(get_current_user),
):
    """
    Активировать Premium-подписку.

    Сейчас — через промокод (заглушка).
    В будущем: интеграция ЮKassa / Stripe.
    """
    if body.plan != "premium":
        raise HTTPException(status_code=400, detail="Доступен только план 'premium'")

    # Проверка промокода
    if body.promo_code:
        if body.promo_code.upper() not in PROMO_CODES:
            raise HTTPException(status_code=400, detail="Неверный промокод")
        ok = activate_premium(current_user, days=body.days, payment_id=f"promo:{body.promo_code}")
        if not ok:
            raise HTTPException(status_code=500, detail="Ошибка активации")
        return {
            "status": "activated",
            "plan": "premium",
            "days": body.days,
            "message": f"Premium активирован на {body.days} дней через промокод",
        }

    # TODO: здесь будет реальный платёж через ЮKassa
    raise HTTPException(
        status_code=402,
        detail={
            "error": "payment_required",
            "message": "Оплата пока недоступна. Используйте промокод для тестирования.",
            "promo_hint": "TESTPREMIUM",
        },
    )


# ── Premium: кто смотрел профиль ─────────────────────────────────────

@router.get("/viewers")
async def profile_viewers(
    current_user: str = Depends(require_premium),
    limit: int = Query(20, ge=1, le=50),
):
    """[Premium] Кто смотрел мой профиль за последние 30 дней."""
    viewers = get_profile_viewers(current_user, limit)
    return {"viewers": viewers, "count": len(viewers)}


# ── Premium: расширенные фильтры в ленте ─────────────────────────────

@router.get("/feed/filtered")
async def premium_feed(
    request: Request,
    current_user: str = Depends(require_premium),
    min_age: Optional[int] = Query(None, ge=18, le=99),
    max_age: Optional[int] = Query(None, ge=18, le=99),
    gender: Optional[str] = Query(None, regex="^(male|female)$"),
    location: Optional[str] = Query(None),
):
    """
    [Premium] Лента с расширенными фильтрами:
    возраст, пол, город.
    """
    try:
        all_users = get_filtered_users(current_user) or []
    except Exception:
        all_users = []

    # Применяем фильтры
    filtered = all_users
    if min_age is not None:
        filtered = [u for u in filtered if u.get("age") and u["age"] >= min_age]
    if max_age is not None:
        filtered = [u for u in filtered if u.get("age") and u["age"] <= max_age]
    if gender:
        filtered = [u for u in filtered if u.get("gender") == gender]
    if location:
        filtered = [
            u for u in filtered
            if u.get("location") and location.lower() in u["location"].lower()
        ]

    return {
        "users": filtered,
        "total": len(filtered),
        "filters_applied": {
            "min_age": min_age,
            "max_age": max_age,
            "gender": gender,
            "location": location,
        },
    }