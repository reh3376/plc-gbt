"""
Analysis and Reporting Module
============================

Modular statistical analysis and reporting components.
Extracted from various files to eliminate code duplication.

Features:
- Statistical analysis utilities
- Performance analysis frameworks
- Report generation systems
- Visualization helpers
- Data summarization tools
"""

import numpy as np
import pandas as pd
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple, Callable
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    """Standard structure for analysis results"""
    analysis_id: str
    analysis_type: str
    timestamp: str
    summary: Dict[str, Any]
    detailed_results: Dict[str, Any]
    metadata: Dict[str, Any]
    quality_score: float
    recommendations: List[str]

@dataclass
class StatisticalSummary:
    """Statistical summary of a dataset or variable"""
    count: int
    mean: float
    std: float
    min: float
    max: float
    q25: float
    q50: float  # median
    q75: float
    range: float
    coefficient_of_variation: float
    skewness: float
    kurtosis: float
    null_count: int
    null_percentage: float

class StatisticalAnalyzer:
    """Core statistical analysis functionality"""
    
    @staticmethod
    def calculate_summary_statistics(data: Union[pd.Series, np.ndarray],
                                   name: str = "data") -> StatisticalSummary:
        """
        Calculate comprehensive statistical summary
        
        Args:
            data: Numeric data to analyze
            name: Name for the data series
            
        Returns:
            StatisticalSummary object
        """
        if isinstance(data, pd.Series):
            data_array = data.values
        else:
            data_array = np.array(data)
        
        # Handle missing values
        valid_data = data_array[~np.isnan(data_array)]
        null_count = len(data_array) - len(valid_data)
        
        if len(valid_data) == 0:
            logger.warning(f"No valid data points for {name}")
            return StatisticalSummary(
                count=0, mean=np.nan, std=np.nan, min=np.nan, max=np.nan,
                q25=np.nan, q50=np.nan, q75=np.nan, range=np.nan,
                coefficient_of_variation=np.nan, skewness=np.nan, kurtosis=np.nan,
                null_count=null_count, null_percentage=100.0
            )
        
        # Calculate statistics
        mean_val = np.mean(valid_data)
        std_val = np.std(valid_data)
        min_val = np.min(valid_data)
        max_val = np.max(valid_data)
        
        # Percentiles
        q25 = np.percentile(valid_data, 25)
        q50 = np.percentile(valid_data, 50)  # median
        q75 = np.percentile(valid_data, 75)
        
        # Derived statistics
        range_val = max_val - min_val
        cv = std_val / mean_val if mean_val != 0 else np.inf
        
        # Higher order moments
        try:
            from scipy import stats
            skewness = stats.skew(valid_data)
            kurtosis_val = stats.kurtosis(valid_data)
        except ImportError:
            skewness = np.nan
            kurtosis_val = np.nan
        
        return StatisticalSummary(
            count=len(valid_data),
            mean=mean_val,
            std=std_val,
            min=min_val,
            max=max_val,
            q25=q25,
            q50=q50,
            q75=q75,
            range=range_val,
            coefficient_of_variation=cv,
            skewness=skewness,
            kurtosis=kurtosis_val,
            null_count=null_count,
            null_percentage=(null_count / len(data_array)) * 100
        )
    
    @staticmethod
    def detect_outliers(data: Union[pd.Series, np.ndarray],
                       method: str = "iqr",
                       threshold: float = 1.5) -> Dict[str, Any]:
        """
        Detect outliers using various methods
        
        Args:
            data: Numeric data to analyze
            method: Method to use ('iqr', 'zscore', 'modified_zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            Dictionary with outlier information
        """
        if isinstance(data, pd.Series):
            data_array = data.values
        else:
            data_array = np.array(data)
        
        valid_data = data_array[~np.isnan(data_array)]
        
        if method == "iqr":
            q75, q25 = np.percentile(valid_data, [75, 25])
            iqr = q75 - q25
            lower_bound = q25 - (threshold * iqr)
            upper_bound = q75 + (threshold * iqr)
            outliers = (data_array < lower_bound) | (data_array > upper_bound)
            
        elif method == "zscore":
            mean_val = np.mean(valid_data)
            std_val = np.std(valid_data)
            z_scores = np.abs((data_array - mean_val) / std_val)
            outliers = z_scores > threshold
            
        elif method == "modified_zscore":
            median_val = np.median(valid_data)
            mad = np.median(np.abs(valid_data - median_val))
            modified_z_scores = 0.6745 * (data_array - median_val) / mad
            outliers = np.abs(modified_z_scores) > threshold
            
        else:
            raise ValueError(f"Unknown outlier detection method: {method}")
        
        outlier_indices = np.where(outliers)[0]
        outlier_values = data_array[outliers]
        
        return {
            "method": method,
            "threshold": threshold,
            "total_outliers": len(outlier_indices),
            "outlier_percentage": (len(outlier_indices) / len(data_array)) * 100,
            "outlier_indices": outlier_indices.tolist(),
            "outlier_values": outlier_values.tolist(),
            "bounds": {
                "lower": locals().get('lower_bound', None),
                "upper": locals().get('upper_bound', None)
            } if method == "iqr" else None
        }
    
    @staticmethod
    def correlation_analysis(df: pd.DataFrame,
                           target_column: Optional[str] = None,
                           method: str = "pearson") -> Dict[str, Any]:
        """
        Perform correlation analysis on DataFrame
        
        Args:
            df: DataFrame to analyze
            target_column: Optional target column for focused analysis
            method: Correlation method ('pearson', 'spearman', 'kendall')
            
        Returns:
            Correlation analysis results
        """
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return {
                "error": "Insufficient numeric columns for correlation analysis",
                "numeric_columns": len(numeric_df.columns)
            }
        
        # Calculate correlation matrix
        corr_matrix = numeric_df.corr(method=method)
        
        # Find highest correlations
        high_correlations = []
        correlation_threshold = 0.7
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i + 1, len(corr_matrix.columns)):
                col1 = corr_matrix.columns[i]
                col2 = corr_matrix.columns[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) >= correlation_threshold:
                    high_correlations.append({
                        "variable_1": col1,
                        "variable_2": col2,
                        "correlation": corr_value,
                        "strength": "strong" if abs(corr_value) >= 0.8 else "moderate"
                    })
        
        results = {
            "method": method,
            "correlation_matrix": corr_matrix.to_dict(),
            "high_correlations": high_correlations,
            "correlation_threshold": correlation_threshold,
            "matrix_shape": corr_matrix.shape
        }
        
        # Target-specific analysis
        if target_column and target_column in corr_matrix.columns:
            target_correlations = corr_matrix[target_column].drop(target_column).sort_values(
                key=abs, ascending=False
            )
            
            results["target_analysis"] = {
                "target_column": target_column,
                "strongest_positive": target_correlations.iloc[0] if len(target_correlations) > 0 else None,
                "strongest_negative": target_correlations.iloc[-1] if len(target_correlations) > 0 else None,
                "top_correlations": target_correlations.head(5).to_dict(),
                "weak_correlations": target_correlations[abs(target_correlations) < 0.3].to_dict()
            }
        
        return results

class PerformanceAnalyzer:
    """Performance analysis for control loops and processes"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_control_performance(self, 
                                  pv_data: np.ndarray,
                                  sp_data: np.ndarray,
                                  cv_data: Optional[np.ndarray] = None,
                                  analysis_id: Optional[str] = None) -> AnalysisResult:
        """
        Comprehensive control loop performance analysis
        
        Args:
            pv_data: Process variable data
            sp_data: Setpoint data
            cv_data: Optional control variable data
            analysis_id: Optional identifier for this analysis
            
        Returns:
            AnalysisResult with comprehensive performance metrics
        """
        if analysis_id is None:
            analysis_id = f"control_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"🔍 Starting control performance analysis: {analysis_id}")
        
        # Basic validation
        if len(pv_data) != len(sp_data):
            raise ValueError("PV and SP data must have same length")
        
        error_data = pv_data - sp_data
        
        # Statistical summaries
        pv_stats = StatisticalAnalyzer.calculate_summary_statistics(pv_data, "PV")
        sp_stats = StatisticalAnalyzer.calculate_summary_statistics(sp_data, "SP")
        error_stats = StatisticalAnalyzer.calculate_summary_statistics(error_data, "Error")
        
        # Performance metrics
        mae = np.mean(np.abs(error_data))
        mse = np.mean(error_data ** 2)
        rmse = np.sqrt(mse)
        
        # Variance explained
        pv_var = np.var(pv_data)
        error_var = np.var(error_data)
        variance_explained = max(0, 1 - (error_var / pv_var)) if pv_var > 0 else 0
        
        # Oscillation analysis
        oscillation_metrics = self._analyze_oscillations(error_data)
        
        # Stability analysis
        stability_metrics = self._analyze_stability(pv_data, sp_data)
        
        # Setpoint tracking
        tracking_metrics = self._analyze_setpoint_tracking(pv_data, sp_data)
        
        # Control variable analysis (if available)
        cv_analysis = None
        if cv_data is not None:
            cv_analysis = self._analyze_control_variable(cv_data, error_data)
        
        # Overall quality score
        quality_score = self._calculate_overall_quality(
            mae, variance_explained, oscillation_metrics, stability_metrics
        )
        
        # Generate recommendations
        recommendations = self._generate_control_recommendations(
            mae, oscillation_metrics, stability_metrics, tracking_metrics
        )
        
        # Compile results
        summary = {
            "mae": mae,
            "mse": mse,
            "rmse": rmse,
            "variance_explained": variance_explained,
            "oscillation_rate": oscillation_metrics["oscillation_percentage"],
            "stability_score": stability_metrics["stability_score"],
            "tracking_score": tracking_metrics["tracking_score"],
            "data_points": len(pv_data)
        }
        
        detailed_results = {
            "statistical_summaries": {
                "pv": asdict(pv_stats),
                "sp": asdict(sp_stats),
                "error": asdict(error_stats)
            },
            "performance_metrics": {
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
                "variance_explained": variance_explained
            },
            "oscillation_analysis": oscillation_metrics,
            "stability_analysis": stability_metrics,
            "tracking_analysis": tracking_metrics,
            "control_variable_analysis": cv_analysis
        }
        
        metadata = {
            "data_length": len(pv_data),
            "has_control_variable": cv_data is not None,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_version": "1.0"
        }
        
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_type="control_performance",
            timestamp=datetime.now().isoformat(),
            summary=summary,
            detailed_results=detailed_results,
            metadata=metadata,
            quality_score=quality_score,
            recommendations=recommendations
        )
        
        # Cache result
        self.analysis_cache[analysis_id] = result
        
        logger.info(f"✅ Control performance analysis completed")
        logger.info(f"   Quality Score: {quality_score:.1f}%")
        logger.info(f"   MAE: {mae:.4f}, Variance Explained: {variance_explained:.1%}")
        
        return result
    
    def _analyze_oscillations(self, error_data: np.ndarray) -> Dict[str, Any]:
        """Analyze oscillatory behavior in error signal"""
        if len(error_data) < 3:
            return {"oscillation_percentage": 0.0, "dominant_frequency": None}
        
        # Count sign changes in error derivative
        error_derivative = np.diff(error_data)
        sign_changes = np.sum(np.diff(np.sign(error_derivative)) != 0)
        oscillation_percentage = (sign_changes / (len(error_derivative) - 1)) * 100
        
        # Frequency analysis (simplified)
        try:
            from scipy.fft import fft, fftfreq
            fft_values = fft(error_data)
            frequencies = fftfreq(len(error_data))
            
            # Find dominant frequency
            magnitude = np.abs(fft_values)
            dominant_freq_idx = np.argmax(magnitude[1:len(magnitude)//2]) + 1
            dominant_frequency = frequencies[dominant_freq_idx]
            
        except ImportError:
            dominant_frequency = None
        
        return {
            "oscillation_percentage": oscillation_percentage,
            "sign_changes": int(sign_changes),
            "dominant_frequency": dominant_frequency,
            "classification": "high" if oscillation_percentage > 20 else 
                           "moderate" if oscillation_percentage > 10 else "low"
        }
    
    def _analyze_stability(self, pv_data: np.ndarray, sp_data: np.ndarray) -> Dict[str, Any]:
        """Analyze system stability"""
        error_data = pv_data - sp_data
        
        # Stability metrics
        error_std = np.std(error_data)
        pv_std = np.std(pv_data)
        
        # Relative stability
        relative_stability = 1 - (error_std / pv_std) if pv_std > 0 else 0
        
        # Drift analysis (linear trend in error)
        time_points = np.arange(len(error_data))
        trend_coeff = np.polyfit(time_points, error_data, 1)[0]
        
        # Stability classification
        if relative_stability > 0.8 and abs(trend_coeff) < 0.001:
            stability_class = "excellent"
            stability_score = 90 + min(10, relative_stability * 10)
        elif relative_stability > 0.6:
            stability_class = "good"
            stability_score = 70 + (relative_stability - 0.6) * 50
        elif relative_stability > 0.4:
            stability_class = "acceptable"
            stability_score = 50 + (relative_stability - 0.4) * 50
        else:
            stability_class = "poor"
            stability_score = relative_stability * 50
        
        return {
            "relative_stability": relative_stability,
            "error_std": error_std,
            "trend_coefficient": trend_coeff,
            "stability_score": stability_score,
            "stability_classification": stability_class,
            "has_drift": abs(trend_coeff) > 0.01
        }
    
    def _analyze_setpoint_tracking(self, pv_data: np.ndarray, sp_data: np.ndarray) -> Dict[str, Any]:
        """Analyze setpoint tracking performance"""
        error_data = pv_data - sp_data
        
        # Tracking accuracy
        mae = np.mean(np.abs(error_data))
        max_error = np.max(np.abs(error_data))
        
        # Response to setpoint changes
        sp_changes = np.abs(np.diff(sp_data)) > np.std(sp_data) * 0.1
        response_times = []
        
        if np.any(sp_changes):
            for i, change in enumerate(sp_changes):
                if change and i < len(pv_data) - 20:
                    # Simplified response time calculation
                    sp_target = sp_data[i + 1]
                    pv_response = pv_data[i + 1:i + 21]  # Next 20 points
                    
                    # Find when PV reaches within 5% of setpoint
                    tolerance = 0.05 * abs(sp_target)
                    within_tolerance = np.abs(pv_response - sp_target) <= tolerance
                    
                    if np.any(within_tolerance):
                        response_time = np.argmax(within_tolerance)
                        response_times.append(response_time)
        
        # Tracking score
        sp_range = np.max(sp_data) - np.min(sp_data)
        tracking_accuracy = 1 - (mae / sp_range) if sp_range > 0 else 0
        tracking_score = max(0, min(100, tracking_accuracy * 100))
        
        return {
            "tracking_accuracy": tracking_accuracy,
            "tracking_score": tracking_score,
            "mae": mae,
            "max_error": max_error,
            "setpoint_changes": int(np.sum(sp_changes)),
            "average_response_time": np.mean(response_times) if response_times else None,
            "tracking_classification": "excellent" if tracking_score > 90 else
                                     "good" if tracking_score > 70 else
                                     "acceptable" if tracking_score > 50 else "poor"
        }
    
    def _analyze_control_variable(self, cv_data: np.ndarray, error_data: np.ndarray) -> Dict[str, Any]:
        """Analyze control variable behavior"""
        cv_stats = StatisticalAnalyzer.calculate_summary_statistics(cv_data, "CV")
        
        # Control effort
        cv_range = np.max(cv_data) - np.min(cv_data)
        cv_variation = np.std(cv_data)
        
        # Saturation analysis
        cv_min, cv_max = np.min(cv_data), np.max(cv_data)
        lower_saturation = np.sum(cv_data <= cv_min + 0.01 * cv_range) / len(cv_data) * 100
        upper_saturation = np.sum(cv_data >= cv_max - 0.01 * cv_range) / len(cv_data) * 100
        
        # Control effectiveness (correlation with error reduction)
        try:
            correlation = np.corrcoef(cv_data[:-1], -np.diff(error_data))[0, 1]
        except:
            correlation = np.nan
        
        return {
            "statistical_summary": asdict(cv_stats),
            "control_range": cv_range,
            "control_variation": cv_variation,
            "lower_saturation_percentage": lower_saturation,
            "upper_saturation_percentage": upper_saturation,
            "error_correlation": correlation,
            "is_saturated": (lower_saturation > 5) or (upper_saturation > 5)
        }
    
    def _calculate_overall_quality(self, mae: float, variance_explained: float,
                                 oscillation_metrics: Dict, stability_metrics: Dict) -> float:
        """Calculate overall quality score"""
        # Normalize metrics to 0-100 scale
        mae_score = max(0, 100 - (mae * 20))  # Assume mae < 5 is excellent
        variance_score = variance_explained * 100
        oscillation_score = max(0, 100 - oscillation_metrics["oscillation_percentage"] * 2)
        stability_score = stability_metrics["stability_score"]
        
        # Weighted average
        weights = [0.3, 0.3, 0.2, 0.2]  # mae, variance, oscillation, stability
        scores = [mae_score, variance_score, oscillation_score, stability_score]
        
        overall_score = sum(w * s for w, s in zip(weights, scores))
        return min(100, max(0, overall_score))
    
    def _generate_control_recommendations(self, mae: float, oscillation_metrics: Dict,
                                        stability_metrics: Dict, tracking_metrics: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # MAE-based recommendations
        if mae > 2.0:
            recommendations.append("High tracking error detected - consider PID tuning")
        elif mae > 1.0:
            recommendations.append("Moderate tracking error - monitor and consider optimization")
        
        # Oscillation recommendations
        if oscillation_metrics["oscillation_percentage"] > 25:
            recommendations.append("High oscillation detected - reduce derivative gain or add filtering")
        elif oscillation_metrics["oscillation_percentage"] > 15:
            recommendations.append("Moderate oscillation - consider tuning adjustments")
        
        # Stability recommendations
        if stability_metrics["stability_score"] < 50:
            recommendations.append("Poor stability - fundamental tuning issues detected")
        elif stability_metrics["has_drift"]:
            recommendations.append("System drift detected - check for process changes or bias")
        
        # Tracking recommendations
        if tracking_metrics["tracking_score"] < 60:
            recommendations.append("Poor setpoint tracking - increase integral gain or reduce deadtime")
        
        if not recommendations:
            recommendations.append("Control performance is within acceptable ranges")
        
        return recommendations

class ReportGenerator:
    """Generate various types of analysis reports"""
    
    @staticmethod
    def generate_summary_report(analysis_result: AnalysisResult,
                              output_format: str = "dict") -> Union[Dict, str]:
        """
        Generate summary report from analysis result
        
        Args:
            analysis_result: AnalysisResult to summarize
            output_format: Output format ('dict', 'json', 'markdown')
            
        Returns:
            Report in requested format
        """
        report_data = {
            "analysis_id": analysis_result.analysis_id,
            "analysis_type": analysis_result.analysis_type,
            "timestamp": analysis_result.timestamp,
            "quality_score": analysis_result.quality_score,
            "summary_metrics": analysis_result.summary,
            "recommendations": analysis_result.recommendations,
            "metadata": analysis_result.metadata
        }
        
        if output_format == "dict":
            return report_data
        elif output_format == "json":
            return json.dumps(report_data, indent=2, default=str)
        elif output_format == "markdown":
            return ReportGenerator._format_markdown_report(report_data)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    @staticmethod
    def _format_markdown_report(report_data: Dict) -> str:
        """Format report as markdown"""
        md = f"""# Analysis Report

**Analysis ID:** {report_data['analysis_id']}  
**Type:** {report_data['analysis_type']}  
**Timestamp:** {report_data['timestamp']}  
**Quality Score:** {report_data['quality_score']:.1f}%

## Summary Metrics

"""
        
        for key, value in report_data['summary_metrics'].items():
            if isinstance(value, float):
                md += f"- **{key.replace('_', ' ').title()}:** {value:.4f}\n"
            else:
                md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        md += "\n## Recommendations\n\n"
        for i, rec in enumerate(report_data['recommendations'], 1):
            md += f"{i}. {rec}\n"
        
        md += f"\n## Metadata\n\n"
        for key, value in report_data['metadata'].items():
            md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        return md
    
    @staticmethod
    def save_report(report_content: Union[Dict, str],
                   file_path: str,
                   format_type: str = "json") -> str:
        """
        Save report to file
        
        Args:
            report_content: Report content to save
            file_path: Output file path
            format_type: File format ('json', 'markdown', 'txt')
            
        Returns:
            Path to saved file
        """
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format_type == "json":
            if isinstance(report_content, dict):
                with open(output_path, 'w') as f:
                    json.dump(report_content, f, indent=2, default=str)
            else:
                with open(output_path, 'w') as f:
                    f.write(str(report_content))
        else:
            with open(output_path, 'w') as f:
                f.write(str(report_content))
        
        logger.info(f"📄 Report saved: {output_path}")
        return str(output_path)

# Utility functions for common analysis operations
def compare_datasets(df1: pd.DataFrame, df2: pd.DataFrame,
                    key_columns: Optional[List[str]] = None) -> Dict[str, Any]:
    """Compare two datasets and identify differences"""
    comparison = {
        "dataset1_shape": df1.shape,
        "dataset2_shape": df2.shape,
        "shape_match": df1.shape == df2.shape,
        "columns_dataset1": list(df1.columns),
        "columns_dataset2": list(df2.columns),
        "common_columns": list(set(df1.columns) & set(df2.columns)),
        "unique_to_dataset1": list(set(df1.columns) - set(df2.columns)),
        "unique_to_dataset2": list(set(df2.columns) - set(df1.columns))
    }
    
    # Compare common columns
    if comparison["common_columns"]:
        column_comparisons = {}
        for col in comparison["common_columns"]:
            if col in df1.select_dtypes(include=[np.number]).columns:
                stats1 = StatisticalAnalyzer.calculate_summary_statistics(df1[col], f"df1_{col}")
                stats2 = StatisticalAnalyzer.calculate_summary_statistics(df2[col], f"df2_{col}")
                
                column_comparisons[col] = {
                    "mean_difference": stats1.mean - stats2.mean,
                    "std_difference": stats1.std - stats2.std,
                    "range_difference": stats1.range - stats2.range
                }
        
        comparison["column_comparisons"] = column_comparisons
    
    return comparison

def create_trend_analysis(data: Union[pd.Series, np.ndarray],
                         window_size: int = 10) -> Dict[str, Any]:
    """Analyze trends in time series data"""
    if isinstance(data, pd.Series):
        data_array = data.values
    else:
        data_array = np.array(data)
    
    # Linear trend
    time_points = np.arange(len(data_array))
    trend_coeff = np.polyfit(time_points, data_array, 1)[0]
    
    # Moving average trend
    df_data = pd.Series(data_array)
    moving_avg = df_data.rolling(window=window_size).mean()
    
    # Trend strength
    trend_strength = abs(trend_coeff) / np.std(data_array) if np.std(data_array) > 0 else 0
    
    return {
        "trend_coefficient": trend_coeff,
        "trend_direction": "increasing" if trend_coeff > 0 else "decreasing" if trend_coeff < 0 else "stable",
        "trend_strength": trend_strength,
        "trend_classification": "strong" if trend_strength > 0.1 else "moderate" if trend_strength > 0.05 else "weak",
        "moving_average": moving_avg.tolist()
    } 