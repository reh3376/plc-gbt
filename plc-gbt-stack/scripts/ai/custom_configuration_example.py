#!/usr/bin/env python3
"""
Custom Configuration Example
============================

Demonstrates creating a completely custom configuration for a specific control scenario.
Example: Temperature Control System with Strict Requirements
"""

from configurable_control_loop_analyzer import (
    ConfigurableControlLoopAnalyzer,
    MetricConfiguration,
    MetricType,
    PerformanceRanges,
)


def create_temperature_control_config():
    """
    Custom configuration for a temperature control system

    Requirements:
    - Very strict error tolerance (±0.2°C excellent, ±0.5°C acceptable)
    - Oscillation must be minimal for sensitive process
    - Settling time critical for production efficiency
    - Higher weight on stability than raw error metrics
    """
    return [
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(
                excellent_max=0.2,    # ±0.2°C excellent
                good_max=0.35,        # ±0.35°C good
                acceptable_max=0.5    # ±0.5°C acceptable
            ),
            weight=1.2,
            description="Temperature deviation tolerance",
            units="°C"
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(
                excellent_max=2.0,    # < 2% oscillation excellent
                good_max=5.0,         # < 5% oscillation good
                acceptable_max=8.0    # < 8% oscillation acceptable
            ),
            weight=2.0,  # Highest priority - stability critical
            description="Temperature stability (oscillation control)",
            units="% oscillation"
        ),
        MetricConfiguration(
            metric_type=MetricType.SETTLING_TIME,
            ranges=PerformanceRanges(
                excellent_max=2.0,    # Settle within 2% of dataset
                good_max=5.0,         # Settle within 5% of dataset
                acceptable_max=10.0   # Settle within 10% of dataset
            ),
            weight=1.5,
            description="Time to reach temperature setpoint",
            units="% of process time"
        ),
        MetricConfiguration(
            metric_type=MetricType.RMSE,
            ranges=PerformanceRanges(
                excellent_max=0.25,   # Very tight RMSE
                good_max=0.4,         # Moderate RMSE
                acceptable_max=0.6    # Maximum acceptable RMSE
            ),
            weight=1.0,
            description="Overall temperature variance",
            units="°C"
        )
    ]

def create_flow_control_config():
    """
    Custom configuration for flow control system

    Requirements:
    - Flow rate accuracy within ±2% (excellent), ±5% (acceptable)
    - Percentage-based metrics more relevant than absolute
    - Less strict on oscillation (flow systems naturally oscillate)
    - High weight on percentage accuracy
    """
    return [
        MetricConfiguration(
            metric_type=MetricType.MAPE,
            ranges=PerformanceRanges(
                excellent_max=2.0,    # ±2% flow accuracy excellent
                good_max=3.5,         # ±3.5% flow accuracy good
                acceptable_max=5.0    # ±5% flow accuracy acceptable
            ),
            weight=2.5,  # Primary metric for flow control
            description="Flow rate percentage accuracy",
            units="% error"
        ),
        MetricConfiguration(
            metric_type=MetricType.VARIANCE_EXPLAINED,
            ranges=PerformanceRanges(
                excellent_max=0.96,   # 96% variance explained excellent
                good_max=0.90,        # 90% variance explained good
                acceptable_max=0.80   # 80% variance explained acceptable
            ),
            weight=1.5,
            description="Control system effectiveness for flow",
            units="ratio",
            higher_is_better=True
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(
                excellent_max=15.0,   # More lenient for flow systems
                good_max=25.0,        # Flow systems can oscillate more
                acceptable_max=40.0   # Still need reasonable stability
            ),
            weight=0.8,  # Lower priority for flow control
            description="Flow oscillation tolerance",
            units="% oscillation"
        )
    ]

def create_pressure_control_config():
    """
    Custom configuration for pressure control system

    Requirements:
    - Safety critical - pressure must be very stable
    - MSE important for detecting dangerous pressure spikes
    - Very low tolerance for oscillation (safety)
    - Quick settling required for safety systems
    """
    return [
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(
                excellent_max=0.1,    # Very tight MSE for safety
                good_max=0.5,         # Moderate MSE
                acceptable_max=1.0    # Maximum safe MSE
            ),
            weight=2.0,  # High weight - safety critical
            description="Pressure variance (safety metric)",
            units="(PSI)²"
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(
                excellent_max=1.0,    # Extremely low oscillation
                good_max=3.0,         # Low oscillation
                acceptable_max=5.0    # Maximum safe oscillation
            ),
            weight=2.5,  # Highest weight - safety critical
            description="Pressure stability (safety critical)",
            units="% oscillation"
        ),
        MetricConfiguration(
            metric_type=MetricType.SETTLING_TIME,
            ranges=PerformanceRanges(
                excellent_max=1.0,    # Very fast settling for safety
                good_max=3.0,         # Fast settling
                acceptable_max=5.0    # Maximum acceptable settling time
            ),
            weight=1.8,
            description="Emergency response speed",
            units="% of process time"
        ),
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(
                excellent_max=0.15,   # Very tight absolute error
                good_max=0.3,         # Moderate absolute error
                acceptable_max=0.5    # Maximum safe absolute error
            ),
            weight=1.5,
            description="Average pressure deviation",
            units="PSI"
        )
    ]

def demo_custom_configurations():
    """Demonstrate the custom configurations"""

    configs = {
        "Temperature Control (Strict)": create_temperature_control_config(),
        "Flow Control (Percentage-based)": create_flow_control_config(),
        "Pressure Control (Safety-critical)": create_pressure_control_config()
    }

    print("🎛️ CUSTOM CONTROL SYSTEM CONFIGURATIONS")
    print("=" * 80)

    for config_name, config in configs.items():
        print(f"\n📊 {config_name}")
        print("-" * 60)

        print("📋 Configuration Details:")
        total_weight = sum(metric.weight for metric in config)

        for metric_config in config:
            metric_name = metric_config.metric_type.value.upper()
            weight = metric_config.weight
            weight_pct = (weight / total_weight) * 100
            ranges = metric_config.ranges
            units = metric_config.units
            description = metric_config.description

            print(f"   {metric_name}:")
            print(f"     Weight: {weight} ({weight_pct:.1f}% of total)")
            print(f"     Ranges: Excellent ≤ {ranges.excellent_max}{units}")
            print(f"             Good ≤ {ranges.good_max}{units}")
            print(f"             Acceptable ≤ {ranges.acceptable_max}{units}")
            print(f"     Purpose: {description}")
            print()

        print(f"   Total Weight: {total_weight}")
        print(f"   Metrics Count: {len(config)}")

        # Show what makes this configuration unique
        if "Temperature" in config_name:
            print("\n🌡️ Temperature Control Focus:")
            print("   • Very strict error tolerance (±0.2°C excellent)")
            print("   • Oscillation heavily weighted (40% of score)")
            print("   • Settling time critical for production")

        elif "Flow" in config_name:
            print("\n🌊 Flow Control Focus:")
            print("   • Percentage-based accuracy (MAPE = 50% of score)")
            print("   • More lenient oscillation limits (flow systems)")
            print("   • Control effectiveness emphasized")

        elif "Pressure" in config_name:
            print("\n⚠️ Pressure Control Focus:")
            print("   • Safety-critical configuration")
            print("   • MSE detects dangerous spikes")
            print("   • Extremely low oscillation tolerance")
            print("   • Fast emergency response required")

def analyze_with_custom_config():
    """Example of running analysis with custom configuration"""

    print("\n🔬 RUNNING CUSTOM ANALYSIS EXAMPLE")
    print("=" * 80)

    # Use temperature control config as example
    config = create_temperature_control_config()
    analyzer = ConfigurableControlLoopAnalyzer(config)

    dataset_path = "/Users/reh3376/repos/control_loop01/control_loop/.datasets/data_beerfeed_03_02-05_09-2025.csv"

    try:
        print("🚀 Analyzing with Temperature Control Configuration...")
        results = analyzer.analyze_control_loop(dataset_path)

        print("\n📊 Results Summary:")
        print(f"   Overall Score: {results.overall_score:.1f}%")
        print(f"   Classification: {results.performance_classification['overall_classification'].upper()}")

        print("\n🧮 Metric Performance:")
        for metric_name, result in results.metric_results.items():
            if "error" not in result:
                value = result["value"]
                classification = result["classification"]
                weight = result["weight"]
                units = result["units"]

                print(f"   {metric_name.upper()}: {value:.4f} {units}")
                print(f"     Classification: {classification.upper()}")
                print(f"     Weight: {weight} (contribution to overall score)")

        print("\n💡 Key Insights:")
        print("   • This configuration emphasizes oscillation control")
        print("   • Temperature-specific thresholds applied")
        print("   • Safety and stability prioritized over raw performance")

    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    demo_custom_configurations()
    analyze_with_custom_config()
