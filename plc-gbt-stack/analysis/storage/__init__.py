#!/usr/bin/env python3
"""
Phase 22.1.4: Analysis Storage Engine
====================================

Comprehensive storage system for control loop analysis results including:
- PostgreSQL schema management for analysis results
- Historical tracking and trend analysis
- Result caching and optimization
- Query interface and data retrieval
- Storage performance monitoring

This module provides enterprise-grade storage capabilities for the Enhanced
Control Loop Analysis Engine with full integration to existing infrastructure.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"

# Storage configuration
STORAGE_CONFIG = {
    "default_database": "postgresql",
    "cache_enabled": True,
    "historical_retention_days": 365,
    "batch_size": 1000,
    "connection_pool_size": 10
}

# Import main components
from .database_schema import (
    DatabaseSchemaManager,
    AnalysisResultSchema,
    StorageMetrics,
    AnalysisType,
    StorageStatus
)

from .result_storage import (
    AnalysisResultStorage,
    StorageResult,
    QueryBuilder,
    QueryFilter
)

from .historical_tracker import (
    HistoricalTracker,
    TrendAnalysis,
    PerformanceMetrics,
    TrendDirection
)

from .storage_manager import (
    StorageManager,
    get_storage_manager,
    initialize_storage
)

# Export main components
__all__ = [
    # Core storage classes
    'StorageManager',
    'AnalysisResultStorage',
    'HistoricalTracker',
    'DatabaseSchemaManager',
    
    # Data classes
    'StorageResult',
    'AnalysisResultSchema',
    'TrendAnalysis',
    'PerformanceMetrics',
    'StorageMetrics',
    
    # Enums
    'AnalysisType',
    'StorageStatus',
    'TrendDirection',
    
    # Utilities
    'QueryBuilder',
    'QueryFilter',
    
    # Factory functions
    'get_storage_manager',
    'initialize_storage',
    
    # Configuration
    'STORAGE_CONFIG'
] 