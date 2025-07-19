#!/usr/bin/env python3
"""
🔍 Universal Code Analysis Framework - AI Enhancement Framework

Generalized static code analysis system extracted from plc-gbt project.
Provides comprehensive code analysis with hallucination detection, quality assessment,
and refactoring recommendations for any codebase.

Universal Features:
- Multi-language code analysis support
- AI hallucination detection in generated code
- Code quality and complexity analysis
- Semantic analysis with configurable providers
- Refactoring recommendations
- Extensible analyzer architecture
- Integration with existing code analysis tools

Author: AI Enhancement Framework (Phase 25)
Extracted from: plc-gbt Static Analysis Framework
Created: 2025-01-18
License: MIT
"""

import ast
import os
import sys
import re
import json
import time
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Core Types and Enums
# ============================================================================

class AnalysisLevel(Enum):
    """Analysis depth levels"""
    SURFACE = "surface"           # Basic syntax and imports
    STRUCTURAL = "structural"     # Functions, classes, complexity  
    SEMANTIC = "semantic"         # Type inference, data flow
    COMPREHENSIVE = "comprehensive" # All analysis + advanced features

class IssueCategory(Enum):
    """Categories of code issues"""
    SYNTAX_ERROR = "syntax_error"
    HALLUCINATION = "hallucination"
    QUALITY_ISSUE = "quality_issue"
    SECURITY_ISSUE = "security_issue"
    PERFORMANCE_ISSUE = "performance_issue"
    MAINTAINABILITY_ISSUE = "maintainability_issue"

class IssueSeverity(Enum):
    """Issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class HallucinationType(Enum):
    """Types of AI hallucinations in code"""
    FAKE_IMPORTS = "fake_imports"
    PLACEHOLDER_VALUES = "placeholder_values"
    TODO_MARKERS = "todo_markers"
    INCOMPLETE_IMPLEMENTATIONS = "incomplete_implementations"
    NON_EXISTENT_APIS = "non_existent_apis"
    EXAMPLE_DATA = "example_data"

@dataclass
class CodeIssue:
    """Universal code issue representation"""
    category: IssueCategory
    severity: IssueSeverity
    line_number: int
    column: int
    description: str
    evidence: str
    suggestion: str
    confidence: float  # 0.0 to 1.0
    issue_type: Optional[str] = None  # Specific type within category
    fix_available: bool = False

@dataclass
class AnalysisResult:
    """Universal analysis result"""
    file_path: str
    analysis_timestamp: datetime
    analysis_level: AnalysisLevel
    language: str
    success: bool
    
    # Basic results
    syntax_valid: bool
    line_count: int
    char_count: int
    
    # Issues found
    issues: List[CodeIssue]
    issue_counts: Dict[IssueCategory, int]
    
    # Metrics
    complexity_score: float
    maintainability_score: float
    quality_score: float
    
    # Additional analysis data
    metadata: Dict[str, Any]
    recommendations: List[str]
    
    # Performance
    analysis_time_ms: float

# ============================================================================
# Analyzer Interface
# ============================================================================

class CodeAnalyzer(ABC):
    """Abstract base class for code analyzers"""
    
    @abstractmethod
    def analyze(self, content: str, file_path: Path) -> AnalysisResult:
        """Analyze code content"""
        pass
    
    @abstractmethod
    def get_supported_languages(self) -> List[str]:
        """Get list of supported programming languages"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get analyzer capabilities"""
        pass

# ============================================================================
# Universal Analyzers
# ============================================================================

class HallucinationDetector:
    """Universal AI hallucination detector for code"""
    
    def __init__(self, custom_patterns: Optional[Dict[str, List[str]]] = None):
        """Initialize with optional custom patterns"""
        self.patterns = self._load_default_patterns()
        if custom_patterns:
            self.patterns.update(custom_patterns)
    
    def detect_hallucinations(self, content: str, file_path: Path, language: str) -> List[CodeIssue]:
        """Detect AI hallucinations in code"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Language-specific detection
            if language.lower() in ['python', 'py']:
                issues.extend(self._detect_python_hallucinations(line, line_num))
            elif language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                issues.extend(self._detect_js_hallucinations(line, line_num))
            
            # Universal patterns
            issues.extend(self._detect_universal_hallucinations(line, line_num))
        
        return issues
    
    def _detect_python_hallucinations(self, line: str, line_num: int) -> List[CodeIssue]:
        """Detect Python-specific hallucinations"""
        issues = []
        
        # Fake imports
        if line.strip().startswith(('import ', 'from ')):
            fake_patterns = [
                r'import\s+(fake_|mock_|example_|placeholder_|nonexistent_)',
                r'from\s+(fake_|mock_|example_|placeholder_|fictional_)'
            ]
            
            for pattern in fake_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.HALLUCINATION,
                        severity=IssueSeverity.HIGH,
                        line_number=line_num,
                        column=0,
                        description="Potentially fake or placeholder import",
                        evidence=line.strip(),
                        suggestion="Replace with actual import or remove",
                        confidence=0.8,
                        issue_type=HallucinationType.FAKE_IMPORTS.value
                    ))
        
        return issues
    
    def _detect_js_hallucinations(self, line: str, line_num: int) -> List[CodeIssue]:
        """Detect JavaScript/TypeScript-specific hallucinations"""
        issues = []
        
        # Fake requires/imports
        if 'require(' in line or 'import ' in line:
            fake_patterns = [
                r'require\(["\']fake_',
                r'import.*from\s+["\']fake_',
                r'import.*from\s+["\']example_'
            ]
            
            for pattern in fake_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.HALLUCINATION,
                        severity=IssueSeverity.HIGH,
                        line_number=line_num,
                        column=0,
                        description="Potentially fake module import",
                        evidence=line.strip(),
                        suggestion="Replace with actual module or remove",
                        confidence=0.8,
                        issue_type=HallucinationType.FAKE_IMPORTS.value
                    ))
        
        return issues
    
    def _detect_universal_hallucinations(self, line: str, line_num: int) -> List[CodeIssue]:
        """Detect universal hallucination patterns"""
        issues = []
        
        # Placeholder values
        placeholder_patterns = [
            r'YOUR_API_KEY',
            r'PLACEHOLDER_\w+',
            r'EXAMPLE_\w+',
            r'REPLACE_WITH_\w+',
            r'INSERT_\w+_HERE'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(CodeIssue(
                    category=IssueCategory.HALLUCINATION,
                    severity=IssueSeverity.MEDIUM,
                    line_number=line_num,
                    column=0,
                    description="Placeholder value that needs replacement",
                    evidence=line.strip(),
                    suggestion="Replace with actual value",
                    confidence=0.9,
                    issue_type=HallucinationType.PLACEHOLDER_VALUES.value
                ))
        
        # TODO markers
        todo_patterns = [
            r'TODO\s*:',
            r'FIXME\s*:',
            r'XXX\s*:',
            r'HACK\s*:',
            r'NOTE\s*:'
        ]
        
        for pattern in todo_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(CodeIssue(
                    category=IssueCategory.HALLUCINATION,
                    severity=IssueSeverity.LOW,
                    line_number=line_num,
                    column=0,
                    description="TODO marker indicating incomplete code",
                    evidence=line.strip(),
                    suggestion="Complete implementation or remove TODO",
                    confidence=1.0,
                    issue_type=HallucinationType.TODO_MARKERS.value
                ))
        
        return issues
    
    def _load_default_patterns(self) -> Dict[str, List[str]]:
        """Load default hallucination patterns"""
        return {
            "fake_imports": [
                r"import\s+(fake_|mock_|example_|placeholder_)",
                r"from\s+(fake_|mock_|example_|fictional_)"
            ],
            "placeholders": [
                r"YOUR_\w+",
                r"PLACEHOLDER_\w+",
                r"EXAMPLE_\w+",
                r"REPLACE_WITH_\w+",
                r"INSERT_\w+_HERE"
            ],
            "todos": [
                r"TODO\s*:",
                r"FIXME\s*:",
                r"XXX\s*:",
                r"HACK\s*:",
                r"NOTE\s*:"
            ]
        }

class QualityAnalyzer:
    """Universal code quality analyzer"""
    
    def __init__(self):
        self.metrics = {}
    
    def analyze_quality(self, content: str, file_path: Path, language: str) -> List[CodeIssue]:
        """Analyze code quality issues"""
        issues = []
        
        if language.lower() in ['python', 'py']:
            issues.extend(self._analyze_python_quality(content))
        elif language.lower() in ['javascript', 'js']:
            issues.extend(self._analyze_js_quality(content))
        
        # Universal quality checks
        issues.extend(self._analyze_universal_quality(content))
        
        return issues
    
    def _analyze_python_quality(self, content: str) -> List[CodeIssue]:
        """Analyze Python-specific quality issues"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Check for overly complex functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_cyclomatic_complexity(node)
                    if complexity > 10:
                        issues.append(CodeIssue(
                            category=IssueCategory.QUALITY_ISSUE,
                            severity=IssueSeverity.MEDIUM,
                            line_number=node.lineno,
                            column=node.col_offset,
                            description=f"Function '{node.name}' has high complexity ({complexity})",
                            evidence=f"def {node.name}(...)",
                            suggestion="Consider breaking into smaller functions",
                            confidence=0.9,
                            issue_type="high_complexity"
                        ))
                
                # Check for too many parameters
                if isinstance(node, ast.FunctionDef) and len(node.args.args) > 6:
                    issues.append(CodeIssue(
                        category=IssueCategory.QUALITY_ISSUE,
                        severity=IssueSeverity.LOW,
                        line_number=node.lineno,
                        column=node.col_offset,
                        description=f"Function '{node.name}' has too many parameters ({len(node.args.args)})",
                        evidence=f"def {node.name}(...)",
                        suggestion="Consider using a configuration object",
                        confidence=0.7,
                        issue_type="too_many_parameters"
                    ))
        
        except SyntaxError:
            # Skip quality analysis for files with syntax errors
            pass
        
        return issues
    
    def _analyze_js_quality(self, content: str) -> List[CodeIssue]:
        """Analyze JavaScript-specific quality issues"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for console.log in production code
            if 'console.log(' in line and '// debug' not in line.lower():
                issues.append(CodeIssue(
                    category=IssueCategory.QUALITY_ISSUE,
                    severity=IssueSeverity.LOW,
                    line_number=line_num,
                    column=0,
                    description="Console.log statement found",
                    evidence=line.strip(),
                    suggestion="Remove console.log or replace with proper logging",
                    confidence=0.8,
                    issue_type="debug_statement"
                ))
        
        return issues
    
    def _analyze_universal_quality(self, content: str) -> List[CodeIssue]:
        """Analyze universal quality issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for long lines
        for line_num, line in enumerate(lines, 1):
            if len(line) > 120:
                issues.append(CodeIssue(
                    category=IssueCategory.QUALITY_ISSUE,
                    severity=IssueSeverity.LOW,
                    line_number=line_num,
                    column=len(line),
                    description=f"Line too long ({len(line)} characters)",
                    evidence=f"{line[:50]}..." if len(line) > 50 else line,
                    suggestion="Break into multiple lines",
                    confidence=0.9,
                    issue_type="long_line"
                ))
        
        # Check for deeply nested code
        for line_num, line in enumerate(lines, 1):
            leading_spaces = len(line) - len(line.lstrip())
            indent_level = leading_spaces // 4  # Assuming 4-space indentation
            
            if indent_level > 6:
                issues.append(CodeIssue(
                    category=IssueCategory.QUALITY_ISSUE,
                    severity=IssueSeverity.MEDIUM,
                    line_number=line_num,
                    column=0,
                    description=f"Deeply nested code (level {indent_level})",
                    evidence=line.strip(),
                    suggestion="Consider extracting methods or simplifying logic",
                    confidence=0.8,
                    issue_type="deep_nesting"
                ))
        
        return issues
    
    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class SecurityAnalyzer:
    """Universal security analyzer"""
    
    def analyze_security(self, content: str, file_path: Path, language: str) -> List[CodeIssue]:
        """Analyze security issues"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for pattern in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(CodeIssue(
                        category=IssueCategory.SECURITY_ISSUE,
                        severity=IssueSeverity.HIGH,
                        line_number=line_num,
                        column=0,
                        description="Potential hardcoded secret detected",
                        evidence=line.strip(),
                        suggestion="Use environment variables or secure credential storage",
                        confidence=0.7,
                        issue_type="hardcoded_secret"
                    ))
        
        return issues

# ============================================================================
# Universal Code Analyzer
# ============================================================================

class UniversalCodeAnalyzer:
    """
    Universal Code Analysis Framework
    
    Provides comprehensive static analysis for multiple programming languages
    with extensible analyzer architecture and AI hallucination detection.
    
    Features:
    - Multi-language support
    - Modular analyzer system
    - AI hallucination detection
    - Code quality assessment
    - Security analysis
    - Performance metrics
    - Refactoring recommendations
    """
    
    def __init__(self, analysis_level: AnalysisLevel = AnalysisLevel.STRUCTURAL):
        """Initialize the universal code analyzer"""
        self.analysis_level = analysis_level
        self.session_id = f"code_analysis_{int(time.time())}"
        self.start_time = datetime.now()
        
        # Initialize analyzers
        self.hallucination_detector = HallucinationDetector()
        self.quality_analyzer = QualityAnalyzer()
        self.security_analyzer = SecurityAnalyzer()
        
        # Language support
        self.supported_languages = [
            'python', 'py',
            'javascript', 'js', 
            'typescript', 'ts',
            'java',
            'rust', 'rs',
            'go',
            'cpp', 'c++', 'cxx',
            'c', 'h'
        ]
        
        # Custom analyzers
        self.custom_analyzers: Dict[str, CodeAnalyzer] = {}
        
        logger.info(f"UniversalCodeAnalyzer initialized: {self.session_id}")
    
    def analyze_file(self, file_path: Union[str, Path], content: Optional[str] = None) -> AnalysisResult:
        """Analyze a single file"""
        file_path = Path(file_path)
        start_time = time.time()
        
        # Read content if not provided
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                return self._create_error_result(file_path, str(e), start_time)
        
        # Detect language
        language = self._detect_language(file_path, content)
        
        # Initialize result
        result = AnalysisResult(
            file_path=str(file_path),
            analysis_timestamp=datetime.now(),
            analysis_level=self.analysis_level,
            language=language,
            success=True,
            syntax_valid=True,
            line_count=len(content.split('\n')),
            char_count=len(content),
            issues=[],
            issue_counts={category: 0 for category in IssueCategory},
            complexity_score=0.0,
            maintainability_score=0.0,
            quality_score=0.0,
            metadata={},
            recommendations=[],
            analysis_time_ms=0.0
        )
        
        try:
            # Basic syntax validation
            if language in ['python', 'py']:
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    result.syntax_valid = False
                    result.issues.append(CodeIssue(
                        category=IssueCategory.SYNTAX_ERROR,
                        severity=IssueSeverity.CRITICAL,
                        line_number=e.lineno or 1,
                        column=e.offset or 0,
                        description=f"Syntax error: {e.msg}",
                        evidence=str(e),
                        suggestion="Fix syntax error",
                        confidence=1.0
                    ))
            
            # Hallucination detection
            if self.analysis_level in [AnalysisLevel.STRUCTURAL, AnalysisLevel.SEMANTIC, AnalysisLevel.COMPREHENSIVE]:
                hallucination_issues = self.hallucination_detector.detect_hallucinations(content, file_path, language)
                result.issues.extend(hallucination_issues)
            
            # Quality analysis
            if self.analysis_level in [AnalysisLevel.STRUCTURAL, AnalysisLevel.SEMANTIC, AnalysisLevel.COMPREHENSIVE]:
                quality_issues = self.quality_analyzer.analyze_quality(content, file_path, language)
                result.issues.extend(quality_issues)
            
            # Security analysis
            if self.analysis_level in [AnalysisLevel.SEMANTIC, AnalysisLevel.COMPREHENSIVE]:
                security_issues = self.security_analyzer.analyze_security(content, file_path, language)
                result.issues.extend(security_issues)
            
            # Custom analyzer integration
            for analyzer_name, analyzer in self.custom_analyzers.items():
                if language in analyzer.get_supported_languages():
                    try:
                        custom_result = analyzer.analyze(content, file_path)
                        result.issues.extend(custom_result.issues)
                    except Exception as e:
                        logger.warning(f"Custom analyzer {analyzer_name} failed: {e}")
            
            # Calculate metrics
            result.issue_counts = self._count_issues(result.issues)
            result.complexity_score = self._calculate_complexity_score(content, language)
            result.maintainability_score = self._calculate_maintainability_score(result)
            result.quality_score = self._calculate_quality_score(result)
            
            # Generate recommendations
            result.recommendations = self._generate_recommendations(result)
            
        except Exception as e:
            result.success = False
            result.metadata['error'] = str(e)
            logger.error(f"Analysis failed for {file_path}: {e}")
        
        # Calculate analysis time
        result.analysis_time_ms = (time.time() - start_time) * 1000
        
        return result
    
    def analyze_directory(self, directory_path: Union[str, Path], 
                         file_patterns: Optional[List[str]] = None) -> Dict[str, AnalysisResult]:
        """Analyze all files in a directory"""
        directory_path = Path(directory_path)
        results = {}
        
        # Default file patterns
        if file_patterns is None:
            file_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.rs', '*.go', '*.cpp', '*.c', '*.h']
        
        # Find files to analyze
        files_to_analyze = []
        for pattern in file_patterns:
            files_to_analyze.extend(directory_path.rglob(pattern))
        
        logger.info(f"Analyzing {len(files_to_analyze)} files in {directory_path}")
        
        # Analyze each file
        for file_path in files_to_analyze:
            try:
                result = self.analyze_file(file_path)
                results[str(file_path)] = result
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
        
        return results
    
    def add_custom_analyzer(self, name: str, analyzer: CodeAnalyzer):
        """Add a custom analyzer"""
        self.custom_analyzers[name] = analyzer
        logger.info(f"Added custom analyzer: {name}")
    
    def _detect_language(self, file_path: Path, content: str) -> str:
        """Detect programming language from file extension and content"""
        extension = file_path.suffix.lower()
        
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.rs': 'rust',
            '.go': 'go',
            '.cpp': 'cpp',
            '.cxx': 'cpp',
            '.cc': 'cpp',
            '.c': 'c',
            '.h': 'c'
        }
        
        return extension_map.get(extension, 'unknown')
    
    def _count_issues(self, issues: List[CodeIssue]) -> Dict[IssueCategory, int]:
        """Count issues by category"""
        counts = {category: 0 for category in IssueCategory}
        for issue in issues:
            counts[issue.category] += 1
        return counts
    
    def _calculate_complexity_score(self, content: str, language: str) -> float:
        """Calculate code complexity score (0-100, lower is better)"""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if not non_empty_lines:
            return 0.0
        
        # Basic complexity metrics
        avg_line_length = sum(len(line) for line in non_empty_lines) / len(non_empty_lines)
        max_line_length = max(len(line) for line in non_empty_lines) if non_empty_lines else 0
        max_indent = max(len(line) - len(line.lstrip()) for line in non_empty_lines) // 4
        
        # Normalize to 0-100 scale
        complexity = min(100, (avg_line_length / 80) * 30 + (max_line_length / 120) * 30 + (max_indent / 6) * 40)
        
        return round(complexity, 2)
    
    def _calculate_maintainability_score(self, result: AnalysisResult) -> float:
        """Calculate maintainability score (0-100, higher is better)"""
        base_score = 100.0
        
        # Deduct points for issues
        for issue in result.issues:
            if issue.severity == IssueSeverity.CRITICAL:
                base_score -= 10
            elif issue.severity == IssueSeverity.HIGH:
                base_score -= 5
            elif issue.severity == IssueSeverity.MEDIUM:
                base_score -= 2
            elif issue.severity == IssueSeverity.LOW:
                base_score -= 1
        
        return max(0.0, round(base_score, 2))
    
    def _calculate_quality_score(self, result: AnalysisResult) -> float:
        """Calculate overall quality score (0-100, higher is better)"""
        if not result.syntax_valid:
            return 0.0
        
        # Base score
        quality_score = 100.0
        
        # Penalize based on issue density
        issue_density = len(result.issues) / max(result.line_count, 1) * 100
        quality_score -= min(50, issue_density * 10)
        
        # Penalize complexity
        quality_score -= min(30, result.complexity_score * 0.3)
        
        return max(0.0, round(quality_score, 2))
    
    def _generate_recommendations(self, result: AnalysisResult) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # High-priority issues
        critical_issues = [i for i in result.issues if i.severity == IssueSeverity.CRITICAL]
        if critical_issues:
            recommendations.append(f"Fix {len(critical_issues)} critical issue(s) immediately")
        
        # Quality improvements
        if result.quality_score < 60:
            recommendations.append("Improve code quality - consider refactoring complex functions")
        
        # Specific issue patterns
        hallucination_count = result.issue_counts.get(IssueCategory.HALLUCINATION, 0)
        if hallucination_count > 0:
            recommendations.append(f"Remove {hallucination_count} AI hallucination(s) from the code")
        
        security_count = result.issue_counts.get(IssueCategory.SECURITY_ISSUE, 0)
        if security_count > 0:
            recommendations.append(f"Address {security_count} security issue(s)")
        
        # Complexity
        if result.complexity_score > 70:
            recommendations.append("Reduce code complexity by breaking down large functions")
        
        return recommendations
    
    def _create_error_result(self, file_path: Path, error: str, start_time: float) -> AnalysisResult:
        """Create an error result for failed analysis"""
        return AnalysisResult(
            file_path=str(file_path),
            analysis_timestamp=datetime.now(),
            analysis_level=self.analysis_level,
            language="unknown",
            success=False,
            syntax_valid=False,
            line_count=0,
            char_count=0,
            issues=[],
            issue_counts={category: 0 for category in IssueCategory},
            complexity_score=0.0,
            maintainability_score=0.0,
            quality_score=0.0,
            metadata={"error": error},
            recommendations=[],
            analysis_time_ms=(time.time() - start_time) * 1000
        )

# ============================================================================
# Convenience Functions
# ============================================================================

def create_code_analyzer(analysis_level: AnalysisLevel = AnalysisLevel.STRUCTURAL) -> UniversalCodeAnalyzer:
    """Factory function to create a code analyzer"""
    return UniversalCodeAnalyzer(analysis_level)

def analyze_file(file_path: Union[str, Path], 
                analysis_level: AnalysisLevel = AnalysisLevel.STRUCTURAL) -> AnalysisResult:
    """Convenience function to analyze a single file"""
    analyzer = create_code_analyzer(analysis_level)
    return analyzer.analyze_file(file_path)

def analyze_directory(directory_path: Union[str, Path],
                     analysis_level: AnalysisLevel = AnalysisLevel.STRUCTURAL,
                     file_patterns: Optional[List[str]] = None) -> Dict[str, AnalysisResult]:
    """Convenience function to analyze a directory"""
    analyzer = create_code_analyzer(analysis_level)
    return analyzer.analyze_directory(directory_path, file_patterns)

if __name__ == "__main__":
    # Example usage
    def main():
        # Create analyzer
        analyzer = create_code_analyzer(AnalysisLevel.COMPREHENSIVE)
        
        # Analyze a file (create sample file for demo)
        sample_code = """
import fake_module  # This is a hallucination
import os

def overly_complex_function(a, b, c, d, e, f, g, h):
    # TODO: This needs to be implemented
    api_key = "YOUR_API_KEY_HERE"  # Placeholder
    
    if a > 0:
        if b > 0:
            if c > 0:
                if d > 0:
                    if e > 0:
                        if f > 0:
                            if g > 0:
                                if h > 0:
                                    return "deeply nested"
    return "result"

def good_function():
    '''A well-written function with proper documentation.'''
    return "Hello, World!"
"""
        
        # Write sample file
        sample_file = Path("sample_analysis.py")
        with open(sample_file, 'w') as f:
            f.write(sample_code)
        
        try:
            # Analyze the file
            result = analyzer.analyze_file(sample_file)
            
            print(f"Analysis Results for {result.file_path}")
            print(f"Language: {result.language}")
            print(f"Success: {result.success}")
            print(f"Quality Score: {result.quality_score}")
            print(f"Complexity Score: {result.complexity_score}")
            print(f"Issues Found: {len(result.issues)}")
            
            # Show issues
            for issue in result.issues[:5]:  # Show first 5 issues
                print(f"  {issue.severity.value.upper()}: {issue.description} (Line {issue.line_number})")
            
            # Show recommendations
            print(f"Recommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")
        
        finally:
            # Cleanup
            if sample_file.exists():
                sample_file.unlink()
    
    main() 