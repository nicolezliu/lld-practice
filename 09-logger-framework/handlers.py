"""
Handlers for the Logging Framework (Observer pattern).

Your job: implement the log handlers.
- Each handler receives log records and outputs them somewhere
- Handlers have their own level filter — they ignore records below their level
- Handlers use a Formatter to convert records to strings

Think about:
- Why does each handler have its own level? (e.g. console=DEBUG, file=ERROR)
- What happens if no formatter is set? (sensible default)
- How does the handler decide whether to process a record?
"""

from abc import ABC, abstractmethod
from typing import Optional
from models import LogRecord, LogLevel
from formatters import LogFormatter, SimpleFormatter


class LogHandler(ABC):
    """
    Abstract base class for log handlers.

    A handler:
    1. Checks if the record's level meets its threshold
    2. Formats the record using its formatter
    3. Outputs the formatted string somewhere (console, file, etc.)
    """

    def __init__(self):
        # TODO: initialize level (default DEBUG — accept everything)
        # TODO: initialize formatter (default SimpleFormatter)
        pass

    def set_level(self, level: LogLevel) -> None:
        """Set the minimum level this handler will process."""
        # TODO
        pass

    def set_formatter(self, formatter: LogFormatter) -> None:
        """Set the formatter used to render records."""
        # TODO
        pass

    def handle(self, record: LogRecord) -> None:
        """
        Process a log record if it meets the level threshold.

        Steps:
        1. Check if record.level >= self.level
        2. If yes, format the record and call emit()
        3. If no, skip silently
        """
        # TODO
        pass

    @abstractmethod
    def emit(self, formatted: str) -> None:
        """
        Output the formatted log string.
        Subclasses implement this for their specific destination.
        """
        ...


class ConsoleHandler(LogHandler):
    """
    Writes formatted log records to stdout.

    This is the simplest handler — just print the string.
    """

    def emit(self, formatted: str) -> None:
        # TODO: print to stdout
        pass


class FileHandler(LogHandler):
    """
    Appends formatted log records to a file.

    Think about:
    - Should you open/close the file on each write, or keep it open?
    - What mode should the file be opened in?
    - Should each record end with a newline?
    """

    def __init__(self, file_path: str):
        """
        Args:
            file_path: path to the log file (will be created if it doesn't exist)
        """
        # TODO: call super().__init__() and store the file path
        pass

    def emit(self, formatted: str) -> None:
        # TODO: append the formatted string to the file (with newline)
        pass


class MemoryHandler(LogHandler):
    """
    Stores formatted log records in an in-memory list.

    This is invaluable for testing — you can inspect exactly what was logged
    without dealing with stdout capture or temp files.
    """

    def __init__(self):
        # TODO: call super().__init__() and create an empty list for records
        pass

    def emit(self, formatted: str) -> None:
        # TODO: append to the in-memory list
        pass

    @property
    def records(self) -> list[str]:
        """Return the list of formatted log strings."""
        # TODO
        pass

    def clear(self) -> None:
        """Clear all stored records."""
        # TODO
        pass
