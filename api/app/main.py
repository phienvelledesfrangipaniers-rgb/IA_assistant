from __future__ import annotations

import os
from datetime import date
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

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


@app.get("/")
def home() -> FileResponse:
    return FileResponse(static_dir / "index.html")


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


@app.post("/rag/ask")
def rag_ask(payload: RagAskPayload) -> dict[str, Any]:
    result = answer_question(payload.pharma_id, payload.question, payload.start, payload.end, rag_settings)
    return result


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
