from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Text, Boolean
from sqlalchemy.exc import SQLAlchemyError
from database import insert_values,conn
# Define constants
DATABASE_URL = "postgresql+psycopg2://Dating-site:root@localhost:5432/sqlalchemy_tuts"
SECRET_KEY = "your_secret_key"

# Initialize FastAPI app
app = FastAPI()

# Add middleware for session management and CORS
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure template engine
templates = Jinja2Templates(directory="templates")

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# In-memory user storage (for demonstration purposes)
users_db = {}

# Password utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

# Function to insert a new user into the database

# Mount static files
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "templates"), name="static")

# Root endpoint
@app.get("/")
async def read_root(request: Request):
    user = request.session.get('user')
    return templates.TemplateResponse("index.html", {"request": request, "user": user})

# Logout endpoint
@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)

# Registration form endpoint
@app.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Registration endpoint
@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    age: int = Form(...),
    gender: bool = Form(...),
    name: str = Form(...),
):
    if username in users_db:
        raise HTTPException(status_code=400, detail="Username already registered")
    if email in [user["email"] for user in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email already registered")
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Hash the password
    hashed_password = get_password_hash(password)

    # Store user in in-memory database (for demonstration)
    users_db[username] = {
        "email": email,
        "username": username,
        "password": hashed_password,
    }

    # Insert user into the database
    user_data = {
        "username": username,
        "age": age,
        "gender": gender,
        "name": name,
        "password": hashed_password
    }
    insert_values(user_data)

    return RedirectResponse(url="/login", status_code=202)

# Login form endpoint
@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request,username: str = Form(...), password: str = Form(...)):
    user = users_db.get(username)
    if user is None or not verify_password(password, user['password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    request.session['user'] = username
    return RedirectResponse(url="/", status_code=303)


@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


@app.get("/username")
async def user_profile(request: Request):
    return templates.TemplateResponse("user_profile.html", {"request": request})