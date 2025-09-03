#!/usr/bin/env python3
"""
🧪 Phase 21: Comprehensive CLI Testing Orchestrator

Comprehensive testing framework for Phase 21.1 and 21.2 with cross-phase
integration validation following AI Task Orchestrator methodology.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (integrated multi-phase testing)
Context Management: Cross-phase validation with comprehensive reporting
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Testing Objectives:
- Phase 21.1: Core CLI Infrastructure validation
- Phase 21.2: Schema Management Commands validation
- Cross-phase integration testing
- Performance and reliability assessment
- Production readiness validation

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21 - Comprehensive CLI Testing
Dependencies: Phase 20 (JSON Schema Framework), Phase 21.1, Phase 21.2
"""

import asyncio
import json
import logging
import sys
import time
import traceback
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import existing testing orchestrators
try:
    from scripts.ai.phase21_1_testing_orchestrator import Phase21_1TestingOrchestrator
    from scripts.ai.phase21_2_testing_orchestrator import Phase21_2TestingOrchestrator
    ORCHESTRATORS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import phase testing orchestrators: {e}")
    ORCHESTRATORS_AVAILABLE = False

from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.tree import Tree

console = Console()

# =============================================================================
# COMPREHENSIVE TESTING FRAMEWORK
# =============================================================================

class ValidationLevel(Enum):
    """Validation level enumeration"""
    CRITICAL = "critical"
    WARNING = "warning"
    PASSED = "passed"
    FAILED = "failed"

@dataclass
class PhaseTestResult:
    """Phase testing result container"""
    phase_id: str
    phase_name: str
    status: ValidationLevel
    overall_score: float
    execution_time: float
    test_count: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    recommendations: List[str] = field(default_factory=list)
    detailed_results: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossPhaseIntegrationResult:
    """Cross-phase integration test result"""
    integration_name: str
    status: ValidationLevel
    score: float
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ComprehensiveValidationResult:
    """Comprehensive validation result container"""
    session_id: str
    timestamp: str
    overall_status: ValidationLevel
    overall_score: float
    total_execution_time: float
    phase21_1_result: Optional[PhaseTestResult] = None
    phase21_2_result: Optional[PhaseTestResult] = None
    integration_results: List[CrossPhaseIntegrationResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    production_readiness: Dict[str, Any] = field(default_factory=dict)

class Phase21ComprehensiveTestingOrchestrator:
    """Comprehensive testing orchestrator for Phase 21"""

    def __init__(self):
        """Initialize comprehensive testing orchestrator"""
        self.session_id = f"phase21_comprehensive_{int(time.time())}"
        self.start_time = datetime.now()
        self.project_root = Path(__file__).parent.parent.parent
        self.results_dir = self.project_root / "results" / "phase21"
        self.temp_dir = None

        # Ensure results directory exists
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize orchestrators
        if ORCHESTRATORS_AVAILABLE:
            self.phase21_1_orchestrator = Phase21_1TestingOrchestrator()
            self.phase21_2_orchestrator = Phase21_2TestingOrchestrator()
        else:
            self.phase21_1_orchestrator = None
            self.phase21_2_orchestrator = None

        logger.info(f"🚀 Comprehensive Testing Session: {self.session_id}")

    async def execute_comprehensive_testing(self) -> ComprehensiveValidationResult:
        """Execute comprehensive testing following AI Task Orchestrator methodology"""
        console.print(Panel(
            "[bold blue]🧪 Phase 21: Comprehensive CLI Testing[/bold blue]\n\n"
            "Following AI Task Orchestrator methodology for systematic validation:\n"
            "• Phase 21.1: Core CLI Infrastructure\n"
            "• Phase 21.2: Schema Management Commands\n"
            "• Cross-phase Integration\n"
            "• Production Readiness Assessment",
            title="🎯 Comprehensive Testing Session",
            border_style="blue"
        ))

        try:
            # Step 1: Task Analysis (following AI Task Orchestrator)
            await self._display_task_analysis()

            # Step 2: Phase 21.1 Testing
            phase21_1_result = await self._execute_phase21_1_testing()

            # Step 3: Phase 21.2 Testing
            phase21_2_result = await self._execute_phase21_2_testing()

            # Step 4: Cross-phase Integration Testing
            integration_results = await self._execute_integration_testing(
                phase21_1_result, phase21_2_result
            )

            # Step 5: Production Readiness Assessment
            production_readiness = await self._assess_production_readiness(
                phase21_1_result, phase21_2_result, integration_results
            )

            # Step 6: Generate Comprehensive Results
            comprehensive_result = await self._generate_comprehensive_results(
                phase21_1_result, phase21_2_result, integration_results, production_readiness
            )

            # Step 7: Save Results and Generate Reports
            await self._save_comprehensive_results(comprehensive_result)

            return comprehensive_result

        except Exception as e:
            logger.error(f"❌ Comprehensive testing failed: {e}")
            traceback.print_exc()
            raise

    async def _display_task_analysis(self):
        """Display task analysis following AI Task Orchestrator methodology"""
        console.print("\n[bold]📋 Task Analysis (AI Task Orchestrator Step 1)[/bold]")

        analysis_table = Table(title="Comprehensive Testing Analysis")
        analysis_table.add_column("Aspect", style="bold")
        analysis_table.add_column("Details", style="cyan")

        analysis_table.add_row("Task Classification", "COMPLEX (Multi-phase integration testing)")
        analysis_table.add_row("Estimated Time", "15-20 minutes comprehensive validation")
        analysis_table.add_row("Context Management", "Cross-phase dependency validation required")
        analysis_table.add_row("Safety Level", "Production systems (CLI infrastructure)")
        analysis_table.add_row("Dependencies", "Phase 20 (Schemas), Phase 21.1 (CLI), Phase 21.2 (Commands)")

        console.print(analysis_table)

        # Show testing scope
        scope_tree = Tree("🎯 Testing Scope")

        phase21_1_branch = scope_tree.add("Phase 21.1: Core CLI Infrastructure")
        phase21_1_branch.add("CLI Entry Point & Command Structure")
        phase21_1_branch.add("Configuration Management System")
        phase21_1_branch.add("Authentication & Authorization")
        phase21_1_branch.add("Session Management")
        phase21_1_branch.add("CLX PLC Integration Readiness")

        phase21_2_branch = scope_tree.add("Phase 21.2: Schema Management Commands")
        phase21_2_branch.add("Schema Listing & Discovery (4 commands)")
        phase21_2_branch.add("Schema Creation & Wizard (3 commands)")
        phase21_2_branch.add("Schema Modification & Versioning (3 commands)")
        phase21_2_branch.add("Schema Validation & Testing (3 commands)")

        integration_branch = scope_tree.add("Cross-Phase Integration")
        integration_branch.add("CLI Infrastructure ↔ Schema Commands")
        integration_branch.add("Authentication ↔ Permission System")
        integration_branch.add("Configuration ↔ Schema Management")
        integration_branch.add("Phase 20 Schema Framework Integration")

        console.print(scope_tree)
        await asyncio.sleep(1)  # Allow user to review

    async def _execute_phase21_1_testing(self) -> PhaseTestResult:
        """Execute Phase 21.1 testing with progress tracking"""
        console.print("\n[bold]🔧 Phase 21.1: Core CLI Infrastructure Testing[/bold]")

        if not self.phase21_1_orchestrator:
            console.print("[red]❌ Phase 21.1 testing orchestrator not available[/red]")
            return PhaseTestResult(
                phase_id="21.1",
                phase_name="Core CLI Infrastructure",
                status=ValidationLevel.FAILED,
                overall_score=0.0,
                execution_time=0.0,
                test_count=0,
                passed_tests=0,
                failed_tests=1,
                warning_tests=0,
                recommendations=["Phase 21.1 testing orchestrator needs to be available"]
            )

        start_time = time.time()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Executing Phase 21.1 tests...", total=1)

                # Execute Phase 21.1 testing
                validation_result = await self.phase21_1_orchestrator.execute_comprehensive_testing()

                progress.update(task, completed=1)

            execution_time = time.time() - start_time

            # Convert validation result to PhaseTestResult
            phase_result = PhaseTestResult(
                phase_id=validation_result.phase_id,
                phase_name=validation_result.phase_name,
                status=ValidationLevel(validation_result.status),
                overall_score=validation_result.overall_score,
                execution_time=execution_time,
                test_count=len(validation_result.component_results),
                passed_tests=len([r for r in validation_result.component_results if r.status == "passed"]),
                failed_tests=len([r for r in validation_result.component_results if r.status == "failed"]),
                warning_tests=len([r for r in validation_result.component_results if r.status == "warning"]),
                recommendations=validation_result.recommendations,
                detailed_results=asdict(validation_result)
            )

            # Display results
            self._display_phase_results("21.1", phase_result)

            return phase_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Phase 21.1 testing failed: {e}")

            return PhaseTestResult(
                phase_id="21.1",
                phase_name="Core CLI Infrastructure",
                status=ValidationLevel.FAILED,
                overall_score=0.0,
                execution_time=execution_time,
                test_count=0,
                passed_tests=0,
                failed_tests=1,
                warning_tests=0,
                recommendations=[f"Phase 21.1 testing failed: {str(e)}"]
            )

    async def _execute_phase21_2_testing(self) -> PhaseTestResult:
        """Execute Phase 21.2 testing with progress tracking"""
        console.print("\n[bold]🔧 Phase 21.2: Schema Management Commands Testing[/bold]")

        if not self.phase21_2_orchestrator:
            console.print("[red]❌ Phase 21.2 testing orchestrator not available[/red]")
            return PhaseTestResult(
                phase_id="21.2",
                phase_name="Schema Management Commands",
                status=ValidationLevel.FAILED,
                overall_score=0.0,
                execution_time=0.0,
                test_count=0,
                passed_tests=0,
                failed_tests=1,
                warning_tests=0,
                recommendations=["Phase 21.2 testing orchestrator needs to be available"]
            )

        start_time = time.time()

        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                task = progress.add_task("Executing Phase 21.2 tests...", total=1)

                # Execute Phase 21.2 testing
                test_results = await self.phase21_2_orchestrator.run_comprehensive_testing()

                progress.update(task, completed=1)

            execution_time = time.time() - start_time

            # Convert test results to PhaseTestResult
            summary = test_results.get("summary", {})
            status_map = {"PASSED": ValidationLevel.PASSED, "WARNING": ValidationLevel.WARNING, "FAILED": ValidationLevel.FAILED}

            phase_result = PhaseTestResult(
                phase_id="21.2",
                phase_name="Schema Management Commands",
                status=status_map.get(test_results.get("overall_status", "FAILED"), ValidationLevel.FAILED),
                overall_score=summary.get("success_rate", 0.0),
                execution_time=execution_time,
                test_count=summary.get("total_tests", 0),
                passed_tests=summary.get("passed", 0),
                failed_tests=summary.get("failed", 0),
                warning_tests=summary.get("warnings", 0),
                recommendations=test_results.get("recommendations", []),
                detailed_results=test_results
            )

            # Display results
            self._display_phase_results("21.2", phase_result)

            return phase_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Phase 21.2 testing failed: {e}")

            return PhaseTestResult(
                phase_id="21.2",
                phase_name="Schema Management Commands",
                status=ValidationLevel.FAILED,
                overall_score=0.0,
                execution_time=execution_time,
                test_count=0,
                passed_tests=0,
                failed_tests=1,
                warning_tests=0,
                recommendations=[f"Phase 21.2 testing failed: {str(e)}"]
            )

    def _display_phase_results(self, phase_id: str, result: PhaseTestResult):
        """Display phase testing results"""
        status_colors = {
            ValidationLevel.PASSED: "green",
            ValidationLevel.WARNING: "yellow",
            ValidationLevel.FAILED: "red",
            ValidationLevel.CRITICAL: "bright_red"
        }

        status_icons = {
            ValidationLevel.PASSED: "✅",
            ValidationLevel.WARNING: "⚠️",
            ValidationLevel.FAILED: "❌",
            ValidationLevel.CRITICAL: "🚨"
        }

        color = status_colors.get(result.status, "white")
        icon = status_icons.get(result.status, "❓")

        console.print(f"\n{icon} [bold {color}]Phase {phase_id} Results[/bold {color}]")
        console.print(f"Score: [bold]{result.overall_score:.1f}%[/bold]")
        console.print(f"Tests: {result.passed_tests} passed, {result.warning_tests} warnings, {result.failed_tests} failed")
        console.print(f"Duration: {result.execution_time:.2f}s")

    async def _execute_integration_testing(self,
                                         phase21_1_result: PhaseTestResult,
                                         phase21_2_result: PhaseTestResult) -> List[CrossPhaseIntegrationResult]:
        """Execute cross-phase integration testing"""
        console.print("\n[bold]🔗 Cross-Phase Integration Testing[/bold]")

        integration_results = []

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=console
        ) as progress:

            # Test 1: CLI Infrastructure + Schema Commands Integration
            task1 = progress.add_task("Testing CLI ↔ Schema Commands integration...", total=1)

            cli_schema_integration = await self._test_cli_schema_integration(
                phase21_1_result, phase21_2_result
            )
            integration_results.append(cli_schema_integration)

            progress.update(task1, completed=1)

            # Test 2: Authentication System Integration
            task2 = progress.add_task("Testing Authentication integration...", total=1)

            auth_integration = await self._test_authentication_integration(
                phase21_1_result, phase21_2_result
            )
            integration_results.append(auth_integration)

            progress.update(task2, completed=1)

            # Test 3: Configuration System Integration
            task3 = progress.add_task("Testing Configuration integration...", total=1)

            config_integration = await self._test_configuration_integration(
                phase21_1_result, phase21_2_result
            )
            integration_results.append(config_integration)

            progress.update(task3, completed=1)

            # Test 4: Phase 20 Schema Framework Integration
            task4 = progress.add_task("Testing Phase 20 integration...", total=1)

            phase20_integration = await self._test_phase20_integration(
                phase21_1_result, phase21_2_result
            )
            integration_results.append(phase20_integration)

            progress.update(task4, completed=1)

        # Display integration results
        self._display_integration_results(integration_results)

        return integration_results

    async def _test_cli_schema_integration(self,
                                         phase21_1_result: PhaseTestResult,
                                         phase21_2_result: PhaseTestResult) -> CrossPhaseIntegrationResult:
        """Test CLI infrastructure and schema commands integration"""
        start_time = time.time()

        try:
            # Check if both phases are functional
            cli_functional = phase21_1_result.status in [ValidationLevel.PASSED, ValidationLevel.WARNING]
            schema_functional = phase21_2_result.status in [ValidationLevel.PASSED, ValidationLevel.WARNING]

            if not cli_functional or not schema_functional:
                return CrossPhaseIntegrationResult(
                    integration_name="CLI ↔ Schema Commands",
                    status=ValidationLevel.FAILED,
                    score=0.0,
                    details={
                        "cli_functional": cli_functional,
                        "schema_functional": schema_functional,
                        "error": "Base phases not functional"
                    }
                )

            # Test CLI command structure includes schema commands
            cli_path = self.project_root / "cli" / "plc_control_loop_cli.py"
            if not cli_path.exists():
                return CrossPhaseIntegrationResult(
                    integration_name="CLI ↔ Schema Commands",
                    status=ValidationLevel.FAILED,
                    score=0.0,
                    details={"error": "CLI file not found"}
                )

            # Check schema command integration in CLI
            with open(cli_path) as f:
                cli_content = f.read()

            schema_integration_indicators = [
                "schema_commands",
                "from cli.commands.schema",
                "add_command(schema_commands"
            ]

            integration_score = 0
            found_indicators = []

            for indicator in schema_integration_indicators:
                if indicator in cli_content:
                    integration_score += 1
                    found_indicators.append(indicator)

            final_score = (integration_score / len(schema_integration_indicators)) * 100

            if final_score >= 80:
                status = ValidationLevel.PASSED
            elif final_score >= 60:
                status = ValidationLevel.WARNING
            else:
                status = ValidationLevel.FAILED

            execution_time = time.time() - start_time

            return CrossPhaseIntegrationResult(
                integration_name="CLI ↔ Schema Commands",
                status=status,
                score=final_score,
                details={
                    "integration_indicators_found": found_indicators,
                    "integration_score": f"{integration_score}/{len(schema_integration_indicators)}",
                    "execution_time": execution_time
                }
            )

        except Exception as e:
            return CrossPhaseIntegrationResult(
                integration_name="CLI ↔ Schema Commands",
                status=ValidationLevel.FAILED,
                score=0.0,
                details={"error": str(e)}
            )

    async def _test_authentication_integration(self,
                                             phase21_1_result: PhaseTestResult,
                                             phase21_2_result: PhaseTestResult) -> CrossPhaseIntegrationResult:
        """Test authentication system integration"""
        start_time = time.time()

        try:
            # Check if authentication components exist
            auth_files = [
                self.project_root / "cli" / "auth" / "auth_manager.py",
                self.project_root / "cli" / "auth" / "session_manager.py"
            ]

            auth_score = 0
            existing_files = []

            for auth_file in auth_files:
                if auth_file.exists():
                    auth_score += 1
                    existing_files.append(str(auth_file.name))

            # Check for permission decorators in schema commands
            schema_commands_file = self.project_root / "cli" / "commands" / "schema.py"
            permission_integration = False

            if schema_commands_file.exists():
                with open(schema_commands_file) as f:
                    schema_content = f.read()

                if "requires_permission" in schema_content:
                    permission_integration = True
                    auth_score += 1

            final_score = (auth_score / 3) * 100

            if final_score >= 80:
                status = ValidationLevel.PASSED
            elif final_score >= 60:
                status = ValidationLevel.WARNING
            else:
                status = ValidationLevel.FAILED

            execution_time = time.time() - start_time

            return CrossPhaseIntegrationResult(
                integration_name="Authentication Integration",
                status=status,
                score=final_score,
                details={
                    "auth_files_found": existing_files,
                    "permission_integration": permission_integration,
                    "execution_time": execution_time
                }
            )

        except Exception as e:
            return CrossPhaseIntegrationResult(
                integration_name="Authentication Integration",
                status=ValidationLevel.FAILED,
                score=0.0,
                details={"error": str(e)}
            )

    async def _test_configuration_integration(self,
                                            phase21_1_result: PhaseTestResult,
                                            phase21_2_result: PhaseTestResult) -> CrossPhaseIntegrationResult:
        """Test configuration system integration"""
        start_time = time.time()

        try:
            # Check if configuration manager exists
            config_file = self.project_root / "cli" / "config_manager.py"

            if not config_file.exists():
                return CrossPhaseIntegrationResult(
                    integration_name="Configuration Integration",
                    status=ValidationLevel.FAILED,
                    score=0.0,
                    details={"error": "Configuration manager not found"}
                )

            # Check configuration features
            with open(config_file) as f:
                config_content = f.read()

            config_features = [
                "class ConfigManager",
                "load_config",
                "save_config",
                "YAML"
            ]

            feature_score = 0
            found_features = []

            for feature in config_features:
                if feature in config_content:
                    feature_score += 1
                    found_features.append(feature)

            final_score = (feature_score / len(config_features)) * 100

            if final_score >= 80:
                status = ValidationLevel.PASSED
            elif final_score >= 60:
                status = ValidationLevel.WARNING
            else:
                status = ValidationLevel.FAILED

            execution_time = time.time() - start_time

            return CrossPhaseIntegrationResult(
                integration_name="Configuration Integration",
                status=status,
                score=final_score,
                details={
                    "config_features_found": found_features,
                    "feature_score": f"{feature_score}/{len(config_features)}",
                    "execution_time": execution_time
                }
            )

        except Exception as e:
            return CrossPhaseIntegrationResult(
                integration_name="Configuration Integration",
                status=ValidationLevel.FAILED,
                score=0.0,
                details={"error": str(e)}
            )

    async def _test_phase20_integration(self,
                                       phase21_1_result: PhaseTestResult,
                                       phase21_2_result: PhaseTestResult) -> CrossPhaseIntegrationResult:
        """Test Phase 20 schema framework integration"""
        start_time = time.time()

        try:
            # Check for Phase 20 schema framework
            phase20_paths = [
                self.project_root / "schemas" / "control-loops",
                self.project_root / "schemas" / "control-loops" / "base",
                self.project_root / "schemas" / "control-loops" / "subtypes"
            ]

            integration_score = 0
            existing_paths = []

            for path in phase20_paths:
                if path.exists():
                    integration_score += 1
                    existing_paths.append(str(path.name))

            # Check for schema manager imports in CLI
            schema_manager_integration = False
            cli_files = [
                self.project_root / "cli" / "commands" / "schema.py",
                self.project_root / "cli" / "plc_control_loop_cli.py"
            ]

            for cli_file in cli_files:
                if cli_file.exists():
                    with open(cli_file) as f:
                        content = f.read()

                    if "schema" in content.lower() and ("manager" in content.lower() or "registry" in content.lower()):
                        schema_manager_integration = True
                        integration_score += 1
                        break

            final_score = (integration_score / 4) * 100

            if final_score >= 75:
                status = ValidationLevel.PASSED
            elif final_score >= 50:
                status = ValidationLevel.WARNING
            else:
                status = ValidationLevel.FAILED

            execution_time = time.time() - start_time

            return CrossPhaseIntegrationResult(
                integration_name="Phase 20 Integration",
                status=status,
                score=final_score,
                details={
                    "phase20_paths_found": existing_paths,
                    "schema_manager_integration": schema_manager_integration,
                    "execution_time": execution_time
                }
            )

        except Exception as e:
            return CrossPhaseIntegrationResult(
                integration_name="Phase 20 Integration",
                status=ValidationLevel.FAILED,
                score=0.0,
                details={"error": str(e)}
            )

    def _display_integration_results(self, integration_results: List[CrossPhaseIntegrationResult]):
        """Display integration testing results"""
        console.print("\n[bold]🔗 Integration Test Results[/bold]")

        integration_table = Table()
        integration_table.add_column("Integration", style="bold")
        integration_table.add_column("Status", style="white")
        integration_table.add_column("Score", style="cyan")
        integration_table.add_column("Details", style="dim")

        for result in integration_results:
            status_icons = {
                ValidationLevel.PASSED: "✅ PASSED",
                ValidationLevel.WARNING: "⚠️ WARNING",
                ValidationLevel.FAILED: "❌ FAILED"
            }

            status_text = status_icons.get(result.status, "❓ UNKNOWN")
            score_text = f"{result.score:.1f}%"

            # Create summary of details
            details_summary = []
            if "error" in result.details:
                details_summary.append(f"Error: {result.details['error']}")
            if "integration_score" in result.details:
                details_summary.append(f"Features: {result.details['integration_score']}")
            if "execution_time" in result.details:
                details_summary.append(f"Time: {result.details['execution_time']:.3f}s")

            integration_table.add_row(
                result.integration_name,
                status_text,
                score_text,
                "; ".join(details_summary)
            )

        console.print(integration_table)

    async def _assess_production_readiness(self,
                                         phase21_1_result: PhaseTestResult,
                                         phase21_2_result: PhaseTestResult,
                                         integration_results: List[CrossPhaseIntegrationResult]) -> Dict[str, Any]:
        """Assess production readiness"""
        console.print("\n[bold]🏭 Production Readiness Assessment[/bold]")

        # Calculate overall readiness scores
        phase_scores = []
        if phase21_1_result:
            phase_scores.append(phase21_1_result.overall_score)
        if phase21_2_result:
            phase_scores.append(phase21_2_result.overall_score)

        integration_scores = [r.score for r in integration_results]

        # Weighted scoring
        phase_weight = 0.7
        integration_weight = 0.3

        phase_avg = sum(phase_scores) / len(phase_scores) if phase_scores else 0
        integration_avg = sum(integration_scores) / len(integration_scores) if integration_scores else 0

        overall_readiness_score = (phase_avg * phase_weight) + (integration_avg * integration_weight)

        # Determine readiness level
        if overall_readiness_score >= 90:
            readiness_level = "PRODUCTION_READY"
            readiness_color = "green"
        elif overall_readiness_score >= 75:
            readiness_level = "READY_WITH_MONITORING"
            readiness_color = "yellow"
        elif overall_readiness_score >= 60:
            readiness_level = "REQUIRES_IMPROVEMENT"
            readiness_color = "orange"
        else:
            readiness_level = "NOT_READY"
            readiness_color = "red"

        # Critical requirements check
        critical_requirements = {
            "CLI Infrastructure Functional": phase21_1_result and phase21_1_result.status != ValidationLevel.FAILED,
            "Schema Commands Available": phase21_2_result and phase21_2_result.status != ValidationLevel.FAILED,
            "Integration Working": len([r for r in integration_results if r.status == ValidationLevel.PASSED]) >= 2,
            "No Critical Failures": all(r.status != ValidationLevel.CRITICAL for r in integration_results)
        }

        critical_passed = sum(1 for req, passed in critical_requirements.items() if passed)
        critical_total = len(critical_requirements)

        production_readiness = {
            "overall_score": overall_readiness_score,
            "readiness_level": readiness_level,
            "readiness_color": readiness_color,
            "critical_requirements": critical_requirements,
            "critical_score": (critical_passed / critical_total) * 100,
            "phase_scores": {
                "phase_21_1": phase21_1_result.overall_score if phase21_1_result else 0,
                "phase_21_2": phase21_2_result.overall_score if phase21_2_result else 0
            },
            "integration_scores": {r.integration_name: r.score for r in integration_results},
            "recommendations": self._generate_production_recommendations(
                overall_readiness_score, critical_requirements, integration_results
            )
        }

        # Display readiness assessment
        self._display_production_readiness(production_readiness)

        return production_readiness

    def _generate_production_recommendations(self,
                                           overall_score: float,
                                           critical_requirements: Dict[str, bool],
                                           integration_results: List[CrossPhaseIntegrationResult]) -> List[str]:
        """Generate production deployment recommendations"""
        recommendations = []

        # Score-based recommendations
        if overall_score >= 90:
            recommendations.append("✅ Ready for immediate production deployment")
        elif overall_score >= 75:
            recommendations.append("⚠️ Ready for production with enhanced monitoring")
        elif overall_score >= 60:
            recommendations.append("🔧 Address identified issues before production deployment")
        else:
            recommendations.append("🚨 Significant improvements required before production use")

        # Critical requirement recommendations
        for requirement, passed in critical_requirements.items():
            if not passed:
                recommendations.append(f"🔴 CRITICAL: Address {requirement}")

        # Integration-specific recommendations
        failed_integrations = [r for r in integration_results if r.status == ValidationLevel.FAILED]
        for integration in failed_integrations:
            recommendations.append(f"🔧 Fix {integration.integration_name} integration")

        # CLX PLC specific recommendations
        recommendations.extend([
            "🏭 CLX PLC Integration: Validate read-only connection enforcement",
            "🔐 Security: Review authentication system for production use",
            "📊 Monitoring: Implement comprehensive logging for production operations",
            "⚡ Performance: Validate response times under production load"
        ])

        return recommendations

    def _display_production_readiness(self, readiness: Dict[str, Any]):
        """Display production readiness assessment"""
        color = readiness["readiness_color"]
        level = readiness["readiness_level"]
        score = readiness["overall_score"]

        console.print(Panel(
            f"[bold {color}]Production Readiness: {level}[/bold {color}]\n\n"
            f"[bold]Overall Score:[/bold] {score:.1f}%\n"
            f"[bold]Critical Requirements:[/bold] {readiness['critical_score']:.1f}% met\n\n"
            f"[bold]Phase Scores:[/bold]\n"
            f"• Phase 21.1: {readiness['phase_scores']['phase_21_1']:.1f}%\n"
            f"• Phase 21.2: {readiness['phase_scores']['phase_21_2']:.1f}%\n\n"
            f"[bold]Integration Scores:[/bold]\n" +
            "\n".join([f"• {name}: {score:.1f}%" for name, score in readiness['integration_scores'].items()]),
            title="🏭 Production Readiness Assessment",
            border_style=color
        ))

        # Display critical requirements
        console.print("\n[bold]Critical Requirements Status:[/bold]")
        for requirement, passed in readiness["critical_requirements"].items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            console.print(f"  {status} {requirement}")

    async def _generate_comprehensive_results(self,
                                            phase21_1_result: PhaseTestResult,
                                            phase21_2_result: PhaseTestResult,
                                            integration_results: List[CrossPhaseIntegrationResult],
                                            production_readiness: Dict[str, Any]) -> ComprehensiveValidationResult:
        """Generate comprehensive validation results"""
        end_time = datetime.now()
        total_execution_time = (end_time - self.start_time).total_seconds()

        # Determine overall status
        all_scores = []
        if phase21_1_result:
            all_scores.append(phase21_1_result.overall_score)
        if phase21_2_result:
            all_scores.append(phase21_2_result.overall_score)
        all_scores.extend([r.score for r in integration_results])

        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0

        # Determine overall status
        if overall_score >= 90:
            overall_status = ValidationLevel.PASSED
        elif overall_score >= 75:
            overall_status = ValidationLevel.WARNING
        else:
            overall_status = ValidationLevel.FAILED

        # Generate comprehensive recommendations
        recommendations = []

        if phase21_1_result:
            recommendations.extend(phase21_1_result.recommendations)
        if phase21_2_result:
            recommendations.extend(phase21_2_result.recommendations)

        recommendations.extend(production_readiness.get("recommendations", []))

        return ComprehensiveValidationResult(
            session_id=self.session_id,
            timestamp=end_time.isoformat(),
            overall_status=overall_status,
            overall_score=overall_score,
            total_execution_time=total_execution_time,
            phase21_1_result=phase21_1_result,
            phase21_2_result=phase21_2_result,
            integration_results=integration_results,
            recommendations=list(set(recommendations)),  # Remove duplicates
            production_readiness=production_readiness
        )

    async def _save_comprehensive_results(self, result: ComprehensiveValidationResult):
        """Save comprehensive results and generate reports"""
        console.print("\n[bold]💾 Saving Comprehensive Results[/bold]")

        # Save JSON results
        json_file = self.results_dir / f"phase21_comprehensive_results_{self.session_id}.json"

        # Convert result to JSON-serializable format
        result_dict = asdict(result)

        # Handle enum serialization
        def convert_enums(obj):
            if isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            elif isinstance(obj, ValidationLevel):
                return obj.value
            elif hasattr(obj, 'value'):  # Handle any enum with .value attribute
                return obj.value
            else:
                return obj

        result_dict = convert_enums(result_dict)

        with open(json_file, 'w') as f:
            json.dump(result_dict, f, indent=2)

        # Generate markdown report
        markdown_file = self.results_dir / f"phase21_comprehensive_report_{self.session_id}.md"
        markdown_content = self._generate_markdown_report(result)

        with open(markdown_file, 'w') as f:
            f.write(markdown_content)

        console.print("✅ Results saved:")
        console.print(f"  📄 JSON: {json_file}")
        console.print(f"  📝 Report: {markdown_file}")

        return json_file, markdown_file

    def _generate_markdown_report(self, result: ComprehensiveValidationResult) -> str:
        """Generate comprehensive markdown report"""
        lines = [
            "# 🧪 Phase 21: Comprehensive CLI Testing Report",
            "",
            f"**Session ID**: {result.session_id}",
            f"**Timestamp**: {result.timestamp}",
            f"**Overall Status**: {result.overall_status.value.upper()}",
            f"**Overall Score**: {result.overall_score:.1f}%",
            f"**Total Execution Time**: {result.total_execution_time:.2f} seconds",
            "",
            "## 📊 Executive Summary",
            "",
            "This comprehensive testing session validated both Phase 21.1 (Core CLI Infrastructure) and Phase 21.2 (Schema Management Commands) with cross-phase integration testing following the AI Task Orchestrator methodology.",
            "",
            "### Key Results:",
        ]

        if result.phase21_1_result:
            lines.extend([
                f"- **Phase 21.1**: {result.phase21_1_result.overall_score:.1f}% ({result.phase21_1_result.status.value})",
                f"  - Tests: {result.phase21_1_result.passed_tests} passed, {result.phase21_1_result.warning_tests} warnings, {result.phase21_1_result.failed_tests} failed"
            ])

        if result.phase21_2_result:
            lines.extend([
                f"- **Phase 21.2**: {result.phase21_2_result.overall_score:.1f}% ({result.phase21_2_result.status.value})",
                f"  - Tests: {result.phase21_2_result.passed_tests} passed, {result.phase21_2_result.warning_tests} warnings, {result.phase21_2_result.failed_tests} failed"
            ])

        lines.extend([
            f"- **Integration**: {len([r for r in result.integration_results if r.status == ValidationLevel.PASSED])} of {len(result.integration_results)} integrations passing",
            f"- **Production Readiness**: {result.production_readiness['readiness_level']} ({result.production_readiness['overall_score']:.1f}%)",
            "",
            "## 🔧 Phase 21.1: Core CLI Infrastructure",
            ""
        ])

        if result.phase21_1_result:
            lines.extend([
                f"**Status**: {result.phase21_1_result.status.value.upper()}",
                f"**Score**: {result.phase21_1_result.overall_score:.1f}%",
                f"**Duration**: {result.phase21_1_result.execution_time:.2f}s",
                "",
                "### Test Results:",
                f"- ✅ **Passed**: {result.phase21_1_result.passed_tests}",
                f"- ⚠️ **Warnings**: {result.phase21_1_result.warning_tests}",
                f"- ❌ **Failed**: {result.phase21_1_result.failed_tests}",
                ""
            ])

        lines.extend([
            "## 🔧 Phase 21.2: Schema Management Commands",
            ""
        ])

        if result.phase21_2_result:
            lines.extend([
                f"**Status**: {result.phase21_2_result.status.value.upper()}",
                f"**Score**: {result.phase21_2_result.overall_score:.1f}%",
                f"**Duration**: {result.phase21_2_result.execution_time:.2f}s",
                "",
                "### Test Results:",
                f"- ✅ **Passed**: {result.phase21_2_result.passed_tests}",
                f"- ⚠️ **Warnings**: {result.phase21_2_result.warning_tests}",
                f"- ❌ **Failed**: {result.phase21_2_result.failed_tests}",
                ""
            ])

        lines.extend([
            "## 🔗 Cross-Phase Integration Results",
            ""
        ])

        for integration in result.integration_results:
            status_icon = {"passed": "✅", "warning": "⚠️", "failed": "❌"}.get(integration.status.value, "❓")
            lines.extend([
                f"### {status_icon} {integration.integration_name}",
                f"**Score**: {integration.score:.1f}%",
                f"**Status**: {integration.status.value.upper()}",
                ""
            ])

        lines.extend([
            "## 🏭 Production Readiness Assessment",
            "",
            f"**Readiness Level**: {result.production_readiness['readiness_level']}",
            f"**Overall Score**: {result.production_readiness['overall_score']:.1f}%",
            f"**Critical Requirements**: {result.production_readiness['critical_score']:.1f}% met",
            "",
            "### Critical Requirements Status:",
            ""
        ])

        for requirement, passed in result.production_readiness["critical_requirements"].items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            lines.append(f"- {status} {requirement}")

        lines.extend([
            "",
            "## 🎯 Recommendations",
            ""
        ])

        for i, recommendation in enumerate(result.recommendations, 1):
            lines.append(f"{i}. {recommendation}")

        lines.extend([
            "",
            "## 📈 Next Steps",
            "",
            "### Immediate Actions:",
        ])

        failed_integrations = [r for r in result.integration_results if r.status == ValidationLevel.FAILED]
        if failed_integrations:
            lines.append("- Address failed integrations:")
            for integration in failed_integrations:
                lines.append(f"  - Fix {integration.integration_name}")

        if result.overall_score >= 75:
            lines.extend([
                "- Proceed with production deployment planning",
                "- Implement enhanced monitoring and logging",
                "- Conduct CLX PLC integration testing"
            ])
        else:
            lines.extend([
                "- Address critical issues before production consideration",
                "- Re-run comprehensive testing after fixes",
                "- Review failed test cases and implementation gaps"
            ])

        lines.extend([
            "",
            "### Future Enhancements:",
            "- Phase 21.3: Instance Management Commands",
            "- CLX PLC read-only integration",
            "- Advanced CLI features and batch operations",
            "- Performance optimization and monitoring",
            "",
            "---",
            "",
            f"**Report Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "**AI Task Orchestrator Methodology**: Systematic multi-phase validation complete"
        ])

        return "\n".join(lines)

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main execution function following AI Task Orchestrator methodology"""
    orchestrator = Phase21ComprehensiveTestingOrchestrator()

    try:
        # Execute comprehensive testing
        result = await orchestrator.execute_comprehensive_testing()

        # Display final results summary
        console.print("\n" + "="*80)
        console.print("[bold]🎯 PHASE 21 COMPREHENSIVE TESTING COMPLETE[/bold]")
        console.print("="*80)

        status_colors = {
            ValidationLevel.PASSED: "green",
            ValidationLevel.WARNING: "yellow",
            ValidationLevel.FAILED: "red"
        }

        color = status_colors.get(result.overall_status, "white")

        console.print(f"[bold {color}]Overall Status: {result.overall_status.value.upper()}[/bold {color}]")
        console.print(f"[bold]Overall Score: {result.overall_score:.1f}%[/bold]")
        console.print(f"[bold]Production Readiness: {result.production_readiness['readiness_level']}[/bold]")
        console.print(f"Session Duration: {result.total_execution_time:.2f} seconds")

        # Summary statistics
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_warnings = 0

        if result.phase21_1_result:
            total_tests += result.phase21_1_result.test_count
            total_passed += result.phase21_1_result.passed_tests
            total_failed += result.phase21_1_result.failed_tests
            total_warnings += result.phase21_1_result.warning_tests

        if result.phase21_2_result:
            total_tests += result.phase21_2_result.test_count
            total_passed += result.phase21_2_result.passed_tests
            total_failed += result.phase21_2_result.failed_tests
            total_warnings += result.phase21_2_result.warning_tests

        console.print(f"\nTotal Tests: {total_tests}")
        console.print(f"✅ Passed: {total_passed}")
        console.print(f"⚠️ Warnings: {total_warnings}")
        console.print(f"❌ Failed: {total_failed}")

        integration_passed = len([r for r in result.integration_results if r.status == ValidationLevel.PASSED])
        console.print(f"🔗 Integration Tests: {integration_passed}/{len(result.integration_results)} passed")

        return result

    except Exception as e:
        console.print(f"[red]❌ Comprehensive testing failed: {e}[/red]")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(main())
