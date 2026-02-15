from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parent
sample_dir = ROOT / "app" / "data" / "sample_input"
sample_dir.mkdir(parents=True, exist_ok=True)

text = (sample_dir / "mock_rfp_healthcare.txt").read_text(encoding="utf-8")


def create_minimal_pdf(path: Path, lines: list[str]) -> None:
    body = ["BT", "/F1 10 Tf", "50 780 Td"]
    for idx, line in enumerate(lines[:70]):
        safe = line.replace("(", "[").replace(")", "]")
        if idx > 0:
            body.append("0 -14 Td")
        body.append(f"({safe[:110]}) Tj")
    body.append("ET")
    stream = "\n".join(body).encode("latin-1", errors="ignore")

    objects = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n")
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(b"5 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj\n")

    content = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(content))
        content.extend(obj)

    xref_pos = len(content)
    content.extend(f"xref\n0 {len(objects)+1}\n".encode("ascii"))
    content.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        content.extend(f"{off:010d} 00000 n \n".encode("ascii"))
    content.extend(
        f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(content)


def create_minimal_docx(path: Path, title: str, paragraphs: list[str]) -> None:
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    def p(txt: str) -> str:
        escaped = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        return f"<w:p><w:r><w:t>{escaped}</w:t></w:r></w:p>"

    body_xml = [p(title)] + [p(x[:250]) for x in paragraphs]
    document = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<w:document xmlns:w=\"http://schemas.openxmlformats.org/wordprocessingml/2006/main\">"
        f"<w:body>{''.join(body_xml)}<w:sectPr/></w:body></w:document>"
    )

    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)


pdf_path = sample_dir / "mock_rfp_healthcare.pdf"
create_minimal_pdf(pdf_path, text.splitlines())

docx_path = sample_dir / "mock_rfp_healthcare.docx"
create_minimal_docx(docx_path, "Mock RFP - Healthcare AI Assistant", text.split("\n\n"))

print(f"Generated: {pdf_path}")
print(f"Generated: {docx_path}")
