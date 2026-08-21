import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.shared.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


@pytest.mark.asyncio
async def test_register_rejects_missing_consent():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/register",
            json={"email": "user@example.com", "password": "longenough", "consent_given": False},
        )
    assert res.status_code == 400
    assert res.json()["detail"]["error_code"] == "CONSENT_REQUIRED"


@pytest.mark.asyncio
async def test_login_invalid_credentials_generic():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
    assert res.status_code == 401
    assert res.json()["detail"]["error_code"] == "INVALID_CREDENTIALS"
    assert "email" not in res.json()["detail"]["message"].lower() or "password" in res.json()["detail"]["message"].lower()


@pytest.mark.asyncio
async def test_me_requires_access_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/auth/me")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_cannot_be_used_as_access_token():
    token = create_refresh_token({"sub": "00000000-0000-0000-0000-000000000001"})
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_two_fa_session_token_cannot_be_used_as_access_token():
    token = create_access_token(
        {"sub": "00000000-0000-0000-0000-000000000001", "scope": "2fa", "type": "2fa"}
    )
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401


def test_argon2id_hash_and_verify():
    hashed = hash_password("correct-horse-battery")
    assert hashed.startswith("$argon2id$")
    assert verify_password("correct-horse-battery", hashed) is True
    assert verify_password("wrong", hashed) is False


def test_access_token_type_claim():
    token = create_access_token({"sub": "user-1", "role": "user"})
    payload = decode_token(token)
    assert payload["type"] == "access"
    assert payload["sub"] == "user-1"


def test_refresh_token_hash_is_lookup_stable():
    token = "opaque-refresh-token-value"
    assert hash_refresh_token(token) == hash_refresh_token(token)
    assert len(hash_refresh_token(token)) == 64


@pytest.mark.asyncio
async def test_me_with_access_token():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        token = create_access_token({"sub": "00000000-0000-0000-0000-000000000001", "role": "user"})
        res = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["email"] == "user@example.com"
