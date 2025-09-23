"""Data models and structures for the PLC Task Orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from plc_orchestrator.utils.enums import (
    ControlSystemComplexity,
    ValidationSeverity,
    ValidationTier,
)


@dataclass
class TaskProgressUpdate:
    """Real-time task progress update"""

    task_id: str
    current_step: int
    total_steps: int
    percentage: float
    status: str
    elapsed_time: float
    details: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ExecutionStep:
    """Individual execution step tracking with enhanced monitoring"""

    name: str
    description: str
    status: str = "pending"
    start_time: datetime | None = None
    end_time: datetime | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    artifacts: list[Path] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize timestamps and ensure artifacts is a list."""
        if self.start_time is None and self.status == "in_progress":
            self.start_time = datetime.now()
        if isinstance(self.artifacts, (str, Path)):
            self.artifacts = [Path(self.artifacts)]

    @property
    def duration(self) -> float | None:
        """Calculate step duration in seconds."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


@dataclass
class TaskAnalysis:
    """Complete task analysis result"""

    task_id: str
    description: str
    complexity: str
    requirements: list[str]
    risks: list[str]
    dependencies: list[str]
    estimated_effort: dict[str, Any]
    execution_plan: list[dict[str, Any]]
    validation_criteria: list[str]
    resources: dict[str, Any] = field(default_factory=dict)
    control_analysis: dict[str, Any] | None = None
    memory_insights: dict[str, Any] | None = None
    similar_implementations: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_control_system_task(self) -> bool:
        """Check if this is a control system related task."""
        return self.control_analysis is not None

    def requires_mathematical_validation(self) -> bool:
        """Check if mathematical validation is required."""
        return any("math" in req.lower() or "equation" in req.lower() for req in self.requirements)


@dataclass
class ValidationResult:
    """Comprehensive validation result"""

    passed: bool
    score: float
    tier: ValidationTier
    issues: list[dict[str, Any]]
    recommendations: list[str]
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def get_critical_issues(self) -> list[dict[str, Any]]:
        """Get only critical severity issues."""
        return [
            issue
            for issue in self.issues
            if issue.get("severity") == ValidationSeverity.CRITICAL.value
        ]

    def get_issues_by_severity(self, severity: ValidationSeverity) -> list[dict[str, Any]]:
        """Get issues filtered by severity level."""
        return [issue for issue in self.issues if issue.get("severity") == severity.value]


@dataclass
class MemoryInsight:
    """Insight retrieved from memory system"""

    source: str  # Which database it came from
    content: Any
    relevance_score: float
    metadata: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ControlSystemAnalysis:
    """Control system specific analysis result"""

    complexity: ControlSystemComplexity
    control_type: str
    safety_requirements: list[str]
    performance_targets: dict[str, Any]
    recommended_algorithms: list[str]
    validation_methods: list[str]
    implementation_risks: list[str]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentChecklist:
    """Production deployment checklist"""

    task_id: str
    environment_checks: list[dict[str, bool]]
    dependency_checks: list[dict[str, bool]]
    security_checks: list[dict[str, bool]]
    performance_checks: list[dict[str, bool]]
    documentation_checks: list[dict[str, bool]]
    overall_readiness: bool
    blocking_issues: list[str]
    recommendations: list[str]

    def get_failed_checks(self) -> list[dict[str, Any]]:
        """Get all failed checklist items."""
        failed = []
        for category in ["environment", "dependency", "security", "performance", "documentation"]:
            checks = getattr(self, f"{category}_checks", [])
            failed.extend(
                [{**check, "category": category} for check in checks if not list(check.values())[0]]
            )
        return failed
