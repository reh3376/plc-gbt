#!/usr/bin/env python3
"""
Real-time Monitoring Dashboard
Created: January 1, 2025
Purpose: Visual performance and system monitoring for PLC-GPT
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict

# Try to import psutil, graceful fallback if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. System metrics will be simulated.")

# FastAPI and web components
import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse, JSONResponse

# Neo4j and Qdrant
from neo4j import GraphDatabase
from qdrant_client import QdrantClient

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io_bytes: Dict[str, int]
    active_connections: int
    uptime_seconds: float

@dataclass
class QueryMetrics:
    """Query performance metrics"""
    timestamp: datetime
    query_count: int
    avg_response_time_ms: float
    cache_hit_rate: float
    active_queries: int
    slow_queries: int
    error_rate: float

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    timestamp: datetime
    neo4j_status: str
    neo4j_connections: int
    neo4j_transaction_rate: float
    qdrant_status: str
    qdrant_collections: int
    qdrant_points_count: int

class MonitoringDashboard:
    """
    Real-time monitoring dashboard for PLC-GPT system.

    Features:
    - System resource monitoring
    - Query performance analytics
    - Database health monitoring
    - Real-time websocket updates
    - Alert system for performance issues
    """

    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "password",
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        metrics_retention_hours: int = 24
    ):
        """Initialize monitoring dashboard"""
        # Database connections
        try:
            self.neo4j_driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(neo4j_user, neo4j_password)
            )
        except Exception as e:
            logger.warning("Failed to connect to Neo4j", error=str(e))
            self.neo4j_driver = None

        try:
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        except Exception as e:
            logger.warning("Failed to connect to Qdrant", error=str(e))
            self.qdrant_client = None

        # Metrics storage
        self.metrics_retention = timedelta(hours=metrics_retention_hours)
        self.system_metrics = deque(maxlen=1000)
        self.query_metrics = deque(maxlen=1000)
        self.database_metrics = deque(maxlen=1000)

        # Real-time tracking
        self.active_connections = set()
        self.active_queries = {}
        self.query_stats = defaultdict(list)
        self.alerts = deque(maxlen=100)

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_time = time.time()

        # FastAPI app
        self.app = FastAPI(title="PLC-GPT Monitoring Dashboard")
        self._setup_routes()

        logger.info(f"MonitoringDashboard initialized, psutil_available={PSUTIL_AVAILABLE}")

    def _setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Main dashboard page"""
            return HTMLResponse(self._get_dashboard_html())

        @self.app.get("/api/metrics/system")
        async def get_system_metrics():
            """Get current system metrics"""
            try:
                current_metrics = await self._collect_system_metrics()
                return JSONResponse({
                    "current": asdict(current_metrics),
                    "history": [asdict(m) for m in list(self.system_metrics)[-50:]]
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/metrics/queries")
        async def get_query_metrics():
            """Get query performance metrics"""
            try:
                current_metrics = await self._collect_query_metrics()
                return JSONResponse({
                    "current": asdict(current_metrics),
                    "history": [asdict(m) for m in list(self.query_metrics)[-50:]]
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/metrics/databases")
        async def get_database_metrics():
            """Get database health metrics"""
            try:
                current_metrics = await self._collect_database_metrics()
                return JSONResponse({
                    "current": asdict(current_metrics),
                    "history": [asdict(m) for m in list(self.database_metrics)[-50:]]
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/health")
        async def health_check():
            """System health check"""
            health = await self._get_system_health()
            return JSONResponse(health)

        @self.app.get("/api/alerts")
        async def get_alerts():
            """Get system alerts"""
            return JSONResponse({
                "alerts": list(self.alerts),
                "count": len(self.alerts)
            })

        @self.app.websocket("/ws/metrics")
        async def websocket_metrics(websocket: WebSocket):
            """WebSocket for real-time metrics"""
            await websocket.accept()
            self.active_connections.add(websocket)

            try:
                while True:
                    # Send current metrics
                    metrics = {
                        "system": asdict(await self._collect_system_metrics()),
                        "queries": asdict(await self._collect_query_metrics()),
                        "database": asdict(await self._collect_database_metrics()),
                        "timestamp": datetime.now().isoformat()
                    }

                    await websocket.send_json(metrics)
                    await asyncio.sleep(5)  # Update every 5 seconds

            except Exception as e:
                logger.warning("WebSocket connection closed", error=str(e))
            finally:
                self.active_connections.discard(websocket)

    async def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics"""
        try:
            if PSUTIL_AVAILABLE:
                # Real metrics using psutil
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                # Network I/O
                network_io = psutil.net_io_counters()
                network_io_bytes = {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_recv": network_io.bytes_recv
                }
            else:
                # Simulated metrics when psutil not available
                import random
                cpu_percent = random.uniform(10, 40)  # Simulated CPU usage
                memory_percent = random.uniform(20, 60)  # Simulated memory usage
                disk_usage_percent = random.uniform(30, 70)  # Simulated disk usage
                network_io_bytes = {
                    "bytes_sent": random.randint(1000000, 10000000),
                    "bytes_recv": random.randint(1000000, 10000000)
                }

                return SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_usage_percent=disk_usage_percent,
                    network_io_bytes=network_io_bytes,
                    active_connections=len(self.active_connections),
                    uptime_seconds=time.time() - self.start_time
                )

            # Uptime
            uptime_seconds = time.time() - self.start_time

            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=(disk.used / disk.total) * 100,
                network_io_bytes=network_io_bytes,
                active_connections=len(self.active_connections),
                uptime_seconds=uptime_seconds
            )

        except Exception as e:
            logger.error("Failed to collect system metrics", error=str(e))
            return SystemMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io_bytes={"bytes_sent": 0, "bytes_recv": 0},
                active_connections=0,
                uptime_seconds=0.0
            )

    async def _collect_query_metrics(self) -> QueryMetrics:
        """Collect query performance metrics"""
        try:
            # Calculate query statistics
            recent_queries = []
            for _query_id, stats_list in self.query_stats.items():
                recent_stats = [
                    s for s in stats_list
                    if s["timestamp"] > datetime.now() - timedelta(minutes=5)
                ]
                recent_queries.extend(recent_stats)

            if recent_queries:
                avg_response_time = sum(q["execution_time_ms"] for q in recent_queries) / len(recent_queries)
                error_count = sum(1 for q in recent_queries if not q.get("success", True))
                error_rate = (error_count / len(recent_queries)) * 100
                slow_queries = sum(1 for q in recent_queries if q["execution_time_ms"] > 1000)
            else:
                avg_response_time = 0.0
                error_rate = 0.0
                slow_queries = 0

            return QueryMetrics(
                timestamp=datetime.now(),
                query_count=len(recent_queries),
                avg_response_time_ms=avg_response_time,
                cache_hit_rate=75.0,  # Would integrate with actual cache metrics
                active_queries=len(self.active_queries),
                slow_queries=slow_queries,
                error_rate=error_rate
            )

        except Exception as e:
            logger.error("Failed to collect query metrics", error=str(e))
            return QueryMetrics(
                timestamp=datetime.now(),
                query_count=0,
                avg_response_time_ms=0.0,
                cache_hit_rate=0.0,
                active_queries=0,
                slow_queries=0,
                error_rate=0.0
            )

    async def _collect_database_metrics(self) -> DatabaseMetrics:
        """Collect database health metrics"""
        try:
            # Neo4j status
            neo4j_status = "connected"
            neo4j_connections = 0
            neo4j_transaction_rate = 0.0

            if self.neo4j_driver:
                try:
                    with self.neo4j_driver.session() as session:
                        result = session.run("RETURN 1")
                        list(result)  # Consume result
                        neo4j_status = "connected"
                except Exception:
                    neo4j_status = "disconnected"
            else:
                neo4j_status = "disconnected"

            # Qdrant status
            qdrant_status = "connected"
            qdrant_collections = 0
            qdrant_points_count = 0

            if self.qdrant_client:
                try:
                    collections = self.qdrant_client.get_collections()
                    qdrant_collections = len(collections.collections)

                    # Count total points across collections
                    for collection in collections.collections:
                        try:
                            info = self.qdrant_client.get_collection(collection.name)
                            qdrant_points_count += info.points_count or 0
                        except Exception:
                            continue

                except Exception:
                    qdrant_status = "disconnected"
            else:
                qdrant_status = "disconnected"

            return DatabaseMetrics(
                timestamp=datetime.now(),
                neo4j_status=neo4j_status,
                neo4j_connections=neo4j_connections,
                neo4j_transaction_rate=neo4j_transaction_rate,
                qdrant_status=qdrant_status,
                qdrant_collections=qdrant_collections,
                qdrant_points_count=qdrant_points_count
            )

        except Exception as e:
            logger.error("Failed to collect database metrics", error=str(e))
            return DatabaseMetrics(
                timestamp=datetime.now(),
                neo4j_status="error",
                neo4j_connections=0,
                neo4j_transaction_rate=0.0,
                qdrant_status="error",
                qdrant_collections=0,
                qdrant_points_count=0
            )

    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        try:
            system_metrics = await self._collect_system_metrics()
            query_metrics = await self._collect_query_metrics()
            db_metrics = await self._collect_database_metrics()

            # Determine health status
            health_issues = []

            if system_metrics.cpu_percent > 80:
                health_issues.append("high_cpu_usage")
            if system_metrics.memory_percent > 85:
                health_issues.append("high_memory_usage")
            if query_metrics.error_rate > 10:
                health_issues.append("high_error_rate")
            if db_metrics.neo4j_status != "connected":
                health_issues.append("neo4j_disconnected")
            if db_metrics.qdrant_status != "connected":
                health_issues.append("qdrant_disconnected")

            if not health_issues:
                status = "healthy"
            elif len(health_issues) <= 2:
                status = "warning"
            else:
                status = "critical"

            return {
                "status": status,
                "issues": health_issues,
                "uptime_seconds": system_metrics.uptime_seconds,
                "last_check": datetime.now().isoformat(),
                "psutil_available": PSUTIL_AVAILABLE,
                "components": {
                    "system": "ok" if system_metrics.cpu_percent < 80 and system_metrics.memory_percent < 85 else "warning",
                    "neo4j": db_metrics.neo4j_status,
                    "qdrant": db_metrics.qdrant_status,
                    "queries": "ok" if query_metrics.error_rate < 10 else "warning"
                }
            }

        except Exception as e:
            logger.error("Failed to get system health", error=str(e))
            return {
                "status": "error",
                "issues": ["health_check_failed"],
                "error": str(e),
                "last_check": datetime.now().isoformat()
            }

    def _get_dashboard_html(self) -> str:
        """Generate dashboard HTML"""
        psutil_warning = "" if PSUTIL_AVAILABLE else """
        <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin-bottom: 20px; border-radius: 4px;">
            <strong>⚠️ Warning:</strong> psutil not available. System metrics are simulated.
            Install with: <code>pip install psutil</code>
        </div>
        """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>PLC-GPT Monitoring Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
                .card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .metric-value {{ font-weight: bold; color: #007bff; }}
                .status-ok {{ color: #28a745; }}
                .status-warning {{ color: #ffc107; }}
                .status-critical {{ color: #dc3545; }}
                .alert {{ padding: 10px; margin: 5px 0; border-radius: 4px; }}
                .alert-warning {{ background-color: #fff3cd; border-left: 4px solid #ffc107; }}
                .alert-critical {{ background-color: #f8d7da; border-left: 4px solid #dc3545; }}
                h1, h2 {{ color: #333; }}
                canvas {{ max-height: 300px; }}
            </style>
        </head>
        <body>
            <h1>PLC-GPT System Monitoring Dashboard</h1>
            {psutil_warning}

            <div class="dashboard">
                <div class="card">
                    <h2>System Health</h2>
                    <div id="system-health">Loading...</div>
                </div>

                <div class="card">
                    <h2>System Metrics</h2>
                    <canvas id="system-chart"></canvas>
                </div>

                <div class="card">
                    <h2>Query Performance</h2>
                    <canvas id="query-chart"></canvas>
                </div>

                <div class="card">
                    <h2>Database Status</h2>
                    <div id="database-status">Loading...</div>
                </div>

                <div class="card">
                    <h2>Recent Alerts</h2>
                    <div id="alerts">Loading...</div>
                </div>
            </div>

            <script>
                // WebSocket connection for real-time updates
                const ws = new WebSocket(`ws://${{window.location.host}}/ws/metrics`);

                // Chart configurations
                const systemChart = new Chart(document.getElementById('system-chart'), {{
                    type: 'line',
                    data: {{
                        labels: [],
                        datasets: [{{
                            label: 'CPU %',
                            data: [],
                            borderColor: 'rgb(75, 192, 192)',
                            tension: 0.1
                        }}, {{
                            label: 'Memory %',
                            data: [],
                            borderColor: 'rgb(255, 99, 132)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{ beginAtZero: true, max: 100 }}
                        }}
                    }}
                }});

                const queryChart = new Chart(document.getElementById('query-chart'), {{
                    type: 'line',
                    data: {{
                        labels: [],
                        datasets: [{{
                            label: 'Avg Response Time (ms)',
                            data: [],
                            borderColor: 'rgb(54, 162, 235)',
                            tension: 0.1
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{ beginAtZero: true }}
                        }}
                    }}
                }});

                ws.onmessage = function(event) {{
                    const data = JSON.parse(event.data);
                    updateDashboard(data);
                }};

                function updateDashboard(data) {{
                    // Update system health
                    const healthDiv = document.getElementById('system-health');
                    healthDiv.innerHTML = `
                        <div class="metric">
                            <span>CPU Usage:</span>
                            <span class="metric-value">${{data.system.cpu_percent.toFixed(1)}}%</span>
                        </div>
                        <div class="metric">
                            <span>Memory Usage:</span>
                            <span class="metric-value">${{data.system.memory_percent.toFixed(1)}}%</span>
                        </div>
                        <div class="metric">
                            <span>Active Connections:</span>
                            <span class="metric-value">${{data.system.active_connections}}</span>
                        </div>
                    `;

                    // Update database status
                    const dbDiv = document.getElementById('database-status');
                    dbDiv.innerHTML = `
                        <div class="metric">
                            <span>Neo4j:</span>
                            <span class="metric-value status-${{data.database.neo4j_status === 'connected' ? 'ok' : 'critical'}}">${{data.database.neo4j_status}}</span>
                        </div>
                        <div class="metric">
                            <span>Qdrant:</span>
                            <span class="metric-value status-${{data.database.qdrant_status === 'connected' ? 'ok' : 'critical'}}">${{data.database.qdrant_status}}</span>
                        </div>
                        <div class="metric">
                            <span>Vector Points:</span>
                            <span class="metric-value">${{data.database.qdrant_points_count.toLocaleString()}}</span>
                        </div>
                    `;

                    // Update charts
                    const time = new Date(data.timestamp).toLocaleTimeString();

                    // System chart
                    systemChart.data.labels.push(time);
                    systemChart.data.datasets[0].data.push(data.system.cpu_percent);
                    systemChart.data.datasets[1].data.push(data.system.memory_percent);

                    if (systemChart.data.labels.length > 20) {{
                        systemChart.data.labels.shift();
                        systemChart.data.datasets[0].data.shift();
                        systemChart.data.datasets[1].data.shift();
                    }}
                    systemChart.update('none');

                    // Query chart
                    queryChart.data.labels.push(time);
                    queryChart.data.datasets[0].data.push(data.queries.avg_response_time_ms);

                    if (queryChart.data.labels.length > 20) {{
                        queryChart.data.labels.shift();
                        queryChart.data.datasets[0].data.shift();
                    }}
                    queryChart.update('none');
                }}

                // Load alerts
                fetch('/api/alerts')
                    .then(response => response.json())
                    .then(data => {{
                        const alertsDiv = document.getElementById('alerts');
                        if (data.alerts.length === 0) {{
                            alertsDiv.innerHTML = '<p>No recent alerts</p>';
                        }} else {{
                            alertsDiv.innerHTML = data.alerts.slice(-5).map(alert => `
                                <div class="alert alert-${{alert.level}}">
                                    <strong>${{alert.level.toUpperCase()}}:</strong> ${{alert.message}}
                                    <br><small>${{new Date(alert.timestamp).toLocaleString()}}</small>
                                </div>
                            `).join('');
                        }}
                    }});
            </script>
        </body>
        </html>
        """

    def run_server(self, host: str = "0.0.0.0", port: int = 8080):
        """Run the monitoring dashboard server"""
        logger.info(f"Starting monitoring dashboard on http://{host}:{port}")
        uvicorn.run(self.app, host=host, port=port)

    def close(self):
        """Clean up resources"""
        if self.neo4j_driver:
            self.neo4j_driver.close()

# Utility function to start monitoring
def start_monitoring_dashboard(
    host: str = "0.0.0.0",
    port: int = 8080,
    **kwargs
):
    """Start the monitoring dashboard"""
    dashboard = MonitoringDashboard(**kwargs)
    dashboard.run_server(host=host, port=port)
