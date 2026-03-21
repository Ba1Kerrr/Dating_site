import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


# ── Хелпер: логин через сессию ───────────────────────────────────────

async def _login(client, username="testuser"):
    from funcs.rate_limit import _request_log, _lock
    async with _lock:
        _request_log.clear()

    with patch("routers.login.info_user", return_value={
        "username": username,
        "password_hash": "hashed",
        "email": f"{username}@test.com",
        "avatar": None,
        "location": "Moscow",
        "gender": "male",
    }), patch("routers.login.verify_password", return_value=True):
        resp = await client.post("/api/login", data={
            "username": username, "password": "pass"
        })
        client.cookies = resp.cookies
    return client


# ── Блокировка ───────────────────────────────────────────────────────

class TestBlock:

    async def test_block_unauthenticated_401(self, client):
        """Без авторизации — 401."""
        resp = await client.post("/api/users/someuser/block")
        assert resp.status_code == 401

    async def test_block_success(self, client):
        """Залогиненный юзер блокирует другого — 200."""
        await _login(client)
        with patch("routers.blocks.block_user", return_value={"ok": True}):
            resp = await client.post("/api/users/otheruser/block")
        assert resp.status_code == 200
        assert resp.json()["status"] == "blocked"
        assert resp.json()["target"] == "otheruser"

    async def test_block_already_blocked_400(self, client):
        """Повторная блокировка — бэкенд возвращает ошибку → 400."""
        await _login(client)
        with patch("routers.blocks.block_user",
                   return_value={"ok": False, "error": "already_blocked"}):
            resp = await client.post("/api/users/otheruser/block")
        assert resp.status_code == 400

    async def test_block_self_400(self, client):
        """Нельзя заблокировать себя."""
        await _login(client)
        with patch("routers.blocks.block_user",
                   return_value={"ok": False, "error": "cannot_block_self"}):
            resp = await client.post("/api/users/testuser/block")
        assert resp.status_code == 400
        assert "cannot_block_self" in resp.json()["detail"]

    async def test_unblock_success(self, client):
        """Разблокировка — 200."""
        await _login(client)
        with patch("routers.blocks.unblock_user", return_value={"ok": True}):
            resp = await client.delete("/api/users/otheruser/block")
        assert resp.status_code == 200
        assert resp.json()["status"] == "unblocked"

    async def test_unblock_unauthenticated_401(self, client):
        resp = await client.delete("/api/users/someuser/block")
        assert resp.status_code == 401

    async def test_get_blocked_list_unauthenticated_401(self, client):
        resp = await client.get("/api/users/blocks")
        assert resp.status_code == 401

    async def test_get_blocked_list_empty(self, client):
        """Пустой чёрный список."""
        await _login(client)
        with patch("routers.blocks.get_blocked_list", return_value=[]):
            resp = await client.get("/api/users/blocks")
        assert resp.status_code == 200
        assert resp.json()["blocked"] == []

    async def test_get_blocked_list_with_users(self, client):
        """Список с одним заблокированным."""
        await _login(client)
        mock_list = [{"username": "baduser", "name": "Bad", "avatar": None, "blocked_at": "2026-03-21T00:00:00"}]
        with patch("routers.blocks.get_blocked_list", return_value=mock_list):
            resp = await client.get("/api/users/blocks")
        assert resp.status_code == 200
        data = resp.json()["blocked"]
        assert len(data) == 1
        assert data[0]["username"] == "baduser"


# ── Жалобы ───────────────────────────────────────────────────────────

class TestReport:

    async def test_report_unauthenticated_401(self, client):
        resp = await client.post("/api/users/someuser/report",
                                 json={"reason": "spam"})
        assert resp.status_code == 401

    async def test_report_success(self, client):
        """Успешная жалоба — 200."""
        await _login(client)
        with patch("routers.blocks.create_report", return_value={"ok": True}):
            resp = await client.post("/api/users/otheruser/report",
                                     json={"reason": "spam", "comment": None})
        assert resp.status_code == 200
        assert resp.json()["status"] == "reported"

    async def test_report_already_reported_409(self, client):
        """Повторная жалоба — 409."""
        await _login(client)
        with patch("routers.blocks.create_report",
                   return_value={"ok": False, "error": "already_reported"}):
            resp = await client.post("/api/users/otheruser/report",
                                     json={"reason": "fake"})
        assert resp.status_code == 409

    async def test_report_invalid_reason_400(self, client):
        """Неверная причина — 400."""
        await _login(client)
        with patch("routers.blocks.create_report",
                   return_value={"ok": False, "error": "invalid_reason"}):
            resp = await client.post("/api/users/otheruser/report",
                                     json={"reason": "invalid_reason"})
        assert resp.status_code == 400

    async def test_report_self_400(self, client):
        """Нельзя жаловаться на себя."""
        await _login(client)
        with patch("routers.blocks.create_report",
                   return_value={"ok": False, "error": "cannot_report_self"}):
            resp = await client.post("/api/users/testuser/report",
                                     json={"reason": "spam"})
        assert resp.status_code == 400

    async def test_report_with_comment(self, client):
        """Жалоба с комментарием."""
        await _login(client)
        with patch("routers.blocks.create_report", return_value={"ok": True}):
            resp = await client.post("/api/users/otheruser/report",
                                     json={"reason": "other",
                                           "comment": "Ведёт себя неприемлемо"})
        assert resp.status_code == 200

    async def test_report_missing_reason_422(self, client):
        """Без поля reason — 422."""
        await _login(client)
        resp = await client.post("/api/users/otheruser/report", json={})
        assert resp.status_code == 422

    @pytest.mark.parametrize("reason", ["spam", "fake", "abuse", "underage", "other"])
    async def test_report_all_valid_reasons(self, client, reason):
        """Все допустимые причины принимаются."""
        await _login(client)
        with patch("routers.blocks.create_report", return_value={"ok": True}):
            resp = await client.post("/api/users/otheruser/report",
                                     json={"reason": reason})
        assert resp.status_code == 200


# ── Админ: очередь жалоб ─────────────────────────────────────────────

class TestAdminReports:

    async def _login_admin(self, client):
        from funcs.rate_limit import _request_log, _lock
        async with _lock:
            _request_log.clear()
        with patch("routers.login.info_user", return_value={
            "username": "Ba1kerr",
            "password_hash": "hashed",
            "email": "admin@test.com",
            "avatar": None,
            "location": None,
            "gender": None,
        }), patch("routers.login.verify_password", return_value=True):
            resp = await client.post("/api/login", data={
                "username": "Ba1kerr", "password": "adminpass"
            })
            client.cookies = resp.cookies
        return client

    async def test_admin_reports_forbidden_for_user(self, client):
        """Обычный пользователь не видит жалобы — 403."""
        await _login(client)
        with patch("routers.blocks.get_user_role", return_value="user"):
            resp = await client.get("/api/admin/reports")
        assert resp.status_code == 403

    async def test_admin_reports_success(self, client):
        """Админ видит список жалоб."""
        await self._login_admin(client)
        mock_reports = [
            {
                "id": 1, "reporter": "user1", "target": "user2",
                "target_avatar": None, "reason": "spam", "comment": None,
                "status": "pending", "created_at": "2026-03-21T00:00:00",
                "reviewed_at": None,
            }
        ]
        with patch("routers.blocks.get_user_role", return_value="admin"), \
             patch("routers.blocks.get_reports", return_value=mock_reports):
            resp = await client.get("/api/admin/reports")
        assert resp.status_code == 200
        data = resp.json()
        assert "reports" in data
        assert data["count"] == 1

    async def test_admin_reports_empty(self, client):
        """Пустая очередь."""
        await self._login_admin(client)
        with patch("routers.blocks.get_user_role", return_value="admin"), \
             patch("routers.blocks.get_reports", return_value=[]):
            resp = await client.get("/api/admin/reports")
        assert resp.status_code == 200
        assert resp.json()["count"] == 0

    async def test_admin_review_dismiss(self, client):
        """Админ отклоняет жалобу."""
        await self._login_admin(client)
        with patch("routers.blocks.get_user_role", return_value="admin"), \
             patch("routers.blocks.review_report",
                   return_value={"ok": True, "action": "dismiss"}):
            resp = await client.post("/api/admin/reports/1/review",
                                     json={"action": "dismiss"})
        assert resp.status_code == 200
        assert resp.json()["action"] == "dismiss"

    async def test_admin_review_ban(self, client):
        """Админ банит нарушителя."""
        await self._login_admin(client)
        with patch("routers.blocks.get_user_role", return_value="admin"), \
             patch("routers.blocks.review_report",
                   return_value={"ok": True, "action": "ban"}):
            resp = await client.post("/api/admin/reports/1/review",
                                     json={"action": "ban"})
        assert resp.status_code == 200
        assert resp.json()["action"] == "ban"

    async def test_admin_review_invalid_action_400(self, client):
        """Неверное действие — 400."""
        await self._login_admin(client)
        with patch("routers.blocks.get_user_role", return_value="admin"), \
             patch("routers.blocks.review_report",
                   return_value={"ok": False, "error": "action must be 'dismiss' or 'ban'"}):
            resp = await client.post("/api/admin/reports/1/review",
                                     json={"action": "delete_all"})
        assert resp.status_code == 400

    async def test_moderator_can_see_reports(self, client):
        """Модератор тоже имеет доступ."""
        await _login(client)
        with patch("routers.blocks.get_user_role", return_value="moderator"), \
             patch("routers.blocks.get_reports", return_value=[]):
            resp = await client.get("/api/admin/reports")
        assert resp.status_code == 200


# ── Функции blocks.py (unit) ─────────────────────────────────────────

class TestBlocksFunctions:

    def test_block_user_success(self):
        from funcs.blocks import block_user
        with patch("funcs.blocks.engine") as mock_engine:
            mock_conn = mock_engine.begin.return_value.__enter__.return_value
            mock_conn.execute.return_value = None
            result = block_user("alice", "bob")
        assert result["ok"] is True

    def test_block_self_returns_error(self):
        from funcs.blocks import block_user
        result = block_user("alice", "alice")
        assert result["ok"] is False
        assert result["error"] == "cannot_block_self"

    def test_is_blocked_true(self):
        from funcs.blocks import is_blocked
        with patch("funcs.blocks.engine") as mock_engine:
            mock_conn = mock_engine.connect.return_value.__enter__.return_value
            mock_conn.execute.return_value.fetchone.return_value = (1,)
            assert is_blocked("alice", "bob") is True

    def test_is_blocked_false(self):
        from funcs.blocks import is_blocked
        with patch("funcs.blocks.engine") as mock_engine:
            mock_conn = mock_engine.connect.return_value.__enter__.return_value
            mock_conn.execute.return_value.fetchone.return_value = None
            assert is_blocked("alice", "bob") is False

    def test_create_report_self_error(self):
        from funcs.blocks import create_report
        result = create_report("alice", "alice", "spam")
        assert result["ok"] is False
        assert result["error"] == "cannot_report_self"

    def test_create_report_invalid_reason(self):
        from funcs.blocks import create_report
        result = create_report("alice", "bob", "nonsense")
        assert result["ok"] is False
        assert "invalid_reason" in result["error"]

    def test_create_report_success(self):
        from funcs.blocks import create_report
        with patch("funcs.blocks.engine") as mock_engine:
            mock_conn = mock_engine.begin.return_value.__enter__.return_value
            mock_conn.execute.return_value.fetchone.return_value = None
            result = create_report("alice", "bob", "spam")
        assert result["ok"] is True

    def test_get_blocked_list_empty(self):
        from funcs.blocks import get_blocked_list
        with patch("funcs.blocks.engine") as mock_engine:
            mock_conn = mock_engine.connect.return_value.__enter__.return_value
            mock_conn.execute.return_value.fetchall.return_value = []
            result = get_blocked_list("alice")
        assert result == []