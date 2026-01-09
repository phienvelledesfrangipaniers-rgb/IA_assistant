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
