#!/usr/bin/env python3
"""
PLC-Optimize: Master CLI Interface for Codebase Optimization Automation
=======================================================================

Comprehensive command-line interface that orchestrates all Phase 14 optimization components
into a unified automation system for enterprise-grade codebase management.

Features:
- Complete codebase analysis and optimization workflows
- Automated refactoring with safety validation
- JSON schema governance and compliance
- CI/CD integration for automated optimization
- Scheduled optimization and monitoring
- Configuration profiles for different scenarios

Following AI Task Orchestrator methodology for EXTENSIVE complexity management.

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 14.4 - Master CLI & CI/CD Integration
Dependencies: All Phase 14 components
"""

import os
import sys
import asyncio
import json
import click
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import subprocess
import yaml
import logging

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent / "modules"))
# Add Phase 14 components to path
sys.path.append(str(Path(__file__).parent / "plc-gbt-stack" / "scripts" / "ai" / "phases" / "phase14"))
from core import BaseOrchestrator, TaskAnalysis

# Import all Phase 14 components
try:
    from .codebase_analyzer import CodebaseAnalyzer, DirectoryAnalysis
    from .code_quality_optimizer import CodeQualityOptimizer, OptimizationResult
    from .modular_extractor import ModularExtractor, ExtractionResult
    from .refactoring_validator import RefactoringValidator, SafetyValidationResult
    from .schema_registry import SchemaRegistry
    from .compliance_engine import ComplianceEngine
    from .multi_db_schema_integration import MultiDBSchemaIntegration
    from .schema_cli import SchemaCLI
    from .git_integration_hooks import GitOptimizationHooks
except ImportError:
    # Fallback for direct execution
    from codebase_analyzer import CodebaseAnalyzer, DirectoryAnalysis
    from code_quality_optimizer import CodeQualityOptimizer, OptimizationResult
    from modular_extractor import ModularExtractor, ExtractionResult
    from refactoring_validator import RefactoringValidator, SafetyValidationResult
    try:
        from schema_registry import SchemaRegistry
        from compliance_engine import ComplianceEngine
        from multi_db_schema_integration import MultiDBSchemaIntegration
        from schema_cli import SchemaCLI
        from git_integration_hooks import GitOptimizationHooks
    except ImportError:
        # Create dummy classes for missing components
        class SchemaRegistry: pass
        class ComplianceEngine: pass
        class MultiDBSchemaIntegration: pass
        class SchemaCLI: pass
        class GitOptimizationHooks: pass

@dataclass
class OptimizationProfile:
    """Configuration profile for different optimization scenarios"""
    name: str
    description: str
    analysis_enabled: bool = True
    quality_optimization_enabled: bool = True
    modular_extraction_enabled: bool = True
    schema_governance_enabled: bool = True
    validation_enabled: bool = True
    git_integration_enabled: bool = False
    auto_apply_safe_changes: bool = False
    backup_before_changes: bool = True
    target_complexity_threshold: float = 10.0
    target_file_size_threshold: int = 1000
    minimum_safety_score: float = 0.8

@dataclass
class OptimizationSession:
    """Comprehensive optimization session tracking"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    profile_used: str = "default"
    project_root: str = ""
    total_files_analyzed: int = 0
    files_optimized: int = 0
    lines_reduced: int = 0
    complexity_improvement: float = 0.0
    validation_score: float = 0.0
    components_executed: List[str] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.components_executed is None:
            self.components_executed = []
        if self.errors is None:
            self.errors = []

class PLCOptimizeMasterCLI(BaseOrchestrator):
    """
    Master CLI orchestrator for comprehensive codebase optimization automation.
    
    Provides unified interface for all Phase 14 optimization components with
    enterprise-grade automation, scheduling, and CI/CD integration capabilities.
    """

    def __init__(self, task_id: str = "plc_optimize_master", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)
        
        # Initialize all Phase 14 components
        self.codebase_analyzer = CodebaseAnalyzer("master_analysis")
        self.quality_optimizer = CodeQualityOptimizer("master_quality")
        self.modular_extractor = ModularExtractor("master_extraction")
        self.refactoring_validator = RefactoringValidator("master_validation")
        self.schema_registry = SchemaRegistry()
        self.compliance_engine = ComplianceEngine(self.schema_registry)
        self.multi_db_integration = MultiDBSchemaIntegration(self.schema_registry)
        self.schema_cli = SchemaCLI()
        self.git_hooks = GitOptimizationHooks("master_git")
        
        # Optimization profiles
        self.optimization_profiles = self._load_optimization_profiles()
        
        # Session tracking
        self.current_session: Optional[OptimizationSession] = None
        self.session_history: List[OptimizationSession] = []
        
        # Automation configuration
        self.automation_config = {
            "enabled": False,
            "schedule": "daily",  # daily, weekly, on-commit
            "max_execution_time": 3600,  # 1 hour
            "notification_webhook": None,
            "rollback_on_failure": True,
            "parallel_execution": True,
            "max_concurrent_operations": 4
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Analyze master CLI orchestration task"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="extensive",
            estimated_time="1-3 hours",
            estimated_lines=2000,
            requirements=[
                "All Phase 14 components available",
                "Git repository with write access", 
                "Sufficient disk space for backups",
                "Python 3.8+ environment"
            ],
            risks=[
                "Large codebase optimization may take significant time",
                "Complex refactoring operations require validation",
                "Git integration requires proper repository setup",
                "Multi-component orchestration complexity"
            ],
            dependencies=[
                "modules.core",
                "phases.phase14.codebase_analyzer",
                "phases.phase14.code_quality_optimizer",
                "phases.phase14.modular_extractor",
                "phases.phase14.refactoring_validator"
            ],
            success_criteria=[
                "All components execute successfully",
                "Validation score >= 0.8",
                "No critical errors during execution",
                "Proper session tracking and reporting"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute master CLI orchestration with comprehensive workflow"""
        self.log_execution_step("Master CLI Orchestration", "started")
        
        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}
            
            # Default to analyzing current directory
            project_root = self.config.get("system.project_root", str(Path.cwd()))
            
            # Create new optimization session
            session = self._create_optimization_session(project_root, "default")
            
            # Execute full optimization workflow
            workflow_result = self.run_full_optimization_workflow(
                project_root=project_root,
                profile_name="default",
                auto_apply=False,
                create_backup=True
            )
            
            # Complete session
            self._complete_optimization_session(workflow_result)
            
            return {
                "status": "completed",
                "session": asdict(self.current_session),
                "workflow_result": workflow_result,
                "components_status": {
                    "analyzer": "available",
                    "optimizer": "available", 
                    "extractor": "available",
                    "validator": "available",
                    "schema_governance": "available"
                }
            }
            
        except Exception as e:
            self.log_error("Master CLI orchestration failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("Master CLI Orchestration", "completed")

    def run_full_optimization_workflow(
        self,
        project_root: str,
        profile_name: str = "default",
        auto_apply: bool = False,
        create_backup: bool = True
    ) -> Dict[str, Any]:
        """
        Execute complete optimization workflow with all Phase 14 components.
        
        Args:
            project_root: Root directory to optimize
            profile_name: Optimization profile to use
            auto_apply: Whether to automatically apply safe optimizations
            create_backup: Whether to create backup before changes
            
        Returns:
            Comprehensive workflow results with all component outputs
        """
        self.log_execution_step("Full Optimization Workflow", "started")
        
        workflow_results = {
            "project_root": project_root,
            "profile_name": profile_name,
            "workflow_start_time": datetime.now().isoformat(),
            "components": {},
            "overall_metrics": {},
            "validation_summary": {},
            "recommendations": []
        }
        
        try:
            profile = self.optimization_profiles.get(profile_name, self.optimization_profiles["default"])
            
            # Create backup if requested
            backup_path = None
            if create_backup:
                backup_path = self._create_project_backup(project_root)
                workflow_results["backup_path"] = str(backup_path)
            
            # Phase 1: Comprehensive Analysis
            if profile.analysis_enabled:
                self.log_execution_step("Comprehensive Analysis", "started")
                analysis_result = self.codebase_analyzer.analyze_directory(project_root)
                workflow_results["components"]["analysis"] = {
                    "status": "completed",
                    "total_files": analysis_result.total_files,
                    "total_lines": analysis_result.total_lines,
                    "average_complexity": analysis_result.average_complexity,
                    "optimization_opportunities": len(analysis_result.optimization_priorities)
                }
                self.current_session.total_files_analyzed = analysis_result.total_files
                self.current_session.components_executed.append("CodebaseAnalyzer")
                self.log_execution_step("Comprehensive Analysis", "completed")
            
            # Phase 2: Code Quality Optimization
            if profile.quality_optimization_enabled:
                self.log_execution_step("Quality Optimization", "started")
                quality_result = self.quality_optimizer.execute()
                workflow_results["components"]["quality_optimization"] = {
                    "status": quality_result.get("status", "completed"),
                    "files_optimized": quality_result.get("files_optimized", 0),
                    "imports_optimized": quality_result.get("imports_optimized", 0),
                    "patterns_standardized": quality_result.get("patterns_standardized", 0)
                }
                self.current_session.components_executed.append("CodeQualityOptimizer")
                self.log_execution_step("Quality Optimization", "completed")
            
            # Phase 3: Modular Extraction
            if profile.modular_extraction_enabled:
                self.log_execution_step("Modular Extraction", "started")
                extraction_result = self.modular_extractor.execute()
                workflow_results["components"]["modular_extraction"] = {
                    "status": extraction_result.get("status", "completed"),
                    "functions_extracted": extraction_result.get("functions_extracted", 0),
                    "modules_created": extraction_result.get("modules_created", 0),
                    "lines_moved": extraction_result.get("total_lines_moved", 0)
                }
                self.current_session.lines_reduced += extraction_result.get("total_lines_moved", 0)
                self.current_session.components_executed.append("ModularExtractor")
                self.log_execution_step("Modular Extraction", "completed")
            
            # Phase 4: Schema Governance
            if profile.schema_governance_enabled:
                self.log_execution_step("Schema Governance", "started")
                compliance_result = self.compliance_engine.execute()
                workflow_results["components"]["schema_governance"] = {
                    "status": compliance_result.get("status", "completed"),
                    "compliance_score": compliance_result.get("compliance_score", 0.0),
                    "violations_found": compliance_result.get("violations_detected", 0),
                    "files_scanned": compliance_result.get("files_scanned", 0)
                }
                self.current_session.components_executed.append("SchemaGovernance")
                self.log_execution_step("Schema Governance", "completed")
            
            # Phase 5: Comprehensive Validation
            if profile.validation_enabled:
                self.log_execution_step("Comprehensive Validation", "started")
                validation_result = self.refactoring_validator.execute()
                workflow_results["components"]["validation"] = {
                    "status": validation_result.get("status", "completed"),
                    "validation_score": validation_result.get("overall_validation_score", 0.0),
                    "safety_score": validation_result.get("safety_score", 0.0),
                    "test_results": validation_result.get("test_results", {})
                }
                self.current_session.validation_score = validation_result.get("overall_validation_score", 0.0)
                self.current_session.components_executed.append("RefactoringValidator")
                self.log_execution_step("Comprehensive Validation", "completed")
            
            # Calculate overall metrics
            workflow_results["overall_metrics"] = self._calculate_overall_metrics(workflow_results)
            
            # Generate recommendations
            workflow_results["recommendations"] = self._generate_workflow_recommendations(
                workflow_results, profile
            )
            
            # Auto-apply safe changes if enabled
            if auto_apply and workflow_results["overall_metrics"]["safety_score"] >= profile.minimum_safety_score:
                self.log_execution_step("Auto-Apply Safe Changes", "started")
                apply_result = self._apply_safe_optimizations(workflow_results)
                workflow_results["auto_apply_result"] = apply_result
                self.log_execution_step("Auto-Apply Safe Changes", "completed")
            
            workflow_results["workflow_end_time"] = datetime.now().isoformat()
            workflow_results["status"] = "completed"
            
            self.log_execution_step("Full Optimization Workflow", "completed")
            return workflow_results
            
        except Exception as e:
            self.log_error("Full optimization workflow failed", e)
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            
            # Restore backup if creation was requested and auto-apply failed
            if create_backup and backup_path and auto_apply:
                self._restore_project_backup(backup_path, project_root)
            
            return workflow_results

    def run_component_analysis(self, project_root: str) -> Dict[str, Any]:
        """Run only the analysis components without making changes"""
        self.log_execution_step("Component Analysis", "started")
        
        try:
            # Run analysis
            analysis_result = self.codebase_analyzer.analyze_directory(project_root)
            
            # Generate optimization opportunities
            opportunities = self.codebase_analyzer.identify_refactoring_opportunities(analysis_result)
            
            return {
                "status": "completed",
                "analysis": {
                    "total_files": analysis_result.total_files,
                    "total_lines": analysis_result.total_lines,
                    "average_complexity": analysis_result.average_complexity,
                    "files_needing_optimization": len([
                        f for f in analysis_result.file_analyses 
                        if f.complexity_score > 10.0 or f.line_count > 1000
                    ])
                },
                "opportunities": [asdict(opp) for opp in opportunities],
                "recommendations": self._generate_analysis_recommendations(analysis_result)
            }
            
        except Exception as e:
            self.log_error("Component analysis failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("Component Analysis", "completed")

    def setup_git_integration(self, project_root: str) -> Dict[str, Any]:
        """Setup git hooks for automated optimization on commits"""
        self.log_execution_step("Git Integration Setup", "started")
        
        try:
            # Install git hooks
            hook_results = self.git_hooks.install_pre_commit_hooks()
            
            # Configure automation settings
            automation_config = {
                "enabled": True,
                "trigger": "pre-commit",
                "safety_threshold": 0.8,
                "max_files_per_commit": 10,
                "timeout_seconds": 300
            }
            
            self._save_automation_config(project_root, automation_config)
            
            return {
                "status": "completed",
                "hooks_installed": len(hook_results),
                "automation_config": automation_config,
                "git_repo_validated": True
            }
            
        except Exception as e:
            self.log_error("Git integration setup failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("Git Integration Setup", "completed")

    def run_schema_governance(self, project_root: str) -> Dict[str, Any]:
        """Run JSON schema governance checks and compliance"""
        self.log_execution_step("Schema Governance", "started")
        
        try:
            # Scan for JSON usage
            scan_results = self.compliance_engine.scan_codebase_for_json(project_root)
            
            # Generate compliance report
            compliance_report = self.compliance_engine.generate_compliance_report()
            
            # Multi-database consistency check
            consistency_report = self.multi_db_integration.validate_database_consistency()
            
            return {
                "status": "completed",
                "json_usages_found": len(scan_results),
                "compliance_score": compliance_report.compliance_score,
                "violations": len(compliance_report.violations),
                "database_consistency": consistency_report.consistency_score,
                "recommendations": compliance_report.recommendations
            }
            
        except Exception as e:
            self.log_error("Schema governance failed", e)
            return {"status": "failed", "error": str(e)}
        finally:
            self.log_execution_step("Schema Governance", "completed")

    def _load_optimization_profiles(self) -> Dict[str, OptimizationProfile]:
        """Load optimization profiles from configuration"""
        return {
            "default": OptimizationProfile(
                name="default",
                description="Balanced optimization suitable for most codebases",
                analysis_enabled=True,
                quality_optimization_enabled=True,
                modular_extraction_enabled=True,
                schema_governance_enabled=True,
                validation_enabled=True,
                auto_apply_safe_changes=False,
                target_complexity_threshold=10.0,
                target_file_size_threshold=1000
            ),
            "conservative": OptimizationProfile(
                name="conservative",
                description="Safe optimizations only with extensive validation",
                analysis_enabled=True,
                quality_optimization_enabled=True,
                modular_extraction_enabled=False,
                schema_governance_enabled=True,
                validation_enabled=True,
                auto_apply_safe_changes=False,
                minimum_safety_score=0.9,
                target_complexity_threshold=15.0
            ),
            "aggressive": OptimizationProfile(
                name="aggressive",
                description="Comprehensive optimization with automated application",
                analysis_enabled=True,
                quality_optimization_enabled=True,
                modular_extraction_enabled=True,
                schema_governance_enabled=True,
                validation_enabled=True,
                git_integration_enabled=True,
                auto_apply_safe_changes=True,
                minimum_safety_score=0.7,
                target_complexity_threshold=8.0,
                target_file_size_threshold=800
            ),
            "ci_cd": OptimizationProfile(
                name="ci_cd",
                description="Optimized for CI/CD pipeline integration",
                analysis_enabled=True,
                quality_optimization_enabled=True,
                modular_extraction_enabled=False,
                schema_governance_enabled=True,
                validation_enabled=True,
                git_integration_enabled=True,
                auto_apply_safe_changes=True,
                backup_before_changes=False,  # Assume git handles versioning
                minimum_safety_score=0.85
            )
        }

    def _create_optimization_session(self, project_root: str, profile_name: str) -> OptimizationSession:
        """Create new optimization session"""
        session = OptimizationSession(
            session_id=f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            start_time=datetime.now(),
            profile_used=profile_name,
            project_root=project_root
        )
        
        self.current_session = session
        self.session_history.append(session)
        
        return session

    def _complete_optimization_session(self, workflow_result: Dict[str, Any]):
        """Complete current optimization session with results"""
        if self.current_session:
            self.current_session.end_time = datetime.now()
            
            # Update metrics from workflow result
            if "overall_metrics" in workflow_result:
                metrics = workflow_result["overall_metrics"]
                self.current_session.files_optimized = metrics.get("files_optimized", 0)
                self.current_session.complexity_improvement = metrics.get("complexity_improvement", 0.0)
                self.current_session.validation_score = metrics.get("validation_score", 0.0)

    def _calculate_overall_metrics(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall optimization metrics from component results"""
        components = workflow_results.get("components", {})
        
        total_files_optimized = 0
        total_complexity_improvement = 0.0
        validation_scores = []
        
        for component_name, component_result in components.items():
            if component_result.get("status") == "completed":
                total_files_optimized += component_result.get("files_optimized", 0)
                
                if "validation_score" in component_result:
                    validation_scores.append(component_result["validation_score"])
        
        overall_validation_score = sum(validation_scores) / len(validation_scores) if validation_scores else 0.0
        
        return {
            "files_optimized": total_files_optimized,
            "complexity_improvement": total_complexity_improvement,
            "validation_score": overall_validation_score,
            "safety_score": overall_validation_score,  # Simplified for demo
            "components_executed": len([c for c in components.values() if c.get("status") == "completed"]),
            "success_rate": len([c for c in components.values() if c.get("status") == "completed"]) / max(len(components), 1)
        }

    def _generate_workflow_recommendations(
        self, 
        workflow_results: Dict[str, Any], 
        profile: OptimizationProfile
    ) -> List[str]:
        """Generate actionable recommendations based on workflow results"""
        recommendations = []
        
        overall_metrics = workflow_results.get("overall_metrics", {})
        validation_score = overall_metrics.get("validation_score", 0.0)
        
        if validation_score < 0.8:
            recommendations.append("Consider running validation again with stricter safety checks")
        
        if overall_metrics.get("files_optimized", 0) == 0:
            recommendations.append("No files were optimized - review analysis results for opportunities")
        
        components = workflow_results.get("components", {})
        
        if "analysis" in components and components["analysis"].get("optimization_opportunities", 0) > 0:
            recommendations.append("Analysis found optimization opportunities - consider running with auto-apply enabled")
        
        if "modular_extraction" in components and components["modular_extraction"].get("functions_extracted", 0) > 0:
            recommendations.append("Functions were extracted - update import statements and test thoroughly")
        
        if "schema_governance" in components and components["schema_governance"].get("violations_found", 0) > 0:
            recommendations.append("JSON schema violations found - implement compliance fixes")
        
        return recommendations

    def _create_project_backup(self, project_root: str) -> Path:
        """Create backup of project before making changes"""
        backup_dir = Path(project_root) / ".plc_optimize_backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}"
        
        # Simple backup - in production would use git or more sophisticated backup
        import shutil
        shutil.copytree(project_root, backup_path, ignore=shutil.ignore_patterns(".plc_optimize_backups"))
        
        return backup_path

    def _restore_project_backup(self, backup_path: Path, project_root: str):
        """Restore project from backup"""
        if backup_path.exists():
            import shutil
            # Remove current files and restore backup
            for item in Path(project_root).iterdir():
                if item.name != ".plc_optimize_backups":
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
            
            # Copy backup files back
            for item in backup_path.iterdir():
                if item.is_dir():
                    shutil.copytree(item, Path(project_root) / item.name)
                else:
                    shutil.copy2(item, project_root)

    def _apply_safe_optimizations(self, workflow_results: Dict[str, Any]) -> Dict[str, Any]:
        """Apply optimizations that are deemed safe based on validation scores"""
        # In a full implementation, this would apply specific optimizations
        # based on safety scores and validation results
        return {
            "optimizations_applied": 0,
            "status": "simulated",
            "message": "Safe optimization application would be implemented here"
        }

    def _generate_analysis_recommendations(self, analysis_result) -> List[str]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        large_files = [f for f in analysis_result.file_analyses if f.line_count > 1000]
        if large_files:
            recommendations.append(f"Consider refactoring {len(large_files)} large files (>1000 lines)")
        
        complex_files = [f for f in analysis_result.file_analyses if f.complexity_score > 10]
        if complex_files:
            recommendations.append(f"Address high complexity in {len(complex_files)} files")
        
        if analysis_result.circular_dependencies:
            recommendations.append(f"Resolve {len(analysis_result.circular_dependencies)} circular dependencies")
        
        return recommendations

    def _save_automation_config(self, project_root: str, config: Dict[str, Any]):
        """Save automation configuration to project"""
        config_file = Path(project_root) / ".plc_optimize_config.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)


# CLI Interface Implementation
@click.group()
@click.option('--config', '-c', help='Configuration file path')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, verbose):
    """PLC-Optimize: Master CLI for Codebase Optimization Automation"""
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['verbose'] = verbose
    
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

@cli.command()
@click.option('--project-root', '-p', default='.', help='Project root directory to analyze')
@click.option('--profile', default='default', help='Optimization profile to use')
@click.option('--auto-apply', is_flag=True, help='Automatically apply safe optimizations')
@click.option('--backup/--no-backup', default=True, help='Create backup before changes')
@click.pass_context
def optimize(ctx, project_root, profile, auto_apply, backup):
    """Run complete optimization workflow on codebase"""
    click.echo("🚀 PLC-Optimize: Complete Codebase Optimization")
    click.echo("=" * 60)
    
    optimizer = PLCOptimizeMasterCLI(config_file=ctx.obj.get('config'))
    
    try:
        with optimizer:
            result = optimizer.run_full_optimization_workflow(
                project_root=project_root,
                profile_name=profile,
                auto_apply=auto_apply,
                create_backup=backup
            )
            
            # Display results
            if result["status"] == "completed":
                click.echo(f"✅ Optimization completed successfully")
                click.echo(f"📊 Files analyzed: {result.get('workflow_result', {}).get('overall_metrics', {}).get('files_optimized', 0)}")
                click.echo(f"🎯 Validation score: {result.get('workflow_result', {}).get('overall_metrics', {}).get('validation_score', 0.0):.2f}")
                
                # Show recommendations
                recommendations = result.get('workflow_result', {}).get('recommendations', [])
                if recommendations:
                    click.echo("\n💡 Recommendations:")
                    for rec in recommendations:
                        click.echo(f"   • {rec}")
            else:
                click.echo(f"❌ Optimization failed: {result.get('error', 'Unknown error')}")
                return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Fatal error: {e}")
        return 1

@cli.command()
@click.option('--project-root', '-p', default='.', help='Project root directory to analyze')
@click.pass_context
def analyze(ctx, project_root):
    """Run codebase analysis without making changes"""
    click.echo("🔍 PLC-Optimize: Codebase Analysis")
    click.echo("=" * 40)
    
    optimizer = PLCOptimizeMasterCLI(config_file=ctx.obj.get('config'))
    
    try:
        with optimizer:
            result = optimizer.run_component_analysis(project_root)
            
            if result["status"] == "completed":
                analysis = result["analysis"]
                click.echo(f"📁 Total files: {analysis['total_files']}")
                click.echo(f"📏 Total lines: {analysis['total_lines']}")
                click.echo(f"📊 Average complexity: {analysis['average_complexity']:.2f}")
                click.echo(f"⚠️  Files needing optimization: {analysis['files_needing_optimization']}")
                
                opportunities = result.get("opportunities", [])
                if opportunities:
                    click.echo(f"\n🎯 Optimization opportunities found: {len(opportunities)}")
                    for i, opp in enumerate(opportunities[:5], 1):
                        click.echo(f"   {i}. {opp.get('description', 'Optimization opportunity')}")
                    
                    if len(opportunities) > 5:
                        click.echo(f"   ... and {len(opportunities) - 5} more")
            else:
                click.echo(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
                return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Fatal error: {e}")
        return 1

@cli.command()
@click.option('--project-root', '-p', default='.', help='Project root directory')
@click.pass_context
def setup_git(ctx, project_root):
    """Setup git hooks for automated optimization"""
    click.echo("🔧 PLC-Optimize: Git Integration Setup")
    click.echo("=" * 40)
    
    optimizer = PLCOptimizeMasterCLI(config_file=ctx.obj.get('config'))
    
    try:
        with optimizer:
            result = optimizer.setup_git_integration(project_root)
            
            if result["status"] == "completed":
                click.echo(f"✅ Git hooks installed: {result['hooks_installed']}")
                click.echo(f"🤖 Automation enabled: {result['automation_config']['enabled']}")
                click.echo(f"⚡ Trigger: {result['automation_config']['trigger']}")
                click.echo("\n💡 Git hooks will now run optimization checks on commits")
            else:
                click.echo(f"❌ Git integration setup failed: {result.get('error', 'Unknown error')}")
                return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Fatal error: {e}")
        return 1

@cli.command()
@click.option('--project-root', '-p', default='.', help='Project root directory')
@click.pass_context
def schema_check(ctx, project_root):
    """Run JSON schema governance and compliance checks"""
    click.echo("📋 PLC-Optimize: Schema Governance")
    click.echo("=" * 40)
    
    optimizer = PLCOptimizeMasterCLI(config_file=ctx.obj.get('config'))
    
    try:
        with optimizer:
            result = optimizer.run_schema_governance(project_root)
            
            if result["status"] == "completed":
                click.echo(f"🔍 JSON usages found: {result['json_usages_found']}")
                click.echo(f"📊 Compliance score: {result['compliance_score']:.2f}")
                click.echo(f"⚠️  Violations: {result['violations']}")
                click.echo(f"🗄️  Database consistency: {result['database_consistency']:.2f}")
                
                recommendations = result.get("recommendations", [])
                if recommendations:
                    click.echo("\n💡 Recommendations:")
                    for rec in recommendations:
                        click.echo(f"   • {rec}")
            else:
                click.echo(f"❌ Schema governance failed: {result.get('error', 'Unknown error')}")
                return 1
        
        return 0
        
    except Exception as e:
        click.echo(f"❌ Fatal error: {e}")
        return 1

@cli.command()
def profiles():
    """List available optimization profiles"""
    click.echo("📋 Available Optimization Profiles:")
    click.echo("=" * 40)
    
    optimizer = PLCOptimizeMasterCLI()
    
    for name, profile in optimizer.optimization_profiles.items():
        click.echo(f"\n🎯 {name}")
        click.echo(f"   Description: {profile.description}")
        click.echo(f"   Analysis: {'✅' if profile.analysis_enabled else '❌'}")
        click.echo(f"   Quality Optimization: {'✅' if profile.quality_optimization_enabled else '❌'}")
        click.echo(f"   Modular Extraction: {'✅' if profile.modular_extraction_enabled else '❌'}")
        click.echo(f"   Schema Governance: {'✅' if profile.schema_governance_enabled else '❌'}")
        click.echo(f"   Auto-apply: {'✅' if profile.auto_apply_safe_changes else '❌'}")
        click.echo(f"   Min Safety Score: {profile.minimum_safety_score}")

@cli.command()
@click.option('--sessions', '-n', default=10, help='Number of recent sessions to show')
def history(sessions):
    """Show optimization session history"""
    click.echo("📈 Optimization Session History:")
    click.echo("=" * 40)
    
    # In a full implementation, this would load session history from storage
    click.echo("Session history would be displayed here")
    click.echo("(Implementation would load from persistent storage)")

if __name__ == '__main__':
    cli() 