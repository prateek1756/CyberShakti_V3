# CyberShakti — Setup & Installation Guide

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-SETUP-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-ENV-001, CSHAKTI-REPO-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [System Prerequisites](#1-system-prerequisites)
2. [Quickstart (Docker Compose)](#2-quickstart-docker-compose)
3. [Manual Local Environment Setup](#3-manual-local-environment-setup)
4. [Database Initialization & Migrations](#4-database-initialization--migrations)
5. [Running Test Suites](#5-running-test-suites)
6. [Troubleshooting Common Setup Issues](#6-troubleshooting-common-setup-issues)

---

## 1. System Prerequisites

Before setting up CyberShakti, ensure your system has the following software installed:

- **Git**: 2.30+
- **Docker & Docker Compose**: Docker Desktop 24+ (with Compose v2)
- **Python**: 3.11.x
- **Node.js**: 18.x or 20.x LTS
- **npm**: 9.x+

---

## 2. Quickstart (Docker Compose)

The fastest way to launch the complete local stack (Backend, Frontend, Postgres with extensions, Redis, and Celery Worker):

```bash
# 1. Clone the repository
git clone https://github.com/cybershakti/cybershakti-v3.git
cd cybershakti-v3

# 2. Create local environment file from template
cp backend/.env.example backend/.env

# 3. Start local Docker Compose stack
docker compose up --build
```

Access services:
- **Frontend SPA**: `http://localhost:5173`
- **FastAPI API**: `http://localhost:8000`
- **Interactive OpenAPI Docs**: `http://localhost:8000/docs`

---

## 3. Manual Local Environment Setup

If running without Docker for local development:

### 3.1 Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create & activate Python 3.11 virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Run FastAPI development server
uvicorn app.main:app --reload --port 8000
```

### 3.2 Celery Worker Setup (Terminal 2)

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
celery -A app.worker.celery_app worker --loglevel=info
```

### 3.3 Frontend Setup (Terminal 3)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```

---

## 4. Database Initialization & Migrations

When running against a fresh PostgreSQL instance, initialize database extensions and run Alembic migrations:

```bash
cd backend

# Apply all database migrations
alembic upgrade head

# Seed initial Cyber Safety Hub content & quiz data (Optional)
python scripts/seed_content.py
```

---

## 5. Running Test Suites

### Backend Unit & Integration Tests:
```bash
cd backend
pytest --cov=app
```

### Frontend Component Tests:
```bash
cd frontend
npm run test:run
```

---

## 6. Troubleshooting Common Setup Issues

| Symptom | Probable Cause | Resolution |
|---|---|---|
| `pgvector extension not found` | Standard Postgres image used instead of `postgis/postgis` | Use `postgis/postgis:15-3.3` Docker image |
| `Celery Connection Refused` | Redis service is not running | Verify Redis is active via `docker compose ps` |
| `CORS Error on Frontend` | `ALLOWED_ORIGINS` in `.env` missing `http://localhost:5173` | Add `http://localhost:5173` to `ALLOWED_ORIGINS` in `backend/.env` |

---

*End of CyberShakti Setup & Installation Guide — CSHAKTI-SETUP-001 v1.0.0*
