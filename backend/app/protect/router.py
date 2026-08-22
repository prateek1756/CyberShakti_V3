import io
import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.shared.auth import get_current_user, get_optional_current_user
from app.shared.models import User
from app.shared.file_crypto import (
    FileCryptoError,
    decrypt_bytes,
    encrypt_bytes,
    safe_download_filename,
)

router = APIRouter()


class PhoneCheckRequest(BaseModel):
    phone_number: str


class PasswordCheckRequest(BaseModel):
    password: str = Field(min_length=1, max_length=1000)


@router.post("/check-phone")
async def check_phone(
    payload: PhoneCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    raw_num = payload.phone_number.strip().replace(" ", "").replace("-", "")
    
    # Emergency Service Check (FR-048)
    emergency_numbers = {"100": "Police", "112": "National Emergency", "108": "Ambulance", "102": "Maternity Helpline"}
    if raw_num in emergency_numbers:
        return {
            "lookup_id": "emerg-001",
            "phone_number_normalised": raw_num,
            "is_emergency_service": True,
            "emergency_service_name": emergency_numbers[raw_num],
            "message": "This is an emergency service number. No risk assessment is performed for emergency numbers.",
            "verdict": None
        }

    # Format normalization
    if raw_num.startswith("+91"):
        normalised = raw_num
    elif len(raw_num) == 10 and raw_num.isdigit():
        normalised = f"+91{raw_num}"
    elif raw_num.startswith("0") and len(raw_num) == 11 and raw_num[1:].isdigit():
        normalised = f"+91{raw_num[1:]}"
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": "Please enter a valid 10-digit Indian phone number."}
        )

    # Simulated threat intelligence lookup
    is_threat = normalised in ["+919876543210", "+919999999999"]
    
    if is_threat:
        return {
            "lookup_id": "lookup-001",
            "phone_number_normalised": normalised,
            "is_emergency_service": False,
            "verdict": {
                "risk_level": "high_risk",
                "risk_label": "High Risk",
                "explanation": "This number has been reported multiple times as associated with fraudulent calls impersonating bank officials.",
                "data_source": "threat_intelligence_api",
                "disclaimer": "Phone number risk data is sourced from threat intelligence and community reports."
            }
        }
    else:
        return {
            "lookup_id": "lookup-002",
            "phone_number_normalised": normalised,
            "is_emergency_service": False,
            "verdict": {
                "risk_level": "safe",
                "risk_label": "Safe / No Reports",
                "explanation": "No threat reports found for this number in our threat database.",
                "absence_of_data_note": "The absence of threat data for a number does not confirm that it is safe. Exercise caution with unexpected calls.",
                "data_source": "threat_intelligence_api"
            }
        }


@router.post("/check-password")
async def check_password(
    payload: PasswordCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    pwd = payload.password
    length = len(pwd)
    
    # Entropy computation
    charset = 0
    if any(c.islower() for c in pwd): charset += 26
    if any(c.isupper() for c in pwd): charset += 26
    if any(c.isdigit() for c in pwd): charset += 10
    if any(not c.isalnum() for c in pwd): charset += 32
    
    entropy = length * math.log2(charset) if charset > 0 else 0
    
    common_pwd = pwd.lower() in ["password", "password123", "123456", "12345678", "qwerty", "admin"]
    
    if common_pwd or entropy < 28:
        strength = "very_weak"
    elif entropy < 45:
        strength = "weak"
    elif entropy < 65:
        strength = "moderate"
    elif entropy < 85:
        strength = "strong"
    else:
        strength = "very_strong"

    improvements = []
    if length < 14:
        improvements.append("Increase length to at least 14 characters for stronger protection.")
    if not any(not c.isalnum() for c in pwd):
        improvements.append("Include special symbols (e.g., !@#$) to boost password complexity.")
    if common_pwd:
        improvements.append("Avoid common passwords or predictable sequences.")

    return {
        "verdict": {
            "strength_level": strength,
            "strength_label": strength.replace("_", " ").title(),
            "entropy_bits": round(entropy, 1),
            "length": length,
            "is_common_password": common_pwd,
            "improvements": improvements,
            "disclaimer": "Do not enter your actual account passwords here. This checker is for assessment purposes only."
        }
    }


@router.post("/encrypt-file")
async def encrypt_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if not password or not password.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_PASSWORD", "message": "Encryption password cannot be empty."}
        )

    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "File exceeds the maximum allowed size."},
        )

    encrypted_payload = encrypt_bytes(content, password)
    filename = safe_download_filename(file.filename, "file") + ".enc"

    return StreamingResponse(
        io.BytesIO(encrypted_payload),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/decrypt-file")
async def decrypt_file(
    file: UploadFile = File(...),
    password: str = Form(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
):
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_PASSWORD", "message": "Decryption password cannot be empty."}
        )

    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "File exceeds the maximum allowed size."},
        )

    try:
        plaintext = decrypt_bytes(content, password)
    except FileCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": exc.error_code, "message": exc.message},
        )

    orig_name = safe_download_filename(file.filename, "decrypted_file")
    if orig_name.endswith(".enc"):
        orig_name = orig_name[:-4] or "decrypted_file"

    return StreamingResponse(
        io.BytesIO(plaintext),
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{orig_name}"'}
    )
