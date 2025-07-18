#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Tyreus-Luyben Tuning Implementation
=============================================================

Implementation of Tyreus-Luyben PID tuning method for conservative, robust control.
Tyreus-Luyben provides more conservative tuning than Ziegler-Nichols, resulting in
better stability margins and reduced overshoot at the cost of slower response.

Key Features:
- Conservative tuning for improved robustness
- Better stability margins than Ziegler-Nichols
- Reduced overshoot and oscillation tendency
- Suitable for processes requiring high stability

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from enum import Enum
import time
from datetime import datetime

# Import algorithm base class
try:
    from ...algorithms import (
        AlgorithmBase, AlgorithmMetadata, AlgorithmCategory, 
        AlgorithmComplexity, registry
    )
    ALGORITHM_REGISTRY_AVAILABLE = True
except ImportError:
    ALGORITHM_REGISTRY_AVAILABLE = False
    logging.warning("⚠️ Algorithm registry not available - using standalone implementation")

logger = logging.getLogger(__name__)

class TLTuningStrategy(Enum):
    """Tyreus-Luyben tuning strategies"""
    STANDARD = "standard"
    PI_ONLY = "pi_only"
    EXTRA_CONSERVATIVE = "extra_conservative"

@dataclass
class TLTuningResult:
    """Tyreus-Luyben tuning result"""
    tuning_method: str
    strategy: TLTuningStrategy
    parameters: Dict[str, float]
    controller_type: str
    process_characteristics: Dict[str, float]
    robustness_analysis: Dict[str, Any]
    stability_analysis: Dict[str, Any]
    performance_prediction: Dict[str, float]
    comparison_with_zn: Dict[str, Any]
    recommendations: List[str]
    execution_time: float

class TyreusLuybenTuner(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Tyreus-Luyben PID tuning algorithm
    
    Provides conservative tuning based on ultimate gain and period,
    offering better robustness than Ziegler-Nichols at the cost
    of slower response times.
    """
    
    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="tyreus_luyben_tuner",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Tyreus-Luyben conservative PID tuning method",
                version="1.0.0",
                min_data_points=50,
                supports_realtime=False,
                tags=["classical", "tyreus_luyben", "conservative", "robust"]
            )
            super().__init__(metadata)
        
        self.logger = logging.getLogger(__name__ + '.TyreusLuybenTuner')
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Tyreus-Luyben tuning"""
        errors = []
        
        # Check for required ultimate gain parameters
        required_fields = ['ultimate_gain', 'ultimate_period']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
            elif not isinstance(data[field], (int, float)):
                errors.append(f"Field '{field}' must be numeric")
            elif data[field] <= 0:
                errors.append(f"Field '{field}' must be positive")
        
        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")
        
        # Check strategy
        if 'strategy' in data:
            try:
                TLTuningStrategy(data['strategy'])
            except ValueError:
                valid_strategies = [s.value for s in TLTuningStrategy]
                errors.append(f"Strategy must be one of: {valid_strategies}")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Tyreus-Luyben tuning algorithm"""
        start_time = time.time()
        
        # Extract parameters
        Ku = data['ultimate_gain']
        Tu = data['ultimate_period']
        controller_type = data.get('controller_type', 'dependent')
        strategy = TLTuningStrategy(data.get('strategy', 'standard'))
        
        try:
            # Process characteristics analysis
            process_characteristics = self._analyze_process_characteristics(Ku, Tu)
            
            # Calculate Tyreus-Luyben parameters
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(Ku, Tu, strategy)
            else:
                pid_params = self._calculate_independent_params(Ku, Tu, strategy)
            
            # Robustness analysis
            robustness_analysis = self._analyze_robustness(Ku, Tu, pid_params, strategy)
            
            # Stability analysis
            stability_analysis = self._analyze_stability(Ku, Tu, pid_params)
            
            # Performance prediction
            performance_prediction = self._predict_performance(Ku, Tu, pid_params, strategy)
            
            # Comparison with Ziegler-Nichols
            comparison_with_zn = self._compare_with_ziegler_nichols(Ku, Tu, pid_params, controller_type)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                Ku, Tu, pid_params, strategy, robustness_analysis, 
                stability_analysis, performance_prediction
            )
            
            execution_time = time.time() - start_time
            
            result = TLTuningResult(
                tuning_method="Tyreus-Luyben",
                strategy=strategy,
                parameters=pid_params,
                controller_type=controller_type,
                process_characteristics=process_characteristics,
                robustness_analysis=robustness_analysis,
                stability_analysis=stability_analysis,
                performance_prediction=performance_prediction,
                comparison_with_zn=comparison_with_zn,
                recommendations=recommendations,
                execution_time=execution_time
            )
            
            return {
                'success': True,
                'result': result,
                'method': 'tyreus_luyben'
            }
            
        except Exception as e:
            self.logger.error(f"Tyreus-Luyben tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'tyreus_luyben'
            }
    
    def _analyze_process_characteristics(self, Ku: float, Tu: float) -> Dict[str, float]:
        """Analyze process characteristics from ultimate parameters"""
        
        # Ultimate frequency
        omega_u = 2 * np.pi / Tu
        
        # Estimate process characteristics at ultimate frequency
        # These are typical relationships for processes at oscillation
        estimated_phase_lag = 180.0  # degrees at ultimate frequency
        estimated_gain_margin_db = 20 * np.log10(Ku) if Ku > 1 else 0
        
        # Process classification based on ultimate period
        if Tu < 10:
            process_speed = "fast"
        elif Tu < 60:
            process_speed = "medium"
        else:
            process_speed = "slow"
        
        # Robustness factor estimation
        robustness_factor = 1.0 / Ku if Ku > 0 else 1.0
        
        return {
            'ultimate_gain': Ku,
            'ultimate_period': Tu,
            'ultimate_frequency': omega_u,
            'process_speed': process_speed,
            'estimated_gain_margin_db': estimated_gain_margin_db,
            'estimated_phase_lag': estimated_phase_lag,
            'robustness_factor': robustness_factor
        }
    
    def _calculate_dependent_params(self, Ku: float, Tu: float, 
                                  strategy: TLTuningStrategy) -> Dict[str, float]:
        """Calculate dependent (positional) PID parameters using Tyreus-Luyben rules"""
        
        if strategy == TLTuningStrategy.STANDARD:
            # Standard Tyreus-Luyben rules (Ti-only)
            Kc = Ku / 3.2
            Ti = 2.2 * Tu
            Td = Tu / 6.3
        elif strategy == TLTuningStrategy.PI_ONLY:
            # PI-only controller (no derivative)
            Kc = Ku / 2.2
            Ti = 2.2 * Tu
            Td = 0.0
        else:  # EXTRA_CONSERVATIVE
            # Extra conservative settings
            Kc = Ku / 4.0
            Ti = 2.5 * Tu
            Td = Tu / 8.0
        
        # Apply reasonable bounds
        Kc = max(0.01, min(100.0, Kc))
        Ti = max(0.01, min(9999.0, Ti))
        Td = max(0.0, min(99.99, Td))
        
        return {
            'Kp': float(Kc),
            'Ti': float(Ti),
            'Td': float(Td)
        }
    
    def _calculate_independent_params(self, Ku: float, Tu: float,
                                    strategy: TLTuningStrategy) -> Dict[str, float]:
        """Calculate independent (parallel) PID parameters using Tyreus-Luyben rules"""
        
        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(Ku, Tu, strategy)
        
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
    
    def _analyze_robustness(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                          strategy: TLTuningStrategy) -> Dict[str, Any]:
        """Analyze robustness characteristics of Tyreus-Luyben tuning"""
        
        Kc = pid_params['Kp']
        
        # Gain margin calculation
        gain_margin = Ku / Kc if Kc > 0 else float('inf')
        gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else 60
        
        # Phase margin estimation (Tyreus-Luyben typically provides good phase margin)
        if strategy == TLTuningStrategy.STANDARD:
            typical_phase_margin = 50.0
        elif strategy == TLTuningStrategy.PI_ONLY:
            typical_phase_margin = 60.0  # PI controllers have better phase margin
        else:  # EXTRA_CONSERVATIVE
            typical_phase_margin = 65.0
        
        # Robustness classification
        if gain_margin_db >= 15 and typical_phase_margin >= 50:
            robustness_level = 'very_high'
        elif gain_margin_db >= 10 and typical_phase_margin >= 40:
            robustness_level = 'high'
        elif gain_margin_db >= 6 and typical_phase_margin >= 30:
            robustness_level = 'medium'
        else:
            robustness_level = 'low'
        
        # Sensitivity analysis
        gain_sensitivity = 1.0 / gain_margin if gain_margin > 0 else 1.0
        model_uncertainty_tolerance = gain_margin_db / 20.0  # Rough estimation
        
        # Disturbance rejection capability
        # Conservative tuning typically has good low-frequency disturbance rejection
        disturbance_rejection_quality = 'good' if strategy != TLTuningStrategy.EXTRA_CONSERVATIVE else 'excellent'
        
        return {
            'gain_margin': gain_margin,
            'gain_margin_db': min(gain_margin_db, 60),  # Cap for display
            'phase_margin_deg': typical_phase_margin,
            'robustness_level': robustness_level,
            'gain_sensitivity': gain_sensitivity,
            'model_uncertainty_tolerance': model_uncertainty_tolerance,
            'disturbance_rejection_quality': disturbance_rejection_quality,
            'strategy_robustness_factor': self._get_strategy_robustness_factor(strategy)
        }
    
    def _get_strategy_robustness_factor(self, strategy: TLTuningStrategy) -> float:
        """Get robustness factor for different strategies"""
        factors = {
            TLTuningStrategy.STANDARD: 1.0,
            TLTuningStrategy.PI_ONLY: 1.2,
            TLTuningStrategy.EXTRA_CONSERVATIVE: 1.5
        }
        return factors[strategy]
    
    def _analyze_stability(self, Ku: float, Tu: float, pid_params: Dict[str, float]) -> Dict[str, Any]:
        """Analyze closed-loop stability"""
        
        Kc = pid_params['Kp']
        
        # Calculate stability margins
        gain_margin = Ku / Kc if Kc > 0 else float('inf')
        gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else 60
        
        # Phase margin (Tyreus-Luyben typically provides 45-60 degrees)
        phase_margin_deg = 50.0  # Typical for Tyreus-Luyben
        
        # Stability assessment
        stable = gain_margin_db >= 6.0 and phase_margin_deg >= 30.0
        
        # Closed-loop bandwidth estimation
        bandwidth_ratio = 1.0 / Tu  # Rough estimation
        
        # Stability classification
        if gain_margin_db >= 12 and phase_margin_deg >= 45:
            stability_class = 'very_stable'
        elif gain_margin_db >= 8 and phase_margin_deg >= 35:
            stability_class = 'stable'
        elif gain_margin_db >= 6 and phase_margin_deg >= 30:
            stability_class = 'marginally_stable'
        else:
            stability_class = 'unstable'
        
        return {
            'gain_margin': gain_margin,
            'gain_margin_db': min(gain_margin_db, 60),
            'phase_margin_deg': phase_margin_deg,
            'stable': stable,
            'stability_class': stability_class,
            'bandwidth_ratio': bandwidth_ratio,
            'oscillation_tendency': 'low'  # Tyreus-Luyben reduces oscillations
        }
    
    def _predict_performance(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                           strategy: TLTuningStrategy) -> Dict[str, float]:
        """Predict closed-loop performance characteristics"""
        
        # Performance predictions based on Tyreus-Luyben characteristics
        # Generally more conservative than Ziegler-Nichols
        
        if strategy == TLTuningStrategy.STANDARD:
            overshoot_percent = 10.0  # Much less than ZN
            settling_time_factor = 6.0
            rise_time_factor = 2.0
        elif strategy == TLTuningStrategy.PI_ONLY:
            overshoot_percent = 5.0   # Even less overshoot
            settling_time_factor = 8.0
            rise_time_factor = 3.0
        else:  # EXTRA_CONSERVATIVE
            overshoot_percent = 2.0   # Minimal overshoot
            settling_time_factor = 10.0
            rise_time_factor = 4.0
        
        # Time predictions
        settling_time = settling_time_factor * Tu
        rise_time = rise_time_factor * Tu
        
        # Performance index (0-1, higher is better)
        # Accounts for robustness vs speed trade-off
        speed_factor = 1.0 / settling_time_factor
        robustness_factor = 1.0 - overshoot_percent / 100
        performance_index = 0.7 * robustness_factor + 0.3 * speed_factor
        
        # Damping characteristics
        damping_ratio = 0.8 + 0.1 * (4.0 - settling_time_factor / 2.0)  # Higher damping
        damping_ratio = max(0.6, min(1.0, damping_ratio))
        
        # Control effort estimation
        control_effort_factor = 0.6  # Generally lower control effort
        
        return {
            'predicted_overshoot_percent': overshoot_percent,
            'predicted_settling_time': settling_time,
            'predicted_rise_time': rise_time,
            'performance_index': performance_index,
            'damping_ratio': damping_ratio,
            'control_effort_factor': control_effort_factor,
            'oscillation_tendency': 'low',
            'robustness_vs_speed_ratio': robustness_factor / speed_factor
        }
    
    def _compare_with_ziegler_nichols(self, Ku: float, Tu: float, tl_params: Dict[str, float],
                                    controller_type: str) -> Dict[str, Any]:
        """Compare Tyreus-Luyben with Ziegler-Nichols tuning"""
        
        # Calculate equivalent Ziegler-Nichols parameters for comparison
        if controller_type == 'dependent':
            zn_kc = 0.6 * Ku
            zn_ti = 0.5 * Tu
            zn_td = 0.125 * Tu
        else:
            zn_kc = 0.6 * Ku
            zn_ki = zn_kc / (0.5 * Tu)
            zn_kd = zn_kc * 0.125 * Tu
        
        tl_kc = tl_params['Kp']
        
        # Calculate comparison metrics
        gain_ratio = tl_kc / zn_kc if zn_kc > 0 else 1.0
        
        if controller_type == 'dependent':
            ti_ratio = tl_params['Ti'] / zn_ti if zn_ti > 0 else 1.0
            td_ratio = tl_params['Td'] / zn_td if zn_td > 0 else 1.0
        else:
            ti_ratio = (tl_params['Ki'] / zn_ki) if zn_ki > 0 else 1.0
            td_ratio = (tl_params['Kd'] / zn_kd) if zn_kd > 0 else 1.0
        
        # Performance comparison
        performance_comparison = {
            'overshoot': 'much_lower',  # TL typically has much lower overshoot
            'settling_time': 'slower',   # TL is more conservative
            'robustness': 'much_higher', # TL provides better robustness
            'oscillation_tendency': 'much_lower'  # TL reduces oscillations
        }
        
        # Recommendation
        if gain_ratio < 0.7:
            recommendation = "Tyreus-Luyben provides significantly more conservative tuning"
        elif gain_ratio < 0.9:
            recommendation = "Tyreus-Luyben provides moderately more conservative tuning"
        else:
            recommendation = "Tyreus-Luyben provides similar aggressiveness to Ziegler-Nichols"
        
        return {
            'gain_ratio_tl_to_zn': gain_ratio,
            'integral_time_ratio': ti_ratio,
            'derivative_time_ratio': td_ratio,
            'performance_comparison': performance_comparison,
            'recommendation': recommendation,
            'preferred_for': [
                'high_reliability_required',
                'conservative_operation',
                'minimal_overshoot_critical',
                'robust_to_model_uncertainty'
            ]
        }
    
    def _generate_recommendations(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                                strategy: TLTuningStrategy, robustness_analysis: Dict[str, Any],
                                stability_analysis: Dict[str, Any], 
                                performance_prediction: Dict[str, float]) -> List[str]:
        """Generate tuning recommendations"""
        recommendations = []
        
        # Strategy recommendations
        if strategy == TLTuningStrategy.STANDARD:
            recommendations.append("Standard Tyreus-Luyben provides good balance of robustness and performance")
        elif strategy == TLTuningStrategy.PI_ONLY:
            recommendations.append("PI-only strategy eliminates derivative kick and noise sensitivity")
        else:
            recommendations.append("Extra conservative strategy for maximum robustness")
        
        # Robustness recommendations
        if robustness_analysis['robustness_level'] == 'very_high':
            recommendations.append("Excellent robustness - suitable for uncertain process conditions")
        elif robustness_analysis['robustness_level'] == 'high':
            recommendations.append("Good robustness - should handle model uncertainties well")
        
        # Stability recommendations
        if stability_analysis['stability_class'] == 'very_stable':
            recommendations.append("Very stable tuning - minimal risk of oscillations")
        
        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] < 5:
            recommendations.append("Low overshoot predicted - excellent for processes requiring tight control")
        
        if performance_prediction['predicted_settling_time'] > 8 * Tu:
            recommendations.append("Conservative settling time - consider more aggressive strategy if speed is critical")
        
        # Process-specific recommendations
        if Tu > 60:
            recommendations.append("Slow process - Tyreus-Luyben conservative approach is well-suited")
        elif Tu < 10:
            recommendations.append("Fast process - monitor for adequate speed of response")
        
        if Ku > 5:
            recommendations.append("High ultimate gain - conservative approach helps manage high sensitivity")
        
        # Industrial recommendations
        recommendations.append("Tyreus-Luyben excellent choice for industrial applications requiring high reliability")
        recommendations.append("Lower maintenance burden due to reduced oscillation tendency")
        
        if strategy != TLTuningStrategy.PI_ONLY:
            recommendations.append("Monitor derivative action for noise sensitivity in industrial environment")
        
        # Comparison recommendations
        recommendations.append("More robust than Ziegler-Nichols but with slower response")
        recommendations.append("Consider if robustness is more important than speed of response")
        
        return recommendations

# Register Tyreus-Luyben algorithm
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(TyreusLuybenTuner)
        logger.info("Tyreus-Luyben algorithm registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Tyreus-Luyben algorithm: {e}")

# Export classes
__all__ = [
    'TyreusLuybenTuner',
    'TLTuningResult',
    'TLTuningStrategy'
]

logger.info("Tyreus-Luyben tuning method implementation completed") 