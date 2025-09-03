"""
🖥️ CLI Framework Package

Core framework components for the PLC Control Loop CLI.
"""

from .command_base import AsyncCommand, BaseCommand
from .permissions import CLICommand, Permission, requires_permission

# Phase 21.5 enhancements
from .progress import (
    BatchProgressTracker,
    InstanceProgressTracker,
    MemoryProgressTracker,
    OperationType,
    ProgressConfig,
    ProgressFactory,
    ProgressTracker,
    SchemaProgressTracker,
    show_operation_summary,
    simple_progress,
    spinner_progress,
)

# Export enhanced components for Phase 21.5
__all__ = [
    # Existing exports
    "CLICommand",
    "Permission",
    "requires_permission",
    "CLICommandBase",

    # Phase 21.5 Progress System
    "ProgressTracker",
    "ProgressConfig",
    "OperationType",
    "SchemaProgressTracker",
    "InstanceProgressTracker",
    "BatchProgressTracker",
    "MemoryProgressTracker",
    "ProgressFactory",
    "simple_progress",
    "spinner_progress",
    "show_operation_summary"
]
