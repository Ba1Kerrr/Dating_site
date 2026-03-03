"""
tests/test_smoke.py — Smoke тесты: все роуты отвечают, не падают с 500
"""
import pytest
pytestmark = pytest.mark.asyncio


class TestSmoke:
    """Проверяем что каждый роут вообще отвечает (не 500)"""

    @pytest.mark.parametrize("path", [
        "/register",
        "/login",
        "/logout",
        "/forgot/forgot_password",
        "/forgot/username",
        "/docs",
        "/openapi.json",
    ])
    async def test_get_routes_not_500(self, client, path):
        resp = await client.get(path)
        assert resp.status_code != 500, f"{path} вернул 500"

    async def test_root_not_500(self, client):
        resp = await client.get("/")
        assert resp.status_code != 500

    async def test_openapi_schema_valid(self, client):
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "openapi" in schema
        assert "paths" in schema
        # Проверяем что ключевые роуты есть в схеме
        paths = schema["paths"]
        assert any("/register" in p for p in paths)
        assert any("/login" in p for p in paths)
