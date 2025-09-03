"""
Comprehensive Test Suite for Data Synchronization Engine
Phase 32.1 Multi-System Integration
AI Task Orchestrator Implementation
"""

import asyncio

# Mock the data sync engine module
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock

import psycopg
import pytest
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
from qdrant_client import AsyncQdrantClient

sys.path.append(str(Path(__file__).parent.parent))

from data_sync_engine import (
    ConflictDetector,
    ConflictResolver,
    DataConflict,
    DataSyncEngine,
    Neo4jSync,
    PostgreSQLSync,
    QdrantSync,
    RedisSync,
    ResolutionStrategy,
    SyncTransaction,
)


class TestDataConflict:
    """Test data conflict detection and representation"""

    def test_data_conflict_creation(self):
        """Test DataConflict creation and validation"""
        conflict = DataConflict(
            conflict_id="conflict_001",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_database="postgres",
            source_data={"value": 25.5, "timestamp": 1640995200.0},
            target_data={"value": 25.7, "timestamp": 1640995210.0},
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        assert conflict.conflict_id == "conflict_001"
        assert conflict.entity_type == "plc_data"
        assert conflict.source_database == "redis"
        assert conflict.target_database == "postgres"
        assert conflict.conflict_type == "value_mismatch"

    def test_conflict_serialization(self):
        """Test DataConflict JSON serialization"""
        conflict = DataConflict(
            conflict_id="conflict_002",
            entity_type="control_loop",
            entity_id="LOOP_001",
            source_database="postgres",
            target_database="neo4j",
            source_data={"setpoint": 25.0},
            target_data={"setpoint": 26.0},
            conflict_type="parameter_mismatch",
            detection_time=datetime.now()
        )

        json_data = conflict.to_dict()

        assert json_data["conflict_id"] == "conflict_002"
        assert json_data["entity_type"] == "control_loop"
        assert json_data["conflict_type"] == "parameter_mismatch"


class TestConflictDetector:
    """Test conflict detection mechanisms"""

    @pytest.fixture
    def conflict_detector(self):
        return ConflictDetector()

    def test_value_mismatch_detection(self, conflict_detector):
        """Test detection of value mismatches between databases"""
        source_data = {"value": 25.5, "timestamp": 1640995200.0, "quality": "good"}
        target_data = {"value": 25.7, "timestamp": 1640995200.0, "quality": "good"}

        conflicts = conflict_detector.detect_conflicts(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_data=source_data,
            target_data=target_data,
            source_db="redis",
            target_db="postgres"
        )

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "value_mismatch"
        assert conflicts[0].source_data["value"] == 25.5
        assert conflicts[0].target_data["value"] == 25.7

    def test_timestamp_conflict_detection(self, conflict_detector):
        """Test detection of timestamp-based conflicts"""
        source_data = {"value": 25.5, "timestamp": 1640995200.0}
        target_data = {"value": 25.5, "timestamp": 1640995100.0}  # Older timestamp

        conflicts = conflict_detector.detect_conflicts(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_data=source_data,
            target_data=target_data,
            source_db="redis",
            target_db="postgres"
        )

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "timestamp_conflict"

    def test_missing_data_detection(self, conflict_detector):
        """Test detection of missing data conflicts"""
        source_data = {"value": 25.5, "timestamp": 1640995200.0}
        target_data = None

        conflicts = conflict_detector.detect_conflicts(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_data=source_data,
            target_data=target_data,
            source_db="redis",
            target_db="postgres"
        )

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "missing_data"

    def test_schema_mismatch_detection(self, conflict_detector):
        """Test detection of schema mismatches"""
        source_data = {"value": 25.5, "unit": "°C", "timestamp": 1640995200.0}
        target_data = {"temperature": 25.5, "time": 1640995200.0}  # Different schema

        conflicts = conflict_detector.detect_conflicts(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_data=source_data,
            target_data=target_data,
            source_db="redis",
            target_db="postgres"
        )

        assert len(conflicts) == 1
        assert conflicts[0].conflict_type == "schema_mismatch"

    def test_no_conflict_detection(self, conflict_detector):
        """Test when no conflicts exist"""
        source_data = {"value": 25.5, "timestamp": 1640995200.0, "quality": "good"}
        target_data = {"value": 25.5, "timestamp": 1640995200.0, "quality": "good"}

        conflicts = conflict_detector.detect_conflicts(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_data=source_data,
            target_data=target_data,
            source_db="redis",
            target_db="postgres"
        )

        assert len(conflicts) == 0


class TestConflictResolver:
    """Test conflict resolution strategies"""

    @pytest.fixture
    def conflict_resolver(self):
        return ConflictResolver()

    def test_timestamp_based_resolution(self, conflict_resolver):
        """Test timestamp-based conflict resolution (latest wins)"""
        conflict = DataConflict(
            conflict_id="conflict_001",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_database="postgres",
            source_data={"value": 25.5, "timestamp": 1640995300.0},  # Newer
            target_data={"value": 25.7, "timestamp": 1640995200.0},  # Older
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        resolution = conflict_resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.TIMESTAMP_BASED
        )

        assert resolution.winning_data == conflict.source_data
        assert resolution.resolution_strategy == ResolutionStrategy.TIMESTAMP_BASED
        assert resolution.target_database == "postgres"

    def test_source_priority_resolution(self, conflict_resolver):
        """Test source database priority resolution"""
        conflict = DataConflict(
            conflict_id="conflict_002",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",  # Real-time source
            target_database="postgres",
            source_data={"value": 25.5, "timestamp": 1640995200.0},
            target_data={"value": 25.7, "timestamp": 1640995300.0},  # Even if newer
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        resolution = conflict_resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.SOURCE_PRIORITY
        )

        assert resolution.winning_data == conflict.source_data
        assert resolution.resolution_strategy == ResolutionStrategy.SOURCE_PRIORITY

    def test_quality_based_resolution(self, conflict_resolver):
        """Test data quality-based resolution"""
        conflict = DataConflict(
            conflict_id="conflict_003",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_database="postgres",
            source_data={"value": 25.5, "quality": "poor"},
            target_data={"value": 25.7, "quality": "good"},
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        resolution = conflict_resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.QUALITY_BASED
        )

        assert resolution.winning_data == conflict.target_data
        assert resolution.resolution_strategy == ResolutionStrategy.QUALITY_BASED

    def test_merge_resolution(self, conflict_resolver):
        """Test data merging resolution strategy"""
        conflict = DataConflict(
            conflict_id="conflict_004",
            entity_type="control_loop",
            entity_id="LOOP_001",
            source_database="postgres",
            target_database="neo4j",
            source_data={"setpoint": 25.0, "kp": 1.0},
            target_data={"setpoint": 26.0, "ki": 0.1},
            conflict_type="partial_mismatch",
            detection_time=datetime.now()
        )

        resolution = conflict_resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.MERGE
        )

        # Should merge non-conflicting fields
        expected_merged = {"setpoint": 25.0, "kp": 1.0, "ki": 0.1}  # Assuming source priority for conflicts
        assert resolution.winning_data == expected_merged
        assert resolution.resolution_strategy == ResolutionStrategy.MERGE

    def test_manual_resolution(self, conflict_resolver):
        """Test manual conflict resolution"""
        conflict = DataConflict(
            conflict_id="conflict_005",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_database="postgres",
            source_data={"value": 25.5},
            target_data={"value": 25.7},
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        manual_data = {"value": 25.6}  # User-chosen value

        resolution = conflict_resolver.resolve_conflict(
            conflict,
            strategy=ResolutionStrategy.MANUAL,
            manual_data=manual_data
        )

        assert resolution.winning_data == manual_data
        assert resolution.resolution_strategy == ResolutionStrategy.MANUAL


class TestSyncTransaction:
    """Test synchronization transaction management"""

    @pytest.fixture
    def sync_transaction(self):
        return SyncTransaction(
            transaction_id="txn_001",
            source_database="redis",
            target_databases=["postgres", "neo4j"],
            entity_type="plc_data"
        )

    def test_transaction_initialization(self, sync_transaction):
        """Test sync transaction initialization"""
        assert sync_transaction.transaction_id == "txn_001"
        assert sync_transaction.source_database == "redis"
        assert "postgres" in sync_transaction.target_databases
        assert "neo4j" in sync_transaction.target_databases
        assert sync_transaction.status == "pending"

    def test_transaction_state_management(self, sync_transaction):
        """Test transaction state transitions"""
        # Start transaction
        sync_transaction.start()
        assert sync_transaction.status == "in_progress"
        assert sync_transaction.start_time is not None

        # Complete transaction
        sync_transaction.complete()
        assert sync_transaction.status == "completed"
        assert sync_transaction.end_time is not None

        # Calculate duration
        duration = sync_transaction.get_duration()
        assert duration >= 0

    def test_transaction_rollback(self, sync_transaction):
        """Test transaction rollback functionality"""
        sync_transaction.start()

        # Add some operations
        sync_transaction.add_operation("insert", "postgres", {"value": 25.5})
        sync_transaction.add_operation("update", "neo4j", {"setpoint": 25.0})

        # Rollback
        sync_transaction.rollback("Database connection failed")

        assert sync_transaction.status == "failed"
        assert sync_transaction.error_message == "Database connection failed"
        assert len(sync_transaction.rollback_operations) == 2

    def test_conflict_handling_in_transaction(self, sync_transaction):
        """Test conflict handling within transactions"""
        conflict = DataConflict(
            conflict_id="conflict_001",
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_database="postgres",
            source_data={"value": 25.5},
            target_data={"value": 25.7},
            conflict_type="value_mismatch",
            detection_time=datetime.now()
        )

        sync_transaction.add_conflict(conflict)

        assert len(sync_transaction.conflicts) == 1
        assert sync_transaction.conflicts[0].conflict_id == "conflict_001"


class TestDatabaseSync:
    """Test individual database synchronization implementations"""

    @pytest.fixture
    def mock_postgres(self):
        return AsyncMock(spec=psycopg.AsyncConnection)

    @pytest.fixture
    def mock_redis(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def mock_neo4j(self):
        return AsyncMock(spec=AsyncGraphDatabase.driver)

    @pytest.fixture
    def mock_qdrant(self):
        return AsyncMock(spec=AsyncQdrantClient)

    @pytest.mark.asyncio
    async def test_postgresql_sync(self, mock_postgres):
        """Test PostgreSQL synchronization operations"""
        postgres_sync = PostgreSQLSync(mock_postgres)

        # Test data insertion
        data = {
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.5,
            "timestamp": 1640995200.0,
            "quality": "good"
        }

        mock_cursor = AsyncMock()
        mock_postgres.cursor.return_value.__aenter__.return_value = mock_cursor

        result = await postgres_sync.insert_data("plc_data", data)

        assert result.success is True
        mock_cursor.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_sync(self, mock_redis):
        """Test Redis synchronization operations"""
        redis_sync = RedisSync(mock_redis)

        # Test data update
        data = {
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.5,
            "timestamp": 1640995200.0
        }

        result = await redis_sync.update_data("plc:PLC_001:temperature", data)

        assert result.success is True
        mock_redis.hset.assert_called_once()

    @pytest.mark.asyncio
    async def test_neo4j_sync(self, mock_neo4j):
        """Test Neo4j synchronization operations"""
        neo4j_sync = Neo4jSync(mock_neo4j)

        # Test relationship creation
        data = {
            "source_id": "PLC_001",
            "target_id": "LOOP_001",
            "relationship_type": "CONTROLS",
            "properties": {"strength": 0.95}
        }

        mock_session = AsyncMock()
        mock_neo4j.session.return_value.__aenter__.return_value = mock_session

        result = await neo4j_sync.create_relationship(data)

        assert result.success is True
        mock_session.run.assert_called_once()

    @pytest.mark.asyncio
    async def test_qdrant_sync(self, mock_qdrant):
        """Test Qdrant synchronization operations"""
        qdrant_sync = QdrantSync(mock_qdrant)

        # Test vector upsert
        data = {
            "id": "doc_001",
            "vector": [0.1, 0.2, 0.3, 0.4],
            "payload": {"device_id": "PLC_001", "tag": "temperature"}
        }

        result = await qdrant_sync.upsert_vector("plc_memory", data)

        assert result.success is True
        mock_qdrant.upsert.assert_called_once()


class TestDataSyncEngine:
    """Test complete data synchronization engine"""

    @pytest.fixture
    def mock_databases(self):
        return {
            "postgres": AsyncMock(spec=psycopg.AsyncConnection),
            "redis": AsyncMock(spec=redis.Redis),
            "neo4j": AsyncMock(spec=AsyncGraphDatabase.driver),
            "qdrant": AsyncMock(spec=AsyncQdrantClient)
        }

    @pytest.fixture
    def sync_engine(self, mock_databases):
        return DataSyncEngine(
            postgres_client=mock_databases["postgres"],
            redis_client=mock_databases["redis"],
            neo4j_client=mock_databases["neo4j"],
            qdrant_client=mock_databases["qdrant"]
        )

    @pytest.mark.asyncio
    async def test_simple_sync_operation(self, sync_engine, mock_databases):
        """Test simple synchronization without conflicts"""
        data = {
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.5,
            "timestamp": 1640995200.0,
            "quality": "good"
        }

        # Mock successful operations
        mock_cursor = AsyncMock()
        mock_databases["postgres"].cursor.return_value.__aenter__.return_value = mock_cursor

        result = await sync_engine.sync_data(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_databases=["postgres"],
            data=data
        )

        assert result.success is True
        assert len(result.conflicts) == 0
        assert result.records_synced == 1

    @pytest.mark.asyncio
    async def test_sync_with_conflicts(self, sync_engine, mock_databases):
        """Test synchronization with conflict detection and resolution"""
        source_data = {"value": 25.5, "timestamp": 1640995300.0}

        # Mock target data retrieval
        mock_cursor = AsyncMock()
        mock_cursor.fetchone.return_value = (
            "PLC_001", "temperature", 25.7, "°C", 1640995200.0, "good"
        )
        mock_databases["postgres"].cursor.return_value.__aenter__.return_value = mock_cursor

        result = await sync_engine.sync_data(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_databases=["postgres"],
            data=source_data,
            conflict_resolution=ResolutionStrategy.TIMESTAMP_BASED
        )

        assert result.success is True
        assert len(result.conflicts) == 1
        assert result.conflicts_resolved == 1

    @pytest.mark.asyncio
    async def test_multi_database_sync(self, sync_engine, mock_databases):
        """Test synchronization across multiple target databases"""
        data = {
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.5,
            "timestamp": 1640995200.0
        }

        # Mock successful operations for all databases
        mock_cursor = AsyncMock()
        mock_databases["postgres"].cursor.return_value.__aenter__.return_value = mock_cursor

        mock_session = AsyncMock()
        mock_databases["neo4j"].session.return_value.__aenter__.return_value = mock_session

        result = await sync_engine.sync_data(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_databases=["postgres", "neo4j"],
            data=data
        )

        assert result.success is True
        assert result.records_synced == 2  # One for each target database

    @pytest.mark.asyncio
    async def test_batch_sync_operation(self, sync_engine, mock_databases):
        """Test batch synchronization for performance"""
        batch_data = [
            {"entity_id": "PLC_001:temperature", "data": {"value": 25.5}},
            {"entity_id": "PLC_001:pressure", "data": {"value": 101.3}},
            {"entity_id": "PLC_002:temperature", "data": {"value": 26.0}}
        ]

        # Mock batch operations
        mock_cursor = AsyncMock()
        mock_databases["postgres"].cursor.return_value.__aenter__.return_value = mock_cursor

        result = await sync_engine.batch_sync(
            entity_type="plc_data",
            source_database="redis",
            target_databases=["postgres"],
            batch_data=batch_data
        )

        assert result.success is True
        assert result.records_synced == 3
        assert result.batch_size == 3

    @pytest.mark.asyncio
    async def test_sync_error_handling(self, sync_engine, mock_databases):
        """Test error handling during synchronization"""
        data = {"value": 25.5}

        # Mock database error
        mock_cursor = AsyncMock()
        mock_cursor.execute.side_effect = psycopg.DatabaseError("Connection failed")
        mock_databases["postgres"].cursor.return_value.__aenter__.return_value = mock_cursor

        result = await sync_engine.sync_data(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_databases=["postgres"],
            data=data
        )

        assert result.success is False
        assert "Connection failed" in result.error_message
        assert result.records_synced == 0

    @pytest.mark.asyncio
    async def test_sync_performance_monitoring(self, sync_engine):
        """Test synchronization performance monitoring"""
        data = {"value": 25.5, "timestamp": 1640995200.0}

        start_time = asyncio.get_event_loop().time()

        # Simulate sync operation
        await sync_engine.sync_data(
            entity_type="plc_data",
            entity_id="PLC_001:temperature",
            source_database="redis",
            target_databases=["postgres"],
            data=data
        )

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Should complete quickly
        assert duration < 1.0

        # Check performance metrics
        metrics = sync_engine.get_performance_metrics()
        assert "total_operations" in metrics
        assert "average_duration" in metrics
        assert "success_rate" in metrics


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest.mark.asyncio
    async def test_real_time_sync_scenario(self):
        """Test real-time data synchronization scenario"""
        # Mock all database clients
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_neo4j = AsyncMock(spec=AsyncGraphDatabase.driver)
        mock_qdrant = AsyncMock(spec=AsyncQdrantClient)

        sync_engine = DataSyncEngine(
            postgres_client=mock_postgres,
            redis_client=mock_redis,
            neo4j_client=mock_neo4j,
            qdrant_client=mock_qdrant
        )

        # Simulate real-time PLC data updates
        plc_updates = [
            {"device_id": "PLC_001", "tag": "temperature", "value": 25.5},
            {"device_id": "PLC_001", "tag": "pressure", "value": 101.3},
            {"device_id": "PLC_002", "tag": "temperature", "value": 26.0}
        ]

        # Mock successful operations
        mock_cursor = AsyncMock()
        mock_postgres.cursor.return_value.__aenter__.return_value = mock_cursor

        # Process updates concurrently
        tasks = []
        for update in plc_updates:
            task = sync_engine.sync_data(
                entity_type="plc_data",
                entity_id=f"{update['device_id']}:{update['tag']}",
                source_database="redis",
                target_databases=["postgres"],
                data=update
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Verify all updates completed successfully
        for result in results:
            assert result.success is True

        # Check total throughput
        total_records = sum(result.records_synced for result in results)
        assert total_records == len(plc_updates)

    @pytest.mark.asyncio
    async def test_disaster_recovery_scenario(self):
        """Test disaster recovery and data consistency restoration"""
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_neo4j = AsyncMock(spec=AsyncGraphDatabase.driver)
        mock_qdrant = AsyncMock(spec=AsyncQdrantClient)

        sync_engine = DataSyncEngine(
            postgres_client=mock_postgres,
            redis_client=mock_redis,
            neo4j_client=mock_neo4j,
            qdrant_client=mock_qdrant
        )

        # Simulate inconsistent data across databases


        # Mock data retrieval
        mock_cursor = AsyncMock()
        mock_cursor.fetchall.return_value = [
            ("PLC_001", "temperature", 25.2, "°C", 1640995200.0, "good")
        ]
        mock_postgres.cursor.return_value.__aenter__.return_value = mock_cursor

        # Perform full data reconciliation
        result = await sync_engine.reconcile_databases(
            entity_type="plc_data",
            source_database="redis",
            target_databases=["postgres"],
            reconciliation_strategy=ResolutionStrategy.TIMESTAMP_BASED
        )

        assert result.success is True
        assert result.conflicts_detected > 0
        assert result.conflicts_resolved == result.conflicts_detected

    @pytest.mark.asyncio
    async def test_high_volume_sync_performance(self):
        """Test synchronization performance under high data volume"""
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_neo4j = AsyncMock(spec=AsyncGraphDatabase.driver)
        mock_qdrant = AsyncMock(spec=AsyncQdrantClient)

        sync_engine = DataSyncEngine(
            postgres_client=mock_postgres,
            redis_client=mock_redis,
            neo4j_client=mock_neo4j,
            qdrant_client=mock_qdrant
        )

        # Generate large dataset (1000 records)
        large_batch = []
        for i in range(1000):
            large_batch.append({
                "entity_id": f"PLC_{i//100:03d}:sensor_{i%100:02d}",
                "data": {"value": 25.0 + i * 0.1, "timestamp": 1640995200.0 + i}
            })

        # Mock batch operations
        mock_cursor = AsyncMock()
        mock_postgres.cursor.return_value.__aenter__.return_value = mock_cursor

        start_time = asyncio.get_event_loop().time()

        result = await sync_engine.batch_sync(
            entity_type="plc_data",
            source_database="redis",
            target_databases=["postgres"],
            batch_data=large_batch,
            batch_size=100  # Process in chunks
        )

        end_time = asyncio.get_event_loop().time()
        duration = end_time - start_time

        # Verify performance
        assert result.success is True
        assert result.records_synced == 1000
        assert duration < 10.0  # Should complete within 10 seconds

        # Calculate throughput
        throughput = result.records_synced / duration
        assert throughput > 100  # At least 100 records per second


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
