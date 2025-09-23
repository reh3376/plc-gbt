#!/usr/bin/env python3
"""
Testing patterns and examples for the AI Task Orchestrator.

This example demonstrates:
1. Unit testing with mocks
2. Integration testing patterns
3. Test fixtures and factories
4. Property-based testing
5. Performance testing
"""

import time
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

from plc_orchestrator import create_orchestrator
from plc_orchestrator.core.analyzer import TaskAnalyzer
from plc_orchestrator.utils.data_models import TaskAnalysis, ValidationResult
from plc_orchestrator.utils.enums import TaskComplexity


# Test Fixtures
@dataclass
class TestFixtures:
    """Common test fixtures."""

    @staticmethod
    def simple_task() -> str:
        """Simple task description."""
        return "Create a function to add two numbers"

    @staticmethod
    def complex_task() -> str:
        """Complex task description."""
        return """
        Implement a distributed caching system with:
        - Redis cluster support
        - Consistent hashing
        - Automatic failover
        - Monitoring and metrics
        - Rate limiting
        """

    @staticmethod
    def valid_code() -> str:
        """Valid Python code."""
        return '''
def add(a: int, b: int) -> int:
    """Add two numbers."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Both arguments must be integers")
    return a + b
'''

    @staticmethod
    def invalid_code() -> str:
        """Invalid Python code with issues."""
        return """
def add(a, b):
    # Missing type hints and docstring
    return a + b
"""

    @staticmethod
    def task_analysis_factory(
        task_id: str = "test_001",
        complexity: str = TaskComplexity.SIMPLE.value,
        requirements: list[str] = None,
    ) -> TaskAnalysis:
        """Factory for TaskAnalysis objects."""
        return TaskAnalysis(
            task_id=task_id,
            description="Test task",
            complexity=complexity,
            requirements=requirements or ["requirement1", "requirement2"],
            risks=["risk1"],
            dependencies=[],
            estimated_effort={"hours": 2, "confidence": 0.8},
            execution_plan=[{"step": 1, "name": "Step 1", "description": "Do something"}],
            domain_tags=["testing"],
            is_control_system=False,
            requires_math_validation=False,
            memory_insights=None,
            control_analysis=None,
        )


class TestingExamples:
    """Examples of testing patterns."""

    def example_unit_tests(self):
        """Example: Unit testing with mocks."""
        print("\n" + "=" * 60)
        print("Example 1: Unit Testing with Mocks")
        print("=" * 60)

        # Test 1: Mock the analyzer
        print("\n1a. Testing TaskAnalyzer with mocks:")

        with patch(
            "plc_orchestrator.core.analyzer.TaskAnalyzer.extract_requirements"
        ) as mock_extract:
            # Setup mock
            mock_extract.return_value = ["mocked_requirement_1", "mocked_requirement_2"]

            # Create analyzer and test
            analyzer = TaskAnalyzer()
            requirements = analyzer.extract_requirements("Any task description")

            print(f"  ✓ Mocked requirements: {requirements}")
            print(f"  ✓ Mock called: {mock_extract.called}")
            print(f"  ✓ Call count: {mock_extract.call_count}")

        # Test 2: Mock external dependencies
        print("\n1b. Mocking external dependencies:")

        with patch("plc_orchestrator.memory.coordinator.MemoryCoordinator") as MockMemory:
            # Setup mock memory coordinator
            mock_memory = MockMemory.return_value
            mock_memory.query_memory = AsyncMock(
                return_value=MagicMock(success=True, data={"similar_tasks": ["task1", "task2"]})
            )

            # Create orchestrator with mocked memory
            orchestrator = create_orchestrator(enable_memory=True)

            # Inject mock (in real tests, use dependency injection)
            if hasattr(orchestrator, "memory_coordinator"):
                orchestrator.memory_coordinator = mock_memory

            print("  ✓ Created orchestrator with mocked memory")
            print("  ✓ Mock memory ready for testing")

    def example_integration_tests(self):
        """Example: Integration testing patterns."""
        print("\n" + "=" * 60)
        print("Example 2: Integration Testing")
        print("=" * 60)

        # Test the full workflow
        print("\n2. Testing complete workflow:")

        orchestrator = create_orchestrator(enable_memory=False)
        fixtures = TestFixtures()

        # Step 1: Analyze
        print("  Step 1: Analyzing task...")
        analysis = orchestrator.analyze_task(fixtures.simple_task())
        assert analysis.task_id is not None
        assert analysis.complexity in [c.value for c in TaskComplexity]
        print(f"    ✓ Analysis complete: {analysis.complexity}")

        # Step 2: Create guide
        print("  Step 2: Creating guide...")
        guide_path = orchestrator.create_implementation_guide(analysis)
        assert guide_path.exists()
        print(f"    ✓ Guide created: {guide_path.name}")

        # Step 3: Validate
        print("  Step 3: Validating code...")
        validation = orchestrator.validate_implementation(
            fixtures.valid_code(), analysis.requirements
        )
        assert isinstance(validation.score, (int, float))
        print(f"    ✓ Validation complete: {validation.score}/100")

        # Step 4: Production check
        print("  Step 4: Production checklist...")
        checklist = orchestrator.get_production_checklist(fixtures.valid_code())
        assert hasattr(checklist, "overall_readiness")
        print(f"    ✓ Production ready: {checklist.overall_readiness}")

        print("\n  ✅ Full integration test passed!")

    def example_test_factories(self):
        """Example: Using test factories and builders."""
        print("\n" + "=" * 60)
        print("Example 3: Test Factories and Builders")
        print("=" * 60)

        class TaskAnalysisBuilder:
            """Builder for test TaskAnalysis objects."""

            def __init__(self):
                self.analysis = TestFixtures.task_analysis_factory()

            def with_complexity(self, complexity: str):
                self.analysis.complexity = complexity
                return self

            def with_requirements(self, requirements: list[str]):
                self.analysis.requirements = requirements
                return self

            def with_control_system(self):
                self.analysis.is_control_system = True
                self.analysis.control_analysis = {
                    "type": "PID",
                    "complexity": "moderate",
                    "safety_critical": True,
                }
                return self

            def build(self) -> TaskAnalysis:
                return self.analysis

        # Example usage
        print("\n3. Building test objects:")

        # Simple task
        simple_analysis = (
            TaskAnalysisBuilder()
            .with_complexity(TaskComplexity.SIMPLE.value)
            .with_requirements(["add function", "type hints"])
            .build()
        )
        print(f"  ✓ Built simple task: {simple_analysis.complexity}")

        # Complex control system task
        control_analysis = (
            TaskAnalysisBuilder()
            .with_complexity(TaskComplexity.COMPLEX.value)
            .with_requirements(["PID control", "safety checks"])
            .with_control_system()
            .build()
        )
        print(f"  ✓ Built control task: {control_analysis.control_analysis['type']}")

    def example_property_testing(self):
        """Example: Property-based testing patterns."""
        print("\n" + "=" * 60)
        print("Example 4: Property-Based Testing")
        print("=" * 60)

        import random

        def generate_random_task(min_length: int = 10, max_length: int = 500) -> str:
            """Generate random task description."""
            words = [
                "create",
                "implement",
                "build",
                "design",
                "develop",
                "function",
                "class",
                "API",
                "system",
                "module",
                "with",
                "for",
                "that",
                "includes",
                "supports",
            ]

            length = random.randint(min_length, max_length)
            task_words = []

            for _ in range(length // 10):  # Approximate word count
                task_words.append(random.choice(words))

            return " ".join(task_words)

        # Property tests
        print("\n4. Testing properties:")
        orchestrator = create_orchestrator()

        # Property 1: All tasks should have valid complexity
        print("  Property 1: Valid complexity for all tasks")
        valid_complexities = [c.value for c in TaskComplexity]

        for i in range(5):
            task = generate_random_task()
            analysis = orchestrator.analyze_task(task)
            assert analysis.complexity in valid_complexities
            print(f"    ✓ Test {i + 1}: {analysis.complexity}")

        # Property 2: Longer tasks tend to be more complex
        print("\n  Property 2: Task length correlates with complexity")
        short_tasks = [generate_random_task(10, 50) for _ in range(3)]
        long_tasks = [generate_random_task(300, 500) for _ in range(3)]

        short_complexities = [orchestrator.analyze_task(t).complexity for t in short_tasks]
        long_complexities = [orchestrator.analyze_task(t).complexity for t in long_tasks]

        print(f"    Short tasks: {short_complexities}")
        print(f"    Long tasks: {long_complexities}")

        # Property 3: Validation should never crash
        print("\n  Property 3: Validation handles any input")
        random_codes = [
            "",  # Empty
            "not python code at all",  # Invalid
            "def f(): pass",  # Minimal valid
            '"""' * 100,  # Stress test
            "\n".join([f"x{i} = {i}" for i in range(100)]),  # Many variables
        ]

        for i, code in enumerate(random_codes):
            try:
                validation = orchestrator.validate_implementation(code, ["any requirement"])
                print(f"    ✓ Test {i + 1}: Handled (score: {validation.score})")
            except Exception as e:
                print(f"    ❌ Test {i + 1}: Failed with {type(e).__name__}")

    def example_performance_tests(self):
        """Example: Performance testing patterns."""
        print("\n" + "=" * 60)
        print("Example 5: Performance Testing")
        print("=" * 60)

        import statistics

        class PerformanceTester:
            """Performance testing utilities."""

            @staticmethod
            def measure_operation(operation: callable, iterations: int = 10) -> dict[str, float]:
                """Measure operation performance."""
                times = []

                for _ in range(iterations):
                    start = time.perf_counter()
                    operation()
                    end = time.perf_counter()
                    times.append(end - start)

                return {
                    "min": min(times),
                    "max": max(times),
                    "mean": statistics.mean(times),
                    "median": statistics.median(times),
                    "stdev": statistics.stdev(times) if len(times) > 1 else 0,
                }

        orchestrator = create_orchestrator(enable_memory=False)
        fixtures = TestFixtures()

        # Test 1: Task analysis performance
        print("\n5a. Task analysis performance:")

        def analyze_task():
            orchestrator.analyze_task(fixtures.simple_task())

        perf = PerformanceTester.measure_operation(analyze_task, iterations=5)
        print(f"  Mean time: {perf['mean']:.3f}s")
        print(f"  Min/Max: {perf['min']:.3f}s / {perf['max']:.3f}s")
        print(f"  Std Dev: {perf['stdev']:.3f}s")

        # Test 2: Validation performance
        print("\n5b. Validation performance:")

        def validate_code():
            orchestrator.validate_implementation(
                fixtures.valid_code(), ["requirement1", "requirement2"]
            )

        perf = PerformanceTester.measure_operation(validate_code, iterations=5)
        print(f"  Mean time: {perf['mean']:.3f}s")
        print(f"  Min/Max: {perf['min']:.3f}s / {perf['max']:.3f}s")

        # Test 3: Scalability test
        print("\n5c. Scalability test (increasing complexity):")

        task_sizes = [10, 50, 100, 500]
        for size in task_sizes:
            task = " ".join(["implement feature"] * size)

            start = time.perf_counter()
            analysis = orchestrator.analyze_task(task)
            elapsed = time.perf_counter() - start

            print(f"  Task size {size:3d}: {elapsed:.3f}s ({analysis.complexity})")

    def example_test_helpers(self):
        """Example: Custom test helpers and assertions."""
        print("\n" + "=" * 60)
        print("Example 6: Test Helpers and Custom Assertions")
        print("=" * 60)

        class OrchestratorTestHelpers:
            """Custom test helpers."""

            @staticmethod
            def assert_valid_analysis(analysis: TaskAnalysis):
                """Assert task analysis is valid."""
                assert analysis.task_id, "Task ID should not be empty"
                assert analysis.complexity in [c.value for c in TaskComplexity]
                assert len(analysis.requirements) > 0, "Should have requirements"
                assert len(analysis.execution_plan) > 0, "Should have execution plan"
                assert 0 <= analysis.estimated_effort["confidence"] <= 1

            @staticmethod
            def assert_validation_quality(validation: ValidationResult, min_score: int = 70):
                """Assert validation meets quality standards."""
                assert validation.score >= min_score, (
                    f"Score {validation.score} below minimum {min_score}"
                )

                # Check for critical issues
                critical_issues = [i for i in validation.issues if i.get("severity") == "CRITICAL"]
                assert len(critical_issues) == 0, f"Found {len(critical_issues)} critical issues"

            @staticmethod
            def create_test_context(**kwargs) -> dict[str, Any]:
                """Create test context with defaults."""
                defaults = {
                    "enable_memory": False,
                    "enable_production_checks": False,
                    "timeout_seconds": 30,
                    "environment": "test",
                }
                defaults.update(kwargs)
                return defaults

        # Use helpers
        print("\n6. Using test helpers:")

        helpers = OrchestratorTestHelpers()
        context = helpers.create_test_context(enable_production_checks=True)
        orchestrator = create_orchestrator(**context)

        # Test with helpers
        analysis = orchestrator.analyze_task("Create REST API")
        helpers.assert_valid_analysis(analysis)
        print("  ✓ Analysis validation passed")

        validation = orchestrator.validate_implementation(
            TestFixtures.valid_code(), analysis.requirements
        )
        helpers.assert_validation_quality(validation, min_score=80)
        print("  ✓ Validation quality passed")


def main():
    """Run all testing examples."""
    print("\n🧪 AI Task Orchestrator - Testing Patterns")
    print("==========================================")

    examples = TestingExamples()

    # Run examples
    examples.example_unit_tests()
    examples.example_integration_tests()
    examples.example_test_factories()
    examples.example_property_testing()
    examples.example_performance_tests()
    examples.example_test_helpers()

    print("\n\n✅ Testing examples completed!")
    print("\nKey Patterns Demonstrated:")
    print("  - Unit testing with mocks and patches")
    print("  - Integration testing full workflows")
    print("  - Test factories and builders")
    print("  - Property-based testing")
    print("  - Performance benchmarking")
    print("  - Custom test helpers and assertions")
    print("\nBest Practices:")
    print("  - Use mocks to isolate units")
    print("  - Test the full integration flow")
    print("  - Create reusable test fixtures")
    print("  - Test edge cases and properties")
    print("  - Monitor performance regressions")
    print("  - Build domain-specific test helpers")


if __name__ == "__main__":
    main()
