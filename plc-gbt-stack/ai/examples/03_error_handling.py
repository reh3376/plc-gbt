#!/usr/bin/env python3
"""
Error handling patterns for the AI Task Orchestrator.

This example demonstrates:
1. Handling configuration errors
2. Graceful degradation without memory
3. Validation error recovery
4. Custom error handlers
5. Retry mechanisms
"""

import asyncio
import logging
from collections.abc import Callable
from contextlib import contextmanager
from typing import TypeVar

from plc_orchestrator import ValidationTier, create_orchestrator
from plc_orchestrator.utils.errors import (
    ConfigurationError,
    TaskAnalysisError,
    ValidationError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorHandlingExamples:
    """Examples of error handling patterns."""

    def example_configuration_errors(self):
        """Example: Handle configuration errors gracefully."""
        print("\n" + "=" * 60)
        print("Example 1: Configuration Error Handling")
        print("=" * 60)

        # Example 1a: Invalid configuration
        print("\n1a. Handling invalid configuration:")
        try:
            orchestrator = create_orchestrator(
                environment="invalid_env",  # Invalid environment
                max_workers=200,  # Out of range
                timeout_seconds=5,  # Too low
            )
        except ConfigurationError as e:
            print(f"  ❌ Configuration error caught: {e}")
            print(f"     Details: {e.details if hasattr(e, 'details') else 'N/A'}")

            # Fallback to defaults
            print("\n  ✓ Using default configuration instead")
            orchestrator = create_orchestrator()
            print(f"    Environment: {orchestrator.config.settings.environment}")

        # Example 1b: Missing required API keys
        print("\n1b. Handling missing API keys:")
        try:
            orchestrator = create_orchestrator(
                enable_math_validation=True,
                wolfram_alpha_api_key=None,  # Missing required key
            )

            # Try to use math validation
            analysis = orchestrator.analyze_task("Calculate derivative of x^2")
            if not analysis.requires_mathematical_validation():
                print("  ⚠️  Math validation disabled due to missing API key")

        except ConfigurationError:
            print("  ✓ Gracefully disabled math validation")

    def example_memory_degradation(self):
        """Example: Graceful degradation when memory is unavailable."""
        print("\n" + "=" * 60)
        print("Example 2: Memory System Degradation")
        print("=" * 60)

        # Try with memory, fallback without
        print("\n2a. Attempting with memory system:")
        try:
            orchestrator = create_orchestrator(
                enable_memory=True,
                redis_url="redis://invalid:6379",  # Invalid Redis URL
            )

            analysis = orchestrator.analyze_task("Build data parser")
            print("  ⚠️  Analysis completed without memory insights")
            print(f"     Task ID: {analysis.task_id}")
            print(f"     Complexity: {analysis.complexity}")

        except Exception as e:
            logger.warning(f"Memory system failed: {e}")

        # Explicit fallback
        print("\n2b. Explicit memory fallback:")
        orchestrator = create_orchestrator(enable_memory=False)
        analysis = orchestrator.analyze_task("Build data parser")
        print("  ✓ Analysis successful without memory")
        print(f"    Complexity: {analysis.complexity}")

    def example_validation_errors(self):
        """Example: Handle validation errors with detailed feedback."""
        print("\n" + "=" * 60)
        print("Example 3: Validation Error Handling")
        print("=" * 60)

        orchestrator = create_orchestrator()

        # Invalid code examples
        test_cases = [
            ("Empty code", ""),
            ("Syntax error", "def func(\n    pass"),
            ("Missing requirements", "def add(a, b): return a + b"),
            ("Security issue", "import os\nos.system('rm -rf /')"),
        ]

        for name, code in test_cases:
            print(f"\n3. Testing: {name}")
            try:
                validation = orchestrator.validate_implementation(
                    code,
                    ["implement function", "include error handling"],
                    validation_tier=ValidationTier.PRODUCTION,
                )

                if not validation.passed:
                    print(f"  ⚠️  Validation failed (score: {validation.score}/100)")
                    # Show first few issues
                    for issue in validation.issues[:2]:
                        print(f"     - [{issue['severity']}] {issue['message']}")

                    # Show recommendations
                    if validation.recommendations:
                        print("  💡 Recommendations:")
                        for rec in validation.recommendations[:2]:
                            print(f"     - {rec}")

            except ValidationError as e:
                print(f"  ❌ Validation error: {e}")
            except Exception as e:
                print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")

    def example_retry_mechanism(self):
        """Example: Implement retry logic for transient failures."""
        print("\n" + "=" * 60)
        print("Example 4: Retry Mechanisms")
        print("=" * 60)

        async def retry_with_backoff(
            func: Callable[..., T],
            max_retries: int = 3,
            backoff_factor: float = 2.0,
            *args,
            **kwargs,
        ) -> T | None:
            """Retry function with exponential backoff."""
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return (
                        await func(*args, **kwargs)
                        if asyncio.iscoroutinefunction(func)
                        else func(*args, **kwargs)
                    )
                except (ConnectionError, TimeoutError) as e:
                    last_exception = e
                    wait_time = backoff_factor**attempt
                    print(f"  Attempt {attempt + 1} failed: {e}")
                    print(f"  Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
                except Exception as e:
                    # Non-retryable error
                    print(f"  Non-retryable error: {e}")
                    raise

            print(f"  ❌ All {max_retries} attempts failed")
            raise last_exception or Exception("All retries failed")

        # Example usage
        async def flaky_operation():
            """Simulate a flaky operation."""
            import random

            if random.random() < 0.7:  # 70% failure rate
                raise ConnectionError("Service temporarily unavailable")
            return "Success!"

        print("\n4. Retrying flaky operation:")
        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(retry_with_backoff(flaky_operation, max_retries=5))
            print(f"  ✓ Operation succeeded: {result}")
        except Exception as e:
            print(f"  ❌ Operation failed after retries: {e}")

    def example_custom_error_handlers(self):
        """Example: Custom error handlers for specific scenarios."""
        print("\n" + "=" * 60)
        print("Example 5: Custom Error Handlers")
        print("=" * 60)

        class TaskErrorHandler:
            """Custom error handler for task processing."""

            def __init__(self):
                self.error_count = 0
                self.error_log = []

            @contextmanager
            def handle_task_errors(self, task_description: str):
                """Context manager for task error handling."""
                try:
                    print(f"\n5. Processing task: {task_description[:50]}...")
                    yield
                    print("  ✓ Task completed successfully")

                except TaskAnalysisError as e:
                    self.error_count += 1
                    self.error_log.append(f"Analysis failed: {e}")
                    print(f"  ❌ Task analysis error: {e}")

                    # Attempt recovery
                    print("  🔄 Attempting simplified analysis...")
                    # Implement fallback logic here

                except ValidationError as e:
                    self.error_count += 1
                    self.error_log.append(f"Validation failed: {e}")
                    print(f"  ❌ Validation error: {e}")

                    # Provide actionable feedback
                    print("  💡 Suggestions:")
                    print("     - Check syntax and formatting")
                    print("     - Ensure all requirements are met")
                    print("     - Review security guidelines")

                except Exception as e:
                    self.error_count += 1
                    self.error_log.append(f"Unexpected: {type(e).__name__}: {e}")
                    print(f"  ❌ Unexpected error: {type(e).__name__}: {e}")

                    # Log for debugging
                    logger.exception("Unexpected error in task processing")

                finally:
                    if self.error_count > 0:
                        print("\n  📊 Error Summary:")
                        print(f"     Total errors: {self.error_count}")
                        print(f"     Recent errors: {len(self.error_log[-5:])}")

        # Use custom handler
        handler = TaskErrorHandler()
        orchestrator = create_orchestrator()

        # Test with various tasks
        test_tasks = [
            "Normal task: Create user authentication",
            "",  # Empty task
            "x" * 10000,  # Very long task
        ]

        for task in test_tasks:
            with handler.handle_task_errors(task):
                if not task:
                    raise TaskAnalysisError("Empty task description")
                elif len(task) > 5000:
                    raise TaskAnalysisError("Task description too long")
                else:
                    analysis = orchestrator.analyze_task(task)
                    print(f"    Complexity: {analysis.complexity}")

    def example_error_aggregation(self):
        """Example: Aggregate and report errors."""
        print("\n" + "=" * 60)
        print("Example 6: Error Aggregation and Reporting")
        print("=" * 60)

        from collections import defaultdict
        from datetime import datetime

        class ErrorAggregator:
            """Aggregate errors for reporting."""

            def __init__(self):
                self.errors_by_type = defaultdict(list)
                self.errors_by_severity = defaultdict(int)
                self.start_time = datetime.now()

            def record_error(self, error_type: str, severity: str, message: str):
                """Record an error."""
                error_entry = {
                    "timestamp": datetime.now(),
                    "severity": severity,
                    "message": message,
                }
                self.errors_by_type[error_type].append(error_entry)
                self.errors_by_severity[severity] += 1

            def get_report(self) -> dict:
                """Generate error report."""
                runtime = (datetime.now() - self.start_time).total_seconds()

                return {
                    "runtime_seconds": runtime,
                    "total_errors": sum(len(errors) for errors in self.errors_by_type.values()),
                    "errors_by_type": {
                        error_type: len(errors)
                        for error_type, errors in self.errors_by_type.items()
                    },
                    "errors_by_severity": dict(self.errors_by_severity),
                    "error_rate": len(self.errors_by_type) / max(runtime, 1),
                    "most_common_type": max(
                        self.errors_by_type.items(), key=lambda x: len(x[1]), default=(None, [])
                    )[0],
                }

        # Simulate error aggregation
        aggregator = ErrorAggregator()
        orchestrator = create_orchestrator()

        # Process multiple tasks
        tasks = [
            "Valid task 1",
            "",  # Will cause error
            "Valid task 2",
            "Another task with $invalid$ characters",
            "Final valid task",
        ]

        print("\n6. Processing batch of tasks:")
        for i, task in enumerate(tasks, 1):
            try:
                if not task:
                    raise TaskAnalysisError("Empty task")
                if "$" in task:
                    raise ValidationError("Invalid characters in task")

                analysis = orchestrator.analyze_task(task)
                print(f"  ✓ Task {i}: Success")

            except TaskAnalysisError as e:
                aggregator.record_error("TaskAnalysis", "ERROR", str(e))
                print(f"  ❌ Task {i}: Analysis error")

            except ValidationError as e:
                aggregator.record_error("Validation", "WARNING", str(e))
                print(f"  ⚠️  Task {i}: Validation warning")

            except Exception as e:
                aggregator.record_error("Unknown", "CRITICAL", str(e))
                print(f"  ❌ Task {i}: Critical error")

        # Generate report
        report = aggregator.get_report()
        print("\n📊 Error Report:")
        print(f"  - Total tasks processed: {len(tasks)}")
        print(f"  - Total errors: {report['total_errors']}")
        print(f"  - Error rate: {report['error_rate']:.2f} errors/second")
        print(f"  - Most common error type: {report['most_common_type']}")
        print(f"  - Severity breakdown: {report['errors_by_severity']}")


def main():
    """Run all error handling examples."""
    print("\n⚠️  AI Task Orchestrator - Error Handling Examples")
    print("==================================================")

    examples = ErrorHandlingExamples()

    # Run examples
    examples.example_configuration_errors()
    examples.example_memory_degradation()
    examples.example_validation_errors()
    examples.example_retry_mechanism()
    examples.example_custom_error_handlers()
    examples.example_error_aggregation()

    print("\n\n✅ Error handling examples completed!")
    print("\nKey Patterns Demonstrated:")
    print("  - Graceful configuration error handling")
    print("  - Fallback when optional systems unavailable")
    print("  - Detailed validation error feedback")
    print("  - Retry logic with exponential backoff")
    print("  - Custom error handlers with recovery")
    print("  - Error aggregation and reporting")
    print("\nBest Practices:")
    print("  - Always provide fallback options")
    print("  - Give users actionable error messages")
    print("  - Log errors for debugging")
    print("  - Implement retry for transient failures")
    print("  - Monitor error rates and patterns")


if __name__ == "__main__":
    main()
