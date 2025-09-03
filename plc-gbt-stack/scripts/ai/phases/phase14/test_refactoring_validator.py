#!/usr/bin/env python3
"""
Phase 14.2.3: RefactoringValidator Simple Test Suite
===================================================

Simple testing suite for the RefactoringValidator to validate core functionality.

Author: AI Task Orchestrator
Date: 2025-01-18
"""

import sys
from pathlib import Path

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
sys.path.append(str(Path(__file__).parent))

def test_refactoring_validator_basic():
    """Test basic RefactoringValidator functionality"""
    print("🧪 Testing RefactoringValidator Basic Functionality")

    try:
        from refactoring_validator import (
            PerformanceComparison,
            RefactoringValidator,
            SafetyValidationResult,
            TestResult,
            ValidationReport,
        )

        # Test 1: Basic initialization
        print("  ➤ Testing initialization...")
        validator = RefactoringValidator("test_validation")
        assert validator.task_id == "test_validation"
        assert validator.validation_config["safety_validation"]["min_safety_score"] == 0.8
        assert validator.validation_config["testing"]["min_coverage"] == 70.0
        print("    ✅ Initialization successful")

        # Test 2: Data class creation
        print("  ➤ Testing data class creation...")

        # Test SafetyValidationResult creation
        safety_result = SafetyValidationResult(
            validation_id="test_safety_001",
            file_path="test.py",
            safety_score=0.85,
            issues_found=["minor issue"],
            critical_issues=[],
            warnings=["warning message"],
            recommendations=["improve documentation"],
            validation_passed=True
        )
        assert safety_result.validation_id == "test_safety_001"
        assert safety_result.validation_passed
        print("    ✅ SafetyValidationResult creation successful")

        # Test TestResult creation
        test_result = TestResult(
            test_id="test_run_001",
            test_type="unit",
            files_tested=["test1.py", "test2.py"],
            tests_run=25,
            tests_passed=23,
            tests_failed=2,
            test_duration=45.2,
            coverage_percentage=82.5,
            failure_details=["test_a failed", "test_b failed"],
            success=True
        )
        assert test_result.test_id == "test_run_001"
        assert test_result.tests_run == 25
        print("    ✅ TestResult creation successful")

        # Test PerformanceComparison creation
        perf_comparison = PerformanceComparison(
            comparison_id="perf_comp_001",
            original_file="original.py",
            refactored_files=["refactored1.py", "refactored2.py"],
            metrics={"execution_time": {"original": 1.5, "refactored": 1.2}},
            performance_change=0.2,  # 20% improvement
            regression_detected=False,
            benchmark_results={"iterations": 5}
        )
        assert perf_comparison.comparison_id == "perf_comp_001"
        assert not perf_comparison.regression_detected
        print("    ✅ PerformanceComparison creation successful")

        # Test 3: Configuration validation
        print("  ➤ Testing configuration...")
        config = validator.validation_config

        # Check safety validation config
        assert "min_safety_score" in config["safety_validation"]
        assert "check_syntax" in config["safety_validation"]
        assert "check_imports" in config["safety_validation"]

        # Check testing config
        assert "run_unit_tests" in config["testing"]
        assert "min_coverage" in config["testing"]
        assert "test_timeout" in config["testing"]

        # Check performance config
        assert "benchmark_iterations" in config["performance"]
        assert "max_regression_threshold" in config["performance"]

        print("    ✅ Configuration validation successful")

        # Test 4: Component integration
        print("  ➤ Testing component integration...")

        # Check that dependencies are initialized
        assert hasattr(validator, 'codebase_analyzer')
        assert hasattr(validator, 'modular_extractor')
        assert hasattr(validator, 'quality_optimizer')

        print("    ✅ Component integration successful")

        print("✅ All basic tests passed!")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_safety_validation():
    """Test safety validation functionality"""
    print("🧪 Testing Safety Validation")

    try:
        from refactoring_validator import RefactoringValidator

        validator = RefactoringValidator("test_safety")

        # Create mock refactoring plan
        mock_plan = type('MockPlan', (), {
            'source_file': __file__,  # Use this test file
            'target_files': ['extracted1.py', 'extracted2.py']
        })()

        print("  ➤ Testing safety validation...")
        safety_result = validator.validate_refactoring_safety(mock_plan)

        # Validate result structure
        assert hasattr(safety_result, 'validation_id')
        assert hasattr(safety_result, 'safety_score')
        assert hasattr(safety_result, 'validation_passed')

        print(f"    📊 Safety Score: {safety_result.safety_score:.2f}")
        print(f"    📊 Issues Found: {len(safety_result.issues_found)}")
        print(f"    📊 Validation Passed: {safety_result.validation_passed}")

        # Safety score should be reasonable (0-1 range)
        assert 0 <= safety_result.safety_score <= 1

        print("✅ Safety validation tests passed!")
        return True

    except Exception as e:
        print(f"❌ Safety validation test failed: {e}")
        return False

def test_automated_testing():
    """Test automated testing functionality"""
    print("🧪 Testing Automated Testing")

    try:
        from refactoring_validator import RefactoringValidator

        validator = RefactoringValidator("test_automated")

        # Test automated testing with mock files
        test_files = ["test_file1.py", "test_file2.py"]

        print("  ➤ Testing automated test execution...")
        test_result = validator.run_automated_tests(test_files)

        # Validate result structure
        assert hasattr(test_result, 'test_id')
        assert hasattr(test_result, 'tests_run')
        assert hasattr(test_result, 'tests_passed')
        assert hasattr(test_result, 'coverage_percentage')

        print(f"    📊 Tests Run: {test_result.tests_run}")
        print(f"    📊 Tests Passed: {test_result.tests_passed}")
        print(f"    📊 Coverage: {test_result.coverage_percentage:.1f}%")
        print(f"    📊 Success: {test_result.success}")

        # Test metrics should be reasonable
        assert test_result.tests_run >= 0
        assert 0 <= test_result.coverage_percentage <= 100

        print("✅ Automated testing tests passed!")
        return True

    except Exception as e:
        print(f"❌ Automated testing test failed: {e}")
        return False

def test_performance_regression():
    """Test performance regression checking"""
    print("🧪 Testing Performance Regression Check")

    try:
        from refactoring_validator import RefactoringValidator

        validator = RefactoringValidator("test_performance")

        # Test performance regression check with mock files
        original_file = "original_code.py"
        refactored_files = ["refactored1.py", "refactored2.py"]

        print("  ➤ Testing performance regression check...")
        perf_result = validator.performance_regression_check(original_file, refactored_files)

        # Validate result structure
        assert hasattr(perf_result, 'comparison_id')
        assert hasattr(perf_result, 'performance_change')
        assert hasattr(perf_result, 'regression_detected')
        assert hasattr(perf_result, 'metrics')

        print(f"    📊 Performance Change: {perf_result.performance_change:.2%}")
        print(f"    📊 Regression Detected: {perf_result.regression_detected}")
        print(f"    📊 Metrics Categories: {len(perf_result.metrics)}")

        # Performance change should be reasonable (-100% to +infinite)
        assert perf_result.performance_change >= -1.0

        print("✅ Performance regression tests passed!")
        return True

    except Exception as e:
        print(f"❌ Performance regression test failed: {e}")
        return False

def run_simple_test_suite():
    """Run simplified test suite for RefactoringValidator"""
    print("🚀 RefactoringValidator Simple Test Suite")
    print("=" * 55)

    tests = [
        ("Basic Functionality", test_refactoring_validator_basic),
        ("Safety Validation", test_safety_validation),
        ("Automated Testing", test_automated_testing),
        ("Performance Regression", test_performance_regression)
    ]

    results = {"passed": 0, "failed": 0, "total": len(tests)}

    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 35)

        try:
            if test_func():
                results["passed"] += 1
                print(f"✅ {test_name} PASSED")
            else:
                results["failed"] += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            results["failed"] += 1
            print(f"❌ {test_name} FAILED: {e}")

    # Final results
    print("\n" + "=" * 55)
    print("📊 FINAL TEST RESULTS")
    print("=" * 55)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / results['total']) * 100:.1f}%")

    if results["failed"] == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {results['failed']} tests failed")

    return results

if __name__ == "__main__":
    results = run_simple_test_suite()
    exit_code = 0 if results["failed"] == 0 else 1
    exit(exit_code)
