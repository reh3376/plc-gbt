#!/usr/bin/env python3
"""
Core Modular Architecture Components
====================================

Base orchestrator pattern and task analysis framework for Phase 14 implementation.
Following AI Task Orchestrator methodology for systematic problem-solving.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 14.3 - JSON Schema Governance Framework
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
import uuid
import tempfile

@dataclass
class TaskAnalysis:
    """Task analysis framework following AI Task Orchestrator methodology"""
    task_id: str
    complexity: str  # simple, moderate, complex, extensive
    estimated_time: str
    estimated_lines: int
    requirements: List[str]
    risks: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ExecutionStep:
    """Individual execution step tracking"""
    step_name: str
    status: str  # started, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

class ConfigurationManager:
    """Configuration management for orchestrator components"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_data = {}
        self.config_file = config_file
        self._load_configuration()
    
    def _load_configuration(self):
        """Load configuration from file or use defaults"""
        default_config = {
            "system": {
                "project_root": str(Path.cwd()),
                "temp_dir": tempfile.gettempdir(),
                "log_level": "INFO",
                "max_execution_time": 3600,  # 1 hour
                "enable_caching": True
            },
            "validation": {
                "min_success_score": 0.8,
                "enable_safety_checks": True,
                "max_error_threshold": 5
            },
            "performance": {
                "enable_metrics": True,
                "metrics_retention_days": 30,
                "benchmark_iterations": 3
            }
        }
        
        self.config_data = default_config
        
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                self._merge_config(self.config_data, file_config)
            except Exception as e:
                logging.warning(f"Failed to load config file {self.config_file}: {e}")
    
    def _merge_config(self, base: Dict, override: Dict):
        """Recursively merge configuration dictionaries"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

class BaseOrchestrator(ABC):
    """
    Base orchestrator class following AI Task Orchestrator methodology.
    
    Provides systematic problem-solving infrastructure including:
    - Task analysis and complexity assessment
    - Execution tracking and logging
    - Performance metrics collection
    - Configuration management
    - Error handling and validation
    """

    def __init__(self, task_id: str, config_file: Optional[str] = None):
        self.task_id = task_id
        self.session_id = f"{task_id}_{int(time.time())}"
        
        # Configuration management
        self.config = ConfigurationManager(config_file)
        
        # Logging setup
        self.logger = self._setup_logging()
        
        # Execution tracking
        self.execution_steps: List[ExecutionStep] = []
        self.performance_metrics: Dict[str, float] = {}
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Task analysis
        self.task_analysis = self._analyze_task()
        
        # Validation state
        self.validation_errors: List[str] = []
        self.requirements_validated = False
        
        self.logger.info(f"🤖 Initialized {self.__class__.__name__} - Task: {task_id}")
        self.logger.info(f"📊 Complexity: {self.task_analysis.complexity}")

    @abstractmethod
    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        pass

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the main orchestrator functionality"""
        pass

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logger = logging.getLogger(f"{self.__class__.__name__}.{self.task_id}")
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        log_level = self.config.get("system.log_level", "INFO")
        logger.setLevel(getattr(logging, log_level))
        
        return logger

    def validate_requirements(self) -> bool:
        """Validate task requirements before execution"""
        self.logger.info("🔍 Validating requirements...")
        
        # Validate dependencies
        missing_deps = []
        for dep in self.task_analysis.dependencies:
            try:
                if dep.startswith('modules.'):
                    # Module dependency
                    module_name = dep.replace('modules.', '')
                    __import__(f'modules.{module_name}')
                else:
                    # Package dependency
                    __import__(dep)
            except ImportError:
                missing_deps.append(dep)
        
        if missing_deps:
            self.validation_errors.append(f"Missing dependencies: {missing_deps}")
        
        # Validate system requirements
        project_root = Path(self.config.get("system.project_root"))
        if not project_root.exists():
            self.validation_errors.append(f"Project root does not exist: {project_root}")
        
        # Check disk space and permissions
        temp_dir = Path(self.config.get("system.temp_dir"))
        if not temp_dir.exists() or not os.access(temp_dir, os.W_OK):
            self.validation_errors.append(f"Cannot write to temp directory: {temp_dir}")
        
        self.requirements_validated = len(self.validation_errors) == 0
        
        if self.requirements_validated:
            self.logger.info("✅ Requirements validation passed")
        else:
            self.logger.error(f"❌ Requirements validation failed: {self.validation_errors}")
        
        return self.requirements_validated

    def log_execution_step(self, step_name: str, status: str, metadata: Optional[Dict[str, Any]] = None):
        """Log execution step with timing information"""
        current_time = datetime.now()
        
        if status == "started":
            step = ExecutionStep(
                step_name=step_name,
                status=status,
                start_time=current_time,
                metadata=metadata or {}
            )
            self.execution_steps.append(step)
            self.logger.info(f"🚀 Started: {step_name}")
            
        elif status in ["completed", "failed"]:
            # Find the matching started step
            for step in reversed(self.execution_steps):
                if step.step_name == step_name and step.status == "started":
                    step.status = status
                    step.end_time = current_time
                    step.duration = (current_time - step.start_time).total_seconds()
                    if metadata:
                        step.metadata.update(metadata)
                    
                    status_emoji = "✅" if status == "completed" else "❌"
                    self.logger.info(f"{status_emoji} {status.title()}: {step_name} ({step.duration:.2f}s)")
                    break
            else:
                # No matching started step found, create a new one
                step = ExecutionStep(
                    step_name=step_name,
                    status=status,
                    start_time=current_time,
                    end_time=current_time,
                    duration=0.0,
                    metadata=metadata or {}
                )
                self.execution_steps.append(step)

    def add_performance_metric(self, metric_name: str, value: float):
        """Add performance metric for tracking"""
        self.performance_metrics[metric_name] = value
        self.logger.debug(f"📊 Metric: {metric_name} = {value}")

    def log_error(self, message: str, exception: Optional[Exception] = None):
        """Log error with context"""
        if exception:
            self.logger.error(f"❌ {message}: {str(exception)}")
        else:
            self.logger.error(f"❌ {message}")
        
        # Add to validation errors for reporting
        error_msg = f"{message}: {str(exception)}" if exception else message
        self.validation_errors.append(error_msg)

    def get_execution_summary(self) -> Dict[str, Any]:
        """Get comprehensive execution summary"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate step statistics
        completed_steps = [s for s in self.execution_steps if s.status == "completed"]
        failed_steps = [s for s in self.execution_steps if s.status == "failed"]
        
        return {
            "session_id": self.session_id,
            "task_analysis": asdict(self.task_analysis),
            "execution_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration": total_duration,
                "steps_completed": len(completed_steps),
                "steps_failed": len(failed_steps),
                "success_rate": len(completed_steps) / max(len(self.execution_steps), 1)
            },
            "performance_metrics": self.performance_metrics,
            "validation_errors": self.validation_errors,
            "requirements_validated": self.requirements_validated,
            "execution_steps": [asdict(step) for step in self.execution_steps]
        }

    def cleanup(self):
        """Cleanup resources and finalize execution"""
        try:
            self.logger.info("🧹 Cleaning up resources...")
            
            # Save execution summary
            summary = self.get_execution_summary()
            summary_file = Path(f"execution_summary_{self.session_id}.json")
            
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            self.logger.info(f"📋 Execution summary saved: {summary_file}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Cleanup failed: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup"""
        self.cleanup()
        
        if exc_type:
            self.log_error(f"Exception during execution: {exc_val}", exc_val)
            return False
        
        return True 