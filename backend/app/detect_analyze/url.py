"""F-01 lexical/domain URL features, normalization, type detection, and chain security (CSHAKTI-ML-001 §2.4).

Maintains exact 19-feature vector order:
1. url_length
2. domain_length
3. path_length
4. num_dots
5. num_hyphens
6. num_underscores
7. num_at_signs
8. num_question_marks
9. num_slashes
10. num_digits
11. digit_to_letter_ratio
12. has_ip_address
13. uses_https
14. has_port_in_url
15. url_entropy
16. subdomain_count
17. is_shortened_url
18. is_suspicious_tld
19. is_brand_lookalike
"""

from __future__ import annotations

import ipaddress
import math
import re
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import unquote, urlparse, urlunparse

SUSPICIOUS_TLDS = (
    ".xyz", ".top", ".click", ".loan", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".zip", ".work", ".buzz", ".monster", ".fit", ".rest", ".bar", ".surf",
    ".sbs", ".cfd", ".icu", ".cam"
)

# Common shorteners including QR shortener domains
SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly",
    "rb.gy", "qr.co", "tiny.cc", "rebrand.ly", "t.ly", "shorturl.at", "bl.ink",
    "v.gd", "buff.ly", "shortcm.li", "qrco.de", "me-qr.com", "qr-code.link"
}

OFFICIAL_DOMAINS = {
    # Indian banking, payments & UPI
    "sbi.co.in", "www.sbi.co.in", "onlinesbi.sbi",
    "hdfcbank.com", "www.hdfcbank.com",
    "icicibank.com", "www.icicibank.com",
    "paytm.com", "www.paytm.com",
    "phonepe.com", "www.phonepe.com",
    "kotak.com", "www.kotak.com",
    "axisbank.com", "www.axisbank.com",
    "pnbindia.in", "www.pnbindia.in",
    "bankofbaroda.in", "www.bankofbaroda.in",
    "canarabank.com", "www.canarabank.com",
    "unionbankofindia.co.in",
    # Indian government & infrastructure
    "rbi.org.in", "www.rbi.org.in",
    "incometax.gov.in",
    "uidai.gov.in",
    "irctc.co.in", "www.irctc.co.in",
    "india.gov.in",
    "epfindia.gov.in",
    "gstn.org.in",
    "npci.org.in",
    "sebi.gov.in",
    "mca.gov.in",
    "passport.gov.in",
    "digilocker.gov.in",
    # Global search & productivity
    "google.com", "www.google.com", "mail.google.com", "drive.google.com",
    "microsoft.com", "www.microsoft.com", "login.microsoftonline.com",
    "office.com", "outlook.com", "live.com",
    "apple.com", "www.apple.com",
    # Social & communication
    "facebook.com", "www.facebook.com",
    "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com", "x.com",
    "whatsapp.com", "www.whatsapp.com",
    "telegram.org", "web.telegram.org",
    "linkedin.com", "www.linkedin.com",
    "youtube.com", "www.youtube.com",
    "reddit.com", "www.reddit.com",
    # Dev & knowledge
    "github.com", "www.github.com",
    "stackoverflow.com", "www.stackoverflow.com",
    "wikipedia.org", "en.wikipedia.org",
    # Commerce & streaming
    "amazon.com", "www.amazon.com", "amazon.in", "www.amazon.in",
    "flipkart.com", "www.flipkart.com",
    "netflix.com", "www.netflix.com",
    "hotstar.com", "www.hotstar.com",
}

BRAND_TOKENS = (
    "paytm", "sbi", "hdfc", "icici", "phonepe", "upi", "uidai", "incometax",
    "irctc", "kotak", "axisbank", "punjabnationalbank", "pnb", "bankofbaroda",
    "canarabank", "unionbank", "paypal", "microsoft", "amazon", "netflix"
)

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


def normalize_url(url: str) -> Tuple[str, Dict[str, Any]]:
    """
    Normalizes a user-supplied URL without discarding phishing signals.
    Handles:
    - Scheme normalization (default https:// if missing, reject invalid schemes)
    - Hostname lowercase & trailing dot removal
    - IDN / Punycode decoding
    - Default port stripping (:80 for http, :443 for https)
    - Obfuscation / double encoding detection
    """
    raw = url.strip()
    if not raw:
        raise ValueError("URL cannot be empty or whitespace only.")

    # Reject non-web schemes
    lower_raw = raw.lower()
    for forbidden in ("javascript:", "data:", "file:", "ftp:", "vbscript:", "about:"):
        if lower_raw.startswith(forbidden):
            raise ValueError(f"Unsupported scheme: {forbidden.rstrip(':')}")

    if not (lower_raw.startswith("http://") or lower_raw.startswith("https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)
    scheme = parsed.scheme.lower()
    if scheme not in ("http", "https"):
        raise ValueError(f"Invalid URL scheme '{scheme}'. Only http and https are supported.")

    netloc = parsed.netloc
    if not netloc:
        raise ValueError("Invalid URL: missing host/domain.")

    # Handle IDN / Punycode & port
    port = parsed.port
    host = (parsed.hostname or "").lower().rstrip(".")

    # Handle Punycode decoding for visibility
    decoded_host = host
    is_punycode = False
    try:
        if "xn--" in host:
            decoded_host = host.encode("ascii").decode("idna")
            is_punycode = True
    except Exception:
        pass

    # Normalize port
    port_str = ""
    if port:
        if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
            port_str = f":{port}"

    normalized_netloc = f"{host}{port_str}"
    
    # Path normalization
    path = parsed.path or ""
    if not path and not parsed.query and not parsed.fragment:
        path = ""

    normalized_url = urlunparse((
        scheme,
        normalized_netloc,
        path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

    # Obfuscation metadata
    obfuscation_info = {
        "is_punycode": is_punycode,
        "decoded_host": decoded_host,
        "percent_encoded_count": raw.count("%"),
        "has_at_symbol": "@" in netloc,
        "has_custom_port": bool(port_str),
    }

    return normalized_url, obfuscation_info


def detect_url_type(url: str, features: Optional[Dict[str, Any]] = None) -> str:
    """
    Classifies URL type:
    - SHORTENED
    - IP_BASED
    - OBFUSCATED
    - REDIRECTING
    - DIRECT
    - UNKNOWN
    """
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        if not host:
            return "UNKNOWN"

        # Check IP-based
        try:
            ipaddress.ip_address(host)
            return "IP_BASED"
        except ValueError:
            pass

        # Check Shortened
        if host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS):
            return "SHORTENED"

        # Check Obfuscation (punycode, excessive percent encoding, multiple @ symbols, hex IP notation)
        if "xn--" in host or "%" in host or "@" in (parsed.netloc or ""):
            return "OBFUSCATED"

        # Check redirecting parameters (e.g. ?url=..., ?redirect=..., ?dest=...)
        query_lower = (parsed.query or "").lower()
        if any(param in query_lower for param in ("url=", "redirect=", "target=", "dest=", "link=", "goto=", "next=")):
            return "REDIRECTING"

        return "DIRECT"
    except Exception:
        return "UNKNOWN"


def analyze_redirect_chain_security(
    original_url: str,
    final_url: str,
    chain: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Analyzes the resolved redirect chain for security risks:
    - Domain switches (cross-domain redirects)
    - HTTPS -> HTTP protocol downgrades
    - High hop count (> 3)
    - Suspicious intermediate domains
    """
    orig_parsed = urlparse(original_url)
    final_parsed = urlparse(final_url)
    
    orig_host = (orig_parsed.hostname or "").lower()
    final_host = (final_parsed.hostname or "").lower()
    
    domain_changed = orig_host != final_host and bool(orig_host) and bool(final_host)
    
    # Protocol downgrade check
    orig_scheme = orig_parsed.scheme.lower()
    final_scheme = final_parsed.scheme.lower()
    https_downgraded = (orig_scheme == "https" and final_scheme == "http")
    
    # Intermediate domains
    intermediate_domains = []
    has_suspicious_intermediate = False
    for hop in chain:
        d = hop.get("domain", "")
        if d and d not in intermediate_domains:
            intermediate_domains.append(d)
            if any(d.endswith(tld) for tld in SUSPICIOUS_TLDS):
                has_suspicious_intermediate = True

    return {
        "redirect_count": max(len(chain) - 1, 0) if chain else 0,
        "domain_changed": domain_changed,
        "original_domain": orig_host,
        "final_domain": final_host,
        "https_downgraded": https_downgraded,
        "intermediate_domains": intermediate_domains,
        "has_suspicious_intermediate": has_suspicious_intermediate,
        "chain_length_risk": len(chain) > 3,
    }


def calculate_brand_similarity(hostname: str) -> Tuple[Optional[str], float]:
    """
    Computes fuzzy brand similarity score (0.0 to 1.0) against targeted institutions using SequenceMatcher.
    Only evaluates domain/subdomain labels, completely ignoring URL paths/queries to eliminate keyword bias.
    """
    import difflib
    host_clean = (hostname or "").lower().split(':')[0].rstrip('.')
    if not host_clean or host_clean in OFFICIAL_DOMAINS or any(host_clean.endswith("." + d) for d in OFFICIAL_DOMAINS):
        return None, 0.0

    parts = host_clean.split('.')
    domain_labels = [p for p in parts if p and p not in ('com', 'in', 'org', 'net', 'co', 'io', 'xyz', 'info', 'online', 'top', 'www', 'gov', 'edu')]
    target_brands = ['paypal', 'microsoft', 'google', 'apple', 'amazon', 'netflix', 'sbi', 'paytm', 'hdfc', 'icici', 'phonepe', 'irctc', 'kotak', 'uidai']

    best_brand = None
    best_score = 0.0

    for label in domain_labels:
        tokens = label.split('-') + [label]
        for token in tokens:
            if not token:
                continue
            for b in target_brands:
                if token == b:
                    best_brand = b
                    best_score = max(best_score, 1.0)
                elif len(token) >= 3 and len(b) >= 3:
                    sim = difflib.SequenceMatcher(None, token, b).ratio()
                    if sim >= 0.75 and sim > best_score:
                        best_score = sim
                        best_brand = b

    return best_brand, round(best_score, 3)


def extract_url_features(url: str) -> Dict[str, Any]:
    """
    Extracts the EXACT 19 lexical & domain features required by F-01 XGBoost model
    plus enriched structural, entropy, and brand metrics.
    Maintains 100% backward compatibility and exact feature order.
    """
    raw = unquote(url.strip())
    parsed = urlparse(raw if raw.startswith(('http://', 'https://')) else f'http://{raw}')
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    query = parsed.query or ""
    fragment = parsed.fragment or ""
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
    
    # Calculate brand similarity strictly on domain/hostname (NEVER on path/query to avoid keyword bias)
    impersonated_brand, brand_sim_score = calculate_brand_similarity(host)
    is_brand_lookalike = 1 if (impersonated_brand is not None and brand_sim_score >= 0.75) else 0

    special_chars = sum(not ch.isalnum() for ch in raw)
    query_params_count = len(query.split("&")) if query else 0

    return {
        # Core 19 Lexical & Domain Features (strict order)
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
        "is_shortened_url": int(host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS)),
        "is_suspicious_tld": int(any(host.endswith(tld) for tld in SUSPICIOUS_TLDS)),
        "is_brand_lookalike": is_brand_lookalike,

        # Additional Enriched Structural & Entropy Features
        "hostname_length": len(host),
        "query_length": len(query),
        "fragment_length": len(fragment),
        "digit_count": sum(c.isdigit() for c in raw),
        "special_character_count": special_chars,
        "special_character_ratio": round(special_chars / max(len(raw), 1), 4),
        "numeric_ratio": round(sum(c.isdigit() for c in raw) / max(len(raw), 1), 4),
        "hostname_entropy": round(_shannon_entropy(host), 4),
        "path_entropy": round(_shannon_entropy(path), 4),
        "query_parameter_count": query_params_count,
        "double_slash_path": 1 if "//" in path else 0,
        "percent_encoded_count": raw.count("%"),
        "at_symbol_present": 1 if "@" in raw else 0,
        "punycode_present": 1 if "xn--" in host else 0,
        "brand_detected": impersonated_brand,
        "brand_similarity_score": brand_sim_score,
        "possible_impersonated_brand": impersonated_brand,

        # Backward compatibility aliases
        "uses_ip_address": uses_ip,
        "is_shortener": host in SHORTENERS or any(host.endswith("." + s) for s in SHORTENERS),
        "has_at_symbol": "@" in raw.split("://", 1)[-1].split("/", 1)[0] if "://" in raw else "@" in raw,
        "hyphen_count": host.count("-"),
        "keyword_hits": [impersonated_brand] if impersonated_brand else [],
        "is_known_brand_lookalike": bool(is_brand_lookalike),
        "has_suspicious_tld": any(host.endswith(tld) for tld in SUSPICIOUS_TLDS),
        "on_phishing_blocklist": None,
        "google_safe_browsing_hit": None,
        "domain_age_days": None,
    }


def feature_vector(features: Dict[str, Any]) -> List[float]:
    """Generates the exact 19-element numeric float array in the order expected by XGBoost."""
    return [float(features.get(name) or 0) for name in NUMERIC_FEATURE_ORDER]


def heuristic_is_high_risk(features: Dict[str, Any]) -> bool:
    """Fallback only when no trained artefact is loaded."""
    return bool(
        features.get("uses_ip_address")
        or features.get("is_shortener")
        or features.get("has_at_symbol")
        or (features.get("hyphen_count") or 0) >= 3
        or features.get("is_suspicious_tld")
        or features.get("is_brand_lookalike")
    )
