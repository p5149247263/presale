from app.services.parser import chunk_text, parse_txt


def test_chunk_text_preserves_section():
    chunks = chunk_text("doc-1", "Section 1: Scope\nMust support SSO.\n\nSection 2: Security\nMust encrypt data.", page=3)
    assert len(chunks) == 2
    assert chunks[0].page == 3
    assert chunks[1].section.lower().startswith("section 2")


def test_parse_txt_basic():
    payload = b"Mandatory: Must support SOC2 controls."
    chunks = parse_txt("doc-2", payload, pii_redaction=True)
    assert len(chunks) == 1
    assert "soc2" in chunks[0].text.lower()
