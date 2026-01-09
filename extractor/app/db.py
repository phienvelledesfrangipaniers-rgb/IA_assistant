from __future__ import annotations

import json
from typing import Any

import psycopg


def get_connection(database_url: str) -> psycopg.Connection:
    return psycopg.connect(database_url, autocommit=True)


def insert_payload(
    conn: psycopg.Connection,
    table: str,
    pharma_id: str,
    payload: Any,
) -> None:
    with conn.cursor() as cur:
        cur.execute(
            f"INSERT INTO staging.{table} (pharma_id, payload) VALUES (%s, %s)",
            (pharma_id, json.dumps(payload)),
        )
