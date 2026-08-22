# CyberShakti V3

**AI-Powered Digital Safety & Cybersecurity Platform**

CyberShakti is a full-stack cybersecurity platform built to help everyday users in India detect financial fraud, phishing, scam messages, deepfake media, fake social profiles, and money mule accounts. It combines production-grade ML models with a modern React frontend and a FastAPI backend, designed around real-world Indian threat contexts — UPI/OTP fraud, KYC scams, WhatsApp phishing, and AI-manipulated media.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [ML Models](#ml-models)
- [API Reference](#api-reference)
- [Database Schema](#database-schema)
- [Authentication](#authentication)
- [Getting Started](#getting-started)
  - [Local Development (SQLite)](#local-development-sqlite)
  - [Docker Compose (Full Stack)](#docker-compose-full-stack)
- [Environment Variables](#environment-variables)
- [Frontend Pages](#frontend-pages)
- [Testing](#testing)
- [Design Decisions & Known Limitations](#design-decisions--known-limitations)

---

## Features

CyberShakti is organized into five modules:

| Module | What It Does |
|---|---|
| **Detect & Analyze** | Phishing URL scan, scam text/message classification, screenshot OCR analysis, QR code scanning, fake social profile assessment, deepfake image detection, money mule account detection |
| **Protect** | Phone number threat lookup, password strength checker, AES-256-GCM file encryption & decryption |
| **Assist & Respond** | Personalized Cyber Risk Score (explainable weighted signal engine), security questionnaire, scam alerts feed |
| **Learn & Prevent** | Daily safety tips, interactive cybersecurity quiz, educational article library |
| **Users & Auth** | JWT auth with refresh token rotation, TOTP 2FA, email verification, password reset, account deletion |

---

## Tech Stack

### Frontend
- **React 18** with Vite 5
- **React Router DOM v6** — client-side routing with animated transitions
- **Tailwind CSS v3** — dark cyberpunk theme (slate/cyan/purple palette)
- **Framer Motion v11** — page and component animations
- **Recharts** — risk score visualizations
- **Lucide React** — icons
- **Axios** — HTTP client with JWT interceptor

### Backend
- **FastAPI** (Python, fully async)
- **Uvicorn** — ASGI server
- **SQLAlchemy 2.0** (async) — ORM with `asyncpg` for PostgreSQL, `aiosqlite` for SQLite dev fallback
- **Alembic** — database migrations
- **Celery 5 + Redis** — async task queue for long-running ML jobs
- **Pydantic v2** — request/response validation
- **PyJWT + Argon2 + pyotp** — authentication

### ML / AI
- **XGBoost + scikit-learn** — phishing URL detection, fake profile assessment, mule account detection
- **TF-IDF + Logistic Regression** — scam text baseline classifier
- **DistilBERT** (HuggingFace Transformers) — scam text primary classifier, loaded in Celery worker
- **EfficientNet-B4** (PyTorch) — deepfake image detection, trained on Celeb-DF dataset
- **EasyOCR** — text extraction from screenshot images
- **SHAP** — explainability for XGBoost models
- **NetworkX** — transaction graph features for mule account detection

### Infrastructure
- **PostgreSQL 15 + PostGIS + pgvector** (production)
- **SQLite** (local dev, no setup required)
- **Redis 7** — Celery broker + result backend
- **Docker + Docker Compose** — 4-service containerized deployment

---

## Project Structure

```
CYBER-SHAKTI-V3/
├── frontend/                        # React SPA (Vite)
│   └── src/
│       ├── pages/                   # 11 page components
│       ├── components/              # Shared UI: Navbar, ThreatResultCard, ScanAnimation, RiskMeter, etc.
│       ├── context/AuthContext.jsx  # JWT state management
│       └── services/api.js          # Axios instance (points to :8000)
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI app, middleware, router registration, lifespan
│   │   ├── config.py                # Pydantic Settings (reads .env), runtime security checks
│   │   ├── worker.py                # Celery app + all async ML task definitions
│   │   ├── tasks_router.py          # GET /tasks/{id}/status polling endpoint
│   │   ├── users_auth/router.py     # Auth: register, login, 2FA, tokens, account mgmt
│   │   ├── detect_analyze/router.py # 7 detection endpoints + URL feature extraction
│   │   ├── assist_respond/router.py # Risk score, questionnaire, scam alerts, assistant
│   │   ├── learn_prevent/router.py  # Daily tip, quiz, articles
│   │   ├── protect/router.py        # Phone check, password check, file encrypt/decrypt
│   │   ├── shared/
│   │   │   ├── models.py            # SQLAlchemy ORM models (17 tables)
│   │   │   ├── auth.py              # JWT auth dependencies
│   │   │   ├── database.py          # Async engine + session factory
│   │   │   ├── security.py          # Argon2, JWT, TOTP utilities
│   │   │   ├── email_service.py     # SMTP email delivery
│   │   │   ├── explanation_engine.py# Human-readable verdict generation
│   │   │   ├── ocr_service.py       # EasyOCR wrapper
│   │   │   ├── uploads.py           # Magic-byte image validation
│   │   │   ├── file_crypto.py       # AES-256-GCM encryption/decryption
│   │   │   ├── rate_limit.py        # In-process rate limiting middleware
│   │   │   └── qrdecode.py          # QR code decoding
│   │   └── ml/
│   │       ├── f01.py               # Phishing URL feature extraction + XGBoost inference
│   │       ├── f02.py               # Scam text NLP pipeline
│   │       ├── f03.py               # Screenshot OCR + scam detection
│   │       ├── f05.py               # Fake profile XGBoost assessment
│   │       ├── f06.py               # Deepfake EfficientNet-B4 detection
│   │       ├── f07.py               # Mule account XGBoost + graph features
│   │       ├── f11.py               # RAG cybersecurity assistant (blocked — ADR-013)
│   │       └── models/              # Trained model artifacts (*.joblib, *.pth, *.safetensors)
│   │
│   ├── ml/
│   │   ├── pipelines/               # Training scripts for all models
│   │   ├── datasets/                # Training datasets (SMS TSV, URLhaus CSV)
│   │   └── knowledge_base/          # RAG knowledge base (Markdown files)
│   │
│   ├── alembic/                     # Database migration scripts
│   ├── tests/                       # pytest test suite
│   ├── requirements.txt
│   └── .env.example
│
└── docker-compose.yml
```

---

## ML Models

### F-01 — Phishing URL Detection
Detects malicious, phishing, and credential-harvesting URLs.

- **Approach:** XGBoost classifier on 17 lexical + domain features extracted from the URL (subdomain depth, entropy, IP address usage, HTTPS, suspicious keywords, URL length, path depth, etc.)
- **Explainability:** SHAP TreeExplainer returns top-5 feature contributions per prediction
- **Risk thresholds:** `prob ≥ 0.75` → high_risk, `≥ 0.55` → moderate_risk, `≥ 0.35` → low_risk, else safe. URLs using raw IPs are bumped to moderate_risk regardless.
- **Model file:** `f01_phishing_url_model.joblib`

### F-02 — Scam Message / Text Classification
Detects scam content in SMS, WhatsApp messages, emails (OTP theft, KYC fraud, lottery, urgency phishing).

- **Approach:** Two-tier — TF-IDF + Logistic Regression baseline (`f02_scam_text_pipeline.joblib`) for synchronous calls. Fine-tuned **DistilBERT** (`distilbert_scam/`) loaded in the Celery worker as primary, with TF-IDF fallback.
- **Preprocessing:** NFKC Unicode normalization, control character removal
- **Model files:** `f02_scam_text_pipeline.joblib`, `distilbert_scam/model.safetensors`

### F-03 — Screenshot OCR + Scam Detection
Detects scam content embedded in chat screenshots (WhatsApp, SMS apps).

- **Approach:** Two-stage async pipeline — (1) EasyOCR with OpenCV CLAHE enhancement extracts text from the image; (2) F-02 classifies the extracted text.
- **Signals detected in text:** urgency language, financial credential mentions (kyc/bank/upi/otp), URL presence
- **Execution:** Async via Celery (`run_screenshot_ocr` task)

### F-05 — Fake Social Profile Detection
Identifies fraudulent social media profiles used in romance scams, investment fraud, and impersonation.

- **Approach:** XGBoost on 12 encoded behavioral signals: account age category, follower count range, following/follower ratio, profile photo presence/genericity, bio presence, unsolicited money requests, celebrity/official impersonation claims, unsolicited DM contact, investment scheme promotion.
- **Note:** Assesses risk signals, not identity — a low-risk result does not confirm profile authenticity.
- **Model file:** `f05_fake_profile_model.joblib`

### F-06 — Deepfake Image Detection
Detects AI-generated facial manipulation and face swaps in images.

- **Approach:** PyTorch **EfficientNet-B4** CNN trained on the Celeb-DF dataset. Images resized to 224×224, ImageNet-normalized. Label 0 = fake (anomaly score = probability of fake).
- **Marked experimental** (`is_experimental: true`) in all verdicts.
- **Model file:** `f06_efficientnet_b4.pth`

### F-07 — Money Mule Account Detection
Identifies bank accounts used as intermediaries in financial crime.

- **Approach:** XGBoost on a 9-feature vector combining transaction signals (account age, velocity, multiple recipients, pass-through pattern, round-amount transfers) with 4 graph centrality features computed via NetworkX.
- **Domain note (ADR-024):** ~~Trained on the Elliptic cryptocurrency dataset~~ **RESOLVED** — Model retrained on a synthetic Indian bank transaction dataset modelling UPI/NEFT/IMPS mule typologies (burst UPI transfers, smurfing < ₹50k, job-scam account recruitment). See `ml/pipelines/train_f07_indian_bank.py`.
- **Marked experimental** in all verdicts.
- **Model file:** `f07_mule_account_model.joblib`

### F-11 — RAG Cybersecurity Assistant *(Blocked)*
A Retrieval-Augmented Generation assistant for cybersecurity Q&A using a local knowledge base.

- **Current status:** **Blocked** — the `/query-assistant` API returns HTTP 501. ADR-013 (LLM provider selection) is unresolved and blocks generation. The RAG retrieval pipeline and knowledge base are implemented but no LLM is wired in.
- **Knowledge base:** `kyc-account-block.md`, `otp-upi-safety.md`, `password-2fa.md`

---

## API Reference

All routes are prefixed `/api/v1`. Swagger UI is available at `http://localhost:8000/docs` in dev mode.

### Auth — `/api/v1/auth`

| Method | Path | Description |
|---|---|---|
| `POST` | `/register` | Create account (`email`, `password`, `consent_given: true`) |
| `GET` | `/verify-email?token=...` | Verify email address via token |
| `POST` | `/login` | Authenticate, returns JWT access+refresh tokens or 2FA challenge |
| `POST` | `/login/2fa` | Complete TOTP 2FA login with `two_fa_session_token` + `totp_code` |
| `POST` | `/refresh` | Rotate refresh token, issue new access token |
| `POST` | `/logout` | Revoke refresh token |
| `POST` | `/password-reset/request` | Send password reset email |
| `POST` | `/password-reset/complete` | Reset password using token |
| `POST` | `/2fa/enroll` | Generate TOTP secret + QR code URI + 8 backup codes |
| `POST` | `/2fa/confirm-enrollment` | Verify TOTP code to activate 2FA |
| `GET` | `/me` | Get current user profile |
| `DELETE` | `/me` | Soft-delete account |

### Detect & Analyze — `/api/v1/detect`

| Method | Path | Description |
|---|---|---|
| `POST` | `/scan-url` | F-01: phishing URL scan → immediate result |
| `POST` | `/scan-message` | F-02: scam text classification → immediate result |
| `POST` | `/scan-screenshot` | F-03: upload screenshot image → async task (poll `/tasks/{id}/status`) |
| `POST` | `/scan-qr` | F-04: upload QR image → decode + F-01 URL check |
| `POST` | `/assess-profile` | F-05: submit profile signals → async task |
| `POST` | `/analyze-media-deepfake` | F-06: upload image → async deepfake detection |
| `POST` | `/assess-mule-account` | F-07: submit transaction signals → mule account risk |

### Protect — `/api/v1/protect`

| Method | Path | Description |
|---|---|---|
| `POST` | `/check-phone` | Phone number threat lookup |
| `POST` | `/check-password` | Password entropy + strength assessment |
| `POST` | `/encrypt-file` | AES-256-GCM file encryption → streams `.enc` file |
| `POST` | `/decrypt-file` | AES-256-GCM file decryption → streams original file |

### Assist & Respond — `/api/v1/assist`

| Method | Path | Description |
|---|---|---|
| `GET` | `/risk-score` | Compute & return Cyber Risk Score with signal breakdown |
| `POST` | `/risk-score/questionnaire` | Submit security habits questionnaire, update score |
| `GET` | `/scam-alerts` | Fetch active regional scam alerts |
| `POST` | `/query-assistant` | F-11 AI assistant (**BLOCKED — returns HTTP 501**) |

### Learn & Prevent — `/api/v1/learn`

| Method | Path | Description |
|---|---|---|
| `GET` | `/daily-tip` | Fetch the daily safety tip |
| `GET` | `/quiz` | Fetch quiz questions |
| `POST` | `/quiz/submit-answer` | Submit quiz answer, receive explanation |
| `GET` | `/articles` | List articles (filterable by category) |
| `GET` | `/articles/{slug}` | Get article by slug |

### Async Tasks — `/api/v1`

| Method | Path | Description |
|---|---|---|
| `GET` | `/tasks/{task_id}/status` | Poll Celery task result (queued / processing / complete / error) |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Service health probe |
| `GET` | `/health/live` | Kubernetes liveness probe |

---

## Database Schema

SQLAlchemy 2.0 ORM models with full cross-database compatibility (PostgreSQL + SQLite).

| Table | Purpose |
|---|---|
| `users` | User accounts — email, Argon2 password hash, email verification, active status, role, TOTP enabled, soft-delete |
| `refresh_tokens` | JWT refresh token store — hashed tokens, issued/expires/revoked timestamps, IP + user-agent |
| `totp_secrets` | Encrypted TOTP secrets for 2FA |
| `backup_codes` | Hashed 2FA backup codes (8 per enrollment) |
| `password_reset_tokens` | Time-limited password reset tokens (1hr expiry) |
| `email_verification_tokens` | Email verification tokens (24hr expiry) |
| `scan_results` | Every ML scan result — feature ID (F-01 → F-08), input type, risk level, raw probability score, task ID/status |
| `risk_score_snapshots` | Snapshots of a user's computed Cyber Risk Score |
| `risk_score_signals` | Individual weighted signal contributions per snapshot |
| `knowledge_base_documents` | Cybersecurity knowledge base articles |
| `assistant_conversations` | F-11 assistant conversation sessions |
| `assistant_messages` | Messages within conversations (role: user/assistant) |
| `scam_alerts` | Regional scam alerts — type, severity, location, source, expiry |
| `safety_tips` | Daily safety tip content |
| `quiz_questions` | Quiz questions with category and difficulty |
| `quiz_options` | Answer options per question (`is_correct` flag) |
| `articles` | Educational articles (slug, content, published status) |
| `audit_log` | Security audit events — event type, user ID, IP, user-agent, JSON detail |

**Migrations:** Run with Alembic (`alembic upgrade head`).  
**Dev auto-init:** On SQLite, tables are created automatically at startup with a seeded demo account.

---

## Authentication

JWT-based with full refresh token rotation, TOTP 2FA, and Argon2id password hashing.

**Registration:** Email + password (min 8 chars) + explicit consent → Argon2 hash → email verification token (24hr) → verification email sent. Returns generic message to prevent email enumeration.

**Login:**
1. Verify Argon2 password hash + email verified status
2. If TOTP enabled: return scoped `two_fa_session_token` (5-min JWT) + `requires_2fa: true`
3. If no 2FA: issue `access_token` (30 min, HS256) + `refresh_token` (7 days, stored as hash in DB)

**Token rotation:** On each `/refresh` call, the old token is revoked and a new one is issued. Detected token reuse (already-revoked token replayed) triggers revocation of **all** active refresh tokens for that user.

**TOTP 2FA:** `pyotp.random_base32()` secret, AES-encrypted before DB storage. 8 backup codes generated at enrollment, each hashed with Argon2.

**Prod security checks (`config.py`):** Startup is blocked in staging/prod if DEBUG is true, the JWT secret is weak (< 32 chars or starts with "dev_secret"), wildcard CORS is configured, or default database credentials are detected.

**Demo account (dev/SQLite only):**
```
Email:    user@cybershakti.in
Password: CyberShakti@123
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- (Optional for full stack) Docker + Docker Compose

### Local Development (SQLite)

No external database or Redis required. The app falls back to SQLite and synchronous task execution.

**1. Clone & set up backend**

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

**2. Configure environment**

```bash
cp .env.example .env
# Edit .env — at minimum set JWT_SECRET_KEY to a random 32+ char string
# Leave DATABASE_URL pointing to sqlite for local dev
```

**3. Start the API server**

```bash
uvicorn app.main:app --reload --port 8000
```

Tables are auto-created and the demo account is seeded on first startup.

**4. Set up frontend**

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

**5. (Optional) Start Celery worker**

Required for async scan features (screenshot OCR, deepfake detection, fake profile, mule account). Requires Redis.

```bash
# Start Redis (Docker)
docker run -d -p 6379:6379 redis:7-alpine

# Start worker
cd backend
celery -A app.worker.celery_app worker --loglevel=info
```

---

### Docker Compose (Full Stack)

Starts PostgreSQL, Redis, the FastAPI API, and the Celery worker together.

```bash
cp backend/.env.example backend/.env
# Edit backend/.env — set strong JWT_SECRET_KEY, verify DB credentials

docker compose up --build
```

Services:
| Service | Port | Description |
|---|---|---|
| `api` | 8000 | FastAPI backend, Swagger UI at `/docs` |
| `worker` | — | Celery ML task worker |
| `postgres` | 5432 | PostgreSQL 15 + PostGIS + pgvector |
| `redis` | 6379 | Celery broker + result backend |

Run migrations after first startup:

```bash
docker compose exec api alembic upgrade head
```

---

## Environment Variables

Copy `backend/.env.example` to `backend/.env` and configure:

| Variable | Description |
|---|---|
| `ENVIRONMENT` | `dev` or `prod` — controls CORS strictness and email verification bypass |
| `DEBUG` | `true` / `false` — enables Swagger UI and verbose errors |
| `PORT` | API port (default `8000`) |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` or `sqlite+aiosqlite:///./cybershakti_local.db` |
| `REDIS_URL` | Redis connection string |
| `CELERY_BROKER_URL` | Celery broker URL (Redis) |
| `CELERY_RESULT_BACKEND` | Celery result backend URL (Redis) |
| `JWT_SECRET_KEY` | HS256 signing secret — must be ≥ 32 chars and random in production |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL (default `30`) |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL (default `7`) |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins for production |
| `RATE_LIMIT_ENABLED` | `true` / `false` |
| `RATE_LIMIT_DEFAULT_PER_MINUTE` | Default rate limit (default `60`) |
| `RATE_LIMIT_AUTH_PER_MINUTE` | Auth endpoint rate limit (default `10`) |
| `MAX_UPLOAD_BYTES` | Max file upload size in bytes (default `10485760` = 10 MB) |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL` | SMTP email delivery |
| `S3_BUCKET_NAME`, `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY` | S3 file storage (optional) |
| `THREAT_INTEL_API_KEY` | External threat intelligence API key (optional, simulated in dev) |
| `LLM_API_KEY` | LLM provider key (reserved — F-11 currently blocked via ADR-013) |

---

## Frontend Pages

| Page | Route(s) | Description |
|---|---|---|
| **Home** | `/` | Landing page with feature cards, system status strip, and risk score CTA |
| **Phishing Scan** | `/detect/phishing-link` | Two-tab: URL text input (F-01) with auto-scheme formatting + QR code image upload (F-04) |
| **Message Scan** | `/detect/message-scan` | Two-tab: paste text (F-02) and screenshot upload with OCR async polling (F-03) |
| **Deepfake Scan** | `/detect/deepfake` | Drag-and-drop image upload → EfficientNet-B4 deepfake analysis (F-06) |
| **MuleTrace** | `/detect/mule-account` | MuleTrace Forensic Network Investigator — dynamic topology map engine with NetworkX centrality analysis, XGBoost classification, and live scenario metrics |
| **Password Check** | `/protect/password-check` | Real-time Shannon entropy calculator, 10B guesses/sec crack time estimator, character checklist & 1-click password generator |
| **File Encryption** | `/protect/file-encryption` | Zero-Knowledge Dual-Engine File Vault — Argon2id + AES-256-GCM server vault with automatic Web Crypto in-browser fallback |
| **Risk Score** | `/assist/risk-score` | Animated risk meter gauge + explainable signal breakdown + security questionnaire |
| **Safety Hub** | `/learn` | Daily safety tip, interactive quiz, and educational articles |
| **Login** | `/login` | Email/password login with inline TOTP 2FA challenge handling |
| **Register** | `/register` | Registration with consent acknowledgment |

---

## Testing

**Backend (pytest)**

```bash
cd backend
pytest --cov=app tests/
```

**Frontend (Vitest)**

```bash
cd frontend
npm run test:run
```

Dependencies: `pytest`, `pytest-asyncio`, `pytest-cov`, `ruff`, `black` (backend); `vitest` (frontend).

---

## Design Decisions & Known Limitations

- **F-07 domain mismatch (ADR-024) — RESOLVED.** The mule account detection model has been retrained on a synthetic Indian bank transaction dataset modelling real UPI/NEFT/IMPS fraud typologies (burst pass-through, smurfing, job-scam recruitment). See `backend/ml/pipelines/train_f07_indian_bank.py`. All verdicts still carry `is_experimental: true` as the dataset is synthetic, not real labelled bank data.

- **MuleTrace Topology Map Engine & Demo Datasets.** The network topology console dynamically updates nodes, centrality metrics, and transaction volume totals across built-in scenarios (`UPI Mule Ring`, `Crypto P2P`, `Smurfing`) and custom CSV uploads (`demo_mule_ring_simple.csv`, `demo_mule_ring_complex.csv`).

- **Dual-Engine Zero-Knowledge File Cryptography.** `/protect/file-encryption` supports both server-side Argon2id + AES-256-GCM and client-side browser Web Crypto API (AES-256-GCM + PBKDF2 100k rounds) to guarantee 100% encryption/decryption availability regardless of network connectivity. Mode switching between Encrypt and Decrypt automatically clears and resets inputs for a clean user state.

- **Password Security & Entropy Engine.** `/protect/password-check` evaluates Shannon entropy bits, character diversity rules, common wordlist matches, and brute-force time estimates assuming 10 billion attempts/second, accessible to both guest and authenticated sessions.

- **F-06 deepfake is experimental.** EfficientNet-B4 is trained on the Celeb-DF dataset (celebrity deepfakes). Performance on in-the-wild or non-celebrity images may vary. All F-06 verdicts carry `is_experimental: true`.

- **Rate limiting is in-process.** `RateLimitMiddleware` stores counters in memory. In a multi-worker deployment, each worker maintains independent counters — deploy a Redis-backed rate limiter (e.g., `slowapi`) for production.

- **ML model files are not tracked in git.** Binary model artifacts (`*.pth`, `*.joblib`, `*.safetensors`) are excluded via `.gitignore`. Re-train using the training scripts in `backend/ml/pipelines/` and `ml/pipelines/`, or download pre-trained artifacts separately.

- **Threat intelligence is simulated.** The phone number lookup (`/protect/check-phone`) uses a simulated response. Integration with a live threat intelligence provider is deferred (ADR-032 is open).

- **DPDP compliance.** Account deletion follows India's Digital Personal Data Protection Act — soft deletion with a grace period and explicit "DELETE MY ACCOUNT" confirmation string requirement.

---

## License

This project is for educational and research purposes.
