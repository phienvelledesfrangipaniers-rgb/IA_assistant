from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=level.upper(),
        stream=sys.stdout,
        format="%(message)s",
    )


class JsonLoggerAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": logging.getLevelName(self.logger.level),
            "message": msg,
        }
        if self.extra:
            payload.update(self.extra)
        return json.dumps(payload, ensure_ascii=False), kwargs


def get_logger(name: str, **extra) -> JsonLoggerAdapter:
    logger = logging.getLogger(name)
    return JsonLoggerAdapter(logger, extra)
