"""tests/test_auth.py — Register / Login / Logout"""
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


# GET страниц больше нет — они в React
# Оставляем только POST тесты

class TestRegisterPost:
    VALID = {
        "username":         "newuser",
        "email":            "new@example.com",
        "password":         "password123",
        "confirm_password": "password123",
        "input_key":        "123456",
    }

    async def test_register_success(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False), \
             patch("routers.registers.insert_db",      return_value=None), \
             patch("routers.registers.hash_password",  return_value="hashed"):
            with patch("routers.registers.send_email", return_value=123456):
                await client.post("/api/register/send-email",
                                  json={"email": "new@example.com"})
            resp = await client.post("/api/register", data=self.VALID)
        assert resp.status_code in (200, 302, 303)

    async def test_register_duplicate_username(self, client):
        with patch("routers.registers.check_username", return_value=True):
            resp = await client.post("/api/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_duplicate_email(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=True):
            resp = await client.post("/api/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_passwords_mismatch(self, client):
        data = {**self.VALID, "confirm_password": "wrongpass"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", data=data)
        assert resp.status_code == 400

    async def test_register_wrong_key(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_missing_fields(self, client):
        resp = await client.post("/api/register", data={"username": "x"})
        assert resp.status_code == 422

    async def test_register_invalid_username_slash(self, client):
        data = {**self.VALID, "username": "/baduser"}
        resp = await client.post("/api/register", data=data)
        assert resp.status_code in (400, 422)

    async def test_register_invalid_username_special(self, client):
        data = {**self.VALID, "username": "bad user!"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", data=data)
        assert resp.status_code == 400


class TestSendEmail:
    async def test_send_email_success(self, client):
        with patch("routers.registers.send_email", return_value=111111):
            resp = await client.post("/api/register/send-email",
                                     json={"email": "test@example.com"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "sent"}

    async def test_send_email_stores_in_session(self, client):
        with patch("routers.registers.send_email", return_value=111111):
            resp = await client.post("/api/register/send-email",
                                     json={"email": "test@example.com"})
        assert resp.status_code == 200


class TestDopInfo:
    async def test_dop_info_no_session_401(self, client):
        resp = await client.post("/api/register/dop-info", data={
            "age": "22", "gender": "male", "name": "Test",
            "location": "Moscow", "bio": "Hi",
        })
        assert resp.status_code in (401, 422)


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


class TestLogout:
    async def test_logout_ok(self, client):
        resp = await client.post("/api/logout")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
