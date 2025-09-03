#!/usr/bin/env python3
"""
🔍 Comprehensive Database Audit System - AI Task Orchestrator Implementation

Following AI Task Orchestrator Guide methodology to systematically audit all 4 databases
used in the PLC Memory Management System for data integrity, completeness, and performance.

Comprehensive validation across:
- Neo4j (medium-term memory/knowledge graph)
- PostgreSQL (long-term memory/persistent storage)
- Redis (short-term memory/context window)
- Qdrant (vector search/pattern matching)

Author: AI Task Orchestrator
Created: 2025-01-10
Purpose: Ensure complete data integrity across all memory tiers
Task Complexity: MODERATE - Multiple database systems with cross-validation
"""

import asyncio
import json
import logging
import sys
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType
from persistent_redis_manager import get_persistent_redis_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DatabaseAuditResult:
    """Audit result for a single database"""
    database_type: DatabaseType
    connection_status: str
    data_integrity_score: float
    total_records: int
    expected_records: int
    data_completeness_percentage: float
    performance_metrics: Dict[str, Any]
    issues_found: List[str]
    recommendations: List[str]
    audit_timestamp: datetime

@dataclass
class CrossDatabaseValidation:
    """Cross-database validation results"""
    data_consistency_score: float
    missing_cross_references: List[str]
    orphaned_records: List[str]
    synchronization_issues: List[str]
    recommendations: List[str]

class ComprehensiveDatabaseAuditor:
    """
    🎯 Comprehensive Database Auditor

    Systematically audits all databases in the PLC Memory Management System
    following AI Task Orchestrator methodology for thorough validation.
    """

    def __init__(self):
        self.db_manager = None
        self.audit_results = {}
        self.cross_validation_results = None
        self.audit_session_id = f"audit_{int(datetime.now().timestamp())}"

    async def initialize_audit_session(self) -> bool:
        """Initialize audit session with all database connections"""
        try:
            print("🚀 Initializing Comprehensive Database Audit Session")
            print("=" * 60)

            self.db_manager = DatabaseManager()
            connection_results = await self.db_manager.initialize_all_connections()

            connected_dbs = sum(1 for result in connection_results.values() if result)
            total_dbs = len(connection_results)

            print(f"📊 Database Connections: {connected_dbs}/{total_dbs}")
            for db_type, connected in connection_results.items():
                status = "✅ Connected" if connected else "❌ Failed"
                print(f"   {db_type.value}: {status}")

            if connected_dbs < total_dbs:
                print(f"⚠️  Warning: {total_dbs - connected_dbs} databases failed to connect")

            return connected_dbs > 0

        except Exception as e:
            logger.error(f"Failed to initialize audit session: {str(e)}")
            return False

    async def audit_neo4j_database(self) -> DatabaseAuditResult:
        """
        Comprehensive Neo4j audit following recent datetime fix validation
        """
        print("\n🔍 Auditing Neo4j Database (Medium-Term Memory)")
        print("-" * 50)

        issues_found = []
        recommendations = []
        performance_metrics = {}

        try:
            if not self.db_manager.connections[DatabaseType.NEO4J]:
                return DatabaseAuditResult(
                    database_type=DatabaseType.NEO4J,
                    connection_status="FAILED",
                    data_integrity_score=0.0,
                    total_records=0,
                    expected_records=0,
                    data_completeness_percentage=0.0,
                    performance_metrics={},
                    issues_found=["Connection failed"],
                    recommendations=["Fix database connection"],
                    audit_timestamp=datetime.now()
                )

            with self.db_manager.connections[DatabaseType.NEO4J].session() as session:
                # 1. Basic node counts and distribution
                start_time = datetime.now()

                result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                total_nodes = result.single()['total_nodes']

                query_time = (datetime.now() - start_time).total_seconds() * 1000
                performance_metrics['basic_query_time_ms'] = query_time

                print(f"📊 Total nodes: {total_nodes}")

                # 2. Node type distribution
                result = session.run("CALL db.labels()")
                labels = [record['label'] for record in result]

                node_distribution = {}
                for label in labels:
                    result = session.run(f"MATCH (n:`{label}`) RETURN count(n) as count")
                    count = result.single()['count']
                    node_distribution[label] = count
                    print(f"   {label}: {count} nodes")

                # 3. Data integrity checks
                print("\n🔬 Data Integrity Analysis:")

                # Check for nodes with missing critical properties
                critical_checks = {
                    "PythonFile": ["name", "path"],
                    "Documentation": ["title", "path"],
                    "CodeModule": ["name"]
                }

                integrity_issues = 0
                for label, required_props in critical_checks.items():
                    if label in node_distribution:
                        for prop in required_props:
                            result = session.run(f"""
                                MATCH (n:`{label}`)
                                WHERE n.`{prop}` IS NULL OR n.`{prop}` = ''
                                RETURN count(n) as missing_count
                            """)
                            missing_count = result.single()['missing_count']
                            if missing_count > 0:
                                integrity_issues += missing_count
                                issues_found.append(f"{missing_count} {label} nodes missing {prop} property")

                print(f"   Integrity issues found: {integrity_issues}")

                # 4. Recent ingestion validation (post datetime fix)
                result = session.run("""
                    MATCH (n:PythonFile)
                    WHERE n.path CONTAINS 'plc_memory_cli.py' OR n.path CONTAINS 'file_processors.py'
                    RETURN count(n) as recent_files
                """)
                recent_files = result.single()['recent_files']
                print(f"   Recent critical files: {recent_files}")

                if recent_files < 2:
                    issues_found.append("Missing recent critical files (plc_memory_cli.py, file_processors.py)")

                # 5. Relationship analysis
                result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
                total_relationships = result.single()['total_relationships']
                print(f"   Total relationships: {total_relationships}")

                # 6. Performance benchmarks
                start_time = datetime.now()
                result = session.run("""
                    MATCH (n:PythonFile)
                    WHERE n.functions_count > 10
                    RETURN n.name, n.functions_count
                    ORDER BY n.functions_count DESC
                    LIMIT 10
                """)
                complex_files = list(result)
                complex_query_time = (datetime.now() - start_time).total_seconds() * 1000
                performance_metrics['complex_query_time_ms'] = complex_query_time

                print(f"   Complex files found: {len(complex_files)}")
                print(f"   Query performance: {complex_query_time:.1f}ms")

                # Calculate scores
                expected_python_files = 100  # Based on recent ingestion
                python_file_count = node_distribution.get('PythonFile', 0)
                data_completeness = min(100.0, (python_file_count / expected_python_files) * 100)

                integrity_score = max(0.0, 100.0 - (integrity_issues * 2))  # 2% penalty per issue

                # Recommendations
                if integrity_issues > 0:
                    recommendations.append("Fix missing node properties to improve data integrity")
                if total_relationships < total_nodes * 0.1:
                    recommendations.append("Consider adding more relationships between nodes")
                if complex_query_time > 100:
                    recommendations.append("Consider database indexing optimization")

                return DatabaseAuditResult(
                    database_type=DatabaseType.NEO4J,
                    connection_status="CONNECTED",
                    data_integrity_score=integrity_score,
                    total_records=total_nodes,
                    expected_records=expected_python_files,
                    data_completeness_percentage=data_completeness,
                    performance_metrics=performance_metrics,
                    issues_found=issues_found,
                    recommendations=recommendations,
                    audit_timestamp=datetime.now()
                )

        except Exception as e:
            logger.error(f"Neo4j audit failed: {str(e)}")
            return DatabaseAuditResult(
                database_type=DatabaseType.NEO4J,
                connection_status="ERROR",
                data_integrity_score=0.0,
                total_records=0,
                expected_records=0,
                data_completeness_percentage=0.0,
                performance_metrics={},
                issues_found=[f"Audit failed: {str(e)}"],
                recommendations=["Investigate database connection and query issues"],
                audit_timestamp=datetime.now()
            )

    async def audit_postgresql_database(self) -> DatabaseAuditResult:
        """
        Comprehensive PostgreSQL audit for long-term storage
        """
        print("\n🔍 Auditing PostgreSQL Database (Long-Term Storage)")
        print("-" * 50)

        issues_found = []
        recommendations = []
        performance_metrics = {}

        try:
            if not self.db_manager.connection_pools.get(DatabaseType.POSTGRESQL):
                return DatabaseAuditResult(
                    database_type=DatabaseType.POSTGRESQL,
                    connection_status="FAILED",
                    data_integrity_score=0.0,
                    total_records=0,
                    expected_records=0,
                    data_completeness_percentage=0.0,
                    performance_metrics={},
                    issues_found=["Connection pool not available"],
                    recommendations=["Fix PostgreSQL connection"],
                    audit_timestamp=datetime.now()
                )

            conn = self.db_manager.connection_pools[DatabaseType.POSTGRESQL].getconn()
            try:
                cursor = conn.cursor()

                # 1. Check for expected tables
                print("📊 Table Structure Analysis:")
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
                existing_tables = [row[0] for row in cursor.fetchall()]

                expected_tables = ['python_files', 'documentation', 'configuration_files']
                missing_tables = [table for table in expected_tables if table not in existing_tables]

                print(f"   Existing tables: {len(existing_tables)}")
                print(f"   Expected tables: {len(expected_tables)}")
                print(f"   Missing tables: {missing_tables}")

                if missing_tables:
                    issues_found.extend([f"Missing table: {table}" for table in missing_tables])
                    recommendations.append("Create missing database schema tables")

                # 2. Data analysis for existing tables
                total_records = 0
                for table in existing_tables:
                    if table in expected_tables:
                        try:
                            start_time = datetime.now()
                            cursor.execute(f"SELECT COUNT(*) FROM {table}")
                            count = cursor.fetchone()[0]
                            query_time = (datetime.now() - start_time).total_seconds() * 1000

                            total_records += count
                            print(f"   {table}: {count} records ({query_time:.1f}ms)")

                            performance_metrics[f"{table}_query_time_ms"] = query_time
                            performance_metrics[f"{table}_record_count"] = count

                            # Check for data quality issues
                            if count > 0:
                                cursor.execute(f"SELECT data FROM {table} LIMIT 1")
                                sample_data = cursor.fetchone()[0]

                                # Validate JSON structure
                                try:
                                    if isinstance(sample_data, str):
                                        parsed_data = json.loads(sample_data)
                                    else:
                                        parsed_data = sample_data

                                    if 'metadata' in parsed_data:
                                        metadata = parsed_data['metadata']
                                        # Check for datetime serialization issues
                                        for key, value in metadata.items():
                                            if isinstance(value, str) and 'T' in value and ':' in value:
                                                # Looks like ISO datetime - good!
                                                continue
                                            elif 'time' in key.lower() and not isinstance(value, str):
                                                issues_found.append(f"Potential datetime serialization issue in {table}")

                                except (json.JSONDecodeError, TypeError) as e:
                                    issues_found.append(f"JSON parsing error in {table}: {str(e)}")

                        except Exception as e:
                            issues_found.append(f"Error querying {table}: {str(e)}")

                # 3. Database performance metrics
                start_time = datetime.now()
                cursor.execute("SELECT version()")
                db_version = cursor.fetchone()[0]
                version_query_time = (datetime.now() - start_time).total_seconds() * 1000

                performance_metrics['version_query_time_ms'] = version_query_time
                performance_metrics['database_version'] = db_version

                print(f"   Database version: {db_version}")
                print(f"   Connection response: {version_query_time:.1f}ms")

                # Calculate scores
                expected_records = 100  # Based on recent ingestion
                data_completeness = min(100.0, (total_records / expected_records) * 100) if expected_records > 0 else 0.0
                integrity_score = max(0.0, 100.0 - (len(issues_found) * 10))  # 10% penalty per issue

                # Additional recommendations
                if total_records == 0:
                    recommendations.append("Initialize database schema and run data ingestion")
                if len(missing_tables) > 0:
                    recommendations.append("Run database schema initialization script")

                return DatabaseAuditResult(
                    database_type=DatabaseType.POSTGRESQL,
                    connection_status="CONNECTED",
                    data_integrity_score=integrity_score,
                    total_records=total_records,
                    expected_records=expected_records,
                    data_completeness_percentage=data_completeness,
                    performance_metrics=performance_metrics,
                    issues_found=issues_found,
                    recommendations=recommendations,
                    audit_timestamp=datetime.now()
                )

            finally:
                cursor.close()
                self.db_manager.connection_pools[DatabaseType.POSTGRESQL].putconn(conn)

        except Exception as e:
            logger.error(f"PostgreSQL audit failed: {str(e)}")
            return DatabaseAuditResult(
                database_type=DatabaseType.POSTGRESQL,
                connection_status="ERROR",
                data_integrity_score=0.0,
                total_records=0,
                expected_records=0,
                data_completeness_percentage=0.0,
                performance_metrics={},
                issues_found=[f"Audit failed: {str(e)}"],
                recommendations=["Investigate PostgreSQL connection and schema issues"],
                audit_timestamp=datetime.now()
            )

    async def audit_redis_cache(self) -> DatabaseAuditResult:
        """
        Comprehensive Redis audit for short-term memory and caching
        """
        print("\n🔍 Auditing Redis Database (Short-Term Memory/Cache)")
        print("-" * 50)

        issues_found = []
        recommendations = []
        performance_metrics = {}

        try:
            # Check persistent Redis manager
            persistent_redis = await get_persistent_redis_manager()

            if not persistent_redis or not persistent_redis.is_connected():
                # Fallback to traditional Redis connection
                redis_client = self.db_manager.connections.get(DatabaseType.REDIS)
                if not redis_client or redis_client == "persistent_connection":
                    return DatabaseAuditResult(
                        database_type=DatabaseType.REDIS,
                        connection_status="FAILED",
                        data_integrity_score=0.0,
                        total_records=0,
                        expected_records=0,
                        data_completeness_percentage=0.0,
                        performance_metrics={},
                        issues_found=["Redis connection not available"],
                        recommendations=["Fix Redis connection and persistent manager"],
                        audit_timestamp=datetime.now()
                    )
            else:
                redis_client = persistent_redis.redis_client

            # 1. Connection and basic metrics
            start_time = datetime.now()
            info = redis_client.info()
            info_query_time = (datetime.now() - start_time).total_seconds() * 1000

            print("📊 Redis Server Info:")
            print(f"   Version: {info.get('redis_version', 'unknown')}")
            print(f"   Memory usage: {info.get('used_memory_human', 'unknown')}")
            print(f"   Connected clients: {info.get('connected_clients', 0)}")
            print(f"   Total keys: {info.get('db0', {}).get('keys', 0) if 'db0' in info else 0}")

            performance_metrics['info_query_time_ms'] = info_query_time
            performance_metrics['redis_version'] = info.get('redis_version', 'unknown')
            performance_metrics['memory_usage_bytes'] = info.get('used_memory', 0)
            performance_metrics['connected_clients'] = info.get('connected_clients', 0)

            # 2. Key analysis
            start_time = datetime.now()
            all_keys = redis_client.keys('*')
            keys_query_time = (datetime.now() - start_time).total_seconds() * 1000

            total_keys = len(all_keys)
            print(f"   Key enumeration: {total_keys} keys ({keys_query_time:.1f}ms)")

            performance_metrics['keys_query_time_ms'] = keys_query_time
            performance_metrics['total_keys'] = total_keys

            # 3. Key pattern analysis
            key_patterns = {}
            for key in all_keys[:100]:  # Sample first 100 keys
                key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                pattern = key_str.split(':')[0] if ':' in key_str else 'other'
                key_patterns[pattern] = key_patterns.get(pattern, 0) + 1

            print(f"   Key patterns: {dict(list(key_patterns.items())[:5])}")

            # 4. Performance testing
            test_key = f"audit_test_{self.audit_session_id}"
            test_value = "audit_test_value"

            # SET performance
            start_time = datetime.now()
            redis_client.set(test_key, test_value)
            set_time = (datetime.now() - start_time).total_seconds() * 1000

            # GET performance
            start_time = datetime.now()
            retrieved_value = redis_client.get(test_key)
            get_time = (datetime.now() - start_time).total_seconds() * 1000

            # Cleanup
            redis_client.delete(test_key)

            performance_metrics['set_operation_time_ms'] = set_time
            performance_metrics['get_operation_time_ms'] = get_time

            print(f"   SET performance: {set_time:.2f}ms")
            print(f"   GET performance: {get_time:.2f}ms")

            # 5. Data integrity validation
            if retrieved_value != test_value.encode('utf-8'):
                issues_found.append("Data integrity issue: Retrieved value doesn't match stored value")

            # 6. Memory and performance analysis
            memory_usage_mb = info.get('used_memory', 0) / (1024 * 1024)

            if memory_usage_mb > 100:  # > 100MB
                recommendations.append("Monitor Redis memory usage - consider cleanup policies")

            if get_time > 10:  # > 10ms for simple GET
                issues_found.append("Poor GET performance detected")
                recommendations.append("Investigate Redis performance optimization")

            if total_keys > 10000:
                recommendations.append("Large number of keys - consider key expiration policies")

            # 7. Persistent connection validation
            if persistent_redis:
                health_status = persistent_redis.is_healthy()
                connection_count = persistent_redis.connection_count

                print(f"   Persistent manager: {'Healthy' if health_status else 'Unhealthy'}")
                print(f"   Connection count: {connection_count}")

                if not health_status:
                    issues_found.append("Persistent Redis manager reports unhealthy status")

                performance_metrics['persistent_manager_healthy'] = health_status
                performance_metrics['persistent_connection_count'] = connection_count

            # Calculate scores
            expected_keys = 50  # Expected cache entries
            data_completeness = min(100.0, (total_keys / expected_keys) * 100) if expected_keys > 0 else 100.0
            integrity_score = max(0.0, 100.0 - (len(issues_found) * 15))  # 15% penalty per issue

            return DatabaseAuditResult(
                database_type=DatabaseType.REDIS,
                connection_status="CONNECTED",
                data_integrity_score=integrity_score,
                total_records=total_keys,
                expected_records=expected_keys,
                data_completeness_percentage=data_completeness,
                performance_metrics=performance_metrics,
                issues_found=issues_found,
                recommendations=recommendations,
                audit_timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Redis audit failed: {str(e)}")
            return DatabaseAuditResult(
                database_type=DatabaseType.REDIS,
                connection_status="ERROR",
                data_integrity_score=0.0,
                total_records=0,
                expected_records=0,
                data_completeness_percentage=0.0,
                performance_metrics={},
                issues_found=[f"Audit failed: {str(e)}"],
                recommendations=["Investigate Redis connection and configuration"],
                audit_timestamp=datetime.now()
            )

    async def audit_qdrant_vectors(self) -> DatabaseAuditResult:
        """
        Comprehensive Qdrant audit for vector storage and embeddings
        """
        print("\n🔍 Auditing Qdrant Database (Vector Storage/Pattern Matching)")
        print("-" * 50)

        issues_found = []
        recommendations = []
        performance_metrics = {}

        try:
            qdrant_client = self.db_manager.connections.get(DatabaseType.QDRANT)

            if not qdrant_client:
                return DatabaseAuditResult(
                    database_type=DatabaseType.QDRANT,
                    connection_status="FAILED",
                    data_integrity_score=0.0,
                    total_records=0,
                    expected_records=0,
                    data_completeness_percentage=0.0,
                    performance_metrics={},
                    issues_found=["Qdrant connection not available"],
                    recommendations=["Fix Qdrant connection"],
                    audit_timestamp=datetime.now()
                )

            # 1. Cluster information
            start_time = datetime.now()
            cluster_info = qdrant_client.info()
            info_query_time = (datetime.now() - start_time).total_seconds() * 1000

            print("📊 Qdrant Cluster Info:")
            print(f"   Version: {cluster_info.version if hasattr(cluster_info, 'version') else 'unknown'}")
            print(f"   Info query time: {info_query_time:.1f}ms")

            performance_metrics['info_query_time_ms'] = info_query_time

            # 2. Collections analysis
            start_time = datetime.now()
            collections = qdrant_client.get_collections()
            collections_query_time = (datetime.now() - start_time).total_seconds() * 1000

            collection_names = [collection.name for collection in collections.collections]
            print(f"   Collections: {len(collection_names)}")

            performance_metrics['collections_query_time_ms'] = collections_query_time
            performance_metrics['collection_count'] = len(collection_names)

            total_vectors = 0
            expected_collections = ['python_code', 'documentation', 'configurations']

            for collection_name in collection_names:
                try:
                    start_time = datetime.now()
                    collection_info = qdrant_client.get_collection(collection_name)
                    collection_query_time = (datetime.now() - start_time).total_seconds() * 1000

                    vector_count = collection_info.points_count
                    total_vectors += vector_count

                    print(f"   {collection_name}: {vector_count} vectors ({collection_query_time:.1f}ms)")

                    performance_metrics[f"{collection_name}_query_time_ms"] = collection_query_time
                    performance_metrics[f"{collection_name}_vector_count"] = vector_count

                except Exception as e:
                    issues_found.append(f"Error querying collection {collection_name}: {str(e)}")

            # 3. Check for expected collections
            missing_collections = [col for col in expected_collections if col not in collection_names]
            if missing_collections:
                issues_found.extend([f"Missing collection: {col}" for col in missing_collections])
                recommendations.append("Create missing vector collections for complete ingestion")

            # 4. Vector quality assessment (if vectors exist)
            if total_vectors > 0 and collection_names:
                try:
                    # Test vector search performance
                    test_collection = collection_names[0]
                    test_vector = [0.1] * 384  # Standard embedding dimension

                    start_time = datetime.now()
                    search_results = qdrant_client.search(
                        collection_name=test_collection,
                        query_vector=test_vector,
                        limit=5
                    )
                    search_time = (datetime.now() - start_time).total_seconds() * 1000

                    print(f"   Search performance: {search_time:.1f}ms ({len(search_results)} results)")
                    performance_metrics['search_query_time_ms'] = search_time

                    if search_time > 500:  # > 500ms for vector search
                        issues_found.append("Poor vector search performance detected")
                        recommendations.append("Consider vector index optimization")

                except Exception as e:
                    issues_found.append(f"Vector search test failed: {str(e)}")

            # 5. Storage and indexing analysis
            if total_vectors == 0:
                issues_found.append("No vectors found in any collection")
                recommendations.append("Run vector embedding generation and ingestion")
            elif total_vectors < 50:  # Expected minimum based on file count
                issues_found.append("Vector count lower than expected")
                recommendations.append("Validate embedding generation process")

            # Calculate scores
            expected_vectors = 200  # Based on file count and chunking
            data_completeness = min(100.0, (total_vectors / expected_vectors) * 100) if expected_vectors > 0 else 0.0
            integrity_score = max(0.0, 100.0 - (len(issues_found) * 10))  # 10% penalty per issue

            return DatabaseAuditResult(
                database_type=DatabaseType.QDRANT,
                connection_status="CONNECTED",
                data_integrity_score=integrity_score,
                total_records=total_vectors,
                expected_records=expected_vectors,
                data_completeness_percentage=data_completeness,
                performance_metrics=performance_metrics,
                issues_found=issues_found,
                recommendations=recommendations,
                audit_timestamp=datetime.now()
            )

        except Exception as e:
            logger.error(f"Qdrant audit failed: {str(e)}")
            return DatabaseAuditResult(
                database_type=DatabaseType.QDRANT,
                connection_status="ERROR",
                data_integrity_score=0.0,
                total_records=0,
                expected_records=0,
                data_completeness_percentage=0.0,
                performance_metrics={},
                issues_found=[f"Audit failed: {str(e)}"],
                recommendations=["Investigate Qdrant connection and configuration"],
                audit_timestamp=datetime.now()
            )

    async def validate_cross_database_consistency(self) -> CrossDatabaseValidation:
        """
        Validate data consistency across all databases
        """
        print("\n🔄 Cross-Database Consistency Validation")
        print("-" * 50)

        missing_cross_references = []
        orphaned_records = []
        synchronization_issues = []
        recommendations = []

        try:
            # 1. File consistency check
            neo4j_result = self.audit_results.get(DatabaseType.NEO4J)
            postgres_result = self.audit_results.get(DatabaseType.POSTGRESQL)
            self.audit_results.get(DatabaseType.QDRANT)

            if neo4j_result and postgres_result:
                neo4j_files = neo4j_result.total_records
                postgres_files = postgres_result.total_records

                file_discrepancy = abs(neo4j_files - postgres_files)
                if file_discrepancy > 10:  # Allow some variance
                    synchronization_issues.append(
                        f"File count mismatch: Neo4j({neo4j_files}) vs PostgreSQL({postgres_files})"
                    )

            # 2. Data completeness correlation
            total_issues = sum(len(result.issues_found) for result in self.audit_results.values())
            avg_completeness = sum(result.data_completeness_percentage for result in self.audit_results.values()) / len(self.audit_results)

            print(f"📊 Overall data completeness: {avg_completeness:.1f}%")
            print(f"📊 Total issues across databases: {total_issues}")

            # 3. Performance correlation
            avg_integrity = sum(result.data_integrity_score for result in self.audit_results.values()) / len(self.audit_results)
            print(f"📊 Average integrity score: {avg_integrity:.1f}%")

            # 4. Consistency score calculation
            consistency_score = max(0.0, 100.0 - (len(synchronization_issues) * 20) - (total_issues * 2))

            # 5. Recommendations
            if consistency_score < 80:
                recommendations.append("Address cross-database synchronization issues")
            if total_issues > 10:
                recommendations.append("Prioritize fixing database-specific issues")
            if avg_completeness < 70:
                recommendations.append("Re-run comprehensive data ingestion")

            print(f"📊 Cross-database consistency score: {consistency_score:.1f}%")

            return CrossDatabaseValidation(
                data_consistency_score=consistency_score,
                missing_cross_references=missing_cross_references,
                orphaned_records=orphaned_records,
                synchronization_issues=synchronization_issues,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Cross-database validation failed: {str(e)}")
            return CrossDatabaseValidation(
                data_consistency_score=0.0,
                missing_cross_references=[],
                orphaned_records=[],
                synchronization_issues=[f"Validation failed: {str(e)}"],
                recommendations=["Investigate cross-database validation issues"]
            )

    async def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Execute comprehensive audit of all databases
        """
        print("🚀 Starting Comprehensive Database Audit")
        print("Following AI Task Orchestrator Guide Methodology")
        print("Task Complexity: MODERATE - Multi-database validation")
        print("=" * 70)

        audit_start_time = datetime.now()

        try:
            # Initialize audit session
            if not await self.initialize_audit_session():
                return {"error": "Failed to initialize audit session"}

            # Audit each database
            print("\n📋 Phase 1: Individual Database Audits")
            self.audit_results[DatabaseType.NEO4J] = await self.audit_neo4j_database()
            self.audit_results[DatabaseType.POSTGRESQL] = await self.audit_postgresql_database()
            self.audit_results[DatabaseType.REDIS] = await self.audit_redis_cache()
            self.audit_results[DatabaseType.QDRANT] = await self.audit_qdrant_vectors()

            # Cross-database validation
            print("\n📋 Phase 2: Cross-Database Validation")
            self.cross_validation_results = await self.validate_cross_database_consistency()

            # Generate summary
            audit_duration = (datetime.now() - audit_start_time).total_seconds()

            summary = {
                "audit_session_id": self.audit_session_id,
                "audit_duration_seconds": audit_duration,
                "databases_audited": len(self.audit_results),
                "individual_results": {db_type.value: asdict(result) for db_type, result in self.audit_results.items()},
                "cross_validation": asdict(self.cross_validation_results),
                "overall_health_score": sum(result.data_integrity_score for result in self.audit_results.values()) / len(self.audit_results),
                "total_issues": sum(len(result.issues_found) for result in self.audit_results.values()),
                "audit_timestamp": datetime.now().isoformat()
            }

            return summary

        except Exception as e:
            logger.error(f"Comprehensive audit failed: {str(e)}")
            traceback.print_exc()
            return {"error": f"Audit failed: {str(e)}"}

        finally:
            if self.db_manager:
                await self.db_manager.close_all_connections()

async def main():
    """
    Main execution function for comprehensive database audit
    """
    auditor = ComprehensiveDatabaseAuditor()
    audit_results = await auditor.run_comprehensive_audit()

    if "error" in audit_results:
        print(f"\n❌ Audit failed: {audit_results['error']}")
        return 1

    # Display summary
    print("\n🎯 Comprehensive Database Audit Complete!")
    print("=" * 70)
    print(f"📊 Overall Health Score: {audit_results['overall_health_score']:.1f}%")
    print(f"🔍 Total Issues Found: {audit_results['total_issues']}")
    print(f"⏱️  Audit Duration: {audit_results['audit_duration_seconds']:.1f} seconds")
    print(f"🗄️  Databases Audited: {audit_results['databases_audited']}/4")

    # Save results
    results_file = f"comprehensive_database_audit_{auditor.audit_session_id}.json"
    with open(results_file, 'w') as f:
        json.dump(audit_results, f, indent=2, default=str)

    print(f"💾 Results saved: {results_file}")

    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
