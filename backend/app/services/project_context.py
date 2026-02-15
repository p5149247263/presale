from __future__ import annotations

from dataclasses import dataclass, field

from app.models.schemas import DocumentChunk
from app.services.vector_store import LocalVectorStore


@dataclass
class ProjectContext:
    vector_store: LocalVectorStore = field(default_factory=LocalVectorStore)
    chunks: list[DocumentChunk] = field(default_factory=list)


class ContextRegistry:
    def __init__(self) -> None:
        self._projects: dict[str, ProjectContext] = {}

    def get(self, project_id: str) -> ProjectContext:
        if project_id not in self._projects:
            self._projects[project_id] = ProjectContext()
        return self._projects[project_id]


registry = ContextRegistry()
