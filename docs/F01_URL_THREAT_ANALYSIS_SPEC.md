# F-01 Phishing Link Scanner / Real-Time URL Threat Analysis Engine

## 1. Overview & Purpose
**F-01** is a high-speed, multi-stage **Real-Time URL Threat Analysis Engine** engineered for CyberShakti V3. It inspects submitted target URLs (including direct links, shortened links, and QR code targets) at scan time to detect credential harvesting portals, brand impersonation campaigns, malicious forwarding chains, and infrastructure spoofing.

---

## 2. Architecture & Pipeline

```
 USER URL
    │
    ▼
1. URL VALIDATION & NORMALIZATION
    ├─ Rejects non-web schemes (javascript:, data:, file:, ftp:, etc.)
    ├─ Punycode / IDN internationalized domain handling
    └─ Hostname lowercase, trailing dot removal, default port cleanup
    │
    ▼
2. GENERIC URL TYPE DETECTION
    ├─ DIRECT (standard registered domains)
    ├─ SHORTENED (bit.ly, qr.co, tinyurl.com, t.co, rebrand.ly, etc.)
    ├─ IP_BASED (numerical IPv4/IPv6 literals)
    ├─ OBFUSCATED (hex/octal representations, embedded '@', multiple encodings)
    └─ REDIRECTING (query params directing to external target)
    │
    ▼
3. SSRF-SAFE LIVE REDIRECT RESOLVER
    ├─ Pre-request DNS resolution & validation
    ├─ Strict subnet filter (rejects 127.0.0.0/8, RFC 1918, 169.254.0.0/16 cloud metadata, CGNAT, loopbacks)
    ├─ Step-by-step redirect following (max 5 hops, 4.0s timeout)
    ├─ HEAD/GET streaming without downloading massive response payloads
    └─ Multi-hop redirect chain capture with HTTP statuses & timing
    │
    ▼
4. REDIRECT CHAIN SECURITY ANALYSIS
    ├─ Cross-domain forward detection
    ├─ Protocol downgrade detection (HTTPS ➔ insecure HTTP)
    └─ Suspicious intermediate domain tracking
    │
    ▼
5. 19 LEXICAL & STRUCTURAL FEATURE EXTRACTION
    ├─ Exact 19 features preserved in strict training order:
    │  [url_length, domain_length, path_length, num_dots, num_hyphens,
    │   num_underscores, num_at_signs, num_question_marks, num_slashes,
    │   num_digits, digit_to_letter_ratio, has_ip_address, uses_https,
    │   has_port_in_url, url_entropy, subdomain_count, is_shortened_url,
    │   is_suspicious_tld, is_brand_lookalike]
    └─ Evaluated on resolved final destination URL
    │
    ▼
6. MACHINE LEARNING & EXPLAINABILITY (XGBoost + SHAP)
    ├─ Native `xgboost.sklearn.XGBClassifier` probability scoring
    └─ SHAP TreeExplainer ranking mapped to human-readable security reasons
    │
    ▼
7. RISK & DECISION ENGINE
    ├─ Link Status: DIRECT | REDIRECTED | UNKNOWN
    ├─ Security Verdict: REAL / LEGITIMATE | SUSPICIOUS | PHISHING | UNKNOWN
    ├─ Calibrated 0–100 Threat Score
    └─ Fail-closed policy: Unverified/unreachable destinations yield UNKNOWN (never false-SAFE)
```

---

## 3. SSRF & Network Security Protections
Live URL analysis presents severe Server-Side Request Forgery (SSRF) risks if an attacker submits internal endpoints (e.g. `http://169.254.169.254/latest/meta-data` or `http://localhost:8000/admin`).

CyberShakti's resolver implements:
* **DNS Pre-Validation**: Resolves all A/AAAA records for the hostname prior to initiating a connection.
* **Blocked Networks**:
  * `127.0.0.0/8`, `::1` (Loopback)
  * `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `fc00::/7` (Private subnets)
  * `169.254.0.0/16`, `fe80::/10` (Link-local & AWS/GCP cloud metadata)
  * `100.64.0.0/10` (Carrier-Grade NAT)
  * `224.0.0.0/4`, `ff00::/8` (Multicast)
* **Hop-by-hop Re-validation**: Validates every intermediate `Location` header in redirect chains.
* **Fail-Closed on Block**: SSRF attempts immediately terminate and are flagged as `CRITICAL` risk with `blocked_internal_network_ssrf`.

---

## 4. 19 Lexical & Domain Features

| # | Feature Name | Type | Description |
|---|---|---|---|
| 1 | `url_length` | int | Total character length of normalized URL |
| 2 | `domain_length` | int | Hostname character count |
| 3 | `path_length` | int | Path segment character count |
| 4 | `num_dots` | int | Total dot occurrences in URL |
| 5 | `num_hyphens` | int | Hyphen count in hostname |
| 6 | `num_underscores` | int | Underscore count in URL |
| 7 | `num_at_signs` | int | `@` symbol count in URL |
| 8 | `num_question_marks` | int | Query parameter delimiter count |
| 9 | `num_slashes` | int | Forward slash count |
| 10 | `num_digits` | int | Digit count in domain name |
| 11 | `digit_to_letter_ratio` | float | Ratio of digits to alphabetic chars in host |
| 12 | `has_ip_address` | int (0/1) | Flag indicating raw numerical IP host |
| 13 | `uses_https` | int (0/1) | Flag indicating HTTPS protocol usage |
| 14 | `has_port_in_url` | int (0/1) | Non-standard port specified (:8080, etc.) |
| 15 | `url_entropy` | float | Shannon character entropy of URL string |
| 16 | `subdomain_count` | int | Subdomain depth |
| 17 | `is_shortened_url` | int (0/1) | Known URL shortener flag |
| 18 | `is_suspicious_tld` | int (0/1) | High-risk TLD (.xyz, .top, .click, etc.) |
| 19 | `is_brand_lookalike` | int (0/1) | Brand token pattern in non-official domain |

---

## 5. API Schema & Contracts

### Endpoint
`POST /api/v1/detect/scan-url`

### Request Body
```json
{
  "url": "https://qr.co/2dt567"
}
```

### Response Body
```json
{
  "scan_id": "8f3b2d10-e51c-4cf8-8c19-90b9a128ec01",
  "input": {
    "url_submitted": "https://qr.co/2dt567",
    "url_normalised": "https://qr.co/2dt567"
  },
  "original_url": "https://qr.co/2dt567",
  "normalized_url": "https://qr.co/2dt567",
  "final_url": "https://target-portal.com/login",
  "url_type": "SHORTENED",
  "link_status": "REDIRECTED",
  "redirect_status": "REDIRECTED",
  "redirect_count": 1,
  "redirect_chain": [
    {
      "step": 1,
      "url": "https://qr.co/2dt567",
      "status_code": 302,
      "location": "https://target-portal.com/login",
      "domain": "qr.co",
      "ip": "104.18.2.1",
      "duration_ms": 142.3
    }
  ],
  "risk_score": 88,
  "verdict": {
    "risk_level": "high_risk",
    "risk_label": "High Risk",
    "verdict_status": "PHISHING",
    "link_status": "REDIRECTED",
    "explanation": "High risk detected! Strong scam or phishing indicators were identified. Key indicators: brand_impersonation, high_url_entropy.",
    "scam_category": "malicious_url",
    "confidence_indicator": "high",
    "is_experimental": false,
    "disclaimer": "This assessment is produced by an automated system and may not detect all threats.",
    "analysed_at": "2026-08-23T02:30:00.000000+00:00"
  },
  "probability": 0.88,
  "ml_probability": 0.88,
  "explanations": [
    "Detected brand impersonation patterns targeting major institution.",
    "URL shortener forwarded to external domain: target-portal.com"
  ],
  "signals": [
    "brand_impersonation",
    "shortener_redirect_hop",
    "high_url_entropy"
  ],
  "url_features": { ... },
  "analysis_time_ms": 284.5,
  "verdict_source": "ml_model"
}
```

---

## 6. Frontend Features (`PhishingScan.jsx`)
* **Real-time Progressive Stages**: Shows visual step-by-step pipeline execution (`Validating URL`, `Resolving live destination`, `Extracting 19 features`, `Evaluating XGBoost & SHAP`, `Synthesizing verdict`).
* **Link Status vs Security Verdict Distinction**: Clearly separates redirect behavior (Direct / Shortened / Redirected) from threat classification (Real / Suspicious / Phishing / Unknown).
* **Redirect Chain Trace Inspector**: Collapsible interactive trace card showing each hop, status code, resolved IP, and duration in milliseconds.
* **Dual URL Inspection**: Displays both the submitted original URL and the resolved final destination inspected by the ML model.

---

## 7. Limitations & Security Advisory
> **Important Advisory**: No automated security system can guarantee 100% detection of every newly registered malicious URL. CyberShakti combines live destination resolution, network SSRF security guards, 19 structural/lexical indicators, native XGBoost classification, and SHAP explainability to provide high-confidence advisory threat assessments.
