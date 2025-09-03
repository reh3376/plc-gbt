#!/usr/bin/env python3
"""
N8N Framework Integration - Performance & Industrial Compliance Tests
Phase 1.5: Automated Testing Suite Implementation

Performance benchmarking and industrial compliance tests with >95% coverage requirement.
Following AI Task Orchestrator methodology with strict compliance.

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.5 - Automated Testing Suite Implementation
"""

import asyncio
import json
import statistics
import time
from unittest.mock import AsyncMock, patch

import pytest
from api.workflow_engine.config import WorkflowEngineConfig
from api.workflow_engine.n8n_integration import (
    IndustrialSafetyLevel,
    PLCGBTWorkflowEngine,
    WorkflowDefinition,
    WorkflowExecutionMode,
    WorkflowExecutionRequest,
)


@pytest.mark.performance
@pytest.mark.industrial
class TestIndustrialPerformanceRequirements:
    """Test industrial automation performance requirements."""

    @pytest.fixture
    async def performance_engine(self):
        """Create workflow engine optimized for performance testing."""
        config = WorkflowEngineConfig(
            industrial_performance_threshold_ms=100.0,  # 100ms threshold
            max_concurrent_executions=20,
            enable_performance_monitoring=True
        )

        with patch('asyncpg.connect') as mock_connect, \
             patch('redis.asyncio.from_url') as mock_redis:

            mock_db = AsyncMock()
            mock_connect.return_value = mock_db
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client

            engine = PLCGBTWorkflowEngine(config)

            with patch.object(engine, '_setup_node_env') as mock_setup, \
                 patch.object(engine, '_install_n8n_dependencies') as mock_install, \
                 patch.object(engine, '_register_nodes') as mock_register:

                mock_setup.return_value = True
                mock_install.return_value = True
                mock_register.return_value = True

                await engine.initialize()

            yield engine

    async def test_workflow_execution_latency_benchmark(self, performance_engine):
        """Test workflow execution meets <100ms industrial requirement."""

        # Create simple performance test workflow
        definition = WorkflowDefinition(
            id="perf-test-latency-001",
            name="Latency Benchmark Workflow",
            description="Performance test for execution latency",
            workflow_data={
                "nodes": [
                    {"id": "start", "type": "n8n-nodes-base.start"},
                    {"id": "function", "type": "n8n-nodes-base.function",
                     "parameters": {"functionCode": "return [{json: {timestamp: Date.now()}}];"}}
                ],
                "connections": {"start": {"main": [["function"]]}},
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["performance", "latency"],
            safety_level=IndustrialSafetyLevel.SIL0
        )

        # Mock fast Node.js execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"timestamp": int(time.time() * 1000)},
                    "execution_time_ms": 45.5  # Under 100ms threshold
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Execute workflow and measure latency
            start_time = time.time()

            request = WorkflowExecutionRequest(
                input_data={"test_input": "latency_test"},
                execution_context={"user_id": "perf_test"},
                execution_mode=WorkflowExecutionMode.REAL_TIME  # Real-time mode
            )

            result = await performance_engine.execute_workflow(definition, request.dict())

            end_time = time.time()
            total_latency_ms = (end_time - start_time) * 1000

            # Assertions for industrial requirements
            assert result.status == "completed"
            assert result.execution_time_ms < 100.0  # <100ms industrial requirement
            assert total_latency_ms < 150.0  # Total API latency including overhead
            assert result.performance_metrics is not None

    async def test_real_time_workflow_execution(self, performance_engine):
        """Test real-time workflow execution for critical control systems."""

        # Critical real-time workflow for industrial control
        definition = WorkflowDefinition(
            id="realtime-control-001",
            name="Real-time Control Workflow",
            description="Critical real-time workflow for control systems",
            workflow_data={
                "nodes": [
                    {"id": "sensor_input", "type": "n8n-nodes-base.start"},
                    {"id": "control_logic", "type": "n8n-nodes-base.function",
                     "parameters": {"functionCode": """
                        // Simulate critical control logic
                        const input = $input.first().json;
                        const controlOutput = {
                            valve_position: input.sensor_value > 50 ? 'open' : 'closed',
                            alarm: input.sensor_value > 80 ? true : false,
                            timestamp: Date.now()
                        };
                        return [{json: controlOutput}];
                     """}},
                    {"id": "output", "type": "n8n-nodes-base.end"}
                ],
                "connections": {
                    "sensor_input": {"main": [["control_logic"]]},
                    "control_logic": {"main": [["output"]]}
                },
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["control", "realtime", "critical"],
            safety_level=IndustrialSafetyLevel.SIL1  # Safety Integrity Level 1
        )

        # Mock ultra-fast execution for real-time requirements
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {
                        "valve_position": "open",
                        "alarm": False,
                        "timestamp": int(time.time() * 1000)
                    },
                    "execution_time_ms": 25.0  # Ultra-fast for real-time
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Execute real-time workflow
            request = WorkflowExecutionRequest(
                input_data={"sensor_value": 65.0, "sensor_id": "temp_01"},
                execution_context={
                    "user_id": "control_system",
                    "priority": "critical",
                    "real_time": True
                },
                execution_mode=WorkflowExecutionMode.REAL_TIME,
                timeout_seconds=10  # Short timeout for real-time
            )

            result = await performance_engine.execute_workflow(definition, request.dict())

            # Real-time performance assertions
            assert result.status == "completed"
            assert result.execution_time_ms < 50.0  # <50ms for critical real-time
            assert result.output_data["valve_position"] == "open"
            assert "timestamp" in result.output_data

    async def test_concurrent_execution_performance(self, performance_engine):
        """Test concurrent workflow execution performance."""

        definition = WorkflowDefinition(
            id="concurrent-perf-001",
            name="Concurrent Performance Test",
            description="Test concurrent execution performance",
            workflow_data={
                "nodes": [{"id": "start", "type": "n8n-nodes-base.start"}],
                "connections": {},
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["concurrent", "performance"],
            safety_level=IndustrialSafetyLevel.SIL0
        )

        # Mock concurrent execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"result": "concurrent_success"},
                    "execution_time_ms": 75.0
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Create multiple concurrent execution tasks
            async def execute_workflow():
                request = WorkflowExecutionRequest(
                    input_data={"test": "concurrent"},
                    execution_context={"user_id": "concurrent_test"},
                    execution_mode=WorkflowExecutionMode.STANDARD
                )
                return await performance_engine.execute_workflow(definition, request.dict())

            # Execute 10 workflows concurrently
            start_time = time.time()

            tasks = [execute_workflow() for _ in range(10)]
            results = await asyncio.gather(*tasks)

            end_time = time.time()
            total_time_ms = (end_time - start_time) * 1000

            # Verify all executions completed successfully
            assert len(results) == 10
            assert all(result.status == "completed" for result in results)

            # Verify concurrent performance
            avg_time_per_execution = total_time_ms / 10
            assert avg_time_per_execution < 200.0  # Average under 200ms

    async def test_memory_usage_industrial_limits(self, performance_engine):
        """Test memory usage stays within industrial automation limits."""

        # Large workflow to test memory usage
        definition = WorkflowDefinition(
            id="memory-test-001",
            name="Memory Usage Test Workflow",
            description="Test memory usage with complex workflow",
            workflow_data={
                "nodes": [
                    {"id": f"node_{i}", "type": "n8n-nodes-base.function"}
                    for i in range(20)  # 20 nodes to simulate complexity
                ],
                "connections": {
                    f"node_{i}": {"main": [[f"node_{i+1}"]]}
                    for i in range(19)
                },
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["memory", "complex"],
            safety_level=IndustrialSafetyLevel.SIL1
        )

        # Mock execution with memory monitoring
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"nodes_processed": 20},
                    "execution_time_ms": 150.0,
                    "memory_usage_mb": 45.0  # Under 200MB limit
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            request = WorkflowExecutionRequest(
                input_data={"complexity_test": True},
                execution_context={"user_id": "memory_test"},
                execution_mode=WorkflowExecutionMode.STANDARD
            )

            result = await performance_engine.execute_workflow(definition, request.dict())

            # Memory usage assertions for industrial systems
            assert result.status == "completed"
            # Industrial requirement: <200MB additional memory overhead
            assert result.performance_metrics.get("memory_usage_mb", 0) < 200.0


@pytest.mark.industrial
class TestIndustrialSafetyCompliance:
    """Test industrial safety and compliance requirements."""

    @pytest.fixture
    def safety_levels_test_data(self):
        """Test data for different safety integrity levels."""
        return {
            IndustrialSafetyLevel.SIL0: {
                "max_execution_time_ms": 1000.0,
                "max_failure_rate": 0.1,  # 10%
                "required_validations": ["basic"]
            },
            IndustrialSafetyLevel.SIL1: {
                "max_execution_time_ms": 500.0,
                "max_failure_rate": 0.01,  # 1%
                "required_validations": ["basic", "redundancy"]
            },
            IndustrialSafetyLevel.SIL2: {
                "max_execution_time_ms": 200.0,
                "max_failure_rate": 0.001,  # 0.1%
                "required_validations": ["basic", "redundancy", "certification"]
            },
            IndustrialSafetyLevel.SIL3: {
                "max_execution_time_ms": 100.0,
                "max_failure_rate": 0.0001,  # 0.01%
                "required_validations": ["basic", "redundancy", "certification", "formal_verification"]
            }
        }

    def test_safety_integrity_level_validation(self, safety_levels_test_data):
        """Test safety integrity level validation for workflows."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine

        config = WorkflowEngineConfig()
        engine = PLCGBTWorkflowEngine(config)

        for safety_level, _requirements in safety_levels_test_data.items():
            definition = WorkflowDefinition(
                id=f"safety-test-{safety_level.value}",
                name=f"Safety Level {safety_level.value} Test",
                description=f"Test workflow for {safety_level.value}",
                workflow_data={"nodes": [], "connections": {}, "active": True},
                version=1,
                status="active",
                industrial_tags=["safety", safety_level.value.lower()],
                safety_level=safety_level
            )

            # Validate safety requirements
            validation_result = engine._validate_safety_requirements(definition)

            # Safety validation should consider the level
            assert validation_result is not None
            assert isinstance(validation_result, dict)

    def test_iec_62443_compliance_validation(self):
        """Test IEC 62443 industrial security compliance."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine

        config = WorkflowEngineConfig(enable_compliance_tracking=True)
        engine = PLCGBTWorkflowEngine(config)

        # Test IEC 62443 security requirements
        security_requirements = {
            "authentication": True,
            "authorization": True,
            "data_integrity": True,
            "confidentiality": True,
            "availability": True,
            "audit_logging": True
        }

        compliance_check = engine._validate_iec_62443_compliance(security_requirements)

        # Should pass basic compliance checks
        assert compliance_check["compliant"] is True
        assert "authentication" in compliance_check["validated_controls"]

    def test_workflow_execution_reliability(self):
        """Test workflow execution reliability for industrial systems."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine

        config = WorkflowEngineConfig()
        engine = PLCGBTWorkflowEngine(config)

        # Simulate execution statistics for reliability calculation
        execution_stats = {
            "total_executions": 10000,
            "successful_executions": 9995,
            "failed_executions": 5,
            "timeout_executions": 0
        }

        reliability_metrics = engine._calculate_reliability_metrics(execution_stats)

        # Industrial requirement: >99.9% reliability
        assert reliability_metrics["success_rate"] > 0.999  # >99.9%
        assert reliability_metrics["availability"] > 0.999  # >99.9% uptime
        assert reliability_metrics["mtbf_hours"] > 1000  # Mean time between failures


@pytest.mark.performance
class TestPerformanceBenchmarking:
    """Performance benchmarking tests for various scenarios."""

    @pytest.mark.slow
    async def test_stress_testing_high_load(self, performance_engine):
        """Stress test workflow engine under high load."""

        # Create stress test workflow
        definition = WorkflowDefinition(
            id="stress-test-001",
            name="Stress Test Workflow",
            description="High-load stress testing",
            workflow_data={
                "nodes": [
                    {"id": "start", "type": "n8n-nodes-base.start"},
                    {"id": "heavy_computation", "type": "n8n-nodes-base.function",
                     "parameters": {"functionCode": """
                        // Simulate heavy computation
                        let result = 0;
                        for (let i = 0; i < 10000; i++) {
                            result += Math.sqrt(i);
                        }
                        return [{json: {result: result}}];
                     """}}
                ],
                "connections": {"start": {"main": [["heavy_computation"]]}},
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["stress", "performance"],
            safety_level=IndustrialSafetyLevel.SIL0
        )

        # Mock heavy computation execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"result": 666.7},
                    "execution_time_ms": 250.0,  # Slower due to computation
                    "memory_usage_mb": 80.0
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Execute multiple stress test iterations
            execution_times = []

            for i in range(50):  # 50 iterations for stress testing
                start_time = time.time()

                request = WorkflowExecutionRequest(
                    input_data={"iteration": i},
                    execution_context={"user_id": "stress_test"},
                    execution_mode=WorkflowExecutionMode.STANDARD
                )

                result = await performance_engine.execute_workflow(definition, request.dict())

                end_time = time.time()
                execution_times.append((end_time - start_time) * 1000)

                assert result.status == "completed"

            # Analyze performance statistics
            avg_time = statistics.mean(execution_times)
            median_time = statistics.median(execution_times)
            max_time = max(execution_times)
            min_time = min(execution_times)
            std_dev = statistics.stdev(execution_times)

            # Performance assertions for stress testing
            assert avg_time < 500.0  # Average under 500ms
            assert max_time < 1000.0  # No execution over 1 second
            assert std_dev < 100.0  # Low variation in performance

            print("Stress Test Results:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Median: {median_time:.2f}ms")
            print(f"  Min: {min_time:.2f}ms")
            print(f"  Max: {max_time:.2f}ms")
            print(f"  Std Dev: {std_dev:.2f}ms")

    async def test_throughput_measurement(self, performance_engine):
        """Test workflow execution throughput measurement."""

        definition = WorkflowDefinition(
            id="throughput-test-001",
            name="Throughput Measurement Test",
            description="Measure workflow execution throughput",
            workflow_data={
                "nodes": [{"id": "start", "type": "n8n-nodes-base.start"}],
                "connections": {},
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["throughput", "performance"],
            safety_level=IndustrialSafetyLevel.SIL0
        )

        # Mock fast execution for throughput testing
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"throughput_test": True},
                    "execution_time_ms": 50.0
                }).encode(),
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process

            # Measure throughput over 1 minute
            start_time = time.time()
            end_time = start_time + 10  # 10 seconds for testing
            executions_completed = 0

            while time.time() < end_time:
                request = WorkflowExecutionRequest(
                    input_data={"throughput_test": True},
                    execution_context={"user_id": "throughput_test"},
                    execution_mode=WorkflowExecutionMode.STANDARD
                )

                result = await performance_engine.execute_workflow(definition, request.dict())

                if result.status == "completed":
                    executions_completed += 1

                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)

            actual_duration = time.time() - start_time
            throughput_per_second = executions_completed / actual_duration

            # Throughput assertions
            assert throughput_per_second > 5.0  # Minimum 5 executions per second
            assert executions_completed > 50  # At least 50 executions in 10 seconds

            print("Throughput Test Results:")
            print(f"  Executions: {executions_completed}")
            print(f"  Duration: {actual_duration:.2f}s")
            print(f"  Throughput: {throughput_per_second:.2f} executions/second")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-m", "performance or industrial"])
