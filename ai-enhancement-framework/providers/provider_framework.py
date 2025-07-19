#!/usr/bin/env python3
"""
🔌 Universal Provider Framework - AI Enhancement Framework

Generalized modular provider abstraction system extracted from plc-gbt project.
Provides a unified interface for integrating any type of service provider including
databases, APIs, AI services, cloud services, and custom integrations.

Universal Features:
- Provider abstraction with unified interface
- Health monitoring and circuit breaker patterns
- Connection pooling and lifecycle management
- Configuration management with environment support
- Performance metrics and monitoring
- Retry patterns and error handling
- Extensible for any service type

Author: AI Enhancement Framework (Phase 25)
Extracted from: plc-gbt Provider Abstraction System
Created: 2025-01-18
License: MIT
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Protocol, TypeVar, Generic, runtime_checkable
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
import uuid
import hashlib
import weakref

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')

# ============================================================================
# Core Types and Enums
# ============================================================================

class ProviderType(Enum):
    """Universal provider types"""
    DATABASE = "database"
    API = "api"
    AI_SERVICE = "ai_service"
    CLOUD_SERVICE = "cloud_service"
    FILE_SYSTEM = "file_system"
    MESSAGE_QUEUE = "message_queue"
    CACHE = "cache"
    CUSTOM = "custom"

class OperationType(Enum):
    """Universal operation types"""
    READ = "read"
    WRITE = "write" 
    UPDATE = "update"
    DELETE = "delete"
    SEARCH = "search"
    EXECUTE = "execute"
    STREAM = "stream"
    BATCH = "batch"
    HEALTH_CHECK = "health_check"

class HealthStatus(Enum):
    """Provider health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

class CircuitBreakerState(Enum):
    """Circuit breaker states for resilience"""
    CLOSED = "closed"         # Normal operation
    OPEN = "open"             # Failing, reject requests
    HALF_OPEN = "half_open"   # Testing if service recovered

@dataclass
class ProviderConfig:
    """Universal provider configuration"""
    provider_type: ProviderType
    provider_name: str
    endpoint: Optional[str] = None  # URL, host:port, file path, etc.
    credentials: Optional[Dict[str, Any]] = None
    connection_params: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: int = 30
    max_connections: int = 10
    retry_attempts: int = 3
    retry_delay_seconds: float = 1.0
    health_check_interval_seconds: int = 60
    circuit_breaker_config: Optional[Dict[str, Any]] = None
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ProviderMetrics:
    """Provider performance metrics"""
    operation_count: int = 0
    total_duration_ms: float = 0.0
    error_count: int = 0
    last_operation_time: Optional[datetime] = None
    last_error_time: Optional[datetime] = None
    health_status: HealthStatus = HealthStatus.UNKNOWN
    connection_count: int = 0
    bytes_transferred: int = 0
    
    @property
    def average_duration_ms(self) -> float:
        """Calculate average operation duration"""
        return self.total_duration_ms / self.operation_count if self.operation_count > 0 else 0.0
    
    @property
    def error_rate(self) -> float:
        """Calculate error rate percentage"""
        return (self.error_count / self.operation_count * 100) if self.operation_count > 0 else 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        return 100.0 - self.error_rate

@dataclass
class OperationRequest:
    """Universal operation request"""
    operation_type: OperationType
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout_override: Optional[int] = None
    retry_override: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class OperationResult:
    """Universal operation result"""
    success: bool
    data: Optional[Any] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None
    duration_ms: float = 0.0
    operation_type: Optional[OperationType] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    provider_name: Optional[str] = None

class CircuitBreaker:
    """Circuit breaker for provider resilience"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitBreakerState.CLOSED
        self.lock = threading.RLock()
    
    def record_success(self):
        """Record successful operation"""
        with self.lock:
            self.failure_count = 0
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                logger.info("Circuit breaker closed - service recovered")
    
    def record_failure(self):
        """Record failed operation"""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            
            if self.failure_count >= self.failure_threshold and self.state == CircuitBreakerState.CLOSED:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if operation can be executed"""
        with self.lock:
            if self.state == CircuitBreakerState.CLOSED:
                return True
            
            if self.state == CircuitBreakerState.OPEN:
                if self.last_failure_time and \
                   (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout_seconds:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info("Circuit breaker half-open - testing service recovery")
                    return True
                return False
            
            return True  # HALF_OPEN state
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        with self.lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
                "failure_threshold": self.failure_threshold,
                "recovery_timeout_seconds": self.recovery_timeout_seconds
            }

# ============================================================================
# Provider Interface
# ============================================================================

@runtime_checkable
class Provider(Protocol):
    """Universal provider interface"""
    
    async def initialize(self) -> bool:
        """Initialize the provider"""
        ...
    
    async def execute_operation(self, request: OperationRequest) -> OperationResult:
        """Execute an operation"""
        ...
    
    async def health_check(self) -> HealthStatus:
        """Check provider health"""
        ...
    
    async def cleanup(self):
        """Clean up provider resources"""
        ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities"""
        ...
    
    def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics"""
        ...

class BaseProvider(ABC):
    """Base implementation for all providers"""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.metrics = ProviderMetrics()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config.circuit_breaker_config.get('failure_threshold', 5) if config.circuit_breaker_config else 5,
            recovery_timeout_seconds=config.circuit_breaker_config.get('recovery_timeout', 60) if config.circuit_breaker_config else 60
        )
        self.connection = None
        self.connection_pool = None
        self.lock = threading.RLock()
        self.health_check_task: Optional[asyncio.Task] = None
        self.shutdown_event = threading.Event()
        self.initialized = False
        
        logger.info(f"{self.__class__.__name__} provider created: {config.provider_name}")
    
    @abstractmethod
    async def _connect(self) -> bool:
        """Establish connection to the provider"""
        pass
    
    @abstractmethod
    async def _disconnect(self):
        """Close connection to the provider"""
        pass
    
    @abstractmethod
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Implementation-specific operation execution"""
        pass
    
    @abstractmethod
    async def _health_check_impl(self) -> HealthStatus:
        """Implementation-specific health check"""
        pass
    
    async def initialize(self) -> bool:
        """Initialize the provider"""
        if self.initialized:
            return True
        
        try:
            success = await self._connect()
            if success:
                self.initialized = True
                await self.start_health_monitoring()
                logger.info(f"Provider {self.config.provider_name} initialized successfully")
            return success
        except Exception as e:
            logger.error(f"Failed to initialize provider {self.config.provider_name}: {e}")
            return False
    
    async def execute_operation(self, request: OperationRequest) -> OperationResult:
        """Execute operation with circuit breaker and retry logic"""
        if not self.initialized:
            return OperationResult(
                success=False,
                error_message="Provider not initialized",
                error_code="NOT_INITIALIZED",
                provider_name=self.config.provider_name
            )
        
        return await self._execute_with_circuit_breaker(request)
    
    async def health_check(self) -> HealthStatus:
        """Check provider health"""
        if not self.initialized:
            return HealthStatus.UNAVAILABLE
        
        try:
            status = await self._health_check_impl()
            self.metrics.health_status = status
            return status
        except Exception as e:
            logger.error(f"Health check failed for {self.config.provider_name}: {e}")
            self.metrics.health_status = HealthStatus.UNKNOWN
            return HealthStatus.UNKNOWN
    
    async def cleanup(self):
        """Clean up provider resources"""
        self.shutdown_event.set()
        
        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass
        
        try:
            await self._disconnect()
            self.initialized = False
            logger.info(f"Provider {self.config.provider_name} cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup for {self.config.provider_name}: {e}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities - override in subclasses"""
        return {
            "provider_type": self.config.provider_type.value,
            "provider_name": self.config.provider_name,
            "operations": ["read", "write"],  # Default operations
            "features": []
        }
    
    def get_metrics(self) -> ProviderMetrics:
        """Get provider metrics"""
        return self.metrics
    
    async def _execute_with_circuit_breaker(self, request: OperationRequest) -> OperationResult:
        """Execute operation with circuit breaker pattern"""
        if not self.circuit_breaker.can_execute():
            return OperationResult(
                success=False,
                error_message="Circuit breaker open - service unavailable",
                error_code="CIRCUIT_BREAKER_OPEN",
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
        
        # Retry logic
        max_retries = request.retry_override or self.config.retry_attempts
        last_exception = None
        
        for attempt in range(max_retries + 1):
            start_time = time.time()
            
            try:
                result = await self._execute_operation_impl(request)
                duration_ms = (time.time() - start_time) * 1000
                
                if result.success:
                    self.circuit_breaker.record_success()
                    self._update_metrics(True, duration_ms, len(str(result.data)) if result.data else 0)
                else:
                    self.circuit_breaker.record_failure()
                    self._update_metrics(False, duration_ms, 0)
                
                result.duration_ms = duration_ms
                result.provider_name = self.config.provider_name
                return result
                
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                last_exception = e
                
                if attempt < max_retries:
                    delay = self.config.retry_delay_seconds * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries + 1}) for {self.config.provider_name}: {e}. Retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    self.circuit_breaker.record_failure()
                    self._update_metrics(False, duration_ms, 0)
                    
                    logger.error(f"Operation failed after {max_retries + 1} attempts for {self.config.provider_name}: {e}")
                    return OperationResult(
                        success=False,
                        error_message=str(e),
                        error_code="OPERATION_FAILED",
                        duration_ms=duration_ms,
                        operation_type=request.operation_type,
                        provider_name=self.config.provider_name
                    )
        
        # Should not reach here, but just in case
        return OperationResult(
            success=False,
            error_message=str(last_exception) if last_exception else "Unknown error",
            error_code="UNKNOWN_ERROR",
            operation_type=request.operation_type,
            provider_name=self.config.provider_name
        )
    
    def _update_metrics(self, success: bool, duration_ms: float, bytes_transferred: int = 0):
        """Update provider metrics"""
        with self.lock:
            self.metrics.operation_count += 1
            self.metrics.total_duration_ms += duration_ms
            self.metrics.last_operation_time = datetime.now()
            self.metrics.bytes_transferred += bytes_transferred
            
            if not success:
                self.metrics.error_count += 1
                self.metrics.last_error_time = datetime.now()
    
    async def start_health_monitoring(self):
        """Start background health monitoring"""
        if self.health_check_task:
            return  # Already started
        
        async def health_monitor():
            while not self.shutdown_event.is_set():
                try:
                    await self.health_check()
                    await asyncio.sleep(self.config.health_check_interval_seconds)
                except Exception as e:
                    logger.error(f"Health monitoring error for {self.config.provider_name}: {e}")
                    await asyncio.sleep(5)  # Shorter interval on error
        
        self.health_check_task = asyncio.create_task(health_monitor())

# ============================================================================
# Built-in Provider Implementations
# ============================================================================

class HttpApiProvider(BaseProvider):
    """HTTP API provider for REST services"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.session = None
    
    async def _connect(self) -> bool:
        """Initialize HTTP session"""
        try:
            import aiohttp
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            self.session = aiohttp.ClientSession(timeout=timeout)
            return True
        except ImportError:
            logger.error("aiohttp library not available for HttpApiProvider")
            return False
        except Exception as e:
            logger.error(f"Failed to create HTTP session: {e}")
            return False
    
    async def _disconnect(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute HTTP operation"""
        if not self.session:
            raise Exception("HTTP session not initialized")
        
        method = self._map_operation_to_http_method(request.operation_type)
        url = request.parameters.get('url') or self.config.endpoint
        headers = request.parameters.get('headers', {})
        data = request.parameters.get('data')
        params = request.parameters.get('params')
        
        if not url:
            raise Exception("No URL specified for HTTP request")
        
        async with self.session.request(method, url, headers=headers, json=data, params=params) as response:
            result_data = await response.text()
            
            if response.status >= 200 and response.status < 300:
                return OperationResult(
                    success=True,
                    data=result_data,
                    operation_type=request.operation_type,
                    metadata={"status_code": response.status, "headers": dict(response.headers)}
                )
            else:
                return OperationResult(
                    success=False,
                    error_message=f"HTTP {response.status}: {result_data}",
                    error_code=str(response.status),
                    operation_type=request.operation_type
                )
    
    async def _health_check_impl(self) -> HealthStatus:
        """Check HTTP service health"""
        if not self.session:
            return HealthStatus.UNAVAILABLE
        
        try:
            health_url = self.config.connection_params.get('health_endpoint') or f"{self.config.endpoint}/health"
            
            async with self.session.get(health_url) as response:
                if response.status == 200:
                    return HealthStatus.HEALTHY
                else:
                    return HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def _map_operation_to_http_method(self, operation_type: OperationType) -> str:
        """Map operation type to HTTP method"""
        mapping = {
            OperationType.READ: 'GET',
            OperationType.WRITE: 'POST',
            OperationType.UPDATE: 'PUT',
            OperationType.DELETE: 'DELETE',
            OperationType.SEARCH: 'GET',
            OperationType.EXECUTE: 'POST'
        }
        return mapping.get(operation_type, 'GET')
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get HTTP provider capabilities"""
        return {
            "provider_type": self.config.provider_type.value,
            "provider_name": self.config.provider_name,
            "operations": ["read", "write", "update", "delete", "search", "execute"],
            "features": ["http_methods", "headers", "authentication", "timeout"]
        }

class FileSystemProvider(BaseProvider):
    """File system provider for local/remote file operations"""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.base_path = Path(config.endpoint or ".")
    
    async def _connect(self) -> bool:
        """Initialize file system access"""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to initialize file system provider: {e}")
            return False
    
    async def _disconnect(self):
        """No explicit disconnect needed for file system"""
        pass
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute file system operation"""
        file_path = self.base_path / request.parameters.get('path', '')
        
        if request.operation_type == OperationType.READ:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return OperationResult(
                    success=True,
                    data=content,
                    operation_type=request.operation_type,
                    metadata={"file_size": len(content), "path": str(file_path)}
                )
            except Exception as e:
                return OperationResult(
                    success=False,
                    error_message=str(e),
                    operation_type=request.operation_type
                )
        
        elif request.operation_type == OperationType.WRITE:
            try:
                content = request.parameters.get('content', '')
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return OperationResult(
                    success=True,
                    data={"bytes_written": len(content)},
                    operation_type=request.operation_type,
                    metadata={"path": str(file_path)}
                )
            except Exception as e:
                return OperationResult(
                    success=False,
                    error_message=str(e),
                    operation_type=request.operation_type
                )
        
        elif request.operation_type == OperationType.DELETE:
            try:
                if file_path.exists():
                    file_path.unlink()
                    return OperationResult(
                        success=True,
                        data={"deleted": str(file_path)},
                        operation_type=request.operation_type
                    )
                else:
                    return OperationResult(
                        success=False,
                        error_message="File not found",
                        error_code="FILE_NOT_FOUND",
                        operation_type=request.operation_type
                    )
            except Exception as e:
                return OperationResult(
                    success=False,
                    error_message=str(e),
                    operation_type=request.operation_type
                )
        
        else:
            return OperationResult(
                success=False,
                error_message=f"Operation {request.operation_type} not supported",
                error_code="OPERATION_NOT_SUPPORTED",
                operation_type=request.operation_type
            )
    
    async def _health_check_impl(self) -> HealthStatus:
        """Check file system health"""
        try:
            test_file = self.base_path / ".health_check"
            test_file.write_text("test")
            test_file.unlink()
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get file system provider capabilities"""
        return {
            "provider_type": self.config.provider_type.value,
            "provider_name": self.config.provider_name,
            "operations": ["read", "write", "delete"],
            "features": ["local_files", "directory_operations", "text_encoding"]
        }

# ============================================================================
# Provider Manager
# ============================================================================

class ProviderManager:
    """
    Universal Provider Manager
    
    Manages multiple providers with unified interface, health monitoring,
    and intelligent routing based on provider capabilities and health.
    
    Features:
    - Multi-provider management
    - Health monitoring and failover
    - Performance metrics aggregation
    - Configuration management
    - Provider discovery and registration
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize provider manager"""
        self.providers: Dict[str, Provider] = {}
        self.provider_configs: Dict[str, ProviderConfig] = {}
        self.provider_factories: Dict[str, Callable[[ProviderConfig], Provider]] = {}
        
        # Register built-in providers
        self._register_builtin_providers()
        
        # Load configuration
        if config_file:
            self.load_configuration(config_file)
        
        logger.info("ProviderManager initialized")
    
    def _register_builtin_providers(self):
        """Register built-in provider factories"""
        self.provider_factories.update({
            "http_api": HttpApiProvider,
            "file_system": FileSystemProvider
        })
    
    def register_provider_factory(self, provider_type: str, factory: Callable[[ProviderConfig], Provider]):
        """Register a custom provider factory"""
        self.provider_factories[provider_type] = factory
        logger.info(f"Registered provider factory: {provider_type}")
    
    async def add_provider(self, config: ProviderConfig) -> bool:
        """Add and initialize a provider"""
        if config.provider_name in self.providers:
            logger.warning(f"Provider {config.provider_name} already exists")
            return False
        
        # Find appropriate factory
        factory = None
        for factory_name, factory_func in self.provider_factories.items():
            if factory_name in config.metadata.get('factory_type', factory_name):
                factory = factory_func
                break
        
        if not factory:
            logger.error(f"No factory found for provider type: {config.provider_type}")
            return False
        
        try:
            # Create and initialize provider
            provider = factory(config)
            success = await provider.initialize()
            
            if success:
                self.providers[config.provider_name] = provider
                self.provider_configs[config.provider_name] = config
                logger.info(f"Provider {config.provider_name} added successfully")
                return True
            else:
                logger.error(f"Failed to initialize provider {config.provider_name}")
                return False
        
        except Exception as e:
            logger.error(f"Error adding provider {config.provider_name}: {e}")
            return False
    
    async def remove_provider(self, provider_name: str) -> bool:
        """Remove and cleanup a provider"""
        if provider_name not in self.providers:
            return False
        
        try:
            provider = self.providers[provider_name]
            await provider.cleanup()
            
            del self.providers[provider_name]
            del self.provider_configs[provider_name]
            
            logger.info(f"Provider {provider_name} removed")
            return True
        
        except Exception as e:
            logger.error(f"Error removing provider {provider_name}: {e}")
            return False
    
    async def execute_operation(self, provider_name: str, request: OperationRequest) -> OperationResult:
        """Execute operation on specific provider"""
        if provider_name not in self.providers:
            return OperationResult(
                success=False,
                error_message=f"Provider {provider_name} not found",
                error_code="PROVIDER_NOT_FOUND",
                operation_type=request.operation_type
            )
        
        provider = self.providers[provider_name]
        return await provider.execute_operation(request)
    
    async def execute_operation_any(self, request: OperationRequest, provider_filter: Optional[Callable[[Provider], bool]] = None) -> OperationResult:
        """Execute operation on first available healthy provider"""
        available_providers = []
        
        for name, provider in self.providers.items():
            if provider_filter and not provider_filter(provider):
                continue
            
            health = await provider.health_check()
            if health in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
                available_providers.append((name, provider))
        
        if not available_providers:
            return OperationResult(
                success=False,
                error_message="No healthy providers available",
                error_code="NO_PROVIDERS_AVAILABLE",
                operation_type=request.operation_type
            )
        
        # Try providers in order
        for name, provider in available_providers:
            result = await provider.execute_operation(request)
            if result.success:
                return result
        
        return OperationResult(
            success=False,
            error_message="All providers failed",
            error_code="ALL_PROVIDERS_FAILED",
            operation_type=request.operation_type
        )
    
    async def health_check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all providers"""
        health_results = {}
        
        for name, provider in self.providers.items():
            try:
                health_results[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                health_results[name] = HealthStatus.UNKNOWN
        
        return health_results
    
    def get_metrics_all(self) -> Dict[str, ProviderMetrics]:
        """Get metrics for all providers"""
        return {name: provider.get_metrics() for name, provider in self.providers.items()}
    
    def get_capabilities_all(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities for all providers"""
        return {name: provider.get_capabilities() for name, provider in self.providers.items()}
    
    def load_configuration(self, config_file: str):
        """Load provider configuration from file"""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            providers_config = config_data.get('providers', {})
            
            for name, provider_config in providers_config.items():
                config = ProviderConfig(
                    provider_type=ProviderType(provider_config['type']),
                    provider_name=name,
                    endpoint=provider_config.get('endpoint'),
                    credentials=provider_config.get('credentials'),
                    connection_params=provider_config.get('connection_params', {}),
                    timeout_seconds=provider_config.get('timeout_seconds', 30),
                    max_connections=provider_config.get('max_connections', 10),
                    retry_attempts=provider_config.get('retry_attempts', 3),
                    retry_delay_seconds=provider_config.get('retry_delay_seconds', 1.0),
                    health_check_interval_seconds=provider_config.get('health_check_interval_seconds', 60),
                    circuit_breaker_config=provider_config.get('circuit_breaker'),
                    enabled=provider_config.get('enabled', True),
                    metadata=provider_config.get('metadata', {})
                )
                
                self.provider_configs[name] = config
            
            logger.info(f"Loaded configuration for {len(self.provider_configs)} providers")
        
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
    
    async def initialize_all(self):
        """Initialize all configured providers"""
        for name, config in self.provider_configs.items():
            if config.enabled:
                await self.add_provider(config)
    
    async def cleanup_all(self):
        """Clean up all providers"""
        for name in list(self.providers.keys()):
            await self.remove_provider(name)

# ============================================================================
# Convenience Functions  
# ============================================================================

def create_provider_manager(config_file: Optional[str] = None) -> ProviderManager:
    """Factory function to create a provider manager"""
    return ProviderManager(config_file)

async def create_configured_provider_manager(config_file: str) -> ProviderManager:
    """Create and initialize a provider manager with configuration"""
    manager = ProviderManager(config_file)
    await manager.initialize_all()
    return manager

# Example configuration format
EXAMPLE_CONFIG = {
    "providers": {
        "web_api": {
            "type": "api",
            "endpoint": "https://api.example.com",
            "credentials": {
                "api_key": "your_api_key"
            },
            "timeout_seconds": 30,
            "enabled": True,
            "metadata": {
                "factory_type": "http_api"
            }
        },
        "local_storage": {
            "type": "file_system",
            "endpoint": "./data",
            "enabled": True,
            "metadata": {
                "factory_type": "file_system"
            }
        }
    }
}

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create provider manager
        manager = create_provider_manager()
        
        # Add file system provider
        fs_config = ProviderConfig(
            provider_type=ProviderType.FILE_SYSTEM,
            provider_name="local_files",
            endpoint="./test_data",
            metadata={"factory_type": "file_system"}
        )
        
        await manager.add_provider(fs_config)
        
        # Test file operations
        write_request = OperationRequest(
            operation_type=OperationType.WRITE,
            parameters={
                "path": "test.txt",
                "content": "Hello, Universal Provider Framework!"
            }
        )
        
        read_request = OperationRequest(
            operation_type=OperationType.READ,
            parameters={"path": "test.txt"}
        )
        
        # Execute operations
        write_result = await manager.execute_operation("local_files", write_request)
        print(f"Write result: {write_result.success}")
        
        read_result = await manager.execute_operation("local_files", read_request)
        print(f"Read result: {read_result.data}")
        
        # Get metrics
        metrics = manager.get_metrics_all()
        print(f"Metrics: {metrics}")
        
        # Cleanup
        await manager.cleanup_all()
    
    asyncio.run(main()) 