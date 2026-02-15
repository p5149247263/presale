from __future__ import annotations

from pathlib import Path

from app.models.schemas import Citation, DocumentChunk
from app.services.parser import chunk_text
from app.services.vector_store import LocalVectorStore


class KnowledgeBaseService:
    def __init__(self, base_path: str = "app/data/sample_kb") -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.vector = LocalVectorStore()
        self._loaded = False

    def _load_existing(self) -> None:
        if self._loaded:
            return
        chunks: list[DocumentChunk] = []
        for file in sorted(self.base_path.glob("*")):
            if file.suffix.lower() not in {".txt", ".md", ".csv"}:
                continue
            doc_id = f"kb-{file.stem}"
            text = file.read_text(encoding="utf-8", errors="ignore")
            chunks.extend(chunk_text(doc_id, text, page=1))
        if chunks:
            self.vector.upsert(chunks)
        self._loaded = True

    def add_document(self, file_name: str, text: str) -> str:
        self._load_existing()
        safe_name = Path(file_name).name
        path = self.base_path / safe_name
        path.write_text(text, encoding="utf-8")
        doc_id = f"kb-{path.stem}"
        chunks = chunk_text(doc_id, text, page=1)
        self.vector.upsert(chunks)
        return doc_id

    def search(self, query: str, k: int = 5) -> list[dict]:
        self._load_existing()
        results = self.vector.query(query, k=k)
        citations = self.vector.citations_from_results(results)
        return [
            {
                "text": res.chunk.text,
                "score": res.score,
                "citation": Citation(
                    doc_id=res.chunk.doc_id,
                    page=res.chunk.page,
                    section=res.chunk.section,
                    snippet_hash=res.chunk.snippet_hash,
                ).model_dump(mode="json"),
            }
            for res in results
        ]
