from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from .query_store import list_queries, replace_queries

CATALOG_PATH = Path(__file__).resolve().parents[2] / "docs" / "queries_catalog.md"


def read_catalog_content() -> str:
    return CATALOG_PATH.read_text(encoding="utf-8")


def write_catalog_content(content: str) -> None:
    CATALOG_PATH.write_text(content, encoding="utf-8")


def parse_catalog(content: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    lines = content.splitlines()
    current_source = ""
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        if line.startswith("## `") and line.endswith("`"):
            current_source = line[4:-1]
            idx += 1
            continue
        if line.startswith("- "):
            description_line = line[2:].strip()
            tags = re.findall(r"#([A-Za-z0-9_]+)", description_line)
            description = re.sub(r"\s+#\S+", "", description_line).strip()
            sql_text = ""
            j = idx + 1
            while j < len(lines) and "```sql" not in lines[j]:
                j += 1
            if j < len(lines) and "```sql" in lines[j]:
                j += 1
                sql_lines: list[str] = []
                while j < len(lines) and "```" not in lines[j]:
                    sql_lines.append(lines[j])
                    j += 1
                sql_text = "\n".join(sql_lines).strip()
                idx = j
            entries.append(
                {
                    "description": description,
                    "tags": tags,
                    "sql_text": sql_text,
                    "source": current_source,
                }
            )
        idx += 1
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
    lines = [
        "# Requêtes SQL passées à `requete()`",
        "",
        "Ce fichier liste toutes les requêtes SQL passées à la fonction `requete` (ou `$win->requete()` / "
        "`$this->requete()`), avec une courte description et des hashtags contenant les noms de tables utilisées.",
        "",
    ]
    sources: dict[str, list[dict[str, Any]]] = {}
    for query in queries:
        sources.setdefault(query.get("source") or "source", []).append(query)
    for source in sorted(sources):
        lines.append(f"## `{source}`")
        for query in sources[source]:
            description = query.get("description") or "Requête"
            tags = " ".join(f"#{tag}" for tag in (query.get("tags") or []))
            tag_suffix = f" {tags}" if tags else ""
            lines.append(f"- {description}{tag_suffix}")
            lines.append("  ```sql")
            sql_text = (query.get("sql_text") or "").strip()
            for sql_line in sql_text.splitlines():
                lines.append(f"  {sql_line}")
            lines.append("  ```")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def export_catalog_queries() -> str:
    queries = list_queries()
    return render_catalog(queries)
