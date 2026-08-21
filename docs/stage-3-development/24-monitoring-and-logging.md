# CyberShakti — Monitoring, Logging & Observability Specification

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-OPS-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-SEC-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Observability Strategy](#1-observability-strategy)
2. [Application Logging Architecture](#2-application-logging-architecture)
3. [Metrics & Performance Monitoring](#3-metrics--performance-monitoring)
4. [Health Check & Liveness Endpoints](#4-health-check--liveness-endpoints)
5. [Alerting Rules & Incident Response](#5-alerting-rules--incident-response)
6. [Audit Log Management](#6-audit-log-management)

---

## 1. Observability Strategy

Observability provides deep visibility into system performance, ML inference execution, error rates, and security events across CyberShakti.

### Three Pillars of Observability:
1. **Logs**: Structured JSON logs capturing application context and security events (without PII).
2. **Metrics**: Real-time performance indicators (latency, throughput, queue depth, error rates).
3. **Traces**: Request-level tracing via `request_id` header propagation across API and Celery workers.

---

## 2. Application Logging Architecture

### 2.1 Log Format & Schema
All backend logs are emitted as structured JSON objects to standard output (`stdout`):

```json
{
  "timestamp": "2026-08-20T15:30:00.123Z",
  "level": "INFO",
  "logger": "app.detect_analyze.views",
  "request_id": "req-9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "event": "scan_completed",
  "feature_id": "F-01",
  "risk_level": "high_risk",
  "duration_ms": 142.5
}
```

### 2.2 Privacy & Security Restrictions in Logs
- **Strictly Prohibited**: Raw user passwords, TOTP codes, JWT tokens, S3 signed URLs, uploaded image contents, raw user message texts, or PII.

---

## 3. Metrics & Performance Monitoring

### Key System Metrics Tracked:

| Metric Name | Type | Description | Target / Threshold |
|---|---|---|---|
| `http_requests_total` | Counter | Total incoming HTTP requests by route & status code | Baseline tracking |
| `http_request_duration_seconds` | Histogram | API endpoint latency distribution | p95 < 500ms (sync routes) |
| `celery_task_queue_length` | Gauge | Number of pending async inference tasks in Redis | Queue depth < 50 tasks |
| `celery_task_execution_seconds` | Histogram | Execution duration of heavy ML tasks (F-03, F-06) | Task duration < 5s |
| `db_connection_pool_usage` | Gauge | Active vs available DB connections | Utilization < 80% |

---

## 4. Health Check & Liveness Endpoints

### 4.1 Liveness Probe (`GET /health/live`)
Returns HTTP 200 OK if the FastAPI process is running. Used by container orchestrators for liveness restart checks.

### 4.2 Readiness Probe (`GET /health/ready`)
Verifies active connection to dependencies (PostgreSQL DB ping, Redis ping, S3 bucket access). Returns HTTP 200 OK if healthy, HTTP 503 if any dependency is unreachable.

```json
{
  "status": "healthy",
  "timestamp": "2026-08-20T15:30:00Z",
  "dependencies": {
    "postgres": "connected",
    "redis": "connected",
    "storage": "connected"
  }
}
```

---

## 5. Alerting Rules & Incident Response

| Alert Condition | Severity | Channel | Action Required |
|---|---|---|---|
| **API Error Rate > 5% over 5m** | Critical | PagerDuty / Slack | Investigate exception logs & backend health |
| **Postgres Connection Exhaustion** | High | Slack / Email | Scale connection pool or investigate leak |
| **Celery Queue Backlog > 100** | High | Slack | Scale worker container replicas |
| **Security Audit: Failed Login Spike** | Warning | Security Channel | Investigate potential brute-force attack |

---

## 6. Audit Log Management

- Audit records written to `audit_log` table in PostgreSQL.
- Retained for 12 months in accordance with security retention policies.
- Accessible exclusively by administrators via `/admin/audit-log`.

---

*End of CyberShakti Monitoring, Logging & Observability Specification — CSHAKTI-OPS-001 v1.0.0*
