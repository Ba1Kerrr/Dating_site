from fastapi import FastAPI, Form, Depends, HTTPException,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from database import insert_db, check_email, check_username,info_user
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

# In-memory user storage (for demonstration purposes)
users_db = {}

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

    users_db[username] = {
        "username": username,
        "email": email,
        "password": hash_password(password),
    }
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