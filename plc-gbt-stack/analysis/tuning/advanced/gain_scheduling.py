#!/usr/bin/env python3
"""
Phase 22.2.3: Gain Scheduling Implementation
===========================================

Advanced gain scheduling algorithms for operating point dependent PID tuning:
- Linear interpolation gain scheduling
- Polynomial interpolation gain scheduling  
- Lookup table-based gain scheduling
- Fuzzy logic gain scheduling

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.3 - Advanced Tuning Strategies
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
import logging
from scipy import interpolate, optimize
from scipy.spatial.distance import cdist
from enum import Enum
import time
from datetime import datetime

# Import algorithm base class if available
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

class GainScheduleType(Enum):
    """Gain scheduling interpolation types"""
    LINEAR = "linear"
    POLYNOMIAL = "polynomial"
    LOOKUP_TABLE = "lookup_table"
    FUZZY_LOGIC = "fuzzy_logic"
    SPLINE = "spline"
    NEURAL_NETWORK = "neural_network"

class SchedulingVariable(Enum):
    """Common scheduling variables"""
    SETPOINT = "setpoint"
    PROCESS_VARIABLE = "process_variable"
    LOAD = "load"
    FLOW_RATE = "flow_rate"
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    CUSTOM = "custom"

@dataclass
class OperatingPoint:
    """Operating point definition"""
    variables: Dict[str, float]
    parameters: Dict[str, float]
    weight: float = 1.0
    label: str = ""
    active: bool = True

@dataclass
class GainScheduleConfiguration:
    """Gain scheduling configuration"""
    schedule_type: GainScheduleType = GainScheduleType.LINEAR
    scheduling_variables: List[str] = field(default_factory=lambda: ["setpoint"])
    
    # Operating points
    operating_points: List[OperatingPoint] = field(default_factory=list)
    
    # Interpolation parameters
    interpolation_method: str = "linear"
    extrapolation_mode: str = "nearest"  # nearest, linear, constant
    smoothing_factor: float = 0.0
    
    # Polynomial parameters
    polynomial_order: int = 2
    regularization: float = 1e-6
    
    # Fuzzy logic parameters
    membership_functions: str = "triangular"  # triangular, gaussian, trapezoidal
    num_fuzzy_sets: int = 5
    defuzzification_method: str = "centroid"  # centroid, weighted_average, max
    
    # Performance parameters
    transition_time: float = 5.0  # seconds
    update_rate: float = 1.0  # Hz
    stability_check: bool = True
    
    # Bounds
    parameter_bounds: Dict[str, Tuple[float, float]] = field(default_factory=lambda: {
        "Kp": (0.1, 10.0),
        "Ti": (0.1, 100.0),
        "Td": (0.0, 10.0)
    })

@dataclass
class GainScheduleResults:
    """Gain scheduling results"""
    tuning_method: str
    schedule_type: GainScheduleType
    configuration: GainScheduleConfiguration
    interpolation_functions: Dict[str, Any]
    operating_points: List[OperatingPoint]
    performance_metrics: Dict[str, float]
    validation_results: Dict[str, Any]
    transition_analysis: Dict[str, Any]
    stability_analysis: Dict[str, Any]
    execution_time: float
    status: str
    parameters: Optional[Dict[str, float]] = None

class GainScheduler:
    """Base gain scheduling class"""
    
    def __init__(self, configuration: Optional[GainScheduleConfiguration] = None):
        self.config = configuration or GainScheduleConfiguration()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Interpolation functions
        self.interpolators = {}
        self.parameter_functions = {}
        
        # Fuzzy logic components
        self.membership_functions = {}
        self.fuzzy_rules = []
        
        # Validation data
        self.validation_points = []
        
    def execute(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Execute gain scheduling setup"""
        try:
            start_time = time.time()
            
            # Extract operating points
            operating_points = self._extract_operating_points(data)
            
            # Build interpolation functions
            interpolation_functions = self._build_interpolators(operating_points)
            
            # Validate interpolation
            validation_results = self._validate_interpolation(operating_points)
            
            # Analyze transitions
            transition_analysis = self._analyze_transitions(operating_points)
            
            # Stability analysis
            stability_analysis = self._analyze_stability(operating_points)
            
            # Performance metrics
            performance_metrics = self._calculate_performance_metrics(validation_results)
            
            execution_time = time.time() - start_time
            
            # Create results
                        # Extract representative parameters for validation
            representative_parameters = self._extract_representative_parameters(operating_points)
            
            result = GainScheduleResults(
                tuning_method=f"GainSchedule_{self.config.schedule_type.value}",
                schedule_type=self.config.schedule_type,
                configuration=self.config,
                interpolation_functions=interpolation_functions,
                operating_points=operating_points,
                performance_metrics=performance_metrics,
                validation_results=validation_results,
                transition_analysis=transition_analysis,
                stability_analysis=stability_analysis,
                execution_time=execution_time,
                status="success"
            )
            
            # Add standard parameters field for validation
            result.parameters = representative_parameters
            
            return {
                'success': True,
                'result': result,
                'method': 'gain_scheduling'
            }
            
        except Exception as e:
            self.logger.error(f"Gain scheduling failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'gain_scheduling'
            }
    
    def _extract_representative_parameters(self, operating_points: List[OperatingPoint]) -> Dict[str, float]:
        """Extract representative PID parameters from operating points"""
        
        if not operating_points:
            return {'Kp': 1.0, 'Ti': 10.0, 'Td': 0.1}
        
        # Get parameters from first operating point as representative
        first_point = operating_points[0]
        params = first_point.parameters
        
        return {
            'Kp': params.get('Kp', 1.0),
            'Ti': params.get('Ti', 10.0), 
            'Td': params.get('Td', 0.1)
        }

    def _extract_operating_points(self, data: Dict[str, Any]) -> List[OperatingPoint]:
        """Extract operating points from data"""
        
        if 'operating_points' in data:
            points = []
            for point_data in data['operating_points']:
                point = OperatingPoint(
                    variables=point_data.get('variables', {}),
                    parameters=point_data.get('parameters', {}),
                    weight=point_data.get('weight', 1.0),
                    label=point_data.get('label', ''),
                    active=point_data.get('active', True)
                )
                points.append(point)
            return points
        
        # Create default operating points if none provided
        return self._create_default_operating_points(data)
    
    def _create_default_operating_points(self, data: Dict[str, Any]) -> List[OperatingPoint]:
        """Create default operating points based on process characteristics"""
        
        # Extract process parameters
        process_gain = data.get('process_gain', 1.0)
        time_constant = data.get('time_constant', 10.0)
        dead_time = data.get('dead_time', 1.0)
        
        # Create operating points at different setpoint levels
        setpoint_range = data.get('setpoint_range', [0, 100])
        num_points = data.get('num_operating_points', 5)
        
        points = []
        setpoints = np.linspace(setpoint_range[0], setpoint_range[1], num_points)
        
        for i, sp in enumerate(setpoints):
            # Simple gain scheduling based on setpoint
            # Higher setpoints might need different tuning
            gain_factor = 1.0 + 0.1 * (sp - setpoint_range[0]) / (setpoint_range[1] - setpoint_range[0])
            
            # Calculate PID parameters using simple rules
            Kp = process_gain * gain_factor
            Ti = time_constant / gain_factor
            Td = dead_time * 0.25
            
            point = OperatingPoint(
                variables={"setpoint": sp},
                parameters={"Kp": Kp, "Ti": Ti, "Td": Td},
                weight=1.0,
                label=f"OP_{i+1}",
                active=True
            )
            points.append(point)
        
        return points
    
    def _build_interpolators(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build interpolation functions based on schedule type"""
        
        if self.config.schedule_type == GainScheduleType.LINEAR:
            return self._build_linear_interpolators(operating_points)
        elif self.config.schedule_type == GainScheduleType.POLYNOMIAL:
            return self._build_polynomial_interpolators(operating_points)
        elif self.config.schedule_type == GainScheduleType.LOOKUP_TABLE:
            return self._build_lookup_table(operating_points)
        elif self.config.schedule_type == GainScheduleType.FUZZY_LOGIC:
            return self._build_fuzzy_system(operating_points)
        elif self.config.schedule_type == GainScheduleType.SPLINE:
            return self._build_spline_interpolators(operating_points)
        else:
            raise ValueError(f"Unknown schedule type: {self.config.schedule_type}")
    
    def _build_linear_interpolators(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build linear interpolation functions"""
        
        # Extract scheduling variables and parameters
        scheduling_vars = []
        parameter_values = {param: [] for param in ['Kp', 'Ti', 'Td']}
        
        for point in operating_points:
            if not point.active:
                continue
            
            # Get scheduling variable values
            var_values = []
            for var_name in self.config.scheduling_variables:
                var_values.append(point.variables.get(var_name, 0.0))
            scheduling_vars.append(var_values)
            
            # Get parameter values
            for param in ['Kp', 'Ti', 'Td']:
                parameter_values[param].append(point.parameters.get(param, 0.0))
        
        scheduling_vars = np.array(scheduling_vars)
        
        # Create interpolators for each parameter
        interpolators = {}
        
        if len(self.config.scheduling_variables) == 1:
            # 1D interpolation
            x = scheduling_vars[:, 0]
            sort_idx = np.argsort(x)
            x_sorted = x[sort_idx]
            
            for param in ['Kp', 'Ti', 'Td']:
                y_sorted = np.array(parameter_values[param])[sort_idx]
                interpolators[param] = interpolate.interp1d(
                    x_sorted, y_sorted,
                    kind=self.config.interpolation_method,
                    fill_value='extrapolate' if self.config.extrapolation_mode == 'linear' else None,
                    bounds_error=False
                )
        else:
            # Multi-dimensional interpolation
            for param in ['Kp', 'Ti', 'Td']:
                y = np.array(parameter_values[param])
                interpolators[param] = interpolate.LinearNDInterpolator(
                    scheduling_vars, y,
                    fill_value=np.nan
                )
        
        self.interpolators = interpolators
        
        return {
            'type': 'linear',
            'interpolators': interpolators,
            'scheduling_variables': self.config.scheduling_variables,
            'operating_points_used': len([p for p in operating_points if p.active])
        }
    
    def _build_polynomial_interpolators(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build polynomial interpolation functions"""
        
        # Extract data
        scheduling_vars = []
        parameter_values = {param: [] for param in ['Kp', 'Ti', 'Td']}
        
        for point in operating_points:
            if not point.active:
                continue
                
            var_values = []
            for var_name in self.config.scheduling_variables:
                var_values.append(point.variables.get(var_name, 0.0))
            scheduling_vars.append(var_values)
            
            for param in ['Kp', 'Ti', 'Td']:
                parameter_values[param].append(point.parameters.get(param, 0.0))
        
        scheduling_vars = np.array(scheduling_vars)
        
        # Fit polynomial for each parameter
        interpolators = {}
        
        if len(self.config.scheduling_variables) == 1:
            # 1D polynomial fitting
            x = scheduling_vars[:, 0]
            
            for param in ['Kp', 'Ti', 'Td']:
                y = np.array(parameter_values[param])
                
                # Fit polynomial with regularization
                coeffs = np.polyfit(x, y, self.config.polynomial_order)
                interpolators[param] = np.poly1d(coeffs)
        else:
            # Multi-dimensional polynomial (using least squares)
            for param in ['Kp', 'Ti', 'Td']:
                y = np.array(parameter_values[param])
                
                # Create polynomial basis functions
                basis_matrix = self._create_polynomial_basis(scheduling_vars, self.config.polynomial_order)
                
                # Regularized least squares
                A = basis_matrix.T @ basis_matrix + self.config.regularization * np.eye(basis_matrix.shape[1])
                b = basis_matrix.T @ y
                coeffs = np.linalg.solve(A, b)
                
                # Create interpolation function
                def make_interpolator(coeffs, order):
                    def interpolator(x):
                        if np.isscalar(x):
                            x = np.array([x])
                        if x.ndim == 1:
                            x = x.reshape(1, -1)
                        basis = self._create_polynomial_basis(x, order)
                        return basis @ coeffs
                    return interpolator
                
                interpolators[param] = make_interpolator(coeffs, self.config.polynomial_order)
        
        self.interpolators = interpolators
        
        return {
            'type': 'polynomial',
            'interpolators': interpolators,
            'polynomial_order': self.config.polynomial_order,
            'regularization': self.config.regularization
        }
    
    def _build_lookup_table(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build lookup table with nearest neighbor interpolation"""
        
        # Store operating points for lookup
        active_points = [p for p in operating_points if p.active]
        
        def lookup_function(variables: Dict[str, float]) -> Dict[str, float]:
            """Lookup function using nearest neighbor"""
            
            # Convert query to vector
            query_vector = []
            for var_name in self.config.scheduling_variables:
                query_vector.append(variables.get(var_name, 0.0))
            query_vector = np.array(query_vector)
            
            # Find distances to all operating points
            distances = []
            for point in active_points:
                point_vector = []
                for var_name in self.config.scheduling_variables:
                    point_vector.append(point.variables.get(var_name, 0.0))
                point_vector = np.array(point_vector)
                
                distance = np.linalg.norm(query_vector - point_vector)
                distances.append(distance)
            
            distances = np.array(distances)
            
            # Find k nearest neighbors (k=3 for interpolation)
            k = min(3, len(active_points))
            nearest_indices = np.argsort(distances)[:k]
            
            if distances[nearest_indices[0]] < 1e-10:
                # Exact match
                nearest_point = active_points[nearest_indices[0]]
                return nearest_point.parameters.copy()
            
            # Weighted interpolation
            weights = 1.0 / (distances[nearest_indices] + 1e-10)
            weights = weights / np.sum(weights)
            
            # Interpolate parameters
            interpolated_params = {}
            for param in ['Kp', 'Ti', 'Td']:
                param_value = 0.0
                for i, idx in enumerate(nearest_indices):
                    param_value += weights[i] * active_points[idx].parameters.get(param, 0.0)
                interpolated_params[param] = param_value
            
            return interpolated_params
        
        self.interpolators = {'lookup_function': lookup_function}
        
        return {
            'type': 'lookup_table',
            'lookup_function': lookup_function,
            'operating_points': active_points,
            'interpolation_neighbors': 3
        }
    
    def _build_fuzzy_system(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build fuzzy logic gain scheduling system"""
        
        # Extract variable ranges
        var_ranges = {}
        for var_name in self.config.scheduling_variables:
            values = [p.variables.get(var_name, 0.0) for p in operating_points if p.active]
            var_ranges[var_name] = (min(values), max(values))
        
        # Create membership functions
        membership_functions = {}
        for var_name in self.config.scheduling_variables:
            var_min, var_max = var_ranges[var_name]
            membership_functions[var_name] = self._create_membership_functions(
                var_min, var_max, self.config.num_fuzzy_sets
            )
        
        # Create fuzzy rules from operating points
        fuzzy_rules = []
        for point in operating_points:
            if not point.active:
                continue
            
            # Create rule antecedent
            antecedent = {}
            for var_name in self.config.scheduling_variables:
                var_value = point.variables.get(var_name, 0.0)
                # Find best matching fuzzy set
                best_set = self._find_best_fuzzy_set(var_value, membership_functions[var_name])
                antecedent[var_name] = best_set
            
            # Rule consequent (PID parameters)
            consequent = point.parameters.copy()
            
            fuzzy_rules.append({
                'antecedent': antecedent,
                'consequent': consequent,
                'weight': point.weight
            })
        
        def fuzzy_inference(variables: Dict[str, float]) -> Dict[str, float]:
            """Fuzzy inference function"""
            
            # Calculate rule activations
            rule_activations = []
            for rule in fuzzy_rules:
                activation = 1.0
                for var_name, fuzzy_set in rule['antecedent'].items():
                    var_value = variables.get(var_name, 0.0)
                    membership = self._evaluate_membership(var_value, fuzzy_set)
                    activation *= membership
                
                activation *= rule['weight']
                rule_activations.append(activation)
            
            # Defuzzification using weighted average
            total_weight = sum(rule_activations) + 1e-10
            
            defuzzified_params = {}
            for param in ['Kp', 'Ti', 'Td']:
                weighted_sum = 0.0
                for i, rule in enumerate(fuzzy_rules):
                    weighted_sum += rule_activations[i] * rule['consequent'].get(param, 0.0)
                defuzzified_params[param] = weighted_sum / total_weight
            
            return defuzzified_params
        
        self.membership_functions = membership_functions
        self.fuzzy_rules = fuzzy_rules
        self.interpolators = {'fuzzy_inference': fuzzy_inference}
        
        return {
            'type': 'fuzzy_logic',
            'fuzzy_inference': fuzzy_inference,
            'membership_functions': membership_functions,
            'fuzzy_rules': fuzzy_rules,
            'num_rules': len(fuzzy_rules)
        }
    
    def _build_spline_interpolators(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Build spline interpolation functions"""
        
        # Extract data
        scheduling_vars = []
        parameter_values = {param: [] for param in ['Kp', 'Ti', 'Td']}
        
        for point in operating_points:
            if not point.active:
                continue
                
            var_values = []
            for var_name in self.config.scheduling_variables:
                var_values.append(point.variables.get(var_name, 0.0))
            scheduling_vars.append(var_values)
            
            for param in ['Kp', 'Ti', 'Td']:
                parameter_values[param].append(point.parameters.get(param, 0.0))
        
        scheduling_vars = np.array(scheduling_vars)
        
        # Create spline interpolators
        interpolators = {}
        
        if len(self.config.scheduling_variables) == 1:
            # 1D spline interpolation
            x = scheduling_vars[:, 0]
            sort_idx = np.argsort(x)
            x_sorted = x[sort_idx]
            
            for param in ['Kp', 'Ti', 'Td']:
                y_sorted = np.array(parameter_values[param])[sort_idx]
                
                # Use cubic spline with smoothing
                interpolators[param] = interpolate.UnivariateSpline(
                    x_sorted, y_sorted,
                    s=self.config.smoothing_factor,
                    k=min(3, len(x_sorted) - 1)  # Cubic or lower order
                )
        else:
            # Multi-dimensional spline (using RBF)
            for param in ['Kp', 'Ti', 'Td']:
                y = np.array(parameter_values[param])
                interpolators[param] = interpolate.RBFInterpolator(
                    scheduling_vars, y,
                    smoothing=self.config.smoothing_factor,
                    kernel='thin_plate_spline'
                )
        
        self.interpolators = interpolators
        
        return {
            'type': 'spline',
            'interpolators': interpolators,
            'smoothing_factor': self.config.smoothing_factor
        }
    
    def _create_polynomial_basis(self, x: np.ndarray, order: int) -> np.ndarray:
        """Create polynomial basis matrix for multi-dimensional data"""
        
        n_points, n_vars = x.shape
        
        # Create all polynomial combinations up to given order
        basis_functions = []
        
        # Include constant term
        basis_functions.append(np.ones(n_points))
        
        # Linear terms
        for i in range(n_vars):
            basis_functions.append(x[:, i])
        
        # Higher order terms
        if order >= 2:
            # Quadratic terms
            for i in range(n_vars):
                basis_functions.append(x[:, i]**2)
            
            # Cross terms
            for i in range(n_vars):
                for j in range(i+1, n_vars):
                    basis_functions.append(x[:, i] * x[:, j])
        
        if order >= 3:
            # Cubic terms
            for i in range(n_vars):
                basis_functions.append(x[:, i]**3)
        
        return np.column_stack(basis_functions)
    
    def _create_membership_functions(self, var_min: float, var_max: float, 
                                   num_sets: int) -> List[Dict[str, Any]]:
        """Create fuzzy membership functions"""
        
        # Create triangular membership functions
        centers = np.linspace(var_min, var_max, num_sets)
        width = (var_max - var_min) / (num_sets - 1) if num_sets > 1 else (var_max - var_min)
        
        membership_functions = []
        for i, center in enumerate(centers):
            mf = {
                'type': self.config.membership_functions,
                'center': center,
                'width': width,
                'left': center - width/2,
                'right': center + width/2,
                'label': f'MF_{i+1}'
            }
            membership_functions.append(mf)
        
        return membership_functions
    
    def _find_best_fuzzy_set(self, value: float, membership_functions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Find the fuzzy set with highest membership for a value"""
        
        best_membership = 0.0
        best_set = membership_functions[0]
        
        for mf in membership_functions:
            membership = self._evaluate_membership(value, mf)
            if membership > best_membership:
                best_membership = membership
                best_set = mf
        
        return best_set
    
    def _evaluate_membership(self, value: float, membership_function: Dict[str, Any]) -> float:
        """Evaluate membership function at given value"""
        
        if membership_function['type'] == 'triangular':
            center = membership_function['center']
            width = membership_function['width']
            
            if width == 0:
                return 1.0 if value == center else 0.0
            
            distance = abs(value - center)
            if distance >= width/2:
                return 0.0
            else:
                return 1.0 - 2*distance/width
        
        elif membership_function['type'] == 'gaussian':
            center = membership_function['center']
            sigma = membership_function['width'] / 4  # Approximate gaussian width
            return np.exp(-0.5 * ((value - center) / sigma)**2)
        
        else:
            # Default to triangular
            return self._evaluate_membership(value, {**membership_function, 'type': 'triangular'})
    
    def get_parameters(self, variables: Dict[str, float]) -> Dict[str, float]:
        """Get PID parameters for given operating conditions"""
        
        if not self.interpolators:
            raise ValueError("Interpolators not built. Call execute() first.")
        
        if self.config.schedule_type == GainScheduleType.LOOKUP_TABLE:
            return self.interpolators['lookup_function'](variables)
        
        elif self.config.schedule_type == GainScheduleType.FUZZY_LOGIC:
            return self.interpolators['fuzzy_inference'](variables)
        
        else:
            # Standard interpolation
            parameters = {}
            
            if len(self.config.scheduling_variables) == 1:
                var_value = variables.get(self.config.scheduling_variables[0], 0.0)
                for param in ['Kp', 'Ti', 'Td']:
                    if param in self.interpolators:
                        parameters[param] = float(self.interpolators[param](var_value))
            else:
                var_values = []
                for var_name in self.config.scheduling_variables:
                    var_values.append(variables.get(var_name, 0.0))
                var_array = np.array(var_values).reshape(1, -1)
                
                for param in ['Kp', 'Ti', 'Td']:
                    if param in self.interpolators:
                        result = self.interpolators[param](var_array)
                        parameters[param] = float(result[0] if hasattr(result, '__len__') else result)
        
        # Apply parameter bounds
        for param, value in parameters.items():
            if param in self.config.parameter_bounds:
                min_val, max_val = self.config.parameter_bounds[param]
                parameters[param] = np.clip(value, min_val, max_val)
        
        return parameters
    
    def _validate_interpolation(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Validate interpolation accuracy"""
        
        if not self.interpolators:
            return {"validation_error": float('inf'), "max_error": float('inf')}
        
        errors = []
        max_errors = {'Kp': 0.0, 'Ti': 0.0, 'Td': 0.0}
        
        for point in operating_points:
            if not point.active:
                continue
            
            # Get interpolated parameters
            interpolated = self.get_parameters(point.variables)
            
            # Calculate errors
            for param in ['Kp', 'Ti', 'Td']:
                actual = point.parameters.get(param, 0.0)
                predicted = interpolated.get(param, 0.0)
                error = abs(actual - predicted)
                errors.append(error)
                max_errors[param] = max(max_errors[param], error)
        
        return {
            "validation_error": float(np.mean(errors)) if errors else 0.0,
            "max_error": float(np.max(errors)) if errors else 0.0,
            "max_errors_by_parameter": max_errors,
            "validation_points": len([p for p in operating_points if p.active])
        }
    
    def _analyze_transitions(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Analyze parameter transitions between operating points"""
        
        if len(operating_points) < 2:
            return {"smooth_transitions": True, "max_parameter_change": 0.0}
        
        max_changes = {'Kp': 0.0, 'Ti': 0.0, 'Td': 0.0}
        
        # Check transitions between consecutive operating points
        active_points = [p for p in operating_points if p.active]
        
        for i in range(len(active_points) - 1):
            point1 = active_points[i]
            point2 = active_points[i + 1]
            
            for param in ['Kp', 'Ti', 'Td']:
                val1 = point1.parameters.get(param, 0.0)
                val2 = point2.parameters.get(param, 0.0)
                change = abs(val2 - val1) / (abs(val1) + 1e-6) * 100  # Percentage change
                max_changes[param] = max(max_changes[param], change)
        
        max_change = max(max_changes.values())
        smooth_transitions = max_change < 50.0  # Less than 50% change
        
        return {
            "smooth_transitions": smooth_transitions,
            "max_parameter_change": max_change,
            "max_changes_by_parameter": max_changes,
            "transition_time": self.config.transition_time
        }
    
    def _analyze_stability(self, operating_points: List[OperatingPoint]) -> Dict[str, Any]:
        """Analyze stability across operating range"""
        
        stable_points = 0
        total_points = 0
        
        for point in operating_points:
            if not point.active:
                continue
            
            total_points += 1
            
            # Simple stability check based on parameter ranges
            Kp = point.parameters.get('Kp', 0.0)
            Ti = point.parameters.get('Ti', 0.0)
            Td = point.parameters.get('Td', 0.0)
            
            # Basic stability criteria
            stable_kp = 0.1 <= Kp <= 10.0
            stable_ti = 0.1 <= Ti <= 100.0
            stable_td = 0.0 <= Td <= 10.0
            
            if stable_kp and stable_ti and stable_td:
                stable_points += 1
        
        stability_ratio = stable_points / max(total_points, 1)
        
        return {
            "globally_stable": stability_ratio >= 0.95,
            "stability_ratio": stability_ratio,
            "stable_points": stable_points,
            "total_points": total_points
        }
    
    def _calculate_performance_metrics(self, validation_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall performance metrics"""
        
        validation_error = validation_results.get('validation_error', 0.0)
        max_error = validation_results.get('max_error', 0.0)
        
        # Performance score (0-100)
        if max_error == 0:
            accuracy_score = 100.0
        else:
            accuracy_score = max(0, 100 - validation_error * 10)
        
        return {
            "accuracy_score": accuracy_score,
            "interpolation_error": validation_error,
            "max_interpolation_error": max_error,
            "scheduling_variables": len(self.config.scheduling_variables),
            "operating_points": len([p for p in self.config.operating_points if p.active])
        }


# Specialized gain schedulers
class LinearGainScheduler(GainScheduler):
    """Linear interpolation gain scheduler"""
    
    def __init__(self, configuration: Optional[GainScheduleConfiguration] = None):
        config = configuration or GainScheduleConfiguration()
        config.schedule_type = GainScheduleType.LINEAR
        super().__init__(config)


class PolynomialGainScheduler(GainScheduler):
    """Polynomial interpolation gain scheduler"""
    
    def __init__(self, configuration: Optional[GainScheduleConfiguration] = None):
        config = configuration or GainScheduleConfiguration()
        config.schedule_type = GainScheduleType.POLYNOMIAL
        super().__init__(config)


class LookupTableScheduler(GainScheduler):
    """Lookup table gain scheduler"""
    
    def __init__(self, configuration: Optional[GainScheduleConfiguration] = None):
        config = configuration or GainScheduleConfiguration()
        config.schedule_type = GainScheduleType.LOOKUP_TABLE
        super().__init__(config)


class FuzzyGainScheduler(GainScheduler):
    """Fuzzy logic gain scheduler"""
    
    def __init__(self, configuration: Optional[GainScheduleConfiguration] = None):
        config = configuration or GainScheduleConfiguration()
        config.schedule_type = GainScheduleType.FUZZY_LOGIC
        super().__init__(config)


# Register algorithms if registry is available
if ALGORITHM_REGISTRY_AVAILABLE:
    
    @registry.register(
        category=AlgorithmCategory.TUNING_CALCULATION,
        complexity=AlgorithmComplexity.MEDIUM,
        metadata=AlgorithmMetadata(
            name="Linear Gain Scheduling",
            description="Linear interpolation-based gain scheduling",
            version="1.0.0",
            author="PLC-GPT Team",
            tags=["gain_scheduling", "linear", "interpolation", "adaptive"]
        )
    )
    class RegisteredLinearGainScheduler(LinearGainScheduler):
        pass


# Export classes and functions
__all__ = [
    'GainScheduler',
    'LinearGainScheduler',
    'PolynomialGainScheduler',
    'LookupTableScheduler',
    'FuzzyGainScheduler',
    'GainScheduleConfiguration',
    'OperatingPoint',
    'GainScheduleResults',
    'GainScheduleType',
    'SchedulingVariable'
] 