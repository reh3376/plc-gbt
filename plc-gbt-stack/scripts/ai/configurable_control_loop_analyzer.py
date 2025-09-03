#!/usr/bin/env python3
"""
Configurable Control Loop Performance Analyzer
=============================================

Flexible performance analyzer that accepts configurable metrics and
performance classification ranges for comprehensive control loop analysis.

Features:
- Configurable performance metrics (MSE, MAE, RMSE, Custom)
- Configurable performance classification ranges
- Multi-metric analysis support
- Industrial standard benchmarking
- Detailed statistical analysis
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Available performance metrics"""
    MSE = "mse"
    MAE = "mae"
    RMSE = "rmse"
    MAPE = "mape"
    R_SQUARED = "r_squared"
    VARIANCE_EXPLAINED = "variance_explained"
    OSCILLATION_RATE = "oscillation_rate"
    SETTLING_TIME = "settling_time"
    CUSTOM = "custom"

@dataclass
class PerformanceRanges:
    """Performance classification ranges for a metric"""
    excellent_max: float
    good_max: float
    acceptable_max: float
    # anything above acceptable_max is considered "poor"

    def classify(self, value: float) -> str:
        """Classify a performance value"""
        if value <= self.excellent_max:
            return "excellent"
        elif value <= self.good_max:
            return "good"
        elif value <= self.acceptable_max:
            return "acceptable"
        else:
            return "poor"

@dataclass
class MetricConfiguration:
    """Configuration for a specific metric"""
    metric_type: MetricType
    ranges: PerformanceRanges
    weight: float = 1.0
    description: str = ""
    units: str = ""
    higher_is_better: bool = False  # True for metrics like R² where higher is better

@dataclass
class AnalysisResults:
    """Complete analysis results"""
    dataset_info: Dict[str, Any]
    control_loop_data: Dict[str, Any]
    metric_results: Dict[str, Any]
    performance_classification: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    recommendations: List[str]
    overall_score: float

class ConfigurableControlLoopAnalyzer:
    """
    Flexible control loop performance analyzer with configurable metrics and ranges
    """

    def __init__(self, metrics_config: List[MetricConfiguration]):
        self.metrics_config = metrics_config
        self.analysis_id = f"control_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Built-in metric calculators
        self.metric_calculators = {
            MetricType.MSE: self._calculate_mse,
            MetricType.MAE: self._calculate_mae,
            MetricType.RMSE: self._calculate_rmse,
            MetricType.MAPE: self._calculate_mape,
            MetricType.R_SQUARED: self._calculate_r_squared,
            MetricType.VARIANCE_EXPLAINED: self._calculate_variance_explained,
            MetricType.OSCILLATION_RATE: self._calculate_oscillation_rate,
            MetricType.SETTLING_TIME: self._calculate_settling_time
        }

        logger.info("🔧 Configurable Control Loop Analyzer initialized")
        logger.info(f"📊 Configured metrics: {[config.metric_type.value for config in metrics_config]}")
        logger.info(f"🎯 Analysis ID: {self.analysis_id}")

    def load_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Load and validate dataset"""
        logger.info(f"📁 Loading dataset: {dataset_path}")

        try:
            df = pd.read_csv(dataset_path, low_memory=False)

            dataset_info = {
                "file_path": dataset_path,
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "columns": list(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
                "load_timestamp": datetime.now().isoformat()
            }

            logger.info(f"✅ Dataset loaded: {len(df):,} rows, {len(df.columns)} columns")
            return {"status": "success", "dataframe": df, "dataset_info": dataset_info}

        except Exception as e:
            logger.error(f"❌ Dataset loading failed: {e}")
            return {"status": "error", "error": str(e)}

    def extract_control_variables(self, df: pd.DataFrame,
                                pv_column: str = None,
                                sp_column: str = None,
                                cv_column: str = None) -> Dict[str, Any]:
        """Extract control loop variables with flexible column detection"""
        logger.info("🔍 Extracting control loop variables...")

        try:
            # Auto-detect columns if not specified
            if not pv_column:
                pv_candidates = [col for col in df.columns if 'PV' in col.upper()]
                pv_column = pv_candidates[0] if pv_candidates else df.select_dtypes(include=[np.number]).columns[0]

            if not cv_column:
                cv_candidates = [col for col in df.columns if 'CV' in col.upper()]
                cv_column = cv_candidates[0] if cv_candidates else None

            # Extract and clean PV data
            pv_data = df[pv_column].dropna()
            if pv_data.dtype == 'object':
                pv_data = pd.to_numeric(pv_data, errors='coerce').dropna()

            # Handle setpoint
            if sp_column and sp_column in df.columns:
                sp_data = df[sp_column].dropna()
                if sp_data.dtype == 'object':
                    sp_data = pd.to_numeric(sp_data, errors='coerce').dropna()
                sp_method = "actual_column"
            else:
                # Create synthetic setpoint using moving average
                window_size = min(100, len(pv_data) // 10)
                sp_data = pv_data.rolling(window=window_size, center=True).mean().dropna()
                sp_method = "synthetic_moving_average"
                logger.info(f"   Created synthetic setpoint using {window_size}-point moving average")

            # Align data lengths
            min_length = min(len(pv_data), len(sp_data))
            pv_array = pv_data.iloc[:min_length].values
            sp_array = sp_data.iloc[:min_length].values
            error_array = pv_array - sp_array

            # Extract control variable if available
            cv_array = None
            if cv_column and cv_column in df.columns:
                cv_data = df[cv_column].dropna()
                if cv_data.dtype == 'object':
                    cv_data = pd.to_numeric(cv_data, errors='coerce').dropna()
                cv_array = cv_data.iloc[:min_length].values

            control_data = {
                "pv_column": pv_column,
                "sp_column": sp_column or "synthetic",
                "cv_column": cv_column,
                "sp_method": sp_method,
                "data_points": min_length,
                "pv_array": pv_array,
                "sp_array": sp_array,
                "error_array": error_array,
                "cv_array": cv_array,
                "process_statistics": {
                    "pv_mean": float(np.mean(pv_array)),
                    "pv_std": float(np.std(pv_array)),
                    "pv_range": float(np.max(pv_array) - np.min(pv_array)),
                    "sp_mean": float(np.mean(sp_array)),
                    "sp_std": float(np.std(sp_array)),
                    "error_mean": float(np.mean(error_array)),
                    "error_std": float(np.std(error_array)),
                    "error_abs_mean": float(np.mean(np.abs(error_array)))
                }
            }

            logger.info("✅ Control variables extracted")
            logger.info(f"   PV: {pv_column}, SP: {sp_method}, CV: {cv_column}")
            logger.info(f"   Data points: {min_length:,}")

            return control_data

        except Exception as e:
            logger.error(f"❌ Control variable extraction failed: {e}")
            return {"error": str(e)}

    def calculate_metrics(self, control_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate all configured metrics"""
        logger.info("🧮 Calculating performance metrics...")

        metric_results = {}

        for config in self.metrics_config:
            try:
                if config.metric_type in self.metric_calculators:
                    calculator = self.metric_calculators[config.metric_type]
                    value = calculator(control_data)

                    classification = config.ranges.classify(value)

                    metric_results[config.metric_type.value] = {
                        "value": float(value),
                        "classification": classification,
                        "weight": config.weight,
                        "description": config.description,
                        "units": config.units,
                        "ranges": {
                            "excellent_max": config.ranges.excellent_max,
                            "good_max": config.ranges.good_max,
                            "acceptable_max": config.ranges.acceptable_max
                        },
                        "higher_is_better": config.higher_is_better
                    }

                    logger.info(f"   {config.metric_type.value.upper()}: {value:.4f} ({classification})")

                else:
                    logger.warning(f"⚠️ Calculator not found for {config.metric_type.value}")

            except Exception as e:
                logger.error(f"❌ Failed to calculate {config.metric_type.value}: {e}")
                metric_results[config.metric_type.value] = {
                    "error": str(e),
                    "value": None,
                    "classification": "error"
                }

        logger.info(f"✅ Calculated {len(metric_results)} metrics")
        return metric_results

    def _calculate_mse(self, control_data: Dict[str, Any]) -> float:
        """Calculate Mean Squared Error"""
        error_array = control_data["error_array"]
        return np.mean(error_array ** 2)

    def _calculate_mae(self, control_data: Dict[str, Any]) -> float:
        """Calculate Mean Absolute Error"""
        error_array = control_data["error_array"]
        return np.mean(np.abs(error_array))

    def _calculate_rmse(self, control_data: Dict[str, Any]) -> float:
        """Calculate Root Mean Squared Error"""
        error_array = control_data["error_array"]
        return np.sqrt(np.mean(error_array ** 2))

    def _calculate_mape(self, control_data: Dict[str, Any]) -> float:
        """Calculate Mean Absolute Percentage Error"""
        pv_array = control_data["pv_array"]
        sp_array = control_data["sp_array"]

        # Avoid division by zero
        mask = sp_array != 0
        if np.sum(mask) == 0:
            return float('inf')

        return np.mean(np.abs((pv_array[mask] - sp_array[mask]) / sp_array[mask])) * 100

    def _calculate_r_squared(self, control_data: Dict[str, Any]) -> float:
        """Calculate R-squared (coefficient of determination)"""
        pv_array = control_data["pv_array"]
        sp_array = control_data["sp_array"]

        ss_res = np.sum((pv_array - sp_array) ** 2)
        ss_tot = np.sum((pv_array - np.mean(pv_array)) ** 2)

        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0

        return 1 - (ss_res / ss_tot)

    def _calculate_variance_explained(self, control_data: Dict[str, Any]) -> float:
        """Calculate variance explained by setpoint tracking"""
        error_array = control_data["error_array"]
        pv_array = control_data["pv_array"]

        error_variance = np.var(error_array)
        pv_variance = np.var(pv_array)

        if pv_variance == 0:
            return 1.0 if error_variance == 0 else 0.0

        return max(0, 1 - (error_variance / pv_variance))

    def _calculate_oscillation_rate(self, control_data: Dict[str, Any]) -> float:
        """Calculate oscillation rate (percentage of sign changes in error derivative)"""
        error_array = control_data["error_array"]

        if len(error_array) < 3:
            return 0.0

        # Calculate error derivative (difference)
        error_derivative = np.diff(error_array)

        # Count sign changes
        sign_changes = np.sum(np.diff(np.sign(error_derivative)) != 0)

        # Convert to percentage
        return (sign_changes / (len(error_derivative) - 1)) * 100

    def _calculate_settling_time(self, control_data: Dict[str, Any]) -> float:
        """Calculate settling time (simplified - time to reach within 5% of setpoint)"""
        pv_array = control_data["pv_array"]
        sp_array = control_data["sp_array"]

        # Calculate percentage error
        percent_error = np.abs((pv_array - sp_array) / sp_array) * 100

        # Find points within 5% of setpoint
        within_tolerance = percent_error <= 5.0

        if np.sum(within_tolerance) == 0:
            return float('inf')  # Never settled

        # Find first occurrence of settling (simplified)
        first_settled = np.argmax(within_tolerance)

        # Convert to percentage of total time
        return (first_settled / len(pv_array)) * 100

    def perform_statistical_analysis(self, control_data: Dict[str, Any],
                                   metric_results: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        logger.info("📊 Performing statistical analysis...")

        error_array = control_data["error_array"]
        pv_array = control_data["pv_array"]
        sp_array = control_data["sp_array"]

        # Distribution analysis
        def calculate_moments(data):
            mean = np.mean(data)
            std = np.std(data)
            if std > 0:
                skewness = np.mean(((data - mean) / std) ** 3)
                kurtosis = np.mean(((data - mean) / std) ** 4) - 3
            else:
                skewness = 0.0
                kurtosis = 0.0
            return {"mean": mean, "std": std, "skewness": skewness, "kurtosis": kurtosis}

        # Stability analysis
        def analyze_stability(data, window_size=100):
            if len(data) < window_size:
                return {"stable": True, "trend": "insufficient_data"}

            # Rolling statistics
            pd.Series(data).rolling(window=window_size).mean()
            rolling_std = pd.Series(data).rolling(window=window_size).std()

            # Trend detection
            recent_trend = np.polyfit(range(len(data)//2, len(data)),
                                    data[len(data)//2:], 1)[0]

            trend_classification = "stable"
            if abs(recent_trend) > np.std(data) * 0.01:
                trend_classification = "increasing" if recent_trend > 0 else "decreasing"

            return {
                "stable": np.std(rolling_std.dropna()) < np.mean(rolling_std.dropna()) * 0.1,
                "trend": trend_classification,
                "trend_slope": float(recent_trend),
                "variability_stability": float(np.std(rolling_std.dropna()))
            }

        statistical_analysis = {
            "error_distribution": calculate_moments(error_array),
            "pv_distribution": calculate_moments(pv_array),
            "stability_analysis": analyze_stability(error_array),
            "control_effectiveness": {
                "tracking_accuracy": float(1 - np.std(error_array) / np.std(pv_array)),
                "disturbance_rejection": float(np.corrcoef(pv_array, sp_array)[0, 1] ** 2),
                "control_effort_efficiency": float(np.std(pv_array) / (np.std(error_array) + 1e-10))
            },
            "data_quality": {
                "completeness": float(len(error_array) / control_data["data_points"]),
                "outlier_percentage": float(np.sum(np.abs(error_array) > 3 * np.std(error_array)) / len(error_array) * 100),
                "signal_to_noise_ratio": float(np.mean(np.abs(pv_array)) / (np.std(error_array) + 1e-10))
            }
        }

        logger.info("✅ Statistical analysis completed")
        return statistical_analysis

    def generate_performance_classification(self, metric_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall performance classification"""
        logger.info("🎯 Generating performance classification...")

        # Classification counts
        classifications = {}
        weighted_scores = []

        for _metric_name, result in metric_results.items():
            if "error" not in result:
                classification = result["classification"]
                weight = result["weight"]

                classifications[classification] = classifications.get(classification, 0) + 1

                # Convert classification to score
                score_map = {"excellent": 100, "good": 75, "acceptable": 50, "poor": 25}
                score = score_map.get(classification, 0)
                weighted_scores.append(score * weight)

        # Calculate overall score
        total_weight = sum(config.weight for config in self.metrics_config)
        overall_score = sum(weighted_scores) / total_weight if total_weight > 0 else 0

        # Determine overall classification
        if overall_score >= 90:
            overall_classification = "excellent"
        elif overall_score >= 70:
            overall_classification = "good"
        elif overall_score >= 50:
            overall_classification = "acceptable"
        else:
            overall_classification = "poor"

        performance_classification = {
            "overall_score": overall_score,
            "overall_classification": overall_classification,
            "classification_distribution": classifications,
            "metric_count": len(metric_results),
            "weighted_average": overall_score
        }

        logger.info(f"✅ Overall performance: {overall_classification} ({overall_score:.1f}%)")
        return performance_classification

    def generate_recommendations(self, metric_results: Dict[str, Any],
                               statistical_analysis: Dict[str, Any],
                               performance_classification: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        overall_score = performance_classification["overall_score"]

        # Performance-based recommendations
        if overall_score < 50:
            recommendations.append("CRITICAL: Control loop requires immediate attention - performance is poor")
            recommendations.append("Consider complete PID tuning review and system diagnostics")
        elif overall_score < 70:
            recommendations.append("Control loop performance is acceptable but has room for improvement")
            recommendations.append("Recommend PID parameter optimization and disturbance analysis")
        elif overall_score < 90:
            recommendations.append("Good control performance with minor optimization opportunities")
            recommendations.append("Consider advanced control strategies for further improvement")
        else:
            recommendations.append("Excellent control performance - maintain current parameters")
            recommendations.append("Monitor for any performance degradation over time")

        # Metric-specific recommendations
        poor_metrics = [name for name, result in metric_results.items()
                       if result.get("classification") == "poor"]

        if poor_metrics:
            recommendations.append(f"Poor performance in: {', '.join(poor_metrics)}")

            if "mse" in poor_metrics or "rmse" in poor_metrics:
                recommendations.append("High error variance detected - check for process disturbances")
            if "mae" in poor_metrics:
                recommendations.append("High average error - review setpoint tracking accuracy")
            if "oscillation_rate" in poor_metrics:
                recommendations.append("Excessive oscillation - reduce controller gain or increase damping")

        # Stability recommendations
        stability = statistical_analysis.get("stability_analysis", {})
        if not stability.get("stable", True):
            recommendations.append("Control loop stability issues detected - review tuning parameters")

        if stability.get("trend") != "stable":
            recommendations.append(f"Process trend detected: {stability.get('trend')} - investigate root cause")

        return recommendations

    def analyze_control_loop(self, dataset_path: str,
                           pv_column: str = None,
                           sp_column: str = None,
                           cv_column: str = None) -> AnalysisResults:
        """Perform complete control loop analysis"""
        logger.info("🚀 Starting control loop analysis")
        logger.info(f"📁 Dataset: {Path(dataset_path).name}")

        # Load dataset
        dataset_result = self.load_dataset(dataset_path)
        if dataset_result["status"] != "success":
            raise Exception(f"Dataset loading failed: {dataset_result.get('error')}")

        df = dataset_result["dataframe"]
        dataset_info = dataset_result["dataset_info"]

        # Extract control variables
        control_data = self.extract_control_variables(df, pv_column, sp_column, cv_column)
        if "error" in control_data:
            raise Exception(f"Control variable extraction failed: {control_data['error']}")

        # Calculate metrics
        metric_results = self.calculate_metrics(control_data)

        # Statistical analysis
        statistical_analysis = self.perform_statistical_analysis(control_data, metric_results)

        # Performance classification
        performance_classification = self.generate_performance_classification(metric_results)

        # Recommendations
        recommendations = self.generate_recommendations(
            metric_results, statistical_analysis, performance_classification
        )

        results = AnalysisResults(
            dataset_info=dataset_info,
            control_loop_data=control_data,
            metric_results=metric_results,
            performance_classification=performance_classification,
            statistical_analysis=statistical_analysis,
            recommendations=recommendations,
            overall_score=performance_classification["overall_score"]
        )

        logger.info(f"✅ Analysis completed - Overall score: {results.overall_score:.1f}%")
        return results

def create_beer_feed_configuration() -> List[MetricConfiguration]:
    """Create typical configuration for beer feed control analysis"""
    return [
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(excellent_max=0.5, good_max=2.0, acceptable_max=10.0),
            weight=1.5,
            description="Mean Squared Error - penalizes large deviations more heavily",
            units="(units)²"
        ),
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(excellent_max=0.3, good_max=1.0, acceptable_max=3.0),
            weight=1.0,
            description="Mean Absolute Error - average magnitude of deviations",
            units="units"
        ),
        MetricConfiguration(
            metric_type=MetricType.RMSE,
            ranges=PerformanceRanges(excellent_max=0.7, good_max=1.5, acceptable_max=3.2),
            weight=1.2,
            description="Root Mean Squared Error - standard deviation of errors",
            units="units"
        ),
        MetricConfiguration(
            metric_type=MetricType.VARIANCE_EXPLAINED,
            ranges=PerformanceRanges(excellent_max=0.95, good_max=0.85, acceptable_max=0.70),
            weight=1.0,
            description="Variance explained by control system",
            units="%",
            higher_is_better=True
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=0.8,
            description="Percentage of oscillatory behavior",
            units="%"
        )
    ]

def main():
    """Main execution with beer feed dataset analysis"""
    print("🧮 Configurable Control Loop Performance Analyzer")
    print("=" * 70)

    # Configuration for beer feed analysis
    config = create_beer_feed_configuration()

    # Initialize analyzer
    analyzer = ConfigurableControlLoopAnalyzer(config)

    # Dataset path
    dataset_path = "/Users/reh3376/repos/control_loop01/control_loop/.datasets/data_beerfeed_03_02-05_09-2025.csv"

    try:
        # Perform analysis
        results = analyzer.analyze_control_loop(dataset_path)

        # Display results
        print("\n📊 CONTROL LOOP PERFORMANCE ANALYSIS RESULTS")
        print("=" * 70)

        # Dataset summary
        dataset_info = results.dataset_info
        print("\n📁 Dataset Information:")
        print(f"   File: {Path(dataset_path).name}")
        print(f"   Rows: {dataset_info['total_rows']:,}")
        print(f"   Columns: {dataset_info['total_columns']}")

        # Control loop data
        control_data = results.control_loop_data
        print("\n🎛️ Control Loop Configuration:")
        print(f"   Process Variable: {control_data['pv_column']}")
        print(f"   Setpoint: {control_data['sp_column']} ({control_data['sp_method']})")
        print(f"   Control Variable: {control_data['cv_column']}")
        print(f"   Data Points: {control_data['data_points']:,}")

        # Process statistics
        stats = control_data['process_statistics']
        print("\n📈 Process Statistics:")
        print(f"   PV Mean: {stats['pv_mean']:.3f}")
        print(f"   PV Std: {stats['pv_std']:.3f}")
        print(f"   Error Mean: {stats['error_mean']:.3f}")
        print(f"   Error Std: {stats['error_std']:.3f}")

        # Performance metrics
        print("\n🧮 Performance Metrics:")
        for metric_name, result in results.metric_results.items():
            if "error" not in result:
                classification = result["classification"].upper()
                value = result["value"]
                units = result["units"]
                description = result["description"]

                print(f"   {metric_name.upper()}: {value:.4f} {units} - {classification}")
                print(f"      {description}")

        # Overall performance
        perf_class = results.performance_classification
        print("\n🎯 Overall Performance Assessment:")
        print(f"   Overall Score: {perf_class['overall_score']:.1f}%")
        print(f"   Classification: {perf_class['overall_classification'].upper()}")

        dist = perf_class['classification_distribution']
        print("   Performance Distribution:")
        for classification, count in dist.items():
            print(f"     {classification.capitalize()}: {count} metrics")

        # Statistical analysis
        stat_analysis = results.statistical_analysis
        stability = stat_analysis['stability_analysis']
        print("\n📊 Statistical Analysis:")
        print(f"   Control Stability: {'✅ Stable' if stability['stable'] else '⚠️ Unstable'}")
        print(f"   Process Trend: {stability['trend'].replace('_', ' ').title()}")

        effectiveness = stat_analysis['control_effectiveness']
        print(f"   Tracking Accuracy: {effectiveness['tracking_accuracy']:.1%}")
        print(f"   Disturbance Rejection: {effectiveness['disturbance_rejection']:.1%}")

        # Recommendations
        print("\n💡 Recommendations:")
        for i, rec in enumerate(results.recommendations, 1):
            print(f"   {i}. {rec}")

        # Save results
        results_dir = Path("results") / "control_loop_analysis"
        results_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"control_loop_analysis_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(asdict(results), f, indent=2, default=str)

        print(f"\n📁 Complete results saved to: {results_file}")

        return results

    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        print(f"\n❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    main()
