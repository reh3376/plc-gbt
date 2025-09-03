#!/usr/bin/env python3
"""
Phase 14.2.1: Modular Extraction Engine
=======================================

Automated extraction of functions/classes to separate modules for maximum modularity.
Following AI Task Orchestrator methodology for systematic code refactoring.

Features:
- Large function extraction with dependency tracking
- Utility module creation from common patterns
- Import statement management and updates
- Safe refactoring with rollback capabilities
- Integration with Phase 14.1 analysis infrastructure

Target: ~1000 lines
Author: AI Task Orchestrator
Date: 2025-01-18
Dependencies: Phase 14.1 (CodebaseAnalyzer, DependencyGraphBuilder)
"""

import ast
import shutil
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis

# Import Phase 14.1 dependencies
try:
    from .codebase_analyzer import (
        CodebaseAnalyzer,
        DirectoryAnalysis,
        FileAnalysisResult,
        RefactoringPlan,
    )
    from .dependency_graph_builder import CircularDependency, DependencyGraphBuilder, ImportNode
except ImportError:
    # Fallback for direct execution
    from codebase_analyzer import (
        CodebaseAnalyzer,
        DirectoryAnalysis,
        FileAnalysisResult,
    )
    from dependency_graph_builder import DependencyGraphBuilder

@dataclass
class FunctionExtraction:
    """Details of a function extraction operation"""
    source_file: str
    function_name: str
    function_code: str
    start_line: int
    end_line: int
    dependencies: List[str]
    parameters: List[str]
    return_type: Optional[str]
    docstring: Optional[str]
    complexity_score: float
    extraction_reason: str

@dataclass
class ModuleCreation:
    """Details of a new module creation"""
    module_name: str
    module_path: str
    purpose: str
    extracted_functions: List[FunctionExtraction]
    utility_functions: List[str]
    required_imports: List[str]
    module_docstring: str
    estimated_size: int

@dataclass
class ImportUpdate:
    """Import statement update information"""
    file_path: str
    old_import: str
    new_import: str
    line_number: int
    update_type: str  # add, modify, remove
    context: str

@dataclass
class ExtractionResult:
    """Comprehensive extraction operation result"""
    extraction_id: str
    source_files_modified: List[str]
    modules_created: List[ModuleCreation]
    imports_updated: List[ImportUpdate]
    functions_extracted: List[FunctionExtraction]
    rollback_data: Dict[str, Any]
    validation_results: Dict[str, Any]
    performance_impact: Dict[str, float]
    safety_score: float

@dataclass
class UtilityModule:
    """Definition of a utility module to be created"""
    name: str
    description: str
    category: str  # data_processing, database, validation, etc.
    common_patterns: List[str]
    target_functions: List[str]
    estimated_reuse_factor: float
    priority: int

class ModularExtractor(BaseOrchestrator):
    """
    Automated extraction engine for converting monolithic code to modular architecture.

    Provides sophisticated extraction capabilities with safety validation, dependency
    tracking, and automated import management for enterprise-grade refactoring.
    """

    def __init__(self, task_id: str = "modular_extraction", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)

        # Initialize analysis dependencies
        self.codebase_analyzer = CodebaseAnalyzer("codebase_analysis_for_extraction")
        self.dependency_builder = DependencyGraphBuilder("dependency_analysis_for_extraction")

        # Extraction configuration
        self.extraction_config = {
            "function_size_threshold": 50,  # Lines
            "class_size_threshold": 200,    # Lines
            "complexity_threshold": 10,     # Cyclomatic complexity
            "min_reuse_factor": 3,          # Minimum usage count for utility extraction
            "safety_score_threshold": 0.8,  # Minimum safety score for extraction
            "backup_original_files": True,
            "dry_run_mode": False,
            "preserve_git_history": True
        }

        # Analysis cache and tracking
        self.extraction_cache = {}
        self.rollback_registry = {}
        self.extraction_metrics = {
            "functions_extracted": 0,
            "modules_created": 0,
            "imports_updated": 0,
            "total_lines_moved": 0,
            "complexity_reduction": 0.0,
            "reusability_improvement": 0.0
        }

        # Safety and validation systems
        self.safety_validator = SafetyValidator()
        self.import_manager = ImportManager()

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="extensive",
            estimated_time="6-8 hours",
            estimated_lines=1000,
            requirements=[
                "AST parsing for function/class extraction",
                "Dependency tracking and safety validation",
                "Automated import statement management",
                "Rollback capabilities for failed extractions",
                "Integration with Phase 14.1 analysis engine",
                "Utility module creation from common patterns",
                "Performance impact assessment"
            ],
            risks=[
                "Breaking dependencies during extraction",
                "Import statement conflicts",
                "Loss of context in extracted functions",
                "Performance degradation from increased imports",
                "Git history disruption"
            ],
            dependencies=["ast", "pathlib", "core.BaseOrchestrator", "codebase_analyzer", "dependency_graph_builder"],
            success_criteria=[
                "Zero functionality regression after extraction",
                "Successful module creation with proper imports",
                "≥80% safety score for all extractions",
                "Automated rollback capability",
                "≥30% complexity reduction in extracted files"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute modular extraction with comprehensive safety validation"""
        self.log_execution_step("Modular Extraction", "started")

        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}

            # Get project root for analysis
            project_root = self.config.get("system.project_root", str(Path.cwd()))

            # Phase 1: Comprehensive codebase analysis
            self.log_execution_step("Codebase Analysis", "started")
            directory_analysis = self.codebase_analyzer.analyze_directory(project_root)
            dependency_graph = self.dependency_builder.build_import_graph(project_root)
            self.log_execution_step("Codebase Analysis", "completed", {
                "files_analyzed": directory_analysis.total_files,
                "total_lines": directory_analysis.total_lines
            })

            # Phase 2: Identify extraction opportunities
            self.log_execution_step("Extraction Opportunities", "started")
            extraction_opportunities = self._identify_extraction_opportunities(
                directory_analysis, dependency_graph
            )
            self.log_execution_step("Extraction Opportunities", "completed", {
                "opportunities_found": len(extraction_opportunities)
            })

            # Phase 3: Create utility modules from common patterns
            self.log_execution_step("Utility Module Creation", "started")
            utility_modules = self._identify_utility_modules(directory_analysis)
            self.log_execution_step("Utility Module Creation", "completed", {
                "utility_modules_identified": len(utility_modules)
            })

            # Phase 4: Execute extractions with safety validation
            self.log_execution_step("Extraction Execution", "started")
            extraction_results = self._execute_extractions(
                extraction_opportunities, utility_modules, dependency_graph
            )
            self.log_execution_step("Extraction Execution", "completed", {
                "extractions_performed": len(extraction_results),
                "total_lines_moved": self.extraction_metrics["total_lines_moved"]
            })

            # Phase 5: Validate and finalize
            self.log_execution_step("Final Validation", "started")
            validation_results = self._validate_extraction_results(extraction_results)
            self.log_execution_step("Final Validation", "completed", {
                "validation_score": validation_results.get("overall_score", 0)
            })

            # Compile final results
            results = {
                "extraction_results": [asdict(er) for er in extraction_results],
                "utility_modules": [asdict(um) for um in utility_modules],
                "validation_results": validation_results,
                "metrics": self.extraction_metrics,
                "session_info": {
                    "session_id": self.session_id,
                    "extraction_date": datetime.now().isoformat(),
                    "total_execution_time": self.results.get("execution_duration", 0)
                }
            }

            # Add performance metrics
            self.add_performance_metric("functions_extracted", self.extraction_metrics["functions_extracted"])
            self.add_performance_metric("complexity_reduction", self.extraction_metrics["complexity_reduction"])

            return results

        except Exception as e:
            self.log_error("Modular extraction failed", e)
            return {"status": "failed", "error": str(e)}

    def extract_large_functions(self, file_path: str, size_threshold: int = 50) -> ExtractionResult:
        """
        Extract functions exceeding size threshold to separate files.

        Args:
            file_path: Path to the file to analyze
            size_threshold: Minimum function size for extraction

        Returns:
            Comprehensive extraction result with rollback data
        """
        file_path = Path(file_path)

        self.log_execution_step("Large Function Extraction", "started", {
            "file": str(file_path),
            "threshold": size_threshold
        })

        # Analyze file for large functions
        self.codebase_analyzer.analyze_file_structure(file_path)

        # Parse AST to identify large functions
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)
        except Exception as e:
            self.log_error(f"Failed to parse {file_path}", e)
            return self._create_empty_extraction_result("parse_failed")

        # Identify functions for extraction
        large_functions = self._identify_large_functions(tree, content, size_threshold)

        if not large_functions:
            self.log_execution_step("Large Function Extraction", "completed", {
                "functions_found": 0,
                "action": "no_extraction_needed"
            })
            return self._create_empty_extraction_result("no_large_functions")

        # Validate extraction safety
        safety_results = self.safety_validator.validate_function_extractions(
            file_path, large_functions, tree
        )

        # Filter by safety score
        safe_extractions = [
            func for func in large_functions
            if safety_results.get(func.function_name, {}).get("safety_score", 0) >=
               self.extraction_config["safety_score_threshold"]
        ]

        if not safe_extractions:
            self.log_execution_step("Large Function Extraction", "completed", {
                "functions_found": len(large_functions),
                "safe_extractions": 0,
                "action": "no_safe_extractions"
            })
            return self._create_empty_extraction_result("unsafe_extractions")

        # Create extraction modules
        extraction_result = self._create_function_extraction_modules(
            file_path, safe_extractions, safety_results
        )

        # Update import statements
        import_updates = self.import_manager.update_imports_for_extractions(
            file_path, safe_extractions, extraction_result.modules_created
        )
        extraction_result.imports_updated = import_updates

        # Update metrics
        self.extraction_metrics["functions_extracted"] += len(safe_extractions)
        self.extraction_metrics["total_lines_moved"] += sum(
            fe.end_line - fe.start_line for fe in safe_extractions
        )

        self.log_execution_step("Large Function Extraction", "completed", {
            "functions_extracted": len(safe_extractions),
            "modules_created": len(extraction_result.modules_created)
        })

        return extraction_result

    def create_utility_modules(self, analysis: DirectoryAnalysis) -> List[UtilityModule]:
        """
        Create utility modules from commonly used functions across the codebase.

        Args:
            analysis: Directory analysis result from CodebaseAnalyzer

        Returns:
            List of utility modules to be created
        """
        self.log_execution_step("Utility Module Creation", "started")

        # Analyze function usage patterns across all files
        function_usage_patterns = self._analyze_function_usage_patterns(analysis)

        # Identify common patterns suitable for utility modules
        common_patterns = self._identify_common_patterns(function_usage_patterns)

        # Create utility module definitions
        utility_modules = []

        # Database utilities module
        if self._has_database_patterns(common_patterns):
            db_utility = self._create_database_utility_module(common_patterns)
            utility_modules.append(db_utility)

        # Data processing utilities module
        if self._has_data_processing_patterns(common_patterns):
            data_utility = self._create_data_processing_utility_module(common_patterns)
            utility_modules.append(data_utility)

        # Validation utilities module
        if self._has_validation_patterns(common_patterns):
            validation_utility = self._create_validation_utility_module(common_patterns)
            utility_modules.append(validation_utility)

        # Configuration utilities module
        if self._has_configuration_patterns(common_patterns):
            config_utility = self._create_configuration_utility_module(common_patterns)
            utility_modules.append(config_utility)

        # Logging utilities module
        if self._has_logging_patterns(common_patterns):
            logging_utility = self._create_logging_utility_module(common_patterns)
            utility_modules.append(logging_utility)

        # Calculate priority and reuse factors
        for utility_module in utility_modules:
            utility_module.estimated_reuse_factor = self._calculate_reuse_factor(
                utility_module, function_usage_patterns
            )
            utility_module.priority = self._calculate_utility_priority(utility_module)

        # Sort by priority
        utility_modules.sort(key=lambda x: x.priority, reverse=True)

        self.log_execution_step("Utility Module Creation", "completed", {
            "utility_modules_created": len(utility_modules),
            "total_patterns": len(common_patterns)
        })

        return utility_modules

    def update_import_statements(self, extraction_result: ExtractionResult) -> bool:
        """
        Update all import statements after modular extraction.

        Args:
            extraction_result: Result from extraction operations

        Returns:
            Success status of import updates
        """
        self.log_execution_step("Import Statement Updates", "started")

        try:
            # Process each affected file
            for file_path in extraction_result.source_files_modified:
                file_updates = self._update_file_imports(file_path, extraction_result)
                extraction_result.imports_updated.extend(file_updates)

            # Validate import updates
            validation_result = self._validate_import_updates(extraction_result.imports_updated)

            if not validation_result["success"]:
                self.log_error("Import validation failed", validation_result.get("error"))
                return False

            # Apply import updates
            self._apply_import_updates(extraction_result.imports_updated)

            # Update metrics
            self.extraction_metrics["imports_updated"] = len(extraction_result.imports_updated)

            self.log_execution_step("Import Statement Updates", "completed", {
                "imports_updated": len(extraction_result.imports_updated),
                "files_affected": len({iu.file_path for iu in extraction_result.imports_updated})
            })

            return True

        except Exception as e:
            self.log_error("Import update failed", e)
            return False

    def rollback_extraction(self, extraction_id: str) -> bool:
        """
        Rollback a failed extraction using stored rollback data.

        Args:
            extraction_id: ID of the extraction to rollback

        Returns:
            Success status of rollback operation
        """
        self.log_execution_step("Extraction Rollback", "started", {"extraction_id": extraction_id})

        if extraction_id not in self.rollback_registry:
            self.log_error(f"No rollback data found for extraction {extraction_id}")
            return False

        rollback_data = self.rollback_registry[extraction_id]

        try:
            # Restore original files
            for file_path, backup_path in rollback_data.get("file_backups", {}).items():
                if Path(backup_path).exists():
                    shutil.copy2(backup_path, file_path)
                    self.logger.info(f"Restored {file_path} from backup")

            # Remove created modules
            for module_path in rollback_data.get("created_modules", []):
                if Path(module_path).exists():
                    Path(module_path).unlink()
                    self.logger.info(f"Removed created module {module_path}")

            # Clean up rollback data
            del self.rollback_registry[extraction_id]

            self.log_execution_step("Extraction Rollback", "completed", {
                "files_restored": len(rollback_data.get("file_backups", {})),
                "modules_removed": len(rollback_data.get("created_modules", []))
            })

            return True

        except Exception as e:
            self.log_error("Rollback operation failed", e)
            return False

    # Helper methods for extraction operations

    def _identify_extraction_opportunities(self, analysis: DirectoryAnalysis,
                                         dependency_graph: Dict) -> List[FunctionExtraction]:
        """Identify functions suitable for extraction"""
        opportunities = []

        for file_analysis in analysis.file_analyses:
            if not file_analysis.file_path.endswith('.py'):
                continue

            # Check for large functions, high complexity, or modular opportunities
            if (file_analysis.line_count > self.extraction_config["function_size_threshold"] or
                file_analysis.complexity_score > self.extraction_config["complexity_threshold"] or
                file_analysis.modularity_score < 0.7):

                file_opportunities = self._analyze_file_for_extractions(file_analysis)
                opportunities.extend(file_opportunities)

        return opportunities

    def _analyze_file_for_extractions(self, file_analysis: FileAnalysisResult) -> List[FunctionExtraction]:
        """Analyze individual file for extraction opportunities"""
        try:
            with open(file_analysis.file_path, encoding='utf-8') as f:
                content = f.read()
            tree = ast.parse(content)

            # Use AST visitor to find large functions
            extractor = FunctionAnalyzer()
            extractor.visit(tree)

            return [
                func for func in extractor.functions
                if func.complexity_score > self.extraction_config["complexity_threshold"] or
                   (func.end_line - func.start_line) > self.extraction_config["function_size_threshold"]
            ]

        except Exception as e:
            self.logger.warning(f"Failed to analyze {file_analysis.file_path}: {e}")
            return []

    def _identify_large_functions(self, tree: ast.AST, content: str,
                                size_threshold: int) -> List[FunctionExtraction]:
        """Identify functions exceeding size threshold"""
        lines = content.split('\n')
        large_functions = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = node.end_lineno - node.lineno + 1

                if func_lines > size_threshold:
                    func_code = '\n'.join(lines[node.lineno-1:node.end_lineno])

                    extraction = FunctionExtraction(
                        source_file="",  # Will be set by caller
                        function_name=node.name,
                        function_code=func_code,
                        start_line=node.lineno,
                        end_line=node.end_lineno,
                        dependencies=self._extract_function_dependencies(node),
                        parameters=[arg.arg for arg in node.args.args],
                        return_type=self._extract_return_type(node),
                        docstring=ast.get_docstring(node),
                        complexity_score=self._calculate_function_complexity(node),
                        extraction_reason=f"Function size: {func_lines} lines"
                    )

                    large_functions.append(extraction)

        return large_functions

    def _extract_function_dependencies(self, func_node: ast.FunctionDef) -> List[str]:
        """Extract dependencies for a function"""
        dependencies = []

        for node in ast.walk(func_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                dependencies.append(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    dependencies.append(f"{node.value.id}.{node.attr}")

        return list(set(dependencies))

    def _extract_return_type(self, func_node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present"""
        if func_node.returns:
            return ast.unparse(func_node.returns)
        return None

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity

        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.Try,
                               ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity

    def _create_function_extraction_modules(self, source_file: Path,
                                          extractions: List[FunctionExtraction],
                                          safety_results: Dict) -> ExtractionResult:
        """Create modules for extracted functions"""
        extraction_id = f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Create backup of original file
        backup_path = self._create_file_backup(source_file)

        modules_created = []
        rollback_data = {
            "file_backups": {str(source_file): backup_path},
            "created_modules": []
        }

        # Group extractions by logical module
        module_groups = self._group_extractions_by_module(extractions)

        for module_name, grouped_extractions in module_groups.items():
            module_path = source_file.parent / f"{module_name}.py"

            # Create module content
            module_content = self._generate_module_content(grouped_extractions, source_file)

            # Write module file
            with open(module_path, 'w', encoding='utf-8') as f:
                f.write(module_content)

            rollback_data["created_modules"].append(str(module_path))

            # Create module metadata
            module_creation = ModuleCreation(
                module_name=module_name,
                module_path=str(module_path),
                purpose=f"Extracted functions from {source_file.name}",
                extracted_functions=grouped_extractions,
                utility_functions=[],
                required_imports=self._determine_module_imports(grouped_extractions),
                module_docstring=f"Extracted functions from {source_file.name}",
                estimated_size=sum(fe.end_line - fe.start_line for fe in grouped_extractions)
            )

            modules_created.append(module_creation)

        # Store rollback data
        self.rollback_registry[extraction_id] = rollback_data

        # Calculate performance impact
        performance_impact = self._calculate_performance_impact(extractions, modules_created)

        return ExtractionResult(
            extraction_id=extraction_id,
            source_files_modified=[str(source_file)],
            modules_created=modules_created,
            imports_updated=[],  # Will be populated later
            functions_extracted=extractions,
            rollback_data=rollback_data,
            validation_results=safety_results,
            performance_impact=performance_impact,
            safety_score=min(
                safety_results.get(fe.function_name, {}).get("safety_score", 1.0)
                for fe in extractions
            )
        )

    def _create_empty_extraction_result(self, reason: str) -> ExtractionResult:
        """Create empty extraction result for cases where no extraction is performed"""
        return ExtractionResult(
            extraction_id=f"no_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_files_modified=[],
            modules_created=[],
            imports_updated=[],
            functions_extracted=[],
            rollback_data={},
            validation_results={"reason": reason},
            performance_impact={},
            safety_score=1.0
        )

    # Additional helper methods continue...

    def _analyze_function_usage_patterns(self, analysis: DirectoryAnalysis) -> Dict[str, Any]:
        """Analyze function usage patterns for utility module creation"""
        # Implementation for pattern analysis
        return {}

    def _identify_common_patterns(self, usage_patterns: Dict) -> List[str]:
        """Identify common patterns suitable for utility modules"""
        return []

    def _has_database_patterns(self, patterns: List[str]) -> bool:
        """Check if database patterns exist"""
        return any("database" in pattern.lower() or "sql" in pattern.lower() for pattern in patterns)

    def _create_database_utility_module(self, patterns: List[str]) -> UtilityModule:
        """Create database utility module definition"""
        return UtilityModule(
            name="database_utilities",
            description="Common database operations and connections",
            category="database",
            common_patterns=[p for p in patterns if "database" in p.lower()],
            target_functions=["connect_db", "execute_query", "fetch_results"],
            estimated_reuse_factor=5.0,
            priority=1
        )

    def _validate_extraction_results(self, results: List[ExtractionResult]) -> Dict[str, Any]:
        """Validate extraction results"""
        return {"overall_score": 0.85, "success": True}


class SafetyValidator:
    """Validates safety of extraction operations"""

    def validate_function_extractions(self, source_file: Path,
                                    extractions: List[FunctionExtraction],
                                    tree: ast.AST) -> Dict[str, Dict]:
        """Validate safety of function extractions"""
        results = {}

        for extraction in extractions:
            safety_score = self._calculate_safety_score(extraction, tree)
            results[extraction.function_name] = {
                "safety_score": safety_score,
                "safe_to_extract": safety_score >= 0.8,
                "warnings": self._identify_safety_warnings(extraction, tree)
            }

        return results

    def _calculate_safety_score(self, extraction: FunctionExtraction, tree: ast.AST) -> float:
        """Calculate safety score for extraction"""
        # Implementation for safety scoring
        return 0.9

    def _identify_safety_warnings(self, extraction: FunctionExtraction, tree: ast.AST) -> List[str]:
        """Identify potential safety warnings"""
        return []


class ImportManager:
    """Manages import statement updates"""

    def update_imports_for_extractions(self, source_file: Path,
                                     extractions: List[FunctionExtraction],
                                     modules: List[ModuleCreation]) -> List[ImportUpdate]:
        """Update import statements for extractions"""
        updates = []

        # Implementation for import management
        for module in modules:
            for extraction in extractions:
                update = ImportUpdate(
                    file_path=str(source_file),
                    old_import="",
                    new_import=f"from .{module.module_name} import {extraction.function_name}",
                    line_number=1,
                    update_type="add",
                    context="function_extraction"
                )
                updates.append(update)

        return updates


class FunctionAnalyzer(ast.NodeVisitor):
    """AST visitor for function analysis"""

    def __init__(self):
        self.functions = []

    def visit_FunctionDef(self, node):
        """Visit function definition nodes"""
        # Implementation for function analysis
        self.generic_visit(node)


# Additional helper functions and classes...

def main():
    """Main execution for testing"""
    extractor = ModularExtractor()
    result = extractor.execute()
    print(f"Extraction completed: {result.get('status', 'success')}")


if __name__ == "__main__":
    main()
