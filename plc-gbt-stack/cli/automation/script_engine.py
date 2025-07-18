#!/usr/bin/env python3
"""
🖥️ Phase 21.4: Automation Support & Scripting Engine

Comprehensive automation framework for CLI scripting, CI/CD integration, command recording,
workflow automation, and batch processing. Enables enterprise-grade automation of control
loop management operations with error handling and recovery.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (500-700 lines, automation framework)
Context Management: Script execution with state management and error recovery
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.4 Objectives:
- Command recording and playback system
- Script creation, editing, and execution
- CI/CD pipeline integration capabilities
- Workflow automation with conditions and loops
- API client generation for integration

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.4.4 - Automation Support
Dependencies: Phase 21.1/21.2/21.3 (CLI Framework), subprocess, jinja2
"""

import os
import sys
import json
import yaml
import subprocess
import shlex
import tempfile
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable, Iterator
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import traceback

# Third-party imports
try:
    import jinja2
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich import print as rprint

# Project imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Set up console and logging
console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# AUTOMATION ENUMS AND DATA STRUCTURES
# =============================================================================

class ScriptStatus(Enum):
    """Script execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class CommandType(Enum):
    """Types of commands in scripts"""
    CLI_COMMAND = "cli_command"
    SHELL_COMMAND = "shell_command"
    CONDITION = "condition"
    LOOP = "loop"
    WAIT = "wait"
    VARIABLE = "variable"
    API_CALL = "api_call"

class TriggerType(Enum):
    """Script trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    FILE_CHANGE = "file_change"

@dataclass
class ScriptCommand:
    """Individual command in a script"""
    id: str
    command_type: CommandType
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    timeout: int = 300  # 5 minutes default
    retry_count: int = 0
    continue_on_error: bool = True
    description: str = ""

@dataclass
class ScriptExecution:
    """Script execution instance"""
    execution_id: str
    script_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: ScriptStatus = ScriptStatus.PENDING
    commands_executed: int = 0
    commands_total: int = 0
    current_command: Optional[str] = None
    output_log: List[str] = field(default_factory=list)
    error_log: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    return_code: int = 0

@dataclass
class AutomationScript:
    """Automation script definition"""
    name: str
    description: str
    author: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    commands: List[ScriptCommand] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    permissions: List[str] = field(default_factory=list)

# =============================================================================
# COMMAND RECORDER
# =============================================================================

class CommandRecorder:
    """Records CLI commands for script creation"""
    
    def __init__(self):
        self.recording = False
        self.recorded_commands = []
        self.current_session = None
        self.start_time = None
        
    def start_recording(self, session_name: str = None) -> str:
        """Start recording commands"""
        if self.recording:
            raise RuntimeError("Already recording")
        
        self.current_session = session_name or f"session_{int(time.time())}"
        self.recorded_commands = []
        self.recording = True
        self.start_time = datetime.now()
        
        console.print(f"🔴 Started recording session: [cyan]{self.current_session}[/cyan]")
        console.print("[dim]All CLI commands will be recorded. Use 'script stop' to finish.[/dim]")
        
        return self.current_session
    
    def stop_recording(self) -> AutomationScript:
        """Stop recording and return script"""
        if not self.recording:
            raise RuntimeError("Not currently recording")
        
        self.recording = False
        duration = datetime.now() - self.start_time
        
        # Create automation script
        script = AutomationScript(
            name=self.current_session,
            description=f"Recorded session from {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            author="Command Recorder",
            commands=self.recorded_commands.copy()
        )
        
        console.print(f"⏹️ Stopped recording session: [cyan]{self.current_session}[/cyan]")
        console.print(f"📝 Recorded {len(self.recorded_commands)} commands in {duration}")
        
        return script
    
    def record_command(self, command: str, parameters: Dict[str, Any] = None):
        """Record a command during recording session"""
        if not self.recording:
            return
        
        command_obj = ScriptCommand(
            id=str(uuid.uuid4()),
            command_type=CommandType.CLI_COMMAND,
            command=command,
            parameters=parameters or {},
            description=f"Recorded command: {command}"
        )
        
        self.recorded_commands.append(command_obj)
        console.print(f"📝 Recorded: [yellow]{command}[/yellow]")

# =============================================================================
# SCRIPT ENGINE
# =============================================================================

class ScriptEngine:
    """Core script execution engine"""
    
    def __init__(self, scripts_dir: Path = None):
        self.scripts_dir = scripts_dir or Path.home() / ".plc-cl" / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        
        # Execution tracking
        self.active_executions: Dict[str, ScriptExecution] = {}
        self.execution_history: List[ScriptExecution] = []
        
        # Templates
        self.template_env = self._setup_templates() if JINJA2_AVAILABLE else None
        
        # Command recorder
        self.recorder = CommandRecorder()
        
    def _setup_templates(self):
        """Setup Jinja2 template environment"""
        template_dir = Path(__file__).parent / "templates"
        if template_dir.exists():
            return jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
        return jinja2.Environment(loader=jinja2.DictLoader({}))
    
    def save_script(self, script: AutomationScript) -> bool:
        """Save script to file"""
        try:
            script_file = self.scripts_dir / f"{script.name}.json"
            script_data = asdict(script)
            
            # Convert datetime objects to strings
            script_data['created_at'] = script.created_at.isoformat()
            
            with open(script_file, 'w') as f:
                json.dump(script_data, f, indent=2)
            
            console.print(f"💾 Script saved: [cyan]{script_file}[/cyan]")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save script {script.name}: {e}")
            console.print(f"❌ Failed to save script: {e}")
            return False
    
    def load_script(self, script_name: str) -> Optional[AutomationScript]:
        """Load script from file"""
        try:
            script_file = self.scripts_dir / f"{script_name}.json"
            if not script_file.exists():
                return None
            
            with open(script_file, 'r') as f:
                script_data = json.load(f)
            
            # Convert string datetime back to datetime object
            if 'created_at' in script_data:
                script_data['created_at'] = datetime.fromisoformat(script_data['created_at'])
            
            # Convert command dictionaries back to ScriptCommand objects
            commands = []
            for cmd_data in script_data.get('commands', []):
                commands.append(ScriptCommand(**cmd_data))
            script_data['commands'] = commands
            
            return AutomationScript(**script_data)
            
        except Exception as e:
            logger.error(f"Failed to load script {script_name}: {e}")
            return None
    
    def list_scripts(self) -> List[str]:
        """List available scripts"""
        scripts = []
        for script_file in self.scripts_dir.glob("*.json"):
            scripts.append(script_file.stem)
        return sorted(scripts)
    
    def execute_script(self, script_name: str, variables: Dict[str, Any] = None) -> str:
        """Execute a script and return execution ID"""
        script = self.load_script(script_name)
        if not script:
            raise ValueError(f"Script not found: {script_name}")
        
        # Create execution instance
        execution = ScriptExecution(
            execution_id=str(uuid.uuid4()),
            script_name=script_name,
            start_time=datetime.now(),
            commands_total=len(script.commands),
            variables={**script.variables, **(variables or {})}
        )
        
        self.active_executions[execution.execution_id] = execution
        
        # Start execution in background
        asyncio.create_task(self._execute_script_async(script, execution))
        
        return execution.execution_id
    
    async def _execute_script_async(self, script: AutomationScript, execution: ScriptExecution):
        """Execute script asynchronously"""
        try:
            execution.status = ScriptStatus.RUNNING
            
            for i, command in enumerate(script.commands):
                if execution.status == ScriptStatus.CANCELLED:
                    break
                
                execution.current_command = command.command
                execution.commands_executed = i
                
                # Execute command
                await self._execute_command(command, execution)
                
                if not command.continue_on_error and execution.return_code != 0:
                    execution.status = ScriptStatus.FAILED
                    break
            
            if execution.status == ScriptStatus.RUNNING:
                execution.status = ScriptStatus.COMPLETED
            
        except Exception as e:
            execution.status = ScriptStatus.FAILED
            execution.error_log.append(f"Script execution error: {str(e)}")
            logger.error(f"Script execution failed: {e}")
        
        finally:
            execution.end_time = datetime.now()
            execution.commands_executed = len(script.commands)
            
            # Move to history
            self.execution_history.append(execution)
            if execution.execution_id in self.active_executions:
                del self.active_executions[execution.execution_id]
    
    async def _execute_command(self, command: ScriptCommand, execution: ScriptExecution):
        """Execute a single command"""
        try:
            if command.command_type == CommandType.CLI_COMMAND:
                await self._execute_cli_command(command, execution)
            elif command.command_type == CommandType.SHELL_COMMAND:
                await self._execute_shell_command(command, execution)
            elif command.command_type == CommandType.WAIT:
                await self._execute_wait_command(command, execution)
            elif command.command_type == CommandType.VARIABLE:
                await self._execute_variable_command(command, execution)
            else:
                execution.output_log.append(f"Unknown command type: {command.command_type}")
                execution.return_code = 1
                
        except Exception as e:
            execution.error_log.append(f"Command execution error: {str(e)}")
            execution.return_code = 1
    
    async def _execute_cli_command(self, command: ScriptCommand, execution: ScriptExecution):
        """Execute CLI command"""
        try:
            # Substitute variables in command
            cmd_str = self._substitute_variables(command.command, execution.variables)
            
            # Parse command
            cmd_parts = shlex.split(cmd_str)
            
            # Execute using subprocess
            proc = await asyncio.create_subprocess_exec(
                *cmd_parts,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=command.timeout
            )
            
            stdout, stderr = await proc.communicate()
            
            execution.return_code = proc.returncode
            if stdout:
                execution.output_log.append(stdout.decode())
            if stderr:
                execution.error_log.append(stderr.decode())
                
        except asyncio.TimeoutError:
            execution.error_log.append(f"Command timeout after {command.timeout}s")
            execution.return_code = 1
        except Exception as e:
            execution.error_log.append(f"CLI command error: {str(e)}")
            execution.return_code = 1
    
    async def _execute_shell_command(self, command: ScriptCommand, execution: ScriptExecution):
        """Execute shell command"""
        try:
            cmd_str = self._substitute_variables(command.command, execution.variables)
            
            proc = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                timeout=command.timeout
            )
            
            stdout, stderr = await proc.communicate()
            
            execution.return_code = proc.returncode
            if stdout:
                execution.output_log.append(stdout.decode())
            if stderr:
                execution.error_log.append(stderr.decode())
                
        except Exception as e:
            execution.error_log.append(f"Shell command error: {str(e)}")
            execution.return_code = 1
    
    async def _execute_wait_command(self, command: ScriptCommand, execution: ScriptExecution):
        """Execute wait command"""
        try:
            wait_time = command.parameters.get('seconds', 1)
            execution.output_log.append(f"Waiting {wait_time} seconds...")
            await asyncio.sleep(wait_time)
            execution.return_code = 0
        except Exception as e:
            execution.error_log.append(f"Wait command error: {str(e)}")
            execution.return_code = 1
    
    async def _execute_variable_command(self, command: ScriptCommand, execution: ScriptExecution):
        """Execute variable assignment command"""
        try:
            var_name = command.parameters.get('name')
            var_value = command.parameters.get('value')
            
            if var_name:
                execution.variables[var_name] = self._substitute_variables(str(var_value), execution.variables)
                execution.output_log.append(f"Set variable {var_name} = {execution.variables[var_name]}")
                execution.return_code = 0
            else:
                execution.error_log.append("Variable command missing name parameter")
                execution.return_code = 1
                
        except Exception as e:
            execution.error_log.append(f"Variable command error: {str(e)}")
            execution.return_code = 1
    
    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Substitute variables in text"""
        if not JINJA2_AVAILABLE:
            # Basic substitution
            for name, value in variables.items():
                text = text.replace(f"{{{{{name}}}}}", str(value))
            return text
        
        try:
            template = jinja2.Template(text)
            return template.render(**variables)
        except Exception as e:
            logger.warning(f"Template substitution failed: {e}")
            return text
    
    def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        if execution_id in self.active_executions:
            self.active_executions[execution_id].status = ScriptStatus.CANCELLED
            return True
        return False
    
    def get_execution_status(self, execution_id: str) -> Optional[ScriptExecution]:
        """Get execution status"""
        if execution_id in self.active_executions:
            return self.active_executions[execution_id]
        
        # Check history
        for execution in self.execution_history:
            if execution.execution_id == execution_id:
                return execution
        
        return None

# =============================================================================
# CI/CD INTEGRATION
# =============================================================================

class CICDIntegration:
    """CI/CD pipeline integration utilities"""
    
    def __init__(self, script_engine: ScriptEngine):
        self.script_engine = script_engine
        self.templates_dir = Path(__file__).parent / "cicd_templates"
    
    def generate_github_workflow(self, script_name: str, triggers: List[str] = None) -> str:
        """Generate GitHub Actions workflow"""
        triggers = triggers or ["push", "pull_request"]
        
        workflow = f'''name: PLC Control Loop Automation

on:
  {chr(10).join([f"{trigger}:" for trigger in triggers])}

jobs:
  plc-automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install PLC-CL CLI
      run: |
        pip install -r requirements.txt
        # Install plc-cl CLI
    
    - name: Execute automation script
      run: |
        plc-cl script play {script_name}
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: automation-results
        path: results/
'''
        return workflow
    
    def generate_gitlab_pipeline(self, script_name: str) -> str:
        """Generate GitLab CI pipeline"""
        pipeline = f'''stages:
  - automation

plc-automation:
  stage: automation
  image: python:3.9
  script:
    - pip install -r requirements.txt
    - plc-cl script play {script_name}
  artifacts:
    paths:
      - results/
    when: always
  only:
    - main
    - develop
'''
        return pipeline
    
    def generate_jenkins_pipeline(self, script_name: str) -> str:
        """Generate Jenkins pipeline"""
        pipeline = f'''pipeline {{
    agent any
    
    stages {{
        stage('Setup') {{
            steps {{
                sh 'pip install -r requirements.txt'
            }}
        }}
        
        stage('Execute Automation') {{
            steps {{
                sh 'plc-cl script play {script_name}'
            }}
        }}
    }}
    
    post {{
        always {{
            archiveArtifacts artifacts: 'results/*', allowEmptyArchive: true
        }}
    }}
}}'''
        return pipeline

# Global instances
script_engine = ScriptEngine()
cicd_integration = CICDIntegration(script_engine)

# =============================================================================
# CLI COMMANDS
# =============================================================================

@click.group()
@click.pass_context
def automation_commands(ctx):
    """Automation and scripting commands"""
    pass

@automation_commands.group()
@click.pass_context
def script(ctx):
    """Script management commands"""
    pass

@script.command('record')
@click.option('--name', help='Recording session name')
def script_record(name):
    """Start recording CLI commands"""
    try:
        session_name = script_engine.recorder.start_recording(name)
        console.print(f"✅ Recording started: {session_name}")
    except Exception as e:
        console.print(f"❌ Failed to start recording: {e}")

@script.command('stop')
@click.option('--save-as', help='Save script with specific name')
def script_stop(save_as):
    """Stop recording and save script"""
    try:
        if not script_engine.recorder.recording:
            console.print("❌ No active recording session")
            return
        
        script_obj = script_engine.recorder.stop_recording()
        
        if save_as:
            script_obj.name = save_as
        
        if script_engine.save_script(script_obj):
            console.print(f"✅ Script saved as: {script_obj.name}")
        else:
            console.print("❌ Failed to save script")
            
    except Exception as e:
        console.print(f"❌ Failed to stop recording: {e}")

@script.command('list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
def script_list(format):
    """List available scripts"""
    scripts = script_engine.list_scripts()
    
    if format == 'json':
        console.print(json.dumps(scripts, indent=2))
    else:
        table = Table(title="Available Scripts")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Commands", style="yellow")
        
        for script_name in scripts:
            script_obj = script_engine.load_script(script_name)
            if script_obj:
                table.add_row(
                    script_name,
                    script_obj.description[:50] + ("..." if len(script_obj.description) > 50 else ""),
                    str(len(script_obj.commands))
                )
        
        console.print(table)

@script.command('info')
@click.argument('script_name')
def script_info(script_name):
    """Show script information"""
    script_obj = script_engine.load_script(script_name)
    if not script_obj:
        console.print(f"❌ Script not found: {script_name}")
        return
    
    info_text = f"""
[bold cyan]{script_obj.name}[/bold cyan] v{script_obj.version}

[bold]Description:[/bold] {script_obj.description}
[bold]Author:[/bold] {script_obj.author}
[bold]Created:[/bold] {script_obj.created_at.strftime('%Y-%m-%d %H:%M:%S')}
[bold]Commands:[/bold] {len(script_obj.commands)}
"""
    
    if script_obj.variables:
        info_text += f"[bold]Variables:[/bold] {', '.join(script_obj.variables.keys())}\n"
    
    if script_obj.tags:
        info_text += f"[bold]Tags:[/bold] {', '.join(script_obj.tags)}\n"
    
    console.print(Panel(info_text, border_style="blue"))
    
    # Show commands
    if script_obj.commands:
        table = Table(title="Script Commands")
        table.add_column("#", style="cyan")
        table.add_column("Type", style="magenta")
        table.add_column("Command", style="green")
        table.add_column("Description", style="yellow")
        
        for i, cmd in enumerate(script_obj.commands, 1):
            table.add_row(
                str(i),
                cmd.command_type.value,
                cmd.command[:50] + ("..." if len(cmd.command) > 50 else ""),
                cmd.description[:30] + ("..." if len(cmd.description) > 30 else "")
            )
        
        console.print(table)

@script.command('play')
@click.argument('script_name')
@click.option('--var', 'variables', multiple=True, help='Script variables (name=value)')
@click.option('--async', 'async_exec', is_flag=True, help='Execute asynchronously')
def script_play(script_name, variables, async_exec):
    """Execute a script"""
    try:
        # Parse variables
        script_vars = {}
        for var in variables:
            if '=' in var:
                name, value = var.split('=', 1)
                script_vars[name] = value
        
        execution_id = script_engine.execute_script(script_name, script_vars)
        console.print(f"🚀 Script execution started: [cyan]{execution_id}[/cyan]")
        
        if not async_exec:
            # Wait for completion and show results
            while True:
                execution = script_engine.get_execution_status(execution_id)
                if execution and execution.status not in [ScriptStatus.RUNNING, ScriptStatus.PENDING]:
                    break
                time.sleep(1)
            
            # Show results
            if execution:
                if execution.status == ScriptStatus.COMPLETED:
                    console.print("✅ Script completed successfully")
                else:
                    console.print(f"❌ Script failed with status: {execution.status.value}")
                
                if execution.output_log:
                    console.print("\n[bold]Output:[/bold]")
                    for line in execution.output_log[-10:]:  # Last 10 lines
                        console.print(line)
                
                if execution.error_log:
                    console.print("\n[bold red]Errors:[/bold red]")
                    for line in execution.error_log[-5:]:  # Last 5 errors
                        console.print(f"[red]{line}[/red]")
        
    except Exception as e:
        console.print(f"❌ Failed to execute script: {e}")

@script.command('status')
@click.argument('execution_id', required=False)
def script_status(execution_id):
    """Show script execution status"""
    if execution_id:
        execution = script_engine.get_execution_status(execution_id)
        if not execution:
            console.print(f"❌ Execution not found: {execution_id}")
            return
        
        # Show detailed status
        status_info = f"""
[bold cyan]Execution Status[/bold cyan]

[bold]ID:[/bold] {execution.execution_id}
[bold]Script:[/bold] {execution.script_name}
[bold]Status:[/bold] {execution.status.value}
[bold]Progress:[/bold] {execution.commands_executed}/{execution.commands_total}
[bold]Started:[/bold] {execution.start_time.strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        if execution.end_time:
            duration = execution.end_time - execution.start_time
            status_info += f"[bold]Duration:[/bold] {duration}\n"
        
        if execution.current_command:
            status_info += f"[bold]Current Command:[/bold] {execution.current_command}\n"
        
        console.print(Panel(status_info, border_style="blue"))
        
    else:
        # Show all active executions
        active = list(script_engine.active_executions.values())
        recent_history = script_engine.execution_history[-10:]
        
        if active:
            table = Table(title="Active Executions")
            table.add_column("ID", style="cyan")
            table.add_column("Script", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Progress", style="yellow")
            
            for execution in active:
                table.add_row(
                    execution.execution_id[:8] + "...",
                    execution.script_name,
                    execution.status.value,
                    f"{execution.commands_executed}/{execution.commands_total}"
                )
            
            console.print(table)
        
        if recent_history:
            table = Table(title="Recent Executions")
            table.add_column("ID", style="cyan")
            table.add_column("Script", style="magenta") 
            table.add_column("Status", style="green")
            table.add_column("Duration", style="yellow")
            
            for execution in recent_history:
                duration = ""
                if execution.end_time:
                    duration = str(execution.end_time - execution.start_time)
                
                table.add_row(
                    execution.execution_id[:8] + "...",
                    execution.script_name,
                    execution.status.value,
                    duration
                )
            
            console.print(table)

@automation_commands.group()
@click.pass_context
def cicd(ctx):
    """CI/CD integration commands"""
    pass

@cicd.command('generate')
@click.argument('platform', type=click.Choice(['github', 'gitlab', 'jenkins']))
@click.argument('script_name')
@click.option('--output', type=click.Path(), help='Output file path')
def cicd_generate(platform, script_name, output):
    """Generate CI/CD pipeline configuration"""
    try:
        if platform == 'github':
            content = cicd_integration.generate_github_workflow(script_name)
            default_file = '.github/workflows/plc-automation.yml'
        elif platform == 'gitlab':
            content = cicd_integration.generate_gitlab_pipeline(script_name)
            default_file = '.gitlab-ci.yml'
        elif platform == 'jenkins':
            content = cicd_integration.generate_jenkins_pipeline(script_name)
            default_file = 'Jenkinsfile'
        
        output_file = Path(output) if output else Path(default_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        output_file.write_text(content)
        console.print(f"✅ {platform.title()} pipeline generated: [cyan]{output_file}[/cyan]")
        
    except Exception as e:
        console.print(f"❌ Failed to generate pipeline: {e}")

# Register commands with main CLI
def register_automation_commands(main_cli):
    """Register automation commands with main CLI"""
    main_cli.add_command(automation_commands, name='automation')

# For standalone testing
if __name__ == "__main__":
    automation_commands() 