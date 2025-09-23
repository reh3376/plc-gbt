"""Test helpers and assertions for orchestrator testing."""

import asyncio
import functools
import time
import unittest
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar
from unittest.mock import patch

from plc_orchestrator.utils.data_models import TaskAnalysis, ValidationResult
from plc_orchestrator.utils.enums import TaskComplexity, ValidationSeverity
from plc_orchestrator.utils.performance import PerformanceMonitor

T = TypeVar("T")


class OrchestratorTestCase(unittest.TestCase):
    """Base test case class with orchestrator-specific helpers."""

    def setUp(self):
        """Set up test case."""
        super().setUp()
        self.performance_monitor = PerformanceMonitor()
        self._test_start_time = time.time()

    def tearDown(self):
        """Tear down test case."""
        super().tearDown()
        test_duration = time.time() - self._test_start_time
        if test_duration > 1.0:
            print(f"\n⚠️  Slow test: {self._testMethodName} took {test_duration:.2f}s")

    def assert_task_valid(self, analysis: TaskAnalysis, **checks):
        """Assert task analysis is valid with optional checks."""
        assert_task_valid(analysis, **checks)

    def assert_validation_passed(
        self, result: ValidationResult, min_score: float = 70.0, max_issues: int = 0
    ):
        """Assert validation passed with constraints."""
        assert_validation_passed(result, min_score, max_issues)

    @contextmanager
    def assert_performance(self, max_duration: float):
        """Assert operation completes within time limit."""
        start = time.perf_counter()
        yield
        duration = time.perf_counter() - start
        self.assertLessEqual(
            duration, max_duration, f"Operation took {duration:.3f}s, expected <= {max_duration}s"
        )

    def run_async(self, coro):
        """Run async coroutine in test."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()


# Assertion functions
def assert_task_valid(
    analysis: TaskAnalysis,
    expected_complexity: str | None = None,
    min_requirements: int = 1,
    max_risks: int | None = None,
    check_execution_plan: bool = True,
    check_estimates: bool = True,
):
    """
    Assert that a task analysis is valid.

    Args:
        analysis: Task analysis to validate
        expected_complexity: Expected complexity level
        min_requirements: Minimum number of requirements
        max_risks: Maximum number of risks
        check_execution_plan: Whether to check execution plan
        check_estimates: Whether to check effort estimates

    Raises:
        AssertionError: If validation fails
    """
    # Basic structure
    assert analysis.task_id, "Task ID should not be empty"
    assert analysis.description, "Description should not be empty"

    # Complexity
    valid_complexities = [c.value for c in TaskComplexity]
    assert analysis.complexity in valid_complexities, f"Invalid complexity: {analysis.complexity}"

    if expected_complexity:
        assert analysis.complexity == expected_complexity, (
            f"Expected complexity {expected_complexity}, got {analysis.complexity}"
        )

    # Requirements
    assert len(analysis.requirements) >= min_requirements, (
        f"Expected at least {min_requirements} requirements, got {len(analysis.requirements)}"
    )

    # Risks
    if max_risks is not None:
        assert len(analysis.risks) <= max_risks, (
            f"Expected at most {max_risks} risks, got {len(analysis.risks)}"
        )

    # Execution plan
    if check_execution_plan:
        assert analysis.execution_plan, "Execution plan should not be empty"
        for i, step in enumerate(analysis.execution_plan):
            assert "step" in step, f"Step {i} missing 'step' field"
            assert "name" in step, f"Step {i} missing 'name' field"
            assert "description" in step, f"Step {i} missing 'description' field"

    # Estimates
    if check_estimates:
        assert analysis.estimated_effort, "Estimated effort should not be empty"
        assert "hours" in analysis.estimated_effort, "Missing 'hours' in effort"
        assert "confidence" in analysis.estimated_effort, "Missing 'confidence' in effort"
        assert 0 <= analysis.estimated_effort["confidence"] <= 1, (
            "Confidence should be between 0 and 1"
        )


def assert_validation_passed(
    result: ValidationResult,
    min_score: float = 70.0,
    max_issues: int = 0,
    required_tier: str | None = None,
):
    """
    Assert that validation passed with constraints.

    Args:
        result: Validation result to check
        min_score: Minimum acceptable score
        max_issues: Maximum number of issues allowed
        required_tier: Required validation tier

    Raises:
        AssertionError: If validation doesn't meet criteria
    """
    assert result.passed, "Validation should have passed"
    assert result.score >= min_score, f"Score {result.score} is below minimum {min_score}"
    assert len(result.issues) <= max_issues, (
        f"Found {len(result.issues)} issues, maximum allowed is {max_issues}"
    )

    if required_tier:
        assert result.validation_tier == required_tier, (
            f"Expected tier {required_tier}, got {result.validation_tier}"
        )

    # Check no critical issues
    critical_issues = [
        i for i in result.issues if i.get("severity") == ValidationSeverity.CRITICAL.value
    ]
    assert not critical_issues, f"Found {len(critical_issues)} critical issues"


def assert_no_errors(issues: list[dict[str, Any]], severity: str | None = None):
    """
    Assert no errors in issue list.

    Args:
        issues: List of issues
        severity: Specific severity to check (None for all)

    Raises:
        AssertionError: If errors found
    """
    if severity:
        filtered = [i for i in issues if i.get("severity") == severity]
        assert not filtered, f"Found {len(filtered)} issues with severity {severity}"
    else:
        assert not issues, f"Found {len(issues)} issues"


# Performance helpers
@contextmanager
def capture_performance(name: str, monitor: PerformanceMonitor | None = None):
    """
    Context manager to capture performance metrics.

    Args:
        name: Name of the operation
        monitor: Performance monitor to use (creates new if None)

    Yields:
        Performance monitor instance
    """
    if monitor is None:
        monitor = PerformanceMonitor()

    with monitor.measure(name):
        yield monitor


def with_test_timeout(timeout: float = 5.0):
    """
    Decorator to add timeout to test functions.

    Args:
        timeout: Timeout in seconds

    Returns:
        Decorated function
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError(f"Test timed out after {timeout}s")

            # Set alarm
            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))

            try:
                return func(*args, **kwargs)
            finally:
                # Clear alarm
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Mock helpers
class MockContext:
    """Context manager for multiple patches."""

    def __init__(self):
        self.patches = []
        self.mocks = {}

    def add_patch(self, target: str, **kwargs):
        """Add a patch to the context."""
        p = patch(target, **kwargs)
        self.patches.append((target, p))
        return self

    def __enter__(self):
        """Enter context and start patches."""
        for target, p in self.patches:
            mock = p.start()
            # Extract name from target
            name = target.split(".")[-1]
            self.mocks[name] = mock
        return self.mocks

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and stop patches."""
        for _, p in self.patches:
            p.stop()


# Comparison helpers
def assert_tasks_equal(
    task1: TaskAnalysis, task2: TaskAnalysis, ignore_fields: list[str] | None = None
):
    """
    Assert two task analyses are equal.

    Args:
        task1: First task
        task2: Second task
        ignore_fields: Fields to ignore in comparison

    Raises:
        AssertionError: If tasks differ
    """
    ignore_fields = ignore_fields or []

    # Compare all fields
    for field in task1.__dataclass_fields__:
        if field in ignore_fields:
            continue

        val1 = getattr(task1, field)
        val2 = getattr(task2, field)

        assert val1 == val2, f"Field '{field}' differs: {val1} != {val2}"


def assert_validation_improved(
    before: ValidationResult, after: ValidationResult, min_improvement: float = 10.0
):
    """
    Assert validation result improved.

    Args:
        before: Previous validation result
        after: New validation result
        min_improvement: Minimum score improvement

    Raises:
        AssertionError: If not improved enough
    """
    score_improvement = after.score - before.score
    assert score_improvement >= min_improvement, (
        f"Score improved by {score_improvement}, expected at least {min_improvement}"
    )

    # Check issue reduction
    issues_before = len(before.issues)
    issues_after = len(after.issues)
    assert issues_after <= issues_before, f"Issues increased from {issues_before} to {issues_after}"


# Data validation helpers
def validate_json_response(response: dict[str, Any], required_fields: list[str]):
    """
    Validate JSON response structure.

    Args:
        response: Response dictionary
        required_fields: Required field names

    Raises:
        AssertionError: If validation fails
    """
    for field in required_fields:
        assert field in response, f"Missing required field: {field}"
        assert response[field] is not None, f"Field '{field}' is None"


# Async test helpers
async def run_concurrent_tests(test_funcs: list[Callable], timeout: float = 10.0):
    """
    Run multiple test functions concurrently.

    Args:
        test_funcs: List of test functions to run
        timeout: Timeout for all tests

    Returns:
        List of results

    Raises:
        TimeoutError: If tests don't complete in time
    """
    tasks = [asyncio.create_task(func()) for func in test_funcs]
    return await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout)


# Coverage helpers
class CoverageTracker:
    """Track code coverage for specific features."""

    def __init__(self):
        self.covered_features = set()
        self.required_features = set()

    def require(self, *features: str):
        """Mark features as required."""
        self.required_features.update(features)

    def cover(self, feature: str):
        """Mark feature as covered."""
        self.covered_features.add(feature)

    def assert_coverage(self, min_percentage: float = 100.0):
        """Assert coverage meets minimum percentage."""
        if not self.required_features:
            return

        coverage = len(self.covered_features) / len(self.required_features) * 100
        uncovered = self.required_features - self.covered_features

        assert coverage >= min_percentage, (
            f"Coverage {coverage:.1f}% below minimum {min_percentage}%. Uncovered: {uncovered}"
        )
