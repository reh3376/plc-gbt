"""
Example logging plugin.

Demonstrates how to create a plugin that hooks into task lifecycle.
"""

import time
from typing import Any

from plc_orchestrator.plugins.base import HookType, Plugin, PluginHook, PluginMetadata
from plc_orchestrator.utils.data_models import TaskAnalysis, ValidationResult


class EnhancedLoggingPlugin(Plugin):
    """Plugin that adds enhanced logging to task processing."""

    def __init__(self):
        """Initialize plugin."""
        self.orchestrator = None
        self.task_start_times: dict[str, float] = {}
        self.log_file = "orchestrator_tasks.log"

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="enhanced_logging",
            version="1.0.0",
            description="Adds detailed logging for task lifecycle events",
            author="AI Task Orchestrator Team",
            tags=["logging", "monitoring", "observability"],
        )

    def initialize(self, orchestrator: Any) -> None:
        """Initialize plugin with orchestrator."""
        self.orchestrator = orchestrator

        # Open log file
        with open(self.log_file, "a") as f:
            f.write(f"\n=== Enhanced Logging Plugin Started at {time.ctime()} ===\n")

    def get_hooks(self) -> list[PluginHook]:
        """Get plugin hooks."""
        return [
            PluginHook(
                hook_type=HookType.PRE_ANALYZE,
                callback=self.on_pre_analyze,
                priority=90,  # High priority to log early
            ),
            PluginHook(
                hook_type=HookType.POST_ANALYZE,
                callback=self.on_post_analyze,
                priority=10,  # Low priority to log after other plugins
            ),
            PluginHook(
                hook_type=HookType.PRE_VALIDATE,
                callback=self.on_pre_validate,
                priority=90,
            ),
            PluginHook(
                hook_type=HookType.POST_VALIDATE,
                callback=self.on_post_validate,
                priority=10,
            ),
            PluginHook(
                hook_type=HookType.ERROR_OCCURRED,
                callback=self.on_error,
                priority=100,  # Highest priority for errors
            ),
            PluginHook(
                hook_type=HookType.PROGRESS_UPDATE,
                callback=self.on_progress,
                priority=50,
            ),
        ]

    def on_pre_analyze(self, task_description: str) -> None:
        """Log before task analysis."""
        task_id = str(hash(task_description))[:8]
        self.task_start_times[task_id] = time.time()

        with open(self.log_file, "a") as f:
            f.write(f"\n[PRE-ANALYZE] Task ID: {task_id}\n")
            f.write(f"Description: {task_description[:100]}...\n")
            f.write(f"Timestamp: {time.ctime()}\n")

    def on_post_analyze(self, task_description: str, analysis: TaskAnalysis) -> None:
        """Log after task analysis."""
        task_id = str(hash(task_description))[:8]
        duration = time.time() - self.task_start_times.get(task_id, time.time())

        with open(self.log_file, "a") as f:
            f.write(f"\n[POST-ANALYZE] Task ID: {task_id}\n")
            f.write(f"Duration: {duration:.2f}s\n")
            f.write(f"Complexity: {analysis.complexity}\n")
            f.write(f"Technologies: {', '.join(analysis.technologies)}\n")
            f.write(f"Requirements: {len(analysis.requirements)}\n")
            f.write(f"Risks: {len(analysis.risks)}\n")

    def on_pre_validate(self, code: str, requirements: list[str] | None) -> None:
        """Log before validation."""
        with open(self.log_file, "a") as f:
            f.write("\n[PRE-VALIDATE]\n")
            f.write(f"Code length: {len(code)} characters\n")
            f.write(f"Requirements to check: {len(requirements or [])}\n")
            f.write(f"Timestamp: {time.ctime()}\n")

    def on_post_validate(self, code: str, result: ValidationResult) -> None:
        """Log after validation."""
        with open(self.log_file, "a") as f:
            f.write("\n[POST-VALIDATE]\n")
            f.write(f"Validation passed: {result.passed}\n")
            f.write(f"Score: {result.score}/100\n")
            f.write(f"Issues found: {len(result.issues)}\n")
            f.write(f"Suggestions: {len(result.suggestions)}\n")

            if result.issues:
                f.write("\nTop issues:\n")
                for issue in result.issues[:5]:
                    f.write(f"  - [{issue.severity}] {issue.message}\n")

    def on_error(self, error: Exception, context: dict[str, Any]) -> None:
        """Log errors."""
        with open(self.log_file, "a") as f:
            f.write("\n[ERROR]\n")
            f.write(f"Error type: {type(error).__name__}\n")
            f.write(f"Error message: {str(error)}\n")
            f.write(f"Context: {context}\n")
            f.write(f"Timestamp: {time.ctime()}\n")

    def on_progress(self, task_id: str, progress: float, message: str) -> None:
        """Log progress updates."""
        with open(self.log_file, "a") as f:
            f.write(f"\n[PROGRESS] Task {task_id}: {progress:.1f}% - {message}\n")

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        with open(self.log_file, "a") as f:
            f.write(f"\n=== Enhanced Logging Plugin Stopped at {time.ctime()} ===\n")
