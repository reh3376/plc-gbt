#!/usr/bin/env python3
"""
Performance Optimizer Module
Created: January 1, 2025
Purpose: Performance optimization and monitoring for PLC-GPT system
"""

import asyncio
import time
import psutil
import gc
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import threading
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# Neo4j
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

# Qdrant
try:
    from qdrant_client import QdrantClient
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    disk_io_read: int
    disk_io_write: int
    network_bytes_sent: int
    network_bytes_recv: int
    active_connections: int
    query_response_time_ms: float
    throughput_ops_per_sec: float
    error_rate_percent: float
    
@dataclass
class DatabaseMetrics:
    """Database-specific performance metrics"""
    connection_pool_size: int
    active_queries: int
    query_queue_size: int
    avg_query_time_ms: float
    cache_hit_ratio: float
    index_usage_percent: float
    storage_size_mb: float

@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    category: str  # 'query', 'indexing', 'caching', 'scaling'
    priority: str  # 'high', 'medium', 'low'
    description: str
    impact: str
    implementation: str
    estimated_improvement: str

class PerformanceOptimizer:
    """
    Comprehensive performance optimization system for PLC-GPT.
    
    Features:
    - Real-time performance monitoring
    - Database query optimization
    - Caching strategy optimization
    - Resource usage optimization
    - Automatic tuning recommendations
    - Load balancing and scaling advice
    """
    
    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        monitoring_interval: int = 30
    ):
        """
        Initialize performance optimizer.
        
        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            monitoring_interval: Monitoring interval in seconds
        """
        # Database connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50
        )
        
        if QDRANT_AVAILABLE:
            self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        else:
            self.qdrant_client = None
            
        # Performance tracking
        self.monitoring_interval = monitoring_interval
        self.metrics_history = []
        self.recommendations = []
        self.optimization_rules = self._load_optimization_rules()
        
        # System resources
        self.process = psutil.Process()
        self.cpu_count = mp.cpu_count()
        self.memory_total = psutil.virtual_memory().total
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'query_time_ms': 500.0,
            'error_rate_percent': 5.0,
            'cache_hit_ratio': 0.8
        }
        
        # Optimization state
        self.is_monitoring = False
        self.monitor_thread = None
        
        logger.info("PerformanceOptimizer initialized",
                   cpu_count=self.cpu_count,
                   memory_gb=round(self.memory_total / (1024**3), 2))
    
    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            logger.warning("Performance monitoring already running")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Performance monitoring started",
                   interval_seconds=self.monitoring_interval)
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
            
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.metrics_history = [
                    m for m in self.metrics_history 
                    if m.timestamp > cutoff_time
                ]
                
                # Check for performance issues
                self._analyze_performance(metrics)
                
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                time.sleep(self.monitoring_interval)
    
    def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk_io = psutil.disk_io_counters()
            network_io = psutil.net_io_counters()
            
            # Database metrics
            neo4j_metrics = self._collect_neo4j_metrics()
            qdrant_metrics = self._collect_qdrant_metrics()
            
            metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_mb=memory.used / (1024 * 1024),
                disk_io_read=disk_io.read_bytes if disk_io else 0,
                disk_io_write=disk_io.write_bytes if disk_io else 0,
                network_bytes_sent=network_io.bytes_sent if network_io else 0,
                network_bytes_recv=network_io.bytes_recv if network_io else 0,
                active_connections=neo4j_metrics.get('active_connections', 0),
                query_response_time_ms=neo4j_metrics.get('avg_query_time_ms', 0),
                throughput_ops_per_sec=self._calculate_throughput(),
                error_rate_percent=self._calculate_error_rate()
            )
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to collect metrics", error=str(e))
            # Return default metrics
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0, memory_percent=0, memory_mb=0,
                disk_io_read=0, disk_io_write=0,
                network_bytes_sent=0, network_bytes_recv=0,
                active_connections=0, query_response_time_ms=0,
                throughput_ops_per_sec=0, error_rate_percent=0
            )
    
    def _collect_neo4j_metrics(self) -> Dict[str, Any]:
        """Collect Neo4j performance metrics"""
        metrics = {}
        
        try:
            with self.neo4j_driver.session() as session:
                # Query execution stats
                result = session.run("""
                    CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Transactions')
                    YIELD attributes
                    RETURN attributes.NumberOfOpenTransactions as open_transactions
                """)
                
                for record in result:
                    metrics['active_connections'] = record.get('open_transactions', 0)
                    break
                
                # Cache statistics
                cache_result = session.run("""
                    CALL dbms.queryJmx('org.neo4j:instance=kernel#0,name=Page cache')
                    YIELD attributes
                    RETURN attributes.HitRatio as hit_ratio
                """)
                
                for record in cache_result:
                    metrics['cache_hit_ratio'] = record.get('hit_ratio', 0)
                    break
                    
        except Exception as e:
            logger.warning("Failed to collect Neo4j metrics", error=str(e))
            
        return metrics
    
    def _collect_qdrant_metrics(self) -> Dict[str, Any]:
        """Collect Qdrant performance metrics"""
        metrics = {}
        
        if not self.qdrant_client:
            return metrics
            
        try:
            collections = self.qdrant_client.get_collections()
            metrics['collection_count'] = len(collections.collections)
            
            total_points = 0
            total_memory = 0
            
            for collection in collections.collections:
                info = self.qdrant_client.get_collection(collection.name)
                total_points += info.points_count or 0
                # Estimate memory usage
                total_memory += (info.points_count or 0) * 3072 * 4  # 3072 dims * 4 bytes
                
            metrics['total_vectors'] = total_points
            metrics['estimated_memory_mb'] = total_memory / (1024 * 1024)
            
        except Exception as e:
            logger.warning("Failed to collect Qdrant metrics", error=str(e))
            
        return metrics
    
    def _calculate_throughput(self) -> float:
        """Calculate current throughput in operations per second"""
        if len(self.metrics_history) < 2:
            return 0.0
            
        # Simple calculation based on recent activity
        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements
        if len(recent_metrics) < 2:
            return 0.0
            
        time_span = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds()
        if time_span <= 0:
            return 0.0
            
        # Estimate operations from network activity changes
        network_ops = recent_metrics[-1].network_bytes_recv - recent_metrics[0].network_bytes_recv
        estimated_ops = network_ops / 1024  # Rough estimate: 1KB per operation
        
        return estimated_ops / time_span
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate percentage"""
        # This would need to be integrated with actual error tracking
        # For now, return a placeholder
        return 0.0
    
    def _analyze_performance(self, metrics: PerformanceMetrics):
        """Analyze performance metrics and generate recommendations"""
        recommendations = []
        
        # CPU analysis
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            recommendations.append(OptimizationRecommendation(
                category='scaling',
                priority='high',
                description=f'High CPU usage: {metrics.cpu_percent:.1f}%',
                impact='Query performance degradation',
                implementation='Consider horizontal scaling or CPU optimization',
                estimated_improvement='20-40% performance gain'
            ))
        
        # Memory analysis
        if metrics.memory_percent > self.thresholds['memory_percent']:
            recommendations.append(OptimizationRecommendation(
                category='caching',
                priority='high',
                description=f'High memory usage: {metrics.memory_percent:.1f}%',
                impact='Risk of memory exhaustion and crashes',
                implementation='Optimize caching strategy, increase RAM, or implement memory cleanup',
                estimated_improvement='15-30% memory reduction'
            ))
        
        # Query performance analysis
        if metrics.query_response_time_ms > self.thresholds['query_time_ms']:
            recommendations.append(OptimizationRecommendation(
                category='query',
                priority='medium',
                description=f'Slow query response: {metrics.query_response_time_ms:.1f}ms',
                impact='Poor user experience',
                implementation='Add indexes, optimize queries, or implement query caching',
                estimated_improvement='30-60% faster queries'
            ))
        
        # Add new recommendations to list
        for rec in recommendations:
            if not any(existing.description == rec.description for existing in self.recommendations):
                self.recommendations.append(rec)
                logger.warning("Performance issue detected",
                             category=rec.category,
                             priority=rec.priority,
                             description=rec.description)
    
    def optimize_neo4j_queries(self) -> List[str]:
        """Optimize Neo4j queries and indexes"""
        optimizations = []
        
        try:
            with self.neo4j_driver.session() as session:
                # Check for missing indexes
                result = session.run("""
                    CALL db.indexes() YIELD name, labelsOrTypes, properties, state
                    RETURN name, labelsOrTypes, properties, state
                """)
                
                existing_indexes = set()
                for record in result:
                    label = record['labelsOrTypes'][0] if record['labelsOrTypes'] else ''
                    props = record['properties']
                    existing_indexes.add(f"{label}.{'.'.join(props)}")
                
                # Recommend common indexes
                recommended_indexes = [
                    ('PLCProgram', 'name'),
                    ('Routine', 'name'),
                    ('AOI', 'name'),
                    ('UDT', 'name'),
                    ('Device', 'catalog_number'),
                    ('SpecDoc', 'title'),
                    ('QuestionAnswer', 'embedding_id')
                ]
                
                for label, prop in recommended_indexes:
                    index_key = f"{label}.{prop}"
                    if index_key not in existing_indexes:
                        create_query = f"CREATE INDEX FOR (n:{label}) ON (n.{prop})"
                        try:
                            session.run(create_query)
                            optimizations.append(f"Created index: {index_key}")
                            logger.info("Created index", label=label, property=prop)
                        except Exception as e:
                            logger.warning("Failed to create index", 
                                         label=label, property=prop, error=str(e))
                
                # Analyze query plans for slow queries
                self._analyze_query_plans(session, optimizations)
                
        except Exception as e:
            logger.error("Failed to optimize Neo4j", error=str(e))
            
        return optimizations
    
    def optimize_qdrant_performance(self) -> List[str]:
        """Optimize Qdrant vector database performance"""
        optimizations = []
        
        if not self.qdrant_client:
            return optimizations
            
        try:
            collections = self.qdrant_client.get_collections()
            
            for collection in collections.collections:
                collection_name = collection.name
                info = self.qdrant_client.get_collection(collection_name)
                
                # Check collection configuration
                if info.config.params.vectors.distance.value != 'Cosine':
                    optimizations.append(f"Consider using Cosine distance for {collection_name}")
                
                # Check if HNSW parameters are optimal
                hnsw_config = info.config.hnsw_config
                if hnsw_config.m < 16:
                    optimizations.append(f"Increase HNSW M parameter for {collection_name} (current: {hnsw_config.m})")
                
                if hnsw_config.ef_construct < 100:
                    optimizations.append(f"Increase HNSW ef_construct for {collection_name} (current: {hnsw_config.ef_construct})")
                
                # Check point count vs memory
                points_count = info.points_count or 0
                if points_count > 100000:
                    optimizations.append(f"Consider partitioning {collection_name} ({points_count} points)")
                    
        except Exception as e:
            logger.error("Failed to optimize Qdrant", error=str(e))
            
        return optimizations
    
    def _analyze_query_plans(self, session, optimizations: List[str]):
        """Analyze Neo4j query execution plans"""
        try:
            # Common problematic patterns
            test_queries = [
                "MATCH (n) WHERE n.name CONTAINS 'test' RETURN count(n)",
                "MATCH (a)-[r]->(b) RETURN count(r)",
                "MATCH (p:PLCProgram)-[:CONTAINS*1..3]-(c) RETURN count(c)"
            ]
            
            for query in test_queries:
                try:
                    result = session.run(f"EXPLAIN {query}")
                    plan = result.consume().plan
                    
                    # Check for table scans
                    if self._has_table_scan(plan):
                        optimizations.append(f"Query has table scan: {query[:50]}...")
                        
                except Exception:
                    continue  # Skip failed queries
                    
        except Exception as e:
            logger.warning("Failed to analyze query plans", error=str(e))
    
    def _has_table_scan(self, plan) -> bool:
        """Check if query plan contains table scans"""
        # Simplified check for NodeByLabelScan without index
        return 'NodeByLabelScan' in str(plan)
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
            
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_query_time = sum(m.query_response_time_ms for m in recent_metrics) / len(recent_metrics)
        
        # Performance score (0-100)
        cpu_score = max(0, 100 - avg_cpu)
        memory_score = max(0, 100 - avg_memory)
        query_score = max(0, 100 - (avg_query_time / 10))  # 1000ms = 0 score
        overall_score = (cpu_score + memory_score + query_score) / 3
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_performance_score": round(overall_score, 1),
            "metrics_summary": {
                "avg_cpu_percent": round(avg_cpu, 1),
                "avg_memory_percent": round(avg_memory, 1),
                "avg_query_time_ms": round(avg_query_time, 1),
                "total_metrics_collected": len(self.metrics_history)
            },
            "recommendations": [
                {
                    "category": rec.category,
                    "priority": rec.priority,
                    "description": rec.description,
                    "impact": rec.impact,
                    "implementation": rec.implementation,
                    "estimated_improvement": rec.estimated_improvement
                }
                for rec in self.recommendations[-10:]  # Last 10 recommendations
            ],
            "system_info": {
                "cpu_count": self.cpu_count,
                "memory_total_gb": round(self.memory_total / (1024**3), 2),
                "monitoring_interval_seconds": self.monitoring_interval
            }
        }
        
        return report
    
    def apply_auto_optimizations(self) -> Dict[str, Any]:
        """Apply safe automatic optimizations"""
        results = {
            "neo4j_optimizations": [],
            "qdrant_optimizations": [],
            "system_optimizations": []
        }
        
        try:
            # Apply Neo4j optimizations
            neo4j_opts = self.optimize_neo4j_queries()
            results["neo4j_optimizations"] = neo4j_opts
            
            # Apply Qdrant optimizations (recommendations only, no auto-changes)
            qdrant_opts = self.optimize_qdrant_performance()
            results["qdrant_optimizations"] = qdrant_opts
            
            # Apply system optimizations
            system_opts = self._apply_system_optimizations()
            results["system_optimizations"] = system_opts
            
            logger.info("Auto-optimizations applied",
                       neo4j_count=len(neo4j_opts),
                       qdrant_count=len(qdrant_opts),
                       system_count=len(system_opts))
            
        except Exception as e:
            logger.error("Failed to apply auto-optimizations", error=str(e))
            results["error"] = str(e)
            
        return results
    
    def _apply_system_optimizations(self) -> List[str]:
        """Apply system-level optimizations"""
        optimizations = []
        
        try:
            # Force garbage collection
            gc.collect()
            optimizations.append("Performed garbage collection")
            
            # Clear query cache if memory is high
            if len(self.metrics_history) > 0:
                latest = self.metrics_history[-1]
                if latest.memory_percent > 85:
                    # This would clear application caches
                    optimizations.append("Memory usage high - recommend clearing caches")
                    
        except Exception as e:
            logger.warning("System optimization failed", error=str(e))
            
        return optimizations
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load optimization rules and thresholds"""
        return {
            "query_timeout_ms": 30000,
            "max_query_complexity": 1000,
            "cache_size_mb": 512,
            "connection_pool_size": 50,
            "batch_size": 1000,
            "parallel_workers": min(8, self.cpu_count)
        }
    
    def close(self):
        """Clean up resources"""
        self.stop_monitoring()
        if self.neo4j_driver:
            self.neo4j_driver.close()

# Utility functions for performance optimization
def benchmark_query(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Benchmark a function execution"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    try:
        result = func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    return {
        "success": success,
        "execution_time_ms": (end_time - start_time) * 1000,
        "memory_delta_mb": (end_memory - start_memory) / (1024 * 1024),
        "result": result,
        "error": error
    }

async def benchmark_async_query(func: Callable, *args, **kwargs) -> Dict[str, Any]:
    """Benchmark an async function execution"""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss
    
    try:
        result = await func(*args, **kwargs)
        success = True
        error = None
    except Exception as e:
        result = None
        success = False
        error = str(e)
    
    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss
    
    return {
        "success": success,
        "execution_time_ms": (end_time - start_time) * 1000,
        "memory_delta_mb": (end_memory - start_memory) / (1024 * 1024),
        "result": result,
        "error": error
    } 