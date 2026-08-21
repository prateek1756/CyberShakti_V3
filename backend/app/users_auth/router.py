from datetime import datetime, timezone, timedelta
import secrets
import pyotp
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.config import settings
from app.shared.database import get_db
from app.shared.models import (
    User, RefreshToken, AuditLog, TOTPSecret, BackupCode,
    PasswordResetToken, EmailVerificationToken,
)
from app.shared.security import (
    hash_password, verify_password, create_access_token, create_refresh_token, decode_token,
    hash_refresh_token, encrypt_totp_secret, decrypt_totp_secret,
)
from app.shared.auth import get_current_user
from app.shared.email_service import EmailService

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    consent_given: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetComplete(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class DeleteAccountRequest(BaseModel):
    password: str
    confirmation: str


class TwoFALoginRequest(BaseModel):
    two_fa_session_token: str
    totp_code: str = Field(min_length=6, max_length=12)


class TwoFAConfirmRequest(BaseModel):
    totp_code: str = Field(min_length=6, max_length=12)


GENERIC_REGISTER_MSG = "Registration successful. Please check your email to verify your account."


async def _issue_session(db: AsyncSession, user: User) -> dict:
    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    await db.commit()
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "requires_2fa": False,
        "refresh_token": refresh_token,
    }


async def _revoke_all_refresh_tokens(db: AsyncSession, user_id) -> None:
    now = datetime.now(timezone.utc)
    stmt = select(RefreshToken).where(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None),
    )
    tokens = (await db.execute(stmt)).scalars().all()
    for token in tokens:
        token.revoked_at = now


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    if not payload.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "CONSENT_REQUIRED", "message": "User consent is required for account creation."}
        )

    stmt = select(User).where(User.email == payload.email.lower())
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        return {"message": GENERIC_REGISTER_MSG}

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        email_verified=False,
        is_active=True,
    )
    db.add(user)
    await db.flush()

    verify_token = secrets.token_urlsafe(32)
    db.add(EmailVerificationToken(
        user_id=user.id,
        token_hash=hash_refresh_token(verify_token),
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    ))
    db.add(AuditLog(event_type="user_registration", user_id=user.id))
    await db.commit()

    # Deliver verification email (REM-05) - raw token is passed to verification link
    EmailService.send_verification_email(payload.email.lower(), verify_token)

    return {"message": GENERIC_REGISTER_MSG}


@router.get("/verify-email")
async def verify_email(token: str = Query(...), db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(token)
    stmt = select(EmailVerificationToken).where(EmailVerificationToken.token_hash == token_hash)
    stored = (await db.execute(stmt)).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not stored or stored.used_at is not None or stored.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "TOKEN_INVALID", "message": "Verification token is invalid or expired."},
        )

    user = (await db.execute(select(User).where(User.id == stored.user_id))).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "TOKEN_INVALID", "message": "Verification token is invalid or expired."},
        )
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error_code": "ALREADY_VERIFIED", "message": "Email is already verified."},
        )

    user.email_verified = True
    stored.used_at = now
    await db.commit()
    return {"message": "Email verified. You can now log in."}


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email.lower(), User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    generic_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error_code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise generic_error

    if not user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error_code": "EMAIL_NOT_VERIFIED", "message": "Verify your email before logging in."},
        )

    if user.totp_enabled:
        return {
            "requires_2fa": True,
            "two_fa_session_token": create_access_token(
                {"sub": str(user.id), "scope": "2fa", "type": "2fa"},
                expires_delta=timedelta(minutes=5),
            ),
            "message": "Enter your authenticator code to complete login."
        }

    return await _issue_session(db, user)


@router.post("/login/2fa")
async def login_2fa(payload: TwoFALoginRequest, db: AsyncSession = Depends(get_db)):
    decoded = decode_token(payload.two_fa_session_token)
    if not decoded or decoded.get("type") != "2fa" or decoded.get("scope") != "2fa":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired 2FA session."},
        )

    from uuid import UUID
    try:
        user_id = UUID(decoded.get("sub", ""))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired 2FA session."},
        )

    user = (await db.execute(select(User).where(User.id == user_id, User.is_active == True))).scalar_one_or_none()
    if not user or not user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired 2FA session."},
        )

    totp_row = (await db.execute(select(TOTPSecret).where(TOTPSecret.user_id == user.id))).scalar_one_or_none()
    secret = decrypt_totp_secret(totp_row.secret) if totp_row else None
    if not secret or not pyotp.TOTP(secret).verify(payload.totp_code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOTP", "message": "Invalid authenticator code."},
        )

    return await _issue_session(db, user)


@router.post("/refresh")
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    decoded = decode_token(payload.refresh_token)
    if not decoded or decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired refresh token"}
        )

    token_hash = hash_refresh_token(payload.refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    stored = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)

    if stored and stored.revoked_at is not None:
        await _revoke_all_refresh_tokens(db, stored.user_id)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_REUSE_DETECTED", "message": "Invalid or expired refresh token"},
        )

    if not stored or stored.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired refresh token"}
        )

    stmt = select(User).where(User.id == stored.user_id, User.is_active == True)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "TOKEN_INVALID", "message": "Invalid or expired refresh token"}
        )

    stored.revoked_at = now
    new_refresh = create_refresh_token({"sub": str(user.id)})
    db.add(RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh),
        expires_at=now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    await db.commit()

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": new_refresh,
    }


@router.post("/logout")
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(payload.refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    result = await db.execute(stmt)
    stored = result.scalar_one_or_none()
    if stored and stored.revoked_at is None:
        stored.revoked_at = datetime.now(timezone.utc)
        await db.commit()
    return {"message": "Logged out."}


@router.post("/password-reset/request")
async def password_reset_request(payload: PasswordResetRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == payload.email.lower(), User.is_active == True)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if user:
        raw = secrets.token_urlsafe(32)
        db.add(PasswordResetToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
        ))
        await db.commit()
        # Deliver password reset email (REM-06) - raw token is passed to reset link
        EmailService.send_password_reset_email(user.email, raw)
    return {"message": "If an account exists for that email, a reset link has been sent."}


@router.post("/password-reset/complete")
async def password_reset_complete(payload: PasswordResetComplete, db: AsyncSession = Depends(get_db)):
    token_hash = hash_refresh_token(payload.token)
    stored = (await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )).scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if not stored or stored.used_at is not None or stored.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "TOKEN_INVALID", "message": "Reset token is invalid or expired."},
        )

    user = (await db.execute(select(User).where(User.id == stored.user_id, User.is_active == True))).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "TOKEN_INVALID", "message": "Reset token is invalid or expired."},
        )

    user.password_hash = hash_password(payload.new_password)
    stored.used_at = now
    await _revoke_all_refresh_tokens(db, user.id)
    await db.commit()
    return {"message": "Password updated. Please log in with your new password."}


@router.post("/2fa/enroll")
async def enroll_2fa(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.totp_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "ALREADY_ENABLED", "message": "Two-factor authentication is already enabled."},
        )

    secret = pyotp.random_base32()
    existing = (await db.execute(select(TOTPSecret).where(TOTPSecret.user_id == current_user.id))).scalar_one_or_none()
    if existing:
        existing.secret = encrypt_totp_secret(secret)
        existing.enrolled_at = datetime.now(timezone.utc)
    else:
        db.add(TOTPSecret(user_id=current_user.id, secret=encrypt_totp_secret(secret)))

    codes = [secrets.token_hex(4) for _ in range(8)]
    await db.execute(delete(BackupCode).where(BackupCode.user_id == current_user.id))
    for code in codes:
        db.add(BackupCode(user_id=current_user.id, code_hash=hash_password(code)))
    await db.commit()

    uri = pyotp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="CyberShakti")
    return {
        "secret": secret,
        "qr_code_uri": uri,
        "backup_codes": codes,
        "message": "Save these backup codes securely. They are shown only once.",
    }


@router.post("/2fa/confirm-enrollment")
async def confirm_2fa(payload: TwoFAConfirmRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    totp_row = (await db.execute(select(TOTPSecret).where(TOTPSecret.user_id == current_user.id))).scalar_one_or_none()
    secret = decrypt_totp_secret(totp_row.secret) if totp_row else None
    if not secret or not pyotp.TOTP(secret).verify(payload.totp_code, valid_window=1):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_TOTP", "message": "Invalid authenticator code."},
        )
    current_user.totp_enabled = True
    await db.commit()
    return {"message": "Two-factor authentication is now enabled."}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": str(current_user.id),
        "email": current_user.email,
        "email_verified": current_user.email_verified,
        "totp_enabled": current_user.totp_enabled,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "role": current_user.role
    }


@router.delete("/me")
async def delete_account(
    payload: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if payload.confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": "Confirmation string must match 'DELETE MY ACCOUNT'"}
        )

    if not verify_password(payload.password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_CREDENTIALS", "message": "Incorrect password"}
        )

    current_user.is_active = False
    current_user.deleted_at = datetime.now(timezone.utc)
    current_user.deletion_requested_at = datetime.now(timezone.utc)
    await _revoke_all_refresh_tokens(db, current_user.id)
    await db.commit()

    return {"message": "Account deactivated. PII purge scheduled within 30 days per DPDP retention rules."}
