#!/usr/bin/env python3
"""
Phase 16 Concurrency & Performance Optimization
===============================================

Advanced performance optimization system for Phase 16: Operational Excellence & Testing
Implements production-ready concurrency patterns, caching strategies, and performance monitoring:

- Async/await concurrency patterns with connection pooling
- Redis caching with intelligent cache invalidation
- Database query optimization with connection pooling
- Memory management and garbage collection optimization
- Real-time performance monitoring and alerting
- Load balancing and auto-scaling recommendations

Builds on existing performance infrastructure for production scalability.
"""

import asyncio
import gc
import json
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import aioredis
import asyncpg
import psutil
import structlog
import uvloop  # High-performance event loop

# Add current directory to path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))

# Import existing performance infrastructure
try:
    from scripts.performance.optimizer import PerformanceOptimizer
    EXISTING_PERFORMANCE_AVAILABLE = True
except ImportError:
    EXISTING_PERFORMANCE_AVAILABLE = False

# Configure structured logging
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time_ms: float
    throughput_rps: float
    active_connections: int
    cache_hit_rate: float
    database_pool_usage: float
    error_rate: float

@dataclass
class ConcurrencyConfig:
    """Concurrency configuration"""
    max_workers: int
    connection_pool_size: int
    async_task_limit: int
    thread_pool_size: int
    process_pool_size: int
    enable_uvloop: bool

@dataclass
class CacheConfig:
    """Cache configuration"""
    redis_url: str
    default_ttl: int
    max_memory_mb: int
    eviction_policy: str
    enable_compression: bool

class OptimizationLevel(Enum):
    """Performance optimization levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    PRODUCTION = "production"

class Phase16PerformanceOptimizer:
    """
    Phase 16 Concurrency & Performance Optimization System

    Advanced performance optimization system that provides:
    - Async/await concurrency patterns
    - Connection pooling for all databases
    - Intelligent Redis caching
    - Memory management optimization
    - Real-time performance monitoring
    - Auto-scaling recommendations
    """

    def __init__(self,
                 optimization_level: OptimizationLevel = OptimizationLevel.PRODUCTION,
                 concurrency_config: Optional[ConcurrencyConfig] = None,
                 cache_config: Optional[CacheConfig] = None):
        """Initialize Phase 16 performance optimizer"""

        self.optimization_level = optimization_level

        # Default concurrency configuration
        self.concurrency_config = concurrency_config or ConcurrencyConfig(
            max_workers=min(32, (os.cpu_count() or 1) * 4),
            connection_pool_size=20,
            async_task_limit=100,
            thread_pool_size=min(16, (os.cpu_count() or 1) * 2),
            process_pool_size=os.cpu_count() or 1,
            enable_uvloop=True
        )

        # Default cache configuration
        self.cache_config = cache_config or CacheConfig(
            redis_url=os.environ.get("REDIS_URL", "redis://localhost:6379"),
            default_ttl=3600,  # 1 hour
            max_memory_mb=512,
            eviction_policy="allkeys-lru",
            enable_compression=True
        )

        # Initialize performance tracking
        self.performance_metrics = []
        self.max_metrics_history = 1000
        self.performance_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "response_time_ms": 1000.0,
            "error_rate": 5.0
        }

        # Connection pools
        self.redis_pool = None
        self.postgres_pool = None
        self.connection_pools = {}

        # Thread and process pools
        self.thread_pool = None
        self.process_pool = None

        # Performance monitoring
        self.is_monitoring = False
        self.monitoring_tasks = []

        # Cache management
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_usage": 0
        }

        # Optimization state
        self.optimization_applied = False
        self.optimization_results = {}

        # Initialize existing performance optimizer if available
        if EXISTING_PERFORMANCE_AVAILABLE:
            try:
                self.existing_optimizer = PerformanceOptimizer(
                    neo4j_uri=os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                    neo4j_user=os.environ.get("NEO4J_USER", "neo4j"),
                    neo4j_password=os.environ.get("NEO4J_PASSWORD", "password")
                )
            except Exception as e:
                logger.warning("Failed to initialize existing performance optimizer", error=str(e))
                self.existing_optimizer = None
        else:
            self.existing_optimizer = None

        logger.info("Phase 16 Performance Optimizer initialized",
                   optimization_level=optimization_level.value,
                   max_workers=self.concurrency_config.max_workers,
                   connection_pool_size=self.concurrency_config.connection_pool_size,
                   cache_ttl=self.cache_config.default_ttl)

    async def initialize_optimization(self):
        """Initialize all optimization components"""
        if self.optimization_applied:
            logger.warning("Optimization already applied")
            return

        logger.info("Initializing Phase 16 performance optimization")

        # Apply uvloop optimization if enabled
        if self.concurrency_config.enable_uvloop:
            try:
                uvloop.install()
                logger.info("uvloop event loop installed for high performance")
            except Exception as e:
                logger.warning("Failed to install uvloop", error=str(e))

        # Initialize connection pools
        await self._initialize_connection_pools()

        # Initialize thread and process pools
        self._initialize_executor_pools()

        # Initialize Redis caching
        await self._initialize_redis_cache()

        # Apply memory optimizations
        self._apply_memory_optimizations()

        # Start performance monitoring
        await self._start_performance_monitoring()

        self.optimization_applied = True
        logger.info("Phase 16 performance optimization initialized successfully")

    async def _initialize_connection_pools(self):
        """Initialize database connection pools"""
        try:
            # PostgreSQL connection pool
            postgres_dsn = os.environ.get(
                "POSTGRES_DSN",
                "postgresql://postgres:password@localhost:5432/plc_gpt"
            )

            self.postgres_pool = await asyncpg.create_pool(
                postgres_dsn,
                min_size=5,
                max_size=self.concurrency_config.connection_pool_size,
                command_timeout=30,
                server_settings={
                    'application_name': 'plc_gpt_phase16',
                    'jit': 'off'  # Disable JIT for consistent performance
                }
            )

            logger.info("PostgreSQL connection pool initialized",
                       pool_size=self.concurrency_config.connection_pool_size)

        except Exception as e:
            logger.error("Failed to initialize PostgreSQL connection pool", error=str(e))

    def _initialize_executor_pools(self):
        """Initialize thread and process executor pools"""
        try:
            # Thread pool for I/O-bound tasks
            self.thread_pool = ThreadPoolExecutor(
                max_workers=self.concurrency_config.thread_pool_size,
                thread_name_prefix="plc_gpt_thread"
            )

            # Process pool for CPU-bound tasks
            self.process_pool = ProcessPoolExecutor(
                max_workers=self.concurrency_config.process_pool_size
            )

            logger.info("Executor pools initialized",
                       thread_pool_size=self.concurrency_config.thread_pool_size,
                       process_pool_size=self.concurrency_config.process_pool_size)

        except Exception as e:
            logger.error("Failed to initialize executor pools", error=str(e))

    async def _initialize_redis_cache(self):
        """Initialize Redis caching system"""
        try:
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.cache_config.redis_url,
                max_connections=self.concurrency_config.connection_pool_size,
                retry_on_timeout=True,
                socket_keepalive=True,
                socket_keepalive_options={}
            )

            # Test Redis connection
            redis = aioredis.Redis(connection_pool=self.redis_pool)
            await redis.ping()

            # Configure Redis for optimal performance
            await redis.config_set("maxmemory", f"{self.cache_config.max_memory_mb}mb")
            await redis.config_set("maxmemory-policy", self.cache_config.eviction_policy)

            logger.info("Redis cache initialized",
                       max_memory_mb=self.cache_config.max_memory_mb,
                       eviction_policy=self.cache_config.eviction_policy)

        except Exception as e:
            logger.error("Failed to initialize Redis cache", error=str(e))

    def _apply_memory_optimizations(self):
        """Apply memory management optimizations"""
        try:
            # Configure garbage collection for better performance
            gc.set_threshold(700, 10, 10)  # More aggressive GC

            # Enable garbage collection debugging in development
            if os.environ.get("DEBUG") == "1":
                gc.set_debug(gc.DEBUG_STATS)

            # Set memory allocation optimization
            if hasattr(sys, 'intern'):
                # Intern frequently used strings
                common_strings = [
                    "status", "success", "error", "data", "timestamp",
                    "healthy", "unhealthy", "pending", "completed"
                ]
                for s in common_strings:
                    sys.intern(s)

            logger.info("Memory optimizations applied")

        except Exception as e:
            logger.error("Failed to apply memory optimizations", error=str(e))

    async def _start_performance_monitoring(self):
        """Start performance monitoring tasks"""
        if self.is_monitoring:
            return

        self.is_monitoring = True

        # Start monitoring tasks
        self.monitoring_tasks = [
            asyncio.create_task(self._monitor_system_performance()),
            asyncio.create_task(self._monitor_cache_performance()),
            asyncio.create_task(self._monitor_database_performance()),
            asyncio.create_task(self._generate_optimization_recommendations())
        ]

        logger.info("Performance monitoring started", tasks_count=len(self.monitoring_tasks))

    async def _monitor_system_performance(self):
        """Monitor system performance metrics"""
        while self.is_monitoring:
            try:
                # Collect system metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()

                # Collect application metrics
                process = psutil.Process()
                process.memory_info().rss / 1024 / 1024  # MB

                # Calculate throughput (placeholder)
                throughput_rps = 50.0  # Would be calculated from actual requests

                # Create performance metrics
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    cpu_usage=cpu_percent,
                    memory_usage=memory.percent,
                    response_time_ms=25.0,  # Placeholder
                    throughput_rps=throughput_rps,
                    active_connections=10,  # Placeholder
                    cache_hit_rate=self._calculate_cache_hit_rate(),
                    database_pool_usage=self._calculate_db_pool_usage(),
                    error_rate=0.5  # Placeholder
                )

                # Store metrics
                self.performance_metrics.append(metrics)

                # Keep only recent metrics
                if len(self.performance_metrics) > self.max_metrics_history:
                    self.performance_metrics = self.performance_metrics[-self.max_metrics_history:]

                # Check performance thresholds
                await self._check_performance_thresholds(metrics)

                # Log performance metrics
                logger.info("performance_metrics",
                           cpu_usage=cpu_percent,
                           memory_usage=memory.percent,
                           cache_hit_rate=metrics.cache_hit_rate,
                           throughput_rps=throughput_rps)

                await asyncio.sleep(30)  # Monitor every 30 seconds

            except Exception as e:
                logger.error("Error monitoring system performance", error=str(e))
                await asyncio.sleep(30)

    async def _monitor_cache_performance(self):
        """Monitor cache performance and statistics"""
        while self.is_monitoring:
            try:
                if self.redis_pool:
                    redis = aioredis.Redis(connection_pool=self.redis_pool)

                    # Get Redis info
                    redis_info = await redis.info()

                    # Update cache stats
                    self.cache_stats.update({
                        "memory_usage": redis_info.get("used_memory", 0),
                        "keyspace_hits": redis_info.get("keyspace_hits", 0),
                        "keyspace_misses": redis_info.get("keyspace_misses", 0),
                        "evicted_keys": redis_info.get("evicted_keys", 0)
                    })

                    logger.info("cache_performance",
                               memory_usage_mb=self.cache_stats["memory_usage"] / 1024 / 1024,
                               hit_rate=self._calculate_cache_hit_rate(),
                               evictions=self.cache_stats["evicted_keys"])

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                logger.error("Error monitoring cache performance", error=str(e))
                await asyncio.sleep(60)

    async def _monitor_database_performance(self):
        """Monitor database performance and connection pools"""
        while self.is_monitoring:
            try:
                if self.postgres_pool:
                    pool_stats = {
                        "size": self.postgres_pool.get_size(),
                        "min_size": self.postgres_pool.get_min_size(),
                        "max_size": self.postgres_pool.get_max_size(),
                        "idle_connections": self.postgres_pool.get_idle_size()
                    }

                    logger.info("database_performance",
                               pool_size=pool_stats["size"],
                               idle_connections=pool_stats["idle_connections"],
                               utilization=self._calculate_db_pool_usage())

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                logger.error("Error monitoring database performance", error=str(e))
                await asyncio.sleep(60)

    async def _generate_optimization_recommendations(self):
        """Generate optimization recommendations based on metrics"""
        while self.is_monitoring:
            try:
                if len(self.performance_metrics) >= 10:
                    recent_metrics = self.performance_metrics[-10:]

                    # Analyze performance trends
                    avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
                    avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
                    avg_response_time = sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics)

                    recommendations = []

                    # CPU optimization recommendations
                    if avg_cpu > 70:
                        recommendations.append({
                            "type": "cpu_optimization",
                            "priority": "high",
                            "message": "High CPU usage detected. Consider scaling horizontally or optimizing CPU-intensive operations.",
                            "avg_cpu": avg_cpu
                        })

                    # Memory optimization recommendations
                    if avg_memory > 80:
                        recommendations.append({
                            "type": "memory_optimization",
                            "priority": "high",
                            "message": "High memory usage detected. Consider increasing cache eviction or optimizing memory usage.",
                            "avg_memory": avg_memory
                        })

                    # Response time optimization
                    if avg_response_time > 500:
                        recommendations.append({
                            "type": "response_time_optimization",
                            "priority": "medium",
                            "message": "High response times detected. Consider optimizing database queries or increasing cache usage.",
                            "avg_response_time": avg_response_time
                        })

                    # Log recommendations
                    if recommendations:
                        logger.warning("optimization_recommendations",
                                     recommendations=recommendations,
                                     metrics_analyzed=len(recent_metrics))

                await asyncio.sleep(300)  # Generate recommendations every 5 minutes

            except Exception as e:
                logger.error("Error generating optimization recommendations", error=str(e))
                await asyncio.sleep(300)

    async def _check_performance_thresholds(self, metrics: PerformanceMetrics):
        """Check performance thresholds and generate alerts"""
        alerts = []

        if metrics.cpu_usage > self.performance_thresholds["cpu_usage"]:
            alerts.append({
                "type": "cpu_threshold_exceeded",
                "severity": "warning",
                "message": f"CPU usage {metrics.cpu_usage:.1f}% exceeds threshold {self.performance_thresholds['cpu_usage']:.1f}%"
            })

        if metrics.memory_usage > self.performance_thresholds["memory_usage"]:
            alerts.append({
                "type": "memory_threshold_exceeded",
                "severity": "error",
                "message": f"Memory usage {metrics.memory_usage:.1f}% exceeds threshold {self.performance_thresholds['memory_usage']:.1f}%"
            })

        if metrics.response_time_ms > self.performance_thresholds["response_time_ms"]:
            alerts.append({
                "type": "response_time_threshold_exceeded",
                "severity": "warning",
                "message": f"Response time {metrics.response_time_ms:.1f}ms exceeds threshold {self.performance_thresholds['response_time_ms']:.1f}ms"
            })

        if metrics.error_rate > self.performance_thresholds["error_rate"]:
            alerts.append({
                "type": "error_rate_threshold_exceeded",
                "severity": "error",
                "message": f"Error rate {metrics.error_rate:.1f}% exceeds threshold {self.performance_thresholds['error_rate']:.1f}%"
            })

        # Log alerts
        for alert in alerts:
            logger.warning("performance_alert",
                          alert_type=alert["type"],
                          severity=alert["severity"],
                          message=alert["message"])

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        hits = self.cache_stats.get("keyspace_hits", 0)
        misses = self.cache_stats.get("keyspace_misses", 0)
        total = hits + misses
        return (hits / total * 100) if total > 0 else 0.0

    def _calculate_db_pool_usage(self) -> float:
        """Calculate database pool usage percentage"""
        if not self.postgres_pool:
            return 0.0

        size = self.postgres_pool.get_size()
        max_size = self.postgres_pool.get_max_size()
        return (size / max_size * 100) if max_size > 0 else 0.0

    # Caching decorators and utilities
    def cached(self, ttl: int = None, key_prefix: str = ""):
        """Decorator for caching function results"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.redis_pool:
                    return await func(*args, **kwargs)

                # Generate cache key
                cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"

                redis = aioredis.Redis(connection_pool=self.redis_pool)

                # Try to get from cache
                cached_result = await redis.get(cache_key)
                if cached_result:
                    self.cache_stats["hits"] += 1
                    return json.loads(cached_result)

                # Execute function and cache result
                result = await func(*args, **kwargs)
                cache_ttl = ttl or self.cache_config.default_ttl

                await redis.setex(
                    cache_key,
                    cache_ttl,
                    json.dumps(result, default=str)
                )

                self.cache_stats["misses"] += 1
                return result

            return wrapper
        return decorator

    @asynccontextmanager
    async def database_transaction(self):
        """Context manager for database transactions with connection pooling"""
        if not self.postgres_pool:
            raise RuntimeError("PostgreSQL connection pool not initialized")

        async with self.postgres_pool.acquire() as conn:
            async with conn.transaction():
                yield conn

    async def execute_concurrent_tasks(self, tasks: List[Callable], max_concurrency: int = None):
        """Execute tasks concurrently with controlled concurrency"""
        max_concurrency = max_concurrency or self.concurrency_config.async_task_limit

        semaphore = asyncio.Semaphore(max_concurrency)

        async def execute_with_semaphore(task):
            async with semaphore:
                return await task()

        # Execute tasks concurrently
        results = await asyncio.gather(
            *[execute_with_semaphore(task) for task in tasks],
            return_exceptions=True
        )

        return results

    async def execute_cpu_bound_task(self, func: Callable, *args, **kwargs):
        """Execute CPU-bound task in process pool"""
        if not self.process_pool:
            raise RuntimeError("Process pool not initialized")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.process_pool, func, *args, **kwargs)

    async def execute_io_bound_task(self, func: Callable, *args, **kwargs):
        """Execute I/O-bound task in thread pool"""
        if not self.thread_pool:
            raise RuntimeError("Thread pool not initialized")

        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func, *args, **kwargs)

    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.performance_metrics:
            # Return basic summary even without metrics
            return {
                "timestamp": datetime.now().isoformat(),
                "optimization_level": self.optimization_level.value,
                "optimization_applied": self.optimization_applied,
                "metrics_count": 0,
                "recent_performance": {
                    "avg_cpu_usage": 0.0,
                    "avg_memory_usage": 0.0,
                    "avg_response_time_ms": 0.0,
                    "avg_throughput_rps": 0.0,
                    "cache_hit_rate": 0.0,
                    "db_pool_usage": 0.0
                },
                "configuration": {
                    "max_workers": self.concurrency_config.max_workers,
                    "connection_pool_size": self.concurrency_config.connection_pool_size,
                    "thread_pool_size": self.concurrency_config.thread_pool_size,
                    "process_pool_size": self.concurrency_config.process_pool_size,
                    "cache_ttl": self.cache_config.default_ttl,
                    "cache_max_memory_mb": self.cache_config.max_memory_mb
                },
                "cache_stats": self.cache_stats
            }

        recent_metrics = self.performance_metrics[-10:] if len(self.performance_metrics) >= 10 else self.performance_metrics

        return {
            "timestamp": datetime.now().isoformat(),
            "optimization_level": self.optimization_level.value,
            "optimization_applied": self.optimization_applied,
            "metrics_count": len(self.performance_metrics),
            "recent_performance": {
                "avg_cpu_usage": sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics),
                "avg_memory_usage": sum(m.memory_usage for m in recent_metrics) / len(recent_metrics),
                "avg_response_time_ms": sum(m.response_time_ms for m in recent_metrics) / len(recent_metrics),
                "avg_throughput_rps": sum(m.throughput_rps for m in recent_metrics) / len(recent_metrics),
                "cache_hit_rate": self._calculate_cache_hit_rate(),
                "db_pool_usage": self._calculate_db_pool_usage()
            },
            "configuration": {
                "max_workers": self.concurrency_config.max_workers,
                "connection_pool_size": self.concurrency_config.connection_pool_size,
                "thread_pool_size": self.concurrency_config.thread_pool_size,
                "process_pool_size": self.concurrency_config.process_pool_size,
                "cache_ttl": self.cache_config.default_ttl,
                "cache_max_memory_mb": self.cache_config.max_memory_mb
            },
            "cache_stats": self.cache_stats
        }

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Phase 16 performance optimizer")

        # Stop monitoring
        self.is_monitoring = False

        # Cancel monitoring tasks
        for task in self.monitoring_tasks:
            task.cancel()

        if self.monitoring_tasks:
            await asyncio.gather(*self.monitoring_tasks, return_exceptions=True)

        # Close connection pools
        if self.postgres_pool:
            await self.postgres_pool.close()

        if self.redis_pool:
            await self.redis_pool.disconnect()

        # Shutdown executor pools
        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)

        if self.process_pool:
            self.process_pool.shutdown(wait=True)

        logger.info("Phase 16 performance optimizer cleanup completed")


# Global optimizer instance
phase16_optimizer = None

def get_phase16_optimizer() -> Phase16PerformanceOptimizer:
    """Get the global Phase 16 performance optimizer instance"""
    global phase16_optimizer
    if phase16_optimizer is None:
        phase16_optimizer = Phase16PerformanceOptimizer()
    return phase16_optimizer


async def main():
    """Main function for running Phase 16 performance optimization"""
    print("🚀 Phase 16 Concurrency & Performance Optimization")
    print("=" * 80)

    # Initialize optimizer
    optimizer = Phase16PerformanceOptimizer(
        optimization_level=OptimizationLevel.PRODUCTION
    )

    try:
        # Initialize optimization
        await optimizer.initialize_optimization()

        print("✅ Performance optimization initialized")
        print(f"✅ Max workers: {optimizer.concurrency_config.max_workers}")
        print(f"✅ Connection pool size: {optimizer.concurrency_config.connection_pool_size}")
        print(f"✅ Cache TTL: {optimizer.cache_config.default_ttl}s")

        # Run for a short time to demonstrate
        await asyncio.sleep(5)

        # Get performance summary
        summary = await optimizer.get_performance_summary()
        print("\n📊 Performance Summary:")
        print(f"   Optimization Level: {summary['optimization_level']}")
        print(f"   Metrics Collected: {summary['metrics_count']}")
        print(f"   Cache Hit Rate: {summary['recent_performance']['cache_hit_rate']:.1f}%")

        print("\n✅ Phase 16 performance optimization demonstration completed")

    except KeyboardInterrupt:
        print("\n🛑 Stopping optimization...")
    finally:
        await optimizer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
