#!/usr/bin/env python3
"""
🤖 Persistent Redis Manager - AI Task Orchestrator Implementation

Advanced Redis connection management system that maintains persistent connections
for enhanced caching and short-term memory performance in the PLC Memory Management System.

Following AI Task Orchestrator Guide methodology for MODERATE complexity task.

Key Features:
- Persistent connection management with automatic reconnection
- Health monitoring and connection validation
- Performance optimization for short-term memory operations
- Graceful degradation and error recovery
- Connection pooling with intelligent sizing
- Real-time metrics and diagnostics

Author: AI Task Orchestrator
Created: 2025-01-10
Phase: Database Connectivity Enhancement
Complexity: MODERATE (100-500 lines, 2-5 files, 1-3 hours)
"""

import os
import sys
import json
import time
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Redis imports
try:
    import redis
    import redis.sentinel
    from redis.connection import ConnectionPool
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ConnectionState(Enum):
    """Redis connection state enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"
    HEALTHY = "healthy"

class CacheOperation(Enum):
    """Cache operation types for monitoring"""
    GET = "get"
    SET = "set"
    DELETE = "delete"
    EXPIRE = "expire"
    EXISTS = "exists"
    PIPELINE = "pipeline"

@dataclass
class RedisConnectionConfig:
    """Configuration for Redis persistent connections"""
    host: str = "localhost"
    port: int = 6379
    password: Optional[str] = None
    database: int = 0
    socket_timeout: float = 5.0
    socket_connect_timeout: float = 5.0
    max_connections: int = 20
    retry_on_timeout: bool = True
    health_check_interval: int = 30
    connection_pool_class_kwargs: Dict[str, Any] = None

@dataclass
class ConnectionMetrics:
    """Redis connection performance metrics"""
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    connection_attempts: int = 0
    successful_connections: int = 0
    failed_connections: int = 0
    last_connection_time: Optional[datetime] = None
    last_successful_operation: Optional[datetime] = None
    last_error: Optional[str] = None
    average_response_time_ms: float = 0.0
    peak_connections: int = 0
    current_connections: int = 0

@dataclass
class HealthCheckResult:
    """Health check result information"""
    is_healthy: bool
    response_time_ms: float
    error_message: Optional[str] = None
    connection_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    last_check_time: datetime = None

class PersistentRedisManager:
    """
    🎯 Persistent Redis Connection Manager
    
    Provides enterprise-grade Redis connection management with:
    - Persistent connections for enhanced performance
    - Automatic reconnection with exponential backoff
    - Health monitoring and diagnostics
    - Connection pooling and resource optimization
    - Performance metrics and monitoring
    - Graceful error handling and recovery
    
    Following AI Task Orchestrator methodology for reliability and performance.
    """
    
    def __init__(self, config: Optional[RedisConnectionConfig] = None):
        """Initialize the persistent Redis manager"""
        self.start_time = datetime.now()
        self.session_id = f"redis_manager_{int(time.time())}"
        
        # Configuration
        self.config = config or self._load_default_config()
        
        # Connection management
        self.connection_pool: Optional[ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.connection_state = ConnectionState.DISCONNECTED
        self.connection_count = 0  # Track active connection count
        
        # Health monitoring
        self.metrics = ConnectionMetrics()
        self.last_health_check: Optional[HealthCheckResult] = None
        self.health_check_thread: Optional[threading.Thread] = None
        self.health_check_enabled = True
        
        # Reconnection management
        self.max_retries = 5
        self.base_retry_delay = 1.0
        self.max_retry_delay = 30.0
        self.current_retry_count = 0
        
        # Performance tracking
        self.operation_times = []
        self.max_operation_history = 1000
        
        # Threading
        self.lock = threading.RLock()
        self.shutdown_event = threading.Event()
        
        logger.info(f"PersistentRedisManager initialized with session: {self.session_id}")

    def _load_default_config(self) -> RedisConnectionConfig:
        """Load default configuration from environment variables"""
        return RedisConnectionConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            password=os.getenv("REDIS_PASSWORD") or None,
            database=int(os.getenv("REDIS_DB", "0")),
            socket_timeout=float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0")),
            socket_connect_timeout=float(os.getenv("REDIS_CONNECT_TIMEOUT", "5.0")),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            retry_on_timeout=os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true",
            health_check_interval=int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))
        )

    async def initialize_connection(self) -> bool:
        """Initialize persistent Redis connection with connection pooling"""
        if not REDIS_AVAILABLE:
            logger.error("Redis library not available. Please install redis-py")
            return False
        
        try:
            with self.lock:
                self.connection_state = ConnectionState.CONNECTING
                self.metrics.connection_attempts += 1
                
                # Create connection pool
                self.connection_pool = ConnectionPool(
                    host=self.config.host,
                    port=self.config.port,
                    password=self.config.password,
                    db=self.config.database,
                    socket_timeout=self.config.socket_timeout,
                    socket_connect_timeout=self.config.socket_connect_timeout,
                    max_connections=self.config.max_connections,
                    retry_on_timeout=self.config.retry_on_timeout,
                    health_check_interval=self.config.health_check_interval
                )
                
                # Create Redis client with connection pool
                self.redis_client = redis.Redis(
                    connection_pool=self.connection_pool,
                    decode_responses=True
                )
                
                # Test connection
                await self._test_connection()
                
                self.connection_state = ConnectionState.CONNECTED
                self.metrics.successful_connections += 1
                self.metrics.last_connection_time = datetime.now()
                self.current_retry_count = 0
                self.connection_count = 1  # Initial connection established
                
                # Start health monitoring
                self._start_health_monitoring()
                
                logger.info(f"✅ Persistent Redis connection established: {self.config.host}:{self.config.port}")
                return True
                
        except Exception as e:
            self.connection_state = ConnectionState.ERROR
            self.metrics.failed_connections += 1
            self.metrics.last_error = str(e)
            logger.error(f"❌ Failed to initialize Redis connection: {str(e)}")
            return False

    async def _test_connection(self) -> bool:
        """Test Redis connection with ping"""
        try:
            start_time = time.time()
            # Run ping in executor to avoid blocking
            loop = asyncio.get_event_loop()
            pong = await loop.run_in_executor(None, self.redis_client.ping)
            response_time = (time.time() - start_time) * 1000
            
            if pong:
                logger.debug(f"Redis ping successful: {response_time:.1f}ms")
                return True
            else:
                raise Exception("Ping returned False")
                
        except Exception as e:
            logger.error(f"Redis connection test failed: {str(e)}")
            raise

    def _start_health_monitoring(self) -> None:
        """Start background health monitoring thread"""
        if self.health_check_thread and self.health_check_thread.is_alive():
            return
        
        def health_check_loop():
            """Background health check loop"""
            while not self.shutdown_event.is_set() and self.health_check_enabled:
                try:
                    asyncio.run(self._perform_health_check())
                    time.sleep(self.config.health_check_interval)
                except Exception as e:
                    logger.error(f"Health check error: {str(e)}")
                    time.sleep(5)  # Wait before retry
        
        self.health_check_thread = threading.Thread(
            target=health_check_loop, daemon=True
        )
        self.health_check_thread.start()
        logger.info("Health monitoring started")

    async def _perform_health_check(self) -> HealthCheckResult:
        """Perform comprehensive health check"""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            loop = asyncio.get_event_loop()
            pong = await loop.run_in_executor(None, self.redis_client.ping)
            
            if not pong:
                raise Exception("Ping failed")
            
            response_time = (time.time() - start_time) * 1000
            
            # Get connection pool info
            connection_count = len(self.connection_pool._available_connections) if self.connection_pool else 0
            self.connection_count = connection_count  # Update instance connection count
            
            # Get Redis info
            info = await loop.run_in_executor(None, self.redis_client.info, 'memory')
            memory_usage_mb = info.get('used_memory', 0) / (1024 * 1024)
            
            # Update connection state
            self.connection_state = ConnectionState.HEALTHY
            
            result = HealthCheckResult(
                is_healthy=True,
                response_time_ms=response_time,
                connection_count=connection_count,
                memory_usage_mb=memory_usage_mb,
                last_check_time=datetime.now()
            )
            
            self.last_health_check = result
            return result
            
        except Exception as e:
            logger.warning(f"Health check failed: {str(e)}")
            self.connection_state = ConnectionState.ERROR
            
            result = HealthCheckResult(
                is_healthy=False,
                response_time_ms=(time.time() - start_time) * 1000,
                error_message=str(e),
                last_check_time=datetime.now()
            )
            
            self.last_health_check = result
            
            # Attempt reconnection if unhealthy
            await self._attempt_reconnection()
            
            return result

    async def _attempt_reconnection(self) -> bool:
        """Attempt to reconnect with exponential backoff"""
        if self.current_retry_count >= self.max_retries:
            logger.error(f"Max reconnection attempts ({self.max_retries}) exceeded")
            return False
        
        self.connection_state = ConnectionState.RECONNECTING
        
        # Calculate delay with exponential backoff
        delay = min(
            self.base_retry_delay * (2 ** self.current_retry_count),
            self.max_retry_delay
        )
        
        logger.info(f"Attempting reconnection in {delay:.1f}s (attempt {self.current_retry_count + 1}/{self.max_retries})")
        
        await asyncio.sleep(delay)
        self.current_retry_count += 1
        
        # Close existing connections
        await self.close_connection()
        
        # Attempt new connection
        success = await self.initialize_connection()
        
        if success:
            logger.info("✅ Reconnection successful")
            self.current_retry_count = 0
        else:
            logger.warning(f"❌ Reconnection attempt {self.current_retry_count} failed")
        
        return success

    async def execute_operation(self, operation: CacheOperation, **kwargs) -> Any:
        """Execute Redis operation with error handling and metrics"""
        if not self.is_connected():
            logger.warning("Redis not connected, attempting reconnection...")
            if not await self.initialize_connection():
                raise Exception("Redis connection unavailable")
        
        start_time = time.time()
        
        try:
            with self.lock:
                self.metrics.total_operations += 1
                
                # Execute operation based on type
                loop = asyncio.get_event_loop()
                
                if operation == CacheOperation.GET:
                    result = await loop.run_in_executor(None, self.redis_client.get, kwargs['key'])
                    if result is not None:
                        self.metrics.cache_hits += 1
                    else:
                        self.metrics.cache_misses += 1
                    
                elif operation == CacheOperation.SET:
                    result = await loop.run_in_executor(
                        None, 
                        self.redis_client.set, 
                        kwargs['key'], 
                        kwargs['value'],
                        ex=kwargs.get('ttl')
                    )
                    
                elif operation == CacheOperation.DELETE:
                    result = await loop.run_in_executor(None, self.redis_client.delete, kwargs['key'])
                    
                elif operation == CacheOperation.EXISTS:
                    result = await loop.run_in_executor(None, self.redis_client.exists, kwargs['key'])
                    
                elif operation == CacheOperation.EXPIRE:
                    result = await loop.run_in_executor(
                        None, 
                        self.redis_client.expire, 
                        kwargs['key'], 
                        kwargs['ttl']
                    )
                    
                else:
                    raise ValueError(f"Unsupported operation: {operation}")
                
                # Record metrics
                execution_time = (time.time() - start_time) * 1000
                self._record_operation_time(execution_time)
                
                self.metrics.successful_operations += 1
                self.metrics.last_successful_operation = datetime.now()
                
                return result
                
        except Exception as e:
            self.metrics.failed_operations += 1
            self.metrics.last_error = str(e)
            logger.error(f"Redis operation {operation.value} failed: {str(e)}")
            
            # Mark connection as potentially unhealthy
            if "connection" in str(e).lower() or "timeout" in str(e).lower():
                self.connection_state = ConnectionState.ERROR
            
            raise

    def _record_operation_time(self, execution_time_ms: float) -> None:
        """Record operation execution time for performance tracking"""
        self.operation_times.append(execution_time_ms)
        
        # Keep only recent operation times
        if len(self.operation_times) > self.max_operation_history:
            self.operation_times = self.operation_times[-self.max_operation_history:]
        
        # Update average response time
        if self.operation_times:
            self.metrics.average_response_time_ms = sum(self.operation_times) / len(self.operation_times)

    def is_connected(self) -> bool:
        """Check if Redis is currently connected and healthy"""
        return (
            self.connection_state in [ConnectionState.CONNECTED, ConnectionState.HEALTHY] 
            and self.redis_client is not None
        )

    def is_healthy(self) -> bool:
        """Check if Redis connection is healthy based on last health check"""
        if not self.last_health_check:
            return False
        
        # Consider healthy if last check was successful and recent
        time_since_check = datetime.now() - self.last_health_check.last_check_time
        return (
            self.last_health_check.is_healthy 
            and time_since_check.total_seconds() < (self.config.health_check_interval * 2)
        )

    def get_connection_status(self) -> Dict[str, Any]:
        """Get comprehensive connection status information"""
        return {
            'session_id': self.session_id,
            'connection_state': self.connection_state.value,
            'is_connected': self.is_connected(),
            'is_healthy': self.is_healthy(),
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds(),
            'configuration': {
                'host': self.config.host,
                'port': self.config.port,
                'database': self.config.database,
                'max_connections': self.config.max_connections,
                'health_check_interval': self.config.health_check_interval
            },
            'metrics': asdict(self.metrics),
            'last_health_check': asdict(self.last_health_check) if self.last_health_check else None,
            'current_retry_count': self.current_retry_count,
            'max_retries': self.max_retries
        }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        cache_hit_rate = 0.0
        if self.metrics.cache_hits + self.metrics.cache_misses > 0:
            cache_hit_rate = self.metrics.cache_hits / (self.metrics.cache_hits + self.metrics.cache_misses)
        
        success_rate = 0.0
        if self.metrics.total_operations > 0:
            success_rate = self.metrics.successful_operations / self.metrics.total_operations
        
        return {
            'total_operations': self.metrics.total_operations,
            'success_rate': success_rate,
            'cache_hit_rate': cache_hit_rate,
            'average_response_time_ms': self.metrics.average_response_time_ms,
            'connection_success_rate': (
                self.metrics.successful_connections / max(self.metrics.connection_attempts, 1)
            ),
            'recent_operation_times': self.operation_times[-10:] if self.operation_times else [],
            'uptime_seconds': (datetime.now() - self.start_time).total_seconds()
        }

    async def close_connection(self) -> None:
        """Gracefully close Redis connection and cleanup resources"""
        try:
            # Stop health monitoring
            self.health_check_enabled = False
            self.shutdown_event.set()
            
            if self.health_check_thread and self.health_check_thread.is_alive():
                self.health_check_thread.join(timeout=5)
            
            # Close Redis connection
            if self.redis_client:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.redis_client.close
                )
                self.redis_client = None
            
            # Close connection pool
            if self.connection_pool:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.connection_pool.disconnect
                )
                self.connection_pool = None
            
            self.connection_state = ConnectionState.DISCONNECTED
            self.connection_count = 0  # Reset connection count
            logger.info("✅ Redis connection closed gracefully")
            
        except Exception as e:
            logger.error(f"Error closing Redis connection: {str(e)}")

    def __del__(self):
        """Cleanup on destruction"""
        if hasattr(self, 'shutdown_event'):
            self.shutdown_event.set()

# Global persistent Redis manager instance
_redis_manager: Optional[PersistentRedisManager] = None

async def get_persistent_redis_manager() -> PersistentRedisManager:
    """Get or create global persistent Redis manager instance"""
    global _redis_manager
    
    if _redis_manager is None:
        _redis_manager = PersistentRedisManager()
        await _redis_manager.initialize_connection()
    
    return _redis_manager

async def close_persistent_redis_manager() -> None:
    """Close global persistent Redis manager"""
    global _redis_manager
    
    if _redis_manager:
        await _redis_manager.close_connection()
        _redis_manager = None

# Convenience functions for common operations
async def redis_get(key: str) -> Optional[str]:
    """Get value from persistent Redis connection"""
    manager = await get_persistent_redis_manager()
    return await manager.execute_operation(CacheOperation.GET, key=key)

async def redis_set(key: str, value: str, ttl: Optional[int] = None) -> bool:
    """Set value in persistent Redis connection"""
    manager = await get_persistent_redis_manager()
    return await manager.execute_operation(CacheOperation.SET, key=key, value=value, ttl=ttl)

async def redis_delete(key: str) -> int:
    """Delete key from persistent Redis connection"""
    manager = await get_persistent_redis_manager()
    return await manager.execute_operation(CacheOperation.DELETE, key=key)

async def redis_exists(key: str) -> bool:
    """Check if key exists in persistent Redis connection"""
    manager = await get_persistent_redis_manager()
    return await manager.execute_operation(CacheOperation.EXISTS, key=key)

async def main():
    """Test and demonstration of persistent Redis manager"""
    logger.info("Testing PersistentRedisManager...")
    
    try:
        # Initialize manager
        manager = PersistentRedisManager()
        success = await manager.initialize_connection()
        
        if success:
            logger.info("✅ Connection established")
            
            # Test operations
            await manager.execute_operation(CacheOperation.SET, key="test:key", value="test_value", ttl=60)
            result = await manager.execute_operation(CacheOperation.GET, key="test:key")
            logger.info(f"Test result: {result}")
            
            # Show status
            status = manager.get_connection_status()
            logger.info(f"Status: {json.dumps(status, indent=2, default=str)}")
            
        else:
            logger.error("❌ Connection failed")
            
    except Exception as e:
        logger.error(f"Test error: {str(e)}")
        
    finally:
        if 'manager' in locals():
            await manager.close_connection()

if __name__ == '__main__':
    asyncio.run(main()) 