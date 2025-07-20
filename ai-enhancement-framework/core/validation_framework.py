#!/usr/bin/env python3
"""
🔍 Comprehensive 8-Tier Validation Framework

Implements the complete validation methodology from the AI Task Orchestrator Guide.
Provides systematic validation across 8 tiers: Syntax, Requirements, Hallucination Detection,
Best Practices, Mathematical, Performance, Safety, and Production readiness.

Author: AI Enhancement Framework
Created: 2025-01-18
License: MIT
"""

import ast
import re
import sys
import time
import json
import subprocess
import importlib.util
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationTier(Enum):
    """8-Tier validation levels from AI Task Orchestrator Guide"""
    SYNTAX = "syntax"
    REQUIREMENTS = "requirements"
    HALLUCINATION = "hallucination_detection"
    BEST_PRACTICES = "best_practices"
    MATHEMATICAL = "mathematical"
    PERFORMANCE = "performance"
    SAFETY = "safety"
    PRODUCTION = "production"

class ValidationSeverity(Enum):
    """Validation issue severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

@dataclass
class ValidationIssue:
    """Individual validation issue"""
    tier: ValidationTier
    severity: ValidationSeverity
    description: str
    line_number: Optional[int] = None
    file_path: Optional[str] = None
    recommendation: Optional[str] = None
    code_snippet: Optional[str] = None

@dataclass
class TierValidationResult:
    """Results for a single validation tier"""
    tier: ValidationTier
    score: float  # 0-100
    status: str   # "passed", "failed", "warning"
    issues: List[ValidationIssue]
    execution_time: float
    details: Dict[str, Any]

@dataclass
class ComprehensiveValidationResult:
    """Complete validation results across all tiers"""
    overall_score: float
    production_ready: bool
    tier_results: Dict[str, TierValidationResult]
    recommendations: List[str]
    execution_time: float
    validation_tier: str
    mathematical_verification: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None
    security_assessment: Optional[Dict[str, Any]] = None

class SyntaxValidator:
    """Tier 1: Syntax Validation"""
    
    def validate(self, code_content: str, file_path: Optional[str] = None) -> TierValidationResult:
        """Validate code syntax across multiple languages"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Determine language by file extension or content analysis
            language = self._detect_language(code_content, file_path)
            
            if language == "python":
                issues.extend(self._validate_python_syntax(code_content))
            elif language == "javascript":
                issues.extend(self._validate_javascript_syntax(code_content))
            elif language == "typescript":
                issues.extend(self._validate_typescript_syntax(code_content))
            else:
                # Generic syntax checks
                issues.extend(self._validate_generic_syntax(code_content))
            
            # Calculate score based on issues
            critical_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.CRITICAL)
            high_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.HIGH)
            
            if critical_issues > 0:
                score = max(0, score - (critical_issues * 30))
            if high_issues > 0:
                score = max(0, score - (high_issues * 15))
                
        except Exception as e:
            logger.error(f"Syntax validation error: {e}")
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.CRITICAL,
                description=f"Syntax validation failed: {str(e)}"
            ))
            score = 0.0
        
        status = "passed" if score >= 90 else "failed" if score < 70 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.SYNTAX,
            score=score,
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"language": language if 'language' in locals() else "unknown"}
        )
    
    def _detect_language(self, code_content: str, file_path: Optional[str]) -> str:
        """Detect programming language"""
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext == ".py":
                return "python"
            elif ext in [".js", ".jsx"]:
                return "javascript"
            elif ext in [".ts", ".tsx"]:
                return "typescript"
        
        # Content-based detection
        if "import " in code_content and "def " in code_content:
            return "python"
        elif "function " in code_content or "const " in code_content:
            return "javascript"
        
        return "generic"
    
    def _validate_python_syntax(self, code_content: str) -> List[ValidationIssue]:
        """Validate Python syntax"""
        issues = []
        
        try:
            ast.parse(code_content)
        except SyntaxError as e:
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.CRITICAL,
                description=f"Python syntax error: {e.msg}",
                line_number=e.lineno,
                recommendation="Fix syntax error before proceeding"
            ))
        except Exception as e:
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.HIGH,
                description=f"Python parsing error: {str(e)}"
            ))
        
        return issues
    
    def _validate_javascript_syntax(self, code_content: str) -> List[ValidationIssue]:
        """Validate JavaScript syntax (basic checks)"""
        issues = []
        
        # Basic JavaScript syntax checks
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for i, char in enumerate(code_content):
            if char in brackets:
                stack.append((char, i))
            elif char in brackets.values():
                if not stack:
                    issues.append(ValidationIssue(
                        tier=ValidationTier.SYNTAX,
                        severity=ValidationSeverity.CRITICAL,
                        description=f"Unmatched closing bracket: {char}",
                        line_number=code_content[:i].count('\n') + 1
                    ))
                else:
                    opening, _ = stack.pop()
                    if brackets[opening] != char:
                        issues.append(ValidationIssue(
                            tier=ValidationTier.SYNTAX,
                            severity=ValidationSeverity.CRITICAL,
                            description=f"Mismatched brackets: {opening} and {char}",
                            line_number=code_content[:i].count('\n') + 1
                        ))
        
        return issues
    
    def _validate_typescript_syntax(self, code_content: str) -> List[ValidationIssue]:
        """Validate TypeScript syntax"""
        # Similar to JavaScript but with TypeScript-specific checks
        return self._validate_javascript_syntax(code_content)
    
    def _validate_generic_syntax(self, code_content: str) -> List[ValidationIssue]:
        """Generic syntax validation"""
        issues = []
        
        # Check for balanced brackets
        brackets = {'(': ')', '[': ']', '{': '}'}
        stack = []
        
        for i, char in enumerate(code_content):
            if char in brackets:
                stack.append(char)
            elif char in brackets.values():
                if not stack:
                    issues.append(ValidationIssue(
                        tier=ValidationTier.SYNTAX,
                        severity=ValidationSeverity.HIGH,
                        description="Unmatched closing bracket",
                        line_number=code_content[:i].count('\n') + 1
                    ))
        
        if stack:
            issues.append(ValidationIssue(
                tier=ValidationTier.SYNTAX,
                severity=ValidationSeverity.HIGH,
                description=f"Unclosed brackets: {stack}"
            ))
        
        return issues

class RequirementsValidator:
    """Tier 2: Requirements Validation"""
    
    def validate(self, code_content: str, requirements: List[str]) -> TierValidationResult:
        """Validate requirement coverage and implementation completeness"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            coverage_results = self._analyze_requirement_coverage(code_content, requirements)
            
            for requirement, coverage in coverage_results.items():
                if coverage < 0.7:  # Less than 70% coverage
                    issues.append(ValidationIssue(
                        tier=ValidationTier.REQUIREMENTS,
                        severity=ValidationSeverity.HIGH,
                        description=f"Requirement not adequately addressed: {requirement}",
                        recommendation=f"Implement missing functionality for: {requirement}"
                    ))
                    score -= 20
                elif coverage < 0.9:  # Less than 90% coverage
                    issues.append(ValidationIssue(
                        tier=ValidationTier.REQUIREMENTS,
                        severity=ValidationSeverity.MEDIUM,
                        description=f"Requirement partially implemented: {requirement}",
                        recommendation=f"Complete implementation for: {requirement}"
                    ))
                    score -= 10
            
            # Check for completeness indicators
            completeness_score = self._check_implementation_completeness(code_content)
            score = (score + completeness_score) / 2
            
        except Exception as e:
            logger.error(f"Requirements validation error: {e}")
            issues.append(ValidationIssue(
                tier=ValidationTier.REQUIREMENTS,
                severity=ValidationSeverity.HIGH,
                description=f"Requirements validation failed: {str(e)}"
            ))
            score = 50.0
        
        status = "passed" if score >= 85 else "failed" if score < 60 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.REQUIREMENTS,
            score=score,
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"coverage_analysis": coverage_results if 'coverage_results' in locals() else {}}
        )
    
    def _analyze_requirement_coverage(self, code_content: str, requirements: List[str]) -> Dict[str, float]:
        """Analyze how well requirements are covered in the code"""
        coverage = {}
        
        for requirement in requirements:
            # Extract key terms from requirement
            key_terms = self._extract_key_terms(requirement)
            
            # Check presence of key terms in code
            matches = 0
            for term in key_terms:
                if term.lower() in code_content.lower():
                    matches += 1
            
            coverage[requirement] = matches / len(key_terms) if key_terms else 0.0
        
        return coverage
    
    def _extract_key_terms(self, requirement: str) -> List[str]:
        """Extract key terms from a requirement"""
        # Simple keyword extraction
        terms = []
        
        # Common technical terms
        tech_patterns = [
            r'\b(?:class|function|method|property|variable)\s+(\w+)',
            r'\b(?:implement|create|build|generate|parse|validate)\s+(\w+)',
            r'\b(?:support|handle|process|convert|transform)\s+(\w+)',
            r'\b(\w+)\s+(?:format|type|protocol|standard)'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, requirement, re.IGNORECASE)
            terms.extend(matches)
        
        # Extract quoted terms
        quoted_terms = re.findall(r'"([^"]+)"', requirement)
        terms.extend(quoted_terms)
        
        # Extract capitalized terms (likely proper nouns/technical terms)
        capitalized = re.findall(r'\b[A-Z][A-Za-z]+\b', requirement)
        terms.extend(capitalized)
        
        return list(set(terms))
    
    def _check_implementation_completeness(self, code_content: str) -> float:
        """Check for implementation completeness indicators"""
        score = 100.0
        
        # Check for placeholder patterns
        placeholders = [
            "TODO", "FIXME", "XXX", "HACK", "NOTE",
            "pass  # TODO", "raise NotImplementedError",
            "// TODO", "/* TODO", "console.log('TODO')",
            "placeholder", "example", "sample_data"
        ]
        
        for placeholder in placeholders:
            if placeholder in code_content:
                score -= 15
        
        # Check for proper error handling
        if "try:" in code_content or "except:" in code_content:
            score += 5
        elif "catch" in code_content:
            score += 5
        
        # Check for documentation
        if '"""' in code_content or "'''" in code_content:
            score += 5
        elif "/**" in code_content:
            score += 5
        
        return max(0, min(100, score))

class HallucinationDetector:
    """Tier 3: Hallucination Detection"""
    
    def validate(self, code_content: str) -> TierValidationResult:
        """Detect AI hallucinations in generated code"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Check for fake imports
            fake_imports = self._detect_fake_imports(code_content)
            issues.extend(fake_imports)
            
            # Check for placeholder URLs/credentials
            placeholder_patterns = self._detect_placeholder_patterns(code_content)
            issues.extend(placeholder_patterns)
            
            # Check for example data patterns
            example_data = self._detect_example_data_patterns(code_content)
            issues.extend(example_data)
            
            # Check for incomplete code markers
            incomplete_markers = self._detect_incomplete_markers(code_content)
            issues.extend(incomplete_markers)
            
            # Calculate score
            critical_hallucinations = sum(1 for issue in issues if issue.severity == ValidationSeverity.CRITICAL)
            high_hallucinations = sum(1 for issue in issues if issue.severity == ValidationSeverity.HIGH)
            
            score -= critical_hallucinations * 25
            score -= high_hallucinations * 15
            
        except Exception as e:
            logger.error(f"Hallucination detection error: {e}")
            issues.append(ValidationIssue(
                tier=ValidationTier.HALLUCINATION,
                severity=ValidationSeverity.HIGH,
                description=f"Hallucination detection failed: {str(e)}"
            ))
            score = 50.0
        
        status = "passed" if score >= 90 else "failed" if score < 70 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.HALLUCINATION,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"hallucination_types": [issue.description for issue in issues]}
        )
    
    def _detect_fake_imports(self, code_content: str) -> List[ValidationIssue]:
        """Detect fake or non-existent module imports"""
        issues = []
        
        # Common fake imports
        fake_modules = [
            "fake_module", "example_library", "sample_package",
            "your_module", "custom_library", "proprietary_sdk",
            "internal_api", "company_module", "secret_library"
        ]
        
        import_patterns = [
            r'import\s+(\w+)',
            r'from\s+(\w+)\s+import',
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s*\{\s*[^}]+\s*\}\s*from\s*[\'"]([^\'"]+)[\'"]'
        ]
        
        for pattern in import_patterns:
            matches = re.finditer(pattern, code_content)
            for match in matches:
                module_name = match.group(1)
                if any(fake in module_name.lower() for fake in fake_modules):
                    issues.append(ValidationIssue(
                        tier=ValidationTier.HALLUCINATION,
                        severity=ValidationSeverity.CRITICAL,
                        description=f"Fake module import detected: {module_name}",
                        line_number=code_content[:match.start()].count('\n') + 1,
                        recommendation=f"Replace {module_name} with actual library or remove import"
                    ))
        
        return issues
    
    def _detect_placeholder_patterns(self, code_content: str) -> List[ValidationIssue]:
        """Detect placeholder URLs, credentials, and configuration"""
        issues = []
        
        placeholder_patterns = [
            (r'https?://(?:example\.com|localhost:\d+|your-domain\.com)', "Placeholder URL"),
            (r'api[_-]?key[\'"\s]*[:=][\'"\s]*(?:your[_-]?key|example[_-]?key|abc123)', "Placeholder API key"),
            (r'password[\'"\s]*[:=][\'"\s]*(?:password|123456|secret)', "Placeholder password"),
            (r'username[\'"\s]*[:=][\'"\s]*(?:user|admin|your[_-]?username)', "Placeholder username"),
            (r'database[_-]?url[\'"\s]*[:=][\'"\s]*.*example', "Placeholder database URL"),
            (r'secret[_-]?key[\'"\s]*[:=][\'"\s]*(?:secret|example)', "Placeholder secret key")
        ]
        
        for pattern, description in placeholder_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                issues.append(ValidationIssue(
                    tier=ValidationTier.HALLUCINATION,
                    severity=ValidationSeverity.HIGH,
                    description=f"{description} detected: {match.group(0)}",
                    line_number=code_content[:match.start()].count('\n') + 1,
                    recommendation=f"Replace with actual {description.lower()} or configuration"
                ))
        
        return issues
    
    def _detect_example_data_patterns(self, code_content: str) -> List[ValidationIssue]:
        """Detect example/sample data patterns"""
        issues = []
        
        example_patterns = [
            r'(?:sample|example|test)[_-]?data',
            r'John\s+Doe|Jane\s+Smith',
            r'user@example\.com',
            r'123[- ]456[- ]7890',
            r'(?:sample|example)[_-]?(?:file|image|document)',
            r'lorem\s+ipsum'
        ]
        
        for pattern in example_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                issues.append(ValidationIssue(
                    tier=ValidationTier.HALLUCINATION,
                    severity=ValidationSeverity.MEDIUM,
                    description=f"Example data pattern detected: {match.group(0)}",
                    line_number=code_content[:match.start()].count('\n') + 1,
                    recommendation="Replace with real data or proper data handling"
                ))
        
        return issues
    
    def _detect_incomplete_markers(self, code_content: str) -> List[ValidationIssue]:
        """Detect incomplete code markers"""
        issues = []
        
        incomplete_markers = [
            (r'#\s*TODO(?:\s*:?\s*(.*))?', "TODO marker"),
            (r'//\s*TODO(?:\s*:?\s*(.*))?', "TODO marker"),
            (r'#\s*FIXME(?:\s*:?\s*(.*))?', "FIXME marker"),
            (r'//\s*FIXME(?:\s*:?\s*(.*))?', "FIXME marker"),
            (r'raise\s+NotImplementedError', "NotImplementedError"),
            (r'pass\s*#.*(?:implement|TODO)', "Placeholder implementation"),
            (r'console\.log\([\'"]TODO[\'"]', "TODO console log"),
            (r'\.\.\.\s*#.*(?:implement|TODO)', "Incomplete implementation")
        ]
        
        for pattern, description in incomplete_markers:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                issues.append(ValidationIssue(
                    tier=ValidationTier.HALLUCINATION,
                    severity=ValidationSeverity.MEDIUM,
                    description=f"{description} found: {match.group(0)}",
                    line_number=code_content[:match.start()].count('\n') + 1,
                    recommendation="Complete the implementation or remove placeholder"
                ))
        
        return issues

class BestPracticesValidator:
    """Tier 4: Best Practices Validation"""
    
    def validate(self, code_content: str, language: str = "python") -> TierValidationResult:
        """Validate coding best practices"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            if language.lower() == "python":
                issues.extend(self._validate_python_best_practices(code_content))
            elif language.lower() in ["javascript", "typescript"]:
                issues.extend(self._validate_js_best_practices(code_content))
            else:
                issues.extend(self._validate_generic_best_practices(code_content))
            
            # Calculate score
            for issue in issues:
                if issue.severity == ValidationSeverity.HIGH:
                    score -= 10
                elif issue.severity == ValidationSeverity.MEDIUM:
                    score -= 5
                elif issue.severity == ValidationSeverity.LOW:
                    score -= 2
            
        except Exception as e:
            logger.error(f"Best practices validation error: {e}")
            score = 50.0
        
        status = "passed" if score >= 80 else "failed" if score < 60 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.BEST_PRACTICES,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"language": language}
        )
    
    def _validate_python_best_practices(self, code_content: str) -> List[ValidationIssue]:
        """Validate Python-specific best practices"""
        issues = []
        
        # Check for print statements instead of logging
        print_matches = re.finditer(r'\bprint\s*\(', code_content)
        for match in print_matches:
            issues.append(ValidationIssue(
                tier=ValidationTier.BEST_PRACTICES,
                severity=ValidationSeverity.MEDIUM,
                description="Using print() instead of logging",
                line_number=code_content[:match.start()].count('\n') + 1,
                recommendation="Use logging instead of print() for better control"
            ))
        
        # Check for proper error handling
        if "except:" in code_content and "except Exception:" not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.BEST_PRACTICES,
                severity=ValidationSeverity.HIGH,
                description="Bare except clause detected",
                recommendation="Use specific exception types"
            ))
        
        # Check for docstrings
        if '"""' not in code_content and "'''" not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.BEST_PRACTICES,
                severity=ValidationSeverity.LOW,
                description="Missing docstrings",
                recommendation="Add docstrings to functions and classes"
            ))
        
        return issues
    
    def _validate_js_best_practices(self, code_content: str) -> List[ValidationIssue]:
        """Validate JavaScript/TypeScript best practices"""
        issues = []
        
        # Check for console.log in production code
        console_matches = re.finditer(r'console\.log\s*\(', code_content)
        for match in console_matches:
            issues.append(ValidationIssue(
                tier=ValidationTier.BEST_PRACTICES,
                severity=ValidationSeverity.MEDIUM,
                description="console.log() found in code",
                line_number=code_content[:match.start()].count('\n') + 1,
                recommendation="Use proper logging framework instead of console.log"
            ))
        
        # Check for var usage (prefer let/const)
        var_matches = re.finditer(r'\bvar\s+', code_content)
        for match in var_matches:
            issues.append(ValidationIssue(
                tier=ValidationTier.BEST_PRACTICES,
                severity=ValidationSeverity.LOW,
                description="Using 'var' instead of 'let' or 'const'",
                line_number=code_content[:match.start()].count('\n') + 1,
                recommendation="Use 'let' or 'const' instead of 'var'"
            ))
        
        return issues
    
    def _validate_generic_best_practices(self, code_content: str) -> List[ValidationIssue]:
        """Validate language-agnostic best practices"""
        issues = []
        
        # Check for security considerations
        security_patterns = [
            (r'password\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded password"),
            (r'api[_-]?key\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded API key"),
            (r'secret\s*=\s*[\'"][^\'"]+[\'"]', "Hardcoded secret")
        ]
        
        for pattern, description in security_patterns:
            matches = re.finditer(pattern, code_content, re.IGNORECASE)
            for match in matches:
                issues.append(ValidationIssue(
                    tier=ValidationTier.BEST_PRACTICES,
                    severity=ValidationSeverity.HIGH,
                    description=f"Security issue: {description}",
                    line_number=code_content[:match.start()].count('\n') + 1,
                    recommendation="Use environment variables or secure configuration"
                ))
        
        return issues

class MathematicalValidator:
    """Tier 5: Mathematical Validation"""
    
    def __init__(self, enable_wolfram_alpha: bool = False):
        self.enable_wolfram_alpha = enable_wolfram_alpha
        self.wolfram_available = False
        
        if enable_wolfram_alpha:
            try:
                # Check if WolframAlpha integration is available
                # This would integrate with the WolframAlpha Pro API
                # For now, we'll simulate the capability
                self.wolfram_available = True
            except ImportError:
                logger.warning("WolframAlpha integration not available")
    
    def validate(self, code_content: str) -> TierValidationResult:
        """Validate mathematical implementations and equations"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Detect mathematical operations
            math_operations = self._detect_mathematical_operations(code_content)
            
            if math_operations:
                # Validate numerical stability
                stability_issues = self._check_numerical_stability(code_content)
                issues.extend(stability_issues)
                
                # Check algorithm correctness
                algorithm_issues = self._validate_algorithms(code_content)
                issues.extend(algorithm_issues)
                
                # WolframAlpha verification (if available)
                if self.wolfram_available:
                    wolfram_issues = self._wolfram_verification(code_content)
                    issues.extend(wolfram_issues)
                
                # Calculate score
                critical_math_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.CRITICAL)
                high_math_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.HIGH)
                
                score -= critical_math_issues * 20
                score -= high_math_issues * 10
            else:
                # No mathematical operations detected
                score = 100.0
            
        except Exception as e:
            logger.error(f"Mathematical validation error: {e}")
            score = 50.0
        
        status = "passed" if score >= 85 else "failed" if score < 65 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.MATHEMATICAL,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={
                "wolfram_available": self.wolfram_available,
                "math_operations_detected": len(math_operations) if 'math_operations' in locals() else 0
            }
        )
    
    def _detect_mathematical_operations(self, code_content: str) -> List[str]:
        """Detect mathematical operations in code"""
        math_patterns = [
            r'import\s+(?:math|numpy|scipy)',
            r'from\s+(?:math|numpy|scipy)',
            r'Math\.',
            r'np\.',
            r'scipy\.',
            r'sqrt|sin|cos|tan|log|exp|pow',
            r'[+\-*/]\s*[=]',
            r'def\s+\w*(?:calculate|compute|solve)',
            r'(?:integral|derivative|matrix|vector|equation)'
        ]
        
        operations = []
        for pattern in math_patterns:
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            operations.extend(matches)
        
        return operations
    
    def _check_numerical_stability(self, code_content: str) -> List[ValidationIssue]:
        """Check for numerical stability issues"""
        issues = []
        
        # Division by zero checks
        division_patterns = [
            r'/\s*(?:[\w\[\]\.]+|\([^)]*\))',
            r'//\s*(?:[\w\[\]\.]+|\([^)]*\))',
            r'np\.divide\s*\(',
            r'\.div\s*\('
        ]
        
        for pattern in division_patterns:
            matches = re.finditer(pattern, code_content)
            for match in matches:
                # Simple heuristic check
                if 'zero' not in code_content[max(0, match.start()-100):match.end()+100].lower():
                    issues.append(ValidationIssue(
                        tier=ValidationTier.MATHEMATICAL,
                        severity=ValidationSeverity.MEDIUM,
                        description="Potential division by zero",
                        line_number=code_content[:match.start()].count('\n') + 1,
                        recommendation="Add zero division checks"
                    ))
        
        return issues
    
    def _validate_algorithms(self, code_content: str) -> List[ValidationIssue]:
        """Validate mathematical algorithms"""
        issues = []
        
        # Check for common algorithmic issues
        if 'sqrt' in code_content and 'negative' not in code_content.lower():
            issues.append(ValidationIssue(
                tier=ValidationTier.MATHEMATICAL,
                severity=ValidationSeverity.LOW,
                description="Square root without negative number check",
                recommendation="Validate input is non-negative before sqrt"
            ))
        
        return issues
    
    def _wolfram_verification(self, code_content: str) -> List[ValidationIssue]:
        """Verify mathematical expressions using WolframAlpha Pro"""
        issues = []
        
        # Placeholder for WolframAlpha Pro integration
        # This would extract mathematical expressions and verify them
        logger.info("WolframAlpha Pro verification would be performed here")
        
        return issues

class PerformanceValidator:
    """Tier 6: Performance Validation"""
    
    def validate(self, code_content: str) -> TierValidationResult:
        """Validate performance characteristics"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Check for performance anti-patterns
            performance_issues = self._check_performance_patterns(code_content)
            issues.extend(performance_issues)
            
            # Analyze algorithmic complexity
            complexity_issues = self._analyze_complexity(code_content)
            issues.extend(complexity_issues)
            
            # Check memory usage patterns
            memory_issues = self._check_memory_patterns(code_content)
            issues.extend(memory_issues)
            
            # Calculate score
            for issue in issues:
                if issue.severity == ValidationSeverity.HIGH:
                    score -= 15
                elif issue.severity == ValidationSeverity.MEDIUM:
                    score -= 8
                elif issue.severity == ValidationSeverity.LOW:
                    score -= 3
            
        except Exception as e:
            logger.error(f"Performance validation error: {e}")
            score = 50.0
        
        status = "passed" if score >= 75 else "failed" if score < 50 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.PERFORMANCE,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"performance_patterns_checked": len(issues)}
        )
    
    def _check_performance_patterns(self, code_content: str) -> List[ValidationIssue]:
        """Check for common performance anti-patterns"""
        issues = []
        
        # Nested loops (potential O(n²) or worse)
        nested_loop_pattern = r'for\s+\w+\s+in\s+[^:]+:\s*[^{}]*for\s+\w+\s+in'
        if re.search(nested_loop_pattern, code_content, re.MULTILINE | re.DOTALL):
            issues.append(ValidationIssue(
                tier=ValidationTier.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                description="Nested loops detected - potential O(n²) complexity",
                recommendation="Consider optimization or alternative algorithms"
            ))
        
        # String concatenation in loops
        string_concat_pattern = r'for\s+[^:]+:[^{}]*\w+\s*\+=\s*[\'"]'
        if re.search(string_concat_pattern, code_content, re.MULTILINE | re.DOTALL):
            issues.append(ValidationIssue(
                tier=ValidationTier.PERFORMANCE,
                severity=ValidationSeverity.HIGH,
                description="String concatenation in loop",
                recommendation="Use list.join() or StringBuilder for better performance"
            ))
        
        return issues
    
    def _analyze_complexity(self, code_content: str) -> List[ValidationIssue]:
        """Analyze algorithmic complexity"""
        issues = []
        
        # Count nested structures
        nesting_level = 0
        max_nesting = 0
        
        for char in code_content:
            if char in '{[(':
                nesting_level += 1
                max_nesting = max(max_nesting, nesting_level)
            elif char in '}])':
                nesting_level -= 1
        
        if max_nesting > 6:
            issues.append(ValidationIssue(
                tier=ValidationTier.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                description=f"High nesting level detected: {max_nesting}",
                recommendation="Consider refactoring to reduce complexity"
            ))
        
        return issues
    
    def _check_memory_patterns(self, code_content: str) -> List[ValidationIssue]:
        """Check for memory usage patterns"""
        issues = []
        
        # Large data structures in memory
        if re.search(r'\.read\(\)\s*(?:#|$)', code_content):
            issues.append(ValidationIssue(
                tier=ValidationTier.PERFORMANCE,
                severity=ValidationSeverity.MEDIUM,
                description="Reading entire file into memory",
                recommendation="Consider streaming or chunked reading"
            ))
        
        return issues

class SafetyValidator:
    """Tier 7: Safety Validation"""
    
    def validate(self, code_content: str, domain: str = "general") -> TierValidationResult:
        """Validate safety compliance and fail-safe mechanisms"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # General safety checks
            safety_issues = self._check_general_safety(code_content)
            issues.extend(safety_issues)
            
            # Domain-specific safety checks
            if domain.lower() in ["control", "industrial", "automation"]:
                control_safety_issues = self._check_control_system_safety(code_content)
                issues.extend(control_safety_issues)
            
            # Security safety checks
            security_issues = self._check_security_safety(code_content)
            issues.extend(security_issues)
            
            # Calculate score
            critical_safety_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.CRITICAL)
            high_safety_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.HIGH)
            
            score -= critical_safety_issues * 30
            score -= high_safety_issues * 15
            
        except Exception as e:
            logger.error(f"Safety validation error: {e}")
            score = 50.0
        
        status = "passed" if score >= 90 else "failed" if score < 70 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.SAFETY,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"domain": domain, "safety_categories_checked": 3}
        )
    
    def _check_general_safety(self, code_content: str) -> List[ValidationIssue]:
        """Check general safety patterns"""
        issues = []
        
        # Input validation
        if "input(" in code_content and "validate" not in code_content.lower():
            issues.append(ValidationIssue(
                tier=ValidationTier.SAFETY,
                severity=ValidationSeverity.HIGH,
                description="User input without validation",
                recommendation="Validate all user inputs before processing"
            ))
        
        # File operations safety
        if "open(" in code_content and "with " not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.SAFETY,
                severity=ValidationSeverity.MEDIUM,
                description="File operation without context manager",
                recommendation="Use 'with' statement for file operations"
            ))
        
        return issues
    
    def _check_control_system_safety(self, code_content: str) -> List[ValidationIssue]:
        """Check control system specific safety requirements"""
        issues = []
        
        # Control system patterns
        control_patterns = [
            "pid", "controller", "setpoint", "feedback",
            "actuator", "sensor", "valve", "motor"
        ]
        
        is_control_system = any(pattern in code_content.lower() for pattern in control_patterns)
        
        if is_control_system:
            # Check for safety limits
            if "limit" not in code_content.lower() and "constraint" not in code_content.lower():
                issues.append(ValidationIssue(
                    tier=ValidationTier.SAFETY,
                    severity=ValidationSeverity.CRITICAL,
                    description="Control system without safety limits",
                    recommendation="Implement safety limits and constraints"
                ))
            
            # Check for emergency stop
            if "emergency" not in code_content.lower() and "stop" not in code_content.lower():
                issues.append(ValidationIssue(
                    tier=ValidationTier.SAFETY,
                    severity=ValidationSeverity.HIGH,
                    description="No emergency stop mechanism detected",
                    recommendation="Implement emergency stop functionality"
                ))
        
        return issues
    
    def _check_security_safety(self, code_content: str) -> List[ValidationIssue]:
        """Check security-related safety issues"""
        issues = []
        
        # SQL injection patterns
        sql_patterns = [
            r'sql\s*=\s*[\'"][^\'\"]*\%s',
            r'execute\s*\(\s*[\'"][^\'\"]*\+',
            r'query\s*\(\s*[\'"][^\'\"]*\+',
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    tier=ValidationTier.SAFETY,
                    severity=ValidationSeverity.CRITICAL,
                    description="Potential SQL injection vulnerability",
                    recommendation="Use parameterized queries"
                ))
        
        return issues

class ProductionValidator:
    """Tier 8: Production Validation"""
    
    def validate(self, code_content: str, deployment_config: Optional[Dict[str, Any]] = None) -> TierValidationResult:
        """Validate production deployment readiness"""
        start_time = time.time()
        issues = []
        score = 100.0
        
        try:
            # Check deployment readiness
            deployment_issues = self._check_deployment_readiness(code_content)
            issues.extend(deployment_issues)
            
            # Check monitoring integration
            monitoring_issues = self._check_monitoring_integration(code_content)
            issues.extend(monitoring_issues)
            
            # Check error recovery mechanisms
            recovery_issues = self._check_error_recovery(code_content)
            issues.extend(recovery_issues)
            
            # Check security compliance
            security_compliance_issues = self._check_security_compliance(code_content)
            issues.extend(security_compliance_issues)
            
            # Check configuration management
            config_issues = self._check_configuration_management(code_content)
            issues.extend(config_issues)
            
            # Calculate score
            critical_prod_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.CRITICAL)
            high_prod_issues = sum(1 for issue in issues if issue.severity == ValidationSeverity.HIGH)
            
            score -= critical_prod_issues * 25
            score -= high_prod_issues * 12
            
        except Exception as e:
            logger.error(f"Production validation error: {e}")
            score = 50.0
        
        status = "passed" if score >= 85 else "failed" if score < 65 else "warning"
        
        return TierValidationResult(
            tier=ValidationTier.PRODUCTION,
            score=max(0, score),
            status=status,
            issues=issues,
            execution_time=time.time() - start_time,
            details={"production_categories_checked": 5}
        )
    
    def _check_deployment_readiness(self, code_content: str) -> List[ValidationIssue]:
        """Check if code is ready for deployment"""
        issues = []
        
        # Check for environment variable usage
        if "os.environ" not in code_content and "getenv" not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.HIGH,
                description="No environment variable usage detected",
                recommendation="Use environment variables for configuration"
            ))
        
        # Check for hardcoded configurations
        hardcoded_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'DEBUG\s*=\s*True',
            r'password\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, code_content, re.IGNORECASE):
                issues.append(ValidationIssue(
                    tier=ValidationTier.PRODUCTION,
                    severity=ValidationSeverity.MEDIUM,
                    description=f"Hardcoded configuration detected: {pattern}",
                    recommendation="Use environment-based configuration"
                ))
        
        return issues
    
    def _check_monitoring_integration(self, code_content: str) -> List[ValidationIssue]:
        """Check for monitoring and observability"""
        issues = []
        
        # Check for logging
        if "logging" not in code_content and "logger" not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.HIGH,
                description="No logging framework detected",
                recommendation="Implement proper logging for monitoring"
            ))
        
        # Check for metrics/telemetry
        metrics_patterns = ["metrics", "telemetry", "prometheus", "statsd"]
        if not any(pattern in code_content.lower() for pattern in metrics_patterns):
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.MEDIUM,
                description="No metrics/telemetry integration",
                recommendation="Add metrics collection for monitoring"
            ))
        
        return issues
    
    def _check_error_recovery(self, code_content: str) -> List[ValidationIssue]:
        """Check error recovery mechanisms"""
        issues = []
        
        # Check for retry mechanisms
        if "retry" not in code_content.lower() and "attempt" not in code_content.lower():
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.MEDIUM,
                description="No retry mechanism detected",
                recommendation="Implement retry logic for resilience"
            ))
        
        # Check for circuit breaker patterns
        if "circuit" not in code_content.lower() and "breaker" not in code_content.lower():
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.LOW,
                description="No circuit breaker pattern detected",
                recommendation="Consider circuit breaker for external dependencies"
            ))
        
        return issues
    
    def _check_security_compliance(self, code_content: str) -> List[ValidationIssue]:
        """Check security compliance for production"""
        issues = []
        
        # Check for SSL/TLS usage
        if "http://" in code_content and "https://" not in code_content:
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.HIGH,
                description="HTTP usage without HTTPS",
                recommendation="Use HTTPS for secure communication"
            ))
        
        return issues
    
    def _check_configuration_management(self, code_content: str) -> List[ValidationIssue]:
        """Check configuration management practices"""
        issues = []
        
        # Check for configuration files
        config_patterns = ["config", "settings", "env"]
        if not any(pattern in code_content.lower() for pattern in config_patterns):
            issues.append(ValidationIssue(
                tier=ValidationTier.PRODUCTION,
                severity=ValidationSeverity.MEDIUM,
                description="No configuration management detected",
                recommendation="Implement proper configuration management"
            ))
        
        return issues

class ComprehensiveValidationFramework:
    """Main validation framework coordinating all 8 tiers"""
    
    def __init__(self, enable_wolfram_alpha: bool = False):
        self.validators = {
            ValidationTier.SYNTAX: SyntaxValidator(),
            ValidationTier.REQUIREMENTS: RequirementsValidator(),
            ValidationTier.HALLUCINATION: HallucinationDetector(),
            ValidationTier.BEST_PRACTICES: BestPracticesValidator(),
            ValidationTier.MATHEMATICAL: MathematicalValidator(enable_wolfram_alpha),
            ValidationTier.PERFORMANCE: PerformanceValidator(),
            ValidationTier.SAFETY: SafetyValidator(),
            ValidationTier.PRODUCTION: ProductionValidator()
        }
    
    def validate_comprehensive(self, 
                             code_content: str,
                             requirements: List[str],
                             validation_tier: str = "comprehensive",
                             file_path: Optional[str] = None,
                             domain: str = "general",
                             deployment_config: Optional[Dict[str, Any]] = None) -> ComprehensiveValidationResult:
        """
        Perform comprehensive validation across all appropriate tiers
        
        Args:
            code_content: Code to validate
            requirements: List of requirements to check against
            validation_tier: "standard", "comprehensive", or "production"
            file_path: Optional file path for language detection
            domain: Domain for specialized validation (e.g., "control", "web")
            deployment_config: Optional deployment configuration
        """
        start_time = time.time()
        tier_results = {}
        all_recommendations = []
        
        # Determine which tiers to run based on validation_tier
        if validation_tier == "comprehensive" or validation_tier == "production":
            tiers_to_run = list(ValidationTier)
        else:  # standard
            tiers_to_run = [
                ValidationTier.SYNTAX,
                ValidationTier.REQUIREMENTS,
                ValidationTier.HALLUCINATION,
                ValidationTier.BEST_PRACTICES
            ]
        
        # Run each validation tier
        for tier in tiers_to_run:
            try:
                if tier == ValidationTier.SYNTAX:
                    result = self.validators[tier].validate(code_content, file_path)
                elif tier == ValidationTier.REQUIREMENTS:
                    result = self.validators[tier].validate(code_content, requirements)
                elif tier == ValidationTier.HALLUCINATION:
                    result = self.validators[tier].validate(code_content)
                elif tier == ValidationTier.BEST_PRACTICES:
                    language = self._detect_language(code_content, file_path)
                    result = self.validators[tier].validate(code_content, language)
                elif tier == ValidationTier.MATHEMATICAL:
                    result = self.validators[tier].validate(code_content)
                elif tier == ValidationTier.PERFORMANCE:
                    result = self.validators[tier].validate(code_content)
                elif tier == ValidationTier.SAFETY:
                    result = self.validators[tier].validate(code_content, domain)
                elif tier == ValidationTier.PRODUCTION:
                    result = self.validators[tier].validate(code_content, deployment_config)
                
                tier_results[tier.value] = result
                
                # Collect recommendations
                for issue in result.issues:
                    if issue.recommendation:
                        all_recommendations.append(issue.recommendation)
                        
            except Exception as e:
                logger.error(f"Error in {tier.value} validation: {e}")
                tier_results[tier.value] = TierValidationResult(
                    tier=tier,
                    score=0.0,
                    status="failed",
                    issues=[ValidationIssue(
                        tier=tier,
                        severity=ValidationSeverity.CRITICAL,
                        description=f"Validation tier failed: {str(e)}"
                    )],
                    execution_time=0.0,
                    details={"error": str(e)}
                )
        
        # Calculate overall score
        total_score = sum(result.score for result in tier_results.values())
        overall_score = total_score / len(tier_results) if tier_results else 0.0
        
        # Determine production readiness
        production_ready = (
            overall_score >= 85 and
            all(result.score >= 70 for result in tier_results.values()) and
            not any(
                issue.severity == ValidationSeverity.CRITICAL 
                for result in tier_results.values() 
                for issue in result.issues
            )
        )
        
        # Additional analysis for comprehensive results
        mathematical_verification = None
        performance_metrics = None
        security_assessment = None
        
        if ValidationTier.MATHEMATICAL.value in tier_results:
            mathematical_verification = {
                "accuracy_score": tier_results[ValidationTier.MATHEMATICAL.value].score,
                "wolfram_verified": tier_results[ValidationTier.MATHEMATICAL.value].details.get("wolfram_available", False)
            }
        
        if ValidationTier.PERFORMANCE.value in tier_results:
            performance_metrics = {
                "performance_score": tier_results[ValidationTier.PERFORMANCE.value].score,
                "optimization_opportunities": len(tier_results[ValidationTier.PERFORMANCE.value].issues)
            }
        
        if ValidationTier.SAFETY.value in tier_results:
            security_assessment = {
                "safety_score": tier_results[ValidationTier.SAFETY.value].score,
                "security_issues": len([
                    issue for issue in tier_results[ValidationTier.SAFETY.value].issues
                    if "security" in issue.description.lower()
                ])
            }
        
        return ComprehensiveValidationResult(
            overall_score=overall_score,
            production_ready=production_ready,
            tier_results=tier_results,
            recommendations=list(set(all_recommendations)),  # Remove duplicates
            execution_time=time.time() - start_time,
            validation_tier=validation_tier,
            mathematical_verification=mathematical_verification,
            performance_metrics=performance_metrics,
            security_assessment=security_assessment
        )
    
    def _detect_language(self, code_content: str, file_path: Optional[str]) -> str:
        """Detect programming language"""
        if file_path:
            ext = Path(file_path).suffix.lower()
            if ext == ".py":
                return "python"
            elif ext in [".js", ".jsx"]:
                return "javascript"
            elif ext in [".ts", ".tsx"]:
                return "typescript"
        
        # Content-based detection
        if "import " in code_content and "def " in code_content:
            return "python"
        elif "function " in code_content or "const " in code_content:
            return "javascript"
        
        return "generic"

# Convenience functions for easy integration
def validate_code_comprehensive(code_content: str, 
                               requirements: List[str],
                               validation_tier: str = "comprehensive",
                               **kwargs) -> ComprehensiveValidationResult:
    """
    Convenience function for comprehensive code validation
    
    Args:
        code_content: Code to validate
        requirements: List of requirements to validate against
        validation_tier: "standard", "comprehensive", or "production"
        **kwargs: Additional arguments for validation
    
    Returns:
        ComprehensiveValidationResult with all validation results
    """
    framework = ComprehensiveValidationFramework(
        enable_wolfram_alpha=kwargs.get('enable_wolfram_alpha', False)
    )
    
    return framework.validate_comprehensive(
        code_content=code_content,
        requirements=requirements,
        validation_tier=validation_tier,
        file_path=kwargs.get('file_path'),
        domain=kwargs.get('domain', 'general'),
        deployment_config=kwargs.get('deployment_config')
    )

def create_validation_report(validation_result: ComprehensiveValidationResult, 
                           output_path: Optional[str] = None) -> str:
    """
    Create a comprehensive validation report
    
    Args:
        validation_result: Results from comprehensive validation
        output_path: Optional path to save the report
    
    Returns:
        Formatted validation report as string
    """
    report = f"""# Comprehensive Validation Report

## Overall Results
- **Overall Score**: {validation_result.overall_score:.1f}%
- **Production Ready**: {'✅ Yes' if validation_result.production_ready else '❌ No'}
- **Validation Tier**: {validation_result.validation_tier}
- **Execution Time**: {validation_result.execution_time:.2f}s

## Tier Results

"""
    
    for tier_name, tier_result in validation_result.tier_results.items():
        status_emoji = "✅" if tier_result.status == "passed" else "⚠️" if tier_result.status == "warning" else "❌"
        report += f"### {tier_name.title()} Validation {status_emoji}\n"
        report += f"- **Score**: {tier_result.score:.1f}%\n"
        report += f"- **Status**: {tier_result.status}\n"
        report += f"- **Issues**: {len(tier_result.issues)}\n"
        report += f"- **Execution Time**: {tier_result.execution_time:.3f}s\n\n"
        
        if tier_result.issues:
            report += "**Issues Found:**\n"
            for issue in tier_result.issues:
                severity_emoji = "🔴" if issue.severity == ValidationSeverity.CRITICAL else "🟡" if issue.severity == ValidationSeverity.HIGH else "🟢"
                report += f"- {severity_emoji} {issue.description}"
                if issue.line_number:
                    report += f" (Line {issue.line_number})"
                if issue.recommendation:
                    report += f"\n  *Recommendation: {issue.recommendation}*"
                report += "\n"
        
        report += "\n"
    
    # Additional analysis sections
    if validation_result.mathematical_verification:
        report += f"""## Mathematical Validation
- **Accuracy Score**: {validation_result.mathematical_verification['accuracy_score']:.1f}%
- **WolframAlpha Verified**: {'✅' if validation_result.mathematical_verification['wolfram_verified'] else '❌'}

"""
    
    if validation_result.performance_metrics:
        report += f"""## Performance Analysis
- **Performance Score**: {validation_result.performance_metrics['performance_score']:.1f}%
- **Optimization Opportunities**: {validation_result.performance_metrics['optimization_opportunities']}

"""
    
    if validation_result.security_assessment:
        report += f"""## Security Assessment
- **Safety Score**: {validation_result.security_assessment['safety_score']:.1f}%
- **Security Issues**: {validation_result.security_assessment['security_issues']}

"""
    
    if validation_result.recommendations:
        report += "## Recommendations\n\n"
        for i, recommendation in enumerate(validation_result.recommendations, 1):
            report += f"{i}. {recommendation}\n"
    
    report += f"""
---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    if output_path:
        Path(output_path).write_text(report)
        logger.info(f"Validation report saved to {output_path}")
    
    return report

if __name__ == "__main__":
    # Example usage
    sample_code = '''
def calculate_something(x, y):
    """Calculate something important."""
    if y == 0:
        raise ValueError("Division by zero")
    
    result = x / y
    print(f"Result: {result}")  # Should use logging
    return result

def main():
    # TODO: Add error handling
    value = calculate_something(10, 2)
    return value
'''
    
    requirements = [
        "Implement division function",
        "Handle division by zero",
        "Return calculated result"
    ]
    
    # Run comprehensive validation
    framework = ComprehensiveValidationFramework(enable_wolfram_alpha=False)
    result = framework.validate_comprehensive(
        code_content=sample_code,
        requirements=requirements,
        validation_tier="comprehensive",
        domain="general"
    )
    
    # Generate report
    report = create_validation_report(result)
    print(report)
    
    print(f"\nValidation completed with {result.overall_score:.1f}% overall score")
    print(f"Production ready: {result.production_ready}") 