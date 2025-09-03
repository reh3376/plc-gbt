#!/usr/bin/env python3
"""
Phase 22.1.3: Algorithm Registry Manager
=======================================

Comprehensive management system for control loop analysis algorithms providing:
- Algorithm discovery and registration
- Input validation and preprocessing
- Algorithm execution and result validation
- Performance monitoring and caching
- Plugin management and extensibility

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from . import AlgorithmCategory, AlgorithmComplexity, registry

logger = logging.getLogger(__name__)

@dataclass
class ExecutionResult:
    """Result of algorithm execution"""
    algorithm_name: str
    success: bool
    result: Optional[Dict[str, Any]]
    execution_time: float
    error_message: Optional[str]
    validation_errors: List[str]
    performance_stats: Dict[str, Any]
    timestamp: str

class AlgorithmRegistryManager:
    """
    Enhanced algorithm registry manager with comprehensive capabilities
    """

    def __init__(self, cache_enabled: bool = True, performance_monitoring: bool = True):
        self.cache_enabled = cache_enabled
        self.performance_monitoring = performance_monitoring
        self._execution_cache = {}
        self._performance_stats = {}
        self._algorithm_workflows = {}

        # Initialize logging
        self.logger = logging.getLogger(__name__ + '.RegistryManager')

        # Load any additional plugins
        self._load_plugins()

        self.logger.info(f"Algorithm Registry Manager initialized with {len(registry.list_algorithms())} algorithms")

    def discover_algorithms(self, category: Optional[AlgorithmCategory] = None,
                          complexity: Optional[AlgorithmComplexity] = None,
                          supports_realtime: Optional[bool] = None) -> List[str]:
        """Discover algorithms based on criteria"""
        algorithms = registry.list_algorithms(category)

        if complexity or supports_realtime is not None:
            filtered_algorithms = []
            for alg_name in algorithms:
                algorithm = registry.get_algorithm(alg_name)
                if algorithm:
                    metadata = algorithm.get_metadata()

                    if complexity and metadata.complexity != complexity:
                        continue

                    if supports_realtime is not None and metadata.supports_realtime != supports_realtime:
                        continue

                    filtered_algorithms.append(alg_name)

            algorithms = filtered_algorithms

        return algorithms

    def get_algorithm_info(self, algorithm_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about an algorithm"""
        algorithm = registry.get_algorithm(algorithm_name)
        if not algorithm:
            return None

        metadata = algorithm.get_metadata()
        performance_stats = algorithm.get_performance_stats()

        return {
            'name': metadata.name,
            'category': metadata.category.value,
            'complexity': metadata.complexity.value,
            'description': metadata.description,
            'version': metadata.version,
            'author': metadata.author,
            'dependencies': metadata.dependencies,
            'tags': metadata.tags,
            'min_data_points': metadata.min_data_points,
            'max_data_points': metadata.max_data_points,
            'supports_realtime': metadata.supports_realtime,
            'citation': metadata.citation,
            'performance_stats': performance_stats,
            'last_updated': datetime.now().isoformat()
        }

    def validate_algorithm_input(self, algorithm_name: str,
                                data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for a specific algorithm"""
        algorithm = registry.get_algorithm(algorithm_name)
        if not algorithm:
            return False, [f"Algorithm '{algorithm_name}' not found"]

        return algorithm.validate_input(data)

    def execute_algorithm(self, algorithm_name: str, data: Dict[str, Any],
                         **kwargs) -> ExecutionResult:
        """Execute algorithm with comprehensive error handling and monitoring"""
        start_time = time.time()
        timestamp = datetime.now().isoformat()

        try:
            # Check cache first
            if self.cache_enabled:
                cache_key = self._generate_cache_key(algorithm_name, data, kwargs)
                if cache_key in self._execution_cache:
                    cached_result = self._execution_cache[cache_key]
                    self.logger.info(f"Cache hit for {algorithm_name}")
                    return ExecutionResult(
                        algorithm_name=algorithm_name,
                        success=True,
                        result=cached_result['result'],
                        execution_time=cached_result['execution_time'],
                        error_message=None,
                        validation_errors=[],
                        performance_stats=cached_result['performance_stats'],
                        timestamp=cached_result['timestamp']
                    )

            # Get algorithm
            algorithm = registry.get_algorithm(algorithm_name)
            if not algorithm:
                raise ValueError(f"Algorithm '{algorithm_name}' not found")

            # Validate input
            is_valid, validation_errors = algorithm.validate_input(data)
            if not is_valid:
                return ExecutionResult(
                    algorithm_name=algorithm_name,
                    success=False,
                    result=None,
                    execution_time=time.time() - start_time,
                    error_message="Input validation failed",
                    validation_errors=validation_errors,
                    performance_stats={},
                    timestamp=timestamp
                )

            # Execute algorithm
            result = registry.execute_algorithm(algorithm_name, data, **kwargs)
            execution_time = time.time() - start_time

            # Get performance stats
            performance_stats = algorithm.get_performance_stats()

            # Cache result
            if self.cache_enabled:
                self._execution_cache[cache_key] = {
                    'result': result,
                    'execution_time': execution_time,
                    'performance_stats': performance_stats,
                    'timestamp': timestamp
                }

            # Update global performance monitoring
            if self.performance_monitoring:
                self._update_performance_stats(algorithm_name, execution_time, True)

            return ExecutionResult(
                algorithm_name=algorithm_name,
                success=True,
                result=result,
                execution_time=execution_time,
                error_message=None,
                validation_errors=[],
                performance_stats=performance_stats,
                timestamp=timestamp
            )

        except Exception as e:
            execution_time = time.time() - start_time
            error_message = str(e)

            # Update performance monitoring for failures
            if self.performance_monitoring:
                self._update_performance_stats(algorithm_name, execution_time, False)

            self.logger.error(f"Algorithm execution failed: {algorithm_name} - {error_message}")

            return ExecutionResult(
                algorithm_name=algorithm_name,
                success=False,
                result=None,
                execution_time=execution_time,
                error_message=error_message,
                validation_errors=[],
                performance_stats={},
                timestamp=timestamp
            )

    def execute_workflow(self, workflow_name: str, data: Dict[str, Any],
                        **kwargs) -> Dict[str, ExecutionResult]:
        """Execute a predefined workflow of algorithms"""
        if workflow_name not in self._algorithm_workflows:
            raise ValueError(f"Workflow '{workflow_name}' not found")

        workflow = self._algorithm_workflows[workflow_name]
        results = {}

        # Execute workflow steps
        current_data = data.copy()

        for step in workflow['steps']:
            algorithm_name = step['algorithm']
            step_kwargs = step.get('kwargs', {})
            step_kwargs.update(kwargs)

            # Execute algorithm
            result = self.execute_algorithm(algorithm_name, current_data, **step_kwargs)
            results[algorithm_name] = result

            # Check if we should continue
            if not result.success and step.get('required', True):
                self.logger.error(f"Required step {algorithm_name} failed, stopping workflow")
                break

            # Update data for next step if needed
            if result.success and step.get('pass_results', False):
                current_data.update(result.result)

        return results

    def register_workflow(self, workflow_name: str, workflow_definition: Dict[str, Any]):
        """Register a new algorithm workflow"""
        required_fields = ['description', 'steps']
        for field in required_fields:
            if field not in workflow_definition:
                raise ValueError(f"Workflow definition missing required field: {field}")

        # Validate workflow steps
        for i, step in enumerate(workflow_definition['steps']):
            if 'algorithm' not in step:
                raise ValueError(f"Step {i} missing 'algorithm' field")

            if step['algorithm'] not in registry.list_algorithms():
                raise ValueError(f"Step {i} references unknown algorithm: {step['algorithm']}")

        self._algorithm_workflows[workflow_name] = workflow_definition
        self.logger.info(f"Registered workflow: {workflow_name}")

    def get_workflow_info(self, workflow_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a registered workflow"""
        if workflow_name not in self._algorithm_workflows:
            return None

        workflow = self._algorithm_workflows[workflow_name]

        # Add algorithm details for each step
        detailed_steps = []
        for step in workflow['steps']:
            algorithm_info = self.get_algorithm_info(step['algorithm'])
            detailed_steps.append({
                'algorithm': step['algorithm'],
                'algorithm_info': algorithm_info,
                'kwargs': step.get('kwargs', {}),
                'required': step.get('required', True),
                'pass_results': step.get('pass_results', False)
            })

        return {
            'name': workflow_name,
            'description': workflow['description'],
            'steps': detailed_steps,
            'total_steps': len(detailed_steps)
        }

    def list_workflows(self) -> List[str]:
        """List all registered workflows"""
        return list(self._algorithm_workflows.keys())

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all algorithms"""
        summary = {
            'total_algorithms': len(registry.list_algorithms()),
            'total_executions': sum(stats.get('total_executions', 0)
                                  for stats in self._performance_stats.values()),
            'cache_enabled': self.cache_enabled,
            'cache_size': len(self._execution_cache),
            'algorithms': {}
        }

        for alg_name in registry.list_algorithms():
            alg_stats = self._performance_stats.get(alg_name, {})
            algorithm = registry.get_algorithm(alg_name)

            if algorithm:
                perf_stats = algorithm.get_performance_stats()
                summary['algorithms'][alg_name] = {
                    'executions': alg_stats.get('total_executions', 0),
                    'success_rate': alg_stats.get('success_rate', 0.0),
                    'average_execution_time': alg_stats.get('average_execution_time', 0.0),
                    'last_execution': alg_stats.get('last_execution'),
                    'algorithm_stats': perf_stats
                }

        return summary

    def clear_cache(self):
        """Clear execution cache"""
        self._execution_cache.clear()
        self.logger.info("Execution cache cleared")

    def export_results(self, results: List[ExecutionResult],
                      format: str = 'json') -> str:
        """Export execution results to various formats"""
        if format == 'json':
            return json.dumps([asdict(result) for result in results],
                            indent=2, default=str)
        elif format == 'csv':
            # Convert to DataFrame and export
            data = []
            for result in results:
                row = {
                    'algorithm_name': result.algorithm_name,
                    'success': result.success,
                    'execution_time': result.execution_time,
                    'error_message': result.error_message,
                    'timestamp': result.timestamp
                }

                # Add key results if available
                if result.result:
                    for key, value in result.result.items():
                        if isinstance(value, (int, float, str, bool)):
                            row[f'result_{key}'] = value

                data.append(row)

            df = pd.DataFrame(data)
            return df.to_csv(index=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def _generate_cache_key(self, algorithm_name: str, data: Dict[str, Any],
                           kwargs: Dict[str, Any]) -> str:
        """Generate cache key for algorithm execution"""
        # Create deterministic hash of inputs
        cache_data = {
            'algorithm': algorithm_name,
            'data': data,
            'kwargs': kwargs
        }

        # Convert to JSON string for hashing
        cache_str = json.dumps(cache_data, sort_keys=True, default=str)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _update_performance_stats(self, algorithm_name: str,
                                 execution_time: float, success: bool):
        """Update performance statistics for an algorithm"""
        if algorithm_name not in self._performance_stats:
            self._performance_stats[algorithm_name] = {
                'total_executions': 0,
                'successful_executions': 0,
                'total_execution_time': 0.0,
                'last_execution': None
            }

        stats = self._performance_stats[algorithm_name]
        stats['total_executions'] += 1
        if success:
            stats['successful_executions'] += 1
        stats['total_execution_time'] += execution_time
        stats['last_execution'] = datetime.now().isoformat()

        # Calculate derived metrics
        stats['success_rate'] = stats['successful_executions'] / stats['total_executions']
        stats['average_execution_time'] = stats['total_execution_time'] / stats['total_executions']

    def _load_plugins(self):
        """Load additional algorithm plugins"""
        # Register built-in algorithms (already done in individual modules)

        # Register common workflows
        self._register_builtin_workflows()

    def _register_builtin_workflows(self):
        """Register built-in algorithm workflows"""

        # Complete step response analysis workflow
        step_analysis_workflow = {
            'description': 'Complete step response analysis from step detection to PID tuning',
            'steps': [
                {
                    'algorithm': 'natural_step_detector',
                    'kwargs': {'confidence_threshold': 0.7},
                    'required': True,
                    'pass_results': True
                },
                {
                    'algorithm': 'fopdt_identifier',
                    'kwargs': {'method': 'optimization'},
                    'required': True,
                    'pass_results': True
                },
                {
                    'algorithm': 'imc_tuner',
                    'kwargs': {'controller_type': 'dependent'},
                    'required': False,
                    'pass_results': False
                }
            ]
        }

        self.register_workflow('complete_step_analysis', step_analysis_workflow)

        # Model comparison workflow
        model_comparison_workflow = {
            'description': 'Compare FOPDT and SOPDT model identification',
            'steps': [
                {
                    'algorithm': 'fopdt_identifier',
                    'kwargs': {'method': 'optimization'},
                    'required': False,
                    'pass_results': False
                },
                {
                    'algorithm': 'sopdt_identifier',
                    'kwargs': {},
                    'required': False,
                    'pass_results': False
                }
            ]
        }

        self.register_workflow('model_comparison', model_comparison_workflow)

        # Adaptive tuning workflow
        adaptive_workflow = {
            'description': 'Real-time adaptive PID tuning',
            'steps': [
                {
                    'algorithm': 'adaptive_tuner',
                    'kwargs': {'adaptation_rate': 0.01},
                    'required': True,
                    'pass_results': False
                }
            ]
        }

        self.register_workflow('adaptive_tuning', adaptive_workflow)

# Create global registry manager instance
registry_manager = AlgorithmRegistryManager()

# Export main components
__all__ = [
    'AlgorithmRegistryManager',
    'ExecutionResult',
    'registry_manager'
]
