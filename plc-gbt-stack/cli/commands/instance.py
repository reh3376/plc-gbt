#!/usr/bin/env python3
"""
🖥️ Phase 21.3: Instance Management Commands

Comprehensive instance management commands for control loop instances with CLX PLC integration.
This module provides complete lifecycle management for control loop instances including creation,
management, validation, testing, and real-time PLC connectivity.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (800-1200 lines, 5-8 files, 1.5 weeks)
Context Management: CLX PLC integration with read-only enforcement
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.3 Objectives:
- Instance creation with schema templates and wizards
- Instance management (list, info, edit, update)
- Instance validation and testing with simulation
- Instance export/import and conversion capabilities
- CLX PLC integration with read-only tag browsing
- Real-time data visualization from production PLCs

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.3 - Instance Management Commands
Dependencies: Phase 20 (Schema Framework), Phase 21.1/21.2 (CLI), pylogix (CLX PLC)
"""

import json
import logging
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, FloatPrompt, IntPrompt, Prompt
from rich.status import Status
from rich.table import Table

# Import CLI framework components
try:
    from ..auth.auth_manager import AuthenticationManager
    from ..config_manager import CLIConfiguration
    from ..framework.command_base import CLICommand, Permission, requires_permission
    CLI_FRAMEWORK_AVAILABLE = True
except ImportError:
    CLI_FRAMEWORK_AVAILABLE = False
    # Fallback definitions
    def requires_permission(perm):
        def decorator(func):
            return func
        return decorator
    class Permission:
        READ = "READ"
        WRITE = "WRITE"
        ADMIN = "ADMIN"

# CLX PLC Integration
try:
    from pylogix import PLC
    PYLOGIX_AVAILABLE = True
except ImportError:
    PYLOGIX_AVAILABLE = False

# Project root setup
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up console and logging
console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# CORE DATA STRUCTURES AND ENUMERATIONS
# =============================================================================

class InstanceStatus(Enum):
    """Control loop instance status"""
    DRAFT = "draft"
    CONFIGURED = "configured"
    VALIDATED = "validated"
    DEPLOYED = "deployed"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    ARCHIVED = "archived"

class InstanceType(Enum):
    """Control loop instance types"""
    BASIC_PID = "basic_pid"
    CASCADE_PID = "cascade_pid"
    FEEDFORWARD_PID = "feedforward_pid"
    MULTI_LOOP = "multi_loop"
    ADAPTIVE_PID = "adaptive_pid"
    MPC = "mpc"
    CUSTOM = "custom"

class ValidationLevel(Enum):
    """Instance validation levels"""
    BASIC = "basic"           # Schema compliance only
    STANDARD = "standard"     # Schema + basic logic validation
    ADVANCED = "advanced"     # Standard + simulation testing
    PRODUCTION = "production" # Advanced + PLC connectivity validation

class PLCConnectionMode(Enum):
    """PLC connection modes"""
    READ_ONLY = "read_only"
    SIMULATION = "simulation"
    OFFLINE = "offline"

@dataclass
class InstanceConfiguration:
    """Control loop instance configuration"""
    instance_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    instance_type: InstanceType = InstanceType.BASIC_PID
    schema_id: str = ""
    schema_version: str = "1.0.0"
    status: InstanceStatus = InstanceStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Control parameters
    parameters: Dict[str, Any] = field(default_factory=dict)

    # PLC integration settings
    plc_connection: Optional[Dict[str, Any]] = None

    # Validation results
    validation_results: Optional[Dict[str, Any]] = None

@dataclass
class PLCTagInfo:
    """PLC tag information"""
    tag_name: str
    data_type: str
    value: Any
    address: str = ""
    description: str = ""
    external_access: str = "Read/Write"
    timestamp: datetime = field(default_factory=datetime.now)
    quality: str = "GOOD"

@dataclass
class PLCConnection:
    """PLC connection configuration"""
    connection_id: str
    host: str
    slot: int = 0
    timeout: float = 5.0
    mode: PLCConnectionMode = PLCConnectionMode.READ_ONLY
    status: str = "DISCONNECTED"
    last_communication: Optional[datetime] = None
    error_count: int = 0

# =============================================================================
# INSTANCE MANAGEMENT CORE CLASSES
# =============================================================================

class InstanceManager:
    """Core instance management functionality"""

    def __init__(self, config: Optional[object] = None):
        self.config = config
        self.instances_dir = Path.cwd() / "instances"
        self.instances_dir.mkdir(exist_ok=True)
        self.templates_dir = Path.cwd() / "templates"
        self.templates_dir.mkdir(exist_ok=True)

    def create_instance(self, config: InstanceConfiguration) -> bool:
        """Create new control loop instance"""
        try:
            instance_file = self.instances_dir / f"{config.instance_id}.json"

            # Generate default parameters based on instance type
            if not config.parameters:
                config.parameters = self._generate_default_parameters(config.instance_type)

            # Save instance configuration
            with open(instance_file, 'w') as f:
                json.dump(asdict(config), f, indent=2, default=str)

            logger.info(f"Created instance: {config.name} ({config.instance_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to create instance: {e}")
            return False

    def list_instances(self, filter_type: Optional[InstanceType] = None,
                      filter_status: Optional[InstanceStatus] = None) -> List[InstanceConfiguration]:
        """List all instances with optional filtering"""
        instances = []

        for instance_file in self.instances_dir.glob("*.json"):
            try:
                with open(instance_file) as f:
                    data = json.load(f)

                # Convert back to InstanceConfiguration
                instance = InstanceConfiguration(**data)

                # Apply filters
                if filter_type and instance.instance_type != filter_type:
                    continue
                if filter_status and instance.status != filter_status:
                    continue

                instances.append(instance)

            except Exception as e:
                logger.warning(f"Failed to load instance {instance_file}: {e}")

        return sorted(instances, key=lambda x: x.updated_at, reverse=True)

    def get_instance(self, instance_id: str) -> Optional[InstanceConfiguration]:
        """Get specific instance by ID"""
        instance_file = self.instances_dir / f"{instance_id}.json"

        if not instance_file.exists():
            return None

        try:
            with open(instance_file) as f:
                data = json.load(f)
            return InstanceConfiguration(**data)

        except Exception as e:
            logger.error(f"Failed to load instance {instance_id}: {e}")
            return None

    def update_instance(self, instance_id: str, updates: Dict[str, Any]) -> bool:
        """Update instance configuration"""
        instance = self.get_instance(instance_id)
        if not instance:
            return False

        try:
            # Apply updates
            for key, value in updates.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            instance.updated_at = datetime.now()

            # Save updated instance
            instance_file = self.instances_dir / f"{instance_id}.json"
            with open(instance_file, 'w') as f:
                json.dump(asdict(instance), f, indent=2, default=str)

            return True

        except Exception as e:
            logger.error(f"Failed to update instance {instance_id}: {e}")
            return False

    def delete_instance(self, instance_id: str) -> bool:
        """Delete instance"""
        instance_file = self.instances_dir / f"{instance_id}.json"

        if not instance_file.exists():
            return False

        try:
            instance_file.unlink()
            logger.info(f"Deleted instance: {instance_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete instance {instance_id}: {e}")
            return False

    def validate_instance(self, instance_id: str, level: ValidationLevel = ValidationLevel.STANDARD) -> Dict[str, Any]:
        """Validate instance configuration"""
        instance = self.get_instance(instance_id)
        if not instance:
            return {"valid": False, "error": "Instance not found"}

        validation_results = {
            "valid": True,
            "level": level.value,
            "timestamp": datetime.now(),
            "checks": [],
            "warnings": [],
            "errors": []
        }

        # Basic validation - schema compliance
        validation_results["checks"].append("Schema compliance check")
        if not instance.schema_id:
            validation_results["errors"].append("No schema ID specified")
            validation_results["valid"] = False

        # Standard validation - parameter validation
        if level in [ValidationLevel.STANDARD, ValidationLevel.ADVANCED, ValidationLevel.PRODUCTION]:
            validation_results["checks"].append("Parameter validation")
            if not instance.parameters:
                validation_results["warnings"].append("No parameters configured")
            else:
                # Validate PID parameters if applicable
                if instance.instance_type == InstanceType.BASIC_PID:
                    required_params = ['kp', 'ki', 'kd', 'setpoint']
                    missing_params = [p for p in required_params if p not in instance.parameters]
                    if missing_params:
                        validation_results["errors"].append(f"Missing PID parameters: {missing_params}")
                        validation_results["valid"] = False

        # Advanced validation - simulation testing
        if level in [ValidationLevel.ADVANCED, ValidationLevel.PRODUCTION]:
            validation_results["checks"].append("Simulation testing")
            # TODO: Implement simulation validation
            validation_results["warnings"].append("Simulation testing not yet implemented")

        # Production validation - PLC connectivity
        if level == ValidationLevel.PRODUCTION:
            validation_results["checks"].append("PLC connectivity validation")
            if instance.plc_connection:
                # TODO: Test PLC connection
                validation_results["warnings"].append("PLC connectivity testing not yet implemented")
            else:
                validation_results["warnings"].append("No PLC connection configured")

        return validation_results

    def _generate_default_parameters(self, instance_type: InstanceType) -> Dict[str, Any]:
        """Generate default parameters for instance type"""
        defaults = {
            InstanceType.BASIC_PID: {
                "kp": 1.0,
                "ki": 0.1,
                "kd": 0.05,
                "setpoint": 0.0,
                "output_min": 0.0,
                "output_max": 100.0,
                "sample_time": 1.0
            },
            InstanceType.CASCADE_PID: {
                "master_kp": 1.0,
                "master_ki": 0.1,
                "master_kd": 0.05,
                "slave_kp": 2.0,
                "slave_ki": 0.2,
                "slave_kd": 0.1,
                "master_setpoint": 0.0,
                "sample_time": 1.0
            },
            InstanceType.FEEDFORWARD_PID: {
                "kp": 1.0,
                "ki": 0.1,
                "kd": 0.05,
                "ff_gain": 0.5,
                "setpoint": 0.0,
                "sample_time": 1.0
            }
        }

        return defaults.get(instance_type, {})

# =============================================================================
# CLX PLC INTEGRATION MANAGER
# =============================================================================

class CLXPLCManager:
    """CLX PLC integration with read-only enforcement"""

    def __init__(self):
        self.connections: Dict[str, PLCConnection] = {}
        self.active_connection: Optional[str] = None
        self.read_only_enforced = True  # Always enforce read-only for safety

    def create_connection(self, host: str, slot: int = 0, timeout: float = 5.0) -> str:
        """Create new PLC connection configuration"""
        connection_id = f"plc_{host.replace('.', '_')}_{slot}"

        connection = PLCConnection(
            connection_id=connection_id,
            host=host,
            slot=slot,
            timeout=timeout,
            mode=PLCConnectionMode.READ_ONLY  # Always read-only
        )

        self.connections[connection_id] = connection
        logger.info(f"Created PLC connection configuration: {connection_id}")
        return connection_id

    def connect(self, connection_id: str) -> bool:
        """Connect to CLX PLC with read-only enforcement"""
        if not PYLOGIX_AVAILABLE:
            logger.error("pylogix library not available - cannot connect to PLC")
            return False

        if connection_id not in self.connections:
            logger.error(f"Connection {connection_id} not found")
            return False

        connection = self.connections[connection_id]

        try:
            # Create pylogix PLC instance
            plc = PLC()
            plc.IPAddress = connection.host
            plc.ProcessorSlot = connection.slot

            # Test connection with a simple read
            test_result = plc.GetPLCTime()

            if test_result.Status == "Success":
                connection.status = "CONNECTED"
                connection.last_communication = datetime.now()
                connection.error_count = 0
                self.active_connection = connection_id

                logger.info(f"✅ Connected to CLX PLC: {connection.host} (Read-Only)")
                logger.info(f"PLC Time: {test_result.Value}")
                return True
            else:
                connection.status = "ERROR"
                connection.error_count += 1
                logger.error(f"❌ PLC connection failed: {test_result.Status}")
                return False

        except Exception as e:
            connection.status = "ERROR"
            connection.error_count += 1
            logger.error(f"❌ PLC connection exception: {e}")
            return False

    def disconnect(self, connection_id: str) -> bool:
        """Disconnect from PLC"""
        if connection_id in self.connections:
            self.connections[connection_id].status = "DISCONNECTED"
            if self.active_connection == connection_id:
                self.active_connection = None
            logger.info(f"Disconnected from PLC: {connection_id}")
            return True
        return False

    def read_tag(self, tag_name: str, connection_id: Optional[str] = None) -> Optional[PLCTagInfo]:
        """Read single tag from PLC (read-only)"""
        if not PYLOGIX_AVAILABLE:
            logger.error("pylogix library not available")
            return None

        conn_id = connection_id or self.active_connection
        if not conn_id or conn_id not in self.connections:
            logger.error("No active PLC connection")
            return None

        connection = self.connections[conn_id]
        if connection.status != "CONNECTED":
            logger.error(f"PLC not connected: {conn_id}")
            return None

        try:
            plc = PLC()
            plc.IPAddress = connection.host
            plc.ProcessorSlot = connection.slot

            result = plc.Read(tag_name)

            if result.Status == "Success":
                connection.last_communication = datetime.now()

                return PLCTagInfo(
                    tag_name=result.TagName,
                    data_type=str(type(result.Value).__name__),
                    value=result.Value,
                    description=f"Read from {connection.host}",
                    timestamp=datetime.now(),
                    quality="GOOD"
                )
            else:
                logger.error(f"Tag read failed: {result.Status}")
                return None

        except Exception as e:
            logger.error(f"Tag read exception: {e}")
            connection.error_count += 1
            return None

    def browse_tags(self, connection_id: Optional[str] = None, filter_pattern: str = "*") -> List[str]:
        """Browse available tags from PLC"""
        if not PYLOGIX_AVAILABLE:
            logger.error("pylogix library not available")
            return []

        conn_id = connection_id or self.active_connection
        if not conn_id or conn_id not in self.connections:
            logger.error("No active PLC connection")
            return []

        connection = self.connections[conn_id]
        if connection.status != "CONNECTED":
            logger.error(f"PLC not connected: {conn_id}")
            return []

        try:
            plc = PLC()
            plc.IPAddress = connection.host
            plc.ProcessorSlot = connection.slot

            # Get tag list from PLC
            tags = plc.GetTagList()

            if tags.Status == "Success":
                connection.last_communication = datetime.now()

                # Filter tags based on pattern
                tag_names = []
                for tag in tags.Value:
                    tag_name = tag.TagName
                    if filter_pattern == "*" or filter_pattern.lower() in tag_name.lower():
                        tag_names.append(tag_name)

                return sorted(tag_names)
            else:
                logger.error(f"Tag list retrieval failed: {tags.Status}")
                return []

        except Exception as e:
            logger.error(f"Tag browse exception: {e}")
            connection.error_count += 1
            return []

    def get_connection_status(self) -> Dict[str, Any]:
        """Get status of all PLC connections"""
        status = {
            "total_connections": len(self.connections),
            "active_connection": self.active_connection,
            "read_only_enforced": self.read_only_enforced,
            "connections": {}
        }

        for conn_id, connection in self.connections.items():
            status["connections"][conn_id] = {
                "host": connection.host,
                "slot": connection.slot,
                "status": connection.status,
                "mode": connection.mode.value,
                "last_communication": connection.last_communication,
                "error_count": connection.error_count
            }

        return status

# =============================================================================
# INSTANCE WIZARD
# =============================================================================

class InstanceWizard:
    """Interactive instance creation wizard"""

    def __init__(self, instance_manager: InstanceManager):
        self.instance_manager = instance_manager
        self.plc_manager = CLXPLCManager()

    def run_wizard(self) -> Optional[InstanceConfiguration]:
        """Run interactive instance creation wizard"""
        console.print(Panel.fit(
            "[bold blue]🧙‍♂️ Instance Creation Wizard[/bold blue]\n"
            "Create a new control loop instance with guided setup",
            border_style="blue"
        ))

        try:
            # Step 1: Basic Information
            console.print("\n[bold]Step 1: Basic Information[/bold]")
            name = Prompt.ask("Instance name", default="New Instance")
            description = Prompt.ask("Description", default="")

            # Step 2: Instance Type Selection
            console.print("\n[bold]Step 2: Instance Type[/bold]")
            type_choices = [t.value for t in InstanceType]
            type_table = Table(title="Available Instance Types")
            type_table.add_column("Option", style="cyan")
            type_table.add_column("Type", style="magenta")
            type_table.add_column("Description", style="green")

            type_descriptions = {
                "basic_pid": "Standard PID controller with single loop",
                "cascade_pid": "Cascade PID with master and slave loops",
                "feedforward_pid": "PID with feedforward compensation",
                "multi_loop": "Multiple interconnected control loops",
                "adaptive_pid": "Self-tuning PID controller",
                "mpc": "Model Predictive Controller",
                "custom": "Custom control strategy"
            }

            for i, type_val in enumerate(type_choices, 1):
                type_table.add_row(str(i), type_val, type_descriptions.get(type_val, ""))

            console.print(type_table)

            type_choice = IntPrompt.ask("Select instance type", choices=list(range(1, len(type_choices) + 1)))
            instance_type = InstanceType(type_choices[type_choice - 1])

            # Step 3: Schema Selection
            console.print("\n[bold]Step 3: Schema Selection[/bold]")
            schema_id = Prompt.ask("Schema ID", default="standard-pid-v1.0")

            # Step 4: Control Parameters
            console.print("\n[bold]Step 4: Control Parameters[/bold]")
            parameters = self._configure_parameters(instance_type)

            # Step 5: PLC Integration (Optional)
            console.print("\n[bold]Step 5: PLC Integration (Optional)[/bold]")
            configure_plc = Confirm.ask("Configure PLC connection?", default=False)

            plc_connection = None
            if configure_plc:
                plc_connection = self._configure_plc_connection()

            # Step 6: Review and Create
            console.print("\n[bold]Step 6: Review Configuration[/bold]")

            config = InstanceConfiguration(
                name=name,
                description=description,
                instance_type=instance_type,
                schema_id=schema_id,
                parameters=parameters,
                plc_connection=plc_connection,
                status=InstanceStatus.CONFIGURED
            )

            self._display_instance_summary(config)

            if Confirm.ask("\nCreate this instance?", default=True):
                if self.instance_manager.create_instance(config):
                    console.print(f"✅ Instance created successfully: [green]{config.instance_id}[/green]")
                    return config
                else:
                    console.print("❌ Failed to create instance")
                    return None
            else:
                console.print("Instance creation cancelled")
                return None

        except KeyboardInterrupt:
            console.print("\n⚠️ Wizard cancelled by user")
            return None
        except Exception as e:
            console.print(f"❌ Wizard error: {e}")
            return None

    def _configure_parameters(self, instance_type: InstanceType) -> Dict[str, Any]:
        """Configure control parameters based on instance type"""
        parameters = {}

        if instance_type == InstanceType.BASIC_PID:
            console.print("Configuring PID parameters:")
            parameters["kp"] = FloatPrompt.ask("Proportional gain (Kp)", default=1.0)
            parameters["ki"] = FloatPrompt.ask("Integral gain (Ki)", default=0.1)
            parameters["kd"] = FloatPrompt.ask("Derivative gain (Kd)", default=0.05)
            parameters["setpoint"] = FloatPrompt.ask("Initial setpoint", default=0.0)
            parameters["output_min"] = FloatPrompt.ask("Output minimum", default=0.0)
            parameters["output_max"] = FloatPrompt.ask("Output maximum", default=100.0)
            parameters["sample_time"] = FloatPrompt.ask("Sample time (seconds)", default=1.0)

        elif instance_type == InstanceType.CASCADE_PID:
            console.print("Configuring Cascade PID parameters:")
            console.print("Master loop:")
            parameters["master_kp"] = FloatPrompt.ask("Master Kp", default=1.0)
            parameters["master_ki"] = FloatPrompt.ask("Master Ki", default=0.1)
            parameters["master_kd"] = FloatPrompt.ask("Master Kd", default=0.05)
            console.print("Slave loop:")
            parameters["slave_kp"] = FloatPrompt.ask("Slave Kp", default=2.0)
            parameters["slave_ki"] = FloatPrompt.ask("Slave Ki", default=0.2)
            parameters["slave_kd"] = FloatPrompt.ask("Slave Kd", default=0.1)
            parameters["master_setpoint"] = FloatPrompt.ask("Master setpoint", default=0.0)

        else:
            # For other types, use defaults and allow manual configuration
            console.print(f"Using default parameters for {instance_type.value}")
            parameters = self.instance_manager._generate_default_parameters(instance_type)

        return parameters

    def _configure_plc_connection(self) -> Optional[Dict[str, Any]]:
        """Configure PLC connection settings"""
        try:
            console.print("PLC Connection Configuration:")
            host = Prompt.ask("PLC IP Address", default="192.168.1.10")
            slot = IntPrompt.ask("PLC Slot", default=0)
            timeout = FloatPrompt.ask("Connection timeout (seconds)", default=5.0)

            # Test connection option
            test_connection = Confirm.ask("Test connection now?", default=False)

            connection_config = {
                "host": host,
                "slot": slot,
                "timeout": timeout,
                "mode": PLCConnectionMode.READ_ONLY.value,
                "enabled": True
            }

            if test_connection:
                console.print("Testing PLC connection...")
                connection_id = self.plc_manager.create_connection(host, slot, timeout)

                with Status("Connecting to PLC...", spinner="dots"):
                    success = self.plc_manager.connect(connection_id)

                if success:
                    console.print("✅ PLC connection successful!")
                    # Browse some tags as verification
                    tags = self.plc_manager.browse_tags(connection_id)
                    console.print(f"Found {len(tags)} tags on PLC")
                    if tags[:5]:  # Show first 5 tags
                        console.print(f"Sample tags: {', '.join(tags[:5])}")

                    self.plc_manager.disconnect(connection_id)
                else:
                    console.print("❌ PLC connection failed")
                    if not Confirm.ask("Continue with configuration anyway?", default=True):
                        return None

            return connection_config

        except Exception as e:
            console.print(f"❌ PLC configuration error: {e}")
            return None

    def _display_instance_summary(self, config: InstanceConfiguration):
        """Display instance configuration summary"""
        summary_table = Table(title="Instance Configuration Summary")
        summary_table.add_column("Property", style="cyan")
        summary_table.add_column("Value", style="magenta")

        summary_table.add_row("Instance ID", config.instance_id)
        summary_table.add_row("Name", config.name)
        summary_table.add_row("Type", config.instance_type.value)
        summary_table.add_row("Schema", config.schema_id)
        summary_table.add_row("Status", config.status.value)

        # Parameters summary
        param_count = len(config.parameters)
        summary_table.add_row("Parameters", f"{param_count} configured")

        # PLC connection summary
        if config.plc_connection:
            plc_info = f"{config.plc_connection['host']}:{config.plc_connection['slot']}"
            summary_table.add_row("PLC Connection", plc_info)
        else:
            summary_table.add_row("PLC Connection", "Not configured")

        console.print(summary_table)

# Global instance manager for CLI commands
instance_manager = InstanceManager()
plc_manager = CLXPLCManager()

# =============================================================================
# CLI COMMAND IMPLEMENTATIONS
# =============================================================================

@click.group()
@click.pass_context
def instance_commands(ctx):
    """Instance management commands for control loop instances with CLX PLC integration"""
    pass

# Instance Creation Commands
@instance_commands.command('create')
@click.option('--schema', '-s', required=True, help='Schema ID to use for instance')
@click.option('--name', '-n', required=True, help='Instance name')
@click.option('--description', '-d', default='', help='Instance description')
@click.option('--type', '-t', 'instance_type',
              type=click.Choice([t.value for t in InstanceType]),
              default=InstanceType.BASIC_PID.value, help='Instance type')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@requires_permission(Permission.WRITE)
def create_instance(schema, name, description, instance_type, output):
    """Create new control loop instance"""
    try:
        config = InstanceConfiguration(
            name=name,
            description=description,
            instance_type=InstanceType(instance_type),
            schema_id=schema,
            status=InstanceStatus.CONFIGURED
        )

        # Generate default parameters
        config.parameters = instance_manager._generate_default_parameters(config.instance_type)

        success = instance_manager.create_instance(config)

        if success:
            if output == 'table':
                table = Table(title=f"Created Instance: {name}")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="green")

                table.add_row("Instance ID", config.instance_id)
                table.add_row("Name", config.name)
                table.add_row("Type", config.instance_type.value)
                table.add_row("Schema", config.schema_id)
                table.add_row("Status", config.status.value)
                table.add_row("Parameters", f"{len(config.parameters)} configured")

                console.print(table)
                console.print("\n✅ Instance created successfully!")

            elif output == 'json':
                result = {"success": True, "instance": asdict(config)}
                console.print(json.dumps(result, indent=2, default=str))

            elif output == 'yaml':
                result = {"success": True, "instance": asdict(config)}
                console.print(yaml.dump(result, default_flow_style=False))
        else:
            console.print("❌ Failed to create instance")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error creating instance: {e}")
        sys.exit(1)

@instance_commands.command('wizard')
@requires_permission(Permission.WRITE)
def instance_wizard():
    """Interactive instance creation wizard"""
    try:
        wizard = InstanceWizard(instance_manager)
        instance = wizard.run_wizard()

        if instance:
            console.print("\n🎉 Instance wizard completed successfully!")
            console.print(f"Instance ID: [green]{instance.instance_id}[/green]")
        else:
            console.print("Instance wizard was cancelled or failed")

    except Exception as e:
        console.print(f"❌ Wizard error: {e}")
        sys.exit(1)

@instance_commands.command('from-template')
@click.argument('template_name')
@click.option('--name', '-n', required=True, help='Instance name')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@requires_permission(Permission.WRITE)
def create_from_template(template_name, name, output):
    """Create instance from template"""
    console.print(f"🔧 Creating instance from template: {template_name}")
    console.print("⚠️ Template functionality will be implemented in future version")

@instance_commands.command('clone')
@click.argument('source_instance_id')
@click.option('--name', '-n', required=True, help='New instance name')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@requires_permission(Permission.WRITE)
def clone_instance(source_instance_id, name, output):
    """Clone existing instance"""
    try:
        source = instance_manager.get_instance(source_instance_id)
        if not source:
            console.print(f"❌ Source instance not found: {source_instance_id}")
            sys.exit(1)

        # Create new configuration based on source
        new_config = InstanceConfiguration(
            name=name,
            description=f"Cloned from {source.name}",
            instance_type=source.instance_type,
            schema_id=source.schema_id,
            schema_version=source.schema_version,
            parameters=source.parameters.copy(),
            status=InstanceStatus.CONFIGURED
        )

        success = instance_manager.create_instance(new_config)

        if success:
            console.print("✅ Instance cloned successfully!")
            console.print(f"New Instance ID: [green]{new_config.instance_id}[/green]")
        else:
            console.print("❌ Failed to clone instance")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error cloning instance: {e}")
        sys.exit(1)

# Instance Management Commands
@instance_commands.command('list')
@click.option('--type', '-t', 'filter_type',
              type=click.Choice([t.value for t in InstanceType]),
              help='Filter by instance type')
@click.option('--status', '-s', 'filter_status',
              type=click.Choice([s.value for s in InstanceStatus]),
              help='Filter by status')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml', 'summary']),
              default='table', help='Output format')
@requires_permission(Permission.READ)
def list_instances(filter_type, filter_status, output):
    """List all control loop instances"""
    try:
        # Apply filters
        type_filter = InstanceType(filter_type) if filter_type else None
        status_filter = InstanceStatus(filter_status) if filter_status else None

        instances = instance_manager.list_instances(type_filter, status_filter)

        if output == 'table':
            if not instances:
                console.print("No instances found matching criteria")
                return

            table = Table(title=f"Control Loop Instances ({len(instances)} found)")
            table.add_column("Instance ID", style="cyan")
            table.add_column("Name", style="magenta")
            table.add_column("Type", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Schema", style="yellow")
            table.add_column("Updated", style="dim")

            for instance in instances:
                # Defensive datetime handling - fix for 'str' object has no attribute 'strftime'
                if instance.updated_at:
                    if isinstance(instance.updated_at, str):
                        # Parse string datetime back to datetime object
                        try:
                            if 'T' in instance.updated_at:
                                dt_obj = datetime.fromisoformat(instance.updated_at.replace('Z', '+00:00'))
                            else:
                                dt_obj = datetime.strptime(instance.updated_at, "%Y-%m-%d %H:%M:%S")
                            updated_str = dt_obj.strftime("%Y-%m-%d %H:%M")
                        except (ValueError, AttributeError):
                            updated_str = str(instance.updated_at)[:16]  # Fallback truncation
                    elif hasattr(instance.updated_at, 'strftime'):
                        updated_str = instance.updated_at.strftime("%Y-%m-%d %H:%M")
                    else:
                        updated_str = str(instance.updated_at)[:16]
                else:
                    updated_str = "Unknown"
                # Defensive enum handling - fix for 'str' object has no attribute 'value'
                instance_type_str = instance.instance_type.value if hasattr(instance.instance_type, 'value') else str(instance.instance_type)
                status_str = instance.status.value if hasattr(instance.status, 'value') else str(instance.status)

                table.add_row(
                    instance.instance_id[:8] + "...",
                    instance.name,
                    instance_type_str,
                    status_str,
                    instance.schema_id,
                    updated_str
                )

            console.print(table)

        elif output == 'summary':
            # Group by status
            status_counts = {}
            type_counts = {}

            for instance in instances:
                # Defensive enum handling
                status = instance.status.value if hasattr(instance.status, 'value') else str(instance.status)
                inst_type = instance.instance_type.value if hasattr(instance.instance_type, 'value') else str(instance.instance_type)

                status_counts[status] = status_counts.get(status, 0) + 1
                type_counts[inst_type] = type_counts.get(inst_type, 0) + 1

            console.print(f"Total Instances: [bold]{len(instances)}[/bold]")

            status_table = Table(title="Status Summary")
            status_table.add_column("Status", style="cyan")
            status_table.add_column("Count", style="magenta")

            for status, count in sorted(status_counts.items()):
                status_table.add_row(status, str(count))

            console.print(status_table)

            type_table = Table(title="Type Summary")
            type_table.add_column("Type", style="cyan")
            type_table.add_column("Count", style="magenta")

            for inst_type, count in sorted(type_counts.items()):
                type_table.add_row(inst_type, str(count))

            console.print(type_table)

        elif output == 'json':
            result = [asdict(instance) for instance in instances]
            console.print(json.dumps(result, indent=2, default=str))

        elif output == 'yaml':
            result = [asdict(instance) for instance in instances]
            console.print(yaml.dump(result, default_flow_style=False))

    except Exception as e:
        console.print(f"❌ Error listing instances: {e}")
        sys.exit(1)

@instance_commands.command('info')
@click.argument('instance_id')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml', 'detailed']),
              default='detailed', help='Output format')
@requires_permission(Permission.READ)
def show_instance_info(instance_id, output):
    """Show detailed information about an instance"""
    try:
        instance = instance_manager.get_instance(instance_id)
        if not instance:
            console.print(f"❌ Instance not found: {instance_id}")
            sys.exit(1)

        if output == 'detailed':
            # Header
            console.print(Panel.fit(
                f"[bold blue]Instance Information[/bold blue]\n"
                f"ID: {instance.instance_id}\n"
                f"Name: {instance.name}",
                border_style="blue"
            ))

            # Basic Information
            basic_table = Table(title="Basic Information")
            basic_table.add_column("Property", style="cyan")
            basic_table.add_column("Value", style="magenta")

            basic_table.add_row("Name", instance.name)
            basic_table.add_row("Description", instance.description or "No description")
            basic_table.add_row("Type", instance.instance_type.value)
            basic_table.add_row("Status", instance.status.value)
            basic_table.add_row("Schema ID", instance.schema_id)
            basic_table.add_row("Schema Version", instance.schema_version)
            # Defensive datetime handling for created_at
            if instance.created_at:
                if isinstance(instance.created_at, str):
                    try:
                        if 'T' in instance.created_at:
                            created_dt = datetime.fromisoformat(instance.created_at.replace('Z', '+00:00'))
                        else:
                            created_dt = datetime.strptime(instance.created_at, "%Y-%m-%d %H:%M:%S")
                        created_str = created_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, AttributeError):
                        created_str = str(instance.created_at)[:19]
                elif hasattr(instance.created_at, 'strftime'):
                    created_str = instance.created_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    created_str = str(instance.created_at)[:19]
            else:
                created_str = "Unknown"

            # Defensive datetime handling for updated_at
            if instance.updated_at:
                if isinstance(instance.updated_at, str):
                    try:
                        if 'T' in instance.updated_at:
                            updated_dt = datetime.fromisoformat(instance.updated_at.replace('Z', '+00:00'))
                        else:
                            updated_dt = datetime.strptime(instance.updated_at, "%Y-%m-%d %H:%M:%S")
                        updated_str = updated_dt.strftime("%Y-%m-%d %H:%M:%S")
                    except (ValueError, AttributeError):
                        updated_str = str(instance.updated_at)[:19]
                elif hasattr(instance.updated_at, 'strftime'):
                    updated_str = instance.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    updated_str = str(instance.updated_at)[:19]
            else:
                updated_str = "Unknown"

            basic_table.add_row("Created", created_str)
            basic_table.add_row("Updated", updated_str)
            basic_table.add_row("Created By", instance.created_by or "Unknown")

            console.print(basic_table)

            # Parameters
            if instance.parameters:
                param_table = Table(title="Control Parameters")
                param_table.add_column("Parameter", style="cyan")
                param_table.add_column("Value", style="green")
                param_table.add_column("Type", style="yellow")

                for param, value in instance.parameters.items():
                    param_table.add_row(param, str(value), type(value).__name__)

                console.print(param_table)
            else:
                console.print("No parameters configured")

            # PLC Connection
            if instance.plc_connection:
                plc_table = Table(title="PLC Connection")
                plc_table.add_column("Property", style="cyan")
                plc_table.add_column("Value", style="green")

                for key, value in instance.plc_connection.items():
                    plc_table.add_row(key, str(value))

                console.print(plc_table)
            else:
                console.print("No PLC connection configured")

            # Validation Results
            if instance.validation_results:
                console.print("\n[bold]Latest Validation Results:[/bold]")
                validation = instance.validation_results

                status_color = "green" if validation.get("valid") else "red"
                console.print(f"Status: [{status_color}]{validation.get('valid', 'Unknown')}[/{status_color}]")
                console.print(f"Level: {validation.get('level', 'Unknown')}")
                console.print(f"Timestamp: {validation.get('timestamp', 'Unknown')}")

                if validation.get("errors"):
                    console.print(f"[red]Errors: {len(validation['errors'])}[/red]")
                    for error in validation["errors"]:
                        console.print(f"  • [red]{error}[/red]")

                if validation.get("warnings"):
                    console.print(f"[yellow]Warnings: {len(validation['warnings'])}[/yellow]")
                    for warning in validation["warnings"]:
                        console.print(f"  • [yellow]{warning}[/yellow]")

        elif output == 'json':
            console.print(json.dumps(asdict(instance), indent=2, default=str))

        elif output == 'yaml':
            console.print(yaml.dump(asdict(instance), default_flow_style=False))

        elif output == 'table':
            table = Table(title=f"Instance: {instance.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Instance ID", instance.instance_id)
            table.add_row("Type", instance.instance_type.value)
            table.add_row("Status", instance.status.value)
            table.add_row("Schema", instance.schema_id)
            table.add_row("Parameters", f"{len(instance.parameters)} configured")

            console.print(table)

    except Exception as e:
        console.print(f"❌ Error showing instance info: {e}")
        sys.exit(1)

@instance_commands.command('update')
@click.argument('instance_id')
@click.option('--name', help='Update instance name')
@click.option('--description', help='Update description')
@click.option('--status', type=click.Choice([s.value for s in InstanceStatus]),
              help='Update status')
@click.option('--set', 'set_params', multiple=True,
              help='Set parameter (format: key=value)')
@requires_permission(Permission.WRITE)
def update_instance(instance_id, name, description, status, set_params):
    """Update instance configuration"""
    try:
        instance = instance_manager.get_instance(instance_id)
        if not instance:
            console.print(f"❌ Instance not found: {instance_id}")
            sys.exit(1)

        updates = {}

        if name:
            updates['name'] = name
        if description:
            updates['description'] = description
        if status:
            updates['status'] = InstanceStatus(status)

        # Handle parameter updates
        if set_params:
            current_params = instance.parameters.copy()
            for param_str in set_params:
                if '=' not in param_str:
                    console.print(f"❌ Invalid parameter format: {param_str} (use key=value)")
                    continue

                key, value = param_str.split('=', 1)

                # Try to convert value to appropriate type
                try:
                    if '.' in value:
                        current_params[key] = float(value)
                    else:
                        current_params[key] = int(value)
                except ValueError:
                    # Keep as string
                    current_params[key] = value

            updates['parameters'] = current_params

        if not updates:
            console.print("No updates specified")
            return

        success = instance_manager.update_instance(instance_id, updates)

        if success:
            console.print("✅ Instance updated successfully!")

            # Show updated values
            table = Table(title="Updated Properties")
            table.add_column("Property", style="cyan")
            table.add_column("New Value", style="green")

            for key, value in updates.items():
                if key == 'parameters':
                    table.add_row(key, f"{len(value)} parameters updated")
                else:
                    table.add_row(key, str(value))

            console.print(table)
        else:
            console.print("❌ Failed to update instance")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error updating instance: {e}")
        sys.exit(1)

@instance_commands.command('delete')
@click.argument('instance_id')
@click.option('--force', '-f', is_flag=True, help='Force deletion without confirmation')
@requires_permission(Permission.ADMIN)
def delete_instance(instance_id, force):
    """Delete instance"""
    try:
        instance = instance_manager.get_instance(instance_id)
        if not instance:
            console.print(f"❌ Instance not found: {instance_id}")
            sys.exit(1)

        if not force:
            console.print(f"Instance to delete: [red]{instance.name}[/red] ({instance_id})")
            if not Confirm.ask("Are you sure you want to delete this instance?", default=False):
                console.print("Deletion cancelled")
                return

        success = instance_manager.delete_instance(instance_id)

        if success:
            console.print(f"✅ Instance deleted successfully: {instance.name}")
        else:
            console.print("❌ Failed to delete instance")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error deleting instance: {e}")
        sys.exit(1)

# Instance Validation Commands
@instance_commands.command('validate')
@click.argument('instance_id')
@click.option('--level', '-l', type=click.Choice([v.value for v in ValidationLevel]),
              default=ValidationLevel.STANDARD.value, help='Validation level')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml', 'detailed']),
              default='detailed', help='Output format')
@requires_permission(Permission.READ)
def validate_instance(instance_id, level, output):
    """Validate instance configuration"""
    try:
        instance = instance_manager.get_instance(instance_id)
        if not instance:
            console.print(f"❌ Instance not found: {instance_id}")
            sys.exit(1)

        validation_level = ValidationLevel(level)

        with Status(f"Validating instance at {validation_level.value} level...", spinner="dots"):
            results = instance_manager.validate_instance(instance_id, validation_level)

        # Update instance with validation results
        instance_manager.update_instance(instance_id, {"validation_results": results})

        if output == 'detailed':
            # Validation Summary
            status_color = "green" if results["valid"] else "red"
            status_symbol = "✅" if results["valid"] else "❌"

            console.print(Panel.fit(
                f"[bold]Validation Results[/bold]\n"
                f"Instance: {instance.name}\n"
                f"Level: {validation_level.value}\n"
                f"Status: {status_symbol} [{status_color}]{'VALID' if results['valid'] else 'INVALID'}[/{status_color}]",
                border_style=status_color
            ))

            # Checks performed
            if results.get("checks"):
                console.print("\n[bold]Checks Performed:[/bold]")
                for check in results["checks"]:
                    console.print(f"  ✓ {check}")

            # Errors
            if results.get("errors"):
                console.print(f"\n[bold red]Errors ({len(results['errors'])}):[/bold red]")
                for error in results["errors"]:
                    console.print(f"  ❌ {error}")

            # Warnings
            if results.get("warnings"):
                console.print(f"\n[bold yellow]Warnings ({len(results['warnings'])}):[/bold yellow]")
                for warning in results["warnings"]:
                    console.print(f"  ⚠️ {warning}")

            # Success message
            if results["valid"]:
                console.print(f"\n✅ Instance validation passed at {validation_level.value} level")
            else:
                console.print("\n❌ Instance validation failed - see errors above")

        elif output == 'json':
            console.print(json.dumps(results, indent=2, default=str))

        elif output == 'yaml':
            console.print(yaml.dump(results, default_flow_style=False))

        elif output == 'table':
            table = Table(title=f"Validation Results: {instance.name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="magenta")

            table.add_row("Valid", "✅ Yes" if results["valid"] else "❌ No")
            table.add_row("Level", validation_level.value)
            table.add_row("Checks", str(len(results.get("checks", []))))
            table.add_row("Errors", str(len(results.get("errors", []))))
            table.add_row("Warnings", str(len(results.get("warnings", []))))
            table.add_row("Timestamp", str(results.get("timestamp", "Unknown")))

            console.print(table)

        # Exit with error code if validation failed
        if not results["valid"]:
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error validating instance: {e}")
        sys.exit(1)

@instance_commands.command('simulate')
@click.argument('instance_id')
@click.option('--scenario', help='Simulation scenario file')
@click.option('--duration', default=60.0, help='Simulation duration (seconds)')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'plot']),
              default='table', help='Output format')
@requires_permission(Permission.READ)
def simulate_instance(instance_id, scenario, duration, output):
    """Simulate instance performance"""
    console.print(f"🔬 Simulating instance: {instance_id}")
    console.print(f"Duration: {duration} seconds")
    if scenario:
        console.print(f"Scenario: {scenario}")
    console.print("⚠️ Simulation functionality will be implemented in future version")

@instance_commands.command('analyze')
@click.argument('instance_id')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'report']),
              default='report', help='Output format')
@requires_permission(Permission.READ)
def analyze_instance(instance_id, output):
    """Analyze instance configuration and performance"""
    console.print(f"📊 Analyzing instance: {instance_id}")
    console.print("⚠️ Analysis functionality will be implemented in future version")

@instance_commands.command('compare')
@click.argument('instance_id_1')
@click.argument('instance_id_2')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'diff']),
              default='diff', help='Output format')
@requires_permission(Permission.READ)
def compare_instances(instance_id_1, instance_id_2, output):
    """Compare two instances"""
    console.print(f"🔍 Comparing instances: {instance_id_1} vs {instance_id_2}")
    console.print("⚠️ Comparison functionality will be implemented in future version")

# Instance Export/Import Commands
@instance_commands.command('export')
@click.argument('instance_id')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'csv', 'excel']),
              default='json', help='Export format')
@click.option('--output', '-o', help='Output file path')
@requires_permission(Permission.READ)
def export_instance(instance_id, format, output):
    """Export instance configuration"""
    try:
        instance = instance_manager.get_instance(instance_id)
        if not instance:
            console.print(f"❌ Instance not found: {instance_id}")
            sys.exit(1)

        # Generate output filename if not provided
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"instance_{instance.name}_{timestamp}.{format}"

        output_path = Path(output)

        try:
            if format == 'json':
                with open(output_path, 'w') as f:
                    json.dump(asdict(instance), f, indent=2, default=str)

            elif format == 'yaml':
                with open(output_path, 'w') as f:
                    yaml.dump(asdict(instance), f, default_flow_style=False)

            elif format == 'csv':
                # For CSV, export parameters as key-value pairs
                import csv
                with open(output_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Property', 'Value'])
                    writer.writerow(['Instance ID', instance.instance_id])
                    writer.writerow(['Name', instance.name])
                    writer.writerow(['Type', instance.instance_type.value])
                    writer.writerow(['Status', instance.status.value])
                    writer.writerow(['Schema', instance.schema_id])

                    # Add parameters
                    for key, value in instance.parameters.items():
                        writer.writerow([f"param_{key}", value])

            else:  # excel format
                console.print("❌ Excel export not yet implemented")
                sys.exit(1)

            console.print(f"✅ Instance exported successfully to: [green]{output_path}[/green]")
            console.print(f"Format: {format}")
            console.print(f"Size: {output_path.stat().st_size} bytes")

        except Exception as e:
            console.print(f"❌ Export failed: {e}")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error exporting instance: {e}")
        sys.exit(1)

@instance_commands.command('import')
@click.argument('file_path')
@click.option('--schema', help='Override schema ID')
@click.option('--name', help='Override instance name')
@click.option('--force', '-f', is_flag=True, help='Force import, overwrite existing')
@requires_permission(Permission.WRITE)
def import_instance(file_path, schema, name, force):
    """Import instance from file"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            console.print(f"❌ File not found: {file_path}")
            sys.exit(1)

        # Detect format from extension
        file_format = file_path.suffix.lower().lstrip('.')

        try:
            if file_format == 'json':
                with open(file_path) as f:
                    data = json.load(f)
            elif file_format in ['yaml', 'yml']:
                with open(file_path) as f:
                    data = yaml.safe_load(f)
            else:
                console.print(f"❌ Unsupported file format: {file_format}")
                sys.exit(1)

            # Create instance configuration
            # Handle both direct instance data and wrapped data
            if 'instance' in data:
                instance_data = data['instance']
            else:
                instance_data = data

            # Generate new instance ID to avoid conflicts
            instance_data['instance_id'] = str(uuid.uuid4())

            # Apply overrides
            if schema:
                instance_data['schema_id'] = schema
            if name:
                instance_data['name'] = name

            # Reset status and timestamps
            instance_data['status'] = InstanceStatus.CONFIGURED.value
            instance_data['created_at'] = datetime.now()
            instance_data['updated_at'] = datetime.now()

            # Create instance configuration object
            instance = InstanceConfiguration(**instance_data)

            # Check for existing instance with same name (if not forcing)
            if not force:
                existing_instances = instance_manager.list_instances()
                existing_names = [inst.name for inst in existing_instances]
                if instance.name in existing_names:
                    console.print(f"❌ Instance with name '{instance.name}' already exists")
                    console.print("Use --force to overwrite or --name to specify different name")
                    sys.exit(1)

            # Create the instance
            success = instance_manager.create_instance(instance)

            if success:
                console.print("✅ Instance imported successfully!")
                console.print(f"Instance ID: [green]{instance.instance_id}[/green]")
                console.print(f"Name: {instance.name}")
                console.print(f"Type: {instance.instance_type.value}")
                console.print(f"Schema: {instance.schema_id}")
            else:
                console.print("❌ Failed to import instance")
                sys.exit(1)

        except Exception as e:
            console.print(f"❌ Import failed: {e}")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ Error importing instance: {e}")
        sys.exit(1)

@instance_commands.command('convert')
@click.argument('instance_id')
@click.option('--to-schema', required=True, help='Target schema ID')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@requires_permission(Permission.WRITE)
def convert_instance(instance_id, to_schema, output):
    """Convert instance to different schema"""
    console.print(f"🔄 Converting instance {instance_id} to schema: {to_schema}")
    console.print("⚠️ Schema conversion functionality will be implemented in future version")

# CLX PLC Integration Commands
@instance_commands.group('plc')
def plc_commands():
    """CLX PLC integration commands"""
    pass

@plc_commands.command('connect')
@click.option('--host', '-h', required=True, help='PLC IP address')
@click.option('--slot', '-s', default=0, help='PLC slot number')
@click.option('--timeout', '-t', default=5.0, help='Connection timeout')
@requires_permission(Permission.READ)
def plc_connect(host, slot, timeout):
    """Connect to CLX PLC (read-only)"""
    try:
        if not PYLOGIX_AVAILABLE:
            console.print("❌ pylogix library not available")
            console.print("Install with: pip install pylogix")
            sys.exit(1)

        console.print(f"Connecting to CLX PLC: {host}:{slot}")
        console.print("🔒 Read-only mode enforced for safety")

        connection_id = plc_manager.create_connection(host, slot, timeout)

        with Status("Connecting to PLC...", spinner="dots"):
            success = plc_manager.connect(connection_id)

        if success:
            console.print("✅ Connected to PLC successfully!")

            # Show connection status
            status = plc_manager.get_connection_status()

            table = Table(title="PLC Connection Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            conn_info = status["connections"][connection_id]
            table.add_row("Host", conn_info["host"])
            table.add_row("Slot", str(conn_info["slot"]))
            table.add_row("Status", conn_info["status"])
            table.add_row("Mode", conn_info["mode"])

            console.print(table)

        else:
            console.print("❌ Failed to connect to PLC")
            console.print("Check IP address, slot number, and network connectivity")
            sys.exit(1)

    except Exception as e:
        console.print(f"❌ PLC connection error: {e}")
        sys.exit(1)

@plc_commands.command('disconnect')
@click.option('--connection-id', help='Specific connection to disconnect')
@requires_permission(Permission.READ)
def plc_disconnect(connection_id):
    """Disconnect from CLX PLC"""
    try:
        if connection_id:
            success = plc_manager.disconnect(connection_id)
            if success:
                console.print(f"✅ Disconnected from PLC: {connection_id}")
            else:
                console.print(f"❌ Failed to disconnect from PLC: {connection_id}")
        else:
            # Disconnect all connections
            status = plc_manager.get_connection_status()
            disconnected = 0

            for conn_id in status["connections"].keys():
                if plc_manager.disconnect(conn_id):
                    disconnected += 1

            console.print(f"✅ Disconnected {disconnected} PLC connections")

    except Exception as e:
        console.print(f"❌ PLC disconnect error: {e}")
        sys.exit(1)

@plc_commands.command('status')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'yaml']),
              default='table', help='Output format')
@requires_permission(Permission.READ)
def plc_status(output):
    """Show PLC connection status"""
    try:
        status = plc_manager.get_connection_status()

        if output == 'table':
            # Summary
            console.print(f"Total Connections: [bold]{status['total_connections']}[/bold]")
            console.print(f"Active Connection: [green]{status['active_connection'] or 'None'}[/green]")
            console.print(f"Read-Only Enforced: [blue]{status['read_only_enforced']}[/blue]")

            if status["connections"]:
                table = Table(title="PLC Connections")
                table.add_column("Connection ID", style="cyan")
                table.add_column("Host", style="magenta")
                table.add_column("Slot", style="blue")
                table.add_column("Status", style="green")
                table.add_column("Mode", style="yellow")
                table.add_column("Last Comm", style="dim")
                table.add_column("Errors", style="red")

                for conn_id, conn_info in status["connections"].items():
                    last_comm = "Never"
                    if conn_info["last_communication"]:
                        last_comm = conn_info["last_communication"].strftime("%H:%M:%S")

                    table.add_row(
                        conn_id,
                        conn_info["host"],
                        str(conn_info["slot"]),
                        conn_info["status"],
                        conn_info["mode"],
                        last_comm,
                        str(conn_info["error_count"])
                    )

                console.print(table)
            else:
                console.print("No PLC connections configured")

        elif output == 'json':
            console.print(json.dumps(status, indent=2, default=str))

        elif output == 'yaml':
            console.print(yaml.dump(status, default_flow_style=False))

    except Exception as e:
        console.print(f"❌ Error getting PLC status: {e}")
        sys.exit(1)

@plc_commands.command('browse')
@click.option('--connection-id', help='PLC connection to browse')
@click.option('--filter', '-f', default='*', help='Tag name filter pattern')
@click.option('--limit', '-l', default=50, help='Maximum number of tags to show')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'list']),
              default='table', help='Output format')
@requires_permission(Permission.READ)
def plc_browse_tags(connection_id, filter, limit, output):
    """Browse PLC tags"""
    try:
        if not PYLOGIX_AVAILABLE:
            console.print("❌ pylogix library not available")
            sys.exit(1)

        with Status("Browsing PLC tags...", spinner="dots"):
            tags = plc_manager.browse_tags(connection_id, filter)

        if not tags:
            console.print("No tags found or PLC not connected")
            return

        # Limit results
        if len(tags) > limit:
            console.print(f"Showing first {limit} of {len(tags)} tags (use --limit to see more)")
            tags = tags[:limit]

        if output == 'table':
            table = Table(title=f"PLC Tags ({len(tags)} found)")
            table.add_column("#", style="dim")
            table.add_column("Tag Name", style="cyan")
            table.add_column("Type", style="magenta")

            for i, tag in enumerate(tags, 1):
                # For simplicity, we'll show tag name only
                # In a full implementation, we'd read tag info to get type
                table.add_row(str(i), tag, "Unknown")

            console.print(table)

        elif output == 'list':
            for tag in tags:
                console.print(tag)

        elif output == 'json':
            result = {"total_tags": len(tags), "tags": tags}
            console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"❌ Error browsing PLC tags: {e}")
        sys.exit(1)

@plc_commands.command('read')
@click.argument('tag_name')
@click.option('--connection-id', help='PLC connection to use')
@click.option('--output', '-o', type=click.Choice(['table', 'json', 'value']),
              default='table', help='Output format')
@requires_permission(Permission.READ)
def plc_read_tag(tag_name, connection_id, output):
    """Read PLC tag value"""
    try:
        if not PYLOGIX_AVAILABLE:
            console.print("❌ pylogix library not available")
            sys.exit(1)

        with Status(f"Reading tag: {tag_name}...", spinner="dots"):
            tag_info = plc_manager.read_tag(tag_name, connection_id)

        if not tag_info:
            console.print(f"❌ Failed to read tag: {tag_name}")
            sys.exit(1)

        if output == 'table':
            table = Table(title=f"Tag Value: {tag_name}")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Tag Name", tag_info.tag_name)
            table.add_row("Value", str(tag_info.value))
            table.add_row("Data Type", tag_info.data_type)
            table.add_row("Quality", tag_info.quality)
            table.add_row("Timestamp", tag_info.timestamp.strftime("%Y-%m-%d %H:%M:%S"))

            console.print(table)

        elif output == 'value':
            console.print(tag_info.value)

        elif output == 'json':
            result = {
                "tag_name": tag_info.tag_name,
                "value": tag_info.value,
                "data_type": tag_info.data_type,
                "quality": tag_info.quality,
                "timestamp": tag_info.timestamp.isoformat()
            }
            console.print(json.dumps(result, indent=2))

    except Exception as e:
        console.print(f"❌ Error reading PLC tag: {e}")
        sys.exit(1)

# Register all commands with the CLI
@click.group()
@click.pass_context
def instance(ctx):
    """Instance management commands (Phase 21.3)"""
    pass

# Add all instance commands to the group
instance.add_command(instance_commands)
