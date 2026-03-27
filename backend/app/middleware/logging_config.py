"""
Structured Logging Configuration

JSON-formatted logs for production, human-readable for development.
Integrates with ELK Stack / Loki for centralized log aggregation.

Log format (production):
    {"timestamp": "2026-03-26T12:00:00", "level": "INFO", "trace_id": "abc123",
     "service": "api", "message": "GET /api/v1/markets - 200 (45ms)"}
"""

import logging
import sys
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production / log aggregation systems."""

    def __init__(self, service_name: str = "api"):
        super().__init__()
        self.service_name = service_name

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "service": self.service_name,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add trace_id if available
        if hasattr(record, "trace_id"):
            log_data["trace_id"] = record.trace_id

        # Add extra fields
        for key in ("status_code", "duration_ms", "method", "path", "error"):
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        # Add exception info
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(service_name: str = "api", level: str = "INFO", json_format: bool = True):
    """
    Configure application logging.

    Args:
        service_name: Name of this microservice (for log identification)
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_format: Use JSON format (production) or human-readable (development)
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)

    if json_format:
        handler.setFormatter(JSONFormatter(service_name=service_name))
    else:
        handler.setFormatter(
            logging.Formatter(
                f"%(asctime)s [{service_name}] %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )

    root_logger.addHandler(handler)

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
