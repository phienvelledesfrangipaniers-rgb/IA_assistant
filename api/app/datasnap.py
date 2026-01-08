from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass
class DataSnapResponse:
    raw: dict[str, Any]
    result: Any


class DataSnapError(RuntimeError):
    pass


class DataSnapClient:
    def __init__(self, host: str, timeout: float = 10.0, retries: int = 3) -> None:
        self.base_url = f"http://{host}:8001"
        self.timeout = timeout
        self.retries = retries

    def _endpoint(self, method_name: str) -> str:
        return f"{self.base_url}/datasnap/rest/TServerMethods1/%22{method_name}%22/"

    def call(self, method_name: str, payload: dict[str, Any]) -> DataSnapResponse:
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        self._endpoint(method_name),
                        json=payload,
                        headers={"Accept": "application/json", "Content-Type": "application/json"},
                    )
                response.raise_for_status()
                data = response.json()
                if "result" not in data:
                    raise DataSnapError("Missing 'result' field in response")
                result = data["result"][0] if isinstance(data["result"], list) else data["result"]
                return DataSnapResponse(raw=data, result=result)
            except (httpx.HTTPError, ValueError, DataSnapError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 10))
                    continue
                break
        raise DataSnapError(f"DataSnap call failed after {self.retries} attempts: {last_error}")
