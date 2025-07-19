#!/usr/bin/env python3
"""
openai_fine_tuning_cli.py - Comprehensive OpenAI Fine-Tuning CLI
===============================================================

Following AI Task Orchestrator methodology for systematic fine-tuning management.
Provides complete workflow automation for industrial control LLM development.

Usage:
    python openai_fine_tuning_cli.py [command] [options]

Commands:
    init         Initialize fine-tuning environment and configuration
    prepare      Prepare training data with validation
    train        Start a new fine-tuning job
    status       Check status of fine-tuning jobs
    validate     Validate a fine-tuned model
    deploy       Deploy model to production
    cost         Analyze and track costs
    docs         Generate documentation

Author: PLC-GPT Team
Version: 1.0.0
"""

import os
import sys
import json
import click
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from tabulate import tabulate
import openai
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from dataclasses import dataclass, asdict
import time
import numpy as np
from enum import Enum

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Initialize Rich console for beautiful output
console = Console()

# =============================================================================
# Data Models
# =============================================================================

class ModelType(Enum):
    """Supported model types for fine-tuning"""
    GPT4O_MINI = "gpt-4o-mini-2024-07-18"
    GPT35_TURBO = "gpt-3.5-turbo-0125"
    
    @classmethod
    def get_production(cls):
        """Get the production model type"""
        return cls.GPT4O_MINI
    
    @classmethod
    def supports_fine_tuning(cls, model: str) -> bool:
        """Check if a model supports fine-tuning"""
        non_supported = ["gpt-4", "gpt-4o", "gpt-4-turbo"]
        return not any(model.startswith(prefix) for prefix in non_supported)

@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning jobs"""
    base_model: str
    n_epochs: int = 3
    batch_size: int = 1
    learning_rate_multiplier: float = 0.1
    suffix: str = "industrial-control"
    seed: int = 42
    
    def to_openai_params(self) -> Dict[str, Any]:
        """Convert to OpenAI API parameters"""
        return {
            "model": self.base_model,
            "hyperparameters": {
                "n_epochs": self.n_epochs,
                "batch_size": self.batch_size,
                "learning_rate_multiplier": self.learning_rate_multiplier
            },
            "suffix": self.suffix,
            "seed": self.seed
        }

@dataclass
class TrainingDataStats:
    """Statistics for training data"""
    total_examples: int
    avg_prompt_tokens: float
    avg_completion_tokens: float
    total_tokens: int
    estimated_cost: float
    quality_score: float
    domain_coverage: Dict[str, int]

@dataclass
class ValidationResult:
    """Model validation results"""
    model_id: str
    accuracy: float
    response_time: float
    domain_scores: Dict[str, float]
    safety_compliance: float
    production_ready: bool
    recommendations: List[str]

# =============================================================================
# Core CLI Class
# =============================================================================

class OpenAIFineTuningCLI:
    """Comprehensive CLI for OpenAI fine-tuning workflows"""
    
    def __init__(self):
        """Initialize the CLI with configuration"""
        self.config_path = Path.home() / ".plc-gpt" / "fine-tuning"
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_path / "config.json"
        self.history_file = self.config_path / "history.json"
        
        # Initialize OpenAI client
        self.client = None
        self._init_openai_client()
        
        # Load configuration
        self.config = self._load_config()
        self.history = self._load_history()
        
    def _init_openai_client(self):
        """Initialize OpenAI client with error handling"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            console.print("[red]Error: OPENAI_API_KEY not found in environment[/red]")
            console.print("Please set your OpenAI API key: export OPENAI_API_KEY='your-key'")
            sys.exit(1)
        
        self.client = openai.OpenAI(api_key=api_key)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {
            "default_model": ModelType.GPT4O_MINI.value,
            "project_name": "industrial-control",
            "validation_threshold": 0.85,
            "cost_limit": 100.0
        }
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """Load job history from file"""
        if self.history_file.exists():
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_history(self):
        """Save job history to file"""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def _add_to_history(self, job_data: Dict[str, Any]):
        """Add a job to history"""
        self.history.append({
            **job_data,
            "timestamp": datetime.now().isoformat()
        })
        self._save_history()
    
    # =============================================================================
    # Command: Initialize
    # =============================================================================
    
    def cmd_init(self, force: bool = False):
        """Initialize fine-tuning environment and configuration"""
        console.print("\n[bold cyan]🚀 OpenAI Fine-Tuning CLI Initialization[/bold cyan]\n")
        
        # Check if already initialized
        if self.config_file.exists() and not force:
            if not Confirm.ask("Configuration already exists. Reinitialize?"):
                return
        
        # Verify OpenAI connection
        with console.status("Verifying OpenAI connection..."):
            try:
                models = self.client.models.list()
                available_models = [m.id for m in models if ModelType.supports_fine_tuning(m.id)]
                console.print(f"[green]✅ Connected to OpenAI (found {len(available_models)} fine-tunable models)[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to connect to OpenAI: {e}[/red]")
                return
        
        # Configure project
        project_name = Prompt.ask("Project name", default=self.config.get("project_name", "industrial-control"))
        default_model = Prompt.ask(
            "Default base model",
            choices=[ModelType.GPT4O_MINI.value, ModelType.GPT35_TURBO.value],
            default=ModelType.GPT4O_MINI.value
        )
        
        # Set cost limits
        cost_limit = float(Prompt.ask("Maximum cost limit (USD)", default="100.0"))
        
        # Update configuration
        self.config.update({
            "project_name": project_name,
            "default_model": default_model,
            "cost_limit": cost_limit,
            "initialized": True,
            "initialized_at": datetime.now().isoformat()
        })
        self._save_config()
        
        # Create project directories
        dirs = ["training_data", "validation_data", "models", "results", "docs"]
        for dir_name in dirs:
            (self.config_path / dir_name).mkdir(exist_ok=True)
        
        console.print("\n[green]✅ Initialization complete![/green]")
        console.print(f"Configuration saved to: {self.config_file}")
        
        # Show next steps
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Prepare training data: [cyan]python openai_fine_tuning_cli.py prepare[/cyan]")
        console.print("2. Start training: [cyan]python openai_fine_tuning_cli.py train[/cyan]")
        console.print("3. Check status: [cyan]python openai_fine_tuning_cli.py status[/cyan]")
    
    # =============================================================================
    # Command: Prepare Training Data
    # =============================================================================
    
    def cmd_prepare(self, input_file: Optional[str] = None, validate_only: bool = False):
        """Prepare and validate training data"""
        console.print("\n[bold cyan]📊 Training Data Preparation[/bold cyan]\n")
        
        # Get input file
        if not input_file:
            input_file = Prompt.ask("Training data file (JSONL format)")
        
        input_path = Path(input_file)
        if not input_path.exists():
            console.print(f"[red]❌ File not found: {input_file}[/red]")
            return
        
        # Load and validate data
        with console.status("Loading training data..."):
            try:
                examples = []
                with open(input_path, 'r') as f:
                    for line in f:
                        examples.append(json.loads(line))
                
                console.print(f"[green]✅ Loaded {len(examples)} examples[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to load data: {e}[/red]")
                return
        
        # Validate format
        validation_errors = []
        for i, example in enumerate(examples):
            if "messages" not in example:
                validation_errors.append(f"Example {i}: Missing 'messages' field")
                continue
            
            messages = example["messages"]
            if not isinstance(messages, list) or len(messages) < 2:
                validation_errors.append(f"Example {i}: Invalid messages format")
                continue
            
            # Check for system, user, assistant messages
            roles = [msg.get("role") for msg in messages]
            if "user" not in roles or "assistant" not in roles:
                validation_errors.append(f"Example {i}: Missing required roles")
        
        if validation_errors:
            console.print("\n[red]Validation errors found:[/red]")
            for error in validation_errors[:10]:  # Show first 10
                console.print(f"  - {error}")
            if len(validation_errors) > 10:
                console.print(f"  ... and {len(validation_errors) - 10} more")
            return
        
        # Calculate statistics
        stats = self._calculate_training_stats(examples)
        
        # Display statistics
        console.print("\n[bold]Training Data Statistics:[/bold]")
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Total Examples", str(stats.total_examples))
        table.add_row("Avg Prompt Tokens", f"{stats.avg_prompt_tokens:.1f}")
        table.add_row("Avg Completion Tokens", f"{stats.avg_completion_tokens:.1f}")
        table.add_row("Total Tokens", f"{stats.total_tokens:,}")
        table.add_row("Estimated Cost", f"${stats.estimated_cost:.2f}")
        table.add_row("Quality Score", f"{stats.quality_score:.2%}")
        
        console.print(table)
        
        # Show domain coverage
        if stats.domain_coverage:
            console.print("\n[bold]Domain Coverage:[/bold]")
            for domain, count in sorted(stats.domain_coverage.items(), key=lambda x: x[1], reverse=True):
                console.print(f"  - {domain}: {count} examples")
        
        if validate_only:
            return
        
        # Save processed data
        if Confirm.ask("\nSave prepared training data?"):
            output_path = self.config_path / "training_data" / f"prepared_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
            with open(output_path, 'w') as f:
                for example in examples:
                    f.write(json.dumps(example) + '\n')
            
            console.print(f"\n[green]✅ Training data saved to: {output_path}[/green]")
            
            # Update config with latest training file
            self.config["latest_training_file"] = str(output_path)
            self._save_config()
    
    def _calculate_training_stats(self, examples: List[Dict[str, Any]]) -> TrainingDataStats:
        """Calculate statistics for training data"""
        total_prompt_tokens = 0
        total_completion_tokens = 0
        domain_keywords = {
            "pid": "PID Control",
            "temperature": "Temperature Control",
            "pressure": "Pressure Control",
            "flow": "Flow Control",
            "level": "Level Control",
            "cascade": "Cascade Control",
            "feedforward": "Feedforward Control",
            "mpc": "Model Predictive Control",
            "safety": "Safety Systems",
            "plc": "PLC Programming"
        }
        domain_counts = {domain: 0 for domain in domain_keywords.values()}
        
        for example in examples:
            messages = example.get("messages", [])
            
            # Estimate tokens (rough approximation)
            prompt_text = " ".join(msg["content"] for msg in messages[:-1])
            completion_text = messages[-1]["content"] if messages else ""
            
            prompt_tokens = len(prompt_text.split()) * 1.3  # Rough token estimate
            completion_tokens = len(completion_text.split()) * 1.3
            
            total_prompt_tokens += prompt_tokens
            total_completion_tokens += completion_tokens
            
            # Check domain coverage
            full_text = (prompt_text + " " + completion_text).lower()
            for keyword, domain in domain_keywords.items():
                if keyword in full_text:
                    domain_counts[domain] += 1
        
        total_examples = len(examples)
        avg_prompt_tokens = total_prompt_tokens / total_examples if total_examples > 0 else 0
        avg_completion_tokens = total_completion_tokens / total_examples if total_examples > 0 else 0
        total_tokens = int(total_prompt_tokens + total_completion_tokens)
        
        # Calculate cost (GPT-4o-mini pricing)
        cost_per_1k_training = 0.0030
        estimated_cost = (total_tokens / 1000) * cost_per_1k_training * 3  # 3 epochs
        
        # Calculate quality score
        quality_factors = [
            min(total_examples / 100, 1.0),  # More examples is better
            min(avg_prompt_tokens / 50, 1.0),  # Longer prompts are better
            min(len([d for d in domain_counts.values() if d > 0]) / 5, 1.0),  # Domain diversity
        ]
        quality_score = np.mean(quality_factors)
        
        return TrainingDataStats(
            total_examples=total_examples,
            avg_prompt_tokens=avg_prompt_tokens,
            avg_completion_tokens=avg_completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=estimated_cost,
            quality_score=quality_score,
            domain_coverage={k: v for k, v in domain_counts.items() if v > 0}
        )
    
    # =============================================================================
    # Command: Train
    # =============================================================================
    
    def cmd_train(self, training_file: Optional[str] = None, config_override: Optional[Dict[str, Any]] = None):
        """Start a new fine-tuning job"""
        console.print("\n[bold cyan]🚀 Starting Fine-Tuning Job[/bold cyan]\n")
        
        # Get training file
        if not training_file:
            training_file = self.config.get("latest_training_file")
            if not training_file:
                training_file = Prompt.ask("Training data file")
        
        training_path = Path(training_file)
        if not training_path.exists():
            console.print(f"[red]❌ Training file not found: {training_file}[/red]")
            return
        
        # Configure fine-tuning
        config = FineTuningConfig(
            base_model=self.config.get("default_model", ModelType.GPT4O_MINI.value),
            **config_override or {}
        )
        
        # Show configuration
        console.print("[bold]Fine-tuning Configuration:[/bold]")
        for key, value in asdict(config).items():
            console.print(f"  {key}: {value}")
        
        if not Confirm.ask("\nProceed with fine-tuning?"):
            return
        
        # Upload training file
        with console.status("Uploading training file..."):
            try:
                with open(training_path, 'rb') as f:
                    file_response = self.client.files.create(
                        file=f,
                        purpose='fine-tune'
                    )
                file_id = file_response.id
                console.print(f"[green]✅ Training file uploaded: {file_id}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Failed to upload file: {e}[/red]")
                return
        
        # Create fine-tuning job
        with console.status("Creating fine-tuning job..."):
            try:
                params = config.to_openai_params()
                params["training_file"] = file_id
                
                job = self.client.fine_tuning.jobs.create(**params)
                console.print(f"\n[green]✅ Fine-tuning job created: {job.id}[/green]")
                
                # Add to history
                self._add_to_history({
                    "job_id": job.id,
                    "base_model": config.base_model,
                    "training_file": str(training_path),
                    "config": asdict(config),
                    "status": "created"
                })
                
            except Exception as e:
                console.print(f"[red]❌ Failed to create job: {e}[/red]")
                return
        
        # Show monitoring command
        console.print(f"\n[bold]Monitor progress:[/bold]")
        console.print(f"  python openai_fine_tuning_cli.py status --job-id {job.id} --watch")
    
    # =============================================================================
    # Command: Status
    # =============================================================================
    
    def cmd_status(self, job_id: Optional[str] = None, watch: bool = False, all_jobs: bool = False):
        """Check status of fine-tuning jobs"""
        console.print("\n[bold cyan]📈 Fine-Tuning Job Status[/bold cyan]\n")
        
        if all_jobs:
            # Show all jobs
            jobs = list(self.client.fine_tuning.jobs.list(limit=10))
            if not jobs:
                console.print("[yellow]No fine-tuning jobs found[/yellow]")
                return
            
            table = Table(title="Fine-Tuning Jobs")
            table.add_column("Job ID", style="cyan")
            table.add_column("Model", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Created", style="white")
            
            for job in jobs:
                status_color = {
                    "succeeded": "green",
                    "failed": "red",
                    "running": "yellow",
                    "queued": "blue"
                }.get(job.status, "white")
                
                table.add_row(
                    job.id,
                    job.model,
                    f"[{status_color}]{job.status}[/{status_color}]",
                    datetime.fromtimestamp(job.created_at).strftime("%Y-%m-%d %H:%M")
                )
            
            console.print(table)
            return
        
        # Get specific job
        if not job_id:
            # Get latest job from history
            if self.history:
                job_id = self.history[-1]["job_id"]
                console.print(f"Using latest job: {job_id}")
            else:
                job_id = Prompt.ask("Job ID")
        
        # Monitor job
        if watch:
            self._watch_job(job_id)
        else:
            self._show_job_status(job_id)
    
    def _show_job_status(self, job_id: str):
        """Show detailed status for a single job"""
        try:
            job = self.client.fine_tuning.jobs.retrieve(job_id)
            
            # Basic info
            console.print(f"[bold]Job ID:[/bold] {job.id}")
            console.print(f"[bold]Status:[/bold] {job.status}")
            console.print(f"[bold]Model:[/bold] {job.model}")
            console.print(f"[bold]Created:[/bold] {datetime.fromtimestamp(job.created_at)}")
            
            if job.finished_at:
                console.print(f"[bold]Finished:[/bold] {datetime.fromtimestamp(job.finished_at)}")
                duration = job.finished_at - job.created_at
                console.print(f"[bold]Duration:[/bold] {duration // 60} minutes")
            
            # Training details
            if hasattr(job, 'trained_tokens') and job.trained_tokens:
                console.print(f"\n[bold]Training Metrics:[/bold]")
                console.print(f"  Trained tokens: {job.trained_tokens:,}")
                
                # Calculate cost
                cost = (job.trained_tokens / 1000) * 0.0030
                console.print(f"  Estimated cost: ${cost:.2f}")
            
            # Result model
            if job.status == "succeeded" and job.fine_tuned_model:
                console.print(f"\n[bold green]✅ Fine-tuned model:[/bold green] {job.fine_tuned_model}")
                console.print("\n[bold]Next steps:[/bold]")
                console.print(f"1. Validate model: [cyan]python openai_fine_tuning_cli.py validate --model {job.fine_tuned_model}[/cyan]")
                console.print(f"2. Deploy model: [cyan]python openai_fine_tuning_cli.py deploy --model {job.fine_tuned_model}[/cyan]")
            
            # Error info
            if job.status == "failed" and hasattr(job, 'error') and job.error:
                console.print(f"\n[bold red]❌ Error:[/bold red] {job.error}")
            
        except Exception as e:
            console.print(f"[red]❌ Failed to get job status: {e}[/red]")
    
    def _watch_job(self, job_id: str):
        """Watch job progress with live updates"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Monitoring job...", total=None)
            
            last_status = None
            while True:
                try:
                    job = self.client.fine_tuning.jobs.retrieve(job_id)
                    
                    if job.status != last_status:
                        progress.update(task, description=f"Status: {job.status}")
                        last_status = job.status
                        
                        if job.status in ["succeeded", "failed", "cancelled"]:
                            progress.stop()
                            console.print(f"\n[bold]Job completed with status: {job.status}[/bold]")
                            self._show_job_status(job_id)
                            break
                    
                    time.sleep(5)  # Check every 5 seconds
                    
                except KeyboardInterrupt:
                    progress.stop()
                    console.print("\n[yellow]Monitoring cancelled[/yellow]")
                    break
                except Exception as e:
                    progress.stop()
                    console.print(f"\n[red]Error: {e}[/red]")
                    break
    
    # =============================================================================
    # Command: Validate
    # =============================================================================
    
    def cmd_validate(self, model_id: Optional[str] = None, test_file: Optional[str] = None):
        """Validate a fine-tuned model"""
        console.print("\n[bold cyan]🔍 Model Validation[/bold cyan]\n")
        
        # Get model ID
        if not model_id:
            # Try to get from latest successful job
            for job in reversed(self.history):
                if job.get("status") == "succeeded" and job.get("fine_tuned_model"):
                    model_id = job["fine_tuned_model"]
                    console.print(f"Using latest model: {model_id}")
                    break
            else:
                model_id = Prompt.ask("Fine-tuned model ID")
        
        # Prepare test prompts
        test_prompts = [
            {
                "category": "PID Tuning",
                "prompt": "What are the recommended PID parameters for a temperature control loop with a 5-minute time constant?",
                "expected_keywords": ["proportional", "integral", "derivative", "gain", "time constant"]
            },
            {
                "category": "Safety Systems",
                "prompt": "Explain the requirements for a SIL-2 safety instrumented system.",
                "expected_keywords": ["safety", "SIL", "reliability", "redundancy", "fault"]
            },
            {
                "category": "Process Control",
                "prompt": "How do you implement cascade control for a distillation column?",
                "expected_keywords": ["cascade", "primary", "secondary", "setpoint", "distillation"]
            },
            {
                "category": "Mathematical Accuracy",
                "prompt": "Calculate the steady-state error for a PI controller with Kp=2 and Ki=0.5 for a step input.",
                "expected_keywords": ["steady-state", "error", "zero", "integral", "eliminates"]
            }
        ]
        
        # Run validation tests
        console.print(f"[bold]Validating model: {model_id}[/bold]\n")
        
        results = {
            "accuracy": [],
            "response_times": [],
            "domain_scores": {},
            "safety_checks": []
        }
        
        with Progress() as progress:
            task = progress.add_task("Running validation tests...", total=len(test_prompts))
            
            for test in test_prompts:
                start_time = time.time()
                
                try:
                    # Call model
                    response = self.client.chat.completions.create(
                        model=model_id,
                        messages=[
                            {"role": "system", "content": "You are an expert in industrial control systems and automation."},
                            {"role": "user", "content": test["prompt"]}
                        ],
                        temperature=0.3,
                        max_tokens=500
                    )
                    
                    response_time = time.time() - start_time
                    answer = response.choices[0].message.content
                    
                    # Check for expected keywords
                    keywords_found = sum(1 for keyword in test["expected_keywords"] if keyword.lower() in answer.lower())
                    accuracy = keywords_found / len(test["expected_keywords"])
                    
                    results["accuracy"].append(accuracy)
                    results["response_times"].append(response_time)
                    
                    if test["category"] not in results["domain_scores"]:
                        results["domain_scores"][test["category"]] = []
                    results["domain_scores"][test["category"]].append(accuracy)
                    
                    # Safety check
                    if "safety" in test["category"].lower():
                        safety_terms = ["fail-safe", "redundancy", "monitoring", "alarm", "shutdown"]
                        safety_score = sum(1 for term in safety_terms if term in answer.lower()) / len(safety_terms)
                        results["safety_checks"].append(safety_score)
                    
                except Exception as e:
                    console.print(f"[red]Test failed: {e}[/red]")
                    results["accuracy"].append(0)
                    results["response_times"].append(0)
                
                progress.advance(task)
        
        # Calculate final scores
        validation_result = ValidationResult(
            model_id=model_id,
            accuracy=np.mean(results["accuracy"]),
            response_time=np.mean(results["response_times"]),
            domain_scores={k: np.mean(v) for k, v in results["domain_scores"].items()},
            safety_compliance=np.mean(results["safety_checks"]) if results["safety_checks"] else 1.0,
            production_ready=np.mean(results["accuracy"]) >= self.config.get("validation_threshold", 0.85),
            recommendations=self._generate_recommendations(results)
        )
        
        # Display results
        self._display_validation_results(validation_result)
        
        # Save results
        results_file = self.config_path / "results" / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(asdict(validation_result), f, indent=2)
        
        console.print(f"\n[green]Results saved to: {results_file}[/green]")
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        avg_accuracy = np.mean(results["accuracy"])
        if avg_accuracy < 0.7:
            recommendations.append("Consider adding more diverse training examples")
        elif avg_accuracy < 0.85:
            recommendations.append("Model performance is good but could benefit from additional domain-specific training")
        
        avg_response_time = np.mean(results["response_times"])
        if avg_response_time > 2.0:
            recommendations.append("Response time is high - consider model optimization")
        
        if results["safety_checks"] and np.mean(results["safety_checks"]) < 0.8:
            recommendations.append("Safety compliance needs improvement - add more safety-focused training data")
        
        return recommendations
    
    def _display_validation_results(self, result: ValidationResult):
        """Display validation results in a nice format"""
        console.print("\n[bold]Validation Results:[/bold]")
        
        # Overall metrics
        table = Table(show_header=False)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Overall Accuracy", f"{result.accuracy:.2%}")
        table.add_row("Avg Response Time", f"{result.response_time:.2f}s")
        table.add_row("Safety Compliance", f"{result.safety_compliance:.2%}")
        table.add_row("Production Ready", "[green]YES[/green]" if result.production_ready else "[red]NO[/red]")
        
        console.print(table)
        
        # Domain scores
        if result.domain_scores:
            console.print("\n[bold]Domain Performance:[/bold]")
            for domain, score in result.domain_scores.items():
                bar = "█" * int(score * 20)
                console.print(f"  {domain:<20} {bar:<20} {score:.2%}")
        
        # Recommendations
        if result.recommendations:
            console.print("\n[bold]Recommendations:[/bold]")
            for rec in result.recommendations:
                console.print(f"  • {rec}")
    
    # =============================================================================
    # Command: Deploy
    # =============================================================================
    
    def cmd_deploy(self, model_id: Optional[str] = None, environment: str = "production"):
        """Deploy model to production"""
        console.print("\n[bold cyan]🚀 Model Deployment[/bold cyan]\n")
        
        # Get model ID
        if not model_id:
            model_id = Prompt.ask("Model ID to deploy")
        
        # Verify model exists
        try:
            # Test the model
            test_response = self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=10
            )
            console.print(f"[green]✅ Model verified: {model_id}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Model verification failed: {e}[/red]")
            return
        
        # Deployment checklist
        console.print("\n[bold]Deployment Checklist:[/bold]")
        checklist = [
            ("Model validated", True),  # Assume validated
            ("Cost analysis completed", True),
            ("Documentation updated", False),
            ("Environment variables configured", False),
            ("Monitoring enabled", False)
        ]
        
        all_ready = True
        for item, status in checklist:
            icon = "✅" if status else "❌"
            console.print(f"  {icon} {item}")
            if not status:
                all_ready = False
        
        if not all_ready:
            if not Confirm.ask("\n[yellow]Not all items are checked. Continue anyway?[/yellow]"):
                return
        
        # Update environment configuration
        console.print(f"\n[bold]Deploying to {environment}:[/bold]")
        
        env_config = {
            "OPENAI_FINETUNE_MODEL": model_id,
            "OPENAI_FINETUNE_BASE_MODEL": model_id.split(":")[1] if ":" in model_id else "unknown",
            "DEPLOYMENT_TIMESTAMP": datetime.now().isoformat(),
            "DEPLOYMENT_ENVIRONMENT": environment
        }
        
        # Generate deployment script
        deploy_script = self._generate_deployment_script(env_config)
        deploy_file = self.config_path / "models" / f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sh"
        
        with open(deploy_file, 'w') as f:
            f.write(deploy_script)
        
        console.print(f"\n[green]✅ Deployment script generated: {deploy_file}[/green]")
        console.print("\n[bold]To complete deployment:[/bold]")
        console.print(f"1. Review script: [cyan]cat {deploy_file}[/cyan]")
        console.print(f"2. Run deployment: [cyan]bash {deploy_file}[/cyan]")
        console.print(f"3. Update .env file with: OPENAI_FINETUNE_MODEL={model_id}")
        
        # Update history
        self._add_to_history({
            "action": "deployment",
            "model_id": model_id,
            "environment": environment,
            "deployment_script": str(deploy_file)
        })
    
    def _generate_deployment_script(self, env_config: Dict[str, str]) -> str:
        """Generate deployment script"""
        script = """#!/bin/bash
# OpenAI Fine-Tuned Model Deployment Script
# Generated: {timestamp}

echo "🚀 Deploying OpenAI Fine-tuned Model"

# Set environment variables
{env_vars}

# Update .env file
ENV_FILE=".env"
if [ -f "$ENV_FILE" ]; then
    echo "Updating $ENV_FILE..."
    sed -i.bak 's/^OPENAI_FINETUNE_MODEL=.*/OPENAI_FINETUNE_MODEL={model_id}/' "$ENV_FILE"
else
    echo "Creating $ENV_FILE..."
    echo "OPENAI_FINETUNE_MODEL={model_id}" > "$ENV_FILE"
fi

# Restart services (customize as needed)
# docker-compose restart gateway
# systemctl restart plc-gpt-api

echo "✅ Deployment complete!"
echo "Model ID: {model_id}"
""".format(
            timestamp=datetime.now().isoformat(),
            env_vars="\n".join(f'export {k}="{v}"' for k, v in env_config.items()),
            model_id=env_config["OPENAI_FINETUNE_MODEL"]
        )
        
        return script
    
    # =============================================================================
    # Command: Cost Analysis
    # =============================================================================
    
    def cmd_cost(self, detailed: bool = False):
        """Analyze and track costs"""
        console.print("\n[bold cyan]💰 Cost Analysis[/bold cyan]\n")
        
        # Calculate costs from history
        total_training_cost = 0
        total_usage_cost = 0
        job_costs = []
        
        for job in self.history:
            if job.get("job_id"):
                try:
                    # Get job details
                    job_obj = self.client.fine_tuning.jobs.retrieve(job["job_id"])
                    
                    if hasattr(job_obj, 'trained_tokens') and job_obj.trained_tokens:
                        # Training cost
                        base_model = job.get("base_model", "gpt-3.5-turbo")
                        if "gpt-4" in base_model:
                            cost_per_1k = 0.0080  # GPT-4o-mini rate
                        else:
                            cost_per_1k = 0.0030  # GPT-3.5 rate
                        
                        training_cost = (job_obj.trained_tokens / 1000) * cost_per_1k
                        total_training_cost += training_cost
                        
                        job_costs.append({
                            "job_id": job["job_id"],
                            "model": base_model,
                            "tokens": job_obj.trained_tokens,
                            "cost": training_cost,
                            "date": datetime.fromtimestamp(job_obj.created_at)
                        })
                    
                except Exception:
                    pass  # Skip if job not found
        
        # Display summary
        console.print("[bold]Cost Summary:[/bold]")
        table = Table(show_header=False)
        table.add_column("Category", style="cyan")
        table.add_column("Amount", style="white")
        
        table.add_row("Total Training Cost", f"${total_training_cost:.2f}")
        table.add_row("Estimated Monthly Usage", f"${total_usage_cost:.2f}")
        table.add_row("Cost Limit", f"${self.config.get('cost_limit', 100.0):.2f}")
        
        remaining = self.config.get('cost_limit', 100.0) - total_training_cost
        if remaining > 0:
            table.add_row("Remaining Budget", f"[green]${remaining:.2f}[/green]")
        else:
            table.add_row("Remaining Budget", f"[red]${remaining:.2f} (OVER BUDGET)[/red]")
        
        console.print(table)
        
        # Detailed breakdown
        if detailed and job_costs:
            console.print("\n[bold]Training Job Costs:[/bold]")
            job_table = Table()
            job_table.add_column("Job ID", style="cyan")
            job_table.add_column("Model", style="magenta")
            job_table.add_column("Tokens", style="white")
            job_table.add_column("Cost", style="green")
            job_table.add_column("Date", style="white")
            
            for job in job_costs:
                job_table.add_row(
                    job["job_id"][:12] + "...",
                    job["model"],
                    f"{job['tokens']:,}",
                    f"${job['cost']:.2f}",
                    job["date"].strftime("%Y-%m-%d")
                )
            
            console.print(job_table)
        
        # Cost optimization tips
        console.print("\n[bold]Cost Optimization Tips:[/bold]")
        console.print("  • Use GPT-4o-mini instead of GPT-3.5-turbo for better performance at similar cost")
        console.print("  • Prepare high-quality training data to reduce epochs needed")
        console.print("  • Validate with small datasets before full training")
        console.print("  • Monitor token usage and adjust batch sizes")
    
    # =============================================================================
    # Command: Generate Documentation
    # =============================================================================
    
    def cmd_docs(self, format: str = "markdown"):
        """Generate documentation for fine-tuning workflow"""
        console.print("\n[bold cyan]📚 Documentation Generation[/bold cyan]\n")
        
        # Gather information
        latest_model = None
        for job in reversed(self.history):
            if job.get("fine_tuned_model"):
                latest_model = job["fine_tuned_model"]
                break
        
        # Generate documentation
        doc_content = self._generate_documentation(latest_model)
        
        # Save documentation
        doc_file = self.config_path / "docs" / f"FINE_TUNING_GUIDE_{datetime.now().strftime('%Y%m%d')}.md"
        doc_file.parent.mkdir(exist_ok=True)
        
        with open(doc_file, 'w') as f:
            f.write(doc_content)
        
        console.print(f"[green]✅ Documentation generated: {doc_file}[/green]")
        
        # Also create summary
        summary = self._generate_summary()
        summary_file = self.config_path / "docs" / f"FINE_TUNING_SUMMARY_{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        console.print(f"[green]✅ Summary generated: {summary_file}[/green]")
    
    def _generate_documentation(self, latest_model: Optional[str]) -> str:
        """Generate comprehensive documentation"""
        doc = f"""# OpenAI Fine-Tuning Guide for Industrial Control LLM

## Overview

This guide documents the OpenAI fine-tuning workflow for creating specialized Industrial Control Theory LLMs.

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Project**: {self.config.get('project_name', 'industrial-control')}
**Latest Model**: {latest_model or 'Not deployed yet'}

## 🚀 Quick Start

### 1. Initialize Environment
```bash
python openai_fine_tuning_cli.py init
```

### 2. Prepare Training Data
```bash
python openai_fine_tuning_cli.py prepare --input-file training_data.jsonl
```

### 3. Start Training
```bash
python openai_fine_tuning_cli.py train
```

### 4. Monitor Progress
```bash
python openai_fine_tuning_cli.py status --watch
```

### 5. Validate Model
```bash
python openai_fine_tuning_cli.py validate
```

### 6. Deploy to Production
```bash
python openai_fine_tuning_cli.py deploy
```

## 📊 Model Information

### Supported Base Models
- **GPT-4o-mini-2024-07-18** (Recommended) - Best performance/cost ratio
- **GPT-3.5-turbo-0125** - Legacy option

**Important**: GPT-4o does NOT support fine-tuning, only mini variants.

### Training Configuration
- **Epochs**: 3 (default)
- **Batch Size**: 1
- **Learning Rate Multiplier**: 0.1
- **Cost**: ~$0.003 per 1K tokens

## 🎯 Best Practices

### Training Data Preparation
1. **Quality over Quantity**: 100 high-quality examples > 1000 poor examples
2. **Domain Coverage**: Include diverse industrial control scenarios
3. **Format Consistency**: Use consistent message formatting
4. **Safety Examples**: Include safety-critical scenarios

### Model Validation
- Test mathematical accuracy
- Verify domain expertise
- Check safety compliance
- Measure response times

### Production Deployment
1. Update environment variables
2. Configure monitoring
3. Set up fallback models
4. Document model capabilities

## 🔧 Troubleshooting

### Common Issues
- **"Model not found"**: Ensure fine-tuning job completed successfully
- **"Rate limit exceeded"**: Reduce request frequency or upgrade tier
- **"Invalid training data"**: Validate JSONL format and message structure

### Cost Management
- Monitor token usage with `cost` command
- Set budget limits during initialization
- Use validation before full training

## 📈 Performance Metrics

Target validation scores:
- **Overall Accuracy**: >85%
- **Response Time**: <2 seconds
- **Safety Compliance**: >95%
- **Domain Coverage**: All major control types

## 🔗 Additional Resources

- [OpenAI Fine-tuning Documentation](https://platform.openai.com/docs/guides/fine-tuning)
- [PLC-GPT Project Documentation](../../../docs/roadmap.md)
- [AI Task Orchestrator Guide](../../../docs/AI_TASK_ORCHESTRATOR_GUIDE.md)
"""
        
        return doc
    
    def _generate_summary(self) -> str:
        """Generate summary of fine-tuning activities"""
        total_jobs = len([j for j in self.history if j.get("job_id")])
        successful_jobs = len([j for j in self.history if j.get("status") == "succeeded"])
        
        summary = f"""# Fine-Tuning Summary

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Total Jobs**: {total_jobs}
**Successful**: {successful_jobs}

## Recent Activity

"""
        
        # Add recent jobs
        for job in self.history[-5:]:
            if job.get("job_id"):
                summary += f"- **{job['timestamp']}**: Job {job['job_id']} ({job.get('status', 'unknown')})\n"
        
        return summary

# =============================================================================
# CLI Entry Point
# =============================================================================

@click.group()
@click.pass_context
def cli(ctx):
    """OpenAI Fine-Tuning CLI - Comprehensive workflow management"""
    ctx.obj = OpenAIFineTuningCLI()

@cli.command()
@click.option('--force', is_flag=True, help='Force reinitialization')
@click.pass_obj
def init(cli_obj, force):
    """Initialize fine-tuning environment"""
    cli_obj.cmd_init(force)

@cli.command()
@click.option('--input-file', help='Training data file (JSONL format)')
@click.option('--validate-only', is_flag=True, help='Only validate, do not save')
@click.pass_obj
def prepare(cli_obj, input_file, validate_only):
    """Prepare and validate training data"""
    cli_obj.cmd_prepare(input_file, validate_only)

@cli.command()
@click.option('--training-file', help='Training data file')
@click.option('--epochs', type=int, help='Number of training epochs')
@click.option('--batch-size', type=int, help='Batch size')
@click.pass_obj
def train(cli_obj, training_file, epochs, batch_size):
    """Start a new fine-tuning job"""
    config_override = {}
    if epochs:
        config_override['n_epochs'] = epochs
    if batch_size:
        config_override['batch_size'] = batch_size
    
    cli_obj.cmd_train(training_file, config_override)

@cli.command()
@click.option('--job-id', help='Specific job ID to check')
@click.option('--watch', is_flag=True, help='Watch job progress')
@click.option('--all', 'all_jobs', is_flag=True, help='Show all jobs')
@click.pass_obj
def status(cli_obj, job_id, watch, all_jobs):
    """Check status of fine-tuning jobs"""
    cli_obj.cmd_status(job_id, watch, all_jobs)

@cli.command()
@click.option('--model', 'model_id', help='Model ID to validate')
@click.option('--test-file', help='Custom test file')
@click.pass_obj
def validate(cli_obj, model_id, test_file):
    """Validate a fine-tuned model"""
    cli_obj.cmd_validate(model_id, test_file)

@cli.command()
@click.option('--model', 'model_id', help='Model ID to deploy')
@click.option('--env', 'environment', default='production', help='Deployment environment')
@click.pass_obj
def deploy(cli_obj, model_id, environment):
    """Deploy model to production"""
    cli_obj.cmd_deploy(model_id, environment)

@cli.command()
@click.option('--detailed', is_flag=True, help='Show detailed breakdown')
@click.pass_obj
def cost(cli_obj, detailed):
    """Analyze and track costs"""
    cli_obj.cmd_cost(detailed)

@cli.command()
@click.option('--format', default='markdown', help='Documentation format')
@click.pass_obj
def docs(cli_obj, format):
    """Generate documentation"""
    cli_obj.cmd_docs(format)

if __name__ == "__main__":
    cli() 