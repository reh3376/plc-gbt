#!/usr/bin/env python3
"""
🖥️ Phase 21: Advanced CLI Control Loop Management - Main Entry Point

Comprehensive command-line interface for control loop schema management, instance
creation, validation, and advanced operations.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (500-1500 lines, 5-15 files, 3-8 hours)  
Context Management: Standard planning with domain awareness
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21 Objectives:
- Create powerful CLI for complete control loop management
- Support schema operations (create, modify, validate, version)
- Enable instance management with guided creation
- Provide advanced features (batch, scripting, REPL, plugins)
- Integrate with existing plc-memory and security systems

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.1 - Core CLI Infrastructure  
Dependencies: Phase 20 (JSON Schema Framework), Phase 15/17 (Security)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich import print as rprint

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up rich console and logging
console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CORE CONSTANTS AND ENUMERATIONS
# =============================================================================

CLI_VERSION = "1.0.0"
CONFIG_FILE_NAME = ".plc-cl-config"
DEFAULT_CONFIG_DIR = Path.home() / ".plc-control-loop"

class OutputFormat(Enum):
    """Supported output formats"""
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

# =============================================================================
# CONFIGURATION MANAGEMENT
# =============================================================================

@dataclass
class CLIConfiguration:
    """CLI configuration settings"""
    # General settings
    default_output_format: str = "table"
    default_schema_registry: str = "plc-gbt-stack/schemas"
    default_instances_dir: str = "plc-gbt-stack/instances"
    
    # Authentication settings
    auth_enabled: bool = True
    api_base_url: str = "http://localhost:8000"
    session_timeout: int = 3600  # 1 hour
    
    # Performance settings
    max_concurrent_operations: int = 5
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes
    
    # Logging settings
    log_level: str = "info"
    log_file: Optional[str] = None
    verbose: bool = False
    
    # Advanced settings
    editor: str = os.environ.get("EDITOR", "nano")
    pager: str = os.environ.get("PAGER", "less")
    color_output: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CLIConfiguration":
        """Create from dictionary"""
        return cls(**data)

class ConfigurationManager:
    """Manages CLI configuration persistence and loading"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or DEFAULT_CONFIG_DIR
        self.config_file = self.config_dir / CONFIG_FILE_NAME
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config: Optional[CLIConfiguration] = None
        
    def load_config(self) -> CLIConfiguration:
        """Load configuration from file or create default"""
        if self._config:
            return self._config
            
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                self._config = CLIConfiguration.from_dict(config_data)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to load config, using defaults: {e}[/yellow]")
                self._config = CLIConfiguration()
        else:
            self._config = CLIConfiguration()
            self.save_config()
            
        return self._config
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        if not self._config:
            return False
            
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config.to_dict(), f, default_flow_style=False)
            return True
        except Exception as e:
            console.print(f"[red]Error saving config: {e}[/red]")
            return False
    
    def update_setting(self, key: str, value: Any) -> bool:
        """Update a specific configuration setting"""
        config = self.load_config()
        if hasattr(config, key):
            setattr(config, key, value)
            self._config = config
            return self.save_config()
        return False
    
    def reset_config(self) -> bool:
        """Reset configuration to defaults"""
        self._config = CLIConfiguration()
        return self.save_config()

# =============================================================================
# CLI CONTEXT AND STATE MANAGEMENT
# =============================================================================

class CLIContext:
    """Global CLI context and state management"""
    
    def __init__(self):
        self.config_manager = ConfigurationManager()
        self.config = self.config_manager.load_config()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = datetime.now()
        
        # State tracking
        self.current_schema: Optional[str] = None
        self.current_instance: Optional[str] = None
        self.operation_count = 0
        self.errors: List[str] = []
        
        # Performance tracking
        self.command_times: Dict[str, float] = {}
        
    def log_operation(self, operation: str, duration: float):
        """Log operation for performance tracking"""
        self.operation_count += 1
        self.command_times[operation] = duration
        
        if self.config.verbose:
            console.print(f"[dim]Operation '{operation}' completed in {duration:.3f}s[/dim]")
    
    def add_error(self, error: str):
        """Add error to tracking"""
        self.errors.append(error)
        logger.error(error)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session summary statistics"""
        session_duration = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "session_id": self.session_id,
            "duration_seconds": session_duration,
            "operations_performed": self.operation_count,
            "errors_encountered": len(self.errors),
            "average_command_time": sum(self.command_times.values()) / len(self.command_times) if self.command_times else 0,
            "config_file": str(self.config_manager.config_file)
        }

# =============================================================================
# AUTHENTICATION AND AUTHORIZATION
# =============================================================================

class AuthenticationManager:
    """Manages CLI authentication and authorization"""
    
    def __init__(self, config: CLIConfiguration):
        self.config = config
        self.session_token: Optional[str] = None
        self.user_info: Optional[Dict[str, Any]] = None
        
    async def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Authenticate user with the system"""
        if not self.config.auth_enabled:
            return True
            
        # For Phase 21.1, implement basic authentication
        # In future phases, integrate with Phase 15/17 security
        
        if not username:
            username = Prompt.ask("Username", default="admin")
        
        if not password:
            password = Prompt.ask("Password", password=True)
        
        # Placeholder authentication logic
        # TODO: Integrate with actual security system in Phase 21.5
        if username and password:
            self.session_token = f"session_{datetime.now().timestamp()}"
            self.user_info = {
                "username": username,
                "authenticated_at": datetime.now().isoformat(),
                "permissions": ["read", "write", "admin"]  # Placeholder
            }
            console.print(f"[green]✅ Authenticated as {username}[/green]")
            return True
        
        console.print("[red]❌ Authentication failed[/red]")
        return False
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        if not self.config.auth_enabled:
            return True
        return self.session_token is not None
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if not self.config.auth_enabled:
            return True
        
        if not self.user_info:
            return False
        
        return permission in self.user_info.get("permissions", [])
    
    def logout(self):
        """Logout current session"""
        self.session_token = None
        self.user_info = None
        console.print("[yellow]👋 Logged out[/yellow]")

# =============================================================================
# ERROR HANDLING AND UTILITIES
# =============================================================================

class CLIError(Exception):
    """Base CLI error class"""
    pass

def handle_cli_error(func):
    """Decorator for handling CLI errors gracefully"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CLIError as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            sys.exit(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]⚠️  Operation cancelled by user[/yellow]")
            sys.exit(130)
        except Exception as e:
            console.print(f"[red]💥 Unexpected error: {str(e)}[/red]")
            if os.environ.get("CLI_DEBUG"):
                raise
            sys.exit(1)
    return wrapper

def async_command(func):
    """Decorator to run async functions in Click commands"""
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

# =============================================================================
# OUTPUT FORMATTING UTILITIES
# =============================================================================

class OutputFormatter:
    """Handles various output formats for CLI responses"""
    
    @staticmethod
    def format_output(data: Any, format_type: str = "table", title: Optional[str] = None) -> None:
        """Format and display output in specified format"""
        if format_type == "json":
            OutputFormatter._format_json(data)
        elif format_type == "yaml":
            OutputFormatter._format_yaml(data)
        elif format_type == "csv":
            OutputFormatter._format_csv(data)
        else:  # table (default)
            OutputFormatter._format_table(data, title)
    
    @staticmethod
    def _format_json(data: Any):
        """Format output as JSON"""
        console.print_json(json.dumps(data, indent=2, default=str))
    
    @staticmethod
    def _format_yaml(data: Any):
        """Format output as YAML"""
        yaml_str = yaml.dump(data, default_flow_style=False)
        console.print(f"[dim]{yaml_str}[/dim]")
    
    @staticmethod
    def _format_csv(data: Any):
        """Format output as CSV"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            console.print(output.getvalue())
        else:
            console.print("[yellow]Warning: CSV format only supports list of dictionaries[/yellow]")
    
    @staticmethod
    def _format_table(data: Any, title: Optional[str] = None):
        """Format output as rich table"""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            table = Table(title=title)
            
            # Add columns
            for key in data[0].keys():
                table.add_column(str(key).replace('_', ' ').title())
            
            # Add rows
            for item in data:
                table.add_row(*[str(v) for v in item.values()])
            
            console.print(table)
        elif isinstance(data, dict):
            table = Table(title=title or "Data")
            table.add_column("Property")
            table.add_column("Value")
            
            for key, value in data.items():
                table.add_row(str(key).replace('_', ' ').title(), str(value))
            
            console.print(table)
        else:
            console.print(data)

# =============================================================================
# MAIN CLI GROUP AND SETUP
# =============================================================================

@click.group()
@click.version_option(version=CLI_VERSION, prog_name="plc-cl")
@click.option('--config-dir', type=click.Path(), 
              help='Configuration directory path')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output')
@click.option('--quiet', '-q', is_flag=True, 
              help='Suppress non-error output') 
@click.option('--format', type=click.Choice(['table', 'json', 'yaml', 'csv']),
              help='Output format')
@click.option('--no-color', is_flag=True,
              help='Disable colored output')
@click.pass_context
@handle_cli_error
def cli(ctx, config_dir, verbose, quiet, format, no_color):
    """
    🖥️ PLC Control Loop CLI - Advanced Control Loop Management
    
    Comprehensive command-line interface for control loop schema management,
    instance creation, validation, and advanced operations.
    
    Examples:
        plc-cl status
        plc-cl schema list
        plc-cl instance create --schema=standard-pid --name=my-controller
        plc-cl batch validate --pattern="*.json"
        plc-cl repl
    """
    # Initialize CLI context
    cli_ctx = CLIContext()
    
    # Override config directory if specified
    if config_dir:
        cli_ctx.config_manager = ConfigurationManager(Path(config_dir))
        cli_ctx.config = cli_ctx.config_manager.load_config()
    
    # Apply command-line overrides
    if verbose:
        cli_ctx.config.verbose = True
        logging.getLogger().setLevel(logging.DEBUG)
    
    if quiet:
        cli_ctx.config.verbose = False
        logging.getLogger().setLevel(logging.WARNING)
    
    if format:
        cli_ctx.config.default_output_format = format
    
    if no_color:
        cli_ctx.config.color_output = False
        console.no_color = True
    
    # Store context for subcommands
    ctx.obj = cli_ctx
    
    # Initialize authentication manager
    cli_ctx.auth_manager = AuthenticationManager(cli_ctx.config)

# =============================================================================
# MAIN STATUS COMMAND
# =============================================================================

@cli.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed status')
@click.option('--format', type=click.Choice(['table', 'json']),
              help='Output format')
@click.pass_context
def status(ctx, detailed, format):
    """Show system status and health"""
    try:
        cli_ctx: CLIContext = ctx.obj
        
        status_info = {
            "cli_version": CLI_VERSION,
            "session_id": cli_ctx.session_id,
            "config_file": str(cli_ctx.config_manager.config_file),
            "authenticated": cli_ctx.auth_manager.is_authenticated() if hasattr(cli_ctx, 'auth_manager') else False,
            "operations_performed": cli_ctx.operation_count,
            "errors_encountered": len(cli_ctx.errors)
        }
        
        if detailed:
            status_info.update(cli_ctx.get_session_summary())
            
            # Check schema registry
            schema_registry_path = Path(cli_ctx.config.default_schema_registry)
            status_info["schema_registry"] = {
                "path": str(schema_registry_path),
                "exists": schema_registry_path.exists(),
                "schemas_available": len(list(schema_registry_path.glob("**/*.json"))) if schema_registry_path.exists() else 0
            }
            
            # Check instances directory  
            instances_path = Path(cli_ctx.config.default_instances_dir)
            status_info["instances_directory"] = {
                "path": str(instances_path),
                "exists": instances_path.exists(),
                "instances_available": len(list(instances_path.glob("**/*.json"))) if instances_path.exists() else 0
            }
        
        OutputFormatter.format_output(
            status_info,
            format or cli_ctx.config.default_output_format,
            "System Status"
        )
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

@cli.command()
@click.pass_context
def version(ctx):
    """Show version information"""
    version_info = {
        "cli_version": CLI_VERSION,
        "python_version": sys.version.split()[0],
        "platform": sys.platform,
        "executable": sys.executable
    }
    
    panel = Panel(
        f"[bold]PLC Control Loop CLI[/bold]\n\n"
        f"Version: {CLI_VERSION}\n"
        f"Python: {sys.version.split()[0]}\n"  
        f"Platform: {sys.platform}",
        title="Version Information",
        border_style="blue"
    )
    
    console.print(panel)

# =============================================================================
# CONFIGURATION COMMANDS
# =============================================================================

@cli.group()
@click.pass_context
def config(ctx):
    """Configuration management commands"""
    pass

@config.command()
@click.option('--format', type=click.Choice(['table', 'json', 'yaml']), 
              default='table', help='Output format')
@click.pass_context
def show(ctx, format):
    """Show current configuration"""
    try:
        cli_ctx: CLIContext = ctx.obj
        config_dict = cli_ctx.config.to_dict()
        
        OutputFormatter.format_output(
            config_dict, 
            format or cli_ctx.config.default_output_format,
            "Current Configuration"
        )
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

@config.command()
@click.argument('key')
@click.argument('value')
@click.pass_context
def set(ctx, key, value):
    """Set configuration value"""
    try:
        cli_ctx: CLIContext = ctx.obj
        
        # Type conversion for common settings
        if key in ['verbose', 'auth_enabled', 'cache_enabled', 'color_output']:
            value = value.lower() in ('true', '1', 'yes', 'on')
        elif key in ['session_timeout', 'max_concurrent_operations', 'cache_ttl']:
            value = int(value)
        
        if cli_ctx.config_manager.update_setting(key, value):
            console.print(f"[green]✅ Set {key} = {value}[/green]")
        else:
            console.print(f"[red]❌ Invalid configuration key: {key}[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

@config.command()
@click.pass_context
def reset(ctx):
    """Reset configuration to defaults"""
    try:
        cli_ctx: CLIContext = ctx.obj
        
        if Confirm.ask("Are you sure you want to reset all configuration to defaults?"):
            if cli_ctx.config_manager.reset_config():
                console.print("[green]✅ Configuration reset to defaults[/green]")
            else:
                console.print("[red]❌ Failed to reset configuration[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# AUTHENTICATION COMMANDS
# =============================================================================

@cli.group()
@click.pass_context
def auth(ctx):
    """Authentication and authorization commands"""
    pass

@auth.command()
@click.option('--username', '-u', prompt=True, help='Username')
@click.option('--password', '-p', prompt=True, hide_input=True, help='Password')
@click.pass_context
def login(ctx, username, password):
    """Login to the system"""
    @async_command
    async def _login_async():
        cli_ctx: CLIContext = ctx.obj
        return await cli_ctx.auth_manager.authenticate(username, password)
    
    try:
        success = _login_async()
        if not success:
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

@auth.command()
@click.pass_context
def logout(ctx):
    """Logout from the system"""
    try:
        cli_ctx: CLIContext = ctx.obj
        cli_ctx.auth_manager.logout()
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

@auth.command()
@click.pass_context
def status(ctx):
    """Show authentication status"""
    try:
        cli_ctx: CLIContext = ctx.obj
        auth_manager = cli_ctx.auth_manager
        
        if auth_manager.is_authenticated():
            user_info = auth_manager.user_info or {}
            console.print(f"[green]✅ Authenticated as: {user_info.get('username', 'Unknown')}[/green]")
            console.print(f"[dim]Session token: {auth_manager.session_token[:20]}...[/dim]")
            console.print(f"[dim]Permissions: {', '.join(user_info.get('permissions', []))}[/dim]")
        else:
            console.print("[red]❌ Not authenticated[/red]")
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# COMMAND GROUP IMPORTS AND REGISTRATION  
# =============================================================================

# Import command groups if available
try:
    from cli.commands.schema import schema_commands
    SCHEMA_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Schema commands not available: {e}")
    SCHEMA_COMMANDS_AVAILABLE = False

try:
    from cli.commands.instance import instance_commands
    INSTANCE_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Instance commands not available: {e}")
    INSTANCE_COMMANDS_AVAILABLE = False

try:
    from cli.commands.batch import batch_commands
    BATCH_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Batch commands not available: {e}")
    BATCH_COMMANDS_AVAILABLE = False

try:
    from cli.plugins.plugin_manager import plugin_commands
    PLUGIN_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Plugin commands not available: {e}")
    PLUGIN_COMMANDS_AVAILABLE = False

try:
    from cli.automation.script_engine import automation_commands
    AUTOMATION_COMMANDS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Automation commands not available: {e}")
    AUTOMATION_COMMANDS_AVAILABLE = False

# Register schema commands if available
if SCHEMA_COMMANDS_AVAILABLE:
    cli.add_command(schema_commands, name='schema')
else:
    # Fallback placeholder
    @cli.group()
    @click.pass_context
    def schema(ctx):
        """Schema management commands (Phase 21.2)"""
        console.print("[yellow]⚠️  Schema commands not available - check installation[/yellow]")

# Register instance commands if available  
if INSTANCE_COMMANDS_AVAILABLE:
    cli.add_command(instance_commands, name='instance')
else:
    # Fallback placeholder
    @cli.group()
    @click.pass_context
    def instance(ctx):
        """Instance management commands (Phase 21.3)"""
        console.print("[yellow]⚠️  Instance commands not available - check installation[/yellow]")

# Register batch commands if available
if BATCH_COMMANDS_AVAILABLE:
    cli.add_command(batch_commands, name='batch')
else:
    # Fallback placeholder
    @cli.group()
    @click.pass_context
    def batch(ctx):
        """Batch operations commands (Phase 21.4)"""
        console.print("[yellow]⚠️  Batch commands not available - check installation[/yellow]")

# Register plugin commands if available
if PLUGIN_COMMANDS_AVAILABLE:
    cli.add_command(plugin_commands, name='plugin')
else:
    # Fallback placeholder
    @cli.group()
    @click.pass_context
    def plugin(ctx):
        """Plugin management commands (Phase 21.5)"""
        console.print("[yellow]⚠️  Plugin commands not available - check installation[/yellow]")

# Register automation commands if available
if AUTOMATION_COMMANDS_AVAILABLE:
    cli.add_command(automation_commands, name='automation')
else:
    # Fallback placeholder
    @cli.group()
    @click.pass_context
    def automation(ctx):
        """Automation commands (Phase 21.6)"""
        console.print("[yellow]⚠️  Automation commands not available - check installation[/yellow]")

@cli.command()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--save-session', is_flag=True, help='Auto-save session on exit')
@click.pass_context
def repl(ctx, verbose, save_session):
    """Interactive REPL mode for real-time operations"""
    try:
        from cli.repl.interactive_repl import PLCControlREPL
        
        cli_context = ctx.obj if ctx else None
        repl_instance = PLCControlREPL(cli_context)
        
        # Configure REPL
        repl_instance.session.verbose = verbose
        repl_instance.session.auto_save = save_session
        
        # Start REPL
        repl_instance.start()
        
    except ImportError as e:
        console.print(f"[red]❌ REPL not available: {e}[/red]")
        console.print("[yellow]💡 Try: pip install prompt_toolkit[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ REPL error: {e}[/red]")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point for CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Goodbye![/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]💥 Critical error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == '__main__':
    main() 