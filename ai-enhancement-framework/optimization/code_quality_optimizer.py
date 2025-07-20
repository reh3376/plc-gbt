#!/usr/bin/env python3
"""
AI Enhancement Framework - Code Quality Optimizer
=================================================

Automated code quality improvements for enterprise-grade refactoring.
Following AI Task Orchestrator methodology for systematic code optimization.

Features:
- Import statement optimization (remove unused, sort, group)
- Large file refactoring into modular components
- Consistent coding pattern standardization
- Code style enforcement and cleanup
- Performance optimization recommendations
- Integration with modular extraction engine

Author: AI Enhancement Framework
Version: 1.0.0
"""

import ast
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import tempfile
import shutil
from collections import defaultdict, Counter
import importlib.util

# Framework imports
from ..core.task_orchestrator import BaseOrchestrator, TaskAnalysis
from .codebase_analyzer import CodebaseAnalyzer, FileAnalysisResult, DirectoryAnalysis
from .modular_extractor import ModularExtractor, FunctionExtraction

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
class PatternStandardization:
    """Details of coding pattern standardization"""
    file_path: str
    patterns_found: List[str]
    patterns_standardized: List[str]
    changes_made: List[str]
    quality_improvement_score: float
    before_complexity: float
    after_complexity: float

@dataclass
class OptimizationResult:
    """Comprehensive optimization result"""
    optimization_id: str
    files_processed: List[str]
    import_optimizations: List[ImportOptimization]
    pattern_standardizations: List[PatternStandardization]
    performance_improvements: Dict[str, float]
    quality_metrics: Dict[str, float]
    rollback_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    overall_score: float

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
                "prefer_from_imports": True,
                "group_order": ["standard", "third_party", "local"]
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
                "consistent_naming": True,
                "remove_dead_code": True,
                "optimize_loops": True
            },
            "quality_thresholds": {
                "min_optimization_score": 0.7,
                "min_safety_score": 0.8,
                "max_complexity_per_function": 10
            },
            "style_preferences": {
                "line_length": 88,
                "indent_size": 4,
                "quote_style": "double",
                "trailing_commas": True
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

    def optimize_imports(self, file_path: str) -> ImportOptimization:
        """
        Optimize import statements (remove unused, sort, group).
        
        Args:
            file_path: Path to file to optimize
            
        Returns:
            Import optimization result
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            lines = content.splitlines()
            
            # Extract current imports
            current_imports = self._extract_imports(tree)
            
            # Find unused imports
            unused_imports = self._find_unused_imports(tree, current_imports)
            
            # Group and sort imports
            grouped_imports = self._group_imports(current_imports, unused_imports)
            
            # Generate optimized import section
            optimized_imports = self._generate_optimized_imports(grouped_imports)
            
            # Calculate optimization score
            optimization_score = self._calculate_import_optimization_score(
                current_imports, optimized_imports, unused_imports
            )
            
            # Estimate performance gain
            performance_gain = len(unused_imports) * 0.01  # Small gain per unused import
            
            return ImportOptimization(
                file_path=file_path,
                original_imports=[imp["line"] for imp in current_imports],
                optimized_imports=optimized_imports,
                unused_imports=[imp["module"] for imp in unused_imports],
                added_imports=[],
                reordered_imports=[],
                optimization_score=optimization_score,
                estimated_performance_gain=performance_gain
            )
            
        except Exception as e:
            self.log(f"Error optimizing imports for {file_path}: {e}", "error")
            return self._create_empty_import_optimization(file_path, str(e))

    def refactor_large_files(self, file_path: str, target_size: int = None) -> OptimizationResult:
        """
        Refactor files exceeding target size into modular components.
        
        Args:
            file_path: Path to file to refactor
            target_size: Target file size (default from config)
            
        Returns:
            Comprehensive refactoring result
        """
        if target_size is None:
            target_size = self.optimization_config["file_refactoring"]["max_file_size"]
        
        optimization_id = self._generate_optimization_id()
        
        try:
            # Analyze file
            file_analysis = self.codebase_analyzer.analyze_file_structure(file_path)
            
            if file_analysis.line_count <= target_size:
                return self._create_empty_optimization_result(
                    optimization_id, f"File size ({file_analysis.line_count}) within target ({target_size})"
                )
            
            # Use modular extractor for large functions
            extraction_result = self.modular_extractor.extract_large_functions(
                file_path, 
                self.optimization_config["file_refactoring"]["min_function_extraction_size"]
            )
            
            # Optimize imports in the refactored file
            import_optimization = self.optimize_imports(file_path)
            
            # Standardize patterns
            pattern_standardization = self.standardize_patterns(file_path)
            
            # Calculate overall metrics
            performance_improvements = {
                "lines_reduced": sum(len(f.function_code.splitlines()) for f in extraction_result.functions_extracted),
                "complexity_reduction": extraction_result.performance_impact.get("complexity_reduction", 0.0),
                "modularity_improvement": extraction_result.performance_impact.get("modularity_improvement", 0.0)
            }
            
            quality_metrics = {
                "import_score": import_optimization.optimization_score,
                "pattern_score": pattern_standardization.quality_improvement_score,
                "extraction_safety": extraction_result.safety_score
            }
            
            overall_score = sum(quality_metrics.values()) / len(quality_metrics)
            
            return OptimizationResult(
                optimization_id=optimization_id,
                files_processed=[file_path],
                import_optimizations=[import_optimization],
                pattern_standardizations=[pattern_standardization],
                performance_improvements=performance_improvements,
                quality_metrics=quality_metrics,
                rollback_data=extraction_result.rollback_data,
                validation_results=extraction_result.validation_results,
                overall_score=overall_score
            )
            
        except Exception as e:
            self.log(f"Error refactoring file {file_path}: {e}", "error")
            raise

    def standardize_patterns(self, file_path: str) -> PatternStandardization:
        """
        Apply consistent coding patterns across the file.
        
        Args:
            file_path: Path to file to standardize
            
        Returns:
            Pattern standardization result
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            tree = ast.parse(content)
            
            # Track changes
            changes_made = []
            patterns_found = []
            patterns_standardized = []
            
            # Calculate initial complexity
            before_complexity = self._calculate_file_complexity(tree)
            
            # Apply standardizations
            if self.optimization_config["pattern_standardization"]["enforce_docstrings"]:
                content, docstring_changes = self._enforce_docstrings(content, tree)
                changes_made.extend(docstring_changes)
                if docstring_changes:
                    patterns_found.append("Missing docstrings")
                    patterns_standardized.append("Added docstrings")
            
            if self.optimization_config["pattern_standardization"]["standardize_logging"]:
                content, logging_changes = self._standardize_logging(content)
                changes_made.extend(logging_changes)
                if logging_changes:
                    patterns_found.append("Inconsistent logging")
                    patterns_standardized.append("Standardized logging")
            
            if self.optimization_config["pattern_standardization"]["standardize_error_handling"]:
                content, error_changes = self._standardize_error_handling(content, tree)
                changes_made.extend(error_changes)
                if error_changes:
                    patterns_found.append("Inconsistent error handling")
                    patterns_standardized.append("Standardized error handling")
            
            if self.optimization_config["pattern_standardization"]["remove_dead_code"]:
                content, dead_code_changes = self._remove_dead_code(content, tree)
                changes_made.extend(dead_code_changes)
                if dead_code_changes:
                    patterns_found.append("Dead code")
                    patterns_standardized.append("Removed dead code")
            
            if self.optimization_config["pattern_standardization"]["optimize_loops"]:
                content, loop_changes = self._optimize_loops(content, tree)
                changes_made.extend(loop_changes)
                if loop_changes:
                    patterns_found.append("Inefficient loops")
                    patterns_standardized.append("Optimized loops")
            
            # Calculate final complexity
            try:
                final_tree = ast.parse(content)
                after_complexity = self._calculate_file_complexity(final_tree)
            except SyntaxError:
                after_complexity = before_complexity
            
            # Calculate quality improvement
            quality_improvement = max(0.0, (before_complexity - after_complexity) / max(before_complexity, 0.1))
            
            # Write optimized content
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return PatternStandardization(
                file_path=file_path,
                patterns_found=patterns_found,
                patterns_standardized=patterns_standardized,
                changes_made=changes_made,
                quality_improvement_score=min(1.0, quality_improvement + 0.1 * len(patterns_standardized)),
                before_complexity=before_complexity,
                after_complexity=after_complexity
            )
            
        except Exception as e:
            self.log(f"Error standardizing patterns for {file_path}: {e}", "error")
            return self._create_empty_pattern_standardization(file_path, str(e))

    def optimize_directory(self, directory_path: str) -> List[OptimizationResult]:
        """
        Optimize all files in a directory.
        
        Args:
            directory_path: Path to directory to optimize
            
        Returns:
            List of optimization results
        """
        directory_analysis = self.codebase_analyzer.analyze_directory(directory_path)
        optimization_results = []
        
        for file_analysis in directory_analysis.file_analyses:
            if file_analysis.file_path.endswith('.py'):
                try:
                    # Optimize individual file
                    if file_analysis.line_count > self.optimization_config["file_refactoring"]["max_file_size"]:
                        result = self.refactor_large_files(file_analysis.file_path)
                    else:
                        # Just optimize imports and patterns for smaller files
                        import_opt = self.optimize_imports(file_analysis.file_path)
                        pattern_std = self.standardize_patterns(file_analysis.file_path)
                        
                        result = OptimizationResult(
                            optimization_id=self._generate_optimization_id(),
                            files_processed=[file_analysis.file_path],
                            import_optimizations=[import_opt],
                            pattern_standardizations=[pattern_std],
                            performance_improvements={},
                            quality_metrics={
                                "import_score": import_opt.optimization_score,
                                "pattern_score": pattern_std.quality_improvement_score
                            },
                            rollback_data={},
                            validation_results={},
                            overall_score=(import_opt.optimization_score + pattern_std.quality_improvement_score) / 2
                        )
                    
                    optimization_results.append(result)
                    
                except Exception as e:
                    self.log(f"Error optimizing {file_analysis.file_path}: {e}", "error")
                    continue
        
        return optimization_results

    def _extract_imports(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """Extract all import statements from AST"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        "type": "import",
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""),
                        "lineno": node.lineno
                    })
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append({
                        "type": "from",
                        "module": module,
                        "name": alias.name,
                        "alias": alias.asname,
                        "line": f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""),
                        "lineno": node.lineno
                    })
        
        return imports

    def _find_unused_imports(self, tree: ast.AST, imports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find unused import statements"""
        # Collect all names used in the code
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Handle module.attribute access
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        # Check which imports are unused
        unused_imports = []
        
        for imp in imports:
            if imp["type"] == "import":
                import_name = imp["alias"] if imp["alias"] else imp["module"].split('.')[0]
                if import_name not in used_names:
                    unused_imports.append(imp)
            elif imp["type"] == "from":
                import_name = imp["alias"] if imp["alias"] else imp["name"]
                if import_name not in used_names:
                    unused_imports.append(imp)
        
        return unused_imports

    def _group_imports(self, imports: List[Dict[str, Any]], 
                      unused_imports: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Group imports by type (standard, third-party, local)"""
        import sys
        standard_library = set(sys.stdlib_module_names) if hasattr(sys, 'stdlib_module_names') else {
            'os', 'sys', 'json', 'datetime', 'pathlib', 'typing', 're', 'ast', 'collections'
        }
        
        unused_modules = {imp["module"] for imp in unused_imports}
        
        groups = {
            "standard": [],
            "third_party": [],
            "local": []
        }
        
        for imp in imports:
            if imp["module"] in unused_modules:
                continue  # Skip unused imports
            
            module_root = imp["module"].split('.')[0]
            
            if module_root in standard_library:
                groups["standard"].append(imp["line"])
            elif module_root.startswith('.') or module_root in ['modules', 'utils', 'core']:
                groups["local"].append(imp["line"])
            else:
                groups["third_party"].append(imp["line"])
        
        # Sort within each group
        for group in groups.values():
            group.sort()
        
        return groups

    def _generate_optimized_imports(self, grouped_imports: Dict[str, List[str]]) -> List[str]:
        """Generate optimized import section"""
        optimized = []
        
        for group_name in self.optimization_config["import_optimization"]["group_order"]:
            if grouped_imports[group_name]:
                if optimized:  # Add blank line between groups
                    optimized.append("")
                optimized.extend(grouped_imports[group_name])
        
        return optimized

    def _calculate_import_optimization_score(self, original: List[Dict[str, Any]], 
                                           optimized: List[str], 
                                           unused: List[Dict[str, Any]]) -> float:
        """Calculate import optimization score"""
        score = 0.8  # Base score
        
        # Bonus for removing unused imports
        if unused:
            score += 0.1 * min(len(unused), 5) / 5  # Up to 0.1 for removing unused
        
        # Bonus for organization
        if len(optimized) > 0:
            score += 0.1  # Organized imports
        
        return min(1.0, score)

    def _enforce_docstrings(self, content: str, tree: ast.AST) -> Tuple[str, List[str]]:
        """Add missing docstrings to functions and classes"""
        changes = []
        lines = content.splitlines()
        
        # Find functions and classes without docstrings
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    # Add basic docstring
                    indent = self._get_indentation(lines, node.lineno - 1)
                    docstring_lines = [
                        f'{indent}    """',
                        f'{indent}    {node.name.replace("_", " ").title()}.',
                        f'{indent}    """'
                    ]
                    
                    # Insert after function/class definition
                    insert_line = node.lineno  # ast.lineno is 1-based
                    for i, docstring_line in enumerate(docstring_lines):
                        lines.insert(insert_line + i, docstring_line)
                    
                    changes.append(f"Added docstring to {node.name}")
        
        return '\n'.join(lines), changes

    def _standardize_logging(self, content: str) -> Tuple[str, List[str]]:
        """Standardize logging statements"""
        changes = []
        
        # Replace print statements with logging
        if 'print(' in content:
            # Simple replacement - in practice, you'd want more sophisticated parsing
            content = re.sub(r'print\((.*?)\)', r'logger.info(\1)', content)
            changes.append("Replaced print statements with logging")
        
        # Ensure logging import is present
        if 'logger.info' in content and 'import logging' not in content:
            lines = content.splitlines()
            # Find import section
            import_line = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('import ') or line.strip().startswith('from '):
                    import_line = i + 1
            
            lines.insert(import_line, 'import logging')
            lines.insert(import_line + 1, '')
            lines.insert(import_line + 2, 'logger = logging.getLogger(__name__)')
            content = '\n'.join(lines)
            changes.append("Added logging import and logger setup")
        
        return content, changes

    def _standardize_error_handling(self, content: str, tree: ast.AST) -> Tuple[str, List[str]]:
        """Standardize error handling patterns"""
        changes = []
        
        # Look for bare except clauses
        bare_except_pattern = r'except:\s*$'
        if re.search(bare_except_pattern, content, re.MULTILINE):
            content = re.sub(bare_except_pattern, 'except Exception as e:', content)
            changes.append("Replaced bare except clauses with specific exception handling")
        
        return content, changes

    def _remove_dead_code(self, content: str, tree: ast.AST) -> Tuple[str, List[str]]:
        """Remove dead code patterns"""
        changes = []
        
        # Remove multiple blank lines
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        if '\\n\\n\\n' in repr(content):
            changes.append("Removed excessive blank lines")
        
        # Remove trailing whitespace
        lines = content.splitlines()
        cleaned_lines = [line.rstrip() for line in lines]
        if lines != cleaned_lines:
            content = '\n'.join(cleaned_lines)
            changes.append("Removed trailing whitespace")
        
        return content, changes

    def _optimize_loops(self, content: str, tree: ast.AST) -> Tuple[str, List[str]]:
        """Optimize loop patterns"""
        changes = []
        
        # Look for range(len()) patterns that could be enumerate
        range_len_pattern = r'for\s+(\w+)\s+in\s+range\(len\((\w+)\)\):'
        if re.search(range_len_pattern, content):
            # This is a simplified replacement - in practice needs more careful parsing
            content = re.sub(
                range_len_pattern, 
                r'for \1, item in enumerate(\2):',
                content
            )
            changes.append("Optimized range(len()) loops to use enumerate")
        
        return content, changes

    def _calculate_file_complexity(self, tree: ast.AST) -> float:
        """Calculate cyclomatic complexity of entire file"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity

    def _get_indentation(self, lines: List[str], line_num: int) -> str:
        """Get indentation of a specific line"""
        if line_num < len(lines):
            line = lines[line_num]
            return line[:len(line) - len(line.lstrip())]
        return ""

    def _generate_optimization_id(self) -> str:
        """Generate unique optimization ID"""
        return f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now())) % 10000:04d}"

    def _create_empty_import_optimization(self, file_path: str, error: str) -> ImportOptimization:
        """Create empty import optimization result"""
        return ImportOptimization(
            file_path=file_path,
            original_imports=[],
            optimized_imports=[],
            unused_imports=[],
            added_imports=[],
            reordered_imports=[],
            optimization_score=0.0,
            estimated_performance_gain=0.0
        )

    def _create_empty_pattern_standardization(self, file_path: str, error: str) -> PatternStandardization:
        """Create empty pattern standardization result"""
        return PatternStandardization(
            file_path=file_path,
            patterns_found=[f"Error: {error}"],
            patterns_standardized=[],
            changes_made=[],
            quality_improvement_score=0.0,
            before_complexity=0.0,
            after_complexity=0.0
        )

    def _create_empty_optimization_result(self, optimization_id: str, reason: str) -> OptimizationResult:
        """Create empty optimization result"""
        return OptimizationResult(
            optimization_id=optimization_id,
            files_processed=[],
            import_optimizations=[],
            pattern_standardizations=[],
            performance_improvements={},
            quality_metrics={},
            rollback_data={},
            validation_results={"message": reason},
            overall_score=1.0
        ) 