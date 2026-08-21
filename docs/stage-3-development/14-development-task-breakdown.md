# CyberShakti — Development Task Breakdown

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-IMPL-002 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-IMPL-001, CSHAKTI-SYS-001, CSHAKTI-SRS-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Task Breakdown Structure](#1-task-breakdown-structure)
2. [Module 1: Infrastructure & Data Engineering Tasks](#2-module-1-infrastructure--data-engineering-tasks)
3. [Module 2: Authentication & User Management Tasks](#3-module-2-authentication--user-management-tasks)
4. [Module 3: Detect & Analyze Service Tasks](#4-module-3-detect--analyze-service-tasks)
5. [Module 4: Protect Service Tasks](#5-module-4-protect-service-tasks)
6. [Module 5: Assist & Respond Service Tasks](#6-module-5-assist--respond-service-tasks)
7. [Module 6: Learn & Prevent Service Tasks](#7-module-6-learn--prevent-service-tasks)
8. [Module 7: Frontend Application Tasks](#8-module-7-frontend-application-tasks)

---

## 1. Task Breakdown Structure

All development tasks are uniquely identified using the scheme `TASK-[MODULE]-[NUMBER]`. Tasks include effort estimates, dependencies, and verification criteria.

---

## 2. Module 1: Infrastructure & Data Engineering Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-INFRA-01` | Setup Docker Compose environment (FastAPI, Redis, Postgres, Celery) | 1 day | None | `docker compose up` starts all 4 services healthy |
| `TASK-INFRA-02` | Configure PostgreSQL database with `pgvector` and `PostGIS` extensions | 0.5 day | TASK-INFRA-01 | Extensions enabled and queryable via SQL |
| `TASK-INFRA-03` | Create initial Alembic database migrations for core tables | 1.5 days | TASK-INFRA-02 | `alembic upgrade head` applies cleanly without error |
| `TASK-INFRA-04` | Setup Redis broker & Celery worker task dispatch harness | 1 day | TASK-INFRA-01 | Sample async ping/pong Celery task succeeds |

---

## 3. Module 2: Authentication & User Management Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-AUTH-01` | Implement user registration endpoint with consent validation (`/auth/register`) | 1 day | TASK-INFRA-03 | Creates unverified user in DB; rejects missing consent |
| `TASK-AUTH-02` | Implement password hashing using Argon2id (`app/shared/security.py`) | 0.5 day | TASK-INFRA-03 | Passes unit test verifying Argon2id format & timing |
| `TASK-AUTH-03` | Implement login endpoint issuing JWT access & refresh tokens (`/auth/login`) | 1.5 days | TASK-AUTH-01 | Returns valid JWT pair on correct credentials |
| `TASK-AUTH-04` | Implement optional TOTP 2FA enrollment and verification (`/auth/2fa/*`) | 2 days | TASK-AUTH-03 | QR code generated; TOTP code validates successfully |
| `TASK-AUTH-05` | Implement JWT authentication & RBAC middleware (`app/middleware/auth.py`) | 1 day | TASK-AUTH-03 | Protects routes; returns 401 unauthenticated / 403 forbidden |

---

## 4. Module 3: Detect & Analyze Service Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-DET-01` | Build F-01 URL feature engineering extractor (`app/detect_analyze/url.py`) | 1.5 days | TASK-INFRA-03 | Extracts lexical, domain, and TLD features correctly |
| `TASK-DET-02` | Build F-01 Phishing URL scan endpoint with XGBoost model inference | 2 days | TASK-DET-01 | Returns 5-level verdict + explanation object |
| `TASK-DET-03` | Build F-02 Scam Text DistilBERT NLP inference handler in Celery worker | 2.5 days | TASK-INFRA-04 | Classifies sample scam text with confidence score |
| `TASK-DET-04` | Build F-03 Screenshot OCR processing pipeline using PaddleOCR | 3 days | TASK-DET-03 | Extracts text from image and passes to F-02 text pipeline |
| `TASK-DET-05` | Build F-04 QR Code decoder and URL router (`/detect/scan-qr`) | 1 day | TASK-DET-02 | Decodes QR image; routes contained URL to F-01 pipeline |
| `TASK-DET-06` | Build F-05 Fake Profile risk assessor (`/detect/assess-profile`) | 2 days | TASK-INFRA-04 | Evaluates observable profile signals with disclaimer |
| `TASK-DET-07` | Build F-06 Deepfake Detection experimental pipeline (PyTorch + OpenCV) | 3 days | TASK-INFRA-04 | Detects human faces in image/video; returns score |
| `TASK-DET-08` | Build F-07 Mule Account Detection experimental pipeline (NetworkX + XGBoost) | 2.5 days | TASK-INFRA-04 | Computes graph features; returns risk verdict |

---

## 5. Module 4: Protect Service Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-PROT-01` | Implement F-08 Scam Call phone lookup service (`/protect/check-phone`) | 1 day | TASK-INFRA-03 | Returns threat status or emergency number response |
| `TASK-PROT-02` | Implement F-09 Password entropy & breach checking (`/protect/check-password`) | 1 day | None | Evaluates length/entropy without persisting input |
| `TASK-PROT-03` | Implement F-10 AES-256-GCM streaming encryption/decryption module | 2.5 days | None | Encrypts and decrypts files with derived Argon2id key |

---

## 6. Module 5: Assist & Respond Service Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-AST-01` | Implement F-12 Cyber Risk Score weighted calculation engine | 2 days | TASK-INFRA-03 | Returns 0-100 score + signal breakdown list |
| `TASK-AST-02` | Implement F-13 PostGIS local scam alert query service | 1.5 days | TASK-INFRA-02 | Returns nearby alerts by city/geo coordinates |
| `TASK-AST-03` | Implement F-11 RAG pipeline (pgvector search + prompt assembly) | 3 days | TASK-INFRA-02 | Retrieves top-k chunks & queries LLM provider |

---

## 7. Module 6: Learn & Prevent Service Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-LRN-01` | Implement F-14 Cyber Safety Hub content APIs (Daily Tip, Articles) | 1 day | TASK-INFRA-03 | Returns active daily tip and paginated articles |
| `TASK-LRN-02` | Implement F-14 Cybersecurity Quiz submission & evaluation API | 1 day | TASK-INFRA-03 | Evaluates selected answer and returns explanation |

---

## 8. Module 7: Frontend Application Tasks

| Task ID | Task Description | Est. Effort | Dependencies | Acceptance Criteria |
|---|---|---|---|---|
| `TASK-FE-01` | Setup Vite + React + Tailwind CSS project structure & routing | 1 day | None | SPA builds cleanly; navigation routes working |
| `TASK-FE-02` | Implement Design System component library (Button, Input, VerdictCard, Modal) | 2 days | TASK-FE-01 | Components pass WCAG AA contrast & storybook tests |
| `TASK-FE-03` | Implement Auth screens (Login, Register, 2FA prompt, Password Reset) | 2 days | TASK-AUTH-03 | Full login/registration user flow operational |
| `TASK-FE-04` | Implement Pillar 1 Detect & Analyze UI screens (F-01 through F-07) | 4 days | TASK-DET-02 | Form submission, polling, and verdict rendering work |
| `TASK-FE-05` | Implement Pillar 2 Protect UI screens (F-08, F-09, F-10 file encrypt) | 2.5 days | TASK-PROT-03 | File upload/download streaming encryption UI functional |
| `TASK-FE-06` | Implement Pillar 3 Assist UI screens (F-11 Chat, F-12 Risk Score Ring, F-13 Alerts) | 3 days | TASK-AST-01 | Risk score gauge renders; AI chat interface operational |
| `TASK-FE-07` | Implement Pillar 4 Learn UI screens (F-14 Daily Tip, Quiz UI, Articles) | 2 days | TASK-LRN-02 | Quiz question flow & answer reveal functional |

---

*End of CyberShakti Development Task Breakdown — CSHAKTI-IMPL-002 v1.0.0*
