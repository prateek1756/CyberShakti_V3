"""F-01 lexical/domain URL features (CSHAKTI-ML-001 §2.4). WHOIS/TI omitted — ADR-032 open."""

from __future__ import annotations

import ipaddress
import math
import re
from typing import Any, Dict, List
from urllib.parse import unquote, urlparse

SUSPICIOUS_TLDS = (".xyz", ".top", ".click", ".loan", ".tk", ".ml", ".ga", ".cf", ".gq", ".zip", ".work")
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly", "rb.gy"}
BRAND_TOKENS = ("paytm", "sbi", "hdfc", "icici", "phonepe", "upi", "uidai", "incometax", "irctc", "kotak")

NUMERIC_FEATURE_ORDER = [
    "url_length",
    "domain_length",
    "path_length",
    "num_dots",
    "num_hyphens",
    "num_underscores",
    "num_at_signs",
    "num_question_marks",
    "num_slashes",
    "num_digits",
    "digit_to_letter_ratio",
    "has_ip_address",
    "uses_https",
    "has_port_in_url",
    "url_entropy",
    "subdomain_count",
    "is_shortened_url",
    "is_suspicious_tld",
    "is_brand_lookalike",
]


def _shannon_entropy(text: str) -> float:
    if not text:
        return 0.0
    freq: Dict[str, int] = {}
    for ch in text:
        freq[ch] = freq.get(ch, 0) + 1
    length = len(text)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def extract_url_features(url: str) -> Dict[str, Any]:
    raw = unquote(url.strip())
    parsed = urlparse(raw)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    uses_ip = False
    if host:
        try:
            ipaddress.ip_address(host)
            uses_ip = True
        except ValueError:
            uses_ip = False

    domain_letters = sum(ch.isalpha() for ch in host)
    domain_digits = sum(ch.isdigit() for ch in host)
    labels = [p for p in host.split(".") if p]
    subdomain_count = max(len(labels) - 2, 0) if not uses_ip else 0
    haystack = f"{host}{path}{parsed.query}".lower()
    brand = any(token in haystack for token in BRAND_TOKENS)

    return {
        "host": host,
        "url_length": len(raw),
        "domain_length": len(host),
        "path_length": len(path),
        "num_dots": raw.count("."),
        "num_hyphens": host.count("-"),
        "num_underscores": raw.count("_"),
        "num_at_signs": raw.count("@"),
        "num_question_marks": raw.count("?"),
        "num_slashes": raw.count("/"),
        "num_digits": domain_digits,
        "digit_to_letter_ratio": (domain_digits / domain_letters) if domain_letters else 0.0,
        "has_ip_address": int(uses_ip),
        "uses_https": int(parsed.scheme.lower() == "https"),
        "has_port_in_url": int(parsed.port is not None and parsed.port not in (80, 443)),
        "url_entropy": round(_shannon_entropy(raw), 4),
        "subdomain_count": subdomain_count,
        "is_shortened_url": int(host in SHORTENERS),
        "is_suspicious_tld": int(any(host.endswith(tld) for tld in SUSPICIOUS_TLDS)),
        "is_brand_lookalike": int(brand),
        "uses_ip_address": uses_ip,
        "is_shortener": host in SHORTENERS,
        "has_at_symbol": "@" in raw.split("://", 1)[-1].split("/", 1)[0],
        "hyphen_count": host.count("-"),
        "keyword_hits": [t for t in BRAND_TOKENS if t in haystack],
        "is_known_brand_lookalike": brand,
        "has_suspicious_tld": any(host.endswith(tld) for tld in SUSPICIOUS_TLDS),
        "on_phishing_blocklist": None,
        "google_safe_browsing_hit": None,
        "domain_age_days": None,
    }


def feature_vector(features: Dict[str, Any]) -> List[float]:
    return [float(features.get(name) or 0) for name in NUMERIC_FEATURE_ORDER]


def heuristic_is_high_risk(features: Dict[str, Any]) -> bool:
    """Fallback only when no trained artefact is loaded."""
    return bool(
        features.get("uses_ip_address")
        or features.get("is_shortener")
        or features.get("has_at_symbol")
        or (features.get("hyphen_count") or 0) >= 3
        or features.get("is_suspicious_tld")
    )
