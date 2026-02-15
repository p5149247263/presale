from __future__ import annotations

import re

from app.core.llm_runtime import get_llm_config
from app.models.schemas import Citation
from app.models.schemas import BrainstormResponse, ClarificationItem
from app.services.llm import LLMClient
from app.services.vector_store import LocalVectorStore


class Brainstormer:
    _HEADING_HINTS = [
        "functional requirements",
        "technical requirements",
        "executive summary",
        "responses must include",
        "proposals will be evaluated",
        "expected annual budget range",
        "vendor must provide",
        "general",
    ]
    def __init__(self, vector_store: LocalVectorStore) -> None:
        self.vector_store = vector_store
        cfg = get_llm_config().model_copy(update={"temperature": 0.3, "max_tokens": 700})
        self.llm = LLMClient(cfg)

    @staticmethod
    def _keywords(text: str) -> list[str]:
        stop = {
            "the", "and", "for", "with", "that", "this", "from", "into", "your", "what", "when", "where", "how",
            "should", "could", "would", "will", "about", "next", "rfp", "client", "project", "include", "plan",
            "need", "have", "has", "had", "our", "their", "them", "they", "then", "than", "are", "was", "were",
            "you", "but", "not", "can", "any",
        }
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
        ranked: list[str] = []
        for t in tokens:
            if t in stop:
                continue
            if t not in ranked:
                ranked.append(t)
        return ranked[:8]

    @staticmethod
    def _has_any(text: str, terms: list[str]) -> bool:
        lower = text.lower()
        return any(term in lower for term in terms)

    def _intent(self, prompt: str, context: str) -> str:
        p = prompt.lower()
        q = f"{prompt}\n{context}".lower()
        # Prioritize direct user ask over retrieved context.
        if self._has_any(p, ["risk", "pitfall", "pitfalls", "failure", "blocker"]):
            return "risk"
        if self._has_any(p, ["cost", "pricing", "budget", "roi"]):
            return "cost"
        if self._has_any(p, ["security", "privacy", "compliance", "soc2", "iso", "hipaa", "gdpr"]):
            return "compliance"
        if self._has_any(p, ["upsell", "cross-sell", "cross sell", "expansion", "additional services"]):
            return "upsell"
        if self._has_any(p, ["latency", "sla", "performance", "scale"]):
            return "performance"
        if self._has_any(p, ["integration", "api", "crm", "erp", "sso"]):
            return "integration"
        if self._has_any(q, ["cost", "pricing", "budget", "roi"]):
            return "cost"
        if self._has_any(q, ["security", "privacy", "compliance", "soc2", "iso", "hipaa", "gdpr"]):
            return "compliance"
        if self._has_any(q, ["risk", "pitfall", "pitfalls", "failure", "blocker"]):
            return "risk"
        if self._has_any(q, ["latency", "sla", "performance", "scale"]):
            return "performance"
        if self._has_any(q, ["integration", "api", "crm", "erp", "sso"]):
            return "integration"
        return "general"

    @staticmethod
    def _safe_topic(keywords: list[str]) -> str:
        if not keywords:
            return "domain"
        banned = {"pitfall", "pitfalls", "reduce", "include", "next", "what", "slow", "fast", "cheap", "expensive"}
        for k in keywords:
            if k not in banned:
                return k
        return "domain"

    def _build_opportunities(self, prompt: str, context: str, keywords: list[str], intent: str) -> list[str]:
        opportunities: list[str] = []
        p = prompt.lower()
        q = f"{prompt}\n{context}".lower()

        if intent == "risk":
            return [
                "Offer a risk-discovery workshop to lock scope, dependencies, and acceptance criteria early.",
                "Add governance package: quality gates, human review checkpoints, and release controls.",
                "Propose pilot-first delivery with explicit exit criteria before scale-up.",
            ]
        if intent == "cost":
            return [
                "Offer FinOps optimization and token-cost governance as an add-on.",
                "Package phased scope with strict phase-1 boundaries to reduce implementation spend.",
                "Include model-routing strategy (small model first, premium model fallback) to control token cost.",
            ]
        if intent == "compliance":
            return [
                "Upsell compliance automation pack: policy checks, audit reports, and control mapping.",
                "Include privacy-by-design controls: PII redaction, retention guardrails, and access governance.",
                "Offer governance operations bundle with evidence-ready reporting and periodic control reviews.",
            ]
        if intent == "performance":
            return [
                "Propose a premium low-latency tier with caching and dedicated inference capacity.",
                "Add workload profiling and capacity planning package before production go-live.",
                "Include SLO monitoring with proactive performance incident response runbooks.",
            ]
        if intent == "integration":
            return [
                "Include integration accelerator bundle for faster CRM/ERP onboarding.",
                "Offer API contract hardening and test harness package for phase-1 systems.",
                "Propose event-driven integration blueprint to reduce coupling and future change cost.",
            ]
        if intent == "upsell":
            return [
                "Upsell managed AI governance package (policy controls, review workflows, audit trails).",
                "Offer observability and evaluation operations as a recurring managed service.",
                "Propose domain accelerator bundle to shorten phase-2 delivery timelines.",
            ]

        # For generic intent, rely on user prompt terms (not retrieved context) to avoid drift.
        if self._has_any(p, ["cost", "pricing", "budget", "roi"]):
            opportunities.append("Offer FinOps optimization and token-cost governance as an add-on.")
        if self._has_any(p, ["latency", "sla", "performance", "scale"]):
            opportunities.append("Propose a premium low-latency tier with caching and dedicated inference capacity.")
        if self._has_any(p, ["security", "privacy", "compliance", "soc2", "iso", "hipaa", "gdpr"]):
            opportunities.append("Upsell compliance automation pack: policy checks, audit reports, and control mapping.")
        if self._has_any(p, ["integration", "api", "crm", "erp", "sso"]):
            opportunities.append("Include integration accelerator bundle for faster CRM/ERP onboarding.")
        if self._has_any(p, ["rag", "knowledge", "search", "citation"]):
            opportunities.append("Propose managed RAG operations with retrieval quality monitoring and re-index SLAs.")

        if not opportunities:
            k = ", ".join(keywords[:3]) if keywords else "business KPIs"
            opportunities = [f"Package a discovery sprint focused on {k}."]

        defaults = [
            "Propose phased rollout with measurable business outcomes per phase.",
            "Offer managed evaluation and monitoring as a recurring service.",
            "Add reusable accelerator templates to reduce delivery effort and bid risk.",
        ]
        for item in defaults:
            if len(opportunities) >= 3:
                break
            if item not in opportunities:
                opportunities.append(item)
        return opportunities[:3]

    def _build_differentiators(self, prompt: str, context: str, keywords: list[str], intent: str) -> list[str]:
        diffs = [
            "Traceable outputs with citation-level provenance for every major recommendation.",
            "Human-in-the-loop checkpoints before final proposal submission.",
        ]
        if intent in {"compliance", "risk"}:
            diffs.append("Governance-by-design with risk register, control mapping, and audit logs.")
        elif intent == "upsell":
            diffs.append("Expansion-ready solution packaging with clear optional service bundles and value metrics.")
        elif intent == "cost":
            diffs.append("Cost-first solution design with explicit trade-offs and sensitivity analysis.")
        elif self._has_any(prompt.lower(), ["speed", "timeline", "delivery"]):
            diffs.append("Accelerator-led delivery approach to reduce time-to-value.")
        else:
            topic = self._safe_topic(keywords)
            diffs.append(f"Reusable {topic} accelerators from prior proposals and case studies.")
        defaults = [
            "Outcome-driven proposal structure with explicit assumptions and traceability.",
            "Cost and risk sensitivity analysis for best/expected/worst scenarios.",
        ]
        for item in defaults:
            if len(diffs) >= 3:
                break
            if item not in diffs:
                diffs.append(item)
        return diffs[:3]

    def _build_clarifications(self, prompt: str, keywords: list[str], intent: str) -> list[ClarificationItem]:
        q = prompt.lower()
        questions: list[ClarificationItem] = []
        if intent == "risk":
            return [
                ClarificationItem(question="Which delivery risks are unacceptable to the client (scope, timeline, compliance, quality)?", reason="Risk prioritization"),
                ClarificationItem(question="What assumptions require client sign-off before build starts?", reason="Scope control"),
                ClarificationItem(question="What are the go/no-go checkpoints for moving from pilot to production?", reason="Governance and release readiness"),
            ]
        if intent == "compliance":
            return [
                ClarificationItem(question="Which compliance frameworks are mandatory at go-live vs phase-2?", reason="Control scope and timeline"),
                ClarificationItem(question="What data classes (PII/PHI/PCI) are in scope and what handling controls are required?", reason="Privacy control design"),
                ClarificationItem(question="What audit evidence cadence is expected by security/compliance stakeholders?", reason="Operational governance"),
            ]
        if intent == "cost":
            return [
                ClarificationItem(question="What budget guardrails and target ROI window should the proposal optimize for?", reason="Cost model and packaging"),
                ClarificationItem(question="Which cost drivers are strict constraints (tokens, infra, staffing, timeline)?", reason="Cost trade-off design"),
                ClarificationItem(question="Which features can be deferred to phase-2 without affecting business value?", reason="Scope right-sizing"),
            ]
        if intent == "upsell":
            return [
                ClarificationItem(question="Which optional services have highest buyer interest (governance, MLOps, analytics, support)?", reason="Upsell prioritization"),
                ClarificationItem(question="What commercial model is preferred for add-ons (fixed scope, retainer, usage-based)?", reason="Packaging strategy"),
                ClarificationItem(question="Which phase-2 capabilities can be positioned as expansion opportunities?", reason="Roadmap-led upsell"),
            ]

        if self._has_any(q, ["cloud", "aws", "azure", "gcp", "on-prem"]):
            questions.append(ClarificationItem(question="Is there a mandated primary cloud or allowed multi-cloud approach?", reason="Architecture and commercial impact"))
        if self._has_any(q, ["cost", "pricing", "budget", "roi"]):
            questions.append(ClarificationItem(question="What budget guardrails and target ROI window should the proposal optimize for?", reason="Cost model and packaging"))
        if self._has_any(q, ["latency", "sla", "scale", "users"]):
            questions.append(ClarificationItem(question="What are the expected peak user concurrency and latency SLAs by workflow?", reason="Capacity and sizing assumptions"))
        if self._has_any(q, ["security", "privacy", "compliance", "soc2", "hipaa", "gdpr"]):
            questions.append(ClarificationItem(question="Which compliance frameworks are mandatory at go-live vs phase-2?", reason="Control scope and timeline"))
        if self._has_any(q, ["integration", "api", "crm", "erp", "sso"]):
            questions.append(ClarificationItem(question="Which source systems are in-scope for phase-1 integration?", reason="Delivery scope and dependencies"))

        if not questions:
            topic = self._safe_topic(keywords)
            questions = [
                ClarificationItem(question=f"What are the top 3 success metrics for {topic} outcomes?", reason="Proposal targeting"),
                ClarificationItem(question="What timeline and decision gates does the client procurement process require?", reason="Execution planning"),
                ClarificationItem(question="What constraints are non-negotiable versus preferred?", reason="Trade-off management"),
            ]
        defaults = [
            ClarificationItem(question="What timeline and decision gates does the client procurement process require?", reason="Execution planning"),
            ClarificationItem(question="What constraints are non-negotiable versus preferred?", reason="Trade-off management"),
        ]
        for item in defaults:
            if len(questions) >= 3:
                break
            if not any(q.question == item.question for q in questions):
                questions.append(item)
        return questions[:3]

    @staticmethod
    def _clean_generated_answer(generated: str, prompt: str, context: str) -> str:
        text = (generated or "").strip()
        if text.startswith("[MOCK-") or "You are an AI presales strategist" in text:
            return ""
        return text[:1000]

    def run(self, prompt: str) -> BrainstormResponse:
        hits = self.vector_store.query(prompt, k=5)
        citations = self._select_citations(hits)
        context = "\n".join([f"- {x.chunk.text[:180]}" for x in hits])
        keywords = self._keywords(f"{prompt}\n{context}")
        intent = self._intent(prompt, context)
        generated = self.llm.complete(
            "You are an AI presales strategist. Draft a concise answer and opportunity ideas.\n"
            f"Prompt: {prompt}\n"
            f"Context:\n{context}"
        )
        answer = self._clean_generated_answer(generated, prompt, context)
        if not answer:
            fallback_by_intent = {
                "cost": "Reduce proposal cost by narrowing phase-1 scope, reusing accelerator templates, and enforcing token/infra budgets with sensitivity scenarios.",
                "compliance": "Prioritize compliance upsells that are auditable at go-live: control mapping, policy enforcement, and evidence-ready reporting.",
                "risk": "Key pitfalls are unclear scope, weak data readiness, and missing governance; mitigate with phased delivery, explicit assumptions, and review checkpoints.",
                "performance": "Prevent performance surprises by setting workflow-level SLAs early, load-testing critical paths, and using caching plus autoscaling.",
                "integration": "De-risk integration by fixing phase-1 system boundaries, API contracts, and dependency ownership before build kickoff.",
                "upsell": "Prioritize high-value upsells tied to business outcomes: governance operations, managed evaluation/monitoring, and accelerator-led phase-2 expansion.",
                "general": "Start with a measurable pilot, keep assumptions explicit, and separate phase-1 essentials from phase-2 options to improve win probability.",
            }
            answer = fallback_by_intent[intent]

        return BrainstormResponse(
            answer=answer,
            opportunities=self._build_opportunities(prompt, context, keywords, intent),
            differentiators=self._build_differentiators(prompt, context, keywords, intent),
            clarification_list=self._build_clarifications(prompt, keywords, intent),
            citations=citations,
        )

    def _select_citations(self, hits) -> list[Citation]:
        filtered = []
        for h in hits:
            section = (h.chunk.section or "").strip().lower()
            text = (h.chunk.text or "").strip().lower()
            if any(hint in section for hint in self._HEADING_HINTS):
                continue
            if len(text.split()) < 6:
                continue
            filtered.append(h)

        source = filtered if filtered else hits
        deduped: list[Citation] = []
        seen: set[tuple[str, int, str]] = set()
        for c in self.vector_store.citations_from_results(source):
            key = (c.doc_id, c.page, c.section)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(c)
        return deduped[:5]
