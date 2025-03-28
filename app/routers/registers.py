from fastapi import APIRouter, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from database import insert_db,insert_values_dopinfo
from database import info_user,check_email,check_username
from hash import hash_password
from verification import send_email
import os
import re
from .schemas import UserAddSchemas
router = APIRouter(prefix='/register', tags=["register"])

templates = Jinja2Templates(directory="templates")
key = ''
@router.get("", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
@router.post("/register")
async def register(request: Request, user: UserAddSchemas):
    input_key = request.session.get("input_key")
    if user.username[0] == "/" or user.username[-1] == "/":
        raise HTTPException(status_code=400, detail="Username cannot start or end with a slash")
    if not re.match("^[a-zA-Z0-9_]+$", user.username):
        raise HTTPException(status_code=400, detail="Username must contain only letters, numbers, and underscores")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    elif check_username(user.name) == True:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif check_email(user.email) == True:
        raise HTTPException(status_code=400, detail="Email already registered")
    if input_key != key:
        raise HTTPException(status_code=400, detail="Code is incorrect")
    insert_db(user.name, user.email ,hash_password(user.password))
    request.session['user'] = user.name
    return RedirectResponse(url="/register/dop-info", status_code=303)
#-----------------------------------------------------------------------------------------------------------------------------
#                                           add some dop-info on your profile(username,age,gender,name,location)

@router.get("/dop-info",response_class =HTMLResponse)
async def read_user(request: Request):
    user = request.session.get('user')
    avatar = info_user(user)['avatar']
    return templates.TemplateResponse("dop_info.html", {"request": request, "user": user,"avatar":avatar})


@router.post("/dop-info")
async def add_read_user(request:Request, age: int = Form(), gender: str = Form(), name: str = Form(), location: str = Form(),file:UploadFile = File(...),bio:str = Form(...)):
    username = request.session.get('user')
    unique_filename = f"{username}-{file.filename}"
    static_dir = os.path.join(os.path.dirname(__file__), "templates","static")
    try:
        # contents = file.file.read()
        with open(os.path.join(static_dir, unique_filename), "wb") as f:
            f.write(await file.read())
        
    except Exception:
        raise HTTPException(status_code=500, detail='Something went wrong')
    finally:
        file.file.close()
    insert_values_dopinfo(username,age,gender,name,location,f"{username}-{file.filename}",bio)
    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)

@router.post('/send_email')
async def send_email_endpoint(request: Request, form_data: dict):
    email = form_data.get("email")
    global key
    key = send_email(email)
    return {"key": key}
