#!/usr/bin/env python3
"""
Phase 22.1.5: Validation Framework
==================================

Comprehensive validation framework for the Enhanced Control Loop Analysis Engine
providing statistical testing, confidence scoring, and WolframAlpha Pro integration
for mathematical verification and industrial control validation.

This module provides enterprise-grade validation capabilities including:
- Statistical testing for analysis results validation
- Multi-dimensional confidence scoring systems
- WolframAlpha Pro mathematical verification
- Industrial control domain-specific validation
- Integration with all Phase 22.1 components

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
from enum import Enum
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Version information
__version__ = "1.0.0"

# Validation configuration
VALIDATION_CONFIG = {
    "statistical_significance": 0.05,
    "confidence_threshold": 0.8,
    "wolfram_timeout": 30,
    "max_validation_attempts": 3,
    "enable_mathematical_verification": True
}

class ValidationLevel(Enum):
    """Validation complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"

class ValidationStatus(Enum):
    """Validation result status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"
    PENDING = "pending"

class ConfidenceLevel(Enum):
    """Confidence assessment levels"""
    VERY_LOW = "very_low"      # < 0.3
    LOW = "low"                # 0.3 - 0.5
    MEDIUM = "medium"          # 0.5 - 0.7
    HIGH = "high"              # 0.7 - 0.9
    VERY_HIGH = "very_high"    # 0.9 - 0.95
    ABSOLUTE = "absolute"      # > 0.95

# Import main components
from .statistical_tests import (
    StatisticalTestSuite,
    StatisticalTestResult,
    TestType,
    run_statistical_validation
)

from .confidence_scoring import (
    ConfidenceScorer,
    ConfidenceScore,
    ConfidenceDimension,
    calculate_overall_confidence
)

from .wolfram_integration import (
    WolframValidator,
    WolframValidationResult,
    MathematicalValidation,
    verify_mathematical_accuracy
)

from .validation_manager import (
    ValidationManager,
    ValidationResult,
    ValidationReport,
    get_validation_manager
)

# Export main components
__all__ = [
    # Core validation classes
    'ValidationManager',
    'StatisticalTestSuite', 
    'ConfidenceScorer',
    'WolframValidator',
    
    # Data classes
    'ValidationResult',
    'ValidationReport',
    'StatisticalTestResult',
    'ConfidenceScore',
    'WolframValidationResult',
    'MathematicalValidation',
    
    # Enums
    'ValidationLevel',
    'ValidationStatus',
    'ConfidenceLevel',
    'TestType',
    'ConfidenceDimension',
    
    # Utility functions
    'run_statistical_validation',
    'calculate_overall_confidence',
    'verify_mathematical_accuracy',
    'get_validation_manager',
    
    # Configuration
    'VALIDATION_CONFIG'
] 