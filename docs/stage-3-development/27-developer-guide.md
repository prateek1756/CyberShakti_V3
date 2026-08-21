# CyberShakti — Developer Onboarding & Architecture Guide

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-DEV-002 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-DEV-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Welcome to CyberShakti](#1-welcome-to-cybershakti)
2. [Architecture Mental Model](#2-architecture-mental-model)
3. [Key Code Patterns & Examples](#3-key-code-patterns--examples)
4. [Adding a New Detection Feature](#4-adding-a-new-detection-feature)
5. [Working with Database & Alembic](#5-working-with-database--alembic)
6. [Working with Async Celery Tasks](#6-working-with-async-celery-tasks)
7. [Submitting a Pull Request](#7-submitting-a-pull-request)

---

## 1. Welcome to CyberShakti

Welcome to the CyberShakti engineering team! CyberShakti is an AI-powered cybersecurity platform designed to protect Indian citizens from digital threats, scams, and cyber fraud.

This guide provides developers with the essential mental models, architectural patterns, and step-by-step workflows required to contribute code effectively.

---

## 2. Architecture Mental Model

CyberShakti is built as a **Modular Monolith** (FastAPI) backed by **Celery Async Workers** (Redis) and **PostgreSQL 15+** (with `pgvector` & `PostGIS`).

```
  [ Frontend React SPA ]
           │
           │ REST HTTP Requests (JWT Auth)
           ▼
  [ FastAPI Gateway: app/main.py ]
           │
           ├──► [ Module Route Handlers ]
           │    ├── app/detect_analyze/
           │    ├── app/protect/
           │    ├── app/assist_respond/
           │    └── app/learn_prevent/
           │
           ├──► [ Synchronous Heavy Work ] ──► [ Redis Task Queue ]
           │                                          │
           │                                          ▼
           │                                [ Celery Worker: app/worker.py ]
           │                                (ML Inference & Heavy Pipeline)
           │
           └──► [ Database Queries (Async SQLAlchemy) ] ──► [ PostgreSQL 15+ ]
```

---

## 3. Key Code Patterns & Examples

### 3.1 Standard API Handler Pattern

All API handlers follow this structure:

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.auth import get_current_user
from app.shared.database import get_db
from app.detect_analyze.schemas import ScanURLRequest, ScanURLResponse

router = APIRouter(prefix="/detect", tags=["detect"])

@router.post("/scan-url", response_model=ScanURLResponse)
async def scan_url(
    payload: ScanURLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # 1. Validate & process
    result = await process_url_scan(db, current_user.id, payload.url)
    
    # 2. Return validated Pydantic response
    return result
```

---

## 4. Adding a New Detection Feature

To add a new feature (e.g., a new threat analyzer):

1. **Define Schema**: Add Pydantic request/response models in `app/detect_analyze/schemas.py`.
2. **Implement Business Logic**: Add core processing logic in `app/detect_analyze/services.py`.
3. **Register Celery Task (If heavy ML)**: Define task function in `app/worker.py`.
4. **Create API Endpoint**: Add route handler in `app/detect_analyze/router.py`.
5. **Add Unit Tests**: Add Pytest unit and integration tests in `backend/tests/`.
6. **Update Frontend UI**: Implement React component & Axios call in `frontend/src/pages/`.

---

## 5. Working with Database & Alembic

### Creating a New Model
Add SQLAlchemy model class to the appropriate module's `models.py` file.

### Generating a Migration
```bash
cd backend
alembic revision --autogenerate -m "add_scam_alert_indexes"
```

### Applying Migrations
```bash
alembic upgrade head
```

---

## 6. Working with Async Celery Tasks

Dispatching a task from an API handler:

```python
from app.worker import analyze_screenshot_task

# Dispatch task asynchronously
task = analyze_screenshot_task.delay(job_id=str(job.id), file_path=s3_path)

# Return task ID to client for polling
return {"task_id": task.id, "status": "queued"}
```

---

## 7. Submitting a Pull Request

1. Branch off `main`: `git checkout -b feature/my-new-feature`.
2. Run linters & tests locally:
   ```bash
   cd backend && ruff check . && pytest
   cd ../frontend && npm run lint && npm run test:run
   ```
3. Push branch and create a Pull Request on GitHub.
4. Verify all GitHub Actions checks pass before requesting review.

---

*End of CyberShakti Developer Onboarding & Architecture Guide — CSHAKTI-DEV-002 v1.0.0*
