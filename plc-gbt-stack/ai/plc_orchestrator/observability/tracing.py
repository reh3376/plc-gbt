"""
Distributed tracing for observability.

Provides spans, context propagation, and trace correlation.
"""

import functools
import time
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)
T = TypeVar("T")


class SpanKind(Enum):
    """Types of spans."""

    INTERNAL = "internal"
    SERVER = "server"
    CLIENT = "client"
    PRODUCER = "producer"
    CONSUMER = "consumer"


class SpanStatus(Enum):
    """Span completion status."""

    OK = "ok"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class SpanContext:
    """Context for distributed tracing."""

    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    span_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_span_id: str | None = None
    trace_flags: int = 0
    trace_state: dict[str, str] = field(default_factory=dict)
    baggage: dict[str, str] = field(default_factory=dict)

    def to_headers(self) -> dict[str, str]:
        """Convert to HTTP headers for propagation."""
        headers = {
            "X-Trace-Id": self.trace_id,
            "X-Span-Id": self.span_id,
            "X-Trace-Flags": str(self.trace_flags),
        }

        if self.parent_span_id:
            headers["X-Parent-Span-Id"] = self.parent_span_id

        # Add trace state
        if self.trace_state:
            state_str = ",".join(f"{k}={v}" for k, v in self.trace_state.items())
            headers["X-Trace-State"] = state_str

        # Add baggage
        if self.baggage:
            baggage_str = ",".join(f"{k}={v}" for k, v in self.baggage.items())
            headers["X-Baggage"] = baggage_str

        return headers

    @classmethod
    def from_headers(cls, headers: dict[str, str]) -> "SpanContext":
        """Create context from HTTP headers."""
        context = cls(
            trace_id=headers.get("X-Trace-Id", str(uuid.uuid4())),
            span_id=headers.get("X-Span-Id", str(uuid.uuid4())),
            parent_span_id=headers.get("X-Parent-Span-Id"),
            trace_flags=int(headers.get("X-Trace-Flags", "0")),
        )

        # Parse trace state
        if "X-Trace-State" in headers:
            for pair in headers["X-Trace-State"].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    context.trace_state[k.strip()] = v.strip()

        # Parse baggage
        if "X-Baggage" in headers:
            for pair in headers["X-Baggage"].split(","):
                if "=" in pair:
                    k, v = pair.split("=", 1)
                    context.baggage[k.strip()] = v.strip()

        return context


@dataclass
class SpanEvent:
    """Event within a span."""

    name: str
    timestamp: float = field(default_factory=time.time)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass
class Span:
    """Distributed tracing span."""

    name: str
    context: SpanContext
    kind: SpanKind = SpanKind.INTERNAL
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    status: SpanStatus = SpanStatus.OK
    attributes: dict[str, Any] = field(default_factory=dict)
    events: list[SpanEvent] = field(default_factory=list)
    parent: "Span | None" = None

    def set_attribute(self, key: str, value: Any) -> None:
        """Set span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add event to span."""
        event = SpanEvent(name, attributes=attributes or {})
        self.events.append(event)
        logger.debug(
            "span_event_added",
            span_id=self.context.span_id,
            event_name=name,
            attributes=attributes,
        )

    def set_status(self, status: SpanStatus, message: str | None = None) -> None:
        """Set span status."""
        self.status = status
        if message:
            self.set_attribute("status.message", message)

    def end(self) -> None:
        """End the span."""
        if self.end_time is None:
            self.end_time = time.time()
            duration = self.end_time - self.start_time

            logger.info(
                "span_ended",
                trace_id=self.context.trace_id,
                span_id=self.context.span_id,
                name=self.name,
                duration=duration,
                status=self.status.value,
                attributes=self.attributes,
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert span to dictionary."""
        return {
            "trace_id": self.context.trace_id,
            "span_id": self.context.span_id,
            "parent_span_id": self.context.parent_span_id,
            "name": self.name,
            "kind": self.kind.value,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": (self.end_time - self.start_time) if self.end_time else None,
            "status": self.status.value,
            "attributes": self.attributes,
            "events": [
                {
                    "name": event.name,
                    "timestamp": event.timestamp,
                    "attributes": event.attributes,
                }
                for event in self.events
            ],
        }


class SpanExporter:
    """Base class for span exporters."""

    def export(self, spans: list[Span]) -> None:
        """Export spans to external system."""
        raise NotImplementedError


class ConsoleSpanExporter(SpanExporter):
    """Export spans to console."""

    def export(self, spans: list[Span]) -> None:
        """Log spans to console."""
        for span in spans:
            logger.info("span_exported", **span.to_dict())


class JaegerExporter(SpanExporter):
    """Export spans to Jaeger."""

    def __init__(self, endpoint: str, service_name: str):
        """Initialize Jaeger exporter."""
        self.endpoint = endpoint
        self.service_name = service_name

    def export(self, spans: list[Span]) -> None:
        """Export spans to Jaeger."""
        # Convert to Jaeger format
        jaeger_spans = []
        for span in spans:
            jaeger_span = {
                "traceID": span.context.trace_id,
                "spanID": span.context.span_id,
                "parentSpanID": span.context.parent_span_id or "",
                "operationName": span.name,
                "startTime": int(span.start_time * 1_000_000),  # microseconds
                "duration": int((span.end_time - span.start_time) * 1_000_000)
                if span.end_time
                else 0,
                "tags": [
                    {"key": k, "type": "string", "value": str(v)}
                    for k, v in span.attributes.items()
                ],
                "process": {
                    "serviceName": self.service_name,
                    "tags": [],
                },
            }
            jaeger_spans.append(jaeger_span)

        # In a real implementation, this would send to Jaeger
        logger.debug("jaeger_export", endpoint=self.endpoint, spans=len(jaeger_spans))


class Tracer:
    """Main tracer for creating and managing spans."""

    def __init__(self, service_name: str, exporters: list[SpanExporter] | None = None):
        """Initialize tracer."""
        self.service_name = service_name
        self.exporters = exporters or [ConsoleSpanExporter()]
        self._spans: list[Span] = []
        self._current_span: Span | None = None

    @contextmanager
    def start_span(
        self,
        name: str,
        kind: SpanKind = SpanKind.INTERNAL,
        attributes: dict[str, Any] | None = None,
        context: SpanContext | None = None,
    ):
        """Start a new span."""
        # Create context
        if context is None:
            if self._current_span:
                # Create child span
                context = SpanContext(
                    trace_id=self._current_span.context.trace_id,
                    parent_span_id=self._current_span.context.span_id,
                    trace_state=self._current_span.context.trace_state.copy(),
                    baggage=self._current_span.context.baggage.copy(),
                )
            else:
                # Create root span
                context = SpanContext()

        # Create span
        span = Span(
            name=name,
            context=context,
            kind=kind,
            attributes=attributes or {},
            parent=self._current_span,
        )

        # Set as current
        previous_span = self._current_span
        self._current_span = span

        logger.debug(
            "span_started",
            trace_id=span.context.trace_id,
            span_id=span.context.span_id,
            name=name,
        )

        try:
            yield span
        except Exception as e:
            span.set_status(SpanStatus.ERROR, str(e))
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            raise
        finally:
            span.end()
            self._spans.append(span)
            self._current_span = previous_span

            # Export if batch size reached
            if len(self._spans) >= 100:
                self.export()

    def get_current_span(self) -> Span | None:
        """Get currently active span."""
        return self._current_span

    def export(self) -> None:
        """Export collected spans."""
        if not self._spans:
            return

        spans_to_export = self._spans[:]
        self._spans.clear()

        for exporter in self.exporters:
            try:
                exporter.export(spans_to_export)
            except Exception as e:
                logger.error(
                    "Failed to export spans",
                    exporter=type(exporter).__name__,
                    error=str(e),
                )


# Global tracer instance
_tracer: Tracer | None = None


def configure_tracing(service_name: str, exporters: list[SpanExporter] | None = None) -> None:
    """Configure global tracer."""
    global _tracer
    _tracer = Tracer(service_name, exporters)


def get_tracer() -> Tracer:
    """Get global tracer."""
    global _tracer
    if _tracer is None:
        _tracer = Tracer("orchestrator")
    return _tracer


@contextmanager
def create_span(
    name: str,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: dict[str, Any] | None = None,
):
    """Create a span using global tracer."""
    tracer = get_tracer()
    with tracer.start_span(name, kind, attributes) as span:
        yield span


def trace(
    name: str | None = None,
    kind: SpanKind = SpanKind.INTERNAL,
    attributes: dict[str, Any] | None = None,
):
    """Decorator for tracing functions."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        span_name = name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            with create_span(span_name, kind, attributes) as span:
                # Add function arguments as attributes
                if args:
                    span.set_attribute("args", str(args)[:100])
                if kwargs:
                    span.set_attribute("kwargs", str(kwargs)[:100])

                return func(*args, **kwargs)

        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            with create_span(span_name, kind, attributes) as span:
                # Add function arguments as attributes
                if args:
                    span.set_attribute("args", str(args)[:100])
                if kwargs:
                    span.set_attribute("kwargs", str(kwargs)[:100])

                return await func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
