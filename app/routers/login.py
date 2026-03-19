from fastapi import APIRouter, HTTPException, Request, Form, Depends
from database.database import info_user
from funcs.hash import verify_password
from funcs.rate_limit import login_rate_limit

router = APIRouter(prefix="/api/login", tags=["login"])

@router.post("")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    _=Depends(login_rate_limit),
):
    user = info_user(username)
    if user is None or not verify_password(password, user.get("password_hash", "")):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    request.session["user"] = username
    return {"status": "ok", "username": username}