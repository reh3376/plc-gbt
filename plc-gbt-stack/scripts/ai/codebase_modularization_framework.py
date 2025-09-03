#!/usr/bin/env python3
"""
Codebase Modularization Framework
=================================

Comprehensive framework for transforming the entire PLC-GPT codebase to a modular
architecture following AI Task Orchestrator Guide methodology.

Based on analysis results showing:
- 179 files, 189,429 lines of code
- Extensive complexity requiring systematic approach
- 4-week implementation with 4 phases
"""

import ast
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ModuleDefinition:
    """Definition of a modular component"""
    name: str
    description: str
    responsibilities: List[str]
    dependencies: List[str]
    exports: List[str]
    complexity: str  # low, medium, high
    priority: int    # 1-5, 1 being highest

@dataclass
class DependencyMapping:
    """Mapping of file dependencies"""
    file_path: str
    imports: List[str]
    exports: List[str]
    internal_dependencies: List[str]
    external_dependencies: List[str]
    complexity_score: int

@dataclass
class RefactoringTask:
    """Individual refactoring task"""
    task_id: str
    title: str
    description: str
    phase: int
    priority: int
    estimated_hours: int
    target_files: List[str]
    dependencies: List[str]
    success_criteria: List[str]
    validation_steps: List[str]

@dataclass
class ModularizationPlan:
    """Complete modularization plan"""
    modules: List[ModuleDefinition]
    dependency_map: List[DependencyMapping]
    refactoring_tasks: List[RefactoringTask]
    timeline: Dict[str, Any]
    risk_mitigation: List[str]
    validation_framework: Dict[str, Any]

class CodebaseModularizationFramework:
    """
    Comprehensive framework for codebase modularization

    Implements systematic approach from AI Task Orchestrator analysis
    """

    def __init__(self, workspace_path: str = "/Users/reh3376/repos/plc-gbt"):
        self.workspace_path = Path(workspace_path)
        self.framework_id = f"modularization_framework_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.scripts_path = self.workspace_path / "plc-gpt-stack" / "scripts"
        logger.info(f"🏗️ Modularization Framework initialized: {self.framework_id}")

    def analyze_dependencies(self) -> List[DependencyMapping]:
        """Analyze current file dependencies and imports"""
        logger.info("🔍 Analyzing current dependencies...")

        dependency_map = []

        if not self.scripts_path.exists():
            logger.warning("Scripts path not found")
            return dependency_map

        for py_file in self.scripts_path.rglob("*.py"):
            try:
                with open(py_file, encoding='utf-8') as f:
                    content = f.read()

                # Parse AST to extract imports
                tree = ast.parse(content)
                imports = []

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.append(node.module)

                # Categorize dependencies
                internal_deps = [imp for imp in imports if any(
                    keyword in imp for keyword in ['scripts', 'plc_gpt', 'modules']
                )]
                external_deps = [imp for imp in imports if imp not in internal_deps]

                # Calculate complexity score based on imports and lines
                lines = len(content.splitlines())
                complexity_score = len(imports) + (lines // 100)

                dependency_map.append(DependencyMapping(
                    file_path=str(py_file.relative_to(self.workspace_path)),
                    imports=imports,
                    exports=self._extract_exports(tree),
                    internal_dependencies=internal_deps,
                    external_dependencies=external_deps,
                    complexity_score=complexity_score
                ))

            except Exception as e:
                logger.warning(f"Failed to analyze {py_file}: {e}")

        logger.info(f"📊 Analyzed {len(dependency_map)} Python files")
        return dependency_map

    def _extract_exports(self, tree: ast.AST) -> List[str]:
        """Extract exported functions and classes from AST"""
        exports = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.name.startswith('_'):  # Public functions
                    exports.append(f"function:{node.name}")
            elif isinstance(node, ast.ClassDef):
                exports.append(f"class:{node.name}")

        return exports

    def define_target_modules(self) -> List[ModuleDefinition]:
        """Define target modular architecture"""
        logger.info("🎯 Defining target modular architecture...")

        modules = [
            ModuleDefinition(
                name="core",
                description="Core infrastructure components",
                responsibilities=[
                    "Base orchestrator patterns",
                    "Configuration management",
                    "Logging infrastructure",
                    "Database connection management",
                    "Error handling framework"
                ],
                dependencies=[],
                exports=[
                    "BaseOrchestrator",
                    "ConfigurationManager",
                    "LoggingManager",
                    "DatabaseManager"
                ],
                complexity="high",
                priority=1
            ),
            ModuleDefinition(
                name="data",
                description="Data processing and management",
                responsibilities=[
                    "Data loading and validation",
                    "Data preprocessing pipelines",
                    "Format conversion utilities",
                    "Data quality checks"
                ],
                dependencies=["core"],
                exports=[
                    "DataLoader",
                    "DataValidator",
                    "DataPreprocessor",
                    "FormatConverter"
                ],
                complexity="medium",
                priority=2
            ),
            ModuleDefinition(
                name="metrics",
                description="Performance metrics and analysis",
                responsibilities=[
                    "Metric calculations",
                    "Performance classification",
                    "Statistical analysis",
                    "Benchmarking utilities"
                ],
                dependencies=["core", "data"],
                exports=[
                    "MetricCalculator",
                    "PerformanceClassifier",
                    "StatisticalAnalyzer",
                    "BenchmarkRunner"
                ],
                complexity="medium",
                priority=2
            ),
            ModuleDefinition(
                name="analysis",
                description="Analysis and reporting framework",
                responsibilities=[
                    "Statistical analysis utilities",
                    "Report generation",
                    "Visualization helpers",
                    "Results aggregation"
                ],
                dependencies=["core", "data", "metrics"],
                exports=[
                    "AnalysisEngine",
                    "ReportGenerator",
                    "VisualizationHelper",
                    "ResultsAggregator"
                ],
                complexity="medium",
                priority=3
            ),
            ModuleDefinition(
                name="ai",
                description="AI and machine learning components",
                responsibilities=[
                    "Task orchestration patterns",
                    "Model training utilities",
                    "Inference engines",
                    "AI workflow management"
                ],
                dependencies=["core", "data", "analysis"],
                exports=[
                    "TaskOrchestrator",
                    "ModelTrainer",
                    "InferenceEngine",
                    "AIWorkflowManager"
                ],
                complexity="high",
                priority=3
            ),
            ModuleDefinition(
                name="integration",
                description="External service integrations",
                responsibilities=[
                    "API client libraries",
                    "External service wrappers",
                    "Authentication helpers",
                    "Rate limiting utilities"
                ],
                dependencies=["core"],
                exports=[
                    "APIClient",
                    "ServiceWrapper",
                    "AuthHelper",
                    "RateLimiter"
                ],
                complexity="medium",
                priority=4
            ),
            ModuleDefinition(
                name="testing",
                description="Testing infrastructure and utilities",
                responsibilities=[
                    "Test fixtures and utilities",
                    "Mock objects and helpers",
                    "Validation frameworks",
                    "Performance testing tools"
                ],
                dependencies=["core"],
                exports=[
                    "TestFixtures",
                    "MockHelpers",
                    "ValidationFramework",
                    "PerformanceTester"
                ],
                complexity="low",
                priority=5
            )
        ]

        logger.info(f"🎯 Defined {len(modules)} target modules")
        return modules

    def create_refactoring_tasks(self, modules: List[ModuleDefinition],
                               dependency_map: List[DependencyMapping]) -> List[RefactoringTask]:
        """Create detailed refactoring tasks based on modules and dependencies"""
        logger.info("📋 Creating refactoring tasks...")

        tasks = []
        task_counter = 1

        # Phase 1: Analysis & Planning Tasks
        tasks.extend([
            RefactoringTask(
                task_id=f"T{task_counter:03d}",
                title="Complete Dependency Analysis",
                description="Analyze all file dependencies and create detailed mapping",
                phase=1,
                priority=1,
                estimated_hours=8,
                target_files=["dependency_analysis_report.json"],
                dependencies=[],
                success_criteria=[
                    "All Python files analyzed",
                    "Dependency map generated",
                    "Circular dependencies identified",
                    "Refactoring priorities established"
                ],
                validation_steps=[
                    "Verify all files processed",
                    "Check dependency accuracy",
                    "Validate complexity scores"
                ]
            ),
            RefactoringTask(
                task_id=f"T{task_counter+1:03d}",
                title="Design Module Architecture",
                description="Create detailed design for each target module",
                phase=1,
                priority=1,
                estimated_hours=12,
                target_files=["module_architecture_design.md"],
                dependencies=["T001"],
                success_criteria=[
                    "Module interfaces defined",
                    "Dependency graph validated",
                    "Migration strategy documented",
                    "Testing approach defined"
                ],
                validation_steps=[
                    "Review module boundaries",
                    "Validate interface contracts",
                    "Check dependency ordering"
                ]
            )
        ])
        task_counter += 2

        # Phase 2: Core Infrastructure Module Tasks
        for module in modules:
            if module.name == "core":
                tasks.append(RefactoringTask(
                    task_id=f"T{task_counter:03d}",
                    title=f"Create {module.name.title()} Module",
                    description=f"Extract and implement {module.description}",
                    phase=2,
                    priority=module.priority,
                    estimated_hours=16,
                    target_files=[f"modules/{module.name}.py"],
                    dependencies=["T001", "T002"],
                    success_criteria=[
                        f"{module.name} module created",
                        "All exports implemented",
                        "Unit tests passing",
                        "Documentation complete"
                    ],
                    validation_steps=[
                        "Run unit tests",
                        "Validate exports",
                        "Check documentation coverage"
                    ]
                ))
                task_counter += 1

        # Phase 3: Domain-Specific Module Tasks
        for module in modules:
            if module.name != "core" and module.name != "testing":
                tasks.append(RefactoringTask(
                    task_id=f"T{task_counter:03d}",
                    title=f"Create {module.name.title()} Module",
                    description=f"Extract and implement {module.description}",
                    phase=3,
                    priority=module.priority,
                    estimated_hours=12,
                    target_files=[f"modules/{module.name}.py"],
                    dependencies=["T003"] + [f"T{i:03d}" for i in range(3, task_counter) if modules[i-3].name in module.dependencies],
                    success_criteria=[
                        f"{module.name} module created",
                        "Dependencies properly imported",
                        "Unit tests passing",
                        "Integration tests passing"
                    ],
                    validation_steps=[
                        "Run unit tests",
                        "Run integration tests",
                        "Validate module isolation"
                    ]
                ))
                task_counter += 1

        # Phase 4: Integration & Migration Tasks
        high_complexity_files = [dm.file_path for dm in dependency_map if dm.complexity_score > 20]

        tasks.extend([
            RefactoringTask(
                task_id=f"T{task_counter:03d}",
                title="Migrate High-Complexity Files",
                description="Refactor files with highest complexity scores to use modules",
                phase=4,
                priority=1,
                estimated_hours=24,
                target_files=high_complexity_files[:10],  # Top 10 most complex
                dependencies=[f"T{i:03d}" for i in range(3, task_counter)],
                success_criteria=[
                    "Import statements updated",
                    "Functionality preserved",
                    "Tests updated and passing",
                    "Performance maintained"
                ],
                validation_steps=[
                    "Run regression tests",
                    "Performance benchmarks",
                    "Code review completed"
                ]
            ),
            RefactoringTask(
                task_id=f"T{task_counter+1:03d}",
                title="Complete Codebase Migration",
                description="Migrate remaining files to use modular architecture",
                phase=4,
                priority=2,
                estimated_hours=32,
                target_files=["All remaining Python files"],
                dependencies=[f"T{task_counter:03d}"],
                success_criteria=[
                    "All files migrated",
                    "Code duplication eliminated",
                    "Comprehensive tests passing",
                    "Documentation updated"
                ],
                validation_steps=[
                    "Full test suite execution",
                    "Code coverage analysis",
                    "Performance validation",
                    "Documentation review"
                ]
            )
        ])

        logger.info(f"📋 Created {len(tasks)} refactoring tasks")
        return tasks

    def create_validation_framework(self) -> Dict[str, Any]:
        """Create comprehensive validation framework"""
        logger.info("✅ Creating validation framework...")

        framework = {
            "automated_tests": {
                "unit_tests": {
                    "description": "Test individual module functionality",
                    "coverage_target": 95,
                    "tools": ["pytest", "coverage.py"],
                    "frequency": "Every commit"
                },
                "integration_tests": {
                    "description": "Test module interactions",
                    "coverage_target": 85,
                    "tools": ["pytest", "testcontainers"],
                    "frequency": "Every pull request"
                },
                "performance_tests": {
                    "description": "Validate performance benchmarks",
                    "tolerance": "5% regression maximum",
                    "tools": ["pytest-benchmark", "memory_profiler"],
                    "frequency": "Weekly"
                }
            },
            "code_quality": {
                "linting": {
                    "tools": ["ruff", "mypy"],
                    "standards": "PEP 8 + type hints",
                    "frequency": "Pre-commit"
                },
                "complexity": {
                    "tool": "radon",
                    "max_complexity": 10,
                    "frequency": "Weekly"
                },
                "duplication": {
                    "tool": "jscpd",
                    "max_duplication": "5%",
                    "frequency": "Weekly"
                }
            },
            "manual_validation": {
                "architecture_review": {
                    "description": "Review module boundaries and interfaces",
                    "frequency": "End of each phase",
                    "reviewers": ["Lead architect", "Senior developer"]
                },
                "code_review": {
                    "description": "Review implementation quality",
                    "frequency": "Every pull request",
                    "reviewers": ["Team lead", "Peer developer"]
                }
            },
            "acceptance_criteria": {
                "functionality": "100% existing functionality preserved",
                "performance": "No performance degradation",
                "maintainability": "Improved code metrics",
                "testability": "Increased test coverage",
                "documentation": "Complete module documentation"
            }
        }

        return framework

    def generate_comprehensive_plan(self) -> ModularizationPlan:
        """Generate complete modularization plan"""
        logger.info("🚀 Generating comprehensive modularization plan...")

        # Generate all components
        dependency_map = self.analyze_dependencies()
        modules = self.define_target_modules()
        tasks = self.create_refactoring_tasks(modules, dependency_map)
        validation_framework = self.create_validation_framework()

        # Create timeline
        timeline = {
            "total_duration": "4 weeks",
            "phases": [
                {
                    "phase": 1,
                    "name": "Analysis & Planning",
                    "duration": "1 week",
                    "tasks": [t.task_id for t in tasks if t.phase == 1],
                    "deliverables": [
                        "Dependency analysis report",
                        "Module architecture design",
                        "Testing infrastructure setup"
                    ]
                },
                {
                    "phase": 2,
                    "name": "Core Infrastructure",
                    "duration": "1 week",
                    "tasks": [t.task_id for t in tasks if t.phase == 2],
                    "deliverables": [
                        "Core module implementation",
                        "Base classes and interfaces",
                        "Configuration framework"
                    ]
                },
                {
                    "phase": 3,
                    "name": "Domain Modules",
                    "duration": "1 week",
                    "tasks": [t.task_id for t in tasks if t.phase == 3],
                    "deliverables": [
                        "Domain-specific modules",
                        "Service layer abstractions",
                        "Utility libraries"
                    ]
                },
                {
                    "phase": 4,
                    "name": "Integration & Migration",
                    "duration": "1 week",
                    "tasks": [t.task_id for t in tasks if t.phase == 4],
                    "deliverables": [
                        "Migrated codebase",
                        "Updated documentation",
                        "Comprehensive test suite"
                    ]
                }
            ]
        }

        # Risk mitigation strategies
        risk_mitigation = [
            "Incremental migration with feature flags",
            "Comprehensive automated testing at each step",
            "Regular validation checkpoints",
            "Rollback strategy for each phase",
            "Performance monitoring throughout process",
            "Code review gates at module boundaries",
            "Documentation updates concurrent with changes"
        ]

        plan = ModularizationPlan(
            modules=modules,
            dependency_map=dependency_map,
            refactoring_tasks=tasks,
            timeline=timeline,
            risk_mitigation=risk_mitigation,
            validation_framework=validation_framework
        )

        logger.info("✅ Comprehensive modularization plan generated")
        return plan

    def save_plan(self, plan: ModularizationPlan) -> str:
        """Save modularization plan to file"""
        results_path = self.workspace_path / "plc-gpt-stack" / "scripts" / "ai"
        results_path.mkdir(parents=True, exist_ok=True)

        output_file = results_path / f"{self.framework_id}_plan.json"

        with open(output_file, 'w') as f:
            json.dump(asdict(plan), f, indent=2, default=str)

        logger.info(f"📁 Modularization plan saved: {output_file}")
        return str(output_file)

    def generate_roadmap_phase(self, plan: ModularizationPlan) -> Dict[str, Any]:
        """Generate roadmap phase content for inclusion in roadmap.md"""
        logger.info("🗺️ Generating roadmap phase content...")

        total_tasks = len(plan.refactoring_tasks)
        total_hours = sum(task.estimated_hours for task in plan.refactoring_tasks)

        roadmap_phase = {
            "phase_number": "14",
            "title": "Codebase Modularization & Architecture Transformation",
            "target": "4 weeks",
            "status": "⏳ Planned (0%)",
            "completion_date": "TBD",
            "complexity": "Extensive (AI Task Orchestrator Classification)",
            "overview": {
                "description": "Comprehensive transformation of entire PLC-GPT codebase to modular architecture following AI Task Orchestrator Guide methodology",
                "scope": f"179 files, 189,429 lines of code → {len(plan.modules)} modular components",
                "methodology": "Systematic 4-phase approach with comprehensive validation",
                "objectives": [
                    "Eliminate 90%+ code duplication across codebase",
                    "Implement clean modular architecture with clear separation of concerns",
                    "Create reusable component library for improved maintainability",
                    "Establish consistent patterns and interfaces throughout system",
                    "Improve developer productivity and code quality metrics"
                ]
            },
            "success_criteria": {
                "code_quality": "90%+ code duplication elimination achieved",
                "architecture": "Clear modular boundaries with minimal coupling",
                "functionality": "100% existing functionality preserved",
                "testing": "95%+ test coverage across all modules",
                "performance": "Performance maintained or improved",
                "documentation": "Complete module documentation and migration guides"
            },
            "phases": [
                {
                    "phase": "14.1",
                    "name": "Analysis & Planning",
                    "duration": "1 week",
                    "description": "Comprehensive dependency analysis and modular architecture design",
                    "tasks": [t.title for t in plan.refactoring_tasks if t.phase == 1],
                    "deliverables": plan.timeline["phases"][0]["deliverables"]
                },
                {
                    "phase": "14.2",
                    "name": "Core Infrastructure Modules",
                    "duration": "1 week",
                    "description": "Create foundational modular components and base patterns",
                    "tasks": [t.title for t in plan.refactoring_tasks if t.phase == 2],
                    "deliverables": plan.timeline["phases"][1]["deliverables"]
                },
                {
                    "phase": "14.3",
                    "name": "Domain-Specific Modules",
                    "duration": "1 week",
                    "description": "Extract domain functionality into specialized modules",
                    "tasks": [t.title for t in plan.refactoring_tasks if t.phase == 3],
                    "deliverables": plan.timeline["phases"][2]["deliverables"]
                },
                {
                    "phase": "14.4",
                    "name": "Integration & Migration",
                    "duration": "1 week",
                    "description": "Migrate entire codebase to use modular architecture",
                    "tasks": [t.title for t in plan.refactoring_tasks if t.phase == 4],
                    "deliverables": plan.timeline["phases"][3]["deliverables"]
                }
            ],
            "target_modules": [
                {
                    "name": module.name,
                    "description": module.description,
                    "complexity": module.complexity,
                    "priority": module.priority
                } for module in plan.modules
            ],
            "risk_assessment": {
                "level": "Medium - manageable with proper planning",
                "mitigation": plan.risk_mitigation
            },
            "validation_framework": {
                "automated_testing": "Unit, integration, and performance tests",
                "code_quality": "Linting, complexity analysis, duplication detection",
                "manual_review": "Architecture and code review processes",
                "acceptance_criteria": plan.validation_framework["acceptance_criteria"]
            },
            "metrics": {
                "current_codebase": "179 files, 189,429 lines",
                "estimated_effort": f"{total_hours} hours across {total_tasks} tasks",
                "target_modules": len(plan.modules),
                "complexity_reduction": "Expected 70%+ reduction in file complexity",
                "duplication_elimination": "90%+ code duplication removal"
            }
        }

        return roadmap_phase

def main():
    """Execute comprehensive codebase modularization framework"""
    print("🏗️ Codebase Modularization Framework")
    print("=" * 80)

    framework = CodebaseModularizationFramework()

    try:
        # Generate comprehensive plan
        plan = framework.generate_comprehensive_plan()

        # Save plan
        plan_file = framework.save_plan(plan)

        # Generate roadmap content
        roadmap_phase = framework.generate_roadmap_phase(plan)

        # Display summary
        print("\n📊 Modularization Plan Summary:")
        print(f"   Target Modules: {len(plan.modules)}")
        print(f"   Refactoring Tasks: {len(plan.refactoring_tasks)}")
        print(f"   Total Effort: {sum(task.estimated_hours for task in plan.refactoring_tasks)} hours")
        print(f"   Dependencies Analyzed: {len(plan.dependency_map)} files")

        print("\n🎯 Target Modules:")
        for module in plan.modules:
            print(f"   {module.name}: {module.description} (Priority {module.priority})")

        print("\n📋 Implementation Phases:")
        for phase in roadmap_phase["phases"]:
            task_count = len([t for t in plan.refactoring_tasks if t.phase == int(phase["phase"].split('.')[1])])
            print(f"   {phase['phase']}: {phase['name']} ({phase['duration']}, {task_count} tasks)")

        print(f"\n✅ Complete plan saved to: {plan_file}")
        print("\n🗺️ Roadmap phase content generated and ready for integration!")
        print("\n🚀 Framework ready for systematic implementation!")

        # Save roadmap phase content
        roadmap_file = Path(plan_file).parent / f"{framework.framework_id}_roadmap_phase.json"
        with open(roadmap_file, 'w') as f:
            json.dump(roadmap_phase, f, indent=2, default=str)
        print(f"📋 Roadmap phase content saved to: {roadmap_file}")

    except Exception as e:
        logger.error(f"❌ Framework generation failed: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())
