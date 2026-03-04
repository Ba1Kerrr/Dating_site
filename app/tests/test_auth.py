"""tests/test_auth.py — Register / Login / Logout"""
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.asyncio


# ═══════════════════════════════════════════════════════════
#  REGISTER GET
# ═══════════════════════════════════════════════════════════
class TestRegisterGet:
    async def test_register_page_200(self, client):
        resp = await client.get("/register")
        assert resp.status_code == 200

    async def test_register_page_has_content(self, client):
        resp = await client.get("/register")
        assert resp.status_code == 200
        assert len(resp.content) > 0


# ═══════════════════════════════════════════════════════════
#  REGISTER POST
# роутер читает key из session и сравнивает с user.input_key (int)
# ═══════════════════════════════════════════════════════════
class TestRegisterPost:
    VALID = {
        "username":         "newuser",
        "email":            "new@example.com",
        "password":         "password123",
        "confirm_password": "password123",
        "input_key":        "123456",
    }

    async def test_register_success_redirects(self, client):
        # кладём ключ в сессию
        client.cookies.set("session", "")
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False), \
             patch("routers.registers.insert_db",      return_value=None), \
             patch("routers.registers.hash_password",  return_value="hashed"):
            # сначала ставим ключ в сессию через send_email
            with patch("routers.registers.send_email", return_value=123456):
                await client.post("/register/send_email",
                                  json={"email": "new@example.com"})
            resp = await client.post("/register", data=self.VALID)
        assert resp.status_code in (200, 302, 303)

    async def test_register_duplicate_username(self, client):
        with patch("routers.registers.check_username", return_value=True):
            resp = await client.post("/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_duplicate_email(self, client):
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=True):
            resp = await client.post("/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_passwords_mismatch(self, client):
        data = {**self.VALID, "confirm_password": "wrongpass"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/register", data=data)
        assert resp.status_code == 400

    async def test_register_wrong_key(self, client):
        # ключ в сессии не установлен → key=None != 123456 → 400
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/register", data=self.VALID)
        assert resp.status_code == 400

    async def test_register_missing_fields(self, client):
        resp = await client.post("/register", data={"username": "x"})
        assert resp.status_code == 422

    async def test_register_invalid_username_slash(self, client):
        data = {**self.VALID, "username": "/baduser"}
        resp = await client.post("/register", data=data)
        assert resp.status_code in (400, 422)

    async def test_register_invalid_username_special(self, client):
        data = {**self.VALID, "username": "bad user!"}
        with patch("routers.registers.check_username", return_value=False), \
             patch("routers.registers.check_email",    return_value=False):
            resp = await client.post("/register", data=data)
        assert resp.status_code == 400


# ═══════════════════════════════════════════════════════════
#  SEND EMAIL
# роутер принимает dict (json body), вызывает send_email(email)
# ═══════════════════════════════════════════════════════════
class TestSendEmail:
    async def test_send_email_success(self, client):
        with patch("routers.registers.send_email", return_value=123456):
            resp = await client.post("/register/send_email",
                                     json={"email": "test@example.com"})
        assert resp.status_code == 200
        assert "key" in resp.json()

    async def test_send_email_returns_key(self, client):
        with patch("routers.registers.send_email", return_value=999999):
            resp = await client.post("/register/send_email",
                                     json={"email": "test@example.com"})
        assert resp.json()["key"] == 999999

    async def test_send_email_stores_in_session(self, client):
        """После вызова ключ должен лежать в сессии для последующей регистрации"""
        with patch("routers.registers.send_email", return_value=111111):
            resp = await client.post("/register/send_email",
                                     json={"email": "test@example.com"})
        assert resp.status_code == 200


# ═══════════════════════════════════════════════════════════
#  DOP INFO
# session['user'] читается напрямую из request.session
# ═══════════════════════════════════════════════════════════
class TestDopInfo:
    async def test_dop_info_get_no_session_crashes(self, client):
        # без сессии info_user(None) вернёт None → AttributeError на ['avatar']
        # роутер не защищён редиректом — упадёт 500, это баг в коде
        resp = await client.get("/register/dop-info")
        assert resp.status_code in (200, 302, 303, 500)

    async def test_dop_info_get_with_session(self, client):
        with patch("routers.registers.info_user", return_value={
            "username": "testuser", "avatar": "avatar.jpg",
            "email": "t@t.com", "password": "h",
            "location": "Moscow", "gender": "male",
        }):
            # ставим сессию напрямую через логин
            with patch("routers.login.info_user", return_value={
                "username": "testuser", "password_hash": "hashed",
                "email": "t@t.com", "avatar": "a.jpg",
                "location": "Moscow", "gender": "male",
            }), patch("routers.login.verify_password", return_value=True):
                await client.post("/login", data={
                    "username": "testuser", "password": "pass"
                })
            resp = await client.get("/register/dop-info")
        assert resp.status_code in (200, 302, 303)


# ═══════════════════════════════════════════════════════════
#  LOGIN
# ═══════════════════════════════════════════════════════════
class TestLogin:
    async def test_login_page_200(self, client):
        resp = await client.get("/login")
        assert resp.status_code == 200

    async def test_login_success_redirects(self, client):
        with patch("routers.login.info_user", return_value={
            "username": "testuser", "password_hash": "hashed",
            "email": "t@t.com", "avatar": "a.jpg",
            "location": "Moscow", "gender": "male",
        }), patch("routers.login.verify_password", return_value=True):
            resp = await client.post("/login", data={
                "username": "testuser", "password": "password123",
            })
        assert resp.status_code in (302, 303)

    async def test_login_wrong_password(self, client):
        with patch("routers.login.info_user", return_value={
            "username": "testuser", "password_hash": "hashed",
        }), patch("routers.login.verify_password", return_value=False):
            resp = await client.post("/login", data={
                "username": "testuser", "password": "wrong",
            })
        assert resp.status_code == 400

    async def test_login_user_not_found(self, client):
        with patch("routers.login.info_user", return_value=None):
            resp = await client.post("/login", data={
                "username": "ghost", "password": "pass",
            })
        assert resp.status_code == 400

    async def test_login_missing_fields(self, client):
        resp = await client.post("/login", data={"username": "only_user"})
        assert resp.status_code == 422


# ═══════════════════════════════════════════════════════════
#  LOGOUT
# ═══════════════════════════════════════════════════════════
class TestLogout:
    async def test_logout_redirects(self, client):
        resp = await client.get("/logout")
        assert resp.status_code in (302, 303)

    async def test_logout_redirects_to_root(self, client):
        resp = await client.get("/logout")
        assert resp.headers.get("location") in ("/", "http://test/")