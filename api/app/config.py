from __future__ import annotations

import os


def parse_hosts(raw: str) -> dict[str, str]:
    hosts: dict[str, str] = {}
    if not raw:
        return hosts
    for item in raw.split(","):
        if "=" not in item:
            continue
        key, value = item.split("=", 1)
        hosts[key.strip()] = value.strip()
    return hosts


def get_pharmacy_hosts() -> dict[str, str]:
    return parse_hosts(os.environ.get("PHARMACY_HOSTS", ""))
