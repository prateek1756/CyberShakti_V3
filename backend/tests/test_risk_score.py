import pytest
from app.assist_respond.router import compute_weighted_risk_score, get_score_band


def test_weighted_risk_score_baseline():
    score, signals = compute_weighted_risk_score(scans=[], questionnaire=None)
    assert score == 50
    band_key, band_label = get_score_band(score)
    assert band_key == "moderate_risk"


def test_weighted_risk_score_questionnaire_safe():
    questionnaire = {
        "uses_2fa_on_bank_apps": True,
        "reuses_passwords": False,
        "shares_otp_with_others": False,
        "locks_phone": True
    }
    score, signals = compute_weighted_risk_score(scans=[], questionnaire=questionnaire)
    # 50 + 10 (2FA) + 10 (phone lock) = 70
    assert score == 70
    band_key, band_label = get_score_band(score)
    assert band_key == "low_risk"


def test_weighted_risk_score_questionnaire_unsafe():
    questionnaire = {
        "uses_2fa_on_bank_apps": False,
        "reuses_passwords": True,
        "shares_otp_with_others": True,
        "locks_phone": False
    }
    score, signals = compute_weighted_risk_score(scans=[], questionnaire=questionnaire)
    # 50 - 10 - 15 - 25 = 0 (clamped)
    assert score == 0
    band_key, band_label = get_score_band(score)
    assert band_key == "very_high_risk"
