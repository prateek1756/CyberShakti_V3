"""F-12 explainable weighted engine (ADR-012 / ADR-020 / CSHAKTI-ML-001 §10)."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID

WEIGHTS_PATH = Path(__file__).resolve().parent / "risk_score_weights.json"
QUESTIONNAIRE_KEYS = (
    "uses_2fa_on_bank_apps",
    "reuses_passwords",
    "shares_otp_with_others",
    "locks_phone",
)

_questionnaire: Dict[str, Dict[str, Optional[bool]]] = {}


def load_weight_config() -> dict:
    return json.loads(WEIGHTS_PATH.read_text(encoding="utf-8"))


def save_questionnaire(user_id: UUID, responses: Dict[str, Optional[bool]]) -> Dict[str, Optional[bool]]:
    cleaned = {k: responses.get(k) for k in QUESTIONNAIRE_KEYS}
    _questionnaire[str(user_id)] = cleaned
    return cleaned


def get_questionnaire(user_id: UUID) -> Dict[str, Optional[bool]]:
    return dict(_questionnaire.get(str(user_id), {}))


def _band(score: int) -> tuple[str, str]:
    if score <= 20:
        return "very_high_risk", "Very High Risk"
    if score <= 40:
        return "high_risk", "High Risk"
    if score <= 60:
        return "moderate_risk", "Moderate Risk"
    if score <= 80:
        return "low_risk", "Low Risk"
    return "well_protected", "Well Protected"


def compute_score(scans: List[Any], questionnaire: Dict[str, Optional[bool]]) -> Dict[str, Any]:
    cfg = load_weight_config()
    weights = cfg["weights"]
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=30)
    breakdown: List[dict] = []
    score = float(cfg["baseline"])

    def add(name: str, active: bool, contribution: float, direction: str, description: str, label: str) -> None:
        nonlocal score
        if not active:
            return
        delta = weights[name] * contribution
        if direction == "negative":
            delta = -abs(delta)
        else:
            delta = abs(delta)
        score += delta
        breakdown.append(
            {
                "signal_name": name,
                "label": label,
                "contribution_direction": direction,
                "weight": weights[name],
                "contribution_value": contribution,
                "description": description,
            }
        )

    high_risk = [
        s
        for s in scans
        if getattr(s, "risk_level", None) in ("high_risk", "critical")
        and (getattr(s, "scanned_at", now) or now) >= cutoff
    ]
    add(
        "recent_high_risk_detections",
        bool(high_risk),
        float(len(high_risk)),
        "negative",
        f"{len(high_risk)} high-risk or critical detections in the last 30 days.",
        "High-risk threat detections",
    )
    add(
        "scans_performed",
        bool(scans),
        1.0,
        "positive",
        "You have used CyberShakti scanning features.",
        "Active scanning usage",
    )
    pwd_scans = [s for s in scans if getattr(s, "feature_id", None) == "F-09" or getattr(s, "input_type", None) == "password_check"]
    add(
        "password_check_performed",
        bool(pwd_scans),
        1.0,
        "positive",
        "You have used the password security checker.",
        "Password check performed",
    )
    weak = [s for s in pwd_scans if getattr(s, "risk_level", None) in ("high_risk", "low_risk")]
    strong = [s for s in pwd_scans if getattr(s, "risk_level", None) == "safe"]
    if weak:
        add("password_check_verdict", True, 1.0, "negative", "A recent password check indicated a weak password.", "Password check verdict")
    elif strong:
        add("password_check_verdict", True, 1.0, "positive", "A recent password check indicated a stronger password.", "Password check verdict")
    add(
        "file_encryption_used",
        any(getattr(s, "feature_id", None) == "F-10" or getattr(s, "input_type", None) == "file_encrypt" for s in scans),
        1.0,
        "positive",
        "You have used secure file encryption.",
        "File encryption used",
    )
    add(
        "quiz_completed",
        any(getattr(s, "feature_id", None) == "F-14" or getattr(s, "input_type", None) == "quiz" for s in scans),
        1.0,
        "positive",
        "You completed a cybersecurity quiz.",
        "Quiz completed",
    )

    q_map = {
        "uses_2fa_on_bank_apps": ("positive", "Two-factor authentication on banking apps", "You reported using 2FA on banking apps."),
        "reuses_passwords": ("negative", "Password reuse", "You reported reusing passwords across accounts."),
        "shares_otp_with_others": ("negative", "OTP sharing", "You reported sharing an OTP with a caller."),
        "locks_phone": ("positive", "Phone lock", "You reported locking your phone with PIN/biometric."),
    }
    for key, (direction, label, desc) in q_map.items():
        value = questionnaire.get(key)
        if value is True:
            add(key, True, 1.0, direction, desc, label)

    final = int(max(0, min(100, round(score))))
    band, band_label = _band(final)
    is_baseline = not breakdown
    if is_baseline:
        breakdown.append(
            {
                "signal_name": "baseline_new_user",
                "label": "Baseline onboarding score",
                "contribution_direction": "positive",
                "weight": 0,
                "contribution_value": cfg["baseline"],
                "description": "Initial baseline score assigned when no Phase 1 signals are active.",
            }
        )
    return {
        "score": final,
        "score_band": band,
        "score_band_label": band_label,
        "signal_breakdown": breakdown,
        "is_baseline": is_baseline,
        "disclaimer": (
            "Your Cyber Risk Score uses the locked Phase 1 signal set and configured unit weights. "
            "It is an estimate, not a comprehensive security audit or ML prediction (ADR-012)."
        ),
        "improvement_actions": [
            "Enable two-factor authentication on banking apps.",
            "Avoid reusing passwords and never share OTPs.",
            "Use the password checker and file encryption tools.",
        ],
        "weight_policy": cfg.get("policy"),
    }
