#!/usr/bin/env python3
"""
Phase 14.2.2: Code Quality Optimizer
====================================

Automated code quality improvements for enterprise-grade refactoring.
Following AI Task Orchestrator methodology for systematic code optimization.

Features:
- Import statement optimization (remove unused, sort, group)
- Large file refactoring into modular components
- Consistent coding pattern standardization
- Code style enforcement and cleanup
- Performance optimization recommendations

Target: ~600 lines
Author: AI Task Orchestrator
Date: 2025-01-18
Dependencies: Phase 14.1 (CodebaseAnalyzer), Phase 14.2.1 (ModularExtractor)
"""

import ast
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

# Import Phase 14 dependencies
try:
    from .codebase_analyzer import CodebaseAnalyzer, DirectoryAnalysis, FileAnalysisResult
    from .modular_extractor import FunctionExtraction, ModularExtractor
except ImportError:
    # Fallback for direct execution
    from codebase_analyzer import CodebaseAnalyzer, DirectoryAnalysis, FileAnalysisResult
    from modular_extractor import ModularExtractor

@dataclass
class ImportOptimization:
    """Details of import statement optimization"""
    file_path: str
    original_imports: List[str]
    optimized_imports: List[str]
    unused_imports: List[str]
    added_imports: List[str]
    reordered_imports: List[str]
    optimization_score: float
    estimated_performance_gain: float

@dataclass
class FileRefactoring:
    """Details of large file refactoring"""
    source_file: str
    original_size: int
    target_files: List[str]
    refactoring_strategy: str
    estimated_new_sizes: List[int]
    complexity_reduction: float
    maintainability_improvement: float
    safety_score: float

@dataclass
class PatternStandardization:
    """Details of coding pattern standardization"""
    pattern_type: str
    files_affected: List[str]
    old_pattern: str
    new_pattern: str
    occurrences_updated: int
    consistency_score: float
    impact_assessment: str

@dataclass
class OptimizationResult:
    """Comprehensive optimization result"""
    optimization_id: str
    import_optimizations: List[ImportOptimization]
    file_refactorings: List[FileRefactoring]
    pattern_standardizations: List[PatternStandardization]
    overall_quality_score: float
    performance_improvements: Dict[str, float]
    maintainability_improvements: Dict[str, float]
    rollback_data: Dict[str, Any]

class CodeQualityOptimizer(BaseOrchestrator):
    """
    Automated code quality optimizer with comprehensive refactoring capabilities.

    Provides enterprise-grade code quality improvements including import optimization,
    file restructuring, and pattern standardization for maximum maintainability.
    """

    def __init__(self, task_id: str = "code_quality_optimization", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)

        # Initialize dependencies
        self.codebase_analyzer = CodebaseAnalyzer("quality_analysis")
        self.modular_extractor = ModularExtractor("quality_extraction")

        # Optimization configuration
        self.optimization_config = {
            "import_optimization": {
                "remove_unused": True,
                "sort_imports": True,
                "group_imports": True,
                "max_line_length": 88,
                "prefer_from_imports": True
            },
            "file_refactoring": {
                "max_file_size": 1000,  # Lines
                "target_file_size": 300,  # Lines
                "min_function_extraction_size": 30,  # Lines
                "preserve_class_cohesion": True
            },
            "pattern_standardization": {
                "enforce_docstrings": True,
                "standardize_logging": True,
                "enforce_type_hints": True,
                "standardize_error_handling": True,
                "consistent_naming": True
            },
            "quality_thresholds": {
                "min_optimization_score": 0.7,
                "min_safety_score": 0.8,
                "max_complexity_per_function": 10
            }
        }

        # Optimization tracking
        self.optimization_metrics = {
            "files_optimized": 0,
            "imports_optimized": 0,
            "patterns_standardized": 0,
            "lines_reduced": 0,
            "complexity_reduction": 0.0,
            "performance_improvement": 0.0
        }

        # Pattern definitions
        self.standard_patterns = self._define_standard_patterns()

        # Rollback system
        self.rollback_registry = {}

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="complex",
            estimated_time="4-6 hours",
            estimated_lines=600,
            requirements=[
                "AST parsing for import analysis",
                "Import statement optimization and sorting",
                "Large file detection and refactoring",
                "Pattern recognition and standardization",
                "Code quality metrics calculation",
                "Safe refactoring with rollback capabilities"
            ],
            risks=[
                "Breaking imports during optimization",
                "Loss of functionality during refactoring",
                "Inconsistent pattern application",
                "Performance regression from excessive imports"
            ],
            dependencies=["ast", "pathlib", "core.BaseOrchestrator", "codebase_analyzer", "modular_extractor"],
            success_criteria=[
                "≥20% improvement in code quality metrics",
                "Zero functionality regression",
                "Consistent pattern application across codebase",
                "≥90% import optimization success rate",
                "Automated rollback capability"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute comprehensive code quality optimization"""
        self.log_execution_step("Code Quality Optimization", "started")

        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}

            # Get project root for analysis
            project_root = self.config.get("system.project_root", str(Path.cwd()))

            # Phase 1: Analyze codebase for optimization opportunities
            self.log_execution_step("Quality Analysis", "started")
            directory_analysis = self.codebase_analyzer.analyze_directory(project_root)
            optimization_opportunities = self._identify_optimization_opportunities(directory_analysis)
            self.log_execution_step("Quality Analysis", "completed", {
                "files_analyzed": directory_analysis.total_files,
                "optimization_opportunities": len(optimization_opportunities)
            })

            # Phase 2: Optimize imports across all files
            self.log_execution_step("Import Optimization", "started")
            import_optimizations = self._optimize_imports(directory_analysis.file_analyses)
            self.log_execution_step("Import Optimization", "completed", {
                "files_optimized": len(import_optimizations),
                "total_imports_optimized": sum(len(opt.unused_imports) for opt in import_optimizations)
            })

            # Phase 3: Refactor large files
            self.log_execution_step("File Refactoring", "started")
            file_refactorings = self._refactor_large_files(directory_analysis.file_analyses)
            self.log_execution_step("File Refactoring", "completed", {
                "files_refactored": len(file_refactorings),
                "total_size_reduction": sum(ref.original_size - sum(ref.estimated_new_sizes) for ref in file_refactorings)
            })

            # Phase 4: Standardize patterns
            self.log_execution_step("Pattern Standardization", "started")
            pattern_standardizations = self._standardize_patterns(directory_analysis.file_analyses)
            self.log_execution_step("Pattern Standardization", "completed", {
                "patterns_standardized": len(pattern_standardizations),
                "total_occurrences": sum(ps.occurrences_updated for ps in pattern_standardizations)
            })

            # Phase 5: Calculate overall quality improvements
            self.log_execution_step("Quality Assessment", "started")
            quality_results = self._assess_quality_improvements(
                import_optimizations, file_refactorings, pattern_standardizations
            )
            self.log_execution_step("Quality Assessment", "completed", {
                "overall_quality_score": quality_results["overall_quality_score"]
            })

            # Compile results
            optimization_result = OptimizationResult(
                optimization_id=f"quality_opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                import_optimizations=import_optimizations,
                file_refactorings=file_refactorings,
                pattern_standardizations=pattern_standardizations,
                overall_quality_score=quality_results["overall_quality_score"],
                performance_improvements=quality_results["performance_improvements"],
                maintainability_improvements=quality_results["maintainability_improvements"],
                rollback_data=self._create_rollback_data()
            )

            # Update metrics
            self.optimization_metrics["files_optimized"] = len(set(
                [opt.file_path for opt in import_optimizations] +
                [ref.source_file for ref in file_refactorings]
            ))

            results = {
                "optimization_result": asdict(optimization_result),
                "metrics": self.optimization_metrics,
                "quality_assessment": quality_results,
                "session_info": {
                    "session_id": self.session_id,
                    "optimization_date": datetime.now().isoformat()
                }
            }

            # Add performance metrics
            self.add_performance_metric("files_optimized", self.optimization_metrics["files_optimized"])
            self.add_performance_metric("overall_quality_score", quality_results["overall_quality_score"])

            return results

        except Exception as e:
            self.log_error("Code quality optimization failed", e)
            return {"status": "failed", "error": str(e)}

    def optimize_imports(self, file_path: str) -> ImportOptimization:
        """
        Optimize import statements in a single file.

        Args:
            file_path: Path to the file to optimize

        Returns:
            Import optimization result with before/after analysis
        """
        file_path = Path(file_path)

        self.log_execution_step("Single File Import Optimization", "started", {
            "file": str(file_path)
        })

        try:
            # Read file content
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            # Analyze imports
            import_analyzer = ImportAnalyzer()
            import_analysis = import_analyzer.analyze_imports(tree, content)

            # Identify unused imports
            usage_analyzer = ImportUsageAnalyzer()
            unused_imports = usage_analyzer.find_unused_imports(tree, import_analysis["imports"])

            # Optimize import order and grouping
            optimizer = ImportStatementOptimizer(self.optimization_config["import_optimization"])
            optimized_imports = optimizer.optimize_import_statements(
                import_analysis["imports"], unused_imports
            )

            # Calculate optimization score
            optimization_score = self._calculate_import_optimization_score(
                import_analysis["imports"], optimized_imports, unused_imports
            )

            # Estimate performance gain
            performance_gain = len(unused_imports) * 0.1  # Simplified calculation

            result = ImportOptimization(
                file_path=str(file_path),
                original_imports=import_analysis["imports"],
                optimized_imports=optimized_imports,
                unused_imports=unused_imports,
                added_imports=optimizer.added_imports,
                reordered_imports=optimizer.reordered_imports,
                optimization_score=optimization_score,
                estimated_performance_gain=performance_gain
            )

            self.log_execution_step("Single File Import Optimization", "completed", {
                "unused_imports_removed": len(unused_imports),
                "optimization_score": optimization_score
            })

            return result

        except Exception as e:
            self.log_error(f"Import optimization failed for {file_path}", e)
            return self._create_empty_import_optimization(str(file_path))

    def refactor_large_files(self, file_path: str, target_size: int = 1000) -> FileRefactoring:
        """
        Refactor files exceeding target size into modular components.

        Args:
            file_path: Path to the file to refactor
            target_size: Maximum target file size in lines

        Returns:
            File refactoring result with modular breakdown
        """
        file_path = Path(file_path)

        self.log_execution_step("Large File Refactoring", "started", {
            "file": str(file_path),
            "target_size": target_size
        })

        try:
            # Analyze file size and complexity
            file_analysis = self.codebase_analyzer.analyze_file_structure(file_path)

            if file_analysis.line_count <= target_size:
                self.log_execution_step("Large File Refactoring", "completed", {
                    "action": "no_refactoring_needed",
                    "file_size": file_analysis.line_count
                })
                return self._create_empty_file_refactoring(str(file_path))

            # Use modular extractor for function/class extraction
            extraction_result = self.modular_extractor.extract_large_functions(
                str(file_path), self.optimization_config["file_refactoring"]["min_function_extraction_size"]
            )

            # Determine refactoring strategy
            strategy = self._determine_refactoring_strategy(file_analysis, extraction_result)

            # Calculate improvements
            complexity_reduction = self._calculate_complexity_reduction(file_analysis, extraction_result)
            maintainability_improvement = self._calculate_maintainability_improvement(
                file_analysis, extraction_result
            )

            # Estimate new file sizes
            estimated_new_sizes = self._estimate_refactored_file_sizes(
                file_analysis, extraction_result, strategy
            )

            target_files = [
                f"{file_path.stem}_{module.module_name}{file_path.suffix}"
                for module in extraction_result.modules_created
            ]

            result = FileRefactoring(
                source_file=str(file_path),
                original_size=file_analysis.line_count,
                target_files=target_files,
                refactoring_strategy=strategy,
                estimated_new_sizes=estimated_new_sizes,
                complexity_reduction=complexity_reduction,
                maintainability_improvement=maintainability_improvement,
                safety_score=extraction_result.safety_score
            )

            self.log_execution_step("Large File Refactoring", "completed", {
                "modules_created": len(extraction_result.modules_created),
                "complexity_reduction": complexity_reduction
            })

            return result

        except Exception as e:
            self.log_error(f"File refactoring failed for {file_path}", e)
            return self._create_empty_file_refactoring(str(file_path))

    def standardize_patterns(self, directory: str) -> List[PatternStandardization]:
        """
        Apply consistent coding patterns across codebase.

        Args:
            directory: Root directory to standardize

        Returns:
            List of pattern standardization results
        """
        self.log_execution_step("Pattern Standardization", "started", {
            "directory": directory
        })

        standardizations = []

        # Find all Python files
        python_files = list(Path(directory).glob("**/*.py"))

        for pattern_type, pattern_config in self.standard_patterns.items():
            if not self.optimization_config["pattern_standardization"].get(pattern_type, True):
                continue

            pattern_results = self._apply_pattern_standardization(
                python_files, pattern_type, pattern_config
            )
            standardizations.extend(pattern_results)

        self.log_execution_step("Pattern Standardization", "completed", {
            "patterns_applied": len(standardizations),
            "files_affected": len({ps.files_affected for ps in standardizations})
        })

        return standardizations

    # Helper methods for optimization operations

    def _identify_optimization_opportunities(self, analysis: DirectoryAnalysis) -> List[Dict[str, Any]]:
        """Identify files needing optimization"""
        opportunities = []

        for file_analysis in analysis.file_analyses:
            if not file_analysis.file_path.endswith('.py'):
                continue

            # Check for import optimization opportunities
            if len(file_analysis.dependencies) > 10:  # Many imports
                opportunities.append({
                    "type": "import_optimization",
                    "file": file_analysis.file_path,
                    "priority": "high",
                    "reason": f"Large number of imports: {len(file_analysis.dependencies)}"
                })

            # Check for large file refactoring
            if file_analysis.line_count > self.optimization_config["file_refactoring"]["max_file_size"]:
                opportunities.append({
                    "type": "file_refactoring",
                    "file": file_analysis.file_path,
                    "priority": "high",
                    "reason": f"Large file: {file_analysis.line_count} lines"
                })

            # Check for pattern standardization
            if file_analysis.modularity_score < 0.7:
                opportunities.append({
                    "type": "pattern_standardization",
                    "file": file_analysis.file_path,
                    "priority": "medium",
                    "reason": f"Low modularity score: {file_analysis.modularity_score}"
                })

        return opportunities

    def _optimize_imports(self, file_analyses: List[FileAnalysisResult]) -> List[ImportOptimization]:
        """Optimize imports across multiple files"""
        optimizations = []

        for file_analysis in file_analyses:
            if not file_analysis.file_path.endswith('.py'):
                continue

            if len(file_analysis.dependencies) > 5:  # Only optimize files with multiple imports
                optimization = self.optimize_imports(file_analysis.file_path)
                if optimization.optimization_score > self.optimization_config["quality_thresholds"]["min_optimization_score"]:
                    optimizations.append(optimization)

        return optimizations

    def _refactor_large_files(self, file_analyses: List[FileAnalysisResult]) -> List[FileRefactoring]:
        """Refactor large files across the codebase"""
        refactorings = []

        for file_analysis in file_analyses:
            if not file_analysis.file_path.endswith('.py'):
                continue

            if file_analysis.line_count > self.optimization_config["file_refactoring"]["max_file_size"]:
                refactoring = self.refactor_large_files(file_analysis.file_path)
                if refactoring.safety_score >= self.optimization_config["quality_thresholds"]["min_safety_score"]:
                    refactorings.append(refactoring)

        return refactorings

    def _standardize_patterns(self, file_analyses: List[FileAnalysisResult]) -> List[PatternStandardization]:
        """Standardize patterns across all files"""
        # Get unique directories to avoid duplicate processing
        directories = {Path(fa.file_path).parent for fa in file_analyses}

        all_standardizations = []
        for directory in directories:
            directory_standardizations = self.standardize_patterns(str(directory))
            all_standardizations.extend(directory_standardizations)

        return all_standardizations

    def _define_standard_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Define standard coding patterns for enforcement"""
        return {
            "enforce_docstrings": {
                "pattern": r"^(def|class)\s+\w+.*?:",
                "replacement": "Add docstring after definition",
                "priority": "medium"
            },
            "standardize_logging": {
                "pattern": r"print\s*\(",
                "replacement": "logger.info(",
                "priority": "high"
            },
            "enforce_type_hints": {
                "pattern": r"def\s+\w+\s*\([^)]*\)\s*:",
                "replacement": "Add type hints to function parameters",
                "priority": "medium"
            },
            "standardize_error_handling": {
                "pattern": r"except\s*:",
                "replacement": "except Exception as e:",
                "priority": "high"
            }
        }

    def _assess_quality_improvements(self, import_opts: List[ImportOptimization],
                                   file_refs: List[FileRefactoring],
                                   pattern_stds: List[PatternStandardization]) -> Dict[str, Any]:
        """Assess overall quality improvements"""

        # Calculate overall quality score
        import_score = sum(opt.optimization_score for opt in import_opts) / max(len(import_opts), 1)
        refactoring_score = sum(ref.maintainability_improvement for ref in file_refs) / max(len(file_refs), 1)
        pattern_score = sum(ps.consistency_score for ps in pattern_stds) / max(len(pattern_stds), 1)

        overall_quality_score = (import_score + refactoring_score + pattern_score) / 3

        # Calculate performance improvements
        performance_improvements = {
            "import_performance": sum(opt.estimated_performance_gain for opt in import_opts),
            "file_structure_performance": len(file_refs) * 0.1,  # Simplified
            "pattern_consistency": len(pattern_stds) * 0.05
        }

        # Calculate maintainability improvements
        maintainability_improvements = {
            "import_maintainability": len(import_opts) * 0.1,
            "file_structure_maintainability": sum(ref.maintainability_improvement for ref in file_refs),
            "pattern_consistency_maintainability": len(pattern_stds) * 0.15
        }

        return {
            "overall_quality_score": overall_quality_score,
            "performance_improvements": performance_improvements,
            "maintainability_improvements": maintainability_improvements,
            "detailed_metrics": {
                "import_optimizations": len(import_opts),
                "file_refactorings": len(file_refs),
                "pattern_standardizations": len(pattern_stds)
            }
        }

    def _create_rollback_data(self) -> Dict[str, Any]:
        """Create rollback data for optimization operations"""
        return {
            "timestamp": datetime.now().isoformat(),
            "file_backups": {},
            "optimization_log": [],
            "rollback_instructions": []
        }

    # Helper classes and utility methods continue...


class ImportAnalyzer(ast.NodeVisitor):
    """AST visitor for import analysis"""

    def __init__(self):
        self.imports = []
        self.from_imports = []

    def analyze_imports(self, tree: ast.AST, content: str) -> Dict[str, List[str]]:
        """Analyze all imports in the AST"""
        self.visit(tree)

        return {
            "imports": self.imports,
            "from_imports": self.from_imports
        }

    def visit_Import(self, node):
        """Visit import statements"""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visit from...import statements"""
        module = node.module or ""
        for alias in node.names:
            self.from_imports.append(f"from {module} import {alias.name}")
        self.generic_visit(node)


class ImportUsageAnalyzer(ast.NodeVisitor):
    """Analyzer for finding unused imports"""

    def __init__(self):
        self.used_names = set()

    def find_unused_imports(self, tree: ast.AST, imports: List[str]) -> List[str]:
        """Find imports that are not used in the code"""
        self.visit(tree)

        unused = []
        for imp in imports:
            # Simplified check - extract module name
            module_name = imp.split('.')[0]
            if module_name not in self.used_names:
                unused.append(imp)

        return unused

    def visit_Name(self, node):
        """Track name usage"""
        self.used_names.add(node.id)
        self.generic_visit(node)


class ImportStatementOptimizer:
    """Optimizer for import statements"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.added_imports = []
        self.reordered_imports = []

    def optimize_import_statements(self, imports: List[str], unused: List[str]) -> List[str]:
        """Optimize import statements according to configuration"""
        # Remove unused imports
        used_imports = [imp for imp in imports if imp not in unused]

        # Sort imports if configured
        if self.config.get("sort_imports", True):
            used_imports = sorted(used_imports)
            self.reordered_imports = used_imports

        # Group imports if configured
        if self.config.get("group_imports", True):
            used_imports = self._group_imports(used_imports)

        return used_imports

    def _group_imports(self, imports: List[str]) -> List[str]:
        """Group imports by standard library, third-party, and local"""
        standard_lib = []
        third_party = []
        local = []

        for imp in imports:
            if imp.startswith('from .') or imp.startswith('import .'):
                local.append(imp)
            elif any(imp.startswith(f'import {lib}') or imp.startswith(f'from {lib}')
                    for lib in ['os', 'sys', 'json', 'ast', 'datetime', 'pathlib']):
                standard_lib.append(imp)
            else:
                third_party.append(imp)

        # Combine with blank lines between groups
        grouped = []
        if standard_lib:
            grouped.extend(standard_lib)
        if third_party:
            if grouped:
                grouped.append("")  # Blank line
            grouped.extend(third_party)
        if local:
            if grouped:
                grouped.append("")  # Blank line
            grouped.extend(local)

        return grouped


# Additional helper methods and utility functions...

def main():
    """Main execution for testing"""
    optimizer = CodeQualityOptimizer()
    result = optimizer.execute()
    print(f"Optimization completed: {result.get('status', 'success')}")


if __name__ == "__main__":
    main()
