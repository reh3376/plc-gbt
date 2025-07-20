#!/usr/bin/env python3
"""
🤖 AI Task Orchestrator - Universal Framework for Coding Task Completion

Generalized framework extracted from plc-gbt project for systematic AI task completion.
Provides AI agents and LLMs with methodical task analysis, planning, and execution.

Universal Features:
- Domain-agnostic task analysis and decomposition
- Resource discovery with configurable integrations
- Context management and planning
- Comprehensive validation framework
- Progress tracking and documentation
- Extensible provider architecture
- Production deployment readiness validation

Author: AI Enhancement Framework (Phase 25)
Extracted from: plc-gbt AI Task Orchestrator
Created: 2025-01-18
License: MIT
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple, Union
from pathlib import Path
from datetime import datetime
import hashlib
import re
import asyncio
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import traceback
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskComplexity(Enum):
    """Task complexity levels following AI Task Orchestrator Guide"""
    SIMPLE = "simple"      # < 100 lines, 1 file, < 1 hour
    MODERATE = "moderate"  # 100-500 lines, 2-5 files, 1-3 hours  
    COMPLEX = "complex"    # 500-1500 lines, 5-15 files, 3-8 hours
    EXTENSIVE = "extensive" # > 1500 lines, > 15 files, > 8 hours

@dataclass
class TaskAnalysisResult:
    """Structured task analysis result"""
    task_id: str
    description: str
    complexity: TaskComplexity
    requirements: List[str]
    estimated_effort: Dict[str, Union[str, int]]
    resources_needed: Dict[str, Any]
    risks: List[str]
    validation_criteria: List[str]
    dependencies: List[str]
    execution_plan: List[Dict[str, Any]]
    timestamp: datetime

@dataclass
class TaskAnalysis:
    """Task analysis framework following AI Task Orchestrator methodology"""
    task_id: str
    complexity: str  # simple, moderate, complex, extensive
    estimated_time: str
    estimated_lines: int
    requirements: List[str]
    risks: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ExecutionStep:
    """Individual execution step tracking"""
    step_name: str
    status: str  # started, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

class AITaskOrchestrator:
    """
    Universal framework for AI agents to complete coding tasks systematically.
    
    Features:
    - Task analysis and decomposition
    - Resource discovery with configurable integrations
    - Context management and planning
    - Comprehensive validation and progress tracking
    - Extensible for domain-specific enhancements
    - Production deployment readiness
    """
    
    def __init__(self, 
                 project_root: Optional[str] = None,
                 project_markers: Optional[List[str]] = None,
                 domain_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the universal task orchestrator.
        
        Args:
            project_root: Root directory of the project (auto-detected if None)
            project_markers: Custom project markers for root detection
            domain_config: Domain-specific configuration for extensions
        """
        self.project_root = Path(project_root) if project_root else self._detect_project_root(project_markers)
        self.temp_dir = Path(tempfile.mkdtemp(prefix="ai_task_"))
        self.task_id = self._generate_task_id()
        self.session_log = []
        self.validation_results = {}
        self.domain_config = domain_config or {}
        
        # Configurable integrations
        self.providers = {}
        self.analyzers = {}
        self.validators = {}
        
        # Initialize base analyzers
        self._initialize_base_components()
        
        logger.info(f"Universal Task Orchestrator initialized: {self.task_id}")
        logger.info(f"Project root: {self.project_root}")
        
    def _initialize_base_components(self):
        """Initialize base framework components"""
        # Basic file system analyzer
        self.analyzers['filesystem'] = FileSystemAnalyzer(self.project_root)
        
        # Basic dependency analyzer
        self.analyzers['dependencies'] = DependencyAnalyzer(self.project_root)
        
        # Basic code analyzer
        self.analyzers['code'] = CodeAnalyzer(self.project_root)
        
    def _detect_project_root(self, custom_markers: Optional[List[str]] = None) -> Path:
        """Auto-detect project root directory with configurable markers."""
        current = Path.cwd()
        
        # Default project markers
        default_markers = [
            '.git', 'README.md', 'pyproject.toml', 'package.json', 
            'requirements.txt', 'setup.py', 'Cargo.toml', 'pom.xml'
        ]
        
        # Use custom markers if provided
        markers = custom_markers or default_markers
        
        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                return current
            current = current.parent
            
        return Path.cwd()
    
    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:6]
        return f"task_{timestamp}_{random_suffix}"
    
    def analyze_task(self, task_description: str) -> TaskAnalysisResult:
        """
        Universal task analysis with domain awareness.
        
        Args:
            task_description: Description of the task to complete
            
        Returns:
            Structured task analysis result
        """
        logger.info("Starting universal task analysis")
        
        # Core analysis
        complexity = self._assess_complexity(task_description)
        requirements = self._extract_requirements(task_description)
        resources = self._identify_resources(task_description)
        risks = self._identify_risks(task_description)
        validation_criteria = self._define_validation_criteria(task_description)
        estimated_effort = self._estimate_effort(task_description, complexity)
        dependencies = self._identify_dependencies(task_description)
        
        # Create execution plan
        execution_plan = self._create_execution_plan(
            complexity, requirements, resources, dependencies
        )
        
        # Build result
        result = TaskAnalysisResult(
            task_id=self.task_id,
            description=task_description,
            complexity=complexity,
            requirements=requirements,
            estimated_effort=estimated_effort,
            resources_needed=resources,
            risks=risks,
            validation_criteria=validation_criteria,
            dependencies=dependencies,
            execution_plan=execution_plan,
            timestamp=datetime.now()
        )
        
        # Save analysis for context management
        analysis_file = self.temp_dir / f"{self.task_id}_analysis.json"
        with open(analysis_file, 'w') as f:
            # Convert dataclass to dict for JSON serialization
            analysis_dict = asdict(result)
            analysis_dict['timestamp'] = analysis_dict['timestamp'].isoformat()
            analysis_dict['complexity'] = analysis_dict['complexity'].value
            json.dump(analysis_dict, f, indent=2)
            
        self.session_log.append({
            "action": "task_analysis",
            "timestamp": datetime.now().isoformat(),
            "result": "completed",
            "file": str(analysis_file)
        })
        
        logger.info(f"Task analysis completed: {complexity.value} complexity")
        return result
    
    def _assess_complexity(self, task_description: str) -> TaskComplexity:
        """Universal complexity assessment based on task scope."""
        desc_lower = task_description.lower()
        
        # Extensive complexity indicators
        extensive_indicators = [
            "entire system", "full implementation", "complete rewrite",
            "comprehensive", "end-to-end", "multiple modules",
            "architecture", "framework", "major refactor",
            "production deployment", "enterprise", "multiple repositories",
            "entire codebase", "full stack", "multi-service"
        ]
        
        # Complex indicators
        complex_indicators = [
            "multiple files", "integration", "database", "api",
            "complex logic", "algorithm", "optimization",
            "testing suite", "documentation", "configuration",
            "multi-step", "workflow", "pipeline"
        ]
        
        # Moderate indicators
        moderate_indicators = [
            "new feature", "modification", "enhancement",
            "class", "function", "module", "component",
            "single file", "utility", "helper"
        ]
        
        if any(indicator in desc_lower for indicator in extensive_indicators):
            return TaskComplexity.EXTENSIVE
        elif any(indicator in desc_lower for indicator in complex_indicators):
            return TaskComplexity.COMPLEX
        elif any(indicator in desc_lower for indicator in moderate_indicators):
            return TaskComplexity.MODERATE
        else:
            return TaskComplexity.SIMPLE
    
    def _extract_requirements(self, task_description: str) -> List[str]:
        """Universal requirement extraction from task description."""
        requirements = []
        
        # File format requirements
        formats = re.findall(r'\b(JSON|CSV|XML|YAML|SQL|TXT|MD|HTML|CSS|JS|TS|PY|RS|GO|JAVA)\b', 
                           task_description, re.IGNORECASE)
        requirements.extend([f"Support for {fmt} format" for fmt in set(formats)])
        
        # Programming language requirements  
        languages = re.findall(r'\b(Python|TypeScript|JavaScript|Java|Rust|Go|C\+\+|SQL|HTML|CSS)\b', 
                             task_description, re.IGNORECASE)
        requirements.extend([f"Implementation in {lang}" for lang in set(languages)])
        
        # Functionality requirements
        functions = re.findall(r'\b(convert|validate|parse|generate|analyze|process|integrate|create|build|deploy|test)\b', 
                             task_description, re.IGNORECASE)
        requirements.extend([f"Must {func} data/files" for func in set(functions)])
        
        # Quality requirements
        if "test" in task_description.lower():
            requirements.append("Include comprehensive testing")
        if "document" in task_description.lower():
            requirements.append("Include documentation")
        if "error" in task_description.lower() or "exception" in task_description.lower():
            requirements.append("Robust error handling")
        if "production" in task_description.lower() or "deploy" in task_description.lower():
            requirements.append("Production deployment ready")
        if "performance" in task_description.lower() or "optimize" in task_description.lower():
            requirements.append("Performance optimization")
            
        return list(set(requirements)) or ["Basic functionality implementation"]
    
    def _identify_resources(self, task_description: str) -> Dict[str, Any]:
        """Universal resource identification."""
        resources = {
            "filesystem": {},
            "dependencies": [],
            "tools": [],
            "documentation": [],
            "code_examples": [],
            "external_services": []
        }
        
        # Filesystem analysis
        if hasattr(self.analyzers, 'filesystem'):
            try:
                fs_info = self.analyzers['filesystem'].analyze()
                resources["filesystem"] = fs_info
            except Exception as e:
                logger.warning(f"Filesystem analysis failed: {e}")
        
        # Dependency analysis
        if hasattr(self.analyzers, 'dependencies'):
            try:
                deps = self.analyzers['dependencies'].identify_dependencies(task_description)
                resources["dependencies"] = deps
            except Exception as e:
                logger.warning(f"Dependency analysis failed: {e}")
        
        # Common tools based on task
        if "git" in task_description.lower():
            resources["tools"].append("git")
        if "docker" in task_description.lower():
            resources["tools"].append("docker")
        if "test" in task_description.lower():
            resources["tools"].extend(["pytest", "unittest", "jest"])
        if "lint" in task_description.lower():
            resources["tools"].extend(["pylint", "flake8", "eslint"])
        if "format" in task_description.lower():
            resources["tools"].extend(["black", "prettier"])
            
        return resources
    
    def _identify_risks(self, task_description: str) -> List[str]:
        """Universal risk identification."""
        risks = []
        
        # Complexity-based risks
        complexity = self._assess_complexity(task_description)
        if complexity == TaskComplexity.EXTENSIVE:
            risks.extend([
                "High complexity may lead to scope creep",
                "Multiple integration points increase failure risk",
                "Large codebase changes may introduce bugs",
                "Extended development time risk"
            ])
        elif complexity == TaskComplexity.COMPLEX:
            risks.extend([
                "Integration complexity may cause delays",
                "Multiple file changes increase merge conflicts",
                "Testing complexity increases"
            ])
        
        # Task-specific risks
        if "production" in task_description.lower():
            risks.append("Production deployment risks")
        if "database" in task_description.lower():
            risks.append("Data integrity and migration risks")
        if "api" in task_description.lower():
            risks.append("API compatibility and versioning risks")
        if "performance" in task_description.lower():
            risks.append("Performance regression risks")
        if "security" in task_description.lower():
            risks.append("Security vulnerability introduction")
            
        return risks or ["Standard development risks"]
    
    def _define_validation_criteria(self, task_description: str) -> List[str]:
        """Define validation criteria for the task."""
        criteria = [
            "Code compiles/runs without errors",
            "Basic functionality works as expected",
            "Code follows project standards"
        ]
        
        if "test" in task_description.lower():
            criteria.append("All tests pass")
        if "performance" in task_description.lower():
            criteria.append("Performance requirements met")
        if "documentation" in task_description.lower():
            criteria.append("Documentation is complete and accurate")
        if "security" in task_description.lower():
            criteria.append("Security analysis passes")
        if "production" in task_description.lower():
            criteria.extend([
                "Production deployment successful",
                "Monitoring and logging configured"
            ])
            
        return criteria
    
    def _estimate_effort(self, task_description: str, complexity: TaskComplexity) -> Dict[str, Union[str, int]]:
        """Estimate development effort based on complexity."""
        effort_mapping = {
            TaskComplexity.SIMPLE: {
                "hours": "< 1",
                "lines_of_code": "< 100",
                "files": 1,
                "developers": 1
            },
            TaskComplexity.MODERATE: {
                "hours": "1-3",
                "lines_of_code": "100-500", 
                "files": "2-5",
                "developers": 1
            },
            TaskComplexity.COMPLEX: {
                "hours": "3-8",
                "lines_of_code": "500-1500",
                "files": "5-15", 
                "developers": "1-2"
            },
            TaskComplexity.EXTENSIVE: {
                "hours": "8+",
                "lines_of_code": "1500+",
                "files": "15+",
                "developers": "2+"
            }
        }
        
        base_estimate = effort_mapping[complexity].copy()
        
        # Adjust based on task specifics
        if "documentation" in task_description.lower():
            base_estimate["additional_hours"] = "Documentation: +20%"
        if "testing" in task_description.lower():
            base_estimate["additional_hours"] = "Testing: +30%"
        if "production" in task_description.lower():
            base_estimate["additional_hours"] = "Production setup: +25%"
            
        return base_estimate
    
    def _identify_dependencies(self, task_description: str) -> List[str]:
        """Identify task dependencies."""
        dependencies = []
        
        # Common dependencies
        if "database" in task_description.lower():
            dependencies.append("Database setup and connection")
        if "api" in task_description.lower():
            dependencies.append("API endpoint availability")
        if "test" in task_description.lower():
            dependencies.append("Testing framework setup")
        if "docker" in task_description.lower():
            dependencies.append("Docker environment")
        if "deployment" in task_description.lower():
            dependencies.append("Deployment infrastructure")
            
        return dependencies or ["No external dependencies identified"]
    
    def _create_execution_plan(self, 
                             complexity: TaskComplexity,
                             requirements: List[str],
                             resources: Dict[str, Any],
                             dependencies: List[str]) -> List[Dict[str, Any]]:
        """Create structured execution plan based on analysis."""
        plan = []
        
        # Step 1: Setup and preparation
        plan.append({
            "step": 1,
            "phase": "setup_and_preparation",
            "action": "Environment setup and dependency validation",
            "description": "Prepare development environment and validate dependencies",
            "deliverables": ["environment_setup", "dependency_check"],
            "validation": "All dependencies available and environment ready",
            "estimated_hours": 0.5 if complexity in [TaskComplexity.SIMPLE, TaskComplexity.MODERATE] else 1
        })
        
        # Step 2: Analysis and design
        plan.append({
            "step": 2,
            "phase": "analysis_and_design", 
            "action": "Detailed analysis and solution design",
            "description": "Analyze requirements and design implementation approach",
            "deliverables": ["requirements_spec", "design_document"],
            "validation": "Design review completed and approved",
            "estimated_hours": 1 if complexity == TaskComplexity.SIMPLE else 2
        })
        
        # Step 3: Core implementation
        implementation_hours = {
            TaskComplexity.SIMPLE: 0.5,
            TaskComplexity.MODERATE: 2,
            TaskComplexity.COMPLEX: 4,
            TaskComplexity.EXTENSIVE: 8
        }
        
        plan.append({
            "step": 3,
            "phase": "core_implementation",
            "action": "Main functionality implementation",
            "description": "Implement core features and functionality",
            "deliverables": ["source_code", "initial_tests"],
            "validation": "Core functionality working as expected",
            "estimated_hours": implementation_hours[complexity]
        })
        
        # Step 4: Testing and validation
        plan.append({
            "step": 4,
            "phase": "testing_and_validation",
            "action": "Comprehensive testing and validation",
            "description": "Test implementation and validate against requirements",
            "deliverables": ["test_suite", "validation_report"],
            "validation": "All tests pass and requirements met",
            "estimated_hours": 1 if complexity == TaskComplexity.SIMPLE else 2
        })
        
        # Step 5: Documentation and finalization
        plan.append({
            "step": 5,
            "phase": "documentation_and_finalization",
            "action": "Documentation and final review",
            "description": "Complete documentation and perform final review",
            "deliverables": ["documentation", "final_review"],
            "validation": "Documentation complete and implementation reviewed",
            "estimated_hours": 0.5 if complexity == TaskComplexity.SIMPLE else 1
        })
        
        return plan
    
    def add_provider(self, name: str, provider: Any):
        """Add a provider for extended functionality."""
        self.providers[name] = provider
        logger.info(f"Added provider: {name}")
    
    def add_analyzer(self, name: str, analyzer: Any):
        """Add an analyzer for extended functionality."""
        self.analyzers[name] = analyzer
        logger.info(f"Added analyzer: {name}")
    
    def add_validator(self, name: str, validator: Any):
        """Add a validator for extended functionality."""
        self.validators[name] = validator
        logger.info(f"Added validator: {name}")
    
    def cleanup(self):
        """Clean up temporary resources."""
        try:
            shutil.rmtree(self.temp_dir)
            logger.info("Temporary directory cleaned up")
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory: {e}")

# ============================================================================
# Supporting Classes
# ============================================================================

class FileSystemAnalyzer:
    """Basic filesystem analysis for project structure."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze project structure."""
        return {
            "total_files": self._count_files(),
            "file_types": self._analyze_file_types(),
            "directory_structure": self._analyze_directories(),
            "size_mb": self._calculate_size()
        }
    
    def _count_files(self) -> int:
        """Count total files in project."""
        try:
            return len(list(self.project_root.rglob("*")))
        except Exception:
            return 0
    
    def _analyze_file_types(self) -> Dict[str, int]:
        """Analyze file type distribution."""
        file_types = {}
        try:
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file():
                    suffix = file_path.suffix.lower()
                    file_types[suffix] = file_types.get(suffix, 0) + 1
        except Exception:
            pass
        return file_types
    
    def _analyze_directories(self) -> List[str]:
        """Get main directory structure."""
        try:
            return [d.name for d in self.project_root.iterdir() if d.is_dir()]
        except Exception:
            return []
    
    def _calculate_size(self) -> float:
        """Calculate project size in MB."""
        try:
            total_size = sum(f.stat().st_size for f in self.project_root.rglob("*") if f.is_file())
            return round(total_size / (1024 * 1024), 2)
        except Exception:
            return 0.0

class DependencyAnalyzer:
    """Basic dependency analysis for project."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def identify_dependencies(self, task_description: str) -> List[str]:
        """Identify project dependencies."""
        dependencies = []
        
        # Check for common dependency files
        dep_files = {
            "requirements.txt": self._parse_requirements,
            "package.json": self._parse_package_json,
            "pyproject.toml": self._parse_pyproject,
            "Cargo.toml": self._parse_cargo,
            "pom.xml": self._parse_maven
        }
        
        for dep_file, parser in dep_files.items():
            file_path = self.project_root / dep_file
            if file_path.exists():
                try:
                    deps = parser(file_path)
                    dependencies.extend(deps)
                except Exception as e:
                    logger.warning(f"Failed to parse {dep_file}: {e}")
        
        return dependencies
    
    def _parse_requirements(self, file_path: Path) -> List[str]:
        """Parse requirements.txt file."""
        with open(file_path, 'r') as f:
            return [line.strip().split('==')[0].split('>=')[0].split('<=')[0] 
                   for line in f if line.strip() and not line.startswith('#')]
    
    def _parse_package_json(self, file_path: Path) -> List[str]:
        """Parse package.json file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
            deps = list(data.get('dependencies', {}).keys())
            deps.extend(list(data.get('devDependencies', {}).keys()))
            return deps
    
    def _parse_pyproject(self, file_path: Path) -> List[str]:
        """Parse pyproject.toml file."""
        # Basic parsing - would need toml library for full support
        return ["toml-dependencies-detected"]
    
    def _parse_cargo(self, file_path: Path) -> List[str]:
        """Parse Cargo.toml file."""
        return ["rust-dependencies-detected"]
    
    def _parse_maven(self, file_path: Path) -> List[str]:
        """Parse pom.xml file."""
        return ["maven-dependencies-detected"]

class CodeAnalyzer:
    """Basic code analysis for project."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def analyze_codebase(self) -> Dict[str, Any]:
        """Basic codebase analysis."""
        return {
            "python_files": len(list(self.project_root.rglob("*.py"))),
            "javascript_files": len(list(self.project_root.rglob("*.js"))),
            "typescript_files": len(list(self.project_root.rglob("*.ts"))),
            "total_lines": self._count_lines(),
        }
    
    def _count_lines(self) -> int:
        """Count total lines of code."""
        total_lines = 0
        code_extensions = ['.py', '.js', '.ts', '.java', '.rs', '.go', '.cpp', '.c', '.h']
        
        try:
            for file_path in self.project_root.rglob("*"):
                if file_path.is_file() and file_path.suffix in code_extensions:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += len(f.readlines())
        except Exception:
            pass
            
        return total_lines

# ============================================================================
# Base Orchestrator Framework
# ============================================================================

class BaseOrchestrator(ABC):
    """
    Base orchestrator class following AI Task Orchestrator methodology.
    
    Provides systematic problem-solving infrastructure including:
    - Task analysis and complexity assessment
    - Execution tracking and logging
    - Performance metrics collection
    - Configuration management
    - Error handling and validation
    """

    def __init__(self, task_id: str, config_file: Optional[str] = None):
        self.task_id = task_id
        self.session_id = f"{task_id}_{int(time.time())}"
        
        # Logging setup
        self.logger = self._setup_logging()
        
        # Execution tracking
        self.execution_steps: List[ExecutionStep] = []
        self.performance_metrics: Dict[str, float] = {}
        self.results: Dict[str, Any] = {}
        self.start_time = datetime.now()
        
        # Task analysis
        self.task_analysis = self._analyze_task()
        
        # Validation state
        self.validation_passed = False
        self.validation_details = {}

    def _setup_logging(self) -> logging.Logger:
        """Set up logging for the orchestrator"""
        logger = logging.getLogger(f"orchestrator.{self.task_id}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger

    def _analyze_task(self) -> TaskAnalysis:
        """Analyze the task - to be implemented by subclasses"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="moderate",
            estimated_time="2-4 hours",
            estimated_lines=500,
            requirements=["Task analysis to be implemented"],
            risks=["Abstract implementation"],
            dependencies=[],
            success_criteria=["Implementation complete"]
        )

    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Execute the task - must be implemented by subclasses"""
        pass

    def log_step(self, step_name: str, status: str = "started"):
        """Log execution step"""
        step = ExecutionStep(
            step_name=step_name,
            status=status,
            start_time=datetime.now() if status == "started" else None,
            end_time=datetime.now() if status in ["completed", "failed"] else None
        )
        self.execution_steps.append(step)
        self.logger.info(f"Step {step_name}: {status}")

    def validate_results(self) -> bool:
        """Validate execution results"""
        # Basic validation - can be overridden by subclasses
        self.validation_passed = len(self.results) > 0
        return self.validation_passed

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        elapsed_time = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "task_id": self.task_id,
            "session_id": self.session_id,
            "elapsed_time": elapsed_time,
            "steps_completed": len([s for s in self.execution_steps if s.status == "completed"]),
            "steps_failed": len([s for s in self.execution_steps if s.status == "failed"]),
            "validation_passed": self.validation_passed,
            "performance_metrics": self.performance_metrics
        }

# ============================================================================
# Utility Functions
# ============================================================================

def create_task_orchestrator(project_root: Optional[str] = None,
                           domain_config: Optional[Dict[str, Any]] = None) -> AITaskOrchestrator:
    """Factory function to create a configured task orchestrator."""
    return AITaskOrchestrator(
        project_root=project_root,
        domain_config=domain_config
    )

if __name__ == "__main__":
    # Example usage
    orchestrator = create_task_orchestrator()
    
    sample_task = """
    Create a Python utility to parse JSON configuration files and validate them 
    against a schema. Include error handling and comprehensive testing.
    """
    
    result = orchestrator.analyze_task(sample_task)
    print(f"Task Analysis Complete: {result.complexity.value}")
    print(f"Estimated effort: {result.estimated_effort}")
    print(f"Requirements: {result.requirements}")
    
    # Cleanup
    orchestrator.cleanup() 