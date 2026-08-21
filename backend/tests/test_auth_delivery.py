import pytest
from unittest.mock import patch, MagicMock
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.shared.email_service import EmailService

@pytest.mark.asyncio
@patch("app.shared.email_service.EmailService.send_verification_email")
async def test_registration_triggers_verification_email(mock_send):
    mock_send.return_value = True
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "strongpassword123",
                "consent_given": True
            }
        )
        
    assert res.status_code == 201
    assert res.json()["message"] == "Registration successful. Please check your email to verify your account."
    
    # Verify mock was called with the correct recipient
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert args[0] == "newuser@example.com"
    # Ensure raw token was generated (string of sufficient length)
    assert len(args[1]) >= 32
    
    # Ensure the raw token is NOT returned in the API response payload
    response_text = res.text
    assert args[1] not in response_text

@pytest.mark.asyncio
@patch("app.shared.email_service.EmailService.send_password_reset_email")
async def test_password_reset_request_triggers_email(mock_send):
    mock_send.return_value = True
    
    # Registration to ensure user exists
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/api/v1/auth/register",
            json={
                "email": "resetuser@example.com",
                "password": "strongpassword123",
                "consent_given": True
            }
        )
        
        # Request password reset
        res = await ac.post(
            "/api/v1/auth/password-reset/request",
            json={"email": "resetuser@example.com"}
        )
        
    assert res.status_code == 200
    assert res.json()["message"] == "If an account exists for that email, a reset link has been sent."
    
    # Verify mock was called
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert args[0] == "resetuser@example.com"
    assert len(args[1]) >= 32
    
    # Ensure raw token is NOT returned in the API response payload
    assert args[1] not in res.text
