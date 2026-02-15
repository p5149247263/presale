from __future__ import annotations

from app.models.schemas import GuardrailResult


def evaluate_output(citation_count: int, confidence: float, min_confidence: float = 0.6) -> GuardrailResult:
    pass_citations = citation_count > 0
    pass_conf = confidence >= min_confidence
    hallucination_risk = max(0.0, 1.0 - confidence)

    comments: list[str] = []
    if not pass_citations:
        comments.append("No citations found. Human review required.")
    if not pass_conf:
        comments.append("Confidence below threshold. Human review required.")

    if not comments:
        comments.append("Output passed baseline guardrails.")

    return GuardrailResult(
        pass_citation_check=pass_citations,
        pass_confidence_threshold=pass_conf,
        hallucination_risk_score=hallucination_risk,
        comments=comments,
    )
