"""
Test driver for the Logging Framework.

Run this to verify your implementation:
    python main.py

Start with the basic scenarios, then add your own edge cases.
"""

from models import LogLevel, LogRecord
from formatters import SimpleFormatter, DetailedFormatter, JsonFormatter
from handlers import ConsoleHandler, FileHandler, MemoryHandler
from logger import Logger, LogManager


def main():
    print("=" * 60)
    print("LOGGING FRAMEWORK — LLD PRACTICE")
    print("=" * 60)

    # Reset LogManager to start fresh
    LogManager.reset()

    # --- Scenario 1: Basic logging with a console handler ---
    print("\n--- Scenario 1: Basic console logging ---")
    logger = LogManager.get_logger("app")
    console = ConsoleHandler()
    console.set_formatter(DetailedFormatter())
    logger.add_handler(console)
    logger.set_level(LogLevel.DEBUG)

    logger.debug("Application starting up")
    logger.info("Configuration loaded")
    logger.warning("Cache miss rate high")
    logger.error("Failed to connect to database")

    # --- Scenario 2: Logger hierarchy and propagation ---
    print("\n--- Scenario 2: Logger hierarchy ---")
    db_logger = LogManager.get_logger("app.db")
    db_logger.info("Connection pool initialized (size=10)")
    db_logger.error("Query timeout after 30s")
    # These should also appear via the parent "app" logger's console handler

    # --- Scenario 3: Handler-level filtering ---
    print("\n--- Scenario 3: Error-only file handler ---")
    memory = MemoryHandler()
    memory.set_level(LogLevel.ERROR)
    memory.set_formatter(SimpleFormatter())
    logger.add_handler(memory)

    logger.info("This goes to console only")
    logger.error("This goes to console AND memory")
    logger.critical("This too goes to both")

    print(f"  Memory handler captured {len(memory.records)} records:")
    for r in memory.records:
        print(f"    {r}")

    # --- Scenario 4: JSON formatter for structured logging ---
    print("\n--- Scenario 4: JSON structured logging ---")
    json_handler = MemoryHandler()
    json_handler.set_formatter(JsonFormatter())
    api_logger = LogManager.get_logger("app.api")
    api_logger.add_handler(json_handler)

    api_logger.info("Request received", method="GET", path="/users", status=200)
    api_logger.error("Request failed", method="POST", path="/orders", status=500)

    print("  JSON records:")
    for r in json_handler.records:
        print(f"    {r}")

    # --- Scenario 5: Isolated logger (propagation disabled) ---
    print("\n--- Scenario 5: Isolated logger (no propagation) ---")
    audit_logger = LogManager.get_logger("audit")
    audit_handler = MemoryHandler()
    audit_handler.set_formatter(SimpleFormatter())
    audit_logger.add_handler(audit_handler)
    audit_logger.propagate = False
    audit_logger.set_level(LogLevel.INFO)

    audit_logger.info("User login: alice@example.com")
    audit_logger.warning("Failed login attempt: bob@example.com")

    root = LogManager.get_logger("")
    root_handler = MemoryHandler()
    root.add_handler(root_handler)

    audit_logger.error("Brute force detected")

    print(f"  Audit handler has {len(audit_handler.records)} records")
    print(f"  Root handler has {len(root_handler.records)} records (should be 0)")

    # --- Scenario 6: Singleton verification ---
    print("\n--- Scenario 6: Singleton verification ---")
    same_logger = LogManager.get_logger("app.db")
    print(f"  Same instance? {same_logger is db_logger}")
    print(f"  Parent correct? {db_logger.parent is logger}")

    # --- Add your own scenarios below! ---
    # Ideas:
    #   - What happens if you log below the logger's level?
    #   - What happens with a deeply nested logger like "app.api.v2.handlers"?
    #   - Try FileHandler and inspect the output file
    #   - Try changing a handler's formatter after logging some records


if __name__ == "__main__":
    main()
