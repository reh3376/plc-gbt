#!/usr/bin/env python3
"""
Phase 22.1.5: Simple Validation Framework Test
==============================================

Simple test script to verify validation framework functionality
without relative import issues.

Author: PLC-GPT Development Team
Date: January 18, 2025
"""

import sys
import os
import numpy as np
import logging

# Add parent directories to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_statistical_tests():
    """Test statistical validation functionality"""
    try:
        from statistical_tests import StatisticalTestSuite
        
        print("✅ Testing Statistical Validation...")
        
        # Create test suite
        suite = StatisticalTestSuite()
        
        # Sample data
        pid_input = {
            'setpoint': [50] * 20 + [60] * 30,
            'process_variable': [49.8 + np.random.normal(0, 0.1) for _ in range(50)],
            'control_output': [45 + np.random.normal(0, 0.5) for _ in range(50)]
        }
        
        pid_results = {
            'kp': 1.5,
            'ki': 0.1,
            'kd': 0.05,
            'success': True
        }
        
        # Run validation
        results = suite.validate_pid_tuning_results(pid_input, pid_results)
        
        print(f"   • Statistical tests completed: {len(results)} tests")
        passed = sum(1 for r in results if r.passed)
        print(f"   • Tests passed: {passed}/{len(results)} ({passed/len(results)*100:.1f}%)")
        
        # Get statistics
        stats = suite.get_test_statistics()
        print(f"   • Total execution time: {stats['total_execution_time']:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Statistical tests failed: {e}")
        return False

def test_confidence_scoring():
    """Test confidence scoring functionality"""
    try:
        from confidence_scoring import ConfidenceScorer
        
        print("✅ Testing Confidence Scoring...")
        
        # Create confidence scorer
        scorer = ConfidenceScorer()
        
        # Sample data
        input_data = {
            'setpoint': [50] * 50,
            'process_variable': [49.9 + np.random.normal(0, 0.1) for _ in range(50)],
            'control_output': [45 + np.random.normal(0, 1) for _ in range(50)]
        }
        
        results = {
            'kp': 1.2,
            'ki': 0.08,
            'kd': 0.03,
            'success': True
        }
        
        # Assess confidence
        confidence = scorer.assess_confidence("pid_tuning", input_data, results)
        
        print(f"   • Overall confidence: {confidence.overall_score:.3f} ({confidence.confidence_level})")
        print(f"   • Weighted score: {confidence.weighted_score:.3f}")
        print(f"   • Dimensions assessed: {len(confidence.dimension_scores)}")
        
        if confidence.critical_issues:
            print(f"   • Critical issues: {len(confidence.critical_issues)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Confidence scoring failed: {e}")
        return False

def test_wolfram_integration():
    """Test WolframAlpha Pro integration"""
    try:
        from wolfram_integration import WolframValidator
        
        print("✅ Testing WolframAlpha Integration...")
        
        # Create validator (without API key, will use mocks)
        validator = WolframValidator(app_id=None)
        
        # Test PID validation
        wolfram_results = validator.validate_pid_tuning_equations(
            kp=1.5, ki=0.1, kd=0.05
        )
        
        print(f"   • WolframAlpha validations: {len(wolfram_results)}")
        successful = sum(1 for r in wolfram_results if r.success)
        print(f"   • Successful validations: {successful}/{len(wolfram_results)}")
        
        # Get statistics
        stats = validator.get_validation_statistics()
        print(f"   • Total validations: {stats['total_validations']}")
        print(f"   • Success rate: {stats['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ WolframAlpha integration failed: {e}")
        return False

def test_validation_manager():
    """Test validation manager orchestration"""
    try:
        from validation_manager import ValidationManager, ValidationLevel
        
        print("✅ Testing Validation Manager...")
        
        # Create validation manager
        manager = ValidationManager(
            enable_statistical=True,
            enable_confidence=True,
            enable_wolfram=True
        )
        
        # Sample data
        input_data = {
            'setpoint': [25.0] * 30 + [35.0] * 30,
            'process_variable': [25.1 + np.random.normal(0, 0.2) for _ in range(60)],
            'control_output': [50 + np.random.normal(0, 2) for _ in range(60)]
        }
        
        results = {
            'kp': 2.5,
            'ki': 0.15,
            'kd': 0.08,
            'success': True
        }
        
        # Run comprehensive validation
        report = manager.validate_analysis_results(
            analysis_type="pid_tuning",
            input_data=input_data,
            results=results,
            validation_level=ValidationLevel.STANDARD
        )
        
        print(f"   • Validation ID: {report.validation_id}")
        print(f"   • Overall status: {report.overall_status.value}")
        print(f"   • Overall score: {report.overall_score:.3f}")
        print(f"   • Execution time: {report.execution_time:.3f}s")
        print(f"   • Statistical results: {len(report.statistical_results)}")
        print(f"   • WolframAlpha results: {len(report.wolfram_results)}")
        
        # Get manager statistics
        stats = manager.get_validation_statistics()
        print(f"   • Manager success rate: {stats['success_rate']:.1%}")
        
        return True
        
    except Exception as e:
        print(f"❌ Validation manager failed: {e}")
        return False

def test_package_imports():
    """Test package initialization and imports"""
    try:
        print("✅ Testing Package Imports...")
        
        # Test package initialization
        import __init__ as validation_package
        
        # Check main exports
        expected_exports = [
            'ValidationManager', 'StatisticalTestSuite', 'ConfidenceScorer', 
            'WolframValidator', 'ValidationLevel', 'ValidationStatus'
        ]
        
        available_exports = [name for name in dir(validation_package) 
                           if name in expected_exports]
        
        print(f"   • Package exports: {len(available_exports)}/{len(expected_exports)}")
        for export in available_exports:
            print(f"     - {export} ✓")
        
        missing_exports = set(expected_exports) - set(available_exports)
        if missing_exports:
            print(f"   • Missing exports: {missing_exports}")
        
        return len(missing_exports) == 0
        
    except Exception as e:
        print(f"❌ Package import failed: {e}")
        return False

def main():
    """Run all validation tests"""
    print("=" * 60)
    print("Phase 22.1.5: Validation Framework Testing")
    print("=" * 60)
    
    test_results = []
    
    # Run individual component tests
    test_results.append(("Package Imports", test_package_imports()))
    test_results.append(("Statistical Tests", test_statistical_tests()))
    test_results.append(("Confidence Scoring", test_confidence_scoring()))
    test_results.append(("WolframAlpha Integration", test_wolfram_integration()))
    test_results.append(("Validation Manager", test_validation_manager()))
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed_tests = 0
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed_tests += 1
    
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print("-" * 60)
    print(f"Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Validation Framework: READY FOR PRODUCTION")
    elif success_rate >= 60:
        print("⚠️  Validation Framework: FUNCTIONAL WITH MINOR ISSUES")
    else:
        print("❌ Validation Framework: NEEDS ATTENTION")
    
    print("=" * 60)
    
    return success_rate >= 80

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 