# Observability Guide

## Overview

The AI Task Orchestrator includes comprehensive observability features to monitor performance, track behavior, and troubleshoot issues in production. This guide covers metrics collection, distributed tracing, and structured logging.

## Features

### 1. Metrics Collection

Track quantitative measurements of system behavior.

#### Available Metrics

- **Counters**: Track counts of events (tasks analyzed, validations performed)
- **Histograms**: Track distributions (request durations, response sizes)
- **Gauges**: Track current values (active tasks, memory usage)
- **Timers**: Track operation durations

#### Basic Usage

```python
from plc_orchestrator.observability import get_metrics_collector

# Get the global metrics collector
metrics = get_metrics_collector()

# Count events
counter = metrics.counter("tasks_processed", labels={"status": "success"})
counter.inc()

# Track durations
timer = metrics.timer("api_request_duration")
with timer.time():
    # Perform operation
    response = make_api_request()

# Track current values
gauge = metrics.gauge("active_connections")
gauge.set(42)

# Track distributions
histogram = metrics.histogram("response_size_bytes")
histogram.observe(len(response_data))
```

#### Configuring Exporters

```python
from plc_orchestrator.observability import configure_metrics, PrometheusExporter

# Configure Prometheus exporter
exporters = [
    PrometheusExporter(push_gateway_url="http://localhost:9091"),
]
configure_metrics(exporters, export_interval=30.0)
```

### 2. Distributed Tracing

Track request flow across components and services.

#### Creating Spans

```python
from plc_orchestrator.observability import create_span, SpanKind

# Create a span for an operation
with create_span("process_data", kind=SpanKind.INTERNAL) as span:
    span.set_attribute("data.size", len(data))
    span.set_attribute("data.type", "json")
    
    # Process data
    result = process(data)
    
    # Add events
    span.add_event("validation_completed", {"valid": True})
    
    # Nested spans
    with create_span("parse_json") as child_span:
        parsed = json.loads(data)
```

#### Trace Propagation

```python
from plc_orchestrator.observability import SpanContext

# Extract context from incoming request
headers = request.headers
context = SpanContext.from_headers(headers)

# Create span with parent context
with create_span("handle_request", context=context) as span:
    # Process request
    response = handle(request)
    
    # Propagate context to downstream service
    downstream_headers = span.context.to_headers()
    downstream_response = requests.get(url, headers=downstream_headers)
```

#### Function Tracing

```python
from plc_orchestrator.observability import trace

@trace(name="calculate_metrics", kind=SpanKind.INTERNAL)
def calculate_metrics(data: list[float]) -> dict[str, float]:
    """Automatically traced function."""
    return {
        "mean": sum(data) / len(data),
        "max": max(data),
        "min": min(data),
    }

# Async functions also supported
@trace()
async def fetch_data(url: str) -> dict:
    """Traced async function."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

### 3. Structured Logging

Enhanced logging with automatic context propagation.

#### Basic Usage

```python
from plc_orchestrator.observability import get_logger, LogContext

# Get a structured logger
logger = get_logger(__name__)

# Log with structured data
logger.info(
    "task_completed",
    task_id="123",
    duration=45.2,
    status="success"
)

# Add context that applies to all logs
with LogContext(user_id="456", session_id="abc"):
    logger.info("Processing user request")
    # All logs within this context will include user_id and session_id
```

#### Correlation IDs

```python
from plc_orchestrator.observability import set_correlation_id

# Set correlation ID for request tracking
set_correlation_id("req-123-456")

# All subsequent logs will include this correlation ID
logger.info("Starting request processing")
```

#### Custom Log Events

```python
# Log API calls
logger.log_api_call(
    method="POST",
    endpoint="/api/v1/tasks",
    status_code=201,
    duration=0.234
)

# Log database operations
logger.log_database_query(
    operation="SELECT",
    table="tasks",
    duration=0.015,
    rows_affected=42
)

# Log task progress
logger.log_task_progress(
    task_id="123",
    status="running",
    progress=0.75
)
```

## Integration with Orchestrator

The orchestrator automatically integrates observability features when enabled.

### Configuration

```python
# In your .env file
ENABLE_OBSERVABILITY=true
METRICS_EXPORT_INTERVAL=60
TRACE_EXPORT_ENDPOINT=http://localhost:14268/api/traces
LOG_FORMAT=json
LOG_LEVEL=INFO
```

### Automatic Instrumentation

When observability is enabled, the orchestrator automatically:

1. **Tracks task metrics**:
   - Task analysis count and duration
   - Validation count, duration, and outcomes
   - Memory operation performance

2. **Creates trace spans**:
   - Task analysis operations
   - Validation processes
   - Memory queries
   - Plugin executions

3. **Logs structured events**:
   - Task lifecycle events
   - Error occurrences
   - Performance milestones

### Example: Full Observability

```python
from plc_orchestrator import create_orchestrator
from plc_orchestrator.observability import configure_metrics, configure_tracing

# Configure observability
configure_metrics([PrometheusExporter()], export_interval=30)
configure_tracing("orchestrator-service", [JaegerExporter("http://localhost:14268")])

# Create orchestrator with observability
orchestrator = create_orchestrator(
    enable_observability=True,
    correlation_id="req-123"
)

# All operations are now automatically instrumented
analysis = orchestrator.analyze_task("Build REST API")
# Metrics: tasks_analyzed counter incremented
# Tracing: Span created for analyze_task
# Logging: Structured log with correlation ID
```

## Dashboards and Visualization

### Prometheus + Grafana

Example Grafana dashboard queries:

```promql
# Task analysis rate
rate(tasks_analyzed_total[5m])

# Average validation duration
rate(validation_duration_sum[5m]) / rate(validation_duration_count[5m])

# Validation success rate
sum(rate(validation_outcomes_total{outcome="passed"}[5m])) /
sum(rate(validation_outcomes_total[5m]))

# Memory operation latency percentiles
histogram_quantile(0.95, rate(memory_operation_duration_bucket[5m]))
```

### Jaeger Tracing

View distributed traces in Jaeger UI:

1. Navigate to http://localhost:16686
2. Select "orchestrator-service"
3. View trace timelines and span details
4. Analyze performance bottlenecks

### ELK Stack

Example Kibana queries:

```json
// Find all errors for a task
{
  "query": {
    "bool": {
      "must": [
        { "term": { "task_id": "123" } },
        { "term": { "level": "error" } }
      ]
    }
  }
}

// Track task progress over time
{
  "query": {
    "term": { "event_type": "task_progress" }
  },
  "aggs": {
    "progress_over_time": {
      "date_histogram": {
        "field": "timestamp",
        "interval": "1m"
      }
    }
  }
}
```

## Performance Impact

Observability features have minimal performance impact:

- **Metrics**: ~0.1ms per operation
- **Tracing**: ~0.5ms per span
- **Logging**: ~0.2ms per log (async in background)

### Optimization Tips

1. **Sampling**: Use trace sampling in production
   ```python
   configure_tracing(
       "orchestrator",
       exporters,
       sampling_rate=0.1  # Sample 10% of traces
   )
   ```

2. **Batch exports**: Configure appropriate export intervals
   ```python
   configure_metrics(exporters, export_interval=60)  # Export every minute
   ```

3. **Selective instrumentation**: Disable for performance-critical paths
   ```python
   # Disable observability for specific operations
   orchestrator = create_orchestrator(enable_observability=False)
   ```

## Troubleshooting

### Common Issues

1. **High memory usage**: Reduce metric cardinality
   ```python
   # Avoid high-cardinality labels
   # Bad: labels={"user_id": user_id}  # Millions of unique values
   # Good: labels={"user_type": user_type}  # Limited set of values
   ```

2. **Missing traces**: Check span propagation
   ```python
   # Ensure context is propagated
   context = SpanContext.from_headers(request.headers)
   with create_span("operation", context=context):
       # ...
   ```

3. **Log volume**: Adjust log levels
   ```python
   # Set appropriate log level
   logger = get_logger(__name__, level="WARNING")
   ```

## Best Practices

1. **Use semantic naming**: Choose descriptive metric and span names
2. **Add context**: Include relevant attributes in spans and logs
3. **Handle errors**: Set appropriate span status on errors
4. **Clean up**: Export metrics and traces before shutdown
5. **Monitor the monitors**: Track observability system health

## Example: Complete Observability Setup

```python
import os
from plc_orchestrator import create_orchestrator
from plc_orchestrator.observability import (
    configure_metrics,
    configure_tracing,
    configure_logging,
    PrometheusExporter,
    JaegerExporter,
)

# Configure all observability features
def setup_observability():
    # Metrics
    configure_metrics(
        exporters=[
            PrometheusExporter(
                push_gateway_url=os.getenv("PROMETHEUS_GATEWAY", "http://localhost:9091")
            )
        ],
        export_interval=30.0
    )
    
    # Tracing
    configure_tracing(
        service_name="orchestrator",
        exporters=[
            JaegerExporter(
                endpoint=os.getenv("JAEGER_ENDPOINT", "http://localhost:14268"),
                service_name="orchestrator"
            )
        ],
        sampling_rate=float(os.getenv("TRACE_SAMPLING_RATE", "0.1"))
    )
    
    # Logging
    configure_logging(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format=os.getenv("LOG_FORMAT", "json"),
        correlation_id=os.getenv("CORRELATION_ID")
    )

# Use orchestrator with full observability
setup_observability()
orchestrator = create_orchestrator(enable_observability=True)

# All operations are now observable
analysis = orchestrator.analyze_task("Implement caching layer")
```
