"""Structured logging for the bot.

Call ``setup_logging()`` once at startup (done lazily by ``get_logger``).
Output is JSON lines when ``BIZGPT_LOG_JSON=true`` (good for log
aggregators in deployment) and human-readable text otherwise. The level is
controlled by ``BIZGPT_LOG_LEVEL`` (default ``INFO``).
"""

import json
import logging
import sys
from datetime import UTC, datetime

_RESERVED = set(vars(logging.makeLogRecord({}))) | {"message", "asctime"}
_configured = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # Include any structured fields passed via `extra=`.
        payload.update({k: v for k, v in vars(record).items() if k not in _RESERVED})
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def setup_logging(level: str | None = None, json_output: bool | None = None) -> None:
    """Configure the root logger once; explicit args override settings."""
    global _configured
    if _configured and level is None and json_output is None:
        return
    from config import get_settings

    s = get_settings()
    level = (level or s.log_level).upper()
    json_output = s.log_json if json_output is None else json_output

    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(
        JsonFormatter()
        if json_output
        else logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    setup_logging()
    return logging.getLogger(name)
