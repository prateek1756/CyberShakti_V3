# CyberShakti — Coding Standards & Guidelines

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-DEV-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SYS-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [General Engineering Principles](#1-general-engineering-principles)
2. [Python & FastAPI Coding Standards](#2-python--fastapi-coding-standards)
3. [JavaScript & React Coding Standards](#3-javascript--react-coding-standards)
4. [SQL & Migration Standards](#4-sql--migration-standards)
5. [Error Handling & Logging Guidelines](#5-error-handling--logging-guidelines)
6. [Security Coding Rules](#6-security-coding-rules)
7. [Code Review & Quality Gates](#7-code-review--quality-gates)

---

## 1. General Engineering Principles

- **No Placeholders**: Never leave `TODO`, `FIXME`, or stub implementations without explicit justification.
- **Fail Fast, Fail Safely**: Validate inputs at boundaries; handle exceptions gracefully without crashing or leaking sensitive info.
- **Self-Documenting Code**: Write clear code, concise function names, and type hints over redundant code comments.

---

## 2. Python & FastAPI Coding Standards

### 2.1 Code Formatting & Style
- Compliant with **PEP 8**. Formatting enforced automatically via `ruff` and `black`.
- Maximum line length: 100 characters.
- Imports sorted automatically via `isort`.

### 2.2 Type Annotations & Pydantic
- Mandatory type hints on all function parameters and return values:
  ```python
  async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
      ...
  ```
- All API request and response bodies MUST use explicit **Pydantic v2** schemas. Do not return raw ORM models directly to the client.

### 2.3 Async Usage
- All database I/O, external HTTP requests, and file operations MUST be asynchronous (`async def`).
- CPU-heavy operations (e.g., encryption, ML feature extraction) MUST be run in Celery workers or `run_in_executor`.

---

## 3. JavaScript & React Coding Standards

### 3.1 Code Style & Formatting
- Formatted via **Prettier** and linted via **ESLint**.
- Use Functional Components and React Hooks exclusively. No Class Components.

### 3.2 State Management & Side Effects
- Local state via `useState`; global auth via `useContext(AuthContext)`.
- Data fetching performed inside `useEffect` or custom data hooks, handling loading, data, and error states.
- Clean up subscriptions and timers in `useEffect` cleanup functions.

---

## 4. SQL & Migration Standards

- SQL keywords MUST be UPPERCASE (`SELECT`, `INSERT`, `WHERE`, `JOIN`).
- Table names MUST be lowercase and plural (`users`, `scan_results`, `scam_alerts`).
- Column names MUST be `snake_case`. Primary keys MUST be named `id`.
- All schema modifications MUST be authored as Alembic migrations in `backend/alembic/versions/`.

---

## 5. Error Handling & Logging Guidelines

### 5.1 Exception Handling
- Catch specific exceptions (e.g., `ValueError`, `JWTError`, `SQLAlchemyError`). Never use bare `except:`.
- API handlers convert internal errors into standard HTTP exception envelopes (`HTTPException`):
  ```python
  raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail={"error_code": "INVALID_URL", "message": "The provided string is not a valid URL"}
  )
  ```

### 5.2 Logging Standards
- Use structured JSON logging (`structlog` or `logging`).
- Log Levels:
  - `DEBUG`: Verbose step-by-step diagnostic information.
  - `INFO`: Business events (user logged in, scan task queued).
  - `WARNING`: Recoverable errors (rate limit reached, API retry).
  - `ERROR`: Unexpected operational failures requiring investigation.
- **NEVER LOG**: Passwords, JWT secrets, raw user uploaded files, or PII.

---

## 6. Security Coding Rules

1. **No String Format Queries**: Never format SQL queries using `%` or f-strings. Always use parameterized SQLAlchemy / asyncpg queries.
2. **Timing Attack Protection**: Use `hmac.compare_digest` or constant-time comparison algorithms for hash and token comparisons.
3. **Nonce / IV Uniqueness**: Always generate a fresh random 96-bit nonce for every AES-256-GCM encryption operation.

---

## 7. Code Review & Quality Gates

Before merging any Pull Request, the CI pipeline enforces:
- `ruff check .` — Linter passes with 0 errors.
- `black --check .` — Formatting verification passes.
- `pytest` — All backend unit & integration tests pass with 100%.
- `npm run test` — All frontend unit tests pass.

---

*End of CyberShakti Coding Standards & Guidelines — CSHAKTI-DEV-001 v1.0.0*
