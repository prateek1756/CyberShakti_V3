# CyberShakti — Product Vision and Scope

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-PVS-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-15 |
| **Traces To** | CSHAKTI-CONST-001 (Project Constitution) |
| **Governed By** | CSHAKTI-CONST-001 — all content in this document must be consistent with the constitution. Conflicts must be recorded in `docs/00-decisions.md`. |

---

## Table of Contents

1. [Problem Statement](#1-problem-statement)
2. [Product Vision](#2-product-vision)
3. [Product Mission](#3-product-mission)
4. [Core Philosophy](#4-core-philosophy)
5. [Target Users](#5-target-users)
6. [Product Scope — In](#6-product-scope--in)
7. [Product Scope — Out](#7-product-scope--out)
8. [Regulatory Context](#8-regulatory-context)
9. [Success Criteria](#9-success-criteria)
10. [Assumptions and Constraints](#10-assumptions-and-constraints)

---

## 1. Problem Statement

### 1.1 India's Digital Threat Landscape

India has one of the world's largest and fastest-growing populations of internet users, with a significant share accessing digital services primarily through mobile devices. This growth has created an enormous attack surface for cybercriminals who specifically target Indian consumers.

The following threat categories represent the core problems CyberShakti is designed to address. Statistics cited below are directional indicators from publicly reported sources; readers should verify current figures from authoritative sources such as CERT-In Annual Reports, NCRB Crime in India reports, and RBI Annual Reports, as these figures change year to year.

**Note on statistics:** Specific numerical claims about cybercrime volumes, financial losses, and incident counts are not asserted in this document. The threat categories below are grounded in publicly reported patterns from CERT-In, RBI, and NCRB. Any quantitative data used in downstream marketing, product communications, or investor materials must be sourced from and attributed to authoritative published sources.

### 1.2 Primary Threat Categories

**UPI and Digital Payment Fraud**

India's Unified Payments Interface (UPI) has enabled hundreds of millions of Indians to transact digitally. This scale has attracted fraudsters who exploit UPI's accessibility. Common attack patterns include fake payment requests, QR code-based payment scams, impersonation of merchants or government officials, and "collect request" fraud where victims are tricked into authorising payments under the pretence of receiving money.

**WhatsApp and Messaging Platform Scams**

WhatsApp is the primary communication platform for a large proportion of Indian internet users. Fraudsters exploit this by circulating phishing links, impersonating family members in distress, running fake job offers, conducting lottery and prize scams, and distributing fraudulent investment scheme promotions through WhatsApp messages and groups.

**OTP Theft and SIM Swap Fraud**

One-time passwords (OTPs) are the primary second factor for digital banking and UPI transactions in India. Fraudsters obtain OTPs through social engineering (convincing victims to share OTPs), SIM swap attacks (fraudulently porting a victim's mobile number to a new SIM), and vishing (voice phishing calls impersonating bank officials or telecom operators).

**Phishing Links and Fake Websites**

Fraudsters create convincing replicas of banking portals, government service websites, and popular e-commerce platforms. These phishing sites harvest login credentials, personal information, and banking details. Links are distributed via SMS (smishing), email, WhatsApp, and social media.

**Deepfake-Based Fraud**

AI-generated synthetic media — deepfake video and audio — is increasingly used in fraud. Known patterns include video calls using deepfaked faces of known individuals to request money transfers, and voice clones impersonating relatives or officials in audio calls. This threat is emerging and growing.

**Fake Profiles and Impersonation**

Fraudsters create fake social media profiles impersonating real individuals, companies, government agencies, or celebrities to conduct romance scams, investment fraud, and credential theft. Victims who trust the apparent identity of the profile may disclose personal information or transfer funds.

**Mule Account Networks**

Money mule accounts are used to layer and move the proceeds of cybercrime, making it harder to trace and recover stolen funds. Individuals are sometimes recruited — often unknowingly — to receive and forward fraudulent transfers, making them unwitting participants in financial crime.

**Scam Calls**

India has a high volume of scam calls impersonating bank officials, insurance companies, government agencies (e.g., fake CBI or IT department officials), and telecom operators. These calls are designed to extract OTPs, personal identification information, and banking credentials through social engineering.

**QR Code Fraud**

QR codes are now ubiquitous in Indian commerce. Fraudsters substitute legitimate QR codes at merchant locations, create fake QR codes for non-existent payment destinations, and circulate QR codes in messages that lead to phishing sites.

**Job and Investment Scams**

Fraudulent job offers promising high salaries for minimal work, and investment schemes promising guaranteed high returns (particularly cryptocurrency and share market scams), are prevalent across messaging platforms and social media. These scams exploit economic aspirations and financial pressures.

### 1.3 Why Existing Solutions Are Insufficient

Most individual Indian consumers do not have access to:

- A single platform that addresses the full breadth of consumer cyberthreats in the Indian context
- Tools that explain threats in plain, accessible language without requiring technical expertise
- Integrated risk assessment that reflects their personal security posture rather than generic advice
- Cybersecurity education that is relevant to the specific threats they face in their daily digital lives

General-purpose antivirus tools and enterprise security products exist but are not designed for the non-technical individual consumer facing India's specific threat landscape.

---

## 2. Product Vision

> CyberShakti is the trusted personal cybersecurity companion for every Indian internet user — making digital safety accessible, understandable, and actionable regardless of technical background.

---

## 3. Product Mission

CyberShakti's mission is to:

- **Detect** the cyber threats most likely to harm Indian consumers — phishing links, scam messages, fake profiles, fraudulent QR codes, suspicious calls, and deepfake media
- **Protect** users' sensitive data and accounts through encryption, password security, and risk awareness
- **Assist** users in understanding their security posture and responding appropriately when threats are identified
- **Educate** users through accessible, India-relevant cybersecurity awareness content so they become harder targets over time

CyberShakti does not guarantee safety. It reduces risk, increases awareness, and helps users make better-informed decisions about their digital interactions.

---

## 4. Core Philosophy

CyberShakti is built on a five-stage philosophy that reflects the complete lifecycle of a user's interaction with a cyber threat:

```
Detect → Analyze → Protect → Assist → Learn
```

### Detect
The system actively finds potential threats — whether a suspicious link, a scam message, a dubious QR code, or a potentially fake profile — and surfaces them for the user's attention. Detection is the entry point for every protective action.

### Analyze
Detection alone is insufficient. CyberShakti analyzes what was detected to classify the nature and severity of the threat. Analysis produces a risk level (Safe through Critical), a plain-language explanation of why the verdict was reached, and enough context for the user to make an informed decision. Analysis distinguishes between noise and genuine risk.

### Protect
Where CyberShakti can actively protect the user — through file encryption, password security assessment, or risk-aware design — it does so. Protection is not passive awareness; it is a set of tools the user can deploy to reduce their actual exposure.

### Assist
After detection and analysis, users need guidance. The AI Cybersecurity Assistant and Cyber Risk Score help users understand their overall security posture, answer specific questions about threats, and determine what to do next. Assistance bridges the gap between knowing there is a risk and knowing how to respond.

### Learn
Long-term protection comes from changing behaviour. The Cyber Safety Hub and its awareness content, daily tips, and quizzes help users understand the tactics fraudsters use and develop safer digital habits. Learning converts one-time awareness into lasting resilience.

---

## 5. Target Users

### 5.1 Primary Target User

**Individual Indian Consumer**

CyberShakti Phase 1 is designed for the individual Indian internet user who is not a cybersecurity professional and does not have a technical background in information security.

**Characteristics:**

| Dimension | Description |
|---|---|
| **Technical literacy** | Basic to moderate. Comfortable with smartphone and WhatsApp. May not understand terms like "phishing", "malware", or "2FA" without explanation. Security explanations must be in plain language. |
| **Primary device** | Mobile device (smartphone) is likely the primary internet access device for a significant proportion of this audience. The responsive web application must deliver a good experience on mobile browsers. Device assumptions to be validated in the UI/UX design phase. |
| **Threat exposure** | High. Regularly receives suspicious WhatsApp messages, scam calls, and phishing links. May have been previously affected by or knows someone affected by digital fraud. |
| **Language** | English-medium product in Phase 1. A significant portion of the target audience operates primarily in Hindi or regional languages. Localisation scope is a future consideration — not in Phase 1 scope. |
| **Age range** | Broad — from young adults entering the workforce and beginning their digital financial lives, to middle-aged users managing family finances digitally, to senior citizens who are a high-target demographic for fraud. |
| **Digital financial activity** | Likely uses UPI (GPay, PhonePe, Paytm) for payments. May use mobile banking. Possibly active on investment platforms. High exposure to UPI-related fraud patterns. |
| **Existing security behaviour** | Likely inconsistent. May reuse passwords. Unlikely to have enabled 2FA on most accounts. May not recognise phishing indicators. Relies on instinct rather than tools for threat assessment. |

### 5.2 Secondary User Segments

The following are sub-segments of the primary user that represent concentrated risk profiles. They are not separate product personas but are useful for grounding feature design decisions:

**Students and young adults (18–25):** High smartphone usage, active on social media, increasingly engaged with digital payments and investment platforms. Higher exposure to job scams, investment scams, and social media impersonation.

**Senior citizens (60+):** Disproportionately targeted by scam callers, fake government official impersonators, and family-emergency social engineering attacks. Lower digital literacy. Higher need for plain-language explanations and proactive alerts.

**Family members managing others' digital safety:** A user who uses CyberShakti to check suspicious links or messages on behalf of a less digitally literate family member (parent, grandparent). Represents a common real-world usage pattern.

### 5.3 Out-of-Scope Users

The following user types are not the target for Phase 1:

- Enterprise security teams or organisational IT administrators
- Cybersecurity professionals seeking advanced threat analysis tools
- Small or medium business owners seeking business-specific security products
- Developers or researchers (except as incidental users)

---

## 6. Product Scope — In

CyberShakti Phase 1 contains exactly **four pillars** and **fourteen features**. This scope is frozen per CSHAKTI-CONST-001 §5 and ADR-002.

Each feature is listed with its locked Phase 1 classification tier. Tier definitions are in CSHAKTI-CONST-001 §4. Tiers may not be reassigned without a recorded and approved change decision (ADR-029).

---

### Pillar 1 — Detect & Analyze

*Purpose: Find, analyze, classify, and explain potential cyber threats targeting Indian consumers.*

| ID | Feature | Tier | Phase 1 Scope |
|---|---|---|---|
| F-01 | Phishing Link Scanning | Core MVP | User submits a URL; the system analyzes it using URL feature engineering, rule-based analysis, and threat intelligence; returns a risk verdict (Safe through Critical) with a plain-language explanation. |
| F-02 | Message & Email Scam Detection | Core MVP | User pastes or submits the text of a suspicious message or email; the system classifies it as scam or legitimate using NLP; returns a risk verdict with explanation. |
| F-03 | Screenshot Scam Scanner | Core MVP | User uploads a screenshot of a suspicious message, notification, or page; the system extracts text via OCR (PaddleOCR) and passes it through the scam NLP classifier; returns a risk verdict with explanation. |
| F-04 | QR Code Scam Scanner | Core MVP | User uploads or captures a QR code image; the system decodes the QR code, extracts the embedded URL, and routes it through the F-01 phishing URL analysis pipeline; returns a risk verdict with explanation. |
| F-05 | Fake Profile Verification | Advanced MVP | User submits signals about a social media profile (profile URL, observable characteristics); the system returns a risk assessment of whether the profile shows indicators of being fake or suspicious. Does not perform identity verification. |
| F-06 | Deepfake Detection | Research/Experimental | User uploads an image or short video; the system applies a CNN-based classifier (EfficientNet or Xception — model selection TBD by empirical evaluation) to assess whether the media shows indicators of synthetic generation. **Research/Experimental: outputs are not production-grade and must communicate uncertainty to the user. This feature is part of Phase 1 research and training scope, not a guaranteed production capability.** |
| F-07 | Mule Account Detection | Research/Experimental | User or system submits account/transaction signals; the system applies graph-feature-augmented classification (XGBoost + NetworkX) to assess whether an account shows indicators associated with mule account patterns. **Research/Experimental: outputs are not production-grade. Dataset domain mismatch (research datasets represent cryptocurrency networks, not bank accounts) must be communicated to users. This feature is part of Phase 1 research and training scope.** |

---

### Pillar 2 — Protect

*Purpose: Protect users, accounts, communications, and sensitive data from identified threats.*

| ID | Feature | Tier | Phase 1 Scope |
|---|---|---|---|
| F-08 | Scam Call Blocking | Advanced MVP | User enters or pastes a phone number; the system looks up the number against available threat/reputation data and returns a risk assessment indicating whether the number is associated with known scam activity. **Phase 1 scope: in-app manual lookup only. Android OS-level automatic call blocking is deferred.** |
| F-09 | Password Security Checker | Core MVP | User enters a password into the checker (not their actual account password — the checker is for assessment purposes); the system evaluates entropy, length, character diversity, common-password patterns, and known-breach indicators; returns a security verdict with specific plain-language improvement guidance. No password is transmitted to a server or stored. |
| F-10 | Secure File Encryption | Core MVP | User uploads a file; the system encrypts it using AES-256-GCM with a user-supplied password (key derived via Argon2id); provides the encrypted file for download. The user can later decrypt using the same password. Encryption and decryption occur without permanent server-side storage of the original plaintext file. |

---

### Pillar 3 — Assist & Respond

*Purpose: Help users understand threats, assess personal cybersecurity posture, and respond appropriately.*

| ID | Feature | Tier | Phase 1 Scope |
|---|---|---|---|
| F-11 | AI Cybersecurity Assistant | Core MVP | Conversational AI assistant powered by an API-based LLM with RAG over a curated CyberShakti knowledge base. Helps users understand threats, explains CyberShakti feature results, answers cybersecurity questions, and provides guidance grounded in the knowledge base. LLM provider TBD (ADR-013 Open). All outputs include AI disclaimer. |
| F-12 | Cyber Risk Score | Core MVP | Produces a personalised cybersecurity risk score for the user based on a controlled set of in-app security signals (scan history, threat detections, password security results) and selected user-reported security-posture signals. Score is produced by an explainable weighted engine. Every score is accompanied by a breakdown of contributing factors in plain language. ML-based risk prediction is not used in Phase 1. |
| F-13 | Location-Based Scam Alerts | Advanced MVP | Surfaces scam and fraud alerts relevant to the user's reported or detected location (city/region level), drawing on a threat database with location-tagged incident data. Uses PostGIS for geospatial queries. No real-time precise location tracking. |

---

### Pillar 4 — Learn & Prevent

*Purpose: Improve cybersecurity awareness and safer digital behaviour through education and preventive guidance.*

| ID | Feature | Tier | Phase 1 Scope |
|---|---|---|---|
| F-14 | Cyber Safety Hub | Core MVP | Curated hub of India-relevant cybersecurity awareness content. Includes: Daily Cyber Safety Tips, Cybersecurity Quiz (sub-feature of F-14), awareness articles covering common threat patterns, preventive guidance, and interactive learning content. |

---

### 6.1 Cross-Cutting Platform Capabilities

The following capabilities underpin all fourteen features and are part of Phase 1 scope, though they are not standalone features:

| Capability | Description |
|---|---|
| **User Authentication** | Email + password registration and login. Optional TOTP-based 2FA. Password reset. Account deletion. (ADR-019) |
| **Cyber Risk Score Engine** | The weighted risk engine that powers F-12, drawing signals from across all features. |
| **Threat Intelligence Integration** | Access to threat and reputation data sources used by F-01, F-04, F-08, and F-13. Specific sources TBD (ADR-032). |
| **Risk Severity Model** | Consistent 5-level risk output (Safe / Low Risk / Moderate Risk / High Risk / Critical) used across all detection features. |
| **Explanation Engine** | Every risk verdict produced by any feature is accompanied by a plain-language explanation. |

---

## 7. Product Scope — Out

The following capabilities are **explicitly not part of CyberShakti Phase 1**. They are documented here to prevent scope creep during development. Any proposal to include these in Phase 1 requires a recorded and approved change decision following the process in CSHAKTI-CONST-001 §14.

### 7.1 Platform and Application Scope

| Out-of-Scope Item | Notes |
|---|---|
| Native Android application | Deferred to a future phase. Phase 1 is a responsive web application only (ADR-025). |
| Native iOS application | Not in Phase 1 scope. |
| Android OS-level automatic call blocking | Requires a native Android app or SDK. Deferred (ADR-018, ADR-025). |
| Real-time call interception or monitoring | Not in Phase 1 scope. |
| Browser extension | Not in Phase 1 scope. |
| Email client integration | Not in Phase 1 scope. |
| Progressive Web App (PWA) with offline-first design | Not explicitly scoped for Phase 1; to be evaluated during UI/UX design if relevant. |

### 7.2 Feature Scope

| Out-of-Scope Item | Notes |
|---|---|
| "I've Been Scammed" standalone incident response workflow | Deferred. Assistance for scam victims may be addressed within F-11 (AI Assistant) or F-14 (Cyber Safety Hub) in Phase 1, but is not a separate top-level feature. |
| Social login (Google, GitHub, or other OAuth providers) | Deferred (ADR-019). |
| ML-based Cyber Risk Score prediction | Not in Phase 1. Phase 1 uses an explainable weighted engine (ADR-012, ADR-020). |
| Advanced Graph Neural Networks (GNN) for mule detection in production | GNNs via PyTorch Geometric are the advanced future path for F-07; not Phase 1 production (ADR-011). |
| Real-time SMS or call screening | Requires OS-level integration; not available in a web application. |
| Automatic threat blocking or content removal | CyberShakti assesses and informs; it does not automatically block content on external platforms. |
| Dark web monitoring | Not in Phase 1 scope. |
| Network traffic monitoring or firewall | Not a consumer web application capability. |
| Antivirus or anti-malware engine | Not in Phase 1 scope. |
| Identity verification | CyberShakti assesses the risk that a profile may be fake (F-05); it does not verify identity (CSHAKTI-CONST-001 §3.2). |

### 7.3 Organisational and Enterprise Scope

| Out-of-Scope Item | Notes |
|---|---|
| Enterprise security management | Phase 1 targets individual consumers only (ADR-017). |
| Multi-user organisational accounts or team dashboards | Not in Phase 1 scope. |
| SIEM integration | Not in Phase 1 scope. |
| Compliance reporting for organisations | Not in Phase 1 scope. |

### 7.4 Language and Localisation

| Out-of-Scope Item | Notes |
|---|---|
| Hindi-language UI | Phase 1 is English-medium. Localisation is a future consideration. |
| Regional language UI (Tamil, Telugu, Bengali, Marathi, etc.) | Not in Phase 1 scope. |
| Multilingual scam text detection (beyond English) | F-02 and F-03 NLP models are primarily English-capable in Phase 1. Multilingual capability is a known limitation to be documented. |

---

## 8. Regulatory Context

### 8.1 Relevant Regulatory Frameworks

The following regulatory frameworks are relevant to CyberShakti's operation. They are documented here as awareness areas — not as assertions of specific legal obligations. All compliance obligations require verification with qualified legal counsel.

**India Information Technology Act 2000 (and amendments)**
Governs electronic records, digital signatures, cybercrime offences, and data protection obligations for intermediaries operating in India. Relevant to CyberShakti's role as an intermediary handling user data and cybersecurity-related information.

**Digital Personal Data Protection Act 2023 (DPDP Act)**
India's personal data protection legislation. Establishes principles of consent, data minimisation, purpose limitation, and data principal rights (access, correction, erasure, grievance redressal). Relevant to every feature that collects, processes, or stores personal data about users.

**RBI and NPCI Guidelines**
The Reserve Bank of India and National Payments Corporation of India publish guidance relevant to digital payment fraud, UPI fraud patterns, and consumer protection in digital transactions. This context informs CyberShakti's threat taxonomy and the relevance of features addressing UPI fraud, scam calls, and payment QR codes.

**Data Residency Considerations**
Where Indian users' personal data is stored and processed may have regulatory implications, particularly under the DPDP Act. The backend deployment target selection (ADR-004, currently TBD between Render/Railway/AWS) and object storage provider selection (ADR-031, Open) should consider data residency requirements. These requirements must be verified with legal counsel before deployment.

### 8.2 Limitations of This Section

- This section is **informational only**.
- Documenting these frameworks in this product definition document does **not** constitute legal compliance with any of them.
- CyberShakti must not represent itself as legally compliant with any of these frameworks in user-facing materials, marketing, or investor communications without proper legal verification.
- Specific legal obligations, mandatory data residency requirements, and regulatory interpretations must not be asserted without authoritative, verified sources.
- Legal review of compliance obligations must be completed before any public launch.

---

## 9. Success Criteria

Success criteria for Phase 1 are expressed as measurable qualitative outcomes. Numerical targets are marked **TBD** and will be established after empirical evaluation, usability testing, and production monitoring. No numerical targets are invented in this document.

### 9.1 Detection and Analysis (Pillar 1)

| Criterion | How It Will Be Measured |
|---|---|
| Users can successfully submit a suspicious link, message, screenshot, or QR code and receive a risk verdict with a plain-language explanation | Usability testing; acceptance test pass rate |
| The phishing URL classifier (F-01) demonstrates measurably better performance than a random baseline on a held-out representative test set | Model validation on holdout dataset — metrics TBD after empirical evaluation |
| The scam text classifier (F-02) demonstrates measurably better performance than a TF-IDF + Logistic Regression baseline | Comparative model evaluation — metrics TBD |
| F-06 (Deepfake Detection) and F-07 (Mule Account Detection) produce outputs that correctly communicate their Research/Experimental status and uncertainty | Acceptance test: disclaimer present in output; user testing confirms understanding of experimental status |
| False positive rate for Core MVP detection features is at an acceptable level for consumer use | TBD — to be set after model validation and usability testing; "acceptable" defined as a rate that does not erode user trust through excessive false alarms |

### 9.2 Protection (Pillar 2)

| Criterion | How It Will Be Measured |
|---|---|
| F-09 Password Security Checker correctly identifies known-weak passwords and provides actionable improvement guidance | Acceptance test against a curated set of weak and strong passwords |
| F-10 Secure File Encryption successfully encrypts and decrypts files using AES-256-GCM without data loss or corruption | Encryption/decryption round-trip tests across supported file types and sizes |
| No plaintext file content or user password is stored server-side during F-10 operations | Security audit of encryption flow; code review |
| F-08 Scam Call Blocking returns risk assessments for known-scam numbers sourced from threat intelligence | Acceptance test against known-scam numbers from selected threat intelligence source (ADR-032 — source TBD) |

### 9.3 Assist & Respond (Pillar 3)

| Criterion | How It Will Be Measured |
|---|---|
| F-11 AI Cybersecurity Assistant returns grounded, non-fabricated responses to common Indian cybersecurity questions | RAG retrieval accuracy testing; hallucination audit against knowledge base |
| F-12 Cyber Risk Score changes appropriately in response to changes in user security behaviour (e.g., completing a scan, updating password security) | Automated integration tests; QA review of score delta behaviour |
| Every F-12 score is accompanied by a plain-language explanation of contributing factors | Acceptance test: explanation field always populated; no unexplained score |
| F-13 Location-Based Scam Alerts surfaces relevant alerts for at least the major Indian metropolitan areas and key fraud-affected regions at launch | Data coverage verification before launch |

### 9.4 Learn & Prevent (Pillar 4)

| Criterion | How It Will Be Measured |
|---|---|
| F-14 Cyber Safety Hub contains a minimum viable set of India-relevant cybersecurity content at launch | Content audit against defined minimum content checklist |
| Daily Cyber Safety Tips are sourced from verified, accurate content — no fabricated threat claims | Content editorial review |
| Cybersecurity Quiz questions are accurate and relevant to Indian consumer threats | Content accuracy review |

### 9.5 Platform Quality

| Criterion | How It Will Be Measured |
|---|---|
| The application is usable on current versions of Chrome, Firefox, Safari, and Edge on both desktop and mobile | Cross-browser testing |
| The application meets WCAG 2.1 Level AA accessibility targets | Automated accessibility testing; manual review — note: full WCAG compliance requires expert accessibility audit |
| All Core MVP features pass their acceptance criteria before Phase 1 release | Acceptance test suite pass rate: 100% for Must Have requirements |
| Authentication flows (registration, login, optional 2FA, password reset, account deletion) work correctly across all supported browsers | End-to-end test pass rate |
| User satisfaction with explanation quality | TBD — to be measured via usability testing before launch |

---

## 10. Assumptions and Constraints

### 10.1 Assumptions

| # | Assumption | Impact if Invalid |
|---|---|---|
| A-01 | Indian consumers will access CyberShakti primarily through mobile browsers, making mobile-first UX the correct design direction. | If desktop is primary, some UX design decisions may need revision. To be validated in UI/UX phase. |
| A-02 | The primary language of interaction for Phase 1 users is English. | If a significant portion of the target audience requires Hindi or regional language support for usability, English-only Phase 1 would limit reach. Localisation deferred to future phase. |
| A-03 | Publicly available phishing URL datasets (PhishTank, URLhaus, and others) will be accessible and licensable for use in training F-01 models. | If key datasets are unavailable or unlicensable, alternative data sourcing strategies must be identified before F-01 model training begins. |
| A-04 | Publicly available scam/spam text datasets will be sufficient in quality and volume for training F-02 baseline and DistilBERT models. | If datasets are insufficient or not representative of Indian scam patterns, additional data collection or augmentation strategies will be needed. |
| A-05 | GPU compute will be available via Kaggle and Google Colab for model training during the research and development phase. | If GPU compute becomes unavailable or insufficient, training timelines and model complexity may need adjustment. |
| A-06 | A reputable threat intelligence source with adequate India-specific coverage and acceptable API terms will be identified for F-01, F-04, F-08, and F-13 (ADR-032). | If no suitable source is identified, detection quality for these features will be limited to model-based classification without real-time threat intelligence enrichment. |
| A-07 | An LLM API provider will be selected (ADR-013) that meets the privacy, cost, and capability requirements for F-11 before F-11 implementation begins. | F-11 implementation is blocked until ADR-013 is resolved. |
| A-08 | The DPDP Act 2023 and IT Act 2000 regulatory obligations, once verified with legal counsel, will be achievable within the Phase 1 architecture and technology choices. | If legal review reveals obligations incompatible with the current design, architecture changes may be required. |
| A-09 | Deepfake detection (F-06) and mule account detection (F-07) training datasets (FaceForensics++, Celeb-DF, DFDC, Elliptic/Elliptic2) will be accessible and their licensing terms will permit their use for the intended research purpose. | If key datasets are inaccessible or unlicensable, alternative data sourcing for these Research/Experimental features must be identified. |

### 10.2 Constraints

| # | Constraint | Source |
|---|---|---|
| C-01 | Phase 1 is a responsive web application only. No native Android or iOS apps. | ADR-025, CSHAKTI-CONST-001 §11 |
| C-02 | The technology stack is frozen as defined in CSHAKTI-CONST-001 §6. No additions, replacements, or removals without a recorded ADR. | CSHAKTI-CONST-001 §6, ADR-002 |
| C-03 | Exactly 14 features across 4 pillars. Feature additions require a recorded and approved change decision. | CSHAKTI-CONST-001 §5, ADR-002 |
| C-04 | All AI/ML model performance claims must be based on empirical validation, not assumed or invented. | CSHAKTI-CONST-001 §3.4, §17 |
| C-05 | No specific regulatory compliance claims may be made without authoritative legal verification. | CSHAKTI-CONST-001 §10, ADR-030 |
| C-06 | Security configuration parameters (Argon2id, JWT, rate limits) must not be permanently set without security benchmarking. | CSHAKTI-CONST-001 §8.4, §8.5, ADR-026 |
| C-07 | The LLM provider for F-11 is unresolved (ADR-013 Open). F-11 implementation cannot begin until this is resolved. | ADR-013 |
| C-08 | Threat intelligence sources for F-01, F-04, F-08, F-13 are unresolved (ADR-032 Open). These features cannot be fully implemented until sources are selected. | ADR-032 |
| C-09 | The object storage provider is unresolved (ADR-031 Open). This affects F-10, F-03, F-04, and MLflow artefact storage. | ADR-031 |
| C-10 | F-06 and F-07 are Research/Experimental. They must not be released as production-grade capabilities without empirical validation. | CSHAKTI-CONST-001 §4, ADR-010, ADR-011 |
| C-11 | Password storage in plaintext is prohibited under all circumstances. | CSHAKTI-CONST-001 §8.2 |
| C-12 | Model training is conducted on local machines, Kaggle GPU, and Google Colab GPU. No dedicated GPU cloud infrastructure is provisioned for Phase 1. | CSHAKTI-CONST-001 §6.16 |

---

*End of CyberShakti Product Vision and Scope — CSHAKTI-PVS-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
