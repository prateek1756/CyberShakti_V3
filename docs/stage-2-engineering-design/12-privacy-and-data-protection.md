# CyberShakti — Privacy & Data Protection Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-PRIV-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SRS-001, CSHAKTI-SEC-001, CSHAKTI-CONST-001 §9 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Privacy Governance & Principles](#1-privacy-governance--principles)
2. [Data Classification Framework](#2-data-classification-framework)
3. [User Consent Architecture](#3-user-consent-architecture)
4. [Data Minimisation & Processing Policy](#4-data-minimisation--processing-policy)
5. [Data Retention & Purge Policy](#5-data-retention--purge-policy)
6. [Data Subject Rights (DPDP Act 2023 Alignment)](#6-data-subject-rights-dpdp-act-2023-alignment)
7. [Third-Party Data Sharing & Sub-processors](#7-third-party-data-sharing--sub-processors)
8. [Telemetry, Analytics & Logging Privacy](#8-telemetry-analytics--logging-privacy)

---

## 1. Privacy Governance & Principles

CyberShakti handles sensitive user data, including personal credentials, security scan inputs, and file uploads. The privacy architecture is governed by CSHAKTI-CONST-001 §9 and aligns with India's **Digital Personal Data Protection (DPDP) Act 2023**.

### Core Privacy Directives:
1. **Consent-First Processing**: No personal data processing occurs without explicit, informed consent.
2. **Data Minimisation**: Collect only the minimum data strictly necessary to fulfill the user-requested feature.
3. **No Unencrypted Plaintext Persistence**: User files (F-10) and raw passwords are never saved in plaintext.
4. **Right to Erasure**: Users can request complete account and personal data deletion.
5. **No Data Monetisation**: User data, scan histories, and telemetry are never sold or shared for advertising.

---

## 2. Data Classification Framework

All data ingested, stored, or processed by CyberShakti is categorized into four sensitivity tiers:

| Sensitivity Tier | Data Types | Examples | Protection Controls |
|---|---|---|---|
| **Tier 1: Restricted (Crypto/Auth)** | Passwords, TOTP Secrets, Encryption Keys, Reset Tokens | User Account Passwords, Argon2id hashes, AES Nonces | Argon2id hashing, Column-level encryption, Short TTLs |
| **Tier 2: Confidential (PII & Files)** | Email Addresses, User Files, Personal Queries, IP Addresses | `users.email`, Uploaded F-10 documents, F-11 Assistant Chat Messages | AES-256-GCM, TLS 1.2+, Strict RBAC, 30-day purge |
| **Tier 3: Internal (Operational)** | Anonymised Scan History, Risk Scores, Audit Logs | `scan_results` (hashed inputs), System metrics | Pseudonymisation, SET NULL on user delete |
| **Tier 4: Public** | Knowledge base articles, Safety Tips, Quiz questions | F-14 Hub content, Public alerts | Read-only public APIs, CDN caching |

---

## 3. User Consent Architecture

### 3.1 Consent Management Flow

Consent is captured explicitly at two distinct touchpoints:

1. **Account Registration Consent**: Mandatory checkbox required during signup:
   > *"I consent to CyberShakti processing my email and scan requests in accordance with the Privacy Policy for digital threat analysis."*
2. **Location Access Consent (F-13)**: Browser-level and UI prompt before retrieving location data:
   > *"CyberShakti requests your city location to display relevant local scam alerts. Location data is used strictly for filtering and is not stored persistently."*

### 3.2 Consent Storage & Audit

- Consent records are stored in `users.consent_given` (boolean) and logged in `audit_log` with timestamp and IP.
- Withdrawing consent triggers account deactivation and initiates the 30-day data deletion process.

---

## 4. Data Minimisation & Processing Policy

### 4.1 Feature-Specific Data Minimisation Rules

| Feature | Input Accepted | Storage Handling | Minimisation Control |
|---|---|---|---|
| **F-01 URL Scan** | URL String | SHA-256 `input_hash` stored in DB | Raw URL discarded after scan completion |
| **F-02 Text Scan** | Message Text | Length & Language stored | Message text **never stored** in database |
| **F-03 Screenshot** | Image File | Temp S3 upload during processing | Image **deleted immediately** from S3 post-OCR |
| **F-09 Password Check** | Password String | In-memory evaluation only | **Zero persistence** — never written to DB or log |
| **F-10 File Encrypt** | Uploaded File | Transferred via stream | Plaintext **never written to disk** or S3 |
| **F-13 Scam Alerts** | City / Geolocation | Processed in-memory for query | Geolocation coordinates **not stored** in DB |

---

## 5. Data Retention & Purge Policy

All personal data is subject to strict lifecycle management.

```
[ Active Account ] ──► [ User Requests Deletion ]
                              │
                              ▼
                  [ Soft Delete (is_active = FALSE) ]
                  [ 30-Day Grace / Retention Window ]
                              │
                              ▼
                  [ Automated Background Purge Worker ]
                  - Hard delete users row PII
                  - Anonymise scan_results (user_id = NULL)
                  - Delete assistant conversation history
                  - Delete associated refresh tokens
```

| Data Category | Active Retention | Post-Account Deletion | Purge Method |
|---|---|---|---|
| User Account PII | Duration of active account | 30 days grace period | Hard DB record delete |
| Scan History Records | 12 months | Immediate anonymisation | `user_id` set to `NULL` |
| AI Assistant Chat History | 90 days rolling | 30 days | Hard DB record delete |
| Uploaded Images (F-03, F-06) | Processing time only (< 1 min) | N/A | S3 Object Hard Delete |
| Refresh Tokens / Sessions | Token expiry | Immediate | Hard DB record delete |

---

## 6. Data Subject Rights (DPDP Act 2023 Alignment)

CyberShakti enforces user data rights through self-service UI flows and API endpoints:

1. **Right to Access (Summary of Data)**: Users can view their complete account details, score history, and scan logs via `/users/me` and `/assist/risk-score`.
2. **Right to Correction**: Users can update their profile information and password via account settings.
3. **Right to Erasure (Deletion)**: Self-service account deletion endpoint (`DELETE /users/me`) requiring password confirmation.
4. **Right to Grievance Redressal**: Contact details for CyberShakti's designated Data Protection Officer (DPO) are published in the Privacy Policy.

---

## 7. Third-Party Data Sharing & Sub-processors

CyberShakti does **not** sell user personal data. Third-party integrations are limited strictly to infrastructure providers bound by non-disclosure and data protection contracts:

| Sub-processor | Purpose | Data Transferred | Protection Measures |
|---|---|---|---|
| **Vercel** | Frontend Hosting / CDN | IP Address, Static HTTP Request | TLS 1.3, Edge security |
| **Threat Intel API Provider** | F-01 URL & F-08 Phone Lookup | Anonymised URL domain / Phone number | No user ID or PII attached |
| **LLM Provider (ADR-013)** | F-11 AI Assistant | Sanitized query string & RAG context | Zero data retention for LLM training |

---

## 8. Telemetry, Analytics & Logging Privacy

- **No Third-Party Trackers**: CyberShakti does not use external tracking scripts (e.g., Google Analytics, Meta Pixel).
- **Application Logs**: Standard HTTP access logs contain no PII, request bodies, or user passwords.
- **Error Logs**: Stack traces are sanitized to strip environment variables, connection strings, and user input tokens.

---

*End of CyberShakti Privacy & Data Protection Specification — CSHAKTI-PRIV-001 v1.0.0*
