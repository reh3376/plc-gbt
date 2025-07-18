#!/usr/bin/env python3
"""
PLC-GBT CLI Testing Framework
============================

Comprehensive testing suite for CLI integration, performance benchmarks,
and CI/CD integration with systematic validation and reporting.

Key Features:
- Integration test suite for all CLI commands
- Performance benchmarking with baseline comparisons
- Memory system validation testing
- PLC integration testing (simulated and real)
- CI/CD pipeline integration
- Comprehensive reporting and analytics
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil
import pytest
import yaml
from dataclasses import dataclass, field
from contextlib import asynccontextmanager, contextmanager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Individual test result with detailed metrics."""
    test_name: str
    test_type: str
    status: str  # passed, failed, skipped
    duration: float
    memory_usage: Optional[float] = None
    cpu_usage: Optional[float] = None
    error_message: Optional[str] = None
    output: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BenchmarkResult:
    """Performance benchmark result."""
    operation: str
    duration: float
    memory_peak: float
    cpu_peak: float
    throughput: Optional[float] = None
    baseline_comparison: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """Collection of related tests."""
    name: str
    description: str
    tests: List[TestResult] = field(default_factory=list)
    benchmarks: List[BenchmarkResult] = field(default_factory=list)
    setup_time: float = 0.0
    teardown_time: float = 0.0
    total_duration: float = 0.0


class CLITestFramework:
    """
    Comprehensive CLI testing framework with integration tests,
    performance benchmarks, and reporting capabilities.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent / "config.yaml"
        self.config = self._load_config()
        self.results_dir = Path(self.config.get("results_dir", "./test_results"))
        self.results_dir.mkdir(exist_ok=True)
        
        self.test_suites: List[TestSuite] = []
        self.session_id = str(uuid.uuid4())[:8]
        self.start_time = datetime.now()
        
        # Performance baselines
        self.baselines = self._load_baselines()
        
        # CLI command base
        self.cli_command = self.config.get("cli_command", "plc-memory")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load testing configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Default testing configuration."""
        return {
            "cli_command": "plc-memory",
            "timeout": 60,
            "memory_limit_mb": 1024,
            "performance_threshold": 0.2,  # 20% degradation threshold
            "parallel_tests": 4,
            "retry_count": 3,
            "results_dir": "./test_results",
            "baselines_file": "performance_baselines.json",
            "test_environments": ["development", "staging"],
            "benchmark_iterations": 5,
            "integration_tests": {
                "enable_plc_tests": False,  # Requires real PLC
                "plc_host": "192.168.1.100",
                "plc_slot": 0,
                "test_schemas": ["basic", "pid-control"],
                "test_instances": 3
            }
        }
    
    def _load_baselines(self) -> Dict[str, float]:
        """Load performance baselines."""
        baseline_file = self.results_dir / self.config.get("baselines_file", "performance_baselines.json")
        if baseline_file.exists():
            with open(baseline_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_baselines(self):
        """Save performance baselines."""
        baseline_file = self.results_dir / self.config.get("baselines_file", "performance_baselines.json")
        with open(baseline_file, 'w') as f:
            json.dump(self.baselines, f, indent=2)
    
    @contextmanager
    def performance_monitor(self):
        """Monitor performance metrics during test execution."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        initial_cpu = process.cpu_percent()
        start_time = time.time()
        
        peak_memory = initial_memory
        peak_cpu = initial_cpu
        
        try:
            yield
        finally:
            end_time = time.time()
            final_memory = process.memory_info().rss / 1024 / 1024
            final_cpu = process.cpu_percent()
            
            duration = end_time - start_time
            peak_memory = max(peak_memory, final_memory)
            peak_cpu = max(peak_cpu, final_cpu)
            
            # Store metrics for access
            self._current_metrics = {
                "duration": duration,
                "peak_memory": peak_memory,
                "peak_cpu": peak_cpu,
                "memory_delta": final_memory - initial_memory
            }
    
    async def run_cli_command(self, command: List[str], timeout: Optional[int] = None) -> Tuple[int, str, str]:
        """
        Execute CLI command asynchronously with timeout and error handling.
        
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        timeout = timeout or self.config.get("timeout", 60)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            
            return process.returncode, stdout.decode(), stderr.decode()
            
        except asyncio.TimeoutError:
            logger.error(f"Command timed out after {timeout}s: {' '.join(command)}")
            return -1, "", f"Command timed out after {timeout}s"
        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            return -1, "", str(e)
    
    async def test_schema_management(self) -> TestSuite:
        """Test schema management operations."""
        suite = TestSuite(
            name="schema_management",
            description="Test all schema management operations"
        )
        
        # Test schema creation
        test_schema_name = f"test_schema_{self.session_id}"
        
        # Create schema test
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "schema", "create",
                "--name", test_schema_name,
                "--description", "Test schema for automated testing",
                "--template", "basic"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="schema_create",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test schema listing
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "schema", "list", "--format", "json"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="schema_list",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test schema validation
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "schema", "validate", test_schema_name
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="schema_validate",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test schema export
        export_file = self.results_dir / f"exported_schema_{self.session_id}.json"
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "schema", "export", test_schema_name,
                "--output", str(export_file), "--format", "json"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="schema_export",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout,
            metadata={"export_file": str(export_file)}
        ))
        
        # Cleanup: Delete test schema
        await self.run_cli_command([
            self.cli_command, "schema", "delete", test_schema_name, "--force"
        ])
        
        return suite
    
    async def test_instance_management(self) -> TestSuite:
        """Test instance management operations."""
        suite = TestSuite(
            name="instance_management",
            description="Test all instance management operations"
        )
        
        # First create a test schema
        test_schema_name = f"test_schema_inst_{self.session_id}"
        await self.run_cli_command([
            self.cli_command, "schema", "create",
            "--name", test_schema_name,
            "--template", "basic"
        ])
        
        test_instance_name = f"test_instance_{self.session_id}"
        
        # Test instance creation
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "instance", "create",
                "--name", test_instance_name,
                "--schema", test_schema_name,
                "--environment", "development"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="instance_create",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test instance listing
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "instance", "list", "--format", "json"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="instance_list",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test instance status
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "instance", "status", test_instance_name
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="instance_status",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Cleanup
        await self.run_cli_command([
            self.cli_command, "instance", "delete", test_instance_name, "--force"
        ])
        await self.run_cli_command([
            self.cli_command, "schema", "delete", test_schema_name, "--force"
        ])
        
        return suite
    
    async def test_memory_system(self) -> TestSuite:
        """Test memory system operations."""
        suite = TestSuite(
            name="memory_system",
            description="Test memory system integration and operations"
        )
        
        # Test memory status
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "memory", "status", "--format", "json"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="memory_status",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test memory search
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "memory", "search", "test", "--limit", "10"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="memory_search",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test memory statistics
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "memory", "stats", "--detailed"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="memory_stats",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        return suite
    
    async def test_batch_operations(self) -> TestSuite:
        """Test batch processing operations."""
        suite = TestSuite(
            name="batch_operations",
            description="Test batch processing and job management"
        )
        
        # Create a simple batch script
        batch_script = self.results_dir / f"test_batch_{self.session_id}.py"
        with open(batch_script, 'w') as f:
            f.write("""
#!/usr/bin/env python3
import time
import sys

print("Batch job starting...")
time.sleep(2)
print("Batch job completed successfully")
sys.exit(0)
""")
        batch_script.chmod(0o755)
        
        test_job_name = f"test_job_{self.session_id}"
        
        # Test batch job creation
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "batch", "create",
                "--name", test_job_name,
                "--script", str(batch_script),
                "--priority", "normal"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="batch_create",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test batch job listing
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "batch", "list", "--format", "json"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="batch_list",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Test batch job execution
        with self.performance_monitor():
            start_time = time.time()
            ret_code, stdout, stderr = await self.run_cli_command([
                self.cli_command, "batch", "run", test_job_name, "--timeout", "30"
            ])
            duration = time.time() - start_time
        
        suite.tests.append(TestResult(
            test_name="batch_run",
            test_type="integration",
            status="passed" if ret_code == 0 else "failed",
            duration=duration,
            memory_usage=self._current_metrics.get("peak_memory"),
            cpu_usage=self._current_metrics.get("peak_cpu"),
            error_message=stderr if ret_code != 0 else None,
            output=stdout
        ))
        
        # Cleanup
        batch_script.unlink()
        
        return suite
    
    async def benchmark_performance(self) -> List[BenchmarkResult]:
        """Run performance benchmarks."""
        benchmarks = []
        iterations = self.config.get("benchmark_iterations", 5)
        
        # Benchmark schema operations
        for i in range(iterations):
            schema_name = f"bench_schema_{i}_{self.session_id}"
            
            with self.performance_monitor():
                start_time = time.time()
                await self.run_cli_command([
                    self.cli_command, "schema", "create",
                    "--name", schema_name,
                    "--template", "basic"
                ])
                create_duration = time.time() - start_time
            
            benchmarks.append(BenchmarkResult(
                operation="schema_create",
                duration=create_duration,
                memory_peak=self._current_metrics.get("peak_memory", 0),
                cpu_peak=self._current_metrics.get("peak_cpu", 0),
                baseline_comparison=self._compare_to_baseline("schema_create", create_duration)
            ))
            
            # Cleanup
            await self.run_cli_command([
                self.cli_command, "schema", "delete", schema_name, "--force"
            ])
        
        # Benchmark memory operations
        for i in range(iterations):
            with self.performance_monitor():
                start_time = time.time()
                await self.run_cli_command([
                    self.cli_command, "memory", "status"
                ])
                status_duration = time.time() - start_time
            
            benchmarks.append(BenchmarkResult(
                operation="memory_status",
                duration=status_duration,
                memory_peak=self._current_metrics.get("peak_memory", 0),
                cpu_peak=self._current_metrics.get("peak_cpu", 0),
                baseline_comparison=self._compare_to_baseline("memory_status", status_duration)
            ))
        
        return benchmarks
    
    def _compare_to_baseline(self, operation: str, duration: float) -> Optional[float]:
        """Compare performance to baseline."""
        if operation in self.baselines:
            baseline = self.baselines[operation]
            return (duration - baseline) / baseline * 100  # Percentage change
        return None
    
    def _update_baselines(self, benchmarks: List[BenchmarkResult]):
        """Update performance baselines with new measurements."""
        for benchmark in benchmarks:
            operation = benchmark.operation
            if operation not in self.baselines:
                self.baselines[operation] = benchmark.duration
            else:
                # Use exponential moving average
                alpha = 0.1
                self.baselines[operation] = (
                    alpha * benchmark.duration + 
                    (1 - alpha) * self.baselines[operation]
                )
    
    async def run_integration_tests(self) -> List[TestSuite]:
        """Run all integration tests."""
        logger.info("Starting integration test suite...")
        
        test_suites = []
        
        # Run individual test suites
        try:
            test_suites.append(await self.test_schema_management())
            test_suites.append(await self.test_instance_management())
            test_suites.append(await self.test_memory_system())
            test_suites.append(await self.test_batch_operations())
            
            # Run PLC tests if enabled
            if self.config.get("integration_tests", {}).get("enable_plc_tests", False):
                test_suites.append(await self.test_plc_integration())
            
        except Exception as e:
            logger.error(f"Integration test error: {e}")
            raise
        
        self.test_suites = test_suites
        return test_suites
    
    async def run_performance_tests(self) -> List[BenchmarkResult]:
        """Run performance benchmarks."""
        logger.info("Starting performance benchmarks...")
        
        benchmarks = await self.benchmark_performance()
        self._update_baselines(benchmarks)
        self._save_baselines()
        
        return benchmarks
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Aggregate test results
        total_tests = sum(len(suite.tests) for suite in self.test_suites)
        passed_tests = sum(1 for suite in self.test_suites for test in suite.tests if test.status == "passed")
        failed_tests = sum(1 for suite in self.test_suites for test in suite.tests if test.status == "failed")
        
        # Performance summary
        benchmarks = []
        for suite in self.test_suites:
            benchmarks.extend(suite.benchmarks)
        
        report = {
            "session_id": self.session_id,
            "timestamp": self.start_time.isoformat(),
            "duration": total_duration,
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_suites": len(self.test_suites)
            },
            "test_suites": [
                {
                    "name": suite.name,
                    "description": suite.description,
                    "total_tests": len(suite.tests),
                    "passed": len([t for t in suite.tests if t.status == "passed"]),
                    "failed": len([t for t in suite.tests if t.status == "failed"]),
                    "duration": suite.total_duration,
                    "tests": [
                        {
                            "name": test.test_name,
                            "type": test.test_type,
                            "status": test.status,
                            "duration": test.duration,
                            "memory_usage": test.memory_usage,
                            "cpu_usage": test.cpu_usage,
                            "error": test.error_message,
                            "timestamp": test.timestamp
                        }
                        for test in suite.tests
                    ]
                }
                for suite in self.test_suites
            ],
            "performance": {
                "benchmarks": [
                    {
                        "operation": b.operation,
                        "duration": b.duration,
                        "memory_peak": b.memory_peak,
                        "cpu_peak": b.cpu_peak,
                        "baseline_comparison": b.baseline_comparison
                    }
                    for b in benchmarks
                ],
                "baselines": self.baselines
            },
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cli_command": self.cli_command,
                "config": self.config
            }
        }
        
        return report
    
    def save_report(self, report: Dict[str, Any]):
        """Save test report to file."""
        report_file = self.results_dir / f"test_report_{self.session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved: {report_file}")
        
        # Also save summary
        summary_file = self.results_dir / f"test_summary_{self.session_id}.txt"
        with open(summary_file, 'w') as f:
            f.write(f"PLC-GBT CLI Test Report Summary\n")
            f.write(f"================================\n\n")
            f.write(f"Session ID: {report['session_id']}\n")
            f.write(f"Timestamp: {report['timestamp']}\n")
            f.write(f"Duration: {report['duration']:.2f}s\n\n")
            f.write(f"Test Results:\n")
            f.write(f"  Total Tests: {report['summary']['total_tests']}\n")
            f.write(f"  Passed: {report['summary']['passed']}\n")
            f.write(f"  Failed: {report['summary']['failed']}\n")
            f.write(f"  Success Rate: {report['summary']['success_rate']:.1f}%\n\n")
            
            for suite in report['test_suites']:
                f.write(f"Suite: {suite['name']}\n")
                f.write(f"  Tests: {suite['total_tests']}, Passed: {suite['passed']}, Failed: {suite['failed']}\n")
                if suite['failed'] > 0:
                    f.write(f"  Failed Tests:\n")
                    for test in suite['tests']:
                        if test['status'] == 'failed':
                            f.write(f"    - {test['name']}: {test['error']}\n")
                f.write(f"\n")
        
        return report_file


class CICDIntegration:
    """CI/CD pipeline integration for automated testing."""
    
    @staticmethod
    def generate_github_workflow() -> str:
        """Generate GitHub Actions workflow for automated testing."""
        return """
name: PLC-GBT CLI Testing

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest psutil pyyaml
    
    - name: Run CLI tests
      run: |
        python -m plc_gbt_stack.cli.testing.test_framework
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.python-version }}
        path: test_results/
    
    - name: Publish test report
      uses: mikepenz/action-junit-report@v3
      if: always()
      with:
        report_paths: 'test_results/junit_*.xml'
        check_name: 'CLI Tests (${{ matrix.python-version }})'
"""
    
    @staticmethod
    def generate_jenkins_pipeline() -> str:
        """Generate Jenkins pipeline for automated testing."""
        return """
pipeline {
    agent any
    
    triggers {
        pollSCM('H/15 * * * *')  # Poll every 15 minutes
        cron('H 2 * * *')        # Daily build at 2 AM
    }
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
        PLC_MEMORY_TEST_ENV = "ci"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Setup Environment') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest psutil pyyaml
                '''
            }
        }
        
        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m plc_gbt_stack.cli.testing.test_framework
                '''
            }
        }
        
        stage('Archive Results') {
            steps {
                archiveArtifacts artifacts: 'test_results/**/*', fingerprint: true
                publishTestResults testResultsPattern: 'test_results/junit_*.xml'
            }
        }
    }
    
    post {
        always {
            cleanWs()
        }
        failure {
            emailext (
                subject: "PLC-GBT CLI Tests Failed: ${env.BUILD_TAG}",
                body: "The CLI test suite failed. Check console output.",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }
    }
}
"""


async def main():
    """Main test execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="PLC-GBT CLI Testing Framework")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance benchmarks")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--report-only", action="store_true", help="Generate report from existing results")
    parser.add_argument("--ci", action="store_true", help="Generate CI/CD configuration files")
    
    args = parser.parse_args()
    
    if args.ci:
        # Generate CI/CD files
        ci_integration = CICDIntegration()
        
        # GitHub Actions
        github_dir = Path(".github/workflows")
        github_dir.mkdir(parents=True, exist_ok=True)
        with open(github_dir / "cli_testing.yml", "w") as f:
            f.write(ci_integration.generate_github_workflow())
        
        # Jenkins
        with open("Jenkinsfile", "w") as f:
            f.write(ci_integration.generate_jenkins_pipeline())
        
        print("CI/CD configuration files generated:")
        print("  - .github/workflows/cli_testing.yml")
        print("  - Jenkinsfile")
        return
    
    # Initialize test framework
    framework = CLITestFramework(config_path=args.config)
    
    try:
        if args.all or args.integration:
            await framework.run_integration_tests()
        
        if args.all or args.performance:
            await framework.run_performance_tests()
        
        # Generate and save report
        report = framework.generate_report()
        report_file = framework.save_report(report)
        
        # Print summary
        print(f"\nTest Execution Complete!")
        print(f"Session ID: {framework.session_id}")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Report saved: {report_file}")
        
        # Exit with failure code if tests failed
        if report['summary']['failed'] > 0:
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 