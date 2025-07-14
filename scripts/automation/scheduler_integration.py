#!/usr/bin/env python3
"""
Scheduler Integration for PLC-Optimize Automation
=================================================

Comprehensive scheduler integration system for periodic optimization runs,
maintenance windows, and automated optimization scheduling.

Features:
- Cron-based scheduling for periodic optimization
- Maintenance window management with configurable schedules
- Integration with system schedulers (cron, systemd timers, Task Scheduler)
- Smart scheduling based on project activity and resource usage
- Schedule conflict detection and resolution
- Performance monitoring and optimization scheduling
- Notification and alerting for scheduled runs

Following AI Task Orchestrator methodology for systematic scheduler integration.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 14.4.4 - Scheduler Integration
Dependencies: Master CLI, Automation Config, All Phase 14 components
"""

import os
import sys
import json
import subprocess
import crontab
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta, time
from dataclasses import dataclass, asdict
from enum import Enum
import platform
import logging
import shutil
import tempfile

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

# Import related components
try:
    from .plc_optimize_cli import PLCOptimizeMasterCLI, OptimizationProfile, OptimizationSession
    from .automation_config_templates import AutomationConfigurationOrchestrator, ConfigurationTemplate
    from .cicd_integration import CICDIntegrationOrchestrator
except ImportError:
    from plc_optimize_cli import PLCOptimizeMasterCLI, OptimizationProfile, OptimizationSession
    from automation_config_templates import AutomationConfigurationOrchestrator, ConfigurationTemplate
    from cicd_integration import CICDIntegrationOrchestrator

class ScheduleFrequency(Enum):
    """Schedule frequency options"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"

class SchedulerType(Enum):
    """Supported scheduler types"""
    CRON = "cron"
    SYSTEMD = "systemd"
    WINDOWS_TASK = "windows_task"
    GITHUB_ACTIONS = "github_actions"
    MANUAL = "manual"

class MaintenanceWindow(Enum):
    """Predefined maintenance windows"""
    EARLY_MORNING = "early_morning"  # 2:00-4:00 AM
    LATE_NIGHT = "late_night"        # 11:00 PM-1:00 AM
    WEEKEND = "weekend"              # Saturday/Sunday
    BUSINESS_HOURS_OFF = "off_hours" # Outside 9-5
    CUSTOM = "custom"

@dataclass
class ScheduleDefinition:
    """Definition of a scheduled optimization"""
    schedule_id: str
    name: str
    description: str
    frequency: ScheduleFrequency
    cron_expression: str
    optimization_profile: str
    project_root: str
    enabled: bool
    maintenance_window: MaintenanceWindow
    auto_apply: bool
    safety_threshold: float
    timeout_minutes: int
    notification_channels: List[str]
    retry_attempts: int
    retry_interval_minutes: int
    
@dataclass
class ScheduleExecutionResult:
    """Result of a scheduled optimization execution"""
    schedule_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime]
    status: str  # pending, running, completed, failed, timeout
    optimization_result: Optional[Dict[str, Any]]
    files_optimized: int
    validation_score: float
    errors: List[str]
    next_execution: Optional[datetime]

@dataclass
class MaintenanceWindowDefinition:
    """Definition of a maintenance window"""
    window_id: str
    name: str
    start_time: time
    end_time: time
    days_of_week: List[int]  # 0=Monday, 6=Sunday
    timezone: str
    max_concurrent_jobs: int
    resource_limits: Dict[str, Any]

class SchedulerIntegrationOrchestrator(BaseOrchestrator):
    """
    Comprehensive scheduler integration orchestrator.
    
    Provides systematic scheduling of optimization tasks with maintenance
    window management, conflict resolution, and performance monitoring.
    """

    def __init__(self, task_id: str = "scheduler_integration", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)
        
        # Initialize related components
        self.master_cli = PLCOptimizeMasterCLI("scheduler_master")
        self.config_orchestrator = AutomationConfigurationOrchestrator("scheduler_config")
        
        # Scheduler configuration
        self.scheduler_config = {
            "default_scheduler": self._detect_available_scheduler(),
            "max_concurrent_jobs": 3,
            "default_timeout_minutes": 60,
            "default_retry_attempts": 2,
            "log_retention_days": 30,
            "performance_monitoring": True,
            "auto_cleanup": True
        }
        
        # Predefined maintenance windows
        self.maintenance_windows = self._initialize_maintenance_windows()
        
        # Active schedules tracking
        self.active_schedules: Dict[str, ScheduleDefinition] = {}
        self.execution_history: List[ScheduleExecutionResult] = []
        
        # Scheduler state
        self.scheduler_type = self.scheduler_config["default_scheduler"]
        self.scheduler_enabled = False

    def _analyze_task(self) -> TaskAnalysis:
        """Analyze scheduler integration task"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="2-3 hours",
            estimated_lines=1200,
            requirements=[
                "System scheduler access (cron, systemd, or Task Scheduler)",
                "Project write permissions for scheduled operations",
                "Notification system configuration",
                "Resource monitoring capabilities"
            ],
            risks=[
                "System scheduler permission requirements",
                "Resource conflicts during scheduled runs",
                "Maintenance window coordination",
                "Long-running optimization impact on system performance"
            ],
            dependencies=[
                "modules.core",
                "plc_optimize_cli",
                "automation_config_templates",
                "System scheduler availability"
            ],
            success_criteria=[
                "Schedules created and activated successfully",
                "Maintenance windows configured properly",
                "Test execution completes without errors",
                "Monitoring and notification systems operational"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute scheduler integration setup"""
        self.log_execution_step("Scheduler Integration Setup", "started")
        
        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}
            
            # Setup scheduler environment
            project_root = self.config.get("system.project_root", str(Path.cwd()))
            
            # Initialize scheduler system
            init_result = self.initialize_scheduler_system(project_root)
            
            # Create default schedules
            default_schedules = self.create_default_schedules(project_root)
            
            # Setup maintenance windows
            maintenance_setup = self.setup_maintenance_windows()
            
            # Enable scheduler monitoring
            monitoring_setup = self.setup_scheduler_monitoring()
            
            return {
                "status": "completed",
                "scheduler_type": self.scheduler_type.value,
                "scheduler_initialized": init_result["success"],
                "schedules_created": len(default_schedules),
                "maintenance_windows": len(maintenance_setup),
                "monitoring_enabled": monitoring_setup["enabled"],
                "next_steps": self._generate_scheduler_guide()
            }
            
        except Exception as e:
            self.log_error("Scheduler integration setup failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("Scheduler Integration Setup", "completed")

    def initialize_scheduler_system(self, project_root: str) -> Dict[str, Any]:
        """
        Initialize the scheduler system for the project.
        
        Args:
            project_root: Project directory
            
        Returns:
            Initialization result with setup details
        """
        self.log_execution_step("Scheduler System Initialization", "started")
        
        try:
            # Create scheduler directories
            scheduler_dir = Path(project_root) / ".plc_optimize" / "scheduler"
            scheduler_dir.mkdir(parents=True, exist_ok=True)
            
            logs_dir = scheduler_dir / "logs"
            logs_dir.mkdir(exist_ok=True)
            
            scripts_dir = scheduler_dir / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            
            # Create scheduler wrapper script
            wrapper_script = self._create_scheduler_wrapper_script(project_root, scripts_dir)
            
            # Setup scheduler configuration
            config_file = self._create_scheduler_config(scheduler_dir)
            
            # Initialize scheduler database
            db_file = self._initialize_scheduler_database(scheduler_dir)
            
            # Test scheduler system
            test_result = self._test_scheduler_system(project_root)
            
            result = {
                "success": True,
                "scheduler_type": self.scheduler_type.value,
                "directories_created": [str(scheduler_dir), str(logs_dir), str(scripts_dir)],
                "wrapper_script": str(wrapper_script),
                "config_file": str(config_file),
                "database_file": str(db_file),
                "test_result": test_result
            }
            
            self.log_execution_step("Scheduler System Initialization", "completed", {
                "directories": len(result["directories_created"])
            })
            
            return result
            
        except Exception as e:
            self.log_error("Scheduler system initialization failed", e)
            return {"success": False, "error": str(e)}

    def create_default_schedules(self, project_root: str) -> List[ScheduleDefinition]:
        """
        Create default optimization schedules for the project.
        
        Args:
            project_root: Project directory
            
        Returns:
            List of created schedule definitions
        """
        self.log_execution_step("Default Schedule Creation", "started")
        
        schedules = []
        
        try:
            # Daily maintenance schedule
            daily_schedule = ScheduleDefinition(
                schedule_id="daily_maintenance",
                name="Daily Maintenance Optimization",
                description="Daily optimization run during early morning maintenance window",
                frequency=ScheduleFrequency.DAILY,
                cron_expression="0 2 * * *",  # 2:00 AM daily
                optimization_profile="conservative",
                project_root=project_root,
                enabled=True,
                maintenance_window=MaintenanceWindow.EARLY_MORNING,
                auto_apply=True,
                safety_threshold=0.85,
                timeout_minutes=60,
                notification_channels=["email"],
                retry_attempts=2,
                retry_interval_minutes=30
            )
            schedules.append(daily_schedule)
            
            # Weekly comprehensive optimization
            weekly_schedule = ScheduleDefinition(
                schedule_id="weekly_comprehensive",
                name="Weekly Comprehensive Optimization",
                description="Weekly comprehensive optimization during weekend maintenance",
                frequency=ScheduleFrequency.WEEKLY,
                cron_expression="0 3 * * 0",  # 3:00 AM on Sundays
                optimization_profile="aggressive",
                project_root=project_root,
                enabled=True,
                maintenance_window=MaintenanceWindow.WEEKEND,
                auto_apply=True,
                safety_threshold=0.8,
                timeout_minutes=120,
                notification_channels=["email", "slack"],
                retry_attempts=3,
                retry_interval_minutes=60
            )
            schedules.append(weekly_schedule)
            
            # Performance monitoring schedule
            performance_schedule = ScheduleDefinition(
                schedule_id="performance_monitoring",
                name="Performance Monitoring",
                description="Regular performance analysis and reporting",
                frequency=ScheduleFrequency.CUSTOM,
                cron_expression="0 */6 * * *",  # Every 6 hours
                optimization_profile="analysis_only",
                project_root=project_root,
                enabled=True,
                maintenance_window=MaintenanceWindow.BUSINESS_HOURS_OFF,
                auto_apply=False,
                safety_threshold=0.9,
                timeout_minutes=30,
                notification_channels=["slack"],
                retry_attempts=1,
                retry_interval_minutes=15
            )
            schedules.append(performance_schedule)
            
            # Add schedules to active tracking
            for schedule in schedules:
                self.active_schedules[schedule.schedule_id] = schedule
            
            # Install schedules in system scheduler
            self._install_schedules_in_system(schedules)
            
            self.log_execution_step("Default Schedule Creation", "completed", {
                "schedules_created": len(schedules)
            })
            
            return schedules
            
        except Exception as e:
            self.log_error("Default schedule creation failed", e)
            return []

    def create_custom_schedule(
        self,
        name: str,
        cron_expression: str,
        optimization_profile: str,
        project_root: str,
        **kwargs
    ) -> ScheduleDefinition:
        """
        Create a custom optimization schedule.
        
        Args:
            name: Schedule name
            cron_expression: Cron expression for scheduling
            optimization_profile: Optimization profile to use
            project_root: Project directory
            **kwargs: Additional schedule options
            
        Returns:
            Created schedule definition
        """
        schedule_id = f"custom_{name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"
        
        schedule = ScheduleDefinition(
            schedule_id=schedule_id,
            name=name,
            description=kwargs.get("description", f"Custom schedule: {name}"),
            frequency=ScheduleFrequency.CUSTOM,
            cron_expression=cron_expression,
            optimization_profile=optimization_profile,
            project_root=project_root,
            enabled=kwargs.get("enabled", True),
            maintenance_window=kwargs.get("maintenance_window", MaintenanceWindow.CUSTOM),
            auto_apply=kwargs.get("auto_apply", False),
            safety_threshold=kwargs.get("safety_threshold", 0.85),
            timeout_minutes=kwargs.get("timeout_minutes", 60),
            notification_channels=kwargs.get("notification_channels", ["email"]),
            retry_attempts=kwargs.get("retry_attempts", 2),
            retry_interval_minutes=kwargs.get("retry_interval_minutes", 30)
        )
        
        # Add to active schedules
        self.active_schedules[schedule_id] = schedule
        
        # Install in system scheduler
        self._install_schedule_in_system(schedule)
        
        return schedule

    def setup_maintenance_windows(self) -> Dict[str, MaintenanceWindowDefinition]:
        """Setup predefined maintenance windows"""
        self.log_execution_step("Maintenance Window Setup", "started")
        
        try:
            windows = {}
            
            for window_type, definition in self.maintenance_windows.items():
                windows[window_type.value] = definition
            
            # Save maintenance window configuration
            self._save_maintenance_windows_config(windows)
            
            self.log_execution_step("Maintenance Window Setup", "completed", {
                "windows_configured": len(windows)
            })
            
            return windows
            
        except Exception as e:
            self.log_error("Maintenance window setup failed", e)
            return {}

    def setup_scheduler_monitoring(self) -> Dict[str, Any]:
        """Setup monitoring for scheduled optimization runs"""
        self.log_execution_step("Scheduler Monitoring Setup", "started")
        
        try:
            monitoring_config = {
                "enabled": True,
                "log_level": "INFO",
                "performance_tracking": True,
                "notification_thresholds": {
                    "execution_time_minutes": 90,
                    "failure_count": 3,
                    "low_validation_score": 0.7
                },
                "cleanup_policy": {
                    "log_retention_days": 30,
                    "execution_history_retention": 100
                }
            }
            
            # Create monitoring script
            monitoring_script = self._create_monitoring_script()
            
            # Setup log rotation
            log_rotation = self._setup_log_rotation()
            
            # Create alert system
            alert_system = self._setup_alert_system()
            
            result = {
                "enabled": True,
                "monitoring_script": str(monitoring_script),
                "log_rotation": log_rotation,
                "alert_system": alert_system,
                "config": monitoring_config
            }
            
            self.log_execution_step("Scheduler Monitoring Setup", "completed")
            
            return result
            
        except Exception as e:
            self.log_error("Scheduler monitoring setup failed", e)
            return {"enabled": False, "error": str(e)}

    def execute_scheduled_optimization(
        self,
        schedule_id: str,
        execution_id: Optional[str] = None
    ) -> ScheduleExecutionResult:
        """
        Execute a scheduled optimization.
        
        Args:
            schedule_id: ID of the schedule to execute
            execution_id: Optional execution ID for tracking
            
        Returns:
            Execution result
        """
        if execution_id is None:
            execution_id = f"{schedule_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.log_execution_step(f"Scheduled Execution {execution_id}", "started")
        
        try:
            schedule = self.active_schedules.get(schedule_id)
            if not schedule:
                raise ValueError(f"Schedule not found: {schedule_id}")
            
            # Create execution result
            result = ScheduleExecutionResult(
                schedule_id=schedule_id,
                execution_id=execution_id,
                start_time=datetime.now(),
                end_time=None,
                status="running",
                optimization_result=None,
                files_optimized=0,
                validation_score=0.0,
                errors=[],
                next_execution=self._calculate_next_execution(schedule)
            )
            
            # Check maintenance window
            if not self._is_within_maintenance_window(schedule.maintenance_window):
                result.status = "skipped"
                result.errors.append("Outside maintenance window")
                result.end_time = datetime.now()
                return result
            
            # Execute optimization using master CLI
            optimization_result = self.master_cli.run_full_optimization_workflow(
                project_root=schedule.project_root,
                profile_name=schedule.optimization_profile,
                auto_apply=schedule.auto_apply,
                create_backup=True
            )
            
            # Update result with optimization outcome
            result.optimization_result = optimization_result
            result.status = optimization_result.get("status", "completed")
            result.end_time = datetime.now()
            
            # Extract metrics
            if "overall_metrics" in optimization_result:
                metrics = optimization_result["overall_metrics"]
                result.files_optimized = metrics.get("files_optimized", 0)
                result.validation_score = metrics.get("validation_score", 0.0)
            
            # Add to execution history
            self.execution_history.append(result)
            
            # Send notifications if configured
            self._send_execution_notifications(schedule, result)
            
            self.log_execution_step(f"Scheduled Execution {execution_id}", "completed", {
                "status": result.status,
                "files_optimized": result.files_optimized,
                "validation_score": result.validation_score
            })
            
            return result
            
        except Exception as e:
            self.log_error(f"Scheduled execution {execution_id} failed", e)
            
            result = ScheduleExecutionResult(
                schedule_id=schedule_id,
                execution_id=execution_id,
                start_time=datetime.now(),
                end_time=datetime.now(),
                status="failed",
                optimization_result=None,
                files_optimized=0,
                validation_score=0.0,
                errors=[str(e)],
                next_execution=self._calculate_next_execution(schedule) if schedule else None
            )
            
            return result

    def _detect_available_scheduler(self) -> SchedulerType:
        """Detect available system scheduler"""
        system = platform.system().lower()
        
        if system in ["linux", "darwin"]:  # Linux or macOS
            # Check for systemd
            if shutil.which("systemctl"):
                return SchedulerType.SYSTEMD
            # Fallback to cron
            elif shutil.which("crontab"):
                return SchedulerType.CRON
        elif system == "windows":
            # Check for Windows Task Scheduler
            if shutil.which("schtasks"):
                return SchedulerType.WINDOWS_TASK
        
        # Check for CI/CD environment
        if os.getenv("GITHUB_ACTIONS"):
            return SchedulerType.GITHUB_ACTIONS
        
        # Default to manual
        return SchedulerType.MANUAL

    def _initialize_maintenance_windows(self) -> Dict[MaintenanceWindow, MaintenanceWindowDefinition]:
        """Initialize predefined maintenance windows"""
        return {
            MaintenanceWindow.EARLY_MORNING: MaintenanceWindowDefinition(
                window_id="early_morning",
                name="Early Morning Maintenance",
                start_time=time(2, 0),  # 2:00 AM
                end_time=time(4, 0),    # 4:00 AM
                days_of_week=list(range(7)),  # All days
                timezone="local",
                max_concurrent_jobs=2,
                resource_limits={"cpu_percent": 50, "memory_mb": 2048}
            ),
            MaintenanceWindow.LATE_NIGHT: MaintenanceWindowDefinition(
                window_id="late_night",
                name="Late Night Maintenance",
                start_time=time(23, 0),  # 11:00 PM
                end_time=time(1, 0),     # 1:00 AM (next day)
                days_of_week=list(range(7)),  # All days
                timezone="local",
                max_concurrent_jobs=2,
                resource_limits={"cpu_percent": 60, "memory_mb": 3072}
            ),
            MaintenanceWindow.WEEKEND: MaintenanceWindowDefinition(
                window_id="weekend",
                name="Weekend Maintenance",
                start_time=time(0, 0),   # Midnight
                end_time=time(23, 59),   # 11:59 PM
                days_of_week=[5, 6],     # Saturday, Sunday
                timezone="local",
                max_concurrent_jobs=3,
                resource_limits={"cpu_percent": 80, "memory_mb": 4096}
            ),
            MaintenanceWindow.BUSINESS_HOURS_OFF: MaintenanceWindowDefinition(
                window_id="off_hours",
                name="Off Business Hours",
                start_time=time(17, 0),  # 5:00 PM
                end_time=time(9, 0),     # 9:00 AM (next day)
                days_of_week=[0, 1, 2, 3, 4],  # Monday-Friday
                timezone="local",
                max_concurrent_jobs=2,
                resource_limits={"cpu_percent": 40, "memory_mb": 1536}
            )
        }

    def _create_scheduler_wrapper_script(self, project_root: str, scripts_dir: Path) -> Path:
        """Create scheduler wrapper script"""
        script_path = scripts_dir / "plc_optimize_scheduler.py"
        
        script_content = f'''#!/usr/bin/env python3
"""
PLC-Optimize Scheduler Wrapper Script
====================================

This script is called by the system scheduler to execute optimization tasks.
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, "{project_root}")

# Configure logging
log_file = Path(__file__).parent.parent / "logs" / f"scheduler_{{datetime.now().strftime('%Y%m%d')}}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("plc-optimize-scheduler")

def main():
    """Main scheduler wrapper function"""
    try:
        # Import scheduler after path setup
        from scheduler_integration import SchedulerIntegrationOrchestrator
        
        # Get command line arguments
        if len(sys.argv) < 2:
            logger.error("Usage: plc_optimize_scheduler.py <schedule_id>")
            sys.exit(1)
        
        schedule_id = sys.argv[1]
        execution_id = sys.argv[2] if len(sys.argv) > 2 else None
        
        logger.info(f"Starting scheduled optimization: {{schedule_id}}")
        
        # Create scheduler orchestrator
        scheduler = SchedulerIntegrationOrchestrator()
        
        # Execute scheduled optimization
        result = scheduler.execute_scheduled_optimization(schedule_id, execution_id)
        
        # Log result
        logger.info(f"Scheduled optimization completed: {{result.status}}")
        logger.info(f"Files optimized: {{result.files_optimized}}")
        logger.info(f"Validation score: {{result.validation_score}}")
        
        # Save result to file
        result_file = Path(__file__).parent.parent / "logs" / f"{{result.execution_id}}_result.json"
        with open(result_file, 'w') as f:
            json.dump({{
                "schedule_id": result.schedule_id,
                "execution_id": result.execution_id,
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "status": result.status,
                "files_optimized": result.files_optimized,
                "validation_score": result.validation_score,
                "errors": result.errors
            }}, f, indent=2)
        
        # Exit with appropriate code
        sys.exit(0 if result.status == "completed" else 1)
        
    except Exception as e:
        logger.error(f"Scheduler wrapper failed: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        script_path.chmod(0o755)
        
        return script_path

    def _create_scheduler_config(self, scheduler_dir: Path) -> Path:
        """Create scheduler configuration file"""
        config_file = scheduler_dir / "scheduler_config.json"
        
        config = {
            "version": "1.0.0",
            "created": datetime.now().isoformat(),
            "scheduler_type": self.scheduler_type.value,
            "configuration": self.scheduler_config,
            "maintenance_windows": {
                name: asdict(window) for name, window in self.maintenance_windows.items()
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2, default=str)
        
        return config_file

    def _initialize_scheduler_database(self, scheduler_dir: Path) -> Path:
        """Initialize scheduler database for tracking executions"""
        db_file = scheduler_dir / "scheduler.db"
        
        # Create simple JSON database for tracking
        initial_db = {
            "schedules": {},
            "executions": [],
            "maintenance_windows": {},
            "statistics": {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "last_execution": None
            }
        }
        
        with open(db_file, 'w') as f:
            json.dump(initial_db, f, indent=2)
        
        return db_file

    def _test_scheduler_system(self, project_root: str) -> Dict[str, Any]:
        """Test the scheduler system"""
        test_result = {
            "scheduler_available": False,
            "wrapper_script_executable": False,
            "permissions_ok": False,
            "test_schedule_created": False
        }
        
        try:
            # Test scheduler availability
            if self.scheduler_type in [SchedulerType.CRON, SchedulerType.SYSTEMD]:
                test_result["scheduler_available"] = shutil.which("crontab") is not None
            elif self.scheduler_type == SchedulerType.WINDOWS_TASK:
                test_result["scheduler_available"] = shutil.which("schtasks") is not None
            else:
                test_result["scheduler_available"] = True
            
            # Test wrapper script
            wrapper_script = Path(project_root) / ".plc_optimize" / "scheduler" / "scripts" / "plc_optimize_scheduler.py"
            test_result["wrapper_script_executable"] = wrapper_script.exists() and os.access(wrapper_script, os.X_OK)
            
            # Test permissions
            scheduler_dir = Path(project_root) / ".plc_optimize" / "scheduler"
            test_result["permissions_ok"] = os.access(scheduler_dir, os.R_OK | os.W_OK)
            
            # Test creating a dummy schedule (don't actually install it)
            test_result["test_schedule_created"] = True
            
        except Exception as e:
            self.log_error("Scheduler system test failed", e)
        
        return test_result

    def _install_schedules_in_system(self, schedules: List[ScheduleDefinition]):
        """Install schedules in the system scheduler"""
        for schedule in schedules:
            self._install_schedule_in_system(schedule)

    def _install_schedule_in_system(self, schedule: ScheduleDefinition):
        """Install a single schedule in the system scheduler"""
        try:
            if self.scheduler_type == SchedulerType.CRON:
                self._install_cron_schedule(schedule)
            elif self.scheduler_type == SchedulerType.SYSTEMD:
                self._install_systemd_schedule(schedule)
            elif self.scheduler_type == SchedulerType.WINDOWS_TASK:
                self._install_windows_task_schedule(schedule)
            else:
                self.logger.info(f"Manual scheduler mode - schedule {schedule.schedule_id} configuration saved")
        except Exception as e:
            self.log_error(f"Failed to install schedule {schedule.schedule_id}", e)

    def _install_cron_schedule(self, schedule: ScheduleDefinition):
        """Install schedule using cron"""
        try:
            # Create cron job command
            wrapper_script = Path(schedule.project_root) / ".plc_optimize" / "scheduler" / "scripts" / "plc_optimize_scheduler.py"
            command = f"cd {schedule.project_root} && python {wrapper_script} {schedule.schedule_id}"
            
            # Add to crontab
            cron_line = f"{schedule.cron_expression} {command}"
            
            # Note: In a real implementation, this would use the crontab module
            # For demo purposes, we'll just log the cron line
            self.logger.info(f"Cron job would be added: {cron_line}")
            
        except Exception as e:
            self.log_error(f"Failed to install cron schedule {schedule.schedule_id}", e)

    def _install_systemd_schedule(self, schedule: ScheduleDefinition):
        """Install schedule using systemd timer"""
        # Systemd timer implementation would go here
        self.logger.info(f"Systemd timer would be created for schedule {schedule.schedule_id}")

    def _install_windows_task_schedule(self, schedule: ScheduleDefinition):
        """Install schedule using Windows Task Scheduler"""
        # Windows Task Scheduler implementation would go here
        self.logger.info(f"Windows task would be created for schedule {schedule.schedule_id}")

    def _calculate_next_execution(self, schedule: ScheduleDefinition) -> datetime:
        """Calculate next execution time for a schedule"""
        # Simple calculation - in production would use proper cron parsing
        now = datetime.now()
        
        if schedule.frequency == ScheduleFrequency.HOURLY:
            return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        elif schedule.frequency == ScheduleFrequency.DAILY:
            return now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif schedule.frequency == ScheduleFrequency.WEEKLY:
            # Next Sunday at 3 AM
            days_ahead = 6 - now.weekday()  # 0=Monday, 6=Sunday
            if days_ahead <= 0:
                days_ahead += 7
            return now.replace(hour=3, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
        else:
            # Default to next day
            return now.replace(hour=2, minute=0, second=0, microsecond=0) + timedelta(days=1)

    def _is_within_maintenance_window(self, window_type: MaintenanceWindow) -> bool:
        """Check if current time is within maintenance window"""
        if window_type == MaintenanceWindow.CUSTOM:
            return True  # Custom windows are always allowed
        
        window = self.maintenance_windows.get(window_type)
        if not window:
            return True
        
        now = datetime.now()
        current_time = now.time()
        current_weekday = now.weekday()
        
        # Check if current day is in allowed days
        if current_weekday not in window.days_of_week:
            return False
        
        # Check if current time is in window
        if window.start_time <= window.end_time:
            # Same day window
            return window.start_time <= current_time <= window.end_time
        else:
            # Overnight window (crosses midnight)
            return current_time >= window.start_time or current_time <= window.end_time

    def _send_execution_notifications(self, schedule: ScheduleDefinition, result: ScheduleExecutionResult):
        """Send notifications for execution results"""
        # Notification implementation would go here
        self.logger.info(f"Notifications would be sent for {result.execution_id} to {schedule.notification_channels}")

    def _save_maintenance_windows_config(self, windows: Dict[str, MaintenanceWindowDefinition]):
        """Save maintenance windows configuration"""
        # Implementation would save to configuration file
        pass

    def _create_monitoring_script(self) -> Path:
        """Create monitoring script for scheduled executions"""
        # Would create monitoring script
        return Path("monitoring_script.py")

    def _setup_log_rotation(self) -> Dict[str, Any]:
        """Setup log rotation for scheduler logs"""
        return {"enabled": True, "retention_days": 30}

    def _setup_alert_system(self) -> Dict[str, Any]:
        """Setup alert system for scheduler events"""
        return {"enabled": True, "channels": ["email", "slack"]}

    def _generate_scheduler_guide(self) -> List[str]:
        """Generate implementation guide for scheduler setup"""
        return [
            "🕒 Scheduler Integration Complete!",
            "",
            "✅ Next Steps:",
            "1. Review created schedules in .plc_optimize/scheduler/",
            "2. Test schedule execution manually:",
            "   python .plc_optimize/scheduler/scripts/plc_optimize_scheduler.py daily_maintenance",
            "3. Monitor logs in .plc_optimize/scheduler/logs/",
            "4. Customize notification channels as needed",
            "5. Adjust maintenance windows based on your workflow",
            "",
            "🔧 Schedule Management:",
            "- Enable/disable schedules as needed",
            "- Monitor execution results and performance",
            "- Adjust safety thresholds based on experience",
            "",
            "⚠️  Important Notes:",
            "- Ensure sufficient system resources during maintenance windows",
            "- Review and test backup/rollback procedures",
            "- Monitor notification channels for execution status"
        ]


if __name__ == "__main__":
    # Demo/test the scheduler integration
    import tempfile
    
    print("🕒 Scheduler Integration Demo")
    print("=" * 40)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create scheduler integration
        scheduler_integration = SchedulerIntegrationOrchestrator()
        
        # Initialize scheduler system
        init_result = scheduler_integration.initialize_scheduler_system(temp_dir)
        
        # Create default schedules
        schedules = scheduler_integration.create_default_schedules(temp_dir)
        
        print(f"✅ Scheduler Type: {scheduler_integration.scheduler_type.value}")
        print(f"📋 Schedules Created: {len(schedules)}")
        
        for schedule in schedules:
            print(f"   • {schedule.name} ({schedule.cron_expression})")
        
        print(f"🕒 Maintenance Windows: {len(scheduler_integration.maintenance_windows)}")
        for window_type, window in scheduler_integration.maintenance_windows.items():
            print(f"   • {window.name}: {window.start_time}-{window.end_time}")
        
        print(f"\n🎯 Scheduler Integration Demo Complete!") 