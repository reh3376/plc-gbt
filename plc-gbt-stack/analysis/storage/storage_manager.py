#!/usr/bin/env python3
"""
Phase 22.1.4: Storage Manager
============================

Unified storage management system that orchestrates all storage components
into a single, comprehensive interface for the Enhanced Control Loop Analysis Engine.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import redis
import os
from pathlib import Path

from .database_schema import (
    DatabaseSchemaManager, AnalysisResultSchema, AnalysisType, 
    StorageStatus, StorageMetrics
)
from .result_storage import (
    AnalysisResultStorage, QueryBuilder, StorageResult, QueryFilter
)
from .historical_tracker import (
    HistoricalTracker, TrendAnalysis, PerformanceMetrics, TrendDirection
)

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Unified storage management system for control loop analysis results
    
    This class provides a single interface for all storage operations including:
    - Result storage and retrieval with caching
    - Historical tracking and trend analysis  
    - Performance monitoring and metrics
    - Database schema management
    - Storage optimization and maintenance
    """
    
    def __init__(self, 
                 postgresql_url: str,
                 redis_url: Optional[str] = None,
                 schema_name: str = "control_analysis",
                 cache_ttl: int = 3600,
                 auto_initialize: bool = True):
        """
        Initialize the storage manager
        
        Args:
            postgresql_url: PostgreSQL connection string
            redis_url: Redis connection string (optional, for caching)
            schema_name: Database schema name
            cache_ttl: Cache time-to-live in seconds
            auto_initialize: Whether to auto-initialize database schema
        """
        self.postgresql_url = postgresql_url
        self.redis_url = redis_url
        self.schema_name = schema_name
        self.cache_ttl = cache_ttl
        
        self.logger = logging.getLogger(__name__ + '.StorageManager')
        
        # Initialize components
        self._initialize_components(auto_initialize)
        
        # Performance tracking
        self._manager_stats = {
            'initialized_at': datetime.utcnow(),
            'total_operations': 0,
            'cache_enabled': redis_url is not None,
            'schema_optimized': False
        }
    
    def _initialize_components(self, auto_initialize: bool):
        """Initialize all storage components"""
        try:
            # Initialize database schema manager
            self.schema_manager = DatabaseSchemaManager(
                self.postgresql_url, 
                self.schema_name
            )
            
            # Initialize Redis client if URL provided
            self.redis_client = None
            if self.redis_url:
                try:
                    self.redis_client = redis.from_url(self.redis_url)
                    # Test connection
                    self.redis_client.ping()
                    self.logger.info("Redis cache enabled")
                except Exception as e:
                    self.logger.warning(f"Redis initialization failed: {e}")
                    self.redis_client = None
            
            # Initialize result storage
            self.result_storage = AnalysisResultStorage(
                self.schema_manager,
                self.redis_client,
                self.cache_ttl
            )
            
            # Initialize historical tracker
            self.historical_tracker = HistoricalTracker(
                self.schema_manager,
                self.result_storage
            )
            
            # Auto-initialize database if requested
            if auto_initialize:
                self.initialize_database()
            
            self.logger.info("Storage manager initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize storage manager: {e}")
            raise
    
    def initialize_database(self, drop_existing: bool = False):
        """Initialize database schema and tables"""
        try:
            self.schema_manager.create_tables(drop_existing)
            self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    # Result Storage Operations
    
    def store_analysis_result(self, 
                            algorithm_name: str,
                            analysis_type: AnalysisType,
                            input_data: Dict[str, Any],
                            result_data: Dict[str, Any],
                            execution_time: float,
                            success: bool,
                            error_message: Optional[str] = None,
                            tags: List[str] = None,
                            metadata: Dict[str, Any] = None) -> StorageResult:
        """
        Store analysis result with comprehensive tracking
        
        Args:
            algorithm_name: Name of the algorithm that produced the result
            analysis_type: Type of analysis performed
            input_data: Input data used for analysis
            result_data: Analysis result data
            execution_time: Time taken to execute analysis
            success: Whether analysis was successful
            error_message: Error message if analysis failed
            tags: Optional tags for categorization
            metadata: Additional metadata
            
        Returns:
            StorageResult with operation details
        """
        try:
            self._manager_stats['total_operations'] += 1
            
            result = self.result_storage.store_result(
                algorithm_name=algorithm_name,
                analysis_type=analysis_type,
                input_data=input_data,
                result_data=result_data,
                execution_time=execution_time,
                success=success,
                error_message=error_message,
                tags=tags,
                metadata=metadata
            )
            
            self.logger.debug(f"Stored analysis result: {result.result_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to store analysis result: {e}")
            raise
    
    def retrieve_results(self, 
                        analysis_type: Optional[AnalysisType] = None,
                        algorithm_name: Optional[str] = None,
                        success_only: bool = True,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        tags: List[str] = None,
                        limit: int = 100,
                        offset: int = 0) -> Tuple[List[Dict[str, Any]], int]:
        """
        Retrieve analysis results with filtering
        
        Args:
            analysis_type: Filter by analysis type
            algorithm_name: Filter by algorithm name
            success_only: Only return successful results
            start_date: Filter by start date
            end_date: Filter by end date
            tags: Filter by tags
            limit: Maximum number of results
            offset: Result offset for pagination
            
        Returns:
            Tuple of (results list, total count)
        """
        try:
            filters = QueryFilter(
                analysis_type=analysis_type,
                algorithm_name=algorithm_name,
                success_only=success_only,
                start_date=start_date,
                end_date=end_date,
                tags=tags,
                limit=limit,
                offset=offset
            )
            
            results, total_count = self.result_storage.retrieve_results(filters)
            
            self.logger.debug(f"Retrieved {len(results)} results")
            return results, total_count
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve results: {e}")
            raise
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get specific result by ID"""
        try:
            return self.result_storage.get_result_by_id(result_id)
        except Exception as e:
            self.logger.error(f"Failed to get result by ID: {e}")
            raise
    
    def delete_results(self, 
                      analysis_type: Optional[AnalysisType] = None,
                      algorithm_name: Optional[str] = None,
                      start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> int:
        """Delete results matching criteria"""
        try:
            filters = QueryFilter(
                analysis_type=analysis_type,
                algorithm_name=algorithm_name,
                start_date=start_date,
                end_date=end_date,
                success_only=False  # Include failed results in deletion
            )
            
            deleted_count = self.result_storage.delete_results(filters)
            self.logger.info(f"Deleted {deleted_count} results")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Failed to delete results: {e}")
            raise
    
    # Statistical and Aggregation Operations
    
    def get_aggregated_statistics(self, 
                                 group_by: str,
                                 analysis_type: Optional[AnalysisType] = None,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get aggregated statistics grouped by specified field
        
        Args:
            group_by: Field to group by ('analysis_type', 'algorithm_name', 'date')
            analysis_type: Filter by analysis type
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of aggregated statistics
        """
        try:
            filters = QueryFilter(
                analysis_type=analysis_type,
                start_date=start_date,
                end_date=end_date,
                success_only=False
            )
            
            stats = self.result_storage.get_aggregated_stats(group_by, filters)
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get aggregated statistics: {e}")
            raise
    
    # Historical Tracking and Trend Analysis
    
    def analyze_performance_trends(self, 
                                  analysis_type: Optional[AnalysisType] = None,
                                  algorithm_name: Optional[str] = None,
                                  days_back: int = 30) -> List[TrendAnalysis]:
        """Analyze performance trends over specified period"""
        try:
            return self.historical_tracker.analyze_performance_trends(
                analysis_type, algorithm_name, days_back
            )
        except Exception as e:
            self.logger.error(f"Failed to analyze performance trends: {e}")
            raise
    
    def get_performance_summary(self, 
                               days_back: int = 7,
                               analysis_type: Optional[AnalysisType] = None) -> PerformanceMetrics:
        """Get comprehensive performance summary"""
        try:
            return self.historical_tracker.get_performance_summary(days_back, analysis_type)
        except Exception as e:
            self.logger.error(f"Failed to get performance summary: {e}")
            raise
    
    def detect_anomalies(self, 
                        days_back: int = 30,
                        analysis_type: Optional[AnalysisType] = None) -> List[Dict[str, Any]]:
        """Detect performance anomalies"""
        try:
            return self.historical_tracker.detect_anomalies(days_back, analysis_type)
        except Exception as e:
            self.logger.error(f"Failed to detect anomalies: {e}")
            raise
    
    def generate_performance_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        try:
            return self.historical_tracker.generate_performance_report(days_back)
        except Exception as e:
            self.logger.error(f"Failed to generate performance report: {e}")
            raise
    
    # Storage Management and Optimization
    
    def get_storage_metrics(self) -> Dict[str, Any]:
        """Get comprehensive storage metrics"""
        try:
            # Get database metrics
            db_metrics = self.schema_manager.get_storage_metrics()
            
            # Get result storage statistics
            storage_stats = self.result_storage.get_storage_statistics()
            
            # Get table information
            table_info = self.schema_manager.get_table_info()
            
            # Combine all metrics
            combined_metrics = {
                'database': {
                    'total_results': db_metrics.total_results,
                    'storage_size_mb': db_metrics.storage_size_mb,
                    'oldest_result': db_metrics.oldest_result.isoformat() if db_metrics.oldest_result else None,
                    'newest_result': db_metrics.newest_result.isoformat() if db_metrics.newest_result else None,
                    'results_by_type': db_metrics.results_by_type,
                    'error_rate': db_metrics.error_rate
                },
                'storage_performance': storage_stats,
                'table_info': table_info,
                'manager_stats': self._manager_stats,
                'cache_enabled': self.redis_client is not None
            }
            
            return combined_metrics
            
        except Exception as e:
            self.logger.error(f"Failed to get storage metrics: {e}")
            raise
    
    def optimize_storage(self) -> Dict[str, Any]:
        """Optimize storage performance"""
        try:
            optimization_results = {
                'started_at': datetime.utcnow().isoformat(),
                'operations': []
            }
            
            # Optimize database tables
            self.schema_manager.optimize_tables()
            optimization_results['operations'].append('Database tables optimized')
            
            # Clear expired cache entries if Redis is enabled
            if self.redis_client:
                cleared_count = self.result_storage.clear_cache("analysis_result:*")
                optimization_results['operations'].append(f'Cleared {cleared_count} cache entries')
            
            # Update optimization flag
            self._manager_stats['schema_optimized'] = True
            self._manager_stats['last_optimization'] = datetime.utcnow()
            
            optimization_results['completed_at'] = datetime.utcnow().isoformat()
            optimization_results['success'] = True
            
            self.logger.info("Storage optimization completed")
            return optimization_results
            
        except Exception as e:
            self.logger.error(f"Failed to optimize storage: {e}")
            raise
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Clean up old analysis data"""
        try:
            cleanup_results = {
                'started_at': datetime.utcnow().isoformat(),
                'days_to_keep': days_to_keep
            }
            
            # Clean up old results
            deleted_count = self.schema_manager.cleanup_old_results(days_to_keep)
            cleanup_results['deleted_results'] = deleted_count
            
            # Clear related cache entries
            if self.redis_client:
                cache_cleared = self.result_storage.clear_cache()
                cleanup_results['cache_cleared'] = cache_cleared
            
            cleanup_results['completed_at'] = datetime.utcnow().isoformat()
            cleanup_results['success'] = True
            
            self.logger.info(f"Cleaned up {deleted_count} old results")
            return cleanup_results
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            raise
    
    # Utility Methods
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        try:
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'components': {},
                'overall_status': 'healthy'
            }
            
            # Check database connection
            try:
                metrics = self.schema_manager.get_storage_metrics()
                health_status['components']['database'] = {
                    'status': 'healthy',
                    'total_results': metrics.total_results
                }
            except Exception as e:
                health_status['components']['database'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            # Check Redis connection
            if self.redis_client:
                try:
                    self.redis_client.ping()
                    health_status['components']['cache'] = {
                        'status': 'healthy',
                        'enabled': True
                    }
                except Exception as e:
                    health_status['components']['cache'] = {
                        'status': 'unhealthy',
                        'enabled': True,
                        'error': str(e)
                    }
                    health_status['overall_status'] = 'degraded'
            else:
                health_status['components']['cache'] = {
                    'status': 'disabled',
                    'enabled': False
                }
            
            # Check storage performance
            try:
                storage_stats = self.result_storage.get_storage_statistics()
                health_status['components']['storage'] = {
                    'status': 'healthy',
                    'cache_hit_rate': storage_stats.get('cache_hit_rate', 0.0),
                    'total_operations': storage_stats.get('total_stores', 0)
                }
            except Exception as e:
                health_status['components']['storage'] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['overall_status'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': 'unhealthy',
                'error': str(e)
            }
    
    def export_configuration(self) -> Dict[str, Any]:
        """Export current configuration"""
        return {
            'schema_name': self.schema_name,
            'cache_ttl': self.cache_ttl,
            'cache_enabled': self.redis_client is not None,
            'manager_stats': self._manager_stats
        }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources"""
        try:
            if self.redis_client:
                self.redis_client.close()
        except Exception as e:
            self.logger.warning(f"Error during cleanup: {e}")

# Global storage manager instance
storage_manager = None

def get_storage_manager(postgresql_url: str = None,
                       redis_url: str = None,
                       **kwargs) -> StorageManager:
    """Get or create global storage manager instance"""
    global storage_manager
    
    if storage_manager is None:
        if postgresql_url is None:
            # Try to get from environment
            postgresql_url = os.getenv('DATABASE_URL') or os.getenv('POSTGRESQL_URL')
            if not postgresql_url:
                raise ValueError("PostgreSQL URL must be provided")
        
        if redis_url is None:
            redis_url = os.getenv('REDIS_URL')
        
        storage_manager = StorageManager(
            postgresql_url=postgresql_url,
            redis_url=redis_url,
            **kwargs
        )
    
    return storage_manager

def initialize_storage(postgresql_url: str = None, 
                      redis_url: str = None,
                      **kwargs) -> StorageManager:
    """Initialize and return storage manager"""
    return get_storage_manager(postgresql_url, redis_url, **kwargs)

# Export main components
__all__ = [
    'StorageManager',
    'get_storage_manager',
    'initialize_storage'
] 