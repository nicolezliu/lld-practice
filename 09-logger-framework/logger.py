"""
Logger and LogManager for the Logging Framework.

Your job: implement the core logging logic.

Logger:
- Has a name, a level, a list of handlers, and an optional parent reference
- Provides convenience methods: debug(), info(), warning(), error(), critical()
- Records propagate up the hierarchy: "app.db" → "app" → root

LogManager (Singleton):
- get_logger(name) returns a Logger, creating it if needed
- Builds hierarchy from dot-separated names:
    "app.db"  →  parent is "app"
    "app"     →  parent is root ("")
    "auth"    →  parent is root ("")
- Same name always returns the same Logger instance

Think about:
- What level should the root logger default to?
- Should a child logger's level override propagation?
- What happens if a logger has no handlers? (relies on parent's handlers via propagation)
"""

from typing import Optional, Any
from models import LogLevel, LogRecord
from handlers import LogHandler
from datetime import datetime


class Logger:
    """
    A named logger that dispatches log records to handlers.

    Think about:
    - When log() is called, should it check the logger's own level first?
    - After handling locally, should it propagate to parent?
    - What if propagate is False?
    """

    def __init__(self, name: str, level: LogLevel = LogLevel.DEBUG):
        """
        Args:
            name: dot-separated logger name (e.g. "app.db.queries")
            level: minimum level this logger will process
        """
        # TODO: initialize name, level, handlers list, parent reference, propagate flag
        pass

    def set_level(self, level: LogLevel) -> None:
        """Set the minimum level this logger will process."""
        # TODO
        pass

    def add_handler(self, handler: LogHandler) -> None:
        """Attach a handler to this logger."""
        # TODO
        pass

    def remove_handler(self, handler: LogHandler) -> None:
        """Remove a handler from this logger."""
        # TODO
        pass

    def log(self, level: LogLevel, message: str, **extra: Any) -> None:
        """
        Log a message at the given level.

        Steps:
        1. Check if level >= self.level — if not, return immediately
        2. Create a LogRecord
        3. Pass the record to each handler attached to this logger
        4. If self.propagate is True and self.parent exists, pass the
           record to the parent logger's handlers (NOT to parent.log() —
           the level check should only happen once at the originating logger)
        """
        # TODO
        pass

    def debug(self, message: str, **extra: Any) -> None:
        """Log a message at DEBUG level."""
        # TODO
        pass

    def info(self, message: str, **extra: Any) -> None:
        """Log a message at INFO level."""
        # TODO
        pass

    def warning(self, message: str, **extra: Any) -> None:
        """Log a message at WARNING level."""
        # TODO
        pass

    def error(self, message: str, **extra: Any) -> None:
        """Log a message at ERROR level."""
        # TODO
        pass

    def critical(self, message: str, **extra: Any) -> None:
        """Log a message at CRITICAL level."""
        # TODO
        pass

    def __repr__(self) -> str:
        return f"Logger({self.name!r}, level={self.level.name})"


class LogManager:
    """
    Singleton registry of loggers.

    LogManager.get_logger("app.db") should:
    1. Return the existing logger if one with that name exists
    2. Create a new logger, wire up its parent, and cache it

    Hierarchy example:
        get_logger("app.db.queries")
        → creates "app.db.queries" with parent "app.db"
        → creates "app.db" with parent "app"
        → creates "app" with parent root ("")
        → root already exists (created on first access)

    Think about:
    - How do you ensure only one instance of LogManager exists? (Singleton)
    - How do you extract the parent name from a dot-separated string?
    """

    _instance: Optional["LogManager"] = None
    _loggers: dict[str, Logger] = {}

    def __new__(cls) -> "LogManager":
        # TODO: implement Singleton pattern
        pass

    @classmethod
    def get_logger(cls, name: str = "") -> Logger:
        """
        Get or create a logger with the given name.

        Args:
            name: dot-separated logger name ("" = root logger)

        Returns:
            The Logger instance for this name.
        """
        # TODO:
        # 1. If name is already in the registry, return it
        # 2. Create a new Logger
        # 3. Determine the parent name (e.g. "app.db" → "app", "app" → "")
        # 4. Recursively get or create the parent logger
        # 5. Set the new logger's parent
        # 6. Cache and return
        pass

    @classmethod
    def reset(cls) -> None:
        """
        Clear all loggers. Useful for testing.
        """
        # TODO: clear the registry
        pass
