# CyberShakti — System Architecture

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-SYS-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-TRD-001, CSHAKTI-SRS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Architectural Pattern](#1-architectural-pattern)
2. [System Component Overview](#2-system-component-overview)
3. [Detailed Component Specifications](#3-detailed-component-specifications)
4. [Synchronous vs. Asynchronous Operation Model](#4-synchronous-vs-asynchronous-operation-model)
5. [Data Flow Summary](#5-data-flow-summary)
6. [Inter-Component Communication](#6-inter-component-communication)
7. [Deployment Topology](#7-deployment-topology)
8. [Scalability Considerations](#8-scalability-considerations)
9. [Failure Modes and Resilience](#9-failure-modes-and-resilience)
10. [Open Architecture Decisions](#10-open-architecture-decisions)

---

## 1. Architectural Pattern

### 1.1 Decision

**Modular Monolith + Isolated AI/ML Workers via Celery** (ADR-014, CSHAKTI-CONST-001 §7.1)

The CyberShakti Phase 1 backend is a **single deployable unit** — one FastAPI application process — internally structured into well-defined modules aligned to the four product pillars. This is not a microservices architecture. The modules share a process, a database connection pool, and a codebase. They are separated at the Python package level, not at the network boundary level.

The one genuine isolation is for **heavy ML inference workloads**: these are dispatched as async tasks to Celery workers via a Redis broker. This prevents computationally expensive inference from blocking the synchronous API response path.

### 1.2 Why This Pattern

| Concern | How Modular Monolith Addresses It |
|---|---|
| Development simplicity | Single codebase, one deploy unit, no distributed systems overhead |
| Testability | Modules are independently testable at the unit and integration level |
| ML isolation | Celery + Redis handles the one genuine isolation need without microservices |
| Future decomposition | Clear module boundaries enable future extraction to services if required |
| Team size appropriateness | Modular monolith is the right architecture for a Phase 1 build with a small team |

### 1.3 What This Is Not

- **Not microservices:** There are no separate services for each pillar or feature in Phase 1.
- **Not serverless:** The ASGI server runs persistently; cold-start latency is incompatible with ML inference.
- **Not an event-driven system:** Celery tasks are dispatched synchronously from API handlers; there is no message bus.

---

## 2. System Component Overview

```
┌────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                               │
│                                                                    │
│   React + Vite SPA (Responsive Web Application)                   │
│   Tailwind CSS | Framer Motion | React Router | Axios | Recharts  │
│   Deployment: Vercel (CDN-distributed)                             │
└───────────────────────────────┬────────────────────────────────────┘
                                │ HTTPS / REST / JSON
                                │ (All traffic over TLS 1.2+)
┌───────────────────────────────▼────────────────────────────────────┐
│                        API GATEWAY LAYER                           │
│                                                                    │
│   FastAPI + Uvicorn (ASGI)                                         │
│   ├── JWT Authentication Middleware (all protected routes)         │
│   ├── RBAC Authorisation Middleware (role enforcement)             │
│   ├── Input Validation (Pydantic v2 schema validation)             │
│   ├── Rate Limiting Middleware (thresholds TBD — ADR-026)          │
│   ├── CORS Middleware (restrictive origin policy)                  │
│   └── Request/Response Logging Middleware                          │
└───┬────────────┬─────────────┬─────────────┬──────────────────────┘
    │            │             │             │
┌───▼──────┐ ┌──▼──────┐ ┌───▼──────┐ ┌───▼───────────────────────┐
│ detect_  │ │ protect │ │ assist_  │ │ users_auth                 │
│ analyze  │ │ module  │ │ respond  │ │                            │
│ module   │ │         │ │ module   │ │ learn_prevent module       │
│          │ │ F-08    │ │          │ │                            │
│ F-01,02  │ │ F-09    │ │ F-11     │ │ F-14 (Cyber Safety Hub)   │
│ F-03,04  │ │ F-10    │ │ F-12     │ │ Registration / Login       │
│ F-05,06  │ │         │ │ F-13     │ │ 2FA / Password Reset       │
│ F-07     │ │         │ │          │ │ Account Deletion           │
└───┬───┬──┘ └───┬─────┘ └────┬─────┘ └──────────────┬────────────┘
    │   │        │            │                       │
    └───┴────────┴────────────┴───────────────────────┘
                              │
              ┌───────────────▼──────────────────────┐
              │     shared module                     │
              │                                       │
              │ - Risk severity model (5 levels)      │
              │ - Explanation engine                  │
              │ - Threat intelligence client          │
              │   (ADR-032 TBD)                       │
              │ - Celery task dispatch utilities      │
              │ - Audit logging                       │
              │ - Error handling utilities            │
              └───────────────┬──────────────────────┘
                              │
              ┌───────────────▼──────────────────────┐
              │     CELERY ASYNC TASK LAYER           │
              │                                       │
              │  Broker: Redis                        │
              │                                       │
              │  Task Workers:                        │
              │  - PhishingURLAnalyzer (F-01 heavy)   │
              │  - ScamTextClassifier (F-02, F-03)    │
              │  - OCRPipeline (F-03 PaddleOCR)       │
              │  - FakeProfileAssessor (F-05)         │
              │  - DeepfakeDetector (F-06) [Exp]      │
              │  - MuleAccountDetector (F-07) [Exp]   │
              │  - AIAssistantRAG (F-11)              │
              └───────────────┬──────────────────────┘
                              │
              ┌───────────────▼──────────────────────┐
              │           DATA LAYER                  │
              │                                       │
              │  PostgreSQL 15+ (single database)     │
              │  ├── pgvector extension               │
              │  │   (F-11 knowledge base embeddings) │
              │  └── PostGIS extension                │
              │      (F-13 geospatial queries)        │
              │                                       │
              │  Redis 7+ (dual role)                 │
              │  ├── Celery broker (task queue)       │
              │  └── Application cache                │
              └───────────────┬──────────────────────┘
                              │
              ┌───────────────▼──────────────────────┐
              │        STORAGE LAYER                  │
              │                                       │
              │  S3-compatible object storage         │
              │  Provider: TBD (ADR-031 Open)         │
              │                                       │
              │  Stores:                              │
              │  - F-10: Encrypted user files         │
              │  - F-03: Uploaded screenshots         │
              │  - F-04: Uploaded QR code images      │
              │  - F-06: Uploaded media files         │
              │  - MLflow: Model artefacts            │
              └───────────────┬──────────────────────┘
                              │
              ┌───────────────▼──────────────────────┐
              │       EXTERNAL SERVICES               │
              │                                       │
              │  Threat Intelligence API              │
              │  (ADR-032 — provider TBD)             │
              │                                       │
              │  LLM API                              │
              │  (ADR-013 — provider TBD)             │
              │                                       │
              │  Email delivery service               │
              │  (for verification/reset emails)      │
              └──────────────────────────────────────┘
```

---

## 3. Detailed Component Specifications

### 3.1 Client Layer — React SPA

| Property | Value |
|---|---|
| Framework | React 18+ with Vite build tool |
| Styling | Tailwind CSS |
| Animation | Framer Motion |
| Routing | React Router v6+ |
| API communication | Axios (REST over HTTPS) |
| Data visualisation | Recharts (Cyber Risk Score display) |
| Deployment | Vercel (CDN edge delivery) |
| Auth token storage | httpOnly cookies preferred over localStorage for JWT storage (security consideration — to be confirmed during security architecture design) |

**Responsibilities:**
- Render all user-facing screens for all 14 features
- Handle client-side routing and navigation
- Submit API requests with JWT in `Authorization` header
- Poll for Celery task results for async operations
- Display risk verdicts, explanations, and disclaimers
- Handle file upload progress and download for F-10

**Does NOT:**
- Store sensitive data locally beyond current session context
- Perform ML inference (all inference is server-side)
- Bypass API validation

### 3.2 API Gateway Layer — FastAPI

| Property | Value |
|---|---|
| Framework | FastAPI |
| ASGI server | Uvicorn (workers: TBD based on deployment target) |
| Data validation | Pydantic v2 |
| Auth | JWT middleware on all protected routes |
| Documentation | Auto-generated OpenAPI docs (`/docs` endpoint) — disabled in production or restricted to internal access |

**Middleware Stack (execution order):**
1. HTTPS termination (at load balancer / reverse proxy level)
2. CORS middleware — restrictive origin list
3. Rate limiting middleware — applied before route handlers
4. JWT authentication middleware — validates token, populates request context
5. RBAC authorisation — checks role claim against route requirements
6. Input validation — Pydantic schemas enforce structure and types
7. Request logging middleware — logs request ID, endpoint, user ID (no PII in logs)
8. Route handler execution

### 3.3 Backend Modules

Each module is a Python package within the FastAPI application. Modules do not import from each other's internals — only from the `shared` module. Cross-module data access goes through the shared data access layer.

| Module | Package Path | Features | Key Responsibilities |
|---|---|---|---|
| `detect_analyze` | `app/detect_analyze/` | F-01, F-02, F-03, F-04, F-05, F-06, F-07 | URL feature extraction, scam text preprocessing, file validation, Celery task dispatch for heavy inference |
| `protect` | `app/protect/` | F-08, F-09, F-10 | Phone number lookup, password entropy evaluation, file encrypt/decrypt, AES-256-GCM implementation |
| `assist_respond` | `app/assist_respond/` | F-11, F-12, F-13 | RAG pipeline orchestration, risk score computation, geospatial alert queries |
| `learn_prevent` | `app/learn_prevent/` | F-14 | Serving tips, quiz, articles from database |
| `users_auth` | `app/users_auth/` | Auth flows | Registration, login, 2FA, password reset, account deletion, JWT issuance |
| `shared` | `app/shared/` | All | Risk model, explanation engine, threat intelligence client, Celery utilities, error handling, audit log |

### 3.4 Celery Async Task Layer

| Property | Value |
|---|---|
| Task queue | Celery |
| Broker | Redis |
| Result backend | Redis (or PostgreSQL — to be decided during environment design) |
| Worker concurrency | TBD based on deployment target resources |
| Task acknowledgement | Workers ack after task begins processing (at-least-once semantics) |

**Task registry:**

| Task Name | Triggered by | Heavy Because | Feature |
|---|---|---|---|
| `analyze_url_phishing` | F-01 (when ML inference needed) | XGBoost inference + TI lookup | F-01 |
| `classify_scam_text` | F-02, F-03 (post-OCR) | DistilBERT transformer inference | F-02, F-03 |
| `run_screenshot_ocr` | F-03 | PaddleOCR on image | F-03 |
| `assess_fake_profile` | F-05 | XGBoost + signal aggregation | F-05 |
| `detect_deepfake` | F-06 | EfficientNet/Xception CNN inference | F-06 |
| `detect_mule_account` | F-07 | NetworkX graph computation + XGBoost | F-07 |
| `query_ai_assistant` | F-11 | LLM API call + pgvector similarity search | F-11 |

**Task result polling pattern (Phase 1):**
Client submits request → API returns `{task_id: "...", status: "queued"}` → Client polls `GET /tasks/{task_id}/status` every N seconds → API returns result when complete.

Push notification (WebSocket or SSE) is **not in Phase 1 scope** but is the preferred long-term pattern.

### 3.5 Data Layer

#### PostgreSQL

Single database instance with extensions (ADR-005).

| Extension | Purpose | Feature |
|---|---|---|
| pgvector | Vector similarity search for knowledge base | F-11 |
| PostGIS | Geospatial point/polygon queries for location alerts | F-13 |

Connection pooling: PgBouncer or SQLAlchemy built-in pool — to be specified during environment design.

#### Redis

Dual-purpose service:
1. **Celery broker:** Routes tasks between API dispatch and worker consumption
2. **Application cache:** Caches threat intelligence lookup results, frequently accessed content, rate-limit counters

Redis is **not** a primary data store. No user data or scan results are stored only in Redis.

### 3.6 Storage Layer

S3-compatible object storage for binary objects that are not suited to PostgreSQL storage (provider TBD — ADR-031).

| Object Type | Bucket / Prefix | Retention | Access |
|---|---|---|---|
| Encrypted user files (F-10) | `user-files/{user_id}/encrypted/` | Until user deletes or account deleted | Presigned URL with expiry |
| Screenshot uploads (F-03) | `scan-uploads/screenshots/{job_id}/` | Deleted after processing | Internal only |
| QR code images (F-04) | `scan-uploads/qrcodes/{job_id}/` | Deleted after processing | Internal only |
| Deepfake media (F-06) | `scan-uploads/deepfake/{job_id}/` | Deleted after processing | Internal only |
| MLflow model artefacts | `mlflow-artefacts/` | Retained per MLflow versioning | Internal / MLflow only |

All user-uploaded media is **deleted from object storage after processing** — it is not retained for model retraining without explicit consent.

---

## 4. Synchronous vs. Asynchronous Operation Model

The API exposes two patterns to the frontend depending on the weight of the operation:

### Pattern A — Synchronous Response

Used for operations that complete within the API request lifecycle.

```
Client → POST /api/v1/protect/password-check
         → FastAPI validates input
         → Password entropy evaluated in-process
         → Response returned in same HTTP cycle
Client ← { verdict, explanation, disclaimer }
```

Features using Pattern A: F-08, F-09, F-12 (read), F-13, F-14, Auth flows, F-02 (fast path for short messages).

### Pattern B — Async Task Pattern

Used for heavy ML inference that cannot complete within an acceptable synchronous HTTP timeout.

```
Client → POST /api/v1/detect/screenshot-scan
         → FastAPI validates file, stores to S3
         → Dispatches Celery task: run_screenshot_ocr
         → Returns immediately
Client ← { task_id: "abc-123", status: "queued" }

Client → GET /api/v1/tasks/abc-123/status  [polls every 3–5 seconds]
         → Celery worker completes OCR + NLP
         → Result stored in Redis / DB
Client ← { status: "complete", result: { verdict, explanation, ... } }
```

Features using Pattern B: F-03, F-05, F-06, F-07, F-11.

---

## 5. Data Flow Summary

### 5.1 URL Scan (F-01) — Synchronous ML Path

```
1. User submits URL via React frontend
2. Frontend → POST /api/v1/detect/scan-url (JWT in header)
3. FastAPI: validate JWT, validate URL format
4. detect_analyze module:
   a. Parse URL into components
   b. Check against threat intelligence API (shared.threat_intel_client)
   c. Extract URL features (lexical, domain, path)
   d. Run XGBoost classifier
   e. Aggregate TI result + ML score → risk level
   f. Generate plain-language explanation
5. Log scan record to PostgreSQL (scan_history table)
6. Update Cyber Risk Score signals
7. Return response: { risk_level, explanation, confidence, disclaimer }
8. Frontend displays verdict with colour-coded severity indicator
```

### 5.2 Scam Text Check (F-02) — Synchronous NLP Path

```
1. User pastes message text
2. POST /api/v1/detect/scan-message
3. FastAPI: validate JWT, validate non-empty text
4. detect_analyze module:
   a. Detect language (flag if non-English)
   b. Preprocess text (clean, truncate to model max tokens)
   c. Run DistilBERT classifier
   d. Generate risk level from probability score
   e. Generate explanation (scam category hint if confidence sufficient)
5. Log to scan_history
6. Update Risk Score signals
7. Return response
```

### 5.3 Screenshot Scan (F-03) — Async Path

```
1. User uploads screenshot image
2. POST /api/v1/detect/scan-screenshot (multipart/form-data)
3. FastAPI: validate JWT, validate file type/size
4. Store file to S3 (scan-uploads/screenshots/{job_id}/)
5. Dispatch Celery task: run_screenshot_ocr(job_id)
6. Return: { task_id, status: "queued" }

[Worker]
7. Download image from S3
8. Run PaddleOCR → extracted text
9. Dispatch sub-task: classify_scam_text(text, job_id)
10. DistilBERT classifies text
11. Generate verdict and explanation
12. Store result in DB (scan_results table)
13. Delete image from S3

[Frontend polling]
14. GET /api/v1/tasks/{task_id}/status
15. Returns complete result when available
```

### 5.4 File Encryption (F-10) — Streaming Pattern

```
1. User uploads file + encryption password
2. POST /api/v1/protect/encrypt-file
3. FastAPI: validate JWT, validate file, validate password non-empty
4. Stream file through encryption:
   a. Generate fresh random nonce (96-bit for AES-256-GCM)
   b. Derive key from password using Argon2id
   c. Encrypt using AES-256-GCM
   d. Append authentication tag
5. Return encrypted file as stream (direct download)
6. Plaintext file content NEVER written to disk or S3
```

---

## 6. Inter-Component Communication

### 6.1 Frontend ↔ Backend

- **Protocol:** HTTPS REST (JSON request/response bodies)
- **Authentication:** JWT `Authorization: Bearer <token>` header on all protected requests
- **File transfers:** `multipart/form-data` for uploads; `application/octet-stream` for encrypted file downloads
- **Error responses:** Consistent error envelope: `{ error_code, message, details (optional) }`

### 6.2 FastAPI ↔ Celery

- **Dispatch:** Celery `.delay()` or `.apply_async()` called from API handler
- **Broker:** Redis pub/sub queue
- **Result retrieval:** Task status polled via API (`GET /tasks/{task_id}/status`)
- **Serialisation:** JSON (celery task arguments and results)

### 6.3 Backend ↔ PostgreSQL

- **ORM:** SQLAlchemy (async mode) or direct async driver (asyncpg) — to be decided during implementation setup
- **Connection management:** Connection pool (size TBD based on deployment target)
- **Migrations:** Alembic

### 6.4 Backend ↔ Redis

- **Cache client:** redis-py or aioredis (async)
- **Celery broker:** Managed by Celery configuration
- **Cache patterns:** Cache-aside (application fetches from DB, writes to cache on miss)

### 6.5 Backend ↔ S3 Storage

- **Client:** boto3 (S3-compatible API)
- **Access pattern:** Presigned URLs for user-facing downloads; direct S3 API calls from backend for internal operations
- **No provider-specific features:** All access uses S3-compatible API only (ADR-031)

### 6.6 Backend ↔ External Services

| Service | Protocol | Auth | Data Sent |
|---|---|---|---|
| Threat Intelligence API | HTTPS REST | API key | URL, phone number (no user PII) |
| LLM API | HTTPS REST | API key | Sanitised user query + retrieved context |
| Email service | SMTP / API | API key | Verification/reset email content |

---

## 7. Deployment Topology

### 7.1 Frontend Deployment

| Item | Value |
|---|---|
| Platform | Vercel |
| Distribution | CDN edge nodes (global) |
| Build trigger | GitHub Actions on merge to main |
| Environment variables | `VITE_API_BASE_URL`, `VITE_APP_ENV` |

### 7.2 Backend Deployment

| Item | Value |
|---|---|
| Platform | Render / Railway / AWS — TBD (ADR-004 consequence) |
| Containerisation | Docker |
| ASGI server | Uvicorn behind a reverse proxy |
| Environment configuration | Environment variables (no secrets in codebase) |

**Backend deployment units:**
- `api` — FastAPI + Uvicorn
- `worker` — Celery worker (same Docker image, different command)
- `postgres` — PostgreSQL 15+ with pgvector and PostGIS extensions
- `redis` — Redis 7+ (shared broker + cache instance in Phase 1)

### 7.3 Deployment Diagram

```
Internet
    │
    ▼
[Vercel CDN] ── serves React SPA
    │
    │ HTTPS API calls
    ▼
[Reverse Proxy / Load Balancer]
    │
    ├──▶ [api container: FastAPI + Uvicorn]
    │         │
    │         ├──▶ [postgres container: PostgreSQL 15+]
    │         └──▶ [redis container: Redis 7+]
    │
    └──▶ [worker container: Celery worker]
              │
              ├──▶ [redis container: Redis 7+]
              ├──▶ [postgres container: PostgreSQL 15+]
              └──▶ [S3-compatible object storage: external]
```

### 7.4 Local Development Stack

```yaml
# docker-compose.yml services (Phase 1)
services:
  api:        # FastAPI + Uvicorn
  worker:     # Celery worker
  postgres:   # PostgreSQL 15+ with pgvector + PostGIS
  redis:      # Redis 7+
```

The frontend runs separately via `npm run dev` (Vite dev server) pointing to the local backend.

---

## 8. Scalability Considerations

### 8.1 Phase 1 Scalability Stance

CyberShakti Phase 1 is not designed for massive concurrent scale. The modular monolith is appropriate for the initial deployment scale. The architecture, however, does not preclude future horizontal scaling at key points.

### 8.2 Horizontal Scaling Points

| Component | How to Scale | Phase 1 Status |
|---|---|---|
| FastAPI API | Multiple Uvicorn workers / multiple container replicas | Single instance in Phase 1 |
| Celery workers | Add more worker container replicas | Single worker in Phase 1 |
| PostgreSQL | Read replicas for read-heavy queries | Not provisioned in Phase 1 |
| Redis | Redis Cluster or Redis Sentinel | Single instance in Phase 1 |

### 8.3 Identified Bottlenecks

| Bottleneck | Risk Level | Mitigation |
|---|---|---|
| Celery worker saturation (too many concurrent ML inference tasks) | Medium | Add worker replicas; task prioritisation |
| PostgreSQL connection exhaustion | Low-Medium | Connection pooling (PgBouncer) |
| LLM API rate limiting (F-11) | Medium | Request queuing in Celery; user-facing wait indicators |
| DistilBERT inference latency | Medium | Model loaded into worker memory at startup (not per-request load) |

---

## 9. Failure Modes and Resilience

### 9.1 Dependency Failure Handling

| Dependency Fails | System Behaviour |
|---|---|
| PostgreSQL | API returns HTTP 503 with user-facing maintenance message. No data corruption — all writes use transactions. |
| Redis (Celery broker) | Async features (F-03, F-05, F-06, F-07, F-11) unavailable. Synchronous features continue. API returns feature-unavailable response for async endpoints. |
| Threat Intelligence API | F-01, F-04, F-08 fall back to ML-only verdict without TI enrichment. Response notes absence of TI data. |
| LLM API | F-11 returns "AI assistant is temporarily unavailable" — not a fabricated response. |
| S3 Storage | F-03, F-04, F-06, F-10 upload endpoints return unavailable error. Scan history features unaffected. |
| Celery worker (crash) | Tasks are requeued from broker on worker restart. Idempotent task design required for safe retry. |

### 9.2 Error Response Conventions

All API errors return a consistent JSON envelope:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "URL format is not valid",
  "details": { "field": "url", "issue": "not a valid URL" }
}
```

Error codes are defined in a shared error code registry — not invented per-endpoint.

### 9.3 No Silent Failures

AI/ML components must **never silently return a default verdict** when an error occurs. A failed inference must return an error state, not a "Safe" verdict. A false Safe verdict from an error is more dangerous than an error response.

---

## 10. Open Architecture Decisions

| Decision | Status | Blocker | ADR |
|---|---|---|---|
| LLM provider for F-11 | Open | F-11 implementation blocked | ADR-013 |
| S3 storage provider | Open | F-03, F-04, F-06, F-10 file storage blocked | ADR-031 |
| Threat intelligence source | Open | F-01, F-04, F-08, F-13 TI enrichment blocked | ADR-032 |
| JWT storage location (httpOnly cookie vs. localStorage) | Pending security architecture review | Auth implementation decision | ADR-026 |
| Celery result backend (Redis vs. PostgreSQL) | Pending environment design | Task result retrieval design | — |
| PostgreSQL connection pool implementation (PgBouncer vs. SQLAlchemy pool) | Pending environment design | Database deployment configuration | — |
| Backend deployment platform | Pending cost/residency evaluation | Backend CI/CD and deployment setup | ADR-004 consequence |

---

*End of CyberShakti System Architecture — CSHAKTI-SYS-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
