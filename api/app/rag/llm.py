from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx


class LLMProvider(Protocol):
    def generate(self, prompt: str) -> str:
        ...


@dataclass
class NoLLMProvider:
    def generate(self, prompt: str) -> str:
        return "LLM non configuré. Voici les extraits pertinents."


@dataclass
class OllamaProvider:
    base_url: str
    model: str

    def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        response = httpx.post(f"{self.base_url}/api/generate", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")


@dataclass
class GPT4AllProvider:
    base_url: str
    model: str
    last_request: dict[str, object] | None = None
    last_response: dict[str, object] | None = None

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        self.last_request = payload
        response = httpx.post(f"{self.base_url}/v1/chat/completions", json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        self.last_response = data
        choices = data.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return message.get("content", "")
