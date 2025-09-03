#!/usr/bin/env python3
"""
PLC-GBT CLI Test Runner
======================

Convenient script to run various types of tests for the PLC-GBT CLI system.
Provides easy access to integration tests, performance benchmarks, and CI/CD integration.

Usage:
    python run_tests.py --help
    python run_tests.py --integration
    python run_tests.py --performance
    python run_tests.py --all
    python run_tests.py --ci-setup
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.testing.test_framework import CICDIntegration, CLITestFramework


class TestRunner:
    """Main test runner orchestrator."""

    def __init__(self, config_path: Optional[Path] = None, verbose: bool = False):
        self.config_path = config_path
        self.verbose = verbose
        self.start_time = datetime.now()

    def setup_environment(self):
        """Setup test environment and validate prerequisites."""
        print("🔧 Setting up test environment...")

        # Check Python version

        # Check required packages
        required_packages = ['psutil', 'pytest', 'pyyaml']
        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing required packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            sys.exit(1)

        # Validate CLI command availability
        try:
            import subprocess
            result = subprocess.run(['plc-memory', '--version'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                print("⚠️  Warning: plc-memory CLI not available or not working")
                print("   Some integration tests may fail")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("⚠️  Warning: plc-memory CLI not found in PATH")
            print("   Integration tests will be skipped")

        print("✅ Environment setup complete")

    async def run_integration_tests(self, quick: bool = False) -> Dict:
        """Run integration test suite."""
        print("🧪 Running integration tests...")

        framework = CLITestFramework(config_path=self.config_path)

        if quick:
            # Override config for quick tests
            framework.config['benchmark_iterations'] = 1
            framework.config['integration_tests']['test_instances'] = 1

        try:
            test_suites = await framework.run_integration_tests()

            # Summary
            total_tests = sum(len(suite.tests) for suite in test_suites)
            passed_tests = sum(
                1 for suite in test_suites
                for test in suite.tests
                if test.status == "passed"
            )
            failed_tests = total_tests - passed_tests

            print("📊 Integration Tests Complete:")
            print(f"   Total: {total_tests}")
            print(f"   Passed: {passed_tests}")
            print(f"   Failed: {failed_tests}")

            if failed_tests > 0:
                print("❌ Some integration tests failed")
                for suite in test_suites:
                    for test in suite.tests:
                        if test.status == "failed":
                            print(f"   - {suite.name}.{test.test_name}: {test.error_message}")
            else:
                print("✅ All integration tests passed")

            return {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'suites': len(test_suites)
            }

        except Exception as e:
            print(f"❌ Integration tests failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return {'total': 0, 'passed': 0, 'failed': 1, 'suites': 0}

    async def run_performance_tests(self) -> Dict:
        """Run performance benchmark tests."""
        print("⚡ Running performance tests...")

        framework = CLITestFramework(config_path=self.config_path)

        try:
            benchmarks = await framework.run_performance_tests()

            print("📈 Performance Tests Complete:")
            print(f"   Benchmarks: {len(benchmarks)}")

            # Show performance summary
            operations = {}
            for benchmark in benchmarks:
                if benchmark.operation not in operations:
                    operations[benchmark.operation] = []
                operations[benchmark.operation].append(benchmark.duration)

            for operation, durations in operations.items():
                avg_duration = sum(durations) / len(durations)
                min_duration = min(durations)
                max_duration = max(durations)
                print(f"   {operation}: {avg_duration:.3f}s avg ({min_duration:.3f}-{max_duration:.3f}s)")

            return {
                'benchmarks': len(benchmarks),
                'operations': len(operations),
                'avg_duration': sum(b.duration for b in benchmarks) / len(benchmarks) if benchmarks else 0
            }

        except Exception as e:
            print(f"❌ Performance tests failed: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return {'benchmarks': 0, 'operations': 0, 'avg_duration': 0}

    async def run_all_tests(self, quick: bool = False) -> Dict:
        """Run complete test suite."""
        print("🚀 Running complete test suite...")

        framework = CLITestFramework(config_path=self.config_path)

        # Run integration tests
        await framework.run_integration_tests()

        # Run performance tests
        await framework.run_performance_tests()

        # Generate comprehensive report
        report = framework.generate_report()
        report_file = framework.save_report(report)

        print("📋 Complete Test Suite Results:")
        print(f"   Session ID: {framework.session_id}")
        print(f"   Total Tests: {report['summary']['total_tests']}")
        print(f"   Passed: {report['summary']['passed']}")
        print(f"   Failed: {report['summary']['failed']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"   Duration: {report['duration']:.1f}s")
        print(f"   Report: {report_file}")

        return report['summary']

    def setup_ci_cd(self, platforms: List[str]):
        """Setup CI/CD integration files."""
        print("🔧 Setting up CI/CD integration...")

        ci_integration = CICDIntegration()

        if 'github' in platforms:
            github_dir = Path(".github/workflows")
            github_dir.mkdir(parents=True, exist_ok=True)

            workflow_file = github_dir / "plc_gbt_cli_testing.yml"
            with open(workflow_file, "w") as f:
                f.write(ci_integration.generate_github_workflow())
            print(f"✅ GitHub Actions workflow: {workflow_file}")

        if 'jenkins' in platforms:
            jenkinsfile = Path("Jenkinsfile")
            with open(jenkinsfile, "w") as f:
                f.write(ci_integration.generate_jenkins_pipeline())
            print(f"✅ Jenkins pipeline: {jenkinsfile}")

        # Create test configuration for CI
        ci_config = {
            "cli_command": "plc-memory",
            "timeout": 30,
            "benchmark_iterations": 3,
            "integration_tests": {
                "enable_plc_tests": False,
                "test_instances": 2
            },
            "performance_tests": {
                "enable_benchmarks": True,
                "thresholds": {
                    "max_schema_create_time": 10.0,
                    "max_instance_create_time": 20.0
                }
            }
        }

        ci_config_file = Path("ci_test_config.yaml")
        with open(ci_config_file, "w") as f:
            import yaml
            yaml.dump(ci_config, f, default_flow_style=False)
        print(f"✅ CI test configuration: {ci_config_file}")

    def generate_test_report(self, results_dir: Optional[Path] = None):
        """Generate test report from existing results."""
        results_dir = results_dir or Path("./test_results")

        if not results_dir.exists():
            print(f"❌ Results directory not found: {results_dir}")
            return

        # Find latest test report
        report_files = list(results_dir.glob("test_report_*.json"))
        if not report_files:
            print("❌ No test reports found")
            return

        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)

        with open(latest_report) as f:
            report = json.load(f)

        print("📋 Latest Test Report Summary:")
        print(f"   Session: {report['session_id']}")
        print(f"   Timestamp: {report['timestamp']}")
        print(f"   Duration: {report['duration']:.1f}s")
        print(f"   Tests: {report['summary']['total_tests']}")
        print(f"   Success Rate: {report['summary']['success_rate']:.1f}%")

        if report['summary']['failed'] > 0:
            print("❌ Failed Tests:")
            for suite in report['test_suites']:
                for test in suite['tests']:
                    if test['status'] == 'failed':
                        print(f"   - {suite['name']}.{test['name']}: {test['error']}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="PLC-GBT CLI Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --integration          # Run integration tests
  %(prog)s --performance          # Run performance benchmarks
  %(prog)s --all                  # Run complete test suite
  %(prog)s --quick --integration  # Quick integration tests
  %(prog)s --ci-setup github      # Setup GitHub Actions
  %(prog)s --report               # Show latest test report
        """
    )

    parser.add_argument(
        "--integration",
        action="store_true",
        help="Run integration tests"
    )

    parser.add_argument(
        "--performance",
        action="store_true",
        help="Run performance benchmarks"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Run complete test suite"
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run tests in quick mode (fewer iterations)"
    )

    parser.add_argument(
        "--ci-setup",
        choices=["github", "jenkins", "all"],
        help="Setup CI/CD integration files"
    )

    parser.add_argument(
        "--report",
        action="store_true",
        help="Generate report from latest test results"
    )

    parser.add_argument(
        "--config",
        type=Path,
        help="Path to test configuration file"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--no-setup",
        action="store_true",
        help="Skip environment setup validation"
    )

    args = parser.parse_args()

    # At least one action required
    if not any([args.integration, args.performance, args.all, args.ci_setup, args.report]):
        parser.print_help()
        sys.exit(1)

    runner = TestRunner(config_path=args.config, verbose=args.verbose)

    if not args.no_setup:
        runner.setup_environment()

    async def run_async_tests():
        """Run async test operations."""
        total_results = {}

        try:
            if args.integration:
                results = await runner.run_integration_tests(quick=args.quick)
                total_results.update(results)

            if args.performance:
                results = await runner.run_performance_tests()
                total_results.update(results)

            if args.all:
                results = await runner.run_all_tests(quick=args.quick)
                total_results.update(results)

            return total_results

        except KeyboardInterrupt:
            print("\n⚠️  Tests interrupted by user")
            return {}
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return {}

    # Handle CI setup
    if args.ci_setup:
        platforms = ['github', 'jenkins'] if args.ci_setup == 'all' else [args.ci_setup]
        runner.setup_ci_cd(platforms)

    # Handle report generation
    if args.report:
        runner.generate_test_report()

    # Run async tests if requested
    if any([args.integration, args.performance, args.all]):
        try:
            results = asyncio.run(run_async_tests())

            # Print final summary
            duration = (datetime.now() - runner.start_time).total_seconds()
            print(f"\n🏁 Test execution completed in {duration:.1f}s")

            # Exit with appropriate code
            if 'failed' in results and results['failed'] > 0:
                print("❌ Some tests failed")
                sys.exit(1)
            else:
                print("✅ All tests passed")
                sys.exit(0)

        except Exception as e:
            print(f"❌ Fatal error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
