from __future__ import annotations

from app.models.schemas import CostAssumption, CostEstimate, CostLineItem
from app.services.vector_store import LocalVectorStore


class CostEstimator:
    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store

    def run(self) -> CostEstimate:
        assumptions = [
            CostAssumption(key="gpu_hours_month", value=320.0, unit="hours"),
            CostAssumption(key="gpu_rate_a10_usd_per_hour", value=1.2, unit="USD/hour"),
            CostAssumption(key="storage_tb", value=10.0, unit="TB"),
            CostAssumption(key="storage_rate_usd_per_tb", value=25.0, unit="USD/TB"),
            CostAssumption(key="egress_tb", value=4.0, unit="TB"),
            CostAssumption(key="egress_rate_usd_per_tb", value=85.0, unit="USD/TB"),
            CostAssumption(key="monthly_prompt_tokens_m", value=120.0, unit="Million tokens"),
            CostAssumption(key="monthly_completion_tokens_m", value=80.0, unit="Million tokens"),
            CostAssumption(key="llm_blended_rate_usd_per_m", value=7.0, unit="USD/M tokens"),
            CostAssumption(key="rag_embedding_tokens_m", value=40.0, unit="Million tokens"),
            CostAssumption(key="embedding_rate_usd_per_m", value=0.3, unit="USD/M tokens"),
        ]

        a = {x.key: x.value for x in assumptions}
        line_items = [
            CostLineItem(
                category="GPU",
                item="Inference + batch processing (A10 equivalent)",
                monthly_cost_usd=a["gpu_hours_month"] * a["gpu_rate_a10_usd_per_hour"],
                notes="Placeholder rate, editable.",
            ),
            CostLineItem(
                category="Storage",
                item="Object + hot vector index",
                monthly_cost_usd=a["storage_tb"] * a["storage_rate_usd_per_tb"],
                notes="Includes snapshots.",
            ),
            CostLineItem(
                category="Networking",
                item="Data egress",
                monthly_cost_usd=a["egress_tb"] * a["egress_rate_usd_per_tb"],
                notes="Assumes internet/API traffic.",
            ),
            CostLineItem(
                category="LLM",
                item="Prompt + completion",
                monthly_cost_usd=(a["monthly_prompt_tokens_m"] + a["monthly_completion_tokens_m"]) * a["llm_blended_rate_usd_per_m"],
                notes="Provider-specific pricing can be swapped.",
            ),
            CostLineItem(
                category="RAG",
                item="Embeddings + retrieval infra",
                monthly_cost_usd=a["rag_embedding_tokens_m"] * a["embedding_rate_usd_per_m"] + 180.0,
                notes="Vector DB + embeddings.",
            ),
            CostLineItem(
                category="Monitoring",
                item="Observability, logging, audit",
                monthly_cost_usd=250.0,
                notes="SIEM/metrics/log retention placeholder.",
            ),
        ]

        expected = round(sum(i.monthly_cost_usd for i in line_items), 2)
        best = round(expected * 0.78, 2)
        worst = round(expected * 1.35, 2)
        citations = self.vector_store.citations_from_results(self.vector_store.query("pricing cost token workload", k=3))

        return CostEstimate(
            assumptions=assumptions,
            line_items=line_items,
            best_case_total=best,
            expected_total=expected,
            worst_case_total=worst,
            citations=citations,
        )
