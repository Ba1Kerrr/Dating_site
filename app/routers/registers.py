import os
import re
from typing import Annotated

from fastapi import APIRouter, HTTPException, Request, Form, File, UploadFile, Depends
from fastapi.responses import JSONResponse

from database.database import insert_db, insert_values_dopinfo, info_user, check_email, check_username
from funcs.hash import hash_password
from funcs.verification import send_email
from funcs.rate_limit import register_rate_limit
from .schemas import UserAddSchemas, EmailSchema

router = APIRouter(prefix="/api/register", tags=["register"])

static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "personal_info"
)
os.makedirs(static_dir, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("")
async def register(
    request: Request,
    user: Annotated[UserAddSchemas, Form()],
    _=Depends(register_rate_limit),
):
    if user.username.startswith("/") or user.username.endswith("/"):
        raise HTTPException(status_code=400, detail="Username cannot start or end with a slash")
    if not re.match(r"^[a-zA-Z0-9_]+$", user.username):
        raise HTTPException(status_code=400, detail="Username must contain only letters, numbers, and underscores")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if check_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if check_email(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    session_key = str(request.session.get("key", ""))
    if str(user.input_key) != session_key:
        raise HTTPException(status_code=400, detail="Confirmation code is incorrect")

    insert_db(user.username, user.email, hash_password(user.password))
    request.session["user"] = user.username
    return {"status": "ok", "username": user.username}


@router.post("/dop-info")
async def dop_info_submit(
    request: Request,
    age:      int        = Form(...),
    gender:   str        = Form(...),
    name:     str        = Form(...),
    location: str        = Form(...),
    bio:      str        = Form(...),
    file: UploadFile     = File(...),
    _=Depends(register_rate_limit),
):
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Invalid file type. Allowed: {ALLOWED_EXTENSIONS}")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")

    unique_filename = f"{username}{ext}"
    filepath = os.path.join(static_dir, unique_filename)

    try:
        with open(filepath, "wb") as f:
            f.write(contents)
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"File save error: {e}")

    avatar_path = f"personal_info/{unique_filename}"
    insert_values_dopinfo(username, age, gender, name, location, avatar_path, bio)
    return {"status": "ok"}


@router.post("/send-email")
async def send_email_endpoint(
    request: Request,
    data: EmailSchema,
    _=Depends(register_rate_limit),
):
    key = send_email(data.email)
    request.session["key"] = str(key)
    return {"status": "sent"}