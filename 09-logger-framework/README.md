# Logger / Logging Framework — LLD Practice

## Problem Statement
Design a logging framework similar to Python's `logging` module or Java's `log4j`.

## Requirements

### Functional
- Support log levels with numeric severity: DEBUG (10), INFO (20), WARNING (30), ERROR (40), CRITICAL (50)
- A logger only processes messages at or above its configured level
- Multiple output handlers: console (stdout), file, in-memory (for testing)
- Configurable formatting — choose how log records are rendered as strings
- Logger hierarchy based on dot-separated names (e.g. `"app.db"` is a child of `"app"`, which is a child of the root logger)
- Log records propagate up the hierarchy — a record logged to `"app.db"` is also handled by `"app"` and the root logger
- Each handler can have its own level filter (e.g. console shows DEBUG+, file only captures ERROR+)

### Non-Functional
- Extensible — easy to add new handlers, formatters, and filters without modifying existing code
- Singleton logger registry — `LogManager.get_logger("app.db")` always returns the same instance
- Lightweight log records — creating a log record should be cheap

## Suggested Design Patterns
- **Singleton** — `LogManager` maintains a global registry of loggers
- **Chain of Responsibility** — log level filtering (logger level → handler level)
- **Observer** — handlers attached to a logger receive log records
- **Strategy** — formatters are interchangeable strategies for rendering records

## Your Task
1. Define `LogLevel` and `LogRecord` in `models.py`
2. Implement formatters in `formatters.py` (Strategy pattern)
3. Implement handlers in `handlers.py` (Observer pattern)
4. Wire up `Logger` and `LogManager` in `logger.py` (Singleton + Chain of Responsibility)
5. Run `main.py` to test your design end-to-end
6. Add your own test scenarios

## Running Tests (by phase)

Work through phases in order — each builds on the previous:

```bash
# Phase 1: Models + Formatters — LogLevel, LogRecord, formatter strategies
python3 -m pytest tests.py -v -k "phase1"

# Phase 2: Handlers — ConsoleHandler, FileHandler, MemoryHandler
python3 -m pytest tests.py -v -k "phase2"

# Phase 3: Logger + LogManager — hierarchy, propagation, filtering
python3 -m pytest tests.py -v -k "phase3"

# All phases
python3 -m pytest tests.py -v
```

## Solution

Once you've given it a solid attempt, check `solution.py` for a reference
implementation. Compare your design choices — there's no single right answer.

## Stretch Goals
- Add async logging (records queued and written on a background thread)
- Add a `RotatingFileHandler` that rolls over after N bytes or N records
- Add a `JsonFormatter` for structured logging (already stubbed — make it production-quality with exception info, extra fields, etc.)
- Add filter objects that can accept/reject records based on custom predicates
