from fastapi import FastAPI, Form, Depends, HTTPException,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from database import insert_db, check_email, check_username,info_user,insert_values_dopinfo

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

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

@app.get("/")
async def read_root(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse("index.html", {"request": request, "user": user})
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    if check_username(username) == True:
        raise HTTPException(status_code=400, detail="Username already registered")
    elif check_email(email) == True:
        raise HTTPException(status_code=400, detail="Email already registered")

    insert_db(username, email,hash_password(password))
    return RedirectResponse(url="/login", status_code=303)

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

@app.get("/users/{username}",response_class =HTMLResponse)
async def read_user(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse("user.html", {"request": request, "user": user})

@app.post("/users/{username}")
async def add_read_user(username,age:int = Form(),gender:str = Form(),name:str = Form(),location:str = Form()):
    insert_values_dopinfo(username,age,gender,name,location)
    #https://ru.stackoverflow.com/questions/801521/%D0%9A%D0%B0%D0%BA-%D0%B4%D0%B0%D1%82%D1%8C-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8E-%D0%B2%D1%81%D1%82%D0%B0%D0%B2%D0%BB%D1%8F%D1%82%D1%8C-%D0%BA%D0%B0%D1%80%D1%82%D0%B8%D0%BD%D0%BA%D1%83-%D0%BD%D0%B0-%D1%81%D0%B0%D0%B9%D1%82%D0%B5
    #это инструкция по добавлению аватарки в базу данных
    return RedirectResponse(url="/", status_code=303)
#next steps will be to add avatar 

#else u need to improve registration params/check
    #add else check :
    # Username may only contain alphanumeric characters or single hyphens,
    #  and cannot begin or end with a hyphen
#and finally 2 steps is :
# to add profile pages on main menu with filtres
# to add update data if you want to recovery your account(update email,password)