"""
Pytest Configuration for Phase 32.1 Multi-System Integration Tests
AI Task Orchestrator Implementation
"""

import pytest
import asyncio
import pytest_asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock
import psycopg
import redis.asyncio as redis
from neo4j import AsyncGraphDatabase
from qdrant_client import AsyncQdrantClient


# Configure pytest-asyncio
pytest_asyncio.auto_mode = True


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_postgres():
    """Mock PostgreSQL connection with common methods."""
    mock_conn = AsyncMock(spec=psycopg.AsyncConnection)
    
    # Mock cursor with common database operations
    mock_cursor = AsyncMock()
    mock_cursor.execute.return_value = None
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchmany.return_value = []
    mock_cursor.rowcount = 0
    
    mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__aexit__.return_value = None
    
    return mock_conn


@pytest.fixture
async def mock_redis():
    """Mock Redis connection with common methods."""
    mock_redis = AsyncMock(spec=redis.Redis)
    
    # Mock common Redis operations
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.hget.return_value = None
    mock_redis.hset.return_value = True
    mock_redis.hgetall.return_value = {}
    mock_redis.delete.return_value = 0
    mock_redis.exists.return_value = 0
    mock_redis.expire.return_value = True
    mock_redis.ttl.return_value = -1
    mock_redis.keys.return_value = []
    mock_redis.scan_iter.return_value = []
    mock_redis.xadd.return_value = "1640995200000-0"
    mock_redis.xread.return_value = []
    mock_redis.publish.return_value = 0
    mock_redis.ping.return_value = True
    
    return mock_redis


@pytest.fixture
async def mock_neo4j():
    """Mock Neo4j driver with common methods."""
    mock_driver = AsyncMock(spec=AsyncGraphDatabase.driver)
    
    # Mock session and result
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_result.data.return_value = []
    mock_result.single.return_value = None
    mock_result.consume.return_value = None
    
    mock_session.run.return_value = mock_result
    mock_session.close.return_value = None
    
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_driver.session.return_value.__aexit__.return_value = None
    mock_driver.close.return_value = None
    mock_driver.verify_connectivity.return_value = None
    
    return mock_driver


@pytest.fixture
async def mock_qdrant():
    """Mock Qdrant client with common methods."""
    mock_client = AsyncMock(spec=AsyncQdrantClient)
    
    # Mock collection operations
    mock_client.get_collections.return_value = []
    mock_client.create_collection.return_value = True
    mock_client.delete_collection.return_value = True
    mock_client.collection_exists.return_value = False
    
    # Mock vector operations
    mock_client.upsert.return_value = True
    mock_client.search.return_value = []
    mock_client.retrieve.return_value = []
    mock_client.delete.return_value = True
    mock_client.count.return_value = 0
    
    # Mock health check
    mock_client.get_cluster_info.return_value = {"status": "green"}
    
    return mock_client


@pytest.fixture
async def mock_databases(mock_postgres, mock_redis, mock_neo4j, mock_qdrant):
    """Collect all database mocks into a single fixture."""
    return {
        "postgres": mock_postgres,
        "redis": mock_redis,
        "neo4j": mock_neo4j,
        "qdrant": mock_qdrant
    }


@pytest.fixture
def sample_plc_data():
    """Sample PLC data for testing."""
    return {
        "device_id": "PLC_001",
        "tag": "temperature",
        "value": 25.5,
        "unit": "°C",
        "timestamp": 1640995200.0,
        "quality": "good"
    }


@pytest.fixture
def sample_control_loop():
    """Sample control loop data for testing."""
    return {
        "id": "LOOP_001",
        "name": "Temperature Control",
        "device_id": "PLC_001",
        "setpoint": 25.0,
        "current_value": 24.8,
        "kp": 1.0,
        "ki": 0.1,
        "kd": 0.05,
        "status": "active"
    }


@pytest.fixture
def sample_historical_data():
    """Sample historical data for testing."""
    return [
        {
            "id": 1,
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.5,
            "unit": "°C",
            "timestamp": 1640995200.0,
            "quality": "good"
        },
        {
            "id": 2,
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.7,
            "unit": "°C",
            "timestamp": 1640995260.0,
            "quality": "good"
        },
        {
            "id": 3,
            "device_id": "PLC_001",
            "tag": "temperature",
            "value": 25.3,
            "unit": "°C",
            "timestamp": 1640995320.0,
            "quality": "good"
        }
    ]


@pytest.fixture
def sample_vector_data():
    """Sample vector data for testing."""
    return {
        "id": "doc_001",
        "vector": [0.1, 0.2, 0.3, 0.4] * 384,  # 1536-dimensional vector
        "payload": {
            "device_id": "PLC_001",
            "tag": "temperature",
            "content": "Temperature sensor data from industrial control system",
            "timestamp": 1640995200.0
        }
    }


@pytest.fixture
def graphql_test_query():
    """Sample GraphQL query for testing."""
    return """
    query {
        plcData(deviceId: "PLC_001", tag: "temperature") {
            deviceId
            tag
            value
            unit
            timestamp
            quality
        }
    }
    """


@pytest.fixture
def graphql_test_mutation():
    """Sample GraphQL mutation for testing."""
    return """
    mutation {
        updatePLCData(input: {
            deviceId: "PLC_001"
            tag: "temperature"
            value: 26.0
            unit: "°C"
            quality: "good"
        }) {
            success
            message
        }
    }
    """


@pytest.fixture
def websocket_test_message():
    """Sample WebSocket message for testing."""
    return {
        "type": "subscribe",
        "channel": "temperature",
        "device_id": "PLC_001"
    }


@pytest.fixture
def sync_conflict_data():
    """Sample data for testing sync conflicts."""
    return {
        "source_data": {
            "value": 25.5,
            "timestamp": 1640995300.0,
            "quality": "good"
        },
        "target_data": {
            "value": 25.7,
            "timestamp": 1640995200.0,
            "quality": "good"
        }
    }


# Test configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "websocket: mark test as websocket-related"
    )
    config.addinivalue_line(
        "markers", "graphql: mark test as GraphQL-related"
    )
    config.addinivalue_line(
        "markers", "sync: mark test as data sync-related"
    )
    config.addinivalue_line(
        "markers", "resilience: mark test as resilience pattern-related"
    )


# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test items during collection."""
    # Add markers based on test file names
    for item in items:
        if "test_websocket" in item.nodeid:
            item.add_marker(pytest.mark.websocket)
        elif "test_graphql" in item.nodeid:
            item.add_marker(pytest.mark.graphql)
        elif "test_data_sync" in item.nodeid:
            item.add_marker(pytest.mark.sync)
        elif "test_resilience" in item.nodeid:
            item.add_marker(pytest.mark.resilience)
        elif "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.slow)


# Async test timeout
@pytest.fixture(autouse=True)
def timeout_all_tests():
    """Add timeout to all async tests."""
    return pytest.mark.timeout(30)  # 30 second timeout


# Test result reporting
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Create test report with additional information."""
    outcome = yield
    rep = outcome.get_result()
    
    # Add test metadata
    if rep.when == "call":
        if hasattr(item, 'function'):
            # Add function docstring as test description
            if item.function.__doc__:
                rep.description = item.function.__doc__.strip()
        
        # Add markers information
        if item.get_closest_marker("slow"):
            rep.test_type = "slow"
        elif item.get_closest_marker("integration"):
            rep.test_type = "integration"
        else:
            rep.test_type = "unit"


# Performance tracking
performance_data = {}


@pytest.fixture(autouse=True)
def track_performance(request):
    """Track test performance metrics."""
    import time
    
    start_time = time.time()
    yield
    end_time = time.time()
    
    duration = end_time - start_time
    test_name = request.node.name
    
    performance_data[test_name] = {
        "duration": duration,
        "markers": [marker.name for marker in request.node.iter_markers()]
    }


def pytest_sessionfinish(session, exitstatus):
    """Print performance summary at the end of test session."""
    if performance_data:
        print("\n" + "="*80)
        print("PERFORMANCE SUMMARY")
        print("="*80)
        
        # Sort by duration
        sorted_tests = sorted(
            performance_data.items(), 
            key=lambda x: x[1]["duration"], 
            reverse=True
        )
        
        print(f"{'Test Name':<50} {'Duration (s)':<12} {'Type':<15}")
        print("-" * 77)
        
        for test_name, data in sorted_tests[:10]:  # Top 10 slowest
            test_type = "integration" if "integration" in data["markers"] else "unit"
            print(f"{test_name:<50} {data['duration']:<12.3f} {test_type:<15}")
        
        # Summary stats
        total_duration = sum(data["duration"] for data in performance_data.values())
        avg_duration = total_duration / len(performance_data)
        
        print("-" * 77)
        print(f"Total tests: {len(performance_data)}")
        print(f"Total duration: {total_duration:.3f}s")
        print(f"Average duration: {avg_duration:.3f}s")
        
        # Slow test warnings
        slow_tests = [
            name for name, data in performance_data.items() 
            if data["duration"] > 5.0 and "slow" not in data["markers"]
        ]
        
        if slow_tests:
            print(f"\nWarning: {len(slow_tests)} tests took >5s but not marked as @pytest.mark.slow:")
            for test in slow_tests[:5]:
                print(f"  - {test}")


# Error handling for async tests
@pytest.fixture(autouse=True)
async def handle_async_exceptions():
    """Handle exceptions in async tests."""
    try:
        yield
    except asyncio.CancelledError:
        print("Test was cancelled")
        raise
    except Exception as e:
        print(f"Async test error: {e}")
        raise


# Clean up resources
@pytest.fixture(scope="session", autouse=True)
async def cleanup_resources():
    """Clean up resources after test session."""
    yield
    
    # Close any remaining async connections
    await asyncio.sleep(0.1)  # Allow pending operations to complete
    
    # Clear performance data
    performance_data.clear() 