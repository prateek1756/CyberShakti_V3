"""F-05 fake-profile signal encoding and XGBoost inference (synthetic-label artefact only)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

DISCLAIMER = (
    "CyberShakti does not verify identities. This assessment evaluates observable risk signals only "
    "and does not confirm whether a profile is genuinely fake or who the account belongs to. "
    "A low-risk result does not mean the profile is genuine."
)

AGE_MAP = {"unknown": 0, "days": 1, "weeks": 2, "months": 3, "years": 4}
FOLLOWER_MAP = {"unknown": 0, "none": 1, "low": 2, "medium": 3, "high": 4}
POSTS_MAP = {"unknown": 0, "none": 1, "few": 2, "some": 3, "many": 4}
PLATFORM_MAP = {"unknown": 0, "instagram": 1, "facebook": 2, "twitter": 3, "whatsapp": 4, "other": 5}

FEATURE_ORDER = [
    "account_age_category",
    "follower_count_range",
    "following_to_follower_ratio_high",
    "has_profile_photo",
    "profile_photo_appears_generic",
    "bio_present",
    "posts_count_range",
    "sent_unsolicited_money_request",
    "claims_celebrity_or_official",
    "platform",
    "contacted_via_dm_unsolicited",
    "promotes_investment_or_scheme",
]

_model = None
_metrics: Optional[dict] = None
_loaded = False


def encode_signals(signals: Dict[str, Any]) -> List[float]:
    return [
        float(AGE_MAP.get(str(signals.get("account_age_category") or "unknown").lower(), 0)),
        float(FOLLOWER_MAP.get(str(signals.get("follower_count_range") or "unknown").lower(), 0)),
        float(bool(signals.get("following_to_follower_ratio_high"))),
        float(bool(signals.get("has_profile_photo"))),
        float(bool(signals.get("profile_photo_appears_generic"))),
        float(bool(signals.get("bio_present"))),
        float(POSTS_MAP.get(str(signals.get("posts_count_range") or "unknown").lower(), 0)),
        float(bool(signals.get("sent_unsolicited_money_request"))),
        float(bool(signals.get("claims_celebrity_or_official"))),
        float(PLATFORM_MAP.get(str(signals.get("platform") or "unknown").lower(), 0)),
        float(bool(signals.get("contacted_via_dm_unsolicited"))),
        float(bool(signals.get("promotes_investment_or_scheme"))),
    ]


def _ensure_loaded() -> None:
    global _model, _metrics, _loaded
    if _loaded:
        return
    _model = load_joblib("f05_fake_profile_model.joblib")
    _metrics = load_json("f05_metrics.json")
    _loaded = True


def infer_profile(signals: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(signals, dict) or not signals:
        raise ValueError("empty_signals")
    _ensure_loaded()
    vector = encode_signals(signals)
    active = [name for name in FEATURE_ORDER if signals.get(name) not in (None, False, "", "unknown")]
    if _model is not None:
        import numpy as np

        prob = float(_model.predict_proba(np.array([vector]))[0][1])
        if prob >= 0.7:
            risk = "high_risk"
        elif prob >= 0.45:
            risk = "moderate_risk"
        else:
            risk = "low_risk"
        source = "ml_model"
        note = "XGBoost trained on synthetic labels derived from documented F-05 indicators. Not an academic fake-account corpus."
        model_loaded = True
    else:
        flags = [
            name
            for name in (
                "sent_unsolicited_money_request",
                "claims_celebrity_or_official",
                "promotes_investment_or_scheme",
                "profile_photo_appears_generic",
                "following_to_follower_ratio_high",
                "contacted_via_dm_unsolicited",
            )
            if signals.get(name)
        ]
        risk = "high_risk" if len(flags) >= 2 else "moderate_risk" if flags else "low_risk"
        prob = None
        source = "heuristic"
        note = "Trained F-05 artefact not loaded."
        model_loaded = False
        active = flags

    verdict = generate_explanation(
        feature_id="F-05",
        risk_level=risk,
        signals=active[:5] or None,
        scam_category="fake_profile",
    )
    return {
        "verdict": verdict,
        "probability": prob,
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "signals_evaluated": len(signals),
        "identity_verification_disclaimer": DISCLAIMER,
        "evaluation": _metrics,
    }
