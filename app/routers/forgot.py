from fastapi import APIRouter, HTTPException, Request, Form
from database.database import update_password, update_password_email
from database.database import info_user, info_user_email, detect_username_from_email
from funcs.hash import hash_password

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
    return {"status": "ok"}


@router.post("/username")
async def forgot_username(
    request: Request,
    email: str = Form(...),
    new_password: str = Form(...),
):
    user = info_user_email(email)
    if not user:
        raise HTTPException(status_code=400, detail="Email not found")
    hashed = hash_password(new_password)
    success = update_password_email(email, hashed)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update password")
    return {"status": "ok"}