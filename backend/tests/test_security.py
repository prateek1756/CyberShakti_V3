import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.shared.task_registry import register_task_owner
from tests.conftest import TEST_USER_ID, TEST_USER_PASSWORD, TEST_USER_EMAIL, auth_headers


@pytest.mark.asyncio
async def test_login_success_issues_typed_tokens():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/login",
            json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )
    assert res.status_code == 200
    body = res.json()
    assert body["token_type"] == "bearer"
    assert body["requires_2fa"] is False
    assert body.get("refresh_token")


@pytest.mark.asyncio
async def test_login_sql_injection_is_literal():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "' OR 1=1 --"},
        )
    assert res.status_code == 401
    assert res.json()["detail"]["error_code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_command_injection_url_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-url",
            json={"url": "; cat /etc/passwd"},
            headers=auth_headers(),
        )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_jwt_alg_none_rejected():
    import base64
    import json
    import time

    def b64url(obj):
        raw = json.dumps(obj, separators=(",", ":")).encode("utf-8")
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")

    now = int(time.time())
    token = (
        b64url({"alg": "none", "typ": "JWT"})
        + "."
        + b64url({"sub": str(TEST_USER_ID), "type": "access", "iat": now, "exp": now + 3600})
        + "."
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_task_status_unknown_is_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/tasks/00000000-0000-0000-0000-000000000099/status",
            headers=auth_headers(),
        )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_task_status_forbidden_for_other_user():
    other_id = "11111111-1111-1111-1111-111111111111"
    register_task_owner("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", other_id)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get(
            "/api/v1/tasks/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/status",
            headers=auth_headers(),
        )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_password_reset_request_does_not_enumerate():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        known = await ac.post("/api/v1/auth/password-reset/request", json={"email": TEST_USER_EMAIL})
        unknown = await ac.post("/api/v1/auth/password-reset/request", json={"email": "missing@example.com"})
    assert known.status_code == 200
    assert unknown.status_code == 200
    assert known.json()["message"] == unknown.json()["message"]


@pytest.mark.asyncio
async def test_screenshot_rejects_non_image_magic():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-screenshot",
            files={"file": ("../../etc/passwd", b"not-an-image", "image/png")},
            headers=auth_headers(),
        )
    assert res.status_code == 415


@pytest.mark.asyncio
async def test_rate_limit_login(monkeypatch):
    from app.config import settings
    from app.shared import rate_limit

    rate_limit._buckets.clear()
    monkeypatch.setattr(settings, "RATE_LIMIT_ENABLED", True)
    monkeypatch.setattr(settings, "RATE_LIMIT_AUTH_PER_MINUTE", 3)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        last = None
        for _ in range(4):
            last = await ac.post(
                "/api/v1/auth/login",
                json={"email": "nobody@example.com", "password": "wrong-password"},
            )
    assert last.status_code == 429
    assert last.json()["error_code"] == "RATE_LIMIT_EXCEEDED"
    rate_limit._buckets.clear()
