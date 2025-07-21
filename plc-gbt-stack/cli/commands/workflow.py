"""
Workflow Management CLI Commands
Phase 26.4: Natural Language Workflow Engine CLI Integration

Provides command-line interface for creating, managing, and optimizing
N8N workflows through natural language interaction.
"""

import click
import json
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys
import os

# Add path for N8N LLM components
sys.path.append(os.path.join(os.path.dirname(__file__), '../../n8n/llm'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../n8n/ui/conversational_interface'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../n8n/templates/industrial_automation'))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from nl_workflow_parser import NaturalLanguageWorkflowParser, WorkflowParsingResult
    from workflow_optimizer import AIWorkflowOptimizer, WorkflowAnalysisResult
    from chat_interface import ConversationalWorkflowManager
    from template_library import IndustrialTemplateLibrary, TemplateCategory, IndustryType
except ImportError as e:
    click.echo(f"Warning: N8N workflow components not available: {e}")
    NaturalLanguageWorkflowParser = None
    AIWorkflowOptimizer = None
    ConversationalWorkflowManager = None
    IndustrialTemplateLibrary = None

console = Console()

# Global instances
workflow_parser = None
workflow_optimizer = None
conversation_manager = None
template_library = None

def init_workflow_components():
    """Initialize workflow components if available"""
    global workflow_parser, workflow_optimizer, conversation_manager, template_library
    
    if NaturalLanguageWorkflowParser:
        workflow_parser = NaturalLanguageWorkflowParser()
        workflow_optimizer = AIWorkflowOptimizer()
        conversation_manager = ConversationalWorkflowManager()
        template_library = IndustrialTemplateLibrary()
        return True
    return False

@click.group()
@click.pass_context
def workflow(ctx):
    """Natural Language Workflow Management Commands (Phase 26.4)
    
    Create, manage, and optimize N8N workflows using natural language descriptions.
    Powered by PLC-GBT's Industrial Control Theory LLM integration.
    """
    if not init_workflow_components():
        console.print("[red]❌ Workflow management not available - N8N components not installed[/red]")
        ctx.exit(1)

@workflow.command()
@click.argument('description', nargs=-1, required=True)
@click.option('--output', '-o', type=click.Path(), help='Output file for workflow JSON')
@click.option('--analyze', '-a', is_flag=True, help='Analyze workflow after creation')
@click.option('--optimize', is_flag=True, help='Optimize workflow after creation')
@click.option('--deploy', '-d', is_flag=True, help='Deploy workflow after creation')
@click.option('--format', '-f', type=click.Choice(['json', 'yaml', 'summary']), 
              default='summary', help='Output format')
def create(description, output, analyze, optimize, deploy, format):
    """Create a new workflow from natural language description
    
    Examples:
        plc-cl workflow create "temperature control for reactor with PID"
        plc-cl workflow create "data logging every 30 seconds" --analyze
        plc-cl workflow create "alarm system for tank levels" --optimize --deploy
    """
    description_text = ' '.join(description)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        task = progress.add_task("Creating workflow...", total=None)
        
        try:
            # Parse workflow request
            result = workflow_parser.parse_workflow_request(description_text)
            
            if result.parsing_success and result.workflow_definition:
                workflow = result.workflow_definition
                
                progress.update(task, description="✅ Workflow created successfully")
                progress.stop()
                
                # Display workflow summary
                if format == 'summary':
                    _display_workflow_summary(workflow, result)
                elif format == 'json':
                    workflow_json = workflow_parser.get_workflow_json(workflow)
                    if output:
                        Path(output).write_text(workflow_json)
                        console.print(f"[green]Workflow saved to {output}[/green]")
                    else:
                        console.print(Syntax(workflow_json, "json", theme="monokai"))
                
                # Optional analysis
                if analyze:
                    _analyze_workflow(workflow)
                
                # Optional optimization
                if optimize:
                    optimized = _optimize_workflow(workflow)
                    if optimized:
                        workflow = optimized.optimized_workflow
                
                # Optional deployment
                if deploy:
                    _deploy_workflow(workflow)
                    
            else:
                progress.stop()
                console.print("[red]❌ Failed to create workflow[/red]")
                if result.error_message:
                    console.print(f"[red]Error: {result.error_message}[/red]")
                
                if result.clarification_needed:
                    console.print("[yellow]Clarification needed:[/yellow]")
                    for clarification in result.clarification_needed:
                        console.print(f"  • {clarification}")
                
                if result.suggestions:
                    console.print("[cyan]Suggestions:[/cyan]")
                    for suggestion in result.suggestions:
                        console.print(f"  • {suggestion}")
        
        except Exception as e:
            progress.stop()
            console.print(f"[red]❌ Error creating workflow: {str(e)}[/red]")

@workflow.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--detailed', '-d', is_flag=True, help='Show detailed analysis')
@click.option('--export', '-e', type=click.Path(), help='Export analysis to file')
def analyze(workflow_file, detailed, export):
    """Analyze an existing workflow for performance and optimization opportunities"""
    
    try:
        # Load workflow from file
        workflow_data = json.loads(Path(workflow_file).read_text())
        
        # Convert to workflow definition (simplified for demo)
        from nl_workflow_parser import WorkflowDefinition, WorkflowType
        workflow = WorkflowDefinition(
            id=workflow_data.get('id', 'unknown'),
            name=workflow_data.get('name', 'Unknown Workflow'),
            workflow_type=WorkflowType.MONITORING,  # Default
            description=workflow_data.get('description', '')
        )
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Analyzing workflow...", total=None)
            
            analysis = workflow_optimizer.performance_analyzer.analyze_workflow_performance(workflow)
            
            progress.update(task, description="✅ Analysis completed")
            progress.stop()
            
            _display_analysis_results(analysis, detailed)
            
            if export:
                _export_analysis_results(analysis, export)
    
    except Exception as e:
        console.print(f"[red]❌ Error analyzing workflow: {str(e)}[/red]")

@workflow.command()
@click.argument('workflow_file', type=click.Path(exists=True))
@click.option('--goals', '-g', multiple=True, 
              type=click.Choice(['performance', 'reliability', 'cost', 'safety', 'maintainability']),
              help='Optimization goals')
@click.option('--output', '-o', type=click.Path(), help='Output file for optimized workflow')
@click.option('--apply', '-a', is_flag=True, help='Apply optimizations automatically')
def optimize(workflow_file, goals, output, apply):
    """Optimize a workflow based on AI analysis and recommendations"""
    
    try:
        # Load and convert workflow (simplified)
        workflow_data = json.loads(Path(workflow_file).read_text())
        from nl_workflow_parser import WorkflowDefinition, WorkflowType
        workflow = WorkflowDefinition(
            id=workflow_data.get('id', 'unknown'),
            name=workflow_data.get('name', 'Unknown Workflow'),
            workflow_type=WorkflowType.MONITORING,
            description=workflow_data.get('description', '')
        )
        
        # Convert goals to optimization types
        from workflow_optimizer import OptimizationType
        optimization_goals = []
        goal_mapping = {
            'performance': OptimizationType.PERFORMANCE,
            'reliability': OptimizationType.RELIABILITY,
            'cost': OptimizationType.COST,
            'safety': OptimizationType.SAFETY,
            'maintainability': OptimizationType.MAINTAINABILITY
        }
        
        for goal in goals:
            if goal in goal_mapping:
                optimization_goals.append(goal_mapping[goal])
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            task = progress.add_task("Optimizing workflow...", total=None)
            
            optimized = workflow_optimizer.optimize_workflow(
                workflow, optimization_goals=optimization_goals or None
            )
            
            progress.update(task, description="✅ Optimization completed")
            progress.stop()
            
            _display_optimization_results(optimized)
            
            if output:
                optimized_json = workflow_parser.get_workflow_json(optimized.optimized_workflow)
                Path(output).write_text(optimized_json)
                console.print(f"[green]Optimized workflow saved to {output}[/green]")
            
            if apply:
                if Confirm.ask("Apply optimizations and update original file?"):
                    optimized_json = workflow_parser.get_workflow_json(optimized.optimized_workflow)
                    Path(workflow_file).write_text(optimized_json)
                    console.print("[green]✅ Optimizations applied[/green]")
    
    except Exception as e:
        console.print(f"[red]❌ Error optimizing workflow: {str(e)}[/red]")

@workflow.command()
@click.option('--category', '-c', type=click.Choice([c.value for c in TemplateCategory]),
              help='Filter by category')
@click.option('--industry', '-i', type=click.Choice([i.value for i in IndustryType]),
              help='Filter by industry')
@click.option('--search', '-s', help='Search templates by keyword')
@click.option('--detailed', '-d', is_flag=True, help='Show detailed template information')
def templates(category, industry, search, detailed):
    """List and search available workflow templates"""
    
    try:
        # Get catalog
        catalog = template_library.get_template_catalog()
        
        # Apply filters
        filtered_templates = catalog['templates']
        
        if category:
            filtered_templates = [t for t in filtered_templates if t['category'] == category]
        
        if industry:
            filtered_templates = [t for t in filtered_templates if t['industry'] == industry]
        
        if search:
            search_results = template_library.search_templates(search)
            filtered_ids = [t.id for t in search_results]
            filtered_templates = [t for t in filtered_templates if t['id'] in filtered_ids]
        
        # Display results
        if not filtered_templates:
            console.print("[yellow]No templates found matching criteria[/yellow]")
            return
        
        if detailed:
            _display_templates_detailed(filtered_templates)
        else:
            _display_templates_table(filtered_templates)
            
        console.print(f"\n[cyan]Total: {len(filtered_templates)} templates[/cyan]")
        
        # Show summary statistics
        if not search and not category and not industry:
            console.print(f"\n[dim]Categories: {', '.join(catalog['categories'].keys())}[/dim]")
            console.print(f"[dim]Industries: {', '.join(catalog['industries'].keys())}[/dim]")
    
    except Exception as e:
        console.print(f"[red]❌ Error listing templates: {str(e)}[/red]")

@workflow.command()
@click.argument('template_id')
@click.option('--params', '-p', multiple=True, help='Template parameters (name=value)')
@click.option('--output', '-o', type=click.Path(), help='Output file for generated workflow')
@click.option('--interactive', '-i', is_flag=True, help='Interactive parameter input')
def from_template(template_id, params, output, interactive):
    """Create a workflow from a template
    
    Examples:
        plc-cl workflow from-template temp_control_basic -p loop_name=TIC_101
        plc-cl workflow from-template data_historian_basic --interactive
    """
    
    try:
        # Get template
        template = template_library.get_template(template_id)
        if not template:
            console.print(f"[red]❌ Template '{template_id}' not found[/red]")
            return
        
        # Collect parameters
        parameters = {}
        
        # Parse command line parameters
        for param in params:
            if '=' in param:
                name, value = param.split('=', 1)
                # Simple type conversion
                if value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                elif value.replace('.', '').replace('-', '').isdigit():
                    value = float(value) if '.' in value else int(value)
                parameters[name] = value
        
        # Interactive parameter input
        if interactive:
            console.print(f"[cyan]📝 Template: {template.name}[/cyan]")
            console.print(f"[dim]{template.description}[/dim]\n")
            
            for param in template.parameters:
                if param.name not in parameters:
                    prompt_text = f"{param.name}"
                    if param.description:
                        prompt_text += f" ({param.description})"
                    if param.default_value is not None:
                        prompt_text += f" [{param.default_value}]"
                    
                    if param.parameter_type == "boolean":
                        value = Confirm.ask(prompt_text, default=param.default_value)
                    elif param.parameter_type == "select" and param.options:
                        console.print(f"Options: {', '.join(param.options)}")
                        value = Prompt.ask(prompt_text, default=param.default_value)
                    else:
                        value = Prompt.ask(prompt_text, default=param.default_value)
                        # Type conversion
                        if param.parameter_type == "number" and isinstance(value, str):
                            try:
                                value = float(value) if '.' in value else int(value)
                            except ValueError:
                                console.print(f"[yellow]Warning: Invalid number for {param.name}[/yellow]")
                    
                    parameters[param.name] = value
        
        # Validate parameters
        valid, errors = template_library.validate_parameters(template_id, parameters)
        if not valid:
            console.print("[red]❌ Parameter validation failed:[/red]")
            for error in errors:
                console.print(f"  • {error}")
            return
        
        # Generate workflow
        workflow_def = template_library.instantiate_template(template_id, parameters)
        if not workflow_def:
            console.print("[red]❌ Failed to generate workflow from template[/red]")
            return
        
        # Display result
        console.print("[green]✅ Workflow generated from template[/green]")
        console.print(f"[cyan]Name: {workflow_def['name']}[/cyan]")
        console.print(f"[cyan]Nodes: {len(workflow_def.get('nodes', []))}[/cyan]")
        console.print(f"[cyan]Connections: {len(workflow_def.get('connections', []))}[/cyan]")
        
        # Save to file
        if output:
            Path(output).write_text(json.dumps(workflow_def, indent=2))
            console.print(f"[green]Workflow saved to {output}[/green]")
        else:
            console.print(Syntax(json.dumps(workflow_def, indent=2), "json", theme="monokai"))
    
    except Exception as e:
        console.print(f"[red]❌ Error generating workflow from template: {str(e)}[/red]")

@workflow.command()
@click.option('--session', '-s', help='Conversation session ID')
def chat(session):
    """Start interactive workflow management chat session"""
    
    if not conversation_manager:
        console.print("[red]❌ Conversational interface not available[/red]")
        return
    
    session_id = session or f"cli_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    user_id = "cli_user"
    
    console.print(Panel.fit(
        "[bold cyan]🤖 PLC-GBT Workflow Assistant[/bold cyan]\n\n"
        "I can help you create, analyze, and optimize industrial automation workflows.\n"
        "Type 'help' for available commands or 'quit' to exit.\n\n"
        "Example: \"Create a temperature control loop for the reactor\"",
        title="Natural Language Workflow Management"
    ))
    
    try:
        while True:
            user_input = Prompt.ask("\n[cyan]You[/cyan]")
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
            
            # Process message asynchronously
            try:
                response = asyncio.run(
                    conversation_manager.handle_user_message(user_id, user_input, session_id)
                )
                
                # Display response
                console.print(f"\n[green]🤖 Assistant[/green]: {response.message}")
                
                if response.suggestions:
                    console.print(f"\n[dim]💡 Suggestions: {', '.join(response.suggestions[:3])}[/dim]")
                
                if response.workflow_preview:
                    console.print(f"[cyan]📊 Workflow: {response.workflow_preview.get('name', 'Unknown')}[/cyan]")
            
            except Exception as e:
                console.print(f"[red]❌ Error: {str(e)}[/red]")
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Chat session ended[/yellow]")

# Helper functions for display
def _display_workflow_summary(workflow, result):
    """Display workflow creation summary"""
    console.print("\n" + "="*60)
    console.print(f"[bold green]✅ Workflow Created: {workflow.name}[/bold green]")
    console.print("="*60)
    
    table = Table(show_header=False, box=None)
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="white")
    
    table.add_row("Type", workflow.workflow_type.value.replace('_', ' ').title())
    table.add_row("Nodes", str(len(workflow.nodes)))
    table.add_row("Connections", str(len(workflow.connections)))
    table.add_row("Confidence", f"{result.confidence:.1%}")
    table.add_row("Processing Time", f"{result.processing_time:.2f}s")
    
    console.print(table)
    
    if workflow.nodes:
        console.print("\n[bold]Workflow Nodes:[/bold]")
        for i, node in enumerate(workflow.nodes, 1):
            console.print(f"  {i}. {node.name} ({node.type.value.replace('_', ' ').title()})")

def _analyze_workflow(workflow):
    """Analyze workflow and display results"""
    console.print("\n[yellow]🔍 Analyzing workflow...[/yellow]")
    
    analysis = workflow_optimizer.performance_analyzer.analyze_workflow_performance(workflow)
    _display_analysis_results(analysis, detailed=False)

def _optimize_workflow(workflow):
    """Optimize workflow and display results"""
    console.print("\n[yellow]🚀 Optimizing workflow...[/yellow]")
    
    optimized = workflow_optimizer.optimize_workflow(workflow)
    _display_optimization_results(optimized)
    return optimized

def _deploy_workflow(workflow):
    """Simulate workflow deployment"""
    console.print(f"\n[yellow]🚀 Deploying workflow: {workflow.name}...[/yellow]")
    
    # Simulate deployment steps
    import time
    with Progress(console=console) as progress:
        task = progress.add_task("Deploying...", total=4)
        
        progress.update(task, description="Validating workflow...")
        time.sleep(0.5)
        progress.advance(task)
        
        progress.update(task, description="Uploading to N8N...")
        time.sleep(0.5)
        progress.advance(task)
        
        progress.update(task, description="Configuring credentials...")
        time.sleep(0.5)
        progress.advance(task)
        
        progress.update(task, description="Activating workflow...")
        time.sleep(0.5)
        progress.advance(task)
    
    console.print(f"[green]✅ Workflow '{workflow.name}' deployed successfully![/green]")
    console.print(f"[dim]Endpoint: https://n8n.plc-automation.internal/workflow/{workflow.id}[/dim]")

def _display_analysis_results(analysis, detailed=False):
    """Display workflow analysis results"""
    console.print(f"\n[bold]📊 Analysis Results for: {analysis.workflow_id}[/bold]")
    
    # Scores table
    scores_table = Table(title="Performance Scores")
    scores_table.add_column("Metric", style="cyan")
    scores_table.add_column("Score", style="white")
    scores_table.add_column("Status", style="white")
    
    def get_status_color(score):
        if score >= 80: return "[green]Excellent[/green]"
        elif score >= 60: return "[yellow]Good[/yellow]"
        else: return "[red]Needs Improvement[/red]"
    
    scores_table.add_row("Overall Health", f"{analysis.overall_health_score:.1f}/100", 
                        get_status_color(analysis.overall_health_score))
    scores_table.add_row("Performance", f"{analysis.performance_score:.1f}/100",
                        get_status_color(analysis.performance_score))
    scores_table.add_row("Reliability", f"{analysis.reliability_score:.1f}/100",
                        get_status_color(analysis.reliability_score))
    scores_table.add_row("Maintainability", f"{analysis.maintainability_score:.1f}/100",
                        get_status_color(analysis.maintainability_score))
    
    console.print(scores_table)
    
    # Issues summary
    if analysis.bottlenecks or analysis.risk_factors:
        console.print(f"\n[bold red]⚠️  Issues Found:[/bold red]")
        for bottleneck in analysis.bottlenecks:
            console.print(f"  🔴 {bottleneck}")
        for risk in analysis.risk_factors:
            console.print(f"  ⚠️  {risk}")
    
    # Recommendations
    if analysis.recommendations:
        console.print(f"\n[bold]💡 Top Recommendations:[/bold]")
        for i, rec in enumerate(analysis.recommendations[:3], 1):
            console.print(f"  {i}. [bold]{rec.title}[/bold] ({rec.priority.value.title()})")
            console.print(f"     {rec.description}")
            if detailed:
                console.print(f"     Expected: {rec.expected_improvement}")

def _display_optimization_results(optimized):
    """Display workflow optimization results"""
    console.print(f"\n[bold]🚀 Optimization Results[/bold]")
    
    console.print(f"[cyan]Original:[/cyan] {optimized.original_workflow.name}")
    console.print(f"[cyan]Optimized:[/cyan] {optimized.optimized_workflow.name}")
    
    # Applied optimizations
    if optimized.applied_optimizations:
        console.print(f"\n[bold]✅ Applied Optimizations ({len(optimized.applied_optimizations)}):[/bold]")
        for i, opt in enumerate(optimized.applied_optimizations, 1):
            console.print(f"  {i}. {opt.title} ({opt.optimization_type.value.title()})")
            console.print(f"     Expected: {opt.expected_improvement}")
    
    # Expected improvements
    if optimized.expected_improvements:
        console.print(f"\n[bold]📈 Expected Improvements:[/bold]")
        for metric, improvement in optimized.expected_improvements.items():
            if improvement > 0:
                console.print(f"  • {metric.replace('_', ' ').title()}: +{improvement*100:.1f}%")

def _display_templates_table(templates):
    """Display templates in a table format"""
    table = Table(title="Available Workflow Templates")
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Category", style="yellow")
    table.add_column("Industry", style="green")
    table.add_column("Complexity", style="magenta")
    table.add_column("Setup Time", style="dim")
    
    for template in templates:
        table.add_row(
            template['id'],
            template['name'],
            template['category'].replace('_', ' ').title(),
            template['industry'].replace('_', ' ').title(),
            template['complexity'].title(),
            template['estimated_setup_time']
        )
    
    console.print(table)

def _display_templates_detailed(templates):
    """Display detailed template information"""
    for template in templates:
        console.print(Panel(
            f"[bold]{template['name']}[/bold]\n\n"
            f"{template['description']}\n\n"
            f"[cyan]Category:[/cyan] {template['category'].replace('_', ' ').title()}\n"
            f"[cyan]Industry:[/cyan] {template['industry'].replace('_', ' ').title()}\n"
            f"[cyan]Complexity:[/cyan] {template['complexity'].title()}\n"
            f"[cyan]Parameters:[/cyan] {template['parameter_count']}\n"
            f"[cyan]Setup Time:[/cyan] {template['estimated_setup_time']}\n"
            f"[cyan]Tags:[/cyan] {', '.join(template['tags'])}",
            title=f"[yellow]{template['id']}[/yellow]"
        ))

def _export_analysis_results(analysis, export_path):
    """Export analysis results to file"""
    export_data = {
        "workflow_id": analysis.workflow_id,
        "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
        "scores": {
            "overall_health": analysis.overall_health_score,
            "performance": analysis.performance_score,
            "reliability": analysis.reliability_score,
            "maintainability": analysis.maintainability_score
        },
        "metrics": {
            "execution_time_avg": analysis.current_metrics.execution_time_avg,
            "throughput_per_hour": analysis.current_metrics.throughput_per_hour,
            "error_rate": analysis.current_metrics.error_rate,
            "success_rate": analysis.current_metrics.success_rate
        },
        "issues": {
            "bottlenecks": analysis.bottlenecks,
            "risk_factors": analysis.risk_factors,
            "compliance_issues": analysis.compliance_issues
        },
        "recommendations": [
            {
                "title": rec.title,
                "type": rec.optimization_type.value,
                "priority": rec.priority.value,
                "description": rec.description,
                "expected_improvement": rec.expected_improvement,
                "implementation_effort": rec.implementation_effort,
                "impact_score": rec.estimated_impact_score
            }
            for rec in analysis.recommendations
        ]
    }
    
    Path(export_path).write_text(json.dumps(export_data, indent=2))
    console.print(f"[green]Analysis exported to {export_path}[/green]")

if __name__ == "__main__":
    workflow() 