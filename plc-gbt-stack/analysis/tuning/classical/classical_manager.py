#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Classical Tuning Manager Implementation
================================================================

Comprehensive management system for classical PID tuning methods.
Provides orchestration, comparison, and selection capabilities for all
implemented classical tuning algorithms.

Features:
- Method selection based on process characteristics
- Multi-method comparison and analysis
- Automatic best method recommendation
- Performance vs robustness trade-off analysis
- Industrial application guidance

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Import classical tuning methods
try:
    from .astrom_hagglund import AHTuningMethod, AstromHagglundTuner
    from .chien_hrones_reswick import (
        ChienHronesReswickTuner,
        CHRControllerType,
        CHROptimizationCriteria,
        CHRResponseType,
    )
    from .cohen_coon import CCResponseType, CohenCoonTuner
    from .lambda_tuning import LambdaOptimizationMode, LambdaStrategy, LambdaTuner
    from .tyreus_luyben import TLTuningStrategy, TyreusLuybenTuner
    from .ziegler_nichols import (
        ZieglerNicholsProcessReaction,
        ZieglerNicholsUltimateGain,
        ZNResponseType,
        ZNTuningType,
    )
    CLASSICAL_METHODS_AVAILABLE = True
except ImportError as e:
    CLASSICAL_METHODS_AVAILABLE = False
    logging.warning(f"⚠️ Classical tuning methods not available: {e}")

# Import algorithm base class
try:
    from ...algorithms import (
        AlgorithmBase,
        AlgorithmCategory,
        AlgorithmComplexity,
        AlgorithmMetadata,
        registry,
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class TuningMethodSelection(Enum):
    """Method selection strategies"""
    AUTOMATIC = "automatic"
    ROBUSTNESS_PRIORITY = "robustness_priority"
    PERFORMANCE_PRIORITY = "performance_priority"
    USER_SPECIFIED = "user_specified"

class ProcessClassification(Enum):
    """Process type classifications"""
    FAST_NO_DEADTIME = "fast_no_deadtime"
    MODERATE_DEADTIME = "moderate_deadtime"
    SIGNIFICANT_DEADTIME = "significant_deadtime"
    DEADTIME_DOMINANT = "deadtime_dominant"
    HIGH_GAIN = "high_gain"
    INTEGRATING = "integrating"

@dataclass
class MethodComparisonResult:
    """Individual method comparison result"""
    method_name: str
    suitability_score: float
    robustness_score: float
    performance_score: float
    overall_score: float
    parameters: Dict[str, float]
    pros: List[str]
    cons: List[str]
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class ClassicalTuningComparison:
    """Comprehensive comparison of classical tuning methods"""
    process_classification: ProcessClassification
    recommended_method: str
    recommended_parameters: Dict[str, float]
    method_results: List[MethodComparisonResult]
    comparison_matrix: Dict[str, Dict[str, float]]
    selection_rationale: str
    trade_off_analysis: Dict[str, Any]
    implementation_guidance: List[str]
    execution_time: float

class TuningMethodSelector:
    """Intelligent selector for classical tuning methods"""

    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.TuningMethodSelector')

    def classify_process(self, K: float, L: float, T: float) -> ProcessClassification:
        """Classify process based on characteristics"""

        lt_ratio = L / T if T > 0 else 0

        # Classification logic
        if abs(K) > 10:
            return ProcessClassification.HIGH_GAIN
        elif abs(K) > 1000:  # Very high gain suggests integrator
            return ProcessClassification.INTEGRATING
        elif lt_ratio < 0.1:
            return ProcessClassification.FAST_NO_DEADTIME
        elif lt_ratio < 0.3:
            return ProcessClassification.MODERATE_DEADTIME
        elif lt_ratio < 1.0:
            return ProcessClassification.SIGNIFICANT_DEADTIME
        else:
            return ProcessClassification.DEADTIME_DOMINANT

    def get_method_suitability(self, process_class: ProcessClassification) -> Dict[str, float]:
        """Get suitability scores for each method based on process classification"""

        # Suitability matrix (0-1, higher is better)
        suitability_matrix = {
            ProcessClassification.FAST_NO_DEADTIME: {
                'ziegler_nichols': 0.9,
                'cohen_coon': 0.3,
                'tyreus_luyben': 0.7,
                'astrom_hagglund': 0.8,
                'chien_hrones_reswick': 0.6,
                'lambda_tuning': 0.8
            },
            ProcessClassification.MODERATE_DEADTIME: {
                'ziegler_nichols': 0.7,
                'cohen_coon': 0.8,
                'tyreus_luyben': 0.8,
                'astrom_hagglund': 0.9,
                'chien_hrones_reswick': 0.9,
                'lambda_tuning': 0.9
            },
            ProcessClassification.SIGNIFICANT_DEADTIME: {
                'ziegler_nichols': 0.5,
                'cohen_coon': 0.9,
                'tyreus_luyben': 0.8,
                'astrom_hagglund': 0.8,
                'chien_hrones_reswick': 0.9,
                'lambda_tuning': 0.8
            },
            ProcessClassification.DEADTIME_DOMINANT: {
                'ziegler_nichols': 0.3,
                'cohen_coon': 0.9,
                'tyreus_luyben': 0.7,
                'astrom_hagglund': 0.7,
                'chien_hrones_reswick': 0.8,
                'lambda_tuning': 0.7
            },
            ProcessClassification.HIGH_GAIN: {
                'ziegler_nichols': 0.4,
                'cohen_coon': 0.6,
                'tyreus_luyben': 0.9,
                'astrom_hagglund': 0.7,
                'chien_hrones_reswick': 0.7,
                'lambda_tuning': 0.9
            },
            ProcessClassification.INTEGRATING: {
                'ziegler_nichols': 0.2,
                'cohen_coon': 0.4,
                'tyreus_luyben': 0.8,
                'astrom_hagglund': 0.6,
                'chien_hrones_reswick': 0.5,
                'lambda_tuning': 0.9
            }
        }

        return suitability_matrix.get(process_class, {
            'ziegler_nichols': 0.5,
            'cohen_coon': 0.5,
            'tyreus_luyben': 0.5,
            'astrom_hagglund': 0.5,
            'chien_hrones_reswick': 0.5,
            'lambda_tuning': 0.5
        })

    def get_method_characteristics(self) -> Dict[str, Dict[str, float]]:
        """Get characteristic scores for each method"""

        return {
            'ziegler_nichols': {
                'robustness': 0.5,
                'performance': 0.8,
                'ease_of_use': 0.9,
                'industrial_acceptance': 0.9
            },
            'cohen_coon': {
                'robustness': 0.7,
                'performance': 0.8,
                'ease_of_use': 0.8,
                'industrial_acceptance': 0.8
            },
            'tyreus_luyben': {
                'robustness': 0.9,
                'performance': 0.6,
                'ease_of_use': 0.8,
                'industrial_acceptance': 0.7
            },
            'astrom_hagglund': {
                'robustness': 0.8,
                'performance': 0.7,
                'ease_of_use': 0.6,
                'industrial_acceptance': 0.7
            },
            'chien_hrones_reswick': {
                'robustness': 0.8,
                'performance': 0.7,
                'ease_of_use': 0.7,
                'industrial_acceptance': 0.6
            },
            'lambda_tuning': {
                'robustness': 0.9,
                'performance': 0.6,
                'ease_of_use': 0.8,
                'industrial_acceptance': 0.8
            }
        }

    def select_best_method(self, suitability_scores: Dict[str, float],
                          method_characteristics: Dict[str, Dict[str, float]],
                          selection_strategy: TuningMethodSelection) -> str:
        """Select best method based on scores and strategy"""

        method_scores = {}

        for method, suitability in suitability_scores.items():
            characteristics = method_characteristics.get(method, {})

            if selection_strategy == TuningMethodSelection.ROBUSTNESS_PRIORITY:
                # Prioritize robustness
                score = 0.6 * suitability + 0.4 * characteristics.get('robustness', 0.5)
            elif selection_strategy == TuningMethodSelection.PERFORMANCE_PRIORITY:
                # Prioritize performance
                score = 0.6 * suitability + 0.4 * characteristics.get('performance', 0.5)
            else:  # AUTOMATIC or balanced
                # Balance all factors
                score = (0.4 * suitability +
                        0.25 * characteristics.get('robustness', 0.5) +
                        0.25 * characteristics.get('performance', 0.5) +
                        0.1 * characteristics.get('industrial_acceptance', 0.5))

            method_scores[method] = score

        # Return method with highest score
        return max(method_scores.items(), key=lambda x: x[1])[0]

class ClassicalTuningManager(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Comprehensive manager for classical PID tuning methods

    Orchestrates multiple classical tuning algorithms, provides comparison
    capabilities, and recommends the best method for given process characteristics.
    """

    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="classical_tuning_manager",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.HIGH,
                description="Comprehensive classical PID tuning method manager and comparator",
                version="1.0.0",
                min_data_points=30,
                supports_realtime=False,
                tags=["classical", "manager", "comparison", "selection"]
            )
            super().__init__(metadata)

        self.logger = logging.getLogger(__name__ + '.ClassicalTuningManager')
        self.selector = TuningMethodSelector()

        # Initialize tuning methods if available
        self.tuning_methods = {}
        if CLASSICAL_METHODS_AVAILABLE:
            self.tuning_methods = {
                'ziegler_nichols_ultimate': ZieglerNicholsUltimateGain(),
                'ziegler_nichols_reaction': ZieglerNicholsProcessReaction(),
                'cohen_coon': CohenCoonTuner(),
                'tyreus_luyben': TyreusLuybenTuner(),
                'astrom_hagglund': AstromHagglundTuner(),
                'chien_hrones_reswick': ChienHronesReswickTuner(),
                'lambda_tuning': LambdaTuner()
            }

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for classical tuning comparison"""
        errors = []

        # Check for required process parameters
        required_fields = ['process_gain', 'dead_time', 'time_constant']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif not isinstance(data[field], (int, float)):
                errors.append(f"Field '{field}' must be numeric")
            elif data[field] <= 0 and field != 'dead_time':  # dead_time can be zero
                errors.append(f"Field '{field}' must be positive")

        # Validate dead time is non-negative
        if 'dead_time' in data and data['dead_time'] < 0:
            errors.append("Dead time must be non-negative")

        # Check selection strategy
        if 'selection_strategy' in data:
            try:
                TuningMethodSelection(data['selection_strategy'])
            except ValueError:
                valid_strategies = [s.value for s in TuningMethodSelection]
                errors.append(f"Selection strategy must be one of: {valid_strategies}")

        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute comprehensive classical tuning comparison"""
        start_time = time.time()

        if not CLASSICAL_METHODS_AVAILABLE:
            return {
                'success': False,
                'error': 'Classical tuning methods not available',
                'method': 'classical_tuning_manager'
            }

        # Extract parameters
        K = data['process_gain']
        L = data['dead_time']
        T = data['time_constant']
        controller_type = data.get('controller_type', 'dependent')
        selection_strategy = TuningMethodSelection(data.get('selection_strategy', 'automatic'))

        try:
            # Classify process
            process_class = self.selector.classify_process(K, L, T)

            # Run all applicable methods
            method_results = self._run_all_methods(K, L, T, controller_type, process_class)

            # Compare methods
            comparison_result = self._compare_methods(
                method_results, process_class, selection_strategy, K, L, T
            )

            execution_time = time.time() - start_time
            comparison_result.execution_time = execution_time

            return {
                'success': True,
                'result': comparison_result,
                'method': 'classical_tuning_manager'
            }

        except Exception as e:
            self.logger.error(f"Classical tuning comparison failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'classical_tuning_manager'
            }

    def _run_all_methods(self, K: float, L: float, T: float, controller_type: str,
                        process_class: ProcessClassification) -> List[MethodComparisonResult]:
        """Run all applicable tuning methods"""

        method_results = []

        # Prepare common data
        base_data = {
            'process_gain': K,
            'dead_time': L,
            'time_constant': T,
            'controller_type': controller_type
        }

        # Run each method with appropriate parameters
        method_configs = {
            'ziegler_nichols_reaction': {
                'data': base_data,
                'tuner': self.tuning_methods['ziegler_nichols_reaction']
            },
            'cohen_coon': {
                'data': base_data,
                'tuner': self.tuning_methods['cohen_coon']
            },
            'tyreus_luyben': {
                'data': {**base_data, 'ultimate_gain': 2.0/K, 'ultimate_period': 4*T},
                'tuner': self.tuning_methods['tyreus_luyben']
            },
            'astrom_hagglund': {
                'data': {**base_data, 'ultimate_gain': 2.0/K, 'ultimate_period': 4*T},
                'tuner': self.tuning_methods['astrom_hagglund']
            },
            'chien_hrones_reswick': {
                'data': {**base_data, 'optimization_criteria': 'twenty_percent_overshoot'},
                'tuner': self.tuning_methods['chien_hrones_reswick']
            },
            'lambda_tuning': {
                'data': {**base_data, 'lambda_strategy': 'balanced'},
                'tuner': self.tuning_methods['lambda_tuning']
            }
        }

        for method_name, config in method_configs.items():
            try:
                start_time = time.time()
                result = config['tuner'].execute(config['data'])
                execution_time = time.time() - start_time

                if result['success']:
                    # Extract parameters from result
                    tuning_result = result['result']
                    parameters = tuning_result.parameters

                    # Calculate scores
                    scores = self._calculate_method_scores(
                        method_name, tuning_result, process_class, K, L, T
                    )

                    # Get pros and cons
                    pros, cons = self._get_method_pros_cons(method_name, tuning_result, process_class)

                    method_results.append(MethodComparisonResult(
                        method_name=method_name,
                        suitability_score=scores['suitability'],
                        robustness_score=scores['robustness'],
                        performance_score=scores['performance'],
                        overall_score=scores['overall'],
                        parameters=parameters,
                        pros=pros,
                        cons=cons,
                        execution_time=execution_time,
                        success=True
                    ))
                else:
                    method_results.append(MethodComparisonResult(
                        method_name=method_name,
                        suitability_score=0.0,
                        robustness_score=0.0,
                        performance_score=0.0,
                        overall_score=0.0,
                        parameters={},
                        pros=[],
                        cons=['Method failed to execute'],
                        execution_time=execution_time,
                        success=False,
                        error_message=result.get('error', 'Unknown error')
                    ))

            except Exception as e:
                self.logger.warning(f"Method {method_name} failed: {e}")
                method_results.append(MethodComparisonResult(
                    method_name=method_name,
                    suitability_score=0.0,
                    robustness_score=0.0,
                    performance_score=0.0,
                    overall_score=0.0,
                    parameters={},
                    pros=[],
                    cons=['Method execution failed'],
                    execution_time=0.0,
                    success=False,
                    error_message=str(e)
                ))

        return method_results

    def _calculate_method_scores(self, method_name: str, tuning_result: Any,
                               process_class: ProcessClassification,
                               K: float, L: float, T: float) -> Dict[str, float]:
        """Calculate scoring metrics for a method"""

        # Get base suitability scores
        suitability_scores = self.selector.get_method_suitability(process_class)
        method_characteristics = self.selector.get_method_characteristics()

        # Base scores
        suitability = suitability_scores.get(method_name.split('_')[0], 0.5)

        # Method-specific robustness and performance scoring
        if hasattr(tuning_result, 'stability_analysis'):
            stability = tuning_result.stability_analysis
            robustness = min(1.0, stability.get('gain_margin_db', 6) / 12)
        elif hasattr(tuning_result, 'robustness_analysis'):
            robustness_level = tuning_result.robustness_analysis.get('robustness_level', 'medium')
            robustness = {'very_high': 1.0, 'high': 0.8, 'medium': 0.6, 'low': 0.4}.get(robustness_level, 0.6)
        else:
            robustness = method_characteristics.get(method_name.split('_')[0], {}).get('robustness', 0.5)

        if hasattr(tuning_result, 'performance_prediction'):
            perf = tuning_result.performance_prediction
            performance = perf.get('performance_index', 0.5)
        else:
            performance = method_characteristics.get(method_name.split('_')[0], {}).get('performance', 0.5)

        # Overall score
        overall = 0.4 * suitability + 0.3 * robustness + 0.3 * performance

        return {
            'suitability': suitability,
            'robustness': robustness,
            'performance': performance,
            'overall': overall
        }

    def _get_method_pros_cons(self, method_name: str, tuning_result: Any,
                            process_class: ProcessClassification) -> Tuple[List[str], List[str]]:
        """Get pros and cons for each method"""

        method_characteristics = {
            'ziegler_nichols': {
                'pros': ['Well-known and widely accepted', 'Simple to apply', 'Good starting point'],
                'cons': ['Can be aggressive', 'Poor robustness', 'May cause oscillations']
            },
            'cohen_coon': {
                'pros': ['Excellent for dead time processes', 'Better than ZN for L/T > 0.3', 'Good stability'],
                'cons': ['Limited to FOPDT model', 'Not suitable for low dead time', 'More complex than ZN']
            },
            'tyreus_luyben': {
                'pros': ['Very conservative and stable', 'Excellent robustness', 'Low oscillation tendency'],
                'cons': ['Slow response', 'Conservative performance', 'May be too sluggish']
            },
            'astrom_hagglund': {
                'pros': ['Automatic identification', 'Real-time capability', 'Good balance'],
                'cons': ['Requires relay test', 'More complex setup', 'Needs process disturbance']
            },
            'chien_hrones_reswick': {
                'pros': ['Multiple optimization criteria', 'Well-defined objectives', 'Good for specific needs'],
                'cons': ['Many options to choose from', 'Less intuitive', 'Method complexity']
            },
            'lambda_tuning': {
                'pros': ['Excellent robustness', 'Smooth response', 'Easy to retune'],
                'cons': ['Conservative performance', 'Slower response', 'Requires lambda selection']
            }
        }

        base_method = method_name.split('_')[0]
        characteristics = method_characteristics.get(base_method, {'pros': [], 'cons': []})

        # Add process-specific pros/cons
        pros = characteristics['pros'].copy()
        cons = characteristics['cons'].copy()

        # Add specific recommendations based on process class
        if process_class == ProcessClassification.DEADTIME_DOMINANT:
            if base_method == 'cohen_coon':
                pros.append('Specifically designed for your process type')
            elif base_method == 'ziegler_nichols':
                cons.append('Not optimal for high dead time processes')

        return pros, cons

    def _compare_methods(self, method_results: List[MethodComparisonResult],
                        process_class: ProcessClassification,
                        selection_strategy: TuningMethodSelection,
                        K: float, L: float, T: float) -> ClassicalTuningComparison:
        """Compare all methods and generate comprehensive analysis"""

        # Sort by overall score
        successful_results = [r for r in method_results if r.success]
        successful_results.sort(key=lambda x: x.overall_score, reverse=True)

        # Create comparison matrix
        comparison_matrix = {}
        for result in method_results:
            comparison_matrix[result.method_name] = {
                'suitability': result.suitability_score,
                'robustness': result.robustness_score,
                'performance': result.performance_score,
                'overall': result.overall_score
            }

        # Get recommended method
        if successful_results:
            recommended = successful_results[0]
            recommended_method = recommended.method_name
            recommended_parameters = recommended.parameters

            # Generate selection rationale
            selection_rationale = f"Selected {recommended_method} based on overall score of {recommended.overall_score:.3f}. "
            selection_rationale += f"This method scored highest in {self._get_best_attribute(recommended)} "
            selection_rationale += f"and is well-suited for {process_class.value} processes."
        else:
            recommended_method = "none"
            recommended_parameters = {}
            selection_rationale = "No methods succeeded in generating tuning parameters."

        # Trade-off analysis
        trade_off_analysis = self._analyze_trade_offs(successful_results)

        # Implementation guidance
        implementation_guidance = self._generate_implementation_guidance(
            process_class, recommended_method, successful_results, K, L, T
        )

        return ClassicalTuningComparison(
            process_classification=process_class,
            recommended_method=recommended_method,
            recommended_parameters=recommended_parameters,
            method_results=method_results,
            comparison_matrix=comparison_matrix,
            selection_rationale=selection_rationale,
            trade_off_analysis=trade_off_analysis,
            implementation_guidance=implementation_guidance,
            execution_time=0.0  # Will be set by caller
        )

    def _get_best_attribute(self, result: MethodComparisonResult) -> str:
        """Get the best attribute for a method result"""
        scores = {
            'suitability': result.suitability_score,
            'robustness': result.robustness_score,
            'performance': result.performance_score
        }
        return max(scores.items(), key=lambda x: x[1])[0]

    def _analyze_trade_offs(self, results: List[MethodComparisonResult]) -> Dict[str, Any]:
        """Analyze trade-offs between methods"""

        if not results:
            return {'analysis': 'No successful methods for comparison'}

        # Find best performers in each category
        best_robustness = max(results, key=lambda x: x.robustness_score)
        best_performance = max(results, key=lambda x: x.performance_score)
        best_overall = max(results, key=lambda x: x.overall_score)

        # Calculate trade-off metrics
        avg_robustness = np.mean([r.robustness_score for r in results])
        avg_performance = np.mean([r.performance_score for r in results])

        robustness_vs_performance = {
            'correlation': np.corrcoef(
                [r.robustness_score for r in results],
                [r.performance_score for r in results]
            )[0, 1] if len(results) > 1 else 0,
            'best_robustness_method': best_robustness.method_name,
            'best_performance_method': best_performance.method_name,
            'trade_off_severity': abs(avg_robustness - avg_performance)
        }

        return {
            'best_robustness': {
                'method': best_robustness.method_name,
                'score': best_robustness.robustness_score
            },
            'best_performance': {
                'method': best_performance.method_name,
                'score': best_performance.performance_score
            },
            'best_overall': {
                'method': best_overall.method_name,
                'score': best_overall.overall_score
            },
            'robustness_vs_performance': robustness_vs_performance,
            'method_diversity': len({r.method_name for r in results}),
            'average_scores': {
                'robustness': avg_robustness,
                'performance': avg_performance,
                'overall': np.mean([r.overall_score for r in results])
            }
        }

    def _generate_implementation_guidance(self, process_class: ProcessClassification,
                                        recommended_method: str,
                                        results: List[MethodComparisonResult],
                                        K: float, L: float, T: float) -> List[str]:
        """Generate implementation guidance"""

        guidance = []

        # Process-specific guidance
        process_guidance = {
            ProcessClassification.FAST_NO_DEADTIME: [
                "Fast process with minimal dead time - most methods should work well",
                "Consider starting with recommended method and fine-tuning as needed"
            ],
            ProcessClassification.MODERATE_DEADTIME: [
                "Moderate dead time process - good candidate for multiple methods",
                "Test recommended method first, consider alternatives if needed"
            ],
            ProcessClassification.SIGNIFICANT_DEADTIME: [
                "Significant dead time requires careful method selection",
                "Cohen-Coon or Lambda tuning typically work best for this process type"
            ],
            ProcessClassification.DEADTIME_DOMINANT: [
                "Dead time dominant process - avoid aggressive tuning methods",
                "Prioritize robustness over speed of response"
            ],
            ProcessClassification.HIGH_GAIN: [
                "High gain process requires conservative tuning",
                "Consider detuning recommended parameters by 20-30% initially"
            ],
            ProcessClassification.INTEGRATING: [
                "Integrating process requires specialized consideration",
                "Lambda tuning typically works best for integrating processes"
            ]
        }

        guidance.extend(process_guidance.get(process_class, []))

        # Method-specific guidance
        if recommended_method != "none":
            if "ziegler_nichols" in recommended_method:
                guidance.append("ZN method selected - test incrementally and monitor for oscillations")
            elif "cohen_coon" in recommended_method:
                guidance.append("Cohen-Coon selected - excellent for your dead time process")
            elif "tyreus_luyben" in recommended_method:
                guidance.append("Tyreus-Luyben selected - very stable but conservative response")
            elif "lambda" in recommended_method:
                guidance.append("Lambda tuning selected - adjust lambda value to balance speed vs robustness")

        # General implementation guidance
        guidance.extend([
            "Always test tuning in manual mode first",
            "Monitor for oscillations and adjust conservatively",
            "Consider process safety limits when implementing new tuning",
            "Document baseline performance before implementing changes"
        ])

        # Alternative method guidance
        if len(results) > 1:
            second_best = sorted(results, key=lambda x: x.overall_score, reverse=True)[1]
            guidance.append(f"Alternative method: {second_best.method_name} (score: {second_best.overall_score:.3f})")

        return guidance

# Register Classical Tuning Manager
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(ClassicalTuningManager)
        logger.info("Classical Tuning Manager registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Classical Tuning Manager: {e}")

# Export classes
__all__ = [
    'ClassicalTuningManager',
    'ClassicalTuningComparison',
    'TuningMethodSelector',
    'MethodComparisonResult',
    'TuningMethodSelection',
    'ProcessClassification'
]

logger.info("Classical Tuning Manager implementation completed")
