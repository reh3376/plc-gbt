#!/usr/bin/env python3
"""
Phase 22.1.5: Validation Manager
===============================

Comprehensive validation manager that orchestrates statistical testing,
confidence scoring, and WolframAlpha Pro integration for complete analysis
validation with industrial control domain expertise.

Author: PLC-GPT Development Team
Date: January 18, 2025
Methodology: AI Task Orchestrator Guide
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import time

from .statistical_tests import StatisticalTestSuite, StatisticalTestResult, run_statistical_validation
from .confidence_scoring import ConfidenceScorer, ConfidenceScore, OverallConfidence
from .wolfram_integration import WolframValidator, WolframValidationResult, MathematicalValidation

logger = logging.getLogger(__name__)

class ValidationLevel(Enum):
    """Validation complexity levels"""
    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    PRODUCTION = "production"

class ValidationStatus(Enum):
    """Overall validation status"""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"
    PENDING = "pending"

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    validation_id: str
    analysis_type: str
    validation_level: ValidationLevel
    overall_status: ValidationStatus
    overall_score: float
    confidence_assessment: OverallConfidence
    statistical_results: List[StatisticalTestResult]
    wolfram_results: List[WolframValidationResult]
    execution_time: float
    summary: str
    recommendations: List[str] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationResult:
    """Individual validation result"""
    component: str  # statistical, confidence, wolfram
    success: bool
    score: float
    status: ValidationStatus
    details: Any
    execution_time: float
    error_message: Optional[str] = None

class ValidationManager:
    """
    Comprehensive validation manager orchestrating all validation components
    """
    
    def __init__(self, 
                 enable_statistical: bool = True,
                 enable_confidence: bool = True,
                 enable_wolfram: bool = True,
                 wolfram_app_id: Optional[str] = None):
        
        self.logger = logging.getLogger(__name__ + '.ValidationManager')
        
        # Component enablement
        self.enable_statistical = enable_statistical
        self.enable_confidence = enable_confidence
        self.enable_wolfram = enable_wolfram
        
        # Initialize validation components
        self.statistical_suite = StatisticalTestSuite() if enable_statistical else None
        self.confidence_scorer = ConfidenceScorer() if enable_confidence else None
        self.wolfram_validator = WolframValidator(wolfram_app_id) if enable_wolfram else None
        
        # Validation thresholds by level
        self.validation_thresholds = {
            ValidationLevel.BASIC: {
                'overall_score': 0.6,
                'statistical_pass_rate': 0.5,
                'confidence_threshold': 0.5,
                'wolfram_success_rate': 0.3
            },
            ValidationLevel.STANDARD: {
                'overall_score': 0.7,
                'statistical_pass_rate': 0.6,
                'confidence_threshold': 0.6,
                'wolfram_success_rate': 0.5
            },
            ValidationLevel.COMPREHENSIVE: {
                'overall_score': 0.8,
                'statistical_pass_rate': 0.7,
                'confidence_threshold': 0.7,
                'wolfram_success_rate': 0.7
            },
            ValidationLevel.PRODUCTION: {
                'overall_score': 0.9,
                'statistical_pass_rate': 0.8,
                'confidence_threshold': 0.8,
                'wolfram_success_rate': 0.8
            }
        }
        
        # Execution statistics
        self._validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'total_execution_time': 0.0,
            'component_stats': {
                'statistical': {'count': 0, 'success': 0, 'time': 0.0},
                'confidence': {'count': 0, 'success': 0, 'time': 0.0},
                'wolfram': {'count': 0, 'success': 0, 'time': 0.0}
            }
        }
    
    def validate_analysis_results(self,
                                analysis_type: str,
                                input_data: Dict[str, Any],
                                results: Dict[str, Any],
                                validation_level: ValidationLevel = ValidationLevel.STANDARD,
                                reference_data: Optional[Dict[str, Any]] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """
        Perform comprehensive validation of analysis results
        
        Args:
            analysis_type: Type of analysis (pid_tuning, step_detection, model_identification)
            input_data: Original input data
            results: Analysis results to validate
            validation_level: Level of validation rigor
            reference_data: Optional reference data for comparison
            metadata: Additional metadata
            
        Returns:
            Comprehensive validation report
        """
        start_time = time.time()
        validation_id = f"validation_{analysis_type}_{int(time.time() * 1000)}"
        
        try:
            self.logger.info(f"Starting {validation_level.value} validation for {analysis_type}")
            
            # Execute validation components
            validation_results = {}
            
            # 1. Statistical Validation
            if self.enable_statistical:
                statistical_result = self._run_statistical_validation(
                    analysis_type, input_data, results, reference_data
                )
                validation_results['statistical'] = statistical_result
            
            # 2. Confidence Assessment
            if self.enable_confidence:
                confidence_result = self._run_confidence_assessment(
                    analysis_type, input_data, results, 
                    validation_results.get('statistical', {}).get('details', []),
                    metadata
                )
                validation_results['confidence'] = confidence_result
            
            # 3. Mathematical Validation (WolframAlpha Pro)
            if self.enable_wolfram:
                wolfram_result = self._run_wolfram_validation(
                    analysis_type, results, metadata
                )
                validation_results['wolfram'] = wolfram_result
            
            # 4. Generate comprehensive report
            report = self._generate_validation_report(
                validation_id,
                analysis_type,
                validation_level,
                validation_results,
                time.time() - start_time
            )
            
            # Update statistics
            self._update_validation_stats(report)
            
            self.logger.info(f"Validation completed: {report.overall_status.value} "
                           f"(score: {report.overall_score:.3f}) in {report.execution_time:.3f}s")
            
            return report
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Validation failed: {e}")
            
            return self._create_error_report(
                validation_id,
                analysis_type,
                validation_level,
                str(e),
                execution_time
            )
    
    def _run_statistical_validation(self,
                                  analysis_type: str,
                                  input_data: Dict[str, Any],
                                  results: Dict[str, Any],
                                  reference_data: Optional[Dict[str, Any]]) -> ValidationResult:
        """Run statistical validation component"""
        start_time = time.time()
        
        try:
            if not self.statistical_suite:
                return ValidationResult(
                    component="statistical",
                    success=False,
                    score=0.0,
                    status=ValidationStatus.ERROR,
                    details=[],
                    execution_time=0.0,
                    error_message="Statistical validation disabled"
                )
            
            # Run statistical tests
            test_results = run_statistical_validation(
                analysis_type, input_data, results, reference_data
            )
            
            # Calculate statistics
            total_tests = len(test_results)
            passed_tests = sum(1 for test in test_results if test.passed)
            pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0
            
            # Determine success
            success = pass_rate >= 0.6  # Minimum pass rate
            status = ValidationStatus.PASSED if success else ValidationStatus.FAILED
            
            execution_time = time.time() - start_time
            
            # Update component stats
            self._validation_stats['component_stats']['statistical']['count'] += 1
            if success:
                self._validation_stats['component_stats']['statistical']['success'] += 1
            self._validation_stats['component_stats']['statistical']['time'] += execution_time
            
            return ValidationResult(
                component="statistical",
                success=success,
                score=pass_rate,
                status=status,
                details=test_results,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Statistical validation failed: {e}")
            
            return ValidationResult(
                component="statistical",
                success=False,
                score=0.0,
                status=ValidationStatus.ERROR,
                details=[],
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _run_confidence_assessment(self,
                                 analysis_type: str,
                                 input_data: Dict[str, Any],
                                 results: Dict[str, Any],
                                 validation_results: List[Any],
                                 metadata: Optional[Dict[str, Any]]) -> ValidationResult:
        """Run confidence assessment component"""
        start_time = time.time()
        
        try:
            if not self.confidence_scorer:
                return ValidationResult(
                    component="confidence",
                    success=False,
                    score=0.0,
                    status=ValidationStatus.ERROR,
                    details=None,
                    execution_time=0.0,
                    error_message="Confidence assessment disabled"
                )
            
            # Assess confidence
            confidence_assessment = self.confidence_scorer.assess_confidence(
                analysis_type, input_data, results, validation_results, metadata
            )
            
            # Determine success
            success = confidence_assessment.overall_score >= 0.6
            status = ValidationStatus.PASSED if success else ValidationStatus.FAILED
            
            execution_time = time.time() - start_time
            
            # Update component stats
            self._validation_stats['component_stats']['confidence']['count'] += 1
            if success:
                self._validation_stats['component_stats']['confidence']['success'] += 1
            self._validation_stats['component_stats']['confidence']['time'] += execution_time
            
            return ValidationResult(
                component="confidence",
                success=success,
                score=confidence_assessment.overall_score,
                status=status,
                details=confidence_assessment,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Confidence assessment failed: {e}")
            
            return ValidationResult(
                component="confidence",
                success=False,
                score=0.0,
                status=ValidationStatus.ERROR,
                details=None,
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _run_wolfram_validation(self,
                              analysis_type: str,
                              results: Dict[str, Any],
                              metadata: Optional[Dict[str, Any]]) -> ValidationResult:
        """Run WolframAlpha Pro validation component"""
        start_time = time.time()
        
        try:
            if not self.wolfram_validator:
                return ValidationResult(
                    component="wolfram",
                    success=False,
                    score=0.0,
                    status=ValidationStatus.ERROR,
                    details=[],
                    execution_time=0.0,
                    error_message="WolframAlpha validation disabled"
                )
            
            # Run appropriate validation based on analysis type
            if analysis_type == "pid_tuning":
                kp = results.get('kp', 0)
                ki = results.get('ki', 0)
                kd = results.get('kd', 0)
                process_params = metadata.get('process_params') if metadata else None
                
                wolfram_results = self.wolfram_validator.validate_pid_tuning_equations(
                    kp, ki, kd, process_params
                )
                
            elif analysis_type == "step_detection":
                step_data = results.get('data', [])
                detected_params = results.get('parameters', {})
                
                wolfram_results = self.wolfram_validator.validate_step_response_analysis(
                    step_data, detected_params
                )
                
            elif analysis_type == "model_identification":
                model_params = results
                fit_metrics = metadata.get('fit_metrics', {}) if metadata else {}
                
                wolfram_results = self.wolfram_validator.validate_model_identification(
                    model_params, fit_metrics
                )
                
            else:
                # Generic validation - create minimal validation
                wolfram_results = []
                self.logger.warning(f"No specific WolframAlpha validation for {analysis_type}")
            
            # Calculate success metrics
            total_validations = len(wolfram_results)
            successful_validations = sum(1 for result in wolfram_results 
                                       if result.success and result.verification_status == 'verified')
            success_rate = successful_validations / total_validations if total_validations > 0 else 0.0
            
            # Determine success
            success = success_rate >= 0.5  # At least 50% validation success
            status = ValidationStatus.PASSED if success else ValidationStatus.FAILED
            
            execution_time = time.time() - start_time
            
            # Update component stats
            self._validation_stats['component_stats']['wolfram']['count'] += 1
            if success:
                self._validation_stats['component_stats']['wolfram']['success'] += 1
            self._validation_stats['component_stats']['wolfram']['time'] += execution_time
            
            return ValidationResult(
                component="wolfram",
                success=success,
                score=success_rate,
                status=status,
                details=wolfram_results,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"WolframAlpha validation failed: {e}")
            
            return ValidationResult(
                component="wolfram",
                success=False,
                score=0.0,
                status=ValidationStatus.ERROR,
                details=[],
                execution_time=execution_time,
                error_message=str(e)
            )
    
    def _generate_validation_report(self,
                                  validation_id: str,
                                  analysis_type: str,
                                  validation_level: ValidationLevel,
                                  validation_results: Dict[str, ValidationResult],
                                  execution_time: float) -> ValidationReport:
        """Generate comprehensive validation report"""
        try:
            # Extract component results
            statistical_result = validation_results.get('statistical')
            confidence_result = validation_results.get('confidence')
            wolfram_result = validation_results.get('wolfram')
            
            # Calculate overall score
            scores = []
            if statistical_result and statistical_result.success:
                scores.append(statistical_result.score)
            if confidence_result and confidence_result.success:
                scores.append(confidence_result.score)
            if wolfram_result and wolfram_result.success:
                scores.append(wolfram_result.score)
            
            overall_score = sum(scores) / len(scores) if scores else 0.0
            
            # Determine overall status
            thresholds = self.validation_thresholds[validation_level]
            
            if overall_score >= thresholds['overall_score']:
                # Check individual component thresholds
                statistical_ok = (not statistical_result or 
                                statistical_result.score >= thresholds['statistical_pass_rate'])
                confidence_ok = (not confidence_result or 
                               confidence_result.score >= thresholds['confidence_threshold'])
                wolfram_ok = (not wolfram_result or 
                            wolfram_result.score >= thresholds['wolfram_success_rate'])
                
                if statistical_ok and confidence_ok and wolfram_ok:
                    overall_status = ValidationStatus.PASSED
                else:
                    overall_status = ValidationStatus.WARNING
            else:
                overall_status = ValidationStatus.FAILED
            
            # Check for errors
            has_errors = any(result and result.status == ValidationStatus.ERROR 
                           for result in validation_results.values())
            if has_errors:
                overall_status = ValidationStatus.ERROR
            
            # Generate summary
            summary = self._generate_summary(
                analysis_type, validation_level, overall_status, overall_score, validation_results
            )
            
            # Collect recommendations and issues
            recommendations = []
            critical_issues = []
            
            for component, result in validation_results.items():
                if result and result.error_message:
                    critical_issues.append(f"{component.title()} validation error: {result.error_message}")
                elif result and not result.success:
                    critical_issues.append(f"{component.title()} validation failed (score: {result.score:.3f})")
            
            # Add component-specific recommendations
            if confidence_result and hasattr(confidence_result.details, 'recommendations'):
                recommendations.extend(confidence_result.details.recommendations)
            
            # Get validation details
            statistical_results = statistical_result.details if statistical_result else []
            confidence_assessment = confidence_result.details if confidence_result else None
            wolfram_results = wolfram_result.details if wolfram_result else []
            
            return ValidationReport(
                validation_id=validation_id,
                analysis_type=analysis_type,
                validation_level=validation_level,
                overall_status=overall_status,
                overall_score=overall_score,
                confidence_assessment=confidence_assessment,
                statistical_results=statistical_results,
                wolfram_results=wolfram_results,
                execution_time=execution_time,
                summary=summary,
                recommendations=recommendations,
                critical_issues=critical_issues,
                metadata={
                    'component_results': {
                        component: {
                            'success': result.success if result else False,
                            'score': result.score if result else 0.0,
                            'execution_time': result.execution_time if result else 0.0
                        }
                        for component, result in validation_results.items()
                    }
                }
            )
            
        except Exception as e:
            self.logger.error(f"Validation report generation failed: {e}")
            return self._create_error_report(
                validation_id, analysis_type, validation_level, str(e), execution_time
            )
    
    def _generate_summary(self,
                         analysis_type: str,
                         validation_level: ValidationLevel,
                         overall_status: ValidationStatus,
                         overall_score: float,
                         validation_results: Dict[str, ValidationResult]) -> str:
        """Generate validation summary"""
        try:
            component_summary = []
            
            for component, result in validation_results.items():
                if result:
                    status_text = "✅" if result.success else "❌"
                    component_summary.append(f"{component.title()}: {status_text} {result.score:.3f}")
                else:
                    component_summary.append(f"{component.title()}: ⚪ disabled")
            
            status_emoji = {
                ValidationStatus.PASSED: "✅",
                ValidationStatus.WARNING: "⚠️",
                ValidationStatus.FAILED: "❌",
                ValidationStatus.ERROR: "🔥"
            }
            
            return (f"{status_emoji.get(overall_status, '❓')} {analysis_type.title()} "
                   f"{validation_level.value} validation: {overall_status.value.upper()} "
                   f"(score: {overall_score:.3f}). Components: {', '.join(component_summary)}")
            
        except Exception:
            return f"Validation summary generation failed"
    
    def _create_error_report(self,
                           validation_id: str,
                           analysis_type: str,
                           validation_level: ValidationLevel,
                           error_msg: str,
                           execution_time: float) -> ValidationReport:
        """Create error validation report"""
        return ValidationReport(
            validation_id=validation_id,
            analysis_type=analysis_type,
            validation_level=validation_level,
            overall_status=ValidationStatus.ERROR,
            overall_score=0.0,
            confidence_assessment=None,
            statistical_results=[],
            wolfram_results=[],
            execution_time=execution_time,
            summary=f"Validation failed: {error_msg}",
            critical_issues=[f"Validation error: {error_msg}"],
            recommendations=["Resolve validation errors and retry"]
        )
    
    def _update_validation_stats(self, report: ValidationReport):
        """Update validation statistics"""
        self._validation_stats['total_validations'] += 1
        
        if report.overall_status == ValidationStatus.PASSED:
            self._validation_stats['successful_validations'] += 1
        else:
            self._validation_stats['failed_validations'] += 1
        
        self._validation_stats['total_execution_time'] += report.execution_time
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Get validation execution statistics"""
        stats = self._validation_stats.copy()
        
        if stats['total_validations'] > 0:
            stats['success_rate'] = stats['successful_validations'] / stats['total_validations']
            stats['average_execution_time'] = stats['total_execution_time'] / stats['total_validations']
        else:
            stats['success_rate'] = 0.0
            stats['average_execution_time'] = 0.0
        
        # Add component success rates
        for component, component_stats in stats['component_stats'].items():
            if component_stats['count'] > 0:
                component_stats['success_rate'] = component_stats['success'] / component_stats['count']
                component_stats['average_time'] = component_stats['time'] / component_stats['count']
            else:
                component_stats['success_rate'] = 0.0
                component_stats['average_time'] = 0.0
        
        return stats
    
    def validate_pid_tuning(self,
                           input_data: Dict[str, Any],
                           tuning_results: Dict[str, Any],
                           validation_level: ValidationLevel = ValidationLevel.STANDARD,
                           process_params: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """Convenience method for PID tuning validation"""
        metadata = {'process_params': process_params} if process_params else None
        return self.validate_analysis_results(
            "pid_tuning", input_data, tuning_results, validation_level, None, metadata
        )
    
    def validate_step_detection(self,
                              input_data: Dict[str, Any],
                              detection_results: Dict[str, Any],
                              validation_level: ValidationLevel = ValidationLevel.STANDARD) -> ValidationReport:
        """Convenience method for step detection validation"""
        return self.validate_analysis_results(
            "step_detection", input_data, detection_results, validation_level
        )
    
    def validate_model_identification(self,
                                    input_data: Dict[str, Any],
                                    model_results: Dict[str, Any],
                                    validation_level: ValidationLevel = ValidationLevel.STANDARD,
                                    fit_metrics: Optional[Dict[str, Any]] = None) -> ValidationReport:
        """Convenience method for model identification validation"""
        metadata = {'fit_metrics': fit_metrics} if fit_metrics else None
        return self.validate_analysis_results(
            "model_identification", input_data, model_results, validation_level, None, metadata
        )

# Global validation manager instance
_validation_manager: Optional[ValidationManager] = None

def get_validation_manager(enable_statistical: bool = True,
                         enable_confidence: bool = True,
                         enable_wolfram: bool = True,
                         wolfram_app_id: Optional[str] = None) -> ValidationManager:
    """
    Get global validation manager instance
    
    Args:
        enable_statistical: Enable statistical validation
        enable_confidence: Enable confidence assessment
        enable_wolfram: Enable WolframAlpha Pro validation
        wolfram_app_id: WolframAlpha App ID
        
    Returns:
        ValidationManager instance
    """
    global _validation_manager
    
    if _validation_manager is None:
        _validation_manager = ValidationManager(
            enable_statistical=enable_statistical,
            enable_confidence=enable_confidence,
            enable_wolfram=enable_wolfram,
            wolfram_app_id=wolfram_app_id
        )
    
    return _validation_manager

# Export main components
__all__ = [
    'ValidationManager',
    'ValidationReport',
    'ValidationResult',
    'ValidationLevel',
    'ValidationStatus',
    'get_validation_manager'
] 