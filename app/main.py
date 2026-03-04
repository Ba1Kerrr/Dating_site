from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from funcs.rate_limit import get_rate_limit_stats, cleanup_old_stats
from database.database import create_messages_table, ensure_admin_exists, get_filtered_users, info_user
from routers.login import router as login_router
from routers.logout import router as logout_router
from routers.registers import router as register_router
from routers.forgot import router as forgot_router
from routers.chat import router as chat_router
from routers.auth import router as auth_router
from routers.profile import router as profile_router
import os
import asyncio
from contextlib import asynccontextmanager

ADMINS = {"Ba1kerr"}

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(cleanup_old_stats())
    create_messages_table()
    ensure_admin_exists()
    yield


app = FastAPI(
    title="Dating Site API",
    version="1.0",
    lifespan=lifespan
)


app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "changeme"),
    max_age=60 * 60 * 24 * 7,
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "templates", "static")),
    name="static",
)

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "templates/static")),
    name="static"
)

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(register_router)
app.include_router(forgot_router)
app.include_router(chat_router)
app.include_router(profile_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Главная страница.
    - Если пользователь залогинен — показываем ленту анкет (ML-фильтрация).
    - Если нет — показываем промо-экран.
    """
    username = request.session.get("user")
    data = []

    if username:
        try:
            # get_filtered_users возвращает список анкет подходящих юзеру
            data = get_filtered_users(username) or []
        except Exception:
            data = []

    return templates.TemplateResponse("index.html", {
        "request": request,
        "user":    username,
        "data":    data,
    })


@app.get("/admin/rate-limit-stats")
async def admin_rate_limit_stats(request: Request):
    admin_user = request.session.get("user")
    if admin_user not in ADMINS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await get_rate_limit_stats(request)

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    username = request.session.get("user")
    return templates.TemplateResponse("about.html", {
        "request":  request,
        "username": username,
    })