"""
F-02 Scam Text / Email Body Detection
TF-IDF (trigram, 80k vocab) + XGBoost — trained on 31,207 real SMS/email messages
from 6 datasets covering smishing, phishing, spam, fraud email, and financial scams.

Three-tier verdict:
  - LEGITIMATE  : prob < 0.40
  - SUSPICIOUS  : 0.40 <= prob < 0.72
  - FRAUD/SCAM  : prob >= 0.72

Model performance (held-out test, 3,121 samples):
  Accuracy: 97.92%  |  ROC-AUC: 0.9987  |  FPR: 0.78%  |  FNR: 3.34%
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, Optional

from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

_bundle = None
_metrics: Optional[dict] = None
_loaded = False

# Confirmed hard-rule scam indicators
HARD_SCAM_SIGNALS = {
    "kyc": "kyc_scam",
    "lottery": "lottery_scam",
    "winner": "prize_scam",
    "prize money": "prize_scam",
    "processing fee": "advance_fee_fraud",
    "click to verify": "credential_phishing",
    "account suspended": "account_freeze_scam",
    "send otp": "otp_theft",
    "share otp": "otp_theft",
    "whatsapp earn": "work_from_home_scam",
    "earn per day": "work_from_home_scam",
    "bitcoin investment": "crypto_fraud",
    "guaranteed returns": "investment_fraud",
}

# Trusted legitimate contexts (reduce false positives)
LEGIT_CONTEXTS = (
    "official app",
    "official website",
    "bluedart.com",
    "flipkart.com",
    "amazon.in",
    "airtel thanks",
    "do not share",
    "we will never ask",
    "irctc.co.in",
    "incometax.gov.in",
    "uidai.gov.in",
)


def preprocess_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", str(text or ""))
    normalized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized[:10000]


def _ensure_loaded() -> None:
    global _bundle, _metrics, _loaded
    if _loaded:
        return
    _bundle = load_joblib("f02_scam_text_pipeline.joblib")
    _metrics = load_json("f02_metrics.json")
    _loaded = True


def _get_ml_prob(cleaned: str) -> Optional[float]:
    """Returns XGBoost probability of fraud/scam (0.0–1.0), or None if model unavailable."""
    if _bundle is None:
        return None
    from sklearn.pipeline import Pipeline as _Pipeline
    if isinstance(_bundle, _Pipeline):
        X = _bundle[:-1].transform([cleaned])
        return float(_bundle[-1].predict_proba(X)[0][1])
    # Legacy dict bundle
    X = _bundle["vectorizer"].transform([cleaned])
    return float(_bundle["model"].predict_proba(X)[0][1])


def infer_text(text: str) -> Dict[str, Any]:
    """
    Runs the full F-02 Scam Text Detection pipeline on a message/email body.

    Returns a dict with:
      - verdict: standard CyberShakti verdict dict
      - probability: float [0.0, 1.0] — scam probability from XGBoost
      - classification: 'LEGITIMATE' | 'SUSPICIOUS' | 'FRAUD_SCAM'
      - scam_signals: list of detected hard-rule signals
      - verdict_source: 'ml_model' | 'heuristic'
      - model_loaded: bool
      - evaluation: model metrics dict
    """
    cleaned = preprocess_text(text)
    if not cleaned:
        raise ValueError("empty_text")

    _ensure_loaded()

    lower = cleaned.lower()

    # Hard-rule signal detection (exact phrase matching)
    scam_signals = [signal for phrase, signal in HARD_SCAM_SIGNALS.items() if phrase in lower]

    # Legit context detection (reduce FP for transactional messages)
    has_legit_context = any(ctx in lower for ctx in LEGIT_CONTEXTS)

    prob = _get_ml_prob(cleaned)

    if prob is not None:
        # Adjust threshold upward if trusted context present (reduce FP)
        scam_threshold = 0.82 if has_legit_context else 0.72
        suspicious_threshold = 0.50 if has_legit_context else 0.40

        # Hard-rule override: confirmed scam phrase + high prob
        if scam_signals and prob >= 0.55:
            scam_threshold = 0.55  # lower bar when phrase match confirms

        if prob >= scam_threshold:
            classification = "FRAUD_SCAM"
            risk_level = "high_risk"
        elif prob >= suspicious_threshold:
            classification = "SUSPICIOUS"
            risk_level = "moderate_risk"
        else:
            classification = "LEGITIMATE"
            risk_level = "safe"

        source = "ml_model"
        note = "TF-IDF (trigram 80k) + XGBoost v2 trained on 31,207 real SMS/email messages — 97.92% accuracy, 0.9987 ROC-AUC."
        model_loaded = True
    else:
        # Heuristic fallback
        if scam_signals:
            classification = "FRAUD_SCAM"
            risk_level = "high_risk"
        else:
            classification = "LEGITIMATE"
            risk_level = "safe"
        prob = None
        source = "heuristic"
        note = "Trained F-02 artefact not loaded; hard-rule heuristic fallback in use."
        model_loaded = False

    # Determine primary scam category for explanation
    primary_category = scam_signals[0] if scam_signals else None
    if not primary_category and prob is not None and prob >= 0.72:
        primary_category = "generic_scam"

    verdict = generate_explanation(
        feature_id="F-02",
        risk_level=risk_level,
        signals=scam_signals or None,
        scam_category=primary_category,
    )

    return {
        "verdict": verdict,
        "probability": prob,
        "classification": classification,
        "risk_level": risk_level,
        "scam_signals": scam_signals,
        "has_legit_context": has_legit_context,
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "language_detected": "undetermined",
        "evaluation": _metrics,
        "text_length": len(cleaned),
    }
