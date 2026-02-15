from app.agents.brainstormer import Brainstormer
from app.services.parser import parse_txt
from app.services.vector_store import LocalVectorStore


def _brainstormer() -> Brainstormer:
    payload = b"""
The solution MUST support SOC2 and encryption controls.
The solution SHOULD provide low latency responses under 2.5 seconds.
The platform should integrate with CRM and ERP APIs.
"""
    chunks = parse_txt("doc-brain", payload)
    vs = LocalVectorStore()
    vs.upsert(chunks)
    return Brainstormer(vs)


def test_brainstorm_output_varies_by_prompt_theme():
    b = _brainstormer()
    cost = b.run("How can we optimize budget and pricing for this deal?")
    security = b.run("What compliance and security upsells should we propose?")

    assert cost.opportunities != security.opportunities
    assert cost.clarification_list != security.clarification_list


def test_brainstorm_security_prompt_includes_compliance_clarification():
    b = _brainstormer()
    out = b.run("Need SOC2 and HIPAA strategy")
    questions = " ".join([x.question.lower() for x in out.clarification_list])
    assert "compliance" in questions or "framework" in questions


def test_brainstorm_returns_non_echo_answer_and_minimum_lists():
    b = _brainstormer()
    out = b.run("How can we reduce proposal cost?")
    assert "You are an AI presales strategist" not in out.answer
    assert "[MOCK-" not in out.answer
    assert len(out.opportunities) >= 3
    assert len(out.differentiators) >= 3
    assert len(out.clarification_list) >= 3


def test_pitfalls_prompt_has_risk_fallback_and_clean_topic_words():
    b = _brainstormer()
    out = b.run("What are pitfalls")
    assert "pitfalls are" in out.answer.lower() or "key pitfalls" in out.answer.lower()
    diff_text = " ".join(out.differentiators).lower()
    assert "pitfalls accelerators" not in diff_text
    opp_text = " ".join(out.opportunities).lower()
    assert "finops" not in opp_text
    assert "compliance automation" not in opp_text
    assert "rag operations" not in opp_text


def test_compliance_prompt_does_not_mix_cost_upsells():
    b = _brainstormer()
    out = b.run("What compliance and security upsells should we include?")
    opp_text = " ".join(out.opportunities).lower()
    assert "finops" not in opp_text
    assert "token-cost" not in opp_text
    assert "compliance" in opp_text or "privacy" in opp_text


def test_upsell_prompt_not_forced_to_cost_intent():
    b = _brainstormer()
    out = b.run("What upsell opportunities should we include?")
    opp_text = " ".join(out.opportunities).lower()
    assert "upsell" in opp_text or "expansion" in opp_text or "managed" in opp_text
    assert "token-cost" not in opp_text
