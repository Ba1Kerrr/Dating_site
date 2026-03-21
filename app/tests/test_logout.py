import pytest

pytestmark = pytest.mark.asyncio


class TestLogout:
    async def test_logout_ok(self, client):
        resp = await client.post("/api/logout")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"