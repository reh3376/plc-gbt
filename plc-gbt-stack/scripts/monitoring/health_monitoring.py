#!/usr/bin/env python3
"""
Enhanced Health Monitoring System for PLC-GPT
Phase 6: Maintenance & Governance Systems

This module provides comprehensive health monitoring including:
- System component health checks
- Predictive failure detection
- Automated alerting and escalation
- Performance degradation monitoring
- Service availability tracking

Following AI Task Orchestrator methodology for structured monitoring.
"""

import json
import logging
import statistics
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil
import requests
from cache.redis_cache import get_cache

# Import existing infrastructure
from monitoring.enterprise_monitoring import AlertSeverity, get_monitoring

from config.enterprise_settings import EnterpriseSettings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status levels."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"
    DEGRADED = "degraded"


class ComponentType(Enum):
    """System component types."""
    DATABASE = "database"
    CACHE = "cache"
    API_SERVICE = "api_service"
    WORKER_SERVICE = "worker_service"
    STORAGE = "storage"
    NETWORK = "network"
    SYSTEM_RESOURCE = "system_resource"


@dataclass
class HealthMetric:
    """Individual health metric."""
    name: str
    value: float
    unit: str
    threshold_warning: float
    threshold_critical: float
    status: HealthStatus
    message: str
    timestamp: datetime


@dataclass
class ComponentHealth:
    """Health status of a system component."""
    component_id: str
    component_type: ComponentType
    name: str
    status: HealthStatus
    metrics: List[HealthMetric]
    last_check: datetime
    uptime_seconds: float
    error_message: Optional[str] = None
    dependencies: List[str] = None


@dataclass
class HealthAlert:
    """Health monitoring alert."""
    alert_id: str
    component_id: str
    severity: AlertSeverity
    message: str
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    escalated: bool = False


@dataclass
class PredictiveAlert:
    """Predictive failure alert."""
    alert_id: str
    component_id: str
    predicted_failure_time: datetime
    confidence: float
    indicators: List[str]
    recommended_actions: List[str]
    timestamp: datetime


class EnhancedHealthMonitoring:
    """
    Enhanced health monitoring system for PLC-GPT.

    Features:
    - Comprehensive component health checks
    - Predictive failure detection
    - Automated alerting and escalation
    - Performance trend analysis
    - Service dependency tracking
    - Custom health check plugins
    """

    def __init__(self, settings: Optional[EnterpriseSettings] = None):
        """Initialize enhanced health monitoring."""
        self.settings = settings or EnterpriseSettings()
        self.enterprise_monitoring = get_monitoring()
        self.cache = get_cache()

        # Monitoring state
        self.components: Dict[str, ComponentHealth] = {}
        self.health_history: Dict[str, List[HealthMetric]] = {}
        self.active_alerts: Dict[str, HealthAlert] = {}
        self.predictive_alerts: Dict[str, PredictiveAlert] = {}
        self.alert_handlers: Dict[str, Callable] = {}

        # Monitoring configuration
        self.check_interval = 30  # seconds
        self.trend_analysis_window = 300  # 5 minutes
        self.prediction_window = 3600  # 1 hour
        self.is_monitoring = False
        self.monitoring_thread = None

        # Initialize components
        self._initialize_system_components()
        self._register_default_alert_handlers()

        logger.info("Enhanced Health Monitoring initialized")

    def _initialize_system_components(self):
        """Initialize all system components to monitor."""

        # Neo4j Database
        self.components['neo4j'] = ComponentHealth(
            component_id='neo4j',
            component_type=ComponentType.DATABASE,
            name='Neo4j Knowledge Graph',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        # PostgreSQL Database
        self.components['postgres'] = ComponentHealth(
            component_id='postgres',
            component_type=ComponentType.DATABASE,
            name='PostgreSQL Metadata Database',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        # Qdrant Vector Database
        self.components['qdrant'] = ComponentHealth(
            component_id='qdrant',
            component_type=ComponentType.DATABASE,
            name='Qdrant Vector Database',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        # Redis Cache
        self.components['redis'] = ComponentHealth(
            component_id='redis',
            component_type=ComponentType.CACHE,
            name='Redis Cache',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        # Gateway API Service
        self.components['gateway'] = ComponentHealth(
            component_id='gateway',
            component_type=ComponentType.API_SERVICE,
            name='Gateway API Service',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=['neo4j', 'qdrant', 'redis']
        )

        # ETL Worker Service
        self.components['etl_worker'] = ComponentHealth(
            component_id='etl_worker',
            component_type=ComponentType.WORKER_SERVICE,
            name='ETL Worker Service',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=['neo4j', 'qdrant', 'postgres']
        )

        # System Resources
        self.components['system_cpu'] = ComponentHealth(
            component_id='system_cpu',
            component_type=ComponentType.SYSTEM_RESOURCE,
            name='System CPU',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        self.components['system_memory'] = ComponentHealth(
            component_id='system_memory',
            component_type=ComponentType.SYSTEM_RESOURCE,
            name='System Memory',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

        self.components['system_disk'] = ComponentHealth(
            component_id='system_disk',
            component_type=ComponentType.SYSTEM_RESOURCE,
            name='System Disk',
            status=HealthStatus.UNKNOWN,
            metrics=[],
            last_check=datetime.now(),
            uptime_seconds=0.0,
            dependencies=[]
        )

    def _register_default_alert_handlers(self):
        """Register default alert handlers."""

        def log_alert_handler(alert: HealthAlert):
            """Log alert to system logs."""
            logger.warning(f"HEALTH ALERT: {alert.component_id} - {alert.message}")

        def critical_alert_handler(alert: HealthAlert):
            """Handle critical alerts with immediate escalation."""
            if alert.severity == AlertSeverity.CRITICAL:
                logger.critical(f"CRITICAL HEALTH ALERT: {alert.component_id} - {alert.message}")
                # In production, this would send notifications to on-call team

        def predictive_alert_handler(alert: PredictiveAlert):
            """Handle predictive failure alerts."""
            logger.warning(f"PREDICTIVE ALERT: {alert.component_id} predicted failure in {alert.predicted_failure_time}")

        self.alert_handlers['log'] = log_alert_handler
        self.alert_handlers['critical'] = critical_alert_handler
        self.alert_handlers['predictive'] = predictive_alert_handler

    def start_monitoring(self):
        """Start health monitoring."""
        if self.is_monitoring:
            logger.warning("Health monitoring already running")
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()

        logger.info("✅ Enhanced health monitoring started")

    def stop_monitoring(self):
        """Stop health monitoring."""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)

        logger.info("✅ Enhanced health monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                start_time = time.time()

                # Check all components
                for component_id in self.components.keys():
                    self._check_component_health(component_id)

                # Analyze trends and predict failures
                self._analyze_health_trends()

                # Process alerts
                self._process_alerts()

                # Calculate sleep time to maintain interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.check_interval - elapsed)
                time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                time.sleep(self.check_interval)

    def _check_component_health(self, component_id: str):
        """Check health of a specific component."""
        if component_id not in self.components:
            return

        component = self.components[component_id]
        time.time()

        try:
            # Check component based on type
            if component.component_type == ComponentType.DATABASE:
                self._check_database_health(component)
            elif component.component_type == ComponentType.CACHE:
                self._check_cache_health(component)
            elif component.component_type == ComponentType.API_SERVICE:
                self._check_api_service_health(component)
            elif component.component_type == ComponentType.WORKER_SERVICE:
                self._check_worker_service_health(component)
            elif component.component_type == ComponentType.SYSTEM_RESOURCE:
                self._check_system_resource_health(component)

            # Update component status
            component.last_check = datetime.now()

            # Store health metrics history
            if component_id not in self.health_history:
                self.health_history[component_id] = []

            for metric in component.metrics:
                self.health_history[component_id].append(metric)

            # Keep only recent history (last hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            self.health_history[component_id] = [
                m for m in self.health_history[component_id]
                if m.timestamp > cutoff_time
            ]

        except Exception as e:
            logger.error(f"Health check failed for {component_id}: {e}")
            component.status = HealthStatus.UNKNOWN
            component.error_message = str(e)

    def _check_database_health(self, component: ComponentHealth):
        """Check database health."""
        component.metrics = []

        if component.component_id == 'neo4j':
            try:
                # Check Neo4j connectivity and performance
                # This would use actual Neo4j driver in production
                response_time = 0.1  # Simulated
                connection_count = 5  # Simulated

                # Response time metric
                response_metric = HealthMetric(
                    name='response_time',
                    value=response_time,
                    unit='seconds',
                    threshold_warning=1.0,
                    threshold_critical=5.0,
                    status=HealthStatus.HEALTHY if response_time < 1.0 else HealthStatus.WARNING,
                    message=f'Response time: {response_time:.3f}s',
                    timestamp=datetime.now()
                )
                component.metrics.append(response_metric)

                # Connection count metric
                connection_metric = HealthMetric(
                    name='connection_count',
                    value=connection_count,
                    unit='connections',
                    threshold_warning=50,
                    threshold_critical=100,
                    status=HealthStatus.HEALTHY if connection_count < 50 else HealthStatus.WARNING,
                    message=f'Active connections: {connection_count}',
                    timestamp=datetime.now()
                )
                component.metrics.append(connection_metric)

                # Overall status
                component.status = HealthStatus.HEALTHY
                component.uptime_seconds += 30  # Increment uptime

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

        elif component.component_id == 'postgres':
            try:
                # Check PostgreSQL health
                response_time = 0.05  # Simulated
                active_connections = 3  # Simulated

                component.metrics.append(HealthMetric(
                    name='response_time',
                    value=response_time,
                    unit='seconds',
                    threshold_warning=0.5,
                    threshold_critical=2.0,
                    status=HealthStatus.HEALTHY if response_time < 0.5 else HealthStatus.WARNING,
                    message=f'Response time: {response_time:.3f}s',
                    timestamp=datetime.now()
                ))

                component.metrics.append(HealthMetric(
                    name='active_connections',
                    value=active_connections,
                    unit='connections',
                    threshold_warning=20,
                    threshold_critical=50,
                    status=HealthStatus.HEALTHY if active_connections < 20 else HealthStatus.WARNING,
                    message=f'Active connections: {active_connections}',
                    timestamp=datetime.now()
                ))

                component.status = HealthStatus.HEALTHY
                component.uptime_seconds += 30

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

        elif component.component_id == 'qdrant':
            try:
                # Check Qdrant health via HTTP API
                response = requests.get('http://localhost:6333/health', timeout=5)
                response_time = response.elapsed.total_seconds()

                if response.status_code == 200:
                    component.metrics.append(HealthMetric(
                        name='response_time',
                        value=response_time,
                        unit='seconds',
                        threshold_warning=1.0,
                        threshold_critical=5.0,
                        status=HealthStatus.HEALTHY if response_time < 1.0 else HealthStatus.WARNING,
                        message=f'Response time: {response_time:.3f}s',
                        timestamp=datetime.now()
                    ))

                    # Get collections info
                    collections_response = requests.get('http://localhost:6333/collections', timeout=5)
                    if collections_response.status_code == 200:
                        collections_data = collections_response.json()
                        collection_count = len(collections_data.get('result', {}).get('collections', []))

                        component.metrics.append(HealthMetric(
                            name='collection_count',
                            value=collection_count,
                            unit='collections',
                            threshold_warning=0,
                            threshold_critical=0,
                            status=HealthStatus.HEALTHY,
                            message=f'Collections: {collection_count}',
                            timestamp=datetime.now()
                        ))

                    component.status = HealthStatus.HEALTHY
                    component.uptime_seconds += 30
                else:
                    component.status = HealthStatus.CRITICAL
                    component.error_message = f"HTTP {response.status_code}"

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

    def _check_cache_health(self, component: ComponentHealth):
        """Check cache health."""
        if component.component_id == 'redis':
            try:
                # Check Redis health
                health_check = self.cache.health_check()

                if health_check['status'] == 'healthy':
                    # Get cache statistics
                    stats = self.cache.get_stats()

                    component.metrics = [
                        HealthMetric(
                            name='hit_rate',
                            value=stats.get('hit_rate', 0.0),
                            unit='percentage',
                            threshold_warning=70.0,
                            threshold_critical=50.0,
                            status=HealthStatus.HEALTHY if stats.get('hit_rate', 0) > 70 else HealthStatus.WARNING,
                            message=f"Hit rate: {stats.get('hit_rate', 0):.1f}%",
                            timestamp=datetime.now()
                        ),
                        HealthMetric(
                            name='memory_usage',
                            value=stats.get('memory_usage', 0.0),
                            unit='MB',
                            threshold_warning=1000.0,
                            threshold_critical=1500.0,
                            status=HealthStatus.HEALTHY if stats.get('memory_usage', 0) < 1000 else HealthStatus.WARNING,
                            message=f"Memory usage: {stats.get('memory_usage', 0):.1f}MB",
                            timestamp=datetime.now()
                        )
                    ]

                    component.status = HealthStatus.HEALTHY
                    component.uptime_seconds += 30
                else:
                    component.status = HealthStatus.CRITICAL
                    component.error_message = health_check.get('message', 'Redis unhealthy')

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

    def _check_api_service_health(self, component: ComponentHealth):
        """Check API service health."""
        if component.component_id == 'gateway':
            try:
                # Check Gateway API health
                response = requests.get('http://localhost:8000/health', timeout=5)
                response_time = response.elapsed.total_seconds()

                if response.status_code == 200:
                    component.metrics = [
                        HealthMetric(
                            name='response_time',
                            value=response_time,
                            unit='seconds',
                            threshold_warning=1.0,
                            threshold_critical=5.0,
                            status=HealthStatus.HEALTHY if response_time < 1.0 else HealthStatus.WARNING,
                            message=f'Response time: {response_time:.3f}s',
                            timestamp=datetime.now()
                        )
                    ]

                    component.status = HealthStatus.HEALTHY
                    component.uptime_seconds += 30
                else:
                    component.status = HealthStatus.CRITICAL
                    component.error_message = f"HTTP {response.status_code}"

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

    def _check_worker_service_health(self, component: ComponentHealth):
        """Check worker service health."""
        if component.component_id == 'etl_worker':
            try:
                # Check ETL worker health (simplified)
                # In production, this would check actual worker process status
                component.metrics = [
                    HealthMetric(
                        name='queue_size',
                        value=0,  # Simulated
                        unit='jobs',
                        threshold_warning=100,
                        threshold_critical=500,
                        status=HealthStatus.HEALTHY,
                        message='Queue empty',
                        timestamp=datetime.now()
                    )
                ]

                component.status = HealthStatus.HEALTHY
                component.uptime_seconds += 30

            except Exception as e:
                component.status = HealthStatus.CRITICAL
                component.error_message = str(e)

    def _check_system_resource_health(self, component: ComponentHealth):
        """Check system resource health."""
        try:
            if component.component_id == 'system_cpu':
                cpu_percent = psutil.cpu_percent(interval=1)

                component.metrics = [
                    HealthMetric(
                        name='cpu_usage',
                        value=cpu_percent,
                        unit='percentage',
                        threshold_warning=80.0,
                        threshold_critical=95.0,
                        status=HealthStatus.HEALTHY if cpu_percent < 80 else (
                            HealthStatus.WARNING if cpu_percent < 95 else HealthStatus.CRITICAL
                        ),
                        message=f'CPU usage: {cpu_percent:.1f}%',
                        timestamp=datetime.now()
                    )
                ]

                component.status = component.metrics[0].status

            elif component.component_id == 'system_memory':
                memory = psutil.virtual_memory()

                component.metrics = [
                    HealthMetric(
                        name='memory_usage',
                        value=memory.percent,
                        unit='percentage',
                        threshold_warning=85.0,
                        threshold_critical=95.0,
                        status=HealthStatus.HEALTHY if memory.percent < 85 else (
                            HealthStatus.WARNING if memory.percent < 95 else HealthStatus.CRITICAL
                        ),
                        message=f'Memory usage: {memory.percent:.1f}%',
                        timestamp=datetime.now()
                    )
                ]

                component.status = component.metrics[0].status

            elif component.component_id == 'system_disk':
                disk = psutil.disk_usage('/')
                disk_percent = (disk.used / disk.total) * 100

                component.metrics = [
                    HealthMetric(
                        name='disk_usage',
                        value=disk_percent,
                        unit='percentage',
                        threshold_warning=90.0,
                        threshold_critical=95.0,
                        status=HealthStatus.HEALTHY if disk_percent < 90 else (
                            HealthStatus.WARNING if disk_percent < 95 else HealthStatus.CRITICAL
                        ),
                        message=f'Disk usage: {disk_percent:.1f}%',
                        timestamp=datetime.now()
                    )
                ]

                component.status = component.metrics[0].status

            component.uptime_seconds += 30

        except Exception as e:
            component.status = HealthStatus.UNKNOWN
            component.error_message = str(e)

    def _analyze_health_trends(self):
        """Analyze health trends and predict potential failures."""
        for component_id, history in self.health_history.items():
            if len(history) < 10:  # Need sufficient data points
                continue

            try:
                self._analyze_component_trends(component_id, history)
            except Exception as e:
                logger.error(f"Trend analysis failed for {component_id}: {e}")

    def _analyze_component_trends(self, component_id: str, history: List[HealthMetric]):
        """Analyze trends for a specific component."""
        # Group metrics by name
        metric_groups = {}
        for metric in history:
            if metric.name not in metric_groups:
                metric_groups[metric.name] = []
            metric_groups[metric.name].append(metric)

        # Analyze each metric type
        for metric_name, metrics in metric_groups.items():
            if len(metrics) < 10:
                continue

            # Get recent values
            recent_values = [m.value for m in metrics[-10:]]

            # Calculate trend
            trend_slope = self._calculate_trend_slope(recent_values)

            # Check for concerning trends
            latest_metric = metrics[-1]

            # Predict failure if trend is concerning
            if self._is_concerning_trend(latest_metric, trend_slope):
                self._create_predictive_alert(component_id, metric_name, latest_metric, trend_slope)

    def _calculate_trend_slope(self, values: List[float]) -> float:
        """Calculate trend slope using linear regression."""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))

        # Calculate slope using least squares
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _is_concerning_trend(self, metric: HealthMetric, slope: float) -> bool:
        """Check if trend is concerning and might lead to failure."""
        # Check if trending towards critical threshold
        if slope > 0:  # Increasing trend
            # Calculate time to critical threshold
            if slope > 0.01:  # Significant slope
                time_to_critical = (metric.threshold_critical - metric.value) / slope
                if 0 < time_to_critical < 120:  # Within 2 hours
                    return True

        return False

    def _create_predictive_alert(
        self,
        component_id: str,
        metric_name: str,
        metric: HealthMetric,
        slope: float
    ):
        """Create predictive failure alert."""
        alert_id = f"predictive_{component_id}_{metric_name}_{int(time.time())}"

        # Calculate predicted failure time
        time_to_failure = (metric.threshold_critical - metric.value) / slope
        predicted_time = datetime.now() + timedelta(minutes=time_to_failure)

        # Calculate confidence based on trend consistency
        confidence = min(0.95, abs(slope) * 100)  # Simplified confidence calculation

        alert = PredictiveAlert(
            alert_id=alert_id,
            component_id=component_id,
            predicted_failure_time=predicted_time,
            confidence=confidence,
            indicators=[f"{metric_name} trending towards critical threshold"],
            recommended_actions=[
                f"Monitor {component_id} {metric_name} closely",
                f"Consider scaling or optimization for {component_id}",
                "Review recent system changes"
            ],
            timestamp=datetime.now()
        )

        self.predictive_alerts[alert_id] = alert

        # Trigger alert handlers
        for handler in self.alert_handlers.values():
            if hasattr(handler, '__name__') and 'predictive' in handler.__name__:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Predictive alert handler failed: {e}")

        logger.warning(f"Predictive alert created: {component_id} {metric_name} failure predicted")

    def _process_alerts(self):
        """Process health alerts and escalations."""
        datetime.now()

        # Check for new alerts
        for component_id, component in self.components.items():
            if component.status in [HealthStatus.WARNING, HealthStatus.CRITICAL]:
                # Check if alert already exists
                existing_alert = None
                for alert in self.active_alerts.values():
                    if alert.component_id == component_id and not alert.resolved:
                        existing_alert = alert
                        break

                if not existing_alert:
                    # Create new alert
                    self._create_health_alert(component)

            elif component.status == HealthStatus.HEALTHY:
                # Resolve any active alerts for this component
                self._resolve_component_alerts(component_id)

        # Check for alert escalations
        self._check_alert_escalations()

    def _create_health_alert(self, component: ComponentHealth):
        """Create health alert for component."""
        alert_id = f"health_{component.component_id}_{int(time.time())}"

        severity = AlertSeverity.HIGH if component.status == HealthStatus.CRITICAL else AlertSeverity.MEDIUM

        message = f"{component.name} is {component.status.value}"
        if component.error_message:
            message += f": {component.error_message}"

        alert = HealthAlert(
            alert_id=alert_id,
            component_id=component.component_id,
            severity=severity,
            message=message,
            timestamp=datetime.now()
        )

        self.active_alerts[alert_id] = alert

        # Trigger alert handlers
        for handler in self.alert_handlers.values():
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

        logger.warning(f"Health alert created: {message}")

    def _resolve_component_alerts(self, component_id: str):
        """Resolve all active alerts for a component."""
        for _alert_id, alert in list(self.active_alerts.items()):
            if alert.component_id == component_id and not alert.resolved:
                alert.resolved = True
                alert.resolved_at = datetime.now()
                logger.info(f"Health alert resolved: {alert.message}")

    def _check_alert_escalations(self):
        """Check for alerts that need escalation."""
        escalation_threshold = timedelta(minutes=15)  # Escalate after 15 minutes

        for alert in self.active_alerts.values():
            if (not alert.resolved and
                not alert.escalated and
                alert.severity == AlertSeverity.HIGH and
                datetime.now() - alert.timestamp > escalation_threshold):

                self._escalate_alert(alert)

    def _escalate_alert(self, alert: HealthAlert):
        """Escalate alert to higher severity."""
        alert.escalated = True
        alert.severity = AlertSeverity.CRITICAL

        # Trigger critical alert handlers
        for handler in self.alert_handlers.values():
            if hasattr(handler, '__name__') and 'critical' in handler.__name__:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Critical alert handler failed: {e}")

        logger.critical(f"Alert escalated to CRITICAL: {alert.message}")

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary."""
        total_components = len(self.components)
        healthy_count = len([c for c in self.components.values() if c.status == HealthStatus.HEALTHY])
        warning_count = len([c for c in self.components.values() if c.status == HealthStatus.WARNING])
        critical_count = len([c for c in self.components.values() if c.status == HealthStatus.CRITICAL])
        unknown_count = len([c for c in self.components.values() if c.status == HealthStatus.UNKNOWN])

        # Determine overall status
        if critical_count > 0:
            overall_status = HealthStatus.CRITICAL
        elif warning_count > 0:
            overall_status = HealthStatus.WARNING
        elif unknown_count > 0:
            overall_status = HealthStatus.UNKNOWN
        else:
            overall_status = HealthStatus.HEALTHY

        return {
            'overall_status': overall_status.value,
            'total_components': total_components,
            'healthy': healthy_count,
            'warning': warning_count,
            'critical': critical_count,
            'unknown': unknown_count,
            'health_percentage': (healthy_count / total_components * 100) if total_components > 0 else 0,
            'active_alerts': len([a for a in self.active_alerts.values() if not a.resolved]),
            'predictive_alerts': len(self.predictive_alerts),
            'last_check': max([c.last_check for c in self.components.values()], default=None)
        }

    def get_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """Get health status of specific component."""
        return self.components.get(component_id)

    def get_active_alerts(self) -> List[HealthAlert]:
        """Get all active (unresolved) alerts."""
        return [alert for alert in self.active_alerts.values() if not alert.resolved]

    def get_predictive_alerts(self) -> List[PredictiveAlert]:
        """Get all predictive alerts."""
        return list(self.predictive_alerts.values())

    def force_health_check(self, component_id: Optional[str] = None):
        """Force immediate health check for component(s)."""
        if component_id:
            if component_id in self.components:
                self._check_component_health(component_id)
                logger.info(f"Forced health check completed for {component_id}")
            else:
                raise ValueError(f"Unknown component: {component_id}")
        else:
            # Check all components
            for comp_id in self.components.keys():
                self._check_component_health(comp_id)
            logger.info("Forced health check completed for all components")

    def register_alert_handler(self, name: str, handler: Callable):
        """Register custom alert handler."""
        self.alert_handlers[name] = handler
        logger.info(f"Alert handler registered: {name}")

    def cleanup(self):
        """Clean up monitoring resources."""
        self.stop_monitoring()


# Global health monitoring instance
health_monitoring = None


def get_health_monitoring(settings=None) -> EnhancedHealthMonitoring:
    """Get or create health monitoring instance."""
    global health_monitoring
    if health_monitoring is None:
        health_monitoring = EnhancedHealthMonitoring(settings)
    return health_monitoring


def main():
    """Main function for standalone execution."""
    import argparse

    parser = argparse.ArgumentParser(description='PLC-GPT Enhanced Health Monitoring')
    parser.add_argument('--start', action='store_true', help='Start health monitoring')
    parser.add_argument('--stop', action='store_true', help='Stop health monitoring')
    parser.add_argument('--status', action='store_true', help='Show health status')
    parser.add_argument('--check', type=str, help='Force health check for component')
    parser.add_argument('--alerts', action='store_true', help='Show active alerts')
    parser.add_argument('--predictive', action='store_true', help='Show predictive alerts')

    args = parser.parse_args()

    monitoring = get_health_monitoring()

    try:
        if args.start:
            monitoring.start_monitoring()
            print("✅ Health monitoring started")

            # Keep running
            import signal
            def signal_handler(sig, frame):
                print("\n🛑 Stopping health monitoring...")
                monitoring.stop_monitoring()
                exit(0)

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            print("Press Ctrl+C to stop...")
            while monitoring.is_monitoring:
                time.sleep(1)

        elif args.stop:
            monitoring.stop_monitoring()
            print("✅ Health monitoring stopped")

        elif args.status:
            summary = monitoring.get_system_health_summary()
            print(json.dumps(summary, indent=2, default=str))

        elif args.check:
            monitoring.force_health_check(args.check)
            component = monitoring.get_component_health(args.check)
            if component:
                print(f"Component: {component.name}")
                print(f"Status: {component.status.value}")
                for metric in component.metrics:
                    print(f"  {metric.name}: {metric.value} {metric.unit} ({metric.status.value})")

        elif args.alerts:
            alerts = monitoring.get_active_alerts()
            print(f"Active alerts ({len(alerts)}):")
            for alert in alerts:
                print(f"  {alert.component_id}: {alert.message} ({alert.severity.value})")

        elif args.predictive:
            alerts = monitoring.get_predictive_alerts()
            print(f"Predictive alerts ({len(alerts)}):")
            for alert in alerts:
                print(f"  {alert.component_id}: Failure predicted at {alert.predicted_failure_time}")
                print(f"    Confidence: {alert.confidence:.1%}")

        else:
            parser.print_help()

    finally:
        monitoring.cleanup()


if __name__ == "__main__":
    main()
