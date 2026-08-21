import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from tests.conftest import auth_headers


@pytest.mark.asyncio
async def test_daily_tip():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learn/daily-tip")
    assert res.status_code == 200
    assert "tip_text" in res.json()


@pytest.mark.asyncio
async def test_quiz_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/learn/quiz")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_quiz_submit_answer():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/learn/quiz/submit-answer",
            json={"question_id": "q-001", "selected_option_id": "o-2"},
            headers=auth_headers(),
        )
    assert res.status_code == 200
    data = res.json()
    assert data["is_correct"] is True
    assert "explanation" in data


@pytest.mark.asyncio
async def test_risk_score_requires_auth():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assist/risk-score")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_risk_score_authenticated():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/v1/assist/risk-score", headers=auth_headers())
    assert res.status_code == 200
    body = res.json()
    assert 0 <= body["score"] <= 100
    assert "signal_breakdown" in body
    assert "disclaimer" in body
