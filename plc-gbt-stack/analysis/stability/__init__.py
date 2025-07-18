#!/usr/bin/env python3
"""
Phase 22.3: Task 22.3.2 - Stability Analysis Tools Package
=========================================================

Comprehensive stability analysis tools including:
- Nyquist and Bode plot generation
- Root locus analysis
- Sensitivity function evaluation
- Robust stability verification

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.3.2 - Stability Analysis
Methodology: AI Task Orchestrator Guide
"""

__version__ = "1.0.0"
__author__ = "PLC-GPT Development Team"
__phase__ = "22.3.2"

# Stability analysis configuration
STABILITY_CONFIG = {
    "version": __version__,
    "supported_analyses": [
        "nyquist_plot",
        "bode_plot", 
        "root_locus",
        "sensitivity_analysis",
        "complementary_sensitivity",
        "robust_stability",
        "gain_phase_margins",
        "stability_assessment"
    ],
    "default_settings": {
        "frequency_points": 1000,
        "frequency_range": {"min": 1e-3, "max": 1e3},
        "gain_range": {"min": 0.1, "max": 10.0},
        "stability_margins": {
            "gain_margin_min": 6.0,  # dB
            "phase_margin_min": 45.0,  # degrees
            "delay_margin_min": 0.5   # seconds
        },
        "robustness_analysis": {
            "uncertainty_bounds": 0.2,  # 20% uncertainty
            "monte_carlo_samples": 1000,
            "uncertainty_types": ["gain", "delay", "pole_zero"]
        }
    },
    "plot_settings": {
        "figure_size": (12, 8),
        "dpi": 300,
        "grid": True,
        "margins": True,
        "legend": True,
        "title_font_size": 14,
        "label_font_size": 12
    }
}

# Stability analysis types
from enum import Enum

class StabilityAnalysisType(Enum):
    """Stability analysis types"""
    NYQUIST = "nyquist"
    BODE = "bode"
    ROOT_LOCUS = "root_locus"
    SENSITIVITY = "sensitivity"
    ROBUST_STABILITY = "robust_stability"

class StabilityStatus(Enum):
    """Stability assessment results"""
    STABLE = "stable"
    MARGINALLY_STABLE = "marginally_stable"
    UNSTABLE = "unstable"
    CONDITIONALLY_STABLE = "conditionally_stable"
    UNKNOWN = "unknown"

class RobustnessLevel(Enum):
    """Robustness assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ADEQUATE = "adequate"
    POOR = "poor"
    INADEQUATE = "inadequate"

# Import stability analysis modules
try:
    from .nyquist import NyquistAnalyzer
    from .bode import BodeAnalyzer
    from .root_locus import RootLocusAnalyzer
    from .sensitivity import SensitivityAnalyzer
    from .robust_stability import RobustStabilityAnalyzer
    from .stability_assessor import StabilityAssessor
    STABILITY_MODULES_AVAILABLE = True
except ImportError:
    STABILITY_MODULES_AVAILABLE = False

# Module availability status
AVAILABILITY_STATUS = {
    "nyquist_analysis": STABILITY_MODULES_AVAILABLE,
    "bode_analysis": STABILITY_MODULES_AVAILABLE,
    "root_locus_analysis": STABILITY_MODULES_AVAILABLE,
    "sensitivity_analysis": STABILITY_MODULES_AVAILABLE,
    "robust_stability_analysis": STABILITY_MODULES_AVAILABLE,
    "stability_assessment": STABILITY_MODULES_AVAILABLE
}

def get_available_analyses():
    """Get list of available stability analyses"""
    return [analysis.value for analysis in StabilityAnalysisType]

def get_analysis_info(analysis_type: str):
    """Get detailed information about a stability analysis"""
    info = {
        "nyquist": {
            "name": "Nyquist Plot Analysis",
            "description": "Frequency domain stability analysis using Nyquist criterion",
            "outputs": ["plot", "encirclements", "stability_assessment"],
            "best_for": ["Closed-loop stability", "Gain/phase margins", "Conditional stability"]
        },
        "bode": {
            "name": "Bode Plot Analysis", 
            "description": "Magnitude and phase frequency response analysis",
            "outputs": ["magnitude_plot", "phase_plot", "margins", "crossover_frequencies"],
            "best_for": ["System identification", "Controller design", "Frequency response"]
        },
        "root_locus": {
            "name": "Root Locus Analysis",
            "description": "Pole movement analysis with varying gain",
            "outputs": ["root_locus_plot", "gain_ranges", "pole_locations"],
            "best_for": ["Gain selection", "Pole placement", "Transient response design"]
        },
        "sensitivity": {
            "name": "Sensitivity Analysis",
            "description": "Analysis of sensitivity and complementary sensitivity functions",
            "outputs": ["sensitivity_plot", "comp_sensitivity_plot", "peak_values"],
            "best_for": ["Disturbance rejection", "Noise sensitivity", "Robust performance"]
        },
        "robust_stability": {
            "name": "Robust Stability Analysis",
            "description": "Stability analysis under model uncertainty",
            "outputs": ["uncertainty_bounds", "stability_margins", "robustness_assessment"],
            "best_for": ["Model uncertainty", "Parameter variations", "Robust design"]
        }
    }
    return info.get(analysis_type, {"description": "Unknown analysis type"})

def assess_stability_margins(gain_margin: float, phase_margin: float, 
                           delay_margin: float = None) -> StabilityStatus:
    """Assess overall stability based on margins"""
    
    gm_min = STABILITY_CONFIG["default_settings"]["stability_margins"]["gain_margin_min"]
    pm_min = STABILITY_CONFIG["default_settings"]["stability_margins"]["phase_margin_min"]
    
    # Basic margin assessment
    gm_adequate = gain_margin >= gm_min
    pm_adequate = phase_margin >= pm_min
    
    if gm_adequate and pm_adequate:
        if gain_margin >= 10 and phase_margin >= 60:
            return StabilityStatus.STABLE
        else:
            return StabilityStatus.MARGINALLY_STABLE
    elif gain_margin > 0 and phase_margin > 0:
        return StabilityStatus.CONDITIONALLY_STABLE
    else:
        return StabilityStatus.UNSTABLE

def assess_robustness_level(robustness_metrics: dict) -> RobustnessLevel:
    """Assess robustness level from various metrics"""
    
    # Extract key metrics
    gain_margin = robustness_metrics.get('gain_margin', 0)
    phase_margin = robustness_metrics.get('phase_margin', 0)
    sensitivity_peak = robustness_metrics.get('sensitivity_peak', float('inf'))
    
    # Calculate robustness score
    score = 0
    
    # Gain margin contribution (30%)
    if gain_margin >= 12:
        score += 0.3
    elif gain_margin >= 8:
        score += 0.2
    elif gain_margin >= 6:
        score += 0.1
    
    # Phase margin contribution (40%)
    if phase_margin >= 70:
        score += 0.4
    elif phase_margin >= 60:
        score += 0.3
    elif phase_margin >= 45:
        score += 0.2
    elif phase_margin >= 30:
        score += 0.1
    
    # Sensitivity peak contribution (30%)
    if sensitivity_peak <= 1.5:
        score += 0.3
    elif sensitivity_peak <= 2.0:
        score += 0.2
    elif sensitivity_peak <= 3.0:
        score += 0.1
    
    # Map score to robustness level
    if score >= 0.8:
        return RobustnessLevel.EXCELLENT
    elif score >= 0.6:
        return RobustnessLevel.GOOD
    elif score >= 0.4:
        return RobustnessLevel.ADEQUATE
    elif score >= 0.2:
        return RobustnessLevel.POOR
    else:
        return RobustnessLevel.INADEQUATE

def generate_stability_recommendations(stability_status: StabilityStatus,
                                     robustness_level: RobustnessLevel,
                                     margins: dict) -> list:
    """Generate stability improvement recommendations"""
    
    recommendations = []
    
    if stability_status == StabilityStatus.UNSTABLE:
        recommendations.append("System is unstable - immediate controller redesign required")
        recommendations.append("Reduce controller gain to achieve stability")
        
    elif stability_status == StabilityStatus.CONDITIONALLY_STABLE:
        recommendations.append("System has conditional stability - careful gain adjustment needed")
        
    elif stability_status == StabilityStatus.MARGINALLY_STABLE:
        recommendations.append("Stability margins are minimal - consider increasing margins")
    
    # Specific margin recommendations
    gain_margin = margins.get('gain_margin', 0)
    phase_margin = margins.get('phase_margin', 0)
    
    if gain_margin < 6:
        recommendations.append(f"Gain margin ({gain_margin:.1f} dB) is below minimum (6 dB)")
        recommendations.append("Reduce proportional gain or add lead compensation")
        
    if phase_margin < 45:
        recommendations.append(f"Phase margin ({phase_margin:.1f}°) is below minimum (45°)")
        recommendations.append("Add phase lead compensation or reduce integral action")
    
    # Robustness recommendations
    if robustness_level in [RobustnessLevel.POOR, RobustnessLevel.INADEQUATE]:
        recommendations.append("Poor robustness - controller may be sensitive to model uncertainty")
        recommendations.append("Consider robust control design techniques")
    
    if not recommendations:
        recommendations.append("Stability and robustness are adequate")
    
    return recommendations

# Export configuration for external use
__all__ = [
    # Configuration
    "STABILITY_CONFIG",
    "AVAILABILITY_STATUS",
    
    # Enums
    "StabilityAnalysisType",
    "StabilityStatus",
    "RobustnessLevel",
    
    # Utility functions
    "get_available_analyses",
    "get_analysis_info",
    "assess_stability_margins",
    "assess_robustness_level",
    "generate_stability_recommendations",
    
    # Classes (if available)
]

# Add available classes to exports
if STABILITY_MODULES_AVAILABLE:
    __all__.extend([
        "NyquistAnalyzer",
        "BodeAnalyzer",
        "RootLocusAnalyzer",
        "SensitivityAnalyzer",
        "RobustStabilityAnalyzer",
        "StabilityAssessor"
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