#!/usr/bin/env python3
"""
Enhanced Control Loop Analysis Orchestrator
==========================================

Phase 22.1.1: Analysis Orchestrator Implementation

Main orchestrator coordinating all analysis components into unified workflows.
Provides high-level analysis coordination, workflow management, and integration
with CLI commands, caching system, and job management.

Features:
- Unified analysis workflow orchestration
- Integration of framework, data pipeline, caching, and job management
- CLI-ready commands and interfaces
- Batch analysis capabilities
- Real-time monitoring and progress tracking
- Results aggregation and reporting
- Integration with existing PLC memory management system

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.1 - Modular Analysis Framework (Orchestrator)
Dependencies: Analysis Framework, Data Pipeline, Caching, Job Management
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import pandas as pd

from .core.caching import cache_manager
from .core.data_pipeline import (
    DataPipeline,
    DataSource,
    DataSourceType,
    ProcessingOptions,
    create_default_processing_options,
)

# Import core analysis components
from .core.framework import (
    AnalysisConfiguration,
    AnalysisObjective,
    AnalysisResult,
    AnalysisStatus,
    analysis_framework,
)
from .core.job_manager import (
    AnalysisJob,
    AnalysisJobManager,
    JobPriority,
    create_job_manager,
)

# Import existing components
try:
    from ..scripts.ai.modules.core import BaseOrchestrator
    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError:
    MODULAR_COMPONENTS_AVAILABLE = False
    logging.warning("⚠️ Modular components not available")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WorkflowType(Enum):
    """Analysis workflow type enumeration"""
    SINGLE_ANALYSIS = "single_analysis"
    BATCH_ANALYSIS = "batch_analysis"
    COMPARATIVE_ANALYSIS = "comparative_analysis"
    OPTIMIZATION_WORKFLOW = "optimization_workflow"
    MONITORING_WORKFLOW = "monitoring_workflow"
    VALIDATION_WORKFLOW = "validation_workflow"

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL_SUCCESS = "partial_success"

@dataclass
class WorkflowConfiguration:
    """Configuration for analysis workflows"""
    workflow_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_type: WorkflowType = WorkflowType.SINGLE_ANALYSIS

    # Analysis configuration
    analysis_objective: AnalysisObjective = AnalysisObjective.PID_TUNING
    data_processing_options: ProcessingOptions = field(default_factory=create_default_processing_options)

    # Execution options
    enable_parallel_execution: bool = True
    max_concurrent_analyses: int = 4
    enable_caching: bool = True
    enable_progress_tracking: bool = True

    # Output options
    generate_reports: bool = True
    export_results: bool = False
    export_format: str = "json"  # json, csv, excel

    # Workflow-specific options
    comparison_metrics: List[str] = field(default_factory=lambda: ["mse", "mae", "rmse"])
    optimization_targets: List[str] = field(default_factory=lambda: ["performance", "stability"])

    # Integration options
    notify_completion: bool = False
    callback_url: Optional[str] = None

    # Timeout and retry
    workflow_timeout_minutes: int = 30
    retry_failed_analyses: bool = True
    max_retries: int = 2

@dataclass
class WorkflowStep:
    """Individual step in analysis workflow"""
    step_id: str
    step_type: str
    description: str

    # Dependencies
    depends_on: List[str] = field(default_factory=list)

    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    result: Optional[Any] = None
    error_message: Optional[str] = None

    # Progress
    progress_percent: float = 0.0

@dataclass
class AnalysisWorkflow:
    """Complete analysis workflow definition"""
    workflow_id: str
    configuration: WorkflowConfiguration

    # Data sources
    data_sources: List[DataSource] = field(default_factory=list)

    # Workflow steps
    steps: List[WorkflowStep] = field(default_factory=list)

    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results
    results: Dict[str, AnalysisResult] = field(default_factory=dict)
    aggregated_results: Optional[Dict[str, Any]] = None

    # Progress tracking
    overall_progress: float = 0.0
    current_step: Optional[str] = None

    # Messages
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class WorkflowResult:
    """Result from workflow execution"""
    workflow_id: str
    status: WorkflowStatus
    configuration: WorkflowConfiguration

    # Execution metrics
    execution_time: float = 0.0
    steps_completed: int = 0
    steps_total: int = 0

    # Results
    analysis_results: Dict[str, AnalysisResult] = field(default_factory=dict)
    aggregated_results: Optional[Dict[str, Any]] = None

    # Summary statistics
    success_rate: float = 0.0
    average_processing_time: float = 0.0
    total_data_points: int = 0

    # Files generated
    report_files: List[str] = field(default_factory=list)
    export_files: List[str] = field(default_factory=list)

    # Messages
    summary_message: str = ""
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

class AnalysisOrchestrator:
    """
    Main orchestrator for enhanced control loop analysis
    """

    def __init__(self, enable_job_manager: bool = True, enable_caching: bool = True):
        """Initialize analysis orchestrator"""
        self.orchestrator_id = f"analysis_orchestrator_{int(time.time())}"
        self.logger = logging.getLogger(f"{__name__}.AnalysisOrchestrator")

        # Core components
        self.analysis_framework = analysis_framework
        self.data_pipeline: Optional[DataPipeline] = None
        self.cache_manager = cache_manager if enable_caching else None
        self.job_manager: Optional[AnalysisJobManager] = None

        # Component initialization flags
        self.job_manager_enabled = enable_job_manager
        self.caching_enabled = enable_caching

        # Workflow storage
        self.active_workflows: Dict[str, AnalysisWorkflow] = {}
        self.completed_workflows: Dict[str, WorkflowResult] = {}

        # Statistics
        self.stats = {
            'workflows_executed': 0,
            'analyses_completed': 0,
            'total_execution_time': 0.0,
            'start_time': datetime.now()
        }

        self.logger.info(f"AnalysisOrchestrator initialized: {self.orchestrator_id}")

    async def initialize(self):
        """Initialize orchestrator components"""
        try:
            # Initialize data pipeline
            self.data_pipeline = DataPipeline(create_default_processing_options())

            # Initialize job manager if enabled
            if self.job_manager_enabled:
                self.job_manager = await create_job_manager(
                    max_workers=4,
                    enable_caching=self.caching_enabled
                )

            self.logger.info("Orchestrator components initialized")

        except Exception as e:
            self.logger.error(f"Orchestrator initialization failed: {e}")
            raise

    async def execute_single_analysis(self,
                                    data_source: DataSource,
                                    objective: AnalysisObjective = AnalysisObjective.PID_TUNING,
                                    **kwargs) -> WorkflowResult:
        """Execute single analysis workflow"""

        # Create workflow configuration
        config = WorkflowConfiguration(
            workflow_type=WorkflowType.SINGLE_ANALYSIS,
            analysis_objective=objective,
            **kwargs
        )

        # Create workflow
        workflow = AnalysisWorkflow(
            workflow_id=config.workflow_id,
            configuration=config,
            data_sources=[data_source]
        )

        # Define workflow steps
        workflow.steps = [
            WorkflowStep("data_loading", "data_processing", "Load and preprocess data"),
            WorkflowStep("analysis_execution", "analysis", "Execute control loop analysis"),
            WorkflowStep("result_validation", "validation", "Validate analysis results"),
            WorkflowStep("report_generation", "reporting", "Generate analysis reports")
        ]

        # Execute workflow
        return await self._execute_workflow(workflow)

    async def execute_batch_analysis(self,
                                   data_sources: List[DataSource],
                                   objective: AnalysisObjective = AnalysisObjective.PID_TUNING,
                                   **kwargs) -> WorkflowResult:
        """Execute batch analysis workflow"""

        # Create workflow configuration
        config = WorkflowConfiguration(
            workflow_type=WorkflowType.BATCH_ANALYSIS,
            analysis_objective=objective,
            enable_parallel_execution=True,
            **kwargs
        )

        # Create workflow
        workflow = AnalysisWorkflow(
            workflow_id=config.workflow_id,
            configuration=config,
            data_sources=data_sources
        )

        # Define workflow steps
        workflow.steps = [
            WorkflowStep("batch_data_loading", "data_processing", "Load all data sources"),
            WorkflowStep("parallel_analysis", "analysis", "Execute parallel analyses"),
            WorkflowStep("result_aggregation", "aggregation", "Aggregate analysis results"),
            WorkflowStep("comparative_report", "reporting", "Generate comparative reports")
        ]

        # Execute workflow
        return await self._execute_workflow(workflow)

    async def execute_comparative_analysis(self,
                                         data_sources: List[DataSource],
                                         comparison_metrics: List[str] = None,
                                         **kwargs) -> WorkflowResult:
        """Execute comparative analysis workflow"""

        if comparison_metrics is None:
            comparison_metrics = ["mse", "mae", "rmse", "oscillation_index"]

        # Create workflow configuration
        config = WorkflowConfiguration(
            workflow_type=WorkflowType.COMPARATIVE_ANALYSIS,
            comparison_metrics=comparison_metrics,
            **kwargs
        )

        # Create workflow
        workflow = AnalysisWorkflow(
            workflow_id=config.workflow_id,
            configuration=config,
            data_sources=data_sources
        )

        # Define workflow steps
        workflow.steps = [
            WorkflowStep("data_standardization", "data_processing", "Standardize data formats"),
            WorkflowStep("baseline_analysis", "analysis", "Establish baseline performance"),
            WorkflowStep("comparative_analysis", "analysis", "Compare against baseline"),
            WorkflowStep("statistical_comparison", "statistics", "Statistical significance testing"),
            WorkflowStep("comparative_report", "reporting", "Generate comparison report")
        ]

        # Execute workflow
        return await self._execute_workflow(workflow)

    async def _execute_workflow(self, workflow: AnalysisWorkflow) -> WorkflowResult:
        """Execute analysis workflow"""
        start_time = time.time()

        try:
            # Store active workflow
            self.active_workflows[workflow.workflow_id] = workflow

            # Initialize workflow
            workflow.status = WorkflowStatus.INITIALIZING
            workflow.started_at = datetime.now()

            self.logger.info(f"Starting workflow {workflow.workflow_id} ({workflow.configuration.workflow_type.value})")

            # Execute workflow steps
            if workflow.configuration.workflow_type == WorkflowType.SINGLE_ANALYSIS:
                await self._execute_single_analysis_workflow(workflow)
            elif workflow.configuration.workflow_type == WorkflowType.BATCH_ANALYSIS:
                await self._execute_batch_analysis_workflow(workflow)
            elif workflow.configuration.workflow_type == WorkflowType.COMPARATIVE_ANALYSIS:
                await self._execute_comparative_analysis_workflow(workflow)
            else:
                raise ValueError(f"Unsupported workflow type: {workflow.configuration.workflow_type}")

            # Update workflow status
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()

            # Create workflow result
            execution_time = time.time() - start_time
            workflow_result = WorkflowResult(
                workflow_id=workflow.workflow_id,
                status=workflow.status,
                configuration=workflow.configuration,
                execution_time=execution_time,
                steps_completed=len([s for s in workflow.steps if s.status == WorkflowStatus.COMPLETED]),
                steps_total=len(workflow.steps),
                analysis_results=workflow.results,
                aggregated_results=workflow.aggregated_results,
                success_rate=len(workflow.results) / max(1, len(workflow.data_sources)),
                summary_message=f"Workflow completed successfully in {execution_time:.2f}s"
            )

            # Store completed workflow
            self.completed_workflows[workflow.workflow_id] = workflow_result
            del self.active_workflows[workflow.workflow_id]

            # Update statistics
            self.stats['workflows_executed'] += 1
            self.stats['analyses_completed'] += len(workflow.results)
            self.stats['total_execution_time'] += execution_time

            self.logger.info(f"Workflow {workflow.workflow_id} completed successfully")
            return workflow_result

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.errors.append(str(e))

            self.logger.error(f"Workflow {workflow.workflow_id} failed: {e}")

            # Create failure result
            workflow_result = WorkflowResult(
                workflow_id=workflow.workflow_id,
                status=WorkflowStatus.FAILED,
                configuration=workflow.configuration,
                execution_time=time.time() - start_time,
                errors=[str(e)],
                summary_message=f"Workflow failed: {str(e)}"
            )

            self.completed_workflows[workflow.workflow_id] = workflow_result
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]

            return workflow_result

    async def _execute_single_analysis_workflow(self, workflow: AnalysisWorkflow) -> Dict[str, Any]:
        """Execute single analysis workflow steps"""
        workflow.status = WorkflowStatus.RUNNING
        data_source = workflow.data_sources[0]

        # Step 1: Data loading and preprocessing
        await self._update_step_status(workflow, "data_loading", WorkflowStatus.RUNNING)

        if not self.data_pipeline:
            self.data_pipeline = DataPipeline(workflow.configuration.data_processing_options)

        processing_result = await self.data_pipeline.process_data_source(data_source)

        if not processing_result.success:
            raise RuntimeError(f"Data processing failed: {processing_result.errors}")

        await self._update_step_status(workflow, "data_loading", WorkflowStatus.COMPLETED)

        # Step 2: Analysis execution
        await self._update_step_status(workflow, "analysis_execution", WorkflowStatus.RUNNING)

        analysis_config = AnalysisConfiguration(
            objective=workflow.configuration.analysis_objective,
            time_column=data_source.time_column,
            **dict(data_source.columns.items())
        )

        analysis_result = await self.analysis_framework.analyze(
            processing_result.data,
            analysis_config
        )

        workflow.results[data_source.source_id] = analysis_result
        await self._update_step_status(workflow, "analysis_execution", WorkflowStatus.COMPLETED)

        # Step 3: Result validation
        await self._update_step_status(workflow, "result_validation", WorkflowStatus.RUNNING)

        validation_score = self._validate_analysis_result(analysis_result)
        if validation_score < 0.7:  # 70% threshold
            workflow.warnings.append(f"Low validation score: {validation_score:.2f}")

        await self._update_step_status(workflow, "result_validation", WorkflowStatus.COMPLETED)

        # Step 4: Report generation
        if workflow.configuration.generate_reports:
            await self._update_step_status(workflow, "report_generation", WorkflowStatus.RUNNING)

            report_data = await self._generate_analysis_report(analysis_result, workflow.configuration)
            workflow.aggregated_results = report_data

            await self._update_step_status(workflow, "report_generation", WorkflowStatus.COMPLETED)

        return {"primary_analysis": analysis_result}

    async def _execute_batch_analysis_workflow(self, workflow: AnalysisWorkflow) -> Dict[str, Any]:
        """Execute batch analysis workflow steps"""
        workflow.status = WorkflowStatus.RUNNING

        # Step 1: Batch data loading
        await self._update_step_status(workflow, "batch_data_loading", WorkflowStatus.RUNNING)

        processed_data = {}
        for data_source in workflow.data_sources:
            if not self.data_pipeline:
                self.data_pipeline = DataPipeline(workflow.configuration.data_processing_options)

            result = await self.data_pipeline.process_data_source(data_source)
            if result.success:
                processed_data[data_source.source_id] = result.data
            else:
                workflow.warnings.append(f"Failed to process {data_source.source_id}: {result.errors}")

        await self._update_step_status(workflow, "batch_data_loading", WorkflowStatus.COMPLETED)

        # Step 2: Parallel analysis execution
        await self._update_step_status(workflow, "parallel_analysis", WorkflowStatus.RUNNING)

        if self.job_manager and workflow.configuration.enable_parallel_execution:
            # Use job manager for parallel execution
            analysis_results = await self._execute_parallel_analyses_with_jobs(
                processed_data, workflow.configuration
            )
        else:
            # Sequential execution
            analysis_results = await self._execute_sequential_analyses(
                processed_data, workflow.configuration
            )

        workflow.results.update(analysis_results)
        await self._update_step_status(workflow, "parallel_analysis", WorkflowStatus.COMPLETED)

        # Step 3: Result aggregation
        await self._update_step_status(workflow, "result_aggregation", WorkflowStatus.RUNNING)

        aggregated_results = await self._aggregate_batch_results(analysis_results)
        workflow.aggregated_results = aggregated_results

        await self._update_step_status(workflow, "result_aggregation", WorkflowStatus.COMPLETED)

        # Step 4: Comparative report
        if workflow.configuration.generate_reports:
            await self._update_step_status(workflow, "comparative_report", WorkflowStatus.RUNNING)

            report_data = await self._generate_batch_report(analysis_results, aggregated_results)
            workflow.aggregated_results.update(report_data)

            await self._update_step_status(workflow, "comparative_report", WorkflowStatus.COMPLETED)

        return analysis_results

    async def _execute_comparative_analysis_workflow(self, workflow: AnalysisWorkflow) -> Dict[str, Any]:
        """Execute comparative analysis workflow steps"""
        workflow.status = WorkflowStatus.RUNNING

        # Execute similar to batch analysis but with comparative focus
        batch_results = await self._execute_batch_analysis_workflow(workflow)

        # Additional comparative analysis
        comparative_results = await self._perform_comparative_analysis(
            batch_results, workflow.configuration.comparison_metrics
        )

        workflow.aggregated_results = comparative_results
        return batch_results

    async def _execute_parallel_analyses_with_jobs(self,
                                                 processed_data: Dict[str, pd.DataFrame],
                                                 config: WorkflowConfiguration) -> Dict[str, AnalysisResult]:
        """Execute analyses using job manager for parallelization"""
        if not self.job_manager:
            return await self._execute_sequential_analyses(processed_data, config)

        analysis_results = {}
        job_ids = []

        # Submit jobs
        for source_id, data in processed_data.items():
            analysis_config = AnalysisConfiguration(objective=config.analysis_objective)

            job = AnalysisJob(
                job_id=str(uuid.uuid4()),
                configuration=analysis_config,
                data=data,
                priority=JobPriority.NORMAL
            )

            job_id = await self.job_manager.submit_job(job)
            job_ids.append((job_id, source_id))

        # Wait for completion
        max_wait_time = config.workflow_timeout_minutes * 60
        start_time = time.time()

        while job_ids and (time.time() - start_time) < max_wait_time:
            completed_jobs = []

            for job_id, source_id in job_ids:
                job_status = await self.job_manager.get_job_status(job_id)

                if job_status and job_status['status'] in ['completed', 'failed']:
                    completed_jobs.append((job_id, source_id))

                    if job_status['status'] == 'completed':
                        # Get result from job manager
                        job = self.job_manager.jobs.get(job_id)
                        if job and job.result:
                            analysis_results[source_id] = job.result

            # Remove completed jobs
            for completed_job in completed_jobs:
                job_ids.remove(completed_job)

            await asyncio.sleep(0.5)

        return analysis_results

    async def _execute_sequential_analyses(self,
                                         processed_data: Dict[str, pd.DataFrame],
                                         config: WorkflowConfiguration) -> Dict[str, AnalysisResult]:
        """Execute analyses sequentially"""
        analysis_results = {}

        for source_id, data in processed_data.items():
            try:
                analysis_config = AnalysisConfiguration(objective=config.analysis_objective)
                result = await self.analysis_framework.analyze(data, analysis_config)
                analysis_results[source_id] = result
            except Exception as e:
                self.logger.error(f"Analysis failed for {source_id}: {e}")

        return analysis_results

    async def _update_step_status(self, workflow: AnalysisWorkflow, step_id: str, status: WorkflowStatus):
        """Update workflow step status"""
        for step in workflow.steps:
            if step.step_id == step_id:
                step.status = status
                if status == WorkflowStatus.RUNNING:
                    step.started_at = datetime.now()
                elif status == WorkflowStatus.COMPLETED:
                    step.completed_at = datetime.now()
                    step.progress_percent = 100.0
                break

        # Update overall progress
        completed_steps = sum(1 for step in workflow.steps if step.status == WorkflowStatus.COMPLETED)
        workflow.overall_progress = (completed_steps / len(workflow.steps)) * 100.0
        workflow.current_step = step_id

    def _validate_analysis_result(self, result: AnalysisResult) -> float:
        """Validate analysis result quality"""
        score = 1.0

        # Check for required parameters
        if not result.model_parameters:
            score -= 0.3

        if not result.tuning_parameters:
            score -= 0.3

        # Check for errors
        if result.errors:
            score -= 0.2 * len(result.errors)

        # Check processing time reasonableness
        if result.processing_time > 60:  # More than 1 minute
            score -= 0.1

        return max(0.0, score)

    async def _generate_analysis_report(self, result: AnalysisResult, config: WorkflowConfiguration) -> Dict[str, Any]:
        """Generate analysis report"""
        return {
            'report_type': 'single_analysis',
            'analysis_id': result.analysis_id,
            'objective': result.objective.value,
            'status': result.status.value,
            'model_parameters': result.model_parameters,
            'tuning_parameters': result.tuning_parameters,
            'performance_metrics': result.performance_metrics,
            'processing_time': result.processing_time,
            'data_points': result.data_points,
            'validation_scores': result.validation_scores,
            'generated_at': datetime.now().isoformat()
        }

    async def _aggregate_batch_results(self, results: Dict[str, AnalysisResult]) -> Dict[str, Any]:
        """Aggregate batch analysis results"""
        if not results:
            return {}

        # Calculate aggregate statistics
        processing_times = [r.processing_time for r in results.values()]
        data_points = [r.data_points for r in results.values()]

        # Aggregate model parameters
        model_params = {}
        for param in ['K', 'L', 'tau']:
            values = [r.model_parameters.get(param, 0) for r in results.values() if r.model_parameters]
            if values:
                model_params[param] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values),
                    'std': (sum((x - sum(values)/len(values))**2 for x in values) / len(values))**0.5
                }

        # Aggregate performance metrics
        performance_metrics = {}
        for metric in ['mse', 'mae', 'rmse']:
            values = [r.performance_metrics.get(metric, 0) for r in results.values() if r.performance_metrics]
            if values:
                performance_metrics[metric] = {
                    'mean': sum(values) / len(values),
                    'min': min(values),
                    'max': max(values)
                }

        return {
            'aggregation_type': 'batch_results',
            'total_analyses': len(results),
            'successful_analyses': len([r for r in results.values() if r.status == AnalysisStatus.COMPLETED]),
            'average_processing_time': sum(processing_times) / len(processing_times),
            'total_data_points': sum(data_points),
            'aggregated_model_parameters': model_params,
            'aggregated_performance_metrics': performance_metrics,
            'aggregated_at': datetime.now().isoformat()
        }

    async def _generate_batch_report(self, results: Dict[str, AnalysisResult],
                                   aggregated: Dict[str, Any]) -> Dict[str, Any]:
        """Generate batch analysis report"""
        return {
            'report_type': 'batch_analysis',
            'summary': aggregated,
            'individual_results': {
                source_id: {
                    'analysis_id': result.analysis_id,
                    'status': result.status.value,
                    'processing_time': result.processing_time,
                    'data_points': result.data_points,
                    'model_parameters': result.model_parameters,
                    'tuning_parameters': result.tuning_parameters,
                    'performance_metrics': result.performance_metrics
                }
                for source_id, result in results.items()
            },
            'generated_at': datetime.now().isoformat()
        }

    async def _perform_comparative_analysis(self, results: Dict[str, AnalysisResult],
                                          metrics: List[str]) -> Dict[str, Any]:
        """Perform comparative analysis between results"""
        if len(results) < 2:
            return {'error': 'Comparative analysis requires at least 2 results'}

        comparisons = {}

        # Compare performance metrics
        for metric in metrics:
            values = {}
            for source_id, result in results.items():
                if result.performance_metrics and metric in result.performance_metrics:
                    values[source_id] = result.performance_metrics[metric]

            if len(values) >= 2:
                sorted_values = sorted(values.items(), key=lambda x: x[1])
                comparisons[metric] = {
                    'best': sorted_values[0],
                    'worst': sorted_values[-1],
                    'ranking': [{'source': k, 'value': v} for k, v in sorted_values],
                    'improvement_potential': sorted_values[-1][1] - sorted_values[0][1]
                }

        return {
            'comparison_type': 'performance_metrics',
            'metrics_compared': metrics,
            'comparisons': comparisons,
            'recommendation': self._generate_comparison_recommendation(comparisons),
            'compared_at': datetime.now().isoformat()
        }

    def _generate_comparison_recommendation(self, comparisons: Dict[str, Any]) -> str:
        """Generate recommendation based on comparative analysis"""
        if not comparisons:
            return "Insufficient data for recommendations"

        # Simple recommendation logic
        best_sources = set()
        for _metric, data in comparisons.items():
            if 'best' in data:
                best_sources.add(data['best'][0])

        if len(best_sources) == 1:
            source = best_sources.pop()
            return f"Source '{source}' shows consistently best performance across metrics"
        else:
            return "Performance varies across metrics - detailed analysis recommended"

    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a workflow"""
        # Check active workflows
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'status': workflow.status.value,
                'progress': workflow.overall_progress,
                'current_step': workflow.current_step,
                'steps': [
                    {
                        'step_id': step.step_id,
                        'status': step.status.value,
                        'progress': step.progress_percent
                    }
                    for step in workflow.steps
                ],
                'results_count': len(workflow.results),
                'warnings': workflow.warnings,
                'errors': workflow.errors
            }

        # Check completed workflows
        if workflow_id in self.completed_workflows:
            result = self.completed_workflows[workflow_id]
            return {
                'workflow_id': workflow_id,
                'status': result.status.value,
                'execution_time': result.execution_time,
                'success_rate': result.success_rate,
                'steps_completed': result.steps_completed,
                'steps_total': result.steps_total,
                'results_count': len(result.analysis_results),
                'summary': result.summary_message
            }

        return None

    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel an active workflow"""
        if workflow_id not in self.active_workflows:
            return False

        workflow = self.active_workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED

        # Cancel any running jobs if using job manager
        if self.job_manager:
            # Implementation would cancel related jobs
            pass

        # Move to completed workflows
        result = WorkflowResult(
            workflow_id=workflow_id,
            status=WorkflowStatus.CANCELLED,
            configuration=workflow.configuration,
            summary_message="Workflow cancelled by user"
        )

        self.completed_workflows[workflow_id] = result
        del self.active_workflows[workflow_id]

        self.logger.info(f"Workflow {workflow_id} cancelled")
        return True

    async def get_orchestrator_statistics(self) -> Dict[str, Any]:
        """Get comprehensive orchestrator statistics"""
        uptime = datetime.now() - self.stats['start_time']

        # Component status
        component_status = {
            'analysis_framework': 'operational',
            'data_pipeline': 'operational' if self.data_pipeline else 'not_initialized',
            'cache_manager': 'operational' if self.cache_manager else 'disabled',
            'job_manager': 'operational' if self.job_manager else 'disabled'
        }

        # Workflow statistics
        workflow_stats = {
            'active_workflows': len(self.active_workflows),
            'completed_workflows': len(self.completed_workflows),
            'total_workflows': self.stats['workflows_executed'],
            'total_analyses': self.stats['analyses_completed'],
            'average_execution_time': (
                self.stats['total_execution_time'] / max(1, self.stats['workflows_executed'])
            )
        }

        return {
            'orchestrator_id': self.orchestrator_id,
            'uptime_seconds': uptime.total_seconds(),
            'component_status': component_status,
            'workflow_statistics': workflow_stats,
            'performance_statistics': self.stats,
            'capabilities': [
                'Single analysis workflows',
                'Batch analysis workflows',
                'Comparative analysis workflows',
                'Parallel execution support',
                'Result caching and aggregation',
                'Progress tracking and monitoring',
                'CLI integration ready'
            ]
        }

# Global orchestrator instance
analysis_orchestrator = AnalysisOrchestrator()

# Convenience functions
async def analyze_single_dataset(file_path: str,
                               objective: AnalysisObjective = AnalysisObjective.PID_TUNING,
                               **kwargs) -> WorkflowResult:
    """Convenience function for single dataset analysis"""
    if not analysis_orchestrator.data_pipeline:
        await analysis_orchestrator.initialize()

    data_source = DataSource(
        source_id="single_dataset",
        source_type=DataSourceType.CSV_FILE,
        location=file_path
    )

    return await analysis_orchestrator.execute_single_analysis(data_source, objective, **kwargs)

async def analyze_multiple_datasets(file_paths: List[str],
                                  objective: AnalysisObjective = AnalysisObjective.PID_TUNING,
                                  **kwargs) -> WorkflowResult:
    """Convenience function for batch analysis of multiple datasets"""
    if not analysis_orchestrator.data_pipeline:
        await analysis_orchestrator.initialize()

    data_sources = [
        DataSource(
            source_id=f"dataset_{i}",
            source_type=DataSourceType.CSV_FILE,
            location=file_path
        )
        for i, file_path in enumerate(file_paths)
    ]

    return await analysis_orchestrator.execute_batch_analysis(data_sources, objective, **kwargs)

def get_orchestrator_info() -> Dict[str, Any]:
    """Get comprehensive orchestrator information"""
    return {
        'version': '22.1.0',
        'orchestrator_id': analysis_orchestrator.orchestrator_id,
        'capabilities': [
            'Single analysis workflows',
            'Batch analysis workflows',
            'Comparative analysis workflows',
            'Parallel job execution',
            'Result caching and persistence',
            'Progress tracking and monitoring',
            'CLI integration support',
            'Multi-database integration'
        ],
        'supported_data_sources': [
            'CSV files',
            'Excel files',
            'Database connections',
            'Real-time PLC data',
            'API endpoints'
        ],
        'supported_objectives': [obj.value for obj in AnalysisObjective],
        'workflow_types': [wf.value for wf in WorkflowType]
    }

if __name__ == "__main__":
    # Demo and testing
    async def main():
        logger.info("🚀 Enhanced Control Loop Analysis Orchestrator - Demo")

        try:
            # Initialize orchestrator
            await analysis_orchestrator.initialize()

            # Create sample data file (for demo)
            import tempfile

            import numpy as np
            import pandas as pd

            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
                # Generate sample control loop data
                time_data = pd.date_range('2025-01-01', periods=100, freq='1S')
                sample_df = pd.DataFrame({
                    'timestamp': time_data,
                    'CV': np.random.randn(100).cumsum() + 50,
                    'PV': np.random.randn(100).cumsum() + 25,
                    'SP': np.full(100, 30)
                })
                sample_df.to_csv(f.name, index=False)
                sample_file = f.name

            # Test single analysis
            logger.info("Testing single analysis workflow...")
            single_result = await analyze_single_dataset(
                sample_file,
                objective=AnalysisObjective.PID_TUNING
            )

            logger.info(f"✅ Single analysis: {single_result.status.value}")
            logger.info(f"📊 Execution time: {single_result.execution_time:.2f}s")
            logger.info(f"📊 Success rate: {single_result.success_rate:.2%}")

            # Test batch analysis
            logger.info("Testing batch analysis workflow...")
            batch_result = await analyze_multiple_datasets(
                [sample_file, sample_file],  # Use same file twice for demo
                objective=AnalysisObjective.PID_TUNING
            )

            logger.info(f"✅ Batch analysis: {batch_result.status.value}")
            logger.info(f"📊 Analyses completed: {len(batch_result.analysis_results)}")
            logger.info(f"📊 Average processing time: {batch_result.average_processing_time:.2f}s")

            # Get orchestrator statistics
            stats = await analysis_orchestrator.get_orchestrator_statistics()
            logger.info(f"📊 Total workflows: {stats['workflow_statistics']['total_workflows']}")
            logger.info(f"📊 Total analyses: {stats['workflow_statistics']['total_analyses']}")

            # Cleanup
            import os
            os.unlink(sample_file)

        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")

        logger.info("✅ Orchestrator demo completed")

    asyncio.run(main())
