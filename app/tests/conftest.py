import sys
import os
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
import types
import importlib
import inspect

sys.path.insert(0, "/app")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

from funcs.rate_limit import _request_log, _lock


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    import asyncio
    async def _reset():
        async with _lock:
            _request_log.clear()
    asyncio.run(_reset())
    yield


def get_database_functions():
    functions = []
    try:
        if "database.database" in sys.modules:
            del sys.modules["database.database"]
        db_module = importlib.import_module("database.database")
        for name, obj in inspect.getmembers(db_module):
            if inspect.isfunction(obj) and not name.startswith('_'):
                functions.append(name)
    except Exception as e:
        print(f"Warning: Could not import database module: {e}")
        functions = [
            "create_messages_table", "info_user", "info_user_email",
            "check_username", "check_email", "insert_db", "insert_values_dopinfo",
            "update_password", "update_password_email", "detect_username_from_email",
            "find_all_users", "check_match_exists", "save_message", "get_messages",
            "get_user_chats", "profile", "get_user_role", "set_user_role",
            "make_first_user_admin", "ensure_admin_exists", "is_admin"
        ]
    return functions


REAL_FUNCTIONS = {
    'check_match_exists', 'save_message', 'get_messages', 'get_user_chats',
    'info_user', 'profile', 'get_user_role', 'is_admin'
}

_db_mock = MagicMock()
_db_module = types.ModuleType("database.database")
_db_module.engine = MagicMock()
_db_module.conn = _db_mock
_db_module.metadata = MagicMock()

all_functions = get_database_functions()

for fn_name in all_functions:
    if fn_name in REAL_FUNCTIONS:
        try:
            real_module = importlib.import_module("database.database")
            if hasattr(real_module, fn_name):
                setattr(_db_module, fn_name, getattr(real_module, fn_name))
            else:
                setattr(_db_module, fn_name, MagicMock())
        except:
            setattr(_db_module, fn_name, MagicMock())
    else:
        setattr(_db_module, fn_name, MagicMock())

sys.modules["database"] = types.ModuleType("database")
sys.modules["database.database"] = _db_module

from main import app


@pytest.fixture
def db():
    _db_mock.reset_mock()
    return _db_module


@pytest_asyncio.fixture
async def client():
    from httpx import AsyncClient, ASGITransport
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=False,
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_client(client):
    with patch("routers.login.info_user", return_value={
        "username": "testuser",
        "password": "hashed",
        "email": "test@example.com",
        "avatar": "avatar.jpg",
        "location": "Moscow",
        "gender": "male",
    }), patch("routers.login.verify_password", return_value=True):
        resp = await client.post("/api/login", data={
            "username": "testuser",
            "password": "password123",
        })
        client.cookies = resp.cookies
    yield client


@pytest.fixture
def clean_rate_limit():
    from funcs.rate_limit import _request_log, _lock
    import asyncio
    async def _clean():
        async with _lock:
            _request_log.clear()
    asyncio.run(_clean())
    yield


@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ.setdefault("TESTING", "true")
    yield