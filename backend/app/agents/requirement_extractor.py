from __future__ import annotations

from collections import Counter
import re

from app.models.schemas import (
    Citation,
    DocumentChunk,
    Requirement,
    RequirementCategory,
    RequirementMatrix,
    RequirementType,
)
from app.services.vector_store import LocalVectorStore


class RequirementExtractor:
    _CATEGORY_TERMS = {
        RequirementCategory.SECURITY: ["security", "privacy", "pii", "phi", "encryption", "rbac", "soc2", "iso", "iam", "access control"],
        RequirementCategory.DATA: ["data", "dataset", "residency", "retention", "lineage", "etl", "warehouse", "lake"],
        RequirementCategory.MODEL: ["model", "llm", "rag", "hallucination", "evaluation", "grounded", "prompt", "fine-tune"],
        RequirementCategory.INTEGRATION: ["api", "integration", "event", "erp", "crm", "webhook", "connector", "sso"],
        RequirementCategory.SLA: ["latency", "uptime", "sla", "p95", "p99", "throughput", "availability"],
        RequirementCategory.COMPLIANCE: ["compliance", "gdpr", "hipaa", "regulatory", "audit", "governance"],
        RequirementCategory.UI: ["ui", "dashboard", "portal", "workflow", "ux", "screen", "interface"],
        RequirementCategory.INFRA: ["cloud", "aws", "azure", "gcp", "on-prem", "kubernetes", "infrastructure"],
    }

    _HEADING_TOKENS = {
        "request for proposal",
        "rfp",
        "table of contents",
        "functional requirements",
        "responses must include",
        "architecture diagram",
        "overview",
        "scope",
        "introduction",
    }

    _ACTION_VERBS = ("must", "shall", "should", "required", "need to", "will ", "supports", "support", "provide", "include")

    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store

    @staticmethod
    def _normalize_line(line: str) -> str:
        line = line.strip()
        line = re.sub(r"^\s*[-*•]\s*", "", line)
        line = re.sub(r"^\s*\d+(\.\d+)*\s*", "", line)
        return line.strip()

    def _is_heading_like(self, text: str) -> bool:
        lower = text.lower().strip(" :.-")
        if not lower:
            return True
        if lower in self._HEADING_TOKENS:
            return True
        if len(lower.split()) <= 6 and not any(v in lower for v in self._ACTION_VERBS):
            return True
        if lower.isupper():
            return True
        if lower.endswith("(optional)") and not any(v in lower for v in self._ACTION_VERBS):
            return True
        return False

    def _looks_like_requirement(self, text: str) -> bool:
        lower = text.lower()
        if len(lower) < 24:
            return False
        if self._is_heading_like(text):
            return False
        if any(token in lower for token in self._HEADING_TOKENS) and not any(v in lower for v in self._ACTION_VERBS):
            return False
        return any(v in lower for v in self._ACTION_VERBS)

    def _classify_type(self, text: str) -> RequirementType:
        lower = text.lower()
        if "must" in lower or "shall" in lower or "mandatory" in lower:
            return RequirementType.MUST
        if "should" in lower or "recommended" in lower:
            return RequirementType.SHOULD
        return RequirementType.NICE

    def _classify_category(self, text: str) -> RequirementCategory:
        lower = text.lower()
        scores = Counter()
        for category, terms in self._CATEGORY_TERMS.items():
            scores[category] = sum(1 for t in terms if t in lower)
        best = scores.most_common(1)[0]
        if best[1] == 0:
            return RequirementCategory.INFRA
        return best[0]

    @staticmethod
    def _dependencies_for(category: RequirementCategory) -> list[str]:
        if category == RequirementCategory.SECURITY:
            return ["Identity provider access", "KMS/secrets setup"]
        if category == RequirementCategory.INTEGRATION:
            return ["Source system API access", "Network allow-listing"]
        if category == RequirementCategory.DATA:
            return ["Data source access", "Data quality baseline"]
        if category == RequirementCategory.MODEL:
            return ["Model endpoint access", "Evaluation dataset"]
        if category == RequirementCategory.SLA:
            return ["Load profile assumptions", "Monitoring/alerting stack"]
        return ["Client data access", "Environment provisioning"]

    @staticmethod
    def _risk_text(req_type: RequirementType) -> str:
        if req_type == RequirementType.MUST:
            return "High risk of non-compliance and proposal disqualification if not met."
        if req_type == RequirementType.SHOULD:
            return "Medium delivery and quality risk if not met."
        return "Lower risk, but may reduce solution competitiveness."

    @staticmethod
    def _citation_from_chunk(chunk: DocumentChunk) -> Citation:
        return Citation(
            doc_id=chunk.doc_id,
            page=chunk.page,
            section=chunk.section,
            snippet_hash=chunk.snippet_hash,
        )

    def run(self, project_id: str) -> RequirementMatrix:
        reqs: list[Requirement] = []
        seen_texts: set[str] = set()

        for chunk in self.vector_store.all_chunks():
            for line in chunk.text.splitlines():
                text = self._normalize_line(line)
                if not self._looks_like_requirement(text):
                    continue
                dedupe_key = text.lower()
                if dedupe_key in seen_texts:
                    continue
                seen_texts.add(dedupe_key)

                req_type = self._classify_type(text)
                category = self._classify_category(text)
                citation = self._citation_from_chunk(chunk)
                confidence = 0.72
                if req_type == RequirementType.MUST:
                    confidence += 0.08
                if category in {RequirementCategory.SECURITY, RequirementCategory.SLA, RequirementCategory.INTEGRATION}:
                    confidence += 0.05

                reqs.append(
                    Requirement(
                        requirement_id=f"REQ-{len(reqs) + 1:03d}",
                        text=text[:300],
                        req_type=req_type,
                        category=category,
                        acceptance_criteria="Validated via traceable test cases, UAT, and stakeholder sign-off against RFP scope.",
                        dependencies=self._dependencies_for(category),
                        risk_if_not_met=self._risk_text(req_type),
                        citations=[citation],
                        confidence=min(0.95, confidence),
                    )
                )

        if not reqs:
            # Fallback: provide minimal traceable output instead of empty matrix.
            results = self.vector_store.query("must should requirement", k=1)
            if results:
                chunk = results[0].chunk
                reqs.append(
                    Requirement(
                        requirement_id="REQ-001",
                        text=chunk.text[:300],
                        req_type=RequirementType.NICE,
                        category=RequirementCategory.INFRA,
                        acceptance_criteria="Manual review required to finalize requirement wording.",
                        dependencies=["Manual analyst validation"],
                        risk_if_not_met="Requirements may be incomplete without manual review.",
                        citations=[self._citation_from_chunk(chunk)],
                        confidence=0.45,
                    )
                )
        return RequirementMatrix(requirements=reqs)
