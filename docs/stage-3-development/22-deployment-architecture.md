# CyberShakti — Deployment Architecture Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-DEPLOY-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-TRD-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Deployment Strategy Overview](#1-deployment-strategy-overview)
2. [Target Cloud Infrastructure Topology](#2-target-cloud-infrastructure-topology)
3. [Frontend Deployment Architecture](#3-frontend-deployment-architecture)
4. [Backend & Worker Deployment Architecture](#4-backend--worker-deployment-architecture)
5. [Database & Caching Infrastructure](#5-database--caching-infrastructure)
6. [Object Storage Setup](#6-object-storage-setup)
7. [SSL/TLS & Domain Management](#7-ssltls--domain-management)
8. [Disaster Recovery & Backup Strategy](#8-disaster-recovery--backup-strategy)

---

## 1. Deployment Strategy Overview

CyberShakti is deployed as a cloud-hosted, containerized modular monolith with dedicated background worker instances. The architecture balances operational simplicity, security, and low deployment cost for Phase 1.

```
                    [ End User Browsers ]
                              │
               ┌──────────────┴──────────────┐
               │ HTTPS (TLS 1.3)             │ HTTPS (TLS 1.2+)
               ▼                             ▼
    [ Vercel CDN Edge ]             [ Cloud Reverse Proxy ]
    (React SPA Frontend)            (WAF / Load Balancer)
                                             │
                                             ▼
                                    [ FastAPI Web Server ]
                                    (Docker App Instance)
                                             │
                       ┌─────────────────────┼─────────────────────┐
                       │ Async Task Queue    │ DB Connections      │ Objects
                       ▼                     ▼                     ▼
               [ Redis Service ]   [ Managed PostgreSQL 15+ ] [ S3 Object Storage ]
               (Broker & Cache)    (pgvector & PostGIS)     (Media & Encrypted Files)
                       ▲
                       │ Consumes Tasks
               [ Celery Workers ]
               (Inference Engines)
```

---

## 2. Target Cloud Infrastructure Topology

| Component | Target Provider / Service | Deployment Unit | Scaling Model |
|---|---|---|---|
| **Frontend** | Vercel Edge Network | Static SPA Bundle | Global CDN auto-scale |
| **API Server** | Render / Railway / AWS ECS | Docker Container (`api`) | Vertical / Horizontal replicas |
| **Async Workers** | Render / Railway / AWS ECS | Docker Container (`worker`) | Dedicated worker container |
| **Primary Database** | Managed PostgreSQL (Neon / Supabase / AWS RDS) | PostgreSQL 15+ | Vertical scaling + Automated Backups |
| **Broker & Cache** | Managed Redis (Upstash / Redis Cloud) | Redis 7+ | Dedicated cache instance |
| **Object Storage** | AWS S3 / Cloudflare R2 | S3-Compatible Storage | Auto-scaling object storage |

---

## 3. Frontend Deployment Architecture

- **Hosting**: Vercel.
- **Build Trigger**: Automatic deployment on merge to `main` branch via GitHub integration.
- **Environment Variables**: `VITE_API_BASE_URL` injected at build time.
- **Cache Strategy**: Immutable asset caching (`Cache-Control: max-age=31536000, immutable`) for hashed assets; `index.html` configured with `no-cache`.

---

## 4. Backend & Worker Deployment Architecture

### 4.1 FastAPI Container (`api`)
- Entrypoint: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`
- Health check endpoint: `GET /health` returning DB and Redis ping status.

### 4.2 Celery Worker Container (`worker`)
- Entrypoint: `celery -A app.worker.celery_app worker --loglevel=info --concurrency=2`
- Shares the same Docker image as `api`, using a different entry command.

---

## 5. Database & Caching Infrastructure

### 5.1 PostgreSQL Setup
- Extensions required: `CREATE EXTENSION IF NOT EXISTS vector;`, `CREATE EXTENSION IF NOT EXISTS postgis;`.
- Connection pooling: Managed via SQLAlchemy async connection pool or PgBouncer.
- SSL connection required (`sslmode=require`).

### 5.2 Redis Setup
- Dual usage: Celery task queue (DB 0) and API rate limiting / caching (DB 1).
- Persistence: RDB snapshots enabled for cache recovery.

---

## 6. Object Storage Setup

- Bucket structure:
  - `user-files/`: Encrypted user files (F-10).
  - `scan-uploads/`: Temporary screenshot / QR uploads (deleted after processing).
  - `mlflow-artefacts/`: Saved ML model weights and evaluation runs.
- Security: All buckets strictly private; CORS configured for frontend domain only; Server-Side Encryption (SSE-S3) enabled.

---

## 7. SSL/TLS & Domain Management

- Primary Domain: `cybershakti.in`
- Subdomains:
  - `app.cybershakti.in` -> Vercel Frontend
  - `api.cybershakti.in` -> Backend API Gateway
- SSL Certificates: Auto-renewed Managed TLS certificates issued by Let's Encrypt / Vercel / Cloud Provider.

---

## 8. Disaster Recovery & Backup Strategy

- **Database Backups**: Automated daily full snapshots + Point-In-Time Recovery (PITR) with 7-day retention.
- **RTO (Recovery Time Objective)**: < 2 hours for full service restoration.
- **RPO (Recovery Point Objective)**: < 15 minutes (max potential data loss window).

---

*End of CyberShakti Deployment Architecture Specification — CSHAKTI-DEPLOY-001 v1.0.0*
