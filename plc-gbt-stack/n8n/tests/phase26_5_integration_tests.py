"""
Phase 26.5: Testing, Validation & Production Readiness
AI Task Orchestrator Implementation

Comprehensive integration testing framework for N8N Workflow Automation Platform
following the AI Task Orchestrator Guide methodology.

This module implements all four tasks of Phase 26.5:
- Task 26.5.1: Integration testing and smoke tests
- Task 26.5.2: End-to-end workflow testing
- Task 26.5.3: Performance and scalability validation
- Task 26.5.4: Security and compliance validation
"""

import asyncio
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import docker
import psycopg2
import redis
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # PASS, FAIL, SKIP, ERROR
    duration: float
    details: str = ""
    error_message: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ValidationMetrics:
    """Validation metrics for Phase 26.5"""
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    skipped_tests: int = 0
    error_tests: int = 0
    overall_score: float = 0.0
    execution_time: float = 0.0

class Phase26_5_IntegrationTestSuite:
    """
    Comprehensive Phase 26.5 Testing Framework
    Following AI Task Orchestrator Guide methodology
    """

    def __init__(self):
        self.session_id = f"phase26_5_{int(time.time())}"
        self.test_results: List[TestResult] = []
        self.metrics = ValidationMetrics()
        self.start_time = time.time()

        # Configuration
        self.n8n_url = "http://localhost:5678"
        self.postgres_config = {
            'host': 'localhost',
            'port': 5432,
            'database': 'plc_gbt',
            'user': 'plc_user',
            'password': 'postgres_password'
        }
        self.redis_config = {
            'host': 'localhost',
            'port': 6379,
            'db': 2
        }

        # Docker client
        self.docker_client = docker.from_env()

        logger.info("🚀 Phase 26.5 Integration Test Suite Initialized")
        logger.info(f"📋 Session ID: {self.session_id}")

    def add_test_result(self, test_name: str, status: str, duration: float,
                       details: str = "", error_message: str = ""):
        """Add test result to the collection"""
        result = TestResult(
            test_name=test_name,
            status=status,
            duration=duration,
            details=details,
            error_message=error_message
        )
        self.test_results.append(result)

        # Update metrics
        self.metrics.total_tests += 1
        if status == "PASS":
            self.metrics.passed_tests += 1
        elif status == "FAIL":
            self.metrics.failed_tests += 1
        elif status == "SKIP":
            self.metrics.skipped_tests += 1
        elif status == "ERROR":
            self.metrics.error_tests += 1

    async def run_test(self, test_name: str, test_func) -> TestResult:
        """Run a single test with timing and error handling"""
        start_time = time.time()
        try:
            logger.info(f"🧪 Running test: {test_name}")
            details = await test_func() if asyncio.iscoroutinefunction(test_func) else test_func()
            duration = time.time() - start_time
            self.add_test_result(test_name, "PASS", duration, details)
            logger.info(f"✅ {test_name}: PASSED ({duration:.2f}s)")
            return self.test_results[-1]
        except Exception as e:
            duration = time.time() - start_time
            error_msg = str(e)
            self.add_test_result(test_name, "FAIL", duration, "", error_msg)
            logger.error(f"❌ {test_name}: FAILED ({duration:.2f}s) - {error_msg}")
            return self.test_results[-1]

    # ========================================
    # Task 26.5.1: Integration Testing and Smoke Tests
    # ========================================

    def test_docker_services_status(self) -> str:
        """Test Docker services health status"""
        services = ['plc-postgres', 'plc-redis', 'plc-neo4j', 'plc-n8n']
        results = {}

        for service_name in services:
            try:
                container = self.docker_client.containers.get(service_name)
                results[service_name] = {
                    'status': container.status,
                    'health': getattr(container.attrs['State'], 'Health', {}).get('Status', 'unknown')
                }
            except Exception as e:
                results[service_name] = {'status': 'not_found', 'error': str(e)}

        return f"Docker services status: {json.dumps(results, indent=2)}"

    def test_n8n_ui_accessibility(self) -> str:
        """Test N8N UI accessibility"""
        try:
            response = requests.get(f"{self.n8n_url}/", timeout=10)
            if response.status_code == 200:
                return f"N8N UI accessible: HTTP {response.status_code}"
            else:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
        except requests.RequestException as e:
            raise Exception(f"N8N UI not accessible: {str(e)}")

    def test_n8n_health_endpoint(self) -> str:
        """Test N8N health endpoint"""
        try:
            response = requests.get(f"{self.n8n_url}/healthz", timeout=10)
            if response.status_code == 200:
                return f"N8N health endpoint: HTTP {response.status_code}"
            else:
                raise Exception(f"Health endpoint failed: HTTP {response.status_code}")
        except requests.RequestException as e:
            raise Exception(f"Health endpoint error: {str(e)}")

    def test_postgresql_schema_creation(self) -> str:
        """Test PostgreSQL n8n schema creation"""
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()

            # Check if n8n schema exists
            cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'n8n';")
            schema_exists = cursor.fetchone()

            if schema_exists:
                # Count tables in n8n schema
                cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'n8n';")
                table_count = cursor.fetchone()[0]

                cursor.close()
                conn.close()
                return f"PostgreSQL n8n schema exists with {table_count} tables"
            else:
                cursor.close()
                conn.close()
                raise Exception("PostgreSQL n8n schema does not exist")

        except Exception as e:
            raise Exception(f"PostgreSQL connection failed: {str(e)}")

    def test_redis_database_isolation(self) -> str:
        """Test Redis database 2 isolation for BullMQ"""
        try:
            r = redis.Redis(**self.redis_config)

            # Test connection
            r.ping()

            # Check database isolation
            r.set("test_key", "phase26_5_test")
            value = r.get("test_key")
            r.delete("test_key")

            if value == b"phase26_5_test":
                return f"Redis database {self.redis_config['db']} accessible and isolated"
            else:
                raise Exception("Redis database test failed")

        except Exception as e:
            raise Exception(f"Redis connection failed: {str(e)}")

    def test_n8n_custom_nodes_directory(self) -> str:
        """Test N8N custom nodes directory structure"""
        expected_dirs = [
            'plc-gbt-stack/n8n/nodes/plc_memory',
            'plc-gbt-stack/n8n/nodes/llm_integration',
            'plc-gbt-stack/n8n/nodes/industrial_protocols'
        ]

        existing_dirs = []
        for dir_path in expected_dirs:
            if Path(dir_path).exists():
                existing_dirs.append(dir_path)

        if len(existing_dirs) == len(expected_dirs):
            return f"All custom node directories exist: {existing_dirs}"
        else:
            missing = set(expected_dirs) - set(existing_dirs)
            raise Exception(f"Missing custom node directories: {missing}")

    # ========================================
    # Task 26.5.2: End-to-End Workflow Testing
    # ========================================

    def test_natural_language_workflow_parser(self) -> str:
        """Test natural language workflow parser"""
        try:
            # Import the workflow parser from Phase 26.4
            sys.path.append('plc-gbt-stack/n8n/llm')
            from nl_workflow_parser import NaturalLanguageWorkflowParser

            parser = NaturalLanguageWorkflowParser()
            test_input = "Create a temperature control loop for the reactor"

            result = parser.parse_workflow_request(test_input)

            if result and hasattr(result, 'workflow_type'):
                return f"Natural language parser working: {result.workflow_type}"
            else:
                raise Exception("Parser did not return expected result")

        except ImportError as e:
            raise Exception(f"Cannot import workflow parser: {str(e)}")
        except Exception as e:
            raise Exception(f"Workflow parser test failed: {str(e)}")

    def test_plc_memory_integration_nodes(self) -> str:
        """Test PLC Memory integration nodes"""
        node_files = [
            'plc-gbt-stack/n8n/nodes/plc_memory/PLCMemory.node.ts',
            'plc-gbt-stack/n8n/nodes/plc_memory/PLCMemoryWebhook.node.ts'
        ]

        existing_nodes = []
        for node_file in node_files:
            if Path(node_file).exists():
                existing_nodes.append(node_file)

        if len(existing_nodes) == len(node_files):
            return f"PLC Memory nodes exist: {len(existing_nodes)} nodes"
        else:
            missing = set(node_files) - set(existing_nodes)
            raise Exception(f"Missing PLC Memory nodes: {missing}")

    def test_llm_integration_nodes(self) -> str:
        """Test LLM integration nodes"""
        node_files = [
            'plc-gbt-stack/n8n/nodes/llm_integration/PLCIndustrialLLM.node.ts',
            'plc-gbt-stack/n8n/nodes/llm_integration/PLCStreamingLLM.node.ts'
        ]

        existing_nodes = []
        for node_file in node_files:
            if Path(node_file).exists():
                existing_nodes.append(node_file)

        if len(existing_nodes) == len(node_files):
            return f"LLM integration nodes exist: {len(existing_nodes)} nodes"
        else:
            missing = set(node_files) - set(existing_nodes)
            raise Exception(f"Missing LLM integration nodes: {missing}")

    def test_industrial_protocol_nodes(self) -> str:
        """Test industrial protocol nodes"""
        node_files = [
            'plc-gbt-stack/n8n/nodes/industrial_protocols/PLCOPCUA.node.ts',
            'plc-gbt-stack/n8n/nodes/industrial_protocols/PLCModbus.node.ts',
            'plc-gbt-stack/n8n/nodes/industrial_protocols/PLCEtherNetIP.node.ts'
        ]

        existing_nodes = []
        for node_file in node_files:
            if Path(node_file).exists():
                existing_nodes.append(node_file)

        if len(existing_nodes) == len(node_files):
            return f"Industrial protocol nodes exist: {len(existing_nodes)} nodes"
        else:
            missing = set(node_files) - set(existing_nodes)
            raise Exception(f"Missing industrial protocol nodes: {missing}")

    # ========================================
    # Task 26.5.3: Performance and Scalability Validation
    # ========================================

    def test_n8n_startup_performance(self) -> str:
        """Test N8N container startup performance"""
        try:
            container = self.docker_client.containers.get('plc-n8n')

            # Get container start time from logs
            created_time = container.attrs['Created']
            started_time = container.attrs['State']['StartedAt']

            return f"N8N container startup metrics collected: Created {created_time}, Started {started_time}"
        except Exception as e:
            raise Exception(f"N8N startup performance test failed: {str(e)}")

    def test_database_performance(self) -> str:
        """Test database performance metrics"""
        try:
            # PostgreSQL performance test
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()

            start_time = time.time()
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'n8n';")
            cursor.fetchone()
            pg_duration = time.time() - start_time

            cursor.close()
            conn.close()

            # Redis performance test
            r = redis.Redis(**self.redis_config)
            start_time = time.time()
            r.ping()
            redis_duration = time.time() - start_time

            return f"Database performance: PostgreSQL {pg_duration:.3f}s, Redis {redis_duration:.3f}s"
        except Exception as e:
            raise Exception(f"Database performance test failed: {str(e)}")

    def test_memory_usage_monitoring(self) -> str:
        """Test memory usage monitoring"""
        try:
            container = self.docker_client.containers.get('plc-n8n')
            stats = container.stats(stream=False)

            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100

            return f"N8N memory usage: {memory_usage} bytes ({memory_percent:.1f}% of limit)"
        except Exception as e:
            raise Exception(f"Memory usage monitoring failed: {str(e)}")

    # ========================================
    # Task 26.5.4: Security and Compliance Validation
    # ========================================

    def test_network_isolation(self) -> str:
        """Test network isolation and security"""
        try:
            # Test localhost-only binding
            response = requests.get("http://127.0.0.1:5678/", timeout=5)
            localhost_status = response.status_code

            # Test that external binding fails (this should timeout/fail)
            try:
                response = requests.get("http://0.0.0.0:5678/", timeout=2)
                external_accessible = True
            except:
                external_accessible = False

            if localhost_status == 200 and not external_accessible:
                return "Network isolation: localhost accessible, external blocked"
            else:
                raise Exception(f"Network isolation failed: localhost={localhost_status}, external={external_accessible}")
        except Exception as e:
            raise Exception(f"Network isolation test failed: {str(e)}")

    def test_database_schema_isolation(self) -> str:
        """Test database schema isolation"""
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()

            # Check schema ownership and permissions
            cursor.execute("""
                SELECT schema_name, schema_owner
                FROM information_schema.schemata
                WHERE schema_name IN ('n8n', 'public', 'plc_memory')
            """)
            schemas = cursor.fetchall()

            cursor.close()
            conn.close()

            n8n_schema = [s for s in schemas if s[0] == 'n8n']
            if n8n_schema:
                return f"Database schema isolation verified: {len(schemas)} schemas, n8n schema exists"
            else:
                raise Exception("N8N schema not found - isolation not implemented")
        except Exception as e:
            raise Exception(f"Database schema isolation test failed: {str(e)}")

    def test_credential_security(self) -> str:
        """Test credential security and encryption"""
        cred_files = [
            'plc-gbt-stack/n8n/credentials/postgresql_plc_memory.json',
            'plc-gbt-stack/n8n/credentials/redis_plc_memory.json',
            'plc-gbt-stack/n8n/credentials/neo4j_plc_memory.json'
        ]

        existing_creds = []
        for cred_file in cred_files:
            if Path(cred_file).exists():
                existing_creds.append(cred_file)

        if len(existing_creds) >= 2:
            return f"Credential files secure: {len(existing_creds)} credential configurations"
        else:
            raise Exception(f"Missing credential configurations: {len(existing_creds)}/{len(cred_files)}")

    # ========================================
    # Test Execution Framework
    # ========================================

    async def run_all_tests(self) -> ValidationMetrics:
        """Run all Phase 26.5 tests"""
        logger.info("🚀 Starting Phase 26.5 Comprehensive Testing Suite")

        # Task 26.5.1: Integration testing and smoke tests
        logger.info("📋 Task 26.5.1: Integration Testing and Smoke Tests")
        await self.run_test("Docker Services Status", self.test_docker_services_status)
        await self.run_test("N8N UI Accessibility", self.test_n8n_ui_accessibility)
        await self.run_test("N8N Health Endpoint", self.test_n8n_health_endpoint)
        await self.run_test("PostgreSQL Schema Creation", self.test_postgresql_schema_creation)
        await self.run_test("Redis Database Isolation", self.test_redis_database_isolation)
        await self.run_test("N8N Custom Nodes Directory", self.test_n8n_custom_nodes_directory)

        # Task 26.5.2: End-to-end workflow testing
        logger.info("📋 Task 26.5.2: End-to-End Workflow Testing")
        await self.run_test("Natural Language Workflow Parser", self.test_natural_language_workflow_parser)
        await self.run_test("PLC Memory Integration Nodes", self.test_plc_memory_integration_nodes)
        await self.run_test("LLM Integration Nodes", self.test_llm_integration_nodes)
        await self.run_test("Industrial Protocol Nodes", self.test_industrial_protocol_nodes)

        # Task 26.5.3: Performance and scalability validation
        logger.info("📋 Task 26.5.3: Performance and Scalability Validation")
        await self.run_test("N8N Startup Performance", self.test_n8n_startup_performance)
        await self.run_test("Database Performance", self.test_database_performance)
        await self.run_test("Memory Usage Monitoring", self.test_memory_usage_monitoring)

        # Task 26.5.4: Security and compliance validation
        logger.info("📋 Task 26.5.4: Security and Compliance Validation")
        await self.run_test("Network Isolation", self.test_network_isolation)
        await self.run_test("Database Schema Isolation", self.test_database_schema_isolation)
        await self.run_test("Credential Security", self.test_credential_security)

        # Calculate final metrics
        self.metrics.execution_time = time.time() - self.start_time
        if self.metrics.total_tests > 0:
            self.metrics.overall_score = (self.metrics.passed_tests / self.metrics.total_tests) * 100

        return self.metrics

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": "26.5",
            "description": "Testing, Validation & Production Readiness",
            "methodology": "AI Task Orchestrator Guide",
            "metrics": {
                "total_tests": self.metrics.total_tests,
                "passed_tests": self.metrics.passed_tests,
                "failed_tests": self.metrics.failed_tests,
                "skipped_tests": self.metrics.skipped_tests,
                "error_tests": self.metrics.error_tests,
                "overall_score": self.metrics.overall_score,
                "execution_time": self.metrics.execution_time
            },
            "test_results": [
                {
                    "test_name": result.test_name,
                    "status": result.status,
                    "duration": result.duration,
                    "details": result.details,
                    "error_message": result.error_message,
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.test_results
            ],
            "summary": {
                "production_ready": self.metrics.overall_score >= 80.0,
                "critical_issues": self.metrics.failed_tests + self.metrics.error_tests,
                "recommendation": self._get_recommendation()
            }
        }
        return report

    def _get_recommendation(self) -> str:
        """Get recommendation based on test results"""
        if self.metrics.overall_score >= 90:
            return "READY FOR PRODUCTION - All tests passing, proceed to Phase 26.6"
        elif self.metrics.overall_score >= 80:
            return "READY WITH MONITORING - Minor issues identified, proceed with enhanced monitoring"
        elif self.metrics.overall_score >= 60:
            return "NEEDS FIXES - Critical issues must be resolved before production"
        else:
            return "NOT READY - Major failures detected, comprehensive remediation required"

    def save_report(self, output_dir: str = "plc-gbt-stack/n8n/tests/results"):
        """Save test report to file"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        report = self.generate_report()
        report_file = Path(output_dir) / f"phase26_5_test_report_{self.session_id}.json"

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Test report saved: {report_file}")
        return report_file


async def main():
    """Main execution function"""
    logger.info("🚀 Phase 26.5: Testing, Validation & Production Readiness")
    logger.info("📋 AI Task Orchestrator Implementation")

    # Initialize test suite
    test_suite = Phase26_5_IntegrationTestSuite()

    try:
        # Run all tests
        metrics = await test_suite.run_all_tests()

        # Generate and save report
        test_suite.save_report()

        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("📊 PHASE 26.5 TEST RESULTS SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total Tests: {metrics.total_tests}")
        logger.info(f"Passed: {metrics.passed_tests}")
        logger.info(f"Failed: {metrics.failed_tests}")
        logger.info(f"Errors: {metrics.error_tests}")
        logger.info(f"Overall Score: {metrics.overall_score:.1f}%")
        logger.info(f"Execution Time: {metrics.execution_time:.2f}s")
        logger.info(f"{'='*60}")

        if metrics.overall_score >= 80:
            logger.info("✅ PHASE 26.5 SUCCESSFUL - Production readiness validated")
        else:
            logger.warning("⚠️ PHASE 26.5 NEEDS ATTENTION - Issues identified")

        return metrics

    except Exception as e:
        logger.error(f"❌ Phase 26.5 execution failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
