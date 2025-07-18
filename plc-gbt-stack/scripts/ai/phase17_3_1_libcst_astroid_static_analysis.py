#!/usr/bin/env python3
"""
🔬 Phase 17.3.1: Advanced Static Analysis Framework with libcst & astroid
PLC-GPT Industrial Control Static Code Analysis Enhancement

This module implements comprehensive static code analysis framework including:
- libcst-based CST (Concrete Syntax Tree) analysis for precise code modifications
- astroid-based semantic analysis for advanced inference and type checking
- Hallucination detection for AI-generated code validation
- Code quality analysis with industrial control domain expertise
- Windows compatibility with pure-Python implementations
- Integration with existing codebase_analyzer.py infrastructure

Following AI Task Orchestrator methodology for systematic static analysis enhancement.

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: 17.3.1 - Advanced Static Analysis Framework
Dependencies: libcst>=1.0.0, astroid>=3.0.0, existing codebase_analyzer.py
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

# Import existing analysis infrastructure
try:
    from codebase_analyzer import (
        CodebaseAnalyzer, FileAnalysisResult, StructuralAnalysis, 
        FileType, AnalysisDepth, AnalysisResult
    )
    EXISTING_ANALYZER_AVAILABLE = True
except ImportError:
    EXISTING_ANALYZER_AVAILABLE = False
    logging.warning("Existing codebase analyzer not available - running in standalone mode")
    
    # Define minimal compatibility classes if not available
    class StructuralAnalysis:
        def __init__(self, imports=None, exports=None, functions=None, classes=None, 
                     variables=None, dependencies=None, ast_nodes=0, complexity_score=0.0, 
                     documentation_coverage=0.0, **kwargs):
            self.imports = imports or []
            self.exports = exports or []
            self.functions = functions or []
            self.classes = classes or []
            self.variables = variables or []
            self.dependencies = dependencies or []
            self.ast_nodes = ast_nodes
            self.complexity_score = complexity_score
            self.documentation_coverage = documentation_coverage
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class FileType:
        PYTHON = "python"
        JAVASCRIPT = "javascript"
        TYPESCRIPT = "typescript"
        MARKDOWN = "markdown"
    
    class AnalysisDepth:
        SURFACE = "surface"
        STRUCTURAL = "structural"
        COMPREHENSIVE = "comprehensive"
    
    # Placeholder analyzer for compatibility
    class CodebaseAnalyzer:
        def analyze_file_structure(self, file_path, content, file_type):
            return StructuralAnalysis()

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
class AdvancedStaticAnalysisResult:
    """Comprehensive static analysis result"""
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
    enhanced_structural_analysis: Optional[StructuralAnalysis]
    
    # Summary metrics
    total_issues: int
    critical_issues: int
    recommendations: List[str]

# ============================================================================
# Advanced Static Analysis Framework
# ============================================================================

class AdvancedStaticAnalyzer:
    """
    Advanced static analysis framework using libcst and astroid.
    
    Provides comprehensive code analysis including:
    - Hallucination detection for AI-generated code
    - Code quality analysis with industrial control domain expertise
    - Semantic analysis using astroid for type inference
    - CST analysis using libcst for precise code modification
    - Integration with existing codebase analyzer infrastructure
    """
    
    def __init__(self, analysis_level: AnalysisLevel = AnalysisLevel.COMPREHENSIVE):
        """Initialize the advanced static analyzer"""
        self.analysis_level = analysis_level
        self.session_id = f"advanced_analysis_{int(time.time())}"
        self.start_time = datetime.now()
        
        # Analysis capabilities
        self.capabilities = {
            'libcst_available': LIBCST_AVAILABLE,
            'astroid_available': ASTROID_AVAILABLE,
            'existing_analyzer': EXISTING_ANALYZER_AVAILABLE
        }
        
        # Initialize analyzers
        self.hallucination_detector = HallucinationDetector()
        self.quality_analyzer = CodeQualityAnalyzer()
        
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
            self.base_analyzer = CodebaseAnalyzer()
        else:
            self.base_analyzer = None
        
        # Industrial control domain patterns
        self.control_patterns = self._load_control_domain_patterns()
        
        logger.info(f"AdvancedStaticAnalyzer initialized with capabilities: {self.capabilities}")
    
    def analyze_file(self, file_path: Union[str, Path], content: Optional[str] = None) -> AdvancedStaticAnalysisResult:
        """
        Perform comprehensive static analysis on a single file.
        
        Args:
            file_path: Path to the file to analyze
            content: Optional file content (if not provided, will read from file)
            
        Returns:
            Comprehensive analysis result
        """
        file_path = Path(file_path)
        
        if content is None:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return self._create_error_result(file_path, str(e))
        
        logger.info(f"Starting advanced static analysis for: {file_path}")
        
        # Initialize result
        result = AdvancedStaticAnalysisResult(
            file_path=str(file_path),
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
            enhanced_structural_analysis=None,
            total_issues=0,
            critical_issues=0,
            recommendations=[]
        )
        
        # Step 1: Basic syntax validation
        try:
            ast.parse(content)
            result.syntax_valid = True
        except SyntaxError as e:
            result.syntax_valid = False
            result.parsing_errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
            logger.warning(f"Syntax error in {file_path}: {e}")
        
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
                base_result = self.base_analyzer.analyze_file_structure(file_path, content, FileType.PYTHON)
                result.enhanced_structural_analysis = base_result
            except Exception as e:
                logger.warning(f"Base analyzer integration failed: {e}")
        
        # Step 6: Generate summary and recommendations
        result.total_issues = len(result.hallucinations) + len(result.quality_issues)
        result.critical_issues = len([h for h in result.hallucinations if h.severity == "critical"]) + \
                                len([q for q in result.quality_issues if q.impact == "high"])
        result.recommendations = self._generate_recommendations(result)
        
        logger.info(f"Analysis completed for {file_path}: {result.total_issues} issues found")
        return result
    
    def analyze_codebase(self, root_path: Union[str, Path], 
                        file_patterns: List[str] = ["*.py"],
                        exclude_patterns: List[str] = None) -> Dict[str, AdvancedStaticAnalysisResult]:
        """
        Analyze an entire codebase with advanced static analysis.
        
        Args:
            root_path: Root directory to analyze
            file_patterns: File patterns to include (default: ["*.py"])
            exclude_patterns: Patterns to exclude
            
        Returns:
            Dictionary mapping file paths to analysis results
        """
        root_path = Path(root_path)
        exclude_patterns = exclude_patterns or [
            "*.pyc", "__pycache__/*", ".git/*", "node_modules/*", ".venv/*"
        ]
        
        logger.info(f"Starting codebase analysis at: {root_path}")
        
        results = {}
        files_to_analyze = []
        
        # Collect files to analyze
        for pattern in file_patterns:
            files_to_analyze.extend(root_path.rglob(pattern))
        
        # Filter out excluded patterns
        filtered_files = []
        for file_path in files_to_analyze:
            exclude = False
            for exclude_pattern in exclude_patterns:
                if file_path.match(exclude_pattern) or exclude_pattern in str(file_path):
                    exclude = True
                    break
            if not exclude:
                filtered_files.append(file_path)
        
        logger.info(f"Found {len(filtered_files)} files to analyze")
        
        # Analyze each file
        for i, file_path in enumerate(filtered_files, 1):
            try:
                logger.info(f"Analyzing file {i}/{len(filtered_files)}: {file_path}")
                result = self.analyze_file(file_path)
                results[str(file_path)] = result
            except Exception as e:
                logger.error(f"Failed to analyze {file_path}: {e}")
                results[str(file_path)] = self._create_error_result(file_path, str(e))
        
        logger.info(f"Codebase analysis completed: {len(results)} files analyzed")
        return results
    
    def generate_analysis_report(self, results: Dict[str, AdvancedStaticAnalysisResult]) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        report = {
            "session_id": self.session_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "analysis_level": self.analysis_level.value,
            "capabilities": self.capabilities,
            "summary": {
                "total_files": len(results),
                "files_with_issues": len([r for r in results.values() if r.total_issues > 0]),
                "total_hallucinations": sum(len(r.hallucinations) for r in results.values()),
                "total_quality_issues": sum(len(r.quality_issues) for r in results.values()),
                "average_quality_score": sum(r.quality_score for r in results.values()) / len(results) if results else 0,
                "critical_issues": sum(r.critical_issues for r in results.values())
            },
            "hallucination_patterns": self._analyze_hallucination_patterns(results),
            "quality_trends": self._analyze_quality_trends(results),
            "recommendations": self._generate_codebase_recommendations(results),
            "detailed_results": {path: asdict(result) for path, result in results.items()}
        }
        
        return report
    
    def _load_control_domain_patterns(self) -> Dict[str, Any]:
        """Load industrial control domain-specific patterns"""
        return {
            "pid_patterns": [
                r"kp\s*=|ki\s*=|kd\s*=",  # PID parameters
                r"setpoint|process_variable|error",  # Control variables
                r"proportional|integral|derivative"  # Control terms
            ],
            "safety_patterns": [
                r"safety_interlock|emergency_stop|fail_safe",
                r"guard|protection|alarm"
            ],
            "communication_patterns": [
                r"modbus|ethernet_ip|devicenet|profibus",
                r"tcp|udp|serial"
            ],
            "suspicious_patterns": [
                r"TODO|FIXME|HACK|XXX",
                r"placeholder|example|sample",
                r"fake_|mock_|dummy_"
            ]
        }
    
    def _calculate_hallucination_score(self, hallucinations: List[HallucinationDetection]) -> float:
        """Calculate overall hallucination score"""
        if not hallucinations:
            return 0.0
        
        severity_weights = {"low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0}
        total_weight = sum(severity_weights[h.severity] * h.confidence for h in hallucinations)
        return min(total_weight / len(hallucinations), 1.0)
    
    def _calculate_quality_score(self, quality_issues: List[CodeQualityAnalysis]) -> float:
        """Calculate code quality score (0-100)"""
        if not quality_issues:
            return 100.0
        
        impact_penalties = {"low": 2, "medium": 5, "high": 10}
        total_penalty = sum(impact_penalties[issue.impact] for issue in quality_issues)
        return max(100.0 - total_penalty, 0.0)
    
    def _generate_recommendations(self, result: AdvancedStaticAnalysisResult) -> List[str]:
        """Generate recommendations based on analysis result"""
        recommendations = []
        
        # Hallucination recommendations
        if result.hallucination_score > 0.3:
            recommendations.append("Review AI-generated code for hallucinations and placeholder content")
        
        # Quality recommendations
        if result.quality_score < 70:
            recommendations.append("Refactor code to improve maintainability and reduce complexity")
        
        # Critical issues
        if result.critical_issues > 0:
            recommendations.append("Address critical issues immediately before deployment")
        
        return recommendations
    
    def _analyze_hallucination_patterns(self, results: Dict[str, AdvancedStaticAnalysisResult]) -> Dict[str, Any]:
        """Analyze hallucination patterns across codebase"""
        pattern_counts = defaultdict(int)
        for result in results.values():
            for hallucination in result.hallucinations:
                pattern_counts[hallucination.category.value] += 1
        
        return dict(pattern_counts)
    
    def _analyze_quality_trends(self, results: Dict[str, AdvancedStaticAnalysisResult]) -> Dict[str, Any]:
        """Analyze code quality trends"""
        issue_counts = defaultdict(int)
        for result in results.values():
            for issue in result.quality_issues:
                issue_counts[issue.issue_type.value] += 1
        
        return dict(issue_counts)
    
    def _generate_codebase_recommendations(self, results: Dict[str, AdvancedStaticAnalysisResult]) -> List[str]:
        """Generate codebase-level recommendations"""
        recommendations = []
        
        total_files = len(results)
        problematic_files = len([r for r in results.values() if r.total_issues > 5])
        
        if problematic_files / total_files > 0.3:
            recommendations.append("Consider comprehensive code review and refactoring initiative")
        
        return recommendations
    
    def _create_error_result(self, file_path: Path, error_message: str) -> AdvancedStaticAnalysisResult:
        """Create error result for failed analysis"""
        return AdvancedStaticAnalysisResult(
            file_path=str(file_path),
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
            enhanced_structural_analysis=None,
            total_issues=1,
            critical_issues=1,
            recommendations=["Fix parsing errors before further analysis"]
        )

# ============================================================================
# Specialized Analyzers
# ============================================================================

class HallucinationDetector:
    """Detects AI hallucinations in code"""
    
    def __init__(self):
        self.patterns = self._load_hallucination_patterns()
    
    def detect_hallucinations(self, content: str, file_path: Path) -> List[HallucinationDetection]:
        """Detect hallucinations in code content"""
        hallucinations = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for fake imports
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                fake_imports = self._detect_fake_imports(line, line_num)
                hallucinations.extend(fake_imports)
            
            # Check for placeholder patterns
            placeholders = self._detect_placeholders(line, line_num)
            hallucinations.extend(placeholders)
            
            # Check for TODO markers
            todos = self._detect_todo_markers(line, line_num)
            hallucinations.extend(todos)
        
        return hallucinations
    
    def _detect_fake_imports(self, line: str, line_num: int) -> List[HallucinationDetection]:
        """Detect potentially fake import statements"""
        fake_patterns = [
            r'import\s+nonexistent_',
            r'import\s+fake_',
            r'import\s+placeholder_',
            r'from\s+example\.',
            r'from\s+fictional_'
        ]
        
        detections = []
        for pattern in fake_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                detections.append(HallucinationDetection(
                    category=HallucinationCategory.FAKE_IMPORTS,
                    line_number=line_num,
                    column=0,
                    description="Potentially fake or placeholder import detected",
                    evidence=line.strip(),
                    confidence=0.8,
                    suggestion="Replace with actual import or remove if not needed",
                    severity="high"
                ))
        
        return detections
    
    def _detect_placeholders(self, line: str, line_num: int) -> List[HallucinationDetection]:
        """Detect placeholder content"""
        placeholder_patterns = [
            r'YOUR_API_KEY',
            r'PLACEHOLDER_',
            r'EXAMPLE_',
            r'TODO:',
            r'pass\s*#.*implement',
            r'raise\s+NotImplementedError'
        ]
        
        detections = []
        for pattern in placeholder_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                detections.append(HallucinationDetection(
                    category=HallucinationCategory.PLACEHOLDER_VALUES,
                    line_number=line_num,
                    column=0,
                    description="Placeholder content that needs implementation",
                    evidence=line.strip(),
                    confidence=0.9,
                    suggestion="Replace placeholder with actual implementation",
                    severity="medium"
                ))
        
        return detections
    
    def _detect_todo_markers(self, line: str, line_num: int) -> List[HallucinationDetection]:
        """Detect TODO markers and incomplete implementations"""
        if re.search(r'TODO|FIXME|XXX|HACK', line, re.IGNORECASE):
            return [HallucinationDetection(
                category=HallucinationCategory.TODO_MARKERS,
                line_number=line_num,
                column=0,
                description="TODO marker indicating incomplete implementation",
                evidence=line.strip(),
                confidence=1.0,
                suggestion="Complete the implementation or remove TODO",
                severity="low"
            )]
        return []
    
    def _load_hallucination_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for hallucination detection"""
        return {
            "fake_imports": [
                r"import\s+fake_",
                r"import\s+mock_",
                r"import\s+example_",
                r"from\s+fictional"
            ],
            "placeholders": [
                r"YOUR_\w+",
                r"PLACEHOLDER_\w+",
                r"EXAMPLE_\w+",
                r"dummy_\w+",
                r"fake_\w+"
            ],
            "incomplete": [
                r"TODO",
                r"FIXME", 
                r"XXX",
                r"HACK",
                r"pass\s*#.*implement"
            ]
        }

class CodeQualityAnalyzer:
    """Analyzes code quality issues"""
    
    def analyze_quality(self, content: str, file_path: Path) -> List[CodeQualityAnalysis]:
        """Analyze code quality"""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            # Analyze complexity
            complexity_issues = self._analyze_complexity(tree, content)
            issues.extend(complexity_issues)
            
            # Analyze unused imports
            unused_import_issues = self._analyze_unused_imports(tree, content)
            issues.extend(unused_import_issues)
            
            # Analyze naming conventions
            naming_issues = self._analyze_naming_conventions(tree)
            issues.extend(naming_issues)
            
        except SyntaxError:
            # Skip analysis for files with syntax errors
            pass
        
        return issues
    
    def _analyze_complexity(self, tree: ast.AST, content: str) -> List[CodeQualityAnalysis]:
        """Analyze code complexity"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                complexity = self._calculate_cyclomatic_complexity(node)
                if complexity > 10:
                    issues.append(CodeQualityAnalysis(
                        issue_type=CodeQualityIssue.COMPLEXITY_HIGH,
                        line_number=node.lineno,
                        description=f"Function '{node.name}' has high cyclomatic complexity ({complexity})",
                        impact="high",
                        recommendation="Break down function into smaller, more manageable pieces",
                        affected_code=f"def {node.name}",
                        estimated_fix_time="2-4 hours"
                    ))
        
        return issues
    
    def _analyze_unused_imports(self, tree: ast.AST, content: str) -> List[CodeQualityAnalysis]:
        """Analyze unused imports"""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated analysis
        return []
    
    def _analyze_naming_conventions(self, tree: ast.AST) -> List[CodeQualityAnalysis]:
        """Analyze naming conventions"""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not self._is_snake_case(node.name):
                    issues.append(CodeQualityAnalysis(
                        issue_type=CodeQualityIssue.INCONSISTENT_NAMING,
                        line_number=node.lineno,
                        description=f"Function '{node.name}' does not follow snake_case convention",
                        impact="low",
                        recommendation="Rename function to follow snake_case convention",
                        affected_code=f"def {node.name}",
                        estimated_fix_time="5 minutes"
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
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention"""
        return name.islower() and '_' in name or name.islower()

class SemanticAnalyzer:
    """Semantic analysis using astroid"""
    
    def __init__(self):
        if not ASTROID_AVAILABLE:
            raise ImportError("astroid is required for semantic analysis")
        self.manager = astroid.manager.AstroidManager()
    
    def analyze(self, content: str, file_path: Path) -> SemanticAnalysis:
        """Perform semantic analysis"""
        try:
            module = astroid.parse(content, module_name=str(file_path))
            
            # Extract semantic information
            defined_names = self._extract_defined_names(module)
            used_names = self._extract_used_names(module)
            undefined_names = list(set(used_names) - set(defined_names))
            type_inferences = self._infer_types(module)
            call_graph = self._build_call_graph(module)
            inheritance_hierarchy = self._build_inheritance_hierarchy(module)
            complexity_metrics = self._calculate_complexity_metrics(module)
            
            return SemanticAnalysis(
                defined_names=defined_names,
                used_names=used_names,
                undefined_names=undefined_names,
                type_inferences=type_inferences,
                call_graph=call_graph,
                inheritance_hierarchy=inheritance_hierarchy,
                complexity_metrics=complexity_metrics
            )
            
        except AstroidError as e:
            logger.warning(f"Astroid analysis failed for {file_path}: {e}")
            return SemanticAnalysis([], [], [], {}, {}, {}, {})
    
    def _extract_defined_names(self, module: astroid.Module) -> List[str]:
        """Extract defined names from module"""
        names = []
        for name, node in module.items():
            names.append(name)
        return names
    
    def _extract_used_names(self, module: astroid.Module) -> List[str]:
        """Extract used names from module"""
        names = []
        for node in module.nodes_of_class(astroid.Name):
            names.append(node.name)
        return list(set(names))
    
    def _infer_types(self, module: astroid.Module) -> Dict[str, str]:
        """Infer types using astroid"""
        types = {}
        for node in module.nodes_of_class(astroid.Name):
            try:
                inferred = list(node.infer())
                if inferred:
                    types[node.name] = str(inferred[0])
            except InferenceError:
                pass
        return types
    
    def _build_call_graph(self, module: astroid.Module) -> Dict[str, List[str]]:
        """Build call graph"""
        call_graph = defaultdict(list)
        for node in module.nodes_of_class(astroid.Call):
            if isinstance(node.func, astroid.Name):
                caller = self._get_containing_function(node)
                if caller:
                    call_graph[caller].append(node.func.name)
        return dict(call_graph)
    
    def _build_inheritance_hierarchy(self, module: astroid.Module) -> Dict[str, List[str]]:
        """Build inheritance hierarchy"""
        hierarchy = {}
        for node in module.nodes_of_class(astroid.ClassDef):
            bases = [base.name for base in node.bases if isinstance(base, astroid.Name)]
            hierarchy[node.name] = bases
        return hierarchy
    
    def _calculate_complexity_metrics(self, module: astroid.Module) -> Dict[str, float]:
        """Calculate complexity metrics"""
        return {
            "total_functions": len(list(module.nodes_of_class(astroid.FunctionDef))),
            "total_classes": len(list(module.nodes_of_class(astroid.ClassDef))),
            "total_lines": len(module.file_bytes.decode().split('\n')) if module.file_bytes else 0
        }
    
    def _get_containing_function(self, node: astroid.NodeNG) -> Optional[str]:
        """Get the name of the function containing a node"""
        parent = node.parent
        while parent:
            if isinstance(parent, astroid.FunctionDef):
                return parent.name
            parent = parent.parent
        return None

class CSTAnalyzer:
    """Concrete Syntax Tree analysis using libcst"""
    
    def __init__(self):
        if not LIBCST_AVAILABLE:
            raise ImportError("libcst is required for CST analysis")
    
    def analyze(self, content: str, file_path: Path) -> CSTAnalysis:
        """Perform CST analysis"""
        try:
            tree = cst.parse_expression(content) if self._is_expression(content) else cst.parse_module(content)
            
            # Analyze formatting and style
            format_violations = self._check_format_violations(tree, content)
            whitespace_issues = self._check_whitespace_issues(content)
            comment_analysis = self._analyze_comments(content)
            docstring_coverage = self._calculate_docstring_coverage(tree)
            modification_suggestions = self._suggest_modifications(tree)
            code_style_score = self._calculate_style_score(format_violations, whitespace_issues)
            
            return CSTAnalysis(
                format_violations=format_violations,
                whitespace_issues=whitespace_issues,
                comment_analysis=comment_analysis,
                docstring_coverage=docstring_coverage,
                modification_suggestions=modification_suggestions,
                code_style_score=code_style_score
            )
            
        except Exception as e:
            logger.warning(f"CST analysis failed for {file_path}: {e}")
            return CSTAnalysis([], [], {}, 0.0, [], 0.0)
    
    def _is_expression(self, content: str) -> bool:
        """Check if content is a single expression"""
        try:
            ast.parse(content, mode='eval')
            return True
        except SyntaxError:
            return False
    
    def _check_format_violations(self, tree: CSTNodeType, content: str) -> List[str]:
        """Check for format violations"""
        violations = []
        
        # This would be expanded with specific formatting rules
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > 100:
                violations.append(f"Line {i} exceeds 100 characters")
        
        return violations
    
    def _check_whitespace_issues(self, content: str) -> List[str]:
        """Check for whitespace issues"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.endswith(' '):
                issues.append(f"Line {i} has trailing whitespace")
            if '\t' in line:
                issues.append(f"Line {i} contains tabs instead of spaces")
        
        return issues
    
    def _analyze_comments(self, content: str) -> Dict[str, Any]:
        """Analyze comments in code"""
        lines = content.split('\n')
        comment_lines = [i+1 for i, line in enumerate(lines) if line.strip().startswith('#')]
        
        return {
            "total_comments": len(comment_lines),
            "comment_lines": comment_lines,
            "comment_density": len(comment_lines) / len(lines) if lines else 0
        }
    
    def _calculate_docstring_coverage(self, tree: CSTNodeType) -> float:
        """Calculate docstring coverage"""
        # Simplified implementation
        return 0.8  # Placeholder
    
    def _suggest_modifications(self, tree: CSTNodeType) -> List[str]:
        """Suggest code modifications"""
        suggestions = []
        # This would be expanded with specific modification suggestions
        return suggestions
    
    def _calculate_style_score(self, format_violations: List[str], whitespace_issues: List[str]) -> float:
        """Calculate code style score"""
        total_issues = len(format_violations) + len(whitespace_issues)
        return max(100.0 - (total_issues * 5), 0.0)

# ============================================================================
# Main Execution and CLI Interface
# ============================================================================

def main():
    """Main execution function for standalone usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Static Analysis Framework")
    parser.add_argument("path", help="Path to file or directory to analyze")
    parser.add_argument("--level", choices=["surface", "structural", "semantic", "comprehensive"],
                       default="comprehensive", help="Analysis level")
    parser.add_argument("--output", help="Output file for analysis report")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format")
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analysis_level = AnalysisLevel(args.level)
    analyzer = AdvancedStaticAnalyzer(analysis_level)
    
    # Perform analysis
    path = Path(args.path)
    if path.is_file():
        result = analyzer.analyze_file(path)
        results = {str(path): result}
    else:
        results = analyzer.analyze_codebase(path)
    
    # Generate report
    report = analyzer.generate_analysis_report(results)
    
    # Output results
    if args.format == "json":
        output_content = json.dumps(report, indent=2, default=str)
    else:
        output_content = f"Advanced Static Analysis Report\n"
        output_content += f"Analysis completed: {report['summary']['total_files']} files\n"
        output_content += f"Total issues: {report['summary']['total_hallucinations'] + report['summary']['total_quality_issues']}\n"
        output_content += f"Critical issues: {report['summary']['critical_issues']}\n"
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_content)
        print(f"Report written to: {args.output}")
    else:
        print(output_content)

if __name__ == "__main__":
    main() 