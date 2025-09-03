#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Lambda Tuning Implementation
======================================================

Implementation of Lambda tuning variants for conservative, smooth response control.
Lambda tuning provides excellent robustness and smooth response characteristics
by allowing the user to specify the desired closed-loop time constant.

Key Features:
- User-specified closed-loop time constant (lambda)
- Multiple lambda selection strategies
- Excellent robustness and smooth response
- Automatic lambda optimization based on process characteristics
- Support for various process models (FOPDT, SOPDT)

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

class LambdaStrategy(Enum):
    """Lambda tuning strategies"""
    USER_SPECIFIED = "user_specified"
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    AUTOMATIC = "automatic"

class LambdaOptimizationMode(Enum):
    """Lambda optimization modes"""
    ROBUSTNESS = "robustness"
    PERFORMANCE = "performance"
    BALANCE = "balance"

class ProcessModelType(Enum):
    """Process model types for lambda tuning"""
    FOPDT = "fopdt"  # First Order Plus Dead Time
    SOPDT = "sopdt"  # Second Order Plus Dead Time
    INTEGRATOR = "integrator"

@dataclass
class LambdaTuningResult:
    """Lambda tuning result"""
    tuning_method: str
    lambda_strategy: LambdaStrategy
    optimization_mode: LambdaOptimizationMode
    lambda_value: float
    parameters: Dict[str, float]
    controller_type: str
    process_model: Dict[str, Any]
    robustness_analysis: Dict[str, Any]
    performance_prediction: Dict[str, float]
    lambda_sensitivity: Dict[str, Any]
    recommendations: List[str]
    execution_time: float

class LambdaTuner(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Lambda tuning algorithm for conservative, robust control

    Provides tuning based on desired closed-loop time constant (lambda),
    offering excellent robustness and smooth response characteristics.
    """

    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="lambda_tuner",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Lambda tuning for conservative, robust control",
                version="1.0.0",
                min_data_points=30,
                supports_realtime=False,
                tags=["classical", "lambda", "robust", "conservative"]
            )
            super().__init__(metadata)

        self.logger = logging.getLogger(__name__ + '.LambdaTuner')

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Lambda tuning"""
        errors = []

        # Check for required process model parameters
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

        # Check lambda value if user-specified
        if 'lambda_value' in data:
            if not isinstance(data['lambda_value'], (int, float)) or data['lambda_value'] <= 0:
                errors.append("Lambda value must be positive numeric value")

        # Check lambda strategy
        if 'lambda_strategy' in data:
            try:
                LambdaStrategy(data['lambda_strategy'])
            except ValueError:
                valid_strategies = [s.value for s in LambdaStrategy]
                errors.append(f"Lambda strategy must be one of: {valid_strategies}")

        # Check optimization mode
        if 'optimization_mode' in data:
            try:
                LambdaOptimizationMode(data['optimization_mode'])
            except ValueError:
                valid_modes = [m.value for m in LambdaOptimizationMode]
                errors.append(f"Optimization mode must be one of: {valid_modes}")

        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Lambda tuning algorithm"""
        start_time = time.time()

        # Extract parameters
        K = data['process_gain']
        L = data['dead_time']
        T = data['time_constant']
        controller_type = data.get('controller_type', 'dependent')
        lambda_strategy = LambdaStrategy(data.get('lambda_strategy', 'balanced'))
        optimization_mode = LambdaOptimizationMode(data.get('optimization_mode', 'balance'))
        user_lambda = data.get('lambda_value', None)

        try:
            # Process model analysis
            process_model = self._analyze_process_model(K, L, T)

            # Determine lambda value based on strategy
            lambda_value = self._determine_lambda_value(
                K, L, T, lambda_strategy, optimization_mode, user_lambda
            )

            # Calculate PID parameters using lambda tuning
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(K, L, T, lambda_value)
            else:
                pid_params = self._calculate_independent_params(K, L, T, lambda_value)

            # Robustness analysis
            robustness_analysis = self._analyze_robustness(K, L, T, lambda_value, pid_params)

            # Performance prediction
            performance_prediction = self._predict_performance(K, L, T, lambda_value, pid_params)

            # Lambda sensitivity analysis
            lambda_sensitivity = self._analyze_lambda_sensitivity(K, L, T, lambda_value)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                K, L, T, lambda_value, pid_params, lambda_strategy,
                optimization_mode, robustness_analysis, performance_prediction
            )

            execution_time = time.time() - start_time

            result = LambdaTuningResult(
                tuning_method="Lambda Tuning",
                lambda_strategy=lambda_strategy,
                optimization_mode=optimization_mode,
                lambda_value=lambda_value,
                parameters=pid_params,
                controller_type=controller_type,
                process_model=process_model,
                robustness_analysis=robustness_analysis,
                performance_prediction=performance_prediction,
                lambda_sensitivity=lambda_sensitivity,
                recommendations=recommendations,
                execution_time=execution_time
            )

            return {
                'success': True,
                'result': result,
                'method': 'lambda_tuning'
            }

        except Exception as e:
            self.logger.error(f"Lambda tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'lambda_tuning'
            }

    def _analyze_process_model(self, K: float, L: float, T: float) -> Dict[str, Any]:
        """Analyze process model characteristics"""

        # Calculate L/T ratio
        lt_ratio = L / T if T > 0 else 0

        # Determine process model type
        if abs(K) > 1000:  # Very high gain suggests integrator
            model_type = ProcessModelType.INTEGRATOR
        elif lt_ratio < 0.1 and T > 10:  # High order process approximation
            model_type = ProcessModelType.SOPDT
        else:
            model_type = ProcessModelType.FOPDT

        # Process characteristics
        dominant_time_constant = max(T, L)
        settling_time_open_loop = 4 * (T + L)

        # Lambda tuning suitability
        if lt_ratio <= 2.0:
            lambda_suitability = "excellent"
        elif lt_ratio <= 5.0:
            lambda_suitability = "good"
        else:
            lambda_suitability = "limited"

        return {
            'process_gain': K,
            'dead_time': L,
            'time_constant': T,
            'lt_ratio': lt_ratio,
            'model_type': model_type.value,
            'dominant_time_constant': dominant_time_constant,
            'settling_time_open_loop': settling_time_open_loop,
            'lambda_suitability': lambda_suitability
        }

    def _determine_lambda_value(self, K: float, L: float, T: float,
                               strategy: LambdaStrategy,
                               optimization_mode: LambdaOptimizationMode,
                               user_lambda: Optional[float]) -> float:
        """Determine lambda value based on strategy and optimization mode"""

        if strategy == LambdaStrategy.USER_SPECIFIED and user_lambda is not None:
            return user_lambda

        # Base lambda calculations based on strategy
        if strategy == LambdaStrategy.CONSERVATIVE:
            base_lambda = max(T, 3 * L)
        elif strategy == LambdaStrategy.BALANCED:
            base_lambda = max(T, 1.5 * L)
        elif strategy == LambdaStrategy.AGGRESSIVE:
            base_lambda = max(0.5 * T, L)
        else:  # AUTOMATIC
            # Automatically select based on process characteristics
            lt_ratio = L / T if T > 0 else 0
            if lt_ratio > 1.0:
                base_lambda = max(T, 2 * L)  # Conservative for high dead time
            elif lt_ratio > 0.3:
                base_lambda = max(T, 1.2 * L)  # Balanced
            else:
                base_lambda = T  # Can be more aggressive for low dead time

        # Adjust based on optimization mode
        if optimization_mode == LambdaOptimizationMode.ROBUSTNESS:
            lambda_value = 1.5 * base_lambda
        elif optimization_mode == LambdaOptimizationMode.PERFORMANCE:
            lambda_value = 0.7 * base_lambda
        else:  # BALANCE
            lambda_value = base_lambda

        # Apply reasonable bounds
        min_lambda = max(0.1, L)  # Minimum lambda should be at least dead time
        max_lambda = 10 * T  # Maximum reasonable lambda
        lambda_value = max(min_lambda, min(max_lambda, lambda_value))

        return lambda_value

    def _calculate_dependent_params(self, K: float, L: float, T: float,
                                  lambda_value: float) -> Dict[str, float]:
        """Calculate dependent PID parameters using lambda tuning"""

        if abs(K) < 1e-6:
            raise ValueError("Process gain is too small for reliable tuning")

        # Lambda tuning formulas for FOPDT process
        # Controller: Gc(s) = Kc * (1 + 1/(Ti*s) + Td*s)
        # Closed-loop: (lambda*s + 1) * e^(-L*s)

        # Calculate PID parameters
        Kc = T / (K * (lambda_value + L))
        Ti = T
        Td = L * T / (lambda_value + L)

        # Apply reasonable bounds
        Kc = max(0.01, min(100.0, Kc))
        Ti = max(0.01, min(9999.0, Ti))
        Td = max(0.0, min(99.99, Td))

        return {
            'Kp': float(Kc),
            'Ti': float(Ti),
            'Td': float(Td)
        }

    def _calculate_independent_params(self, K: float, L: float, T: float,
                                    lambda_value: float) -> Dict[str, float]:
        """Calculate independent PID parameters using lambda tuning"""

        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(K, L, T, lambda_value)

        # Convert to independent form
        Kc = dependent_params['Kp']
        Ti = dependent_params['Ti']
        Td = dependent_params['Td']

        # Independent form conversion
        Kp = Kc
        Ki = Kc / Ti if Ti > 0 else 0
        Kd = Kc * Td

        # Apply reasonable bounds
        Kp = max(0.01, min(100.0, Kp))
        Ki = max(0.0, min(10.0, Ki))
        Kd = max(0.0, min(10.0, Kd))

        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }

    def _analyze_robustness(self, K: float, L: float, T: float,
                          lambda_value: float, pid_params: Dict[str, float]) -> Dict[str, Any]:
        """Analyze robustness characteristics of lambda tuning"""

        # Lambda tuning typically provides excellent robustness
        pid_params['Kp']

        # Gain margin estimation for lambda tuning
        # Lambda tuning inherently provides good gain margins
        estimated_gain_margin = (lambda_value + L) / L if L > 0 else 5.0
        gain_margin_db = 20 * np.log10(estimated_gain_margin) if estimated_gain_margin > 0 else 20

        # Phase margin estimation for lambda tuning
        # Lambda tuning typically provides 45-60 degrees phase margin
        phase_margin_deg = 60 - 20 * (L / (lambda_value + L)) if (lambda_value + L) > 0 else 45
        phase_margin_deg = max(30, min(75, phase_margin_deg))

        # Robustness classification
        if gain_margin_db >= 12 and phase_margin_deg >= 50:
            robustness_level = 'very_high'
        elif gain_margin_db >= 8 and phase_margin_deg >= 40:
            robustness_level = 'high'
        elif gain_margin_db >= 6 and phase_margin_deg >= 30:
            robustness_level = 'medium'
        else:
            robustness_level = 'low'

        # Model uncertainty tolerance
        uncertainty_tolerance = min(0.5, lambda_value / (2 * T)) if T > 0 else 0.3

        # Load disturbance rejection
        disturbance_rejection = 'excellent' if lambda_value <= 2 * T else 'good' if lambda_value <= 4 * T else 'fair'

        return {
            'gain_margin_db': min(gain_margin_db, 40),  # Cap for display
            'phase_margin_deg': phase_margin_deg,
            'robustness_level': robustness_level,
            'model_uncertainty_tolerance': uncertainty_tolerance,
            'disturbance_rejection': disturbance_rejection,
            'stability_excellent': True,  # Lambda tuning provides inherent stability
            'noise_sensitivity': 'low'  # Generally low noise sensitivity
        }

    def _predict_performance(self, K: float, L: float, T: float,
                           lambda_value: float, pid_params: Dict[str, float]) -> Dict[str, float]:
        """Predict performance characteristics for lambda tuning"""

        # Lambda tuning performance characteristics
        # Generally provides overdamped response with no overshoot

        # Rise time estimation
        rise_time = 2.2 * (lambda_value + L)

        # Settling time estimation (to 2% of final value)
        settling_time = 4 * (lambda_value + L)

        # Overshoot (lambda tuning typically has minimal overshoot)
        overshoot_percent = max(0, 5 * (1 - lambda_value / T)) if T > 0 else 0
        overshoot_percent = min(10, overshoot_percent)  # Cap at 10%

        # IAE estimation for lambda tuning
        iae_factor = 1.2 + lambda_value / (2 * T) if T > 0 else 1.5
        iae_estimate = iae_factor * (T + L)

        # Performance index (0-1, higher is better)
        # Balance between speed and robustness
        speed_factor = T / (lambda_value + L) if (lambda_value + L) > 0 else 0.5
        robustness_factor = min(1.0, lambda_value / T) if T > 0 else 0.8
        performance_index = 0.3 * speed_factor + 0.7 * robustness_factor

        # Damping ratio (lambda tuning typically overdamped)
        damping_ratio = 1.0 + lambda_value / (4 * T) if T > 0 else 1.2
        damping_ratio = min(2.0, damping_ratio)  # Cap at critically overdamped

        # Control effort estimation
        control_effort_factor = 0.7  # Generally moderate control effort

        return {
            'predicted_rise_time': rise_time,
            'predicted_settling_time': settling_time,
            'predicted_overshoot_percent': overshoot_percent,
            'predicted_iae': iae_estimate,
            'performance_index': performance_index,
            'damping_ratio': damping_ratio,
            'control_effort_factor': control_effort_factor,
            'response_type': 'overdamped',
            'smooth_response': True
        }

    def _analyze_lambda_sensitivity(self, K: float, L: float, T: float,
                                  lambda_value: float) -> Dict[str, Any]:
        """Analyze sensitivity to lambda value changes"""

        # Test lambda variations
        lambda_variations = [0.5, 0.8, 1.0, 1.2, 1.5, 2.0]
        sensitivity_results = []

        base_params = self._calculate_dependent_params(K, L, T, lambda_value)
        base_settling_time = 4 * (lambda_value + L)

        for factor in lambda_variations:
            test_lambda = lambda_value * factor
            test_params = self._calculate_dependent_params(K, L, T, test_lambda)
            test_settling_time = 4 * (test_lambda + L)

            # Calculate parameter changes
            kc_change = (test_params['Kp'] - base_params['Kp']) / base_params['Kp'] * 100
            settling_change = (test_settling_time - base_settling_time) / base_settling_time * 100

            sensitivity_results.append({
                'lambda_factor': factor,
                'lambda_value': test_lambda,
                'kc_change_percent': kc_change,
                'settling_time_change_percent': settling_change
            })

        # Calculate overall sensitivity
        kc_sensitivity = np.std([r['kc_change_percent'] for r in sensitivity_results])
        settling_sensitivity = np.std([r['settling_time_change_percent'] for r in sensitivity_results])

        # Sensitivity classification
        if kc_sensitivity < 20 and settling_sensitivity < 30:
            sensitivity_level = 'low'
        elif kc_sensitivity < 40 and settling_sensitivity < 50:
            sensitivity_level = 'medium'
        else:
            sensitivity_level = 'high'

        # Optimal lambda range
        min_recommended = max(L, 0.5 * T)
        max_recommended = min(5 * T, 4 * lambda_value)

        return {
            'sensitivity_level': sensitivity_level,
            'kc_sensitivity': kc_sensitivity,
            'settling_time_sensitivity': settling_sensitivity,
            'sensitivity_results': sensitivity_results,
            'optimal_lambda_range': (min_recommended, max_recommended),
            'lambda_tuning_flexibility': 'high'  # Easy to adjust lambda for different trade-offs
        }

    def _generate_recommendations(self, K: float, L: float, T: float,
                                lambda_value: float, pid_params: Dict[str, float],
                                strategy: LambdaStrategy,
                                optimization_mode: LambdaOptimizationMode,
                                robustness_analysis: Dict[str, Any],
                                performance_prediction: Dict[str, float]) -> List[str]:
        """Generate lambda tuning recommendations"""
        recommendations = []

        lt_ratio = L / T if T > 0 else 0

        # Lambda strategy recommendations
        if strategy == LambdaStrategy.USER_SPECIFIED:
            recommendations.append(f"User-specified lambda = {lambda_value:.2f} - monitor performance and adjust if needed")
        elif strategy == LambdaStrategy.CONSERVATIVE:
            recommendations.append("Conservative lambda strategy - excellent robustness with slower response")
        elif strategy == LambdaStrategy.BALANCED:
            recommendations.append("Balanced lambda strategy - good compromise between speed and robustness")
        elif strategy == LambdaStrategy.AGGRESSIVE:
            recommendations.append("Aggressive lambda strategy - faster response but monitor for oscillations")
        else:
            recommendations.append("Automatic lambda selection - optimized for process characteristics")

        # Optimization mode recommendations
        if optimization_mode == LambdaOptimizationMode.ROBUSTNESS:
            recommendations.append("Robustness-optimized lambda - ideal for uncertain or varying process conditions")
        elif optimization_mode == LambdaOptimizationMode.PERFORMANCE:
            recommendations.append("Performance-optimized lambda - faster response but verify robustness")
        else:
            recommendations.append("Balanced optimization - good trade-off between performance and robustness")

        # Robustness recommendations
        if robustness_analysis['robustness_level'] == 'very_high':
            recommendations.append("Excellent robustness - suitable for industrial applications with model uncertainty")
        elif robustness_analysis['robustness_level'] == 'high':
            recommendations.append("High robustness - good for most industrial applications")

        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] < 2:
            recommendations.append("Minimal overshoot predicted - excellent for applications requiring stable response")

        if performance_prediction['predicted_settling_time'] > 8 * (T + L):
            recommendations.append("Conservative settling time - consider reducing lambda for faster response if acceptable")

        # Lambda value recommendations
        lambda_to_tau_ratio = lambda_value / T if T > 0 else 1
        if lambda_to_tau_ratio < 0.5:
            recommendations.append("Aggressive lambda (< 0.5*τ) - monitor for stability and robustness")
        elif lambda_to_tau_ratio > 3:
            recommendations.append("Conservative lambda (> 3*τ) - very stable but slow response")
        else:
            recommendations.append("Well-balanced lambda - good choice for most applications")

        # Process-specific recommendations
        if lt_ratio > 1.0:
            recommendations.append("High dead time process - lambda tuning excellent choice for robustness")
        elif lt_ratio < 0.1:
            recommendations.append("Low dead time process - could consider more aggressive lambda for faster response")

        if abs(K) > 5:
            recommendations.append("High process gain - lambda tuning provides good sensitivity management")

        # Implementation recommendations
        recommendations.append("Lambda tuning provides inherently stable and smooth response")
        recommendations.append("Easy to retune by adjusting lambda value based on performance requirements")

        if robustness_analysis['disturbance_rejection'] == 'excellent':
            recommendations.append("Excellent disturbance rejection - well-suited for processes with load variations")

        # Lambda adjustment recommendations
        recommendations.append("Decrease lambda for faster response, increase for better robustness")
        recommendations.append("Lambda tuning ideal for applications prioritizing stability over speed")

        return recommendations

# Register Lambda tuning algorithm
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(LambdaTuner)
        logger.info("Lambda tuning algorithm registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Lambda tuning algorithm: {e}")

# Export classes
__all__ = [
    'LambdaTuner',
    'LambdaTuningResult',
    'LambdaStrategy',
    'LambdaOptimizationMode',
    'ProcessModelType'
]

logger.info("Lambda tuning method implementation completed")
