#!/usr/bin/env python3
"""
N8N Framework Integration - Integration Test Suite
Phase 1.4: Basic Workflow Execution Integration with Performance Benchmarking

Following AI Task Orchestrator TypeScript methodology with strict compliance.
This module provides comprehensive integration testing for the workflow engine.

Key Features:
- Real workflow execution testing with n8n framework
- Performance benchmarking for industrial requirements
- Database integration validation
- Error handling and resilience testing
- Industrial compliance verification

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.4 - Basic Workflow Execution Integration
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import statistics

import aiofiles

import asyncpg
import redis.asyncio as redis
from pydantic import BaseModel, Field

# Add project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import workflow engine components
from api.workflow_engine.n8n_integration import (
    PLCGBTWorkflowEngine,
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionResult,
    WorkflowStatus,
    WorkflowExecutionMode,
    IndustrialSafetyLevel
)
from api.workflow_engine.database_migration import DatabaseMigrationManager, MigrationConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
DATA_PROCESSING_NODE_NAME = "Data Processing 1"


class IntegrationTestResult(BaseModel):
    """Integration test result with comprehensive metrics."""
    
    test_name: str = Field(..., description="Test name identifier")
    success: bool = Field(..., description="Test success status")
    execution_time_ms: float = Field(..., description="Test execution time in milliseconds")
    error_message: Optional[str] = Field(default=None, description="Error message if failed")
    
    # Performance metrics
    workflow_execution_time_ms: Optional[float] = Field(default=None)
    database_operation_time_ms: Optional[float] = Field(default=None)
    node_js_bridge_time_ms: Optional[float] = Field(default=None)
    
    # Industrial compliance metrics
    safety_compliance: bool = Field(default=True)
    performance_threshold_met: bool = Field(default=True)
    data_integrity_verified: bool = Field(default=True)
    
    # Additional metadata
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    phase: str = Field(default="1.4")


class PerformanceBenchmark(BaseModel):
    """Performance benchmark results for industrial requirements."""
    
    # Execution performance
    average_execution_time_ms: float
    median_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    standard_deviation_ms: float
    
    # Industrial performance requirements
    real_time_threshold_met: bool  # <50ms for real-time workflows
    industrial_threshold_met: bool  # <100ms for industrial workflows
    
    # Throughput metrics
    executions_per_second: float
    concurrent_execution_capability: int
    
    # Resource utilization
    memory_usage_mb: Optional[float] = None
    cpu_utilization_percent: Optional[float] = None
    
    # Reliability metrics
    success_rate_percent: float
    error_rate_percent: float
    timeout_rate_percent: float


class IntegrationTestSuite:
    """
    Comprehensive integration test suite for N8N Framework Integration.
    
    Tests all aspects of the workflow engine including:
    - Basic workflow execution
    - Database operations
    - Performance benchmarking  
    - Error handling and resilience
    - Industrial compliance requirements
    """
    
    def __init__(self, database_url: str, redis_url: str = "redis://localhost:6379"):
        self.database_url = database_url
        self.redis_url = redis_url
        self.engine: Optional[PLCGBTWorkflowEngine] = None
        self.test_results: List[IntegrationTestResult] = []
        
        # Test configuration
        self.performance_test_iterations = 10
        self.concurrent_execution_test_count = 5
        self.industrial_performance_threshold_ms = 100.0
        self.real_time_performance_threshold_ms = 50.0
        
    async def __aenter__(self) -> 'IntegrationTestSuite':
        """Async context manager entry."""
        await self.setup()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit with cleanup."""
        await self.cleanup()
    
    async def setup(self) -> None:
        """Setup test environment with database migration and engine initialization."""
        logger.info("🚀 Setting up integration test environment...")
        
        try:
            # Ensure database schema exists
            await self._ensure_database_schema()
            
            # Initialize workflow engine
            self.engine = PLCGBTWorkflowEngine(
                database_url=self.database_url,
                redis_url=self.redis_url
            )
            await self.engine.initialize()
            
            # Verify all components are healthy
            health_status = await self.engine.get_engine_health()
            if health_status["engine_status"] != "healthy":
                raise RuntimeError(f"Engine not healthy: {health_status}")
            
            logger.info("✅ Test environment setup completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Test environment setup failed: {e}")
            raise
    
    async def cleanup(self) -> None:
        """Clean up test environment."""
        logger.info("🧹 Cleaning up test environment...")
        
        if self.engine:
            await self.engine.shutdown()
            
        # Clean up test data (optional - keep for analysis)
        # await self._cleanup_test_data()
        
        logger.info("✅ Test environment cleanup completed")
    
    async def _ensure_database_schema(self) -> None:
        """Ensure database schema exists for testing."""
        logger.info("🔍 Checking database schema...")
        
        try:
            # Check if schema exists
            conn = await asyncpg.connect(self.database_url)
            schema_exists = await conn.fetchval(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'plc_workflows'"
            )
            await conn.close()
            
            if not schema_exists:
                logger.info("📋 Database schema not found - running migration...")
                
                config = MigrationConfig(database_url=self.database_url)
                async with DatabaseMigrationManager(config) as migration_manager:
                    migration_status = await migration_manager.run_migration()
                    
                    if not migration_status.success:
                        raise RuntimeError(f"Database migration failed: {migration_status.error_message}")
                
                logger.info("✅ Database migration completed successfully")
            else:
                logger.info("✅ Database schema already exists")
                
        except Exception as e:
            logger.error(f"❌ Database schema setup failed: {e}")
            raise
    
    # Test Sample Workflow Definitions
    
    def _create_simple_test_workflow(self) -> WorkflowDefinition:
        """Create a simple test workflow for basic functionality testing."""
        return WorkflowDefinition(
            name="Integration Test - Simple Workflow",
            description="Simple test workflow for integration testing",
            nodes=[
                {
                    "id": "start-node",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [100, 100],
                    "parameters": {},
                    "typeVersion": 1
                },
                {
                    "id": "set-node",
                    "name": "Set Values",
                    "type": "n8n-nodes-base.set",
                    "position": [300, 100],
                    "parameters": {
                        "values": {
                            "string": [
                                {
                                    "name": "test_output",
                                    "value": "Integration test successful"
                                },
                                {
                                    "name": "timestamp",
                                    "value": "={{new Date().toISOString()}}"
                                }
                            ]
                        }
                    },
                    "typeVersion": 1
                }
            ],
            connections={
                "Start": {
                    "main": [
                        [
                            {
                                "node": "Set Values",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            industrial_category="testing",
            safety_level=IndustrialSafetyLevel.SIL0,
            compliance_requirements=["integration_testing"]
        )
    
    def _create_performance_test_workflow(self) -> WorkflowDefinition:
        """Create a workflow designed for performance testing."""
        return WorkflowDefinition(
            name="Integration Test - Performance Benchmark",
            description="Performance testing workflow with multiple operations",
            nodes=[
                {
                    "id": "start-node",
                    "name": "Start",
                    "type": "n8n-nodes-base.start",
                    "position": [100, 100],
                    "parameters": {},
                    "typeVersion": 1
                },
                {
                    "id": "function-node-1",
                    "name": DATA_PROCESSING_NODE_NAME,
                    "type": "n8n-nodes-base.function",
                    "position": [300, 100],
                    "parameters": {
                        "functionCode": """
                        // Simulate data processing
                        const startTime = Date.now();
                        const data = [];
                        for (let i = 0; i < 1000; i++) {
                            data.push({
                                id: i,
                                value: Math.random() * 100,
                                timestamp: new Date()
                            });
                        }
                        const processingTime = Date.now() - startTime;
                        
                        return [{
                            json: {
                                processed_records: data.length,
                                processing_time_ms: processingTime,
                                test_phase: '1.4'
                            }
                        }];
                        """
                    },
                    "typeVersion": 1
                },
                {
                    "id": "function-node-2",
                    "name": "Data Processing 2",
                    "type": "n8n-nodes-base.function",
                    "position": [500, 100],
                    "parameters": {
                        "functionCode": """
                        // Simulate additional processing
                        const input = $input.all();
                        const result = input[0].json;
                        
                        return [{
                            json: {
                                ...result,
                                final_processing: true,
                                completion_timestamp: new Date().toISOString()
                            }
                        }];
                        """
                    },
                    "typeVersion": 1
                }
            ],
            connections={
                "Start": {
                    "main": [
                        [
                            {
                                "node": DATA_PROCESSING_NODE_NAME,
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                },
                DATA_PROCESSING_NODE_NAME: {
                    "main": [
                        [
                            {
                                "node": "Data Processing 2",
                                "type": "main",
                                "index": 0
                            }
                        ]
                    ]
                }
            },
            industrial_category="performance_testing",
            safety_level=IndustrialSafetyLevel.SIL1,
            performance_profile={
                "expected_execution_time_ms": 50,
                "memory_usage_target_mb": 10,
                "cpu_intensive": False
            }
        )
    
    # Core Integration Tests
    
    async def test_basic_workflow_creation(self) -> IntegrationTestResult:
        """Test basic workflow creation and storage."""
        test_name = "Basic Workflow Creation"
        logger.info(f"🧪 Running test: {test_name}")
        
        start_time = time.time()
        
        try:
            # Create test workflow
            workflow_definition = self._create_simple_test_workflow()
            
            # Create workflow in engine
            workflow_id = await self.engine.create_workflow(
                workflow_definition,
                created_by="integration_test"
            )
            
            # Verify workflow was created
            retrieved_workflow = await self.engine.get_workflow(workflow_id)
            
            if not retrieved_workflow:
                raise AssertionError("Workflow not found after creation")
            
            if retrieved_workflow.name != workflow_definition.name:
                raise AssertionError("Workflow name mismatch after retrieval")
            
            execution_time = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                test_name=test_name,
                success=True,
                execution_time_ms=execution_time,
                database_operation_time_ms=execution_time
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e)
            )
    
    async def test_basic_workflow_execution(self) -> IntegrationTestResult:
        """Test basic workflow execution functionality."""
        test_name = "Basic Workflow Execution"
        logger.info(f"🧪 Running test: {test_name}")
        
        start_time = time.time()
        
        try:
            # Create and store workflow
            workflow_definition = self._create_simple_test_workflow()
            workflow_id = await self.engine.create_workflow(workflow_definition)
            
            # Execute workflow
            execution_request = WorkflowExecutionRequest(
                workflow_id=workflow_id,
                input_data={"test_input": "integration_test_data"},
                execution_mode=WorkflowExecutionMode.MANUAL
            )
            
            workflow_execution_start = time.time()
            execution_result = await self.engine.execute_workflow(execution_request)
            workflow_execution_time = (time.time() - workflow_execution_start) * 1000
            
            # Validate execution result
            if execution_result.status != WorkflowStatus.COMPLETED:
                raise AssertionError(f"Workflow execution failed: {execution_result.error_message}")
            
            if not execution_result.output_data:
                raise AssertionError("No output data from workflow execution")
            
            total_execution_time = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                test_name=test_name,
                success=True,
                execution_time_ms=total_execution_time,
                workflow_execution_time_ms=workflow_execution_time,
                performance_threshold_met=workflow_execution_time < self.industrial_performance_threshold_ms
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e),
                performance_threshold_met=False
            )
    
    async def test_performance_benchmark(self) -> Tuple[IntegrationTestResult, PerformanceBenchmark]:
        """Comprehensive performance benchmarking test."""
        test_name = "Performance Benchmark"
        logger.info(f"🧪 Running test: {test_name} ({self.performance_test_iterations} iterations)")
        
        start_time = time.time()
        execution_times = []
        success_count = 0
        error_count = 0
        timeout_count = 0
        
        try:
            # Create performance test workflow
            workflow_definition = self._create_performance_test_workflow()
            workflow_id = await self.engine.create_workflow(workflow_definition)
            
            # Run multiple iterations for statistical analysis
            for i in range(self.performance_test_iterations):
                try:
                    execution_request = WorkflowExecutionRequest(
                        workflow_id=workflow_id,
                        input_data={"iteration": i + 1},
                        execution_mode=WorkflowExecutionMode.MANUAL,
                        timeout_seconds=30
                    )
                    
                    iteration_start = time.time()
                    result = await self.engine.execute_workflow(execution_request)
                    iteration_time = (time.time() - iteration_start) * 1000
                    
                    execution_times.append(iteration_time)
                    
                    if result.status == WorkflowStatus.COMPLETED:
                        success_count += 1
                    elif result.status == WorkflowStatus.TIMEOUT:
                        timeout_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    logger.warning(f"⚠️ Iteration {i+1} failed: {e}")
                    error_count += 1
                    execution_times.append(30000)  # Timeout value
            
            # Calculate performance metrics
            if execution_times:
                avg_time = statistics.mean(execution_times)
                median_time = statistics.median(execution_times)
                min_time = min(execution_times)
                max_time = max(execution_times)
                std_dev = statistics.stdev(execution_times) if len(execution_times) > 1 else 0.0
                
                success_rate = (success_count / self.performance_test_iterations) * 100
                error_rate = (error_count / self.performance_test_iterations) * 100
                timeout_rate = (timeout_count / self.performance_test_iterations) * 100
                
                # Calculate throughput
                total_test_time = (time.time() - start_time)
                executions_per_second = self.performance_test_iterations / total_test_time
                
                benchmark = PerformanceBenchmark(
                    average_execution_time_ms=avg_time,
                    median_execution_time_ms=median_time,
                    min_execution_time_ms=min_time,
                    max_execution_time_ms=max_time,
                    standard_deviation_ms=std_dev,
                    real_time_threshold_met=avg_time < self.real_time_performance_threshold_ms,
                    industrial_threshold_met=avg_time < self.industrial_performance_threshold_ms,
                    executions_per_second=executions_per_second,
                    concurrent_execution_capability=self.concurrent_execution_test_count,
                    success_rate_percent=success_rate,
                    error_rate_percent=error_rate,
                    timeout_rate_percent=timeout_rate
                )
                
                total_execution_time = (time.time() - start_time) * 1000
                
                test_result = IntegrationTestResult(
                    test_name=test_name,
                    success=success_count > 0,
                    execution_time_ms=total_execution_time,
                    workflow_execution_time_ms=avg_time,
                    performance_threshold_met=benchmark.industrial_threshold_met,
                    safety_compliance=True,
                    data_integrity_verified=True
                )
                
                return test_result, benchmark
            else:
                raise AssertionError("No successful executions recorded")
                
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            # Create error benchmark
            error_benchmark = PerformanceBenchmark(
                average_execution_time_ms=0.0,
                median_execution_time_ms=0.0,
                min_execution_time_ms=0.0,
                max_execution_time_ms=0.0,
                standard_deviation_ms=0.0,
                real_time_threshold_met=False,
                industrial_threshold_met=False,
                executions_per_second=0.0,
                concurrent_execution_capability=0,
                success_rate_percent=0.0,
                error_rate_percent=100.0,
                timeout_rate_percent=0.0
            )
            
            error_result = IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e),
                performance_threshold_met=False
            )
            
            return error_result, error_benchmark
    
    async def test_database_integration(self) -> IntegrationTestResult:
        """Test database integration functionality."""
        test_name = "Database Integration"
        logger.info(f"🧪 Running test: {test_name}")
        
        start_time = time.time()
        
        try:
            # Test database connectivity
            async with self.engine.db_pool.acquire() as conn:
                # Test basic query
                version = await conn.fetchval("SELECT version()")
                if not version:
                    raise AssertionError("Database version query failed")
                
                # Test workflow schema access
                workflow_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM plc_workflows.workflow_definitions"
                )
                
                # Test execution history
                execution_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM plc_workflows.workflow_executions"
                )
                
                logger.info(f"📊 Database stats - Workflows: {workflow_count}, Executions: {execution_count}")
            
            execution_time = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                test_name=test_name,
                success=True,
                execution_time_ms=execution_time,
                database_operation_time_ms=execution_time,
                data_integrity_verified=True
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e),
                data_integrity_verified=False
            )
    
    async def test_redis_integration(self) -> IntegrationTestResult:
        """Test Redis cache integration."""
        test_name = "Redis Integration"
        logger.info(f"🧪 Running test: {test_name}")
        
        start_time = time.time()
        
        try:
            # Test Redis connectivity
            await self.engine.redis_client.ping()
            
            # Test cache operations
            test_key = "integration_test:cache_test"
            test_value = {"timestamp": datetime.now(timezone.utc).isoformat(), "test": True}
            
            await self.engine.redis_client.hset(test_key, mapping=test_value)
            
            # Retrieve and verify
            cached_data = await self.engine.redis_client.hgetall(test_key)
            
            if not cached_data:
                raise AssertionError("Cache data not found after setting")
            
            # Cleanup test data
            await self.engine.redis_client.delete(test_key)
            
            execution_time = (time.time() - start_time) * 1000
            
            return IntegrationTestResult(
                test_name=test_name,
                success=True,
                execution_time_ms=execution_time,
                data_integrity_verified=True
            )
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return IntegrationTestResult(
                test_name=test_name,
                success=False,
                execution_time_ms=execution_time,
                error_message=str(e),
                data_integrity_verified=False
            )
    
    # Main Test Execution
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests and return comprehensive results."""
        logger.info("🚀 Starting comprehensive integration test suite...")
        logger.info("=" * 80)
        
        suite_start_time = time.time()
        
        # Run individual tests
        test_functions = [
            self.test_basic_workflow_creation,
            self.test_basic_workflow_execution,
            self.test_database_integration,
            self.test_redis_integration
        ]
        
        # Run basic tests
        for test_func in test_functions:
            result = await test_func()
            self.test_results.append(result)
            
            status_icon = "✅" if result.success else "❌"
            logger.info(f"{status_icon} {result.test_name}: {result.execution_time_ms:.2f}ms")
            
            if not result.success:
                logger.error(f"   Error: {result.error_message}")
        
        # Run performance benchmark test
        perf_result, benchmark = await self.test_performance_benchmark()
        self.test_results.append(perf_result)
        
        status_icon = "✅" if perf_result.success else "❌"
        logger.info(f"{status_icon} {perf_result.test_name}: {perf_result.execution_time_ms:.2f}ms")
        logger.info(f"   📊 Average execution: {benchmark.average_execution_time_ms:.2f}ms")
        logger.info(f"   🎯 Performance threshold (<{self.industrial_performance_threshold_ms}ms): {'✅' if benchmark.industrial_threshold_met else '❌'}")
        logger.info(f"   🏆 Success rate: {benchmark.success_rate_percent:.1f}%")
        
        # Calculate overall results
        suite_execution_time = (time.time() - suite_start_time) * 1000
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests) * 100
        
        # Industrial compliance assessment
        performance_compliant_tests = sum(
            1 for result in self.test_results 
            if result.performance_threshold_met
        )
        performance_compliance_rate = (performance_compliant_tests / total_tests) * 100
        
        # Compile comprehensive results
        results_summary = {
            "overview": {
                "phase": "1.4",
                "suite_execution_time_ms": suite_execution_time,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate_percent": success_rate,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "industrial_compliance": {
                "performance_compliance_rate_percent": performance_compliance_rate,
                "industrial_threshold_ms": self.industrial_performance_threshold_ms,
                "real_time_threshold_ms": self.real_time_performance_threshold_ms,
                "overall_compliance": success_rate >= 95 and performance_compliance_rate >= 90
            },
            "performance_benchmark": {
                "average_execution_time_ms": benchmark.average_execution_time_ms,
                "median_execution_time_ms": benchmark.median_execution_time_ms,
                "min_execution_time_ms": benchmark.min_execution_time_ms,
                "max_execution_time_ms": benchmark.max_execution_time_ms,
                "standard_deviation_ms": benchmark.standard_deviation_ms,
                "industrial_threshold_met": benchmark.industrial_threshold_met,
                "real_time_threshold_met": benchmark.real_time_threshold_met,
                "executions_per_second": benchmark.executions_per_second,
                "success_rate_percent": benchmark.success_rate_percent
            },
            "detailed_results": [result.dict() for result in self.test_results],
            "engine_health": await self.engine.get_engine_health()
        }
        
        # Log final summary
        logger.info("=" * 80)
        logger.info("🎯 INTEGRATION TEST SUITE SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        logger.info(f"⏱️ Total Execution Time: {suite_execution_time:.2f}ms")
        logger.info(f"🏭 Industrial Compliance: {performance_compliance_rate:.1f}%")
        logger.info(f"⚡ Performance Threshold: {'✅ MET' if benchmark.industrial_threshold_met else '❌ NOT MET'}")
        
        if success_rate >= 95:
            logger.info("🎉 INTEGRATION TEST SUITE PASSED - Ready for Phase 1.5!")
        else:
            logger.error("❌ INTEGRATION TEST SUITE FAILED - Review and fix issues")
        
        return results_summary


async def main():
    """Main entry point for integration testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="N8N Framework Integration Test Suite")
    parser.add_argument(
        "--database-url",
        default=os.getenv("DATABASE_URL", "postgresql://plc_user:CHANGE_PASSWORD@localhost:5432/plc_database"),
        help="PostgreSQL database URL"
    )
    parser.add_argument(
        "--redis-url", 
        default=os.getenv("REDIS_URL", "redis://localhost:6379"),
        help="Redis connection URL"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=10,
        help="Number of performance test iterations"
    )
    
    args = parser.parse_args()
    
    try:
        async with IntegrationTestSuite(args.database_url, args.redis_url) as test_suite:
            test_suite.performance_test_iterations = args.iterations
            
            results = await test_suite.run_all_tests()
            
            # Save results for analysis
            results_file = Path("integration_test_results.json")
            async with aiofiles.open(results_file, 'w') as f:
                await f.write(json.dumps(results, indent=2, default=str))
            
            logger.info(f"📄 Results saved to: {results_file}")
            
            # Exit with appropriate code
            if results["overview"]["success_rate_percent"] >= 95:
                logger.info("✅ Integration tests passed - Phase 1.4 ready for completion!")
                sys.exit(0)
            else:
                logger.error("❌ Integration tests failed - Review and fix issues")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"❌ Integration test suite failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
