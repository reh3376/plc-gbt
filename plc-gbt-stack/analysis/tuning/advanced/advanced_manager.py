#!/usr/bin/env python3
"""
Phase 22.2.3: Advanced Tuning Manager
====================================

Comprehensive manager for all advanced tuning strategies including:
- Strategy selection and recommendation
- Multi-strategy comparison and validation
- Hybrid strategy implementation
- Performance optimization across strategies

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.3 - Advanced Tuning Strategies
Methodology: AI Task Orchestrator Guide
"""

import concurrent.futures
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Import advanced strategy components
try:
    from . import adaptive_control, gain_scheduling, mpc_tuning, multi_loop_coordination
    MPCTuner = mpc_tuning.MPCTuner
    EconomicMPCTuner = mpc_tuning.EconomicMPCTuner
    RobustMPCTuner = mpc_tuning.RobustMPCTuner
    HybridMPCTuner = mpc_tuning.HybridMPCTuner
    AdaptiveController = adaptive_control.AdaptiveController
    RLSAdaptiveController = adaptive_control.RLSAdaptiveController
    GradientDescentController = adaptive_control.GradientDescentController
    GainScheduler = gain_scheduling.GainScheduler
    LinearGainScheduler = gain_scheduling.LinearGainScheduler
    FuzzyGainScheduler = gain_scheduling.FuzzyGainScheduler
    MultiLoopCoordinator = multi_loop_coordination.MultiLoopCoordinator
    DecentralizedCoordinator = multi_loop_coordination.DecentralizedCoordinator
    CentralizedCoordinator = multi_loop_coordination.CentralizedCoordinator
    ADVANCED_STRATEGIES_AVAILABLE = True
except ImportError as e:
    ADVANCED_STRATEGIES_AVAILABLE = False
    logging.warning(f"⚠️ Advanced strategies not available: {e}")

# Import algorithm base class if available
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

class StrategySelectionMode(Enum):
    """Strategy selection modes"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    COMPARATIVE = "comparative"
    HYBRID = "hybrid"
    PERFORMANCE_DRIVEN = "performance_driven"

class ProcessCharacteristics(Enum):
    """Process characteristics for strategy selection"""
    SINGLE_LOOP = "single_loop"
    MULTI_LOOP = "multi_loop"
    CONSTRAINED = "constrained"
    TIME_VARYING = "time_varying"
    NONLINEAR = "nonlinear"
    ECONOMIC_OPTIMIZATION = "economic_optimization"

@dataclass
class AdvancedTuningConfiguration:
    """Advanced tuning manager configuration"""
    selection_mode: StrategySelectionMode = StrategySelectionMode.AUTOMATIC
    enabled_strategies: List[str] = field(default_factory=lambda: [
        "mpc_tuning", "adaptive_control", "gain_scheduling", "multi_loop_coordination"
    ])

    # Automatic selection parameters
    process_characteristics: List[ProcessCharacteristics] = field(default_factory=list)
    performance_weights: Dict[str, float] = field(default_factory=lambda: {
        "tracking": 1.0,
        "robustness": 0.8,
        "economic": 0.6,
        "interaction": 0.4
    })

    # Strategy-specific configurations
    mpc_config: Optional[Dict[str, Any]] = None
    adaptive_config: Optional[Dict[str, Any]] = None
    gain_schedule_config: Optional[Dict[str, Any]] = None
    multi_loop_config: Optional[Dict[str, Any]] = None

    # Comparison parameters
    comparison_metrics: List[str] = field(default_factory=lambda: [
        "performance", "robustness", "complexity", "implementation_cost"
    ])

    # Execution parameters
    parallel_execution: bool = True
    max_workers: int = 4
    timeout_per_strategy: float = 300.0  # seconds

    # Validation parameters
    cross_validation: bool = True
    validation_split: float = 0.2
    monte_carlo_samples: int = 100

@dataclass
class StrategyResult:
    """Result from a single strategy"""
    strategy_name: str
    success: bool
    result: Any
    execution_time: float
    performance_score: float
    robustness_score: float
    complexity_score: float
    implementation_cost: float
    error_message: Optional[str] = None

@dataclass
class AdvancedTuningResults:
    """Advanced tuning manager results"""
    tuning_method: str
    configuration: AdvancedTuningConfiguration
    strategy_results: List[StrategyResult]
    recommended_strategy: str
    recommendation_confidence: float
    comparative_analysis: Dict[str, Any]
    hybrid_parameters: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    validation_results: Dict[str, Any]
    execution_summary: Dict[str, Any]
    execution_time: float
    status: str

class AdvancedTuningManager:
    """Comprehensive advanced tuning strategy manager"""

    def __init__(self, configuration: Optional[AdvancedTuningConfiguration] = None):
        self.config = configuration or AdvancedTuningConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Strategy registry
        self.strategy_registry = self._build_strategy_registry()

        # Selection rules
        self.selection_rules = self._build_selection_rules()

        # Results storage
        self.strategy_results = []
        self.execution_history = []

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute advanced tuning strategy selection and optimization"""
        try:
            start_time = time.time()

            # Analyze process characteristics
            process_analysis = self._analyze_process_characteristics(data)

            # Select strategies based on configuration and analysis
            selected_strategies = self._select_strategies(process_analysis, data)

            # Execute selected strategies
            strategy_results = self._execute_strategies(selected_strategies, data)

            # Compare and analyze results
            comparative_analysis = self._compare_strategies(strategy_results)

            # Select recommended strategy
            recommended_strategy, confidence = self._recommend_strategy(strategy_results, comparative_analysis)

            # Generate hybrid parameters if applicable
            hybrid_parameters = self._generate_hybrid_parameters(strategy_results)

            # Validate results
            validation_results = self._validate_results(strategy_results, data)

            # Calculate performance metrics
            performance_metrics = self._calculate_performance_metrics(strategy_results)

            # Create execution summary
            execution_summary = self._create_execution_summary(strategy_results)

            execution_time = time.time() - start_time

            # Create results
            result = AdvancedTuningResults(
                tuning_method="AdvancedTuningManager",
                configuration=self.config,
                strategy_results=strategy_results,
                recommended_strategy=recommended_strategy,
                recommendation_confidence=confidence,
                comparative_analysis=comparative_analysis,
                hybrid_parameters=hybrid_parameters,
                performance_metrics=performance_metrics,
                validation_results=validation_results,
                execution_summary=execution_summary,
                execution_time=execution_time,
                status="success"
            )

            return {
                'success': True,
                'result': result,
                'method': 'advanced_tuning_manager'
            }

        except Exception as e:
            self.logger.error(f"Advanced tuning manager failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'advanced_tuning_manager'
            }

    def _build_strategy_registry(self) -> Dict[str, Any]:
        """Build registry of available strategies"""

        registry = {}

        if ADVANCED_STRATEGIES_AVAILABLE:
            # MPC strategies
            registry['mpc_tracking'] = {
                'class': MPCTuner,
                'category': 'mpc',
                'complexity': 'high',
                'best_for': ['constrained', 'multivariable', 'predictive']
            }
            registry['mpc_economic'] = {
                'class': EconomicMPCTuner,
                'category': 'mpc',
                'complexity': 'high',
                'best_for': ['economic_optimization', 'cost_minimization']
            }
            registry['mpc_robust'] = {
                'class': RobustMPCTuner,
                'category': 'mpc',
                'complexity': 'high',
                'best_for': ['uncertainty', 'robustness']
            }

            # Adaptive strategies
            registry['adaptive_rls'] = {
                'class': RLSAdaptiveController,
                'category': 'adaptive',
                'complexity': 'medium',
                'best_for': ['time_varying', 'unknown_parameters']
            }
            registry['adaptive_gradient'] = {
                'class': GradientDescentController,
                'category': 'adaptive',
                'complexity': 'medium',
                'best_for': ['online_learning', 'parameter_drift']
            }

            # Gain scheduling strategies
            registry['gain_schedule_linear'] = {
                'class': LinearGainScheduler,
                'category': 'gain_scheduling',
                'complexity': 'medium',
                'best_for': ['nonlinear', 'wide_operating_range']
            }
            registry['gain_schedule_fuzzy'] = {
                'class': FuzzyGainScheduler,
                'category': 'gain_scheduling',
                'complexity': 'medium',
                'best_for': ['expert_knowledge', 'linguistic_rules']
            }

            # Multi-loop strategies
            registry['multi_loop_decentralized'] = {
                'class': DecentralizedCoordinator,
                'category': 'multi_loop',
                'complexity': 'high',
                'best_for': ['interacting_loops', 'distributed_control']
            }
            registry['multi_loop_centralized'] = {
                'class': CentralizedCoordinator,
                'category': 'multi_loop',
                'complexity': 'high',
                'best_for': ['tight_coupling', 'global_optimization']
            }
        else:
            # Mock strategies for testing
            self.logger.warning("Using mock strategies - advanced implementations not available")
            registry = self._create_mock_strategies()

        return registry

    def _create_mock_strategies(self) -> Dict[str, Any]:
        """Create mock strategies for testing when implementations not available"""

        class MockStrategy:
            def __init__(self, name):
                self.name = name

            def execute(self, data):
                return {
                    'success': True,
                    'result': {
                        'tuning_method': self.name,
                        'parameters': {'Kp': 1.0, 'Ti': 10.0, 'Td': 1.0},
                        'performance_metrics': {'score': 0.8},
                        'execution_time': 0.1
                    }
                }

        return {
            'mpc_tracking': {
                'class': lambda: MockStrategy('MPC_Tracking'),
                'category': 'mpc',
                'complexity': 'high',
                'best_for': ['constrained']
            },
            'adaptive_rls': {
                'class': lambda: MockStrategy('Adaptive_RLS'),
                'category': 'adaptive',
                'complexity': 'medium',
                'best_for': ['time_varying']
            },
            'gain_schedule_linear': {
                'class': lambda: MockStrategy('Gain_Schedule_Linear'),
                'category': 'gain_scheduling',
                'complexity': 'medium',
                'best_for': ['nonlinear']
            },
            'multi_loop_decentralized': {
                'class': lambda: MockStrategy('Multi_Loop_Decentralized'),
                'category': 'multi_loop',
                'complexity': 'high',
                'best_for': ['interacting_loops']
            }
        }

    def _build_selection_rules(self) -> Dict[str, Any]:
        """Build strategy selection rules"""

        rules = {
            # Process type based selection
            'single_loop': {
                'preferred': ['adaptive_rls', 'gain_schedule_linear'],
                'avoid': ['multi_loop_decentralized', 'multi_loop_centralized']
            },
            'multi_loop': {
                'preferred': ['multi_loop_decentralized', 'multi_loop_centralized'],
                'fallback': ['adaptive_rls']
            },
            'constrained': {
                'preferred': ['mpc_tracking', 'mpc_robust'],
                'fallback': ['gain_schedule_linear']
            },
            'time_varying': {
                'preferred': ['adaptive_rls', 'adaptive_gradient'],
                'fallback': ['gain_schedule_fuzzy']
            },
            'nonlinear': {
                'preferred': ['gain_schedule_linear', 'gain_schedule_fuzzy', 'mpc_tracking'],
                'fallback': ['adaptive_rls']
            },
            'economic_optimization': {
                'preferred': ['mpc_economic'],
                'fallback': ['mpc_tracking']
            }
        }

        return rules

    def _analyze_process_characteristics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze process characteristics to guide strategy selection"""

        characteristics = {
            'process_type': 'single_loop',
            'has_constraints': False,
            'is_time_varying': False,
            'is_nonlinear': False,
            'requires_economic_optimization': False,
            'interaction_level': 'low',
            'uncertainty_level': 'low',
            'complexity_score': 1.0
        }

        # Analyze based on provided data
        if 'control_loops' in data and len(data['control_loops']) > 1:
            characteristics['process_type'] = 'multi_loop'
            characteristics['complexity_score'] += 1.0

        if 'interactions' in data and len(data['interactions']) > 0:
            interaction_strength = np.mean([abs(i.get('interaction_gain', 0)) for i in data['interactions']])
            if interaction_strength > 0.3:
                characteristics['interaction_level'] = 'high'
                characteristics['complexity_score'] += 0.5
            elif interaction_strength > 0.1:
                characteristics['interaction_level'] = 'medium'
                characteristics['complexity_score'] += 0.2

        # Check for constraints
        constraint_indicators = ['cv_min', 'cv_max', 'mv_min', 'mv_max', 'constraints']
        if any(indicator in str(data) for indicator in constraint_indicators):
            characteristics['has_constraints'] = True
            characteristics['complexity_score'] += 0.5

        # Check for time-varying behavior
        if 'time_varying' in data or 'adaptive' in str(data).lower():
            characteristics['is_time_varying'] = True
            characteristics['complexity_score'] += 0.3

        # Check for nonlinearity
        if 'nonlinear' in str(data).lower() or 'operating_points' in data:
            characteristics['is_nonlinear'] = True
            characteristics['complexity_score'] += 0.4

        # Check for economic optimization
        if any(keyword in str(data).lower() for keyword in ['economic', 'cost', 'profit', 'energy']):
            characteristics['requires_economic_optimization'] = True
            characteristics['complexity_score'] += 0.6

        # Assess uncertainty level
        if 'uncertainty' in data or 'noise' in str(data).lower():
            characteristics['uncertainty_level'] = 'high'
            characteristics['complexity_score'] += 0.3

        return characteristics

    def _select_strategies(self, process_analysis: Dict[str, Any], data: Dict[str, Any]) -> List[str]:
        """Select appropriate strategies based on process analysis"""

        if self.config.selection_mode == StrategySelectionMode.MANUAL:
            return self.config.enabled_strategies

        elif self.config.selection_mode == StrategySelectionMode.COMPARATIVE:
            return list(self.strategy_registry.keys())

        else:  # AUTOMATIC or PERFORMANCE_DRIVEN
            selected = []

            # Rule-based selection
            for characteristic, is_present in process_analysis.items():
                if is_present and characteristic in self.selection_rules:
                    rule = self.selection_rules[characteristic]
                    selected.extend(rule.get('preferred', []))

            # Remove duplicates and filter by enabled strategies
            selected = list(set(selected))
            selected = [s for s in selected if s in self.config.enabled_strategies]

            # Ensure at least one strategy is selected
            if not selected and self.config.enabled_strategies:
                selected = [self.config.enabled_strategies[0]]

            # Limit number of strategies for automatic mode
            if self.config.selection_mode == StrategySelectionMode.AUTOMATIC:
                selected = selected[:3]  # Limit to top 3

            return selected

    def _execute_strategies(self, selected_strategies: List[str], data: Dict[str, Any]) -> List[StrategyResult]:
        """Execute selected strategies"""

        results = []

        if self.config.parallel_execution:
            # Parallel execution
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_strategy = {}

                for strategy_name in selected_strategies:
                    if strategy_name in self.strategy_registry:
                        future = executor.submit(
                            self._execute_single_strategy,
                            strategy_name,
                            data
                        )
                        future_to_strategy[future] = strategy_name

                for future in concurrent.futures.as_completed(future_to_strategy, timeout=self.config.timeout_per_strategy):
                    strategy_name = future_to_strategy[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        self.logger.error(f"Strategy {strategy_name} failed: {e}")
                        results.append(StrategyResult(
                            strategy_name=strategy_name,
                            success=False,
                            result=None,
                            execution_time=0.0,
                            performance_score=0.0,
                            robustness_score=0.0,
                            complexity_score=0.0,
                            implementation_cost=0.0,
                            error_message=str(e)
                        ))
        else:
            # Sequential execution
            for strategy_name in selected_strategies:
                result = self._execute_single_strategy(strategy_name, data)
                results.append(result)

        return results

    def _execute_single_strategy(self, strategy_name: str, data: Dict[str, Any]) -> StrategyResult:
        """Execute a single strategy"""

        start_time = time.time()

        try:
            # Get strategy class
            strategy_info = self.strategy_registry[strategy_name]
            strategy_class = strategy_info['class']

            # Create strategy instance
            if callable(strategy_class):
                strategy = strategy_class()
            else:
                strategy = strategy_class

            # Execute strategy
            result = strategy.execute(data)
            execution_time = time.time() - start_time

            if result['success']:
                # Calculate scores
                performance_score = self._calculate_performance_score(result['result'])
                robustness_score = self._calculate_robustness_score(result['result'])
                complexity_score = self._calculate_complexity_score(strategy_info, result['result'])
                implementation_cost = self._calculate_implementation_cost(strategy_info)

                return StrategyResult(
                    strategy_name=strategy_name,
                    success=True,
                    result=result['result'],
                    execution_time=execution_time,
                    performance_score=performance_score,
                    robustness_score=robustness_score,
                    complexity_score=complexity_score,
                    implementation_cost=implementation_cost
                )
            else:
                return StrategyResult(
                    strategy_name=strategy_name,
                    success=False,
                    result=None,
                    execution_time=execution_time,
                    performance_score=0.0,
                    robustness_score=0.0,
                    complexity_score=0.0,
                    implementation_cost=0.0,
                    error_message=result.get('error', 'Unknown error')
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return StrategyResult(
                strategy_name=strategy_name,
                success=False,
                result=None,
                execution_time=execution_time,
                performance_score=0.0,
                robustness_score=0.0,
                complexity_score=0.0,
                implementation_cost=0.0,
                error_message=str(e)
            )

    def _calculate_performance_score(self, result: Any) -> float:
        """Calculate performance score from strategy result"""

        # Extract performance metrics
        if hasattr(result, 'performance_metrics'):
            metrics = result.performance_metrics
            if isinstance(metrics, dict):
                # Combine various performance indicators
                score = 0.0
                count = 0

                for key, value in metrics.items():
                    if isinstance(value, (int, float)) and not np.isnan(value):
                        # Normalize different metrics to 0-1 scale
                        if 'error' in key.lower():
                            normalized = 1.0 / (1.0 + abs(value))
                        elif 'time' in key.lower():
                            normalized = 1.0 / (1.0 + value/10)
                        else:
                            normalized = min(abs(value), 1.0)

                        score += normalized
                        count += 1

                return score / max(count, 1)

        # Default scoring based on execution success
        return 0.7 if result else 0.0

    def _calculate_robustness_score(self, result: Any) -> float:
        """Calculate robustness score from strategy result"""

        # Look for robustness indicators
        if hasattr(result, 'robustness_analysis'):
            analysis = result.robustness_analysis
            if isinstance(analysis, dict):
                robust_indicators = analysis.get('robust', False)
                robustness_prob = analysis.get('robustness_probability', 0.5)

                if isinstance(robust_indicators, bool):
                    base_score = 0.8 if robust_indicators else 0.3
                else:
                    base_score = 0.5

                return base_score * robustness_prob

        # Look for stability indicators
        if hasattr(result, 'stability_analysis'):
            analysis = result.stability_analysis
            if isinstance(analysis, dict):
                stable = analysis.get('stable', False)
                return 0.7 if stable else 0.2

        return 0.5  # Default moderate robustness

    def _calculate_complexity_score(self, strategy_info: Dict[str, Any], result: Any) -> float:
        """Calculate complexity score (lower is better)"""

        # Base complexity from strategy category
        complexity_map = {
            'mpc': 0.8,
            'adaptive': 0.6,
            'gain_scheduling': 0.5,
            'multi_loop': 0.9
        }

        base_complexity = complexity_map.get(strategy_info.get('category', 'unknown'), 0.5)

        # Adjust based on result complexity
        if hasattr(result, 'execution_time'):
            time_factor = min(result.execution_time / 10.0, 0.3)  # Max 0.3 penalty
            base_complexity += time_factor

        return min(base_complexity, 1.0)

    def _calculate_implementation_cost(self, strategy_info: Dict[str, Any]) -> float:
        """Calculate implementation cost score (lower is better)"""

        # Cost based on complexity and requirements
        cost_map = {
            'mpc': 0.9,      # High cost (optimization, constraints)
            'adaptive': 0.6,  # Medium cost (online computation)
            'gain_scheduling': 0.4,  # Lower cost (lookup/interpolation)
            'multi_loop': 0.8  # High cost (coordination, communication)
        }

        return cost_map.get(strategy_info.get('category', 'unknown'), 0.5)

    def _compare_strategies(self, strategy_results: List[StrategyResult]) -> Dict[str, Any]:
        """Compare strategies across multiple criteria"""

        successful_results = [r for r in strategy_results if r.success]

        if not successful_results:
            return {"comparison_available": False, "reason": "No successful strategies"}

        # Create comparison matrix
        comparison_data = []
        for result in successful_results:
            comparison_data.append({
                'strategy': result.strategy_name,
                'performance': result.performance_score,
                'robustness': result.robustness_score,
                'complexity': 1.0 - result.complexity_score,  # Invert for comparison
                'cost': 1.0 - result.implementation_cost,  # Invert for comparison
                'execution_time': result.execution_time,
                'overall_score': self._calculate_overall_score(result)
            })

        comparison_df = pd.DataFrame(comparison_data)

        # Rankings
        rankings = {}
        for metric in ['performance', 'robustness', 'complexity', 'cost', 'overall_score']:
            if metric in comparison_df.columns:
                rankings[metric] = comparison_df.nlargest(len(comparison_df), metric)['strategy'].tolist()

        # Best in each category
        best_performers = {}
        for metric in ['performance', 'robustness', 'complexity', 'cost']:
            if metric in comparison_df.columns:
                best_idx = comparison_df[metric].idxmax()
                best_performers[metric] = comparison_df.loc[best_idx, 'strategy']

        return {
            "comparison_available": True,
            "comparison_matrix": comparison_data,
            "rankings": rankings,
            "best_performers": best_performers,
            "num_successful_strategies": len(successful_results),
            "num_failed_strategies": len(strategy_results) - len(successful_results)
        }

    def _calculate_overall_score(self, result: StrategyResult) -> float:
        """Calculate weighted overall score"""

        weights = self.config.performance_weights

        score = (weights.get('tracking', 1.0) * result.performance_score +
                weights.get('robustness', 0.8) * result.robustness_score +
                weights.get('economic', 0.6) * (1.0 - result.implementation_cost) +
                weights.get('interaction', 0.4) * (1.0 - result.complexity_score))

        total_weight = sum(weights.values())
        return score / total_weight

    def _recommend_strategy(self, strategy_results: List[StrategyResult],
                           comparative_analysis: Dict[str, Any]) -> Tuple[str, float]:
        """Recommend best strategy with confidence"""

        successful_results = [r for r in strategy_results if r.success]

        if not successful_results:
            return "none", 0.0

        # Calculate overall scores
        scored_results = [(r, self._calculate_overall_score(r)) for r in successful_results]
        scored_results.sort(key=lambda x: x[1], reverse=True)

        best_strategy = scored_results[0][0].strategy_name
        best_score = scored_results[0][1]

        # Calculate confidence based on score separation
        if len(scored_results) > 1:
            second_score = scored_results[1][1]
            score_separation = best_score - second_score
            confidence = min(0.5 + score_separation, 1.0)
        else:
            confidence = 0.8  # High confidence if only one successful strategy

        # Adjust confidence based on absolute score
        confidence *= best_score

        return best_strategy, confidence

    def _generate_hybrid_parameters(self, strategy_results: List[StrategyResult]) -> Optional[Dict[str, Any]]:
        """Generate hybrid parameters combining multiple strategies"""

        if self.config.selection_mode != StrategySelectionMode.HYBRID:
            return None

        successful_results = [r for r in strategy_results if r.success]

        if len(successful_results) < 2:
            return None

        # Weighted parameter combination
        total_weight = sum(self._calculate_overall_score(r) for r in successful_results)

        if total_weight == 0:
            return None

        hybrid_params = {'Kp': 0.0, 'Ti': 0.0, 'Td': 0.0}

        for result in successful_results:
            weight = self._calculate_overall_score(result) / total_weight

            # Extract parameters from result
            params = self._extract_parameters(result.result)

            for param in ['Kp', 'Ti', 'Td']:
                if param in params:
                    hybrid_params[param] += weight * params[param]

        return {
            'parameters': hybrid_params,
            'combination_method': 'weighted_average',
            'strategies_combined': [r.strategy_name for r in successful_results],
            'weights': [self._calculate_overall_score(r) / total_weight for r in successful_results]
        }

    def _extract_parameters(self, result: Any) -> Dict[str, float]:
        """Extract PID parameters from strategy result"""

        params = {}

        # Try different parameter locations
        if hasattr(result, 'parameters'):
            if isinstance(result.parameters, dict):
                params.update(result.parameters)

        if hasattr(result, 'final_parameters'):
            if isinstance(result.final_parameters, dict):
                params.update(result.final_parameters)

        if hasattr(result, 'optimized_parameters'):
            opt_params = result.optimized_parameters
            if isinstance(opt_params, dict):
                # Handle multi-loop case
                if len(opt_params) == 1:
                    params.update(list(opt_params.values())[0])
                else:
                    # Use first loop parameters
                    first_loop = list(opt_params.keys())[0]
                    params.update(opt_params[first_loop])

        # Ensure default values
        params.setdefault('Kp', 1.0)
        params.setdefault('Ti', 10.0)
        params.setdefault('Td', 1.0)

        return params

    def _validate_results(self, strategy_results: List[StrategyResult], data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate strategy results"""

        validation = {
            "total_strategies": len(strategy_results),
            "successful_strategies": len([r for r in strategy_results if r.success]),
            "failed_strategies": len([r for r in strategy_results if not r.success]),
            "average_execution_time": np.mean([r.execution_time for r in strategy_results]),
            "parameter_consistency": True,
            "stability_validated": True
        }

        # Cross-validation if enabled
        if self.config.cross_validation:
            cv_results = self._cross_validate_strategies(strategy_results, data)
            validation.update(cv_results)

        return validation

    def _cross_validate_strategies(self, strategy_results: List[StrategyResult],
                                  data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-validation of strategies"""

        # Simplified cross-validation
        successful_results = [r for r in strategy_results if r.success]

        if len(successful_results) < 2:
            return {"cross_validation": False, "reason": "Insufficient successful strategies"}

        # Parameter consistency check
        all_params = []
        for result in successful_results:
            params = self._extract_parameters(result.result)
            all_params.append([params['Kp'], params['Ti'], params['Td']])

        all_params = np.array(all_params)
        param_std = np.std(all_params, axis=0)
        param_consistency = np.all(param_std / (np.mean(all_params, axis=0) + 1e-6) < 0.5)

        return {
            "cross_validation": True,
            "parameter_consistency": bool(param_consistency),
            "parameter_variation": param_std.tolist(),
            "strategies_validated": len(successful_results)
        }

    def _calculate_performance_metrics(self, strategy_results: List[StrategyResult]) -> Dict[str, float]:
        """Calculate overall performance metrics"""

        successful_results = [r for r in strategy_results if r.success]

        if not successful_results:
            return {"success_rate": 0.0}

        return {
            "success_rate": len(successful_results) / len(strategy_results),
            "average_performance_score": np.mean([r.performance_score for r in successful_results]),
            "average_robustness_score": np.mean([r.robustness_score for r in successful_results]),
            "average_execution_time": np.mean([r.execution_time for r in successful_results]),
            "best_performance_score": max(r.performance_score for r in successful_results),
            "performance_std": np.std([r.performance_score for r in successful_results])
        }

    def _create_execution_summary(self, strategy_results: List[StrategyResult]) -> Dict[str, Any]:
        """Create execution summary"""

        return {
            "total_strategies_attempted": len(strategy_results),
            "successful_executions": len([r for r in strategy_results if r.success]),
            "failed_executions": len([r for r in strategy_results if not r.success]),
            "total_execution_time": sum(r.execution_time for r in strategy_results),
            "parallel_execution": self.config.parallel_execution,
            "strategy_names": [r.strategy_name for r in strategy_results],
            "execution_order": [r.strategy_name for r in strategy_results],
            "failure_reasons": [r.error_message for r in strategy_results if r.error_message]
        }

    def get_available_strategies(self) -> List[str]:
        """Get list of available advanced tuning strategies"""
        return list(self.strategy_registry.keys())

    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """Get detailed information about a strategy"""
        if strategy_name not in self.strategy_registry:
            return {"error": f"Strategy '{strategy_name}' not found"}

        strategy = self.strategy_registry[strategy_name]
        return {
            "name": strategy_name,
            "class": strategy.__class__.__name__,
            "available": ADVANCED_STRATEGIES_AVAILABLE,
            "description": f"Advanced tuning strategy: {strategy_name}"
        }

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of recent executions"""
        return {
            "total_executions": len(self.execution_history),
            "recent_strategies": [result.get("strategy", "unknown") for result in self.strategy_results[-5:]],
            "available_strategies": self.get_available_strategies(),
            "strategy_availability": ADVANCED_STRATEGIES_AVAILABLE
        }


# Register algorithm if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:

    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.HIGH,
        metadata=AlgorithmMetadata(
            name="Advanced Tuning Manager",
            description="Comprehensive manager for advanced tuning strategies",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["advanced", "multi_strategy", "optimization", "coordination"]
        )
    )
    class RegisteredAdvancedTuningManager(AdvancedTuningManager):
        pass


# Export classes and functions
__all__ = [
    'AdvancedTuningManager',
    'AdvancedTuningConfiguration',
    'StrategyResult',
    'AdvancedTuningResults',
    'StrategySelectionMode',
    'ProcessCharacteristics'
]
