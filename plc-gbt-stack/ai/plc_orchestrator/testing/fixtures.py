"""Test fixtures and factories for the orchestrator."""

import random
import string
from typing import Any
from unittest.mock import AsyncMock, MagicMock

from plc_orchestrator import AITaskOrchestrator, create_orchestrator
from plc_orchestrator.memory.coordinator import MemoryCoordinator
from plc_orchestrator.utils.data_models import (
    TaskAnalysis,
    ValidationResult,
)
from plc_orchestrator.utils.enums import (
    ControlSystemComplexity,
    TaskComplexity,
    ValidationSeverity,
    ValidationTier,
)


class OrchestratorFixtures:
    """Common test fixtures for orchestrator testing."""

    # Sample task descriptions
    TASKS = {
        "simple": [
            "Create a function to add two numbers",
            "Write a hello world program",
            "Parse a JSON string",
            "Format a date string",
            "Calculate the area of a circle",
        ],
        "moderate": [
            "Build a REST API endpoint with validation",
            "Create a class with inheritance",
            "Implement a binary search algorithm",
            "Design a simple cache with TTL",
            "Parse CSV with error handling",
        ],
        "complex": [
            "Design a distributed task queue system",
            "Implement OAuth2 authentication flow",
            "Build a real-time chat application",
            "Create a machine learning pipeline",
            "Design microservices architecture",
        ],
        "control_system": [
            "Implement PID controller for temperature",
            "Design cascade control for distillation",
            "Create safety interlock system",
            "Build SCADA interface for monitoring",
            "Implement feedforward control",
        ],
    }

    # Sample code snippets
    CODE_SAMPLES = {
        "valid_simple": '''
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b
''',
        "valid_complex": '''
import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class Task:
    """Represents a task in the queue."""
    id: str
    payload: Dict[str, Any]
    priority: int = 0
    
class DistributedTaskQueue:
    """A distributed task queue implementation."""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.workers: List[asyncio.Task] = []
        
    async def enqueue(self, task: Task) -> str:
        """Add a task to the queue."""
        # Implementation here
        return task.id
        
    async def process(self) -> None:
        """Process tasks from the queue."""
        while True:
            task = await self._get_next_task()
            if task:
                await self._process_task(task)
''',
        "invalid_syntax": """
def broken_function(
    # Missing closing parenthesis
    return "broken"
""",
        "missing_requirements": """
def incomplete():
    pass
""",
    }

    # Sample requirements
    REQUIREMENTS = {
        "basic": [
            "Function must have type hints",
            "Include error handling",
            "Add documentation",
        ],
        "api": [
            "Validate input parameters",
            "Return JSON response",
            "Handle authentication",
            "Include rate limiting",
            "Log all requests",
        ],
        "control": [
            "Implement PID algorithm",
            "Include anti-windup",
            "Add safety limits",
            "Support manual override",
            "Log control actions",
        ],
    }


class TaskFactory:
    """Factory for creating test TaskAnalysis objects."""

    @staticmethod
    def create(
        task_id: str | None = None,
        description: str | None = None,
        complexity: str | None = None,
        requirements: list[str] | None = None,
        is_control_system: bool = False,
        requires_math: bool = False,
        **kwargs,
    ) -> TaskAnalysis:
        """
        Create a TaskAnalysis object for testing.

        Args:
            task_id: Task identifier
            description: Task description
            complexity: Task complexity level
            requirements: List of requirements
            is_control_system: Whether it's a control system task
            requires_math: Whether it requires math validation
            **kwargs: Additional fields

        Returns:
            TaskAnalysis object
        """
        # Generate defaults
        if task_id is None:
            task_id = f"test_{TaskFactory._random_id()}"

        if description is None:
            description = random.choice(OrchestratorFixtures.TASKS["moderate"])

        if complexity is None:
            complexity = random.choice([c.value for c in TaskComplexity])

        if requirements is None:
            requirements = OrchestratorFixtures.REQUIREMENTS["basic"].copy()

        # Build execution plan
        num_steps = {"simple": 3, "moderate": 5, "complex": 8, "extensive": 12}.get(complexity, 5)
        execution_plan = [
            {
                "step": i + 1,
                "name": f"Step {i + 1}",
                "description": f"Execute step {i + 1} of the plan",
                "estimated_time": random.randint(10, 60),
            }
            for i in range(num_steps)
        ]

        # Build control analysis if needed
        control_analysis = None
        if is_control_system:
            control_analysis = {
                "type": random.choice(["PID", "Cascade", "Feedforward", "MPC"]),
                "complexity": random.choice([c.value for c in ControlSystemComplexity]),
                "safety_critical": random.choice([True, False]),
                "requires_simulation": True,
            }

        # Create object
        return TaskAnalysis(
            task_id=task_id,
            description=description,
            complexity=complexity,
            requirements=requirements,
            risks=kwargs.get("risks", ["Risk 1", "Risk 2"]),
            dependencies=kwargs.get("dependencies", []),
            estimated_effort=kwargs.get("estimated_effort", {"hours": 4, "confidence": 0.8}),
            execution_plan=execution_plan,
            domain_tags=kwargs.get("domain_tags", ["testing", "example"]),
            is_control_system=is_control_system,
            requires_math_validation=requires_math,
            memory_insights=kwargs.get("memory_insights"),
            control_analysis=control_analysis,
        )

    @staticmethod
    def create_batch(count: int, **kwargs) -> list[TaskAnalysis]:
        """Create multiple TaskAnalysis objects."""
        return [TaskFactory.create(**kwargs) for _ in range(count)]

    @staticmethod
    def _random_id(length: int = 8) -> str:
        """Generate random ID."""
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


class ValidationFactory:
    """Factory for creating test ValidationResult objects."""

    @staticmethod
    def create(
        passed: bool | None = None,
        score: float | None = None,
        tier: str | None = None,
        issues: list[dict[str, Any]] | None = None,
        **kwargs,
    ) -> ValidationResult:
        """
        Create a ValidationResult object for testing.

        Args:
            passed: Whether validation passed
            score: Validation score (0-100)
            tier: Validation tier
            issues: List of validation issues
            **kwargs: Additional fields

        Returns:
            ValidationResult object
        """
        if passed is None:
            passed = random.choice([True, False])

        if score is None:
            score = random.uniform(70, 100) if passed else random.uniform(0, 69)

        if tier is None:
            tier = random.choice([t.value for t in ValidationTier])

        if issues is None and not passed:
            # Generate some issues
            severities = [s.value for s in ValidationSeverity]
            issues = [
                {
                    "type": random.choice(["syntax", "requirements", "style", "security"]),
                    "severity": random.choice(severities),
                    "message": f"Issue {i + 1}: Description of the problem",
                    "line": random.randint(1, 100),
                }
                for i in range(random.randint(1, 5))
            ]
        elif issues is None:
            issues = []

        return ValidationResult(
            passed=passed,
            score=score,
            validation_tier=tier,
            issues=issues,
            recommendations=kwargs.get("recommendations", []),
            metadata=kwargs.get("metadata", {}),
        )

    @staticmethod
    def create_passing(score: float = 95.0, **kwargs) -> ValidationResult:
        """Create a passing validation result."""
        kwargs["passed"] = True
        kwargs["score"] = score
        kwargs.setdefault("issues", [])
        return ValidationFactory.create(**kwargs)

    @staticmethod
    def create_failing(score: float = 45.0, issue_count: int = 3, **kwargs) -> ValidationResult:
        """Create a failing validation result."""
        kwargs["passed"] = False
        kwargs["score"] = score

        # Generate issues
        issues = []
        for i in range(issue_count):
            issues.append(
                {
                    "type": "requirements",
                    "severity": ValidationSeverity.HIGH.value,
                    "message": f"Missing requirement {i + 1}",
                    "line": None,
                }
            )

        kwargs["issues"] = issues
        return ValidationFactory.create(**kwargs)


def create_test_orchestrator(**config_overrides) -> AITaskOrchestrator:
    """
    Create an orchestrator configured for testing.

    Args:
        **config_overrides: Configuration overrides

    Returns:
        Configured orchestrator for testing
    """
    # Default test configuration
    test_config = {
        "environment": "test",
        "enable_memory": False,
        "enable_production_checks": False,
        "enable_math_validation": False,
        "timeout_seconds": 10,
        "max_workers": 1,
    }

    # Apply overrides
    test_config.update(config_overrides)

    # Create orchestrator
    return create_orchestrator(**test_config)


def mock_memory_coordinator() -> MemoryCoordinator:
    """
    Create a mock memory coordinator for testing.

    Returns:
        Mocked MemoryCoordinator
    """
    mock = MagicMock(spec=MemoryCoordinator)

    # Mock async methods
    mock.initialize_all_connections = AsyncMock()
    mock.close_all_connections = AsyncMock()
    mock.query_memory = AsyncMock(
        return_value=MagicMock(success=True, data={"results": [], "count": 0})
    )
    mock.store_memory = AsyncMock(return_value=True)

    return mock


class TestDataGenerator:
    """Generate test data for various scenarios."""

    @staticmethod
    def generate_code(
        lines: int = 50,
        include_imports: bool = True,
        include_class: bool = False,
        include_errors: bool = False,
    ) -> str:
        """Generate Python code for testing."""
        code_lines = []

        # Imports
        if include_imports:
            code_lines.extend(
                [
                    "import asyncio",
                    "from typing import Dict, List, Optional",
                    "from dataclasses import dataclass",
                    "",
                ]
            )

        # Class definition
        if include_class:
            code_lines.extend(
                [
                    "@dataclass",
                    "class TestClass:",
                    '    """Test class for validation."""',
                    "    name: str",
                    "    value: int = 0",
                    "",
                ]
            )

        # Functions
        num_functions = max(1, lines // 10)
        for i in range(num_functions):
            if include_errors and i == 0:
                # Intentional syntax error
                code_lines.extend(
                    [
                        f"def function_{i}(",
                        "    # Missing closing parenthesis",
                        "    pass",
                    ]
                )
            else:
                code_lines.extend(
                    [
                        f"def function_{i}(x: int) -> int:",
                        f'    """Function {i} docstring."""',
                        f"    return x * {i + 1}",
                        "",
                    ]
                )

        # Pad to requested lines
        while len(code_lines) < lines:
            code_lines.append("# Comment line")

        return "\n".join(code_lines[:lines])

    @staticmethod
    def generate_requirements(count: int = 5, domain: str = "general") -> list[str]:
        """Generate test requirements."""
        templates = {
            "general": [
                "Implement {feature} with error handling",
                "Add type hints to all functions",
                "Include comprehensive documentation",
                "Write unit tests with {coverage}% coverage",
                "Follow {standard} coding standards",
            ],
            "api": [
                "Implement REST endpoint for {resource}",
                "Add authentication using {method}",
                "Validate all input parameters",
                "Return appropriate HTTP status codes",
                "Include rate limiting",
            ],
            "control": [
                "Implement {algorithm} control algorithm",
                "Add safety interlocks for {parameter}",
                "Include manual override capability",
                "Log all control actions",
                "Support {protocol} communication",
            ],
        }

        template_list = templates.get(domain, templates["general"])
        requirements = []

        for i in range(count):
            template = random.choice(template_list)
            # Fill in placeholders
            requirement = template.format(
                feature=f"feature_{i}",
                coverage=random.randint(80, 95),
                standard="PEP8",
                resource=f"resource_{i}",
                method="JWT",
                algorithm="PID",
                parameter=f"param_{i}",
                protocol="Modbus",
            )
            requirements.append(requirement)

        return requirements
