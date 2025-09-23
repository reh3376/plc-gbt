"""
PLC Task Orchestrator - Enhanced Framework for Coding Task Completion

A modular framework that provides AI agents and LLMs with systematic task analysis,
planning, and execution capabilities.

Key Features:
- Multi-database memory integration (Redis, Neo4j, PostgreSQL, Qdrant)
- Industrial control domain awareness
- Mathematical validation with WolframAlpha Pro
- Comprehensive multi-tier validation framework
- Production deployment readiness validation
- Pattern recognition from similar implementations
- Real-time progress monitoring
"""

from plc_orchestrator.config.settings import OrchestratorConfig
from plc_orchestrator.core.analyzer import TaskAnalyzer
from plc_orchestrator.core.orchestrator import AITaskOrchestrator
from plc_orchestrator.core.progress import TaskProgressMonitor
from plc_orchestrator.core.validator import TaskValidator
from plc_orchestrator.utils.data_models import (
    ExecutionStep,
    TaskAnalysis,
    TaskProgressUpdate,
    ValidationResult,
)
from plc_orchestrator.utils.enums import (
    ControlSystemComplexity,
    ExecutionSteps,
    TaskComplexity,
    TaskStatus,
    ValidationSeverity,
    ValidationTier,
)

# Version info
__version__ = "2.0.0"
__author__ = "PLC-GBT Team"

# Public API
__all__ = [
    # Main orchestrator
    "AITaskOrchestrator",
    # Configuration
    "OrchestratorConfig",
    # Core components
    "TaskAnalyzer",
    "TaskValidator",
    "TaskProgressMonitor",
    # Enums
    "TaskComplexity",
    "TaskStatus",
    "ExecutionSteps",
    "ControlSystemComplexity",
    "ValidationTier",
    "ValidationSeverity",
    # Data models
    "TaskProgressUpdate",
    "ExecutionStep",
    "TaskAnalysis",
    "ValidationResult",
]


# Convenience function for quick start
def create_orchestrator(config_file: str | None = None, **kwargs) -> AITaskOrchestrator:
    """
    Create and configure an AI Task Orchestrator instance.

    Args:
        config_file: Optional path to configuration file
        **kwargs: Additional configuration overrides

    Returns:
        Configured AITaskOrchestrator instance

    Raises:
        ConfigurationError: If configuration validation fails

    Example:
        >>> orchestrator = create_orchestrator(enable_memory=True)
        >>> analysis = orchestrator.analyze_task("Build PLC data parser")
    """
    from plc_orchestrator.config.validators import validate_all_configs
    from plc_orchestrator.utils.errors import ConfigurationError

    # Create configuration
    config = OrchestratorConfig(config_file=config_file, **kwargs)

    # Validate configuration on startup
    try:
        validate_all_configs(config)
    except ConfigurationError as e:
        # Log the error before re-raising
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Configuration validation failed: {e}")
        raise

    return AITaskOrchestrator(config=config)
