import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio

MOCK_PROFILE = {
    "id": 1, "username": "testuser", "email": "t@t.com",
    "age": 25, "gender": "male", "name": "Test",
    "avatar": "avatar.jpg", "location": "Moscow", "bio": "Hi",
}


async def _login(client):
    from funcs.rate_limit import _request_log, _lock
    async with _lock:
        _request_log.clear()

    with patch("routers.login.info_user", return_value={
        "username": "testuser", "password": "hashed",
        "email": "t@t.com", "avatar": "a.jpg",
        "location": "Moscow", "gender": "male",
    }), patch("routers.login.verify_password", return_value=True):
        resp = await client.post("/api/login", data={
            "username": "testuser", "password": "pass"
        })
        client.cookies = resp.cookies
    return client


class TestProfilePage:
    async def test_profile_unauthenticated_401(self, client):
        with patch("routers.profile.get_profile", return_value=MOCK_PROFILE):
            resp = await client.get("/api/profile/testuser")
        assert resp.status_code == 401

    async def test_profile_authenticated_200(self, client):
        await _login(client)
        with patch("routers.profile.get_profile", return_value=MOCK_PROFILE):
            resp = await client.get("/api/profile/testuser")
        assert resp.status_code == 200

    async def test_profile_not_found_404(self, client):
        await _login(client)
        with patch("routers.profile.get_profile", return_value=None):
            resp = await client.get("/api/profile/ghost_user")
        assert resp.status_code == 404

    async def test_edit_profile_forbidden_other_user(self, client):
        await _login(client)
        resp = await client.post("/api/profile/otheruser/edit", data={
            "name": "Hacker", "bio": "", "location": "", "age": "0",
        })
        assert resp.status_code == 403

    async def test_edit_profile_no_session_401(self, client):
        resp = await client.post("/api/profile/testuser/edit", data={
            "name": "Test", "bio": "", "location": "", "age": "0",
        })
        assert resp.status_code == 401


class TestChatList:
    async def test_chat_list_unauthenticated_401(self, client):
        resp = await client.get("/api/chat/list")
        assert resp.status_code == 401

    async def test_chat_list_authenticated_200(self, client):
        await _login(client)
        with patch("routers.chat.get_user_chats", return_value=[]):
            resp = await client.get("/api/chat/list")
        assert resp.status_code == 200

    async def test_chat_history_no_match_403(self, client):
        from funcs.jwt_auth import create_access_token
        token = create_access_token("testuser")
        with patch("routers.chat.check_match_exists", return_value=False):
            resp = await client.get(
                "/api/chat/anna/history",
                headers={"Authorization": f"Bearer {token}"}
            )
        assert resp.status_code == 403

    async def test_chat_history_with_match_200(self, client):
        from funcs.jwt_auth import create_access_token
        token = create_access_token("testuser")
        with patch("routers.chat.check_match_exists", return_value=True), \
             patch("routers.chat.get_messages", return_value=[
                 {"id": 1, "sender": "testuser", "receiver": "anna",
                  "text": "hi", "created_at": None, "is_read": True}
             ]):
            resp = await client.get(
                "/api/chat/anna/history",
                headers={"Authorization": f"Bearer {token}"}
            )
        assert resp.status_code == 200
        assert "messages" in resp.json()