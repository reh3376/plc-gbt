"""Custom exceptions and error handling for the PLC Task Orchestrator."""

from typing import Any


class OrchestratorError(Exception):
    """Base exception for all orchestrator errors."""

    def __init__(
        self, message: str, code: str = "ORCHESTRATOR_ERROR", details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ConfigurationError(OrchestratorError):
    """Raised when there's a configuration issue."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message=message, code="CONFIGURATION_ERROR", details=details)


class ValidationError(OrchestratorError):
    """Raised when validation fails."""

    def __init__(
        self,
        message: str,
        validation_tier: str,
        issues: list[dict[str, Any]],
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"validation_tier": validation_tier, "issues": issues, **(details or {})},
        )
        self.validation_tier = validation_tier
        self.issues = issues


class MemorySystemError(OrchestratorError):
    """Raised when memory system operations fail."""

    def __init__(
        self,
        message: str,
        database: str | None = None,
        operation: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="MEMORY_SYSTEM_ERROR",
            details={"database": database, "operation": operation, **(details or {})},
        )
        self.database = database
        self.operation = operation


class TaskAnalysisError(OrchestratorError):
    """Raised when task analysis fails."""

    def __init__(
        self, message: str, task_description: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code="TASK_ANALYSIS_ERROR",
            details={"task_description": task_description, **(details or {})},
        )


class ExecutionError(OrchestratorError):
    """Raised when task execution fails."""

    def __init__(
        self, message: str, step_name: str, task_id: str, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code="EXECUTION_ERROR",
            details={"step_name": step_name, "task_id": task_id, **(details or {})},
        )
        self.step_name = step_name
        self.task_id = task_id


class DependencyError(OrchestratorError):
    """Raised when required dependencies are not available."""

    def __init__(
        self, message: str, missing_dependencies: list[str], details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code="DEPENDENCY_ERROR",
            details={"missing_dependencies": missing_dependencies, **(details or {})},
        )
        self.missing_dependencies = missing_dependencies


class TimeoutError(OrchestratorError):
    """Raised when an operation times out."""

    def __init__(
        self,
        message: str,
        operation: str,
        timeout_seconds: float,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            code="TIMEOUT_ERROR",
            details={"operation": operation, "timeout_seconds": timeout_seconds, **(details or {})},
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class PluginError(OrchestratorError):
    """Raised when plugin operations fail."""

    def __init__(
        self, message: str, plugin_name: str | None = None, details: dict[str, Any] | None = None
    ) -> None:
        super().__init__(
            message=message,
            code="PLUGIN_ERROR",
            details={"plugin_name": plugin_name, **(details or {})},
        )
        self.plugin_name = plugin_name
