"""
Safety and Validation Layer
Phase 23.1.4: Command Validation and Safety Mechanisms

Provides comprehensive safety validation including command verification,
destructive operation confirmation, hallucination detection, and error recovery.
"""

import re
import os
import json
import subprocess
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone

from . import LLMResponse, LLMResponseStatus, ApplicationContext

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk levels for operations"""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ValidationResult(Enum):
    """Validation result types"""
    APPROVED = "approved"
    BLOCKED = "blocked"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    MODIFIED = "modified"
    ERROR = "error"

class SafetyCheckType(Enum):
    """Types of safety checks"""
    COMMAND_SYNTAX = "command_syntax"
    DESTRUCTIVE_OPERATION = "destructive_operation"
    FILE_ACCESS = "file_access"
    SYSTEM_IMPACT = "system_impact"
    HALLUCINATION = "hallucination"
    RATE_LIMIT = "rate_limit"
    PRIVILEGE_ESCALATION = "privilege_escalation"

@dataclass
class SafetyCheck:
    """Individual safety check result"""
    check_type: SafetyCheckType
    passed: bool
    risk_level: RiskLevel
    message: str
    suggested_action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    result: ValidationResult
    risk_level: RiskLevel
    safety_checks: List[SafetyCheck]
    original_command: str
    validated_command: Optional[str] = None
    confirmation_required: bool = False
    confirmation_message: Optional[str] = None
    error_details: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)

class CommandValidator:
    """Validates CLI commands for safety and correctness"""
    
    def __init__(self):
        self.dangerous_commands = {
            "rm": {"patterns": [r"rm\s+-rf", r"rm\s+.*\*"], "risk": RiskLevel.CRITICAL},
            "delete": {"patterns": [r"delete\s+all", r"delete\s+.*\*"], "risk": RiskLevel.HIGH},
            "format": {"patterns": [r"format", r"mkfs"], "risk": RiskLevel.CRITICAL},
            "shutdown": {"patterns": [r"shutdown", r"reboot", r"halt"], "risk": RiskLevel.HIGH},
            "chmod": {"patterns": [r"chmod\s+777", r"chmod\s+-R"], "risk": RiskLevel.MEDIUM},
            "chown": {"patterns": [r"chown\s+-R"], "risk": RiskLevel.MEDIUM},
            "dd": {"patterns": [r"dd\s+.*of="], "risk": RiskLevel.HIGH},
            "truncate": {"patterns": [r"truncate.*>", r">\s*/dev/null"], "risk": RiskLevel.MEDIUM}
        }
        
        self.allowed_commands = [
            "plc-cl", "python", "python3", "pip", "ls", "cat", "head", "tail",
            "grep", "find", "pwd", "cd", "mkdir", "cp", "mv", "echo", "which",
            "git", "nano", "vim", "less", "more", "wc", "sort", "uniq"
        ]
        
        self.restricted_paths = [
            "/etc", "/bin", "/sbin", "/usr/bin", "/usr/sbin", "/boot",
            "/dev", "/proc", "/sys", "/tmp", "/var/log"
        ]
    
    def validate_command(self, command: str, context: ApplicationContext) -> ValidationReport:
        """Validate a command for safety and correctness"""
        safety_checks = []
        risk_level = RiskLevel.SAFE
        
        # Basic syntax check
        syntax_check = self._check_command_syntax(command)
        safety_checks.append(syntax_check)
        if syntax_check.risk_level.value > risk_level.value:
            risk_level = syntax_check.risk_level
        
        # Destructive operation check
        destructive_check = self._check_destructive_operations(command)
        safety_checks.append(destructive_check)
        if destructive_check.risk_level.value > risk_level.value:
            risk_level = destructive_check.risk_level
        
        # File access check
        file_check = self._check_file_access(command)
        safety_checks.append(file_check)
        if file_check.risk_level.value > risk_level.value:
            risk_level = file_check.risk_level
        
        # System impact check
        system_check = self._check_system_impact(command, context)
        safety_checks.append(system_check)
        if system_check.risk_level.value > risk_level.value:
            risk_level = system_check.risk_level
        
        # Privilege escalation check
        privilege_check = self._check_privilege_escalation(command)
        safety_checks.append(privilege_check)
        if privilege_check.risk_level.value > risk_level.value:
            risk_level = privilege_check.risk_level
        
        # Determine validation result
        result = self._determine_validation_result(safety_checks, risk_level)
        
        # Generate confirmation message if needed
        confirmation_message = None
        confirmation_required = False
        if result == ValidationResult.REQUIRES_CONFIRMATION:
            confirmation_required = True
            confirmation_message = self._generate_confirmation_message(command, safety_checks)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(command, safety_checks)
        
        return ValidationReport(
            result=result,
            risk_level=risk_level,
            safety_checks=safety_checks,
            original_command=command,
            confirmation_required=confirmation_required,
            confirmation_message=confirmation_message,
            recommendations=recommendations
        )
    
    def _check_command_syntax(self, command: str) -> SafetyCheck:
        """Check basic command syntax"""
        if not command or not command.strip():
            return SafetyCheck(
                check_type=SafetyCheckType.COMMAND_SYNTAX,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message="Empty or invalid command"
            )
        
        # Check for command injection patterns
        injection_patterns = [
            r";\s*rm", r"&&\s*rm", r"\|\s*rm", r"`.*`", r"\$\(.*\)",
            r">\s*/dev", r"<\s*/dev", r"\|&", r"2>&1"
        ]
        
        for pattern in injection_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SafetyCheck(
                    check_type=SafetyCheckType.COMMAND_SYNTAX,
                    passed=False,
                    risk_level=RiskLevel.HIGH,
                    message=f"Potential command injection detected: {pattern}"
                )
        
        # Check if command starts with allowed command
        first_command = command.strip().split()[0] if command.strip() else ""
        if first_command not in self.allowed_commands:
            return SafetyCheck(
                check_type=SafetyCheckType.COMMAND_SYNTAX,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"Command '{first_command}' not in allowed list",
                suggested_action=f"Use one of: {', '.join(self.allowed_commands[:5])}"
            )
        
        return SafetyCheck(
            check_type=SafetyCheckType.COMMAND_SYNTAX,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="Command syntax appears valid"
        )
    
    def _check_destructive_operations(self, command: str) -> SafetyCheck:
        """Check for potentially destructive operations"""
        for cmd_name, config in self.dangerous_commands.items():
            for pattern in config["patterns"]:
                if re.search(pattern, command, re.IGNORECASE):
                    return SafetyCheck(
                        check_type=SafetyCheckType.DESTRUCTIVE_OPERATION,
                        passed=False,
                        risk_level=config["risk"],
                        message=f"Destructive operation detected: {cmd_name}",
                        suggested_action="Consider safer alternatives or add confirmation"
                    )
        
        return SafetyCheck(
            check_type=SafetyCheckType.DESTRUCTIVE_OPERATION,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="No destructive operations detected"
        )
    
    def _check_file_access(self, command: str) -> SafetyCheck:
        """Check for unauthorized file access"""
        for restricted_path in self.restricted_paths:
            if restricted_path in command:
                return SafetyCheck(
                    check_type=SafetyCheckType.FILE_ACCESS,
                    passed=False,
                    risk_level=RiskLevel.HIGH,
                    message=f"Access to restricted path: {restricted_path}",
                    suggested_action="Ensure you have proper permissions"
                )
        
        # Check for wildcard operations in sensitive areas
        if re.search(r"\*.*(/etc|/bin|/usr)", command):
            return SafetyCheck(
                check_type=SafetyCheckType.FILE_ACCESS,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message="Wildcard operation in sensitive directory"
            )
        
        return SafetyCheck(
            check_type=SafetyCheckType.FILE_ACCESS,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="File access appears safe"
        )
    
    def _check_system_impact(self, command: str, context: ApplicationContext) -> SafetyCheck:
        """Check potential system impact"""
        # Check for resource-intensive operations
        intensive_patterns = [
            r"find\s+/.*\*", r"grep\s+-r.*\*", r"chmod\s+-R", r"chown\s+-R"
        ]
        
        for pattern in intensive_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SafetyCheck(
                    check_type=SafetyCheckType.SYSTEM_IMPACT,
                    passed=False,
                    risk_level=RiskLevel.MEDIUM,
                    message="Potentially resource-intensive operation",
                    suggested_action="Consider limiting scope or running during off-peak hours"
                )
        
        # Check for operations that might conflict with current system state
        if "plc-cl" in command and context.system_state.get("status") != "ready":
            return SafetyCheck(
                check_type=SafetyCheckType.SYSTEM_IMPACT,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message="System may not be ready for this operation",
                suggested_action="Wait for system to be ready or check system status"
            )
        
        return SafetyCheck(
            check_type=SafetyCheckType.SYSTEM_IMPACT,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="System impact appears minimal"
        )
    
    def _check_privilege_escalation(self, command: str) -> SafetyCheck:
        """Check for privilege escalation attempts"""
        escalation_patterns = [
            r"sudo", r"su\s+", r"chmod\s+\+s", r"setuid", r"setgid"
        ]
        
        for pattern in escalation_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SafetyCheck(
                    check_type=SafetyCheckType.PRIVILEGE_ESCALATION,
                    passed=False,
                    risk_level=RiskLevel.HIGH,
                    message="Privilege escalation detected",
                    suggested_action="Ensure you have proper authorization"
                )
        
        return SafetyCheck(
            check_type=SafetyCheckType.PRIVILEGE_ESCALATION,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="No privilege escalation detected"
        )
    
    def _determine_validation_result(self, safety_checks: List[SafetyCheck], risk_level: RiskLevel) -> ValidationResult:
        """Determine overall validation result"""
        failed_checks = [check for check in safety_checks if not check.passed]
        
        if not failed_checks:
            return ValidationResult.APPROVED
        
        critical_failures = [check for check in failed_checks if check.risk_level == RiskLevel.CRITICAL]
        if critical_failures:
            return ValidationResult.BLOCKED
        
        high_risk_failures = [check for check in failed_checks if check.risk_level == RiskLevel.HIGH]
        if high_risk_failures:
            return ValidationResult.REQUIRES_CONFIRMATION
        
        medium_risk_failures = [check for check in failed_checks if check.risk_level == RiskLevel.MEDIUM]
        if medium_risk_failures:
            return ValidationResult.REQUIRES_CONFIRMATION
        
        return ValidationResult.APPROVED
    
    def _generate_confirmation_message(self, command: str, safety_checks: List[SafetyCheck]) -> str:
        """Generate confirmation message for risky operations"""
        failed_checks = [check for check in safety_checks if not check.passed]
        
        message = f"⚠️ WARNING: The command '{command}' has been flagged for the following concerns:\n\n"
        
        for check in failed_checks:
            message += f"• {check.message} (Risk: {check.risk_level.value.upper()})\n"
            if check.suggested_action:
                message += f"  Suggestion: {check.suggested_action}\n"
        
        message += "\nDo you want to proceed with this command? (yes/no): "
        return message
    
    def _generate_recommendations(self, command: str, safety_checks: List[SafetyCheck]) -> List[str]:
        """Generate safety recommendations"""
        recommendations = []
        
        failed_checks = [check for check in safety_checks if not check.passed]
        
        for check in failed_checks:
            if check.suggested_action:
                recommendations.append(check.suggested_action)
        
        # General recommendations based on command type
        if "rm" in command:
            recommendations.append("Consider using a backup strategy before deletion")
        
        if "*" in command:
            recommendations.append("Test with a single file first to verify behavior")
        
        if "chmod" in command or "chown" in command:
            recommendations.append("Verify file permissions are appropriate for security")
        
        return list(set(recommendations))  # Remove duplicates

class HallucinationDetector:
    """Detects potential hallucinations in LLM responses"""
    
    def __init__(self):
        self.known_commands = [
            "plc-cl", "python", "python3", "pip", "ls", "cat", "head", "tail",
            "grep", "find", "pwd", "cd", "mkdir", "cp", "mv", "echo"
        ]
        
        self.plc_cl_subcommands = [
            "create", "analyze", "optimize", "validate", "export", "import",
            "list", "delete", "update", "configure", "status"
        ]
    
    def detect_hallucination(self, response: LLMResponse, context: ApplicationContext) -> SafetyCheck:
        """Detect potential hallucinations in LLM response"""
        content = response.content.lower()
        
        # Check for non-existent commands
        if self._contains_nonexistent_commands(content):
            return SafetyCheck(
                check_type=SafetyCheckType.HALLUCINATION,
                passed=False,
                risk_level=RiskLevel.MEDIUM,
                message="Response contains non-existent commands",
                suggested_action="Verify commands before execution"
            )
        
        # Check for impossible file paths
        if self._contains_impossible_paths(content, context):
            return SafetyCheck(
                check_type=SafetyCheckType.HALLUCINATION,
                passed=False,
                risk_level=RiskLevel.LOW,
                message="Response references non-existent file paths",
                suggested_action="Verify file paths exist"
            )
        
        # Check for inconsistent information
        if self._contains_inconsistent_info(content, context):
            return SafetyCheck(
                check_type=SafetyCheckType.HALLUCINATION,
                passed=False,
                risk_level=RiskLevel.LOW,
                message="Response contains inconsistent information",
                suggested_action="Double-check provided information"
            )
        
        return SafetyCheck(
            check_type=SafetyCheckType.HALLUCINATION,
            passed=True,
            risk_level=RiskLevel.SAFE,
            message="No hallucination detected"
        )
    
    def _contains_nonexistent_commands(self, content: str) -> bool:
        """Check for references to non-existent commands"""
        # Look for command patterns
        command_patterns = [
            r"plc-cl\s+(\w+)",
            r"python\s+(\w+\.py)",
            r"(\w+)\s+--\w+"
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                
                # Check if plc-cl subcommand exists
                if "plc-cl" in pattern and match not in self.plc_cl_subcommands:
                    return True
        
        return False
    
    def _contains_impossible_paths(self, content: str, context: ApplicationContext) -> bool:
        """Check for references to impossible file paths"""
        # Extract potential file paths
        path_patterns = [
            r"/[\w/.-]+",
            r"[\w.-]+/[\w/.-]+",
            r"[\w.-]+\.(?:json|py|txt|csv|xml)"
        ]
        
        for pattern in path_patterns:
            paths = re.findall(pattern, content)
            for path in paths:
                # Check if path makes sense in current context
                if path.startswith('/') and not any(allowed in path for allowed in ['/home', '/tmp', '/var', context.current_directory]):
                    return True
        
        return False
    
    def _contains_inconsistent_info(self, content: str, context: ApplicationContext) -> bool:
        """Check for inconsistent information"""
        # Check if response contradicts known context
        if "current directory" in content:
            if context.current_directory not in content and "plc-gbt" not in content:
                return True
        
        # Check for contradictory statements
        contradictory_patterns = [
            (r"file exists", r"file (does not exist|not found)"),
            (r"command successful", r"command failed"),
            (r"installation complete", r"installation failed")
        ]
        
        for positive, negative in contradictory_patterns:
            if re.search(positive, content) and re.search(negative, content):
                return True
        
        return False

class SafetyValidator:
    """Main safety validation orchestrator"""
    
    def __init__(self):
        self.command_validator = CommandValidator()
        self.hallucination_detector = HallucinationDetector()
        self.validation_history: List[ValidationReport] = []
    
    def validate_llm_response(self, response: LLMResponse, context: ApplicationContext) -> ValidationReport:
        """Comprehensive validation of LLM response"""
        safety_checks = []
        
        # Check for hallucinations
        hallucination_check = self.hallucination_detector.detect_hallucination(response, context)
        safety_checks.append(hallucination_check)
        
        # Extract and validate any commands in the response
        commands = self._extract_commands_from_response(response.content)
        command_validation = None
        
        if commands:
            # Validate the most concerning command
            for command in commands:
                validation = self.command_validator.validate_command(command, context)
                if command_validation is None or validation.risk_level.value > command_validation.risk_level.value:
                    command_validation = validation
        
        if command_validation:
            safety_checks.extend(command_validation.safety_checks)
            overall_risk = max(hallucination_check.risk_level, command_validation.risk_level, key=lambda x: x.value)
            overall_result = command_validation.result
        else:
            overall_risk = hallucination_check.risk_level
            overall_result = ValidationResult.APPROVED if hallucination_check.passed else ValidationResult.REQUIRES_CONFIRMATION
        
        # Create comprehensive report
        report = ValidationReport(
            result=overall_result,
            risk_level=overall_risk,
            safety_checks=safety_checks,
            original_command=commands[0] if commands else "",
            confirmation_required=overall_result == ValidationResult.REQUIRES_CONFIRMATION,
            confirmation_message=command_validation.confirmation_message if command_validation else None,
            recommendations=command_validation.recommendations if command_validation else []
        )
        
        # Store in history
        self.validation_history.append(report)
        if len(self.validation_history) > 100:
            self.validation_history = self.validation_history[-100:]
        
        return report
    
    def _extract_commands_from_response(self, content: str) -> List[str]:
        """Extract potential commands from LLM response"""
        commands = []
        
        # Look for code blocks
        code_block_pattern = r"```(?:bash|shell|sh)?\n?(.*?)\n?```"
        code_blocks = re.findall(code_block_pattern, content, re.DOTALL)
        for block in code_blocks:
            commands.extend(line.strip() for line in block.split('\n') if line.strip())
        
        # Look for inline commands
        inline_patterns = [
            r"`([^`]+)`",
            r"run\s+([^\n]+)",
            r"execute\s+([^\n]+)",
            r"command:\s*([^\n]+)"
        ]
        
        for pattern in inline_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            commands.extend(matches)
        
        # Filter out non-command text
        filtered_commands = []
        for cmd in commands:
            cmd = cmd.strip()
            if any(cmd.startswith(allowed) for allowed in ["plc-cl", "python", "ls", "cat", "grep"]):
                filtered_commands.append(cmd)
        
        return filtered_commands
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of validation activities"""
        if not self.validation_history:
            return {"total_validations": 0}
        
        total = len(self.validation_history)
        approved = sum(1 for r in self.validation_history if r.result == ValidationResult.APPROVED)
        blocked = sum(1 for r in self.validation_history if r.result == ValidationResult.BLOCKED)
        confirmations = sum(1 for r in self.validation_history if r.result == ValidationResult.REQUIRES_CONFIRMATION)
        
        risk_counts = {}
        for level in RiskLevel:
            risk_counts[level.value] = sum(1 for r in self.validation_history if r.risk_level == level)
        
        return {
            "total_validations": total,
            "approved": approved,
            "blocked": blocked,
            "confirmations_required": confirmations,
            "approval_rate": round(approved / total * 100, 1),
            "risk_distribution": risk_counts,
            "recent_activity": self.validation_history[-5:]
        }

# Singleton validator instance
_safety_validator: Optional[SafetyValidator] = None

def get_safety_validator() -> SafetyValidator:
    """Get singleton safety validator instance"""
    global _safety_validator
    if _safety_validator is None:
        _safety_validator = SafetyValidator()
    return _safety_validator

def validate_command(command: str, context: ApplicationContext) -> ValidationReport:
    """Quick function to validate a command"""
    validator = get_safety_validator()
    return validator.command_validator.validate_command(command, context)

def validate_llm_response(response: LLMResponse, context: ApplicationContext) -> ValidationReport:
    """Quick function to validate an LLM response"""
    validator = get_safety_validator()
    return validator.validate_llm_response(response, context)

# Export main components
__all__ = [
    "RiskLevel",
    "ValidationResult",
    "SafetyCheckType",
    "SafetyCheck",
    "ValidationReport",
    "CommandValidator",
    "HallucinationDetector",
    "SafetyValidator",
    "get_safety_validator",
    "validate_command",
    "validate_llm_response"
] 