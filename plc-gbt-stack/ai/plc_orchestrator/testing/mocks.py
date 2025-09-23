"""Mock implementations for testing."""

import asyncio
from typing import Any
from unittest.mock import MagicMock

from plc_orchestrator.memory import MemoryRequest, MemoryResponse
from plc_orchestrator.testing.fixtures import TaskFactory, ValidationFactory
from plc_orchestrator.utils.data_models import TaskAnalysis, ValidationResult
from plc_orchestrator.utils.enums import TaskComplexity


class MockMemoryAdapter:
    """Mock memory adapter for testing."""

    def __init__(self, data: list[dict[str, Any]] | None = None):
        """
        Initialize mock adapter.

        Args:
            data: Initial data to return from queries
        """
        self.data = data or []
        self.stored_items = []
        self.query_count = 0
        self.store_count = 0
        self.connected = False

    async def connect(self) -> None:
        """Mock connection."""
        await asyncio.sleep(0.01)  # Simulate connection time
        self.connected = True

    async def disconnect(self) -> None:
        """Mock disconnection."""
        self.connected = False

    async def query(self, request: MemoryRequest) -> MemoryResponse:
        """Mock query operation."""
        self.query_count += 1

        # Simulate query delay
        await asyncio.sleep(0.05)

        # Filter data based on request
        results = self.data
        if request.query and "description" in request.query:
            search_term = request.query["description"].lower()
            results = [
                item for item in self.data if search_term in item.get("description", "").lower()
            ]

        return MemoryResponse(
            success=True,
            data={"results": results, "count": len(results)},
            metadata={"source": "mock"},
        )

    async def store(self, data: Any, metadata: dict[str, Any] | None = None) -> bool:
        """Mock store operation."""
        self.store_count += 1

        # Simulate store delay
        await asyncio.sleep(0.02)

        # Store item
        item = {"data": data, "metadata": metadata}
        self.stored_items.append(item)
        self.data.append(data)

        return True

    def reset(self):
        """Reset mock state."""
        self.data.clear()
        self.stored_items.clear()
        self.query_count = 0
        self.store_count = 0


class MockTaskAnalyzer:
    """Mock task analyzer for testing."""

    def __init__(self, default_complexity: str = TaskComplexity.MODERATE.value):
        """
        Initialize mock analyzer.

        Args:
            default_complexity: Default complexity to return
        """
        self.default_complexity = default_complexity
        self.analyzed_tasks = []
        self.custom_responses = {}

    def analyze_task(self, description: str) -> TaskAnalysis:
        """Mock task analysis."""
        self.analyzed_tasks.append(description)

        # Check for custom response
        if description in self.custom_responses:
            return self.custom_responses[description]

        # Generate default response
        complexity = self._determine_complexity(description)
        return TaskFactory.create(
            description=description,
            complexity=complexity,
            requirements=self._generate_requirements(description),
            is_control_system="control" in description.lower() or "pid" in description.lower(),
        )

    def set_custom_response(self, description: str, analysis: TaskAnalysis):
        """Set custom response for specific description."""
        self.custom_responses[description] = analysis

    def _determine_complexity(self, description: str) -> str:
        """Determine complexity based on description."""
        desc_lower = description.lower()

        if any(word in desc_lower for word in ["simple", "basic", "hello"]):
            return TaskComplexity.SIMPLE.value
        elif any(word in desc_lower for word in ["complex", "distributed", "architecture"]):
            return TaskComplexity.COMPLEX.value
        elif any(word in desc_lower for word in ["extensive", "enterprise", "large-scale"]):
            return TaskComplexity.EXTENSIVE.value
        else:
            return self.default_complexity

    def _generate_requirements(self, description: str) -> list[str]:
        """Generate requirements based on description."""
        requirements = ["Basic implementation"]

        if "error" in description.lower():
            requirements.append("Error handling")
        if "test" in description.lower():
            requirements.append("Unit tests")
        if "api" in description.lower():
            requirements.extend(["Input validation", "Authentication"])
        if "async" in description.lower():
            requirements.append("Async/await support")

        return requirements


class MockValidator:
    """Mock validator for testing."""

    def __init__(self, default_pass: bool = True, default_score: float = 85.0):
        """
        Initialize mock validator.

        Args:
            default_pass: Default pass/fail status
            default_score: Default validation score
        """
        self.default_pass = default_pass
        self.default_score = default_score
        self.validated_code = []
        self.custom_responses = {}

    def validate_implementation(
        self, code: str, requirements: list[str], validation_tier: str | None = None
    ) -> ValidationResult:
        """Mock validation."""
        self.validated_code.append((code, requirements, validation_tier))

        # Check for custom response
        code_key = code[:50]  # Use first 50 chars as key
        if code_key in self.custom_responses:
            return self.custom_responses[code_key]

        # Generate validation result
        if not code or "syntax error" in code.lower():
            return ValidationFactory.create_failing(score=0.0, issue_count=1)

        # Check requirements
        missing_requirements = []
        if "error handling" in " ".join(requirements).lower() and "try" not in code:
            missing_requirements.append("Error handling")
        if "type hints" in " ".join(requirements).lower() and "->" not in code:
            missing_requirements.append("Type hints")

        if missing_requirements:
            return ValidationFactory.create_failing(
                score=self.default_score - 20, issue_count=len(missing_requirements)
            )

        return ValidationFactory.create_passing(score=self.default_score)

    def set_custom_response(self, code_prefix: str, result: ValidationResult):
        """Set custom response for code starting with prefix."""
        self.custom_responses[code_prefix[:50]] = result


class MockWolframClient:
    """Mock WolframAlpha client for testing."""

    def __init__(self, available: bool = True):
        """
        Initialize mock client.

        Args:
            available: Whether the service is available
        """
        self.available = available
        self.queries = []
        self.responses = {
            "derivative of x^2": "2*x",
            "integral of sin(x)": "-cos(x) + C",
            "solve x^2 + 2*x + 1 = 0": "x = -1",
        }

    async def query(self, expression: str) -> dict[str, Any]:
        """Mock WolframAlpha query."""
        if not self.available:
            raise ConnectionError("WolframAlpha service unavailable")

        self.queries.append(expression)

        # Simulate API delay
        await asyncio.sleep(0.1)

        # Check for known response
        result = self.responses.get(expression.lower(), f"Result for: {expression}")

        return {
            "success": True,
            "result": result,
            "pods": [
                {"title": "Input", "text": expression},
                {"title": "Result", "text": result},
            ],
        }

    def add_response(self, expression: str, result: str):
        """Add custom response for expression."""
        self.responses[expression.lower()] = result


class MockProgressMonitor:
    """Mock progress monitor for testing."""

    def __init__(self):
        """Initialize mock monitor."""
        self.steps = []
        self.completed_steps = []
        self.failed_steps = []
        self.callbacks = []

    def set_total_steps(self, total: int):
        """Set total steps."""
        self.total_steps = total

    def start_step(self, step_number: int, step_name: str, details: dict[str, Any] | None = None):
        """Start a step."""
        step = {
            "number": step_number,
            "name": step_name,
            "details": details,
            "start_time": asyncio.get_event_loop().time(),
        }
        self.steps.append(step)

        # Notify callbacks
        for callback in self.callbacks:
            callback("step_started", step)

    def complete_step(self, step_number: int, result: dict[str, Any] | None = None):
        """Complete a step."""
        self.completed_steps.append(
            {
                "number": step_number,
                "result": result,
                "end_time": asyncio.get_event_loop().time(),
            }
        )

        # Notify callbacks
        for callback in self.callbacks:
            callback("step_completed", {"number": step_number, "result": result})

    def fail_step(self, step_number: int, error: str):
        """Fail a step."""
        self.failed_steps.append(
            {
                "number": step_number,
                "error": error,
            }
        )

        # Notify callbacks
        for callback in self.callbacks:
            callback("step_failed", {"number": step_number, "error": error})

    def add_progress_callback(self, callback):
        """Add progress callback."""
        self.callbacks.append(callback)

    def get_percentage(self) -> float:
        """Get completion percentage."""
        if not hasattr(self, "total_steps") or self.total_steps == 0:
            return 0.0
        return len(self.completed_steps) / self.total_steps * 100


def create_mock_orchestrator(**config):
    """
    Create a fully mocked orchestrator for testing.

    Args:
        **config: Configuration options

    Returns:
        Mock orchestrator with all dependencies mocked
    """
    orchestrator = MagicMock()

    # Mock analyzer
    orchestrator.analyzer = MockTaskAnalyzer(
        default_complexity=config.get("default_complexity", TaskComplexity.MODERATE.value)
    )

    # Mock validator
    orchestrator.validator = MockValidator(
        default_pass=config.get("default_validation_pass", True),
        default_score=config.get("default_validation_score", 85.0),
    )

    # Mock memory coordinator
    orchestrator.memory_coordinator = MockMemoryAdapter(data=config.get("memory_data", []))

    # Mock progress monitor
    orchestrator.progress_monitor = MockProgressMonitor()

    # Wire up main methods
    orchestrator.analyze_task = orchestrator.analyzer.analyze_task
    orchestrator.validate_implementation = orchestrator.validator.validate_implementation

    # Mock other methods
    orchestrator.create_implementation_guide = MagicMock(return_value="/tmp/guide_test.md")
    orchestrator.get_production_checklist = MagicMock(
        return_value=MagicMock(overall_readiness=True, checks=[])
    )
    orchestrator.create_summary_document = MagicMock(return_value="/tmp/summary_test.md")

    return orchestrator
