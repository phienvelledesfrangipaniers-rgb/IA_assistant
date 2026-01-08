from __future__ import annotations

import os

import psycopg


def get_connection() -> psycopg.Connection:
    database_url = os.environ.get("DATABASE_URL", "postgresql://ia:ia@db:5432/ia_pharma")
    return psycopg.connect(database_url, autocommit=True)


def check_connection() -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return True
    except psycopg.Error:
        return False
