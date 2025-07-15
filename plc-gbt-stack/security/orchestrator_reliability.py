#!/usr/bin/env python3
"""
Orchestrator Reliability System for PLC-GPT
Phase 15.3: Orchestrator Reliability

This module provides enhanced orchestrator reliability including:
- UUID7 task IDs for better traceability
- Fail-fast subsystem validation
- Offline mode for air-gapped environments
- Enhanced error handling and recovery
- System health monitoring and alerting

Following AI Task Orchestrator methodology for systematic reliability enhancement.
"""

import asyncio
import logging
import json
import time
import hashlib
import struct
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum
import uuid
import random

# System monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logging.warning("psutil not available for system monitoring")

# Network connectivity
try:
    import socket
    import requests
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False
    logging.warning("network libraries not available")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class SubsystemStatus(Enum):
    """Subsystem health status."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    UNKNOWN = "unknown"


class OperationMode(Enum):
    """System operation modes."""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    MAINTENANCE = "maintenance"


@dataclass
class TaskMetadata:
    """Enhanced task metadata with UUID7 and traceability."""
    task_id: str  # UUID7 format
    parent_task_id: Optional[str] = None
    task_type: str = ""
    description: str = ""
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout: Optional[timedelta] = None
    retry_count: int = 0
    max_retries: int = 3
    tags: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    subsystems_required: List[str] = field(default_factory=list)


@dataclass
class SubsystemHealth:
    """Subsystem health information."""
    name: str
    status: SubsystemStatus
    last_check: datetime
    response_time: float
    error_count: int
    error_rate: float
    details: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System performance metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    subsystem_health: Dict[str, SubsystemHealth]


class UUID7Generator:
    """
    UUID7 generator for time-ordered, globally unique task identifiers.
    
    UUID7 provides better performance and traceability than MD5 hashes
    by incorporating timestamp information for natural ordering.
    """
    
    def __init__(self):
        """Initialize UUID7 generator."""
        self.last_timestamp = 0
        self.counter = 0
        
    def generate(self) -> str:
        """
        Generate a UUID7 identifier.
        
        Returns:
            UUID7 string in standard format
        """
        # Get current timestamp in milliseconds
        timestamp = int(time.time() * 1000)
        
        # Handle clock regression or same timestamp
        if timestamp <= self.last_timestamp:
            self.counter += 1
            if self.counter >= 4096:  # 12-bit counter overflow
                time.sleep(0.001)  # Wait 1ms
                timestamp = int(time.time() * 1000)
                self.counter = 0
        else:
            self.counter = 0
        
        self.last_timestamp = timestamp
        
        # Generate UUID7
        # Format: TTTTTTTT-TTTT-7XXX-XXXX-XXXXXXXXXXXX
        # Where T = timestamp, X = random/counter
        
        # 48-bit timestamp (milliseconds since epoch)
        timestamp_high = (timestamp >> 16) & 0xFFFFFFFF
        timestamp_low = timestamp & 0xFFFF
        
        # 12-bit counter + 4-bit version (7)
        counter_and_version = (0x7000) | (self.counter & 0x0FFF)
        
        # 62-bit random + 2-bit variant
        random_part = random.getrandbits(62) | 0x8000000000000000
        
        # Construct UUID
        uuid_int = (timestamp_high << 96) | (timestamp_low << 80) | (counter_and_version << 64) | random_part
        
        # Convert to standard UUID format
        uuid_obj = uuid.UUID(int=uuid_int)
        return str(uuid_obj)
    
    def extract_timestamp(self, uuid7_str: str) -> datetime:
        """
        Extract timestamp from UUID7.
        
        Args:
            uuid7_str: UUID7 string
            
        Returns:
            Datetime object representing creation time
        """
        try:
            uuid_obj = uuid.UUID(uuid7_str)
            uuid_int = uuid_obj.int
            
            # Extract 48-bit timestamp
            timestamp_high = (uuid_int >> 96) & 0xFFFFFFFF
            timestamp_low = (uuid_int >> 80) & 0xFFFF
            timestamp_ms = (timestamp_high << 16) | timestamp_low
            
            return datetime.fromtimestamp(timestamp_ms / 1000.0)
            
        except Exception as e:
            logger.error(f"Failed to extract timestamp from UUID7 {uuid7_str}: {e}")
            return datetime.utcnow()


class SubsystemValidator:
    """
    Subsystem validation and health checking.
    
    Provides fail-fast validation of required subsystems
    before task execution to prevent cascading failures.
    """
    
    def __init__(self):
        """Initialize subsystem validator."""
        self.subsystems: Dict[str, SubsystemHealth] = {}
        self.validation_cache: Dict[str, Tuple[bool, datetime]] = {}
        self.cache_ttl = 30  # 30 seconds
        
        # Register default subsystems
        self._register_default_subsystems()
        
        logger.info("SubsystemValidator initialized")
    
    def _register_default_subsystems(self):
        """Register default PLC-GPT subsystems."""
        default_subsystems = [
            {
                "name": "redis",
                "validator": self._validate_redis,
                "dependencies": []
            },
            {
                "name": "neo4j",
                "validator": self._validate_neo4j,
                "dependencies": []
            },
            {
                "name": "postgresql",
                "validator": self._validate_postgresql,
                "dependencies": []
            },
            {
                "name": "qdrant",
                "validator": self._validate_qdrant,
                "dependencies": []
            },
            {
                "name": "openai_api",
                "validator": self._validate_openai_api,
                "dependencies": []
            },
            {
                "name": "vault",
                "validator": self._validate_vault,
                "dependencies": []
            }
        ]
        
        for subsystem in default_subsystems:
            self.register_subsystem(
                subsystem["name"],
                subsystem["validator"],
                subsystem["dependencies"]
            )
    
    def register_subsystem(self, name: str, validator: Callable, dependencies: List[str] = None):
        """
        Register a subsystem for validation.
        
        Args:
            name: Subsystem name
            validator: Validation function
            dependencies: List of dependent subsystems
        """
        self.subsystems[name] = SubsystemHealth(
            name=name,
            status=SubsystemStatus.UNKNOWN,
            last_check=datetime.utcnow(),
            response_time=0.0,
            error_count=0,
            error_rate=0.0,
            dependencies=dependencies or []
        )
        
        # Store validator function
        setattr(self, f"_validator_{name}", validator)
        
        logger.info(f"✅ Registered subsystem: {name}")
    
    async def validate_subsystem(self, name: str, force_check: bool = False) -> bool:
        """
        Validate a specific subsystem.
        
        Args:
            name: Subsystem name
            force_check: Force validation bypass cache
            
        Returns:
            True if subsystem is healthy, False otherwise
        """
        if name not in self.subsystems:
            logger.error(f"Unknown subsystem: {name}")
            return False
        
        # Check cache first
        if not force_check and name in self.validation_cache:
            cached_result, cached_time = self.validation_cache[name]
            if datetime.utcnow() - cached_time < timedelta(seconds=self.cache_ttl):
                return cached_result
        
        subsystem = self.subsystems[name]
        start_time = time.time()
        
        try:
            # Get validator function
            validator = getattr(self, f"_validator_{name}", None)
            if not validator:
                logger.error(f"No validator found for subsystem: {name}")
                return False
            
            # Run validation
            is_healthy = await validator()
            
            # Update subsystem health
            response_time = time.time() - start_time
            subsystem.last_check = datetime.utcnow()
            subsystem.response_time = response_time
            
            if is_healthy:
                subsystem.status = SubsystemStatus.HEALTHY
                subsystem.error_count = max(0, subsystem.error_count - 1)
            else:
                subsystem.status = SubsystemStatus.FAILED
                subsystem.error_count += 1
            
            # Calculate error rate
            total_checks = max(1, subsystem.error_count + 100)  # Assume 100 successful checks
            subsystem.error_rate = subsystem.error_count / total_checks
            
            # Cache result
            self.validation_cache[name] = (is_healthy, datetime.utcnow())
            
            logger.info(f"{'✅' if is_healthy else '❌'} Subsystem {name}: {subsystem.status.value} ({response_time:.3f}s)")
            return is_healthy
            
        except Exception as e:
            logger.error(f"Subsystem validation failed for {name}: {e}")
            subsystem.status = SubsystemStatus.FAILED
            subsystem.error_count += 1
            return False
    
    async def validate_all_subsystems(self, required_only: bool = False) -> Dict[str, bool]:
        """
        Validate all registered subsystems.
        
        Args:
            required_only: Only validate required subsystems
            
        Returns:
            Dictionary of subsystem validation results
        """
        results = {}
        
        for name in self.subsystems.keys():
            if required_only and name not in ["redis", "neo4j", "postgresql"]:
                continue
            
            results[name] = await self.validate_subsystem(name)
        
        return results
    
    async def fail_fast_validation(self, required_subsystems: List[str]) -> Tuple[bool, List[str]]:
        """
        Perform fail-fast validation of required subsystems.
        
        Args:
            required_subsystems: List of required subsystem names
            
        Returns:
            Tuple of (all_healthy, failed_subsystems)
        """
        failed_subsystems = []
        
        for subsystem_name in required_subsystems:
            is_healthy = await self.validate_subsystem(subsystem_name)
            if not is_healthy:
                failed_subsystems.append(subsystem_name)
        
        all_healthy = len(failed_subsystems) == 0
        
        if not all_healthy:
            logger.error(f"❌ Fail-fast validation failed: {failed_subsystems}")
        else:
            logger.info(f"✅ Fail-fast validation passed for: {required_subsystems}")
        
        return all_healthy, failed_subsystems
    
    # Subsystem validation functions
    async def _validate_redis(self) -> bool:
        """Validate Redis subsystem."""
        try:
            # Simple Redis connectivity check
            import redis
            client = redis.Redis(host='localhost', port=6379, socket_timeout=1)
            client.ping()
            return True
        except Exception as e:
            logger.debug(f"Redis validation failed: {e}")
            return False
    
    async def _validate_neo4j(self) -> bool:
        """Validate Neo4j subsystem."""
        try:
            from neo4j import GraphDatabase
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            with driver.session() as session:
                result = session.run("RETURN 1")
                return result.single()[0] == 1
        except Exception as e:
            logger.debug(f"Neo4j validation failed: {e}")
            return False
    
    async def _validate_postgresql(self) -> bool:
        """Validate PostgreSQL subsystem."""
        try:
            import psycopg2
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="postgres",
                user="postgres",
                password="password",
                connect_timeout=1
            )
            conn.close()
            return True
        except Exception as e:
            logger.debug(f"PostgreSQL validation failed: {e}")
            return False
    
    async def _validate_qdrant(self) -> bool:
        """Validate Qdrant subsystem."""
        try:
            if NETWORK_AVAILABLE:
                response = requests.get("http://localhost:6333/health", timeout=1)
                return response.status_code == 200
            return False
        except Exception as e:
            logger.debug(f"Qdrant validation failed: {e}")
            return False
    
    async def _validate_openai_api(self) -> bool:
        """Validate OpenAI API subsystem."""
        try:
            if NETWORK_AVAILABLE:
                response = requests.get("https://api.openai.com/v1/models", timeout=2)
                return response.status_code in [200, 401]  # 401 is OK (auth required)
            return False
        except Exception as e:
            logger.debug(f"OpenAI API validation failed: {e}")
            return False
    
    async def _validate_vault(self) -> bool:
        """Validate Vault subsystem."""
        try:
            if NETWORK_AVAILABLE:
                response = requests.get("http://localhost:8200/v1/sys/health", timeout=1)
                return response.status_code in [200, 429, 501]  # Various healthy states
            return False
        except Exception as e:
            logger.debug(f"Vault validation failed: {e}")
            return False
    
    def get_subsystem_health(self) -> Dict[str, SubsystemHealth]:
        """Get health status of all subsystems."""
        return self.subsystems.copy()


class ReliableTaskOrchestrator:
    """
    Reliable task orchestrator with enhanced error handling.
    
    Provides UUID7 task IDs, fail-fast validation, offline mode,
    and comprehensive error recovery mechanisms.
    """
    
    def __init__(self, offline_mode: bool = False):
        """
        Initialize reliable task orchestrator.
        
        Args:
            offline_mode: Enable offline mode for air-gapped environments
        """
        self.offline_mode = offline_mode
        self.operation_mode = OperationMode.OFFLINE if offline_mode else OperationMode.ONLINE
        
        # Core components
        self.uuid7_generator = UUID7Generator()
        self.subsystem_validator = SubsystemValidator()
        
        # Task management
        self.active_tasks: Dict[str, TaskMetadata] = {}
        self.completed_tasks: Dict[str, TaskMetadata] = {}
        self.failed_tasks: Dict[str, TaskMetadata] = {}
        
        # System monitoring
        self.system_metrics: List[SystemMetrics] = []
        self.alert_handlers: List[Callable] = []
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.task_timeout_default = timedelta(minutes=30)
        self.health_check_interval = 60  # seconds
        
        # Audit logging
        self.audit_log_path = Path("logs/orchestrator_audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info(f"ReliableTaskOrchestrator initialized - mode: {self.operation_mode.value}")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        asyncio.create_task(self._health_monitor())
        asyncio.create_task(self._task_timeout_monitor())
    
    def _audit_log(self, operation: str, task_id: str, details: Dict[str, Any]):
        """Log orchestrator events for audit."""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "task_id": task_id,
            "details": details,
            "operation_mode": self.operation_mode.value
        }
        
        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(audit_event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write orchestrator audit log: {e}")
    
    async def create_task(
        self,
        task_type: str,
        description: str,
        subsystems_required: List[str] = None,
        priority: int = 0,
        timeout: timedelta = None,
        parent_task_id: str = None,
        dependencies: List[str] = None,
        tags: Dict[str, str] = None
    ) -> str:
        """
        Create a new task with UUID7 identifier.
        
        Args:
            task_type: Type of task
            description: Task description
            subsystems_required: Required subsystems
            priority: Task priority (higher = more important)
            timeout: Task timeout
            parent_task_id: Parent task ID for hierarchical tasks
            dependencies: Task dependencies
            tags: Task tags for categorization
            
        Returns:
            UUID7 task identifier
        """
        try:
            # Generate UUID7 task ID
            task_id = self.uuid7_generator.generate()
            
            # Create task metadata
            task_metadata = TaskMetadata(
                task_id=task_id,
                parent_task_id=parent_task_id,
                task_type=task_type,
                description=description,
                priority=priority,
                timeout=timeout or self.task_timeout_default,
                subsystems_required=subsystems_required or [],
                dependencies=dependencies or [],
                tags=tags or {}
            )
            
            # Store task
            self.active_tasks[task_id] = task_metadata
            
            # Log audit event
            self._audit_log("create_task", task_id, {
                "task_type": task_type,
                "description": description,
                "priority": priority,
                "subsystems_required": subsystems_required or [],
                "parent_task_id": parent_task_id
            })
            
            logger.info(f"✅ Task created: {task_id} ({task_type})")
            return task_id
            
        except Exception as e:
            logger.error(f"Failed to create task: {e}")
            raise
    
    async def execute_task(self, task_id: str, task_function: Callable, *args, **kwargs) -> bool:
        """
        Execute a task with fail-fast validation.
        
        Args:
            task_id: Task identifier
            task_function: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            True if task completed successfully, False otherwise
        """
        try:
            task_metadata = self.active_tasks.get(task_id)
            if not task_metadata:
                logger.error(f"Task {task_id} not found")
                return False
            
            # Check dependencies
            if task_metadata.dependencies:
                unmet_dependencies = []
                for dep_id in task_metadata.dependencies:
                    if dep_id not in self.completed_tasks:
                        unmet_dependencies.append(dep_id)
                
                if unmet_dependencies:
                    logger.error(f"Task {task_id} has unmet dependencies: {unmet_dependencies}")
                    return False
            
            # Fail-fast subsystem validation
            if task_metadata.subsystems_required and not self.offline_mode:
                all_healthy, failed_subsystems = await self.subsystem_validator.fail_fast_validation(
                    task_metadata.subsystems_required
                )
                
                if not all_healthy:
                    logger.error(f"Task {task_id} failed subsystem validation: {failed_subsystems}")
                    await self._fail_task(task_id, f"Subsystem validation failed: {failed_subsystems}")
                    return False
            
            # Check concurrent task limit
            if len(self.active_tasks) > self.max_concurrent_tasks:
                logger.warning(f"Task {task_id} delayed due to concurrent task limit")
                return False
            
            # Start task execution
            task_metadata.started_at = datetime.utcnow()
            
            logger.info(f"🚀 Starting task: {task_id} ({task_metadata.task_type})")
            
            # Execute task function
            start_time = time.time()
            result = await task_function(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Complete task
            task_metadata.completed_at = datetime.utcnow()
            self.completed_tasks[task_id] = task_metadata
            del self.active_tasks[task_id]
            
            # Log audit event
            self._audit_log("complete_task", task_id, {
                "execution_time": execution_time,
                "result": str(result)[:100] if result else None
            })
            
            logger.info(f"✅ Task completed: {task_id} ({execution_time:.3f}s)")
            return True
            
        except Exception as e:
            logger.error(f"Task {task_id} execution failed: {e}")
            await self._fail_task(task_id, str(e))
            return False
    
    async def _fail_task(self, task_id: str, error_message: str):
        """Mark task as failed."""
        task_metadata = self.active_tasks.get(task_id)
        if task_metadata:
            task_metadata.completed_at = datetime.utcnow()
            self.failed_tasks[task_id] = task_metadata
            del self.active_tasks[task_id]
            
            # Log audit event
            self._audit_log("fail_task", task_id, {
                "error_message": error_message
            })
    
    async def cancel_task(self, task_id: str, reason: str = "") -> bool:
        """
        Cancel a running task.
        
        Args:
            task_id: Task identifier
            reason: Cancellation reason
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        try:
            task_metadata = self.active_tasks.get(task_id)
            if not task_metadata:
                logger.error(f"Task {task_id} not found")
                return False
            
            # Remove from active tasks
            del self.active_tasks[task_id]
            
            # Log audit event
            self._audit_log("cancel_task", task_id, {
                "reason": reason
            })
            
            logger.info(f"❌ Task cancelled: {task_id} ({reason})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel task {task_id}: {e}")
            return False
    
    async def _health_monitor(self):
        """Background health monitoring."""
        while True:
            try:
                # Collect system metrics
                if PSUTIL_AVAILABLE:
                    cpu_usage = psutil.cpu_percent()
                    memory_usage = psutil.virtual_memory().percent
                    disk_usage = psutil.disk_usage('/').percent
                else:
                    cpu_usage = memory_usage = disk_usage = 0.0
                
                # Validate subsystems
                subsystem_results = await self.subsystem_validator.validate_all_subsystems()
                
                # Create system metrics
                metrics = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    cpu_usage=cpu_usage,
                    memory_usage=memory_usage,
                    disk_usage=disk_usage,
                    network_latency=0.0,  # TODO: Implement network latency check
                    active_tasks=len(self.active_tasks),
                    completed_tasks=len(self.completed_tasks),
                    failed_tasks=len(self.failed_tasks),
                    subsystem_health=self.subsystem_validator.get_subsystem_health()
                )
                
                # Store metrics
                self.system_metrics.append(metrics)
                
                # Keep only last 24 hours of metrics
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.system_metrics = [m for m in self.system_metrics if m.timestamp > cutoff_time]
                
                # Check for alerts
                await self._check_alerts(metrics)
                
                # Wait for next check
                await asyncio.sleep(self.health_check_interval)
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(self.health_check_interval)
    
    async def _task_timeout_monitor(self):
        """Monitor for task timeouts."""
        while True:
            try:
                now = datetime.utcnow()
                timed_out_tasks = []
                
                for task_id, task_metadata in self.active_tasks.items():
                    if task_metadata.started_at:
                        elapsed = now - task_metadata.started_at
                        if elapsed > task_metadata.timeout:
                            timed_out_tasks.append(task_id)
                
                # Handle timed out tasks
                for task_id in timed_out_tasks:
                    logger.warning(f"⏰ Task timeout: {task_id}")
                    await self._fail_task(task_id, "Task timeout")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Task timeout monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _check_alerts(self, metrics: SystemMetrics):
        """Check for alert conditions."""
        alerts = []
        
        # CPU usage alert
        if metrics.cpu_usage > 90:
            alerts.append(f"High CPU usage: {metrics.cpu_usage:.1f}%")
        
        # Memory usage alert
        if metrics.memory_usage > 90:
            alerts.append(f"High memory usage: {metrics.memory_usage:.1f}%")
        
        # Disk usage alert
        if metrics.disk_usage > 95:
            alerts.append(f"High disk usage: {metrics.disk_usage:.1f}%")
        
        # Failed subsystems alert
        failed_subsystems = [
            name for name, health in metrics.subsystem_health.items()
            if health.status == SubsystemStatus.FAILED
        ]
        if failed_subsystems:
            alerts.append(f"Failed subsystems: {failed_subsystems}")
        
        # Send alerts
        for alert in alerts:
            await self._send_alert(alert)
    
    async def _send_alert(self, message: str):
        """Send system alert."""
        for handler in self.alert_handlers:
            try:
                await handler(message)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
    
    def add_alert_handler(self, handler: Callable):
        """Add alert handler."""
        self.alert_handlers.append(handler)
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status."""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                "task_id": task_id,
                "status": TaskStatus.RUNNING.value,
                "task_type": task.task_type,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "priority": task.priority,
                "subsystems_required": task.subsystems_required
            }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": TaskStatus.COMPLETED.value,
                "task_type": task.task_type,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "priority": task.priority
            }
        
        # Check failed tasks
        if task_id in self.failed_tasks:
            task = self.failed_tasks[task_id]
            return {
                "task_id": task_id,
                "status": TaskStatus.FAILED.value,
                "task_type": task.task_type,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "priority": task.priority
            }
        
        return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        latest_metrics = self.system_metrics[-1] if self.system_metrics else None
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "operation_mode": self.operation_mode.value,
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "system_metrics": {
                "cpu_usage": latest_metrics.cpu_usage if latest_metrics else 0.0,
                "memory_usage": latest_metrics.memory_usage if latest_metrics else 0.0,
                "disk_usage": latest_metrics.disk_usage if latest_metrics else 0.0
            } if latest_metrics else {},
            "subsystem_health": {
                name: {
                    "status": health.status.value,
                    "response_time": health.response_time,
                    "error_rate": health.error_rate
                }
                for name, health in (latest_metrics.subsystem_health.items() if latest_metrics else {})
            },
            "uuid7_generator": {
                "last_timestamp": self.uuid7_generator.last_timestamp,
                "counter": self.uuid7_generator.counter
            }
        }


# Example alert handler
async def log_alert_handler(message: str):
    """Example alert handler that logs alerts."""
    logger.warning(f"🚨 ALERT: {message}")


# Global instance for easy access
_reliable_task_orchestrator = None


def get_reliable_task_orchestrator(offline_mode: bool = False) -> ReliableTaskOrchestrator:
    """Get global ReliableTaskOrchestrator instance."""
    global _reliable_task_orchestrator
    
    if _reliable_task_orchestrator is None:
        _reliable_task_orchestrator = ReliableTaskOrchestrator(offline_mode=offline_mode)
        _reliable_task_orchestrator.add_alert_handler(log_alert_handler)
    
    return _reliable_task_orchestrator


if __name__ == "__main__":
    # Test the ReliableTaskOrchestrator
    async def test_orchestrator():
        print("🔧 Testing ReliableTaskOrchestrator...")
        
        # Initialize orchestrator
        orchestrator = get_reliable_task_orchestrator(offline_mode=True)
        
        # Test UUID7 generation
        uuid7_gen = UUID7Generator()
        for i in range(5):
            uuid7_id = uuid7_gen.generate()
            timestamp = uuid7_gen.extract_timestamp(uuid7_id)
            print(f"UUID7 {i+1}: {uuid7_id} (created: {timestamp})")
        
        # Test task creation
        task_id = await orchestrator.create_task(
            task_type="test_task",
            description="Test task for orchestrator validation",
            subsystems_required=["redis", "neo4j"],
            priority=1,
            tags={"test": "true", "phase": "15.3"}
        )
        
        print(f"✅ Task created: {task_id}")
        
        # Test task execution
        async def sample_task():
            await asyncio.sleep(0.1)
            return "Task completed successfully"
        
        success = await orchestrator.execute_task(task_id, sample_task)
        print(f"✅ Task execution result: {success}")
        
        # Get task status
        status = orchestrator.get_task_status(task_id)
        print(f"📊 Task status: {status}")
        
        # Get system status
        system_status = orchestrator.get_system_status()
        print(f"📊 System status: {json.dumps(system_status, indent=2)}")
        
        print("🎉 ReliableTaskOrchestrator test completed!")
    
    # Run test
    asyncio.run(test_orchestrator()) 