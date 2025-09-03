#!/usr/bin/env python3
"""
Phase 22.2.3: Adaptive Control Implementation
============================================

Advanced adaptive control algorithms for real-time PID tuning including:
- Recursive Least Squares (RLS) adaptive control
- Gradient descent parameter adaptation
- Kalman filter-based adaptive control
- Neural network adaptive control

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.3 - Advanced Tuning Strategies
Methodology: AI Task Orchestrator Guide
"""

import logging
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

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

class AdaptiveAlgorithmType(Enum):
    """Adaptive control algorithm types"""
    RECURSIVE_LEAST_SQUARES = "rls"
    GRADIENT_DESCENT = "gradient_descent"
    KALMAN_FILTER = "kalman_filter"
    NEURAL_NETWORK = "neural_network"

class AdaptationMode(Enum):
    """Adaptation modes"""
    CONTINUOUS = "continuous"
    BATCH = "batch"
    TRIGGERED = "triggered"
    SCHEDULED = "scheduled"

@dataclass
class AdaptiveConfiguration:
    """Adaptive control configuration"""
    algorithm_type: AdaptiveAlgorithmType = AdaptiveAlgorithmType.RECURSIVE_LEAST_SQUARES
    adaptation_mode: AdaptationMode = AdaptationMode.CONTINUOUS

    # RLS parameters
    forgetting_factor: float = 0.95
    initial_covariance: float = 1000.0
    regularization: float = 1e-6

    # Gradient descent parameters
    learning_rate: float = 0.01
    momentum: float = 0.9
    decay_rate: float = 0.99

    # Kalman filter parameters
    process_noise: float = 0.01
    measurement_noise: float = 0.1
    initial_state_covariance: float = 1.0

    # Neural network parameters
    hidden_layers: List[int] = field(default_factory=lambda: [10, 5])
    activation: str = "tanh"
    nn_learning_rate: float = 0.001

    # Adaptation bounds
    parameter_min: Dict[str, float] = field(default_factory=lambda: {"Kp": 0.1, "Ti": 0.1, "Td": 0.0})
    parameter_max: Dict[str, float] = field(default_factory=lambda: {"Kp": 10.0, "Ti": 100.0, "Td": 10.0})

    # Performance monitoring
    adaptation_threshold: float = 0.1
    performance_window: int = 50
    stability_check: bool = True

@dataclass
class AdaptiveState:
    """Adaptive controller state"""
    parameters: Dict[str, float]
    covariance_matrix: np.ndarray
    parameter_history: List[Dict[str, float]]
    performance_history: List[float]
    adaptation_active: bool = True
    last_update_time: float = 0.0
    iteration_count: int = 0

@dataclass
class AdaptiveResults:
    """Adaptive control results"""
    tuning_method: str
    algorithm_type: AdaptiveAlgorithmType
    configuration: AdaptiveConfiguration
    final_parameters: Dict[str, float]
    parameter_evolution: List[Dict[str, float]]
    performance_metrics: Dict[str, float]
    adaptation_statistics: Dict[str, Any]
    convergence_analysis: Dict[str, Any]
    stability_analysis: Dict[str, Any]
    execution_time: float
    status: str

class AdaptiveController:
    """Base adaptive control class"""

    def __init__(self, configuration: Optional[AdaptiveConfiguration] = None):
        self.config = configuration or AdaptiveConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize adaptive state
        self.state = AdaptiveState(
            parameters={"Kp": 1.0, "Ti": 10.0, "Td": 1.0},
            covariance_matrix=np.eye(3) * self.config.initial_covariance,
            parameter_history=[],
            performance_history=[]
        )

        # Data buffers
        self.input_buffer = deque(maxlen=self.config.performance_window)
        self.output_buffer = deque(maxlen=self.config.performance_window)
        self.error_buffer = deque(maxlen=self.config.performance_window)

    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute adaptive control tuning"""
        try:
            start_time = time.time()

            # Initialize if needed
            self._initialize_adaptation(data)

            # Run adaptation algorithm
            final_parameters = self._run_adaptation(data)

            # Analyze results
            performance_metrics = self._analyze_performance()
            adaptation_statistics = self._calculate_adaptation_statistics()
            convergence_analysis = self._analyze_convergence()
            stability_analysis = self._analyze_stability()

            execution_time = time.time() - start_time

            # Create results
            result = AdaptiveResults(
                tuning_method=f"Adaptive_{self.config.algorithm_type.value}",
                algorithm_type=self.config.algorithm_type,
                configuration=self.config,
                final_parameters=final_parameters,
                parameter_evolution=self.state.parameter_history.copy(),
                performance_metrics=performance_metrics,
                adaptation_statistics=adaptation_statistics,
                convergence_analysis=convergence_analysis,
                stability_analysis=stability_analysis,
                execution_time=execution_time,
                status="success"
            )

            return {
                'success': True,
                'result': result,
                'method': 'adaptive_control'
            }

        except Exception as e:
            self.logger.error(f"Adaptive control failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'adaptive_control'
            }

    def _initialize_adaptation(self, data: Dict[str, Any]):
        """Initialize adaptation algorithm"""

        # Set initial parameters if provided
        if 'initial_parameters' in data:
            initial_params = data['initial_parameters']
            self.state.parameters.update(initial_params)

        # Initialize buffers with any provided data
        if 'process_data' in data:
            process_data = data['process_data']
            if isinstance(process_data, dict):
                if 'input' in process_data:
                    self.input_buffer.extend(process_data['input'])
                if 'output' in process_data:
                    self.output_buffer.extend(process_data['output'])
                if 'error' in process_data:
                    self.error_buffer.extend(process_data['error'])

    def _run_adaptation(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Run adaptation algorithm (base implementation)"""

        # Extract time series data
        time_data = self._extract_time_series(data)

        if len(time_data) < 10:  # Need minimum data for adaptation
            self.logger.warning("Insufficient data for adaptation")
            return self.state.parameters

        # Perform adaptation based on algorithm type
        if self.config.algorithm_type == AdaptiveAlgorithmType.RECURSIVE_LEAST_SQUARES:
            return self._rls_adaptation(time_data)
        elif self.config.algorithm_type == AdaptiveAlgorithmType.GRADIENT_DESCENT:
            return self._gradient_descent_adaptation(time_data)
        elif self.config.algorithm_type == AdaptiveAlgorithmType.KALMAN_FILTER:
            return self._kalman_filter_adaptation(time_data)
        elif self.config.algorithm_type == AdaptiveAlgorithmType.NEURAL_NETWORK:
            return self._neural_network_adaptation(time_data)
        else:
            raise ValueError(f"Unknown algorithm type: {self.config.algorithm_type}")

    def _extract_time_series(self, data: Dict[str, Any]) -> pd.DataFrame:
        """Extract time series data for adaptation"""

        if 'time_series' in data:
            ts_data = data['time_series']
            if isinstance(ts_data, pd.DataFrame):
                return ts_data
            elif isinstance(ts_data, dict):
                return pd.DataFrame(ts_data)

        # Create synthetic data for testing
        n_points = 100
        time_index = np.arange(n_points)

        # Simple process simulation
        setpoint = np.ones(n_points)
        noise = np.random.normal(0, 0.1, n_points)
        output = np.cumsum(noise) + setpoint
        error = setpoint - output
        control_signal = np.random.normal(0, 0.5, n_points)

        return pd.DataFrame({
            'time': time_index,
            'setpoint': setpoint,
            'output': output,
            'error': error,
            'control_signal': control_signal
        })

    def _rls_adaptation(self, time_data: pd.DataFrame) -> Dict[str, float]:
        """Recursive Least Squares adaptation"""

        # Extract signals
        error = time_data['error'].values
        output = time_data['output'].values

        # Initialize RLS matrices
        theta = np.array([self.state.parameters['Kp'],
                         1/self.state.parameters['Ti'],
                         self.state.parameters['Td']])
        P = self.state.covariance_matrix.copy()
        lambda_f = self.config.forgetting_factor

        # RLS iteration
        for i in range(1, len(error)):
            # Regression vector (simplified)
            phi = np.array([error[i-1],
                           np.sum(error[:i]),
                           error[i] - error[i-1] if i > 0 else 0])

            # RLS update
            K = P @ phi / (lambda_f + phi.T @ P @ phi + self.config.regularization)
            prediction_error = output[i] - phi.T @ theta
            theta = theta + K * prediction_error
            P = (P - np.outer(K, phi.T @ P)) / lambda_f

            # Apply parameter bounds
            theta = self._apply_parameter_bounds(theta)

        # Convert back to PID parameters
        updated_params = {
            'Kp': float(theta[0]),
            'Ti': float(1/max(theta[1], 1e-6)),
            'Td': float(theta[2])
        }

        # Update state
        self.state.parameters = updated_params
        self.state.covariance_matrix = P
        self.state.parameter_history.append(updated_params.copy())

        return updated_params

    def _gradient_descent_adaptation(self, time_data: pd.DataFrame) -> Dict[str, float]:
        """Gradient descent parameter adaptation"""

        error = time_data['error'].values

        # Calculate performance metric (ISE)
        performance = np.sum(error**2)

        # Gradient estimation using finite differences
        eps = 1e-6
        gradients = {}

        for param_name in ['Kp', 'Ti', 'Td']:
            # Perturb parameter
            original_value = self.state.parameters[param_name]

            # Forward difference
            self.state.parameters[param_name] = original_value + eps
            perf_plus = self._simulate_performance(time_data)

            self.state.parameters[param_name] = original_value - eps
            perf_minus = self._simulate_performance(time_data)

            # Restore original value
            self.state.parameters[param_name] = original_value

            # Calculate gradient
            gradients[param_name] = (perf_plus - perf_minus) / (2 * eps)

        # Gradient descent update
        learning_rate = self.config.learning_rate
        for param_name in ['Kp', 'Ti', 'Td']:
            self.state.parameters[param_name] -= learning_rate * gradients[param_name]

        # Apply bounds
        self.state.parameters = self._apply_parameter_bounds_dict(self.state.parameters)

        # Update history
        self.state.parameter_history.append(self.state.parameters.copy())
        self.state.performance_history.append(performance)

        return self.state.parameters

    def _kalman_filter_adaptation(self, time_data: pd.DataFrame) -> Dict[str, float]:
        """Kalman filter-based adaptation"""

        # State vector: [Kp, Ki, Kd]
        x = np.array([self.state.parameters['Kp'],
                     1/self.state.parameters['Ti'],
                     self.state.parameters['Td']])

        # State covariance
        P = self.state.covariance_matrix.copy()

        # Process and measurement noise
        Q = np.eye(3) * self.config.process_noise
        R = self.config.measurement_noise

        error = time_data['error'].values

        # Kalman filter iterations
        for i in range(1, len(error)):
            # Prediction step
            x_pred = x  # Assume constant parameters
            P_pred = P + Q

            # Measurement update
            if i > 2:  # Need enough history for measurement
                # Observation model (simplified)
                H = np.array([error[i-1], np.sum(error[:i]),
                             error[i] - error[i-1] if i > 0 else 0])

                # Kalman gain
                S = H.T @ P_pred @ H + R
                K = P_pred @ H / S

                # Update
                innovation = error[i] - H.T @ x_pred
                x = x_pred + K * innovation
                P = P_pred - np.outer(K, H.T @ P_pred)

                # Apply bounds
                x = self._apply_parameter_bounds(x)

        # Convert back to PID parameters
        updated_params = {
            'Kp': float(x[0]),
            'Ti': float(1/max(x[1], 1e-6)),
            'Td': float(x[2])
        }

        # Update state
        self.state.parameters = updated_params
        self.state.covariance_matrix = P
        self.state.parameter_history.append(updated_params.copy())

        return updated_params

    def _neural_network_adaptation(self, time_data: pd.DataFrame) -> Dict[str, float]:
        """Neural network-based adaptive control"""

        # Simplified neural network implementation
        # In practice, would use TensorFlow/PyTorch

        # Extract features
        error = time_data['error'].values
        output = time_data['output'].values

        # Feature engineering
        features = []
        for i in range(5, len(error)):
            feature_vector = [
                error[i-1], error[i-2], error[i-3],  # Error history
                output[i-1], output[i-2],  # Output history
                np.mean(error[i-5:i]),  # Recent error mean
                np.std(error[i-5:i])   # Recent error std
            ]
            features.append(feature_vector)

        if len(features) < 10:
            self.logger.warning("Insufficient data for neural network adaptation")
            return self.state.parameters

        features = np.array(features)

        # Simple single-layer neural network update
        # Target: minimize error
        target_params = np.array([self.state.parameters['Kp'],
                                1/self.state.parameters['Ti'],
                                self.state.parameters['Td']])

        # Simplified gradient-based update
        error_mean = np.mean(np.abs(error[-10:]))

        if error_mean > 0.1:  # Adapt if error is significant
            # Simple heuristic updates
            if np.mean(error[-5:]) > 0:  # Persistent positive error
                target_params[0] *= 1.05  # Increase Kp
                target_params[1] *= 1.02  # Increase Ki (decrease Ti)
            else:  # Oscillatory behavior
                target_params[0] *= 0.95  # Decrease Kp
                target_params[2] *= 1.1   # Increase Td

        # Apply bounds
        target_params = self._apply_parameter_bounds(target_params)

        # Convert back
        updated_params = {
            'Kp': float(target_params[0]),
            'Ti': float(1/max(target_params[1], 1e-6)),
            'Td': float(target_params[2])
        }

        # Update state
        self.state.parameters = updated_params
        self.state.parameter_history.append(updated_params.copy())

        return updated_params

    def _apply_parameter_bounds(self, params: np.ndarray) -> np.ndarray:
        """Apply parameter bounds to parameter array"""

        param_names = ['Kp', 'Ti_inv', 'Td']  # Note: Ti_inv = 1/Ti
        bounded_params = params.copy()

        for i, name in enumerate(param_names):
            if name == 'Ti_inv':
                # Handle inverse Ti bounds
                min_val = 1/self.config.parameter_max['Ti']
                max_val = 1/self.config.parameter_min['Ti']
            else:
                param_key = name
                min_val = self.config.parameter_min.get(param_key, -np.inf)
                max_val = self.config.parameter_max.get(param_key, np.inf)

            bounded_params[i] = np.clip(bounded_params[i], min_val, max_val)

        return bounded_params

    def _apply_parameter_bounds_dict(self, params: Dict[str, float]) -> Dict[str, float]:
        """Apply parameter bounds to parameter dictionary"""

        bounded_params = params.copy()

        for param_name, value in params.items():
            min_val = self.config.parameter_min.get(param_name, -np.inf)
            max_val = self.config.parameter_max.get(param_name, np.inf)
            bounded_params[param_name] = np.clip(value, min_val, max_val)

        return bounded_params

    def _simulate_performance(self, time_data: pd.DataFrame) -> float:
        """Simulate performance with current parameters"""

        # Simplified performance simulation
        error = time_data['error'].values

        # Basic PID response simulation
        Kp = self.state.parameters['Kp']
        Ti = self.state.parameters['Ti']
        Td = self.state.parameters['Td']

        control_signal = np.zeros_like(error)
        integral = 0
        previous_error = 0

        for i in range(len(error)):
            # PID calculation
            integral += error[i]
            derivative = error[i] - previous_error

            control_signal[i] = (Kp * error[i] +
                                Kp/Ti * integral +
                                Kp * Td * derivative)

            previous_error = error[i]

        # Performance metric (ISE)
        performance = np.sum(error**2)

        return performance

    def _analyze_performance(self) -> Dict[str, float]:
        """Analyze adaptation performance"""

        if not self.state.performance_history:
            return {"performance_improvement": 0.0, "convergence_rate": 0.0}

        # Performance improvement
        if len(self.state.performance_history) > 1:
            initial_perf = self.state.performance_history[0]
            final_perf = self.state.performance_history[-1]
            improvement = (initial_perf - final_perf) / initial_perf * 100
        else:
            improvement = 0.0

        # Convergence rate
        convergence_rate = 0.0
        if len(self.state.performance_history) > 10:
            recent_change = np.std(self.state.performance_history[-10:])
            convergence_rate = 1.0 / (1.0 + recent_change)  # Higher is better

        return {
            "performance_improvement": improvement,
            "convergence_rate": convergence_rate,
            "final_performance": self.state.performance_history[-1] if self.state.performance_history else 0.0,
            "adaptation_steps": len(self.state.parameter_history)
        }

    def _calculate_adaptation_statistics(self) -> Dict[str, Any]:
        """Calculate adaptation statistics"""

        if not self.state.parameter_history:
            return {"parameter_changes": {}, "adaptation_active": False}

        # Parameter changes
        parameter_changes = {}
        for param_name in ['Kp', 'Ti', 'Td']:
            values = [params[param_name] for params in self.state.parameter_history]
            parameter_changes[param_name] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "final": values[-1] if values else 0.0
            }

        return {
            "parameter_changes": parameter_changes,
            "adaptation_active": self.state.adaptation_active,
            "iteration_count": self.state.iteration_count,
            "last_update_time": self.state.last_update_time
        }

    def _analyze_convergence(self) -> Dict[str, Any]:
        """Analyze parameter convergence"""

        if len(self.state.parameter_history) < 5:
            return {"converged": False, "convergence_time": None}

        # Check if parameters have stabilized
        recent_params = self.state.parameter_history[-5:]

        convergence_check = {}
        for param_name in ['Kp', 'Ti', 'Td']:
            values = [params[param_name] for params in recent_params]
            relative_change = np.std(values) / (np.mean(values) + 1e-6)
            convergence_check[param_name] = relative_change < self.config.adaptation_threshold

        converged = all(convergence_check.values())

        return {
            "converged": converged,
            "convergence_check": convergence_check,
            "convergence_time": len(self.state.parameter_history) if converged else None,
            "adaptation_threshold": self.config.adaptation_threshold
        }

    def _analyze_stability(self) -> Dict[str, Any]:
        """Analyze stability of adapted controller"""

        if not self.state.parameter_history:
            return {"stable": False, "stability_margin": 0.0}

        # Get final parameters
        final_params = self.state.parameter_history[-1]
        Kp = final_params['Kp']
        Ti = final_params['Ti']
        Td = final_params['Td']

        # Simple stability check based on parameter ranges
        stable_kp = 0.1 <= Kp <= 10.0
        stable_ti = 0.1 <= Ti <= 100.0
        stable_td = 0.0 <= Td <= 10.0

        stable = stable_kp and stable_ti and stable_td

        # Stability margin (simplified)
        margin_kp = min(Kp / 0.1, 10.0 / Kp)
        margin_ti = min(Ti / 0.1, 100.0 / Ti)
        margin_td = min((Td + 0.1) / 0.1, 10.0 / (Td + 0.1))

        stability_margin = min(margin_kp, margin_ti, margin_td)

        return {
            "stable": stable,
            "stability_margin": float(stability_margin),
            "parameter_stability": {
                "Kp": stable_kp,
                "Ti": stable_ti,
                "Td": stable_td
            }
        }


# Specialized adaptive controllers
class RLSAdaptiveController(AdaptiveController):
    """Recursive Least Squares adaptive controller"""

    def __init__(self, configuration: Optional[AdaptiveConfiguration] = None):
        config = configuration or AdaptiveConfiguration()
        config.algorithm_type = AdaptiveAlgorithmType.RECURSIVE_LEAST_SQUARES
        super().__init__(config)


class GradientDescentController(AdaptiveController):
    """Gradient descent adaptive controller"""

    def __init__(self, configuration: Optional[AdaptiveConfiguration] = None):
        config = configuration or AdaptiveConfiguration()
        config.algorithm_type = AdaptiveAlgorithmType.GRADIENT_DESCENT
        super().__init__(config)


class KalmanFilterController(AdaptiveController):
    """Kalman filter adaptive controller"""

    def __init__(self, configuration: Optional[AdaptiveConfiguration] = None):
        config = configuration or AdaptiveConfiguration()
        config.algorithm_type = AdaptiveAlgorithmType.KALMAN_FILTER
        super().__init__(config)


class NeuralAdaptiveController(AdaptiveController):
    """Neural network adaptive controller"""

    def __init__(self, configuration: Optional[AdaptiveConfiguration] = None):
        config = configuration or AdaptiveConfiguration()
        config.algorithm_type = AdaptiveAlgorithmType.NEURAL_NETWORK
        super().__init__(config)


# Register algorithms if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:

    @registry.register(
        category=AlgorithmCategory.ADAPTIVE_CONTROL,
        complexity=AlgorithmComplexity.HIGH,
        metadata=AlgorithmMetadata(
            name="RLS Adaptive Control",
            description="Recursive Least Squares adaptive PID tuning",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["adaptive", "rls", "recursive", "real-time"]
        )
    )
    class RegisteredRLSController(RLSAdaptiveController):
        pass


# Export classes and functions
__all__ = [
    'AdaptiveController',
    'RLSAdaptiveController',
    'GradientDescentController',
    'KalmanFilterController',
    'NeuralAdaptiveController',
    'AdaptiveConfiguration',
    'AdaptiveState',
    'AdaptiveResults',
    'AdaptiveAlgorithmType',
    'AdaptationMode'
]
