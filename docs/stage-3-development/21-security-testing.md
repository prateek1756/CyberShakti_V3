# CyberShakti — Security Testing & Vulnerability Assessment

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-TEST-004 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SEC-001, CSHAKTI-THREAT-001, CSHAKTI-CONST-001 §8 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Security Testing Objectives](#1-security-testing-objectives)
2. [Automated Security Scanning (SAST & DAST)](#2-automated-security-scanning-sast--dast)
3. [Penetration Testing Test Cases](#3-penetration-testing-test-cases)
4. [Cryptographic Verification Suite](#4-cryptographic-verification-suite)
5. [Dependency & Supply Chain Audit](#5-dependency--supply-chain-audit)
6. [Compliance Verification (DPDP Act 2023)](#6-compliance-verification-dpdp-act-2023)

---

## 1. Security Testing Objectives

CyberShakti stores sensitive cryptographic data and processes security threats. The security testing strategy validates that all security controls specified in CSHAKTI-SEC-001 and CSHAKTI-THREAT-001 function correctly under attack.

### Core Focus Areas:
- **Zero Plaintext Credentials**: Verify passwords, secrets, and raw user files are never leaked.
- **OWASP API Top 10 Coverage**: Validate resistance against authorization bypass, rate limiting failure, and injection.
- **Cryptographic Rigour**: Validate AES-256-GCM authenticated encryption and Argon2id key derivation implementation.

---

## 2. Automated Security Scanning (SAST & DAST)

| Scan Type | Tool | Frequency | Scope | Pass Criteria |
|---|---|---|---|---|
| **Static Analysis (SAST)** | `bandit` | Every Commit / PR | Python backend codebase (`app/`) | 0 High or Medium severity findings |
| **Dependency Scan** | `pip-audit` / `npm audit` | Daily CI Job | Backend & Frontend dependencies | 0 Known Critical/High CVEs |
| **Secret Scanning** | `trufflehog` / `git-leaks` | Every Commit | Complete git repository commit history | 0 Committed secrets or private keys |
| **Dynamic Scan (DAST)** | OWASP ZAP | Weekly Nightly CI | Active FastAPI endpoints | 0 High risk API vulnerabilities |

---

## 3. Penetration Testing Test Cases

### 3.1 Authentication & Authorisation Tests

| Test ID | Vulnerability Category | Attack Vector | Expected Defense |
|---|---|---|---|
| `SEC-TC-01` | Broken Object Level Auth (BOLA) | Accessing another user's scan result (`GET /detect/scans/{other_user_id}`) | Returns HTTP 403 Forbidden |
| `SEC-TC-02` | RBAC Bypass | User token calling `/admin/users` | Returns HTTP 403 Forbidden |
| `SEC-TC-03` | JWT Signature Forgery | Modifying JWT payload with `alg: "none"` | API rejects request with HTTP 401 |
| `SEC-TC-04` | Credential Stuffing / Brute Force | Sending 100 consecutive failed logins to `/auth/login` | Rate limit triggers HTTP 429 after threshold |

### 3.2 Injection & Input Manipulation Tests

| Test ID | Vulnerability Category | Attack Vector | Expected Defense |
|---|---|---|---|
| `SEC-TC-05` | SQL Injection | Submitting `' OR 1=1 --` into login email field | Handled as literal string via Pydantic/SQLAlchemy; no syntax error |
| `SEC-TC-06` | Command Injection | Submitting `; cat /etc/passwd` into F-01 URL scan field | Validated by URL parser; returns HTTP 422 |
| `SEC-TC-07` | Path Traversal | Uploading filename `../../etc/passwd` to F-03 screenshot API | File saved under random UUID path in S3; path traversal stripped |

---

## 4. Cryptographic Verification Suite

### 4.1 F-10 File Encryption Integrity Check
- **Test**: Encrypt a test file using `POST /protect/encrypt-file`. Flip 1 single bit in the resulting `.enc` file ciphertext. Attempt to decrypt via `POST /protect/decrypt-file`.
- **Expected Result**: Decryption fails with HTTP 400 `WRONG_PASSWORD` / Authentication Tag Verification Error. Zero byte content output.

### 4.2 Nonce Uniqueness Check
- **Test**: Perform 10,000 consecutive file encryptions with identical input file and password.
- **Expected Result**: All 10,000 generated 96-bit nonces MUST be unique. Zero nonce collisions allowed.

---

## 5. Dependency & Supply Chain Audit

- All container base images MUST use pinned digest tags (e.g., `python:3.11-slim@sha256:...`).
- Third-party Python libraries audited for unmaintained or suspicious dependencies.

---

## 6. Compliance Verification (DPDP Act 2023)

- **Erasure Verification**: Perform self-service account deletion. Inspect database to confirm PII fields (`email`, `password_hash`) are purged within defined retention window.
- **Consent Enforcement**: Attempt registration without checking consent box. Verify API returns HTTP 400 `CONSENT_REQUIRED`.

---

*End of CyberShakti Security Testing & Vulnerability Assessment — CSHAKTI-TEST-004 v1.0.0*
