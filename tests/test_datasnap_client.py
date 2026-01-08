from __future__ import annotations

import json

import httpx
import pytest

from extractor.app.datasnap import DataSnapClient


class MockTransport(httpx.BaseTransport):
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        payload = {"result": [{"status": "ok"}]}
        return httpx.Response(200, content=json.dumps(payload).encode())


def test_datasnap_client_success(monkeypatch: pytest.MonkeyPatch) -> None:
    transport = MockTransport()

    class MockClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            super().__init__(transport=transport, *args, **kwargs)

    monkeypatch.setattr(httpx, "Client", MockClient)

    client = DataSnapClient("127.0.0.1", timeout=1, retries=1)
    response = client.call("SALES_QUERY", {"query": "SALES_QUERY"})

    assert response.result == {"status": "ok"}
