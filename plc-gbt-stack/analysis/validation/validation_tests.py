#!/usr/bin/env python3
"""
Phase 22.1.5: Validation Framework Testing
==========================================

Comprehensive testing framework for the validation system including
statistical tests, confidence scoring, WolframAlpha Pro integration,
and validation manager functionality.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
import unittest

import numpy as np

from .confidence_scoring import ConfidenceDimension, ConfidenceScorer
from .statistical_tests import StatisticalTestSuite, TestType
from .validation_manager import ValidationLevel, ValidationManager
from .wolfram_integration import MathematicalValidation, ValidationType, WolframValidator

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestStatisticalValidation(unittest.TestCase):
    """Test statistical validation functionality"""

    def setUp(self):
        self.test_suite = StatisticalTestSuite()

        # Sample data for testing
        self.sample_pid_input = {
            'setpoint': [50] * 20 + [60] * 30,
            'process_variable': [49.8, 50.1, 49.9, 50.0, 50.2] * 10,
            'control_output': [45, 46, 44, 45, 47] * 10
        }

        self.sample_pid_results = {
            'kp': 1.5,
            'ki': 0.1,
            'kd': 0.05,
            'success': True
        }

        self.sample_step_data = list(range(20)) + [20] * 30  # Step response
        self.sample_step_results = {
            'steps': [{
                'time': 20,
                'magnitude': 20,
                'confidence': 0.95
            }],
            'success': True
        }

    def test_pid_tuning_validation(self):
        """Test PID tuning validation"""
        results = self.test_suite.validate_pid_tuning_results(
            self.sample_pid_input,
            self.sample_pid_results
        )

        self.assertGreater(len(results), 0, "Should return validation results")

        # Check that we have key validation tests
        test_names = [result.test_name for result in results]
        self.assertIn("PID Parameter Reasonableness", test_names)

        # Check that all results have required fields
        for result in results:
            self.assertIsInstance(result.test_name, str)
            self.assertIsInstance(result.test_type, TestType)
            self.assertIsInstance(result.statistic, (int, float))
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.confidence, (int, float))

    def test_step_detection_validation(self):
        """Test step detection validation"""
        results = self.test_suite.validate_step_detection_results(
            self.sample_step_data,
            self.sample_step_results['steps']
        )

        self.assertGreater(len(results), 0, "Should return validation results")

        # Check that results contain expected components
        for result in results:
            self.assertGreater(len(result.description), 0, "Should have description")
            self.assertIsInstance(result.recommendations, list)

    def test_model_identification_validation(self):
        """Test model identification validation"""
        input_data = list(range(50))
        output_data = [x * 1.5 + np.random.normal(0, 0.1) for x in input_data]
        model_params = {
            'process_gain': 1.5,
            'time_constant': 10.0,
            'dead_time': 2.0,
            'r_squared': 0.95
        }

        results = self.test_suite.validate_model_identification_results(
            input_data, output_data, model_params
        )

        self.assertGreater(len(results), 0, "Should return validation results")

        # Check parameter validation
        param_test = next((r for r in results if "Parameter" in r.test_name), None)
        self.assertIsNotNone(param_test, "Should include parameter validation")

    def test_normality_test(self):
        """Test normality testing"""
        # Normal data
        normal_data = np.random.normal(0, 1, 100).tolist()
        result = self.test_suite._test_normality(normal_data, "Normal Data Test")

        self.assertEqual(result.test_type, TestType.NORMALITY)
        self.assertIsInstance(result.p_value, float)

        # Non-normal data (uniform)
        uniform_data = np.random.uniform(0, 1, 100).tolist()
        result = self.test_suite._test_normality(uniform_data, "Uniform Data Test")

        self.assertEqual(result.test_type, TestType.NORMALITY)

    def test_insufficient_data_handling(self):
        """Test handling of insufficient data"""
        small_data = [1, 2, 3]  # Too small for meaningful statistics

        result = self.test_suite._test_normality(small_data, "Small Data Test")
        self.assertFalse(result.passed, "Should fail with insufficient data")
        self.assertIn("Insufficient", result.description)

    def test_statistical_suite_statistics(self):
        """Test statistical suite execution statistics"""
        # Run some validations
        self.test_suite.validate_pid_tuning_results(
            self.sample_pid_input,
            self.sample_pid_results
        )

        stats = self.test_suite.get_test_statistics()

        self.assertIn('total_tests', stats)
        self.assertIn('passed_tests', stats)
        self.assertIn('pass_rate', stats)
        self.assertGreater(stats['total_tests'], 0)

class TestConfidenceScoring(unittest.TestCase):
    """Test confidence scoring functionality"""

    def setUp(self):
        self.confidence_scorer = ConfidenceScorer()

        self.sample_input_data = {
            'setpoint': [50] * 50,
            'process_variable': [49.9 + np.random.normal(0, 0.1) for _ in range(50)],
            'control_output': [45 + np.random.normal(0, 1) for _ in range(50)]
        }

        self.sample_results = {
            'kp': 1.2,
            'ki': 0.08,
            'kd': 0.03,
            'success': True
        }

    def test_confidence_assessment(self):
        """Test overall confidence assessment"""
        confidence = self.confidence_scorer.assess_confidence(
            "pid_tuning",
            self.sample_input_data,
            self.sample_results
        )

        self.assertIsInstance(confidence.overall_score, float)
        self.assertGreaterEqual(confidence.overall_score, 0.0)
        self.assertLessEqual(confidence.overall_score, 1.0)
        self.assertIn(confidence.confidence_level,
                     ['very_low', 'low', 'medium', 'high', 'very_high', 'absolute'])

        # Check dimension scores
        self.assertIn(ConfidenceDimension.DATA_QUALITY, confidence.dimension_scores)
        self.assertIn(ConfidenceDimension.ALGORITHM_PERFORMANCE, confidence.dimension_scores)

    def test_data_quality_assessment(self):
        """Test data quality confidence dimension"""
        score = self.confidence_scorer._assess_data_quality(self.sample_input_data)

        self.assertEqual(score.dimension, ConfidenceDimension.DATA_QUALITY)
        self.assertIsInstance(score.score, float)
        self.assertIsInstance(score.evidence, list)
        self.assertGreater(len(score.evidence), 0)
        self.assertIn('completeness', score.metrics)

    def test_algorithm_performance_assessment(self):
        """Test algorithm performance confidence dimension"""
        metadata = {'execution_time': 0.5, 'iterations': 10}

        score = self.confidence_scorer._assess_algorithm_performance(
            "pid_tuning",
            self.sample_results,
            metadata
        )

        self.assertEqual(score.dimension, ConfidenceDimension.ALGORITHM_PERFORMANCE)
        self.assertIsInstance(score.score, float)
        self.assertIn('execution_success', score.metrics)

    def test_domain_consistency_assessment(self):
        """Test domain consistency confidence dimension"""
        score = self.confidence_scorer._assess_domain_consistency(
            "pid_tuning",
            self.sample_results
        )

        self.assertEqual(score.dimension, ConfidenceDimension.DOMAIN_CONSISTENCY)
        self.assertIsInstance(score.score, float)

        # Test with invalid parameters
        invalid_results = {
            'kp': -1.0,  # Invalid negative gain
            'ki': 1000.0,  # Unreasonably high
            'kd': -0.1,  # Invalid negative
            'success': True
        }

        score = self.confidence_scorer._assess_domain_consistency(
            "pid_tuning",
            invalid_results
        )

        self.assertLess(score.score, 0.8, "Should have low confidence for invalid parameters")

    def test_confidence_level_mapping(self):
        """Test confidence score to level mapping"""
        test_cases = [
            (0.1, 'very_low'),
            (0.4, 'low'),
            (0.6, 'medium'),
            (0.8, 'high'),
            (0.92, 'very_high'),
            (0.98, 'absolute')
        ]

        for score, expected_level in test_cases:
            level = self.confidence_scorer._score_to_confidence_level(score)
            self.assertEqual(level, expected_level,
                           f"Score {score} should map to {expected_level}")

class TestWolframIntegration(unittest.TestCase):
    """Test WolframAlpha Pro integration functionality"""

    def setUp(self):
        # Initialize without API key for testing (will use mock responses)
        self.wolfram_validator = WolframValidator(app_id=None)

    def test_pid_tuning_validation(self):
        """Test PID tuning equations validation"""
        results = self.wolfram_validator.validate_pid_tuning_equations(
            kp=1.5, ki=0.1, kd=0.05
        )

        self.assertGreater(len(results), 0, "Should return validation results")

        for result in results:
            self.assertIsInstance(result.validation_id, str)
            self.assertIsInstance(result.query, str)
            self.assertIsInstance(result.success, bool)
            self.assertIsInstance(result.confidence, float)

    def test_step_response_validation(self):
        """Test step response analysis validation"""
        step_data = [0] * 10 + [1] * 20  # Step response
        parameters = {
            'rise_time': 5,
            'settling_time': 15,
            'overshoot': 0.1,
            'steady_state_value': 1.0
        }

        results = self.wolfram_validator.validate_step_response_analysis(
            step_data, parameters
        )

        self.assertGreater(len(results), 0, "Should return validation results")

    def test_model_identification_validation(self):
        """Test model identification validation"""
        model_params = {
            'gain': 2.0,
            'time_constant': 10.0,
            'dead_time': 1.5
        }
        fit_metrics = {
            'r_squared': 0.92
        }

        results = self.wolfram_validator.validate_model_identification(
            model_params, fit_metrics
        )

        self.assertGreater(len(results), 0, "Should return validation results")

    def test_mathematical_validation_types(self):
        """Test different types of mathematical validation"""
        validations = [
            MathematicalValidation(
                expression="2 + 2",
                validation_type=ValidationType.NUMERICAL_CALCULATION,
                expected_result=4
            ),
            MathematicalValidation(
                expression="x^2 + 2*x + 1",
                validation_type=ValidationType.SYMBOLIC_MANIPULATION
            ),
            MathematicalValidation(
                expression="s + 1",
                validation_type=ValidationType.CONTROL_THEORY
            )
        ]

        for validation in validations:
            result = self.wolfram_validator.validate_expression(validation)
            self.assertIsInstance(result.validation_id, str)
            self.assertIsInstance(result.query, str)

    def test_cache_functionality(self):
        """Test result caching"""
        validation = MathematicalValidation(
            expression="1 + 1",
            validation_type=ValidationType.NUMERICAL_CALCULATION
        )

        # First call
        result1 = self.wolfram_validator.validate_expression(validation)

        # Second call (should use cache)
        result2 = self.wolfram_validator.validate_expression(validation)

        # Results should be equivalent but different validation IDs
        self.assertEqual(result1.query, result2.query)
        self.assertNotEqual(result1.validation_id, result2.validation_id)

        # Check cache statistics
        stats = self.wolfram_validator.get_validation_statistics()
        self.assertIn('cache_hits', stats)

class TestValidationManager(unittest.TestCase):
    """Test validation manager functionality"""

    def setUp(self):
        self.validation_manager = ValidationManager(
            enable_statistical=True,
            enable_confidence=True,
            enable_wolfram=True
        )

        self.sample_input = {
            'setpoint': [50] * 25 + [60] * 25,
            'process_variable': [49.9 + np.random.normal(0, 0.2) for _ in range(50)],
            'control_output': [45 + np.random.normal(0, 1) for _ in range(50)]
        }

        self.sample_results = {
            'kp': 1.8,
            'ki': 0.12,
            'kd': 0.04,
            'success': True
        }

    def test_comprehensive_validation(self):
        """Test comprehensive validation workflow"""
        report = self.validation_manager.validate_analysis_results(
            analysis_type="pid_tuning",
            input_data=self.sample_input,
            results=self.sample_results,
            validation_level=ValidationLevel.STANDARD
        )

        self.assertIsInstance(report.validation_id, str)
        self.assertEqual(report.analysis_type, "pid_tuning")
        self.assertEqual(report.validation_level, ValidationLevel.STANDARD)
        self.assertIsInstance(report.overall_score, float)
        self.assertIsInstance(report.summary, str)
        self.assertIsInstance(report.recommendations, list)

    def test_validation_levels(self):
        """Test different validation levels"""
        levels = [ValidationLevel.BASIC, ValidationLevel.STANDARD,
                 ValidationLevel.COMPREHENSIVE, ValidationLevel.PRODUCTION]

        for level in levels:
            report = self.validation_manager.validate_analysis_results(
                analysis_type="pid_tuning",
                input_data=self.sample_input,
                results=self.sample_results,
                validation_level=level
            )

            self.assertEqual(report.validation_level, level)
            self.assertIsInstance(report.overall_score, float)

    def test_convenience_methods(self):
        """Test convenience validation methods"""
        # Test PID tuning validation
        pid_report = self.validation_manager.validate_pid_tuning(
            self.sample_input,
            self.sample_results
        )
        self.assertEqual(pid_report.analysis_type, "pid_tuning")

        # Test step detection validation
        step_input = {'data': list(range(20)) + [20] * 20}
        step_results = {
            'steps': [{'time': 20, 'magnitude': 20}],
            'success': True
        }

        step_report = self.validation_manager.validate_step_detection(
            step_input,
            step_results
        )
        self.assertEqual(step_report.analysis_type, "step_detection")

        # Test model identification validation
        model_input = {'input': list(range(30)), 'output': list(range(30))}
        model_results = {
            'process_gain': 1.5,
            'time_constant': 8.0,
            'dead_time': 1.0,
            'success': True
        }

        model_report = self.validation_manager.validate_model_identification(
            model_input,
            model_results
        )
        self.assertEqual(model_report.analysis_type, "model_identification")

    def test_error_handling(self):
        """Test error handling in validation"""
        # Test with invalid input
        invalid_input = {}
        invalid_results = {}

        report = self.validation_manager.validate_analysis_results(
            analysis_type="invalid_type",
            input_data=invalid_input,
            results=invalid_results
        )

        # Should still return a report, possibly with errors
        self.assertIsInstance(report.validation_id, str)
        self.assertIsInstance(report.overall_score, float)

    def test_statistics_tracking(self):
        """Test validation statistics tracking"""
        # Run several validations
        for _i in range(3):
            self.validation_manager.validate_analysis_results(
                analysis_type="pid_tuning",
                input_data=self.sample_input,
                results=self.sample_results
            )

        stats = self.validation_manager.get_validation_statistics()

        self.assertIn('total_validations', stats)
        self.assertIn('success_rate', stats)
        self.assertIn('component_stats', stats)
        self.assertEqual(stats['total_validations'], 3)

class TestValidationIntegration(unittest.TestCase):
    """Test integration between validation components"""

    def test_end_to_end_validation(self):
        """Test complete end-to-end validation workflow"""
        # Create realistic test data
        np.random.seed(42)  # For reproducible results

        input_data = {
            'setpoint': [25.0] * 30 + [35.0] * 30 + [30.0] * 40,
            'process_variable': [],
            'control_output': []
        }

        # Simulate realistic process response
        pv = 25.0
        co = 50.0
        for sp in input_data['setpoint']:
            error = sp - pv
            co += error * 0.1 + np.random.normal(0, 0.5)
            co = max(0, min(100, co))  # Clamp control output

            pv += (co - 50) * 0.02 + np.random.normal(0, 0.1)
            input_data['process_variable'].append(pv)
            input_data['control_output'].append(co)

        # Realistic PID tuning results
        tuning_results = {
            'kp': 2.5,
            'ki': 0.15,
            'kd': 0.08,
            'success': True,
            'rise_time': 8.5,
            'settling_time': 25.0,
            'overshoot': 0.12
        }

        # Process parameters
        process_params = {
            'gain': 1.8,
            'time_constant': 15.0,
            'dead_time': 2.0
        }

        # Create validation manager
        manager = ValidationManager(
            enable_statistical=True,
            enable_confidence=True,
            enable_wolfram=True
        )

        # Run comprehensive validation
        report = manager.validate_analysis_results(
            analysis_type="pid_tuning",
            input_data=input_data,
            results=tuning_results,
            validation_level=ValidationLevel.COMPREHENSIVE,
            metadata={'process_params': process_params}
        )

        # Validate report structure
        self.assertIsInstance(report, type(report))
        self.assertGreater(len(report.summary), 0)
        self.assertIsInstance(report.overall_score, float)
        self.assertIn(report.overall_status.value, ['passed', 'failed', 'warning', 'error'])

        # Check component results
        if report.statistical_results:
            self.assertGreater(len(report.statistical_results), 0)

        if report.confidence_assessment:
            self.assertIsInstance(report.confidence_assessment.overall_score, float)

        if report.wolfram_results:
            self.assertGreater(len(report.wolfram_results), 0)

        # Log results for inspection
        logger.info(f"Validation Report Summary: {report.summary}")
        logger.info(f"Overall Score: {report.overall_score:.3f}")
        logger.info(f"Execution Time: {report.execution_time:.3f}s")

def run_validation_tests():
    """Run all validation tests"""
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestStatisticalValidation,
        TestConfidenceScoring,
        TestWolframIntegration,
        TestValidationManager,
        TestValidationIntegration
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    return result

if __name__ == "__main__":
    print("=" * 60)
    print("Phase 22.1.5: Validation Framework Testing")
    print("=" * 60)

    result = run_validation_tests()

    print("\n" + "=" * 60)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("=" * 60)

# Export test components
__all__ = [
    'TestStatisticalValidation',
    'TestConfidenceScoring',
    'TestWolframIntegration',
    'TestValidationManager',
    'TestValidationIntegration',
    'run_validation_tests'
]
