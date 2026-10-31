"""
Models for the Logging Framework.

Your job: fill in the class bodies.
- LogLevel is an enum with numeric values so levels can be compared (DEBUG < INFO < ...)
- LogRecord is a lightweight data container for a single log event
"""

from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class LogLevel(IntEnum):
    """
    Severity levels for log records.

    Uses numeric values so you can compare:  LogLevel.DEBUG < LogLevel.ERROR

    Think about: why IntEnum instead of Enum?
    """
    # TODO: define members with numeric values
    # DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40, CRITICAL = 50
    pass


# ---------------------------------------------------------------------------
# Log Record
# ---------------------------------------------------------------------------

@dataclass
class LogRecord:
    """
    A single log event — created by a Logger, consumed by Handlers.

    Think about:
    - What information does a handler need to format and output a record?
    - Should timestamp be set automatically on creation?
    - What is the `extra` dict for? (structured metadata like user_id, request_id)
    """
    # TODO: define fields
    # - timestamp: datetime (default to now)
    # - level: LogLevel
    # - message: str
    # - logger_name: str
    # - extra: dict[str, Any] (default empty dict)
    pass
