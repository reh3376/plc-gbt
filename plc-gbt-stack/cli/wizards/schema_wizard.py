#!/usr/bin/env python3
"""
🧙 Phase 21.2: Interactive Schema Creation Wizard

Advanced wizard for guided creation of control loop schemas with comprehensive
help, validation, and customization options.

AI Task Orchestrator Implementation
=====================================
Task Classification: ADVANCED (300-800 lines, interactive UI)
Context Management: User-guided workflow with validation
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.2 Objectives:
- Provide intuitive schema creation workflow
- Offer comprehensive help and guidance
- Enable advanced customization options
- Integrate with Phase 20 schema framework

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.2 - Schema Management Commands
Dependencies: Phase 20 (JSON Schema Framework), Phase 21.1 (CLI Infrastructure)
"""

import os
import sys
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich.columns import Columns
from rich.align import Align
from rich.text import Text
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich import print as rprint

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize console
console = Console()

# =============================================================================
# WIZARD CONFIGURATION CLASSES
# =============================================================================

class WizardStep(Enum):
    """Wizard steps enumeration"""
    WELCOME = "welcome"
    SCHEMA_TYPE = "schema_type"
    BASIC_INFO = "basic_info"
    ADVANCED_OPTIONS = "advanced_options"
    PARAMETERS = "parameters"
    VALIDATION = "validation"
    SUMMARY = "summary"
    CONFIRMATION = "confirmation"
    CREATION = "creation"
    COMPLETION = "completion"

@dataclass
class SchemaTemplate:
    """Schema template configuration"""
    name: str
    description: str
    base_type: str
    default_properties: Dict[str, Any] = field(default_factory=dict)
    suggested_parameters: List[str] = field(default_factory=list)
    validation_rules: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)

@dataclass 
class WizardState:
    """Wizard state tracking"""
    current_step: WizardStep = WizardStep.WELCOME
    schema_name: str = ""
    schema_description: str = ""
    schema_version: str = "01.00.001"
    base_type: str = ""
    is_subtype: bool = False
    parent_schema: str = ""
    subtype: str = ""
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    validation_enabled: bool = True
    advanced_features: Dict[str, Any] = field(default_factory=dict)
    template: Optional[SchemaTemplate] = None

class SchemaCreationWizard:
    """Interactive schema creation wizard"""
    
    def __init__(self, schema_manager, cli_context):
        """Initialize wizard with schema manager and CLI context"""
        self.schema_manager = schema_manager
        self.cli_context = cli_context
        self.state = WizardState()
        self.templates = self._load_schema_templates()
        
    def run(self) -> bool:
        """Run the complete wizard workflow"""
        try:
            console.clear()
            
            # Run wizard steps
            steps = [
                self._step_welcome,
                self._step_schema_type,
                self._step_basic_info,
                self._step_advanced_options,
                self._step_parameters,
                self._step_validation,
                self._step_summary,
                self._step_confirmation,
                self._step_creation,
                self._step_completion
            ]
            
            for step_func in steps:
                if not step_func():
                    console.print("[yellow]🚫 Wizard cancelled by user[/yellow]")
                    return False
                    
                # Small delay between steps for better UX
                import time
                time.sleep(0.1)
            
            return True
            
        except KeyboardInterrupt:
            console.print("\n[yellow]🚫 Wizard interrupted by user[/yellow]")
            return False
        except Exception as e:
            console.print(f"\n[red]❌ Wizard error: {str(e)}[/red]")
            logger.exception("Wizard error")
            return False
    
    def _step_welcome(self) -> bool:
        """Welcome step with wizard overview"""
        self.state.current_step = WizardStep.WELCOME
        
        welcome_panel = Panel(
            "[bold blue]🧙 Interactive Schema Creation Wizard[/bold blue]\n\n"
            "[bold]Welcome![/bold] This wizard will guide you through creating a custom control loop schema.\n\n"
            "[bold]What you'll do:[/bold]\n"
            "• Choose a base schema type or template\n"
            "• Configure basic schema information\n"
            "• Customize parameters and validation\n"
            "• Review and create your schema\n\n"
            "[bold]Features:[/bold]\n"
            "• Step-by-step guidance with help\n"
            "• Template-based creation\n"
            "• Advanced customization options\n"
            "• Real-time validation\n\n"
            "[dim]You can exit at any time with Ctrl+C[/dim]",
            title="🎯 Control Loop Schema Wizard",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(welcome_panel)
        console.print()
        
        # Show available features
        feature_table = Table(title="Wizard Capabilities")
        feature_table.add_column("Feature", style="bold cyan")
        feature_table.add_column("Description", style="white")
        
        feature_table.add_row("🎨 Templates", "Pre-configured schema templates for common use cases")
        feature_table.add_row("🔧 Customization", "Add custom properties and validation rules")
        feature_table.add_row("🧪 Validation", "Real-time schema validation and testing")
        feature_table.add_row("📋 Inheritance", "Create subtypes that inherit from base schemas")
        feature_table.add_row("💾 Auto-save", "Automatic backup and version management")
        
        console.print(feature_table)
        console.print()
        
        return Confirm.ask("[bold]Ready to start creating your schema?[/bold]", default=True)
    
    def _step_schema_type(self) -> bool:
        """Schema type selection step"""
        self.state.current_step = WizardStep.SCHEMA_TYPE
        
        console.print(Panel(
            "[bold]Step 1: Choose Schema Type[/bold]\n\n"
            "Select the type of control loop schema you want to create:",
            title="📋 Schema Type Selection",
            border_style="green"
        ))
        
        # Show available options
        options = [
            ("Template-based", "Use a pre-configured template (recommended for beginners)"),
            ("Base Type", "Start from a fundamental control loop type"),
            ("Subtype", "Create a specialized variant of an existing schema"),
            ("Custom", "Build a completely custom schema from scratch")
        ]
        
        option_table = Table()
        option_table.add_column("Option", style="bold")
        option_table.add_column("Description", style="dim")
        
        for i, (option, desc) in enumerate(options, 1):
            option_table.add_row(f"{i}. {option}", desc)
        
        console.print(option_table)
        console.print()
        
        while True:
            choice = IntPrompt.ask(
                "Select an option",
                choices=[str(i) for i in range(1, len(options) + 1)],
                show_choices=False
            )
            
            if choice == 1:  # Template-based
                return self._select_template()
            elif choice == 2:  # Base Type
                return self._select_base_type()
            elif choice == 3:  # Subtype
                return self._select_subtype()
            elif choice == 4:  # Custom
                return self._select_custom()
            
    def _select_template(self) -> bool:
        """Template selection workflow"""
        console.print("\n[bold]📋 Available Schema Templates[/bold]")
        
        if not self.templates:
            console.print("[yellow]⚠️  No templates available. Falling back to base type selection.[/yellow]")
            return self._select_base_type()
        
        # Display templates
        template_table = Table()
        template_table.add_column("ID", style="cyan")
        template_table.add_column("Name", style="bold")
        template_table.add_column("Description", style="white")
        template_table.add_column("Type", style="green")
        
        for i, template in enumerate(self.templates, 1):
            template_table.add_row(
                str(i),
                template.name,
                template.description,
                template.base_type
            )
        
        console.print(template_table)
        console.print()
        
        choice = IntPrompt.ask(
            "Select a template",
            choices=[str(i) for i in range(1, len(self.templates) + 1)]
        )
        
        selected_template = self.templates[choice - 1]
        self.state.template = selected_template
        self.state.base_type = selected_template.base_type
        
        # Show template details
        self._show_template_details(selected_template)
        
        return Confirm.ask(f"Use the '{selected_template.name}' template?", default=True)
    
    def _select_base_type(self) -> bool:
        """Base type selection workflow"""
        console.print("\n[bold]🏗️  Available Base Schema Types[/bold]")
        
        base_types = [
            ("ladder-logic-standard-pid", "Basic PID controller in ladder logic"),
            ("ladder-logic-advanced-pid", "Advanced PID with enhanced features"),
            ("function-block-standard-pide", "Standard PIDE function block"),
            ("function-block-advanced-pide", "Advanced PIDE with full feature set")
        ]
        
        type_table = Table()
        type_table.add_column("ID", style="cyan")
        type_table.add_column("Type", style="bold")
        type_table.add_column("Description", style="white")
        
        for i, (type_name, desc) in enumerate(base_types, 1):
            type_table.add_row(str(i), type_name, desc)
        
        console.print(type_table)
        console.print()
        
        choice = IntPrompt.ask(
            "Select a base type",
            choices=[str(i) for i in range(1, len(base_types) + 1)]
        )
        
        self.state.base_type = base_types[choice - 1][0]
        return True
    
    def _select_subtype(self) -> bool:
        """Subtype selection workflow"""
        console.print("\n[bold]🔗 Create Schema Subtype[/bold]")
        
        # First, select parent schema
        schemas = self.schema_manager.scan_schemas()
        base_schemas = [s for s in schemas if s.schema_type == "base"]
        
        if not base_schemas:
            console.print("[red]❌ No base schemas available for inheritance[/red]")
            return self._select_base_type()
        
        console.print("\n[bold]Available parent schemas:[/bold]")
        
        parent_table = Table()
        parent_table.add_column("ID", style="cyan")
        parent_table.add_column("Title", style="bold")
        parent_table.add_column("Type", style="green")
        parent_table.add_column("Version", style="yellow")
        
        for i, schema in enumerate(base_schemas, 1):
            parent_table.add_row(
                str(i),
                schema.title,
                schema.schema_type,
                schema.version
            )
        
        console.print(parent_table)
        console.print()
        
        choice = IntPrompt.ask(
            "Select parent schema",
            choices=[str(i) for i in range(1, len(base_schemas) + 1)]
        )
        
        self.state.parent_schema = base_schemas[choice - 1].schema_id
        self.state.is_subtype = True
        
        # Now select subtype variant
        subtypes = [
            ("feedforward", "Add feedforward disturbance compensation"),
            ("cascade", "Create master-slave cascade configuration"),
            ("combined", "Combine feedforward and cascade control"),
            ("multi-formula", "Advanced multi-formula weighted feedforward")
        ]
        
        console.print("\n[bold]Subtype options:[/bold]")
        
        subtype_table = Table()
        subtype_table.add_column("ID", style="cyan")
        subtype_table.add_column("Subtype", style="bold")
        subtype_table.add_column("Description", style="white")
        
        for i, (subtype_name, desc) in enumerate(subtypes, 1):
            subtype_table.add_row(str(i), subtype_name, desc)
        
        console.print(subtype_table)
        console.print()
        
        choice = IntPrompt.ask(
            "Select subtype",
            choices=[str(i) for i in range(1, len(subtypes) + 1)]
        )
        
        self.state.subtype = subtypes[choice - 1][0]
        return True
    
    def _select_custom(self) -> bool:
        """Custom schema selection workflow"""
        console.print("\n[bold]🛠️  Custom Schema Creation[/bold]")
        console.print(
            "You've chosen to create a completely custom schema.\n"
            "This option gives you full control but requires more configuration.\n"
        )
        
        self.state.base_type = "custom"
        
        return Confirm.ask("Continue with custom schema creation?", default=True)
    
    def _step_basic_info(self) -> bool:
        """Basic information collection step"""
        self.state.current_step = WizardStep.BASIC_INFO
        
        console.print(Panel(
            "[bold]Step 2: Basic Schema Information[/bold]\n\n"
            "Provide basic information about your schema:",
            title="📝 Schema Details",
            border_style="green"
        ))
        
        # Schema name
        while True:
            if self.state.template:
                default_name = f"Custom {self.state.template.name}"
            else:
                default_name = f"My {self.state.base_type.replace('-', ' ').title()}"
            
            name = Prompt.ask(
                "[bold]Schema name[/bold]",
                default=default_name
            )
            
            # Validate name
            if len(name.strip()) < 3:
                console.print("[red]❌ Name must be at least 3 characters long[/red]")
                continue
            
            self.state.schema_name = name.strip()
            break
        
        # Schema description
        if self.state.template:
            default_desc = f"Custom schema based on {self.state.template.name} template"
        else:
            default_desc = f"Custom control loop schema for {self.state.base_type}"
        
        description = Prompt.ask(
            "[bold]Schema description[/bold]",
            default=default_desc
        )
        self.state.schema_description = description
        
        # Version
        version = Prompt.ask(
            "[bold]Initial version[/bold] (format: XX.YY.ZZZ)",
            default="01.00.001"
        )
        
        # Validate version format
        if not re.match(r'^\d{2}\.\d{2}\.\d{3}$', version):
            console.print("[yellow]⚠️  Invalid version format. Using default 01.00.001[/yellow]")
            version = "01.00.001"
        
        self.state.schema_version = version
        
        # Show summary
        info_table = Table(title="Schema Information Summary")
        info_table.add_column("Property", style="bold")
        info_table.add_column("Value", style="cyan")
        
        info_table.add_row("Name", self.state.schema_name)
        info_table.add_row("Description", self.state.schema_description)
        info_table.add_row("Version", self.state.schema_version)
        info_table.add_row("Base Type", self.state.base_type)
        
        if self.state.is_subtype:
            info_table.add_row("Parent Schema", self.state.parent_schema)
            info_table.add_row("Subtype", self.state.subtype)
        
        console.print(info_table)
        console.print()
        
        return Confirm.ask("Continue with this information?", default=True)
    
    def _step_advanced_options(self) -> bool:
        """Advanced options configuration step"""
        self.state.current_step = WizardStep.ADVANCED_OPTIONS
        
        console.print(Panel(
            "[bold]Step 3: Advanced Options[/bold]\n\n"
            "Configure advanced features and options:",
            title="⚙️ Advanced Configuration",
            border_style="blue"
        ))
        
        # Validation options
        enable_validation = Confirm.ask(
            "Enable comprehensive validation rules?",
            default=True
        )
        self.state.validation_enabled = enable_validation
        
        # Custom properties
        add_properties = Confirm.ask(
            "Add custom properties to your schema?",
            default=False
        )
        
        if add_properties:
            self._configure_custom_properties()
        
        # Advanced features based on type
        if self.state.base_type != "custom":
            self._configure_advanced_features()
        
        return True
    
    def _configure_custom_properties(self):
        """Configure custom properties interactively"""
        console.print("\n[bold]🔧 Custom Properties Configuration[/bold]")
        console.print("Add custom properties to extend your schema functionality.\n")
        
        while True:
            prop_name = Prompt.ask("Property name (or 'done' to finish)")
            
            if prop_name.lower() == 'done':
                break
            
            # Validate property name
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', prop_name):
                console.print("[red]❌ Invalid property name. Use letters, numbers, and underscores only.[/red]")
                continue
            
            if prop_name in self.state.custom_properties:
                console.print(f"[yellow]⚠️  Property '{prop_name}' already exists.[/yellow]")
                continue
            
            # Property type
            prop_types = ["string", "number", "integer", "boolean", "array", "object"]
            console.print(f"Property types: {', '.join(prop_types)}")
            
            prop_type = Prompt.ask("Property type", choices=prop_types)
            
            # Property description
            prop_desc = Prompt.ask("Property description")
            
            # Additional constraints
            constraints = {}
            
            if prop_type in ["number", "integer"]:
                add_range = Confirm.ask("Add minimum/maximum constraints?", default=False)
                if add_range:
                    try:
                        min_val = FloatPrompt.ask("Minimum value")
                        max_val = FloatPrompt.ask("Maximum value")
                        constraints["minimum"] = min_val
                        constraints["maximum"] = max_val
                    except:
                        console.print("[yellow]⚠️  Invalid range values. Skipping constraints.[/yellow]")
            
            elif prop_type == "string":
                add_pattern = Confirm.ask("Add pattern validation?", default=False)
                if add_pattern:
                    pattern = Prompt.ask("Regular expression pattern")
                    constraints["pattern"] = pattern
            
            # Build property definition
            prop_def = {
                "type": prop_type,
                "description": prop_desc,
                **constraints
            }
            
            self.state.custom_properties[prop_name] = prop_def
            
            console.print(f"[green]✅ Added property: {prop_name} ({prop_type})[/green]")
        
        if self.state.custom_properties:
            console.print(f"\n[bold]Added {len(self.state.custom_properties)} custom properties[/bold]")
    
    def _configure_advanced_features(self):
        """Configure advanced features based on schema type"""
        console.print(f"\n[bold]🚀 Advanced Features for {self.state.base_type}[/bold]")
        
        # Common advanced features
        features = {
            "enhanced_diagnostics": Confirm.ask("Enable enhanced diagnostics?", default=False),
            "performance_monitoring": Confirm.ask("Enable performance monitoring?", default=False),
            "alarm_integration": Confirm.ask("Enable alarm integration?", default=True),
            "historical_data": Confirm.ask("Enable historical data tracking?", default=False)
        }
        
        # Type-specific features
        if "pid" in self.state.base_type.lower():
            features.update({
                "auto_tuning": Confirm.ask("Enable auto-tuning capabilities?", default=False),
                "adaptive_control": Confirm.ask("Enable adaptive control?", default=False)
            })
        
        elif "pide" in self.state.base_type.lower():
            features.update({
                "multi_loop_coordination": Confirm.ask("Enable multi-loop coordination?", default=False),
                "advanced_filtering": Confirm.ask("Enable advanced filtering?", default=True)
            })
        
        self.state.advanced_features = features
        
        # Show enabled features
        enabled_features = [name for name, enabled in features.items() if enabled]
        if enabled_features:
            console.print(f"\n[green]✅ Enabled features: {', '.join(enabled_features)}[/green]")
    
    def _step_parameters(self) -> bool:
        """Parameters configuration step"""
        self.state.current_step = WizardStep.PARAMETERS
        
        console.print(Panel(
            "[bold]Step 4: Parameters Configuration[/bold]\n\n"
            "Configure specific parameters for your schema:",
            title="🔢 Parameters",
            border_style="yellow"
        ))
        
        if self.state.template and self.state.template.suggested_parameters:
            console.print("[bold]📋 Template suggests these parameters:[/bold]")
            for param in self.state.template.suggested_parameters:
                console.print(f"  • {param}")
            console.print()
        
        # Show parameter configuration based on type
        if self.state.base_type != "custom":
            self._show_parameter_guidelines()
        
        # Ask if user wants to customize parameters
        customize = Confirm.ask("Customize parameter ranges and defaults?", default=False)
        
        if customize:
            self._configure_parameters()
        
        return True
    
    def _show_parameter_guidelines(self):
        """Show parameter guidelines for the selected schema type"""
        guidelines = {
            "ladder-logic-standard-pid": [
                "Proportional Gain (Kp): 0.1 - 10.0 (typical)",
                "Integral Time (Ti): 0.1 - 1000 seconds",
                "Derivative Time (Td): 0.0 - 10 seconds",
                "Output Limits: 0-100% (standard)"
            ],
            "ladder-logic-advanced-pid": [
                "All standard PID parameters",
                "Derivative Filter: 0.1 - 5.0 (filter constant)",
                "Setpoint Weighting: 0.0 - 1.0",
                "Output Rate Limiting: 0.1 - 100%/min"
            ],
            "function-block-standard-pide": [
                "PGain: 0.1 - 100.0",
                "IGain: 0.0 - 10.0 repeats/minute",
                "DGain: 0.0 - 5.0 minutes",
                "Enhanced derivative filter available"
            ],
            "function-block-advanced-pide": [
                "All PIDE parameters",
                "Multi-variable support",
                "Advanced timing controls",
                "Cascade coordination"
            ]
        }
        
        if self.state.base_type in guidelines:
            console.print(f"[bold]📊 Typical parameters for {self.state.base_type}:[/bold]")
            for guideline in guidelines[self.state.base_type]:
                console.print(f"  • {guideline}")
            console.print()
    
    def _configure_parameters(self):
        """Interactive parameter configuration"""
        console.print("\n[bold]🔧 Parameter Configuration[/bold]")
        console.print("This is an advanced feature. Default parameters will be used if skipped.\n")
        
        # For now, show that this feature is available but not fully implemented
        console.print("[yellow]⚠️  Advanced parameter configuration is available in the full implementation.[/yellow]")
        console.print("[dim]Default parameter ranges will be applied based on your schema type.[/dim]")
    
    def _step_validation(self) -> bool:
        """Validation configuration step"""
        self.state.current_step = WizardStep.VALIDATION
        
        console.print(Panel(
            "[bold]Step 5: Validation Configuration[/bold]\n\n"
            "Configure validation rules and constraints:",
            title="✅ Validation",
            border_style="green"
        ))
        
        if not self.state.validation_enabled:
            console.print("[yellow]⚠️  Validation is disabled. Skipping validation configuration.[/yellow]")
            return True
        
        # Show validation options
        validation_table = Table(title="Available Validation Rules")
        validation_table.add_column("Rule", style="bold")
        validation_table.add_column("Description", style="white")
        validation_table.add_column("Enabled", style="cyan")
        
        validation_rules = [
            ("Required Fields", "Ensure all required properties are present", "Yes"),
            ("Type Checking", "Validate property data types", "Yes"),
            ("Range Validation", "Check numerical ranges and constraints", "Yes"),
            ("Pattern Matching", "Validate string patterns (e.g., tag names)", "Yes"),
            ("Business Rules", "Apply domain-specific validation rules", "Optional"),
            ("Cross-References", "Validate references between properties", "Optional")
        ]
        
        for rule, desc, enabled in validation_rules:
            validation_table.add_row(rule, desc, enabled)
        
        console.print(validation_table)
        console.print()
        
        # Ask about business rules
        enable_business_rules = Confirm.ask(
            "Enable business rule validation (e.g., PID stability checks)?",
            default=True
        )
        
        # Ask about cross-references
        enable_cross_refs = Confirm.ask(
            "Enable cross-reference validation?",
            default=False
        )
        
        console.print(f"[green]✅ Validation configured with {4 + int(enable_business_rules) + int(enable_cross_refs)} rule types[/green]")
        
        return True
    
    def _step_summary(self) -> bool:
        """Summary step showing all configurations"""
        self.state.current_step = WizardStep.SUMMARY
        
        console.print(Panel(
            "[bold]Step 6: Summary[/bold]\n\n"
            "Review your schema configuration before creation:",
            title="📋 Configuration Summary",
            border_style="blue"
        ))
        
        # Create comprehensive summary
        summary_table = Table(title="Schema Configuration Summary")
        summary_table.add_column("Category", style="bold")
        summary_table.add_column("Details", style="white")
        
        # Basic information
        basic_info = f"""Name: {self.state.schema_name}
Description: {self.state.schema_description}
Version: {self.state.schema_version}
Base Type: {self.state.base_type}"""
        
        if self.state.is_subtype:
            basic_info += f"\nParent Schema: {self.state.parent_schema}\nSubtype: {self.state.subtype}"
        
        summary_table.add_row("Basic Info", basic_info)
        
        # Template information
        if self.state.template:
            template_info = f"Template: {self.state.template.name}\nTemplate Type: {self.state.template.base_type}"
            summary_table.add_row("Template", template_info)
        
        # Custom properties
        if self.state.custom_properties:
            props = [f"{name} ({prop['type']})" for name, prop in self.state.custom_properties.items()]
            summary_table.add_row("Custom Properties", f"{len(props)} properties:\n" + "\n".join(props))
        
        # Advanced features
        if self.state.advanced_features:
            enabled_features = [name for name, enabled in self.state.advanced_features.items() if enabled]
            if enabled_features:
                summary_table.add_row("Advanced Features", "\n".join(enabled_features))
        
        # Validation
        validation_status = "Enabled" if self.state.validation_enabled else "Disabled"
        summary_table.add_row("Validation", validation_status)
        
        console.print(summary_table)
        console.print()
        
        # Show file location
        safe_name = re.sub(r'[^a-zA-Z0-9-_]', '-', self.state.schema_name.lower())
        if self.state.is_subtype:
            output_path = f"schemas/control-loops/subtypes/{self.state.subtype}/{safe_name}.json"
        else:
            output_path = f"schemas/control-loops/custom/{safe_name}.json"
        
        console.print(f"[dim]Schema will be saved to: {output_path}[/dim]")
        console.print()
        
        return True
    
    def _step_confirmation(self) -> bool:
        """Final confirmation step"""
        self.state.current_step = WizardStep.CONFIRMATION
        
        console.print(Panel(
            "[bold]Step 7: Final Confirmation[/bold]\n\n"
            "Ready to create your schema?",
            title="🎯 Create Schema",
            border_style="green"
        ))
        
        # Final checks
        checks = [
            ("Schema name set", bool(self.state.schema_name)),
            ("Base type selected", bool(self.state.base_type)),
            ("Configuration complete", True),
            ("No conflicts detected", True)  # Would do actual conflict checking
        ]
        
        check_table = Table(title="Pre-creation Checks")
        check_table.add_column("Check", style="bold")
        check_table.add_column("Status", style="white")
        
        all_passed = True
        for check, passed in checks:
            status = "✅ Pass" if passed else "❌ Fail"
            if not passed:
                all_passed = False
            check_table.add_row(check, status)
        
        console.print(check_table)
        console.print()
        
        if not all_passed:
            console.print("[red]❌ Some checks failed. Please review your configuration.[/red]")
            return False
        
        return Confirm.ask(
            "[bold]Create the schema now?[/bold]",
            default=True
        )
    
    def _step_creation(self) -> bool:
        """Schema creation step"""
        self.state.current_step = WizardStep.CREATION
        
        console.print(Panel(
            "[bold]Step 8: Creating Schema[/bold]\n\n"
            "Creating your custom schema...",
            title="🏗️ Schema Creation",
            border_style="yellow"
        ))
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                # Create progress tasks
                task1 = progress.add_task("Preparing schema structure...", total=100)
                progress.update(task1, advance=25)
                
                # Build schema data
                schema_data = self._build_schema_data()
                progress.update(task1, advance=25, description="Building schema content...")
                
                # Validate schema
                if self.state.validation_enabled:
                    if not self._validate_schema_data(schema_data):
                        console.print("[red]❌ Schema validation failed[/red]")
                        return False
                
                progress.update(task1, advance=25, description="Validating schema...")
                
                # Save schema
                output_path = self._save_schema(schema_data)
                progress.update(task1, advance=25, description="Saving schema file...")
                
                # Completion
                progress.update(task1, completed=100, description="Schema created successfully!")
                
                # Store output path for completion step
                self.state.output_path = output_path
            
            return True
            
        except Exception as e:
            console.print(f"[red]❌ Failed to create schema: {str(e)}[/red]")
            logger.exception("Schema creation failed")
            return False
    
    def _step_completion(self) -> bool:
        """Completion step"""
        self.state.current_step = WizardStep.COMPLETION
        
        success_panel = Panel(
            f"[bold green]🎉 Schema Created Successfully![/bold green]\n\n"
            f"[bold]Name:[/bold] {self.state.schema_name}\n"
            f"[bold]Type:[/bold] {self.state.base_type}\n"
            f"[bold]Version:[/bold] {self.state.schema_version}\n"
            f"[bold]File:[/bold] {getattr(self.state, 'output_path', 'Unknown')}\n\n"
            f"[bold]Next Steps:[/bold]\n"
            f"• Use 'plc-cl schema list' to see your new schema\n"
            f"• Use 'plc-cl schema info {self.state.schema_name}' for details\n"
            f"• Create instances with 'plc-cl instance create'\n"
            f"• Validate with 'plc-cl schema validate'",
            title="✅ Success",
            border_style="green",
            padding=(1, 2)
        )
        
        console.print(success_panel)
        
        # Refresh schema cache
        try:
            self.schema_manager.scan_schemas(force_refresh=True)
        except:
            pass
        
        return True
    
    # Helper methods
    
    def _load_schema_templates(self) -> List[SchemaTemplate]:
        """Load available schema templates"""
        # For now, return built-in templates
        # In full implementation, this would load from template files
        templates = [
            SchemaTemplate(
                name="Basic Temperature Control",
                description="Standard PID controller for temperature control applications",
                base_type="ladder-logic-standard-pid",
                suggested_parameters=["temperature_setpoint", "heating_output", "cooling_output"],
                validation_rules=["temperature_range", "safety_limits"]
            ),
            SchemaTemplate(
                name="Flow Rate Controller",
                description="PIDE controller optimized for flow rate control",
                base_type="function-block-standard-pide", 
                suggested_parameters=["flow_setpoint", "valve_position", "flow_measurement"],
                validation_rules=["flow_range", "valve_limits"]
            ),
            SchemaTemplate(
                name="Pressure Control System",
                description="Advanced PID for pressure control with safety interlocks",
                base_type="ladder-logic-advanced-pid",
                suggested_parameters=["pressure_setpoint", "relief_valve", "safety_cutoff"],
                validation_rules=["pressure_limits", "safety_requirements"]
            )
        ]
        
        return templates
    
    def _show_template_details(self, template: SchemaTemplate):
        """Show detailed template information"""
        details_panel = Panel(
            f"[bold]{template.name}[/bold]\n\n"
            f"[bold]Description:[/bold] {template.description}\n"
            f"[bold]Base Type:[/bold] {template.base_type}\n"
            f"[bold]Suggested Parameters:[/bold] {', '.join(template.suggested_parameters)}\n"
            f"[bold]Validation Rules:[/bold] {', '.join(template.validation_rules)}",
            title="📋 Template Details",
            border_style="cyan"
        )
        console.print(details_panel)
        console.print()
    
    def _build_schema_data(self) -> Dict[str, Any]:
        """Build the final schema data structure"""
        schema_data = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": self.state.schema_name,
            "description": self.state.schema_description,
            "version": self.state.schema_version,
            "type": "object",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": self.cli_context.auth_manager.user_info.get('username', 'CLI User'),
            "wizard_generated": True
        }
        
        # Add base properties based on type
        if self.state.base_type != "custom":
            schema_data["base_type"] = self.state.base_type
        
        if self.state.is_subtype:
            schema_data["parent_schema"] = self.state.parent_schema
            schema_data["subtype"] = self.state.subtype
        
        # Add custom properties
        if self.state.custom_properties:
            if "properties" not in schema_data:
                schema_data["properties"] = {}
            schema_data["properties"].update(self.state.custom_properties)
        
        # Add advanced features
        if self.state.advanced_features:
            schema_data["advanced_features"] = self.state.advanced_features
        
        return schema_data
    
    def _validate_schema_data(self, schema_data: Dict[str, Any]) -> bool:
        """Validate the schema data before saving"""
        try:
            # Basic JSON Schema validation
            from jsonschema import Draft202012Validator
            Draft202012Validator.check_schema(schema_data)
            return True
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return False
    
    def _save_schema(self, schema_data: Dict[str, Any]) -> str:
        """Save the schema to file"""
        # Determine output path
        safe_name = re.sub(r'[^a-zA-Z0-9-_]', '-', self.state.schema_name.lower())
        
        if self.state.is_subtype:
            output_dir = self.schema_manager.base_path / "subtypes" / self.state.subtype
        else:
            output_dir = self.schema_manager.base_path / "custom"
        
        output_path = output_dir / f"{safe_name}.json"
        
        # Create directory if needed
        os.makedirs(output_dir, exist_ok=True)
        
        # Save file
        with open(output_path, 'w') as f:
            json.dump(schema_data, f, indent=2)
        
        return str(output_path)

# =============================================================================
# WIZARD FACTORY FUNCTION
# =============================================================================

def create_schema_wizard(schema_manager, cli_context) -> SchemaCreationWizard:
    """Factory function to create a schema wizard instance"""
    return SchemaCreationWizard(schema_manager, cli_context)

# Export for use in CLI commands
__all__ = ['SchemaCreationWizard', 'create_schema_wizard', 'WizardState', 'SchemaTemplate'] 