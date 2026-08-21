"""F-02 scam text: TF-IDF + Logistic Regression baseline (ADR-009). DistilBERT is not loaded unless artefact exists."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Optional

from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

_bundle = None
_metrics: Optional[dict] = None
_loaded = False

SCAM_KEYWORDS = ("otp", "kyc", "blocked", "lottery", "winner", "prize", "urgent", "verify", "account")


def preprocess_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    normalized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:5000]


def _ensure_loaded() -> None:
    global _bundle, _metrics, _loaded
    if _loaded:
        return
    _bundle = load_joblib("f02_scam_text_pipeline.joblib")
    _metrics = load_json("f02_metrics.json")
    _loaded = True


def infer_text(text: str) -> Dict[str, Any]:
    cleaned = preprocess_text(text)
    if not cleaned:
        raise ValueError("empty_text")
    _ensure_loaded()
    keywords = [k for k in SCAM_KEYWORDS if k in cleaned.lower()]
    if _bundle is not None:
        # Support both Pipeline objects (sklearn) and legacy {"vectorizer":..., "model":...} dicts
        from sklearn.pipeline import Pipeline as _Pipeline
        if isinstance(_bundle, _Pipeline):
            X = _bundle[:-1].transform([cleaned])  # all steps except the classifier
            prob = float(_bundle[-1].predict_proba(X)[0][1])
        else:
            vectorizer = _bundle["vectorizer"]
            clf = _bundle["model"]
            X = vectorizer.transform([cleaned])
            prob = float(clf.predict_proba(X)[0][1])
        is_scam = prob >= 0.5
        source = "ml_model"
        note = "TF-IDF + Logistic Regression baseline (ADR-009). DistilBERT fine-tune artefact is not loaded."
        model_loaded = True
    else:
        is_scam = bool(keywords)
        prob = None
        source = "heuristic"
        note = "Trained F-02 artefact not loaded; keyword fallback in use."
        model_loaded = False

    risk_level = "high_risk" if is_scam else "safe"
    verdict = generate_explanation(
        feature_id="F-02",
        risk_level=risk_level,
        signals=keywords or None,
        scam_category="otp_theft" if "otp" in keywords else ("kyc_scam" if "kyc" in keywords else None),
    )
    return {
        "verdict": verdict,
        "probability": prob,
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "language_detected": "undetermined",
        "scam_indicators": keywords,
        "evaluation": _metrics,
        "text_length": len(cleaned),
    }
