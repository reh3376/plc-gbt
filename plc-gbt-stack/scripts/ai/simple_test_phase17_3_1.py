#!/usr/bin/env python3
"""
Simple test for Phase 17.3.1 to isolate issues
"""

import sys
from pathlib import Path

# Add the module path
sys.path.append(str(Path(__file__).parent))

def test_basic_import():
    """Test basic import functionality"""
    print("Testing basic import...")

    try:
        # Import the main module
        print("✅ Main module imported successfully")

        # Test class imports
        from phase17_3_1_libcst_astroid_static_analysis import (
            AdvancedStaticAnalyzer,
            AnalysisLevel,
        )
        print("✅ Core classes imported successfully")

        # Test analyzer initialization
        analyzer = AdvancedStaticAnalyzer(AnalysisLevel.SURFACE)
        print(f"✅ Analyzer initialized: {analyzer.capabilities}")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hallucination_detection():
    """Test hallucination detection"""
    print("\nTesting hallucination detection...")

    try:
        from phase17_3_1_libcst_astroid_static_analysis import HallucinationDetector

        detector = HallucinationDetector()

        test_code = '''
import fake_module
def test_function():
    api_key = "YOUR_API_KEY"
    return api_key
'''

        hallucinations = detector.detect_hallucinations(test_code, Path("test.py"))
        print(f"✅ Detected {len(hallucinations)} hallucinations")

        for h in hallucinations:
            print(f"  - {h.category.value}: {h.description}")

        return True

    except Exception as e:
        print(f"❌ Hallucination detection test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simple tests"""
    print("🔬 Simple Phase 17.3.1 Test Suite")
    print("=" * 50)

    tests = [
        test_basic_import,
        test_hallucination_detection,
    ]

    results = []
    for test in tests:
        result = test()
        results.append(result)

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All simple tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
