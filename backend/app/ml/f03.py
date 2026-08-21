"""F-03: OpenCV preprocess + PaddleOCR when available, then F-02 classification."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import numpy as np

from app.ml.f02 import infer_text
from app.shared.explanation_engine import generate_explanation


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    import cv2

    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError("unreadable_image")
    if max(image.shape[:2]) > 1600:
        scale = 1600 / max(image.shape[:2])
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(l)
    enhanced = cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)
    return cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)


def _ocr_paddle(rgb: np.ndarray) -> Tuple[str, str, bool]:
    try:
        from paddleocr import PaddleOCR
    except Exception:
        return "", "failed", False

    try:
        engine = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        result = engine.ocr(rgb, cls=True)
    except Exception:
        return "", "failed", False

    lines = []
    confs = []
    if result:
        for page in result:
            if not page:
                continue
            for item in page:
                if item and len(item) >= 2:
                    text, conf = item[1]
                    if text:
                        lines.append(text)
                        confs.append(float(conf))
    joined = "\n".join(lines).strip()
    if not joined:
        return "", "failed", False
    mean_conf = sum(confs) / len(confs) if confs else 0.0
    if mean_conf >= 0.85:
        quality = "good"
    elif mean_conf >= 0.6:
        quality = "fair"
    else:
        quality = "low"
    return joined, quality, True


def analyze_screenshot(image_bytes: bytes) -> Dict[str, Any]:
    rgb = preprocess_image(image_bytes)
    text, quality, ocr_ok = _ocr_paddle(rgb)
    if not ocr_ok:
        verdict = generate_explanation(
            feature_id="F-03",
            risk_level="low_risk",
            signals=["ocr_unavailable"],
        )
        return {
            "ocr_result": {"text_extracted": "", "ocr_quality": quality, "text_found": False},
            "verdict": verdict,
            "model_note": "PaddleOCR is not available in this runtime (ADR-022 provisional). No simulated OCR text is returned.",
        }
    text_result = infer_text(text)
    text_result["verdict"]["feature_id"] = "F-03"
    return {
        "ocr_result": {"text_extracted": text, "ocr_quality": quality, "text_found": True},
        "verdict": text_result["verdict"],
        "model_note": "OCR → F-02 TF-IDF/LR pipeline.",
        "f02": {"probability": text_result.get("probability"), "model_loaded": text_result.get("model_loaded")},
    }
