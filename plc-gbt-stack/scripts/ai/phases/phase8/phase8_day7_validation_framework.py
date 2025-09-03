#!/usr/bin/env python3
"""
Phase 8 Day 7: Advanced Control Features Validation Framework
=============================================================

Comprehensive validation framework following AI Task Orchestrator Guide methodology
to validate the implementation of advanced control features including:
- Feed-forward and cascade control systems
- Multi-loop interaction analysis and coordination
- Advanced controller options (Smith predictor, adaptive control, constraint optimization)

This framework ensures quality, correctness, and integration compliance.
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Validation result structure"""
    component: str
    test_name: str
    status: str  # "passed", "failed", "warning"
    score: float  # 0.0 - 1.0
    details: Dict[str, Any]
    timestamp: str

@dataclass
class ValidationSummary:
    """Overall validation summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    overall_score: float
    validation_level: str  # "excellent", "good", "acceptable", "poor"

class Phase8Day7ValidationFramework:
    """
    Comprehensive validation framework for Phase 8 Day 7 implementation
    Following AI Task Orchestrator Guide methodology
    """

    def __init__(self):
        self.session_id = f"phase8_day7_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.results_dir = Path("results/phase8")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        self.validation_results = []
        self.implementation_results = None

    def load_implementation_results(self) -> bool:
        """Load the latest Phase 8 Day 7 implementation results"""
        try:
            # Find the most recent results file
            results_files = list(self.results_dir.glob("phase8_day7_*_complete_results.json"))
            if not results_files:
                logger.error("❌ No implementation results found")
                return False

            latest_file = max(results_files, key=lambda x: x.stat().st_mtime)

            with open(latest_file) as f:
                self.implementation_results = json.load(f)

            logger.info(f"✅ Loaded implementation results from: {latest_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load implementation results: {e}")
            return False

    def validate_phase_8_7_1_feedforward_cascade(self) -> List[ValidationResult]:
        """Validate Phase 8.7.1: Feed-forward and Cascade Control Implementation"""
        results = []

        if "8.7.1" not in self.implementation_results["phases"]:
            results.append(ValidationResult(
                component="Phase 8.7.1",
                test_name="Phase Existence",
                status="failed",
                score=0.0,
                details={"error": "Phase 8.7.1 not found in results"},
                timestamp=datetime.now().isoformat()
            ))
            return results

        phase_data = self.implementation_results["phases"]["8.7.1"]
        components = phase_data.get("components", {})

        # Test 1: Feed-forward Controller Validation
        if "feedforward" in components:
            ff_data = components["feedforward"]
            ff_score = 0.0
            ff_details = {}

            # Check class implementation
            if ff_data.get("class") == "FeedforwardController":
                ff_score += 0.25
                ff_details["class_implemented"] = True
            else:
                ff_details["class_implemented"] = False

            # Check configuration
            config = ff_data.get("config", {})
            if all(key in config for key in ["disturbance_variable", "lead_time", "gain"]):
                ff_score += 0.25
                ff_details["configuration_complete"] = True
            else:
                ff_details["configuration_complete"] = False

            # Check functionality
            if ff_data.get("test_disturbance") and ff_data.get("ff_output"):
                ff_score += 0.25
                ff_details["functionality_tested"] = True
            else:
                ff_details["functionality_tested"] = False

            # Check lead compensator
            if ff_data.get("lead_compensator_available"):
                ff_score += 0.25
                ff_details["lead_compensator"] = True
            else:
                ff_details["lead_compensator"] = False

            results.append(ValidationResult(
                component="FeedforwardController",
                test_name="Implementation Validation",
                status="passed" if ff_score >= 0.7 else "warning" if ff_score >= 0.5 else "failed",
                score=ff_score,
                details=ff_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 2: Cascade Control Manager Validation
        if "cascade" in components:
            cascade_data = components["cascade"]
            cascade_score = 0.0
            cascade_details = {}

            # Check class implementation
            if cascade_data.get("class") == "CascadeControlManager":
                cascade_score += 0.3
                cascade_details["class_implemented"] = True

            # Check configuration success
            if cascade_data.get("config_success"):
                cascade_score += 0.3
                cascade_details["configuration_successful"] = True

            # Check loop configuration
            if cascade_data.get("total_loops_configured", 0) > 0:
                cascade_score += 0.2
                cascade_details["loops_configured"] = cascade_data.get("total_loops_configured", 0)

            # Check calculation functionality
            if cascade_data.get("test_secondary_sp") is not None:
                cascade_score += 0.2
                cascade_details["calculation_functional"] = True

            results.append(ValidationResult(
                component="CascadeControlManager",
                test_name="Implementation Validation",
                status="passed" if cascade_score >= 0.7 else "warning" if cascade_score >= 0.5 else "failed",
                score=cascade_score,
                details=cascade_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 3: Disturbance Mapper Validation
        if "disturbance_mapper" in components:
            dm_data = components["disturbance_mapper"]
            dm_score = 0.0
            dm_details = {}

            # Check class and registrations
            if dm_data.get("class") == "DisturbanceMapper":
                dm_score += 0.25

            if dm_data.get("registered_disturbances", 0) >= 2:
                dm_score += 0.25
                dm_details["registrations"] = dm_data.get("registered_disturbances", 0)

            # Check impact mapping
            impact_map = dm_data.get("test_impact_map", {})
            if len(impact_map) >= 2:
                dm_score += 0.25
                dm_details["impact_mapping"] = True

            # Check compensation recommendations
            compensation = dm_data.get("test_compensation", {})
            if "strategy" in compensation and "actions" in compensation:
                dm_score += 0.25
                dm_details["compensation_logic"] = True

            results.append(ValidationResult(
                component="DisturbanceMapper",
                test_name="Implementation Validation",
                status="passed" if dm_score >= 0.7 else "warning" if dm_score >= 0.5 else "failed",
                score=dm_score,
                details=dm_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 4: Integration Test Validation
        if "integration_test" in components:
            int_data = components["integration_test"]
            int_score = 0.0
            int_details = {}

            # Check overall success
            if int_data.get("overall_success"):
                int_score += 0.5
                int_details["overall_success"] = True

            # Check test scenarios
            scenarios = int_data.get("test_scenarios", [])
            if len(scenarios) >= 2:
                int_score += 0.3
                successful_scenarios = sum(1 for s in scenarios if s.get("success"))
                int_details["scenarios_tested"] = len(scenarios)
                int_details["scenarios_successful"] = successful_scenarios

                if successful_scenarios == len(scenarios):
                    int_score += 0.2

            results.append(ValidationResult(
                component="IntegrationTest",
                test_name="Feed-forward Cascade Integration",
                status="passed" if int_score >= 0.7 else "warning" if int_score >= 0.5 else "failed",
                score=int_score,
                details=int_details,
                timestamp=datetime.now().isoformat()
            ))

        return results

    def validate_phase_8_7_2_multiloop_interaction(self) -> List[ValidationResult]:
        """Validate Phase 8.7.2: Multi-Loop Interaction Analysis"""
        results = []

        if "8.7.2" not in self.implementation_results["phases"]:
            results.append(ValidationResult(
                component="Phase 8.7.2",
                test_name="Phase Existence",
                status="failed",
                score=0.0,
                details={"error": "Phase 8.7.2 not found in results"},
                timestamp=datetime.now().isoformat()
            ))
            return results

        phase_data = self.implementation_results["phases"]["8.7.2"]
        components = phase_data.get("components", {})

        # Test 1: Loop Interaction Analyzer
        if "interaction_analyzer" in components:
            ia_data = components["interaction_analyzer"]
            ia_score = 0.0
            ia_details = {}

            if ia_data.get("class") == "LoopInteractionAnalyzer":
                ia_score += 0.25

            if ia_data.get("detected_interactions", 0) > 0:
                ia_score += 0.25
                ia_details["interactions_detected"] = ia_data.get("detected_interactions", 0)

            if ia_data.get("strongest_interaction", 0) > 0:
                ia_score += 0.25
                ia_details["strongest_interaction"] = ia_data.get("strongest_interaction", 0)

            if ia_data.get("test_loops", 0) >= 3:
                ia_score += 0.25

            results.append(ValidationResult(
                component="LoopInteractionAnalyzer",
                test_name="Interaction Analysis",
                status="passed" if ia_score >= 0.7 else "warning" if ia_score >= 0.5 else "failed",
                score=ia_score,
                details=ia_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 2: Interaction Matrix
        if "interaction_matrix" in components:
            im_data = components["interaction_matrix"]
            im_score = 0.0
            im_details = {}

            if im_data.get("rga_calculated"):
                im_score += 0.4
                im_details["rga_calculated"] = True

            if im_data.get("recommended_pairings"):
                im_score += 0.3
                im_details["pairings_recommended"] = len(im_data.get("recommended_pairings", []))

            if im_data.get("matrix_size", 0) >= 2:
                im_score += 0.3

            results.append(ValidationResult(
                component="InteractionMatrix",
                test_name="RGA Calculation",
                status="passed" if im_score >= 0.7 else "warning" if im_score >= 0.5 else "failed",
                score=im_score,
                details=im_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 3: Decoupling Controller
        if "decoupling_controller" in components:
            dc_data = components["decoupling_controller"]
            dc_score = 0.0
            dc_details = {}

            if dc_data.get("test_signals") and dc_data.get("decoupled_signals"):
                dc_score += 0.5
                dc_details["decoupling_functional"] = True

            condition_number = dc_data.get("decoupler_condition_number", float('inf'))
            if condition_number < 10:  # Well-conditioned
                dc_score += 0.5
                dc_details["well_conditioned"] = True
            else:
                dc_details["well_conditioned"] = False

            results.append(ValidationResult(
                component="DecouplingController",
                test_name="Decoupling Algorithm",
                status="passed" if dc_score >= 0.7 else "warning" if dc_score >= 0.5 else "failed",
                score=dc_score,
                details=dc_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 4: Multi-Loop Coordinator
        if "multiloop_coordinator" in components:
            mc_data = components["multiloop_coordinator"]
            mc_score = 0.0
            mc_details = {}

            if mc_data.get("registered_loops", 0) >= 2:
                mc_score += 0.3
                mc_details["loops_registered"] = mc_data.get("registered_loops", 0)

            coordination = mc_data.get("test_coordination", {})
            if coordination:
                mc_score += 0.4
                mc_details["coordination_tested"] = True

                # Check if coordination actually modifies outputs
                modified_outputs = 0
                for loop_data in coordination.values():
                    if loop_data.get("original_output") != loop_data.get("coordinated_output"):
                        modified_outputs += 1

                if modified_outputs > 0:
                    mc_score += 0.3
                    mc_details["outputs_modified"] = modified_outputs

            results.append(ValidationResult(
                component="MultiLoopCoordinator",
                test_name="Loop Coordination",
                status="passed" if mc_score >= 0.7 else "warning" if mc_score >= 0.5 else "failed",
                score=mc_score,
                details=mc_details,
                timestamp=datetime.now().isoformat()
            ))

        return results

    def validate_phase_8_7_3_advanced_controllers(self) -> List[ValidationResult]:
        """Validate Phase 8.7.3: Advanced Controller Options"""
        results = []

        if "8.7.3" not in self.implementation_results["phases"]:
            results.append(ValidationResult(
                component="Phase 8.7.3",
                test_name="Phase Existence",
                status="failed",
                score=0.0,
                details={"error": "Phase 8.7.3 not found in results"},
                timestamp=datetime.now().isoformat()
            ))
            return results

        phase_data = self.implementation_results["phases"]["8.7.3"]
        components = phase_data.get("components", {})

        # Test 1: Smith Predictor
        if "smith_predictor" in components:
            sp_data = components["smith_predictor"]
            sp_score = 0.0
            sp_details = {}

            if sp_data.get("class") == "SmithPredictorController":
                sp_score += 0.25

            if sp_data.get("process_model") and sp_data.get("dead_time", 0) > 0:
                sp_score += 0.25
                sp_details["model_configured"] = True

            if sp_data.get("test_prediction") is not None:
                sp_score += 0.25
                sp_details["prediction_functional"] = True

            if sp_data.get("buffer_size", 0) > 0:
                sp_score += 0.25
                sp_details["buffer_implemented"] = True

            results.append(ValidationResult(
                component="SmithPredictorController",
                test_name="Dead-time Compensation",
                status="passed" if sp_score >= 0.7 else "warning" if sp_score >= 0.5 else "failed",
                score=sp_score,
                details=sp_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 2: Adaptive Control
        if "adaptive_control" in components:
            ac_data = components["adaptive_control"]
            ac_score = 0.0
            ac_details = {}

            if ac_data.get("adaptation_enabled"):
                ac_score += 0.3
                ac_details["adaptation_enabled"] = True

            if ac_data.get("adapted_parameters"):
                ac_score += 0.3
                params = ac_data.get("adapted_parameters", {})
                if all(key in params for key in ["kp", "ki"]):
                    ac_score += 0.2
                    ac_details["parameters_adapted"] = True

            if ac_data.get("adaptation_steps", 0) > 0:
                ac_score += 0.2
                ac_details["adaptation_steps"] = ac_data.get("adaptation_steps", 0)

            results.append(ValidationResult(
                component="AdaptiveControlFramework",
                test_name="Parameter Adaptation",
                status="passed" if ac_score >= 0.7 else "warning" if ac_score >= 0.5 else "failed",
                score=ac_score,
                details=ac_details,
                timestamp=datetime.now().isoformat()
            ))

        # Test 3: Constraint Optimizer
        if "constraint_optimizer" in components:
            co_data = components["constraint_optimizer"]
            co_score = 0.0
            co_details = {}

            if co_data.get("active_constraints", 0) > 0:
                co_score += 0.3
                co_details["constraints_defined"] = co_data.get("active_constraints", 0)

            if co_data.get("optimized_values"):
                co_score += 0.4
                co_details["optimization_functional"] = True

            if co_data.get("constraint_violations"):
                co_score += 0.3
                violations = co_data.get("constraint_violations", {})
                co_details["violation_checking"] = len(violations) > 0

            results.append(ValidationResult(
                component="ConstraintOptimizer",
                test_name="Constraint Optimization",
                status="passed" if co_score >= 0.7 else "warning" if co_score >= 0.5 else "failed",
                score=co_score,
                details=co_details,
                timestamp=datetime.now().isoformat()
            ))

        return results

    def calculate_validation_summary(self, all_results: List[ValidationResult]) -> ValidationSummary:
        """Calculate overall validation summary"""

        total_tests = len(all_results)
        passed_tests = sum(1 for r in all_results if r.status == "passed")
        failed_tests = sum(1 for r in all_results if r.status == "failed")
        warning_tests = sum(1 for r in all_results if r.status == "warning")

        # Calculate overall score
        if total_tests > 0:
            overall_score = sum(r.score for r in all_results) / total_tests
        else:
            overall_score = 0.0

        # Determine validation level
        if overall_score >= 0.9:
            validation_level = "excellent"
        elif overall_score >= 0.8:
            validation_level = "good"
        elif overall_score >= 0.6:
            validation_level = "acceptable"
        else:
            validation_level = "poor"

        return ValidationSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            overall_score=overall_score,
            validation_level=validation_level
        )

    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of Phase 8 Day 7 implementation"""

        logger.info("🧪 Starting Phase 8 Day 7 Comprehensive Validation")

        # Load implementation results
        if not self.load_implementation_results():
            return {"status": "failed", "error": "Could not load implementation results"}

        validation_session = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "methodology": "AI Task Orchestrator Guide Validation Framework",
            "implementation_session": self.implementation_results.get("session_id", "unknown"),
            "validation_results": {}
        }

        try:
            # Validate each phase
            phase_8_7_1_results = self.validate_phase_8_7_1_feedforward_cascade()
            phase_8_7_2_results = self.validate_phase_8_7_2_multiloop_interaction()
            phase_8_7_3_results = self.validate_phase_8_7_3_advanced_controllers()

            # Combine all results
            all_results = phase_8_7_1_results + phase_8_7_2_results + phase_8_7_3_results
            self.validation_results = all_results

            # Calculate summary
            summary = self.calculate_validation_summary(all_results)

            validation_session["validation_results"] = {
                "phase_8_7_1": [asdict(r) for r in phase_8_7_1_results],
                "phase_8_7_2": [asdict(r) for r in phase_8_7_2_results],
                "phase_8_7_3": [asdict(r) for r in phase_8_7_3_results],
                "summary": asdict(summary)
            }

            validation_session["overall_status"] = "completed"
            validation_session["completion_time"] = datetime.now().isoformat()

            # Save validation results
            results_file = self.results_dir / f"{self.session_id}_validation_results.json"
            with open(results_file, 'w') as f:
                json.dump(validation_session, f, indent=2)

            logger.info(f"✅ Validation completed. Results: {results_file}")

        except Exception as e:
            validation_session["overall_status"] = "failed"
            validation_session["error"] = str(e)
            logger.error(f"❌ Validation failed: {e}")

        return validation_session

def main():
    """Main execution function"""
    async def run_validation():
        validator = Phase8Day7ValidationFramework()
        results = await validator.run_comprehensive_validation()

        # Print summary
        print("\n" + "="*80)
        print("🧪 PHASE 8 DAY 7 VALIDATION SUMMARY")
        print("="*80)

        if "validation_results" in results:
            summary = results["validation_results"]["summary"]
            print(f"Overall Score: {summary['overall_score']:.3f} ({summary['validation_level'].upper()})")
            print(f"Total Tests: {summary['total_tests']}")
            print(f"  • Passed: {summary['passed_tests']}")
            print(f"  • Warnings: {summary['warning_tests']}")
            print(f"  • Failed: {summary['failed_tests']}")
            print()

            # Phase-by-phase breakdown
            for phase_name, phase_results in results["validation_results"].items():
                if phase_name != "summary" and isinstance(phase_results, list):
                    avg_score = sum(r["score"] for r in phase_results) / len(phase_results) if phase_results else 0
                    print(f"{phase_name}: {avg_score:.3f} ({len(phase_results)} tests)")

        else:
            print(f"Status: {results.get('overall_status', 'unknown')}")
            if 'error' in results:
                print(f"Error: {results['error']}")

        print("="*80)

        return results

    return asyncio.run(run_validation())

if __name__ == "__main__":
    main()
