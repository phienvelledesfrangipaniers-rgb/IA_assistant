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

app = FastAPI(title="Assistant IA Pharmacie API")

rag_settings: RagSettings = load_rag_settings()

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ExtractPayload(BaseModel):
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


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/config")
def config_page() -> FileResponse:
    return FileResponse(static_dir / "config.html")


@app.get("/sql")
def sql_page() -> FileResponse:
    return FileResponse(static_dir / "sql.html")


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "database": check_connection()}


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
        response = client.call("query_thread_data", {"query": sql_text})
    except DataSnapError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"pharma_id": payload.pharma_id, "result": response.result}


@app.post("/rag/ask")
def rag_ask(payload: RagAskPayload) -> dict[str, Any]:
    result = answer_question(payload.pharma_id, payload.question, payload.start, payload.end, rag_settings)
    return result


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
