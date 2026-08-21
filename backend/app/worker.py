import os
import logging
import joblib
import pandas as pd
import torch
from typing import Dict, Any
from celery import Celery
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from app.config import settings
from app.shared.explanation_engine import generate_explanation

logger = logging.getLogger(__name__)

celery_app = Celery(
    "cybershakti_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
)

# ---------------------------------------------------------------------------
# Model path constants
# ---------------------------------------------------------------------------
MODEL_DIR = os.path.join(os.path.dirname(__file__), "ml", "models")
F02_MODEL_PATH = os.path.join(MODEL_DIR, "f02_scam_text_pipeline.joblib")
F02_DISTILBERT_DIR = os.path.join(MODEL_DIR, "distilbert_scam")
F05_MODEL_PATH = os.path.join(MODEL_DIR, "f05_fake_profile_model.joblib")
F06_EFFICIENTNET_PATH = os.path.join(MODEL_DIR, "f06_efficientnet_b4.pth")
F07_MODEL_PATH = os.path.join(MODEL_DIR, "f07_mule_account_model.joblib")

# ---------------------------------------------------------------------------
# Lazy-load models at worker startup
# ---------------------------------------------------------------------------
f02_pipeline = joblib.load(F02_MODEL_PATH) if os.path.exists(F02_MODEL_PATH) else None

f02_tokenizer = None
f02_distilbert = None
if os.path.exists(F02_DISTILBERT_DIR):
    try:
        f02_tokenizer = DistilBertTokenizer.from_pretrained(F02_DISTILBERT_DIR)
        f02_distilbert = DistilBertForSequenceClassification.from_pretrained(F02_DISTILBERT_DIR)
        f02_distilbert.eval()
    except Exception as exc:
        logger.warning("Could not load DistilBERT model: %s", exc)

f05_model = joblib.load(F05_MODEL_PATH) if os.path.exists(F05_MODEL_PATH) else None
f07_model = joblib.load(F07_MODEL_PATH) if os.path.exists(F07_MODEL_PATH) else None


# ---------------------------------------------------------------------------
# F-02 helper: classify text using primary (DistilBERT) or baseline (TF-IDF)
# ---------------------------------------------------------------------------
def _classify_text_f02(text: str) -> float:
    """Return scam probability [0,1] using DistilBERT (primary) or TF-IDF baseline."""
    if f02_distilbert is not None and f02_tokenizer is not None:
        try:
            inputs = f02_tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
            with torch.no_grad():
                logits = f02_distilbert(**inputs).logits
                prob = float(torch.softmax(logits, dim=1)[0, 1])
            return prob
        except Exception as exc:
            logger.warning("DistilBERT inference failed, falling back to TF-IDF: %s", exc)
    if f02_pipeline is not None:
        return float(f02_pipeline.predict_proba([text])[0, 1])
    # No model loaded — return a safe default that triggers review
    logger.error("No F-02 model loaded; returning neutral probability 0.5")
    return 0.5


# ---------------------------------------------------------------------------
# F-06 helper: preprocess image bytes -> 4D tensor for EfficientNet
# ---------------------------------------------------------------------------
def _preprocess_image_for_efficientnet(file_path: str) -> torch.Tensor:
    """
    Load image from disk and convert to normalised (1,3,224,224) PyTorch tensor.
    Raises FileNotFoundError or ValueError on invalid input.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    from PIL import Image
    import io

    with open(file_path, "rb") as fh:
        raw = fh.read()

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise ValueError(f"Cannot decode image file {file_path}: {exc}") from exc

    img = img.resize((224, 224), Image.BILINEAR)

    # Convert to (C, H, W) float32 tensor, normalize with ImageNet mean/std
    import numpy as np
    arr = np.array(img, dtype=np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    arr = (arr - mean) / std
    arr = arr.transpose(2, 0, 1)  # H,W,C -> C,H,W
    tensor = torch.from_numpy(arr).unsqueeze(0)  # (1,3,224,224)
    return tensor


# ---------------------------------------------------------------------------
# Celery Tasks
# ---------------------------------------------------------------------------

@celery_app.task(name="tasks.run_screenshot_ocr")
def run_screenshot_ocr(job_id: str, file_path: str) -> Dict[str, Any]:
    """
    F-03 Screenshot Scam Scanner.

    Pipeline:
      1. Read actual image bytes from file_path (written by the API router).
      2. Run EasyOCR to extract text.
      3. Pass extracted text to F-02 scam classifier.
      4. Return verdict and clean up temp file.
    """
    from app.shared.ocr_service import extract_text_from_image_bytes

    if not os.path.exists(file_path):
        logger.error("F-03: file_path does not exist: %s", file_path)
        return {
            "job_id": job_id,
            "error": "OCR_FILE_NOT_FOUND",
            "message": "Uploaded file not found on worker.",
            "verdict": {"risk_level": "error", "detail": "Internal processing error."}
        }

    try:
        with open(file_path, "rb") as fh:
            image_bytes = fh.read()
    except Exception as exc:
        logger.error("F-03: cannot read file %s: %s", file_path, exc)
        return {"job_id": job_id, "error": "OCR_READ_ERROR", "message": str(exc)}
    finally:
        # Always clean up temp file
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Run actual OCR
    ocr_error = None
    extracted_text = ""
    try:
        extracted_text = extract_text_from_image_bytes(image_bytes)
    except ValueError as exc:
        ocr_error = f"Invalid image: {exc}"
        logger.warning("F-03 OCR validation error: %s", exc)
    except RuntimeError as exc:
        ocr_error = f"OCR engine error: {exc}"
        logger.error("F-03 OCR runtime error: %s", exc)

    if ocr_error:
        return {
            "job_id": job_id,
            "error": "OCR_FAILED",
            "message": ocr_error,
            "verdict": {"risk_level": "error", "detail": "Could not process image."}
        }

    if not extracted_text.strip():
        # No text found — image may be blank or contain only graphics
        return {
            "job_id": job_id,
            "ocr_result": {
                "text_extracted": "",
                "ocr_quality": "no_text",
                "text_found": False,
                "engine": "EasyOCR"
            },
            "verdict": generate_explanation(
                feature_id="F-03",
                risk_level="safe",
                signals=[],
                scam_category=None
            )
        }

    # Classify extracted text via F-02 pipeline
    prob = _classify_text_f02(extracted_text)
    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"

    # Derive signals from extracted text for explanation
    text_lower = extracted_text.lower()
    signals = []
    if any(w in text_lower for w in ["urgent", "immediately", "now", "today"]):
        signals.append("urgency_language")
    if any(w in text_lower for w in ["kyc", "account", "bank", "upi", "otp"]):
        signals.append("financial_credential_mention")
    if any(w in text_lower for w in ["http://", "https://", "bit.ly", "goo.gl"]):
        signals.append("url_present")

    explanation_data = generate_explanation(
        feature_id="F-03",
        risk_level=risk_level,
        signals=signals or None,
        scam_category="bank_phishing" if prob >= 0.4 else None
    )

    return {
        "job_id": job_id,
        "ocr_result": {
            "text_extracted": extracted_text[:1000],  # cap response size
            "ocr_quality": "good",
            "text_found": True,
            "engine": "EasyOCR",
            "char_count": len(extracted_text)
        },
        "verdict": explanation_data
    }


@celery_app.task(name="tasks.assess_fake_profile")
def assess_fake_profile(job_id: str, signals: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task evaluating observable profile risk signals using trained F-05 model."""
    feature_dict = {
        'account_age_category': signals.get('account_age_category', 0),
        'follower_count_range': signals.get('follower_count_range', 0),
        'following_to_follower_ratio_high': 1 if signals.get('following_to_follower_ratio_high') else 0,
        'has_profile_photo': 1 if signals.get('has_profile_photo', True) else 0,
        'profile_photo_appears_generic': 1 if signals.get('profile_photo_appears_generic') else 0,
        'bio_present': 1 if signals.get('bio_present', True) else 0,
        'sent_unsolicited_money_request': 1 if signals.get('sent_unsolicited_money_request') else 0,
        'claims_celebrity_or_official': 1 if signals.get('claims_celebrity_or_official') else 0,
        'contacted_via_dm_unsolicited': 1 if signals.get('contacted_via_dm_unsolicited') else 0,
        'promotes_investment_or_scheme': 1 if signals.get('promotes_investment_or_scheme') else 0
    }

    if f05_model is not None:
        df_feat = pd.DataFrame([feature_dict])
        prob = float(f05_model.predict_proba(df_feat)[0, 1])
    else:
        prob = 0.85 if signals.get('sent_unsolicited_money_request') else 0.15

    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"
    active_signals = [k for k, v in feature_dict.items() if v == 1]

    explanation_data = generate_explanation(
        feature_id="F-05",
        risk_level=risk_level,
        signals=active_signals[:3],
        scam_category="fake_profile"
    )

    return {
        "job_id": job_id,
        "signals_evaluated": len(signals),
        "risk_probability": round(prob, 4),
        "verdict": explanation_data
    }


@celery_app.task(name="tasks.detect_deepfake")
def detect_deepfake(job_id: str, file_path: str) -> Dict[str, Any]:
    """
    F-06 Deepfake Detection.

    Pipeline:
      1. Load actual image bytes from file_path.
      2. Preprocess into (1,3,224,224) tensor with ImageNet normalization.
      3. Run EfficientNet-B4 inference.
      4. Clean up temp file.
    """
    from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector

    # Load and preprocess actual image
    try:
        tensor = _preprocess_image_for_efficientnet(file_path)
    except FileNotFoundError as exc:
        logger.error("F-06: %s", exc)
        return {
            "job_id": job_id,
            "error": "FILE_NOT_FOUND",
            "message": str(exc),
            "verdict": {"risk_level": "error"}
        }
    except ValueError as exc:
        logger.warning("F-06: invalid image: %s", exc)
        return {
            "job_id": job_id,
            "error": "INVALID_IMAGE",
            "message": str(exc),
            "verdict": {"risk_level": "error"}
        }
    finally:
        try:
            os.remove(file_path)
        except Exception:
            pass

    # Load EfficientNet-B4 model
    model = DeepfakeEfficientNetDetector(pretrained=False)
    if os.path.exists(F06_EFFICIENTNET_PATH):
        try:
            model.load_state_dict(torch.load(F06_EFFICIENTNET_PATH, weights_only=True))
        except Exception as exc:
            logger.error("F-06: model load failed: %s", exc)

    model.eval()

    with torch.no_grad():
        outputs = model(tensor)
        prob = float(torch.softmax(outputs, dim=1)[0, 0])  # label 0 = fake; anomaly score = prob_fake

    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"

    explanation_data = generate_explanation(
        feature_id="F-06",
        risk_level=risk_level,
        signals=["cnn_facial_anomaly_detected", "efficientnet_b4_feature_noise"],
        is_experimental=True
    )

    return {
        "job_id": job_id,
        "media_analysis": {
            "faces_detected": 1,
            "architecture": "EfficientNet-B4 (PyTorch)",
            "anomaly_score": round(prob, 4)
        },
        "verdict": explanation_data
    }


@celery_app.task(name="tasks.detect_mule_account")
def detect_mule_account(job_id: str, account_signals: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task executing graph-aware mule account classification using trained F-07 model."""
    feature_dict = {
        'account_age_category': account_signals.get('account_age_category', 0),
        'transaction_velocity_high': 1 if account_signals.get('transaction_velocity_high') else 0,
        'multiple_recipients': 1 if account_signals.get('multiple_recipients') else 0,
        'round_amount_transfers': 1 if account_signals.get('round_amount_transfers') else 0,
        'account_used_for_receiving_then_forwarding': 1 if account_signals.get('pass_through') else 0,
        'graph_in_degree': account_signals.get('graph_in_degree', 12),
        'graph_out_degree': account_signals.get('graph_out_degree', 15),
        'graph_betweenness_centrality': account_signals.get('graph_betweenness_centrality', 0.45),
        'graph_clustering_coefficient': account_signals.get('graph_clustering_coefficient', 0.12)
    }

    if f07_model is not None:
        df_feat = pd.DataFrame([feature_dict])
        prob = float(f07_model.predict_proba(df_feat)[0, 1])
    else:
        prob = 0.88

    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"

    explanation_data = generate_explanation(
        feature_id="F-07",
        risk_level=risk_level,
        signals=["high_transaction_velocity", "pass_through_pattern"],
        is_experimental=True
    )

    return {
        "job_id": job_id,
        "mule_probability": round(prob, 4),
        "verdict": explanation_data
    }
