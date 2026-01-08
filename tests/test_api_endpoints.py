from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import main


client = TestClient(main.app)


def test_health_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(main, "check_connection", lambda: True)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_sales_kpi_endpoint(monkeypatch) -> None:
    monkeypatch.setattr(main, "get_sales_kpi", lambda *_: [{"sales_date": "2024-01-01"}])
    response = client.get("/kpi/frang/sales")
    assert response.status_code == 200
    assert response.json()["items"][0]["sales_date"] == "2024-01-01"
