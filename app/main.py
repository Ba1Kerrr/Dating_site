from fastapi import FastAPI, Form, Depends, HTTPException,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import File, UploadFile
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
import re
from database import insert_db,update_password,insert_values_dopinfo,update_password_email
from database import info_user,check_email,check_username,info_user_email,detect_username_from_email
from hash import hash_password,verify_password
import os

#-----------------------------------------------------------------------------------------------------------------------------
#                                        set up fastapi

app = FastAPI()
#add my static files(css,other)
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "templates"), name="static")

# Middleware for session management
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Template configuration
templates = Jinja2Templates(directory="templates")

#-----------------------------------------------------------------------------------------------------------------------------
#                                           base page

@app.get("/")
async def read_root(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
#to add profile pages on main menu with filtres to find you second part
#add your avatar to the right corner

#-----------------------------------------------------------------------------------------------------------------------------
#                                            register

@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if username[0] == "/" or username[-1] == "/":
        raise HTTPException(status_code=400, detail="Username cannot start or end with a slash")
    if not re.match("^[a-zA-Z0-9_]+$", username):
        raise HTTPException(status_code=400, detail="Username must contain only letters, numbers, and underscores")
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    elif check_username(username) == True:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif check_email(email) == True:
        raise HTTPException(status_code=400, detail="Email already registered")

    insert_db(username, email,hash_password(password))
    return RedirectResponse(url="/login", status_code=303)

#-----------------------------------------------------------------------------------------------------------------------------
#                                               login

@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request,username: str = Form(...), password: str = Form(...)):
    user = info_user(username) # - {'username': 'smth', 'email': '12345@text.com', 'password': 'hashedpassw'}
    if user is None or not verify_password(password, user['password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)

#-----------------------------------------------------------------------------------------------------------------------------
#                                            if u forgot password

@app.post("/forgot_password")
async def update_password(request: Request, username: str = Form(...), new_password: str = Form(...)):
    user = info_user(username)
    hashed_new_password = hash_password(new_password)
    success = update_password(username, hashed_new_password)
    if not success:
        raise HTTPException(status_code=400)
    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)

@app.get('/forgot_password',response_class=HTMLResponse)
async def forgot_password_get(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})
#-----------------------------------------------------------------------------------------------------------------------------
#                                            if u forgot username

@app.get("/forgot_username",response_class = HTMLResponse)
async def forgot_usrname_get(request: Request):
    return templates.TemplateResponse("Forgot_username.html", {"request": request})

@app.post("/forgot_username")
async def forgot_usrname(request: Request, email: str = Form(...), new_password: str = Form(...)):
    user = info_user_email(email)
    hashed_new_password = hash_password(new_password)
    success = update_password_email(info_user_email, hashed_new_password)
    if not success:
        raise HTTPException(status_code=400)
    request.session['user'] = detect_username_from_email(email)
    return RedirectResponse(url="/", status_code=303)
#https://ru.stackoverflow.com/questions/865445/%D0%9F%D0%BE%D0%B4%D1%82%D0%B2%D0%B5%D1%80%D0%B6%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5-email-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%87%D0%B5%D1%80%D0%B5%D0%B7-api
#2Fac auth - send verification code
#-----------------------------------------------------------------------------------------------------------------------------
#                                           add some dop-info on your profile(username,age,gender,name,location)

@app.get("/users/{username}",response_class =HTMLResponse)
async def read_user(request: Request):
    user = request.session.get('user')
    avatar = info_user(user)['avatar']
    return templates.TemplateResponse("user.html", {"request": request, "user": user,"avatar":avatar})


@app.post("/users/{username}")
async def add_read_user(request:Request,username: str, age: int = Form(), gender: str = Form(), name: str = Form(), location: str = Form(),file:UploadFile = File(...)):
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
    # insert_values_dopinfo(username,age,gender,name,location,f"{username}-{file.filename}")
    return templates.TemplateResponse("user.html", {"request": request, "user": username})
 

#-----------------------------------------------------------------------------------------------------------------------------
#                                                       logout
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
#-----------------------------------------------------------------------------------------------------------------------------
#                               Handling JavaScript Functions to Prevent Errors
@app.post("/upload")
async def upload():
    return 0
#-----------------------------------------------------------------------------------------------------------------------------
#                                                       dop-info about futures

#and finally steps are :
# to add profile pages on main menu with filtres to find you second part
#incude in my project redis,nginx
# in next steps is create and use server



#git commit -m "added docker settings,restore if you forgot password,image preview and add avatar to DB"