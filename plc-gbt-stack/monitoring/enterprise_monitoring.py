#!/usr/bin/env python3
"""
Enhanced Monitoring System for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

import psutil
import redis
from auth.rbac import Role
from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram
from prometheus_client.exposition import generate_latest

from config.enterprise_settings import EnterpriseSettings


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Metric types for monitoring."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class MetricData:
    """Metric data structure."""
    name: str
    value: float
    timestamp: datetime
    labels: Dict[str, str]
    metric_type: MetricType
    description: str = ""
    unit: str = ""


@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    name: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None


@dataclass
class PerformanceMetrics:
    """System performance metrics."""
    cpu_usage_percent: float
    memory_usage_percent: float
    disk_usage_percent: float
    network_io_bytes_sent: int
    network_io_bytes_recv: int
    active_connections: int
    request_count: int
    error_count: int
    avg_response_time: float
    cache_hit_rate: float
    database_connections: int
    queue_size: int


class EnterpriseMonitoring:
    """
    Comprehensive monitoring system with metrics collection,
    alerting, and integration with existing monitoring infrastructure.
    """

    def __init__(self, settings: EnterpriseSettings):
        self.settings = settings
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

        # Prometheus metrics
        self.registry = CollectorRegistry()
        self._setup_prometheus_metrics()

        # Metrics storage
        self.metrics_buffer = []
        self.alerts = []
        self.alert_handlers = {}

        # Performance tracking
        self.performance_metrics = PerformanceMetrics(
            cpu_usage_percent=0.0,
            memory_usage_percent=0.0,
            disk_usage_percent=0.0,
            network_io_bytes_sent=0,
            network_io_bytes_recv=0,
            active_connections=0,
            request_count=0,
            error_count=0,
            avg_response_time=0.0,
            cache_hit_rate=0.0,
            database_connections=0,
            queue_size=0
        )

        # Thresholds for alerts
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'error_rate': 5.0,
            'response_time': 2.0,
            'cache_hit_rate': 70.0,
            'database_connections': 100,
            'queue_size': 1000,
            'neo4j_orphaned_nodes': 10
        }

        # Monitoring intervals
        self.collection_interval = 60  # seconds
        self.alert_check_interval = 30  # seconds

        self.logger = logging.getLogger(__name__)
        self.is_running = False

        # Initialize monitoring tasks
        self._monitoring_tasks = []

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        # Request metrics
        self.request_count = Counter(
            'plc_gpt_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status_code', 'user_role'],
            registry=self.registry
        )

        self.request_duration = Histogram(
            'plc_gpt_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint', 'user_role'],
            registry=self.registry
        )

        # Authentication metrics
        self.auth_attempts = Counter(
            'plc_gpt_auth_attempts_total',
            'Total authentication attempts',
            ['result', 'method'],
            registry=self.registry
        )

        self.active_sessions = Gauge(
            'plc_gpt_active_sessions',
            'Number of active user sessions',
            ['user_role'],
            registry=self.registry
        )

        # Cache metrics
        self.cache_operations = Counter(
            'plc_gpt_cache_operations_total',
            'Total cache operations',
            ['operation', 'result'],
            registry=self.registry
        )

        self.cache_hit_rate = Gauge(
            'plc_gpt_cache_hit_rate',
            'Cache hit rate percentage',
            registry=self.registry
        )

        # Database metrics
        self.database_connections = Gauge(
            'plc_gpt_database_connections',
            'Active database connections',
            ['database'],
            registry=self.registry
        )

        self.query_duration = Histogram(
            'plc_gpt_query_duration_seconds',
            'Database query duration in seconds',
            ['database', 'operation'],
            registry=self.registry
        )

        # System metrics
        self.system_cpu_usage = Gauge(
            'plc_gpt_system_cpu_usage_percent',
            'System CPU usage percentage',
            registry=self.registry
        )

        self.system_memory_usage = Gauge(
            'plc_gpt_system_memory_usage_percent',
            'System memory usage percentage',
            registry=self.registry
        )

        self.system_disk_usage = Gauge(
            'plc_gpt_system_disk_usage_percent',
            'System disk usage percentage',
            registry=self.registry
        )

        # Rate limiting metrics
        self.rate_limit_hits = Counter(
            'plc_gpt_rate_limit_hits_total',
            'Total rate limit hits',
            ['user_role', 'limit_type'],
            registry=self.registry
        )

        # Error metrics
        self.error_count = Counter(
            'plc_gpt_errors_total',
            'Total errors',
            ['error_type', 'component'],
            registry=self.registry
        )

        # Business metrics
        self.file_uploads = Counter(
            'plc_gpt_file_uploads_total',
            'Total file uploads',
            ['file_type', 'user_role'],
            registry=self.registry
        )

        self.data_processed = Counter(
            'plc_gpt_data_processed_bytes',
            'Total data processed in bytes',
            ['operation', 'user_role'],
            registry=self.registry
        )

    def start_monitoring(self):
        """Start the monitoring system."""
        if self.is_running:
            return

        self.is_running = True
        self.logger.info("Starting enterprise monitoring system")

        # Start monitoring tasks
        self._monitoring_tasks = [
            asyncio.create_task(self._collect_system_metrics()),
            asyncio.create_task(self._collect_application_metrics()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._flush_metrics())
        ]

    def stop_monitoring(self):
        """Stop the monitoring system."""
        if not self.is_running:
            return

        self.is_running = False
        self.logger.info("Stopping enterprise monitoring system")

        # Cancel monitoring tasks
        for task in self._monitoring_tasks:
            task.cancel()

        self._monitoring_tasks = []

    async def _collect_system_metrics(self):
        """Collect system-level metrics."""
        while self.is_running:
            try:
                # CPU usage
                cpu_percent = psutil.cpu_percent(interval=1)
                self.system_cpu_usage.set(cpu_percent)
                self.performance_metrics.cpu_usage_percent = cpu_percent

                # Memory usage
                memory = psutil.virtual_memory()
                memory_percent = memory.percent
                self.system_memory_usage.set(memory_percent)
                self.performance_metrics.memory_usage_percent = memory_percent

                # Disk usage
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100
                self.system_disk_usage.set(disk_percent)
                self.performance_metrics.disk_usage_percent = disk_percent

                # Network I/O
                net_io = psutil.net_io_counters()
                self.performance_metrics.network_io_bytes_sent = net_io.bytes_sent
                self.performance_metrics.network_io_bytes_recv = net_io.bytes_recv

                # Store metrics
                self._store_metric('system_cpu_usage', cpu_percent)
                self._store_metric('system_memory_usage', memory_percent)
                self._store_metric('system_disk_usage', disk_percent)

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"Error collecting system metrics: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _collect_application_metrics(self):
        """Collect application-specific metrics."""
        while self.is_running:
            try:
                # Cache metrics
                cache_stats = self._get_cache_stats()
                if cache_stats:
                    hit_rate = cache_stats.get('hit_rate', 0)
                    if isinstance(hit_rate, str):
                        hit_rate = float(hit_rate.rstrip('%'))

                    self.cache_hit_rate.set(hit_rate)
                    self.performance_metrics.cache_hit_rate = hit_rate

                    # Cache operations
                    self.cache_operations.labels(
                        operation='hit',
                        result='success'
                    ).inc(cache_stats.get('hits', 0))

                    self.cache_operations.labels(
                        operation='miss',
                        result='success'
                    ).inc(cache_stats.get('misses', 0))

                # Database metrics
                db_stats = self._get_database_stats()
                if db_stats:
                    for db_name, stats in db_stats.items():
                        self.database_connections.labels(database=db_name).set(
                            stats.get('active_connections', 0)
                        )

                # Rate limiting metrics
                rate_limit_stats = self._get_rate_limit_stats()
                if rate_limit_stats:
                    for event in rate_limit_stats.get('rate_limit_events', []):
                        self.rate_limit_hits.labels(
                            user_role=event.get('user_role', 'unknown'),
                            limit_type=event.get('limit_type', 'unknown')
                        ).inc()

                await asyncio.sleep(self.collection_interval)

            except Exception as e:
                self.logger.error(f"Error collecting application metrics: {e}")
                await asyncio.sleep(self.collection_interval)

    async def _check_alerts(self):
        """Check for alert conditions."""
        while self.is_running:
            try:
                # Check system alerts
                self._check_system_alerts()

                # Check application alerts
                self._check_application_alerts()

                # Check business alerts
                self._check_business_alerts()

                await asyncio.sleep(self.alert_check_interval)

            except Exception as e:
                self.logger.error(f"Error checking alerts: {e}")
                await asyncio.sleep(self.alert_check_interval)

    async def _flush_metrics(self):
        """Flush metrics to storage."""
        while self.is_running:
            try:
                if self.metrics_buffer:
                    # Store metrics in Redis
                    metrics_data = [asdict(metric) for metric in self.metrics_buffer]

                    # Store with timestamp-based key
                    key = f"metrics:{datetime.utcnow().strftime('%Y%m%d%H%M')}"
                    self.redis_client.lpush(key, *[json.dumps(metric) for metric in metrics_data])
                    self.redis_client.expire(key, 604800)  # Keep for 7 days

                    # Clear buffer
                    self.metrics_buffer = []

                await asyncio.sleep(60)  # Flush every minute

            except Exception as e:
                self.logger.error(f"Error flushing metrics: {e}")
                await asyncio.sleep(60)

    def _check_system_alerts(self):
        """Check system-level alerts."""
        # CPU usage alert
        if self.performance_metrics.cpu_usage_percent > self.alert_thresholds['cpu_usage']:
            self._create_alert(
                'high_cpu_usage',
                AlertSeverity.HIGH,
                f"High CPU usage: {self.performance_metrics.cpu_usage_percent:.1f}%",
                'system',
                {'cpu_usage': self.performance_metrics.cpu_usage_percent}
            )

        # Memory usage alert
        if self.performance_metrics.memory_usage_percent > self.alert_thresholds['memory_usage']:
            self._create_alert(
                'high_memory_usage',
                AlertSeverity.HIGH,
                f"High memory usage: {self.performance_metrics.memory_usage_percent:.1f}%",
                'system',
                {'memory_usage': self.performance_metrics.memory_usage_percent}
            )

        # Disk usage alert
        if self.performance_metrics.disk_usage_percent > self.alert_thresholds['disk_usage']:
            self._create_alert(
                'high_disk_usage',
                AlertSeverity.CRITICAL,
                f"High disk usage: {self.performance_metrics.disk_usage_percent:.1f}%",
                'system',
                {'disk_usage': self.performance_metrics.disk_usage_percent}
            )

    def _check_application_alerts(self):
        """Check application-specific alerts."""
        # Cache hit rate alert
        if self.performance_metrics.cache_hit_rate < self.alert_thresholds['cache_hit_rate']:
            self._create_alert(
                'low_cache_hit_rate',
                AlertSeverity.MEDIUM,
                f"Low cache hit rate: {self.performance_metrics.cache_hit_rate:.1f}%",
                'cache',
                {'cache_hit_rate': self.performance_metrics.cache_hit_rate}
            )

        # Response time alert
        if self.performance_metrics.avg_response_time > self.alert_thresholds['response_time']:
            self._create_alert(
                'high_response_time',
                AlertSeverity.HIGH,
                f"High response time: {self.performance_metrics.avg_response_time:.2f}s",
                'application',
                {'avg_response_time': self.performance_metrics.avg_response_time}
            )

        # Neo4j orphaned nodes alert
        orphaned_nodes_count = self._get_neo4j_orphaned_nodes_count()
        if orphaned_nodes_count > self.alert_thresholds['neo4j_orphaned_nodes']:
            self._create_alert(
                'neo4j_orphaned_nodes_exceeded',
                AlertSeverity.HIGH,
                f"Neo4j orphaned nodes exceeded threshold: {orphaned_nodes_count} > {self.alert_thresholds['neo4j_orphaned_nodes']}",
                'neo4j',
                {'orphaned_nodes_count': orphaned_nodes_count, 'threshold': self.alert_thresholds['neo4j_orphaned_nodes']}
            )

    def _check_business_alerts(self):
        """Check business-specific alerts."""
        # Error rate alert
        if self.performance_metrics.request_count > 0:
            error_rate = (self.performance_metrics.error_count / self.performance_metrics.request_count) * 100
            if error_rate > self.alert_thresholds['error_rate']:
                self._create_alert(
                    'high_error_rate',
                    AlertSeverity.HIGH,
                    f"High error rate: {error_rate:.1f}%",
                    'application',
                    {'error_rate': error_rate}
                )

    def _create_alert(self, name: str, severity: AlertSeverity, message: str,
                     source: str, metadata: Dict[str, Any]):
        """Create a new alert."""
        alert = Alert(
            alert_id=f"{name}_{int(time.time())}",
            name=name,
            severity=severity,
            message=message,
            timestamp=datetime.utcnow(),
            source=source,
            metadata=metadata
        )

        self.alerts.append(alert)
        self.logger.warning(f"Alert created: {alert.name} - {alert.message}")

        # Store alert in Redis
        alert_key = f"alert:{alert.alert_id}"
        self.redis_client.hset(alert_key, mapping=asdict(alert))
        self.redis_client.expire(alert_key, 604800)  # Keep for 7 days

        # Trigger alert handlers
        self._trigger_alert_handlers(alert)

    def _trigger_alert_handlers(self, alert: Alert):
        """Trigger registered alert handlers."""
        for handler_name, handler in self.alert_handlers.items():
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Error in alert handler {handler_name}: {e}")

    def _store_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Store a metric in the buffer."""
        metric = MetricData(
            name=name,
            value=value,
            timestamp=datetime.utcnow(),
            labels=labels or {},
            metric_type=MetricType.GAUGE
        )
        self.metrics_buffer.append(metric)

    def _get_cache_stats(self) -> Optional[Dict[str, Any]]:
        """Get cache statistics."""
        try:
            from cache.redis_cache import get_cache
            cache = get_cache()
            return cache.get_stats()
        except Exception as e:
            self.logger.error(f"Error getting cache stats: {e}")
            return None

    def _get_database_stats(self) -> Optional[Dict[str, Any]]:
        """Get database statistics."""
        try:
            # This would integrate with your database monitoring
            return {
                'postgres': {'active_connections': 5},
                'neo4j': {'active_connections': 3}
            }
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return None

    def _get_rate_limit_stats(self) -> Optional[Dict[str, Any]]:
        """Get rate limiting statistics."""
        try:
            from middleware.rate_limiter import get_rate_limiter
            limiter = get_rate_limiter()
            return limiter.get_rate_limit_stats()
        except Exception as e:
            self.logger.error(f"Error getting rate limit stats: {e}")
            return None

    def _get_neo4j_orphaned_nodes_count(self) -> int:
        """Get the count of orphaned nodes in Neo4j."""
        try:
            from neo4j.graph_db import get_graph_db
            graph_db = get_graph_db()
            return graph_db.get_orphaned_nodes_count()
        except Exception as e:
            self.logger.error(f"Error getting Neo4j orphaned nodes count: {e}")
            return 0

    # Public API methods
    def record_request(self, method: str, endpoint: str, status_code: int,
                      duration: float, user_role: Role):
        """Record a request metric."""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code),
            user_role=user_role.value
        ).inc()

        self.request_duration.labels(
            method=method,
            endpoint=endpoint,
            user_role=user_role.value
        ).observe(duration)

        # Update performance metrics
        self.performance_metrics.request_count += 1
        if status_code >= 400:
            self.performance_metrics.error_count += 1

    def record_auth_attempt(self, result: str, method: str):
        """Record an authentication attempt."""
        self.auth_attempts.labels(result=result, method=method).inc()

    def record_cache_operation(self, operation: str, result: str):
        """Record a cache operation."""
        self.cache_operations.labels(operation=operation, result=result).inc()

    def record_database_query(self, database: str, operation: str, duration: float):
        """Record a database query."""
        self.query_duration.labels(database=database, operation=operation).observe(duration)

    def record_file_upload(self, file_type: str, user_role: Role):
        """Record a file upload."""
        self.file_uploads.labels(file_type=file_type, user_role=user_role.value).inc()

    def record_data_processed(self, operation: str, bytes_processed: int, user_role: Role):
        """Record data processing."""
        self.data_processed.labels(operation=operation, user_role=user_role.value).inc(bytes_processed)

    def record_error(self, error_type: str, component: str):
        """Record an error."""
        self.error_count.labels(error_type=error_type, component=component).inc()

    def update_active_sessions(self, user_role: Role, count: int):
        """Update active sessions count."""
        self.active_sessions.labels(user_role=user_role.value).set(count)

    def register_alert_handler(self, name: str, handler: Callable[[Alert], None]):
        """Register an alert handler."""
        self.alert_handlers[name] = handler

    def get_metrics(self) -> str:
        """Get Prometheus metrics."""
        return generate_latest(self.registry).decode('utf-8')

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return asdict(self.performance_metrics)

    def get_alerts(self, severity: Optional[AlertSeverity] = None,
                  resolved: bool = False) -> List[Alert]:
        """Get alerts with optional filtering."""
        alerts = self.alerts

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if not resolved:
            alerts = [a for a in alerts if not a.resolved]

        return alerts

    def resolve_alert(self, alert_id: str, resolved_by: str) -> bool:
        """Resolve an alert."""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                alert.resolved_by = resolved_by

                # Update in Redis
                alert_key = f"alert:{alert_id}"
                self.redis_client.hset(alert_key, mapping=asdict(alert))

                return True

        return False

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for monitoring UI."""
        return {
            'performance_metrics': self.get_performance_metrics(),
            'recent_alerts': self.get_alerts()[:10],
            'system_health': {
                'cpu_usage': self.performance_metrics.cpu_usage_percent,
                'memory_usage': self.performance_metrics.memory_usage_percent,
                'disk_usage': self.performance_metrics.disk_usage_percent,
                'cache_hit_rate': self.performance_metrics.cache_hit_rate
            },
            'request_metrics': {
                'total_requests': self.performance_metrics.request_count,
                'error_count': self.performance_metrics.error_count,
                'avg_response_time': self.performance_metrics.avg_response_time
            }
        }


# Global monitoring instance
monitoring = None


def get_monitoring() -> EnterpriseMonitoring:
    """Get the global monitoring instance."""
    global monitoring
    if monitoring is None:
        settings = EnterpriseSettings()
        monitoring = EnterpriseMonitoring(settings)
    return monitoring


# Monitoring decorators
def monitor_performance(operation: str = None):
    """Decorator to monitor function performance."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Record successful operation
                monitoring_instance = get_monitoring()
                monitoring_instance._store_metric(
                    f"{operation or func.__name__}_duration",
                    duration,
                    {'status': 'success'}
                )

                return result

            except Exception as e:
                duration = time.time() - start_time

                # Record failed operation
                monitoring_instance = get_monitoring()
                monitoring_instance._store_metric(
                    f"{operation or func.__name__}_duration",
                    duration,
                    {'status': 'error'}
                )

                monitoring_instance.record_error(
                    error_type=type(e).__name__,
                    component=func.__module__
                )

                raise

        return wrapper
    return decorator


def monitor_database_query(database: str, operation: str):
    """Decorator to monitor database queries."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                monitoring_instance = get_monitoring()
                monitoring_instance.record_database_query(database, operation, duration)

                return result

            except Exception:
                duration = time.time() - start_time

                monitoring_instance = get_monitoring()
                monitoring_instance.record_database_query(database, f"{operation}_error", duration)

                raise

        return wrapper
    return decorator


# Health check functions
def health_check_redis() -> Dict[str, Any]:
    """Health check for Redis."""
    try:
        from cache.redis_cache import get_cache
        cache = get_cache()
        return cache.health_check()
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


def health_check_database() -> Dict[str, Any]:
    """Health check for databases."""
    try:
        # This would implement actual database health checks
        return {
            'status': 'healthy',
            'databases': {
                'postgres': 'connected',
                'neo4j': 'connected'
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }


def comprehensive_health_check() -> Dict[str, Any]:
    """Comprehensive system health check."""
    return {
        'system': {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        },
        'redis': health_check_redis(),
        'database': health_check_database(),
        'timestamp': datetime.utcnow().isoformat()
    }
