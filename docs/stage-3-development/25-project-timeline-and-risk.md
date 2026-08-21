# CyberShakti — Project Timeline & Risk Management Plan

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-PM-001 |
| **Version** | 1.0.0 |
| **Status** | Draft |
| **Date** | 2026-08-20 |
| **Traces To** | CSHAKTI-IMPL-001, CSHAKTI-CONST-001 |
| **Governed By** | CSHAKTI-CONST-001 — conflicts recorded in `docs/00-decisions.md` |

---

## Table of Contents

1. [Project Master Schedule](#1-project-master-schedule)
2. [Gantt Schedule Overview](#2-gantt-schedule-overview)
3. [Resource Allocation](#3-resource-allocation)
4. [Risk Register & Mitigation Matrix](#4-risk-register--mitigation-matrix)
5. [Governance & Change Control](#5-governance--change-control)

---

## 1. Project Master Schedule

CyberShakti Phase 1 follows an 11-week master execution timeline organized into four major phases.

```
Week 1-2:   Phase 1 Foundation Setup & Architecture Bootstrap
Week 3-5:   Phase 2 Core MVP Detection Features (F-01 through F-04)
Week 6-7:   Phase 3 Protection Services & Security Features (F-08, F-09, F-10)
Week 8-9:   Phase 4 Assist, Respond & Learn Features (F-12, F-13, F-14, F-11)
Week 10-11: Phase 5 Experimental Features, Hardening & Launch Audit
```

---

## 2. Gantt Schedule Overview

| Workstream / Phase | Start Wk | End Wk | Key Deliverables | Milestone Sign-off |
|---|---|---|---|---|
| **Infrastructure & Auth** | Wk 1 | Wk 2 | DB Migrations, JWT Auth, Docker Compose | Milestone 0 |
| **Core Detection MVP** | Wk 3 | Wk 5 | F-01, F-02, F-03, F-04 APIs & UIs | Milestone 1 |
| **Protection Pillar** | Wk 6 | Wk 7 | F-08 Lookup, F-09 Password, F-10 Encrypt | Milestone 2 |
| **Assist & Learn Pillar** | Wk 8 | Wk 9 | F-12 Score, F-13 Alerts, F-14 Hub, F-11 RAG | Milestone 3 |
| **Experimental & Launch** | Wk 10 | Wk 11 | F-05, F-06, F-07, Security Audit & Launch | Milestone 4 |

---

## 3. Resource Allocation

| Role / Responsibility | Key Focus Areas | Allocation |
|---|---|---|
| **Backend & Security Engineer** | FastAPI endpoints, DB design, Cryptography, Auth | Full-time |
| **Frontend Engineer** | React Vite SPA, UI/UX Components, State Management | Full-time |
| **AI/ML Engineer** | DistilBERT fine-tuning, XGBoost, PaddleOCR, RAG | Full-time |
| **DevOps & QA Engineer** | Docker Compose, CI/CD, Pytest/Playwright automation | Part-time |

---

## 4. Risk Register & Mitigation Matrix

### 4.1 Technical & Delivery Risks

| Risk ID | Risk Event | Impact | Likelihood | Risk Level | Mitigation Strategy |
|---|---|---|---|---|---|
| **R-TECH-01** | Open ADR-013 (LLM provider) remains unresolved, blocking F-11 | High | Medium | **HIGH** | Deploy F-11 with "Feature Coming Soon" fallback state (FR-071); maintain mock LLM service during development |
| **R-TECH-02** | India-specific scam text dataset unavailable for F-02 fine-tuning | High | High | **HIGH** | Curate initial synthetic dataset from public CERT-In advisories; start classical TF-IDF baseline first |
| **R-TECH-03** | Heavy ML tasks cause worker memory exhaustion on small server targets | Medium | Medium | **MEDIUM** | Model lazy-loading; worker process memory recycling; concurrency cap on memory-intensive workers |
| **R-TECH-04** | OCR accuracy fails on low-resolution screenshot uploads (F-03) | Medium | High | **MEDIUM** | Implement image contrast preprocessing; display OCR quality indicator to user; fail gracefully |

### 4.2 Security & Compliance Risks

| Risk ID | Risk Event | Impact | Likelihood | Risk Level | Mitigation Strategy |
|---|---|---|---|---|---|
| **R-SEC-01** | Cryptographic key or password leakage in application logs | Critical | Low | **HIGH** | Strict log sanitization rules; automated SAST scanning via `bandit` and `trufflehog` |
| **R-SEC-02** | User account enumeration via auth error messages | Medium | High | **MEDIUM** | Enforce generic error envelopes (`"Invalid email or password"`) across all auth endpoints |

---

## 5. Governance & Change Control

- All modifications to scope, technology stack, or timeline MUST be approved following the 6-step change control process in **CSHAKTI-CONST-001 §14**.
- Any architectural change MUST be documented in `docs/00-decisions.md` before implementation begins.

---

*End of CyberShakti Project Timeline & Risk Management Plan — CSHAKTI-PM-001 v1.0.0*
