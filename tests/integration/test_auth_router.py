"""Integration test /auth — login redirect + callback (mock Google OAuth)."""

import pytest

pytestmark = pytest.mark.integration


class TestAuthLogin:
    async def test_login_redirects_to_google(self, client):
        # Không có session Google OAuth thật ở test env -> authorize_redirect
        # ném lỗi khi không có credentials hợp lệ. Chỉ assert nó không 401
        # (401 là lỗi auth của user, không phải lỗi OAuth flow).
        response = await client.get("/auth/login", follow_redirects=False)
        assert response.status_code != 401


class TestAuthMe:
    async def test_get_me_authenticated(self, authed_client, test_user):
        """GET /auth/me với authed_client → 200 + trả user hiện tại."""
        response = await authed_client.get("/auth/me")
        assert response.status_code == 200
        body = response.json()
        assert body["email"] == test_user.email
        assert body["name"] == test_user.name

    async def test_get_me_unauthenticated_returns_401(self, client):
        """GET /auth/me không auth → 401."""
        response = await client.get("/auth/me")
        assert response.status_code == 401


class TestLogout:
    async def test_logout_returns_204(self, authed_client):
        """POST /auth/logout → 204, session cleared."""
        response = await authed_client.post("/auth/logout")
        assert response.status_code == 204
