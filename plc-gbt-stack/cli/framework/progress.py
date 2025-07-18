#!/usr/bin/env python3
"""
⏳ Phase 21.5: Progress Indicators System

Comprehensive progress tracking system for CLI operations with rich visual feedback,
time estimation, and performance monitoring.

AI Task Orchestrator Implementation
=====================================
Task Classification: MODERATE (Progress indication framework)
Context Management: Real-time operation tracking with user feedback
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.5 Objectives:
- Rich progress indicators for all operations
- Time estimation and performance tracking
- Context-aware progress messages
- Multi-stage operation support

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.5.1 - Progress Indicators
Dependencies: rich, click
"""

import time
import asyncio
import threading
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from rich.console import Console
from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    FileSizeColumn,
    TransferSpeedColumn
)
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich import print as rprint

console = Console()

# =============================================================================
# PROGRESS SYSTEM CLASSES
# =============================================================================

class OperationType(Enum):
    """Types of operations that can be tracked"""
    SCHEMA_VALIDATION = "schema_validation"
    INSTANCE_CREATION = "instance_creation"
    BATCH_PROCESSING = "batch_processing"
    PLC_CONNECTION = "plc_connection"
    DATA_PROCESSING = "data_processing"
    FILE_OPERATION = "file_operation"
    MEMORY_OPERATION = "memory_operation"
    EXPORT_IMPORT = "export_import"

@dataclass
class ProgressConfig:
    """Configuration for progress tracking"""
    show_spinner: bool = True
    show_percentage: bool = True
    show_time_elapsed: bool = True
    show_time_remaining: bool = True
    show_speed: bool = False
    show_details: bool = True
    refresh_rate: int = 10  # Hz
    auto_clear: bool = True

@dataclass
class OperationMetrics:
    """Metrics collected during operation"""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    processing_rate: float = 0.0  # items per second
    estimated_completion: Optional[datetime] = None
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage"""
        if self.completed_items + self.failed_items == 0:
            return 0.0
        return (self.completed_items / (self.completed_items + self.failed_items)) * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Calculate elapsed time"""
        end = self.end_time or datetime.now()
        return end - self.start_time

class ProgressTracker:
    """
    Comprehensive progress tracking system
    
    Features:
    - Multiple progress bar types
    - Time estimation and performance tracking
    - Context-aware messaging
    - Multi-stage operation support
    """
    
    def __init__(self, config: Optional[ProgressConfig] = None):
        self.config = config or ProgressConfig()
        self.progress: Optional[Progress] = None
        self.current_task: Optional[int] = None
        self.metrics = OperationMetrics()
        self.operation_type: Optional[OperationType] = None
        self.sub_operations: Dict[str, int] = {}
        
    def _create_progress_bar(self, operation_type: OperationType) -> Progress:
        """Create appropriate progress bar for operation type"""
        
        columns = []
        
        if self.config.show_spinner:
            columns.append(SpinnerColumn())
        
        columns.append(TextColumn("[progress.description]{task.description}"))
        
        if operation_type in [OperationType.FILE_OPERATION, OperationType.EXPORT_IMPORT]:
            columns.extend([
                BarColumn(),
                TaskProgressColumn(),
                FileSizeColumn(),
                TransferSpeedColumn()
            ])
        elif operation_type in [OperationType.BATCH_PROCESSING, OperationType.DATA_PROCESSING]:
            columns.extend([
                BarColumn(),
                MofNCompleteColumn(),
                TaskProgressColumn()
            ])
        else:
            columns.extend([
                BarColumn(),
                TaskProgressColumn()
            ])
        
        if self.config.show_time_elapsed:
            columns.append(TimeElapsedColumn())
        
        if self.config.show_time_remaining:
            columns.append(TimeRemainingColumn())
        
        return Progress(
            *columns,
            refresh_per_second=self.config.refresh_rate,
            auto_refresh=True
        )
    
    @contextmanager
    def track_operation(self, description: str, total: Optional[int] = None, 
                       operation_type: OperationType = OperationType.DATA_PROCESSING):
        """Context manager for tracking operations"""
        
        self.operation_type = operation_type
        self.metrics = OperationMetrics()
        self.metrics.total_items = total or 0
        
        # Create and start progress bar
        self.progress = self._create_progress_bar(operation_type)
        
        try:
            with self.progress:
                self.current_task = self.progress.add_task(
                    description, 
                    total=total
                )
                yield self
        finally:
            if self.config.auto_clear:
                self.progress = None
                self.current_task = None
            self.metrics.end_time = datetime.now()
    
    def update(self, advance: int = 1, description: Optional[str] = None, **kwargs):
        """Update progress"""
        if self.progress and self.current_task is not None:
            if description:
                self.progress.update(self.current_task, description=description)
            self.progress.update(self.current_task, advance=advance, **kwargs)
            
            # Update metrics
            self.metrics.completed_items += advance
            self._update_performance_metrics()
    
    def set_total(self, total: int):
        """Set total number of items"""
        if self.progress and self.current_task is not None:
            self.progress.update(self.current_task, total=total)
            self.metrics.total_items = total
    
    def add_failure(self, count: int = 1):
        """Record failed items"""
        self.metrics.failed_items += count
    
    def _update_performance_metrics(self):
        """Update performance metrics"""
        elapsed = self.metrics.elapsed_time.total_seconds()
        if elapsed > 0:
            self.metrics.processing_rate = self.metrics.completed_items / elapsed
            
            # Estimate completion time
            if self.metrics.total_items > 0:
                remaining_items = self.metrics.total_items - self.metrics.completed_items
                if self.metrics.processing_rate > 0:
                    remaining_seconds = remaining_items / self.metrics.processing_rate
                    self.metrics.estimated_completion = datetime.now() + timedelta(seconds=remaining_seconds)
    
    def add_sub_operation(self, name: str, description: str, total: Optional[int] = None) -> int:
        """Add sub-operation to track"""
        if self.progress:
            task_id = self.progress.add_task(description, total=total)
            self.sub_operations[name] = task_id
            return task_id
        return -1
    
    def update_sub_operation(self, name: str, advance: int = 1, **kwargs):
        """Update sub-operation progress"""
        if self.progress and name in self.sub_operations:
            task_id = self.sub_operations[name]
            self.progress.update(task_id, advance=advance, **kwargs)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get operation summary"""
        return {
            "operation_type": self.operation_type.value if self.operation_type else None,
            "total_items": self.metrics.total_items,
            "completed_items": self.metrics.completed_items,
            "failed_items": self.metrics.failed_items,
            "success_rate": self.metrics.success_rate,
            "elapsed_time": str(self.metrics.elapsed_time),
            "processing_rate": f"{self.metrics.processing_rate:.2f} items/sec",
            "estimated_completion": self.metrics.estimated_completion.isoformat() if self.metrics.estimated_completion else None
        }

# =============================================================================
# SPECIALIZED PROGRESS TRACKERS
# =============================================================================

class SchemaProgressTracker(ProgressTracker):
    """Specialized progress tracker for schema operations"""
    
    def __init__(self):
        super().__init__(ProgressConfig(show_time_remaining=True, show_details=True))
        
    @contextmanager
    def track_schema_validation(self, schema_count: int):
        """Track schema validation progress"""
        with self.track_operation(
            f"Validating {schema_count} schemas...",
            total=schema_count,
            operation_type=OperationType.SCHEMA_VALIDATION
        ) as tracker:
            yield tracker
    
    @contextmanager
    def track_schema_creation(self, steps: int = 5):
        """Track schema creation steps"""
        with self.track_operation(
            "Creating schema...",
            total=steps,
            operation_type=OperationType.SCHEMA_VALIDATION
        ) as tracker:
            yield tracker

class InstanceProgressTracker(ProgressTracker):
    """Specialized progress tracker for instance operations"""
    
    def __init__(self):
        super().__init__(ProgressConfig(show_speed=True, show_time_remaining=True))
    
    @contextmanager
    def track_instance_creation(self, instance_count: int):
        """Track instance creation progress"""
        with self.track_operation(
            f"Creating {instance_count} instances...",
            total=instance_count,
            operation_type=OperationType.INSTANCE_CREATION
        ) as tracker:
            yield tracker
    
    @contextmanager
    def track_plc_connection(self):
        """Track PLC connection progress"""
        with self.track_operation(
            "Connecting to PLC...",
            operation_type=OperationType.PLC_CONNECTION
        ) as tracker:
            yield tracker

class BatchProgressTracker(ProgressTracker):
    """Specialized progress tracker for batch operations"""
    
    def __init__(self):
        super().__init__(ProgressConfig(show_speed=True, show_time_remaining=True, show_details=True))
    
    @contextmanager
    def track_batch_processing(self, total_files: int, operation_name: str):
        """Track batch processing progress"""
        with self.track_operation(
            f"Batch {operation_name} ({total_files} files)...",
            total=total_files,
            operation_type=OperationType.BATCH_PROCESSING
        ) as tracker:
            # Add sub-operations for different stages
            tracker.add_sub_operation("validation", "Validating files...", total_files)
            tracker.add_sub_operation("processing", "Processing files...", total_files)
            tracker.add_sub_operation("output", "Generating output...", total_files)
            yield tracker

class MemoryProgressTracker(ProgressTracker):
    """Specialized progress tracker for memory operations"""
    
    def __init__(self):
        super().__init__(ProgressConfig(show_spinner=True, show_time_elapsed=True))
    
    @contextmanager
    def track_memory_ingestion(self, file_count: int):
        """Track memory system ingestion"""
        with self.track_operation(
            f"Ingesting {file_count} files to memory...",
            total=file_count,
            operation_type=OperationType.MEMORY_OPERATION
        ) as tracker:
            yield tracker
    
    @contextmanager
    def track_memory_optimization(self):
        """Track memory optimization"""
        with self.track_operation(
            "Optimizing memory tiers...",
            operation_type=OperationType.MEMORY_OPERATION
        ) as tracker:
            yield tracker

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def show_operation_summary(tracker: ProgressTracker, title: str = "Operation Summary"):
    """Show detailed operation summary"""
    summary = tracker.get_summary()
    
    table = Table(title=title)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Total Items", str(summary["total_items"]))
    table.add_row("Completed", str(summary["completed_items"]))
    table.add_row("Failed", str(summary["failed_items"]))
    table.add_row("Success Rate", f"{summary['success_rate']:.1f}%")
    table.add_row("Elapsed Time", summary["elapsed_time"])
    table.add_row("Processing Rate", summary["processing_rate"])
    
    console.print(table)

@contextmanager
def simple_progress(description: str, total: Optional[int] = None):
    """Simple progress context manager"""
    tracker = ProgressTracker()
    with tracker.track_operation(description, total) as progress:
        yield progress

# Spinner for indefinite operations
@contextmanager
def spinner_progress(description: str):
    """Simple spinner for indefinite operations"""
    with console.status(description) as status:
        yield status

# =============================================================================
# ASYNC PROGRESS SUPPORT
# =============================================================================

class AsyncProgressTracker:
    """Async-compatible progress tracker"""
    
    def __init__(self, config: Optional[ProgressConfig] = None):
        self.config = config or ProgressConfig()
        self.sync_tracker = ProgressTracker(config)
    
    async def track_async_operation(self, description: str, async_func: Callable, 
                                  total: Optional[int] = None,
                                  operation_type: OperationType = OperationType.DATA_PROCESSING):
        """Track async operation with progress"""
        
        with self.sync_tracker.track_operation(description, total, operation_type) as tracker:
            # Run async function in executor to maintain progress updates
            result = await async_func(tracker)
            return result

# =============================================================================
# GLOBAL PROGRESS FACTORY
# =============================================================================

class ProgressFactory:
    """Factory for creating appropriate progress trackers"""
    
    @staticmethod
    def create_tracker(operation_type: OperationType) -> ProgressTracker:
        """Create appropriate tracker for operation type"""
        
        if operation_type == OperationType.SCHEMA_VALIDATION:
            return SchemaProgressTracker()
        elif operation_type == OperationType.INSTANCE_CREATION:
            return InstanceProgressTracker()
        elif operation_type == OperationType.BATCH_PROCESSING:
            return BatchProgressTracker()
        elif operation_type == OperationType.MEMORY_OPERATION:
            return MemoryProgressTracker()
        else:
            return ProgressTracker()
    
    @staticmethod
    def create_config(verbose: bool = False, detailed: bool = False) -> ProgressConfig:
        """Create progress config based on user preferences"""
        return ProgressConfig(
            show_details=detailed or verbose,
            show_time_remaining=detailed,
            show_speed=verbose,
            refresh_rate=20 if verbose else 10
        )

# =============================================================================
# EXAMPLES AND TESTING
# =============================================================================

if __name__ == "__main__":
    import random
    
    async def demo_progress_system():
        """Demonstrate the progress system"""
        
        console.print("[bold blue]🎯 Progress System Demo[/bold blue]\n")
        
        # Demo 1: Simple file processing
        with simple_progress("Processing files", total=10) as progress:
            for i in range(10):
                time.sleep(0.2)
                progress.update(1, description=f"Processing file {i+1}/10")
        
        console.print("[green]✅ File processing complete[/green]\n")
        
        # Demo 2: Schema validation
        schema_tracker = SchemaProgressTracker()
        with schema_tracker.track_schema_validation(5) as progress:
            for i in range(5):
                time.sleep(0.3)
                progress.update(1, description=f"Validating schema {i+1}")
        
        show_operation_summary(schema_tracker, "Schema Validation Summary")
        console.print()
        
        # Demo 3: Batch processing with sub-operations
        batch_tracker = BatchProgressTracker()
        with batch_tracker.track_batch_processing(20, "validation") as progress:
            # Validation phase
            for i in range(20):
                time.sleep(0.1)
                progress.update_sub_operation("validation", 1)
            
            # Processing phase
            for i in range(20):
                time.sleep(0.1)
                progress.update_sub_operation("processing", 1)
                progress.update(1, description=f"Processed {i+1}/20 files")
        
        show_operation_summary(batch_tracker, "Batch Processing Summary")
        
    asyncio.run(demo_progress_system()) 