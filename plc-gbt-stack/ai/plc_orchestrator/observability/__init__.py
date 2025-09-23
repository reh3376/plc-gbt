"""
Observability module for AI Task Orchestrator.

Provides structured logging, metrics collection, and distributed tracing.
"""

from plc_orchestrator.observability.metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    Timer,
)
from plc_orchestrator.observability.structured_logger import (
    LogContext,
    StructuredLogger,
    configure_logging,
)
from plc_orchestrator.observability.tracing import (
    Span,
    SpanContext,
    Tracer,
    create_span,
    trace,
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "Counter",
    "Histogram",
    "Gauge",
    "Timer",
    # Tracing
    "Tracer",
    "Span",
    "SpanContext",
    "create_span",
    "trace",
    # Logging
    "StructuredLogger",
    "LogContext",
    "configure_logging",
]
