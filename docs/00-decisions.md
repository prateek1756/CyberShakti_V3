# CyberShakti — Architecture Decision Record / Decision Log

| Field | Value |
|---|---|
| **Document ID** | CSHAKTI-ADR-LOG-001 |
| **Version** | 1.0.0 |
| **Status** | Living document — updated throughout the project lifecycle |
| **Date** | 2026-08-15 |
| **Authority** | All decisions recorded here are governed by the change control process defined in CSHAKTI-CONST-001 §14 |

---

## Status Definitions

| Status | Meaning |
|---|---|
| **Accepted** | Decision is locked. Change control process (CSHAKTI-CONST-001 §14) is required to modify. |
| **Provisional** | Decision is directionally chosen but requires empirical validation before being fully locked. May be revised based on evidence. |
| **Open** | Decision is unresolved. Must be resolved before implementation of the affected feature or component begins. |
| **Pending** | A proposed change has been recorded but not yet approved. Must not be acted upon until approved. |

---

## ADR Index

| ID | Title | Status |
|---|---|---|
| ADR-001 | Four-pillar product structure | Accepted |
| ADR-002 | 14-feature freeze with locked 4-tier classification | Accepted |
| ADR-003 | React + Vite frontend | Accepted |
| ADR-004 | FastAPI + Python backend | Accepted |
| ADR-005 | PostgreSQL as primary and only database | Accepted |
| ADR-006 | pgvector for vector embeddings within PostgreSQL | Accepted |
| ADR-007 | PostGIS for geospatial queries within PostgreSQL | Accepted |
| ADR-008 | XGBoost as baseline model for phishing URL classification | Provisional |
| ADR-009 | DistilBERT for scam and email NLP classification | Provisional |
| ADR-010 | EfficientNet and/or Xception for deepfake detection evaluation | Provisional |
| ADR-011 | XGBoost + graph features (NetworkX) for mule account detection | Provisional |
| ADR-012 | Explainable weighted risk engine for Cyber Risk Score in Phase 1 | Accepted |
| ADR-013 | API-based LLM + RAG for AI Cybersecurity Assistant | Open |
| ADR-014 | Modular monolith architecture + isolated AI/ML services | Accepted |
| ADR-015 | Kiro / Antigravity / Cursor as implementation assistants | Accepted |
| ADR-016 | India-first geographic and regulatory scope | Accepted |
| ADR-017 | Individual consumer as primary target user | Accepted |
| ADR-018 | Scam Call Blocking Phase 1: in-app lookup only | Accepted |
| ADR-019 | Auth: email + password + optional TOTP 2FA | Accepted |
| ADR-020 | Cyber Risk Score: controlled Phase 1 signal set | Accepted |
| ADR-021 | AES-256-GCM for file encryption; Argon2id for password-derived keys | Accepted |
| ADR-022 | PaddleOCR for screenshot text extraction | Provisional |
| ADR-023 | QR Code Scanner: no separate DL model; routes to phishing URL analyzer | Accepted |
| ADR-024 | Mule account detection dataset limitations (Elliptic / Elliptic2) | Accepted |
| ADR-025 | Phase 1 = responsive web application; native apps deferred | Accepted |
| ADR-026 | Security configuration parameters are TBD pending benchmarking | Accepted |
| ADR-027 | PII protection: minimization and appropriate protection principle | Accepted |
| ADR-028 | Formal 6-step change control process | Accepted |
| ADR-029 | Feature classification tiers are locked | Accepted |
| ADR-030 | Regulatory references are compliance considerations requiring legal verification | Accepted |
| ADR-031 | S3-compatible object storage: provider TBD | Open |
| ADR-032 | Threat intelligence sources: selection TBD | Open |

---

## ADR-001 — Four-Pillar Product Structure

| Field | Value |
|---|---|
| **Decision ID** | ADR-001 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti is organised into exactly four product pillars: Detect & Analyze, Protect, Assist & Respond, and Learn & Prevent. |

**Context:** A cybersecurity platform serving non-technical Indian consumers must be intuitively structured. Features need to be discoverable by purpose, not by technical taxonomy. A pillar-based structure groups features by the outcome they deliver to the user, supporting both product coherence and UI navigation design.

**Options Considered:**
- Single flat feature list with no grouping
- Two-tier grouping (detection vs. protection)
- Four-pillar structure (Detect & Analyze / Protect / Assist & Respond / Learn & Prevent)
- Domain-based grouping (social media, communications, financial, identity)

**Chosen Option:** Four-pillar structure.

**Reason:** The four pillars map directly to the core user journey — a user detects a threat, is protected from it, gets assistance to respond, and learns to prevent future incidents. This sequence (Detect → Analyze → Protect → Assist → Learn) is the product's core philosophy. Domain-based grouping was rejected because many threats span multiple domains, which would create ambiguity in feature placement and user navigation.

**Consequences:** All 14 features must be assigned to exactly one pillar. No feature may span pillars. New features added in future phases must fit within an existing pillar or trigger a documented pillar structure review.

**Related Documents:** CSHAKTI-CONST-001 §5

---

## ADR-002 — 14-Feature Freeze with Locked 4-Tier Classification

| Field | Value |
|---|---|
| **Decision ID** | ADR-002 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti Phase 1 contains exactly 14 top-level features, classified into 4 tiers (Core MVP, Advanced MVP, Research/Experimental, Deferred/Future). This set is frozen. |

**Context:** Unbounded scope is the most common cause of delayed or failed software projects. A frozen feature set with explicit classification tiers allows the team to build quality features rather than a large number of partially complete ones. The classification system distinguishes production requirements from research scope, preventing Research/Experimental features from being held to the same release-readiness standard as Core MVP features — or vice versa.

**Options Considered:**
- Open feature list, prioritised by sprint
- Frozen feature list with no tier classification
- Frozen feature list with binary classification (MVP vs. deferred)
- Frozen feature list with 4-tier classification

**Chosen Option:** Frozen feature list with 4-tier classification.

**Reason:** The 4-tier system is the minimum granularity needed to correctly govern Phase 1 scope. Core MVP and Advanced MVP features have different implementation complexity but both ship in Phase 1. Research/Experimental features (F-06, F-07) require research and training scope in Phase 1 but must not be released as production-grade without empirical validation. The fourth tier (Deferred/Future) preserves the approved product concept without creating Phase 1 implementation obligations.

**Consequences:** No features may be added to the Phase 1 set without a recorded and approved change decision. Feature tier reassignments require the same change process. Development agents and engineers may not autonomously reclassify features.

**Related Documents:** CSHAKTI-CONST-001 §4, §5

---

## ADR-003 — React + Vite Frontend

| Field | Value |
|---|---|
| **Decision ID** | ADR-003 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The CyberShakti frontend is built with React as the UI framework and Vite as the build tool, with Tailwind CSS, Framer Motion, React Router, Axios, and Recharts as supporting libraries. |

**Context:** The frontend must be a responsive web application. The chosen stack must support component-based UI development, rapid iteration, and a rich interactive experience suitable for a security platform serving non-technical users.

**Options Considered:**
- React + Vite + Tailwind CSS (selected stack)
- Next.js (React-based with SSR)
- Vue 3 + Vite
- Angular

**Chosen Option:** React + Vite.

**Reason:** React is the most widely adopted frontend framework with a large ecosystem and strong AI coding tool support. Vite provides significantly faster build and hot-reload performance than legacy bundlers. Tailwind CSS enables rapid, consistent styling without custom CSS overhead. Next.js was considered but its SSR complexity is not justified by Phase 1 requirements — a responsive single-page application is sufficient. Vue and Angular were not selected as they would reduce AI coding tool effectiveness and team familiarity assumptions.

**Consequences:** All frontend development uses React conventions. Server-side rendering is not available in Phase 1. If SSR becomes a requirement (for SEO or performance reasons), migration to Next.js would require a documented change decision.

**Related Documents:** CSHAKTI-CONST-001 §6.1

---

## ADR-004 — FastAPI + Python Backend

| Field | Value |
|---|---|
| **Decision ID** | ADR-004 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The CyberShakti backend is built with Python and FastAPI, with Pydantic for data validation, Uvicorn as the ASGI server, Celery for async task queuing, and Redis as the Celery broker and cache. |

**Context:** The backend must serve a React frontend via a REST API and must orchestrate multiple AI/ML inference workloads. The language and framework choice must align with the AI/ML stack to avoid a language-boundary between the API layer and the ML inference layer.

**Options Considered:**
- Python + FastAPI (selected)
- Python + Django REST Framework
- Node.js + Express
- Go + Gin

**Chosen Option:** Python + FastAPI.

**Reason:** Python is the native language of the entire AI/ML stack (PyTorch, scikit-learn, XGBoost, Hugging Face, PaddleOCR, NetworkX). Using Python for the backend eliminates inter-language serialisation overhead and simplifies model serving. FastAPI's async-native design, automatic OpenAPI documentation, and Pydantic integration make it the strongest Python web framework for an API-first backend. Django REST Framework was rejected as more heavyweight than required for Phase 1. Node.js and Go were rejected due to the language-boundary problem with the ML stack.

**Consequences:** All backend development uses Python and FastAPI conventions. The backend deployment target must support Python ASGI applications. Celery + Redis must be included in all deployment environments.

**Related Documents:** CSHAKTI-CONST-001 §6.2

---

## ADR-005 — PostgreSQL as Primary and Only Database

| Field | Value |
|---|---|
| **Decision ID** | ADR-005 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | PostgreSQL is the single relational database for CyberShakti. No additional databases are permitted without a recorded ADR. |

**Context:** Using a single well-understood database reduces operational complexity, avoids data consistency challenges across multiple stores, and simplifies deployment and backup. PostgreSQL is highly capable and, through its extension system, supports vector similarity search (pgvector) and geospatial queries (PostGIS) — eliminating the need for separate specialised databases.

**Options Considered:**
- PostgreSQL only (selected)
- PostgreSQL + Redis (Redis as a data store, not just cache)
- PostgreSQL + MongoDB (for unstructured data)
- PostgreSQL + dedicated vector database (e.g., Pinecone, Weaviate, Qdrant)

**Chosen Option:** PostgreSQL only, with pgvector and PostGIS extensions.

**Reason:** PostgreSQL's extension architecture satisfies all Phase 1 data storage requirements within a single system. Adding MongoDB would introduce a second database engine for marginal benefit — Phase 1 data is sufficiently structured for a relational model. A dedicated vector database would add operational overhead and a network hop that pgvector within PostgreSQL avoids entirely. Redis is retained as a Celery broker and cache only, not as a primary data store.

**Consequences:** All persistent data lives in PostgreSQL. The data model must be designed to work within a relational schema. If future scale requirements create genuine bottlenecks in the relational model, a database change decision must be recorded and approved before any migration begins.

**Related Documents:** CSHAKTI-CONST-001 §6.3, §7.4, ADR-006, ADR-007

---

## ADR-006 — pgvector for Vector Embeddings Within PostgreSQL

| Field | Value |
|---|---|
| **Decision ID** | ADR-006 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | Vector embeddings for the AI Cybersecurity Assistant knowledge base are stored and queried using the pgvector extension within PostgreSQL. A separate standalone vector database is not used. |

**Context:** The AI Cybersecurity Assistant (F-11) requires a Retrieval-Augmented Generation (RAG) pipeline that performs similarity search over a curated cybersecurity knowledge base. This requires vector storage and approximate nearest-neighbour search capability.

**Options Considered:**
- pgvector within PostgreSQL (selected)
- Pinecone (managed vector database)
- Weaviate (open-source vector database)
- Qdrant (open-source vector database)
- Chroma (lightweight vector database)

**Chosen Option:** pgvector within PostgreSQL.

**Reason:** pgvector provides sufficient vector search capability for Phase 1 knowledge base scale within the existing PostgreSQL instance, adding zero new infrastructure dependencies. Dedicated vector databases (Pinecone, Weaviate, Qdrant, Chroma) introduce additional services, separate connection management, separate backups, and additional cost — none of which are justified by Phase 1 requirements. If knowledge base scale grows to a point where pgvector performance is demonstrably insufficient, migration to a dedicated vector store can be evaluated with a new ADR.

**Consequences:** Vector embeddings are co-located with relational data in PostgreSQL. Knowledge base size must be monitored as the product scales. No separate vector database infrastructure is required for Phase 1 deployment.

**Related Documents:** CSHAKTI-CONST-001 §6.3, §6.10, ADR-005, ADR-013

---

## ADR-007 — PostGIS for Geospatial Queries Within PostgreSQL

| Field | Value |
|---|---|
| **Decision ID** | ADR-007 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | Geospatial queries for Location-Based Scam Alerts (F-13) are served by the PostGIS extension within PostgreSQL. No separate geospatial database is used. |

**Context:** F-13 Location-Based Scam Alerts requires the ability to store and query threat data associated with geographic locations, enabling the system to surface scam alerts relevant to a user's location.

**Options Considered:**
- PostGIS within PostgreSQL (selected)
- Separate spatial database
- Application-layer geospatial filtering without a spatial database
- Redis geospatial commands

**Chosen Option:** PostGIS within PostgreSQL.

**Reason:** PostGIS is the most mature and capable open-source geospatial database extension, and integrating it within the existing PostgreSQL instance adds zero new infrastructure. Application-layer filtering was rejected as it would not scale and would require loading all location data into memory. Redis geospatial commands were considered for Phase 1 simplicity but rejected in favour of PostGIS's richer query capability and persistence model within the primary database.

**Consequences:** Location-tagged threat data is stored in PostgreSQL with PostGIS geometry types. Geospatial indexing (e.g., GiST indexes on geometry columns) must be configured during database design. No separate geospatial infrastructure is required.

**Related Documents:** CSHAKTI-CONST-001 §6.3, ADR-005

---

## ADR-008 — XGBoost as Baseline Model for Phishing URL Classification

| Field | Value |
|---|---|
| **Decision ID** | ADR-008 |
| **Date** | 2026-08-15 |
| **Status** | Provisional |
| **Decision** | XGBoost is the selected baseline model for phishing URL classification (F-01), with LightGBM as a comparison candidate. Model selection is subject to empirical validation. |

**Context:** F-01 Phishing Link Scanning requires a model that classifies URLs as phishing or legitimate based on engineered features (lexical, domain, path, query characteristics). This is a structured tabular classification problem well-suited to gradient boosting methods.

**Options Considered:**
- Logistic Regression (baseline)
- Random Forest
- XGBoost (selected as baseline)
- LightGBM (comparison candidate)
- Deep learning URL classifier (neural network over character sequences)

**Chosen Option:** XGBoost as primary baseline; LightGBM as comparison candidate.

**Reason:** XGBoost is well-established for tabular classification problems with engineered features. It handles mixed feature types, missing values, and feature interactions effectively. LightGBM offers comparable performance with faster training on large datasets and will be evaluated alongside XGBoost. Deep learning approaches were not selected as the primary baseline because the problem is a structured tabular task where gradient boosting consistently performs well and is more interpretable than neural approaches.

**Consequences:** URL feature engineering is a critical dependency — model performance is bounded by the quality of extracted features. The baseline must be established and documented before any advanced model variants are evaluated. Model selection is **provisional** — final choice depends on empirical performance on a representative phishing URL dataset. All performance metrics (precision, recall, F1, ROC-AUC, FPR, FNR) are TBD.

**Related Documents:** CSHAKTI-CONST-001 §3.1, §3.4, §5.1 (F-01)

---

## ADR-009 — DistilBERT for Scam and Email NLP Classification

| Field | Value |
|---|---|
| **Decision ID** | ADR-009 |
| **Date** | 2026-08-15 |
| **Status** | Provisional |
| **Decision** | DistilBERT (fine-tuned) is the selected model for scam message and email text classification (F-02, F-03), with TF-IDF + Logistic Regression as the mandatory baseline comparison. Model selection is subject to empirical validation. |

**Context:** F-02 Message & Email Scam Detection and F-03 Screenshot Scam Scanner (post-OCR text) require a model that understands the semantic content of text to identify scam patterns. This is an NLP classification problem where semantic understanding matters — lexical features alone are insufficient for adversarial scam text.

**Options Considered:**
- TF-IDF + Logistic Regression (mandatory baseline)
- TF-IDF + SVM
- DistilBERT fine-tuned (selected)
- BERT fine-tuned
- RoBERTa fine-tuned
- LLM zero-shot classification

**Chosen Option:** DistilBERT fine-tuned, with TF-IDF + Logistic Regression as mandatory baseline.

**Reason:** DistilBERT offers approximately 97% of BERT's performance at 40% of the model size and 60% of the inference speed, making it more practical for production inference than full BERT. The classical TF-IDF + Logistic Regression baseline must be established first to quantify the benefit of fine-tuned transformers — if the classical baseline is sufficient, it should be preferred for its simplicity and interpretability. LLM zero-shot classification was rejected for this use case as it introduces inference cost and latency disproportionate to the classification task.

**Consequences:** Training requires GPU compute (Kaggle GPU / Google Colab GPU). The baseline must be run before DistilBERT fine-tuning. Model selection is **provisional** — final choice depends on comparative empirical performance. Multilingual capability (Hindi and other Indian languages) is a known limitation that must be documented and evaluated. All performance metrics are TBD.

**Related Documents:** CSHAKTI-CONST-001 §3.1, §3.4, §5.1 (F-02, F-03)

---

## ADR-010 — EfficientNet and/or Xception for Deepfake Detection Evaluation

| Field | Value |
|---|---|
| **Decision ID** | ADR-010 |
| **Date** | 2026-08-15 |
| **Status** | Provisional |
| **Decision** | EfficientNet and Xception are the candidate architectures for deepfake detection model evaluation (F-06). Final architecture selection depends on empirical evaluation. F-06 is classified Research/Experimental. |

**Context:** F-06 Deepfake Detection is classified Research/Experimental. The feature requires a model capable of detecting synthetic or manipulated media. This is an active research problem with no universally optimal architecture. EfficientNet and Xception are well-established in the deepfake detection literature and represent reasonable starting points for Phase 1 research.

**Options Considered:**
- EfficientNet (selected as candidate)
- Xception (selected as candidate)
- ResNet-based classifier
- Vision Transformer (ViT)
- Custom CNN architecture

**Chosen Option:** EfficientNet and Xception evaluated empirically; final selection TBD.

**Reason:** Both EfficientNet and Xception have demonstrated competitive performance in published deepfake detection research. Evaluating both against the same datasets allows an evidence-based selection rather than an arbitrary one. ResNet was not excluded as a possibility but is lower priority given the published performance of EfficientNet/Xception. ViT was considered but introduces additional complexity and compute requirements not yet justified for the Research/Experimental phase.

**Consequences:** F-06 must not be represented as production-grade deepfake detection. Generalisation to unseen generation methods is a known and documented limitation. Training requires GPU compute. All performance metrics are TBD. Datasets (FaceForensics++, Celeb-DF, DFDC) require access and licensing verification before use.

**Related Documents:** CSHAKTI-CONST-001 §3.1, §3.4, §5.1 (F-06)

---

## ADR-011 — XGBoost + Graph Features (NetworkX) for Mule Account Detection

| Field | Value |
|---|---|
| **Decision ID** | ADR-011 |
| **Date** | 2026-08-15 |
| **Status** | Provisional |
| **Decision** | XGBoost with graph-engineered features (NetworkX) is the Phase 1 approach for mule account detection (F-07). Graph Neural Networks (PyTorch Geometric) are the advanced path for future phases. F-07 is classified Research/Experimental. |

**Context:** F-07 Mule Account Detection requires identifying accounts that may be part of money-muling networks. This involves both individual account signals and network/graph relationships between accounts. Graph Neural Networks (GNNs) represent the state-of-the-art approach but require significant graph construction infrastructure. For Phase 1 research scope, graph feature engineering with a classical classifier is a practical starting point.

**Options Considered:**
- XGBoost with tabular features only
- XGBoost with NetworkX-engineered graph features (selected)
- Graph Neural Networks via PyTorch Geometric (deferred to advanced phase)
- Rule-based detection only

**Chosen Option:** XGBoost + NetworkX graph features for Phase 1; GNNs for future phases.

**Reason:** NetworkX graph feature engineering extracts meaningful structural features (degree centrality, clustering coefficient, path length, community membership) from account transaction graphs and feeds them as tabular features to XGBoost. This approach provides graph-aware classification without the full infrastructure required for end-to-end GNN training in Phase 1. GNNs via PyTorch Geometric are preserved as the advanced path once the Phase 1 research baseline is established.

**Consequences:** F-07 must not be represented as production-grade mule detection. The Elliptic/Elliptic2 dataset limitation (see ADR-024) must be prominently documented. Real-world bank mule detection applicability requires separate validation. All performance metrics are TBD.

**Related Documents:** CSHAKTI-CONST-001 §3.1, §3.4, §5.1 (F-07), ADR-024

---

## ADR-012 — Explainable Weighted Risk Engine for Cyber Risk Score in Phase 1

| Field | Value |
|---|---|
| **Decision ID** | ADR-012 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The Cyber Risk Score (F-12) is produced in Phase 1 by an explainable weighted risk engine using a controlled set of in-app security signals and selected user-reported security-posture signals. ML-based risk prediction is explicitly not part of Phase 1. |

**Context:** F-12 Cyber Risk Score must give users a personalised assessment of their cybersecurity posture. The score must be explainable — users must understand why they received the score they did. In Phase 1, a weighted engine is preferred over an ML model because: (a) it is fully explainable by design, (b) it does not require a training dataset that does not yet exist, and (c) it can be implemented and refined iteratively as signal quality improves.

**Options Considered:**
- Purely rule-based fixed score
- Weighted risk engine with controlled signal set (selected)
- ML-based risk prediction model (rejected for Phase 1)
- Hybrid weighted engine + ML model

**Chosen Option:** Explainable weighted risk engine with controlled Phase 1 signal set.

**Reason:** An ML-based risk model requires labelled training data mapping user behaviour to security outcomes — data that does not exist at Phase 1. A weighted engine with a curated, controlled signal set is honest about its methodology, fully explainable, and produces a score that users can understand and act on. The signal set is controlled (not open-ended) to prevent the score from becoming arbitrary. ML-based prediction remains an option for a future phase once behavioural data has accumulated.

**Consequences:** The Phase 1 signal set must be explicitly defined and locked during engineering design. Every score output must include an explanation of which signals contributed to it and why. The signal set must not be silently expanded by developers or AI coding tools without a recorded change decision.

**Related Documents:** CSHAKTI-CONST-001 §5.3, ADR-020

---

## ADR-013 — API-Based LLM + RAG for AI Cybersecurity Assistant

| Field | Value |
|---|---|
| **Decision ID** | ADR-013 |
| **Date** | 2026-08-15 |
| **Status** | Open |
| **Decision** | The AI Cybersecurity Assistant (F-11) uses an API-based LLM integrated with a RAG pipeline over a curated CyberShakti knowledge base. The specific LLM provider is unresolved. |

**Context:** F-11 requires a conversational AI assistant capable of answering cybersecurity questions, explaining threat verdicts, and providing guidance grounded in a curated knowledge base. Training an LLM from scratch is not feasible or justified — API-based integration with RAG is the approved approach.

**Options Considered:**
- OpenAI API (GPT-4 / GPT-4o family)
- Anthropic API (Claude family)
- Google AI API (Gemini family)
- Open-source self-hosted LLM (Llama 3, Mistral, etc.)
- No LLM — rule-based assistant only

**Chosen Option:** API-based LLM (provider TBD). Open-source self-hosted LLM remains a viable alternative if data privacy or cost requirements make API-based integration unsuitable.

**Resolution Required:** The LLM provider decision requires evaluation of: (a) API cost and rate limits at expected usage volume, (b) capability for cybersecurity reasoning tasks, (c) data privacy terms — specifically whether user query content is used for model training by the provider, (d) India data residency implications of API calls to external providers, (e) availability and reliability of the provider's API.

**Consequences:** F-11 implementation cannot begin until this decision is resolved. The RAG pipeline, pgvector schema, and knowledge base design are not provider-dependent and can proceed. All LLM outputs must include a disclaimer that responses are AI-generated and should not be the sole basis for security decisions. The assistant must not fabricate threat intelligence.

**Related Documents:** CSHAKTI-CONST-001 §6.10, ADR-006

---

## ADR-014 — Modular Monolith Architecture + Isolated AI/ML Services

| Field | Value |
|---|---|
| **Decision ID** | ADR-014 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti Phase 1 uses a modular monolith architecture. Heavy AI/ML inference workloads are isolated as async Celery workers. Microservices decomposition is not used in Phase 1. |

**Context:** The architecture must balance development simplicity (appropriate for a Phase 1 build), operational manageability, and the genuine need to isolate computationally heavy AI/ML inference from synchronous API responses.

**Options Considered:**
- Full microservices architecture
- Modular monolith with async task queue (selected)
- Monolith with no internal module boundaries
- Serverless functions

**Chosen Option:** Modular monolith + Celery async workers.

**Reason:** A modular monolith provides the development simplicity and deployment manageability appropriate for Phase 1, while internal module boundaries enforce the architectural discipline needed to support future decomposition if required. Microservices were rejected as they introduce network boundaries, distributed tracing complexity, and deployment overhead that are not justified by Phase 1 requirements. Celery + Redis handles the one genuine isolation need — heavy ML inference — without requiring a full microservices architecture. Serverless was rejected due to cold-start latency incompatibility with ML inference workloads.

**Consequences:** All backend code is deployed as a single unit in Phase 1. Internal module boundaries (by pillar) must be maintained during implementation — collapsing boundaries to "move fast" is not acceptable. Future microservices decomposition requires a change decision and must not be introduced autonomously.

**Related Documents:** CSHAKTI-CONST-001 §7, ADR-004, ADR-005

---

## ADR-015 — AI Development Tools as Implementation Assistants

| Field | Value |
|---|---|
| **Decision ID** | ADR-015 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | Kiro, Antigravity, Cursor, and other AI-assisted coding tools are approved as implementation assistants. They are not sources of requirements, architecture decisions, or product scope. Any autonomous change to locked decisions requires the change control process. |

**Context:** CyberShakti is being developed with AI-assisted coding tools. These tools can significantly accelerate implementation but carry a risk of autonomously deviating from approved documentation — adding features, changing technology choices, or resolving open decisions without authorisation.

**Options Considered:**
- Prohibit AI coding tools entirely
- Use AI coding tools without governance constraints
- Use AI coding tools with explicit governance constraints (selected)

**Chosen Option:** AI coding tools with explicit governance constraints.

**Reason:** The productivity benefit of AI coding tools is real. The governance risk is equally real. The correct response is to define exactly what these tools may and may not do, and to enforce this through the change control process. Prohibiting them entirely would be counterproductive.

**Consequences:** AI coding tools must follow approved documentation. When they encounter gaps or conflicts, they must flag rather than autonomously resolve. Any change to a locked decision surfaced during AI-assisted implementation must be recorded in this document before being acted upon.

**Related Documents:** CSHAKTI-CONST-001 §15, ADR-028

---

## ADR-016 — India-First Geographic and Regulatory Scope

| Field | Value |
|---|---|
| **Decision ID** | ADR-016 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti Phase 1 is designed primarily for Indian consumers, with the Indian regulatory context (IT Act 2000, DPDP Act 2023, RBI/NPCI guidelines) and Indian threat landscape (UPI fraud, WhatsApp scams, OTP phishing, SIM swap) as the primary context. |

**Context:** The product's threat intelligence, scam taxonomy, UX language, and regulatory awareness must be grounded in a specific context to be genuinely useful. An India-first focus allows the product to address the highest-impact threat patterns for the target user base rather than producing a generic cybersecurity tool.

**Options Considered:**
- Global-generic scope with no regional specificity
- India-first scope (selected)
- Multi-region scope from Phase 1

**Chosen Option:** India-first scope.

**Reason:** The founding context is India's rapidly growing digital consumer base and its specific threat landscape. Indian consumers face a distinct set of high-frequency threats — UPI payment fraud, WhatsApp-based social engineering, OTP theft, SIM swap fraud, job scams, QR code fraud — that justify a tailored approach. A generic global product would dilute this specificity without adding value for the primary target user in Phase 1.

**Consequences:** Threat intelligence sourcing, scam taxonomy, example content, and UX copy should reflect the Indian context. Regulatory references are India-specific (see ADR-030). Global expansion, if pursued, requires a separate scoping decision. Regulatory obligations for operating in India require legal verification (see ADR-030).

**Related Documents:** CSHAKTI-CONST-001 §10, ADR-017, ADR-030

---

## ADR-017 — Individual Consumer as Primary Target User

| Field | Value |
|---|---|
| **Decision ID** | ADR-017 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The primary target user for CyberShakti Phase 1 is the individual Indian consumer — a non-technical person using digital services and exposed to consumer-facing cyber threats. Enterprise, organisational, and professional security use cases are not in Phase 1 scope. |

**Context:** A cybersecurity platform must be designed with a clear user in mind. Designing for both enterprise security teams and individual consumers simultaneously produces a product that serves neither well. The individual consumer focus shapes the UX language, explanation depth, feature selection, and pricing model.

**Options Considered:**
- Individual consumer (selected)
- Small and medium business (SMB) owner
- Cybersecurity professional / prosumer
- All of the above simultaneously

**Chosen Option:** Individual consumer — non-technical, India-first.

**Reason:** The founding problem is consumer-facing cybercrime in India. Individual consumers are the most exposed, least served, and most numerous potential users. Enterprise security is a fundamentally different product category with different requirements, procurement models, and compliance frameworks. Targeting enterprise in Phase 1 would distort the product design without validated demand.

**Consequences:** All UX decisions must be evaluated against the non-technical individual consumer standard. Technical jargon must be translated into actionable plain language. Features appropriate only for enterprise or professional users must not be added to Phase 1 without a scope change decision.

**Related Documents:** CSHAKTI-CONST-001 §2 (Principle 8), ADR-016

---

## ADR-018 — Scam Call Blocking Phase 1: In-App Lookup Only

| Field | Value |
|---|---|
| **Decision ID** | ADR-018 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | F-08 Scam Call Blocking Phase 1 scope is: in-app phone-number lookup and risk assessment against threat/reputation data. Android OS-level automatic call blocking is deferred to a future phase. |

**Context:** The feature is named "Scam Call Blocking" but the Phase 1 implementation scope is explicitly bounded to prevent scope overreach. Android OS-level call screening integration requires Android-specific native development, OS permissions management, and a different technical architecture than the Phase 1 responsive web application.

**Options Considered:**
- In-app manual number lookup and risk assessment (selected for Phase 1)
- Android OS-level automatic call blocking (deferred)
- Both simultaneously in Phase 1

**Chosen Option:** In-app manual number lookup for Phase 1; Android integration deferred.

**Reason:** The Phase 1 platform is a responsive web application (ADR-025). Android OS-level integration requires a native Android application or a dedicated Android SDK — neither of which is in Phase 1 scope. The in-app lookup provides genuine value to users who want to check a number before calling back or engaging with a caller, without requiring a native app.

**Consequences:** F-08 acceptance criteria must not reference Android OS integration. Users must manually enter or paste a phone number for lookup. Real-time call interception is not possible in Phase 1.

**Related Documents:** CSHAKTI-CONST-001 §5.3, §11, ADR-025

---

## ADR-019 — Auth: Email + Password + Optional TOTP 2FA

| Field | Value |
|---|---|
| **Decision ID** | ADR-019 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti authentication uses email and password as the primary credential, with optional TOTP-based 2FA. Social login (Google, GitHub OAuth, etc.) is deferred. |

**Context:** A cybersecurity platform that does not support strong authentication would be inconsistent with its own security principles. 2FA reduces account takeover risk significantly. Making 2FA optional rather than mandatory in Phase 1 reduces onboarding friction for non-technical users while still enabling security-aware users to harden their accounts.

**Options Considered:**
- Email + password only
- Email + password + optional TOTP 2FA (selected)
- Email + password + mandatory 2FA
- Social login only (Google / GitHub)
- Email + password + social login

**Chosen Option:** Email + password + optional TOTP 2FA; social login deferred.

**Reason:** Optional 2FA balances security enablement with non-technical user onboarding friction. Mandatory 2FA was considered but rejected for Phase 1 to avoid creating a barrier for the primary target user (non-technical Indian consumer). Social login adds OAuth integration complexity and third-party dependency not justified for Phase 1. TOTP is a well-established, provider-independent 2FA standard that does not require SMS (which has its own security weaknesses).

**Consequences:** Authentication flows must cover: registration, login, optional 2FA enrollment, 2FA-enabled login, password reset, and account deletion. JWT configuration parameters (algorithm, expiry, refresh lifetime) are TBD per ADR-026.

**Related Documents:** CSHAKTI-CONST-001 §8.5, §8.6, ADR-026

---

## ADR-020 — Cyber Risk Score: Controlled Phase 1 Signal Set

| Field | Value |
|---|---|
| **Decision ID** | ADR-020 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The Cyber Risk Score (F-12) uses a controlled, explicitly defined set of in-app security signals and selected user-reported security-posture signals in Phase 1. The signal set is not open-ended. ML-based risk prediction is not used in Phase 1. |

**Context:** The Cyber Risk Score must be explainable and grounded in signals the system can actually measure or verify. An open-ended signal set risks producing a score that is difficult to explain, difficult to validate, and potentially misleading. A controlled signal set ensures the score remains honest and defensible.

**Options Considered:**
- Open-ended signal set (any detectable signal)
- Controlled in-app signals only (no user-reported signals)
- Controlled in-app signals + controlled user-reported signals (selected)
- ML-based risk prediction model (rejected for Phase 1)

**Chosen Option:** Controlled in-app + selected user-reported signals; explainable weighted engine.

**Reason:** In-app signals (threat detections, scan history, password security check results) are objectively measurable. Selected user-reported signals (e.g., "have you enabled 2FA on your key accounts?", "do you reuse passwords?") add security-posture context that in-app signals alone cannot capture. The signal set must be explicitly defined during engineering design — not left open for developers to expand. ML-based prediction requires labelled training data that does not exist at Phase 1.

**Consequences:** The Phase 1 signal set must be formally defined and locked in the engineering design phase. Every score must include an explanation of contributing signals. The signal set must not be silently expanded. A future phase may introduce ML-based risk prediction once behavioural data has accumulated.

**Related Documents:** CSHAKTI-CONST-001 §5.3, ADR-012

---

## ADR-021 — AES-256-GCM for File Encryption; Argon2id for Password-Derived Keys

| Field | Value |
|---|---|
| **Decision ID** | ADR-021 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | F-10 Secure File Encryption uses AES-256-GCM as the encryption algorithm. Where user-provided passwords are used to derive encryption keys, Argon2id is the key derivation function. Specific configuration parameters are TBD per ADR-026. |

**Context:** F-10 requires secure, standards-based file encryption. The choices must be defensible, well-established, and not invented. AES-256-GCM is the current industry standard for authenticated symmetric encryption. Argon2id is the Password Hashing Competition winner and the current recommendation for password-based key derivation.

**Options Considered:**
- AES-256-CBC (no authentication tag — rejected)
- AES-256-GCM (selected — authenticated encryption)
- ChaCha20-Poly1305 (viable alternative)
- Custom encryption scheme (rejected — never invent cryptography)

**Chosen Option:** AES-256-GCM + Argon2id for password-derived keys.

**Reason:** AES-256-GCM provides both confidentiality and integrity (authenticated encryption), detecting tampering of encrypted files. AES-256-CBC was rejected because it requires separate MAC computation and is more error-prone in implementation. ChaCha20-Poly1305 is a viable alternative but AES-256-GCM benefits from hardware acceleration on most modern processors. Argon2id is preferred over bcrypt and scrypt for key derivation due to its resistance to both GPU and side-channel attacks.

**Consequences:** AES-256-GCM requires correct nonce (IV) management — nonces must never be reused with the same key. Argon2id parameter tuning (memory, time, parallelism) must be performed through benchmarking per ADR-026. Custom or improvised cryptography is strictly prohibited.

**Related Documents:** CSHAKTI-CONST-001 §8.3, §8.4, ADR-026

---

## ADR-022 — PaddleOCR for Screenshot Text Extraction

| Field | Value |
|---|---|
| **Decision ID** | ADR-022 |
| **Date** | 2026-08-15 |
| **Status** | Provisional |
| **Decision** | PaddleOCR is the selected OCR library for screenshot text extraction in the F-03 Screenshot Scam Scanner pipeline. Selection is subject to performance validation on representative Indian-context screenshots. |

**Context:** F-03 Screenshot Scam Scanner requires extracting text from user-uploaded screenshots before passing it to the scam NLP classifier. The OCR library must handle mixed-language text (English + Hindi/regional scripts), low-resolution mobile screenshots, and varied screenshot formats commonly seen in Indian messaging apps.

**Options Considered:**
- PaddleOCR (selected as baseline)
- Tesseract OCR
- Google Cloud Vision API (external service)
- AWS Textract (external service)

**Chosen Option:** PaddleOCR.

**Reason:** PaddleOCR is open-source, supports multiple languages including Hindi and other Indian scripts, and can be deployed locally without sending user data to external cloud services (important for privacy). Tesseract was considered but generally shows lower accuracy on mixed-language and low-quality images. Cloud Vision API and Textract were rejected as they require sending user screenshot data to external providers, which creates privacy risks inconsistent with CyberShakti's privacy principles.

**Consequences:** OCR accuracy on Indian-context screenshots must be empirically validated. OCR errors propagate to the downstream NLP classifier — OCR accuracy is a ceiling on overall F-03 accuracy. This decision is **provisional** — if PaddleOCR accuracy on representative test data is insufficient, alternatives must be evaluated with a new ADR.

**Related Documents:** CSHAKTI-CONST-001 §5.1 (F-03), §6.8

---

## ADR-023 — QR Code Scanner: No Separate DL Model; Routes to Phishing URL Analyzer

| Field | Value |
|---|---|
| **Decision ID** | ADR-023 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | F-04 QR Code Scam Scanner does not use a separate deep-learning model. It decodes the QR code, extracts the embedded URL, and routes it to the F-01 phishing URL analysis pipeline. |

**Context:** QR code scams predominantly work by embedding malicious URLs in QR codes. The threat is the URL, not the QR code image itself. A separate deep-learning model for "QR code scam detection" would be unnecessary complexity — the existing phishing URL analysis capability is the appropriate tool once the URL is extracted.

**Options Considered:**
- Separate deep-learning model for QR scam classification (rejected)
- QR decode + route to F-01 phishing URL analyzer (selected)
- QR decode + rule-based URL check only (no ML)

**Chosen Option:** QR decode + route to F-01 phishing URL analyzer.

**Reason:** The threat in QR code scams is the embedded URL. Routing the decoded URL through the established phishing URL analysis pipeline (F-01) reuses existing capability, reduces complexity, and avoids the need to build and maintain a redundant model. A separate DL model for QR images would add training data requirements, model maintenance burden, and inference overhead for no additional detection capability.

**Consequences:** F-04 quality is directly dependent on F-01 phishing URL analysis quality. QR codes containing non-URL content (contact cards, WiFi credentials, plain text, calendar events) must be handled gracefully — the system must not attempt to analyse non-URL content as a URL. Malformed or unreadable QR codes must produce an appropriate error response.

**Related Documents:** CSHAKTI-CONST-001 §5.1 (F-04), ADR-008

---

## ADR-024 — Mule Account Detection Dataset Limitations

| Field | Value |
|---|---|
| **Decision ID** | ADR-024 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The Elliptic and Elliptic2 datasets are used as research reference datasets for F-07 Mule Account Detection. These datasets represent cryptocurrency transaction networks, not bank mule accounts. This domain mismatch is a documented limitation that must appear prominently in all F-07 documentation and user-facing output. |

**Context:** F-07 Mule Account Detection is classified Research/Experimental. Publicly available labelled datasets for bank mule account detection do not exist due to privacy and regulatory constraints. Elliptic and Elliptic2 are the most relevant publicly available financial network datasets, but they represent cryptocurrency transaction graphs — not traditional bank account behaviour. Using them for research requires explicitly acknowledging this limitation.

**Options Considered:**
- Use Elliptic/Elliptic2 without documenting limitations (rejected — dishonest)
- Use Elliptic/Elliptic2 with prominent limitation documentation (selected)
- Decline to include F-07 in Phase 1 scope (rejected — feature is approved as Research/Experimental)
- Attempt to construct a synthetic bank mule dataset (not approved for Phase 1)

**Chosen Option:** Use Elliptic/Elliptic2 as research reference with prominent limitation documentation.

**Reason:** The research value of F-07 is in developing the detection methodology and pipeline, even if the training dataset is a proxy rather than a direct match. The limitation must be prominently documented so that F-07 outputs are never presented to users as definitive bank mule detection. Dishonest documentation of dataset applicability is not acceptable under CyberShakti's product principles.

**Consequences:** All F-07 documentation must state the dataset domain mismatch clearly. F-07 user-facing output must include a disclaimer about the experimental nature of the assessment. Real-world bank mule account detection applicability requires separate validation with domain-appropriate data, which is not available in Phase 1.

**Related Documents:** CSHAKTI-CONST-001 §3.2, §3.5, §5.1 (F-07), ADR-011

---

## ADR-025 — Phase 1 = Responsive Web Application; Native Apps Deferred

| Field | Value |
|---|---|
| **Decision ID** | ADR-025 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | CyberShakti Phase 1 is delivered as a responsive web application only. Native Android and iOS applications are deferred to future phases. |

**Context:** Building a responsive web application and native mobile applications simultaneously in Phase 1 would spread development effort across three different codebases and delivery targets. The responsive web application approach allows mobile users to access CyberShakti through their mobile browser while the team focuses on building quality features.

**Options Considered:**
- Responsive web application only (selected for Phase 1)
- Native Android application only
- Responsive web + native Android simultaneously
- Progressive Web App (PWA)
- React Native cross-platform app

**Chosen Option:** Responsive web application for Phase 1.

**Reason:** A responsive web application reaches all device types (desktop, tablet, mobile) through a single codebase without requiring app store distribution. This maximises Phase 1 development efficiency. Mobile-first UX design ensures the experience is good on the devices most commonly used by Indian consumers. Native apps are not excluded from future phases — they are deferred, not rejected.

**Consequences:** Android OS-level integrations (call screening, notification permissions beyond browser notifications) are not available in Phase 1. F-08 Scam Call Blocking is bounded to in-app lookup (ADR-018). Mobile browser compatibility must be validated during UI/UX design.

**Related Documents:** CSHAKTI-CONST-001 §11, ADR-018

---

## ADR-026 — Security Configuration Parameters Are TBD Pending Benchmarking

| Field | Value |
|---|---|
| **Decision ID** | ADR-026 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The following security configuration parameters are approved in principle but their specific values are TBD pending security benchmarking and threat-model review: Argon2id memory cost, time cost, parallelism factor; JWT algorithm selection, access token expiry, refresh token lifetime; rate limiting thresholds for all public endpoints. |

**Context:** Security configuration parameters must be tuned to the specific deployment environment and threat model. Locking specific values in Phase 1 documentation before benchmarking has been performed would either produce insecure settings (too weak) or unusably slow settings (too aggressive). The correct approach is to establish the framework and defer specific values to the security benchmarking activity during engineering design or implementation.

**Options Considered:**
- Lock specific values in Phase 1 documentation (rejected — premature without benchmarking)
- Defer all security decisions entirely (rejected — technology choices can be locked)
- Lock technology choices, mark specific parameters as TBD (selected)

**Chosen Option:** Lock technology choices (Argon2id, JWT, AES-256-GCM, rate limiting required); mark specific configuration values as TBD.

**Reason:** The technology choices are stable and well-justified. The specific configuration values depend on the deployment hardware, expected user load, and threat model — none of which are fully characterised at Phase 1 documentation stage. Arbitrarily set values that are not benchmarked are a security risk.

**Consequences:** No developer or AI coding tool may permanently set these values without a documented benchmarking result. All security configuration must be externalised as configurable parameters, not hard-coded constants. A security benchmarking task must be included in the Stage 3 development plan.

**Related Documents:** CSHAKTI-CONST-001 §8.4, §8.5, §8.9, ADR-021

---

## ADR-027 — PII Protection: Minimization and Appropriate Protection Principle

| Field | Value |
|---|---|
| **Decision ID** | ADR-027 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | Sensitive personal data must be minimized, protected at rest using appropriate encryption and access controls, and never stored unnecessarily in plaintext. This principle governs all features that handle personal data. |

**Context:** A cybersecurity platform handling user data about threats, security posture, and files must apply strong PII protection principles. The principle is stated as a design mandate rather than as specific technical controls, because the appropriate controls vary by data type and sensitivity.

**Options Considered:**
- Absolute rule: "no PII in plaintext at rest under any circumstances"
- Minimization + appropriate protection principle (selected)
- No formal PII principle (rejected)

**Chosen Option:** Minimization + appropriate protection principle.

**Reason:** The absolute rule was replaced with the minimization principle because different types of personal data warrant different levels of protection. A username displayed in a UI does not require the same protection as an encrypted file or a stored threat assessment. The principle requires appropriate controls for each data type, with a strong bias towards minimization (don't collect it if you don't need it) and explicit prohibition on unnecessary plaintext storage of sensitive data.

**Consequences:** Every feature that collects personal data must justify what it collects, document how it is protected, and confirm it is not stored unnecessarily in plaintext. Data classification (public, internal, sensitive, highly sensitive) must be defined during engineering design.

**Related Documents:** CSHAKTI-CONST-001 §8.11, §9

---

## ADR-028 — Formal 6-Step Change Control Process

| Field | Value |
|---|---|
| **Decision ID** | ADR-028 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | All changes to locked requirements, technology decisions, architecture decisions, and feature scope must follow the 6-step change control process defined in CSHAKTI-CONST-001 §14. |

**Context:** AI-assisted development tools and fast-moving development teams create a risk of undocumented, unreviewed changes to project foundations. A formal change control process ensures that all significant changes are visible, justified, and approved before being acted upon.

**Options Considered:**
- No formal change control (rejected — creates documentation drift)
- Informal change control (verbal or Slack-based approvals)
- Formal 6-step change control process (selected)

**Chosen Option:** Formal 6-step process: Identify → Explain → Identify Impact → Describe Consequences → Record → Approve.

**Reason:** A documented, traceable change control process is the only way to maintain the integrity of the documentation hierarchy as the project evolves. Informal processes produce undocumented changes that are invisible to downstream consumers (AI tools, new team members, auditors).

**Consequences:** Every change to a locked item must be traceable in `docs/00-decisions.md`. A change that has been recorded but not yet approved has **Pending** status and must not be acted upon. This process applies to all content in the constitution, all ADRs, all PRD acceptance criteria, all TRD specifications, and all SRS requirements.

**Related Documents:** CSHAKTI-CONST-001 §14, ADR-015

---

## ADR-029 — Feature Classification Tiers Are Locked

| Field | Value |
|---|---|
| **Decision ID** | ADR-029 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | The feature classification tiers defined in CSHAKTI-CONST-001 §5.1 are locked. Developers and AI coding tools may not reassign tiers without following the change control process. |

**Context:** Without an explicit lock on the classification table, there is a risk that AI coding tools or developers might silently reassign feature tiers — for example, treating a Research/Experimental feature as Core MVP and attempting to build it to a production-grade standard not achievable in Phase 1, or conversely deprioritising a Core MVP feature.

**Options Considered:**
- Allow autonomous tier reassignment by the development team
- Lock tiers with change control required for reassignment (selected)

**Chosen Option:** Lock tiers; change control required for reassignment.

**Reason:** The classification tiers were deliberated and locked for specific reasons. F-06 (Deepfake Detection) and F-07 (Mule Account Detection) are Research/Experimental because production-grade performance cannot be guaranteed in Phase 1 — not because they are unimportant. Reclassifying them upward without empirical evidence would be dishonest. Reclassifying Core MVP features downward without justification would reduce the product's value.

**Consequences:** All 14 feature tiers are as defined in CSHAKTI-CONST-001 §5.1. Any proposed reassignment requires a recorded and approved change decision explaining why the tier is no longer appropriate.

**Related Documents:** CSHAKTI-CONST-001 §4, §5, ADR-002, ADR-028

---

## ADR-030 — Regulatory References Are Compliance Considerations Requiring Legal Verification

| Field | Value |
|---|---|
| **Decision ID** | ADR-030 |
| **Date** | 2026-08-15 |
| **Status** | Accepted |
| **Decision** | References to IT Act 2000, DPDP Act 2023, RBI/NPCI guidelines, and data residency in CyberShakti documentation are compliance consideration areas. They do not constitute legal compliance. Specific legal obligations must be verified with qualified legal counsel. |

**Context:** A product operating in India's digital space must be aware of relevant regulatory frameworks. However, referencing regulations in documentation without legal review risks asserting specific obligations that may be incorrect, incomplete, or misinterpreted. Incorrect compliance claims are both a legal risk and a credibility risk.

**Options Considered:**
- Do not reference regulatory frameworks at all
- Reference frameworks as definitive legal obligations (rejected — requires legal expertise)
- Reference frameworks as compliance consideration areas requiring verification (selected)

**Chosen Option:** Reference as compliance consideration areas requiring authoritative legal verification.

**Reason:** Complete regulatory unawareness would be irresponsible. Asserting specific legal obligations without qualified legal review would be incorrect and potentially misleading. Flagging frameworks as awareness areas that require legal verification is the honest and responsible position.

**Consequences:** No CyberShakti document may assert specific legal obligations without an authoritative source reference. No user-facing material may claim regulatory compliance without proper legal verification. Legal counsel must review regulatory obligations before launch.

**Related Documents:** CSHAKTI-CONST-001 §10, ADR-016

---

## ADR-031 — S3-Compatible Object Storage: Provider TBD

| Field | Value |
|---|---|
| **Decision ID** | ADR-031 |
| **Date** | 2026-08-15 |
| **Status** | Open |
| **Decision** | S3-compatible object storage is required for encrypted file storage, uploaded media (screenshots, QR code images), and model artefacts. The specific provider is unresolved. |

**Context:** Multiple features (F-10 Secure File Encryption, F-03 Screenshot Scam Scanner, F-04 QR Code Scam Scanner, MLflow model artefacts) require object storage. Using S3-compatible storage provides provider flexibility, but the specific provider must be selected before implementation begins.

**Options Considered:**
- AWS S3 (native)
- Cloudflare R2 (S3-compatible, no egress fees)
- Backblaze B2 (S3-compatible, low cost)
- MinIO (self-hosted S3-compatible)
- DigitalOcean Spaces (S3-compatible)

**Resolution Required:** Provider selection requires evaluation of: (a) cost at expected storage and transfer volumes, (b) data residency — whether data can be stored in India or a nearby region, (c) compatibility with the selected backend deployment target (ADR-004 consequence), (d) reliability and SLA, (e) integration complexity. The decision must be recorded as an update to this ADR before storage-dependent features are implemented.

**Consequences:** All object storage access must use S3-compatible APIs to preserve provider portability. No provider-specific SDK features may be used that would create lock-in without a recorded change decision. Uploaded user media must be stored with appropriate access controls and encryption.

**Related Documents:** CSHAKTI-CONST-001 §6.12, ADR-005, ADR-027

---

## ADR-032 — Threat Intelligence Sources: Selection TBD

| Field | Value |
|---|---|
| **Decision ID** | ADR-032 |
| **Date** | 2026-08-15 |
| **Status** | Open |
| **Decision** | CyberShakti requires threat intelligence and reputation data sources for phishing URL detection (F-01), QR code scanning (F-04), phone number risk assessment (F-08), and location-based scam alerts (F-13). The specific sources are unresolved. |

**Context:** Multiple features depend on access to threat intelligence and reputation data. The quality, freshness, coverage, and cost of threat intelligence sources directly affect detection quality. Sources must be reputable, maintained, and have acceptable licensing terms.

**Options Considered:**
- PhishTank (free, community-contributed phishing URL data)
- URLhaus (abuse.ch — malicious URL data)
- Google Safe Browsing API (free tier available)
- VirusTotal API (commercial tiers)
- CERT-In threat feeds (India-specific)
- Commercial threat intelligence providers
- Self-built threat database from community/user reports

**Resolution Required:** Each feature's threat intelligence requirement must be evaluated separately. Selection criteria: (a) data quality and freshness, (b) India-specific threat coverage where relevant, (c) API licensing terms and usage limits, (d) cost at expected query volume, (e) data privacy terms (user query data must not be exposed to third parties without consent). Phone number reputation data for F-08 requires separate sourcing evaluation from URL reputation data for F-01/F-04.

**Consequences:** Features F-01, F-04, F-08, and F-13 cannot be fully implemented until threat intelligence sources are selected and integrated. The quality of these features is bounded by the quality of the selected intelligence sources. Source selection must be recorded as an update to this ADR before implementation begins.

**Related Documents:** CSHAKTI-CONST-001 §3.1, §5.1 (F-01, F-04, F-08, F-13), ADR-008, ADR-023

---

*End of CyberShakti Decision Log — CSHAKTI-ADR-LOG-001 v1.0.0*

*This is a living document. New ADRs and amendments to existing ADRs are added throughout the project lifecycle following the change control process defined in CSHAKTI-CONST-001 §14.*
