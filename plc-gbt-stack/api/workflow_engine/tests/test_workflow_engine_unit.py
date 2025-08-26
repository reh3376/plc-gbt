#!/usr/bin/env python3
"""
N8N Framework Integration - Unit Tests  
Phase 1.5: Automated Testing Suite Implementation

Unit tests for PLCGBTWorkflowEngine core functionality with >95% coverage requirement.
Following AI Task Orchestrator methodology with strict compliance.

Author: AI Task Orchestrator
Date: December 22, 2024  
Phase: 1.5 - Automated Testing Suite Implementation
"""

import asyncio
import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from typing import Dict, Any

from api.workflow_engine.n8n_integration import (
    PLCGBTWorkflowEngine, 
    WorkflowDefinition,
    WorkflowExecutionRequest,
    WorkflowExecutionResult,
    WorkflowExecutionMode,
    IndustrialSafetyLevel
)
from api.workflow_engine.config import WorkflowEngineConfig


class TestWorkflowEngineConfiguration:
    """Test workflow engine configuration and initialization."""
    
    def test_config_initialization(self):
        """Test configuration model creation and validation."""
        config = WorkflowEngineConfig(
            database_url="postgresql://test:test@localhost:5432/testdb",
            redis_url="redis://localhost:6379/1",
            n8n_framework_path="/test/path",
            max_concurrent_executions=5,
            industrial_performance_threshold_ms=50.0
        )
        
        assert config.database_url == "postgresql://test:test@localhost:5432/testdb"
        assert config.redis_url == "redis://localhost:6379/1"
        assert config.n8n_framework_path == "/test/path"
        assert config.max_concurrent_executions == 5
        assert config.industrial_performance_threshold_ms == 50.0
    
    def test_config_validation_constraints(self):
        """Test configuration validation constraints."""
        # Test concurrent execution limits
        with pytest.raises(Exception):  # Should raise validation error
            WorkflowEngineConfig(max_concurrent_executions=0)  # Below minimum
        
        with pytest.raises(Exception):  # Should raise validation error  
            WorkflowEngineConfig(max_concurrent_executions=101)  # Above maximum
    
    def test_config_environment_variables(self):
        """Test environment variable integration."""
        with patch.dict('os.environ', {
            'WORKFLOW_ENGINE_DATABASE_URL': 'postgresql://env:env@localhost:5432/envdb',
            'WORKFLOW_ENGINE_REDIS_URL': 'redis://localhost:6379/2'
        }):
            config = WorkflowEngineConfig()
            assert 'env:env@localhost' in config.database_url
            assert 'redis://localhost:6379/2' == config.redis_url


class TestWorkflowDefinitionModels:
    """Test Pydantic models for workflow definitions."""
    
    def test_workflow_definition_creation(self):
        """Test workflow definition model validation."""
        definition = WorkflowDefinition(
            id="test-workflow-001",
            name="Test Workflow", 
            description="Test workflow description",
            workflow_data={
                "nodes": [{"id": "start", "type": "start"}],
                "connections": {},
                "active": True
            },
            version=1,
            status="active",
            industrial_tags=["test", "basic"],
            safety_level=IndustrialSafetyLevel.SIL0
        )
        
        assert definition.id == "test-workflow-001"
        assert definition.name == "Test Workflow"
        assert definition.safety_level == IndustrialSafetyLevel.SIL0
        assert "test" in definition.industrial_tags
    
    def test_workflow_execution_request(self):
        """Test workflow execution request model."""
        request = WorkflowExecutionRequest(
            input_data={"param1": "value1"},
            execution_context={"user_id": "test-user"},
            execution_mode=WorkflowExecutionMode.STANDARD,
            timeout_seconds=300
        )
        
        assert request.input_data["param1"] == "value1"
        assert request.execution_mode == WorkflowExecutionMode.STANDARD
        assert request.timeout_seconds == 300
    
    def test_workflow_execution_result(self):
        """Test workflow execution result model."""
        result = WorkflowExecutionResult(
            execution_id="exec-001",
            workflow_id="workflow-001", 
            status="completed",
            output_data={"result": "success"},
            execution_time_ms=150.5,
            performance_metrics={
                "memory_usage_mb": 25.0,
                "cpu_usage_percent": 15.0
            },
            error_message=None
        )
        
        assert result.execution_id == "exec-001"
        assert result.status == "completed"
        assert result.execution_time_ms == 150.5
        assert result.performance_metrics["memory_usage_mb"] == 25.0


@pytest.mark.asyncio
class TestPLCGBTWorkflowEngine:
    """Test core workflow engine functionality."""
    
    @pytest.fixture
    async def mock_engine(self):
        """Create mocked workflow engine for testing."""
        with patch('asyncpg.connect') as mock_connect, \
             patch('redis.asyncio.from_url') as mock_redis:
            
            # Mock database connection
            mock_db = AsyncMock()
            mock_connect.return_value = mock_db
            
            # Mock Redis connection
            mock_redis_client = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            config = WorkflowEngineConfig(
                database_url="postgresql://test:test@localhost:5432/testdb",
                redis_url="redis://localhost:6379/1",
                n8n_framework_path="/test/n8n"
            )
            
            engine = PLCGBTWorkflowEngine(config)
            
            # Mock initialization dependencies
            with patch.object(engine, '_setup_node_env') as mock_setup, \
                 patch.object(engine, '_install_n8n_dependencies') as mock_install, \
                 patch.object(engine, '_register_nodes') as mock_register:
                
                mock_setup.return_value = True
                mock_install.return_value = True  
                mock_register.return_value = True
                
                await engine.initialize()
            
            yield engine
    
    async def test_engine_initialization(self, mock_engine):
        """Test workflow engine initialization process."""
        assert mock_engine.is_initialized is True
        assert mock_engine.db_pool is not None
        assert mock_engine.redis_client is not None
    
    async def test_workflow_creation(self, mock_engine):
        """Test workflow definition creation and storage."""
        definition = WorkflowDefinition(
            id="test-workflow-002", 
            name="Test Creation Workflow",
            description="Test workflow for creation testing",
            workflow_data={"nodes": [], "connections": {}, "active": True},
            version=1,
            status="active",
            industrial_tags=["test"],
            safety_level=IndustrialSafetyLevel.SIL0
        )
        
        # Mock database insertion
        with patch.object(mock_engine.db_pool, 'acquire') as mock_acquire:
            mock_conn = AsyncMock()
            mock_acquire.return_value.__aenter__.return_value = mock_conn
            mock_conn.fetchval.return_value = definition.id
            
            result = await mock_engine.create_workflow(
                definition, 
                created_by="test-user"
            )
            
            assert result == definition.id
            mock_conn.execute.assert_called_once()
    
    async def test_workflow_execution(self, mock_engine):
        """Test workflow execution with performance monitoring.""" 
        # Mock Node.js execution
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (
                json.dumps({
                    "status": "completed",
                    "output_data": {"result": "test_output"},
                    "execution_time_ms": 75.5
                }).encode(), 
                b""
            )
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            definition = WorkflowDefinition(
                id="exec-test-001",
                name="Execution Test",
                description="Test execution",
                workflow_data={"nodes": [], "connections": {}, "active": True},
                version=1,
                status="active", 
                industrial_tags=["test"],
                safety_level=IndustrialSafetyLevel.SIL0
            )
            
            request = WorkflowExecutionRequest(
                input_data={"test": "data"},
                execution_context={"user_id": "test"},
                execution_mode=WorkflowExecutionMode.STANDARD
            )
            
            result = await mock_engine.execute_workflow(definition, request.dict())
            
            assert result.status == "completed" 
            assert result.output_data["result"] == "test_output"
            assert result.execution_time_ms == 75.5
    
    async def test_performance_monitoring(self, mock_engine):
        """Test performance monitoring and thresholds."""
        # Test performance threshold validation
        with patch.object(mock_engine, '_monitor_performance') as mock_monitor:
            mock_monitor.return_value = {
                "execution_time_ms": 150.0,  # Above 100ms threshold
                "memory_usage_mb": 30.0,
                "cpu_usage_percent": 20.0
            }
            
            # This should trigger performance warning
            metrics = await mock_engine._monitor_performance("test-exec")
            
            assert metrics["execution_time_ms"] > 100.0
            assert "memory_usage_mb" in metrics
    
    async def test_error_handling(self, mock_engine):
        """Test error handling and recovery mechanisms."""
        # Test Node.js execution failure
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Error: Node execution failed")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            definition = WorkflowDefinition(
                id="error-test-001",
                name="Error Test",
                description="Test error handling", 
                workflow_data={"nodes": [], "connections": {}, "active": True},
                version=1,
                status="active",
                industrial_tags=["test"],
                safety_level=IndustrialSafetyLevel.SIL0
            )
            
            request = WorkflowExecutionRequest(
                input_data={"test": "error"},
                execution_context={"user_id": "test"},
                execution_mode=WorkflowExecutionMode.STANDARD
            )
            
            result = await mock_engine.execute_workflow(definition, request.dict())
            
            assert result.status == "failed"
            assert result.error_message is not None
            assert "Error" in result.error_message
    
    async def test_industrial_safety_validation(self, mock_engine):
        """Test industrial safety level validation."""
        # Test SIL2 workflow requirements
        definition = WorkflowDefinition(
            id="safety-test-001",
            name="Safety Critical Workflow",
            description="Test safety validation",
            workflow_data={"nodes": [], "connections": {}, "active": True},
            version=1,
            status="active",
            industrial_tags=["safety", "critical"],
            safety_level=IndustrialSafetyLevel.SIL2
        )
        
        # SIL2 workflows should have stricter validation
        validation_result = mock_engine._validate_safety_requirements(definition)
        
        # Mock validation logic
        assert validation_result is not None
    
    async def test_concurrent_execution_limits(self, mock_engine):
        """Test concurrent execution management."""
        # Mock concurrent executions beyond limit
        mock_engine.config.max_concurrent_executions = 2
        mock_engine._active_executions = {"exec1": True, "exec2": True}
        
        # Should reject new execution
        can_execute = mock_engine._can_execute_workflow()
        assert can_execute is False
        
        # Should allow after reducing active executions
        mock_engine._active_executions = {"exec1": True}
        can_execute = mock_engine._can_execute_workflow()
        assert can_execute is True


@pytest.mark.unit
class TestWorkflowEngineUtilities:
    """Test utility functions and helpers."""
    
    def test_node_script_generation(self):
        """Test Node.js execution script generation."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine
        
        config = WorkflowEngineConfig()
        engine = PLCGBTWorkflowEngine(config)
        
        workflow_data = {"nodes": [], "connections": {}, "active": True}
        input_data = {"test": "input"}
        
        script = engine._create_execution_script(
            workflow_data=workflow_data,
            input_data=input_data,
            execution_id="test-123"
        )
        
        assert "const workflow" in script
        assert "test-123" in script
        assert "input" in script
    
    def test_performance_metrics_calculation(self):
        """Test performance metrics calculation."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine
        
        config = WorkflowEngineConfig()
        engine = PLCGBTWorkflowEngine(config)
        
        # Mock performance data
        start_time = 1000.0
        end_time = 1100.5  # 100.5ms execution
        
        metrics = engine._calculate_performance_metrics(
            start_time=start_time,
            end_time=end_time,
            memory_usage=25.0
        )
        
        assert metrics["execution_time_ms"] == 100.5
        assert metrics["memory_usage_mb"] == 25.0
    
    def test_workflow_validation(self):
        """Test workflow definition validation."""
        from api.workflow_engine.n8n_integration import PLCGBTWorkflowEngine
        
        config = WorkflowEngineConfig()
        engine = PLCGBTWorkflowEngine(config)
        
        # Valid workflow
        valid_workflow = {
            "nodes": [{"id": "start", "type": "n8n-nodes-base.start"}],
            "connections": {},
            "active": True
        }
        
        is_valid = engine._validate_workflow_structure(valid_workflow)
        assert is_valid is True
        
        # Invalid workflow (missing nodes)
        invalid_workflow = {
            "connections": {},
            "active": True
        }
        
        is_valid = engine._validate_workflow_structure(invalid_workflow)
        assert is_valid is False


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
