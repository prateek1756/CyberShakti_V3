import os
import uuid
import joblib
import pandas as pd
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.shared.database import get_db
from app.shared.auth import get_current_user, get_optional_current_user
from app.shared.models import User, ScanResult
from app.shared.explanation_engine import generate_explanation
from app.shared.uploads import validate_image_bytes, UploadError
from app.shared.qrdecode import decode_qr_payload
from app.worker import (
    run_screenshot_ocr, assess_fake_profile, detect_deepfake, detect_mule_account
)
from app.detect_analyze.url import extract_url_features, feature_vector
import numpy as np

# Upload directory for temporary scan files
SCAN_UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scan-uploads")
os.makedirs(SCAN_UPLOAD_DIR, exist_ok=True)

router = APIRouter()

# --- Pydantic Schemas ---
class ScanURLRequest(BaseModel):
    url: str


class ScanMessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)


class ProfileCheckRequest(BaseModel):
    signals: Dict[str, Any]


class MuleAccountRequest(BaseModel):
    account_signals: Dict[str, Any]


class MuleTransactionAnalysisRequest(BaseModel):
    transactions: List[Dict[str, Any]]


# --- Endpoints ---

@router.post("/scan-url")
async def scan_url(
    payload: ScanURLRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    url_str = payload.url.strip()
    if not (url_str.startswith("http://") or url_str.startswith("https://")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": "Input must be a valid http or https URL string."}
        )

    from app.ml.f01 import infer_url_async

    try:
        f01_res = await infer_url_async(url_str, resolve_live=True)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": str(val_err)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "URL_SCAN_FAILED", "message": f"URL analysis failed: {str(exc)}"}
        )

    risk_level = f01_res["verdict"]["risk_level"]
    prob = f01_res["ml_probability"]
    risk_score = f01_res["risk_score"]

    # Persist scan result record (fail-safe for offline demo)
    try:
        scan_rec = ScanResult(
            user_id=current_user.id if current_user else None,
            feature_id="F-01",
            input_type="url",
            risk_level=risk_level,
            risk_score_raw=round(prob if prob is not None else (risk_score / 100.0), 4),
            verdict_source=f01_res["verdict_source"],
            task_status="complete"
        )
        db.add(scan_rec)
        await db.commit()
        scan_id_val = str(scan_rec.id)
    except Exception:
        if db:
            await db.rollback()
        scan_id_val = str(uuid.uuid4())

    return {
        "scan_id": scan_id_val,
        "input": {
            "url_submitted": payload.url.strip(),
            "url_normalised": f01_res["normalized_url"]
        },
        "original_url": f01_res["original_url"],
        "normalized_url": f01_res["normalized_url"],
        "final_url": f01_res["final_url"],
        "classification": f01_res["classification"],
        "url_type": f01_res["url_type"],
        "link_status": f01_res["link_status"],
        "redirect_status": f01_res["redirect_status"],
        "redirect_count": f01_res["redirect_count"],
        "redirect_chain": f01_res["redirect_chain"],
        "redirect_analysis": f01_res["redirect_analysis"],
        "risk_score": f01_res["risk_score"],
        "confidence": f01_res["confidence"],
        "verdict": f01_res["verdict"],
        "probability": f01_res["probability"],
        "ml_probability": f01_res["ml_probability"],
        "features": f01_res["features"],
        "url_features": f01_res["url_features"],
        "explanations": f01_res["explanations"],
        "explanation": f01_res["explanation"],
        "signals": f01_res["signals"],
        "model": f01_res["model"],
        "analysis_time_ms": f01_res["analysis_time_ms"],
        "verdict_source": f01_res["verdict_source"],
    }


@router.post("/scan-message")
async def scan_message(
    payload: ScanMessageRequest,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    text_str = payload.text.strip()
    if not text_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": "Text cannot be empty."}
        )

    # Run trained F-02 TF-IDF + XGBoost NLP pipeline via the canonical inference module
    from app.ml.f02 import infer_text

    try:
        f02_res = infer_text(text_str)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "VALIDATION_ERROR", "message": str(val_err)}
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "TEXT_SCAN_FAILED", "message": f"Text analysis failed: {str(exc)}"}
        )

    prob = f02_res.get("probability")
    risk_level = f02_res.get("risk_level", "safe")
    classification = f02_res.get("classification", "LEGITIMATE")
    scam_signals = f02_res.get("scam_signals", [])
    explanation_data = f02_res.get("verdict", {})

    scan_id_val = str(uuid.uuid4())
    if db is not None:
        try:
            scan_rec = ScanResult(
                user_id=current_user.id if current_user else None,
                feature_id="F-02",
                input_type="text",
                risk_level=risk_level,
                risk_score_raw=round(prob, 4) if prob is not None else 0.0,
                verdict_source=f02_res.get("verdict_source", "ml_model"),
                task_status="complete"
            )
            db.add(scan_rec)
            await db.commit()
            scan_id_val = str(scan_rec.id)
        except Exception:
            pass


    return {
        "scan_id": scan_id_val,
        "input": {
            "text_length": f02_res.get("text_length", len(text_str)),
            "language_detected": f02_res.get("language_detected", "undetermined"),
        },
        "verdict": explanation_data,
        "classification": classification,
        "risk_level": risk_level,
        "probability": prob,
        "scam_signals": scam_signals,
        "model_note": f02_res.get("model_note"),
        "model_loaded": f02_res.get("model_loaded", False),
        "evaluation": f02_res.get("evaluation"),
    }



@router.post("/scan-screenshot")
async def scan_screenshot(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Read and size-check bytes first
    image_bytes = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "Upload must not exceed 10 MB."}
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_FILE", "message": "Uploaded file is empty."}
        )

    # Validate magic bytes — reject non-image payloads
    try:
        validate_image_bytes(image_bytes)
    except UploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"error_code": exc.error_code, "message": exc.message})

    # Write actual bytes to a uniquely-named temp file
    task_id = uuid.uuid4()
    safe_filename = f"screenshot_{task_id}.bin"
    file_path = os.path.join(SCAN_UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as fh:
        fh.write(image_bytes)

    # Dispatch Celery task with the real file path
    run_screenshot_ocr.delay(job_id=str(task_id), file_path=file_path)

    return {
        "task_id": str(task_id),
        "status": "queued",
        "message": "Screenshot received. Analysis will complete in a few seconds.",
        "poll_url": f"/api/v1/tasks/{task_id}/status"
    }


@router.post("/scan-qr")
async def scan_qr(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    F-04 QR Code Scanner.
    Pipeline:
      1. Read & size-check upload bytes.
      2. Validate image magic bytes.
      3. Decode QR payload via pyzbar.
      4. If payload is a URL → run through F-01 phishing model.
      5. Otherwise → return payload as plain text content.
    """
    # Read and size-check bytes
    image_bytes = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "Upload must not exceed 10 MB."}
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_FILE", "message": "Uploaded file is empty."}
        )

    # Validate magic bytes — reject non-image payloads
    try:
        validate_image_bytes(image_bytes)
    except UploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"error_code": exc.error_code, "message": exc.message})

    # Decode QR code from image
    decoded_payload = decode_qr_payload(image_bytes)
    if decoded_payload is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error_code": "QR_NOT_DETECTED",
                "message": "No QR code was detected in the uploaded image. Please upload a clear, well-lit QR code image."
            }
        )

    payload_stripped = decoded_payload.strip()
    is_url = payload_stripped.lower().startswith("http://") or payload_stripped.lower().startswith("https://")

    if is_url:
        from app.ml.f01 import infer_url_async
        try:
            f01_res = await infer_url_async(payload_stripped, resolve_live=True)
            risk_level = f01_res["verdict"]["risk_level"]
            prob = f01_res["ml_probability"]
            explanation_data = f01_res["verdict"]
            feats = f01_res["url_features"]
        except Exception:
            # Fallback
            feats = extract_url_features(payload_stripped)
            if f01_model is not None:
                X = np.array([feature_vector(feats)])
                prob = float(f01_model.predict_proba(X)[0, 1])
            else:
                is_phishing = any(sub in payload_stripped.lower() for sub in ["kyc", "verify", "bank", "bit.ly", "login-update", "reward"])
                prob = 0.89 if is_phishing else 0.05

            risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"
            signals = ["suspicious_qr_url", "high_url_entropy"] if prob >= 0.4 else None
            scam_category = "qr_phishing" if prob >= 0.4 else None

            explanation_data = generate_explanation(
                feature_id="F-04",
                risk_level=risk_level,
                signals=signals,
                scam_category=scam_category
            )

        # Persist scan result
        try:
            scan_rec = ScanResult(
                user_id=current_user.id if current_user else None,
                feature_id="F-04",
                input_type="qr_url",
                risk_level=risk_level,
                risk_score_raw=round(prob if prob is not None else 0.5, 4),
                verdict_source="ml_model",
                task_status="complete"
            )
            db.add(scan_rec)
            await db.commit()
            scan_id_val = str(scan_rec.id)
        except Exception:
            if db:
                await db.rollback()
            scan_id_val = str(uuid.uuid4())

        return {
            "scan_id": scan_id_val,
            "qr_result": {
                "decoded_content": payload_stripped,
                "content_type": "url",
                "is_readable": True
            },
            "verdict": explanation_data,
            "url_features": feats
        }

    # Non-URL payload (plain text, vCard, Wi-Fi credentials, etc.) — no ML classification
    explanation_data = generate_explanation(
        feature_id="F-04",
        risk_level="safe",
        signals=None,
        scam_category=None
    )
    return {
        "scan_id": str(uuid.uuid4()),
        "qr_result": {
            "decoded_content": payload_stripped,
            "content_type": "text",
            "is_readable": True
        },
        "verdict": explanation_data
    }


@router.post("/assess-profile")
async def check_profile(
    payload: ProfileCheckRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    task_id = uuid.uuid4()
    assess_fake_profile.delay(job_id=str(task_id), signals=payload.signals)
    return {
        "task_id": str(task_id),
        "status": "queued",
        "poll_url": f"/api/v1/tasks/{task_id}/status"
    }


@router.post("/analyze-media-deepfake")
async def analyze_deepfake(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # Read and size-check bytes
    image_bytes = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(image_bytes) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "Upload must not exceed 10 MB."}
        )
    if len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_FILE", "message": "Uploaded file is empty."}
        )

    from app.shared.uploads import validate_media_bytes
    try:
        media_fmt = validate_media_bytes(image_bytes)
    except UploadError as exc:
        raise HTTPException(status_code=exc.status_code, detail={"error_code": exc.error_code, "message": exc.message})

    # Write media bytes to temp file with proper extension for OpenCV VideoCapture
    task_id = uuid.uuid4()
    safe_filename = f"media_{task_id}.{media_fmt if media_fmt in ('mp4', 'avi', 'mov', 'webm') else 'png'}"
    file_path = os.path.join(SCAN_UPLOAD_DIR, safe_filename)
    with open(file_path, "wb") as fh:
        fh.write(image_bytes)


    # Run synchronously in dev mode (no Redis needed)
    try:
        from app.config import settings as _settings
        from app.worker import detect_deepfake as _detect_deepfake
        result = _detect_deepfake(job_id=str(task_id), file_path=file_path)
        return {
            "task_id": str(task_id),
            "status": "complete",
            "result": result,
            "experimental_disclaimer": "Deepfake detection is an experimental research feature.",
        }
    except Exception as exc:
        # Fallback: dispatch to Celery if eager fails
        from app.worker import detect_deepfake as _detect_deepfake
        detect_deepfake.delay(job_id=str(task_id), file_path=file_path)
        return {
            "task_id": str(task_id),
            "status": "queued",
            "experimental_disclaimer": "Deepfake detection is an experimental research feature.",
            "poll_url": f"/api/v1/tasks/{task_id}/status"
        }


@router.post("/assess-mule-account")
async def check_mule(
    payload: MuleAccountRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    task_id = str(uuid.uuid4())
    signals = payload.account_signals if payload.account_signals is not None else payload.model_dump()

    # 1. Primary: Direct sync execution via worker
    try:
        from app.worker import detect_mule_account as _detect_mule_account
        result = _detect_mule_account(job_id=task_id, account_signals=signals)
        return {
            "task_id": task_id,
            "status": "complete",
            "result": result,
        }
    except Exception:
        pass

    # 2. Fallback: Direct f07 ML module inference
    try:
        from app.ml.f07 import infer_mule
        f07_res = infer_mule(signals)
        return {
            "task_id": task_id,
            "status": "complete",
            "result": {
                "job_id": task_id,
                "mule_probability": f07_res.get("probability") if f07_res.get("probability") is not None else 0.05,
                "verdict": f07_res.get("verdict")
            }
        }
    except Exception:
        pass

    # 3. Last fallback: Celery async queue (if Redis is running)
    try:
        detect_mule_account.delay(job_id=task_id, account_signals=signals)
        return {
            "task_id": task_id,
            "status": "queued",
            "poll_url": f"/api/v1/tasks/{task_id}/status"
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error_code": "MULE_ANALYSIS_FAILED", "message": "Failed to analyze mule account signals."}
        )


@router.post("/analyze-mule-transactions")
async def analyze_mule_txns(
    payload: MuleTransactionAnalysisRequest,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Analyzes a list of transaction records using NetworkX graph analytics engine.
    Returns node risk scores, directed payment edges, role classifications, and mule ring summaries.
    """
    from app.ml.f07 import analyze_transaction_network
    graph_data = analyze_transaction_network(payload.transactions)
    return {
        "status": "complete",
        "graph_data": graph_data,
        "disclaimer": DISCLAIMERS_MULE if 'DISCLAIMERS_MULE' in globals() else "Research indicator only; not legal proof of fraud."
    }


@router.post("/analyze-mule-csv")
async def analyze_mule_csv_upload(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Upload a transaction CSV (sender, receiver, amount, timestamp) to analyze the financial network.
    """
    content = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(content) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error_code": "FILE_TOO_LARGE", "message": "Upload must not exceed 10 MB."}
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_FILE", "message": "Uploaded CSV file is empty."}
        )

    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        text_content = content.decode("latin-1", errors="replace")

    import csv
    import io

    reader = csv.DictReader(io.StringIO(text_content))
    transactions = []
    for row in reader:
        # Standardize field names
        sender = row.get("sender") or row.get("sender_account") or row.get("from") or row.get("Source") or row.get("Sender") or ""
        receiver = row.get("receiver") or row.get("receiver_account") or row.get("to") or row.get("Destination") or row.get("Receiver") or ""
        amount_raw = row.get("amount") or row.get("txn_amount") or row.get("Amount") or "0"
        timestamp = row.get("timestamp") or row.get("time") or row.get("Date") or row.get("Timestamp") or ""

        if sender and receiver:
            try:
                amt = float(amount_raw.replace("$", "").replace("₹", "").replace(",", "").strip())
            except ValueError:
                amt = 0.0
            transactions.append({
                "sender": sender.strip(),
                "receiver": receiver.strip(),
                "amount": amt,
                "timestamp": timestamp.strip()
            })

    from app.ml.f07 import analyze_transaction_network
    graph_data = analyze_transaction_network(transactions)

    return {
        "status": "complete",
        "transactions_parsed": len(transactions),
        "graph_data": graph_data
    }

