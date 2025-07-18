#!/usr/bin/env python3
"""
Phase 22.2.3: Advanced Tuning Strategies Production Validation
=============================================================

Comprehensive validation and testing suite for all advanced tuning strategies.
Tests MPC tuning, adaptive control, gain scheduling, multi-loop coordination,
and the advanced tuning manager with industrial scenarios.

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.3 - Advanced Tuning Strategies
Methodology: AI Task Orchestrator Guide
"""

import sys
import os
import time
import json
import traceback
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Add parent directories to path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Import advanced strategies
    from mpc_tuning import MPCTuner, EconomicMPCTuner, RobustMPCTuner, HybridMPCTuner
    from adaptive_control import AdaptiveController, RLSAdaptiveController, GradientDescentController
    from gain_scheduling import GainScheduler, LinearGainScheduler, FuzzyGainScheduler
    from multi_loop_coordination import MultiLoopCoordinator, DecentralizedCoordinator, CentralizedCoordinator
    from advanced_manager import AdvancedTuningManager
    
    IMPORTS_SUCCESSFUL = True
    import_errors = []
    
except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    import_errors = [str(e)]
    print(f"❌ Import Error: {e}")

def main():
    """Main validation function"""
    
    print("🧪 Phase 22.2.3: Advanced Tuning Strategies Production Validation")
    print("=" * 80)
    
    if not IMPORTS_SUCCESSFUL:
        print("❌ CRITICAL: Import failures prevent validation")
        for error in import_errors:
            print(f"   Error: {error}")
        return
    
    validator = AdvancedStrategiesValidator()
    results = validator.run_comprehensive_validation()
    
    # Print summary
    validator.print_summary(results)
    
    # Save results
    validator.save_results(results)

class AdvancedStrategiesValidator:
    """Comprehensive validator for advanced tuning strategies"""
    
    def __init__(self):
        self.test_scenarios = self._create_test_scenarios()
        self.validation_results = {}
        
    def _create_test_scenarios(self) -> List[Dict[str, Any]]:
        """Create comprehensive test scenarios"""
        
        scenarios = [
            {
                'name': 'Single Loop Temperature Control',
                'description': 'Simple temperature control with MPC constraints',
                'data': {
                    'process_gain': 2.0,
                    'time_constant': 15.0,
                    'dead_time': 2.0,
                    'setpoint': 80.0,
                    'output_min': 0.0,
                    'output_max': 100.0,
                    'input_min': 0.0,
                    'input_max': 100.0,
                    'economic_coefficient': 1.5,
                    'constraints': True
                }
            },
            {
                'name': 'Time-Varying Flow Process',
                'description': 'Flow control with time-varying parameters',
                'data': {
                    'process_gain': 1.5,
                    'time_constant': 8.0,
                    'dead_time': 1.0,
                    'setpoint': 50.0,
                    'time_varying': True,
                    'parameter_drift': 0.1,
                    'process_data': {
                        'input': [0.5, 0.6, 0.7, 0.8, 0.9] * 20,
                        'output': [48, 49, 51, 52, 50] * 20,
                        'error': [2, 1, -1, -2, 0] * 20
                    }
                }
            },
            {
                'name': 'Nonlinear Level Control',
                'description': 'Level control with gain scheduling',
                'data': {
                    'process_gain': 1.0,
                    'time_constant': 12.0,
                    'dead_time': 1.5,
                    'setpoint_range': [20, 80],
                    'num_operating_points': 5,
                    'operating_points': [
                        {
                            'variables': {'setpoint': 20},
                            'parameters': {'Kp': 0.8, 'Ti': 12.0, 'Td': 1.5}
                        },
                        {
                            'variables': {'setpoint': 50},
                            'parameters': {'Kp': 1.2, 'Ti': 10.0, 'Td': 1.2}
                        },
                        {
                            'variables': {'setpoint': 80},
                            'parameters': {'Kp': 1.8, 'Ti': 8.0, 'Td': 1.0}
                        }
                    ]
                }
            },
            {
                'name': 'Multi-Loop Interacting System',
                'description': '2x2 interacting control system',
                'data': {
                    'control_loops': [
                        {
                            'loop_id': 'temp_loop',
                            'name': 'Temperature Control',
                            'process_gain': 2.0,
                            'time_constant': 15.0,
                            'dead_time': 2.0,
                            'setpoint': 80.0,
                            'kp': 1.0,
                            'ti': 15.0,
                            'td': 2.0
                        },
                        {
                            'loop_id': 'flow_loop',
                            'name': 'Flow Control',
                            'process_gain': 1.5,
                            'time_constant': 8.0,
                            'dead_time': 1.0,
                            'setpoint': 50.0,
                            'kp': 1.2,
                            'ti': 8.0,
                            'td': 1.0
                        }
                    ],
                    'interactions': [
                        {
                            'from_loop': 'temp_loop',
                            'to_loop': 'flow_loop',
                            'interaction_gain': 0.3,
                            'bidirectional': True
                        },
                        {
                            'from_loop': 'flow_loop',
                            'to_loop': 'temp_loop',
                            'interaction_gain': 0.2,
                            'bidirectional': True
                        }
                    ]
                }
            },
            {
                'name': 'Economic Optimization Process',
                'description': 'Economic MPC with cost optimization',
                'data': {
                    'process_gain': 1.8,
                    'time_constant': 10.0,
                    'dead_time': 1.5,
                    'setpoint': 60.0,
                    'economic_coefficient': 2.0,
                    'operating_cost_weight': 0.7,
                    'constraints': {
                        'output_min': 10.0,
                        'output_max': 90.0,
                        'input_min': 0.0,
                        'input_max': 100.0
                    },
                    'economic_optimization': True
                }
            }
        ]
        
        return scenarios
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all advanced strategies"""
        
        print("🔧 Starting Advanced Tuning Strategies Validation")
        print("-" * 60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'strategy_results': {},
            'performance_summary': {},
            'validation_score': 0.0,
            'status': 'unknown'
        }
        
        # Test individual strategies
        strategies_to_test = [
            ('MPC Tuning', MPCTuner),
            ('Economic MPC', EconomicMPCTuner),
            ('Robust MPC', RobustMPCTuner),
            ('Hybrid MPC', HybridMPCTuner),
            ('Adaptive Controller', AdaptiveController),
            ('RLS Adaptive', RLSAdaptiveController),
            ('Gradient Descent Adaptive', GradientDescentController),
            ('Gain Scheduler', GainScheduler),
            ('Linear Gain Scheduler', LinearGainScheduler),
            ('Fuzzy Gain Scheduler', FuzzyGainScheduler),
            ('Multi-Loop Coordinator', MultiLoopCoordinator),
            ('Decentralized Coordinator', DecentralizedCoordinator),
            ('Centralized Coordinator', CentralizedCoordinator),
            ('Advanced Tuning Manager', AdvancedTuningManager)
        ]
        
        for strategy_name, strategy_class in strategies_to_test:
            print(f"🎯 Testing {strategy_name}")
            print("-" * 50)
            
            strategy_results = self._test_strategy(strategy_name, strategy_class)
            results['strategy_results'][strategy_name] = strategy_results
            
            # Update overall counts
            results['total_tests'] += strategy_results['total_tests']
            results['passed_tests'] += strategy_results['passed_tests']
            results['failed_tests'] += strategy_results['failed_tests']
            
            print(f"  📊 {strategy_name} Summary: {strategy_results['passed_tests']}/{strategy_results['total_tests']} passed ({strategy_results['success_rate']:.1f}%)")
            print()
        
        # Calculate final metrics
        results['validation_score'] = (results['passed_tests'] / max(results['total_tests'], 1)) * 100
        results['status'] = self._determine_status(results['validation_score'])
        
        # Performance summary
        results['performance_summary'] = self._create_performance_summary(results)
        
        return results
    
    def _test_strategy(self, strategy_name: str, strategy_class) -> Dict[str, Any]:
        """Test a single strategy across all applicable scenarios"""
        
        strategy_results = {
            'strategy_name': strategy_name,
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'success_rate': 0.0,
            'average_execution_time': 0.0,
            'performance_metrics': {}
        }
        
        execution_times = []
        
        for scenario in self.test_scenarios:
            # Check if strategy is applicable to scenario
            if not self._is_strategy_applicable(strategy_name, scenario):
                continue
            
            strategy_results['total_tests'] += 1
            
            try:
                # Create strategy instance
                strategy = strategy_class()
                
                # Execute strategy
                start_time = time.time()
                result = strategy.execute(scenario['data'])
                execution_time = time.time() - start_time
                execution_times.append(execution_time)
                
                # Validate result
                is_valid, validation_details = self._validate_strategy_result(result, scenario)
                
                test_detail = {
                    'scenario': scenario['name'],
                    'success': is_valid,
                    'execution_time': execution_time,
                    'validation_details': validation_details,
                    'error': None
                }
                
                if is_valid:
                    strategy_results['passed_tests'] += 1
                    print(f"    ✅ {scenario['name']}: SUCCESS ({execution_time:.3f}s)")
                else:
                    strategy_results['failed_tests'] += 1
                    print(f"    ❌ {scenario['name']}: FAILED - {validation_details.get('reason', 'Unknown')}")
                
                strategy_results['test_details'].append(test_detail)
                
            except Exception as e:
                strategy_results['failed_tests'] += 1
                error_msg = str(e)
                
                test_detail = {
                    'scenario': scenario['name'],
                    'success': False,
                    'execution_time': 0.0,
                    'validation_details': {'reason': 'Exception occurred'},
                    'error': error_msg
                }
                
                strategy_results['test_details'].append(test_detail)
                print(f"    ❌ {scenario['name']}: EXCEPTION - {error_msg}")
        
        # Calculate metrics
        if strategy_results['total_tests'] > 0:
            strategy_results['success_rate'] = (strategy_results['passed_tests'] / strategy_results['total_tests']) * 100
        
        if execution_times:
            strategy_results['average_execution_time'] = sum(execution_times) / len(execution_times)
        
        return strategy_results
    
    def _is_strategy_applicable(self, strategy_name: str, scenario: Dict[str, Any]) -> bool:
        """Check if strategy is applicable to scenario"""
        
        scenario_data = scenario['data']
        
        # MPC strategies - applicable to constrained problems
        if 'MPC' in strategy_name:
            return 'constraints' in scenario_data or any(key in scenario_data for key in ['output_min', 'output_max', 'input_min', 'input_max'])
        
        # Adaptive strategies - applicable to time-varying problems
        if 'Adaptive' in strategy_name:
            return 'time_varying' in scenario_data or 'process_data' in scenario_data
        
        # Gain scheduling - applicable to nonlinear problems
        if 'Gain' in strategy_name:
            return 'operating_points' in scenario_data or 'setpoint_range' in scenario_data
        
        # Multi-loop strategies - applicable to multi-loop problems
        if 'Multi' in strategy_name or 'Coordinator' in strategy_name:
            return 'control_loops' in scenario_data and len(scenario_data.get('control_loops', [])) > 1
        
        # Advanced manager - applicable to all scenarios
        if 'Manager' in strategy_name:
            return True
        
        return True  # Default to applicable
    
    def _validate_strategy_result(self, result: Dict[str, Any], scenario: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Validate strategy execution result"""
        
        validation_details = {}
        
        # Check basic result structure
        if not isinstance(result, dict):
            return False, {'reason': 'Result is not a dictionary'}
        
        if not result.get('success', False):
            return False, {'reason': f"Strategy failed: {result.get('error', 'Unknown error')}"}
        
        strategy_result = result.get('result')
        if not strategy_result:
            return False, {'reason': 'No strategy result returned'}
        
        # Check for required attributes
        required_checks = []
        
        # Check execution time
        if hasattr(strategy_result, 'execution_time'):
            exec_time = strategy_result.execution_time
            if exec_time > 60.0:  # More than 1 minute
                required_checks.append(f"Long execution time: {exec_time:.2f}s")
        
        # Check for parameters (if applicable)
        parameter_found = False
        parameter_locations = ['parameters', 'final_parameters', 'optimized_parameters']
        
        for location in parameter_locations:
            if hasattr(strategy_result, location):
                params = getattr(strategy_result, location)
                if params:
                    parameter_found = True
                    # Validate parameter reasonableness
                    param_validation = self._validate_parameters(params)
                    if not param_validation['valid']:
                        required_checks.append(f"Invalid parameters: {param_validation['reason']}")
                    break
        
        if not parameter_found:
            required_checks.append("No parameters found in result")
        
        # Check for performance metrics
        if hasattr(strategy_result, 'performance_metrics'):
            metrics = strategy_result.performance_metrics
            if not isinstance(metrics, dict) or not metrics:
                required_checks.append("No performance metrics available")
        
        # Determine overall validity
        is_valid = len(required_checks) == 0
        validation_details = {
            'checks_performed': len(required_checks) + 3,  # Basic checks
            'issues_found': required_checks,
            'parameter_found': parameter_found,
            'has_performance_metrics': hasattr(strategy_result, 'performance_metrics')
        }
        
        if not is_valid:
            validation_details['reason'] = '; '.join(required_checks)
        
        return is_valid, validation_details
    
    def _validate_parameters(self, params: Any) -> Dict[str, Any]:
        """Validate PID parameters"""
        
        # Handle different parameter structures
        if hasattr(params, '__dict__'):
            param_dict = params.__dict__
        elif isinstance(params, dict):
            param_dict = params
        else:
            return {'valid': False, 'reason': 'Parameters not in recognizable format'}
        
        # For multi-loop parameters, check first loop
        if all(isinstance(v, dict) for v in param_dict.values()):
            # Multi-loop case
            first_loop = list(param_dict.values())[0]
            param_dict = first_loop
        
        # Check individual parameters
        issues = []
        
        # Check Kp
        kp = param_dict.get('Kp', param_dict.get('kp'))
        if kp is not None:
            if not (0.001 <= kp <= 100.0):
                issues.append(f"Kp out of range: {kp}")
        
        # Check Ti
        ti = param_dict.get('Ti', param_dict.get('ti'))
        if ti is not None:
            if not (0.01 <= ti <= 1000.0):
                issues.append(f"Ti out of range: {ti}")
        
        # Check Td
        td = param_dict.get('Td', param_dict.get('td'))
        if td is not None:
            if not (0.0 <= td <= 100.0):
                issues.append(f"Td out of range: {td}")
        
        is_valid = len(issues) == 0
        
        return {
            'valid': is_valid,
            'reason': '; '.join(issues) if issues else 'Parameters valid',
            'parameters_found': [k for k in param_dict.keys() if k.lower() in ['kp', 'ti', 'td']]
        }
    
    def _determine_status(self, validation_score: float) -> str:
        """Determine overall validation status"""
        
        if validation_score >= 90.0:
            return "EXCELLENT"
        elif validation_score >= 80.0:
            return "VERY GOOD"
        elif validation_score >= 70.0:
            return "GOOD"
        elif validation_score >= 60.0:
            return "ACCEPTABLE"
        else:
            return "NEEDS IMPROVEMENT"
    
    def _create_performance_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create performance summary"""
        
        strategy_performances = []
        total_execution_time = 0.0
        
        for strategy_name, strategy_result in results['strategy_results'].items():
            strategy_performances.append({
                'strategy': strategy_name,
                'success_rate': strategy_result['success_rate'],
                'avg_execution_time': strategy_result['average_execution_time'],
                'tests_passed': strategy_result['passed_tests'],
                'total_tests': strategy_result['total_tests']
            })
            total_execution_time += strategy_result['average_execution_time']
        
        # Sort by success rate
        strategy_performances.sort(key=lambda x: x['success_rate'], reverse=True)
        
        return {
            'best_performing_strategies': strategy_performances[:3],
            'total_execution_time': total_execution_time,
            'average_strategy_success_rate': sum(s['success_rate'] for s in strategy_performances) / max(len(strategy_performances), 1),
            'strategies_tested': len(strategy_performances),
            'scenarios_tested': len(self.test_scenarios)
        }
    
    def print_summary(self, results: Dict[str, Any]):
        """Print validation summary"""
        
        print("=" * 80)
        print("🏁 PHASE 22.2.3 ADVANCED TUNING STRATEGIES - PRODUCTION VALIDATION")
        print("=" * 80)
        print()
        
        print("📊 OVERALL RESULTS:")
        print(f"   Total Tests: {results['total_tests']}")
        print(f"   Passed: {results['passed_tests']} ✅")
        print(f"   Failed: {results['failed_tests']} ❌")
        print(f"   Success Rate: {results['passed_tests']/max(results['total_tests'], 1)*100:.1f}%")
        print(f"   Validation Score: {results['validation_score']:.1f} ({results['status']})")
        print(f"   Overall Status: {'✅' if results['validation_score'] >= 70 else '⚠️' if results['validation_score'] >= 50 else '❌'} {results['status']}")
        print()
        
        print("📋 STRATEGY RESULTS:")
        for strategy_name, strategy_result in results['strategy_results'].items():
            status_icon = "✅" if strategy_result['success_rate'] >= 70 else "⚠️" if strategy_result['success_rate'] >= 50 else "❌"
            print(f"   {status_icon} {strategy_name}:")
            print(f"      Success Rate: {strategy_result['success_rate']:.1f}% ({strategy_result['passed_tests']}/{strategy_result['total_tests']})")
            print(f"      Avg Execution Time: {strategy_result['average_execution_time']:.3f}s")
        print()
        
        # Performance analysis
        perf_summary = results['performance_summary']
        print("📈 PERFORMANCE ANALYSIS:")
        print(f"   Total Execution Time: {perf_summary['total_execution_time']:.3f}s")
        print(f"   Average Strategy Success Rate: {perf_summary['average_strategy_success_rate']:.1f}%")
        print(f"   Strategies Tested: {perf_summary['strategies_tested']}")
        print(f"   Scenarios Tested: {perf_summary['scenarios_tested']}")
        print()
        
        print("🏆 TOP PERFORMING STRATEGIES:")
        for i, strategy in enumerate(perf_summary['best_performing_strategies'][:3], 1):
            print(f"   {i}. {strategy['strategy']}: {strategy['success_rate']:.1f}% ({strategy['tests_passed']}/{strategy['total_tests']})")
        print()
        
        print("💡 RECOMMENDATIONS:")
        if results['validation_score'] >= 80:
            print("   ✅ Advanced tuning strategies are working excellent")
            print("   ✅ Ready for production deployment")
            print("   ✅ Can proceed to next phase")
        elif results['validation_score'] >= 60:
            print("   ⚠️ Advanced tuning strategies are working well")
            print("   ⚠️ Minor improvements recommended for production")
            print("   ✅ Can proceed with monitoring")
        else:
            print("   ❌ Advanced tuning strategies need improvement")
            print("   ❌ Review failed tests before production deployment")
        print()
        
        print("🎯 PHASE 22.2.3 COMPLETION STATUS:")
        if results['validation_score'] >= 70:
            print("   ✅ PHASE 22.2.3 SUCCESSFULLY COMPLETED")
            print("   ✅ Advanced Tuning Strategies production validated")
            print("   ✅ Ready for Phase 22.3: Performance Analysis Suite")
        else:
            print("   ⚠️ PHASE 22.2.3 NEEDS ATTENTION")
            print("   ⚠️ Some strategies require debugging")
        print("=" * 80)
    
    def save_results(self, results: Dict[str, Any]):
        """Save validation results to file"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"advanced_strategies_validation_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"📁 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️ Failed to save results: {e}")

if __name__ == "__main__":
    main() 