from __future__ import annotations

import threading

from app.core.config import settings
from app.models.schemas import LLMConfig


_lock = threading.Lock()
_runtime_config = LLMConfig(provider=settings.llm_provider, model=settings.llm_model)


def get_llm_config() -> LLMConfig:
    with _lock:
        return _runtime_config.model_copy(deep=True)


def set_llm_config(config: LLMConfig) -> LLMConfig:
    global _runtime_config
    with _lock:
        _runtime_config = config
        return _runtime_config.model_copy(deep=True)
