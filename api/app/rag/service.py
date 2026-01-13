from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

from docx import Document
from pypdf import PdfReader

from ..db import get_connection
from ..kpi import build_kpi_summary
from ..table_descriptions import list_table_descriptions
from .embeddings import embed_text, vector_literal
from .llm import GPT4AllProvider, LLMProvider, NoLLMProvider, OllamaProvider


@dataclass
class RagSettings:
    embedding_dim: int
    chunk_size: int
    llm_provider: LLMProvider


def load_rag_settings() -> RagSettings:
    embedding_dim = int(os.environ.get("RAG_EMBEDDING_DIM", "128"))
    chunk_size = int(os.environ.get("RAG_CHUNK_SIZE", "800"))

    gpt4all_url = os.environ.get("GPT4ALL_URL", "http://192.168.0.100:4891")
    gpt4all_model = os.environ.get("GPT4ALL_MODEL")
    if gpt4all_url and gpt4all_model:
        provider: LLMProvider = GPT4AllProvider(gpt4all_url, gpt4all_model)
    else:
        ollama_url = os.environ.get("OLLAMA_URL")
        ollama_model = os.environ.get("OLLAMA_MODEL")
        if ollama_url and ollama_model:
            provider = OllamaProvider(ollama_url, ollama_model)
        else:
            provider = NoLLMProvider()

    return RagSettings(
        embedding_dim=embedding_dim,
        chunk_size=chunk_size,
        llm_provider=provider,
    )


def _read_text(path: Path) -> str:
    if path.suffix.lower() == ".txt":
        return path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if path.suffix.lower() == ".docx":
        doc = Document(str(path))
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    return ""


def _chunk_text(text: str, chunk_size: int) -> Iterable[str]:
    buffer: list[str] = []
    current_len = 0
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if current_len + len(line) > chunk_size and buffer:
            yield " ".join(buffer)
            buffer = [line]
            current_len = len(line)
        else:
            buffer.append(line)
            current_len += len(line)
    if buffer:
        yield " ".join(buffer)


def index_folder(pharma_id: str, path: str, settings: RagSettings) -> tuple[int, list[dict[str, str]]]:
    base = Path(path)
    if not base.exists():
        raise FileNotFoundError(path)

    inserted = 0
    errors: list[dict[str, str]] = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            for file_path in base.rglob("*"):
                if file_path.suffix.lower() not in {".txt", ".pdf", ".docx"}:
                    continue
                try:
                    content = _read_text(file_path)
                except Exception as exc:
                    errors.append({"path": str(file_path), "error": str(exc)})
                    continue
                if not content:
                    continue
                for chunk in _chunk_text(content, settings.chunk_size):
                    vector = embed_text(chunk, settings.embedding_dim)
                    cur.execute(
                        """
                        INSERT INTO rag.documents (pharma_id, source_path, content, embedding, metadata)
                        VALUES (%s, %s, %s, %s::vector, %s::jsonb)
                        """,
                        (
                            pharma_id,
                            str(file_path),
                            chunk,
                            vector_literal(vector),
                            json.dumps({"filename": file_path.name}),
                        ),
                    )
                    inserted += 1
    return inserted, errors


def search_documents(pharma_id: str, question: str, settings: RagSettings) -> list[dict[str, str]]:
    vector = embed_text(question, settings.embedding_dim)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT source_path, content
                FROM rag.documents
                WHERE pharma_id = %s
                ORDER BY embedding <-> %s::vector
                LIMIT 5
                """,
                (pharma_id, vector_literal(vector)),
            )
            rows = cur.fetchall()
    return [{"source_path": row[0], "content": row[1]} for row in rows]


def answer_question(
    pharma_id: str,
    question: str,
    start: date | None,
    end: date | None,
    settings: RagSettings,
) -> dict[str, object]:
    sources = search_documents(pharma_id, question, settings)
    kpi_summary = build_kpi_summary(pharma_id, start, end)
    table_descriptions = list_table_descriptions()
    prompt = (
        f"Question: {question}\n"
        f"KPI: {kpi_summary}\n"
        f"Descriptions tables: {table_descriptions}\n"
        f"Sources: {sources}"
    )
    if isinstance(settings.llm_provider, NoLLMProvider):
        snippets = [
            source["content"][:300].replace("\n", " ").strip()
            for source in sources
            if source.get("content")
        ]
        snippet_text = "\n".join(f"- {snippet}" for snippet in snippets[:3]) or "- Aucun extrait trouvé."
        table_summary = (
            "\n".join(
                f"- {table}: {desc}"
                for table, desc in sorted(table_descriptions.items())
                if desc
            )
            or "- Aucun descriptif de table."
        )
        answer = (
            "Réponse basée sur les documents indexés et les KPI disponibles.\n"
            f"Question: {question}\n"
            f"Résumé KPI: {kpi_summary}\n"
            "Descriptions de tables:\n"
            f"{table_summary}\n"
            "Extraits principaux:\n"
            f"{snippet_text}"
        )
    else:
        answer = settings.llm_provider.generate(prompt)
    return {
        "answer": answer,
        "sources": sources,
        "kpi_summary": kpi_summary,
    }
