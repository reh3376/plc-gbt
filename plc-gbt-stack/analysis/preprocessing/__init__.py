#!/usr/bin/env python3
"""
Enhanced Control Loop Data Preprocessing Package
===============================================

Phase 22.1.2: Enhanced Data Preprocessing

Advanced preprocessing capabilities for industrial control loop data analysis:
- Specialized industrial data collectors for multiple sources
- Advanced validation and quality assessment
- Control-specific preprocessing algorithms
- Real-time data stream processing
- Integration with existing data pipeline framework

Components:
- collectors: Unified data collection from CSV, PLC, databases, real-time streams
- validators: Advanced validation for industrial control data quality
- processors: Specialized preprocessing algorithms for control systems
- quality: Data quality assessment and improvement tools
- streams: Real-time data streaming and synchronization

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.2 - Enhanced Data Preprocessing
Dependencies: Phase 22.1.1 (Core Framework), existing DataLoader modules
"""

from .collectors import (
    CollectionResult,
    CollectionStrategy,
    DatabaseCollector,
    DataSource,
    PLCDataCollector,
    StreamCollector,
    UnifiedDataCollector,
)
from .processors import (
    ControlDataProcessor,
    ProcessingStrategy,
    SignalProcessor,
    TimeSeriesProcessor,
)
from .processors import ProcessingOptions as AdvancedProcessingOptions
from .quality import (
    DataQualityAssessor,
    QualityImprover,
    QualityMetrics,
    QualityReport,
    QualityThresholds,
)
from .streams import (
    DataBuffer,
    RealTimeProcessor,
    StreamingOptions,
    StreamSynchronizer,
    SynchronizationStrategy,
)
from .validators import (
    ControlLoopValidator,
    IndustrialDataValidator,
    RealTimeValidator,
    ValidationRule,
    ValidationSeverity,
)
from .validators import ValidationResult as PreprocessingValidationResult

__all__ = [
    # Collectors
    'UnifiedDataCollector',
    'PLCDataCollector',
    'DatabaseCollector',
    'StreamCollector',
    'CollectionStrategy',
    'DataSource',
    'CollectionResult',

    # Validators
    'IndustrialDataValidator',
    'ControlLoopValidator',
    'RealTimeValidator',
    'ValidationSeverity',
    'PreprocessingValidationResult',
    'ValidationRule',

    # Processors
    'ControlDataProcessor',
    'SignalProcessor',
    'TimeSeriesProcessor',
    'ProcessingStrategy',
    'AdvancedProcessingOptions',

    # Quality
    'DataQualityAssessor',
    'QualityImprover',
    'QualityMetrics',
    'QualityThresholds',
    'QualityReport',

    # Streams
    'RealTimeProcessor',
    'StreamSynchronizer',
    'DataBuffer',
    'StreamingOptions',
    'SynchronizationStrategy'
]

__version__ = "1.0.0"
__phase__ = "22.1.2"
