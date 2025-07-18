#!/usr/bin/env python3
"""
Enhanced Control Loop Analysis Job Manager
==========================================

Phase 22.1.1: Async Analysis Job Management

Advanced job management system for control loop analysis providing:
- Async job orchestration with progress tracking
- Scalable concurrent analysis execution
- Job queuing, prioritization, and resource management
- Integration with analysis framework and caching system
- Real-time job monitoring and cancellation support

Features:
- Multi-worker async job processing
- Job dependency management and scheduling
- Progress tracking with detailed status updates
- Resource allocation and throttling
- Job result aggregation and notification
- Integration with existing CLI and monitoring systems

Author: AI Task Orchestrator
Created: January 18, 2025
Phase: 22.1.1 - Modular Analysis Framework (Job Management)
Dependencies: Analysis Framework, Result Caching, CLI Infrastructure
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, AsyncGenerator, Set
import concurrent.futures
import threading

# Import analysis framework components
from .framework import AnalysisFramework, AnalysisResult, AnalysisConfiguration, AnalysisObjective, AnalysisStatus
from .caching import CacheManager, CacheResult

# Import existing components
try:
    from ...scripts.ai.modules.core import BaseOrchestrator
    MODULAR_COMPONENTS_AVAILABLE = True
except ImportError:
    MODULAR_COMPONENTS_AVAILABLE = False
    logging.warning("⚠️ Modular components not available")

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobStatus(Enum):
    """Analysis job status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"

class JobPriority(Enum):
    """Job priority enumeration"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4
    CRITICAL = 5

class WorkerStatus(Enum):
    """Worker status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"

@dataclass
class JobConfiguration:
    """Job execution configuration"""
    
    # Resource allocation
    max_workers: int = 4
    max_concurrent_jobs: int = 10
    job_timeout_seconds: int = 300  # 5 minutes default
    
    # Queue management
    max_queue_size: int = 100
    enable_priority_queue: bool = True
    auto_retry_failed: bool = True
    max_retries: int = 3
    
    # Performance tuning
    worker_keepalive_seconds: int = 60
    batch_processing: bool = True
    result_aggregation: bool = True
    
    # Monitoring
    enable_progress_tracking: bool = True
    progress_update_interval: float = 1.0  # seconds
    enable_notifications: bool = True
    
    # Integration
    enable_caching: bool = True
    cache_results: bool = True
    use_existing_cache: bool = True

@dataclass
class JobProgress:
    """Job progress information"""
    job_id: str
    current_stage: str = "initializing"
    completed_stages: List[str] = field(default_factory=list)
    total_stages: int = 1
    progress_percent: float = 0.0
    
    # Timing information
    started_at: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    # Status details
    current_operation: str = ""
    items_processed: int = 0
    items_total: int = 0
    
    # Messages
    status_message: str = ""
    warnings: List[str] = field(default_factory=list)
    
    def update_progress(self, percent: float, message: str = "", operation: str = ""):
        """Update progress information"""
        self.progress_percent = max(0.0, min(100.0, percent))
        if message:
            self.status_message = message
        if operation:
            self.current_operation = operation
        
        # Estimate completion time
        if self.started_at and self.progress_percent > 0:
            elapsed = datetime.now() - self.started_at
            total_estimated = elapsed / (self.progress_percent / 100.0)
            self.estimated_completion = self.started_at + total_estimated

@dataclass
class AnalysisJob:
    """Analysis job definition"""
    job_id: str
    configuration: AnalysisConfiguration
    data: Any  # Analysis data
    
    # Job metadata
    created_at: datetime = field(default_factory=datetime.now)
    priority: JobPriority = JobPriority.NORMAL
    timeout_seconds: int = 300
    
    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Job IDs this job depends on
    tags: List[str] = field(default_factory=list)
    
    # Execution state
    status: JobStatus = JobStatus.PENDING
    assigned_worker: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Progress tracking
    progress: JobProgress = field(default_factory=lambda: JobProgress(""))
    
    # Results
    result: Optional[AnalysisResult] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Callbacks
    progress_callback: Optional[Callable[[JobProgress], None]] = None
    completion_callback: Optional[Callable[['AnalysisJob'], None]] = None
    
    def __post_init__(self):
        """Initialize job after creation"""
        if not self.progress.job_id:
            self.progress.job_id = self.job_id
    
    def is_ready_to_run(self, completed_jobs: Set[str]) -> bool:
        """Check if job is ready to run based on dependencies"""
        if self.status != JobStatus.QUEUED:
            return False
        
        # Check if all dependencies are completed
        for dep_id in self.dependencies:
            if dep_id not in completed_jobs:
                return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if job has timed out"""
        if self.started_at is None:
            return False
        
        elapsed = datetime.now() - self.started_at
        return elapsed.total_seconds() > self.timeout_seconds

@dataclass
class JobResult:
    """Job execution result"""
    job_id: str
    status: JobStatus
    result: Optional[AnalysisResult] = None
    
    # Execution metrics
    execution_time: float = 0.0
    queue_time: float = 0.0
    worker_id: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Performance metrics
    peak_memory_mb: float = 0.0
    cpu_time_seconds: float = 0.0

class AnalysisWorker:
    """Async analysis worker for job execution"""
    
    def __init__(self, worker_id: str, analysis_framework: AnalysisFramework):
        self.worker_id = worker_id
        self.analysis_framework = analysis_framework
        self.status = WorkerStatus.IDLE
        self.current_job: Optional[AnalysisJob] = None
        self.jobs_completed = 0
        self.logger = logging.getLogger(f"{__name__}.Worker.{worker_id}")
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_execution_time = 0.0
        self.errors_encountered = 0
    
    async def execute_job(self, job: AnalysisJob) -> JobResult:
        """Execute an analysis job"""
        start_time = time.time()
        
        try:
            self.status = WorkerStatus.BUSY
            self.current_job = job
            
            # Update job status
            job.status = JobStatus.RUNNING
            job.assigned_worker = self.worker_id
            job.started_at = datetime.now()
            job.progress.started_at = job.started_at
            
            self.logger.info(f"Starting job {job.job_id}")
            
            # Execute analysis
            job.progress.update_progress(10.0, "Initializing analysis", "setup")
            
            # Run the actual analysis
            analysis_result = await self._run_analysis(job)
            
            job.progress.update_progress(100.0, "Analysis completed", "finished")
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now()
            job.result = analysis_result
            
            # Create job result
            result = JobResult(
                job_id=job.job_id,
                status=JobStatus.COMPLETED,
                result=analysis_result,
                execution_time=time.time() - start_time,
                worker_id=self.worker_id
            )
            
            self.jobs_completed += 1
            self.total_execution_time += result.execution_time
            
            # Call completion callback if provided
            if job.completion_callback:
                try:
                    job.completion_callback(job)
                except Exception as e:
                    self.logger.warning(f"Completion callback failed: {e}")
            
            self.logger.info(f"Job {job.job_id} completed in {result.execution_time:.2f}s")
            return result
            
        except asyncio.TimeoutError:
            job.status = JobStatus.TIMEOUT
            error_msg = f"Job {job.job_id} timed out after {job.timeout_seconds}s"
            self.logger.error(error_msg)
            self.errors_encountered += 1
            
            return JobResult(
                job_id=job.job_id,
                status=JobStatus.TIMEOUT,
                execution_time=time.time() - start_time,
                worker_id=self.worker_id,
                error_message=error_msg
            )
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            error_msg = f"Job {job.job_id} failed: {str(e)}"
            self.logger.error(error_msg)
            self.errors_encountered += 1
            
            return JobResult(
                job_id=job.job_id,
                status=JobStatus.FAILED,
                execution_time=time.time() - start_time,
                worker_id=self.worker_id,
                error_message=error_msg,
                retry_count=job.retry_count
            )
            
        finally:
            self.status = WorkerStatus.IDLE
            self.current_job = None
    
    async def _run_analysis(self, job: AnalysisJob) -> AnalysisResult:
        """Run the actual analysis with progress tracking"""
        # Update progress through analysis stages
        stages = ["validation", "preprocessing", "analysis", "validation", "results"]
        
        for i, stage in enumerate(stages):
            progress = (i + 1) / len(stages) * 90  # Leave 10% for completion
            job.progress.update_progress(progress, f"Executing {stage}", stage)
            job.progress.completed_stages.append(stage)
            
            # Call progress callback if provided
            if job.progress_callback:
                try:
                    job.progress_callback(job.progress)
                except Exception as e:
                    self.logger.warning(f"Progress callback failed: {e}")
            
            # Small delay to simulate processing
            await asyncio.sleep(0.1)
        
        # Execute the actual analysis
        try:
            result = await asyncio.wait_for(
                self.analysis_framework.analyze(job.data, job.configuration),
                timeout=job.timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            raise asyncio.TimeoutError(f"Analysis timed out after {job.timeout_seconds}s")
    
    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker performance statistics"""
        uptime = datetime.now() - self.start_time
        return {
            'worker_id': self.worker_id,
            'status': self.status.value,
            'jobs_completed': self.jobs_completed,
            'uptime_seconds': uptime.total_seconds(),
            'total_execution_time': self.total_execution_time,
            'average_job_time': self.total_execution_time / max(1, self.jobs_completed),
            'errors_encountered': self.errors_encountered,
            'current_job': self.current_job.job_id if self.current_job else None
        }

class AnalysisJobManager:
    """
    Main job manager for orchestrating analysis jobs
    """
    
    def __init__(self, config: JobConfiguration = None, 
                 analysis_framework: AnalysisFramework = None,
                 cache_manager: CacheManager = None):
        """Initialize job manager"""
        self.config = config or JobConfiguration()
        self.analysis_framework = analysis_framework or AnalysisFramework()
        self.cache_manager = cache_manager
        
        self.manager_id = f"job_manager_{int(time.time())}"
        self.logger = logging.getLogger(f"{__name__}.JobManager")
        
        # Job storage
        self.jobs: Dict[str, AnalysisJob] = {}
        self.job_queue = deque()  # Priority queue would be better for production
        self.completed_jobs: Set[str] = set()
        
        # Worker management
        self.workers: Dict[str, AnalysisWorker] = {}
        self.worker_tasks: Dict[str, asyncio.Task] = {}
        
        # Execution state
        self.is_running = False
        self.manager_task: Optional[asyncio.Task] = None
        
        # Statistics
        self.stats = {
            'jobs_submitted': 0,
            'jobs_completed': 0,
            'jobs_failed': 0,
            'total_execution_time': 0.0,
            'start_time': datetime.now()
        }
        
        # Initialize workers
        self._initialize_workers()
        
        self.logger.info(f"JobManager initialized: {self.manager_id}")
    
    def _initialize_workers(self):
        """Initialize analysis workers"""
        for i in range(self.config.max_workers):
            worker_id = f"worker_{i+1}"
            worker = AnalysisWorker(worker_id, self.analysis_framework)
            self.workers[worker_id] = worker
        
        self.logger.info(f"Initialized {len(self.workers)} workers")
    
    async def start(self):
        """Start the job manager"""
        if self.is_running:
            self.logger.warning("Job manager is already running")
            return
        
        self.is_running = True
        self.manager_task = asyncio.create_task(self._job_manager_loop())
        self.logger.info("Job manager started")
    
    async def stop(self):
        """Stop the job manager"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        # Cancel all running tasks
        if self.manager_task:
            self.manager_task.cancel()
        
        # Cancel worker tasks
        for task in self.worker_tasks.values():
            task.cancel()
        
        # Wait for cleanup
        await asyncio.sleep(0.1)
        
        self.logger.info("Job manager stopped")
    
    async def submit_job(self, job: AnalysisJob) -> str:
        """Submit a job for execution"""
        try:
            # Check queue capacity
            if len(self.job_queue) >= self.config.max_queue_size:
                raise RuntimeError(f"Job queue is full (max: {self.config.max_queue_size})")
            
            # Check for cached results if enabled
            if self.config.use_existing_cache and self.cache_manager:
                cache_key = self.cache_manager.generate_cache_key(
                    AnalysisResult(
                        analysis_id=job.configuration.analysis_id,
                        status=AnalysisStatus.PENDING,
                        objective=job.configuration.objective,
                        timestamp=datetime.now()
                    )
                )
                
                cached_result = await self.cache_manager.retrieve_result(cache_key)
                if cached_result.success and cached_result.data:
                    # Return cached result immediately
                    job.status = JobStatus.COMPLETED
                    job.result = AnalysisResult(**cached_result.data)
                    self.completed_jobs.add(job.job_id)
                    
                    self.logger.info(f"Job {job.job_id} served from cache")
                    return job.job_id
            
            # Add job to storage and queue
            self.jobs[job.job_id] = job
            job.status = JobStatus.QUEUED
            
            # Insert based on priority if enabled
            if self.config.enable_priority_queue:
                self._insert_by_priority(job)
            else:
                self.job_queue.append(job.job_id)
            
            self.stats['jobs_submitted'] += 1
            
            self.logger.info(f"Job {job.job_id} submitted (priority: {job.priority.name})")
            return job.job_id
            
        except Exception as e:
            self.logger.error(f"Job submission failed: {e}")
            raise
    
    def _insert_by_priority(self, job: AnalysisJob):
        """Insert job into queue based on priority"""
        # Simple priority insertion (production would use a proper priority queue)
        inserted = False
        for i, queued_job_id in enumerate(self.job_queue):
            queued_job = self.jobs[queued_job_id]
            if job.priority.value > queued_job.priority.value:
                # Insert before lower priority job
                self.job_queue.insert(i, job.job_id)
                inserted = True
                break
        
        if not inserted:
            self.job_queue.append(job.job_id)
    
    async def _job_manager_loop(self):
        """Main job management loop"""
        try:
            while self.is_running:
                # Clean up completed worker tasks
                self._cleanup_worker_tasks()
                
                # Process job queue
                await self._process_job_queue()
                
                # Check for timed out jobs
                self._check_timeouts()
                
                # Update progress for running jobs
                if self.config.enable_progress_tracking:
                    self._update_job_progress()
                
                # Brief sleep to prevent tight loop
                await asyncio.sleep(0.1)
                
        except asyncio.CancelledError:
            self.logger.info("Job manager loop cancelled")
        except Exception as e:
            self.logger.error(f"Job manager loop error: {e}")
    
    def _cleanup_worker_tasks(self):
        """Clean up completed worker tasks"""
        completed_tasks = []
        for worker_id, task in self.worker_tasks.items():
            if task.done():
                completed_tasks.append(worker_id)
        
        for worker_id in completed_tasks:
            del self.worker_tasks[worker_id]
    
    async def _process_job_queue(self):
        """Process jobs from the queue"""
        if not self.job_queue:
            return
        
        # Find available workers
        available_workers = [
            worker for worker in self.workers.values()
            if worker.status == WorkerStatus.IDLE and worker.worker_id not in self.worker_tasks
        ]
        
        if not available_workers:
            return
        
        # Process jobs up to available worker count
        jobs_to_process = min(len(available_workers), len(self.job_queue))
        
        for _ in range(jobs_to_process):
            if not self.job_queue:
                break
            
            job_id = self.job_queue.popleft()
            job = self.jobs[job_id]
            
            # Check if job is ready to run (dependencies satisfied)
            if not job.is_ready_to_run(self.completed_jobs):
                # Put back at end of queue
                self.job_queue.append(job_id)
                continue
            
            # Assign worker
            worker = available_workers.pop(0)
            
            # Start job execution
            task = asyncio.create_task(self._execute_job_with_worker(worker, job))
            self.worker_tasks[worker.worker_id] = task
    
    async def _execute_job_with_worker(self, worker: AnalysisWorker, job: AnalysisJob):
        """Execute job with specified worker"""
        try:
            result = await worker.execute_job(job)
            
            # Update statistics
            if result.status == JobStatus.COMPLETED:
                self.stats['jobs_completed'] += 1
                self.completed_jobs.add(job.job_id)
            elif result.status == JobStatus.FAILED:
                self.stats['jobs_failed'] += 1
                
                # Handle retry logic
                if (self.config.auto_retry_failed and 
                    job.retry_count < self.config.max_retries):
                    job.retry_count += 1
                    job.status = JobStatus.QUEUED
                    self.job_queue.append(job.job_id)
                    self.logger.info(f"Retrying job {job.job_id} (attempt {job.retry_count + 1})")
            
            self.stats['total_execution_time'] += result.execution_time
            
            # Cache result if successful and caching enabled
            if (result.status == JobStatus.COMPLETED and 
                self.config.cache_results and 
                self.cache_manager and 
                result.result):
                try:
                    await self.cache_manager.store_result(result.result)
                except Exception as e:
                    self.logger.warning(f"Result caching failed: {e}")
            
        except Exception as e:
            self.logger.error(f"Job execution error: {e}")
    
    def _check_timeouts(self):
        """Check for timed out jobs"""
        for job in self.jobs.values():
            if job.status == JobStatus.RUNNING and job.is_expired():
                job.status = JobStatus.TIMEOUT
                self.stats['jobs_failed'] += 1
                self.logger.warning(f"Job {job.job_id} timed out")
    
    def _update_job_progress(self):
        """Update progress for running jobs"""
        # This would be called periodically to update job progress
        # Progress updates are handled by workers during job execution
        pass
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return {
            'job_id': job.job_id,
            'status': job.status.value,
            'priority': job.priority.name,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'assigned_worker': job.assigned_worker,
            'progress': asdict(job.progress),
            'retry_count': job.retry_count,
            'error_message': job.error_message
        }
    
    async def cancel_job(self, job_id: str) -> bool:
        """Cancel a job"""
        job = self.jobs.get(job_id)
        if not job:
            return False
        
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False
        
        job.status = JobStatus.CANCELLED
        
        # Remove from queue if queued
        if job_id in self.job_queue:
            self.job_queue.remove(job_id)
        
        # Cancel worker task if running
        if job.assigned_worker and job.assigned_worker in self.worker_tasks:
            task = self.worker_tasks[job.assigned_worker]
            task.cancel()
        
        self.logger.info(f"Job {job_id} cancelled")
        return True
    
    async def get_manager_statistics(self) -> Dict[str, Any]:
        """Get comprehensive job manager statistics"""
        uptime = datetime.now() - self.stats['start_time']
        
        # Worker statistics
        worker_stats = {}
        for worker_id, worker in self.workers.items():
            worker_stats[worker_id] = worker.get_worker_stats()
        
        # Job status breakdown
        status_counts = {}
        for status in JobStatus:
            status_counts[status.value] = sum(
                1 for job in self.jobs.values() if job.status == status
            )
        
        return {
            'manager_id': self.manager_id,
            'uptime_seconds': uptime.total_seconds(),
            'is_running': self.is_running,
            'configuration': asdict(self.config),
            'statistics': {
                **self.stats,
                'jobs_in_queue': len(self.job_queue),
                'active_workers': sum(1 for w in self.workers.values() if w.status == WorkerStatus.BUSY),
                'average_execution_time': (
                    self.stats['total_execution_time'] / max(1, self.stats['jobs_completed'])
                )
            },
            'job_status_breakdown': status_counts,
            'worker_statistics': worker_stats
        }

# Convenience functions
async def create_job_manager(max_workers: int = 4, 
                           enable_caching: bool = True) -> AnalysisJobManager:
    """Create and start a job manager"""
    config = JobConfiguration(
        max_workers=max_workers,
        enable_caching=enable_caching
    )
    
    from .caching import cache_manager
    manager = AnalysisJobManager(
        config=config,
        cache_manager=cache_manager if enable_caching else None
    )
    
    await manager.start()
    return manager

async def submit_analysis_job(job_manager: AnalysisJobManager,
                            data: Any,
                            objective: AnalysisObjective = AnalysisObjective.PID_TUNING,
                            priority: JobPriority = JobPriority.NORMAL,
                            **kwargs) -> str:
    """Convenience function to submit an analysis job"""
    from .framework import AnalysisConfiguration
    
    config = AnalysisConfiguration(objective=objective, **kwargs)
    job = AnalysisJob(
        job_id=str(uuid.uuid4()),
        configuration=config,
        data=data,
        priority=priority
    )
    
    return await job_manager.submit_job(job)

if __name__ == "__main__":
    # Demo and testing
    async def main():
        logger.info("🚀 Enhanced Control Loop Analysis Job Manager - Demo")
        
        try:
            # Create job manager
            job_manager = await create_job_manager(max_workers=2)
            
            # Create sample jobs
            sample_data = {
                'timestamp': list(range(100)),
                'CV': [50 + i * 0.1 for i in range(100)],
                'PV': [25 + i * 0.05 for i in range(100)]
            }
            
            # Submit jobs
            job_ids = []
            for i in range(5):
                job_id = await submit_analysis_job(
                    job_manager,
                    sample_data,
                    objective=AnalysisObjective.PID_TUNING,
                    priority=JobPriority.NORMAL if i < 3 else JobPriority.HIGH
                )
                job_ids.append(job_id)
                logger.info(f"Submitted job {i+1}: {job_id}")
            
            # Wait for jobs to complete
            logger.info("Waiting for jobs to complete...")
            await asyncio.sleep(5)
            
            # Check job statuses
            for job_id in job_ids:
                status = await job_manager.get_job_status(job_id)
                if status:
                    logger.info(f"Job {job_id}: {status['status']} ({status['progress']['progress_percent']:.1f}%)")
            
            # Get manager statistics
            stats = await job_manager.get_manager_statistics()
            logger.info(f"📊 Jobs completed: {stats['statistics']['jobs_completed']}")
            logger.info(f"📊 Jobs failed: {stats['statistics']['jobs_failed']}")
            logger.info(f"📊 Average execution time: {stats['statistics']['average_execution_time']:.2f}s")
            
            # Stop job manager
            await job_manager.stop()
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
        
        logger.info("✅ Job manager demo completed")
    
    asyncio.run(main()) 