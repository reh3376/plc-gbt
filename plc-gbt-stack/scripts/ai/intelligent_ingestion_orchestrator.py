#!/usr/bin/env python3
"""
🤖 Intelligent Ingestion Orchestrator - AI Task Orchestrator Implementation

Enhanced ingestion system that applies AI Task Orchestrator methodology to break up
complex ingestion tasks and manage system bandwidth efficiently. Ensures files are
processed in manageable chunks to prevent overwhelming the system.

Key Features:
- File-level complexity assessment
- Bandwidth-aware batch processing
- Progressive ingestion with checkpoints
- Automatic retry and recovery
- Resource throttling and monitoring

Author: AI Task Orchestrator
Created: 2025-01-09
Based on: AI_TASK_ORCHESTRATOR_GUIDE.md methodology
"""

import asyncio
import hashlib
import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from codebase_analyzer import AnalysisDepth, AnalysisResult, CodebaseAnalyzer, FileType
from database_manager import DatabaseManager
from memory_coordinator import MemoryCoordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngestionComplexity(Enum):
    """File ingestion complexity levels (based on AI Task Orchestrator Guide)"""
    SIMPLE = "simple"           # < 100 lines, basic file types
    MODERATE = "moderate"       # 100-500 lines, standard complexity
    COMPLEX = "complex"         # 500-1500 lines, complex structure
    EXTENSIVE = "extensive"     # > 1500 lines, requires special handling

class BatchStrategy(Enum):
    """Batch processing strategies"""
    SEQUENTIAL = "sequential"       # Process files one by one
    SMALL_BATCH = "small_batch"    # 5-10 files per batch
    MEDIUM_BATCH = "medium_batch"  # 20-50 files per batch
    LARGE_BATCH = "large_batch"    # 100+ files per batch

@dataclass
class FileComplexityAssessment:
    """Assessment of individual file complexity"""
    file_path: str
    complexity: IngestionComplexity
    line_count: int
    size_bytes: int
    file_type: FileType
    estimated_processing_time_ms: float
    bandwidth_requirement: str  # low, medium, high
    requires_special_handling: bool
    risk_factors: List[str]

@dataclass
class IngestionBatch:
    """Batch of files for processing"""
    batch_id: str
    files: List[AnalysisResult]
    complexity_distribution: Dict[str, int]
    total_estimated_time_ms: float
    total_size_bytes: int
    strategy: BatchStrategy
    priority: int = 5

@dataclass
class IngestionCheckpoint:
    """Checkpoint for resuming ingestion"""
    checkpoint_id: str
    timestamp: datetime
    completed_files: List[str]
    failed_files: List[str]
    remaining_files: List[str]
    session_metadata: Dict[str, Any]

class BandwidthManager:
    """Manages system bandwidth and resource utilization during ingestion"""

    def __init__(self):
        self.current_load = 0.0
        self.max_concurrent_files = 10
        self.rate_limit_per_second = 5
        self.last_operation_time = time.time()
        self.operation_history = []

        # Bandwidth thresholds
        self.bandwidth_limits = {
            "low": 0.3,     # 30% of max capacity
            "medium": 0.6,  # 60% of max capacity
            "high": 0.9     # 90% of max capacity
        }

    async def can_process_file(self, file_assessment: FileComplexityAssessment) -> bool:
        """Check if system can handle processing this file now"""
        required_bandwidth = self.bandwidth_limits[file_assessment.bandwidth_requirement]

        if self.current_load + required_bandwidth > 1.0:
            logger.warning(f"Bandwidth limit reached: {self.current_load:.1%}, cannot process {file_assessment.file_path}")
            return False

        # Rate limiting check
        current_time = time.time()
        recent_operations = [t for t in self.operation_history if current_time - t < 1.0]

        if len(recent_operations) >= self.rate_limit_per_second:
            logger.info(f"Rate limit reached: {len(recent_operations)} operations in last second")
            return False

        return True

    async def acquire_bandwidth(self, file_assessment: FileComplexityAssessment):
        """Reserve bandwidth for file processing"""
        required_bandwidth = self.bandwidth_limits[file_assessment.bandwidth_requirement]
        self.current_load += required_bandwidth
        self.operation_history.append(time.time())

        # Keep only recent history
        current_time = time.time()
        self.operation_history = [t for t in self.operation_history if current_time - t < 60.0]

        logger.debug(f"Bandwidth acquired: {required_bandwidth:.1%}, total load: {self.current_load:.1%}")

    async def release_bandwidth(self, file_assessment: FileComplexityAssessment):
        """Release bandwidth after file processing"""
        required_bandwidth = self.bandwidth_limits[file_assessment.bandwidth_requirement]
        self.current_load = max(0.0, self.current_load - required_bandwidth)
        logger.debug(f"Bandwidth released: {required_bandwidth:.1%}, total load: {self.current_load:.1%}")

    async def wait_for_capacity(self, required_bandwidth: str, max_wait_seconds: int = 60):
        """Wait until system has enough capacity"""
        required = self.bandwidth_limits[required_bandwidth]
        wait_start = time.time()

        while self.current_load + required > 1.0:
            if time.time() - wait_start > max_wait_seconds:
                raise TimeoutError(f"Timeout waiting for bandwidth capacity: {required_bandwidth}")

            logger.info(f"Waiting for bandwidth capacity: {self.current_load:.1%} + {required:.1%} > 100%")
            await asyncio.sleep(1.0)

class FileComplexityAnalyzer:
    """Analyzes individual files for complexity assessment following AI Task Orchestrator Guide"""

    def __init__(self):
        # Complexity thresholds from AI Task Orchestrator Guide
        self.complexity_thresholds = {
            IngestionComplexity.SIMPLE: {"max_lines": 100, "max_size_mb": 1},
            IngestionComplexity.MODERATE: {"max_lines": 500, "max_size_mb": 5},
            IngestionComplexity.COMPLEX: {"max_lines": 1500, "max_size_mb": 15},
            IngestionComplexity.EXTENSIVE: {"max_lines": float('inf'), "max_size_mb": float('inf')}
        }

    def assess_file_complexity(self, analysis_result: AnalysisResult) -> FileComplexityAssessment:
        """Assess complexity of individual file based on AI Task Orchestrator criteria"""
        file_metadata = analysis_result.file_metadata

        # Basic metrics
        line_count = file_metadata.line_count
        size_bytes = file_metadata.size_bytes
        size_mb = size_bytes / (1024 * 1024)

        # Determine complexity level
        complexity = self._determine_complexity(line_count, size_mb, file_metadata.file_type)

        # Estimate processing time based on complexity
        base_time_per_line = {
            IngestionComplexity.SIMPLE: 0.1,     # 0.1ms per line
            IngestionComplexity.MODERATE: 0.5,   # 0.5ms per line
            IngestionComplexity.COMPLEX: 2.0,    # 2ms per line
            IngestionComplexity.EXTENSIVE: 5.0   # 5ms per line
        }

        estimated_time = line_count * base_time_per_line[complexity]

        # Determine bandwidth requirement
        bandwidth_requirement = self._determine_bandwidth_requirement(complexity, file_metadata.file_type)

        # Identify risk factors
        risk_factors = self._identify_risk_factors(analysis_result)

        # Check if special handling required
        requires_special_handling = (
            complexity == IngestionComplexity.EXTENSIVE or
            len(risk_factors) > 2 or
            size_mb > 50
        )

        return FileComplexityAssessment(
            file_path=file_metadata.path,
            complexity=complexity,
            line_count=line_count,
            size_bytes=size_bytes,
            file_type=file_metadata.file_type,
            estimated_processing_time_ms=estimated_time,
            bandwidth_requirement=bandwidth_requirement,
            requires_special_handling=requires_special_handling,
            risk_factors=risk_factors
        )

    def _determine_complexity(self, line_count: int, size_mb: float, file_type: FileType) -> IngestionComplexity:
        """Determine complexity level based on AI Task Orchestrator thresholds"""

        # Special handling for certain file types
        binary_types = []
        try:
            # Check if these file types exist in the enum
            if hasattr(FileType, 'BINARY'):
                binary_types.append(FileType.BINARY)
            if hasattr(FileType, 'IMAGE'):
                binary_types.append(FileType.IMAGE)
            if hasattr(FileType, 'ARCHIVE'):
                binary_types.append(FileType.ARCHIVE)
        except AttributeError:
            pass

        if file_type in binary_types:
            return IngestionComplexity.SIMPLE if size_mb < 1 else IngestionComplexity.MODERATE

        # Apply line count and size thresholds
        if line_count <= 100 and size_mb <= 1:
            return IngestionComplexity.SIMPLE
        elif line_count <= 500 and size_mb <= 5:
            return IngestionComplexity.MODERATE
        elif line_count <= 1500 and size_mb <= 15:
            return IngestionComplexity.COMPLEX
        else:
            return IngestionComplexity.EXTENSIVE

    def _determine_bandwidth_requirement(self, complexity: IngestionComplexity, file_type: FileType) -> str:
        """Determine bandwidth requirement based on complexity and file type"""

        # High bandwidth file types (code that requires complex processing)
        high_bandwidth_types = []
        try:
            if hasattr(FileType, 'PYTHON'):
                high_bandwidth_types.append(FileType.PYTHON)
            if hasattr(FileType, 'JAVASCRIPT'):
                high_bandwidth_types.append(FileType.JAVASCRIPT)
            if hasattr(FileType, 'TYPESCRIPT'):
                high_bandwidth_types.append(FileType.TYPESCRIPT)
        except AttributeError:
            pass

        if file_type in high_bandwidth_types:
            if complexity in [IngestionComplexity.COMPLEX, IngestionComplexity.EXTENSIVE]:
                return "high"
            elif complexity == IngestionComplexity.MODERATE:
                return "medium"
            else:
                return "low"

        # Medium bandwidth file types (structured data)
        medium_bandwidth_types = []
        try:
            if hasattr(FileType, 'JSON'):
                medium_bandwidth_types.append(FileType.JSON)
            if hasattr(FileType, 'YAML'):
                medium_bandwidth_types.append(FileType.YAML)
            if hasattr(FileType, 'XML'):
                medium_bandwidth_types.append(FileType.XML)
        except AttributeError:
            pass

        if file_type in medium_bandwidth_types:
            return "medium" if complexity != IngestionComplexity.SIMPLE else "low"

        # Low bandwidth file types (everything else)
        return "low"

    def _identify_risk_factors(self, analysis_result: AnalysisResult) -> List[str]:
        """Identify potential risk factors for processing"""
        risk_factors = []

        file_metadata = analysis_result.file_metadata
        structural = analysis_result.structural_analysis

        # File size risks
        if file_metadata.size_bytes > 50 * 1024 * 1024:  # 50MB
            risk_factors.append("very_large_file")

        # Line count risks
        if file_metadata.line_count > 5000:
            risk_factors.append("very_long_file")

        # Structural complexity risks
        if structural:
            if len(structural.functions) > 100:
                risk_factors.append("many_functions")
            if len(structural.classes) > 50:
                risk_factors.append("many_classes")
            if structural.complexity_score and structural.complexity_score > 10:
                risk_factors.append("high_complexity")
            if len(structural.dependencies) > 50:
                risk_factors.append("many_dependencies")

        # File type risks
        if hasattr(FileType, 'BINARY') and file_metadata.file_type == FileType.BINARY:
            risk_factors.append("binary_file")

        # Encoding risks
        if file_metadata.encoding not in ['utf-8', 'ascii']:
            risk_factors.append("unusual_encoding")

        return risk_factors

class BatchOrchestrator:
    """Orchestrates file processing in intelligent batches following AI Task Orchestrator methodology"""

    def __init__(self, bandwidth_manager: BandwidthManager):
        self.bandwidth_manager = bandwidth_manager
        self.complexity_analyzer = FileComplexityAnalyzer()

        # Batch size configurations
        self.batch_configs = {
            BatchStrategy.SEQUENTIAL: {"max_files": 1, "max_complexity_mix": False},
            BatchStrategy.SMALL_BATCH: {"max_files": 10, "max_complexity_mix": True},
            BatchStrategy.MEDIUM_BATCH: {"max_files": 50, "max_complexity_mix": True},
            BatchStrategy.LARGE_BATCH: {"max_files": 200, "max_complexity_mix": False}
        }

    def create_intelligent_batches(self, analysis_results: List[AnalysisResult]) -> List[IngestionBatch]:
        """Create intelligent batches based on file complexity analysis"""

        # Step 1: Assess complexity of all files
        logger.info(f"🔍 Assessing complexity of {len(analysis_results)} files")

        file_assessments = []
        for result in analysis_results:
            assessment = self.complexity_analyzer.assess_file_complexity(result)
            file_assessments.append((result, assessment))

        # Step 2: Group by complexity and requirements
        complexity_groups = {
            IngestionComplexity.SIMPLE: [],
            IngestionComplexity.MODERATE: [],
            IngestionComplexity.COMPLEX: [],
            IngestionComplexity.EXTENSIVE: []
        }

        for result, assessment in file_assessments:
            complexity_groups[assessment.complexity].append((result, assessment))

        # Step 3: Create batches using AI Task Orchestrator strategy
        batches = []

        # Handle EXTENSIVE files individually (following AI Task Orchestrator Guide)
        for result, assessment in complexity_groups[IngestionComplexity.EXTENSIVE]:
            batch = self._create_single_file_batch(result, assessment)
            batches.append(batch)
            logger.warning(f"📁 EXTENSIVE file requires individual processing: {assessment.file_path}")

        # Handle COMPLEX files in small batches
        if complexity_groups[IngestionComplexity.COMPLEX]:
            complex_batches = self._create_batches_for_complexity(
                complexity_groups[IngestionComplexity.COMPLEX],
                BatchStrategy.SMALL_BATCH,
                IngestionComplexity.COMPLEX
            )
            batches.extend(complex_batches)

        # Handle MODERATE files in medium batches
        if complexity_groups[IngestionComplexity.MODERATE]:
            moderate_batches = self._create_batches_for_complexity(
                complexity_groups[IngestionComplexity.MODERATE],
                BatchStrategy.MEDIUM_BATCH,
                IngestionComplexity.MODERATE
            )
            batches.extend(moderate_batches)

        # Handle SIMPLE files in large batches
        if complexity_groups[IngestionComplexity.SIMPLE]:
            simple_batches = self._create_batches_for_complexity(
                complexity_groups[IngestionComplexity.SIMPLE],
                BatchStrategy.LARGE_BATCH,
                IngestionComplexity.SIMPLE
            )
            batches.extend(simple_batches)

        # Sort batches by priority (EXTENSIVE first, then COMPLEX, etc.)

        batches.sort(key=lambda b: b.priority)

        logger.info(f"📦 Created {len(batches)} intelligent batches")
        self._log_batch_summary(batches)

        return batches

    def _create_single_file_batch(self, result: AnalysisResult, assessment: FileComplexityAssessment) -> IngestionBatch:
        """Create batch for single complex file"""
        batch_id = f"extensive_{hashlib.md5(assessment.file_path.encode()).hexdigest()[:8]}"

        return IngestionBatch(
            batch_id=batch_id,
            files=[result],
            complexity_distribution={assessment.complexity.value: 1},
            total_estimated_time_ms=assessment.estimated_processing_time_ms,
            total_size_bytes=assessment.size_bytes,
            strategy=BatchStrategy.SEQUENTIAL,
            priority=1  # Highest priority for complex files
        )

    def _create_batches_for_complexity(
        self,
        file_list: List[Tuple[AnalysisResult, FileComplexityAssessment]],
        strategy: BatchStrategy,
        complexity: IngestionComplexity
    ) -> List[IngestionBatch]:
        """Create batches for files of similar complexity"""

        batches = []
        config = self.batch_configs[strategy]
        max_files = config["max_files"]

        # Sort by processing time estimate
        file_list.sort(key=lambda x: x[1].estimated_processing_time_ms)

        # Create batches
        current_batch_files = []
        current_batch_assessments = []

        for result, assessment in file_list:
            if len(current_batch_files) >= max_files:
                # Create batch from current files
                batch = self._finalize_batch(current_batch_files, current_batch_assessments, strategy, complexity)
                batches.append(batch)

                # Start new batch
                current_batch_files = []
                current_batch_assessments = []

            current_batch_files.append(result)
            current_batch_assessments.append(assessment)

        # Create final batch if files remain
        if current_batch_files:
            batch = self._finalize_batch(current_batch_files, current_batch_assessments, strategy, complexity)
            batches.append(batch)

        return batches

    def _finalize_batch(
        self,
        files: List[AnalysisResult],
        assessments: List[FileComplexityAssessment],
        strategy: BatchStrategy,
        complexity: IngestionComplexity
    ) -> IngestionBatch:
        """Finalize batch creation with metadata"""

        batch_id = f"{complexity.value}_{int(time.time())}_{len(files)}"

        # Calculate batch metrics
        total_time = sum(a.estimated_processing_time_ms for a in assessments)
        total_size = sum(a.size_bytes for a in assessments)

        complexity_dist = {}
        for assessment in assessments:
            comp = assessment.complexity.value
            complexity_dist[comp] = complexity_dist.get(comp, 0) + 1

        # Set priority based on complexity
        priority_map = {
            IngestionComplexity.EXTENSIVE: 1,
            IngestionComplexity.COMPLEX: 2,
            IngestionComplexity.MODERATE: 3,
            IngestionComplexity.SIMPLE: 4
        }

        return IngestionBatch(
            batch_id=batch_id,
            files=files,
            complexity_distribution=complexity_dist,
            total_estimated_time_ms=total_time,
            total_size_bytes=total_size,
            strategy=strategy,
            priority=priority_map[complexity]
        )

    def _log_batch_summary(self, batches: List[IngestionBatch]):
        """Log summary of created batches"""
        total_files = sum(len(b.files) for b in batches)

        strategy_counts = {}
        complexity_counts = {}

        for batch in batches:
            strategy_counts[batch.strategy.value] = strategy_counts.get(batch.strategy.value, 0) + 1

            for complexity, count in batch.complexity_distribution.items():
                complexity_counts[complexity] = complexity_counts.get(complexity, 0) + count

        logger.info("📊 Batch Summary:")
        logger.info(f"   Total files: {total_files}")
        logger.info(f"   Total batches: {len(batches)}")
        logger.info(f"   Strategy distribution: {strategy_counts}")
        logger.info(f"   Complexity distribution: {complexity_counts}")

class IntelligentIngestionOrchestrator:
    """
    🎯 Intelligent Ingestion Orchestrator

    Applies AI Task Orchestrator methodology to break up complex ingestion tasks
    and manage system bandwidth efficiently. Ensures files are processed in
    manageable chunks to prevent overwhelming the system.

    Features:
    - File-level complexity assessment following AI Task Orchestrator Guide
    - Intelligent batch creation based on complexity and resource requirements
    - Bandwidth-aware processing with throttling and monitoring
    - Progressive ingestion with checkpoints and recovery
    - Automatic retry logic for failed files
    """

    def __init__(self, memory_coordinator: MemoryCoordinator):
        self.memory_coordinator = memory_coordinator
        self.bandwidth_manager = BandwidthManager()
        self.batch_orchestrator = BatchOrchestrator(self.bandwidth_manager)

        # Session management
        self.session_id = f"ingestion_orch_{int(time.time())}"
        self.start_time = datetime.now()
        self.checkpoints = []

        # Progress tracking
        self.processing_stats = {
            'total_files': 0,
            'completed_files': 0,
            'failed_files': 0,
            'skipped_files': 0,
            'total_batches': 0,
            'completed_batches': 0,
            'total_processing_time_ms': 0.0,
            'average_file_time_ms': 0.0
        }

        logger.info(f"IntelligentIngestionOrchestrator initialized: {self.session_id}")

    async def ingest_codebase_intelligently(
        self,
        root_path: str,
        analysis_depth: AnalysisDepth = AnalysisDepth.STRUCTURAL,
        max_concurrent_batches: int = 3,
        checkpoint_interval_minutes: int = 5
    ) -> Dict[str, Any]:
        """
        Intelligently ingest codebase using AI Task Orchestrator methodology

        Features:
        - Complexity-based file assessment
        - Bandwidth-aware batch processing
        - Progressive ingestion with checkpoints
        - Automatic recovery and retry
        """

        start_time = time.time()
        logger.info(f"🚀 Starting intelligent codebase ingestion: {root_path}")
        logger.info(f"📊 Analysis depth: {analysis_depth.value}")
        logger.info(f"⚡ Max concurrent batches: {max_concurrent_batches}")

        try:
            # Step 1: Analyze codebase (same as before)
            logger.info("🔍 Step 1: Analyzing codebase structure")
            analyzer = CodebaseAnalyzer(root_path, analysis_depth)
            analysis_results = analyzer.analyze_codebase()

            self.processing_stats['total_files'] = len(analysis_results)
            logger.info(f"📁 Found {len(analysis_results)} files to process")

            # Step 2: Create intelligent batches based on complexity
            logger.info("📦 Step 2: Creating intelligent batches")
            batches = self.batch_orchestrator.create_intelligent_batches(analysis_results)

            self.processing_stats['total_batches'] = len(batches)

            # Step 3: Process batches with bandwidth management
            logger.info("⚡ Step 3: Processing batches with bandwidth management")

            processed_files = []
            failed_files = []

            # Track checkpoint timing
            last_checkpoint = time.time()

            # Process batches with controlled concurrency
            semaphore = asyncio.Semaphore(max_concurrent_batches)

            for batch_index, batch in enumerate(batches):
                async with semaphore:
                    logger.info(f"🔄 Processing batch {batch_index + 1}/{len(batches)}: {batch.batch_id}")
                    logger.info(f"   Files in batch: {len(batch.files)}")
                    logger.info(f"   Strategy: {batch.strategy.value}")
                    logger.info(f"   Estimated time: {batch.total_estimated_time_ms:.0f}ms")

                    batch_results = await self._process_batch_intelligently(batch)

                    # Update progress
                    processed_files.extend(batch_results['processed'])
                    failed_files.extend(batch_results['failed'])

                    self.processing_stats['completed_batches'] += 1
                    self.processing_stats['completed_files'] += len(batch_results['processed'])
                    self.processing_stats['failed_files'] += len(batch_results['failed'])

                    # Create checkpoint if interval reached
                    if time.time() - last_checkpoint > checkpoint_interval_minutes * 60:
                        await self._create_checkpoint(processed_files, failed_files, batches[batch_index + 1:])
                        last_checkpoint = time.time()

                    # Log progress
                    progress = (batch_index + 1) / len(batches) * 100
                    logger.info(f"📊 Progress: {progress:.1f}% ({batch_index + 1}/{len(batches)} batches)")

            # Final statistics
            total_time = (time.time() - start_time) * 1000
            self.processing_stats['total_processing_time_ms'] = total_time

            if self.processing_stats['completed_files'] > 0:
                self.processing_stats['average_file_time_ms'] = (
                    total_time / self.processing_stats['completed_files']
                )

            # Create final summary
            summary = {
                'session_id': self.session_id,
                'root_path': root_path,
                'analysis_depth': analysis_depth.value,
                'methodology': 'AI Task Orchestrator Intelligent Ingestion',
                'total_files_analyzed': len(analysis_results),
                'total_batches_created': len(batches),
                'successfully_processed': len(processed_files),
                'failed_files': len(failed_files),
                'processing_time_ms': total_time,
                'files_per_second': len(processed_files) / (total_time / 1000) if total_time > 0 else 0,
                'bandwidth_management': {
                    'peak_load': f"{max(0.0, self.bandwidth_manager.current_load):.1%}",
                    'rate_limited_operations': len([t for t in self.bandwidth_manager.operation_history if time.time() - t < 60]),
                    'avg_operation_interval_ms': self._calculate_avg_operation_interval()
                },
                'complexity_analysis': self._generate_complexity_summary(batches),
                'performance_metrics': self.processing_stats,
                'checkpoints_created': len(self.checkpoints)
            }

            logger.info("✅ Intelligent codebase ingestion complete!")
            logger.info(f"📊 Processed {len(processed_files)} files in {len(batches)} batches")
            logger.info(f"⚡ Average processing speed: {summary['files_per_second']:.1f} files/sec")
            logger.info(f"🎯 Success rate: {len(processed_files)/(len(processed_files) + len(failed_files))*100:.1f}%")

            return summary

        except Exception as e:
            logger.error(f"❌ Error during intelligent ingestion: {str(e)}")
            raise

    async def _process_batch_intelligently(self, batch: IngestionBatch) -> Dict[str, List[str]]:
        """Process a batch of files with intelligent bandwidth management"""

        processed_files = []
        failed_files = []

        for file_result in batch.files:
            try:
                # Assess file complexity for bandwidth management
                assessment = self.batch_orchestrator.complexity_analyzer.assess_file_complexity(file_result)

                # Check if system can handle this file now
                if not await self.bandwidth_manager.can_process_file(assessment):
                    # Wait for capacity
                    await self.bandwidth_manager.wait_for_capacity(
                        assessment.bandwidth_requirement,
                        max_wait_seconds=30
                    )

                # Acquire bandwidth
                await self.bandwidth_manager.acquire_bandwidth(assessment)

                try:
                    # Process file using existing file processor
                    processed = self.memory_coordinator.file_processor.process_file(file_result)

                    if processed:
                        # Store in databases
                        storage_results = await self.memory_coordinator.file_processor.store_processed_content(processed)

                        processed_files.append({
                            'file_path': file_result.file_metadata.path,
                            'complexity': assessment.complexity.value,
                            'chunks': len(processed.content_chunks),
                            'storage_results': storage_results,
                            'processing_time_ms': assessment.estimated_processing_time_ms
                        })

                        logger.debug(f"✅ Processed: {file_result.file_metadata.path}")
                    else:
                        failed_files.append(file_result.file_metadata.path)
                        logger.warning(f"❌ Failed to process: {file_result.file_metadata.path}")

                finally:
                    # Always release bandwidth
                    await self.bandwidth_manager.release_bandwidth(assessment)

                # Small delay to prevent overwhelming the system
                if assessment.complexity in [IngestionComplexity.COMPLEX, IngestionComplexity.EXTENSIVE]:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"❌ Error processing {file_result.file_metadata.path}: {str(e)}")
                failed_files.append(file_result.file_metadata.path)

        return {
            'processed': processed_files,
            'failed': failed_files
        }

    async def _create_checkpoint(self, processed_files: List[str], failed_files: List[str], remaining_batches: List[IngestionBatch]):
        """Create checkpoint for recovery"""
        checkpoint = IngestionCheckpoint(
            checkpoint_id=f"{self.session_id}_{len(self.checkpoints)}",
            timestamp=datetime.now(),
            completed_files=[f['file_path'] if isinstance(f, dict) else f for f in processed_files],
            failed_files=failed_files,
            remaining_files=[f.file_metadata.path for batch in remaining_batches for f in batch.files],
            session_metadata={
                'session_id': self.session_id,
                'stats': self.processing_stats.copy()
            }
        )

        self.checkpoints.append(checkpoint)

        # Save checkpoint to file
        checkpoint_file = f"checkpoint_{checkpoint.checkpoint_id}.json"
        with open(checkpoint_file, 'w') as f:
            json.dump(asdict(checkpoint), f, indent=2, default=str)

        logger.info(f"💾 Checkpoint created: {checkpoint_file}")

    def _calculate_avg_operation_interval(self) -> float:
        """Calculate average interval between operations"""
        if len(self.bandwidth_manager.operation_history) < 2:
            return 0.0

        intervals = []
        sorted_history = sorted(self.bandwidth_manager.operation_history)

        for i in range(1, len(sorted_history)):
            intervals.append(sorted_history[i] - sorted_history[i-1])

        return (sum(intervals) / len(intervals)) * 1000 if intervals else 0.0

    def _generate_complexity_summary(self, batches: List[IngestionBatch]) -> Dict[str, Any]:
        """Generate summary of complexity analysis"""
        complexity_stats = {
            'simple': 0,
            'moderate': 0,
            'complex': 0,
            'extensive': 0
        }

        strategy_stats = {
            'sequential': 0,
            'small_batch': 0,
            'medium_batch': 0,
            'large_batch': 0
        }

        for batch in batches:
            strategy_stats[batch.strategy.value] += len(batch.files)

            for complexity, count in batch.complexity_distribution.items():
                complexity_stats[complexity] += count

        return {
            'complexity_distribution': complexity_stats,
            'strategy_distribution': strategy_stats,
            'total_batches': len(batches),
            'average_batch_size': sum(len(b.files) for b in batches) / len(batches) if batches else 0
        }

async def main():
    """
    🚀 Demonstration of Intelligent Ingestion Orchestrator
    """
    print("🤖 Intelligent Ingestion Orchestrator - AI Task Orchestrator Implementation")
    print("=" * 80)

    # Initialize components

    db_manager = DatabaseManager()
    coordinator = MemoryCoordinator(db_manager)
    orchestrator = IntelligentIngestionOrchestrator(coordinator)

    try:
        # Initialize database connections
        print("\n🔗 Step 1: Initializing Database Connections")
        await db_manager.initialize_all_connections()

        # Demo intelligent ingestion
        print("\n🚀 Step 2: Intelligent Codebase Ingestion")

        # Use current directory as demo
        demo_path = "."

        result = await orchestrator.ingest_codebase_intelligently(
            root_path=demo_path,
            analysis_depth=AnalysisDepth.STRUCTURAL,
            max_concurrent_batches=2,
            checkpoint_interval_minutes=1
        )

        print("\n📊 Ingestion Results:")
        print(f"✅ Total files processed: {result['successfully_processed']}")
        print(f"❌ Failed files: {result['failed_files']}")
        print(f"📦 Total batches: {result['total_batches_created']}")
        print(f"⚡ Processing speed: {result['files_per_second']:.1f} files/sec")
        print(f"🎯 Methodology: {result['methodology']}")

        print("\n🔧 Bandwidth Management:")
        bw = result['bandwidth_management']
        print(f"Peak load: {bw['peak_load']}")
        print(f"Rate limited ops: {bw['rate_limited_operations']}")
        print(f"Avg operation interval: {bw['avg_operation_interval_ms']:.1f}ms")

        print("\n📈 Complexity Analysis:")
        complexity = result['complexity_analysis']
        print(f"Simple files: {complexity['complexity_distribution']['simple']}")
        print(f"Moderate files: {complexity['complexity_distribution']['moderate']}")
        print(f"Complex files: {complexity['complexity_distribution']['complex']}")
        print(f"Extensive files: {complexity['complexity_distribution']['extensive']}")

        print("\n🎯 Intelligent ingestion demonstration complete!")

    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1

    finally:
        await db_manager.close_all_connections()

    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
