"""
SOLUTION — Logger / Logging Framework

Don't peek until you've given it a solid attempt!

This is one valid solution. Yours may differ in structure and still be
perfectly correct — there's no single "right" LLD answer. Compare your
design choices against this one and think about trade-offs.

Patterns used:
- Singleton — LogManager ensures one registry of loggers
- Chain of Responsibility — level checks at logger → handler
- Observer — handlers are observers attached to loggers
- Strategy — formatters are interchangeable strategies
"""

from abc import ABC, abstractmethod
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
import json


# ===================================================================
# Models
# ===================================================================

class LogLevel(IntEnum):
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


@dataclass
class LogRecord:
    level: LogLevel
    message: str
    logger_name: str
    timestamp: datetime = field(default_factory=datetime.now)
    extra: dict[str, Any] = field(default_factory=dict)


# ===================================================================
# Formatters (Strategy pattern)
# ===================================================================

class LogFormatter(ABC):
    @abstractmethod
    def format(self, record: LogRecord) -> str:
        ...


class SimpleFormatter(LogFormatter):
    """Output: [LEVEL] message"""

    def format(self, record: LogRecord) -> str:
        return f"[{record.level.name}] {record.message}"


class DetailedFormatter(LogFormatter):
    """Output: timestamp [LEVEL] logger_name: message"""

    def format(self, record: LogRecord) -> str:
        ts = record.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"{ts} [{record.level.name}] {record.logger_name}: {record.message}"


class JsonFormatter(LogFormatter):
    """Output: JSON string with timestamp, level, logger, message, extra."""

    def format(self, record: LogRecord) -> str:
        data = {
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "logger": record.logger_name,
            "message": record.message,
        }
        if record.extra:
            data["extra"] = record.extra
        return json.dumps(data)


# ===================================================================
# Handlers (Observer pattern)
# ===================================================================

class LogHandler(ABC):
    """
    Key design decisions:

    1. Each handler has its own level — this lets you route DEBUG+ to
       console but only ERROR+ to file.

    2. handle() checks the level before calling emit(). This means
       subclasses only need to implement the output logic.

    3. Default formatter is SimpleFormatter so handlers work out of
       the box without explicit configuration.
    """

    def __init__(self):
        self._level: LogLevel = LogLevel.DEBUG
        self._formatter: LogFormatter = SimpleFormatter()

    def set_level(self, level: LogLevel) -> None:
        self._level = level

    def set_formatter(self, formatter: LogFormatter) -> None:
        self._formatter = formatter

    @property
    def level(self) -> LogLevel:
        return self._level

    @property
    def formatter(self) -> LogFormatter:
        return self._formatter

    def handle(self, record: LogRecord) -> None:
        if record.level >= self._level:
            formatted = self._formatter.format(record)
            self.emit(formatted)

    @abstractmethod
    def emit(self, formatted: str) -> None:
        ...


class ConsoleHandler(LogHandler):
    def emit(self, formatted: str) -> None:
        print(formatted)


class FileHandler(LogHandler):
    def __init__(self, file_path: str):
        super().__init__()
        self._file_path = file_path

    @property
    def file_path(self) -> str:
        return self._file_path

    def emit(self, formatted: str) -> None:
        with open(self._file_path, "a") as f:
            f.write(formatted + "\n")


class MemoryHandler(LogHandler):
    """
    Stores formatted records in a list — ideal for testing.
    You can inspect .records to verify exactly what was logged.
    """

    def __init__(self):
        super().__init__()
        self._records: list[str] = []

    def emit(self, formatted: str) -> None:
        self._records.append(formatted)

    @property
    def records(self) -> list[str]:
        return list(self._records)

    def clear(self) -> None:
        self._records.clear()


# ===================================================================
# Logger (Chain of Responsibility)
# ===================================================================

class Logger:
    """
    Key design decisions:

    1. log() checks the logger's level first. If the record doesn't
       meet the threshold, it's discarded entirely (no propagation).

    2. After passing to local handlers, the record propagates to the
       parent logger's _handle_record() method — NOT to parent.log().
       This way the level check only happens once at the originating
       logger. Parent handlers still apply their own level filter.

    3. The propagate flag (default True) controls whether records
       bubble up. Set it to False to create isolated loggers.
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.DEBUG):
        self.name = name
        self.level = level
        self.handlers: list[LogHandler] = []
        self.parent: Optional["Logger"] = None
        self.propagate: bool = True

    def set_level(self, level: LogLevel) -> None:
        self.level = level

    def add_handler(self, handler: LogHandler) -> None:
        self.handlers.append(handler)

    def remove_handler(self, handler: LogHandler) -> None:
        self.handlers.remove(handler)

    def log(self, level: LogLevel, message: str, **extra: Any) -> None:
        if level < self.level:
            return
        record = LogRecord(
            level=level,
            message=message,
            logger_name=self.name,
            extra=extra if extra else {},
        )
        self._handle_record(record)

    def _handle_record(self, record: LogRecord) -> None:
        """Pass record to this logger's handlers, then propagate to parent."""
        for handler in self.handlers:
            handler.handle(record)
        if self.propagate and self.parent is not None:
            self.parent._handle_record(record)

    def debug(self, message: str, **extra: Any) -> None:
        self.log(LogLevel.DEBUG, message, **extra)

    def info(self, message: str, **extra: Any) -> None:
        self.log(LogLevel.INFO, message, **extra)

    def warning(self, message: str, **extra: Any) -> None:
        self.log(LogLevel.WARNING, message, **extra)

    def error(self, message: str, **extra: Any) -> None:
        self.log(LogLevel.ERROR, message, **extra)

    def critical(self, message: str, **extra: Any) -> None:
        self.log(LogLevel.CRITICAL, message, **extra)

    def __repr__(self) -> str:
        return f"Logger({self.name!r}, level={self.level.name})"


# ===================================================================
# LogManager (Singleton)
# ===================================================================

class LogManager:
    """
    Key design decisions:

    1. Singleton via __new__ — only one LogManager instance exists.

    2. The root logger (name="") is created lazily on first access.
       It defaults to WARNING level, matching Python's logging module.

    3. Hierarchy is built by splitting on dots:
       "app.db.queries" → parent "app.db" → parent "app" → parent ""

    4. get_logger() recursively creates missing intermediate loggers
       so the hierarchy is always complete.

    5. reset() clears everything — essential for test isolation.
    """

    _instance: Optional["LogManager"] = None
    _loggers: dict[str, Logger] = {}

    def __new__(cls) -> "LogManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_logger(cls, name: str = "") -> Logger:
        if name in cls._loggers:
            return cls._loggers[name]

        # Create the logger
        if name == "":
            # Root logger — default to WARNING
            logger = Logger(name="", level=LogLevel.WARNING)
            logger.propagate = False  # root has nowhere to propagate
        else:
            logger = Logger(name=name, level=LogLevel.DEBUG)
            # Determine parent name
            if "." in name:
                parent_name = name.rsplit(".", 1)[0]
            else:
                parent_name = ""
            logger.parent = cls.get_logger(parent_name)

        cls._loggers[name] = logger
        return logger

    @classmethod
    def reset(cls) -> None:
        cls._loggers.clear()
        cls._instance = None
