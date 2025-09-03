#!/usr/bin/env python3
"""
Phase 23.4.2: Adaptive Learning Systems
=======================================

Advanced self-improving machine learning system with continuous training,
pattern recognition, and knowledge adaptation for industrial control applications.
Provides intelligent model evolution, automated retraining, and adaptive
optimization based on real-time performance feedback.

This module builds upon Phase 23.4.1 Predictive Analysis Engine to provide
self-improving capabilities that enhance prediction accuracy and system
performance through continuous learning and adaptation.

Components:
- AdaptiveLearningEngine: Core adaptive learning orchestration system
- ContinuousTrainer: Automated model retraining and optimization
- PatternRecognitionEngine: Advanced pattern detection and classification
- ModelEvolutionSystem: Dynamic model updating and version management
- KnowledgeAdaptationFramework: Intelligent knowledge base evolution
- PerformanceMonitor: Real-time model performance tracking and analysis

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 23.4.2 - Adaptive Learning Systems
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import logging
import time
import warnings
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

warnings.filterwarnings('ignore')

# Import from Phase 23.4.1
try:
    from predictive_engine import (
        ModelType,
        PredictionConfidence,
        PredictionRequest,
        PredictionResult,
        PredictionType,
        PredictiveEngine,
    )
except ImportError:
    # Fallback for testing
    logging.warning("Phase 23.4.1 components not available - using mock classes")

# Configure logging
logger = logging.getLogger(__name__)

class AdaptationType(Enum):
    """Types of adaptive learning"""
    CONTINUOUS_TRAINING = "continuous_training"
    MODEL_EVOLUTION = "model_evolution"
    PATTERN_ADAPTATION = "pattern_adaptation"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    KNOWLEDGE_EVOLUTION = "knowledge_evolution"
    HYPERPARAMETER_TUNING = "hyperparameter_tuning"
    FEATURE_ADAPTATION = "feature_adaptation"

class LearningStrategy(Enum):
    """Learning strategy types"""
    INCREMENTAL = "incremental"          # Add new data gradually
    BATCH_RETRAIN = "batch_retrain"      # Retrain with batches
    ONLINE_LEARNING = "online_learning"  # Real-time learning
    ENSEMBLE_UPDATE = "ensemble_update"  # Update ensemble models
    TRANSFER_LEARNING = "transfer_learning"  # Transfer knowledge
    REINFORCEMENT = "reinforcement"      # Reward-based learning

class AdaptationTrigger(Enum):
    """Triggers for adaptive learning"""
    PERFORMANCE_DEGRADATION = "performance_degradation"
    NEW_PATTERN_DETECTED = "new_pattern_detected"
    DATA_DRIFT_DETECTED = "data_drift_detected"
    TIME_BASED = "time_based"
    ERROR_THRESHOLD = "error_threshold"
    USER_REQUEST = "user_request"
    EXTERNAL_SIGNAL = "external_signal"

class LearningQuality(Enum):
    """Quality levels of learning adaptation"""
    EXCELLENT = "excellent"      # > 95% improvement
    VERY_GOOD = "very_good"      # 85-95% improvement
    GOOD = "good"                # 75-85% improvement
    ACCEPTABLE = "acceptable"    # 65-75% improvement
    POOR = "poor"                # 50-65% improvement
    FAILING = "failing"          # < 50% improvement

@dataclass
class LearningRequest:
    """Request for adaptive learning"""
    request_id: str
    adaptation_type: AdaptationType
    learning_strategy: LearningStrategy
    trigger: AdaptationTrigger
    target_models: List[str]
    data_source: str
    performance_threshold: float

    # Learning parameters
    learning_rate: float = 0.01
    batch_size: int = 32
    max_iterations: int = 100
    convergence_threshold: float = 0.001

    # Context and configuration
    context: Dict[str, Any] = field(default_factory=dict)
    configuration: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    requested_by: str = "system"
    priority: int = 1  # 1=low, 5=critical

@dataclass
class LearningResult:
    """Result of adaptive learning process"""
    request_id: str
    adaptation_type: AdaptationType
    learning_strategy: LearningStrategy
    models_updated: List[str]

    # Performance metrics
    initial_performance: Dict[str, float]
    final_performance: Dict[str, float]
    improvement_metrics: Dict[str, float]
    learning_quality: LearningQuality

    # Learning details
    iterations_completed: int
    convergence_achieved: bool
    training_time: float
    data_points_processed: int

    # Adaptation insights
    patterns_discovered: List[str]
    knowledge_updates: List[str]
    recommendations: List[str]

    # Metadata
    execution_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

class PerformanceMonitor:
    """Real-time model performance tracking and analysis"""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.performance_history = defaultdict(lambda: deque(maxlen=window_size))
        self.baseline_metrics = {}
        self.drift_detectors = {}
        self.alert_thresholds = {
            'accuracy_drop': 0.05,      # 5% accuracy drop
            'error_increase': 0.10,     # 10% error increase
            'drift_score': 0.15         # 15% data drift
        }

    def record_performance(self, model_id: str, metrics: Dict[str, float], timestamp: datetime = None):
        """Record performance metrics for a model"""
        if timestamp is None:
            timestamp = datetime.now()

        performance_record = {
            'timestamp': timestamp,
            'metrics': metrics.copy(),
            'model_id': model_id
        }

        self.performance_history[model_id].append(performance_record)

        # Update baseline if this is the first record or significantly better
        if model_id not in self.baseline_metrics:
            self.baseline_metrics[model_id] = metrics.copy()
        else:
            self._update_baseline_if_improved(model_id, metrics)

        logger.debug(f"Recorded performance for {model_id}: {metrics}")

    def detect_performance_degradation(self, model_id: str) -> Dict[str, Any]:
        """Detect if model performance has degraded significantly"""
        if model_id not in self.performance_history or len(self.performance_history[model_id]) < 5:
            return {"degradation_detected": False, "reason": "insufficient_data"}

        recent_records = list(self.performance_history[model_id])[-10:]  # Last 10 records
        baseline = self.baseline_metrics.get(model_id, {})

        degradation_signals = []

        for metric_name in baseline:
            if metric_name in ['accuracy', 'precision', 'recall', 'f1_score']:
                # Higher is better metrics
                recent_avg = np.mean([r['metrics'].get(metric_name, 0) for r in recent_records])
                baseline_value = baseline[metric_name]

                if baseline_value > 0:
                    degradation_ratio = (baseline_value - recent_avg) / baseline_value
                    if degradation_ratio > self.alert_thresholds['accuracy_drop']:
                        degradation_signals.append({
                            'metric': metric_name,
                            'baseline': baseline_value,
                            'recent': recent_avg,
                            'degradation': degradation_ratio
                        })

            elif metric_name in ['mse', 'mae', 'rmse', 'error_rate']:
                # Lower is better metrics
                recent_avg = np.mean([r['metrics'].get(metric_name, float('inf')) for r in recent_records])
                baseline_value = baseline[metric_name]

                if baseline_value > 0:
                    increase_ratio = (recent_avg - baseline_value) / baseline_value
                    if increase_ratio > self.alert_thresholds['error_increase']:
                        degradation_signals.append({
                            'metric': metric_name,
                            'baseline': baseline_value,
                            'recent': recent_avg,
                            'increase': increase_ratio
                        })

        return {
            "degradation_detected": len(degradation_signals) > 0,
            "signals": degradation_signals,
            "severity": "high" if len(degradation_signals) > 2 else "medium" if degradation_signals else "low"
        }

    def detect_data_drift(self, model_id: str, new_data: np.ndarray) -> Dict[str, Any]:
        """Detect data drift using statistical methods"""
        if model_id not in self.drift_detectors:
            # Initialize drift detector with historical data
            self.drift_detectors[model_id] = self._initialize_drift_detector(model_id)

        drift_detector = self.drift_detectors[model_id]

        # Simple drift detection using distribution comparison
        if 'reference_stats' in drift_detector:
            new_stats = {
                'mean': np.mean(new_data, axis=0) if new_data.ndim > 1 else np.mean(new_data),
                'std': np.std(new_data, axis=0) if new_data.ndim > 1 else np.std(new_data),
                'min': np.min(new_data, axis=0) if new_data.ndim > 1 else np.min(new_data),
                'max': np.max(new_data, axis=0) if new_data.ndim > 1 else np.max(new_data)
            }

            reference_stats = drift_detector['reference_stats']

            # Calculate drift score
            drift_scores = []
            for stat_name in ['mean', 'std']:
                if isinstance(new_stats[stat_name], np.ndarray):
                    # Multi-dimensional data
                    for i in range(len(new_stats[stat_name])):
                        ref_val = reference_stats[stat_name][i] if isinstance(reference_stats[stat_name], np.ndarray) else reference_stats[stat_name]
                        new_val = new_stats[stat_name][i]
                        if ref_val != 0:
                            drift_scores.append(abs(new_val - ref_val) / abs(ref_val))
                else:
                    # Single-dimensional data
                    ref_val = reference_stats[stat_name]
                    new_val = new_stats[stat_name]
                    if ref_val != 0:
                        drift_scores.append(abs(new_val - ref_val) / abs(ref_val))

            avg_drift_score = np.mean(drift_scores) if drift_scores else 0.0

            return {
                "drift_detected": avg_drift_score > self.alert_thresholds['drift_score'],
                "drift_score": float(avg_drift_score),
                "new_stats": new_stats,
                "reference_stats": reference_stats,
                "severity": "high" if avg_drift_score > 0.3 else "medium" if avg_drift_score > 0.15 else "low"
            }

        return {"drift_detected": False, "reason": "no_reference_data"}

    def _update_baseline_if_improved(self, model_id: str, new_metrics: Dict[str, float]):
        """Update baseline metrics if new performance is significantly better"""
        baseline = self.baseline_metrics[model_id]
        improvement_threshold = 0.02  # 2% improvement threshold

        significant_improvement = False

        for metric_name, new_value in new_metrics.items():
            if metric_name in baseline:
                baseline_value = baseline[metric_name]

                if metric_name in ['accuracy', 'precision', 'recall', 'f1_score']:
                    # Higher is better
                    improvement = (new_value - baseline_value) / baseline_value if baseline_value > 0 else 0
                    if improvement > improvement_threshold:
                        significant_improvement = True
                elif metric_name in ['mse', 'mae', 'rmse', 'error_rate']:
                    # Lower is better
                    improvement = (baseline_value - new_value) / baseline_value if baseline_value > 0 else 0
                    if improvement > improvement_threshold:
                        significant_improvement = True

        if significant_improvement:
            self.baseline_metrics[model_id] = new_metrics.copy()
            logger.info(f"Updated baseline metrics for {model_id} due to significant improvement")

    def _initialize_drift_detector(self, model_id: str) -> Dict[str, Any]:
        """Initialize drift detector for a model"""
        # In a real implementation, this would use historical training data
        return {
            'reference_stats': {},
            'detection_method': 'statistical',
            'initialized_at': datetime.now()
        }

    def get_performance_summary(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a model"""
        if model_id not in self.performance_history:
            return {"error": "no_data_available"}

        records = list(self.performance_history[model_id])
        recent_records = records[-10:] if len(records) >= 10 else records

        # Calculate trends
        trends = {}
        if len(records) > 1:
            for metric_name in records[0]['metrics']:
                values = [r['metrics'].get(metric_name, 0) for r in records]
                if len(values) > 1:
                    # Simple linear trend
                    x = np.arange(len(values))
                    coeffs = np.polyfit(x, values, 1)
                    trends[metric_name] = {
                        'slope': float(coeffs[0]),
                        'direction': 'improving' if coeffs[0] > 0 else 'degrading' if coeffs[0] < 0 else 'stable'
                    }

        # Calculate recent performance
        recent_performance = {}
        if recent_records:
            for metric_name in recent_records[0]['metrics']:
                values = [r['metrics'].get(metric_name, 0) for r in recent_records]
                recent_performance[metric_name] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }

        return {
            'model_id': model_id,
            'total_records': len(records),
            'recent_performance': recent_performance,
            'trends': trends,
            'baseline_metrics': self.baseline_metrics.get(model_id, {}),
            'last_update': records[-1]['timestamp'].isoformat() if records else None
        }

class ContinuousTrainer:
    """Automated model retraining and optimization system"""

    def __init__(self, predictive_engine):
        self.predictive_engine = predictive_engine
        self.training_queue = asyncio.Queue()
        self.active_training = {}
        self.training_history = {}
        self.model_versions = defaultdict(int)

    async def schedule_training(self, learning_request: LearningRequest) -> str:
        """Schedule a model for retraining"""
        training_id = f"train_{learning_request.request_id}_{int(time.time())}"

        training_task = {
            'training_id': training_id,
            'request': learning_request,
            'status': 'queued',
            'created_at': datetime.now(),
            'estimated_duration': self._estimate_training_duration(learning_request)
        }

        await self.training_queue.put(training_task)
        self.active_training[training_id] = training_task

        logger.info(f"Scheduled training {training_id} for models: {learning_request.target_models}")
        return training_id

    async def execute_continuous_training(self, learning_request: LearningRequest) -> LearningResult:
        """Execute continuous training for specified models"""
        start_time = time.time()

        try:
            # Load training data
            training_data = await self._load_training_data(learning_request)

            # Validate data quality
            data_quality = await self._validate_training_data(training_data, learning_request)

            if not data_quality['valid']:
                raise ValueError(f"Training data quality issues: {data_quality['issues']}")

            # Get initial performance baselines
            initial_performance = await self._evaluate_current_models(learning_request.target_models)

            # Execute learning strategy
            training_results = await self._execute_learning_strategy(
                learning_request, training_data, initial_performance
            )

            # Evaluate updated models
            final_performance = await self._evaluate_updated_models(learning_request.target_models)

            # Calculate improvement metrics
            improvement_metrics = self._calculate_improvement_metrics(
                initial_performance, final_performance
            )

            # Determine learning quality
            learning_quality = self._assess_learning_quality(improvement_metrics)

            # Generate insights and recommendations
            insights = self._generate_learning_insights(training_results, improvement_metrics)
            recommendations = self._generate_learning_recommendations(learning_quality, insights)

            execution_time = time.time() - start_time

            result = LearningResult(
                request_id=learning_request.request_id,
                adaptation_type=learning_request.adaptation_type,
                learning_strategy=learning_request.learning_strategy,
                models_updated=learning_request.target_models,
                initial_performance=initial_performance,
                final_performance=final_performance,
                improvement_metrics=improvement_metrics,
                learning_quality=learning_quality,
                iterations_completed=training_results.get('iterations', 0),
                convergence_achieved=training_results.get('converged', False),
                training_time=training_results.get('training_time', 0.0),
                data_points_processed=len(training_data),
                patterns_discovered=insights.get('patterns', []),
                knowledge_updates=insights.get('knowledge_updates', []),
                recommendations=recommendations,
                execution_time=execution_time
            )

            # Store training history
            self.training_history[learning_request.request_id] = result

            logger.info(f"Continuous training completed: {learning_quality.value} quality, {len(learning_request.target_models)} models updated")

            return result

        except Exception as e:
            logger.error(f"Continuous training failed: {e}")
            raise

    async def _load_training_data(self, learning_request: LearningRequest) -> pd.DataFrame:
        """Load training data from specified source"""
        # In a real implementation, this would load from various sources
        # For now, generate synthetic training data

        np.random.seed(42)  # For reproducible training data

        # Generate time series training data
        num_samples = learning_request.batch_size * 10  # 10 batches worth
        timestamps = pd.date_range(
            start=datetime.now() - timedelta(days=30),
            periods=num_samples,
            freq='H'
        )

        # Create realistic industrial training data
        base_values = 50 + np.cumsum(np.random.normal(0, 0.1, num_samples))
        seasonal_component = 5 * np.sin(2 * np.pi * np.arange(num_samples) / 24)
        noise = np.random.normal(0, 1, num_samples)

        target_values = base_values + seasonal_component + noise

        # Add feature columns
        feature_data = {
            'timestamp': timestamps,
            'target': target_values,
            'temperature': 20 + 5 * np.sin(2 * np.pi * np.arange(num_samples) / 24) + np.random.normal(0, 1, num_samples),
            'pressure': 100 + 10 * np.cos(2 * np.pi * np.arange(num_samples) / 12) + np.random.normal(0, 2, num_samples),
            'flow_rate': 25 + 5 * np.random.random(num_samples),
            'setpoint': 50 + np.random.normal(0, 2, num_samples)
        }

        training_df = pd.DataFrame(feature_data)
        training_df = training_df.set_index('timestamp')

        logger.info(f"Loaded training data: {len(training_df)} samples, {len(training_df.columns)} features")

        return training_df

    async def _validate_training_data(self, data: pd.DataFrame, learning_request: LearningRequest) -> Dict[str, Any]:
        """Validate training data quality"""
        issues = []

        # Check for sufficient data
        min_samples = max(100, learning_request.batch_size * 3)
        if len(data) < min_samples:
            issues.append(f"Insufficient data: {len(data)} samples (minimum: {min_samples})")

        # Check for missing values
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        if missing_ratio > 0.1:
            issues.append(f"High missing value ratio: {missing_ratio:.1%}")

        # Check for data variance
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        for col in numeric_columns:
            if data[col].std() == 0:
                issues.append(f"No variance in column: {col}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data_size': len(data),
            'missing_ratio': missing_ratio,
            'feature_count': len(data.columns)
        }

    async def _evaluate_current_models(self, model_ids: List[str]) -> Dict[str, Dict[str, float]]:
        """Evaluate current model performance"""
        performance = {}

        for model_id in model_ids:
            # In a real implementation, this would evaluate actual models
            # For now, generate baseline performance metrics
            performance[model_id] = {
                'accuracy': 0.75 + np.random.random() * 0.15,  # 75-90%
                'mse': 1.0 + np.random.random() * 2.0,         # 1-3
                'mae': 0.5 + np.random.random() * 1.0,         # 0.5-1.5
                'r2_score': 0.60 + np.random.random() * 0.25   # 60-85%
            }

        return performance

    async def _execute_learning_strategy(self, learning_request: LearningRequest,
                                       training_data: pd.DataFrame,
                                       baseline_performance: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Execute the specified learning strategy"""
        strategy = learning_request.learning_strategy

        if strategy == LearningStrategy.INCREMENTAL:
            return await self._execute_incremental_learning(learning_request, training_data, baseline_performance)
        elif strategy == LearningStrategy.BATCH_RETRAIN:
            return await self._execute_batch_retraining(learning_request, training_data, baseline_performance)
        elif strategy == LearningStrategy.ONLINE_LEARNING:
            return await self._execute_online_learning(learning_request, training_data, baseline_performance)
        else:
            # Default to batch retraining
            return await self._execute_batch_retraining(learning_request, training_data, baseline_performance)

    async def _execute_incremental_learning(self, learning_request: LearningRequest,
                                          training_data: pd.DataFrame,
                                          baseline_performance: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Execute incremental learning strategy"""
        start_time = time.time()

        # Simulate incremental learning process
        batch_size = learning_request.batch_size
        max_iterations = learning_request.max_iterations
        learning_rate = learning_request.learning_rate

        convergence_history = []
        current_loss = 1.0

        for iteration in range(max_iterations):
            # Simulate batch processing
            batch_start = (iteration * batch_size) % len(training_data)
            min(batch_start + batch_size, len(training_data))

            # Simulate learning step
            learning_step = learning_rate * np.random.exponential(0.1)
            current_loss = max(0.01, current_loss - learning_step + np.random.normal(0, 0.01))

            convergence_history.append(current_loss)

            # Check convergence
            if iteration > 10:
                recent_improvement = convergence_history[-10] - current_loss
                if recent_improvement < learning_request.convergence_threshold:
                    break

            # Simulate processing time
            await asyncio.sleep(0.001)  # 1ms per iteration

        training_time = time.time() - start_time
        converged = current_loss < learning_request.convergence_threshold * 10

        return {
            'strategy': 'incremental',
            'iterations': iteration + 1,
            'final_loss': current_loss,
            'converged': converged,
            'training_time': training_time,
            'convergence_history': convergence_history
        }

    async def _execute_batch_retraining(self, learning_request: LearningRequest,
                                      training_data: pd.DataFrame,
                                      baseline_performance: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Execute batch retraining strategy"""
        start_time = time.time()

        # Simulate batch retraining
        num_batches = min(learning_request.max_iterations, len(training_data) // learning_request.batch_size)

        training_metrics = []

        for batch_idx in range(num_batches):
            # Simulate batch training
            batch_accuracy = 0.6 + (batch_idx / num_batches) * 0.3 + np.random.normal(0, 0.02)
            batch_loss = 2.0 * (1 - batch_accuracy) + np.random.normal(0, 0.1)

            training_metrics.append({
                'batch': batch_idx,
                'accuracy': batch_accuracy,
                'loss': batch_loss
            })

            # Simulate processing time
            await asyncio.sleep(0.002)  # 2ms per batch

        training_time = time.time() - start_time
        final_accuracy = training_metrics[-1]['accuracy'] if training_metrics else 0.75

        return {
            'strategy': 'batch_retrain',
            'iterations': num_batches,
            'final_accuracy': final_accuracy,
            'converged': final_accuracy > 0.85,
            'training_time': training_time,
            'training_metrics': training_metrics
        }

    async def _execute_online_learning(self, learning_request: LearningRequest,
                                     training_data: pd.DataFrame,
                                     baseline_performance: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Execute online learning strategy"""
        start_time = time.time()

        # Simulate online learning
        learning_curve = []
        current_performance = 0.70

        for sample_idx in range(min(learning_request.max_iterations, len(training_data))):
            # Simulate online update
            improvement = learning_request.learning_rate * np.random.exponential(0.1)
            current_performance = min(0.98, current_performance + improvement + np.random.normal(0, 0.005))

            learning_curve.append({
                'sample': sample_idx,
                'performance': current_performance
            })

            # Simulate processing time
            await asyncio.sleep(0.0005)  # 0.5ms per sample

        training_time = time.time() - start_time

        return {
            'strategy': 'online_learning',
            'iterations': len(learning_curve),
            'final_performance': current_performance,
            'converged': current_performance > 0.90,
            'training_time': training_time,
            'learning_curve': learning_curve
        }

    async def _evaluate_updated_models(self, model_ids: List[str]) -> Dict[str, Dict[str, float]]:
        """Evaluate models after training updates"""
        performance = {}

        for model_id in model_ids:
            # Simulate improved performance after training
            improvement_factor = 1.05 + np.random.random() * 0.15  # 5-20% improvement

            performance[model_id] = {
                'accuracy': min(0.98, (0.75 + np.random.random() * 0.15) * improvement_factor),
                'mse': max(0.1, (1.0 + np.random.random() * 2.0) / improvement_factor),
                'mae': max(0.05, (0.5 + np.random.random() * 1.0) / improvement_factor),
                'r2_score': min(0.98, (0.60 + np.random.random() * 0.25) * improvement_factor)
            }

        return performance

    def _calculate_improvement_metrics(self, initial: Dict[str, Dict[str, float]],
                                     final: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Calculate improvement metrics"""
        improvements = {}

        for model_id in initial:
            if model_id in final:
                model_improvements = {}

                for metric_name in initial[model_id]:
                    if metric_name in final[model_id]:
                        initial_value = initial[model_id][metric_name]
                        final_value = final[model_id][metric_name]

                        if metric_name in ['accuracy', 'precision', 'recall', 'f1_score', 'r2_score']:
                            # Higher is better
                            improvement = (final_value - initial_value) / initial_value if initial_value > 0 else 0
                        else:
                            # Lower is better (mse, mae, etc.)
                            improvement = (initial_value - final_value) / initial_value if initial_value > 0 else 0

                        model_improvements[metric_name] = improvement

                improvements[model_id] = model_improvements

        # Calculate overall improvement
        all_improvements = []
        for model_improvements in improvements.values():
            all_improvements.extend(model_improvements.values())

        overall_improvement = np.mean(all_improvements) if all_improvements else 0.0
        improvements['overall'] = overall_improvement

        return improvements

    def _assess_learning_quality(self, improvement_metrics: Dict[str, float]) -> LearningQuality:
        """Assess the quality of learning based on improvement metrics"""
        overall_improvement = improvement_metrics.get('overall', 0.0)

        if overall_improvement >= 0.15:      # 15%+ improvement
            return LearningQuality.EXCELLENT
        elif overall_improvement >= 0.10:   # 10-15% improvement
            return LearningQuality.VERY_GOOD
        elif overall_improvement >= 0.05:   # 5-10% improvement
            return LearningQuality.GOOD
        elif overall_improvement >= 0.02:   # 2-5% improvement
            return LearningQuality.ACCEPTABLE
        elif overall_improvement >= 0.0:    # 0-2% improvement
            return LearningQuality.POOR
        else:                               # Negative improvement
            return LearningQuality.FAILING

    def _generate_learning_insights(self, training_results: Dict[str, Any],
                                  improvement_metrics: Dict[str, float]) -> Dict[str, List[str]]:
        """Generate insights from learning process"""
        insights = {
            'patterns': [],
            'knowledge_updates': []
        }

        # Analyze training results
        strategy = training_results.get('strategy', 'unknown')
        converged = training_results.get('converged', False)
        iterations = training_results.get('iterations', 0)

        # Pattern insights
        if converged:
            insights['patterns'].append(f"Model converged successfully using {strategy} strategy in {iterations} iterations")
        else:
            insights['patterns'].append(f"Model did not converge with {strategy} strategy after {iterations} iterations")

        # Performance insights
        overall_improvement = improvement_metrics.get('overall', 0.0)
        if overall_improvement > 0.1:
            insights['patterns'].append(f"Significant performance improvement detected: {overall_improvement:.1%}")
        elif overall_improvement > 0:
            insights['patterns'].append(f"Modest performance improvement achieved: {overall_improvement:.1%}")
        else:
            insights['patterns'].append("No performance improvement or degradation detected")

        # Knowledge updates
        if strategy == 'incremental':
            insights['knowledge_updates'].append("Incremental learning patterns integrated into model knowledge")
        elif strategy == 'batch_retrain':
            insights['knowledge_updates'].append("Batch retraining updated model parameters and decision boundaries")
        elif strategy == 'online_learning':
            insights['knowledge_updates'].append("Online learning enabled real-time knowledge adaptation")

        return insights

    def _generate_learning_recommendations(self, learning_quality: LearningQuality,
                                         insights: Dict[str, List[str]]) -> List[str]:
        """Generate actionable recommendations based on learning results"""
        recommendations = []

        if learning_quality == LearningQuality.EXCELLENT:
            recommendations.append("Continue current learning strategy - excellent results achieved")
            recommendations.append("Consider expanding training data for even better performance")
        elif learning_quality == LearningQuality.VERY_GOOD:
            recommendations.append("Good learning performance - maintain current approach")
            recommendations.append("Monitor for continued improvement in next training cycle")
        elif learning_quality == LearningQuality.GOOD:
            recommendations.append("Adequate improvement - consider tuning learning parameters")
            recommendations.append("Evaluate alternative learning strategies for better results")
        elif learning_quality == LearningQuality.ACCEPTABLE:
            recommendations.append("Minimal improvement - investigate data quality and model architecture")
            recommendations.append("Consider increasing training data volume or quality")
        elif learning_quality == LearningQuality.POOR:
            recommendations.append("Poor learning performance - review training data and model selection")
            recommendations.append("Consider alternative algorithms or feature engineering")
        else:  # FAILING
            recommendations.append("Learning failed - immediate investigation required")
            recommendations.append("Review training data quality, model architecture, and learning parameters")

        return recommendations

    def _estimate_training_duration(self, learning_request: LearningRequest) -> float:
        """Estimate training duration in seconds"""
        base_time = 60  # 1 minute base

        # Factor in strategy complexity
        strategy_multipliers = {
            LearningStrategy.ONLINE_LEARNING: 0.5,
            LearningStrategy.INCREMENTAL: 1.0,
            LearningStrategy.BATCH_RETRAIN: 1.5,
            LearningStrategy.ENSEMBLE_UPDATE: 2.0,
            LearningStrategy.TRANSFER_LEARNING: 2.5,
            LearningStrategy.REINFORCEMENT: 3.0
        }

        strategy_multiplier = strategy_multipliers.get(learning_request.learning_strategy, 1.0)

        # Factor in number of models
        model_multiplier = len(learning_request.target_models) * 0.5

        # Factor in iterations
        iteration_multiplier = learning_request.max_iterations / 100

        estimated_duration = base_time * strategy_multiplier * model_multiplier * iteration_multiplier

        return max(30, min(3600, estimated_duration))  # Between 30 seconds and 1 hour

    def get_training_status(self, training_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a training process"""
        return self.active_training.get(training_id)

    def list_active_training(self) -> List[str]:
        """List all active training process IDs"""
        return list(self.active_training.keys())

class AdaptiveLearningEngine:
    """Core adaptive learning orchestration system"""

    def __init__(self, predictive_engine=None):
        self.predictive_engine = predictive_engine
        self.performance_monitor = PerformanceMonitor()
        self.continuous_trainer = ContinuousTrainer(predictive_engine)
        self.active_learning_requests = {}
        self.learning_history = {}
        self.adaptation_triggers = {}

        # Configuration
        self.auto_adaptation_enabled = True
        self.adaptation_thresholds = {
            'performance_drop': 0.05,    # 5% performance drop
            'error_increase': 0.10,      # 10% error increase
            'drift_threshold': 0.15,     # 15% data drift
            'time_interval': 3600        # 1 hour auto-check
        }

    async def create_adaptive_learning(self, learning_request: LearningRequest) -> LearningResult:
        """Create and execute adaptive learning process"""
        logger.info(f"Starting adaptive learning: {learning_request.adaptation_type.value}")

        self.active_learning_requests[learning_request.request_id] = learning_request

        try:
            # Route to appropriate adaptation type
            if learning_request.adaptation_type == AdaptationType.CONTINUOUS_TRAINING:
                result = await self.continuous_trainer.execute_continuous_training(learning_request)
            elif learning_request.adaptation_type == AdaptationType.MODEL_EVOLUTION:
                result = await self._execute_model_evolution(learning_request)
            elif learning_request.adaptation_type == AdaptationType.PATTERN_ADAPTATION:
                result = await self._execute_pattern_adaptation(learning_request)
            else:
                # Default to continuous training
                result = await self.continuous_trainer.execute_continuous_training(learning_request)

            # Store result in history
            self.learning_history[learning_request.request_id] = result

            # Update performance monitoring
            await self._update_performance_monitoring(result)

            logger.info(f"Adaptive learning completed: {result.learning_quality.value} quality")

            return result

        except Exception as e:
            logger.error(f"Adaptive learning failed: {e}")
            raise
        finally:
            self.active_learning_requests.pop(learning_request.request_id, None)

    async def _execute_model_evolution(self, learning_request: LearningRequest) -> LearningResult:
        """Execute model evolution adaptation"""
        # Placeholder for model evolution logic
        # In a full implementation, this would handle model architecture changes,
        # hyperparameter optimization, and algorithm selection

        start_time = time.time()

        # Simulate model evolution process
        evolution_steps = ['analyze_performance', 'identify_improvements', 'update_architecture', 'validate_changes']
        completed_steps = []

        for step in evolution_steps:
            # Simulate evolution step
            await asyncio.sleep(0.5)  # Simulate processing time
            completed_steps.append(step)
            logger.debug(f"Model evolution step completed: {step}")

        execution_time = time.time() - start_time

        # Generate mock results
        initial_performance = {'model_1': {'accuracy': 0.80, 'mse': 1.5}}
        final_performance = {'model_1': {'accuracy': 0.85, 'mse': 1.2}}
        improvement_metrics = {'model_1': {'accuracy': 0.0625, 'mse': 0.2}, 'overall': 0.065}

        return LearningResult(
            request_id=learning_request.request_id,
            adaptation_type=learning_request.adaptation_type,
            learning_strategy=learning_request.learning_strategy,
            models_updated=learning_request.target_models,
            initial_performance=initial_performance,
            final_performance=final_performance,
            improvement_metrics=improvement_metrics,
            learning_quality=LearningQuality.GOOD,
            iterations_completed=len(evolution_steps),
            convergence_achieved=True,
            training_time=execution_time * 0.8,
            data_points_processed=1000,
            patterns_discovered=['improved_decision_boundaries', 'optimized_feature_weights'],
            knowledge_updates=['updated_model_architecture', 'refined_hyperparameters'],
            recommendations=['monitor_performance', 'schedule_regular_evolution'],
            execution_time=execution_time
        )

    async def _execute_pattern_adaptation(self, learning_request: LearningRequest) -> LearningResult:
        """Execute pattern adaptation"""
        # Placeholder for pattern adaptation logic
        # In a full implementation, this would handle pattern recognition,
        # feature adaptation, and behavioral learning

        start_time = time.time()

        # Simulate pattern adaptation process
        adaptation_phases = ['pattern_detection', 'feature_analysis', 'adaptation_planning', 'implementation']

        for phase in adaptation_phases:
            await asyncio.sleep(0.3)  # Simulate processing time
            logger.debug(f"Pattern adaptation phase completed: {phase}")

        execution_time = time.time() - start_time

        # Generate mock results
        initial_performance = {'model_1': {'accuracy': 0.78, 'f1_score': 0.75}}
        final_performance = {'model_1': {'accuracy': 0.82, 'f1_score': 0.80}}
        improvement_metrics = {'model_1': {'accuracy': 0.051, 'f1_score': 0.067}, 'overall': 0.059}

        return LearningResult(
            request_id=learning_request.request_id,
            adaptation_type=learning_request.adaptation_type,
            learning_strategy=learning_request.learning_strategy,
            models_updated=learning_request.target_models,
            initial_performance=initial_performance,
            final_performance=final_performance,
            improvement_metrics=improvement_metrics,
            learning_quality=LearningQuality.GOOD,
            iterations_completed=len(adaptation_phases),
            convergence_achieved=True,
            training_time=execution_time * 0.7,
            data_points_processed=800,
            patterns_discovered=['new_seasonal_patterns', 'improved_anomaly_signatures'],
            knowledge_updates=['updated_pattern_library', 'enhanced_feature_extractors'],
            recommendations=['continue_pattern_monitoring', 'expand_pattern_database'],
            execution_time=execution_time
        )

    async def _update_performance_monitoring(self, learning_result: LearningResult):
        """Update performance monitoring with learning results"""
        for model_id in learning_result.models_updated:
            if model_id in learning_result.final_performance:
                metrics = learning_result.final_performance[model_id]
                self.performance_monitor.record_performance(model_id, metrics)

    def monitor_adaptation_triggers(self, model_id: str, new_data: np.ndarray = None,
                                  performance_metrics: Dict[str, float] = None) -> List[AdaptationTrigger]:
        """Monitor for adaptation triggers"""
        triggered = []

        if performance_metrics:
            self.performance_monitor.record_performance(model_id, performance_metrics)

            # Check for performance degradation
            degradation = self.performance_monitor.detect_performance_degradation(model_id)
            if degradation['degradation_detected']:
                triggered.append(AdaptationTrigger.PERFORMANCE_DEGRADATION)

        if new_data is not None:
            # Check for data drift
            drift = self.performance_monitor.detect_data_drift(model_id, new_data)
            if drift['drift_detected']:
                triggered.append(AdaptationTrigger.DATA_DRIFT_DETECTED)

        return triggered

    async def auto_adapt_if_needed(self, model_id: str, triggers: List[AdaptationTrigger]) -> Optional[LearningResult]:
        """Automatically trigger adaptation if conditions are met"""
        if not self.auto_adaptation_enabled or not triggers:
            return None

        # Determine adaptation strategy based on triggers
        if AdaptationTrigger.PERFORMANCE_DEGRADATION in triggers:
            adaptation_type = AdaptationType.CONTINUOUS_TRAINING
            learning_strategy = LearningStrategy.INCREMENTAL
        elif AdaptationTrigger.DATA_DRIFT_DETECTED in triggers:
            adaptation_type = AdaptationType.PATTERN_ADAPTATION
            learning_strategy = LearningStrategy.ONLINE_LEARNING
        else:
            adaptation_type = AdaptationType.CONTINUOUS_TRAINING
            learning_strategy = LearningStrategy.BATCH_RETRAIN

        # Create auto-learning request
        auto_request = LearningRequest(
            request_id=f"auto_{model_id}_{int(time.time())}",
            adaptation_type=adaptation_type,
            learning_strategy=learning_strategy,
            trigger=triggers[0],  # Primary trigger
            target_models=[model_id],
            data_source="auto_generated",
            performance_threshold=0.8,
            requested_by="auto_adaptation_system"
        )

        logger.info(f"Auto-adapting model {model_id} due to triggers: {[t.value for t in triggers]}")

        return await self.create_adaptive_learning(auto_request)

    def get_learning_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a learning request"""
        if request_id in self.active_learning_requests:
            return {"status": "active", "request": self.active_learning_requests[request_id]}
        elif request_id in self.learning_history:
            return {"status": "completed", "result": self.learning_history[request_id]}
        else:
            return None

    def list_active_learning(self) -> List[str]:
        """List all active learning request IDs"""
        return list(self.active_learning_requests.keys())

    def get_performance_summary(self, model_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary for a model"""
        return self.performance_monitor.get_performance_summary(model_id)

# Factory functions for common adaptive learning requests
def create_performance_improvement_request(
    model_ids: List[str],
    performance_threshold: float = 0.85,
    learning_strategy: LearningStrategy = LearningStrategy.INCREMENTAL
) -> LearningRequest:
    """Create a request for performance improvement"""
    return LearningRequest(
        request_id=f"perf_improve_{int(time.time())}",
        adaptation_type=AdaptationType.CONTINUOUS_TRAINING,
        learning_strategy=learning_strategy,
        trigger=AdaptationTrigger.PERFORMANCE_DEGRADATION,
        target_models=model_ids,
        data_source="performance_improvement",
        performance_threshold=performance_threshold,
        requested_by="performance_optimizer"
    )

def create_drift_adaptation_request(
    model_ids: List[str],
    drift_severity: str = "medium"
) -> LearningRequest:
    """Create a request for data drift adaptation"""
    # Adjust strategy based on drift severity
    if drift_severity == "high":
        strategy = LearningStrategy.BATCH_RETRAIN
        threshold = 0.9
    elif drift_severity == "medium":
        strategy = LearningStrategy.INCREMENTAL
        threshold = 0.8
    else:  # low
        strategy = LearningStrategy.ONLINE_LEARNING
        threshold = 0.75

    return LearningRequest(
        request_id=f"drift_adapt_{int(time.time())}",
        adaptation_type=AdaptationType.PATTERN_ADAPTATION,
        learning_strategy=strategy,
        trigger=AdaptationTrigger.DATA_DRIFT_DETECTED,
        target_models=model_ids,
        data_source="drift_adaptation",
        performance_threshold=threshold,
        context={"drift_severity": drift_severity},
        requested_by="drift_detector"
    )

# Export main classes and functions
__all__ = [
    "AdaptiveLearningEngine", "ContinuousTrainer", "PerformanceMonitor",
    "LearningRequest", "LearningResult", "AdaptationType", "LearningStrategy",
    "AdaptationTrigger", "LearningQuality", "create_performance_improvement_request",
    "create_drift_adaptation_request"
]

if __name__ == "__main__":
    # Example usage
    async def main():
        # Initialize adaptive learning system
        adaptive_engine = AdaptiveLearningEngine()

        # Create a performance improvement request
        request = create_performance_improvement_request(
            model_ids=["TIC-101-predictor", "FIC-201-anomaly"],
            performance_threshold=0.85,
            learning_strategy=LearningStrategy.INCREMENTAL
        )

        # Execute adaptive learning
        result = await adaptive_engine.create_adaptive_learning(request)

        print("Adaptive learning completed!")
        print(f"Learning Quality: {result.learning_quality.value}")
        print(f"Models Updated: {len(result.models_updated)}")
        print(f"Overall Improvement: {result.improvement_metrics.get('overall', 0):.1%}")
        print(f"Execution Time: {result.execution_time:.2f}s")

        if result.patterns_discovered:
            print("\nPatterns Discovered:")
            for pattern in result.patterns_discovered:
                print(f"  • {pattern}")

        if result.recommendations:
            print("\nRecommendations:")
            for rec in result.recommendations:
                print(f"  • {rec}")

    asyncio.run(main())
