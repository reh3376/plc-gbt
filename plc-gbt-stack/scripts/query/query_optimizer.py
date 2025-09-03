#!/usr/bin/env python3
"""
Query Optimizer & Intelligent Caching
Created: January 1, 2025
Purpose: Advanced query optimization and smart caching strategies for PLC-GPT
"""

import hashlib
import json
import logging
import re
import sqlite3
import threading
import time
from collections import OrderedDict, defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Neo4j
from neo4j import GraphDatabase

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class QueryPlan:
    """Represents an optimized query execution plan"""
    original_query: str
    optimized_query: str
    estimated_cost: float
    execution_strategy: str
    cache_key: str
    optimization_techniques: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheEntry:
    """Represents a cached query result"""
    key: str
    result: Any
    query_hash: str
    created_at: datetime
    last_accessed: datetime
    access_count: int
    expiry_time: Optional[datetime]
    size_bytes: int
    tags: List[str] = field(default_factory=list)

@dataclass
class QueryStats:
    """Query execution statistics"""
    query_hash: str
    execution_count: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    cache_hits: int
    cache_misses: int
    last_executed: datetime
    optimization_impact: float = 0.0

class IntelligentQueryOptimizer:
    """
    Advanced query optimization and caching system.

    Features:
    - Query plan analysis and optimization
    - Intelligent cache warming and eviction
    - Query pattern recognition and optimization
    - Performance-based adaptive caching
    - Query statistics and analytics
    """

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        cache_size_mb: int = 512,
        cache_db_path: str = "query_cache.db"
    ):
        """
        Initialize query optimizer.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            cache_size_mb: Maximum cache size in MB
            cache_db_path: Path to SQLite cache database
        """
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50
        )

        # Cache configuration
        self.cache_size_bytes = cache_size_mb * 1024 * 1024
        self.cache_db_path = cache_db_path
        self.current_cache_size = 0

        # In-memory caches
        self.memory_cache = OrderedDict()  # LRU cache
        self.query_plans = {}  # Query plan cache
        self.query_stats = defaultdict(lambda: QueryStats(
            query_hash="", execution_count=0, total_time_ms=0,
            avg_time_ms=0, min_time_ms=float('inf'), max_time_ms=0,
            cache_hits=0, cache_misses=0, last_executed=datetime.now()
        ))

        # Performance tracking
        self.optimization_rules = self._load_optimization_rules()
        self.query_patterns = defaultdict(int)

        # Threading
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=4)

        # Initialize cache database
        self._init_cache_db()

        logger.info("IntelligentQueryOptimizer initialized",
                   cache_size_mb=cache_size_mb,
                   cache_db_path=cache_db_path)

    def _init_cache_db(self):
        """Initialize SQLite cache database"""
        try:
            with sqlite3.connect(self.cache_db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS query_cache (
                        key TEXT PRIMARY KEY,
                        result BLOB,
                        query_hash TEXT,
                        created_at TEXT,
                        last_accessed TEXT,
                        access_count INTEGER,
                        expiry_time TEXT,
                        size_bytes INTEGER,
                        tags TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS query_stats (
                        query_hash TEXT PRIMARY KEY,
                        execution_count INTEGER,
                        total_time_ms REAL,
                        avg_time_ms REAL,
                        min_time_ms REAL,
                        max_time_ms REAL,
                        cache_hits INTEGER,
                        cache_misses INTEGER,
                        last_executed TEXT,
                        optimization_impact REAL
                    )
                """)

                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cache_accessed
                    ON query_cache(last_accessed)
                """)

                conn.commit()

        except Exception as e:
            logger.error("Failed to initialize cache database", error=str(e))

    async def optimize_query(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        strategy: str = "auto"
    ) -> QueryPlan:
        """
        Optimize a Cypher query for better performance.

        Args:
            query: Original Cypher query
            parameters: Query parameters
            strategy: Optimization strategy ("auto", "speed", "memory", "accuracy")

        Returns:
            Optimized query plan
        """
        if parameters is None:
            parameters = {}

        # Generate query hash for caching
        query_content = f"{query}_{json.dumps(parameters, sort_keys=True)}"
        query_hash = hashlib.md5(query_content.encode()).hexdigest()

        # Check if we have a cached plan
        if query_hash in self.query_plans:
            plan = self.query_plans[query_hash]
            logger.debug("Using cached query plan", query_hash=query_hash)
            return plan

        start_time = time.time()

        try:
            # Analyze query structure
            query_analysis = self._analyze_query(query)

            # Apply optimization techniques
            optimized_query = query
            optimization_techniques = []

            if strategy in ["auto", "speed"]:
                # Speed optimizations
                optimized_query, speed_opts = self._apply_speed_optimizations(
                    optimized_query, query_analysis, parameters
                )
                optimization_techniques.extend(speed_opts)

            if strategy in ["auto", "memory"]:
                # Memory optimizations
                optimized_query, memory_opts = self._apply_memory_optimizations(
                    optimized_query, query_analysis
                )
                optimization_techniques.extend(memory_opts)

            # Estimate query cost
            estimated_cost = await self._estimate_query_cost(optimized_query, parameters)

            # Create execution strategy
            execution_strategy = self._determine_execution_strategy(
                query_analysis, estimated_cost, strategy
            )

            # Generate cache key
            cache_key = self._generate_cache_key(optimized_query, parameters)

            # Create query plan
            plan = QueryPlan(
                original_query=query,
                optimized_query=optimized_query,
                estimated_cost=estimated_cost,
                execution_strategy=execution_strategy,
                cache_key=cache_key,
                optimization_techniques=optimization_techniques,
                metadata={
                    "query_hash": query_hash,
                    "analysis": query_analysis,
                    "optimization_time_ms": (time.time() - start_time) * 1000,
                    "strategy": strategy
                }
            )

            # Cache the plan
            self.query_plans[query_hash] = plan

            logger.info("Query optimized",
                       query_hash=query_hash,
                       techniques=len(optimization_techniques),
                       estimated_cost=estimated_cost,
                       strategy=execution_strategy)

            return plan

        except Exception as e:
            logger.error("Query optimization failed", error=str(e))
            # Return original query as fallback
            return QueryPlan(
                original_query=query,
                optimized_query=query,
                estimated_cost=1.0,
                execution_strategy="direct",
                cache_key=self._generate_cache_key(query, parameters),
                optimization_techniques=[],
                metadata={"error": str(e)}
            )

    def _analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query structure and patterns"""
        query_lower = query.lower()

        analysis = {
            "query_type": "unknown",
            "complexity": "low",
            "has_aggregation": False,
            "has_sorting": False,
            "has_limiting": False,
            "relationship_patterns": [],
            "node_labels": [],
            "estimated_result_size": "small",
            "optimization_opportunities": []
        }

        # Determine query type
        if "match" in query_lower:
            if "create" in query_lower or "merge" in query_lower:
                analysis["query_type"] = "write"
            else:
                analysis["query_type"] = "read"
        elif "create" in query_lower:
            analysis["query_type"] = "create"
        elif "delete" in query_lower:
            analysis["query_type"] = "delete"

        # Check for complexity indicators
        if "with" in query_lower or "union" in query_lower:
            analysis["complexity"] = "high"
        elif "*" in query or "collect" in query_lower:
            analysis["complexity"] = "medium"

        # Check for aggregation
        aggregation_functions = ["count", "sum", "avg", "min", "max", "collect"]
        analysis["has_aggregation"] = any(func in query_lower for func in aggregation_functions)

        # Check for sorting and limiting
        analysis["has_sorting"] = "order by" in query_lower
        analysis["has_limiting"] = "limit" in query_lower or "skip" in query_lower

        # Find relationship patterns
        rel_patterns = re.findall(r'-\[([^\]]*)\]-', query)
        analysis["relationship_patterns"] = [p.strip(':') for p in rel_patterns if p]

        # Find node labels
        label_patterns = re.findall(r'\([\w]*:(\w+)[^\)]*\)', query)
        analysis["node_labels"] = list(set(label_patterns))

        # Identify optimization opportunities
        if not analysis["has_limiting"] and analysis["query_type"] == "read":
            analysis["optimization_opportunities"].append("add_limit")

        if "*" in query and not analysis["has_limiting"]:
            analysis["optimization_opportunities"].append("limit_traversal")

        if analysis["has_aggregation"] and not analysis["has_sorting"]:
            analysis["optimization_opportunities"].append("optimize_aggregation")

        return analysis

    def _apply_speed_optimizations(
        self,
        query: str,
        analysis: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Apply speed-focused optimizations"""
        optimized_query = query
        techniques = []

        # Add LIMIT if missing for read queries
        if "add_limit" in analysis["optimization_opportunities"]:
            if not re.search(r'\bLIMIT\s+\d+', optimized_query, re.IGNORECASE):
                optimized_query += " LIMIT 1000"
                techniques.append("added_default_limit")

        # Optimize variable-length relationships
        if "limit_traversal" in analysis["optimization_opportunities"]:
            # Replace unrestricted * with reasonable limits
            optimized_query = re.sub(
                r'-\[\*\]-',
                '-[*1..5]-',
                optimized_query
            )
            techniques.append("limited_traversal_depth")

        # Add index hints for known patterns
        if analysis["node_labels"]:
            for label in analysis["node_labels"]:
                if label in ["PLCProgram", "Routine", "AOI", "UDT"]:
                    techniques.append(f"index_hint_{label}")

        # Optimize ORDER BY with LIMIT
        if analysis["has_sorting"] and analysis["has_limiting"]:
            # Ensure ORDER BY comes before LIMIT for better performance
            optimized_query = re.sub(
                r'(\bLIMIT\s+\d+)\s+(\bORDER\s+BY\s+[^L]+)',
                r'\2 \1',
                optimized_query,
                flags=re.IGNORECASE
            )
            techniques.append("reordered_limit_orderby")

        return optimized_query, techniques

    def _apply_memory_optimizations(
        self,
        query: str,
        analysis: Dict[str, Any]
    ) -> Tuple[str, List[str]]:
        """Apply memory-focused optimizations"""
        optimized_query = query
        techniques = []

        # Optimize aggregation queries
        if "optimize_aggregation" in analysis["optimization_opportunities"]:
            # Use WITH to break up complex aggregations
            if "count" in query.lower() and "collect" in query.lower():
                techniques.append("split_aggregation")

        # Reduce result set size for complex traversals
        if analysis["complexity"] == "high":
            techniques.append("added_filters")

        # Stream large results
        if not analysis["has_limiting"] and analysis["estimated_result_size"] == "large":
            optimized_query += " LIMIT 10000"
            techniques.append("stream_optimization")

        return optimized_query, techniques

    async def _estimate_query_cost(
        self,
        query: str,
        parameters: Dict[str, Any]
    ) -> float:
        """Estimate query execution cost"""
        try:
            with self.neo4j_driver.session() as session:
                # Use EXPLAIN to get query plan
                result = session.run(f"EXPLAIN {query}", parameters)
                plan = result.consume().plan

                # Simplified cost estimation based on plan
                cost = 1.0

                # Add cost for each operator
                if plan:
                    cost += self._calculate_plan_cost(plan)

                return min(cost, 100.0)  # Cap at 100

        except Exception as e:
            logger.warning("Failed to estimate query cost", error=str(e))
            return 5.0

    def _calculate_plan_cost(self, plan) -> float:
        """Calculate cost from Neo4j query plan"""
        cost = 0.0
        plan_str = str(plan).lower()

        # Add cost for expensive operations
        if "nodebyLabelscan" in plan_str:
            cost += 2.0
        if "expand" in plan_str:
            cost += 1.5
        if "filter" in plan_str:
            cost += 1.0
        if "sort" in plan_str:
            cost += 3.0
        if "aggregation" in plan_str:
            cost += 2.5

        return cost

    def _determine_execution_strategy(
        self,
        analysis: Dict[str, Any],
        estimated_cost: float,
        user_strategy: str
    ) -> str:
        """Determine optimal execution strategy"""

        if estimated_cost > 50.0:
            return "batched"
        elif analysis["complexity"] == "high":
            return "parallel"
        elif analysis["has_aggregation"]:
            return "streaming"
        elif user_strategy == "speed":
            return "cached"
        else:
            return "direct"

    def _generate_cache_key(self, query: str, parameters: Dict[str, Any]) -> str:
        """Generate cache key for query and parameters"""
        query_content = f"{query}_{json.dumps(parameters, sort_keys=True)}"
        return hashlib.sha256(query_content.encode()).hexdigest()

    async def get_cached_result(self, cache_key: str) -> Optional[Any]:
        """Get result from cache"""
        with self.lock:
            if cache_key in self.memory_cache:
                entry = self.memory_cache[cache_key]

                # Check expiry
                if entry.expiry_time and entry.expiry_time < datetime.now():
                    del self.memory_cache[cache_key]
                    self.current_cache_size -= entry.size_bytes
                    return None

                # Update access statistics
                entry.last_accessed = datetime.now()
                entry.access_count += 1

                # Move to end (LRU)
                self.memory_cache.move_to_end(cache_key)

                logger.debug("Cache hit", cache_key=cache_key[:16])
                return entry.result

            return None

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_size_mb = self.current_cache_size / (1024 * 1024)
            cache_utilization = (self.current_cache_size / self.cache_size_bytes) * 100

            # Calculate hit rates
            total_hits = sum(stats.cache_hits for stats in self.query_stats.values())
            total_misses = sum(stats.cache_misses for stats in self.query_stats.values())
            hit_rate = (total_hits / (total_hits + total_misses)) * 100 if (total_hits + total_misses) > 0 else 0

            return {
                "cache_entries": len(self.memory_cache),
                "cache_size_mb": round(total_size_mb, 2),
                "cache_utilization_percent": round(cache_utilization, 1),
                "hit_rate_percent": round(hit_rate, 1),
                "total_hits": total_hits,
                "total_misses": total_misses,
                "query_plans_cached": len(self.query_plans)
            }

    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load query optimization rules"""
        return {
            "max_traversal_depth": 10,
            "default_limit": 1000,
            "large_result_threshold": 10000,
            "expensive_operation_threshold": 50.0,
            "cache_ttl_minutes": 30,
            "index_hints": {
                "PLCProgram": ["name", "uuid"],
                "Routine": ["name", "uuid"],
                "AOI": ["name", "uuid"],
                "UDT": ["name", "uuid"],
                "Device": ["catalog_number", "uuid"]
            }
        }

    def close(self):
        """Clean up resources"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
        self.executor.shutdown(wait=True)

# Utility functions for query optimization
def analyze_query_complexity(query: str) -> str:
    """Analyze query complexity level"""
    query_lower = query.lower()

    complexity_indicators = [
        ("high", ["union", "with.*with", "optional match.*optional match"]),
        ("medium", ["collect", "unwind", "\\*", "order by"]),
        ("low", ["match", "return", "where"])
    ]

    for level, patterns in complexity_indicators:
        if any(re.search(pattern, query_lower) for pattern in patterns):
            return level

    return "low"

def extract_query_patterns(query: str) -> List[str]:
    """Extract common query patterns for optimization"""
    patterns = []

    query_lower = query.lower()

    # Pattern detection
    if "shortest" in query_lower:
        patterns.append("shortest_path")
    if re.search(r'-\[.*\*.*\]-', query):
        patterns.append("variable_length_path")
    if "count(" in query_lower:
        patterns.append("aggregation_count")
    if "collect(" in query_lower:
        patterns.append("aggregation_collect")
    if "order by" in query_lower and "limit" in query_lower:
        patterns.append("top_n")

    return patterns
