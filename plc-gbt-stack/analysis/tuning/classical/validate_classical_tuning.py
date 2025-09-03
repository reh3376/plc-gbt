#!/usr/bin/env python3
"""
Phase 22.2.2: Classical Tuning Methods Production Validation
==========================================================

Comprehensive validation and testing suite for all classical PID tuning methods.
Tests the actual implementation using the correct execute() interface and validates
all industrial control scenarios with proper error handling.

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.2 - Classical Tuning Methods
Methodology: AI Task Orchestrator Guide
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime
from typing import Any, Dict, Tuple

# Add parent directories to path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import classical tuning methods
try:
    from astrom_hagglund import AstromHagglundTuner
    from chien_hrones_reswick import ChienHronesReswickTuner
    from classical_manager import ClassicalTuningManager
    from cohen_coon import CohenCoonTuner
    from lambda_tuning import LambdaTuner
    from tyreus_luyben import TyreusLuybenTuner
    from ziegler_nichols import ZieglerNicholsProcessReaction, ZieglerNicholsUltimateGain

    IMPLEMENTATIONS_AVAILABLE = True
    print("✅ All classical tuning implementations loaded successfully")

except ImportError as e:
    print(f"❌ Failed to import classical tuning methods: {e}")
    IMPLEMENTATIONS_AVAILABLE = False


class ClassicalTuningProductionValidator:
    """Production-grade validation suite for classical tuning methods"""

    def __init__(self):
        self.results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'methods': {},
            'execution_times': [],
            'validation_score': 0.0,
            'timestamp': datetime.now().isoformat(),
            'production_ready': False
        }

        # Industrial test scenarios with realistic process parameters
        self.test_scenarios = [
            {
                'name': 'Fast Temperature Process',
                'description': 'Fast responding temperature control with moderate dead time',
                'data': {
                    'process_gain': 2.5,
                    'dead_time': 1.0,
                    'time_constant': 5.0,
                    'ultimate_gain': 4.2,
                    'ultimate_period': 8.0,
                    'controller_type': 'dependent',
                    'response_type': 'quarter_decay',  # For ZN methods
                    'cc_response_type': 'standard',     # For Cohen-Coon
                    'chr_response_type': 'setpoint'     # For CHR
                }
            },
            {
                'name': 'Flow Control Process',
                'description': 'Flow control with fast dynamics and minimal dead time',
                'data': {
                    'process_gain': 1.8,
                    'dead_time': 0.5,
                    'time_constant': 3.0,
                    'ultimate_gain': 6.1,
                    'ultimate_period': 5.2,
                    'controller_type': 'dependent',
                    'response_type': 'quarter_decay',
                    'cc_response_type': 'standard',
                    'chr_response_type': 'setpoint'
                }
            },
            {
                'name': 'Dead Time Dominant Process',
                'description': 'High dead time process typical in large industrial systems',
                'data': {
                    'process_gain': 1.2,
                    'dead_time': 6.0,
                    'time_constant': 8.0,
                    'ultimate_gain': 2.8,
                    'ultimate_period': 15.6,
                    'controller_type': 'dependent',
                    'response_type': 'no_overshoot',
                    'cc_response_type': 'conservative',
                    'chr_response_type': 'disturbance'
                }
            },
            {
                'name': 'High Gain Pressure Process',
                'description': 'High gain pressure control with medium dynamics',
                'data': {
                    'process_gain': 4.0,
                    'dead_time': 2.5,
                    'time_constant': 12.0,
                    'ultimate_gain': 3.5,
                    'ultimate_period': 20.0,
                    'controller_type': 'dependent',
                    'response_type': 'some_overshoot',
                    'cc_response_type': 'aggressive',
                    'chr_response_type': 'setpoint'
                }
            }
        ]

    def test_method(self, method_name: str, tuner_class, test_scenario: Dict) -> Tuple[bool, str, float, Dict]:
        """Test a single tuning method with a scenario using the correct execute interface"""
        start_time = time.time()

        try:
            # Create tuner instance
            tuner = tuner_class()

            # Prepare data for execute method
            data = test_scenario['data'].copy()

            # Use the appropriate response type for each method
            if 'Cohen-Coon' in method_name:
                data['response_type'] = data['cc_response_type']
            elif 'Chien-Hrones-Reswick' in method_name:
                data['response_type'] = data['chr_response_type']
            # ZN and other methods already use the correct response_type

            # Execute tuning using the correct interface
            result = tuner.execute(data)

            execution_time = time.time() - start_time

            # Validate result structure
            if not isinstance(result, dict):
                return False, f"Invalid result type: {type(result)}", execution_time, {}

            # Check for success
            if not result.get('success', False):
                error_msg = result.get('error', 'Unknown error')
                return False, f"Method failed: {error_msg}", execution_time, {}

            # Extract tuning result
            tuning_result = result.get('result')
            if not tuning_result:
                return False, "No tuning result returned", execution_time, {}

            # Validate parameters
            if hasattr(tuning_result, 'parameters'):
                params = tuning_result.parameters
                if not self._validate_parameters(params):
                    return False, f"Invalid parameters: {params}", execution_time, {}
            else:
                return False, "No parameters in tuning result", execution_time, {}

            # Create detailed results
            detailed_results = {
                'method': tuning_result.tuning_method if hasattr(tuning_result, 'tuning_method') else method_name,
                'parameters': params,
                'execution_time': execution_time,
                'performance': getattr(tuning_result, 'performance_prediction', {}),
                'stability': getattr(tuning_result, 'stability_analysis', {}),
                'confidence': 0.85  # Default confidence
            }

            return True, "SUCCESS", execution_time, detailed_results

        except Exception as e:
            execution_time = time.time() - start_time
            return False, f"{method_name} test failed: {str(e)}", execution_time, {}

    def test_classical_manager(self, test_scenario: Dict) -> Tuple[bool, str, float, Dict]:
        """Test the Classical Tuning Manager specifically"""
        start_time = time.time()

        try:
            manager = ClassicalTuningManager()

            # Prepare data for manager
            data = test_scenario['data'].copy()
            data['selection_strategy'] = 'automatic'

            # Execute manager
            result = manager.execute(data)

            execution_time = time.time() - start_time

            # Validate result
            if not isinstance(result, dict) or not result.get('success', False):
                error_msg = result.get('error', 'Manager execution failed')
                return False, error_msg, execution_time, {}

            comparison_result = result.get('result')
            if not comparison_result:
                return False, "No comparison result returned", execution_time, {}

            # Check for recommended method
            recommended_method = getattr(comparison_result, 'recommended_method', 'Unknown')

            detailed_results = {
                'recommended_method': recommended_method,
                'execution_time': execution_time,
                'methods_compared': getattr(comparison_result, 'method_count', 0),
                'confidence': 0.90
            }

            return True, "SUCCESS", execution_time, detailed_results

        except Exception as e:
            execution_time = time.time() - start_time
            return False, f"Classical Manager test failed: {str(e)}", execution_time, {}

    def _validate_parameters(self, params: Dict[str, Any]) -> bool:
        """Validate PID parameter ranges"""
        try:
            # Check for required parameters
            if 'Kp' not in params:
                return False

            kp = float(params['Kp'])

            # Basic range checks
            if not (0.001 <= kp <= 1000):
                return False

            # Check Ti if present
            if 'Ti' in params:
                ti = float(params['Ti'])
                if ti <= 0 or ti > 10000:
                    return False

            # Check Td if present
            if 'Td' in params:
                td = float(params['Td'])
                if td < 0 or td > 1000:
                    return False

            # Check for NaN or infinite values
            for value in params.values():
                if isinstance(value, (int, float)):
                    if not (-1e6 < float(value) < 1e6):
                        return False

            return True

        except (ValueError, TypeError):
            return False

    def run_comprehensive_validation(self):
        """Run comprehensive validation of all classical tuning methods"""

        print("🔧 Phase 22.2.2: Classical Tuning Methods Production Validation")
        print("=" * 70)
        print()

        if not IMPLEMENTATIONS_AVAILABLE:
            print("❌ Cannot run validation - implementations not available")
            return

        # Define test methods with their proper classes
        test_methods = [
            ('Ziegler-Nichols Ultimate Gain', ZieglerNicholsUltimateGain),
            ('Ziegler-Nichols Process Reaction', ZieglerNicholsProcessReaction),
            ('Cohen-Coon', CohenCoonTuner),
            ('Tyreus-Luyben', TyreusLuybenTuner),
            ('Åström-Hägglund', AstromHagglundTuner),
            ('Chien-Hrones-Reswick', ChienHronesReswickTuner),
            ('Lambda Tuning', LambdaTuner)
        ]

        for method_name, tuner_class in test_methods:
            print(f"🎯 Testing {method_name}")
            print("-" * 50)

            method_results = {
                'passed': 0,
                'failed': 0,
                'execution_times': [],
                'errors': [],
                'detailed_results': []
            }

            for scenario in self.test_scenarios:
                print(f"  📊 Testing scenario: {scenario['name']}")

                success, error_msg, execution_time, detailed_results = self.test_method(
                    method_name, tuner_class, scenario
                )

                # Update counters
                self.results['total_tests'] += 1
                if success:
                    self.results['passed_tests'] += 1
                    method_results['passed'] += 1
                    print(f"    ✅ PASSED: {error_msg}")

                    # Display parameters if available
                    if 'parameters' in detailed_results:
                        params = detailed_results['parameters']
                        param_str = ", ".join([f"{k}={v:.3f}" if isinstance(v, (int, float)) else f"{k}={v}"
                                             for k, v in params.items()])
                        print(f"    📈 Parameters: {param_str}")
                else:
                    self.results['failed_tests'] += 1
                    method_results['failed'] += 1
                    method_results['errors'].append(error_msg)
                    print(f"    ❌ FAILED: {error_msg}")

                method_results['execution_times'].append(execution_time)
                method_results['detailed_results'].append(detailed_results)
                self.results['execution_times'].append(execution_time)

            # Calculate method statistics
            total_method_tests = len(self.test_scenarios)
            success_rate = (method_results['passed'] / total_method_tests) * 100
            avg_time = sum(method_results['execution_times']) / len(method_results['execution_times'])

            print(f"  📊 Method Summary: {method_results['passed']}/{total_method_tests} passed ({success_rate:.1f}%)")
            print(f"  ⏱️  Average execution time: {avg_time:.3f}s")
            print()

            # Store method results
            self.results['methods'][method_name] = {
                'passed': method_results['passed'],
                'failed': method_results['failed'],
                'success_rate': success_rate,
                'avg_execution_time': avg_time,
                'errors': method_results['errors'],
                'detailed_results': method_results['detailed_results']
            }

        # Test Classical Manager separately
        print("🎯 Testing Classical Manager")
        print("-" * 50)

        manager_results = {'passed': 0, 'failed': 0, 'execution_times': [], 'errors': [], 'detailed_results': []}

        for scenario in self.test_scenarios:
            print(f"  📊 Testing scenario: {scenario['name']}")

            success, error_msg, execution_time, detailed_results = self.test_classical_manager(scenario)

            self.results['total_tests'] += 1
            if success:
                self.results['passed_tests'] += 1
                manager_results['passed'] += 1
                print(f"    ✅ PASSED: {error_msg}")
                if 'recommended_method' in detailed_results:
                    print(f"    🎯 Recommended: {detailed_results['recommended_method']}")
            else:
                self.results['failed_tests'] += 1
                manager_results['failed'] += 1
                manager_results['errors'].append(error_msg)
                print(f"    ❌ FAILED: {error_msg}")

            manager_results['execution_times'].append(execution_time)
            manager_results['detailed_results'].append(detailed_results)
            self.results['execution_times'].append(execution_time)

        # Calculate manager statistics
        total_manager_tests = len(self.test_scenarios)
        manager_success_rate = (manager_results['passed'] / total_manager_tests) * 100
        manager_avg_time = sum(manager_results['execution_times']) / len(manager_results['execution_times'])

        print(f"  📊 Manager Summary: {manager_results['passed']}/{total_manager_tests} passed ({manager_success_rate:.1f}%)")
        print(f"  ⏱️  Average execution time: {manager_avg_time:.3f}s")
        print()

        # Store manager results
        self.results['methods']['Classical Manager'] = {
            'passed': manager_results['passed'],
            'failed': manager_results['failed'],
            'success_rate': manager_success_rate,
            'avg_execution_time': manager_avg_time,
            'errors': manager_results['errors'],
            'detailed_results': manager_results['detailed_results']
        }

        # Calculate overall validation score
        if self.results['total_tests'] > 0:
            self.results['validation_score'] = (self.results['passed_tests'] / self.results['total_tests']) * 100

        # Determine production readiness
        self.results['production_ready'] = self.results['validation_score'] >= 85

        self._print_final_results()
        self._save_results()

    def _print_final_results(self):
        """Print comprehensive final results"""
        print("=" * 70)
        print("🏁 PHASE 22.2.2 CLASSICAL TUNING METHODS - PRODUCTION VALIDATION")
        print("=" * 70)
        print()

        # Overall results
        print("📊 OVERALL RESULTS:")
        print(f"   Total Tests: {self.results['total_tests']}")
        print(f"   Passed: {self.results['passed_tests']} ✅")
        print(f"   Failed: {self.results['failed_tests']} ❌")
        print(f"   Success Rate: {self.results['validation_score']:.1f}%")

        # Grade assignment
        score = self.results['validation_score']
        if score >= 95:
            grade = "A+ (Outstanding)"
            status = "✅ OUTSTANDING"
        elif score >= 90:
            grade = "A (Excellent)"
            status = "✅ EXCELLENT"
        elif score >= 80:
            grade = "B+ (Very Good)"
            status = "✅ VERY GOOD"
        elif score >= 70:
            grade = "B (Good)"
            status = "✅ GOOD"
        elif score >= 60:
            grade = "C (Fair)"
            status = "⚠️ FAIR"
        else:
            grade = "F (Poor)"
            status = "❌ FAILED"

        print(f"   Validation Score: {score:.3f} ({grade})")
        print(f"   Overall Status: {status}")
        print(f"   Production Ready: {'✅ YES' if self.results['production_ready'] else '❌ NO'}")
        print()

        # Method-by-method results
        print("📋 METHOD RESULTS:")
        for method_name, results in self.results['methods'].items():
            status_icon = "✅" if results['success_rate'] >= 75 else "⚠️" if results['success_rate'] >= 50 else "❌"
            print(f"   {status_icon} {method_name}:")
            print(f"      Success Rate: {results['success_rate']:.1f}% ({results['passed']}/{results['passed'] + results['failed']})")
            print(f"      Avg Execution Time: {results['avg_execution_time']:.3f}s")
            if results['errors']:
                print(f"      Errors: {len(results['errors'])}")

            # Show sample parameters from successful tests
            successful_results = [r for r in results['detailed_results'] if 'parameters' in r]
            if successful_results:
                sample_params = successful_results[0]['parameters']
                param_str = ", ".join([f"{k}={v:.3f}" if isinstance(v, (int, float)) else f"{k}={v}"
                                     for k, v in list(sample_params.items())[:3]])
                print(f"      Sample Parameters: {param_str}")
        print()

        # Performance analysis
        if self.results['execution_times']:
            avg_time = sum(self.results['execution_times']) / len(self.results['execution_times'])
            min_time = min(self.results['execution_times'])
            max_time = max(self.results['execution_times'])

            print("⏱️ PERFORMANCE ANALYSIS:")
            print(f"   Average Execution Time: {avg_time:.3f}s")
            print(f"   Fastest Test: {min_time:.3f}s")
            print(f"   Slowest Test: {max_time:.3f}s")
            print(f"   Performance Rating: {'Excellent' if avg_time < 0.1 else 'Good' if avg_time < 0.5 else 'Fair'}")
            print()

        # Recommendations
        print("💡 RECOMMENDATIONS:")
        if self.results['validation_score'] >= 90:
            print("   ✅ Classical tuning methods are production-ready")
            print("   ✅ All major methods implemented and validated successfully")
            print("   ✅ Ready to proceed to Phase 22.2.3: Advanced Tuning Strategies")
            print("   ✅ Performance is excellent across all industrial scenarios")
        elif self.results['validation_score'] >= 75:
            print("   ✅ Classical tuning methods are working well")
            print("   ⚠️ Minor improvements recommended for production deployment")
            print("   ✅ Can proceed to next phase with monitoring")
        else:
            print("   ❌ Significant issues detected in classical tuning methods")
            print("   ❌ Address failures before proceeding to next phase")
            print("   ❌ Consider debugging and additional testing")
        print()

        # Phase completion status
        print("🎯 PHASE 22.2.2 COMPLETION STATUS:")
        if self.results['validation_score'] >= 85:
            print("   ✅ PHASE 22.2.2 SUCCESSFULLY COMPLETED")
            print("   ✅ Classical Tuning Methods production validated")
            print("   ✅ Ready for Phase 22.2.3: Advanced Tuning Strategies")
        elif self.results['validation_score'] >= 70:
            print("   ⚠️ PHASE 22.2.2 COMPLETED WITH MINOR ISSUES")
            print("   ⚠️ Address recommendations before Phase 22.2.3")
        else:
            print("   ❌ PHASE 22.2.2 REQUIRES ATTENTION")
            print("   ❌ Address validation issues before proceeding")
        print("=" * 70)
        print()

    def _save_results(self):
        """Save validation results to JSON file"""
        filename = "classical_tuning_production_validation.json"

        # Convert results to JSON-serializable format
        json_results = self.results.copy()

        try:
            with open(filename, 'w') as f:
                json.dump(json_results, f, indent=2, default=str)
            print(f"📁 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save results: {e}")


def main():
    """Main validation execution"""
    try:
        validator = ClassicalTuningProductionValidator()
        validator.run_comprehensive_validation()

        # Return validation score for programmatic use
        return validator.results['validation_score']

    except Exception as e:
        print(f"❌ Critical error during validation: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return 0.0


if __name__ == "__main__":
    validation_score = main()

    # Exit with appropriate code based on production readiness
    if validation_score >= 90:
        sys.exit(0)  # Excellent - production ready
    elif validation_score >= 75:
        sys.exit(1)  # Good - proceed with caution
    else:
        sys.exit(2)  # Poor - needs attention
