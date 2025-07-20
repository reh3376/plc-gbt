#!/usr/bin/env python3
"""
AI Enhancement Framework - Codebase Analyzer
============================================

Comprehensive codebase analysis with modular architecture assessment.
Following AI Task Orchestrator methodology for systematic code optimization.

Features:
- File structure analysis with complexity metrics
- Directory analysis with dependency mapping
- Refactoring opportunity identification
- Modular architecture compliance assessment
- Performance optimization recommendations
- Hallucination detection for AI-generated code

Author: AI Enhancement Framework
Version: 1.0.0
"""

import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import re
import json
import hashlib
import importlib.util
from collections import defaultdict, Counter

# Framework imports
from ..core.task_orchestrator import BaseOrchestrator, TaskAnalysis

@dataclass
class FileAnalysisResult:
    """Individual file analysis result"""
    file_path: str
    size_bytes: int
    line_count: int
    function_count: int
    class_count: int
    import_count: int
    complexity_score: float
    maintainability_index: float
    modularity_score: float
    optimization_opportunities: List[str]
    refactoring_suggestions: List[str]
    dependencies: List[str]
    exports: List[str]
    technical_debt_score: float
    test_coverage_estimate: float
    hallucination_indicators: List[str]

@dataclass
class DirectoryAnalysis:
    """Directory analysis result"""
    directory_path: str
    total_files: int
    total_lines: int
    file_analyses: List[FileAnalysisResult]
    circular_dependencies: List[str]
    common_patterns: Dict[str, int]
    modularity_violations: List[str]
    overall_quality_score: float
    refactoring_priority: List[str]

@dataclass
class RefactoringPlan:
    """Detailed refactoring plan"""
    plan_id: str
    target_files: List[str]
    refactoring_type: str
    description: str
    estimated_effort: str
    risk_level: str
    prerequisites: List[str]
    expected_benefits: List[str]
    validation_requirements: List[str]

class CodebaseAnalyzer(BaseOrchestrator):
    """
    Comprehensive codebase analysis engine with modular architecture assessment.
    
    Provides sophisticated analysis of Python codebases for optimization opportunities,
    modular architecture compliance, and automated refactoring recommendations.
    """

    def __init__(self, task_id: str = "codebase_analysis", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)
        
        # Analysis configuration
        self.analysis_config = {
            "max_function_lines": 50,
            "max_file_lines": 1000,
            "max_complexity": 10,
            "min_modularity_score": 0.7,
            "supported_extensions": [".py", ".ts", ".js", ".sql"],
            "ignore_patterns": ["__pycache__", ".git", "node_modules", ".venv", "*.pyc"],
            "complexity_weights": {
                "cyclomatic": 0.4,
                "cognitive": 0.3,
                "maintainability": 0.3
            },
            "hallucination_patterns": [
                r"TODO.*implement.*",
                r"placeholder.*implementation",
                r"example\.com",
                r"your_.*_here",
                r"replace.*with.*actual"
            ]
        }
        
        # Analysis cache for performance
        self.analysis_cache = {}
        self.file_hash_cache = {}
        
        # Metrics tracking
        self.analysis_metrics = {
            "files_analyzed": 0,
            "functions_analyzed": 0,
            "classes_analyzed": 0,
            "optimization_opportunities": 0,
            "refactoring_suggestions": 0,
            "hallucinations_detected": 0
        }

    def analyze_file_structure(self, file_path: str) -> FileAnalysisResult:
        """
        Analyze individual file for modularity, complexity, optimization opportunities.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Detailed file analysis result
        """
        file_path = Path(file_path)
        
        # Check cache first
        file_hash = self._get_file_hash(file_path)
        if file_hash in self.analysis_cache:
            return self.analysis_cache[file_hash]
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Basic file metrics
            size_bytes = file_path.stat().st_size
            line_count = len(content.splitlines())
            
            # Parse AST for Python files
            if file_path.suffix == '.py':
                result = self._analyze_python_file(file_path, content, size_bytes, line_count)
            else:
                result = self._analyze_generic_file(file_path, content, size_bytes, line_count)
            
            # Cache result
            self.analysis_cache[file_hash] = result
            self.analysis_metrics["files_analyzed"] += 1
            
            return result
            
        except Exception as e:
            self.log(f"Error analyzing file {file_path}: {e}", "error")
            return self._create_error_result(file_path, str(e))

    def _analyze_python_file(self, file_path: Path, content: str, size_bytes: int, line_count: int) -> FileAnalysisResult:
        """Analyze Python file using AST parsing"""
        try:
            tree = ast.parse(content)
            
            # Count components
            function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            import_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
            
            # Calculate complexity metrics
            complexity_score = self._calculate_complexity(tree)
            maintainability_index = self._calculate_maintainability(tree, line_count)
            modularity_score = self._calculate_modularity(tree)
            technical_debt_score = self._calculate_technical_debt(tree, content)
            
            # Identify optimization opportunities
            optimization_opportunities = self._identify_optimization_opportunities(tree, content)
            refactoring_suggestions = self._generate_refactoring_suggestions(tree, line_count)
            
            # Extract dependencies and exports
            dependencies = self._extract_dependencies(tree)
            exports = self._extract_exports(tree)
            
            # Detect hallucination indicators
            hallucination_indicators = self._detect_hallucinations(content)
            
            # Estimate test coverage
            test_coverage_estimate = self._estimate_test_coverage(file_path, tree)
            
            self.analysis_metrics["functions_analyzed"] += function_count
            self.analysis_metrics["classes_analyzed"] += class_count
            self.analysis_metrics["optimization_opportunities"] += len(optimization_opportunities)
            self.analysis_metrics["refactoring_suggestions"] += len(refactoring_suggestions)
            self.analysis_metrics["hallucinations_detected"] += len(hallucination_indicators)
            
            return FileAnalysisResult(
                file_path=str(file_path),
                size_bytes=size_bytes,
                line_count=line_count,
                function_count=function_count,
                class_count=class_count,
                import_count=import_count,
                complexity_score=complexity_score,
                maintainability_index=maintainability_index,
                modularity_score=modularity_score,
                optimization_opportunities=optimization_opportunities,
                refactoring_suggestions=refactoring_suggestions,
                dependencies=dependencies,
                exports=exports,
                technical_debt_score=technical_debt_score,
                test_coverage_estimate=test_coverage_estimate,
                hallucination_indicators=hallucination_indicators
            )
            
        except SyntaxError as e:
            self.log(f"Syntax error in {file_path}: {e}", "warning")
            return self._create_syntax_error_result(file_path, size_bytes, line_count, str(e))

    def _detect_hallucinations(self, content: str) -> List[str]:
        """Detect hallucination indicators in code"""
        indicators = []
        
        for pattern in self.analysis_config["hallucination_patterns"]:
            matches = re.findall(pattern, content, re.IGNORECASE)
            indicators.extend(matches)
        
        # Additional hallucination checks
        if "from fake_module import" in content:
            indicators.append("fake_module_import")
        
        if "api_key = 'your_key_here'" in content:
            indicators.append("placeholder_credentials")
        
        if content.count("pass  # TODO") > 2:
            indicators.append("excessive_todo_placeholders")
        
        return indicators

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
            elif isinstance(node, ast.comprehension):
                complexity += 1
        
        return min(complexity / 10.0, 1.0)  # Normalize to 0-1 scale

    def _calculate_maintainability(self, tree: ast.AST, line_count: int) -> float:
        """Calculate maintainability index"""
        # Simplified maintainability calculation
        complexity = self._calculate_complexity(tree) * 10
        
        # Count operators and operands (simplified)
        operators = 0
        operands = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.operator):
                operators += 1
            elif isinstance(node, (ast.Name, ast.Constant)):
                operands += 1
        
        # Halstead metrics (simplified)
        vocabulary = operators + operands
        length = operators + operands
        
        if vocabulary > 0 and length > 0:
            volume = length * (vocabulary.bit_length() if vocabulary > 0 else 1)
            maintainability = max(0, 171 - 5.2 * np.log(volume) - 0.23 * complexity - 16.2 * np.log(line_count))
            return min(maintainability / 100.0, 1.0)
        
        return 0.5  # Default moderate maintainability

    def _calculate_modularity(self, tree: ast.AST) -> float:
        """Calculate modularity score based on code organization"""
        score = 1.0
        
        # Check for proper class organization
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        # Penalty for too many top-level functions
        if len(functions) > 10:
            score -= 0.2
        
        # Bonus for proper class encapsulation
        if classes and len(functions) / max(len(classes), 1) < 5:
            score += 0.1
        
        # Check for imports organization
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        if len(imports) > 20:
            score -= 0.1
        
        return max(0.0, min(1.0, score))

    def _calculate_technical_debt(self, tree: ast.AST, content: str) -> float:
        """Calculate technical debt score"""
        debt_score = 0.0
        
        # Count TODO comments
        todo_count = content.count("TODO") + content.count("FIXME") + content.count("HACK")
        debt_score += todo_count * 0.1
        
        # Count long functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > 50:
                    debt_score += 0.2
        
        # Count magic numbers
        magic_numbers = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in [0, 1, -1, 100] and abs(node.value) > 1:
                    magic_numbers += 1
        
        debt_score += magic_numbers * 0.05
        
        return min(1.0, debt_score)

    def _identify_optimization_opportunities(self, tree: ast.AST, content: str) -> List[str]:
        """Identify code optimization opportunities"""
        opportunities = []
        
        # Check for inefficient loops
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                # Look for list comprehension opportunities
                if any(isinstance(child, ast.Append) for child in ast.walk(node)):
                    opportunities.append("Consider list comprehension instead of append in loop")
        
        # Check for string concatenation in loops
        if re.search(r'for.*:\s*.*\+=.*str', content, re.MULTILINE):
            opportunities.append("Use join() instead of string concatenation in loops")
        
        # Check for duplicate imports
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.append(f"{node.module}.{alias.name}")
        
        if len(imports) != len(set(imports)):
            opportunities.append("Remove duplicate imports")
        
        # Check for large functions
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                if func_lines > self.analysis_config["max_function_lines"]:
                    opportunities.append(f"Consider breaking down large function: {node.name}")
        
        return opportunities

    def _generate_refactoring_suggestions(self, tree: ast.AST, line_count: int) -> List[str]:
        """Generate refactoring suggestions"""
        suggestions = []
        
        # Suggest file splitting for large files
        if line_count > self.analysis_config["max_file_lines"]:
            suggestions.append("Consider splitting large file into smaller modules")
        
        # Suggest class extraction for grouped functions
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        if len(functions) > 15:
            suggestions.append("Consider grouping related functions into classes")
        
        # Suggest utility module extraction
        function_names = [node.name for node in functions]
        utility_patterns = ['_helper', '_util', '_format', '_convert']
        utility_functions = [name for name in function_names 
                           if any(pattern in name for pattern in utility_patterns)]
        
        if len(utility_functions) > 3:
            suggestions.append("Consider extracting utility functions to separate module")
        
        return suggestions

    def _extract_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract file dependencies"""
        dependencies = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    dependencies.append(alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                dependencies.append(node.module)
        
        return list(set(dependencies))

    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """Extract what this file exports"""
        exports = []
        
        # Find __all__ definition
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for elt in node.value.elts:
                                if isinstance(elt, ast.Constant):
                                    exports.append(elt.value)
        
        # If no __all__, extract top-level definitions
        if not exports:
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not node.name.startswith('_'):
                        exports.append(node.name)
        
        return exports

    def _estimate_test_coverage(self, file_path: Path, tree: ast.AST) -> float:
        """Estimate test coverage based on test file presence"""
        # Look for corresponding test file
        test_patterns = [
            file_path.parent / f"test_{file_path.name}",
            file_path.parent / "tests" / f"test_{file_path.name}",
            file_path.parent.parent / "tests" / f"test_{file_path.name}"
        ]
        
        has_test_file = any(test_path.exists() for test_path in test_patterns)
        
        # Count testable functions (public functions)
        public_functions = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                public_functions += 1
        
        if has_test_file:
            return 0.8 if public_functions > 0 else 1.0
        else:
            return 0.2 if public_functions > 0 else 1.0

    def analyze_directory(self, directory: str) -> DirectoryAnalysis:
        """
        Analyze entire directory structure with dependency mapping.
        
        Args:
            directory: Path to directory to analyze
            
        Returns:
            Comprehensive directory analysis
        """
        directory_path = Path(directory)
        file_analyses = []
        total_lines = 0
        
        # Find all analyzable files
        for ext in self.analysis_config["supported_extensions"]:
            for file_path in directory_path.rglob(f"*{ext}"):
                # Skip ignored patterns
                if any(pattern in str(file_path) for pattern in self.analysis_config["ignore_patterns"]):
                    continue
                
                analysis = self.analyze_file_structure(file_path)
                file_analyses.append(analysis)
                total_lines += analysis.line_count
        
        # Analyze circular dependencies
        circular_dependencies = self._detect_circular_dependencies(file_analyses)
        
        # Find common patterns
        common_patterns = self._find_common_patterns(file_analyses)
        
        # Identify modularity violations
        modularity_violations = self._identify_modularity_violations(file_analyses)
        
        # Calculate overall quality score
        overall_quality_score = self._calculate_overall_quality(file_analyses)
        
        # Prioritize refactoring targets
        refactoring_priority = self._prioritize_refactoring(file_analyses)
        
        return DirectoryAnalysis(
            directory_path=str(directory_path),
            total_files=len(file_analyses),
            total_lines=total_lines,
            file_analyses=file_analyses,
            circular_dependencies=circular_dependencies,
            common_patterns=common_patterns,
            modularity_violations=modularity_violations,
            overall_quality_score=overall_quality_score,
            refactoring_priority=refactoring_priority
        )

    def identify_refactoring_opportunities(self, analysis: DirectoryAnalysis) -> List[RefactoringPlan]:
        """Generate automated refactoring recommendations"""
        refactoring_plans = []
        
        # Large file refactoring opportunities
        large_files = [fa for fa in analysis.file_analyses 
                      if fa.line_count > self.analysis_config["max_file_lines"]]
        
        for file_analysis in large_files:
            plan = self._create_file_splitting_plan(file_analysis)
            refactoring_plans.append(plan)
        
        # Complex function extraction opportunities
        complex_files = [fa for fa in analysis.file_analyses 
                        if fa.complexity_score > self.analysis_config["max_complexity"]]
        
        for file_analysis in complex_files:
            plan = self._create_function_extraction_plan(file_analysis)
            refactoring_plans.append(plan)
        
        # Circular dependency resolution
        if analysis.circular_dependencies:
            plan = self._create_dependency_resolution_plan(analysis.circular_dependencies)
            refactoring_plans.append(plan)
        
        # Modular architecture improvements
        low_modularity_files = [fa for fa in analysis.file_analyses 
                               if fa.modularity_score < self.analysis_config["min_modularity_score"]]
        
        if low_modularity_files:
            plan = self._create_modularity_improvement_plan(low_modularity_files)
            refactoring_plans.append(plan)
        
        return refactoring_plans

    def _get_file_hash(self, file_path: Path) -> str:
        """Get file hash for caching"""
        stat = file_path.stat()
        return hashlib.md5(f"{file_path}:{stat.st_mtime}:{stat.st_size}".encode()).hexdigest()

    def _create_error_result(self, file_path: Path, error: str) -> FileAnalysisResult:
        """Create error result for failed analysis"""
        return FileAnalysisResult(
            file_path=str(file_path),
            size_bytes=0,
            line_count=0,
            function_count=0,
            class_count=0,
            import_count=0,
            complexity_score=0.0,
            maintainability_index=0.0,
            modularity_score=0.0,
            optimization_opportunities=[f"Analysis failed: {error}"],
            refactoring_suggestions=[],
            dependencies=[],
            exports=[],
            technical_debt_score=1.0,
            test_coverage_estimate=0.0,
            hallucination_indicators=[]
        )

    def _create_syntax_error_result(self, file_path: Path, size_bytes: int, line_count: int, error: str) -> FileAnalysisResult:
        """Create result for files with syntax errors"""
        return FileAnalysisResult(
            file_path=str(file_path),
            size_bytes=size_bytes,
            line_count=line_count,
            function_count=0,
            class_count=0,
            import_count=0,
            complexity_score=1.0,  # High complexity due to syntax issues
            maintainability_index=0.0,
            modularity_score=0.0,
            optimization_opportunities=[f"Fix syntax error: {error}"],
            refactoring_suggestions=["Fix syntax errors before refactoring"],
            dependencies=[],
            exports=[],
            technical_debt_score=1.0,
            test_coverage_estimate=0.0,
            hallucination_indicators=[f"syntax_error: {error}"]
        )

    def _analyze_generic_file(self, file_path: Path, content: str, size_bytes: int, line_count: int) -> FileAnalysisResult:
        """Analyze non-Python files"""
        return FileAnalysisResult(
            file_path=str(file_path),
            size_bytes=size_bytes,
            line_count=line_count,
            function_count=0,
            class_count=0,
            import_count=0,
            complexity_score=0.1,
            maintainability_index=0.8,
            modularity_score=0.5,
            optimization_opportunities=[],
            refactoring_suggestions=[],
            dependencies=[],
            exports=[],
            technical_debt_score=0.1,
            test_coverage_estimate=0.5,
            hallucination_indicators=[]
        )

    def _detect_circular_dependencies(self, file_analyses: List[FileAnalysisResult]) -> List[str]:
        """Detect circular dependencies between files"""
        # Simplified circular dependency detection
        dependencies = {}
        for analysis in file_analyses:
            dependencies[analysis.file_path] = analysis.dependencies
        
        circular = []
        for file_path, deps in dependencies.items():
            for dep in deps:
                if dep in dependencies and file_path in dependencies[dep]:
                    circular.append(f"{file_path} <-> {dep}")
        
        return list(set(circular))

    def _find_common_patterns(self, file_analyses: List[FileAnalysisResult]) -> Dict[str, int]:
        """Find common code patterns across files"""
        patterns = defaultdict(int)
        
        for analysis in file_analyses:
            # Count common optimization opportunities
            for opportunity in analysis.optimization_opportunities:
                patterns[opportunity] += 1
            
            # Count common dependencies
            for dep in analysis.dependencies:
                patterns[f"uses_{dep}"] += 1
        
        return dict(patterns)

    def _identify_modularity_violations(self, file_analyses: List[FileAnalysisResult]) -> List[str]:
        """Identify modularity violations"""
        violations = []
        
        for analysis in file_analyses:
            if analysis.modularity_score < self.analysis_config["min_modularity_score"]:
                violations.append(f"Low modularity: {analysis.file_path}")
            
            if analysis.line_count > self.analysis_config["max_file_lines"]:
                violations.append(f"Large file: {analysis.file_path}")
            
            if analysis.complexity_score > 0.8:
                violations.append(f"High complexity: {analysis.file_path}")
        
        return violations

    def _calculate_overall_quality(self, file_analyses: List[FileAnalysisResult]) -> float:
        """Calculate overall codebase quality score"""
        if not file_analyses:
            return 0.0
        
        scores = []
        for analysis in file_analyses:
            score = (
                analysis.maintainability_index * 0.3 +
                analysis.modularity_score * 0.3 +
                (1 - analysis.complexity_score) * 0.2 +
                (1 - analysis.technical_debt_score) * 0.2
            )
            scores.append(score)
        
        return sum(scores) / len(scores)

    def _prioritize_refactoring(self, file_analyses: List[FileAnalysisResult]) -> List[str]:
        """Prioritize files for refactoring"""
        # Score files by refactoring urgency
        scored_files = []
        
        for analysis in file_analyses:
            urgency_score = (
                analysis.technical_debt_score * 0.4 +
                analysis.complexity_score * 0.3 +
                (1 - analysis.modularity_score) * 0.2 +
                (analysis.line_count / 1000) * 0.1
            )
            scored_files.append((urgency_score, analysis.file_path))
        
        # Sort by urgency (highest first)
        scored_files.sort(reverse=True)
        
        return [file_path for _, file_path in scored_files[:10]]

    def _create_file_splitting_plan(self, file_analysis: FileAnalysisResult) -> RefactoringPlan:
        """Create plan for splitting large file"""
        return RefactoringPlan(
            plan_id=f"split_{hashlib.md5(file_analysis.file_path.encode()).hexdigest()[:8]}",
            target_files=[file_analysis.file_path],
            refactoring_type="file_splitting",
            description=f"Split large file ({file_analysis.line_count} lines) into smaller modules",
            estimated_effort="2-4 hours",
            risk_level="medium",
            prerequisites=["Comprehensive test coverage", "Dependency analysis"],
            expected_benefits=["Improved maintainability", "Better modularity", "Easier testing"],
            validation_requirements=["All tests pass", "No circular dependencies", "Import statements updated"]
        )

    def _create_function_extraction_plan(self, file_analysis: FileAnalysisResult) -> RefactoringPlan:
        """Create plan for extracting complex functions"""
        return RefactoringPlan(
            plan_id=f"extract_{hashlib.md5(file_analysis.file_path.encode()).hexdigest()[:8]}",
            target_files=[file_analysis.file_path],
            refactoring_type="function_extraction",
            description=f"Extract complex functions to utility modules",
            estimated_effort="1-2 hours",
            risk_level="low",
            prerequisites=["Function dependency analysis"],
            expected_benefits=["Reduced complexity", "Improved reusability", "Better testing"],
            validation_requirements=["Function behavior unchanged", "All tests pass"]
        )

    def _create_dependency_resolution_plan(self, circular_dependencies: List[str]) -> RefactoringPlan:
        """Create plan for resolving circular dependencies"""
        return RefactoringPlan(
            plan_id=f"resolve_circular_{len(circular_dependencies)}",
            target_files=[],
            refactoring_type="dependency_resolution",
            description=f"Resolve {len(circular_dependencies)} circular dependencies",
            estimated_effort="4-8 hours",
            risk_level="high",
            prerequisites=["Complete dependency mapping", "Test coverage"],
            expected_benefits=["Cleaner architecture", "Easier maintenance", "Better testability"],
            validation_requirements=["No circular imports", "All functionality preserved"]
        )

    def _create_modularity_improvement_plan(self, low_modularity_files: List[FileAnalysisResult]) -> RefactoringPlan:
        """Create plan for improving modularity"""
        return RefactoringPlan(
            plan_id=f"modularity_{len(low_modularity_files)}",
            target_files=[f.file_path for f in low_modularity_files],
            refactoring_type="modularity_improvement",
            description=f"Improve modularity of {len(low_modularity_files)} files",
            estimated_effort="3-6 hours",
            risk_level="medium",
            prerequisites=["Architecture design", "Module interface definition"],
            expected_benefits=["Better code organization", "Improved reusability", "Easier maintenance"],
            validation_requirements=["Clear module boundaries", "Minimal coupling", "High cohesion"]
        )

# Make numpy available for calculations
try:
    import numpy as np
except ImportError:
    # Fallback for environments without numpy
    class np:
        @staticmethod
        def log(x):
            import math
            return math.log(x) 