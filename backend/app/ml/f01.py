"""F-01 Real-Time URL Threat Analysis Engine:
- Connects live destination resolver + redirect chain security.
- Preserves 19 lexical/domain features & XGBoost model inference.
- Preserves & enriches SHAP explanations with human-readable security signals.
- Separates Link Status (DIRECT, REDIRECTED, UNKNOWN) from Security Verdict (LEGITIMATE, SUSPICIOUS, PHISHING, UNKNOWN).
- Computes comprehensive 0-100 risk score.
- Fails closed to UNKNOWN (never false-SAFE) on unresolvable/blocked hosts.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, Tuple

from app.detect_analyze.url import (
    NUMERIC_FEATURE_ORDER,
    analyze_redirect_chain_security,
    detect_url_type,
    extract_url_features,
    feature_vector,
    heuristic_is_high_risk,
    normalize_url,
)
from app.detect_analyze.url_resolver import ResolutionResult, resolve_url_safely
from app.ml.loader import load_joblib, load_json
from app.shared.explanation_engine import generate_explanation

_model = None
_metrics: Optional[dict] = None
_loaded = False

FEATURE_HUMAN_LABELS = {
    "url_entropy": "High URL randomness / Shannon entropy",
    "subdomain_count": "Excessive subdomain nesting",
    "num_hyphens": "Excessive hyphens in hostname",
    "digit_to_letter_ratio": "Suspicious digit density in domain",
    "num_digits": "High digit count in domain name",
    "is_brand_lookalike": "Brand keyword impersonation pattern",
    "is_suspicious_tld": "High-risk suspicious top-level domain (TLD)",
    "has_ip_address": "Direct numerical IP address used instead of domain",
    "has_port_in_url": "Non-standard port number in URL",
    "is_shortened_url": "URL shortener / redirect service detected",
    "num_dots": "Excessive dots in URL structure",
    "url_length": "Abnormally long URL length",
    "path_length": "Complex obfuscated path structure",
    "num_at_signs": "Embedded '@' credential obfuscation character",
    "uses_https": "Insecure unencrypted HTTP protocol",
}


def _ensure_loaded() -> None:
    global _model, _metrics, _loaded
    if _loaded:
        return
    _model = load_joblib("f01_phishing_url_model.joblib")
    _metrics = load_json("f01_metrics.json")
    _loaded = True


def _shap_factors(model, vector: List[float]) -> Tuple[List[str], List[str]]:
    """
    Extracts top risk factors (positive SHAP pushing towards phishing)
    and protective factors (negative SHAP pushing towards legitimate).
    """
    try:
        import numpy as np
        import shap

        explainer = shap.TreeExplainer(model)
        values = explainer.shap_values(np.array([vector]))
        row = values[0] if not isinstance(values, list) else values[1][0]
        
        paired = list(zip(NUMERIC_FEATURE_ORDER, row))
        # Positive contributions -> risk factors
        risk_sorted = sorted([p for p in paired if p[1] > 0.01], key=lambda x: x[1], reverse=True)
        # Negative contributions -> protective factors
        protective_sorted = sorted([p for p in paired if p[1] < -0.01], key=lambda x: x[1])

        risk_factors = [FEATURE_HUMAN_LABELS.get(name, name) for name, _ in risk_sorted[:4]]
        protective_factors = [f"Normal {name.replace('_', ' ')}" for name, _ in protective_sorted[:3]]
        return risk_factors, protective_factors
    except Exception:
        return [], []


def calculate_comprehensive_risk(
    ml_probability: Optional[float],
    final_features: Dict[str, Any],
    orig_features: Dict[str, Any],
    chain_sec: Dict[str, Any],
    resolution: ResolutionResult,
    obfuscation: Dict[str, Any],
) -> Tuple[int, str, str, List[str], List[str]]:
    """
    Computes a grounded risk score (0-100), link_status, security_verdict, human-readable explanations, and raw signals.
    
    Link Statuses:
    - DIRECT
    - REDIRECTED
    - UNKNOWN

    Security Verdicts:
    - REAL / LEGITIMATE (safe)
    - SUSPICIOUS (moderate_risk / low_risk)
    - PHISHING (high_risk / critical)
    - UNKNOWN (unresolvable or blocked SSRF)
    """
    explanations: List[str] = []
    signals: List[str] = []

    # 1. Determine Link Status
    if resolution.status == "REDIRECTED" or resolution.redirect_count > 0:
        link_status = "REDIRECTED"
    elif resolution.status == "SUCCESS":
        link_status = "DIRECT"
    else:
        link_status = "UNKNOWN"

    # 2. Check for SSRF Block
    if resolution.status == "BLOCKED_SSRF":
        signals.append("blocked_internal_network_ssrf")
        explanations.append("Destination attempts to access internal or restricted network infrastructure (SSRF prevented).")
        return 95, link_status, "critical", explanations, signals

    # 3. Base Score from ML Probability or Heuristics
    if ml_probability is not None:
        base_score = ml_probability * 100.0
    else:
        # Heuristic base
        base_score = 80.0 if heuristic_is_high_risk(final_features) else 10.0

    score = base_score

    # 4. Check for Unresolvable / Dead Destination
    if not resolution.is_reachable and resolution.status in ("DNS_ERROR", "TIMEOUT", "CONNECTION_ERROR", "UNRESOLVED_ERROR"):
        signals.append("destination_unreachable")
        explanations.append(f"Destination could not be verified online ({resolution.error_message or 'Server unreachable'}).")
        
        # If the URL is already high-risk or phishing structurally (e.g. brand spoofing, suspicious TLD, high entropy)
        # classify it as high_risk / phishing with reachability warning.
        # Otherwise, if it has no obvious phishing signals, fail closed to UNKNOWN rather than SAFE.
        has_phish_signals = (
            final_features.get("is_brand_lookalike")
            or orig_features.get("is_brand_lookalike")
            or final_features.get("is_suspicious_tld")
            or final_features.get("uses_ip_address")
            or score >= 70.0
        )
        if not has_phish_signals:
            return 50, link_status, "unknown", explanations, signals

    # 5. Multi-Signal Modifiers (Grounded & Calibrated)

    # Brand lookalike / spoofing
    if final_features.get("is_brand_lookalike") or orig_features.get("is_brand_lookalike"):
        hits = final_features.get("keyword_hits", []) or orig_features.get("keyword_hits", [])
        brand_names = ", ".join(hits) if hits else "major institution"
        signals.append("brand_impersonation")
        explanations.append(f"Detected brand impersonation patterns targeting {brand_names}.")
        score = max(score, 75.0)

    # Suspicious TLD
    if final_features.get("is_suspicious_tld"):
        signals.append("suspicious_tld")
        explanations.append("Domain utilizes a high-risk top-level domain frequently associated with phishing campaigns.")
        score = max(score, score + 15.0)

    # Direct IP Address
    if final_features.get("uses_ip_address"):
        signals.append("ip_based_destination")
        explanations.append("Target uses a raw numerical IP address instead of a registered domain name.")
        score = max(score, 65.0)

    # HTTPS -> HTTP downgrade
    if chain_sec.get("https_downgraded"):
        signals.append("ssl_downgrade")
        explanations.append("Redirect chain downgraded secure HTTPS connection to insecure HTTP.")
        score = max(score, score + 20.0)

    # Cross-domain hop with shortener
    if chain_sec.get("domain_changed") and orig_features.get("is_shortened_url"):
        signals.append("shortener_redirect_hop")
        explanations.append(f"URL shortener forwarded to external domain: {chain_sec.get('final_domain')}.")

    # Suspicious intermediate hop
    if chain_sec.get("has_suspicious_intermediate"):
        signals.append("suspicious_intermediate_domain")
        explanations.append("Redirect chain passed through intermediate domains with suspicious reputations.")
        score = max(score, score + 25.0)

    # High Shannon entropy
    if final_features.get("url_entropy", 0) > 4.2:
        signals.append("high_url_entropy")
        explanations.append("Target URL exhibits abnormally high character randomness indicative of auto-generated phishing kits.")

    # Punycode / IDN spoofing
    if obfuscation.get("is_punycode"):
        signals.append("punycode_homograph")
        explanations.append(f"Punycode/IDN internationalized domain detected (Decoded: {obfuscation.get('decoded_host')}).")
        score = max(score, score + 15.0)

    # Clamp risk score between 0 and 100
    final_score = int(min(max(round(score), 0), 100))

    # 5. Map to Standard Security Verdict
    if final_score >= 75:
        risk_level = "high_risk"
    elif final_score >= 45:
        risk_level = "moderate_risk"
    elif final_score >= 25:
        risk_level = "low_risk"
    else:
        risk_level = "safe"

    if not explanations:
        if risk_level == "safe":
            explanations.append("No suspicious redirect patterns, brand impersonation, or abnormal lexical features were identified.")
        else:
            explanations.append("Elevated structural risk score computed from machine learning evaluation.")

    return final_score, link_status, risk_level, explanations, signals


async def infer_url_async(
    url: str,
    resolve_live: bool = True,
    max_redirects: int = 5,
    timeout_seconds: float = 4.0
) -> Dict[str, Any]:
    """
    Asynchronously runs the full Real-Time URL Threat Analysis pipeline.
    """
    import time
    start_time = time.perf_counter()

    # 1. Validation & Normalization
    normalized_url, obfuscation = normalize_url(url)
    url_type = detect_url_type(normalized_url)

    # 2. Live Safe Resolution
    if resolve_live:
        resolution = await resolve_url_safely(
            normalized_url,
            max_redirects=max_redirects,
            timeout_seconds=timeout_seconds
        )
    else:
        resolution = ResolutionResult(
            original_url=url,
            final_url=normalized_url,
            redirect_count=0,
            redirect_chain=[],
            status="SUCCESS",
            is_safe_resolution=True,
            is_reachable=True,
        )

    final_url = resolution.final_url or normalized_url

    # 3. Feature Extraction on Final URL & Original URL
    final_features = extract_url_features(final_url)
    orig_features = extract_url_features(normalized_url)
    chain_sec = analyze_redirect_chain_security(normalized_url, final_url, resolution.redirect_chain)

    # 4. XGBoost Inference & SHAP
    _ensure_loaded()
    vector = feature_vector(final_features)
    model_loaded = _model is not None

    if model_loaded and resolution.is_reachable:
        import numpy as np
        prob = float(_model.predict_proba(np.array([vector]))[0][1])
        shap_risk, shap_protective = _shap_factors(_model, vector)
        source = "ml_model"
        note = "Native XGBoost evaluated on resolved final destination features."
    else:
        prob = None
        shap_risk, shap_protective = [], []
        source = "heuristic"
        note = "Lexical fallback and behavioral engine in use."

    # 5. Risk & Decision Engine
    risk_score, link_status, risk_level, explanations, raw_signals = calculate_comprehensive_risk(
        ml_probability=prob,
        final_features=final_features,
        orig_features=orig_features,
        chain_sec=chain_sec,
        resolution=resolution,
        obfuscation=obfuscation,
    )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    verdict_obj = generate_explanation(
        feature_id="F-01",
        risk_level=risk_level,
        signals=raw_signals or None,
        scam_category="malicious_url" if risk_level in ("high_risk", "critical") else None,
    )

    # Human-readable verdict mapping
    verdict_labels = {
        "safe": "REAL / LEGITIMATE",
        "low_risk": "LOW RISK",
        "moderate_risk": "SUSPICIOUS",
        "high_risk": "PHISHING",
        "critical": "CRITICAL THREAT",
        "unknown": "UNKNOWN / UNVERIFIED",
    }
    verdict_obj["verdict_status"] = verdict_labels.get(risk_level, risk_level.upper())
    verdict_obj["link_status"] = link_status

    structured_explanation = {
        "top_risk_factors": shap_risk if shap_risk else [exp for exp in explanations if "No suspicious" not in exp][:3],
        "protective_factors": shap_protective if shap_protective else (["Normal domain structure", "Low lexical complexity"] if risk_level in ("safe", "low_risk") else [])
    }

    return {
        "original_url": url,
        "normalized_url": normalized_url,
        "final_url": final_url,
        "classification": verdict_labels.get(risk_level, risk_level.upper()),
        "url_type": url_type,
        "link_status": link_status,
        "redirect_status": link_status,
        "redirect_count": resolution.redirect_count,
        "redirect_chain": resolution.redirect_chain,
        "redirect_analysis": {
            "redirect_count": resolution.redirect_count,
            "final_url": final_url,
            "final_domain_changed": chain_sec.get("domain_changed", False),
            "chain": resolution.redirect_chain
        },
        "resolution_details": resolution.to_dict(),
        "risk_score": risk_score,
        "confidence": round(1.0 - (prob if prob is not None else 0.5) if risk_level == "safe" else (prob if prob is not None else (risk_score / 100.0)), 2),
        "verdict": verdict_obj,
        "probability": prob,
        "ml_probability": prob,
        "features": final_features,
        "url_features": final_features,
        "original_features": orig_features,
        "explanations": explanations,
        "explanation": structured_explanation,
        "signals": raw_signals,
        "model": {
            "name": "XGBoost",
            "feature_count": len(NUMERIC_FEATURE_ORDER),
            "version": "native-v3"
        },
        "verdict_source": source,
        "model_note": note,
        "model_loaded": model_loaded,
        "evaluation": _metrics,
        "analysis_time_ms": elapsed_ms,
    }


def infer_url(url: str) -> Dict[str, Any]:
    """
    Synchronous entrypoint for backward compatibility.
    Runs async resolution safely on the current or new event loop.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(asyncio.run, infer_url_async(url)).result()
                return result
        else:
            return loop.run_until_complete(infer_url_async(url))
    except Exception:
        return asyncio.run(infer_url_async(url))
