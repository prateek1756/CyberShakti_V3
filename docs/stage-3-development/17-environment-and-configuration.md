# CyberShakti — Environment & Configuration Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-ENV-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-SEC-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Configuration Management Strategy](#1-configuration-management-strategy)
2. [Environment Types](#2-environment-types)
3. [Environment Variables Reference](#3-environment-variables-reference)
4. [Secrets Injection & Management](#4-secrets-injection--management)
5. [Docker Environment Orchestration](#5-docker-environment-orchestration)

---

## 1. Configuration Management Strategy

CyberShakti follows the 12-Factor App methodology for configuration. All application configuration is read at startup from environment variables using Pydantic v2 BaseSettings (`app/config.py`).

### Rules:
- **Zero Secrets in Repository**: Secrets must never be hardcoded or committed to git.
- **Fail Early on Missing Config**: Missing mandatory environment variables must cause the application startup to fail with an explicit validation error message.

---

## 2. Environment Types

| Environment | Purpose | Infrastructure Target | Configuration Source |
|---|---|---|---|
| **Development (`dev`)** | Local developer testing | Docker Compose (local host) | Local `.env` file |
| **Staging (`stage`)** | Pre-release integration testing | Cloud Containers (Render / AWS) | Platform Secret Manager |
| **Production (`prod`)** | Production system serving users | Cloud Containers (Vercel + Cloud DB) | Platform Secret Manager |

---

## 3. Environment Variables Reference

### 3.1 Backend Configuration (`backend/app/config.py`)

| Variable Name | Type | Default / Example | Description | Sensitive? |
|---|---|---|---|---|
| `ENVIRONMENT` | string | `dev` | System environment: `dev`, `stage`, `prod` | No |
| `DEBUG` | boolean | `false` | Enable debug logs & Swagger UI | No |
| `PORT` | integer | `8000` | FastAPI server listening port | No |
| `DATABASE_URL` | string | `postgresql+asyncpg://...` | PostgreSQL connection string | **YES** |
| `REDIS_URL` | string | `redis://localhost:6379/0` | Redis Celery broker & cache URL | **YES** |
| `JWT_SECRET_KEY` | string | *Generated 64-byte random* | Secret key for signing JWT tokens | **YES** |
| `JWT_ALGORITHM` | string | `HS256` | Token signing algorithm | No |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | integer | `30` | Access token TTL in minutes | No |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | integer | `7` | Refresh token TTL in days | No |
| `THREAT_INTEL_API_KEY` | string | *API key* | Key for external threat intel API | **YES** |
| `LLM_API_KEY` | string | *API key* | Key for LLM Assistant provider (ADR-013) | **YES** |
| `S3_BUCKET_NAME` | string | `cybershakti-storage` | S3 bucket for media & encrypted files | No |
| `S3_ENDPOINT_URL` | string | `https://s3.amazonaws.com` | S3 API endpoint URL | No |
| `S3_ACCESS_KEY_ID` | string | *Access Key* | AWS/S3 storage access key | **YES** |
| `S3_SECRET_ACCESS_KEY` | string | *Secret Key* | AWS/S3 storage secret key | **YES** |

### 3.2 Frontend Configuration (`frontend/.env`)

| Variable Name | Example Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000/api/v1` | Base URL for FastAPI backend endpoints |
| `VITE_APP_ENV` | `development` | UI environment indicator |

---

## 4. Secrets Injection & Management

- **Local Development**: Managed via `.env` file copied from `.env.example`.
- **CI/CD Pipelines**: Secrets injected into GitHub Actions via GitHub Repository Secrets (`${{ secrets.JWT_SECRET_KEY }}`).
- **Production Deployment**: Secrets injected directly into container environment by the hosting provider's Secret Management service.

---

## 5. Docker Environment Orchestration

Local development environment is orchestrated via `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: cybershakti_db
      POSTGRES_USER: cybershakti_user
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    env_file: ./backend/.env
    depends_on:
      - postgres
      - redis

  worker:
    build: ./backend
    command: celery -A app.worker.celery_app worker --loglevel=info
    volumes:
      - ./backend:/app
    env_file: ./backend/.env
    depends_on:
      - redis
      - postgres
```

---

*End of CyberShakti Environment & Configuration Specification — CSHAKTI-ENV-001 v1.0.0*
