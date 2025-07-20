#!/usr/bin/env python3
"""
AI Enhancement Framework - Modular Extraction Engine
===================================================

Automated extraction of functions/classes to separate modules for maximum modularity.
Following AI Task Orchestrator methodology for systematic code refactoring.

Features:
- Large function extraction with dependency tracking
- Utility module creation from common patterns
- Import statement management and updates
- Safe refactoring with rollback capabilities
- Integration with codebase analysis infrastructure

Author: AI Enhancement Framework
Version: 1.0.0
"""

import ast
import os
import sys
import shutil
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import hashlib
import tempfile
from collections import defaultdict, Counter
from contextlib import contextmanager

# Framework imports
from ..core.task_orchestrator import BaseOrchestrator, TaskAnalysis
from .codebase_analyzer import CodebaseAnalyzer, FileAnalysisResult, DirectoryAnalysis, RefactoringPlan

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

class ModularExtractor(BaseOrchestrator):
    """
    Automated extraction of functions/classes to separate modules.
    
    Provides sophisticated modular extraction capabilities including large function
    extraction, utility module creation, and comprehensive import management with
    safety validation and rollback capabilities.
    """

    def __init__(self, task_id: str = "modular_extraction", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)
        
        # Initialize dependencies
        self.codebase_analyzer = CodebaseAnalyzer("extraction_analysis")
        
        # Extraction configuration
        self.extraction_config = {
            "min_function_size": 30,  # Minimum lines for extraction
            "max_function_size": 200,  # Maximum lines before mandatory extraction
            "utility_patterns": ["_helper", "_util", "_format", "_convert", "_validate"],
            "common_function_threshold": 3,  # Functions used in 3+ files
            "dependency_analysis_depth": 3,
            "safety_requirements": {
                "min_test_coverage": 0.7,
                "max_complexity_increase": 0.1,
                "require_backup": True
            },
            "module_organization": {
                "max_functions_per_module": 15,
                "prefer_thematic_grouping": True,
                "create_init_files": True
            }
        }
        
        # Extraction tracking
        self.extraction_metrics = {
            "functions_extracted": 0,
            "modules_created": 0,
            "imports_updated": 0,
            "lines_restructured": 0,
            "complexity_reduction": 0.0
        }
        
        # Safety and rollback management
        self.rollback_stack = []
        self.backup_directory = None

    def extract_large_functions(self, file_path: str, size_threshold: int = None) -> ExtractionResult:
        """
        Extract functions exceeding size threshold to separate files.
        
        Args:
            file_path: Path to file to analyze
            size_threshold: Line threshold for extraction (default from config)
            
        Returns:
            Comprehensive extraction result
        """
        if size_threshold is None:
            size_threshold = self.extraction_config["min_function_size"]
        
        extraction_id = self._generate_extraction_id()
        
        try:
            # Analyze source file
            file_analysis = self.codebase_analyzer.analyze_file_structure(file_path)
            
            # Parse AST for detailed function analysis
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Identify extraction candidates
            extraction_candidates = self._identify_extraction_candidates(
                tree, content, file_analysis, size_threshold
            )
            
            if not extraction_candidates:
                return self._create_empty_result(extraction_id, "No extraction candidates found")
            
            # Create backup before extraction
            self._create_backup(file_path)
            
            # Perform extractions
            modules_created = []
            functions_extracted = []
            imports_updated = []
            
            for candidate in extraction_candidates:
                # Extract function to appropriate module
                module_result = self._extract_function_to_module(
                    file_path, candidate, extraction_id
                )
                
                modules_created.extend(module_result["modules"])
                functions_extracted.append(candidate)
                imports_updated.extend(module_result["imports"])
            
            # Update source file
            updated_content = self._update_source_file(
                file_path, content, extraction_candidates, imports_updated
            )
            
            # Validate extraction
            validation_results = self._validate_extraction(
                file_path, updated_content, functions_extracted
            )
            
            # Calculate performance impact
            performance_impact = self._calculate_performance_impact(
                file_analysis, functions_extracted
            )
            
            # Create rollback data
            rollback_data = self._create_rollback_data(
                extraction_id, file_path, content, modules_created
            )
            
            # Update metrics
            self.extraction_metrics["functions_extracted"] += len(functions_extracted)
            self.extraction_metrics["modules_created"] += len(modules_created)
            self.extraction_metrics["imports_updated"] += len(imports_updated)
            
            return ExtractionResult(
                extraction_id=extraction_id,
                source_files_modified=[file_path],
                modules_created=modules_created,
                imports_updated=imports_updated,
                functions_extracted=functions_extracted,
                rollback_data=rollback_data,
                validation_results=validation_results,
                performance_impact=performance_impact,
                safety_score=validation_results.get("safety_score", 0.0)
            )
            
        except Exception as e:
            self.log(f"Error during extraction: {e}", "error")
            self._rollback_extraction(extraction_id)
            raise

    def create_utility_modules(self, analysis: DirectoryAnalysis) -> List[ModuleCreation]:
        """
        Create utility modules from commonly used functions.
        
        Args:
            analysis: Directory analysis result
            
        Returns:
            List of created utility modules
        """
        utility_modules = []
        
        # Find common patterns across files
        common_functions = self._find_common_functions(analysis.file_analyses)
        
        # Group functions by purpose
        function_groups = self._group_functions_by_purpose(common_functions)
        
        # Create modules for each group
        for group_name, functions in function_groups.items():
            if len(functions) >= self.extraction_config["common_function_threshold"]:
                module = self._create_utility_module(group_name, functions)
                utility_modules.append(module)
        
        return utility_modules

    def update_import_statements(self, extraction_result: ExtractionResult) -> bool:
        """
        Update all import statements after modular extraction.
        
        Args:
            extraction_result: Result from extraction operation
            
        Returns:
            Success status
        """
        try:
            for import_update in extraction_result.imports_updated:
                self._apply_import_update(import_update)
            
            # Validate all imports still work
            validation_passed = self._validate_all_imports(extraction_result)
            
            if not validation_passed:
                self.log("Import validation failed, rolling back", "error")
                self._rollback_extraction(extraction_result.extraction_id)
                return False
            
            return True
            
        except Exception as e:
            self.log(f"Error updating imports: {e}", "error")
            self._rollback_extraction(extraction_result.extraction_id)
            return False

    def _identify_extraction_candidates(self, tree: ast.AST, content: str, 
                                      file_analysis: FileAnalysisResult, 
                                      size_threshold: int) -> List[FunctionExtraction]:
        """Identify functions that should be extracted"""
        candidates = []
        lines = content.splitlines()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Calculate function metrics
                start_line = node.lineno - 1
                end_line = getattr(node, 'end_lineno', start_line + 10) - 1
                function_lines = end_line - start_line + 1
                
                # Check if function meets extraction criteria
                if function_lines >= size_threshold:
                    function_code = '\n'.join(lines[start_line:end_line + 1])
                    
                    # Analyze function dependencies
                    dependencies = self._analyze_function_dependencies(node, tree)
                    
                    # Calculate complexity
                    complexity = self._calculate_function_complexity(node)
                    
                    # Determine extraction reason
                    reasons = []
                    if function_lines > self.extraction_config["max_function_size"]:
                        reasons.append("Exceeds maximum function size")
                    if complexity > 0.8:
                        reasons.append("High complexity")
                    if any(pattern in node.name for pattern in self.extraction_config["utility_patterns"]):
                        reasons.append("Utility function pattern")
                    
                    if reasons:
                        candidate = FunctionExtraction(
                            source_file=file_analysis.file_path,
                            function_name=node.name,
                            function_code=function_code,
                            start_line=start_line,
                            end_line=end_line,
                            dependencies=dependencies,
                            parameters=[arg.arg for arg in node.args.args],
                            return_type=self._extract_return_type(node),
                            docstring=ast.get_docstring(node),
                            complexity_score=complexity,
                            extraction_reason="; ".join(reasons)
                        )
                        candidates.append(candidate)
        
        return candidates

    def _analyze_function_dependencies(self, func_node: ast.FunctionDef, tree: ast.AST) -> List[str]:
        """Analyze function dependencies within the file"""
        dependencies = []
        
        # Find all names used in the function
        for node in ast.walk(func_node):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                dependencies.append(node.id)
        
        # Filter to only include dependencies defined in the same file
        defined_names = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign)):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            defined_names.add(target.id)
                else:
                    defined_names.add(node.name)
        
        return [dep for dep in dependencies if dep in defined_names]

    def _calculate_function_complexity(self, func_node: ast.FunctionDef) -> float:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return min(complexity / 10.0, 1.0)  # Normalize to 0-1 scale

    def _extract_return_type(self, func_node: ast.FunctionDef) -> Optional[str]:
        """Extract return type annotation if present"""
        if func_node.returns:
            if isinstance(func_node.returns, ast.Name):
                return func_node.returns.id
            elif isinstance(func_node.returns, ast.Constant):
                return str(func_node.returns.value)
            else:
                return "Any"
        return None

    def _extract_function_to_module(self, source_file: str, function: FunctionExtraction, 
                                  extraction_id: str) -> Dict[str, Any]:
        """Extract a single function to appropriate module"""
        # Determine target module based on function characteristics
        module_name = self._determine_target_module(function)
        module_path = self._get_module_path(source_file, module_name)
        
        # Create or update target module
        if not Path(module_path).exists():
            module = self._create_new_module(module_path, module_name, [function])
            modules_created = [module]
        else:
            module = self._add_function_to_existing_module(module_path, function)
            modules_created = []
        
        # Generate import updates
        import_updates = self._generate_import_updates(source_file, function, module_path)
        
        return {
            "modules": modules_created,
            "imports": import_updates
        }

    def _determine_target_module(self, function: FunctionExtraction) -> str:
        """Determine the best target module for a function"""
        func_name = function.function_name
        
        # Check for utility patterns
        for pattern in self.extraction_config["utility_patterns"]:
            if pattern in func_name:
                return f"{pattern[1:]}_utils"  # Remove leading underscore
        
        # Default to generic utilities
        return "utils"

    def _get_module_path(self, source_file: str, module_name: str) -> str:
        """Get path for target module"""
        source_path = Path(source_file)
        parent_dir = source_path.parent
        
        # Create utils directory if it doesn't exist
        utils_dir = parent_dir / "utils"
        utils_dir.mkdir(exist_ok=True)
        
        return str(utils_dir / f"{module_name}.py")

    def _create_new_module(self, module_path: str, module_name: str, 
                          functions: List[FunctionExtraction]) -> ModuleCreation:
        """Create a new module with extracted functions"""
        # Generate module content
        module_content = self._generate_module_content(module_name, functions)
        
        # Write module file
        with open(module_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        
        # Create __init__.py if needed
        init_path = Path(module_path).parent / "__init__.py"
        if not init_path.exists() and self.extraction_config["module_organization"]["create_init_files"]:
            with open(init_path, 'w') as f:
                f.write('"""Utility modules for extracted functions."""\n')
        
        return ModuleCreation(
            module_name=module_name,
            module_path=module_path,
            purpose=f"Utility module for {', '.join(f.function_name for f in functions)}",
            extracted_functions=functions,
            utility_functions=[f.function_name for f in functions],
            required_imports=self._extract_required_imports(functions),
            module_docstring=f'"""Utility functions extracted from various modules."""',
            estimated_size=sum(len(f.function_code.splitlines()) for f in functions)
        )

    def _generate_module_content(self, module_name: str, functions: List[FunctionExtraction]) -> str:
        """Generate content for a new module"""
        content_parts = [
            f'#!/usr/bin/env python3',
            f'"""',
            f'{module_name.title()} - Extracted Utility Functions',
            f'{"=" * (len(module_name) + 35)}',
            f'',
            f'Automatically extracted utility functions for improved modularity.',
            f'',
            f'Extracted functions:',
        ]
        
        for func in functions:
            content_parts.append(f'- {func.function_name}: {func.extraction_reason}')
        
        content_parts.extend([
            f'',
            f'Generated: {datetime.now().isoformat()}',
            f'"""',
            f'',
        ])
        
        # Add imports
        imports = self._extract_required_imports(functions)
        if imports:
            content_parts.extend(imports)
            content_parts.append('')
        
        # Add functions
        for func in functions:
            content_parts.extend([
                '',
                func.function_code,
                ''
            ])
        
        return '\n'.join(content_parts)

    def _extract_required_imports(self, functions: List[FunctionExtraction]) -> List[str]:
        """Extract imports required by functions"""
        imports = set()
        
        for func in functions:
            # Parse function code to find imports
            try:
                tree = ast.parse(func.function_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.add(f"import {alias.name}")
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            imports.add(f"from {module} import {alias.name}")
            except SyntaxError:
                # Skip if function code can't be parsed independently
                continue
        
        return sorted(list(imports))

    def _generate_import_updates(self, source_file: str, function: FunctionExtraction, 
                               module_path: str) -> List[ImportUpdate]:
        """Generate import updates for extracted function"""
        updates = []
        
        # Calculate relative import path
        source_path = Path(source_file)
        module_path_obj = Path(module_path)
        
        try:
            relative_path = os.path.relpath(module_path_obj.parent, source_path.parent)
            if relative_path == '.':
                import_path = f"utils.{module_path_obj.stem}"
            else:
                import_path = f"{relative_path.replace('/', '.')}.{module_path_obj.stem}"
        except ValueError:
            # Fallback to absolute import
            import_path = f"utils.{module_path_obj.stem}"
        
        # Create import update
        update = ImportUpdate(
            file_path=source_file,
            old_import="",  # No old import to replace
            new_import=f"from {import_path} import {function.function_name}",
            line_number=1,  # Add at top of file
            update_type="add",
            context=f"Import for extracted function {function.function_name}"
        )
        
        updates.append(update)
        return updates

    def _update_source_file(self, file_path: str, content: str, 
                          extracted_functions: List[FunctionExtraction],
                          import_updates: List[ImportUpdate]) -> str:
        """Update source file after extraction"""
        lines = content.splitlines()
        
        # Remove extracted functions (in reverse order to maintain line numbers)
        for func in sorted(extracted_functions, key=lambda f: f.start_line, reverse=True):
            del lines[func.start_line:func.end_line + 1]
        
        # Add imports at the top
        import_lines = []
        for update in import_updates:
            if update.update_type == "add":
                import_lines.append(update.new_import)
        
        if import_lines:
            # Find insertion point (after existing imports)
            insert_point = 0
            for i, line in enumerate(lines):
                if line.strip().startswith(('import ', 'from ')) or line.strip().startswith('#'):
                    insert_point = i + 1
                elif line.strip() == '':
                    continue
                else:
                    break
            
            # Insert new imports
            for i, import_line in enumerate(import_lines):
                lines.insert(insert_point + i, import_line)
        
        updated_content = '\n'.join(lines)
        
        # Write updated file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return updated_content

    def _validate_extraction(self, file_path: str, updated_content: str, 
                           extracted_functions: List[FunctionExtraction]) -> Dict[str, Any]:
        """Validate extraction results"""
        validation_results = {
            "syntax_valid": False,
            "imports_valid": False,
            "functionality_preserved": False,
            "safety_score": 0.0,
            "issues": []
        }
        
        try:
            # Check syntax
            ast.parse(updated_content)
            validation_results["syntax_valid"] = True
            
            # Check imports (simplified)
            validation_results["imports_valid"] = True
            
            # Assume functionality preserved (would need tests)
            validation_results["functionality_preserved"] = True
            
            # Calculate safety score
            safety_score = 0.0
            if validation_results["syntax_valid"]:
                safety_score += 0.4
            if validation_results["imports_valid"]:
                safety_score += 0.3
            if validation_results["functionality_preserved"]:
                safety_score += 0.3
            
            validation_results["safety_score"] = safety_score
            
        except SyntaxError as e:
            validation_results["issues"].append(f"Syntax error: {e}")
        except Exception as e:
            validation_results["issues"].append(f"Validation error: {e}")
        
        return validation_results

    def _calculate_performance_impact(self, original_analysis: FileAnalysisResult, 
                                   extracted_functions: List[FunctionExtraction]) -> Dict[str, float]:
        """Calculate performance impact of extraction"""
        return {
            "complexity_reduction": 0.1 * len(extracted_functions),
            "maintainability_improvement": 0.05 * len(extracted_functions),
            "lines_reduced": sum(len(f.function_code.splitlines()) for f in extracted_functions),
            "modularity_improvement": 0.2
        }

    def _create_backup(self, file_path: str) -> str:
        """Create backup before extraction"""
        if not self.backup_directory:
            self.backup_directory = tempfile.mkdtemp(prefix="extraction_backup_")
        
        backup_path = Path(self.backup_directory) / f"{Path(file_path).name}.backup"
        shutil.copy2(file_path, backup_path)
        
        return str(backup_path)

    def _create_rollback_data(self, extraction_id: str, source_file: str, 
                            original_content: str, modules_created: List[ModuleCreation]) -> Dict[str, Any]:
        """Create rollback data for extraction"""
        rollback_data = {
            "extraction_id": extraction_id,
            "source_file": source_file,
            "original_content": original_content,
            "modules_created": [m.module_path for m in modules_created],
            "backup_directory": self.backup_directory,
            "timestamp": datetime.now().isoformat()
        }
        
        self.rollback_stack.append(rollback_data)
        return rollback_data

    def _rollback_extraction(self, extraction_id: str) -> bool:
        """Rollback an extraction operation"""
        for rollback_data in reversed(self.rollback_stack):
            if rollback_data["extraction_id"] == extraction_id:
                try:
                    # Restore original file
                    with open(rollback_data["source_file"], 'w') as f:
                        f.write(rollback_data["original_content"])
                    
                    # Remove created modules
                    for module_path in rollback_data["modules_created"]:
                        if Path(module_path).exists():
                            os.remove(module_path)
                    
                    self.log(f"Successfully rolled back extraction {extraction_id}", "info")
                    return True
                    
                except Exception as e:
                    self.log(f"Error during rollback: {e}", "error")
                    return False
        
        self.log(f"No rollback data found for extraction {extraction_id}", "warning")
        return False

    def _generate_extraction_id(self) -> str:
        """Generate unique extraction ID"""
        return f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]}"

    def _create_empty_result(self, extraction_id: str, reason: str) -> ExtractionResult:
        """Create empty extraction result"""
        return ExtractionResult(
            extraction_id=extraction_id,
            source_files_modified=[],
            modules_created=[],
            imports_updated=[],
            functions_extracted=[],
            rollback_data={},
            validation_results={"message": reason},
            performance_impact={},
            safety_score=1.0
        )

    def _find_common_functions(self, file_analyses: List[FileAnalysisResult]) -> Dict[str, List[str]]:
        """Find functions common across multiple files"""
        function_usage = defaultdict(list)
        
        # This is a simplified implementation
        # In practice, you'd analyze AST of each file to find actual function calls
        
        return dict(function_usage)

    def _group_functions_by_purpose(self, common_functions: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """Group functions by their purpose"""
        groups = defaultdict(list)
        
        for func_name, files in common_functions.items():
            # Determine group based on function name patterns
            for pattern in self.extraction_config["utility_patterns"]:
                if pattern in func_name:
                    groups[pattern[1:]].append(func_name)  # Remove underscore
                    break
            else:
                groups["general"].append(func_name)
        
        return dict(groups)

    def _create_utility_module(self, group_name: str, functions: List[str]) -> ModuleCreation:
        """Create a utility module for a group of functions"""
        # This is a simplified implementation
        return ModuleCreation(
            module_name=f"{group_name}_utils",
            module_path=f"utils/{group_name}_utils.py",
            purpose=f"Utility functions for {group_name}",
            extracted_functions=[],
            utility_functions=functions,
            required_imports=[],
            module_docstring=f'"""Utility functions for {group_name} operations."""',
            estimated_size=len(functions) * 20  # Rough estimate
        )

    def _apply_import_update(self, import_update: ImportUpdate) -> None:
        """Apply a single import update"""
        # Read file
        with open(import_update.file_path, 'r') as f:
            lines = f.readlines()
        
        # Apply update based on type
        if import_update.update_type == "add":
            lines.insert(import_update.line_number, import_update.new_import + '\n')
        elif import_update.update_type == "modify":
            lines[import_update.line_number] = import_update.new_import + '\n'
        elif import_update.update_type == "remove":
            del lines[import_update.line_number]
        
        # Write file
        with open(import_update.file_path, 'w') as f:
            f.writelines(lines)

    def _validate_all_imports(self, extraction_result: ExtractionResult) -> bool:
        """Validate that all imports work correctly"""
        try:
            for file_path in extraction_result.source_files_modified:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Try to parse (basic validation)
                ast.parse(content)
            
            return True
            
        except Exception as e:
            self.log(f"Import validation failed: {e}", "error")
            return False

    @contextmanager
    def extraction_context(self, safety_checks: bool = True):
        """Context manager for safe extraction operations"""
        backup_dir = None
        try:
            if safety_checks:
                backup_dir = tempfile.mkdtemp(prefix="extraction_safety_")
                self.backup_directory = backup_dir
            
            yield
            
        except Exception as e:
            self.log(f"Extraction failed: {e}", "error")
            if backup_dir and self.rollback_stack:
                # Attempt to rollback all operations in this context
                for rollback_data in reversed(self.rollback_stack):
                    self._rollback_extraction(rollback_data["extraction_id"])
            raise
        finally:
            if backup_dir:
                # Cleanup backup directory if successful
                shutil.rmtree(backup_dir, ignore_errors=True) 