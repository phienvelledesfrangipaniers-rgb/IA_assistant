from __future__ import annotations

import os
from dataclasses import dataclass


def _parse_hosts(raw: str) -> dict[str, str]:
    hosts: dict[str, str] = {}
    if not raw:
        return hosts
    for item in raw.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        hosts[key.strip()] = value.strip()
    return hosts


@dataclass(frozen=True)
class Settings:
    database_url: str
    pharmacy_hosts: dict[str, str]
    datasnap_timeout: float
    datasnap_retries: int
    log_level: str



def load_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("DATABASE_URL", "postgresql://ia:ia@db:5432/ia_pharma"),
        pharmacy_hosts=_parse_hosts(os.environ.get("PHARMACY_HOSTS", "")),
        datasnap_timeout=float(os.environ.get("DATASNAP_TIMEOUT", "10")),
        datasnap_retries=int(os.environ.get("DATASNAP_RETRIES", "3")),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
