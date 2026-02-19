import json
import logging

from src.shared.logger import JsonFormatter, resolve_log_level


def test_json_formatter_includes_standard_and_extra_fields() -> None:
    logger = logging.getLogger("test-json-logger")
    record = logger.makeRecord(
        name=logger.name,
        level=logging.INFO,
        fn=__file__,
        lno=10,
        msg="hello",
        args=(),
        exc_info=None,
        extra={"event": "unit_test", "request_id": "req-1", "status_code": 200},
    )

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test-json-logger"
    assert payload["service"] == "test-json-logger"
    assert payload["message"] == "hello"
    assert payload["event"] == "unit_test"
    assert payload["request_id"] == "req-1"
    assert payload["status_code"] == 200
    assert "timestamp" in payload


def test_resolve_log_level_handles_valid_and_invalid_values() -> None:
    assert resolve_log_level("debug") == logging.DEBUG
    assert resolve_log_level("INFO") == logging.INFO
    assert resolve_log_level("invalid", default=logging.WARNING) == logging.WARNING
