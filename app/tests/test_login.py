import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


class TestLogin:
    async def test_login_success(self, client):
        with patch("routers.login.info_user", return_value={
            "username": "testuser", "password_hash": "hashed",
            "email": "t@t.com", "avatar": "a.jpg",
            "location": "Moscow", "gender": "male",
        }), patch("routers.login.verify_password", return_value=True):
            resp = await client.post("/api/login", data={
                "username": "testuser", "password": "password123",
            })
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    async def test_login_wrong_password(self, client):
        with patch("routers.login.info_user", return_value={
            "username": "testuser", "password_hash": "hashed",
        }), patch("routers.login.verify_password", return_value=False):
            resp = await client.post("/api/login", data={
                "username": "testuser", "password": "wrong",
            })
        assert resp.status_code == 400

    async def test_login_user_not_found(self, client):
        with patch("routers.login.info_user", return_value=None):
            resp = await client.post("/api/login", data={
                "username": "ghost", "password": "pass",
            })
        assert resp.status_code == 400

    async def test_login_missing_fields(self, client):
        resp = await client.post("/api/login", data={"username": "only_user"})
        assert resp.status_code == 422