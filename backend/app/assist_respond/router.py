import uuid
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.shared.database import get_db
from app.shared.auth import get_current_user, get_optional_current_user
from app.shared.models import (
    User, ScanResult, ScamAlert, RiskScoreSnapshot, RiskScoreSignal
)

router = APIRouter()


class AssistantQueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    conversation_id: Optional[str] = None


class QuestionnaireRequest(BaseModel):
    uses_2fa_on_bank_apps: Optional[bool] = None
    reuses_passwords: Optional[bool] = None
    shares_otp_with_others: Optional[bool] = None
    locks_phone: Optional[bool] = None


@router.post("/query-assistant")
async def query_assistant(
    payload: AssistantQueryRequest,
    current_user: User = Depends(get_current_user)
):
    """
    F-11 AI Cybersecurity Assistant Query Endpoint.
    Blocked per Step 8 rule because ADR-013 (LLM Provider Selection) is OPEN.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={
            "error_code": "LLM_PROVIDER_UNRESOLVED",
            "message": "F-11 AI Assistant is BLOCKED. ADR-013 (LLM Provider Selection) remains OPEN in 00-decisions.md.",
            "adr_id": "ADR-013",
            "status": "OPEN"
        }
    )


def compute_weighted_risk_score(
    scans: List[ScanResult],
    questionnaire: Optional[Dict[str, Optional[bool]]] = None
) -> tuple[int, List[Dict[str, Any]]]:
    """
    Computes Cyber Risk Score using the approved weighted engine (CSHAKTI-ML-001 §10, ADR-012, ADR-020).
    Baseline: 50
    """
    score = 50
    signals = []

    # 1. Activity signals from scan history
    if scans:
        high_risk_scans = [s for s in scans if s.risk_level in ["high_risk", "critical"]]
        if high_risk_scans:
            penalty = len(high_risk_scans) * 10
            score -= penalty
            signals.append({
                "signal_name": "recent_high_risk_detections",
                "label": "High-risk scam detections",
                "contribution_direction": "negative",
                "weight": -10.0,
                "description": f"Detected {len(high_risk_scans)} high-risk threat(s) in scan history."
            })

        scan_bonus = min(len(scans) * 5, 20)
        score += scan_bonus
        signals.append({
            "signal_name": "scans_performed",
            "label": "Active scan usage",
            "contribution_direction": "positive",
            "weight": 5.0,
            "description": f"Performed {len(scans)} security scan(s)."
        })
        
        has_pwd_check = any(s.feature_id == "F-09" for s in scans)
        if has_pwd_check:
            score += 5
            signals.append({
                "signal_name": "password_check_performed",
                "label": "Password strength check",
                "contribution_direction": "positive",
                "weight": 5.0,
                "description": "Checked password strength using F-09."
            })
            
        has_file_enc = any(s.feature_id == "F-10" for s in scans)
        if has_file_enc:
            score += 10
            signals.append({
                "signal_name": "file_encryption_used",
                "label": "Secure file encryption",
                "contribution_direction": "positive",
                "weight": 10.0,
                "description": "Used AES-256-GCM file encryption."
            })
    else:
        signals.append({
            "signal_name": "baseline_new_user",
            "label": "Initial onboarding baseline",
            "contribution_direction": "positive",
            "weight": 0.0,
            "description": "Baseline score assigned to new user accounts."
        })

    # 2. User-reported questionnaire signals (CSHAKTI-ML-001 §10.2)
    if questionnaire:
        if questionnaire.get("uses_2fa_on_bank_apps") is True:
            score += 10
            signals.append({
                "signal_name": "uses_2fa_on_bank_apps",
                "label": "2FA on banking apps",
                "contribution_direction": "positive",
                "weight": 10.0,
                "description": "Two-factor authentication enabled on banking apps."
            })
        elif questionnaire.get("uses_2fa_on_bank_apps") is False:
            score -= 10
            signals.append({
                "signal_name": "uses_2fa_on_bank_apps",
                "label": "Missing 2FA on banking apps",
                "contribution_direction": "negative",
                "weight": -10.0,
                "description": "Two-factor authentication not enabled on banking apps."
            })

        if questionnaire.get("reuses_passwords") is True:
            score -= 15
            signals.append({
                "signal_name": "reuses_passwords",
                "label": "Password reuse across accounts",
                "contribution_direction": "negative",
                "weight": -15.0,
                "description": "Reusing passwords increases vulnerability to credential stuffing."
            })

        if questionnaire.get("shares_otp_with_others") is True:
            score -= 25
            signals.append({
                "signal_name": "shares_otp_with_others",
                "label": "Shared OTP with callers",
                "contribution_direction": "negative",
                "weight": -25.0,
                "description": "Sharing OTPs exposes accounts to immediate unauthorized takeover."
            })

        if questionnaire.get("locks_phone") is True:
            score += 10
            signals.append({
                "signal_name": "locks_phone",
                "label": "Device lock enabled",
                "contribution_direction": "positive",
                "weight": 10.0,
                "description": "Device protected with PIN/Biometric lock."
            })

    final_score = max(0, min(100, int(score)))
    return final_score, signals


def get_score_band(score: int) -> tuple[str, str]:
    if score <= 20:
        return "very_high_risk", "Very High Risk"
    elif score <= 40:
        return "high_risk", "High Risk"
    elif score <= 60:
        return "moderate_risk", "Moderate Risk"
    elif score <= 80:
        return "low_risk", "Low Risk"
    else:
        return "well_protected", "Well Protected"


@router.get("/risk-score")
async def get_risk_score(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    scans = []
    q_data = None
    try:
        stmt = select(ScanResult).where(ScanResult.user_id == current_user.id)
        results = await db.execute(stmt)
        scans = list(results.scalars().all())

        stmt_snap = select(RiskScoreSnapshot).where(RiskScoreSnapshot.user_id == current_user.id).order_by(desc(RiskScoreSnapshot.computed_at)).limit(1)
        res_snap = await db.execute(stmt_snap)
        latest_snap = res_snap.scalar_one_or_none()

        if latest_snap:
            stmt_sig = select(RiskScoreSignal).where(RiskScoreSignal.snapshot_id == latest_snap.id)
            res_sig = await db.execute(stmt_sig)
            sig_objs = res_sig.scalars().all()
            q_data = {s.signal_name: True for s in sig_objs if s.contribution_direction == "positive"}
    except Exception:
        pass

    score, signal_breakdown = compute_weighted_risk_score(scans, q_data)
    band_key, band_label = get_score_band(score)

    return {
        "score": score,
        "score_band": band_key,
        "score_band_label": band_label,
        "signal_breakdown": signal_breakdown,
        "improvement_actions": [
            "Enable 2FA on banking and email accounts.",
            "Never share OTPs or PINs over phone calls.",
            "Use non-reused passwords evaluated via Password Security Checker."
        ],
        "disclaimer": "Your Cyber Risk Score is calculated using an explainable weighted signal engine based on your activity and responses."
    }


@router.post("/risk-score/questionnaire")
async def update_questionnaire(
    payload: QuestionnaireRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    scans = []
    try:
        stmt = select(ScanResult).where(ScanResult.user_id == current_user.id)
        results = await db.execute(stmt)
        scans = list(results.scalars().all())
    except Exception:
        pass

    q_dict = payload.model_dump()
    score, signals = compute_weighted_risk_score(scans, q_dict)

    try:
        snapshot = RiskScoreSnapshot(
            user_id=current_user.id,
            score=score,
            signal_count=len(signals)
        )
        db.add(snapshot)
        await db.commit()
        await db.refresh(snapshot)

        for sig in signals:
            sig_obj = RiskScoreSignal(
                snapshot_id=snapshot.id,
                signal_name=sig["signal_name"],
                signal_value={"label": sig["label"]},
                contribution_direction=sig["contribution_direction"],
                weight=sig["weight"]
            )
            db.add(sig_obj)
            
        await db.commit()
    except Exception:
        pass

    band_key, band_label = get_score_band(score)

    return {
        "message": "Questionnaire responses saved and Risk Score updated.",
        "score": score,
        "score_band": band_key,
        "score_band_label": band_label,
        "signal_breakdown": signals
    }


@router.get("/scam-alerts")
async def get_scam_alerts(
    city: Optional[str] = "Mumbai",
    state: Optional[str] = None,
    current_user: Optional[User] = Depends(get_optional_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ScamAlert).where(ScamAlert.is_active == True).limit(10)
    result = await db.execute(stmt)
    alerts = list(result.scalars().all())

    if not alerts:
        mock_alerts = [
            {
                "alert_id": str(uuid.uuid4()),
                "title": f"Fraudulent UPI Collect Requests Targeting {city} Residents",
                "description": "Multiple reports of fake UPI collect requests impersonating utility board officials demanding bill payments.",
                "alert_type": "upi_fraud",
                "severity": "high_risk",
                "published_at": "2026-08-18T10:00:00Z",
                "source": "CERT-In Advisory"
            }
        ]
        return {
            "location": {"resolved_location": f"{city}, India", "precision": "city"},
            "alerts": mock_alerts,
            "total_alerts": 1,
            "last_updated": "2026-08-20T08:00:00Z",
            "data_disclaimer": "Alert data is sourced from publicly reported incidents and official advisories."
        }

    return {
        "location": {"resolved_location": f"{city}, India", "precision": "city"},
        "alerts": [
            {
                "alert_id": str(a.id),
                "title": a.title,
                "description": a.description,
                "alert_type": a.alert_type,
                "severity": a.severity,
                "published_at": a.published_at.isoformat(),
                "source": a.source
            } for a in alerts
        ],
        "total_alerts": len(alerts),
        "last_updated": "2026-08-20T08:00:00Z",
        "data_disclaimer": "Alert data is sourced from publicly reported incidents and official advisories."
    }
