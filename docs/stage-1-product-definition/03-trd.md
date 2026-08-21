# CyberShakti — Technical Requirements Document

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-TRD-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-15 |
| **Traces To** | CSHAKTI-PRD-001, CSHAKTI-PVS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — all content must be consistent with the constitution. Conflicts recorded in `docs/00-decisions.md`. |

---

## Table of Contents

1. [Technology Stack Specification](#1-technology-stack-specification)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [AI/ML Pipeline Specifications](#3-aiml-pipeline-specifications)
4. [LLM and RAG Architecture](#4-llm-and-rag-architecture)
5. [Security Technical Requirements](#5-security-technical-requirements)
6. [Database Technical Requirements](#6-database-technical-requirements)
7. [Infrastructure Requirements](#7-infrastructure-requirements)
8. [Performance Requirements](#8-performance-requirements)
9. [External Integration Requirements](#9-external-integration-requirements)
10. [Testing Requirements](#10-testing-requirements)

---

## 1. Technology Stack Specification

The following stack is frozen per CSHAKTI-CONST-001 §6. No technology may be replaced, added, or removed without a recorded and approved ADR in `docs/00-decisions.md`.

### 1.1 Frontend

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| React | UI component framework | Latest stable (v18+) | ADR-003 |
| Vite | Build tool | Latest stable | ADR-003 |
| Tailwind CSS | Utility-first CSS | Latest stable (v3+) | ADR-003 |
| Framer Motion | UI animations | Latest stable | ADR-003 |
| React Router | Client-side routing | Latest stable (v6+) | ADR-003 |
| Axios | HTTP client | Latest stable | ADR-003 |
| Recharts | Data visualisation | Latest stable | ADR-003 |

**Rationale:** React + Vite is the selected stack (ADR-003) for its ecosystem maturity, AI coding tool support, and build performance. Exact versions are pinned during implementation — not in Phase 1 documentation.

### 1.2 Backend

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| Python | Primary backend language | 3.11+ (LTS) | ADR-004 |
| FastAPI | Web framework | Latest stable | ADR-004 |
| Pydantic | Data validation and serialisation | v2+ | ADR-004 |
| Uvicorn | ASGI server | Latest stable | ADR-004 |
| Celery | Async task queue | Latest stable | ADR-004, ADR-014 |
| Redis | Celery broker and cache | Latest stable (7+) | ADR-004, ADR-014 |

**Rationale:** Python + FastAPI aligns the API layer with the ML stack (ADR-004), eliminating language boundary. Celery + Redis isolates heavy ML inference as async tasks (ADR-014).

### 1.3 Database

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| PostgreSQL | Primary and only relational database | 15+ | ADR-005 |
| pgvector | Vector similarity search extension | Latest stable | ADR-006 |
| PostGIS | Geospatial query extension | Latest stable | ADR-007 |

**Rationale:** Single database instance with extensions satisfies all Phase 1 storage needs without additional infrastructure (ADR-005, ADR-006, ADR-007).

### 1.4 Machine Learning

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| NumPy | Numerical computing | Latest stable | — |
| Pandas | Data manipulation | Latest stable (2+) | — |
| Scikit-learn | Classical ML, preprocessing | Latest stable | — |
| XGBoost | Gradient boosting | Latest stable | ADR-008, ADR-011 |
| LightGBM | Gradient boosting (comparison) | Latest stable | ADR-008 |

### 1.5 Deep Learning

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| PyTorch | Deep learning framework | Latest stable (2+) | ADR-009, ADR-010 |
| TorchVision | Computer vision utilities | Latest stable | ADR-010 |

### 1.6 NLP

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| Hugging Face Transformers | Model hub and fine-tuning | Latest stable | ADR-009 |
| DistilBERT | Scam/email text classification | Pretrained base from HuggingFace | ADR-009 |
| Tokenizers | Fast tokenisation | Latest stable | ADR-009 |
| spaCy / NLTK | NLP utilities | Latest stable | — |

### 1.7 Computer Vision and OCR

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| OpenCV | Image preprocessing | Latest stable | ADR-010, ADR-022 |
| EfficientNet | Deepfake detection candidate | Via TorchVision or timm | ADR-010 |
| Xception | Deepfake detection candidate | Via custom PyTorch implementation | ADR-010 |
| PaddleOCR | Screenshot text extraction | Latest stable | ADR-022 |

### 1.8 Graph

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| NetworkX | Graph feature engineering | Latest stable | ADR-011 |
| PyTorch Geometric | GNN — advanced future path only | Latest stable (installed but not production in Phase 1) | ADR-011 |

### 1.9 AI Assistant

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| API-based LLM | Language model | Provider TBD — ADR-013 (Open) | ADR-013 |
| RAG pipeline | Retrieval-Augmented Generation | Custom implementation | ADR-013, ADR-006 |
| pgvector | Knowledge base embedding storage | Within PostgreSQL | ADR-006 |

### 1.10 Security Technologies

| Technology | Role | Version Guidance | ADR |
|---|---|---|---|
| AES-256-GCM | File encryption | Standard library implementation | ADR-021 |
| Argon2id | Password-derived key generation | argon2-cffi or equivalent | ADR-021, ADR-026 |
| JWT | Authentication tokens | python-jose or PyJWT | ADR-019, ADR-026 |
| RBAC | Authorisation model | Custom implementation in FastAPI | ADR-019 |

### 1.11 Storage, MLOps, Testing, DevOps

| Technology | Role | ADR |
|---|---|---|
| S3-compatible object storage | File and media storage | ADR-031 (Open) |
| MLflow | Model versioning and experiment tracking | — |
| Git + GitHub | Source control | ADR-015 |
| Pytest | Backend tests | — |
| Vitest | Frontend unit tests | — |
| React Testing Library | Frontend component tests | — |
| Playwright | End-to-end tests | — |
| Postman or Bruno | API contract tests | — |
| Docker | Containerisation | ADR-014 |
| GitHub Actions | CI/CD | — |
| Vercel | Frontend deployment | ADR-003 |
| Render / Railway / AWS | Backend deployment (TBD) | ADR-004 |


---

## 2. System Architecture Overview

### 2.1 Architectural Pattern

**Modular Monolith + Isolated AI/ML Services via Celery async workers** (ADR-014).

The backend is a single deployable FastAPI application with clear internal module boundaries aligned to the four product pillars. Heavy ML inference is offloaded to Celery workers. No microservices decomposition in Phase 1.

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                             │
│          React + Vite SPA (Responsive Web Application)         │
│                  Deployed: Vercel                               │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTPS / REST (JSON)
┌───────────────────────────▼─────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│              FastAPI + Uvicorn (ASGI)                           │
│         JWT Authentication Middleware                           │
│         RBAC Authorisation Middleware                           │
│         Input Validation (Pydantic)                             │
│         Rate Limiting Middleware                                 │
└────┬──────────┬──────────┬──────────┬──────────┬───────────────┘
     │          │          │          │          │
┌────▼───┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────┐ ┌───▼────────────┐
│Detect & │ │Protect │ │Assist &│ │Learn & │ │User & Auth     │
│Analyze  │ │Module  │ │Respond │ │Prevent │ │Module          │
│Module   │ │        │ │Module  │ │Module  │ │                │
│F-01..07 │ │F-08..10│ │F-11..13│ │F-14    │ │Auth/RBAC/      │
└────┬────┘ └───┬────┘ └───┬────┘ └────────┘ │Profile/Score   │
     │          │          │                  └───────┬────────┘
     └──────────┴──────────┴──────────────────────────┘
                            │
          ┌─────────────────▼──────────────────────┐
          │         CELERY ASYNC TASK LAYER         │
          │  Redis Broker                           │
          │                                         │
          │  Workers:                               │
          │  - PhishingURLAnalyzer                  │
          │  - ScamTextClassifier (F-02, F-03)      │
          │  - OCRPipeline (F-03)                   │
          │  - FakeProfileAssessor (F-05)           │
          │  - DeepfakeDetector (F-06) [Exp]        │
          │  - MuleAccountDetector (F-07) [Exp]     │
          │  - AIAssistantRAG (F-11)                │
          └─────────────────┬──────────────────────┘
                            │
          ┌─────────────────▼──────────────────────┐
          │           DATA LAYER                    │
          │                                         │
          │  PostgreSQL (primary database)          │
          │  ├── pgvector extension                 │
          │  │   (AI Assistant knowledge base)      │
          │  └── PostGIS extension                  │
          │      (Location-based scam alerts)       │
          │                                         │
          │  Redis (cache + Celery broker)          │
          └─────────────────┬──────────────────────┘
                            │
          ┌─────────────────▼──────────────────────┐
          │         STORAGE LAYER                   │
          │  S3-compatible object storage           │
          │  (encrypted files, uploaded media,      │
          │   MLflow model artefacts)               │
          │  Provider: TBD (ADR-031)                │
          └─────────────────┬──────────────────────┘
                            │
          ┌─────────────────▼──────────────────────┐
          │         EXTERNAL SERVICES               │
          │  Threat Intelligence API (ADR-032 TBD) │
          │  LLM API (ADR-013 Open)                 │
          └────────────────────────────────────────┘
```

### 2.3 Module Boundaries

The backend maintains these internal module boundaries (not separate services — internal packages):

| Module | Responsibility | Features Served |
|---|---|---|
| `detect_analyze` | Orchestrates all detection and analysis features | F-01, F-02, F-03, F-04, F-05, F-06, F-07 |
| `protect` | Orchestrates protection features | F-08, F-09, F-10 |
| `assist_respond` | Orchestrates assist and respond features | F-11, F-12, F-13 |
| `learn_prevent` | Serves Cyber Safety Hub content | F-14 |
| `users_auth` | Registration, login, 2FA, account management | Auth flows |
| `shared` | Common utilities, risk model, explanation engine, threat intelligence client | All features |

### 2.4 Synchronous vs. Asynchronous Operations

| Category | Handling | Features |
|---|---|---|
| Lightweight synchronous | Direct FastAPI response | F-08 (number lookup), F-09 (password check), F-12 (score read), F-13 (alert query), F-14 (content fetch), Auth |
| Synchronous ML inference (fast) | FastAPI response after in-process inference | F-01 (URL scan), F-02 (text scan) |
| Async heavy inference | Celery task; client polls or receives notification | F-03 (OCR+NLP), F-05 (profile), F-06 (deepfake), F-07 (mule), F-11 (LLM call) |
| File operations | Streaming upload/download | F-10 (encrypt/decrypt) |


---

## 3. AI/ML Pipeline Specifications

All performance targets are TBD pending empirical evaluation. No accuracy numbers are invented. Baseline models must be established before advanced models are evaluated (CSHAKTI-CONST-001 §3.4).

---

### 3.1 F-01 — Phishing URL Classification Pipeline

**Feature:** F-01 Phishing Link Scanning | **Tier:** Core MVP | **ADR:** ADR-008 (Provisional)

**Pipeline:**
```
URL Input
  ↓
Input Validation & Normalisation
  ↓
URL Feature Engineering
  (lexical features, domain features, path/query features)
  ↓
Rule-Based Pre-Filter
  (known-safe domain whitelist, known-malicious blocklist)
  ↓
Threat Intelligence Lookup
  (ADR-032 — source TBD)
  ↓
XGBoost Classifier
  (on engineered features)
  ↓
Risk Score Aggregation
  (combines TI match + ML score)
  ↓
Risk Level Assignment (Safe–Critical)
  ↓
Plain-Language Explanation Generation
  ↓
Response
```

**Datasets:**
- PhishTank (public phishing URL dataset — community-contributed)
- URLhaus by abuse.ch (malicious URL dataset)
- Additional reputable public phishing URL datasets as identified
- Legitimate URL samples from public crawls and curated lists
- **Licensing:** All datasets must be verified for licensing/access terms before use

**Preprocessing:**
- URL parsing and normalisation (scheme, domain, path, query, fragment extraction)
- Domain registration age lookup (where available from WHOIS or similar — may be deferred)
- Redirect chain handling: Phase 1 analyses submitted URL only (no redirect following)

**Feature Engineering:**
- Lexical: URL length, domain length, path length, number of special characters, entropy of URL string, presence of IP address instead of domain, suspicious TLD list membership
- Domain: age of domain (if available), subdomain depth, presence of brand keywords in non-brand domain
- Path/Query: number of parameters, presence of suspicious keywords (login, banking, verify, update, OTP), base64-like strings in path
- Structural: URL scheme (http vs https), port specification, presence of @ character

**Model Candidates:**
- Baseline: TF-IDF on URL tokens + Logistic Regression (establish first)
- Primary: XGBoost on engineered features
- Comparison: LightGBM on engineered features

**Training Environment:** Local development machine; Kaggle GPU if dataset scale requires

**Validation Metrics Required:**
- Precision, Recall, F1-score (phishing class)
- ROC-AUC, PR-AUC
- False Positive Rate (legitimate URLs flagged as phishing)
- False Negative Rate (phishing URLs missed)
- All values: **TBD — not to be invented**

**Performance Targets:** TBD after empirical evaluation on representative holdout dataset

**Known Limitations (must be documented):**
- Newly registered phishing domains not yet in training data will evade detection initially
- Adversarial URL obfuscation techniques can defeat lexical feature analysis
- Dataset freshness degrades over time — model retraining pipeline required
- Domain age features require WHOIS lookups which add latency and may not be available for all domains

**Model Versioning:** MLflow — experiment tracking, model registry, version tagging

---

### 3.2 F-02 — Scam Text Classification Pipeline

**Feature:** F-02 Message & Email Scam Detection | **Tier:** Core MVP | **ADR:** ADR-009 (Provisional)

**Pipeline:**
```
Text Input
  ↓
Input Validation (length, encoding)
  ↓
Text Preprocessing
  (cleaning, normalisation, tokenisation)
  ↓
Baseline Model (TF-IDF + Logistic Regression)
  [Established first — before fine-tuning]
  ↓
DistilBERT Fine-Tuned Classifier
  (trained on scam/spam dataset)
  ↓
Confidence Score
  ↓
Risk Level Assignment
  ↓
Scam Category Classification (where confident)
  ↓
Plain-Language Explanation
  ↓
Response
```

**Datasets:**
- Public SMS spam/scam datasets (e.g., UCI SMS Spam Collection, Kaggle spam datasets)
- India-specific scam text examples (collection strategy TBD — manual curation, community contribution)
- Legitimate message samples for negative class
- **Licensing:** All datasets must be verified before use. India-specific data collection must comply with applicable privacy requirements.

**Preprocessing:**
- Text cleaning: remove excessive whitespace, normalise unicode, strip HTML tags if present
- Language detection: flag non-English text for appropriate handling (Phase 1 is English-primary)
- Tokenisation: Hugging Face tokenizer aligned with DistilBERT vocabulary

**Model Candidates:**
- Baseline (mandatory): TF-IDF vectorisation + Logistic Regression
- Baseline 2: TF-IDF + SVM
- Primary: DistilBERT fine-tuned on scam classification task

**Baseline Requirement:** The classical baseline must be evaluated on the same holdout set before DistilBERT fine-tuning begins. If the baseline performance is sufficient for the use case, the simpler model is preferred (CSHAKTI-CONST-001 §3.1).

**Training Environment:** Kaggle GPU / Google Colab GPU (T4 or better)

**Validation Metrics Required:**
- Precision, Recall, F1-score (scam class)
- ROC-AUC, PR-AUC
- False Positive Rate, False Negative Rate
- Comparison table: baseline vs. DistilBERT
- All values: **TBD**

**Performance Targets:** TBD after empirical evaluation

**Known Limitations:**
- Phase 1 model is primarily English; Hindi and regional language scam texts will not be reliably classified
- Novel scam patterns not in training data may not be detected
- Very short messages (under ~5 tokens) may not provide sufficient context for reliable classification
- Adversarial text (deliberate misspellings, character substitutions) can evade detection

**Model Versioning:** MLflow

---

### 3.3 F-03 — Screenshot Scam Scanner Pipeline

**Feature:** F-03 Screenshot Scam Scanner | **Tier:** Core MVP | **ADR:** ADR-022 (PaddleOCR — Provisional)

**Pipeline:**
```
Image Upload (JPEG/PNG)
  ↓
Image Validation (format, size, basic integrity)
  ↓
Image Preprocessing (OpenCV)
  (resize if necessary, contrast enhancement for low-quality images)
  ↓
PaddleOCR Text Extraction
  ↓
OCR Confidence Assessment
  ↓
Extracted Text → F-02 Scam Text Classification Pipeline
  ↓
Risk Level + OCR Quality Indicator + Explanation
  ↓
Response
```

**Dependencies:** F-03 quality is bounded by PaddleOCR accuracy on the input image. OCR errors propagate to the downstream NLP classifier.

**OCR Configuration:**
- PaddleOCR with multi-language model (English + Hindi support where available)
- Local deployment — images are NOT sent to external OCR services (privacy principle)
- Confidence threshold for OCR output to be determined during engineering design

**Performance Targets:** TBD after OCR accuracy benchmarking on representative Indian screenshot corpus (WhatsApp, SMS, email app formats)

**Known Limitations:**
- OCR accuracy degrades significantly on very low resolution or heavily compressed screenshots
- Mixed-script text (Devanagari + Latin in same line) may produce OCR errors
- Non-text scam indicators (visual elements, logos) are not detected — text only
- Screenshots with decorative fonts or stylised text may not be extracted accurately

**Model Versioning:** N/A — no separate model; PaddleOCR version pinned in requirements


---

### 3.4 F-04 — QR Code Scanner Pipeline

**Feature:** F-04 QR Code Scam Scanner | **Tier:** Core MVP | **ADR:** ADR-023

**Pipeline:**
```
QR Code Image Upload
  ↓
Image Validation
  ↓
QR Decode (standard QR decode library)
  ↓
Content Type Detection
  (URL / vCard / WiFi / Plain Text / Other)
  ↓
  ├── If URL → F-01 Phishing URL Analysis Pipeline
  └── If Non-URL → Content Type Response (no URL analysis applied)
  ↓
Risk Verdict + Decoded Content + Explanation
  ↓
Response
```

**QR Decode Library:** Standard Python QR decode library (e.g., pyzbar, opencv-based decoder, or equivalent well-maintained library — specific selection during implementation). No ML model for QR image analysis.

**Known Limitations:**
- Quality of URL risk assessment is bounded by F-01 pipeline quality
- Non-URL QR content cannot be assessed for safety beyond content type identification
- Damaged or partial QR codes cannot be decoded

---

### 3.5 F-05 — Fake Profile Risk Assessment Pipeline

**Feature:** F-05 Fake Profile Verification | **Tier:** Advanced MVP | **ADR:** ADR-011 (Provisional — same model family as F-07)

**Pipeline:**
```
Profile Signal Inputs
  ↓
Input Validation
  ↓
Feature Engineering
  (account age signal, follower/following ratio, post frequency,
   profile completeness, content consistency indicators,
   name pattern analysis — exact features defined in engineering design)
  ↓
XGBoost / LightGBM Classifier
  (trained on fake profile research datasets)
  ↓
Risk Score
  ↓
Risk Level Assignment
  ↓
Explanation (which signals contributed)
  ↓
Identity Verification Disclaimer (mandatory)
  ↓
Response
```

**Datasets:** Public fake profile and social network research datasets (e.g., datasets from academic research on bot/fake account detection). Licensing and access must be verified before use. Real-world ground truth for fake profiles is inherently limited.

**Model Candidates:**
- XGBoost on engineered profile features
- LightGBM on engineered profile features

**Validation Metrics Required:** Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, FNR — all TBD

**Known Limitations:**
- Ground truth for "definitely fake" profiles is difficult to establish from public datasets
- Feature set is limited to observable, user-submitted signals in Phase 1 (no platform API access)
- Sophisticated fake profiles designed to evade detection will not be reliably caught
- This feature must always be presented as risk assessment, never as identity verification

**Model Versioning:** MLflow

---

### 3.6 F-06 — Deepfake Detection Pipeline

**Feature:** F-06 Deepfake Detection | **Tier:** Research/Experimental | **ADR:** ADR-010 (Provisional)

> **Research/Experimental:** This pipeline is for Phase 1 research and training scope. Production-grade performance is not guaranteed and must not be claimed without empirical validation.

**Pipeline:**
```
Image or Video Upload
  ↓
File Validation (type, size)
  ↓
Preprocessing (OpenCV)
  ├── Image: face detection → face crop → resize to model input dimensions
  └── Video: frame extraction → per-frame face detection and crop
  ↓
CNN Classifier (EfficientNet or Xception — selected by empirical evaluation)
  ↓
Per-Frame Scores (for video)
  ↓
Score Aggregation (for video: mean / max of frame scores)
  ↓
Confidence Assessment
  ↓
Risk Assessment + Research/Experimental Disclaimer + Confidence Indicator
  ↓
Response
```

**Datasets:**
- FaceForensics++ (academic dataset — access via official request to Technical University of Munich)
- Celeb-DF (academic dataset)
- DFDC (Deepfake Detection Challenge dataset — Meta AI Research)
- **Access and licensing for each dataset must be verified and respected before any use. Restricted access datasets require formal request/approval.**

**Model Candidates:**
- EfficientNet-B4 (or similar variant) — fine-tuned for binary classification (real/fake)
- Xception — fine-tuned for binary classification

**Training Environment:** Kaggle GPU / Google Colab GPU (P100 or T4 or better)

**Validation Metrics Required:** Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, FNR — all TBD

**Performance Targets:** TBD — Research/Experimental status means production-grade accuracy cannot be guaranteed in Phase 1. Initial models are expected to have meaningful false positive and false negative rates.

**Known Limitations (must be documented prominently):**
- Deepfake detection is an active research problem with no universally reliable solution
- Models trained on one generation method (FaceForensics++) may not generalise to other methods
- Adversarial deepfakes designed to evade detection models will not be reliably caught
- High false positive rate on genuine but unusual images (heavy filters, artistic photos) is expected
- No face detected in image → cannot be assessed
- Very short video clips provide insufficient frames for reliable analysis
- This feature must never be presented as definitive deepfake detection capability

**Model Versioning:** MLflow

---

### 3.7 F-07 — Mule Account Detection Pipeline

**Feature:** F-07 Mule Account Detection | **Tier:** Research/Experimental | **ADR:** ADR-011 (Provisional), ADR-024

> **Research/Experimental:** This pipeline is for Phase 1 research and training scope. The primary research datasets (Elliptic/Elliptic2) represent cryptocurrency transaction networks, not bank accounts (ADR-024). Real-world bank mule detection applicability is not validated in Phase 1.

**Pipeline:**
```
Account Signal Inputs
  ↓
Input Validation
  ↓
Tabular Feature Engineering
  (account-level signals: transaction frequency, account age, etc.)
  ↓
Graph Construction (NetworkX)
  (build transaction graph from available signals)
  ↓
Graph Feature Engineering
  (degree centrality, clustering coefficient, community membership,
   path lengths, hub/authority scores — exact features defined in engineering design)
  ↓
Combined Feature Vector (tabular + graph features)
  ↓
XGBoost Classifier
  ↓
Risk Score
  ↓
Risk Level + Full Disclaimer Set + Explanation
  ↓
Response
```

**Advanced Future Path (not Phase 1 production):**
Graph Neural Network via PyTorch Geometric (installed but not deployed in Phase 1 production).

**Datasets:**
- Elliptic dataset (Bitcoin transaction graph with labelled illicit/licit transactions — available on Kaggle)
- Elliptic2 dataset (extended version)
- **Critical limitation (ADR-024):** These datasets represent cryptocurrency transaction networks. They do not represent traditional bank account mule patterns. The applicability of models trained on these datasets to real-world bank mule detection is NOT validated and must NOT be assumed.

**Validation Metrics Required:** Precision, Recall, F1, ROC-AUC, PR-AUC, FPR, FNR — all TBD

**Known Limitations (must be documented prominently):**
- Dataset domain mismatch: Elliptic represents crypto, not bank accounts
- Real-world bank mule detection requires domain-appropriate labelled data not available in Phase 1
- Graph construction from limited user-submitted signals will be less informative than full transaction graph data
- This feature must never be presented as definitive mule account detection
- Results must not be used as the basis for any legal, financial, or regulatory action

**Model Versioning:** MLflow


---

## 4. LLM and RAG Architecture

**Feature:** F-11 AI Cybersecurity Assistant | **ADR:** ADR-013 (Open — LLM provider TBD), ADR-006

### 4.1 Architecture Overview

```
User Query
  ↓
Query Preprocessing (cleaning, length validation)
  ↓
Query Embedding (embedding model — provider-dependent or separate embedding model)
  ↓
pgvector Similarity Search
  (top-k nearest neighbours in CyberShakti knowledge base)
  ↓
Context Retrieval (top-k relevant knowledge base chunks)
  ↓
Prompt Construction
  (system prompt + retrieved context + user query)
  ↓
LLM API Call (provider TBD — ADR-013)
  ↓
Response Post-Processing
  (grounding check, disclaimer injection)
  ↓
Response to User + AI Disclaimer
```

### 4.2 Knowledge Base Design

**Content scope (Phase 1):**
- Cybersecurity awareness content covering Indian threat taxonomy (UPI fraud, WhatsApp scams, OTP theft, phishing, scam calls, deepfakes, fake profiles)
- CyberShakti feature explanations (how each feature works, what results mean)
- Threat glossary (plain-language definitions of cybersecurity terms)
- Preventive guidance content (what to do if you receive a suspicious call/message)
- CERT-In advisories and public cybersecurity guidance (attributed and referenced)

**Chunking strategy:** Content is split into semantically meaningful chunks (paragraph or section level — exact chunking strategy defined during engineering design). Each chunk stores: text content, source reference, date, topic tags.

**Embedding model:** TBD — dependent on LLM provider selection (ADR-013). Provider-native embedding model or a separate open-source embedding model (e.g., sentence-transformers). Decision recorded as part of ADR-013 resolution.

### 4.3 pgvector Schema Concept

```sql
-- Conceptual schema (not final — detailed schema in Stage 2 Database Design)
knowledge_base_chunks (
  id              UUID PRIMARY KEY,
  content         TEXT NOT NULL,
  embedding       VECTOR(N),  -- dimension N depends on embedding model
  source_title    TEXT,
  source_url      TEXT,
  topic_tags      TEXT[],
  created_at      TIMESTAMP,
  updated_at      TIMESTAMP
)
-- Index: pgvector IVFFlat or HNSW index on embedding column
```

### 4.4 Retrieval Strategy

- Top-k similarity search (k TBD during engineering design — typically 3–5 chunks)
- Similarity metric: cosine similarity (pgvector default)
- Minimum similarity threshold to prevent irrelevant retrieval (threshold TBD)
- If retrieval returns no sufficiently similar chunks: assistant acknowledges the knowledge gap rather than fabricating an answer

### 4.5 Grounding and Hallucination Mitigation

- System prompt must instruct the LLM to answer only based on retrieved context
- System prompt must instruct the LLM to acknowledge when it does not know rather than fabricating
- System prompt must instruct the LLM not to provide legal, financial, or medical advice
- Post-processing step checks response for absence of context — if the LLM appears to have answered beyond the retrieved content, a fallback or disclaimer is applied
- All responses include the mandatory AI disclaimer (CSHAKTI-PRD-001 §4.3)

### 4.6 Provider Independence

The RAG pipeline, knowledge base, and pgvector schema are designed to be LLM-provider-independent. The LLM API call is isolated in a provider adapter layer. When ADR-013 is resolved, only the provider adapter requires changes — the rest of the pipeline is unaffected.

---

## 5. Security Technical Requirements

### 5.1 Password Storage

Passwords must be stored as hashes. Approved algorithms: Argon2id (preferred) or bcrypt. Plaintext password storage is **strictly prohibited** under all circumstances (CSHAKTI-CONST-001 §8.2).

Implementation: use a well-maintained Python library (e.g., `argon2-cffi` for Argon2id, `bcrypt` for bcrypt). Do not implement password hashing from scratch.

### 5.2 File Encryption (F-10)

- Algorithm: AES-256-GCM (authenticated encryption — provides confidentiality and integrity)
- Key derivation: Argon2id from user-supplied password
- Argon2id parameters (memory cost, time cost, parallelism): **TBD — ADR-026** — must be determined through benchmarking on target deployment hardware
- Nonce (IV) management: a fresh random nonce must be generated for every encryption operation. Nonce reuse with the same key is a critical security failure and is strictly prohibited.
- Nonce and Argon2id salt are embedded in the encrypted file output for self-contained decryption
- Encrypted file format must be documented during engineering design

### 5.3 Authentication Tokens (JWT)

- JWT is the approved authentication mechanism (ADR-019)
- Algorithm: RS256 (asymmetric) preferred over HS256 (symmetric) for better key management — **final selection in engineering design**
- Access token expiry: **TBD — ADR-026** — must not be permanently set in Phase 1
- Refresh token lifetime: **TBD — ADR-026**
- Refresh token rotation: recommended (new refresh token issued on each use; old invalidated)
- Token storage on client: HttpOnly cookies preferred over localStorage for XSS resistance — final decision in engineering design
- All tokens must be validated on every protected API request

### 5.4 Authorisation (RBAC)

- RBAC model approved (ADR-019)
- Phase 1 minimum roles: `user` (standard authenticated user), `admin` (system administration)
- Role definitions and permission matrices: defined in Stage 2 Engineering Design
- All API endpoints must explicitly declare required role; no endpoint defaults to unrestricted access

### 5.5 Transport Security

- HTTPS required for all communications between client and server
- TLS 1.2 minimum; TLS 1.3 preferred
- HTTP Strict Transport Security (HSTS) header required in production
- TLS certificate management: handled by deployment platform (Vercel for frontend; Render/Railway/AWS for backend)

### 5.6 Input Validation

- All request inputs validated with Pydantic models before processing
- File uploads: validate MIME type, file extension, and file size before any processing
- URL inputs: validate URL structure before passing to F-01 pipeline
- Phone number inputs: validate format and normalise before lookup
- Free-form text inputs: maximum length enforced; encoding validated
- No input is passed to a database query, shell command, or ML model without validation

### 5.7 Rate Limiting

- Required on all public-facing endpoints (unauthenticated and authenticated)
- Implementation: FastAPI middleware (e.g., slowapi or equivalent)
- Specific thresholds: **TBD — ADR-026** — must be set based on expected usage patterns and threat model review
- Rate limiting applies per IP address and per user account (authenticated endpoints)
- Exceeded rate limit returns HTTP 429 with a Retry-After header

### 5.8 CORS Configuration

- CORS must be configured to permit only explicitly approved origins
- Wildcard origins (`*`) are strictly prohibited in production (CSHAKTI-CONST-001 §8.10)
- Allowed origins: the production Vercel frontend URL + any approved development URLs
- CORS configuration must be externalised as an environment variable — not hard-coded

### 5.9 Additional Security Headers

The following HTTP security headers must be set on all API responses:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Content-Security-Policy`: defined during engineering design
- `Referrer-Policy: strict-origin-when-cross-origin`

### 5.10 PII and Sensitive Data Handling

- Sensitive personal data must not appear in application logs in plaintext
- Passwords must never appear in logs
- API keys and secrets must be managed via environment variables — never committed to source control
- Uploaded files containing sensitive personal information must not be retained beyond their processing purpose


---

## 6. Database Technical Requirements

### 6.1 PostgreSQL Configuration Principles

- Single PostgreSQL instance serves all Phase 1 data (ADR-005)
- pgvector and PostGIS extensions must be enabled at database initialisation
- Separate schemas or databases for different concerns (e.g., application data vs. test data) — exact schema organisation defined in Stage 2 Database Design
- All database credentials managed via environment variables; never hard-coded

### 6.2 Schema Design Principles

- Normalised relational design; avoid data duplication
- Sensitive data columns must use appropriate encryption or hashing
  - Passwords: hashed with Argon2id/bcrypt — never stored as plaintext or reversibly encrypted
  - Uploaded file references: store paths/keys, not file content inline
- Audit trail: security-relevant events (login, 2FA changes, account deletion, scans) must be logged in an audit table
- Soft deletes for user data (mark as deleted, retain for defined period per retention policy, then purge) — exact retention policy defined in engineering design

### 6.3 pgvector Configuration

- Extension: `CREATE EXTENSION IF NOT EXISTS vector;`
- Vector dimensions: determined by embedding model choice (dependent on ADR-013 resolution)
- Index type: IVFFlat or HNSW — selection based on knowledge base size and query latency requirements (determined during engineering design)
- Similarity function: cosine similarity for semantic search

### 6.4 PostGIS Configuration

- Extension: `CREATE EXTENSION IF NOT EXISTS postgis;`
- Location data stored as PostGIS geometry points or polygons (WGS84 coordinate system)
- GiST spatial index on location-tagged threat/alert data for performant geospatial queries
- User location queries use city/region-level bounding boxes — not precise point queries (privacy by design)

### 6.5 Indexing Strategy Principles

- Primary keys on all tables (UUID preferred over sequential integer for security)
- Foreign key constraints enforced at database level
- Indexes on all foreign key columns
- Indexes on columns used in frequent WHERE clauses (e.g., user_id, created_at, status)
- Full index specification defined in Stage 2 Database Design

### 6.6 Migration Strategy

- Versioned database migrations using a migration tool (Alembic for Python — recommended; final selection in engineering design)
- Migrations committed to source control alongside application code
- No manual database schema changes in any environment — all changes via migrations
- Migration rollback capability required for all non-destructive schema changes

### 6.7 Backup Requirements

- Automated daily backups of PostgreSQL data
- Backup retention period: TBD during engineering design
- Backup restoration procedure must be tested before production launch
- Specific backup tooling and schedule: defined in engineering design based on deployment platform

---

## 7. Infrastructure Requirements

### 7.1 Containerisation

- All services (FastAPI backend, Celery workers, Redis) must be containerised using Docker
- Docker Compose configuration for local development environment (brings up all required services)
- Dockerfile for each deployable service
- Environment-specific configuration via environment variables (`.env` files for local; secrets management for production)
- No secrets committed to source control

### 7.2 Local Development Environment

The local development environment must include:
- FastAPI backend (Uvicorn, hot reload)
- Celery workers
- Redis
- PostgreSQL with pgvector and PostGIS extensions
- PaddleOCR (local)
- MLflow tracking server (local or shared)

All started via Docker Compose. Developers do not need to manually install services beyond Docker.

### 7.3 CI/CD Pipeline (GitHub Actions)

**On every pull request:**
- Linting (Python: flake8/ruff; TypeScript/React: ESLint)
- Type checking (Python: mypy; TypeScript: tsc)
- Backend unit tests (Pytest)
- Frontend unit tests (Vitest)
- Build verification (Vite build)

**On merge to main:**
- All PR checks pass first
- Integration tests
- Docker image build verification
- Deployment to staging environment (if configured)

**On release/tag:**
- All checks pass
- Docker image tagged and pushed to registry
- Deployment to production

### 7.4 Deployment Architecture

**Frontend:**
- Platform: Vercel
- Environment variables: configured in Vercel dashboard
- Custom domain with HTTPS: required for production

**Backend:**
- Platform: Render / Railway / AWS — **TBD based on workload, cost, and data residency requirements**
- Deployed as Docker container(s)
- Celery workers: separate container(s) or separate worker dyno/service on the same platform
- Redis: managed Redis instance on the deployment platform or self-hosted in container
- Environment variables: managed via platform secrets management

**Database:**
- PostgreSQL: managed PostgreSQL instance on the deployment platform (e.g., Render PostgreSQL, Railway PostgreSQL, AWS RDS) — specific provider TBD with backend deployment decision
- pgvector and PostGIS extensions must be supported by the managed PostgreSQL provider

**Object Storage:**
- S3-compatible provider: **TBD — ADR-031**
- Access credentials managed via IAM roles or access keys in environment variables

**MLflow:**
- Local: running in Docker Compose
- Shared/production: deployment location TBD during engineering design (may be a separate small service or a managed MLflow instance)

### 7.5 Model Training Infrastructure

- Local development machine: for small-scale experimentation and debugging
- Kaggle GPU (T4/P100): for dataset-scale training of DistilBERT, EfficientNet/Xception
- Google Colab GPU: alternative to Kaggle for training workloads
- No dedicated cloud GPU infrastructure provisioned for Phase 1 (CSHAKTI-CONST-001 §6.16)
- Trained model artefacts stored in MLflow and/or S3-compatible storage (ADR-031)

---

## 8. Performance Requirements

All specific targets are **TBD pending benchmarking**. The categories below define the expected user experience class for each operation type. No latency numbers are invented.

### 8.1 Response Time Categories

| Category | Expected User Experience | Examples | Target |
|---|---|---|---|
| Lightweight synchronous | Near-instantaneous; no perceptible wait | F-09 (password check), F-12 (score read), F-13 (alert query), F-14 (content fetch), auth token validation | TBD — benchmark target: sub-500ms (to be confirmed) |
| Standard ML inference | A few seconds; loading indicator shown | F-01 (URL scan), F-02 (text scan), F-08 (number lookup) | TBD — benchmark target: under 5 seconds (to be confirmed) |
| Async heavy inference | Result not immediate; user notified on completion | F-03 (OCR+NLP), F-05 (profile), F-06 (deepfake), F-07 (mule), F-11 (LLM) | TBD — benchmark after implementation |
| File upload/download | Progress indicator shown; size-dependent | F-10 (encrypt/decrypt), F-03 (screenshot upload), F-06 (video upload) | TBD — file size limits defined in engineering design |

### 8.2 File Size Limits

All file upload size limits are TBD during engineering design based on:
- Storage cost (ADR-031)
- Processing time impact on system load
- User experience (upload time on mobile connections)

### 8.3 Concurrent User Handling

Phase 1 expected user scale: TBD. The modular monolith + Celery architecture must be designed to allow horizontal scaling of the API layer and Celery workers independently.

### 8.4 Celery Task Queue Performance

- Task result polling or notification mechanism (WebSocket or polling — TBD during engineering design) for async operations
- Celery worker concurrency: TBD based on hardware and workload
- Task timeout: defined per task type during engineering design; heavy ML tasks must not block the queue indefinitely

### 8.5 LLM API Performance (F-11)

- Time-to-first-token: dependent on LLM provider (ADR-013 — provider TBD)
- Streaming response preferred for UX (reduces perceived latency)
- LLM API timeout and fallback behaviour: defined in engineering design; the system must handle provider outages gracefully without exposing raw API errors to users

---

## 9. External Integration Requirements

### 9.1 Threat Intelligence Integration

**Requirement:** F-01, F-04, F-08, and F-13 depend on threat intelligence and reputation data (ADR-032 — provider TBD).

**Technical requirements for integration:**
- RESTful API integration with configurable base URL and API key (environment variable)
- Response caching layer (Redis) to reduce repeated lookups for the same indicator — cache TTL TBD
- Fallback behaviour: if threat intelligence API is unavailable, the system falls back to ML model classification only and notifies the user that real-time threat data is unavailable
- Rate limiting awareness: integration must respect the provider's API rate limits
- Data returned from threat intelligence APIs must not be logged with user-identifying information

### 9.2 LLM API Integration (F-11)

**Requirements:**
- Provider adapter pattern: LLM API calls isolated in a provider-specific adapter class
- API key: managed via environment variable — never committed to source control
- Request timeout: TBD — must be set to prevent indefinite blocking
- Retry logic: exponential backoff for transient failures (network errors, rate limit exceeded)
- Fallback: if LLM API is unavailable, assistant returns a graceful degraded response ("The AI assistant is temporarily unavailable. Please try again shortly.") rather than an error
- Streaming support: if the selected provider supports streaming, implement streaming response for improved UX

### 9.3 PaddleOCR Integration (F-03)

- PaddleOCR deployed locally within the backend service (no external API call — privacy by design)
- Initialisation at service startup (not per-request) to avoid cold-start latency
- Input: preprocessed image bytes
- Output: extracted text strings with confidence scores per detected text region

### 9.4 QR Decode Library Integration (F-04)

- Standard Python QR decode library (specific library selected during implementation — e.g., pyzbar)
- Runs locally within the backend service
- Input: image bytes
- Output: decoded content string + content type

---

## 10. Testing Requirements

### 10.1 Backend Testing (Pytest)

- Unit tests for all business logic modules (URL feature engineering, risk scoring engine, text preprocessing, etc.)
- Integration tests for API endpoints (using FastAPI TestClient)
- Database integration tests (using a test database instance — not the production database)
- Celery task tests (using Celery eager execution mode in tests)
- Test coverage threshold: TBD — a minimum threshold must be set and enforced in CI/CD
- Tests must run without external dependencies (LLM API, threat intelligence API) — these are mocked in tests

### 10.2 Frontend Testing (Vitest + React Testing Library)

- Unit tests for utility functions and hooks
- Component tests for all user-facing components (especially risk verdict display, disclaimer text)
- Tests verify that disclaimer text is always present in AI/ML output components
- Tests verify that Research/Experimental label is present on F-06 and F-07 feature entry points

### 10.3 End-to-End Testing (Playwright)

Critical user flows covered by Playwright tests:
- Registration and email verification flow
- Login flow (with and without 2FA)
- F-01 URL scan: submit URL, receive verdict with explanation
- F-02 text scan: submit text, receive verdict with explanation
- F-09 password check: submit password, receive verdict with recommendations
- F-10 file encryption: upload file, receive encrypted download
- F-14 Cyber Safety Hub: access tips and quiz

### 10.4 API Contract Testing (Postman or Bruno)

- API contract tests for all public and authenticated endpoints
- Covers: correct HTTP status codes, response schema validation, error response format
- Tests run against a local development environment

### 10.5 ML Model Validation Requirements

- A held-out test set must be reserved for final model evaluation — it must not be used during training or hyperparameter tuning
- Test set must be representative of real-world distribution (not just random split of training data)
- No data leakage between train/validation/test sets
- For all model-bearing features (F-01, F-02, F-05, F-06, F-07): validation report produced with precision, recall, F1, ROC-AUC, PR-AUC, FPR, FNR on the held-out test set before any production deployment decision
- Baseline model comparison required (F-01: vs. logistic regression; F-02: vs. TF-IDF + LR)
- MLflow experiments track all training runs, hyperparameters, and metrics

### 10.6 Security Testing Requirements

- Input validation testing: test boundary conditions, invalid inputs, oversized inputs for all endpoints
- Authentication bypass testing: verify all protected endpoints require valid JWT
- Authorisation testing: verify RBAC enforcement — a `user`-role token cannot access `admin`-role endpoints
- Rate limiting testing: verify rate limits are enforced
- Dependency scanning: automated dependency vulnerability scanning in CI/CD pipeline (e.g., pip-audit for Python, npm audit for Node.js)

---

*End of CyberShakti Technical Requirements Document — CSHAKTI-TRD-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
