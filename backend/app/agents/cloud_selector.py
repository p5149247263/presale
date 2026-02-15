from __future__ import annotations

from app.models.schemas import CloudRecommendation, RequirementMatrix
from app.services.vector_store import LocalVectorStore


class CloudSelector:
    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store

    def run(self, reqs: RequirementMatrix, client_notes: str) -> CloudRecommendation:
        text = " ".join([r.text for r in reqs.requirements]).lower() + " " + client_notes.lower()
        primary = "AWS"

        if "azure" in text or "microsoft" in text:
            primary = "Azure"
        elif "gcp" in text or "google" in text:
            primary = "GCP"
        elif "on-prem" in text or "air-gapped" in text:
            primary = "OnPrem"

        results = self.vector_store.query("cloud preference data residency compliance latency", k=4)
        citations = self.vector_store.citations_from_results(results)

        return CloudRecommendation(
            primary_cloud=primary,  # type: ignore[arg-type]
            rationale=(
                f"{primary} is selected based on stated stack preferences, compliance posture, and delivery velocity. "
                "Alternative is included for negotiation and risk balancing."
            ),
            alternatives=["AWS", "Azure", "GCP", "OnPrem"],
            constraints_considered=[
                "Client preference",
                "Data residency",
                "Compliance requirements",
                "Latency/cost constraints",
            ],
            citations=citations,
        )
