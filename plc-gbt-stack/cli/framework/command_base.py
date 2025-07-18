#!/usr/bin/env python3
"""
🖥️ CLI Framework - Base Command Classes

Provides base classes for CLI commands with consistent error handling,
logging, and async support.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.1 - Core CLI Infrastructure
"""

import asyncio
import time
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from datetime import datetime

import click
from rich.console import Console

console = Console()
logger = logging.getLogger(__name__)

class BaseCommand(ABC):
    """Base class for CLI commands with common functionality"""
    
    def __init__(self, cli_context):
        self.cli_context = cli_context
        self.config = cli_context.config
        self.start_time = time.time()
        
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute the command"""
        pass
    
    def log_start(self, operation: str, **params):
        """Log command start"""
        if self.config.verbose:
            console.print(f"[dim]Starting {operation}...[/dim]")
        logger.info(f"Command started: {operation}", extra={"params": params})
    
    def log_success(self, operation: str, result: Any = None):
        """Log successful completion"""
        duration = time.time() - self.start_time
        self.cli_context.log_operation(operation, duration)
        
        if self.config.verbose:
            console.print(f"[green]✅ {operation} completed in {duration:.3f}s[/green]")
        
        logger.info(f"Command completed: {operation}", extra={
            "duration": duration,
            "result_type": type(result).__name__ if result else None
        })
    
    def log_error(self, operation: str, error: Exception):
        """Log error"""
        duration = time.time() - self.start_time
        error_msg = f"{operation} failed: {str(error)}"
        
        self.cli_context.add_error(error_msg)
        console.print(f"[red]❌ {error_msg}[/red]")
        
        logger.error(f"Command failed: {operation}", extra={
            "duration": duration,
            "error": str(error),
            "error_type": type(error).__name__
        })

class AsyncCommand(BaseCommand):
    """Base class for async CLI commands"""
    
    @abstractmethod
    async def execute_async(self, *args, **kwargs) -> Any:
        """Execute the async command"""
        pass
    
    def execute(self, *args, **kwargs) -> Any:
        """Sync wrapper for async execution"""
        return asyncio.run(self.execute_async(*args, **kwargs))

class SchemaCommand(BaseCommand):
    """Base class for schema-related commands"""
    
    def __init__(self, cli_context):
        super().__init__(cli_context)
        self.schema_registry_path = cli_context.config.default_schema_registry
        
    def validate_schema_exists(self, schema_id: str) -> bool:
        """Validate that a schema exists"""
        # TODO: Implement actual schema validation in Phase 21.2
        return True
    
    def get_schema_path(self, schema_id: str) -> str:
        """Get path to schema file"""
        return f"{self.schema_registry_path}/{schema_id}.json"

class InstanceCommand(BaseCommand):
    """Base class for instance-related commands"""
    
    def __init__(self, cli_context):
        super().__init__(cli_context)
        self.instances_dir = cli_context.config.default_instances_dir
        
    def validate_instance_exists(self, instance_id: str) -> bool:
        """Validate that an instance exists"""
        # TODO: Implement actual instance validation in Phase 21.3
        return True
    
    def get_instance_path(self, instance_id: str) -> str:
        """Get path to instance file"""
        return f"{self.instances_dir}/{instance_id}.json"

def command_wrapper(command_class):
    """Decorator to wrap command classes with consistent execution"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            ctx = click.get_current_context()
            cli_context = ctx.obj
            
            command = command_class(cli_context)
            operation_name = func.__name__
            
            try:
                command.log_start(operation_name, **kwargs)
                result = command.execute(*args, **kwargs)
                command.log_success(operation_name, result)
                return result
            except Exception as e:
                command.log_error(operation_name, e)
                raise
        
        return wrapper
    return decorator 