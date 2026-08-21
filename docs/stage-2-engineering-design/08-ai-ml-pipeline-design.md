# CyberShakti — AI/ML Pipeline Design

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-ML-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-TRD-001, CSHAKTI-SRS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 §3 (AI/ML Principles) — no performance metrics are invented; all targets marked TBD |

---

## Table of Contents

1. [AI/ML Overview and Governance](#1-aiml-overview-and-governance)
2. [F-01 — Phishing URL Classification Pipeline](#2-f-01--phishing-url-classification-pipeline)
3. [F-02 — Message & Email Scam Detection Pipeline](#3-f-02--message--email-scam-detection-pipeline)
4. [F-03 — Screenshot Scam Scanner Pipeline](#4-f-03--screenshot-scam-scanner-pipeline)
5. [F-04 — QR Code Scam Scanner Pipeline](#5-f-04--qr-code-scam-scanner-pipeline)
6. [F-05 — Fake Profile Risk Assessment Pipeline](#6-f-05--fake-profile-risk-assessment-pipeline)
7. [F-06 — Deepfake Detection Pipeline (Research/Experimental)](#7-f-06--deepfake-detection-pipeline-researchexperimental)
8. [F-07 — Mule Account Detection Pipeline (Research/Experimental)](#8-f-07--mule-account-detection-pipeline-researchexperimental)
9. [F-11 — AI Cybersecurity Assistant RAG Pipeline](#9-f-11--ai-cybersecurity-assistant-rag-pipeline)
10. [F-12 — Cyber Risk Score Engine](#10-f-12--cyber-risk-score-engine)
11. [Cross-Pipeline: Explanation Engine](#11-cross-pipeline-explanation-engine)
12. [Model Versioning and MLflow](#12-model-versioning-and-mlflow)
13. [Implementation Status](#13-implementation-status)

---

## 1. AI/ML Overview and Governance

### 1.1 Governing Principles

All AI/ML work in CyberShakti is governed by CSHAKTI-CONST-001 §3. Key constraints:

- **No invented metrics**: All performance targets (precision, recall, F1, ROC-AUC, FPR, FNR) are **TBD** until empirical evaluation on representative datasets is complete (CSHAKTI-CONST-001 §3.4)
- **No unsupported claims**: The system must never claim 100% detection, perfect accuracy, or guaranteed protection (CSHAKTI-CONST-001 §3.2)
- **Explainability required**: Every AI/ML output must include a plain-language explanation (CSHAKTI-CONST-001 §3.3)
- **Baseline first**: Baseline models must be established and documented before advanced variants are evaluated
- **Dataset integrity**: Datasets must be from reputable sources; licensing verified; limitations documented

### 1.2 Approach Selection Rationale

| Feature | Approach | Rationale |
|---|---|---|
| F-01 Phishing URL | XGBoost on engineered features + TI lookup | Structured tabular problem; gradient boosting well-established |
| F-02 Scam text | DistilBERT fine-tuned + classical baseline | Semantic understanding required; DistilBERT practical for inference |
| F-03 Screenshot | PaddleOCR → F-02 NLP pipeline | Composable reuse of F-02; no separate model needed |
| F-04 QR Code | Decode → route to F-01 | URL is the threat; no separate model needed (ADR-023) |
| F-05 Fake profile | XGBoost/LightGBM on observable signals | Structured signal set; gradient boosting appropriate |
| F-06 Deepfake | EfficientNet / Xception CNN | Computer vision classification; state-of-art CNN architectures |
| F-07 Mule account | XGBoost + NetworkX graph features | Graph-aware tabular classification; GNN deferred to future |
| F-11 AI assistant | API-based LLM + RAG (pgvector) | Open-ended NLP; LLM training not feasible; RAG grounds responses |
| F-12 Risk score | Explainable weighted engine | Fully explainable by design; no training data available in Phase 1 |

### 1.3 Implementation Status Legend

All pipelines in this document are **PLANNED** unless explicitly marked **IMPLEMENTED**. No implementation has been verified in the repository.

---

## 2. F-01 — Phishing URL Classification Pipeline

**Feature:** F-01 Phishing Link Scanning | **Tier:** Core MVP | **ADR:** ADR-008 (Provisional)
**Status:** PLANNED

### 2.1 Problem Definition

Binary classification: given a URL, determine whether it is a phishing attempt or legitimate. The system must be robust to obfuscation tactics common in Indian phishing campaigns (subdomain abuse, homoglyph domains, URL shorteners, HTTPS on phishing sites).

### 2.2 Input

- URL string (submitted by user or decoded from QR code via F-04)
- Maximum URL length: 2048 characters

### 2.3 Data Preprocessing

1. Normalise URL (decode percent-encoding, lowercase domain)
2. Parse into components: scheme, domain, subdomain, path, query string, fragment
3. Resolve URL shorteners: **Phase 1 does not unshorten URLs** (privacy and latency concern); this is a documented limitation
4. Validate URL structure — return validation error for non-URLs

### 2.4 Feature Engineering

**Lexical features (from URL string):**

| Feature | Description |
|---|---|
| `url_length` | Total URL length in characters |
| `domain_length` | Domain portion length |
| `path_length` | Path length |
| `num_dots` | Count of dots in full URL |
| `num_hyphens` | Count of hyphens in domain |
| `num_underscores` | Count of underscores |
| `num_at_signs` | Count of @ signs (phishing indicator) |
| `num_question_marks` | Count of ? characters |
| `num_slashes` | Count of / characters |
| `num_digits` | Count of digits in domain |
| `digit_to_letter_ratio` | Ratio of digits to letters in domain |
| `has_ip_address` | Boolean: domain is an IP address (phishing indicator) |
| `uses_https` | Boolean: scheme is HTTPS |
| `has_port_in_url` | Boolean: non-standard port specified |
| `url_entropy` | Shannon entropy of URL string |
| `subdomain_count` | Number of subdomain levels |
| `is_shortened_url` | Boolean: domain matches known URL shortener list |

**Domain-based features:**

| Feature | Description |
|---|---|
| `tld` | Top-level domain (one-hot encoded for common TLDs) |
| `is_suspicious_tld` | Boolean: TLD associated with abuse (.xyz, .top, .tk, etc.) |
| `domain_age_days` | Days since domain registration (WHOIS — may be null) |
| `is_brand_lookalike` | Boolean: domain contains known Indian bank/brand name in subdomain or path |

**Threat intelligence features:**

| Feature | Description |
|---|---|
| `on_phishing_blocklist` | Boolean: domain/URL in PhishTank or URLhaus |
| `google_safe_browsing_hit` | Boolean: URL flagged by Google Safe Browsing API (if integrated — ADR-032) |

### 2.5 Model Selection

**Baseline (mandatory first):** Logistic Regression on TF-IDF character n-grams of URL

**Primary candidate:** XGBoost on engineered features (ADR-008)

**Comparison candidate:** LightGBM on same feature set

Final model selection depends on empirical performance comparison on a held-out test set. All performance metrics (precision, recall, F1, ROC-AUC, FPR, FNR) are **TBD**.

### 2.6 Training Datasets

| Dataset | Source | Notes |
|---|---|---|
| PhishTank | phishtank.com | Community-contributed phishing URL database; requires API key; licensing: open for non-commercial / requires verification |
| URLhaus | abuse.ch | Malicious URL database; actively maintained; licensing: open |
| ISCX-URL-2016 | University of New Brunswick | Balanced legitimate/phishing URL dataset; licensing: research use — verify before use |
| Legitimate URLs | Common Crawl / Alexa/Tranco top-1M | Random sample of legitimate URLs for negative class |

**Dataset limitations:**
- PhishTank and URLhaus represent globally distributed phishing; India-specific coverage is unknown
- Legitimate URL samples may not represent the full range of Indian web properties
- Temporal drift: phishing URLs change rapidly; models must be periodically retrained

### 2.7 Validation Strategy

- Stratified train/validation/test split (80/10/10)
- No data leakage: test set URLs are temporally separated from training set where possible
- Metrics: Precision, Recall, F1-score, ROC-AUC, PR-AUC, False Positive Rate (FPR), False Negative Rate (FNR)
- **All numerical targets: TBD**

### 2.8 Risk Aggregation

Final verdict combines:
1. Threat intelligence match (highest priority — TI hit → High Risk or Critical immediately)
2. ML classifier probability score
3. Rule-based signals (IP address URL → always Moderate Risk minimum)

### 2.9 False Positive and False Negative Handling

| Case | Risk | Mitigation |
|---|---|---|
| False positive (legitimate URL flagged) | User fails to visit legitimate site | Confidence indicator shows uncertainty; explanation references specific signals |
| False negative (phishing URL missed) | User may visit phishing site | Layered defence: TI lookup + ML + rules; not single point of failure |

### 2.10 Explainability

SHAP values (SHapley Additive exPlanations) are computed for each XGBoost prediction to identify the top contributing features. These are translated into plain-language explanation text by the Explanation Engine (Section 11).

### 2.11 Model Monitoring

- Track: FPR and FNR on a time-stratified evaluation set monthly
- Alert: Significant drift in feature distributions (new phishing tactics)
- Retrain trigger: Model performance degrades beyond threshold (threshold TBD after baseline established)

---

## 3. F-02 — Message & Email Scam Detection Pipeline

**Feature:** F-02 Message & Email Scam Detection | **Tier:** Core MVP | **ADR:** ADR-009 (Provisional)
**Status:** PLANNED

### 3.1 Problem Definition

Multi-class and binary classification: given a text message or email body, determine whether it is a scam and, if so, classify the scam type (KYC scam, OTP theft, lottery scam, job scam, investment scam, etc.).

### 3.2 Input

- Free-form text string (message/email body)
- Maximum length: 5000 characters (truncated at model max tokens for transformer input)

### 3.3 Data Preprocessing

1. Language detection (langdetect or fasttext-based)
2. Unicode normalisation (NFKC)
3. Remove excessive whitespace and control characters
4. Tokenisation via Hugging Face Tokenizers (DistilBERT tokeniser)
5. Truncate to model maximum token length (512 tokens for DistilBERT)

### 3.4 Feature Engineering

For DistilBERT: no manual feature engineering — the model learns representations from subword tokens.

For classical baseline (TF-IDF):
- Character n-grams (3–5 grams)
- Word n-grams (1–2 grams)
- Scam-related keyword presence features (handcrafted: OTP, KYC, prize, lottery, urgent, verify, account blocked, etc.)
- Urgency language indicators
- URL presence and count

### 3.5 Model Selection

**Mandatory baseline:** TF-IDF (char+word n-grams) + Logistic Regression

**Primary candidate:** `distilbert-base-uncased` fine-tuned (or `distilbert-base-multilingual-cased` — to be evaluated for multilingual capability)

**Comparison:** `distilbert-base-uncased` vs. TF-IDF+LR on same evaluation set

**Multilingual note:** Phase 1 is English-first. Hindi-language scam message capability is a known limitation. If `distilbert-base-multilingual-cased` shows acceptable performance on Hindi samples during evaluation, it may be preferred. This decision is empirical.

### 3.6 Training Datasets

| Dataset | Notes |
|---|---|
| SMS Spam Collection Dataset (UCI) | English SMS spam/ham; baseline training |
| Enron email dataset (spam subset) | English email spam; research licence |
| India-specific scam message samples | **Collection required**: curated from public reports, CERT-In advisories, social media scam reports; no publicly available labelled dataset known at time of writing |
| Synthetic augmentation | Generated from known scam templates for rare categories |

**Dataset limitation (critical):** No large-scale, India-specific, labelled scam message dataset is publicly available at time of writing. This is the primary constraint on F-02 model quality. Data collection and curation is a prerequisite for quality model training.

### 3.7 Validation Strategy

- Stratified split by class label and, where possible, by time
- Evaluation metrics: Precision, Recall, F1-score (per class and macro-averaged), ROC-AUC (binary), Confusion Matrix
- False positive analysis: What types of legitimate messages are most commonly misclassified?
- **All numerical targets: TBD**

### 3.8 Inference Pipeline (Production)

```
Text Input
  ↓
Language Detection
  ↓
Preprocessing (normalise, truncate)
  ↓
DistilBERT Tokeniser
  ↓
DistilBERT Classifier (fine-tuned)
  ↓
Scam Probability Score [0, 1]
  ↓
Scam Category Classification (multi-class head or separate classifier)
  ↓
Risk Level Assignment
  ↓
Explanation Generation (LIME or attention-based for transformers)
  ↓
Response
```

### 3.9 Model Loading

DistilBERT model is loaded into Celery worker memory at worker startup — not per-request. This avoids the significant latency cost of loading a 260MB model for each inference call.

---

## 4. F-03 — Screenshot Scam Scanner Pipeline

**Feature:** F-03 Screenshot Scam Scanner | **Tier:** Core MVP | **ADR:** ADR-022 (Provisional)
**Status:** PLANNED

### 4.1 Problem Definition

Extract text from a user-uploaded screenshot and classify it using the F-02 scam text pipeline.

### 4.2 Pipeline

```
Screenshot Upload (JPEG/PNG)
  ↓
File Type and Size Validation
  ↓
S3 Upload (temp storage)
  ↓
[Celery Worker]
  ↓
Image Preprocessing (OpenCV)
  - Resize if necessary
  - Contrast enhancement for low-quality screenshots
  - Convert to RGB
  ↓
PaddleOCR Text Extraction
  - Multi-language support (English + Hindi attempted)
  - Bounding box extraction
  ↓
OCR Quality Assessment
  - Confidence score aggregation
  - Minimum confidence threshold check
  ↓
Text Extraction Result
  ↓ (if text found)
F-02 Scam Text Classification Pipeline
  ↓
Verdict + Extracted Text + OCR Quality
  ↓
S3 Object Deletion
  ↓
Result stored in DB
```

### 4.3 OCR Quality Indicators

| Quality Level | Meaning |
|---|---|
| `good` | High confidence OCR; text is likely accurate |
| `fair` | Moderate confidence; some characters may be misread |
| `low` | Low confidence; text may be significantly garbled |
| `failed` | OCR could not extract any text |

### 4.4 Limitations

- OCR accuracy is an upper bound on overall F-03 accuracy — if OCR mis-reads scam text, the downstream classifier may not detect the scam
- Low-quality screenshots (blurry, very small text, heavy compression) will produce poor OCR quality
- OCR quality must be communicated to the user via the `ocr_quality` field

### 4.5 PaddleOCR Selection (ADR-022 — Provisional)

PaddleOCR is selected as the OCR baseline. If empirical testing on a representative set of Indian screenshot samples shows insufficient accuracy, alternatives (Tesseract, cloud-based OCR with appropriate privacy controls) must be evaluated with a new ADR.

---

## 5. F-04 — QR Code Scam Scanner Pipeline

**Feature:** F-04 QR Code Scam Scanner | **Tier:** Core MVP | **ADR:** ADR-023 (Accepted)
**Status:** PLANNED

### 5.1 Pipeline

```
QR Code Image Upload
  ↓
File Validation
  ↓
QR Code Decode (pyzbar or OpenCV QR reader)
  ↓
Content Type Classification
  - URL → route to F-01 pipeline
  - vCard → identify and return non-risk response
  - WiFi credentials → identify and return non-risk response
  - Plain text → return decoded content; no risk verdict
  - Other → identify and return non-risk response
  ↓ (URL path only)
F-01 Phishing URL Classification Pipeline
  ↓
Verdict
```

### 5.2 Design Note (ADR-023)

F-04 has no independent ML model. The threat in QR code scams is universally the embedded URL. Routing to the existing F-01 pipeline avoids code duplication and ensures consistent URL analysis quality.

---

## 6. F-05 — Fake Profile Risk Assessment Pipeline

**Feature:** F-05 Fake Profile Verification | **Tier:** Advanced MVP
**Status:** PLANNED

### 6.1 Problem Definition

Given a set of observable signals about a social media profile, assess the probability that the profile is fake or operated by a fraudster. This is **not** identity verification — CyberShakti cannot confirm who someone is (CSHAKTI-CONST-001 §3.2).

### 6.2 Input Signals (Phase 1 Observable Set)

The Phase 1 signal set is controlled and explicit. Signals are observable without accessing private profile data or performing identity checks:

| Signal | Type | Description |
|---|---|---|
| `account_age_category` | Categorical | Estimated account age bracket |
| `follower_count_range` | Categorical | Approximate follower count range |
| `following_to_follower_ratio_high` | Boolean | Following far more accounts than followers |
| `has_profile_photo` | Boolean | Profile photo present |
| `profile_photo_appears_generic` | Boolean | Photo looks like stock photo or AI-generated |
| `bio_present` | Boolean | Profile bio is populated |
| `posts_count_range` | Categorical | Approximate number of posts |
| `sent_unsolicited_money_request` | Boolean | Has requested money without prior relationship |
| `claims_celebrity_or_official` | Boolean | Claims to be a celebrity, government official, or authority |
| `platform` | Categorical | Social media platform |
| `contacted_via_dm_unsolicited` | Boolean | Contacted user without prior relationship |
| `promotes_investment_or_scheme` | Boolean | Actively promoting investment or get-rich scheme |

### 6.3 Model Selection

**Baseline:** Logistic Regression on one-hot/ordinal-encoded signal features

**Primary candidate:** XGBoost or LightGBM on encoded features

**Training note:** No publicly available labelled fake profile dataset that maps directly to this signal set exists. Training data must be collected from:
- Publicly reported scam profile characteristics
- Academic datasets on fake social media accounts
- Synthetic data generation based on documented fake profile indicators

### 6.4 Mandatory Disclaimer

Every F-05 response must include: *"CyberShakti does not verify identities. This assessment evaluates observable risk signals only and does not confirm whether a profile is genuinely fake or who the account belongs to. A low-risk result does not mean the profile is genuine."*

---

## 7. F-06 — Deepfake Detection Pipeline (Research/Experimental)

**Feature:** F-06 Deepfake Detection | **Tier:** Research/Experimental | **ADR:** ADR-010 (Provisional)
**Status:** PLANNED — Research Phase

### 7.1 Classification

**RESEARCH/EXPERIMENTAL.** This pipeline is part of Phase 1 research scope. It is NOT a production-grade, guaranteed capability. All outputs carry mandatory experimental disclaimers (FR-036). Performance metrics are TBD.

### 7.2 Problem Definition

Binary classification: given an image or short video clip, assess whether it contains indicators of AI-generated synthetic media (deepfake). Focus: human face deepfakes (face-swapped or fully synthesised faces).

### 7.3 Pipeline

```
Media Upload (JPEG, PNG, or MP4 short clip)
  ↓
File Validation (type, size, duration for video)
  ↓
S3 Upload (temp)
  ↓
[Celery Worker]
  ↓
Frame Extraction (for video: sample N frames uniformly)
  ↓
Face Detection (OpenCV Haar Cascade or DLib face detector)
  ↓ (if face detected)
Face Region Cropping and Preprocessing
  - Align face
  - Resize to model input dimension
  - Normalise pixel values
  ↓
CNN Inference (EfficientNet-B4 or Xception — to be selected empirically)
  ↓
Deepfake Probability Score [0, 1]
  ↓ (for video: aggregate scores across frames)
Frame-level aggregation (mean / max strategy — TBD)
  ↓
Risk Level Assignment
  ↓
Experimental Disclaimer + Explanation
  ↓
S3 Object Deletion
```

### 7.4 Candidate Models (ADR-010)

| Model | Architecture | Rationale |
|---|---|---|
| EfficientNet-B4 | Compound-scaled CNN | Strong performance in deepfake detection literature; efficient inference |
| Xception | Depthwise separable convolutions | Frequently cited in deepfake detection research |

Both models are evaluated on the same datasets. Final selection is empirical. Both are implemented via PyTorch (TorchVision or timm library).

### 7.5 Training Datasets (Subject to Licensing Verification)

| Dataset | Content | License Status |
|---|---|---|
| FaceForensics++ | Face manipulation videos (DeepFakes, Face2Face, FaceSwap, NeuralTextures) | Academic use; requires request approval |
| Celeb-DF v2 | Celebrity deepfake videos, high quality | Research use; verify current terms |
| DFDC (DeepFake Detection Challenge) | Kaggle competition dataset | Verify current terms |

**Critical limitation:** These datasets represent Western faces predominantly. Performance on Indian faces has not been empirically validated. This is a documented generalisation limitation that must be communicated to users.

### 7.6 Known Limitations

- Generalisation to unseen deepfake generation methods is poor (deepfake detectors are often brittle to new GAN architectures)
- Performance on Indian faces in Indian lighting conditions is unvalidated
- Video deepfakes where manipulation is audio-only (voice cloning) are not detected by this pipeline
- Low-quality compressed video may reduce detection accuracy
- All of these limitations must be communicated to users in the experimental disclaimer

---

## 8. F-07 — Mule Account Detection Pipeline (Research/Experimental)

**Feature:** F-07 Mule Account Detection | **Tier:** Research/Experimental | **ADR:** ADR-011 (Provisional), ADR-024 (Accepted)
**Status:** PLANNED — Research Phase

### 8.1 Classification

**RESEARCH/EXPERIMENTAL.** Not production-grade. Three mandatory disclaimers required in every response (FR-042):
1. Research/Experimental status
2. Dataset domain mismatch (Elliptic dataset represents cryptocurrency, not Indian bank accounts)
3. General statistical indicator notice

### 8.2 Problem Definition

Given observable account/transaction signals, assess whether an account exhibits patterns associated with money mule activity.

### 8.3 Pipeline

```
Account Signal Input
  ↓
Signal Validation (minimum signal threshold)
  ↓
[Celery Worker]
  ↓
Tabular Feature Construction from signals
  ↓
Graph Feature Engineering (NetworkX)
  - If transaction network graph is available:
    Compute degree centrality, clustering coefficient,
    betweenness centrality, community membership
  - If no graph data: graph features are null / zero
  ↓
XGBoost Classifier (tabular + graph features)
  ↓
Mule Probability Score [0, 1]
  ↓
Risk Level Assignment
  ↓
All Three Mandatory Disclaimers
  ↓
Plain-language explanation (signal contributions)
```

### 8.4 Training Dataset and Limitation (ADR-024)

The Elliptic dataset (cryptocurrency transaction network) and Elliptic2 dataset are the primary available labelled datasets for money laundering pattern detection. These represent Bitcoin/cryptocurrency networks — **not Indian bank account networks**.

**This domain mismatch is critical and must be prominently documented.** A model trained on Elliptic data does not directly validate for Indian bank mule detection. Phase 1 establishes a research pipeline; real-world validation requires domain-specific data that is not publicly available.

### 8.5 Future Path (Not Phase 1)

PyTorch Geometric Graph Neural Networks (GNNs) operating on a properly constructed account transaction graph represent the advanced path for future phases (ADR-011). This requires:
- Access to real transaction graph data
- A properly constructed account-node/transaction-edge graph
- GNN training infrastructure

---

## 9. F-11 — AI Cybersecurity Assistant RAG Pipeline

**Feature:** F-11 AI Cybersecurity Assistant | **Tier:** Core MVP | **ADR:** ADR-013 (Open), ADR-006 (Accepted)
**Status:** PLANNED — Blocked by ADR-013 (LLM provider unresolved)

### 9.1 Architecture

```
User Query (natural language)
  ↓
Query Preprocessing
  - Length validation
  - Domain check (reject clearly out-of-scope)
  ↓
Query Embedding
  (via embedding model — dimension must match knowledge base embeddings)
  ↓
pgvector Similarity Search
  (knowledge_base_chunks table, cosine similarity)
  ↓
Top-K Retrieved Chunks (K TBD — typically 3–5)
  ↓
Prompt Assembly
  - System prompt (cybersecurity assistant persona + constraints)
  - Retrieved context chunks
  - User query
  ↓
LLM API Call (provider TBD — ADR-013)
  ↓
Response Filtering
  - Remove hallucinated threat intelligence claims
  - Ensure out-of-scope handling
  - Ensure legal/financial/medical advice declination
  ↓
Response + AI Disclaimer + Source Attribution
```

### 9.2 Knowledge Base Construction

The CyberShakti knowledge base is a curated collection of cybersecurity content:

| Content Type | Sources | Notes |
|---|---|---|
| Threat advisory documents | CERT-In advisories, RBI circulars, NPCI guidance | Publicly available; attribution required |
| Scam awareness content | Cyberdost (I4C/MHA), consumer protection resources | Publicly available Indian government sources |
| CyberShakti internal content | F-14 Cyber Safety Hub articles | Internally authored |
| General cybersecurity guidance | Authoritative sources (NIST, OWASP where applicable) | Curated for Indian consumer context |

**Knowledge base process:**
1. Document ingestion (PDF, HTML, markdown)
2. Document chunking (chunk size and overlap TBD — typically 200–500 tokens with 50-token overlap)
3. Embedding generation (batch processing)
4. Storage in `knowledge_base_chunks` table with pgvector embeddings

### 9.3 Prompt Design Principles

The system prompt for F-11 must enforce:
- Cybersecurity domain constraint
- Decline to provide legal, financial, or medical advice
- Acknowledge knowledge gaps rather than fabricating
- Always attribute to knowledge base sources where possible
- Never claim guaranteed protection or fabricate threat statistics
- Always include AI disclaimer in response

Specific prompt content is implementation-level and not documented here.

### 9.4 Hallucination Mitigation

| Risk | Mitigation |
|---|---|
| LLM fabricates threat statistics | System prompt instructs to cite only knowledge base content; response filtering checks for unsupported statistical claims |
| LLM fabricates specific threat actors or incidents | Same constraint |
| LLM provides dangerous advice (e.g., "share OTP to verify") | Constrained system prompt; domain guardrails |
| LLM answers out-of-scope questions | Out-of-scope detection in query preprocessing; system prompt reinforcement |

### 9.5 Dependency

F-11 **cannot be deployed** until ADR-013 (LLM provider) is resolved (FR-071).

---

## 10. F-12 — Cyber Risk Score Engine

**Feature:** F-12 Cyber Risk Score | **Tier:** Core MVP | **ADR:** ADR-012, ADR-020 (Accepted)
**Status:** PLANNED

### 10.1 Design

F-12 uses an **explainable weighted risk engine** — not a machine learning model (ADR-012). This is a deliberate design decision enabling full explainability without requiring training data.

### 10.2 Phase 1 Controlled Signal Set

The following signals and only these signals contribute to the Phase 1 Cyber Risk Score. This set is locked (ADR-020). Additions require a recorded change decision.

**In-app activity signals:**

| Signal | Source | Direction | Description |
|---|---|---|---|
| `recent_high_risk_detections` | scan_results | Negative | High Risk/Critical verdicts in past 30 days |
| `scans_performed` | scan_results | Positive | User actively uses scanning features |
| `password_check_performed` | scan_results | Positive | User has checked password strength |
| `password_check_verdict` | scan_results | Negative/Positive | Weak/strong password detected |
| `file_encryption_used` | scan_results | Positive | User has used secure file encryption |
| `quiz_completed` | learn_prevent | Positive | User completed the cybersecurity quiz |

**User-reported questionnaire signals:**

| Signal | Question | Direction |
|---|---|---|
| `uses_2fa_on_bank_apps` | Do you have two-factor authentication enabled on your banking apps? | Positive if yes |
| `reuses_passwords` | Do you reuse the same password across multiple accounts? | Negative if yes |
| `shares_otp_with_others` | Have you ever shared an OTP with someone who called you? | Negative if yes |
| `locks_phone` | Do you use a PIN/password/biometric to lock your phone? | Positive if yes |

### 10.3 Score Calculation

```
score = 50 (baseline for new users)
For each active signal:
  score += signal_weight × contribution_value
score = clamp(score, 0, 100)
```

Individual signal weights are configured values — not hardcoded. Weights must be reviewed and adjusted based on observed score distributions after Phase 1 launch.

### 10.4 Score Bands

| Band | Score Range | Label |
|---|---|---|
| Very High Risk | 0–20 | Very High Risk |
| High Risk | 21–40 | High Risk |
| Moderate Risk | 41–60 | Moderate Risk |
| Low Risk | 61–80 | Low Risk |
| Well Protected | 81–100 | Well Protected |

Score band boundaries are configurable and subject to adjustment.

### 10.5 Explainability

Every score response includes `signal_breakdown`: a list of each contributing signal, its label, its direction (positive/negative), and a plain-language description. No score is presented without this breakdown.

---

## 11. Cross-Pipeline: Explanation Engine

All AI/ML pipelines use a shared **Explanation Engine** in `app/shared/explanation_engine.py`.

### 11.1 Responsibilities

- Map raw model outputs (SHAP values, feature importance, attention scores) to user-facing explanation text
- Select and rank the most relevant signals for explanation (top 3–5 contributing factors)
- Generate plain-language text accessible to non-technical Indian consumers
- Append the appropriate disclaimer for each feature type
- Add language-limitation notice when non-English input is detected (F-02, F-03)

### 11.2 Explanation Templates

Explanation text is template-based, not LLM-generated (to avoid hallucination risk in the explanation itself). Templates are parameterised by:
- Detected scam category
- Top contributing features
- Confidence level
- Verdict source (TI vs. ML vs. combined)

Example template instantiation for F-01:

> *"This URL shows [N] indicators associated with phishing sites. The domain was registered recently and contains a known Indian bank's name as a subdomain — a common pattern in credential-harvesting attacks. The URL also appears on a known phishing database."*

---

## 12. Model Versioning and MLflow

All models are versioned and tracked using MLflow.

### 12.1 MLflow Tracking

For every training run:
- Dataset version and split details
- All hyperparameters
- All evaluation metrics (on validation and test sets)
- Model artefact (saved model file)
- Training environment (Python version, library versions)

### 12.2 Model Registry

MLflow Model Registry tracks model lifecycle stages:
- `Staging` — candidate model, not yet deployed
- `Production` — currently serving model
- `Archived` — retired model versions retained for audit

### 12.3 Model Artefact Storage

MLflow model artefacts are stored in S3-compatible object storage (ADR-031). The storage path follows MLflow's default artefact structure.

---

## 13. Implementation Status

| Feature | Pipeline Status | Model Status | Dataset Status |
|---|---|---|---|
| F-01 Phishing URL | PLANNED | PLANNED | Datasets identified; licensing TBD |
| F-02 Scam Text | PLANNED | PLANNED | India-specific data collection required |
| F-03 Screenshot OCR | PLANNED | N/A (PaddleOCR) | N/A |
| F-04 QR Code | PLANNED | N/A (decode + F-01) | N/A |
| F-05 Fake Profile | PLANNED | PLANNED | Data collection required |
| F-06 Deepfake | PLANNED (Research) | PLANNED (Research) | Licensing verification required |
| F-07 Mule Account | PLANNED (Research) | PLANNED (Research) | Elliptic available; domain mismatch documented |
| F-11 AI Assistant | PLANNED (Blocked — ADR-013) | N/A (API-based LLM) | Knowledge base curation required |
| F-12 Risk Score | PLANNED | N/A (Weighted engine) | N/A |

---

*End of CyberShakti AI/ML Pipeline Design — CSHAKTI-ML-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
