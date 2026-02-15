# AI Presales Copilot - System Design (v0.1)

## 1. Objective
AI Presales Copilot automates presales for AI/ML/GenAI opportunities by ingesting RFP artifacts, extracting requirements, generating architecture/cloud/cost/risk recommendations, and drafting traceable proposal documents with citations.

## 2. Architecture Overview
The platform uses a modular agentic backend and a React workflow UI.

### Core Modules
- Ingestion + Parser: reads PDF/DOCX/TXT, extracts text chunks, section/page metadata, and optional table-like content.
- Vector/RAG Layer: indexes chunks in a local vector store (FAISS if available, deterministic embedding fallback otherwise); retrieves evidence for generation.
- Agents:
  - RequirementExtractor
  - SolutionArchitect
  - CloudSelector
  - CostEstimator
  - RiskAssessor
  - ProposalWriter
  - Brainstormer
- Guardrails + Evaluation: citation presence checks, confidence thresholds, hallucination risk score, and explicit human review checkpoints.
- Security + Governance: simple RBAC, encrypted document storage, PII redaction option, append-only audit log.
- Async Job Queue: thread-backed queue for heavier operations (requirements extraction and future long-running workflows).
- Export Engine: proposal generation to DOCX/PDF plus appendices (requirements, risks, architecture Mermaid).

### Data Flow
1. User creates project and uploads RFP + annexures + notes.
2. Backend parses files into chunks (`doc_id`, `page`, `section`, `snippet_hash`) and stores encrypted originals.
3. Chunks are embedded/indexed in the vector store.
4. Agents retrieve relevant chunks and generate structured outputs with citations.
5. Guardrail evaluator scores outputs; low-confidence/no-citation outputs are marked for human review.
6. Approved artifacts are composed into proposal outline and exported as DOCX/PDF.
7. Workspace stores versions and allows brainstorming/Q&A over project + KB context.

### Traceability Contract
Every generated artifact includes citation objects:
`{doc_id, page, section, snippet_hash}`.
These are shown in UI and persisted with outputs for auditability.

## 3. Deployment and Ops
- Backend: FastAPI service, stateless API + local persisted JSON stores for demo mode.
- Frontend: Vite React app with stepwise workflow.
- Optional containerized run via Docker Compose.
- CI: backend tests + frontend build validation.

## 4. Extensibility
- LLM Provider abstraction supports `openai`, `anthropic`, `local`, and `mock` modes.
- Vector provider setting supports local FAISS and can be extended to Pinecone/Azure AI Search adapters.
- Job queue can be swapped to Celery/RQ as scale grows.
