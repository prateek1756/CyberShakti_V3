import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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

# Lazy-load EfficientNet-B4 once at worker startup (Fix 3 — avoids 71 MB disk read per request)
f06_efficientnet = None
if os.path.exists(F06_EFFICIENTNET_PATH):
    try:
        from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector
        f06_efficientnet = DeepfakeEfficientNetDetector(pretrained=False)
        f06_efficientnet.load_state_dict(
            torch.load(F06_EFFICIENTNET_PATH, weights_only=True)
        )
        f06_efficientnet.eval()
        logger.info("EfficientNet-B4 loaded successfully at worker startup.")
    except Exception as exc:
        logger.warning("Could not load EfficientNet-B4 model: %s", exc)


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
def _preprocess_media_for_efficientnet(file_path: str) -> Tuple[torch.Tensor, int, str]:
    """
    Load image or video from disk and convert to normalised (N,3,224,224) PyTorch tensor.
    For videos, extracts up to 8 evenly-spaced frames.
    Returns: (tensor, frame_count, media_type)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Media file not found: {file_path}")

    from PIL import Image
    import cv2
    import io
    import numpy as np

    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    # First attempt reading as a video via OpenCV VideoCapture
    cap = cv2.VideoCapture(file_path)
    frames_list = []
    is_video = False

    if cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames > 1:
            is_video = True
            # Sample up to 8 frames evenly across the video
            sample_count = min(8, max(1, total_frames))
            indices = np.linspace(0, total_frames - 1, sample_count, dtype=int)
            for idx in indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
                ret, frame = cap.read()
                if ret and frame is not None:
                    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(rgb).resize((224, 224), Image.BILINEAR)
                    arr = (np.array(img, dtype=np.float32) / 255.0 - mean) / std
                    frames_list.append(arr.transpose(2, 0, 1))
        cap.release()

    # If not a video or no video frames read, decode as image
    if not frames_list:
        with open(file_path, "rb") as fh:
            raw = fh.read()
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as exc:
            raise ValueError(f"Cannot decode media file {file_path}: {exc}") from exc

        img = img.resize((224, 224), Image.BILINEAR)
        arr = (np.array(img, dtype=np.float32) / 255.0 - mean) / std
        frames_list.append(arr.transpose(2, 0, 1))

    # Stack frames into tensor: (N, 3, 224, 224)
    tensor = torch.from_numpy(np.stack(frames_list, axis=0))
    media_type = "video" if is_video else "image"
    return tensor, len(frames_list), media_type



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

    # Load and preprocess media (image or video)
    try:
        tensor, frame_count, media_type = _preprocess_media_for_efficientnet(file_path)
    except FileNotFoundError as exc:
        logger.error("F-06: %s", exc)
        return {
            "job_id": job_id,
            "error": "FILE_NOT_FOUND",
            "message": str(exc),
            "verdict": {"risk_level": "error"}
        }
    except ValueError as exc:
        logger.warning("F-06: invalid media: %s", exc)
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

    # Use module-level lazy-loaded model (Fix 3)
    model = f06_efficientnet
    if model is None:
        # Model was not loaded at startup — attempt a one-shot load as fallback
        try:
            from ml.pipelines.train_f06_efficientnet import DeepfakeEfficientNetDetector
            model = DeepfakeEfficientNetDetector(pretrained=False)
            if os.path.exists(F06_EFFICIENTNET_PATH):
                model.load_state_dict(torch.load(F06_EFFICIENTNET_PATH, weights_only=True))
            model.eval()
        except Exception as exc:
            logger.error("F-06: model unavailable: %s", exc)
            return {
                "job_id": job_id,
                "error": "MODEL_UNAVAILABLE",
                "message": "Deepfake model could not be loaded.",
                "verdict": {"risk_level": "error"}
            }

    model.eval()

    with torch.no_grad():
        outputs = model(tensor)
        # label 0 = fake; anomaly score = prob_fake across all sampled frames
        probs = torch.softmax(outputs, dim=1)[:, 0]
        prob = float(torch.mean(probs))  # average anomaly across sampled video frames

    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"

    # Gate signals on probability — do not emit high-risk signals for safe results (Fix 5)
    signals = ["cnn_facial_anomaly_detected", "efficientnet_b4_feature_noise"] if prob >= 0.4 else []
    if media_type == "video":
        signals.append(f"video_analyzed_{frame_count}_frames")

    explanation_data = generate_explanation(
        feature_id="F-06",
        risk_level=risk_level,
        signals=signals or None,
        is_experimental=True
    )

    return {
        "job_id": job_id,
        "media_analysis": {
            "faces_detected": 1,
            "architecture": "EfficientNet-B4 (PyTorch)",
            "media_type": media_type,
            "frames_analyzed": frame_count,
            "anomaly_score": round(prob, 4)
        },
        "verdict": explanation_data
    }



@celery_app.task(name="tasks.detect_mule_account")
def detect_mule_account(job_id: str, account_signals: Dict[str, Any]) -> Dict[str, Any]:
    """Celery task executing graph-aware mule account classification using trained F-07 model."""
    if not isinstance(account_signals, dict):
        account_signals = {}
    txn_velocity = 1 if account_signals.get('transaction_velocity_high') else 0
    mult_recip = 1 if account_signals.get('multiple_recipients') else 0
    round_amt = 1 if account_signals.get('round_amount_transfers') else 0
    pass_thru = 1 if account_signals.get('pass_through') else 0
    age_cat = int(account_signals.get('account_age_category', 0))

    # Graph properties derived dynamically from user inputs if not explicitly supplied
    in_deg = account_signals.get('graph_in_degree')
    if in_deg is None:
        in_deg = 15 if (mult_recip or pass_thru) else 2

    out_deg = account_signals.get('graph_out_degree')
    if out_deg is None:
        out_deg = 18 if (mult_recip or pass_thru) else 2

    btw = account_signals.get('graph_betweenness_centrality')
    if btw is None:
        btw = 0.45 if (pass_thru and txn_velocity) else 0.02

    clust = account_signals.get('graph_clustering_coefficient')
    if clust is None:
        clust = 0.12 if pass_thru else 0.65

    feature_dict = {
        'account_age_category': age_cat,
        'transaction_velocity_high': txn_velocity,
        'multiple_recipients': mult_recip,
        'round_amount_transfers': round_amt,
        'account_used_for_receiving_then_forwarding': pass_thru,
        'graph_in_degree': in_deg,
        'graph_out_degree': out_deg,
        'graph_betweenness_centrality': btw,
        'graph_clustering_coefficient': clust
    }

    if f07_model is not None:
        df_feat = pd.DataFrame([feature_dict])
        prob = float(f07_model.predict_proba(df_feat)[0, 1])
    else:
        # Fallback heuristic calculation if model not present
        score = 0.05
        if pass_thru: score += 0.35
        if txn_velocity: score += 0.25
        if mult_recip: score += 0.20
        if age_cat == 0: score += 0.15
        prob = min(0.98, max(0.02, score))

    risk_level = "high_risk" if prob >= 0.7 else "moderate_risk" if prob >= 0.4 else "safe"

    # Derive signals from actual feature values rather than hardcoding them (Fix 5)
    signal_map = {
        "transaction_velocity_high": "high_transaction_velocity",
        "account_used_for_receiving_then_forwarding": "pass_through_pattern",
        "multiple_recipients": "multiple_recipients_detected",
        "round_amount_transfers": "round_amount_pattern",
    }
    signals = [label for key, label in signal_map.items() if feature_dict.get(key) == 1]

    explanation_data = generate_explanation(
        feature_id="F-07",
        risk_level=risk_level,
        signals=signals or None,
        is_experimental=True
    )

    return {
        "job_id": job_id,
        "mule_probability": round(prob, 4),
        "verdict": explanation_data
    }
