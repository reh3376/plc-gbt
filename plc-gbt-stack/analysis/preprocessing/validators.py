#!/usr/bin/env python3
"""
Industrial Data Validators - Phase 22.1.2
==========================================

Advanced validation system for industrial control data with specialized rules
for control loops, process variables, and time-series data quality assessment.

Features:
- Control loop specific validation (PV, SP, CV relationships)
- Time-series data consistency checks
- Signal quality assessment (noise, outliers, drift)
- Real-time validation for streaming data
- Configurable validation rules and thresholds
- Integration with existing DataValidator patterns

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.2 - Enhanced Data Preprocessing (Validators)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

# Import existing validation modules
try:
    from ...scripts.ai.modules.data import DataValidator
    MODULAR_DATA_AVAILABLE = True
except ImportError:
    MODULAR_DATA_AVAILABLE = False
    logging.warning("⚠️ Existing data modules not available - using standalone implementation")

# Import PID analysis for control-specific validation
try:
    from ...docs.context.pid_analysis_bundle import infer_interval
    PID_BUNDLE_AVAILABLE = True
except ImportError:
    PID_BUNDLE_AVAILABLE = False
    logging.warning("⚠️ PID analysis bundle not available")

# Setup logging
logger = logging.getLogger(__name__)

class ValidationSeverity(Enum):
    """Severity levels for validation issues"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ValidationCategory(Enum):
    """Categories of validation checks"""
    DATA_STRUCTURE = "data_structure"
    DATA_QUALITY = "data_quality"
    CONTROL_LOGIC = "control_logic"
    TIME_SERIES = "time_series"
    SIGNAL_QUALITY = "signal_quality"
    PROCESS_PHYSICS = "process_physics"
    SAFETY = "safety"

@dataclass
class ValidationRule:
    """Definition of a validation rule"""
    name: str
    category: ValidationCategory
    severity: ValidationSeverity
    description: str
    check_function: Callable[[pd.DataFrame], 'ValidationResult']
    enabled: bool = True
    threshold: Optional[float] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationResult:
    """Result of a validation check"""
    rule_name: str
    category: ValidationCategory
    severity: ValidationSeverity
    passed: bool
    score: float  # 0.0 to 1.0
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    affected_columns: List[str] = field(default_factory=list)
    affected_rows: List[int] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    data_shape: Tuple[int, int]
    validation_results: List[ValidationResult]
    overall_score: float
    passed_checks: int
    failed_checks: int
    warnings: int
    errors: int
    critical_issues: int
    summary: Dict[str, Any]
    generated_at: datetime = field(default_factory=datetime.now)

    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationResult]:
        """Get validation results by severity level"""
        return [r for r in self.validation_results if r.severity == severity]

    def get_issues_by_category(self, category: ValidationCategory) -> List[ValidationResult]:
        """Get validation results by category"""
        return [r for r in self.validation_results if r.category == category]

class BaseValidator(ABC):
    """Abstract base class for validators"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.rules: List[ValidationRule] = []
        self._initialize_rules()

    @abstractmethod
    def _initialize_rules(self):
        """Initialize validation rules"""
        pass

    def add_rule(self, rule: ValidationRule):
        """Add a validation rule"""
        self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove a validation rule by name"""
        self.rules = [r for r in self.rules if r.name != rule_name]

    def validate(self, data: pd.DataFrame) -> ValidationReport:
        """Run all validation rules on the data"""
        results = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            try:
                result = rule.check_function(data)
                results.append(result)
            except Exception as e:
                error_result = ValidationResult(
                    rule_name=rule.name,
                    category=rule.category,
                    severity=ValidationSeverity.ERROR,
                    passed=False,
                    score=0.0,
                    message=f"Validation rule failed: {str(e)}",
                    details={"exception": str(e)}
                )
                results.append(error_result)
                self.logger.error(f"Validation rule '{rule.name}' failed: {e}")

        return self._generate_report(data, results)

    def _generate_report(self, data: pd.DataFrame, results: List[ValidationResult]) -> ValidationReport:
        """Generate validation report from results"""
        passed_checks = sum(1 for r in results if r.passed)
        failed_checks = len(results) - passed_checks
        warnings = sum(1 for r in results if r.severity == ValidationSeverity.WARNING)
        errors = sum(1 for r in results if r.severity == ValidationSeverity.ERROR)
        critical_issues = sum(1 for r in results if r.severity == ValidationSeverity.CRITICAL)

        # Calculate overall score
        if results:
            overall_score = sum(r.score for r in results) / len(results)
        else:
            overall_score = 0.0

        summary = {
            "total_rules": len(results),
            "data_quality_score": overall_score,
            "completeness": self._calculate_completeness(data),
            "consistency": self._calculate_consistency(results),
            "reliability": self._calculate_reliability(results)
        }

        return ValidationReport(
            data_shape=data.shape,
            validation_results=results,
            overall_score=overall_score,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warnings=warnings,
            errors=errors,
            critical_issues=critical_issues,
            summary=summary
        )

    def _calculate_completeness(self, data: pd.DataFrame) -> float:
        """Calculate data completeness score"""
        if data.empty:
            return 0.0
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        return 1.0 - (missing_cells / total_cells)

    def _calculate_consistency(self, results: List[ValidationResult]) -> float:
        """Calculate consistency score from validation results"""
        structure_results = [r for r in results if r.category == ValidationCategory.DATA_STRUCTURE]
        if not structure_results:
            return 1.0
        return sum(r.score for r in structure_results) / len(structure_results)

    def _calculate_reliability(self, results: List[ValidationResult]) -> float:
        """Calculate reliability score from validation results"""
        quality_results = [r for r in results if r.category == ValidationCategory.DATA_QUALITY]
        if not quality_results:
            return 1.0
        return sum(r.score for r in quality_results) / len(quality_results)

class IndustrialDataValidator(BaseValidator):
    """General industrial data validator"""

    def __init__(self):
        super().__init__("IndustrialDataValidator")

    def _initialize_rules(self):
        """Initialize industrial data validation rules"""

        # Data structure rules
        self.add_rule(ValidationRule(
            name="non_empty_data",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.CRITICAL,
            description="Data must not be empty",
            check_function=self._check_non_empty
        ))

        self.add_rule(ValidationRule(
            name="minimum_rows",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.WARNING,
            description="Data should have minimum number of rows for analysis",
            check_function=self._check_minimum_rows,
            threshold=50
        ))

        self.add_rule(ValidationRule(
            name="numeric_columns",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.ERROR,
            description="Key columns should be numeric",
            check_function=self._check_numeric_columns
        ))

        # Data quality rules
        self.add_rule(ValidationRule(
            name="missing_data_threshold",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.WARNING,
            description="Missing data should be within acceptable limits",
            check_function=self._check_missing_data,
            threshold=0.05  # 5% maximum missing data
        ))

        self.add_rule(ValidationRule(
            name="duplicate_detection",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.WARNING,
            description="Check for duplicate records",
            check_function=self._check_duplicates
        ))

        self.add_rule(ValidationRule(
            name="outlier_detection",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.INFO,
            description="Detect statistical outliers",
            check_function=self._check_outliers,
            threshold=3.0  # Z-score threshold
        ))

        # Time series rules
        self.add_rule(ValidationRule(
            name="time_monotonicity",
            category=ValidationCategory.TIME_SERIES,
            severity=ValidationSeverity.ERROR,
            description="Time series should be monotonically increasing",
            check_function=self._check_time_monotonicity
        ))

        self.add_rule(ValidationRule(
            name="sampling_consistency",
            category=ValidationCategory.TIME_SERIES,
            severity=ValidationSeverity.WARNING,
            description="Sampling intervals should be consistent",
            check_function=self._check_sampling_consistency
        ))

    def _check_non_empty(self, data: pd.DataFrame) -> ValidationResult:
        """Check if data is not empty"""
        passed = not data.empty
        score = 1.0 if passed else 0.0

        return ValidationResult(
            rule_name="non_empty_data",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.CRITICAL,
            passed=passed,
            score=score,
            message="Data is not empty" if passed else "Data is empty",
            details={"row_count": len(data), "column_count": len(data.columns)}
        )

    def _check_minimum_rows(self, data: pd.DataFrame) -> ValidationResult:
        """Check if data has minimum number of rows"""
        min_rows = 50  # Default threshold
        passed = len(data) >= min_rows
        score = min(len(data) / min_rows, 1.0) if len(data) > 0 else 0.0

        return ValidationResult(
            rule_name="minimum_rows",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.WARNING,
            passed=passed,
            score=score,
            message=f"Data has {len(data)} rows (minimum: {min_rows})",
            details={"row_count": len(data), "minimum_required": min_rows},
            recommendations=["Consider collecting more data for better analysis"] if not passed else []
        )

    def _check_numeric_columns(self, data: pd.DataFrame) -> ValidationResult:
        """Check if key columns are numeric"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
        non_numeric_cols = data.select_dtypes(exclude=[np.number]).columns.tolist()

        # Remove obvious non-numeric columns
        expected_non_numeric = ['timestamp', 'time', 'datetime', 'date', 'name', 'tag', 'description']
        unexpected_non_numeric = [col for col in non_numeric_cols
                                 if not any(expected in col.lower() for expected in expected_non_numeric)]

        passed = len(unexpected_non_numeric) == 0
        score = len(numeric_cols) / len(data.columns) if len(data.columns) > 0 else 0.0

        return ValidationResult(
            rule_name="numeric_columns",
            category=ValidationCategory.DATA_STRUCTURE,
            severity=ValidationSeverity.ERROR,
            passed=passed,
            score=score,
            message=f"Found {len(numeric_cols)} numeric columns, {len(unexpected_non_numeric)} unexpected non-numeric",
            details={
                "numeric_columns": numeric_cols,
                "non_numeric_columns": non_numeric_cols,
                "unexpected_non_numeric": unexpected_non_numeric
            },
            affected_columns=unexpected_non_numeric,
            recommendations=["Convert text columns to numeric where appropriate"] if unexpected_non_numeric else []
        )

    def _check_missing_data(self, data: pd.DataFrame) -> ValidationResult:
        """Check missing data percentage"""
        if data.empty:
            return ValidationResult(
                rule_name="missing_data_threshold",
                category=ValidationCategory.DATA_QUALITY,
                severity=ValidationSeverity.WARNING,
                passed=False,
                score=0.0,
                message="Cannot check missing data on empty dataset"
            )

        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        missing_ratio = missing_cells / total_cells
        threshold = 0.05  # 5%

        passed = missing_ratio <= threshold
        score = max(0.0, 1.0 - (missing_ratio / threshold))

        return ValidationResult(
            rule_name="missing_data_threshold",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.WARNING,
            passed=passed,
            score=score,
            message=f"Missing data: {missing_ratio:.2%} (threshold: {threshold:.2%})",
            details={
                "missing_cells": missing_cells,
                "total_cells": total_cells,
                "missing_ratio": missing_ratio,
                "threshold": threshold
            },
            recommendations=["Investigate data collection issues", "Consider interpolation for missing values"] if not passed else []
        )

    def _check_duplicates(self, data: pd.DataFrame) -> ValidationResult:
        """Check for duplicate records"""
        if data.empty:
            return ValidationResult(
                rule_name="duplicate_detection",
                category=ValidationCategory.DATA_QUALITY,
                severity=ValidationSeverity.WARNING,
                passed=True,
                score=1.0,
                message="No duplicates found (empty dataset)"
            )

        duplicate_count = data.duplicated().sum()
        duplicate_ratio = duplicate_count / len(data)

        passed = duplicate_count == 0
        score = max(0.0, 1.0 - duplicate_ratio)

        return ValidationResult(
            rule_name="duplicate_detection",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.WARNING,
            passed=passed,
            score=score,
            message=f"Found {duplicate_count} duplicate records ({duplicate_ratio:.2%})",
            details={
                "duplicate_count": duplicate_count,
                "total_records": len(data),
                "duplicate_ratio": duplicate_ratio
            },
            recommendations=["Remove duplicate records", "Check data collection process"] if not passed else []
        )

    def _check_outliers(self, data: pd.DataFrame) -> ValidationResult:
        """Check for statistical outliers using Z-score"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return ValidationResult(
                rule_name="outlier_detection",
                category=ValidationCategory.DATA_QUALITY,
                severity=ValidationSeverity.INFO,
                passed=True,
                score=1.0,
                message="No numeric columns for outlier detection"
            )

        threshold = 3.0
        outlier_counts = {}
        total_outliers = 0

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                z_scores = np.abs(stats.zscore(col_data))
                outliers = (z_scores > threshold).sum()
                outlier_counts[col] = outliers
                total_outliers += outliers

        total_values = sum(len(data[col].dropna()) for col in numeric_cols)
        outlier_ratio = total_outliers / total_values if total_values > 0 else 0.0

        # Consider up to 5% outliers as acceptable
        passed = outlier_ratio <= 0.05
        score = max(0.0, 1.0 - (outlier_ratio / 0.05))

        return ValidationResult(
            rule_name="outlier_detection",
            category=ValidationCategory.DATA_QUALITY,
            severity=ValidationSeverity.INFO,
            passed=passed,
            score=score,
            message=f"Found {total_outliers} outliers ({outlier_ratio:.2%})",
            details={
                "outlier_counts_by_column": outlier_counts,
                "total_outliers": total_outliers,
                "outlier_ratio": outlier_ratio,
                "z_score_threshold": threshold
            },
            recommendations=["Investigate extreme values", "Consider data cleaning"] if outlier_ratio > 0.1 else []
        )

    def _check_time_monotonicity(self, data: pd.DataFrame) -> ValidationResult:
        """Check if time series is monotonically increasing"""
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]

        if not time_columns:
            return ValidationResult(
                rule_name="time_monotonicity",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=True,
                score=1.0,
                message="No time columns found for monotonicity check"
            )

        # Check first time column
        time_col = time_columns[0]
        try:
            time_series = pd.to_datetime(data[time_col])
            is_monotonic = time_series.is_monotonic_increasing

            if is_monotonic:
                score = 1.0
                message = f"Time series '{time_col}' is monotonically increasing"
            else:
                # Count backwards steps
                diff = time_series.diff()
                backwards_steps = (diff < timedelta(0)).sum()
                score = max(0.0, 1.0 - (backwards_steps / len(time_series)))
                message = f"Time series '{time_col}' has {backwards_steps} backwards steps"

            return ValidationResult(
                rule_name="time_monotonicity",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=is_monotonic,
                score=score,
                message=message,
                details={
                    "time_column": time_col,
                    "is_monotonic": is_monotonic,
                    "backwards_steps": backwards_steps if not is_monotonic else 0
                },
                affected_columns=[time_col],
                recommendations=["Sort data by timestamp", "Check data collection order"] if not is_monotonic else []
            )

        except Exception as e:
            return ValidationResult(
                rule_name="time_monotonicity",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=False,
                score=0.0,
                message=f"Failed to parse time column '{time_col}': {str(e)}",
                details={"error": str(e), "time_column": time_col}
            )

    def _check_sampling_consistency(self, data: pd.DataFrame) -> ValidationResult:
        """Check consistency of sampling intervals"""
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]

        if not time_columns or len(data) < 3:
            return ValidationResult(
                rule_name="sampling_consistency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=True,
                score=1.0,
                message="Insufficient data for sampling consistency check"
            )

        time_col = time_columns[0]
        try:
            time_series = pd.to_datetime(data[time_col])
            intervals = time_series.diff().dropna()

            if len(intervals) == 0:
                return ValidationResult(
                    rule_name="sampling_consistency",
                    category=ValidationCategory.TIME_SERIES,
                    severity=ValidationSeverity.WARNING,
                    passed=True,
                    score=1.0,
                    message="No intervals to check"
                )

            # Convert to seconds for analysis
            interval_seconds = intervals.dt.total_seconds()

            # Use PID bundle if available for interval inference
            if PID_BUNDLE_AVAILABLE:
                try:
                    modal_interval = infer_interval(time_series.astype('int64') / 1e9)
                except:
                    modal_interval = interval_seconds.mode().iloc[0] if not interval_seconds.mode().empty else interval_seconds.median()
            else:
                modal_interval = interval_seconds.mode().iloc[0] if not interval_seconds.mode().empty else interval_seconds.median()

            # Calculate consistency score
            deviations = np.abs(interval_seconds - modal_interval)
            relative_deviations = deviations / modal_interval

            # Allow up to 10% deviation as acceptable
            acceptable_deviation = 0.1
            consistent_count = (relative_deviations <= acceptable_deviation).sum()
            consistency_ratio = consistent_count / len(interval_seconds)

            passed = consistency_ratio >= 0.8  # 80% of intervals should be consistent
            score = consistency_ratio

            return ValidationResult(
                rule_name="sampling_consistency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=passed,
                score=score,
                message=f"Sampling consistency: {consistency_ratio:.1%} (modal interval: {modal_interval:.1f}s)",
                details={
                    "modal_interval_seconds": modal_interval,
                    "consistency_ratio": consistency_ratio,
                    "total_intervals": len(interval_seconds),
                    "consistent_intervals": consistent_count,
                    "acceptable_deviation": acceptable_deviation
                },
                recommendations=["Check data collection timing", "Consider resampling data"] if not passed else []
            )

        except Exception as e:
            return ValidationResult(
                rule_name="sampling_consistency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=False,
                score=0.0,
                message=f"Failed to check sampling consistency: {str(e)}",
                details={"error": str(e)}
            )

class ControlLoopValidator(BaseValidator):
    """Specialized validator for control loop data"""

    def __init__(self):
        super().__init__("ControlLoopValidator")

    def _initialize_rules(self):
        """Initialize control loop specific validation rules"""

        # Control variable presence
        self.add_rule(ValidationRule(
            name="control_variables_present",
            category=ValidationCategory.CONTROL_LOGIC,
            severity=ValidationSeverity.CRITICAL,
            description="Essential control variables (PV, SP, CV) should be present",
            check_function=self._check_control_variables
        ))

        # Control variable relationships
        self.add_rule(ValidationRule(
            name="control_logic_consistency",
            category=ValidationCategory.CONTROL_LOGIC,
            severity=ValidationSeverity.ERROR,
            description="Control variables should show logical relationships",
            check_function=self._check_control_logic
        ))

        # Signal quality checks
        self.add_rule(ValidationRule(
            name="signal_noise_level",
            category=ValidationCategory.SIGNAL_QUALITY,
            severity=ValidationSeverity.WARNING,
            description="Signal noise should be within acceptable limits",
            check_function=self._check_signal_noise
        ))

        # Process physics checks
        self.add_rule(ValidationRule(
            name="process_variable_ranges",
            category=ValidationCategory.PROCESS_PHYSICS,
            severity=ValidationSeverity.ERROR,
            description="Process variables should be within physically reasonable ranges",
            check_function=self._check_variable_ranges
        ))

        # Safety checks
        self.add_rule(ValidationRule(
            name="safety_limits",
            category=ValidationCategory.SAFETY,
            severity=ValidationSeverity.CRITICAL,
            description="Process variables should not exceed safety limits",
            check_function=self._check_safety_limits
        ))

    def _check_control_variables(self, data: pd.DataFrame) -> ValidationResult:
        """Check presence of essential control variables"""
        # Common control variable patterns
        pv_patterns = ['pv', 'process_variable', 'measurement', 'sensor']
        sp_patterns = ['sp', 'setpoint', 'set_point', 'target']
        cv_patterns = ['cv', 'control_variable', 'output', 'manipulated']

        columns_lower = [col.lower() for col in data.columns]

        found_pv = any(any(pattern in col for pattern in pv_patterns) for col in columns_lower)
        found_sp = any(any(pattern in col for pattern in sp_patterns) for col in columns_lower)
        found_cv = any(any(pattern in col for pattern in cv_patterns) for col in columns_lower)

        found_variables = sum([found_pv, found_sp, found_cv])
        passed = found_variables >= 2  # At least PV and one other
        score = found_variables / 3.0

        details = {
            "found_pv": found_pv,
            "found_sp": found_sp,
            "found_cv": found_cv,
            "total_found": found_variables,
            "columns": list(data.columns)
        }

        if found_variables == 3:
            message = "All essential control variables found (PV, SP, CV)"
        elif found_variables == 2:
            message = "Two control variables found - missing one essential variable"
        elif found_variables == 1:
            message = "Only one control variable found - missing multiple essential variables"
        else:
            message = "No control variables detected - check column naming"

        recommendations = []
        if not found_pv:
            recommendations.append("Add process variable (PV) data")
        if not found_sp:
            recommendations.append("Add setpoint (SP) data")
        if not found_cv:
            recommendations.append("Add control variable (CV) data")

        return ValidationResult(
            rule_name="control_variables_present",
            category=ValidationCategory.CONTROL_LOGIC,
            severity=ValidationSeverity.CRITICAL,
            passed=passed,
            score=score,
            message=message,
            details=details,
            recommendations=recommendations
        )

    def _check_control_logic(self, data: pd.DataFrame) -> ValidationResult:
        """Check logical consistency of control variables"""
        # This is a simplified check - would need more sophisticated analysis
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) < 2:
            return ValidationResult(
                rule_name="control_logic_consistency",
                category=ValidationCategory.CONTROL_LOGIC,
                severity=ValidationSeverity.ERROR,
                passed=True,
                score=1.0,
                message="Insufficient numeric columns for control logic check"
            )

        # Look for correlations between variables (basic check)
        correlations = data[numeric_cols].corr()

        # Count reasonable correlations (not too high, not too low)
        reasonable_correlations = 0
        total_pairs = 0

        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                corr_value = abs(correlations.iloc[i, j])
                if not np.isnan(corr_value):
                    total_pairs += 1
                    # Reasonable correlation range for control variables
                    if 0.1 <= corr_value <= 0.9:
                        reasonable_correlations += 1

        if total_pairs > 0:
            score = reasonable_correlations / total_pairs
            passed = score >= 0.5
        else:
            score = 0.0
            passed = False

        return ValidationResult(
            rule_name="control_logic_consistency",
            category=ValidationCategory.CONTROL_LOGIC,
            severity=ValidationSeverity.ERROR,
            passed=passed,
            score=score,
            message=f"Control logic consistency: {score:.1%}",
            details={
                "reasonable_correlations": reasonable_correlations,
                "total_pairs": total_pairs,
                "correlation_matrix": correlations.round(3).to_dict()
            },
            recommendations=["Verify control loop configuration", "Check for sensor malfunctions"] if not passed else []
        )

    def _check_signal_noise(self, data: pd.DataFrame) -> ValidationResult:
        """Check signal noise levels"""
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) == 0:
            return ValidationResult(
                rule_name="signal_noise_level",
                category=ValidationCategory.SIGNAL_QUALITY,
                severity=ValidationSeverity.WARNING,
                passed=True,
                score=1.0,
                message="No numeric columns for noise analysis"
            )

        noise_scores = {}
        total_score = 0.0

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 10:
                # Calculate signal-to-noise ratio
                signal_std = col_data.std()
                signal_mean = abs(col_data.mean())

                if signal_mean > 0:
                    # Calculate noise using first-order differences
                    noise_std = col_data.diff().std() / np.sqrt(2)  # Normalize for first difference
                    snr = signal_std / (noise_std + 1e-10)

                    # Score based on SNR (higher is better)
                    noise_score = min(snr / 10.0, 1.0)  # Normalize to 0-1
                    noise_scores[col] = noise_score
                    total_score += noise_score

        if noise_scores:
            average_score = total_score / len(noise_scores)
            passed = average_score >= 0.5
        else:
            average_score = 0.0
            passed = False

        return ValidationResult(
            rule_name="signal_noise_level",
            category=ValidationCategory.SIGNAL_QUALITY,
            severity=ValidationSeverity.WARNING,
            passed=passed,
            score=average_score,
            message=f"Average signal quality score: {average_score:.2f}",
            details={"noise_scores_by_column": noise_scores},
            recommendations=["Check sensor calibration", "Investigate electrical noise sources"] if not passed else []
        )

    def _check_variable_ranges(self, data: pd.DataFrame) -> ValidationResult:
        """Check if variables are within reasonable ranges"""
        # This would need domain-specific knowledge about typical ranges
        # For now, do basic sanity checks

        numeric_cols = data.select_dtypes(include=[np.number]).columns
        range_issues = []

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                min_val = col_data.min()
                max_val = col_data.max()

                # Basic sanity checks
                if min_val == max_val:
                    range_issues.append(f"{col}: No variation (constant value)")
                elif min_val < -1000000 or max_val > 1000000:
                    range_issues.append(f"{col}: Extreme values detected")
                elif np.isinf(min_val) or np.isinf(max_val):
                    range_issues.append(f"{col}: Infinite values detected")

        passed = len(range_issues) == 0
        score = max(0.0, 1.0 - (len(range_issues) / len(numeric_cols))) if numeric_cols else 1.0

        return ValidationResult(
            rule_name="process_variable_ranges",
            category=ValidationCategory.PROCESS_PHYSICS,
            severity=ValidationSeverity.ERROR,
            passed=passed,
            score=score,
            message=f"Range validation: {len(range_issues)} issues found",
            details={"range_issues": range_issues},
            recommendations=["Investigate extreme values", "Check sensor calibration"] if range_issues else []
        )

    def _check_safety_limits(self, data: pd.DataFrame) -> ValidationResult:
        """Check safety limits - simplified implementation"""
        # In a real system, this would check against configured safety limits
        # For now, just check for extreme outliers

        numeric_cols = data.select_dtypes(include=[np.number]).columns
        safety_violations = []

        for col in numeric_cols:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                # Use 6-sigma as extreme safety threshold
                mean_val = col_data.mean()
                std_val = col_data.std()

                if std_val > 0:
                    z_scores = np.abs((col_data - mean_val) / std_val)
                    extreme_count = (z_scores > 6).sum()

                    if extreme_count > 0:
                        safety_violations.append(f"{col}: {extreme_count} extreme values")

        passed = len(safety_violations) == 0
        score = 1.0 if passed else 0.5  # Safety is critical

        return ValidationResult(
            rule_name="safety_limits",
            category=ValidationCategory.SAFETY,
            severity=ValidationSeverity.CRITICAL,
            passed=passed,
            score=score,
            message=f"Safety check: {len(safety_violations)} potential violations",
            details={"safety_violations": safety_violations},
            recommendations=["Immediate investigation required for safety violations"] if safety_violations else []
        )

class RealTimeValidator(BaseValidator):
    """Validator for real-time streaming data"""

    def __init__(self):
        super().__init__("RealTimeValidator")
        self.last_validation_time = datetime.now()
        self.validation_history = []

    def _initialize_rules(self):
        """Initialize real-time validation rules"""

        self.add_rule(ValidationRule(
            name="data_freshness",
            category=ValidationCategory.TIME_SERIES,
            severity=ValidationSeverity.WARNING,
            description="Data should be recent for real-time processing",
            check_function=self._check_data_freshness,
            threshold=300  # 5 minutes
        ))

        self.add_rule(ValidationRule(
            name="update_frequency",
            category=ValidationCategory.TIME_SERIES,
            severity=ValidationSeverity.ERROR,
            description="Data updates should meet frequency requirements",
            check_function=self._check_update_frequency
        ))

    def _check_data_freshness(self, data: pd.DataFrame) -> ValidationResult:
        """Check if data is fresh enough for real-time processing"""
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]

        if not time_columns or data.empty:
            return ValidationResult(
                rule_name="data_freshness",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=False,
                score=0.0,
                message="No time data for freshness check"
            )

        try:
            time_col = time_columns[0]
            latest_time = pd.to_datetime(data[time_col]).max()
            current_time = datetime.now()

            # Handle timezone-naive datetime
            if latest_time.tz is None:
                current_time = current_time.replace(tzinfo=None)

            age_seconds = (current_time - latest_time).total_seconds()
            threshold = 300  # 5 minutes

            passed = age_seconds <= threshold
            score = max(0.0, 1.0 - (age_seconds / (threshold * 2)))  # Gradual degradation

            return ValidationResult(
                rule_name="data_freshness",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=passed,
                score=score,
                message=f"Data age: {age_seconds:.0f} seconds (threshold: {threshold}s)",
                details={
                    "latest_timestamp": latest_time,
                    "current_time": current_time,
                    "age_seconds": age_seconds,
                    "threshold_seconds": threshold
                },
                recommendations=["Check data source connectivity", "Verify data collection process"] if not passed else []
            )

        except Exception as e:
            return ValidationResult(
                rule_name="data_freshness",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.WARNING,
                passed=False,
                score=0.0,
                message=f"Failed to check data freshness: {str(e)}"
            )

    def _check_update_frequency(self, data: pd.DataFrame) -> ValidationResult:
        """Check data update frequency"""
        if len(data) < 2:
            return ValidationResult(
                rule_name="update_frequency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=False,
                score=0.0,
                message="Insufficient data for frequency check"
            )

        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]

        if not time_columns:
            return ValidationResult(
                rule_name="update_frequency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=False,
                score=0.0,
                message="No time column for frequency check"
            )

        try:
            time_col = time_columns[0]
            time_series = pd.to_datetime(data[time_col])
            intervals = time_series.diff().dropna()

            if len(intervals) == 0:
                return ValidationResult(
                    rule_name="update_frequency",
                    category=ValidationCategory.TIME_SERIES,
                    severity=ValidationSeverity.ERROR,
                    passed=False,
                    score=0.0,
                    message="No intervals found"
                )

            # Calculate average update frequency
            avg_interval = intervals.mean().total_seconds()
            frequency_hz = 1.0 / avg_interval if avg_interval > 0 else 0.0

            # Expect at least 0.1 Hz (10 second intervals) for real-time
            min_frequency = 0.1
            passed = frequency_hz >= min_frequency
            score = min(frequency_hz / min_frequency, 1.0)

            return ValidationResult(
                rule_name="update_frequency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=passed,
                score=score,
                message=f"Update frequency: {frequency_hz:.3f} Hz (minimum: {min_frequency} Hz)",
                details={
                    "frequency_hz": frequency_hz,
                    "average_interval_seconds": avg_interval,
                    "minimum_frequency_hz": min_frequency
                },
                recommendations=["Increase data collection frequency", "Check sampling configuration"] if not passed else []
            )

        except Exception as e:
            return ValidationResult(
                rule_name="update_frequency",
                category=ValidationCategory.TIME_SERIES,
                severity=ValidationSeverity.ERROR,
                passed=False,
                score=0.0,
                message=f"Failed to check update frequency: {str(e)}"
            )
