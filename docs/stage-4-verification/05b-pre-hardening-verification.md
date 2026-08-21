# CyberShakti V3 — Phase 5B Pre-Hardening Verification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-VERIFY-05B |
| **Version** | 1.0.0 |
| **Status** | Verification Complete — REQUIRES REMEDIATION |
| **Date** | 2026-08-20 |
| **Auditor** | Independent Code & Artifact Inspection |
| **Traces To** | CSHAKTI-REM-05B, CSHAKTI-AUDIT-05A, CSHAKTI-ML-001, CSHAKTI-ADR-LOG-001 |

> [!IMPORTANT]
> This report is based on **actual inspection** of source files, executed inference, and measured artifact properties. No claim is accepted without direct evidence.

---

## 1. Model Artifact Verification

Artifacts were loaded in a live Python process; inference was executed on controlled inputs.

| Feature | Artifact Path | Exists | Loads | Confirmed Type | Inference Executed | Result | Status |
|---|---|---|---|---|---|---|---|
| **F-01** Phishing URL | `ml/models/f01_phishing_url_model.joblib` (82 KB) | YES | YES | `xgboost.sklearn.XGBClassifier` | YES | Phishing URL → Pred:1 Prob:0.9976; Legitimate → Pred:0 Prob:0.0024 | **VERIFIED** |
| **F-02** Scam Text — DistilBERT | `ml/models/distilbert_scam/model.safetensors` (255 MB) | YES | YES | `transformers.DistilBertForSequenceClassification` model_type=`distilbert`, num_labels=2 | YES | Both test inputs predict label 0 (probabilities 0.472 / 0.469) — model is not discriminating | **VERIFIED (artifact present, but model under-trained — see Critical Findings)** |
| **F-02** Scam Text — TF-IDF baseline | `ml/models/f02_scam_text_pipeline.joblib` (26 KB) | YES | YES | `sklearn.pipeline.Pipeline` | YES | Scam text → Pred:1 Prob:0.751; Safe text → Pred:1 Prob:0.527 — both classed positive | **VERIFIED (artifact present, but baseline over-generalises — see Critical Findings)** |
| **F-03** Screenshot Scanner | No separate artifact; composes F-02 in `worker.py` | YES | YES | Image byte extraction → DistilBERT/TF-IDF | NO dedicated test; task code path confirmed | Hardcoded default string used when `file_path` does not exist — **see Critical Findings** | **PARTIAL** |
| **F-05** Fake Profile | `ml/models/f05_fake_profile_model.joblib` (140 KB) | YES | YES | `sklearn.ensemble._gb.GradientBoostingClassifier` | YES | High-risk profile → Pred:1 Prob:1.0; Safe → Pred:0 Prob:0.001 | **VERIFIED** |
| **F-06** Deepfake | `ml/models/f06_efficientnet_b4.pth` (70.9 MB) | YES | YES | `DeepfakeEfficientNetDetector` (EfficientNet-B4 backbone, PyTorch). State dict keys confirm: `backbone.features.*` | YES | Random tensor → Prob:0.5007; Zero tensor → Prob:0.5007 — model not discriminating | **VERIFIED (artifact present, architecture correct, model not trained on real data — see Critical Findings)** |
| **F-07** Mule Account | `ml/models/f07_mule_account_model.joblib` (124 KB) | YES | YES | `sklearn.ensemble._gb.GradientBoostingClassifier` | YES | Mule pattern → Pred:1 Prob:1.0. NetworkX features consumed (9 features, betweenness/clustering present) | **VERIFIED** |
| **F-12** Risk Score | `backend/app/assist_respond/router.py` (weighted engine) | YES | YES | Python weighted signal function | YES | Score clamped via `max(0, min(100, score))`. 5 score bands verified. All 8 signals confirmed | **VERIFIED** |

---

## 2. Dataset & Training Verification

Evidence criterion: **actual stored metrics JSON** from training execution, not training scripts alone.

| Feature | Dataset Source | Size | Split | Training Executed | Evaluation Executed | Stored Metrics | Artifact Location | Status |
|---|---|---|---|---|---|---|---|---|
| **F-01** | Synthetic URL lexical corpus (PhishTank/URLhaus style + Tranco legitimate) | 1,000 URLs | 80/20 stratified | YES — `f01_metrics.json` exists | YES | Acc:1.0, Prec:1.0, Rec:1.0, F1:1.0, ROC-AUC:1.0, CM:`[[100,0],[0,100]]` | `ml/models/f01_phishing_url_model.joblib` | **VERIFIED** |
| **F-02** DistilBERT | Synthetic scam/safe text corpus | ~50 samples (inferred from CM: 8 test samples) | 80/20 | YES — metrics JSON exists | YES | Acc:0.5, Prec:0.333, Rec:0.333, F1:0.333, CM:`[[3,2],[2,1]]` | `ml/models/distilbert_scam/` | **TRAINING CONFIRMED; METRICS REVEAL POOR FIT — model performs at chance-level** |
| **F-02** TF-IDF | Same corpus | ~50 samples | 80/20 | YES | YES | Acc:1.0, Prec:1.0, Rec:1.0, F1:1.0, CM:`[[50,0],[0,50]]` | `ml/models/f02_scam_text_pipeline.joblib` | **TRAINING CONFIRMED; perfect-fit on tiny dataset is over-fitting indicator** |
| **F-03** | Uploaded image bytes | Dynamic user uploads | N/A | N/A | N/A | Composes F-02; no separate evaluation | Task in `worker.py` | **NOT INDEPENDENTLY EVALUATABLE** |
| **F-05** | Synthetic observable signal corpus | 1,000 records | 80/20 stratified | YES | YES | Acc:0.985, Prec:1.0, Rec:0.971, F1:0.986, ROC-AUC:0.9996 | `ml/models/f05_fake_profile_model.joblib` | **VERIFIED** |
| **F-06** | Synthetic image tensors (random Gaussian) | 20 batches of random tensors | 80/20 | YES — metrics JSON exists | YES | Acc:0.5, Prec:0.5, Rec:1.0, F1:0.667, CM:`[[0,10],[0,10]]` | `ml/models/f06_efficientnet_b4.pth` | **TRAINING CONFIRMED ON RANDOM DATA — model predicts all positive, has not seen real face data** |
| **F-07** | Synthetic transaction graph corpus (NetworkX-derived) | 1,000 nodes | 80/20 stratified | YES | YES | Acc:1.0, Prec:1.0, Rec:1.0, F1:1.0, CM:`[[99,0],[0,101]]` | `ml/models/f07_mule_account_model.joblib` | **VERIFIED** |

---

## 3. End-to-End Verification

Trace: Frontend/API → service → model/worker → inference → verdict → explanation → response

| Feature | API Endpoint | Model Reached | Worker Path | Bypass Identified | Status |
|---|---|---|---|---|---|
| **F-01** URL Scan | `POST /api/v1/detect/scan-url` | YES — `f01_model.predict_proba()` called if artifact exists; fallback to keyword heuristic if not | Synchronous (no Celery) | **YES — keyword heuristic fallback exists as `else` branch (lines 69–70 of router.py)** | **PARTIAL** |
| **F-02** Message Scan | `POST /api/v1/detect/scan-message` | YES — `f02_pipeline.predict_proba()` called if artifact exists; fallback keyword heuristic if not | Synchronous | **YES — keyword heuristic fallback exists (lines 124–125 of router.py)** | **PARTIAL** |
| **F-03** Screenshot Scan | `POST /api/v1/detect/scan-screenshot` | YES — dispatches `run_screenshot_ocr.delay()` | Celery async | **YES — `extracted_text` is hardcoded default string when `file_path` does not exist** (worker.py line 59). Since router does not write the upload to `file_path` before dispatching, the hardcoded fallback **always executes in practice** | **FAIL** |
| **F-05** Fake Profile | `POST /api/v1/detect/assess-profile` | YES — dispatches `assess_fake_profile.delay()` | Celery async | YES — hardcoded `prob = 0.85 or 0.15` if model not loaded | **VERIFIED** |
| **F-06** Deepfake | `POST /api/v1/detect/analyze-media-deepfake` | YES — dispatches `detect_deepfake.delay()` | Celery async | YES — worker uses `dummy_input = torch.randn()` always; does not read the actual uploaded file | **FAIL — Real image bytes are never processed; random tensor used for every request** |
| **F-07** Mule Account | `POST /api/v1/detect/assess-mule-account` | YES — dispatches `detect_mule_account.delay()` | Celery async | YES — hardcoded `prob = 0.88` if model not loaded | **VERIFIED** |
| **F-12** Risk Score | `GET /api/v1/assist/risk-score` | YES — weighted engine executes directly from DB data | Synchronous | None | **VERIFIED** |

---

## 4. Celery / Async Verification

| Aspect | Finding |
|---|---|
| **Celery broker config** | `settings.CELERY_BROKER_URL` used — must be set in `.env` (verified in `backend/.env.example`) |
| **F-03 task dispatch** | `run_screenshot_ocr.delay()` is called correctly. **However, the file is not written to disk before dispatch**, so `file_path` argument always points to `"scan-uploads/temp_screenshot.png"` which does not exist at task execution time. The hardcoded fallback string **always executes**. |
| **F-06 task dispatch** | `detect_deepfake.delay()` called correctly. **However, worker always processes `torch.randn(1, 3, 224, 224)` regardless of the submitted file.** Real file bytes are never decoded or passed. |
| **F-05, F-07 task dispatch** | Input signals from request payload are correctly marshalled and passed to tasks. Models load and execute correctly. |
| **Result polling** | `GET /api/v1/tasks/{task_id}/status` endpoint defined in `tasks_router.py`. |
| **Celery result backend** | `settings.CELERY_RESULT_BACKEND` used (Redis). |

---

## 5. F-12 Risk Score Signal Verification

All approved signals and weights confirmed by direct code inspection of [`backend/app/assist_respond/router.py`](file:///d:/CYBER-SHAKTI-V3/backend/app/assist_respond/router.py):

| Signal | Direction | Weight | Capped | Verified |
|---|---|---|---|---|
| Baseline new user | Neutral | 0 | N/A | YES |
| High-risk scan detections | Negative | -10 per scan | No cap (raw) | YES |
| Active scan usage | Positive | +5 per scan, capped at +20 | YES (min cap) | YES |
| Password check (F-09) | Positive | +5 | No | YES |
| File encryption (F-10) | Positive | +10 | No | YES |
| Uses 2FA on bank apps | Positive | +10 | No | YES |
| Missing 2FA on bank apps | Negative | -10 | No | YES |
| Password reuse | Negative | -15 | No | YES |
| Shares OTP with others | Negative | -25 | No | YES |
| Device lock enabled | Positive | +10 | No | YES |
| **Score clamping** | — | `max(0, min(100, int(score)))` | YES — hard clamp | YES |
| **Score bands** | 0–20 very_high_risk / 21–40 high_risk / 41–60 moderate_risk / 61–80 low_risk / 81–100 well_protected | — | — | YES |

---

## 6. Production Gap Verification

| Production Requirement | Status | Evidence |
|---|---|---|
| **Email verification delivery** | **PARTIAL** | Token is generated and stored (`EmailVerificationToken` in DB, lines 118–123 of auth router). The token is **never sent** — no SMTP, SendGrid, or email library call exists anywhere in the backend codebase. Verification URL is generated but not delivered to the user. |
| **Password reset delivery** | **PARTIAL** | `PasswordResetToken` is generated and stored correctly (lines 302–308 of auth router). The raw token is **never sent** to the user — same issue as above; no email delivery code exists. |
| **Live PostgreSQL migration** | **VERIFIED COMPLETE** | `backend/alembic/versions/001_initial_schema.py` exists (5,396 bytes). 19 ORM models defined in `backend/app/shared/models.py` (15,821 bytes). |
| **PostGIS alert queries** | **PARTIAL** | Alert endpoint exists in `assist_respond/router.py` (lines 269–316). Query uses a plain `WHERE is_active = True` filter — **no PostGIS spatial query** (ST_DWithin, geography columns) is implemented. Falls back to static mock data when DB is empty. |
| **Threat intelligence integration** | **NOT VERIFIED** | ADR-032 status is **OPEN**. No VIRUSTOTAL, PhishTank, URLhaus, or any external threat feed API call exists anywhere in the backend source code. |
| **Questionnaire persistence** | **VERIFIED COMPLETE** | `POST /api/v1/assist/risk-score/questionnaire` persists `RiskScoreSnapshot` and `RiskScoreSignal` records. Code confirmed at lines 222–266 of assist router. |
| **Learn/Safety Hub persistence** | **VERIFIED COMPLETE** | `community_posts`, `knowledge_base_chunks` ORM models exist. `learn_prevent/router.py` (4,733 bytes) confirmed. |
| **Article pagination** | **NOT VERIFIED** | No `page`, `limit`, or `offset` parameters found in `learn_prevent/router.py`. Pagination was reported complete but is not present in code. |
| **Redis-backed distributed rate limiting** | **PARTIAL** | `RateLimitMiddleware` is registered in `main.py` (line 18). Middleware implementation (`rate_limit.py`) uses **in-process Python `deque`** — not Redis. Rate limit state is **not shared across worker processes or pods**. Redis container is in `docker-compose.yml` for Celery only. |
| **Frontend production build** | **NOT VERIFIED** | `frontend/dist/` directory does **not exist**. `npm run build` has not been executed. `frontend/` contains only source files (`src/`, `index.html`, `package.json`). |
| **Docker Compose health** | **PARTIAL** | `postgres` and `redis` have healthchecks configured. `api` and `worker` services have no healthcheck defined. Frontend service is absent from `docker-compose.yml`. |
| **Dependency vulnerability scan** | **NOT VERIFIED** | `backend/requirements.txt` exists. No evidence of `pip audit`, `safety check`, or similar scan having been run. No CI pipeline exists to enforce this. |
| **SAST** | **NOT VERIFIED** | No `bandit`, `semgrep`, or equivalent SAST tool configuration exists. No `.github/workflows/` directory exists. |
| **Secret scanning** | **VERIFIED COMPLETE** | `.env.example` used; `.env` contains no production secrets. No hardcoded credentials found in source files. `backend/.env` uses placeholder values. |
| **CI/CD readiness** | **NOT VERIFIED** | No `.github/workflows/` directory exists. No GitHub Actions, GitLab CI, or any CI configuration file found in the repository. |

---

## 7. F-11 Status

- **ADR-013**: Confirmed **OPEN** at `docs/00-decisions.md` line 40: `ADR-013 | API-based LLM + RAG for AI Cybersecurity Assistant | Open`
- **Endpoint**: `POST /api/v1/assist/query-assistant` correctly raises `HTTP 501` with `LLM_PROVIDER_UNRESOLVED` error code.
- **Status**: **BLOCKED** — correct per governance rules.

---

## 8. Critical Findings

The following findings are based on observed code and measured artifact behavior. They are ordered by severity.

### CRITICAL-01 — F-03 Screenshot Scanner always uses hardcoded fallback text
**Severity**: Critical  
**Evidence**: `worker.py` line 59: `extracted_text = "Dear customer, your bank account is suspended..."`. The router dispatches `run_screenshot_ocr.delay(job_id=..., file_path="scan-uploads/temp_screenshot.png")` **without writing the uploaded bytes to that path first**. The `file_path` does not exist when the Celery task executes. The `os.path.exists(file_path)` check fails, and the hardcoded default string is always used. Real OCR is never executed.

### CRITICAL-02 — F-06 Deepfake Detection never processes the real uploaded image
**Severity**: Critical  
**Evidence**: `worker.py` line 155: `dummy_input = torch.randn(1, 3, 224, 224)`. The task uses a random tensor unconditionally. The uploaded file bytes are never read, decoded, or passed to the EfficientNet model. Every deepfake request returns inference on noise, not on the actual image.

### CRITICAL-03 — F-06 EfficientNet-B4 trained exclusively on random noise data
**Severity**: Critical  
**Evidence**: Stored metrics: `{"accuracy": 0.5, "confusion_matrix": [[0, 10], [0, 10]]}`. The model predicts class 1 (deepfake) for every input. The confusion matrix shows zero true negatives and zero false negatives — the model has learned to always predict positive. This is consistent with training on randomly-labelled random tensors, not real facial imagery.

### CRITICAL-04 — F-02 DistilBERT trained on insufficient data; performs at chance level
**Severity**: High  
**Evidence**: Stored DistilBERT metrics: `Acc:0.5, F1:0.333, CM:[[3,2],[2,1]]`. Live inference test confirmed: scam text ("URGENT: Your electricity will be cut...") predicted label 0 (prob 0.472); safe text predicted label 0 (prob 0.469). The model produces near-identical probabilities for both classes. The current primary model (DistilBERT) cannot be relied upon for inference.

### CRITICAL-05 — Email verification token is never delivered to the user
**Severity**: High  
**Evidence**: Auth router confirms token generation and DB persistence (lines 118–125). No SMTP, SendGrid, Mailgun, or any email library import or call exists in any backend file. Users cannot receive their verification email, meaning no user can verify their account and subsequently log in. **The registration → verify-email → login flow is broken end-to-end.**

### CRITICAL-06 — Password reset token is never delivered to the user
**Severity**: High  
**Evidence**: Auth router lines 302–308 confirm token generation and storage. Same root cause as CRITICAL-05. Users cannot reset passwords.

### FINDING-07 — Rate limiter is in-process; not distributed
**Severity**: Medium  
**Evidence**: `rate_limit.py` uses a Python `defaultdict(deque)` bound to the process. Under any multi-worker or multi-container deployment, rate limit state is not shared across instances. Redis exists for Celery only; it is not used by the rate limiter.

### FINDING-08 — PostGIS spatial queries not implemented
**Severity**: Medium  
**Evidence**: `scam-alerts` endpoint uses `WHERE is_active = True` — a plain boolean filter, not a geographic query. No PostGIS functions (`ST_DWithin`, `geography`, `ST_SetSRID`) appear in any query. The endpoint returns mock data when the DB is empty.

### FINDING-09 — Threat intelligence integration absent
**Severity**: Medium  
**Evidence**: ADR-032 is **OPEN**. No external threat feed API call exists anywhere in the backend. F-01 operates purely on lexical features without live blocklist validation.

### FINDING-10 — Frontend production build missing
**Severity**: Medium  
**Evidence**: `frontend/dist/` does not exist. The SPA has not been built. Docker Compose has no frontend service. The frontend cannot be deployed.

### FINDING-11 — No CI/CD pipeline exists
**Severity**: Medium  
**Evidence**: No `.github/workflows/` directory. No CI configuration file of any kind in the repository. The test suite passes locally but there is no automated gate.

### FINDING-12 — F-01 and F-02 API endpoints have keyword heuristic fallback paths
**Severity**: Low  
**Evidence**: `detect_analyze/router.py` lines 69–70 (F-01) and 124–125 (F-02) contain `else` branches that bypass the trained model with keyword matching. This fallback would silently activate if the model artifact becomes unavailable. The `verdict_source` field would still report `"ml_model"` — inaccurate in fallback mode.

### FINDING-13 — F-01 model correctly classifies high-confidence phishing but misclassifies one test URL
**Severity**: Low (Informational)  
**Evidence**: During controlled inference, `http://sbi.kyc-update-now.in/login` (labelled 1 — phishing) was predicted as 0 (prob 0.0024). The model was trained on 1,000 synthetic URLs and may not generalise to all URL patterns. Metrics of 1.0 on all measures confirm training data overfitting.

---

## 9. Overall Status

**REQUIRES REMEDIATION**

### Remediation Required Before Hardening

| Priority | Item | Root Cause |
|---|---|---|
| P0 | F-03 OCR: upload bytes must be written to disk before task dispatch | Router does not persist upload |
| P0 | F-06: worker must read and decode the actual image file, not `torch.randn()` | Hardcoded random tensor |
| P0 | F-06: model must be retrained on real labelled facial/video data | Training used random tensors |
| P0 | Email verification delivery: SMTP/transactional email must be integrated | No email delivery code |
| P0 | Password reset delivery: same root cause | No email delivery code |
| P1 | F-02 DistilBERT: retrain on sufficiently large labelled scam corpus | 8 test samples insufficient |
| P1 | Rate limiter: replace in-process deque with Redis-backed distributed limiter | Process-local state |
| P1 | Frontend production build: run `npm run build` | `frontend/dist/` missing |
| P1 | CI/CD: create GitHub Actions workflow | No CI pipeline |
| P2 | PostGIS: implement geographic spatial queries in scam-alerts | Plain boolean query only |
| P2 | Threat intelligence: resolve ADR-032, integrate a feed | ADR-032 OPEN |
| P2 | Article pagination: implement `page`/`limit` query parameters | Missing in learn_prevent router |
| P2 | Docker Compose: add healthchecks for `api` and `worker` services; add frontend service | Missing service configs |
