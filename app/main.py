import json
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
from verification import send_email
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
async def register(request: Request,username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...),input_key: str = Form(...)):
    form_data = await request.form()
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")
    confirm_password = form_data.get("confirm_password")
    input_key = form_data.get("input_key")
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
    if input_key != key:
        raise HTTPException(status_code=400, detail="Code is incorrect")
    insert_db(username, email,hash_password(password))
    return RedirectResponse(url="/users/{username}", status_code=303)

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
    #здесь будет штука,получающая email из переменной user(это делается - user['email']) и отправляющая письмо
    #затем мы отправлям с функцию js в самом фронтенде,когда пользователь отправил свой username(для этого создать отдельный button) и обрабатываем ее на бэке
    #после этого ждем отправки от пользователя с формы ключ для восстановления
    #затем в случаи успеха(желательно это также сделать в js(передать js инпут от пользователя)),затем даем челу ввести новый пароль
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
    #даем ему ввести email,высылаем код,проверяем его,потом даем ему ввести новый пароль
    hashed_new_password = hash_password(new_password)
    success = update_password_email(info_user_email, hashed_new_password)
    if not success:
        raise HTTPException(status_code=400)
    request.session['user'] = detect_username_from_email(email)
    return RedirectResponse(url="/", status_code=303)

#-----------------------------------------------------------------------------------------------------------------------------
#                                           add some dop-info on your profile(username,age,gender,name,location)

@app.get("/users/{username}",response_class =HTMLResponse)
async def read_user(request: Request):
    user = request.session.get('user')
    avatar = info_user(user)['avatar']
    return templates.TemplateResponse("dop_info.html", {"request": request, "user": user,"avatar":avatar})


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
    return templates.TemplateResponse("dop_info.html", {"request": request, "user": username})
    #сдесь нужно сделать так чтоб чел видел обычную страницу(нужно в html поменять display,увести все в левый угол,затем будем делать сами фотки этого человека как в той же инсте или вк )
                                        #!!!!полностью поменять оформление профиля!!!!!!

#-----------------------------------------------------------------------------------------------------------------------------
#                                                       logout
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
#-----------------------------------------------------------------------------------------------------------------------------
#                               Handling JavaScript Functions
@app.post("/upload")
async def upload():
    return 1
@app.post('/send_email')
async def send_email_endpoint(request: Request, form_data: dict):
    email = form_data.get("email")
    global key
    key = send_email(email)
    return {"key": key}
#-----------------------------------------------------------------------------------------------------------------------------
#                                                       dop-info about futures

#and finally steps are :
# to add profile pages on main menu with filtres to find you second part
#incude in my project redis,nginx
# in next steps is create and use server
#add redis,kafka

# ну верификацию сделал,но она работает очень коряво,
# нужно также сделать проверку js на то чтоб все данные были корректные(подключить модели)
# также почитать все в файле fastapi-help