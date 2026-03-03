from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from database.database import create_messages_table
from routers.login     import router as login_router
from routers.logout    import router as logout_router
from routers.registers import router as register_router
from routers.forgot    import router as forgot_router
from routers.chat      import router as chat_router
from routers.auth      import router as auth_router
from routers.profile import router as profile_router
import os

app = FastAPI(title="Dating Site API", version="1.0")

# ─── Middleware ───────────────────────────────────────────────────────────────

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "changeme"),
    max_age=60 * 60 * 24 * 7,  # 7 дней
    https_only=False,           # поставь True на проде
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static files ─────────────────────────────────────────────────────────────

app.mount("/static", StaticFiles(directory="templates/static"), name="static")

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(register_router)
app.include_router(forgot_router)
app.include_router(chat_router)
app.include_router(profile_router)

# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    create_messages_table()


@app.get("/")
async def root():
    return {"status": "ok"}