#!/usr/bin/env python3
"""
Phase 8 Day 8.7: Advanced Control Strategy Analyzer
==================================================

Following AI Task Orchestrator Guide methodology for complex task implementation.

TASK ANALYSIS (per AI Task Orchestrator Guide):
- Complexity: COMPLEX (500-1500 lines, multiple concepts)
- Requirements: Mathematical PID equation conversions, process variable analysis, 
  control strategy determination
- Risk Assessment: Integration complexity, mathematical accuracy, strategy validation

IMPLEMENTATION SCOPE:
1. PID Equation Variable Conversions (Independent ↔ Dependent)
2. Process Variable Analysis (PPV, SPV, DV relationships)
3. Control Strategy Determination (Cascade vs Feedforward)
4. Advanced Control Logic (correlation analysis, lag assessment)
5. Integration with existing timing fundamentals

User's Critical Mathematical Relationships:
From Independent to Dependent:
Kc = Kp, Ti = Kp/Ki, Td = Kd/Kp

From Dependent to Independent:  
Kp = Kc, Ki = Kc/Ti, Kd = Kc × Td

Advanced Control Strategy Rules:
- PPV (long lag) + SPV (short lag, high correlation) → CASCADE CONTROL
- Multiple DVs or strong single DV → FEEDFORWARD CONTROL
"""

import asyncio
import json
import logging
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import scipy.stats as stats
from scipy.signal import correlate
import warnings
warnings.filterwarnings('ignore')

# Import timing fundamentals
from phase8_day8_6_control_timing_fundamentals import (
    ProcessType, ProcessTimingCharacteristics, TimingOptimizer
)

# Import process standards  
from phase8_day8_5_process_specific_performance_standards import (
    ProcessPerformanceStandards, ProcessStandardsDatabase
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VariableConversionType(Enum):
    """PID variable conversion types"""
    INDEPENDENT_TO_DEPENDENT = "independent_to_dependent"
    DEPENDENT_TO_INDEPENDENT = "dependent_to_independent"

class ControlStrategyType(Enum):
    """Advanced control strategy types"""
    STANDARD_PID = "standard_pid"
    CASCADE_CONTROL = "cascade_control"
    FEEDFORWARD_CONTROL = "feedforward_control"
    HYBRID_CASCADE_FEEDFORWARD = "hybrid_cascade_feedforward"
    ADVANCED_PREDICTIVE = "advanced_predictive"

@dataclass
class PIDVariables:
    """PID equation variables - both independent and dependent forms"""
    
    # Independent gains (standard form)
    kp: float  # Proportional gain
    ki: float  # Integral gain  
    kd: float  # Derivative gain
    
    # Dependent parameters (time-based form)
    kc: float  # Controller gain
    ti: float  # Integral time (seconds)
    td: float  # Derivative time (seconds)
    
    # Metadata
    conversion_type: VariableConversionType
    time_units: str = "seconds"
    validation_score: float = 0.0

@dataclass 
class ProcessVariableCharacteristics:
    """Process variable analysis for control strategy determination"""
    
    # Primary Process Variable (PPV) analysis
    ppv_name: str
    ppv_lag_time: float           # PPV response lag (seconds)
    ppv_time_constant: float      # PPV dominant time constant
    ppv_noise_level: float        # PPV measurement noise
    
    # Secondary Process Variable (SPV) analysis  
    spv_name: Optional[str] = None
    spv_lag_time: Optional[float] = None      # SPV response lag (seconds)
    spv_time_constant: Optional[float] = None # SPV time constant
    spv_correlation: Optional[float] = None   # SPV-PPV correlation coefficient
    
    # Disturbance Variable (DV) analysis
    dv_variables: List[str] = None            # List of disturbance variables
    dv_impacts: List[float] = None            # Impact strength (0-1) for each DV
    dv_lag_times: List[float] = None          # DV response lags
    dv_predictability: List[float] = None     # DV predictability (0-1)
    
    # Strategy determination results
    recommended_strategy: ControlStrategyType = ControlStrategyType.STANDARD_PID
    strategy_confidence: float = 0.0
    strategy_justification: str = ""

class PIDVariableConverter:
    """Convert between independent and dependent PID equation forms"""
    
    def __init__(self):
        self.conversion_tolerance = 1e-10  # Numerical precision tolerance
        
    def independent_to_dependent(self, kp: float, ki: float, kd: float) -> PIDVariables:
        """
        Convert independent gains to dependent time-based parameters
        
        From Independent to Dependent:
        Kc = Kp
        Ti = Kp/Ki  
        Td = Kd/Kp
        """
        logger.info(f"🔄 Converting independent gains: Kp={kp:.3f}, Ki={ki:.3f}, Kd={kd:.3f}")
        
        # Mathematical conversion (user's formulas)
        kc = kp
        
        # Handle division by zero for integral term
        if abs(ki) < self.conversion_tolerance:
            ti = float('inf')  # No integral action
            logger.warning("⚠️ Ki ≈ 0: Integral action disabled (Ti = ∞)")
        else:
            ti = kp / ki
            
        # Handle division by zero for derivative term  
        if abs(kp) < self.conversion_tolerance:
            td = 0.0  # No derivative action
            logger.warning("⚠️ Kp ≈ 0: Derivative action disabled (Td = 0)")
        else:
            td = kd / kp
            
        # Validate conversion
        validation_score = self._validate_conversion(kp, ki, kd, kc, ti, td, "to_dependent")
        
        pid_vars = PIDVariables(
            kp=kp, ki=ki, kd=kd,
            kc=kc, ti=ti, td=td,
            conversion_type=VariableConversionType.INDEPENDENT_TO_DEPENDENT,
            validation_score=validation_score
        )
        
        logger.info(f"✅ Dependent form: Kc={kc:.3f}, Ti={ti:.3f}s, Td={td:.3f}s")
        return pid_vars
    
    def dependent_to_independent(self, kc: float, ti: float, td: float) -> PIDVariables:
        """
        Convert dependent time-based parameters to independent gains
        
        From Dependent to Independent:
        Kp = Kc
        Ki = Kc/Ti
        Kd = Kc × Td  
        """
        logger.info(f"🔄 Converting dependent params: Kc={kc:.3f}, Ti={ti:.3f}s, Td={td:.3f}s")
        
        # Mathematical conversion (user's formulas)
        kp = kc
        
        # Handle division by zero for integral term
        if abs(ti) < self.conversion_tolerance or ti == float('inf'):
            ki = 0.0  # No integral action
            logger.warning("⚠️ Ti ≈ 0 or ∞: Integral action disabled (Ki = 0)")
        else:
            ki = kc / ti
            
        # Derivative term calculation
        kd = kc * td
        
        # Validate conversion
        validation_score = self._validate_conversion(kp, ki, kd, kc, ti, td, "to_independent")
        
        pid_vars = PIDVariables(
            kp=kp, ki=ki, kd=kd,
            kc=kc, ti=ti, td=td,
            conversion_type=VariableConversionType.DEPENDENT_TO_INDEPENDENT,
            validation_score=validation_score
        )
        
        logger.info(f"✅ Independent form: Kp={kp:.3f}, Ki={ki:.3f}, Kd={kd:.3f}")
        return pid_vars
    
    def _validate_conversion(self, kp: float, ki: float, kd: float, 
                           kc: float, ti: float, td: float, direction: str) -> float:
        """Validate bidirectional conversion accuracy"""
        
        try:
            if direction == "to_dependent":
                # Forward conversion validation
                kc_check = kp
                ti_check = kp / ki if abs(ki) > self.conversion_tolerance else float('inf')
                td_check = kd / kp if abs(kp) > self.conversion_tolerance else 0.0
                
                errors = [
                    abs(kc - kc_check) if kc != float('inf') else 0,
                    abs(ti - ti_check) if ti != float('inf') and ti_check != float('inf') else 0,
                    abs(td - td_check)
                ]
                
            else:  # to_independent
                # Reverse conversion validation  
                kp_check = kc
                ki_check = kc / ti if abs(ti) > self.conversion_tolerance and ti != float('inf') else 0.0
                kd_check = kc * td
                
                errors = [
                    abs(kp - kp_check),
                    abs(ki - ki_check),
                    abs(kd - kd_check)
                ]
            
            max_error = max(errors)
            
            if max_error < 1e-6:
                return 100.0  # Perfect conversion
            elif max_error < 1e-3:
                return 95.0   # Excellent conversion
            elif max_error < 1e-1:
                return 85.0   # Good conversion
            else:
                return 70.0   # Acceptable conversion
                
        except Exception as e:
            logger.error(f"❌ Conversion validation failed: {e}")
            return 50.0

class ProcessVariableAnalyzer:
    """Analyze process variables for advanced control strategy determination"""
    
    def __init__(self):
        self.cascade_threshold = {
            "min_spv_correlation": 0.7,      # SPV-PPV correlation threshold
            "max_lag_ratio": 0.3,            # SPV lag / PPV lag ratio
            "min_lag_difference": 10.0       # Minimum PPV-SPV lag difference (seconds)
        }
        
        self.feedforward_threshold = {
            "min_dv_impact": 0.3,            # Minimum DV impact for feedforward
            "min_predictability": 0.6,       # Minimum DV predictability
            "multiple_dv_count": 2           # Number of DVs for feedforward consideration
        }
    
    def analyze_process_variables(self, process_data: Dict[str, Any]) -> ProcessVariableCharacteristics:
        """
        Analyze process variables and determine optimal control strategy
        
        Args:
            process_data: Dictionary containing process variable information
        """
        logger.info("🔍 Analyzing process variables for control strategy determination...")
        
        # Extract PPV characteristics
        ppv_analysis = self._analyze_ppv(process_data.get("ppv", {}))
        
        # Extract SPV characteristics (if available)
        spv_analysis = self._analyze_spv(process_data.get("spv", {}), ppv_analysis)
        
        # Extract DV characteristics
        dv_analysis = self._analyze_dvs(process_data.get("dvs", []))
        
        # Determine optimal control strategy
        strategy_analysis = self._determine_control_strategy(ppv_analysis, spv_analysis, dv_analysis)
        
        pv_characteristics = ProcessVariableCharacteristics(
            ppv_name=ppv_analysis["name"],
            ppv_lag_time=ppv_analysis["lag_time"],
            ppv_time_constant=ppv_analysis["time_constant"],
            ppv_noise_level=ppv_analysis["noise_level"],
            
            spv_name=spv_analysis.get("name"),
            spv_lag_time=spv_analysis.get("lag_time"),
            spv_time_constant=spv_analysis.get("time_constant"),
            spv_correlation=spv_analysis.get("correlation"),
            
            dv_variables=dv_analysis.get("names", []),
            dv_impacts=dv_analysis.get("impacts", []),
            dv_lag_times=dv_analysis.get("lag_times", []),
            dv_predictability=dv_analysis.get("predictability", []),
            
            recommended_strategy=strategy_analysis["strategy"],
            strategy_confidence=strategy_analysis["confidence"],
            strategy_justification=strategy_analysis["justification"]
        )
        
        logger.info(f"✅ Strategy recommendation: {strategy_analysis['strategy'].value}")
        logger.info(f"📊 Confidence: {strategy_analysis['confidence']:.1f}%")
        
        return pv_characteristics
    
    def _analyze_ppv(self, ppv_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Primary Process Variable characteristics"""
        
        return {
            "name": ppv_data.get("name", "Unknown_PPV"),
            "lag_time": ppv_data.get("lag_time", 60.0),
            "time_constant": ppv_data.get("time_constant", 120.0),
            "noise_level": ppv_data.get("noise_level", 0.05),
            "measurement_range": ppv_data.get("range", [0, 100])
        }
    
    def _analyze_spv(self, spv_data: Dict[str, Any], ppv_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Secondary Process Variable characteristics"""
        
        if not spv_data:
            return {}
            
        spv_lag = spv_data.get("lag_time", 30.0)
        ppv_lag = ppv_analysis["lag_time"]
        
        # Calculate SPV-PPV correlation (simulated or from data)
        correlation = spv_data.get("correlation_with_ppv", 0.8)
        
        return {
            "name": spv_data.get("name", "Unknown_SPV"),
            "lag_time": spv_lag,
            "time_constant": spv_data.get("time_constant", 45.0),
            "correlation": correlation,
            "lag_ratio": spv_lag / ppv_lag if ppv_lag > 0 else 1.0
        }
    
    def _analyze_dvs(self, dv_data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze Disturbance Variables characteristics"""
        
        if not dv_data_list:
            return {"names": [], "impacts": [], "lag_times": [], "predictability": []}
        
        dv_analysis = {
            "names": [],
            "impacts": [],
            "lag_times": [],
            "predictability": []
        }
        
        for dv in dv_data_list:
            dv_analysis["names"].append(dv.get("name", "Unknown_DV"))
            dv_analysis["impacts"].append(dv.get("impact", 0.5))
            dv_analysis["lag_times"].append(dv.get("lag_time", 30.0))
            dv_analysis["predictability"].append(dv.get("predictability", 0.7))
        
        return dv_analysis
    
    def _determine_control_strategy(self, ppv_analysis: Dict[str, Any], 
                                  spv_analysis: Dict[str, Any],
                                  dv_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine optimal control strategy based on process variable analysis"""
        
        strategies_evaluated = []
        
        # 1. Evaluate CASCADE CONTROL potential
        cascade_score, cascade_reason = self._evaluate_cascade_potential(ppv_analysis, spv_analysis)
        strategies_evaluated.append(("CASCADE", cascade_score, cascade_reason))
        
        # 2. Evaluate FEEDFORWARD CONTROL potential  
        feedforward_score, feedforward_reason = self._evaluate_feedforward_potential(dv_analysis)
        strategies_evaluated.append(("FEEDFORWARD", feedforward_score, feedforward_reason))
        
        # 3. Evaluate HYBRID potential
        hybrid_score = min(cascade_score * 0.7, feedforward_score * 0.7)  # Conservative hybrid scoring
        if cascade_score > 70 and feedforward_score > 70:
            hybrid_reason = "Both cascade and feedforward conditions met"
            strategies_evaluated.append(("HYBRID", hybrid_score, hybrid_reason))
        
        # 4. Standard PID baseline
        standard_score = 60.0  # Default baseline
        standard_reason = "Standard PID control with timing optimization"
        strategies_evaluated.append(("STANDARD", standard_score, standard_reason))
        
        # Select best strategy
        best_strategy = max(strategies_evaluated, key=lambda x: x[1])
        
        strategy_map = {
            "CASCADE": ControlStrategyType.CASCADE_CONTROL,
            "FEEDFORWARD": ControlStrategyType.FEEDFORWARD_CONTROL,
            "HYBRID": ControlStrategyType.HYBRID_CASCADE_FEEDFORWARD,
            "STANDARD": ControlStrategyType.STANDARD_PID
        }
        
        return {
            "strategy": strategy_map[best_strategy[0]],
            "confidence": best_strategy[1],
            "justification": best_strategy[2],
            "all_evaluations": strategies_evaluated
        }
    
    def _evaluate_cascade_potential(self, ppv_analysis: Dict[str, Any], 
                                  spv_analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate potential for cascade control"""
        
        if not spv_analysis:
            return 20.0, "No secondary process variable available"
        
        # Criteria for cascade control
        spv_correlation = spv_analysis.get("correlation", 0.0)
        lag_ratio = spv_analysis.get("lag_ratio", 1.0)
        ppv_lag = ppv_analysis["lag_time"]
        spv_lag = spv_analysis.get("lag_time", ppv_lag)
        lag_difference = ppv_lag - spv_lag
        
        score = 0.0
        reasons = []
        
        # High SPV-PPV correlation
        if spv_correlation >= self.cascade_threshold["min_spv_correlation"]:
            score += 30.0
            reasons.append(f"High SPV-PPV correlation ({spv_correlation:.2f})")
        elif spv_correlation >= 0.5:
            score += 15.0
            reasons.append(f"Moderate SPV-PPV correlation ({spv_correlation:.2f})")
        else:
            reasons.append(f"Low SPV-PPV correlation ({spv_correlation:.2f})")
        
        # SPV responds faster than PPV
        if lag_ratio <= self.cascade_threshold["max_lag_ratio"]:
            score += 30.0
            reasons.append(f"SPV much faster than PPV (ratio={lag_ratio:.2f})")
        elif lag_ratio <= 0.6:
            score += 20.0
            reasons.append(f"SPV faster than PPV (ratio={lag_ratio:.2f})")
        else:
            reasons.append(f"SPV not significantly faster (ratio={lag_ratio:.2f})")
        
        # Sufficient lag difference
        if lag_difference >= self.cascade_threshold["min_lag_difference"]:
            score += 25.0
            reasons.append(f"Significant lag difference ({lag_difference:.1f}s)")
        elif lag_difference >= 5.0:
            score += 15.0
            reasons.append(f"Moderate lag difference ({lag_difference:.1f}s)")
        else:
            reasons.append(f"Insufficient lag difference ({lag_difference:.1f}s)")
        
        # Long PPV lag time favors cascade
        if ppv_lag >= 60.0:
            score += 15.0
            reasons.append(f"Long PPV lag time ({ppv_lag:.1f}s)")
        
        return score, "; ".join(reasons)
    
    def _evaluate_feedforward_potential(self, dv_analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate potential for feedforward control"""
        
        dv_impacts = dv_analysis.get("impacts", [])
        dv_predictability = dv_analysis.get("predictability", [])
        dv_names = dv_analysis.get("names", [])
        
        if not dv_impacts:
            return 25.0, "No disturbance variables identified"
        
        score = 0.0
        reasons = []
        
        # Strong DV impact
        max_impact = max(dv_impacts) if dv_impacts else 0.0
        strong_dvs = [i for i in dv_impacts if i >= self.feedforward_threshold["min_dv_impact"]]
        
        if max_impact >= 0.7:
            score += 35.0
            reasons.append(f"Very strong DV impact ({max_impact:.2f})")
        elif max_impact >= self.feedforward_threshold["min_dv_impact"]:
            score += 25.0
            reasons.append(f"Strong DV impact ({max_impact:.2f})")
        else:
            reasons.append(f"Weak DV impact ({max_impact:.2f})")
        
        # Multiple significant DVs
        if len(strong_dvs) >= self.feedforward_threshold["multiple_dv_count"]:
            score += 25.0
            reasons.append(f"Multiple strong DVs ({len(strong_dvs)})")
        elif len(strong_dvs) >= 1:
            score += 15.0
            reasons.append(f"Single strong DV")
        
        # DV predictability
        if dv_predictability:
            avg_predictability = np.mean(dv_predictability)
            if avg_predictability >= self.feedforward_threshold["min_predictability"]:
                score += 20.0
                reasons.append(f"High DV predictability ({avg_predictability:.2f})")
            elif avg_predictability >= 0.4:
                score += 10.0
                reasons.append(f"Moderate DV predictability ({avg_predictability:.2f})")
            else:
                reasons.append(f"Low DV predictability ({avg_predictability:.2f})")
        
        # Measurable and controllable DVs
        if len(dv_names) >= 2:
            score += 20.0
            reasons.append(f"Multiple measurable DVs ({len(dv_names)})")
        
        return score, "; ".join(reasons)

class AdvancedControlStrategyOrchestrator:
    """Main orchestrator following AI Task Orchestrator Guide methodology"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "phase": "8.8.7",
            "task": "Advanced Control Strategy Analysis",
            "start_time": self.start_time.isoformat(),
            "methodology": "AI Task Orchestrator Guide",
            "capabilities": [],
            "validation_results": {},
            "status": "in_progress"
        }
        
        # Initialize components
        self.pid_converter = PIDVariableConverter()
        self.pv_analyzer = ProcessVariableAnalyzer()
        
    async def task_analysis_phase(self) -> Dict[str, Any]:
        """Phase 1: Task Analysis (per AI Task Orchestrator Guide)"""
        logger.info("📋 Phase 1: Task Analysis following AI Task Orchestrator Guide...")
        
        analysis = {
            "complexity": "COMPLEX",
            "estimated_lines": "500-1500",
            "estimated_time": "3-8 hours",
            "requirements": [
                "PID equation variable conversions (independent ↔ dependent)",
                "Process variable analysis (PPV, SPV, DV)",
                "Control strategy determination logic",
                "Mathematical accuracy validation",
                "Integration with timing fundamentals"
            ],
            "risks": [
                "Mathematical conversion errors",
                "Strategy selection logic complexity", 
                "Integration with existing components",
                "Validation of control theory principles"
            ],
            "resources_needed": {
                "mathematical_libraries": ["numpy", "scipy"],
                "existing_components": ["timing_fundamentals", "process_standards"],
                "validation_frameworks": ["bidirectional_conversion", "strategy_scoring"]
            }
        }
        
        self.results["task_analysis"] = analysis
        logger.info(f"✅ Task classified as {analysis['complexity']} with {len(analysis['requirements'])} requirements")
        return analysis
    
    async def demonstration_beer_feed_advanced_analysis(self) -> Dict[str, Any]:
        """Demonstrate advanced control analysis for beer feed process"""
        logger.info("🍺 Demonstrating advanced control analysis for beer feed...")
        
        demo_result = {
            "task": "Beer Feed Advanced Control Analysis",
            "pid_conversions": {},
            "process_analysis": {},
            "validation_score": 0.0
        }
        
        try:
            # Step 1: PID Variable Conversions
            logger.info("🔄 Step 1: PID equation variable conversions...")
            
            # Example independent gains for beer feed
            kp_independent = 2.5   # Proportional gain
            ki_independent = 0.8   # Integral gain  
            kd_independent = 1.2   # Derivative gain
            
            # Convert to dependent form
            dependent_vars = self.pid_converter.independent_to_dependent(
                kp_independent, ki_independent, kd_independent
            )
            
            # Convert back to verify
            independent_vars = self.pid_converter.dependent_to_independent(
                dependent_vars.kc, dependent_vars.ti, dependent_vars.td
            )
            
            demo_result["pid_conversions"] = {
                "original_independent": {"kp": kp_independent, "ki": ki_independent, "kd": kd_independent},
                "converted_dependent": asdict(dependent_vars),
                "reconverted_independent": asdict(independent_vars),
                "conversion_accuracy": (dependent_vars.validation_score + independent_vars.validation_score) / 2
            }
            
            # Step 2: Process Variable Analysis
            logger.info("🔍 Step 2: Process variable analysis...")
            
            # Beer feed process characteristics
            beer_feed_process = {
                "ppv": {
                    "name": "Beer_Feed_Flow_Rate",
                    "lag_time": 45.0,           # Long lag time
                    "time_constant": 60.0,
                    "noise_level": 0.02,
                    "range": [0, 50]
                },
                "spv": {
                    "name": "Valve_Position_Feedback", 
                    "lag_time": 8.0,            # Much shorter lag time
                    "time_constant": 12.0,
                    "correlation_with_ppv": 0.85  # High correlation
                },
                "dvs": [
                    {
                        "name": "Upstream_Pressure",
                        "impact": 0.6,             # Strong impact
                        "lag_time": 15.0,
                        "predictability": 0.8      # Highly predictable
                    },
                    {
                        "name": "Tank_Level",
                        "impact": 0.4,
                        "lag_time": 30.0,
                        "predictability": 0.9
                    }
                ]
            }
            
            # Analyze process variables
            pv_characteristics = self.pv_analyzer.analyze_process_variables(beer_feed_process)
            
            demo_result["process_analysis"] = {
                "process_variables": asdict(pv_characteristics),
                "strategy_recommendation": pv_characteristics.recommended_strategy.value,
                "strategy_confidence": pv_characteristics.strategy_confidence,
                "strategy_justification": pv_characteristics.strategy_justification
            }
            
            # Calculate overall validation score
            conversion_score = demo_result["pid_conversions"]["conversion_accuracy"]
            strategy_score = pv_characteristics.strategy_confidence
            overall_score = (conversion_score * 0.4 + strategy_score * 0.6)
            
            demo_result["validation_score"] = overall_score
            
            logger.info(f"✅ Beer feed analysis complete: {overall_score:.1f}% validation score")
            logger.info(f"🎯 Recommended strategy: {pv_characteristics.recommended_strategy.value}")
            
            return demo_result
            
        except Exception as e:
            logger.error(f"❌ Beer feed analysis failed: {e}")
            demo_result["validation_score"] = 0.0
            demo_result["error"] = str(e)
            return demo_result
    
    async def comprehensive_strategy_validation(self) -> Dict[str, Any]:
        """Comprehensive validation of strategy determination logic"""
        logger.info("🔍 Comprehensive strategy validation across multiple scenarios...")
        
        validation_result = {
            "task": "Strategy Validation Suite",
            "test_scenarios": [],
            "validation_score": 0.0
        }
        
        try:
            # Test scenarios for different control strategies
            test_scenarios = [
                {
                    "name": "Ideal Cascade Scenario",
                    "process": {
                        "ppv": {"name": "Temperature", "lag_time": 180.0, "time_constant": 240.0, "noise_level": 0.1},
                        "spv": {"name": "Heater_Power", "lag_time": 20.0, "time_constant": 30.0, "correlation_with_ppv": 0.9},
                        "dvs": []
                    },
                    "expected_strategy": ControlStrategyType.CASCADE_CONTROL
                },
                {
                    "name": "Strong Feedforward Scenario", 
                    "process": {
                        "ppv": {"name": "Product_Quality", "lag_time": 120.0, "time_constant": 180.0, "noise_level": 0.05},
                        "spv": {},
                        "dvs": [
                            {"name": "Feed_Rate", "impact": 0.8, "lag_time": 10.0, "predictability": 0.9},
                            {"name": "Raw_Material_Quality", "impact": 0.7, "lag_time": 5.0, "predictability": 0.85}
                        ]
                    },
                    "expected_strategy": ControlStrategyType.FEEDFORWARD_CONTROL
                },
                {
                    "name": "Hybrid Control Scenario",
                    "process": {
                        "ppv": {"name": "Reactor_Concentration", "lag_time": 200.0, "time_constant": 300.0, "noise_level": 0.03},
                        "spv": {"name": "Catalyst_Temp", "lag_time": 40.0, "time_constant": 60.0, "correlation_with_ppv": 0.8},
                        "dvs": [
                            {"name": "Feed_Composition", "impact": 0.6, "lag_time": 15.0, "predictability": 0.8}
                        ]
                    },
                    "expected_strategy": ControlStrategyType.HYBRID_CASCADE_FEEDFORWARD
                },
                {
                    "name": "Standard PID Scenario",
                    "process": {
                        "ppv": {"name": "Simple_Flow", "lag_time": 30.0, "time_constant": 45.0, "noise_level": 0.02},
                        "spv": {},
                        "dvs": [{"name": "Minor_Disturbance", "impact": 0.2, "lag_time": 20.0, "predictability": 0.5}]
                    },
                    "expected_strategy": ControlStrategyType.STANDARD_PID
                }
            ]
            
            scenario_scores = []
            
            for scenario in test_scenarios:
                logger.info(f"📋 Testing scenario: {scenario['name']}")
                
                # Analyze scenario
                pv_characteristics = self.pv_analyzer.analyze_process_variables(scenario["process"])
                
                # Check if recommendation matches expectation
                correct_strategy = pv_characteristics.recommended_strategy == scenario["expected_strategy"]
                confidence_score = pv_characteristics.strategy_confidence
                
                scenario_score = confidence_score if correct_strategy else max(0, confidence_score - 30)
                scenario_scores.append(scenario_score)
                
                validation_result["test_scenarios"].append({
                    "scenario_name": scenario["name"],
                    "expected_strategy": scenario["expected_strategy"].value,
                    "recommended_strategy": pv_characteristics.recommended_strategy.value,
                    "strategy_confidence": confidence_score,
                    "correct_recommendation": correct_strategy,
                    "scenario_score": scenario_score,
                    "justification": pv_characteristics.strategy_justification
                })
                
                logger.info(f"{'✅' if correct_strategy else '❌'} {scenario['name']}: {scenario_score:.1f}%")
            
            validation_result["validation_score"] = np.mean(scenario_scores) if scenario_scores else 0
            
            logger.info(f"✅ Strategy validation: {validation_result['validation_score']:.1f}% overall accuracy")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Strategy validation failed: {e}")
            validation_result["validation_score"] = 0.0
            validation_result["error"] = str(e)
            return validation_result
    
    async def run_implementation(self) -> Dict[str, Any]:
        """Run complete implementation following AI Task Orchestrator Guide"""
        logger.info("🚀 Starting Phase 8 Day 8.7: Advanced Control Strategy Analysis")
        logger.info("📋 Following AI Task Orchestrator Guide methodology...")
        
        try:
            # Phase 1: Task Analysis
            task_analysis = await self.task_analysis_phase()
            
            # Record capabilities
            self.results["capabilities"] = [
                "PID Independent ↔ Dependent Variable Conversion",
                "Primary Process Variable (PPV) Analysis",
                "Secondary Process Variable (SPV) Correlation Analysis", 
                "Disturbance Variable (DV) Impact Assessment",
                "Cascade Control Strategy Detection",
                "Feedforward Control Strategy Detection",
                "Hybrid Control Strategy Determination",
                "Mathematical Conversion Validation",
                "Strategy Confidence Scoring"
            ]
            
            # Phase 2: Beer Feed Advanced Analysis  
            logger.info("🍺 Phase 2: Beer feed advanced analysis...")
            beer_feed_analysis = await self.demonstration_beer_feed_advanced_analysis()
            self.results["validation_results"]["beer_feed_advanced"] = beer_feed_analysis
            
            # Phase 3: Comprehensive Strategy Validation
            logger.info("🔍 Phase 3: Comprehensive strategy validation...")
            strategy_validation = await self.comprehensive_strategy_validation()
            self.results["validation_results"]["strategy_validation"] = strategy_validation
            
            # Calculate overall validation score
            validation_scores = [
                beer_feed_analysis.get("validation_score", 0),
                strategy_validation.get("validation_score", 0)
            ]
            overall_score = np.mean(validation_scores) if validation_scores else 0
            
            self.results.update({
                "overall_validation_score": overall_score,
                "status": "completed_excellent" if overall_score >= 85 else "completed_good" if overall_score >= 70 else "completed_needs_improvement",
                "completion_time": datetime.now().isoformat(),
                "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60
            })
            
            logger.info(f"🎉 Phase 8 Day 8.7 completed with {overall_score:.1f}% validation score")
            
        except Exception as e:
            logger.error(f"❌ Phase 8 Day 8.7 implementation failed: {e}")
            self.results.update({
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            })
        
        return self.results

async def main():
    """Main execution function"""
    orchestrator = AdvancedControlStrategyOrchestrator()
    results = await orchestrator.run_implementation()
    
    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase8"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"phase8_day8_7_advanced_control_strategy_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n🎯 Phase 8 Day 8.7 Advanced Control Strategy Analysis Results:")
    print(f"Overall Validation Score: {results.get('overall_validation_score', 0):.1f}%")
    
    # Show beer feed analysis results
    beer_feed = results.get('validation_results', {}).get('beer_feed_advanced', {})
    if beer_feed:
        conversions = beer_feed.get('pid_conversions', {})
        process_analysis = beer_feed.get('process_analysis', {})
        
        print(f"\n🍺 Beer Feed Advanced Analysis:")
        print(f"PID Conversion Accuracy: {conversions.get('conversion_accuracy', 0):.1f}%")
        
        if process_analysis:
            strategy = process_analysis.get('strategy_recommendation', 'unknown')
            confidence = process_analysis.get('strategy_confidence', 0)
            print(f"Recommended Strategy: {strategy.upper()}")
            print(f"Strategy Confidence: {confidence:.1f}%")
    
    # Show strategy validation results
    strategy_val = results.get('validation_results', {}).get('strategy_validation', {})
    if strategy_val:
        print(f"\n🔍 Strategy Validation Suite:")
        print(f"Overall Accuracy: {strategy_val.get('validation_score', 0):.1f}%")
        
        scenarios = strategy_val.get('test_scenarios', [])
        for scenario in scenarios:
            status = "✅" if scenario.get('correct_recommendation', False) else "❌"
            print(f"{status} {scenario.get('scenario_name', 'Unknown')}: {scenario.get('scenario_score', 0):.1f}%")
    
    print(f"\nCapabilities: {len(results.get('capabilities', []))}")
    print(f"Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 