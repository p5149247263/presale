from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json

from app.models.schemas import Project


class LocalStorage:
    def __init__(self, base_path: str = "app/data/storage") -> None:
        self.base = Path(base_path)
        self.base.mkdir(parents=True, exist_ok=True)
        (self.base / "projects").mkdir(exist_ok=True)
        (self.base / "docs").mkdir(exist_ok=True)

    def save_project(self, project: Project) -> None:
        path = self.base / "projects" / f"{project.project_id}.json"
        path.write_text(project.model_dump_json(indent=2), encoding="utf-8")

    def load_project(self, project_id: str) -> Project | None:
        path = self.base / "projects" / f"{project_id}.json"
        if not path.exists():
            return None
        return Project.model_validate_json(path.read_text(encoding="utf-8"))

    def list_projects(self) -> list[Project]:
        items: list[Project] = []
        for file in sorted((self.base / "projects").glob("*.json")):
            items.append(Project.model_validate_json(file.read_text(encoding="utf-8")))
        return items

    def save_json(self, namespace: str, key: str, value: dict[str, Any]) -> None:
        ns = self.base / namespace
        ns.mkdir(parents=True, exist_ok=True)
        (ns / f"{key}.json").write_text(json.dumps(value, indent=2), encoding="utf-8")

    def load_json(self, namespace: str, key: str) -> dict[str, Any] | None:
        path = self.base / namespace / f"{key}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
