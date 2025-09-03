#!/usr/bin/env python3
"""
Phase 22.3: Task 22.3.3 - Disturbance Analysis Package
======================================================

Comprehensive disturbance analysis tools including:
- Load disturbance rejection assessment
- Setpoint tracking performance
- Noise sensitivity analysis
- Feedforward effectiveness evaluation

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.3.3 - Disturbance Analysis
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.3.3"

# Disturbance analysis configuration
DISTURBANCE_CONFIG = {
    "version": __version__,
    "supported_analyses": [
        "load_disturbance_rejection",
        "setpoint_tracking",
        "noise_sensitivity",
        "feedforward_effectiveness",
        "disturbance_characterization",
        "rejection_performance",
        "tracking_bandwidth",
        "noise_attenuation"
    ],
    "default_settings": {
        "disturbance_types": ["step", "ramp", "sine", "random"],
        "frequency_range": {"min": 1e-4, "max": 1e2},
        "noise_analysis": {
            "measurement_noise_std": 0.01,
            "process_noise_std": 0.05,
            "frequency_bands": [
                {"name": "low", "range": [0, 0.01]},
                {"name": "medium", "range": [0.01, 0.1]},
                {"name": "high", "range": [0.1, 1.0]}
            ]
        },
        "performance_criteria": {
            "settling_time_max": 120.0,  # seconds
            "overshoot_max": 0.15,       # 15%
            "steady_state_error_max": 0.02,  # 2%
            "disturbance_rejection_min": 0.8  # 80% rejection
        }
    },
    "analysis_settings": {
        "time_horizon": 600.0,  # 10 minutes
        "simulation_points": 1000,
        "monte_carlo_runs": 100,
        "confidence_level": 0.95
    }
}

# Disturbance analysis types
from enum import Enum


class DisturbanceType(Enum):
    """Types of disturbances"""
    LOAD_DISTURBANCE = "load_disturbance"
    SETPOINT_CHANGE = "setpoint_change"
    MEASUREMENT_NOISE = "measurement_noise"
    PROCESS_NOISE = "process_noise"
    MODEL_UNCERTAINTY = "model_uncertainty"

class DisturbanceCharacteristic(Enum):
    """Disturbance signal characteristics"""
    STEP = "step"
    RAMP = "ramp"
    IMPULSE = "impulse"
    SINUSOIDAL = "sinusoidal"
    RANDOM = "random"
    COLORED_NOISE = "colored_noise"

class RejectionPerformance(Enum):
    """Disturbance rejection performance levels"""
    EXCELLENT = "excellent"      # >90% rejection
    GOOD = "good"               # 80-90% rejection
    ADEQUATE = "adequate"       # 60-80% rejection
    POOR = "poor"              # 40-60% rejection
    INADEQUATE = "inadequate"   # <40% rejection

class TrackingPerformance(Enum):
    """Setpoint tracking performance levels"""
    EXCELLENT = "excellent"      # Fast, minimal overshoot
    GOOD = "good"               # Good response
    ADEQUATE = "adequate"       # Acceptable response
    POOR = "poor"              # Slow or oscillatory
    INADEQUATE = "inadequate"   # Very poor tracking

# Import disturbance analysis modules
try:
    from .disturbance_characterizer import DisturbanceCharacterizer
    from .feedforward import FeedforwardAnalyzer
    from .load_rejection import LoadDisturbanceAnalyzer
    from .noise_sensitivity import NoiseSensitivityAnalyzer
    from .setpoint_tracking import SetpointTrackingAnalyzer
    DISTURBANCE_MODULES_AVAILABLE = True
except ImportError:
    DISTURBANCE_MODULES_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "load_disturbance_analysis": DISTURBANCE_MODULES_AVAILABLE,
    "setpoint_tracking_analysis": DISTURBANCE_MODULES_AVAILABLE,
    "noise_sensitivity_analysis": DISTURBANCE_MODULES_AVAILABLE,
    "feedforward_analysis": DISTURBANCE_MODULES_AVAILABLE,
    "disturbance_characterization": DISTURBANCE_MODULES_AVAILABLE
}

def get_available_analyses():
    """Get list of available disturbance analyses"""
    return list(DISTURBANCE_CONFIG["supported_analyses"])

def get_analysis_info(analysis_type: str):
    """Get detailed information about a disturbance analysis"""
    info = {
        "load_disturbance_rejection": {
            "name": "Load Disturbance Rejection Analysis",
            "description": "Assess controller's ability to reject load disturbances",
            "inputs": ["process_model", "controller_parameters", "disturbance_profile"],
            "outputs": ["rejection_ratio", "settling_time", "peak_deviation"],
            "best_for": ["Process control", "Regulatory control", "Unmeasured disturbances"]
        },
        "setpoint_tracking": {
            "name": "Setpoint Tracking Analysis",
            "description": "Evaluate controller's setpoint following performance",
            "inputs": ["setpoint_profile", "controller_parameters", "process_model"],
            "outputs": ["tracking_error", "response_time", "overshoot"],
            "best_for": ["Servo control", "Reference tracking", "Production changes"]
        },
        "noise_sensitivity": {
            "name": "Noise Sensitivity Analysis",
            "description": "Analyze controller sensitivity to measurement noise",
            "inputs": ["noise_characteristics", "controller_parameters"],
            "outputs": ["noise_amplification", "control_signal_variation", "filtering_effectiveness"],
            "best_for": ["Noisy measurements", "High-frequency disturbances", "Filter design"]
        },
        "feedforward_effectiveness": {
            "name": "Feedforward Control Effectiveness",
            "description": "Evaluate feedforward controller performance",
            "inputs": ["feedforward_model", "measured_disturbances", "process_model"],
            "outputs": ["disturbance_compensation", "improvement_ratio", "coordination_effectiveness"],
            "best_for": ["Measurable disturbances", "Predictive control", "Multi-loop systems"]
        },
        "disturbance_characterization": {
            "name": "Disturbance Characterization",
            "description": "Identify and characterize unknown disturbances",
            "inputs": ["time_series_data", "process_information"],
            "outputs": ["disturbance_type", "frequency_content", "magnitude_distribution"],
            "best_for": ["Unknown disturbances", "Root cause analysis", "Model improvement"]
        }
    }
    return info.get(analysis_type, {"description": "Unknown analysis type"})

def assess_rejection_performance(rejection_ratio: float, settling_time: float,
                               steady_state_error: float) -> RejectionPerformance:
    """Assess overall disturbance rejection performance"""

    score = 0

    # Rejection ratio contribution (50%)
    if rejection_ratio >= 0.9:
        score += 2.0
    elif rejection_ratio >= 0.8:
        score += 1.5
    elif rejection_ratio >= 0.6:
        score += 1.0
    elif rejection_ratio >= 0.4:
        score += 0.5

    # Settling time contribution (30%)
    max_settling = DISTURBANCE_CONFIG["default_settings"]["performance_criteria"]["settling_time_max"]
    if settling_time <= max_settling * 0.5:
        score += 1.2
    elif settling_time <= max_settling:
        score += 0.8
    elif settling_time <= max_settling * 1.5:
        score += 0.4

    # Steady state error contribution (20%)
    max_error = DISTURBANCE_CONFIG["default_settings"]["performance_criteria"]["steady_state_error_max"]
    if steady_state_error <= max_error * 0.5:
        score += 0.8
    elif steady_state_error <= max_error:
        score += 0.6
    elif steady_state_error <= max_error * 2:
        score += 0.3

    # Map score to performance level
    if score >= 3.5:
        return RejectionPerformance.EXCELLENT
    elif score >= 2.5:
        return RejectionPerformance.GOOD
    elif score >= 1.5:
        return RejectionPerformance.ADEQUATE
    elif score >= 0.8:
        return RejectionPerformance.POOR
    else:
        return RejectionPerformance.INADEQUATE

def assess_tracking_performance(tracking_error: float, response_time: float,
                              overshoot: float) -> TrackingPerformance:
    """Assess setpoint tracking performance"""

    score = 0

    # Tracking error contribution (40%)
    if tracking_error <= 0.02:  # 2% error
        score += 1.6
    elif tracking_error <= 0.05:  # 5% error
        score += 1.2
    elif tracking_error <= 0.1:   # 10% error
        score += 0.8
    elif tracking_error <= 0.2:   # 20% error
        score += 0.4

    # Response time contribution (40%)
    if response_time <= 30:  # 30 seconds
        score += 1.6
    elif response_time <= 60:  # 1 minute
        score += 1.2
    elif response_time <= 120:  # 2 minutes
        score += 0.8
    elif response_time <= 300:  # 5 minutes
        score += 0.4

    # Overshoot contribution (20%)
    max_overshoot = DISTURBANCE_CONFIG["default_settings"]["performance_criteria"]["overshoot_max"]
    if overshoot <= max_overshoot * 0.5:
        score += 0.8
    elif overshoot <= max_overshoot:
        score += 0.6
    elif overshoot <= max_overshoot * 2:
        score += 0.3

    # Map score to performance level
    if score >= 3.5:
        return TrackingPerformance.EXCELLENT
    elif score >= 2.5:
        return TrackingPerformance.GOOD
    elif score >= 1.5:
        return TrackingPerformance.ADEQUATE
    elif score >= 0.8:
        return TrackingPerformance.POOR
    else:
        return TrackingPerformance.INADEQUATE

def generate_disturbance_recommendations(rejection_performance: RejectionPerformance,
                                       tracking_performance: TrackingPerformance,
                                       analysis_results: dict) -> list:
    """Generate disturbance handling improvement recommendations"""

    recommendations = []

    # Rejection performance recommendations
    if rejection_performance == RejectionPerformance.INADEQUATE:
        recommendations.append("Disturbance rejection is inadequate - major controller redesign needed")
        recommendations.append("Consider feedforward control for measurable disturbances")

    elif rejection_performance == RejectionPerformance.POOR:
        recommendations.append("Poor disturbance rejection - increase integral gain")
        recommendations.append("Consider cascade control for improved rejection")

    elif rejection_performance == RejectionPerformance.ADEQUATE:
        recommendations.append("Adequate rejection - minor tuning improvements possible")

    # Tracking performance recommendations
    if tracking_performance == TrackingPerformance.INADEQUATE:
        recommendations.append("Setpoint tracking is inadequate - controller retuning required")

    elif tracking_performance == TrackingPerformance.POOR:
        recommendations.append("Poor tracking performance - increase proportional gain")
        recommendations.append("Consider derivative action for improved response")

    # Specific metric recommendations
    noise_sensitivity = analysis_results.get('noise_sensitivity', 0)
    if noise_sensitivity > 1.5:  # High noise amplification
        recommendations.append("High noise sensitivity - add measurement filtering")
        recommendations.append("Reduce derivative gain to minimize noise amplification")

    settling_time = analysis_results.get('settling_time', 0)
    if settling_time > 120:  # Slow settling
        recommendations.append("Slow disturbance recovery - increase integral gain")

    overshoot = analysis_results.get('overshoot', 0)
    if overshoot > 0.2:  # >20% overshoot
        recommendations.append("Excessive overshoot - reduce proportional gain")

    if not recommendations:
        recommendations.append("Disturbance handling performance is satisfactory")

    return recommendations

def calculate_disturbance_metrics(time_data: dict, disturbance_data: dict) -> dict:
    """Calculate comprehensive disturbance performance metrics"""

    import numpy as np

    metrics = {}

    # Basic time series data
    time = time_data.get('time', np.array([]))
    setpoint = time_data.get('setpoint', np.array([]))
    process_variable = time_data.get('process_variable', np.array([]))
    control_output = time_data.get('control_output', np.array([]))

    if len(time) > 0 and len(process_variable) > 0:

        # Error calculation
        error = setpoint - process_variable

        # Disturbance rejection metrics
        if 'disturbance_start' in disturbance_data:
            start_idx = disturbance_data['disturbance_start']
            end_idx = disturbance_data.get('disturbance_end', len(time))

            # Peak deviation during disturbance
            disturbance_error = error[start_idx:end_idx]
            metrics['peak_deviation'] = np.max(np.abs(disturbance_error))

            # Settling time after disturbance
            steady_state = np.mean(error[-50:]) if len(error) >= 50 else 0
            settling_band = 0.02 * np.abs(steady_state) if steady_state != 0 else 0.02

            # Find settling time
            for i in range(end_idx, len(error)):
                if np.abs(error[i] - steady_state) <= settling_band:
                    metrics['settling_time'] = time[i] - time[end_idx]
                    break
            else:
                metrics['settling_time'] = time[-1] - time[end_idx]

        # Overall performance metrics
        metrics['rms_error'] = np.sqrt(np.mean(error**2))
        metrics['max_error'] = np.max(np.abs(error))
        metrics['steady_state_error'] = np.mean(error[-50:]) if len(error) >= 50 else 0

        # Control effort metrics
        if len(control_output) > 0:
            metrics['control_variation'] = np.sum(np.abs(np.diff(control_output)))
            metrics['max_control_output'] = np.max(np.abs(control_output))

    return metrics

# Export configuration for external use
__all__ = [
    # Configuration
    "DISTURBANCE_CONFIG",
    "AVAILABILITY_STATUS",

    # Enums
    "DisturbanceType",
    "DisturbanceCharacteristic",
    "RejectionPerformance",
    "TrackingPerformance",

    # Utility functions
    "get_available_analyses",
    "get_analysis_info",
    "assess_rejection_performance",
    "assess_tracking_performance",
    "generate_disturbance_recommendations",
    "calculate_disturbance_metrics",

    # Classes (if available)
]

# Add available classes to exports
if DISTURBANCE_MODULES_AVAILABLE:
    __all__.extend([
        "LoadDisturbanceAnalyzer",
        "SetpointTrackingAnalyzer",
        "NoiseSensitivityAnalyzer",
        "FeedforwardAnalyzer",
        "DisturbanceCharacterizer"
    ])

# Package version and status information
def get_package_info():
    """Get comprehensive package information"""
    return {
        "version": __version__,
        "phase": __phase__,
        "author": __author__,
        "available_analyses": get_available_analyses(),
        "total_available": len([v for v in AVAILABILITY_STATUS.values() if v]),
        "total_modules": len(AVAILABILITY_STATUS),
        "completion_percentage": len([v for v in AVAILABILITY_STATUS.values() if v]) / len(AVAILABILITY_STATUS) * 100,
        "implementation_status": AVAILABILITY_STATUS
    }
