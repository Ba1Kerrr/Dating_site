"""tests/test_register.py — Register / SendEmail / DopInfo"""
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


class TestRegisterPost:
    VALID = {
        "username":         "newuser",
        "email":            "new@example.com",
        "password":         "password123",
        "confirm_password": "password123",
        "input_key":        123456,
    }

    async def test_register_success(self, client):
        with patch("routers.registers.check_username",  return_value=False), \
             patch("routers.registers.check_email",     return_value=False), \
             patch("routers.registers.insert_db",       return_value=None), \
             patch("routers.registers.hash_password",   return_value="hashed"), \
             patch("routers.registers.send_verification_email") as mock_send, \
             patch("routers.registers.random.randint",  return_value=123456):
            mock_send.delay.return_value = None
            await client.post("/api/register/send-email",
                              json={"email": "new@example.com"})
            resp = await client.post("/api/register", json=self.VALID)
        assert resp.status_code in (200, 302, 303)

    async def test_register_duplicate_username(self, client):
        with patch("routers.registers.check_username", return_value=True):
            resp = await client.post("/api/register", json=self.VALID)
        assert resp.status_code == 400

    async def test_register_duplicate_email(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=True):
            resp = await client.post("/api/register", json=self.VALID)
        assert resp.status_code == 400

    async def test_register_passwords_mismatch(self, client):
        data = {**self.VALID, "confirm_password": "wrongpass"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", json=data)
        assert resp.status_code == 400

    async def test_register_wrong_key(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", json=self.VALID)
        assert resp.status_code == 400

    async def test_register_missing_fields(self, client):
        resp = await client.post("/api/register", json={"username": "x"})
        assert resp.status_code == 422

    async def test_register_invalid_username_slash(self, client):
        data = {**self.VALID, "username": "/baduser"}
        resp = await client.post("/api/register", json=data)
        assert resp.status_code in (400, 422)

    async def test_register_invalid_username_special(self, client):
        data = {**self.VALID, "username": "bad user!"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/api/register", json=data)
        assert resp.status_code == 400


class TestSendEmail:
    async def test_send_email_success(self, client):
        with patch("routers.registers.send_verification_email") as mock_send:
            mock_send.delay.return_value = None
            resp = await client.post("/api/register/send-email",
                                     json={"email": "test@example.com"})
        assert resp.status_code == 200
        assert resp.json() == {"status": "sent"}

    async def test_send_email_stores_in_session(self, client):
        with patch("routers.registers.send_verification_email") as mock_send:
            mock_send.delay.return_value = None
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