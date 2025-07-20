#!/usr/bin/env python3
"""
AI Enhancement Framework - Modular Provider Abstraction Layer
============================================================

Modular provider layer abstraction for unified database access patterns.
Extracted from Phase 17.3.2 implementation with enhanced framework integration.

Components:
1. Abstract Database Provider Interface - Unified database access patterns
2. Redis Provider Implementation - Cache operations with connection pooling
3. Neo4j Provider Implementation - Graph operations with transaction management
4. PostgreSQL Provider Implementation - Relational operations with connection pooling
5. Qdrant Provider Implementation - Vector operations with batch processing
6. Provider Factory Pattern - Dynamic provider instantiation and management
7. Provider Health Monitoring - Health checks and automatic failover
8. Configuration Management - Provider-specific configuration handling
9. Connection Lifecycle Management - Resource management and cleanup
10. Error Handling and Resilience - Retry patterns and circuit breakers

Author: AI Enhancement Framework
Extracted from: Phase 17.3.2 PLC-GBT Implementation
Version: 1.0.0
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
from typing import Dict, List, Any, Optional, Union, Tuple, Callable, Protocol, TypeVar, Generic
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
import uuid
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed
import weakref

# Database imports with availability checking
try:
    from neo4j import GraphDatabase, basic_auth, AsyncGraphDatabase
    from neo4j.exceptions import ServiceUnavailable, TransientError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import psycopg2
    import psycopg2.pool
    from psycopg2.extras import RealDictCursor
    from psycopg2 import sql, OperationalError, InterfaceError
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    from qdrant_client import QdrantClient, AsyncQdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition
    from qdrant_client.http.exceptions import ResponseHandlingException
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import redis
    import redis.asyncio as aioredis
    from redis.exceptions import ConnectionError, TimeoutError, RedisError
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Framework imports
from .provider_framework import (
    Provider, BaseProvider, ProviderConfig, ProviderType, OperationType,
    OperationRequest, OperationResult, HealthStatus, ProviderMetrics
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Type definitions
T = TypeVar('T')
ProviderResult = Dict[str, Any]
ConnectionConfig = Dict[str, Any]

class DatabaseType(Enum):
    """Supported database types"""
    REDIS = "redis"
    NEO4J = "neo4j"
    POSTGRESQL = "postgresql"
    QDRANT = "qdrant"

class ConnectionStatus(Enum):
    """Connection status tracking"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

@dataclass
class DatabaseProviderConfig(ProviderConfig):
    """Extended configuration for database providers"""
    database_type: DatabaseType = DatabaseType.REDIS
    host: str = "localhost"
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    database: Optional[str] = None
    ssl_enabled: bool = False
    ssl_config: Optional[Dict[str, Any]] = field(default_factory=dict)
    pool_size: int = 10
    pool_timeout: int = 30
    connection_timeout: int = 30
    query_timeout: int = 300
    auto_reconnect: bool = True
    reconnect_attempts: int = 3
    reconnect_delay: float = 1.0

class AbstractDatabaseProvider(BaseProvider):
    """Abstract base class for database providers"""
    
    def __init__(self, config: DatabaseProviderConfig):
        super().__init__(config)
        self.db_config = config
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.connection_pool = None
        self.active_connections = set()
        self.connection_lock = threading.RLock()
        self.last_connection_attempt = None
        self.connection_errors = []
        
    @abstractmethod
    async def _create_connection(self) -> Any:
        """Create a new database connection"""
        pass
    
    @abstractmethod
    async def _create_connection_pool(self) -> Any:
        """Create connection pool"""
        pass
    
    @abstractmethod
    async def _test_connection(self, connection: Any) -> bool:
        """Test if connection is valid"""
        pass
    
    @abstractmethod
    async def _close_connection(self, connection: Any):
        """Close a database connection"""
        pass
    
    @abstractmethod
    async def _execute_query(self, connection: Any, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute database query"""
        pass
    
    async def _connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection_status = ConnectionStatus.CONNECTING
            self.last_connection_attempt = datetime.now()
            
            if self.db_config.pool_size > 1:
                self.connection_pool = await self._create_connection_pool()
            else:
                self.connection = await self._create_connection()
            
            # Test connection
            if self.connection_pool:
                test_conn = await self._get_connection()
                is_valid = await self._test_connection(test_conn)
                await self._return_connection(test_conn)
            else:
                is_valid = await self._test_connection(self.connection)
            
            if is_valid:
                self.connection_status = ConnectionStatus.CONNECTED
                logger.info(f"Database provider {self.config.provider_name} connected successfully")
                return True
            else:
                self.connection_status = ConnectionStatus.ERROR
                return False
                
        except Exception as e:
            self.connection_status = ConnectionStatus.ERROR
            self.connection_errors.append(f"{datetime.now()}: {str(e)}")
            logger.error(f"Failed to connect to {self.config.provider_name}: {e}")
            return False
    
    async def _disconnect(self):
        """Close database connection"""
        try:
            self.connection_status = ConnectionStatus.DISCONNECTED
            
            # Close active connections
            for conn in list(self.active_connections):
                await self._close_connection(conn)
                self.active_connections.discard(conn)
            
            # Close connection pool
            if self.connection_pool:
                await self._close_connection_pool()
                self.connection_pool = None
            
            # Close single connection
            if self.connection:
                await self._close_connection(self.connection)
                self.connection = None
                
            logger.info(f"Database provider {self.config.provider_name} disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting from {self.config.provider_name}: {e}")
    
    async def _close_connection_pool(self):
        """Close connection pool - to be overridden by specific implementations"""
        pass
    
    async def _get_connection(self) -> Any:
        """Get connection from pool or single connection"""
        if self.connection_pool:
            # Implementation-specific pool connection retrieval
            return await self._get_pool_connection()
        else:
            return self.connection
    
    async def _return_connection(self, connection: Any):
        """Return connection to pool"""
        if self.connection_pool:
            await self._return_pool_connection(connection)
    
    async def _get_pool_connection(self) -> Any:
        """Get connection from pool - to be overridden"""
        raise NotImplementedError("Pool connection retrieval not implemented")
    
    async def _return_pool_connection(self, connection: Any):
        """Return connection to pool - to be overridden"""
        pass
    
    @contextmanager
    def connection_context(self):
        """Connection context manager for safe connection handling"""
        connection = None
        try:
            connection = asyncio.run(self._get_connection())
            self.active_connections.add(connection)
            yield connection
        except Exception as e:
            logger.error(f"Connection context error: {e}")
            raise
        finally:
            if connection:
                self.active_connections.discard(connection)
                asyncio.run(self._return_connection(connection))

class RedisProvider(AbstractDatabaseProvider):
    """Redis cache provider implementation"""
    
    def __init__(self, config: DatabaseProviderConfig):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis library not available. Install with: pip install redis")
        
        # Set default port for Redis
        if config.port is None:
            config.port = 6379
        
        super().__init__(config)
        self.redis_pool = None
        self.redis_client = None
    
    async def _create_connection(self) -> redis.Redis:
        """Create Redis connection"""
        return redis.Redis(
            host=self.db_config.host,
            port=self.db_config.port,
            password=self.db_config.password,
            db=int(self.db_config.database) if self.db_config.database else 0,
            socket_timeout=self.db_config.connection_timeout,
            socket_connect_timeout=self.db_config.connection_timeout,
            decode_responses=True
        )
    
    async def _create_connection_pool(self) -> redis.ConnectionPool:
        """Create Redis connection pool"""
        self.redis_pool = redis.ConnectionPool(
            host=self.db_config.host,
            port=self.db_config.port,
            password=self.db_config.password,
            db=int(self.db_config.database) if self.db_config.database else 0,
            max_connections=self.db_config.pool_size,
            socket_timeout=self.db_config.connection_timeout,
            socket_connect_timeout=self.db_config.connection_timeout,
            decode_responses=True
        )
        return self.redis_pool
    
    async def _test_connection(self, connection: redis.Redis) -> bool:
        """Test Redis connection"""
        try:
            await asyncio.to_thread(connection.ping)
            return True
        except Exception:
            return False
    
    async def _close_connection(self, connection: redis.Redis):
        """Close Redis connection"""
        try:
            connection.close()
        except Exception as e:
            logger.error(f"Error closing Redis connection: {e}")
    
    async def _close_connection_pool(self):
        """Close Redis connection pool"""
        if self.redis_pool:
            self.redis_pool.disconnect()
    
    async def _get_pool_connection(self) -> redis.Redis:
        """Get Redis connection from pool"""
        return redis.Redis(connection_pool=self.redis_pool)
    
    async def _execute_query(self, connection: redis.Redis, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute Redis command"""
        # Parse Redis command from query string
        parts = query.strip().split()
        command = parts[0].upper()
        args = parts[1:] if len(parts) > 1 else []
        
        # Apply parameters if provided
        if params:
            for i, arg in enumerate(args):
                if arg in params:
                    args[i] = params[arg]
        
        # Execute command
        return await asyncio.to_thread(connection.execute_command, command, *args)
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute Redis operation"""
        start_time = time.time()
        
        try:
            connection = await self._get_connection()
            
            if request.operation_type == OperationType.READ:
                key = request.parameters.get('key')
                if not key:
                    raise ValueError("Redis READ operation requires 'key' parameter")
                
                result = await asyncio.to_thread(connection.get, key)
                
            elif request.operation_type == OperationType.WRITE:
                key = request.parameters.get('key')
                value = request.parameters.get('value')
                ttl = request.parameters.get('ttl')
                
                if not key or value is None:
                    raise ValueError("Redis WRITE operation requires 'key' and 'value' parameters")
                
                if ttl:
                    result = await asyncio.to_thread(connection.setex, key, ttl, value)
                else:
                    result = await asyncio.to_thread(connection.set, key, value)
                    
            elif request.operation_type == OperationType.DELETE:
                key = request.parameters.get('key')
                if not key:
                    raise ValueError("Redis DELETE operation requires 'key' parameter")
                
                result = await asyncio.to_thread(connection.delete, key)
                
            elif request.operation_type == OperationType.SEARCH:
                pattern = request.parameters.get('pattern', '*')
                result = await asyncio.to_thread(connection.keys, pattern)
                
            else:
                # Execute custom Redis command
                query = request.parameters.get('query', '')
                result = await self._execute_query(connection, query, request.parameters)
            
            await self._return_connection(connection)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=result,
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                error_message=str(e),
                error_code="REDIS_ERROR",
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
    
    async def _health_check_impl(self) -> HealthStatus:
        """Redis health check"""
        try:
            connection = await self._get_connection()
            await asyncio.to_thread(connection.ping)
            await self._return_connection(connection)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Redis provider capabilities"""
        return {
            "operations": [op.value for op in OperationType],
            "data_types": ["string", "hash", "list", "set", "sorted_set", "stream"],
            "features": ["caching", "session_storage", "pub_sub", "transactions"],
            "max_key_size": "512MB",
            "max_value_size": "512MB",
            "clustering": True,
            "persistence": True
        }

class Neo4jProvider(AbstractDatabaseProvider):
    """Neo4j graph database provider implementation"""
    
    def __init__(self, config: DatabaseProviderConfig):
        if not NEO4J_AVAILABLE:
            raise ImportError("Neo4j library not available. Install with: pip install neo4j")
        
        # Set default port for Neo4j
        if config.port is None:
            config.port = 7687
        
        super().__init__(config)
        self.driver = None
    
    async def _create_connection(self) -> Any:
        """Create Neo4j driver (acts as connection pool)"""
        uri = f"bolt://{self.db_config.host}:{self.db_config.port}"
        
        self.driver = GraphDatabase.driver(
            uri,
            auth=basic_auth(self.db_config.username, self.db_config.password) if self.db_config.username else None,
            max_connection_lifetime=3600,
            max_connection_pool_size=self.db_config.pool_size,
            connection_timeout=self.db_config.connection_timeout,
            max_retry_time=30
        )
        
        return self.driver
    
    async def _create_connection_pool(self) -> Any:
        """Neo4j driver is already a connection pool"""
        return await self._create_connection()
    
    async def _test_connection(self, connection: Any) -> bool:
        """Test Neo4j connection"""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1").single()
            return True
        except Exception:
            return False
    
    async def _close_connection(self, connection: Any):
        """Close Neo4j driver"""
        if self.driver:
            self.driver.close()
    
    async def _get_connection(self) -> Any:
        """Get Neo4j session"""
        return self.driver.session()
    
    async def _return_connection(self, connection: Any):
        """Close Neo4j session"""
        if connection:
            connection.close()
    
    async def _execute_query(self, connection: Any, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute Cypher query"""
        return connection.run(query, params or {})
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute Neo4j operation"""
        start_time = time.time()
        
        try:
            session = await self._get_connection()
            
            query = request.parameters.get('query', '')
            params = request.parameters.get('params', {})
            
            if request.operation_type == OperationType.READ:
                result = session.run(query, params)
                data = [record.data() for record in result]
                
            elif request.operation_type == OperationType.WRITE:
                with session.begin_transaction() as tx:
                    result = tx.run(query, params)
                    tx.commit()
                    data = result.consume().counters
                    
            elif request.operation_type == OperationType.DELETE:
                with session.begin_transaction() as tx:
                    result = tx.run(query, params)
                    tx.commit()
                    data = result.consume().counters
                    
            else:
                result = session.run(query, params)
                data = [record.data() for record in result]
            
            await self._return_connection(session)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=data,
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                error_message=str(e),
                error_code="NEO4J_ERROR",
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
    
    async def _health_check_impl(self) -> HealthStatus:
        """Neo4j health check"""
        try:
            session = await self._get_connection()
            session.run("RETURN 1").single()
            await self._return_connection(session)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Neo4j provider capabilities"""
        return {
            "operations": [op.value for op in OperationType],
            "query_language": "Cypher",
            "features": ["ACID_transactions", "graph_algorithms", "spatial", "full_text_search"],
            "max_nodes": "35 billion",
            "max_relationships": "35 billion",
            "clustering": True,
            "causal_clustering": True
        }

class PostgreSQLProvider(AbstractDatabaseProvider):
    """PostgreSQL relational database provider implementation"""
    
    def __init__(self, config: DatabaseProviderConfig):
        if not POSTGRESQL_AVAILABLE:
            raise ImportError("PostgreSQL library not available. Install with: pip install psycopg2-binary")
        
        # Set default port for PostgreSQL
        if config.port is None:
            config.port = 5432
        
        super().__init__(config)
    
    async def _create_connection(self) -> psycopg2.extensions.connection:
        """Create PostgreSQL connection"""
        return psycopg2.connect(
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.username,
            password=self.db_config.password,
            database=self.db_config.database or 'postgres',
            connect_timeout=self.db_config.connection_timeout
        )
    
    async def _create_connection_pool(self) -> psycopg2.pool.ThreadedConnectionPool:
        """Create PostgreSQL connection pool"""
        return psycopg2.pool.ThreadedConnectionPool(
            1,  # minconn
            self.db_config.pool_size,  # maxconn
            host=self.db_config.host,
            port=self.db_config.port,
            user=self.db_config.username,
            password=self.db_config.password,
            database=self.db_config.database or 'postgres',
            connect_timeout=self.db_config.connection_timeout
        )
    
    async def _test_connection(self, connection: psycopg2.extensions.connection) -> bool:
        """Test PostgreSQL connection"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            return True
        except Exception:
            return False
    
    async def _close_connection(self, connection: psycopg2.extensions.connection):
        """Close PostgreSQL connection"""
        try:
            connection.close()
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connection: {e}")
    
    async def _close_connection_pool(self):
        """Close PostgreSQL connection pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
    
    async def _get_pool_connection(self) -> psycopg2.extensions.connection:
        """Get connection from PostgreSQL pool"""
        return self.connection_pool.getconn()
    
    async def _return_pool_connection(self, connection: psycopg2.extensions.connection):
        """Return connection to PostgreSQL pool"""
        self.connection_pool.putconn(connection)
    
    async def _execute_query(self, connection: psycopg2.extensions.connection, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute PostgreSQL query"""
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            
            if cursor.description:
                return cursor.fetchall()
            else:
                return cursor.rowcount
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute PostgreSQL operation"""
        start_time = time.time()
        
        try:
            connection = await self._get_connection()
            
            query = request.parameters.get('query', '')
            params = request.parameters.get('params', {})
            
            result = await asyncio.to_thread(self._execute_query, connection, query, params)
            
            # Commit for write operations
            if request.operation_type in [OperationType.WRITE, OperationType.UPDATE, OperationType.DELETE]:
                await asyncio.to_thread(connection.commit)
            
            await self._return_connection(connection)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=result,
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                error_message=str(e),
                error_code="POSTGRESQL_ERROR",
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
    
    async def _health_check_impl(self) -> HealthStatus:
        """PostgreSQL health check"""
        try:
            connection = await self._get_connection()
            await asyncio.to_thread(self._test_connection, connection)
            await self._return_connection(connection)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get PostgreSQL provider capabilities"""
        return {
            "operations": [op.value for op in OperationType],
            "query_language": "SQL",
            "features": ["ACID_transactions", "JSON_support", "full_text_search", "spatial_data", "extensions"],
            "max_database_size": "unlimited",
            "max_table_size": "32TB",
            "max_row_size": "1.6TB",
            "replication": True,
            "partitioning": True
        }

class QdrantProvider(AbstractDatabaseProvider):
    """Qdrant vector database provider implementation"""
    
    def __init__(self, config: DatabaseProviderConfig):
        if not QDRANT_AVAILABLE:
            raise ImportError("Qdrant library not available. Install with: pip install qdrant-client")
        
        # Set default port for Qdrant
        if config.port is None:
            config.port = 6333
        
        super().__init__(config)
        self.client = None
    
    async def _create_connection(self) -> QdrantClient:
        """Create Qdrant client"""
        self.client = QdrantClient(
            host=self.db_config.host,
            port=self.db_config.port,
            timeout=self.db_config.connection_timeout
        )
        return self.client
    
    async def _create_connection_pool(self) -> QdrantClient:
        """Qdrant client handles connection pooling internally"""
        return await self._create_connection()
    
    async def _test_connection(self, connection: QdrantClient) -> bool:
        """Test Qdrant connection"""
        try:
            connection.get_collections()
            return True
        except Exception:
            return False
    
    async def _close_connection(self, connection: QdrantClient):
        """Close Qdrant client"""
        if self.client:
            self.client.close()
    
    async def _get_connection(self) -> QdrantClient:
        """Get Qdrant client"""
        return self.client
    
    async def _execute_query(self, connection: QdrantClient, query: str, params: Dict[str, Any] = None) -> Any:
        """Execute Qdrant operation based on query type"""
        # Parse operation from query
        parts = query.strip().split()
        operation = parts[0].upper()
        
        if operation == "SEARCH":
            collection_name = params.get('collection_name')
            vector = params.get('vector')
            limit = params.get('limit', 10)
            return connection.search(
                collection_name=collection_name,
                query_vector=vector,
                limit=limit
            )
        elif operation == "INSERT":
            collection_name = params.get('collection_name')
            points = params.get('points')
            return connection.upsert(
                collection_name=collection_name,
                points=points
            )
        else:
            raise ValueError(f"Unsupported Qdrant operation: {operation}")
    
    async def _execute_operation_impl(self, request: OperationRequest) -> OperationResult:
        """Execute Qdrant operation"""
        start_time = time.time()
        
        try:
            client = await self._get_connection()
            
            if request.operation_type == OperationType.SEARCH:
                collection_name = request.parameters.get('collection_name')
                vector = request.parameters.get('vector')
                limit = request.parameters.get('limit', 10)
                
                result = await asyncio.to_thread(
                    client.search,
                    collection_name=collection_name,
                    query_vector=vector,
                    limit=limit
                )
                
            elif request.operation_type == OperationType.WRITE:
                collection_name = request.parameters.get('collection_name')
                points = request.parameters.get('points')
                
                result = await asyncio.to_thread(
                    client.upsert,
                    collection_name=collection_name,
                    points=points
                )
                
            elif request.operation_type == OperationType.DELETE:
                collection_name = request.parameters.get('collection_name')
                point_ids = request.parameters.get('point_ids')
                
                result = await asyncio.to_thread(
                    client.delete,
                    collection_name=collection_name,
                    points_selector=point_ids
                )
                
            else:
                # Execute custom operation
                query = request.parameters.get('query', '')
                result = await asyncio.to_thread(self._execute_query, client, query, request.parameters)
            
            duration_ms = (time.time() - start_time) * 1000
            
            return OperationResult(
                success=True,
                data=result,
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return OperationResult(
                success=False,
                error_message=str(e),
                error_code="QDRANT_ERROR",
                duration_ms=duration_ms,
                operation_type=request.operation_type,
                provider_name=self.config.provider_name
            )
    
    async def _health_check_impl(self) -> HealthStatus:
        """Qdrant health check"""
        try:
            client = await self._get_connection()
            await asyncio.to_thread(client.get_collections)
            return HealthStatus.HEALTHY
        except Exception:
            return HealthStatus.UNAVAILABLE
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get Qdrant provider capabilities"""
        return {
            "operations": [OperationType.SEARCH.value, OperationType.WRITE.value, OperationType.DELETE.value],
            "vector_types": ["dense", "sparse"],
            "distance_metrics": ["cosine", "euclidean", "dot_product"],
            "features": ["filtering", "payload", "collections", "snapshots"],
            "max_vector_size": 65536,
            "max_collection_size": "unlimited",
            "clustering": True,
            "replication": True
        }

class ProviderFactory:
    """Factory for creating database providers"""
    
    _providers = {
        DatabaseType.REDIS: RedisProvider,
        DatabaseType.NEO4J: Neo4jProvider,
        DatabaseType.POSTGRESQL: PostgreSQLProvider,
        DatabaseType.QDRANT: QdrantProvider
    }
    
    @classmethod
    def create_provider(cls, config: DatabaseProviderConfig) -> AbstractDatabaseProvider:
        """Create database provider based on configuration"""
        provider_class = cls._providers.get(config.database_type)
        
        if not provider_class:
            raise ValueError(f"Unsupported database type: {config.database_type}")
        
        return provider_class(config)
    
    @classmethod
    def register_provider(cls, db_type: DatabaseType, provider_class: type):
        """Register custom database provider"""
        cls._providers[db_type] = provider_class
    
    @classmethod
    def get_available_providers(cls) -> List[DatabaseType]:
        """Get list of available database provider types"""
        available = []
        
        if REDIS_AVAILABLE:
            available.append(DatabaseType.REDIS)
        if NEO4J_AVAILABLE:
            available.append(DatabaseType.NEO4J)
        if POSTGRESQL_AVAILABLE:
            available.append(DatabaseType.POSTGRESQL)
        if QDRANT_AVAILABLE:
            available.append(DatabaseType.QDRANT)
            
        return available

class ProviderManager:
    """Manager for multiple database providers"""
    
    def __init__(self):
        self.providers: Dict[str, AbstractDatabaseProvider] = {}
        self.configs: Dict[str, DatabaseProviderConfig] = {}
        self.lock = threading.RLock()
    
    async def add_provider(self, name: str, config: DatabaseProviderConfig) -> bool:
        """Add and initialize a database provider"""
        try:
            provider = ProviderFactory.create_provider(config)
            
            if await provider.initialize():
                with self.lock:
                    self.providers[name] = provider
                    self.configs[name] = config
                logger.info(f"Provider {name} added successfully")
                return True
            else:
                logger.error(f"Failed to initialize provider {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding provider {name}: {e}")
            return False
    
    async def remove_provider(self, name: str) -> bool:
        """Remove a database provider"""
        try:
            with self.lock:
                provider = self.providers.get(name)
                if provider:
                    await provider.cleanup()
                    del self.providers[name]
                    del self.configs[name]
                    logger.info(f"Provider {name} removed")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"Error removing provider {name}: {e}")
            return False
    
    async def execute_operation(self, provider_name: str, request: OperationRequest) -> OperationResult:
        """Execute operation on specific provider"""
        provider = self.providers.get(provider_name)
        if not provider:
            return OperationResult(
                success=False,
                error_message=f"Provider {provider_name} not found",
                error_code="PROVIDER_NOT_FOUND"
            )
        
        return await provider.execute_operation(request)
    
    async def health_check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all providers"""
        results = {}
        
        for name, provider in self.providers.items():
            try:
                results[name] = await provider.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = HealthStatus.UNAVAILABLE
        
        return results
    
    def get_provider_metrics(self) -> Dict[str, ProviderMetrics]:
        """Get metrics for all providers"""
        return {name: provider.get_metrics() for name, provider in self.providers.items()}
    
    async def cleanup_all(self):
        """Cleanup all providers"""
        for provider in self.providers.values():
            try:
                await provider.cleanup()
            except Exception as e:
                logger.error(f"Error during provider cleanup: {e}")
        
        self.providers.clear()
        self.configs.clear()

# Example usage and configuration helpers
def create_redis_config(host: str = "localhost", port: int = 6379, 
                       password: str = None, database: str = "0") -> DatabaseProviderConfig:
    """Create Redis provider configuration"""
    return DatabaseProviderConfig(
        provider_type=ProviderType.DATABASE,
        provider_name="redis",
        database_type=DatabaseType.REDIS,
        host=host,
        port=port,
        password=password,
        database=database
    )

def create_neo4j_config(host: str = "localhost", port: int = 7687,
                       username: str = "neo4j", password: str = "password") -> DatabaseProviderConfig:
    """Create Neo4j provider configuration"""
    return DatabaseProviderConfig(
        provider_type=ProviderType.DATABASE,
        provider_name="neo4j",
        database_type=DatabaseType.NEO4J,
        host=host,
        port=port,
        username=username,
        password=password
    )

def create_postgresql_config(host: str = "localhost", port: int = 5432,
                           username: str = "postgres", password: str = "password",
                           database: str = "postgres") -> DatabaseProviderConfig:
    """Create PostgreSQL provider configuration"""
    return DatabaseProviderConfig(
        provider_type=ProviderType.DATABASE,
        provider_name="postgresql",
        database_type=DatabaseType.POSTGRESQL,
        host=host,
        port=port,
        username=username,
        password=password,
        database=database
    )

def create_qdrant_config(host: str = "localhost", port: int = 6333) -> DatabaseProviderConfig:
    """Create Qdrant provider configuration"""
    return DatabaseProviderConfig(
        provider_type=ProviderType.DATABASE,
        provider_name="qdrant",
        database_type=DatabaseType.QDRANT,
        host=host,
        port=port
    ) 