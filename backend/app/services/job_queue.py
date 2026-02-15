from __future__ import annotations

import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable
from uuid import uuid4

from app.models.schemas import Job, JobStatus


class JobQueue:
    def __init__(self, workers: int = 4) -> None:
        self._executor = ThreadPoolExecutor(max_workers=workers)
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def submit(self, project_id: str, task: str, fn: Callable[[Callable[[int, str], None]], dict]) -> Job:
        job_id = str(uuid4())
        job = Job(job_id=job_id, project_id=project_id, task=task, status=JobStatus.QUEUED, progress=0)
        with self._lock:
            self._jobs[job_id] = job

        def progress(p: int, message: str) -> None:
            with self._lock:
                existing = self._jobs[job_id]
                self._jobs[job_id] = existing.model_copy(update={"progress": p, "message": message, "status": JobStatus.RUNNING})

        def run() -> None:
            try:
                progress(10, "Started")
                result = fn(progress)
                with self._lock:
                    existing = self._jobs[job_id]
                    self._jobs[job_id] = existing.model_copy(
                        update={
                            "status": JobStatus.COMPLETED,
                            "progress": 100,
                            "message": "Completed",
                            "result": result,
                        }
                    )
            except Exception as exc:
                with self._lock:
                    existing = self._jobs[job_id]
                    self._jobs[job_id] = existing.model_copy(
                        update={
                            "status": JobStatus.FAILED,
                            "message": f"{exc}\n{traceback.format_exc()[:1200]}",
                        }
                    )

        self._executor.submit(run)
        return job

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)
