# CyberShakti — AI/ML Model Testing & Evaluation Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-TEST-003 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-ML-001, CSHAKTI-CONST-001 §3 |
| **Governed By** | CSHAKTI-CONST-001 §3 — all metric targets marked TBD until empirical evaluation |

---

## Table of Contents

1. [AI/ML Evaluation Philosophy](#1-aiml-evaluation-philosophy)
2. [Evaluation Datasets & Splitting Strategy](#2-evaluation-datasets--splitting-strategy)
3. [Evaluation Metrics & Benchmarks](#3-evaluation-metrics--benchmarks)
4. [Adversarial & Robustness Testing](#4-adversarial--robustness-testing)
5. [Model Drift & Continuous Monitoring](#5-model-drift--continuous-monitoring)
6. [Explainability Verification](#6-explainability-verification)

---

## 1. AI/ML Evaluation Philosophy

In accordance with **CSHAKTI-CONST-001 §3.4**, no performance metrics (Precision, Recall, F1, Accuracy, ROC-AUC) are fabricated or assumed prior to empirical evaluation.

### Testing Principles:
- **No Inferred Precision**: Models must be evaluated on real held-out test sets.
- **Baseline Comparison**: Advanced models (e.g., DistilBERT) MUST be empirically compared against classical baselines (e.g., TF-IDF + Logistic Regression).
- **Out-of-Distribution Robustness**: Models are evaluated on deliberately obfuscated and adversarial samples.

---

## 2. Evaluation Datasets & Splitting Strategy

### 2.1 Splitting Rules
- **Train / Validation / Test Split**: 80% / 10% / 10% stratified split.
- **Temporal Splitting**: For time-sensitive datasets (e.g., phishing URLs), the test set MUST consist of samples collected strictly AFTER the training set date to evaluate temporal drift.

### 2.2 Feature Evaluation Sets

| Feature | Primary Evaluation Dataset | Negative Class Source |
|---|---|---|
| **F-01 Phishing URL** | PhishTank + URLhaus corpus | Tranco / Alexa Top 1M legitimate URLs |
| **F-02 Scam Text** | Curated Indian Scam Message corpus | SMS Spam Collection + Legitimate transactional messages |
| **F-03 Screenshot OCR** | Curated scam screenshot test set | Clear document & UI screenshots |
| **F-05 Fake Profile** | Curated signal dataset | Legitimate verified profile signal set |
| **F-06 Deepfake** | FaceForensics++ / Celeb-DF v2 | Standard unmanipulated face video dataset |
| **F-07 Mule Account** | Elliptic Transaction Graph | Standard legitimate account transaction data |

---

## 3. Evaluation Metrics & Benchmarks

The following metrics are computed for each model evaluation run via `ml/pipelines/evaluate_models.py`:

```
                Actual Positive    Actual Negative
Predicted Pos       True Pos (TP)    False Pos (FP)
Predicted Neg       False Neg (FN)   True Neg (TN)

Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1-Score = 2 * (Precision * Recall) / (Precision + Recall)
FPR = FP / (FP + TN)
```

> **Target Thresholds**: All target metric thresholds (Precision, Recall, F1) are **TBD** pending initial baseline training runs.

---

## 4. Adversarial & Robustness Testing

Models must undergo automated robustness testing before release:

### 4.1 URL Obfuscation Tests (F-01)
- Homoglyph domain substitution (e.g., `bаnk.com` using Cyrillic 'а').
- Excessive subdomain nesting (`login.verify.account.bank.com.scam.info`).
- IP address hostnames (`http://192.168.1.1/login`).

### 4.2 Text Obfuscation Tests (F-02)
- Zero-width space insertion inside scam keywords (`K Y C`, `O T P`).
- Leetspeak substitution (`K Y C u p d a t 3`).
- Mixed Hindi-English (Hinglish) text strings.

---

## 5. Model Drift & Continuous Monitoring

- **Monitoring Metric**: Track weekly prediction score distribution shifts via Population Stability Index (PSI).
- **Trigger for Retraining**: When PSI > 0.25 or when monthly evaluation on fresh threat samples shows performance drop beyond threshold.
- **MLflow Tracking**: All model evaluations logged to MLflow with complete hyperparameter and dataset git commit hashes.

---

## 6. Explainability Verification

Every ML prediction MUST be verified for explainability output:
- **F-01 XGBoost**: Verify SHAP top-3 feature contribution list is generated.
- **F-02 DistilBERT**: Verify attention weights highlight key scam trigger phrases.
- **Fail-Safe**: If explanation engine fails, return model verdict with generic category explanation; NEVER crash the API call.

---

*End of CyberShakti AI/ML Model Testing & Evaluation Specification — CSHAKTI-TEST-003 v1.0.0*
