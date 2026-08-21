# CyberShakti — Security Architecture

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-SEC-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-DB-001, CSHAKTI-SRS-001, CSHAKTI-CONST-001 §8 |
| **Governed By** | CSHAKTI-CONST-001 §8, §9, §10 |

---

## Table of Contents

1. [Security Principles](#1-security-principles)
2. [Authentication Architecture](#2-authentication-architecture)
3. [Authorisation Architecture](#3-authorisation-architecture)
4. [Transport Security](#4-transport-security)
5. [Input Validation and Sanitisation](#5-input-validation-and-sanitisation)
6. [Rate Limiting and Abuse Prevention](#6-rate-limiting-and-abuse-prevention)
7. [Password and Key Security](#7-password-and-key-security)
8. [File Encryption Architecture (F-10)](#8-file-encryption-architecture-f-10)
9. [Data Protection at Rest](#9-data-protection-at-rest)
10. [API Security](#10-api-security)
11. [Secrets Management](#11-secrets-management)
12. [Logging and Audit](#12-logging-and-audit)
13. [Error Handling Security](#13-error-handling-security)
14. [Dependency and Supply Chain Security](#14-dependency-and-supply-chain-security)
15. [Security Configuration Parameters (TBD)](#15-security-configuration-parameters-tbd)

---

## 1. Security Principles

CyberShakti is a cybersecurity platform. Its security must be held to a higher standard than a typical consumer web application. The governing security principles are defined in CSHAKTI-CONST-001 §8.

**Non-negotiable security requirements:**
1. Plaintext password storage is **prohibited under all circumstances** (CSHAKTI-CONST-001 §8.2)
2. All communications use HTTPS (TLS 1.2 minimum, 1.3 preferred) (CSHAKTI-CONST-001 §8.7)
3. All user inputs are validated and sanitised before processing (CSHAKTI-CONST-001 §8.8)
4. Rate limiting is applied to all public-facing endpoints (CSHAKTI-CONST-001 §8.9)
5. CORS wildcard (`*`) is prohibited in production (CSHAKTI-CONST-001 §8.10)
6. All security configuration parameters not yet determined must be resolved through benchmarking before production (CSHAKTI-CONST-001 §8.12, ADR-026)
7. All security decisions must be defensible and documented — security by obscurity is not acceptable (CSHAKTI-CONST-001 §10)

---

## 2. Authentication Architecture

### 2.1 Authentication Method

**Email + password + optional TOTP 2FA** (ADR-019)

### 2.2 Password Hashing

Passwords are stored as **Argon2id** hashes. Plaintext passwords are never stored, logged, cached, or transmitted beyond the authentication endpoint.

Argon2id configuration parameters (memory cost, time cost, parallelism) are **TBD pending security benchmarking** (ADR-026, CSHAKTI-CONST-001 §8.4). These values must be determined through:
- Benchmarking on target hardware (target: hash computation time 100–500ms on server hardware — industry guidance)
- Threat-model review of attack scenarios

Interim development values must not be carried into production without this review.

### 2.3 JWT Token Architecture

| Token Type | Purpose | Expiry | Storage |
|---|---|---|---|
| Access token | API authentication | Short-lived (TBD — ADR-026) | Client-side (storage method TBD) |
| Refresh token | Obtain new access tokens | Longer-lived (TBD — ADR-026) | httpOnly cookie preferred (reduces XSS risk) |

**JWT algorithm:** TBD — RS256 (asymmetric, preferred for stateless validation across services) or HS256 (symmetric, simpler for single-service) — to be decided during security review (ADR-026).

**JWT claims:**
```json
{
  "sub": "<user_uuid>",
  "role": "<user|admin>",
  "email": "<user_email>",
  "iat": <issued_at_unix>,
  "exp": <expiry_unix>,
  "jti": "<unique_token_id>"
}
```

`jti` (JWT ID) enables token blacklisting/revocation if implemented. Refresh token rotation is recommended.

### 2.4 TOTP 2FA Architecture

- **Algorithm:** TOTP (RFC 6238), SHA-1, 6 digits, 30-second window
- **TOTP secret:** Stored in `totp_secrets` table; **must be encrypted at rest** (column-level or application-layer encryption)
- **QR code:** Generated server-side as a `otpauth://totp/...` URI; QR image rendered client-side
- **Backup codes:** 8 codes generated at enrollment; each stored as an Argon2id hash in `backup_codes` table; displayed to user once only (FR-100)
- **Verification window:** Accept ±1 time step (30s tolerance for clock drift)

### 2.5 Session Management

- Access token expiry causes re-authentication via refresh token
- Refresh token rotation: each use of a refresh token issues a new refresh token and invalidates the old one (reduces refresh token theft risk)
- All tokens invalidated on: password change (FR-102), account deletion, explicit logout
- Partial authentication session (two_fa_session_token): short-lived (< 5 minutes), single-use, stored as a hash

### 2.6 Account Takeover Mitigations

| Attack | Mitigation |
|---|---|
| Credential stuffing | Rate limiting on login; account lockout after N failures (N TBD) |
| Password spray | Rate limiting per IP and per account |
| Token theft | Short-lived access tokens; httpOnly cookie for refresh token (XSS barrier) |
| TOTP bypass | TOTP enforced server-side; backup codes hashed; timing-safe TOTP comparison |
| Email enumeration | Generic error messages for registration and password reset (FR-094, FR-097) |

---

## 3. Authorisation Architecture

### 3.1 RBAC Model

Role-Based Access Control (RBAC) with two roles (ADR-019):

| Role | Access |
|---|---|
| `user` | Access own account, own scan results, own risk score, all public features |
| `admin` | All user access + admin endpoints (user management, content management, audit log, scam alert management) |

### 3.2 Enforcement

RBAC is enforced at the FastAPI middleware level using a decorator/dependency pattern:

```python
# Example FastAPI dependency
from app.shared.auth import require_role

@router.get("/admin/users", dependencies=[Depends(require_role("admin"))])
async def list_users():
    ...
```

Every route that requires a specific role uses this dependency. Missing this dependency on a route is a security defect detectable by security testing.

### 3.3 Object-Level Authorisation

Users may only access their own resources:
- Scan results: `scan_results.user_id` must match authenticated user's `sub` claim
- Risk score: computed for authenticated user only
- Task results: `task_id` is checked against the submitting user's identity
- Conversation history: `conversations.user_id` must match

No user may access another user's data via the API.

---

## 4. Transport Security

### 4.1 HTTPS Requirements

- All production traffic over HTTPS
- TLS 1.2 minimum; TLS 1.3 preferred (CSHAKTI-CONST-001 §8.7)
- HTTP requests redirected to HTTPS (301 redirect at reverse proxy level)
- HSTS (HTTP Strict Transport Security) header enabled with appropriate `max-age`

### 4.2 TLS Configuration

TLS is terminated at the load balancer / reverse proxy level. Recommended cipher suites align with current Mozilla SSL Configuration Generator guidance (Intermediate or Modern profile).

### 4.3 Certificate Management

- TLS certificates: managed by deployment platform (Vercel handles frontend; backend platform handles API)
- Certificate expiry monitoring: alerting when certificate expires within 30 days

### 4.4 CORS Configuration

```python
# Allowed origins — restrictive list, no wildcard
ALLOWED_ORIGINS = [
    "https://cybershakti.in",          # Production frontend
    "https://www.cybershakti.in",      # Production frontend (www)
    "http://localhost:5173",           # Development only
]
```

`*` wildcard origin is **prohibited in production** (CSHAKTI-CONST-001 §8.10).

CORS is configured for API responses only; the frontend SPA is served by Vercel's CDN (no CORS needed for static assets).

---

## 5. Input Validation and Sanitisation

### 5.1 Validation Framework

All API inputs are validated by Pydantic v2 schemas before reaching route handlers. Pydantic validation enforces:
- Type correctness
- Field presence/optionality
- String length limits
- Pattern matching (email format, URL format, phone number format)
- Numeric range constraints

### 5.2 Validation Rules by Input Type

| Input Type | Validation |
|---|---|
| URL (F-01, F-04) | Must parse as valid URL; max 2048 chars; scheme must be http or https |
| Text (F-02) | Non-empty; max 5000 chars; unicode normalised |
| Image file (F-03, F-04, F-06) | MIME type verification (not just extension); max size TBD; antivirus scan deferred |
| Phone number (F-08) | 10-digit Indian format or +91 prefix; digits only |
| Password (F-09) | Non-empty; max 1000 chars (to prevent DoS via Argon2id on huge input) |
| File for encryption (F-10) | Max size TBD; file type allowlist or blocklist TBD |
| Email (auth) | RFC 5322 format; max 320 chars; lowercase normalised |
| Registration password | Non-empty; minimum 8 chars; max 128 chars |

### 5.3 Injection Prevention

| Injection Type | Prevention |
|---|---|
| SQL injection | Parameterised queries via SQLAlchemy ORM / asyncpg — no raw string concatenation |
| NoSQL injection | Not applicable (no MongoDB or similar) |
| Command injection | No shell commands are executed from user input |
| Path traversal | File access is through S3 object paths (not filesystem paths) with user-controlled naming prohibited |
| XSS | Frontend uses React's automatic HTML escaping; API returns JSON (not HTML); `Content-Type: application/json` |
| Template injection | No server-side templating with user input |
| SSRF | URL submissions are not fetched by the server in Phase 1 (URL is analysed locally, not fetched) — this eliminates the primary SSRF risk for F-01 |

### 5.4 File Upload Security

- MIME type validation: verify MIME type from file content (magic bytes), not file extension
- Maximum file size enforced before processing
- Files stored temporarily in S3 under non-guessable paths
- Files deleted from S3 after processing
- No file execution — uploaded files are never executed by the server
- Malware scanning: deferred to a future phase (considered a desirable enhancement)

---

## 6. Rate Limiting and Abuse Prevention

### 6.1 Rate Limiting Strategy

Rate limiting is implemented at the FastAPI middleware layer using a configurable rate limiter (e.g., `slowapi` library backed by Redis).

Two limiting dimensions:
1. **Per IP address:** Prevents unauthenticated abuse
2. **Per user ID:** Prevents authenticated abuse by a single account

### 6.2 Rate Limit Thresholds

All specific thresholds are **TBD pending security benchmarking and threat-model review** (ADR-026, NFR-SEC-005). The categories below represent the tiering structure:

| Endpoint Category | Throttle Tier | Rationale |
|---|---|---|
| `POST /auth/login` | Very strict | Brute-force credential stuffing |
| `POST /auth/register` | Strict | Account creation abuse |
| `POST /auth/password-reset/request` | Strict | Email flooding |
| 2FA endpoints | Strict | Account takeover prevention |
| Detection scan endpoints | Moderate | Resource consumption |
| File upload endpoints | Moderate | Storage and compute abuse |
| Content endpoints (GET /learn/) | Liberal | Public content; low abuse risk |

### 6.3 Lockout Behaviour

After exceeding the login rate limit:
- Temporary IP block (duration TBD)
- Account-level lockout is an additional option (requires careful design to avoid denial-of-service on legitimate users)
- `Retry-After` header indicates wait time

### 6.4 Suspicious Activity Detection

Audit log patterns that should trigger alerts (monitoring — not automated blocking in Phase 1):
- Multiple failed login attempts from same IP within short window
- Registration of many accounts from same IP
- Unusual volume of high-rate-limit endpoint calls

---

## 7. Password and Key Security

### 7.1 User Password Storage

Argon2id hash only. Configuration TBD (ADR-026). Implementation uses `argon2-cffi` Python library.

### 7.2 Password-Derived Key Generation (F-10)

For file encryption key derivation from user-supplied password:
- Algorithm: Argon2id
- Parameters: TBD (ADR-026) — must be tuned for server-side KDF use case (faster than password hashing to avoid DoS, but still resistant to GPU attacks)
- Output key length: 256 bits (32 bytes) for AES-256-GCM key

### 7.3 TOTP Secret Protection

TOTP secrets in `totp_secrets.secret` column are sensitive cryptographic material.

> **Decision Status: PENDING** — Application-layer encryption vs. database column-level encryption must be decided during implementation. The chosen approach must be documented as an ADR update to ADR-026.

### 7.4 JWT Signing Keys

- JWT signing key must never be stored in source code or committed to Git
- Key is loaded from environment variable at startup
- If RS256 is selected: private key stored as environment variable (base64-encoded PEM); public key may be exposed via JWKS endpoint for verification

---

## 8. File Encryption Architecture (F-10)

### 8.1 Encryption Algorithm

**AES-256-GCM** (Authenticated Encryption with Associated Data) — ADR-021.

AES-256-GCM provides:
- **Confidentiality**: 256-bit AES key prevents brute-force decryption
- **Integrity and authenticity**: 128-bit authentication tag detects file tampering
- **AEAD**: Additional authenticated data can be used for metadata binding

### 8.2 Nonce (IV) Management

Critical security requirement: **nonces must never be reused with the same key.**

Implementation:
- Generate a cryptographically random 96-bit (12-byte) nonce per encryption operation
- Store the nonce prepended to the ciphertext in the output file
- Never reuse a nonce; never use a counter-based nonce without careful overflow management

### 8.3 Encrypted File Format

```
[MAGIC_BYTES: 8 bytes] [VERSION: 1 byte] [NONCE: 12 bytes] [SALT: 32 bytes] [CIPHERTEXT: N bytes] [AUTH_TAG: 16 bytes]
```

Where:
- `MAGIC_BYTES`: fixed identifier to recognise CyberShakti-encrypted files
- `VERSION`: format version (for future compatibility)
- `NONCE`: random per-encryption nonce
- `SALT`: random per-encryption salt for Argon2id KDF
- `CIPHERTEXT`: encrypted file content
- `AUTH_TAG`: GCM authentication tag (appended by AES-GCM)

### 8.4 Key Derivation

```
encryption_key = Argon2id(
    password = user_supplied_password,
    salt = random_32_byte_salt,    # per-encryption, stored in file header
    memory_cost = TBD,
    time_cost = TBD,
    parallelism = TBD,
    hash_len = 32                  # 256-bit key
)
```

### 8.5 Server-Side Security

- Plaintext file content is **never written to disk** (processed in memory or as a stream)
- After encryption, the encrypted output is returned directly to the client
- No encrypted or plaintext file is stored persistently by the server beyond the response
- Password value is **never logged, cached, or stored**

---

## 9. Data Protection at Rest

### 9.1 PostgreSQL at Rest

- Full database encryption at rest: depends on deployment platform's disk encryption capability (TBD — ADR-004)
- Minimum expectation: filesystem-level encryption on the PostgreSQL volume
- Sensitive columns with additional protection: `totp_secrets.secret` (application-layer encryption)

### 9.2 S3 Object Storage at Rest

- Server-Side Encryption (SSE) enabled on all buckets (S3 SSE-S3 or SSE-KMS depending on provider — ADR-031)
- Access controlled via IAM policies; public access disabled on all buckets

### 9.3 Redis at Rest

- Redis is used for transient data (task queue, cache)
- Redis persistence (RDB/AOF) must have filesystem encryption where enabled
- Sensitive data (user queries, scan inputs) must not be cached in Redis

### 9.4 Backup Encryption

Database backups must be encrypted before storage. Backup encryption keys must be managed separately from the database encryption.

---

## 10. API Security

### 10.1 Security Headers

The FastAPI application must set these HTTP response headers:

| Header | Value | Purpose |
|---|---|---|
| `Strict-Transport-Security` | `max-age=63072000; includeSubDomains` | Force HTTPS |
| `X-Content-Type-Options` | `nosniff` | Prevent MIME sniffing |
| `X-Frame-Options` | `DENY` | Prevent clickjacking |
| `Content-Security-Policy` | Defined for SPA | XSS mitigation |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | Limit referrer data |
| `Permissions-Policy` | Restrict camera, microphone, geolocation | Principle of least privilege |
| `Cache-Control` | `no-store` for sensitive API responses | Prevent caching of sensitive data |

### 10.2 OpenAPI Documentation Access

The FastAPI auto-generated OpenAPI documentation (`/docs`, `/redoc`) must be:
- **Disabled in production** or access-restricted to internal network / authenticated admin users
- Available in development and staging environments

### 10.3 Request Size Limits

Maximum request body size enforced at the reverse proxy and application level to prevent large-payload DoS attacks.

### 10.4 Sensitive Data in URLs

Sensitive data (tokens, passwords, API keys) must **never** appear in URL query strings (they appear in server logs). Tokens are sent in headers or request bodies; never in query parameters.

---

## 11. Secrets Management

### 11.1 Secret Types

| Secret | Storage |
|---|---|
| Database connection string | Environment variable |
| Redis connection string | Environment variable |
| JWT signing key | Environment variable |
| Argon2id parameters | Configuration file (not a secret, but not hardcoded) |
| LLM API key | Environment variable (ADR-013) |
| Threat intelligence API key | Environment variable (ADR-032) |
| S3 access key and secret | Environment variable |
| Email service API key | Environment variable |

### 11.2 Rules

1. No secrets in source code or configuration files committed to Git
2. `.env` files are in `.gitignore`; `.env.example` with placeholder values is committed
3. Secrets in CI/CD are stored as GitHub Actions secrets (not in workflow files)
4. Production secrets should use a secrets manager (AWS Secrets Manager, HashiCorp Vault) — Phase 1 may use environment variables if the deployment platform provides secure injection; this must be reviewed before production launch
5. Secrets are rotated on a defined schedule; immediately on suspected compromise

---

## 12. Logging and Audit

### 12.1 Security Event Audit Log

Security-relevant events are written to the `audit_log` table (append-only):

| Event | Trigger |
|---|---|
| `user_registration` | Successful registration |
| `email_verified` | Email verification completed |
| `user_login_success` | Successful login (with or without 2FA) |
| `user_login_failed` | Failed login attempt |
| `user_login_2fa_failed` | Failed TOTP verification |
| `password_reset_requested` | Password reset link sent |
| `password_reset_completed` | Password successfully changed |
| `totp_enrolled` | 2FA enrollment completed |
| `totp_disabled` | 2FA disabled by user |
| `account_deleted` | Account deletion completed |
| `admin_action` | Any admin-role action |
| `rate_limit_exceeded` | Rate limit triggered (high-sensitivity endpoints) |

### 12.2 What Must NOT Appear in Logs

- Passwords (plaintext or hashed)
- JWT tokens
- Encryption keys
- User-submitted scam text, URLs, or file contents
- PII beyond user ID and email (in audit context)
- TOTP codes or backup codes

### 12.3 Application Logs

Application logs use structured logging (JSON format) with:
- `request_id`: Unique per-request correlation ID
- `user_id`: UUID of authenticated user (where applicable)
- `endpoint`: Route path
- `status_code`: HTTP response status
- `duration_ms`: Request processing time
- `error_code`: Error code if applicable

Application logs must not contain PII or sensitive data.

---

## 13. Error Handling Security

### 13.1 External Error Messages

External error responses (sent to clients) must:
- Never expose stack traces
- Never expose database schema details
- Never reveal whether an email address is registered (FR-094)
- Never reveal which authentication factor failed (FR-097)
- Use the standard error code/message format (see API spec §14)

### 13.2 Internal Error Logging

Full error details (stack trace, context) are logged internally (not sent to client). The `request_id` in the response allows support correlation to logs.

### 13.3 AI/ML Error Handling

If ML inference fails:
- Return an error response — **never return a default 'Safe' verdict**
- Error response clearly indicates that analysis was not completed
- User is advised to exercise caution

A false 'Safe' verdict resulting from a model error is more dangerous than an error response.

---

## 14. Dependency and Supply Chain Security

### 14.1 Dependency Management

- Python dependencies pinned in `requirements.txt` or `pyproject.toml` with exact versions
- Node.js dependencies pinned in `package-lock.json`
- `pip-audit` (Python) and `npm audit` (Node.js) run in CI pipeline

### 14.2 Dependency Updates

- Security advisories monitored via GitHub Dependabot or equivalent
- Critical security patches applied within a defined SLA (Phase 1: within 7 days of advisory)

### 14.3 Model Supply Chain

- Pre-trained ML models downloaded from Hugging Face Hub — verify model hash/checksum
- No model artefacts stored in Git repository (stored in S3 / MLflow artefact store)
- Model provenance tracked in MLflow experiment records

---

## 15. Security Configuration Parameters (TBD)

The following parameters are **TBD** and must be resolved through security benchmarking and threat-model review before production deployment (ADR-026, CSHAKTI-CONST-001 §8.12):

| Parameter | Status | Resolution Process |
|---|---|---|
| Argon2id memory cost (m) | TBD | Benchmark on server hardware; target 100–500ms hash time |
| Argon2id time cost (t) | TBD | Same benchmark |
| Argon2id parallelism (p) | TBD | Same benchmark |
| Argon2id KDF parameters for F-10 | TBD | Separate benchmark for KDF use case |
| JWT access token expiry | TBD | Threat-model review: balance usability vs. token theft risk |
| JWT refresh token lifetime | TBD | Threat-model review |
| JWT algorithm (RS256 vs. HS256) | TBD | Security architecture review |
| Login rate limit thresholds | TBD | Threat-model review + usability testing |
| Registration rate limit thresholds | TBD | Threat-model review |
| Account lockout threshold (failed logins) | TBD | Threat-model review |
| Account lockout duration | TBD | Threat-model review |
| TOTP time window tolerance | TBD (likely ±1 step) | Usability review |
| HSTS max-age | TBD | Standard guidance: 2 years (63072000 seconds) for mature sites |
| Maximum file size for uploads | TBD | Performance + abuse prevention analysis |

> **Important:** These parameters **must not** be permanently set by developers or AI coding tools during implementation without completing the benchmarking and review process. Placeholder values used during development must not be carried into production.

---

*End of CyberShakti Security Architecture — CSHAKTI-SEC-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
