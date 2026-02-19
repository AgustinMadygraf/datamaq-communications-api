from datetime import datetime, timezone
import json
import logging
from typing import Any


_RESERVED_LOG_RECORD_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "level": record.levelname,
            "logger": record.name,
            "service": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key in _RESERVED_LOG_RECORD_ATTRS or key.startswith("_"):
                continue
            payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def resolve_log_level(level_name: str | int | None, default: int = logging.INFO) -> int:
    if isinstance(level_name, int):
        return level_name

    if isinstance(level_name, str):
        clean = level_name.strip().upper()
        if clean:
            resolved = getattr(logging, "_nameToLevel", {}).get(clean)
            if isinstance(resolved, int):
                return resolved

    return default


def configure_logging(level: int | str = logging.INFO) -> None:
    root_logger = logging.getLogger()
    resolved_level = resolve_log_level(level)
    root_logger.setLevel(resolved_level)

    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        root_logger.addHandler(handler)
        return

    for handler in root_logger.handlers:
        handler.setLevel(resolved_level)
        handler.setFormatter(JsonFormatter())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
