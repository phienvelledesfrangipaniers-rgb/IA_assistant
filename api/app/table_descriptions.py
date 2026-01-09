from __future__ import annotations

import json
import os
from pathlib import Path


def _descriptions_path() -> Path:
    return Path(os.environ.get("TABLE_DESCRIPTIONS_FILE", "/data/uploads/table_descriptions.json"))


def _load() -> dict[str, str]:
    path = _descriptions_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save(data: dict[str, str]) -> None:
    path = _descriptions_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def list_table_descriptions() -> dict[str, str]:
    return _load()


def get_table_description(table: str) -> str:
    data = _load()
    return data.get(table, "")


def save_table_description(table: str, description: str) -> None:
    data = _load()
    data[table] = description.strip()
    _save(data)
