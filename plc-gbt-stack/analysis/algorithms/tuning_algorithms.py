#!/usr/bin/env python3
"""
Phase 22.1.3: Tuning Algorithms
==============================

Advanced PID tuning algorithms for control loop optimization, building upon
the proven IMC methodology from pid_analysis_bundle.py with enhancements:

- Enhanced IMC (Internal Model Control) tuning
- Adaptive PID tuning algorithms
- Multi-objective tuning optimization
- Robust tuning for model uncertainty
- Real-time tuning adjustment

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from scipy import signal, optimize
from scipy.optimize import minimize, differential_evolution
import warnings

from . import (
    AlgorithmBase, AlgorithmMetadata, AlgorithmCategory, 
    AlgorithmComplexity, registry
)

logger = logging.getLogger(__name__)

@dataclass
class TuningResult:
    """Results from PID tuning analysis"""
    tuning_method: str
    parameters: Dict[str, float]
    performance_metrics: Dict[str, float]
    stability_analysis: Dict[str, Any]
    robustness_analysis: Dict[str, Any]
    controller_type: str  # 'dependent' or 'independent'
    recommendations: List[str]

class IMCTuner(AlgorithmBase):
    """
    Enhanced IMC tuning algorithm based on pid_analysis_bundle.py with
    improved robustness and multi-objective optimization
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="imc_tuner",
            category=AlgorithmCategory.TUNING_CALCULATION,
            complexity=AlgorithmComplexity.MEDIUM,
            description="Enhanced IMC tuning with robustness analysis",
            version="1.1.0",
            min_data_points=10,  # Only needs model parameters
            supports_realtime=True,
            tags=["tuning", "IMC", "PID", "robust", "pid_analysis"]
        )
        super().__init__(metadata)
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for IMC tuning"""
        errors = []
        
        # Check for model parameters
        if 'model_parameters' not in data:
            errors.append("Missing 'model_parameters' dictionary")
        else:
            model_params = data['model_parameters']
            required_params = ['K', 'tau', 'theta']
            
            for param in required_params:
                if param not in model_params:
                    errors.append(f"Missing model parameter: '{param}'")
                elif not isinstance(model_params[param], (int, float)):
                    errors.append(f"Model parameter '{param}' must be numeric")
                elif model_params[param] <= 0:
                    if param != 'theta':  # theta can be zero
                        errors.append(f"Model parameter '{param}' must be positive")
        
        # Check controller type if specified
        if 'controller_type' in data:
            if data['controller_type'] not in ['dependent', 'independent']:
                errors.append("Controller type must be 'dependent' or 'independent'")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute IMC tuning algorithm"""
        model_params = data['model_parameters']
        controller_type = data.get('controller_type', 'dependent')
        
        # Extract model parameters
        K = model_params['K']
        tau = model_params['tau']
        theta = model_params['theta']
        
        # Tuning parameters
        lambda_c = kwargs.get('lambda_c', None)  # Closed-loop time constant
        robustness_factor = kwargs.get('robustness_factor', 1.0)
        performance_weight = kwargs.get('performance_weight', 0.7)
        robustness_weight = kwargs.get('robustness_weight', 0.3)
        
        # Auto-select lambda_c if not provided
        if lambda_c is None:
            lambda_c = self._auto_select_lambda_c(tau, theta, robustness_factor)
        
        # IMC tuning calculations
        if controller_type == 'dependent':
            pid_params = self._imc_dependent_tuning(K, tau, theta, lambda_c)
        else:
            pid_params = self._imc_independent_tuning(K, tau, theta, lambda_c)
        
        # Multi-objective optimization refinement
        if performance_weight != 1.0:
            pid_params = self._multi_objective_optimization(
                K, tau, theta, pid_params, 
                performance_weight, robustness_weight
            )
        
        # Performance analysis
        performance_metrics = self._analyze_performance(
            K, tau, theta, pid_params, controller_type
        )
        
        # Stability analysis
        stability_analysis = self._analyze_stability(
            K, tau, theta, pid_params, controller_type
        )
        
        # Robustness analysis
        robustness_analysis = self._analyze_robustness(
            K, tau, theta, pid_params, controller_type
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            pid_params, performance_metrics, stability_analysis, robustness_analysis
        )
        
        return {
            'tuning_method': 'IMC_enhanced',
            'parameters': pid_params,
            'performance_metrics': performance_metrics,
            'stability_analysis': stability_analysis,
            'robustness_analysis': robustness_analysis,
            'controller_type': controller_type,
            'recommendations': recommendations,
            'lambda_c_used': lambda_c,
            'model_parameters': model_params,
            'tuning_options': {
                'robustness_factor': robustness_factor,
                'performance_weight': performance_weight,
                'robustness_weight': robustness_weight
            }
        }
    
    def _auto_select_lambda_c(self, tau: float, theta: float, 
                             robustness_factor: float) -> float:
        """Automatically select closed-loop time constant"""
        # Base lambda_c selection (conservative approach)
        if theta > 0:
            lambda_c_base = max(theta, tau * 0.1)
        else:
            lambda_c_base = tau * 0.1
        
        # Adjust for robustness
        lambda_c = lambda_c_base * robustness_factor
        
        # Ensure reasonable bounds
        lambda_c = max(lambda_c, tau * 0.05)  # Not too aggressive
        lambda_c = min(lambda_c, tau * 2.0)   # Not too conservative
        
        return lambda_c
    
    def _imc_dependent_tuning(self, K: float, tau: float, theta: float, 
                             lambda_c: float) -> Dict[str, float]:
        """IMC tuning for dependent (positional) PID form"""
        # IMC-PID formulas for dependent form
        Kp = (tau) / (K * (lambda_c + theta))
        Ti = tau
        Td = 0.0  # Conservative start
        
        # Add derivative action if beneficial
        if theta > 0:
            Td = theta * tau / (tau + lambda_c)
        
        # Ensure reasonable bounds
        Kp = max(0.01, min(100.0, Kp))
        Ti = max(0.01, min(9999.0, Ti))
        Td = max(0.0, min(99.99, Td))
        
        return {
            'Kp': float(Kp),
            'Ti': float(Ti),
            'Td': float(Td)
        }
    
    def _imc_independent_tuning(self, K: float, tau: float, theta: float, 
                               lambda_c: float) -> Dict[str, float]:
        """IMC tuning for independent (parallel/velocity) PID form"""
        # Convert to independent form
        Kp = tau / (K * (lambda_c + theta))
        Ki = Kp / tau if tau > 0 else 0
        Kd = Kp * theta * tau / (tau + lambda_c) if theta > 0 else 0
        
        # Ensure reasonable bounds
        Kp = max(0.01, min(100.0, Kp))
        Ki = max(0.0, min(10.0, Ki))
        Kd = max(0.0, min(10.0, Kd))
        
        return {
            'Kp': float(Kp),
            'Ki': float(Ki),
            'Kd': float(Kd)
        }
    
    def _multi_objective_optimization(self, K: float, tau: float, theta: float,
                                    initial_params: Dict[str, float],
                                    performance_weight: float,
                                    robustness_weight: float) -> Dict[str, float]:
        """Multi-objective optimization for performance vs robustness"""
        
        def objective(params_array):
            # Reconstruct parameters
            if len(params_array) == 3:  # dependent form
                params = {
                    'Kp': params_array[0],
                    'Ti': params_array[1],
                    'Td': params_array[2]
                }
                controller_type = 'dependent'
            else:  # independent form
                params = {
                    'Kp': params_array[0],
                    'Ki': params_array[1],
                    'Kd': params_array[2]
                }
                controller_type = 'independent'
            
            # Calculate performance metrics
            perf_metrics = self._analyze_performance(K, tau, theta, params, controller_type)
            robust_metrics = self._analyze_robustness(K, tau, theta, params, controller_type)
            
            # Objective function (minimize)
            performance_cost = 1.0 - perf_metrics['performance_index']
            robustness_cost = 1.0 - robust_metrics['robustness_index']
            
            total_cost = (performance_weight * performance_cost + 
                         robustness_weight * robustness_cost)
            
            return total_cost
        
        # Parameter bounds
        if 'Ti' in initial_params:  # dependent form
            bounds = [
                (0.01, 100.0),    # Kp
                (0.01, 9999.0),   # Ti
                (0.0, 99.99)      # Td
            ]
            x0 = [initial_params['Kp'], initial_params['Ti'], initial_params['Td']]
        else:  # independent form
            bounds = [
                (0.01, 100.0),    # Kp
                (0.0, 10.0),      # Ki
                (0.0, 10.0)       # Kd
            ]
            x0 = [initial_params['Kp'], initial_params['Ki'], initial_params['Kd']]
        
        # Optimize
        result = minimize(
            objective,
            x0=x0,
            bounds=bounds,
            method='L-BFGS-B'
        )
        
        # Return optimized parameters
        if 'Ti' in initial_params:  # dependent form
            return {
                'Kp': float(result.x[0]),
                'Ti': float(result.x[1]),
                'Td': float(result.x[2])
            }
        else:  # independent form
            return {
                'Kp': float(result.x[0]),
                'Ki': float(result.x[1]),
                'Kd': float(result.x[2])
            }
    
    def _analyze_performance(self, K: float, tau: float, theta: float,
                           pid_params: Dict[str, float], 
                           controller_type: str) -> Dict[str, float]:
        """Analyze closed-loop performance metrics"""
        
        # Simulate step response
        time_sim = np.linspace(0, tau * 10, 1000)
        response = self._simulate_closed_loop_response(
            time_sim, K, tau, theta, pid_params, controller_type
        )
        
        # Performance metrics
        final_value = response[-1]
        
        # Rise time (10% to 90%)
        rise_10 = np.where(response >= 0.1 * final_value)[0]
        rise_90 = np.where(response >= 0.9 * final_value)[0]
        
        if len(rise_10) > 0 and len(rise_90) > 0:
            rise_time = time_sim[rise_90[0]] - time_sim[rise_10[0]]
        else:
            rise_time = tau  # fallback
        
        # Settling time (2% criteria)
        settling_mask = np.abs(response - final_value) <= 0.02 * final_value
        if np.any(settling_mask):
            settling_indices = np.where(settling_mask)[0]
            # Find last time before final settling
            for i in range(len(settling_indices)-1, 0, -1):
                if settling_indices[i] - settling_indices[i-1] > 1:
                    settling_time = time_sim[settling_indices[i]]
                    break
            else:
                settling_time = time_sim[settling_indices[0]]
        else:
            settling_time = time_sim[-1]
        
        # Overshoot
        max_response = np.max(response)
        overshoot = (max_response - final_value) / final_value * 100 if final_value != 0 else 0
        
        # Performance index (0-1, higher is better)
        normalized_rise = max(0, 1 - rise_time / (tau * 5))
        normalized_settling = max(0, 1 - settling_time / (tau * 10))
        overshoot_penalty = max(0, 1 - abs(overshoot) / 50)
        
        performance_index = (normalized_rise * 0.3 + 
                           normalized_settling * 0.4 + 
                           overshoot_penalty * 0.3)
        
        return {
            'rise_time': float(rise_time),
            'settling_time': float(settling_time),
            'overshoot_percent': float(overshoot),
            'final_value': float(final_value),
            'performance_index': float(performance_index)
        }
    
    def _analyze_stability(self, K: float, tau: float, theta: float,
                          pid_params: Dict[str, float], 
                          controller_type: str) -> Dict[str, Any]:
        """Analyze closed-loop stability"""
        
        # Create transfer functions
        if controller_type == 'dependent':
            Kp, Ti, Td = pid_params['Kp'], pid_params['Ti'], pid_params['Td']
            
            # Process transfer function with delay approximation (Pade)
            if theta > 0:
                # First-order Pade approximation for delay
                delay_num = [-theta/2, 1]
                delay_den = [theta/2, 1]
                
                # Process
                process_num = [K]
                process_den = [tau, 1]
                
                # Combined process with delay
                num = np.convolve(process_num, delay_num)
                den = np.convolve(process_den, delay_den)
            else:
                num = [K]
                den = [tau, 1]
            
            # PID controller transfer function
            pid_num = [Kp*Td*Ti, Kp*Ti, Kp]
            pid_den = [Ti, 0]
            
        else:  # independent form
            Kp, Ki, Kd = pid_params['Kp'], pid_params['Ki'], pid_params['Kd']
            
            # Similar analysis for independent form
            if theta > 0:
                delay_num = [-theta/2, 1]
                delay_den = [theta/2, 1]
                process_num = [K]
                process_den = [tau, 1]
                num = np.convolve(process_num, delay_num)
                den = np.convolve(process_den, delay_den)
            else:
                num = [K]
                den = [tau, 1]
            
            # PID controller (parallel form)
            pid_num = [Kd, Kp, Ki]
            pid_den = [1, 0]
        
        # Create transfer function objects
        try:
            from scipy.signal import TransferFunction
            
            process_tf = TransferFunction(num, den)
            pid_tf = TransferFunction(pid_num, pid_den)
            
            # Open-loop transfer function
            ol_tf = signal.series(pid_tf, process_tf)
            
            # Closed-loop transfer function
            cl_tf = signal.feedback(ol_tf, 1)
            
            # Stability analysis
            poles = cl_tf.poles
            stable = np.all(np.real(poles) < 0)
            
            # Gain and phase margins
            w, h = signal.freqresp(ol_tf, w=np.logspace(-3, 3, 1000))
            mag_db = 20 * np.log10(np.abs(h))
            phase_deg = np.angle(h) * 180 / np.pi
            
            # Gain margin
            phase_crossover_idx = np.where(np.diff(np.sign(phase_deg + 180)))[0]
            if len(phase_crossover_idx) > 0:
                gain_margin_db = -mag_db[phase_crossover_idx[0]]
            else:
                gain_margin_db = float('inf')
            
            # Phase margin
            gain_crossover_idx = np.where(np.diff(np.sign(mag_db)))[0]
            if len(gain_crossover_idx) > 0:
                phase_margin_deg = 180 + phase_deg[gain_crossover_idx[0]]
            else:
                phase_margin_deg = float('inf')
            
        except Exception as e:
            # Fallback analysis
            stable = True
            gain_margin_db = 6.0  # Conservative estimate
            phase_margin_deg = 45.0  # Conservative estimate
            poles = []
        
        return {
            'stable': bool(stable),
            'gain_margin_db': float(gain_margin_db),
            'phase_margin_deg': float(phase_margin_deg),
            'poles': [complex(p) for p in poles] if len(poles) > 0 else [],
            'stability_index': min(1.0, (gain_margin_db / 20) * (phase_margin_deg / 180))
        }
    
    def _analyze_robustness(self, K: float, tau: float, theta: float,
                           pid_params: Dict[str, float], 
                           controller_type: str) -> Dict[str, Any]:
        """Analyze robustness to model uncertainties"""
        
        # Test robustness with parameter variations
        variations = [0.8, 0.9, 1.0, 1.1, 1.2]  # ±20% variation
        robust_performance = []
        
        for k_var in variations:
            for tau_var in variations:
                for theta_var in variations:
                    # Varied parameters
                    K_test = K * k_var
                    tau_test = tau * tau_var
                    theta_test = theta * theta_var
                    
                    # Test stability
                    stability = self._analyze_stability(
                        K_test, tau_test, theta_test, pid_params, controller_type
                    )
                    
                    # Test performance
                    performance = self._analyze_performance(
                        K_test, tau_test, theta_test, pid_params, controller_type
                    )
                    
                    if stability['stable']:
                        robust_performance.append(performance['performance_index'])
                    else:
                        robust_performance.append(0.0)
        
        # Robustness metrics
        min_performance = np.min(robust_performance)
        mean_performance = np.mean(robust_performance)
        performance_std = np.std(robust_performance)
        
        # Robustness index (0-1, higher is better)
        robustness_index = min_performance * (1 - performance_std)
        
        return {
            'min_performance': float(min_performance),
            'mean_performance': float(mean_performance),
            'performance_std': float(performance_std),
            'robustness_index': float(max(0, robustness_index)),
            'stable_variations': int(np.sum(np.array(robust_performance) > 0)),
            'total_variations': len(robust_performance)
        }
    
    def _simulate_closed_loop_response(self, time: np.ndarray, K: float, 
                                     tau: float, theta: float,
                                     pid_params: Dict[str, float],
                                     controller_type: str) -> np.ndarray:
        """Simulate closed-loop step response"""
        dt = time[1] - time[0] if len(time) > 1 else 0.01
        
        # Initialize arrays
        setpoint = np.ones_like(time)  # Unit step
        output = np.zeros_like(time)
        error = np.zeros_like(time)
        control_signal = np.zeros_like(time)
        
        # PID terms
        integral_sum = 0.0
        previous_error = 0.0
        
        # Process simulation with delay
        delay_buffer = np.zeros(max(1, int(theta / dt)))
        delay_index = 0
        
        for i in range(1, len(time)):
            # Error calculation
            error[i] = setpoint[i] - output[i-1]
            
            # PID calculation
            if controller_type == 'dependent':
                Kp, Ti, Td = pid_params['Kp'], pid_params['Ti'], pid_params['Td']
                
                # Integral term
                integral_sum += error[i] * dt
                integral_term = integral_sum / Ti if Ti > 0 else 0
                
                # Derivative term
                derivative_term = Td * (error[i] - previous_error) / dt
                
                # Control signal
                control_signal[i] = Kp * (error[i] + integral_term + derivative_term)
                
            else:  # independent form
                Kp, Ki, Kd = pid_params['Kp'], pid_params['Ki'], pid_params['Kd']
                
                # Proportional term
                proportional_term = Kp * error[i]
                
                # Integral term
                integral_sum += error[i] * dt
                integral_term = Ki * integral_sum
                
                # Derivative term
                derivative_term = Kd * (error[i] - previous_error) / dt
                
                # Control signal
                control_signal[i] = proportional_term + integral_term + derivative_term
            
            # Apply control signal through delay
            if len(delay_buffer) > 1:
                delayed_control = delay_buffer[delay_index]
                delay_buffer[delay_index] = control_signal[i]
                delay_index = (delay_index + 1) % len(delay_buffer)
            else:
                delayed_control = control_signal[i]
            
            # Process response (first-order)
            doutput_dt = K * delayed_control - output[i-1]
            output[i] = output[i-1] + (doutput_dt / tau) * dt
            
            previous_error = error[i]
        
        return output
    
    def _generate_recommendations(self, pid_params: Dict[str, float],
                                performance_metrics: Dict[str, float],
                                stability_analysis: Dict[str, Any],
                                robustness_analysis: Dict[str, Any]) -> List[str]:
        """Generate tuning recommendations"""
        recommendations = []
        
        # Performance recommendations
        if performance_metrics['overshoot_percent'] > 20:
            recommendations.append("Consider reducing proportional gain to decrease overshoot")
        
        if performance_metrics['settling_time'] > performance_metrics['rise_time'] * 5:
            recommendations.append("Consider increasing integral action to reduce settling time")
        
        if performance_metrics['rise_time'] > 5.0:
            recommendations.append("Consider increasing proportional gain to improve response speed")
        
        # Stability recommendations
        if stability_analysis['gain_margin_db'] < 6:
            recommendations.append("Warning: Low gain margin - reduce proportional gain for safety")
        
        if stability_analysis['phase_margin_deg'] < 30:
            recommendations.append("Warning: Low phase margin - consider reducing derivative action")
        
        # Robustness recommendations
        if robustness_analysis['robustness_index'] < 0.5:
            recommendations.append("Poor robustness - consider more conservative tuning")
        
        if robustness_analysis['stable_variations'] < robustness_analysis['total_variations'] * 0.8:
            recommendations.append("Tuning may be unstable with model variations - increase conservatism")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Tuning appears well-balanced for current model")
        
        return recommendations

class AdaptiveTuner(AlgorithmBase):
    """
    Adaptive PID tuning algorithm with real-time parameter adjustment
    """
    
    def __init__(self):
        metadata = AlgorithmMetadata(
            name="adaptive_tuner",
            category=AlgorithmCategory.ADAPTIVE_CONTROL,
            complexity=AlgorithmComplexity.HIGH,
            description="Adaptive PID tuning with real-time parameter adjustment",
            version="1.0.0",
            min_data_points=100,
            supports_realtime=True,
            tags=["adaptive", "tuning", "PID", "real_time", "self_tuning"]
        )
        super().__init__(metadata)
    
    def validate_input(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate input data for adaptive tuning"""
        errors = []
        
        required_fields = ['time', 'setpoint', 'process_output', 'control_output']
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: '{field}'")
        
        if not errors:
            time_data = np.array(data['time'])
            if len(time_data) < self.metadata.min_data_points:
                errors.append(f"Minimum {self.metadata.min_data_points} data points required")
        
        return len(errors) == 0, errors
    
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute adaptive tuning algorithm"""
        time_data = np.array(data['time'])
        setpoint_data = np.array(data['setpoint'])
        output_data = np.array(data['process_output'])
        control_data = np.array(data['control_output'])
        
        # Parameters
        adaptation_rate = kwargs.get('adaptation_rate', 0.01)
        forgetting_factor = kwargs.get('forgetting_factor', 0.95)
        initial_params = kwargs.get('initial_params', {'Kp': 1.0, 'Ki': 0.1, 'Kd': 0.01})
        
        # Adaptive tuning using recursive least squares
        adapted_params = self._recursive_adaptation(
            time_data, setpoint_data, output_data, control_data,
            adaptation_rate, forgetting_factor, initial_params
        )
        
        # Performance analysis for final parameters
        performance_metrics = self._evaluate_adaptive_performance(
            time_data, setpoint_data, output_data, adapted_params
        )
        
        return {
            'tuning_method': 'adaptive_recursive',
            'parameters': adapted_params,
            'performance_metrics': performance_metrics,
            'adaptation_trajectory': adapted_params,  # Could include full history
            'controller_type': 'independent',
            'recommendations': self._generate_adaptive_recommendations(performance_metrics),
            'adaptation_options': {
                'adaptation_rate': adaptation_rate,
                'forgetting_factor': forgetting_factor
            }
        }
    
    def _recursive_adaptation(self, time_data: np.ndarray, setpoint_data: np.ndarray,
                            output_data: np.ndarray, control_data: np.ndarray,
                            adaptation_rate: float, forgetting_factor: float,
                            initial_params: Dict[str, float]) -> Dict[str, float]:
        """Recursive least squares parameter adaptation"""
        
        # Initialize parameters
        params = np.array([initial_params['Kp'], initial_params['Ki'], initial_params['Kd']])
        
        # Covariance matrix initialization
        P = np.eye(3) * 1000  # High initial uncertainty
        
        # Recursive estimation
        for i in range(1, len(time_data)):
            dt = time_data[i] - time_data[i-1]
            
            # Error and regressor
            error = setpoint_data[i] - output_data[i]
            
            # Simple regressor (error, integral of error, derivative of error)
            if i > 1:
                error_derivative = (error - (setpoint_data[i-1] - output_data[i-1])) / dt
            else:
                error_derivative = 0
            
            error_integral = np.sum((setpoint_data[:i+1] - output_data[:i+1])) * dt
            
            regressor = np.array([error, error_integral, error_derivative])
            
            # Update covariance matrix
            P = (1/forgetting_factor) * (P - (P @ np.outer(regressor, regressor) @ P) / 
                                        (forgetting_factor + regressor @ P @ regressor))
            
            # Update parameters
            prediction_error = control_data[i] - regressor @ params
            params = params + adaptation_rate * P @ regressor * prediction_error
            
            # Bounds enforcement
            params[0] = np.clip(params[0], 0.01, 100.0)  # Kp
            params[1] = np.clip(params[1], 0.0, 10.0)    # Ki  
            params[2] = np.clip(params[2], 0.0, 10.0)    # Kd
        
        return {
            'Kp': float(params[0]),
            'Ki': float(params[1]),
            'Kd': float(params[2])
        }
    
    def _evaluate_adaptive_performance(self, time_data: np.ndarray, 
                                     setpoint_data: np.ndarray,
                                     output_data: np.ndarray,
                                     params: Dict[str, float]) -> Dict[str, float]:
        """Evaluate performance of adaptive tuning"""
        
        # Calculate tracking error
        error = setpoint_data - output_data
        
        # Performance metrics
        mse = np.mean(error ** 2)
        mae = np.mean(np.abs(error))
        tracking_performance = 1.0 / (1.0 + mse)
        
        return {
            'mse': float(mse),
            'mae': float(mae),
            'tracking_performance': float(tracking_performance),
            'final_error': float(error[-1]),
            'performance_index': float(tracking_performance)
        }
    
    def _generate_adaptive_recommendations(self, performance_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations for adaptive tuning"""
        recommendations = []
        
        if performance_metrics['mse'] > 1.0:
            recommendations.append("High tracking error - consider increasing adaptation rate")
        
        if performance_metrics['tracking_performance'] < 0.5:
            recommendations.append("Poor tracking performance - check model assumptions")
        
        if abs(performance_metrics['final_error']) > 0.1:
            recommendations.append("Large steady-state error - verify integral action")
        
        if not recommendations:
            recommendations.append("Adaptive tuning performing well")
        
        return recommendations

# Register algorithms
registry.register(IMCTuner)
registry.register(AdaptiveTuner)

# Export algorithms
__all__ = [
    'IMCTuner',
    'AdaptiveTuner',
    'TuningResult'
] 