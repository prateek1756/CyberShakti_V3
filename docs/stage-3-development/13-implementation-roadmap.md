# CyberShakti — Implementation Roadmap

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-IMPL-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-SRS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Implementation Strategy](#1-implementation-strategy)
2. [Phase 1 Execution Milestones](#2-phase-1-execution-milestones)
3. [Component Development Sequence](#3-component-development-sequence)
4. [Critical Path & Dependencies](#4-critical-path--dependencies)
5. [Feature Rollout Matrix](#5-feature-rollout-matrix)

---

## 1. Implementation Strategy

CyberShakti follows an iterative, component-driven implementation roadmap. Development is structured around building core infrastructure first (Auth, DB, Base API Gateway), followed by Pillar 1 Detect & Analyze core MVP features, then Pillar 2 Protect, Pillar 3 Assist & Respond, and Pillar 4 Learn & Prevent.

### Core Principles:
- **Baseline First**: Basic functional rule/heuristic endpoints deployed before ML pipeline integration.
- **Async Isolation**: Heavy tasks isolated via Celery workers from day one.
- **Continuous Integration**: Test suites and linting run on every pull request.

---

## 2. Phase 1 Execution Milestones

```
Milestone 0: Foundation Setup (Weeks 1-2)
  ├── Repo structure & Docker environment
  ├── Database migrations (PostgreSQL + pgvector + PostGIS)
  └── Auth & User Management module

Milestone 1: Core Detection MVP (Weeks 3-5)
  ├── F-01 Phishing Link Scanner
  ├── F-02 Message & Email Scam Detection
  ├── F-03 Screenshot Scam Scanner
  └── F-04 QR Code Scam Scanner

Milestone 2: Protection Pillar & Infrastructure (Weeks 6-7)
  ├── F-08 Scam Call Blocking (Lookup)
  ├── F-09 Password Security Checker
  └── F-10 Secure File Encryption (AES-256-GCM)

Milestone 3: Assist, Respond & Learn (Weeks 8-9)
  ├── F-12 Cyber Risk Score Engine
  ├── F-13 Location Scam Alerts
  ├── F-14 Cyber Safety Hub
  └── F-11 AI Assistant (Pending ADR-013)

Milestone 4: Experimental Features & Hardening (Weeks 10-11)
  ├── F-05 Fake Profile Verification
  ├── F-06 Deepfake Detection (Research)
  ├── F-07 Mule Account Detection (Research)
  └── E2E Testing & Security Audit Sign-off
```

---

## 3. Component Development Sequence

### Step 1: Core Framework & Shared Kernel
- Setup FastAPI project structure (`app/main.py`, `app/shared/`).
- Configure Pydantic v2 settings and environment management.
- Implement database connection pool and base Alembic migrations (`users`, `refresh_tokens`, `audit_log`).
- Build JWT authentication and RBAC middleware.

### Step 2: Detection Service & Celery Infrastructure
- Provision Redis broker container.
- Implement Celery task worker bootstrap.
- Build F-01 URL feature extractor and threat intel client.
- Integrate DistilBERT inference handler into Celery worker for F-02 text scan.
- Integrate PaddleOCR pipeline for F-03 screenshot processing.

### Step 3: Protection & Security Features
- Implement F-09 password entropy & breach check engine.
- Implement F-10 streaming AES-256-GCM encryption & Argon2id KDF pipeline.
- Build F-08 phone number threat list lookup service.

### Step 4: Assistant & Community Features
- Implement F-12 weighted Cyber Risk Score engine.
- Implement F-13 PostGIS geospatial query handler for local alerts.
- Build F-14 Cyber Safety Hub content endpoints and quiz engine.
- Integrate F-11 RAG pipeline (pgvector similarity search + LLM provider integration once ADR-013 resolves).

---

## 4. Critical Path & Dependencies

```
[DB & Auth Setup] ──► [API Gateway Middleware]
                             │
                             ├──► [F-01 URL Scan] ──► [F-04 QR Code Scanner]
                             ├──► [Celery Worker] ──► [F-02 Text Scan] ──► [F-03 Screenshot Scan]
                             ├──► [F-10 AES Encryption Pipeline]
                             └──► [F-12 Cyber Risk Score Engine] ◄── (Consumes scan history)
```

- **Blocker 1**: Celery + Redis must be operational before F-03, F-05, F-06, F-07 development.
- **Blocker 2**: ADR-013 (LLM provider) must be resolved before F-11 AI Assistant completion.

---

## 5. Feature Rollout Matrix

| Feature | Milestone Target | Release Tier | Blocker / Dependency |
|---|---|---|---|
| **F-01** Phishing Link Scanning | Milestone 1 | Core MVP | Threat Intel API (ADR-032) |
| **F-02** Message & Email Scam | Milestone 1 | Core MVP | DistilBERT weights |
| **F-03** Screenshot Scanner | Milestone 1 | Core MVP | PaddleOCR, Celery |
| **F-04** QR Code Scanner | Milestone 1 | Core MVP | F-01 Pipeline |
| **F-05** Fake Profile Verification | Milestone 4 | Advanced MVP | Signal dataset |
| **F-06** Deepfake Detection | Milestone 4 | Experimental | PyTorch / GPU worker |
| **F-07** Mule Account Detection | Milestone 4 | Experimental | NetworkX / Elliptic data |
| **F-08** Scam Call Blocking | Milestone 2 | Core MVP | Phone threat database |
| **F-09** Password Security Checker | Milestone 2 | Core MVP | None |
| **F-10** Secure File Encryption | Milestone 2 | Core MVP | Argon2id KDF |
| **F-11** AI Cybersecurity Assistant | Milestone 3 | Core MVP | ADR-013 (LLM Provider) |
| **F-12** Cyber Risk Score | Milestone 3 | Core MVP | Scan History schema |
| **F-13** Location Scam Alerts | Milestone 3 | Core MVP | PostGIS Extension |
| **F-14** Cyber Safety Hub | Milestone 3 | Core MVP | Content curation |

---

*End of CyberShakti Implementation Roadmap — CSHAKTI-IMPL-001 v1.0.0*
