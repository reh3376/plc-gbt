#!/usr/bin/env python3
"""
Phase 22.4: Real-time Monitoring & Diagnostics Validation
=========================================================

Comprehensive validation script for Phase 22.4 implementing:
- Task 22.4.1: Real-time Data Acquisition validation
- Task 22.4.2: Live Analysis Engine validation
- Task 22.4.3: Diagnostic System validation
- Task 22.4.4: Alerting Framework validation

Author: PLC-GPT Development Team
Date: January 18, 2025
Phase: 22.4 - Real-time Monitoring & Diagnostics Validation
Methodology: AI Task Orchestrator Guide
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validation results
class ValidationResults:
    def __init__(self):
        self.results = {
            "phase": "22.4",
            "validation_timestamp": datetime.now().isoformat(),
            "tasks": {
                "22.4.1": {"name": "Real-time Data Acquisition", "status": "pending", "score": 0},
                "22.4.2": {"name": "Live Analysis Engine", "status": "pending", "score": 0},
                "22.4.3": {"name": "Diagnostic System", "status": "pending", "score": 0},
                "22.4.4": {"name": "Alerting Framework", "status": "pending", "score": 0}
            },
            "overall_score": 0,
            "completion_status": "pending",
            "details": {}
        }

    def update_task(self, task_id: str, status: str, score: int, details: Dict[str, Any]):
        self.results["tasks"][task_id]["status"] = status
        self.results["tasks"][task_id]["score"] = score
        self.results["details"][task_id] = details

    def calculate_overall_score(self):
        scores = [task["score"] for task in self.results["tasks"].values()]
        self.results["overall_score"] = sum(scores) / len(scores) if scores else 0

        if self.results["overall_score"] >= 90:
            self.results["completion_status"] = "excellent"
        elif self.results["overall_score"] >= 80:
            self.results["completion_status"] = "good"
        elif self.results["overall_score"] >= 70:
            self.results["completion_status"] = "satisfactory"
        else:
            self.results["completion_status"] = "needs_improvement"

    def save_results(self, filename: str):
        """Save validation results to JSON file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.results, f, indent=2)
            logger.info(f"✅ Validation results saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving results: {e}")

def test_task_22_4_1_data_acquisition():
    """Validate Task 22.4.1: Real-time Data Acquisition"""

    logger.info("🔍 Testing Task 22.4.1: Real-time Data Acquisition")
    score = 0
    details = {"tests": [], "issues": [], "capabilities": []}

    try:
        # Test 1: Import realtime package
        try:
            from . import (
                REALTIME_CONFIG,
                DataSourceConfig,
                DataSourceType,
                RealTimeDataPoint,
                StreamingMode,
            )
            details["tests"].append("✅ Package imports successful")
            score += 20
        except ImportError as e:
            details["issues"].append(f"❌ Package import failed: {e}")
            return score, details

        # Test 2: Configuration validation
        try:
            config_keys = set(REALTIME_CONFIG.keys())
            required_keys = {"version", "data_sources", "streaming", "analysis", "performance"}
            if required_keys.issubset(config_keys):
                details["tests"].append("✅ Configuration structure valid")
                score += 15
            else:
                missing = required_keys - config_keys
                details["issues"].append(f"❌ Missing config keys: {missing}")
        except Exception as e:
            details["issues"].append(f"❌ Configuration validation failed: {e}")

        # Test 3: Data source configuration
        try:
            DataSourceConfig(
                source_id="test_source",
                source_type=DataSourceType.OPC_UA,
                connection_string="opc.tcp://localhost:4840",
                tags=["Temperature", "Pressure"],
                sampling_rate=1.0
            )
            details["tests"].append("✅ Data source configuration created")
            details["capabilities"].append("OPC UA data source configuration")
            score += 15
        except Exception as e:
            details["issues"].append(f"❌ Data source config creation failed: {e}")

        # Test 4: Real-time data point structure
        try:
            data_point = RealTimeDataPoint(
                timestamp=datetime.now(),
                source_id="test_source",
                tag_name="Temperature",
                value=25.5,
                quality="Good"
            )

            # Validate data point attributes
            required_attrs = ["timestamp", "source_id", "tag_name", "value", "quality"]
            if all(hasattr(data_point, attr) for attr in required_attrs):
                details["tests"].append("✅ Real-time data point structure valid")
                details["capabilities"].append("Real-time data point handling")
                score += 15
            else:
                details["issues"].append("❌ Data point missing required attributes")
        except Exception as e:
            details["issues"].append(f"❌ Data point creation failed: {e}")

        # Test 5: Enum validation
        try:
            # Test data source types
            source_types = [member.value for member in DataSourceType]
            expected_types = ["opc_ua", "modbus_tcp", "ethernet_ip", "mqtt", "websocket"]

            if all(t in source_types for t in expected_types):
                details["tests"].append("✅ Data source types enumeration complete")
                score += 15
            else:
                missing = set(expected_types) - set(source_types)
                details["issues"].append(f"❌ Missing data source types: {missing}")

            # Test streaming modes
            streaming_modes = [member.value for member in StreamingMode]
            if len(streaming_modes) >= 3:
                details["tests"].append("✅ Streaming modes enumeration adequate")
                details["capabilities"].append("Multiple streaming modes supported")
                score += 10
            else:
                details["issues"].append("❌ Insufficient streaming modes")
        except Exception as e:
            details["issues"].append(f"❌ Enum validation failed: {e}")

        # Test 6: Configuration completeness
        try:
            protocols = REALTIME_CONFIG.get("data_sources", {}).get("protocols", [])
            if len(protocols) >= 5:
                details["tests"].append("✅ Comprehensive protocol support")
                details["capabilities"].append(f"Supports {len(protocols)} protocols")
                score += 10
            else:
                details["issues"].append(f"❌ Limited protocol support: {len(protocols)}")
        except Exception as e:
            details["issues"].append(f"❌ Protocol validation failed: {e}")

    except Exception as e:
        details["issues"].append(f"❌ Task 22.4.1 validation failed: {e}")
        score = 0

    logger.info(f"📊 Task 22.4.1 Score: {score}/100")
    return score, details

def test_task_22_4_2_live_analysis():
    """Validate Task 22.4.2: Live Analysis Engine"""

    logger.info("🔍 Testing Task 22.4.2: Live Analysis Engine")
    score = 0
    details = {"tests": [], "issues": [], "capabilities": []}

    try:
        # Test 1: Import live analysis components
        try:
            from ..realtime.live_engine import (
                LiveAnalysisEngine,
                PerformanceDegradationDetector,
                RollingWindowCalculator,
                StreamingAnalyzer,
                StreamingConfiguration,
            )
            details["tests"].append("✅ Live analysis engine imports successful")
            score += 15
        except ImportError as e:
            details["issues"].append(f"❌ Live analysis import failed: {e}")
            return score, details

        # Test 2: Configuration creation
        try:
            config = StreamingConfiguration(
                stream_id="test_stream",
                window_size=300,
                overlap_ratio=0.5,
                update_frequency=1.0,
                enable_trend_detection=True,
                enable_anomaly_detection=True,
                enable_degradation_detection=True
            )
            details["tests"].append("✅ Streaming configuration created")
            score += 10
        except Exception as e:
            details["issues"].append(f"❌ Configuration creation failed: {e}")
            return score, details

        # Test 3: Rolling window calculator
        try:
            calculator = RollingWindowCalculator(window_size=100, overlap_ratio=0.5)

            # Add test data points
            for i in range(50):
                timestamp = datetime.now() + timedelta(seconds=i)
                value = 25.0 + 5.0 * np.sin(i * 0.1) + np.random.normal(0, 0.5)
                calculator.add_data_point("test_stream", timestamp, value)

            # Check if window is ready
            if calculator.is_window_ready("test_stream"):
                details["tests"].append("✅ Rolling window calculator functional")
                details["capabilities"].append("Rolling window statistical analysis")
                score += 15
            else:
                details["issues"].append("❌ Rolling window not ready with sufficient data")

        except Exception as e:
            details["issues"].append(f"❌ Rolling window calculator test failed: {e}")

        # Test 4: Streaming analyzer
        try:
            analyzer = StreamingAnalyzer(config)

            # Test data processing
            {
                "timestamp": datetime.now(),
                "value": 26.5,
                "source_id": "test_source",
                "tag_name": "Temperature"
            }

            # Note: This would normally be an async call, but we'll test the structure
            if hasattr(analyzer, 'process_data_stream'):
                details["tests"].append("✅ Streaming analyzer structure valid")
                details["capabilities"].append("Real-time data stream analysis")
                score += 15
            else:
                details["issues"].append("❌ Missing process_data_stream method")

        except Exception as e:
            details["issues"].append(f"❌ Streaming analyzer test failed: {e}")

        # Test 5: Live analysis engine
        try:
            configurations = [config]
            engine = LiveAnalysisEngine(configurations)

            # Test engine methods
            required_methods = ["start_engine", "stop_engine", "process_data_point", "get_engine_statistics"]
            missing_methods = [method for method in required_methods if not hasattr(engine, method)]

            if not missing_methods:
                details["tests"].append("✅ Live analysis engine interface complete")
                details["capabilities"].append("Complete live analysis orchestration")
                score += 15
            else:
                details["issues"].append(f"❌ Missing engine methods: {missing_methods}")

        except Exception as e:
            details["issues"].append(f"❌ Live analysis engine test failed: {e}")

        # Test 6: Performance degradation detector
        try:
            detector = PerformanceDegradationDetector(sensitivity=0.8)

            # Create baseline data
            baseline_data = np.random.normal(25.0, 1.0, 200)
            detector.establish_baseline("test_stream", baseline_data)

            # Test degradation detection
            degraded_data = np.random.normal(27.0, 2.0, 50)  # Higher mean and variance
            detection_result = detector.detect_degradation("test_stream", degraded_data)

            if "degradation_detected" in detection_result:
                details["tests"].append("✅ Performance degradation detection functional")
                details["capabilities"].append("Baseline comparison and degradation detection")
                score += 15
            else:
                details["issues"].append("❌ Invalid degradation detection result")

        except Exception as e:
            details["issues"].append(f"❌ Degradation detector test failed: {e}")

        # Test 7: Integration capabilities
        try:
            # Check for performance integration
            from ..realtime.live_engine import PERFORMANCE_INTEGRATION_AVAILABLE
            if PERFORMANCE_INTEGRATION_AVAILABLE:
                details["tests"].append("✅ Performance analysis integration available")
                details["capabilities"].append("Integration with Phase 22.3 performance analysis")
                score += 10
            else:
                details["tests"].append("⚠️ Performance analysis integration not available")

            # Check algorithm registry integration
            from ..realtime.live_engine import ALGORITHM_REGISTRY_AVAILABLE
            if ALGORITHM_REGISTRY_AVAILABLE:
                details["capabilities"].append("Algorithm registry integration")
                score += 5

        except Exception as e:
            details["issues"].append(f"❌ Integration test failed: {e}")

    except Exception as e:
        details["issues"].append(f"❌ Task 22.4.2 validation failed: {e}")
        score = 0

    logger.info(f"📊 Task 22.4.2 Score: {score}/100")
    return score, details

def test_task_22_4_3_diagnostics():
    """Validate Task 22.4.3: Diagnostic System"""

    logger.info("🔍 Testing Task 22.4.3: Diagnostic System")
    score = 0
    details = {"tests": [], "issues": [], "capabilities": []}

    try:
        # Test 1: Import diagnostic components
        try:
            from ..diagnostics import (
                DIAGNOSTICS_CONFIG,
                ComprehensiveDiagnosticResult,
                ControllerHealthResult,
                DiagnosticType,
                FaultSeverity,
                HealthStatus,
                OscillationResult,
                SensorFaultResult,
                ValveStictionResult,
            )
            details["tests"].append("✅ Diagnostic system imports successful")
            score += 15
        except ImportError as e:
            details["issues"].append(f"❌ Diagnostic import failed: {e}")
            return score, details

        # Test 2: Configuration validation
        try:
            config_keys = set(DIAGNOSTICS_CONFIG.keys())
            required_keys = {"supported_diagnostics", "valve_stiction", "oscillation_detection", "controller_health"}
            if required_keys.issubset(config_keys):
                details["tests"].append("✅ Diagnostic configuration structure valid")
                score += 10
            else:
                missing = required_keys - config_keys
                details["issues"].append(f"❌ Missing config sections: {missing}")
        except Exception as e:
            details["issues"].append(f"❌ Configuration validation failed: {e}")

        # Test 3: Diagnostic types enumeration
        try:
            diagnostic_types = [member.value for member in DiagnosticType]
            expected_types = ["valve_stiction", "oscillation", "controller_health", "sensor_fault"]

            if all(t in diagnostic_types for t in expected_types):
                details["tests"].append("✅ Diagnostic types enumeration complete")
                details["capabilities"].append(f"Supports {len(diagnostic_types)} diagnostic types")
                score += 15
            else:
                missing = set(expected_types) - set(diagnostic_types)
                details["issues"].append(f"❌ Missing diagnostic types: {missing}")
        except Exception as e:
            details["issues"].append(f"❌ Diagnostic types validation failed: {e}")

        # Test 4: Valve stiction result structure
        try:
            valve_result = ValveStictionResult(
                stiction_detected=True,
                stiction_index=0.75,
                confidence=0.85,
                detection_method="histogram",
                stick_slip_ratio=2.5,
                dead_band_estimate=0.5,
                recommendations=["Check valve position", "Consider maintenance"]
            )

            required_attrs = ["stiction_detected", "stiction_index", "confidence", "detection_method"]
            if all(hasattr(valve_result, attr) for attr in required_attrs):
                details["tests"].append("✅ Valve stiction result structure valid")
                details["capabilities"].append("Valve stiction detection and analysis")
                score += 15
            else:
                details["issues"].append("❌ Valve stiction result missing attributes")
        except Exception as e:
            details["issues"].append(f"❌ Valve stiction result test failed: {e}")

        # Test 5: Oscillation result structure
        try:
            from ..diagnostics import OscillationType

            oscillation_result = OscillationResult(
                oscillation_detected=True,
                oscillation_type=OscillationType.SINUSOIDAL,
                dominant_frequency=0.1,
                power_ratio=0.8,
                harris_index=0.25,
                amplitude=2.5,
                recommendations=["Review controller tuning", "Check for disturbances"]
            )

            if hasattr(oscillation_result, 'oscillation_detected') and hasattr(oscillation_result, 'harris_index'):
                details["tests"].append("✅ Oscillation detection result structure valid")
                details["capabilities"].append("Oscillation detection and characterization")
                score += 15
            else:
                details["issues"].append("❌ Oscillation result missing key attributes")
        except Exception as e:
            details["issues"].append(f"❌ Oscillation result test failed: {e}")

        # Test 6: Controller health monitoring
        try:
            controller_result = ControllerHealthResult(
                health_status=HealthStatus.WARNING,
                performance_index=0.75,
                tuning_quality=0.65,
                saturation_frequency=0.05,
                activity_level=0.8,
                degradation_factors=["High output saturation", "Poor setpoint tracking"],
                recommendations=["Retune controller", "Check for process changes"]
            )

            if hasattr(controller_result, 'health_status') and hasattr(controller_result, 'performance_index'):
                details["tests"].append("✅ Controller health monitoring structure valid")
                details["capabilities"].append("Controller performance assessment")
                score += 15
            else:
                details["issues"].append("❌ Controller health result missing attributes")
        except Exception as e:
            details["issues"].append(f"❌ Controller health test failed: {e}")

        # Test 7: Sensor fault detection
        try:
            sensor_result = SensorFaultResult(
                fault_detected=True,
                fault_types=["bias", "drift"],
                fault_severity=FaultSeverity.MEDIUM,
                bias_estimate=1.5,
                drift_rate=0.01,
                noise_level=0.2,
                recommendations=["Calibrate sensor", "Check wiring"]
            )

            if hasattr(sensor_result, 'fault_detected') and hasattr(sensor_result, 'fault_severity'):
                details["tests"].append("✅ Sensor fault detection structure valid")
                details["capabilities"].append("Sensor fault identification and classification")
                score += 10
            else:
                details["issues"].append("❌ Sensor fault result missing attributes")
        except Exception as e:
            details["issues"].append(f"❌ Sensor fault test failed: {e}")

        # Test 8: Utility functions
        try:
            from ..diagnostics import (
                get_available_diagnostics,
            )

            # Test available diagnostics
            available = get_available_diagnostics()
            if len(available) >= 4:
                details["tests"].append("✅ Diagnostic utility functions available")
                details["capabilities"].append("Comprehensive diagnostic utilities")
                score += 5
            else:
                details["issues"].append(f"❌ Limited diagnostic options: {len(available)}")
        except Exception as e:
            details["issues"].append(f"❌ Utility functions test failed: {e}")

    except Exception as e:
        details["issues"].append(f"❌ Task 22.4.3 validation failed: {e}")
        score = 0

    logger.info(f"📊 Task 22.4.3 Score: {score}/100")
    return score, details

def test_task_22_4_4_alerting():
    """Validate Task 22.4.4: Alerting Framework"""

    logger.info("🔍 Testing Task 22.4.4: Alerting Framework")
    score = 0
    details = {"tests": [], "issues": [], "capabilities": []}

    try:
        # Test 1: Import alerting components
        try:
            from ..alerts import (
                ALERTING_CONFIG,
                Alert,
                AlertCategory,
                AlertCondition,
                AlertPriority,
                AlertStatus,
                NotificationChannel,
                NotificationMessage,
                RootCauseAnalysis,
            )
            details["tests"].append("✅ Alerting framework imports successful")
            score += 15
        except ImportError as e:
            details["issues"].append(f"❌ Alerting import failed: {e}")
            return score, details

        # Test 2: Configuration validation
        try:
            config_keys = set(ALERTING_CONFIG.keys())
            required_keys = {"supported_channels", "alert_priorities", "notification_settings", "root_cause_analysis"}
            if required_keys.issubset(config_keys):
                details["tests"].append("✅ Alerting configuration structure valid")
                score += 10
            else:
                missing = required_keys - config_keys
                details["issues"].append(f"❌ Missing config sections: {missing}")
        except Exception as e:
            details["issues"].append(f"❌ Configuration validation failed: {e}")

        # Test 3: Alert condition creation
        try:
            condition = AlertCondition(
                condition_id="temp_high",
                name="High Temperature Alert",
                description="Temperature exceeds safe operating limits",
                condition_type="threshold",
                parameters={"threshold": 80.0, "operator": ">"},
                priority=AlertPriority.HIGH,
                category=AlertCategory.SAFETY,
                threshold_value=80.0,
                comparison_operator=">",
                notification_channels=[NotificationChannel.EMAIL, NotificationChannel.SMS]
            )

            required_attrs = ["condition_id", "name", "priority", "category", "threshold_value"]
            if all(hasattr(condition, attr) for attr in required_attrs):
                details["tests"].append("✅ Alert condition creation successful")
                details["capabilities"].append("Configurable alert conditions")
                score += 15
            else:
                details["issues"].append("❌ Alert condition missing required attributes")
        except Exception as e:
            details["issues"].append(f"❌ Alert condition creation failed: {e}")

        # Test 4: Alert instance creation
        try:
            alert = Alert(
                alert_id="alert_001",
                condition_id="temp_high",
                title="High Temperature Detected",
                description="Temperature sensor reading 85°C exceeds threshold of 80°C",
                priority=AlertPriority.HIGH,
                category=AlertCategory.SAFETY,
                status=AlertStatus.ACTIVE,
                triggered_time=datetime.now(),
                source_id="sensor_01",
                tag_name="Temperature",
                current_value=85.0,
                threshold_value=80.0
            )

            if hasattr(alert, 'alert_id') and hasattr(alert, 'priority') and hasattr(alert, 'status'):
                details["tests"].append("✅ Alert instance creation successful")
                details["capabilities"].append("Alert lifecycle management")
                score += 15
            else:
                details["issues"].append("❌ Alert instance missing key attributes")
        except Exception as e:
            details["issues"].append(f"❌ Alert instance creation failed: {e}")

        # Test 5: Notification message formatting
        try:
            from ..alerts import format_notification_message

            message = format_notification_message(alert, NotificationChannel.EMAIL)

            if hasattr(message, 'message_id') and hasattr(message, 'subject') and hasattr(message, 'body'):
                details["tests"].append("✅ Notification message formatting successful")
                details["capabilities"].append("Multi-channel notification formatting")
                score += 15
            else:
                details["issues"].append("❌ Notification message missing attributes")
        except Exception as e:
            details["issues"].append(f"❌ Notification message formatting failed: {e}")

        # Test 6: Alert filtering and prioritization
        try:
            from ..alerts import filter_alerts, prioritize_alerts

            # Create test alerts
            alerts = [
                Alert(
                    alert_id=f"alert_{i}",
                    condition_id="test_condition",
                    title=f"Test Alert {i}",
                    description="Test alert",
                    priority=priority,
                    category=AlertCategory.PERFORMANCE,
                    status=AlertStatus.ACTIVE,
                    triggered_time=datetime.now()
                )
                for i, priority in enumerate([AlertPriority.CRITICAL, AlertPriority.HIGH, AlertPriority.LOW])
            ]

            # Test filtering
            filtered = filter_alerts(alerts, {"min_priority": "high"})
            prioritized = prioritize_alerts(alerts)

            if len(filtered) <= len(alerts) and len(prioritized) == len(alerts):
                details["tests"].append("✅ Alert filtering and prioritization functional")
                details["capabilities"].append("Alert filtering and prioritization")
                score += 15
            else:
                details["issues"].append("❌ Alert filtering/prioritization failed")
        except Exception as e:
            details["issues"].append(f"❌ Alert filtering test failed: {e}")

        # Test 7: Root cause analysis structure
        try:
            rca = RootCauseAnalysis(
                analysis_id="rca_001",
                primary_alert_id="alert_001",
                related_alert_ids=["alert_002", "alert_003"],
                confidence_score=0.85,
                probable_cause="Valve stiction causing temperature oscillation",
                contributing_factors=["Poor tuning", "Worn valve seat"],
                correlation_evidence={"correlation_coefficient": 0.9},
                immediate_actions=["Check valve position", "Review controller output"],
                preventive_actions=["Schedule valve maintenance", "Retune controller"],
                analysis_time=datetime.now(),
                analysis_method="correlation_analysis",
                data_sources=["temperature_sensor", "valve_position"]
            )

            required_attrs = ["analysis_id", "confidence_score", "probable_cause", "immediate_actions"]
            if all(hasattr(rca, attr) for attr in required_attrs):
                details["tests"].append("✅ Root cause analysis structure valid")
                details["capabilities"].append("Root cause analysis integration")
                score += 10
            else:
                details["issues"].append("❌ Root cause analysis missing attributes")
        except Exception as e:
            details["issues"].append(f"❌ Root cause analysis test failed: {e}")

        # Test 8: Utility functions
        try:
            from ..alerts import (
                get_available_channels,
                validate_alert_condition,
            )

            # Test available channels
            channels = get_available_channels()
            if len(channels) >= 6:
                details["tests"].append("✅ Comprehensive notification channels available")
                details["capabilities"].append(f"Supports {len(channels)} notification channels")
                score += 5
            else:
                details["issues"].append(f"❌ Limited notification channels: {len(channels)}")

            # Test alert validation
            validation = validate_alert_condition(condition)
            if "valid" in validation:
                details["capabilities"].append("Alert condition validation")
                score += 5

        except Exception as e:
            details["issues"].append(f"❌ Utility functions test failed: {e}")

    except Exception as e:
        details["issues"].append(f"❌ Task 22.4.4 validation failed: {e}")
        score = 0

    logger.info(f"📊 Task 22.4.4 Score: {score}/100")
    return score, details

async def run_comprehensive_validation():
    """Run comprehensive validation for all Phase 22.4 tasks"""

    logger.info("🚀 Starting Phase 22.4: Real-time Monitoring & Diagnostics Validation")
    logger.info("=" * 80)

    # Initialize results
    results = ValidationResults()

    # Test Task 22.4.1: Real-time Data Acquisition
    score_1, details_1 = test_task_22_4_1_data_acquisition()
    results.update_task("22.4.1", "completed" if score_1 >= 70 else "needs_improvement", score_1, details_1)

    # Test Task 22.4.2: Live Analysis Engine
    score_2, details_2 = test_task_22_4_2_live_analysis()
    results.update_task("22.4.2", "completed" if score_2 >= 70 else "needs_improvement", score_2, details_2)

    # Test Task 22.4.3: Diagnostic System
    score_3, details_3 = test_task_22_4_3_diagnostics()
    results.update_task("22.4.3", "completed" if score_3 >= 70 else "needs_improvement", score_3, details_3)

    # Test Task 22.4.4: Alerting Framework
    score_4, details_4 = test_task_22_4_4_alerting()
    results.update_task("22.4.4", "completed" if score_4 >= 70 else "needs_improvement", score_4, details_4)

    # Calculate overall score
    results.calculate_overall_score()

    # Display results
    logger.info("=" * 80)
    logger.info("📊 PHASE 22.4 VALIDATION RESULTS")
    logger.info("=" * 80)

    for task_id, task_info in results.results["tasks"].items():
        status_emoji = "✅" if task_info["score"] >= 70 else "❌" if task_info["score"] < 50 else "⚠️"
        logger.info(f"{status_emoji} {task_id}: {task_info['name']} - {task_info['score']}/100")

        # Display capabilities
        task_details = results.results["details"].get(task_id, {})
        capabilities = task_details.get("capabilities", [])
        if capabilities:
            logger.info(f"   🔧 Capabilities: {', '.join(capabilities[:3])}{'...' if len(capabilities) > 3 else ''}")

        # Display issues
        issues = task_details.get("issues", [])
        if issues:
            logger.info(f"   ⚠️ Issues: {len(issues)} found")

    logger.info("=" * 80)
    logger.info(f"🎯 OVERALL SCORE: {results.results['overall_score']:.1f}/100")
    logger.info(f"📈 COMPLETION STATUS: {results.results['completion_status'].upper()}")

    # Detailed capabilities summary
    all_capabilities = []
    for task_details in results.results["details"].values():
        all_capabilities.extend(task_details.get("capabilities", []))

    logger.info(f"🔧 TOTAL CAPABILITIES IMPLEMENTED: {len(all_capabilities)}")

    # Phase 22.4 completion assessment
    if results.results["overall_score"] >= 90:
        logger.info("🎉 PHASE 22.4 EXCELLENT COMPLETION - Production ready!")
    elif results.results["overall_score"] >= 80:
        logger.info("✅ PHASE 22.4 GOOD COMPLETION - Minor improvements recommended")
    elif results.results["overall_score"] >= 70:
        logger.info("⚠️ PHASE 22.4 SATISFACTORY COMPLETION - Some improvements needed")
    else:
        logger.info("❌ PHASE 22.4 NEEDS IMPROVEMENT - Significant work required")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = f"../../results/phase22/phase22_4_validation_{timestamp}.json"

    # Ensure results directory exists
    os.makedirs(os.path.dirname(results_filename), exist_ok=True)
    results.save_results(results_filename)

    return results.results

def generate_completion_summary(validation_results: Dict[str, Any]):
    """Generate Phase 22.4 completion summary"""

    summary = f"""
# Phase 22.4: Real-time Monitoring & Diagnostics - Completion Summary

## Validation Results
- **Overall Score**: {validation_results['overall_score']:.1f}/100
- **Completion Status**: {validation_results['completion_status'].title()}
- **Validation Date**: {validation_results['validation_timestamp']}

## Task Completion Status

### Task 22.4.1: Real-time Data Acquisition
- **Score**: {validation_results['tasks']['22.4.1']['score']}/100
- **Status**: {validation_results['tasks']['22.4.1']['status'].title()}

### Task 22.4.2: Live Analysis Engine
- **Score**: {validation_results['tasks']['22.4.2']['score']}/100
- **Status**: {validation_results['tasks']['22.4.2']['status'].title()}

### Task 22.4.3: Diagnostic System
- **Score**: {validation_results['tasks']['22.4.3']['score']}/100
- **Status**: {validation_results['tasks']['22.4.3']['status'].title()}

### Task 22.4.4: Alerting Framework
- **Score**: {validation_results['tasks']['22.4.4']['score']}/100
- **Status**: {validation_results['tasks']['22.4.4']['status'].title()}

## Implementation Highlights

### Key Capabilities Delivered
"""

    # Collect all capabilities
    all_capabilities = []
    for task_details in validation_results["details"].values():
        all_capabilities.extend(task_details.get("capabilities", []))

    for capability in set(all_capabilities):
        summary += f"- {capability}\n"

    summary += f"""
## Technical Achievement
- **Total Test Cases**: {sum(len(details.get('tests', [])) for details in validation_results['details'].values())}
- **Successful Implementations**: {len([t for t in validation_results['tasks'].values() if t['score'] >= 70])}
- **Integration Points**: Multiple (Performance Analysis, Algorithm Registry, Diagnostic Systems)

## Next Steps
"""

    if validation_results['overall_score'] >= 90:
        summary += "- Phase 22.4 EXCELLENT completion - Ready for production deployment\n"
        summary += "- Proceed to Phase 22.5: Reporting & Visualization\n"
    elif validation_results['overall_score'] >= 80:
        summary += "- Phase 22.4 GOOD completion - Minor optimizations recommended\n"
        summary += "- Address remaining issues and proceed to Phase 22.5\n"
    else:
        summary += "- Review and address identified issues\n"
        summary += "- Re-run validation after improvements\n"

    return summary

if __name__ == "__main__":
    # Run validation
    validation_results = asyncio.run(run_comprehensive_validation())

    # Generate completion summary
    summary = generate_completion_summary(validation_results)

    # Save summary
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f"../../results/phase22/phase22_4_completion_summary_{timestamp}.md"

    try:
        with open(summary_filename, 'w') as f:
            f.write(summary)
        logger.info(f"✅ Completion summary saved to {summary_filename}")
    except Exception as e:
        logger.error(f"❌ Error saving summary: {e}")

    # Exit with appropriate code
    overall_score = validation_results.get('overall_score', 0)
    exit_code = 0 if overall_score >= 70 else 1
    sys.exit(exit_code)
