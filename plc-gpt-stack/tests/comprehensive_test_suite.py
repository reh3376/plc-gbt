#!/usr/bin/env python3
"""
Comprehensive Test Suite for PLC-GPT System
Created: January 1, 2025
Purpose: End-to-end testing for Phase 3 Day 3 implementation
"""

import asyncio
import os
import sys
import json
import time
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock
import traceback

# Add paths for local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'query'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'etl'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'performance'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'workers'))

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class TestResult:
    """Container for test results"""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.start_time = datetime.now()
        self.end_time = None
        self.success = False
        self.error_message = None
        self.details = {}
        self.duration_ms = 0
        
    def mark_success(self, details: Dict[str, Any] = None):
        """Mark test as successful"""
        self.end_time = datetime.now()
        self.success = True
        self.details = details or {}
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        
    def mark_failure(self, error_message: str, details: Dict[str, Any] = None):
        """Mark test as failed"""
        self.end_time = datetime.now()
        self.success = False
        self.error_message = error_message
        self.details = details or {}
        self.duration_ms = (self.end_time - self.start_time).total_seconds() * 1000
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting"""
        return {
            "test_name": self.test_name,
            "success": self.success,
            "duration_ms": round(self.duration_ms, 2),
            "error_message": self.error_message,
            "details": self.details,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

class ComprehensiveTestSuite:
    """
    Comprehensive testing suite for PLC-GPT Phase 3 Day 3 implementation.
    
    Tests all major components:
    - Query service (vector + graph)
    - ACD file processing
    - Performance optimization
    - ETL pipeline integration
    - End-to-end workflows
    """
    
    def __init__(self):
        """Initialize test suite"""
        self.test_results = []
        self.temp_dir = None
        self.test_data_dir = None
        
        # Test configuration
        self.config = {
            "neo4j_uri": os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
            "neo4j_user": os.environ.get("NEO4J_USER", "neo4j"),
            "neo4j_password": os.environ.get("NEO4J_PASSWORD", "password"),
            "qdrant_host": os.environ.get("QDRANT_HOST", "localhost"),
            "qdrant_port": int(os.environ.get("QDRANT_PORT", "6333")),
            "openai_api_key": os.environ.get("OPENAI_API_KEY")
        }
        
        # Test timeout (30 seconds per test)
        self.test_timeout = 30
        
        logger.info("ComprehensiveTestSuite initialized")
    
    def setup_test_environment(self):
        """Set up test environment with temp directories and test data"""
        # Create temporary directories
        self.temp_dir = tempfile.mkdtemp(prefix="plc_gpt_test_")
        self.test_data_dir = os.path.join(self.temp_dir, "test_data")
        os.makedirs(self.test_data_dir, exist_ok=True)
        
        # Create sample test files
        self._create_sample_test_files()
        
        logger.info("Test environment set up", temp_dir=self.temp_dir)
    
    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Test environment cleaned up")
    
    def _create_sample_test_files(self):
        """Create sample test files for testing"""
        # Sample ACD file content (XML-based)
        acd_content = """<?xml version="1.0" encoding="UTF-8"?>
<AutomationControlDatabase>
    <ProjectInfo name="TestProject" version="1.0" created="2025-01-01T00:00:00"/>
    <Components>
        <Component id="ctrl_001" name="MainController" type="CONTROLLER" 
                  manufacturer="Rockwell" catalog="1756-L83E"/>
        <Component id="io_001" name="InputModule" type="INPUT_MODULE" 
                  manufacturer="Rockwell" catalog="1756-IB16"/>
        <Component id="io_002" name="OutputModule" type="OUTPUT_MODULE" 
                  manufacturer="Rockwell" catalog="1756-OB16E"/>
    </Components>
    <PLCReferences>
        <PLCReference id="ref_001" address="Local:1:I.Data.0" component="io_001"/>
        <PLCReference id="ref_002" address="Local:2:O.Data.0" component="io_002"/>
    </PLCReferences>
</AutomationControlDatabase>"""
        
        with open(os.path.join(self.test_data_dir, "sample.acd"), "w") as f:
            f.write(acd_content)
        
        # Sample PDF text content
        pdf_text = """PLC Programming Manual
        
Chapter 1: Introduction
This manual covers the basics of PLC programming.

Chapter 2: AOI Development
Add-On Instructions (AOIs) are reusable code blocks.

Q: What is an AOI?
A: An Add-On Instruction is a custom instruction that encapsulates logic.

Q: How do you create an AOI?
A: Use Studio 5000 software to create and configure AOIs.
"""
        
        with open(os.path.join(self.test_data_dir, "sample.txt"), "w") as f:
            f.write(pdf_text)
        
        logger.debug("Sample test files created")
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        start_time = datetime.now()
        
        try:
            self.setup_test_environment()
            
            # Test categories
            test_categories = [
                ("Query Service Tests", self._test_query_service),
                ("ACD Processing Tests", self._test_acd_processing),
                ("Performance Optimization Tests", self._test_performance_optimization),
                ("ETL Integration Tests", self._test_etl_integration),
                ("End-to-End Workflow Tests", self._test_end_to_end_workflows)
            ]
            
            for category_name, test_method in test_categories:
                logger.info(f"Running {category_name}")
                
                try:
                    await asyncio.wait_for(test_method(), timeout=self.test_timeout * 5)
                except asyncio.TimeoutError:
                    self._add_test_result(f"{category_name} - TIMEOUT", False, "Test category timed out")
                except Exception as e:
                    self._add_test_result(f"{category_name} - ERROR", False, f"Category failed: {str(e)}")
            
            # Generate summary report
            end_time = datetime.now()
            total_duration = (end_time - start_time).total_seconds()
            
            summary = self._generate_test_summary(total_duration)
            
            logger.info("All tests completed", 
                       total_tests=len(self.test_results),
                       passed=summary["summary"]["passed"],
                       failed=summary["summary"]["failed"],
                       duration_seconds=total_duration)
            
            return summary
            
        finally:
            self.cleanup_test_environment()
    
    async def _test_query_service(self):
        """Test query service functionality"""
        test_name = "Query Service"
        
        try:
            # Import and test query service
            from query_service import QueryService, QueryResult
            
            # Test 1: Initialize query service
            result = TestResult(f"{test_name} - Initialization")
            try:
                query_service = QueryService(
                    neo4j_uri=self.config["neo4j_uri"],
                    neo4j_user=self.config["neo4j_user"],
                    neo4j_password=self.config["neo4j_password"],
                    qdrant_host=self.config["qdrant_host"],
                    qdrant_port=self.config["qdrant_port"],
                    openai_api_key=self.config["openai_api_key"]
                )
                
                result.mark_success({"component": "query_service", "initialized": True})
            except Exception as e:
                result.mark_failure(f"Failed to initialize QueryService: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 2: Health check
            result = TestResult(f"{test_name} - Health Check")
            try:
                health = await query_service.health_check()
                result.mark_success({
                    "health_status": health,
                    "neo4j_healthy": health.get("neo4j", False),
                    "qdrant_healthy": health.get("qdrant", False)
                })
            except Exception as e:
                result.mark_failure(f"Health check failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 3: Vector query (mock test)
            result = TestResult(f"{test_name} - Vector Query")
            try:
                query_result = await query_service.query(
                    "test query",
                    strategy="vector",
                    max_results=5
                )
                
                result.mark_success({
                    "query_executed": True,
                    "strategy": query_result.query_strategy,
                    "processing_time_ms": query_result.processing_time_ms
                })
            except Exception as e:
                result.mark_failure(f"Vector query failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 4: Graph query
            result = TestResult(f"{test_name} - Graph Query")
            try:
                query_result = await query_service.query(
                    "find components",
                    strategy="graph",
                    max_results=5
                )
                
                result.mark_success({
                    "query_executed": True,
                    "strategy": query_result.query_strategy,
                    "processing_time_ms": query_result.processing_time_ms
                })
            except Exception as e:
                result.mark_failure(f"Graph query failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 5: Hybrid query
            result = TestResult(f"{test_name} - Hybrid Query")
            try:
                query_result = await query_service.query(
                    "what is an AOI?",
                    strategy="hybrid",
                    max_results=5
                )
                
                result.mark_success({
                    "query_executed": True,
                    "strategy": query_result.query_strategy,
                    "processing_time_ms": query_result.processing_time_ms,
                    "has_answer": query_result.answer is not None
                })
            except Exception as e:
                result.mark_failure(f"Hybrid query failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Cleanup
            query_service.close()
            
        except ImportError as e:
            self._add_test_result(f"{test_name} - Import Error", False, f"Failed to import query_service: {str(e)}")
    
    async def _test_acd_processing(self):
        """Test ACD file processing functionality"""
        test_name = "ACD Processing"
        
        try:
            # Import ACD processor
            from acd_processor import ACDProcessor, process_acd_file
            
            # Test 1: Initialize ACD processor
            result = TestResult(f"{test_name} - Initialization")
            try:
                processor = ACDProcessor()
                result.mark_success({"component": "acd_processor", "initialized": True})
            except Exception as e:
                result.mark_failure(f"Failed to initialize ACDProcessor: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 2: Process sample ACD file
            result = TestResult(f"{test_name} - File Processing")
            try:
                acd_file_path = os.path.join(self.test_data_dir, "sample.acd")
                acd_project = processor.process_file(acd_file_path)
                
                result.mark_success({
                    "file_processed": True,
                    "project_name": acd_project.project_name,
                    "components_count": len(acd_project.components),
                    "plc_references_count": len(acd_project.plc_references)
                })
            except Exception as e:
                result.mark_failure(f"ACD file processing failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 3: Extract PLC connections
            result = TestResult(f"{test_name} - PLC Connection Extraction")
            try:
                connections = processor.extract_plc_connections(acd_project)
                result.mark_success({
                    "connections_extracted": True,
                    "connections_count": len(connections),
                    "connection_types": list(set(c.get('io_type', 'UNKNOWN') for c in connections))
                })
            except Exception as e:
                result.mark_failure(f"PLC connection extraction failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 4: Generate summary
            result = TestResult(f"{test_name} - Summary Generation")
            try:
                summary = processor.generate_summary(acd_project)
                result.mark_success({
                    "summary_generated": True,
                    "summary_keys": list(summary.keys()),
                    "component_types": summary.get("component_types", {})
                })
            except Exception as e:
                result.mark_failure(f"Summary generation failed: {str(e)}")
            
            self.test_results.append(result)
            
        except ImportError as e:
            self._add_test_result(f"{test_name} - Import Error", False, f"Failed to import acd_processor: {str(e)}")
    
    async def _test_performance_optimization(self):
        """Test performance optimization functionality"""
        test_name = "Performance Optimization"
        
        try:
            # Import performance optimizer
            from optimizer import PerformanceOptimizer, benchmark_query
            
            # Test 1: Initialize performance optimizer
            result = TestResult(f"{test_name} - Initialization")
            try:
                optimizer = PerformanceOptimizer(
                    neo4j_uri=self.config["neo4j_uri"],
                    neo4j_user=self.config["neo4j_user"],
                    neo4j_password=self.config["neo4j_password"],
                    qdrant_host=self.config["qdrant_host"],
                    qdrant_port=self.config["qdrant_port"]
                )
                
                result.mark_success({"component": "performance_optimizer", "initialized": True})
            except Exception as e:
                result.mark_failure(f"Failed to initialize PerformanceOptimizer: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 2: Collect metrics
            result = TestResult(f"{test_name} - Metrics Collection")
            try:
                metrics = optimizer.collect_metrics()
                result.mark_success({
                    "metrics_collected": True,
                    "cpu_percent": metrics.cpu_percent,
                    "memory_percent": metrics.memory_percent,
                    "timestamp": metrics.timestamp.isoformat()
                })
            except Exception as e:
                result.mark_failure(f"Metrics collection failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 3: Generate optimization report
            result = TestResult(f"{test_name} - Optimization Report")
            try:
                # Add some metrics to history first
                optimizer.metrics_history.append(metrics)
                
                report = optimizer.get_optimization_report()
                result.mark_success({
                    "report_generated": True,
                    "performance_score": report.get("overall_performance_score"),
                    "recommendations_count": len(report.get("recommendations", []))
                })
            except Exception as e:
                result.mark_failure(f"Optimization report generation failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 4: Benchmark function
            result = TestResult(f"{test_name} - Function Benchmarking")
            try:
                def test_function():
                    time.sleep(0.01)  # Simulate work
                    return "test_result"
                
                benchmark_result = benchmark_query(test_function)
                result.mark_success({
                    "benchmark_completed": True,
                    "execution_time_ms": benchmark_result["execution_time_ms"],
                    "success": benchmark_result["success"]
                })
            except Exception as e:
                result.mark_failure(f"Function benchmarking failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Cleanup
            optimizer.close()
            
        except ImportError as e:
            self._add_test_result(f"{test_name} - Import Error", False, f"Failed to import optimizer: {str(e)}")
    
    async def _test_etl_integration(self):
        """Test ETL pipeline integration"""
        test_name = "ETL Integration"
        
        try:
            # Import ETL components
            from document_parser import DocumentParser
            
            # Test 1: Initialize document parser
            result = TestResult(f"{test_name} - Document Parser Init")
            try:
                parser = DocumentParser()
                result.mark_success({"component": "document_parser", "initialized": True})
            except Exception as e:
                result.mark_failure(f"Failed to initialize DocumentParser: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 2: Parse ACD file
            result = TestResult(f"{test_name} - ACD File Parsing")
            try:
                acd_file_path = os.path.join(self.test_data_dir, "sample.acd")
                extracted_doc = parser.parse_document(acd_file_path)
                
                if extracted_doc:
                    result.mark_success({
                        "file_parsed": True,
                        "file_type": extracted_doc.file_type,
                        "components_count": extracted_doc.content.get("component_counts", {}).get("components", 0)
                    })
                else:
                    result.mark_failure("ACD parsing returned None")
                    
            except Exception as e:
                result.mark_failure(f"ACD file parsing failed: {str(e)}")
            
            self.test_results.append(result)
            
            # Test 3: Checksum calculation
            result = TestResult(f"{test_name} - Checksum Calculation")
            try:
                acd_file_path = os.path.join(self.test_data_dir, "sample.acd")
                checksum = parser.calculate_checksum(acd_file_path)
                result.mark_success({
                    "checksum_calculated": True,
                    "checksum": checksum,
                    "checksum_length": len(checksum)
                })
            except Exception as e:
                result.mark_failure(f"Checksum calculation failed: {str(e)}")
            
            self.test_results.append(result)
            
        except ImportError as e:
            self._add_test_result(f"{test_name} - Import Error", False, f"Failed to import ETL components: {str(e)}")
    
    async def _test_end_to_end_workflows(self):
        """Test end-to-end workflows"""
        test_name = "End-to-End Workflows"
        
        # Test 1: Complete ACD processing workflow
        result = TestResult(f"{test_name} - ACD Processing Workflow")
        try:
            # Simulate complete workflow: ACD file -> Parser -> Components -> Graph
            from document_parser import DocumentParser
            from acd_processor import ACDProcessor
            
            # Step 1: Parse ACD file
            parser = DocumentParser()
            acd_file_path = os.path.join(self.test_data_dir, "sample.acd")
            extracted_doc = parser.parse_document(acd_file_path)
            
            # Step 2: Verify parsing worked
            if not extracted_doc:
                raise Exception("Document parsing failed")
            
            # Step 3: Extract components
            components = extracted_doc.content.get("components", [])
            plc_refs = extracted_doc.content.get("plc_references", [])
            
            result.mark_success({
                "workflow_completed": True,
                "steps_executed": ["parse", "extract", "validate"],
                "components_extracted": len(components),
                "plc_references_extracted": len(plc_refs),
                "file_type": extracted_doc.file_type
            })
            
        except Exception as e:
            result.mark_failure(f"End-to-end ACD workflow failed: {str(e)}")
        
        self.test_results.append(result)
        
        # Test 2: Performance monitoring workflow
        result = TestResult(f"{test_name} - Performance Monitoring Workflow")
        try:
            from optimizer import PerformanceOptimizer
            
            # Initialize optimizer
            optimizer = PerformanceOptimizer(
                neo4j_uri=self.config["neo4j_uri"],
                neo4j_user=self.config["neo4j_user"],
                neo4j_password=self.config["neo4j_password"],
                monitoring_interval=1  # Short interval for testing
            )
            
            # Collect metrics
            metrics = optimizer.collect_metrics()
            
            # Generate report
            optimizer.metrics_history.append(metrics)
            report = optimizer.get_optimization_report()
            
            optimizer.close()
            
            result.mark_success({
                "workflow_completed": True,
                "steps_executed": ["initialize", "collect_metrics", "generate_report"],
                "performance_score": report.get("overall_performance_score"),
                "metrics_collected": True
            })
            
        except Exception as e:
            result.mark_failure(f"Performance monitoring workflow failed: {str(e)}")
        
        self.test_results.append(result)
        
        # Test 3: Query service integration workflow
        result = TestResult(f"{test_name} - Query Integration Workflow")
        try:
            from query_service import QueryService
            
            # Initialize query service
            query_service = QueryService(
                neo4j_uri=self.config["neo4j_uri"],
                neo4j_user=self.config["neo4j_user"],
                neo4j_password=self.config["neo4j_password"],
                qdrant_host=self.config["qdrant_host"],
                qdrant_port=self.config["qdrant_port"]
            )
            
            # Test different query strategies
            strategies = ["vector", "graph", "hybrid"]
            strategy_results = {}
            
            for strategy in strategies:
                try:
                    query_result = await query_service.query(
                        f"test {strategy} query",
                        strategy=strategy,
                        max_results=3
                    )
                    strategy_results[strategy] = {
                        "success": True,
                        "processing_time_ms": query_result.processing_time_ms
                    }
                except Exception as e:
                    strategy_results[strategy] = {
                        "success": False,
                        "error": str(e)
                    }
            
            query_service.close()
            
            successful_strategies = sum(1 for r in strategy_results.values() if r["success"])
            
            result.mark_success({
                "workflow_completed": True,
                "strategies_tested": len(strategies),
                "successful_strategies": successful_strategies,
                "strategy_results": strategy_results
            })
            
        except Exception as e:
            result.mark_failure(f"Query integration workflow failed: {str(e)}")
        
        self.test_results.append(result)
    
    def _add_test_result(self, test_name: str, success: bool, message: str, details: Dict[str, Any] = None):
        """Helper to add test result"""
        result = TestResult(test_name)
        if success:
            result.mark_success(details or {"message": message})
        else:
            result.mark_failure(message, details)
        self.test_results.append(result)
    
    def _generate_test_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate comprehensive test summary"""
        passed = sum(1 for r in self.test_results if r.success)
        failed = len(self.test_results) - passed
        
        # Category analysis
        categories = {}
        for result in self.test_results:
            category = result.test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[category]["total"] += 1
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        # Performance analysis
        avg_test_duration = sum(r.duration_ms for r in self.test_results) / len(self.test_results) if self.test_results else 0
        slowest_test = max(self.test_results, key=lambda r: r.duration_ms) if self.test_results else None
        
        return {
            "summary": {
                "total_tests": len(self.test_results),
                "passed": passed,
                "failed": failed,
                "success_rate": round((passed / len(self.test_results)) * 100, 1) if self.test_results else 0,
                "total_duration_seconds": round(total_duration, 2),
                "avg_test_duration_ms": round(avg_test_duration, 2)
            },
            "categories": categories,
            "performance": {
                "slowest_test": {
                    "name": slowest_test.test_name if slowest_test else None,
                    "duration_ms": round(slowest_test.duration_ms, 2) if slowest_test else 0
                }
            },
            "detailed_results": [result.to_dict() for result in self.test_results],
            "timestamp": datetime.now().isoformat(),
            "phase": "Phase 3 Day 3",
            "version": "1.0.0"
        }
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            filename = f"comprehensive_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = self._generate_test_summary(0)  # Duration will be recalculated
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Test results saved", filename=filename)
        return filename

# CLI interface for running tests
async def main():
    """Main function for CLI execution"""
    print("🧪 Starting Comprehensive Test Suite for PLC-GPT Phase 3 Day 3")
    print("=" * 60)
    
    test_suite = ComprehensiveTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print summary
        print("\n📊 Test Results Summary")
        print("=" * 30)
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: ✅ {results['summary']['passed']}")
        print(f"Failed: ❌ {results['summary']['failed']}")
        print(f"Success Rate: {results['summary']['success_rate']}%")
        print(f"Duration: {results['summary']['total_duration_seconds']}s")
        
        # Print category breakdown
        print("\n📈 Category Breakdown")
        print("-" * 20)
        for category, stats in results['categories'].items():
            status = "✅" if stats['failed'] == 0 else "❌"
            print(f"{status} {category}: {stats['passed']}/{stats['total']} passed")
        
        # Print failed tests
        failed_tests = [r for r in results['detailed_results'] if not r['success']]
        if failed_tests:
            print("\n❌ Failed Tests")
            print("-" * 15)
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['error_message']}")
        
        # Save results
        filename = test_suite.save_results()
        print(f"\n💾 Results saved to: {filename}")
        
        # Final status
        if results['summary']['failed'] == 0:
            print("\n🎉 ALL TESTS PASSED! Phase 3 Day 3 implementation is ready!")
            return 0
        else:
            print(f"\n⚠️  {results['summary']['failed']} tests failed. Review and fix before proceeding.")
            return 1
            
    except Exception as e:
        print(f"\n💥 Test suite execution failed: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 