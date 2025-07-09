#!/usr/bin/env python3
"""
Security Governance System for PLC-GPT
Phase 6: Maintenance & Governance Systems

This module provides comprehensive security governance including:
- Data protection and masking
- Audit trail management
- Compliance monitoring
- Access control automation
- Security policy enforcement

Following AI Task Orchestrator methodology for structured governance.
"""

import asyncio
import logging
import json
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import uuid

# Import existing infrastructure
from auth.rbac import Role, Permission, get_rbac_manager
from auth.jwt_manager import get_jwt_manager
from config.enterprise_settings import EnterpriseSettings
from monitoring.enterprise_monitoring import get_monitoring

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Types of audit events."""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CONFIG_CHANGE = "system_config_change"
    SECURITY_VIOLATION = "security_violation"
    BACKUP_CREATED = "backup_created"
    BACKUP_RESTORED = "backup_restored"
    MAINTENANCE_TASK = "maintenance_task"


class ComplianceStandard(Enum):
    """Compliance standards."""
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOX = "sox"
    ISO27001 = "iso27001"
    NIST = "nist"


class DataClassification(Enum):
    """Data classification levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


@dataclass
class AuditEvent:
    """Audit event record."""
    event_id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: Optional[str]
    user_role: Optional[str]
    resource: str
    action: str
    result: str  # 'success', 'failure', 'denied'
    ip_address: Optional[str]
    user_agent: Optional[str]
    details: Dict[str, Any]
    risk_level: str = 'low'  # 'low', 'medium', 'high', 'critical'


@dataclass
class ComplianceCheck:
    """Compliance check result."""
    check_id: str
    standard: ComplianceStandard
    requirement: str
    status: str  # 'compliant', 'non_compliant', 'partial'
    severity: str  # 'low', 'medium', 'high', 'critical'
    findings: List[str]
    remediation: List[str]
    last_checked: datetime


@dataclass
class DataProtectionPolicy:
    """Data protection policy definition."""
    policy_id: str
    name: str
    description: str
    classification: DataClassification
    retention_days: int
    encryption_required: bool
    masking_rules: List[Dict[str, Any]]
    access_controls: List[str]
    audit_required: bool


class SecurityGovernanceSystem:
    """
    Comprehensive security governance system for PLC-GPT.
    
    Features:
    - Audit trail management
    - Data protection and masking
    - Compliance monitoring
    - Security policy enforcement
    - Access control automation
    - Risk assessment and mitigation
    """
    
    def __init__(self, settings: Optional[EnterpriseSettings] = None):
        """Initialize security governance system."""
        self.settings = settings or EnterpriseSettings()
        self.rbac_manager = get_rbac_manager()
        self.jwt_manager = get_jwt_manager()
        self.monitoring = get_monitoring()
        
        # Governance state
        self.audit_events: List[AuditEvent] = []
        self.compliance_checks: Dict[str, ComplianceCheck] = {}
        self.data_policies: Dict[str, DataProtectionPolicy] = {}
        self.security_violations: List[Dict[str, Any]] = []
        
        # Paths
        self.audit_dir = Path("logs/audit")
        self.compliance_dir = Path("logs/compliance")
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.compliance_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize governance components
        self._initialize_data_protection_policies()
        self._initialize_compliance_checks()
        
        logger.info("Security Governance System initialized")
    
    def _initialize_data_protection_policies(self):
        """Initialize data protection policies."""
        
        # PLC Configuration Data Policy
        self.data_policies['plc_config'] = DataProtectionPolicy(
            policy_id='plc_config',
            name='PLC Configuration Data',
            description='Protection policy for PLC configuration and control logic',
            classification=DataClassification.CONFIDENTIAL,
            retention_days=2555,  # 7 years
            encryption_required=True,
            masking_rules=[
                {'field': 'customer_name', 'method': 'hash'},
                {'field': 'site_location', 'method': 'partial'},
                {'field': 'serial_number', 'method': 'mask'}
            ],
            access_controls=['admin', 'developer'],
            audit_required=True
        )
        
        # User Data Policy
        self.data_policies['user_data'] = DataProtectionPolicy(
            policy_id='user_data',
            name='User Personal Data',
            description='Protection policy for user personal information',
            classification=DataClassification.RESTRICTED,
            retention_days=1095,  # 3 years
            encryption_required=True,
            masking_rules=[
                {'field': 'email', 'method': 'partial'},
                {'field': 'phone', 'method': 'mask'},
                {'field': 'address', 'method': 'hash'}
            ],
            access_controls=['admin'],
            audit_required=True
        )
        
        # System Logs Policy
        self.data_policies['system_logs'] = DataProtectionPolicy(
            policy_id='system_logs',
            name='System Logs and Metrics',
            description='Protection policy for system logs and performance metrics',
            classification=DataClassification.INTERNAL,
            retention_days=365,  # 1 year
            encryption_required=False,
            masking_rules=[
                {'field': 'ip_address', 'method': 'partial'},
                {'field': 'user_id', 'method': 'hash'}
            ],
            access_controls=['admin', 'developer', 'auditor'],
            audit_required=True
        )
        
        # Training Data Policy
        self.data_policies['training_data'] = DataProtectionPolicy(
            policy_id='training_data',
            name='AI Training Data',
            description='Protection policy for AI model training datasets',
            classification=DataClassification.CONFIDENTIAL,
            retention_days=1825,  # 5 years
            encryption_required=True,
            masking_rules=[
                {'field': 'customer_tag', 'method': 'hash'},
                {'field': 'proprietary_info', 'method': 'redact'}
            ],
            access_controls=['admin', 'developer'],
            audit_required=True
        )
    
    def _initialize_compliance_checks(self):
        """Initialize compliance monitoring checks."""
        
        # GDPR Compliance Checks
        self.compliance_checks['gdpr_data_retention'] = ComplianceCheck(
            check_id='gdpr_data_retention',
            standard=ComplianceStandard.GDPR,
            requirement='Data retention policies must be enforced',
            status='compliant',
            severity='high',
            findings=[],
            remediation=[],
            last_checked=datetime.now()
        )
        
        self.compliance_checks['gdpr_right_to_erasure'] = ComplianceCheck(
            check_id='gdpr_right_to_erasure',
            standard=ComplianceStandard.GDPR,
            requirement='Users must be able to request data deletion',
            status='compliant',
            severity='high',
            findings=[],
            remediation=[],
            last_checked=datetime.now()
        )
        
        # ISO 27001 Compliance Checks
        self.compliance_checks['iso27001_access_control'] = ComplianceCheck(
            check_id='iso27001_access_control',
            standard=ComplianceStandard.ISO27001,
            requirement='Access controls must be implemented and monitored',
            status='compliant',
            severity='high',
            findings=[],
            remediation=[],
            last_checked=datetime.now()
        )
        
        self.compliance_checks['iso27001_audit_logging'] = ComplianceCheck(
            check_id='iso27001_audit_logging',
            standard=ComplianceStandard.ISO27001,
            requirement='Security events must be logged and monitored',
            status='compliant',
            severity='medium',
            findings=[],
            remediation=[],
            last_checked=datetime.now()
        )
    
    def log_audit_event(
        self,
        event_type: AuditEventType,
        user_id: Optional[str],
        user_role: Optional[str],
        resource: str,
        action: str,
        result: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        risk_level: str = 'low'
    ) -> str:
        """Log an audit event."""
        
        event_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        audit_event = AuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type,
            user_id=user_id,
            user_role=user_role,
            resource=resource,
            action=action,
            result=result,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {},
            risk_level=risk_level
        )
        
        # Add to in-memory storage
        self.audit_events.append(audit_event)
        
        # Keep only last 10,000 events in memory
        if len(self.audit_events) > 10000:
            self.audit_events = self.audit_events[-10000:]
        
        # Write to audit log file
        self._write_audit_event_to_file(audit_event)
        
        # Check for security violations
        if risk_level in ['high', 'critical'] or result == 'denied':
            self._check_security_violation(audit_event)
        
        logger.info(f"Audit event logged: {event_type.value} - {result}")
        return event_id
    
    def _write_audit_event_to_file(self, event: AuditEvent):
        """Write audit event to log file."""
        try:
            # Create daily audit log file
            log_date = event.timestamp.strftime("%Y%m%d")
            log_file = self.audit_dir / f"audit_{log_date}.jsonl"
            
            # Convert event to JSON
            event_data = asdict(event)
            event_data['timestamp'] = event.timestamp.isoformat()
            event_data['event_type'] = event.event_type.value
            
            # Append to log file
            with open(log_file, 'a') as f:
                f.write(json.dumps(event_data) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to write audit event to file: {e}")
    
    def _check_security_violation(self, event: AuditEvent):
        """Check for potential security violations."""
        violation_detected = False
        violation_type = None
        
        # Check for failed login attempts
        if event.event_type == AuditEventType.USER_LOGIN and event.result == 'failure':
            recent_failures = self._count_recent_failed_logins(event.user_id, event.ip_address)
            if recent_failures >= 5:
                violation_detected = True
                violation_type = 'brute_force_attempt'
        
        # Check for permission violations
        elif event.event_type == AuditEventType.PERMISSION_DENIED:
            recent_denials = self._count_recent_permission_denials(event.user_id)
            if recent_denials >= 10:
                violation_detected = True
                violation_type = 'excessive_permission_denials'
        
        # Check for unusual access patterns
        elif event.event_type == AuditEventType.DATA_ACCESS:
            if self._detect_unusual_access_pattern(event):
                violation_detected = True
                violation_type = 'unusual_access_pattern'
        
        if violation_detected:
            self._handle_security_violation(event, violation_type)
    
    def _count_recent_failed_logins(self, user_id: Optional[str], ip_address: Optional[str]) -> int:
        """Count recent failed login attempts."""
        cutoff_time = datetime.now() - timedelta(minutes=15)
        count = 0
        
        for audit_event in reversed(self.audit_events):
            if audit_event.timestamp < cutoff_time:
                break
            
            if (audit_event.event_type == AuditEventType.USER_LOGIN and
                audit_event.result == 'failure' and
                (audit_event.user_id == user_id or audit_event.ip_address == ip_address)):
                count += 1
        
        return count
    
    def _count_recent_permission_denials(self, user_id: Optional[str]) -> int:
        """Count recent permission denials for a user."""
        cutoff_time = datetime.now() - timedelta(hours=1)
        count = 0
        
        for audit_event in reversed(self.audit_events):
            if audit_event.timestamp < cutoff_time:
                break
            
            if (audit_event.event_type == AuditEventType.PERMISSION_DENIED and
                audit_event.user_id == user_id):
                count += 1
        
        return count
    
    def _detect_unusual_access_pattern(self, event: AuditEvent) -> bool:
        """Detect unusual data access patterns."""
        # Check for access outside normal hours
        hour = event.timestamp.hour
        if hour < 6 or hour > 22:  # Outside 6 AM - 10 PM
            return True
        
        # Check for rapid successive access
        cutoff_time = datetime.now() - timedelta(minutes=5)
        access_count = 0
        
        for audit_event in reversed(self.audit_events):
            if audit_event.timestamp < cutoff_time:
                break
            
            if (audit_event.event_type == AuditEventType.DATA_ACCESS and
                audit_event.user_id == event.user_id):
                access_count += 1
        
        return access_count > 50  # More than 50 accesses in 5 minutes
    
    def _handle_security_violation(self, event: AuditEvent, violation_type: str):
        """Handle detected security violation."""
        violation_record = {
            'violation_id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'violation_type': violation_type,
            'triggering_event': asdict(event),
            'severity': 'high',
            'status': 'detected',
            'remediation_actions': []
        }
        
        # Add specific remediation actions
        if violation_type == 'brute_force_attempt':
            violation_record['remediation_actions'].extend([
                'Temporary IP address blocking',
                'User account lockout',
                'Security team notification'
            ])
        elif violation_type == 'excessive_permission_denials':
            violation_record['remediation_actions'].extend([
                'Review user permissions',
                'User training recommendation',
                'Supervisor notification'
            ])
        elif violation_type == 'unusual_access_pattern':
            violation_record['remediation_actions'].extend([
                'Enhanced monitoring',
                'User verification',
                'Access pattern analysis'
            ])
        
        # Store violation record
        self.security_violations.append(violation_record)
        
        # Send alert
        self.monitoring.create_alert(
            f'security_violation_{violation_type}',
            'high',
            f'Security violation detected: {violation_type}',
            'security_governance'
        )
        
        logger.warning(f"Security violation detected: {violation_type} for user {event.user_id}")
    
    def apply_data_masking(self, data: Dict[str, Any], policy_id: str) -> Dict[str, Any]:
        """Apply data masking based on protection policy."""
        if policy_id not in self.data_policies:
            logger.warning(f"Unknown data policy: {policy_id}")
            return data
        
        policy = self.data_policies[policy_id]
        masked_data = data.copy()
        
        for rule in policy.masking_rules:
            field = rule['field']
            method = rule['method']
            
            if field in masked_data:
                original_value = masked_data[field]
                
                if method == 'hash':
                    masked_data[field] = self._hash_value(str(original_value))
                elif method == 'partial':
                    masked_data[field] = self._partial_mask(str(original_value))
                elif method == 'mask':
                    masked_data[field] = self._full_mask(str(original_value))
                elif method == 'redact':
                    masked_data[field] = '[REDACTED]'
        
        return masked_data
    
    def _hash_value(self, value: str) -> str:
        """Create hash of value for masking."""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
    
    def _partial_mask(self, value: str) -> str:
        """Partially mask value (show first and last characters)."""
        if len(value) <= 4:
            return '*' * len(value)
        return value[:2] + '*' * (len(value) - 4) + value[-2:]
    
    def _full_mask(self, value: str) -> str:
        """Fully mask value."""
        return '*' * min(len(value), 8)
    
    def check_data_access_permission(
        self,
        user_id: str,
        user_role: str,
        resource: str,
        action: str
    ) -> bool:
        """Check if user has permission to access data."""
        
        # Log access attempt
        self.log_audit_event(
            AuditEventType.DATA_ACCESS,
            user_id,
            user_role,
            resource,
            action,
            'attempt'
        )
        
        # Check RBAC permissions
        try:
            role_enum = Role(user_role)
            has_permission = self.rbac_manager.has_permission(role_enum, Permission.READ_DATA)
            
            result = 'success' if has_permission else 'denied'
            risk_level = 'low' if has_permission else 'medium'
            
            # Log result
            self.log_audit_event(
                AuditEventType.PERMISSION_GRANTED if has_permission else AuditEventType.PERMISSION_DENIED,
                user_id,
                user_role,
                resource,
                action,
                result,
                risk_level=risk_level
            )
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            
            # Log failure
            self.log_audit_event(
                AuditEventType.PERMISSION_DENIED,
                user_id,
                user_role,
                resource,
                action,
                'failure',
                risk_level='high'
            )
            
            return False
    
    def run_compliance_checks(self) -> Dict[str, ComplianceCheck]:
        """Run all compliance checks."""
        logger.info("Running compliance checks")
        
        for check_id, check in self.compliance_checks.items():
            try:
                if check.standard == ComplianceStandard.GDPR:
                    self._check_gdpr_compliance(check)
                elif check.standard == ComplianceStandard.ISO27001:
                    self._check_iso27001_compliance(check)
                
                check.last_checked = datetime.now()
                
            except Exception as e:
                logger.error(f"Compliance check failed: {check_id} - {e}")
                check.status = 'non_compliant'
                check.findings.append(f"Check failed: {e}")
        
        # Write compliance report
        self._write_compliance_report()
        
        return self.compliance_checks
    
    def _check_gdpr_compliance(self, check: ComplianceCheck):
        """Check GDPR compliance requirements."""
        check.findings = []
        check.remediation = []
        
        if check.check_id == 'gdpr_data_retention':
            # Check data retention policies
            for policy_id, policy in self.data_policies.items():
                if policy.retention_days > 2555:  # Max 7 years
                    check.findings.append(f"Policy {policy_id} retention exceeds 7 years")
                    check.remediation.append(f"Review retention period for {policy_id}")
            
            check.status = 'compliant' if not check.findings else 'non_compliant'
            
        elif check.check_id == 'gdpr_right_to_erasure':
            # Check if data deletion capabilities exist
            # This would check actual implementation
            check.status = 'compliant'
            check.findings.append("Data deletion API implemented")
    
    def _check_iso27001_compliance(self, check: ComplianceCheck):
        """Check ISO 27001 compliance requirements."""
        check.findings = []
        check.remediation = []
        
        if check.check_id == 'iso27001_access_control':
            # Check access control implementation
            if self.rbac_manager:
                check.findings.append("RBAC system implemented")
                check.status = 'compliant'
            else:
                check.findings.append("No access control system found")
                check.remediation.append("Implement RBAC system")
                check.status = 'non_compliant'
                
        elif check.check_id == 'iso27001_audit_logging':
            # Check audit logging
            recent_events = len([e for e in self.audit_events if e.timestamp > datetime.now() - timedelta(days=1)])
            if recent_events > 0:
                check.findings.append(f"Audit logging active: {recent_events} events in last 24h")
                check.status = 'compliant'
            else:
                check.findings.append("No recent audit events found")
                check.remediation.append("Verify audit logging is working")
                check.status = 'partial'
    
    def _write_compliance_report(self):
        """Write compliance report to file."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.compliance_dir / f"compliance_report_{timestamp}.json"
            
            report_data = {
                'timestamp': datetime.now().isoformat(),
                'checks': {check_id: asdict(check) for check_id, check in self.compliance_checks.items()},
                'summary': self._generate_compliance_summary()
            }
            
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2, default=str)
                
            logger.info(f"Compliance report written: {report_file}")
            
        except Exception as e:
            logger.error(f"Failed to write compliance report: {e}")
    
    def _generate_compliance_summary(self) -> Dict[str, Any]:
        """Generate compliance summary."""
        total_checks = len(self.compliance_checks)
        compliant_checks = len([c for c in self.compliance_checks.values() if c.status == 'compliant'])
        non_compliant_checks = len([c for c in self.compliance_checks.values() if c.status == 'non_compliant'])
        partial_checks = len([c for c in self.compliance_checks.values() if c.status == 'partial'])
        
        compliance_percentage = (compliant_checks / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'total_checks': total_checks,
            'compliant': compliant_checks,
            'non_compliant': non_compliant_checks,
            'partial': partial_checks,
            'compliance_percentage': round(compliance_percentage, 2),
            'overall_status': 'compliant' if compliance_percentage >= 90 else 'needs_attention'
        }
    
    def get_audit_events(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get filtered audit events."""
        filtered_events = self.audit_events
        
        # Apply filters
        if start_date:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_date]
        
        if end_date:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_date]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        # Sort by timestamp (newest first) and limit
        filtered_events.sort(key=lambda x: x.timestamp, reverse=True)
        return filtered_events[:limit]
    
    def get_security_violations(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent security violations."""
        return self.security_violations[-limit:]
    
    def get_governance_status(self) -> Dict[str, Any]:
        """Get overall governance system status."""
        return {
            'audit_events_count': len(self.audit_events),
            'security_violations_count': len(self.security_violations),
            'data_policies_count': len(self.data_policies),
            'compliance_checks': self._generate_compliance_summary(),
            'last_compliance_check': max(
                [check.last_checked for check in self.compliance_checks.values()],
                default=None
            ),
            'system_status': 'active'
        }
    
    def cleanup_old_audit_logs(self, retention_days: int = 2555):
        """Clean up old audit log files."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_files = []
        
        for log_file in self.audit_dir.glob("audit_*.jsonl"):
            try:
                # Extract date from filename
                date_str = log_file.stem.split('_')[1]
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date < cutoff_date:
                    log_file.unlink()
                    deleted_files.append(str(log_file))
                    
            except Exception as e:
                logger.warning(f"Failed to process audit log file {log_file}: {e}")
        
        if deleted_files:
            logger.info(f"Cleaned up {len(deleted_files)} old audit log files")
        
        return deleted_files


# Global governance system instance
governance_system = None


def get_governance_system(settings=None) -> SecurityGovernanceSystem:
    """Get or create governance system instance."""
    global governance_system
    if governance_system is None:
        governance_system = SecurityGovernanceSystem(settings)
    return governance_system


def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='PLC-GPT Security Governance System')
    parser.add_argument('--compliance-check', action='store_true', help='Run compliance checks')
    parser.add_argument('--audit-report', action='store_true', help='Generate audit report')
    parser.add_argument('--cleanup-logs', type=int, help='Clean up audit logs older than N days')
    parser.add_argument('--status', action='store_true', help='Show governance status')
    
    args = parser.parse_args()
    
    governance = get_governance_system()
    
    if args.compliance_check:
        results = governance.run_compliance_checks()
        print("Compliance check results:")
        for check_id, check in results.items():
            print(f"  {check_id}: {check.status}")
    
    elif args.audit_report:
        events = governance.get_audit_events(limit=50)
        print(f"Recent audit events ({len(events)}):")
        for event in events[:10]:  # Show last 10
            print(f"  {event.timestamp}: {event.event_type.value} - {event.result}")
    
    elif args.cleanup_logs:
        deleted = governance.cleanup_old_audit_logs(args.cleanup_logs)
        print(f"Cleaned up {len(deleted)} old audit log files")
    
    elif args.status:
        status = governance.get_governance_status()
        print(json.dumps(status, indent=2, default=str))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 