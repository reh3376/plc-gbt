#!/usr/bin/env python3
"""
Phase 23.3: Task Execution Engine
================================

Comprehensive task planning and execution system for complex multi-step operations
derived from natural language inputs. Provides autonomous execution with safety
checks, progress tracking, and intelligent error recovery.

This module integrates with Phase 23.1 (LLM Integration) and Phase 23.2 (Natural
Language Understanding) to provide end-to-end task automation capabilities.

Components:
- TaskPlan: Structured representation of multi-step tasks
- TaskExecutor: Core execution engine with safety and monitoring
- ExecutionContext: Stateful context management during execution
- ProgressTracker: Real-time progress monitoring and user feedback
- ErrorRecovery: Intelligent error handling and recovery strategies

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 23.3 - Task Execution Engine
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task execution status enumeration"""
    PENDING = "pending"
    PLANNING = "planning"
    PLANNED = "planned"
    EXECUTING = "executing"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ROLLBACK = "rollback"

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

class StepType(Enum):
    """Types of execution steps"""
    CLI_COMMAND = "cli_command"
    API_CALL = "api_call"
    FILE_OPERATION = "file_operation"
    DATABASE_QUERY = "database_query"
    VALIDATION = "validation"
    SAFETY_CHECK = "safety_check"
    USER_CONFIRMATION = "user_confirmation"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    PARALLEL = "parallel"

@dataclass
class TaskStep:
    """Individual step in a task execution plan"""
    step_id: str
    step_type: StepType
    description: str
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: int = 30
    retry_count: int = 3
    rollback_command: Optional[str] = None
    safety_level: int = 1  # 1=low risk, 5=high risk
    confirmation_required: bool = False
    
    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    retries_attempted: int = 0

@dataclass
class TaskPlan:
    """Complete task execution plan with metadata"""
    task_id: str
    name: str
    description: str
    original_request: str
    steps: List[TaskStep] = field(default_factory=list)
    
    # Metadata
    priority: TaskPriority = TaskPriority.NORMAL
    estimated_duration: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"
    
    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percentage: float = 0.0
    current_step_index: int = 0
    
    # Safety and validation
    safety_score: float = 1.0  # 1.0=safe, 5.0=dangerous
    requires_approval: bool = False
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None

class ExecutionContext:
    """Maintains state and context during task execution"""
    
    def __init__(self, task_plan: TaskPlan):
        self.task_plan = task_plan
        self.variables: Dict[str, Any] = {}
        self.step_results: Dict[str, Any] = {}
        self.rollback_stack: List[str] = []
        self.execution_log: List[Dict[str, Any]] = []
        self.safety_violations: List[str] = []
        
    def set_variable(self, name: str, value: Any) -> None:
        """Set a context variable"""
        self.variables[name] = value
        self.log_event("variable_set", {"name": name, "value": str(value)})
        
    def get_variable(self, name: str, default: Any = None) -> Any:
        """Get a context variable"""
        return self.variables.get(name, default)
        
    def set_step_result(self, step_id: str, result: Any) -> None:
        """Store result from a completed step"""
        self.step_results[step_id] = result
        self.log_event("step_completed", {"step_id": step_id, "result": str(result)})
        
    def get_step_result(self, step_id: str) -> Any:
        """Get result from a previously completed step"""
        return self.step_results.get(step_id)
        
    def add_rollback_action(self, action: str) -> None:
        """Add an action to the rollback stack"""
        self.rollback_stack.append(action)
        
    def log_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an execution event"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.execution_log.append(event)
        logger.info(f"Task {self.task_plan.task_id}: {event_type} - {data}")
        
    def add_safety_violation(self, violation: str) -> None:
        """Record a safety violation"""
        self.safety_violations.append(violation)
        self.log_event("safety_violation", {"violation": violation})
        logger.warning(f"Safety violation in task {self.task_plan.task_id}: {violation}")

class ProgressTracker:
    """Real-time progress tracking and user feedback"""
    
    def __init__(self, task_plan: TaskPlan):
        self.task_plan = task_plan
        self.callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
    def add_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a progress callback function"""
        self.callbacks.append(callback)
        
    def update_progress(self, step_index: int, step_status: TaskStatus, message: str = "") -> None:
        """Update task progress"""
        total_steps = len(self.task_plan.steps)
        progress_percentage = (step_index / total_steps) * 100 if total_steps > 0 else 0
        
        self.task_plan.current_step_index = step_index
        self.task_plan.progress_percentage = progress_percentage
        
        progress_data = {
            "task_id": self.task_plan.task_id,
            "task_name": self.task_plan.name,
            "progress_percentage": progress_percentage,
            "current_step": step_index,
            "total_steps": total_steps,
            "step_status": step_status.value,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Notify all callbacks
        for callback in self.callbacks:
            try:
                callback(progress_data)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")

class ErrorRecovery:
    """Intelligent error handling and recovery strategies"""
    
    def __init__(self):
        self.recovery_strategies: Dict[str, Callable] = {
            "retry": self._retry_strategy,
            "skip": self._skip_strategy,
            "rollback": self._rollback_strategy,
            "alternative": self._alternative_strategy,
            "user_intervention": self._user_intervention_strategy
        }
        
    async def handle_error(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """
        Handle step execution error and determine recovery action
        
        Returns:
            Tuple[bool, str]: (should_continue, recovery_action)
        """
        error_type = type(error).__name__
        error_message = str(error)
        
        context.log_event("error_occurred", {
            "step_id": step.step_id,
            "error_type": error_type,
            "error_message": error_message
        })
        
        # Determine recovery strategy based on error type and step configuration
        if step.retries_attempted < step.retry_count:
            return await self._retry_strategy(step, error, context)
        elif step.safety_level <= 2:  # Low-risk steps can be skipped
            return await self._skip_strategy(step, error, context)
        elif step.rollback_command:
            return await self._rollback_strategy(step, error, context)
        else:
            return await self._user_intervention_strategy(step, error, context)
            
    async def _retry_strategy(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """Retry the failed step"""
        step.retries_attempted += 1
        wait_time = min(2 ** step.retries_attempted, 30)  # Exponential backoff, max 30s
        
        context.log_event("retry_attempt", {
            "step_id": step.step_id,
            "attempt": step.retries_attempted,
            "wait_time": wait_time
        })
        
        await asyncio.sleep(wait_time)
        return True, "retry"
        
    async def _skip_strategy(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """Skip the failed step and continue"""
        context.log_event("step_skipped", {
            "step_id": step.step_id,
            "reason": "error_recovery"
        })
        
        step.status = TaskStatus.FAILED
        step.error = str(error)
        return True, "skip"
        
    async def _rollback_strategy(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """Execute rollback command and continue"""
        try:
            if step.rollback_command:
                context.log_event("rollback_initiated", {"step_id": step.step_id})
                # Execute rollback command (implementation depends on command type)
                context.add_rollback_action(step.rollback_command)
                
            return True, "rollback"
        except Exception as rollback_error:
            context.log_event("rollback_failed", {
                "step_id": step.step_id,
                "rollback_error": str(rollback_error)
            })
            return False, "rollback_failed"
            
    async def _alternative_strategy(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """Try an alternative approach"""
        # This would be implemented based on specific step types and available alternatives
        context.log_event("alternative_attempted", {"step_id": step.step_id})
        return True, "alternative"
        
    async def _user_intervention_strategy(self, step: TaskStep, error: Exception, context: ExecutionContext) -> Tuple[bool, str]:
        """Request user intervention"""
        context.log_event("user_intervention_required", {
            "step_id": step.step_id,
            "error": str(error)
        })
        
        # In a real implementation, this would prompt the user
        # For now, we'll mark as failed and stop execution
        return False, "user_intervention_required"

class TaskExecutor:
    """Core task execution engine with safety and monitoring"""
    
    def __init__(self):
        self.running_tasks: Dict[str, TaskPlan] = {}
        self.completed_tasks: Dict[str, TaskPlan] = {}
        self.error_recovery = ErrorRecovery()
        self.safety_checks_enabled = True
        
        # Command executors for different step types
        self.step_executors: Dict[StepType, Callable] = {
            StepType.CLI_COMMAND: self._execute_cli_command,
            StepType.API_CALL: self._execute_api_call,
            StepType.FILE_OPERATION: self._execute_file_operation,
            StepType.DATABASE_QUERY: self._execute_database_query,
            StepType.VALIDATION: self._execute_validation,
            StepType.SAFETY_CHECK: self._execute_safety_check,
            StepType.USER_CONFIRMATION: self._execute_user_confirmation,
            StepType.CONDITIONAL: self._execute_conditional,
            StepType.LOOP: self._execute_loop,
            StepType.PARALLEL: self._execute_parallel
        }
        
    async def execute_task(self, task_plan: TaskPlan) -> bool:
        """
        Execute a complete task plan
        
        Returns:
            bool: True if task completed successfully, False otherwise
        """
        task_plan.status = TaskStatus.EXECUTING
        task_plan.start_time = datetime.now()
        self.running_tasks[task_plan.task_id] = task_plan
        
        context = ExecutionContext(task_plan)
        progress_tracker = ProgressTracker(task_plan)
        
        try:
            logger.info(f"Starting task execution: {task_plan.name} ({task_plan.task_id})")
            
            # Pre-execution safety checks
            if self.safety_checks_enabled:
                if not await self._perform_safety_checks(task_plan, context):
                    task_plan.status = TaskStatus.FAILED
                    context.add_safety_violation("Pre-execution safety checks failed")
                    return False
                    
            # Execute steps in sequence
            for i, step in enumerate(task_plan.steps):
                if task_plan.status in [TaskStatus.CANCELLED, TaskStatus.FAILED]:
                    break
                    
                progress_tracker.update_progress(i, TaskStatus.EXECUTING, f"Executing: {step.description}")
                
                success = await self._execute_step(step, context)
                if not success and step.safety_level >= 4:  # High-risk step failed
                    task_plan.status = TaskStatus.FAILED
                    break
                    
            # Determine final status
            if task_plan.status == TaskStatus.EXECUTING:
                if all(step.status in [TaskStatus.COMPLETED, TaskStatus.FAILED] for step in task_plan.steps):
                    failed_critical_steps = [s for s in task_plan.steps 
                                           if s.status == TaskStatus.FAILED and s.safety_level >= 4]
                    if not failed_critical_steps:
                        task_plan.status = TaskStatus.COMPLETED
                        progress_tracker.update_progress(len(task_plan.steps), TaskStatus.COMPLETED, "Task completed successfully")
                    else:
                        task_plan.status = TaskStatus.FAILED
                        
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            task_plan.status = TaskStatus.FAILED
            context.log_event("task_execution_error", {"error": str(e)})
            
        finally:
            task_plan.end_time = datetime.now()
            self.running_tasks.pop(task_plan.task_id, None)
            self.completed_tasks[task_plan.task_id] = task_plan
            
            logger.info(f"Task execution completed: {task_plan.name} - Status: {task_plan.status.value}")
            
        return task_plan.status == TaskStatus.COMPLETED
        
    async def _execute_step(self, step: TaskStep, context: ExecutionContext) -> bool:
        """Execute a single step with error handling and retries"""
        step.status = TaskStatus.EXECUTING
        step.start_time = datetime.now()
        
        while step.retries_attempted <= step.retry_count:
            try:
                # Check dependencies
                if not self._check_dependencies(step, context):
                    step.status = TaskStatus.FAILED
                    step.error = "Dependencies not satisfied"
                    return False
                    
                # Get appropriate executor
                executor = self.step_executors.get(step.step_type)
                if not executor:
                    raise ValueError(f"No executor found for step type: {step.step_type}")
                    
                # Execute with timeout
                result = await asyncio.wait_for(
                    executor(step, context),
                    timeout=step.timeout_seconds
                )
                
                step.result = result
                step.status = TaskStatus.COMPLETED
                step.end_time = datetime.now()
                context.set_step_result(step.step_id, result)
                
                logger.debug(f"Step completed: {step.step_id} - {step.description}")
                return True
                
            except Exception as e:
                logger.error(f"Step execution error: {step.step_id} - {e}")
                
                # Handle error with recovery strategy
                should_continue, recovery_action = await self.error_recovery.handle_error(step, e, context)
                
                if recovery_action == "retry":
                    continue  # Try again
                elif recovery_action == "skip":
                    return True  # Consider as success for continuation
                elif not should_continue:
                    step.status = TaskStatus.FAILED
                    step.error = str(e)
                    step.end_time = datetime.now()
                    return False
                    
        # If we get here, all retries failed
        step.status = TaskStatus.FAILED
        step.end_time = datetime.now()
        return False
        
    def _check_dependencies(self, step: TaskStep, context: ExecutionContext) -> bool:
        """Check if step dependencies are satisfied"""
        for dep_id in step.dependencies:
            dep_result = context.get_step_result(dep_id)
            if dep_result is None:
                return False
        return True
        
    async def _perform_safety_checks(self, task_plan: TaskPlan, context: ExecutionContext) -> bool:
        """Perform pre-execution safety checks"""
        # Check overall task safety score
        if task_plan.safety_score >= 4.0 and not task_plan.approved_by:
            context.add_safety_violation("High-risk task requires approval")
            return False
            
        # Check for dangerous step combinations
        high_risk_steps = [s for s in task_plan.steps if s.safety_level >= 4]
        if len(high_risk_steps) > 3:
            context.add_safety_violation("Too many high-risk steps in single task")
            return False
            
        # Check for required confirmations
        confirmation_steps = [s for s in task_plan.steps if s.confirmation_required]
        for step in confirmation_steps:
            # In a real implementation, this would prompt for confirmation
            context.log_event("confirmation_required", {"step_id": step.step_id})
            
        return True
        
    # Step execution methods
    async def _execute_cli_command(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a CLI command step"""
        import subprocess
        
        command = step.command
        # Substitute variables from context
        for var_name, var_value in context.variables.items():
            command = command.replace(f"{{{var_name}}}", str(var_value))
            
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=step.timeout_seconds
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"Command failed: {result.stderr}")
            
        return result.stdout.strip()
        
    async def _execute_api_call(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute an API call step"""
        # Implementation would depend on the specific API
        # For now, return a mock result
        await asyncio.sleep(0.1)  # Simulate API call
        return {"status": "success", "data": step.parameters}
        
    async def _execute_file_operation(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a file operation step"""
        operation = step.parameters.get("operation", "read")
        file_path = step.parameters.get("path", "")
        
        if operation == "read":
            with open(file_path, 'r') as f:
                return f.read()
        elif operation == "write":
            content = step.parameters.get("content", "")
            with open(file_path, 'w') as f:
                f.write(content)
            return f"Written {len(content)} characters to {file_path}"
        else:
            raise ValueError(f"Unknown file operation: {operation}")
            
    async def _execute_database_query(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a database query step"""
        # Implementation would depend on the database type
        await asyncio.sleep(0.1)  # Simulate query
        return {"rows_affected": 1, "data": []}
        
    async def _execute_validation(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a validation step"""
        validation_type = step.parameters.get("type", "generic")
        value = context.get_variable(step.parameters.get("variable", ""))
        
        # Simple validation examples
        if validation_type == "not_empty":
            if not value:
                raise ValueError("Value is empty")
        elif validation_type == "numeric":
            if not isinstance(value, (int, float)):
                raise ValueError("Value is not numeric")
                
        return True
        
    async def _execute_safety_check(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a safety check step"""
        check_type = step.parameters.get("type", "generic")
        
        # Example safety checks
        if check_type == "system_resources":
            # Check system resources
            import psutil
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            if cpu_usage > 90:
                raise RuntimeError("CPU usage too high for safe operation")
            if memory_usage > 90:
                raise RuntimeError("Memory usage too high for safe operation")
                
        return True
        
    async def _execute_user_confirmation(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a user confirmation step"""
        message = step.parameters.get("message", "Confirm to continue")
        
        # In a real implementation, this would prompt the user
        # For now, we'll auto-confirm for testing
        context.log_event("user_confirmation", {"message": message, "auto_confirmed": True})
        return True
        
    async def _execute_conditional(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a conditional step"""
        condition = step.parameters.get("condition", "true")
        variable_name = step.parameters.get("variable", "")
        expected_value = step.parameters.get("expected_value", True)
        
        actual_value = context.get_variable(variable_name)
        
        if condition == "equals":
            result = actual_value == expected_value
        elif condition == "not_equals":
            result = actual_value != expected_value
        elif condition == "greater_than":
            result = actual_value > expected_value
        elif condition == "less_than":
            result = actual_value < expected_value
        else:
            result = True  # Default to true
            
        return result
        
    async def _execute_loop(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute a loop step"""
        iterations = step.parameters.get("iterations", 1)
        loop_variable = step.parameters.get("loop_variable", "i")
        
        results = []
        for i in range(iterations):
            context.set_variable(loop_variable, i)
            results.append(f"Loop iteration {i}")
            
        return results
        
    async def _execute_parallel(self, step: TaskStep, context: ExecutionContext) -> Any:
        """Execute parallel steps"""
        parallel_steps = step.parameters.get("steps", [])
        
        # For simplicity, we'll execute them sequentially
        # In a real implementation, these would run in parallel
        results = []
        for parallel_step_data in parallel_steps:
            results.append(f"Parallel step: {parallel_step_data}")
            
        return results
        
    def get_task_status(self, task_id: str) -> Optional[TaskPlan]:
        """Get the current status of a task"""
        return self.running_tasks.get(task_id) or self.completed_tasks.get(task_id)
        
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        task = self.running_tasks.get(task_id)
        if task:
            task.status = TaskStatus.CANCELLED
            logger.info(f"Task cancelled: {task_id}")
            return True
        return False
        
    def get_running_tasks(self) -> List[TaskPlan]:
        """Get all currently running tasks"""
        return list(self.running_tasks.values())
        
    def get_completed_tasks(self) -> List[TaskPlan]:
        """Get all completed tasks"""
        return list(self.completed_tasks.values())

# Factory function for creating common task types
def create_control_loop_analysis_task(loop_name: str, data_source: str) -> TaskPlan:
    """Create a task plan for control loop analysis"""
    task_id = f"analysis_{loop_name}_{int(time.time())}"
    
    steps = [
        TaskStep(
            step_id=f"{task_id}_validate_data",
            step_type=StepType.VALIDATION,
            description=f"Validate data source for {loop_name}",
            command="validate_data_source",
            parameters={"source": data_source, "type": "not_empty"},
            safety_level=1
        ),
        TaskStep(
            step_id=f"{task_id}_load_data",
            step_type=StepType.CLI_COMMAND,
            description=f"Load control loop data for {loop_name}",
            command=f"plc-memory ingest --source {data_source} --loop {loop_name}",
            dependencies=[f"{task_id}_validate_data"],
            safety_level=2
        ),
        TaskStep(
            step_id=f"{task_id}_analyze",
            step_type=StepType.CLI_COMMAND,
            description=f"Analyze control loop {loop_name}",
            command=f"plc-control-loop analyze --loop {loop_name}",
            dependencies=[f"{task_id}_load_data"],
            safety_level=2
        ),
        TaskStep(
            step_id=f"{task_id}_generate_report",
            step_type=StepType.CLI_COMMAND,
            description=f"Generate analysis report for {loop_name}",
            command=f"plc-control-loop report --loop {loop_name} --format json",
            dependencies=[f"{task_id}_analyze"],
            safety_level=1
        )
    ]
    
    return TaskPlan(
        task_id=task_id,
        name=f"Analyze Control Loop: {loop_name}",
        description=f"Complete analysis of control loop {loop_name} using data from {data_source}",
        original_request=f"Analyze the {loop_name} control loop",
        steps=steps,
        priority=TaskPriority.NORMAL,
        estimated_duration=timedelta(minutes=10),
        safety_score=2.0
    )

def create_schema_management_task(operation: str, schema_name: str) -> TaskPlan:
    """Create a task plan for schema management operations"""
    task_id = f"schema_{operation}_{schema_name}_{int(time.time())}"
    
    steps = []
    
    if operation == "create":
        steps = [
            TaskStep(
                step_id=f"{task_id}_validate_name",
                step_type=StepType.VALIDATION,
                description=f"Validate schema name: {schema_name}",
                command="validate_schema_name",
                parameters={"name": schema_name, "type": "not_empty"},
                safety_level=1
            ),
            TaskStep(
                step_id=f"{task_id}_create_schema",
                step_type=StepType.CLI_COMMAND,
                description=f"Create new schema: {schema_name}",
                command=f"plc-control-loop schema create --name {schema_name}",
                dependencies=[f"{task_id}_validate_name"],
                safety_level=2
            ),
            TaskStep(
                step_id=f"{task_id}_validate_schema",
                step_type=StepType.CLI_COMMAND,
                description=f"Validate created schema: {schema_name}",
                command=f"plc-control-loop schema validate --name {schema_name}",
                dependencies=[f"{task_id}_create_schema"],
                safety_level=1
            )
        ]
    elif operation == "delete":
        steps = [
            TaskStep(
                step_id=f"{task_id}_safety_check",
                step_type=StepType.SAFETY_CHECK,
                description="Perform safety check before deletion",
                command="safety_check",
                parameters={"type": "system_resources"},
                safety_level=3
            ),
            TaskStep(
                step_id=f"{task_id}_user_confirm",
                step_type=StepType.USER_CONFIRMATION,
                description=f"Confirm deletion of schema: {schema_name}",
                command="user_confirmation",
                parameters={"message": f"Are you sure you want to delete schema {schema_name}?"},
                dependencies=[f"{task_id}_safety_check"],
                safety_level=4,
                confirmation_required=True
            ),
            TaskStep(
                step_id=f"{task_id}_delete_schema",
                step_type=StepType.CLI_COMMAND,
                description=f"Delete schema: {schema_name}",
                command=f"plc-control-loop schema delete --name {schema_name} --force",
                dependencies=[f"{task_id}_user_confirm"],
                safety_level=4,
                rollback_command=f"plc-control-loop schema restore --name {schema_name}"
            )
        ]
        
    return TaskPlan(
        task_id=task_id,
        name=f"Schema {operation.title()}: {schema_name}",
        description=f"{operation.title()} schema {schema_name}",
        original_request=f"{operation} schema {schema_name}",
        steps=steps,
        priority=TaskPriority.NORMAL,
        estimated_duration=timedelta(minutes=5),
        safety_score=3.0 if operation == "delete" else 2.0,
        requires_approval=operation == "delete"
    )

# Export main classes and functions
__all__ = [
    "TaskStatus", "TaskPriority", "StepType",
    "TaskStep", "TaskPlan", "ExecutionContext",
    "ProgressTracker", "ErrorRecovery", "TaskExecutor",
    "create_control_loop_analysis_task", "create_schema_management_task"
]

if __name__ == "__main__":
    # Example usage
    async def main():
        executor = TaskExecutor()
        
        # Create a sample task
        task = create_control_loop_analysis_task("TIC-101", "/path/to/data.csv")
        
        # Execute the task
        success = await executor.execute_task(task)
        print(f"Task execution result: {success}")
        print(f"Final status: {task.status}")
        
    asyncio.run(main()) 