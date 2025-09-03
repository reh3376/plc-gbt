#!/usr/bin/env python3
"""
Phase 22.1.5: Statistical Testing Framework
===========================================

Comprehensive statistical testing suite for validating control loop analysis results
with industrial control domain-specific tests and statistical significance assessment.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
from scipy.stats import (
    anderson,
    pearsonr,
    shapiro,
)

logger = logging.getLogger(__name__)

class TestType(Enum):
    """Types of statistical tests"""
    NORMALITY = "normality"
    CORRELATION = "correlation"
    REGRESSION = "regression"
    VARIANCE = "variance"
    GOODNESS_OF_FIT = "goodness_of_fit"
    TIME_SERIES = "time_series"
    CONTROL_SPECIFIC = "control_specific"
    STABILITY = "stability"

@dataclass
class StatisticalTestResult:
    """Result of a statistical test"""
    test_name: str
    test_type: TestType
    statistic: float
    p_value: float
    critical_value: Optional[float]
    significance_level: float
    passed: bool
    confidence: float
    description: str
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

class StatisticalTestSuite:
    """
    Comprehensive statistical testing suite for control loop analysis validation
    """

    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.logger = logging.getLogger(__name__ + '.StatisticalTestSuite')

        # Test execution statistics
        self._test_stats = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'total_execution_time': 0.0
        }

    def validate_pid_tuning_results(self,
                                   input_data: Dict[str, Any],
                                   tuning_results: Dict[str, Any],
                                   reference_data: Optional[Dict[str, Any]] = None) -> List[StatisticalTestResult]:
        """Validate PID tuning results with statistical tests"""
        results = []
        start_time = datetime.now()

        try:
            # Extract key data
            setpoint = input_data.get('setpoint', [])
            process_variable = input_data.get('process_variable', [])
            control_output = input_data.get('control_output', [])

            kp = tuning_results.get('kp', 0)
            ki = tuning_results.get('ki', 0)
            kd = tuning_results.get('kd', 0)

            # Test 1: PID Parameter Reasonableness
            param_test = self._test_pid_parameter_reasonableness(kp, ki, kd)
            results.append(param_test)

            # Test 2: Process Variable Normality
            if len(process_variable) > 10:
                normality_test = self._test_normality(
                    process_variable,
                    "Process Variable Normality"
                )
                results.append(normality_test)

            # Test 3: Setpoint Tracking Performance
            if len(setpoint) > 5 and len(process_variable) > 5:
                tracking_test = self._test_setpoint_tracking(setpoint, process_variable)
                results.append(tracking_test)

            # Test 4: Control Output Stability
            if len(control_output) > 10:
                stability_test = self._test_control_stability(control_output)
                results.append(stability_test)

            # Test 5: System Response Characteristics
            if len(process_variable) > 20:
                response_test = self._test_system_response(process_variable, setpoint)
                results.append(response_test)

            # Test 6: Reference Comparison (if available)
            if reference_data:
                comparison_test = self._test_reference_comparison(
                    tuning_results, reference_data
                )
                results.append(comparison_test)

            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_test_stats(results, execution_time)

            self.logger.info(f"PID tuning validation completed: {len(results)} tests in {execution_time:.3f}s")

        except Exception as e:
            self.logger.error(f"PID tuning validation failed: {e}")
            error_result = StatisticalTestResult(
                test_name="PID Validation Error",
                test_type=TestType.CONTROL_SPECIFIC,
                statistic=0.0,
                p_value=1.0,
                critical_value=None,
                significance_level=self.significance_level,
                passed=False,
                confidence=0.0,
                description=f"Validation failed: {str(e)}",
                recommendations=["Check input data format and completeness"]
            )
            results.append(error_result)

        return results

    def validate_step_detection_results(self,
                                       data: List[float],
                                       detected_steps: List[Dict[str, Any]]) -> List[StatisticalTestResult]:
        """Validate step detection results"""
        results = []
        start_time = datetime.now()

        try:
            # Test 1: Step Detection Quality
            quality_test = self._test_step_detection_quality(data, detected_steps)
            results.append(quality_test)

            # Test 2: Step Magnitude Significance
            for i, step in enumerate(detected_steps):
                magnitude_test = self._test_step_magnitude_significance(
                    data, step, f"Step_{i+1}"
                )
                results.append(magnitude_test)

            # Test 3: Step Timing Accuracy
            timing_test = self._test_step_timing_accuracy(data, detected_steps)
            results.append(timing_test)

            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_test_stats(results, execution_time)

            self.logger.info(f"Step detection validation completed: {len(results)} tests in {execution_time:.3f}s")

        except Exception as e:
            self.logger.error(f"Step detection validation failed: {e}")
            error_result = StatisticalTestResult(
                test_name="Step Detection Error",
                test_type=TestType.TIME_SERIES,
                statistic=0.0,
                p_value=1.0,
                critical_value=None,
                significance_level=self.significance_level,
                passed=False,
                confidence=0.0,
                description=f"Validation failed: {str(e)}",
                recommendations=["Check step detection input data"]
            )
            results.append(error_result)

        return results

    def validate_model_identification_results(self,
                                            input_data: List[float],
                                            output_data: List[float],
                                            model_params: Dict[str, Any]) -> List[StatisticalTestResult]:
        """Validate model identification results"""
        results = []
        start_time = datetime.now()

        try:
            # Test 1: Model Fit Quality
            fit_test = self._test_model_fit_quality(input_data, output_data, model_params)
            results.append(fit_test)

            # Test 2: Residual Analysis
            residual_test = self._test_residual_analysis(input_data, output_data, model_params)
            results.append(residual_test)

            # Test 3: Parameter Significance
            param_test = self._test_parameter_significance(model_params)
            results.append(param_test)

            # Test 4: Model Stability
            stability_test = self._test_model_stability(model_params)
            results.append(stability_test)

            execution_time = (datetime.now() - start_time).total_seconds()
            self._update_test_stats(results, execution_time)

            self.logger.info(f"Model identification validation completed: {len(results)} tests in {execution_time:.3f}s")

        except Exception as e:
            self.logger.error(f"Model identification validation failed: {e}")
            error_result = StatisticalTestResult(
                test_name="Model Identification Error",
                test_type=TestType.REGRESSION,
                statistic=0.0,
                p_value=1.0,
                critical_value=None,
                significance_level=self.significance_level,
                passed=False,
                confidence=0.0,
                description=f"Validation failed: {str(e)}",
                recommendations=["Check model identification input data"]
            )
            results.append(error_result)

        return results

    def _test_pid_parameter_reasonableness(self, kp: float, ki: float, kd: float) -> StatisticalTestResult:
        """Test if PID parameters are within reasonable ranges"""
        try:
            # Define reasonable ranges for industrial applications
            kp_range = (0.001, 1000.0)
            ki_range = (0.0, 100.0)
            kd_range = (0.0, 10.0)

            # Check each parameter
            kp_valid = kp_range[0] <= kp <= kp_range[1]
            ki_valid = ki_range[0] <= ki <= ki_range[1]
            kd_valid = kd_range[0] <= kd <= kd_range[1]

            # Calculate reasonableness score
            valid_count = sum([kp_valid, ki_valid, kd_valid])
            reasonableness_score = valid_count / 3.0

            # Determine pass/fail
            passed = reasonableness_score >= 0.8
            confidence = reasonableness_score

            recommendations = []
            if not kp_valid:
                recommendations.append(f"Kp value {kp:.4f} outside reasonable range {kp_range}")
            if not ki_valid:
                recommendations.append(f"Ki value {ki:.4f} outside reasonable range {ki_range}")
            if not kd_valid:
                recommendations.append(f"Kd value {kd:.4f} outside reasonable range {kd_range}")

            return StatisticalTestResult(
                test_name="PID Parameter Reasonableness",
                test_type=TestType.CONTROL_SPECIFIC,
                statistic=reasonableness_score,
                p_value=1.0 - reasonableness_score,
                critical_value=0.8,
                significance_level=self.significance_level,
                passed=passed,
                confidence=confidence,
                description=f"PID parameters reasonableness check: Kp={kp:.4f}, Ki={ki:.4f}, Kd={kd:.4f}",
                recommendations=recommendations,
                metadata={'kp': kp, 'ki': ki, 'kd': kd, 'valid_params': valid_count}
            )

        except Exception as e:
            return self._create_error_result("PID Parameter Reasonableness", TestType.CONTROL_SPECIFIC, str(e))

    def _test_normality(self, data: List[float], test_name: str) -> StatisticalTestResult:
        """Test data normality using multiple methods"""
        try:
            data_array = np.array(data)

            # Remove NaN values
            clean_data = data_array[~np.isnan(data_array)]

            if len(clean_data) < 8:
                return StatisticalTestResult(
                    test_name=test_name,
                    test_type=TestType.NORMALITY,
                    statistic=0.0,
                    p_value=1.0,
                    critical_value=None,
                    significance_level=self.significance_level,
                    passed=False,
                    confidence=0.0,
                    description="Insufficient data for normality test",
                    recommendations=["Collect more data points (minimum 8 required)"]
                )

            # Shapiro-Wilk test (most powerful for small samples)
            if len(clean_data) <= 5000:
                statistic, p_value = shapiro(clean_data)
                test_method = "Shapiro-Wilk"
            else:
                # Use Anderson-Darling for larger samples
                result = anderson(clean_data, dist='norm')
                statistic = result.statistic
                p_value = 0.05 if statistic > result.critical_values[2] else 0.1  # Approximate
                test_method = "Anderson-Darling"

            passed = p_value > self.significance_level
            confidence = p_value if passed else (1.0 - p_value)

            recommendations = []
            if not passed:
                recommendations.append("Data may not be normally distributed")
                recommendations.append("Consider data transformation or non-parametric methods")

            return StatisticalTestResult(
                test_name=test_name,
                test_type=TestType.NORMALITY,
                statistic=statistic,
                p_value=p_value,
                critical_value=self.significance_level,
                significance_level=self.significance_level,
                passed=passed,
                confidence=confidence,
                description=f"{test_method} normality test on {len(clean_data)} data points",
                recommendations=recommendations,
                metadata={'method': test_method, 'sample_size': len(clean_data)}
            )

        except Exception as e:
            return self._create_error_result(test_name, TestType.NORMALITY, str(e))

    def _test_setpoint_tracking(self, setpoint: List[float], process_variable: List[float]) -> StatisticalTestResult:
        """Test setpoint tracking performance"""
        try:
            sp_array = np.array(setpoint)
            pv_array = np.array(process_variable)

            # Ensure same length
            min_len = min(len(sp_array), len(pv_array))
            sp_array = sp_array[:min_len]
            pv_array = pv_array[:min_len]

            # Calculate tracking error
            error = pv_array - sp_array
            rmse = np.sqrt(np.mean(error**2))
            mae = np.mean(np.abs(error))

            # Calculate tracking performance metrics
            if np.std(sp_array) > 0:
                normalized_rmse = rmse / np.std(sp_array)
            else:
                normalized_rmse = rmse

            # Correlation between setpoint and process variable
            correlation, p_value = pearsonr(sp_array, pv_array)

            # Performance criteria (industry typical)
            tracking_quality = correlation if correlation > 0 else 0
            passed = correlation > 0.8 and normalized_rmse < 0.2

            recommendations = []
            if correlation < 0.8:
                recommendations.append(f"Low correlation {correlation:.3f} between setpoint and PV")
            if normalized_rmse > 0.2:
                recommendations.append(f"High normalized RMSE {normalized_rmse:.3f}")
            if not recommendations:
                recommendations.append("Good setpoint tracking performance")

            return StatisticalTestResult(
                test_name="Setpoint Tracking Performance",
                test_type=TestType.CONTROL_SPECIFIC,
                statistic=correlation,
                p_value=p_value,
                critical_value=0.8,
                significance_level=self.significance_level,
                passed=passed,
                confidence=tracking_quality,
                description=f"Setpoint tracking: correlation={correlation:.3f}, RMSE={rmse:.3f}",
                recommendations=recommendations,
                metadata={
                    'correlation': correlation,
                    'rmse': rmse,
                    'mae': mae,
                    'normalized_rmse': normalized_rmse
                }
            )

        except Exception as e:
            return self._create_error_result("Setpoint Tracking Performance", TestType.CONTROL_SPECIFIC, str(e))

    def _test_control_stability(self, control_output: List[float]) -> StatisticalTestResult:
        """Test control output stability"""
        try:
            co_array = np.array(control_output)

            # Remove NaN values
            clean_co = co_array[~np.isnan(co_array)]

            if len(clean_co) < 10:
                return self._create_insufficient_data_result("Control Output Stability", TestType.STABILITY)

            # Calculate stability metrics
            co_std = np.std(clean_co)
            co_mean = np.mean(clean_co)
            coefficient_of_variation = co_std / abs(co_mean) if co_mean != 0 else float('inf')

            # Calculate rate of change
            if len(clean_co) > 1:
                diff = np.diff(clean_co)
                rate_of_change = np.mean(np.abs(diff))
                max_rate = np.max(np.abs(diff))
            else:
                rate_of_change = 0
                max_rate = 0

            # Stability criteria
            cv_threshold = 0.1  # 10% coefficient of variation
            rate_threshold = co_std * 0.5  # Rate threshold based on standard deviation

            cv_stable = coefficient_of_variation < cv_threshold
            rate_stable = rate_of_change < rate_threshold

            stability_score = (int(cv_stable) + int(rate_stable)) / 2.0
            passed = stability_score >= 0.8

            recommendations = []
            if not cv_stable:
                recommendations.append(f"High coefficient of variation {coefficient_of_variation:.3f}")
            if not rate_stable:
                recommendations.append(f"High rate of change {rate_of_change:.3f}")
            if not recommendations:
                recommendations.append("Control output is stable")

            return StatisticalTestResult(
                test_name="Control Output Stability",
                test_type=TestType.STABILITY,
                statistic=stability_score,
                p_value=1.0 - stability_score,
                critical_value=0.8,
                significance_level=self.significance_level,
                passed=passed,
                confidence=stability_score,
                description=f"Control stability: CV={coefficient_of_variation:.3f}, Rate={rate_of_change:.3f}",
                recommendations=recommendations,
                metadata={
                    'coefficient_of_variation': coefficient_of_variation,
                    'rate_of_change': rate_of_change,
                    'max_rate': max_rate,
                    'std_dev': co_std
                }
            )

        except Exception as e:
            return self._create_error_result("Control Output Stability", TestType.STABILITY, str(e))

    def _test_system_response(self, process_variable: List[float], setpoint: List[float]) -> StatisticalTestResult:
        """Test system response characteristics"""
        try:
            pv_array = np.array(process_variable)
            sp_array = np.array(setpoint)

            # Ensure same length
            min_len = min(len(pv_array), len(sp_array))
            pv_array = pv_array[:min_len]
            sp_array = sp_array[:min_len]

            if min_len < 20:
                return self._create_insufficient_data_result("System Response", TestType.TIME_SERIES)

            # Detect step changes in setpoint
            sp_diff = np.diff(sp_array)
            step_threshold = np.std(sp_diff) * 3
            step_indices = np.where(np.abs(sp_diff) > step_threshold)[0]

            if len(step_indices) == 0:
                return StatisticalTestResult(
                    test_name="System Response",
                    test_type=TestType.TIME_SERIES,
                    statistic=0.0,
                    p_value=1.0,
                    critical_value=None,
                    significance_level=self.significance_level,
                    passed=False,
                    confidence=0.0,
                    description="No significant setpoint steps detected",
                    recommendations=["Perform step test for system response analysis"]
                )

            # Analyze first step response
            step_idx = step_indices[0]
            step_start = max(0, step_idx - 5)
            step_end = min(len(pv_array), step_idx + 20)

            response_data = pv_array[step_start:step_end]
            initial_value = np.mean(pv_array[step_start:step_idx])
            final_value = sp_array[step_idx + 1]

            # Calculate response characteristics
            settling_time = self._calculate_settling_time(response_data, initial_value, final_value)
            overshoot = self._calculate_overshoot(response_data, initial_value, final_value)
            rise_time = self._calculate_rise_time(response_data, initial_value, final_value)

            # Response quality assessment
            good_settling = settling_time < len(response_data) * 0.8 if settling_time > 0 else False
            low_overshoot = overshoot < 0.2  # Less than 20% overshoot
            reasonable_rise = 0 < rise_time < len(response_data) * 0.5 if rise_time > 0 else False

            response_quality = (int(good_settling) + int(low_overshoot) + int(reasonable_rise)) / 3.0
            passed = response_quality >= 0.6

            recommendations = []
            if not good_settling:
                recommendations.append(f"Long settling time: {settling_time}")
            if not low_overshoot:
                recommendations.append(f"High overshoot: {overshoot:.1%}")
            if not reasonable_rise:
                recommendations.append(f"Poor rise time: {rise_time}")
            if not recommendations:
                recommendations.append("Good system response characteristics")

            return StatisticalTestResult(
                test_name="System Response",
                test_type=TestType.TIME_SERIES,
                statistic=response_quality,
                p_value=1.0 - response_quality,
                critical_value=0.6,
                significance_level=self.significance_level,
                passed=passed,
                confidence=response_quality,
                description=f"Response: settling={settling_time}, overshoot={overshoot:.1%}, rise={rise_time}",
                recommendations=recommendations,
                metadata={
                    'settling_time': settling_time,
                    'overshoot': overshoot,
                    'rise_time': rise_time,
                    'step_detected': len(step_indices)
                }
            )

        except Exception as e:
            return self._create_error_result("System Response", TestType.TIME_SERIES, str(e))

    def _test_reference_comparison(self, results: Dict[str, Any], reference: Dict[str, Any]) -> StatisticalTestResult:
        """Compare results against reference data"""
        try:
            # Extract comparable parameters
            comparable_params = ['kp', 'ki', 'kd', 'process_gain', 'time_constant', 'dead_time']

            comparisons = []
            for param in comparable_params:
                if param in results and param in reference:
                    result_val = results[param]
                    ref_val = reference[param]

                    if ref_val != 0:
                        relative_error = abs(result_val - ref_val) / abs(ref_val)
                        comparisons.append(relative_error)

            if not comparisons:
                return StatisticalTestResult(
                    test_name="Reference Comparison",
                    test_type=TestType.GOODNESS_OF_FIT,
                    statistic=0.0,
                    p_value=1.0,
                    critical_value=None,
                    significance_level=self.significance_level,
                    passed=False,
                    confidence=0.0,
                    description="No comparable parameters found",
                    recommendations=["Ensure reference data contains comparable parameters"]
                )

            # Calculate overall agreement
            mean_error = np.mean(comparisons)
            agreement_score = max(0, 1.0 - mean_error)

            # Agreement criteria
            passed = mean_error < 0.2  # Less than 20% average error

            recommendations = []
            if mean_error > 0.2:
                recommendations.append(f"High average error {mean_error:.1%} compared to reference")
            else:
                recommendations.append("Good agreement with reference data")

            return StatisticalTestResult(
                test_name="Reference Comparison",
                test_type=TestType.GOODNESS_OF_FIT,
                statistic=agreement_score,
                p_value=mean_error,
                critical_value=0.2,
                significance_level=self.significance_level,
                passed=passed,
                confidence=agreement_score,
                description=f"Reference comparison: {len(comparisons)} parameters, {mean_error:.1%} avg error",
                recommendations=recommendations,
                metadata={
                    'compared_parameters': len(comparisons),
                    'mean_relative_error': mean_error,
                    'individual_errors': comparisons
                }
            )

        except Exception as e:
            return self._create_error_result("Reference Comparison", TestType.GOODNESS_OF_FIT, str(e))

    # Additional test methods for step detection and model identification...

    def _calculate_settling_time(self, data: np.ndarray, initial: float, final: float) -> int:
        """Calculate settling time (2% criteria)"""
        try:
            if len(data) < 5:
                return -1

            tolerance = 0.02 * abs(final - initial)
            target_band = (final - tolerance, final + tolerance)

            # Find when signal enters and stays in settling band
            in_band = (data >= target_band[0]) & (data <= target_band[1])

            for i in range(len(data) - 5):
                if all(in_band[i:i+5]):  # Must stay in band for 5 consecutive points
                    return i

            return len(data)  # Never settled

        except Exception:
            return -1

    def _calculate_overshoot(self, data: np.ndarray, initial: float, final: float) -> float:
        """Calculate percentage overshoot"""
        try:
            if len(data) < 3:
                return 0.0

            step_magnitude = abs(final - initial)
            if step_magnitude == 0:
                return 0.0

            if final > initial:
                peak = np.max(data)
                overshoot = max(0, peak - final)
            else:
                peak = np.min(data)
                overshoot = max(0, final - peak)

            return overshoot / step_magnitude

        except Exception:
            return 0.0

    def _calculate_rise_time(self, data: np.ndarray, initial: float, final: float) -> int:
        """Calculate rise time (10% to 90%)"""
        try:
            if len(data) < 5:
                return -1

            step_magnitude = final - initial
            if abs(step_magnitude) < 1e-6:
                return -1

            ten_percent = initial + 0.1 * step_magnitude
            ninety_percent = initial + 0.9 * step_magnitude

            # Find crossing points
            if step_magnitude > 0:
                cross_10 = np.where(data >= ten_percent)[0]
                cross_90 = np.where(data >= ninety_percent)[0]
            else:
                cross_10 = np.where(data <= ten_percent)[0]
                cross_90 = np.where(data <= ninety_percent)[0]

            if len(cross_10) > 0 and len(cross_90) > 0:
                return cross_90[0] - cross_10[0]

            return -1

        except Exception:
            return -1

    def _create_error_result(self, test_name: str, test_type: TestType, error_msg: str) -> StatisticalTestResult:
        """Create error result for failed tests"""
        return StatisticalTestResult(
            test_name=test_name,
            test_type=test_type,
            statistic=0.0,
            p_value=1.0,
            critical_value=None,
            significance_level=self.significance_level,
            passed=False,
            confidence=0.0,
            description=f"Test failed: {error_msg}",
            recommendations=["Check input data and test configuration"]
        )

    def _create_insufficient_data_result(self, test_name: str, test_type: TestType) -> StatisticalTestResult:
        """Create result for insufficient data"""
        return StatisticalTestResult(
            test_name=test_name,
            test_type=test_type,
            statistic=0.0,
            p_value=1.0,
            critical_value=None,
            significance_level=self.significance_level,
            passed=False,
            confidence=0.0,
            description="Insufficient data for statistical test",
            recommendations=["Collect more data points for reliable statistical analysis"]
        )

    def _update_test_stats(self, results: List[StatisticalTestResult], execution_time: float):
        """Update test execution statistics"""
        self._test_stats['total_tests'] += len(results)
        self._test_stats['passed_tests'] += sum(1 for r in results if r.passed)
        self._test_stats['failed_tests'] += sum(1 for r in results if not r.passed)
        self._test_stats['total_execution_time'] += execution_time

    def get_test_statistics(self) -> Dict[str, Any]:
        """Get test execution statistics"""
        stats = self._test_stats.copy()
        if stats['total_tests'] > 0:
            stats['pass_rate'] = stats['passed_tests'] / stats['total_tests']
            stats['average_execution_time'] = stats['total_execution_time'] / stats['total_tests']
        else:
            stats['pass_rate'] = 0.0
            stats['average_execution_time'] = 0.0
        return stats

def run_statistical_validation(analysis_type: str,
                              input_data: Dict[str, Any],
                              results: Dict[str, Any],
                              reference_data: Optional[Dict[str, Any]] = None,
                              significance_level: float = 0.05) -> List[StatisticalTestResult]:
    """
    Run statistical validation for analysis results

    Args:
        analysis_type: Type of analysis (pid_tuning, step_detection, model_identification)
        input_data: Original input data
        results: Analysis results to validate
        reference_data: Optional reference data for comparison
        significance_level: Statistical significance level

    Returns:
        List of statistical test results
    """
    test_suite = StatisticalTestSuite(significance_level)

    if analysis_type == "pid_tuning":
        return test_suite.validate_pid_tuning_results(input_data, results, reference_data)
    elif analysis_type == "step_detection":
        data = input_data.get('data', [])
        detected_steps = results.get('steps', [])
        return test_suite.validate_step_detection_results(data, detected_steps)
    elif analysis_type == "model_identification":
        input_signal = input_data.get('input', [])
        output_signal = input_data.get('output', [])
        return test_suite.validate_model_identification_results(input_signal, output_signal, results)
    else:
        # Generic validation
        logger.warning(f"Unknown analysis type: {analysis_type}, using generic validation")
        return []

# Export main components
__all__ = [
    'StatisticalTestSuite',
    'StatisticalTestResult',
    'TestType',
    'run_statistical_validation'
]
