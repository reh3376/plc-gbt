#!/usr/bin/env python3
"""
Phase 22.1.5: Confidence Scoring System
=======================================

Multi-dimensional confidence assessment system for control loop analysis results
providing comprehensive confidence metrics with industrial control domain expertise.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class ConfidenceDimension(Enum):
    """Dimensions of confidence assessment"""
    DATA_QUALITY = "data_quality"
    ALGORITHM_PERFORMANCE = "algorithm_performance"
    STATISTICAL_SIGNIFICANCE = "statistical_significance"
    DOMAIN_CONSISTENCY = "domain_consistency"
    MATHEMATICAL_ACCURACY = "mathematical_accuracy"
    CONVERGENCE_STABILITY = "convergence_stability"
    CROSS_VALIDATION = "cross_validation"
    HISTORICAL_COMPARISON = "historical_comparison"

@dataclass
class ConfidenceScore:
    """Confidence score for a specific dimension"""
    dimension: ConfidenceDimension
    score: float  # 0.0 to 1.0
    confidence_level: str  # very_low, low, medium, high, very_high, absolute
    weight: float  # Importance weight for overall calculation
    evidence: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

@dataclass
class OverallConfidence:
    """Overall confidence assessment"""
    overall_score: float
    confidence_level: str
    weighted_score: float
    dimension_scores: Dict[ConfidenceDimension, ConfidenceScore]
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class ConfidenceScorer:
    """
    Comprehensive confidence scoring system for control loop analysis validation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__ + '.ConfidenceScorer')
        
        # Default dimension weights (can be customized)
        self.dimension_weights = {
            ConfidenceDimension.DATA_QUALITY: 0.20,
            ConfidenceDimension.ALGORITHM_PERFORMANCE: 0.18,
            ConfidenceDimension.STATISTICAL_SIGNIFICANCE: 0.15,
            ConfidenceDimension.DOMAIN_CONSISTENCY: 0.15,
            ConfidenceDimension.MATHEMATICAL_ACCURACY: 0.12,
            ConfidenceDimension.CONVERGENCE_STABILITY: 0.10,
            ConfidenceDimension.CROSS_VALIDATION: 0.08,
            ConfidenceDimension.HISTORICAL_COMPARISON: 0.02
        }
        
        # Confidence level thresholds
        self.confidence_thresholds = {
            'very_low': (0.0, 0.3),
            'low': (0.3, 0.5),
            'medium': (0.5, 0.7),
            'high': (0.7, 0.9),
            'very_high': (0.9, 0.95),
            'absolute': (0.95, 1.0)
        }
    
    def assess_confidence(self,
                         analysis_type: str,
                         input_data: Dict[str, Any],
                         results: Dict[str, Any],
                         validation_results: Optional[List[Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> OverallConfidence:
        """
        Assess overall confidence in analysis results
        
        Args:
            analysis_type: Type of analysis performed
            input_data: Original input data
            results: Analysis results
            validation_results: Statistical validation results
            metadata: Additional metadata
            
        Returns:
            Overall confidence assessment
        """
        try:
            dimension_scores = {}
            
            # Assess each confidence dimension
            dimension_scores[ConfidenceDimension.DATA_QUALITY] = self._assess_data_quality(input_data)
            dimension_scores[ConfidenceDimension.ALGORITHM_PERFORMANCE] = self._assess_algorithm_performance(
                analysis_type, results, metadata
            )
            dimension_scores[ConfidenceDimension.STATISTICAL_SIGNIFICANCE] = self._assess_statistical_significance(
                validation_results
            )
            dimension_scores[ConfidenceDimension.DOMAIN_CONSISTENCY] = self._assess_domain_consistency(
                analysis_type, results
            )
            dimension_scores[ConfidenceDimension.MATHEMATICAL_ACCURACY] = self._assess_mathematical_accuracy(
                results, metadata
            )
            dimension_scores[ConfidenceDimension.CONVERGENCE_STABILITY] = self._assess_convergence_stability(
                results, metadata
            )
            dimension_scores[ConfidenceDimension.CROSS_VALIDATION] = self._assess_cross_validation(
                input_data, results, metadata
            )
            dimension_scores[ConfidenceDimension.HISTORICAL_COMPARISON] = self._assess_historical_comparison(
                results, metadata
            )
            
            # Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(dimension_scores)
            
            self.logger.info(f"Confidence assessment completed: {overall_confidence.confidence_level} "
                           f"({overall_confidence.overall_score:.3f})")
            
            return overall_confidence
            
        except Exception as e:
            self.logger.error(f"Confidence assessment failed: {e}")
            return self._create_error_confidence(str(e))
    
    def _assess_data_quality(self, input_data: Dict[str, Any]) -> ConfidenceScore:
        """Assess data quality confidence"""
        try:
            evidence = []
            metrics = {}
            score_components = []
            
            # Check data completeness
            data_fields = ['setpoint', 'process_variable', 'control_output', 'data']
            available_fields = sum(1 for field in data_fields if field in input_data and input_data[field])
            completeness_score = available_fields / len(data_fields)
            score_components.append(completeness_score)
            metrics['completeness'] = completeness_score
            evidence.append(f"Data completeness: {available_fields}/{len(data_fields)} fields")
            
            # Check data size adequacy
            data_sizes = []
            for field in data_fields:
                if field in input_data and isinstance(input_data[field], (list, np.ndarray)):
                    data_sizes.append(len(input_data[field]))
            
            if data_sizes:
                min_size = min(data_sizes)
                max_size = max(data_sizes)
                avg_size = np.mean(data_sizes)
                
                # Size adequacy scoring
                if avg_size >= 100:
                    size_score = 1.0
                elif avg_size >= 50:
                    size_score = 0.8
                elif avg_size >= 20:
                    size_score = 0.6
                elif avg_size >= 10:
                    size_score = 0.4
                else:
                    size_score = 0.2
                
                score_components.append(size_score)
                metrics['size_adequacy'] = size_score
                metrics['average_size'] = avg_size
                evidence.append(f"Average data size: {avg_size:.1f} points")
            else:
                score_components.append(0.2)
                evidence.append("No valid data arrays found")
            
            # Check data consistency (if multiple arrays)
            if len(data_sizes) > 1:
                size_variation = (max_size - min_size) / max_size if max_size > 0 else 1.0
                consistency_score = max(0, 1.0 - size_variation)
                score_components.append(consistency_score)
                metrics['size_consistency'] = consistency_score
                evidence.append(f"Size consistency: {consistency_score:.3f}")
            else:
                score_components.append(0.8)  # Neutral score for single array
            
            # Check for missing values and outliers
            outlier_scores = []
            for field in data_fields:
                if field in input_data and isinstance(input_data[field], (list, np.ndarray)):
                    data_array = np.array(input_data[field])
                    valid_data = data_array[~np.isnan(data_array)]
                    
                    if len(valid_data) > 0:
                        # Missing values
                        missing_ratio = (len(data_array) - len(valid_data)) / len(data_array)
                        missing_score = max(0, 1.0 - missing_ratio * 2)  # Penalize missing values
                        
                        # Outliers (using IQR method)
                        if len(valid_data) > 4:
                            q1, q3 = np.percentile(valid_data, [25, 75])
                            iqr = q3 - q1
                            if iqr > 0:
                                outlier_bounds = (q1 - 1.5 * iqr, q3 + 1.5 * iqr)
                                outliers = np.sum((valid_data < outlier_bounds[0]) | (valid_data > outlier_bounds[1]))
                                outlier_ratio = outliers / len(valid_data)
                                outlier_score = max(0, 1.0 - outlier_ratio * 3)  # Penalize outliers
                            else:
                                outlier_score = 0.5  # Neutral for constant data
                        else:
                            outlier_score = 0.6  # Insufficient data for outlier detection
                        
                        field_quality = (missing_score + outlier_score) / 2
                        outlier_scores.append(field_quality)
                        
                        metrics[f'{field}_missing_ratio'] = missing_ratio
                        metrics[f'{field}_outlier_ratio'] = outlier_ratio if 'outlier_ratio' in locals() else 0
            
            if outlier_scores:
                data_quality_score = np.mean(outlier_scores)
                score_components.append(data_quality_score)
                metrics['data_quality'] = data_quality_score
                evidence.append(f"Data quality score: {data_quality_score:.3f}")
            else:
                score_components.append(0.5)
                evidence.append("No data available for quality assessment")
            
            # Calculate overall data quality score
            overall_score = np.mean(score_components)
            confidence_level = self._score_to_confidence_level(overall_score)
            
            recommendations = []
            if overall_score < 0.7:
                recommendations.append("Consider collecting more data for better confidence")
            if completeness_score < 0.5:
                recommendations.append("Missing critical data fields")
            if avg_size < 50:
                recommendations.append("Data size may be insufficient for reliable analysis")
            
            return ConfidenceScore(
                dimension=ConfidenceDimension.DATA_QUALITY,
                score=overall_score,
                confidence_level=confidence_level,
                weight=self.dimension_weights[ConfidenceDimension.DATA_QUALITY],
                evidence=evidence,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self._create_error_dimension_score(
                ConfidenceDimension.DATA_QUALITY, 
                f"Data quality assessment failed: {e}"
            )
    
    def _assess_algorithm_performance(self, 
                                    analysis_type: str, 
                                    results: Dict[str, Any],
                                    metadata: Optional[Dict[str, Any]]) -> ConfidenceScore:
        """Assess algorithm performance confidence"""
        try:
            evidence = []
            metrics = {}
            score_components = []
            
            # Check algorithm execution success
            success = results.get('success', False)
            execution_score = 1.0 if success else 0.0
            score_components.append(execution_score)
            metrics['execution_success'] = execution_score
            evidence.append(f"Algorithm execution: {'successful' if success else 'failed'}")
            
            # Check execution time performance
            if metadata and 'execution_time' in metadata:
                exec_time = metadata['execution_time']
                
                # Time performance scoring (context-dependent)
                if analysis_type == 'pid_tuning':
                    time_threshold = 10.0  # 10 seconds
                elif analysis_type == 'step_detection':
                    time_threshold = 5.0   # 5 seconds
                else:
                    time_threshold = 15.0  # 15 seconds default
                
                time_score = max(0, min(1.0, time_threshold / max(exec_time, 0.1)))
                score_components.append(time_score)
                metrics['execution_time_score'] = time_score
                metrics['execution_time'] = exec_time
                evidence.append(f"Execution time: {exec_time:.3f}s (score: {time_score:.3f})")
            else:
                score_components.append(0.7)  # Neutral score
                evidence.append("Execution time not available")
            
            # Check result completeness
            expected_fields = self._get_expected_result_fields(analysis_type)
            available_fields = sum(1 for field in expected_fields if field in results)
            completeness_score = available_fields / len(expected_fields) if expected_fields else 1.0
            score_components.append(completeness_score)
            metrics['result_completeness'] = completeness_score
            evidence.append(f"Result completeness: {available_fields}/{len(expected_fields)} fields")
            
            # Check result validity
            validity_score = self._assess_result_validity(analysis_type, results)
            score_components.append(validity_score)
            metrics['result_validity'] = validity_score
            evidence.append(f"Result validity score: {validity_score:.3f}")
            
            # Check algorithm-specific performance metrics
            if analysis_type == 'pid_tuning':
                performance_score = self._assess_pid_performance(results, metadata)
            elif analysis_type == 'step_detection':
                performance_score = self._assess_step_detection_performance(results, metadata)
            elif analysis_type == 'model_identification':
                performance_score = self._assess_model_performance(results, metadata)
            else:
                performance_score = 0.7  # Neutral for unknown types
            
            score_components.append(performance_score)
            metrics['algorithm_specific_performance'] = performance_score
            evidence.append(f"Algorithm-specific performance: {performance_score:.3f}")
            
            # Calculate overall algorithm performance score
            overall_score = np.mean(score_components)
            confidence_level = self._score_to_confidence_level(overall_score)
            
            recommendations = []
            if not success:
                recommendations.append("Algorithm execution failed - check input data and parameters")
            if completeness_score < 0.8:
                recommendations.append("Results missing expected fields")
            if validity_score < 0.6:
                recommendations.append("Result values appear invalid")
            if overall_score < 0.7:
                recommendations.append("Consider algorithm parameter tuning")
            
            return ConfidenceScore(
                dimension=ConfidenceDimension.ALGORITHM_PERFORMANCE,
                score=overall_score,
                confidence_level=confidence_level,
                weight=self.dimension_weights[ConfidenceDimension.ALGORITHM_PERFORMANCE],
                evidence=evidence,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self._create_error_dimension_score(
                ConfidenceDimension.ALGORITHM_PERFORMANCE,
                f"Algorithm performance assessment failed: {e}"
            )
    
    def _assess_statistical_significance(self, validation_results: Optional[List[Any]]) -> ConfidenceScore:
        """Assess statistical significance confidence"""
        try:
            evidence = []
            metrics = {}
            
            if not validation_results:
                return ConfidenceScore(
                    dimension=ConfidenceDimension.STATISTICAL_SIGNIFICANCE,
                    score=0.3,
                    confidence_level='low',
                    weight=self.dimension_weights[ConfidenceDimension.STATISTICAL_SIGNIFICANCE],
                    evidence=["No statistical validation results available"],
                    metrics={},
                    recommendations=["Perform statistical validation for better confidence assessment"]
                )
            
            # Analyze validation results
            total_tests = len(validation_results)
            passed_tests = sum(1 for result in validation_results if result.passed)
            
            if total_tests == 0:
                pass_rate = 0.0
            else:
                pass_rate = passed_tests / total_tests
            
            metrics['total_tests'] = total_tests
            metrics['passed_tests'] = passed_tests
            metrics['pass_rate'] = pass_rate
            evidence.append(f"Statistical tests: {passed_tests}/{total_tests} passed ({pass_rate:.1%})")
            
            # Assess confidence levels of individual tests
            confidence_scores = [result.confidence for result in validation_results if hasattr(result, 'confidence')]
            if confidence_scores:
                avg_confidence = np.mean(confidence_scores)
                min_confidence = np.min(confidence_scores)
                metrics['average_test_confidence'] = avg_confidence
                metrics['minimum_test_confidence'] = min_confidence
                evidence.append(f"Average test confidence: {avg_confidence:.3f}")
                evidence.append(f"Minimum test confidence: {min_confidence:.3f}")
            else:
                avg_confidence = 0.5
                min_confidence = 0.5
            
            # Assess p-values significance
            p_values = [result.p_value for result in validation_results if hasattr(result, 'p_value')]
            if p_values:
                significant_p_values = sum(1 for p in p_values if p < 0.05)
                p_value_rate = significant_p_values / len(p_values)
                metrics['significant_p_value_rate'] = p_value_rate
                evidence.append(f"Statistically significant results: {significant_p_values}/{len(p_values)}")
            else:
                p_value_rate = 0.5
            
            # Calculate overall statistical significance score
            score_components = [pass_rate, avg_confidence, min_confidence * 0.5, p_value_rate]
            overall_score = np.mean(score_components)
            confidence_level = self._score_to_confidence_level(overall_score)
            
            recommendations = []
            if pass_rate < 0.7:
                recommendations.append("Low statistical test pass rate - review analysis parameters")
            if avg_confidence < 0.6:
                recommendations.append("Low average test confidence - consider more data")
            if p_value_rate < 0.5:
                recommendations.append("Few statistically significant results")
            
            return ConfidenceScore(
                dimension=ConfidenceDimension.STATISTICAL_SIGNIFICANCE,
                score=overall_score,
                confidence_level=confidence_level,
                weight=self.dimension_weights[ConfidenceDimension.STATISTICAL_SIGNIFICANCE],
                evidence=evidence,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self._create_error_dimension_score(
                ConfidenceDimension.STATISTICAL_SIGNIFICANCE,
                f"Statistical significance assessment failed: {e}"
            )
    
    def _assess_domain_consistency(self, analysis_type: str, results: Dict[str, Any]) -> ConfidenceScore:
        """Assess domain consistency confidence"""
        try:
            evidence = []
            metrics = {}
            score_components = []
            
            if analysis_type == 'pid_tuning':
                # Check PID parameter ranges
                kp = results.get('kp', 0)
                ki = results.get('ki', 0)
                kd = results.get('kd', 0)
                
                # Industrial typical ranges
                kp_valid = 0.001 <= kp <= 1000
                ki_valid = 0 <= ki <= 100
                kd_valid = 0 <= kd <= 10
                
                param_validity = (int(kp_valid) + int(ki_valid) + int(kd_valid)) / 3
                score_components.append(param_validity)
                metrics['parameter_validity'] = param_validity
                evidence.append(f"PID parameter validity: {param_validity:.3f}")
                
                # Check stability criteria
                if kp > 0:
                    # Basic stability check (simplified)
                    stability_margin = 1.0 / (1.0 + kp)  # Simplified
                    stability_score = min(1.0, stability_margin * 2)
                else:
                    stability_score = 0.0
                
                score_components.append(stability_score)
                metrics['stability_score'] = stability_score
                evidence.append(f"Stability score: {stability_score:.3f}")
            
            elif analysis_type == 'step_detection':
                steps = results.get('steps', [])
                
                if steps:
                    # Check step magnitude reasonableness
                    magnitudes = [step.get('magnitude', 0) for step in steps]
                    if magnitudes:
                        avg_magnitude = np.mean(np.abs(magnitudes))
                        magnitude_score = min(1.0, avg_magnitude / 100)  # Normalize to typical range
                        score_components.append(magnitude_score)
                        metrics['magnitude_score'] = magnitude_score
                        evidence.append(f"Step magnitude score: {magnitude_score:.3f}")
                    
                    # Check step timing distribution
                    times = [step.get('time', 0) for step in steps]
                    if len(times) > 1:
                        time_intervals = np.diff(sorted(times))
                        if len(time_intervals) > 0:
                            min_interval = np.min(time_intervals)
                            timing_score = min(1.0, min_interval / 10)  # At least 10 time units apart
                            score_components.append(timing_score)
                            metrics['timing_score'] = timing_score
                            evidence.append(f"Step timing score: {timing_score:.3f}")
                else:
                    score_components.append(0.5)
                    evidence.append("No steps detected for domain assessment")
            
            elif analysis_type == 'model_identification':
                # Check model parameters
                gain = results.get('process_gain', results.get('gain', 0))
                time_constant = results.get('time_constant', results.get('tau', 0))
                dead_time = results.get('dead_time', results.get('theta', 0))
                
                # Check parameter reasonableness
                gain_valid = 0.1 <= abs(gain) <= 100 if gain != 0 else False
                tau_valid = 0.1 <= time_constant <= 1000 if time_constant > 0 else False
                theta_valid = 0 <= dead_time <= time_constant if time_constant > 0 else dead_time >= 0
                
                param_validity = (int(gain_valid) + int(tau_valid) + int(theta_valid)) / 3
                score_components.append(param_validity)
                metrics['model_parameter_validity'] = param_validity
                evidence.append(f"Model parameter validity: {param_validity:.3f}")
                
                # Check model fit quality
                r_squared = results.get('r_squared', results.get('fit_quality', 0))
                fit_score = max(0, min(1, r_squared)) if r_squared is not None else 0.5
                score_components.append(fit_score)
                metrics['fit_score'] = fit_score
                evidence.append(f"Model fit score: {fit_score:.3f}")
            
            else:
                # Generic domain consistency check
                score_components.append(0.7)  # Neutral score
                evidence.append(f"Generic domain assessment for {analysis_type}")
            
            # Calculate overall domain consistency score
            if score_components:
                overall_score = np.mean(score_components)
            else:
                overall_score = 0.5
            
            confidence_level = self._score_to_confidence_level(overall_score)
            
            recommendations = []
            if overall_score < 0.6:
                recommendations.append("Results may not be consistent with industrial control domain expectations")
            if analysis_type == 'pid_tuning' and param_validity < 0.8:
                recommendations.append("PID parameters outside typical industrial ranges")
            
            return ConfidenceScore(
                dimension=ConfidenceDimension.DOMAIN_CONSISTENCY,
                score=overall_score,
                confidence_level=confidence_level,
                weight=self.dimension_weights[ConfidenceDimension.DOMAIN_CONSISTENCY],
                evidence=evidence,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self._create_error_dimension_score(
                ConfidenceDimension.DOMAIN_CONSISTENCY,
                f"Domain consistency assessment failed: {e}"
            )
    
    # Additional dimension assessment methods...
    
    def _assess_mathematical_accuracy(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> ConfidenceScore:
        """Assess mathematical accuracy confidence"""
        # Placeholder for WolframAlpha Pro integration
        return ConfidenceScore(
            dimension=ConfidenceDimension.MATHEMATICAL_ACCURACY,
            score=0.8,  # Default high confidence pending WolframAlpha integration
            confidence_level='high',
            weight=self.dimension_weights[ConfidenceDimension.MATHEMATICAL_ACCURACY],
            evidence=["Mathematical validation pending WolframAlpha Pro integration"],
            metrics={},
            recommendations=["Integrate WolframAlpha Pro validation for complete mathematical verification"]
        )
    
    def _assess_convergence_stability(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> ConfidenceScore:
        """Assess convergence stability confidence"""
        try:
            evidence = []
            metrics = {}
            
            # Check for convergence indicators in metadata
            if metadata:
                iterations = metadata.get('iterations', 0)
                converged = metadata.get('converged', True)
                convergence_error = metadata.get('convergence_error', 0.0)
                
                # Convergence quality scoring
                convergence_score = 1.0 if converged else 0.3
                
                if iterations > 0:
                    # Prefer fewer iterations for faster convergence
                    iteration_score = max(0.2, min(1.0, 100 / max(iterations, 1)))
                else:
                    iteration_score = 0.5
                
                if convergence_error > 0:
                    error_score = max(0.2, min(1.0, 0.01 / max(convergence_error, 1e-6)))
                else:
                    error_score = 0.8
                
                overall_score = (convergence_score + iteration_score + error_score) / 3
                
                metrics['convergence_score'] = convergence_score
                metrics['iteration_score'] = iteration_score
                metrics['error_score'] = error_score
                evidence.append(f"Convergence: {'achieved' if converged else 'failed'}")
                evidence.append(f"Iterations: {iterations}")
                evidence.append(f"Final error: {convergence_error:.6f}")
            else:
                overall_score = 0.6  # Neutral score without metadata
                evidence.append("No convergence information available")
            
            confidence_level = self._score_to_confidence_level(overall_score)
            
            recommendations = []
            if overall_score < 0.7:
                recommendations.append("Algorithm convergence may be unstable")
            
            return ConfidenceScore(
                dimension=ConfidenceDimension.CONVERGENCE_STABILITY,
                score=overall_score,
                confidence_level=confidence_level,
                weight=self.dimension_weights[ConfidenceDimension.CONVERGENCE_STABILITY],
                evidence=evidence,
                metrics=metrics,
                recommendations=recommendations
            )
            
        except Exception as e:
            return self._create_error_dimension_score(
                ConfidenceDimension.CONVERGENCE_STABILITY,
                f"Convergence stability assessment failed: {e}"
            )
    
    def _assess_cross_validation(self, input_data: Dict[str, Any], results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> ConfidenceScore:
        """Assess cross-validation confidence"""
        # Placeholder for cross-validation implementation
        return ConfidenceScore(
            dimension=ConfidenceDimension.CROSS_VALIDATION,
            score=0.7,
            confidence_level='medium',
            weight=self.dimension_weights[ConfidenceDimension.CROSS_VALIDATION],
            evidence=["Cross-validation not yet implemented"],
            metrics={},
            recommendations=["Implement cross-validation for improved confidence assessment"]
        )
    
    def _assess_historical_comparison(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> ConfidenceScore:
        """Assess historical comparison confidence"""
        # Placeholder for historical comparison implementation
        return ConfidenceScore(
            dimension=ConfidenceDimension.HISTORICAL_COMPARISON,
            score=0.6,
            confidence_level='medium',
            weight=self.dimension_weights[ConfidenceDimension.HISTORICAL_COMPARISON],
            evidence=["Historical comparison not yet implemented"],
            metrics={},
            recommendations=["Implement historical comparison for enhanced confidence assessment"]
        )
    
    def _calculate_overall_confidence(self, dimension_scores: Dict[ConfidenceDimension, ConfidenceScore]) -> OverallConfidence:
        """Calculate overall confidence from dimension scores"""
        try:
            # Calculate weighted score
            total_weight = 0.0
            weighted_sum = 0.0
            
            for dimension, score in dimension_scores.items():
                weighted_sum += score.score * score.weight
                total_weight += score.weight
            
            if total_weight > 0:
                weighted_score = weighted_sum / total_weight
            else:
                weighted_score = 0.0
            
            # Calculate simple average for overall score
            overall_score = np.mean([score.score for score in dimension_scores.values()])
            
            # Determine confidence level
            confidence_level = self._score_to_confidence_level(overall_score)
            
            # Collect critical issues and recommendations
            critical_issues = []
            recommendations = []
            
            for dimension, score in dimension_scores.items():
                if score.score < 0.5:
                    critical_issues.append(f"Low {dimension.value} confidence: {score.score:.3f}")
                recommendations.extend(score.recommendations)
            
            # Remove duplicate recommendations
            recommendations = list(set(recommendations))
            
            return OverallConfidence(
                overall_score=overall_score,
                confidence_level=confidence_level,
                weighted_score=weighted_score,
                dimension_scores=dimension_scores,
                critical_issues=critical_issues,
                recommendations=recommendations,
                metadata={'calculation_method': 'weighted_average'}
            )
            
        except Exception as e:
            self.logger.error(f"Overall confidence calculation failed: {e}")
            return self._create_error_overall_confidence(str(e))
    
    def _score_to_confidence_level(self, score: float) -> str:
        """Convert numerical score to confidence level string"""
        for level, (min_val, max_val) in self.confidence_thresholds.items():
            if min_val <= score <= max_val:
                return level
        return 'very_low'
    
    def _get_expected_result_fields(self, analysis_type: str) -> List[str]:
        """Get expected result fields for analysis type"""
        if analysis_type == 'pid_tuning':
            return ['kp', 'ki', 'kd', 'success']
        elif analysis_type == 'step_detection':
            return ['steps', 'success']
        elif analysis_type == 'model_identification':
            return ['process_gain', 'time_constant', 'dead_time', 'success']
        else:
            return ['success']
    
    def _assess_result_validity(self, analysis_type: str, results: Dict[str, Any]) -> float:
        """Assess validity of result values"""
        try:
            if analysis_type == 'pid_tuning':
                kp = results.get('kp', 0)
                ki = results.get('ki', 0)
                kd = results.get('kd', 0)
                
                # Check for NaN or infinite values
                valid_kp = np.isfinite(kp) and kp >= 0
                valid_ki = np.isfinite(ki) and ki >= 0
                valid_kd = np.isfinite(kd) and kd >= 0
                
                return (int(valid_kp) + int(valid_ki) + int(valid_kd)) / 3
                
            elif analysis_type == 'step_detection':
                steps = results.get('steps', [])
                if not steps:
                    return 0.5  # No steps detected is valid
                
                valid_steps = 0
                for step in steps:
                    magnitude = step.get('magnitude', 0)
                    time = step.get('time', 0)
                    if np.isfinite(magnitude) and np.isfinite(time) and time >= 0:
                        valid_steps += 1
                
                return valid_steps / len(steps) if steps else 0.5
                
            else:
                # Generic validity check
                return 0.8
                
        except Exception:
            return 0.0
    
    def _assess_pid_performance(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> float:
        """Assess PID-specific performance"""
        try:
            # Check for additional PID metrics
            performance_score = 0.7  # Base score
            
            if 'rise_time' in results:
                rise_time = results['rise_time']
                if 0 < rise_time < 100:  # Reasonable rise time
                    performance_score += 0.1
            
            if 'settling_time' in results:
                settling_time = results['settling_time']
                if 0 < settling_time < 200:  # Reasonable settling time
                    performance_score += 0.1
            
            if 'overshoot' in results:
                overshoot = results['overshoot']
                if 0 <= overshoot <= 0.2:  # Low overshoot
                    performance_score += 0.1
            
            return min(1.0, performance_score)
            
        except Exception:
            return 0.7
    
    def _assess_step_detection_performance(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> float:
        """Assess step detection specific performance"""
        try:
            steps = results.get('steps', [])
            
            if not steps:
                return 0.5  # No steps detected
            
            # Check step quality metrics
            quality_scores = []
            for step in steps:
                confidence = step.get('confidence', 0.5)
                quality_scores.append(confidence)
            
            if quality_scores:
                return np.mean(quality_scores)
            else:
                return 0.6
                
        except Exception:
            return 0.6
    
    def _assess_model_performance(self, results: Dict[str, Any], metadata: Optional[Dict[str, Any]]) -> float:
        """Assess model identification specific performance"""
        try:
            r_squared = results.get('r_squared', results.get('fit_quality', 0))
            
            if r_squared is not None:
                return max(0, min(1, r_squared))
            else:
                return 0.6
                
        except Exception:
            return 0.6
    
    def _create_error_dimension_score(self, dimension: ConfidenceDimension, error_msg: str) -> ConfidenceScore:
        """Create error dimension score"""
        return ConfidenceScore(
            dimension=dimension,
            score=0.0,
            confidence_level='very_low',
            weight=self.dimension_weights[dimension],
            evidence=[f"Assessment failed: {error_msg}"],
            metrics={},
            recommendations=["Check input data and resolve assessment errors"]
        )
    
    def _create_error_confidence(self, error_msg: str) -> OverallConfidence:
        """Create error overall confidence"""
        return OverallConfidence(
            overall_score=0.0,
            confidence_level='very_low',
            weighted_score=0.0,
            dimension_scores={},
            critical_issues=[f"Confidence assessment failed: {error_msg}"],
            recommendations=["Resolve assessment errors and retry"]
        )
    
    def _create_error_overall_confidence(self, error_msg: str) -> OverallConfidence:
        """Create error overall confidence"""
        return OverallConfidence(
            overall_score=0.0,
            confidence_level='very_low',
            weighted_score=0.0,
            dimension_scores={},
            critical_issues=[f"Overall confidence calculation failed: {error_msg}"],
            recommendations=["Check dimension scores and retry calculation"]
        )

def calculate_overall_confidence(dimension_scores: List[ConfidenceScore]) -> OverallConfidence:
    """
    Calculate overall confidence from individual dimension scores
    
    Args:
        dimension_scores: List of confidence scores for different dimensions
        
    Returns:
        Overall confidence assessment
    """
    scorer = ConfidenceScorer()
    dimension_dict = {score.dimension: score for score in dimension_scores}
    return scorer._calculate_overall_confidence(dimension_dict)

# Export main components
__all__ = [
    'ConfidenceScorer',
    'ConfidenceScore',
    'OverallConfidence',
    'ConfidenceDimension',
    'calculate_overall_confidence'
] 