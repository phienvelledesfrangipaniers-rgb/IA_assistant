from __future__ import annotations

import hashlib
from typing import Iterable


def embed_text(text: str, dimension: int) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [b / 255.0 for b in digest]
    repeated = (values * ((dimension // len(values)) + 1))[:dimension]
    return repeated


def vector_literal(vector: Iterable[float]) -> str:
    return "[" + ",".join(f"{value:.6f}" for value in vector) + "]"
