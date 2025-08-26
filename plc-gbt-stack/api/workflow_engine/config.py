#!/usr/bin/env python3
"""
N8N Framework Integration - Configuration Management
Phase 1.3: PLCGBTWorkflowEngine Configuration

Following AI Task Orchestrator TypeScript methodology with strict compliance.
This module provides configuration management for the workflow engine integration.

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.3 - Core Engine Integration
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class WorkflowEngineConfig(BaseSettings):
    """
    Configuration settings for PLC-GBT Workflow Engine.
    
    Uses Pydantic BaseSettings for environment variable integration
    and type validation following strict TypeScript methodology.
    """
    
    # Database configuration
    database_url: str = Field(
        default="postgresql://plc_user:CHANGE_PASSWORD@localhost:5432/plc_database",
        description="PostgreSQL database connection URL"
    )
    
    # Redis configuration  
    redis_url: str = Field(
        default="redis://localhost:6379",
        description="Redis connection URL for caching"
    )
    
    # N8N Framework configuration
    n8n_framework_path: Optional[str] = Field(
        default=None,
        description="Path to N8N framework directory"
    )
    
    # Performance configuration
    max_concurrent_executions: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum concurrent workflow executions"
    )
    
    default_execution_timeout: int = Field(
        default=300,
        ge=10,
        le=3600,
        description="Default workflow execution timeout in seconds"
    )
    
    real_time_execution_timeout: int = Field(
        default=10,
        ge=1,
        le=60,
        description="Real-time workflow execution timeout in seconds"
    )
    
    # Industrial configuration
    industrial_performance_threshold_ms: float = Field(
        default=100.0,
        ge=1.0,
        le=1000.0,
        description="Performance threshold for industrial workflows in milliseconds"
    )
    
    enable_performance_monitoring: bool = Field(
        default=True,
        description="Enable comprehensive performance monitoring"
    )
    
    enable_compliance_tracking: bool = Field(
        default=True,
        description="Enable industrial compliance tracking"
    )
    
    # Security configuration
    jwt_secret_key: str = Field(
        default="development-secret-key-change-in-production",
        description="JWT token secret key"
    )
    
    api_key_header: str = Field(
        default="Authorization",
        description="API key header name"
    )
    
    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    enable_debug_logging: bool = Field(
        default=False,
        description="Enable debug logging"
    )
    
    class Config:
        env_file = ".env"
        env_prefix = "WORKFLOW_ENGINE_"
        case_sensitive = False


def get_config() -> WorkflowEngineConfig:
    """Get workflow engine configuration instance."""
    return WorkflowEngineConfig()


# Global configuration instance
workflow_engine_config = get_config()
