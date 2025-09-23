"""
PLC-GBT Workflow Engine Configuration

This module provides centralized configuration management for the N8N Framework
integration within PLC-GBT. It handles database connections, paths, logging,
and performance settings required for industrial automation workflows.

Industrial Requirements:
- Database: PostgreSQL with asyncpg for async operations
- Redis: Caching and session management  
- Node.js: N8N workflow execution environment
- Performance: <100ms execution overhead target
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
    and validation. Supports both development and production environments
    with industrial-grade performance and reliability requirements.
    """
    
    # Database Configuration (PostgreSQL)
    database_url: str = Field(
        default="postgresql://plc_user:CHANGE_PASSWORD@localhost:5432/plc_gbt",
        description="PostgreSQL database connection URL for workflow storage"
    )
    
    # Redis Configuration (Caching & Session Management)
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for caching and session management"
    )
    
    # Node.js Environment Configuration
    node_path: str = Field(
        default="/usr/local/bin/node",
        description="Path to Node.js executable for N8N workflow execution"
    )
    
    # N8N Framework Integration Path
    n8n_framework_path: Path = Field(
        default=Path(__file__).parent.parent.parent / "n8n-framework",
        description="Path to cloned N8N framework for workflow execution"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level for workflow engine (DEBUG, INFO, WARNING, ERROR)"
    )
    
    # Performance & Industrial Requirements  
    performance_threshold_ms: float = Field(
        default=100.0,
        description="Maximum acceptable workflow execution overhead in milliseconds"
    )
    
    max_concurrent_executions: int = Field(
        default=10,
        description="Maximum number of concurrent workflow executions"
    )
    
    execution_timeout_seconds: int = Field(
        default=300,
        description="Default timeout for workflow execution in seconds"
    )
    
    # Industrial Safety Configuration
    enable_safety_validation: bool = Field(
        default=True,
        description="Enable industrial safety level validation for workflows"
    )
    
    # Development vs Production Environment
    environment: str = Field(
        default="development",
        description="Runtime environment (development, staging, production)"
    )
    
    class Config:
        """Pydantic configuration for environment variable loading."""
        env_prefix = "WORKFLOW_ENGINE_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_config() -> WorkflowEngineConfig:
    """
    Factory function to create and return workflow engine configuration.
    
    Returns:
        WorkflowEngineConfig: Configured instance with environment variables loaded
        
    Example:
        >>> config = get_config()
        >>> print(config.database_url)
        postgresql://plc_user:password@localhost:5432/plc_gbt
    """
    return WorkflowEngineConfig()


# Global configuration instance for module-level access
_config_instance: Optional[WorkflowEngineConfig] = None


def get_global_config() -> WorkflowEngineConfig:
    """
    Get global singleton configuration instance.
    
    Returns:
        WorkflowEngineConfig: Global configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = get_config()
    return _config_instance
