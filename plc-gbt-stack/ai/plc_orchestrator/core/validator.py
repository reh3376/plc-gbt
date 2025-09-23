"""Task validation module for the PLC Task Orchestrator."""

import ast
import re
from typing import Any

from plc_orchestrator.config.settings import OrchestratorConfig
from plc_orchestrator.utils.data_models import ValidationResult
from plc_orchestrator.utils.enums import ValidationSeverity, ValidationTier
from plc_orchestrator.utils.helpers import sanitize_code
from plc_orchestrator.utils.logging import get_logger


class TaskValidator:
    """Validates task implementations against requirements and quality standards."""

    def __init__(self, config: OrchestratorConfig) -> None:
        """
        Initialize task validator.

        Args:
            config: Orchestrator configuration
        """
        self.config = config
        self.logger = get_logger(__name__, config.get_logging_config())

    def validate(
        self,
        code_content: str,
        requirements: list[str],
        validation_tier: ValidationTier = ValidationTier.REQUIREMENTS,
    ) -> ValidationResult:
        """
        Validate code against requirements and quality standards.

        Args:
            code_content: Code to validate
            requirements: List of requirements to check
            validation_tier: Level of validation to perform

        Returns:
            Validation result with issues and recommendations
        """
        self.logger.info(f"Starting validation at tier: {validation_tier.value}")

        # Get validation tiers to execute
        tiers = self._get_validation_tiers(validation_tier)

        # Execute validations
        all_issues = []
        all_recommendations = []
        details = {}

        for tier in tiers:
            tier_result = self._execute_tier_validation(tier, code_content, requirements)
            all_issues.extend(tier_result.get("issues", []))
            all_recommendations.extend(tier_result.get("recommendations", []))
            details[tier.value] = tier_result

        # Calculate overall score
        score = self._calculate_validation_score(all_issues)
        passed = score >= 70 and not any(
            issue.get("severity") == ValidationSeverity.CRITICAL.value for issue in all_issues
        )

        result = ValidationResult(
            passed=passed,
            score=score,
            tier=validation_tier,
            issues=all_issues,
            recommendations=all_recommendations,
            details=details,
        )

        self.logger.info(
            "Validation completed",
            extra={
                "passed": passed,
                "score": score,
                "issues_count": len(all_issues),
                "critical_issues": len(result.get_critical_issues()),
            },
        )

        return result

    def _get_validation_tiers(self, up_to_tier: ValidationTier) -> list[ValidationTier]:
        """Get list of validation tiers to execute."""
        tier_order = [
            ValidationTier.SYNTAX,
            ValidationTier.REQUIREMENTS,
            ValidationTier.HALLUCINATION,
            ValidationTier.BEST_PRACTICES,
            ValidationTier.MATHEMATICAL,
            ValidationTier.PERFORMANCE,
            ValidationTier.SAFETY,
            ValidationTier.PRODUCTION,
        ]

        # Find index of requested tier
        try:
            index = tier_order.index(up_to_tier)
            return tier_order[: index + 1]
        except ValueError:
            return [up_to_tier]

    def _execute_tier_validation(
        self, tier: ValidationTier, code_content: str, requirements: list[str]
    ) -> dict[str, Any]:
        """Execute validation for a specific tier."""
        validators = {
            ValidationTier.SYNTAX: self._validate_syntax,
            ValidationTier.REQUIREMENTS: lambda c: self._validate_requirements(c, requirements),
            ValidationTier.HALLUCINATION: self._validate_hallucination,
            ValidationTier.BEST_PRACTICES: self._validate_best_practices,
            ValidationTier.MATHEMATICAL: self._validate_mathematical,
            ValidationTier.PERFORMANCE: self._validate_performance,
            ValidationTier.SAFETY: self._validate_safety,
            ValidationTier.PRODUCTION: self._validate_production,
        }

        validator = validators.get(tier)
        if validator:
            return validator(code_content)
        else:
            return {"issues": [], "recommendations": []}

    def _validate_syntax(self, code_content: str) -> dict[str, Any]:
        """Validate Python syntax."""
        issues = []
        recommendations = []

        try:
            # Sanitize code first
            sanitized = sanitize_code(code_content)
            if sanitized != code_content:
                issues.append(
                    {
                        "type": "security",
                        "severity": ValidationSeverity.HIGH.value,
                        "message": "Potentially dangerous code patterns detected and sanitized",
                        "line": None,
                    }
                )

            # Parse as AST
            tree = ast.parse(code_content)

            # Check for basic issues
            visitor = SyntaxVisitor()
            visitor.visit(tree)

            if visitor.issues:
                issues.extend(visitor.issues)

            if visitor.recommendations:
                recommendations.extend(visitor.recommendations)

        except SyntaxError as e:
            issues.append(
                {
                    "type": "syntax",
                    "severity": ValidationSeverity.CRITICAL.value,
                    "message": f"Syntax error: {e}",
                    "line": e.lineno,
                }
            )

        except Exception as e:
            issues.append(
                {
                    "type": "parse",
                    "severity": ValidationSeverity.HIGH.value,
                    "message": f"Failed to parse code: {e}",
                    "line": None,
                }
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "passed": len([i for i in issues if i["severity"] == ValidationSeverity.CRITICAL.value])
            == 0,
        }

    def _validate_requirements(self, code_content: str, requirements: list[str]) -> dict[str, Any]:
        """Validate requirements coverage."""
        issues = []
        recommendations = []
        covered_requirements = []

        for req in requirements:
            # Simple keyword-based checking
            req_keywords = extract_requirement_keywords(req)
            if any(keyword.lower() in code_content.lower() for keyword in req_keywords):
                covered_requirements.append(req)
            else:
                issues.append(
                    {
                        "type": "requirement",
                        "severity": ValidationSeverity.HIGH.value,
                        "message": f"Requirement not clearly implemented: {req}",
                        "requirement": req,
                        "line": None,
                    }
                )

        coverage = len(covered_requirements) / len(requirements) * 100 if requirements else 100

        if coverage < 100:
            recommendations.append(
                f"Consider implementing missing requirements. Coverage: {coverage:.1f}%"
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "coverage": coverage,
            "covered_requirements": covered_requirements,
            "missing_requirements": [r for r in requirements if r not in covered_requirements],
        }

    def _validate_hallucination(self, code_content: str) -> dict[str, Any]:
        """Detect potential hallucinations in code."""
        issues = []
        recommendations = []

        # Patterns that might indicate hallucination
        hallucination_patterns = [
            # Incomplete implementations
            (r"pass\s*$", "Empty implementation detected", ValidationSeverity.HIGH),
            (r"\.\.\.", "Ellipsis indicating incomplete code", ValidationSeverity.HIGH),
            (r"# TODO", "TODO comment found", ValidationSeverity.MEDIUM),
            (r"raise NotImplementedError", "Not implemented error", ValidationSeverity.HIGH),
            # Placeholder text
            (r"your_.*_here", "Placeholder text detected", ValidationSeverity.HIGH),
            (r"example\.com", "Example domain detected", ValidationSeverity.MEDIUM),
            (r"INSERT.*HERE", "Placeholder instruction detected", ValidationSeverity.HIGH),
            # Non-existent modules (common hallucinations)
            (
                r"from made_up_module import",
                "Potentially non-existent import",
                ValidationSeverity.HIGH,
            ),
            (r"import fictional_", "Suspicious module name", ValidationSeverity.HIGH),
        ]

        for pattern, message, severity in hallucination_patterns:
            matches = re.finditer(pattern, code_content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                line_num = code_content[: match.start()].count("\n") + 1
                issues.append(
                    {
                        "type": "hallucination",
                        "severity": severity.value,
                        "message": message,
                        "line": line_num,
                        "match": match.group(),
                    }
                )

        # Check for unrealistic performance claims in comments
        perf_claims = re.findall(r"#.*?(\d+)x\s*faster", code_content, re.IGNORECASE)
        for claim in perf_claims:
            if int(claim) > 100:
                issues.append(
                    {
                        "type": "hallucination",
                        "severity": ValidationSeverity.LOW.value,
                        "message": f"Unrealistic performance claim: {claim}x faster",
                        "line": None,
                    }
                )

        if issues:
            recommendations.append("Review and complete all placeholder implementations")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "hallucination_score": len(issues),
        }

    def _validate_best_practices(self, code_content: str) -> dict[str, Any]:
        """Validate code quality and best practices."""
        issues = []
        recommendations = []

        # Parse AST once
        tree = ast.parse(code_content)
        lines = code_content.split("\n")

        # Run individual validation checks
        self._check_function_complexity(tree, issues)
        self._check_line_lengths(lines, issues)
        self._check_import_organization(lines, recommendations)
        self._check_documentation(tree, issues)
        self._check_type_hints(tree, recommendations)

        return {
            "issues": issues,
            "recommendations": recommendations,
            "quality_score": 100 - len(issues) * 5,
        }

    def _check_function_complexity(self, tree: ast.AST, issues: list[dict[str, Any]]) -> None:
        """Check function complexity."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    issues.append(
                        {
                            "type": "complexity",
                            "severity": ValidationSeverity.MEDIUM.value,
                            "message": f"Function '{node.name}' has high complexity: {complexity}",
                            "line": node.lineno,
                        }
                    )

    def _check_line_lengths(self, lines: list[str], issues: list[dict[str, Any]]) -> None:
        """Check line length violations."""
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                issues.append(
                    {
                        "type": "style",
                        "severity": ValidationSeverity.LOW.value,
                        "message": f"Line too long ({len(line)} > 100 characters)",
                        "line": i,
                    }
                )

    def _check_import_organization(self, lines: list[str], recommendations: list[str]) -> None:
        """Check if imports are properly organized."""
        import_lines = [l for l in lines if l.strip().startswith(("import ", "from "))]
        if import_lines and not is_imports_sorted(import_lines):
            recommendations.append("Consider sorting imports alphabetically")

    def _check_documentation(self, tree: ast.AST, issues: list[dict[str, Any]]) -> None:
        """Check for missing documentation."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    issues.append(
                        {
                            "type": "documentation",
                            "severity": ValidationSeverity.LOW.value,
                            "message": f"Missing docstring for {node.__class__.__name__}: {node.name}",
                            "line": node.lineno,
                        }
                    )

    def _check_type_hints(self, tree: ast.AST, recommendations: list[str]) -> None:
        """Check for missing type hints."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns and node.name != "__init__":
                    recommendations.append(
                        f"Consider adding return type hint to function '{node.name}'"
                    )

    def _validate_mathematical(self, code_content: str) -> dict[str, Any]:
        """Validate mathematical correctness (placeholder for WolframAlpha integration)."""
        issues = []
        recommendations = []

        # Look for mathematical operations
        math_patterns = [
            (r"(\w+)\s*=\s*.*?(?:math\.|np\.|scipy\.)", "Mathematical calculation detected"),
            (r"def\s+(\w+).*?(?:derivative|integral|transform)", "Mathematical function detected"),
        ]

        math_functions = []
        for pattern, description in math_patterns:
            matches = re.finditer(pattern, code_content)
            for match in matches:
                math_functions.append(
                    {
                        "name": match.group(1),
                        "description": description,
                        "line": code_content[: match.start()].count("\n") + 1,
                    }
                )

        if math_functions and self.config.settings.enable_math_validation:
            recommendations.append("Mathematical validation available via WolframAlpha integration")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "math_functions": math_functions,
            "requires_validation": len(math_functions) > 0,
        }

    def _validate_performance(self, code_content: str) -> dict[str, Any]:
        """Validate performance considerations."""
        issues = []
        recommendations = []

        # Check for performance anti-patterns
        perf_patterns = [
            (
                r"for.*?in.*?for.*?in",
                "Nested loops detected - consider optimization",
                ValidationSeverity.MEDIUM,
            ),
            (
                r"time\.sleep\(\d+\)",
                "Blocking sleep detected - consider async",
                ValidationSeverity.LOW,
            ),
            (
                r"\+=.*?loop",
                "String concatenation in loop - use list.append",
                ValidationSeverity.MEDIUM,
            ),
            (
                r"global\s+\w+",
                "Global variable usage - consider refactoring",
                ValidationSeverity.LOW,
            ),
        ]

        for pattern, message, severity in perf_patterns:
            if re.search(pattern, code_content, re.IGNORECASE | re.DOTALL):
                issues.append(
                    {
                        "type": "performance",
                        "severity": severity.value,
                        "message": message,
                        "line": None,
                    }
                )

        # Check for missing optimizations
        if "def " in code_content and "@lru_cache" not in code_content:
            if re.search(r"def\s+\w+.*?pure.*?function", code_content):
                recommendations.append("Consider using @lru_cache for pure functions")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "performance_score": 100 - len(issues) * 10,
        }

    def _validate_safety(self, code_content: str) -> dict[str, Any]:
        """Validate safety considerations for control systems."""
        issues = []
        recommendations = []

        # Safety patterns to check
        safety_patterns = [
            (r"while\s+True:", "Infinite loop without break condition", ValidationSeverity.HIGH),
            (r"except:\s*pass", "Silent exception handling", ValidationSeverity.HIGH),
            (r"eval\(|exec\(", "Dynamic code execution", ValidationSeverity.CRITICAL),
            (r"pickle\.loads?\(", "Unsafe deserialization", ValidationSeverity.HIGH),
        ]

        for pattern, message, severity in safety_patterns:
            if re.search(pattern, code_content):
                issues.append(
                    {"type": "safety", "severity": severity.value, "message": message, "line": None}
                )

        # Check for bounds checking in control code
        if "setpoint" in code_content.lower() or "control" in code_content.lower():
            if not re.search(r"(min|max|clamp|limit|bound)", code_content):
                recommendations.append("Consider adding bounds checking for control outputs")

        return {
            "issues": issues,
            "recommendations": recommendations,
            "safety_compliant": len(
                [i for i in issues if i["severity"] == ValidationSeverity.CRITICAL.value]
            )
            == 0,
        }

    def _validate_production(self, code_content: str) -> dict[str, Any]:
        """Validate production readiness."""
        issues = []
        recommendations = []

        # Production readiness checks
        checks = {
            "logging": self._check_logging_implementation(code_content),
            "error_handling": self._check_error_handling(code_content),
            "configuration": self._check_configuration_management(code_content),
            "monitoring": self._check_monitoring_hooks(code_content),
            "security": self._check_security_practices(code_content),
            "documentation": self._check_documentation_completeness(code_content),
        }

        for check_name, passed in checks.items():
            if not passed:
                issues.append(
                    {
                        "type": "production",
                        "severity": ValidationSeverity.MEDIUM.value,
                        "message": f"Missing production requirement: {check_name}",
                        "line": None,
                    }
                )

        # Calculate production readiness score
        readiness_score = sum(1 for passed in checks.values() if passed) / len(checks) * 100

        if readiness_score < 100:
            recommendations.append(
                f"Production readiness: {readiness_score:.0f}%. "
                "Consider implementing missing requirements."
            )

        return {
            "issues": issues,
            "recommendations": recommendations,
            "production_ready": readiness_score >= 80,
            "readiness_score": readiness_score,
            "checks": checks,
        }

    def _check_logging_implementation(self, code_content: str) -> bool:
        """Check if logging is properly implemented."""
        return any(
            pattern in code_content
            for pattern in ["import logging", "from logging import", "import structlog", "logger."]
        )

    def _check_error_handling(self, code_content: str) -> bool:
        """Check if error handling is implemented."""
        # Look for try/except blocks
        has_try_except = "try:" in code_content and "except" in code_content
        # But not bare except
        has_bare_except = bool(re.search(r"except:\s*$", code_content, re.MULTILINE))
        return has_try_except and not has_bare_except

    def _check_configuration_management(self, code_content: str) -> bool:
        """Check if configuration is properly managed."""
        return any(
            pattern in code_content
            for pattern in ["config", "Config", "settings", "Settings", "environ", "dotenv"]
        )

    def _check_monitoring_hooks(self, code_content: str) -> bool:
        """Check if monitoring hooks are present."""
        return any(
            pattern in code_content
            for pattern in ["metric", "telemetry", "statsd", "prometheus", "datadog"]
        )

    def _check_security_practices(self, code_content: str) -> bool:
        """Check if security practices are followed."""
        # Patterns that indicate security issues
        bad_patterns = [
            r'password\s*=\s*["\']',  # Hardcoded password
            r'secret\s*=\s*["\']',  # Hardcoded secret
            r'token\s*=\s*["\']',  # Hardcoded token
            r"eval\(",  # Dynamic code evaluation
            r"exec\(",  # Dynamic code execution
        ]
        return not any(re.search(pattern, code_content) for pattern in bad_patterns)

    def _check_documentation_completeness(self, code_content: str) -> bool:
        """Check if documentation is complete."""
        # Simple check for docstrings
        tree = ast.parse(code_content)
        total_items = 0
        documented_items = 0

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                total_items += 1
                if ast.get_docstring(node):
                    documented_items += 1

        return documented_items >= total_items * 0.8 if total_items > 0 else True

    def _calculate_validation_score(self, issues: list[dict[str, Any]]) -> float:
        """Calculate overall validation score."""
        if not issues:
            return 100.0

        # Weight by severity
        severity_weights = {
            ValidationSeverity.CRITICAL.value: 20,
            ValidationSeverity.HIGH.value: 10,
            ValidationSeverity.MEDIUM.value: 5,
            ValidationSeverity.LOW.value: 2,
            ValidationSeverity.INFO.value: 0,
        }

        total_penalty = 0
        for issue in issues:
            severity = issue.get("severity", ValidationSeverity.LOW.value)
            total_penalty += severity_weights.get(severity, 2)

        score = max(0, 100 - total_penalty)
        return score


class SyntaxVisitor(ast.NodeVisitor):
    """AST visitor for syntax validation."""

    def __init__(self):
        self.issues = []
        self.recommendations = []

    def visit_Name(self, node):
        """Check for undefined names."""
        # This is a simplified check - real implementation would need scope tracking
        if node.id == "undefined":
            self.issues.append(
                {
                    "type": "undefined",
                    "severity": ValidationSeverity.HIGH.value,
                    "message": f"Potentially undefined name: {node.id}",
                    "line": node.lineno,
                }
            )
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Check function definitions."""
        # Check for missing return in non-void functions
        if node.name != "__init__" and not has_return_statement(node):
            self.recommendations.append(
                f"Function '{node.name}' might be missing a return statement"
            )
        self.generic_visit(node)


def extract_requirement_keywords(requirement: str) -> list[str]:
    """Extract key words from a requirement string."""
    # Remove common words
    stop_words = {"must", "should", "need", "to", "the", "a", "an", "and", "or", "with"}
    words = requirement.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords


def calculate_cyclomatic_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of a function."""
    complexity = 1  # Base complexity

    for child in ast.walk(node):
        if (
            isinstance(child, (ast.If, ast.While, ast.For))
            or isinstance(child, ast.ExceptHandler)
            or isinstance(child, ast.With)
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1

    return complexity


def has_return_statement(node: ast.FunctionDef) -> bool:
    """Check if function has a return statement."""
    for child in ast.walk(node):
        if isinstance(child, ast.Return):
            return True
    return False


def is_imports_sorted(import_lines: list[str]) -> bool:
    """Check if import statements are sorted."""
    sorted_lines = sorted(import_lines, key=lambda x: x.lower())
    return import_lines == sorted_lines
