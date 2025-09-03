"""
Comprehensive Test Suite for WebSocket Real-time Server
Phase 32.1 Multi-System Integration
AI Task Orchestrator Implementation
"""

import asyncio
import json

# Mock the websocket server module
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import psycopg
import pytest
import redis.asyncio as redis
import websockets

sys.path.append(str(Path(__file__).parent.parent))

from websocket_server import (
    ConnectionManager,
    HeartbeatManager,
    PLCDataPoint,
    PLCDataStreamer,
    SubscriptionManager,
    WebSocketServer,
)


class TestPLCDataPoint:
    """Test PLCDataPoint type safety and validation"""

    def test_plc_data_point_creation(self):
        """Test PLCDataPoint creation and validation"""
        data = PLCDataPoint(
            device_id="PLC_001",
            timestamp=1640995200.0,
            tag="temperature",
            value=25.5,
            unit="°C",
            quality="good"
        )

        assert data.device_id == "PLC_001"
        assert data.timestamp == 1640995200.0
        assert data.tag == "temperature"
        assert data.value == 25.5
        assert data.unit == "°C"
        assert data.quality == "good"

    def test_plc_data_point_serialization(self):
        """Test PLCDataPoint JSON serialization"""
        data = PLCDataPoint(
            device_id="PLC_002",
            timestamp=1640995300.0,
            tag="pressure",
            value=101.3,
            unit="kPa",
            quality="good"
        )

        json_data = data.to_dict()
        expected = {
            "device_id": "PLC_002",
            "timestamp": 1640995300.0,
            "tag": "pressure",
            "value": 101.3,
            "unit": "kPa",
            "quality": "good"
        }

        assert json_data == expected


class TestConnectionManager:
    """Test WebSocket connection management"""

    @pytest.fixture
    def connection_manager(self):
        return ConnectionManager()

    def test_connection_registration(self, connection_manager):
        """Test connection registration and tracking"""
        mock_websocket = MagicMock()
        mock_websocket.remote_address = ("127.0.0.1", 8080)

        client_id = connection_manager.register_connection(mock_websocket)

        assert client_id in connection_manager.connections
        assert connection_manager.connections[client_id]["websocket"] == mock_websocket
        assert connection_manager.connections[client_id]["subscriptions"] == set()

    def test_connection_unregistration(self, connection_manager):
        """Test connection cleanup on disconnect"""
        mock_websocket = MagicMock()
        mock_websocket.remote_address = ("127.0.0.1", 8080)

        client_id = connection_manager.register_connection(mock_websocket)
        connection_manager.unregister_connection(client_id)

        assert client_id not in connection_manager.connections

    def test_subscription_management(self, connection_manager):
        """Test subscription handling per connection"""
        mock_websocket = MagicMock()
        mock_websocket.remote_address = ("127.0.0.1", 8080)

        client_id = connection_manager.register_connection(mock_websocket)
        connection_manager.add_subscription(client_id, "temperature_alerts")
        connection_manager.add_subscription(client_id, "pressure_monitoring")

        subscriptions = connection_manager.get_subscriptions(client_id)
        assert "temperature_alerts" in subscriptions
        assert "pressure_monitoring" in subscriptions

        connection_manager.remove_subscription(client_id, "temperature_alerts")
        subscriptions = connection_manager.get_subscriptions(client_id)
        assert "temperature_alerts" not in subscriptions
        assert "pressure_monitoring" in subscriptions


class TestHeartbeatManager:
    """Test heartbeat monitoring and connection health"""

    @pytest.fixture
    def heartbeat_manager(self):
        return HeartbeatManager(heartbeat_interval=1.0, timeout=3.0)

    @pytest.mark.asyncio
    async def test_heartbeat_monitoring(self, heartbeat_manager):
        """Test heartbeat monitoring for active connections"""
        mock_websocket = AsyncMock()
        client_id = "test_client_001"

        heartbeat_manager.register_client(client_id, mock_websocket)

        # Simulate heartbeat response
        await heartbeat_manager.handle_heartbeat_response(client_id)

        # Check client is alive
        assert heartbeat_manager.is_client_alive(client_id)

    @pytest.mark.asyncio
    async def test_heartbeat_timeout(self, heartbeat_manager):
        """Test heartbeat timeout detection"""
        mock_websocket = AsyncMock()
        client_id = "test_client_002"

        heartbeat_manager.register_client(client_id, mock_websocket)

        # Wait for timeout
        await asyncio.sleep(4.0)

        # Client should be marked as inactive
        assert not heartbeat_manager.is_client_alive(client_id)

    @pytest.mark.asyncio
    async def test_heartbeat_cleanup(self, heartbeat_manager):
        """Test cleanup of inactive connections"""
        mock_websocket = AsyncMock()
        client_id = "test_client_003"

        heartbeat_manager.register_client(client_id, mock_websocket)
        inactive_clients = await heartbeat_manager.cleanup_inactive_clients()

        # Initially no inactive clients
        assert len(inactive_clients) == 0

        # Wait for timeout
        await asyncio.sleep(4.0)
        inactive_clients = await heartbeat_manager.cleanup_inactive_clients()

        # Client should be detected as inactive
        assert client_id in inactive_clients


class TestSubscriptionManager:
    """Test subscription management for different data streams"""

    @pytest.fixture
    def subscription_manager(self):
        return SubscriptionManager()

    def test_channel_subscription(self, subscription_manager):
        """Test channel-based subscription management"""
        client_id = "client_001"
        channel = "temperature_sensors"

        subscription_manager.subscribe(client_id, channel)

        assert client_id in subscription_manager.get_subscribers(channel)
        assert channel in subscription_manager.get_client_subscriptions(client_id)

    def test_unsubscription(self, subscription_manager):
        """Test unsubscription from channels"""
        client_id = "client_002"
        channel = "pressure_sensors"

        subscription_manager.subscribe(client_id, channel)
        subscription_manager.unsubscribe(client_id, channel)

        assert client_id not in subscription_manager.get_subscribers(channel)
        assert channel not in subscription_manager.get_client_subscriptions(client_id)

    def test_client_cleanup(self, subscription_manager):
        """Test cleanup of all client subscriptions"""
        client_id = "client_003"
        channels = ["temperature", "pressure", "flow_rate"]

        for channel in channels:
            subscription_manager.subscribe(client_id, channel)

        subscription_manager.cleanup_client(client_id)

        for channel in channels:
            assert client_id not in subscription_manager.get_subscribers(channel)
        assert len(subscription_manager.get_client_subscriptions(client_id)) == 0


class TestPLCDataStreamer:
    """Test PLC data streaming and Redis integration"""

    @pytest.fixture
    def mock_redis(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def plc_streamer(self, mock_redis):
        return PLCDataStreamer(redis_client=mock_redis)

    @pytest.mark.asyncio
    async def test_data_publishing(self, plc_streamer, mock_redis):
        """Test publishing PLC data to Redis streams"""
        data_point = PLCDataPoint(
            device_id="PLC_001",
            timestamp=1640995200.0,
            tag="temperature",
            value=25.5,
            unit="°C",
            quality="good"
        )

        await plc_streamer.publish_data(data_point)

        # Verify Redis stream add was called
        mock_redis.xadd.assert_called_once()
        call_args = mock_redis.xadd.call_args
        assert call_args[0][0] == "plc_data_stream"
        assert "device_id" in call_args[0][1]
        assert call_args[0][1]["device_id"] == "PLC_001"

    @pytest.mark.asyncio
    async def test_data_subscription(self, plc_streamer, mock_redis):
        """Test subscribing to PLC data streams"""
        callback = AsyncMock()

        # Mock Redis stream data
        mock_redis.xread.return_value = [
            ("plc_data_stream", [
                ("1640995200000-0", {
                    b"device_id": b"PLC_001",
                    b"tag": b"temperature",
                    b"value": b"25.5",
                    b"timestamp": b"1640995200.0"
                })
            ])
        ]

        await plc_streamer.subscribe_to_stream("plc_data_stream", callback)

        # Verify callback was called with parsed data
        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_filtering(self, plc_streamer):
        """Test data filtering by device and tag"""
        data_points = [
            PLCDataPoint("PLC_001", 1640995200.0, "temperature", 25.5, "°C", "good"),
            PLCDataPoint("PLC_002", 1640995300.0, "pressure", 101.3, "kPa", "good"),
            PLCDataPoint("PLC_001", 1640995400.0, "humidity", 65.0, "%", "good")
        ]

        # Filter by device
        filtered = plc_streamer.filter_by_device(data_points, "PLC_001")
        assert len(filtered) == 2
        assert all(dp.device_id == "PLC_001" for dp in filtered)

        # Filter by tag
        filtered = plc_streamer.filter_by_tag(data_points, "temperature")
        assert len(filtered) == 1
        assert filtered[0].tag == "temperature"


class TestWebSocketServer:
    """Test complete WebSocket server functionality"""

    @pytest.fixture
    def mock_redis(self):
        return AsyncMock(spec=redis.Redis)

    @pytest.fixture
    def mock_postgres(self):
        return AsyncMock(spec=psycopg.AsyncConnection)

    @pytest.fixture
    def websocket_server(self, mock_redis, mock_postgres):
        server = WebSocketServer(
            host="localhost",
            port=8765,
            redis_client=mock_redis,
            postgres_client=mock_postgres
        )
        return server

    @pytest.mark.asyncio
    async def test_server_startup(self, websocket_server):
        """Test server initialization and startup"""
        assert websocket_server.host == "localhost"
        assert websocket_server.port == 8765
        assert websocket_server.is_running is False

        # Mock startup
        with patch('websockets.serve') as mock_serve:
            await websocket_server.start()
            mock_serve.assert_called_once_with(
                websocket_server.handle_client,
                "localhost",
                8765
            )

    @pytest.mark.asyncio
    async def test_client_connection_handling(self, websocket_server):
        """Test client connection and message handling"""
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = ("127.0.0.1", 8080)
        mock_websocket.recv.side_effect = [
            json.dumps({"type": "subscribe", "channel": "temperature"}),
            json.dumps({"type": "heartbeat", "timestamp": 1640995200.0}),
            websockets.exceptions.ConnectionClosed(None, None)
        ]

        await websocket_server.handle_client(mock_websocket, "/")

        # Verify connection was handled
        mock_websocket.send.assert_called()

    @pytest.mark.asyncio
    async def test_message_routing(self, websocket_server):
        """Test message routing to appropriate handlers"""
        test_cases = [
            {"type": "subscribe", "channel": "temperature"},
            {"type": "unsubscribe", "channel": "pressure"},
            {"type": "heartbeat", "timestamp": 1640995200.0},
            {"type": "get_data", "device_id": "PLC_001", "tag": "temperature"}
        ]

        for message in test_cases:
            response = await websocket_server.handle_message("client_001", message)
            assert "status" in response
            assert response["status"] in ["success", "error"]

    @pytest.mark.asyncio
    async def test_error_handling(self, websocket_server):
        """Test error handling for invalid messages and connection issues"""
        # Test invalid JSON
        response = await websocket_server.handle_message("client_001", "invalid_json")
        assert response["status"] == "error"
        assert "Invalid JSON" in response["message"]

        # Test missing message type
        response = await websocket_server.handle_message("client_001", {"data": "test"})
        assert response["status"] == "error"
        assert "Missing message type" in response["message"]

        # Test unknown message type
        response = await websocket_server.handle_message("client_001", {"type": "unknown"})
        assert response["status"] == "error"
        assert "Unknown message type" in response["message"]

    @pytest.mark.asyncio
    async def test_data_broadcasting(self, websocket_server):
        """Test broadcasting data to subscribed clients"""
        # Register mock clients
        mock_websocket1 = AsyncMock()
        mock_websocket2 = AsyncMock()

        client1_id = websocket_server.connection_manager.register_connection(mock_websocket1)
        client2_id = websocket_server.connection_manager.register_connection(mock_websocket2)

        # Subscribe clients to different channels
        websocket_server.subscription_manager.subscribe(client1_id, "temperature")
        websocket_server.subscription_manager.subscribe(client2_id, "pressure")
        websocket_server.subscription_manager.subscribe(client2_id, "temperature")

        # Broadcast temperature data
        data = PLCDataPoint("PLC_001", 1640995200.0, "temperature", 25.5, "°C", "good")
        await websocket_server.broadcast_data("temperature", data)

        # Verify only subscribed clients received data
        mock_websocket1.send.assert_called_once()
        mock_websocket2.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, websocket_server):
        """Test performance monitoring and metrics collection"""
        # Simulate client connections
        for i in range(10):
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ("127.0.0.1", 8080 + i)
            websocket_server.connection_manager.register_connection(mock_websocket)

        metrics = websocket_server.get_performance_metrics()

        assert metrics["active_connections"] == 10
        assert "uptime" in metrics
        assert "messages_processed" in metrics
        assert "errors" in metrics


class TestIntegrationScenarios:
    """Test complete integration scenarios"""

    @pytest.mark.asyncio
    async def test_complete_plc_data_flow(self):
        """Test complete data flow from PLC to WebSocket clients"""
        # Mock dependencies
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)

        # Create server
        server = WebSocketServer(
            host="localhost",
            port=8765,
            redis_client=mock_redis,
            postgres_client=mock_postgres
        )

        # Mock client connection
        mock_websocket = AsyncMock()
        mock_websocket.remote_address = ("127.0.0.1", 8080)

        client_id = server.connection_manager.register_connection(mock_websocket)
        server.subscription_manager.subscribe(client_id, "temperature")

        # Simulate PLC data
        plc_data = PLCDataPoint(
            device_id="PLC_001",
            timestamp=1640995200.0,
            tag="temperature",
            value=25.5,
            unit="°C",
            quality="good"
        )

        # Publish and broadcast data
        await server.plc_streamer.publish_data(plc_data)
        await server.broadcast_data("temperature", plc_data)

        # Verify data was sent to client
        mock_websocket.send.assert_called_once()
        sent_data = json.loads(mock_websocket.send.call_args[0][0])
        assert sent_data["type"] == "data"
        assert sent_data["channel"] == "temperature"
        assert sent_data["data"]["device_id"] == "PLC_001"

    @pytest.mark.asyncio
    async def test_high_load_scenario(self):
        """Test server performance under high load"""
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)

        server = WebSocketServer(
            host="localhost",
            port=8765,
            redis_client=mock_redis,
            postgres_client=mock_postgres
        )

        # Simulate 100 concurrent clients
        clients = []
        for i in range(100):
            mock_websocket = AsyncMock()
            mock_websocket.remote_address = ("127.0.0.1", 8080 + i)
            client_id = server.connection_manager.register_connection(mock_websocket)
            server.subscription_manager.subscribe(client_id, "temperature")
            clients.append((client_id, mock_websocket))

        # Broadcast data to all clients
        plc_data = PLCDataPoint("PLC_001", 1640995200.0, "temperature", 25.5, "°C", "good")

        start_time = asyncio.get_event_loop().time()
        await server.broadcast_data("temperature", plc_data)
        end_time = asyncio.get_event_loop().time()

        # Verify performance (should complete in under 1 second)
        assert (end_time - start_time) < 1.0

        # Verify all clients received data
        for client_id, mock_websocket in clients:
            mock_websocket.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_fault_tolerance(self):
        """Test fault tolerance and error recovery"""
        mock_redis = AsyncMock(spec=redis.Redis)
        mock_postgres = AsyncMock(spec=psycopg.AsyncConnection)

        server = WebSocketServer(
            host="localhost",
            port=8765,
            redis_client=mock_redis,
            postgres_client=mock_postgres
        )

        # Simulate Redis connection failure
        mock_redis.xadd.side_effect = redis.RedisError("Connection failed")

        plc_data = PLCDataPoint("PLC_001", 1640995200.0, "temperature", 25.5, "°C", "good")

        # Should handle error gracefully
        try:
            await server.plc_streamer.publish_data(plc_data)
        except Exception as e:
            pytest.fail(f"Server should handle Redis errors gracefully: {e}")

        # Verify error was logged
        assert server.error_count > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
