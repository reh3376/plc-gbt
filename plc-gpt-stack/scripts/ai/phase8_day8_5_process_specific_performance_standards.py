#!/usr/bin/env python3
"""
Phase 8 Day 8.5: Process-Specific Performance Standards Orchestrator
===================================================================

Critical enhancement based on user feedback: Generic thresholds are inadequate!
Real industrial processes require specific, context-sensitive performance criteria.

Example: Beer feed control loop requires MAE < 0.25 gpm (not generic < 2.0)
What we called "stable" (MAE=1.525) is actually "very poorly tuned" for beer feed.

Implements:
1. Process-Specific Performance Definitions (MAE, oscillation, deadband per process type)
2. Industry Standard Control Performance Metrics (beer feed, temperature, pressure, etc.)
3. Enhanced AI Validation with Process-Aware Thresholds
4. Real-Time Performance Assessment with Correct Standards
5. Process Loop Classification and Standards Database

Foundation: User's critical insight about beer feed MAE < 0.25 gpm requirement
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

# Database connections for storing standards
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Import validated components for enhanced assessment
from phase8_day6_ai_enhanced_tuning_orchestrator import AITuningRecommendationEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProcessType(Enum):
    """Process control loop types with specific requirements"""
    BEER_FEED_FLOW = "beer_feed_flow"
    TEMPERATURE_CONTROL = "temperature_control"
    PRESSURE_CONTROL = "pressure_control"
    LEVEL_CONTROL = "level_control"
    pH_CONTROL = "ph_control"
    FLOW_CONTROL = "flow_control"
    COMPOSITION_CONTROL = "composition_control"
    DISTILLATION_CONTROL = "distillation_control"

@dataclass
class ProcessPerformanceStandards:
    """Process-specific performance standards"""
    process_type: ProcessType
    process_name: str
    
    # MAE (Mean Absolute Error) standards
    mae_excellent: float      # Best performance threshold
    mae_good: float          # Acceptable performance  
    mae_acceptable: float    # Minimum acceptable
    mae_poor: float         # Below this is poor
    mae_units: str          # Units for MAE (gpm, °F, psi, etc.)
    
    # Oscillation standards  
    oscillation_excellent: float    # % oscillation for excellent
    oscillation_good: float        # % oscillation for good
    oscillation_acceptable: float  # % oscillation acceptable
    oscillation_poor: float       # % oscillation poor
    
    # Deadband and response standards
    deadband_optimal: float        # Optimal deadband size
    deadband_units: str           # Deadband units
    response_time_target: float   # Target response time (seconds)
    settling_time_target: float   # Target settling time (seconds)
    
    # Control Variable standards
    cv_saturation_limit: float    # CV saturation % limit
    cv_utilization_optimal: float # Optimal CV utilization %
    
    # Process-specific parameters
    setpoint_range: Tuple[float, float]  # Normal setpoint range
    process_gain_typical: float         # Typical process gain
    time_constant_typical: float       # Typical time constant
    
    # Performance scoring weights
    mae_weight: float = 0.4           # Weight for MAE in overall score
    oscillation_weight: float = 0.3   # Weight for oscillation
    response_weight: float = 0.2      # Weight for response time
    cv_weight: float = 0.1            # Weight for CV utilization

class ProcessStandardsDatabase:
    """Database of process-specific performance standards"""
    
    def __init__(self):
        self.standards = {}
        self._initialize_industry_standards()
    
    def _initialize_industry_standards(self):
        """Initialize industry-standard performance criteria"""
        
        # Beer Feed Flow Control (User's specific requirement)
        self.standards[ProcessType.BEER_FEED_FLOW] = ProcessPerformanceStandards(
            process_type=ProcessType.BEER_FEED_FLOW,
            process_name="Beer Feed Flow Control",
            
            # User specified: MAE < 0.25 gpm for stable
            mae_excellent=0.15,      # Excellent: < 0.15 gpm
            mae_good=0.25,          # Good: < 0.25 gpm (user requirement)
            mae_acceptable=0.5,     # Acceptable: < 0.5 gpm  
            mae_poor=1.0,          # Poor: > 1.0 gpm
            mae_units="gpm",
            
            oscillation_excellent=1.0,    # < 1% oscillation excellent
            oscillation_good=2.0,        # < 2% oscillation good
            oscillation_acceptable=5.0,   # < 5% oscillation acceptable
            oscillation_poor=10.0,       # > 10% oscillation poor
            
            deadband_optimal=0.1,         # 0.1 gpm deadband
            deadband_units="gpm",
            response_time_target=30.0,    # 30 second response
            settling_time_target=90.0,    # 90 second settling
            
            cv_saturation_limit=5.0,      # < 5% CV saturation
            cv_utilization_optimal=60.0,  # 60% optimal CV usage
            
            setpoint_range=(5.0, 50.0),   # 5-50 gpm typical range
            process_gain_typical=2.5,     # Typical gain
            time_constant_typical=45.0,   # 45 second time constant
        )
        
        # Temperature Control (Brewing/Distillation)
        self.standards[ProcessType.TEMPERATURE_CONTROL] = ProcessPerformanceStandards(
            process_type=ProcessType.TEMPERATURE_CONTROL,
            process_name="Temperature Control",
            
            mae_excellent=0.5,      # < 0.5°F excellent
            mae_good=1.0,          # < 1.0°F good
            mae_acceptable=2.0,     # < 2.0°F acceptable
            mae_poor=5.0,          # > 5.0°F poor
            mae_units="°F",
            
            oscillation_excellent=0.5,    # < 0.5% excellent
            oscillation_good=1.0,        # < 1.0% good
            oscillation_acceptable=3.0,   # < 3.0% acceptable
            oscillation_poor=8.0,        # > 8.0% poor
            
            deadband_optimal=0.2,         # 0.2°F deadband
            deadband_units="°F",
            response_time_target=120.0,   # 2 minute response
            settling_time_target=300.0,   # 5 minute settling
            
            cv_saturation_limit=3.0,      # < 3% CV saturation
            cv_utilization_optimal=70.0,  # 70% optimal CV usage
            
            setpoint_range=(60.0, 220.0), # 60-220°F typical range
            process_gain_typical=1.5,     # Typical gain
            time_constant_typical=180.0,  # 3 minute time constant
        )
        
        # Pressure Control
        self.standards[ProcessType.PRESSURE_CONTROL] = ProcessPerformanceStandards(
            process_type=ProcessType.PRESSURE_CONTROL,
            process_name="Pressure Control",
            
            mae_excellent=0.1,      # < 0.1 psi excellent
            mae_good=0.25,         # < 0.25 psi good
            mae_acceptable=0.5,     # < 0.5 psi acceptable
            mae_poor=1.0,          # > 1.0 psi poor
            mae_units="psi",
            
            oscillation_excellent=0.5,    # < 0.5% excellent
            oscillation_good=1.5,        # < 1.5% good
            oscillation_acceptable=4.0,   # < 4.0% acceptable
            oscillation_poor=10.0,       # > 10.0% poor
            
            deadband_optimal=0.05,        # 0.05 psi deadband
            deadband_units="psi",
            response_time_target=15.0,    # 15 second response
            settling_time_target=45.0,    # 45 second settling
            
            cv_saturation_limit=2.0,      # < 2% CV saturation
            cv_utilization_optimal=65.0,  # 65% optimal CV usage
            
            setpoint_range=(0.0, 50.0),   # 0-50 psi typical range
            process_gain_typical=3.0,     # Typical gain
            time_constant_typical=25.0,   # 25 second time constant
        )
        
        # Level Control
        self.standards[ProcessType.LEVEL_CONTROL] = ProcessPerformanceStandards(
            process_type=ProcessType.LEVEL_CONTROL,
            process_name="Level Control",
            
            mae_excellent=0.5,      # < 0.5% level excellent
            mae_good=1.0,          # < 1.0% level good
            mae_acceptable=2.0,     # < 2.0% level acceptable
            mae_poor=5.0,          # > 5.0% level poor
            mae_units="% level",
            
            oscillation_excellent=1.0,    # < 1.0% excellent
            oscillation_good=2.0,        # < 2.0% good
            oscillation_acceptable=5.0,   # < 5.0% acceptable
            oscillation_poor=12.0,       # > 12.0% poor
            
            deadband_optimal=0.5,         # 0.5% level deadband
            deadband_units="% level",
            response_time_target=60.0,    # 1 minute response
            settling_time_target=180.0,   # 3 minute settling
            
            cv_saturation_limit=5.0,      # < 5% CV saturation
            cv_utilization_optimal=50.0,  # 50% optimal CV usage
            
            setpoint_range=(20.0, 80.0),  # 20-80% typical range
            process_gain_typical=1.0,     # Typical gain
            time_constant_typical=120.0,  # 2 minute time constant
        )
        
        # pH Control (for fermentation/brewing)
        self.standards[ProcessType.pH_CONTROL] = ProcessPerformanceStandards(
            process_type=ProcessType.pH_CONTROL,
            process_name="pH Control",
            
            mae_excellent=0.05,     # < 0.05 pH excellent
            mae_good=0.1,          # < 0.1 pH good
            mae_acceptable=0.2,     # < 0.2 pH acceptable
            mae_poor=0.5,          # > 0.5 pH poor
            mae_units="pH units",
            
            oscillation_excellent=0.5,    # < 0.5% excellent
            oscillation_good=1.0,        # < 1.0% good
            oscillation_acceptable=3.0,   # < 3.0% acceptable
            oscillation_poor=8.0,        # > 8.0% poor
            
            deadband_optimal=0.02,        # 0.02 pH deadband
            deadband_units="pH units",
            response_time_target=45.0,    # 45 second response
            settling_time_target=120.0,   # 2 minute settling
            
            cv_saturation_limit=3.0,      # < 3% CV saturation
            cv_utilization_optimal=60.0,  # 60% optimal CV usage
            
            setpoint_range=(3.0, 9.0),    # pH 3-9 typical range
            process_gain_typical=0.5,     # Typical gain
            time_constant_typical=60.0,   # 1 minute time constant
        )
    
    def get_standards(self, process_type: ProcessType) -> ProcessPerformanceStandards:
        """Get performance standards for process type"""
        return self.standards.get(process_type)
    
    def list_available_standards(self) -> List[ProcessType]:
        """List all available process standards"""
        return list(self.standards.keys())

class ProcessSpecificValidator:
    """Validates control performance using process-specific standards"""
    
    def __init__(self, standards_db: ProcessStandardsDatabase):
        self.standards_db = standards_db
        self.ai_engine = AITuningRecommendationEngine()
        
    async def assess_loop_performance(self, process_type: ProcessType, 
                                    loop_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess loop performance using process-specific standards"""
        
        standards = self.standards_db.get_standards(process_type)
        if not standards:
            raise ValueError(f"No standards defined for process type: {process_type}")
        
        logger.info(f"🎯 Assessing {standards.process_name} with specific standards...")
        
        assessment = {
            "process_type": process_type.value,
            "process_name": standards.process_name,
            "standards_applied": asdict(standards),
            "current_performance": {},
            "performance_rating": {},
            "improvement_needed": {},
            "validation_score": 0.0
        }
        
        try:
            # Extract current performance metrics
            current_mae = loop_data.get("mae", 0.0)
            current_oscillation = loop_data.get("oscillation_index", 0.0)
            current_response_time = loop_data.get("response_time", 0.0)
            current_cv_saturation = loop_data.get("cv_saturation", 0.0)
            
            assessment["current_performance"] = {
                "mae": current_mae,
                "mae_units": standards.mae_units,
                "oscillation_index": current_oscillation,
                "response_time": current_response_time,
                "cv_saturation": current_cv_saturation
            }
            
            # Assess MAE performance
            mae_rating = self._assess_mae_performance(current_mae, standards)
            assessment["performance_rating"]["mae"] = mae_rating
            
            # Assess oscillation performance
            oscillation_rating = self._assess_oscillation_performance(current_oscillation, standards)
            assessment["performance_rating"]["oscillation"] = oscillation_rating
            
            # Assess response time performance
            response_rating = self._assess_response_performance(current_response_time, standards)
            assessment["performance_rating"]["response_time"] = response_rating
            
            # Assess CV utilization
            cv_rating = self._assess_cv_performance(current_cv_saturation, standards)
            assessment["performance_rating"]["cv_utilization"] = cv_rating
            
            # Calculate weighted overall score
            overall_score = (
                mae_rating["score"] * standards.mae_weight +
                oscillation_rating["score"] * standards.oscillation_weight +
                response_rating["score"] * standards.response_weight +
                cv_rating["score"] * standards.cv_weight
            )
            
            assessment["validation_score"] = overall_score
            assessment["overall_rating"] = self._get_overall_rating(overall_score)
            
            # Generate improvement recommendations
            assessment["improvement_needed"] = self._generate_improvement_recommendations(
                assessment["performance_rating"], standards
            )
            
            logger.info(f"✅ {standards.process_name} assessment: {overall_score:.1f}% ({assessment['overall_rating']})")
            return assessment
            
        except Exception as e:
            logger.error(f"❌ Performance assessment failed: {e}")
            assessment["validation_score"] = 0.0
            assessment["error"] = str(e)
            return assessment
    
    def _assess_mae_performance(self, current_mae: float, standards: ProcessPerformanceStandards) -> Dict[str, Any]:
        """Assess MAE performance against standards"""
        
        if current_mae <= standards.mae_excellent:
            rating = "excellent"
            score = 100.0
        elif current_mae <= standards.mae_good:
            rating = "good"
            score = 85.0
        elif current_mae <= standards.mae_acceptable:
            rating = "acceptable"
            score = 70.0
        elif current_mae <= standards.mae_poor:
            rating = "poor"
            score = 40.0
        else:
            rating = "very_poor"
            score = 20.0
        
        return {
            "rating": rating,
            "score": score,
            "current_value": current_mae,
            "target_excellent": standards.mae_excellent,
            "target_good": standards.mae_good,
            "units": standards.mae_units,
            "improvement_needed": max(0, current_mae - standards.mae_good)
        }
    
    def _assess_oscillation_performance(self, current_oscillation: float, standards: ProcessPerformanceStandards) -> Dict[str, Any]:
        """Assess oscillation performance against standards"""
        
        if current_oscillation <= standards.oscillation_excellent:
            rating = "excellent"
            score = 100.0
        elif current_oscillation <= standards.oscillation_good:
            rating = "good"
            score = 85.0
        elif current_oscillation <= standards.oscillation_acceptable:
            rating = "acceptable"
            score = 70.0
        elif current_oscillation <= standards.oscillation_poor:
            rating = "poor"
            score = 40.0
        else:
            rating = "very_poor"
            score = 20.0
        
        return {
            "rating": rating,
            "score": score,
            "current_value": current_oscillation,
            "target_excellent": standards.oscillation_excellent,
            "target_good": standards.oscillation_good,
            "units": "%",
            "improvement_needed": max(0, current_oscillation - standards.oscillation_good)
        }
    
    def _assess_response_performance(self, current_response: float, standards: ProcessPerformanceStandards) -> Dict[str, Any]:
        """Assess response time performance against standards"""
        
        target = standards.response_time_target
        if current_response <= target:
            rating = "excellent"
            score = 100.0
        elif current_response <= target * 1.5:
            rating = "good"
            score = 85.0
        elif current_response <= target * 2.0:
            rating = "acceptable"
            score = 70.0
        elif current_response <= target * 3.0:
            rating = "poor"
            score = 40.0
        else:
            rating = "very_poor"
            score = 20.0
        
        return {
            "rating": rating,
            "score": score,
            "current_value": current_response,
            "target": target,
            "units": "seconds",
            "improvement_needed": max(0, current_response - target)
        }
    
    def _assess_cv_performance(self, current_saturation: float, standards: ProcessPerformanceStandards) -> Dict[str, Any]:
        """Assess CV utilization performance against standards"""
        
        if current_saturation <= standards.cv_saturation_limit:
            rating = "excellent"
            score = 100.0
        elif current_saturation <= standards.cv_saturation_limit * 2:
            rating = "good"
            score = 85.0
        elif current_saturation <= standards.cv_saturation_limit * 3:
            rating = "acceptable"
            score = 70.0
        elif current_saturation <= standards.cv_saturation_limit * 5:
            rating = "poor"
            score = 40.0
        else:
            rating = "very_poor"
            score = 20.0
        
        return {
            "rating": rating,
            "score": score,
            "current_value": current_saturation,
            "target_limit": standards.cv_saturation_limit,
            "units": "%",
            "improvement_needed": max(0, current_saturation - standards.cv_saturation_limit)
        }
    
    def _get_overall_rating(self, score: float) -> str:
        """Get overall performance rating"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "acceptable"
        elif score >= 50:
            return "poor"
        else:
            return "very_poor"
    
    def _generate_improvement_recommendations(self, performance_rating: Dict[str, Any], 
                                            standards: ProcessPerformanceStandards) -> Dict[str, Any]:
        """Generate specific improvement recommendations"""
        
        recommendations = {
            "priority_actions": [],
            "tuning_adjustments": {},
            "expected_improvements": {}
        }
        
        # MAE improvement recommendations
        mae_rating = performance_rating.get("mae", {})
        if mae_rating.get("rating") in ["poor", "very_poor"]:
            recommendations["priority_actions"].append({
                "action": "Reduce MAE",
                "current": f"{mae_rating.get('current_value', 0):.3f} {mae_rating.get('units', '')}",
                "target": f"{mae_rating.get('target_good', 0):.3f} {mae_rating.get('units', '')}",
                "improvement_needed": f"{mae_rating.get('improvement_needed', 0):.3f} {mae_rating.get('units', '')}",
                "priority": "high"
            })
            
            recommendations["tuning_adjustments"]["kc"] = "increase_proportional_gain"
            recommendations["tuning_adjustments"]["ti"] = "decrease_integral_time"
        
        # Oscillation improvement recommendations  
        oscillation_rating = performance_rating.get("oscillation", {})
        if oscillation_rating.get("rating") in ["poor", "very_poor"]:
            recommendations["priority_actions"].append({
                "action": "Reduce Oscillation",
                "current": f"{oscillation_rating.get('current_value', 0):.1f}%",
                "target": f"{oscillation_rating.get('target_good', 0):.1f}%",
                "improvement_needed": f"{oscillation_rating.get('improvement_needed', 0):.1f}%",
                "priority": "high"
            })
            
            recommendations["tuning_adjustments"]["kc"] = "decrease_proportional_gain"
            recommendations["tuning_adjustments"]["ti"] = "increase_integral_time"
        
        return recommendations

class Phase8Day8_5Orchestrator:
    """Main orchestrator for Process-Specific Performance Standards"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "phase": "8.8.5",
            "task": "Process-Specific Performance Standards",
            "start_time": self.start_time.isoformat(),
            "standards_database": {},
            "validation_results": {},
            "status": "in_progress"
        }
        
        # Initialize components
        self.standards_db = ProcessStandardsDatabase()
        self.validator = ProcessSpecificValidator(self.standards_db)
        
    async def validate_beer_feed_with_correct_standards(self) -> Dict[str, Any]:
        """Re-validate beer feed data with correct process-specific standards"""
        logger.info("🍺 Re-validating beer feed control with correct standards...")
        
        validation_result = {
            "task": "Beer Feed Control Re-validation",
            "previous_assessment": "stable (INCORRECT)",
            "correct_assessment": "",
            "validation_score": 0.0
        }
        
        try:
            # Beer feed data from Phase 8 Day 6.5 validation
            beer_feed_data = {
                "loop_id": "beer_feed_control",
                "mae": 1.525,  # This was considered "excellent" - WRONG!
                "oscillation_index": 2.8,
                "cv_saturation": 0.0,
                "response_time": 45.0,
                "process_type": ProcessType.BEER_FEED_FLOW
            }
            
            # Assess with correct process-specific standards
            assessment = await self.validator.assess_loop_performance(
                ProcessType.BEER_FEED_FLOW, beer_feed_data
            )
            
            validation_result.update({
                "previous_assessment": {
                    "mae_assessment": "excellent (MAE=1.525 < 2.0 generic)",
                    "overall_score": 79.1,
                    "status": "stable"
                },
                "correct_assessment": {
                    "mae_assessment": f"very_poor (MAE=1.525 >> 0.25 gpm required)",
                    "overall_score": assessment["validation_score"],
                    "status": assessment["overall_rating"],
                    "improvement_needed": assessment["improvement_needed"]
                },
                "performance_details": assessment,
                "validation_score": assessment["validation_score"]
            })
            
            logger.info(f"🎯 Correct beer feed assessment: {assessment['validation_score']:.1f}% ({assessment['overall_rating']})")
            return validation_result
            
        except Exception as e:
            logger.error(f"❌ Beer feed re-validation failed: {e}")
            validation_result["validation_score"] = 0.0
            return validation_result
    
    async def demonstrate_process_specific_standards(self) -> Dict[str, Any]:
        """Demonstrate process-specific standards for multiple process types"""
        logger.info("🎯 Demonstrating process-specific performance standards...")
        
        demo_result = {
            "task": "Process-Specific Standards Demonstration",
            "process_assessments": [],
            "validation_score": 0.0
        }
        
        try:
            # Test different process types with typical performance data
            test_processes = [
                {
                    "type": ProcessType.BEER_FEED_FLOW,
                    "data": {"mae": 1.525, "oscillation_index": 2.8, "cv_saturation": 0.0, "response_time": 45.0}
                },
                {
                    "type": ProcessType.TEMPERATURE_CONTROL, 
                    "data": {"mae": 1.2, "oscillation_index": 1.5, "cv_saturation": 2.0, "response_time": 150.0}
                },
                {
                    "type": ProcessType.PRESSURE_CONTROL,
                    "data": {"mae": 0.3, "oscillation_index": 3.0, "cv_saturation": 1.0, "response_time": 20.0}
                }
            ]
            
            assessment_scores = []
            
            for process_test in test_processes:
                assessment = await self.validator.assess_loop_performance(
                    process_test["type"], process_test["data"]
                )
                
                demo_result["process_assessments"].append({
                    "process_type": process_test["type"].value,
                    "assessment": assessment,
                    "score": assessment["validation_score"]
                })
                
                assessment_scores.append(assessment["validation_score"])
            
            demo_result["validation_score"] = np.mean(assessment_scores) if assessment_scores else 0
            
            logger.info(f"✅ Process-specific standards demonstration: {demo_result['validation_score']:.1f}% average")
            return demo_result
            
        except Exception as e:
            logger.error(f"❌ Standards demonstration failed: {e}")
            demo_result["validation_score"] = 0.0
            return demo_result
    
    async def run_implementation(self) -> Dict[str, Any]:
        """Run complete Phase 8 Day 8.5 implementation"""
        logger.info("🚀 Starting Phase 8 Day 8.5: Process-Specific Performance Standards")
        
        try:
            # Document available standards
            self.results["standards_database"] = {
                "available_processes": [ptype.value for ptype in self.standards_db.list_available_standards()],
                "total_standards": len(self.standards_db.standards),
                "example_beer_feed": asdict(self.standards_db.get_standards(ProcessType.BEER_FEED_FLOW))
            }
            
            # Re-validate beer feed with correct standards
            logger.info("🍺 Step 1: Re-validating beer feed control...")
            beer_feed_validation = await self.validate_beer_feed_with_correct_standards()
            self.results["validation_results"]["beer_feed_revalidation"] = beer_feed_validation
            
            # Demonstrate process-specific standards
            logger.info("🎯 Step 2: Demonstrating process-specific standards...")
            standards_demo = await self.demonstrate_process_specific_standards()
            self.results["validation_results"]["standards_demonstration"] = standards_demo
            
            # Calculate overall validation score
            validation_scores = [
                beer_feed_validation.get("validation_score", 0),
                standards_demo.get("validation_score", 0)
            ]
            overall_score = np.mean(validation_scores) if validation_scores else 0
            
            self.results.update({
                "overall_validation_score": overall_score,
                "status": "completed_excellent" if overall_score >= 85 else "completed_good" if overall_score >= 70 else "completed_needs_improvement",
                "completion_time": datetime.now().isoformat(),
                "duration_minutes": (datetime.now() - self.start_time).total_seconds() / 60
            })
            
            logger.info(f"🎉 Phase 8 Day 8.5 completed with {overall_score:.1f}% validation score")
            
        except Exception as e:
            logger.error(f"❌ Phase 8 Day 8.5 implementation failed: {e}")
            self.results.update({
                "status": "failed",
                "error": str(e),
                "completion_time": datetime.now().isoformat()
            })
        
        return self.results

async def main():
    """Main execution function"""
    orchestrator = Phase8Day8_5Orchestrator()
    results = await orchestrator.run_implementation()
    
    # Save results
    results_dir = Path(__file__).parent.parent.parent / "results" / "phase8"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"phase8_day8_5_process_standards_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n🎯 Phase 8 Day 8.5 Process-Specific Standards Results:")
    print(f"Overall Validation Score: {results.get('overall_validation_score', 0):.1f}%")
    
    # Show beer feed re-assessment
    beer_feed = results.get('validation_results', {}).get('beer_feed_revalidation', {})
    if beer_feed:
        print(f"\n🍺 Beer Feed Control Re-assessment:")
        print(f"Previous (WRONG): 'Stable' with MAE=1.525 < 2.0 generic")
        correct = beer_feed.get('correct_assessment', {})
        print(f"Correct Assessment: '{correct.get('status', 'unknown').title()}' with MAE=1.525 >> 0.25 gpm required")
        print(f"Validation Score: {beer_feed.get('validation_score', 0):.1f}%")
    
    print(f"\nAvailable Process Standards: {len(results.get('standards_database', {}).get('available_processes', []))}")
    print(f"Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main()) 