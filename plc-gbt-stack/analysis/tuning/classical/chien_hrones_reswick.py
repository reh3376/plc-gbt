#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Chien-Hrones-Reswick Tuning Implementation
=====================================================================

Implementation of Chien-Hrones-Reswick (CHR) PID tuning method with multiple
optimization criteria. CHR provides tuning rules optimized for different
performance objectives including setpoint tracking and disturbance rejection.

Key Features:
- Multiple optimization criteria (0%, 20% overshoot, disturbance rejection)
- Setpoint vs disturbance response optimization
- Load disturbance rejection capabilities
- Various controller configurations (P, PI, PID)

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

class CHROptimizationCriteria(Enum):
    """Chien-Hrones-Reswick optimization criteria"""
    NO_OVERSHOOT = "no_overshoot"
    TWENTY_PERCENT_OVERSHOOT = "twenty_percent_overshoot"
    MINIMUM_IAE = "minimum_iae"
    DISTURBANCE_REJECTION = "disturbance_rejection"

class CHRControllerType(Enum):
    """CHR controller configurations"""
    P_ONLY = "p_only"
    PI = "pi"
    PID = "pid"

class CHRResponseType(Enum):
    """CHR response optimization type"""
    SETPOINT = "setpoint"
    DISTURBANCE = "disturbance"

@dataclass
class CHRTuningResult:
    """Chien-Hrones-Reswick tuning result"""
    tuning_method: str
    optimization_criteria: CHROptimizationCriteria
    controller_config: CHRControllerType
    response_type: CHRResponseType
    parameters: Dict[str, float]
    controller_type: str
    process_characteristics: Dict[str, float]
    performance_prediction: Dict[str, float]
    optimization_analysis: Dict[str, Any]
    recommendations: List[str]
    execution_time: float

class ChienHronesReswickTuner(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Chien-Hrones-Reswick PID tuning algorithm

    Provides tuning rules optimized for different performance criteria
    including setpoint tracking and disturbance rejection with various
    overshoot specifications.
    """

    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="chien_hrones_reswick_tuner",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Chien-Hrones-Reswick multi-criteria PID tuning method",
                version="1.0.0",
                min_data_points=50,
                supports_realtime=False,
                tags=["classical", "chr", "multi_criteria", "optimization"]
            )
            super().__init__(metadata)

        self.logger = logging.getLogger(__name__ + '.ChienHronesReswickTuner')

    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Chien-Hrones-Reswick tuning"""
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

        # Check optimization criteria
        if 'optimization_criteria' in data:
            try:
                CHROptimizationCriteria(data['optimization_criteria'])
            except ValueError:
                valid_criteria = [c.value for c in CHROptimizationCriteria]
                errors.append(f"Optimization criteria must be one of: {valid_criteria}")

        # Check controller configuration
        if 'controller_config' in data:
            try:
                CHRControllerType(data['controller_config'])
            except ValueError:
                valid_configs = [c.value for c in CHRControllerType]
                errors.append(f"Controller config must be one of: {valid_configs}")

        # Check response type
        if 'response_type' in data:
            try:
                CHRResponseType(data['response_type'])
            except ValueError:
                valid_types = [t.value for t in CHRResponseType]
                errors.append(f"Response type must be one of: {valid_types}")

        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")

        return len(errors) == 0, errors

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Chien-Hrones-Reswick tuning algorithm"""
        start_time = time.time()

        # Extract parameters
        K = data['process_gain']
        L = data['dead_time']
        T = data['time_constant']
        controller_type = data.get('controller_type', 'dependent')
        optimization_criteria = CHROptimizationCriteria(data.get('optimization_criteria', 'twenty_percent_overshoot'))
        controller_config = CHRControllerType(data.get('controller_config', 'pid'))
        response_type = CHRResponseType(data.get('response_type', 'setpoint'))

        try:
            # Process characteristics analysis
            process_characteristics = self._analyze_process_characteristics(K, L, T)

            # Calculate CHR parameters based on criteria and configuration
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(
                    K, L, T, optimization_criteria, controller_config, response_type
                )
            else:
                pid_params = self._calculate_independent_params(
                    K, L, T, optimization_criteria, controller_config, response_type
                )

            # Performance prediction based on optimization criteria
            performance_prediction = self._predict_performance(
                K, L, T, pid_params, optimization_criteria, response_type
            )

            # Optimization analysis
            optimization_analysis = self._analyze_optimization(
                K, L, T, pid_params, optimization_criteria, controller_config, response_type
            )

            # Generate recommendations
            recommendations = self._generate_recommendations(
                K, L, T, pid_params, optimization_criteria, controller_config,
                response_type, performance_prediction, optimization_analysis
            )

            execution_time = time.time() - start_time

            result = CHRTuningResult(
                tuning_method="Chien-Hrones-Reswick",
                optimization_criteria=optimization_criteria,
                controller_config=controller_config,
                response_type=response_type,
                parameters=pid_params,
                controller_type=controller_type,
                process_characteristics=process_characteristics,
                performance_prediction=performance_prediction,
                optimization_analysis=optimization_analysis,
                recommendations=recommendations,
                execution_time=execution_time
            )

            return {
                'success': True,
                'result': result,
                'method': 'chien_hrones_reswick'
            }

        except Exception as e:
            self.logger.error(f"Chien-Hrones-Reswick tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'chien_hrones_reswick'
            }

    def _analyze_process_characteristics(self, K: float, L: float, T: float) -> Dict[str, float]:
        """Analyze process characteristics for CHR tuning"""

        # Calculate L/T ratio
        lt_ratio = L / T if T > 0 else 0

        # Process classification based on L/T ratio
        if lt_ratio < 0.1:
            process_class = "lag_dominant"
        elif lt_ratio < 0.5:
            process_class = "balanced"
        elif lt_ratio < 1.0:
            process_class = "delay_dominant"
        else:
            process_class = "severe_delay"

        # CHR applicability assessment
        chr_suitability = "excellent" if 0.1 <= lt_ratio <= 2.0 else "good" if lt_ratio <= 3.0 else "limited"

        # Process dynamics
        settling_time_estimate = 4 * (T + L)
        response_speed = "fast" if settling_time_estimate < 30 else "medium" if settling_time_estimate < 120 else "slow"

        return {
            'process_gain': K,
            'dead_time': L,
            'time_constant': T,
            'lt_ratio': lt_ratio,
            'process_class': process_class,
            'chr_suitability': chr_suitability,
            'settling_time_estimate': settling_time_estimate,
            'response_speed': response_speed
        }

    def _calculate_dependent_params(self, K: float, L: float, T: float,
                                  criteria: CHROptimizationCriteria,
                                  config: CHRControllerType,
                                  response_type: CHRResponseType) -> Dict[str, float]:
        """Calculate dependent PID parameters using CHR rules"""

        if T <= 0:
            raise ValueError("Time constant must be positive")

        # CHR tuning rules - get the appropriate rule set
        rule = self._get_chr_rule(criteria, config, response_type)

        # Calculate parameters based on CHR formulas
        if config == CHRControllerType.P_ONLY:
            Kc = rule['Kc_factor'] * T / (K * L) if L > 0 else rule['Kc_factor'] / K
            Ti = float('inf')  # No integral action
            Td = 0.0
        elif config == CHRControllerType.PI:
            Kc = rule['Kc_factor'] * T / (K * L) if L > 0 else rule['Kc_factor'] / K
            Ti = rule['Ti_factor'] * L if L > 0 else rule['Ti_factor'] * T
            Td = 0.0
        else:  # PID
            Kc = rule['Kc_factor'] * T / (K * L) if L > 0 else rule['Kc_factor'] / K
            Ti = rule['Ti_factor'] * L if L > 0 else rule['Ti_factor'] * T
            Td = rule['Td_factor'] * L if L > 0 else 0.0

        # Apply reasonable bounds
        Kc = max(0.01, min(100.0, Kc))
        Ti = max(0.01, min(9999.0, Ti)) if Ti != float('inf') else float('inf')
        Td = max(0.0, min(99.99, Td))

        return {
            'Kp': float(Kc),
            'Ti': float(Ti) if Ti != float('inf') else 0.0,  # Convert inf to 0 for display
            'Td': float(Td)
        }

    def _calculate_independent_params(self, K: float, L: float, T: float,
                                    criteria: CHROptimizationCriteria,
                                    config: CHRControllerType,
                                    response_type: CHRResponseType) -> Dict[str, float]:
        """Calculate independent PID parameters using CHR rules"""

        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(K, L, T, criteria, config, response_type)

        # Convert to independent form
        Kc = dependent_params['Kp']
        Ti = dependent_params['Ti']
        Td = dependent_params['Td']

        # Independent form conversion
        Kp = Kc
        if config == CHRControllerType.P_ONLY:
            Ki = 0.0
        else:
            Ki = Kc / Ti if Ti > 0 else 0.0

        if config == CHRControllerType.PID:
            Kd = Kc * Td
        else:
            Kd = 0.0

        # Apply reasonable bounds
        Kp = max(0.01, min(100.0, Kp))
        Ki = max(0.0, min(10.0, Ki))
        Kd = max(0.0, min(10.0, Kd))

        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }

    def _get_chr_rule(self, criteria: CHROptimizationCriteria,
                     config: CHRControllerType,
                     response_type: CHRResponseType) -> Dict[str, float]:
        """Get CHR tuning rule factors based on criteria and configuration"""

        # CHR tuning rules table
        # Format: {criteria: {config: {response_type: {Kc_factor, Ti_factor, Td_factor}}}}

        chr_rules = {
            CHROptimizationCriteria.NO_OVERSHOOT: {
                CHRControllerType.P_ONLY: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.3, 'Ti_factor': 0, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.3, 'Ti_factor': 0, 'Td_factor': 0}
                },
                CHRControllerType.PI: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.35, 'Ti_factor': 1.2, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.6, 'Ti_factor': 4.0, 'Td_factor': 0}
                },
                CHRControllerType.PID: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.6, 'Ti_factor': 1.0, 'Td_factor': 0.5},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.95, 'Ti_factor': 2.4, 'Td_factor': 0.42}
                }
            },
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: {
                CHRControllerType.P_ONLY: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.7, 'Ti_factor': 0, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.7, 'Ti_factor': 0, 'Td_factor': 0}
                },
                CHRControllerType.PI: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.6, 'Ti_factor': 1.0, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.7, 'Ti_factor': 2.3, 'Td_factor': 0}
                },
                CHRControllerType.PID: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.95, 'Ti_factor': 1.4, 'Td_factor': 0.47},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 1.2, 'Ti_factor': 2.0, 'Td_factor': 0.42}
                }
            },
            CHROptimizationCriteria.MINIMUM_IAE: {
                CHRControllerType.P_ONLY: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.5, 'Ti_factor': 0, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.5, 'Ti_factor': 0, 'Td_factor': 0}
                },
                CHRControllerType.PI: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.45, 'Ti_factor': 0.8, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.65, 'Ti_factor': 3.0, 'Td_factor': 0}
                },
                CHRControllerType.PID: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.75, 'Ti_factor': 1.2, 'Td_factor': 0.4},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 1.0, 'Ti_factor': 2.2, 'Td_factor': 0.4}
                }
            },
            CHROptimizationCriteria.DISTURBANCE_REJECTION: {
                CHRControllerType.P_ONLY: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.3, 'Ti_factor': 0, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 0.8, 'Ti_factor': 0, 'Td_factor': 0}
                },
                CHRControllerType.PI: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.35, 'Ti_factor': 1.2, 'Td_factor': 0},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 1.0, 'Ti_factor': 3.5, 'Td_factor': 0}
                },
                CHRControllerType.PID: {
                    CHRResponseType.SETPOINT: {'Kc_factor': 0.6, 'Ti_factor': 1.0, 'Td_factor': 0.5},
                    CHRResponseType.DISTURBANCE: {'Kc_factor': 1.35, 'Ti_factor': 2.5, 'Td_factor': 0.37}
                }
            }
        }

        return chr_rules[criteria][config][response_type]

    def _predict_performance(self, K: float, L: float, T: float,
                           pid_params: Dict[str, float],
                           criteria: CHROptimizationCriteria,
                           response_type: CHRResponseType) -> Dict[str, float]:
        """Predict performance characteristics based on CHR criteria"""

        lt_ratio = L / T if T > 0 else 0

        # Performance predictions based on optimization criteria
        if criteria == CHROptimizationCriteria.NO_OVERSHOOT:
            overshoot_percent = 0.0
            settling_time_factor = 8.0
            rise_time_factor = 3.0
            iae_factor = 2.0
        elif criteria == CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT:
            overshoot_percent = 20.0
            settling_time_factor = 5.0
            rise_time_factor = 1.5
            iae_factor = 1.2
        elif criteria == CHROptimizationCriteria.MINIMUM_IAE:
            overshoot_percent = 10.0
            settling_time_factor = 6.0
            rise_time_factor = 2.0
            iae_factor = 1.0  # Optimized for minimum IAE
        else:  # DISTURBANCE_REJECTION
            overshoot_percent = 15.0
            settling_time_factor = 6.0
            rise_time_factor = 2.5
            iae_factor = 1.5

        # Adjust for process characteristics
        settling_time = settling_time_factor * (T + L)
        rise_time = rise_time_factor * (T + L)
        iae_estimate = iae_factor * (T + L) * (1 + lt_ratio)

        # Performance index based on criteria
        if criteria == CHROptimizationCriteria.NO_OVERSHOOT:
            performance_index = 1.0 - settling_time / (10 * (T + L))  # Penalize slow response
        elif criteria == CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT:
            performance_index = 0.8 + 0.2 * (1 - settling_time / (8 * (T + L)))  # Balance speed/overshoot
        elif criteria == CHROptimizationCriteria.MINIMUM_IAE:
            performance_index = max(0, 1 - iae_estimate / (3 * (T + L)))  # Optimize for IAE
        else:  # DISTURBANCE_REJECTION
            performance_index = 0.9 if response_type == CHRResponseType.DISTURBANCE else 0.7

        # Damping characteristics
        damping_ratios = {
            CHROptimizationCriteria.NO_OVERSHOOT: 1.0,
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: 0.45,
            CHROptimizationCriteria.MINIMUM_IAE: 0.7,
            CHROptimizationCriteria.DISTURBANCE_REJECTION: 0.6
        }
        damping_ratio = damping_ratios[criteria]

        return {
            'predicted_overshoot_percent': overshoot_percent,
            'predicted_settling_time': settling_time,
            'predicted_rise_time': rise_time,
            'predicted_iae': iae_estimate,
            'performance_index': max(0, min(1, performance_index)),
            'damping_ratio': damping_ratio,
            'optimization_target': criteria.value
        }

    def _analyze_optimization(self, K: float, L: float, T: float,
                            pid_params: Dict[str, float],
                            criteria: CHROptimizationCriteria,
                            config: CHRControllerType,
                            response_type: CHRResponseType) -> Dict[str, Any]:
        """Analyze the optimization characteristics"""

        lt_ratio = L / T if T > 0 else 0

        # Optimization target analysis
        target_analysis = {
            'primary_objective': self._get_primary_objective(criteria),
            'secondary_benefits': self._get_secondary_benefits(criteria, response_type),
            'trade_offs': self._get_trade_offs(criteria, config)
        }

        # Suitability assessment
        suitability_factors = {
            'process_type_match': self._assess_process_match(criteria, lt_ratio),
            'controller_config_optimal': self._assess_config_optimality(criteria, config),
            'response_type_appropriate': self._assess_response_appropriateness(criteria, response_type)
        }

        overall_suitability = np.mean(list(suitability_factors.values()))

        # Performance vs robustness trade-off
        robustness_scores = {
            CHROptimizationCriteria.NO_OVERSHOOT: 0.9,
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: 0.6,
            CHROptimizationCriteria.MINIMUM_IAE: 0.7,
            CHROptimizationCriteria.DISTURBANCE_REJECTION: 0.8
        }

        speed_scores = {
            CHROptimizationCriteria.NO_OVERSHOOT: 0.4,
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: 0.9,
            CHROptimizationCriteria.MINIMUM_IAE: 0.8,
            CHROptimizationCriteria.DISTURBANCE_REJECTION: 0.6
        }

        return {
            'target_analysis': target_analysis,
            'suitability_factors': suitability_factors,
            'overall_suitability': overall_suitability,
            'robustness_score': robustness_scores[criteria],
            'speed_score': speed_scores[criteria],
            'optimization_balance': 'robustness' if robustness_scores[criteria] > speed_scores[criteria] else 'speed',
            'criteria_achievement': self._estimate_criteria_achievement(criteria, config, lt_ratio)
        }

    def _get_primary_objective(self, criteria: CHROptimizationCriteria) -> str:
        """Get primary optimization objective"""
        objectives = {
            CHROptimizationCriteria.NO_OVERSHOOT: "Eliminate overshoot for stable response",
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: "Balance speed and stability with controlled overshoot",
            CHROptimizationCriteria.MINIMUM_IAE: "Minimize integral absolute error for optimal tracking",
            CHROptimizationCriteria.DISTURBANCE_REJECTION: "Optimize load disturbance rejection capability"
        }
        return objectives[criteria]

    def _get_secondary_benefits(self, criteria: CHROptimizationCriteria,
                              response_type: CHRResponseType) -> List[str]:
        """Get secondary benefits of the optimization"""
        benefits = {
            CHROptimizationCriteria.NO_OVERSHOOT: ["High stability", "Predictable response", "Low wear on actuators"],
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: ["Fast response", "Good tracking", "Reasonable robustness"],
            CHROptimizationCriteria.MINIMUM_IAE: ["Optimal tracking error", "Good transient response", "Balanced performance"],
            CHROptimizationCriteria.DISTURBANCE_REJECTION: ["Excellent load handling", "Steady-state accuracy", "Industrial robustness"]
        }

        base_benefits = benefits[criteria]

        # Add response-type specific benefits
        if response_type == CHRResponseType.DISTURBANCE:
            base_benefits.append("Optimized for disturbance response")
        else:
            base_benefits.append("Optimized for setpoint tracking")

        return base_benefits

    def _get_trade_offs(self, criteria: CHROptimizationCriteria,
                       config: CHRControllerType) -> List[str]:
        """Get trade-offs of the optimization"""
        trade_offs = {
            CHROptimizationCriteria.NO_OVERSHOOT: ["Slower response", "Larger settling time", "Conservative control"],
            CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT: ["Some overshoot", "Reduced stability margin", "Potential oscillations"],
            CHROptimizationCriteria.MINIMUM_IAE: ["Moderate overshoot", "IAE-focused, not other metrics", "May not suit all processes"],
            CHROptimizationCriteria.DISTURBANCE_REJECTION: ["Setpoint response not optimal", "Potentially aggressive", "Higher control effort"]
        }

        base_trade_offs = trade_offs[criteria]

        # Add configuration-specific trade-offs
        if config == CHRControllerType.P_ONLY:
            base_trade_offs.append("No steady-state error elimination")
        elif config == CHRControllerType.PI:
            base_trade_offs.append("No derivative action for fast transients")

        return base_trade_offs

    def _assess_process_match(self, criteria: CHROptimizationCriteria, lt_ratio: float) -> float:
        """Assess how well the criteria matches the process type"""
        # Different criteria work better for different L/T ratios
        if criteria == CHROptimizationCriteria.NO_OVERSHOOT:
            # Better for higher L/T ratios (delay dominant)
            return min(1.0, 0.5 + lt_ratio)
        elif criteria == CHROptimizationCriteria.TWENTY_PERCENT_OVERSHOOT:
            # Good for moderate L/T ratios
            return 1.0 - abs(lt_ratio - 0.3) if lt_ratio <= 0.6 else 0.5
        elif criteria == CHROptimizationCriteria.MINIMUM_IAE:
            # Good for all process types
            return 0.9
        else:  # DISTURBANCE_REJECTION
            # Excellent for all types, especially with disturbances
            return 0.95

    def _assess_config_optimality(self, criteria: CHROptimizationCriteria,
                                config: CHRControllerType) -> float:
        """Assess optimality of controller configuration for criteria"""
        # PID generally best, PI good for most, P limited
        config_scores = {
            CHRControllerType.P_ONLY: 0.5,
            CHRControllerType.PI: 0.8,
            CHRControllerType.PID: 1.0
        }

        base_score = config_scores[config]

        # Adjust for specific criteria
        if criteria == CHROptimizationCriteria.DISTURBANCE_REJECTION and config == CHRControllerType.PID:
            base_score = 1.0  # PID excellent for disturbance rejection
        elif criteria == CHROptimizationCriteria.NO_OVERSHOOT and config == CHRControllerType.PI:
            base_score = 0.9  # PI often sufficient for no overshoot

        return base_score

    def _assess_response_appropriateness(self, criteria: CHROptimizationCriteria,
                                       response_type: CHRResponseType) -> float:
        """Assess appropriateness of response type for criteria"""
        if criteria == CHROptimizationCriteria.DISTURBANCE_REJECTION:
            return 1.0 if response_type == CHRResponseType.DISTURBANCE else 0.7
        else:
            return 1.0 if response_type == CHRResponseType.SETPOINT else 0.8

    def _estimate_criteria_achievement(self, criteria: CHROptimizationCriteria,
                                     config: CHRControllerType, lt_ratio: float) -> float:
        """Estimate how well the criteria will be achieved"""

        # Base achievement based on method accuracy
        base_achievement = 0.85

        # Adjust for process characteristics
        if lt_ratio > 2.0:  # Very high dead time
            base_achievement *= 0.8
        elif lt_ratio < 0.1:  # Very low dead time
            base_achievement *= 0.9

        # Adjust for controller configuration
        if config == CHRControllerType.P_ONLY:
            base_achievement *= 0.7
        elif config == CHRControllerType.PI:
            base_achievement *= 0.9

        return min(1.0, base_achievement)

    def _generate_recommendations(self, K: float, L: float, T: float,
                                pid_params: Dict[str, float],
                                criteria: CHROptimizationCriteria,
                                config: CHRControllerType,
                                response_type: CHRResponseType,
                                performance_prediction: Dict[str, float],
                                optimization_analysis: Dict[str, Any]) -> List[str]:
        """Generate tuning recommendations"""
        recommendations = []

        lt_ratio = L / T if T > 0 else 0

        # Method and criteria recommendations
        recommendations.append(f"CHR tuning optimized for: {optimization_analysis['target_analysis']['primary_objective']}")

        # Configuration recommendations
        if config == CHRControllerType.PID:
            recommendations.append("PID configuration provides full control capability")
        elif config == CHRControllerType.PI:
            recommendations.append("PI configuration eliminates derivative noise sensitivity")
        else:
            recommendations.append("P-only configuration - consider adding integral action for steady-state accuracy")

        # Response type recommendations
        if response_type == CHRResponseType.DISTURBANCE:
            recommendations.append("Optimized for disturbance rejection - excellent for processes with frequent load changes")
        else:
            recommendations.append("Optimized for setpoint tracking - ideal for frequent setpoint changes")

        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] == 0:
            recommendations.append("No overshoot design - very stable but slower response")
        elif performance_prediction['predicted_overshoot_percent'] > 15:
            recommendations.append("Higher overshoot expected - monitor for stability in practice")

        # Optimization quality recommendations
        if optimization_analysis['overall_suitability'] > 0.8:
            recommendations.append("Excellent match between optimization criteria and process characteristics")
        elif optimization_analysis['overall_suitability'] > 0.6:
            recommendations.append("Good optimization match - should provide reliable performance")
        else:
            recommendations.append("Fair optimization match - consider alternative criteria or methods")

        # Process-specific recommendations
        if lt_ratio > 1.0:
            recommendations.append("High dead time process - CHR well-suited for this application")
        elif lt_ratio < 0.1:
            recommendations.append("Low dead time process - consider Ziegler-Nichols as alternative")

        # Criteria-specific recommendations
        if criteria == CHROptimizationCriteria.MINIMUM_IAE:
            recommendations.append("IAE-optimized tuning - excellent for tracking applications")
        elif criteria == CHROptimizationCriteria.DISTURBANCE_REJECTION:
            recommendations.append("Consider feedforward control for further disturbance rejection improvement")

        # Trade-off recommendations
        recommendations.extend(optimization_analysis['target_analysis']['trade_offs'][:2])  # Top 2 trade-offs

        # Industrial implementation recommendations
        recommendations.append("CHR provides reliable tuning with well-defined optimization objectives")
        recommendations.append("Test tuning with realistic process conditions and disturbances")

        return recommendations

# Register Chien-Hrones-Reswick algorithm
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(ChienHronesReswickTuner)
        logger.info("Chien-Hrones-Reswick algorithm registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Chien-Hrones-Reswick algorithm: {e}")

# Export classes
__all__ = [
    'ChienHronesReswickTuner',
    'CHRTuningResult',
    'CHROptimizationCriteria',
    'CHRControllerType',
    'CHRResponseType'
]

logger.info("Chien-Hrones-Reswick tuning method implementation completed")
