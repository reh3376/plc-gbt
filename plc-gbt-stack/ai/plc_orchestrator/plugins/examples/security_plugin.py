"""
Example security validation plugin.

Demonstrates adding custom validation rules and security checks.
"""

import ast
import re
from typing import Any

from plc_orchestrator.plugins.base import (
    HookType,
    PluginHook,
    PluginMetadata,
    ValidatorPlugin,
)
from plc_orchestrator.utils.data_models import ValidationIssue, ValidationResult
from plc_orchestrator.utils.enums import ValidationSeverity


class SecurityValidationPlugin(ValidatorPlugin):
    """Plugin that adds enhanced security validation."""

    def __init__(self):
        """Initialize plugin."""
        self.orchestrator = None
        self.security_patterns = {
            # Dangerous imports
            r"import\s+pickle": "Pickle can execute arbitrary code",
            r"import\s+marshal": "Marshal can execute arbitrary code",
            r"from\s+pickle\s+import": "Pickle can execute arbitrary code",
            # Command injection
            r"os\.system\s*\(": "Potential command injection via os.system",
            r"subprocess\.call\s*\(.*shell\s*=\s*True": "Shell=True is dangerous",
            r"eval\s*\(": "eval() can execute arbitrary code",
            r"exec\s*\(": "exec() can execute arbitrary code",
            # SQL injection
            r'\.execute\s*\(\s*["\'].*%[s|d].*["\'].*%': "Potential SQL injection",
            r"\.execute\s*\(.*\+": "String concatenation in SQL query",
            r'f["\'].*SELECT.*{': "F-string in SQL query",
            # Path traversal
            r"\.\.\/": "Potential path traversal",
            r"os\.path\.join\s*\(.*\.\.": "Path traversal in join",
            # Hardcoded secrets
            r'["\']password["\']\s*[:=]\s*["\'][^"\']+["\']': "Hardcoded password",
            r'["\']api_key["\']\s*[:=]\s*["\'][^"\']+["\']': "Hardcoded API key",
            r'["\']secret["\']\s*[:=]\s*["\'][^"\']+["\']': "Hardcoded secret",
            # Weak cryptography
            r"hashlib\.md5": "MD5 is cryptographically weak",
            r"hashlib\.sha1": "SHA1 is cryptographically weak",
            r"random\.": "Use secrets module for cryptographic randomness",
        }

        self.safe_patterns = {
            # Parameterized queries
            r'\.execute\s*\(["\'][^"\']*\?[^"\']*["\']\s*,': "Good: Parameterized query",
            r'\.execute\s*\(["\'][^"\']*%s[^"\']*["\']\s*,\s*\(': "Good: Parameterized query",
            # Input validation
            r"\.isalnum\(\)": "Good: Input validation",
            r"re\.match\s*\(": "Good: Input validation with regex",
            # Safe subprocess
            r"subprocess\.run\s*\(\s*\[": "Good: Subprocess with list arguments",
        }

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="security_validation",
            version="1.0.0",
            description="Enhanced security validation for code analysis",
            author="Security Team",
            tags=["security", "validation", "safety"],
            dependencies=["plc_orchestrator>=2.0.0"],
        )

    def initialize(self, orchestrator: Any) -> None:
        """Initialize plugin with orchestrator."""
        self.orchestrator = orchestrator

    def get_hooks(self) -> list[PluginHook]:
        """Get plugin hooks."""
        return [
            PluginHook(
                hook_type=HookType.POST_VALIDATE,
                callback=self.enhance_validation,
                priority=70,  # Run after standard validation
            ),
        ]

    def validate_code(self, code: str, result: ValidationResult) -> ValidationResult:
        """Enhance code validation with security checks."""
        # Perform security analysis
        security_issues = self._analyze_security(code)

        # Add security issues to result
        for issue in security_issues:
            result.issues.append(issue)

        # Update passed status if critical security issues found
        critical_issues = [i for i in security_issues if i.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            result.passed = False

        # Adjust score based on security issues
        security_penalty = len(security_issues) * 5
        result.score = max(0, result.score - security_penalty)

        # Add security recommendations
        if security_issues:
            result.suggestions.append(
                "Consider running a dedicated security scanner for comprehensive analysis"
            )

        return result

    def enhance_validation(self, code: str, result: ValidationResult) -> ValidationResult:
        """Hook method for POST_VALIDATE."""
        return self.validate_code(code, result)

    def _analyze_security(self, code: str) -> list[ValidationIssue]:
        """Analyze code for security issues."""
        issues = []

        # Check against security patterns
        for pattern, message in self.security_patterns.items():
            matches = list(re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE))
            for match in matches:
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    ValidationIssue(
                        line=line_num,
                        column=match.start() - code.rfind("\n", 0, match.start()),
                        severity=ValidationSeverity.HIGH,
                        message=f"Security: {message}",
                        rule="security-check",
                        suggestion=self._get_suggestion(pattern),
                    )
                )

        # AST-based analysis
        try:
            tree = ast.parse(code)
            issues.extend(self._analyze_ast_security(tree))
        except SyntaxError:
            # Code has syntax errors, skip AST analysis
            pass

        # Check for good practices
        good_practices = 0
        for pattern, message in self.safe_patterns.items():
            if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                good_practices += 1

        # Add positive feedback if good practices found
        if good_practices >= 3:
            issues.append(
                ValidationIssue(
                    line=0,
                    column=0,
                    severity=ValidationSeverity.INFO,
                    message=f"Good: Found {good_practices} security best practices",
                    rule="security-positive",
                )
            )

        return issues

    def _analyze_ast_security(self, tree: ast.AST) -> list[ValidationIssue]:
        """Analyze AST for security issues."""
        issues = []

        class SecurityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.issues = []

            def visit_Import(self, node: ast.Import) -> None:
                """Check imports."""
                for alias in node.names:
                    if alias.name in ["pickle", "marshal", "__builtin__", "__builtins__"]:
                        self.issues.append(
                            ValidationIssue(
                                line=node.lineno,
                                column=node.col_offset,
                                severity=ValidationSeverity.HIGH,
                                message=f"Security: Dangerous import '{alias.name}'",
                                rule="dangerous-import",
                            )
                        )
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call) -> None:
                """Check function calls."""
                # Check for eval/exec
                if isinstance(node.func, ast.Name):
                    if node.func.id in ["eval", "exec", "compile"]:
                        self.issues.append(
                            ValidationIssue(
                                line=node.lineno,
                                column=node.col_offset,
                                severity=ValidationSeverity.CRITICAL,
                                message=f"Security: {node.func.id}() can execute arbitrary code",
                                rule="dangerous-function",
                                suggestion=f"Avoid using {node.func.id}(). Consider safer alternatives.",
                            )
                        )
                self.generic_visit(node)

        visitor = SecurityVisitor()
        visitor.visit(tree)

        return visitor.issues

    def _get_suggestion(self, pattern: str) -> str | None:
        """Get suggestion for fixing security issue."""
        suggestions = {
            r"os\.system": "Use subprocess.run() with list arguments instead",
            r"eval\s*\(": "Parse data safely without eval(). Use ast.literal_eval() for literals",
            r"\.execute\s*\(.*\+": "Use parameterized queries with placeholders",
            r"hashlib\.md5": "Use hashlib.sha256() or stronger for security",
            r"random\.": "Use secrets module for cryptographic operations",
            r'["\']password["\']': "Use environment variables or secure key management",
        }

        for pat, suggestion in suggestions.items():
            if re.match(pat, pattern):
                return suggestion

        return None

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.security_patterns.clear()
        self.safe_patterns.clear()

    # Required by ValidatorPlugin but not used
    def analyze_task(self, task: str, analysis: Any) -> Any:
        """Not used in this plugin."""
        return analysis
