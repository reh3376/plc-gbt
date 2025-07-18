#!/usr/bin/env python3
"""
Data Quality Assessment & Improvement - Phase 22.1.2
====================================================

Advanced data quality assessment and improvement tools specifically designed
for industrial control loop data with comprehensive quality metrics and
automated improvement suggestions.

Features:
- Multi-dimensional quality assessment (completeness, accuracy, consistency)
- Control-specific quality metrics (signal quality, control performance)
- Automated quality improvement recommendations
- Real-time quality monitoring capabilities
- Integration with existing validation frameworks

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.2 - Enhanced Data Preprocessing (Quality)
"""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import warnings
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import IsolationForest
import time

# Setup logging
logger = logging.getLogger(__name__)

class QualityDimension(Enum):
    """Data quality dimensions"""
    COMPLETENESS = "completeness"      # Presence of data
    ACCURACY = "accuracy"              # Correctness of values
    CONSISTENCY = "consistency"        # Internal consistency
    VALIDITY = "validity"              # Conformance to rules
    TIMELINESS = "timeliness"          # Data freshness
    UNIQUENESS = "uniqueness"          # Absence of duplicates
    SIGNAL_QUALITY = "signal_quality"  # Industrial signal quality
    CONTROL_PERFORMANCE = "control_performance"  # Control loop performance

@dataclass
class QualityThresholds:
    """Quality thresholds for assessment"""
    completeness_min: float = 0.95        # 95% completeness required
    accuracy_min: float = 0.90            # 90% accuracy required
    consistency_min: float = 0.85         # 85% consistency required
    validity_min: float = 0.90            # 90% validity required
    timeliness_max_age_hours: float = 24  # Data should be < 24 hours old
    uniqueness_min: float = 0.95          # 95% unique records required
    signal_to_noise_min: float = 3.0      # Minimum SNR ratio
    control_performance_min: float = 0.70 # 70% control performance

@dataclass 
class QualityMetrics:
    """Comprehensive quality metrics for a dataset"""
    # Basic quality dimensions
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    consistency_score: float = 0.0
    validity_score: float = 0.0
    timeliness_score: float = 0.0
    uniqueness_score: float = 0.0
    
    # Industrial-specific quality metrics
    signal_quality_score: float = 0.0
    control_performance_score: float = 0.0
    
    # Overall scores
    overall_score: float = 0.0
    
    # Detailed metrics
    missing_data_percentage: float = 0.0
    duplicate_records_count: int = 0
    outlier_percentage: float = 0.0
    data_age_hours: float = 0.0
    
    # Signal quality metrics
    average_snr: float = 0.0
    noise_level: float = 0.0
    signal_stability: float = 0.0
    
    # Control performance metrics
    control_error_metrics: Dict[str, float] = field(default_factory=dict)
    setpoint_tracking_performance: float = 0.0
    disturbance_rejection_performance: float = 0.0
    
    # Assessment timestamp
    assessed_at: datetime = field(default_factory=datetime.now)

@dataclass
class QualityIssue:
    """Individual quality issue identification"""
    dimension: QualityDimension
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_columns: List[str] = field(default_factory=list)
    affected_rows: List[int] = field(default_factory=list)
    recommendation: str = ""
    estimated_impact: float = 0.0  # 0.0 to 1.0

@dataclass
class QualityReport:
    """Comprehensive quality assessment report"""
    dataset_info: Dict[str, Any]
    quality_metrics: QualityMetrics
    quality_issues: List[QualityIssue]
    improvement_recommendations: List[str]
    processing_suggestions: List[str]
    assessment_summary: str
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_critical_issues(self) -> List[QualityIssue]:
        """Get critical quality issues"""
        return [issue for issue in self.quality_issues if issue.severity == "critical"]
    
    def get_issues_by_dimension(self, dimension: QualityDimension) -> List[QualityIssue]:
        """Get issues by quality dimension"""
        return [issue for issue in self.quality_issues if issue.dimension == dimension]

class DataQualityAssessor:
    """
    Comprehensive data quality assessor for industrial control data
    """
    
    def __init__(self, thresholds: Optional[QualityThresholds] = None):
        self.thresholds = thresholds or QualityThresholds()
        self.logger = logging.getLogger(f"{__name__}.DataQualityAssessor")
    
    def assess_quality(self, data: pd.DataFrame, 
                      control_variables: Optional[Dict[str, str]] = None) -> QualityReport:
        """
        Perform comprehensive quality assessment
        
        Args:
            data: DataFrame to assess
            control_variables: Dict mapping control variable types to column names
            
        Returns:
            Complete quality report
        """
        start_time = time.time()
        
        # Initialize metrics and issues
        metrics = QualityMetrics()
        issues = []
        
        # Dataset information
        dataset_info = {
            "row_count": len(data),
            "column_count": len(data.columns),
            "numeric_columns": len(data.select_dtypes(include=[np.number]).columns),
            "memory_usage_mb": data.memory_usage(deep=True).sum() / 1024 / 1024,
            "assessment_duration": 0.0
        }
        
        try:
            # Assess each quality dimension
            metrics.completeness_score, completeness_issues = self._assess_completeness(data)
            issues.extend(completeness_issues)
            
            metrics.accuracy_score, accuracy_issues = self._assess_accuracy(data)
            issues.extend(accuracy_issues)
            
            metrics.consistency_score, consistency_issues = self._assess_consistency(data)
            issues.extend(consistency_issues)
            
            metrics.validity_score, validity_issues = self._assess_validity(data)
            issues.extend(validity_issues)
            
            metrics.timeliness_score, timeliness_issues = self._assess_timeliness(data)
            issues.extend(timeliness_issues)
            
            metrics.uniqueness_score, uniqueness_issues = self._assess_uniqueness(data)
            issues.extend(uniqueness_issues)
            
            # Industrial-specific assessments
            metrics.signal_quality_score, signal_issues = self._assess_signal_quality(data)
            issues.extend(signal_issues)
            
            if control_variables:
                metrics.control_performance_score, control_issues = self._assess_control_performance(
                    data, control_variables)
                issues.extend(control_issues)
            
            # Calculate overall score
            dimension_scores = [
                metrics.completeness_score,
                metrics.accuracy_score,
                metrics.consistency_score,
                metrics.validity_score,
                metrics.timeliness_score,
                metrics.uniqueness_score,
                metrics.signal_quality_score
            ]
            
            if control_variables:
                dimension_scores.append(metrics.control_performance_score)
            
            metrics.overall_score = np.mean(dimension_scores)
            
            # Generate improvement recommendations
            improvement_recommendations = self._generate_improvement_recommendations(issues)
            processing_suggestions = self._generate_processing_suggestions(metrics, issues)
            
            # Create assessment summary
            assessment_summary = self._create_assessment_summary(metrics, issues)
            
        except Exception as e:
            self.logger.error(f"Quality assessment failed: {e}")
            assessment_summary = f"Quality assessment failed: {str(e)}"
            improvement_recommendations = ["Fix data loading issues before quality assessment"]
            processing_suggestions = []
        
        # Finalize dataset info
        dataset_info["assessment_duration"] = time.time() - start_time
        
        return QualityReport(
            dataset_info=dataset_info,
            quality_metrics=metrics,
            quality_issues=issues,
            improvement_recommendations=improvement_recommendations,
            processing_suggestions=processing_suggestions,
            assessment_summary=assessment_summary
        )
    
    def _assess_completeness(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess data completeness"""
        issues = []
        
        if data.empty:
            issues.append(QualityIssue(
                dimension=QualityDimension.COMPLETENESS,
                severity="critical",
                description="Dataset is completely empty",
                recommendation="Verify data source and collection process"
            ))
            return 0.0, issues
        
        # Calculate completeness metrics
        total_cells = data.size
        missing_cells = data.isnull().sum().sum()
        completeness_ratio = 1.0 - (missing_cells / total_cells)
        
        # Check per-column completeness
        column_completeness = 1.0 - (data.isnull().sum() / len(data))
        problematic_columns = column_completeness[column_completeness < self.thresholds.completeness_min]
        
        if len(problematic_columns) > 0:
            severity = "critical" if problematic_columns.min() < 0.5 else "high"
            issues.append(QualityIssue(
                dimension=QualityDimension.COMPLETENESS,
                severity=severity,
                description=f"{len(problematic_columns)} columns have low completeness",
                affected_columns=problematic_columns.index.tolist(),
                recommendation=f"Investigate missing data in: {', '.join(problematic_columns.index[:3])}"
            ))
        
        # Overall completeness score
        score = max(0.0, min(1.0, completeness_ratio))
        
        return score, issues
    
    def _assess_accuracy(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess data accuracy using statistical methods"""
        issues = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return 1.0, issues  # No numeric data to assess
        
        accuracy_scores = []
        
        for col in numeric_cols:
            col_data = data[col].dropna()
            
            if len(col_data) < 10:
                continue
            
            # Detect outliers as accuracy issue
            z_scores = np.abs(stats.zscore(col_data))
            outlier_count = (z_scores > 3.0).sum()
            outlier_ratio = outlier_count / len(col_data)
            
            if outlier_ratio > 0.05:  # More than 5% outliers
                severity = "high" if outlier_ratio > 0.15 else "medium"
                issues.append(QualityIssue(
                    dimension=QualityDimension.ACCURACY,
                    severity=severity,
                    description=f"Column '{col}' has {outlier_ratio:.1%} outliers",
                    affected_columns=[col],
                    recommendation=f"Investigate extreme values in {col}"
                ))
            
            # Accuracy score based on outlier ratio
            accuracy_scores.append(max(0.0, 1.0 - outlier_ratio))
        
        overall_accuracy = np.mean(accuracy_scores) if accuracy_scores else 1.0
        return overall_accuracy, issues
    
    def _assess_consistency(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess internal data consistency"""
        issues = []
        consistency_scores = []
        
        # Check data type consistency
        type_consistency = self._check_type_consistency(data)
        consistency_scores.append(type_consistency)
        
        # Check value range consistency for numeric columns
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = data[col].dropna()
            
            if len(col_data) < 2:
                continue
            
            # Check for unrealistic value jumps
            if len(col_data) > 1:
                differences = col_data.diff().abs()
                threshold = col_data.std() * 10  # 10 standard deviations
                large_jumps = (differences > threshold).sum()
                
                if large_jumps > len(col_data) * 0.01:  # More than 1% large jumps
                    issues.append(QualityIssue(
                        dimension=QualityDimension.CONSISTENCY,
                        severity="medium",
                        description=f"Column '{col}' has {large_jumps} unrealistic value jumps",
                        affected_columns=[col],
                        recommendation=f"Check for measurement errors in {col}"
                    ))
                    consistency_scores.append(0.7)
                else:
                    consistency_scores.append(1.0)
        
        overall_consistency = np.mean(consistency_scores) if consistency_scores else 1.0
        return overall_consistency, issues
    
    def _assess_validity(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess data validity against expected formats and ranges"""
        issues = []
        validity_scores = []
        
        # Check for obviously invalid values
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = data[col]
            
            # Check for infinite values
            inf_count = np.isinf(col_data).sum()
            if inf_count > 0:
                issues.append(QualityIssue(
                    dimension=QualityDimension.VALIDITY,
                    severity="high",
                    description=f"Column '{col}' contains {inf_count} infinite values",
                    affected_columns=[col],
                    recommendation=f"Replace infinite values in {col}"
                ))
                validity_scores.append(0.5)
            else:
                validity_scores.append(1.0)
        
        # Check timestamp validity
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
        for col in time_columns:
            try:
                pd.to_datetime(data[col])
                validity_scores.append(1.0)
            except:
                issues.append(QualityIssue(
                    dimension=QualityDimension.VALIDITY,
                    severity="high",
                    description=f"Column '{col}' contains invalid timestamps",
                    affected_columns=[col],
                    recommendation=f"Fix timestamp format in {col}"
                ))
                validity_scores.append(0.0)
        
        overall_validity = np.mean(validity_scores) if validity_scores else 1.0
        return overall_validity, issues
    
    def _assess_timeliness(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess data timeliness"""
        issues = []
        
        # Find time columns
        time_columns = [col for col in data.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if not time_columns:
            return 1.0, issues  # No time data to assess
        
        try:
            time_col = time_columns[0]
            timestamps = pd.to_datetime(data[time_col])
            latest_time = timestamps.max()
            current_time = datetime.now()
            
            # Handle timezone-naive datetime
            if latest_time.tz is None:
                current_time = current_time.replace(tzinfo=None)
            
            age_hours = (current_time - latest_time).total_seconds() / 3600
            
            if age_hours > self.thresholds.timeliness_max_age_hours:
                severity = "critical" if age_hours > 168 else "high"  # 1 week = critical
                issues.append(QualityIssue(
                    dimension=QualityDimension.TIMELINESS,
                    severity=severity,
                    description=f"Data is {age_hours:.1f} hours old",
                    recommendation="Update data source or collection frequency"
                ))
            
            # Timeliness score based on age
            score = max(0.0, 1.0 - (age_hours / (self.thresholds.timeliness_max_age_hours * 2)))
            
        except Exception as e:
            issues.append(QualityIssue(
                dimension=QualityDimension.TIMELINESS,
                severity="medium",
                description=f"Cannot assess timeliness: {str(e)}",
                recommendation="Check timestamp format"
            ))
            score = 0.5
        
        return score, issues
    
    def _assess_uniqueness(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess data uniqueness"""
        issues = []
        
        if data.empty:
            return 1.0, issues
        
        # Count duplicates
        duplicate_count = data.duplicated().sum()
        uniqueness_ratio = 1.0 - (duplicate_count / len(data))
        
        if uniqueness_ratio < self.thresholds.uniqueness_min:
            severity = "high" if duplicate_count > len(data) * 0.1 else "medium"
            issues.append(QualityIssue(
                dimension=QualityDimension.UNIQUENESS,
                severity=severity,
                description=f"Dataset contains {duplicate_count} duplicate records ({duplicate_count/len(data):.1%})",
                recommendation="Remove duplicate records"
            ))
        
        return uniqueness_ratio, issues
    
    def _assess_signal_quality(self, data: pd.DataFrame) -> Tuple[float, List[QualityIssue]]:
        """Assess signal quality for industrial data"""
        issues = []
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) == 0:
            return 1.0, issues
        
        signal_scores = []
        
        for col in numeric_cols:
            col_data = data[col].dropna()
            
            if len(col_data) < 10:
                continue
            
            # Calculate signal-to-noise ratio
            signal_std = col_data.std()
            noise_std = col_data.diff().std() / np.sqrt(2)  # Estimate noise from differences
            snr = signal_std / (noise_std + 1e-10)
            
            if snr < self.thresholds.signal_to_noise_min:
                severity = "high" if snr < 1.0 else "medium"
                issues.append(QualityIssue(
                    dimension=QualityDimension.SIGNAL_QUALITY,
                    severity=severity,
                    description=f"Column '{col}' has low signal-to-noise ratio: {snr:.2f}",
                    affected_columns=[col],
                    recommendation=f"Consider filtering or sensor calibration for {col}"
                ))
            
            # Signal quality score based on SNR
            signal_scores.append(min(1.0, snr / self.thresholds.signal_to_noise_min))
        
        overall_signal_quality = np.mean(signal_scores) if signal_scores else 1.0
        return overall_signal_quality, issues
    
    def _assess_control_performance(self, data: pd.DataFrame, 
                                  control_variables: Dict[str, str]) -> Tuple[float, List[QualityIssue]]:
        """Assess control loop performance"""
        issues = []
        
        # Check if required control variables are present
        required_vars = ['PV', 'SP']
        missing_vars = [var for var in required_vars 
                       if var not in control_variables or control_variables[var] not in data.columns]
        
        if missing_vars:
            issues.append(QualityIssue(
                dimension=QualityDimension.CONTROL_PERFORMANCE,
                severity="critical",
                description=f"Missing required control variables: {missing_vars}",
                recommendation="Ensure PV and SP data are available"
            ))
            return 0.0, issues
        
        # Calculate control performance metrics
        pv_col = control_variables['PV']
        sp_col = control_variables['SP']
        
        pv_data = data[pv_col].dropna()
        sp_data = data[sp_col].dropna()
        
        # Align data lengths
        min_length = min(len(pv_data), len(sp_data))
        if min_length < 10:
            issues.append(QualityIssue(
                dimension=QualityDimension.CONTROL_PERFORMANCE,
                severity="high",
                description="Insufficient data for control performance assessment",
                recommendation="Collect more control data"
            ))
            return 0.0, issues
        
        pv_values = pv_data.iloc[:min_length].values
        sp_values = sp_data.iloc[:min_length].values
        
        # Calculate control error metrics
        error = pv_values - sp_values
        mae = np.mean(np.abs(error))
        rmse = np.sqrt(np.mean(error**2))
        
        # Setpoint tracking performance (based on error relative to SP range)
        sp_range = np.max(sp_values) - np.min(sp_values)
        if sp_range > 0:
            normalized_mae = mae / sp_range
            tracking_performance = max(0.0, 1.0 - normalized_mae)
        else:
            tracking_performance = 1.0  # Perfect tracking if SP is constant
        
        if tracking_performance < self.thresholds.control_performance_min:
            severity = "high" if tracking_performance < 0.5 else "medium"
            issues.append(QualityIssue(
                dimension=QualityDimension.CONTROL_PERFORMANCE,
                severity=severity,
                description=f"Poor setpoint tracking performance: {tracking_performance:.2f}",
                recommendation="Review controller tuning and performance"
            ))
        
        return tracking_performance, issues
    
    def _check_type_consistency(self, data: pd.DataFrame) -> float:
        """Check data type consistency within columns"""
        if data.empty:
            return 1.0
        
        # Most pandas operations ensure type consistency, so this is mainly 
        # checking for mixed types in object columns
        object_cols = data.select_dtypes(include=['object']).columns
        
        if len(object_cols) == 0:
            return 1.0
        
        consistency_scores = []
        for col in object_cols:
            col_data = data[col].dropna()
            if len(col_data) == 0:
                continue
            
            # Check if all values can be converted to the same type
            try:
                pd.to_numeric(col_data)
                consistency_scores.append(1.0)  # All numeric
            except:
                try:
                    pd.to_datetime(col_data)
                    consistency_scores.append(1.0)  # All datetime
                except:
                    # Mixed types
                    consistency_scores.append(0.7)
        
        return np.mean(consistency_scores) if consistency_scores else 1.0
    
    def _generate_improvement_recommendations(self, issues: List[QualityIssue]) -> List[str]:
        """Generate improvement recommendations based on issues"""
        recommendations = []
        
        # Group issues by dimension
        dimension_issues = {}
        for issue in issues:
            if issue.dimension not in dimension_issues:
                dimension_issues[issue.dimension] = []
            dimension_issues[issue.dimension].append(issue)
        
        # Generate recommendations per dimension
        for dimension, dim_issues in dimension_issues.items():
            critical_issues = [i for i in dim_issues if i.severity == "critical"]
            high_issues = [i for i in dim_issues if i.severity == "high"]
            
            if critical_issues:
                recommendations.append(f"CRITICAL: Address {dimension.value} issues immediately")
            elif high_issues:
                recommendations.append(f"HIGH PRIORITY: Improve {dimension.value}")
            
            # Add specific recommendations
            for issue in dim_issues[:3]:  # Top 3 issues per dimension
                if issue.recommendation:
                    recommendations.append(f"- {issue.recommendation}")
        
        return recommendations
    
    def _generate_processing_suggestions(self, metrics: QualityMetrics, 
                                       issues: List[QualityIssue]) -> List[str]:
        """Generate data processing suggestions"""
        suggestions = []
        
        # Based on completeness
        if metrics.completeness_score < 0.9:
            suggestions.append("Apply interpolation for missing values")
        
        # Based on accuracy
        if metrics.accuracy_score < 0.8:
            suggestions.append("Remove or clip outliers")
        
        # Based on signal quality
        if metrics.signal_quality_score < 0.7:
            suggestions.append("Apply signal filtering (moving average or Butterworth)")
        
        # Based on uniqueness
        if metrics.uniqueness_score < 0.95:
            suggestions.append("Remove duplicate records")
        
        # Based on specific issues
        for issue in issues:
            if issue.dimension == QualityDimension.SIGNAL_QUALITY:
                suggestions.append("Consider noise reduction techniques")
            elif issue.dimension == QualityDimension.CONTROL_PERFORMANCE:
                suggestions.append("Analyze control loop tuning parameters")
        
        return list(set(suggestions))  # Remove duplicates
    
    def _create_assessment_summary(self, metrics: QualityMetrics, 
                                 issues: List[QualityIssue]) -> str:
        """Create a summary of the quality assessment"""
        critical_count = len([i for i in issues if i.severity == "critical"])
        high_count = len([i for i in issues if i.severity == "high"])
        
        summary = f"Overall Quality Score: {metrics.overall_score:.2f}/1.00\n"
        summary += f"Key Scores - Completeness: {metrics.completeness_score:.2f}, "
        summary += f"Accuracy: {metrics.accuracy_score:.2f}, "
        summary += f"Signal Quality: {metrics.signal_quality_score:.2f}\n"
        
        if critical_count > 0:
            summary += f"⚠️ {critical_count} CRITICAL issues require immediate attention\n"
        if high_count > 0:
            summary += f"🔴 {high_count} HIGH priority issues found\n"
        
        if metrics.overall_score >= 0.9:
            summary += "✅ Data quality is excellent"
        elif metrics.overall_score >= 0.7:
            summary += "⚡ Data quality is good with room for improvement"
        elif metrics.overall_score >= 0.5:
            summary += "⚠️ Data quality needs improvement"
        else:
            summary += "❌ Data quality is poor - significant issues found"
        
        return summary

class QualityImprover:
    """
    Automated data quality improvement tool
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.QualityImprover")
    
    def improve_quality(self, data: pd.DataFrame, 
                       quality_report: QualityReport) -> Tuple[pd.DataFrame, List[str]]:
        """
        Apply automated quality improvements based on assessment
        
        Args:
            data: Original data
            quality_report: Quality assessment report
            
        Returns:
            Tuple of (improved_data, improvement_log)
        """
        improved_data = data.copy()
        improvement_log = []
        
        try:
            # Apply improvements based on issues
            for issue in quality_report.quality_issues:
                if issue.severity in ["critical", "high"]:
                    if issue.dimension == QualityDimension.UNIQUENESS:
                        improved_data = self._remove_duplicates(improved_data)
                        improvement_log.append("Removed duplicate records")
                    
                    elif issue.dimension == QualityDimension.VALIDITY:
                        improved_data = self._fix_validity_issues(improved_data, issue)
                        improvement_log.append(f"Fixed validity issues in {issue.affected_columns}")
            
            # Apply general improvements based on scores
            metrics = quality_report.quality_metrics
            
            if metrics.completeness_score < 0.9:
                improved_data = self._handle_missing_data(improved_data)
                improvement_log.append("Applied interpolation for missing values")
            
            if metrics.accuracy_score < 0.8:
                improved_data = self._handle_outliers(improved_data)
                improvement_log.append("Handled outliers")
            
        except Exception as e:
            self.logger.error(f"Quality improvement failed: {e}")
            improvement_log.append(f"Quality improvement failed: {str(e)}")
        
        return improved_data, improvement_log
    
    def _remove_duplicates(self, data: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate records"""
        return data.drop_duplicates()
    
    def _fix_validity_issues(self, data: pd.DataFrame, issue: QualityIssue) -> pd.DataFrame:
        """Fix validity issues"""
        improved_data = data.copy()
        
        for col in issue.affected_columns:
            if col in improved_data.columns:
                # Replace infinite values with NaN
                improved_data[col] = improved_data[col].replace([np.inf, -np.inf], np.nan)
        
        return improved_data
    
    def _handle_missing_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle missing data with interpolation"""
        improved_data = data.copy()
        numeric_cols = improved_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if improved_data[col].isnull().sum() > 0:
                improved_data[col] = improved_data[col].interpolate(method='linear')
        
        return improved_data
    
    def _handle_outliers(self, data: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using IQR method"""
        improved_data = data.copy()
        numeric_cols = improved_data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = improved_data[col].dropna()
            
            if len(col_data) > 10:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Clip outliers to bounds
                improved_data[col] = improved_data[col].clip(lower_bound, upper_bound)
        
        return improved_data 