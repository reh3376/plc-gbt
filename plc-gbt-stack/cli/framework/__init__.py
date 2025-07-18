"""
🖥️ CLI Framework Package

Core framework components for the PLC Control Loop CLI.
"""

from .command_base import BaseCommand, AsyncCommand
from .permissions import Permission, requires_permission, CLICommand

# Phase 21.5 enhancements
from .progress import (
    ProgressTracker, 
    ProgressConfig, 
    OperationType,
    SchemaProgressTracker,
    InstanceProgressTracker,
    BatchProgressTracker,
    MemoryProgressTracker,
    ProgressFactory,
    simple_progress,
    spinner_progress,
    show_operation_summary
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