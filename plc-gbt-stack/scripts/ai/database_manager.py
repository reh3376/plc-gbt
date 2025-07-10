#!/usr/bin/env python3
"""
🤖 Multi-Database Manager - AI Task Orchestrator Implementation

Unified database management system for coordinating:
- Neo4j: Medium-term structured knowledge and relationships  
- PostgreSQL: Long-term persistent storage and historical data
- Qdrant: Vector embeddings for pattern matching and similarity search
- Redis: Short-term context window management and real-time caching

Following AI Task Orchestrator Guide methodology for EXTENSIVE complexity task.

Author: AI Task Orchestrator
Created: 2025-01-09
Phase: Database Integration (Step 2 of 6)
"""

import os
import sys
import json
import time
import logging
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import traceback

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env file in project root (plc-gbt-stack directory)
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        # Fallback: try current directory
        load_dotenv()
except ImportError:
    # python-dotenv not available - environment variables must be set manually
    pass

# Import persistent Redis manager
try:
    from persistent_redis_manager import PersistentRedisManager, get_persistent_redis_manager, close_persistent_redis_manager
    PERSISTENT_REDIS_AVAILABLE = True
except ImportError:
    PERSISTENT_REDIS_AVAILABLE = False

# Database imports
try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

try:
    import psycopg2
    import psycopg2.pool
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Database type enumeration for multi-database architecture"""
    NEO4J = "neo4j"           # Graph database for relationships
    POSTGRESQL = "postgresql"  # Relational database for structured data
    QDRANT = "qdrant"         # Vector database for embeddings
    REDIS = "redis"           # In-memory cache for short-term data

class MemoryTier(Enum):
    """Memory tier classification for intelligent data routing"""
    SHORT_TERM = "short_term"     # Redis - Context window, real-time caching
    MEDIUM_TERM = "medium_term"   # Neo4j - Session memory, structured knowledge  
    LONG_TERM = "long_term"       # PostgreSQL - Persistent storage, historical data
    PATTERN_MATCHING = "pattern"  # Qdrant - Vector embeddings, similarity search

class DatabaseStatus(Enum):
    """Database connection status enumeration"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    INITIALIZING = "initializing"
    UNKNOWN = "unknown"

@dataclass
class DatabaseConfig:
    """Database connection configuration"""
    host: str
    port: int
    database: str = None
    username: str = None
    password: str = None
    connection_params: Dict[str, Any] = None

@dataclass
class DatabaseHealth:
    """Database health status information"""
    database_type: DatabaseType
    status: DatabaseStatus
    last_check: datetime
    response_time_ms: float
    error_message: Optional[str] = None
    connection_count: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

@dataclass
class QueryResult:
    """Unified query result structure"""
    database_type: DatabaseType
    success: bool
    data: Any
    execution_time_ms: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class DatabaseManager:
    """
    🎯 Unified Multi-Database Management System
    
    Coordinates operations across Neo4j, PostgreSQL, Qdrant, and Redis
    following the AI Task Orchestrator methodology for memory management.
    
    Features:
    - Unified connection management with health monitoring
    - Intelligent query routing based on data type and tier
    - Automatic failover and recovery mechanisms
    - Performance monitoring and optimization
    - Transaction coordination across databases
    - Connection pooling and resource management
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize the multi-database manager"""
        self.start_time = datetime.now()
        self.session_id = f"db_manager_{int(time.time())}"
        
        # Database connections
        self.connections = {
            DatabaseType.NEO4J: None,
            DatabaseType.POSTGRESQL: None,
            DatabaseType.QDRANT: None,
            DatabaseType.REDIS: None
        }
        
        # Connection pools
        self.connection_pools = {}
        
        # Persistent Redis manager
        self.persistent_redis_manager: Optional[PersistentRedisManager] = None
        self.use_persistent_redis = PERSISTENT_REDIS_AVAILABLE
        
        # Database configurations
        self.configs = {}
        
        # Health monitoring
        self.health_status = {}
        self.last_health_check = {}
        
        # Performance metrics
        self.query_stats = {db_type: {"count": 0, "total_time": 0.0, "errors": 0} 
                           for db_type in DatabaseType}
        
        # Error handling
        self.error_counts = {db_type: 0 for db_type in DatabaseType}
        self.max_retries = 3
        self.retry_delay = 1.0
        
        # Load configuration
        self._load_configurations(config_file)
        
        logger.info(f"DatabaseManager initialized with session: {self.session_id}")
        if self.use_persistent_redis:
            logger.info("✅ Persistent Redis manager enabled for enhanced caching performance")

    def _load_configurations(self, config_file: Optional[str] = None) -> None:
        """Load database configurations from file or environment"""
        try:
            if config_file and Path(config_file).exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                self._parse_config_data(config_data)
            else:
                self._load_from_environment()
                
            logger.info("Database configurations loaded successfully")
        except Exception as e:
            logger.error(f"Error loading configurations: {str(e)}")
            self._load_default_configurations()

    def _load_from_environment(self) -> None:
        """Load configuration from environment variables"""
        self.configs = {
            DatabaseType.NEO4J: DatabaseConfig(
                host=os.getenv("NEO4J_HOST", "localhost"),
                port=int(os.getenv("NEO4J_PORT", "7687")),
                username=os.getenv("NEO4J_USER", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", "password")
            ),
            DatabaseType.POSTGRESQL: DatabaseConfig(
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=int(os.getenv("POSTGRES_PORT", "5432")),
                database=os.getenv("POSTGRES_DB", "plc_metadata"),
                username=os.getenv("POSTGRES_USER", "plc_user"),
                password=os.getenv("POSTGRES_PASSWORD", "password")
            ),
            DatabaseType.QDRANT: DatabaseConfig(
                host=os.getenv("QDRANT_HOST", "localhost"),
                port=int(os.getenv("QDRANT_PORT", "6333"))
            ),
            DatabaseType.REDIS: DatabaseConfig(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", "6379"))
            )
        }

    def _load_default_configurations(self) -> None:
        """Load default configurations as fallback"""
        logger.warning("Loading default database configurations")
        self.configs = {
            DatabaseType.NEO4J: DatabaseConfig(
                host="localhost", port=7687, username="neo4j", password="password"
            ),
            DatabaseType.POSTGRESQL: DatabaseConfig(
                host="localhost", port=5432, database="plc_metadata",
                username="plc_user", password="password"
            ),
            DatabaseType.QDRANT: DatabaseConfig(
                host="localhost", port=6333
            ),
            DatabaseType.REDIS: DatabaseConfig(
                host="localhost", port=6379
            )
        }

    def _parse_config_data(self, config_data: Dict[str, Any]) -> None:
        """Parse configuration data from JSON"""
        for db_name, db_config in config_data.get("databases", {}).items():
            try:
                db_type = DatabaseType(db_name.lower())
                self.configs[db_type] = DatabaseConfig(**db_config)
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid configuration for {db_name}: {str(e)}")

    async def initialize_all_connections(self) -> Dict[DatabaseType, bool]:
        """Initialize connections to all available databases"""
        logger.info("🔗 Initializing all database connections...")
        
        results = {}
        initialization_tasks = []
        
        # Create initialization tasks for each database
        for db_type in DatabaseType:
            if self._is_database_available(db_type):
                task = self._initialize_single_connection(db_type)
                initialization_tasks.append((db_type, task))
        
        # Execute initialization tasks concurrently
        for db_type, task in initialization_tasks:
            try:
                results[db_type] = await task
                logger.info(f"✅ {db_type.value} initialization: {'success' if results[db_type] else 'failed'}")
            except Exception as e:
                logger.error(f"❌ {db_type.value} initialization error: {str(e)}")
                results[db_type] = False
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        logger.info(f"🎯 Database initialization complete: {successful}/{total} databases connected")
        
        return results

    async def _initialize_single_connection(self, db_type: DatabaseType) -> bool:
        """Initialize connection to a single database"""
        try:
            config = self.configs.get(db_type)
            if not config:
                logger.error(f"No configuration found for {db_type.value}")
                return False
            
            if db_type == DatabaseType.NEO4J and NEO4J_AVAILABLE:
                return await self._initialize_neo4j(config)
            elif db_type == DatabaseType.POSTGRESQL and POSTGRESQL_AVAILABLE:
                return await self._initialize_postgresql(config)
            elif db_type == DatabaseType.QDRANT and QDRANT_AVAILABLE:
                return await self._initialize_qdrant(config)
            elif db_type == DatabaseType.REDIS and REDIS_AVAILABLE:
                return await self._initialize_redis(config)
            else:
                logger.warning(f"Database {db_type.value} not available or library not installed")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing {db_type.value}: {str(e)}")
            self.error_counts[db_type] += 1
            return False

    async def _initialize_neo4j(self, config: DatabaseConfig) -> bool:
        """Initialize Neo4j connection"""
        try:
            uri = f"bolt://{config.host}:{config.port}"
            self.connections[DatabaseType.NEO4J] = GraphDatabase.driver(
                uri, auth=basic_auth(config.username, config.password)
            )
            
            # Test connection
            with self.connections[DatabaseType.NEO4J].session() as session:
                result = session.run("RETURN 1 as test")
                record = result.single()
                if record and record["test"] == 1:
                    logger.info(f"✅ Neo4j connected at {uri}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Neo4j connection error: {str(e)}")
            return False

    async def _initialize_postgresql(self, config: DatabaseConfig) -> bool:
        """Initialize PostgreSQL connection with connection pooling"""
        try:
            connection_string = (
                f"host={config.host} port={config.port} "
                f"dbname={config.database} user={config.username} "
                f"password={config.password}"
            )
            
            # Create connection pool
            self.connection_pools[DatabaseType.POSTGRESQL] = psycopg2.pool.ThreadedConnectionPool(
                minconn=1, maxconn=10, dsn=connection_string
            )
            
            # Test connection
            conn = self.connection_pools[DatabaseType.POSTGRESQL].getconn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            self.connection_pools[DatabaseType.POSTGRESQL].putconn(conn)
            
            if result and result[0] == 1:
                logger.info(f"✅ PostgreSQL connected at {config.host}:{config.port}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {str(e)}")
            return False

    async def _initialize_qdrant(self, config: DatabaseConfig) -> bool:
        """Initialize Qdrant connection"""
        try:
            self.connections[DatabaseType.QDRANT] = QdrantClient(
                host=config.host, port=config.port
            )
            
            # Test connection
            info = self.connections[DatabaseType.QDRANT].info()
            if info:
                logger.info(f"✅ Qdrant connected at {config.host}:{config.port}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Qdrant connection error: {str(e)}")
            return False

    async def _initialize_redis(self, config: DatabaseConfig) -> bool:
        """Initialize Redis connection (with persistent manager if available)"""
        try:
            if self.use_persistent_redis:
                # Use persistent Redis manager for enhanced performance
                self.persistent_redis_manager = await get_persistent_redis_manager()
                
                if self.persistent_redis_manager.is_connected():
                    logger.info(f"✅ Persistent Redis connection established at {config.host}:{config.port}")
                    # Store a reference for compatibility with existing code
                    self.connections[DatabaseType.REDIS] = "persistent_connection"
                    return True
                else:
                    logger.warning("Persistent Redis manager failed, falling back to traditional connection")
                    self.use_persistent_redis = False
            
            # Fallback to traditional Redis connection
            self.connections[DatabaseType.REDIS] = redis.Redis(
                host=config.host, port=config.port, decode_responses=True
            )
            
            # Test connection
            pong = self.connections[DatabaseType.REDIS].ping()
            if pong:
                logger.info(f"✅ Redis connected at {config.host}:{config.port}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Redis connection error: {str(e)}")
            return False

    def _is_database_available(self, db_type: DatabaseType) -> bool:
        """Check if database library is available"""
        availability_map = {
            DatabaseType.NEO4J: NEO4J_AVAILABLE,
            DatabaseType.POSTGRESQL: POSTGRESQL_AVAILABLE,
            DatabaseType.QDRANT: QDRANT_AVAILABLE,
            DatabaseType.REDIS: REDIS_AVAILABLE
        }
        return availability_map.get(db_type, False)

    async def check_health(self, db_type: Optional[DatabaseType] = None) -> Dict[DatabaseType, DatabaseHealth]:
        """Check health status of databases"""
        if db_type:
            databases_to_check = [db_type]
        else:
            databases_to_check = [db for db in DatabaseType if self.connections.get(db)]
        
        health_results = {}
        
        for db in databases_to_check:
            start_time = time.time()
            
            try:
                is_healthy = await self._check_single_database_health(db)
                response_time = (time.time() - start_time) * 1000
                
                health_results[db] = DatabaseHealth(
                    database_type=db,
                    status=DatabaseStatus.CONNECTED if is_healthy else DatabaseStatus.ERROR,
                    last_check=datetime.now(),
                    response_time_ms=response_time
                )
                
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                health_results[db] = DatabaseHealth(
                    database_type=db,
                    status=DatabaseStatus.ERROR,
                    last_check=datetime.now(),
                    response_time_ms=response_time,
                    error_message=str(e)
                )
        
        self.health_status.update(health_results)
        return health_results

    async def health_check(self, db_type: Optional[DatabaseType] = None) -> Dict[str, Any]:
        """
        Alias for check_health() to maintain CLI compatibility.
        Returns simplified health information in expected format.
        """
        health_results = await self.check_health(db_type)
        
        # Convert to the expected format for CLI
        simplified_results = {}
        for db_type, health in health_results.items():
            simplified_results[db_type.value] = {
                'status': health.status.value,
                'response_time_ms': health.response_time_ms,
                'last_check': health.last_check.isoformat() if health.last_check else None,
                'error_message': health.error_message
            }
        
        return simplified_results

    async def _check_single_database_health(self, db_type: DatabaseType) -> bool:
        """Check health of a single database"""
        try:
            if db_type == DatabaseType.NEO4J and self.connections[db_type]:
                with self.connections[db_type].session() as session:
                    result = session.run("RETURN 1")
                    return result.single() is not None
                    
            elif db_type == DatabaseType.POSTGRESQL and self.connection_pools.get(db_type):
                conn = self.connection_pools[db_type].getconn()
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                self.connection_pools[db_type].putconn(conn)
                return result is not None
                
            elif db_type == DatabaseType.QDRANT and self.connections[db_type]:
                info = self.connections[db_type].info()
                return info is not None
                
            elif db_type == DatabaseType.REDIS and self.connections[db_type]:
                if self.use_persistent_redis and self.persistent_redis_manager:
                    return self.persistent_redis_manager.is_healthy()
                else:
                    return self.connections[db_type].ping()
                
            return False
            
        except Exception as e:
            logger.error(f"Health check failed for {db_type.value}: {str(e)}")
            return False

    async def execute_query(self, db_type: DatabaseType, query: str, 
                          parameters: Optional[Dict[str, Any]] = None,
                          timeout: Optional[float] = None) -> QueryResult:
        """Execute query on specified database with unified result format"""
        start_time = time.time()
        
        try:
            # Update query statistics
            self.query_stats[db_type]["count"] += 1
            
            # Route to appropriate database
            if db_type == DatabaseType.NEO4J:
                result = await self._execute_neo4j_query(query, parameters, timeout)
            elif db_type == DatabaseType.POSTGRESQL:
                result = await self._execute_postgresql_query(query, parameters, timeout)
            elif db_type == DatabaseType.QDRANT:
                result = await self._execute_qdrant_query(query, parameters, timeout)
            elif db_type == DatabaseType.REDIS:
                result = await self._execute_redis_query(query, parameters, timeout)
            else:
                raise ValueError(f"Unsupported database type: {db_type}")
            
            execution_time = (time.time() - start_time) * 1000
            self.query_stats[db_type]["total_time"] += execution_time
            
            return QueryResult(
                database_type=db_type,
                success=True,
                data=result,
                execution_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            self.query_stats[db_type]["errors"] += 1
            self.error_counts[db_type] += 1
            
            logger.error(f"Query execution failed on {db_type.value}: {str(e)}")
            
            return QueryResult(
                database_type=db_type,
                success=False,
                data=None,
                execution_time_ms=execution_time,
                error_message=str(e)
            )

    async def _execute_neo4j_query(self, query: str, parameters: Optional[Dict[str, Any]] = None, 
                                 timeout: Optional[float] = None) -> Any:
        """Execute Neo4j Cypher query"""
        if not self.connections[DatabaseType.NEO4J]:
            raise RuntimeError("Neo4j connection not available")
        
        with self.connections[DatabaseType.NEO4J].session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]

    async def _execute_postgresql_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                                       timeout: Optional[float] = None) -> Any:
        """Execute PostgreSQL SQL query"""
        if not self.connection_pools.get(DatabaseType.POSTGRESQL):
            raise RuntimeError("PostgreSQL connection pool not available")
        
        conn = self.connection_pools[DatabaseType.POSTGRESQL].getconn()
        try:
            cursor = conn.cursor()
            cursor.execute(query, parameters or {})
            
            if cursor.description:
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [dict(zip(columns, row)) for row in rows]
            else:
                result = {"affected_rows": cursor.rowcount}
            
            conn.commit()
            cursor.close()
            return result
            
        finally:
            self.connection_pools[DatabaseType.POSTGRESQL].putconn(conn)

    async def _execute_qdrant_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                                   timeout: Optional[float] = None) -> Any:
        """Execute Qdrant vector query"""
        if not self.connections[DatabaseType.QDRANT]:
            raise RuntimeError("Qdrant connection not available")
        
        # Qdrant uses method calls rather than query strings
        # This is a simplified implementation - extend based on actual use cases
        if query == "search":
            collection_name = parameters.get("collection")
            query_vector = parameters.get("vector")
            limit = parameters.get("limit", 10)
            
            return self.connections[DatabaseType.QDRANT].search(
                collection_name=collection_name,
                query_vector=query_vector,
                limit=limit
            )
        elif query == "get_collections":
            return self.connections[DatabaseType.QDRANT].get_collections()
        elif query == "upsert":
            # Real Qdrant upsert operation
            collection_name = parameters.get("collection")
            points = parameters.get("points", [])
            
            # Convert points to Qdrant format
            from qdrant_client.models import PointStruct
            qdrant_points = []
            for point in points:
                qdrant_point = PointStruct(
                    id=point.get("id"),
                    vector=point.get("vector"),
                    payload=point.get("payload", {})
                )
                qdrant_points.append(qdrant_point)
            
            # Perform upsert operation
            return self.connections[DatabaseType.QDRANT].upsert(
                collection_name=collection_name,
                points=qdrant_points
            )
        else:
            raise ValueError(f"Unsupported Qdrant query: {query}")

    async def _execute_redis_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                                  timeout: Optional[float] = None) -> Any:
        """Execute Redis command (using persistent manager if available)"""
        if not self.connections[DatabaseType.REDIS]:
            raise RuntimeError("Redis connection not available")
        
        # Use persistent Redis manager if available for enhanced performance
        if self.use_persistent_redis and self.persistent_redis_manager:
            from persistent_redis_manager import CacheOperation
            
            if query == "get":
                return await self.persistent_redis_manager.execute_operation(
                    CacheOperation.GET, key=parameters.get("key")
                )
            elif query == "set":
                return await self.persistent_redis_manager.execute_operation(
                    CacheOperation.SET, 
                    key=parameters.get("key"), 
                    value=parameters.get("value"),
                    ttl=parameters.get("ttl")
                )
            elif query == "delete":
                return await self.persistent_redis_manager.execute_operation(
                    CacheOperation.DELETE, key=parameters.get("key")
                )
            elif query == "exists":
                return await self.persistent_redis_manager.execute_operation(
                    CacheOperation.EXISTS, key=parameters.get("key")
                )
            else:
                # Fall back to traditional Redis client for unsupported operations
                redis_client = self.persistent_redis_manager.redis_client
                if query == "keys":
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        None, redis_client.keys, parameters.get("pattern", "*")
                    )
                else:
                    raise ValueError(f"Unsupported Redis query for persistent manager: {query}")
        else:
            # Traditional Redis client approach
            redis_client = self.connections[DatabaseType.REDIS]
            
            if query == "get":
                return redis_client.get(parameters.get("key"))
            elif query == "set":
                return redis_client.set(parameters.get("key"), parameters.get("value"))
            elif query == "delete":
                return redis_client.delete(parameters.get("key"))
            elif query == "keys":
                return redis_client.keys(parameters.get("pattern", "*"))
            else:
                raise ValueError(f"Unsupported Redis query: {query}")

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics for all databases"""
        metrics = {
            "session_id": self.session_id,
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "databases": {}
        }
        
        for db_type in DatabaseType:
            stats = self.query_stats[db_type]
            
            avg_execution_time = (
                stats["total_time"] / stats["count"] 
                if stats["count"] > 0 else 0.0
            )
            
            error_rate = (
                stats["errors"] / stats["count"] * 100 
                if stats["count"] > 0 else 0.0
            )
            
            metrics["databases"][db_type.value] = {
                "query_count": stats["count"],
                "total_execution_time_ms": stats["total_time"],
                "average_execution_time_ms": avg_execution_time,
                "error_count": stats["errors"],
                "error_rate_percent": error_rate,
                "connection_status": "connected" if self.connections.get(db_type) else "disconnected"
            }
        
        return metrics

    def get_memory_tier_mapping(self) -> Dict[MemoryTier, DatabaseType]:
        """Get the mapping between memory tiers and database types"""
        return {
            MemoryTier.SHORT_TERM: DatabaseType.REDIS,
            MemoryTier.MEDIUM_TERM: DatabaseType.NEO4J,
            MemoryTier.LONG_TERM: DatabaseType.POSTGRESQL,
            MemoryTier.PATTERN_MATCHING: DatabaseType.QDRANT
        }

    async def close_all_connections(self) -> None:
        """Close all database connections and clean up resources"""
        logger.info("🔒 Closing all database connections...")
        
        for db_type, connection in self.connections.items():
            try:
                if connection:
                    if db_type == DatabaseType.NEO4J:
                        connection.close()
                        logger.info(f"✅ {db_type.value} connection closed")
                    elif db_type == DatabaseType.REDIS:
                        if self.use_persistent_redis and self.persistent_redis_manager:
                            # Note: Persistent Redis connections are intentionally kept alive
                            # They will be managed by the persistent manager lifecycle
                            logger.info(f"✅ {db_type.value} persistent connection maintained")
                        else:
                            connection.close()
                            logger.info(f"✅ {db_type.value} connection closed")
                    elif db_type == DatabaseType.QDRANT:
                        connection.close()
                        logger.info(f"✅ {db_type.value} connection closed")
                    # PostgreSQL connections will be handled by their respective cleanup
                    
            except Exception as e:
                logger.error(f"Error closing {db_type.value} connection: {str(e)}")
        
        # Close PostgreSQL connection pool
        if DatabaseType.POSTGRESQL in self.connection_pools:
            try:
                self.connection_pools[DatabaseType.POSTGRESQL].closeall()
                logger.info("✅ PostgreSQL connection pool closed")
            except Exception as e:
                logger.error(f"Error closing PostgreSQL pool: {str(e)}")
        
        # Clear all connections (except persistent Redis)
        for db_type in DatabaseType:
            if db_type == DatabaseType.REDIS and self.use_persistent_redis:
                # Keep persistent Redis connection reference
                continue
            self.connections[db_type] = None
        
        self.connection_pools.clear()
        
        logger.info("🎯 All database connections closed successfully")

    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        duration = datetime.now() - self.start_time
        
        summary = {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "duration_seconds": duration.total_seconds(),
            "connected_databases": sum(1 for conn in self.connections.values() if conn is not None),
            "total_databases": len(DatabaseType),
            "performance_metrics": self.get_performance_metrics(),
            "health_status": {
                db_type.value: asdict(health) 
                for db_type, health in self.health_status.items()
            },
            "error_summary": {
                db_type.value: count 
                for db_type, count in self.error_counts.items()
            }
        }
        
        return summary

async def main():
    """
    🚀 Main execution function demonstrating DatabaseManager capabilities
    """
    print("🤖 Multi-Database Manager - AI Task Orchestrator Implementation")
    print("=" * 70)
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        # Initialize all connections
        print("\n🔗 Step 1: Initializing Database Connections")
        results = await db_manager.initialize_all_connections()
        
        # Health check
        print("\n🔍 Step 2: Database Health Check")
        health_status = await db_manager.check_health()
        
        for db_type, health in health_status.items():
            status_emoji = "✅" if health.status == DatabaseStatus.CONNECTED else "❌"
            print(f"{status_emoji} {db_type.value}: {health.status.value} "
                  f"({health.response_time_ms:.1f}ms)")
        
        # Performance metrics
        print("\n📊 Step 3: Performance Metrics")
        metrics = db_manager.get_performance_metrics()
        print(f"Session uptime: {metrics['uptime_seconds']:.1f} seconds")
        
        for db_name, db_metrics in metrics["databases"].items():
            print(f"{db_name}: {db_metrics['query_count']} queries, "
                  f"{db_metrics['connection_status']}")
        
        # Memory tier mapping
        print("\n🏗️ Step 4: Memory Tier Architecture")
        tier_mapping = db_manager.get_memory_tier_mapping()
        for tier, db_type in tier_mapping.items():
            print(f"{tier.value} → {db_type.value}")
        
        # Session summary
        print("\n📋 Step 5: Session Summary")
        summary = db_manager.get_session_summary()
        print(f"Connected databases: {summary['connected_databases']}/{summary['total_databases']}")
        
        print("\n🎯 DatabaseManager demonstration complete!")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    finally:
        # Clean up connections
        print("\n🔒 Closing Connections")
        await db_manager.close_all_connections()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 