"""
Formatters for the Logging Framework (Strategy pattern).

Your job: implement the formatting strategies.
- Each formatter turns a LogRecord into a string
- Think about: how would you add a new format without modifying existing code?
- Think about: what information is useful in different contexts?
  (development → simple, production → detailed, log aggregation → JSON)
"""

from abc import ABC, abstractmethod
from models import LogRecord


class LogFormatter(ABC):
    """Abstract formatter — defines how a LogRecord becomes a string."""

    @abstractmethod
    def format(self, record: LogRecord) -> str:
        """Format a log record into a string."""
        ...


class SimpleFormatter(LogFormatter):
    """
    Minimal format for quick development.

    Output: "[LEVEL] message"
    Example: "[INFO] Server started on port 8080"
    """

    def format(self, record: LogRecord) -> str:
        # TODO: format as "[LEVEL] message"
        pass


class DetailedFormatter(LogFormatter):
    """
    Verbose format with timestamp and logger name.

    Output: "timestamp [LEVEL] logger_name: message"
    Example: "2024-01-15 10:30:00 [WARNING] app.db: Connection pool exhausted"

    Use strftime format: "%Y-%m-%d %H:%M:%S"
    """

    def format(self, record: LogRecord) -> str:
        # TODO: format as "timestamp [LEVEL] logger_name: message"
        pass


class JsonFormatter(LogFormatter):
    """
    Structured JSON output for log aggregation systems.

    Output: JSON string with keys: timestamp, level, logger, message, extra
    Example: {"timestamp": "2024-01-15T10:30:00", "level": "ERROR", ...}

    Hint: use the `json` module.
    """

    def format(self, record: LogRecord) -> str:
        # TODO: format as a JSON string
        pass
