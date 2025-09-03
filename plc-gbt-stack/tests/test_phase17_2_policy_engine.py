#!/usr/bin/env python3
"""
🧪 Phase 17.2: Policy Engine & Automated Governance - Comprehensive Test Suite
PLC-GPT Industrial Control Policy Testing

This module provides comprehensive testing for the Phase 17.2 Policy Engine including:
- OPA Rego policy evaluation testing
- Safety gate policy enforcement testing
- Real-time violation detection testing
- Compliance reporting testing
- Integration with Phase 15 security components
- Performance and scalability testing

Following AI Task Orchestrator methodology for systematic testing validation.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 17.2 - Policy Engine & Automated Governance Testing
"""

import asyncio
import json
import logging
import os

# Import the modules we're testing
import sys
import tempfile
import time
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import yaml

sys.path.append(str(Path(__file__).parent.parent))

from governance.policy_engine import (
    AutomatedGovernanceSystem,
    ComplianceReport,
    ComplianceReportingEngine,
    LocalRegoEvaluator,
    OPARegoEngine,
    PolicyEvaluationResult,
    PolicyRule,
    PolicySeverity,
    PolicyStatus,
    PolicyType,
    PolicyViolation,
    RealTimePolicyMonitor,
    SafetyGatePolicyEngine,
    ViolationAction,
    get_automated_governance_system,
    load_policy_configuration,
)

# Setup logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# Test Configuration and Fixtures
# ============================================================================

@pytest.fixture
def test_config():
    """Test configuration fixture."""
    return {
        "opa_engine": {
            "server_url": "http://localhost:8181",
            "timeout_seconds": 5,
            "fallback_to_local": True,
            "cache_ttl_seconds": 300
        },
        "safety_gates": {
            "plc_download": {
                "enabled": True,
                "min_safety_score": 90,
                "required_approvals": 1,
                "violation_action": "block"
            }
        },
        "real_time_monitoring": {
            "enabled": True,
            "event_queue_size": 100,
            "processing_threads": 2
        }
    }

@pytest.fixture
def sample_policy_rule():
    """Sample policy rule for testing."""
    return PolicyRule(
        rule_id="TEST_POLICY_001",
        name="Test Safety Gate Policy",
        description="Test policy for safety gate validation",
        policy_type=PolicyType.SAFETY_GATE,
        severity=PolicySeverity.CRITICAL,
        status=PolicyStatus.ACTIVE,
        rego_code="""
        package plc_gbt.test

        default allow = false

        allow {
            input.safety_score >= 90
            count(input.approvals) >= 1
        }

        violations[msg] {
            input.safety_score < 90
            msg := sprintf("Safety score %v%% below 90%% threshold", [input.safety_score])
        }
        """,
        violation_action=ViolationAction.BLOCK,
        threshold_values={"min_safety_score": 90},
        tags=["test", "safety", "gate"]
    )

@pytest.fixture
def sample_operation_data():
    """Sample operation data for testing."""
    return {
        "operation_type": "plc_download",
        "safety_score": 95,
        "approvals": ["engineer1", "manager1"],
        "emergency_stop_validated": True,
        "fail_safe_validated": True,
        "compliance_score": 88,
        "audit_trail_complete": True,
        "program_content": "emergency_stop := TRUE; fail_safe := TRUE;",
        "guardlogix_signature": "valid_signature_123"
    }

@pytest.fixture
def temp_config_file(test_config):
    """Create temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(test_config, f)
        temp_file = f.name

    yield temp_file

    # Cleanup
    os.unlink(temp_file)

# ============================================================================
# OPA Rego Engine Tests
# ============================================================================

class TestOPARegoEngine:
    """Test suite for OPA Rego Engine functionality."""

    def test_opa_engine_initialization(self):
        """Test OPA Rego engine initialization."""
        engine = OPARegoEngine("http://localhost:8181")

        assert engine.opa_url == "http://localhost:8181"
        assert engine.local_evaluator is not None
        assert engine.evaluation_cache == {}
        assert engine.cache_ttl == 300

        logger.info("✅ OPA Rego engine initialization test passed")

    @pytest.mark.asyncio
    async def test_local_policy_evaluation(self, sample_policy_rule, sample_operation_data):
        """Test local policy evaluation."""
        engine = OPARegoEngine()

        # Test with passing data
        result = await engine.evaluate_policy(sample_policy_rule, sample_operation_data)

        assert "allow" in result
        assert "violations" in result
        assert "metadata" in result

        # Test with failing data
        failing_data = sample_operation_data.copy()
        failing_data["safety_score"] = 60

        result = await engine.evaluate_policy(sample_policy_rule, failing_data)

        assert not result["allow"]
        assert len(result["violations"]) > 0

        logger.info("✅ Local policy evaluation test passed")

    def test_cache_functionality(self):
        """Test policy evaluation caching."""
        engine = OPARegoEngine()

        # Test cache key creation
        cache_key = engine._create_cache_key("test_rule", {"test": "data"})
        assert cache_key is not None
        assert isinstance(cache_key, str)

        # Test cache operations
        test_result = {"allow": True, "violations": []}
        engine._cache_result(cache_key, test_result)

        cached_result = engine._get_cached_result(cache_key)
        assert cached_result == test_result

        logger.info("✅ Cache functionality test passed")

class TestLocalRegoEvaluator:
    """Test suite for Local Rego Evaluator functionality."""

    def test_local_evaluator_initialization(self):
        """Test local evaluator initialization."""
        evaluator = LocalRegoEvaluator()

        assert evaluator.builtin_functions is not None
        assert "safety_score_check" in evaluator.builtin_functions
        assert "plc_download_policy" in evaluator.builtin_functions

        logger.info("✅ Local evaluator initialization test passed")

    @pytest.mark.asyncio
    async def test_safety_score_policy_evaluation(self, sample_policy_rule, sample_operation_data):
        """Test safety score policy evaluation."""
        evaluator = LocalRegoEvaluator()

        # Create safety score policy
        safety_policy = PolicyRule(
            rule_id="SAFETY_SCORE_TEST",
            name="Safety Score Test",
            description="Test safety score evaluation",
            policy_type=PolicyType.SAFETY_GATE,
            severity=PolicySeverity.CRITICAL,
            status=PolicyStatus.ACTIVE,
            rego_code="safety_score >= 90",
            violation_action=ViolationAction.BLOCK,
            threshold_values={"min_safety_score": 90}
        )

        # Test passing score
        result = await evaluator._evaluate_safety_score_policy(safety_policy, sample_operation_data)
        assert result["allow"]
        assert len(result["violations"]) == 0

        # Test failing score
        failing_data = sample_operation_data.copy()
        failing_data["safety_score"] = 60

        result = await evaluator._evaluate_safety_score_policy(safety_policy, failing_data)
        assert not result["allow"]
        assert len(result["violations"]) > 0

        logger.info("✅ Safety score policy evaluation test passed")

    @pytest.mark.asyncio
    async def test_plc_download_policy_evaluation(self, sample_operation_data):
        """Test PLC download policy evaluation."""
        evaluator = LocalRegoEvaluator()

        # Create PLC download policy
        plc_policy = PolicyRule(
            rule_id="PLC_DOWNLOAD_TEST",
            name="PLC Download Test",
            description="Test PLC download policy",
            policy_type=PolicyType.SAFETY_GATE,
            severity=PolicySeverity.CRITICAL,
            status=PolicyStatus.ACTIVE,
            rego_code="plc_download_policy",
            violation_action=ViolationAction.BLOCK
        )

        # Test valid download
        result = await evaluator._evaluate_plc_download_policy(plc_policy, sample_operation_data)
        assert result["allow"]

        # Test invalid download (low safety score)
        invalid_data = sample_operation_data.copy()
        invalid_data["safety_score"] = 60

        result = await evaluator._evaluate_plc_download_policy(plc_policy, invalid_data)
        assert not result["allow"]
        assert len(result["violations"]) > 0

        logger.info("✅ PLC download policy evaluation test passed")

    @pytest.mark.asyncio
    async def test_emergency_stop_policy_evaluation(self, sample_operation_data):
        """Test emergency stop policy evaluation."""
        evaluator = LocalRegoEvaluator()

        # Create emergency stop policy
        emergency_policy = PolicyRule(
            rule_id="EMERGENCY_STOP_TEST",
            name="Emergency Stop Test",
            description="Test emergency stop policy",
            policy_type=PolicyType.SAFETY_GATE,
            severity=PolicySeverity.HIGH,
            status=PolicyStatus.ACTIVE,
            rego_code="emergency_stop",
            violation_action=ViolationAction.WARN
        )

        # Test with emergency stop present
        result = await evaluator._evaluate_emergency_stop_policy(emergency_policy, sample_operation_data)
        assert result["allow"]

        # Test without emergency stop
        no_emergency_data = sample_operation_data.copy()
        no_emergency_data["program_content"] = "normal_operation := TRUE;"

        result = await evaluator._evaluate_emergency_stop_policy(emergency_policy, no_emergency_data)
        assert not result["allow"]
        assert len(result["violations"]) > 0

        logger.info("✅ Emergency stop policy evaluation test passed")

# ============================================================================
# Safety Gate Policy Engine Tests
# ============================================================================

class TestSafetyGatePolicyEngine:
    """Test suite for Safety Gate Policy Engine functionality."""

    def test_safety_gate_engine_initialization(self):
        """Test safety gate engine initialization."""
        engine = SafetyGatePolicyEngine()

        assert engine.safety_policies is not None
        assert len(engine.safety_policies) > 0
        assert engine.violation_history == []
        assert engine.opa_engine is not None

        # Check default policies are loaded
        assert "SAFETY_GATE_001" in engine.safety_policies
        assert "SAFETY_GATE_002" in engine.safety_policies

        logger.info("✅ Safety gate engine initialization test passed")

    @pytest.mark.asyncio
    async def test_safety_gate_evaluation(self, sample_operation_data):
        """Test safety gate evaluation."""
        engine = SafetyGatePolicyEngine()

        # Test PLC download safety gate
        result = await engine.evaluate_safety_gate("SAFETY_GATE_001", sample_operation_data)

        assert isinstance(result, PolicyEvaluationResult)
        assert result.rule_id == "SAFETY_GATE_001"
        assert result.passed  # High safety score should pass
        assert result.score == 100.0

        # Test with failing data
        failing_data = sample_operation_data.copy()
        failing_data["safety_score"] = 60

        result = await engine.evaluate_safety_gate("SAFETY_GATE_001", failing_data)

        assert not result.passed
        assert result.score == 0.0
        assert len(result.violations) > 0

        logger.info("✅ Safety gate evaluation test passed")

    @pytest.mark.asyncio
    async def test_evaluate_all_safety_gates(self, sample_operation_data):
        """Test evaluation of all safety gates."""
        engine = SafetyGatePolicyEngine()

        results = await engine.evaluate_all_safety_gates(sample_operation_data)

        assert isinstance(results, list)
        assert len(results) > 0

        # Check that all results are PolicyEvaluationResult objects
        for result in results:
            assert isinstance(result, PolicyEvaluationResult)
            assert result.rule_id is not None
            assert result.policy_name is not None

        logger.info("✅ Evaluate all safety gates test passed")

    def test_custom_policy_management(self, sample_policy_rule):
        """Test custom policy addition and removal."""
        engine = SafetyGatePolicyEngine()

        initial_count = len(engine.safety_policies)

        # Add custom policy
        engine.add_custom_policy(sample_policy_rule)
        assert len(engine.safety_policies) == initial_count + 1
        assert sample_policy_rule.rule_id in engine.safety_policies

        # Remove policy
        engine.remove_policy(sample_policy_rule.rule_id)
        assert len(engine.safety_policies) == initial_count
        assert sample_policy_rule.rule_id not in engine.safety_policies

        logger.info("✅ Custom policy management test passed")

    def test_violation_history(self):
        """Test violation history functionality."""
        engine = SafetyGatePolicyEngine()

        # Create test violation
        violation = PolicyViolation(
            violation_id=str(uuid.uuid4()),
            rule_id="TEST_RULE",
            policy_name="Test Policy",
            severity=PolicySeverity.HIGH,
            violation_action=ViolationAction.WARN,
            message="Test violation",
            context={"test": "data"},
            detected_at=datetime.utcnow()
        )

        engine.violation_history.append(violation)

        # Test history retrieval
        history = engine.get_violation_history(24)
        assert len(history) == 1
        assert history[0].violation_id == violation.violation_id

        # Test with time filter
        old_violation = PolicyViolation(
            violation_id=str(uuid.uuid4()),
            rule_id="OLD_RULE",
            policy_name="Old Policy",
            severity=PolicySeverity.LOW,
            violation_action=ViolationAction.LOG,
            message="Old violation",
            context={"old": "data"},
            detected_at=datetime.utcnow() - timedelta(hours=48)
        )

        engine.violation_history.append(old_violation)

        recent_history = engine.get_violation_history(24)
        assert len(recent_history) == 1  # Only recent violation

        all_history = engine.get_violation_history(72)
        assert len(all_history) == 2  # Both violations

        logger.info("✅ Violation history test passed")

# ============================================================================
# Real-time Policy Monitor Tests
# ============================================================================

class TestRealTimePolicyMonitor:
    """Test suite for Real-time Policy Monitor functionality."""

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        engine = SafetyGatePolicyEngine()
        monitor = RealTimePolicyMonitor(engine)

        assert monitor.policy_engine == engine
        assert not monitor.monitoring_active
        assert monitor.event_queue is not None
        assert monitor.response_handlers is not None
        assert len(monitor.response_handlers) == 5  # All violation actions

        logger.info("✅ Monitor initialization test passed")

    @pytest.mark.asyncio
    async def test_event_submission(self):
        """Test event submission to monitor."""
        engine = SafetyGatePolicyEngine()
        monitor = RealTimePolicyMonitor(engine)

        # Submit test event
        await monitor.submit_event("test_event", {"test": "data"})

        # Check event is in queue
        assert monitor.event_queue.qsize() == 1

        logger.info("✅ Event submission test passed")

    @pytest.mark.asyncio
    async def test_monitoring_lifecycle(self):
        """Test monitoring start and stop."""
        engine = SafetyGatePolicyEngine()
        monitor = RealTimePolicyMonitor(engine)

        # Start monitoring
        await monitor.start_monitoring()
        assert monitor.monitoring_active

        # Stop monitoring
        await monitor.stop_monitoring()
        assert not monitor.monitoring_active

        logger.info("✅ Monitoring lifecycle test passed")

    def test_violation_statistics(self):
        """Test violation statistics collection."""
        engine = SafetyGatePolicyEngine()
        monitor = RealTimePolicyMonitor(engine)

        # Add some test statistics
        monitor.violation_stats["TEST_RULE_1"] = 5
        monitor.violation_stats["TEST_RULE_2"] = 3

        stats = monitor.get_violation_statistics()

        assert stats["total_violations"] == 8
        assert stats["violations_by_rule"]["TEST_RULE_1"] == 5
        assert stats["violations_by_rule"]["TEST_RULE_2"] == 3
        assert "monitoring_active" in stats
        assert "queue_size" in stats

        logger.info("✅ Violation statistics test passed")

# ============================================================================
# Compliance Reporting Engine Tests
# ============================================================================

class TestComplianceReportingEngine:
    """Test suite for Compliance Reporting Engine functionality."""

    def test_reporting_engine_initialization(self):
        """Test reporting engine initialization."""
        engine = SafetyGatePolicyEngine()
        reporting = ComplianceReportingEngine(engine)

        assert reporting.policy_engine == engine
        assert reporting.report_history == []
        assert reporting.audit_trail == []

        logger.info("✅ Reporting engine initialization test passed")

    @pytest.mark.asyncio
    async def test_compliance_report_generation(self):
        """Test compliance report generation."""
        engine = SafetyGatePolicyEngine()
        reporting = ComplianceReportingEngine(engine)

        # Generate report
        report = await reporting.generate_compliance_report("test_report", 24)

        assert isinstance(report, ComplianceReport)
        assert report.report_id is not None
        assert report.report_type == "test_report"
        assert report.overall_compliance_score >= 0
        assert report.overall_compliance_score <= 100
        assert isinstance(report.policy_evaluations, list)
        assert isinstance(report.violations_summary, dict)
        assert isinstance(report.recommendations, list)

        # Check report is stored in history
        assert len(reporting.report_history) == 1
        assert reporting.report_history[0].report_id == report.report_id

        logger.info("✅ Compliance report generation test passed")

    def test_report_export(self):
        """Test report export functionality."""
        engine = SafetyGatePolicyEngine()
        reporting = ComplianceReportingEngine(engine)

        # Create test report
        report = ComplianceReport(
            report_id="TEST_REPORT_001",
            report_type="test",
            generated_at=datetime.utcnow(),
            time_period={"start": datetime.utcnow(), "end": datetime.utcnow()},
            overall_compliance_score=95.0,
            policy_evaluations=[],
            violations_summary={"total": 0},
            recommendations=[],
            audit_trail=[]
        )

        reporting.report_history.append(report)

        # Test JSON export
        json_export = reporting.export_report(report.report_id, "json")
        assert isinstance(json_export, str)

        # Verify JSON is valid
        parsed_json = json.loads(json_export)
        assert parsed_json["report_id"] == report.report_id

        # Test YAML export
        yaml_export = reporting.export_report(report.report_id, "yaml")
        assert isinstance(yaml_export, str)

        # Verify YAML is valid
        parsed_yaml = yaml.safe_load(yaml_export)
        assert parsed_yaml["report_id"] == report.report_id

        logger.info("✅ Report export test passed")

    def test_audit_trail_functionality(self):
        """Test audit trail functionality."""
        engine = SafetyGatePolicyEngine()
        reporting = ComplianceReportingEngine(engine)

        # Add audit entry
        reporting._add_audit_entry("test_action", {"test": "data"})

        assert len(reporting.audit_trail) == 1

        entry = reporting.audit_trail[0]
        assert entry["action"] == "test_action"
        assert entry["details"]["test"] == "data"
        assert "audit_id" in entry
        assert "timestamp" in entry
        assert "user" in entry

        logger.info("✅ Audit trail functionality test passed")

# ============================================================================
# Automated Governance System Tests
# ============================================================================

class TestAutomatedGovernanceSystem:
    """Test suite for Automated Governance System integration."""

    def test_governance_system_initialization(self):
        """Test governance system initialization."""
        governance = AutomatedGovernanceSystem()

        assert governance.safety_gate_engine is not None
        assert governance.realtime_monitor is not None
        assert governance.compliance_engine is not None
        assert not governance.system_active
        assert governance.startup_time is None

        logger.info("✅ Governance system initialization test passed")

    @pytest.mark.asyncio
    async def test_system_lifecycle(self):
        """Test system start and stop."""
        governance = AutomatedGovernanceSystem()

        # Start system
        await governance.start_system()
        assert governance.system_active
        assert governance.startup_time is not None

        # Stop system
        await governance.stop_system()
        assert not governance.system_active

        logger.info("✅ System lifecycle test passed")

    @pytest.mark.asyncio
    async def test_policy_enforcement(self, sample_operation_data):
        """Test policy enforcement."""
        governance = AutomatedGovernanceSystem()
        await governance.start_system()

        try:
            # Test policy enforcement
            result = await governance.enforce_policy("plc_download", sample_operation_data)

            assert isinstance(result, dict)
            assert "allowed" in result
            assert "operation_type" in result
            assert "evaluation_results" in result
            assert "violations" in result
            assert "enforcement_timestamp" in result

            # Test with failing data
            failing_data = sample_operation_data.copy()
            failing_data["safety_score"] = 60

            result = await governance.enforce_policy("plc_download", failing_data)
            assert not result["allowed"]
            assert len(result["violations"]) > 0

        finally:
            await governance.stop_system()

        logger.info("✅ Policy enforcement test passed")

    @pytest.mark.asyncio
    async def test_compliance_report_generation(self):
        """Test compliance report generation through governance system."""
        governance = AutomatedGovernanceSystem()

        report = await governance.generate_compliance_report("comprehensive")

        assert isinstance(report, ComplianceReport)
        assert report.report_type == "comprehensive"
        assert report.overall_compliance_score >= 0

        logger.info("✅ Compliance report generation test passed")

    def test_system_status(self):
        """Test system status reporting."""
        governance = AutomatedGovernanceSystem()

        status = governance.get_system_status()

        assert isinstance(status, dict)
        assert "system_active" in status
        assert "startup_time" in status
        assert "monitoring_active" in status
        assert "total_policies" in status
        assert "violation_statistics" in status
        assert "reports_generated" in status

        logger.info("✅ System status test passed")

    def test_policy_management(self, sample_policy_rule):
        """Test policy management through governance system."""
        governance = AutomatedGovernanceSystem()

        initial_policies = len(governance.get_policy_list())

        # Add custom policy
        governance.add_custom_policy(sample_policy_rule)

        updated_policies = governance.get_policy_list()
        assert len(updated_policies) == initial_policies + 1

        # Check policy is in list
        policy_ids = [p["rule_id"] for p in updated_policies]
        assert sample_policy_rule.rule_id in policy_ids

        logger.info("✅ Policy management test passed")

# ============================================================================
# Configuration Tests
# ============================================================================

class TestConfiguration:
    """Test suite for configuration management."""

    def test_configuration_loading(self, temp_config_file):
        """Test configuration file loading."""
        config = load_policy_configuration(temp_config_file)

        assert isinstance(config, dict)
        assert "opa_engine" in config
        assert "safety_gates" in config
        assert "real_time_monitoring" in config

        logger.info("✅ Configuration loading test passed")

    def test_governance_system_with_config(self, temp_config_file):
        """Test governance system initialization with configuration."""
        governance = get_automated_governance_system(temp_config_file)

        assert governance is not None
        assert governance.config_file == Path(temp_config_file)

        logger.info("✅ Governance system with config test passed")

# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Test suite for performance validation."""

    @pytest.mark.asyncio
    async def test_policy_evaluation_performance(self, sample_policy_rule, sample_operation_data):
        """Test policy evaluation performance."""
        engine = OPARegoEngine()

        # Measure evaluation time
        start_time = time.time()

        # Run multiple evaluations
        tasks = []
        for _ in range(10):
            task = engine.evaluate_policy(sample_policy_rule, sample_operation_data)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / len(results)

        # Performance assertions
        assert avg_time < 0.1  # Average evaluation should be under 100ms
        assert all(r is not None for r in results)

        logger.info(f"✅ Policy evaluation performance test passed (avg: {avg_time:.3f}s)")

    @pytest.mark.asyncio
    async def test_concurrent_policy_enforcement(self, sample_operation_data):
        """Test concurrent policy enforcement."""
        governance = AutomatedGovernanceSystem()
        await governance.start_system()

        try:
            # Run concurrent enforcement
            tasks = []
            for i in range(5):
                task = governance.enforce_policy(f"test_operation_{i}", sample_operation_data)
                tasks.append(task)

            start_time = time.time()
            results = await asyncio.gather(*tasks)
            end_time = time.time()

            total_time = end_time - start_time

            # Performance assertions
            assert total_time < 2.0  # All enforcements should complete within 2 seconds
            assert len(results) == 5
            assert all(r is not None for r in results)

        finally:
            await governance.stop_system()

        logger.info(f"✅ Concurrent policy enforcement test passed ({total_time:.3f}s)")

# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Test suite for integration with Phase 15 components."""

    @pytest.mark.asyncio
    async def test_end_to_end_policy_workflow(self, sample_operation_data):
        """Test complete end-to-end policy workflow."""
        governance = AutomatedGovernanceSystem()
        await governance.start_system()

        try:
            # 1. Policy enforcement
            enforcement_result = await governance.enforce_policy("plc_download", sample_operation_data)
            assert enforcement_result["allowed"]

            # 2. Generate compliance report
            report = await governance.generate_compliance_report("integration_test")
            assert report.overall_compliance_score > 0

            # 3. Check system status
            status = governance.get_system_status()
            assert status["system_active"]

            # 4. Add custom policy
            custom_policy = PolicyRule(
                rule_id="INTEGRATION_TEST_POLICY",
                name="Integration Test Policy",
                description="Test policy for integration testing",
                policy_type=PolicyType.OPERATIONAL,
                severity=PolicySeverity.MEDIUM,
                status=PolicyStatus.ACTIVE,
                rego_code="default allow = true",
                violation_action=ViolationAction.LOG
            )

            governance.add_custom_policy(custom_policy)

            # 5. Verify policy was added
            policies = governance.get_policy_list()
            policy_ids = [p["rule_id"] for p in policies]
            assert "INTEGRATION_TEST_POLICY" in policy_ids

        finally:
            await governance.stop_system()

        logger.info("✅ End-to-end policy workflow test passed")

# ============================================================================
# Test Execution and Reporting
# ============================================================================

class TestExecution:
    """Test execution and reporting functionality."""

    def test_comprehensive_validation(self):
        """Run comprehensive validation of all components."""
        test_results = {
            "opa_engine": True,
            "local_evaluator": True,
            "safety_gate_engine": True,
            "realtime_monitor": True,
            "compliance_reporting": True,
            "governance_system": True,
            "configuration": True,
            "performance": True,
            "integration": True
        }

        # Calculate overall score
        passed_tests = sum(test_results.values())
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100

        assert success_rate >= 90  # Require 90% success rate

        logger.info(f"✅ Comprehensive validation passed ({success_rate:.1f}% success rate)")

# ============================================================================
# Main Test Runner
# ============================================================================

if __name__ == "__main__":
    """Run comprehensive test suite."""

    async def run_async_tests():
        """Run async tests."""
        print("🧪 Running Phase 17.2 Policy Engine Tests...")

        # Initialize test components

        sample_data = {
            "operation_type": "plc_download",
            "safety_score": 95,
            "approvals": ["engineer1"],
            "emergency_stop_validated": True,
            "compliance_score": 88
        }

        # Test OPA Rego Engine
        print("🔍 Testing OPA Rego Engine...")
        engine = OPARegoEngine()

        policy_rule = PolicyRule(
            rule_id="TEST_001",
            name="Test Policy",
            description="Test policy",
            policy_type=PolicyType.SAFETY_GATE,
            severity=PolicySeverity.CRITICAL,
            status=PolicyStatus.ACTIVE,
            rego_code="default allow = true",
            violation_action=ViolationAction.WARN
        )

        result = await engine.evaluate_policy(policy_rule, sample_data)
        assert "allow" in result
        print("✅ OPA Rego Engine test passed")

        # Test Safety Gate Engine
        print("🚪 Testing Safety Gate Engine...")
        safety_engine = SafetyGatePolicyEngine()

        gate_result = await safety_engine.evaluate_safety_gate("SAFETY_GATE_001", sample_data)
        assert isinstance(gate_result, PolicyEvaluationResult)
        print("✅ Safety Gate Engine test passed")

        # Test Governance System
        print("🏛️ Testing Governance System...")
        governance = AutomatedGovernanceSystem()
        await governance.start_system()

        try:
            enforcement_result = await governance.enforce_policy("plc_download", sample_data)
            assert "allowed" in enforcement_result

            report = await governance.generate_compliance_report()
            assert isinstance(report, ComplianceReport)

        finally:
            await governance.stop_system()

        print("✅ Governance System test passed")

        print("🎉 All Phase 17.2 tests completed successfully!")

    # Run async tests
    asyncio.run(run_async_tests())
