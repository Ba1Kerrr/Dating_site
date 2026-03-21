from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from funcs.rate_limit import get_rate_limit_stats, cleanup_old_stats
from database.database import (
    create_messages_table, ensure_admin_exists,
    get_filtered_users_safe,                       # ← вместо get_filtered_users
)
from routers.login import router as login_router
from routers.logout import router as logout_router
from routers.registers import router as register_router
from routers.forgot import router as forgot_router
from routers.chat import router as chat_router
from routers.auth import router as auth_router
from routers.profile import router as profile_router
from routers.subscription import router as subscription_router
from routers.blocks import router as blocks_router
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


app = FastAPI(title="Dating Site API", version="1.0", lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "changeme"),
    max_age=60 * 60 * 24 * 7,
    https_only=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:80",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:5175",
        "http://localhost:3000",
        "http://127.0.0.1",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(login_router)
app.include_router(logout_router)
app.include_router(register_router)
app.include_router(forgot_router)
app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(subscription_router)
app.include_router(blocks_router)


@app.get("/api/feed")
async def feed(request: Request):
    """Лента — исключает заблокированных в обе стороны."""
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"users": get_filtered_users_safe(username)}


@app.get("/api/admin/rate-limit-stats")
async def admin_rate_limit_stats(request: Request):
    if request.session.get("user") not in ADMINS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await get_rate_limit_stats(request)