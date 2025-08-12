from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database.database import insert_db,insert_values_dopinfo
from app.database.database import info_user,check_email,check_username
from app.funcs.hash import hash_password
from app.funcs.verification import send_email
import os
import re
from .schemas import UserAddSchemas
router = APIRouter(prefix='/register', tags=["register"])

templates = Jinja2Templates(directory="app/templates")


static_dir = os.path.join( os.path.dirname(os.path.dirname(__file__)), "templates", "static")
print(static_dir)
@router.get("", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("")
async def register(request: Request, user: Annotated[UserAddSchemas, Form()]):
    key = request.session.get("key")
    if user.username[0] == "/" or user.username[-1] == "/":
        raise HTTPException(status_code=400, detail="Username cannot sstart or end with a slash")
    if not re.match("^[a-zA-Z0-9_]+$", user.username):
        raise HTTPException(status_code=400, detail="Username must contain only letters, numbers, and underscores")
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    elif check_username(user.username) == True:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif check_email(user.email) == True:
        raise HTTPException(status_code=400, detail="Email already registered")
    if user.input_key != key:
        raise HTTPException(status_code=400, detail="Code is incorrect")
    insert_db(user.username, user.email ,hash_password(user.password))
    request.session['user'] = user.username
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
    try:
        # contents = file.file.read()
        with open(os.path.join(static_dir, unique_filename), "wb") as f:
            f.write(await file.read())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error- {e}")
    finally:
        file.file.close()
    username = request.session.get('user')
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    insert_values_dopinfo(username,age,gender,name,location,f"{username}-{file.filename}",bio)
    return RedirectResponse(url="/", status_code=303)

@router.post('/send_email')
async def send_email_endpoint(request: Request, form_data: dict):
    email = form_data.get("email")
    key = send_email(email)
    request.session['key'] = key
    print(request.session)
    return {"key": key}

