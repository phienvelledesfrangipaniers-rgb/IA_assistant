from __future__ import annotations

from typing import Any

from .db import get_connection


def list_queries() -> list[dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, tags, sql_text, source, created_at, updated_at
                FROM catalog.saved_queries
                ORDER BY name
                """
            )
            rows = cur.fetchall()
    return [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "tags": row[3] or [],
            "sql_text": row[4],
            "source": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None,
        }
        for row in rows
    ]


def get_query(query_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, tags, sql_text, source, created_at, updated_at
                FROM catalog.saved_queries
                WHERE id = %s
                """,
                (query_id,),
            )
            row = cur.fetchone()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "description": row[2],
        "tags": row[3] or [],
        "sql_text": row[4],
        "source": row[5],
        "created_at": row[6].isoformat() if row[6] else None,
        "updated_at": row[7].isoformat() if row[7] else None,
    }


def create_query(data: dict[str, Any]) -> dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO catalog.saved_queries (name, description, tags, sql_text, source)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    data.get("name"),
                    data.get("description"),
                    data.get("tags"),
                    data.get("sql_text"),
                    data.get("source"),
                ),
            )
            query_id = cur.fetchone()[0]
    return get_query(query_id) or {}


def update_query(query_id: int, data: dict[str, Any]) -> dict[str, Any] | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE catalog.saved_queries
                SET name = %s,
                    description = %s,
                    tags = %s,
                    sql_text = %s,
                    source = %s,
                    updated_at = NOW()
                WHERE id = %s
                """,
                (
                    data.get("name"),
                    data.get("description"),
                    data.get("tags"),
                    data.get("sql_text"),
                    data.get("source"),
                    query_id,
                ),
            )
    return get_query(query_id)


def delete_query(query_id: int) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM catalog.saved_queries WHERE id = %s", (query_id,))


def replace_queries(queries: list[dict[str, Any]]) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM catalog.saved_queries")
            if queries:
                cur.executemany(
                    """
                    INSERT INTO catalog.saved_queries (name, description, tags, sql_text, source)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    [
                        (
                            query.get("name"),
                            query.get("description"),
                            query.get("tags"),
                            query.get("sql_text"),
                            query.get("source"),
                        )
                        for query in queries
                    ],
                )
