import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_emergency_number_exclusion():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/protect/check-phone",
            json={"phone_number": "112"},
            headers=auth_headers(),
        )
    assert res.status_code == 200
    data = res.json()
    assert data["is_emergency_service"] is True
    assert data["verdict"] is None


@pytest.mark.asyncio
async def test_password_strength_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/protect/check-password",
            json={"password": "password123"},
            headers=auth_headers(),
        )
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"]["strength_level"] == "very_weak"
    assert "disclaimer" in data["verdict"]


@pytest.mark.asyncio
async def test_encrypt_decrypt_roundtrip_endpoint():
    payload = b"hello-cybershakti"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        enc = await ac.post(
            "/api/v1/protect/encrypt-file",
            files={"file": ("note.txt", payload, "text/plain")},
            data={"password": "Secret123!"},
            headers=auth_headers(),
        )
        assert enc.status_code == 200
        blob = enc.content
        dec = await ac.post(
            "/api/v1/protect/decrypt-file",
            files={"file": ("note.txt.enc", blob, "application/octet-stream")},
            data={"password": "Secret123!"},
            headers=auth_headers(),
        )
        assert dec.status_code == 200
        assert dec.content == payload


@pytest.mark.asyncio
async def test_decrypt_wrong_password_returns_400():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        enc = await ac.post(
            "/api/v1/protect/encrypt-file",
            files={"file": ("note.txt", b"secret", "text/plain")},
            data={"password": "Secret123!"},
            headers=auth_headers(),
        )
        dec = await ac.post(
            "/api/v1/protect/decrypt-file",
            files={"file": ("note.txt.enc", enc.content, "application/octet-stream")},
            data={"password": "WrongPass"},
            headers=auth_headers(),
        )
    assert dec.status_code == 400
    assert dec.json()["detail"]["error_code"] == "WRONG_PASSWORD"
