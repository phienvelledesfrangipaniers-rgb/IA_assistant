from __future__ import annotations

from typing import Any

from .config import Settings
from .datasnap import DataSnapClient
from .db import insert_payload
from .logger import get_logger


class ExtractionError(RuntimeError):
    pass


def extract_dataset(
    settings: Settings,
    pharma_id: str,
    dataset: str,
    sql: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not sql:
        raise ExtractionError("SQL query is required")
    host = settings.pharmacy_hosts.get(pharma_id)
    if not host:
        raise ExtractionError(f"Unknown pharmacy '{pharma_id}'")

    client = DataSnapClient(host, timeout=settings.datasnap_timeout, retries=settings.datasnap_retries)
    payload: dict[str, Any] = {"sql": sql}
    if params:
        payload["params"] = params

    logger = get_logger("extractor", pharma_id=pharma_id, dataset=dataset)
    response = client.call("query_thread", payload)
    logger.info("datasnap_response")

    return {"dataset": dataset, "result": response.result}


def persist_result(
    settings: Settings,
    pharma_id: str,
    dataset: str,
    result: dict[str, Any],
) -> None:
    table = f"{dataset}_raw"
    from .db import get_connection

    logger = get_logger("extractor", pharma_id=pharma_id, dataset=dataset)
    with get_connection(settings.database_url) as conn:
        insert_payload(conn, table, pharma_id, result)
    logger.info("staging_inserted", extra={"table": table})
