import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from tests.conftest import auth_headers
from app.detect_analyze.url import extract_url_features


@pytest.mark.asyncio
async def test_scan_url_optional_auth():
    # scan-url permits unauthenticated access (user_id will be None)
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/scan-url", json={"url": "http://bank-kyc-verify.info"})
    assert res.status_code == 200
    assert "verdict" in res.json()


@pytest.mark.asyncio
async def test_scan_url_phishing():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-url",
            json={"url": "http://sbi-verify-kyc.info/login?token=abc"},
            headers=auth_headers(),
        )
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"]["risk_level"] in ["high_risk", "moderate_risk", "safe"]
    assert "explanation" in data["verdict"]
    assert "url_features" in data


@pytest.mark.asyncio
async def test_scan_url_invalid():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-url",
            json={"url": "invalid_url_string"},
            headers=auth_headers(),
        )
    assert res.status_code == 400
    assert res.json()["detail"]["error_code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_scan_message_scam():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/detect/scan-message",
            json={"text": "URGENT: Your bank account is suspended. Update KYC immediately at http://bit.ly/kyc-fix or call 9876543210."},
            headers=auth_headers(),
        )
    assert res.status_code == 200
    data = res.json()
    assert data["verdict"]["risk_level"] in ["high_risk", "moderate_risk"]
    assert "disclaimer" in data["verdict"]


def test_url_features_detect_ip():
    features = extract_url_features("http://192.168.1.1/kyc-verify")
    assert features["has_ip_address"] == 1
    assert features["url_length"] == len("http://192.168.1.1/kyc-verify")
