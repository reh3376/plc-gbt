#!/usr/bin/env python3
"""
Phase 22.1.4: Analysis Result Storage
====================================

Comprehensive storage and retrieval system for control loop analysis results
with PostgreSQL integration, query optimization, and caching strategies.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import json
import hashlib
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import uuid
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError
import redis

from .database_schema import (
    DatabaseSchemaManager, AnalysisResultSchema, AnalysisType, 
    StorageStatus, StorageMetrics
)

logger = logging.getLogger(__name__)

@dataclass
class StorageResult:
    """Result of storage operation"""
    success: bool
    result_id: Optional[str]
    storage_time: float
    cached: bool
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class QueryFilter:
    """Query filter for result retrieval"""
    analysis_type: Optional[AnalysisType] = None
    algorithm_name: Optional[str] = None
    success_only: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: List[str] = None
    limit: int = 100
    offset: int = 0

class QueryBuilder:
    """
    SQL query builder for analysis results
    """
    
    def __init__(self, schema_manager: DatabaseSchemaManager):
        self.schema_manager = schema_manager
        self.table = schema_manager.tables['analysis_results']
    
    def build_select_query(self, filters: QueryFilter) -> sa.sql.Select:
        """Build SELECT query with filters"""
        query = sa.select(self.table)
        
        # Apply filters
        if filters.analysis_type:
            query = query.where(self.table.c.analysis_type == filters.analysis_type.value)
        
        if filters.algorithm_name:
            query = query.where(self.table.c.algorithm_name == filters.algorithm_name)
        
        if filters.success_only:
            query = query.where(self.table.c.success == True)
        
        if filters.start_date:
            query = query.where(self.table.c.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.where(self.table.c.created_at <= filters.end_date)
        
        if filters.tags:
            # JSONB array contains filter
            for tag in filters.tags:
                query = query.where(self.table.c.tags.op('?')(tag))
        
        # Order by creation date (newest first)
        query = query.order_by(self.table.c.created_at.desc())
        
        # Apply limit and offset
        if filters.limit > 0:
            query = query.limit(filters.limit)
        
        if filters.offset > 0:
            query = query.offset(filters.offset)
        
        return query
    
    def build_count_query(self, filters: QueryFilter) -> sa.sql.Select:
        """Build COUNT query with filters"""
        query = sa.select(sa.func.count(self.table.c.id))
        
        # Apply same filters as select query (without limit/offset)
        if filters.analysis_type:
            query = query.where(self.table.c.analysis_type == filters.analysis_type.value)
        
        if filters.algorithm_name:
            query = query.where(self.table.c.algorithm_name == filters.algorithm_name)
        
        if filters.success_only:
            query = query.where(self.table.c.success == True)
        
        if filters.start_date:
            query = query.where(self.table.c.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.where(self.table.c.created_at <= filters.end_date)
        
        if filters.tags:
            for tag in filters.tags:
                query = query.where(self.table.c.tags.op('?')(tag))
        
        return query
    
    def build_aggregation_query(self, group_by: str, filters: QueryFilter) -> sa.sql.Select:
        """Build aggregation query"""
        if group_by == 'analysis_type':
            group_column = self.table.c.analysis_type
        elif group_by == 'algorithm_name':
            group_column = self.table.c.algorithm_name
        elif group_by == 'date':
            group_column = sa.func.date_trunc('day', self.table.c.created_at)
        else:
            raise ValueError(f"Unsupported group_by: {group_by}")
        
        query = sa.select(
            group_column.label('group_key'),
            sa.func.count().label('total_count'),
            sa.func.count(sa.case((self.table.c.success == True, 1))).label('success_count'),
            sa.func.avg(self.table.c.execution_time).label('avg_execution_time'),
            sa.func.min(self.table.c.created_at).label('first_execution'),
            sa.func.max(self.table.c.created_at).label('last_execution')
        )
        
        # Apply filters
        if filters.analysis_type and group_by != 'analysis_type':
            query = query.where(self.table.c.analysis_type == filters.analysis_type.value)
        
        if filters.algorithm_name and group_by != 'algorithm_name':
            query = query.where(self.table.c.algorithm_name == filters.algorithm_name)
        
        if filters.start_date:
            query = query.where(self.table.c.created_at >= filters.start_date)
        
        if filters.end_date:
            query = query.where(self.table.c.created_at <= filters.end_date)
        
        query = query.group_by(group_column).order_by(group_column)
        
        return query

class AnalysisResultStorage:
    """
    Comprehensive storage system for analysis results
    """
    
    def __init__(self, schema_manager: DatabaseSchemaManager, 
                 redis_client: Optional[redis.Redis] = None,
                 cache_ttl: int = 3600):
        self.schema_manager = schema_manager
        self.redis_client = redis_client
        self.cache_ttl = cache_ttl
        self.query_builder = QueryBuilder(schema_manager)
        
        # Create session factory
        self.Session = sessionmaker(bind=schema_manager.engine)
        
        self.logger = logging.getLogger(__name__ + '.ResultStorage')
        
        # Performance tracking
        self._storage_stats = {
            'total_stores': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_queries': 0,
            'total_storage_time': 0.0
        }
    
    def store_result(self, algorithm_name: str, analysis_type: AnalysisType,
                    input_data: Dict[str, Any], result_data: Dict[str, Any],
                    execution_time: float, success: bool,
                    error_message: Optional[str] = None,
                    tags: List[str] = None,
                    metadata: Dict[str, Any] = None) -> StorageResult:
        """Store analysis result with caching"""
        start_time = datetime.now()
        
        try:
            # Generate unique result ID
            result_id = str(uuid.uuid4())
            
            # Generate input data hash for deduplication
            input_hash = self._generate_input_hash(input_data)
            
            # Check cache first
            if self.redis_client and success:
                cached_result = self._check_cache(input_hash, algorithm_name)
                if cached_result:
                    self._storage_stats['cache_hits'] += 1
                    return StorageResult(
                        success=True,
                        result_id=cached_result['result_id'],
                        storage_time=0.0,
                        cached=True,
                        metadata={'source': 'cache'}
                    )
            
            # Create analysis result schema
            analysis_result = AnalysisResultSchema(
                result_id=result_id,
                analysis_type=analysis_type,
                algorithm_name=algorithm_name,
                input_data_hash=input_hash,
                result_data=result_data,
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # Store in database
            storage_time = self._store_to_database(analysis_result)
            
            # Cache successful results
            if self.redis_client and success:
                self._cache_result(input_hash, algorithm_name, result_id, result_data)
            
            # Update statistics
            self._storage_stats['total_stores'] += 1
            self._storage_stats['total_storage_time'] += storage_time
            if not success or not cached_result:
                self._storage_stats['cache_misses'] += 1
            
            return StorageResult(
                success=True,
                result_id=result_id,
                storage_time=storage_time,
                cached=False,
                metadata={'database_stored': True}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to store result: {e}")
            return StorageResult(
                success=False,
                result_id=None,
                storage_time=(datetime.now() - start_time).total_seconds(),
                cached=False,
                error_message=str(e)
            )
    
    def _store_to_database(self, result: AnalysisResultSchema) -> float:
        """Store result to PostgreSQL database"""
        start_time = datetime.now()
        
        with self.Session() as session:
            try:
                # Insert into analysis_results table
                insert_query = sa.insert(self.schema_manager.tables['analysis_results']).values(
                    result_id=result.result_id,
                    analysis_type=result.analysis_type.value,
                    algorithm_name=result.algorithm_name,
                    input_data_hash=result.input_data_hash,
                    result_data=result.result_data,
                    execution_time=result.execution_time,
                    success=result.success,
                    error_message=result.error_message,
                    created_at=result.created_at,
                    updated_at=result.updated_at,
                    tags=result.tags,
                    metadata=result.metadata,
                    version=result.version
                )
                
                session.execute(insert_query)
                session.commit()
                
                storage_time = (datetime.now() - start_time).total_seconds()
                self.logger.debug(f"Stored result {result.result_id} in {storage_time:.3f}s")
                
                return storage_time
                
            except IntegrityError as e:
                session.rollback()
                self.logger.warning(f"Duplicate result ID: {result.result_id}")
                raise
            except Exception as e:
                session.rollback()
                self.logger.error(f"Database storage failed: {e}")
                raise
    
    def retrieve_results(self, filters: QueryFilter) -> Tuple[List[Dict[str, Any]], int]:
        """Retrieve analysis results with filtering"""
        start_time = datetime.now()
        
        try:
            with self.Session() as session:
                # Build and execute count query
                count_query = self.query_builder.build_count_query(filters)
                total_count = session.execute(count_query).scalar()
                
                # Build and execute select query
                select_query = self.query_builder.build_select_query(filters)
                results = session.execute(select_query).fetchall()
                
                # Convert to dictionaries
                result_list = []
                for row in results:
                    result_dict = dict(row._mapping)
                    # Convert UUID to string
                    result_dict['id'] = str(result_dict['id'])
                    result_list.append(result_dict)
                
                query_time = (datetime.now() - start_time).total_seconds()
                self._storage_stats['total_queries'] += 1
                
                self.logger.debug(f"Retrieved {len(result_list)} results in {query_time:.3f}s")
                
                return result_list, total_count
                
        except Exception as e:
            self.logger.error(f"Failed to retrieve results: {e}")
            raise
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get specific result by ID"""
        try:
            with self.Session() as session:
                query = sa.select(self.schema_manager.tables['analysis_results']).where(
                    self.schema_manager.tables['analysis_results'].c.result_id == result_id
                )
                
                result = session.execute(query).fetchone()
                
                if result:
                    result_dict = dict(result._mapping)
                    result_dict['id'] = str(result_dict['id'])
                    return result_dict
                else:
                    return None
                    
        except Exception as e:
            self.logger.error(f"Failed to get result by ID: {e}")
            raise
    
    def get_aggregated_stats(self, group_by: str, filters: QueryFilter) -> List[Dict[str, Any]]:
        """Get aggregated statistics"""
        try:
            with self.Session() as session:
                query = self.query_builder.build_aggregation_query(group_by, filters)
                results = session.execute(query).fetchall()
                
                stats_list = []
                for row in results:
                    stats_dict = dict(row._mapping)
                    # Calculate success rate
                    if stats_dict['total_count'] > 0:
                        stats_dict['success_rate'] = stats_dict['success_count'] / stats_dict['total_count']
                    else:
                        stats_dict['success_rate'] = 0.0
                    
                    stats_list.append(stats_dict)
                
                return stats_list
                
        except Exception as e:
            self.logger.error(f"Failed to get aggregated stats: {e}")
            raise
    
    def delete_results(self, filters: QueryFilter) -> int:
        """Delete results matching filters"""
        try:
            with self.Session() as session:
                # Build delete query using same filter logic
                delete_query = sa.delete(self.schema_manager.tables['analysis_results'])
                
                if filters.analysis_type:
                    delete_query = delete_query.where(
                        self.schema_manager.tables['analysis_results'].c.analysis_type == filters.analysis_type.value
                    )
                
                if filters.algorithm_name:
                    delete_query = delete_query.where(
                        self.schema_manager.tables['analysis_results'].c.algorithm_name == filters.algorithm_name
                    )
                
                if filters.start_date:
                    delete_query = delete_query.where(
                        self.schema_manager.tables['analysis_results'].c.created_at >= filters.start_date
                    )
                
                if filters.end_date:
                    delete_query = delete_query.where(
                        self.schema_manager.tables['analysis_results'].c.created_at <= filters.end_date
                    )
                
                result = session.execute(delete_query)
                deleted_count = result.rowcount
                session.commit()
                
                self.logger.info(f"Deleted {deleted_count} results")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to delete results: {e}")
            session.rollback()
            raise
    
    def _generate_input_hash(self, input_data: Dict[str, Any]) -> str:
        """Generate hash for input data deduplication"""
        # Create deterministic JSON string
        json_str = json.dumps(input_data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()
    
    def _check_cache(self, input_hash: str, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """Check Redis cache for existing result"""
        if not self.redis_client:
            return None
        
        try:
            cache_key = f"analysis_result:{algorithm_name}:{input_hash}"
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                return json.loads(cached_data)
            else:
                return None
                
        except Exception as e:
            self.logger.warning(f"Cache check failed: {e}")
            return None
    
    def _cache_result(self, input_hash: str, algorithm_name: str, 
                     result_id: str, result_data: Dict[str, Any]):
        """Cache result in Redis"""
        if not self.redis_client:
            return
        
        try:
            cache_key = f"analysis_result:{algorithm_name}:{input_hash}"
            cache_data = {
                'result_id': result_id,
                'result_data': result_data,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(cache_data, default=str)
            )
            
        except Exception as e:
            self.logger.warning(f"Cache storage failed: {e}")
    
    def get_storage_statistics(self) -> Dict[str, Any]:
        """Get storage performance statistics"""
        stats = self._storage_stats.copy()
        
        # Calculate derived metrics
        if stats['total_queries'] > 0:
            stats['cache_hit_rate'] = stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])
        else:
            stats['cache_hit_rate'] = 0.0
        
        if stats['total_stores'] > 0:
            stats['average_storage_time'] = stats['total_storage_time'] / stats['total_stores']
        else:
            stats['average_storage_time'] = 0.0
        
        return stats
    
    def clear_cache(self, pattern: str = "analysis_result:*"):
        """Clear cached results"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted_count = self.redis_client.delete(*keys)
                self.logger.info(f"Cleared {deleted_count} cached results")
                return deleted_count
            else:
                return 0
                
        except Exception as e:
            self.logger.error(f"Failed to clear cache: {e}")
            return 0

# Export main components
__all__ = [
    'AnalysisResultStorage',
    'QueryBuilder',
    'StorageResult',
    'QueryFilter'
] 