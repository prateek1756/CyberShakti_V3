# CyberShakti — CI/CD Pipeline & Continuous Integration Strategy

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-DEPLOY-002 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-DEPLOY-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [CI/CD Philosophy](#1-cicd-philosophy)
2. [GitHub Actions Workflow Architecture](#2-github-actions-workflow-architecture)
3. [Workflow 1: Pull Request Validation (`pr-validation.yml`)](#3-workflow-1-pull-request-validation-pr-validationyml)
4. [Workflow 2: Staging Deployment (`staging-deploy.yml`)](#4-workflow-2-staging-deployment-staging-deployyml)
5. [Workflow 3: Production Release (`prod-release.yml`)](#5-workflow-3-production-release-prod-releaseyml)
6. [Secrets & Environment Management in CI](#6-secrets--environment-management-in-ci)
7. [Rollback & Recovery Procedures](#7-rollback--recovery-procedures)

---

## 1. CI/CD Philosophy

Continuous Integration and Continuous Deployment (CI/CD) automates all verification, testing, building, and deployment steps for CyberShakti.

### Principles:
- **No Manual Direct Production Edits**: All changes enter production via merged GitHub Pull Requests passing CI gates.
- **Fail Fast**: Syntax errors, linting issues, and unit test failures stop the pipeline in < 2 minutes.
- **Reproducible Builds**: Docker containers and frontend static bundles built once and promoted through environments.

---

## 2. GitHub Actions Workflow Architecture

```
[ Developer Pushes Code / Opens PR ]
                 │
                 ▼
 ┌───────────────────────────────────────────────┐
 │ WORKFLOW 1: PR Validation (pr-validation.yml) │
 │ - Linting: ruff, black, eslint, prettier       │
 │ - Security Audit: bandit, pip-audit, npm audit│
 │ - Tests: pytest, vitest, coverage report      │
 └───────────────────────┬───────────────────────┘
                         │ Pass & Approved Merge to main
                         ▼
 ┌───────────────────────────────────────────────┐
 │ WORKFLOW 2: Staging Deploy (staging-deploy.yml)│
 │ - Build Docker containers                     │
 │ - Run Database Migrations (Alembic)           │
 │ - Deploy to Staging Platform & Vercel Preview │
 │ - Run Integration & Playwright E2E Tests       │
 └───────────────────────┬───────────────────────┘
                         │ Manual Approval Tag (Release Tag)
                         ▼
 ┌───────────────────────────────────────────────┐
 │ WORKFLOW 3: Prod Release (prod-release.yml)   │
 │ - Production DB Migration                     │
 │ - Deploy Production Containers & Vercel Prod  │
 │ - Run Post-Deploy Health Checks               │
 └───────────────────────────────────────────────┘
```

---

## 3. Workflow 1: Pull Request Validation (`pr-validation.yml`)

Triggers on: Every Pull Request targeted at `main`.

### Jobs:
1. **backend-lint-and-test**:
   - Install Python 3.11 & dependencies.
   - Run `ruff check backend/` and `black --check backend/`.
   - Run `bandit -r backend/app/`.
   - Spin up PostgreSQL & Redis service containers in GHA runner.
   - Run `pytest --cov=backend/app --cov-fail-under=80`.
2. **frontend-lint-and-test**:
   - Install Node 18 & npm dependencies.
   - Run `npm run lint` and `npm run format:check`.
   - Run `npm run test:run` (Vitest).

---

## 4. Workflow 2: Staging Deployment (`staging-deploy.yml`)

Triggers on: Push to `main` branch.

### Jobs:
1. **build-and-push-docker**:
   - Build Docker image for `api` and `worker`.
   - Push to Container Registry with commit SHA tag.
2. **deploy-staging**:
   - Execute database migrations (`alembic upgrade head`) on staging DB.
   - Update staging deployment containers with new image tag.
   - Trigger Vercel staging deployment.
3. **e2e-testing**:
   - Run Playwright E2E test suite against staging URL.

---

## 5. Workflow 3: Production Release (`prod-release.yml`)

Triggers on: Publishing a GitHub Release / Release Tag (`v*.*.*`).

### Jobs:
1. **production-deploy**:
   - Execute production database migrations.
   - Update production container deployments.
   - Promote Vercel build to Production (`--prod`).
2. **post-deploy-verify**:
   - Query `GET https://api.cybershakti.in/health`.
   - Verify zero errors returned.

---

## 6. Secrets & Environment Management in CI

All deployment credentials are configured as GitHub Repository Secrets:
- `VERCEL_TOKEN` & `VERCEL_ORG_ID`
- `RENDER_API_KEY` / `AWS_ACCESS_KEY_ID`
- `STAGING_DATABASE_URL` / `PROD_DATABASE_URL`

---

## 7. Rollback & Recovery Procedures

- **Frontend Rollback**: Instant 1-click rollback via Vercel Dashboard to previous deployment deployment ID.
- **Backend Rollback**: Revert deployment container image tag to previous release tag.
- **Database Rollback**: Revert schema using `alembic downgrade -1` if migration is backward-compatible.

---

*End of CyberShakti CI/CD Strategy — CSHAKTI-DEPLOY-002 v1.0.0*
