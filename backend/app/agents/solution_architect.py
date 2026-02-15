from __future__ import annotations

from app.core.llm_runtime import get_llm_config
from app.models.schemas import ArchitectureOption, RequirementMatrix
from app.services.llm import LLMClient
from app.services.vector_store import LocalVectorStore


class SolutionArchitect:
    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store
        cfg = get_llm_config().model_copy(update={"temperature": 0.2, "max_tokens": 900})
        self.llm = LLMClient(cfg)

    def run(self, reqs: RequirementMatrix) -> list[ArchitectureOption]:
        results = self.vector_store.query("architecture rag fine-tune streaming batch", k=5)
        citations = self.vector_store.citations_from_results(results)
        req_context = "\n".join([f"- {r.req_type.value}: {r.text[:160]}" for r in reqs.requirements[:8]])
        plan_a_summary = self.llm.complete(
            "Create a 2-3 sentence architecture recommendation for Plan A (RAG-first) for an AI presales proposal.\n"
            f"Requirements context:\n{req_context}"
        )
        plan_b_summary = self.llm.complete(
            "Create a 2-3 sentence architecture recommendation for Plan B (fine-tune hybrid) for an AI presales proposal.\n"
            f"Requirements context:\n{req_context}"
        )

        plan_a = ArchitectureOption(
            name="Plan A - RAG First",
            summary=plan_a_summary[:400],
            components=["API Gateway", "Orchestrator", "Vector DB", "LLM", "Guardrails", "Observability"],
            data_flow=[
                "Source systems -> ETL -> Document store -> Chunk/Embed -> Vector DB",
                "User query -> Retriever -> Prompt Builder -> LLM -> Cited Answer",
            ],
            model_flow=["Embed model", "Retrieval reranker", "Hosted foundation model"],
            latency_scalability_notes=[
                "P95 latency target under 2.5s with cache and ANN index.",
                "Horizontal scaling for retrieval and orchestration layers.",
            ],
            integration_plan=["REST APIs for CRM/ERP", "Eventing with queue for async pipelines"],
            mermaid=(
                "graph TD\n"
                "U[User] --> FE[Portal]\n"
                "FE --> ORCH[Orchestrator API]\n"
                "ORCH --> RET[RAG Retriever]\n"
                "RET --> VDB[Vector DB]\n"
                "ORCH --> LLM[LLM Provider]\n"
                "ORCH --> G[Guardrails + Eval]\n"
                "ORCH --> LOG[Audit + Monitoring]"
            ),
            citations=citations,
        )

        plan_b = ArchitectureOption(
            name="Plan B - Domain Fine-Tune Hybrid",
            summary=plan_b_summary[:400],
            components=["Feature Store", "Fine-tuned model", "RAG layer", "Human review console"],
            data_flow=["Data lake -> Labeling -> Fine-tune -> Inference endpoint", "RAG sidecar for policy docs"],
            model_flow=["Fine-tuned open-source model", "Fallback hosted LLM"],
            latency_scalability_notes=[
                "Lower per-request latency for known intents.",
                "Higher MLOps overhead and governance requirements.",
            ],
            integration_plan=["CI/CD for model registry", "MLflow for versioning and drift alerts"],
            mermaid=(
                "graph LR\n"
                "DS[Data Sources] --> TR[Training Pipeline]\n"
                "TR --> REG[Model Registry]\n"
                "REG --> INF[Inference API]\n"
                "Q[Query] --> RAG[RAG Layer]\n"
                "RAG --> INF"
            ),
            citations=citations,
        )

        return [plan_a, plan_b]
