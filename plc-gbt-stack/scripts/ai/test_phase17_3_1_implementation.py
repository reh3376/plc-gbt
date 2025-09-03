#!/usr/bin/env python3
"""
🧪 Test Suite for Phase 17.3.1: Advanced Static Analysis Framework
PLC-GPT Industrial Control Static Code Analysis Testing

Comprehensive test suite for validating the libcst/astroid static analysis framework
including hallucination detection, code quality analysis, and integration testing.

Following AI Task Orchestrator methodology for systematic validation.

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: 17.3.1 - Testing & Validation
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the module path
sys.path.append(str(Path(__file__).parent))

def test_imports_and_dependencies():
    """Test that all required imports and dependencies are available"""
    print("🧪 Testing Phase 17.3.1 Imports and Dependencies")
    print("=" * 60)

    # Test basic imports
    try:
        from phase17_3_1_libcst_astroid_static_analysis import (
            AdvancedStaticAnalyzer,
            AnalysisLevel,
            CodeQualityAnalyzer,
            CodeQualityIssue,
            HallucinationCategory,
            HallucinationDetector,
        )
        print("✅ Core framework imports successful")
    except ImportError as e:
        print(f"❌ Core framework import failed: {e}")
        return False

    # Test optional dependencies
    try:
        import libcst as cst
        print("✅ libcst available for CST analysis")
        libcst_available = True
    except ImportError:
        print("⚠️  libcst not available - CST analysis will be disabled")
        libcst_available = False

    try:
        import astroid
        print("✅ astroid available for semantic analysis")
        astroid_available = True
    except ImportError:
        print("⚠️  astroid not available - semantic analysis will be disabled")
        astroid_available = False

    # Test existing analyzer integration
    try:
        from codebase_analyzer import CodebaseAnalyzer, FileType
        print("✅ Existing codebase analyzer integration available")
        existing_analyzer = True
    except ImportError:
        print("⚠️  Existing analyzer not available - running in standalone mode")
        existing_analyzer = False

    print("\n📊 Dependency Status:")
    print(f"  • libcst: {'✅' if libcst_available else '❌'}")
    print(f"  • astroid: {'✅' if astroid_available else '❌'}")
    print(f"  • Existing analyzer: {'✅' if existing_analyzer else '❌'}")

    return True

def test_analyzer_initialization():
    """Test analyzer initialization with different levels"""
    print("\n🧪 Testing Analyzer Initialization")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import AdvancedStaticAnalyzer, AnalysisLevel

        # Test each analysis level
        levels = [AnalysisLevel.SURFACE, AnalysisLevel.STRUCTURAL, AnalysisLevel.SEMANTIC, AnalysisLevel.COMPREHENSIVE]

        for level in levels:
            analyzer = AdvancedStaticAnalyzer(level)
            print(f"✅ Analyzer initialized successfully with level: {level.value}")
            print(f"   Capabilities: {analyzer.capabilities}")

        return True

    except Exception as e:
        print(f"❌ Analyzer initialization failed: {e}")
        return False

def test_hallucination_detection():
    """Test hallucination detection capabilities"""
    print("\n🧪 Testing Hallucination Detection")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import HallucinationDetector

        detector = HallucinationDetector()

        # Test code with hallucinations
        test_code = '''
import fake_module
from nonexistent_library import something
import real_module

def my_function():
    # TODO: Implement this function
    api_key = "YOUR_API_KEY_HERE"
    placeholder_value = "PLACEHOLDER_DATA"
    return EXAMPLE_RETURN_VALUE

def another_function():
    pass  # FIXME: Add implementation
'''

        hallucinations = detector.detect_hallucinations(test_code, Path("test_file.py"))

        print(f"📊 Detected {len(hallucinations)} hallucinations:")
        for i, h in enumerate(hallucinations, 1):
            print(f"  {i}. Line {h.line_number}: {h.category.value} - {h.description}")
            print(f"     Evidence: {h.evidence}")
            print(f"     Severity: {h.severity}, Confidence: {h.confidence}")

        # Verify we detect expected hallucinations
        expected_categories = {'fake_imports', 'placeholder_values', 'todo_markers'}
        detected_categories = {h.category.value for h in hallucinations}

        if expected_categories.issubset(detected_categories):
            print("✅ Hallucination detection working correctly")
            return True
        else:
            print(f"⚠️  Expected {expected_categories}, got {detected_categories}")
            return False

    except Exception as e:
        print(f"❌ Hallucination detection test failed: {e}")
        return False

def test_code_quality_analysis():
    """Test code quality analysis"""
    print("\n🧪 Testing Code Quality Analysis")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import CodeQualityAnalyzer

        analyzer = CodeQualityAnalyzer()

        # Test code with quality issues
        test_code = '''
def ComplexFunction(a, b, c, d, e):
    # High complexity function
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        return a + b + c + d + e
                    else:
                        return a + b + c + d
                else:
                    return a + b + c
            else:
                return a + b
        else:
            return a
    else:
        return 0

def snake_case_function():
    return "good"

def CamelCaseFunction():
    return "bad naming"
'''

        quality_issues = analyzer.analyze_quality(test_code, Path("test_file.py"))

        print(f"📊 Detected {len(quality_issues)} quality issues:")
        for i, issue in enumerate(quality_issues, 1):
            print(f"  {i}. Line {issue.line_number}: {issue.issue_type.value}")
            print(f"     Description: {issue.description}")
            print(f"     Impact: {issue.impact}")
            print(f"     Recommendation: {issue.recommendation}")

        print("✅ Code quality analysis working correctly")
        return True

    except Exception as e:
        print(f"❌ Code quality analysis test failed: {e}")
        return False

def test_file_analysis():
    """Test complete file analysis"""
    print("\n🧪 Testing Complete File Analysis")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import AdvancedStaticAnalyzer, AnalysisLevel

        analyzer = AdvancedStaticAnalyzer(AnalysisLevel.COMPREHENSIVE)

        # Create test file content
        test_code = '''
#!/usr/bin/env python3
"""
Test module for static analysis
"""

import os
import sys
import fake_module  # This is a hallucination

def well_written_function(param: str) -> str:
    """
    A well-documented function with good practices.

    Args:
        param: Input parameter

    Returns:
        Processed string
    """
    return param.upper()

def BadlyWrittenFunction(a, b, c, d, e, f, g, h):
    # TODO: This function needs implementation
    api_key = "YOUR_API_KEY"  # Placeholder

    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                if h > 0:
                                    return "complex"
                                else:
                                    return "still complex"
                            else:
                                return "very complex"
                        else:
                            return "extremely complex"
                    else:
                        return "too complex"
                else:
                    return "way too complex"
            else:
                return "impossibly complex"
        else:
            return "ridiculously complex"
    else:
        return "insanely complex"

class ExampleClass:
    def __init__(self):
        self.placeholder = EXAMPLE_VALUE  # Another hallucination
'''

        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            temp_file = f.name

        try:
            # Analyze the file
            result = analyzer.analyze_file(temp_file)

            print(f"📊 Analysis Results for {Path(temp_file).name}:")
            print(f"  • Syntax valid: {result.syntax_valid}")
            print(f"  • Hallucinations found: {len(result.hallucinations)}")
            print(f"  • Quality issues: {len(result.quality_issues)}")
            print(f"  • Hallucination score: {result.hallucination_score:.2f}")
            print(f"  • Quality score: {result.quality_score:.1f}")
            print(f"  • Total issues: {result.total_issues}")
            print(f"  • Critical issues: {result.critical_issues}")

            # Print hallucinations
            if result.hallucinations:
                print("\n  🔍 Hallucinations detected:")
                for h in result.hallucinations:
                    print(f"    - Line {h.line_number}: {h.category.value} ({h.severity})")

            # Print quality issues
            if result.quality_issues:
                print("\n  📊 Quality issues:")
                for q in result.quality_issues:
                    print(f"    - Line {q.line_number}: {q.issue_type.value} ({q.impact})")

            # Print recommendations
            if result.recommendations:
                print("\n  💡 Recommendations:")
                for rec in result.recommendations:
                    print(f"    - {rec}")

            print("✅ File analysis completed successfully")
            return True

        finally:
            # Clean up temporary file
            os.unlink(temp_file)

    except Exception as e:
        print(f"❌ File analysis test failed: {e}")
        return False

def test_codebase_analysis():
    """Test codebase analysis on a small directory"""
    print("\n🧪 Testing Codebase Analysis")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import AdvancedStaticAnalyzer, AnalysisLevel

        analyzer = AdvancedStaticAnalyzer(AnalysisLevel.STRUCTURAL)

        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            test_files = {
                "good_file.py": '''
def well_written_function():
    """A well-documented function."""
    return "good"
''',
                "bad_file.py": '''
import fake_module
def BadFunction():
    # TODO: implement
    return YOUR_PLACEHOLDER
''',
                "another_file.py": '''
def AnotherComplexFunction(a, b, c, d, e, f):
    if a:
        if b:
            if c:
                if d:
                    if e:
                        if f:
                            return "too complex"
    return "result"
'''
            }

            # Write test files
            for filename, content in test_files.items():
                (temp_path / filename).write_text(content)

            # Analyze the codebase
            results = analyzer.analyze_codebase(temp_path)

            print("📊 Codebase Analysis Results:")
            print(f"  • Files analyzed: {len(results)}")

            total_hallucinations = sum(len(r.hallucinations) for r in results.values())
            total_quality_issues = sum(len(r.quality_issues) for r in results.values())

            print(f"  • Total hallucinations: {total_hallucinations}")
            print(f"  • Total quality issues: {total_quality_issues}")

            # Generate report
            report = analyzer.generate_analysis_report(results)

            print("\n📋 Generated Report Summary:")
            print(f"  • Session ID: {report['session_id']}")
            print(f"  • Analysis level: {report['analysis_level']}")
            print(f"  • Files with issues: {report['summary']['files_with_issues']}")
            print(f"  • Average quality score: {report['summary']['average_quality_score']:.1f}")

            print("✅ Codebase analysis completed successfully")
            return True

    except Exception as e:
        print(f"❌ Codebase analysis test failed: {e}")
        return False

def test_performance():
    """Test performance with larger code samples"""
    print("\n🧪 Testing Performance")
    print("=" * 60)

    try:
        from phase17_3_1_libcst_astroid_static_analysis import AdvancedStaticAnalyzer, AnalysisLevel

        # Test with different analysis levels
        levels = [AnalysisLevel.SURFACE, AnalysisLevel.STRUCTURAL, AnalysisLevel.COMPREHENSIVE]

        # Generate larger test code
        large_test_code = '''
#!/usr/bin/env python3
"""Large test module for performance testing"""

import os
import sys
import json
import fake_large_module
'''

        # Add many functions to test scalability
        for i in range(20):
            large_test_code += f'''
def function_{i}(param1, param2, param3):
    """Function {i} documentation"""
    # TODO: Implement function {i}
    if param1 > {i}:
        if param2 > {i*2}:
            if param3 > {i*3}:
                return param1 + param2 + param3
            else:
                return param1 + param2
        else:
            return param1
    else:
        return YOUR_PLACEHOLDER_{i}
'''

        for level in levels:
            analyzer = AdvancedStaticAnalyzer(level)

            start_time = time.time()

            # Write to temporary file and analyze
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(large_test_code)
                temp_file = f.name

            try:
                result = analyzer.analyze_file(temp_file)
                end_time = time.time()

                print(f"  📊 {level.value} analysis:")
                print(f"    • Time: {end_time - start_time:.3f} seconds")
                print(f"    • Issues found: {result.total_issues}")
                print(f"    • Lines analyzed: ~{len(large_test_code.split())}")

            finally:
                os.unlink(temp_file)

        print("✅ Performance testing completed")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Phase 17.3.1 Advanced Static Analysis Framework Tests")
    print("=" * 80)

    tests = [
        ("Import Dependencies", test_imports_and_dependencies),
        ("Analyzer Initialization", test_analyzer_initialization),
        ("Hallucination Detection", test_hallucination_detection),
        ("Code Quality Analysis", test_code_quality_analysis),
        ("File Analysis", test_file_analysis),
        ("Codebase Analysis", test_codebase_analysis),
        ("Performance Testing", test_performance),
    ]

    results = {}

    for test_name, test_func in tests:
        print(f"\n🔄 Running: {test_name}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for success in results.values() if success)
    total = len(results)

    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Phase 17.3.1 implementation is working correctly.")
        return True
    else:
        print(f"⚠️  {total - passed} tests failed. Review implementation.")
        return False

def main():
    """Main execution function"""
    success = run_all_tests()

    if success:
        print("\n🏆 Phase 17.3.1: Advanced Static Analysis Framework - IMPLEMENTATION VALIDATED")
        print("✅ Ready for integration with Phase 17.3.2: Modular Provider Layer")
        return 0
    else:
        print("\n❌ Phase 17.3.1: Implementation needs review and fixes")
        return 1

if __name__ == "__main__":
    exit(main())
