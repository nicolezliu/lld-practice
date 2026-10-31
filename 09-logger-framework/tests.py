"""
Phased tests for the Logging Framework.

Run all tests:
    python -m pytest tests.py -v

Run by phase:
    python -m pytest tests.py -v -k "phase1"    # Models + Formatters
    python -m pytest tests.py -v -k "phase2"    # Handlers
    python -m pytest tests.py -v -k "phase3"    # Logger + LogManager

Each phase builds on the previous — start with phase1 and get all tests
green before moving on.
"""

import json
import os
import pytest
from datetime import datetime

from models import LogLevel, LogRecord
from formatters import SimpleFormatter, DetailedFormatter, JsonFormatter
from handlers import ConsoleHandler, FileHandler, MemoryHandler
from logger import Logger, LogManager


# ===================================================================
# PHASE 1: Models + Formatters — LogLevel, LogRecord, formatters
# ===================================================================

class TestPhase1LogLevel:
    """Verify LogLevel enum and numeric ordering."""

    def test_levels_exist(self):
        assert LogLevel.DEBUG
        assert LogLevel.INFO
        assert LogLevel.WARNING
        assert LogLevel.ERROR
        assert LogLevel.CRITICAL

    def test_numeric_values(self):
        assert LogLevel.DEBUG == 10
        assert LogLevel.INFO == 20
        assert LogLevel.WARNING == 30
        assert LogLevel.ERROR == 40
        assert LogLevel.CRITICAL == 50

    def test_ordering(self):
        assert LogLevel.DEBUG < LogLevel.INFO
        assert LogLevel.INFO < LogLevel.WARNING
        assert LogLevel.WARNING < LogLevel.ERROR
        assert LogLevel.ERROR < LogLevel.CRITICAL

    def test_comparison_with_int(self):
        assert LogLevel.DEBUG >= 10
        assert LogLevel.CRITICAL <= 50


class TestPhase1LogRecord:
    """Verify LogRecord data class."""

    def test_basic_creation(self):
        record = LogRecord(
            level=LogLevel.INFO,
            message="test message",
            logger_name="app",
        )
        assert record.level == LogLevel.INFO
        assert record.message == "test message"
        assert record.logger_name == "app"

    def test_timestamp_auto_set(self):
        before = datetime.now()
        record = LogRecord(
            level=LogLevel.INFO,
            message="test",
            logger_name="app",
        )
        after = datetime.now()
        assert before <= record.timestamp <= after

    def test_extra_defaults_to_empty_dict(self):
        record = LogRecord(
            level=LogLevel.INFO,
            message="test",
            logger_name="app",
        )
        assert record.extra == {}

    def test_extra_with_data(self):
        record = LogRecord(
            level=LogLevel.ERROR,
            message="failed",
            logger_name="app.db",
            extra={"user_id": 42, "request_id": "abc-123"},
        )
        assert record.extra["user_id"] == 42
        assert record.extra["request_id"] == "abc-123"


class TestPhase1SimpleFormatter:
    """Verify SimpleFormatter output."""

    def test_format_info(self):
        fmt = SimpleFormatter()
        record = LogRecord(level=LogLevel.INFO, message="hello", logger_name="app")
        result = fmt.format(record)
        assert result == "[INFO] hello"

    def test_format_error(self):
        fmt = SimpleFormatter()
        record = LogRecord(level=LogLevel.ERROR, message="boom", logger_name="app")
        result = fmt.format(record)
        assert result == "[ERROR] boom"


class TestPhase1DetailedFormatter:
    """Verify DetailedFormatter output."""

    def test_format_includes_timestamp_and_logger(self):
        fmt = DetailedFormatter()
        ts = datetime(2024, 1, 15, 10, 30, 0)
        record = LogRecord(
            level=LogLevel.WARNING,
            message="pool exhausted",
            logger_name="app.db",
            timestamp=ts,
        )
        result = fmt.format(record)
        assert result == "2024-01-15 10:30:00 [WARNING] app.db: pool exhausted"

    def test_format_debug_level(self):
        fmt = DetailedFormatter()
        ts = datetime(2024, 6, 1, 8, 0, 0)
        record = LogRecord(
            level=LogLevel.DEBUG,
            message="entering function",
            logger_name="app.core",
            timestamp=ts,
        )
        result = fmt.format(record)
        assert result == "2024-06-01 08:00:00 [DEBUG] app.core: entering function"


class TestPhase1JsonFormatter:
    """Verify JsonFormatter output."""

    def test_format_parses_as_json(self):
        fmt = JsonFormatter()
        record = LogRecord(
            level=LogLevel.ERROR,
            message="connection refused",
            logger_name="app.db",
        )
        result = fmt.format(record)
        data = json.loads(result)
        assert data["level"] == "ERROR"
        assert data["message"] == "connection refused"
        assert data["logger"] == "app.db"
        assert "timestamp" in data

    def test_format_includes_extra(self):
        fmt = JsonFormatter()
        record = LogRecord(
            level=LogLevel.INFO,
            message="request",
            logger_name="app",
            extra={"user_id": 42},
        )
        result = fmt.format(record)
        data = json.loads(result)
        assert data["extra"]["user_id"] == 42

    def test_format_omits_extra_when_empty(self):
        fmt = JsonFormatter()
        record = LogRecord(
            level=LogLevel.INFO,
            message="test",
            logger_name="app",
        )
        result = fmt.format(record)
        data = json.loads(result)
        assert "extra" not in data


# ===================================================================
# PHASE 2: Handlers — ConsoleHandler, FileHandler, MemoryHandler
# ===================================================================

class TestPhase2MemoryHandler:
    """MemoryHandler is the workhorse for testing — verify it thoroughly."""

    def test_stores_records(self):
        handler = MemoryHandler()
        record = LogRecord(level=LogLevel.INFO, message="hello", logger_name="test")
        handler.handle(record)
        assert len(handler.records) == 1
        assert "[INFO] hello" in handler.records[0]

    def test_multiple_records(self):
        handler = MemoryHandler()
        for msg in ["one", "two", "three"]:
            record = LogRecord(level=LogLevel.INFO, message=msg, logger_name="test")
            handler.handle(record)
        assert len(handler.records) == 3

    def test_clear(self):
        handler = MemoryHandler()
        record = LogRecord(level=LogLevel.INFO, message="hello", logger_name="test")
        handler.handle(record)
        handler.clear()
        assert len(handler.records) == 0

    def test_level_filtering(self):
        handler = MemoryHandler()
        handler.set_level(LogLevel.ERROR)
        handler.handle(LogRecord(level=LogLevel.DEBUG, message="skip", logger_name="t"))
        handler.handle(LogRecord(level=LogLevel.INFO, message="skip", logger_name="t"))
        handler.handle(LogRecord(level=LogLevel.WARNING, message="skip", logger_name="t"))
        handler.handle(LogRecord(level=LogLevel.ERROR, message="keep", logger_name="t"))
        handler.handle(LogRecord(level=LogLevel.CRITICAL, message="keep", logger_name="t"))
        assert len(handler.records) == 2

    def test_custom_formatter(self):
        handler = MemoryHandler()
        handler.set_formatter(DetailedFormatter())
        ts = datetime(2024, 1, 1, 12, 0, 0)
        record = LogRecord(
            level=LogLevel.INFO,
            message="formatted",
            logger_name="app",
            timestamp=ts,
        )
        handler.handle(record)
        assert handler.records[0] == "2024-01-01 12:00:00 [INFO] app: formatted"

    def test_records_returns_copy(self):
        handler = MemoryHandler()
        record = LogRecord(level=LogLevel.INFO, message="hello", logger_name="test")
        handler.handle(record)
        records = handler.records
        records.clear()  # modifying the returned list
        assert len(handler.records) == 1  # original should be unaffected


class TestPhase2ConsoleHandler:
    """Verify ConsoleHandler writes to stdout."""

    def test_prints_to_stdout(self, capsys):
        handler = ConsoleHandler()
        record = LogRecord(level=LogLevel.INFO, message="console test", logger_name="t")
        handler.handle(record)
        captured = capsys.readouterr()
        assert "[INFO] console test" in captured.out

    def test_respects_level(self, capsys):
        handler = ConsoleHandler()
        handler.set_level(LogLevel.ERROR)
        record = LogRecord(level=LogLevel.DEBUG, message="hidden", logger_name="t")
        handler.handle(record)
        captured = capsys.readouterr()
        assert captured.out == ""


class TestPhase2FileHandler:
    """Verify FileHandler writes to file."""

    def test_writes_to_file(self, tmp_path):
        log_file = tmp_path / "test.log"
        handler = FileHandler(str(log_file))
        record = LogRecord(level=LogLevel.ERROR, message="file test", logger_name="t")
        handler.handle(record)
        content = log_file.read_text()
        assert "[ERROR] file test" in content

    def test_appends_multiple_records(self, tmp_path):
        log_file = tmp_path / "test.log"
        handler = FileHandler(str(log_file))
        handler.handle(LogRecord(level=LogLevel.INFO, message="line 1", logger_name="t"))
        handler.handle(LogRecord(level=LogLevel.INFO, message="line 2", logger_name="t"))
        lines = log_file.read_text().strip().split("\n")
        assert len(lines) == 2


# ===================================================================
# PHASE 3: Logger + LogManager — hierarchy, propagation, filtering
# ===================================================================

class TestPhase3Logger:
    """Verify Logger behavior."""

    def test_convenience_methods(self):
        handler = MemoryHandler()
        logger = Logger("test")
        logger.add_handler(handler)
        logger.debug("d")
        logger.info("i")
        logger.warning("w")
        logger.error("e")
        logger.critical("c")
        assert len(handler.records) == 5
        assert "[DEBUG] d" in handler.records[0]
        assert "[CRITICAL] c" in handler.records[4]

    def test_level_filtering(self):
        handler = MemoryHandler()
        logger = Logger("test", level=LogLevel.WARNING)
        logger.add_handler(handler)
        logger.debug("skip")
        logger.info("skip")
        logger.warning("keep")
        logger.error("keep")
        assert len(handler.records) == 2

    def test_set_level(self):
        handler = MemoryHandler()
        logger = Logger("test", level=LogLevel.ERROR)
        logger.add_handler(handler)
        logger.warning("skip")
        assert len(handler.records) == 0
        logger.set_level(LogLevel.DEBUG)
        logger.warning("now visible")
        assert len(handler.records) == 1

    def test_multiple_handlers(self):
        h1 = MemoryHandler()
        h2 = MemoryHandler()
        logger = Logger("test")
        logger.add_handler(h1)
        logger.add_handler(h2)
        logger.info("broadcast")
        assert len(h1.records) == 1
        assert len(h2.records) == 1

    def test_remove_handler(self):
        h1 = MemoryHandler()
        h2 = MemoryHandler()
        logger = Logger("test")
        logger.add_handler(h1)
        logger.add_handler(h2)
        logger.remove_handler(h1)
        logger.info("only h2")
        assert len(h1.records) == 0
        assert len(h2.records) == 1

    def test_extra_kwargs_in_record(self):
        handler = MemoryHandler()
        handler.set_formatter(JsonFormatter())
        logger = Logger("test")
        logger.add_handler(handler)
        logger.info("request", user_id=42, path="/api/v1")
        data = json.loads(handler.records[0])
        assert data["extra"]["user_id"] == 42
        assert data["extra"]["path"] == "/api/v1"


class TestPhase3Propagation:
    """Verify log record propagation through logger hierarchy."""

    def test_propagates_to_parent(self):
        parent_handler = MemoryHandler()
        child_handler = MemoryHandler()

        parent = Logger("app")
        parent.add_handler(parent_handler)

        child = Logger("app.db")
        child.add_handler(child_handler)
        child.parent = parent

        child.info("database query")
        # Record should appear in both handlers
        assert len(child_handler.records) == 1
        assert len(parent_handler.records) == 1

    def test_propagation_disabled(self):
        parent_handler = MemoryHandler()
        child_handler = MemoryHandler()

        parent = Logger("app")
        parent.add_handler(parent_handler)

        child = Logger("app.db")
        child.add_handler(child_handler)
        child.parent = parent
        child.propagate = False

        child.info("isolated")
        assert len(child_handler.records) == 1
        assert len(parent_handler.records) == 0  # did not propagate

    def test_propagation_skips_level_check_on_parent(self):
        """
        Parent level should NOT re-filter propagated records.
        If child accepts the record, parent's handlers get it
        (handlers still apply their own level filter though).
        """
        parent_handler = MemoryHandler()

        parent = Logger("app", level=LogLevel.ERROR)
        parent.add_handler(parent_handler)

        child = Logger("app.db", level=LogLevel.DEBUG)
        child.parent = parent

        child.debug("should propagate despite parent level")
        assert len(parent_handler.records) == 1

    def test_handler_level_still_filters_during_propagation(self):
        """
        Parent's handler has its own level filter — it can reject
        records even though propagation delivered them.
        """
        parent_handler = MemoryHandler()
        parent_handler.set_level(LogLevel.ERROR)

        parent = Logger("app")
        parent.add_handler(parent_handler)

        child = Logger("app.db")
        child.parent = parent

        child.info("below handler threshold")
        assert len(parent_handler.records) == 0

    def test_multi_level_propagation(self):
        """Records propagate through multiple levels: grandchild → child → root."""
        root_handler = MemoryHandler()
        root = Logger("")
        root.add_handler(root_handler)
        root.propagate = False

        mid = Logger("app")
        mid.parent = root

        leaf = Logger("app.db")
        leaf.parent = mid

        leaf.error("deep error")
        assert len(root_handler.records) == 1


class TestPhase3LogManager:
    """Verify Singleton LogManager and logger hierarchy."""

    def setup_method(self):
        """Reset LogManager between tests for isolation."""
        LogManager.reset()

    def test_get_root_logger(self):
        root = LogManager.get_logger("")
        assert root.name == ""

    def test_root_logger_default_level(self):
        root = LogManager.get_logger("")
        assert root.level == LogLevel.WARNING

    def test_same_name_returns_same_instance(self):
        logger1 = LogManager.get_logger("app")
        logger2 = LogManager.get_logger("app")
        assert logger1 is logger2

    def test_hierarchy_parent_wiring(self):
        child = LogManager.get_logger("app.db")
        parent = LogManager.get_logger("app")
        root = LogManager.get_logger("")
        assert child.parent is parent
        assert parent.parent is root

    def test_deep_hierarchy(self):
        leaf = LogManager.get_logger("app.db.queries.slow")
        queries = LogManager.get_logger("app.db.queries")
        db = LogManager.get_logger("app.db")
        app = LogManager.get_logger("app")
        root = LogManager.get_logger("")
        assert leaf.parent is queries
        assert queries.parent is db
        assert db.parent is app
        assert app.parent is root

    def test_propagation_through_manager_hierarchy(self):
        root = LogManager.get_logger("")
        root_handler = MemoryHandler()
        root.add_handler(root_handler)

        child = LogManager.get_logger("app.db")
        child.info("propagated")
        assert len(root_handler.records) == 1

    def test_reset_clears_all(self):
        LogManager.get_logger("app")
        LogManager.reset()
        # After reset, "app" should be a fresh instance
        logger = LogManager.get_logger("app")
        assert logger.handlers == []

    def test_singleton_identity(self):
        m1 = LogManager()
        m2 = LogManager()
        assert m1 is m2
