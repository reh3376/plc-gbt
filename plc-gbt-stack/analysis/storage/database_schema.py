#!/usr/bin/env python3
"""
Phase 22.1.4: Database Schema Management
=======================================

Comprehensive database schema management for control loop analysis results
with PostgreSQL optimization, indexing strategies, and performance monitoring.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.schema import Index
import uuid

logger = logging.getLogger(__name__)

class AnalysisType(Enum):
    """Types of control loop analysis"""
    STEP_DETECTION = "step_detection"
    MODEL_IDENTIFICATION = "model_identification"
    PID_TUNING = "pid_tuning"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    ADAPTIVE_CONTROL = "adaptive_control"
    WORKFLOW_EXECUTION = "workflow_execution"

class StorageStatus(Enum):
    """Storage operation status"""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CACHED = "cached"

@dataclass
class AnalysisResultSchema:
    """Schema definition for analysis results"""
    result_id: str
    analysis_type: AnalysisType
    algorithm_name: str
    input_data_hash: str
    result_data: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str]
    created_at: datetime
    updated_at: datetime
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"

@dataclass
class StorageMetrics:
    """Storage performance metrics"""
    total_results: int
    storage_size_mb: float
    average_query_time: float
    cache_hit_rate: float
    oldest_result: Optional[datetime]
    newest_result: Optional[datetime]
    results_by_type: Dict[str, int]
    error_rate: float

class DatabaseSchemaManager:
    """
    Comprehensive database schema management for analysis results
    """
    
    def __init__(self, connection_string: str, schema_name: str = "control_analysis"):
        self.connection_string = connection_string
        self.schema_name = schema_name
        self.engine = None
        self.metadata = None
        self.tables = {}
        
        self.logger = logging.getLogger(__name__ + '.SchemaManager')
        
        # Initialize database connection
        self._initialize_connection()
        
        # Create schema if needed
        self._ensure_schema_exists()
        
        # Define table schemas
        self._define_table_schemas()
    
    def _initialize_connection(self):
        """Initialize database connection and engine"""
        try:
            self.engine = create_engine(
                self.connection_string,
                pool_size=10,
                max_overflow=20,
                pool_timeout=30,
                pool_recycle=3600,
                echo=False
            )
            
            self.metadata = MetaData(schema=self.schema_name)
            
            # Test connection
            with self.engine.connect() as conn:
                conn.execute(sa.text("SELECT 1"))
            
            self.logger.info(f"Database connection established: {self.schema_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database connection: {e}")
            raise
    
    def _ensure_schema_exists(self):
        """Ensure the analysis schema exists"""
        try:
            with self.engine.connect() as conn:
                # Check if schema exists
                result = conn.execute(sa.text(
                    "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
                ), {"schema": self.schema_name})
                
                if not result.fetchone():
                    # Create schema
                    conn.execute(sa.text(f"CREATE SCHEMA {self.schema_name}"))
                    conn.commit()
                    self.logger.info(f"Created schema: {self.schema_name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to ensure schema exists: {e}")
            raise
    
    def _define_table_schemas(self):
        """Define all table schemas for analysis storage"""
        
        # Main analysis results table
        self.tables['analysis_results'] = Table(
            'analysis_results',
            self.metadata,
            Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            Column('result_id', String(255), unique=True, nullable=False, index=True),
            Column('analysis_type', String(50), nullable=False, index=True),
            Column('algorithm_name', String(100), nullable=False, index=True),
            Column('input_data_hash', String(64), nullable=False, index=True),
            Column('result_data', JSONB, nullable=False),
            Column('execution_time', Float, nullable=False),
            Column('success', Boolean, nullable=False, index=True),
            Column('error_message', Text, nullable=True),
            Column('created_at', DateTime, nullable=False, default=datetime.utcnow, index=True),
            Column('updated_at', DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow),
            Column('tags', JSONB, nullable=True),
            Column('metadata', JSONB, nullable=True),
            Column('version', String(20), nullable=False, default='1.0.0'),
            schema=self.schema_name
        )
        
        # Performance metrics table
        self.tables['performance_metrics'] = Table(
            'performance_metrics',
            self.metadata,
            Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            Column('metric_date', DateTime, nullable=False, index=True),
            Column('analysis_type', String(50), nullable=False, index=True),
            Column('algorithm_name', String(100), nullable=False, index=True),
            Column('execution_count', Integer, nullable=False),
            Column('average_execution_time', Float, nullable=False),
            Column('success_rate', Float, nullable=False),
            Column('error_count', Integer, nullable=False),
            Column('total_processing_time', Float, nullable=False),
            Column('cache_hit_count', Integer, nullable=False),
            Column('cache_miss_count', Integer, nullable=False),
            Column('created_at', DateTime, nullable=False, default=datetime.utcnow),
            schema=self.schema_name
        )
        
        # Analysis workflows table
        self.tables['analysis_workflows'] = Table(
            'analysis_workflows',
            self.metadata,
            Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            Column('workflow_id', String(255), unique=True, nullable=False, index=True),
            Column('workflow_name', String(100), nullable=False),
            Column('workflow_definition', JSONB, nullable=False),
            Column('execution_results', JSONB, nullable=True),
            Column('total_execution_time', Float, nullable=True),
            Column('success', Boolean, nullable=True, index=True),
            Column('created_at', DateTime, nullable=False, default=datetime.utcnow, index=True),
            Column('completed_at', DateTime, nullable=True),
            Column('metadata', JSONB, nullable=True),
            schema=self.schema_name
        )
        
        # Storage statistics table
        self.tables['storage_statistics'] = Table(
            'storage_statistics',
            self.metadata,
            Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
            Column('snapshot_date', DateTime, nullable=False, index=True),
            Column('total_results', Integer, nullable=False),
            Column('storage_size_bytes', Float, nullable=False),
            Column('average_query_time_ms', Float, nullable=False),
            Column('cache_hit_rate', Float, nullable=False),
            Column('results_by_type', JSONB, nullable=False),
            Column('error_rate', Float, nullable=False),
            Column('oldest_result_date', DateTime, nullable=True),
            Column('newest_result_date', DateTime, nullable=True),
            schema=self.schema_name
        )
        
        # Create composite indexes for performance
        self._create_indexes()
    
    def _create_indexes(self):
        """Create performance-optimized indexes"""
        
        # Composite indexes for analysis_results
        Index(
            'idx_analysis_type_created',
            self.tables['analysis_results'].c.analysis_type,
            self.tables['analysis_results'].c.created_at,
            postgresql_using='btree'
        )
        
        Index(
            'idx_algorithm_success_created',
            self.tables['analysis_results'].c.algorithm_name,
            self.tables['analysis_results'].c.success,
            self.tables['analysis_results'].c.created_at,
            postgresql_using='btree'
        )
        
        Index(
            'idx_input_hash_created',
            self.tables['analysis_results'].c.input_data_hash,
            self.tables['analysis_results'].c.created_at,
            postgresql_using='btree'
        )
        
        # JSONB indexes for metadata searching
        Index(
            'idx_result_data_gin',
            self.tables['analysis_results'].c.result_data,
            postgresql_using='gin'
        )
        
        Index(
            'idx_metadata_gin',
            self.tables['analysis_results'].c.metadata,
            postgresql_using='gin'
        )
        
        # Performance metrics indexes
        Index(
            'idx_perf_metrics_date_type',
            self.tables['performance_metrics'].c.metric_date,
            self.tables['performance_metrics'].c.analysis_type,
            postgresql_using='btree'
        )
    
    def create_tables(self, drop_existing: bool = False):
        """Create all analysis storage tables"""
        try:
            if drop_existing:
                self.metadata.drop_all(self.engine)
                self.logger.warning("Dropped existing tables")
            
            self.metadata.create_all(self.engine)
            self.logger.info("Created all analysis storage tables")
            
            # Create additional database objects
            self._create_functions()
            self._create_triggers()
            
        except Exception as e:
            self.logger.error(f"Failed to create tables: {e}")
            raise
    
    def _create_functions(self):
        """Create useful database functions"""
        try:
            with self.engine.connect() as conn:
                # Function to calculate storage metrics
                storage_metrics_function = f"""
                CREATE OR REPLACE FUNCTION {self.schema_name}.calculate_storage_metrics()
                RETURNS TABLE(
                    total_results INTEGER,
                    storage_size_mb FLOAT,
                    oldest_result TIMESTAMP,
                    newest_result TIMESTAMP,
                    success_rate FLOAT
                ) AS $$
                BEGIN
                    RETURN QUERY
                    SELECT 
                        COUNT(*)::INTEGER as total_results,
                        (pg_total_relation_size('{self.schema_name}.analysis_results'::regclass) / 1024.0 / 1024.0)::FLOAT as storage_size_mb,
                        MIN(created_at) as oldest_result,
                        MAX(created_at) as newest_result,
                        (COUNT(CASE WHEN success THEN 1 END)::FLOAT / COUNT(*)::FLOAT) as success_rate
                    FROM {self.schema_name}.analysis_results;
                END;
                $$ LANGUAGE plpgsql;
                """
                
                conn.execute(sa.text(storage_metrics_function))
                conn.commit()
                
                # Function to clean old results
                cleanup_function = f"""
                CREATE OR REPLACE FUNCTION {self.schema_name}.cleanup_old_results(days_to_keep INTEGER)
                RETURNS INTEGER AS $$
                DECLARE
                    deleted_count INTEGER;
                BEGIN
                    DELETE FROM {self.schema_name}.analysis_results 
                    WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
                    
                    GET DIAGNOSTICS deleted_count = ROW_COUNT;
                    RETURN deleted_count;
                END;
                $$ LANGUAGE plpgsql;
                """
                
                conn.execute(sa.text(cleanup_function))
                conn.commit()
                
                self.logger.info("Created database functions")
                
        except Exception as e:
            self.logger.error(f"Failed to create functions: {e}")
    
    def _create_triggers(self):
        """Create database triggers for automation"""
        try:
            with self.engine.connect() as conn:
                # Trigger to update statistics automatically
                stats_trigger = f"""
                CREATE OR REPLACE FUNCTION {self.schema_name}.update_statistics_trigger()
                RETURNS TRIGGER AS $$
                BEGIN
                    -- Update daily statistics
                    INSERT INTO {self.schema_name}.storage_statistics (
                        snapshot_date, total_results, storage_size_bytes,
                        average_query_time_ms, cache_hit_rate, results_by_type, error_rate
                    )
                    SELECT 
                        DATE_TRUNC('day', NOW()),
                        COUNT(*),
                        pg_total_relation_size('{self.schema_name}.analysis_results'::regclass),
                        0.0, -- placeholder for query time
                        0.0, -- placeholder for cache hit rate
                        '{{}}'::jsonb, -- placeholder for results by type
                        (1.0 - COUNT(CASE WHEN success THEN 1 END)::FLOAT / COUNT(*)::FLOAT)
                    FROM {self.schema_name}.analysis_results
                    WHERE NOT EXISTS (
                        SELECT 1 FROM {self.schema_name}.storage_statistics 
                        WHERE snapshot_date = DATE_TRUNC('day', NOW())
                    );
                    
                    RETURN NULL;
                END;
                $$ LANGUAGE plpgsql;
                
                CREATE TRIGGER update_statistics_daily
                    AFTER INSERT ON {self.schema_name}.analysis_results
                    FOR EACH STATEMENT
                    EXECUTE FUNCTION {self.schema_name}.update_statistics_trigger();
                """
                
                conn.execute(sa.text(stats_trigger))
                conn.commit()
                
                self.logger.info("Created database triggers")
                
        except Exception as e:
            self.logger.error(f"Failed to create triggers: {e}")
    
    def get_table_info(self) -> Dict[str, Any]:
        """Get information about storage tables"""
        info = {}
        
        try:
            with self.engine.connect() as conn:
                for table_name, table in self.tables.items():
                    # Get row count
                    count_query = sa.text(f"SELECT COUNT(*) FROM {self.schema_name}.{table_name}")
                    row_count = conn.execute(count_query).scalar()
                    
                    # Get table size
                    size_query = sa.text(f"""
                        SELECT pg_size_pretty(pg_total_relation_size('{self.schema_name}.{table_name}'::regclass))
                    """)
                    table_size = conn.execute(size_query).scalar()
                    
                    info[table_name] = {
                        'row_count': row_count,
                        'size': table_size,
                        'columns': len(table.columns),
                        'indexes': len(table.indexes)
                    }
                    
        except Exception as e:
            self.logger.error(f"Failed to get table info: {e}")
            
        return info
    
    def optimize_tables(self):
        """Optimize tables for better performance"""
        try:
            with self.engine.connect() as conn:
                for table_name in self.tables.keys():
                    # Analyze table statistics
                    analyze_query = sa.text(f"ANALYZE {self.schema_name}.{table_name}")
                    conn.execute(analyze_query)
                    
                    # Vacuum table
                    vacuum_query = sa.text(f"VACUUM {self.schema_name}.{table_name}")
                    conn.execute(vacuum_query)
                
                conn.commit()
                self.logger.info("Optimized all tables")
                
        except Exception as e:
            self.logger.error(f"Failed to optimize tables: {e}")
    
    def get_storage_metrics(self) -> StorageMetrics:
        """Get current storage metrics"""
        try:
            with self.engine.connect() as conn:
                # Use the stored function
                metrics_query = sa.text(f"SELECT * FROM {self.schema_name}.calculate_storage_metrics()")
                result = conn.execute(metrics_query).fetchone()
                
                if result:
                    # Get results by type
                    type_query = sa.text(f"""
                        SELECT analysis_type, COUNT(*) as count
                        FROM {self.schema_name}.analysis_results
                        GROUP BY analysis_type
                    """)
                    type_results = conn.execute(type_query).fetchall()
                    results_by_type = {row[0]: row[1] for row in type_results}
                    
                    # Calculate average query time (placeholder)
                    avg_query_time = 0.0  # Would need query log analysis
                    
                    # Calculate cache hit rate (placeholder)
                    cache_hit_rate = 0.0  # Would need cache statistics
                    
                    return StorageMetrics(
                        total_results=result[0],
                        storage_size_mb=result[1],
                        average_query_time=avg_query_time,
                        cache_hit_rate=cache_hit_rate,
                        oldest_result=result[2],
                        newest_result=result[3],
                        results_by_type=results_by_type,
                        error_rate=1.0 - result[4]
                    )
                else:
                    return StorageMetrics(
                        total_results=0,
                        storage_size_mb=0.0,
                        average_query_time=0.0,
                        cache_hit_rate=0.0,
                        oldest_result=None,
                        newest_result=None,
                        results_by_type={},
                        error_rate=0.0
                    )
                    
        except Exception as e:
            self.logger.error(f"Failed to get storage metrics: {e}")
            raise
    
    def cleanup_old_results(self, days_to_keep: int = 365) -> int:
        """Clean up old analysis results"""
        try:
            with self.engine.connect() as conn:
                cleanup_query = sa.text(f"SELECT {self.schema_name}.cleanup_old_results(:days)")
                result = conn.execute(cleanup_query, {"days": days_to_keep})
                deleted_count = result.scalar()
                conn.commit()
                
                self.logger.info(f"Cleaned up {deleted_count} old results")
                return deleted_count
                
        except Exception as e:
            self.logger.error(f"Failed to cleanup old results: {e}")
            raise

# Export main components
__all__ = [
    'DatabaseSchemaManager',
    'AnalysisResultSchema',
    'StorageMetrics',
    'AnalysisType',
    'StorageStatus'
] 