# CyberShakti V3 — Phase 5A Model Conformance Audit

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-AUDIT-05A |
| **Version** | 1.0.0 |
| **Status** | Audit Completed |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-ML-001, CSHAKTI-CONST-001 §3, CSHAKTI-ADR-LOG-001 |
| **Governed By** | CSHAKTI-CONST-001 — Independent Model Conformance Verification |

---

## Executive Result

**Overall Status**: **PARTIALLY CONFORMANT**

An independent model conformance audit was conducted by inspecting the source code, training scripts in `ml/pipelines/`, serialized models in `ml/models/`, API endpoints, Celery workers, and the governance documentation (`docs/00-decisions.md` and `docs/stage-2-engineering-design/08-ai-ml-pipeline-design.md`).

- **Fully Conformant**: F-05 (Fake Profile), F-07 (Mule Account), F-12 (Cyber Risk Score).
- **Partially Conformant**: F-01 (Phishing URL), F-02 (Scam Text), F-03 (Screenshot OCR).
- **Non-Conformant**: F-06 (Deepfake Detection — uses RandomForest tabular features instead of CNN architectures EfficientNet-B4 / Xception).
- **Blocked**: F-11 (AI Assistant — correctly blocked per Step 8 rule due to OPEN decision ADR-013).

---

## Model Conformance Matrix

| Feature | Approved Model | Actual Model | Dataset | Conformance | Reason |
|---|---|---|---|---|---|
| **F-01** Phishing URL | XGBoost / LR Baseline (ADR-008) | `GradientBoostingClassifier` | Synthetic Lexical (1,000 URLs) | **PARTIALLY CONFORMANT** | Scikit-Learn `GradientBoosting` used as substitute for XGBoost library; synthetic dataset used. |
| **F-02** Scam Text | DistilBERT / TF-IDF+LR (ADR-009) | `TF-IDF + LogisticRegression` | Synthetic Text Corpus (500 SMS) | **PARTIALLY CONFORMANT** | Matches approved mandatory baseline in CSHAKTI-ML-001 §3.5; full DistilBERT fine-tuning deferred. |
| **F-03** Screenshot OCR | PaddleOCR → F-02 NLP (ADR-022) | OCR Text Extractor → F-02 NLP | Screenshot Image Content | **PARTIALLY CONFORMANT** | Pipeline composes F-02 NLP classifier correctly; PaddleOCR relies on text extraction fallback. |
| **F-05** Fake Profile | XGBoost / LightGBM (CSHAKTI-ML-001) | `GradientBoostingClassifier` | 10 Controlled Signal Set | **CONFORMANT** | Matches primary model family and exact controlled signal set in CSHAKTI-ML-001 §6.2. |
| **F-06** Deepfake | EfficientNet-B4 / Xception (ADR-010) | `RandomForestClassifier` | Synthetic Frequency Features | **NON-CONFORMANT** | Uses tabular `RandomForest` on frequency features instead of CNN architectures EfficientNet/Xception. |
| **F-07** Mule Account | XGBoost + NetworkX (ADR-011/024) | `GradientBoosting` + NetworkX | NetworkX Graph + Txn Velocity | **CONFORMANT** | Matches ADR-011 & ADR-024; incorporates NetworkX degree/betweenness/clustering graph features. |
| **F-11** AI Assistant | pgvector RAG + LLM (ADR-013) | RAG Search Foundation | Knowledge Base Documents | **BLOCKED** | ADR-013 is OPEN. Endpoint correctly returns HTTP 501 / BLOCKED per Step 8 rule. |
| **F-12** Risk Score | Weighted Signal Engine (ADR-012/020) | Weighted Signal Engine | In-App Activity + Questionnaire | **CONFORMANT** | Matches exact controlled signals, weights, score clamping [0, 100], and score bands in ADR-020. |

---

## Detailed Feature Evaluation

### F-01 Phishing Link Scanning
- **Approved**: XGBoost on 17 engineered features + TF-IDF Logistic Regression baseline (ADR-008, CSHAKTI-ML-001 §2.5).
- **Actual**: `ml/pipelines/train_f01_phishing_url.py` extracts all 17 lexical and domain features (`url_length`, `domain_length`, `path_length`, `num_dots`, `num_hyphens`, `num_underscores`, `num_at_signs`, `num_question_marks`, `num_slashes`, `num_digits`, `digit_to_letter_ratio`, `has_ip_address`, `uses_https`, `has_port_in_url`, `url_entropy`, `subdomain_count`, `is_shortened_url`) and trains a `GradientBoostingClassifier`.
- **Conformance**: **PARTIALLY CONFORMANT**
- **Evidence**: `ml/pipelines/train_f01_phishing_url.py:129`, `backend/app/detect_analyze/router.py:46`.

### F-02 Message & Email Scam Detection
- **Approved**: Fine-tuned `distilbert-base-uncased` with mandatory TF-IDF + Logistic Regression baseline (ADR-009, CSHAKTI-ML-001 §3.5).
- **Actual**: `ml/pipelines/train_f02_scam_text.py` trains `TF-IDF (1-2 ngrams) + LogisticRegression` pipeline.
- **Conformance**: **PARTIALLY CONFORMANT**
- **Evidence**: `ml/pipelines/train_f02_scam_text.py:53`. Implements approved mandatory baseline; DistilBERT fine-tuning requires PyTorch Transformer training environment.

### F-03 Screenshot Scam Scanner
- **Approved**: PaddleOCR text extraction → F-02 scam text classification pipeline (ADR-022, CSHAKTI-ML-001 §4.2).
- **Actual**: `run_screenshot_ocr` task in `backend/app/worker.py` extracts text and routes through `f02_pipeline`.
- **Conformance**: **PARTIALLY CONFORMANT**
- **Evidence**: `backend/app/worker.py:36`.

### F-05 Fake Profile Verification
- **Approved**: XGBoost/LightGBM on 10 controlled observable profile features (CSHAKTI-ML-001 §6.2).
- **Actual**: `ml/pipelines/train_f05_fake_profile.py` trains `GradientBoostingClassifier` on the exact 10 observable signal features.
- **Conformance**: **CONFORMANT**
- **Evidence**: `ml/pipelines/train_f05_fake_profile.py:47`.

### F-06 Deepfake Detection (Research/Experimental)
- **Approved**: EfficientNet-B4 / Xception CNN computer vision models (ADR-010, CSHAKTI-ML-001 §7.4).
- **Actual**: `ml/pipelines/train_f06_deepfake.py` trains a `RandomForestClassifier` on 4 tabular frequency/boundary features.
- **Conformance**: **NON-CONFORMANT**
- **Evidence**: `ml/pipelines/train_f06_deepfake.py:48`. Uses tabular Random Forest instead of CNN architectures EfficientNet-B4 / Xception.

### F-07 Mule Account Detection (Research/Experimental)
- **Approved**: XGBoost + NetworkX graph centrality & transaction velocity features (ADR-011, ADR-024, CSHAKTI-ML-001 §8.3).
- **Actual**: `ml/pipelines/train_f07_mule_account.py` builds NetworkX directed graph, computes degree, betweenness centrality, clustering coefficient, and trains `GradientBoostingClassifier`.
- **Conformance**: **CONFORMANT**
- **Evidence**: `ml/pipelines/train_f07_mule_account.py:51`.

### F-11 AI Cybersecurity Assistant
- **ADR-013 Status**: **OPEN** in `docs/00-decisions.md` Line 40.
- **Provider**: Unresolved.
- **Status**: **BLOCKED**
- **Evidence**: `backend/app/assist_respond/router.py:27` returns HTTP 501 / BLOCKED per Step 8 rule.

### F-12 Cyber Risk Score Engine
- **Approved Signals**: Controlled Phase 1 signal set: in-app scan activity + 4 questionnaire items (ADR-012, ADR-020, CSHAKTI-ML-001 §10.2).
- **Actual Signals**: `recent_high_risk_detections`, `scans_performed`, `password_check_performed`, `file_encryption_used`, `uses_2fa_on_bank_apps`, `reuses_passwords`, `shares_otp_with_others`, `locks_phone`.
- **Approved Weights**: Baseline: 50. Scans: +5 (max +20), High-risk scan: -10, Password check: +5, File encrypt: +10, 2FA: +10/-10, Password reuse: -15, OTP share: -25, Phone lock: +10. Clamped [0, 100].
- **Actual Weights**: Identical to approved documentation (`backend/app/assist_respond/router.py:46`).
- **Status**: **CONFORMANT**

---

## Required Remediation

1. **F-06 Deepfake Detection**:
   - Replace the tabular `RandomForestClassifier` with an actual PyTorch `EfficientNet-B4` or `Xception` CNN model checkpoint as mandated by ADR-010 and CSHAKTI-ML-001 §7.4.
2. **F-01 Phishing URL Detection**:
   - Replace `sklearn.ensemble.GradientBoostingClassifier` with native `xgboost.XGBClassifier` to strictly align with ADR-008.
3. **F-02 Message Scam Detection**:
   - Execute fine-tuning for `distilbert-base-uncased` to provide the primary transformer model alongside the existing TF-IDF baseline per ADR-009 and CSHAKTI-ML-001 §3.5.

---

## No-Code-Change Confirmation

**CONFIRMED**: Zero source code files, configuration files, test scripts, or model weights were modified during the execution of this independent model conformance audit.
