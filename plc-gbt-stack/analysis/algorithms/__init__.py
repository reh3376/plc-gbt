#!/usr/bin/env python3
"""
Phase 22.1.3: Algorithm Registry System
======================================

Comprehensive algorithm registry for control loop analysis including:
- Step detection algorithms
- FOPDT/SOPDT model identification
- IMC tuning calculations
- Adaptive tuning algorithms
- Model validation and quality assessment

This module provides a plugin-based architecture for algorithm management
with dynamic registration, validation, and execution capabilities.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

from typing import Dict, List, Any, Optional, Type, Callable, Union, Tuple
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
import logging
import time
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)

class AlgorithmCategory(Enum):
    """Categories of control loop analysis algorithms"""
    STEP_DETECTION = "step_detection"
    MODEL_IDENTIFICATION = "model_identification"
    TUNING_CALCULATION = "tuning_calculation"
    ADAPTIVE_CONTROL = "adaptive_control"
    SIGNAL_PROCESSING = "signal_processing"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    VALIDATION = "validation"

class AlgorithmComplexity(Enum):
    """Algorithm computational complexity levels"""
    LOW = "low"          # <1s execution
    MEDIUM = "medium"    # 1-10s execution
    HIGH = "high"        # 10-60s execution
    VERY_HIGH = "very_high"  # >60s execution

@dataclass
class AlgorithmMetadata:
    """Metadata for algorithm registration"""
    name: str
    category: AlgorithmCategory
    complexity: AlgorithmComplexity
    description: str
    version: str = "1.0.0"
    author: str = "PLC-GPT Team"
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    min_data_points: int = 10
    max_data_points: Optional[int] = None
    supports_realtime: bool = False
    citation: Optional[str] = None

class AlgorithmBase(ABC):
    """Base class for all control loop analysis algorithms"""
    
    def __init__(self, metadata: AlgorithmMetadata):
        self.metadata = metadata
        self._validated = False
        self._performance_stats = {}
    
    @abstractmethod
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute the algorithm with input data"""
        pass
    
    @abstractmethod
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data format and requirements"""
        pass
    
    def get_metadata(self) -> AlgorithmMetadata:
        """Get algorithm metadata"""
        return self.metadata
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get algorithm performance statistics"""
        return self._performance_stats.copy()

class AlgorithmRegistry:
    """Central registry for all control loop analysis algorithms"""
    
    def __init__(self):
        self._algorithms: Dict[str, Type[AlgorithmBase]] = {}
        self._instances: Dict[str, AlgorithmBase] = {}
        self._categories: Dict[AlgorithmCategory, List[str]] = {
            category: [] for category in AlgorithmCategory
        }
        logger.info("Algorithm registry initialized")
    
    def register(self, algorithm_class: Type[AlgorithmBase]) -> bool:
        """Register an algorithm class"""
        try:
            # Create temporary instance to get metadata
            temp_instance = algorithm_class()
            metadata = temp_instance.get_metadata()
            
            # Validate metadata
            if not metadata.name:
                logger.error(f"Algorithm {algorithm_class.__name__} missing name")
                return False
            
            # Register algorithm
            self._algorithms[metadata.name] = algorithm_class
            self._categories[metadata.category].append(metadata.name)
            
            logger.info(f"Registered algorithm: {metadata.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register algorithm {algorithm_class.__name__}: {e}")
            return False
    
    def get_algorithm(self, name: str) -> Optional[AlgorithmBase]:
        """Get algorithm instance by name"""
        if name not in self._algorithms:
            logger.warning(f"Algorithm '{name}' not found")
            return None
        
        if name not in self._instances:
            self._instances[name] = self._algorithms[name]()
        
        return self._instances[name]
    
    def list_algorithms(self, category: Optional[AlgorithmCategory] = None) -> List[str]:
        """List available algorithms, optionally filtered by category"""
        if category:
            return self._categories.get(category, [])
        return list(self._algorithms.keys())
    
    def get_algorithms_by_category(self) -> Dict[AlgorithmCategory, List[str]]:
        """Get algorithms grouped by category"""
        return self._categories.copy()
    
    def execute_algorithm(self, name: str, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute algorithm by name with input validation"""
        algorithm = self.get_algorithm(name)
        if not algorithm:
            raise ValueError(f"Algorithm '{name}' not found")
        
        # Validate input
        is_valid, errors = algorithm.validate_input(data)
        if not is_valid:
            raise ValueError(f"Input validation failed: {errors}")
        
        # Execute algorithm
        start_time = time.time()
        result = algorithm.execute(data, **kwargs)
        execution_time = time.time() - start_time
        
        # Update performance stats
        algorithm._performance_stats.update({
            'last_execution_time': execution_time,
            'total_executions': algorithm._performance_stats.get('total_executions', 0) + 1,
            'average_execution_time': (
                algorithm._performance_stats.get('average_execution_time', 0) * 
                algorithm._performance_stats.get('total_executions', 0) + execution_time
            ) / (algorithm._performance_stats.get('total_executions', 0) + 1)
        })
        
        # Add metadata to result
        result['_metadata'] = {
            'algorithm_name': name,
            'execution_time': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        return result

# Global registry instance
registry = AlgorithmRegistry()

# Export main components
__all__ = [
    'AlgorithmCategory',
    'AlgorithmComplexity', 
    'AlgorithmMetadata',
    'AlgorithmBase',
    'AlgorithmRegistry',
    'registry'
] 