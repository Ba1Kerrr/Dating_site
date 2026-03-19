"""tests/test_smoke.py — Smoke тесты"""
import pytest
pytestmark = pytest.mark.asyncio


class TestSmoke:
    @pytest.mark.parametrize("path", [
        "/docs",
        "/openapi.json",
    ])
    async def test_get_routes_not_500(self, client, path):
        resp = await client.get(path)
        assert resp.status_code != 500, f"{path} вернул 500"

    async def test_root_not_500(self, client):
        resp = await client.get("/")
        assert resp.status_code != 500

    async def test_logout_not_500(self, client):
        resp = await client.post("/api/logout")
        assert resp.status_code != 500

    async def test_openapi_schema_valid(self, client):
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        schema = resp.json()
        assert "openapi" in schema
        assert "paths" in schema
        paths = schema["paths"]
        assert any("/api/register" in p for p in paths)
        assert any("/api/login" in p for p in paths)