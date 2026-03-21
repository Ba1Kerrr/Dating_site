from fastapi import APIRouter, HTTPException, Request, Form
from database.database import update_password, update_password_email
from database.database import info_user, info_user_email
from funcs.hash import hash_password
from celery_app import send_password_reset_email

# Alias so tests can patch `routers.forgot.detect_username_from_email`
detect_username_from_email = info_user_email

router = APIRouter(prefix='/api/forgot', tags=["forgot"])


@router.post("/password")
async def forgot_password(
    request: Request,
    username: str = Form(...),
    new_password: str = Form(...),
):
    user = info_user(username)
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    hashed = hash_password(new_password)
    success = update_password(username, hashed)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")

    # Уведомление об изменении пароля — в фоне через Celery
    email = user.get("email")
    if email:
        send_password_reset_email.delay(email, username)

    return {"status": "ok"}


@router.post("/username")
async def forgot_username(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
):
    user = detect_username_from_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="Email not found")

    hashed = hash_password(new_password)
    success = update_password_email(email, hashed)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")

    # Уведомление — в фоне
    send_password_reset_email.delay(email, user.get("username", ""))

    return {"status": "ok"}