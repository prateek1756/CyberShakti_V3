from typing import Dict, Any, List, Optional
from datetime import timezone, datetime


RISK_DESCRIPTIONS = {
    "safe": "No known threat indicators or scam patterns were detected in this analysis.",
    "low_risk": "Low risk detected. Minor signals present, but no definitive threat indicators found.",
    "moderate_risk": "Moderate risk detected. Exercise caution and verify details before interacting.",
    "high_risk": "High risk detected! Strong scam or phishing indicators were identified.",
    "critical": "Critical threat detected! High likelihood of active fraud or malicious activity."
}


AI_DISCLAIMER_STANDARD = (
    "This assessment is produced by an automated system and may not detect all threats. "
    "Do not rely solely on this verdict. Exercise caution with any suspicious content."
)

EXPERIMENTAL_DISCLAIMER_STANDARD = (
    "This is an experimental research feature. Results are indicative only and should not "
    "be used as definitive evidence of manipulation. False positives and false negatives occur."
)


def generate_explanation(
    feature_id: str,
    risk_level: str,
    signals: Optional[List[str]] = None,
    scam_category: Optional[str] = None,
    is_experimental: bool = False
) -> Dict[str, Any]:
    """
    Generates plain-language explanation objects adhering to CyberShakti standards.
    """
    base_explanation = RISK_DESCRIPTIONS.get(risk_level.lower(), "Risk assessment completed.")
    
    explanation_parts = [base_explanation]
    
    if scam_category:
        category_readable = scam_category.replace("_", " ").title()
        explanation_parts.append(f"Category pattern match: {category_readable}.")
        
    if signals and len(signals) > 0:
        signal_text = ", ".join(signals[:3])
        explanation_parts.append(f"Key indicators: {signal_text}.")
        
    full_explanation = " ".join(explanation_parts)
    
    disclaimer = EXPERIMENTAL_DISCLAIMER_STANDARD if is_experimental else AI_DISCLAIMER_STANDARD
    
    return {
        "risk_level": risk_level.lower(),
        "risk_label": risk_level.replace("_", " ").title(),
        "explanation": full_explanation,
        "scam_category": scam_category,
        "confidence_indicator": "high" if risk_level in ["critical", "high_risk", "safe"] else "medium",
        "is_experimental": is_experimental,
        "disclaimer": disclaimer,
        "analysed_at": datetime.now(timezone.utc).isoformat()
    }
