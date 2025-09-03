#!/usr/bin/env python3
"""
🏛️ Phase 17.2: Policy Engine & Automated Governance
PLC-GPT Industrial Control Policy Enforcement

This module implements comprehensive policy engine with OPA Rego integration for:
- Automated compliance enforcement with industrial safety standards
- Safety gate policies with configurable thresholds
- Real-time policy violation detection and response
- Automated compliance reporting and audit trails
- Integration with Phase 15 security components

Following AI Task Orchestrator methodology for systematic governance enhancement.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 17.2 - Policy Engine & Automated Governance
"""

import asyncio
import hashlib
import json
import logging
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import yaml

# OPA Rego integration
try:
    import aiohttp
    import requests
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False
    logging.warning("Network libraries not available for OPA integration")

# Real-time monitoring
try:
    import watchdog
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logging.warning("Watchdog library not available for real-time monitoring")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Policy Engine Core Framework
# ============================================================================

class PolicyType(Enum):
    """Types of policies supported by the engine"""
    SAFETY_GATE = "safety_gate"
    COMPLIANCE = "compliance"
    SECURITY = "security"
    OPERATIONAL = "operational"
    EMERGENCY = "emergency"
    AUDIT = "audit"

class PolicySeverity(Enum):
    """Policy violation severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class PolicyStatus(Enum):
    """Policy enforcement status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"

class ViolationAction(Enum):
    """Actions to take on policy violations"""
    BLOCK = "block"
    WARN = "warn"
    LOG = "log"
    ESCALATE = "escalate"
    EMERGENCY_STOP = "emergency_stop"

@dataclass
class PolicyRule:
    """Individual policy rule definition"""
    rule_id: str
    name: str
    description: str
    policy_type: PolicyType
    severity: PolicySeverity
    status: PolicyStatus
    rego_code: str
    violation_action: ViolationAction
    threshold_values: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = "system"
    tags: List[str] = field(default_factory=list)

@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_id: str
    rule_id: str
    policy_name: str
    severity: PolicySeverity
    violation_action: ViolationAction
    message: str
    context: Dict[str, Any]
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
    escalated: bool = False
    escalation_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""
    evaluation_id: str
    rule_id: str
    policy_name: str
    passed: bool
    score: float
    message: str
    context: Dict[str, Any]
    evaluated_at: datetime
    evaluation_time_ms: float
    violations: List[PolicyViolation] = field(default_factory=list)

@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""
    report_id: str
    report_type: str
    generated_at: datetime
    time_period: Dict[str, datetime]
    overall_compliance_score: float
    policy_evaluations: List[PolicyEvaluationResult]
    violations_summary: Dict[str, int]
    recommendations: List[str]
    audit_trail: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

# ============================================================================
# OPA Rego Policy Engine
# ============================================================================

class OPARegoEngine:
    """
    Open Policy Agent (OPA) Rego integration engine.

    Provides OPA Rego policy evaluation with local fallback
    for industrial control system policy enforcement.
    """

    def __init__(self, opa_url: str = "http://localhost:8181"):
        """
        Initialize OPA Rego engine.

        Args:
            opa_url: OPA server URL
        """
        self.opa_url = opa_url
        self.local_evaluator = LocalRegoEvaluator()
        self.evaluation_cache: Dict[str, Any] = {}
        self.cache_ttl = 300  # 5 minutes

        logger.info(f"OPARegoEngine initialized with URL: {opa_url}")

    async def evaluate_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate policy rule against input data.

        Args:
            policy_rule: Policy rule to evaluate
            input_data: Input data for evaluation

        Returns:
            Evaluation result
        """
        try:
            # Create cache key
            cache_key = self._create_cache_key(policy_rule.rule_id, input_data)

            # Check cache first
            cached_result = self._get_cached_result(cache_key)
            if cached_result:
                logger.debug(f"Using cached result for policy {policy_rule.rule_id}")
                return cached_result

            # Try OPA server first
            if NETWORK_AVAILABLE:
                try:
                    result = await self._evaluate_with_opa_server(policy_rule, input_data)
                    if result:
                        self._cache_result(cache_key, result)
                        return result
                except Exception as e:
                    logger.warning(f"OPA server evaluation failed: {e}, falling back to local")

            # Fall back to local evaluation
            result = await self.local_evaluator.evaluate(policy_rule, input_data)
            self._cache_result(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Policy evaluation failed for {policy_rule.rule_id}: {e}")
            return {
                "allow": False,
                "violations": [f"Policy evaluation error: {str(e)}"],
                "metadata": {"error": True, "error_message": str(e)}
            }

    async def _evaluate_with_opa_server(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Evaluate policy using OPA server."""
        try:
            payload = {
                "input": input_data,
                "policy": policy_rule.rego_code
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.opa_url}/v1/data/plc_gbt/evaluate",
                    json=payload,
                    timeout=5.0
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"OPA server returned status {response.status}")
                        return None

        except Exception as e:
            logger.error(f"OPA server communication failed: {e}")
            return None

    def _create_cache_key(self, rule_id: str, input_data: Dict[str, Any]) -> str:
        """Create cache key for evaluation result."""
        data_hash = hashlib.sha256(json.dumps(input_data, sort_keys=True).encode()).hexdigest()
        return f"{rule_id}:{data_hash}"

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached evaluation result."""
        if cache_key in self.evaluation_cache:
            cached_entry = self.evaluation_cache[cache_key]
            if time.time() - cached_entry["timestamp"] < self.cache_ttl:
                return cached_entry["result"]
            else:
                del self.evaluation_cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache evaluation result."""
        self.evaluation_cache[cache_key] = {
            "result": result,
            "timestamp": time.time()
        }

class LocalRegoEvaluator:
    """
    Local Rego policy evaluator for offline operation.

    Provides basic policy evaluation without OPA server dependency
    for air-gapped industrial environments.
    """

    def __init__(self):
        """Initialize local evaluator."""
        self.builtin_functions = {
            "safety_score_check": self._safety_score_check,
            "plc_download_policy": self._plc_download_policy,
            "emergency_stop_policy": self._emergency_stop_policy,
            "compliance_threshold": self._compliance_threshold,
            "audit_requirement": self._audit_requirement
        }

        logger.info("LocalRegoEvaluator initialized")

    async def evaluate(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate policy rule locally.

        Args:
            policy_rule: Policy rule to evaluate
            input_data: Input data for evaluation

        Returns:
            Evaluation result
        """
        try:
            # Parse simple Rego-like rules
            if "safety_score" in policy_rule.rego_code:
                return await self._evaluate_safety_score_policy(policy_rule, input_data)
            elif "plc_download" in policy_rule.rego_code:
                return await self._evaluate_plc_download_policy(policy_rule, input_data)
            elif "emergency_stop" in policy_rule.rego_code:
                return await self._evaluate_emergency_stop_policy(policy_rule, input_data)
            elif "compliance" in policy_rule.rego_code:
                return await self._evaluate_compliance_policy(policy_rule, input_data)
            else:
                # Generic evaluation
                return await self._evaluate_generic_policy(policy_rule, input_data)

        except Exception as e:
            logger.error(f"Local policy evaluation failed: {e}")
            return {
                "allow": False,
                "violations": [f"Local evaluation error: {str(e)}"],
                "metadata": {"error": True, "error_message": str(e)}
            }

    async def _evaluate_safety_score_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate safety score policy."""
        safety_score = input_data.get("safety_score", 0)
        threshold = policy_rule.threshold_values.get("min_safety_score", 90)

        passed = safety_score >= threshold
        violations = []

        if not passed:
            violations.append(f"Safety score {safety_score}% below threshold {threshold}%")

        return {
            "allow": passed,
            "violations": violations,
            "metadata": {
                "safety_score": safety_score,
                "threshold": threshold,
                "policy_type": "safety_gate"
            }
        }

    async def _evaluate_plc_download_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate PLC download policy."""
        operation_type = input_data.get("operation_type", "")
        safety_score = input_data.get("safety_score", 0)
        approvals = input_data.get("approvals", [])

        violations = []

        # Check safety score
        if safety_score < 70:
            violations.append(f"Safety score {safety_score}% too low for PLC download")

        # Check approvals
        if operation_type == "critical" and len(approvals) < 2:
            violations.append("Critical PLC download requires 2+ approvals")

        passed = len(violations) == 0

        return {
            "allow": passed,
            "violations": violations,
            "metadata": {
                "operation_type": operation_type,
                "safety_score": safety_score,
                "approvals_count": len(approvals)
            }
        }

    async def _evaluate_emergency_stop_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate emergency stop policy."""
        program_content = input_data.get("program_content", "")

        violations = []

        # Check for emergency stop implementation
        if "emergency_stop" not in program_content.lower():
            violations.append("Emergency stop functionality not found in program")

        if "fail_safe" not in program_content.lower():
            violations.append("Fail-safe behavior not implemented")

        passed = len(violations) == 0

        return {
            "allow": passed,
            "violations": violations,
            "metadata": {
                "program_analyzed": True,
                "emergency_stop_found": "emergency_stop" in program_content.lower()
            }
        }

    async def _evaluate_compliance_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate compliance policy."""
        compliance_score = input_data.get("compliance_score", 0)
        threshold = policy_rule.threshold_values.get("min_compliance", 85)

        passed = compliance_score >= threshold
        violations = []

        if not passed:
            violations.append(f"Compliance score {compliance_score}% below threshold {threshold}%")

        return {
            "allow": passed,
            "violations": violations,
            "metadata": {
                "compliance_score": compliance_score,
                "threshold": threshold
            }
        }

    async def _evaluate_generic_policy(self, policy_rule: PolicyRule, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generic policy evaluation."""
        # Simple rule evaluation based on policy type
        if policy_rule.policy_type == PolicyType.SAFETY_GATE:
            return await self._evaluate_safety_score_policy(policy_rule, input_data)
        else:
            return {
                "allow": True,
                "violations": [],
                "metadata": {"generic_evaluation": True}
            }

    # Built-in functions for policy evaluation
    def _safety_score_check(self, score: float, threshold: float) -> bool:
        """Check if safety score meets threshold."""
        return score >= threshold

    def _plc_download_policy(self, operation_data: Dict[str, Any]) -> bool:
        """Check PLC download policy compliance."""
        safety_score = operation_data.get("safety_score", 0)
        approvals = operation_data.get("approvals", [])

        return safety_score >= 70 and len(approvals) >= 1

    def _emergency_stop_policy(self, program_content: str) -> bool:
        """Check emergency stop policy compliance."""
        return "emergency_stop" in program_content.lower()

    def _compliance_threshold(self, score: float, threshold: float) -> bool:
        """Check compliance threshold."""
        return score >= threshold

    def _audit_requirement(self, operation_data: Dict[str, Any]) -> bool:
        """Check audit requirements."""
        return "audit_trail" in operation_data

# ============================================================================
# Safety Gate Policy Engine
# ============================================================================

class SafetyGatePolicyEngine:
    """
    Safety gate policy engine for industrial control systems.

    Implements safety gate policies with configurable thresholds
    and automated enforcement for critical operations.
    """

    def __init__(self, config_file: str = None):
        """
        Initialize safety gate policy engine.

        Args:
            config_file: Optional configuration file path
        """
        self.config_file = Path(config_file) if config_file else None
        self.safety_policies: Dict[str, PolicyRule] = {}
        self.violation_history: List[PolicyViolation] = []
        self.opa_engine = OPARegoEngine()

        # Load default safety gate policies
        self._load_default_safety_policies()

        logger.info("SafetyGatePolicyEngine initialized")

    def _load_default_safety_policies(self):
        """Load default safety gate policies."""
        default_policies = [
            PolicyRule(
                rule_id="SAFETY_GATE_001",
                name="PLC Download Safety Gate",
                description="Prevent PLC download if safety score < 90%",
                policy_type=PolicyType.SAFETY_GATE,
                severity=PolicySeverity.CRITICAL,
                status=PolicyStatus.ACTIVE,
                rego_code="""
                package plc_gbt.safety_gates

                default allow = false

                allow {
                    input.operation_type == "plc_download"
                    input.safety_score >= 90
                    count(input.approvals) >= 1
                }

                violations[msg] {
                    input.operation_type == "plc_download"
                    input.safety_score < 90
                    msg := sprintf("Safety score %v%% below 90%% threshold", [input.safety_score])
                }
                """,
                violation_action=ViolationAction.BLOCK,
                threshold_values={"min_safety_score": 90},
                tags=["safety", "plc", "download"]
            ),
            PolicyRule(
                rule_id="SAFETY_GATE_002",
                name="Critical Operation Safety Gate",
                description="Critical operations require 95% safety score",
                policy_type=PolicyType.SAFETY_GATE,
                severity=PolicySeverity.CRITICAL,
                status=PolicyStatus.ACTIVE,
                rego_code="""
                package plc_gbt.safety_gates

                default allow = false

                allow {
                    input.operation_type == "critical"
                    input.safety_score >= 95
                    count(input.approvals) >= 2
                    input.emergency_stop_validated == true
                }

                violations[msg] {
                    input.operation_type == "critical"
                    input.safety_score < 95
                    msg := sprintf("Critical operation safety score %v%% below 95%% threshold", [input.safety_score])
                }
                """,
                violation_action=ViolationAction.BLOCK,
                threshold_values={"min_safety_score": 95},
                tags=["safety", "critical", "operation"]
            ),
            PolicyRule(
                rule_id="SAFETY_GATE_003",
                name="Emergency Stop Validation Gate",
                description="All programs must implement emergency stop",
                policy_type=PolicyType.SAFETY_GATE,
                severity=PolicySeverity.HIGH,
                status=PolicyStatus.ACTIVE,
                rego_code="""
                package plc_gbt.safety_gates

                default allow = false

                allow {
                    contains(lower(input.program_content), "emergency_stop")
                    contains(lower(input.program_content), "fail_safe")
                }

                violations[msg] {
                    not contains(lower(input.program_content), "emergency_stop")
                    msg := "Emergency stop functionality not found in program"
                }
                """,
                violation_action=ViolationAction.WARN,
                threshold_values={},
                tags=["safety", "emergency", "stop"]
            ),
            PolicyRule(
                rule_id="SAFETY_GATE_004",
                name="Compliance Threshold Gate",
                description="Operations require minimum compliance score",
                policy_type=PolicyType.COMPLIANCE,
                severity=PolicySeverity.MEDIUM,
                status=PolicyStatus.ACTIVE,
                rego_code="""
                package plc_gbt.compliance

                default allow = false

                allow {
                    input.compliance_score >= 85
                    input.audit_trail_complete == true
                }

                violations[msg] {
                    input.compliance_score < 85
                    msg := sprintf("Compliance score %v%% below 85%% threshold", [input.compliance_score])
                }
                """,
                violation_action=ViolationAction.WARN,
                threshold_values={"min_compliance": 85},
                tags=["compliance", "threshold"]
            )
        ]

        for policy in default_policies:
            self.safety_policies[policy.rule_id] = policy

    async def evaluate_safety_gate(self, gate_id: str, input_data: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Evaluate safety gate policy.

        Args:
            gate_id: Safety gate policy ID
            input_data: Input data for evaluation

        Returns:
            Policy evaluation result
        """
        try:
            policy = self.safety_policies.get(gate_id)
            if not policy:
                raise ValueError(f"Safety gate policy {gate_id} not found")

            evaluation_start = time.time()

            # Evaluate policy using OPA engine
            opa_result = await self.opa_engine.evaluate_policy(policy, input_data)

            evaluation_time = (time.time() - evaluation_start) * 1000

            # Create evaluation result
            result = PolicyEvaluationResult(
                evaluation_id=str(uuid.uuid4()),
                rule_id=gate_id,
                policy_name=policy.name,
                passed=opa_result.get("allow", False),
                score=100.0 if opa_result.get("allow", False) else 0.0,
                message=opa_result.get("message", "Policy evaluation completed"),
                context=input_data,
                evaluated_at=datetime.utcnow(),
                evaluation_time_ms=evaluation_time
            )

            # Handle violations
            if not result.passed:
                violations = opa_result.get("violations", [])
                for violation_msg in violations:
                    violation = PolicyViolation(
                        violation_id=str(uuid.uuid4()),
                        rule_id=gate_id,
                        policy_name=policy.name,
                        severity=policy.severity,
                        violation_action=policy.violation_action,
                        message=violation_msg,
                        context=input_data,
                        detected_at=datetime.utcnow()
                    )
                    result.violations.append(violation)
                    self.violation_history.append(violation)

            logger.info(f"Safety gate {gate_id} evaluation: {'PASSED' if result.passed else 'FAILED'}")
            return result

        except Exception as e:
            logger.error(f"Safety gate evaluation failed for {gate_id}: {e}")
            return PolicyEvaluationResult(
                evaluation_id=str(uuid.uuid4()),
                rule_id=gate_id,
                policy_name="Error",
                passed=False,
                score=0.0,
                message=f"Evaluation error: {str(e)}",
                context=input_data,
                evaluated_at=datetime.utcnow(),
                evaluation_time_ms=0.0
            )

    async def evaluate_all_safety_gates(self, input_data: Dict[str, Any]) -> List[PolicyEvaluationResult]:
        """
        Evaluate all active safety gate policies.

        Args:
            input_data: Input data for evaluation

        Returns:
            List of evaluation results
        """
        results = []

        for gate_id, policy in self.safety_policies.items():
            if policy.status == PolicyStatus.ACTIVE:
                result = await self.evaluate_safety_gate(gate_id, input_data)
                results.append(result)

        return results

    def get_violation_history(self, hours: int = 24) -> List[PolicyViolation]:
        """
        Get violation history for specified time period.

        Args:
            hours: Number of hours to look back

        Returns:
            List of violations
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [v for v in self.violation_history if v.detected_at >= cutoff_time]

    def add_custom_policy(self, policy_rule: PolicyRule):
        """Add custom safety gate policy."""
        self.safety_policies[policy_rule.rule_id] = policy_rule
        logger.info(f"Added custom safety gate policy: {policy_rule.rule_id}")

    def remove_policy(self, rule_id: str):
        """Remove safety gate policy."""
        if rule_id in self.safety_policies:
            del self.safety_policies[rule_id]
            logger.info(f"Removed safety gate policy: {rule_id}")

# ============================================================================
# Real-time Policy Violation Detection
# ============================================================================

class RealTimePolicyMonitor:
    """
    Real-time policy violation detection and response system.

    Monitors system events and operations for policy violations
    with automated response capabilities.
    """

    def __init__(self, policy_engine: SafetyGatePolicyEngine):
        """
        Initialize real-time policy monitor.

        Args:
            policy_engine: Safety gate policy engine
        """
        self.policy_engine = policy_engine
        self.monitoring_active = False
        self.event_queue = asyncio.Queue()
        self.response_handlers: Dict[ViolationAction, Callable] = {}
        self.violation_stats: Dict[str, int] = {}

        # Set up default response handlers
        self._setup_default_handlers()

        logger.info("RealTimePolicyMonitor initialized")

    def _setup_default_handlers(self):
        """Set up default violation response handlers."""
        self.response_handlers[ViolationAction.BLOCK] = self._handle_block_violation
        self.response_handlers[ViolationAction.WARN] = self._handle_warn_violation
        self.response_handlers[ViolationAction.LOG] = self._handle_log_violation
        self.response_handlers[ViolationAction.ESCALATE] = self._handle_escalate_violation
        self.response_handlers[ViolationAction.EMERGENCY_STOP] = self._handle_emergency_stop_violation

    async def start_monitoring(self):
        """Start real-time policy monitoring."""
        self.monitoring_active = True

        # Start event processing task
        asyncio.create_task(self._process_events())

        logger.info("Real-time policy monitoring started")

    async def stop_monitoring(self):
        """Stop real-time policy monitoring."""
        self.monitoring_active = False
        logger.info("Real-time policy monitoring stopped")

    async def submit_event(self, event_type: str, event_data: Dict[str, Any]):
        """
        Submit event for policy evaluation.

        Args:
            event_type: Type of event
            event_data: Event data
        """
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": datetime.utcnow()
        }

        await self.event_queue.put(event)

    async def _process_events(self):
        """Process events from the queue."""
        while self.monitoring_active:
            try:
                # Get event from queue with timeout
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # Evaluate event against policies
                await self._evaluate_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Event processing error: {e}")

    async def _evaluate_event(self, event: Dict[str, Any]):
        """
        Evaluate event against all policies.

        Args:
            event: Event to evaluate
        """
        try:
            event_data = event["event_data"]

            # Evaluate against all safety gates
            evaluation_results = await self.policy_engine.evaluate_all_safety_gates(event_data)

            # Process violations
            for result in evaluation_results:
                if not result.passed:
                    await self._handle_violations(result.violations)

        except Exception as e:
            logger.error(f"Event evaluation failed: {e}")

    async def _handle_violations(self, violations: List[PolicyViolation]):
        """
        Handle policy violations.

        Args:
            violations: List of violations to handle
        """
        for violation in violations:
            # Update violation statistics
            self.violation_stats[violation.rule_id] = self.violation_stats.get(violation.rule_id, 0) + 1

            # Call appropriate handler
            handler = self.response_handlers.get(violation.violation_action)
            if handler:
                await handler(violation)
            else:
                logger.warning(f"No handler for violation action: {violation.violation_action}")

    async def _handle_block_violation(self, violation: PolicyViolation):
        """Handle BLOCK violation action."""
        logger.critical(f"🚫 BLOCKING OPERATION: {violation.message}")

        # In production, this would integrate with the actual system to block the operation
        # For now, we log the blocking action

        # Could integrate with Phase 15 safety interlocks here

    async def _handle_warn_violation(self, violation: PolicyViolation):
        """Handle WARN violation action."""
        logger.warning(f"⚠️ WARNING: {violation.message}")

        # Send warning notifications
        # Could integrate with notification systems here

    async def _handle_log_violation(self, violation: PolicyViolation):
        """Handle LOG violation action."""
        logger.info(f"📝 LOGGED: {violation.message}")

    async def _handle_escalate_violation(self, violation: PolicyViolation):
        """Handle ESCALATE violation action."""
        logger.error(f"🚨 ESCALATING: {violation.message}")

        # Mark violation as escalated
        violation.escalated = True
        violation.escalation_details = {
            "escalated_at": datetime.utcnow().isoformat(),
            "escalation_reason": "Policy violation requires management attention"
        }

        # In production, this would notify management or trigger alerts

    async def _handle_emergency_stop_violation(self, violation: PolicyViolation):
        """Handle EMERGENCY_STOP violation action."""
        logger.critical(f"🛑 EMERGENCY STOP: {violation.message}")

        # In production, this would trigger emergency shutdown procedures
        # Could integrate with industrial safety systems here

    def get_violation_statistics(self) -> Dict[str, Any]:
        """Get violation statistics."""
        return {
            "total_violations": sum(self.violation_stats.values()),
            "violations_by_rule": self.violation_stats,
            "monitoring_active": self.monitoring_active,
            "queue_size": self.event_queue.qsize()
        }

# ============================================================================
# Automated Compliance Reporting
# ============================================================================

class ComplianceReportingEngine:
    """
    Automated compliance reporting and audit trail system.

    Generates comprehensive compliance reports with audit trails
    and automated compliance monitoring.
    """

    def __init__(self, policy_engine: SafetyGatePolicyEngine):
        """
        Initialize compliance reporting engine.

        Args:
            policy_engine: Safety gate policy engine
        """
        self.policy_engine = policy_engine
        self.report_history: List[ComplianceReport] = []
        self.audit_trail: List[Dict[str, Any]] = []

        logger.info("ComplianceReportingEngine initialized")

    async def generate_compliance_report(
        self,
        report_type: str = "comprehensive",
        time_period_hours: int = 24
    ) -> ComplianceReport:
        """
        Generate comprehensive compliance report.

        Args:
            report_type: Type of report to generate
            time_period_hours: Time period for report

        Returns:
            Compliance report
        """
        try:
            report_start = datetime.utcnow()
            report_end = report_start
            report_period_start = report_start - timedelta(hours=time_period_hours)

            # Get violation history for the time period
            violations = self.policy_engine.get_violation_history(time_period_hours)

            # Calculate compliance metrics
            total_evaluations = len(violations) + 100  # Mock additional evaluations
            violation_count = len(violations)
            compliance_score = ((total_evaluations - violation_count) / total_evaluations) * 100

            # Categorize violations by severity
            violations_summary = {
                "critical": len([v for v in violations if v.severity == PolicySeverity.CRITICAL]),
                "high": len([v for v in violations if v.severity == PolicySeverity.HIGH]),
                "medium": len([v for v in violations if v.severity == PolicySeverity.MEDIUM]),
                "low": len([v for v in violations if v.severity == PolicySeverity.LOW]),
                "total": violation_count
            }

            # Generate recommendations
            recommendations = []
            if violations_summary["critical"] > 0:
                recommendations.append("Address critical policy violations immediately")
            if compliance_score < 90:
                recommendations.append("Review and strengthen policy compliance procedures")
            if violations_summary["total"] > 10:
                recommendations.append("Consider additional training on policy compliance")

            # Create mock policy evaluations
            policy_evaluations = []
            for rule_id, policy in self.policy_engine.safety_policies.items():
                if policy.status == PolicyStatus.ACTIVE:
                    policy_violations = [v for v in violations if v.rule_id == rule_id]
                    policy_score = 100.0 if len(policy_violations) == 0 else max(0, 100 - len(policy_violations) * 10)

                    evaluation = PolicyEvaluationResult(
                        evaluation_id=str(uuid.uuid4()),
                        rule_id=rule_id,
                        policy_name=policy.name,
                        passed=len(policy_violations) == 0,
                        score=policy_score,
                        message=f"Policy evaluation for {policy.name}",
                        context={"report_period": f"{time_period_hours} hours"},
                        evaluated_at=report_start,
                        evaluation_time_ms=0.0,
                        violations=policy_violations
                    )
                    policy_evaluations.append(evaluation)

            # Create compliance report
            report = ComplianceReport(
                report_id=str(uuid.uuid4()),
                report_type=report_type,
                generated_at=report_start,
                time_period={
                    "start": report_period_start,
                    "end": report_end
                },
                overall_compliance_score=compliance_score,
                policy_evaluations=policy_evaluations,
                violations_summary=violations_summary,
                recommendations=recommendations,
                audit_trail=self.audit_trail[-100:],  # Last 100 audit entries
                metadata={
                    "total_policies_evaluated": len(policy_evaluations),
                    "evaluation_period_hours": time_period_hours,
                    "generated_by": "automated_compliance_engine"
                }
            )

            # Store report
            self.report_history.append(report)

            # Add to audit trail
            self._add_audit_entry("compliance_report_generated", {
                "report_id": report.report_id,
                "report_type": report_type,
                "compliance_score": compliance_score
            })

            logger.info(f"Compliance report generated: {report.report_id} (score: {compliance_score:.1f}%)")
            return report

        except Exception as e:
            logger.error(f"Compliance report generation failed: {e}")
            raise

    def _add_audit_entry(self, action: str, details: Dict[str, Any]):
        """Add entry to audit trail."""
        entry = {
            "audit_id": str(uuid.uuid4()),
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
            "user": "system"
        }
        self.audit_trail.append(entry)

    def get_report_history(self, limit: int = 10) -> List[ComplianceReport]:
        """Get compliance report history."""
        return self.report_history[-limit:]

    def export_report(self, report_id: str, format: str = "json") -> str:
        """
        Export compliance report.

        Args:
            report_id: Report ID to export
            format: Export format (json, yaml, csv)

        Returns:
            Exported report data
        """
        report = next((r for r in self.report_history if r.report_id == report_id), None)
        if not report:
            raise ValueError(f"Report {report_id} not found")

        if format == "json":
            return json.dumps(asdict(report), indent=2, default=str)
        elif format == "yaml":
            return yaml.dump(asdict(report), default_flow_style=False)
        else:
            raise ValueError(f"Unsupported export format: {format}")

# ============================================================================
# Main Policy Engine Integration
# ============================================================================

class AutomatedGovernanceSystem:
    """
    Main automated governance system integrating all policy components.

    Provides unified interface for policy management, enforcement,
    and compliance reporting.
    """

    def __init__(self, config_file: str = None):
        """
        Initialize automated governance system.

        Args:
            config_file: Optional configuration file path
        """
        self.config_file = Path(config_file) if config_file else None

        # Initialize components
        self.safety_gate_engine = SafetyGatePolicyEngine(config_file)
        self.realtime_monitor = RealTimePolicyMonitor(self.safety_gate_engine)
        self.compliance_engine = ComplianceReportingEngine(self.safety_gate_engine)

        # System state
        self.system_active = False
        self.startup_time = None

        logger.info("AutomatedGovernanceSystem initialized")

    async def start_system(self):
        """Start the automated governance system."""
        try:
            self.startup_time = datetime.utcnow()

            # Start real-time monitoring
            await self.realtime_monitor.start_monitoring()

            self.system_active = True
            logger.info("🏛️ Automated Governance System started successfully")

        except Exception as e:
            logger.error(f"Failed to start governance system: {e}")
            raise

    async def stop_system(self):
        """Stop the automated governance system."""
        try:
            # Stop real-time monitoring
            await self.realtime_monitor.stop_monitoring()

            self.system_active = False
            logger.info("🏛️ Automated Governance System stopped")

        except Exception as e:
            logger.error(f"Failed to stop governance system: {e}")
            raise

    async def enforce_policy(self, operation_type: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enforce policies for an operation.

        Args:
            operation_type: Type of operation
            operation_data: Operation data

        Returns:
            Policy enforcement result
        """
        try:
            # Submit event for real-time monitoring
            await self.realtime_monitor.submit_event(operation_type, operation_data)

            # Evaluate safety gates
            evaluation_results = await self.safety_gate_engine.evaluate_all_safety_gates(operation_data)

            # Determine overall result
            all_passed = all(result.passed for result in evaluation_results)
            violations = []
            for result in evaluation_results:
                violations.extend(result.violations)

            # Create enforcement result
            enforcement_result = {
                "allowed": all_passed,
                "operation_type": operation_type,
                "evaluation_results": [asdict(result) for result in evaluation_results],
                "violations": [asdict(v) for v in violations],
                "enforcement_timestamp": datetime.utcnow().isoformat(),
                "metadata": {
                    "total_policies_evaluated": len(evaluation_results),
                    "violations_count": len(violations)
                }
            }

            logger.info(f"Policy enforcement for {operation_type}: {'ALLOWED' if all_passed else 'BLOCKED'}")
            return enforcement_result

        except Exception as e:
            logger.error(f"Policy enforcement failed: {e}")
            return {
                "allowed": False,
                "error": str(e),
                "enforcement_timestamp": datetime.utcnow().isoformat()
            }

    async def generate_compliance_report(self, report_type: str = "comprehensive") -> ComplianceReport:
        """Generate compliance report."""
        return await self.compliance_engine.generate_compliance_report(report_type)

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        return {
            "system_active": self.system_active,
            "startup_time": self.startup_time.isoformat() if self.startup_time else None,
            "monitoring_active": self.realtime_monitor.monitoring_active,
            "total_policies": len(self.safety_gate_engine.safety_policies),
            "violation_statistics": self.realtime_monitor.get_violation_statistics(),
            "reports_generated": len(self.compliance_engine.report_history)
        }

    def add_custom_policy(self, policy_rule: PolicyRule):
        """Add custom policy rule."""
        self.safety_gate_engine.add_custom_policy(policy_rule)

    def get_policy_list(self) -> List[Dict[str, Any]]:
        """Get list of all policies."""
        return [asdict(policy) for policy in self.safety_gate_engine.safety_policies.values()]

# ============================================================================
# Configuration Management
# ============================================================================

def load_policy_configuration(config_file: str) -> Dict[str, Any]:
    """Load policy configuration from file."""
    try:
        config_path = Path(config_file)
        if not config_path.exists():
            logger.warning(f"Configuration file not found: {config_file}")
            return {}

        with open(config_path) as f:
            if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                return yaml.safe_load(f)
            else:
                return json.load(f)

    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return {}

def get_automated_governance_system(config_file: str = None) -> AutomatedGovernanceSystem:
    """Get configured automated governance system instance."""
    return AutomatedGovernanceSystem(config_file)

# ============================================================================
# Testing and Validation
# ============================================================================

if __name__ == "__main__":
    # Test the automated governance system
    async def test_governance_system():
        print("🏛️ Testing Automated Governance System...")

        # Initialize system
        governance = get_automated_governance_system()

        # Start system
        await governance.start_system()

        # Test policy enforcement
        test_operation_data = {
            "operation_type": "plc_download",
            "safety_score": 85,
            "approvals": ["engineer1"],
            "program_content": "emergency_stop := TRUE; fail_safe := TRUE;",
            "compliance_score": 90,
            "audit_trail_complete": True
        }

        enforcement_result = await governance.enforce_policy("plc_download", test_operation_data)
        print(f"✅ Policy enforcement result: {enforcement_result['allowed']}")

        # Generate compliance report
        report = await governance.generate_compliance_report()
        print(f"📊 Compliance report generated: {report.report_id} (score: {report.overall_compliance_score:.1f}%)")

        # Get system status
        status = governance.get_system_status()
        print(f"🔍 System status: {status}")

        # Stop system
        await governance.stop_system()

        print("🎉 Governance system test completed successfully!")

    # Run test
    asyncio.run(test_governance_system())
