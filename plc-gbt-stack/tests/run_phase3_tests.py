#!/usr/bin/env python3
"""
Phase 3 Day 3 Test Runner
Created: January 1, 2025
Purpose: Simple test runner for Phase 3 Day 3 implementation validation
"""

import argparse
import asyncio
import os
import sys
from typing import Any, Dict

# Add tests directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))

def setup_environment():
    """Set up environment variables for testing"""
    # Default test configuration
    default_config = {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "QDRANT_HOST": "localhost",
        "QDRANT_PORT": "6333",
        "OPENAI_API_KEY": ""  # Will need to be set by user
    }

    # Set defaults if not already set
    for key, value in default_config.items():
        if key not in os.environ and value:
            os.environ[key] = value

    print("🔧 Environment Configuration:")
    print(f"   Neo4j URI: {os.environ.get('NEO4J_URI', 'NOT SET')}")
    print(f"   Neo4j User: {os.environ.get('NEO4J_USER', 'NOT SET')}")
    print(f"   Qdrant Host: {os.environ.get('QDRANT_HOST', 'NOT SET')}")
    print(f"   Qdrant Port: {os.environ.get('QDRANT_PORT', 'NOT SET')}")
    print(f"   OpenAI API Key: {'SET' if os.environ.get('OPENAI_API_KEY') else 'NOT SET'}")
    print()

async def run_comprehensive_tests():
    """Run the comprehensive test suite"""
    try:
        from comprehensive_test_suite import ComprehensiveTestSuite

        print("🚀 Starting Phase 3 Day 3 comprehensive tests...")

        test_suite = ComprehensiveTestSuite()
        results = await test_suite.run_all_tests()

        return results

    except ImportError as e:
        print(f"❌ Failed to import test suite: {e}")
        return None
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        return None

def print_results(results: Dict[str, Any]):
    """Print formatted test results"""
    if not results:
        print("❌ No test results available")
        return False

    summary = results.get("summary", {})
    categories = results.get("categories", {})

    print("\n" + "="*60)
    print("📊 PHASE 3 DAY 3 TEST RESULTS")
    print("="*60)

    # Overall summary
    print("📈 Overall Results:")
    print(f"   Total Tests: {summary.get('total_tests', 0)}")
    print(f"   Passed: ✅ {summary.get('passed', 0)}")
    print(f"   Failed: ❌ {summary.get('failed', 0)}")
    print(f"   Success Rate: {summary.get('success_rate', 0)}%")
    print(f"   Duration: {summary.get('total_duration_seconds', 0):.2f}s")

    # Category breakdown
    print("\n🔍 Component Test Results:")
    for category, stats in categories.items():
        status = "✅" if stats['failed'] == 0 else "❌"
        print(f"   {status} {category}: {stats['passed']}/{stats['total']} passed")

    # Failed tests details
    failed_tests = [r for r in results.get('detailed_results', []) if not r.get('success', True)]
    if failed_tests:
        print(f"\n🚨 Failed Tests ({len(failed_tests)}):")
        for test in failed_tests[:10]:  # Show first 10 failures
            print(f"   • {test.get('test_name', 'Unknown')}")
            print(f"     Error: {test.get('error_message', 'No error message')}")

        if len(failed_tests) > 10:
            print(f"   ... and {len(failed_tests) - 10} more failures")

    # Success determination
    all_passed = summary.get('failed', 1) == 0

    print("\n" + "="*60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Phase 3 Day 3 implementation is ready for production!")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Please review and fix the failing components before proceeding.")
    print("="*60)

    return all_passed

def check_dependencies():
    """Check if required dependencies are available"""
    print("🔍 Checking dependencies...")

    required_modules = [
        "neo4j",
        "psutil",
        "structlog"
    ]

    optional_modules = [
        ("qdrant_client", "Qdrant integration"),
        ("openai", "OpenAI API integration")
    ]

    missing_required = []
    missing_optional = []

    # Check required modules
    for module in required_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            missing_required.append(module)
            print(f"   ❌ {module} (REQUIRED)")

    # Check optional modules
    for module, description in optional_modules:
        try:
            __import__(module)
            print(f"   ✅ {module} ({description})")
        except ImportError:
            missing_optional.append((module, description))
            print(f"   ⚠️  {module} ({description}) - OPTIONAL")

    if missing_required:
        print(f"\n❌ Missing required dependencies: {', '.join(missing_required)}")
        print("Please install them with: pip install " + " ".join(missing_required))
        return False

    if missing_optional:
        print("\n⚠️  Missing optional dependencies may cause some tests to be skipped")

    print("✅ Dependency check completed")
    return True

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Phase 3 Day 3 Test Runner")
    parser.add_argument("--skip-deps", action="store_true", help="Skip dependency check")
    parser.add_argument("--quick", action="store_true", help="Run quick tests only")
    args = parser.parse_args()

    print("🧪 PLC-GPT Phase 3 Day 3 Test Runner")
    print("="*50)

    # Check dependencies
    if not args.skip_deps:
        if not check_dependencies():
            print("\n❌ Dependency check failed. Use --skip-deps to bypass.")
            return 1
        print()

    # Setup environment
    setup_environment()

    # Run tests
    results = await run_comprehensive_tests()

    if results is None:
        print("❌ Failed to run tests")
        return 1

    # Print results
    success = print_results(results)

    # Save results file
    filename = f"phase3_day3_test_results_{results.get('timestamp', '').replace(':', '-').replace('T', '_')[:19]}.json"
    try:
        import json
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Detailed results saved to: {filename}")
    except Exception as e:
        print(f"⚠️  Failed to save results file: {e}")

    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Test run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)
