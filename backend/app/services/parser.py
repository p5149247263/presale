from __future__ import annotations

from io import BytesIO
from pathlib import Path

from app.models.schemas import DocumentChunk
from app.services.storage import LocalStorage
from app.services.pii import redact_pii


def _section_from_line(line: str, current: str) -> str:
    stripped = line.strip()
    if not stripped:
        return current
    if stripped.endswith(":") or stripped.lower().startswith(("section", "1.", "2.", "3.", "4.")):
        return stripped[:120]
    return current


def chunk_text(doc_id: str, text: str, page: int = 1) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    current_section = "General"
    for raw_block in text.split("\n\n"):
        block = raw_block.strip()
        if not block:
            continue
        first_line = block.splitlines()[0]
        current_section = _section_from_line(first_line, current_section)
        snippet_hash = LocalStorage.hash_text(f"{doc_id}|{page}|{current_section}|{block[:200]}")
        chunks.append(
            DocumentChunk(
                doc_id=doc_id,
                page=page,
                section=current_section,
                text=block,
                snippet_hash=snippet_hash,
            )
        )
    return chunks


def parse_txt(doc_id: str, data: bytes, pii_redaction: bool = True) -> list[DocumentChunk]:
    text = data.decode("utf-8", errors="ignore")
    if pii_redaction:
        text = redact_pii(text)
    return chunk_text(doc_id, text, page=1)


def parse_docx(doc_id: str, data: bytes, pii_redaction: bool = True) -> list[DocumentChunk]:
    try:
        from docx import Document as DocxDocument
    except Exception as exc:
        raise ValueError("DOCX parsing requires python-docx dependency") from exc
    doc = DocxDocument(BytesIO(data))
    full_text = "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    if pii_redaction:
        full_text = redact_pii(full_text)
    return chunk_text(doc_id, full_text, page=1)


def parse_pdf(doc_id: str, data: bytes, pii_redaction: bool = True) -> list[DocumentChunk]:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise ValueError("PDF parsing requires pypdf dependency") from exc
    reader = PdfReader(BytesIO(data))
    chunks: list[DocumentChunk] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if pii_redaction:
            text = redact_pii(text)
        chunks.extend(chunk_text(doc_id, text, page=idx))
    return chunks


def parse_file(doc_id: str, file_name: str, data: bytes, pii_redaction: bool = True) -> list[DocumentChunk]:
    suffix = Path(file_name).suffix.lower()
    if suffix == ".txt":
        return parse_txt(doc_id, data, pii_redaction=pii_redaction)
    if suffix == ".docx":
        return parse_docx(doc_id, data, pii_redaction=pii_redaction)
    if suffix == ".pdf":
        return parse_pdf(doc_id, data, pii_redaction=pii_redaction)
    raise ValueError(f"Unsupported file type: {suffix}")
