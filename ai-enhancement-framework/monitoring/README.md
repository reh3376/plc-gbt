# AI Enhancement Framework - Monitoring Framework

## 📋 Overview

The Monitoring Framework provides comprehensive health monitoring, performance tracking, and alerting capabilities for all AI Enhancement Framework services. It ensures system reliability, early issue detection, and optimal performance through real-time monitoring and automated response mechanisms.

## 🏗️ Architecture

### Core Components

#### 1. Health Check Monitor (`health_check.py`)
- **Purpose**: Comprehensive service health monitoring
- **Features**:
  - Multi-service health verification (Redis, Neo4j, PostgreSQL, Qdrant, Framework API)
  - Real-time performance metrics collection
  - Automated alerting and notification
  - Historical health data tracking
  - Continuous monitoring capabilities

#### 2. Performance Metrics Collector
- **Purpose**: System performance tracking and analysis
- **Metrics**:
  - Response time monitoring
  - Memory usage tracking
  - CPU utilization analysis
  - Database connection pool status
  - Network latency measurements

#### 3. Alert Manager
- **Purpose**: Intelligent alerting and notification system
- **Capabilities**:
  - Threshold-based alerting
  - Escalation policies
  - Multiple notification channels
  - Alert aggregation and filtering
  - Incident management integration

## 🚀 Quick Start

### Basic Health Check
```bash
# Single comprehensive health check
python monitoring/health_check.py

# Quiet mode (minimal output)
python monitoring/health_check.py --quiet

# Save report to file
python monitoring/health_check.py --output health_report.json
```

### Continuous Monitoring
```bash
# Monitor every 60 seconds
python monitoring/health_check.py --continuous 60

# Monitor with performance testing
python monitoring/health_check.py --continuous 30 --performance

# Background monitoring with logging
nohup python monitoring/health_check.py --continuous 60 --quiet > monitor.log 2>&1 &
```

### Advanced Configuration
```bash
# Use custom configuration
python monitoring/health_check.py --config config/monitoring.json

# Monitor specific services only
python monitoring/health_check.py --services redis,postgresql

# High-frequency monitoring for debugging
python monitoring/health_check.py --continuous 5 --debug
```

## ⚙️ Configuration

### Default Configuration
The health monitor uses the following default configuration:

```python
{
    'redis': {
        'url': 'redis://localhost:6379',
        'timeout': 5.0
    },
    'neo4j': {
        'uri': 'bolt://localhost:7687',
        'auth': ('neo4j', 'ai_framework_password'),
        'timeout': 10.0
    },
    'postgresql': {
        'host': 'localhost',
        'port': 5432,
        'database': 'ai_framework',
        'user': 'ai_framework_user',
        'password': 'ai_framework_password',
        'timeout': 10.0
    },
    'qdrant': {
        'url': 'http://localhost:6333',
        'timeout': 10.0
    },
    'framework_api': {
        'url': 'http://localhost:8000',
        'timeout': 15.0
    },
    'thresholds': {
        'response_time_warning': 1000,  # ms
        'response_time_critical': 5000,  # ms
        'error_rate_warning': 5,  # %
        'error_rate_critical': 15  # %
    }
}
```

### Custom Configuration File
Create a custom configuration file for your environment:

```json
{
    "redis": {
        "url": "redis://your-redis-host:6379",
        "timeout": 3.0
    },
    "thresholds": {
        "response_time_warning": 500,
        "response_time_critical": 2000
    },
    "notifications": {
        "email": {
            "enabled": true,
            "smtp_server": "smtp.example.com",
            "recipients": ["admin@example.com"]
        },
        "slack": {
            "enabled": true,
            "webhook_url": "https://hooks.slack.com/services/..."
        }
    }
}
```

## 📊 Health Check Services

### Redis Health Check
- **Connection Test**: Basic ping verification
- **Performance Test**: Read/write operations
- **Metrics Collected**:
  - Response time
  - Memory usage
  - Connected clients
  - Keyspace hit/miss ratio
  - Uptime information

### Neo4j Health Check
- **Connection Test**: Cypher query execution
- **Database Info**: Component and version verification
- **Metrics Collected**:
  - Query response time
  - Database components
  - Connection status
  - Transaction information

### PostgreSQL Health Check
- **Connection Test**: Database connectivity verification
- **Statistics**: Database size and connection info
- **Metrics Collected**:
  - Query response time
  - Database size
  - Active connections
  - Connection pool status

### Qdrant Health Check
- **Connection Test**: Vector database connectivity
- **Collection Info**: Available collections and status
- **Metrics Collected**:
  - API response time
  - Cluster information
  - Collection statistics
  - Storage metrics

### Framework API Health Check
- **Endpoint Test**: Health and info endpoints
- **Service Status**: Application health verification
- **Metrics Collected**:
  - API response time
  - Service availability
  - Application metrics
  - Error rates

## 🔔 Alerting and Notifications

### Health Status Levels
- **Healthy**: All systems operational (Green)
- **Degraded**: Some performance issues detected (Yellow)
- **Unhealthy**: Critical issues requiring attention (Red)
- **Unknown**: Unable to determine status (Gray)

### Alert Thresholds
- **Response Time Warning**: >1000ms
- **Response Time Critical**: >5000ms
- **Error Rate Warning**: >5%
- **Error Rate Critical**: >15%
- **Service Downtime**: >30 seconds

### Notification Channels
- **Console Output**: Real-time status display
- **Log Files**: Structured logging for analysis
- **JSON Reports**: Machine-readable status reports
- **Email Alerts**: Critical issue notifications
- **Slack Integration**: Team communication
- **Webhook Support**: Custom integrations

## 📈 Performance Monitoring

### Metrics Collection
The monitoring framework collects comprehensive performance metrics:

#### System Metrics
- **CPU Usage**: Per-service CPU utilization
- **Memory Usage**: RAM consumption patterns
- **Disk I/O**: Storage operation performance
- **Network I/O**: Inter-service communication metrics

#### Application Metrics
- **Response Times**: Service latency measurements
- **Throughput**: Request processing rates
- **Error Rates**: Failure percentages
- **Queue Depths**: Pending operation counts

#### Database Metrics
- **Connection Pools**: Active and idle connections
- **Query Performance**: Execution time analysis
- **Cache Hit Rates**: Memory efficiency metrics
- **Storage Utilization**: Disk space usage

### Performance Analysis
```python
# Example: Analyze performance trends
from monitoring.health_check import HealthMonitor
import asyncio

async def analyze_performance():
    async with HealthMonitor() as monitor:
        # Collect baseline metrics
        baseline = await monitor.check_all_services()
        
        # Monitor for degradation
        for i in range(10):
            current = await monitor.check_all_services()
            
            # Compare performance
            if current.summary['average_response_time'] > baseline.summary['average_response_time'] * 1.5:
                print("⚠️ Performance degradation detected!")
            
            await asyncio.sleep(30)

asyncio.run(analyze_performance())
```

## 🔧 Customization and Extension

### Custom Health Checks
Add your own service health checks:

```python
from monitoring.health_check import HealthMonitor, ServiceHealth
import time

class CustomHealthMonitor(HealthMonitor):
    async def check_custom_service(self) -> ServiceHealth:
        start_time = time.time()
        
        try:
            # Your custom health check logic here
            # Example: check external API
            response = await self.session.get('https://api.example.com/health')
            response.raise_for_status()
            
            response_time = (time.time() - start_time) * 1000
            
            return ServiceHealth(
                name='Custom Service',
                status='healthy',
                response_time=response_time,
                last_check=datetime.now(),
                details={'status_code': response.status}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                name='Custom Service',
                status='unhealthy',
                response_time=response_time,
                last_check=datetime.now(),
                error_message=str(e)
            )
```

### Custom Alerting
Implement custom alert handlers:

```python
class CustomAlertHandler:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    async def send_alert(self, health: SystemHealth):
        if health.overall_status in ['unhealthy', 'degraded']:
            alert_data = {
                'status': health.overall_status,
                'timestamp': health.last_check.isoformat(),
                'services': {
                    name: service.status 
                    for name, service in health.services.items()
                    if service.status != 'healthy'
                }
            }
            
            # Send to your alert system
            async with aiohttp.ClientSession() as session:
                await session.post(self.webhook_url, json=alert_data)
```

## 🔍 Troubleshooting

### Common Issues

#### Health Check Timeouts
```bash
# Increase timeout values
python monitoring/health_check.py --config config/extended_timeouts.json
```

#### Connection Refused Errors
```bash
# Check if services are running
docker-compose ps

# Restart services if needed
docker-compose restart redis neo4j postgresql qdrant
```

#### Performance Degradation
```bash
# Run performance-focused health check
python monitoring/health_check.py --performance

# Check resource usage
docker stats
```

### Debug Mode
Enable debug logging for detailed troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run health check with debug info
python monitoring/health_check.py --debug
```

## 📊 Monitoring Dashboard

### Real-time Dashboard
Create a simple monitoring dashboard:

```python
import streamlit as st
import asyncio
from monitoring.health_check import HealthMonitor

st.title("AI Enhancement Framework Monitor")

async def get_health_data():
    async with HealthMonitor() as monitor:
        return await monitor.check_all_services()

if st.button("Refresh Health Status"):
    health = asyncio.run(get_health_data())
    
    # Display overall status
    if health.overall_status == 'healthy':
        st.success(f"System Status: {health.overall_status.title()}")
    elif health.overall_status == 'degraded':
        st.warning(f"System Status: {health.overall_status.title()}")
    else:
        st.error(f"System Status: {health.overall_status.title()}")
    
    # Display service details
    for name, service in health.services.items():
        with st.expander(f"{name} - {service.status}"):
            st.metric("Response Time", f"{service.response_time:.2f}ms")
            if service.error_message:
                st.error(service.error_message)
```

## 🚀 Production Deployment

### Monitoring in Production
For production environments:

1. **Continuous Monitoring**: Run health checks every 30-60 seconds
2. **Alert Configuration**: Set up email/Slack notifications
3. **Log Aggregation**: Send logs to centralized logging system
4. **Metrics Storage**: Store metrics in time-series database
5. **Dashboard Integration**: Connect to Grafana/Datadog

### Example Production Configuration
```json
{
    "monitoring": {
        "interval": 60,
        "alert_channels": ["email", "slack", "pagerduty"],
        "metrics_storage": "prometheus",
        "log_level": "INFO"
    },
    "thresholds": {
        "response_time_warning": 500,
        "response_time_critical": 2000,
        "error_rate_warning": 1,
        "error_rate_critical": 5
    }
}
```

## 📚 API Reference

### HealthMonitor Class
```python
class HealthMonitor:
    async def check_redis() -> ServiceHealth
    async def check_neo4j() -> ServiceHealth
    async def check_postgresql() -> ServiceHealth
    async def check_qdrant() -> ServiceHealth
    async def check_framework_api() -> ServiceHealth
    async def check_all_services() -> SystemHealth
    
    def save_health_report(health: SystemHealth, filepath: str)
    def print_health_report(health: SystemHealth)
```

### ServiceHealth DataClass
```python
@dataclass
class ServiceHealth:
    name: str
    status: str  # 'healthy', 'unhealthy', 'degraded', 'unknown'
    response_time: float
    last_check: datetime
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
```

### SystemHealth DataClass
```python
@dataclass
class SystemHealth:
    overall_status: str
    last_check: datetime
    services: Dict[str, ServiceHealth]
    summary: Dict[str, Any]
```

## 🔗 Related Documentation

- **[Health Check Script](health_check.py)** - Main monitoring implementation
- **[Installation Guide](../cursor/CURSOR_INSTALLATION_HOW_TO.md)** - Setup instructions
- **[Configuration Guide](../cursor/CONFIGURATION_GUIDE.md)** - Advanced configuration
- **[Troubleshooting Guide](../cursor/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Docker Configuration](../docker/docker-compose.yml)** - Service orchestration

---

**Monitoring Framework Version**: 1.0.0  
**AI Enhancement Framework**: 1.0.0  
**Last Updated**: January 18, 2025  
**Status**: Production Ready ✅ 