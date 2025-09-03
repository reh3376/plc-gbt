"""
Core Components for Enhanced PLC Format Converter
================================================

This module contains the core converter logic and data models for Phase 3.9
enhanced data preservation capabilities.
"""

from .converter import EnhancedPLCConverter
from .models import (
    BinaryDataBlock,
    ComponentExtraction,
    ConversionResult,
    ConversionStatus,
    DataIntegrityScore,
    # Enhanced models for Phase 3.9
    EnhancedPLCComponent,
    PLCController,
    PLCDevice,
    PLCProgram,
    PLCProject,
    PLCRoutine,
    PLCTag,
)

__all__ = [
    "EnhancedPLCConverter",
    "PLCProject",
    "PLCController",
    "PLCProgram",
    "PLCRoutine",
    "PLCTag",
    "PLCDevice",
    "ConversionResult",
    "ConversionStatus",
    "DataIntegrityScore",
    "EnhancedPLCComponent",
    "BinaryDataBlock",
    "ComponentExtraction"
]
