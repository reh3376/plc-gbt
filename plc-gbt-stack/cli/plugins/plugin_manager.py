#!/usr/bin/env python3
"""
🖥️ Phase 21.4: Plugin System

Extensible plugin architecture for custom CLI functionality with dynamic loading,
validation, dependency management, and lifecycle control. Enables users and developers
to extend the CLI with custom commands, processors, and integrations.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (400-600 lines, extensible architecture)
Context Management: Dynamic loading with security and validation
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.4 Objectives:
- Dynamic plugin discovery and loading system
- Plugin validation and security framework
- Dependency management and version compatibility
- Plugin lifecycle management (install, enable, disable, uninstall)
- Template system for plugin development

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.4.3 - Plugin System
Dependencies: Phase 21.1 (CLI Framework), importlib, packaging
"""

import os
import sys
import json
import importlib
import importlib.util
import logging
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Type
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import inspect
from abc import ABC, abstractmethod
import hashlib

# Third-party imports
try:
    import packaging.version
    PACKAGING_AVAILABLE = True
except ImportError:
    PACKAGING_AVAILABLE = False

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich import print as rprint

# Project imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up console and logging
console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# PLUGIN SYSTEM ENUMS AND DATA STRUCTURES
# =============================================================================

class PluginStatus(Enum):
    """Plugin status states"""
    INSTALLED = "installed"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ERROR = "error"
    LOADING = "loading"
    UNINSTALLED = "uninstalled"

class PluginType(Enum):
    """Plugin types"""
    COMMAND = "command"
    PROCESSOR = "processor"
    INTEGRATION = "integration"
    EXTENSION = "extension"
    THEME = "theme"

class PluginPriority(Enum):
    """Plugin loading priority"""
    CRITICAL = 0
    HIGH = 10
    NORMAL = 50
    LOW = 100

@dataclass
class PluginMetadata:
    """Plugin metadata structure"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    priority: PluginPriority = PluginPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    cli_version_min: str = "1.0.0"
    cli_version_max: str = "2.0.0"
    entry_point: str = "main"
    config_schema: Dict[str, Any] = field(default_factory=dict)
    permissions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    website: str = ""
    license: str = "Unknown"

@dataclass
class PluginInstance:
    """Runtime plugin instance"""
    metadata: PluginMetadata
    module: Any = None
    entry_function: Callable = None
    status: PluginStatus = PluginStatus.INSTALLED
    install_path: Path = None
    config: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    load_time: Optional[datetime] = None
    last_used: Optional[datetime] = None

class PluginInterface(ABC):
    """Base interface for plugins"""
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def initialize(self, cli_context, config: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        pass
    
    @abstractmethod
    def get_commands(self) -> List[click.Command]:
        """Return list of CLI commands provided by this plugin"""
        pass
    
    def cleanup(self):
        """Cleanup plugin resources"""
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        return True

# =============================================================================
# PLUGIN MANAGER
# =============================================================================

class PluginManager:
    """Comprehensive plugin management system"""
    
    def __init__(self, plugins_dir: Path = None, cli_context=None):
        self.cli_context = cli_context
        self.plugins_dir = plugins_dir or Path.home() / ".plc-cl" / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)
        
        # Plugin registry
        self.plugins: Dict[str, PluginInstance] = {}
        self.plugin_commands: Dict[str, List[click.Command]] = {}
        
        # Configuration
        self.config_file = self.plugins_dir / "plugins.json"
        self.config = self._load_config()
        
        # Security settings
        self.allow_unsigned = self.config.get("allow_unsigned_plugins", False)
        self.auto_enable = self.config.get("auto_enable_plugins", False)
        
        # Plugin templates directory
        self.templates_dir = Path(__file__).parent / "templates"
        
    def _load_config(self) -> Dict[str, Any]:
        """Load plugin configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load plugin config: {e}")
        
        return {
            "allow_unsigned_plugins": False,
            "auto_enable_plugins": False,
            "plugin_directories": [str(self.plugins_dir)],
            "disabled_plugins": [],
            "plugin_configs": {}
        }
    
    def _save_config(self):
        """Save plugin configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save plugin config: {e}")
    
    def discover_plugins(self) -> List[Path]:
        """Discover available plugins in plugin directories"""
        plugin_paths = []
        
        for plugin_dir in self.config.get("plugin_directories", []):
            plugin_dir = Path(plugin_dir)
            if plugin_dir.exists():
                # Look for plugin files and directories
                for item in plugin_dir.iterdir():
                    if item.is_file() and item.suffix == '.py':
                        plugin_paths.append(item)
                    elif item.is_dir():
                        # Look for __init__.py or main.py
                        init_file = item / "__init__.py"
                        main_file = item / "main.py"
                        if init_file.exists():
                            plugin_paths.append(init_file)
                        elif main_file.exists():
                            plugin_paths.append(main_file)
        
        return plugin_paths
    
    def load_plugin_metadata(self, plugin_path: Path) -> Optional[PluginMetadata]:
        """Load plugin metadata from file"""
        try:
            # Load the module to extract metadata
            spec = importlib.util.spec_from_file_location("plugin_module", plugin_path)
            if not spec or not spec.loader:
                return None
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for metadata in various forms
            metadata = None
            
            # Check for PLUGIN_METADATA constant
            if hasattr(module, 'PLUGIN_METADATA'):
                metadata_dict = module.PLUGIN_METADATA
                metadata = PluginMetadata(**metadata_dict)
            
            # Check for get_metadata function
            elif hasattr(module, 'get_metadata'):
                metadata = module.get_metadata()
            
            # Check for plugin class implementing PluginInterface
            elif hasattr(module, 'Plugin'):
                plugin_class = module.Plugin
                if issubclass(plugin_class, PluginInterface):
                    plugin_instance = plugin_class()
                    metadata = plugin_instance.get_metadata()
            
            return metadata
            
        except Exception as e:
            logger.error(f"Failed to load metadata from {plugin_path}: {e}")
            return None
    
    def validate_plugin(self, plugin_path: Path, metadata: PluginMetadata) -> bool:
        """Validate plugin before loading"""
        try:
            # Check CLI version compatibility
            if PACKAGING_AVAILABLE:
                cli_version = "1.0.0"  # Would get from actual CLI version
                if not (packaging.version.parse(metadata.cli_version_min) <= 
                       packaging.version.parse(cli_version) <= 
                       packaging.version.parse(metadata.cli_version_max)):
                    logger.error(f"Plugin {metadata.name} incompatible with CLI version {cli_version}")
                    return False
            
            # Check dependencies
            for dep in metadata.dependencies:
                if dep not in self.plugins:
                    logger.error(f"Plugin {metadata.name} depends on missing plugin: {dep}")
                    return False
            
            # Security check (basic)
            if not self.allow_unsigned and not self._is_plugin_signed(plugin_path):
                logger.warning(f"Plugin {metadata.name} is not signed")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Plugin validation failed: {e}")
            return False
    
    def _is_plugin_signed(self, plugin_path: Path) -> bool:
        """Check if plugin is digitally signed (mock implementation)"""
        # In a real implementation, would check digital signatures
        signature_file = plugin_path.parent / f"{plugin_path.stem}.sig"
        return signature_file.exists() or self.allow_unsigned
    
    def load_plugin(self, plugin_path: Path) -> bool:
        """Load a single plugin"""
        try:
            # Load metadata
            metadata = self.load_plugin_metadata(plugin_path)
            if not metadata:
                logger.error(f"Failed to load metadata from {plugin_path}")
                return False
            
            # Validate plugin
            if not self.validate_plugin(plugin_path, metadata):
                return False
            
            # Check if already loaded
            if metadata.name in self.plugins:
                logger.warning(f"Plugin {metadata.name} already loaded")
                return False
            
            # Check if disabled
            if metadata.name in self.config.get("disabled_plugins", []):
                logger.info(f"Plugin {metadata.name} is disabled")
                return False
            
            # Load the module
            spec = importlib.util.spec_from_file_location(f"plugin_{metadata.name}", plugin_path)
            if not spec or not spec.loader:
                return False
            
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Create plugin instance
            plugin_instance = PluginInstance(
                metadata=metadata,
                module=module,
                status=PluginStatus.LOADING,
                install_path=plugin_path,
                config=self.config.get("plugin_configs", {}).get(metadata.name, {})
            )
            
            # Initialize plugin
            if hasattr(module, 'initialize'):
                init_result = module.initialize(self.cli_context, plugin_instance.config)
                if not init_result:
                    plugin_instance.status = PluginStatus.ERROR
                    plugin_instance.error_message = "Initialization failed"
                    return False
            
            # Get commands
            commands = []
            if hasattr(module, 'get_commands'):
                commands = module.get_commands()
            elif hasattr(module, 'commands'):
                commands = module.commands
            
            # Register plugin
            plugin_instance.status = PluginStatus.ENABLED
            plugin_instance.load_time = datetime.now()
            self.plugins[metadata.name] = plugin_instance
            self.plugin_commands[metadata.name] = commands
            
            logger.info(f"Loaded plugin: {metadata.name} v{metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_path}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a plugin"""
        try:
            if plugin_name not in self.plugins:
                return False
            
            plugin = self.plugins[plugin_name]
            
            # Call cleanup if available
            if plugin.module and hasattr(plugin.module, 'cleanup'):
                plugin.module.cleanup()
            
            # Remove from registry
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_commands:
                del self.plugin_commands[plugin_name]
            
            logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unload plugin {plugin_name}: {e}")
            return False
    
    def enable_plugin(self, plugin_name: str) -> bool:
        """Enable a plugin"""
        try:
            disabled_plugins = self.config.get("disabled_plugins", [])
            if plugin_name in disabled_plugins:
                disabled_plugins.remove(plugin_name)
                self.config["disabled_plugins"] = disabled_plugins
                self._save_config()
            
            # If plugin is loaded, mark as enabled
            if plugin_name in self.plugins:
                self.plugins[plugin_name].status = PluginStatus.ENABLED
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to enable plugin {plugin_name}: {e}")
            return False
    
    def disable_plugin(self, plugin_name: str) -> bool:
        """Disable a plugin"""
        try:
            disabled_plugins = self.config.get("disabled_plugins", [])
            if plugin_name not in disabled_plugins:
                disabled_plugins.append(plugin_name)
                self.config["disabled_plugins"] = disabled_plugins
                self._save_config()
            
            # If plugin is loaded, mark as disabled and unload
            if plugin_name in self.plugins:
                self.plugins[plugin_name].status = PluginStatus.DISABLED
                return self.unload_plugin(plugin_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to disable plugin {plugin_name}: {e}")
            return False
    
    def install_plugin(self, plugin_source: Union[str, Path]) -> bool:
        """Install a plugin from file or URL"""
        try:
            plugin_source = Path(plugin_source)
            
            if not plugin_source.exists():
                logger.error(f"Plugin file not found: {plugin_source}")
                return False
            
            # Load metadata to get plugin name
            metadata = self.load_plugin_metadata(plugin_source)
            if not metadata:
                logger.error("Failed to load plugin metadata")
                return False
            
            # Create plugin directory
            plugin_dir = self.plugins_dir / metadata.name
            plugin_dir.mkdir(exist_ok=True)
            
            # Copy plugin file
            if plugin_source.is_file():
                if plugin_source.suffix == '.zip':
                    # Extract zip file
                    with zipfile.ZipFile(plugin_source, 'r') as zip_ref:
                        zip_ref.extractall(plugin_dir)
                else:
                    # Copy single file
                    shutil.copy2(plugin_source, plugin_dir / "main.py")
            
            console.print(f"✅ Plugin {metadata.name} installed successfully")
            
            # Auto-enable if configured
            if self.auto_enable:
                return self.load_plugin(plugin_dir / "main.py")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install plugin: {e}")
            console.print(f"❌ Plugin installation failed: {e}")
            return False
    
    def uninstall_plugin(self, plugin_name: str) -> bool:
        """Uninstall a plugin"""
        try:
            # Unload first if loaded
            if plugin_name in self.plugins:
                self.unload_plugin(plugin_name)
            
            # Remove plugin directory
            plugin_dir = self.plugins_dir / plugin_name
            if plugin_dir.exists():
                shutil.rmtree(plugin_dir)
            
            # Remove from config
            disabled_plugins = self.config.get("disabled_plugins", [])
            if plugin_name in disabled_plugins:
                disabled_plugins.remove(plugin_name)
            
            plugin_configs = self.config.get("plugin_configs", {})
            if plugin_name in plugin_configs:
                del plugin_configs[plugin_name]
            
            self._save_config()
            
            console.print(f"✅ Plugin {plugin_name} uninstalled successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            console.print(f"❌ Plugin uninstall failed: {e}")
            return False
    
    def load_all_plugins(self):
        """Load all available plugins"""
        plugin_paths = self.discover_plugins()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading plugins...", total=len(plugin_paths))
            
            for plugin_path in plugin_paths:
                progress.update(task, description=f"Loading {plugin_path.name}")
                self.load_plugin(plugin_path)
                progress.advance(task)
        
        console.print(f"✅ Loaded {len(self.plugins)} plugins")
    
    def get_plugin_commands(self) -> List[click.Command]:
        """Get all commands from loaded plugins"""
        commands = []
        for plugin_name, plugin_commands in self.plugin_commands.items():
            commands.extend(plugin_commands)
        return commands
    
    def create_plugin_template(self, plugin_name: str, plugin_type: PluginType, output_dir: Path = None) -> bool:
        """Create a plugin template"""
        try:
            output_dir = output_dir or Path.cwd()
            plugin_dir = output_dir / plugin_name
            plugin_dir.mkdir(exist_ok=True)
            
            # Template content based on plugin type
            if plugin_type == PluginType.COMMAND:
                template_content = self._get_command_plugin_template(plugin_name)
            elif plugin_type == PluginType.PROCESSOR:
                template_content = self._get_processor_plugin_template(plugin_name)
            else:
                template_content = self._get_basic_plugin_template(plugin_name)
            
            # Write template files
            (plugin_dir / "main.py").write_text(template_content)
            (plugin_dir / "README.md").write_text(f"# {plugin_name} Plugin\n\nDescription of your plugin here.")
            
            console.print(f"✅ Plugin template created: {plugin_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create plugin template: {e}")
            return False
    
    def _get_command_plugin_template(self, plugin_name: str) -> str:
        """Get command plugin template"""
        return f'''#!/usr/bin/env python3
"""
{plugin_name} Plugin - Command Plugin Template
"""

import click
from plc_gbt_stack.cli.plugins.plugin_manager import PluginInterface, PluginMetadata, PluginType

PLUGIN_METADATA = {{
    "name": "{plugin_name}",
    "version": "1.0.0",
    "description": "Custom command plugin",
    "author": "Your Name",
    "plugin_type": PluginType.COMMAND,
    "entry_point": "main"
}}

class Plugin(PluginInterface):
    def get_metadata(self):
        return PluginMetadata(**PLUGIN_METADATA)
    
    def initialize(self, cli_context, config):
        # Initialize your plugin here
        return True
    
    def get_commands(self):
        return [custom_command]

@click.command()
@click.option('--example', help='Example option')
def custom_command(example):
    """Custom command from {plugin_name} plugin"""
    click.echo(f"Hello from {plugin_name} plugin!")
    if example:
        click.echo(f"Example option: {{example}}")

def main():
    """Plugin entry point"""
    return Plugin()
'''
    
    def _get_processor_plugin_template(self, plugin_name: str) -> str:
        """Get processor plugin template"""
        return f'''#!/usr/bin/env python3
"""
{plugin_name} Plugin - Processor Plugin Template
"""

from plc_gbt_stack.cli.plugins.plugin_manager import PluginInterface, PluginMetadata, PluginType

PLUGIN_METADATA = {{
    "name": "{plugin_name}",
    "version": "1.0.0", 
    "description": "Custom processor plugin",
    "author": "Your Name",
    "plugin_type": PluginType.PROCESSOR,
    "entry_point": "main"
}}

class Plugin(PluginInterface):
    def get_metadata(self):
        return PluginMetadata(**PLUGIN_METADATA)
    
    def initialize(self, cli_context, config):
        # Initialize your processor here
        return True
    
    def get_commands(self):
        return []  # Processors typically don't add commands
    
    def process_data(self, data):
        """Process data - implement your custom logic here"""
        # Your processing logic here
        return data

def main():
    """Plugin entry point"""
    return Plugin()
'''
    
    def _get_basic_plugin_template(self, plugin_name: str) -> str:
        """Get basic plugin template"""
        return f'''#!/usr/bin/env python3
"""
{plugin_name} Plugin - Basic Plugin Template
"""

from plc_gbt_stack.cli.plugins.plugin_manager import PluginInterface, PluginMetadata, PluginType

PLUGIN_METADATA = {{
    "name": "{plugin_name}",
    "version": "1.0.0",
    "description": "Basic plugin template",
    "author": "Your Name", 
    "plugin_type": PluginType.EXTENSION,
    "entry_point": "main"
}}

class Plugin(PluginInterface):
    def get_metadata(self):
        return PluginMetadata(**PLUGIN_METADATA)
    
    def initialize(self, cli_context, config):
        # Initialize your plugin here
        return True
    
    def get_commands(self):
        return []

def main():
    """Plugin entry point"""
    return Plugin()
'''

# Global plugin manager instance
plugin_manager = PluginManager()

# =============================================================================
# CLI COMMANDS
# =============================================================================

@click.group()
@click.pass_context
def plugin_commands(ctx):
    """Plugin management commands"""
    pass

@plugin_commands.command('list')
@click.option('--status', type=click.Choice(['all', 'enabled', 'disabled', 'error']),
              default='all', help='Filter by plugin status')
@click.option('--format', type=click.Choice(['table', 'json']), 
              default='table', help='Output format')
def plugin_list(status, format):
    """List installed plugins"""
    plugins = plugin_manager.plugins
    
    if status != 'all':
        plugins = {name: plugin for name, plugin in plugins.items() 
                  if plugin.status.value == status}
    
    if format == 'json':
        result = {}
        for name, plugin in plugins.items():
            result[name] = {
                'name': plugin.metadata.name,
                'version': plugin.metadata.version,
                'status': plugin.status.value,
                'type': plugin.metadata.plugin_type.value,
                'description': plugin.metadata.description
            }
        console.print(json.dumps(result, indent=2))
    else:
        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="magenta")
        table.add_column("Status", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Description", style="white")
        
        for plugin in plugins.values():
            status_color = {
                PluginStatus.ENABLED: "green",
                PluginStatus.DISABLED: "yellow",
                PluginStatus.ERROR: "red"
            }.get(plugin.status, "white")
            
            table.add_row(
                plugin.metadata.name,
                plugin.metadata.version,
                f"[{status_color}]{plugin.status.value}[/{status_color}]",
                plugin.metadata.plugin_type.value,
                plugin.metadata.description[:50] + ("..." if len(plugin.metadata.description) > 50 else "")
            )
        
        console.print(table)

@plugin_commands.command('install')
@click.argument('plugin_path', type=click.Path(exists=True))
@click.option('--enable', is_flag=True, help='Enable plugin after installation')
def plugin_install(plugin_path, enable):
    """Install a plugin from file"""
    success = plugin_manager.install_plugin(plugin_path)
    
    if success and enable:
        # Get plugin name from metadata
        metadata = plugin_manager.load_plugin_metadata(Path(plugin_path))
        if metadata:
            plugin_manager.enable_plugin(metadata.name)

@plugin_commands.command('uninstall')
@click.argument('plugin_name')
@click.option('--force', is_flag=True, help='Force uninstall without confirmation')
def plugin_uninstall(plugin_name, force):
    """Uninstall a plugin"""
    if not force:
        if not Confirm.ask(f"Are you sure you want to uninstall plugin '{plugin_name}'?"):
            return
    
    plugin_manager.uninstall_plugin(plugin_name)

@plugin_commands.command('enable')
@click.argument('plugin_name')
def plugin_enable(plugin_name):
    """Enable a plugin"""
    if plugin_manager.enable_plugin(plugin_name):
        console.print(f"✅ Plugin {plugin_name} enabled")
    else:
        console.print(f"❌ Failed to enable plugin {plugin_name}")

@plugin_commands.command('disable')
@click.argument('plugin_name')
def plugin_disable(plugin_name):
    """Disable a plugin"""
    if plugin_manager.disable_plugin(plugin_name):
        console.print(f"✅ Plugin {plugin_name} disabled")
    else:
        console.print(f"❌ Failed to disable plugin {plugin_name}")

@plugin_commands.command('info')
@click.argument('plugin_name')
def plugin_info(plugin_name):
    """Show detailed plugin information"""
    if plugin_name not in plugin_manager.plugins:
        console.print(f"❌ Plugin {plugin_name} not found")
        return
    
    plugin = plugin_manager.plugins[plugin_name]
    metadata = plugin.metadata
    
    info_text = f"""
[bold cyan]{metadata.name}[/bold cyan] v{metadata.version}

[bold]Description:[/bold] {metadata.description}
[bold]Author:[/bold] {metadata.author}
[bold]Type:[/bold] {metadata.plugin_type.value}
[bold]Status:[/bold] {plugin.status.value}
[bold]Priority:[/bold] {metadata.priority.value}
[bold]License:[/bold] {metadata.license}
"""
    
    if metadata.website:
        info_text += f"[bold]Website:[/bold] {metadata.website}\n"
    
    if metadata.dependencies:
        info_text += f"[bold]Dependencies:[/bold] {', '.join(metadata.dependencies)}\n"
    
    if metadata.tags:
        info_text += f"[bold]Tags:[/bold] {', '.join(metadata.tags)}\n"
    
    if plugin.load_time:
        info_text += f"[bold]Loaded:[/bold] {plugin.load_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if plugin.error_message:
        info_text += f"[bold red]Error:[/bold red] {plugin.error_message}\n"
    
    console.print(Panel(info_text, border_style="blue"))

@plugin_commands.command('create')
@click.argument('plugin_name')
@click.option('--type', 'plugin_type', 
              type=click.Choice(['command', 'processor', 'integration', 'extension']),
              default='command', help='Plugin type')
@click.option('--output-dir', type=click.Path(), help='Output directory')
def plugin_create(plugin_name, plugin_type, output_dir):
    """Create a new plugin template"""
    output_path = Path(output_dir) if output_dir else Path.cwd()
    plugin_type_enum = PluginType(plugin_type)
    
    if plugin_manager.create_plugin_template(plugin_name, plugin_type_enum, output_path):
        console.print(f"✅ Plugin template '{plugin_name}' created successfully")
        console.print(f"📁 Location: {output_path / plugin_name}")
        console.print("\n🔧 Next steps:")
        console.print("1. Edit the main.py file to implement your plugin logic")
        console.print("2. Test your plugin")
        console.print(f"3. Install with: plc-cl plugin install {output_path / plugin_name / 'main.py'}")

@plugin_commands.command('reload')
@click.argument('plugin_name', required=False)
def plugin_reload(plugin_name):
    """Reload plugins (or specific plugin)"""
    if plugin_name:
        if plugin_name in plugin_manager.plugins:
            plugin_manager.unload_plugin(plugin_name)
            # Find plugin path and reload
            plugin_paths = plugin_manager.discover_plugins()
            for path in plugin_paths:
                metadata = plugin_manager.load_plugin_metadata(path)
                if metadata and metadata.name == plugin_name:
                    if plugin_manager.load_plugin(path):
                        console.print(f"✅ Plugin {plugin_name} reloaded")
                    else:
                        console.print(f"❌ Failed to reload plugin {plugin_name}")
                    return
            console.print(f"❌ Plugin {plugin_name} not found")
        else:
            console.print(f"❌ Plugin {plugin_name} not loaded")
    else:
        # Reload all plugins
        console.print("🔄 Reloading all plugins...")
        plugin_manager.load_all_plugins()

# Register commands with main CLI
def register_plugin_commands(main_cli):
    """Register plugin commands with main CLI"""
    main_cli.add_command(plugin_commands, name='plugin')

# For standalone testing
if __name__ == "__main__":
    plugin_commands() 