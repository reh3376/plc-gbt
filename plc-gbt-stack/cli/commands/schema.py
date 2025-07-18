#!/usr/bin/env python3
"""
🔧 Phase 21.2: Schema Management Commands

Comprehensive CLI commands for schema operations including listing, creation,
modification, and validation of control loop schemas.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (500-1500 lines, multiple command types)
Context Management: Integration with Phase 20 schema framework
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.2 Objectives:
- Implement schema listing and discovery commands
- Create schema creation commands with wizard support
- Develop schema modification and versioning commands
- Provide comprehensive schema validation commands

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.2 - Schema Management Commands
Dependencies: Phase 20 (JSON Schema Framework), Phase 21.1 (CLI Infrastructure)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import re
import difflib
import tempfile
import subprocess

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.syntax import Syntax
from rich import print as rprint

# Initialize logger early
logger = logging.getLogger(__name__)

# CLI Framework imports
try:
    from cli.framework.command_base import CLICommandBase
    from cli.framework.decorators import requires_permission
except ImportError:
    # Fallback for missing framework components
    class CLICommandBase:
        pass
    def requires_permission(permission):
        def decorator(func):
            return func
        return decorator
from rich.columns import Columns
from rich.align import Align

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Schema framework imports
try:
    # Add parent directories to path for imports
    cli_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(cli_root))
    
    from schemas.control_loops.schema_manager import ControlLoopSchemaManager, SchemaMetadata
    from schemas.control_loops.generate_base_schemas import generate_all_base_schemas
    SCHEMA_FRAMEWORK_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Warning: Could not import schema framework: {e}")
    SCHEMA_FRAMEWORK_AVAILABLE = False
    
    # Fallback definitions
    class ControlLoopSchemaManager:
        def __init__(self, *args, **kwargs):
            raise ImportError("Schema framework not available")
    
    class SchemaMetadata:
        def __init__(self, *args, **kwargs):
            raise ImportError("Schema framework not available")

# Set up console
console = Console()

# =============================================================================
# SCHEMA COMMAND ENUMERATIONS
# =============================================================================

class SchemaFormat(Enum):
    """Supported schema output formats"""
    JSON = "json"
    YAML = "yaml"
    TABLE = "table"
    TREE = "tree"
    SUMMARY = "summary"

class SchemaType(Enum):
    """Control loop schema types"""
    LADDER_LOGIC_STANDARD_PID = "ladder-logic-standard-pid"
    LADDER_LOGIC_ADVANCED_PID = "ladder-logic-advanced-pid"
    FUNCTION_BLOCK_STANDARD_PIDE = "function-block-standard-pide"
    FUNCTION_BLOCK_ADVANCED_PIDE = "function-block-advanced-pide"
    CUSTOM = "custom"
    SUBTYPE = "subtype"

class SchemaStatus(Enum):
    """Schema status levels"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

# =============================================================================
# SCHEMA UTILITY CLASSES
# =============================================================================

@dataclass
class SchemaInfo:
    """Schema information container"""
    schema_id: str
    title: str
    description: str
    version: str
    schema_type: str
    status: str
    created_at: str
    created_by: str
    file_path: str
    size_bytes: int
    validation_status: bool

class SchemaManager:
    """Enhanced schema manager for CLI operations"""
    
    def __init__(self, base_path: Optional[str] = None):
        """Initialize schema manager with CLI-specific enhancements"""
        self.base_path = Path(base_path or "plc-gbt-stack/schemas/control-loops")
        self.schema_manager = ControlLoopSchemaManager(str(self.base_path))
        self.cache = {}
        self.last_scan = None
        
    def scan_schemas(self, force_refresh: bool = False) -> List[SchemaInfo]:
        """Scan and catalog all available schemas"""
        if not force_refresh and self.cache and self.last_scan:
            time_diff = (datetime.now() - self.last_scan).seconds
            if time_diff < 30:  # Use cache for 30 seconds
                return self.cache.get('schemas', [])
        
        schemas = []
        schema_dirs = [
            self.base_path / "base",
            self.base_path / "subtypes",
            self.base_path / "custom",
            self.base_path / "extensions"
        ]
        
        for schema_dir in schema_dirs:
            if not schema_dir.exists():
                continue
                
            for schema_file in schema_dir.glob("*.json"):
                try:
                    with open(schema_file, 'r') as f:
                        schema_data = json.load(f)
                    
                    schema_info = SchemaInfo(
                        schema_id=schema_data.get('$id', schema_file.stem),
                        title=schema_data.get('title', 'Unknown'),
                        description=schema_data.get('description', 'No description'),
                        version=self._extract_version(schema_data),
                        schema_type=self._determine_schema_type(schema_file, schema_data),
                        status=self._determine_status(schema_data),
                        created_at=schema_data.get('created_at', 'Unknown'),
                        created_by=schema_data.get('created_by', 'Unknown'),
                        file_path=str(schema_file),
                        size_bytes=schema_file.stat().st_size,
                        validation_status=self._validate_schema(schema_data)
                    )
                    schemas.append(schema_info)
                    
                except Exception as e:
                    logger.warning(f"Failed to process schema {schema_file}: {e}")
        
        # Cache results
        self.cache['schemas'] = schemas
        self.last_scan = datetime.now()
        
        return schemas
    
    def _extract_version(self, schema_data: Dict[str, Any]) -> str:
        """Extract version from schema data"""
        version = schema_data.get('version')
        if version:
            return version
        
        # Check in properties
        props = schema_data.get('properties', {})
        version_prop = props.get('version', {})
        if 'enum' in version_prop and version_prop['enum']:
            return version_prop['enum'][0]
        
        return "Unknown"
    
    def _determine_schema_type(self, file_path: Path, schema_data: Dict[str, Any]) -> str:
        """Determine schema type from file path and content"""
        if 'base' in file_path.parts:
            return "base"
        elif 'subtypes' in file_path.parts:
            return "subtype"
        elif 'custom' in file_path.parts:
            return "custom"
        elif 'extensions' in file_path.parts:
            return "extension"
        else:
            return "unknown"
    
    def _determine_status(self, schema_data: Dict[str, Any]) -> str:
        """Determine schema status"""
        status = schema_data.get('status', 'active')
        if status in [s.value for s in SchemaStatus]:
            return status
        return SchemaStatus.ACTIVE.value
    
    def _validate_schema(self, schema_data: Dict[str, Any]) -> bool:
        """Validate schema against JSON Schema standards"""
        try:
            # Basic JSON Schema validation
            from jsonschema import Draft202012Validator
            Draft202012Validator.check_schema(schema_data)
            return True
        except Exception:
            return False
    
    def search_schemas(self, query: str, search_fields: List[str] = None) -> List[SchemaInfo]:
        """Search schemas by query string"""
        if search_fields is None:
            search_fields = ['title', 'description', 'schema_id', 'schema_type']
        
        schemas = self.scan_schemas()
        query_lower = query.lower()
        
        matching_schemas = []
        for schema in schemas:
            for field in search_fields:
                field_value = getattr(schema, field, '').lower()
                if query_lower in field_value:
                    matching_schemas.append(schema)
                    break
        
        return matching_schemas
    
    def get_schema_by_id(self, schema_id: str) -> Optional[SchemaInfo]:
        """Get schema information by ID"""
        schemas = self.scan_schemas()
        for schema in schemas:
            if schema.schema_id == schema_id or schema_id in schema.file_path:
                return schema
        return None
    
    def load_schema_content(self, schema_info: SchemaInfo) -> Dict[str, Any]:
        """Load full schema content from file"""
        try:
            with open(schema_info.file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema content: {e}")
            return {}

# =============================================================================
# SCHEMA LISTING AND DISCOVERY COMMANDS
# =============================================================================

@click.group(name='schema')
@click.pass_context
def schema_commands(ctx):
    """Schema management commands for control loop configurations"""
    # Initialize schema manager in CLI context
    cli_ctx: CLIContext = ctx.obj
    if not hasattr(cli_ctx, 'schema_manager'):
        cli_ctx.schema_manager = SchemaManager()

@schema_commands.command('list')
@click.option('--type', '-t', 'schema_type', 
              type=click.Choice([t.value for t in SchemaType]),
              help='Filter by schema type')
@click.option('--status', '-s',
              type=click.Choice([s.value for s in SchemaStatus]),
              help='Filter by schema status')
@click.option('--format', '-f', 'output_format',
              type=click.Choice([f.value for f in SchemaFormat]),
              default=SchemaFormat.TABLE.value,
              help='Output format')
@click.option('--verbose', '-v', is_flag=True,
              help='Show detailed information')
@click.option('--refresh', is_flag=True,
              help='Force refresh schema cache')
@click.pass_context
@requires_permission('schema:read')
def list_schemas(ctx, schema_type, status, output_format, verbose, refresh):
    """List all available control loop schemas
    
    Examples:
        plc-cl schema list                      # List all schemas
        plc-cl schema list --type=base          # List only base schemas
        plc-cl schema list --format=json       # Output as JSON
        plc-cl schema list --verbose            # Show detailed info
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Scan schemas
        with console.status("[bold green]Scanning schemas...", spinner="dots"):
            schemas = schema_manager.scan_schemas(force_refresh=refresh)
        
        # Apply filters
        if schema_type:
            schemas = [s for s in schemas if s.schema_type == schema_type]
        
        if status:
            schemas = [s for s in schemas if s.status == status]
        
        if not schemas:
            console.print("[yellow]No schemas found matching the criteria[/yellow]")
            return
        
        # Output in requested format
        if output_format == SchemaFormat.JSON.value:
            output = {
                "schemas": [asdict(s) for s in schemas],
                "total_count": len(schemas),
                "scan_time": datetime.now().isoformat()
            }
            console.print_json(data=output)
            
        elif output_format == SchemaFormat.YAML.value:
            output = {
                "schemas": [asdict(s) for s in schemas],
                "total_count": len(schemas),
                "scan_time": datetime.now().isoformat()
            }
            console.print(yaml.dump(output, default_flow_style=False))
            
        elif output_format == SchemaFormat.TABLE.value:
            _display_schemas_table(schemas, verbose)
            
        elif output_format == SchemaFormat.SUMMARY.value:
            _display_schemas_summary(schemas)
        
        # Show summary footer
        if output_format in [SchemaFormat.TABLE.value, SchemaFormat.SUMMARY.value]:
            console.print(f"\n[dim]Found {len(schemas)} schema(s)[/dim]")
            
    except Exception as e:
        console.print(f"[red]❌ Error listing schemas: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('search')
@click.argument('query', required=True)
@click.option('--field', '-f', 'search_fields', multiple=True,
              type=click.Choice(['title', 'description', 'schema_id', 'schema_type']),
              help='Fields to search in (can be specified multiple times)')
@click.option('--format', 'output_format',
              type=click.Choice([f.value for f in SchemaFormat]),
              default=SchemaFormat.TABLE.value,
              help='Output format')
@click.option('--case-sensitive', is_flag=True,
              help='Case-sensitive search')
@click.pass_context
@requires_permission('schema:read')
def search_schemas(ctx, query, search_fields, output_format, case_sensitive):
    """Search schemas by query string
    
    Examples:
        plc-cl schema search "advanced pid"           # Search all fields
        plc-cl schema search "temperature" -f title   # Search only titles
        plc-cl schema search "cascade" --case-sensitive
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Convert search fields to list
        fields = list(search_fields) if search_fields else None
        
        # Adjust query case sensitivity
        search_query = query if case_sensitive else query
        
        with console.status("[bold green]Searching schemas...", spinner="dots"):
            matching_schemas = schema_manager.search_schemas(search_query, fields)
        
        if not matching_schemas:
            console.print(f"[yellow]No schemas found matching '{query}'[/yellow]")
            return
        
        # Display results
        if output_format == SchemaFormat.JSON.value:
            output = {
                "query": query,
                "search_fields": fields or ["all"],
                "matches": [asdict(s) for s in matching_schemas],
                "match_count": len(matching_schemas)
            }
            console.print_json(data=output)
        elif output_format == SchemaFormat.TABLE.value:
            console.print(f"[bold]Search results for: '{query}'[/bold]\n")
            _display_schemas_table(matching_schemas, verbose=True)
        
        console.print(f"\n[dim]Found {len(matching_schemas)} matching schema(s)[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error searching schemas: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('info')
@click.argument('schema_id', required=True)
@click.option('--format', 'output_format',
              type=click.Choice([f.value for f in SchemaFormat]),
              default=SchemaFormat.SUMMARY.value,
              help='Output format')
@click.option('--show-schema', is_flag=True,
              help='Show full schema content')
@click.pass_context
@requires_permission('schema:read')
def schema_info(ctx, schema_id, output_format, show_schema):
    """Show detailed information about a specific schema
    
    Examples:
        plc-cl schema info "ladder-logic-standard-pid"
        plc-cl schema info "my-custom-schema" --show-schema
        plc-cl schema info "advanced-pid" --format=json
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schema
        schema_info = schema_manager.get_schema_by_id(schema_id)
        if not schema_info:
            console.print(f"[red]❌ Schema '{schema_id}' not found[/red]")
            sys.exit(1)
        
        # Load full schema content if requested
        schema_content = None
        if show_schema or output_format == SchemaFormat.JSON.value:
            schema_content = schema_manager.load_schema_content(schema_info)
        
        # Display information
        if output_format == SchemaFormat.JSON.value:
            output = {
                "schema_info": asdict(schema_info),
                "schema_content": schema_content
            }
            console.print_json(data=output)
            
        elif output_format == SchemaFormat.SUMMARY.value:
            _display_schema_details(schema_info, schema_content if show_schema else None)
        
    except Exception as e:
        console.print(f"[red]❌ Error retrieving schema info: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('tree')
@click.option('--type', 'schema_type',
              type=click.Choice([t.value for t in SchemaType]),
              help='Filter by schema type')
@click.option('--show-inheritance', is_flag=True,
              help='Show schema inheritance relationships')
@click.pass_context
@requires_permission('schema:read')
def schema_tree(ctx, schema_type, show_inheritance):
    """Display schemas in a tree structure showing relationships
    
    Examples:
        plc-cl schema tree                      # Show all schemas
        plc-cl schema tree --type=base          # Show only base schemas
        plc-cl schema tree --show-inheritance   # Show inheritance
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        schemas = schema_manager.scan_schemas()
        
        # Apply filters
        if schema_type:
            schemas = [s for s in schemas if s.schema_type == schema_type]
        
        # Create tree structure
        tree = Tree("📁 Control Loop Schemas", style="bold blue")
        
        # Group by type
        schema_groups = {}
        for schema in schemas:
            group = schema.schema_type
            if group not in schema_groups:
                schema_groups[group] = []
            schema_groups[group].append(schema)
        
        # Build tree
        for group_name, group_schemas in sorted(schema_groups.items()):
            group_node = tree.add(f"📂 {group_name.title()} ({len(group_schemas)})",
                                style="bold green")
            
            for schema in sorted(group_schemas, key=lambda x: x.title):
                status_icon = _get_status_icon(schema.status)
                validation_icon = "✅" if schema.validation_status else "❌"
                
                schema_node = group_node.add(
                    f"{status_icon} {validation_icon} {schema.title}",
                    style="cyan"
                )
                
                # Add details
                schema_node.add(f"Version: {schema.version}", style="dim")
                schema_node.add(f"ID: {schema.schema_id}", style="dim")
                if show_inheritance:
                    # Add inheritance info (would need to parse schema content)
                    schema_node.add("Inheritance: TBD", style="dim yellow")
        
        console.print(tree)
        console.print(f"\n[dim]Total schemas: {len(schemas)}[/dim]")
        
    except Exception as e:
        console.print(f"[red]❌ Error displaying schema tree: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# DISPLAY HELPER FUNCTIONS
# =============================================================================

def _display_schemas_table(schemas: List[SchemaInfo], verbose: bool = False):
    """Display schemas in a table format"""
    table = Table(title="Control Loop Schemas")
    
    # Define columns based on verbosity
    if verbose:
        table.add_column("Status", style="cyan", min_width=8)
        table.add_column("Type", style="green", min_width=10)
        table.add_column("Title", style="bold", min_width=20)
        table.add_column("Version", style="yellow", min_width=10)
        table.add_column("Valid", style="red", min_width=6)
        table.add_column("Size", style="dim", min_width=8)
        table.add_column("Created", style="dim", min_width=12)
    else:
        table.add_column("Status", style="cyan", min_width=8)
        table.add_column("Title", style="bold", min_width=25)
        table.add_column("Type", style="green", min_width=12)
        table.add_column("Version", style="yellow", min_width=10)
        table.add_column("Valid", style="red", min_width=6)
    
    # Add rows
    for schema in sorted(schemas, key=lambda x: (x.schema_type, x.title)):
        status_icon = _get_status_icon(schema.status)
        validation_icon = "✅" if schema.validation_status else "❌"
        
        if verbose:
            table.add_row(
                f"{status_icon} {schema.status}",
                schema.schema_type,
                schema.title,
                schema.version,
                validation_icon,
                _format_file_size(schema.size_bytes),
                _format_date(schema.created_at)
            )
        else:
            table.add_row(
                f"{status_icon} {schema.status}",
                schema.title,
                schema.schema_type,
                schema.version,
                validation_icon
            )
    
    console.print(table)

def _display_schemas_summary(schemas: List[SchemaInfo]):
    """Display schemas summary with statistics"""
    # Statistics
    total_schemas = len(schemas)
    valid_schemas = sum(1 for s in schemas if s.validation_status)
    
    # Group by type
    type_counts = {}
    status_counts = {}
    
    for schema in schemas:
        type_counts[schema.schema_type] = type_counts.get(schema.schema_type, 0) + 1
        status_counts[schema.status] = status_counts.get(schema.status, 0) + 1
    
    # Display summary
    summary_table = Table(title="Schema Summary")
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Count", style="cyan")
    summary_table.add_column("Percentage", style="green")
    
    summary_table.add_row("Total Schemas", str(total_schemas), "100%")
    summary_table.add_row("Valid Schemas", str(valid_schemas), 
                         f"{(valid_schemas/total_schemas*100):.1f}%" if total_schemas > 0 else "0%")
    
    console.print(summary_table)
    
    # Type breakdown
    if type_counts:
        type_table = Table(title="Schema Types")
        type_table.add_column("Type", style="bold")
        type_table.add_column("Count", style="cyan")
        
        for schema_type, count in sorted(type_counts.items()):
            type_table.add_row(schema_type.title(), str(count))
        
        console.print(type_table)

def _display_schema_details(schema_info: SchemaInfo, schema_content: Optional[Dict[str, Any]] = None):
    """Display detailed schema information"""
    # Main info panel
    info_lines = [
        f"[bold]ID:[/bold] {schema_info.schema_id}",
        f"[bold]Title:[/bold] {schema_info.title}",
        f"[bold]Description:[/bold] {schema_info.description}",
        f"[bold]Version:[/bold] {schema_info.version}",
        f"[bold]Type:[/bold] {schema_info.schema_type}",
        f"[bold]Status:[/bold] {_get_status_icon(schema_info.status)} {schema_info.status}",
        f"[bold]Valid:[/bold] {'✅ Yes' if schema_info.validation_status else '❌ No'}",
        f"[bold]File:[/bold] {schema_info.file_path}",
        f"[bold]Size:[/bold] {_format_file_size(schema_info.size_bytes)}",
        f"[bold]Created:[/bold] {_format_date(schema_info.created_at)}",
        f"[bold]Created by:[/bold] {schema_info.created_by}"
    ]
    
    panel = Panel(
        "\n".join(info_lines),
        title=f"Schema Information: {schema_info.title}",
        border_style="blue"
    )
    console.print(panel)
    
    # Schema content
    if schema_content:
        console.print("\n[bold]Schema Content:[/bold]")
        syntax = Syntax(
            json.dumps(schema_content, indent=2),
            "json",
            theme="monokai",
            line_numbers=True
        )
        console.print(syntax)

def _get_status_icon(status: str) -> str:
    """Get icon for schema status"""
    icons = {
        'active': '🟢',
        'draft': '🟡',
        'deprecated': '🟠',
        'archived': '🔴'
    }
    return icons.get(status, '⚪')

def _format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def _format_date(date_str: str) -> str:
    """Format date string for display"""
    try:
        if date_str == "Unknown":
            return date_str
        # Try to parse and reformat
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str

# =============================================================================
# CLI INTEGRATION
# =============================================================================

# Register schema commands with main CLI
def register_schema_commands(cli_group):
    """Register schema commands with the main CLI group"""
    cli_group.add_command(schema_commands)

# Export for use in main CLI
__all__ = ['schema_commands', 'register_schema_commands', 'SchemaManager'] 

# =============================================================================
# SCHEMA CREATION COMMANDS
# =============================================================================

@schema_commands.command('create')
@click.option('--type', '-t', 'base_type', 
              type=click.Choice([t.value for t in SchemaType if t != SchemaType.CUSTOM]),
              required=True,
              help='Base schema type to create')
@click.option('--name', '-n', required=True,
              help='Name for the new schema')
@click.option('--description', '-d',
              help='Description of the schema')
@click.option('--version', '-v', default="01.00.001",
              help='Initial version (format: XX.YY.ZZZ)')
@click.option('--output', '-o',
              help='Output file path (default: auto-generated)')
@click.option('--dry-run', is_flag=True,
              help='Show what would be created without saving')
@click.pass_context
@requires_permission('schema:create')
def create_schema(ctx, base_type, name, description, version, output, dry_run):
    """Create a new control loop schema from a base type
    
    Examples:
        plc-cl schema create --type=ladder-logic-standard-pid --name="My PID Controller"
        plc-cl schema create -t function-block-standard-pide -n "Temperature Control" -d "HVAC temperature control loop"
        plc-cl schema create --type=custom --name="Custom Controller" --dry-run
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Validate version format
        if not re.match(r'^\d{2}\.\d{2}\.\d{3}$', version):
            console.print("[red]❌ Invalid version format. Use XX.YY.ZZZ (e.g., 01.00.001)[/red]")
            sys.exit(1)
        
        # Create schema metadata
        metadata = SchemaMetadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            created_by=cli_ctx.auth_manager.user_info.get('username', 'CLI User'),
            version=version,
            schema_type=base_type,
            description=description or f"Custom {base_type} schema"
        )
        
        with console.status("[bold green]Creating schema...", spinner="dots"):
            try:
                # Create the schema using the schema manager
                new_schema = schema_manager.schema_manager.create_base_schema(base_type, metadata)
                
                # Customize schema title and description
                new_schema['title'] = name
                if description:
                    new_schema['description'] = description
                
                # Generate output path if not provided
                if not output:
                    safe_name = re.sub(r'[^a-zA-Z0-9-_]', '-', name.lower())
                    output = str(schema_manager.base_path / "custom" / f"{safe_name}.json")
                
                # Show schema preview
                if dry_run:
                    console.print(f"[bold]Schema that would be created:[/bold]")
                    console.print(f"[dim]Output path: {output}[/dim]\n")
                    
                    syntax = Syntax(
                        json.dumps(new_schema, indent=2),
                        "json",
                        theme="monokai",
                        line_numbers=True
                    )
                    console.print(syntax)
                    console.print(f"\n[yellow]💡 Use --no-dry-run to actually create the schema[/yellow]")
                    return
                
                # Save schema
                os.makedirs(os.path.dirname(output), exist_ok=True)
                with open(output, 'w') as f:
                    json.dump(new_schema, f, indent=2)
                
                # Success message
                console.print(f"[green]✅ Schema created successfully![/green]")
                console.print(f"[dim]Name: {name}[/dim]")
                console.print(f"[dim]Type: {base_type}[/dim]")
                console.print(f"[dim]Version: {version}[/dim]")
                console.print(f"[dim]File: {output}[/dim]")
                
                # Refresh cache
                schema_manager.scan_schemas(force_refresh=True)
                
            except Exception as e:
                console.print(f"[red]❌ Failed to create schema: {str(e)}[/red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]❌ Error creating schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('create-subtype')
@click.option('--base', '-b', 'base_schema_id', required=True,
              help='Base schema ID to inherit from')
@click.option('--subtype', '-s', required=True,
              type=click.Choice(['feedforward', 'cascade', 'combined', 'multi-formula']),
              help='Subtype to create')
@click.option('--name', '-n', required=True,
              help='Name for the subtype schema')
@click.option('--description', '-d',
              help='Description of the subtype schema')
@click.option('--version', '-v', default="01.00.001",
              help='Initial version (format: XX.YY.ZZZ)')
@click.option('--output', '-o',
              help='Output file path (default: auto-generated)')
@click.pass_context
@requires_permission('schema:create')
def create_subtype_schema(ctx, base_schema_id, subtype, name, description, version, output):
    """Create a subtype schema that inherits from a base schema
    
    Examples:
        plc-cl schema create-subtype --base="ladder-logic-standard-pid" --subtype=feedforward --name="PID with Feedforward"
        plc-cl schema create-subtype -b "function-block-advanced-pide" -s cascade -n "Cascade PIDE"
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Validate base schema exists
        base_schema_info = schema_manager.get_schema_by_id(base_schema_id)
        if not base_schema_info:
            console.print(f"[red]❌ Base schema '{base_schema_id}' not found[/red]")
            sys.exit(1)
        
        # Validate version format
        if not re.match(r'^\d{2}\.\d{2}\.\d{3}$', version):
            console.print("[red]❌ Invalid version format. Use XX.YY.ZZZ (e.g., 01.00.001)[/red]")
            sys.exit(1)
        
        # Create subtype-specific properties
        additional_properties = _get_subtype_properties(subtype)
        
        # Create schema metadata
        metadata = SchemaMetadata(
            created_at=datetime.now(timezone.utc).isoformat(),
            created_by=cli_ctx.auth_manager.user_info.get('username', 'CLI User'),
            version=version,
            schema_type=f"{base_schema_info.schema_type}-{subtype}",
            parent_schema=base_schema_id,
            description=description or f"{subtype.title()} variant of {base_schema_info.title}"
        )
        
        with console.status("[bold green]Creating subtype schema...", spinner="dots"):
            try:
                # Create the subtype schema
                new_schema = schema_manager.schema_manager.create_subtype_schema(
                    base_schema_info.schema_type,
                    subtype,
                    metadata,
                    additional_properties
                )
                
                # Customize schema title
                new_schema['title'] = name
                
                # Generate output path if not provided
                if not output:
                    safe_name = re.sub(r'[^a-zA-Z0-9-_]', '-', name.lower())
                    output = str(schema_manager.base_path / "subtypes" / subtype / f"{safe_name}.json")
                
                # Save schema
                os.makedirs(os.path.dirname(output), exist_ok=True)
                with open(output, 'w') as f:
                    json.dump(new_schema, f, indent=2)
                
                # Success message
                console.print(f"[green]✅ Subtype schema created successfully![/green]")
                console.print(f"[dim]Name: {name}[/dim]")
                console.print(f"[dim]Base: {base_schema_id}[/dim]")
                console.print(f"[dim]Subtype: {subtype}[/dim]")
                console.print(f"[dim]File: {output}[/dim]")
                
                # Refresh cache
                schema_manager.scan_schemas(force_refresh=True)
                
            except Exception as e:
                console.print(f"[red]❌ Failed to create subtype schema: {str(e)}[/red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]❌ Error creating subtype schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('wizard')
@click.option('--interactive', '-i', is_flag=True, default=True,
              help='Run in interactive mode (default)')
@click.pass_context
@requires_permission('schema:create')
def schema_wizard(ctx, interactive):
    """Interactive schema creation wizard
    
    Guides you through the process of creating a custom schema with
    step-by-step prompts and validation.
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        console.print(Panel(
            "[bold blue]🧙 Schema Creation Wizard[/bold blue]\n\n"
            "This wizard will guide you through creating a custom control loop schema.\n"
            "You can exit at any time by pressing Ctrl+C.",
            title="Welcome",
            border_style="blue"
        ))
        
        # Step 1: Choose base type
        console.print("\n[bold]Step 1: Choose Base Schema Type[/bold]")
        base_types = [t.value for t in SchemaType if t != SchemaType.CUSTOM and t != SchemaType.SUBTYPE]
        
        for i, base_type in enumerate(base_types, 1):
            console.print(f"  {i}. {base_type}")
        
        while True:
            try:
                choice = IntPrompt.ask("Select base type", choices=[str(i) for i in range(1, len(base_types) + 1)])
                base_type = base_types[choice - 1]
                break
            except:
                console.print("[red]Invalid choice. Please try again.[/red]")
        
        # Step 2: Basic information
        console.print(f"\n[bold]Step 2: Basic Information[/bold]")
        name = Prompt.ask("Schema name")
        description = Prompt.ask("Schema description", default="Custom control loop schema")
        version = Prompt.ask("Initial version", default="01.00.001")
        
        # Validate version
        if not re.match(r'^\d{2}\.\d{2}\.\d{3}$', version):
            console.print("[yellow]⚠️  Invalid version format. Using default 01.00.001[/yellow]")
            version = "01.00.001"
        
        # Step 3: Advanced options
        console.print(f"\n[bold]Step 3: Advanced Options[/bold]")
        create_subtype = Confirm.ask("Create as subtype (inherits from existing schema)?", default=False)
        
        subtype = None
        base_schema_id = None
        
        if create_subtype:
            # List available base schemas
            schemas = schema_manager.scan_schemas()
            base_schemas = [s for s in schemas if s.schema_type == "base"]
            
            if not base_schemas:
                console.print("[red]❌ No base schemas available for inheritance[/red]")
                sys.exit(1)
            
            console.print("\nAvailable base schemas:")
            for i, schema in enumerate(base_schemas, 1):
                console.print(f"  {i}. {schema.title} ({schema.schema_id})")
            
            while True:
                try:
                    choice = IntPrompt.ask("Select base schema", 
                                         choices=[str(i) for i in range(1, len(base_schemas) + 1)])
                    base_schema_id = base_schemas[choice - 1].schema_id
                    break
                except:
                    console.print("[red]Invalid choice. Please try again.[/red]")
            
            # Choose subtype
            subtype_options = ['feedforward', 'cascade', 'combined', 'multi-formula']
            console.print("\nSubtype options:")
            for i, subtype_option in enumerate(subtype_options, 1):
                console.print(f"  {i}. {subtype_option}")
            
            while True:
                try:
                    choice = IntPrompt.ask("Select subtype", 
                                         choices=[str(i) for i in range(1, len(subtype_options) + 1)])
                    subtype = subtype_options[choice - 1]
                    break
                except:
                    console.print("[red]Invalid choice. Please try again.[/red]")
        
        # Step 4: Summary and confirmation
        console.print(f"\n[bold]Step 4: Summary[/bold]")
        
        summary_table = Table(title="Schema Creation Summary")
        summary_table.add_column("Property", style="bold")
        summary_table.add_column("Value", style="cyan")
        
        summary_table.add_row("Name", name)
        summary_table.add_row("Description", description)
        summary_table.add_row("Version", version)
        summary_table.add_row("Base Type", base_type)
        
        if create_subtype:
            summary_table.add_row("Parent Schema", base_schema_id)
            summary_table.add_row("Subtype", subtype)
        
        console.print(summary_table)
        
        if not Confirm.ask("\nProceed with schema creation?", default=True):
            console.print("[yellow]❌ Schema creation cancelled[/yellow]")
            return
        
        # Step 5: Create the schema
        console.print(f"\n[bold]Step 5: Creating Schema[/bold]")
        
        try:
            if create_subtype:
                # Create subtype schema
                additional_properties = _get_subtype_properties(subtype)
                metadata = SchemaMetadata(
                    created_at=datetime.now(timezone.utc).isoformat(),
                    created_by=cli_ctx.auth_manager.user_info.get('username', 'CLI User'),
                    version=version,
                    schema_type=f"{base_type}-{subtype}",
                    parent_schema=base_schema_id,
                    description=description
                )
                
                new_schema = schema_manager.schema_manager.create_subtype_schema(
                    base_type, subtype, metadata, additional_properties
                )
                output_dir = schema_manager.base_path / "subtypes" / subtype
            else:
                # Create base schema
                metadata = SchemaMetadata(
                    created_at=datetime.now(timezone.utc).isoformat(),
                    created_by=cli_ctx.auth_manager.user_info.get('username', 'CLI User'),
                    version=version,
                    schema_type=base_type,
                    description=description
                )
                
                new_schema = schema_manager.schema_manager.create_base_schema(base_type, metadata)
                output_dir = schema_manager.base_path / "custom"
            
            # Customize schema
            new_schema['title'] = name
            new_schema['description'] = description
            
            # Save schema
            safe_name = re.sub(r'[^a-zA-Z0-9-_]', '-', name.lower())
            output_path = output_dir / f"{safe_name}.json"
            
            os.makedirs(output_dir, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(new_schema, f, indent=2)
            
            # Success
            console.print(Panel(
                f"[green]✅ Schema created successfully![/green]\n\n"
                f"[bold]Name:[/bold] {name}\n"
                f"[bold]File:[/bold] {output_path}\n"
                f"[bold]Type:[/bold] {base_type}\n"
                f"[bold]Version:[/bold] {version}",
                title="Success",
                border_style="green"
            ))
            
            # Refresh cache
            schema_manager.scan_schemas(force_refresh=True)
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create schema: {str(e)}[/red]")
            sys.exit(1)
            
    except KeyboardInterrupt:
        console.print("\n[yellow]❌ Schema creation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]❌ Error in schema wizard: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# SCHEMA MODIFICATION COMMANDS
# =============================================================================

@schema_commands.command('modify')
@click.argument('schema_id', required=True)
@click.option('--add-property', multiple=True,
              help='Add property (format: name:type:description)')
@click.option('--remove-property', multiple=True,
              help='Remove property by name')
@click.option('--set-description',
              help='Set new description')
@click.option('--set-title',
              help='Set new title')
@click.option('--version-increment', 
              type=click.Choice(['patch', 'minor', 'major']),
              default='patch',
              help='Version increment type')
@click.option('--backup', is_flag=True, default=True,
              help='Create backup before modification')
@click.option('--dry-run', is_flag=True,
              help='Show changes without applying them')
@click.pass_context
@requires_permission('schema:modify')
def modify_schema(ctx, schema_id, add_property, remove_property, set_description, 
                 set_title, version_increment, backup, dry_run):
    """Modify an existing schema
    
    Examples:
        plc-cl schema modify "my-schema" --add-property "new_param:number:A new parameter"
        plc-cl schema modify "my-schema" --set-title "Updated Title" --version-increment minor
        plc-cl schema modify "my-schema" --remove-property "old_param" --dry-run
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schema
        schema_info = schema_manager.get_schema_by_id(schema_id)
        if not schema_info:
            console.print(f"[red]❌ Schema '{schema_id}' not found[/red]")
            sys.exit(1)
        
        # Load current schema
        current_schema = schema_manager.load_schema_content(schema_info)
        if not current_schema:
            console.print(f"[red]❌ Failed to load schema content[/red]")
            sys.exit(1)
        
        # Create backup if requested
        if backup and not dry_run:
            backup_dir = schema_manager.base_path / "modifications" / "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{schema_info.schema_id}_{timestamp}.json"
            
            with open(backup_file, 'w') as f:
                json.dump(current_schema, f, indent=2)
            
            console.print(f"[dim]Backup created: {backup_file}[/dim]")
        
        # Apply modifications
        modified_schema = current_schema.copy()
        changes = []
        
        # Add properties
        for prop_def in add_property:
            try:
                parts = prop_def.split(':', 2)
                if len(parts) != 3:
                    console.print(f"[red]❌ Invalid property format: {prop_def}[/red]")
                    continue
                
                prop_name, prop_type, prop_desc = parts
                
                if 'properties' not in modified_schema:
                    modified_schema['properties'] = {}
                
                modified_schema['properties'][prop_name] = {
                    'type': prop_type,
                    'description': prop_desc
                }
                changes.append(f"Added property: {prop_name} ({prop_type})")
                
            except Exception as e:
                console.print(f"[red]❌ Failed to add property {prop_def}: {e}[/red]")
        
        # Remove properties
        for prop_name in remove_property:
            if 'properties' in modified_schema and prop_name in modified_schema['properties']:
                del modified_schema['properties'][prop_name]
                changes.append(f"Removed property: {prop_name}")
            else:
                console.print(f"[yellow]⚠️  Property '{prop_name}' not found[/yellow]")
        
        # Set new description
        if set_description:
            modified_schema['description'] = set_description
            changes.append(f"Updated description")
        
        # Set new title
        if set_title:
            modified_schema['title'] = set_title
            changes.append(f"Updated title to: {set_title}")
        
        # Update version
        old_version = schema_info.version
        new_version = _increment_version(old_version, version_increment)
        
        # Update version in schema
        if 'properties' in modified_schema and 'version' in modified_schema['properties']:
            if 'enum' in modified_schema['properties']['version']:
                modified_schema['properties']['version']['enum'] = [new_version]
        
        modified_schema['version'] = new_version
        changes.append(f"Version: {old_version} → {new_version}")
        
        # Show changes
        if changes:
            console.print(f"\n[bold]Changes to be applied:[/bold]")
            for change in changes:
                console.print(f"  • {change}")
        else:
            console.print("[yellow]No changes to apply[/yellow]")
            return
        
        if dry_run:
            console.print(f"\n[bold]Modified schema preview:[/bold]")
            syntax = Syntax(
                json.dumps(modified_schema, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)
            console.print(f"\n[yellow]💡 Remove --dry-run to apply changes[/yellow]")
            return
        
        # Save modified schema
        with open(schema_info.file_path, 'w') as f:
            json.dump(modified_schema, f, indent=2)
        
        console.print(f"[green]✅ Schema modified successfully![/green]")
        console.print(f"[dim]File: {schema_info.file_path}[/dim]")
        console.print(f"[dim]New version: {new_version}[/dim]")
        
        # Refresh cache
        schema_manager.scan_schemas(force_refresh=True)
        
    except Exception as e:
        console.print(f"[red]❌ Error modifying schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('version')
@click.argument('schema_id', required=True)
@click.option('--description', '-d', required=True,
              help='Description of changes in this version')
@click.option('--increment', '-i',
              type=click.Choice(['patch', 'minor', 'major']),
              default='patch',
              help='Version increment type')
@click.pass_context
@requires_permission('schema:modify')
def version_schema(ctx, schema_id, description, increment):
    """Create a new version of an existing schema
    
    Examples:
        plc-cl schema version "my-schema" --description "Fixed validation rules"
        plc-cl schema version "my-schema" -d "Added new features" --increment minor
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schema
        schema_info = schema_manager.get_schema_by_id(schema_id)
        if not schema_info:
            console.print(f"[red]❌ Schema '{schema_id}' not found[/red]")
            sys.exit(1)
        
        # Load current schema
        current_schema = schema_manager.load_schema_content(schema_info)
        if not current_schema:
            console.print(f"[red]❌ Failed to load schema content[/red]")
            sys.exit(1)
        
        with console.status("[bold green]Creating new version...", spinner="dots"):
            try:
                # Create version using schema manager
                changes = {"description": description}
                new_schema = schema_manager.schema_manager.version_schema(
                    schema_info.schema_id, changes, description
                )
                
                console.print(f"[green]✅ New schema version created![/green]")
                console.print(f"[dim]Previous version: {schema_info.version}[/dim]")
                console.print(f"[dim]New version: {new_schema['properties']['version']['enum'][0]}[/dim]")
                console.print(f"[dim]Change description: {description}[/dim]")
                
                # Refresh cache
                schema_manager.scan_schemas(force_refresh=True)
                
            except Exception as e:
                console.print(f"[red]❌ Failed to create new version: {str(e)}[/red]")
                sys.exit(1)
                
    except Exception as e:
        console.print(f"[red]❌ Error versioning schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('diff')
@click.argument('schema_id_1', required=True)
@click.argument('schema_id_2', required=True)
@click.option('--format', 'output_format',
              type=click.Choice(['unified', 'side-by-side', 'json']),
              default='unified',
              help='Diff output format')
@click.option('--context', '-c', default=3,
              help='Lines of context to show')
@click.pass_context
@requires_permission('schema:read')
def diff_schemas(ctx, schema_id_1, schema_id_2, output_format, context):
    """Compare two schemas and show differences
    
    Examples:
        plc-cl schema diff "schema-v1" "schema-v2"
        plc-cl schema diff "base-schema" "custom-schema" --format=side-by-side
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schemas
        schema1 = schema_manager.get_schema_by_id(schema_id_1)
        schema2 = schema_manager.get_schema_by_id(schema_id_2)
        
        if not schema1:
            console.print(f"[red]❌ Schema '{schema_id_1}' not found[/red]")
            sys.exit(1)
        
        if not schema2:
            console.print(f"[red]❌ Schema '{schema_id_2}' not found[/red]")
            sys.exit(1)
        
        # Load schema contents
        content1 = schema_manager.load_schema_content(schema1)
        content2 = schema_manager.load_schema_content(schema2)
        
        # Convert to formatted JSON strings
        json1 = json.dumps(content1, indent=2, sort_keys=True)
        json2 = json.dumps(content2, indent=2, sort_keys=True)
        
        # Generate diff
        if output_format == 'json':
            # Create JSON diff object
            diff_result = {
                "schema_1": {
                    "id": schema1.schema_id,
                    "title": schema1.title,
                    "version": schema1.version
                },
                "schema_2": {
                    "id": schema2.schema_id,
                    "title": schema2.title,
                    "version": schema2.version
                },
                "differences": list(difflib.unified_diff(
                    json1.splitlines(),
                    json2.splitlines(),
                    fromfile=schema1.title,
                    tofile=schema2.title,
                    n=context,
                    lineterm=''
                ))
            }
            console.print_json(data=diff_result)
            
        elif output_format == 'unified':
            console.print(f"[bold]Comparing schemas:[/bold]")
            console.print(f"[cyan]Schema 1:[/cyan] {schema1.title} (v{schema1.version})")
            console.print(f"[cyan]Schema 2:[/cyan] {schema2.title} (v{schema2.version})")
            console.print()
            
            diff_lines = list(difflib.unified_diff(
                json1.splitlines(),
                json2.splitlines(),
                fromfile=f"{schema1.title} (v{schema1.version})",
                tofile=f"{schema2.title} (v{schema2.version})",
                n=context,
                lineterm=''
            ))
            
            if not diff_lines:
                console.print("[green]✅ Schemas are identical[/green]")
            else:
                for line in diff_lines:
                    if line.startswith('+++'):
                        console.print(f"[green]{line}[/green]")
                    elif line.startswith('---'):
                        console.print(f"[red]{line}[/red]")
                    elif line.startswith('+'):
                        console.print(f"[green]{line}[/green]")
                    elif line.startswith('-'):
                        console.print(f"[red]{line}[/red]")
                    elif line.startswith('@@'):
                        console.print(f"[blue]{line}[/blue]")
                    else:
                        console.print(f"[dim]{line}[/dim]")
        
        elif output_format == 'side-by-side':
            console.print("[yellow]⚠️  Side-by-side format not yet implemented[/yellow]")
            console.print("[dim]Using unified format instead...[/dim]")
            # Fall back to unified for now
            
    except Exception as e:
        console.print(f"[red]❌ Error comparing schemas: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# SCHEMA VALIDATION COMMANDS
# =============================================================================

@schema_commands.command('validate')
@click.argument('schema_file', type=click.Path(exists=True), required=True)
@click.option('--strict', is_flag=True,
              help='Use strict validation rules')
@click.option('--format', 'output_format',
              type=click.Choice(['table', 'json', 'summary']),
              default='table',
              help='Output format for validation results')
@click.pass_context
@requires_permission('schema:validate')
def validate_schema(ctx, schema_file, strict, output_format):
    """Validate a schema file against JSON Schema standards
    
    Examples:
        plc-cl schema validate my-schema.json
        plc-cl schema validate schema.json --strict --format=json
    """
    try:
        # Load schema file
        with open(schema_file, 'r') as f:
            schema_data = json.load(f)
        
        # Perform validation
        validation_results = _validate_schema_comprehensive(schema_data, strict)
        
        # Display results
        if output_format == 'json':
            console.print_json(data=validation_results)
        elif output_format == 'table':
            _display_validation_table(validation_results)
        elif output_format == 'summary':
            _display_validation_summary(validation_results)
        
        # Exit with appropriate code
        if not validation_results['is_valid']:
            sys.exit(1)
            
    except Exception as e:
        console.print(f"[red]❌ Error validating schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('lint')
@click.argument('schema_id', required=True)
@click.option('--fix', is_flag=True,
              help='Automatically fix linting issues where possible')
@click.option('--rules', multiple=True,
              help='Specific linting rules to check')
@click.pass_context
@requires_permission('schema:validate')
def lint_schema(ctx, schema_id, fix, rules):
    """Lint a schema for best practices and potential issues
    
    Examples:
        plc-cl schema lint "my-schema"
        plc-cl schema lint "my-schema" --fix
        plc-cl schema lint "my-schema" --rules naming --rules structure
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schema
        schema_info = schema_manager.get_schema_by_id(schema_id)
        if not schema_info:
            console.print(f"[red]❌ Schema '{schema_id}' not found[/red]")
            sys.exit(1)
        
        # Load schema content
        schema_content = schema_manager.load_schema_content(schema_info)
        
        # Perform linting
        lint_results = _lint_schema_comprehensive(schema_content, list(rules) if rules else None)
        
        # Display results
        _display_lint_results(lint_results)
        
        # Apply fixes if requested
        if fix and lint_results['fixable_issues']:
            if Confirm.ask("Apply automatic fixes?", default=True):
                fixed_schema = _apply_lint_fixes(schema_content, lint_results['fixable_issues'])
                
                # Save fixed schema
                with open(schema_info.file_path, 'w') as f:
                    json.dump(fixed_schema, f, indent=2)
                
                console.print(f"[green]✅ Applied {len(lint_results['fixable_issues'])} fixes[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ Error linting schema: {str(e)}[/red]")
        sys.exit(1)

@schema_commands.command('test')
@click.argument('schema_id', required=True)
@click.option('--instance', '-i', 'instance_file',
              type=click.Path(exists=True),
              help='Test with specific instance file')
@click.option('--generate-examples', is_flag=True,
              help='Generate example instances for testing')
@click.pass_context
@requires_permission('schema:validate')
def test_schema(ctx, schema_id, instance_file, generate_examples):
    """Test a schema with instance data
    
    Examples:
        plc-cl schema test "my-schema" --instance data.json
        plc-cl schema test "my-schema" --generate-examples
    """
    try:
        cli_ctx: CLIContext = ctx.obj
        schema_manager = cli_ctx.schema_manager
        
        # Find schema
        schema_info = schema_manager.get_schema_by_id(schema_id)
        if not schema_info:
            console.print(f"[red]❌ Schema '{schema_id}' not found[/red]")
            sys.exit(1)
        
        # Load schema content
        schema_content = schema_manager.load_schema_content(schema_info)
        
        if instance_file:
            # Test with provided instance
            with open(instance_file, 'r') as f:
                instance_data = json.load(f)
            
            validation_errors = schema_manager.schema_manager.validate_instance(
                schema_info.schema_id, instance_data
            )
            
            if validation_errors:
                console.print(f"[red]❌ Instance validation failed:[/red]")
                for error in validation_errors:
                    console.print(f"  • {error}")
                sys.exit(1)
            else:
                console.print(f"[green]✅ Instance validation passed![/green]")
        
        elif generate_examples:
            # Generate example instances
            examples = _generate_schema_examples(schema_content)
            
            console.print(f"[bold]Generated examples for {schema_info.title}:[/bold]")
            for i, example in enumerate(examples, 1):
                console.print(f"\n[cyan]Example {i}:[/cyan]")
                syntax = Syntax(
                    json.dumps(example, indent=2),
                    "json",
                    theme="monokai"
                )
                console.print(syntax)
        
        else:
            console.print("[yellow]⚠️  Please specify --instance or --generate-examples[/yellow]")
            
    except Exception as e:
        console.print(f"[red]❌ Error testing schema: {str(e)}[/red]")
        sys.exit(1)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_subtype_properties(subtype: str) -> Dict[str, Any]:
    """Get additional properties for schema subtypes"""
    if subtype == 'feedforward':
        return {
            "feedforward_configuration": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "default": True},
                    "feedforward_gain": {"type": "number", "minimum": 0},
                    "disturbance_input": {"type": "string"}
                },
                "required": ["enabled", "feedforward_gain"]
            }
        }
    elif subtype == 'cascade':
        return {
            "cascade_configuration": {
                "type": "object",
                "properties": {
                    "master_loop": {"type": "boolean", "default": True},
                    "slave_setpoint_source": {"type": "string"},
                    "cascade_ratio": {"type": "number", "minimum": 0}
                },
                "required": ["master_loop"]
            }
        }
    elif subtype == 'combined':
        return {
            "feedforward_configuration": {
                "type": "object",
                "properties": {
                    "enabled": {"type": "boolean", "default": True},
                    "feedforward_gain": {"type": "number", "minimum": 0}
                }
            },
            "cascade_configuration": {
                "type": "object",
                "properties": {
                    "master_loop": {"type": "boolean", "default": True},
                    "cascade_ratio": {"type": "number", "minimum": 0}
                }
            }
        }
    elif subtype == 'multi-formula':
        return {
            "multi_formula_configuration": {
                "type": "object",
                "properties": {
                    "formula_count": {"type": "integer", "minimum": 1, "maximum": 4},
                    "weighted_feedforward": {"type": "boolean", "default": True},
                    "formula_weights": {
                        "type": "array",
                        "items": {"type": "number", "minimum": 0, "maximum": 1}
                    }
                },
                "required": ["formula_count"]
            }
        }
    else:
        return {}

def _increment_version(version: str, increment_type: str) -> str:
    """Increment version number based on type"""
    try:
        major, minor, patch = map(int, version.split('.'))
        
        if increment_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif increment_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
            
        return f"{major:02d}.{minor:02d}.{patch:03d}"
        
    except:
        # Fallback for invalid version format
        return "01.00.001"

def _validate_schema_comprehensive(schema_data: Dict[str, Any], strict: bool = False) -> Dict[str, Any]:
    """Comprehensive schema validation"""
    results = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "info": [],
        "validation_time": datetime.now().isoformat()
    }
    
    try:
        # JSON Schema Draft validation
        from jsonschema import Draft202012Validator
        validator = Draft202012Validator(schema_data)
        
        # Check schema structure
        try:
            validator.check_schema(schema_data)
            results["info"].append("JSON Schema structure is valid")
        except Exception as e:
            results["errors"].append(f"JSON Schema validation failed: {str(e)}")
            results["is_valid"] = False
        
        # Additional validation checks
        required_fields = ['$schema', 'title', 'description', 'type']
        for field in required_fields:
            if field not in schema_data:
                if strict:
                    results["errors"].append(f"Missing required field: {field}")
                    results["is_valid"] = False
                else:
                    results["warnings"].append(f"Recommended field missing: {field}")
        
        # Check for best practices
        if 'properties' in schema_data:
            prop_count = len(schema_data['properties'])
            if prop_count > 50:
                results["warnings"].append(f"Large number of properties ({prop_count}), consider breaking into sub-schemas")
            elif prop_count == 0:
                results["warnings"].append("Schema has no properties defined")
        
    except Exception as e:
        results["errors"].append(f"Validation error: {str(e)}")
        results["is_valid"] = False
    
    return results

def _lint_schema_comprehensive(schema_data: Dict[str, Any], rules: Optional[List[str]] = None) -> Dict[str, Any]:
    """Comprehensive schema linting"""
    results = {
        "issues": [],
        "fixable_issues": [],
        "score": 100,
        "categories": {
            "naming": [],
            "structure": [],
            "documentation": [],
            "validation": []
        }
    }
    
    # Naming checks
    if not rules or 'naming' in rules:
        if 'title' in schema_data:
            title = schema_data['title']
            if not title[0].isupper():
                results["categories"]["naming"].append("Title should start with capital letter")
                results["fixable_issues"].append({
                    "type": "title_case",
                    "current": title,
                    "suggested": title.title()
                })
    
    # Structure checks
    if not rules or 'structure' in rules:
        if 'properties' in schema_data:
            props = schema_data['properties']
            if 'required' not in schema_data:
                results["categories"]["structure"].append("No required fields specified")
        
    # Documentation checks
    if not rules or 'documentation' in rules:
        if 'description' not in schema_data or len(schema_data.get('description', '')) < 10:
            results["categories"]["documentation"].append("Description too short or missing")
    
    # Calculate total issues
    total_issues = sum(len(cat) for cat in results["categories"].values())
    results["issues"] = [issue for cat in results["categories"].values() for issue in cat]
    
    # Calculate score
    if total_issues > 0:
        results["score"] = max(0, 100 - (total_issues * 10))
    
    return results

def _display_validation_table(results: Dict[str, Any]):
    """Display validation results in table format"""
    table = Table(title="Schema Validation Results")
    table.add_column("Type", style="bold")
    table.add_column("Count", style="cyan")
    table.add_column("Messages", style="white")
    
    # Add rows for each type
    if results["errors"]:
        table.add_row("❌ Errors", str(len(results["errors"])), "\n".join(results["errors"]))
    
    if results["warnings"]:
        table.add_row("⚠️  Warnings", str(len(results["warnings"])), "\n".join(results["warnings"]))
    
    if results["info"]:
        table.add_row("ℹ️  Info", str(len(results["info"])), "\n".join(results["info"]))
    
    console.print(table)
    
    # Overall status
    if results["is_valid"]:
        console.print("\n[green]✅ Schema validation passed[/green]")
    else:
        console.print("\n[red]❌ Schema validation failed[/red]")

def _display_validation_summary(results: Dict[str, Any]):
    """Display validation summary"""
    status_color = "green" if results["is_valid"] else "red"
    status_icon = "✅" if results["is_valid"] else "❌"
    
    summary = f"{status_icon} Validation: {'PASSED' if results['is_valid'] else 'FAILED'}\n"
    summary += f"Errors: {len(results['errors'])}\n"
    summary += f"Warnings: {len(results['warnings'])}\n"
    summary += f"Info: {len(results['info'])}"
    
    panel = Panel(summary, title="Validation Summary", border_style=status_color)
    console.print(panel)

def _display_lint_results(results: Dict[str, Any]):
    """Display linting results"""
    console.print(f"[bold]Linting Score: {results['score']}/100[/bold]")
    
    if results["issues"]:
        table = Table(title="Linting Issues")
        table.add_column("Category", style="bold")
        table.add_column("Issues", style="white")
        
        for category, issues in results["categories"].items():
            if issues:
                table.add_row(category.title(), "\n".join(issues))
        
        console.print(table)
    else:
        console.print("[green]✅ No linting issues found[/green]")

def _apply_lint_fixes(schema_data: Dict[str, Any], fixes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply automatic lint fixes"""
    fixed_schema = schema_data.copy()
    
    for fix in fixes:
        if fix["type"] == "title_case":
            fixed_schema["title"] = fix["suggested"]
    
    return fixed_schema

def _generate_schema_examples(schema_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate example instances from schema"""
    examples = []
    
    # Basic example with required fields only
    if 'properties' in schema_data:
        basic_example = {}
        required_fields = schema_data.get('required', [])
        
        for field in required_fields:
            if field in schema_data['properties']:
                prop = schema_data['properties'][field]
                basic_example[field] = _generate_example_value(prop)
        
        if basic_example:
            examples.append(basic_example)
    
    return examples

def _generate_example_value(property_def: Dict[str, Any]) -> Any:
    """Generate example value for a property"""
    prop_type = property_def.get('type', 'string')
    
    if prop_type == 'string':
        if 'enum' in property_def:
            return property_def['enum'][0]
        return property_def.get('default', 'example_value')
    elif prop_type == 'number':
        return property_def.get('default', 1.0)
    elif prop_type == 'integer':
        return property_def.get('default', 1)
    elif prop_type == 'boolean':
        return property_def.get('default', True)
    elif prop_type == 'array':
        return []
    elif prop_type == 'object':
        return {}
    else:
        return None 