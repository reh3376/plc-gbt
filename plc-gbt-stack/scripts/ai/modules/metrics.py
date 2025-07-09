"""
Performance Metrics Module
==========================

Modular performance metric calculations and classification system.
Extracted from control loop analyzer for reuse across the entire codebase.

Features:
- Configurable metric types and calculations
- Performance range classification
- Weighted scoring system
- Extensible metric registration
- Statistical validation
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union
import logging

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Available performance metrics"""
    MSE = "mse"
    MAE = "mae" 
    RMSE = "rmse"
    MAPE = "mape"
    R_SQUARED = "r_squared"
    VARIANCE_EXPLAINED = "variance_explained"
    OSCILLATION_RATE = "oscillation_rate"
    SETTLING_TIME = "settling_time"
    ISE = "ise"  # Integral Squared Error
    IAE = "iae"  # Integral Absolute Error
    ITAE = "itae"  # Integral Time-weighted Absolute Error
    OVERSHOOT = "overshoot"
    RISE_TIME = "rise_time"
    STEADY_STATE_ERROR = "steady_state_error"
    CUSTOM = "custom"

@dataclass
class PerformanceRanges:
    """Performance classification ranges for a metric"""
    excellent_max: float
    good_max: float
    acceptable_max: float
    # anything above acceptable_max is considered "poor"
    
    def classify(self, value: float, higher_is_better: bool = False) -> str:
        """
        Classify a performance value
        
        Args:
            value: The metric value to classify
            higher_is_better: True if higher values indicate better performance
            
        Returns:
            Classification string: excellent, good, acceptable, poor
        """
        if higher_is_better:
            # For metrics where higher is better (R², variance explained)
            if value >= self.excellent_max:
                return "excellent"
            elif value >= self.good_max:
                return "good"
            elif value >= self.acceptable_max:
                return "acceptable"
            else:
                return "poor"
        else:
            # For metrics where lower is better (MAE, MSE, oscillation)
            if value <= self.excellent_max:
                return "excellent"
            elif value <= self.good_max:
                return "good"
            elif value <= self.acceptable_max:
                return "acceptable"
            else:
                return "poor"

@dataclass
class MetricConfiguration:
    """Configuration for a specific metric"""
    metric_type: MetricType
    ranges: PerformanceRanges
    weight: float = 1.0
    description: str = ""
    units: str = ""
    higher_is_better: bool = False  # True for metrics like R² where higher is better
    custom_calculator: Optional[Callable] = None  # For custom metrics

@dataclass
class MetricResult:
    """Result of a metric calculation"""
    metric_type: MetricType
    value: float
    classification: str
    weight: float
    description: str
    units: str
    higher_is_better: bool
    ranges: PerformanceRanges

class MetricCalculator:
    """
    Modular metric calculator with configurable metrics
    
    Supports both built-in and custom metrics with consistent interface.
    """
    
    def __init__(self):
        # Built-in metric calculators
        self.calculators = {
            MetricType.MSE: self._calculate_mse,
            MetricType.MAE: self._calculate_mae,
            MetricType.RMSE: self._calculate_rmse,
            MetricType.MAPE: self._calculate_mape,
            MetricType.R_SQUARED: self._calculate_r_squared,
            MetricType.VARIANCE_EXPLAINED: self._calculate_variance_explained,
            MetricType.OSCILLATION_RATE: self._calculate_oscillation_rate,
            MetricType.SETTLING_TIME: self._calculate_settling_time,
            MetricType.ISE: self._calculate_ise,
            MetricType.IAE: self._calculate_iae,
            MetricType.ITAE: self._calculate_itae,
            MetricType.OVERSHOOT: self._calculate_overshoot,
            MetricType.RISE_TIME: self._calculate_rise_time,
            MetricType.STEADY_STATE_ERROR: self._calculate_steady_state_error
        }
    
    def register_custom_metric(self, metric_type: MetricType, calculator: Callable):
        """Register a custom metric calculator"""
        self.calculators[metric_type] = calculator
        logger.info(f"Custom metric registered: {metric_type.value}")
    
    def calculate_metric(self, metric_config: MetricConfiguration, data: Dict[str, Any]) -> MetricResult:
        """
        Calculate a single metric based on configuration
        
        Args:
            metric_config: Configuration for the metric
            data: Input data containing arrays and parameters
            
        Returns:
            MetricResult with value and classification
        """
        try:
            # Get calculator function
            if metric_config.custom_calculator:
                calculator = metric_config.custom_calculator
            elif metric_config.metric_type in self.calculators:
                calculator = self.calculators[metric_config.metric_type]
            else:
                raise ValueError(f"No calculator found for {metric_config.metric_type.value}")
            
            # Calculate metric value
            value = calculator(data)
            
            # Classify performance
            classification = metric_config.ranges.classify(value, metric_config.higher_is_better)
            
            return MetricResult(
                metric_type=metric_config.metric_type,
                value=float(value),
                classification=classification,
                weight=metric_config.weight,
                description=metric_config.description,
                units=metric_config.units,
                higher_is_better=metric_config.higher_is_better,
                ranges=metric_config.ranges
            )
            
        except Exception as e:
            logger.error(f"Failed to calculate {metric_config.metric_type.value}: {e}")
            raise
    
    def calculate_multiple_metrics(self, metric_configs: List[MetricConfiguration], 
                                 data: Dict[str, Any]) -> Dict[str, MetricResult]:
        """Calculate multiple metrics from configurations"""
        results = {}
        
        for config in metric_configs:
            try:
                result = self.calculate_metric(config, data)
                results[config.metric_type.value] = result
                logger.debug(f"Calculated {config.metric_type.value}: {result.value:.4f} ({result.classification})")
            except Exception as e:
                logger.error(f"Failed to calculate {config.metric_type.value}: {e}")
                # Create error result
                results[config.metric_type.value] = MetricResult(
                    metric_type=config.metric_type,
                    value=float('nan'),
                    classification="error",
                    weight=config.weight,
                    description=f"Error: {str(e)}",
                    units=config.units,
                    higher_is_better=config.higher_is_better,
                    ranges=config.ranges
                )
        
        return results
    
    # Built-in metric calculators
    def _calculate_mse(self, data: Dict[str, Any]) -> float:
        """Calculate Mean Squared Error"""
        error_array = data["error_array"]
        return np.mean(error_array ** 2)
    
    def _calculate_mae(self, data: Dict[str, Any]) -> float:
        """Calculate Mean Absolute Error"""
        error_array = data["error_array"]
        return np.mean(np.abs(error_array))
    
    def _calculate_rmse(self, data: Dict[str, Any]) -> float:
        """Calculate Root Mean Squared Error"""
        error_array = data["error_array"]
        return np.sqrt(np.mean(error_array ** 2))
    
    def _calculate_mape(self, data: Dict[str, Any]) -> float:
        """Calculate Mean Absolute Percentage Error"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        
        # Avoid division by zero
        mask = sp_array != 0
        if np.sum(mask) == 0:
            return float('inf')
        
        return np.mean(np.abs((pv_array[mask] - sp_array[mask]) / sp_array[mask])) * 100
    
    def _calculate_r_squared(self, data: Dict[str, Any]) -> float:
        """Calculate R-squared (coefficient of determination)"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        
        ss_res = np.sum((pv_array - sp_array) ** 2)
        ss_tot = np.sum((pv_array - np.mean(pv_array)) ** 2)
        
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        
        return 1 - (ss_res / ss_tot)
    
    def _calculate_variance_explained(self, data: Dict[str, Any]) -> float:
        """Calculate variance explained by setpoint tracking"""
        error_array = data["error_array"]
        pv_array = data["pv_array"]
        
        error_variance = np.var(error_array)
        pv_variance = np.var(pv_array)
        
        if pv_variance == 0:
            return 1.0 if error_variance == 0 else 0.0
        
        return max(0, 1 - (error_variance / pv_variance))
    
    def _calculate_oscillation_rate(self, data: Dict[str, Any]) -> float:
        """Calculate oscillation rate (percentage of sign changes in error derivative)"""
        error_array = data["error_array"]
        
        if len(error_array) < 3:
            return 0.0
        
        # Calculate error derivative (difference)
        error_derivative = np.diff(error_array)
        
        # Count sign changes
        sign_changes = np.sum(np.diff(np.sign(error_derivative)) != 0)
        
        # Convert to percentage
        return (sign_changes / (len(error_derivative) - 1)) * 100
    
    def _calculate_settling_time(self, data: Dict[str, Any]) -> float:
        """Calculate settling time (simplified - time to reach within tolerance)"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        tolerance = data.get("settling_tolerance", 0.05)  # 5% default
        
        # Calculate percentage error
        with np.errstate(divide='ignore', invalid='ignore'):
            percent_error = np.abs((pv_array - sp_array) / sp_array) * 100
        
        # Handle division by zero
        percent_error = np.nan_to_num(percent_error, nan=0.0, posinf=100.0, neginf=100.0)
        
        # Find points within tolerance
        within_tolerance = percent_error <= (tolerance * 100)
        
        if np.sum(within_tolerance) == 0:
            return 100.0  # Never settled (100% of time)
        
        # Find first occurrence of settling (simplified)
        first_settled = np.argmax(within_tolerance)
        
        # Convert to percentage of total time
        return (first_settled / len(pv_array)) * 100
    
    def _calculate_ise(self, data: Dict[str, Any]) -> float:
        """Calculate Integral Squared Error"""
        error_array = data["error_array"]
        dt = data.get("sampling_time", 1.0)
        return np.sum(error_array ** 2) * dt
    
    def _calculate_iae(self, data: Dict[str, Any]) -> float:
        """Calculate Integral Absolute Error"""
        error_array = data["error_array"]
        dt = data.get("sampling_time", 1.0)
        return np.sum(np.abs(error_array)) * dt
    
    def _calculate_itae(self, data: Dict[str, Any]) -> float:
        """Calculate Integral Time-weighted Absolute Error"""
        error_array = data["error_array"]
        dt = data.get("sampling_time", 1.0)
        time_array = np.arange(len(error_array)) * dt
        return np.sum(time_array * np.abs(error_array)) * dt
    
    def _calculate_overshoot(self, data: Dict[str, Any]) -> float:
        """Calculate maximum overshoot percentage"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        
        # Find step changes in setpoint
        sp_changes = np.abs(np.diff(sp_array)) > np.std(sp_array) * 0.1
        
        if not np.any(sp_changes):
            return 0.0  # No significant setpoint changes
        
        # Find maximum overshoot after step changes
        max_overshoot = 0.0
        
        for i, change in enumerate(sp_changes):
            if change and i < len(pv_array) - 50:  # Need enough data after change
                sp_final = sp_array[i + 1]
                pv_response = pv_array[i + 1:i + 51]  # Next 50 points
                
                if sp_final != 0:
                    max_pv = np.max(pv_response)
                    overshoot = abs((max_pv - sp_final) / sp_final) * 100
                    max_overshoot = max(max_overshoot, overshoot)
        
        return max_overshoot
    
    def _calculate_rise_time(self, data: Dict[str, Any]) -> float:
        """Calculate rise time (10% to 90% of final value)"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        
        # Find step changes in setpoint
        sp_changes = np.abs(np.diff(sp_array)) > np.std(sp_array) * 0.1
        
        if not np.any(sp_changes):
            return 0.0  # No significant setpoint changes
        
        # Calculate rise time for first significant step
        step_index = np.argmax(sp_changes)
        if step_index >= len(pv_array) - 50:
            return 0.0
        
        sp_initial = sp_array[step_index]
        sp_final = sp_array[step_index + 1]
        pv_response = pv_array[step_index:step_index + 50]
        
        # Calculate 10% and 90% values
        value_10 = sp_initial + 0.1 * (sp_final - sp_initial)
        value_90 = sp_initial + 0.9 * (sp_final - sp_initial)
        
        # Find crossing points
        cross_10 = np.argmax(pv_response >= value_10) if np.any(pv_response >= value_10) else 0
        cross_90 = np.argmax(pv_response >= value_90) if np.any(pv_response >= value_90) else len(pv_response) - 1
        
        # Convert to percentage of response window
        rise_time = (cross_90 - cross_10) / len(pv_response) * 100
        return max(0, rise_time)
    
    def _calculate_steady_state_error(self, data: Dict[str, Any]) -> float:
        """Calculate steady state error"""
        pv_array = data["pv_array"]
        sp_array = data["sp_array"]
        
        # Use last 10% of data as steady state
        steady_start = int(len(pv_array) * 0.9)
        pv_steady = pv_array[steady_start:]
        sp_steady = sp_array[steady_start:]
        
        # Calculate average error in steady state
        steady_error = np.mean(pv_steady - sp_steady)
        
        # Convert to percentage if possible
        mean_sp = np.mean(sp_steady)
        if mean_sp != 0:
            return abs(steady_error / mean_sp) * 100
        else:
            return abs(steady_error)

class PerformanceClassifier:
    """
    Performance classification system with weighted scoring
    """
    
    def __init__(self):
        self.classification_scores = {
            "excellent": 100,
            "good": 75,
            "acceptable": 50,
            "poor": 25,
            "error": 0
        }
    
    def calculate_overall_score(self, metric_results: Dict[str, MetricResult]) -> Dict[str, Any]:
        """
        Calculate overall performance score from metric results
        
        Args:
            metric_results: Dictionary of metric results
            
        Returns:
            Dictionary with overall score and classification breakdown
        """
        if not metric_results:
            return {
                "overall_score": 0.0,
                "overall_classification": "error",
                "classification_distribution": {},
                "metric_count": 0,
                "weighted_contributions": {}
            }
        
        # Calculate weighted scores
        weighted_scores = []
        total_weight = 0
        classifications = {}
        contributions = {}
        
        for metric_name, result in metric_results.items():
            if result.classification != "error":
                score = self.classification_scores.get(result.classification, 0)
                weighted_score = score * result.weight
                weighted_scores.append(weighted_score)
                total_weight += result.weight
                
                # Count classifications
                classifications[result.classification] = classifications.get(result.classification, 0) + 1
                
                # Track individual contributions
                contributions[metric_name] = {
                    "score": score,
                    "weight": result.weight,
                    "weighted_score": weighted_score,
                    "classification": result.classification
                }
        
        # Calculate overall score
        overall_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0
        
        # Determine overall classification
        overall_classification = self._score_to_classification(overall_score)
        
        return {
            "overall_score": overall_score,
            "overall_classification": overall_classification,
            "classification_distribution": classifications,
            "metric_count": len(metric_results),
            "weighted_contributions": contributions,
            "total_weight": total_weight
        }
    
    def _score_to_classification(self, score: float) -> str:
        """Convert numeric score to classification"""
        if score >= 90:
            return "excellent"
        elif score >= 70:
            return "good"
        elif score >= 50:
            return "acceptable"
        else:
            return "poor"
    
    def generate_performance_summary(self, metric_results: Dict[str, MetricResult]) -> str:
        """Generate human-readable performance summary"""
        overall_info = self.calculate_overall_score(metric_results)
        
        summary = f"Overall Performance: {overall_info['overall_classification'].upper()} ({overall_info['overall_score']:.1f}%)\n"
        summary += f"Metrics Evaluated: {overall_info['metric_count']}\n\n"
        
        # Classification breakdown
        summary += "Performance Distribution:\n"
        for classification, count in overall_info['classification_distribution'].items():
            summary += f"  {classification.capitalize()}: {count} metrics\n"
        
        summary += "\nDetailed Metrics:\n"
        for metric_name, result in metric_results.items():
            if result.classification != "error":
                summary += f"  {metric_name.upper()}: {result.value:.4f} {result.units} ({result.classification})\n"
                summary += f"    {result.description}\n"
        
        return summary

# Predefined metric configurations for common use cases
def create_standard_control_metrics() -> List[MetricConfiguration]:
    """Create standard control loop metrics configuration"""
    return [
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(excellent_max=0.5, good_max=1.5, acceptable_max=3.0),
            weight=1.0,
            description="Mean Absolute Error - average magnitude of deviations",
            units="units"
        ),
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=5.0, acceptable_max=15.0),
            weight=1.2,
            description="Mean Squared Error - penalizes large deviations",
            units="(units)²"
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=1.5,
            description="Oscillation rate - percentage of oscillatory behavior",
            units="%"
        ),
        MetricConfiguration(
            metric_type=MetricType.SETTLING_TIME,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=1.0,
            description="Settling time - time to reach setpoint",
            units="% of process time"
        )
    ]

def create_process_quality_metrics() -> List[MetricConfiguration]:
    """Create process quality metrics configuration"""
    return [
        MetricConfiguration(
            metric_type=MetricType.VARIANCE_EXPLAINED,
            ranges=PerformanceRanges(excellent_max=0.95, good_max=0.85, acceptable_max=0.70),
            weight=2.0,
            description="Control system effectiveness",
            units="ratio",
            higher_is_better=True
        ),
        MetricConfiguration(
            metric_type=MetricType.R_SQUARED,
            ranges=PerformanceRanges(excellent_max=0.95, good_max=0.85, acceptable_max=0.70),
            weight=1.5,
            description="Statistical correlation metric",
            units="R²",
            higher_is_better=True
        ),
        MetricConfiguration(
            metric_type=MetricType.STEADY_STATE_ERROR,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=3.0, acceptable_max=5.0),
            weight=1.8,
            description="Steady state accuracy",
            units="% error"
        )
    ] 