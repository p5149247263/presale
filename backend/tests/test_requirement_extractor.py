from app.agents.requirement_extractor import RequirementExtractor
from app.models.schemas import RequirementCategory, RequirementType
from app.services.parser import parse_txt
from app.services.vector_store import LocalVectorStore


def test_extractor_filters_headings_and_keeps_actionable_requirements():
    text = b"""
REQUEST FOR PROPOSAL (RFP)

3.3 Functional Requirements (OPTIONAL)

The solution MUST provide citation-grounded answers for every generated response.
The platform MUST support encryption at rest and in transit and role-based access controls.
The solution SHOULD integrate with existing EMR and CRM systems using secure APIs.
Architecture diagram
"""
    chunks = parse_txt("doc-a", text)
    vs = LocalVectorStore()
    vs.upsert(chunks)

    matrix = RequirementExtractor(vs).run("p1")
    req_texts = [r.text.lower() for r in matrix.requirements]

    assert any("citation-grounded" in t for t in req_texts)
    assert any("encryption" in t for t in req_texts)
    assert any("integrate" in t for t in req_texts)

    assert not any("request for proposal" in t for t in req_texts)
    assert not any("functional requirements" in t for t in req_texts)
    assert not any(t.strip() == "architecture diagram" for t in req_texts)


def test_extractor_classifies_type_and_category():
    text = b"The platform MUST support encryption and SOC2 controls."
    chunks = parse_txt("doc-b", text)
    vs = LocalVectorStore()
    vs.upsert(chunks)

    matrix = RequirementExtractor(vs).run("p2")
    assert len(matrix.requirements) == 1
    req = matrix.requirements[0]
    assert req.req_type == RequirementType.MUST
    assert req.category == RequirementCategory.SECURITY
    assert len(req.citations) == 1
