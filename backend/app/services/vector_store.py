from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from app.models.schemas import Citation, DocumentChunk

try:
    import faiss  # type: ignore
except Exception:
    faiss = None


@dataclass
class SearchResult:
    chunk: DocumentChunk
    score: float


class LocalVectorStore:
    def __init__(self) -> None:
        self._chunks: list[DocumentChunk] = []
        self._vectors: np.ndarray | None = None
        self._index = None

    @staticmethod
    def _embed(text: str, dim: int = 128) -> np.ndarray:
        # Deterministic lightweight embedding for local mock mode.
        vec = np.zeros(dim, dtype=np.float32)
        for token in text.lower().split():
            vec[hash(token) % dim] += 1.0
        norm = np.linalg.norm(vec)
        return vec if norm == 0 else vec / norm

    def upsert(self, chunks: list[DocumentChunk]) -> None:
        self._chunks.extend(chunks)
        embeds = np.vstack([self._embed(c.text) for c in self._chunks]).astype(np.float32)
        self._vectors = embeds
        if faiss is not None:
            index = faiss.IndexFlatIP(embeds.shape[1])
            index.add(embeds)
            self._index = index

    def all_chunks(self) -> list[DocumentChunk]:
        return list(self._chunks)

    def query(self, query: str, k: int = 5) -> list[SearchResult]:
        if not self._chunks:
            return []
        q = self._embed(query).reshape(1, -1).astype(np.float32)

        if self._index is not None:
            scores, idxs = self._index.search(q, min(k, len(self._chunks)))
            return [
                SearchResult(chunk=self._chunks[int(i)], score=float(s))
                for s, i in zip(scores[0], idxs[0])
                if int(i) >= 0
            ]

        assert self._vectors is not None
        sims = np.dot(self._vectors, q.T).reshape(-1)
        top_k = np.argsort(-sims)[:k]
        return [SearchResult(chunk=self._chunks[int(i)], score=float(sims[int(i)])) for i in top_k]

    @staticmethod
    def citations_from_results(results: list[SearchResult]) -> list[Citation]:
        citations: list[Citation] = []
        seen = set()
        for res in results:
            key = (res.chunk.doc_id, res.chunk.page, res.chunk.section, res.chunk.snippet_hash)
            if key in seen:
                continue
            seen.add(key)
            citations.append(
                Citation(
                    doc_id=res.chunk.doc_id,
                    page=res.chunk.page,
                    section=res.chunk.section,
                    snippet_hash=res.chunk.snippet_hash,
                )
            )
        return citations
