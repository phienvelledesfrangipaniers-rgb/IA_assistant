from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import get_pharmacy_hosts
from .datasnap import DataSnapClient, DataSnapError
from .db import check_connection
from .kpi import get_purchase_changes, get_sales_kpi, get_stock_alerts
from .rag.service import RagSettings, answer_question, index_folder, load_rag_settings
from .table_descriptions import (
    get_table_description,
    list_table_descriptions,
    save_table_description,
)
from .query_catalog import (
    catalog_entries_with_names,
    export_catalog_queries,
    import_catalog_queries,
    read_catalog_content,
    write_catalog_content,
)
from .query_store import create_query, delete_query, get_query, list_queries, update_query

app = FastAPI(title="Assistant IA Pharmacie API")

rag_settings: RagSettings = load_rag_settings()

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.on_event("startup")
def seed_catalog_queries() -> None:
    try:
        if list_queries():
            return
    except Exception:
        return
    try:
        content = read_catalog_content()
    except FileNotFoundError:
        return
    import_catalog_queries(content)


class ExtractPayload(BaseModel):
    sql: str
    params: dict | None = None


class RagIndexPayload(BaseModel):
    pharma_id: str
    path: str


class RagAskPayload(BaseModel):
    pharma_id: str
    question: str
    start: date | None = None
    end: date | None = None


class SqlQueryPayload(BaseModel):
    pharma_id: str
    sql: str


class EnvUpdatePayload(BaseModel):
    content: str


class TableInfoPayload(BaseModel):
    pharma_id: str
    table: str


class TableDescriptionPayload(BaseModel):
    table: str
    description: str


class SavedQueryPayload(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] | None = None
    sql_text: str
    source: str | None = None


class CatalogPayload(BaseModel):
    content: str


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/config")
def config_page() -> FileResponse:
    return FileResponse(static_dir / "config.html")


@app.get("/extraction")
def extraction_page() -> FileResponse:
    return FileResponse(static_dir / "extraction.html")


@app.get("/extraction/")
def extraction_page_slash() -> FileResponse:
    return FileResponse(static_dir / "extraction.html")


@app.get("/kpi")
def kpi_page() -> FileResponse:
    return FileResponse(static_dir / "kpi.html")


@app.get("/kpi/")
def kpi_page_slash() -> FileResponse:
    return FileResponse(static_dir / "kpi.html")


@app.get("/rag")
def rag_page() -> FileResponse:
    return FileResponse(static_dir / "rag.html")


@app.get("/rag/")
def rag_page_slash() -> FileResponse:
    return FileResponse(static_dir / "rag.html")


@app.get("/prompt")
def prompt_page() -> FileResponse:
    return FileResponse(static_dir / "prompt.html")


@app.get("/prompt/")
def prompt_page_slash() -> FileResponse:
    return FileResponse(static_dir / "prompt.html")


@app.get("/env")
def env_page() -> FileResponse:
    return FileResponse(static_dir / "env.html")


@app.get("/env/")
def env_page_slash() -> FileResponse:
    return FileResponse(static_dir / "env.html")


@app.get("/sql")
def sql_page() -> FileResponse:
    return FileResponse(static_dir / "sql.html")


@app.get("/sql/")
def sql_page_slash() -> FileResponse:
    return FileResponse(static_dir / "sql.html")


def _env_file_path() -> Path:
    return Path(os.environ.get("ENV_FILE", ".env"))


def _read_env_file() -> str:
    env_file = _env_file_path()
    if not env_file.exists():
        return ""
    return env_file.read_text(encoding="utf-8")


def _apply_env_content(content: str) -> None:
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ[key.strip()] = value


@app.get("/env/load")
def env_load() -> dict[str, Any]:
    env_file = _env_file_path()
    return {"path": str(env_file), "content": _read_env_file()}


@app.post("/env/save")
def env_save(payload: EnvUpdatePayload) -> dict[str, Any]:
    env_file = _env_file_path()
    env_file.write_text(payload.content, encoding="utf-8")
    _apply_env_content(payload.content)
    return {"status": "ok", "path": str(env_file)}


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "database": check_connection()}


@app.get("/pharmacies/test")
def pharmacies_test() -> dict[str, Any]:
    results = []
    for pharma_id, host in get_pharmacy_hosts().items():
        url = f"http://{host}:8001/test/"
        try:
            response = httpx.get(url, timeout=5)
            ok = response.status_code == 200
            detail = f"HTTP {response.status_code}"
        except httpx.HTTPError as exc:
            ok = False
            detail = str(exc)
        results.append({"pharma_id": pharma_id, "host": host, "ok": ok, "detail": detail})
    return {"items": results}


@app.post("/extract/{pharma_id}/{dataset}")
def trigger_extract(pharma_id: str, dataset: str, payload: ExtractPayload) -> dict[str, Any]:
    extractor_url = os.environ.get("EXTRACTOR_URL")
    if not extractor_url:
        raise HTTPException(status_code=500, detail="EXTRACTOR_URL not configured")
    url = f"{extractor_url}/extract/{pharma_id}/{dataset}"
    try:
        response = httpx.post(url, json=payload.model_dump(), timeout=30)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return response.json()


@app.get("/kpi/{pharma_id}/sales")
def sales_kpi(
    pharma_id: str,
    from_: date | None = Query(None, alias="from"),
    to: date | None = Query(None, alias="to"),
) -> dict[str, Any]:
    data = get_sales_kpi(pharma_id, from_, to)
    return {"pharma_id": pharma_id, "items": data}


@app.get("/kpi/{pharma_id}/stock_alerts")
def stock_alerts(pharma_id: str) -> dict[str, Any]:
    data = get_stock_alerts(pharma_id)
    return {"pharma_id": pharma_id, "items": data}


@app.get("/kpi/{pharma_id}/purchases")
def purchase_changes(pharma_id: str) -> dict[str, Any]:
    data = get_purchase_changes(pharma_id)
    return {"pharma_id": pharma_id, "items": data}


@app.post("/rag/index")
def rag_index(payload: RagIndexPayload) -> dict[str, Any]:
    try:
        count = index_folder(payload.pharma_id, payload.path, rag_settings)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "ok", "indexed": count}


@app.post("/rag/upload")
def rag_upload(
    pharma_id: str = Form(...),
    files: list[UploadFile] = File(...),
) -> dict[str, Any]:
    upload_dir = Path(os.environ.get("RAG_UPLOAD_DIR", "/data/uploads")) / pharma_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    for upload in files:
        target = upload_dir / upload.filename
        with target.open("wb") as buffer:
            buffer.write(upload.file.read())
    count = index_folder(pharma_id, str(upload_dir), rag_settings)
    return {"status": "ok", "indexed": count}


@app.post("/sql/query")
def sql_query(payload: SqlQueryPayload) -> dict[str, Any]:
    sql_text = payload.sql.strip()
    if not sql_text.lower().startswith("select"):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed")
    hosts = get_pharmacy_hosts()
    host = hosts.get(payload.pharma_id)
    if not host:
        raise HTTPException(status_code=404, detail="Unknown pharmacy")
    client = DataSnapClient(host)
    try:
        response = client.call("query_thread", {"sql": sql_text})
    except DataSnapError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"pharma_id": payload.pharma_id, "result": response.result}


def _select_results(result: Any) -> list[dict[str, Any]]:
    if result is None:
        return []
    if isinstance(result, list):
        return [row for row in result if isinstance(row, dict)]
    if isinstance(result, dict):
        return [result]
    return []


def _safe_identifier(value: str) -> str:
    clean = value.strip()
    if not clean.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table identifier")
    return clean


def _fetch_tables(client: DataSnapClient) -> list[str]:
    queries = [
        "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' ORDER BY table_name",
        "SELECT name FROM sysobjects WHERE xtype = 'U' ORDER BY name",
    ]
    for query in queries:
        response = client.call("query_thread", {"sql": query})
        rows = _select_results(response.result)
        if not rows:
            continue
        key = "table_name" if "table_name" in rows[0] else "name" if "name" in rows[0] else None
        if not key:
            continue
        tables = [str(row.get(key)) for row in rows if row.get(key)]
        if tables:
            return tables
    return []


def _fetch_columns(client: DataSnapClient, table: str) -> list[dict[str, str]]:
    safe_table = _safe_identifier(table)
    queries = [
        (
            "SELECT column_name, data_type FROM information_schema.columns "
            f"WHERE table_name = '{safe_table}' ORDER BY ordinal_position"
        ),
        (
            "SELECT name AS column_name, type_name AS data_type "
            "FROM syscolumns sc JOIN systypes st ON sc.xusertype = st.xusertype "
            f"JOIN sysobjects so ON sc.id = so.id WHERE so.name = '{safe_table}' "
            "ORDER BY sc.colid"
        ),
    ]
    for query in queries:
        response = client.call("query_thread", {"sql": query})
        rows = _select_results(response.result)
        if not rows:
            continue
        normalized: list[dict[str, str]] = []
        for row in rows:
            name = row.get("column_name") or row.get("name")
            data_type = row.get("data_type") or row.get("type_name") or ""
            if name:
                normalized.append({"name": str(name), "data_type": str(data_type)})
        if normalized:
            return normalized
    return []


@app.get("/sql/pharmacies")
def sql_pharmacies() -> dict[str, Any]:
    hosts = get_pharmacy_hosts()
    return {"items": sorted(hosts.keys())}


@app.get("/sql/tables")
def sql_tables(pharma_id: str = Query(...)) -> dict[str, Any]:
    hosts = get_pharmacy_hosts()
    host = hosts.get(pharma_id)
    if not host:
        raise HTTPException(status_code=404, detail="Unknown pharmacy")
    client = DataSnapClient(host)
    try:
        tables = _fetch_tables(client)
    except DataSnapError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"pharma_id": pharma_id, "tables": tables}


@app.post("/sql/table_info")
def sql_table_info(payload: TableInfoPayload) -> dict[str, Any]:
    hosts = get_pharmacy_hosts()
    host = hosts.get(payload.pharma_id)
    if not host:
        raise HTTPException(status_code=404, detail="Unknown pharmacy")
    client = DataSnapClient(host)
    try:
        columns = _fetch_columns(client, payload.table)
    except DataSnapError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"pharma_id": payload.pharma_id, "table": payload.table, "columns": columns}


@app.get("/sql/descriptions")
def sql_table_descriptions(table: str | None = None) -> dict[str, Any]:
    if table:
        description = get_table_description(table)
        return {"table": table, "description": description}
    return {"items": list_table_descriptions()}


@app.post("/sql/descriptions")
def sql_table_descriptions_save(payload: TableDescriptionPayload) -> dict[str, Any]:
    save_table_description(payload.table, payload.description)
    return {"status": "ok"}


@app.get("/queries")
def queries_list() -> dict[str, Any]:
    try:
        return {"items": list_queries()}
    except Exception:
        try:
            entries = catalog_entries_with_names(read_catalog_content())
        except FileNotFoundError:
            entries = []
        items = []
        for idx, entry in enumerate(entries, start=1):
            items.append(
                {
                    "id": idx,
                    "name": entry.get("name"),
                    "description": entry.get("description"),
                    "tags": entry.get("tags") or [],
                    "sql_text": entry.get("sql_text"),
                    "source": entry.get("source"),
                    "created_at": None,
                    "updated_at": None,
                }
            )
        return {"items": items}

@app.post("/queries")
def query_create(payload: SavedQueryPayload) -> dict[str, Any]:
    query = create_query(
        {
            "name": payload.name,
            "description": payload.description,
            "tags": payload.tags or [],
            "sql_text": payload.sql_text,
            "source": payload.source,
        }
    )
    return query


@app.put("/queries/{query_id}")
def query_update(query_id: int, payload: SavedQueryPayload) -> dict[str, Any]:
    query = update_query(
        query_id,
        {
            "name": payload.name,
            "description": payload.description,
            "tags": payload.tags or [],
            "sql_text": payload.sql_text,
            "source": payload.source,
        },
    )
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query


@app.delete("/queries/{query_id}")
def query_delete(query_id: int) -> dict[str, Any]:
    delete_query(query_id)
    return {"status": "ok"}


@app.get("/queries/catalog")
def queries_catalog_read() -> dict[str, Any]:
    return {"content": read_catalog_content()}


@app.put("/queries/catalog")
def queries_catalog_write(payload: CatalogPayload) -> dict[str, Any]:
    write_catalog_content(payload.content)
    return {"status": "ok"}


@app.post("/queries/catalog/import")
def queries_catalog_import() -> dict[str, Any]:
    content = read_catalog_content()
    entries = import_catalog_queries(content)
    return {"status": "ok", "count": len(entries)}


@app.post("/queries/catalog/export")
def queries_catalog_export() -> dict[str, Any]:
    content = export_catalog_queries()
    write_catalog_content(content)
    return {"status": "ok", "content": content}


@app.get("/queries/{query_id}")
def query_get(query_id: int) -> dict[str, Any]:
    query = get_query(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return query

@app.post("/rag/ask")
def rag_ask(payload: RagAskPayload) -> dict[str, Any]:
    result = answer_question(payload.pharma_id, payload.question, payload.start, payload.end, rag_settings)
    return result


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
