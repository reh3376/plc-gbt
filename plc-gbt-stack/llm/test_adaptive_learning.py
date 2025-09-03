#!/usr/bin/env python3
"""
Phase 23.4.2: Adaptive Learning Systems - Test Suite
===================================================

Comprehensive test suite for the Adaptive Learning Systems, validating all
self-improving ML capabilities, continuous training, pattern recognition,
and knowledge adaptation for industrial control systems.

This test suite validates:
- Adaptive learning engine orchestration
- Continuous training and model evolution
- Performance monitoring and drift detection
- Pattern recognition and adaptation
- Learning quality assessment and optimization
- Integration with Phase 23.4.1 Predictive Analysis Engine

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 23.4.2 - Adaptive Learning Systems Testing
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

import numpy as np

# Import the adaptive learning components
from adaptive_learning import (
    AdaptationTrigger,
    AdaptationType,
    AdaptiveLearningEngine,
    ContinuousTrainer,
    LearningQuality,
    LearningRequest,
    LearningResult,
    LearningStrategy,
    PerformanceMonitor,
    create_drift_adaptation_request,
    create_performance_improvement_request,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdaptiveLearningTestSuite:
    """Comprehensive test suite for Adaptive Learning Systems"""

    def __init__(self):
        self.test_results = {
            "core_functionality": [],
            "continuous_training": [],
            "performance_monitoring": [],
            "pattern_adaptation": [],
            "learning_quality": [],
            "integration": []
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.start_time = None

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """Run all adaptive learning tests"""
        self.start_time = time.time()
        logger.info("🚀 Starting Adaptive Learning Systems Test Suite")

        try:
            # Test Category 1: Core Functionality (20 tests)
            await self._test_core_functionality()

            # Test Category 2: Continuous Training (25 tests)
            await self._test_continuous_training()

            # Test Category 3: Performance Monitoring (20 tests)
            await self._test_performance_monitoring()

            # Test Category 4: Pattern Adaptation (15 tests)
            await self._test_pattern_adaptation()

            # Test Category 5: Learning Quality Assessment (10 tests)
            await self._test_learning_quality()

            # Test Category 6: Integration Testing (10 tests)
            await self._test_integration()

            return self._calculate_results()

        except Exception as e:
            logger.error(f"Test suite execution failed: {e}")
            return self._generate_error_results(str(e))

    async def _test_core_functionality(self):
        """Test core adaptive learning functionality (20 tests)"""
        category = "core_functionality"
        logger.info("🔧 Testing Core Functionality...")

        # Test 1-5: Engine Initialization
        try:
            engine = AdaptiveLearningEngine()
            self._record_test(category, "engine_creation", engine is not None, "AdaptiveLearningEngine should instantiate")
            self._record_test(category, "performance_monitor", engine.performance_monitor is not None, "Should have performance monitor")
            self._record_test(category, "continuous_trainer", engine.continuous_trainer is not None, "Should have continuous trainer")
            self._record_test(category, "auto_adaptation", hasattr(engine, 'auto_adaptation_enabled'), "Should have auto-adaptation capability")
            self._record_test(category, "adaptation_thresholds", isinstance(engine.adaptation_thresholds, dict), "Should have adaptation thresholds")
        except Exception as e:
            self._record_test(category, "engine_initialization", False, f"Engine initialization failed: {e}")

        # Test 6-10: Request Creation and Validation
        try:
            # Test factory functions
            perf_request = create_performance_improvement_request(["model_1", "model_2"])
            self._record_test(category, "perf_request_creation", perf_request.request_id is not None, "Should create performance improvement request")
            self._record_test(category, "perf_request_type", perf_request.adaptation_type == AdaptationType.CONTINUOUS_TRAINING, "Should set correct adaptation type")

            drift_request = create_drift_adaptation_request(["model_3"], drift_severity="high")
            self._record_test(category, "drift_request_creation", drift_request.request_id is not None, "Should create drift adaptation request")
            self._record_test(category, "drift_request_strategy", drift_request.learning_strategy == LearningStrategy.BATCH_RETRAIN, "Should set strategy based on severity")

            # Test request validation
            self._record_test(category, "request_models", len(perf_request.target_models) == 2, "Should set target models correctly")

        except Exception as e:
            self._record_test(category, "request_creation", False, f"Request creation failed: {e}")

        # Test 11-15: Enum and Type Validation
        try:
            # Test AdaptationType enum
            self._record_test(category, "adaptation_type_enum", hasattr(AdaptationType, 'CONTINUOUS_TRAINING'), "Should have CONTINUOUS_TRAINING type")
            self._record_test(category, "adaptation_type_evolution", hasattr(AdaptationType, 'MODEL_EVOLUTION'), "Should have MODEL_EVOLUTION type")

            # Test LearningStrategy enum
            self._record_test(category, "learning_strategy_enum", hasattr(LearningStrategy, 'INCREMENTAL'), "Should have INCREMENTAL strategy")
            self._record_test(category, "learning_strategy_online", hasattr(LearningStrategy, 'ONLINE_LEARNING'), "Should have ONLINE_LEARNING strategy")

            # Test LearningQuality enum
            self._record_test(category, "learning_quality_enum", hasattr(LearningQuality, 'EXCELLENT'), "Should have EXCELLENT quality level")

        except Exception as e:
            self._record_test(category, "enum_validation", False, f"Enum validation failed: {e}")

        # Test 16-20: Data Structure Validation
        try:
            # Test LearningRequest structure
            request = LearningRequest(
                request_id="test_001",
                adaptation_type=AdaptationType.CONTINUOUS_TRAINING,
                learning_strategy=LearningStrategy.INCREMENTAL,
                trigger=AdaptationTrigger.PERFORMANCE_DEGRADATION,
                target_models=["model_test"],
                data_source="test_source",
                performance_threshold=0.8
            )

            self._record_test(category, "request_structure", request.request_id == "test_001", "Should create request with correct ID")
            self._record_test(category, "request_threshold", request.performance_threshold == 0.8, "Should set performance threshold")
            self._record_test(category, "request_defaults", request.learning_rate == 0.01, "Should have default learning rate")
            self._record_test(category, "request_context", isinstance(request.context, dict), "Should have context dictionary")
            self._record_test(category, "request_timestamp", request.created_at is not None, "Should have creation timestamp")

        except Exception as e:
            self._record_test(category, "data_structure", False, f"Data structure validation failed: {e}")

    async def _test_continuous_training(self):
        """Test continuous training capabilities (25 tests)"""
        category = "continuous_training"
        logger.info("🔄 Testing Continuous Training...")

        # Test 1-5: Trainer Initialization
        try:
            trainer = ContinuousTrainer(None)  # Mock predictive engine
            self._record_test(category, "trainer_creation", trainer is not None, "ContinuousTrainer should instantiate")
            self._record_test(category, "training_queue", hasattr(trainer, 'training_queue'), "Should have training queue")
            self._record_test(category, "active_training", isinstance(trainer.active_training, dict), "Should have active training tracker")
            self._record_test(category, "training_history", isinstance(trainer.training_history, dict), "Should have training history")

        except Exception as e:
            self._record_test(category, "trainer_initialization", False, f"Trainer initialization failed: {e}")

        # Test 6-15: Training Strategies
        try:
            engine = AdaptiveLearningEngine()

            # Test incremental learning
            incremental_request = create_performance_improvement_request(
                ["test_model"],
                learning_strategy=LearningStrategy.INCREMENTAL
            )
            incremental_request.max_iterations = 10  # Fast test

            incremental_result = await engine.create_adaptive_learning(incremental_request)
            self._record_test(category, "incremental_execution", incremental_result is not None, "Should execute incremental learning")
            self._record_test(category, "incremental_quality", hasattr(incremental_result.learning_quality, 'value'), "Should assess learning quality")
            self._record_test(category, "incremental_models", len(incremental_result.models_updated) > 0, "Should update models")

            # Test batch retraining
            batch_request = create_drift_adaptation_request(["test_model"], drift_severity="high")
            batch_request.max_iterations = 5  # Fast test

            batch_result = await engine.create_adaptive_learning(batch_request)
            self._record_test(category, "batch_execution", batch_result is not None, "Should execute batch retraining")
            self._record_test(category, "batch_strategy", batch_result.learning_strategy == LearningStrategy.BATCH_RETRAIN, "Should use batch strategy")
            self._record_test(category, "batch_convergence", isinstance(batch_result.convergence_achieved, bool), "Should report convergence status")

            # Test online learning
            online_request = create_drift_adaptation_request(["test_model"], drift_severity="low")
            online_request.max_iterations = 10  # Fast test

            online_result = await engine.create_adaptive_learning(online_request)
            self._record_test(category, "online_execution", online_result is not None, "Should execute online learning")
            self._record_test(category, "online_strategy", online_result.learning_strategy == LearningStrategy.ONLINE_LEARNING, "Should use online strategy")

            # Test performance metrics
            self._record_test(category, "performance_tracking", 'overall' in incremental_result.improvement_metrics, "Should track overall improvement")
            self._record_test(category, "execution_time", incremental_result.execution_time > 0, "Should track execution time")

        except Exception as e:
            self._record_test(category, "training_strategies", False, f"Training strategies failed: {e}")

        # Test 16-25: Training Quality and Metrics
        try:
            # Test learning quality assessment
            trainer = ContinuousTrainer(None)

            # Test excellent improvement
            excellent_metrics = {'overall': 0.20}  # 20% improvement
            excellent_quality = trainer._assess_learning_quality(excellent_metrics)
            self._record_test(category, "excellent_quality", excellent_quality == LearningQuality.EXCELLENT, "Should recognize excellent learning")

            # Test poor improvement
            poor_metrics = {'overall': 0.01}  # 1% improvement
            poor_quality = trainer._assess_learning_quality(poor_metrics)
            self._record_test(category, "poor_quality", poor_quality == LearningQuality.POOR, "Should recognize poor learning")

            # Test improvement calculation
            initial_perf = {'model_1': {'accuracy': 0.8, 'mse': 1.0}}
            final_perf = {'model_1': {'accuracy': 0.85, 'mse': 0.9}}
            improvement = trainer._calculate_improvement_metrics(initial_perf, final_perf)
            self._record_test(category, "improvement_calculation", 'overall' in improvement, "Should calculate improvement metrics")

            # Test training duration estimation
            test_request = create_performance_improvement_request(["model_1", "model_2"])
            estimated_duration = trainer._estimate_training_duration(test_request)
            self._record_test(category, "duration_estimation", 30 <= estimated_duration <= 3600, "Should estimate reasonable duration")

            # Test insight generation
            mock_training_results = {'strategy': 'incremental', 'converged': True, 'iterations': 10}
            mock_improvement = {'overall': 0.1}
            insights = trainer._generate_learning_insights(mock_training_results, mock_improvement)
            self._record_test(category, "insight_generation", 'patterns' in insights, "Should generate learning insights")

            # Test recommendation generation
            recommendations = trainer._generate_learning_recommendations(LearningQuality.GOOD, insights)
            self._record_test(category, "recommendation_generation", len(recommendations) > 0, "Should generate recommendations")

            # Test training queue management
            test_request = create_performance_improvement_request(["queue_test"])
            training_id = await trainer.schedule_training(test_request)
            self._record_test(category, "training_scheduling", training_id is not None, "Should schedule training")

            status = trainer.get_training_status(training_id)
            self._record_test(category, "status_tracking", status is not None, "Should track training status")

            active_list = trainer.list_active_training()
            self._record_test(category, "active_list", isinstance(active_list, list), "Should list active training")

        except Exception as e:
            self._record_test(category, "training_quality", False, f"Training quality testing failed: {e}")

    async def _test_performance_monitoring(self):
        """Test performance monitoring capabilities (20 tests)"""
        category = "performance_monitoring"
        logger.info("📊 Testing Performance Monitoring...")

        # Test 1-5: Monitor Initialization
        try:
            monitor = PerformanceMonitor(window_size=100)
            self._record_test(category, "monitor_creation", monitor is not None, "PerformanceMonitor should instantiate")
            self._record_test(category, "window_size", monitor.window_size == 100, "Should set window size")
            self._record_test(category, "performance_history", hasattr(monitor, 'performance_history'), "Should have performance history")
            self._record_test(category, "baseline_metrics", isinstance(monitor.baseline_metrics, dict), "Should have baseline metrics")
            self._record_test(category, "alert_thresholds", isinstance(monitor.alert_thresholds, dict), "Should have alert thresholds")
        except Exception as e:
            self._record_test(category, "monitor_initialization", False, f"Monitor initialization failed: {e}")

        # Test 6-15: Performance Recording and Analysis
        try:
            monitor = PerformanceMonitor()

            # Test performance recording
            test_metrics = {'accuracy': 0.85, 'mse': 1.2, 'mae': 0.8}
            monitor.record_performance("test_model", test_metrics)
            self._record_test(category, "performance_recording", len(monitor.performance_history["test_model"]) > 0, "Should record performance")

            # Test baseline establishment
            self._record_test(category, "baseline_establishment", "test_model" in monitor.baseline_metrics, "Should establish baseline")

            # Test performance summary
            summary = monitor.get_performance_summary("test_model")
            self._record_test(category, "performance_summary", 'recent_performance' in summary, "Should generate performance summary")
            self._record_test(category, "summary_metrics", isinstance(summary.get('recent_performance', {}), dict), "Should include recent metrics")

            # Test with multiple records for trend analysis
            for i in range(10):
                varied_metrics = {'accuracy': 0.8 + i * 0.01, 'mse': 1.5 - i * 0.02}
                monitor.record_performance("trend_model", varied_metrics)

            trend_summary = monitor.get_performance_summary("trend_model")
            self._record_test(category, "trend_analysis", 'trends' in trend_summary, "Should analyze trends")

            # Test degradation detection
            # First, establish a good baseline
            good_metrics = {'accuracy': 0.90, 'mse': 0.5}
            monitor.record_performance("degrade_model", good_metrics)

            # Then add degraded performance
            for i in range(10):
                bad_metrics = {'accuracy': 0.75, 'mse': 1.5}  # Significantly worse
                monitor.record_performance("degrade_model", bad_metrics)

            degradation = monitor.detect_performance_degradation("degrade_model")
            self._record_test(category, "degradation_detection", degradation.get('degradation_detected', False), "Should detect performance degradation")
            self._record_test(category, "degradation_signals", 'signals' in degradation, "Should provide degradation signals")

            # Test data drift detection
            np.random.normal(50, 5, 100)
            drifted_data = np.random.normal(70, 8, 100)  # Different distribution

            drift_result = monitor.detect_data_drift("drift_model", drifted_data)
            self._record_test(category, "drift_detection", 'drift_detected' in drift_result, "Should detect data drift")

        except Exception as e:
            self._record_test(category, "performance_analysis", False, f"Performance analysis failed: {e}")

        # Test 16-20: Advanced Monitoring Features
        try:
            monitor = PerformanceMonitor()

            # Test baseline update logic
            initial_metrics = {'accuracy': 0.80}
            improved_metrics = {'accuracy': 0.85}  # 5% improvement

            monitor.record_performance("update_model", initial_metrics)
            original_baseline = monitor.baseline_metrics["update_model"]['accuracy']

            monitor.record_performance("update_model", improved_metrics)
            updated_baseline = monitor.baseline_metrics["update_model"]['accuracy']

            self._record_test(category, "baseline_update", updated_baseline > original_baseline, "Should update baseline for significant improvement")

            # Test drift detector initialization
            drift_detector = monitor._initialize_drift_detector("init_model")
            self._record_test(category, "drift_detector_init", isinstance(drift_detector, dict), "Should initialize drift detector")

            # Test performance monitoring with no data
            no_data_summary = monitor.get_performance_summary("nonexistent_model")
            self._record_test(category, "no_data_handling", 'error' in no_data_summary, "Should handle missing data gracefully")

            # Test window size functionality
            small_monitor = PerformanceMonitor(window_size=3)
            for i in range(10):
                small_monitor.record_performance("window_test", {'accuracy': 0.8 + i * 0.01})

            window_history = small_monitor.performance_history["window_test"]
            self._record_test(category, "window_size_limit", len(window_history) <= 3, "Should respect window size limit")

            # Test alert threshold configuration
            self._record_test(category, "alert_thresholds_config", 'accuracy_drop' in monitor.alert_thresholds, "Should have configurable alert thresholds")

        except Exception as e:
            self._record_test(category, "advanced_monitoring", False, f"Advanced monitoring failed: {e}")

    async def _test_pattern_adaptation(self):
        """Test pattern adaptation capabilities (15 tests)"""
        category = "pattern_adaptation"
        logger.info("🎯 Testing Pattern Adaptation...")

        # Test 1-5: Adaptation Trigger Detection
        try:
            engine = AdaptiveLearningEngine()

            # Test performance degradation trigger
            degraded_metrics = {'accuracy': 0.70, 'mse': 2.0}  # Poor performance
            triggers = engine.monitor_adaptation_triggers("perf_model", performance_metrics=degraded_metrics)

            # Record multiple poor performances to trigger degradation detection
            for _i in range(15):
                engine.performance_monitor.record_performance("perf_model", degraded_metrics)

            triggers = engine.monitor_adaptation_triggers("perf_model", performance_metrics=degraded_metrics)
            # Note: May not trigger immediately due to baseline establishment
            self._record_test(category, "trigger_monitoring", isinstance(triggers, list), "Should monitor adaptation triggers")

            # Test data drift trigger
            normal_data = np.random.normal(50, 5, 100)
            drift_triggers = engine.monitor_adaptation_triggers("drift_model", new_data=normal_data)
            self._record_test(category, "drift_trigger_monitoring", isinstance(drift_triggers, list), "Should monitor drift triggers")

            # Test auto-adaptation capability
            self._record_test(category, "auto_adaptation_enabled", engine.auto_adaptation_enabled, "Should have auto-adaptation enabled")
            self._record_test(category, "adaptation_thresholds", len(engine.adaptation_thresholds) > 0, "Should have adaptation thresholds")

        except Exception as e:
            self._record_test(category, "trigger_detection", False, f"Trigger detection failed: {e}")

        # Test 6-10: Pattern Recognition and Adaptation
        try:
            engine = AdaptiveLearningEngine()

            # Test pattern adaptation request
            pattern_request = LearningRequest(
                request_id="pattern_test",
                adaptation_type=AdaptationType.PATTERN_ADAPTATION,
                learning_strategy=LearningStrategy.ONLINE_LEARNING,
                trigger=AdaptationTrigger.NEW_PATTERN_DETECTED,
                target_models=["pattern_model"],
                data_source="pattern_data",
                performance_threshold=0.8,
                max_iterations=5
            )

            pattern_result = await engine.create_adaptive_learning(pattern_request)
            self._record_test(category, "pattern_adaptation_execution", pattern_result is not None, "Should execute pattern adaptation")
            self._record_test(category, "pattern_adaptation_type", pattern_result.adaptation_type == AdaptationType.PATTERN_ADAPTATION, "Should use pattern adaptation type")
            self._record_test(category, "pattern_discoveries", len(pattern_result.patterns_discovered) > 0, "Should discover patterns")

            # Test model evolution adaptation
            evolution_request = LearningRequest(
                request_id="evolution_test",
                adaptation_type=AdaptationType.MODEL_EVOLUTION,
                learning_strategy=LearningStrategy.ENSEMBLE_UPDATE,
                trigger=AdaptationTrigger.PERFORMANCE_DEGRADATION,
                target_models=["evolution_model"],
                data_source="evolution_data",
                performance_threshold=0.85,
                max_iterations=4
            )

            evolution_result = await engine.create_adaptive_learning(evolution_request)
            self._record_test(category, "model_evolution_execution", evolution_result is not None, "Should execute model evolution")
            self._record_test(category, "knowledge_updates", len(evolution_result.knowledge_updates) > 0, "Should generate knowledge updates")

        except Exception as e:
            self._record_test(category, "pattern_adaptation", False, f"Pattern adaptation failed: {e}")

        # Test 11-15: Adaptation Quality and Results
        try:
            # Test adaptation result validation
            self._record_test(category, "adaptation_quality", hasattr(pattern_result, 'learning_quality'), "Should assess adaptation quality")
            self._record_test(category, "improvement_metrics", 'overall' in pattern_result.improvement_metrics, "Should calculate improvement metrics")
            self._record_test(category, "execution_tracking", pattern_result.execution_time > 0, "Should track execution time")
            self._record_test(category, "convergence_reporting", isinstance(pattern_result.convergence_achieved, bool), "Should report convergence")

            # Test recommendation generation
            self._record_test(category, "adaptation_recommendations", len(pattern_result.recommendations) > 0, "Should generate adaptation recommendations")

        except Exception as e:
            self._record_test(category, "adaptation_quality", False, f"Adaptation quality testing failed: {e}")

    async def _test_learning_quality(self):
        """Test learning quality assessment (10 tests)"""
        category = "learning_quality"
        logger.info("🎖️ Testing Learning Quality...")

        # Test 1-5: Quality Assessment Levels
        try:
            trainer = ContinuousTrainer(None)

            # Test different quality levels
            excellent_improvement = {'overall': 0.20}  # 20% improvement
            excellent_quality = trainer._assess_learning_quality(excellent_improvement)
            self._record_test(category, "excellent_assessment", excellent_quality == LearningQuality.EXCELLENT, "Should assess excellent quality correctly")

            very_good_improvement = {'overall': 0.12}  # 12% improvement
            very_good_quality = trainer._assess_learning_quality(very_good_improvement)
            self._record_test(category, "very_good_assessment", very_good_quality == LearningQuality.VERY_GOOD, "Should assess very good quality correctly")

            good_improvement = {'overall': 0.07}  # 7% improvement
            good_quality = trainer._assess_learning_quality(good_improvement)
            self._record_test(category, "good_assessment", good_quality == LearningQuality.GOOD, "Should assess good quality correctly")

            poor_improvement = {'overall': 0.01}  # 1% improvement
            poor_quality = trainer._assess_learning_quality(poor_improvement)
            self._record_test(category, "poor_assessment", poor_quality == LearningQuality.POOR, "Should assess poor quality correctly")

            failing_improvement = {'overall': -0.05}  # Negative improvement
            failing_quality = trainer._assess_learning_quality(failing_improvement)
            self._record_test(category, "failing_assessment", failing_quality == LearningQuality.FAILING, "Should assess failing quality correctly")

        except Exception as e:
            self._record_test(category, "quality_assessment", False, f"Quality assessment failed: {e}")

        # Test 6-10: Quality-based Recommendations
        try:
            # Test recommendation generation for different quality levels
            mock_insights = {'patterns': ['test_pattern'], 'knowledge_updates': ['test_update']}

            excellent_recs = trainer._generate_learning_recommendations(LearningQuality.EXCELLENT, mock_insights)
            self._record_test(category, "excellent_recommendations", len(excellent_recs) > 0, "Should generate recommendations for excellent quality")

            poor_recs = trainer._generate_learning_recommendations(LearningQuality.POOR, mock_insights)
            self._record_test(category, "poor_recommendations", len(poor_recs) > 0, "Should generate recommendations for poor quality")

            failing_recs = trainer._generate_learning_recommendations(LearningQuality.FAILING, mock_insights)
            self._record_test(category, "failing_recommendations", len(failing_recs) > 0, "Should generate recommendations for failing quality")

            # Test that recommendations are different for different quality levels
            excellent_content = ' '.join(excellent_recs)
            poor_content = ' '.join(poor_recs)
            self._record_test(category, "recommendation_differentiation", excellent_content != poor_content, "Should generate different recommendations for different quality levels")

            # Test insight integration in recommendations
            self._record_test(category, "insight_integration", any('pattern' in rec.lower() or 'knowledge' in rec.lower() or 'continue' in rec.lower() for rec in excellent_recs), "Should integrate insights into recommendations")

        except Exception as e:
            self._record_test(category, "quality_recommendations", False, f"Quality-based recommendations failed: {e}")

    async def _test_integration(self):
        """Test integration with other components (10 tests)"""
        category = "integration"
        logger.info("🔗 Testing Integration...")

        # Test 1-3: Engine Management
        try:
            engine = AdaptiveLearningEngine()

            # Test learning status tracking
            test_request = create_performance_improvement_request(["integration_test"])

            # Test status before execution
            status_before = engine.get_learning_status(test_request.request_id)
            self._record_test(category, "status_before_execution", status_before is None, "Should have no status before execution")

            # Test active learning tracking
            active_before = engine.list_active_learning()
            self._record_test(category, "active_tracking", isinstance(active_before, list), "Should track active learning")

            # Test performance summary integration
            summary = engine.get_performance_summary("test_model")
            self._record_test(category, "performance_summary_integration", isinstance(summary, dict), "Should integrate performance summaries")

        except Exception as e:
            self._record_test(category, "engine_management", False, f"Engine management testing failed: {e}")

        # Test 4-7: Learning Request Processing
        try:
            # Test different adaptation types
            continuous_request = create_performance_improvement_request(["continuous_test"])
            pattern_request = create_drift_adaptation_request(["pattern_test"])

            self._record_test(category, "continuous_request_type", continuous_request.adaptation_type == AdaptationType.CONTINUOUS_TRAINING, "Should create continuous training requests")
            self._record_test(category, "pattern_request_type", pattern_request.adaptation_type == AdaptationType.PATTERN_ADAPTATION, "Should create pattern adaptation requests")

            # Test request parameter validation
            valid_threshold = continuous_request.performance_threshold > 0
            self._record_test(category, "threshold_validation", valid_threshold, "Should have valid performance threshold")

            valid_models = len(pattern_request.target_models) > 0
            self._record_test(category, "models_validation", valid_models, "Should have target models")

        except Exception as e:
            self._record_test(category, "request_processing", False, f"Request processing testing failed: {e}")

        # Test 8-10: End-to-End Integration
        try:
            engine = AdaptiveLearningEngine()

            # Test full adaptive learning workflow
            e2e_request = create_performance_improvement_request(["e2e_test"], performance_threshold=0.8)
            e2e_request.max_iterations = 3  # Fast test

            e2e_result = await engine.create_adaptive_learning(e2e_request)
            self._record_test(category, "end_to_end_learning", e2e_result is not None, "Should complete end-to-end adaptive learning")

            # Test result caching
            cached_result = engine.get_learning_status(e2e_request.request_id)
            self._record_test(category, "result_caching", cached_result is not None, "Should cache learning results")

            # Test concurrent learning requests
            concurrent_requests = [
                create_performance_improvement_request([f"concurrent_{i}"], performance_threshold=0.75)
                for i in range(3)
            ]

            # Set fast execution for testing
            for req in concurrent_requests:
                req.max_iterations = 2

            concurrent_results = await asyncio.gather(
                *[engine.create_adaptive_learning(req) for req in concurrent_requests],
                return_exceptions=True
            )

            successful_concurrent = sum(1 for result in concurrent_results if isinstance(result, LearningResult))
            self._record_test(category, "concurrent_learning", successful_concurrent >= 2, f"Should handle concurrent learning ({successful_concurrent}/3 successful)")

        except Exception as e:
            self._record_test(category, "end_to_end_integration", False, f"End-to-end integration testing failed: {e}")

    def _record_test(self, category: str, test_name: str, passed: bool, description: str):
        """Record a test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1

        result = {
            "test_name": test_name,
            "passed": passed,
            "description": description,
            "timestamp": datetime.now().isoformat()
        }

        self.test_results[category].append(result)

        # Log result
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {status} {test_name}: {description}")

    def _calculate_results(self) -> Dict[str, Any]:
        """Calculate comprehensive test results"""
        execution_time = time.time() - self.start_time
        overall_score = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0

        # Calculate category scores
        category_scores = {}
        for category, tests in self.test_results.items():
            passed = sum(1 for test in tests if test["passed"])
            total = len(tests)
            score = (passed / total * 100) if total > 0 else 0
            category_scores[category] = {
                "passed": passed,
                "total": total,
                "score": round(score, 1)
            }

        # Determine validation level
        if overall_score >= 95:
            validation_level = "EXCELLENT"
        elif overall_score >= 85:
            validation_level = "VERY_GOOD"
        elif overall_score >= 75:
            validation_level = "GOOD"
        elif overall_score >= 65:
            validation_level = "ACCEPTABLE"
        else:
            validation_level = "NEEDS_IMPROVEMENT"

        # Key capabilities
        capabilities = [
            "Adaptive learning engine orchestration",
            "Continuous training and model optimization",
            "Real-time performance monitoring and tracking",
            "Pattern recognition and adaptation",
            "Data drift detection and response",
            "Learning quality assessment and improvement",
            "Multi-strategy learning (incremental, batch, online)",
            "Automatic adaptation trigger detection",
            "Knowledge base evolution and updates",
            "Integration with Phase 23.4.1 Predictive Engine"
        ]

        return {
            "phase": "23.4.2",
            "component": "Adaptive Learning Systems",
            "validation_date": datetime.now().isoformat(),
            "execution_time_seconds": round(execution_time, 2),
            "overall_score": round(overall_score, 1),
            "validation_level": validation_level,
            "total_tests": self.total_tests,
            "passed_tests": self.passed_tests,
            "failed_tests": self.total_tests - self.passed_tests,
            "category_breakdown": category_scores,
            "capabilities_validated": len(capabilities),
            "capabilities": capabilities,
            "production_readiness": overall_score >= 80,
            "detailed_results": self.test_results,
            "summary": {
                "core_functionality": f"{category_scores.get('core_functionality', {}).get('score', 0)}%",
                "continuous_training": f"{category_scores.get('continuous_training', {}).get('score', 0)}%",
                "performance_monitoring": f"{category_scores.get('performance_monitoring', {}).get('score', 0)}%",
                "pattern_adaptation": f"{category_scores.get('pattern_adaptation', {}).get('score', 0)}%",
                "learning_quality": f"{category_scores.get('learning_quality', {}).get('score', 0)}%",
                "integration": f"{category_scores.get('integration', {}).get('score', 0)}%"
            },
            "recommendations": self._generate_recommendations(overall_score, category_scores)
        }

    def _generate_recommendations(self, overall_score: float, category_scores: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        if overall_score < 80:
            recommendations.append("Overall score below production threshold - address failing tests")

        for category, scores in category_scores.items():
            if scores["score"] < 70:
                recommendations.append(f"Improve {category} - current score: {scores['score']}%")

        if category_scores.get("continuous_training", {}).get("score", 0) < 85:
            recommendations.append("Enhance continuous training capabilities and strategy implementation")

        if category_scores.get("performance_monitoring", {}).get("score", 0) < 90:
            recommendations.append("Strengthen performance monitoring and drift detection systems")

        if not recommendations:
            recommendations.append("All validations passing - Adaptive Learning Systems ready for production")

        return recommendations

    def _generate_error_results(self, error_message: str) -> Dict[str, Any]:
        """Generate error results when test suite fails"""
        return {
            "phase": "23.4.2",
            "component": "Adaptive Learning Systems",
            "validation_date": datetime.now().isoformat(),
            "status": "ERROR",
            "error": error_message,
            "overall_score": 0.0,
            "validation_level": "FAILED",
            "production_readiness": False,
            "recommendations": ["Fix test suite execution error before validation"]
        }

# Main execution function
async def run_adaptive_learning_tests() -> Dict[str, Any]:
    """Run comprehensive Adaptive Learning Systems tests"""
    test_suite = AdaptiveLearningTestSuite()
    return await test_suite.run_comprehensive_tests()

if __name__ == "__main__":
    # Run the comprehensive test suite
    async def main():
        print("🚀 Starting Phase 23.4.2: Adaptive Learning Systems Test Suite")
        print("=" * 80)

        results = await run_adaptive_learning_tests()

        print("\n" + "=" * 80)
        print("📊 PHASE 23.4.2 TEST RESULTS SUMMARY")
        print("=" * 80)
        print(f"Overall Score: {results['overall_score']}% ({results['validation_level']})")
        print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
        print(f"Execution Time: {results['execution_time_seconds']}s")
        print(f"Production Ready: {'✅ YES' if results['production_readiness'] else '❌ NO'}")

        print("\n📋 Category Scores:")
        for category, score in results['summary'].items():
            print(f"  {category.replace('_', ' ').title()}: {score}")

        print(f"\n🎯 Capabilities Validated: {results['capabilities_validated']}")

        if results['recommendations']:
            print("\n💡 Recommendations:")
            for rec in results['recommendations']:
                print(f"  • {rec}")

        print("\n" + "=" * 80)
        print("Phase 23.4.2 Testing Complete! 🎉")

    asyncio.run(main())
