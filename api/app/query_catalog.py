from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

from .query_store import list_queries, replace_queries

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "queries_catalog.json"
CATALOG_PATH = Path(os.environ.get("QUERIES_CATALOG_PATH", str(DEFAULT_CATALOG_PATH)))


def read_catalog_content() -> str:
    try:
        return CATALOG_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        content = render_catalog([])
        CATALOG_PATH.write_text(content, encoding="utf-8")
        return content


def write_catalog_content(content: str) -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CATALOG_PATH.write_text(content, encoding="utf-8")


def _extract_description_tags(description_line: str) -> tuple[str, list[str]]:
    tags = re.findall(r"#([A-Za-z0-9_]+)", description_line)
    description = re.sub(r"\s+#\S+", "", description_line).strip()
    return description, tags


def _normalize_entry(entry: dict[str, Any]) -> dict[str, Any]:
    raw_description = entry.get("descriptif") or entry.get("description") or ""
    sql_text = entry.get("requete") or entry.get("sql_text") or ""
    source = entry.get("fichier") or entry.get("source") or ""
    tags = entry.get("tags")
    if not isinstance(tags, list):
        tags = None
    description, extracted_tags = _extract_description_tags(raw_description)
    if tags is None:
        tags = extracted_tags
    return {
        "description": description,
        "tags": tags,
        "sql_text": sql_text,
        "source": source,
    }


def parse_catalog(content: str) -> list[dict[str, Any]]:
    try:
        payload = json.loads(content) if content.strip() else []
    except json.JSONDecodeError:
        return []
    if not isinstance(payload, list):
        return []
    entries = [_normalize_entry(item) for item in payload if isinstance(item, dict)]
    return [entry for entry in entries if entry.get("sql_text")]


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "query"


def catalog_entries_with_names(content: str) -> list[dict[str, Any]]:
    entries = parse_catalog(content)
    counts: dict[str, int] = {}
    for entry in entries:
        base = f"{_slugify(entry.get('source') or 'source')}_{_slugify(entry.get('description') or '')}"
        counts.setdefault(base, 0)
        counts[base] += 1
        suffix = f"_{counts[base]}" if counts[base] > 1 else ""
        entry["name"] = f"{base}{suffix}"
    return entries


def import_catalog_queries(content: str) -> list[dict[str, Any]]:
    entries = catalog_entries_with_names(content)
    replace_queries(entries)
    return entries


def render_catalog(queries: list[dict[str, Any]]) -> str:
    payload: list[dict[str, Any]] = []
    for query in queries:
        description = query.get("description") or "Requête"
        tags = query.get("tags") or []
        tag_suffix = " ".join(f"#{tag}" for tag in tags)
        descriptif = f"{description} {tag_suffix}".strip()
        payload.append(
            {
                "descriptif": descriptif,
                "requete": (query.get("sql_text") or "").strip(),
                "fichier": query.get("source") or "source",
            }
        )
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def export_catalog_queries() -> str:
    queries = list_queries()
    return render_catalog(queries)
