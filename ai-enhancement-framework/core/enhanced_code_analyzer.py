#!/usr/bin/env python3
"""
🔬 Enhanced Code Analyzer - AI Enhancement Framework
Advanced Static Analysis with libcst & astroid Integration

This module implements comprehensive static code analysis framework including:
- libcst-based CST (Concrete Syntax Tree) analysis for precise code modifications
- astroid-based semantic analysis for advanced inference and type checking
- Hallucination detection for AI-generated code validation
- Code quality analysis with industrial control domain expertise
- Integration with existing ai-enhancement-framework infrastructure

Following AI Task Orchestrator methodology for systematic static analysis enhancement.

Author: AI Enhancement Framework
Created: 2025-01-17
Updated: 2025-01-17 (Phase 17.3.1 Integration)
Dependencies: libcst>=1.0.0, astroid>=3.0.0, existing code_analyzer.py
"""

import asyncio
import logging
import json
import hashlib
import time
import ast
import re
import sys
import os
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Iterator
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum, IntEnum
import uuid
import subprocess
from collections import defaultdict, Counter
import importlib.util

# Advanced static analysis libraries
try:
    import libcst as cst
    from libcst import metadata
    from libcst.metadata import QualifiedNameProvider, ScopeProvider, TypeInferenceProvider
    LIBCST_AVAILABLE = True
    CSTNodeType = cst.CSTNode
except ImportError:
    LIBCST_AVAILABLE = False
    logging.warning("libcst not available - advanced CST analysis disabled")
    CSTNodeType = Any  # Fallback type for when libcst is not available

try:
    import astroid
    from astroid import manager, nodes
    from astroid.exceptions import AstroidError, InferenceError
    ASTROID_AVAILABLE = True
except ImportError:
    ASTROID_AVAILABLE = False
    logging.warning("astroid not available - semantic analysis disabled")

# Import existing framework components
try:
    from .code_analyzer import CodeAnalyzer, AnalysisResult, ComplexityMetrics, CodeIssue
    EXISTING_ANALYZER_AVAILABLE = True
except ImportError:
    EXISTING_ANALYZER_AVAILABLE = False
    logging.warning("Existing code analyzer not available - running in standalone mode")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Core Data Structures for Advanced Static Analysis
# ============================================================================

class AnalysisLevel(Enum):
    """Analysis depth levels for static analysis"""
    SURFACE = "surface"           # Basic syntax checking
    STRUCTURAL = "structural"     # AST-based analysis
    SEMANTIC = "semantic"         # Type inference and semantic analysis
    COMPREHENSIVE = "comprehensive"  # Full libcst/astroid analysis

class HallucinationCategory(Enum):
    """Categories of AI hallucination patterns"""
    FAKE_IMPORTS = "fake_imports"
    PLACEHOLDER_VALUES = "placeholder_values"
    INCOMPLETE_IMPLEMENTATIONS = "incomplete_implementations"
    NON_EXISTENT_APIS = "non_existent_apis"
    EXAMPLE_DATA = "example_data"
    TODO_MARKERS = "todo_markers"
    FICTIONAL_LIBRARIES = "fictional_libraries"
    UNREACHABLE_CODE = "unreachable_code"

class CodeQualityIssue(Enum):
    """Code quality issue types"""
    COMPLEXITY_HIGH = "complexity_high"
    DUPLICATION = "duplication"
    DEAD_CODE = "dead_code"
    UNUSED_IMPORTS = "unused_imports"
    INCONSISTENT_NAMING = "inconsistent_naming"
    SECURITY_RISK = "security_risk"
    PERFORMANCE_ISSUE = "performance_issue"
    MAINTAINABILITY_LOW = "maintainability_low"

@dataclass
class HallucinationDetection:
    """Detected hallucination in code"""
    category: HallucinationCategory
    line_number: int
    column: int
    description: str
    evidence: str
    confidence: float  # 0.0 to 1.0
    suggestion: str
    severity: str  # low, medium, high, critical

@dataclass
class CodeQualityAnalysis:
    """Code quality analysis result"""
    issue_type: CodeQualityIssue
    line_number: Optional[int]
    description: str
    impact: str  # low, medium, high
    recommendation: str
    affected_code: str
    estimated_fix_time: str

@dataclass
class SemanticAnalysis:
    """Semantic analysis result using astroid"""
    defined_names: List[str]
    used_names: List[str]
    undefined_names: List[str]
    type_inferences: Dict[str, str]
    call_graph: Dict[str, List[str]]
    inheritance_hierarchy: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]

@dataclass
class CSTAnalysis:
    """Concrete Syntax Tree analysis using libcst"""
    format_violations: List[str]
    whitespace_issues: List[str]
    comment_analysis: Dict[str, Any]
    docstring_coverage: float
    modification_suggestions: List[str]
    code_style_score: float

@dataclass
class EnhancedAnalysisResult:
    """Comprehensive enhanced analysis result"""
    file_path: str
    analysis_timestamp: datetime
    analysis_level: AnalysisLevel
    
    # Basic analysis
    syntax_valid: bool
    parsing_errors: List[str]
    
    # Hallucination detection
    hallucinations: List[HallucinationDetection]
    hallucination_score: float  # 0.0 (clean) to 1.0 (heavily hallucinated)
    
    # Code quality
    quality_issues: List[CodeQualityAnalysis]
    quality_score: float  # 0.0 to 100.0
    
    # Advanced analysis (if available)
    semantic_analysis: Optional[SemanticAnalysis]
    cst_analysis: Optional[CSTAnalysis]
    
    # Integration with existing analyzer
    base_analysis: Optional[AnalysisResult]
    
    # Summary metrics
    total_issues: int
    critical_issues: int
    recommendations: List[str]

# ============================================================================
# Hallucination Detection System
# ============================================================================

class HallucinationDetector:
    """
    Comprehensive hallucination detection for AI-generated code.
    
    Detects common patterns that indicate AI has generated fictional code,
    placeholder content, or incomplete implementations.
    """
    
    def __init__(self):
        """Initialize hallucination detection patterns"""
        self.patterns = self._load_hallucination_patterns()
        self.industrial_patterns = self._load_industrial_control_patterns()
    
    def _load_hallucination_patterns(self) -> Dict[HallucinationCategory, List[Dict[str, Any]]]:
        """Load hallucination detection patterns"""
        return {
            HallucinationCategory.FAKE_IMPORTS: [
                {
                    "pattern": r"import (non_existent_module|fake_module|example_lib)",
                    "confidence": 0.9,
                    "description": "Import of non-existent module"
                },
                {
                    "pattern": r"from fictional\.|from example\.|from placeholder\.",
                    "confidence": 0.8,
                    "description": "Import from fictional package"
                }
            ],
            HallucinationCategory.PLACEHOLDER_VALUES: [
                {
                    "pattern": r"(placeholder|example|dummy|test)_\w+",
                    "confidence": 0.7,
                    "description": "Placeholder variable names"
                },
                {
                    "pattern": r"YOUR_\w+|REPLACE_\w+|INSERT_\w+",
                    "confidence": 0.9,
                    "description": "Template placeholder values"
                }
            ],
            HallucinationCategory.TODO_MARKERS: [
                {
                    "pattern": r"TODO:|FIXME:|XXX:|HACK:",
                    "confidence": 0.6,
                    "description": "TODO markers indicating incomplete code"
                },
                {
                    "pattern": r"# Implementation needed|# Not implemented",
                    "confidence": 0.8,
                    "description": "Explicit implementation markers"
                }
            ],
            HallucinationCategory.INCOMPLETE_IMPLEMENTATIONS: [
                {
                    "pattern": r"raise NotImplementedError|pass\s*$|\.\.\.|\.\.\.$",
                    "confidence": 0.7,
                    "description": "Incomplete function implementations"
                }
            ]
        }
    
    def _load_industrial_control_patterns(self) -> List[Dict[str, Any]]:
        """Load industrial control specific patterns"""
        return [
            {
                "pattern": r"fictional_plc|example_controller|dummy_pid",
                "confidence": 0.8,
                "description": "Fictional industrial control components"
            },
            {
                "pattern": r"perfect_tuning|ideal_response|magic_algorithm",
                "confidence": 0.9,
                "description": "Unrealistic control algorithm claims"
            }
        ]
    
    def detect_hallucinations(self, content: str, file_path: str) -> List[HallucinationDetection]:
        """Detect hallucinations in code content"""
        hallucinations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check each category of hallucination patterns
            for category, patterns in self.patterns.items():
                for pattern_info in patterns:
                    pattern = pattern_info["pattern"]
                    confidence = pattern_info["confidence"]
                    description = pattern_info["description"]
                    
                    if re.search(pattern, line_stripped, re.IGNORECASE):
                        hallucination = HallucinationDetection(
                            category=category,
                            line_number=line_num,
                            column=line.find(line_stripped) + 1,
                            description=description,
                            evidence=line_stripped,
                            confidence=confidence,
                            suggestion=self._generate_suggestion(category, line_stripped),
                            severity=self._determine_severity(confidence)
                        )
                        hallucinations.append(hallucination)
        
        return hallucinations
    
    def _generate_suggestion(self, category: HallucinationCategory, evidence: str) -> str:
        """Generate improvement suggestions for detected hallucinations"""
        suggestions = {
            HallucinationCategory.FAKE_IMPORTS: "Replace with actual library imports or remove if unnecessary",
            HallucinationCategory.PLACEHOLDER_VALUES: "Replace placeholder with actual implementation",
            HallucinationCategory.TODO_MARKERS: "Complete the implementation or remove TODO marker",
            HallucinationCategory.INCOMPLETE_IMPLEMENTATIONS: "Implement the function logic"
        }
        return suggestions.get(category, "Review and complete the implementation")
    
    def _determine_severity(self, confidence: float) -> str:
        """Determine severity based on confidence score"""
        if confidence >= 0.9:
            return "critical"
        elif confidence >= 0.7:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        else:
            return "low"

# ============================================================================
# Code Quality Analyzer
# ============================================================================

class AdvancedCodeQualityAnalyzer:
    """
    Advanced code quality analysis with industrial control domain expertise.
    """
    
    def __init__(self):
        """Initialize code quality analyzer"""
        self.quality_rules = self._load_quality_rules()
        self.industrial_rules = self._load_industrial_control_rules()
    
    def _load_quality_rules(self) -> Dict[CodeQualityIssue, List[Dict[str, Any]]]:
        """Load code quality analysis rules"""
        return {
            CodeQualityIssue.COMPLEXITY_HIGH: [
                {
                    "threshold": 10,
                    "description": "Function complexity exceeds recommended threshold",
                    "recommendation": "Break down into smaller functions"
                }
            ],
            CodeQualityIssue.UNUSED_IMPORTS: [
                {
                    "pattern": r"^import\s+(\w+)(?:\s+as\s+\w+)?$",
                    "description": "Potentially unused import detected",
                    "recommendation": "Remove unused imports to improve clarity"
                }
            ],
            CodeQualityIssue.INCONSISTENT_NAMING: [
                {
                    "pattern": r"[A-Z][a-z]+[A-Z]",  # CamelCase in Python
                    "description": "Inconsistent naming convention (should use snake_case)",
                    "recommendation": "Use snake_case for Python variables and functions"
                }
            ]
        }
    
    def _load_industrial_control_rules(self) -> List[Dict[str, Any]]:
        """Load industrial control specific quality rules"""
        return [
            {
                "pattern": r"pid_\w+|controller_\w+",
                "rule": "Industrial control variables should have descriptive names",
                "recommendation": "Use descriptive names like 'temperature_controller' instead of 'pid_1'"
            },
            {
                "pattern": r"setpoint|process_variable|control_output",
                "rule": "Control variables should include units in comments",
                "recommendation": "Add unit information for control variables"
            }
        ]
    
    def analyze_quality(self, content: str, file_path: str) -> List[CodeQualityAnalysis]:
        """Analyze code quality issues"""
        quality_issues = []
        lines = content.split('\n')
        
        # AST-based analysis for complexity
        try:
            tree = ast.parse(content)
            complexity_issues = self._analyze_complexity(tree, lines)
            quality_issues.extend(complexity_issues)
        except SyntaxError:
            pass  # Skip complexity analysis for invalid syntax
        
        # Pattern-based analysis
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            for issue_type, rules in self.quality_rules.items():
                for rule in rules:
                    if "pattern" in rule and re.search(rule["pattern"], line_stripped):
                        issue = CodeQualityAnalysis(
                            issue_type=issue_type,
                            line_number=line_num,
                            description=rule["description"],
                            impact="medium",
                            recommendation=rule["recommendation"],
                            affected_code=line_stripped,
                            estimated_fix_time="5-10 minutes"
                        )
                        quality_issues.append(issue)
        
        return quality_issues
    
    def _analyze_complexity(self, tree: ast.AST, lines: List[str]) -> List[CodeQualityAnalysis]:
        """Analyze code complexity using AST"""
        complexity_issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, astroid.FunctionDef)):
                complexity = self._calculate_complexity(node)
                if complexity > 10:  # Threshold
                    issue = CodeQualityAnalysis(
                        issue_type=CodeQualityIssue.COMPLEXITY_HIGH,
                        line_number=node.lineno,
                        description=f"Function '{node.name}' has high complexity: {complexity}",
                        impact="high",
                        recommendation="Break down into smaller, more focused functions",
                        affected_code=f"def {node.name}(...)",
                        estimated_fix_time="30-60 minutes"
                    )
                    complexity_issues.append(issue)
        
        return complexity_issues
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                                ast.With, ast.Assert, ast.Comprehension)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

# ============================================================================
# Semantic Analyzer
# ============================================================================

class SemanticAnalyzer:
    """
    Semantic analysis using astroid for advanced type inference and analysis.
    """
    
    def __init__(self):
        """Initialize semantic analyzer"""
        if ASTROID_AVAILABLE:
            self.manager = astroid.manager.AstroidManager()
        else:
            self.manager = None
    
    def analyze(self, content: str, file_path: str) -> Optional[SemanticAnalysis]:
        """Perform semantic analysis using astroid"""
        if not ASTROID_AVAILABLE:
            return None
        
        try:
            module = astroid.parse(content, modname=Path(file_path).stem)
            
            # Collect semantic information
            defined_names = self._extract_defined_names(module)
            used_names = self._extract_used_names(module)
            undefined_names = self._find_undefined_names(defined_names, used_names)
            type_inferences = self._perform_type_inference(module)
            call_graph = self._build_call_graph(module)
            inheritance_hierarchy = self._extract_inheritance(module)
            complexity_metrics = self._calculate_semantic_complexity(module)
            
            return SemanticAnalysis(
                defined_names=defined_names,
                used_names=used_names,
                undefined_names=undefined_names,
                type_inferences=type_inferences,
                call_graph=call_graph,
                inheritance_hierarchy=inheritance_hierarchy,
                complexity_metrics=complexity_metrics
            )
            
        except (AstroidError, Exception) as e:
            logger.warning(f"Semantic analysis failed for {file_path}: {str(e)}")
            return None
    
    def _extract_defined_names(self, module: astroid.Module) -> List[str]:
        """Extract all defined names in the module"""
        defined_names = []
        
        for node in module.nodes_of_class((astroid.FunctionDef, astroid.ClassDef, 
                                         astroid.Assign, astroid.Import, astroid.ImportFrom)):
            if isinstance(node, (astroid.FunctionDef, astroid.ClassDef)):
                defined_names.append(node.name)
            elif isinstance(node, astroid.Assign):
                for target in node.targets:
                    if isinstance(target, astroid.AssignName):
                        defined_names.append(target.name)
        
        return defined_names
    
    def _extract_used_names(self, module: astroid.Module) -> List[str]:
        """Extract all used names in the module"""
        used_names = []
        
        for node in module.nodes_of_class(astroid.Name):
            if isinstance(node.ctx, astroid.Load):
                used_names.append(node.name)
        
        return list(set(used_names))
    
    def _find_undefined_names(self, defined_names: List[str], used_names: List[str]) -> List[str]:
        """Find names that are used but not defined"""
        # Filter out built-in names
        builtins = set(dir(__builtins__))
        undefined = []
        
        for name in used_names:
            if name not in defined_names and name not in builtins:
                undefined.append(name)
        
        return undefined
    
    def _perform_type_inference(self, module: astroid.Module) -> Dict[str, str]:
        """Perform type inference on module elements"""
        type_inferences = {}
        
        for node in module.nodes_of_class((astroid.FunctionDef, astroid.Assign)):
            try:
                if isinstance(node, astroid.FunctionDef):
                    # Infer return type
                    inferred = list(node.infer_call_result(caller=None, context=None))
                    if inferred:
                        type_inferences[node.name] = str(inferred[0])
                elif isinstance(node, astroid.Assign):
                    # Infer variable type
                    for target in node.targets:
                        if isinstance(target, astroid.AssignName):
                            inferred = list(node.value.infer())
                            if inferred:
                                type_inferences[target.name] = str(inferred[0])
            except (InferenceError, Exception):
                continue
        
        return type_inferences
    
    def _build_call_graph(self, module: astroid.Module) -> Dict[str, List[str]]:
        """Build call graph showing function dependencies"""
        call_graph = {}
        
        for func in module.nodes_of_class(astroid.FunctionDef):
            calls = []
            for call in func.nodes_of_class(astroid.Call):
                if isinstance(call.func, astroid.Name):
                    calls.append(call.func.name)
            call_graph[func.name] = calls
        
        return call_graph
    
    def _extract_inheritance(self, module: astroid.Module) -> Dict[str, List[str]]:
        """Extract class inheritance hierarchy"""
        inheritance = {}
        
        for cls in module.nodes_of_class(astroid.ClassDef):
            bases = []
            for base in cls.bases:
                if isinstance(base, astroid.Name):
                    bases.append(base.name)
            inheritance[cls.name] = bases
        
        return inheritance
    
    def _calculate_semantic_complexity(self, module: astroid.Module) -> Dict[str, float]:
        """Calculate semantic complexity metrics"""
        metrics = {}
        
        # Function complexity
        for func in module.nodes_of_class(astroid.FunctionDef):
            complexity = len(list(func.nodes_of_class((astroid.If, astroid.While, astroid.For))))
            metrics[f"{func.name}_complexity"] = complexity
        
        # Module complexity
        total_functions = len(list(module.nodes_of_class(astroid.FunctionDef)))
        total_classes = len(list(module.nodes_of_class(astroid.ClassDef)))
        metrics["module_complexity"] = total_functions + total_classes * 2
        
        return metrics

# ============================================================================
# CST Analyzer
# ============================================================================

class CSTAnalyzer:
    """
    Concrete Syntax Tree analysis using libcst for precise code modification.
    """
    
    def __init__(self):
        """Initialize CST analyzer"""
        self.format_rules = self._load_format_rules()
    
    def _load_format_rules(self) -> Dict[str, Any]:
        """Load formatting and style rules"""
        return {
            "max_line_length": 88,
            "indent_size": 4,
            "require_docstrings": True,
            "trailing_whitespace": False
        }
    
    def analyze(self, content: str, file_path: str) -> Optional[CSTAnalysis]:
        """Perform CST analysis using libcst"""
        if not LIBCST_AVAILABLE:
            return None
        
        try:
            tree = cst.parse_expression(content) if len(content.split('\n')) == 1 else cst.parse_module(content)
            
            format_violations = self._check_format_violations(content)
            whitespace_issues = self._check_whitespace_issues(content)
            comment_analysis = self._analyze_comments(content)
            docstring_coverage = self._calculate_docstring_coverage(tree)
            modification_suggestions = self._generate_modification_suggestions(tree, content)
            code_style_score = self._calculate_style_score(content)
            
            return CSTAnalysis(
                format_violations=format_violations,
                whitespace_issues=whitespace_issues,
                comment_analysis=comment_analysis,
                docstring_coverage=docstring_coverage,
                modification_suggestions=modification_suggestions,
                code_style_score=code_style_score
            )
            
        except Exception as e:
            logger.warning(f"CST analysis failed for {file_path}: {str(e)}")
            return None
    
    def _check_format_violations(self, content: str) -> List[str]:
        """Check for formatting violations"""
        violations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if len(line) > self.format_rules["max_line_length"]:
                violations.append(f"Line {line_num}: Exceeds maximum length ({len(line)} > {self.format_rules['max_line_length']})")
            
            if line.endswith(' ') or line.endswith('\t'):
                violations.append(f"Line {line_num}: Trailing whitespace detected")
        
        return violations
    
    def _check_whitespace_issues(self, content: str) -> List[str]:
        """Check for whitespace issues"""
        issues = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if '\t' in line:
                issues.append(f"Line {line_num}: Tab character found (use spaces)")
            
            leading_spaces = len(line) - len(line.lstrip(' '))
            if leading_spaces % self.format_rules["indent_size"] != 0:
                issues.append(f"Line {line_num}: Inconsistent indentation")
        
        return issues
    
    def _analyze_comments(self, content: str) -> Dict[str, Any]:
        """Analyze comments in the code"""
        lines = content.split('\n')
        comment_lines = [i for i, line in enumerate(lines) if line.strip().startswith('#')]
        
        return {
            "total_comments": len(comment_lines),
            "comment_ratio": len(comment_lines) / len(lines) if lines else 0,
            "comment_lines": comment_lines
        }
    
    def _calculate_docstring_coverage(self, tree: cst.CSTNode) -> float:
        """Calculate docstring coverage percentage"""
        if not LIBCST_AVAILABLE:
            return 0.0
        
        # This is a simplified calculation - would need more sophisticated CST traversal
        # for production use
        return 0.75  # Placeholder
    
    def _generate_modification_suggestions(self, tree: cst.CSTNode, content: str) -> List[str]:
        """Generate suggestions for code modifications"""
        suggestions = []
        
        # Analyze content for common improvements
        if "print(" in content:
            suggestions.append("Consider using logging instead of print statements")
        
        if "except:" in content:
            suggestions.append("Use specific exception types instead of bare except")
        
        return suggestions
    
    def _calculate_style_score(self, content: str) -> float:
        """Calculate overall code style score"""
        score = 100.0
        lines = content.split('\n')
        
        # Deduct points for various style issues
        for line in lines:
            if len(line) > self.format_rules["max_line_length"]:
                score -= 1
            if line.endswith(' '):
                score -= 0.5
            if '\t' in line:
                score -= 0.5
        
        return max(0.0, score)

# ============================================================================
# Enhanced Code Analyzer
# ============================================================================

class EnhancedCodeAnalyzer:
    """
    Enhanced code analyzer integrating advanced static analysis capabilities
    with the existing ai-enhancement-framework infrastructure.
    """
    
    def __init__(self, analysis_level: AnalysisLevel = AnalysisLevel.COMPREHENSIVE):
        """Initialize the enhanced code analyzer"""
        self.analysis_level = analysis_level
        self.session_id = f"enhanced_analysis_{int(time.time())}"
        self.start_time = datetime.now()
        
        # Analysis capabilities
        self.capabilities = {
            'libcst_available': LIBCST_AVAILABLE,
            'astroid_available': ASTROID_AVAILABLE,
            'existing_analyzer': EXISTING_ANALYZER_AVAILABLE
        }
        
        # Initialize analyzers
        self.hallucination_detector = HallucinationDetector()
        self.quality_analyzer = AdvancedCodeQualityAnalyzer()
        
        if ASTROID_AVAILABLE:
            self.semantic_analyzer = SemanticAnalyzer()
        else:
            self.semantic_analyzer = None
            
        if LIBCST_AVAILABLE:
            self.cst_analyzer = CSTAnalyzer()
        else:
            self.cst_analyzer = None
            
        # Integration with existing analyzer
        if EXISTING_ANALYZER_AVAILABLE:
            self.base_analyzer = CodeAnalyzer()
        else:
            self.base_analyzer = None
        
        # Industrial control domain patterns
        self.control_patterns = self._load_control_domain_patterns()
        
        logger.info(f"EnhancedCodeAnalyzer initialized with capabilities: {self.capabilities}")
    
    def _load_control_domain_patterns(self) -> Dict[str, List[str]]:
        """Load industrial control domain-specific patterns"""
        return {
            "pid_patterns": [
                r"kp|ki|kd|proportional|integral|derivative",
                r"setpoint|process_variable|control_output|error",
                r"pid_controller|pid_tuning|pid_parameters"
            ],
            "safety_patterns": [
                r"safety_interlock|emergency_stop|fail_safe",
                r"alarm|fault|error_handling|redundancy"
            ],
            "optimization_patterns": [
                r"objective_function|constraint|optimization",
                r"minimize|maximize|optimal|efficiency"
            ]
        }
    
    def analyze_file(self, file_path: str, content: Optional[str] = None) -> EnhancedAnalysisResult:
        """Perform comprehensive enhanced analysis of a single file"""
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                logger.error(f"Error reading file {file_path}: {str(e)}")
                return self._create_error_result(file_path, str(e))
        
        result = EnhancedAnalysisResult(
            file_path=file_path,
            analysis_timestamp=datetime.now(),
            analysis_level=self.analysis_level,
            syntax_valid=False,
            parsing_errors=[],
            hallucinations=[],
            hallucination_score=0.0,
            quality_issues=[],
            quality_score=0.0,
            semantic_analysis=None,
            cst_analysis=None,
            base_analysis=None,
            total_issues=0,
            critical_issues=0,
            recommendations=[]
        )
        
        # Step 1: Basic syntax validation
        result.syntax_valid, result.parsing_errors = self._validate_syntax(content)
        
        # Step 2: Hallucination detection
        if result.syntax_valid:
            result.hallucinations = self.hallucination_detector.detect_hallucinations(content, file_path)
            result.hallucination_score = self._calculate_hallucination_score(result.hallucinations)
        
        # Step 3: Code quality analysis
        result.quality_issues = self.quality_analyzer.analyze_quality(content, file_path)
        result.quality_score = self._calculate_quality_score(result.quality_issues)
        
        # Step 4: Advanced analysis (if capabilities available)
        if self.analysis_level in [AnalysisLevel.SEMANTIC, AnalysisLevel.COMPREHENSIVE]:
            if self.semantic_analyzer and result.syntax_valid:
                result.semantic_analysis = self.semantic_analyzer.analyze(content, file_path)
        
        if self.analysis_level == AnalysisLevel.COMPREHENSIVE:
            if self.cst_analyzer and result.syntax_valid:
                result.cst_analysis = self.cst_analyzer.analyze(content, file_path)
        
        # Step 5: Integration with existing analyzer
        if self.base_analyzer and result.syntax_valid:
            try:
                base_result = self.base_analyzer.analyze_file(file_path, content)
                result.base_analysis = base_result
            except Exception as e:
                logger.warning(f"Base analyzer integration failed: {e}")
        
        # Step 6: Generate summary and recommendations
        result.total_issues = len(result.hallucinations) + len(result.quality_issues)
        result.critical_issues = len([h for h in result.hallucinations if h.severity == "critical"]) + \
                                len([q for q in result.quality_issues if q.impact == "high"])
        result.recommendations = self._generate_recommendations(result)
        
        logger.info(f"Enhanced analysis completed for {file_path}: {result.total_issues} issues found")
        return result
    
    def analyze_codebase(self, root_path: str, file_patterns: List[str] = None) -> Dict[str, EnhancedAnalysisResult]:
        """Analyze entire codebase with enhanced static analysis"""
        if file_patterns is None:
            file_patterns = ["*.py"]
        
        results = {}
        root = Path(root_path)
        
        # Find all files matching patterns
        files_to_analyze = []
        for pattern in file_patterns:
            files_to_analyze.extend(root.rglob(pattern))
        
        logger.info(f"Analyzing {len(files_to_analyze)} files in codebase")
        
        for file_path in files_to_analyze:
            try:
                result = self.analyze_file(str(file_path))
                results[str(file_path)] = result
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {str(e)}")
                results[str(file_path)] = self._create_error_result(str(file_path), str(e))
        
        return results
    
    def _validate_syntax(self, content: str) -> Tuple[bool, List[str]]:
        """Validate Python syntax"""
        try:
            ast.parse(content)
            return True, []
        except SyntaxError as e:
            return False, [f"Syntax error at line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [f"Parsing error: {str(e)}"]
    
    def _calculate_hallucination_score(self, hallucinations: List[HallucinationDetection]) -> float:
        """Calculate overall hallucination score"""
        if not hallucinations:
            return 0.0
        
        total_confidence = sum(h.confidence for h in hallucinations)
        return min(1.0, total_confidence / len(hallucinations))
    
    def _calculate_quality_score(self, quality_issues: List[CodeQualityAnalysis]) -> float:
        """Calculate overall quality score"""
        base_score = 100.0
        
        for issue in quality_issues:
            if issue.impact == "high":
                base_score -= 10
            elif issue.impact == "medium":
                base_score -= 5
            else:
                base_score -= 2
        
        return max(0.0, base_score)
    
    def _generate_recommendations(self, result: EnhancedAnalysisResult) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        
        # Hallucination recommendations
        critical_hallucinations = [h for h in result.hallucinations if h.severity == "critical"]
        if critical_hallucinations:
            recommendations.append(f"Address {len(critical_hallucinations)} critical hallucination(s) immediately")
        
        # Quality recommendations
        high_impact_issues = [q for q in result.quality_issues if q.impact == "high"]
        if high_impact_issues:
            recommendations.append(f"Fix {len(high_impact_issues)} high-impact quality issue(s)")
        
        # Complexity recommendations
        if result.base_analysis:
            complexity = getattr(result.base_analysis, 'complexity', None)
            if complexity and complexity > 10:
                recommendations.append("Consider refactoring to reduce complexity")
        
        # General recommendations
        if result.hallucination_score > 0.5:
            recommendations.append("High hallucination score detected - review AI-generated code carefully")
        
        if result.quality_score < 70:
            recommendations.append("Code quality below threshold - consider comprehensive refactoring")
        
        return recommendations
    
    def _create_error_result(self, file_path: str, error_message: str) -> EnhancedAnalysisResult:
        """Create an error result for failed analysis"""
        return EnhancedAnalysisResult(
            file_path=file_path,
            analysis_timestamp=datetime.now(),
            analysis_level=self.analysis_level,
            syntax_valid=False,
            parsing_errors=[error_message],
            hallucinations=[],
            hallucination_score=0.0,
            quality_issues=[],
            quality_score=0.0,
            semantic_analysis=None,
            cst_analysis=None,
            base_analysis=None,
            total_issues=1,
            critical_issues=1,
            recommendations=["Fix parsing errors before proceeding with analysis"]
        )
    
    def generate_analysis_report(self, results: Dict[str, EnhancedAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        total_files = len(results)
        syntax_errors = sum(1 for r in results.values() if not r.syntax_valid)
        total_hallucinations = sum(len(r.hallucinations) for r in results.values())
        total_quality_issues = sum(len(r.quality_issues) for r in results.values())
        avg_quality_score = sum(r.quality_score for r in results.values()) / total_files if total_files else 0
        
        report = {
            "analysis_summary": {
                "total_files": total_files,
                "syntax_errors": syntax_errors,
                "total_hallucinations": total_hallucinations,
                "total_quality_issues": total_quality_issues,
                "average_quality_score": avg_quality_score,
                "analysis_timestamp": datetime.now().isoformat()
            },
            "capabilities": self.capabilities,
            "recommendations": self._generate_codebase_recommendations(results),
            "detailed_results": {path: asdict(result) for path, result in results.items()}
        }
        
        return report
    
    def _generate_codebase_recommendations(self, results: Dict[str, EnhancedAnalysisResult]) -> List[str]:
        """Generate codebase-level recommendations"""
        recommendations = []
        
        # Syntax issues
        syntax_issues = sum(1 for r in results.values() if not r.syntax_valid)
        if syntax_issues > 0:
            recommendations.append(f"Fix {syntax_issues} file(s) with syntax errors")
        
        # Hallucination patterns
        hallucination_files = sum(1 for r in results.values() if r.hallucination_score > 0.3)
        if hallucination_files > len(results) * 0.1:  # More than 10% of files
            recommendations.append("High proportion of files contain hallucinations - review AI-generated code")
        
        # Quality patterns
        low_quality_files = sum(1 for r in results.values() if r.quality_score < 70)
        if low_quality_files > len(results) * 0.2:  # More than 20% of files
            recommendations.append("Implement code quality standards and refactoring plan")
        
        return recommendations 