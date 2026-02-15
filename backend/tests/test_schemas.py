import pytest
from pydantic import ValidationError

from app.models.schemas import Citation


def test_citation_requires_positive_page():
    with pytest.raises(ValidationError):
        Citation(doc_id="d1", page=0, section="S1", snippet_hash="abc")


def test_citation_ok():
    c = Citation(doc_id="d1", page=1, section="S1", snippet_hash="abc")
    assert c.page == 1
