from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError

from app.core.config import settings
from app.models.schemas import LLMConfig


class LLMClient:
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def complete(self, prompt: str) -> str:
        if self.config.provider == "mock":
            return f"[MOCK-{self.config.model}] {prompt[:500]}"
        if self.config.provider == "openai":
            return self._openai_complete(prompt)
        if self.config.provider == "anthropic":
            return self._anthropic_complete(prompt)
        if self.config.provider == "local":
            return self._local_complete(prompt)
        return f"[UNSUPPORTED-{self.config.provider}:{self.config.model}] {prompt[:500]}"

    def _openai_complete(self, prompt: str) -> str:
        if not settings.openai_api_key:
            return "[OPENAI] Missing COPILOT_OPENAI_API_KEY. Falling back to mock output."
        payload = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        req = request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openai_api_key}",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
        except (HTTPError, URLError, KeyError, IndexError, TimeoutError) as exc:
            return f"[OPENAI_ERROR] {exc}"

    def _anthropic_complete(self, prompt: str) -> str:
        if not settings.anthropic_api_key:
            return "[ANTHROPIC] Missing COPILOT_ANTHROPIC_API_KEY. Falling back to mock output."
        payload = {
            "model": self.config.model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        req = request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["content"][0]["text"]
        except (HTTPError, URLError, KeyError, IndexError, TimeoutError) as exc:
            return f"[ANTHROPIC_ERROR] {exc}"

    def _local_complete(self, prompt: str) -> str:
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
        }
        req = request.Request(
            f"{settings.local_llm_base_url.rstrip('/')}/api/generate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data.get("response", "")
        except (HTTPError, URLError, KeyError, TimeoutError) as exc:
            return f"[LOCAL_LLM_ERROR] {exc}"
