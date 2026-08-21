# CyberShakti — Test Plan & Test Cases

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-TEST-002 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SRS-001, CSHAKTI-TEST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Scope of Testing](#1-scope-of-testing)
2. [Functional Test Cases (Pillar 1: Detect & Analyze)](#2-functional-test-cases-pillar-1-detect--analyze)
3. [Functional Test Cases (Pillar 2: Protect)](#3-functional-test-cases-pillar-2-protect)
4. [Functional Test Cases (Pillar 3: Assist & Respond)](#4-functional-test-cases-pillar-3-assist--respond)
5. [Functional Test Cases (Pillar 4: Learn & Prevent)](#5-functional-test-cases-pillar-4-learn--prevent)
6. [Authentication & Account Test Cases](#6-authentication--account-test-cases)
7. [Non-Functional & Performance Test Cases](#7-non-functional--performance-test-cases)

---

## 1. Scope of Testing

This document provides the formal master test case suite for CyberShakti Phase 1. Every test case links directly to a Functional Requirement (`FR-###`) or Non-Functional Requirement (`NFR-###`) from CSHAKTI-SRS-001.

---

## 2. Functional Test Cases (Pillar 1: Detect & Analyze)

| Test Case ID | Traces To | Title / Scenario | Preconditions | Test Steps / Input | Expected Result | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| `TC-DET-001` | FR-001, FR-006 | Submit valid phishing URL | Authenticated user | Submit `http://bank-kyc-verify-xyz.info` to `/detect/scan-url` | Returns HTTP 200, `risk_level: "high_risk"`, non-empty explanation | Verdict returned with explanation and valid risk level |
| `TC-DET-002` | FR-002 | Submit invalid non-URL string | Authenticated user | Submit `"hello world"` to `/detect/scan-url` | Returns HTTP 422 Validation Error | Validation error envelope returned; no scan executed |
| `TC-DET-003` | FR-009, FR-012 | Submit scam SMS text | Authenticated user | Submit KYC urgency scam text to `/detect/scan-message` | Returns HTTP 200, `risk_level: "high_risk"`, scam indicators | Verdict returned with plain-language explanation |
| `TC-DET-004` | FR-016, FR-018 | Screenshot OCR scam scan | Authenticated user | Upload PNG screenshot of OTP scam text to `/detect/scan-screenshot` | Task queued (HTTP 202); poll result returns extracted text & High Risk verdict | Text extracted via OCR & classified correctly |
| `TC-DET-005` | FR-023, FR-025 | QR code containing phishing URL | Authenticated user | Upload QR image encoding phishing link to `/detect/scan-qr` | Returns HTTP 200, decoded URL, and High/Critical Risk verdict | QR decoded & URL analyzed via F-01 pipeline |
| `TC-DET-006` | FR-034, FR-036 | Deepfake analysis experimental disclaimer | User on F-06 screen | Navigate to `/detect/deepfake-check` | "Experimental" label displayed prominently before file upload | Experimental disclaimer present before and after scan |

---

## 3. Functional Test Cases (Pillar 2: Protect)

| Test Case ID | Traces To | Title / Scenario | Preconditions | Test Steps / Input | Expected Result | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| `TC-PROT-001` | FR-045, FR-047 | Scam phone number lookup | Authenticated user | Submit `"9876543210"` to `/protect/check-phone` | Returns HTTP 200, phone threat report status, and data source indicator | Threat verdict returned with data source attribution |
| `TC-PROT-002` | FR-048 | Emergency number exclusion | Authenticated user | Submit `"112"` to `/protect/check-phone` | Returns HTTP 200, `is_emergency_service: true`, no risk verdict | Identified as emergency number; no threat risk assigned |
| `TC-PROT-003` | FR-053, FR-056 | Password strength checker | Authenticated user | Submit `"password123"` to `/protect/check-password` | Returns `strength_level: "very_weak"` + improvements; password NOT logged | Weak verdict returned; zero password persistence |
| `TC-PROT-004` | FR-057, FR-059 | Secure file encryption & decryption | Authenticated user | Upload `sample.pdf` + password `"Secret123!"` to `/protect/encrypt-file` | Produces `.enc` binary stream. Re-uploading with correct password decrypts original file | File successfully encrypted and decrypted cleanly |
| `TC-PROT-005` | FR-060 | Decryption with wrong password | Authenticated user | Upload `.enc` file + wrong password `"WrongPass"` | Returns HTTP 400 `WRONG_PASSWORD` error; zero file content returned | Error envelope returned; plaintext never leaked |

---

## 4. Functional Test Cases (Pillar 3: Assist & Respond)

| Test Case ID | Traces To | Title / Scenario | Preconditions | Test Steps / Input | Expected Result | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| `TC-AST-001` | FR-072, FR-074 | Retrieve Cyber Risk Score | Authenticated user with scan history | Call `GET /assist/risk-score` | Returns HTTP 200, score (0-100), signal breakdown list, and recommendations | Score breakdown and disclaimer present |
| `TC-AST-002` | FR-080, FR-083 | Location scam alerts query | Authenticated user | Call `GET /assist/scam-alerts?city=Mumbai` | Returns HTTP 200, active Mumbai alerts or "no recent alerts" message | Returns matching alerts or clear empty state message |

---

## 5. Functional Test Cases (Pillar 4: Learn & Prevent)

| Test Case ID | Traces To | Title / Scenario | Preconditions | Test Steps / Input | Expected Result | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| `TC-LRN-001` | FR-086 | Fetch Daily Safety Tip | Public access | Call `GET /learn/daily-tip` | Returns HTTP 200, tip text, category, and date | Valid tip returned |
| `TC-LRN-002` | FR-087, FR-088 | Cybersecurity Quiz interaction | Authenticated user | Submit answer to `/learn/quiz/submit-answer` | Returns HTTP 200, `is_correct` boolean, and plain-language explanation | Correct answer and explanation displayed |

---

## 6. Authentication & Account Test Cases

| Test Case ID | Traces To | Title / Scenario | Preconditions | Test Steps / Input | Expected Result | Pass/Fail Criteria |
|---|---|---|---|---|---|---|
| `TC-AUTH-001` | FR-092, FR-095 | User registration without consent | Unauthenticated | Submit email & password with `consent_given: false` | Returns HTTP 400 `CONSENT_REQUIRED` error | Registration rejected without consent |
| `TC-AUTH-002` | FR-096, FR-097 | Invalid login credentials | Registered user | Submit wrong password to `/auth/login` | Returns HTTP 401 generic `"Invalid email or password"` | Generic error returned; field specifics hidden |
| `TC-AUTH-003` | FR-103, FR-104 | Self-service account deletion | Authenticated user | Call `DELETE /users/me` with password & typed confirmation | Account soft-deleted; sessions invalidated; PII purge scheduled | User account deactivated and tokens revoked |

---

## 7. Non-Functional & Performance Test Cases

| Test Case ID | Traces To | Title / Scenario | Test Method | Target Benchmark | Pass/Fail Criteria |
|---|---|---|---|---|---|
| `TC-NFR-PERF-01` | NFR-PERF-001 | Synchronous API response time | Locust load test against `/protect/check-password` | Target: TBD after benchmarking | Response time within benchmark |
| `TC-NFR-SEC-01` | NFR-SEC-004 | Unauthenticated route protection | HTTP client request without Bearer token | HTTP 401 Unauthorized | Access blocked across all protected endpoints |
| `TC-NFR-SEC-02` | NFR-SEC-007 | CORS Wildcard Prohibition | OPTIONS request with external `Origin` header | Production headers exclude `*` | Origin strictly validated |

---

*End of CyberShakti Test Plan & Test Cases — CSHAKTI-TEST-002 v1.0.0*
