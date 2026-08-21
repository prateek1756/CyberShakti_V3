# CyberShakti — Threat Model & Security Risk Analysis

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-THREAT-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-SEC-001, CSHAKTI-CONST-001 §8 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Threat Modeling Framework](#1-threat-modeling-framework)
2. [System Trust Boundaries](#2-system-trust-boundaries)
3. [Attacker Personas & Threat Actors](#3-attacker-personas--threat-actors)
4. [STRIDE Threat Analysis](#4-stride-threat-analysis)
5. [AI/ML Specific Threat Analysis](#5-aiml-specific-threat-analysis)
6. [Risk Assessment Matrix](#6-risk-assessment-matrix)
7. [Mitigation Controls Summary](#7-mitigation-controls-summary)
8. [Residual Risks & Trade-offs](#8-residual-risks--trade-offs)

---

## 1. Threat Modeling Framework

CyberShakti employs the **STRIDE** methodology (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) combined with OWASP Top 10 API Security Risks and OWASP Top 10 for LLM Applications to analyze potential threats against the platform.

Threat modeling is a living process. This document represents the baseline Phase 1 threat analysis based on CSHAKTI-SYS-001 and CSHAKTI-SEC-001.

---

## 2. System Trust Boundaries

```
[ UNTRUSTED ZONE: Public Internet / End Users ]
                      │
                      │ HTTPS (TLS 1.2+)
                      ▼
┌─────────────────────────────────────────────────────────┐
│ TRUST BOUNDARY 1: Edge / Gateway                       │
│ - Vercel SPA CDN                                        │
│ - FastAPI Gateway (Rate Limiting, CORS, WAF)            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ Internal REST Calls / Authenticated JWT
                      ▼
┌─────────────────────────────────────────────────────────┐
│ TRUST BOUNDARY 2: Core Application Logic                │
│ - FastAPI App Modules (detect, protect, assist, learn)  │
│ - Auth & Session Manager                                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┴───────────────┐
        │ Internal Network            │ Async Tasks
        ▼                             ▼
┌───────────────────────────┐ ┌───────────────────────────┐
│ TRUST BOUNDARY 3: Storage │ │ TRUST BOUNDARY 4: Workers │
│ - PostgreSQL 15+          │ │ - Celery Async Workers    │
│ - Redis Broker/Cache      │ │ - ML Inference Pipelines  │
│ - S3 Storage Buckets      │ └─────────────┬─────────────┘
└───────────────────────────┘               │ Outbound HTTPS (API Key)
                                            ▼
                              ┌───────────────────────────┐
                              │ External APIs             │
                              │ - Threat Intel / LLM API  │
                              └───────────────────────────┘
```

---

## 3. Attacker Personas & Threat Actors

| Persona | Motivation | Capabilities | Target |
|---|---|---|---|
| **Casual Scammer** | Test if their scam URL/text is flagged | Submits text/URLs to scanning API | Detection rules & ML models |
| **Sophisticated Fraud Ring** | Bypass detection algorithms | Automated API probing, adversarial input generation | F-01, F-02, F-05 ML classifiers |
| **Malicious User** | Steal user data or disrupt service | Exploiting auth flaws, injection, DoS | Auth, DB, S3 Storage |
| **Compromised Insider / Service** | Data exfiltration or code injection | Access to infrastructure environment variables | DB, Secrets, System Logs |

---

## 4. STRIDE Threat Analysis

### 4.1 Spoofing (Identity)

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-S01 | Attacker impersonates legitimate user via stolen JWT | API Gateway / Auth | High | Short-lived JWT access tokens, httpOnly refresh tokens, refresh token rotation | Mitigated |
| T-S02 | Brute-force guessing of user passwords | `/auth/login` | High | Argon2id hashing, strict rate limiting, lockout policy, optional 2FA | Mitigated |
| T-S03 | Email impersonation during registration | `/auth/register` | Medium | Mandatory email verification prior to account activation | Mitigated |

### 4.2 Tampering (Data Integrity)

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-T01 | Tampering with stored scan results or user risk scores | PostgreSQL | High | Least-privilege DB roles, parameterised queries, audit logging | Mitigated |
| T-T02 | Altering encrypted user files in transit/rest (F-10) | Storage / API | High | AES-256-GCM authenticated encryption (128-bit auth tag) | Mitigated |
| T-T03 | Tampering with ML model weights in storage | S3 Artefact Store | Critical | Strict S3 IAM policy, checksum validation before worker model loading | Mitigated |

### 4.3 Repudiation

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-R01 | User denies making fraudulent scan submissions or account actions | System Audit Log | Medium | Immutable append-only `audit_log` table recording user ID, timestamp, event type | Mitigated |
| T-R02 | Admin denies modifying critical system configurations or alerts | Admin API | High | Mandatory admin audit logging with non-repudiable timestamps | Mitigated |

### 4.4 Information Disclosure

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-I01 | Leakage of user email or password hashes via API errors or logs | Error Handler / Logging | High | Generic error envelopes, strict prohibition of PII/credentials in logs | Mitigated |
| T-I02 | Disclosure of sensitive plaintext files during F-10 encryption | API / Temp Storage | Critical | Streaming encryption; plaintext never written to disk or S3 | Mitigated |
| T-I03 | Account enumeration via login/registration endpoints | Auth API | Medium | Generic error responses (FR-094, FR-097) for missing/duplicate accounts | Mitigated |

### 4.5 Denial of Service (DoS)

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-D01 | Heavy ML inference endpoint flooding (F-03 OCR, F-06 Deepfake) | Celery Workers / API | High | Offloading to Celery async queues, strict per-user & per-IP rate limits | Mitigated |
| T-D02 | Large file upload payload exhaustion | API Gateway | Medium | File size limits enforced at gateway prior to reading request body | Mitigated |
| T-D03 | Exhaustion of Argon2id password hashing worker threads | `/auth/login` | High | Strict rate limiting on auth endpoints; max password length limit (1000 chars) | Mitigated |

### 4.6 Elevation of Privilege

| ID | Threat Description | Vulnerable Component | Impact | Mitigation Controls | Status |
|---|---|---|---|---|---|
| T-E01 | Regular user accessing administrative management endpoints | Admin API | Critical | Centralized RBAC middleware enforcing `role: admin` check on all admin routes | Mitigated |
| T-E02 | Insecure Direct Object Reference (IDOR) to access other users' scans | `/detect` & `/assist` API | High | Explicit ownership checks (`user_id == current_user.id`) in query filters | Mitigated |

---

## 5. AI/ML Specific Threat Analysis

### 5.1 Adversarial Inputs & Evasion

- **Threat:** Scammers craft URLs or text containing homoglyphs, zero-width spaces, or intentional misspellings to evade DistilBERT / XGBoost detection.
- **Mitigation:** Unicode normalisation (NFKC) in preprocessing, rule-based keyword pre-filters, continuous model retraining with evasive samples, and threat intelligence list fallback.

### 5.2 Model Inversion & Data Extraction

- **Threat:** Querying F-11 AI Assistant to extract raw system prompts or proprietary training data.
- **Mitigation:** RAG pipeline context isolation, system prompt guardrails against prompt injection, output filtering middleware.

### 5.3 Data Poisoning

- **Threat:** Submitting malicious feedback or automated reports to corrupt future training datasets.
- **Mitigation:** Offline dataset curation and validation; no automated online model updating directly from user inputs in Phase 1.

---

## 6. Risk Assessment Matrix

| Threat ID | Threat Category | Likelihood | Impact | Severity | Primary Mitigation |
|---|---|---|---|---|---|
| **T-E01** | Elevation of Privilege | Low | Critical | **High** | RBAC Middleware |
| **T-I02** | Information Disclosure | Low | Critical | **High** | Streaming Encryption |
| **T-D01** | Denial of Service | Medium | High | **High** | Celery + Rate Limiting |
| **T-S01** | Spoofing | Medium | High | **High** | JWT + Refresh Rotation |
| **T-T02** | Tampering | Low | High | **Medium** | AES-256-GCM |
| **T-I03** | Information Disclosure | High | Low | **Medium** | Generic Error Envelopes |

---

## 7. Mitigation Controls Summary

1. **Authentication & Identity:** Argon2id, JWT with refresh token rotation, optional TOTP 2FA.
2. **Authorisation & Access Control:** Strict RBAC with ownership enforcement on all database queries.
3. **Cryptography:** AES-256-GCM for files, TLS 1.2+ for transit, Argon2id for password keys.
4. **Resilience & Rate Limiting:** Redis-backed rate limiting on API endpoints, async task queue isolation via Celery.
5. **Data Protection:** Zero plaintext persistence for user files, no raw PII in application logs.

---

## 8. Residual Risks & Trade-offs

1. **Third-Party API Dependency:** Reliance on external Threat Intelligence & LLM providers creates a potential single point of failure or latency bottleneck. *Trade-off:* Acceptable for Phase 1 to avoid building proprietary threat feeds.
2. **Async Task Result Polling:** Polling introduces minor network overhead compared to WebSockets. *Trade-off:* Preferred for operational simplicity in modular monolith.

---

*End of CyberShakti Threat Model & Security Risk Analysis — CSHAKTI-THREAT-001 v1.0.0*
