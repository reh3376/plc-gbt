#!/usr/bin/env python3
"""
Demonstration of Configurable Control Loop Analyzer
===================================================

Shows how to easily customize metrics and performance ranges for different scenarios.
"""

from configurable_control_loop_analyzer import (
    ConfigurableControlLoopAnalyzer,
    MetricConfiguration,
    MetricType,
    PerformanceRanges,
)


def create_mse_focused_config():
    """Configuration focused primarily on MSE metrics"""
    return [
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=5.0, acceptable_max=15.0),
            weight=2.0,  # Double weight for MSE
            description="Primary MSE metric for gradient-based optimization",
            units="(units)²"
        ),
        MetricConfiguration(
            metric_type=MetricType.RMSE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=2.2, acceptable_max=3.9),
            weight=1.5,
            description="RMSE for interpretable error magnitude",
            units="units"
        )
    ]

def create_mae_focused_config():
    """Configuration focused on MAE and robust metrics"""
    return [
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(excellent_max=0.5, good_max=1.5, acceptable_max=4.0),
            weight=2.0,  # Primary metric
            description="Mean Absolute Error - robust to outliers",
            units="units"
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=10.0, good_max=25.0, acceptable_max=50.0),
            weight=1.0,
            description="Oscillation detection for stability",
            units="%"
        )
    ]

def create_process_control_config():
    """Industrial process control configuration"""
    return [
        MetricConfiguration(
            metric_type=MetricType.VARIANCE_EXPLAINED,
            ranges=PerformanceRanges(excellent_max=0.98, good_max=0.90, acceptable_max=0.75),
            weight=1.5,
            description="Control system effectiveness",
            units="ratio",
            higher_is_better=True
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=8.0, good_max=20.0, acceptable_max=40.0),
            weight=1.2,
            description="Process stability assessment",
            units="%"
        ),
        MetricConfiguration(
            metric_type=MetricType.SETTLING_TIME,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=1.0,
            description="Response speed metric",
            units="% of dataset"
        )
    ]

def create_research_config():
    """Research-focused comprehensive analysis"""
    return [
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(excellent_max=2.0, good_max=8.0, acceptable_max=20.0),
            weight=1.0,
            description="MSE for mathematical analysis",
            units="(units)²"
        ),
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=2.5, acceptable_max=5.0),
            weight=1.0,
            description="MAE for comparison studies",
            units="units"
        ),
        MetricConfiguration(
            metric_type=MetricType.MAPE,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=0.8,
            description="Percentage-based error for reporting",
            units="%"
        ),
        MetricConfiguration(
            metric_type=MetricType.R_SQUARED,
            ranges=PerformanceRanges(excellent_max=0.95, good_max=0.85, acceptable_max=0.70),
            weight=1.0,
            description="Statistical correlation metric",
            units="R²",
            higher_is_better=True
        )
    ]

def demo_configurations():
    """Demonstrate different configurations"""

    configs = {
        "MSE-Focused (ML/Optimization)": create_mse_focused_config(),
        "MAE-Focused (Robust Control)": create_mae_focused_config(),
        "Process Control (Industrial)": create_process_control_config(),
        "Research (Comprehensive)": create_research_config()
    }

    dataset_path = "/Users/reh3376/repos/control_loop01/control_loop/.datasets/data_beerfeed_03_02-05_09-2025.csv"

    print("🔬 CONFIGURATION COMPARISON DEMO")
    print("=" * 80)

    results_summary = {}

    for config_name, config in configs.items():
        print(f"\n📊 Configuration: {config_name}")
        print("-" * 60)

        # Show configuration details
        print("📋 Metrics Configuration:")
        for metric_config in config:
            metric_name = metric_config.metric_type.value.upper()
            weight = metric_config.weight
            ranges = metric_config.ranges
            print(f"   {metric_name}: Weight={weight}, Range=({ranges.excellent_max}, {ranges.good_max}, {ranges.acceptable_max})")

        # Run analysis
        analyzer = ConfigurableControlLoopAnalyzer(config)
        try:
            results = analyzer.analyze_control_loop(dataset_path)

            # Store key results
            results_summary[config_name] = {
                "overall_score": results.overall_score,
                "classification": results.performance_classification["overall_classification"],
                "metric_count": len(results.metric_results)
            }

            print("\n🎯 Results:")
            print(f"   Overall Score: {results.overall_score:.1f}%")
            print(f"   Classification: {results.performance_classification['overall_classification'].upper()}")

            # Show metric results
            print("   Detailed Metrics:")
            for metric_name, result in results.metric_results.items():
                if "error" not in result:
                    value = result["value"]
                    classification = result["classification"]
                    weight = result["weight"]
                    print(f"     {metric_name.upper()}: {value:.4f} ({classification}) [weight: {weight}]")

        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            results_summary[config_name] = {"error": str(e)}

    # Comparison summary
    print("\n📊 CONFIGURATION COMPARISON SUMMARY")
    print("=" * 80)

    for config_name, result in results_summary.items():
        if "error" not in result:
            score = result["overall_score"]
            classification = result["classification"]
            metric_count = result["metric_count"]
            print(f"{config_name:30} | Score: {score:5.1f}% | Class: {classification:10} | Metrics: {metric_count}")
        else:
            print(f"{config_name:30} | ERROR: {result['error']}")

    print("\n💡 Key Insights:")
    print("   • Different configurations yield different performance assessments")
    print("   • Metric weights and ranges significantly impact overall scoring")
    print("   • Choose configuration based on your specific control objectives")
    print("   • MSE-focused configs are ideal for gradient-based optimization")
    print("   • MAE-focused configs are robust to outliers and noise")
    print("   • Process control configs emphasize stability and response")
    print("   • Research configs provide comprehensive analysis")

if __name__ == "__main__":
    demo_configurations()
