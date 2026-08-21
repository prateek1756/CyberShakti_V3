# CyberShakti — Testing Strategy

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-TEST-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-SRS-001, CSHAKTI-TRD-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Testing Vision & Quality Philosophy](#1-testing-vision--quality-philosophy)
2. [Testing Pyramid](#2-testing-pyramid)
3. [Test Environment Architecture](#3-test-environment-architecture)
4. [Testing Tooling Stack](#4-testing-tooling-stack)
5. [Test Data Management](#5-test-data-management)
6. [Quality Gates & CI Integration](#6-quality-gates--ci-integration)

---

## 1. Testing Vision & Quality Philosophy

CyberShakti requires high reliability because false verdicts (false positives or false negatives) can damage user trust or expose users to real financial harm. 

### Core Quality Mandates:
- **Zero Regression**: Every bug fix MUST be accompanied by a regression test.
- **Traceability**: All test cases trace back to functional requirements in CSHAKTI-SRS-001.
- **Automated Verification**: Manual testing is reserved for exploratory UI/UX validation; all critical paths are automated.

---

## 2. Testing Pyramid

```
          / \
         /   \      E2E Tests (Playwright)
        /  E2E \     - Critical User Journeys (Auth, Scan, Encrypt)
       /-------\
      /   API   \    Integration & Contract Tests (Pytest + HTTP Client)
     /           \   - FastAPI endpoints, Celery workers, Database queries
    /-------------\
   /   Unit Tests  \  Unit Tests (Pytest, Vitest)
  /                 \ - ML feature extractors, Risk engine, Cryptography, React components
 /-------------------\
```

| Test Level | Scope | Execution Frequency | Target Coverage |
|---|---|---|---|
| **Unit Tests** | Individual functions, models, components | Pre-commit & CI (every commit) | >= 80% line coverage |
| **Integration Tests** | API endpoints, DB, Celery tasks | CI (pull requests) | Key API workflows |
| **E2E Tests** | Full stack web application flow | Pre-merge & Nightly | Primary user journeys |
| **Security Tests** | Auth, Rate limiting, Injection, File upload | Nightly & Pre-release | OWASP Top 10 |

---

## 3. Test Environment Architecture

- **Unit Tests**: Run in isolated processes with mock dependencies (using `unittest.mock` and `pytest-mock`).
- **Integration Tests**: Run against isolated Docker container instances of PostgreSQL and Redis (`pytest-docker` or test DB container). Test database schema is migrated fresh via Alembic before test suite runs.
- **E2E Tests**: Playwright executes headless Chromium against local frontend dev server and test backend instance.

---

## 4. Testing Tooling Stack

| Category | Tool | Usage |
|---|---|---|
| **Backend Unit & Integration** | Pytest | Test runner for Python backend |
| **Async Test Support** | `pytest-asyncio` | Async fixture and test execution |
| **HTTP Client Testing** | `httpx` / FastAPI `TestClient` | In-process API integration testing |
| **Frontend Unit & Component** | Vitest + React Testing Library | Component rendering & hook tests |
| **End-to-End Testing** | Playwright | Full user journey automation |
| **Coverage Reporting** | `coverage.py` / `vitest --coverage` | Code coverage measurement |
| **Security Linting** | `bandit` / `pip-audit` / `npm audit` | Automated dependency vulnerability scans |

---

## 5. Test Data Management

- **Database Fixtures**: Pytest fixtures populate static baseline data (e.g., test users, initial Cyber Safety Hub content) using clean database transactions rolled back after each test.
- **Sample Threat Data**: Synthetic datasets containing sample phishing URLs, scam text snippets, and test QR codes stored in `backend/tests/fixtures/`.
- **Zero Production Data in Tests**: Live user data is never used in testing environments.

---

## 6. Quality Gates & CI Integration

### Pre-Merge Requirements:
1. **100% Test Pass Rate**: Zero failing unit or integration tests.
2. **Code Coverage Threshold**: Minimum 80% code coverage across `app/` modules.
3. **No High-Severity Vulnerabilities**: Security audits (`bandit`, `pip-audit`, `npm audit`) clean of critical vulnerabilities.

---

*End of CyberShakti Testing Strategy — CSHAKTI-TEST-001 v1.0.0*
