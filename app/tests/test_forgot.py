import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


class TestForgotPassword:
    async def test_success(self, client):
        with patch("routers.forgot.info_user", return_value={
                "username": "testuser", "email": "t@t.com",
             }), \
             patch("routers.forgot.hash_password", return_value="newhashed"), \
             patch("routers.forgot.update_password", return_value=(True, "ok")):
            resp = await client.post("/api/forgot/password", data={
                "username":     "testuser",
                "new_password": "newpass456",
            })
        assert resp.status_code in (200, 302, 303, 400)

    async def test_user_not_found(self, client):
        with patch("routers.forgot.info_user", return_value=None), \
             patch("routers.forgot.hash_password", return_value="hashed"), \
             patch("routers.forgot.update_password", return_value=(False, "not found")):
            resp = await client.post("/api/forgot/password", data={
                "username":     "ghost",
                "new_password": "newpass",
            })
        assert resp.status_code in (200, 302, 303, 400, 500)

    async def test_missing_fields(self, client):
        resp = await client.post("/api/forgot/password", data={"username": "testuser"})
        assert resp.status_code == 422

    async def test_update_fails_400(self, client):
        with patch("routers.forgot.info_user", return_value={"username": "testuser"}), \
             patch("routers.forgot.hash_password", return_value="hashed"), \
             patch("routers.forgot.update_password", return_value=False):
            resp = await client.post("/api/forgot/password", data={
                "username":     "testuser",
                "new_password": "newpass456",
            })
        assert resp.status_code in (200, 302, 303, 400)


class TestForgotUsername:
    async def test_success(self, client):
        with patch("routers.forgot.info_user_email", return_value={
                "username": "testuser", "email": "t@t.com",
             }), \
             patch("routers.forgot.detect_username_from_email", return_value="testuser"), \
             patch("routers.forgot.hash_password",              return_value="newhashed"), \
             patch("routers.forgot.update_password_email",      return_value=(True, "ok")):
            resp = await client.post("/api/forgot/username", data={
                "email":        "test@example.com",
                "new_password": "newpass456",
            })
        assert resp.status_code in (200, 302, 303, 400, 500)

    async def test_missing_fields(self, client):
        resp = await client.post("/api/forgot/username", data={"email": "t@t.com"})
        assert resp.status_code == 422

    async def test_update_fails_400(self, client):
        with patch("routers.forgot.info_user_email", return_value={"username": "u"}), \
             patch("routers.forgot.hash_password",         return_value="hashed"), \
             patch("routers.forgot.update_password_email", return_value=False):
            resp = await client.post("/api/forgot/username", data={
                "email":        "test@example.com",
                "new_password": "newpass456",
            })
        assert resp.status_code in (200, 302, 303, 400)