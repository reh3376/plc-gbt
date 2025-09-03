#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Cohen-Coon Tuning Implementation
==========================================================

Implementation of Cohen-Coon PID tuning method for dead-time dominant processes.
Cohen-Coon tuning provides better performance than Ziegler-Nichols for processes
with significant dead time (L/T > 0.3), offering improved stability and response.

Key Features:
- Optimized for dead-time dominant processes
- Better stability margins than Ziegler-Nichols
- Reduced overshoot and improved settling time
- Automatic L/T ratio analysis for method suitability

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Tuple

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

class CCResponseType(Enum):
    """Cohen-Coon response characteristics"""
    STANDARD = "standard"
    CONSERVATIVE = "conservative"
    AGGRESSIVE = "aggressive"

@dataclass
class CohenCoonResult:
    """Cohen-Coon tuning result"""
    tuning_method: str
    response_type: CCResponseType
    parameters: Dict[str, float]
    controller_type: str
    process_characteristics: Dict[str, float]
    suitability_analysis: Dict[str, Any]
    stability_analysis: Dict[str, Any]
    performance_prediction: Dict[str, float]
    recommendations: List[str]
    execution_time: float

class CohenCoonTuner(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Cohen-Coon PID tuning algorithm

    Specifically designed for processes with significant dead time.
    Provides better performance than Ziegler-Nichols for dead-time
    dominant processes (L/T > 0.3).
    """

    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="cohen_coon_tuner",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Cohen-Coon tuning for dead-time dominant processes",
                version="1.0.0",
                min_data_points=50,
                supports_realtime=False,
                tags=["classical", "cohen_coon", "dead_time", "FOPDT"]
            )
            super().__init__(metadata)

        self.logger = logging.getLogger(__name__ + '.CohenCoonTuner')

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Cohen-Coon tuning"""
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

        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")

        # Check response type
        if 'response_type' in data:
            try:
                CCResponseType(data['response_type'])
            except ValueError:
                valid_types = [t.value for t in CCResponseType]
                errors.append(f"Response type must be one of: {valid_types}")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Cohen-Coon tuning algorithm"""
        start_time = time.time()

        # Extract parameters
        K = data['process_gain']
        L = data['dead_time']
        T = data['time_constant']
        controller_type = data.get('controller_type', 'dependent')
        response_type = CCResponseType(data.get('response_type', 'standard'))

        try:
            # Process characteristics analysis
            process_characteristics = self._analyze_process_characteristics(K, L, T)

            # Suitability analysis for Cohen-Coon method
            suitability_analysis = self._analyze_method_suitability(K, L, T)

            # Calculate Cohen-Coon parameters
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(K, L, T, response_type)
            else:
                pid_params = self._calculate_independent_params(K, L, T, response_type)

            # Stability analysis
            stability_analysis = self._analyze_stability(K, L, T, pid_params)

            # Performance prediction
            performance_prediction = self._predict_performance(K, L, T, pid_params, response_type)

            # Generate recommendations
            recommendations = self._generate_recommendations(
                K, L, T, pid_params, suitability_analysis, stability_analysis, performance_prediction
            )

            execution_time = time.time() - start_time

            result = CohenCoonResult(
                tuning_method="Cohen-Coon",
                response_type=response_type,
                parameters=pid_params,
                controller_type=controller_type,
                process_characteristics=process_characteristics,
                suitability_analysis=suitability_analysis,
                stability_analysis=stability_analysis,
                performance_prediction=performance_prediction,
                recommendations=recommendations,
                execution_time=execution_time
            )

            return {
                'success': True,
                'result': result,
                'method': 'cohen_coon'
            }

        except Exception as e:
            self.logger.error(f"Cohen-Coon tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'cohen_coon'
            }

    def _analyze_process_characteristics(self, K: float, L: float, T: float) -> Dict[str, float]:
        """Analyze process characteristics for Cohen-Coon suitability"""

        # Calculate L/T ratio
        lt_ratio = L / T if T > 0 else 0

        # Classify process type
        if lt_ratio < 0.1:
            process_type = "fast_no_deadtime"
        elif lt_ratio < 0.3:
            process_type = "moderate_deadtime"
        elif lt_ratio < 1.0:
            process_type = "significant_deadtime"
        else:
            process_type = "deadtime_dominant"

        # Calculate process settling characteristics
        open_loop_settling_time = 4 * (T + L)
        dominant_time_constant = max(T, L)

        return {
            'process_gain': K,
            'dead_time': L,
            'time_constant': T,
            'lt_ratio': lt_ratio,
            'process_type': process_type,
            'open_loop_settling_time': open_loop_settling_time,
            'dominant_time_constant': dominant_time_constant
        }

    def _analyze_method_suitability(self, K: float, L: float, T: float) -> Dict[str, Any]:
        """Analyze suitability of Cohen-Coon method for this process"""

        lt_ratio = L / T if T > 0 else 0

        # Cohen-Coon is most suitable for processes with significant dead time
        if lt_ratio >= 0.3:
            suitability = "excellent"
            reason = "Cohen-Coon is specifically designed for dead-time dominant processes"
        elif lt_ratio >= 0.1:
            suitability = "good"
            reason = "Cohen-Coon provides good performance for moderate dead time processes"
        else:
            suitability = "poor"
            reason = "Ziegler-Nichols or IMC may be better for low dead time processes"

        # Additional suitability factors
        factors = {
            'lt_ratio_suitable': lt_ratio >= 0.1,
            'gain_reasonable': 0.1 <= abs(K) <= 10.0,
            'time_constants_reasonable': T >= 0.1 and L >= 0,
            'first_order_assumption': True  # Cohen-Coon assumes FOPDT model
        }

        overall_suitable = all(factors.values()) and suitability in ['good', 'excellent']

        return {
            'suitability': suitability,
            'reason': reason,
            'lt_ratio': lt_ratio,
            'suitability_factors': factors,
            'overall_suitable': overall_suitable,
            'alternative_methods': self._suggest_alternatives(lt_ratio, K, T, L)
        }

    def _suggest_alternatives(self, lt_ratio: float, K: float, T: float, L: float) -> List[str]:
        """Suggest alternative tuning methods based on process characteristics"""
        alternatives = []

        if lt_ratio < 0.1:
            alternatives.append("Ziegler-Nichols Process Reaction - better for low dead time")
            alternatives.append("IMC tuning - provides smooth response")

        if abs(K) > 5.0:
            alternatives.append("IMC with lambda detuning - better for high gain processes")

        if T > 100 or L > 50:
            alternatives.append("Lambda tuning - more conservative for slow processes")

        if lt_ratio > 2.0:
            alternatives.append("Model Predictive Control - better for extreme dead time")

        return alternatives

    def _calculate_dependent_params(self, K: float, L: float, T: float,
                                  response_type: CCResponseType) -> Dict[str, float]:
        """Calculate dependent (positional) PID parameters using Cohen-Coon rules"""

        if T <= 0:
            raise ValueError("Time constant must be positive")

        # Cohen-Coon parameter calculations
        lt_ratio = L / T

        # Base Cohen-Coon formulas
        if response_type == CCResponseType.STANDARD:
            # Standard Cohen-Coon rules
            Kc_factor = (1.35 + 0.25 * lt_ratio) / (K * lt_ratio)
            Ti_factor = 2.5 + 0.6 * lt_ratio
            Td_factor = 0.37 - 0.37 * lt_ratio
        elif response_type == CCResponseType.CONSERVATIVE:
            # More conservative settings
            Kc_factor = (1.0 + 0.2 * lt_ratio) / (K * lt_ratio)
            Ti_factor = 3.0 + 0.8 * lt_ratio
            Td_factor = 0.3 - 0.3 * lt_ratio
        else:  # AGGRESSIVE
            # More aggressive settings
            Kc_factor = (1.7 + 0.3 * lt_ratio) / (K * lt_ratio)
            Ti_factor = 2.0 + 0.4 * lt_ratio
            Td_factor = 0.4 - 0.4 * lt_ratio

        # Calculate parameters
        if lt_ratio > 0:
            Kc = Kc_factor * T
            Ti = Ti_factor * L
            Td = max(Td_factor * L, 0.0)  # Ensure non-negative derivative time
        else:
            # Fallback for zero dead time (use simplified rules)
            Kc = 1.0 / K
            Ti = T
            Td = 0.0

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
                                    response_type: CCResponseType) -> Dict[str, float]:
        """Calculate independent (parallel) PID parameters using Cohen-Coon rules"""

        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(K, L, T, response_type)

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

    def _analyze_stability(self, K: float, L: float, T: float,
                          pid_params: Dict[str, float]) -> Dict[str, Any]:
        """Analyze closed-loop stability for Cohen-Coon tuned system"""

        lt_ratio = L / T if T > 0 else 0
        Kc = pid_params['Kp']

        # Gain margin estimation for FOPDT with PID
        # Using approximation for first-order plus dead time system
        open_loop_gain = abs(K * Kc)

        if open_loop_gain > 0:
            gain_margin = 1.0 / open_loop_gain
            gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else 0
        else:
            gain_margin = float('inf')
            gain_margin_db = 60  # Cap for display

        # Phase margin estimation (empirical correlation for FOPDT)
        # Cohen-Coon typically provides better phase margin than ZN
        base_phase_margin = 45.0  # Cohen-Coon baseline
        phase_margin_deg = base_phase_margin - 30 * lt_ratio
        phase_margin_deg = max(phase_margin_deg, 10.0)  # Minimum reasonable value

        # Robustness assessment
        if gain_margin_db >= 12 and phase_margin_deg >= 45:
            robustness_level = 'high'
        elif gain_margin_db >= 6 and phase_margin_deg >= 30:
            robustness_level = 'medium'
        else:
            robustness_level = 'low'

        # Stability classification
        stable = gain_margin_db >= 6 and phase_margin_deg >= 30

        return {
            'gain_margin': gain_margin,
            'gain_margin_db': min(gain_margin_db, 60),  # Cap for display
            'phase_margin_deg': phase_margin_deg,
            'robustness_level': robustness_level,
            'stable': stable,
            'lt_ratio': lt_ratio,
            'open_loop_gain': open_loop_gain
        }

    def _predict_performance(self, K: float, L: float, T: float,
                           pid_params: Dict[str, float],
                           response_type: CCResponseType) -> Dict[str, float]:
        """Predict closed-loop performance characteristics"""

        lt_ratio = L / T if T > 0 else 0

        # Performance predictions based on Cohen-Coon characteristics
        # Cohen-Coon typically provides less overshoot than ZN

        if response_type == CCResponseType.STANDARD:
            base_overshoot = 15.0  # Lower than ZN
            settling_factor = 5.0
            rise_factor = 1.2
        elif response_type == CCResponseType.CONSERVATIVE:
            base_overshoot = 5.0
            settling_factor = 7.0
            rise_factor = 2.0
        else:  # AGGRESSIVE
            base_overshoot = 25.0
            settling_factor = 4.0
            rise_factor = 0.8

        # Adjust for dead time ratio
        overshoot_percent = base_overshoot * (1 + 0.5 * lt_ratio)
        settling_time = settling_factor * (T + L)
        rise_time = rise_factor * (T + L)

        # IAE estimation (Integral Absolute Error)
        # Cohen-Coon typically gives better IAE than ZN for dead time processes
        iae_factor = 1.5 + 2.0 * lt_ratio  # Increases with dead time
        iae_estimate = iae_factor * (T + L)

        # Performance index (0-1, higher is better)
        # Accounts for overshoot, settling time, and dead time challenges
        performance_index = max(0, 1 - overshoot_percent/50 - settling_time/(8*(T+L)) - lt_ratio/2)

        # Damping ratio estimation
        damping_ratio = 0.7 - 0.3 * lt_ratio
        damping_ratio = max(0.3, min(1.0, damping_ratio))

        return {
            'predicted_overshoot_percent': min(overshoot_percent, 80),
            'predicted_settling_time': settling_time,
            'predicted_rise_time': rise_time,
            'predicted_iae': iae_estimate,
            'performance_index': performance_index,
            'damping_ratio': damping_ratio,
            'lt_ratio_impact': lt_ratio
        }

    def _generate_recommendations(self, K: float, L: float, T: float,
                                pid_params: Dict[str, float],
                                suitability_analysis: Dict[str, Any],
                                stability_analysis: Dict[str, Any],
                                performance_prediction: Dict[str, float]) -> List[str]:
        """Generate tuning recommendations"""
        recommendations = []

        lt_ratio = L / T if T > 0 else 0

        # Method suitability recommendations
        if suitability_analysis['suitability'] == 'excellent':
            recommendations.append("Excellent choice: Cohen-Coon is ideal for this dead-time dominant process")
        elif suitability_analysis['suitability'] == 'good':
            recommendations.append("Good choice: Cohen-Coon should provide better performance than Ziegler-Nichols")
        else:
            recommendations.append("Consider alternative methods: Process has low dead time")
            recommendations.extend(suitability_analysis['alternative_methods'][:2])  # Top 2 alternatives

        # Stability recommendations
        if stability_analysis['robustness_level'] == 'low':
            recommendations.append("Low robustness - consider more conservative settings")
        elif stability_analysis['robustness_level'] == 'high':
            recommendations.append("High robustness - tuning should be stable in industrial conditions")

        if stability_analysis['gain_margin_db'] < 6:
            recommendations.append("Low gain margin - reduce proportional gain by 20-30%")

        if stability_analysis['phase_margin_deg'] < 30:
            recommendations.append("Poor phase margin - reduce derivative action or increase lambda")

        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] > 20:
            recommendations.append("High overshoot predicted - consider conservative variant")

        if performance_prediction['predicted_settling_time'] > 10 * (T + L):
            recommendations.append("Slow settling predicted - may need more aggressive tuning")

        # Dead time specific recommendations
        if lt_ratio > 1.0:
            recommendations.append("Very high dead time - consider predictive control strategies")
        elif lt_ratio > 0.5:
            recommendations.append("High dead time - monitor for oscillations and detune if necessary")

        # Process specific recommendations
        if abs(K) > 5.0:
            recommendations.append("High process gain - monitor for sensitivity to disturbances")

        if T > 100:
            recommendations.append("Slow process - consider operator training for manual override procedures")

        # General industrial recommendations
        recommendations.append("Test tuning in small increments and validate performance")
        recommendations.append("Cohen-Coon provides better dead time compensation than Ziegler-Nichols")

        if lt_ratio >= 0.3:
            recommendations.append("Consider feedforward control to improve disturbance rejection")

        return recommendations

# Register Cohen-Coon algorithm
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(CohenCoonTuner)
        logger.info("Cohen-Coon algorithm registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Cohen-Coon algorithm: {e}")

# Export classes
__all__ = [
    'CohenCoonTuner',
    'CohenCoonResult',
    'CCResponseType'
]

logger.info("Cohen-Coon tuning method implementation completed")
