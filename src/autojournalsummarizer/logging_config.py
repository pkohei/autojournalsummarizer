"""Structured logging configuration for AutoJournalSummarizer."""

import logging
import sys
from pathlib import Path
from typing import Any

from .config import Settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with structured information."""
        log_entry = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "component": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_entry.update(record.extra_fields)

        return str(log_entry)


def setup_logging(settings: Settings, test_mode: bool = False) -> logging.Logger:
    """Setup structured logging for the application.

    Args:
        settings: Application settings.
        test_mode: Whether running in test mode.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("autojournalsummarizer")

    # Clear any existing handlers
    logger.handlers.clear()

    # Set log level
    log_level = logging.DEBUG if test_mode else logging.INFO
    logger.setLevel(log_level)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Simple format for console in test mode
    if test_mode:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    else:
        formatter = StructuredFormatter()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for production
    if not test_mode:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        file_handler = logging.FileHandler(log_dir / "autojournalsummarizer.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(StructuredFormatter())
        logger.addHandler(file_handler)

    return logger


def log_with_context(
    logger: logging.Logger, level: int, message: str, **context: Any
) -> None:
    """Log message with additional context.

    Args:
        logger: Logger instance.
        level: Log level.
        message: Log message.
        **context: Additional context fields.
    """
    extra = {"extra_fields": context} if context else {}
    logger.log(level, message, extra=extra)
