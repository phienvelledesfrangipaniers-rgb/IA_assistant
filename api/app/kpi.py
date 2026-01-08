from __future__ import annotations

from datetime import date
from typing import Any

from .db import get_connection


def refresh_sales_daily(pharma_id: str) -> None:
    sql = """
    INSERT INTO mart.sales_daily (pharma_id, sales_date, gross_revenue, estimated_margin, ticket_count)
    SELECT
        %s as pharma_id,
        (payload->>'date')::date as sales_date,
        (payload->>'gross_revenue')::numeric as gross_revenue,
        (payload->>'estimated_margin')::numeric as estimated_margin,
        (payload->>'ticket_count')::int as ticket_count
    FROM staging.sales_raw
    WHERE pharma_id = %s;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pharma_id, pharma_id))


def get_sales_kpi(pharma_id: str, start: date | None, end: date | None) -> list[dict[str, Any]]:
    sql = """
    SELECT sales_date, gross_revenue, estimated_margin, ticket_count
    FROM mart.sales_daily
    WHERE pharma_id = %s
    AND (%s IS NULL OR sales_date >= %s)
    AND (%s IS NULL OR sales_date <= %s)
    ORDER BY sales_date DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pharma_id, start, start, end, end))
            rows = cur.fetchall()
    return [
        {
            "sales_date": row[0].isoformat(),
            "gross_revenue": float(row[1]) if row[1] is not None else None,
            "estimated_margin": float(row[2]) if row[2] is not None else None,
            "ticket_count": row[3],
        }
        for row in rows
    ]


def get_stock_alerts(pharma_id: str) -> list[dict[str, Any]]:
    sql = """
    SELECT product_code, product_name, stock_qty, coverage_days, status
    FROM mart.stock_status
    WHERE pharma_id = %s
    ORDER BY coverage_days DESC NULLS LAST;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pharma_id,))
            rows = cur.fetchall()
    return [
        {
            "product_code": row[0],
            "product_name": row[1],
            "stock_qty": float(row[2]) if row[2] is not None else None,
            "coverage_days": float(row[3]) if row[3] is not None else None,
            "status": row[4],
        }
        for row in rows
    ]


def get_purchase_changes(pharma_id: str) -> list[dict[str, Any]]:
    sql = """
    SELECT product_code, previous_price, latest_price, change_pct, detected_at
    FROM mart.purchase_price_changes
    WHERE pharma_id = %s
    ORDER BY detected_at DESC;
    """
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (pharma_id,))
            rows = cur.fetchall()
    return [
        {
            "product_code": row[0],
            "previous_price": float(row[1]) if row[1] is not None else None,
            "latest_price": float(row[2]) if row[2] is not None else None,
            "change_pct": float(row[3]) if row[3] is not None else None,
            "detected_at": row[4].isoformat() if row[4] else None,
        }
        for row in rows
    ]


def build_kpi_summary(pharma_id: str, start: date | None, end: date | None) -> dict[str, Any]:
    sales = get_sales_kpi(pharma_id, start, end)
    stock = get_stock_alerts(pharma_id)
    purchases = get_purchase_changes(pharma_id)
    return {
        "sales": sales[:5],
        "stock_alerts": stock[:5],
        "purchase_changes": purchases[:5],
    }
