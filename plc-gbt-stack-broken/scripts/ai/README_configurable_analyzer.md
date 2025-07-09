# Configurable Control Loop Performance Analyzer

## Overview

Flexible control loop analyzer that accepts **configurable metrics** and **performance classification ranges** instead of being locked to specific metrics like MSE.

## Quick Start

```python
from configurable_control_loop_analyzer import (
    ConfigurableControlLoopAnalyzer, 
    MetricConfiguration, 
    PerformanceRanges, 
    MetricType
)

# 1. Define your metric configuration
config = [
    MetricConfiguration(
        metric_type=MetricType.MSE,  # Choose any metric
        ranges=PerformanceRanges(    # Set your thresholds
            excellent_max=1.0, 
            good_max=5.0, 
            acceptable_max=15.0
        ),
        weight=2.0,                  # Set importance weight
        description="Primary optimization metric",
        units="(units)²"
    ),
    # Add more metrics as needed...
]

# 2. Create analyzer with your configuration
analyzer = ConfigurableControlLoopAnalyzer(config)

# 3. Analyze your dataset
results = analyzer.analyze_control_loop("your_dataset.csv")
```

## Available Metrics

- **MSE** - Mean Squared Error (gradient-friendly)
- **MAE** - Mean Absolute Error (robust to outliers) 
- **RMSE** - Root Mean Squared Error (interpretable units)
- **MAPE** - Mean Absolute Percentage Error (scale-independent)
- **R_SQUARED** - Coefficient of determination (correlation)
- **VARIANCE_EXPLAINED** - Control system effectiveness
- **OSCILLATION_RATE** - Stability assessment  
- **SETTLING_TIME** - Response speed metric

## Pre-built Configurations

### MSE-Focused (ML/Optimization)
```python
def create_mse_config():
    return [
        MetricConfiguration(
            metric_type=MetricType.MSE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=5.0, acceptable_max=15.0),
            weight=2.0,  # Primary metric
            description="Gradient-descent optimizable metric"
        ),
        MetricConfiguration(
            metric_type=MetricType.RMSE,
            ranges=PerformanceRanges(excellent_max=1.0, good_max=2.2, acceptable_max=3.9),
            weight=1.5,
            description="Interpretable error magnitude"
        )
    ]
```

### MAE-Focused (Robust Control)
```python  
def create_mae_config():
    return [
        MetricConfiguration(
            metric_type=MetricType.MAE,
            ranges=PerformanceRanges(excellent_max=0.5, good_max=1.5, acceptable_max=4.0),
            weight=2.0,  # Primary metric
            description="Outlier-resistant metric"
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=10.0, good_max=25.0, acceptable_max=50.0),
            weight=1.0,
            description="Stability assessment"
        )
    ]
```

### Industrial Process Control
```python
def create_process_config():
    return [
        MetricConfiguration(
            metric_type=MetricType.VARIANCE_EXPLAINED,
            ranges=PerformanceRanges(excellent_max=0.98, good_max=0.90, acceptable_max=0.75),
            weight=1.5,
            description="Control effectiveness",
            higher_is_better=True  # Higher variance explained = better
        ),
        MetricConfiguration(
            metric_type=MetricType.OSCILLATION_RATE,
            ranges=PerformanceRanges(excellent_max=8.0, good_max=20.0, acceptable_max=40.0),
            weight=1.2,
            description="Process stability"
        ),
        MetricConfiguration(
            metric_type=MetricType.SETTLING_TIME,
            ranges=PerformanceRanges(excellent_max=5.0, good_max=15.0, acceptable_max=30.0),
            weight=1.0,
            description="Response speed"
        )
    ]
```

## Configuration Options

### MetricConfiguration Parameters
- **metric_type**: Choose from MetricType enum
- **ranges**: PerformanceRanges object with thresholds
- **weight**: Importance weight (default: 1.0)  
- **description**: Human-readable description
- **units**: Measurement units for display
- **higher_is_better**: True for metrics where higher = better (default: False)

### PerformanceRanges Parameters
- **excellent_max**: Upper bound for "excellent" classification
- **good_max**: Upper bound for "good" classification  
- **acceptable_max**: Upper bound for "acceptable" classification
- Values above acceptable_max are classified as "poor"

## Use Cases

| Configuration | Best For | Key Metrics |
|---------------|----------|-------------|
| **MSE-Focused** | ML optimization, gradient descent | MSE, RMSE |
| **MAE-Focused** | Robust control, noisy environments | MAE, Oscillation |
| **Process Control** | Industrial applications | Variance Explained, Stability |
| **Research** | Comprehensive analysis | MSE, MAE, MAPE, R² |

## Example Results

Same dataset, different configurations:

- **MSE-Focused**: 50.0% (Acceptable) - Focuses on differentiability
- **MAE-Focused**: 58.3% (Acceptable) - Emphasizes robustness  
- **Process Control**: 45.3% (Poor) - Strict stability requirements
- **Research**: 67.1% (Acceptable) - Balanced comprehensive view

## Benefits

✅ **Flexible**: Not locked to any specific metric  
✅ **Configurable**: Custom thresholds for your application  
✅ **Weighted**: Emphasize important metrics  
✅ **Extensible**: Easy to add new metrics  
✅ **Comparable**: Consistent interface across configurations  
✅ **Industrial**: Ready for production use  

## File Locations

- **Main Analyzer**: `scripts/ai/configurable_control_loop_analyzer.py`
- **Demo Script**: `scripts/ai/demo_custom_configurations.py`
- **This Guide**: `scripts/ai/README_configurable_analyzer.md` 