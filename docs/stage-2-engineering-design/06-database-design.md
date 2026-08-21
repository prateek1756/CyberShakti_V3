# CyberShakti — Database Design

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-DB-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-SRS-001, CSHAKTI-TRD-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Database System Selection](#1-database-system-selection)
2. [Entity Overview](#2-entity-overview)
3. [Entity Relationship Model](#3-entity-relationship-model)
4. [Entity Definitions](#4-entity-definitions)
5. [Extension Usage](#5-extension-usage)
6. [Indexing Strategy](#6-indexing-strategy)
7. [Data Retention and Lifecycle](#7-data-retention-and-lifecycle)
8. [Security Considerations](#8-security-considerations)
9. [Migration Strategy](#9-migration-strategy)
10. [Assumptions and Open Items](#10-assumptions-and-open-items)

---

## 1. Database System Selection

**PostgreSQL 15+** is the single relational database for CyberShakti Phase 1 (ADR-005, CSHAKTI-CONST-001 §6.3). No additional databases are used. The following PostgreSQL extensions are installed:

| Extension | Purpose | Feature |
|---|---|---|
| `pgvector` | Vector similarity search for AI assistant RAG pipeline | F-11 |
| `PostGIS` | Geospatial point and polygon queries | F-13 |

Redis is used exclusively as a Celery broker and application cache. Redis is **not** a persistent data store — no user data, scan results, or application state is stored only in Redis.

---

## 2. Entity Overview

CyberShakti's data model is organised around these primary entity groups:

| Group | Entities | Purpose |
|---|---|---|
| **User and Auth** | `users`, `refresh_tokens`, `totp_secrets`, `backup_codes`, `password_reset_tokens`, `email_verification_tokens` | Account lifecycle, authentication state |
| **Scan History** | `scan_results` | Record of all user scans across all detection features |
| **Cyber Risk Score** | `risk_score_snapshots`, `risk_score_signals` | Risk score state and signal contributions |
| **AI Assistant** | `knowledge_base_documents`, `knowledge_base_chunks`, `assistant_conversations`, `assistant_messages` | RAG knowledge base and conversation history |
| **Location Alerts** | `scam_alerts` | Location-tagged threat alert records |
| **Content** | `safety_tips`, `quiz_questions`, `quiz_options`, `articles` | Cyber Safety Hub content |
| **Audit** | `audit_log` | Immutable record of security-relevant events |

---

## 3. Entity Relationship Model

```
users
  ├── refresh_tokens (1:many)
  ├── totp_secrets (1:0..1)
  ├── backup_codes (1:many)
  ├── password_reset_tokens (1:many)
  ├── email_verification_tokens (1:many)
  ├── scan_results (1:many)
  ├── risk_score_snapshots (1:many)
  │       └── risk_score_signals (1:many, via snapshot_id)
  └── assistant_conversations (1:many)
          └── assistant_messages (1:many, via conversation_id)

knowledge_base_documents
  └── knowledge_base_chunks (1:many)
          (each chunk has a pgvector embedding column)

scam_alerts (standalone, PostGIS geometry column)

safety_tips (standalone content table)
quiz_questions
  └── quiz_options (1:many)
articles (standalone content table)

audit_log (append-only, references user_id where applicable)
```

---

## 4. Entity Definitions

### 4.1 `users`

Stores core user account information.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | Stable user identifier |
| `email` | VARCHAR(320) | NOT NULL, UNIQUE, LOWER() normalised | Email addresses stored lowercase |
| `password_hash` | VARCHAR(512) | NOT NULL | Argon2id hash — never plaintext |
| `email_verified` | BOOLEAN | NOT NULL, DEFAULT FALSE | Account active only when TRUE |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | FALSE after account deletion before PII purge |
| `role` | VARCHAR(20) | NOT NULL, DEFAULT 'user' | 'user' or 'admin' (RBAC) |
| `totp_enabled` | BOOLEAN | NOT NULL, DEFAULT FALSE | 2FA enrollment status |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last modification timestamp |
| `deleted_at` | TIMESTAMPTZ | NULL | Soft delete timestamp; NULL = active |
| `deletion_requested_at` | TIMESTAMPTZ | NULL | Timestamp of deletion request for retention tracking |

**Security notes:**
- `email` is the login credential; stored lowercase, indexed uniquely
- `password_hash` contains ONLY the Argon2id hash — never the password
- `deleted_at` enables soft deletion; PII purge follows retention schedule
- `role` supports RBAC — values are constrained to 'user', 'admin'

**Indexes:**
- `UNIQUE INDEX ON users(email)` — for login lookup
- `INDEX ON users(is_active)` — for active user queries

---

### 4.2 `refresh_tokens`

Stores JWT refresh tokens for secure session management.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `token_hash` | VARCHAR(512) | NOT NULL, UNIQUE | SHA-256 hash of the token — never stored in plaintext |
| `issued_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Expiry based on refresh token lifetime TBD (ADR-026) |
| `revoked_at` | TIMESTAMPTZ | NULL | NULL = active; populated on logout or password reset |
| `user_agent` | TEXT | NULL | Browser/device context for session management |
| `ip_address` | INET | NULL | Issue-time IP for audit purposes |

**Notes:**
- Only the token hash is stored; the actual token value is never persisted
- Tokens are invalidated on password reset (FR-102)
- Expired and revoked tokens are eligible for periodic cleanup

---

### 4.3 `totp_secrets`

Stores TOTP secrets for two-factor authentication.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, UNIQUE, FK → users(id) ON DELETE CASCADE | One TOTP secret per user |
| `secret` | TEXT | NOT NULL | TOTP secret — MUST be encrypted at rest |
| `enrolled_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `algorithm` | VARCHAR(10) | NOT NULL, DEFAULT 'SHA1' | TOTP algorithm (RFC 6238 standard) |
| `digits` | SMALLINT | NOT NULL, DEFAULT 6 | |
| `period` | SMALLINT | NOT NULL, DEFAULT 30 | Seconds per TOTP window |

**Security note:** The TOTP `secret` column contains sensitive cryptographic material and must be encrypted at rest using column-level encryption or application-layer encryption. This is a security requirement, not optional.

---

### 4.4 `backup_codes`

Stores hashed 2FA backup codes.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `code_hash` | VARCHAR(512) | NOT NULL | Argon2id hash of the backup code |
| `used_at` | TIMESTAMPTZ | NULL | NULL = unused; populated when code is consumed |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

---

### 4.5 `password_reset_tokens`

Short-lived tokens for password reset flow.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `token_hash` | VARCHAR(512) | NOT NULL, UNIQUE | Hash of the reset token in the email link |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Short-lived: 15–60 minutes (TBD) |
| `used_at` | TIMESTAMPTZ | NULL | NULL = unused; consumed on password change |

---

### 4.6 `email_verification_tokens`

Tokens sent in email verification links at registration.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `token_hash` | VARCHAR(512) | NOT NULL, UNIQUE | Hash of token in verification link |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `expires_at` | TIMESTAMPTZ | NOT NULL | Short-lived: 24–48 hours (TBD) |
| `used_at` | TIMESTAMPTZ | NULL | NULL = unused; consumed on verification |

---

### 4.7 `scan_results`

Central record of all user-initiated scans across all detection features. One row per scan event.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE SET NULL | SET NULL on deletion to preserve anonymised history |
| `feature_id` | VARCHAR(10) | NOT NULL | 'F-01' through 'F-07', 'F-08' |
| `input_type` | VARCHAR(20) | NOT NULL | 'url', 'text', 'image', 'qr_image', 'profile_signals', 'phone', 'media_file', 'account_signals' |
| `input_hash` | VARCHAR(512) | NULL | SHA-256 hash of input for deduplication (never stores raw input) |
| `risk_level` | VARCHAR(20) | NULL | 'safe', 'low_risk', 'moderate_risk', 'high_risk', 'critical' |
| `risk_score_raw` | NUMERIC(5,4) | NULL | Raw model probability (0.0000–1.0000) |
| `verdict_source` | VARCHAR(20) | NULL | 'threat_intelligence', 'ml_model', 'combined', 'rule_based' |
| `is_experimental` | BOOLEAN | NOT NULL, DEFAULT FALSE | TRUE for F-06, F-07 outputs |
| `task_id` | UUID | NULL | Celery task ID for async scans |
| `task_status` | VARCHAR(20) | NULL | 'queued', 'processing', 'complete', 'error' |
| `scanned_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `completed_at` | TIMESTAMPTZ | NULL | When result was finalised |
| `error_code` | VARCHAR(50) | NULL | Error code if scan failed |

**Notes:**
- Raw input text/URL/image content is **never stored** in this table
- `input_hash` enables lookup of repeated submissions without storing the input
- `user_id` is SET NULL on user deletion (anonymised record retained for system quality)
- Scan results are a key input signal for the Cyber Risk Score engine

**Indexes:**
- `INDEX ON scan_results(user_id, scanned_at DESC)` — for user scan history queries
- `INDEX ON scan_results(feature_id, scanned_at DESC)` — for feature-level analytics
- `INDEX ON scan_results(task_id)` — for task status polling

---

### 4.8 `risk_score_snapshots`

Point-in-time snapshots of a user's Cyber Risk Score.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `score` | SMALLINT | NOT NULL | 0–100 (scale TBD during risk engine design) |
| `computed_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `signal_count` | SMALLINT | NOT NULL | Number of signals that contributed |

---

### 4.9 `risk_score_signals`

The individual signal contributions to a specific score snapshot.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `snapshot_id` | UUID | NOT NULL, FK → risk_score_snapshots(id) ON DELETE CASCADE | |
| `signal_name` | VARCHAR(100) | NOT NULL | Identifier from the Phase 1 controlled signal set |
| `signal_value` | JSONB | NOT NULL | The signal value (typed per signal definition) |
| `contribution_direction` | VARCHAR(10) | NOT NULL | 'positive' or 'negative' (improves or worsens score) |
| `weight` | NUMERIC(4,3) | NOT NULL | Signal weight in the weighted engine (0.000–1.000) |

---

### 4.10 `knowledge_base_documents`

Source documents in the AI Assistant knowledge base.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `title` | VARCHAR(500) | NOT NULL | Document title |
| `source` | VARCHAR(200) | NULL | Attribution/source name |
| `source_url` | TEXT | NULL | Source URL if applicable |
| `content_type` | VARCHAR(50) | NOT NULL | 'article', 'guideline', 'threat_advisory', 'faq' |
| `language` | VARCHAR(10) | NOT NULL, DEFAULT 'en' | ISO 639-1 language code |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | FALSE = retired from knowledge base |

---

### 4.11 `knowledge_base_chunks`

Chunked text segments from knowledge base documents with vector embeddings for similarity search.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `document_id` | UUID | NOT NULL, FK → knowledge_base_documents(id) ON DELETE CASCADE | |
| `chunk_index` | SMALLINT | NOT NULL | Position of chunk within document |
| `chunk_text` | TEXT | NOT NULL | Actual chunk text content |
| `embedding` | VECTOR(768) | NULL | pgvector embedding (dimension depends on embedding model — TBD) |
| `token_count` | SMALLINT | NULL | Approximate token count of chunk |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Index:**
- `USING ivfflat (embedding vector_cosine_ops)` — approximate nearest-neighbour search index for pgvector

**Note on embedding dimension:** 768 is shown as a placeholder consistent with DistilBERT/BERT-base embeddings. The actual dimension is determined by the embedding model selected for the RAG pipeline (depends on ADR-013 resolution).

---

### 4.12 `assistant_conversations`

Groups assistant messages into conversation sessions.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `user_id` | UUID | NOT NULL, FK → users(id) ON DELETE CASCADE | |
| `started_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `last_message_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | FALSE = archived/ended |

---

### 4.13 `assistant_messages`

Individual messages within an assistant conversation.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `conversation_id` | UUID | NOT NULL, FK → assistant_conversations(id) ON DELETE CASCADE | |
| `role` | VARCHAR(20) | NOT NULL | 'user' or 'assistant' |
| `content` | TEXT | NOT NULL | Message text |
| `retrieved_chunk_ids` | UUID[] | NULL | Knowledge base chunk IDs used in this response |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Privacy note:** User queries are personal data. Retention policy must be applied (Section 7).

---

### 4.14 `scam_alerts`

Location-tagged scam and fraud alert records for F-13.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `title` | VARCHAR(500) | NOT NULL | Alert title |
| `description` | TEXT | NOT NULL | Alert description |
| `alert_type` | VARCHAR(50) | NOT NULL | 'upi_fraud', 'whatsapp_scam', 'phone_scam', 'job_scam', 'investment_scam', 'other' |
| `severity` | VARCHAR(20) | NOT NULL | 'low_risk', 'moderate_risk', 'high_risk', 'critical' |
| `location_point` | GEOMETRY(Point, 4326) | NULL | PostGIS point (longitude, latitude) — for city-level lookups |
| `location_name` | VARCHAR(200) | NOT NULL | Human-readable location (e.g., "Mumbai", "Delhi NCR") |
| `state` | VARCHAR(100) | NULL | Indian state |
| `source` | VARCHAR(200) | NULL | Attribution/source |
| `source_url` | TEXT | NULL | Source URL |
| `published_at` | TIMESTAMPTZ | NOT NULL | When the alert was first published |
| `expires_at` | TIMESTAMPTZ | NULL | When the alert is no longer considered current (NULL = no expiry) |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | FALSE = alert removed from display |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**PostGIS index:**
- `USING GIST (location_point)` — for fast geospatial proximity queries

---

### 4.15 `safety_tips`

Daily cyber safety tips for F-14 Cyber Safety Hub.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `tip_text` | TEXT | NOT NULL | Tip content |
| `category` | VARCHAR(100) | NULL | e.g., 'phishing', 'password', 'upi', 'scam_calls' |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `display_date` | DATE | NULL | If set, show on this specific date; NULL = rotate by algorithm |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `reviewed_at` | TIMESTAMPTZ | NULL | Content review sign-off timestamp (FR-090) |
| `reviewed_by` | VARCHAR(200) | NULL | Reviewer identifier |

---

### 4.16 `quiz_questions`

Quiz questions for the Cybersecurity Quiz sub-feature of F-14.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `question_text` | TEXT | NOT NULL | |
| `explanation` | TEXT | NOT NULL | Shown after answering (FR-088) |
| `category` | VARCHAR(100) | NOT NULL | Threat category (e.g., 'upi_fraud', 'whatsapp_scam') |
| `difficulty` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | 'easy', 'medium', 'hard' |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | |
| `reviewed_at` | TIMESTAMPTZ | NULL | Content review sign-off |

---

### 4.17 `quiz_options`

Answer options for quiz questions.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `question_id` | UUID | NOT NULL, FK → quiz_questions(id) ON DELETE CASCADE | |
| `option_text` | TEXT | NOT NULL | |
| `is_correct` | BOOLEAN | NOT NULL | Exactly one option per question must be TRUE |
| `display_order` | SMALLINT | NOT NULL | Presentation order |

---

### 4.18 `articles`

Awareness articles for F-14 Cyber Safety Hub.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PRIMARY KEY | |
| `title` | VARCHAR(500) | NOT NULL | |
| `slug` | VARCHAR(500) | NOT NULL, UNIQUE | URL-friendly identifier |
| `content` | TEXT | NOT NULL | Markdown content |
| `category` | VARCHAR(100) | NOT NULL | e.g., 'upi_fraud', 'whatsapp_scam', 'otp_theft' |
| `tags` | TEXT[] | NULL | Array of tag strings |
| `is_published` | BOOLEAN | NOT NULL, DEFAULT FALSE | FALSE = draft |
| `published_at` | TIMESTAMPTZ | NULL | |
| `reviewed_at` | TIMESTAMPTZ | NULL | Content review sign-off |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

---

### 4.19 `audit_log`

Append-only record of security-relevant events. No rows are ever updated or deleted.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | BIGSERIAL | PRIMARY KEY | Sequential for ordering |
| `event_type` | VARCHAR(100) | NOT NULL | 'user_login', 'login_failed', 'password_reset', '2fa_enrolled', 'account_deleted', 'admin_action', etc. |
| `user_id` | UUID | NULL | NULL for pre-authentication events |
| `ip_address` | INET | NULL | |
| `user_agent` | TEXT | NULL | |
| `event_detail` | JSONB | NULL | Structured event-specific context (no PII) |
| `occurred_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | |

**Design rules:**
- This table is append-only. No UPDATE or DELETE is permitted by application code.
- `event_detail` must not contain PII (no passwords, tokens, or personal data)
- Retained per audit log retention policy (Section 7)

---

## 5. Extension Usage

### 5.1 pgvector

Used in `knowledge_base_chunks.embedding` column.

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create index for approximate nearest-neighbour search
CREATE INDEX ON knowledge_base_chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
-- (list count TBD based on knowledge base size)
```

Similarity search query pattern:
```sql
SELECT chunk_text, document_id,
       1 - (embedding <=> $1::vector) AS similarity
FROM knowledge_base_chunks
WHERE is_active = TRUE
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

### 5.2 PostGIS

Used in `scam_alerts.location_point` column.

```sql
-- Enable extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Spatial index
CREATE INDEX ON scam_alerts USING GIST (location_point);

-- Example: Find alerts within 50km of a user's city centre
SELECT * FROM scam_alerts
WHERE is_active = TRUE
  AND ST_DWithin(
    location_point::geography,
    ST_SetSRID(ST_Point($longitude, $latitude), 4326)::geography,
    50000  -- 50km radius
  )
ORDER BY published_at DESC
LIMIT 20;
```

---

## 6. Indexing Strategy

| Table | Index | Type | Purpose |
|---|---|---|---|
| `users` | `(email)` | UNIQUE B-tree | Login lookup |
| `users` | `(is_active)` | B-tree | Active user filtering |
| `refresh_tokens` | `(token_hash)` | UNIQUE B-tree | Token validation lookup |
| `refresh_tokens` | `(user_id)` | B-tree | User session management |
| `scan_results` | `(user_id, scanned_at DESC)` | B-tree | User scan history |
| `scan_results` | `(task_id)` | B-tree | Async task status polling |
| `knowledge_base_chunks` | `(embedding)` | IVFFlat | pgvector ANN search |
| `scam_alerts` | `(location_point)` | GiST | PostGIS geospatial queries |
| `scam_alerts` | `(is_active, published_at DESC)` | B-tree | Active alert listing |
| `articles` | `(slug)` | UNIQUE B-tree | URL slug lookup |
| `audit_log` | `(user_id, occurred_at)` | B-tree | User audit queries |
| `audit_log` | `(event_type, occurred_at)` | B-tree | Event-type analytics |

---

## 7. Data Retention and Lifecycle

All retention periods below are **proposed values** and must be confirmed through legal review of DPDP Act 2023 obligations (ADR-030) before production deployment.

| Data Category | Retention Period | Action on Expiry |
|---|---|---|
| Active user accounts | Until account deletion requested | Soft delete → PII purge after retention period |
| PII after deletion request | 30 days (proposed) | Hard delete of email, password_hash, personal fields |
| Anonymised scan records | 12 months (proposed) | Delete or further anonymise |
| Assistant conversation messages | 90 days from last message (proposed) | Delete |
| Refresh tokens (expired) | 7 days after expiry | Delete |
| Password reset tokens (expired/used) | 24 hours | Delete |
| Email verification tokens (expired/used) | 24 hours | Delete |
| Audit log entries | 12 months (proposed) | Archive or delete (legal verification required) |
| Uploaded scan media (S3) | Deleted after processing | Immediate deletion |
| Backup codes (used) | 30 days (proposed) | Delete |

> **Decision Status: PENDING** — All retention periods must be reviewed against DPDP Act 2023 obligations by qualified legal counsel before launch (ADR-030).

---

## 8. Security Considerations

### 8.1 Sensitive Column Policy

| Column | Classification | Protection |
|---|---|---|
| `users.password_hash` | Sensitive | Argon2id hash — never stored in plaintext |
| `users.email` | PII | Stored lowercase; accessible only by authenticated owner and admin |
| `totp_secrets.secret` | Sensitive cryptographic | Must be encrypted at rest (column encryption or application layer) |
| `backup_codes.code_hash` | Sensitive | Argon2id hash of code |
| `refresh_tokens.token_hash` | Sensitive | SHA-256 hash — never the raw token |
| `assistant_messages.content` | Potentially sensitive | User query content — subject to retention policy |
| `scan_results.input_hash` | Sensitive | SHA-256 hash only — no raw input stored |
| `audit_log.event_detail` | Sensitive metadata | Must not contain PII |

### 8.2 Database Access Control

- Application connects with a **least-privilege database user** — not the PostgreSQL superuser
- Separate database users for: application (DML), migrations (DDL), read-only analytics
- Direct database access from outside the deployment network is prohibited
- Database connection credentials are managed as environment variables (never in codebase)

### 8.3 Input Validation at Application Layer

All data persisted to the database must have passed Pydantic validation at the API layer. No raw user input reaches database queries without sanitisation. Parameterised queries are used for all dynamic SQL (no string concatenation).

### 8.4 No PII in Logs

Database query logs and application logs must not capture column values that contain PII or sensitive data. Slow query logs capture query structures only, not parameter values.

---

## 9. Migration Strategy

Database schema changes are managed via **Alembic** (Python migration framework, standard for SQLAlchemy/FastAPI projects).

### 9.1 Migration Rules

1. Every schema change is captured as an Alembic migration file — no manual DDL in production
2. Migrations are reversible wherever possible (include a `downgrade()` function)
3. Migrations are reviewed before execution in production
4. No destructive migrations (column drops, table drops) are executed without explicit approval
5. Data migrations (backfills) are separated from schema migrations
6. Migrations are tested in a staging environment before production

### 9.2 Initial Schema Bootstrap

The initial schema is created by running all Alembic migrations from zero. No raw SQL bootstrap script is maintained separately.

---

## 10. Assumptions and Open Items

| Item | Status | Notes |
|---|---|---|
| TOTP secret encryption at rest | Decision Required | Column-level encryption vs. application-layer encryption must be decided during security architecture review |
| pgvector embedding dimension | TBD | Depends on embedding model selected (ADR-013 resolution) |
| `knowledge_base_chunks` list count for IVFFlat index | TBD | Depends on total knowledge base size at launch |
| All retention periods | Pending legal review | Must be confirmed against DPDP Act 2023 before launch (ADR-030) |
| SQLAlchemy async driver vs. asyncpg | TBD | To be decided during environment setup |
| Connection pool size | TBD | Based on deployment target resource specifications |
| Database encryption at rest | TBD | Depends on deployment platform (ADR-004, ADR-031) — PostgreSQL with filesystem-level encryption preferred |

---

*End of CyberShakti Database Design — CSHAKTI-DB-001 v1.0.0*

*This document may only be amended through the change control process defined in CSHAKTI-CONST-001 §14.*
