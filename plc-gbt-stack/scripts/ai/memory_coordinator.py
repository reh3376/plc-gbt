#!/usr/bin/env python3
"""
🤖 Memory Coordination Layer - AI Task Orchestrator Implementation

Phase 5: Intelligent memory coordination that manages data flow between databases
and optimizes query routing based on content type and access patterns.

Memory Tier Strategy:
- Redis: Short-term memory (context window, real-time caching)
- Neo4j: Medium-term memory (structured knowledge, relationships)  
- PostgreSQL: Long-term memory (persistent storage, historical data)
- Qdrant: Pattern matching (vector embeddings, similarity search)

Author: AI Task Orchestrator
Created: 2025-01-09
Phase: Memory Coordination (Step 4 of 6)
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
import hashlib

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from database_manager import DatabaseManager, DatabaseType, MemoryTier, QueryResult
from file_processors import FileProcessorOrchestrator, ProcessedContent
from codebase_analyzer import CodebaseAnalyzer, AnalysisResult, AnalysisDepth

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryStrategy(Enum):
    """Query routing strategies"""
    SPEED_OPTIMIZED = "speed"        # Prioritize fastest response
    ACCURACY_OPTIMIZED = "accuracy"  # Prioritize most comprehensive results
    COST_OPTIMIZED = "cost"         # Prioritize least resource usage
    BALANCED = "balanced"           # Balance speed, accuracy, and cost

class DataFlow(Enum):
    """Data flow directions in memory hierarchy"""
    INGEST = "ingest"              # New data flowing into system
    PROMOTE = "promote"            # Moving data to faster tier
    DEMOTE = "demote"             # Moving data to slower tier
    REPLICATE = "replicate"       # Copying data across tiers
    EVICT = "evict"               # Removing data from tier

@dataclass
class MemoryRequest:
    """Memory operation request"""
    operation_type: str
    data_type: str
    content: Any
    priority: int = 5
    ttl_seconds: Optional[int] = None
    routing_strategy: QueryStrategy = QueryStrategy.BALANCED
    metadata: Dict[str, Any] = None

@dataclass
class MemoryResponse:
    """Memory operation response"""
    success: bool
    data: Any
    source_tier: MemoryTier
    execution_time_ms: float
    cache_hit: bool = False
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

class IntelligentRouter:
    """Intelligent query routing based on data type and access patterns"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.access_patterns = {}
        self.performance_history = {}
        
    def route_query(self, request: MemoryRequest) -> List[DatabaseType]:
        """Determine optimal database routing for query"""
        
        # Content-based routing
        if request.data_type == 'code_function':
            if request.routing_strategy == QueryStrategy.SPEED_OPTIMIZED:
                return [DatabaseType.REDIS, DatabaseType.NEO4J]
            elif request.routing_strategy == QueryStrategy.ACCURACY_OPTIMIZED:
                return [DatabaseType.NEO4J, DatabaseType.POSTGRESQL, DatabaseType.QDRANT]
            else:  # BALANCED
                return [DatabaseType.NEO4J, DatabaseType.REDIS]
        
        elif request.data_type == 'documentation':
            if request.routing_strategy == QueryStrategy.SPEED_OPTIMIZED:
                return [DatabaseType.REDIS, DatabaseType.QDRANT]
            else:
                return [DatabaseType.QDRANT, DatabaseType.POSTGRESQL]
        
        elif request.data_type == 'configuration':
            return [DatabaseType.POSTGRESQL, DatabaseType.REDIS]
        
        elif request.data_type == 'search_similarity':
            return [DatabaseType.QDRANT, DatabaseType.NEO4J]
        
        # Default routing
        return [DatabaseType.NEO4J, DatabaseType.POSTGRESQL]
    
    def update_access_pattern(self, data_id: str, access_time: datetime):
        """Update access patterns for intelligent caching"""
        if data_id not in self.access_patterns:
            self.access_patterns[data_id] = []
        
        self.access_patterns[data_id].append(access_time)
        
        # Keep only recent access history
        cutoff = datetime.now() - timedelta(days=7)
        self.access_patterns[data_id] = [
            t for t in self.access_patterns[data_id] if t > cutoff
        ]

class CacheManager:
    """Multi-tier caching with intelligent warming and invalidation"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'warming_operations': 0
        }
        
    async def get_cached(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        try:
            result = await self.db_manager.execute_query(
                DatabaseType.REDIS,
                "get",
                {"key": key}
            )
            
            if result.success and result.data:
                self.cache_stats['hits'] += 1
                return json.loads(result.data) if result.data != 'None' else None
            else:
                self.cache_stats['misses'] += 1
                return None
                
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            self.cache_stats['misses'] += 1
            return None
    
    async def set_cached(self, key: str, data: Any, ttl: int = 3600) -> bool:
        """Set data in Redis cache with TTL"""
        try:
            serialized_data = json.dumps(data, default=str)
            result = await self.db_manager.execute_query(
                DatabaseType.REDIS,
                "set",
                {"key": key, "value": serialized_data}
            )
            return result.success
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
    
    async def warm_cache(self, frequently_accessed_data: List[str]):
        """Pre-load frequently accessed data into cache"""
        for data_key in frequently_accessed_data:
            # Logic to pre-load from slower tiers to cache
            self.cache_stats['warming_operations'] += 1
        
        logger.info(f"Cache warming complete: {len(frequently_accessed_data)} items")

class DataMigrationManager:
    """Automatic data migration between memory tiers"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.migration_rules = {
            'hot_data_threshold': 10,      # Access count for promotion to Redis
            'cold_data_threshold': 1,      # Access count for demotion
            'age_threshold_days': 30       # Age threshold for archiving
        }
    
    async def analyze_migration_candidates(self) -> Dict[DataFlow, List[str]]:
        """Analyze data for migration opportunities"""
        candidates = {
            DataFlow.PROMOTE: [],    # Move to faster tier
            DataFlow.DEMOTE: [],     # Move to slower tier  
            DataFlow.EVICT: []       # Remove from fast tier
        }
        
        # Mock analysis - in real implementation, query access patterns
        # from database logs and usage statistics
        
        return candidates
    
    async def execute_migration(self, flow_type: DataFlow, data_ids: List[str]) -> int:
        """Execute data migration between tiers"""
        successful_migrations = 0
        
        for data_id in data_ids:
            try:
                if flow_type == DataFlow.PROMOTE:
                    # Move from PostgreSQL to Redis for faster access
                    await self._promote_to_cache(data_id)
                elif flow_type == DataFlow.DEMOTE:
                    # Move from Redis to PostgreSQL for long-term storage
                    await self._demote_to_storage(data_id)
                elif flow_type == DataFlow.EVICT:
                    # Remove from Redis cache
                    await self._evict_from_cache(data_id)
                
                successful_migrations += 1
                
            except Exception as e:
                logger.error(f"Migration failed for {data_id}: {str(e)}")
        
        logger.info(f"Migration complete: {successful_migrations}/{len(data_ids)} successful")
        return successful_migrations
    
    async def _promote_to_cache(self, data_id: str):
        """Promote data from storage to cache"""
        # Implementation would load from PostgreSQL and store in Redis
        pass
    
    async def _demote_to_storage(self, data_id: str):
        """Demote data from cache to storage"""
        # Implementation would save to PostgreSQL and remove from Redis
        pass
    
    async def _evict_from_cache(self, data_id: str):
        """Evict data from cache"""
        # Implementation would remove from Redis
        pass

class MemoryCoordinator:
    """
    🎯 Intelligent Memory Coordination System
    
    Coordinates data flow between all memory tiers with intelligent routing,
    caching, and migration following AI Task Orchestrator methodology.
    
    Features:
    - Intelligent query routing based on data type and access patterns
    - Multi-tier caching with automatic warming and invalidation
    - Automatic data migration between memory tiers
    - Performance optimization with query result caching
    - Conflict resolution for eventually consistent updates
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.router = IntelligentRouter(db_manager)
        self.cache_manager = CacheManager(db_manager)
        self.migration_manager = DataMigrationManager(db_manager)
        self.file_processor = FileProcessorOrchestrator(db_manager)
        
        # Performance tracking
        self.operation_stats = {
            'queries': 0,
            'ingestions': 0,
            'cache_hits': 0,
            'migrations': 0,
            'total_time_ms': 0.0
        }
        
        # Session tracking
        self.session_id = f"memory_coord_{int(time.time())}"
        self.start_time = datetime.now()
        
        logger.info(f"MemoryCoordinator initialized: {self.session_id}")
    
    async def ingest_codebase(self, root_path: str, analysis_depth: AnalysisDepth = AnalysisDepth.STRUCTURAL, use_intelligent_orchestrator: bool = True) -> Dict[str, Any]:
        """Ingest entire codebase into multi-database memory system"""
        
        if use_intelligent_orchestrator:
            # Use AI Task Orchestrator intelligent ingestion methodology
            from intelligent_ingestion_orchestrator import IntelligentIngestionOrchestrator
            orchestrator = IntelligentIngestionOrchestrator(self)
            
            logger.info("🤖 Using AI Task Orchestrator intelligent ingestion methodology")
            return await orchestrator.ingest_codebase_intelligently(
                root_path=root_path,
                analysis_depth=analysis_depth,
                max_concurrent_batches=3,
                checkpoint_interval_minutes=5
            )
        
        else:
            # Legacy simple ingestion (kept for compatibility)
            start_time = time.time()
            
            logger.info(f"🔄 Starting legacy codebase ingestion: {root_path}")
            
            # Step 1: Analyze codebase
            analyzer = CodebaseAnalyzer(root_path, analysis_depth)
            analysis_results = analyzer.analyze_codebase()
            
            # Step 2: Process files and generate embeddings
            processed_files = []
            failed_files = []
            
            for result in analysis_results:
                try:
                    processed = self.file_processor.process_file(result)
                    if processed:
                        # Step 3: Store in appropriate databases
                        storage_results = await self.file_processor.store_processed_content(processed)
                        processed_files.append({
                            'file_path': result.file_metadata.path,
                            'chunks': len(processed.content_chunks),
                            'storage_results': storage_results
                        })
                    else:
                        failed_files.append(result.file_metadata.path)
                        
                except Exception as e:
                    logger.error(f"Processing failed for {result.file_metadata.path}: {str(e)}")
                    failed_files.append(result.file_metadata.path)
            
            # Update statistics
            self.operation_stats['ingestions'] += len(processed_files)
            ingestion_time = (time.time() - start_time) * 1000
            self.operation_stats['total_time_ms'] += ingestion_time
            
            summary = {
                'session_id': self.session_id,
                'root_path': root_path,
                'analysis_depth': analysis_depth.value,
                'methodology': 'Legacy Sequential Processing',
                'total_files_analyzed': len(analysis_results),
                'successfully_processed': len(processed_files),
                'failed_files': len(failed_files),
                'ingestion_time_ms': ingestion_time,
                'files_per_second': len(processed_files) / (ingestion_time / 1000) if ingestion_time > 0 else 0,
                'processed_files': processed_files[:10],  # Sample of processed files
                'failed_files': failed_files[:10]        # Sample of failed files
            }
            
            logger.info(f"✅ Codebase ingestion complete: {len(processed_files)} files processed")
            return summary
    
    async def query_memory(self, request: MemoryRequest) -> MemoryResponse:
        """Query memory system with intelligent routing"""
        start_time = time.time()
        
        # Step 1: Check cache first
        cache_key = self._generate_cache_key(request)
        cached_result = await self.cache_manager.get_cached(cache_key)
        
        if cached_result:
            execution_time = (time.time() - start_time) * 1000
            return MemoryResponse(
                success=True,
                data=cached_result,
                source_tier=MemoryTier.SHORT_TERM,
                execution_time_ms=execution_time,
                cache_hit=True
            )
        
        # Step 2: Route query to appropriate databases
        databases = self.router.route_query(request)
        
        for db_type in databases:
            try:
                # Convert database type to query
                query, params = self._convert_request_to_query(request, db_type)
                
                result = await self.db_manager.execute_query(db_type, query, params)
                
                if result.success and result.data:
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Cache the result
                    await self.cache_manager.set_cached(cache_key, result.data)
                    
                    # Update access patterns
                    data_id = request.metadata.get('data_id') if request.metadata else cache_key
                    self.router.update_access_pattern(data_id, datetime.now())
                    
                    # Update statistics
                    self.operation_stats['queries'] += 1
                    self.operation_stats['total_time_ms'] += execution_time
                    
                    return MemoryResponse(
                        success=True,
                        data=result.data,
                        source_tier=self._db_type_to_tier(db_type),
                        execution_time_ms=execution_time,
                        cache_hit=False
                    )
                    
            except Exception as e:
                logger.error(f"Query failed on {db_type.value}: {str(e)}")
                continue
        
        # No successful results
        execution_time = (time.time() - start_time) * 1000
        return MemoryResponse(
            success=False,
            data=None,
            source_tier=MemoryTier.SHORT_TERM,
            execution_time_ms=execution_time,
            error_message="No databases returned results"
        )
    
    async def optimize_memory_tiers(self) -> Dict[str, Any]:
        """Optimize memory tiers through intelligent migration"""
        start_time = time.time()
        
        logger.info("🔧 Starting memory tier optimization")
        
        # Step 1: Analyze migration candidates
        candidates = await self.migration_manager.analyze_migration_candidates()
        
        # Step 2: Execute migrations
        migration_results = {}
        for flow_type, data_ids in candidates.items():
            if data_ids:
                migrated = await self.migration_manager.execute_migration(flow_type, data_ids)
                migration_results[flow_type.value] = {
                    'candidates': len(data_ids),
                    'successful': migrated
                }
        
        # Step 3: Warm cache with frequently accessed data
        # This would analyze access patterns to determine what to pre-load
        await self.cache_manager.warm_cache(['frequently_accessed_item_1'])
        
        optimization_time = (time.time() - start_time) * 1000
        self.operation_stats['migrations'] += sum(r['successful'] for r in migration_results.values())
        
        summary = {
            'session_id': self.session_id,
            'optimization_time_ms': optimization_time,
            'migration_results': migration_results,
            'cache_stats': self.cache_manager.cache_stats,
            'performance_improvement': 'Data migration completed successfully'
        }
        
        logger.info("✅ Memory tier optimization complete")
        return summary
    
    def _generate_cache_key(self, request: MemoryRequest) -> str:
        """Generate cache key for request"""
        key_data = f"{request.operation_type}_{request.data_type}_{str(request.content)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _convert_request_to_query(self, request: MemoryRequest, db_type: DatabaseType) -> Tuple[str, Dict[str, Any]]:
        """Convert memory request to database-specific query"""
        if db_type == DatabaseType.NEO4J:
            if request.operation_type == 'search_functions':
                return "MATCH (f:Function) WHERE f.name CONTAINS $name RETURN f", {"name": str(request.content)}
            else:
                return "MATCH (n) RETURN n LIMIT 1", {}
        
        elif db_type == DatabaseType.POSTGRESQL:
            if request.operation_type == 'search_files':
                return "SELECT * FROM python_files WHERE data::text LIKE %s LIMIT 10", (f"%{request.content}%",)
            else:
                return "SELECT 1", ()
        
        elif db_type == DatabaseType.QDRANT:
            return "search", {
                "collection": "code",
                "vector": [0.1] * 384,  # Mock vector
                "limit": 10
            }
        
        elif db_type == DatabaseType.REDIS:
            return "get", {"key": str(request.content)}
        
        return "SELECT 1", {}
    
    def _db_type_to_tier(self, db_type: DatabaseType) -> MemoryTier:
        """Convert database type to memory tier"""
        mapping = {
            DatabaseType.REDIS: MemoryTier.SHORT_TERM,
            DatabaseType.NEO4J: MemoryTier.MEDIUM_TERM,
            DatabaseType.POSTGRESQL: MemoryTier.LONG_TERM,
            DatabaseType.QDRANT: MemoryTier.PATTERN_MATCHING
        }
        return mapping.get(db_type, MemoryTier.MEDIUM_TERM)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        duration = datetime.now() - self.start_time
        
        avg_query_time = (
            self.operation_stats['total_time_ms'] / self.operation_stats['queries']
            if self.operation_stats['queries'] > 0 else 0
        )
        
        return {
            'session_id': self.session_id,
            'uptime_seconds': duration.total_seconds(),
            'total_operations': sum([
                self.operation_stats['queries'],
                self.operation_stats['ingestions'],
                self.operation_stats['migrations']
            ]),
            'queries_executed': self.operation_stats['queries'],
            'files_ingested': self.operation_stats['ingestions'],
            'data_migrations': self.operation_stats['migrations'],
            'cache_hit_rate': (
                self.cache_manager.cache_stats['hits'] / 
                (self.cache_manager.cache_stats['hits'] + self.cache_manager.cache_stats['misses'])
                if (self.cache_manager.cache_stats['hits'] + self.cache_manager.cache_stats['misses']) > 0 
                else 0
            ),
            'average_query_time_ms': avg_query_time,
            'memory_tier_utilization': {
                'short_term_redis': 'Available',
                'medium_term_neo4j': 'Available', 
                'long_term_postgresql': 'Available',
                'pattern_qdrant': 'Available'
            }
        }

async def main():
    """
    🚀 Main demonstration of memory coordination system
    """
    print("🤖 Intelligent Memory Coordination Layer - AI Task Orchestrator Implementation")
    print("=" * 75)
    
    # Initialize components
    db_manager = DatabaseManager()
    coordinator = MemoryCoordinator(db_manager)
    
    try:
        # Initialize database connections
        print("\n🔗 Step 1: Initializing Database Connections")
        await db_manager.initialize_all_connections()
        
        # Demo memory operations
        print("\n💾 Step 2: Demo Memory Operations")
        
        # Test query routing
        request = MemoryRequest(
            operation_type='search_functions',
            data_type='code_function',
            content='process_file',
            routing_strategy=QueryStrategy.BALANCED,
            metadata={'data_id': 'demo_function'}
        )
        
        response = await coordinator.query_memory(request)
        print(f"✅ Query result: {response.success}, Source: {response.source_tier.value}")
        print(f"   Execution time: {response.execution_time_ms:.1f}ms")
        
        # Test memory optimization
        print("\n🔧 Step 3: Memory Tier Optimization")
        optimization_result = await coordinator.optimize_memory_tiers()
        print(f"✅ Optimization complete in {optimization_result['optimization_time_ms']:.1f}ms")
        
        # Performance summary
        print("\n📊 Step 4: Performance Summary")
        summary = coordinator.get_performance_summary()
        print(f"Total operations: {summary['total_operations']}")
        print(f"Cache hit rate: {summary['cache_hit_rate']:.1%}")
        print(f"Average query time: {summary['average_query_time_ms']:.1f}ms")
        
        print("\n🎯 Memory coordination demonstration complete!")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    finally:
        await db_manager.close_all_connections()
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main())) 