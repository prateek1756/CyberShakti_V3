import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch, AsyncMock
from app.main import app
from app.detect_analyze.url import (
    extract_url_features,
    feature_vector,
    normalize_url,
    detect_url_type,
    analyze_redirect_chain_security,
    NUMERIC_FEATURE_ORDER,
)
from app.detect_analyze.url_resolver import (
    is_ip_blocked,
    validate_hostname_safe,
    resolve_url_safely,
    ResolutionResult,
)
from app.ml.f01 import infer_url, infer_url_async


# --- 1. Lexical & 19-Feature Vector Integrity ---

def test_19_features_order_and_count():
    assert len(NUMERIC_FEATURE_ORDER) == 19
    url = "https://secure-banking-login.example.com/verify?token=123"
    feats = extract_url_features(url)
    vec = feature_vector(feats)
    assert len(vec) == 19
    assert feats["url_length"] == len(url)
    assert feats["uses_https"] == 1
    assert feats["has_ip_address"] == 0


def test_brand_and_tld_features():
    phish_url = "http://sbi-kyc-update-portal.xyz/login"
    feats = extract_url_features(phish_url)
    assert feats["is_suspicious_tld"] == 1
    assert feats["is_brand_lookalike"] == 1
    assert "sbi" in feats["keyword_hits"]


# --- 2. URL Normalization & Validation ---

def test_normalize_valid_urls():
    norm, obf = normalize_url("google.com")
    assert norm == "https://google.com"

    norm, obf = normalize_url("http://EXAMPLE.COM:80/path/test")
    assert norm == "http://example.com/path/test"

    norm, obf = normalize_url("https://sbi.co.in:443/")
    assert norm == "https://sbi.co.in/"


def test_normalize_rejects_malicious_schemes():
    for bad in ["javascript:alert(1)", "data:text/html,hack", "file:///etc/passwd", "ftp://ftp.server"]:
        with pytest.raises(ValueError):
            normalize_url(bad)


def test_normalize_empty_rejects():
    with pytest.raises(ValueError):
        normalize_url("   ")


# --- 3. URL Type Detection ---

def test_detect_url_types():
    assert detect_url_type("https://bit.ly/3xyz") == "SHORTENED"
    assert detect_url_type("https://qr.co/2dt567") == "SHORTENED"
    assert detect_url_type("http://192.168.1.1/admin") == "IP_BASED"
    assert detect_url_type("https://user:pass@example.com/login") == "OBFUSCATED"
    assert detect_url_type("https://google.com/search?q=test") == "DIRECT"
    assert detect_url_type("https://gate.example.com/login?redirect=http://target.com") == "REDIRECTING"


# --- 4. SSRF & Network Security Protections ---

def test_ssrf_ip_blocking():
    # Loopback
    assert is_ip_blocked("127.0.0.1") is True
    assert is_ip_blocked("127.0.1.5") is True
    assert is_ip_blocked("::1") is True

    # Private RFC 1918
    assert is_ip_blocked("10.0.0.1") is True
    assert is_ip_blocked("172.16.0.1") is True
    assert is_ip_blocked("192.168.1.1") is True

    # Cloud Metadata
    assert is_ip_blocked("169.254.169.254") is True
    assert is_ip_blocked("169.254.1.1") is True

    # Public safe IPs
    assert is_ip_blocked("8.8.8.8") is False
    assert is_ip_blocked("1.1.1.1") is False
    assert is_ip_blocked("142.250.190.46") is False


def test_validate_hostname_safe_localhost():
    is_safe, reason, ips = validate_hostname_safe("localhost")
    assert is_safe is False
    assert "restricted IP" in reason or "BLOCKED_IP_RANGE" in reason or "SSRF_PREVENTED" in reason


def test_validate_hostname_safe_raw_private_ip():
    is_safe, reason, ips = validate_hostname_safe("192.168.1.1")
    assert is_safe is False
    assert "BLOCKED_IP_RANGE" in reason


# --- 5. Redirect Chain Security Analysis ---

def test_redirect_chain_security_analysis():
    chain = [
        {"step": 1, "url": "https://qr.co/2dt567", "domain": "qr.co"},
        {"step": 2, "url": "http://sbi-fake-portal.xyz/login", "domain": "sbi-fake-portal.xyz"}
    ]
    res = analyze_redirect_chain_security("https://qr.co/2dt567", "http://sbi-fake-portal.xyz/login", chain)
    assert res["domain_changed"] is True
    assert res["https_downgraded"] is True
    assert res["has_suspicious_intermediate"] is True


# --- 6. Live Async Inference Engine & UNKNOWN State ---

@pytest.mark.asyncio
async def test_infer_url_direct_legitimate():
    res = await infer_url_async("https://www.google.com", resolve_live=False)
    assert res["link_status"] == "DIRECT"
    assert res["verdict"]["risk_level"] in ("safe", "low_risk")
    assert res["risk_score"] < 40


@pytest.mark.asyncio
async def test_infer_url_direct_phishing():
    res = await infer_url_async("http://sbi-bank-kyc-verification.xyz/login?token=abc", resolve_live=False)
    assert res["verdict"]["risk_level"] in ("high_risk", "moderate_risk")
    assert res["risk_score"] >= 60


@pytest.mark.asyncio
async def test_infer_url_ssrf_blocked_fails_closed():
    # Attempting to scan loopback must trigger SSRF block and high/critical risk
    res = await infer_url_async("http://127.0.0.1:8000/admin", resolve_live=True)
    assert res["resolution_details"]["status"] == "BLOCKED_SSRF"
    assert res["verdict"]["risk_level"] == "critical"
    assert res["risk_score"] >= 90


@pytest.mark.asyncio
async def test_infer_url_unreachable_destination_becomes_unknown_never_safe():
    # An unreachable domain without lexical phishing signals must NOT default to SAFE -> must be UNKNOWN
    res = await infer_url_async("https://unreachabledomain987654321.org/page", resolve_live=True)
    assert res["resolution_details"]["is_reachable"] is False
    assert res["verdict"]["risk_level"] == "unknown"
    assert res["verdict"]["verdict_status"] == "UNKNOWN / UNVERIFIED"


# --- 7. Full API Endpoint Verification ---

@pytest.mark.asyncio
async def test_api_scan_url_endpoint_enriched_response():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/scan-url", json={"url": "https://www.google.com"})
    assert res.status_code == 200
    data = res.json()
    assert "scan_id" in data
    assert "original_url" in data
    assert "final_url" in data
    assert "url_type" in data
    assert "link_status" in data
    assert "redirect_chain" in data
    assert "risk_score" in data
    assert "verdict" in data
    assert "url_features" in data
    assert len(data["url_features"]) >= 19


@pytest.mark.asyncio
async def test_api_scan_url_endpoint_invalid_input():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.post("/api/v1/detect/scan-url", json={"url": "not-a-valid-url-no-scheme-or-bad"})
    assert res.status_code == 400
    assert res.json()["detail"]["error_code"] == "VALIDATION_ERROR"


# --- 8. Comprehensive Keyword-Bias & Structural Risk Tests ---

@pytest.mark.asyncio
async def test_group_a_same_keyword_no_phishing_bias():
    """
    Test Group A: Legitimate domains with /login path MUST NOT be classified as phishing.
    """
    urls = [
        "https://example.com/login",
        "https://example.org/login",
        "https://example.net/login",
    ]
    for u in urls:
        res = await infer_url_async(u, resolve_live=False)
        assert res["classification"] in ("REAL / LEGITIMATE", "LOW RISK"), f"URL {u} falsely flagged as {res['classification']}"
        assert res["risk_score"] < 40, f"URL {u} risk score too high: {res['risk_score']}"


@pytest.mark.asyncio
async def test_group_b_security_words_no_phishing_bias():
    """
    Test Group B: Legitimate URLs containing security-sensitive keywords (/security, /verify, /account, /secure)
    must NOT be classified as phishing solely due to path words.
    """
    urls = [
        "https://example.com/security",
        "https://example.com/verify",
        "https://example.com/account",
        "https://example.com/secure",
    ]
    for u in urls:
        res = await infer_url_async(u, resolve_live=False)
        assert res["classification"] in ("REAL / LEGITIMATE", "LOW RISK"), f"Security URL {u} falsely classified as {res['classification']}"
        assert res["risk_score"] < 40


@pytest.mark.asyncio
async def test_group_c_structural_risk_detection():
    """
    Test Group C: Structural risk indicators (raw IP, excessive subdomains, brand lookalike domains, suspicious TLDs, entropy)
    must trigger appropriate risk scores based on structure, NOT keywords.
    """
    # 1. Brand typosquatting domain (paypa1-security.com)
    res_brand = await infer_url_async("http://paypa1-security.com/portal", resolve_live=False)
    assert res_brand["url_features"]["is_brand_lookalike"] == 1
    assert res_brand["risk_score"] >= 65

    # 2. Suspicious TLD + excessive subdomains
    res_tld = await infer_url_async("http://portal.auth.client.update-services.xyz/action", resolve_live=False)
    assert res_tld["url_features"]["is_suspicious_tld"] == 1
    assert res_tld["risk_score"] >= 50

    # 3. Direct raw IP address
    res_ip = await infer_url_async("http://203.0.113.10/dashboard", resolve_live=False)
    assert res_ip["url_features"]["has_ip_address"] == 1
    assert res_ip["risk_score"] >= 50


@pytest.mark.asyncio
async def test_group_d_legitimate_complex_urls_with_auth_params():
    """
    Test Group D: Complex legitimate enterprise URLs with authentication/session parameters
    must remain safely classified without false positive alerts.
    """
    complex_urls = [
        "https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin",
        "https://github.com/login?return_to=%2Fsettings%2Fsecurity",
        "https://aws.amazon.com/console/home?region=us-east-1#services",
    ]
    for u in complex_urls:
        res = await infer_url_async(u, resolve_live=False)
        assert res["classification"] in ("REAL / LEGITIMATE", "LOW RISK")
        assert res["risk_score"] < 45

