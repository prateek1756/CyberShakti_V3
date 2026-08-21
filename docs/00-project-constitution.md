# CyberShakti — Project Constitution

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-CONST-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-15 |
| **Authority** | Apex document. All downstream documents must be consistent with this constitution. |

---

## Table of Contents

1. [Purpose and Authority](#1-purpose-and-authority)
2. [Product Principles](#2-product-principles)
3. [AI/ML Principles](#3-aiml-principles)
4. [Feature Classification System](#4-feature-classification-system)
5. [Feature Freeze Declaration](#5-feature-freeze-declaration)
6. [Technology Freeze Declaration](#6-technology-freeze-declaration)
7. [Architecture Principles](#7-architecture-principles)
8. [Security Principles](#8-security-principles)
9. [Privacy Principles](#9-privacy-principles)
10. [Regulatory Acknowledgement](#10-regulatory-acknowledgement)
11. [Device Strategy](#11-device-strategy)
12. [Risk Severity Model](#12-risk-severity-model)
13. [Traceability Principle](#13-traceability-principle)
14. [Change Control Rules](#14-change-control-rules)
15. [Development Agent Rules](#15-development-agent-rules)
16. [Documentation Rules](#16-documentation-rules)
17. [Success Metrics Principle](#17-success-metrics-principle)

---

## 1. Purpose and Authority

### 1.1 Position in the Documentation Hierarchy

This document is the **apex of the CyberShakti documentation hierarchy**. It governs the entire project. Every downstream document — Product Vision & Scope, PRD, TRD, SRS, System Architecture, Database Design, API Specification, AI/ML Pipeline Specifications, UI/UX Specification, and all Implementation plans — must be consistent with the principles, decisions, and constraints defined here.

### 1.2 What This Document Governs

This constitution governs:

- Product principles and philosophy
- AI/ML principles and prohibited claims
- Feature freeze — the locked set of 14 features across 4 pillars
- Feature classification tiers
- Technology freeze — the locked technology stack
- Architecture principles
- Security principles
- Privacy principles
- Device strategy
- Risk severity model
- Traceability requirements
- Change control process
- Development agent rules
- Documentation rules
- Success metrics principle
- Regulatory acknowledgements

### 1.3 Authority Rules

- No downstream document may **silently contradict** any principle, decision, or constraint defined in this constitution.
- When a conflict is discovered between this document and any downstream document, the conflict must be **recorded as an unresolved decision** in `docs/00-decisions.md`.
- Conflicts must **not** be silently resolved by editing either document without following the change control process defined in Section 14.
- This document itself may only be amended through the change control process defined in Section 14.

---

## 2. Product Principles

CyberShakti is governed by the following ten product principles. All product, design, and engineering decisions must be evaluated against these principles.

### Principle 1 — Quality Over Feature Quantity

A smaller set of well-implemented, reliable, and explainable features delivers more user value than a large set of fragile or incomplete ones. Phase 1 scope is intentionally bounded. Scope expansion requires a formal change decision.

### Principle 2 — Security by Design

Security is a first-class architectural concern, built into the system from the ground up. It is not a post-implementation addition. Every feature must be designed with its threat model in mind before implementation begins.

### Principle 3 — Privacy by Design

Data minimization, purpose limitation, and user consent are built into every feature from the design stage onwards. The system must never collect, store, or process personal data beyond what is necessary for the stated purpose of each feature.

### Principle 4 — Explainability for Security Decisions

Every risk assessment, threat verdict, and security recommendation produced by CyberShakti must be explainable in plain language that is accessible to non-technical Indian consumers. Users must be able to understand not just what the result is, but why it was produced and what they should do in response. Unexplained security verdicts are not acceptable.

### Principle 5 — No Unsupported AI Claims

AI/ML outputs must be presented with appropriate confidence communication. The system must never claim detection capabilities, accuracy levels, or protection guarantees that it cannot reliably demonstrate through empirical evidence. All AI/ML limitations must be documented and, where user-facing, disclosed.

### Principle 6 — No Unnecessary Complexity

Architecture, technology choices, and implementation must be as simple as the requirements allow. Every added dependency, service, or abstraction layer must be justified by a concrete requirement. Complexity must earn its place.

### Principle 7 — Modular Architecture

The system must be designed as independently maintainable modules with clear boundaries. No feature should create unmanageable coupling with unrelated features or system components. Module boundaries must be respected throughout implementation.

### Principle 8 — Human-Readable Security Explanations

Security outputs must be understandable by non-technical Indian consumers. Technical jargon must be translated into actionable guidance. Risk verdicts must be accompanied by plain-language explanations and recommended next steps where appropriate.

### Principle 9 — User Safety Takes Priority Over Engagement

Product decisions that trade user security, privacy, or safety for engagement metrics are not acceptable. Where a conflict exists between maximizing engagement and protecting the user, user protection takes precedence.

### Principle 10 — All Security Decisions Must Be Defensible

Every security design choice must be explainable and justifiable to a technically informed reviewer. Security-by-obscurity is not an acceptable security strategy. All security decisions must be documented and traceable to a known security principle or threat model finding.

---

## 3. AI/ML Principles

### 3.1 Choosing the Right Approach

AI and ML must be applied where they provide genuine, demonstrable value. The choice of approach must be driven by the problem, not by the appeal of the technology.

| Approach | When to Use |
|---|---|
| **Deterministic security engineering** | When the problem can be solved reliably with rules, heuristics, or established algorithms. Examples: password entropy calculation, AES-256-GCM encryption, Phase 1 Cyber Risk Score weighted engine. |
| **Classical ML (XGBoost, LightGBM, Logistic Regression)** | When classification or prediction provides genuine value, training data is available, and the problem does not require understanding of unstructured text or images. Examples: phishing URL classification, fake profile risk assessment. |
| **Deep Learning / NLP (DistilBERT, EfficientNet, Xception)** | When the problem requires understanding of text semantics or image content and classical ML is demonstrably insufficient. Examples: scam message classification, deepfake detection. |
| **LLM + RAG** | For open-ended cybersecurity assistance where the system must reason over a curated knowledge base and provide contextual, grounded guidance. LLMs must not be trained from scratch. API-based integration with RAG is the approved approach. |
| **Threat intelligence / reputation data** | For URL, phone number, and domain risk lookups where curated, maintained datasets provide reliable threat signal. |

### 3.2 Prohibited Claims

The following claims must **never** appear in any CyberShakti document, user interface, marketing material, or external communication:

- **100% detection rate** — no detection system achieves 100% detection
- **Perfect accuracy** — no ML model achieves perfect accuracy
- **Guaranteed protection** — cybersecurity tools reduce risk; they do not guarantee safety
- **Zero false positives** — false positives are an inherent property of detection systems
- **Zero false negatives** — false negatives are an inherent property of detection systems
- **Definitive identity verification** — CyberShakti assesses the risk that a profile may be fake; it does not verify identity

### 3.3 Explainability Requirement

- All AI/ML outputs that affect user decisions must include a **plain-language explanation** of why that result was produced.
- Probabilistic outputs must not be presented as definitive verdicts. Confidence levels must be communicated in user-accessible language.
- Features classified as **Research/Experimental** must communicate their experimental status and inherent uncertainty to users within the output itself.

### 3.4 Model Performance Principle

- Do not invent model performance numbers at any stage of documentation.
- All performance targets (precision, recall, F1-score, ROC-AUC, PR-AUC, false positive rate, false negative rate) are **TBD** until empirical evaluation on representative datasets is complete.
- Baseline models must be established and documented before advanced model variants are evaluated.
- Model versioning must be maintained using MLflow throughout the research, training, and deployment lifecycle.

### 3.5 Dataset Integrity Principle

- Datasets used for model training must be from reputable, documented sources.
- Dataset licensing and access restrictions must be verified before use.
- Dataset limitations must be documented — particularly where a dataset does not directly represent the real-world problem being solved.
- No data leakage between training, validation, and test sets is permitted.

---

## 4. Feature Classification System

CyberShakti Phase 1 uses a four-tier feature classification system. Every feature in the product is assigned exactly one tier. Tiers are locked and may not be reassigned without a recorded and approved change decision.

| Tier | Definition | Implications |
|---|---|---|
| **Core MVP** | Production-ready feature required for Phase 1 launch. | Must meet all quality, security, reliability, and accessibility standards before Phase 1 release. No shortcuts on testing or security review. |
| **Advanced MVP** | Planned Phase 1 feature with greater implementation complexity. Included in Phase 1 scope. | Implementation may be phased within Phase 1. Must meet the same quality standards as Core MVP upon completion. |
| **Research/Experimental** | Part of the Phase 1 product definition and research/training scope. The capability is researched, designed, and potentially trained during Phase 1. | Must **NOT** be represented as production-grade, guaranteed, or definitive functionality without empirical validation. Users must be clearly informed of the experimental status of all outputs from these features. |
| **Deferred/Future** | Approved product concept. Not in Phase 1 scope. | May be planned for a future phase. Must not be implemented in Phase 1 without a recorded and approved change decision. |

---

## 5. Feature Freeze Declaration

CyberShakti Phase 1 contains **exactly four pillars** and **exactly fourteen features**. This feature set is frozen for Phase 1.

**No additional top-level features may be added to Phase 1 without a recorded and approved change decision following the process in Section 14.**

### 5.1 Feature Inventory

| ID | Feature | Pillar | Phase 1 Tier |
|---|---|---|---|
| F-01 | Phishing Link Scanning | Pillar 1 — Detect & Analyze | Core MVP |
| F-02 | Message & Email Scam Detection | Pillar 1 — Detect & Analyze | Core MVP |
| F-03 | Screenshot Scam Scanner | Pillar 1 — Detect & Analyze | Core MVP |
| F-04 | QR Code Scam Scanner | Pillar 1 — Detect & Analyze | Core MVP |
| F-05 | Fake Profile Verification | Pillar 1 — Detect & Analyze | Advanced MVP |
| F-06 | Deepfake Detection | Pillar 1 — Detect & Analyze | Research/Experimental |
| F-07 | Mule Account Detection | Pillar 1 — Detect & Analyze | Research/Experimental |
| F-08 | Scam Call Blocking | Pillar 2 — Protect | Advanced MVP |
| F-09 | Password Security Checker | Pillar 2 — Protect | Core MVP |
| F-10 | Secure File Encryption | Pillar 2 — Protect | Core MVP |
| F-11 | AI Cybersecurity Assistant | Pillar 3 — Assist & Respond | Core MVP |
| F-12 | Cyber Risk Score | Pillar 3 — Assist & Respond | Core MVP |
| F-13 | Location-Based Scam Alerts | Pillar 3 — Assist & Respond | Advanced MVP |
| F-14 | Cyber Safety Hub | Pillar 4 — Learn & Prevent | Core MVP |

**Distribution:** Core MVP = 9 | Advanced MVP = 3 | Research/Experimental = 2 | Deferred/Future = 0

### 5.2 Pillar Purposes

| Pillar | Purpose |
|---|---|
| **Pillar 1 — Detect & Analyze** | Find, analyze, classify, and explain potential cyber threats targeting Indian consumers. |
| **Pillar 2 — Protect** | Protect users, accounts, communications, and sensitive data from identified threats. |
| **Pillar 3 — Assist & Respond** | Help users understand threats, assess their personal cybersecurity posture, and respond appropriately. |
| **Pillar 4 — Learn & Prevent** | Improve cybersecurity awareness and safer digital behavior through education and preventive guidance. |

### 5.3 Feature Scope Notes

- **F-08 Scam Call Blocking — Phase 1 scope**: in-app phone-number lookup and risk assessment against available threat and reputation data only. Android OS-level automatic call blocking is **deferred** to a future phase.
- **F-12 Cyber Risk Score — Phase 1 approach**: explainable weighted risk engine using a controlled set of in-app security signals and selected user-reported security-posture signals. ML-based risk prediction is **not** part of Phase 1.
- **F-06 and F-07 — Research/Experimental**: these features are part of the Phase 1 product definition and research/training scope. They must not be represented as production-grade capabilities without empirical validation.
- **Cybersecurity Quiz**: a sub-feature of F-14 Cyber Safety Hub. It is **not** a separate top-level feature.
- **"I've Been Scammed" incident response workflow**: deferred. It is **not** a separate top-level Phase 1 feature.

---

## 6. Technology Freeze Declaration

The following technology stack is frozen for Phase 1. No technology may be replaced, supplemented, or removed without a recorded and approved Architecture Decision Record (ADR) in `docs/00-decisions.md`.

### 6.1 Frontend

| Technology | Role |
|---|---|
| React | UI component framework |
| Vite | Frontend build tool |
| Tailwind CSS | Utility-first CSS styling |
| Framer Motion | UI animations |
| React Router | Client-side routing |
| Axios | HTTP client for API communication |
| Recharts | Data visualization and charts |

### 6.2 Backend

| Technology | Role |
|---|---|
| Python | Primary backend language |
| FastAPI | Web framework |
| Pydantic | Data validation and serialization |
| Uvicorn | ASGI server |
| Celery | Async task queue for heavy ML inference |
| Redis | Celery broker and application cache |

### 6.3 Database

| Technology | Role |
|---|---|
| PostgreSQL | Primary and only relational database |
| pgvector (PostgreSQL extension) | Vector similarity search for AI Assistant knowledge base — runs within PostgreSQL; not a separate database |
| PostGIS (PostgreSQL extension) | Geospatial queries for Location-Based Scam Alerts — runs within PostgreSQL; not a separate database |

### 6.4 Machine Learning

| Technology | Role |
|---|---|
| NumPy | Numerical computing |
| Pandas | Data manipulation and analysis |
| Scikit-learn | Classical ML utilities, preprocessing, baseline models |
| XGBoost | Gradient boosting — phishing detection, fake profile risk assessment, mule detection |
| LightGBM | Gradient boosting alternative for comparative evaluation |

### 6.5 Deep Learning

| Technology | Role |
|---|---|
| PyTorch | Primary deep learning framework |
| TorchVision | Computer vision model utilities |

### 6.6 NLP

| Technology | Role |
|---|---|
| Hugging Face Transformers | Model hub access and fine-tuning infrastructure |
| DistilBERT | Scam and email text classification |
| Tokenizers | Fast tokenization library |
| spaCy / NLTK | NLP utilities where appropriate (tokenization, entity recognition, text preprocessing) |

### 6.7 Computer Vision

| Technology | Role |
|---|---|
| OpenCV | Image preprocessing and manipulation |
| EfficientNet | Deepfake detection candidate model |
| Xception | Deepfake detection candidate model |

### 6.8 OCR

| Technology | Role |
|---|---|
| PaddleOCR | Text extraction from screenshots (F-03 pipeline) |

### 6.9 Graph

| Technology | Role |
|---|---|
| NetworkX | Graph feature engineering for mule account detection (Phase 1) |
| PyTorch Geometric | Graph Neural Networks — advanced/future path for mule detection; not Phase 1 production |

### 6.10 AI Assistant

| Technology | Role |
|---|---|
| API-based LLM | Language model for cybersecurity assistance — provider TBD (see ADR-013) |
| RAG pipeline | Retrieval-Augmented Generation over CyberShakti knowledge base |
| pgvector | Vector storage for knowledge base embeddings (within PostgreSQL) |

### 6.11 Security

| Technology | Role |
|---|---|
| AES-256-GCM | File encryption algorithm (F-10) |
| Argon2id | Password-derived key generation; configuration parameters TBD |
| JWT | Authentication tokens; configuration parameters TBD |
| RBAC | Role-Based Access Control for authorization |

### 6.12 Storage

| Technology | Role |
|---|---|
| S3-compatible object storage | Encrypted file storage, uploaded media (screenshots, QR images), model artefacts — provider TBD |

### 6.13 MLOps

| Technology | Role |
|---|---|
| MLflow | Model versioning and experiment tracking |
| Git + GitHub | Source control and collaboration |

### 6.14 Testing

| Technology | Role |
|---|---|
| Pytest | Backend unit and integration tests |
| Vitest | Frontend unit tests |
| React Testing Library | Frontend component tests |
| Playwright | End-to-end browser tests |
| Postman or Bruno | API contract tests |

### 6.15 DevOps

| Technology | Role |
|---|---|
| Docker | Containerization of all services |
| GitHub Actions | CI/CD pipeline automation |

### 6.16 Deployment

| Target | Technology |
|---|---|
| Frontend | Vercel |
| Backend | Render / Railway / AWS — final selection TBD based on workload, cost, and data residency considerations |
| Model training | Kaggle GPU / Google Colab GPU (development and research phase) |

### 6.17 Technologies Requiring an ADR Before Introduction

The following technologies must **not** be introduced without a recorded and approved ADR:

- Kubernetes
- Kafka
- MongoDB
- Any database beyond PostgreSQL (with its approved extensions)
- A separate, standalone vector database
- Multiple simultaneous cloud providers
- Microservices architecture decomposition

---

## 7. Architecture Principles

### 7.1 Preferred Architectural Pattern

**Modular Monolith + Isolated AI/ML Services where justified.**

The backend is a single deployable unit structured as well-defined internal modules. AI/ML inference workloads that are computationally heavy or have materially different scaling requirements may be isolated as Celery workers or separately deployable services where this is justified by concrete requirements.

### 7.2 Internal Module Boundaries

The backend must maintain clear internal module boundaries corresponding to the four product pillars, plus supporting modules for authentication, user management, and shared infrastructure. These boundaries must be respected throughout implementation. Modules must be independently testable.

### 7.3 Async Task Queue

Heavy ML inference operations (e.g., deepfake detection, screenshot OCR + NLP, mule detection) must be handled via **Celery + Redis** as an async task queue. This prevents these workloads from blocking synchronous API responses.

### 7.4 Single Database

PostgreSQL, with its pgvector and PostGIS extensions, is the **single database**. No additional databases may be introduced without a recorded ADR.

### 7.5 Requires a Recorded ADR Before Introduction

Microservices decomposition, Kubernetes, Kafka, MongoDB, separate vector databases, multiple simultaneous cloud providers.

---

## 8. Security Principles

### 8.1 Security by Design

Security is a first-class concern from architecture design onwards. It is not retrofitted after implementation. Every feature must have its threat model considered before engineering design begins.

### 8.2 Password Storage

Plaintext password storage is **strictly prohibited under all circumstances, without exception**. Passwords must be stored as hashes using Argon2id or bcrypt.

### 8.3 File Encryption

**AES-256-GCM** is the approved algorithm for file encryption in F-10 Secure File Encryption.

### 8.4 Password-Derived Keys

**Argon2id** is approved for password-derived key generation. The specific Argon2id parameters — memory cost, time cost, and parallelism factor — are **TBD pending security benchmarking and threat-model review**. These parameters must not be permanently locked in Phase 1 documentation and must not be arbitrarily assigned by developers or AI coding tools.

### 8.5 Authentication Tokens

**JWT** is approved for authentication. The specific algorithm (e.g., RS256 or HS256), access token expiry duration, and refresh token lifetime are **TBD pending threat-model review** (see ADR-026). These values must not be permanently set in Phase 1 documentation.

### 8.6 Authorization

**RBAC (Role-Based Access Control)** is the approved authorization model. Role definitions will be specified during Stage 2 Engineering Design. Minimum roles: user, admin.

### 8.7 Transport Security

All communications must use **HTTPS**. TLS 1.2 is the minimum acceptable version. TLS 1.3 is preferred.

### 8.8 Input Validation

All user inputs and all data received from external sources must be **validated and sanitized** before processing. This applies to: form inputs, file uploads, API payloads, URL parameters, and data from external threat intelligence sources.

### 8.9 Rate Limiting

Rate limiting is **required** on all public-facing endpoints to mitigate abuse, credential stuffing, and denial-of-service risk. Specific rate limit thresholds are **TBD pending benchmarking and threat-model review** (see ADR-026).

### 8.10 CORS

Cross-Origin Resource Sharing must be configured restrictively. **Wildcard origins (`*`) are not permitted in production** under any circumstances.

### 8.11 PII Protection

Sensitive personal data must be minimized, protected at rest using appropriate encryption and access controls, and **never stored unnecessarily in plaintext**. The system must collect only the data necessary for the stated purpose of each feature.

### 8.12 Security Configuration Parameters

All security configuration parameters marked TBD in this document — including Argon2id parameters, JWT expiry, refresh token lifetime, and rate limit thresholds — must be determined through proper security benchmarking and threat-model review before any production deployment. They must not be arbitrarily assigned by developers or AI coding tools during implementation.

---

## 9. Privacy Principles

### 9.1 Privacy by Design

Data minimization, purpose limitation, and user consent are built into every feature from the design stage onwards. Privacy is not a compliance checkbox — it is an architectural requirement.

### 9.2 Data Minimization

Collect only the data that is strictly necessary for the stated purpose of each feature. If a feature can be implemented without collecting a particular data point, it must not collect it.

### 9.3 Purpose Limitation

Data collected for one stated purpose must not be used for any other purpose without explicit user consent. Cross-purpose data use is not acceptable.

### 9.4 Informed Consent

Users must be clearly informed of what data is collected, how it is used, and how long it is retained before any data is collected. Consent must be meaningful and informed — not buried in terms and conditions.

### 9.5 Retention Limits

Personal data must not be retained beyond its required purpose or beyond applicable retention periods. Retention policies must be defined for each category of data during engineering design.

### 9.6 User Rights

Users must be able to:
- Access their personal data held by the system
- Request correction of inaccurate personal data
- Request deletion of their personal data (right to erasure)
- Withdraw consent where consent is the basis for processing

### 9.7 Regulatory References

The following are referenced as compliance areas requiring authoritative legal verification:

- India Information Technology Act 2000
- Digital Personal Data Protection Act 2023 (DPDP Act)
- RBI/NPCI guidelines relevant to financial fraud detection
- Data residency considerations for Indian users

Referencing these frameworks in this documentation does **not** constitute legal compliance. See Section 10.

---

## 10. Regulatory Acknowledgement

The following regulatory frameworks are relevant to CyberShakti's operation as an Indian-market cybersecurity product. They are flagged as compliance consideration areas:

| Framework | Relevance |
|---|---|
| **India IT Act 2000** | Governs electronic records, cybercrime, and data protection obligations for intermediaries operating in India. |
| **DPDP Act 2023** | India's personal data protection legislation. Covers consent, data minimization, data principal rights (access, correction, erasure), and obligations of data fiduciaries. |
| **RBI/NPCI guidelines** | Relevant to the threat landscape context — UPI fraud taxonomy, digital payment fraud patterns, reporting obligations. |
| **Data residency** | Considerations around where Indian users' personal data is stored and processed. May have implications for backend deployment target selection. |

### 10.1 Important Limitations

- This section is **informational**. It documents awareness of relevant regulatory frameworks.
- Referencing these regulations in CyberShakti documentation does **not** constitute legal compliance with any of them.
- Actual compliance obligations must be verified with **qualified legal counsel** and appropriate regulatory experts.
- This documentation must not invent or assert specific legal obligations, mandatory data residency requirements, or regulatory interpretations without authoritative, verified sources.
- CyberShakti must not claim regulatory compliance in any user-facing or external communication without proper legal verification.

---

## 11. Device Strategy

### 11.1 Phase 1 Platform

CyberShakti Phase 1 is a **responsive web application**. This is the only supported platform in Phase 1.

### 11.2 Mobile-First UX

Mobile-first is the **preferred design direction** for the Phase 1 web application, reflecting the reality that many Indian consumers primarily access the internet via mobile browsers. This direction must be validated and confirmed during the UI/UX design phase.

### 11.3 Native Android Application

A native Android application is **not a Phase 1 requirement**. Native Android development is deferred to a future phase.

### 11.4 Android Call-Screening Integration

Android OS-level automatic call screening or call blocking integration is **deferred** to a future phase. Phase 1 F-08 Scam Call Blocking is limited to in-app phone-number lookup and risk assessment against available threat/reputation data.

### 11.5 Native iOS Application

A native iOS application is **not in Phase 1 scope**.

---

## 12. Risk Severity Model

CyberShakti uses a consistent five-level risk severity model across all features that produce risk assessments or threat verdicts.

| Level | Label | Description |
|---|---|---|
| 1 | **Safe** | No threat signals detected. The analysed item shows no indicators of a threat based on available data and analysis. |
| 2 | **Low Risk** | Minor or uncertain signals detected. The item warrants awareness but does not require immediate action. Users should monitor or proceed with caution. |
| 3 | **Moderate Risk** | Notable threat signals detected. Caution is advised. Users should investigate further before proceeding. |
| 4 | **High Risk** | Strong threat signals detected. Action is recommended. Users should avoid interacting with the item and consider protective measures. |
| 5 | **Critical** | Confirmed or near-certain threat detected. Immediate action is required. Users must not interact with the item. |

### 12.1 Threshold Configuration

Exact numerical thresholds mapping model confidence scores or rule-based signal weights to each severity level are **configurable** and must be finalized after empirical evaluation of each feature's model or rule engine. Thresholds must not be permanently hard-coded in Phase 1 documentation.

### 12.2 Explanation Requirement

Every risk verdict produced by any feature must be accompanied by a plain-language explanation accessible to a non-technical Indian consumer. A verdict without an explanation does not meet the CyberShakti standard.

---

## 13. Traceability Principle

All major requirements must remain traceable through the following chain from the product level down to the test level:

```
Product Feature
      ↓
PRD Requirement
      ↓
TRD Requirement
      ↓
SRS Requirement
      ↓
Architecture Component
      ↓
API / Database Design
      ↓
Implementation Task
      ↓
Test Case
```

### 13.1 Implementation

The SRS (CSHAKTI-SRS-001) must include a **Requirements Traceability Matrix** that implements this chain for all functional requirements and non-functional requirements, linking each requirement to its PRD source, relevant constitutional principle, applicable ADR, and a test case placeholder.

### 13.2 Traceability IDs

All requirements must carry stable IDs throughout the chain:

- Feature IDs: F-01 through F-14
- PRD requirements: referenced by feature ID and section
- SRS functional requirements: FR-001 onwards
- SRS non-functional requirements: NFR-001 onwards
- ADRs: ADR-001 onwards
- Test cases: TC-001 onwards (assigned during Stage 3)

---

## 14. Change Control Rules

No locked requirement, technology decision, architecture decision, or feature scope may be **silently changed** by a developer, engineer, or AI coding tool.

### 14.1 Change Control Process

Any proposed change to locked content must follow this six-step process:

| Step | Action |
|---|---|
| **1. Identify** | Identify the affected decision or requirement by its ID (ADR number, requirement ID, or document section reference). |
| **2. Explain** | Document the reason for the proposed change. Vague explanations ("it seemed better") are not acceptable. |
| **3. Identify Impact** | Identify all documents that would be affected by the change. |
| **4. Describe Consequences** | Describe the technical and product impact — what changes, what breaks, what dependencies are affected. |
| **5. Record** | Record the proposed change in `docs/00-decisions.md` as a new ADR or an amendment to an existing ADR. |
| **6. Approve** | The change becomes authoritative only after explicit approval from the project decision authority. A change recorded but not yet approved is in **Pending** status and must not be acted upon. |

### 14.2 Scope of Change Control

This process applies to changes to any of the following:

- Any principle, rule, or constraint in this Project Constitution
- Any Architecture Decision Record in `docs/00-decisions.md`
- Any PRD acceptance criterion
- Any TRD specification or performance target
- Any SRS functional or non-functional requirement
- The feature freeze (Section 5)
- The feature classification tiers (Section 4 and 5)
- The technology freeze (Section 6)
- The architecture principles (Section 7)

---

## 15. Development Agent Rules

### 15.1 Approved Tools

The following AI-assisted development tools are approved for use during CyberShakti implementation: **Kiro, Antigravity, Cursor**, and other AI-assisted coding tools as appropriate.

### 15.2 Role of AI Development Tools

These tools are **implementation assistants**. Their role is to accelerate implementation of approved, documented requirements. They are **not** sources of project requirements, architecture decisions, or product scope.

### 15.3 Prohibited Autonomous Actions

AI coding tools and agents must **not** autonomously:

- Add features or modify feature scope
- Change the approved technology stack
- Replace, supplement, or remove databases
- Change the approved architecture pattern
- Remove, weaken, or bypass security requirements
- Change AI/ML model choices or feature classification tiers
- Modify product scope or the feature freeze
- Silently resolve open decisions
- Claim or assert regulatory compliance on behalf of the project
- Permanently set security configuration parameters that are marked TBD

### 15.4 Required Behaviour

When an AI coding tool encounters a situation where the approved documentation appears incomplete, ambiguous, or in conflict:

- It must **flag the issue** rather than resolve it autonomously
- It must **not proceed** with a change that contradicts approved documentation
- Any deviation from approved documentation must go through the **change control process** defined in Section 14

---

## 16. Documentation Rules

### 16.1 Hierarchy Enforcement

The documentation hierarchy governs all project documentation. Each document is the source of truth for its designated layer. Documents may not be authored out of order.

### 16.2 Downstream Constraint

Downstream documents may reference and elaborate on upstream decisions and principles. They may **not** contradict them. If elaboration in a downstream document reveals a gap or conflict in an upstream document, that conflict must be recorded per Section 16.3.

### 16.3 Conflict Resolution

When a conflict between this constitution and any downstream document is discovered:

1. Record the conflict as an unresolved decision in `docs/00-decisions.md`
2. Do not silently edit either document to resolve it
3. The conflict remains open until explicitly resolved through the change control process

### 16.4 Validation Gates

Each document in the hierarchy must be **explicitly validated** before the next document is authored. Validation must produce a written report identifying: completeness, contradictions, invented assumptions, and open decisions.

### 16.5 Document Status Lifecycle

All documents follow this status lifecycle: **Draft → Under Review → Locked**

Documents must not be treated as authoritative until they reach **Locked** status following a successful validation review.

### 16.6 No Invented Content

Documentation must not contain:
- Invented performance metrics
- Invented model accuracy numbers
- Invented latency targets
- Invented user adoption figures
- Asserted regulatory compliance
- Fabricated dataset descriptions
- Unsupported technical claims

---

## 17. Success Metrics Principle

### 17.1 No Invented Metrics

Numerical success metrics must not be invented at any stage of documentation or planning. Fabricated numbers create false expectations, mislead development prioritization, and undermine the credibility of the product definition.

### 17.2 Where Empirical Baselines Do Not Exist

Where empirical baselines do not yet exist:
- Define **measurable qualitative outcomes** that describe what success looks and feels like
- Mark any numerical targets as **TBD**
- Add a note describing how numerical targets will be established (e.g., "to be set after usability testing", "to be set after model validation on representative dataset", "to be set after production monitoring baseline is established")

### 17.3 Prohibited Fabrications

The following types of numbers must never be fabricated in any CyberShakti document:

- Model precision, recall, F1-score, ROC-AUC, or PR-AUC values
- API latency or response time targets (unless grounded in benchmarking)
- User adoption rates, DAU/MAU targets, or retention rates
- User satisfaction scores (CSAT, NPS, etc.)
- System availability or uptime percentages
- False positive rates or false negative rates

### 17.4 Establishing Quantitative Targets

Quantitative performance targets are established through:
- **Empirical benchmarking** (for latency, throughput)
- **Model validation on representative holdout datasets** (for ML model metrics)
- **Usability testing** (for user experience metrics)
- **Production monitoring** (for availability and reliability targets)

Until these activities are completed, all numerical targets remain **TBD**.

---

*End of CyberShakti Project Constitution — CSHAKTI-CONST-001 v1.0.0*

*This document may only be amended through the change control process defined in Section 14.*
