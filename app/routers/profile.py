import uuid
import os
from typing import Optional

from fastapi.responses import JSONResponse
from funcs.jwt_auth import get_current_user_flexible as get_current_user
from funcs.subscription import record_profile_view, get_user_plan
from fastapi import APIRouter, Request, HTTPException, Form, File, UploadFile, Depends
from database.database import profile as get_profile, insert_values_dopinfo

router = APIRouter()
static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "personal_info"
)
os.makedirs(static_dir, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.get("/api/profile/{username}")
async def view_profile(
    username: str,
    request: Request,
    current_user: str = Depends(get_current_user),
):
    """Просмотр профиля. Записывает просмотр для Premium-аналитики."""
    user_info = get_profile(username)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    is_owner = current_user == username

    # Записываем просмотр (не себя) — нужно для Premium "кто смотрел"
    if not is_owner:
        record_profile_view(viewer_username=current_user, target_username=username)

    profile_data = {
        "username":  user_info.get("username"),
        "name":      user_info.get("name"),
        "age":       user_info.get("age"),
        "gender":    user_info.get("gender"),
        "location":  user_info.get("location"),
        "bio":       user_info.get("bio"),
        "avatar":    user_info.get("avatar"),
        "is_own":    is_owner,
        # Показываем email только владельцу
        **({"email": user_info.get("email")} if is_owner else {}),
    }

    return JSONResponse(content=profile_data)


@router.post("/api/profile/{username}/edit")
async def edit_profile(
    username: str,
    request: Request,
    name: Optional[str] = Form(""),
    bio: Optional[str] = Form(""),
    location: Optional[str] = Form(""),
    age: Optional[int] = Form(0),
    file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user),
):
    if current_user != username:
        raise HTTPException(status_code=403, detail="Can't edit other user's profile")

    current = get_profile(username) or {}
    avatar  = current.get("avatar", "")

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type")
        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
        filename = f"{username}-{uuid.uuid4().hex}{ext}"
        with open(os.path.join(static_dir, filename), "wb") as f:
            f.write(contents)
        avatar = f"personal_info/{filename}"

    insert_values_dopinfo(
        username = username,
        age      = age      or current.get("age", 0),
        gender   = current.get("gender", ""),
        name     = name     or current.get("name", ""),
        location = location or current.get("location", ""),
        avatar   = avatar,
        bio      = bio      or current.get("bio", ""),
    )
    return {"status": "ok"}