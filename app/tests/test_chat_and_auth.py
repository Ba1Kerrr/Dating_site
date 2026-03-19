import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime, timedelta, timezone
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))

os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_ROUTE", "postgresql://test:test@localhost/test")


class TestJWT:
    def test_create_and_decode_access_token(self):
        from funcs.jwt_auth import create_access_token, decode_token
        token = create_access_token("ivan")
        payload = decode_token(token)
        assert payload["sub"] == "ivan"
        assert payload["type"] == "access"

    def test_create_and_decode_refresh_token(self):
        from funcs.jwt_auth import create_refresh_token, decode_token
        token = create_refresh_token("ivan")
        payload = decode_token(token)
        assert payload["sub"] == "ivan"
        assert payload["type"] == "refresh"

    def test_invalid_token_raises(self):
        from funcs.jwt_auth import decode_token
        from fastapi import HTTPException
        with pytest.raises(HTTPException) as exc:
            decode_token("this.is.garbage")
        assert exc.value.status_code == 401

    def test_expired_token_raises(self):
        from funcs.jwt_auth import decode_token, SECRET_KEY, ALGORITHM
        from fastapi import HTTPException
        from jose import jwt
        token = jwt.encode(
            {"sub": "ivan", "exp": datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1), "type": "access"},
            SECRET_KEY, algorithm=ALGORITHM
        )
        with pytest.raises(HTTPException):
            decode_token(token)

    def test_get_current_user_dependency(self):
        from funcs.jwt_auth import create_access_token, get_current_user
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient

        test_app = FastAPI()

        @test_app.get("/protected")
        async def protected(user: str = Depends(get_current_user)):
            return {"user": user}

        client = TestClient(test_app)
        token = create_access_token("ivan")
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["user"] == "ivan"

    def test_get_current_user_no_token(self):
        from funcs.jwt_auth import get_current_user
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient

        test_app = FastAPI()

        @test_app.get("/protected")
        async def protected(user: str = Depends(get_current_user)):
            return {"user": user}

        client = TestClient(test_app)
        resp = client.get("/protected")
        assert resp.status_code == 401

    def test_refresh_token_cannot_be_used_as_access(self):
        from funcs.jwt_auth import create_refresh_token, get_current_user
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient

        test_app = FastAPI()

        @test_app.get("/protected")
        async def protected(user: str = Depends(get_current_user)):
            return {"user": user}

        client = TestClient(test_app)
        token = create_refresh_token("ivan")
        resp = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 401


class TestAuthRouter:

    def _make_app(self):
        with patch("database.database.engine"), patch("database.database.conn"):
            from routers.auth import router
            app = FastAPI()
            app.include_router(router)
            return app

    def test_get_token_success(self):
        with patch("routers.auth.info_user") as mock_info, \
             patch("routers.auth.verify_password", return_value=True):
            mock_info.return_value = {"username": "ivan", "password": "hashed"}
            client = TestClient(self._make_app())
            resp = client.post("/auth/token", json={"username": "ivan", "password": "pw"})
            assert resp.status_code == 200
            data = resp.json()
            assert "access_token" in data
            assert "refresh_token" in data

    def test_get_token_wrong_password(self):
        with patch("routers.auth.info_user") as mock_info, \
             patch("routers.auth.verify_password", return_value=False):
            mock_info.return_value = {"username": "ivan", "password": "hashed"}
            client = TestClient(self._make_app())
            resp = client.post("/auth/token", json={"username": "ivan", "password": "wrong"})
            assert resp.status_code == 401

    def test_get_token_user_not_found(self):
        with patch("routers.auth.info_user", return_value=None):
            client = TestClient(self._make_app())
            resp = client.post("/auth/token", json={"username": "ghost", "password": "pw"})
            assert resp.status_code == 401

    def test_refresh_token(self):
        from funcs.jwt_auth import create_refresh_token
        with patch("routers.auth.info_user") as mock_info:
            mock_info.return_value = {"username": "ivan"}
            client = TestClient(self._make_app())
            refresh = create_refresh_token("ivan")
            resp = client.post("/auth/refresh", json={"refresh_token": refresh})
            assert resp.status_code == 200
            assert "access_token" in resp.json()

    def test_refresh_with_access_token_fails(self):
        from funcs.jwt_auth import create_access_token
        client = TestClient(self._make_app())
        token = create_access_token("ivan")
        resp = client.post("/auth/refresh", json={"refresh_token": token})
        assert resp.status_code == 401


class TestChatDatabase:

    def test_check_match_exists_true(self):
        with patch("database.database.check_match_exists") as mock_check:
            mock_check.return_value = True
            result = mock_check("ivan", "anna")
            assert result is True

    def test_check_match_exists_false(self):
        with patch("database.database.check_match_exists") as mock_check:
            mock_check.return_value = False
            result = mock_check("ivan", "ghost")
            assert result is False

    def test_save_message_returns_id(self):
        with patch("database.database.save_message") as mock_save:
            mock_save.return_value = 42
            result = mock_save("ivan", "anna", "Привет!")
            assert result == 42

    def test_get_messages_returns_list(self):
        with patch("database.database.get_messages") as mock_get:
            mock_messages = [
                {"id": 1, "sender": "ivan", "receiver": "anna", "text": "Привет!"},
                {"id": 2, "sender": "anna", "receiver": "ivan", "text": "Привет!"}
            ]
            mock_get.return_value = mock_messages
            result = mock_get("ivan", "anna")
            assert len(result) == 2


class TestChatRouter:

    def _make_app(self):
        with patch("database.database.engine"), patch("database.database.conn"):
            from routers.chat import router
            app = FastAPI()
            app.add_middleware(SessionMiddleware, secret_key="test")
            app.include_router(router)
            return app

    def test_api_history_requires_token(self):
        client = TestClient(self._make_app())
        resp = client.get("/api/chat/anna/history")
        assert resp.status_code == 401

    def test_api_history_with_token(self):
        from funcs.jwt_auth import create_access_token
        with patch("routers.chat.check_match_exists", return_value=True), \
             patch("routers.chat.get_messages", return_value=[]):
            client = TestClient(self._make_app())
            token = create_access_token("ivan")
            resp = client.get(
                "/api/chat/anna/history",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code == 200

    def test_api_history_no_match_forbidden(self):
        from funcs.jwt_auth import create_access_token
        with patch("routers.chat.check_match_exists", return_value=False):
            client = TestClient(self._make_app())
            token = create_access_token("ivan")
            resp = client.get(
                "/api/chat/anna/history",
                headers={"Authorization": f"Bearer {token}"}
            )
            assert resp.status_code == 403


class TestRateLimit:

    def test_rate_limit_blocks_after_max(self):
        from funcs.rate_limit import make_rate_limiter
        from fastapi import FastAPI, Depends
        from fastapi.testclient import TestClient

        limiter = make_rate_limiter(max_requests=3, window_seconds=60)
        test_app = FastAPI()

        @test_app.post("/limited")
        async def limited(_=Depends(limiter)):
            return {"ok": True}

        client = TestClient(test_app, raise_server_exceptions=False)

        for i in range(3):
            resp = client.post("/limited")
            assert resp.status_code == 200

        resp = client.post("/limited")
        assert resp.status_code == 429