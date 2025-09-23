"""Progress monitoring module for the PLC Task Orchestrator."""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from plc_orchestrator.utils.data_models import TaskProgressUpdate
from plc_orchestrator.utils.helpers import format_duration
from plc_orchestrator.utils.logging import get_logger


class TaskProgressMonitor:
    """Monitors and reports task execution progress."""

    def __init__(self, task_id: str, config: dict[str, Any] | None = None) -> None:
        """
        Initialize progress monitor.

        Args:
            task_id: Unique task identifier
            config: Optional configuration
        """
        self.task_id = task_id
        self.config = config or {}
        self.logger = get_logger(__name__, config)

        # Progress tracking
        self.start_time = datetime.now()
        self.current_step = 0
        self.total_steps = 0
        self.status = "initialized"
        self.step_details: dict[int, dict[str, Any]] = {}

        # Callbacks
        self.progress_callbacks: list[Callable[[TaskProgressUpdate], None]] = []

    def set_total_steps(self, total: int) -> None:
        """
        Set total number of steps.

        Args:
            total: Total number of steps
        """
        self.total_steps = total
        self.logger.info(f"Task {self.task_id}: Set total steps to {total}")

    def start_step(
        self, step_number: int, step_name: str, details: dict[str, Any] | None = None
    ) -> None:
        """
        Mark the start of a step.

        Args:
            step_number: Step number (1-based)
            step_name: Name of the step
            details: Optional step details
        """
        self.current_step = step_number
        self.status = f"Running: {step_name}"

        self.step_details[step_number] = {
            "name": step_name,
            "start_time": datetime.now(),
            "status": "in_progress",
            "details": details or {},
        }

        self.logger.info(
            f"Task {self.task_id}: Started step {step_number}/{self.total_steps} - {step_name}"
        )

        self._emit_progress_update()

    def complete_step(self, step_number: int, result: dict[str, Any] | None = None) -> None:
        """
        Mark a step as completed.

        Args:
            step_number: Step number
            result: Optional step result
        """
        if step_number in self.step_details:
            step_info = self.step_details[step_number]
            step_info["end_time"] = datetime.now()
            step_info["status"] = "completed"
            step_info["result"] = result or {}

            duration = (step_info["end_time"] - step_info["start_time"]).total_seconds()
            step_info["duration"] = duration

            self.logger.info(
                f"Task {self.task_id}: Completed step {step_number}/{self.total_steps} "
                f"- {step_info['name']} in {format_duration(duration)}"
            )

        self._emit_progress_update()

    def fail_step(self, step_number: int, error: str) -> None:
        """
        Mark a step as failed.

        Args:
            step_number: Step number
            error: Error message
        """
        if step_number in self.step_details:
            step_info = self.step_details[step_number]
            step_info["end_time"] = datetime.now()
            step_info["status"] = "failed"
            step_info["error"] = error

            self.logger.error(
                f"Task {self.task_id}: Failed step {step_number}/{self.total_steps} "
                f"- {step_info['name']}: {error}"
            )

        self.status = f"Failed: {error}"
        self._emit_progress_update()

    def update_progress(
        self,
        current_step: int | None = None,
        status: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> TaskProgressUpdate:
        """
        Update task progress.

        Args:
            current_step: Current step number
            status: Status message
            details: Additional details

        Returns:
            Progress update object
        """
        if current_step is not None:
            self.current_step = current_step
        if status is not None:
            self.status = status

        update = self._create_progress_update(details)
        self._emit_progress_update(update)

        return update

    def add_progress_callback(self, callback: Callable[[TaskProgressUpdate], None]) -> None:
        """
        Add a progress callback.

        Args:
            callback: Function to call on progress updates
        """
        self.progress_callbacks.append(callback)

    def get_elapsed_time(self) -> float:
        """
        Get elapsed time in seconds.

        Returns:
            Elapsed time
        """
        return (datetime.now() - self.start_time).total_seconds()

    def get_percentage(self) -> float:
        """
        Get completion percentage.

        Returns:
            Percentage (0-100)
        """
        if self.total_steps == 0:
            return 0.0
        return (self.current_step / self.total_steps) * 100

    def get_summary(self) -> dict[str, Any]:
        """
        Get progress summary.

        Returns:
            Summary dictionary
        """
        elapsed_time = self.get_elapsed_time()
        percentage = self.get_percentage()

        # Calculate step statistics
        completed_steps = [s for s in self.step_details.values() if s["status"] == "completed"]
        failed_steps = [s for s in self.step_details.values() if s["status"] == "failed"]

        return {
            "task_id": self.task_id,
            "status": self.status,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "percentage": percentage,
            "elapsed_time": elapsed_time,
            "elapsed_time_formatted": format_duration(elapsed_time),
            "start_time": self.start_time.isoformat(),
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "step_details": self.step_details,
            "estimated_remaining_time": self._estimate_remaining_time(),
        }

    def _create_progress_update(
        self, additional_details: dict[str, Any] | None = None
    ) -> TaskProgressUpdate:
        """Create a progress update object."""
        details = {
            "step_name": self.step_details.get(self.current_step, {}).get("name", ""),
            "completed_steps": len(
                [s for s in self.step_details.values() if s["status"] == "completed"]
            ),
            "failed_steps": len([s for s in self.step_details.values() if s["status"] == "failed"]),
        }

        if additional_details:
            details.update(additional_details)

        return TaskProgressUpdate(
            task_id=self.task_id,
            current_step=self.current_step,
            total_steps=self.total_steps,
            percentage=self.get_percentage(),
            status=self.status,
            elapsed_time=self.get_elapsed_time(),
            details=details,
            timestamp=datetime.now(),
        )

    def _emit_progress_update(self, update: TaskProgressUpdate | None = None) -> None:
        """Emit progress update to callbacks."""
        if update is None:
            update = self._create_progress_update()

        for callback in self.progress_callbacks:
            try:
                callback(update)
            except Exception as e:
                self.logger.error(f"Progress callback error: {e}")

    def _estimate_remaining_time(self) -> float | None:
        """Estimate remaining time based on completed steps."""
        completed_steps = [
            s for s in self.step_details.values() if s["status"] == "completed" and "duration" in s
        ]

        if not completed_steps or self.current_step >= self.total_steps:
            return None

        # Calculate average step duration
        avg_duration = sum(s["duration"] for s in completed_steps) / len(completed_steps)

        # Estimate remaining time
        remaining_steps = self.total_steps - self.current_step
        return avg_duration * remaining_steps


class ProgressReporter:
    """Utility class for reporting progress in different formats."""

    @staticmethod
    def console_reporter(update: TaskProgressUpdate) -> None:
        """
        Report progress to console.

        Args:
            update: Progress update
        """
        bar_length = 30
        filled_length = int(bar_length * update.percentage / 100)
        bar = "█" * filled_length + "░" * (bar_length - filled_length)

        print(
            f"\r[{bar}] {update.percentage:.1f}% - "
            f"Step {update.current_step}/{update.total_steps}: {update.status}",
            end="",
            flush=True,
        )

        if update.percentage >= 100:
            print()  # New line at completion

    @staticmethod
    def json_reporter(update: TaskProgressUpdate) -> dict[str, Any]:
        """
        Convert progress update to JSON-serializable format.

        Args:
            update: Progress update

        Returns:
            JSON-serializable dictionary
        """
        return {
            "task_id": update.task_id,
            "current_step": update.current_step,
            "total_steps": update.total_steps,
            "percentage": update.percentage,
            "status": update.status,
            "elapsed_time": update.elapsed_time,
            "timestamp": update.timestamp.isoformat(),
            "details": update.details,
        }
