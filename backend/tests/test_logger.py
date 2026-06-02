import json
import logging
from backend.utils.logger import JSONFormatter

def test_logger_initialization() -> None:
    # Importing inside function ensures it picks up the conftest environment
    from backend.utils.logger import logger
    assert logger.name == "nse_platform"
    assert len(logger.handlers) >= 1
    assert isinstance(logger.handlers[0].formatter, JSONFormatter)
    assert logger.level == logging.DEBUG # Default from conftest

def test_json_formatting() -> None:
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    # Simulate adding a correlation_id which our logger supports
    record.correlation_id = "req-123"
    
    formatted = formatter.format(record)
    data = json.loads(formatted)
    
    assert data["message"] == "Test message"
    assert data["level"] == "INFO"
    assert data["service"] == "nse-intelligence-platform"
    assert data["correlation_id"] == "req-123"
    assert "timestamp" in data
