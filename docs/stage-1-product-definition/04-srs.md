# CyberShakti — Software Requirements Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-SRS-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-15 |
| **Traces To** | CSHAKTI-TRD-001, CSHAKTI-PRD-001, CSHAKTI-PVS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — all content must be consistent with the constitution. Conflicts recorded in `docs/00-decisions.md`. |

---

## Table of Contents

1. [Introduction and Scope](#1-introduction-and-scope)
2. [Functional Requirements](#2-functional-requirements)
3. [Non-Functional Requirements](#3-non-functional-requirements)
4. [Interface Requirements](#4-interface-requirements)
5. [System Constraints](#5-system-constraints)
6. [Assumptions and Dependencies](#6-assumptions-and-dependencies)
7. [Out-of-Scope Requirements](#7-out-of-scope-requirements)
8. [Requirements Traceability Matrix](#8-requirements-traceability-matrix)

---

## 1. Introduction and Scope

### 1.1 Purpose

This document is the formal Software Requirements Specification for CyberShakti Phase 1. It defines the complete, traceable, testable set of functional and non-functional requirements that the Phase 1 system must satisfy.

This document is the primary input for:
- Test planning and test case definition (Stage 3)
- Architecture and database design (Stage 2)
- API specification (Stage 2)
- Implementation task breakdown (Stage 3)

### 1.2 Scope

This SRS covers the complete Phase 1 CyberShakti system: all 14 features across 4 pillars, the authentication and account management system, the Cyber Risk Score engine, and all supporting infrastructure as defined in the approved Phase 1 product definition.

### 1.3 Requirement ID Scheme

| Prefix | Category |
|---|---|
| FR-### | Functional requirement |
| NFR-PERF-### | Non-functional — performance |
| NFR-SEC-### | Non-functional — security |
| NFR-PRIV-### | Non-functional — privacy |
| NFR-SCALE-### | Non-functional — scalability |
| NFR-REL-### | Non-functional — reliability |
| NFR-USE-### | Non-functional — usability |
| NFR-ACC-### | Non-functional — accessibility |
| NFR-MAINT-### | Non-functional — maintainability |
| NFR-PORT-### | Non-functional — portability |

### 1.4 Priority Definitions

| Priority | Meaning |
|---|---|
| **Must Have** | Required for Phase 1 launch. System is not releasable without it. |
| **Should Have** | Strongly desired for Phase 1. Absence significantly degrades user value. |
| **Could Have** | Beneficial but not launch-critical. Can be deferred within Phase 1 if necessary. |

### 1.5 How to Read This Document

Requirements are atomic — one behaviour per requirement. Each requirement has a stable ID, a priority, a source, a description, and an acceptance criterion. The Traceability Matrix in Section 8 links every requirement to its upstream source and downstream test case placeholder.

---

## 2. Functional Requirements

### 2.1 Pillar 1 — Detect & Analyze

#### F-01: Phishing Link Scanning

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-001 | Must Have | The system SHALL accept a URL string as input for phishing risk analysis. | A URL submitted via the F-01 endpoint is accepted and processed without error. |
| FR-002 | Must Have | The system SHALL validate that the submitted input is a recognisable URL structure before analysis. | A non-URL string input (e.g., "hello world") returns a validation error response, not a risk verdict. |
| FR-003 | Must Have | The system SHALL perform URL feature engineering (lexical, domain, path, query features) on the submitted URL. | Feature extraction runs without error on any valid URL input. |
| FR-004 | Must Have | The system SHALL check the submitted URL against configured threat intelligence sources. | A URL present on the configured threat list returns a risk verdict reflecting the threat intelligence match. |
| FR-005 | Must Have | The system SHALL classify the URL using the trained phishing URL classifier. | The classifier returns a numeric risk score for any valid, parseable URL input. |
| FR-006 | Must Have | The system SHALL return a risk verdict at one of five levels: Safe, Low Risk, Moderate Risk, High Risk, or Critical. | Every F-01 response contains a risk level field populated with one of the five defined values. |
| FR-007 | Must Have | The system SHALL return a non-empty plain-language explanation with every F-01 risk verdict. | Automated test confirms explanation field is never empty in any F-01 response. |
| FR-008 | Must Have | The system SHALL include a confidence indicator in every F-01 response distinguishing threat-intelligence-based verdicts from model-based verdicts. | Response contains a confidence indicator field with one of the defined values. |

#### F-02: Message & Email Scam Detection

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-009 | Must Have | The system SHALL accept free-form text input for scam classification. | Text submitted via the F-02 endpoint is accepted and processed. |
| FR-010 | Must Have | The system SHALL validate that text input is not empty before classification. | An empty text input returns a validation error — not a risk verdict. |
| FR-011 | Must Have | The system SHALL classify submitted text using the trained scam NLP classifier. | The classifier returns a scam probability score for any non-empty text input. |
| FR-012 | Must Have | The system SHALL return a risk verdict (Safe through Critical) with a plain-language explanation for all F-02 requests. | Every F-02 response contains a populated risk level and a non-empty explanation field. |
| FR-013 | Must Have | The system SHALL include the standard AI disclaimer in every F-02 response. | Automated test confirms disclaimer field is present in every F-02 response. |
| FR-014 | Should Have | The system SHALL indicate when submitted text is detected as non-English, with a note that Phase 1 analysis is optimised for English. | A Hindi-only input returns a response with a language-limitation notice. |
| FR-015 | Should Have | The system SHALL return a scam category hint (e.g., KYC scam, OTP scam, job scam) when classifier confidence is sufficient. | A known KYC scam message returns a response including a scam category field. |

#### F-03: Screenshot Scam Scanner

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-016 | Must Have | The system SHALL accept image file uploads (JPEG, PNG) for screenshot scanning. | A valid JPEG or PNG file upload is accepted and processed. |
| FR-017 | Must Have | The system SHALL validate file type and file size before processing. | An oversized file or unsupported format returns a validation error before OCR is attempted. |
| FR-018 | Must Have | The system SHALL extract text from uploaded screenshots using PaddleOCR. | Text is extracted from a clear screenshot of a scam message without error. |
| FR-019 | Must Have | The system SHALL include an OCR quality indicator in the response. | Every F-03 response contains an OCR quality field indicating extraction confidence. |
| FR-020 | Must Have | The system SHALL pass extracted text through the F-02 scam NLP classifier and return a risk verdict with explanation. | A screenshot of a scam message returns a Moderate Risk or higher verdict. |
| FR-021 | Must Have | The system SHALL return the extracted text in the response for user transparency. | Every F-03 response includes the extracted text field (empty if no text was extracted). |
| FR-022 | Must Have | The system SHALL return "no scam-related text detected" when OCR extracts no text — it SHALL NOT return a Safe risk verdict in this case. | A screenshot with no readable text returns a "no text detected" response, not a Safe verdict. |

#### F-04: QR Code Scam Scanner

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-023 | Must Have | The system SHALL accept QR code image uploads for scanning. | A valid QR code image upload is accepted and decoded. |
| FR-024 | Must Have | The system SHALL decode the QR code and identify the content type (URL, contact, WiFi, plain text, other). | A QR code encoding a URL is decoded; the content type is correctly identified as URL. |
| FR-025 | Must Have | The system SHALL route decoded URL content through the F-01 phishing URL analysis pipeline. | A QR code encoding a known phishing URL returns a High Risk or Critical verdict via F-01 analysis. |
| FR-026 | Must Have | The system SHALL return an appropriate non-risk response for non-URL QR content without applying URL analysis. | A QR code encoding a vCard returns a content-type identification response, not a phishing verdict. |
| FR-027 | Must Have | The system SHALL return the decoded QR content in the response. | Every F-04 response includes the decoded content field. |
| FR-028 | Must Have | The system SHALL return a clear error for unreadable or malformed QR codes. | An unreadable QR image returns an error response — not a risk verdict. |

#### F-05: Fake Profile Verification

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-029 | Must Have | The system SHALL accept a set of profile signals as input for fake profile risk assessment. | A valid profile signal submission is accepted and processed. |
| FR-030 | Must Have | The system SHALL return a risk assessment (not identity verification) with a mandatory identity-verification disclaimer. | Every F-05 response includes the identity-verification disclaimer. |
| FR-031 | Must Have | The system SHALL return an "insufficient signals" response when the submitted signal set is too sparse for assessment. | A submission with no meaningful signals returns an insufficient-signals response, not a risk verdict. |
| FR-032 | Must Have | The system SHALL include a non-empty explanation identifying which submitted signals contributed to the risk level. | Every risk verdict in an F-05 response includes a populated explanation field. |
| FR-033 | Should Have | The system SHALL classify submitted profile signals using the trained fake profile risk model (XGBoost or LightGBM). | A profile submission with high-risk signals returns Moderate Risk or higher. |

#### F-06: Deepfake Detection (Research/Experimental)

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-034 | Must Have | The system SHALL display a prominent "Experimental" label on the F-06 feature entry point before any media is submitted. | UI test confirms Experimental label is present on the feature entry point. |
| FR-035 | Must Have | The system SHALL accept image and short video file uploads for deepfake analysis. | A valid JPEG image upload is accepted and processed. |
| FR-036 | Must Have | The system SHALL include the Research/Experimental disclaimer in every F-06 response. | Automated test confirms Research/Experimental disclaimer is present in every F-06 response. |
| FR-037 | Must Have | The system SHALL return "no face detected" when the uploaded media contains no detectable human face — it SHALL NOT return a deepfake risk verdict. | An image with no face returns a "no face detected" response, not a risk verdict. |
| FR-038 | Must Have | The system SHALL include a plain-language confidence indicator in every F-06 response. | Every F-06 response includes a confidence indicator field. |
| FR-039 | Must Have | The system SHALL validate file type and size before processing. | An oversized file returns a validation error before analysis is attempted. |

#### F-07: Mule Account Detection (Research/Experimental)

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-040 | Must Have | The system SHALL display a prominent "Experimental" label on the F-07 feature entry point before any signals are submitted. | UI test confirms Experimental label is present on the feature entry point. |
| FR-041 | Must Have | The system SHALL accept account signal inputs for mule account risk assessment. | A valid signal submission is accepted and processed. |
| FR-042 | Must Have | The system SHALL include all three mandatory disclaimers in every F-07 response: Research/Experimental status, dataset domain mismatch, and general statistical indicator notice. | Automated test confirms all three disclaimer fields are present in every F-07 response. |
| FR-043 | Must Have | The system SHALL return an "insufficient signals" response when submitted signals are insufficient for assessment. | A sparse signal submission returns an insufficient-signals response. |
| FR-044 | Must Have | The system SHALL include a non-empty explanation of which signals contributed to the risk level. | Every F-07 risk verdict response includes a populated explanation field. |


### 2.2 Pillar 2 — Protect

#### F-08: Scam Call Blocking

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-045 | Must Have | The system SHALL accept a phone number input for scam risk lookup. | A valid 10-digit Indian phone number is accepted and looked up. |
| FR-046 | Must Have | The system SHALL validate and normalise phone number format (10-digit, +91 prefix, 0xx prefix) before lookup. | An invalid format returns a validation error with formatting guidance. |
| FR-047 | Must Have | The system SHALL return a risk verdict and explanation based on threat/reputation data lookup. | A number on the configured threat list returns Moderate Risk or higher with an explanation. |
| FR-048 | Must Have | The system SHALL NEVER return a risk verdict for emergency service numbers (100, 112, 108, 102, and equivalents). | Submitting emergency number 112 returns a "this is an emergency service number" response, not a risk verdict. |
| FR-049 | Must Have | The system SHALL include a data source indicator and disclaimer in every F-08 response. | Every F-08 response contains both a data-source field and a disclaimer field. |
| FR-050 | Must Have | The system SHALL return Safe or Low Risk with an explicit "absence of data does not confirm safety" note for numbers with no threat data. | A number with no threat intelligence data returns Safe or Low Risk with the absence-of-data note. |

#### F-09: Password Security Checker

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-051 | Must Have | The system SHALL accept a password string for security assessment. | A password input is accepted and assessed. |
| FR-052 | Must Have | The system SHALL validate that the password input is not empty before assessment. | An empty password input returns a validation error — not a security verdict. |
| FR-053 | Must Have | The system SHALL evaluate password entropy, length, character diversity, and common password patterns. | "password123" returns a Very Weak verdict; a 16-character random mixed-case alphanumeric+symbol string returns Strong or Very Strong. |
| FR-054 | Must Have | The system SHALL return a security verdict with at least one specific, actionable improvement recommendation for every non-maximum verdict. | Every verdict below Very Strong includes at least one specific improvement recommendation. |
| FR-055 | Must Have | The system SHALL display the "do not enter your actual account password" notice before and after assessment. | UI test confirms the notice is present on the feature entry point and in the result. |
| FR-056 | Must Have | The system SHALL NOT store or log the submitted password value in any database, log file, or persistent storage. | Security audit and code review confirm no password value is written to any storage or log. |

#### F-10: Secure File Encryption

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-057 | Must Have | The system SHALL accept a file upload and an encryption password to produce an AES-256-GCM encrypted file. | A file encrypted with a password produces an encrypted output file available for download. |
| FR-058 | Must Have | The system SHALL derive the encryption key from the user-supplied password using Argon2id. | Encryption uses Argon2id-derived key; this is verifiable in code review. |
| FR-059 | Must Have | The system SHALL accept an encrypted file and the correct password to produce the original decrypted file. | A file encrypted with password X is successfully decrypted with password X, producing the original file. |
| FR-060 | Must Have | The system SHALL return an error if decryption is attempted with an incorrect password — it SHALL NOT return any file content. | Decryption with a wrong password returns an error response and no file content. |
| FR-061 | Must Have | The system SHALL NOT retain the plaintext version of the uploaded file after the encrypted output is provided. | Security audit confirms no plaintext file persists after the encrypt operation completes. |
| FR-062 | Must Have | The system SHALL validate file type and file size before processing. | A file exceeding the size limit returns a validation error before any processing. |
| FR-063 | Must Have | The system SHALL display the password-loss warning prominently before and after encryption. | UI test confirms password-loss warning is present on the encryption entry point and in the result. |
| FR-064 | Must Have | The system SHALL generate a fresh random nonce for every encryption operation. | Code review confirms a new random nonce is generated per encryption call; nonces are not reused. |

### 2.3 Pillar 3 — Assist & Respond

#### F-11: AI Cybersecurity Assistant

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-065 | Must Have | The system SHALL accept natural language text queries for the AI assistant. | A text query is submitted and a response is returned. |
| FR-066 | Must Have | The system SHALL retrieve relevant content from the knowledge base via pgvector similarity search before generating a response. | A question about a known topic (e.g., KYC scam) returns a response referencing knowledge base content. |
| FR-067 | Must Have | The system SHALL include the mandatory AI disclaimer in every F-11 response. | Automated test confirms disclaimer is present in every F-11 response. |
| FR-068 | Must Have | The system SHALL return a polite out-of-scope response for queries entirely outside the cybersecurity domain. | A query like "What is the capital of France?" returns an out-of-scope response, not a cybersecurity answer. |
| FR-069 | Must Have | The system SHALL decline to provide legal, financial, or medical advice and indicate this to the user. | A query requesting legal advice returns the appropriate refusal response. |
| FR-070 | Must Have | The system SHALL acknowledge knowledge gaps rather than fabricating answers when no relevant knowledge base content is retrieved. | A query on a topic not in the knowledge base returns a gap-acknowledgement response, not a fabricated answer. |
| FR-071 | Must Have | F-11 SHALL NOT be deployed until ADR-013 (LLM provider) is resolved and the provider is configured. | F-11 endpoint returns a "feature not yet available" response in any environment where the LLM provider is not configured. |

#### F-12: Cyber Risk Score

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-072 | Must Have | The system SHALL compute a Cyber Risk Score for each authenticated user based on the defined Phase 1 signal set. | An authenticated user's score is returned when the F-12 endpoint is called. |
| FR-073 | Must Have | The system SHALL use exclusively the Phase 1 controlled signal set for score computation. | Code review confirms no signals beyond the defined Phase 1 set contribute to the score. |
| FR-074 | Must Have | The system SHALL return a score breakdown identifying each contributing signal and its contribution direction (positive or negative). | Every F-12 response includes a breakdown field listing all contributing signals. |
| FR-075 | Must Have | The system SHALL display the score disclaimer with every score presentation. | Automated test confirms disclaimer field is present in every F-12 response. |
| FR-076 | Must Have | The system SHALL return a baseline score with an onboarding prompt for new users with no activity and no questionnaire responses. | A new user with zero activity receives a baseline score and an onboarding prompt — not an error. |
| FR-077 | Must Have | The system SHALL update the score when the user completes new in-app activities or updates their questionnaire responses. | Completing a high-risk scan changes the score in the expected direction; change is reflected in the next score retrieval. |
| FR-078 | Must Have | The system SHALL provide improvement action recommendations linked to the lowest-scoring signals. | F-12 response includes at least one improvement action recommendation. |
| FR-079 | Should Have | The system SHALL provide basic score history showing whether the score has improved or worsened over time. | A user who has improved their score over multiple sessions can see a positive trend indicator. |

#### F-13: Location-Based Scam Alerts

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-080 | Must Have | The system SHALL accept a user's city or region as input (self-selected dropdown or browser geolocation at city precision). | A city selection returns relevant alerts for that city if they exist. |
| FR-081 | Must Have | The system SHALL request browser geolocation permission only with an explicit user consent prompt. | Browser geolocation is not accessed without the user seeing and acknowledging the consent prompt. |
| FR-082 | Must Have | The system SHALL NOT store user location data persistently without explicit user consent. | Location data is used for the geospatial query and is not retained in the database without consent. |
| FR-083 | Must Have | The system SHALL return a "no recent alerts for your area" response for locations with no alerts — not an error or blank screen. | Selecting a city with no alerts returns the defined "no alerts" message. |
| FR-084 | Must Have | The system SHALL include a data freshness indicator and disclaimer in every F-13 response. | Every F-13 response includes last-updated timestamp and disclaimer fields. |
| FR-085 | Should Have | The system SHALL return alerts for all major Indian metropolitan areas (Mumbai, Delhi, Bengaluru, Chennai, Hyderabad, Kolkata, Pune) if alert data exists for those areas. | Alert data coverage for major metros is verified before Phase 1 launch. |

### 2.4 Pillar 4 — Learn & Prevent

#### F-14: Cyber Safety Hub

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-086 | Must Have | The system SHALL display a Daily Cyber Safety Tip on the hub home page. | A tip is displayed on hub access; the same tip is not repeated on consecutive calendar days if the tip set has more than one entry. |
| FR-087 | Must Have | The system SHALL provide a Cybersecurity Quiz with a minimum of 10 questions covering at least 3 different Indian threat categories. | The quiz contains at least 10 questions tagged across at least 3 threat categories. |
| FR-088 | Must Have | The system SHALL display the correct answer and a brief explanation after each quiz question is answered. | After submitting a quiz answer, the correct answer and explanation are displayed regardless of whether the user was correct. |
| FR-089 | Must Have | The system SHALL provide awareness articles covering at minimum: UPI fraud, WhatsApp scams, OTP theft, phishing links, and scam calls. | Content audit confirms articles exist for all five required threat categories. |
| FR-090 | Must Have | All Cyber Safety Hub content (tips, quiz questions, articles) SHALL have been reviewed for factual accuracy before publication. | A content review sign-off record exists for all published content. |
| FR-091 | Should Have | The system SHALL display preventive guidance content (what to do if you receive a scam call, message, etc.). | Preventive guidance pages are accessible from the hub. |

### 2.5 Authentication and Account Management

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-092 | Must Have | The system SHALL support user registration with email address and password. | A valid email + password combination successfully creates an account. |
| FR-093 | Must Have | The system SHALL send an email verification link upon registration and require email verification before account activation. | An unverified account cannot log in. |
| FR-094 | Must Have | The system SHALL return a generic error on duplicate email registration — it SHALL NOT indicate whether the email is registered. | Registering with an already-registered email returns the same error message as any other registration failure — no enumeration. |
| FR-095 | Must Have | The system SHALL NOT allow account creation without the user ticking the data consent checkbox. | Submitting registration without the consent checkbox returns a validation error. |
| FR-096 | Must Have | The system SHALL support login with email and password, returning JWT access and refresh tokens on success. | Valid credentials return JWT tokens; invalid credentials return a generic error. |
| FR-097 | Must Have | The system SHALL return a generic "invalid email or password" error on login failure — it SHALL NOT specify which field is wrong. | Failed login always returns the same generic error message regardless of which credential is wrong. |
| FR-098 | Must Have | The system SHALL support optional TOTP 2FA enrollment via QR code and authenticator app. | A user can enroll 2FA by scanning the QR code in an authenticator app and confirming with a valid TOTP code. |
| FR-099 | Must Have | The system SHALL require a valid TOTP code at login for users with 2FA enabled. | A user with 2FA enabled cannot complete login without a valid TOTP code. |
| FR-100 | Must Have | The system SHALL generate backup codes at 2FA enrollment and display them exactly once. | Backup codes are shown during enrollment and cannot be retrieved again after the enrollment session ends. |
| FR-101 | Must Have | The system SHALL support password reset via a time-limited email link. | A user who requests a password reset receives an email with a link; clicking the link allows setting a new password. |
| FR-102 | Must Have | The system SHALL invalidate all active sessions after a successful password reset. | After password reset, previously issued JWTs are no longer accepted. |
| FR-103 | Must Have | The system SHALL support account deletion with password re-entry confirmation. | Account deletion requires successful password re-entry; single-click deletion is not permitted. |
| FR-104 | Must Have | The system SHALL delete or anonymise user personal data after account deletion in accordance with the defined retention policy. | After account deletion, the user's PII is not accessible via the application. |
| FR-105 | Must Have | The system SHALL apply rate limiting to login attempts and block or throttle after a defined number of consecutive failures. | After the defined number of failed attempts (TBD), further attempts are rate-limited or temporarily blocked. |

### 2.6 Cross-Cutting Requirements

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| FR-106 | Must Have | The system SHALL use the 5-level risk severity model (Safe / Low Risk / Moderate Risk / High Risk / Critical) consistently across all detection features (F-01, F-02, F-03, F-04, F-05, F-06, F-07, F-08). | All detection feature responses use only the five defined risk level values. |
| FR-107 | Must Have | Every risk verdict produced by any feature SHALL be accompanied by a non-empty plain-language explanation. | Automated test confirms explanation field is never empty in any risk verdict response across all features. |
| FR-108 | Must Have | All AI/ML outputs (F-01 through F-08, F-11, F-12) SHALL include appropriate disclaimer text as defined in CSHAKTI-PRD-001 §4.3. | Automated test confirms disclaimer text is present in responses from all AI/ML features. |
| FR-109 | Must Have | Research/Experimental features (F-06, F-07) SHALL be labelled "Experimental" in the UI entry point before any user input is submitted. | UI tests confirm Experimental label is present on F-06 and F-07 entry points. |
| FR-110 | Must Have | The system SHALL NOT claim 100% detection, perfect accuracy, guaranteed protection, zero false positives, or zero false negatives in any user-facing text. | Content review of all UI copy confirms absence of prohibited claim language. |
| FR-111 | Must Have | All protected API endpoints SHALL require a valid JWT token for access. | Requests to protected endpoints without a valid JWT return HTTP 401. |
| FR-112 | Must Have | The system SHALL enforce RBAC — user-role tokens SHALL NOT be able to access admin-role endpoints. | A user-role JWT used against an admin endpoint returns HTTP 403. |


---

## 3. Non-Functional Requirements

### 3.1 Performance

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-PERF-001 | Must Have | Lightweight synchronous operations (F-09, F-12 read, F-13 query, F-14 content fetch, auth token validation) SHALL complete within a target response time to be set after benchmarking. | Performance target: TBD after benchmarking. Benchmark must be completed before Phase 1 launch. |
| NFR-PERF-002 | Must Have | Standard ML inference operations (F-01 URL scan, F-02 text scan, F-08 lookup) SHALL complete within a target response time to be set after benchmarking. | Performance target: TBD after benchmarking. |
| NFR-PERF-003 | Must Have | Heavy inference operations (F-03 OCR+NLP, F-05 profile, F-06 deepfake, F-07 mule, F-11 LLM) SHALL be handled via Celery async workers; the API SHALL NOT block on these operations. | Requests for async operations return an immediate task-accepted acknowledgement with a task ID; result is retrieved separately. |
| NFR-PERF-004 | Must Have | File upload operations (F-10, F-03, F-06) SHALL provide user-visible upload progress indication. | Upload progress indicator is visible in the UI during file upload. |
| NFR-PERF-005 | Must Have | File size limits for all upload-accepting features SHALL be defined during engineering design and enforced. | File size limits are defined, documented, and enforced before launch. |

### 3.2 Security

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-SEC-001 | Must Have | All user passwords SHALL be stored as Argon2id or bcrypt hashes. Plaintext password storage is prohibited. | Security audit and code review confirm no plaintext passwords exist in any storage or log. |
| NFR-SEC-002 | Must Have | File encryption in F-10 SHALL use AES-256-GCM. | Code review confirms AES-256-GCM is used; no other encryption algorithm is used for user files. |
| NFR-SEC-003 | Must Have | All API communications SHALL use HTTPS with TLS 1.2 minimum; TLS 1.3 preferred. | SSL/TLS configuration verified before production launch. |
| NFR-SEC-004 | Must Have | All protected API endpoints SHALL require valid JWT authentication. | Unauthenticated requests to protected endpoints return HTTP 401. |
| NFR-SEC-005 | Must Have | Rate limiting SHALL be applied to all public-facing endpoints. Specific thresholds are TBD pending threat-model review (ADR-026). | Rate limiting is active in production; threshold values are documented and tracked. |
| NFR-SEC-006 | Must Have | All user inputs and external data SHALL be validated and sanitised before processing. | Input validation tests confirm boundary and injection-style inputs return controlled error responses. |
| NFR-SEC-007 | Must Have | CORS SHALL be configured to permit only explicitly approved origins. Wildcard `*` origins are prohibited in production. | Production CORS configuration does not contain `*` as an allowed origin. |
| NFR-SEC-008 | Must Have | Security configuration parameters (Argon2id parameters, JWT expiry, refresh token lifetime, rate limit thresholds) SHALL be TBD until determined through proper security benchmarking and threat-model review. | Security configuration values are externalised as environment variables; no values are hard-coded in source code. |
| NFR-SEC-009 | Must Have | Required HTTP security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy) SHALL be present on all API responses. | Security header scan of production API confirms all required headers are present. |
| NFR-SEC-010 | Must Have | API keys, LLM provider keys, and database credentials SHALL be managed via environment variables and SHALL NOT be committed to source control. | Repository scan confirms no secrets are committed. CI/CD pipeline includes a secrets-scanning step. |
| NFR-SEC-011 | Must Have | AES-256-GCM encryption in F-10 SHALL use a fresh random nonce for every encryption operation. | Code review confirms nonce generation is per-operation and random. |

### 3.3 Privacy

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-PRIV-001 | Must Have | Sensitive personal data SHALL be minimised, protected at rest using appropriate encryption and access controls, and never stored unnecessarily in plaintext. | Data classification and protection measures are documented and reviewed during engineering design. |
| NFR-PRIV-002 | Must Have | The system SHALL provide user account deletion functionality that removes or anonymises the user's personal data. | Account deletion flow is tested; deleted user's PII is not accessible via the application after deletion. |
| NFR-PRIV-003 | Must Have | The system SHALL display a data collection disclosure and require informed consent before account creation. | Automated test confirms registration cannot be completed without the consent checkbox. |
| NFR-PRIV-004 | Must Have | The system SHALL provide user data access, correction, and deletion capabilities accessible from account settings. | UI test confirms access, correction, and deletion functions are accessible from account settings. |
| NFR-PRIV-005 | Must Have | User location data (F-13) SHALL NOT be stored persistently without explicit user consent. | Location data handling code is reviewed; persistent storage requires explicit consent flow. |
| NFR-PRIV-006 | Must Have | Uploaded files in F-10 (plaintext) SHALL NOT be permanently stored server-side after the encrypted output is provided to the user. | Security audit confirms plaintext file is not present in storage after successful encrypt operation. |
| NFR-PRIV-007 | Must Have | India IT Act 2000 and DPDP Act 2023 are referenced as compliance consideration areas. Actual compliance obligations SHALL be verified with qualified legal counsel before launch. | Legal review is completed and documented before Phase 1 public launch. |

### 3.4 Scalability

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-SCALE-001 | Must Have | The backend API layer SHALL support horizontal scaling (multiple instances behind a load balancer). | The API is stateless (JWT-based auth, no server-side session state); horizontal scaling is validated in engineering design. |
| NFR-SCALE-002 | Must Have | Heavy ML inference SHALL be handled by Celery workers that can be scaled independently of the API layer. | Celery worker count is configurable; worker scale-out does not require API changes. |
| NFR-SCALE-003 | Should Have | The database connection pool SHALL be configured to handle expected concurrent load without connection exhaustion. | Connection pool configuration is defined during engineering design based on expected user scale. |

### 3.5 Reliability

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-REL-001 | Must Have | Availability target for Phase 1: TBD after deployment architecture is finalised. | Availability target is defined and monitored after Phase 1 launch. |
| NFR-REL-002 | Must Have | The system SHALL handle AI/ML service failures (LLM API unavailability, Celery worker failure) gracefully without exposing internal errors or stack traces to users. | Simulated LLM API failure returns a user-friendly degraded response — not a raw error. |
| NFR-REL-003 | Must Have | The system SHALL handle external dependency failures (threat intelligence API unavailability) gracefully and inform users that real-time threat data is temporarily unavailable. | Simulated threat intelligence API failure returns a fallback response with a user-visible note. |
| NFR-REL-004 | Should Have | The system SHALL implement health check endpoints for all services to support monitoring and deployment health validation. | Health check endpoints return HTTP 200 when services are operational. |

### 3.6 Usability

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-USE-001 | Must Have | The application SHALL be a responsive web application functional on modern desktop and mobile browsers (Chrome, Firefox, Safari, Edge — current and previous major version). | Cross-browser testing confirms functional operation across all four browsers on desktop and mobile. |
| NFR-USE-002 | Must Have | All risk verdicts and AI/ML outputs SHALL be expressed in plain language accessible to a non-technical Indian consumer. | Usability testing with representative users confirms comprehension of verdict language. |
| NFR-USE-003 | Must Have | All disclaimer text (AI outputs, Research/Experimental features, security caveats) SHALL be visible in the UI without requiring user action to reveal (e.g., not hidden in expandable tooltips for primary warnings). | UI review confirms primary disclaimers are visible without user interaction. |
| NFR-USE-004 | Should Have | The application SHALL display meaningful loading states for all asynchronous operations — not blank screens. | UI test confirms loading indicators are present for all async feature operations. |
| NFR-USE-005 | Should Have | Error messages displayed to users SHALL be plain-language and actionable — not raw technical errors or stack traces. | All user-facing error messages are reviewed for plain-language compliance before launch. |

### 3.7 Accessibility

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-ACC-001 | Must Have | The application SHALL target WCAG 2.1 Level AA accessibility. Full compliance requires expert accessibility review and testing — automated tools alone are not sufficient. | Automated accessibility scan (e.g., axe) passes with no critical or serious violations. Expert accessibility review completed before launch. |
| NFR-ACC-002 | Must Have | All images SHALL have meaningful alt text. Decorative images SHALL have empty alt attributes. | Automated accessibility scan confirms alt text compliance. |
| NFR-ACC-003 | Must Have | All form inputs SHALL have associated label elements. | Automated accessibility scan confirms all form inputs have labels. |
| NFR-ACC-004 | Must Have | Risk level information SHALL NOT be conveyed by colour alone — text labels SHALL accompany colour coding. | UI review confirms risk levels use both colour and text labels. |
| NFR-ACC-005 | Must Have | The application SHALL be keyboard-navigable — all interactive elements reachable and operable via keyboard. | Keyboard navigation test confirms all interactive elements are reachable. |
| NFR-ACC-006 | Must Have | Touch targets on mobile SHALL meet minimum size requirements (44×44px per WCAG 2.5.5). | UI design review confirms touch target sizing. |

### 3.8 Maintainability

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-MAINT-001 | Must Have | All ML models SHALL be versioned using MLflow with experiment tracking. | MLflow runs exist for all trained models; each deployment-ready model version is tagged in MLflow. |
| NFR-MAINT-002 | Must Have | The change control process defined in CSHAKTI-CONST-001 §14 SHALL be followed for all modifications to locked requirements. | No locked requirement is changed without a corresponding ADR entry in `docs/00-decisions.md`. |
| NFR-MAINT-003 | Must Have | Database schema changes SHALL be managed via versioned migrations. | All schema changes are applied via migration scripts; no manual schema changes in any environment. |
| NFR-MAINT-004 | Must Have | All services SHALL be containerised using Docker. | All deployable services have Dockerfiles; Docker Compose starts all services for local development. |
| NFR-MAINT-005 | Should Have | Backend code SHALL maintain a minimum test coverage threshold (TBD) enforced in CI/CD. | CI/CD pipeline fails if coverage drops below the defined threshold. |
| NFR-MAINT-006 | Should Have | All API endpoints SHALL have auto-generated documentation (FastAPI/OpenAPI). | OpenAPI documentation is accessible at the `/docs` endpoint of the running API. |

### 3.9 Portability

| ID | Priority | Description | Acceptance Criterion |
|---|---|---|---|
| NFR-PORT-001 | Must Have | All environment-specific configuration (API keys, database URLs, LLM provider keys, S3 credentials) SHALL be externalised as environment variables. | Code review confirms no environment-specific values are hard-coded in source. |
| NFR-PORT-002 | Must Have | Object storage access SHALL use S3-compatible APIs to preserve provider portability. | Storage client uses only S3-compatible API calls; no provider-specific SDK features used without documented justification. |
| NFR-PORT-003 | Should Have | The LLM integration SHALL use a provider adapter pattern to allow provider switching with minimal code changes. | LLM provider change requires only adapter configuration changes, not core pipeline changes. |

---

## 4. Interface Requirements

### 4.1 User Interface

- Phase 1 is a responsive web application (ADR-025)
- Mobile-first layout preferred; validated in UI/UX design phase
- Supported browsers: Chrome, Firefox, Safari, Edge (current and previous major version)
- Minimum supported screen width: 320px
- Touch-friendly on mobile browsers

### 4.2 API Interface

- RESTful API implemented with FastAPI
- Request and response format: JSON
- Authentication: JWT Bearer token in Authorization header for all protected endpoints
- API documentation: auto-generated via FastAPI/OpenAPI, accessible at `/docs` (development) and `/redoc`
- Error responses: consistent JSON format with `error_code`, `message`, and `details` fields
- All endpoints versioned (e.g., `/api/v1/...`)

### 4.3 External Service Interfaces

| Service | Interface Type | Status | Notes |
|---|---|---|---|
| Threat intelligence API (F-01, F-04, F-08, F-13) | REST API (provider TBD) | ADR-032 Open | Must support query-by-URL, query-by-phone-number |
| LLM API (F-11) | REST API (provider TBD) | ADR-013 Open | Must support chat completion with streaming |
| PaddleOCR (F-03) | Local Python library | ADR-022 Provisional | Deployed within backend service |
| QR decode library (F-04) | Local Python library | TBD in implementation | Standard library, no external API |
| S3-compatible object storage | S3 API | ADR-031 Open | Used for file storage and model artefacts |

---

## 5. System Constraints

### 5.1 Technology Constraints

- The technology stack is frozen as defined in CSHAKTI-CONST-001 §6 and ADR-002. No deviations without a recorded ADR.
- PostgreSQL with pgvector and PostGIS is the only database. No additional databases may be introduced without a recorded ADR.
- Python 3.11+ is required for the backend. No other backend language is permitted.
- Microservices architecture is not used in Phase 1. The modular monolith pattern is enforced (ADR-014).

### 5.2 Regulatory Constraints

- IT Act 2000 and DPDP Act 2023 are compliance consideration areas requiring authoritative legal verification before launch (ADR-030, CSHAKTI-CONST-001 §10).
- CyberShakti must not claim regulatory compliance in any communication without proper legal verification.
- Data residency requirements must be verified with legal counsel before deployment target is finalised (ADR-031 consequence).

### 5.3 Operational Constraints

- Phase 1 is a responsive web application only. No native Android or iOS app (ADR-025).
- Android OS-level call blocking is not available (ADR-018).
- F-11 AI Cybersecurity Assistant cannot be deployed until ADR-013 (LLM provider) is resolved.
- F-01, F-04, F-08, F-13 cannot be fully deployed until ADR-032 (threat intelligence sources) is resolved.
- F-10 and other file-dependent features cannot be fully deployed until ADR-031 (object storage provider) is resolved.
- F-06 and F-07 are Research/Experimental and must not be represented as production-grade without empirical validation.
- Security configuration parameters (Argon2id, JWT, rate limits) must not be permanently set without benchmarking (ADR-026).
- Model training is conducted on Kaggle GPU and Google Colab GPU — no dedicated cloud GPU infrastructure (CSHAKTI-CONST-001 §6.16).

---

## 6. Assumptions and Dependencies

### 6.1 Assumptions

These assumptions are inherited from CSHAKTI-PVS-001 §10.1. If any assumption proves invalid, the affected requirements must be reviewed.

| ID | Assumption |
|---|---|
| A-01 | Indian consumers primarily access CyberShakti via mobile browsers — mobile-first UX is the correct design direction. |
| A-02 | Phase 1 users interact primarily in English. |
| A-03 | Phishing URL training datasets (PhishTank, URLhaus) are accessible and licensable. |
| A-04 | Scam text training datasets are sufficient in quality and volume for F-02 model training. |
| A-05 | GPU compute via Kaggle and Google Colab is available for model training. |
| A-06 | A reputable threat intelligence source with India-specific coverage will be identified (ADR-032). |
| A-07 | An LLM API provider meeting privacy, cost, and capability requirements will be selected (ADR-013). |
| A-08 | Regulatory obligations (IT Act 2000, DPDP Act 2023) will be achievable within the Phase 1 architecture. |
| A-09 | Research dataset access (FaceForensics++, Celeb-DF, DFDC, Elliptic/Elliptic2) will be obtainable within licensing terms. |

### 6.2 External Dependencies

| Dependency | Required By | Status |
|---|---|---|
| Threat intelligence API provider | FR-004, FR-047, FR-025 (via F-01), FR-085 | ADR-032 Open |
| LLM API provider | FR-065–FR-071 | ADR-013 Open |
| S3-compatible object storage provider | FR-057–FR-064 (F-10), FR-016–FR-022 (F-03) | ADR-031 Open |
| Backend deployment platform | All FR | TBD — ADR-004 consequence |
| PaddleOCR (local) | FR-018 | ADR-022 Provisional |
| Research datasets | F-06, F-07 model training | Dataset access must be verified |
| Legal review (regulatory compliance) | NFR-PRIV-007 | Required before launch |

---

## 7. Out-of-Scope Requirements

The following are formally out of Phase 1 scope. They are stated as SHALL NOT requirements to prevent implementation drift.

| ID | Out-of-Scope Requirement |
|---|---|
| OOS-001 | The system SHALL NOT implement Android OS-level automatic call blocking. |
| OOS-002 | The system SHALL NOT provide a native Android application. |
| OOS-003 | The system SHALL NOT provide a native iOS application. |
| OOS-004 | The system SHALL NOT perform identity verification for any feature. F-05 is risk assessment only. |
| OOS-005 | The system SHALL NOT use ML-based risk score prediction in Phase 1. F-12 uses a weighted engine only. |
| OOS-006 | The system SHALL NOT deploy Graph Neural Networks (PyTorch Geometric) as a production feature in Phase 1. |
| OOS-007 | The system SHALL NOT support social login (Google, GitHub, or other OAuth providers) in Phase 1. |
| OOS-008 | The system SHALL NOT implement a standalone "I've Been Scammed" incident response workflow as a separate top-level feature. |
| OOS-009 | The system SHALL NOT implement enterprise security management, multi-user organisational accounts, or SIEM integration. |
| OOS-010 | The system SHALL NOT implement real-time SMS or call screening. |
| OOS-011 | The system SHALL NOT implement automatic content blocking or content removal on external platforms. |
| OOS-012 | The system SHALL NOT implement dark web monitoring. |
| OOS-013 | The system SHALL NOT implement a network traffic monitor or firewall. |
| OOS-014 | The system SHALL NOT implement an antivirus or anti-malware scanning engine. |
| OOS-015 | The system SHALL NOT provide Hindi-language or regional-language UI in Phase 1. |
| OOS-016 | The system SHALL NOT represent F-06 or F-07 outputs as production-grade, definitive, or legally admissible without empirical validation. |

---

## 8. Requirements Traceability Matrix

This matrix links every functional requirement to its upstream PRD source, relevant constitution principle, applicable ADR, and downstream test case placeholder (TC-NNN — to be assigned during Stage 3).

**Legend:**
- **FR ID**: Requirement identifier
- **PRD Source**: Source feature ID or section in CSHAKTI-PRD-001
- **Const. Principle**: Relevant constitutional principle(s)
- **ADR**: Relevant ADR(s)
- **TC Placeholder**: Test case ID (assigned in Stage 3)

| FR ID | Description Summary | PRD Source | Const. Principle | ADR | TC |
|---|---|---|---|---|---|
| FR-001 | Accept URL for phishing analysis | F-01 | P4, P5 | ADR-008 | TC-001 |
| FR-002 | Validate URL format before analysis | F-01 | P2, P6 | ADR-008 | TC-002 |
| FR-003 | URL feature engineering | F-01 | P4 | ADR-008 | TC-003 |
| FR-004 | Threat intelligence lookup | F-01 | P5 | ADR-032 | TC-004 |
| FR-005 | XGBoost classification | F-01 | P4, P5 | ADR-008 | TC-005 |
| FR-006 | Return 5-level risk verdict | F-01 | P4, P8 | ADR-001 | TC-006 |
| FR-007 | Non-empty explanation with verdict | F-01 | P4, P8 | ADR-001 | TC-007 |
| FR-008 | Confidence indicator in response | F-01 | P5 | ADR-008 | TC-008 |
| FR-009 | Accept text for scam classification | F-02 | P4 | ADR-009 | TC-009 |
| FR-010 | Validate non-empty text input | F-02 | P2, P6 | ADR-009 | TC-010 |
| FR-011 | NLP classifier on text | F-02 | P4, P5 | ADR-009 | TC-011 |
| FR-012 | Return risk verdict + explanation | F-02 | P4, P8 | ADR-009 | TC-012 |
| FR-013 | AI disclaimer in F-02 response | F-02 | P5 | ADR-009 | TC-013 |
| FR-014 | Non-English language notice | F-02 | P8 | ADR-009 | TC-014 |
| FR-015 | Scam category hint | F-02 | P4, P8 | ADR-009 | TC-015 |
| FR-016 | Accept image for screenshot scan | F-03 | P4 | ADR-022 | TC-016 |
| FR-017 | File type/size validation | F-03 | P2, P6 | ADR-022 | TC-017 |
| FR-018 | PaddleOCR text extraction | F-03 | P4 | ADR-022 | TC-018 |
| FR-019 | OCR quality indicator in response | F-03 | P5, P8 | ADR-022 | TC-019 |
| FR-020 | NLP classification on extracted text | F-03 | P4, P5 | ADR-009, ADR-022 | TC-020 |
| FR-021 | Return extracted text for transparency | F-03 | P4, P8 | ADR-022 | TC-021 |
| FR-022 | No-text response for empty OCR | F-03 | P5, P8 | ADR-022 | TC-022 |
| FR-023 | Accept QR image for scanning | F-04 | P4 | ADR-023 | TC-023 |
| FR-024 | QR decode and content type ID | F-04 | P4 | ADR-023 | TC-024 |
| FR-025 | Route URL to F-01 pipeline | F-04 | P4 | ADR-023, ADR-008 | TC-025 |
| FR-026 | Non-URL QR response without URL analysis | F-04 | P5, P6 | ADR-023 | TC-026 |
| FR-027 | Return decoded QR content | F-04 | P4, P8 | ADR-023 | TC-027 |
| FR-028 | Error for unreadable QR | F-04 | P6, P8 | ADR-023 | TC-028 |
| FR-029 | Accept profile signals | F-05 | P4 | ADR-011 | TC-029 |
| FR-030 | Identity-verification disclaimer | F-05 | P5 | ADR-011 | TC-030 |
| FR-031 | Insufficient signals response | F-05 | P5, P6 | ADR-011 | TC-031 |
| FR-032 | Non-empty signal explanation | F-05 | P4, P8 | ADR-011 | TC-032 |
| FR-033 | Fake profile risk model classification | F-05 | P4 | ADR-011 | TC-033 |
| FR-034 | Experimental label on F-06 entry | F-06 | P5 | ADR-010, ADR-029 | TC-034 |
| FR-035 | Accept media for deepfake analysis | F-06 | P4 | ADR-010 | TC-035 |
| FR-036 | Research/Experimental disclaimer | F-06 | P5 | ADR-010, ADR-029 | TC-036 |
| FR-037 | No-face-detected response | F-06 | P5, P8 | ADR-010 | TC-037 |
| FR-038 | Confidence indicator in F-06 response | F-06 | P5 | ADR-010 | TC-038 |
| FR-039 | File validation before F-06 processing | F-06 | P2, P6 | ADR-010 | TC-039 |
| FR-040 | Experimental label on F-07 entry | F-07 | P5 | ADR-011, ADR-029 | TC-040 |
| FR-041 | Accept account signals for F-07 | F-07 | P4 | ADR-011 | TC-041 |
| FR-042 | All three disclaimers in F-07 response | F-07 | P5 | ADR-011, ADR-024, ADR-029 | TC-042 |
| FR-043 | Insufficient signals response for F-07 | F-07 | P5, P6 | ADR-011 | TC-043 |
| FR-044 | Non-empty signal explanation for F-07 | F-07 | P4, P8 | ADR-011 | TC-044 |
| FR-045 | Accept phone number for F-08 | F-08 | P4 | ADR-018, ADR-032 | TC-045 |
| FR-046 | Phone number format validation | F-08 | P2, P6 | ADR-018 | TC-046 |
| FR-047 | Threat data risk verdict for F-08 | F-08 | P4 | ADR-032 | TC-047 |
| FR-048 | No risk verdict for emergency numbers | F-08 | P9 | ADR-018 | TC-048 |
| FR-049 | Data source + disclaimer in F-08 | F-08 | P5, P8 | ADR-018 | TC-049 |
| FR-050 | Safe/Low + absence-of-data note | F-08 | P5, P8 | ADR-032 | TC-050 |
| FR-051 | Accept password for F-09 | F-09 | P4 | — | TC-051 |
| FR-052 | Empty password validation | F-09 | P6 | — | TC-052 |
| FR-053 | Password entropy/length/diversity eval | F-09 | P4 | — | TC-053 |
| FR-054 | Actionable improvement recommendations | F-09 | P4, P8 | — | TC-054 |
| FR-055 | "Do not enter actual password" notice | F-09 | P8, P9 | — | TC-055 |
| FR-056 | Password never stored or logged | F-09 | P2, P3 | ADR-027 | TC-056 |
| FR-057 | AES-256-GCM file encryption | F-10 | P2 | ADR-021 | TC-057 |
| FR-058 | Argon2id key derivation | F-10 | P2, P10 | ADR-021, ADR-026 | TC-058 |
| FR-059 | Successful decryption with correct password | F-10 | P4 | ADR-021 | TC-059 |
| FR-060 | Error on wrong-password decryption | F-10 | P2 | ADR-021 | TC-060 |
| FR-061 | No plaintext file retained after encrypt | F-10 | P3 | ADR-027 | TC-061 |
| FR-062 | File type/size validation for F-10 | F-10 | P6 | ADR-021 | TC-062 |
| FR-063 | Password-loss warning display | F-10 | P8 | ADR-021 | TC-063 |
| FR-064 | Fresh nonce per encryption operation | F-10 | P2, P10 | ADR-021 | TC-064 |
| FR-065 | Accept query for F-11 | F-11 | P4 | ADR-013 | TC-065 |
| FR-066 | RAG retrieval before response | F-11 | P4, P5 | ADR-013, ADR-006 | TC-066 |
| FR-067 | AI disclaimer in F-11 response | F-11 | P5 | ADR-013 | TC-067 |
| FR-068 | Out-of-scope response for non-cybersec queries | F-11 | P6, P9 | ADR-013 | TC-068 |
| FR-069 | Decline legal/financial/medical advice | F-11 | P5, P10 | ADR-013 | TC-069 |
| FR-070 | Acknowledge knowledge gap — no fabrication | F-11 | P5 | ADR-013 | TC-070 |
| FR-071 | F-11 blocked until ADR-013 resolved | F-11 | — | ADR-013 | TC-071 |
| FR-072 | Compute Cyber Risk Score for user | F-12 | P4 | ADR-012, ADR-020 | TC-072 |
| FR-073 | Use Phase 1 controlled signal set only | F-12 | P5, P6 | ADR-012, ADR-020 | TC-073 |
| FR-074 | Score breakdown in response | F-12 | P4, P8 | ADR-012 | TC-074 |
| FR-075 | Score disclaimer in every response | F-12 | P5 | ADR-012 | TC-075 |
| FR-076 | Baseline score + prompt for new users | F-12 | P8 | ADR-012 | TC-076 |
| FR-077 | Score updates on new activity | F-12 | P4 | ADR-012, ADR-020 | TC-077 |
| FR-078 | Improvement action recommendations | F-12 | P4, P8 | ADR-012 | TC-078 |
| FR-079 | Basic score history indicator | F-12 | P4 | ADR-012 | TC-079 |
| FR-080 | Accept location input for F-13 | F-13 | P4 | ADR-007 | TC-080 |
| FR-081 | Explicit geolocation consent prompt | F-13 | P3, P9 | ADR-027 | TC-081 |
| FR-082 | No persistent location without consent | F-13 | P3 | ADR-027 | TC-082 |
| FR-083 | No-alerts message for empty location | F-13 | P8 | ADR-007 | TC-083 |
| FR-084 | Data freshness + disclaimer in F-13 | F-13 | P5, P8 | ADR-007 | TC-084 |
| FR-085 | Alert coverage for major metros | F-13 | P4 | ADR-032 | TC-085 |
| FR-086 | Daily Cyber Safety Tip | F-14 | P4, P8 | — | TC-086 |
| FR-087 | Quiz with min 10 questions, 3 categories | F-14 | P4 | — | TC-087 |
| FR-088 | Correct answer + explanation after quiz | F-14 | P4, P8 | — | TC-088 |
| FR-089 | Awareness articles for 5 threat types | F-14 | P4, P8 | — | TC-089 |
| FR-090 | Content accuracy review before publish | F-14 | P5, P10 | — | TC-090 |
| FR-091 | Preventive guidance content | F-14 | P4, P8 | — | TC-091 |
| FR-092 | User registration (email + password) | §5 Auth | P2 | ADR-019 | TC-092 |
| FR-093 | Email verification required | §5 Auth | P2 | ADR-019 | TC-093 |
| FR-094 | No email enumeration on duplicate | §5 Auth | P2 | ADR-019 | TC-094 |
| FR-095 | Consent checkbox required | §7 Privacy | P3 | ADR-027 | TC-095 |
| FR-096 | JWT tokens on successful login | §5 Auth | P2 | ADR-019, ADR-026 | TC-096 |
| FR-097 | Generic login error (no field enumeration) | §5 Auth | P2 | ADR-019 | TC-097 |
| FR-098 | TOTP 2FA enrollment | §5 Auth | P2 | ADR-019 | TC-098 |
| FR-099 | TOTP required at login if enrolled | §5 Auth | P2 | ADR-019 | TC-099 |
| FR-100 | Backup codes displayed once | §5 Auth | P2, P8 | ADR-019 | TC-100 |
| FR-101 | Password reset via time-limited email | §5 Auth | P2 | ADR-019, ADR-026 | TC-101 |
| FR-102 | Sessions invalidated after password reset | §5 Auth | P2 | ADR-019 | TC-102 |
| FR-103 | Account deletion with password confirmation | §5 Auth | P3 | ADR-027 | TC-103 |
| FR-104 | PII deleted/anonymised after deletion | §5 Auth, §7 Privacy | P3 | ADR-027 | TC-104 |
| FR-105 | Rate limiting on login attempts | §5 Auth | P2 | ADR-026 | TC-105 |
| FR-106 | 5-level risk model across all detection | §4 AI/ML | P4 | ADR-001 | TC-106 |
| FR-107 | Non-empty explanation with every verdict | §4 AI/ML | P4, P8 | ADR-001 | TC-107 |
| FR-108 | Appropriate disclaimers in all AI/ML output | §4 AI/ML | P5 | ADR-015 | TC-108 |
| FR-109 | Experimental label on F-06, F-07 entry | §4 AI/ML | P5 | ADR-029 | TC-109 |
| FR-110 | No prohibited claims in UI copy | §4 AI/ML | P5 | ADR-002 | TC-110 |
| FR-111 | JWT required on all protected endpoints | §5 Auth | P2 | ADR-019, ADR-026 | TC-111 |
| FR-112 | RBAC enforcement | §5 Auth | P2, P10 | ADR-019 | TC-112 |

**Note:** Constitution Principles referenced as P1–P10 (Principle 1 = Quality over feature quantity through Principle 10 = All security decisions must be defensible, as defined in CSHAKTI-CONST-001 §2).

---

*End of CyberShakti Software Requirements Specification — CSHAKTI-SRS-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
