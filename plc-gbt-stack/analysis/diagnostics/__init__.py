#!/usr/bin/env python3
"""
Phase 22.4: Task 22.4.3 - Diagnostic System Package
===================================================

Comprehensive diagnostic system including:
- Valve stiction detection
- Oscillation diagnosis  
- Controller health monitoring
- Sensor fault detection

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.4.3 - Diagnostic System
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.4.3"

# Diagnostic system configuration
DIAGNOSTICS_CONFIG = {
    "version": __version__,
    "supported_diagnostics": [
        "valve_stiction",
        "oscillation_detection",
        "controller_health",
        "sensor_fault_detection",
        "actuator_health",
        "measurement_validation",
        "process_health",
        "communication_diagnostics"
    ],
    "valve_stiction": {
        "detection_methods": ["histogram", "ellipse", "correlation", "pattern_matching"],
        "thresholds": {
            "stiction_index_min": 0.3,
            "correlation_threshold": 0.7,
            "pattern_confidence_min": 0.8
        },
        "analysis_window": 300  # seconds
    },
    "oscillation_detection": {
        "methods": ["spectral_analysis", "autocorrelation", "harris_index", "pattern_detection"],
        "thresholds": {
            "harris_index_min": 0.15,
            "dominant_frequency_power": 0.6,
            "oscillation_confidence": 0.7
        },
        "frequency_range": [0.001, 0.5]  # Hz
    },
    "controller_health": {
        "metrics": ["tuning_quality", "performance_index", "saturation_frequency", "output_activity"],
        "thresholds": {
            "performance_degradation": 0.2,
            "saturation_limit": 0.1,
            "activity_threshold": 0.05
        },
        "assessment_period": 3600  # seconds
    },
    "sensor_fault": {
        "detection_types": ["bias", "drift", "noise", "frozen", "spike", "calibration"],
        "thresholds": {
            "bias_threshold": 2.0,  # standard deviations
            "drift_rate_max": 0.01,  # %/hour
            "noise_increase_factor": 3.0,
            "frozen_duration": 300  # seconds
        }
    },
    "analysis_settings": {
        "min_data_points": 100,
        "confidence_level": 0.95,
        "update_frequency": 60,  # seconds
        "historical_comparison": True
    }
}

# Diagnostic types and severity levels
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import logging

class DiagnosticType(Enum):
    """Types of diagnostic analysis"""
    VALVE_STICTION = "valve_stiction"
    OSCILLATION = "oscillation"
    CONTROLLER_HEALTH = "controller_health"
    SENSOR_FAULT = "sensor_fault"
    ACTUATOR_HEALTH = "actuator_health"
    PROCESS_HEALTH = "process_health"

class FaultSeverity(Enum):
    """Fault severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HealthStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    FAULTY = "faulty"
    UNKNOWN = "unknown"

class OscillationType(Enum):
    """Types of oscillations"""
    NONE = "none"
    SINUSOIDAL = "sinusoidal"
    SQUARE_WAVE = "square_wave"
    SAWTOOTH = "sawtooth"
    IRREGULAR = "irregular"
    LIMIT_CYCLE = "limit_cycle"

@dataclass
class DiagnosticConfiguration:
    """Configuration for diagnostic analysis"""
    diagnostic_id: str
    diagnostic_types: List[DiagnosticType]
    analysis_window: int = 300  # seconds
    update_frequency: int = 60   # seconds
    confidence_threshold: float = 0.7
    enable_trending: bool = True
    enable_alerts: bool = True

@dataclass
class ValveStictionResult:
    """Valve stiction diagnostic results"""
    stiction_detected: bool
    stiction_index: float
    confidence: float
    detection_method: str
    stick_slip_ratio: float
    dead_band_estimate: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class OscillationResult:
    """Oscillation diagnostic results"""
    oscillation_detected: bool
    oscillation_type: OscillationType
    dominant_frequency: float
    power_ratio: float
    harris_index: float
    amplitude: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ControllerHealthResult:
    """Controller health diagnostic results"""
    health_status: HealthStatus
    performance_index: float
    tuning_quality: float
    saturation_frequency: float
    activity_level: float
    degradation_factors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class SensorFaultResult:
    """Sensor fault diagnostic results"""
    fault_detected: bool
    fault_types: List[str]
    fault_severity: FaultSeverity
    bias_estimate: float
    drift_rate: float
    noise_level: float
    recommendations: List[str] = field(default_factory=list)

@dataclass
class ComprehensiveDiagnosticResult:
    """Comprehensive diagnostic analysis results"""
    diagnostic_id: str
    timestamp: datetime
    overall_health: HealthStatus
    valve_stiction: ValveStictionResult
    oscillation: OscillationResult
    controller_health: ControllerHealthResult
    sensor_fault: SensorFaultResult
    analysis_quality: float
    processing_time: float
    next_analysis: datetime

# Import diagnostic modules
try:
    from .valve_stiction import ValveStictionDetector
    from .oscillation_detector import OscillationDetector
    from .controller_health import ControllerHealthMonitor
    from .sensor_diagnostics import SensorFaultDetector
    from .diagnostic_engine import DiagnosticEngine
    DIAGNOSTIC_MODULES_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_MODULES_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "valve_stiction_detection": DIAGNOSTIC_MODULES_AVAILABLE,
    "oscillation_detection": DIAGNOSTIC_MODULES_AVAILABLE,
    "controller_health_monitoring": DIAGNOSTIC_MODULES_AVAILABLE,
    "sensor_fault_detection": DIAGNOSTIC_MODULES_AVAILABLE,
    "diagnostic_engine": DIAGNOSTIC_MODULES_AVAILABLE
}

def get_available_diagnostics():
    """Get list of available diagnostic analyses"""
    return DIAGNOSTICS_CONFIG["supported_diagnostics"]

def get_diagnostic_info(diagnostic_type: str):
    """Get detailed information about a diagnostic type"""
    info = {
        "valve_stiction": {
            "name": "Valve Stiction Detection",
            "description": "Detect valve stiction using multiple analysis methods",
            "methods": ["Histogram", "Ellipse fitting", "Correlation analysis", "Pattern matching"],
            "outputs": ["Stiction index", "Confidence", "Dead band estimate", "Recommendations"],
            "best_for": ["Control valves", "Pneumatic actuators", "Slow responding loops"]
        },
        "oscillation_detection": {
            "name": "Oscillation Detection and Analysis",
            "description": "Detect and characterize process oscillations",
            "methods": ["Spectral analysis", "Autocorrelation", "Harris index", "Pattern detection"],
            "outputs": ["Oscillation type", "Frequency", "Amplitude", "Power ratio"],
            "best_for": ["Control loop instability", "Tuning problems", "Interaction effects"]
        },
        "controller_health": {
            "name": "Controller Health Monitoring",
            "description": "Monitor PID controller performance and health",
            "metrics": ["Performance index", "Tuning quality", "Saturation frequency", "Activity level"],
            "outputs": ["Health status", "Degradation factors", "Tuning recommendations"],
            "best_for": ["Loop performance", "Tuning validation", "Maintenance planning"]
        },
        "sensor_fault_detection": {
            "name": "Sensor Fault Detection",
            "description": "Detect sensor faults and measurement problems",
            "fault_types": ["Bias", "Drift", "Noise", "Frozen", "Spike", "Calibration"],
            "outputs": ["Fault type", "Severity", "Estimates", "Recommendations"],
            "best_for": ["Measurement validation", "Sensor maintenance", "Process safety"]
        },
        "actuator_health": {
            "name": "Actuator Health Assessment",
            "description": "Monitor actuator performance and health",
            "parameters": ["Response time", "Linearity", "Hysteresis", "Wear"],
            "outputs": ["Health status", "Performance metrics", "Maintenance needs"],
            "best_for": ["Actuator maintenance", "Performance optimization", "Failure prevention"]
        }
    }
    return info.get(diagnostic_type, {"description": "Unknown diagnostic type"})

def assess_overall_health(diagnostic_results: List[Any]) -> HealthStatus:
    """Assess overall system health from individual diagnostic results"""
    
    health_scores = []
    
    for result in diagnostic_results:
        if hasattr(result, 'health_status'):
            status = result.health_status
        elif hasattr(result, 'fault_severity'):
            # Convert fault severity to health status
            severity = result.fault_severity
            if severity == FaultSeverity.NONE:
                status = HealthStatus.HEALTHY
            elif severity == FaultSeverity.LOW:
                status = HealthStatus.WARNING
            elif severity == FaultSeverity.MEDIUM:
                status = HealthStatus.DEGRADED
            else:
                status = HealthStatus.FAULTY
        else:
            # Generic assessment based on detection flags
            if hasattr(result, 'stiction_detected') and result.stiction_detected:
                status = HealthStatus.DEGRADED
            elif hasattr(result, 'oscillation_detected') and result.oscillation_detected:
                status = HealthStatus.WARNING
            elif hasattr(result, 'fault_detected') and result.fault_detected:
                status = HealthStatus.FAULTY
            else:
                status = HealthStatus.HEALTHY
        
        # Convert status to numeric score
        status_scores = {
            HealthStatus.HEALTHY: 1.0,
            HealthStatus.WARNING: 0.7,
            HealthStatus.DEGRADED: 0.4,
            HealthStatus.FAULTY: 0.1,
            HealthStatus.UNKNOWN: 0.5
        }
        health_scores.append(status_scores.get(status, 0.5))
    
    if not health_scores:
        return HealthStatus.UNKNOWN
    
    # Calculate overall health score
    overall_score = min(health_scores)  # Use worst case
    
    # Map back to health status
    if overall_score >= 0.9:
        return HealthStatus.HEALTHY
    elif overall_score >= 0.6:
        return HealthStatus.WARNING
    elif overall_score >= 0.3:
        return HealthStatus.DEGRADED
    else:
        return HealthStatus.FAULTY

def generate_diagnostic_recommendations(results: ComprehensiveDiagnosticResult) -> List[str]:
    """Generate comprehensive diagnostic recommendations"""
    
    recommendations = []
    
    # Valve stiction recommendations
    if results.valve_stiction.stiction_detected:
        recommendations.extend(results.valve_stiction.recommendations)
        if results.valve_stiction.stiction_index > 0.7:
            recommendations.append("CRITICAL: Valve stiction severely affecting control - immediate maintenance required")
        
    # Oscillation recommendations
    if results.oscillation.oscillation_detected:
        recommendations.extend(results.oscillation.recommendations)
        if results.oscillation.harris_index > 0.3:
            recommendations.append("Significant oscillation detected - review controller tuning")
    
    # Controller health recommendations
    if results.controller_health.health_status in [HealthStatus.DEGRADED, HealthStatus.FAULTY]:
        recommendations.extend(results.controller_health.recommendations)
        
    # Sensor fault recommendations
    if results.sensor_fault.fault_detected:
        recommendations.extend(results.sensor_fault.recommendations)
        if results.sensor_fault.fault_severity in [FaultSeverity.HIGH, FaultSeverity.CRITICAL]:
            recommendations.append("CRITICAL: Sensor fault affecting measurement quality - immediate attention required")
    
    # Overall system recommendations
    if results.overall_health == HealthStatus.FAULTY:
        recommendations.insert(0, "SYSTEM ALERT: Multiple faults detected - comprehensive system review recommended")
    elif results.overall_health == HealthStatus.DEGRADED:
        recommendations.insert(0, "PERFORMANCE DEGRADED: Proactive maintenance recommended to prevent failures")
    
    # Remove duplicates while preserving order
    unique_recommendations = []
    for rec in recommendations:
        if rec not in unique_recommendations:
            unique_recommendations.append(rec)
    
    if not unique_recommendations:
        unique_recommendations.append("System operating normally - continue routine monitoring")
    
    return unique_recommendations

def calculate_diagnostic_confidence(individual_confidences: List[float]) -> float:
    """Calculate overall diagnostic confidence"""
    
    if not individual_confidences:
        return 0.0
    
    # Use harmonic mean for conservative confidence estimate
    harmonic_mean = len(individual_confidences) / sum(1/c for c in individual_confidences if c > 0)
    return min(harmonic_mean, 1.0)

def prioritize_diagnostics(results: ComprehensiveDiagnosticResult) -> List[Tuple[str, str, float]]:
    """Prioritize diagnostic findings by severity and impact"""
    
    priorities = []
    
    # Valve stiction priority
    if results.valve_stiction.stiction_detected:
        severity = "HIGH" if results.valve_stiction.stiction_index > 0.7 else "MEDIUM"
        priority_score = results.valve_stiction.stiction_index * 100
        priorities.append(("Valve Stiction", severity, priority_score))
    
    # Oscillation priority
    if results.oscillation.oscillation_detected:
        severity = "HIGH" if results.oscillation.harris_index > 0.3 else "MEDIUM"
        priority_score = results.oscillation.harris_index * 100
        priorities.append(("Oscillation", severity, priority_score))
    
    # Controller health priority
    if results.controller_health.health_status in [HealthStatus.DEGRADED, HealthStatus.FAULTY]:
        severity = "HIGH" if results.controller_health.health_status == HealthStatus.FAULTY else "MEDIUM"
        priority_score = (1.0 - results.controller_health.performance_index) * 100
        priorities.append(("Controller Health", severity, priority_score))
    
    # Sensor fault priority
    if results.sensor_fault.fault_detected:
        severity_map = {
            FaultSeverity.CRITICAL: "CRITICAL",
            FaultSeverity.HIGH: "HIGH", 
            FaultSeverity.MEDIUM: "MEDIUM",
            FaultSeverity.LOW: "LOW"
        }
        severity = severity_map.get(results.sensor_fault.fault_severity, "MEDIUM")
        priority_score = len(results.sensor_fault.fault_types) * 25  # 25 points per fault type
        priorities.append(("Sensor Fault", severity, priority_score))
    
    # Sort by priority score (highest first)
    priorities.sort(key=lambda x: x[2], reverse=True)
    
    return priorities

def create_diagnostic_summary(results: ComprehensiveDiagnosticResult) -> Dict[str, Any]:
    """Create a comprehensive diagnostic summary"""
    
    priorities = prioritize_diagnostics(results)
    recommendations = generate_diagnostic_recommendations(results)
    
    # Calculate overall system score
    health_scores = {
        HealthStatus.HEALTHY: 100,
        HealthStatus.WARNING: 75,
        HealthStatus.DEGRADED: 50,
        HealthStatus.FAULTY: 25,
        HealthStatus.UNKNOWN: 0
    }
    
    individual_confidences = [
        results.valve_stiction.confidence,
        results.oscillation.power_ratio,  # Use power ratio as confidence proxy
        results.controller_health.performance_index,
        1.0 - (len(results.sensor_fault.fault_types) * 0.2)  # Decrease confidence with more faults
    ]
    
    overall_confidence = calculate_diagnostic_confidence(individual_confidences)
    
    summary = {
        "diagnostic_id": results.diagnostic_id,
        "timestamp": results.timestamp.isoformat(),
        "overall_health_status": results.overall_health.value,
        "overall_health_score": health_scores.get(results.overall_health, 0),
        "overall_confidence": overall_confidence,
        "analysis_quality": results.analysis_quality,
        "processing_time": results.processing_time,
        
        "priority_issues": [
            {
                "issue": priority[0],
                "severity": priority[1], 
                "score": priority[2]
            } for priority in priorities
        ],
        
        "detailed_findings": {
            "valve_stiction": {
                "detected": results.valve_stiction.stiction_detected,
                "index": results.valve_stiction.stiction_index,
                "confidence": results.valve_stiction.confidence
            },
            "oscillation": {
                "detected": results.oscillation.oscillation_detected,
                "type": results.oscillation.oscillation_type.value,
                "frequency": results.oscillation.dominant_frequency,
                "harris_index": results.oscillation.harris_index
            },
            "controller_health": {
                "status": results.controller_health.health_status.value,
                "performance_index": results.controller_health.performance_index,
                "tuning_quality": results.controller_health.tuning_quality
            },
            "sensor_fault": {
                "detected": results.sensor_fault.fault_detected,
                "types": results.sensor_fault.fault_types,
                "severity": results.sensor_fault.fault_severity.value
            }
        },
        
        "recommendations": recommendations,
        "next_analysis": results.next_analysis.isoformat(),
        
        "system_metrics": {
            "total_issues": len(priorities),
            "critical_issues": len([p for p in priorities if p[1] == "CRITICAL"]),
            "high_priority_issues": len([p for p in priorities if p[1] == "HIGH"]),
            "maintenance_urgency": "IMMEDIATE" if any(p[1] == "CRITICAL" for p in priorities) else 
                                  "HIGH" if any(p[1] == "HIGH" for p in priorities) else
                                  "MEDIUM" if priorities else "LOW"
        }
    }
    
    return summary

# Utility functions for diagnostic analysis
def detect_pattern_in_signal(signal: np.ndarray, pattern_type: str) -> Dict[str, Any]:
    """Generic pattern detection in signals"""
    
    if len(signal) < 10:
        return {"pattern_detected": False, "confidence": 0.0}
    
    try:
        if pattern_type == "stiction":
            # Look for characteristic stick-slip behavior
            derivative = np.diff(signal)
            zero_crossings = np.sum(np.diff(np.sign(derivative)) != 0)
            pattern_strength = zero_crossings / len(derivative)
            
            return {
                "pattern_detected": pattern_strength > 0.1,
                "confidence": min(pattern_strength * 5, 1.0),
                "characteristics": {
                    "zero_crossings": zero_crossings,
                    "pattern_strength": pattern_strength
                }
            }
            
        elif pattern_type == "oscillation":
            # Look for periodic behavior
            autocorr = np.correlate(signal, signal, mode='full')
            autocorr = autocorr[autocorr.size // 2:]
            
            # Find peaks in autocorrelation
            peaks = []
            for i in range(1, len(autocorr) - 1):
                if autocorr[i] > autocorr[i-1] and autocorr[i] > autocorr[i+1]:
                    peaks.append(i)
            
            if peaks:
                max_autocorr = max(autocorr[peaks]) / autocorr[0] if autocorr[0] != 0 else 0
                return {
                    "pattern_detected": max_autocorr > 0.3,
                    "confidence": max_autocorr,
                    "characteristics": {
                        "max_autocorr": max_autocorr,
                        "peak_locations": peaks[:5]  # First 5 peaks
                    }
                }
        
    except Exception:
        pass
    
    return {"pattern_detected": False, "confidence": 0.0}

def calculate_signal_quality(signal: np.ndarray) -> Dict[str, float]:
    """Calculate signal quality metrics"""
    
    if len(signal) < 2:
        return {"quality_score": 0.0, "snr": 0.0, "completeness": 0.0}
    
    # Signal-to-noise ratio estimation
    signal_power = np.var(signal)
    noise_estimate = np.var(np.diff(signal)) / 2  # High-frequency noise estimate
    snr = signal_power / noise_estimate if noise_estimate > 0 else float('inf')
    snr_db = 10 * np.log10(snr) if snr > 0 else 0
    
    # Data completeness
    nan_count = np.sum(np.isnan(signal))
    completeness = 1.0 - (nan_count / len(signal))
    
    # Overall quality score
    snr_score = min(snr_db / 20.0, 1.0)  # Normalize to 0-1 (20 dB = good)
    quality_score = (snr_score + completeness) / 2.0
    
    return {
        "quality_score": quality_score,
        "snr_db": snr_db,
        "completeness": completeness,
        "signal_power": signal_power,
        "noise_estimate": noise_estimate
    }

# Export configuration for external use
__all__ = [
    # Configuration
    "DIAGNOSTICS_CONFIG",
    "AVAILABILITY_STATUS",
    
    # Data classes
    "DiagnosticConfiguration",
    "ValveStictionResult",
    "OscillationResult", 
    "ControllerHealthResult",
    "SensorFaultResult",
    "ComprehensiveDiagnosticResult",
    
    # Enums
    "DiagnosticType",
    "FaultSeverity",
    "HealthStatus",
    "OscillationType",
    
    # Utility functions
    "get_available_diagnostics",
    "get_diagnostic_info",
    "assess_overall_health",
    "generate_diagnostic_recommendations",
    "calculate_diagnostic_confidence",
    "prioritize_diagnostics",
    "create_diagnostic_summary",
    "detect_pattern_in_signal",
    "calculate_signal_quality",
    
    # Classes (if available)
]

# Add available classes to exports
if DIAGNOSTIC_MODULES_AVAILABLE:
    __all__.extend([
        "ValveStictionDetector",
        "OscillationDetector",
        "ControllerHealthMonitor",
        "SensorFaultDetector",
        "DiagnosticEngine"
    ])

# Package version and status information
def get_package_info():
    """Get comprehensive package information"""
    return {
        "version": __version__,
        "phase": __phase__,
        "author": __author__,
        "available_diagnostics": get_available_diagnostics(),
        "total_available": len([v for v in AVAILABILITY_STATUS.values() if v]),
        "total_modules": len(AVAILABILITY_STATUS),
        "completion_percentage": len([v for v in AVAILABILITY_STATUS.values() if v]) / len(AVAILABILITY_STATUS) * 100,
        "implementation_status": AVAILABILITY_STATUS
    } 