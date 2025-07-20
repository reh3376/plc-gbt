#!/usr/bin/env python3
"""
AI Enhancement Framework - Installation Verification Script

Comprehensive verification of AI Enhancement Framework installation and configuration.
This script validates all components, dependencies, and integration points.
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import importlib
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VerificationResult:
    """Result of a verification check."""
    component: str
    status: str  # "passed", "failed", "warning", "skipped"
    message: str
    details: Optional[Dict[str, Any]] = None

class InstallationVerifier:
    """
    Comprehensive installation verifier for AI Enhancement Framework.
    
    Checks:
    - Core framework components
    - Optional dependencies
    - Configuration files
    - Integration points
    - Performance benchmarks
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize the verifier."""
        self.verbose = verbose
        self.results: List[VerificationResult] = []
        self.base_path = Path.cwd()
        
    async def run_verification(self) -> Dict[str, Any]:
        """Run complete installation verification."""
        print("🔍 AI Enhancement Framework - Installation Verification")
        print("=" * 60)
        
        # Core component verification
        await self._verify_core_components()
        
        # Dependency verification
        await self._verify_dependencies()
        
        # Configuration verification
        await self._verify_configuration()
        
        # Integration verification
        await self._verify_integrations()
        
        # Performance verification
        await self._verify_performance()
        
        # Generate summary
        return await self._generate_summary()
    
    async def _verify_core_components(self) -> None:
        """Verify core framework components."""
        print("\n📦 Core Components:")
        
        core_components = [
            ("ai_enhancement_framework", "Main framework package"),
            ("ai_enhancement_framework.core", "Core module"),
            ("ai_enhancement_framework.core.task_orchestrator", "Task Orchestrator"),
            ("ai_enhancement_framework.core.memory_manager", "Memory Manager"),
            ("ai_enhancement_framework.core.code_analyzer", "Code Analyzer"),
            ("ai_enhancement_framework.cursor", "Cursor Integration"),
            ("ai_enhancement_framework.cursor.context_manager", "Context Manager"),
            ("ai_enhancement_framework.cursor.memory_persistence", "Memory Persistence"),
        ]
        
        for module_name, description in core_components:
            try:
                module = importlib.import_module(module_name)
                
                # Check for key classes/functions
                if hasattr(module, '__version__'):
                    version = module.__version__
                    message = f"✅ {description} (v{version})"
                    status = "passed"
                elif hasattr(module, '__all__'):
                    exports = len(module.__all__)
                    message = f"✅ {description} ({exports} exports)"
                    status = "passed"
                else:
                    message = f"✅ {description}"
                    status = "passed"
                
                self.results.append(VerificationResult(
                    component=module_name,
                    status=status,
                    message=message
                ))
                print(f"  {message}")
                
            except ImportError as e:
                message = f"❌ {description} - Import failed: {e}"
                self.results.append(VerificationResult(
                    component=module_name,
                    status="failed",
                    message=message,
                    details={"error": str(e)}
                ))
                print(f"  {message}")
            except Exception as e:
                message = f"⚠️  {description} - Error: {e}"
                self.results.append(VerificationResult(
                    component=module_name,
                    status="warning",
                    message=message,
                    details={"error": str(e)}
                ))
                print(f"  {message}")
    
    async def _verify_dependencies(self) -> None:
        """Verify optional dependencies."""
        print("\n🔧 Dependencies:")
        
        # Required dependencies
        required_deps = [
            ("pydantic", "Data validation"),
            ("typing_extensions", "Type annotations")
        ]
        
        # Optional dependencies
        optional_deps = [
            ("redis", "Redis cache support"),
            ("neo4j", "Neo4j graph database support"),
            ("psycopg2", "PostgreSQL support"),
            ("qdrant_client", "Qdrant vector database support"),
            ("aiohttp", "Async HTTP support"),
            ("asyncpg", "Async PostgreSQL support"),
            ("click", "CLI support"),
            ("structlog", "Structured logging")
        ]
        
        # Check required dependencies
        for dep_name, description in required_deps:
            try:
                importlib.import_module(dep_name)
                message = f"✅ {description}"
                self.results.append(VerificationResult(
                    component=f"dependency_{dep_name}",
                    status="passed",
                    message=message
                ))
                print(f"  {message}")
            except ImportError:
                message = f"❌ {description} - REQUIRED"
                self.results.append(VerificationResult(
                    component=f"dependency_{dep_name}",
                    status="failed",
                    message=message
                ))
                print(f"  {message}")
        
        # Check optional dependencies
        for dep_name, description in optional_deps:
            try:
                importlib.import_module(dep_name)
                message = f"✅ {description}"
                self.results.append(VerificationResult(
                    component=f"optional_{dep_name}",
                    status="passed",
                    message=message
                ))
                print(f"  {message}")
            except ImportError:
                message = f"⚠️  {description} - Optional (not installed)"
                self.results.append(VerificationResult(
                    component=f"optional_{dep_name}",
                    status="warning",
                    message=message
                ))
                if self.verbose:
                    print(f"  {message}")
    
    async def _verify_configuration(self) -> None:
        """Verify configuration files and setup."""
        print("\n⚙️  Configuration:")
        
        config_checks = [
            (".cursorrules", "Cursor IDE configuration"),
            (".ai_framework_config.json", "Framework configuration"),
            ("pyproject.toml", "Python project configuration"),
            (".gitignore", "Git ignore file"),
        ]
        
        for file_name, description in config_checks:
            file_path = self.base_path / file_name
            
            if file_path.exists():
                try:
                    # Validate file content based on type
                    if file_name.endswith('.json'):
                        with open(file_path, 'r') as f:
                            json.load(f)  # Validate JSON
                    
                    size = file_path.stat().st_size
                    message = f"✅ {description} ({size} bytes)"
                    self.results.append(VerificationResult(
                        component=f"config_{file_name}",
                        status="passed",
                        message=message,
                        details={"path": str(file_path), "size": size}
                    ))
                    print(f"  {message}")
                    
                except Exception as e:
                    message = f"⚠️  {description} - Invalid format: {e}"
                    self.results.append(VerificationResult(
                        component=f"config_{file_name}",
                        status="warning",
                        message=message,
                        details={"error": str(e)}
                    ))
                    print(f"  {message}")
            else:
                message = f"⚠️  {description} - Not found"
                self.results.append(VerificationResult(
                    component=f"config_{file_name}",
                    status="warning",
                    message=message
                ))
                if self.verbose:
                    print(f"  {message}")
    
    async def _verify_integrations(self) -> None:
        """Verify integration points."""
        print("\n🔗 Integrations:")
        
        # Test CLI integration
        try:
            result = subprocess.run([
                sys.executable, "-m", "ai_enhancement_framework.cli", "--version"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                message = f"✅ CLI Integration - {version}"
                self.results.append(VerificationResult(
                    component="cli_integration",
                    status="passed",
                    message=message,
                    details={"output": version}
                ))
            else:
                message = f"❌ CLI Integration - Exit code {result.returncode}"
                self.results.append(VerificationResult(
                    component="cli_integration",
                    status="failed",
                    message=message,
                    details={"stderr": result.stderr}
                ))
            print(f"  {message}")
            
        except Exception as e:
            message = f"❌ CLI Integration - Error: {e}"
            self.results.append(VerificationResult(
                component="cli_integration",
                status="failed",
                message=message,
                details={"error": str(e)}
            ))
            print(f"  {message}")
        
        # Test framework imports
        try:
            from ai_enhancement_framework.core import AITaskOrchestrator
            orchestrator = AITaskOrchestrator()
            
            # Test basic functionality
            analysis = orchestrator.analyze_task("test task")
            
            message = f"✅ Framework Integration - Task orchestrator functional"
            self.results.append(VerificationResult(
                component="framework_integration",
                status="passed",
                message=message,
                details={"complexity": analysis.complexity}
            ))
            print(f"  {message}")
            
        except Exception as e:
            message = f"❌ Framework Integration - Error: {e}"
            self.results.append(VerificationResult(
                component="framework_integration",
                status="failed",
                message=message,
                details={"error": str(e)}
            ))
            print(f"  {message}")
    
    async def _verify_performance(self) -> None:
        """Verify performance characteristics."""
        print("\n⚡ Performance:")
        
        try:
            from ai_enhancement_framework.core import AITaskOrchestrator
            import time
            
            # Measure task analysis performance
            orchestrator = AITaskOrchestrator()
            
            start_time = time.time()
            for i in range(10):
                orchestrator.analyze_task(f"Test task {i}")
            end_time = time.time()
            
            avg_time = (end_time - start_time) / 10 * 1000  # milliseconds
            
            if avg_time < 100:
                status = "passed"
                emoji = "✅"
            elif avg_time < 500:
                status = "warning"
                emoji = "⚠️"
            else:
                status = "failed"
                emoji = "❌"
            
            message = f"{emoji} Task Analysis Performance - {avg_time:.1f}ms average"
            self.results.append(VerificationResult(
                component="performance_task_analysis",
                status=status,
                message=message,
                details={"average_time_ms": avg_time}
            ))
            print(f"  {message}")
            
        except Exception as e:
            message = f"❌ Performance Test - Error: {e}"
            self.results.append(VerificationResult(
                component="performance_test",
                status="failed",
                message=message,
                details={"error": str(e)}
            ))
            print(f"  {message}")
    
    async def _generate_summary(self) -> Dict[str, Any]:
        """Generate verification summary."""
        print("\n" + "=" * 60)
        print("📊 Verification Summary:")
        
        # Count results by status
        status_counts = {
            "passed": 0,
            "failed": 0,
            "warning": 0,
            "skipped": 0
        }
        
        for result in self.results:
            status_counts[result.status] += 1
        
        total = len(self.results)
        passed = status_counts["passed"]
        failed = status_counts["failed"]
        warnings = status_counts["warning"]
        
        # Calculate score
        score = (passed / total * 100) if total > 0 else 0
        
        print(f"  Total Checks: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⚠️  Warnings: {warnings}")
        print(f"  📊 Success Rate: {score:.1f}%")
        
        # Overall status
        if failed == 0 and warnings <= total * 0.2:  # Allow up to 20% warnings
            overall_status = "✅ INSTALLATION VERIFIED"
            recommendations = ["Framework is ready for use!"]
        elif failed == 0:
            overall_status = "⚠️  INSTALLATION MOSTLY COMPLETE"
            recommendations = [
                "Framework is functional but has some optional components missing",
                "Consider installing additional dependencies for full functionality"
            ]
        else:
            overall_status = "❌ INSTALLATION INCOMPLETE"
            recommendations = [
                "Critical components are missing or broken",
                "Please reinstall the framework: pip install -e .[full]",
                "Check error messages above for specific issues"
            ]
        
        print(f"\n{overall_status}")
        
        if recommendations:
            print("\n💡 Recommendations:")
            for rec in recommendations:
                print(f"  • {rec}")
        
        # Detailed results for verbose mode
        if self.verbose and failed > 0:
            print("\n🔍 Failed Checks:")
            for result in self.results:
                if result.status == "failed":
                    print(f"  • {result.component}: {result.message}")
                    if result.details:
                        print(f"    Details: {result.details}")
        
        summary = {
            "overall_status": overall_status,
            "success_rate": score,
            "total_checks": total,
            "counts": status_counts,
            "recommendations": recommendations,
            "results": [
                {
                    "component": r.component,
                    "status": r.status,
                    "message": r.message,
                    "details": r.details
                }
                for r in self.results
            ]
        }
        
        return summary

async def main():
    """Main verification function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Verify AI Enhancement Framework installation"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run verification
    verifier = InstallationVerifier(verbose=args.verbose)
    summary = await verifier.run_verification()
    
    # Save results if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"\n💾 Results saved to: {args.output}")
    
    # Exit with appropriate code
    if summary["counts"]["failed"] > 0:
        sys.exit(1)
    elif summary["counts"]["warning"] > summary["total_checks"] * 0.5:
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    asyncio.run(main()) 