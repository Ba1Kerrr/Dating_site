# routers/profile.py
from fastapi import APIRouter, Request, HTTPException, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database.database import profile as get_profile, insert_values_dopinfo
import os

router = APIRouter(prefix="/profile", tags=["profile"])
templates = Jinja2Templates(directory="templates")

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates", "static")


@router.get("/{username}", response_class=HTMLResponse)
async def view_profile(request: Request, username: str):
    current_user = request.session.get("user")
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)

    user_profile = get_profile(username)
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")

    return templates.TemplateResponse("profile.html", {
        "request":  request,
        "profile":  user_profile,
        "is_own":   current_user == username,
    })


@router.post("/{username}/edit")
async def edit_profile(
    request: Request,
    username: str,
    name:     str = Form(default=""),
    bio:      str = Form(default=""),
    location: str = Form(default=""),
    age:      int = Form(default=0),
    file: UploadFile = File(default=None),
):
    current_user = request.session.get("user")
    if not current_user or current_user != username:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Текущий профиль чтобы не затереть аватар если не загрузили новый
    current = get_profile(username)
    avatar = current.get("avatar") if current else None

    if file and file.filename:
        import uuid
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp", ".gif"):
            raise HTTPException(status_code=400, detail="Invalid file type")
        avatar = f"{username}-{uuid.uuid4().hex}{ext}"
        with open(os.path.join(static_dir, avatar), "wb") as f:
            f.write(await file.read())

    insert_values_dopinfo(
        username=username,
        age=age or (current.get("age") if current else 0),
        gender=current.get("gender", "") if current else "",
        name=name or (current.get("name", "") if current else ""),
        location=location or (current.get("location", "") if current else ""),
        avatar=avatar or "",
        bio=bio or (current.get("bio", "") if current else ""),
    )

    return RedirectResponse(url=f"/profile/{username}", status_code=303)