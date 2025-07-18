#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.2 - Ziegler-Nichols Tuning Implementation
===============================================================

Implementation of classical Ziegler-Nichols PID tuning methods:
- Ultimate Gain Method (Closed-loop oscillation method)
- Process Reaction Curve Method (Open-loop step response method)

These methods are foundational in industrial control and provide reliable tuning
for a wide range of process types with well-established tuning rules.

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods  
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import logging
from scipy import signal
from scipy.optimize import minimize_scalar
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

class ZNResponseType(Enum):
    """Ziegler-Nichols response characteristics"""
    QUARTER_DECAY = "quarter_decay"
    NO_OVERSHOOT = "no_overshoot"
    SOME_OVERSHOOT = "some_overshoot"

class ZNTuningType(Enum):
    """Ziegler-Nichols tuning method types"""
    ULTIMATE_GAIN = "ultimate_gain"
    PROCESS_REACTION = "process_reaction"

@dataclass
class ZNTuningParameters:
    """Ziegler-Nichols tuning parameters result"""
    tuning_method: str
    tuning_type: ZNTuningType
    response_type: ZNResponseType
    parameters: Dict[str, float]
    controller_type: str
    process_characteristics: Dict[str, float]
    stability_analysis: Dict[str, Any]
    performance_prediction: Dict[str, float]
    recommendations: List[str]
    execution_time: float

class ZieglerNicholsUltimateGain(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Ziegler-Nichols Ultimate Gain (Closed-loop) tuning method
    
    This method requires finding the ultimate gain (Ku) and ultimate period (Tu)
    where the closed-loop system oscillates at the margin of stability.
    """
    
    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="ziegler_nichols_ultimate_gain",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Ziegler-Nichols Ultimate Gain (closed-loop) tuning method",
                version="1.0.0",
                min_data_points=100,
                supports_realtime=False,
                tags=["classical", "ZN", "ultimate_gain", "closed_loop"]
            )
            super().__init__(metadata)
        
        self.logger = logging.getLogger(__name__ + '.ZieglerNicholsUltimateGain')
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Ultimate Gain method"""
        errors = []
        
        # Check for required fields
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
        
        # Check response type
        if 'response_type' in data:
            try:
                ZNResponseType(data['response_type'])
            except ValueError:
                valid_types = [t.value for t in ZNResponseType]
                errors.append(f"Response type must be one of: {valid_types}")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Ziegler-Nichols Ultimate Gain tuning"""
        start_time = time.time()
        
        # Extract parameters
        Ku = data['ultimate_gain']
        Tu = data['ultimate_period']
        controller_type = data.get('controller_type', 'dependent')
        response_type = ZNResponseType(data.get('response_type', 'quarter_decay'))
        
        try:
            # Calculate ZN parameters based on response type
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_params(Ku, Tu, response_type)
            else:
                pid_params = self._calculate_independent_params(Ku, Tu, response_type)
            
            # Process characteristics
            process_characteristics = {
                'ultimate_gain': Ku,
                'ultimate_period': Tu,
                'ultimate_frequency': 2 * np.pi / Tu,
                'gain_margin_db': 20 * np.log10(Ku) if Ku > 1 else 0,
                'phase_margin_deg': 0.0  # At oscillation point
            }
            
            # Stability analysis
            stability_analysis = self._analyze_stability(Ku, Tu, pid_params, controller_type)
            
            # Performance prediction
            performance_prediction = self._predict_performance(Ku, Tu, pid_params, response_type)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                Ku, Tu, pid_params, response_type, stability_analysis, performance_prediction
            )
            
            execution_time = time.time() - start_time
            
            result = ZNTuningParameters(
                tuning_method="Ziegler-Nichols Ultimate Gain",
                tuning_type=ZNTuningType.ULTIMATE_GAIN,
                response_type=response_type,
                parameters=pid_params,
                controller_type=controller_type,
                process_characteristics=process_characteristics,
                stability_analysis=stability_analysis,
                performance_prediction=performance_prediction,
                recommendations=recommendations,
                execution_time=execution_time
            )
            
            return {
                'success': True,
                'result': result,
                'method': 'ziegler_nichols_ultimate_gain'
            }
            
        except Exception as e:
            self.logger.error(f"Ziegler-Nichols Ultimate Gain tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'ziegler_nichols_ultimate_gain'
            }
    
    def _calculate_dependent_params(self, Ku: float, Tu: float, 
                                  response_type: ZNResponseType) -> Dict[str, float]:
        """Calculate dependent (positional) PID parameters"""
        
        # Classic Ziegler-Nichols Ultimate Gain rules
        if response_type == ZNResponseType.QUARTER_DECAY:
            # Standard ZN rules for quarter-decay ratio
            Kc = 0.6 * Ku
            Ti = 0.5 * Tu
            Td = 0.125 * Tu
        elif response_type == ZNResponseType.NO_OVERSHOOT:
            # More conservative settings
            Kc = 0.2 * Ku
            Ti = 0.5 * Tu
            Td = 0.33 * Tu
        else:  # SOME_OVERSHOOT
            # Slightly aggressive settings
            Kc = 0.33 * Ku
            Ti = 0.5 * Tu
            Td = 0.33 * Tu
        
        return {
            'Kp': float(Kc),  # For compatibility, Kp = Kc in dependent form
            'Ti': float(Ti),
            'Td': float(Td)
        }
    
    def _calculate_independent_params(self, Ku: float, Tu: float,
                                    response_type: ZNResponseType) -> Dict[str, float]:
        """Calculate independent (parallel) PID parameters"""
        
        # Get dependent parameters first
        dependent_params = self._calculate_dependent_params(Ku, Tu, response_type)
        
        # Convert to independent form
        Kc = dependent_params['Kp']
        Ti = dependent_params['Ti'] 
        Td = dependent_params['Td']
        
        # Independent form conversion
        Kp = Kc
        Ki = Kc / Ti if Ti > 0 else 0
        Kd = Kc * Td
        
        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }
    
    def _analyze_stability(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                          controller_type: str) -> Dict[str, Any]:
        """Analyze stability characteristics"""
        
        # Calculate stability margins
        gain_margin = Ku / pid_params['Kp'] if pid_params['Kp'] > 0 else float('inf')
        gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else float('inf')
        
        # Phase margin estimation (ZN typically gives poor phase margin)
        phase_margin_deg = 30.0  # Typical ZN phase margin
        
        # Stability assessment
        stable = gain_margin_db >= 6.0 and phase_margin_deg >= 30.0
        
        return {
            'gain_margin': gain_margin,
            'gain_margin_db': gain_margin_db,
            'phase_margin_deg': phase_margin_deg,
            'stable': stable,
            'robustness_level': 'low' if gain_margin_db < 6 else 'medium' if gain_margin_db < 12 else 'high'
        }
    
    def _predict_performance(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                           response_type: ZNResponseType) -> Dict[str, float]:
        """Predict closed-loop performance characteristics"""
        
        # Performance predictions based on ZN theory and response type
        if response_type == ZNResponseType.QUARTER_DECAY:
            # Quarter-decay ratio response
            overshoot_percent = 25.0
            settling_time_factor = 4.0
            rise_time_factor = 0.35
        elif response_type == ZNResponseType.NO_OVERSHOOT:
            # No overshoot response
            overshoot_percent = 0.0
            settling_time_factor = 8.0
            rise_time_factor = 1.0
        else:  # SOME_OVERSHOOT
            # Some overshoot response
            overshoot_percent = 10.0
            settling_time_factor = 6.0
            rise_time_factor = 0.5
        
        # Time predictions based on ultimate period
        settling_time = settling_time_factor * Tu
        rise_time = rise_time_factor * Tu
        
        # Performance index (0-1, higher is better)
        performance_index = max(0, 1 - overshoot_percent/50 - settling_time/(10*Tu))
        
        return {
            'predicted_overshoot_percent': overshoot_percent,
            'predicted_settling_time': settling_time,
            'predicted_rise_time': rise_time,
            'performance_index': performance_index,
            'damping_ratio': 0.7 if response_type == ZNResponseType.NO_OVERSHOOT else 0.3
        }
    
    def _generate_recommendations(self, Ku: float, Tu: float, pid_params: Dict[str, float],
                                response_type: ZNResponseType, stability_analysis: Dict[str, Any],
                                performance_prediction: Dict[str, float]) -> List[str]:
        """Generate tuning recommendations"""
        recommendations = []
        
        # Stability recommendations
        if stability_analysis['gain_margin_db'] < 6:
            recommendations.append("Low gain margin - consider reducing proportional gain for better robustness")
        
        if stability_analysis['phase_margin_deg'] < 30:
            recommendations.append("Poor phase margin - Ziegler-Nichols typically gives aggressive tuning")
        
        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] > 20:
            recommendations.append("High overshoot predicted - consider no-overshoot ZN variant or additional detuning")
        
        if performance_prediction['predicted_settling_time'] > 8 * Tu:
            recommendations.append("Slow settling time - controller may be too conservative")
        
        # Method-specific recommendations
        if response_type == ZNResponseType.QUARTER_DECAY:
            recommendations.append("Standard ZN quarter-decay tuning - good starting point but may need detuning")
        
        # Process-specific recommendations
        if Tu > 60:  # Slow process
            recommendations.append("Slow process detected - consider IMC or Lambda tuning for better robustness")
        
        if Ku < 1:
            recommendations.append("Low ultimate gain - process may be difficult to control")
        
        # General recommendations
        recommendations.append("Test tuning incrementally and monitor for oscillations")
        recommendations.append("Consider detuning by 20-30% for improved robustness in industrial settings")
        
        return recommendations

class ZieglerNicholsProcessReaction(AlgorithmBase if ALGORITHM_REGISTRY_AVAILABLE else object):
    """
    Ziegler-Nichols Process Reaction Curve (Open-loop) tuning method
    
    This method uses the open-loop step response to identify process characteristics
    and calculate PID parameters based on the reaction curve analysis.
    """
    
    def __init__(self):
        if ALGORITHM_REGISTRY_AVAILABLE:
            metadata = AlgorithmMetadata(
                name="ziegler_nichols_process_reaction",
                category=AlgorithmCategory.TUNING_CALCULATION,
                complexity=AlgorithmComplexity.MEDIUM,
                description="Ziegler-Nichols Process Reaction Curve (open-loop) tuning method",
                version="1.0.0",
                min_data_points=50,
                supports_realtime=False,
                tags=["classical", "ZN", "process_reaction", "open_loop"]
            )
            super().__init__(metadata)
        
        self.logger = logging.getLogger(__name__ + '.ZieglerNicholsProcessReaction')
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for Process Reaction method"""
        errors = []
        
        # Check for time series data or process model parameters
        if 'time_data' in data and 'output_data' in data and 'input_data' in data:
            # Time series approach
            for field in ['time_data', 'output_data', 'input_data']:
                if not isinstance(data[field], (list, np.ndarray)):
                    errors.append(f"Field '{field}' must be array-like")
                elif len(data[field]) < 10:
                    errors.append(f"Field '{field}' must have at least 10 data points")
        elif 'process_gain' in data and 'dead_time' in data and 'time_constant' in data:
            # Model parameters approach
            for field in ['process_gain', 'dead_time', 'time_constant']:
                if field not in data:
                    errors.append(f"Missing required field: '{field}'")
                elif not isinstance(data[field], (int, float)):
                    errors.append(f"Field '{field}' must be numeric")
                elif data[field] <= 0 and field != 'dead_time':  # dead_time can be zero
                    errors.append(f"Field '{field}' must be positive")
        else:
            errors.append("Must provide either time series data or process model parameters")
        
        # Check controller type
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute Ziegler-Nichols Process Reaction tuning"""
        start_time = time.time()
        
        controller_type = data.get('controller_type', 'dependent')
        response_type = ZNResponseType(data.get('response_type', 'quarter_decay'))
        
        try:
            # Determine process characteristics
            if 'time_data' in data:
                # Analyze time series data
                process_params = self._analyze_step_response(
                    data['time_data'], data['output_data'], data['input_data']
                )
            else:
                # Use provided model parameters
                process_params = {
                    'process_gain': data['process_gain'],
                    'dead_time': data['dead_time'],
                    'time_constant': data['time_constant']
                }
            
            # Calculate ZN parameters
            if controller_type == 'dependent':
                pid_params = self._calculate_dependent_reaction_params(process_params, response_type)
            else:
                pid_params = self._calculate_independent_reaction_params(process_params, response_type)
            
            # Analysis and predictions
            stability_analysis = self._analyze_reaction_stability(process_params, pid_params)
            performance_prediction = self._predict_reaction_performance(process_params, pid_params, response_type)
            recommendations = self._generate_reaction_recommendations(
                process_params, pid_params, stability_analysis, performance_prediction
            )
            
            execution_time = time.time() - start_time
            
            result = ZNTuningParameters(
                tuning_method="Ziegler-Nichols Process Reaction",
                tuning_type=ZNTuningType.PROCESS_REACTION,
                response_type=response_type,
                parameters=pid_params,
                controller_type=controller_type,
                process_characteristics=process_params,
                stability_analysis=stability_analysis,
                performance_prediction=performance_prediction,
                recommendations=recommendations,
                execution_time=execution_time
            )
            
            return {
                'success': True,
                'result': result,
                'method': 'ziegler_nichols_process_reaction'
            }
            
        except Exception as e:
            self.logger.error(f"Ziegler-Nichols Process Reaction tuning failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'ziegler_nichols_process_reaction'
            }
    
    def _analyze_step_response(self, time_data: np.ndarray, output_data: np.ndarray,
                              input_data: np.ndarray) -> Dict[str, float]:
        """Analyze step response to extract process characteristics"""
        
        # Convert to numpy arrays
        time = np.array(time_data)
        output = np.array(output_data)
        input_signal = np.array(input_data)
        
        # Find step change in input
        input_diff = np.diff(input_signal)
        step_index = np.argmax(np.abs(input_diff))
        
        if step_index == 0:
            step_index = 1
        
        # Calculate step size
        step_size = input_signal[step_index + 1] - input_signal[step_index]
        
        if abs(step_size) < 1e-6:
            raise ValueError("No significant step change detected in input")
        
        # Baseline and final values
        baseline = np.mean(output[:step_index])
        final_value = np.mean(output[-20:])  # Last 20 points
        
        # Process gain
        process_gain = (final_value - baseline) / step_size
        
        # Dead time estimation - first significant change in output
        output_threshold = baseline + 0.02 * (final_value - baseline)
        dead_time_indices = np.where(np.abs(output - baseline) >= abs(output_threshold - baseline))[0]
        
        if len(dead_time_indices) > 0:
            dead_time_index = dead_time_indices[0]
            dead_time = time[dead_time_index] - time[step_index]
        else:
            dead_time = 0.0
        
        # Time constant estimation - 63.2% of final response
        target_value = baseline + 0.632 * (final_value - baseline)
        
        # Find time when output reaches 63.2% of final value
        if final_value > baseline:
            tau_indices = np.where(output >= target_value)[0]
        else:
            tau_indices = np.where(output <= target_value)[0]
        
        if len(tau_indices) > 0:
            tau_index = tau_indices[0]
            time_constant = time[tau_index] - time[step_index] - dead_time
        else:
            # Fallback estimation
            time_constant = (time[-1] - time[step_index]) / 3
        
        # Ensure positive time constant
        time_constant = max(time_constant, 0.1)
        
        return {
            'process_gain': float(process_gain),
            'dead_time': float(max(dead_time, 0.0)),
            'time_constant': float(time_constant),
            'step_size': float(step_size),
            'baseline_value': float(baseline),
            'final_value': float(final_value)
        }
    
    def _calculate_dependent_reaction_params(self, process_params: Dict[str, float],
                                           response_type: ZNResponseType) -> Dict[str, float]:
        """Calculate dependent PID parameters from process reaction curve"""
        
        K = process_params['process_gain']
        L = process_params['dead_time']
        T = process_params['time_constant']
        
        # ZN Process Reaction Curve rules
        if abs(K) < 1e-6:
            raise ValueError("Process gain is too small for reliable tuning")
        
        if response_type == ZNResponseType.QUARTER_DECAY:
            # Standard ZN reaction curve rules
            Kc = 1.2 * T / (K * L) if L > 0 else 1.0 / K
            Ti = 2.0 * L if L > 0 else T
            Td = 0.5 * L if L > 0 else 0.0
        elif response_type == ZNResponseType.NO_OVERSHOOT:
            # Conservative settings
            Kc = 0.6 * T / (K * L) if L > 0 else 0.5 / K
            Ti = 4.0 * L if L > 0 else 2.0 * T
            Td = L if L > 0 else 0.0
        else:  # SOME_OVERSHOOT
            # Moderate settings
            Kc = 0.9 * T / (K * L) if L > 0 else 0.8 / K
            Ti = 3.0 * L if L > 0 else 1.5 * T
            Td = 0.5 * L if L > 0 else 0.0
        
        return {
            'Kp': float(Kc),
            'Ti': float(Ti),
            'Td': float(Td)
        }
    
    def _calculate_independent_reaction_params(self, process_params: Dict[str, float],
                                             response_type: ZNResponseType) -> Dict[str, float]:
        """Calculate independent PID parameters from process reaction curve"""
        
        # Get dependent parameters first
        dependent_params = self._calculate_dependent_reaction_params(process_params, response_type)
        
        # Convert to independent form
        Kc = dependent_params['Kp']
        Ti = dependent_params['Ti']
        Td = dependent_params['Td']
        
        Kp = Kc
        Ki = Kc / Ti if Ti > 0 else 0
        Kd = Kc * Td
        
        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }
    
    def _analyze_reaction_stability(self, process_params: Dict[str, float],
                                  pid_params: Dict[str, float]) -> Dict[str, Any]:
        """Analyze stability for process reaction method"""
        
        K = process_params['process_gain']
        L = process_params['dead_time']
        T = process_params['time_constant']
        
        # Calculate L/T ratio for stability assessment
        if T > 0:
            lt_ratio = L / T
        else:
            lt_ratio = float('inf')
        
        # Stability assessment based on L/T ratio
        if lt_ratio < 0.1:
            stability_level = 'high'
        elif lt_ratio < 0.3:
            stability_level = 'medium'
        else:
            stability_level = 'low'
        
        # Gain margin estimation
        Kc = pid_params['Kp']
        gain_margin = abs(1.0 / (K * Kc)) if K * Kc != 0 else float('inf')
        gain_margin_db = 20 * np.log10(gain_margin) if gain_margin > 0 else float('inf')
        
        # Phase margin (rough estimation for FOPDT)
        phase_margin_deg = 60 - 57.3 * L / T if T > 0 else 60
        
        return {
            'lt_ratio': lt_ratio,
            'stability_level': stability_level,
            'gain_margin': gain_margin,
            'gain_margin_db': min(gain_margin_db, 60),  # Cap at 60dB for display
            'phase_margin_deg': max(phase_margin_deg, 0),
            'stable': gain_margin_db >= 6 and phase_margin_deg >= 30
        }
    
    def _predict_reaction_performance(self, process_params: Dict[str, float],
                                    pid_params: Dict[str, float],
                                    response_type: ZNResponseType) -> Dict[str, float]:
        """Predict performance for process reaction method"""
        
        L = process_params['dead_time']
        T = process_params['time_constant']
        
        # Performance predictions based on L/T ratio and response type
        lt_ratio = L / T if T > 0 else 0
        
        if response_type == ZNResponseType.QUARTER_DECAY:
            overshoot_base = 25.0
            settling_factor = 4.0
            rise_factor = 1.0
        elif response_type == ZNResponseType.NO_OVERSHOOT:
            overshoot_base = 0.0
            settling_factor = 8.0
            rise_factor = 2.0
        else:  # SOME_OVERSHOOT
            overshoot_base = 10.0
            settling_factor = 6.0
            rise_factor = 1.5
        
        # Adjust for process characteristics
        overshoot_percent = overshoot_base * (1 + lt_ratio)
        settling_time = settling_factor * (T + L)
        rise_time = rise_factor * (T + L)
        
        # Performance index
        performance_index = max(0, 1 - lt_ratio - overshoot_percent/100)
        
        return {
            'predicted_overshoot_percent': min(overshoot_percent, 100),
            'predicted_settling_time': settling_time,
            'predicted_rise_time': rise_time,
            'performance_index': performance_index,
            'lt_ratio': lt_ratio
        }
    
    def _generate_reaction_recommendations(self, process_params: Dict[str, float],
                                         pid_params: Dict[str, float],
                                         stability_analysis: Dict[str, Any],
                                         performance_prediction: Dict[str, float]) -> List[str]:
        """Generate recommendations for process reaction method"""
        recommendations = []
        
        L = process_params['dead_time']
        T = process_params['time_constant']
        lt_ratio = L / T if T > 0 else 0
        
        # Process characteristic recommendations
        if lt_ratio > 0.5:
            recommendations.append("High dead time ratio (L/T > 0.5) - consider Cohen-Coon or IMC tuning instead")
        elif lt_ratio < 0.1:
            recommendations.append("Low dead time process - ZN should work well")
        
        # Stability recommendations
        if stability_analysis['stability_level'] == 'low':
            recommendations.append("Process difficult to control - consider more conservative tuning")
        
        if stability_analysis['gain_margin_db'] < 6:
            recommendations.append("Low gain margin - reduce proportional gain by 20-30%")
        
        # Performance recommendations
        if performance_prediction['predicted_overshoot_percent'] > 25:
            recommendations.append("High overshoot predicted - consider no-overshoot variant")
        
        # Method-specific recommendations
        recommendations.append("ZN Process Reaction gives aggressive tuning - test carefully")
        recommendations.append("Consider detuning for industrial robustness")
        
        if L > T:
            recommendations.append("Dead time dominant process - Cohen-Coon may be better suited")
        
        return recommendations

# Register Ziegler-Nichols algorithms
if ALGORITHM_REGISTRY_AVAILABLE:
    try:
        registry.register(ZieglerNicholsUltimateGain)
        registry.register(ZieglerNicholsProcessReaction)
        logger.info("Ziegler-Nichols algorithms registered successfully")
    except Exception as e:
        logger.warning(f"Failed to register Ziegler-Nichols algorithms: {e}")

# Export classes
__all__ = [
    'ZieglerNicholsUltimateGain',
    'ZieglerNicholsProcessReaction', 
    'ZNTuningParameters',
    'ZNResponseType',
    'ZNTuningType'
]

logger.info("Ziegler-Nichols tuning methods implementation completed") 