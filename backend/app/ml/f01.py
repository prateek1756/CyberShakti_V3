"""F-01 inference: trained XGBoost if artefact exists; otherwise documented lexical fallback."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.detect_analyze.url import NUMERIC_FEATURE_ORDER, extract_url_features, feature_vector, heuristic_is_high_risk
from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

_model = None
_metrics: Optional[dict] = None
_loaded = False


def _ensure_loaded() -> None:
    global _model, _metrics, _loaded
    if _loaded:
        return
    _model = load_joblib("f01_phishing_url_model.joblib")
    _metrics = load_json("f01_metrics.json")
    _loaded = True


def probability_to_risk(prob: float, features: Dict[str, Any]) -> str:
    if features.get("uses_ip_address"):
        if prob < 0.4:
            return "moderate_risk"
    if prob >= 0.75:
        return "high_risk"
    if prob >= 0.55:
        return "moderate_risk"
    if prob >= 0.35:
        return "low_risk"
    return "safe"


def _shap_signals(model, vector: List[float]) -> List[str]:
    try:
        import numpy as np
        import shap

        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(np.array([vector]))
        row = values[0] if not isinstance(values, list) else values[1][0]
        ranked = sorted(zip(NUMERIC_FEATURE_ORDER, row), key=lambda x: abs(float(x[1])), reverse=True)
        return [name for name, val in ranked[:5] if abs(float(val)) > 0]
    except Exception:
        booster = getattr(model, "get_booster", None)
        if booster:
            scores = booster().get_score(importance_type="gain")
            ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            return [k for k, _ in ranked[:5]]
        return []


def infer_url(url: str) -> Dict[str, Any]:
    features = extract_url_features(url)
    _ensure_loaded()
    vector = feature_vector(features)
    model_loaded = _model is not None
    if model_loaded:
        import numpy as np

        prob = float(_model.predict_proba(np.array([vector]))[0][1])
        risk_level = probability_to_risk(prob, features)
        signals = _shap_signals(_model, vector)
        source = "ml_model"
        note = "XGBoost on lexical/domain features. Threat-intel lookups are not integrated (ADR-032 open)."
    else:
        is_phish = heuristic_is_high_risk(features)
        prob = None
        risk_level = "high_risk" if is_phish else "safe"
        signals = ["lexical_fallback"] if is_phish else []
        source = "heuristic"
        note = "Trained F-01 artefact not loaded; lexical fallback in use."

    verdict = generate_explanation(
        feature_id="F-01",
        risk_level=risk_level,
        signals=signals or None,
        scam_category="malicious_url" if risk_level in ("high_risk", "critical") else None,
    )
    return {
        "features": features,
        "verdict": verdict,
        "probability": prob,
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "evaluation": _metrics,
    }
