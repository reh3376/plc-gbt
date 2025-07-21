#!/usr/bin/env python3
"""
🧠 Universal Memory Management System - AI Enhancement Framework

Generalized multi-database memory management system extracted from plc-gbt project.
Provides configurable memory tiers with intelligent routing and coordination.

Universal Features:
- Configurable memory tier architecture (short, medium, long-term, pattern matching)
- Provider-based database abstraction (Redis, Neo4j, PostgreSQL, Qdrant, etc.)
- Intelligent query routing based on data type and access patterns
- Multi-tier caching with automatic warming and invalidation
- Performance monitoring and optimization
- Extensible for any database technology

Author: AI Enhancement Framework (Phase 25)
Extracted from: plc-gbt Memory Management System  
Created: 2025-01-18
License: MIT
"""

import os
import sys
import json
import time
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Protocol, runtime_checkable
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Core Types and Interfaces
# ============================================================================

class MemoryTier(Enum):
    """Memory tier classification for intelligent data routing"""
    SHORT_TERM = "short_term"        # Fast access cache (Redis, in-memory)
    MEDIUM_TERM = "medium_term"      # Structured knowledge (Neo4j, graph databases)
    LONG_TERM = "long_term"          # Persistent storage (PostgreSQL, file systems)
    PATTERN_MATCHING = "pattern"     # Vector/similarity search (Qdrant, Pinecone)

class QueryStrategy(Enum):
    """Query routing strategies for optimization"""
    SPEED_OPTIMIZED = "speed"        # Prioritize fastest response
    ACCURACY_OPTIMIZED = "accuracy"  # Prioritize most comprehensive results
    COST_OPTIMIZED = "cost"          # Prioritize least resource usage
    BALANCED = "balanced"            # Balance speed, accuracy, and cost

@dataclass
class DatabaseConfig:
    """Universal database configuration"""
    provider_type: str              # e.g., "redis", "neo4j", "postgresql", "qdrant"
    connection_params: Dict[str, Any]
    tier: MemoryTier
    priority: int = 1               # Higher priority = preferred for tier
    enabled: bool = True
    max_connections: int = 10
    timeout_seconds: int = 30
    retry_attempts: int = 3

@dataclass
class QueryResult:
    """Universal query result"""
    success: bool
    data: Any
    metadata: Dict[str, Any]
    execution_time_ms: float
    source_tier: MemoryTier
    source_provider: str

@dataclass
class MemoryRequest:
    """Memory operation request"""
    operation: str                  # get, set, delete, search, etc.
    data_type: str                 # content, metadata, embedding, etc.
    tier_preference: Optional[MemoryTier] = None
    routing_strategy: QueryStrategy = QueryStrategy.BALANCED
    context: Dict[str, Any] = None

# ============================================================================
# Provider Interface
# ============================================================================

@runtime_checkable
class MemoryProvider(Protocol):
    """Universal interface for memory providers"""
    
    async def connect(self, config: DatabaseConfig) -> bool:
        """Establish connection to the provider"""
        ...
    
    async def disconnect(self) -> bool:
        """Close connection to the provider"""
        ...
    
    async def health_check(self) -> Dict[str, Any]:
        """Check provider health and performance"""
        ...
    
    async def execute_query(self, request: MemoryRequest) -> QueryResult:
        """Execute a memory operation"""
        ...
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities and supported operations"""
        ...
    
    def get_tier(self) -> MemoryTier:
        """Get the memory tier this provider serves"""
        ...

class BaseMemoryProvider(ABC):
    """Base implementation for memory providers"""
    
    def __init__(self, provider_name: str, tier: MemoryTier):
        self.provider_name = provider_name
        self.tier = tier
        self.connected = False
        self.connection = None
        self.stats = {
            "queries": 0,
            "errors": 0,
            "total_time_ms": 0.0,
            "last_health_check": None
        }
    
    @abstractmethod
    async def connect(self, config: DatabaseConfig) -> bool:
        """Establish connection to the provider"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Close connection to the provider"""
        pass
    
    @abstractmethod
    async def execute_query(self, request: MemoryRequest) -> QueryResult:
        """Execute a memory operation"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Base health check implementation"""
        if not self.connected:
            return {"healthy": False, "reason": "Not connected"}
        
        try:
            # Subclasses can override for specific health checks
            self.stats["last_health_check"] = datetime.now().isoformat()
            return {
                "healthy": True,
                "provider": self.provider_name,
                "tier": self.tier.value,
                "stats": self.stats
            }
        except Exception as e:
            return {"healthy": False, "reason": str(e)}
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Base capabilities - subclasses should override"""
        return {
            "provider": self.provider_name,
            "tier": self.tier.value,
            "operations": ["get", "set", "delete"],
            "data_types": ["text", "json"]
        }
    
    def get_tier(self) -> MemoryTier:
        """Get the memory tier this provider serves"""
        return self.tier

# ============================================================================
# Built-in Providers
# ============================================================================

class RedisMemoryProvider(BaseMemoryProvider):
    """Redis provider for short-term memory"""
    
    def __init__(self):
        super().__init__("redis", MemoryTier.SHORT_TERM)
        self.redis = None
    
    async def connect(self, config: DatabaseConfig) -> bool:
        """Connect to Redis"""
        try:
            # Import Redis if available
            import redis.asyncio as redis
            
            conn_params = config.connection_params
            self.redis = redis.Redis(
                host=conn_params.get('host', 'localhost'),
                port=conn_params.get('port', 6379),
                db=conn_params.get('db', 0),
                decode_responses=conn_params.get('decode_responses', True),
                socket_timeout=config.timeout_seconds
            )
            
            # Test connection
            await self.redis.ping()
            self.connected = True
            logger.info(f"✅ {self.provider_name} connected successfully")
            return True
            
        except ImportError:
            logger.warning("Redis library not available")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from Redis"""
        try:
            if self.redis:
                await self.redis.close()
            self.connected = False
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from Redis: {e}")
            return False
    
    async def execute_query(self, request: MemoryRequest) -> QueryResult:
        """Execute Redis operation"""
        start_time = time.time()
        
        try:
            if not self.connected:
                raise Exception("Redis not connected")
            
            result = None
            if request.operation == "get":
                key = request.context.get("key")
                result = await self.redis.get(key)
            elif request.operation == "set":
                key = request.context.get("key")
                value = request.context.get("value")
                ttl = request.context.get("ttl")
                if ttl:
                    result = await self.redis.setex(key, ttl, value)
                else:
                    result = await self.redis.set(key, value)
            elif request.operation == "delete":
                key = request.context.get("key")
                result = await self.redis.delete(key)
            
            execution_time = (time.time() - start_time) * 1000
            self.stats["queries"] += 1
            self.stats["total_time_ms"] += execution_time
            
            return QueryResult(
                success=True,
                data=result,
                metadata={"operation": request.operation},
                execution_time_ms=execution_time,
                source_tier=self.tier,
                source_provider=self.provider_name
            )
            
        except Exception as e:
            self.stats["errors"] += 1
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                success=False,
                data=None,
                metadata={"error": str(e)},
                execution_time_ms=execution_time,
                source_tier=self.tier,
                source_provider=self.provider_name
            )
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Redis capabilities"""
        return {
            "provider": self.provider_name,
            "tier": self.tier.value,
            "operations": ["get", "set", "delete", "exists", "keys", "expire"],
            "data_types": ["string", "hash", "list", "set", "zset"],
            "features": ["ttl", "pattern_matching", "pub_sub"]
        }

class InMemoryProvider(BaseMemoryProvider):
    """In-memory provider for testing and simple use cases"""
    
    def __init__(self):
        super().__init__("in_memory", MemoryTier.SHORT_TERM)
        self.data = {}
        self.expiry = {}
    
    async def connect(self, config: DatabaseConfig) -> bool:
        """Connect to in-memory storage"""
        self.connected = True
        logger.info(f"✅ {self.provider_name} initialized")
        return True
    
    async def disconnect(self) -> bool:
        """Disconnect from in-memory storage"""
        self.data.clear()
        self.expiry.clear()
        self.connected = False
        return True
    
    async def execute_query(self, request: MemoryRequest) -> QueryResult:
        """Execute in-memory operation"""
        start_time = time.time()
        
        try:
            self._cleanup_expired()
            
            result = None
            if request.operation == "get":
                key = request.context.get("key")
                result = self.data.get(key)
            elif request.operation == "set":
                key = request.context.get("key")
                value = request.context.get("value")
                ttl = request.context.get("ttl")
                self.data[key] = value
                if ttl:
                    self.expiry[key] = time.time() + ttl
            elif request.operation == "delete":
                key = request.context.get("key")
                result = self.data.pop(key, None) is not None
                self.expiry.pop(key, None)
            
            execution_time = (time.time() - start_time) * 1000
            self.stats["queries"] += 1
            self.stats["total_time_ms"] += execution_time
            
            return QueryResult(
                success=True,
                data=result,
                metadata={"operation": request.operation},
                execution_time_ms=execution_time,
                source_tier=self.tier,
                source_provider=self.provider_name
            )
            
        except Exception as e:
            self.stats["errors"] += 1
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                success=False,
                data=None,
                metadata={"error": str(e)},
                execution_time_ms=execution_time,
                source_tier=self.tier,
                source_provider=self.provider_name
            )
    
    def _cleanup_expired(self):
        """Remove expired keys"""
        current_time = time.time()
        expired_keys = [key for key, expiry in self.expiry.items() if expiry <= current_time]
        for key in expired_keys:
            self.data.pop(key, None)
            self.expiry.pop(key, None)

# ============================================================================
# Memory Manager
# ============================================================================

class UniversalMemoryManager:
    """
    Universal Memory Management System
    
    Coordinates operations across multiple memory tiers and providers
    with intelligent routing and performance optimization.
    
    Features:
    - Multi-tier memory architecture
    - Provider-based database abstraction
    - Intelligent query routing
    - Performance monitoring
    - Automatic failover and recovery
    - Extensible provider architecture
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the universal memory manager"""
        self.session_id = f"memory_mgr_{int(time.time())}"
        self.start_time = datetime.now()
        
        # Provider management
        self.providers: Dict[str, MemoryProvider] = {}
        self.tier_providers: Dict[MemoryTier, List[MemoryProvider]] = {
            tier: [] for tier in MemoryTier
        }
        
        # Configuration
        self.configs: Dict[str, DatabaseConfig] = {}
        
        # Performance tracking
        self.stats = {
            "queries": 0,
            "cache_hits": 0,
            "errors": 0,
            "total_time_ms": 0.0
        }
        
        # Health monitoring
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.last_health_check = datetime.now()
        
        # Load configuration
        self._load_configuration(config_file)
        
        # Initialize built-in providers
        self._register_builtin_providers()
        
        logger.info(f"UniversalMemoryManager initialized: {self.session_id}")
    
    def _load_configuration(self, config_file: Optional[str] = None):
        """Load memory management configuration"""
        if config_file and Path(config_file).exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                self._parse_config(config_data)
            except Exception as e:
                logger.error(f"Failed to load config file: {e}")
                self._load_default_config()
        else:
            self._load_default_config()
    
    def _load_default_config(self):
        """Load default configuration"""
        self.configs = {
            "in_memory": DatabaseConfig(
                provider_type="in_memory",
                connection_params={},
                tier=MemoryTier.SHORT_TERM,
                enabled=True
            )
        }
        logger.info("Loaded default in-memory configuration")
    
    def _parse_config(self, config_data: Dict[str, Any]):
        """Parse configuration data"""
        providers_config = config_data.get("providers", {})
        
        for name, provider_config in providers_config.items():
            self.configs[name] = DatabaseConfig(
                provider_type=provider_config["type"],
                connection_params=provider_config.get("connection", {}),
                tier=MemoryTier(provider_config["tier"]),
                priority=provider_config.get("priority", 1),
                enabled=provider_config.get("enabled", True),
                max_connections=provider_config.get("max_connections", 10),
                timeout_seconds=provider_config.get("timeout", 30),
                retry_attempts=provider_config.get("retries", 3)
            )
    
    def _register_builtin_providers(self):
        """Register built-in provider types"""
        self.provider_factories = {
            "redis": RedisMemoryProvider,
            "in_memory": InMemoryProvider
        }
    
    async def initialize(self):
        """Initialize all configured providers"""
        for name, config in self.configs.items():
            if config.enabled:
                await self.add_provider(name, config)
    
    async def add_provider(self, name: str, config: DatabaseConfig) -> bool:
        """Add and initialize a memory provider"""
        try:
            # Create provider instance
            if config.provider_type in self.provider_factories:
                provider = self.provider_factories[config.provider_type]()
            else:
                logger.error(f"Unknown provider type: {config.provider_type}")
                return False
            
            # Connect provider
            if await provider.connect(config):
                self.providers[name] = provider
                self.tier_providers[config.tier].append(provider)
                logger.info(f"✅ Provider '{name}' added to tier {config.tier.value}")
                return True
            else:
                logger.error(f"Failed to connect provider '{name}'")
                return False
                
        except Exception as e:
            logger.error(f"Error adding provider '{name}': {e}")
            return False
    
    def register_provider_factory(self, provider_type: str, factory_class):
        """Register a custom provider factory"""
        self.provider_factories[provider_type] = factory_class
        logger.info(f"Registered custom provider factory: {provider_type}")
    
    async def execute_request(self, request: MemoryRequest) -> QueryResult:
        """Execute a memory request with intelligent routing"""
        start_time = time.time()
        
        try:
            # Determine target providers
            providers = self._route_request(request)
            
            if not providers:
                raise Exception("No suitable providers available")
            
            # Try providers in order of preference
            for provider in providers:
                try:
                    result = await provider.execute_query(request)
                    
                    # Update statistics
                    self.stats["queries"] += 1
                    if result.success:
                        execution_time = (time.time() - start_time) * 1000
                        self.stats["total_time_ms"] += execution_time
                        return result
                    
                except Exception as e:
                    logger.warning(f"Provider {provider.provider_name} failed: {e}")
                    continue
            
            # All providers failed
            raise Exception("All providers failed")
            
        except Exception as e:
            self.stats["errors"] += 1
            execution_time = (time.time() - start_time) * 1000
            
            return QueryResult(
                success=False,
                data=None,
                metadata={"error": str(e)},
                execution_time_ms=execution_time,
                source_tier=MemoryTier.SHORT_TERM,  # Default
                source_provider="unknown"
            )
    
    def _route_request(self, request: MemoryRequest) -> List[MemoryProvider]:
        """Route request to appropriate providers based on strategy"""
        if request.tier_preference:
            # Use specific tier
            providers = self.tier_providers.get(request.tier_preference, [])
        else:
            # Auto-route based on strategy
            if request.routing_strategy == QueryStrategy.SPEED_OPTIMIZED:
                # Prefer short-term memory
                providers = (self.tier_providers[MemoryTier.SHORT_TERM] + 
                           self.tier_providers[MemoryTier.MEDIUM_TERM])
            elif request.routing_strategy == QueryStrategy.ACCURACY_OPTIMIZED:
                # Prefer long-term and structured memory
                providers = (self.tier_providers[MemoryTier.LONG_TERM] + 
                           self.tier_providers[MemoryTier.MEDIUM_TERM])
            else:  # BALANCED or COST_OPTIMIZED
                # Try all tiers
                providers = []
                for tier in MemoryTier:
                    providers.extend(self.tier_providers[tier])
        
        # Filter connected providers
        return [p for p in providers if hasattr(p, 'connected') and p.connected]
    
    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all providers"""
        health_results = {}
        
        for name, provider in self.providers.items():
            try:
                health_results[name] = await provider.health_check()
            except Exception as e:
                health_results[name] = {"healthy": False, "error": str(e)}
        
        self.health_status = health_results
        self.last_health_check = datetime.now()
        
        return health_results
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        await self.health_check_all()
        
        provider_stats = {}
        for name, provider in self.providers.items():
            if hasattr(provider, 'stats'):
                provider_stats[name] = provider.stats
        
        return {
            "session_id": self.session_id,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "global_stats": self.stats,
            "provider_stats": provider_stats,
            "health_status": self.health_status,
            "tier_distribution": {
                tier.value: len(providers) 
                for tier, providers in self.tier_providers.items()
            }
        }
    
    async def cleanup(self):
        """Clean up all providers and connections"""
        for name, provider in self.providers.items():
            try:
                await provider.disconnect()
                logger.info(f"Disconnected provider: {name}")
            except Exception as e:
                logger.error(f"Error disconnecting {name}: {e}")
        
        self.providers.clear()
        for tier_list in self.tier_providers.values():
            tier_list.clear()

# ============================================================================
# Convenience Functions
# ============================================================================

def create_memory_manager(config_file: Optional[str] = None) -> UniversalMemoryManager:
    """Factory function to create a memory manager"""
    return UniversalMemoryManager(config_file)

async def create_default_memory_manager() -> UniversalMemoryManager:
    """Create and initialize a memory manager with default configuration"""
    manager = UniversalMemoryManager()
    await manager.initialize()
    return manager

# Example configuration format
EXAMPLE_CONFIG = {
    "providers": {
        "redis_cache": {
            "type": "redis",
            "tier": "short_term",
            "connection": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "enabled": True,
            "priority": 1
        },
        "backup_memory": {
            "type": "in_memory", 
            "tier": "short_term",
            "connection": {},
            "enabled": True,
            "priority": 2
        }
    }
}

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create and initialize memory manager
        manager = await create_default_memory_manager()
        
        # Test basic operations
        set_request = MemoryRequest(
            operation="set",
            data_type="string",
            context={"key": "test_key", "value": "test_value"}
        )
        
        get_request = MemoryRequest(
            operation="get", 
            data_type="string",
            context={"key": "test_key"}
        )
        
        # Execute operations
        set_result = await manager.execute_request(set_request)
        print(f"Set result: {set_result.success}")
        
        get_result = await manager.execute_request(get_request)
        print(f"Get result: {get_result.data}")
        
        # Get statistics
        stats = await manager.get_stats()
        print(f"Stats: {stats}")
        
        # Cleanup
        await manager.cleanup()
    
    asyncio.run(main()) 