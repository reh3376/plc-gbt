"""
Metrics collection for observability.

Provides counters, histograms, gauges, and timers for performance monitoring.
"""

import time
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)
T = TypeVar("T")


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    TIMER = "timer"


@dataclass
class MetricValue:
    """Container for metric values."""

    type: MetricType
    name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    unit: str | None = None
    description: str | None = None


class MetricExporter(ABC):
    """Base class for metric exporters."""

    @abstractmethod
    def export(self, metrics: list[MetricValue]) -> None:
        """Export metrics to external system."""
        pass


class ConsoleExporter(MetricExporter):
    """Export metrics to console/logs."""

    def export(self, metrics: list[MetricValue]) -> None:
        """Log metrics to console."""
        for metric in metrics:
            logger.info(
                "metric_exported",
                metric_type=metric.type.value,
                name=metric.name,
                value=metric.value,
                labels=metric.labels,
                unit=metric.unit,
            )


class PrometheusExporter(MetricExporter):
    """Export metrics in Prometheus format."""

    def __init__(self, push_gateway_url: str | None = None):
        """Initialize Prometheus exporter."""
        self.push_gateway_url = push_gateway_url
        self._metrics_cache: dict[str, list[MetricValue]] = defaultdict(list)

    def export(self, metrics: list[MetricValue]) -> None:
        """Export metrics to Prometheus."""
        # Group metrics by name
        for metric in metrics:
            self._metrics_cache[metric.name].append(metric)

        # Format as Prometheus text format
        output_lines = []
        for name, values in self._metrics_cache.items():
            if not values:
                continue

            # Add metric description
            first_metric = values[0]
            if first_metric.description:
                output_lines.append(f"# HELP {name} {first_metric.description}")
            output_lines.append(f"# TYPE {name} {first_metric.type.value}")

            # Add metric values
            for value in values:
                labels_str = self._format_labels(value.labels)
                output_lines.append(f"{name}{labels_str} {value.value}")

        # Push to gateway or write to file
        if self.push_gateway_url:
            self._push_to_gateway("\n".join(output_lines))
        else:
            logger.debug("prometheus_metrics", metrics="\n".join(output_lines))

    def _format_labels(self, labels: dict[str, str]) -> str:
        """Format labels for Prometheus."""
        if not labels:
            return ""

        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_pairs) + "}"

    def _push_to_gateway(self, metrics_text: str) -> None:
        """Push metrics to Prometheus push gateway."""
        # Implementation would use requests or similar
        logger.warning("Push gateway not implemented", url=self.push_gateway_url)


class Counter:
    """Monotonically increasing counter."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ):
        """Initialize counter."""
        self.name = name
        self.description = description
        self.labels = labels or {}
        self._value = 0.0

    def inc(self, value: float = 1.0) -> None:
        """Increment counter."""
        if value < 0:
            raise ValueError("Counter can only be incremented with positive values")
        self._value += value
        logger.debug("counter_incremented", name=self.name, value=value)

    def get(self) -> float:
        """Get current value."""
        return self._value

    def to_metric_value(self) -> MetricValue:
        """Convert to MetricValue."""
        return MetricValue(
            type=MetricType.COUNTER,
            name=self.name,
            value=self._value,
            labels=self.labels,
            description=self.description,
        )


class Gauge:
    """Gauge that can go up or down."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ):
        """Initialize gauge."""
        self.name = name
        self.description = description
        self.labels = labels or {}
        self._value = 0.0

    def set(self, value: float) -> None:
        """Set gauge value."""
        self._value = value
        logger.debug("gauge_set", name=self.name, value=value)

    def inc(self, value: float = 1.0) -> None:
        """Increment gauge."""
        self._value += value

    def dec(self, value: float = 1.0) -> None:
        """Decrement gauge."""
        self._value -= value

    def get(self) -> float:
        """Get current value."""
        return self._value

    def to_metric_value(self) -> MetricValue:
        """Convert to MetricValue."""
        return MetricValue(
            type=MetricType.GAUGE,
            name=self.name,
            value=self._value,
            labels=self.labels,
            description=self.description,
        )


class Histogram:
    """Histogram for tracking distributions."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
        buckets: list[float] | None = None,
    ):
        """Initialize histogram."""
        self.name = name
        self.description = description
        self.labels = labels or {}
        self.buckets = buckets or [0.1, 0.5, 1.0, 5.0, 10.0, float("inf")]
        self._values: list[float] = []
        self._sum = 0.0
        self._count = 0

    def observe(self, value: float) -> None:
        """Record an observation."""
        self._values.append(value)
        self._sum += value
        self._count += 1
        logger.debug("histogram_observed", name=self.name, value=value)

    def get_percentile(self, percentile: float) -> float:
        """Get percentile value."""
        if not self._values:
            return 0.0

        sorted_values = sorted(self._values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]

    def to_metric_values(self) -> list[MetricValue]:
        """Convert to MetricValues."""
        metrics = []

        # Count metric
        metrics.append(
            MetricValue(
                type=MetricType.COUNTER,
                name=f"{self.name}_count",
                value=float(self._count),
                labels=self.labels,
            )
        )

        # Sum metric
        metrics.append(
            MetricValue(
                type=MetricType.COUNTER,
                name=f"{self.name}_sum",
                value=self._sum,
                labels=self.labels,
            )
        )

        # Bucket metrics
        for bucket in self.buckets:
            count = sum(1 for v in self._values if v <= bucket)
            bucket_labels = {**self.labels, "le": str(bucket)}
            metrics.append(
                MetricValue(
                    type=MetricType.COUNTER,
                    name=f"{self.name}_bucket",
                    value=float(count),
                    labels=bucket_labels,
                )
            )

        return metrics


class Timer:
    """Timer for measuring durations."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ):
        """Initialize timer."""
        self.name = name
        self.histogram = Histogram(
            name=name,
            description=description,
            labels=labels,
            buckets=[0.001, 0.01, 0.1, 0.5, 1.0, 5.0, 10.0, float("inf")],
        )

    @contextmanager
    def time(self):
        """Context manager for timing operations."""
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start
            self.histogram.observe(duration)
            logger.debug("timer_recorded", name=self.name, duration=duration)

    def time_func(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator for timing functions."""

        def wrapper(*args: Any, **kwargs: Any) -> T:
            with self.time():
                return func(*args, **kwargs)

        return wrapper

    def to_metric_values(self) -> list[MetricValue]:
        """Convert to MetricValues."""
        return self.histogram.to_metric_values()


class MetricsCollector:
    """Central metrics collection and export."""

    def __init__(self, exporters: list[MetricExporter] | None = None):
        """Initialize metrics collector."""
        self.exporters = exporters or [ConsoleExporter()]
        self._metrics: dict[str, Any] = {}
        self._export_interval = 60.0  # seconds
        self._last_export = time.time()

    def counter(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> Counter:
        """Create or get a counter."""
        key = self._metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Counter(name, description, labels)
        return self._metrics[key]

    def gauge(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> Gauge:
        """Create or get a gauge."""
        key = self._metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Gauge(name, description, labels)
        return self._metrics[key]

    def histogram(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
        buckets: list[float] | None = None,
    ) -> Histogram:
        """Create or get a histogram."""
        key = self._metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Histogram(name, description, labels, buckets)
        return self._metrics[key]

    def timer(
        self,
        name: str,
        description: str | None = None,
        labels: dict[str, str] | None = None,
    ) -> Timer:
        """Create or get a timer."""
        key = self._metric_key(name, labels)
        if key not in self._metrics:
            self._metrics[key] = Timer(name, description, labels)
        return self._metrics[key]

    def _metric_key(self, name: str, labels: dict[str, str] | None) -> str:
        """Generate unique key for metric."""
        label_str = ",".join(f"{k}={v}" for k, v in sorted((labels or {}).items()))
        return f"{name}:{label_str}"

    def collect(self) -> list[MetricValue]:
        """Collect all metric values."""
        values = []
        for metric in self._metrics.values():
            if isinstance(metric, (Counter, Gauge)):
                values.append(metric.to_metric_value())
            elif isinstance(metric, (Histogram, Timer)):
                values.extend(metric.to_metric_values())
        return values

    def export(self, force: bool = False) -> None:
        """Export metrics to configured exporters."""
        current_time = time.time()
        if not force and (current_time - self._last_export) < self._export_interval:
            return

        metrics = self.collect()
        for exporter in self.exporters:
            try:
                exporter.export(metrics)
            except Exception as e:
                logger.error(
                    "Failed to export metrics", exporter=type(exporter).__name__, error=str(e)
                )

        self._last_export = current_time

    def configure_export_interval(self, interval: float) -> None:
        """Set export interval in seconds."""
        self._export_interval = interval


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get global metrics collector."""
    return _metrics_collector


def configure_metrics(exporters: list[MetricExporter], export_interval: float = 60.0) -> None:
    """Configure global metrics collection."""
    global _metrics_collector
    _metrics_collector = MetricsCollector(exporters)
    _metrics_collector.configure_export_interval(export_interval)
