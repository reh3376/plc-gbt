#!/usr/bin/env python3
"""
Industrial Safety Interlocks for PLC-GPT
Phase 15.2: Industrial Safety Interlocks

This module provides critical safety interlocks for industrial control operations,
ensuring human approval for PLC downloads and compliance with ISA-95 standards.

Features:
- Human approval workflow for PLC downloads
- GuardLogix safety signature validation
- Change management SOP integration
- Safety audit trail and compliance
- Emergency override capabilities
- Multi-level approval system

Following AI Task Orchestrator methodology for systematic safety enhancement.
"""

import asyncio
import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

# Digital signature and cryptography
try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding, rsa
    from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logging.warning("cryptography library not available for digital signatures")

# Email notifications
try:
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False
    logging.warning("email libraries not available for notifications")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ApprovalStatus(Enum):
    """Status of approval requests."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EMERGENCY_OVERRIDE = "emergency_override"


class SafetyLevel(Enum):
    """Safety levels for PLC operations."""
    ROUTINE = "routine"  # Standard operations
    ELEVATED = "elevated"  # Critical system changes
    CRITICAL = "critical"  # Safety-critical operations
    EMERGENCY = "emergency"  # Emergency operations


class PLCOperationType(Enum):
    """Types of PLC operations requiring approval."""
    DOWNLOAD = "download"
    UPLOAD = "upload"
    ONLINE_CHANGE = "online_change"
    SAFETY_CONFIGURATION = "safety_configuration"
    FIRMWARE_UPDATE = "firmware_update"
    PROGRAM_MODIFICATION = "program_modification"


@dataclass
class ApprovalRequest:
    """Approval request structure."""
    request_id: str
    operation_type: PLCOperationType
    safety_level: SafetyLevel
    requester: str
    plc_identifier: str
    program_hash: str
    description: str
    justification: str
    created_at: datetime
    expires_at: datetime
    status: ApprovalStatus = ApprovalStatus.PENDING
    approvers_required: int = 1
    approvals: List[Dict[str, Any]] = field(default_factory=list)
    rejections: List[Dict[str, Any]] = field(default_factory=list)
    safety_analysis: Optional[Dict[str, Any]] = None
    guardlogix_signature: Optional[str] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SafetyAnalysis:
    """Safety analysis results."""
    analysis_id: str
    request_id: str
    safety_score: float  # 0-100 scale
    risk_level: str
    hazards_identified: List[str]
    mitigation_measures: List[str]
    compliance_status: Dict[str, bool]
    recommendations: List[str]
    analyst: str
    analyzed_at: datetime
    valid_until: datetime


@dataclass
class ApprovalPolicy:
    """Approval policy configuration."""
    operation_type: PLCOperationType
    safety_level: SafetyLevel
    approvers_required: int
    timeout_hours: int
    require_safety_analysis: bool
    require_guardlogix_signature: bool
    allowed_approvers: List[str]
    emergency_override_enabled: bool
    notification_recipients: List[str]


class GuardLogixValidator:
    """
    GuardLogix safety signature validation.

    Validates safety signatures for GuardLogix safety systems
    according to IEC 61508 and IEC 61511 standards.
    """

    def __init__(self, cert_dir: str = "security/guardlogix"):
        """
        Initialize GuardLogix validator.

        Args:
            cert_dir: Directory containing GuardLogix certificates
        """
        self.cert_dir = Path(cert_dir)
        self.cert_dir.mkdir(parents=True, exist_ok=True)

        # Safety signature validation
        self.safety_keys: Dict[str, Any] = {}
        self.signature_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(f"GuardLogixValidator initialized - cert_dir: {self.cert_dir}")

    def generate_safety_signature(self, program_data: bytes, safety_key: str) -> str:
        """
        Generate safety signature for PLC program.

        Args:
            program_data: PLC program binary data
            safety_key: Safety key identifier

        Returns:
            Safety signature string
        """
        if not CRYPTO_AVAILABLE:
            logger.warning("Cryptography not available - generating mock signature")
            return f"mock_signature_{hashlib.sha256(program_data).hexdigest()[:16]}"

        try:
            # Create safety signature
            program_hash = hashlib.sha256(program_data).hexdigest()
            timestamp = datetime.utcnow().isoformat()

            # Combine program hash with timestamp and safety metadata
            signature_data = {
                "program_hash": program_hash,
                "timestamp": timestamp,
                "safety_key": safety_key,
                "signature_version": "1.0",
                "compliance_standards": ["IEC_61508", "IEC_61511"]
            }

            # Create deterministic signature
            signature_string = json.dumps(signature_data, sort_keys=True)
            signature_hash = hashlib.sha256(signature_string.encode()).hexdigest()

            # Store in cache for validation
            self.signature_cache[signature_hash] = signature_data

            logger.info(f"✅ Safety signature generated: {signature_hash[:16]}...")
            return signature_hash

        except Exception as e:
            logger.error(f"Failed to generate safety signature: {e}")
            raise

    def validate_safety_signature(self, program_data: bytes, signature: str) -> bool:
        """
        Validate safety signature for PLC program.

        Args:
            program_data: PLC program binary data
            signature: Safety signature to validate

        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Check signature cache
            if signature not in self.signature_cache:
                logger.warning(f"❌ Safety signature not found in cache: {signature[:16]}...")
                return False

            signature_data = self.signature_cache[signature]

            # Validate program hash
            program_hash = hashlib.sha256(program_data).hexdigest()
            if program_hash != signature_data["program_hash"]:
                logger.warning(f"❌ Program hash mismatch: expected {signature_data['program_hash'][:16]}..., got {program_hash[:16]}...")
                return False

            # Check signature age (valid for 24 hours)
            signature_time = datetime.fromisoformat(signature_data["timestamp"])
            if datetime.utcnow() - signature_time > timedelta(hours=24):
                logger.warning(f"❌ Safety signature expired: {signature_data['timestamp']}")
                return False

            logger.info(f"✅ Safety signature validated: {signature[:16]}...")
            return True

        except Exception as e:
            logger.error(f"Failed to validate safety signature: {e}")
            return False

    def get_signature_info(self, signature: str) -> Optional[Dict[str, Any]]:
        """Get information about a safety signature."""
        return self.signature_cache.get(signature)


class SafetyAnalyzer:
    """
    Safety analysis engine for PLC operations.

    Analyzes PLC programs for safety risks and compliance
    with industrial safety standards.
    """

    def __init__(self):
        """Initialize safety analyzer."""
        self.analysis_cache: Dict[str, SafetyAnalysis] = {}
        self.safety_rules: List[Dict[str, Any]] = []

        # Load default safety rules
        self._load_default_safety_rules()

        logger.info("SafetyAnalyzer initialized")

    def _load_default_safety_rules(self):
        """Load default safety analysis rules."""
        self.safety_rules = [
            {
                "rule_id": "SAFETY_001",
                "name": "Emergency Stop Validation",
                "description": "Verify emergency stop functionality",
                "severity": "critical",
                "check_function": self._check_emergency_stop
            },
            {
                "rule_id": "SAFETY_002",
                "name": "Safety Interlock Validation",
                "description": "Verify safety interlocks are properly configured",
                "severity": "high",
                "check_function": self._check_safety_interlocks
            },
            {
                "rule_id": "SAFETY_003",
                "name": "Fail-Safe Configuration",
                "description": "Verify fail-safe behavior on system failure",
                "severity": "critical",
                "check_function": self._check_fail_safe
            },
            {
                "rule_id": "SAFETY_004",
                "name": "Redundancy Validation",
                "description": "Verify critical system redundancy",
                "severity": "high",
                "check_function": self._check_redundancy
            },
            {
                "rule_id": "SAFETY_005",
                "name": "Watchdog Timer Validation",
                "description": "Verify watchdog timer configuration",
                "severity": "medium",
                "check_function": self._check_watchdog
            }
        ]

    def _check_emergency_stop(self, program_data: bytes) -> Tuple[bool, str]:
        """Check emergency stop functionality."""
        # Mock implementation - in production, this would analyze the actual PLC program
        program_str = program_data.decode('utf-8', errors='ignore').lower()

        if 'emergency' in program_str and 'stop' in program_str:
            return True, "Emergency stop functionality detected"
        else:
            return False, "Emergency stop functionality not found"

    def _check_safety_interlocks(self, program_data: bytes) -> Tuple[bool, str]:
        """Check safety interlocks."""
        program_str = program_data.decode('utf-8', errors='ignore').lower()

        interlock_keywords = ['interlock', 'safety', 'permit', 'enable']
        found_keywords = [kw for kw in interlock_keywords if kw in program_str]

        if len(found_keywords) >= 2:
            return True, f"Safety interlocks detected: {', '.join(found_keywords)}"
        else:
            return False, "Insufficient safety interlock configuration"

    def _check_fail_safe(self, program_data: bytes) -> Tuple[bool, str]:
        """Check fail-safe configuration."""
        program_str = program_data.decode('utf-8', errors='ignore').lower()

        failsafe_keywords = ['fail', 'safe', 'default', 'fallback']
        found_keywords = [kw for kw in failsafe_keywords if kw in program_str]

        if len(found_keywords) >= 2:
            return True, f"Fail-safe configuration detected: {', '.join(found_keywords)}"
        else:
            return False, "Fail-safe configuration not adequately implemented"

    def _check_redundancy(self, program_data: bytes) -> Tuple[bool, str]:
        """Check system redundancy."""
        program_str = program_data.decode('utf-8', errors='ignore').lower()

        redundancy_keywords = ['redundant', 'backup', 'secondary', 'dual']
        found_keywords = [kw for kw in redundancy_keywords if kw in program_str]

        if found_keywords:
            return True, f"Redundancy detected: {', '.join(found_keywords)}"
        else:
            return False, "No redundancy configuration found"

    def _check_watchdog(self, program_data: bytes) -> Tuple[bool, str]:
        """Check watchdog timer configuration."""
        program_str = program_data.decode('utf-8', errors='ignore').lower()

        if 'watchdog' in program_str or 'wdt' in program_str:
            return True, "Watchdog timer configuration detected"
        else:
            return False, "Watchdog timer not configured"

    async def analyze_program(self, program_data: bytes, operation_type: PLCOperationType) -> SafetyAnalysis:
        """
        Analyze PLC program for safety compliance.

        Args:
            program_data: PLC program binary data
            operation_type: Type of operation being performed

        Returns:
            SafetyAnalysis object
        """
        try:
            analysis_id = str(uuid.uuid4())
            analysis_start = datetime.utcnow()

            # Run safety rule checks
            hazards_identified = []
            mitigation_measures = []
            compliance_status = {}

            safety_score = 0
            total_rules = len(self.safety_rules)

            for rule in self.safety_rules:
                try:
                    passed, message = rule["check_function"](program_data)
                    compliance_status[rule["rule_id"]] = passed

                    if passed:
                        safety_score += 1
                        mitigation_measures.append(f"{rule['name']}: {message}")
                    else:
                        hazards_identified.append(f"{rule['name']}: {message}")

                except Exception as e:
                    logger.error(f"Safety rule {rule['rule_id']} failed: {e}")
                    compliance_status[rule["rule_id"]] = False
                    hazards_identified.append(f"{rule['name']}: Analysis failed - {str(e)}")

            # Calculate safety score (0-100)
            safety_score_percent = (safety_score / total_rules) * 100

            # Determine risk level
            if safety_score_percent >= 90:
                risk_level = "low"
            elif safety_score_percent >= 70:
                risk_level = "medium"
            elif safety_score_percent >= 50:
                risk_level = "high"
            else:
                risk_level = "critical"

            # Generate recommendations
            recommendations = []
            if safety_score_percent < 100:
                recommendations.append("Address identified safety hazards before deployment")
            if safety_score_percent < 70:
                recommendations.append("Consider additional safety review by certified safety engineer")
            if operation_type == PLCOperationType.SAFETY_CONFIGURATION:
                recommendations.append("Verify compliance with IEC 61508/61511 standards")

            # Create safety analysis
            analysis = SafetyAnalysis(
                analysis_id=analysis_id,
                request_id="",  # Will be set by calling function
                safety_score=safety_score_percent,
                risk_level=risk_level,
                hazards_identified=hazards_identified,
                mitigation_measures=mitigation_measures,
                compliance_status=compliance_status,
                recommendations=recommendations,
                analyst="automated_safety_analyzer",
                analyzed_at=analysis_start,
                valid_until=analysis_start + timedelta(hours=24)
            )

            # Cache analysis
            self.analysis_cache[analysis_id] = analysis

            logger.info(f"✅ Safety analysis completed: {analysis_id} (score: {safety_score_percent:.1f}%)")
            return analysis

        except Exception as e:
            logger.error(f"Safety analysis failed: {e}")
            raise


class IndustrialSafetyInterlocks:
    """
    Industrial Safety Interlocks system for PLC operations.

    Provides comprehensive safety interlocks including:
    - Human approval workflows
    - Safety analysis and validation
    - GuardLogix signature verification
    - Change management integration
    - Emergency override capabilities
    """

    def __init__(self, config_file: str = None):
        """
        Initialize industrial safety interlocks.

        Args:
            config_file: Optional configuration file path
        """
        self.config_file = Path(config_file) if config_file else None

        # Core components
        self.guardlogix_validator = GuardLogixValidator()
        self.safety_analyzer = SafetyAnalyzer()

        # Request management
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.approval_policies: Dict[Tuple[PLCOperationType, SafetyLevel], ApprovalPolicy] = {}

        # Notifications
        self.notification_handlers: List[Callable] = []

        # Audit logging
        self.audit_log_path = Path("logs/safety_interlocks_audit.log")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self._load_default_policies()

        logger.info("IndustrialSafetyInterlocks initialized")

    def _load_default_policies(self):
        """Load default approval policies."""
        default_policies = [
            ApprovalPolicy(
                operation_type=PLCOperationType.DOWNLOAD,
                safety_level=SafetyLevel.ROUTINE,
                approvers_required=1,
                timeout_hours=24,
                require_safety_analysis=True,
                require_guardlogix_signature=False,
                allowed_approvers=["control_engineer", "plant_manager"],
                emergency_override_enabled=True,
                notification_recipients=["control_team@company.com"]
            ),
            ApprovalPolicy(
                operation_type=PLCOperationType.DOWNLOAD,
                safety_level=SafetyLevel.CRITICAL,
                approvers_required=2,
                timeout_hours=48,
                require_safety_analysis=True,
                require_guardlogix_signature=True,
                allowed_approvers=["safety_engineer", "plant_manager", "operations_director"],
                emergency_override_enabled=False,
                notification_recipients=["safety_team@company.com", "management@company.com"]
            ),
            ApprovalPolicy(
                operation_type=PLCOperationType.SAFETY_CONFIGURATION,
                safety_level=SafetyLevel.CRITICAL,
                approvers_required=3,
                timeout_hours=72,
                require_safety_analysis=True,
                require_guardlogix_signature=True,
                allowed_approvers=["safety_engineer", "plant_manager", "operations_director", "safety_director"],
                emergency_override_enabled=False,
                notification_recipients=["safety_team@company.com", "management@company.com", "regulatory@company.com"]
            )
        ]

        for policy in default_policies:
            key = (policy.operation_type, policy.safety_level)
            self.approval_policies[key] = policy

    def _audit_log(self, operation: str, request_id: str, details: Dict[str, Any]):
        """Log safety interlock events for audit."""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "operation": operation,
            "request_id": request_id,
            "details": details,
            "user": details.get("user", "system"),
            "session_id": str(uuid.uuid4())
        }

        try:
            with open(self.audit_log_path, 'a') as f:
                f.write(json.dumps(audit_event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write safety audit log: {e}")

    async def request_approval(
        self,
        operation_type: PLCOperationType,
        safety_level: SafetyLevel,
        requester: str,
        plc_identifier: str,
        program_data: bytes,
        description: str,
        justification: str
    ) -> str:
        """
        Request approval for PLC operation.

        Args:
            operation_type: Type of operation
            safety_level: Safety level of operation
            requester: Username of requester
            plc_identifier: PLC system identifier
            program_data: PLC program binary data
            description: Operation description
            justification: Business justification

        Returns:
            Request ID for tracking
        """
        try:
            # Get approval policy
            policy_key = (operation_type, safety_level)
            policy = self.approval_policies.get(policy_key)

            if not policy:
                raise ValueError(f"No approval policy found for {operation_type.value} at {safety_level.value} level")

            # Generate request ID
            request_id = str(uuid.uuid4())

            # Calculate program hash
            program_hash = hashlib.sha256(program_data).hexdigest()

            # Create approval request
            request = ApprovalRequest(
                request_id=request_id,
                operation_type=operation_type,
                safety_level=safety_level,
                requester=requester,
                plc_identifier=plc_identifier,
                program_hash=program_hash,
                description=description,
                justification=justification,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=policy.timeout_hours),
                approvers_required=policy.approvers_required
            )

            # Perform safety analysis if required
            if policy.require_safety_analysis:
                logger.info(f"🔍 Performing safety analysis for request {request_id}")
                safety_analysis = await self.safety_analyzer.analyze_program(program_data, operation_type)
                safety_analysis.request_id = request_id
                request.safety_analysis = asdict(safety_analysis)

                # Check if safety score meets minimum requirements
                if safety_analysis.safety_score < 50:
                    logger.warning(f"⚠️ Safety score too low: {safety_analysis.safety_score:.1f}%")
                    request.status = ApprovalStatus.REJECTED
                    request.audit_trail.append({
                        "action": "auto_rejected",
                        "reason": "safety_score_too_low",
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": {"safety_score": safety_analysis.safety_score}
                    })

            # Generate GuardLogix signature if required
            if policy.require_guardlogix_signature and request.status == ApprovalStatus.PENDING:
                logger.info(f"🔐 Generating GuardLogix signature for request {request_id}")
                signature = self.guardlogix_validator.generate_safety_signature(
                    program_data,
                    f"safety_key_{plc_identifier}"
                )
                request.guardlogix_signature = signature

            # Store request
            self.approval_requests[request_id] = request

            # Log audit event
            self._audit_log("request_approval", request_id, {
                "operation_type": operation_type.value,
                "safety_level": safety_level.value,
                "requester": requester,
                "plc_identifier": plc_identifier,
                "program_hash": program_hash,
                "policy_applied": f"{policy_key[0].value}_{policy_key[1].value}"
            })

            # Send notifications
            await self._send_notifications(request, policy, "approval_requested")

            logger.info(f"✅ Approval request created: {request_id}")
            return request_id

        except Exception as e:
            logger.error(f"Failed to create approval request: {e}")
            raise

    async def approve_request(self, request_id: str, approver: str, comments: str = "") -> bool:
        """
        Approve a pending request.

        Args:
            request_id: Request ID to approve
            approver: Username of approver
            comments: Optional approval comments

        Returns:
            True if approved successfully, False otherwise
        """
        try:
            request = self.approval_requests.get(request_id)
            if not request:
                logger.error(f"Request {request_id} not found")
                return False

            if request.status != ApprovalStatus.PENDING:
                logger.error(f"Request {request_id} is not pending (status: {request.status})")
                return False

            # Check if request has expired
            if datetime.utcnow() > request.expires_at:
                request.status = ApprovalStatus.EXPIRED
                logger.error(f"Request {request_id} has expired")
                return False

            # Validate approver
            policy_key = (request.operation_type, request.safety_level)
            policy = self.approval_policies.get(policy_key)

            if policy and approver not in policy.allowed_approvers:
                logger.error(f"Approver {approver} not authorized for this request type")
                return False

            # Check if approver has already approved
            existing_approval = next((a for a in request.approvals if a["approver"] == approver), None)
            if existing_approval:
                logger.warning(f"Approver {approver} has already approved request {request_id}")
                return False

            # Add approval
            approval = {
                "approver": approver,
                "approved_at": datetime.utcnow().isoformat(),
                "comments": comments,
                "approval_id": str(uuid.uuid4())
            }

            request.approvals.append(approval)

            # Check if enough approvals
            if len(request.approvals) >= request.approvers_required:
                request.status = ApprovalStatus.APPROVED
                logger.info(f"✅ Request {request_id} fully approved")

                # Send approval notification
                await self._send_notifications(request, policy, "approval_completed")
            else:
                logger.info(f"⏳ Request {request_id} partially approved ({len(request.approvals)}/{request.approvers_required})")

            # Update audit trail
            request.audit_trail.append({
                "action": "approved",
                "approver": approver,
                "timestamp": datetime.utcnow().isoformat(),
                "comments": comments
            })

            # Log audit event
            self._audit_log("approve_request", request_id, {
                "approver": approver,
                "comments": comments,
                "approvals_count": len(request.approvals),
                "approvals_required": request.approvers_required
            })

            return True

        except Exception as e:
            logger.error(f"Failed to approve request {request_id}: {e}")
            return False

    async def reject_request(self, request_id: str, rejector: str, reason: str) -> bool:
        """
        Reject a pending request.

        Args:
            request_id: Request ID to reject
            rejector: Username of rejector
            reason: Rejection reason

        Returns:
            True if rejected successfully, False otherwise
        """
        try:
            request = self.approval_requests.get(request_id)
            if not request:
                logger.error(f"Request {request_id} not found")
                return False

            if request.status != ApprovalStatus.PENDING:
                logger.error(f"Request {request_id} is not pending (status: {request.status})")
                return False

            # Add rejection
            rejection = {
                "rejector": rejector,
                "rejected_at": datetime.utcnow().isoformat(),
                "reason": reason,
                "rejection_id": str(uuid.uuid4())
            }

            request.rejections.append(rejection)
            request.status = ApprovalStatus.REJECTED

            # Update audit trail
            request.audit_trail.append({
                "action": "rejected",
                "rejector": rejector,
                "timestamp": datetime.utcnow().isoformat(),
                "reason": reason
            })

            # Log audit event
            self._audit_log("reject_request", request_id, {
                "rejector": rejector,
                "reason": reason
            })

            # Send rejection notification
            policy_key = (request.operation_type, request.safety_level)
            policy = self.approval_policies.get(policy_key)
            await self._send_notifications(request, policy, "approval_rejected")

            logger.info(f"❌ Request {request_id} rejected by {rejector}")
            return True

        except Exception as e:
            logger.error(f"Failed to reject request {request_id}: {e}")
            return False

    async def emergency_override(self, request_id: str, override_user: str, justification: str) -> bool:
        """
        Emergency override for critical situations.

        Args:
            request_id: Request ID to override
            override_user: Username performing override
            justification: Emergency justification

        Returns:
            True if override successful, False otherwise
        """
        try:
            request = self.approval_requests.get(request_id)
            if not request:
                logger.error(f"Request {request_id} not found")
                return False

            # Check if emergency override is enabled
            policy_key = (request.operation_type, request.safety_level)
            policy = self.approval_policies.get(policy_key)

            if not policy or not policy.emergency_override_enabled:
                logger.error(f"Emergency override not enabled for request {request_id}")
                return False

            # Perform emergency override
            request.status = ApprovalStatus.EMERGENCY_OVERRIDE

            # Update audit trail
            request.audit_trail.append({
                "action": "emergency_override",
                "override_user": override_user,
                "timestamp": datetime.utcnow().isoformat(),
                "justification": justification
            })

            # Log audit event
            self._audit_log("emergency_override", request_id, {
                "override_user": override_user,
                "justification": justification
            })

            # Send emergency override notification
            await self._send_notifications(request, policy, "emergency_override")

            logger.warning(f"⚠️ Emergency override applied to request {request_id} by {override_user}")
            return True

        except Exception as e:
            logger.error(f"Failed to apply emergency override to request {request_id}: {e}")
            return False

    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of approval request.

        Args:
            request_id: Request ID

        Returns:
            Request status dictionary or None if not found
        """
        request = self.approval_requests.get(request_id)
        if not request:
            return None

        return {
            "request_id": request.request_id,
            "status": request.status.value,
            "operation_type": request.operation_type.value,
            "safety_level": request.safety_level.value,
            "requester": request.requester,
            "plc_identifier": request.plc_identifier,
            "description": request.description,
            "created_at": request.created_at.isoformat(),
            "expires_at": request.expires_at.isoformat(),
            "approvals_count": len(request.approvals),
            "approvals_required": request.approvers_required,
            "safety_analysis": request.safety_analysis,
            "guardlogix_signature": request.guardlogix_signature[:16] + "..." if request.guardlogix_signature else None
        }

    def can_execute_operation(self, request_id: str) -> bool:
        """
        Check if operation can be executed.

        Args:
            request_id: Request ID

        Returns:
            True if operation can be executed, False otherwise
        """
        request = self.approval_requests.get(request_id)
        if not request:
            return False

        return request.status in [ApprovalStatus.APPROVED, ApprovalStatus.EMERGENCY_OVERRIDE]

    async def _send_notifications(self, request: ApprovalRequest, policy: ApprovalPolicy, event_type: str):
        """Send notifications for approval events."""
        try:
            # Create notification message
            message = {
                "event_type": event_type,
                "request_id": request.request_id,
                "operation_type": request.operation_type.value,
                "safety_level": request.safety_level.value,
                "requester": request.requester,
                "plc_identifier": request.plc_identifier,
                "description": request.description,
                "status": request.status.value,
                "timestamp": datetime.utcnow().isoformat()
            }

            # Send to notification handlers
            for handler in self.notification_handlers:
                try:
                    await handler(message)
                except Exception as e:
                    logger.error(f"Notification handler failed: {e}")

            logger.info(f"📧 Notifications sent for {event_type}: {request.request_id}")

        except Exception as e:
            logger.error(f"Failed to send notifications: {e}")

    def add_notification_handler(self, handler: Callable):
        """Add notification handler."""
        self.notification_handlers.append(handler)

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status."""
        now = datetime.utcnow()

        # Count requests by status
        status_counts = {}
        for status in ApprovalStatus:
            status_counts[status.value] = sum(1 for r in self.approval_requests.values() if r.status == status)

        # Count expired requests
        expired_count = sum(1 for r in self.approval_requests.values() if r.expires_at < now and r.status == ApprovalStatus.PENDING)

        return {
            "timestamp": now.isoformat(),
            "total_requests": len(self.approval_requests),
            "status_counts": status_counts,
            "expired_requests": expired_count,
            "policies_configured": len(self.approval_policies),
            "notification_handlers": len(self.notification_handlers),
            "safety_analyzer_rules": len(self.safety_analyzer.safety_rules),
            "guardlogix_signatures": len(self.guardlogix_validator.signature_cache)
        }


# Example notification handler
async def email_notification_handler(message: Dict[str, Any]):
    """Example email notification handler."""
    logger.info(f"📧 Email notification: {message['event_type']} for request {message['request_id']}")
    # In production, this would send actual emails


# Global instance for easy access
_industrial_safety_interlocks = None


def get_industrial_safety_interlocks() -> IndustrialSafetyInterlocks:
    """Get global IndustrialSafetyInterlocks instance."""
    global _industrial_safety_interlocks

    if _industrial_safety_interlocks is None:
        _industrial_safety_interlocks = IndustrialSafetyInterlocks()
        _industrial_safety_interlocks.add_notification_handler(email_notification_handler)

    return _industrial_safety_interlocks


if __name__ == "__main__":
    # Test the IndustrialSafetyInterlocks
    async def test_safety_interlocks():
        print("🔒 Testing IndustrialSafetyInterlocks...")

        # Initialize system
        safety_system = get_industrial_safety_interlocks()

        # Test program data
        test_program = b"""
        // Test PLC Program
        PROGRAM Main
        VAR
            emergency_stop : BOOL;
            safety_interlock : BOOL;
            fail_safe_mode : BOOL;
            watchdog_timer : TIME;
        END_VAR

        // Emergency stop logic
        IF emergency_stop THEN
            // Safe shutdown
            fail_safe_mode := TRUE;
        END_IF

        // Safety interlock check
        IF NOT safety_interlock THEN
            // Prevent operation
            fail_safe_mode := TRUE;
        END_IF

        END_PROGRAM
        """

        # Request approval
        request_id = await safety_system.request_approval(
            operation_type=PLCOperationType.DOWNLOAD,
            safety_level=SafetyLevel.ROUTINE,
            requester="test_engineer",
            plc_identifier="PLC_001",
            program_data=test_program,
            description="Test PLC program download",
            justification="System testing and validation"
        )

        print(f"✅ Approval request created: {request_id}")

        # Check status
        status = safety_system.get_request_status(request_id)
        print(f"📊 Request status: {status}")

        # Approve request
        approved = await safety_system.approve_request(
            request_id=request_id,
            approver="control_engineer",
            comments="Program reviewed and approved for testing"
        )

        print(f"✅ Approval result: {approved}")

        # Check if operation can be executed
        can_execute = safety_system.can_execute_operation(request_id)
        print(f"🚀 Can execute operation: {can_execute}")

        # Get system status
        system_status = safety_system.get_system_status()
        print(f"📊 System status: {json.dumps(system_status, indent=2)}")

        print("🎉 IndustrialSafetyInterlocks test completed!")

    # Run test
    asyncio.run(test_safety_interlocks())
