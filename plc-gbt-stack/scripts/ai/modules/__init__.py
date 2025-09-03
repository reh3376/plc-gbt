"""
PLC-GPT Modular Architecture
============================

Core modules for reusable functionality across the entire codebase.

Modules:
- core: Database connections, logging, configuration
- metrics: Performance metric calculations and classifications
- data: Data loading, validation, preprocessing
- ai: AI Task Orchestrator base classes and patterns
- analysis: Statistical analysis and reporting
- integration: External service integrations
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"

# Core module imports
from .analysis import PerformanceAnalyzer, ReportGenerator, StatisticalAnalyzer
from .core import BaseOrchestrator, ConfigurationManager, DatabaseManager, LoggingManager
from .data import DataLoader, DataPreprocessor, DataValidator
from .integration import (
    GitHubAPIClient,
    OpenAIClient,
    ServiceContext,
    ServiceManager,
    ServiceStatus,
    ServiceType,
    WolframAlphaProClient,
    create_service_manager_with_defaults,
)
from .metrics import MetricCalculator, MetricType, PerformanceClassifier, PerformanceRanges

__all__ = [
    # Core
    'BaseOrchestrator',
    'DatabaseManager',
    'ConfigurationManager',
    'LoggingManager',

    # Metrics
    'MetricCalculator',
    'PerformanceClassifier',
    'MetricType',
    'PerformanceRanges',

    # Data
    'DataLoader',
    'DataValidator',
    'DataPreprocessor',

    # Analysis
    'StatisticalAnalyzer',
    'ReportGenerator',
    'PerformanceAnalyzer',

    # Integration
    'ServiceManager',
    'WolframAlphaProClient',
    'OpenAIClient',
    'GitHubAPIClient',
    'ServiceType',
    'ServiceStatus',
    'create_service_manager_with_defaults',
    'ServiceContext'
]
