"""Logging configuration and utilities for the PLC Task Orchestrator."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    import structlog

    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False


def get_logger(name: str, config: dict[str, Any] | None = None) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)
        config: Optional configuration dict

    Returns:
        Configured logger instance
    """
    if STRUCTLOG_AVAILABLE and (config is None or config.get("use_structlog", True)):
        return get_structured_logger(name, config)
    else:
        return get_standard_logger(name, config)


def get_structured_logger(name: str, config: dict[str, Any] | None = None) -> Any:
    """
    Get a structured logger using structlog.

    Args:
        name: Logger name
        config: Optional configuration

    Returns:
        Structured logger instance
    """
    # Configure structlog if not already configured
    if not structlog.is_configured():
        processors = [
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        # Add JSON renderer for production, console for development
        if config and config.get("environment") == "production":
            processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    # Get logger and bind context
    logger = structlog.get_logger(name)

    # Add default context
    if config:
        logger = logger.bind(
            service="plc_orchestrator",
            environment=config.get("environment", "development"),
            version=config.get("version", "2.0.0"),
        )

    return logger


def get_standard_logger(name: str, config: dict[str, Any] | None = None) -> logging.Logger:
    """
    Get a standard Python logger.

    Args:
        name: Logger name
        config: Optional configuration

    Returns:
        Standard logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if no handlers exist
    if not logger.handlers:
        # Set level
        level = logging.INFO
        if config:
            level_name = config.get("log_level", "INFO").upper()
            level = getattr(logging, level_name, logging.INFO)

        logger.setLevel(level)

        # Create handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        if config and config.get("environment") == "production":
            formatter = logging.Formatter(
                '{"time": "%(asctime)s", "level": "%(levelname)s", '
                '"logger": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s - %(message)s")

        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def setup_file_logging(
    log_dir: Path,
    log_file: str = "orchestrator.log",
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up file-based logging with rotation.

    Args:
        log_dir: Directory for log files
        log_file: Log file name
        max_bytes: Maximum size before rotation
        backup_count: Number of backup files to keep
    """
    from logging.handlers import RotatingFileHandler

    # Ensure log directory exists
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create file handler
    file_handler = RotatingFileHandler(
        log_dir / log_file, maxBytes=max_bytes, backupCount=backup_count
    )

    # Set formatter
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s - %(name)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add to root logger
    logging.getLogger().addHandler(file_handler)


class LogContext:
    """Context manager for temporary log context."""

    def __init__(self, logger: Any, **context: Any) -> None:
        self.logger = logger
        self.context = context
        self.original_logger = None

    def __enter__(self) -> Any:
        """Enter context and bind values."""
        if hasattr(self.logger, "bind"):
            self.original_logger = self.logger
            self.logger = self.logger.bind(**self.context)
        return self.logger

    def __exit__(self, *args: Any) -> None:
        """Exit context and restore original logger."""
        if self.original_logger:
            self.logger = self.original_logger


def log_execution_time(logger: Any, operation: str) -> Any:
    """
    Decorator to log execution time of functions.

    Args:
        logger: Logger instance
        operation: Operation name for logging

    Returns:
        Decorator function
    """

    def decorator(func: Any) -> Any:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = datetime.now()

            try:
                if hasattr(logger, "info"):
                    logger.info(f"{operation} started")

                result = func(*args, **kwargs)

                duration = (datetime.now() - start_time).total_seconds()
                if hasattr(logger, "info"):
                    logger.info(f"{operation} completed", extra={"duration_seconds": duration})

                return result

            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                if hasattr(logger, "error"):
                    logger.error(
                        f"{operation} failed", extra={"duration_seconds": duration, "error": str(e)}
                    )
                raise

        return wrapper

    return decorator
