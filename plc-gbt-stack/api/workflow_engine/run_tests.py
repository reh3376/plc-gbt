#!/usr/bin/env python3
"""
N8N Framework Integration - Test Runner
Phase 1.5: Automated Testing Suite Implementation

Comprehensive test runner with >95% coverage requirement and performance reporting.
Following AI Task Orchestrator methodology with strict compliance.

Usage:
    python run_tests.py                    # Run all tests
    python run_tests.py --unit            # Run only unit tests  
    python run_tests.py --integration     # Run only integration tests
    python run_tests.py --performance     # Run only performance tests
    python run_tests.py --industrial      # Run only industrial tests
    python run_tests.py --coverage        # Run with detailed coverage report

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.5 - Automated Testing Suite Implementation
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

# Add project root to Python path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestRunner:
    """
    Comprehensive test runner for N8N Framework Integration.
    
    Provides automated testing with coverage reporting, performance benchmarking,
    and industrial compliance validation.
    """
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.test_dir = Path(__file__).parent / "tests"
        self.coverage_dir = self.test_dir / "coverage_html"
        self.results = {
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "total_tests": 0,
            "passed_tests": 0, 
            "failed_tests": 0,
            "coverage_percent": 0.0,
            "performance_metrics": {},
            "industrial_compliance": {}
        }
    
    def setup_environment(self):
        """Setup testing environment and dependencies."""
        print("🔧 Setting up testing environment...")
        
        # Ensure test directory exists
        self.test_dir.mkdir(exist_ok=True)
        self.coverage_dir.mkdir(exist_ok=True)
        
        # Check required Python packages
        required_packages = [
            "pytest", "pytest-asyncio", "pytest-cov", "pytest-xdist",
            "httpx", "asyncpg", "redis", "pydantic", "fastapi"
        ]
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                print(f"⚠️ Missing package: {package}")
                print(f"Install with: pip install {package}")
        
        print("✅ Environment setup complete")
    
    def run_pytest_command(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run pytest with specified arguments."""
        
        base_args = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "--verbose",
            "--tb=short",
            "--disable-warnings",
            "--strict-markers"
        ]
        
        # Add coverage arguments
        coverage_args = [
            "--cov=api.workflow_engine",
            f"--cov-report=html:{self.coverage_dir}",
            "--cov-report=term-missing",
            f"--cov-report=xml:{self.test_dir}/coverage.xml",
            "--cov-fail-under=95"
        ]
        
        full_args = base_args + coverage_args + args
        
        print(f"🧪 Running: {' '.join(full_args[2:])}")  # Skip python -m
        
        return subprocess.run(
            full_args,
            capture_output=True,
            text=True,
            cwd=str(self.project_root)
        )
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Run unit tests with coverage reporting."""
        print("📋 Running Unit Tests...")
        
        result = self.run_pytest_command([
            "-m", "unit",
            "test_workflow_engine_unit.py"
        ])
        
        return self.parse_pytest_output(result, "unit")
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests."""
        print("🔗 Running Integration Tests...")
        
        result = self.run_pytest_command([
            "-m", "integration", 
            "test_api_integration.py"
        ])
        
        return self.parse_pytest_output(result, "integration")
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance and industrial compliance tests."""
        print("⚡ Running Performance & Industrial Tests...")
        
        result = self.run_pytest_command([
            "-m", "performance or industrial",
            "test_performance_industrial.py",
            "--timeout=600"  # 10 minute timeout for performance tests
        ])
        
        return self.parse_pytest_output(result, "performance")
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites."""
        print("🚀 Running Complete Test Suite...")
        
        result = self.run_pytest_command([
            "--maxfail=10",  # Stop after 10 failures
            "-n", "auto"  # Parallel execution
        ])
        
        return self.parse_pytest_output(result, "all")
    
    def parse_pytest_output(self, result: subprocess.CompletedProcess, test_type: str) -> Dict[str, Any]:
        """Parse pytest output and extract metrics."""
        
        output = result.stdout + result.stderr
        
        # Extract test counts
        passed = output.count(" PASSED")
        failed = output.count(" FAILED") + output.count(" ERROR")
        skipped = output.count(" SKIPPED")
        total = passed + failed + skipped
        
        # Extract coverage percentage
        coverage_percent = 0.0
        for line in output.split('\n'):
            if 'TOTAL' in line and '%' in line:
                try:
                    coverage_percent = float(line.split()[-1].replace('%', ''))
                    break
                except (ValueError, IndexError):
                    pass
        
        # Extract performance metrics if available
        performance_metrics = {}
        if "performance" in test_type.lower() or test_type == "all":
            # Look for performance data in output
            for line in output.split('\n'):
                if "Average:" in line and "ms" in line:
                    try:
                        avg_time = float(line.split("Average:")[1].split("ms")[0].strip())
                        performance_metrics["avg_execution_time_ms"] = avg_time
                    except (ValueError, IndexError):
                        pass
                elif "Throughput:" in line and "executions/second" in line:
                    try:
                        throughput = float(line.split("Throughput:")[1].split("executions/second")[0].strip())
                        performance_metrics["throughput_per_second"] = throughput
                    except (ValueError, IndexError):
                        pass
        
        test_results = {
            "test_type": test_type,
            "return_code": result.returncode,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "coverage_percent": coverage_percent,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "performance_metrics": performance_metrics,
            "output": output
        }
        
        # Print summary
        status_emoji = "✅" if result.returncode == 0 else "❌"
        print(f"{status_emoji} {test_type.title()} Tests Complete:")
        print(f"  Tests: {passed} passed, {failed} failed, {skipped} skipped")
        print(f"  Coverage: {coverage_percent:.1f}%")
        print(f"  Success Rate: {test_results['success_rate']:.1f}%")
        
        if performance_metrics:
            print(f"  Performance:")
            for metric, value in performance_metrics.items():
                print(f"    {metric}: {value}")
        
        return test_results
    
    def generate_comprehensive_report(self, all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        
        total_tests = sum(r["total_tests"] for r in all_results)
        total_passed = sum(r["passed_tests"] for r in all_results) 
        total_failed = sum(r["failed_tests"] for r in all_results)
        
        # Calculate overall metrics
        overall_success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        overall_coverage = max((r["coverage_percent"] for r in all_results), default=0)
        
        # Aggregate performance metrics
        performance_summary = {}
        for result in all_results:
            performance_summary.update(result["performance_metrics"])
        
        # Industrial compliance check
        industrial_compliance = {
            "coverage_requirement_met": overall_coverage >= 95.0,  # >95% required
            "success_rate_requirement_met": overall_success_rate >= 95.0,  # >95% required
            "performance_requirements": {
                "execution_latency_ok": performance_summary.get("avg_execution_time_ms", 0) < 100.0,
                "throughput_ok": performance_summary.get("throughput_per_second", 0) > 5.0
            }
        }
        
        comprehensive_report = {
            "test_execution": {
                "start_time": self.results["start_time"],
                "end_time": self.results["end_time"], 
                "duration_seconds": self.results["duration_seconds"]
            },
            "test_results": {
                "total_tests": total_tests,
                "passed_tests": total_passed,
                "failed_tests": total_failed,
                "success_rate_percent": overall_success_rate
            },
            "coverage": {
                "coverage_percent": overall_coverage,
                "requirement_met": overall_coverage >= 95.0
            },
            "performance_metrics": performance_summary,
            "industrial_compliance": industrial_compliance,
            "detailed_results": all_results,
            "phase_completion": {
                "phase_1_5_ready": (
                    overall_coverage >= 95.0 and 
                    overall_success_rate >= 95.0 and
                    total_failed == 0
                )
            }
        }
        
        return comprehensive_report
    
    def save_report(self, report: Dict[str, Any]):
        """Save comprehensive report to file."""
        
        report_file = self.test_dir / "test_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 Comprehensive report saved: {report_file}")
        
        # Also create human-readable summary
        summary_file = self.test_dir / "test_summary.txt"
        
        with open(summary_file, 'w') as f:
            f.write("N8N Framework Integration - Test Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Test Duration: {report['test_execution']['duration_seconds']:.1f} seconds\n")
            f.write(f"Total Tests: {report['test_results']['total_tests']}\n")
            f.write(f"Passed: {report['test_results']['passed_tests']}\n")
            f.write(f"Failed: {report['test_results']['failed_tests']}\n")
            f.write(f"Success Rate: {report['test_results']['success_rate_percent']:.1f}%\n")
            f.write(f"Coverage: {report['coverage']['coverage_percent']:.1f}%\n\n")
            
            f.write("Industrial Compliance:\n")
            f.write(f"- Coverage Requirement (>95%): {'✅ PASS' if report['industrial_compliance']['coverage_requirement_met'] else '❌ FAIL'}\n")
            f.write(f"- Success Rate Requirement (>95%): {'✅ PASS' if report['industrial_compliance']['success_rate_requirement_met'] else '❌ FAIL'}\n")
            
            f.write(f"\nPhase 1.5 Ready: {'✅ YES' if report['phase_completion']['phase_1_5_ready'] else '❌ NO'}\n")
        
        print(f"📋 Test summary saved: {summary_file}")


def main():
    """Main entry point for test runner."""
    
    parser = argparse.ArgumentParser(
        description="N8N Framework Integration - Comprehensive Test Runner"
    )
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")  
    parser.add_argument("--performance", action="store_true", help="Run performance tests only")
    parser.add_argument("--industrial", action="store_true", help="Run industrial compliance tests only")
    parser.add_argument("--coverage", action="store_true", help="Generate detailed coverage report")
    parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = TestRunner()
    runner.setup_environment()
    
    print("🚀 N8N Framework Integration - Automated Test Suite")
    print("=" * 60)
    print("Phase 1.5: Automated Testing Suite Implementation")
    print("Target: >95% Test Coverage with Industrial Compliance")
    print("=" * 60)
    
    # Record start time
    start_time = time.time()
    runner.results["start_time"] = start_time
    
    all_results = []
    
    try:
        # Run requested test suites
        if args.unit:
            all_results.append(runner.run_unit_tests())
        elif args.integration:
            all_results.append(runner.run_integration_tests())
        elif args.performance or args.industrial:
            all_results.append(runner.run_performance_tests())
        else:
            # Run all tests by default
            all_results.append(runner.run_unit_tests())
            all_results.append(runner.run_integration_tests())
            all_results.append(runner.run_performance_tests())
        
    except KeyboardInterrupt:
        print("\n⏹️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)
    
    # Record end time
    end_time = time.time()
    runner.results["end_time"] = end_time
    runner.results["duration_seconds"] = end_time - start_time
    
    # Generate comprehensive report
    comprehensive_report = runner.generate_comprehensive_report(all_results)
    
    # Save report
    if args.report or not any([args.unit, args.integration, args.performance, args.industrial]):
        runner.save_report(comprehensive_report)
    
    # Print final summary
    print("\n" + "=" * 60)
    print("🎯 PHASE 1.5 TEST EXECUTION COMPLETE")
    print("=" * 60)
    
    overall_success = comprehensive_report["phase_completion"]["phase_1_5_ready"]
    status_emoji = "✅" if overall_success else "❌"
    
    print(f"{status_emoji} Overall Status: {'PASS' if overall_success else 'FAIL'}")
    print(f"📊 Test Coverage: {comprehensive_report['coverage']['coverage_percent']:.1f}%")
    print(f"📈 Success Rate: {comprehensive_report['test_results']['success_rate_percent']:.1f}%")
    print(f"⏱️ Duration: {comprehensive_report['test_execution']['duration_seconds']:.1f}s")
    
    if overall_success:
        print("\n🎉 Phase 1.5 Requirements Met - Ready for User Validation!")
        print("Next Step: Phase 1.6 - User Interactive Testing and Validation")
        sys.exit(0)
    else:
        print("\n⚠️ Phase 1.5 Requirements Not Met - Review Test Results")
        sys.exit(1)


if __name__ == "__main__":
    main()
