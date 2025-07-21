#!/usr/bin/env python3
"""
AI Enhancement Framework - Optimization Package
==============================================

Code analysis, optimization, and refactoring tools for automated code improvement.

This package provides comprehensive tools for:
- Codebase analysis with complexity metrics
- Automated function/class extraction to modules
- Import statement optimization
- Code quality improvements
- Pattern standardization
- Refactoring validation

Author: AI Enhancement Framework
Version: 1.0.0
"""

from .codebase_analyzer import (
    CodebaseAnalyzer,
    FileAnalysisResult,
    DirectoryAnalysis,
    RefactoringPlan
)

from .modular_extractor import (
    ModularExtractor,
    FunctionExtraction,
    ModuleCreation,
    ImportUpdate,
    ExtractionResult
)

from .code_quality_optimizer import (
    CodeQualityOptimizer,
    ImportOptimization,
    PatternStandardization,
    OptimizationResult
)

__all__ = [
    # Codebase Analyzer
    'CodebaseAnalyzer',
    'FileAnalysisResult',
    'DirectoryAnalysis', 
    'RefactoringPlan',
    
    # Modular Extractor
    'ModularExtractor',
    'FunctionExtraction',
    'ModuleCreation',
    'ImportUpdate',
    'ExtractionResult',
    
    # Code Quality Optimizer
    'CodeQualityOptimizer',
    'ImportOptimization',
    'PatternStandardization',
    'OptimizationResult'
]

__version__ = "1.0.0"
__author__ = "AI Enhancement Framework"
__description__ = "Comprehensive code optimization and refactoring tools"

# Package metadata
PACKAGE_INFO = {
    "name": "ai-enhancement-framework-optimization",
    "version": __version__,
    "description": __description__,
    "author": __author__,
    "provides": [
        "Automated codebase analysis",
        "Function/class extraction to modules", 
        "Import optimization",
        "Code quality improvements",
        "Pattern standardization",
        "Refactoring validation"
    ],
    "dependencies": [
        "ast (built-in)",
        "pathlib (built-in)",
        "typing (built-in)",
        "dataclasses (built-in)",
        "collections (built-in)"
    ],
    "optional_dependencies": [
        "libcst>=1.0.0 (for advanced CST analysis)",
        "astroid>=3.0.0 (for semantic analysis)"
    ]
}

def get_version():
    """Get package version"""
    return __version__

def get_info():
    """Get package information"""
    return PACKAGE_INFO

def create_analyzer(task_id: str = "analysis", config_file: str = None) -> CodebaseAnalyzer:
    """
    Create a configured codebase analyzer.
    
    Args:
        task_id: Unique task identifier
        config_file: Optional configuration file path
        
    Returns:
        Configured CodebaseAnalyzer instance
    """
    return CodebaseAnalyzer(task_id, config_file)

def create_extractor(task_id: str = "extraction", config_file: str = None) -> ModularExtractor:
    """
    Create a configured modular extractor.
    
    Args:
        task_id: Unique task identifier
        config_file: Optional configuration file path
        
    Returns:
        Configured ModularExtractor instance
    """
    return ModularExtractor(task_id, config_file)

def create_optimizer(task_id: str = "optimization", config_file: str = None) -> CodeQualityOptimizer:
    """
    Create a configured code quality optimizer.
    
    Args:
        task_id: Unique task identifier
        config_file: Optional configuration file path
        
    Returns:
        Configured CodeQualityOptimizer instance
    """
    return CodeQualityOptimizer(task_id, config_file)

def optimize_project(project_path: str, config: dict = None) -> dict:
    """
    Perform comprehensive optimization on a project directory.
    
    Args:
        project_path: Path to project directory
        config: Optional configuration overrides
        
    Returns:
        Dictionary with optimization results
    """
    # Create components
    analyzer = create_analyzer("project_analysis")
    extractor = create_extractor("project_extraction") 
    optimizer = create_optimizer("project_optimization")
    
    try:
        # Analyze project
        analysis = analyzer.analyze_directory(project_path)
        
        # Get refactoring recommendations
        refactoring_plans = analyzer.identify_refactoring_opportunities(analysis)
        
        # Optimize files
        optimization_results = optimizer.optimize_directory(project_path)
        
        return {
            "status": "success",
            "analysis": {
                "total_files": analysis.total_files,
                "total_lines": analysis.total_lines,
                "quality_score": analysis.overall_quality_score,
                "violations": len(analysis.modularity_violations)
            },
            "refactoring_plans": len(refactoring_plans),
            "optimizations": len(optimization_results),
            "overall_improvement": sum(r.overall_score for r in optimization_results) / max(len(optimization_results), 1)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "analysis": {},
            "refactoring_plans": 0,
            "optimizations": 0,
            "overall_improvement": 0.0
        } 