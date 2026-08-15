"""
Centralized Logging Configuration for Digital Castle S.P.C
---
Structured JSON logging with rotation, filtering, and security.
"""

import logging
import logging.handlers
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs structured JSON logs.
    Hides sensitive information (API keys, passwords, etc.).
    """

    SENSITIVE_KEYS = {
        "api_key",
        "token",
        "password",
        "secret",
        "auth",
        "credential",
        "key",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "__dict__"):
            extra_fields = {
                k: v
                for k, v in record.__dict__.items()
                if k
                not in {
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "message",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                }
            }
            # Sanitize sensitive fields
            extra_fields = self._sanitize(extra_fields)
            log_data.update(extra_fields)

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        return json.dumps(log_data, default=str)

    @classmethod
    def _sanitize(cls, data: dict) -> dict:
        """Remove sensitive information from log data."""
        if not isinstance(data, dict):
            return data

        sanitized = {}
        for key, value in data.items():
            # Check if key name suggests sensitive data
            if any(
                sensitive in key.lower() for sensitive in cls.SENSITIVE_KEYS
            ):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = cls._sanitize(value)
            elif isinstance(value, (list, tuple)):
                sanitized[key] = [
                    cls._sanitize(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                sanitized[key] = value

        return sanitized


class SensitiveDataFilter(logging.Filter):
    """
    Filter that removes sensitive data from log records.
    """

    SENSITIVE_PATTERNS = [
        "ANTHROPIC_API_KEY",
        "DEEPSEEK_API_KEY",
        "TOGETHER_API_KEY",
        "GITHUB_TOKEN",
        "TELEGRAM_BOT_TOKEN",
        "DATABASE_URL",
        "SECRET_KEY",
        "password",
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter out sensitive data."""
        # Check message
        for pattern in self.SENSITIVE_PATTERNS:
            if pattern in record.getMessage():
                # Replace actual values with placeholders
                record.msg = self._redact_message(record.msg)
                if record.args:
                    record.args = tuple(
                        self._redact_value(arg) for arg in record.args
                    )

        return True

    @staticmethod
    def _redact_message(message: str) -> str:
        """Redact sensitive patterns from message."""
        import re

        # Pattern: API_KEY=value
        message = re.sub(
            r"(API_KEY|TOKEN|PASSWORD|SECRET)=\S+",
            r"\1=***REDACTED***",
            message,
            flags=re.IGNORECASE,
        )

        # Pattern: Bearer token
        message = re.sub(
            r"Bearer\s+\S+",
            "Bearer ***REDACTED***",
            message,
            flags=re.IGNORECASE,
        )

        return message

    @staticmethod
    def _redact_value(value) -> str:
        """Redact sensitive values."""
        if not isinstance(value, str):
            return value
        if len(value) > 32 and value.isalnum():
            return f"{value[:8]}***REDACTED***{value[-8:]}"
        return value


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 30,  # 30 days
) -> None:
    """
    Configure logging for the entire application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        max_bytes: Max size per log file
        backup_count: Number of backup files to keep
    """
    # Create log directory
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True, parents=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatters
    json_formatter = JSONFormatter()
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Add sensitive data filter to all handlers
    sensitive_filter = SensitiveDataFilter()

    # 1. Console Handler (INFO+ level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    console_handler.addFilter(sensitive_filter)
    root_logger.addHandler(console_handler)

    # 2. Main Log File (all levels, rotated daily)
    main_log_file = log_path / "digital-castle.log"
    main_handler = logging.handlers.RotatingFileHandler(
        filename=main_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    main_handler.setLevel(log_level)
    main_handler.setFormatter(json_formatter)
    main_handler.addFilter(sensitive_filter)
    root_logger.addHandler(main_handler)

    # 3. Error Log File (ERROR+ level)
    error_log_file = log_path / "errors.log"
    error_handler = logging.handlers.RotatingFileHandler(
        filename=error_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(json_formatter)
    error_handler.addFilter(sensitive_filter)
    root_logger.addHandler(error_handler)

    # 4. Agent Log File (for agent-specific logging)
    agent_log_file = log_path / "agents.log"
    agent_handler = logging.handlers.RotatingFileHandler(
        filename=agent_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    agent_handler.setLevel(logging.DEBUG)
    agent_handler.setFormatter(json_formatter)
    agent_handler.addFilter(sensitive_filter)
    agent_logger = logging.getLogger("agents")
    agent_logger.addHandler(agent_handler)

    # 5. Performance Log File (for timing and metrics)
    perf_log_file = log_path / "performance.log"
    perf_handler = logging.handlers.RotatingFileHandler(
        filename=perf_log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    perf_handler.setLevel(logging.INFO)
    perf_handler.setFormatter(json_formatter)
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)

    logging.info("Logging configured successfully")
    logging.info(f"Log directory: {log_path.absolute()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


def log_performance(
    logger: logging.Logger,
    operation: str,
    duration_ms: float,
    status: str = "success",
    **kwargs,
) -> None:
    """
    Log performance metrics for an operation.

    Args:
        logger: Logger instance
        operation: Operation name
        duration_ms: Duration in milliseconds
        status: Status (success, error, timeout)
        **kwargs: Additional context
    """
    logger.info(
        f"{operation} completed",
        extra={
            "operation": operation,
            "duration_ms": duration_ms,
            "status": status,
            **kwargs,
        },
    )


# Initialize logging on module import
if os.getenv("APP_ENV") == "production":
    setup_logging(
        log_level="WARNING",
        log_dir=os.getenv("LOG_DIR", "/var/log/digital-castle"),
    )
else:
    setup_logging(
        log_level="DEBUG",
        log_dir=os.getenv("LOG_DIR", "logs"),
    )
