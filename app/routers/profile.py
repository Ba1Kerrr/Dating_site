import os
import uuid

from fastapi import APIRouter, Request, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database.database import profile as get_profile, insert_values_dopinfo

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

static_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "static", "personal_info"
)
os.makedirs(static_dir, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


# ─── GET /profile/{username} ──────────────────────────────────────────────────

@router.get("/{username}", response_class=HTMLResponse)
async def view_profile(request: Request, username: str):
    current_user = request.session.get("user")
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_profile = get_profile(username)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": user_profile,
        "is_own":  current_user == username,
    })


# ─── POST /profile/{username}/edit ────────────────────────────────────────────

@router.post("/{username}/edit")
async def edit_profile(
    request:  Request,
    username: str,
    name:     str        = Form(default=""),
    bio:      str        = Form(default=""),
    location: str        = Form(default=""),
    age:      int        = Form(default=0),
    file: UploadFile     = File(default=None),
):
    current_user = request.session.get("user")
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    if current_user != username:
        raise HTTPException(status_code=403, detail="Forbidden")

    current = get_profile(username) or {}
    avatar  = current.get("avatar", "")

    # Загрузка нового аватара если передан
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="Invalid file type")

        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
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

    return RedirectResponse(url=f"/profile/{username}", status_code=303)
