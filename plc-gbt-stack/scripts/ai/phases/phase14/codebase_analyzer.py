#!/usr/bin/env python3
"""
Phase 14.1.1: Codebase Analysis Engine
======================================

Comprehensive codebase analysis with modular architecture assessment.
Following AI Task Orchestrator methodology for systematic code optimization.

Features:
- File structure analysis with complexity metrics
- Directory analysis with dependency mapping
- Refactoring opportunity identification
- Modular architecture compliance assessment
- Performance optimization recommendations

Target: ~800 lines
Author: AI Task Orchestrator
Date: 2025-01-18
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

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

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

@dataclass
class DirectoryAnalysis:
    """Directory structure analysis result"""
    directory_path: str
    total_files: int
    total_lines: int
    total_functions: int
    total_classes: int
    average_complexity: float
    modular_compliance_score: float
    file_analyses: List[FileAnalysisResult]
    dependency_graph: Dict[str, List[str]]
    circular_dependencies: List[List[str]]
    optimization_priorities: List[Dict[str, Any]]
    architecture_recommendations: List[str]

@dataclass
class RefactoringPlan:
    """Comprehensive refactoring plan"""
    plan_id: str
    target_files: List[str]
    refactoring_type: str  # modular_extraction, code_splitting, optimization
    estimated_effort: str
    safety_score: float
    impact_assessment: Dict[str, Any]
    step_by_step_plan: List[Dict[str, Any]]
    validation_criteria: List[str]
    rollback_strategy: str

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
            }
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
            "refactoring_suggestions": 0
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="2-4 hours",
            estimated_lines=800,
            requirements=[
                "AST parsing for Python code analysis",
                "Dependency graph generation",
                "Complexity metrics calculation",
                "Modular architecture assessment",
                "Refactoring opportunity identification"
            ],
            risks=[
                "Large codebase analysis performance",
                "Circular dependency detection complexity",
                "AST parsing errors on malformed code"
            ],
            dependencies=["ast", "pathlib", "core.BaseOrchestrator"],
            success_criteria=[
                "Accurate complexity metrics",
                "Comprehensive dependency mapping",
                "Actionable refactoring recommendations",
                "Performance under 30 seconds for 1000+ files"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute codebase analysis with comprehensive reporting"""
        self.log_execution_step("Codebase Analysis", "started")
        
        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}
            
            # Default analysis of current project
            project_root = self.config.get("system.project_root", str(Path.cwd()))
            
            # Perform comprehensive analysis
            analysis_result = self.analyze_directory(project_root)
            
            # Generate optimization recommendations
            optimization_plan = self._generate_optimization_plan(analysis_result)
            
            # Create performance summary
            performance_summary = self._create_performance_summary(analysis_result)
            
            # Save results
            results = {
                "analysis_result": asdict(analysis_result),
                "optimization_plan": optimization_plan,
                "performance_summary": performance_summary,
                "metrics": self.analysis_metrics,
                "session_info": {
                    "session_id": self.session_id,
                    "analysis_date": datetime.now().isoformat(),
                    "total_execution_time": self.results.get("execution_duration", 0)
                }
            }
            
            # Add performance metrics
            self.add_performance_metric("files_analyzed", self.analysis_metrics["files_analyzed"])
            self.add_performance_metric("optimization_opportunities", self.analysis_metrics["optimization_opportunities"])
            
            self.log_execution_step("Codebase Analysis", "completed", {
                "files_analyzed": self.analysis_metrics["files_analyzed"],
                "optimization_opportunities": self.analysis_metrics["optimization_opportunities"]
            })
            
            return results
            
        except Exception as e:
            self.log_error("Codebase analysis failed", e)
            return {"status": "failed", "error": str(e)}

    def analyze_file_structure(self, file_path: str) -> FileAnalysisResult:
        """
        Analyze individual file for modularity, complexity, optimization opportunities.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Comprehensive file analysis result
        """
        file_path = Path(file_path)
        
        # Check cache first
        file_hash = self._get_file_hash(file_path)
        if file_path.as_posix() in self.analysis_cache:
            cached_result = self.analysis_cache[file_path.as_posix()]
            if cached_result.get("file_hash") == file_hash:
                return cached_result["analysis"]
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse AST for Python files
            if file_path.suffix == '.py':
                analysis = self._analyze_python_file(file_path, content)
            else:
                analysis = self._analyze_generic_file(file_path, content)
            
            # Cache result
            self.analysis_cache[file_path.as_posix()] = {
                "file_hash": file_hash,
                "analysis": analysis
            }
            
            self.analysis_metrics["files_analyzed"] += 1
            return analysis
            
        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_path}: {e}")
            return self._create_error_analysis(file_path, str(e))

    def _analyze_python_file(self, file_path: Path, content: str) -> FileAnalysisResult:
        """Analyze Python file using AST parsing"""
        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            return self._create_error_analysis(file_path, f"Syntax error: {e}")
        
        # Extract basic metrics
        lines = content.split('\n')
        line_count = len(lines)
        size_bytes = len(content.encode('utf-8'))
        
        # AST analysis
        ast_analyzer = PythonASTAnalyzer()
        ast_metrics = ast_analyzer.analyze(tree)
        
        # Calculate complexity metrics
        complexity_score = self._calculate_complexity_score(ast_metrics, line_count)
        maintainability_index = self._calculate_maintainability_index(complexity_score, line_count)
        modularity_score = self._calculate_modularity_score(ast_metrics, line_count)
        technical_debt_score = self._calculate_technical_debt(ast_metrics, complexity_score)
        
        # Identify optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            ast_metrics, line_count, complexity_score
        )
        
        # Generate refactoring suggestions
        refactoring_suggestions = self._generate_refactoring_suggestions(
            ast_metrics, line_count, modularity_score
        )
        
        # Extract dependencies and exports
        dependencies = self._extract_dependencies(tree)
        exports = self._extract_exports(tree)
        
        # Estimate test coverage
        test_coverage_estimate = self._estimate_test_coverage(file_path, ast_metrics)
        
        return FileAnalysisResult(
            file_path=str(file_path),
            size_bytes=size_bytes,
            line_count=line_count,
            function_count=ast_metrics["function_count"],
            class_count=ast_metrics["class_count"],
            import_count=ast_metrics["import_count"],
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            modularity_score=modularity_score,
            optimization_opportunities=optimization_opportunities,
            refactoring_suggestions=refactoring_suggestions,
            dependencies=dependencies,
            exports=exports,
            technical_debt_score=technical_debt_score,
            test_coverage_estimate=test_coverage_estimate
        )

    def _analyze_generic_file(self, file_path: Path, content: str) -> FileAnalysisResult:
        """Analyze non-Python files with basic metrics"""
        lines = content.split('\n')
        line_count = len(lines)
        size_bytes = len(content.encode('utf-8'))
        
        # Basic complexity for non-Python files
        complexity_score = min(line_count / 100, 10)  # Simple line-based complexity
        maintainability_index = max(100 - complexity_score * 10, 0)
        modularity_score = 0.5  # Neutral for non-Python files
        
        return FileAnalysisResult(
            file_path=str(file_path),
            size_bytes=size_bytes,
            line_count=line_count,
            function_count=0,
            class_count=0,
            import_count=0,
            complexity_score=complexity_score,
            maintainability_index=maintainability_index,
            modularity_score=modularity_score,
            optimization_opportunities=[],
            refactoring_suggestions=[],
            dependencies=[],
            exports=[],
            technical_debt_score=0.0,
            test_coverage_estimate=0.0
        )

    def analyze_directory(self, directory: str) -> DirectoryAnalysis:
        """
        Analyze entire directory structure with dependency mapping.
        
        Args:
            directory: Root directory to analyze
            
        Returns:
            Comprehensive directory analysis
        """
        directory_path = Path(directory)
        
        self.log_execution_step("Directory Analysis", "started", {"directory": str(directory_path)})
        
        # Find all analyzable files
        files_to_analyze = self._find_analyzable_files(directory_path)
        
        # Analyze each file
        file_analyses = []
        for file_path in files_to_analyze:
            analysis = self.analyze_file_structure(file_path)
            file_analyses.append(analysis)
        
        # Calculate aggregate metrics
        total_files = len(file_analyses)
        total_lines = sum(fa.line_count for fa in file_analyses)
        total_functions = sum(fa.function_count for fa in file_analyses)
        total_classes = sum(fa.class_count for fa in file_analyses)
        average_complexity = sum(fa.complexity_score for fa in file_analyses) / max(total_files, 1)
        
        # Build dependency graph
        dependency_graph = self._build_dependency_graph(file_analyses)
        
        # Detect circular dependencies
        circular_dependencies = self._detect_circular_dependencies(dependency_graph)
        
        # Calculate modular compliance score
        modular_compliance_score = self._calculate_modular_compliance(file_analyses)
        
        # Generate optimization priorities
        optimization_priorities = self._prioritize_optimizations(file_analyses)
        
        # Generate architecture recommendations
        architecture_recommendations = self._generate_architecture_recommendations(
            file_analyses, dependency_graph, circular_dependencies
        )
        
        self.log_execution_step("Directory Analysis", "completed", {
            "total_files": total_files,
            "total_lines": total_lines,
            "circular_dependencies": len(circular_dependencies)
        })
        
        return DirectoryAnalysis(
            directory_path=str(directory_path),
            total_files=total_files,
            total_lines=total_lines,
            total_functions=total_functions,
            total_classes=total_classes,
            average_complexity=average_complexity,
            modular_compliance_score=modular_compliance_score,
            file_analyses=file_analyses,
            dependency_graph=dependency_graph,
            circular_dependencies=circular_dependencies,
            optimization_priorities=optimization_priorities,
            architecture_recommendations=architecture_recommendations
        )

    def identify_refactoring_opportunities(self, analysis: DirectoryAnalysis) -> List[RefactoringPlan]:
        """
        Generate automated refactoring recommendations.
        
        Args:
            analysis: Directory analysis result
            
        Returns:
            List of detailed refactoring plans
        """
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
        
        self.analysis_metrics["refactoring_suggestions"] = len(refactoring_plans)
        
        return refactoring_plans

    def _find_analyzable_files(self, directory: Path) -> List[Path]:
        """Find all files that can be analyzed"""
        analyzable_files = []
        
        for ext in self.analysis_config["supported_extensions"]:
            pattern = f"**/*{ext}"
            files = directory.glob(pattern)
            
            for file_path in files:
                if not self._should_ignore_file(file_path):
                    analyzable_files.append(file_path)
        
        return sorted(analyzable_files)

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns"""
        path_str = str(file_path)
        
        for pattern in self.analysis_config["ignore_patterns"]:
            if pattern in path_str:
                return True
        
        return False

    def _get_file_hash(self, file_path: Path) -> str:
        """Get file hash for caching"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return str(file_path.stat().st_mtime)

    def _create_error_analysis(self, file_path: Path, error: str) -> FileAnalysisResult:
        """Create error analysis result for failed files"""
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
            technical_debt_score=10.0,  # High debt for failed analysis
            test_coverage_estimate=0.0
        )

    # ... Additional helper methods continue below ...
    
    def _calculate_complexity_score(self, ast_metrics: Dict, line_count: int) -> float:
        """Calculate weighted complexity score"""
        cyclomatic = ast_metrics.get("cyclomatic_complexity", 1)
        cognitive = ast_metrics.get("cognitive_complexity", 1)
        
        # Normalize metrics
        normalized_cyclomatic = min(cyclomatic / 10, 1.0)
        normalized_cognitive = min(cognitive / 15, 1.0)
        normalized_length = min(line_count / 1000, 1.0)
        
        weights = self.analysis_config["complexity_weights"]
        
        score = (
            normalized_cyclomatic * weights["cyclomatic"] +
            normalized_cognitive * weights["cognitive"] +
            normalized_length * weights["maintainability"]
        ) * 10
        
        return round(score, 2)

    def _calculate_maintainability_index(self, complexity: float, line_count: int) -> float:
        """Calculate maintainability index (0-100, higher is better)"""
        # Simplified maintainability index
        base_score = 100
        complexity_penalty = complexity * 5
        length_penalty = max(0, (line_count - 500) / 50)
        
        score = max(0, base_score - complexity_penalty - length_penalty)
        return round(score, 2)

    def _calculate_modularity_score(self, ast_metrics: Dict, line_count: int) -> float:
        """Calculate modularity score (0-1, higher is better)"""
        function_count = ast_metrics.get("function_count", 0)
        class_count = ast_metrics.get("class_count", 0)
        
        # Score based on function/class density and file size
        if line_count == 0:
            return 0.0
        
        function_density = function_count / max(line_count / 50, 1)  # Functions per 50 lines
        class_density = class_count / max(line_count / 200, 1)      # Classes per 200 lines
        
        # Ideal ranges: 1-3 functions per 50 lines, 1 class per 200 lines
        function_score = 1.0 - abs(function_density - 2.0) / 5.0
        class_score = 1.0 - abs(class_density - 1.0) / 3.0
        
        # Size penalty for very large files
        size_score = 1.0 if line_count <= 500 else max(0, 1.0 - (line_count - 500) / 1500)
        
        score = (function_score + class_score + size_score) / 3
        return max(0.0, min(1.0, score))

    def _calculate_technical_debt(self, ast_metrics: Dict, complexity: float) -> float:
        """Calculate technical debt score (0-10, lower is better)"""
        debt_factors = []
        
        # Complexity-based debt
        debt_factors.append(complexity / 10)
        
        # TODO/FIXME comments
        todo_count = ast_metrics.get("todo_comments", 0)
        debt_factors.append(min(todo_count / 10, 1.0))
        
        # Long parameter lists
        max_params = ast_metrics.get("max_parameters", 0)
        if max_params > 5:
            debt_factors.append(min((max_params - 5) / 10, 1.0))
        
        # Deep nesting
        max_nesting = ast_metrics.get("max_nesting", 0)
        if max_nesting > 4:
            debt_factors.append(min((max_nesting - 4) / 6, 1.0))
        
        return round(sum(debt_factors) / len(debt_factors) * 10, 2) if debt_factors else 0.0

# Helper class for AST analysis
class PythonASTAnalyzer(ast.NodeVisitor):
    """AST analyzer for Python files"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.function_count = 0
        self.class_count = 0
        self.import_count = 0
        self.cyclomatic_complexity = 1
        self.cognitive_complexity = 0
        self.max_parameters = 0
        self.max_nesting = 0
        self.current_nesting = 0
        self.todo_comments = 0
        
    def analyze(self, tree: ast.AST) -> Dict[str, int]:
        self.reset()
        self.visit(tree)
        
        return {
            "function_count": self.function_count,
            "class_count": self.class_count,
            "import_count": self.import_count,
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "max_parameters": self.max_parameters,
            "max_nesting": self.max_nesting,
            "todo_comments": self.todo_comments
        }
    
    def visit_FunctionDef(self, node):
        self.function_count += 1
        self.max_parameters = max(self.max_parameters, len(node.args.args))
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_ClassDef(self, node):
        self.class_count += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_Import(self, node):
        self.import_count += len(node.names)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.import_count += len(node.names)
        self.generic_visit(node)
    
    def visit_If(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_For(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_While(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.current_nesting += 1
        self.max_nesting = max(self.max_nesting, self.current_nesting)
        self.generic_visit(node)
        self.current_nesting -= 1
    
    def visit_Try(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.generic_visit(node)
    
    def visit_ExceptHandler(self, node):
        self.cyclomatic_complexity += 1
        self.cognitive_complexity += 1
        self.generic_visit(node)


# Additional helper methods for CodebaseAnalyzer
def _identify_optimization_opportunities(self, ast_metrics: Dict, line_count: int, complexity: float) -> List[str]:
    """Identify specific optimization opportunities"""
    opportunities = []
    
    if line_count > self.analysis_config["max_file_lines"]:
        opportunities.append(f"File too large ({line_count} lines) - consider splitting")
    
    if complexity > self.analysis_config["max_complexity"]:
        opportunities.append(f"High complexity ({complexity}) - refactor complex functions")
    
    if ast_metrics.get("max_parameters", 0) > 5:
        opportunities.append("Functions with too many parameters - consider parameter objects")
    
    if ast_metrics.get("max_nesting", 0) > 4:
        opportunities.append("Deep nesting detected - consider early returns or extraction")
    
    if ast_metrics.get("todo_comments", 0) > 5:
        opportunities.append("Many TODO comments - address technical debt")
    
    function_count = ast_metrics.get("function_count", 0)
    if function_count > 20:
        opportunities.append("Many functions - consider grouping into classes or modules")
    
    return opportunities

def _generate_refactoring_suggestions(self, ast_metrics: Dict, line_count: int, modularity: float) -> List[str]:
    """Generate specific refactoring suggestions"""
    suggestions = []
    
    if modularity < 0.5:
        suggestions.append("Improve modularity by extracting utility functions")
    
    if line_count > 500:
        suggestions.append("Split large file into focused modules")
    
    if ast_metrics.get("function_count", 0) < 3 and line_count > 100:
        suggestions.append("Extract reusable functions from procedural code")
    
    if ast_metrics.get("class_count", 0) > 5:
        suggestions.append("Consider organizing classes into separate modules")
    
    return suggestions

def _extract_dependencies(self, tree: ast.AST) -> List[str]:
    """Extract import dependencies from AST"""
    dependencies = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                dependencies.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                dependencies.append(node.module)
    
    return list(set(dependencies))

def _extract_exports(self, tree: ast.AST) -> List[str]:
    """Extract exported functions and classes"""
    exports = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not node.name.startswith('_'):  # Public functions/classes
                exports.append(node.name)
    
    return exports

def _estimate_test_coverage(self, file_path: Path, ast_metrics: Dict) -> float:
    """Estimate test coverage based on file patterns"""
    # Look for corresponding test file
    test_patterns = [
        file_path.parent / f"test_{file_path.name}",
        file_path.parent / "tests" / file_path.name,
        file_path.parent.parent / "tests" / file_path.name
    ]
    
    has_test_file = any(pattern.exists() for pattern in test_patterns)
    
    # Basic heuristic: if test file exists, assume 70% coverage, otherwise 10%
    base_coverage = 0.7 if has_test_file else 0.1
    
    # Adjust based on function count (more functions = harder to test)
    function_count = ast_metrics.get("function_count", 0)
    if function_count > 10:
        base_coverage *= 0.8
    
    return min(base_coverage, 0.9)

def _build_dependency_graph(self, file_analyses: List[FileAnalysisResult]) -> Dict[str, List[str]]:
    """Build dependency graph from file analyses"""
    graph = defaultdict(list)
    
    # Create mapping of module names to file paths
    module_to_file = {}
    for analysis in file_analyses:
        file_path = Path(analysis.file_path)
        module_name = file_path.stem
        module_to_file[module_name] = analysis.file_path
    
    # Build graph
    for analysis in file_analyses:
        for dep in analysis.dependencies:
            # Extract module name from dependency
            dep_module = dep.split('.')[0]
            if dep_module in module_to_file:
                graph[analysis.file_path].append(module_to_file[dep_module])
    
    return dict(graph)

def _detect_circular_dependencies(self, dependency_graph: Dict[str, List[str]]) -> List[List[str]]:
    """Detect circular dependencies using DFS"""
    visited = set()
    rec_stack = set()
    cycles = []
    
    def dfs(node, path):
        if node in rec_stack:
            # Found cycle
            cycle_start = path.index(node)
            cycles.append(path[cycle_start:])
            return
        
        if node in visited:
            return
        
        visited.add(node)
        rec_stack.add(node)
        
        for neighbor in dependency_graph.get(node, []):
            dfs(neighbor, path + [neighbor])
        
        rec_stack.remove(node)
    
    for node in dependency_graph:
        if node not in visited:
            dfs(node, [node])
    
    return cycles

def _calculate_modular_compliance(self, file_analyses: List[FileAnalysisResult]) -> float:
    """Calculate overall modular compliance score"""
    if not file_analyses:
        return 0.0
    
    total_score = sum(analysis.modularity_score for analysis in file_analyses)
    average_score = total_score / len(file_analyses)
    
    # Penalty for files exceeding size limits
    oversized_files = sum(1 for analysis in file_analyses 
                         if analysis.line_count > self.analysis_config["max_file_lines"])
    size_penalty = oversized_files / len(file_analyses) * 0.3
    
    return max(0.0, average_score - size_penalty)

def _prioritize_optimizations(self, file_analyses: List[FileAnalysisResult]) -> List[Dict[str, Any]]:
    """Prioritize optimization opportunities by impact"""
    priorities = []
    
    for analysis in file_analyses:
        if analysis.optimization_opportunities:
            priority_score = self._calculate_priority_score(analysis)
            priorities.append({
                "file_path": analysis.file_path,
                "priority_score": priority_score,
                "opportunities": analysis.optimization_opportunities,
                "impact": self._assess_optimization_impact(analysis)
            })
    
    # Sort by priority score (higher = more important)
    priorities.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return priorities

def _calculate_priority_score(self, analysis: FileAnalysisResult) -> float:
    """Calculate priority score for optimization"""
    score = 0.0
    
    # Size factor
    if analysis.line_count > 1000:
        score += 3.0
    elif analysis.line_count > 500:
        score += 1.5
    
    # Complexity factor
    score += analysis.complexity_score * 0.5
    
    # Technical debt factor
    score += analysis.technical_debt_score * 0.3
    
    # Modularity factor (lower modularity = higher priority)
    score += (1.0 - analysis.modularity_score) * 2.0
    
    return round(score, 2)

def _assess_optimization_impact(self, analysis: FileAnalysisResult) -> Dict[str, str]:
    """Assess potential impact of optimization"""
    impact = {
        "maintainability": "medium",
        "performance": "low",
        "readability": "medium"
    }
    
    if analysis.line_count > 1000:
        impact["maintainability"] = "high"
        impact["readability"] = "high"
    
    if analysis.complexity_score > 8:
        impact["maintainability"] = "high"
        impact["performance"] = "medium"
    
    return impact

def _generate_architecture_recommendations(self, file_analyses: List[FileAnalysisResult], 
                                         dependency_graph: Dict[str, List[str]], 
                                         circular_deps: List[List[str]]) -> List[str]:
    """Generate architecture improvement recommendations"""
    recommendations = []
    
    # Large file recommendations
    large_files = [fa for fa in file_analyses if fa.line_count > 1000]
    if large_files:
        recommendations.append(f"Split {len(large_files)} large files into focused modules")
    
    # Circular dependency recommendations
    if circular_deps:
        recommendations.append(f"Resolve {len(circular_deps)} circular dependencies")
        recommendations.append("Consider dependency inversion or interface extraction")
    
    # Low modularity recommendations
    low_modularity = [fa for fa in file_analyses if fa.modularity_score < 0.5]
    if low_modularity:
        recommendations.append(f"Improve modularity in {len(low_modularity)} files")
    
    # High complexity recommendations
    high_complexity = [fa for fa in file_analyses if fa.complexity_score > 8]
    if high_complexity:
        recommendations.append(f"Refactor {len(high_complexity)} high-complexity files")
    
    # Module organization recommendations
    total_functions = sum(fa.function_count for fa in file_analyses)
    if total_functions > 100:
        recommendations.append("Consider creating utility modules for common functions")
    
    return recommendations

def _generate_optimization_plan(self, analysis: DirectoryAnalysis) -> Dict[str, Any]:
    """Generate comprehensive optimization plan"""
    return {
        "summary": {
            "total_files": analysis.total_files,
            "files_needing_optimization": len(analysis.optimization_priorities),
            "circular_dependencies": len(analysis.circular_dependencies),
            "estimated_effort": self._estimate_optimization_effort(analysis)
        },
        "priorities": analysis.optimization_priorities[:10],  # Top 10 priorities
        "quick_wins": self._identify_quick_wins(analysis),
        "major_refactoring": self._identify_major_refactoring(analysis),
        "architecture_improvements": analysis.architecture_recommendations
    }

def _estimate_optimization_effort(self, analysis: DirectoryAnalysis) -> str:
    """Estimate effort required for optimization"""
    total_score = sum(item["priority_score"] for item in analysis.optimization_priorities)
    
    if total_score > 50:
        return "High (3-4 weeks)"
    elif total_score > 20:
        return "Medium (1-2 weeks)"
    else:
        return "Low (2-5 days)"

def _identify_quick_wins(self, analysis: DirectoryAnalysis) -> List[Dict[str, Any]]:
    """Identify quick optimization wins"""
    quick_wins = []
    
    for item in analysis.optimization_priorities:
        if item["priority_score"] < 2.0:  # Low effort, good impact
            quick_wins.append({
                "file": item["file_path"],
                "action": "Quick refactoring",
                "effort": "1-2 hours"
            })
    
    return quick_wins[:5]  # Top 5 quick wins

def _identify_major_refactoring(self, analysis: DirectoryAnalysis) -> List[Dict[str, Any]]:
    """Identify major refactoring opportunities"""
    major_items = []
    
    for item in analysis.optimization_priorities:
        if item["priority_score"] > 5.0:
            major_items.append({
                "file": item["file_path"],
                "action": "Major refactoring",
                "effort": "1-2 days"
            })
    
    return major_items

def _create_performance_summary(self, analysis: DirectoryAnalysis) -> Dict[str, Any]:
    """Create performance summary of the analysis"""
    return {
        "analysis_metrics": self.analysis_metrics,
        "codebase_health": {
            "average_complexity": analysis.average_complexity,
            "modular_compliance": analysis.modular_compliance_score,
            "total_technical_debt": sum(fa.technical_debt_score for fa in analysis.file_analyses),
            "estimated_test_coverage": sum(fa.test_coverage_estimate for fa in analysis.file_analyses) / len(analysis.file_analyses)
        },
        "recommendations_summary": {
            "high_priority_files": len([p for p in analysis.optimization_priorities if p["priority_score"] > 5]),
            "medium_priority_files": len([p for p in analysis.optimization_priorities if 2 <= p["priority_score"] <= 5]),
            "low_priority_files": len([p for p in analysis.optimization_priorities if p["priority_score"] < 2])
        }
    }

def _create_file_splitting_plan(self, file_analysis: FileAnalysisResult) -> RefactoringPlan:
    """Create plan for splitting large files"""
    return RefactoringPlan(
        plan_id=f"split_{Path(file_analysis.file_path).stem}",
        target_files=[file_analysis.file_path],
        refactoring_type="file_splitting",
        estimated_effort="4-8 hours",
        safety_score=0.8,
        impact_assessment={
            "maintainability": "high",
            "readability": "high",
            "testability": "medium"
        },
        step_by_step_plan=[
            {"step": 1, "action": "Identify logical groupings of functions/classes"},
            {"step": 2, "action": "Create new module files"},
            {"step": 3, "action": "Move code to appropriate modules"},
            {"step": 4, "action": "Update import statements"},
            {"step": 5, "action": "Run tests to verify functionality"}
        ],
        validation_criteria=[
            "All tests pass after refactoring",
            "No circular dependencies introduced",
            "Import statements updated correctly"
        ],
        rollback_strategy="Git commit before changes, revert if issues"
    )

def _create_function_extraction_plan(self, file_analysis: FileAnalysisResult) -> RefactoringPlan:
    """Create plan for extracting complex functions"""
    return RefactoringPlan(
        plan_id=f"extract_{Path(file_analysis.file_path).stem}",
        target_files=[file_analysis.file_path],
        refactoring_type="function_extraction",
        estimated_effort="2-4 hours",
        safety_score=0.9,
        impact_assessment={
            "maintainability": "medium",
            "readability": "high",
            "testability": "high"
        },
        step_by_step_plan=[
            {"step": 1, "action": "Identify complex functions (>50 lines)"},
            {"step": 2, "action": "Extract helper functions"},
            {"step": 3, "action": "Create utility modules if needed"},
            {"step": 4, "action": "Update function calls"},
            {"step": 5, "action": "Add unit tests for extracted functions"}
        ],
        validation_criteria=[
            "Function complexity reduced",
            "All existing tests pass",
            "New functions have tests"
        ],
        rollback_strategy="Automated rollback using git"
    )

def _create_dependency_resolution_plan(self, circular_deps: List[List[str]]) -> RefactoringPlan:
    """Create plan for resolving circular dependencies"""
    target_files = list(set(file for cycle in circular_deps for file in cycle))
    
    return RefactoringPlan(
        plan_id="resolve_circular_deps",
        target_files=target_files,
        refactoring_type="dependency_resolution",
        estimated_effort="1-2 days",
        safety_score=0.6,
        impact_assessment={
            "maintainability": "high",
            "architecture": "high",
            "risk": "medium"
        },
        step_by_step_plan=[
            {"step": 1, "action": "Analyze dependency cycles"},
            {"step": 2, "action": "Identify common interfaces"},
            {"step": 3, "action": "Extract shared components"},
            {"step": 4, "action": "Implement dependency inversion"},
            {"step": 5, "action": "Verify no cycles remain"}
        ],
        validation_criteria=[
            "Zero circular dependencies",
            "All functionality preserved",
            "Clean dependency graph"
        ],
        rollback_strategy="Full system rollback - high risk change"
    )

def _create_modularity_improvement_plan(self, low_modularity_files: List[FileAnalysisResult]) -> RefactoringPlan:
    """Create plan for improving modularity"""
    target_files = [fa.file_path for fa in low_modularity_files]
    
    return RefactoringPlan(
        plan_id="improve_modularity",
        target_files=target_files,
        refactoring_type="modularity_improvement",
        estimated_effort="1-3 days",
        safety_score=0.7,
        impact_assessment={
            "maintainability": "high",
            "reusability": "medium",
            "testability": "medium"
        },
        step_by_step_plan=[
            {"step": 1, "action": "Extract utility functions"},
            {"step": 2, "action": "Group related functionality"},
            {"step": 3, "action": "Create focused modules"},
            {"step": 4, "action": "Improve code organization"},
            {"step": 5, "action": "Update documentation"}
        ],
        validation_criteria=[
            "Improved modularity scores",
            "Better code organization",
            "Maintained functionality"
        ],
        rollback_strategy="Incremental changes with git checkpoints"
    )

# Add these methods to the CodebaseAnalyzer class
CodebaseAnalyzer._identify_optimization_opportunities = _identify_optimization_opportunities
CodebaseAnalyzer._generate_refactoring_suggestions = _generate_refactoring_suggestions
CodebaseAnalyzer._extract_dependencies = _extract_dependencies
CodebaseAnalyzer._extract_exports = _extract_exports
CodebaseAnalyzer._estimate_test_coverage = _estimate_test_coverage
CodebaseAnalyzer._build_dependency_graph = _build_dependency_graph
CodebaseAnalyzer._detect_circular_dependencies = _detect_circular_dependencies
CodebaseAnalyzer._calculate_modular_compliance = _calculate_modular_compliance
CodebaseAnalyzer._prioritize_optimizations = _prioritize_optimizations
CodebaseAnalyzer._calculate_priority_score = _calculate_priority_score
CodebaseAnalyzer._assess_optimization_impact = _assess_optimization_impact
CodebaseAnalyzer._generate_architecture_recommendations = _generate_architecture_recommendations
CodebaseAnalyzer._generate_optimization_plan = _generate_optimization_plan
CodebaseAnalyzer._estimate_optimization_effort = _estimate_optimization_effort
CodebaseAnalyzer._identify_quick_wins = _identify_quick_wins
CodebaseAnalyzer._identify_major_refactoring = _identify_major_refactoring
CodebaseAnalyzer._create_performance_summary = _create_performance_summary
CodebaseAnalyzer._create_file_splitting_plan = _create_file_splitting_plan
CodebaseAnalyzer._create_function_extraction_plan = _create_function_extraction_plan
CodebaseAnalyzer._create_dependency_resolution_plan = _create_dependency_resolution_plan
CodebaseAnalyzer._create_modularity_improvement_plan = _create_modularity_improvement_plan 