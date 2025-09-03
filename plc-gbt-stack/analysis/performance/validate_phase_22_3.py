#!/usr/bin/env python3
"""
Phase 22.3: Performance Analysis Suite Validation
================================================

Comprehensive validation of all Phase 22.3 tasks:
- Task 22.3.1: Performance Metrics
- Task 22.3.2: Stability Analysis
- Task 22.3.3: Disturbance Analysis
- Task 22.3.4: Benchmarking System

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.3 - Performance Analysis Suite Validation
Methodology: AI Task Orchestrator Guide
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

import numpy as np

# Add parent directories to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import performance analysis modules
    from benchmarking import (
        BENCHMARKING_CONFIG,
        BenchmarkType,
        PerformanceLevel,
        analyze_trend_direction,
        assess_performance_level,
        get_available_benchmarks,
    )
    from disturbance import (
        DISTURBANCE_CONFIG,
        DisturbanceType,
        RejectionPerformance,
        assess_rejection_performance,
        calculate_disturbance_metrics,
    )
    from disturbance import get_available_analyses as get_disturbance_analyses
    from performance import (
        PERFORMANCE_CONFIG,
        PerformanceGrade,
        PerformanceMetric,
        calculate_performance_grade,
        get_available_metrics,
        get_performance_recommendations,
    )
    from stability import (
        STABILITY_CONFIG,
        StabilityAnalysisType,
        StabilityStatus,
        assess_stability_margins,
        generate_stability_recommendations,
    )
    from stability import get_available_analyses as get_stability_analyses

    IMPORTS_SUCCESSFUL = True
    import_errors = []

except ImportError as e:
    IMPORTS_SUCCESSFUL = False
    import_errors = [str(e)]
    print(f"❌ Import Error: {e}")

def generate_test_data() -> Dict[str, np.ndarray]:
    """Generate synthetic test data for validation"""

    # Time vector (10 minutes of data at 1 Hz)
    time = np.linspace(0, 600, 600)

    # Process parameters
    K = 1.2  # Process gain
    tau = 15.0  # Time constant
    theta = 2.0  # Dead time

    # Setpoint profile with step changes
    setpoint = np.ones_like(time) * 50.0
    setpoint[200:400] = 60.0  # Step change at t=200s
    setpoint[500:] = 45.0     # Another step at t=500s

    # Simulate process response (simplified FOPDT)
    process_variable = np.zeros_like(time)
    control_output = np.zeros_like(time)

    # PID parameters
    Kp = 0.8
    Ti = 12.0
    Td = 2.0

    # Simple PID simulation
    integral = 0
    previous_error = 0
    dt = time[1] - time[0]

    for i in range(1, len(time)):
        # Error calculation
        error = setpoint[i] - process_variable[i-1]

        # PID calculation
        proportional = Kp * error
        integral += error * dt
        derivative = (error - previous_error) / dt

        control_output[i] = proportional + Kp/Ti * integral + Kp*Td * derivative

        # Process simulation (simplified)
        if i >= int(theta/dt):  # Account for dead time
            process_variable[i] = (process_variable[i-1] +
                                 dt/tau * (K * control_output[i-int(theta/dt)] - process_variable[i-1]))
        else:
            process_variable[i] = process_variable[i-1]

        previous_error = error

    # Add some noise
    measurement_noise = np.random.normal(0, 0.1, len(time))
    process_variable += measurement_noise

    # Add disturbance at t=300s
    disturbance = np.zeros_like(time)
    disturbance[300:] = -2.0  # Load disturbance
    process_variable[300:] += np.cumsum(disturbance[300:]) * dt / tau

    return {
        'time': time,
        'setpoint': setpoint,
        'process_variable': process_variable,
        'control_output': control_output,
        'disturbance': disturbance,
        'error': setpoint - process_variable
    }

def validate_task_22_3_1_performance_metrics() -> Dict[str, Any]:
    """Validate Task 22.3.1: Performance Metrics"""

    print("🎯 Testing Task 22.3.1: Performance Metrics")
    print("-" * 50)

    results = {
        "task": "22.3.1 - Performance Metrics",
        "tests": [],
        "overall_success": True
    }

    try:
        # Test 1: Available metrics
        available_metrics = get_available_metrics()
        test_1 = {
            "name": "Available Metrics Check",
            "success": len(available_metrics) >= 8,
            "details": f"Found {len(available_metrics)} metrics: {available_metrics}",
            "expected": "At least 8 metrics (IAE, ISE, ITAE, settling_time, overshoot, etc.)"
        }
        results["tests"].append(test_1)
        print(f"    {'✅' if test_1['success'] else '❌'} {test_1['name']}: {test_1['details']}")

        # Test 2: Configuration validation
        config_valid = (
            'supported_metrics' in PERFORMANCE_CONFIG and
            'default_settings' in PERFORMANCE_CONFIG and
            'performance_targets' in PERFORMANCE_CONFIG
        )
        test_2 = {
            "name": "Configuration Validation",
            "success": config_valid,
            "details": f"Configuration keys present: {list(PERFORMANCE_CONFIG.keys())}",
            "expected": "All required configuration sections present"
        }
        results["tests"].append(test_2)
        print(f"    {'✅' if test_2['success'] else '❌'} {test_2['name']}: {test_2['details']}")

        # Test 3: Performance grade calculation
        test_metrics = {
            'iae': 25.0,
            'settling_time': 45.0,
            'overshoot': 0.08,
            'gain_margin': 8.5,
            'phase_margin': 65.0
        }
        grade = calculate_performance_grade(test_metrics)
        test_3 = {
            "name": "Performance Grade Calculation",
            "success": isinstance(grade, PerformanceGrade),
            "details": f"Calculated grade: {grade.value}",
            "expected": "Valid PerformanceGrade enum value"
        }
        results["tests"].append(test_3)
        print(f"    {'✅' if test_3['success'] else '❌'} {test_3['name']}: {test_3['details']}")

        # Test 4: Recommendations generation
        recommendations = get_performance_recommendations(test_metrics, grade)
        test_4 = {
            "name": "Recommendations Generation",
            "success": isinstance(recommendations, list) and len(recommendations) > 0,
            "details": f"Generated {len(recommendations)} recommendations",
            "expected": "List of actionable recommendations"
        }
        results["tests"].append(test_4)
        print(f"    {'✅' if test_4['success'] else '❌'} {test_4['name']}: {test_4['details']}")

        # Update overall success
        results["overall_success"] = all(test["success"] for test in results["tests"])

    except Exception as e:
        results["overall_success"] = False
        results["error"] = str(e)
        print(f"    ❌ Task 22.3.1 failed with error: {e}")

    return results

def validate_task_22_3_2_stability_analysis() -> Dict[str, Any]:
    """Validate Task 22.3.2: Stability Analysis"""

    print("\n🎯 Testing Task 22.3.2: Stability Analysis")
    print("-" * 50)

    results = {
        "task": "22.3.2 - Stability Analysis",
        "tests": [],
        "overall_success": True
    }

    try:
        # Test 1: Available analyses
        available_analyses = get_stability_analyses()
        test_1 = {
            "name": "Available Analyses Check",
            "success": len(available_analyses) >= 4,
            "details": f"Found {len(available_analyses)} analyses: {available_analyses}",
            "expected": "At least 4 analyses (nyquist, bode, root_locus, sensitivity)"
        }
        results["tests"].append(test_1)
        print(f"    {'✅' if test_1['success'] else '❌'} {test_1['name']}: {test_1['details']}")

        # Test 2: Stability assessment
        gain_margin = 8.5  # dB
        phase_margin = 65.0  # degrees
        stability_status = assess_stability_margins(gain_margin, phase_margin)
        test_2 = {
            "name": "Stability Assessment",
            "success": isinstance(stability_status, StabilityStatus),
            "details": f"Assessed stability: {stability_status.value}",
            "expected": "Valid StabilityStatus enum value"
        }
        results["tests"].append(test_2)
        print(f"    {'✅' if test_2['success'] else '❌'} {test_2['name']}: {test_2['details']}")

        # Test 3: Stability recommendations
        margins = {'gain_margin': gain_margin, 'phase_margin': phase_margin}
        recommendations = generate_stability_recommendations(stability_status, None, margins)
        test_3 = {
            "name": "Stability Recommendations",
            "success": isinstance(recommendations, list) and len(recommendations) > 0,
            "details": f"Generated {len(recommendations)} recommendations",
            "expected": "List of stability recommendations"
        }
        results["tests"].append(test_3)
        print(f"    {'✅' if test_3['success'] else '❌'} {test_3['name']}: {test_3['details']}")

        # Test 4: Configuration validation
        config_valid = (
            'supported_analyses' in STABILITY_CONFIG and
            'default_settings' in STABILITY_CONFIG and
            'plot_settings' in STABILITY_CONFIG
        )
        test_4 = {
            "name": "Stability Configuration",
            "success": config_valid,
            "details": f"Configuration sections: {list(STABILITY_CONFIG.keys())}",
            "expected": "All required configuration sections present"
        }
        results["tests"].append(test_4)
        print(f"    {'✅' if test_4['success'] else '❌'} {test_4['name']}: {test_4['details']}")

        # Update overall success
        results["overall_success"] = all(test["success"] for test in results["tests"])

    except Exception as e:
        results["overall_success"] = False
        results["error"] = str(e)
        print(f"    ❌ Task 22.3.2 failed with error: {e}")

    return results

def validate_task_22_3_3_disturbance_analysis() -> Dict[str, Any]:
    """Validate Task 22.3.3: Disturbance Analysis"""

    print("\n🎯 Testing Task 22.3.3: Disturbance Analysis")
    print("-" * 50)

    results = {
        "task": "22.3.3 - Disturbance Analysis",
        "tests": [],
        "overall_success": True
    }

    try:
        # Test 1: Available analyses
        available_analyses = get_disturbance_analyses()
        test_1 = {
            "name": "Available Analyses Check",
            "success": len(available_analyses) >= 5,
            "details": f"Found {len(available_analyses)} analyses: {available_analyses[:3]}...",
            "expected": "At least 5 analyses (load rejection, tracking, noise, feedforward, etc.)"
        }
        results["tests"].append(test_1)
        print(f"    {'✅' if test_1['success'] else '❌'} {test_1['name']}: {test_1['details']}")

        # Test 2: Rejection performance assessment
        rejection_ratio = 0.85
        settling_time = 45.0
        steady_state_error = 0.015
        rejection_perf = assess_rejection_performance(rejection_ratio, settling_time, steady_state_error)
        test_2 = {
            "name": "Rejection Performance Assessment",
            "success": isinstance(rejection_perf, RejectionPerformance),
            "details": f"Assessed performance: {rejection_perf.value}",
            "expected": "Valid RejectionPerformance enum value"
        }
        results["tests"].append(test_2)
        print(f"    {'✅' if test_2['success'] else '❌'} {test_2['name']}: {test_2['details']}")

        # Test 3: Disturbance metrics calculation
        test_data = generate_test_data()
        disturbance_data = {'disturbance_start': 300, 'disturbance_end': 350}
        metrics = calculate_disturbance_metrics(test_data, disturbance_data)
        test_3 = {
            "name": "Disturbance Metrics Calculation",
            "success": isinstance(metrics, dict) and len(metrics) >= 3,
            "details": f"Calculated {len(metrics)} metrics: {list(metrics.keys())}",
            "expected": "Dictionary with disturbance performance metrics"
        }
        results["tests"].append(test_3)
        print(f"    {'✅' if test_3['success'] else '❌'} {test_3['name']}: {test_3['details']}")

        # Test 4: Configuration validation
        config_valid = (
            'supported_analyses' in DISTURBANCE_CONFIG and
            'default_settings' in DISTURBANCE_CONFIG and
            'performance_criteria' in DISTURBANCE_CONFIG['default_settings']
        )
        test_4 = {
            "name": "Disturbance Configuration",
            "success": config_valid,
            "details": f"Configuration sections: {list(DISTURBANCE_CONFIG.keys())}",
            "expected": "All required configuration sections present"
        }
        results["tests"].append(test_4)
        print(f"    {'✅' if test_4['success'] else '❌'} {test_4['name']}: {test_4['details']}")

        # Update overall success
        results["overall_success"] = all(test["success"] for test in results["tests"])

    except Exception as e:
        results["overall_success"] = False
        results["error"] = str(e)
        print(f"    ❌ Task 22.3.3 failed with error: {e}")

    return results

def validate_task_22_3_4_benchmarking_system() -> Dict[str, Any]:
    """Validate Task 22.3.4: Benchmarking System"""

    print("\n🎯 Testing Task 22.3.4: Benchmarking System")
    print("-" * 50)

    results = {
        "task": "22.3.4 - Benchmarking System",
        "tests": [],
        "overall_success": True
    }

    try:
        # Test 1: Available benchmarks
        available_benchmarks = get_available_benchmarks()
        test_1 = {
            "name": "Available Benchmarks Check",
            "success": len(available_benchmarks) >= 6,
            "details": f"Found {len(available_benchmarks)} benchmarks: {available_benchmarks[:3]}...",
            "expected": "At least 6 benchmark types"
        }
        results["tests"].append(test_1)
        print(f"    {'✅' if test_1['success'] else '❌'} {test_1['name']}: {test_1['details']}")

        # Test 2: Performance level assessment
        metric_value = 0.8
        benchmarks = {"excellent": 0.9, "good": 0.7, "acceptable": 0.5}
        perf_level = assess_performance_level(metric_value, benchmarks, higher_is_better=True)
        test_2 = {
            "name": "Performance Level Assessment",
            "success": isinstance(perf_level, PerformanceLevel),
            "details": f"Assessed level: {perf_level.value}",
            "expected": "Valid PerformanceLevel enum value"
        }
        results["tests"].append(test_2)
        print(f"    {'✅' if test_2['success'] else '❌'} {test_2['name']}: {test_2['details']}")

        # Test 3: Trend analysis
        time_series = [1.0, 1.1, 1.2, 1.15, 1.25, 1.3, 1.28, 1.35, 1.4, 1.38, 1.45]
        trend = analyze_trend_direction(time_series)
        test_3 = {
            "name": "Trend Analysis",
            "success": hasattr(trend, 'value'),
            "details": f"Detected trend: {trend.value if hasattr(trend, 'value') else 'Unknown'}",
            "expected": "Valid trend direction"
        }
        results["tests"].append(test_3)
        print(f"    {'✅' if test_3['success'] else '❌'} {test_3['name']}: {test_3['details']}")

        # Test 4: Industry standards
        industry_standards = BENCHMARKING_CONFIG.get('industry_standards', {})
        test_4 = {
            "name": "Industry Standards Database",
            "success": len(industry_standards) >= 2,
            "details": f"Available standards: {list(industry_standards.keys())}",
            "expected": "Multiple industry standard databases"
        }
        results["tests"].append(test_4)
        print(f"    {'✅' if test_4['success'] else '❌'} {test_4['name']}: {test_4['details']}")

        # Update overall success
        results["overall_success"] = all(test["success"] for test in results["tests"])

    except Exception as e:
        results["overall_success"] = False
        results["error"] = str(e)
        print(f"    ❌ Task 22.3.4 failed with error: {e}")

    return results

def run_comprehensive_validation() -> Dict[str, Any]:
    """Run comprehensive Phase 22.3 validation"""

    print("🧪 Phase 22.3: Performance Analysis Suite Validation")
    print("=" * 80)

    start_time = time.time()

    # Check imports first
    if not IMPORTS_SUCCESSFUL:
        print(f"❌ Import failures: {import_errors}")
        return {
            "phase": "22.3",
            "status": "FAILED - Import errors",
            "import_errors": import_errors,
            "timestamp": datetime.now().isoformat()
        }

    # Run all task validations
    task_results = []

    # Task 22.3.1: Performance Metrics
    task_22_3_1 = validate_task_22_3_1_performance_metrics()
    task_results.append(task_22_3_1)

    # Task 22.3.2: Stability Analysis
    task_22_3_2 = validate_task_22_3_2_stability_analysis()
    task_results.append(task_22_3_2)

    # Task 22.3.3: Disturbance Analysis
    task_22_3_3 = validate_task_22_3_3_disturbance_analysis()
    task_results.append(task_22_3_3)

    # Task 22.3.4: Benchmarking System
    task_22_3_4 = validate_task_22_3_4_benchmarking_system()
    task_results.append(task_22_3_4)

    # Calculate overall results
    total_tests = sum(len(task["tests"]) for task in task_results)
    passed_tests = sum(len([test for test in task["tests"] if test["success"]]) for task in task_results)
    overall_success = all(task["overall_success"] for task in task_results)

    execution_time = time.time() - start_time

    # Summary
    print("\n" + "=" * 80)
    print("🏁 PHASE 22.3 PERFORMANCE ANALYSIS SUITE - VALIDATION SUMMARY")
    print("=" * 80)
    print("📊 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {total_tests - passed_tests} ❌")
    print(f"   Success Rate: {passed_tests/total_tests*100:.1f}%")
    print(f"   Overall Status: {'✅ PASSED' if overall_success else '❌ FAILED'}")
    print(f"   Execution Time: {execution_time:.3f}s")

    print("\n📋 TASK RESULTS:")
    for task in task_results:
        task_passed = len([test for test in task["tests"] if test["success"]])
        task_total = len(task["tests"])
        status = "✅" if task["overall_success"] else "❌"
        print(f"   {status} {task['task']}: {task_passed}/{task_total} tests passed")

    # Phase completion assessment
    completion_percentage = passed_tests / total_tests * 100
    if completion_percentage >= 90:
        completion_status = "✅ PHASE 22.3 COMPLETED SUCCESSFULLY"
        recommendations = ["Phase 22.3 Performance Analysis Suite is production ready"]
    elif completion_percentage >= 75:
        completion_status = "⚠️ PHASE 22.3 MOSTLY COMPLETE"
        recommendations = ["Minor fixes needed before production deployment"]
    else:
        completion_status = "❌ PHASE 22.3 NEEDS SIGNIFICANT WORK"
        recommendations = ["Major implementation work required"]

    print("\n🎯 PHASE 22.3 COMPLETION STATUS:")
    print(f"   {completion_status}")
    print(f"   Completion Score: {completion_percentage:.1f}%")

    print("\n💡 RECOMMENDATIONS:")
    for rec in recommendations:
        print(f"   • {rec}")

    # Create comprehensive results
    validation_results = {
        "phase": "22.3 - Performance Analysis Suite",
        "timestamp": datetime.now().isoformat(),
        "execution_time": execution_time,
        "overall_success": overall_success,
        "completion_percentage": completion_percentage,
        "completion_status": completion_status,
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "task_results": task_results,
        "recommendations": recommendations,
        "deliverables_status": {
            "performance_metrics": task_22_3_1["overall_success"],
            "stability_analysis": task_22_3_2["overall_success"],
            "disturbance_analysis": task_22_3_3["overall_success"],
            "benchmarking_system": task_22_3_4["overall_success"]
        }
    }

    return validation_results

def main():
    """Main validation function"""

    # Run comprehensive validation
    results = run_comprehensive_validation()

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"phase_22_3_validation_results_{timestamp}.json"

    try:
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📁 Results saved to: {results_file}")
    except Exception as e:
        print(f"\n⚠️ Could not save results: {e}")

    return results

if __name__ == "__main__":
    main()
