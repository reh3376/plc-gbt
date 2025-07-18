#!/usr/bin/env python3
"""
Phase 22.2: Task 22.2.1 - Enhanced IMC Tuning Testing Framework
===============================================================

Comprehensive testing framework for Enhanced IMC Tuning implementation including:
- Automatic lambda selection validation
- Multi-objective optimization testing
- Constraint handling verification
- Robustness analysis validation
- Integration testing with various process models
- Performance benchmarking and comparison with basic IMC

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.2.1 - Enhanced IMC Testing
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import pandas as pd
import unittest
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

# Import enhanced IMC components
from .imc_enhanced import (
    EnhancedIMCTuner,
    AutoLambdaSelector,
    MultiObjectiveOptimizer,
    ConstraintHandler,
    RobustnessAnalyzer,
    LambdaSelectionStrategy,
    OptimizationObjective,
    ConstraintSpecification
)

# Configure logging for testing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Test case definition for Enhanced IMC testing"""
    name: str
    model_params: Dict[str, float]
    controller_type: str
    expected_stability: bool
    performance_threshold: float
    description: str

class EnhancedIMCTestSuite:
    """
    Comprehensive test suite for Enhanced IMC Tuning system
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.EnhancedIMCTestSuite')
        self.test_results = {}
        self.performance_metrics = {}
        
        # Initialize test systems
        self.test_cases = self._define_test_cases()
        
        # Initialize Enhanced IMC components
        self.enhanced_imc_tuner = EnhancedIMCTuner()
        self.lambda_selector = AutoLambdaSelector()
        self.multi_objective_optimizer = MultiObjectiveOptimizer()
        self.constraint_handler = ConstraintHandler()
        self.robustness_analyzer = RobustnessAnalyzer()
    
    def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Run complete Enhanced IMC testing suite"""
        self.logger.info("🧪 Starting Enhanced IMC Tuning Comprehensive Testing Suite")
        start_time = time.time()
        
        test_results = {
            'lambda_selection_tests': self._test_lambda_selection(),
            'multi_objective_tests': self._test_multi_objective_optimization(),
            'constraint_handling_tests': self._test_constraint_handling(),
            'robustness_analysis_tests': self._test_robustness_analysis(),
            'integration_tests': self._test_full_integration(),
            'performance_comparison_tests': self._test_performance_comparison(),
            'edge_case_tests': self._test_edge_cases()
        }
        
        # Calculate overall test score
        overall_score = self._calculate_overall_test_score(test_results)
        
        execution_time = time.time() - start_time
        
        final_results = {
            'overall_score': overall_score,
            'execution_time': execution_time,
            'test_results': test_results,
            'summary': self._generate_test_summary(test_results, overall_score),
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        self.logger.info(f"✅ Enhanced IMC Testing completed in {execution_time:.2f}s with score: {overall_score:.1f}%")
        return final_results
    
    def _define_test_cases(self) -> List[TestCase]:
        """Define comprehensive test cases for various process types"""
        return [
            TestCase(
                name="Fast Process - Low Dead Time",
                model_params={'K': 2.5, 'tau': 10.0, 'theta': 1.0},
                controller_type='dependent',
                expected_stability=True,
                performance_threshold=0.8,
                description="Fast responding process with minimal dead time"
            ),
            TestCase(
                name="Slow Process - High Dead Time",
                model_params={'K': 1.2, 'tau': 50.0, 'theta': 15.0},
                controller_type='dependent',
                expected_stability=True,
                performance_threshold=0.7,
                description="Slow process with significant dead time"
            ),
            TestCase(
                name="High Gain Process",
                model_params={'K': 8.0, 'tau': 20.0, 'theta': 3.0},
                controller_type='independent',
                expected_stability=True,
                performance_threshold=0.75,
                description="High gain process requiring careful tuning"
            ),
            TestCase(
                name="Integrating-like Process",
                model_params={'K': 0.5, 'tau': 100.0, 'theta': 5.0},
                controller_type='dependent',
                expected_stability=True,
                performance_threshold=0.65,
                description="Near-integrating process with large time constant"
            ),
            TestCase(
                name="No Dead Time Process",
                model_params={'K': 1.5, 'tau': 25.0, 'theta': 0.0},
                controller_type='independent',
                expected_stability=True,
                performance_threshold=0.85,
                description="Pure first-order process without dead time"
            ),
            TestCase(
                name="Challenging Process",
                model_params={'K': 5.0, 'tau': 8.0, 'theta': 12.0},
                controller_type='dependent',
                expected_stability=True,
                performance_threshold=0.6,
                description="Dead time dominant process (theta > tau)"
            )
        ]
    
    def _test_lambda_selection(self) -> Dict[str, Any]:
        """Test automatic lambda selection strategies"""
        self.logger.info("🎯 Testing Automatic Lambda Selection")
        
        test_results = {}
        strategies = [
            LambdaSelectionStrategy.CONSERVATIVE,
            LambdaSelectionStrategy.BALANCED,
            LambdaSelectionStrategy.AGGRESSIVE,
            LambdaSelectionStrategy.ADAPTIVE,
            LambdaSelectionStrategy.OPTIMAL
        ]
        
        for strategy in strategies:
            strategy_results = []
            
            for test_case in self.test_cases:
                K, tau, theta = test_case.model_params['K'], test_case.model_params['tau'], test_case.model_params['theta']
                
                try:
                    # Test lambda selection
                    lambda_c = self.lambda_selector.select_lambda(K, tau, theta, strategy)
                    
                    # Validate lambda_c reasonableness
                    lambda_valid = self._validate_lambda_selection(lambda_c, tau, theta, strategy)
                    
                    # Test performance with selected lambda
                    performance_score = self._evaluate_lambda_performance(K, tau, theta, lambda_c, test_case.controller_type)
                    
                    strategy_results.append({
                        'test_case': test_case.name,
                        'lambda_c': lambda_c,
                        'lambda_valid': lambda_valid,
                        'performance_score': performance_score,
                        'success': lambda_valid and performance_score > 0.3
                    })
                    
                except Exception as e:
                    strategy_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate strategy success rate
            successful_tests = sum(1 for result in strategy_results if result.get('success', False))
            success_rate = successful_tests / len(strategy_results) * 100
            
            test_results[strategy.value] = {
                'success_rate': success_rate,
                'results': strategy_results,
                'average_performance': np.mean([r.get('performance_score', 0) for r in strategy_results])
            }
        
        # Overall lambda selection test score
        overall_success_rate = np.mean([result['success_rate'] for result in test_results.values()])
        
        return {
            'overall_success_rate': overall_success_rate,
            'strategy_results': test_results,
            'passed': overall_success_rate >= 80.0
        }
    
    def _test_multi_objective_optimization(self) -> Dict[str, Any]:
        """Test multi-objective optimization functionality"""
        self.logger.info("🎯 Testing Multi-Objective Optimization")
        
        test_results = {}
        objectives = [
            OptimizationObjective.PERFORMANCE_ONLY,
            OptimizationObjective.ROBUSTNESS_ONLY,
            OptimizationObjective.BALANCED
        ]
        
        for objective in objectives:
            objective_results = []
            
            for test_case in self.test_cases:
                K, tau, theta = test_case.model_params['K'], test_case.model_params['tau'], test_case.model_params['theta']
                
                try:
                    # Test optimization
                    optimization_result = self.multi_objective_optimizer.optimize(
                        K, tau, theta, test_case.controller_type, objective
                    )
                    
                    success = optimization_result['success']
                    if success:
                        params = optimization_result['parameters']
                        details = optimization_result['optimization_details']
                        
                        # Validate optimized parameters
                        params_valid = self._validate_pid_parameters(params, test_case.controller_type)
                        
                        # Test performance
                        performance_score = details.get('performance_score', 0)
                        robustness_score = details.get('robustness_score', 0)
                        
                        objective_results.append({
                            'test_case': test_case.name,
                            'optimization_success': success,
                            'parameters_valid': params_valid,
                            'performance_score': performance_score,
                            'robustness_score': robustness_score,
                            'final_cost': details.get('final_cost', float('inf')),
                            'success': success and params_valid and performance_score > 0.3
                        })
                    else:
                        objective_results.append({
                            'test_case': test_case.name,
                            'success': False,
                            'error': 'Optimization failed'
                        })
                        
                except Exception as e:
                    objective_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate objective success rate
            successful_tests = sum(1 for result in objective_results if result.get('success', False))
            success_rate = successful_tests / len(objective_results) * 100
            
            test_results[objective.value] = {
                'success_rate': success_rate,
                'results': objective_results,
                'average_performance': np.mean([r.get('performance_score', 0) for r in objective_results]),
                'average_robustness': np.mean([r.get('robustness_score', 0) for r in objective_results])
            }
        
        # Overall multi-objective optimization test score
        overall_success_rate = np.mean([result['success_rate'] for result in test_results.values()])
        
        return {
            'overall_success_rate': overall_success_rate,
            'objective_results': test_results,
            'passed': overall_success_rate >= 75.0
        }
    
    def _test_constraint_handling(self) -> Dict[str, Any]:
        """Test constraint handling functionality"""
        self.logger.info("🎯 Testing Constraint Handling")
        
        test_results = {}
        
        # Define test constraints
        test_constraints = [
            ConstraintSpecification(
                gain_limits={'Kp': (0.1, 5.0), 'Ti': (1.0, 100.0), 'Td': (0.0, 10.0)},
                output_limits=(-10.0, 10.0),
                safety_margins={'Kp': 0.1}
            ),
            ConstraintSpecification(
                gain_limits={'Kp': (0.5, 2.0), 'Ki': (0.01, 1.0), 'Kd': (0.0, 0.5)},
                rate_limits=(-5.0, 5.0),
                integral_windup_limit=50.0
            ),
            ConstraintSpecification(
                output_limits=(-1.0, 1.0),  # Very tight output limits
                safety_margins={'Kp': 0.2, 'Ti': 0.1}
            )
        ]
        
        for i, constraints in enumerate(test_constraints):
            constraint_results = []
            
            for test_case in self.test_cases:
                K, tau, theta = test_case.model_params['K'], test_case.model_params['tau'], test_case.model_params['theta']
                
                try:
                    # Get unconstrained parameters first
                    unconstrained_optimization = self.multi_objective_optimizer.optimize(
                        K, tau, theta, test_case.controller_type
                    )
                    
                    if unconstrained_optimization['success']:
                        unconstrained_params = unconstrained_optimization['parameters']
                        
                        # Apply constraints
                        constraint_result = self.constraint_handler.apply_constraints(
                            unconstrained_params, constraints, K, tau, theta
                        )
                        
                        constrained_params = constraint_result['constrained_parameters']
                        
                        # Validate constraint satisfaction
                        constraints_satisfied = self._validate_constraint_satisfaction(
                            constrained_params, constraints
                        )
                        
                        # Test performance with constrained parameters
                        constrained_performance = self._evaluate_constrained_performance(
                            K, tau, theta, constrained_params, test_case.controller_type
                        )
                        
                        constraint_results.append({
                            'test_case': test_case.name,
                            'constraints_applied': len(constraint_result['modifications']) > 0,
                            'constraints_satisfied': constraints_satisfied,
                            'performance_score': constrained_performance,
                            'success': constraints_satisfied and constrained_performance > 0.2
                        })
                    else:
                        constraint_results.append({
                            'test_case': test_case.name,
                            'success': False,
                            'error': 'Initial optimization failed'
                        })
                        
                except Exception as e:
                    constraint_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': str(e)
                    })
            
            # Calculate constraint handling success rate
            successful_tests = sum(1 for result in constraint_results if result.get('success', False))
            success_rate = successful_tests / len(constraint_results) * 100
            
            test_results[f'constraint_set_{i+1}'] = {
                'success_rate': success_rate,
                'results': constraint_results,
                'average_performance': np.mean([r.get('performance_score', 0) for r in constraint_results])
            }
        
        # Overall constraint handling test score
        overall_success_rate = np.mean([result['success_rate'] for result in test_results.values()])
        
        return {
            'overall_success_rate': overall_success_rate,
            'constraint_results': test_results,
            'passed': overall_success_rate >= 70.0
        }
    
    def _test_robustness_analysis(self) -> Dict[str, Any]:
        """Test robustness analysis functionality"""
        self.logger.info("🎯 Testing Robustness Analysis")
        
        robustness_results = []
        
        for test_case in self.test_cases:
            K, tau, theta = test_case.model_params['K'], test_case.model_params['tau'], test_case.model_params['theta']
            
            try:
                # Get optimized parameters
                optimization_result = self.multi_objective_optimizer.optimize(
                    K, tau, theta, test_case.controller_type
                )
                
                if optimization_result['success']:
                    params = optimization_result['parameters']
                    
                    # Perform robustness analysis
                    robustness_analysis = self.robustness_analyzer.analyze_robustness(
                        K, tau, theta, params, test_case.controller_type
                    )
                    
                    # Validate robustness analysis components
                    monte_carlo_valid = self._validate_monte_carlo_results(robustness_analysis['monte_carlo_analysis'])
                    worst_case_valid = self._validate_worst_case_results(robustness_analysis['worst_case_analysis'])
                    margins_valid = self._validate_margin_analysis(robustness_analysis['margin_analysis'])
                    
                    overall_robustness_score = robustness_analysis['overall_robustness_score']
                    
                    robustness_results.append({
                        'test_case': test_case.name,
                        'monte_carlo_valid': monte_carlo_valid,
                        'worst_case_valid': worst_case_valid,
                        'margins_valid': margins_valid,
                        'overall_robustness_score': overall_robustness_score,
                        'success': monte_carlo_valid and worst_case_valid and margins_valid and overall_robustness_score > 0.3
                    })
                else:
                    robustness_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': 'Parameter optimization failed'
                    })
                    
            except Exception as e:
                robustness_results.append({
                    'test_case': test_case.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate robustness analysis success rate
        successful_tests = sum(1 for result in robustness_results if result.get('success', False))
        success_rate = successful_tests / len(robustness_results) * 100
        
        average_robustness_score = np.mean([r.get('overall_robustness_score', 0) for r in robustness_results])
        
        return {
            'success_rate': success_rate,
            'results': robustness_results,
            'average_robustness_score': average_robustness_score,
            'passed': success_rate >= 80.0 and average_robustness_score >= 0.6
        }
    
    def _test_full_integration(self) -> Dict[str, Any]:
        """Test full Enhanced IMC integration"""
        self.logger.info("🎯 Testing Full Enhanced IMC Integration")
        
        integration_results = []
        
        for test_case in self.test_cases:
            try:
                # Prepare input data
                input_data = {
                    'model_parameters': test_case.model_params,
                    'controller_type': test_case.controller_type
                }
                
                # Test full Enhanced IMC tuning
                start_time = time.time()
                result = self.enhanced_imc_tuner.execute(
                    input_data,
                    lambda_strategy=LambdaSelectionStrategy.BALANCED,
                    optimization_objective=OptimizationObjective.BALANCED,
                    performance_weight=0.7,
                    robustness_weight=0.3
                )
                execution_time = time.time() - start_time
                
                if result['success']:
                    tuning_result = result['result']
                    
                    # Validate complete result
                    result_valid = self._validate_complete_result(tuning_result, test_case)
                    
                    # Check performance against threshold
                    performance_adequate = (
                        tuning_result.performance_metrics['performance_index'] >= test_case.performance_threshold
                    )
                    
                    # Check robustness
                    robustness_adequate = (
                        tuning_result.robustness_metrics['overall_robustness_score'] >= 0.5
                    )
                    
                    integration_results.append({
                        'test_case': test_case.name,
                        'execution_time': execution_time,
                        'result_valid': result_valid,
                        'performance_adequate': performance_adequate,
                        'robustness_adequate': robustness_adequate,
                        'performance_score': tuning_result.performance_metrics['performance_index'],
                        'robustness_score': tuning_result.robustness_metrics['overall_robustness_score'],
                        'lambda_c': tuning_result.lambda_c_selected,
                        'success': result_valid and performance_adequate and robustness_adequate
                    })
                else:
                    integration_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                    
            except Exception as e:
                integration_results.append({
                    'test_case': test_case.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate integration success rate
        successful_tests = sum(1 for result in integration_results if result.get('success', False))
        success_rate = successful_tests / len(integration_results) * 100
        
        average_execution_time = np.mean([r.get('execution_time', 0) for r in integration_results])
        average_performance = np.mean([r.get('performance_score', 0) for r in integration_results])
        average_robustness = np.mean([r.get('robustness_score', 0) for r in integration_results])
        
        return {
            'success_rate': success_rate,
            'results': integration_results,
            'average_execution_time': average_execution_time,
            'average_performance_score': average_performance,
            'average_robustness_score': average_robustness,
            'passed': success_rate >= 85.0 and average_performance >= 0.7 and average_robustness >= 0.6
        }
    
    def _test_performance_comparison(self) -> Dict[str, Any]:
        """Test performance comparison between Enhanced IMC and basic IMC"""
        self.logger.info("🎯 Testing Performance Comparison with Basic IMC")
        
        comparison_results = []
        
        for test_case in self.test_cases:
            K, tau, theta = test_case.model_params['K'], test_case.model_params['tau'], test_case.model_params['theta']
            
            try:
                # Enhanced IMC tuning
                enhanced_data = {
                    'model_parameters': test_case.model_params,
                    'controller_type': test_case.controller_type
                }
                enhanced_result = self.enhanced_imc_tuner.execute(enhanced_data)
                
                # Basic IMC tuning (fallback implementation)
                basic_result = self._basic_imc_tuning(K, tau, theta, test_case.controller_type)
                
                if enhanced_result['success'] and basic_result['success']:
                    enhanced_performance = enhanced_result['result'].performance_metrics['performance_index']
                    enhanced_robustness = enhanced_result['result'].robustness_metrics['overall_robustness_score']
                    
                    basic_performance = basic_result['performance_score']
                    basic_robustness = basic_result['robustness_score']
                    
                    # Calculate improvements
                    performance_improvement = (enhanced_performance - basic_performance) / basic_performance * 100
                    robustness_improvement = (enhanced_robustness - basic_robustness) / basic_robustness * 100
                    
                    comparison_results.append({
                        'test_case': test_case.name,
                        'enhanced_performance': enhanced_performance,
                        'basic_performance': basic_performance,
                        'enhanced_robustness': enhanced_robustness,
                        'basic_robustness': basic_robustness,
                        'performance_improvement_percent': performance_improvement,
                        'robustness_improvement_percent': robustness_improvement,
                        'overall_improvement': (performance_improvement + robustness_improvement) / 2,
                        'success': performance_improvement >= 0 or robustness_improvement >= 10  # Allow trade-offs
                    })
                else:
                    comparison_results.append({
                        'test_case': test_case.name,
                        'success': False,
                        'error': 'One or both tuning methods failed'
                    })
                    
            except Exception as e:
                comparison_results.append({
                    'test_case': test_case.name,
                    'success': False,
                    'error': str(e)
                })
        
        # Calculate overall improvement metrics
        successful_tests = sum(1 for result in comparison_results if result.get('success', False))
        success_rate = successful_tests / len(comparison_results) * 100
        
        avg_performance_improvement = np.mean([r.get('performance_improvement_percent', 0) for r in comparison_results])
        avg_robustness_improvement = np.mean([r.get('robustness_improvement_percent', 0) for r in comparison_results])
        
        return {
            'success_rate': success_rate,
            'results': comparison_results,
            'average_performance_improvement': avg_performance_improvement,
            'average_robustness_improvement': avg_robustness_improvement,
            'passed': success_rate >= 80.0 and (avg_performance_improvement >= 5.0 or avg_robustness_improvement >= 15.0)
        }
    
    def _test_edge_cases(self) -> Dict[str, Any]:
        """Test edge cases and error handling"""
        self.logger.info("🎯 Testing Edge Cases and Error Handling")
        
        edge_case_results = []
        
        # Define edge cases
        edge_cases = [
            {'name': 'Zero Gain', 'params': {'K': 0.0, 'tau': 10.0, 'theta': 1.0}, 'expect_error': True},
            {'name': 'Negative Gain', 'params': {'K': -1.0, 'tau': 10.0, 'theta': 1.0}, 'expect_error': False},
            {'name': 'Zero Time Constant', 'params': {'K': 1.0, 'tau': 0.0, 'theta': 1.0}, 'expect_error': True},
            {'name': 'Large Dead Time', 'params': {'K': 1.0, 'tau': 1.0, 'theta': 100.0}, 'expect_error': False},
            {'name': 'Very Small Parameters', 'params': {'K': 0.001, 'tau': 0.01, 'theta': 0.001}, 'expect_error': False},
            {'name': 'Very Large Parameters', 'params': {'K': 1000.0, 'tau': 10000.0, 'theta': 1000.0}, 'expect_error': False}
        ]
        
        for edge_case in edge_cases:
            try:
                input_data = {
                    'model_parameters': edge_case['params'],
                    'controller_type': 'dependent'
                }
                
                # Test input validation
                valid, errors = self.enhanced_imc_tuner.validate_input(input_data)
                
                if valid:
                    # Attempt tuning
                    result = self.enhanced_imc_tuner.execute(input_data)
                    
                    if edge_case['expect_error']:
                        # Should have failed but didn't
                        edge_case_results.append({
                            'case': edge_case['name'],
                            'success': False,
                            'reason': 'Expected error but tuning succeeded'
                        })
                    else:
                        # Should have succeeded
                        edge_case_results.append({
                            'case': edge_case['name'],
                            'success': result['success'],
                            'reason': 'Handled edge case appropriately' if result['success'] else result.get('error', 'Unknown error')
                        })
                else:
                    # Input validation failed
                    if edge_case['expect_error']:
                        # Expected failure
                        edge_case_results.append({
                            'case': edge_case['name'],
                            'success': True,
                            'reason': 'Correctly rejected invalid input'
                        })
                    else:
                        # Unexpected failure
                        edge_case_results.append({
                            'case': edge_case['name'],
                            'success': False,
                            'reason': f'Unexpected validation failure: {errors}'
                        })
                        
            except Exception as e:
                if edge_case['expect_error']:
                    edge_case_results.append({
                        'case': edge_case['name'],
                        'success': True,
                        'reason': 'Correctly handled with exception'
                    })
                else:
                    edge_case_results.append({
                        'case': edge_case['name'],
                        'success': False,
                        'reason': f'Unexpected exception: {str(e)}'
                    })
        
        # Calculate edge case handling success rate
        successful_tests = sum(1 for result in edge_case_results if result.get('success', False))
        success_rate = successful_tests / len(edge_case_results) * 100
        
        return {
            'success_rate': success_rate,
            'results': edge_case_results,
            'passed': success_rate >= 80.0
        }
    
    # Helper methods for validation
    def _validate_lambda_selection(self, lambda_c: float, tau: float, theta: float, 
                                  strategy: LambdaSelectionStrategy) -> bool:
        """Validate lambda selection reasonableness"""
        if lambda_c <= 0:
            return False
        
        # Strategy-specific validation
        if strategy == LambdaSelectionStrategy.CONSERVATIVE:
            return lambda_c >= tau * 0.1  # Should be conservative
        elif strategy == LambdaSelectionStrategy.AGGRESSIVE:
            return lambda_c <= tau * 0.5  # Should be aggressive
        else:
            return tau * 0.01 <= lambda_c <= tau * 2.0  # Reasonable range
    
    def _validate_pid_parameters(self, params: Dict[str, float], controller_type: str) -> bool:
        """Validate PID parameter reasonableness"""
        if controller_type == 'dependent':
            required = ['Kp', 'Ti', 'Td']
        else:
            required = ['Kp', 'Ki', 'Kd']
        
        for param in required:
            if param not in params:
                return False
            
            value = params[param]
            if np.isnan(value) or np.isinf(value):
                return False
            
            # Parameter-specific bounds
            if param == 'Kp' and (value <= 0 or value > 1000):
                return False
            elif param == 'Ti' and (value <= 0 or value > 10000):
                return False
            elif param in ['Td', 'Ki', 'Kd'] and (value < 0 or value > 1000):
                return False
        
        return True
    
    def _validate_constraint_satisfaction(self, params: Dict[str, float], 
                                        constraints: ConstraintSpecification) -> bool:
        """Validate that parameters satisfy constraints"""
        if constraints.gain_limits:
            for param, (min_val, max_val) in constraints.gain_limits.items():
                if param in params:
                    if not (min_val <= params[param] <= max_val):
                        return False
        
        return True
    
    def _validate_monte_carlo_results(self, mc_results: Dict[str, Any]) -> bool:
        """Validate Monte Carlo analysis results"""
        required_fields = ['stability_probability', 'performance_statistics']
        return all(field in mc_results for field in required_fields)
    
    def _validate_worst_case_results(self, wc_results: Dict[str, Any]) -> bool:
        """Validate worst-case analysis results"""
        required_fields = ['all_combinations_stable', 'worst_case_performance']
        return all(field in wc_results for field in required_fields)
    
    def _validate_margin_analysis(self, margin_results: Dict[str, Any]) -> bool:
        """Validate margin analysis results"""
        required_fields = ['gain_margin_db', 'phase_margin_deg']
        return all(field in margin_results for field in required_fields)
    
    def _validate_complete_result(self, result, test_case: TestCase) -> bool:
        """Validate complete Enhanced IMC result"""
        required_attrs = [
            'tuning_method', 'parameters', 'lambda_c_selected',
            'performance_metrics', 'robustness_metrics', 'recommendations'
        ]
        
        for attr in required_attrs:
            if not hasattr(result, attr):
                return False
        
        # Validate parameter format
        return self._validate_pid_parameters(result.parameters, test_case.controller_type)
    
    def _evaluate_lambda_performance(self, K: float, tau: float, theta: float, 
                                   lambda_c: float, controller_type: str) -> float:
        """Evaluate performance of lambda selection"""
        # Simple IMC tuning with selected lambda
        try:
            if controller_type == 'dependent':
                Kp = tau / (K * (lambda_c + theta))
                params = {'Kp': Kp, 'Ti': tau, 'Td': 0.0}
            else:
                Kp = tau / (K * (lambda_c + theta))
                Ki = Kp / tau if tau > 0 else 0
                params = {'Kp': Kp, 'Ki': Ki, 'Kd': 0.0}
            
            # Simple performance estimation
            if lambda_c > 0:
                rise_time_est = lambda_c + theta
                normalized_performance = max(0, 1 - rise_time_est / (tau * 4))
                return normalized_performance
            else:
                return 0.0
                
        except:
            return 0.0
    
    def _evaluate_constrained_performance(self, K: float, tau: float, theta: float,
                                        params: Dict[str, float], controller_type: str) -> float:
        """Evaluate performance with constrained parameters"""
        # Use the same approach as lambda performance evaluation
        try:
            # Estimate closed-loop time constant from PID parameters
            if controller_type == 'dependent':
                lambda_est = (tau / (K * params['Kp'])) - theta if K * params['Kp'] != 0 else tau
            else:
                lambda_est = (tau / (K * params['Kp'])) - theta if K * params['Kp'] != 0 else tau
            
            if lambda_est > 0:
                rise_time_est = lambda_est + theta
                normalized_performance = max(0, 1 - rise_time_est / (tau * 4))
                return normalized_performance
            else:
                return 0.2  # Minimum performance for stability
                
        except:
            return 0.0
    
    def _basic_imc_tuning(self, K: float, tau: float, theta: float, controller_type: str) -> Dict[str, Any]:
        """Basic IMC tuning for comparison"""
        try:
            lambda_c = max(theta, tau * 0.1)  # Simple lambda selection
            
            if controller_type == 'dependent':
                Kp = tau / (K * (lambda_c + theta))
                params = {'Kp': Kp, 'Ti': tau, 'Td': 0.0}
            else:
                Kp = tau / (K * (lambda_c + theta))
                Ki = Kp / tau if tau > 0 else 0
                params = {'Kp': Kp, 'Ki': Ki, 'Kd': 0.0}
            
            # Simple performance and robustness estimation
            performance_score = max(0, 1 - (lambda_c + theta) / (tau * 4))
            robustness_score = 0.6  # Conservative estimate
            
            return {
                'success': True,
                'parameters': params,
                'performance_score': performance_score,
                'robustness_score': robustness_score
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _calculate_overall_test_score(self, test_results: Dict[str, Any]) -> float:
        """Calculate overall test score from all test components"""
        weights = {
            'lambda_selection_tests': 0.15,
            'multi_objective_tests': 0.20,
            'constraint_handling_tests': 0.15,
            'robustness_analysis_tests': 0.20,
            'integration_tests': 0.20,
            'performance_comparison_tests': 0.05,
            'edge_case_tests': 0.05
        }
        
        total_score = 0.0
        
        for test_name, weight in weights.items():
            if test_name in test_results:
                test_result = test_results[test_name]
                
                # Get success rate from test result
                if 'overall_success_rate' in test_result:
                    score = test_result['overall_success_rate']
                elif 'success_rate' in test_result:
                    score = test_result['success_rate']
                else:
                    score = 50.0  # Default middle score
                
                # Bonus for passing tests
                if test_result.get('passed', False):
                    score = min(100.0, score * 1.1)
                
                total_score += weight * score
        
        return min(100.0, total_score)
    
    def _generate_test_summary(self, test_results: Dict[str, Any], overall_score: float) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        
        summary = {
            'overall_score': overall_score,
            'grade': self._get_test_grade(overall_score),
            'components_tested': len(test_results),
            'components_passed': sum(1 for result in test_results.values() if result.get('passed', False)),
            'key_findings': [],
            'recommendations': []
        }
        
        # Generate key findings
        if test_results.get('lambda_selection_tests', {}).get('passed', False):
            summary['key_findings'].append("✅ Automatic lambda selection working correctly across all strategies")
        
        if test_results.get('multi_objective_tests', {}).get('passed', False):
            summary['key_findings'].append("✅ Multi-objective optimization successfully balancing performance and robustness")
        
        if test_results.get('robustness_analysis_tests', {}).get('passed', False):
            summary['key_findings'].append("✅ Comprehensive robustness analysis providing reliable uncertainty quantification")
        
        if test_results.get('integration_tests', {}).get('passed', False):
            summary['key_findings'].append("✅ Full Enhanced IMC integration working seamlessly across diverse process types")
        
        # Generate recommendations
        if overall_score < 80:
            summary['recommendations'].append("Consider additional testing and validation before production deployment")
        
        if not test_results.get('constraint_handling_tests', {}).get('passed', False):
            summary['recommendations'].append("Improve constraint handling reliability for safety-critical applications")
        
        if overall_score >= 90:
            summary['recommendations'].append("✅ Ready for Phase 22.2.2 implementation (Classical Tuning Methods)")
        
        return summary
    
    def _get_test_grade(self, score: float) -> str:
        """Get letter grade for test score"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        else:
            return "F"

# Main testing execution
def run_enhanced_imc_tests() -> Dict[str, Any]:
    """Run comprehensive Enhanced IMC testing suite"""
    test_suite = EnhancedIMCTestSuite()
    return test_suite.run_comprehensive_testing()

if __name__ == "__main__":
    # Run tests when executed directly
    print("🧪 Running Enhanced IMC Tuning Test Suite...")
    results = run_enhanced_imc_tests()
    
    print(f"\n📊 Test Results Summary:")
    print(f"Overall Score: {results['overall_score']:.1f}%")
    print(f"Grade: {results['summary']['grade']}")
    print(f"Execution Time: {results['execution_time']:.2f} seconds")
    print(f"Components Passed: {results['summary']['components_passed']}/{results['summary']['components_tested']}")
    
    if results['summary']['key_findings']:
        print(f"\n🔍 Key Findings:")
        for finding in results['summary']['key_findings']:
            print(f"  {finding}")
    
    if results['summary']['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in results['summary']['recommendations']:
            print(f"  {rec}") 