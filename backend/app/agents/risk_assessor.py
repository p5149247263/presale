from __future__ import annotations

from app.models.schemas import RiskCategory, RiskItem, RiskRegister, RequirementMatrix
from app.services.vector_store import LocalVectorStore


class RiskAssessor:
    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store

    def run(self, reqs: RequirementMatrix) -> RiskRegister:
        citations = self.vector_store.citations_from_results(self.vector_store.query("risk privacy hallucination compliance ip bias", k=6))

        risks = [
            RiskItem(
                risk_id="RISK-001",
                category=RiskCategory.PRIVACY,
                description="PII/PHI leakage through prompts, logs, or downstream integrations.",
                likelihood="Medium",
                impact="High",
                mitigations=["PII redaction", "Data minimization", "Encryption at rest/in transit", "Access controls"],
                owner="Security Lead",
                residual_risk="Medium",
                citations=citations,
            ),
            RiskItem(
                risk_id="RISK-002",
                category=RiskCategory.HALLUCINATION,
                description="Unverifiable model responses can impact business decisions.",
                likelihood="Medium",
                impact="High",
                mitigations=["RAG with citations", "Constrained generation", "Eval harness", "Human review checkpoint"],
                owner="AI Lead",
                residual_risk="Medium",
                citations=citations,
            ),
            RiskItem(
                risk_id="RISK-003",
                category=RiskCategory.REGULATORY,
                description="Misalignment with SOC2/ISO controls and sector regulations.",
                likelihood="Low",
                impact="High",
                mitigations=["Control mapping", "Audit trails", "Policy-based retention"],
                owner="Compliance Officer",
                residual_risk="Low",
                citations=citations,
            ),
            RiskItem(
                risk_id="RISK-004",
                category=RiskCategory.OPS,
                description="Model drift and performance degradation over time.",
                likelihood="Medium",
                impact="Medium",
                mitigations=["MLflow versioning", "Drift monitoring", "Rollback strategy", "SLO alerts"],
                owner="MLOps Lead",
                residual_risk="Low",
                citations=citations,
            ),
        ]
        return RiskRegister(risks=risks)
