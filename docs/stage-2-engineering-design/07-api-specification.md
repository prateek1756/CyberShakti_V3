# CyberShakti — API Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-API-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-DB-001, CSHAKTI-SRS-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [API Design Principles](#1-api-design-principles)
2. [Base URL and Versioning](#2-base-url-and-versioning)
3. [Authentication](#3-authentication)
4. [Common Response Formats](#4-common-response-formats)
5. [Authentication Endpoints](#5-authentication-endpoints)
6. [Pillar 1 — Detect & Analyze Endpoints](#6-pillar-1--detect--analyze-endpoints)
7. [Pillar 2 — Protect Endpoints](#7-pillar-2--protect-endpoints)
8. [Pillar 3 — Assist & Respond Endpoints](#8-pillar-3--assist--respond-endpoints)
9. [Pillar 4 — Learn & Prevent Endpoints](#9-pillar-4--learn--prevent-endpoints)
10. [Task Status Endpoints](#10-task-status-endpoints)
11. [User Account Endpoints](#11-user-account-endpoints)
12. [Admin Endpoints](#12-admin-endpoints)
13. [Rate Limiting](#13-rate-limiting)
14. [Error Reference](#14-error-reference)

---

## 1. API Design Principles

1. **REST**: Resources are nouns; HTTP methods express actions
2. **JSON**: All request and response bodies are `application/json` unless explicitly noted (file uploads use `multipart/form-data`)
3. **Versioned**: All endpoints are prefixed `/api/v1/`
4. **Authenticated**: All endpoints except registration, login, password-reset-request, and public content require JWT authentication
5. **Consistent error envelope**: All errors return the same error object structure
6. **No raw user input stored**: API handlers never log or store raw user-submitted text/URLs/files
7. **Status codes are meaningful**: 200 = success, 201 = created, 202 = accepted (async), 400 = bad request, 401 = unauthenticated, 403 = forbidden, 404 = not found, 422 = validation error, 429 = rate limited, 503 = service unavailable

---

## 2. Base URL and Versioning

```
Production:  https://api.cybershakti.in/api/v1
Development: http://localhost:8000/api/v1
```

All endpoints documented below are relative to `/api/v1`.

**Auto-generated OpenAPI documentation:**
- `GET /docs` — Swagger UI (disabled or access-restricted in production)
- `GET /openapi.json` — OpenAPI schema

---

## 3. Authentication

### 3.1 JWT Token Structure

All protected endpoints require a JWT `Bearer` token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

JWT payload (minimum claims):
```json
{
  "sub": "<user_id_uuid>",
  "role": "user",
  "email": "<user_email>",
  "iat": 1724163600,
  "exp": 1724167200,
  "jti": "<unique_token_id>"
}
```

JWT algorithm and expiry values: **TBD pending security benchmarking and threat-model review (ADR-026)**.

### 3.2 Token Refresh

Access tokens are short-lived. Clients use the `/auth/refresh` endpoint with a refresh token (sent as httpOnly cookie or in request body — storage mechanism TBD per security architecture review) to obtain a new access token.

### 3.3 Protected vs. Public Endpoints

| Access Level | Description |
|---|---|
| **Public** | No authentication required |
| **Authenticated** | Valid JWT required (role: user or admin) |
| **Admin** | Valid JWT required with role: admin |

---

## 4. Common Response Formats

### 4.1 Risk Verdict Object

Returned by all detection features (F-01 through F-08):

```json
{
  "risk_level": "high_risk",
  "risk_label": "High Risk",
  "risk_score_raw": 0.8723,
  "verdict_source": "combined",
  "explanation": "This URL contains multiple indicators associated with phishing sites targeting Indian bank customers. The domain was registered recently and uses a subdomain pattern common in credential-harvesting attacks.",
  "scam_category": "bank_phishing",
  "confidence_indicator": "high",
  "is_experimental": false,
  "disclaimer": "This assessment is produced by an automated system and may not detect all threats. Do not rely solely on this verdict. Exercise caution with any suspicious content.",
  "analysed_at": "2026-08-20T15:30:00Z"
}
```

**Field definitions:**

| Field | Type | Values |
|---|---|---|
| `risk_level` | string | `safe`, `low_risk`, `moderate_risk`, `high_risk`, `critical` |
| `risk_label` | string | Human-readable: `Safe`, `Low Risk`, `Moderate Risk`, `High Risk`, `Critical` |
| `risk_score_raw` | float \| null | 0.0–1.0 model probability; null for rule-only verdicts |
| `verdict_source` | string | `threat_intelligence`, `ml_model`, `combined`, `rule_based` |
| `explanation` | string | Non-empty plain-language explanation (always present) |
| `scam_category` | string \| null | Category hint when confidence sufficient; null otherwise |
| `confidence_indicator` | string | `low`, `medium`, `high` — user-facing confidence signal |
| `is_experimental` | boolean | true for F-06, F-07 only |
| `disclaimer` | string | Always present for AI/ML outputs |
| `analysed_at` | ISO 8601 | Timestamp of analysis |

### 4.2 Async Task Response Object

```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "Your request has been queued for analysis. Use the task_id to poll for results.",
  "poll_url": "/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000/status"
}
```

### 4.3 Error Object

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "The submitted URL is not a valid URL format.",
  "details": {
    "field": "url",
    "issue": "invalid_url_format"
  },
  "request_id": "req-abc-123"
}
```

---

## 5. Authentication Endpoints

### 5.1 Register

```
POST /auth/register
Access: Public
```

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "S3cur3P@ssw0rd!",
  "consent_given": true
}
```

**Responses:**

| Status | Meaning | Body |
|---|---|---|
| 201 | Account created; verification email sent | `{ "message": "Registration successful. Check your email to verify your account." }` |
| 400 | `consent_given` is false | Error: `CONSENT_REQUIRED` |
| 422 | Validation error (bad email, weak password format) | Error: `VALIDATION_ERROR` |
| 409 | Email already registered | Error: `EMAIL_ALREADY_EXISTS` — **Note:** Per FR-094, same generic error as other failures to prevent email enumeration. Implementation should return 409 only for internal logic; external response may be normalised to 422 |

**Validation rules:**
- `email`: valid email format, max 320 chars
- `password`: minimum 8 characters (strength assessment is a separate feature, not registration gate — additional format requirements TBD)
- `consent_given`: must be `true`

---

### 5.2 Verify Email

```
GET /auth/verify-email?token=<token>
Access: Public
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Email verified; account activated |
| 400 | Token invalid or expired |
| 409 | Email already verified |

---

### 5.3 Login

```
POST /auth/login
Access: Public
Rate limited: Yes (strict — see §13)
```

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "S3cur3P@ssw0rd!"
}
```

**Response (no 2FA):**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "expires_in": 3600,
  "requires_2fa": false
}
```

**Response (2FA required):**
```json
{
  "requires_2fa": true,
  "two_fa_session_token": "<short_lived_partial_auth_token>",
  "message": "Enter your authenticator code to complete login."
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Login successful |
| 401 | Invalid email or password (generic — never specifies which field) |
| 403 | Email not verified |
| 429 | Rate limit exceeded |

---

### 5.4 Complete 2FA Login

```
POST /auth/login/2fa
Access: Public (requires two_fa_session_token from login step)
Rate limited: Yes
```

**Request body:**
```json
{
  "two_fa_session_token": "<partial_auth_token>",
  "totp_code": "123456"
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | 2FA verified; returns access_token and refresh_token |
| 401 | Invalid TOTP code or session token |
| 410 | Session token expired |

---

### 5.5 Refresh Access Token

```
POST /auth/refresh
Access: Authenticated (refresh token required)
```

**Request body:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Returns new access_token |
| 401 | Invalid or expired refresh token |

---

### 5.6 Logout

```
POST /auth/logout
Access: Authenticated
```

**Request body:**
```json
{
  "refresh_token": "<refresh_token>"
}
```

Revokes the refresh token. Access tokens cannot be revoked (short-lived by design).

---

### 5.7 Request Password Reset

```
POST /auth/password-reset/request
Access: Public
Rate limited: Yes
```

**Request body:**
```json
{
  "email": "user@example.com"
}
```

**Always returns 200** regardless of whether the email is registered (prevents account enumeration — FR-094).

---

### 5.8 Complete Password Reset

```
POST /auth/password-reset/complete
Access: Public
```

**Request body:**
```json
{
  "token": "<reset_token_from_email>",
  "new_password": "NewS3cur3P@ss!"
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Password changed; all sessions invalidated (FR-102) |
| 400 | Token invalid, expired, or already used |
| 422 | Validation error (weak password) |

---

### 5.9 Enroll TOTP 2FA

```
POST /auth/2fa/enroll
Access: Authenticated
```

**Response:**
```json
{
  "secret": "<totp_secret_base32>",
  "qr_code_uri": "otpauth://totp/CyberShakti:<email>?secret=<secret>&issuer=CyberShakti",
  "backup_codes": ["code1", "code2", "code3", "code4", "code5", "code6", "code7", "code8"],
  "message": "Save these backup codes securely. They are shown only once."
}
```

**Note:** Enrollment is not confirmed until the user submits a valid TOTP code via `POST /auth/2fa/confirm-enrollment`.

---

### 5.10 Confirm 2FA Enrollment

```
POST /auth/2fa/confirm-enrollment
Access: Authenticated
```

**Request body:**
```json
{
  "totp_code": "123456"
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | 2FA enrollment confirmed; users.totp_enabled = TRUE |
| 401 | Invalid TOTP code |

---

## 6. Pillar 1 — Detect & Analyze Endpoints

### 6.1 Scan URL — F-01 Phishing Link Scanning

```
POST /detect/scan-url
Access: Authenticated
```

**Request body:**
```json
{
  "url": "https://example.com/suspicious-page"
}
```

**Response (synchronous):**
```json
{
  "scan_id": "<uuid>",
  "input": {
    "url_submitted": "https://example.com/suspicious-page",
    "url_normalised": "https://example.com/suspicious-page"
  },
  "verdict": { /* Risk Verdict Object — see §4.1 */ },
  "url_features": {
    "domain_age_days": null,
    "is_known_brand_lookalike": true,
    "uses_ip_address": false,
    "subdomain_depth": 2,
    "has_suspicious_tld": false
  }
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Scan complete; verdict returned |
| 400 | Input is not a valid URL format |
| 401 | Unauthenticated |
| 422 | Validation error |
| 503 | Threat intelligence service unavailable (fallback to ML-only indicated in response) |

**Notes:**
- `url_features` provides transparency into what signals influenced the verdict
- `domain_age_days` may be null if WHOIS lookup is not available
- Verdict returned synchronously for Phase 1 (may shift to async if latency is unacceptable after benchmarking)

---

### 6.2 Scan Message — F-02 Message & Email Scam Detection

```
POST /detect/scan-message
Access: Authenticated
```

**Request body:**
```json
{
  "text": "Dear customer, your bank account will be suspended. Click here to update KYC: http://bit.ly/kyc-update-xyz"
}
```

**Response:**
```json
{
  "scan_id": "<uuid>",
  "input": {
    "text_length": 112,
    "language_detected": "en",
    "language_note": null
  },
  "verdict": { /* Risk Verdict Object */ },
  "scam_indicators": ["urgency_language", "kyc_mention", "shortened_url"]
}
```

**Responses:**

| Status | Meaning |
|---|---|
| 200 | Scan complete |
| 400 | Empty text input |
| 401 | Unauthenticated |
| 422 | Text exceeds maximum length |

**Notes:**
- `language_note` is populated when non-English text is detected (FR-014)
- `scam_indicators` lists detected pattern categories (not raw model features)
- Raw text input is **never logged or stored**; only `text_length` and `language_detected` are recorded

---

### 6.3 Scan Screenshot — F-03 Screenshot Scam Scanner

```
POST /detect/scan-screenshot
Access: Authenticated
Content-Type: multipart/form-data
```

**Request:**
- Field: `file` — image file (JPEG or PNG)
- Max file size: TBD during environment design (FR-017)

**Response (async — returns task reference):**
```json
{
  "task_id": "<uuid>",
  "status": "queued",
  "message": "Screenshot received. Analysis will complete in a few seconds.",
  "poll_url": "/api/v1/tasks/<task_id>/status"
}
```

**Task completion result:**
```json
{
  "task_id": "<uuid>",
  "status": "complete",
  "result": {
    "scan_id": "<uuid>",
    "ocr_result": {
      "text_extracted": "Dear customer, your account is blocked. Call 9999999999",
      "ocr_quality": "good",
      "text_found": true
    },
    "verdict": { /* Risk Verdict Object */ }
  }
}
```

**When no text is found:**
```json
{
  "task_id": "<uuid>",
  "status": "complete",
  "result": {
    "scan_id": "<uuid>",
    "ocr_result": {
      "text_extracted": "",
      "ocr_quality": "low",
      "text_found": false
    },
    "no_text_message": "No readable text was found in this screenshot. Cannot perform scam analysis.",
    "verdict": null
  }
}
```

---

### 6.4 Scan QR Code — F-04 QR Code Scam Scanner

```
POST /detect/scan-qr
Access: Authenticated
Content-Type: multipart/form-data
```

**Request:**
- Field: `file` — QR code image

**Response (synchronous):**
```json
{
  "scan_id": "<uuid>",
  "qr_result": {
    "decoded_content": "https://upi-payment-xyz.in/collect?vpa=fraud@ybl",
    "content_type": "url",
    "is_readable": true
  },
  "verdict": { /* Risk Verdict Object — from F-01 pipeline */ }
}
```

**Non-URL QR content:**
```json
{
  "scan_id": "<uuid>",
  "qr_result": {
    "decoded_content": "BEGIN:VCARD\nFN:John Doe\n...",
    "content_type": "vcard",
    "is_readable": true
  },
  "verdict": null,
  "non_url_message": "This QR code contains contact information (vCard). No URL was found to analyse."
}
```

**Unreadable QR:**
```json
{
  "error_code": "QR_DECODE_FAILED",
  "message": "The uploaded image does not contain a readable QR code.",
  "details": null
}
```

---

### 6.5 Assess Fake Profile — F-05 Fake Profile Verification

```
POST /detect/assess-profile
Access: Authenticated
```

**Request body:**
```json
{
  "signals": {
    "profile_url": "https://www.instagram.com/suspicious_profile",
    "account_age_category": "less_than_1_month",
    "follower_count_range": "0_to_50",
    "following_to_follower_ratio_high": true,
    "has_profile_photo": true,
    "profile_photo_appears_generic": true,
    "bio_present": false,
    "posts_count_range": "0_to_5",
    "sent_unsolicited_money_request": true,
    "claims_celebrity_or_official": false,
    "platform": "instagram"
  }
}
```

**Response (async):**
```json
{
  "task_id": "<uuid>",
  "status": "queued",
  "poll_url": "/api/v1/tasks/<task_id>/status"
}
```

**Task result:**
```json
{
  "scan_id": "<uuid>",
  "identity_verification_disclaimer": "CyberShakti does not verify identities. This assessment evaluates observable risk signals only. A low-risk result does not confirm that a profile is genuine.",
  "signals_evaluated": 8,
  "verdict": { /* Risk Verdict Object */ }
}
```

---

### 6.6 Detect Deepfake — F-06 (Research/Experimental)

```
POST /detect/analyze-media-deepfake
Access: Authenticated
Content-Type: multipart/form-data
```

**Request:**
- Field: `file` — image (JPEG, PNG) or short video (MP4, max duration TBD)
- Max file size: TBD

**Response (async):**
```json
{
  "task_id": "<uuid>",
  "status": "queued",
  "experimental_disclaimer": "Deepfake detection is an experimental research feature. Results are indicative only and should not be used as definitive evidence of manipulation. False positives and false negatives occur.",
  "poll_url": "/api/v1/tasks/<task_id>/status"
}
```

**Task result:**
```json
{
  "scan_id": "<uuid>",
  "media_analysis": {
    "faces_detected": 1,
    "media_type": "image"
  },
  "verdict": { /* Risk Verdict Object — is_experimental: true */ },
  "experimental_disclaimer": "..."
}
```

---

### 6.7 Assess Mule Account — F-07 (Research/Experimental)

```
POST /detect/assess-mule-account
Access: Authenticated
```

**Request body:**
```json
{
  "account_signals": {
    "account_age_category": "less_than_3_months",
    "transaction_velocity_high": true,
    "multiple_recipients": true,
    "round_amount_transfers": true,
    "cross_bank_transfers_high": false,
    "account_used_for_receiving_then_forwarding": true
  }
}
```

**Response (async):**
Returns task reference with all three mandatory disclaimers.

---

## 7. Pillar 2 — Protect Endpoints

### 7.1 Check Phone Number — F-08 Scam Call Blocking

```
POST /protect/check-phone
Access: Authenticated
```

**Request body:**
```json
{
  "phone_number": "9876543210"
}
```

**Phone number formats accepted:**
- `9876543210` (10-digit)
- `+919876543210` (+91 prefix)
- `09876543210` (0 prefix)

**Response:**
```json
{
  "lookup_id": "<uuid>",
  "phone_number_normalised": "+919876543210",
  "is_emergency_service": false,
  "verdict": {
    "risk_level": "high_risk",
    "risk_label": "High Risk",
    "explanation": "This number has been reported multiple times as associated with fraudulent calls impersonating bank officials.",
    "data_source": "threat_intelligence_api",
    "data_freshness": "2026-08-18T10:00:00Z",
    "absence_of_data_note": null,
    "disclaimer": "Phone number risk data is sourced from community reports and threat intelligence. The absence of a threat record does not confirm that a number is safe."
  }
}
```

**Emergency service response:**
```json
{
  "lookup_id": "<uuid>",
  "phone_number_normalised": "112",
  "is_emergency_service": true,
  "emergency_service_name": "National Emergency Number",
  "message": "This is an emergency service number. No risk assessment is performed for emergency numbers.",
  "verdict": null
}
```

**No data response:**
```json
{
  "verdict": {
    "risk_level": "safe",
    "explanation": "No threat reports found for this number in our database.",
    "absence_of_data_note": "The absence of threat data for a number does not confirm that it is safe. Exercise caution with unexpected calls.",
    "data_source": "threat_intelligence_api"
  }
}
```

---

### 7.2 Check Password Strength — F-09 Password Security Checker

```
POST /protect/check-password
Access: Authenticated
```

**Request body:**
```json
{
  "password": "MyP@ssw0rd"
}
```

**Response:**
```json
{
  "verdict": {
    "strength_level": "moderate",
    "strength_label": "Moderate",
    "entropy_bits": 42.3,
    "length": 10,
    "has_uppercase": true,
    "has_lowercase": true,
    "has_numbers": true,
    "has_symbols": true,
    "is_common_password": false,
    "is_in_breach_list": false,
    "improvements": [
      "Increase length to at least 14 characters for stronger protection.",
      "Avoid predictable letter-to-symbol substitutions (e.g., @ for a, 0 for o)."
    ],
    "disclaimer": "Do not enter your actual account passwords here. This checker is for assessment purposes only."
  }
}
```

**Security note:** The password value is **never logged, stored, or transmitted beyond the assessment endpoint**. The response includes strength indicators and recommendations only.

**Strength levels:** `very_weak`, `weak`, `moderate`, `strong`, `very_strong`

---

### 7.3 Encrypt File — F-10 Secure File Encryption

```
POST /protect/encrypt-file
Access: Authenticated
Content-Type: multipart/form-data
```

**Request:**
- Field: `file` — file to encrypt (max size TBD)
- Field: `password` — encryption password (non-empty string)

**Response:** Encrypted file returned as binary stream for direct download.

```
HTTP 200 OK
Content-Type: application/octet-stream
Content-Disposition: attachment; filename="original_filename.enc"
```

**Error responses:**

| Status | Error Code | Meaning |
|---|---|---|
| 400 | `EMPTY_PASSWORD` | Password field is empty |
| 413 | `FILE_TOO_LARGE` | File exceeds size limit |
| 415 | `UNSUPPORTED_FILE_TYPE` | File type not permitted (TBD) |
| 500 | `ENCRYPTION_FAILED` | Internal encryption error |

---

### 7.4 Decrypt File — F-10 Secure File Encryption (Decrypt)

```
POST /protect/decrypt-file
Access: Authenticated
Content-Type: multipart/form-data
```

**Request:**
- Field: `file` — encrypted `.enc` file
- Field: `password` — decryption password

**Response on success:** Original file returned as binary stream.

**Error responses:**

| Status | Error Code | Meaning |
|---|---|---|
| 400 | `WRONG_PASSWORD` | Decryption failed — incorrect password or corrupted file |
| 400 | `INVALID_ENCRYPTED_FILE` | File does not appear to be a CyberShakti-encrypted file |

---

## 8. Pillar 3 — Assist & Respond Endpoints

### 8.1 Query AI Assistant — F-11

```
POST /assist/query-assistant
Access: Authenticated
```

**Request body:**
```json
{
  "query": "I received a WhatsApp message saying I won a lottery. Is this a scam?",
  "conversation_id": null
}
```

`conversation_id` is null for a new conversation; use the returned ID for follow-up messages.

**Response (async):**
```json
{
  "task_id": "<uuid>",
  "conversation_id": "<uuid>",
  "poll_url": "/api/v1/tasks/<task_id>/status"
}
```

**Task result:**
```json
{
  "conversation_id": "<uuid>",
  "message_id": "<uuid>",
  "response": "Yes, this is almost certainly a lottery scam...",
  "knowledge_sources": [
    {
      "document_title": "Lottery and Prize Scam Awareness Guide",
      "relevance": "high"
    }
  ],
  "ai_disclaimer": "This response is generated by an AI assistant and is grounded in CyberShakti's knowledge base. It is for informational purposes only and should not replace advice from cybersecurity professionals, law enforcement, or legal counsel.",
  "is_out_of_scope": false,
  "out_of_scope_message": null
}
```

**Feature availability:** F-11 endpoint returns HTTP 503 with `error_code: FEATURE_NOT_YET_AVAILABLE` if LLM provider is not configured (FR-071, ADR-013).

---

### 8.2 Get Cyber Risk Score — F-12

```
GET /assist/risk-score
Access: Authenticated
```

**Response:**
```json
{
  "score": 62,
  "score_band": "moderate",
  "score_band_label": "Moderate Risk",
  "computed_at": "2026-08-20T15:00:00Z",
  "signal_breakdown": [
    {
      "signal_name": "recent_high_risk_scans",
      "label": "High-risk threats detected recently",
      "contribution_direction": "negative",
      "description": "You have encountered high-risk threats in the past 7 days."
    },
    {
      "signal_name": "password_strength_checked",
      "label": "Password security checked",
      "contribution_direction": "positive",
      "description": "You have used the Password Security Checker."
    }
  ],
  "improvement_actions": [
    "Check your most frequently used passwords with the Password Security Checker.",
    "Enable two-factor authentication (2FA) on your bank and UPI apps."
  ],
  "disclaimer": "Your Cyber Risk Score is based on your activity within CyberShakti and self-reported security posture indicators. It is an estimate, not a comprehensive security audit.",
  "is_baseline": false,
  "onboarding_prompt": null
}
```

---

### 8.3 Update Risk Score Questionnaire — F-12

```
POST /assist/risk-score/questionnaire
Access: Authenticated
```

**Request body:**
```json
{
  "responses": {
    "uses_2fa_on_bank_apps": true,
    "reuses_passwords": false,
    "shares_otp_with_others": false,
    "uses_public_wifi_for_banking": null
  }
}
```

`null` for a question means "prefer not to answer" — it does not contribute to the score.

---

### 8.4 Get Location Scam Alerts — F-13

```
GET /assist/scam-alerts?city=Mumbai&state=Maharashtra
Access: Authenticated
```

**Or with coordinates (city-level precision, explicit consent required before first use):**

```
GET /assist/scam-alerts?lat=19.0760&lng=72.8777&precision=city
```

**Response:**
```json
{
  "location": {
    "resolved_location": "Mumbai, Maharashtra",
    "precision": "city"
  },
  "alerts": [
    {
      "alert_id": "<uuid>",
      "title": "Fraudulent UPI Collect Requests Targeting Mumbai Residents",
      "description": "Multiple reports of fake UPI collect requests impersonating electricity board officials...",
      "alert_type": "upi_fraud",
      "severity": "high_risk",
      "severity_label": "High Risk",
      "published_at": "2026-08-18T10:00:00Z",
      "source": "CERT-In Advisory",
      "source_url": "https://cert-in.org.in/..."
    }
  ],
  "total_alerts": 1,
  "last_updated": "2026-08-20T08:00:00Z",
  "data_disclaimer": "Alert data is sourced from publicly reported incidents and official advisories. Coverage may be incomplete. Always verify alerts from official sources.",
  "no_alerts_message": null
}
```

**No alerts for location:**
```json
{
  "alerts": [],
  "total_alerts": 0,
  "no_alerts_message": "No recent scam alerts found for your area. Stay alert — absence of alerts does not mean no threats exist.",
  "last_updated": "2026-08-20T08:00:00Z"
}
```

---

## 9. Pillar 4 — Learn & Prevent Endpoints

### 9.1 Get Daily Safety Tip — F-14

```
GET /learn/daily-tip
Access: Public (or Authenticated — TBD)
```

**Response:**
```json
{
  "tip_id": "<uuid>",
  "tip_text": "Never share OTPs with anyone — not even bank officials. Genuine banks will never ask for your OTP over a call.",
  "category": "otp_security",
  "date": "2026-08-20"
}
```

---

### 9.2 Get Quiz Questions — F-14

```
GET /learn/quiz?count=10&category=all
Access: Authenticated
```

**Response:**
```json
{
  "quiz_id": "<uuid>",
  "questions": [
    {
      "question_id": "<uuid>",
      "question_text": "A caller claiming to be from your bank asks for your UPI PIN to 'verify your account'. What should you do?",
      "category": "upi_fraud",
      "options": [
        { "option_id": "<uuid>", "text": "Share the PIN — it's your bank calling" },
        { "option_id": "<uuid>", "text": "Hang up and call your bank's official number" },
        { "option_id": "<uuid>", "text": "Ask them to send an email instead" },
        { "option_id": "<uuid>", "text": "Share only the last 4 digits" }
      ]
    }
  ]
}
```

---

### 9.3 Submit Quiz Answer — F-14

```
POST /learn/quiz/submit-answer
Access: Authenticated
```

**Request body:**
```json
{
  "question_id": "<uuid>",
  "selected_option_id": "<uuid>"
}
```

**Response:**
```json
{
  "is_correct": true,
  "correct_option_id": "<uuid>",
  "explanation": "Genuine banks and financial institutions will never ask for your UPI PIN, password, or OTP. Hang up and contact your bank via their official verified number."
}
```

---

### 9.4 List Articles — F-14

```
GET /learn/articles?category=whatsapp_scam&page=1&per_page=10
Access: Public
```

---

### 9.5 Get Article — F-14

```
GET /learn/articles/{slug}
Access: Public
```

---

## 10. Task Status Endpoints

### 10.1 Poll Task Status

```
GET /tasks/{task_id}/status
Access: Authenticated (only the submitting user may poll their own tasks)
```

**Response (queued):**
```json
{
  "task_id": "<uuid>",
  "status": "queued",
  "message": "Your request is waiting to be processed."
}
```

**Response (processing):**
```json
{
  "task_id": "<uuid>",
  "status": "processing",
  "message": "Analysis is in progress."
}
```

**Response (complete):**
```json
{
  "task_id": "<uuid>",
  "status": "complete",
  "result": { /* Feature-specific result object */ }
}
```

**Response (error):**
```json
{
  "task_id": "<uuid>",
  "status": "error",
  "error_code": "OCR_PROCESSING_FAILED",
  "message": "Text extraction from the screenshot failed. Please try again with a clearer image."
}
```

---

## 11. User Account Endpoints

### 11.1 Get Current User Profile

```
GET /users/me
Access: Authenticated
```

**Response:**
```json
{
  "user_id": "<uuid>",
  "email": "user@example.com",
  "email_verified": true,
  "totp_enabled": false,
  "created_at": "2026-07-01T10:00:00Z",
  "role": "user"
}
```

---

### 11.2 Delete Account

```
DELETE /users/me
Access: Authenticated
```

**Request body:**
```json
{
  "password": "CurrentP@ssword",
  "confirmation": "DELETE MY ACCOUNT"
}
```

Requires password re-entry AND typed confirmation string (FR-103). Returns 200 on success; triggers PII purge process per retention schedule.

---

## 12. Admin Endpoints

Admin endpoints are accessible only to users with `role: admin` JWT claim. All admin endpoints return HTTP 403 for non-admin tokens.

| Endpoint | Method | Purpose |
|---|---|---|
| `/admin/users` | GET | List users (paginated) |
| `/admin/users/{user_id}` | GET | Get user details |
| `/admin/users/{user_id}/deactivate` | POST | Deactivate a user account |
| `/admin/scam-alerts` | POST | Create a new scam alert |
| `/admin/scam-alerts/{alert_id}` | PUT | Update a scam alert |
| `/admin/scam-alerts/{alert_id}` | DELETE | Deactivate a scam alert |
| `/admin/knowledge-base/documents` | POST | Add a knowledge base document |
| `/admin/knowledge-base/documents/{doc_id}` | DELETE | Retire a knowledge base document |
| `/admin/audit-log` | GET | Query the audit log (paginated) |
| `/admin/content/tips` | POST | Add a safety tip |
| `/admin/content/articles` | POST | Create an article |

Full admin endpoint specifications will be detailed in a separate Admin API addendum during implementation.

---

## 13. Rate Limiting

Rate limiting is applied to all public-facing endpoints. Specific thresholds are TBD pending security benchmarking and threat-model review (ADR-026, NFR-SEC-005).

| Endpoint Category | Sensitivity | Rate Limit Strictness |
|---|---|---|
| `POST /auth/login` | High | Strictest — brute-force risk |
| `POST /auth/register` | Medium-High | Strict — abuse prevention |
| `POST /auth/password-reset/request` | Medium | Moderate — email abuse risk |
| `POST /auth/2fa/` | High | Strict — account takeover risk |
| Detection scan endpoints | Medium | Per-user and global limits |
| `POST /protect/encrypt-file`, `decrypt-file` | Medium | Per-user limits |
| `GET /learn/` content endpoints | Low | Liberal |
| `GET /assist/risk-score` | Low | Liberal |

**Rate limit response:**
```
HTTP 429 Too Many Requests
Retry-After: 60
```

```json
{
  "error_code": "RATE_LIMIT_EXCEEDED",
  "message": "Too many requests. Please wait before trying again.",
  "retry_after_seconds": 60
}
```

---

## 14. Error Reference

| Error Code | HTTP Status | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Input validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | No or invalid JWT |
| `TOKEN_EXPIRED` | 401 | JWT has expired |
| `FORBIDDEN` | 403 | Insufficient role |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `CONSENT_REQUIRED` | 400 | Registration consent not given |
| `EMAIL_ALREADY_EXISTS` | 409 | Duplicate email at registration |
| `EMAIL_NOT_VERIFIED` | 403 | Login before email verification |
| `INVALID_CREDENTIALS` | 401 | Wrong email or password |
| `INVALID_TOTP_CODE` | 401 | Wrong 2FA code |
| `TOKEN_INVALID` | 400 | Reset/verify token is invalid or expired |
| `EMPTY_PASSWORD` | 400 | Encryption/check password empty |
| `FILE_TOO_LARGE` | 413 | Upload exceeds size limit |
| `UNSUPPORTED_FILE_TYPE` | 415 | File type not accepted |
| `QR_DECODE_FAILED` | 400 | QR code unreadable |
| `OCR_PROCESSING_FAILED` | 422 | Screenshot OCR failed |
| `WRONG_PASSWORD` | 400 | Decryption with wrong password |
| `INVALID_ENCRYPTED_FILE` | 400 | File not in expected encrypted format |
| `FEATURE_NOT_YET_AVAILABLE` | 503 | Feature blocked by unresolved dependency (F-11, ADR-013) |
| `SERVICE_UNAVAILABLE` | 503 | Dependency (DB, Redis, TI API) temporarily unavailable |
| `INSUFFICIENT_SIGNALS` | 422 | F-05, F-07 profile/account signals too sparse |
| `NO_FACE_DETECTED` | 422 | F-06 deepfake — no face in media |
| `EMERGENCY_NUMBER` | 200 | F-08 phone number is an emergency service |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

*End of CyberShakti API Specification — CSHAKTI-API-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
