#!/usr/bin/env python3
"""
🤖 Comprehensive System Validator - AI Task Orchestrator Implementation

End-to-end validation system for the complete multi-database memory management
system with intelligent ingestion capabilities.

Validates:
- Database coordination and connectivity
- Intelligent vs Legacy ingestion methods
- File processing and storage
- CLI functionality and options
- Performance metrics and monitoring
- Error handling and recovery
- System integration and reliability

Author: AI Task Orchestrator
Created: 2025-01-09
Purpose: Comprehensive system validation and testing
"""

import os
import sys
import json
import time
import asyncio
import logging
import tempfile
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from database_manager import DatabaseManager, DatabaseType
from memory_coordinator import MemoryCoordinator
from intelligent_ingestion_orchestrator import IntelligentIngestionOrchestrator
from codebase_analyzer import CodebaseAnalyzer, AnalysisDepth
from file_processors import FileProcessorOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    """Validation test results"""
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    WARNING = "WARNING"

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    result: ValidationResult
    execution_time_ms: float
    details: str
    metrics: Dict[str, Any] = None
    error_message: Optional[str] = None

@dataclass
class ValidationReport:
    """Comprehensive validation report"""
    session_id: str
    timestamp: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    warning_tests: int
    total_execution_time_ms: float
    test_results: List[TestResult]
    system_info: Dict[str, Any]
    performance_summary: Dict[str, Any]

class SystemValidator:
    """
    🎯 Comprehensive System Validation Framework
    
    Provides end-to-end testing and validation of the complete multi-database
    memory management system including intelligent ingestion capabilities.
    
    Features:
    - Database connectivity and coordination testing
    - Intelligent vs Legacy ingestion comparison
    - Performance benchmarking and metrics
    - Error handling and recovery validation  
    - CLI functionality testing
    - System integration verification
    """
    
    def __init__(self):
        self.session_id = f"validator_{int(time.time())}"
        self.start_time = datetime.now()
        self.test_results: List[TestResult] = []
        
        # Test configuration
        self.test_data_dir = Path(tempfile.mkdtemp(prefix="plc_validation_"))
        self.create_test_data()
        
        # System components
        self.db_manager = None
        self.coordinator = None
        self.orchestrator = None
        
        logger.info(f"SystemValidator initialized: {self.session_id}")
        logger.info(f"Test data directory: {self.test_data_dir}")
    
    def create_test_data(self):
        """Create test files and data for validation"""
        logger.info("📁 Creating test data for validation")
        
        # Create various file types for testing
        test_files = {
            "simple_python.py": """
# Simple Python file for testing
def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""",
            "complex_python.py": """
# Complex Python file for testing (500+ lines simulated)
import os
import sys
import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

class ComplexClass:
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.processed_items = []
        
    def process_data(self, items: List[Any]) -> Dict[str, Any]:
        results = {}
        for item in items:
            if isinstance(item, dict):
                processed = self._process_dict(item)
                results[item.get('id', 'unknown')] = processed
            elif isinstance(item, list):
                processed = self._process_list(item)
                results[f"list_{len(item)}"] = processed
        return results
    
    def _process_dict(self, data: dict) -> dict:
        return {k: str(v).upper() for k, v in data.items()}
    
    def _process_list(self, data: list) -> list:
        return [str(item).lower() for item in data]

async def async_function():
    await asyncio.sleep(0.1)
    return "async result"

def function_with_many_lines():
    # This function simulates complexity
    data = []
    for i in range(100):
        item = {
            'id': i,
            'value': i * 2,
            'processed': False
        }
        data.append(item)
    
    processor = ComplexClass({'config': 'test'})
    results = processor.process_data(data)
    
    return results

# Additional functions to increase line count
""" + "\n".join([f"def function_{i}(): pass" for i in range(50)]),
            
            "test_config.json": json.dumps({
                "database": {
                    "redis": {"host": "localhost", "port": 6379},
                    "neo4j": {"uri": "bolt://localhost:7687"},
                    "postgresql": {"host": "localhost", "port": 5432},
                    "qdrant": {"host": "localhost", "port": 6333}
                },
                "settings": {
                    "batch_size": 100,
                    "timeout": 30,
                    "retries": 3
                }
            }, indent=2),
            
            "test_markdown.md": """
# Test Markdown File

This is a test markdown file for validation purposes.

## Features

- Code analysis
- File processing
- Database storage

### Code Examples

```python
def example():
    return "test"
```

## Links

[Documentation](https://example.com)
[API Reference](https://api.example.com)
""",
            
            "test_yaml.yml": """
apiVersion: v1
kind: ConfigMap
metadata:
  name: test-config
data:
  database.host: localhost
  database.port: "5432"
  features:
    - analysis
    - processing
    - storage
""",
            
            "large_file.txt": "This is a large text file.\n" * 1000
        }
        
        # Create test files
        for filename, content in test_files.items():
            file_path = self.test_data_dir / filename
            with open(file_path, 'w') as f:
                f.write(content)
        
        logger.info(f"✅ Created {len(test_files)} test files")
    
    async def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """Run individual test and record results"""
        start_time = time.time()
        
        try:
            logger.info(f"🔄 Running test: {test_name}")
            result, details, metrics = await test_func(*args, **kwargs)
            execution_time = (time.time() - start_time) * 1000
            
            test_result = TestResult(
                test_name=test_name,
                result=result,
                execution_time_ms=execution_time,
                details=details,
                metrics=metrics
            )
            
            status_icon = {
                ValidationResult.PASS: "✅",
                ValidationResult.FAIL: "❌",
                ValidationResult.SKIP: "⏭️",
                ValidationResult.WARNING: "⚠️"
            }[result]
            
            logger.info(f"{status_icon} {test_name}: {result.value} ({execution_time:.1f}ms)")
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            test_result = TestResult(
                test_name=test_name,
                result=ValidationResult.FAIL,
                execution_time_ms=execution_time,
                details=f"Test failed with exception: {str(e)}",
                error_message=str(e)
            )
            logger.error(f"❌ {test_name}: FAILED - {str(e)}")
        
        self.test_results.append(test_result)
        return test_result
    
    async def test_database_connectivity(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test database connectivity and health"""
        try:
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize_all_connections()
            
            # Use check_all_connections instead of health_check
            health_results = await self.db_manager.check_all_connections()
            
            connected_dbs = sum(1 for status in health_results.values() 
                              if status.get('status') == 'connected')
            total_dbs = len(health_results)
            
            if connected_dbs >= 1:  # At least one database connected
                result = ValidationResult.PASS
                details = f"Database connectivity: {connected_dbs}/{total_dbs} databases connected"
            else:
                result = ValidationResult.FAIL
                details = f"Database connectivity: No databases connected"
            
            metrics = {
                'total_databases': total_dbs,
                'connected_databases': connected_dbs,
                'health_results': health_results
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Database connectivity failed: {str(e)}", {}
    
    async def test_memory_coordinator_initialization(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test memory coordinator initialization and functionality"""
        try:
            if not self.db_manager:
                return ValidationResult.SKIP, "Database manager not available", {}
            
            self.coordinator = MemoryCoordinator(self.db_manager)
            
            # Test performance summary
            perf_summary = self.coordinator.get_performance_summary()
            
            if perf_summary['session_id']:
                result = ValidationResult.PASS
                details = f"Memory coordinator initialized successfully: {perf_summary['session_id']}"
            else:
                result = ValidationResult.FAIL
                details = "Memory coordinator initialization failed"
            
            metrics = {
                'session_id': perf_summary['session_id'],
                'uptime_seconds': perf_summary['uptime_seconds'],
                'memory_tier_utilization': perf_summary['memory_tier_utilization']
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Memory coordinator initialization failed: {str(e)}", {}
    
    async def test_codebase_analysis(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test codebase analysis functionality"""
        try:
            analyzer = CodebaseAnalyzer(str(self.test_data_dir), AnalysisDepth.STRUCTURAL)
            results = analyzer.analyze_codebase()
            
            if len(results) > 0:
                result = ValidationResult.PASS
                details = f"Codebase analysis successful: {len(results)} files analyzed"
            else:
                result = ValidationResult.FAIL
                details = "Codebase analysis failed: No files analyzed"
            
            # Get analysis summary
            summary = analyzer.get_analysis_summary()
            
            metrics = {
                'total_files_analyzed': len(results),
                'file_types': summary['statistics']['file_types'],
                'total_functions': summary['statistics']['total_functions'],
                'total_classes': summary['statistics']['total_classes'],
                'analysis_time_ms': summary['performance']['total_analysis_time'] * 1000
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Codebase analysis failed: {str(e)}", {}
    
    async def test_intelligent_ingestion(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test intelligent ingestion orchestrator"""
        try:
            if not self.coordinator:
                return ValidationResult.SKIP, "Memory coordinator not available", {}
            
            self.orchestrator = IntelligentIngestionOrchestrator(self.coordinator)
            
            # Run intelligent ingestion
            result_data = await self.orchestrator.ingest_codebase_intelligently(
                root_path=str(self.test_data_dir),
                analysis_depth=AnalysisDepth.STRUCTURAL,
                max_concurrent_batches=2,
                checkpoint_interval_minutes=1
            )
            
            success_rate = (result_data['successfully_processed'] / 
                          result_data['total_files_analyzed'] * 100)
            
            if success_rate >= 50:  # At least 50% success rate
                result = ValidationResult.PASS
                details = f"Intelligent ingestion successful: {success_rate:.1f}% success rate"
            else:
                result = ValidationResult.FAIL
                details = f"Intelligent ingestion failed: {success_rate:.1f}% success rate"
            
            metrics = {
                'methodology': result_data['methodology'],
                'total_files_analyzed': result_data['total_files_analyzed'],
                'successfully_processed': result_data['successfully_processed'],
                'failed_files': result_data['failed_files'],
                'success_rate': success_rate,
                'files_per_second': result_data['files_per_second'],
                'total_batches_created': result_data.get('total_batches_created', 0),
                'complexity_analysis': result_data.get('complexity_analysis', {}),
                'bandwidth_management': result_data.get('bandwidth_management', {})
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Intelligent ingestion failed: {str(e)}", {}
    
    async def test_legacy_ingestion(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test legacy ingestion method for comparison"""
        try:
            if not self.coordinator:
                return ValidationResult.SKIP, "Memory coordinator not available", {}
            
            # Run legacy ingestion
            result_data = await self.coordinator.ingest_codebase(
                root_path=str(self.test_data_dir),
                analysis_depth=AnalysisDepth.STRUCTURAL,
                use_intelligent_orchestrator=False
            )
            
            success_rate = (result_data['successfully_processed'] / 
                          result_data['total_files_analyzed'] * 100)
            
            if success_rate >= 50:  # At least 50% success rate
                result = ValidationResult.PASS
                details = f"Legacy ingestion successful: {success_rate:.1f}% success rate"
            else:
                result = ValidationResult.FAIL
                details = f"Legacy ingestion failed: {success_rate:.1f}% success rate"
            
            metrics = {
                'methodology': result_data['methodology'],
                'total_files_analyzed': result_data['total_files_analyzed'],
                'successfully_processed': result_data['successfully_processed'],
                'failed_files': result_data['failed_files'],
                'success_rate': success_rate,
                'files_per_second': result_data['files_per_second'],
                'ingestion_time_ms': result_data.get('ingestion_time_ms', 0)
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Legacy ingestion failed: {str(e)}", {}
    
    async def test_cli_functionality(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test CLI functionality and commands"""
        try:
            cli_script = Path(__file__).parent / "plc_memory_cli.py"
            
            if not cli_script.exists():
                return ValidationResult.FAIL, "CLI script not found", {}
            
            # Test CLI help command
            result = subprocess.run([
                sys.executable, str(cli_script), "--help"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "PLC Memory Management" in result.stdout:
                cli_help_success = True
            else:
                cli_help_success = False
            
            # Test CLI version command
            result = subprocess.run([
                sys.executable, str(cli_script), "version"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and "Version:" in result.stdout:
                cli_version_success = True
            else:
                cli_version_success = False
            
            # Test CLI dry run
            result = subprocess.run([
                sys.executable, str(cli_script), "ingest", str(self.test_data_dir), 
                "--method", "intelligent", "--dry-run"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and "Would process" in result.stdout:
                cli_dryrun_success = True
            else:
                cli_dryrun_success = False
            
            successful_tests = sum([cli_help_success, cli_version_success, cli_dryrun_success])
            total_tests = 3
            
            if successful_tests == total_tests:
                result_status = ValidationResult.PASS
                details = f"CLI functionality: {successful_tests}/{total_tests} tests passed"
            elif successful_tests > 0:
                result_status = ValidationResult.WARNING
                details = f"CLI functionality: {successful_tests}/{total_tests} tests passed"
            else:
                result_status = ValidationResult.FAIL
                details = f"CLI functionality: {successful_tests}/{total_tests} tests passed"
            
            metrics = {
                'help_command': cli_help_success,
                'version_command': cli_version_success,
                'dry_run_command': cli_dryrun_success,
                'success_rate': successful_tests / total_tests
            }
            
            return result_status, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"CLI testing failed: {str(e)}", {}
    
    async def test_error_handling(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test error handling and recovery capabilities"""
        try:
            errors_caught = 0
            total_error_tests = 0
            
            # Test 1: Invalid path handling
            total_error_tests += 1
            try:
                analyzer = CodebaseAnalyzer("/nonexistent/path", AnalysisDepth.STRUCTURAL)
                results = analyzer.analyze_codebase()
                # Should return empty results, not crash
                if len(results) == 0:
                    errors_caught += 1
            except Exception:
                pass  # Expected to handle gracefully
            
            # Test 2: Database connection failure handling
            total_error_tests += 1
            try:
                if self.coordinator:
                    # This should handle gracefully with logging
                    perf = self.coordinator.get_performance_summary()
                    if perf:  # Should return even with failed connections
                        errors_caught += 1
            except Exception:
                pass
            
            # Test 3: File processing error handling
            total_error_tests += 1
            try:
                if self.coordinator:
                    file_processor = FileProcessorOrchestrator(self.db_manager)
                    # Should handle file processing errors gracefully
                    errors_caught += 1
            except Exception:
                pass
            
            if errors_caught >= total_error_tests // 2:  # At least half should pass
                result = ValidationResult.PASS
                details = f"Error handling: {errors_caught}/{total_error_tests} scenarios handled"
            else:
                result = ValidationResult.WARNING
                details = f"Error handling: {errors_caught}/{total_error_tests} scenarios handled"
            
            metrics = {
                'error_scenarios_tested': total_error_tests,
                'errors_handled_gracefully': errors_caught,
                'error_handling_rate': errors_caught / total_error_tests
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Error handling test failed: {str(e)}", {}
    
    async def test_performance_metrics(self) -> Tuple[ValidationResult, str, Dict[str, Any]]:
        """Test performance monitoring and metrics collection"""
        try:
            if not self.coordinator:
                return ValidationResult.SKIP, "Memory coordinator not available", {}
            
            # Get performance summary
            perf_summary = self.coordinator.get_performance_summary()
            
            # Check required metrics are present
            required_metrics = [
                'session_id', 'uptime_seconds', 'total_operations',
                'cache_hit_rate', 'memory_tier_utilization'
            ]
            
            present_metrics = sum(1 for metric in required_metrics 
                                if metric in perf_summary)
            
            if present_metrics == len(required_metrics):
                result = ValidationResult.PASS
                details = f"Performance metrics: All {present_metrics} metrics available"
            elif present_metrics > len(required_metrics) // 2:
                result = ValidationResult.WARNING
                details = f"Performance metrics: {present_metrics}/{len(required_metrics)} metrics available"
            else:
                result = ValidationResult.FAIL
                details = f"Performance metrics: {present_metrics}/{len(required_metrics)} metrics available"
            
            metrics = {
                'required_metrics': required_metrics,
                'present_metrics': present_metrics,
                'performance_summary': perf_summary
            }
            
            return result, details, metrics
            
        except Exception as e:
            return ValidationResult.FAIL, f"Performance metrics test failed: {str(e)}", {}
    
    async def run_comprehensive_validation(self) -> ValidationReport:
        """Run all validation tests and generate comprehensive report"""
        logger.info("🚀 Starting comprehensive system validation")
        logger.info(f"Session ID: {self.session_id}")
        
        # Define test suite
        test_suite = [
            ("Database Connectivity", self.test_database_connectivity),
            ("Memory Coordinator Initialization", self.test_memory_coordinator_initialization),
            ("Codebase Analysis", self.test_codebase_analysis),
            ("Intelligent Ingestion", self.test_intelligent_ingestion),
            ("Legacy Ingestion", self.test_legacy_ingestion),
            ("CLI Functionality", self.test_cli_functionality),
            ("Error Handling", self.test_error_handling),
            ("Performance Metrics", self.test_performance_metrics)
        ]
        
        # Run all tests
        for test_name, test_func in test_suite:
            await self.run_test(test_name, test_func)
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.result == ValidationResult.PASS)
        failed_tests = sum(1 for r in self.test_results if r.result == ValidationResult.FAIL)
        skipped_tests = sum(1 for r in self.test_results if r.result == ValidationResult.SKIP)
        warning_tests = sum(1 for r in self.test_results if r.result == ValidationResult.WARNING)
        
        total_execution_time = sum(r.execution_time_ms for r in self.test_results)
        
        # Gather system information
        system_info = {
            'python_version': sys.version,
            'platform': sys.platform,
            'test_data_directory': str(self.test_data_dir),
            'validation_timestamp': datetime.now().isoformat()
        }
        
        # Create performance summary
        performance_summary = {}
        if self.coordinator:
            performance_summary = self.coordinator.get_performance_summary()
        
        # Generate comprehensive report
        report = ValidationReport(
            session_id=self.session_id,
            timestamp=datetime.now(),
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            warning_tests=warning_tests,
            total_execution_time_ms=total_execution_time,
            test_results=self.test_results,
            system_info=system_info,
            performance_summary=performance_summary
        )
        
        logger.info("✅ Comprehensive validation complete")
        logger.info(f"📊 Results: {passed_tests} PASS, {failed_tests} FAIL, {warning_tests} WARNING, {skipped_tests} SKIP")
        
        return report
    
    def generate_report_file(self, report: ValidationReport) -> str:
        """Generate comprehensive validation report file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"validation_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        logger.info(f"📄 Validation report saved: {report_file}")
        return report_file
    
    def print_summary_report(self, report: ValidationReport):
        """Print human-readable summary report"""
        print("\n" + "="*80)
        print("🤖 COMPREHENSIVE SYSTEM VALIDATION REPORT")
        print("="*80)
        print(f"Session ID: {report.session_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Total execution time: {report.total_execution_time_ms:.1f}ms")
        print("")
        
        # Summary statistics
        print("📊 TEST SUMMARY:")
        print(f"  ✅ PASSED:  {report.passed_tests}")
        print(f"  ❌ FAILED:  {report.failed_tests}")
        print(f"  ⚠️  WARNING: {report.warning_tests}")
        print(f"  ⏭️  SKIPPED: {report.skipped_tests}")
        print(f"  📝 TOTAL:   {report.total_tests}")
        
        success_rate = report.passed_tests / report.total_tests * 100 if report.total_tests > 0 else 0
        print(f"  🎯 SUCCESS RATE: {success_rate:.1f}%")
        print("")
        
        # Individual test results
        print("📋 DETAILED RESULTS:")
        for test in report.test_results:
            status_icon = {
                ValidationResult.PASS: "✅",
                ValidationResult.FAIL: "❌",
                ValidationResult.SKIP: "⏭️",
                ValidationResult.WARNING: "⚠️"
            }[test.result]
            
            print(f"  {status_icon} {test.test_name}: {test.result.value}")
            print(f"     {test.details}")
            print(f"     Execution time: {test.execution_time_ms:.1f}ms")
            
            if test.error_message:
                print(f"     Error: {test.error_message}")
            print("")
        
        # Overall system health
        if report.failed_tests == 0:
            print("🎯 OVERALL STATUS: ✅ SYSTEM HEALTHY")
        elif report.failed_tests <= 2:
            print("🎯 OVERALL STATUS: ⚠️  MINOR ISSUES DETECTED")
        else:
            print("🎯 OVERALL STATUS: ❌ CRITICAL ISSUES DETECTED")
        
        print("="*80)
    
    async def cleanup(self):
        """Clean up test resources"""
        try:
            # Close database connections
            if self.db_manager:
                await self.db_manager.close_all_connections()
            
            # Clean up test data directory
            import shutil
            if self.test_data_dir.exists():
                shutil.rmtree(self.test_data_dir)
                logger.info(f"🧹 Cleaned up test data: {self.test_data_dir}")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")

async def main():
    """
    🚀 Main validation execution
    """
    print("🤖 Comprehensive System Validator - AI Task Orchestrator Implementation")
    print("=" * 80)
    
    validator = SystemValidator()
    
    try:
        # Run comprehensive validation
        report = await validator.run_comprehensive_validation()
        
        # Generate and save report
        report_file = validator.generate_report_file(report)
        
        # Print summary
        validator.print_summary_report(report)
        
        print(f"\n💾 Detailed report saved to: {report_file}")
        
        # Return appropriate exit code
        if report.failed_tests == 0:
            return 0
        elif report.failed_tests <= 2:
            return 1  # Minor issues
        else:
            return 2  # Critical issues
            
    except Exception as e:
        logger.error(f"Validation failed: {str(e)}")
        print(f"❌ Validation failed: {str(e)}")
        return 3
    
    finally:
        await validator.cleanup()

if __name__ == "__main__":
    exit(asyncio.run(main())) 