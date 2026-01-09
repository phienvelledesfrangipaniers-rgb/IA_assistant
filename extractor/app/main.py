from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .config import load_settings
from .extractor import ExtractionError, extract_dataset, persist_result
from .logger import setup_logging

settings = load_settings()
setup_logging(settings.log_level)

app = FastAPI(title="Winpharma Extractor")


class ExtractRequest(BaseModel):
    params: dict | None = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/extract/{pharma_id}/{dataset}")
def extract(pharma_id: str, dataset: str, payload: ExtractRequest) -> dict:
    try:
        result = extract_dataset(settings, pharma_id, dataset, payload.params)
        persist_result(settings, pharma_id, dataset, result)
        return {"status": "ok", "dataset": dataset}
    except ExtractionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run()
