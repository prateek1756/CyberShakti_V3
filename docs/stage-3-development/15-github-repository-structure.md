# CyberShakti — GitHub Repository Structure & Directory Organization

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-REPO-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Repository Layout Overview](#1-repository-layout-overview)
2. [Root Level Structure](#2-root-level-structure)
3. [Backend Code Structure (`backend/`)](#3-backend-code-structure-backend)
4. [Frontend Code Structure (`frontend/`)](#4-frontend-code-structure-frontend)
5. [Documentation Directory (`docs/`)](#5-documentation-directory-docs)
6. [ML Pipeline & Model Registry (`ml/`)](#6-ml-pipeline--model-registry-ml)
7. [Branching & Commit Guidelines](#7-branching--commit-guidelines)

---

## 1. Repository Layout Overview

CyberShakti is maintained as a single structured repository containing the complete modular monolith backend, React Vite frontend, ML model training scripts, and architectural documentation.

```
d:\CYBER-SHAKTI-V3\
├── .github/                 # CI/CD Workflows & Issue Templates
├── backend/                 # FastAPI Application & Celery Workers
├── frontend/                # React + Vite SPA Application
├── ml/                      # ML Training Scripts, Datasets, MLflow Config
├── docs/                    # Project Documentation (Stage 1, 2, 3)
├── scripts/                 # Utility & Deployment Scripts
├── docker-compose.yml       # Local Development Orchestration
├── README.md                # Project Root Readme
└── LICENSE                  # License File
```

---

## 2. Root Level Structure

- `.github/workflows/`: CI/CD workflows for testing, linting, and deployment.
- `docker-compose.yml`: Provisions API, Worker, PostgreSQL (with extensions), and Redis.
- `docker-compose.override.yml`: Local overrides for development environment mounting.
- `.env.example`: Template for environment variables (no secret values).

---

## 3. Backend Code Structure (`backend/`)

```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization & gateway routes
│   ├── config.py            # Pydantic v2 settings management
│   ├── detect_analyze/      # Module: F-01 through F-07 implementation
│   ├── protect/             # Module: F-08, F-09, F-10 implementation
│   ├── assist_respond/      # Module: F-11, F-12, F-13 implementation
│   ├── learn_prevent/       # Module: F-14 Implementation
│   ├── users_auth/          # Registration, Login, JWT, TOTP, RBAC
│   ├── shared/              # Shared Utilities (Risk Model, Explanations, Audit Log)
│   └── worker.py            # Celery Worker Entry Point & Task Registration
├── alembic/                 # Database Migration Scripts
│   ├── versions/            # Schema migration versions
│   └── env.py               # Alembic environment config
├── tests/                   # Backend Pytest Suite
│   ├── unit/                # Fast unit tests
│   ├── integration/         # API & DB integration tests
│   └── conftest.py          # Pytest fixtures & setup
├── Dockerfile               # Backend Docker Container definition
├── pyproject.toml           # Poetry / Pip dependency specifications
└── requirements.txt         # Pinned production requirements
```

---

## 4. Frontend Code Structure (`frontend/`)

```
frontend/
├── src/
│   ├── main.jsx             # React entry point
│   ├── App.jsx              # App root & React Router layout
│   ├── components/          # Reusable Design System components
│   │   ├── common/          # Buttons, Inputs, Modals, Cards
│   │   ├── VerdictCard.jsx  # Standardised 5-level verdict card
│   │   └── ProgressRing.jsx # Cyber Risk Score gauge display
│   ├── pages/               # Page-level screen components
│   │   ├── Home.jsx         # Dashboard / Landing
│   │   ├── DetectHub.jsx    # Detect pillar hub
│   │   ├── PhishingScan.jsx # F-01 scan screen
│   │   ├── MessageScan.jsx  # F-02 text scan screen
│   │   ├── FileEncrypt.jsx  # F-10 file encryption screen
│   │   └── RiskScore.jsx    # F-12 Cyber Risk Score screen
│   ├── services/            # Axios API client modules
│   │   ├── api.js           # Base HTTP client with JWT interceptor
│   │   ├── authService.js   # Login, registration, token refresh
│   │   └── detectService.js # Scan submission & task polling
│   ├── context/             # React Context (AuthContext, ThemeContext)
│   └── styles/              # Tailwind CSS imports & global styles
├── public/                  # Static assets (favicon, icons)
├── package.json             # NPM dependencies & scripts
├── vite.config.js           # Vite build configuration
└── tailwind.config.js       # Tailwind CSS design system tokens
```

---

## 5. Documentation Directory (`docs/`)

```
docs/
├── 00-project-constitution.md             # CSHAKTI-CONST-001 (Apex Document)
├── 00-decisions.md                        # Architectural Decision Records (ADRs)
├── stage-1-product-definition/            # Product Definition Docs (PVS, PRD, TRD, SRS)
├── stage-2-engineering-design/            # Technical Specifications (Architecture, DB, API, ML, Security, UX, Threat Model, Privacy)
└── stage-3-development/                   # Implementation Guides (Roadmap, Tasks, Repo, Coding, Test, Deploy, Setup)
```

---

## 6. ML Pipeline & Model Registry (`ml/`)

```
ml/
├── notebooks/               # Data exploration & model prototyping
├── pipelines/               # Training & evaluation scripts
│   ├── train_url_xgboost.py # F-01 model training
│   ├── train_scam_bert.py   # F-02 DistilBERT fine-tuning
│   └── evaluate_models.py   # Evaluation metrics computation
├── data/                    # Local raw/processed datasets (gitignored)
└── mlflow/                  # MLflow experiment tracking config
```

---

## 7. Branching & Commit Guidelines

- `main`: Protected production branch. Deploys automatically to staging/production on merge.
- `feature/[feature-name]`: Individual feature branches (e.g., `feature/f01-url-scanner`).
- `fix/[bug-description]`: Bug fix branches.
- Commit Message Standard: Conventional Commits (`feat: add F-01 scan API endpoint`, `fix: resolve JWT token refresh race condition`).

---

*End of CyberShakti GitHub Repository Structure & Directory Organization — CSHAKTI-REPO-001 v1.0.0*
