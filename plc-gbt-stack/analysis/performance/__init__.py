#!/usr/bin/env python3
"""
Phase 22.3: Performance Analysis Suite Package
=============================================

Comprehensive loop performance assessment tools including:
- IAE, ISE, ITAE calculations
- Settling time and overshoot analysis
- Robustness metrics (GM, PM)
- Control effort quantification

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.3 - Performance Analysis Suite
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.3"

# Performance analysis configuration
PERFORMANCE_CONFIG = {
    "version": __version__,
    "supported_metrics": [
        "iae",          # Integral Absolute Error
        "ise",          # Integral Squared Error
        "itae",         # Integral Time Absolute Error
        "itse",         # Integral Time Squared Error
        "settling_time", # Time to reach steady state
        "overshoot",    # Maximum overshoot percentage
        "rise_time",    # Time to rise from 10% to 90%
        "control_effort", # Total control signal energy
        "gain_margin",  # Stability margin in dB
        "phase_margin", # Phase margin in degrees
        "robustness_index" # Combined robustness metric
    ],
    "default_settings": {
        "settling_criteria": 0.02,  # 2% settling band
        "overshoot_threshold": 0.05, # 5% overshoot warning
        "time_window": 3600,  # 1 hour analysis window
        "sampling_rate": 1.0,  # 1 Hz default
        "stability_margin": {
            "gain_margin_min": 6.0,  # dB
            "phase_margin_min": 60.0  # degrees
        }
    },
    "performance_targets": {
        "iae_max": 100.0,
        "ise_max": 500.0,
        "settling_time_max": 60.0,  # seconds
        "overshoot_max": 0.1,  # 10%
        "control_effort_max": 1000.0
    }
}

# Performance metric types
from enum import Enum


class PerformanceMetric(Enum):
    """Performance metric types"""
    IAE = "iae"
    ISE = "ise"
    ITAE = "itae"
    ITSE = "itse"
    SETTLING_TIME = "settling_time"
    OVERSHOOT = "overshoot"
    RISE_TIME = "rise_time"
    CONTROL_EFFORT = "control_effort"
    GAIN_MARGIN = "gain_margin"
    PHASE_MARGIN = "phase_margin"
    ROBUSTNESS_INDEX = "robustness_index"

class AnalysisType(Enum):
    """Analysis type categories"""
    TIME_DOMAIN = "time_domain"
    FREQUENCY_DOMAIN = "frequency_domain"
    STABILITY = "stability"
    ROBUSTNESS = "robustness"
    COMPARATIVE = "comparative"

class PerformanceGrade(Enum):
    """Performance assessment grades"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

# Import performance analysis modules
try:
    from .metrics import (
        ControlEffortAnalyzer,
        FrequencyDomainMetrics,
        PerformanceMetricsCalculator,
        RobustnessAnalyzer,
        TimeDomainMetrics,
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "performance_metrics": METRICS_AVAILABLE,
    "stability_analysis": False,  # Will be implemented
    "disturbance_analysis": False,  # Will be implemented
    "benchmarking_system": False   # Will be implemented
}

def get_available_metrics():
    """Get list of available performance metrics"""
    return [metric.value for metric in PerformanceMetric]

def get_metric_info(metric_type: str):
    """Get detailed information about a performance metric"""
    info = {
        "iae": {
            "name": "Integral Absolute Error",
            "description": "Sum of absolute error over time",
            "units": "engineering_units * time",
            "lower_is_better": True,
            "typical_range": "0-1000"
        },
        "ise": {
            "name": "Integral Squared Error",
            "description": "Sum of squared error over time",
            "units": "engineering_units² * time",
            "lower_is_better": True,
            "typical_range": "0-10000"
        },
        "itae": {
            "name": "Integral Time Absolute Error",
            "description": "Time-weighted absolute error integral",
            "units": "engineering_units * time²",
            "lower_is_better": True,
            "typical_range": "0-100000"
        },
        "settling_time": {
            "name": "Settling Time",
            "description": "Time to reach steady state within tolerance",
            "units": "seconds",
            "lower_is_better": True,
            "typical_range": "1-300"
        },
        "overshoot": {
            "name": "Maximum Overshoot",
            "description": "Maximum percentage overshoot of setpoint",
            "units": "percentage",
            "lower_is_better": True,
            "typical_range": "0-50"
        },
        "control_effort": {
            "name": "Control Effort",
            "description": "Total energy of control signal",
            "units": "control_units² * time",
            "lower_is_better": True,
            "typical_range": "0-10000"
        },
        "gain_margin": {
            "name": "Gain Margin",
            "description": "Stability margin in gain",
            "units": "dB",
            "higher_is_better": True,
            "typical_range": "3-20"
        },
        "phase_margin": {
            "name": "Phase Margin",
            "description": "Stability margin in phase",
            "units": "degrees",
            "higher_is_better": True,
            "typical_range": "30-90"
        }
    }
    return info.get(metric_type, {"description": "Unknown metric"})

def calculate_performance_grade(metrics: dict) -> PerformanceGrade:
    """Calculate overall performance grade based on metrics"""

    score = 0
    total_metrics = 0

    # Grade individual metrics
    if 'iae' in metrics:
        iae = metrics['iae']
        if iae < 10: score += 4
        elif iae < 50: score += 3
        elif iae < 100: score += 2
        elif iae < 200: score += 1
        total_metrics += 1

    if 'settling_time' in metrics:
        settling = metrics['settling_time']
        if settling < 10: score += 4
        elif settling < 30: score += 3
        elif settling < 60: score += 2
        elif settling < 120: score += 1
        total_metrics += 1

    if 'overshoot' in metrics:
        overshoot = metrics['overshoot'] * 100  # Convert to percentage
        if overshoot < 5: score += 4
        elif overshoot < 10: score += 3
        elif overshoot < 20: score += 2
        elif overshoot < 40: score += 1
        total_metrics += 1

    if 'gain_margin' in metrics:
        gm = metrics['gain_margin']
        if gm > 12: score += 4
        elif gm > 8: score += 3
        elif gm > 6: score += 2
        elif gm > 3: score += 1
        total_metrics += 1

    if 'phase_margin' in metrics:
        pm = metrics['phase_margin']
        if pm > 75: score += 4
        elif pm > 60: score += 3
        elif pm > 45: score += 2
        elif pm > 30: score += 1
        total_metrics += 1

    if total_metrics == 0:
        return PerformanceGrade.ACCEPTABLE

    average_score = score / total_metrics

    if average_score >= 3.5:
        return PerformanceGrade.EXCELLENT
    elif average_score >= 2.5:
        return PerformanceGrade.GOOD
    elif average_score >= 1.5:
        return PerformanceGrade.ACCEPTABLE
    elif average_score >= 0.5:
        return PerformanceGrade.POOR
    else:
        return PerformanceGrade.UNACCEPTABLE

def get_performance_recommendations(metrics: dict, grade: PerformanceGrade) -> list:
    """Generate performance improvement recommendations"""

    recommendations = []

    if grade in [PerformanceGrade.POOR, PerformanceGrade.UNACCEPTABLE]:
        recommendations.append("Consider complete PID retuning")

    if metrics.get('overshoot', 0) > 0.15:  # >15% overshoot
        recommendations.append("Reduce proportional gain to decrease overshoot")

    if metrics.get('settling_time', 0) > 120:  # >2 minutes
        recommendations.append("Increase integral gain to improve settling time")

    if metrics.get('iae', float('inf')) > 200:
        recommendations.append("Review process model and consider advanced tuning")

    if metrics.get('gain_margin', 0) < 6:
        recommendations.append("Increase gain margin for better stability")

    if metrics.get('phase_margin', 0) < 45:
        recommendations.append("Increase phase margin to improve robustness")

    if not recommendations:
        recommendations.append("Performance is satisfactory")

    return recommendations

# Export configuration for external use
__all__ = [
    # Configuration
    "PERFORMANCE_CONFIG",
    "AVAILABILITY_STATUS",

    # Enums
    "PerformanceMetric",
    "AnalysisType",
    "PerformanceGrade",

    # Utility functions
    "get_available_metrics",
    "get_metric_info",
    "calculate_performance_grade",
    "get_performance_recommendations",

    # Classes (if available)
]

# Add available classes to exports
if METRICS_AVAILABLE:
    __all__.extend([
        "PerformanceMetricsCalculator",
        "TimeDomainMetrics",
        "FrequencyDomainMetrics",
        "ControlEffortAnalyzer",
        "RobustnessAnalyzer"
    ])

# Package version and status information
def get_package_info():
    """Get comprehensive package information"""
    return {
        "version": __version__,
        "phase": __phase__,
        "author": __author__,
        "available_metrics": get_available_metrics(),
        "total_available": len([v for v in AVAILABILITY_STATUS.values() if v]),
        "total_modules": len(AVAILABILITY_STATUS),
        "completion_percentage": len([v for v in AVAILABILITY_STATUS.values() if v]) / len(AVAILABILITY_STATUS) * 100,
        "implementation_status": AVAILABILITY_STATUS
    }
