#!/usr/bin/env python3
"""
Phase 22.1.3: Algorithm Registry Validation Tests
================================================

Comprehensive validation and testing framework for the algorithm registry
to ensure all components function correctly and meet specifications.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

from . import registry
from .registry_manager import registry_manager

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of algorithm validation test"""
    test_name: str
    algorithm_name: str
    success: bool
    execution_time: float
    error_message: Optional[str] = None
    details: Dict[str, Any] = None

class AlgorithmRegistryValidator:
    """
    Comprehensive validation framework for algorithm registry
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.Validator')
        self.test_data = self._generate_test_data()

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        start_time = time.time()

        results = {
            'summary': {},
            'algorithm_tests': {},
            'workflow_tests': {},
            'performance_tests': {},
            'integration_tests': {}
        }

        try:
            # Test individual algorithms
            self.logger.info("Testing individual algorithms...")
            results['algorithm_tests'] = self._test_all_algorithms()

            # Test workflows
            self.logger.info("Testing workflows...")
            results['workflow_tests'] = self._test_workflows()

            # Performance tests
            self.logger.info("Running performance tests...")
            results['performance_tests'] = self._test_performance()

            # Integration tests
            self.logger.info("Running integration tests...")
            results['integration_tests'] = self._test_integration()

            # Generate summary
            results['summary'] = self._generate_summary(results)
            results['summary']['total_validation_time'] = time.time() - start_time

        except Exception as e:
            self.logger.error(f"Validation failed: {e}")
            results['summary'] = {
                'success': False,
                'error': str(e),
                'total_validation_time': time.time() - start_time
            }

        return results

    def _test_all_algorithms(self) -> Dict[str, ValidationResult]:
        """Test all registered algorithms"""
        results = {}

        for algorithm_name in registry.list_algorithms():
            self.logger.info(f"Testing algorithm: {algorithm_name}")
            result = self._test_single_algorithm(algorithm_name)
            results[algorithm_name] = result

        return results

    def _test_single_algorithm(self, algorithm_name: str) -> ValidationResult:
        """Test a single algorithm with appropriate test data"""
        start_time = time.time()

        try:
            # Get algorithm info
            algorithm_info = registry_manager.get_algorithm_info(algorithm_name)
            if not algorithm_info:
                return ValidationResult(
                    test_name="algorithm_execution",
                    algorithm_name=algorithm_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message="Algorithm not found"
                )

            # Select appropriate test data
            test_data = self._select_test_data(algorithm_info['category'])

            # Validate input
            is_valid, validation_errors = registry_manager.validate_algorithm_input(
                algorithm_name, test_data
            )

            if not is_valid:
                return ValidationResult(
                    test_name="algorithm_execution",
                    algorithm_name=algorithm_name,
                    success=False,
                    execution_time=time.time() - start_time,
                    error_message=f"Input validation failed: {validation_errors}"
                )

            # Execute algorithm
            execution_result = registry_manager.execute_algorithm(algorithm_name, test_data)

            # Validate output
            output_valid = self._validate_algorithm_output(algorithm_name, execution_result.result)

            return ValidationResult(
                test_name="algorithm_execution",
                algorithm_name=algorithm_name,
                success=execution_result.success and output_valid,
                execution_time=time.time() - start_time,
                error_message=execution_result.error_message if not execution_result.success else None,
                details={
                    'input_validation': is_valid,
                    'output_validation': output_valid,
                    'execution_time': execution_result.execution_time,
                    'algorithm_info': algorithm_info
                }
            )

        except Exception as e:
            return ValidationResult(
                test_name="algorithm_execution",
                algorithm_name=algorithm_name,
                success=False,
                execution_time=time.time() - start_time,
                error_message=str(e)
            )

    def _test_workflows(self) -> Dict[str, Any]:
        """Test all registered workflows"""
        results = {}

        for workflow_name in registry_manager.list_workflows():
            self.logger.info(f"Testing workflow: {workflow_name}")

            try:
                # Get workflow info
                workflow_info = registry_manager.get_workflow_info(workflow_name)

                # Select test data for first algorithm in workflow
                first_algorithm = workflow_info['steps'][0]['algorithm']
                first_alg_info = registry_manager.get_algorithm_info(first_algorithm)
                test_data = self._select_test_data(first_alg_info['category'])

                # Execute workflow
                start_time = time.time()
                workflow_results = registry_manager.execute_workflow(workflow_name, test_data)
                execution_time = time.time() - start_time

                # Analyze results
                success = all(result.success for result in workflow_results.values())

                results[workflow_name] = {
                    'success': success,
                    'execution_time': execution_time,
                    'step_results': {name: result.success for name, result in workflow_results.items()},
                    'workflow_info': workflow_info
                }

            except Exception as e:
                results[workflow_name] = {
                    'success': False,
                    'error': str(e)
                }

        return results

    def _test_performance(self) -> Dict[str, Any]:
        """Test performance characteristics"""
        results = {
            'execution_times': {},
            'memory_usage': {},
            'cache_performance': {}
        }

        # Test execution times for different data sizes
        for algorithm_name in registry.list_algorithms():
            algorithm_info = registry_manager.get_algorithm_info(algorithm_name)
            category = algorithm_info['category']

            times = []
            data_sizes = [50, 100, 500, 1000]

            for size in data_sizes:
                if size >= algorithm_info['min_data_points']:
                    test_data = self._generate_test_data_size(category, size)

                    start_time = time.time()
                    result = registry_manager.execute_algorithm(algorithm_name, test_data)
                    execution_time = time.time() - start_time

                    if result.success:
                        times.append({'size': size, 'time': execution_time})

            results['execution_times'][algorithm_name] = times

        # Test cache performance
        test_algorithm = 'natural_step_detector'
        test_data = self._select_test_data('step_detection')

        # First execution (no cache)
        start_time = time.time()
        registry_manager.execute_algorithm(test_algorithm, test_data)
        first_time = time.time() - start_time

        # Second execution (cached)
        start_time = time.time()
        registry_manager.execute_algorithm(test_algorithm, test_data)
        cached_time = time.time() - start_time

        results['cache_performance'] = {
            'first_execution_time': first_time,
            'cached_execution_time': cached_time,
            'speedup_factor': first_time / (cached_time + 1e-10)
        }

        return results

    def _test_integration(self) -> Dict[str, Any]:
        """Test integration between components"""
        results = {}

        # Test step detection -> model identification -> tuning workflow
        try:
            # Generate step response data
            time_data, input_data, output_data = self._generate_step_response_data()

            # Step 1: Step detection
            step_data = {
                'time': time_data,
                'values': output_data
            }

            step_result = registry_manager.execute_algorithm('natural_step_detector', step_data)

            # Step 2: Model identification (if steps found)
            if step_result.success and step_result.result['step_times']:
                model_data = {
                    'time': time_data,
                    'input': input_data,
                    'output': output_data
                }

                model_result = registry_manager.execute_algorithm('fopdt_identifier', model_data)

                # Step 3: Tuning (if model identified)
                if model_result.success:
                    tuning_data = {
                        'model_parameters': model_result.result['parameters'],
                        'controller_type': 'dependent'
                    }

                    tuning_result = registry_manager.execute_algorithm('imc_tuner', tuning_data)

                    results['complete_workflow'] = {
                        'success': tuning_result.success,
                        'step_detection': step_result.success,
                        'model_identification': model_result.success,
                        'tuning': tuning_result.success,
                        'final_parameters': tuning_result.result if tuning_result.success else None
                    }
                else:
                    results['complete_workflow'] = {
                        'success': False,
                        'error': 'Model identification failed'
                    }
            else:
                results['complete_workflow'] = {
                    'success': False,
                    'error': 'Step detection failed'
                }

        except Exception as e:
            results['complete_workflow'] = {
                'success': False,
                'error': str(e)
            }

        return results

    def _generate_test_data(self) -> Dict[str, Any]:
        """Generate comprehensive test data for all algorithm types"""
        time_data, input_data, output_data = self._generate_step_response_data()

        return {
            'step_detection': {
                'time': time_data,
                'values': output_data
            },
            'model_identification': {
                'time': time_data,
                'input': input_data,
                'output': output_data
            },
            'tuning_calculation': {
                'model_parameters': {
                    'K': 2.5,
                    'tau': 5.0,
                    'theta': 1.0
                },
                'controller_type': 'dependent'
            },
            'adaptive_control': {
                'time': time_data,
                'setpoint': np.ones_like(time_data),
                'process_output': output_data,
                'control_output': input_data
            }
        }

    def _generate_step_response_data(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate synthetic step response data for testing"""
        # Time vector
        dt = 0.1
        time_data = np.arange(0, 50, dt)

        # Input step
        input_data = np.zeros_like(time_data)
        step_time = 10.0
        input_data[time_data >= step_time] = 1.0

        # FOPDT response
        K = 2.5
        tau = 5.0
        theta = 1.0

        output_data = np.zeros_like(time_data)
        for i, t in enumerate(time_data):
            if t > step_time + theta:
                t_effective = t - step_time - theta
                output_data[i] = K * (1 - np.exp(-t_effective / tau))

        # Add noise
        noise_level = 0.05
        output_data += np.random.normal(0, noise_level, len(output_data))

        return time_data, input_data, output_data

    def _select_test_data(self, category: str) -> Dict[str, Any]:
        """Select appropriate test data for algorithm category"""
        if category == 'step_detection':
            return self.test_data['step_detection']
        elif category == 'model_identification':
            return self.test_data['model_identification']
        elif category == 'tuning_calculation':
            return self.test_data['tuning_calculation']
        elif category == 'adaptive_control':
            return self.test_data['adaptive_control']
        else:
            return self.test_data['step_detection']  # fallback

    def _generate_test_data_size(self, category: str, size: int) -> Dict[str, Any]:
        """Generate test data of specific size"""
        base_data = self._select_test_data(category)

        if 'time' in base_data:
            # Resample to desired size
            original_size = len(base_data['time'])
            indices = np.linspace(0, original_size-1, size, dtype=int)

            resized_data = {}
            for key, value in base_data.items():
                if isinstance(value, np.ndarray) and len(value) == original_size:
                    resized_data[key] = value[indices]
                else:
                    resized_data[key] = value

            return resized_data
        else:
            return base_data

    def _validate_algorithm_output(self, algorithm_name: str,
                                  result: Optional[Dict[str, Any]]) -> bool:
        """Validate algorithm output structure and content"""
        if result is None:
            return False

        try:
            algorithm_info = registry_manager.get_algorithm_info(algorithm_name)
            category = algorithm_info['category']

            if category == 'step_detection':
                required_fields = ['step_times', 'step_magnitudes', 'step_confidence']
                return all(field in result for field in required_fields)

            elif category == 'model_identification':
                required_fields = ['model_type', 'parameters', 'fit_quality']
                return all(field in result for field in required_fields)

            elif category == 'tuning_calculation':
                required_fields = ['tuning_method', 'parameters', 'performance_metrics']
                return all(field in result for field in required_fields)

            elif category == 'adaptive_control':
                required_fields = ['tuning_method', 'parameters']
                return all(field in result for field in required_fields)

            else:
                return True  # Unknown category, assume valid

        except Exception as e:
            self.logger.error(f"Output validation error: {e}")
            return False

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation summary"""
        summary = {
            'success': True,
            'total_algorithms': len(results['algorithm_tests']),
            'successful_algorithms': 0,
            'failed_algorithms': 0,
            'total_workflows': len(results['workflow_tests']),
            'successful_workflows': 0,
            'failed_workflows': 0,
            'performance_metrics': {},
            'recommendations': []
        }

        # Algorithm summary
        for _alg_name, result in results['algorithm_tests'].items():
            if result.success:
                summary['successful_algorithms'] += 1
            else:
                summary['failed_algorithms'] += 1
                summary['success'] = False

        # Workflow summary
        for _workflow_name, result in results['workflow_tests'].items():
            if result.get('success', False):
                summary['successful_workflows'] += 1
            else:
                summary['failed_workflows'] += 1

        # Performance summary
        if 'cache_performance' in results['performance_tests']:
            cache_perf = results['performance_tests']['cache_performance']
            summary['performance_metrics']['cache_speedup'] = cache_perf.get('speedup_factor', 1.0)

        # Generate recommendations
        if summary['failed_algorithms'] > 0:
            summary['recommendations'].append(
                f"Review {summary['failed_algorithms']} failed algorithm tests"
            )

        if summary['failed_workflows'] > 0:
            summary['recommendations'].append(
                f"Review {summary['failed_workflows']} failed workflow tests"
            )

        if summary['success']:
            summary['recommendations'].append("All validation tests passed successfully")

        return summary

# Export validation functions
def run_validation() -> Dict[str, Any]:
    """Run comprehensive algorithm registry validation"""
    validator = AlgorithmRegistryValidator()
    return validator.run_comprehensive_validation()

def quick_validation() -> bool:
    """Run quick validation to check basic functionality"""
    try:
        validator = AlgorithmRegistryValidator()

        # Test one algorithm from each category
        test_algorithms = ['natural_step_detector', 'fopdt_identifier', 'imc_tuner']

        for alg_name in test_algorithms:
            if alg_name in registry.list_algorithms():
                result = validator._test_single_algorithm(alg_name)
                if not result.success:
                    return False

        return True

    except Exception as e:
        logger.error(f"Quick validation failed: {e}")
        return False

__all__ = [
    'AlgorithmRegistryValidator',
    'ValidationResult',
    'run_validation',
    'quick_validation'
]
