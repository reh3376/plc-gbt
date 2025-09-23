"""
Enhanced structured logging for observability.

Provides context-aware logging with automatic correlation.
"""

import json
import logging
import sys
import time
from contextvars import ContextVar
from typing import Any

import structlog
from structlog.processors import CallsiteParameter

# Context variables for correlation
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


class LogContext:
    """Context manager for adding logging context."""

    def __init__(self, **kwargs: Any):
        """Initialize with context values."""
        self.context = kwargs
        self._token = None

    def __enter__(self):
        """Enter context."""
        current = _log_context.get()
        new_context = {**current, **self.context}
        self._token = _log_context.set(new_context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if self._token:
            _log_context.reset(self._token)


def add_context_processor(logger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Add context variables to log events."""
    # Add correlation ID
    correlation_id = _correlation_id.get()
    if correlation_id:
        event_dict["correlation_id"] = correlation_id

    # Add custom context
    context = _log_context.get()
    if context:
        event_dict.update(context)

    # Add tracing context if available
    try:
        from plc_orchestrator.observability.tracing import get_tracer

        tracer = get_tracer()
        current_span = tracer.get_current_span()
        if current_span:
            event_dict["trace_id"] = current_span.context.trace_id
            event_dict["span_id"] = current_span.context.span_id
    except ImportError:
        pass

    return event_dict


def add_metrics_processor(logger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """Track log metrics."""
    try:
        from plc_orchestrator.observability.metrics import get_metrics_collector

        collector = get_metrics_collector()

        # Count log levels
        level = event_dict.get("level", "info").lower()
        counter = collector.counter(
            "log_messages_total", labels={"level": level, "logger": logger.name}
        )
        counter.inc()

        # Count errors
        if level in ("error", "critical"):
            error_counter = collector.counter("log_errors_total", labels={"logger": logger.name})
            error_counter.inc()
    except ImportError:
        pass

    return event_dict


class StructuredLogger:
    """Enhanced logger with structured output and context."""

    def __init__(self, name: str, level: str = "INFO"):
        """Initialize structured logger."""
        self.name = name
        self._logger = structlog.get_logger(name)
        self._configure_logging(level)

    def _configure_logging(self, level: str) -> None:
        """Configure structured logging."""
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.CallsiteParameterAdder(
                    parameters=[
                        CallsiteParameter.FILENAME,
                        CallsiteParameter.LINENO,
                        CallsiteParameter.FUNC_NAME,
                    ]
                ),
                add_context_processor,
                add_metrics_processor,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.dict_tracebacks,
                structlog.processors.JSONRenderer()
                if sys.stderr.isatty()
                else structlog.dev.ConsoleRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Configure stdlib logging
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, level.upper()),
        )

    def with_context(self, **kwargs: Any) -> "StructuredLogger":
        """Create logger with additional context."""
        bound_logger = self._logger.bind(**kwargs)
        new_logger = StructuredLogger.__new__(StructuredLogger)
        new_logger.name = self.name
        new_logger._logger = bound_logger
        return new_logger

    def debug(self, msg: str, **kwargs: Any) -> None:
        """Log debug message."""
        self._logger.debug(msg, **kwargs)

    def info(self, msg: str, **kwargs: Any) -> None:
        """Log info message."""
        self._logger.info(msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        """Log warning message."""
        self._logger.warning(msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        """Log error message."""
        self._logger.error(msg, **kwargs)

    def critical(self, msg: str, **kwargs: Any) -> None:
        """Log critical message."""
        self._logger.critical(msg, **kwargs)

    def exception(self, msg: str, **kwargs: Any) -> None:
        """Log exception with traceback."""
        self._logger.exception(msg, **kwargs)

    def log_event(self, event_type: str, **kwargs: Any) -> None:
        """Log a structured event."""
        self._logger.info(event_type, event_type=event_type, **kwargs)

    def log_api_call(
        self,
        method: str,
        endpoint: str,
        status_code: int | None = None,
        duration: float | None = None,
        **kwargs: Any,
    ) -> None:
        """Log API call with standard fields."""
        self._logger.info(
            "api_call",
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            duration=duration,
            **kwargs,
        )

    def log_database_query(
        self,
        operation: str,
        table: str | None = None,
        duration: float | None = None,
        rows_affected: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Log database operation."""
        self._logger.info(
            "database_query",
            operation=operation,
            table=table,
            duration=duration,
            rows_affected=rows_affected,
            **kwargs,
        )

    def log_task_progress(
        self, task_id: str, status: str, progress: float | None = None, **kwargs: Any
    ) -> None:
        """Log task progress update."""
        self._logger.info(
            "task_progress", task_id=task_id, status=status, progress=progress, **kwargs
        )


class JSONFormatter(logging.Formatter):
    """JSON formatter for standard logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": time.time(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "filename": record.filename,
            "lineno": record.lineno,
            "funcName": record.funcName,
        }

        # Add exception info
        if record.exc_info:
            log_data["exc_info"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name",
                "msg",
                "args",
                "created",
                "filename",
                "funcName",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "thread",
                "threadName",
                "exc_info",
                "exc_text",
                "stack_info",
            ):
                log_data[key] = value

        # Add context
        correlation_id = _correlation_id.get()
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        context = _log_context.get()
        if context:
            log_data.update(context)

        return json.dumps(log_data)


def configure_logging(
    level: str = "INFO",
    format: str = "json",
    correlation_id: str | None = None,
) -> StructuredLogger:
    """Configure and get structured logger."""
    if correlation_id:
        _correlation_id.set(correlation_id)

    # Configure structlog
    if format == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.CallsiteParameterAdder(
                parameters=[
                    CallsiteParameter.FILENAME,
                    CallsiteParameter.LINENO,
                    CallsiteParameter.FUNC_NAME,
                ]
            ),
            add_context_processor,
            add_metrics_processor,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.dict_tracebacks,
            renderer,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )

    # Set JSON formatter for all handlers if JSON format
    if format == "json":
        json_formatter = JSONFormatter()
        for handler in logging.root.handlers:
            handler.setFormatter(json_formatter)

    return StructuredLogger("orchestrator", level)


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for all logs."""
    _correlation_id.set(correlation_id)


def get_correlation_id() -> str | None:
    """Get current correlation ID."""
    return _correlation_id.get()
