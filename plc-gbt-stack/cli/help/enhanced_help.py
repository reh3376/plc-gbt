#!/usr/bin/env python3
"""
📚 Phase 21.5: Enhanced Help System

Context-aware help system with comprehensive documentation, examples, tutorials,
and man page generation for all CLI commands.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (Documentation system with examples)
Context Management: Context-aware help with command history integration
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.5 Objectives:
- Context-aware help messages based on user history
- Comprehensive examples for every command
- Tutorial mode for beginners with step-by-step guidance
- Man page generation for offline documentation
- Interactive help with command suggestions

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.5.2 - Enhanced Help System
Dependencies: Phase 21.1-21.4 CLI framework, rich, click
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Set up console and logging
console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# HELP SYSTEM CLASSES
# =============================================================================

@dataclass
class HelpExample:
    """Individual help example"""
    title: str
    description: str
    command: str
    expected_output: Optional[str] = None
    notes: Optional[str] = None
    difficulty: str = "beginner"  # beginner, intermediate, advanced

@dataclass
class CommandHelp:
    """Comprehensive help information for a command"""
    command: str
    description: str
    synopsis: str
    options: List[Dict[str, str]] = field(default_factory=list)
    examples: List[HelpExample] = field(default_factory=list)
    related_commands: List[str] = field(default_factory=list)
    tutorials: List[str] = field(default_factory=list)
    troubleshooting: List[Dict[str, str]] = field(default_factory=list)
    see_also: List[str] = field(default_factory=list)

class HelpLevel(Enum):
    """Help detail levels"""
    BRIEF = "brief"
    NORMAL = "normal"
    DETAILED = "detailed"
    EXPERT = "expert"

class UserExperience(Enum):
    """User experience levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class UserContext:
    """User context for personalized help"""
    experience_level: UserExperience = UserExperience.BEGINNER
    command_history: List[str] = field(default_factory=list)
    frequent_commands: Dict[str, int] = field(default_factory=dict)
    last_help_requests: List[str] = field(default_factory=list)
    preferred_output_format: str = "table"
    completion_stats: Dict[str, Dict[str, int]] = field(default_factory=dict)

class EnhancedHelpSystem:
    """
    Enhanced help system with context-aware assistance

    Features:
    - Context-aware help based on user history
    - Comprehensive examples and tutorials
    - Interactive help with command suggestions
    - Man page generation
    - Difficulty-based filtering
    """

    def __init__(self):
        self.help_data: Dict[str, CommandHelp] = {}
        self.user_context = UserContext()
        self.help_cache: Dict[str, str] = {}
        self._load_help_data()

    def _load_help_data(self):
        """Load comprehensive help data for all commands"""

        # Schema commands help
        self.help_data["schema"] = CommandHelp(
            command="schema",
            description="Comprehensive schema management operations for control loop configurations",
            synopsis="plc-cl schema [SUBCOMMAND] [OPTIONS]",
            options=[
                {"option": "--format", "description": "Output format (table, json, yaml)"},
                {"option": "--verbose", "description": "Show detailed information"},
                {"option": "--help", "description": "Show command help"}
            ],
            examples=[
                HelpExample(
                    title="List all available schemas",
                    description="Display all schemas in the registry with basic information",
                    command="plc-cl schema list",
                    expected_output="Table showing schema names, types, versions, and descriptions",
                    difficulty="beginner"
                ),
                HelpExample(
                    title="Search for specific schema types",
                    description="Find schemas matching specific criteria",
                    command="plc-cl schema list --type=pid --status=active",
                    expected_output="Filtered list of PID-type schemas that are active",
                    difficulty="intermediate"
                ),
                HelpExample(
                    title="Get detailed schema information",
                    description="View complete details about a specific schema",
                    command="plc-cl schema info standard-pid",
                    expected_output="Comprehensive schema details including properties and validation rules",
                    difficulty="beginner"
                ),
                HelpExample(
                    title="Create new custom schema",
                    description="Create a new schema from scratch with guided wizard",
                    command="plc-cl schema create --name=my-cascade-pid --type=cascade",
                    expected_output="Interactive wizard to define schema properties",
                    difficulty="intermediate"
                ),
                HelpExample(
                    title="Validate schema against instances",
                    description="Test schema with example instance data",
                    command="plc-cl schema validate standard-pid --generate-examples",
                    expected_output="Validation results with example instance data",
                    difficulty="advanced"
                )
            ],
            related_commands=["instance", "batch", "config"],
            tutorials=["schema-creation-tutorial", "validation-best-practices"],
            troubleshooting=[
                {"problem": "Schema not found", "solution": "Check schema registry path and permissions"},
                {"problem": "Validation errors", "solution": "Review schema syntax and JSON Schema compliance"}
            ],
            see_also=["JSON Schema specification", "Control loop documentation"]
        )

        # Instance commands help
        self.help_data["instance"] = CommandHelp(
            command="instance",
            description="Control loop instance management with PLC integration capabilities",
            synopsis="plc-cl instance [SUBCOMMAND] [OPTIONS]",
            options=[
                {"option": "--schema", "description": "Base schema for instance creation"},
                {"option": "--plc-host", "description": "PLC IP address for connectivity"},
                {"option": "--format", "description": "Output format (table, json, yaml)"}
            ],
            examples=[
                HelpExample(
                    title="List all instances",
                    description="Show all configured control loop instances",
                    command="plc-cl instance list",
                    expected_output="Table of instances with names, schemas, and status",
                    difficulty="beginner"
                ),
                HelpExample(
                    title="Create new PID controller instance",
                    description="Create a control loop instance using standard PID schema",
                    command="plc-cl instance create --schema=standard-pid --name=reactor-temp-control",
                    expected_output="New instance created with default PID parameters",
                    difficulty="intermediate"
                ),
                HelpExample(
                    title="Connect to PLC and browse tags",
                    description="Establish read-only connection to ControlLogix PLC",
                    command="plc-cl instance plc connect --host=192.168.1.100 --slot=0",
                    expected_output="PLC connection status and available tag listing",
                    notes="Requires network access to PLC",
                    difficulty="advanced"
                ),
                HelpExample(
                    title="Real-time data monitoring",
                    description="Monitor PLC tag values in real-time",
                    command="plc-cl instance plc read 'Program:MainProgram.Temperature_PV'",
                    expected_output="Current tag value with timestamp and quality",
                    notes="PLC must be connected first",
                    difficulty="advanced"
                ),
                HelpExample(
                    title="Export instance configuration",
                    description="Export instance to portable format",
                    command="plc-cl instance export my-controller --format=json",
                    expected_output="JSON file with complete instance configuration",
                    difficulty="intermediate"
                )
            ],
            related_commands=["schema", "batch", "plc"],
            tutorials=["instance-creation-guide", "plc-integration-setup"],
            troubleshooting=[
                {"problem": "PLC connection failed", "solution": "Check network connectivity and PLC IP address"},
                {"problem": "Tag not found", "solution": "Verify tag name syntax and PLC program structure"}
            ]
        )

        # Batch commands help
        self.help_data["batch"] = CommandHelp(
            command="batch",
            description="Batch operations for enterprise-scale instance and schema management",
            synopsis="plc-cl batch [SUBCOMMAND] [OPTIONS]",
            options=[
                {"option": "--input", "description": "Input file for batch processing"},
                {"option": "--pattern", "description": "File pattern for batch operations"},
                {"option": "--parallel", "description": "Number of parallel operations"}
            ],
            examples=[
                HelpExample(
                    title="Batch create instances from CSV",
                    description="Create multiple instances from CSV file specification",
                    command="plc-cl batch create --from-csv=controllers.csv",
                    expected_output="Progress bar showing instance creation status",
                    difficulty="intermediate"
                ),
                HelpExample(
                    title="Validate multiple configurations",
                    description="Validate all JSON instance files in directory",
                    command="plc-cl batch validate --pattern='instances/*.json'",
                    expected_output="Validation report for all matching files",
                    difficulty="advanced"
                ),
                HelpExample(
                    title="Mass export for backup",
                    description="Export all instances for backup purposes",
                    command="plc-cl batch export --all --output-dir=backup/",
                    expected_output="All instances exported to backup directory",
                    difficulty="intermediate"
                )
            ],
            related_commands=["instance", "schema", "config"],
            tutorials=["batch-processing-guide", "automation-scripting"]
        )

        # REPL commands help
        self.help_data["repl"] = CommandHelp(
            command="repl",
            description="Interactive mode for real-time control loop management",
            synopsis="plc-cl repl [OPTIONS]",
            options=[
                {"option": "--verbose", "description": "Enable verbose output in REPL"},
                {"option": "--save-session", "description": "Auto-save session on exit"}
            ],
            examples=[
                HelpExample(
                    title="Start interactive session",
                    description="Launch REPL for interactive command execution",
                    command="plc-cl repl",
                    expected_output="Interactive prompt with command completion",
                    difficulty="beginner"
                ),
                HelpExample(
                    title="REPL with session saving",
                    description="Start REPL with automatic session persistence",
                    command="plc-cl repl --save-session",
                    expected_output="REPL with session history saved on exit",
                    difficulty="intermediate"
                )
            ],
            related_commands=["status", "help"],
            tutorials=["repl-user-guide", "interactive-workflows"]
        )

    def get_contextual_help(self, command: str, subcommand: Optional[str] = None,
                          level: HelpLevel = HelpLevel.NORMAL) -> str:
        """Get contextual help based on user experience and history"""

        # Update user context
        self._update_user_context(command, subcommand)

        # Get base help
        help_key = f"{command}.{subcommand}" if subcommand else command
        if help_key not in self.help_data and command in self.help_data:
            help_data = self.help_data[command]
        else:
            return self._generate_basic_help(command, subcommand)

        # Generate contextual help
        return self._generate_enhanced_help(help_data, level)

    def _update_user_context(self, command: str, subcommand: Optional[str] = None):
        """Update user context based on help request"""
        full_command = f"{command}.{subcommand}" if subcommand else command

        # Update command history
        self.user_context.command_history.append(full_command)
        if len(self.user_context.command_history) > 50:
            self.user_context.command_history = self.user_context.command_history[-50:]

        # Update frequency tracking
        if command not in self.user_context.frequent_commands:
            self.user_context.frequent_commands[command] = 0
        self.user_context.frequent_commands[command] += 1

        # Update help requests
        self.user_context.last_help_requests.append(full_command)
        if len(self.user_context.last_help_requests) > 10:
            self.user_context.last_help_requests = self.user_context.last_help_requests[-10:]

        # Auto-adjust experience level based on usage
        total_commands = sum(self.user_context.frequent_commands.values())
        if total_commands > 50:
            self.user_context.experience_level = UserExperience.ADVANCED
        elif total_commands > 20:
            self.user_context.experience_level = UserExperience.INTERMEDIATE

    def _generate_enhanced_help(self, help_data: CommandHelp, level: HelpLevel) -> str:
        """Generate enhanced help output"""

        # Create help sections
        sections = []

        # Title and description
        title_panel = Panel(
            f"[bold blue]{help_data.command.upper()}[/bold blue]\n\n{help_data.description}",
            title="Command Help",
            border_style="blue"
        )
        sections.append(title_panel)

        # Synopsis
        synopsis_text = f"[bold]SYNOPSIS[/bold]\n    {help_data.synopsis}"
        sections.append(synopsis_text)

        # Options (if detailed level)
        if level in [HelpLevel.DETAILED, HelpLevel.EXPERT] and help_data.options:
            options_table = Table(title="Options")
            options_table.add_column("Option", style="cyan")
            options_table.add_column("Description", style="white")

            for option in help_data.options:
                options_table.add_row(option["option"], option["description"])

            sections.append(options_table)

        # Examples (filtered by user experience)
        if help_data.examples:
            examples_text = "[bold]EXAMPLES[/bold]\n"

            # Filter examples by difficulty
            suitable_examples = self._filter_examples_by_experience(help_data.examples)

            for i, example in enumerate(suitable_examples[:5], 1):  # Show max 5 examples
                examples_text += f"\n[bold cyan]{i}. {example.title}[/bold cyan]\n"
                examples_text += f"   {example.description}\n"
                examples_text += f"   [yellow]$ {example.command}[/yellow]\n"

                if example.expected_output and level == HelpLevel.DETAILED:
                    examples_text += f"   [dim]Expected: {example.expected_output}[/dim]\n"

                if example.notes:
                    examples_text += f"   [dim]Note: {example.notes}[/dim]\n"

            sections.append(examples_text)

        # Related commands (if not beginner)
        if (self.user_context.experience_level != UserExperience.BEGINNER and
            help_data.related_commands):
            related_text = "[bold]RELATED COMMANDS[/bold]\n"
            related_text += ", ".join([f"[cyan]{cmd}[/cyan]" for cmd in help_data.related_commands])
            sections.append(related_text)

        # Troubleshooting (if advanced)
        if (level == HelpLevel.DETAILED and help_data.troubleshooting):
            troubleshooting_table = Table(title="Common Issues")
            troubleshooting_table.add_column("Problem", style="red")
            troubleshooting_table.add_column("Solution", style="green")

            for issue in help_data.troubleshooting:
                troubleshooting_table.add_row(issue["problem"], issue["solution"])

            sections.append(troubleshooting_table)

        # Generate personalized suggestions
        if level == HelpLevel.EXPERT:
            suggestions = self._generate_personalized_suggestions(help_data.command)
            if suggestions:
                suggestions_text = f"[bold]PERSONALIZED SUGGESTIONS[/bold]\n{suggestions}"
                sections.append(suggestions_text)

        return "\n\n".join([str(section) for section in sections])

    def _filter_examples_by_experience(self, examples: List[HelpExample]) -> List[HelpExample]:
        """Filter examples based on user experience level"""
        experience_levels = {
            UserExperience.BEGINNER: ["beginner"],
            UserExperience.INTERMEDIATE: ["beginner", "intermediate"],
            UserExperience.ADVANCED: ["beginner", "intermediate", "advanced"],
            UserExperience.EXPERT: ["beginner", "intermediate", "advanced", "expert"]
        }

        allowed_difficulties = experience_levels[self.user_context.experience_level]
        return [ex for ex in examples if ex.difficulty in allowed_difficulties]

    def _generate_personalized_suggestions(self, command: str) -> str:
        """Generate personalized suggestions based on user history"""
        suggestions = []

        # Suggest based on command frequency
        if command in self.user_context.frequent_commands:
            count = self.user_context.frequent_commands[command]
            if count > 10:
                suggestions.append(f"You've used {command} {count} times - consider creating aliases for common operations")

        # Suggest based on recent help requests
        recent_helps = self.user_context.last_help_requests[-5:]
        if command in recent_helps:
            suggestions.append(f"Consider exploring the tutorial mode for {command} with: plc-cl tutorial {command}")

        # Suggest related workflows
        if command == "schema":
            suggestions.append("After creating schemas, use 'instance create' to build control loop instances")
        elif command == "instance":
            suggestions.append("Use 'batch' commands for managing multiple instances efficiently")

        return "\n".join([f"• {suggestion}" for suggestion in suggestions])

    def _generate_basic_help(self, command: str, subcommand: Optional[str] = None) -> str:
        """Generate basic help for unknown commands"""
        return f"Help not available for: {command}" + (f" {subcommand}" if subcommand else "")

    def generate_tutorial(self, topic: str) -> str:
        """Generate interactive tutorial for specific topic"""
        tutorials = {
            "schema": self._schema_tutorial(),
            "instance": self._instance_tutorial(),
            "getting-started": self._getting_started_tutorial()
        }

        return tutorials.get(topic, f"Tutorial not available for: {topic}")

    def _schema_tutorial(self) -> str:
        """Schema management tutorial"""
        return """
[bold blue]📚 Schema Management Tutorial[/bold blue]

[bold]Step 1: Understanding Schemas[/bold]
Schemas define the structure and validation rules for control loop configurations.

[bold]Step 2: List Available Schemas[/bold]
    [yellow]$ plc-cl schema list[/yellow]

[bold]Step 3: Examine a Schema[/bold]
    [yellow]$ plc-cl schema info standard-pid[/yellow]

[bold]Step 4: Create Your First Schema[/bold]
    [yellow]$ plc-cl schema wizard[/yellow]

[bold]Step 5: Validate Your Schema[/bold]
    [yellow]$ plc-cl schema validate my-schema --generate-examples[/yellow]

[bold]Next Steps:[/bold]
• Create instances using your schema with 'instance create'
• Learn batch operations with 'tutorial batch'
"""

    def _instance_tutorial(self) -> str:
        """Instance management tutorial"""
        return """
[bold blue]📚 Instance Management Tutorial[/bold blue]

[bold]Step 1: Understanding Instances[/bold]
Instances are specific control loop configurations based on schemas.

[bold]Step 2: List Available Instances[/bold]
    [yellow]$ plc-cl instance list[/yellow]

[bold]Step 3: Create Your First Instance[/bold]
    [yellow]$ plc-cl instance create --schema=standard-pid --name=my-controller[/yellow]

[bold]Step 4: Connect to PLC (Advanced)[/bold]
    [yellow]$ plc-cl instance plc connect --host=YOUR_PLC_IP[/yellow]

[bold]Step 5: Monitor Real-time Data[/bold]
    [yellow]$ plc-cl instance plc read 'Program:MainProgram.TagName'[/yellow]

[bold]Next Steps:[/bold]
• Explore batch operations for multiple instances
• Learn REPL mode for interactive management
"""

    def _getting_started_tutorial(self) -> str:
        """Getting started tutorial"""
        return """
[bold blue]🚀 Getting Started with PLC Control Loop CLI[/bold blue]

[bold]Step 1: Check System Status[/bold]
    [yellow]$ plc-cl status[/yellow]

[bold]Step 2: Explore Available Schemas[/bold]
    [yellow]$ plc-cl schema list[/yellow]

[bold]Step 3: Create Your First Instance[/bold]
    [yellow]$ plc-cl instance create --schema=standard-pid[/yellow]

[bold]Step 4: Try Interactive Mode[/bold]
    [yellow]$ plc-cl repl[/yellow]

[bold]Step 5: Get Help Anytime[/bold]
    [yellow]$ plc-cl help [command][/yellow]

[bold]Quick Tips:[/bold]
• Use --help with any command for detailed information
• Start with schema management, then create instances
• REPL mode is great for interactive exploration
"""

    def generate_man_page(self, command: str) -> str:
        """Generate man page format documentation"""
        if command not in self.help_data:
            return f"No manual page available for {command}"

        help_data = self.help_data[command]

        man_page = f"""PLC-CL-{command.upper()}(1)                    User Commands                    PLC-CL-{command.upper()}(1)

NAME
       plc-cl {command} - {help_data.description}

SYNOPSIS
       {help_data.synopsis}

DESCRIPTION
       {help_data.description}

OPTIONS
"""

        for option in help_data.options:
            man_page += f"       {option['option']}\n              {option['description']}\n\n"

        man_page += "EXAMPLES\n"
        for example in help_data.examples[:3]:
            man_page += f"       {example.command}\n              {example.description}\n\n"

        if help_data.see_also:
            man_page += "SEE ALSO\n"
            man_page += f"       {', '.join(help_data.see_also)}\n\n"

        man_page += f"PLC Control Loop CLI                  {datetime.now().strftime('%B %Y')}                    PLC-CL-{command.upper()}(1)"

        return man_page

# =============================================================================
# GLOBAL HELP SYSTEM INSTANCE
# =============================================================================

_help_system: Optional[EnhancedHelpSystem] = None

def get_help_system() -> EnhancedHelpSystem:
    """Get or create global help system instance"""
    global _help_system
    if _help_system is None:
        _help_system = EnhancedHelpSystem()
    return _help_system

def show_contextual_help(command: str, subcommand: Optional[str] = None,
                        level: HelpLevel = HelpLevel.NORMAL):
    """Show contextual help for a command"""
    help_system = get_help_system()
    help_content = help_system.get_contextual_help(command, subcommand, level)
    console.print(help_content)

def show_tutorial(topic: str):
    """Show interactive tutorial"""
    help_system = get_help_system()
    tutorial_content = help_system.generate_tutorial(topic)
    console.print(tutorial_content)

def generate_man_page_file(command: str, output_path: Optional[Path] = None):
    """Generate man page file for a command"""
    help_system = get_help_system()
    man_content = help_system.generate_man_page(command)

    if output_path is None:
        output_path = Path(f"plc-cl-{command}.1")

    with open(output_path, 'w') as f:
        f.write(man_content)

    console.print(f"[green]✅ Man page generated: {output_path}[/green]")

# =============================================================================
# CLI INTEGRATION COMMANDS
# =============================================================================

@click.command()
@click.argument('command', required=False)
@click.option('--detailed', '-d', is_flag=True, help='Show detailed help')
@click.option('--tutorial', '-t', is_flag=True, help='Show interactive tutorial')
@click.option('--man-page', is_flag=True, help='Generate man page')
@click.option('--examples-only', is_flag=True, help='Show only examples')
def enhanced_help(command, detailed, tutorial, man_page, examples_only):
    """Enhanced help system with context-aware assistance"""

    if not command:
        # Show general help
        show_contextual_help("general")
        return

    if tutorial:
        show_tutorial(command)
    elif man_page:
        generate_man_page_file(command)
    else:
        level = HelpLevel.DETAILED if detailed else HelpLevel.NORMAL
        show_contextual_help(command, level=level)

if __name__ == "__main__":
    enhanced_help()
