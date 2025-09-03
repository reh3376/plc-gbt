#!/usr/bin/env python3
"""
Phase 26.7: n8n-MCP AI Enhancement Integration - Comprehensive Validation Script

This script validates the n8n-MCP integration with the existing PLC-GBT Phase 26
N8N Workflow Automation Platform, ensuring compatibility with the fine-tuned LLM
and multi-database architecture.

Usage:
    python phase26_7_n8n_mcp_integration_validation.py
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

import aiohttp
import docker
from docker.errors import NotFound

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class N8NMCPIntegrationValidator:
    """Comprehensive validator for n8n-MCP integration with PLC-GBT ecosystem."""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.validation_results = {}
        self.start_time = datetime.now()
        self.session_id = f"phase26_7_validation_{int(time.time())}"

        # Service endpoints
        self.n8n_url = "http://127.0.0.1:5678"
        self.n8n_mcp_url = "http://127.0.0.1:3000"
        self.vault_url = "http://127.0.0.1:8200"
        self.gateway_url = "http://127.0.0.1:8000"

        # Expected containers
        self.required_containers = [
            "plc-n8n",
            "plc-n8n-mcp",
            "plc-neo4j",
            "plc-postgres",
            "plc-redis",
            "plc-qdrant",
            "plc-vault"
        ]

    async def run_validation(self) -> Dict:
        """Run comprehensive validation of n8n-MCP integration."""
        logger.info(f"Starting Phase 26.7 n8n-MCP Integration Validation - Session: {self.session_id}")

        validation_tasks = [
            ("Infrastructure", self.validate_infrastructure),
            ("Docker Services", self.validate_docker_services),
            ("Network Connectivity", self.validate_network_connectivity),
            ("n8n-MCP Service", self.validate_n8n_mcp_service),
            ("n8n Integration", self.validate_n8n_integration),
            ("Database Compatibility", self.validate_database_compatibility),
            ("MCP Tools", self.validate_mcp_tools),
            ("Performance", self.validate_performance),
            ("Security", self.validate_security),
            ("End-to-End Workflow", self.validate_end_to_end)
        ]

        overall_score = 0
        total_tests = len(validation_tasks)

        for test_name, test_func in validation_tasks:
            logger.info(f"Running {test_name} validation...")
            try:
                result = await test_func()
                self.validation_results[test_name] = result
                score = result.get('score', 0)
                overall_score += score

                status = "✅ PASS" if score >= 80 else "⚠️ WARN" if score >= 60 else "❌ FAIL"
                logger.info(f"{test_name}: {status} ({score}%)")

            except Exception as e:
                logger.error(f"{test_name} validation failed: {e}")
                self.validation_results[test_name] = {
                    'score': 0,
                    'status': 'ERROR',
                    'error': str(e),
                    'details': {}
                }

        # Calculate overall results
        overall_percentage = (overall_score / total_tests) if total_tests > 0 else 0

        self.validation_results['summary'] = {
            'session_id': self.session_id,
            'overall_score': overall_percentage,
            'total_tests': total_tests,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - self.start_time).total_seconds(),
            'status': self._get_overall_status(overall_percentage)
        }

        # Save results
        await self.save_results()

        logger.info(f"Validation complete. Overall score: {overall_percentage:.1f}%")
        return self.validation_results

    async def validate_infrastructure(self) -> Dict:
        """Validate basic infrastructure requirements."""
        details = {}
        score = 0

        try:
            # Check Docker availability
            docker_info = self.docker_client.info()
            details['docker_available'] = True
            details['docker_version'] = docker_info.get('ServerVersion', 'unknown')
            score += 20

            # Check Docker Compose project
            try:
                containers = self.docker_client.containers.list(
                    filters={"label": "com.docker.compose.project=plc-gbt-stack"}
                )
                details['compose_project_found'] = len(containers) > 0
                if len(containers) > 0:
                    score += 20
            except Exception as e:
                details['compose_project_error'] = str(e)

            # Check required directories
            required_dirs = [
                project_root / "plc-gbt-stack",
                project_root / "plc-gbt-stack" / ".cursor",
                project_root / "plc-gbt-stack" / "scripts" / "validation"
            ]

            dirs_exist = 0
            for dir_path in required_dirs:
                if dir_path.exists():
                    dirs_exist += 1

            details['required_directories'] = f"{dirs_exist}/{len(required_dirs)}"
            score += (dirs_exist / len(required_dirs)) * 20

            # Check configuration files
            config_files = [
                project_root / "plc-gbt-stack" / "docker-compose.yml",
                project_root / "plc-gbt-stack" / ".cursor" / "mcp.json"
            ]

            configs_exist = 0
            for config_file in config_files:
                if config_file.exists():
                    configs_exist += 1

            details['configuration_files'] = f"{configs_exist}/{len(config_files)}"
            score += (configs_exist / len(config_files)) * 20

            # Check environment variables
            env_vars = ['N8N_MCP_AUTH_TOKEN', 'NEO4J_PASSWORD', 'POSTGRES_PASSWORD']
            env_available = sum(1 for var in env_vars if os.getenv(var) is not None)
            details['environment_variables'] = f"{env_available}/{len(env_vars)}"
            score += (env_available / len(env_vars)) * 20

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_docker_services(self) -> Dict:
        """Validate Docker service health and configuration."""
        details = {}
        score = 0

        try:
            running_containers = []
            healthy_containers = []

            for container_name in self.required_containers:
                try:
                    container = self.docker_client.containers.get(container_name)
                    running_containers.append(container_name)

                    # Check health status
                    health = container.attrs.get('State', {}).get('Health', {})
                    status = health.get('Status', 'unknown')

                    if status == 'healthy' or (status == 'none' and container.status == 'running'):
                        healthy_containers.append(container_name)

                    details[f'{container_name}_status'] = container.status
                    details[f'{container_name}_health'] = status

                except NotFound:
                    details[f'{container_name}_status'] = 'not_found'
                except Exception as e:
                    details[f'{container_name}_error'] = str(e)

            # Calculate scores
            running_score = (len(running_containers) / len(self.required_containers)) * 50
            health_score = (len(healthy_containers) / len(self.required_containers)) * 50
            score = running_score + health_score

            details['containers_running'] = f"{len(running_containers)}/{len(self.required_containers)}"
            details['containers_healthy'] = f"{len(healthy_containers)}/{len(self.required_containers)}"

            # Special validation for n8n-mcp container
            try:
                n8n_mcp_container = self.docker_client.containers.get("plc-n8n-mcp")
                env_vars = n8n_mcp_container.attrs.get('Config', {}).get('Env', [])

                required_env = ['MCP_MODE=http', 'N8N_API_URL=http://plc-n8n:5678']
                env_found = [env for env in env_vars if any(req in env for req in required_env)]

                details['n8n_mcp_environment'] = f"{len(env_found)}/{len(required_env)}"

            except Exception as e:
                details['n8n_mcp_validation_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_network_connectivity(self) -> Dict:
        """Validate network connectivity between services."""
        details = {}
        score = 0

        try:
            # Test service endpoints
            endpoints = [
                ('n8n', self.n8n_url + '/healthz'),
                ('n8n-mcp', self.n8n_mcp_url + '/health'),
                ('vault', self.vault_url + '/v1/sys/health'),
                ('gateway', self.gateway_url + '/health')
            ]

            successful_connections = 0

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                for service_name, endpoint in endpoints:
                    try:
                        async with session.get(endpoint) as response:
                            if response.status in [200, 429]:  # 429 for Vault rate limiting
                                successful_connections += 1
                                details[f'{service_name}_connectivity'] = 'OK'
                            else:
                                details[f'{service_name}_connectivity'] = f'HTTP_{response.status}'
                    except Exception as e:
                        details[f'{service_name}_connectivity'] = f'ERROR: {str(e)}'

            score = (successful_connections / len(endpoints)) * 100
            details['successful_connections'] = f"{successful_connections}/{len(endpoints)}"

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_n8n_mcp_service(self) -> Dict:
        """Validate n8n-MCP service functionality."""
        details = {}
        score = 0

        try:
            # Test MCP health endpoint
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    async with session.get(f"{self.n8n_mcp_url}/health") as response:
                        if response.status == 200:
                            health_data = await response.json()
                            details['health_status'] = health_data.get('status', 'unknown')
                            details['mcp_mode'] = health_data.get('mode', 'unknown')
                            details['version'] = health_data.get('version', 'unknown')

                            if health_data.get('status') == 'healthy':
                                score += 30

                except Exception as e:
                    details['health_endpoint_error'] = str(e)

                # Test MCP tools endpoint
                try:
                    async with session.get(f"{self.n8n_mcp_url}/tools") as response:
                        if response.status == 200:
                            tools_data = await response.json()
                            details['available_tools'] = len(tools_data.get('tools', []))

                            # Check for essential MCP tools
                            essential_tools = [
                                'tools_documentation',
                                'list_nodes',
                                'get_node_essentials',
                                'validate_workflow'
                            ]

                            available_tool_names = [tool.get('name', '') for tool in tools_data.get('tools', [])]
                            essential_found = sum(1 for tool in essential_tools if tool in available_tool_names)

                            details['essential_tools'] = f"{essential_found}/{len(essential_tools)}"
                            score += (essential_found / len(essential_tools)) * 30

                except Exception as e:
                    details['tools_endpoint_error'] = str(e)

                # Test database connectivity
                try:
                    async with session.get(f"{self.n8n_mcp_url}/database/stats") as response:
                        if response.status == 200:
                            db_data = await response.json()
                            details['database_ready'] = db_data.get('ready', False)
                            details['node_count'] = db_data.get('node_count', 0)

                            if db_data.get('ready') and db_data.get('node_count', 0) > 500:
                                score += 20

                except Exception as e:
                    details['database_stats_error'] = str(e)

                # Test n8n API connectivity through MCP
                try:
                    headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}
                    async with session.get(f"{self.n8n_mcp_url}/n8n/health", headers=headers) as response:
                        if response.status == 200:
                            n8n_health = await response.json()
                            details['n8n_api_connectivity'] = n8n_health.get('status', 'unknown')
                            score += 20
                        else:
                            details['n8n_api_status'] = response.status

                except Exception as e:
                    details['n8n_api_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_n8n_integration(self) -> Dict:
        """Validate n8n service integration and API compatibility."""
        details = {}
        score = 0

        try:
            # Direct n8n health check
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                try:
                    async with session.get(f"{self.n8n_url}/healthz") as response:
                        if response.status == 200:
                            details['n8n_health'] = 'OK'
                            score += 25
                        else:
                            details['n8n_health'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['n8n_health_error'] = str(e)

                # Test n8n API endpoints
                api_endpoints = [
                    '/api/v1/workflows',
                    '/api/v1/executions',
                    '/api/v1/credentials/schema'
                ]

                api_success = 0
                headers = {'X-N8N-API-KEY': os.getenv('N8N_API_KEY', '')} if os.getenv('N8N_API_KEY') else {}

                for endpoint in api_endpoints:
                    try:
                        async with session.get(f"{self.n8n_url}{endpoint}", headers=headers) as response:
                            if response.status in [200, 401]:  # 401 expected without API key
                                api_success += 1
                                details[f'api{endpoint.replace("/", "_")}'] = response.status
                    except Exception as e:
                        details[f'api{endpoint.replace("/", "_")}_error'] = str(e)

                score += (api_success / len(api_endpoints)) * 25
                details['api_endpoints_accessible'] = f"{api_success}/{len(api_endpoints)}"

                # Test workflow validation through MCP
                try:
                    test_workflow = {
                        "name": "Test Workflow",
                        "nodes": [
                            {
                                "id": "test-node",
                                "type": "n8n-nodes-base.start",
                                "typeVersion": 1,
                                "position": [100, 200]
                            }
                        ],
                        "connections": {},
                        "active": False
                    }

                    mcp_headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}

                    async with session.post(
                        f"{self.n8n_mcp_url}/validate/workflow",
                        json=test_workflow,
                        headers=mcp_headers
                    ) as response:
                        if response.status == 200:
                            validation_result = await response.json()
                            details['workflow_validation'] = 'OK'
                            details['validation_score'] = validation_result.get('score', 0)
                            score += 25
                        else:
                            details['workflow_validation'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['workflow_validation_error'] = str(e)

                # Test industrial automation compatibility
                try:
                    industrial_query = "modbus opc industrial"

                    async with session.get(
                        f"{self.n8n_mcp_url}/search/nodes",
                        params={'query': industrial_query},
                        headers=mcp_headers
                    ) as response:
                        if response.status == 200:
                            search_results = await response.json()
                            industrial_nodes = len(search_results.get('nodes', []))
                            details['industrial_nodes_found'] = industrial_nodes

                            if industrial_nodes > 0:
                                score += 25

                except Exception as e:
                    details['industrial_search_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_database_compatibility(self) -> Dict:
        """Validate multi-database architecture compatibility."""
        details = {}
        score = 0

        try:
            # Test database connections through existing services
            database_services = [
                ('redis', 'redis://plc-redis:6379'),
                ('neo4j', 'bolt://plc-neo4j:7687'),
                ('postgres', 'postgresql://plc-postgres:5432'),
                ('qdrant', 'http://plc-qdrant:6333')
            ]

            accessible_dbs = 0

            for db_name, _connection_string in database_services:
                try:
                    # Use Docker network to test connectivity
                    container = self.docker_client.containers.get(f"plc-{db_name}")
                    if container.status == 'running':
                        accessible_dbs += 1
                        details[f'{db_name}_status'] = 'running'
                    else:
                        details[f'{db_name}_status'] = container.status

                except Exception as e:
                    details[f'{db_name}_error'] = str(e)

            score = (accessible_dbs / len(database_services)) * 100
            details['accessible_databases'] = f"{accessible_dbs}/{len(database_services)}"

            # Validate namespace isolation
            try:
                n8n_mcp_container = self.docker_client.containers.get("plc-n8n-mcp")
                volumes = n8n_mcp_container.attrs.get('Mounts', [])

                isolated_storage = any('n8n_mcp_data' in vol.get('Source', '') for vol in volumes)
                details['namespace_isolation'] = isolated_storage

                if isolated_storage:
                    score = min(score + 10, 100)  # Bonus for proper isolation

            except Exception as e:
                details['isolation_check_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_mcp_tools(self) -> Dict:
        """Validate MCP tools functionality and coverage."""
        details = {}
        score = 0

        try:
            headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # Test essential MCP tools
                essential_tests = [
                    ('tools_documentation', f"{self.n8n_mcp_url}/tools/documentation"),
                    ('list_nodes', f"{self.n8n_mcp_url}/nodes"),
                    ('search_nodes', f"{self.n8n_mcp_url}/search/nodes?query=http"),
                    ('get_node_essentials', f"{self.n8n_mcp_url}/nodes/n8n-nodes-base.httpRequest/essentials")
                ]

                successful_tools = 0

                for tool_name, endpoint in essential_tests:
                    try:
                        async with session.get(endpoint, headers=headers) as response:
                            if response.status == 200:
                                successful_tools += 1
                                details[f'{tool_name}_status'] = 'OK'

                                # Additional validation for specific tools
                                if tool_name == 'list_nodes':
                                    data = await response.json()
                                    node_count = len(data.get('nodes', []))
                                    details['total_nodes'] = node_count

                                elif tool_name == 'search_nodes':
                                    data = await response.json()
                                    search_results = len(data.get('nodes', []))
                                    details['search_functionality'] = f"{search_results} results"

                            else:
                                details[f'{tool_name}_status'] = f'HTTP_{response.status}'

                    except Exception as e:
                        details[f'{tool_name}_error'] = str(e)

                tool_score = (successful_tools / len(essential_tests)) * 60
                score += tool_score

                # Test advanced MCP functionality
                advanced_tests = [
                    ('validate_workflow', f"{self.n8n_mcp_url}/validate/workflow"),
                    ('ai_tools', f"{self.n8n_mcp_url}/ai/tools"),
                    ('database_stats', f"{self.n8n_mcp_url}/database/stats")
                ]

                advanced_success = 0

                for tool_name, endpoint in advanced_tests:
                    try:
                        if tool_name == 'validate_workflow':
                            # POST test with sample workflow
                            test_data = {"name": "Test", "nodes": [], "connections": {}}
                            async with session.post(endpoint, json=test_data, headers=headers) as response:
                                if response.status == 200:
                                    advanced_success += 1
                                    details[f'{tool_name}_advanced'] = 'OK'
                                else:
                                    details[f'{tool_name}_advanced'] = f'HTTP_{response.status}'
                        else:
                            # GET test
                            async with session.get(endpoint, headers=headers) as response:
                                if response.status == 200:
                                    advanced_success += 1
                                    details[f'{tool_name}_advanced'] = 'OK'
                                else:
                                    details[f'{tool_name}_advanced'] = f'HTTP_{response.status}'

                    except Exception as e:
                        details[f'{tool_name}_advanced_error'] = str(e)

                advanced_score = (advanced_success / len(advanced_tests)) * 40
                score += advanced_score

                details['essential_tools_success'] = f"{successful_tools}/{len(essential_tests)}"
                details['advanced_tools_success'] = f"{advanced_success}/{len(advanced_tests)}"

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_performance(self) -> Dict:
        """Validate performance metrics and response times."""
        details = {}
        score = 0

        try:
            headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # Test response times
                performance_tests = [
                    ('health_check', f"{self.n8n_mcp_url}/health"),
                    ('node_search', f"{self.n8n_mcp_url}/search/nodes?query=http"),
                    ('tools_list', f"{self.n8n_mcp_url}/tools"),
                    ('database_stats', f"{self.n8n_mcp_url}/database/stats")
                ]

                response_times = []
                successful_requests = 0

                for test_name, endpoint in performance_tests:
                    try:
                        start_time = time.time()
                        async with session.get(endpoint, headers=headers) as response:
                            end_time = time.time()
                            response_time = (end_time - start_time) * 1000  # Convert to ms

                            if response.status == 200:
                                successful_requests += 1
                                response_times.append(response_time)
                                details[f'{test_name}_response_time'] = f"{response_time:.2f}ms"
                            else:
                                details[f'{test_name}_status'] = response.status

                    except Exception as e:
                        details[f'{test_name}_error'] = str(e)

                # Calculate performance scores
                if response_times:
                    avg_response_time = sum(response_times) / len(response_times)
                    details['average_response_time'] = f"{avg_response_time:.2f}ms"

                    # Score based on average response time (target: <100ms excellent, <500ms good)
                    if avg_response_time < 100:
                        time_score = 40
                    elif avg_response_time < 500:
                        time_score = 30
                    elif avg_response_time < 1000:
                        time_score = 20
                    else:
                        time_score = 10

                    score += time_score

                # Score based on successful requests
                success_rate = (successful_requests / len(performance_tests)) * 100
                details['success_rate'] = f"{success_rate:.1f}%"
                score += (success_rate / 100) * 40

                # Memory usage check
                try:
                    n8n_mcp_container = self.docker_client.containers.get("plc-n8n-mcp")
                    stats = n8n_mcp_container.stats(stream=False)

                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100

                    details['memory_usage'] = f"{memory_percent:.1f}%"

                    # Score based on memory efficiency (target: <50% excellent, <75% good)
                    if memory_percent < 50:
                        memory_score = 20
                    elif memory_percent < 75:
                        memory_score = 15
                    else:
                        memory_score = 10

                    score += memory_score

                except Exception as e:
                    details['memory_check_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_security(self) -> Dict:
        """Validate security configuration and compliance."""
        details = {}
        score = 0

        try:
            # Check container security configuration
            try:
                n8n_mcp_container = self.docker_client.containers.get("plc-n8n-mcp")
                container_config = n8n_mcp_container.attrs

                # Check if running as non-root
                user = container_config.get('Config', {}).get('User', '')
                details['non_root_user'] = bool(user and user != 'root')
                if details['non_root_user']:
                    score += 20

                # Check network isolation
                networks = container_config.get('NetworkSettings', {}).get('Networks', {})
                isolated_network = 'plc-internal-network' in networks
                details['network_isolation'] = isolated_network
                if isolated_network:
                    score += 20

                # Check port exposure (should only expose to localhost)
                ports = container_config.get('NetworkSettings', {}).get('Ports', {})
                localhost_only = True
                for port_config in ports.values():
                    if port_config:
                        for binding in port_config:
                            if binding.get('HostIp') not in ['127.0.0.1', 'localhost']:
                                localhost_only = False
                                break

                details['localhost_only_binding'] = localhost_only
                if localhost_only:
                    score += 20

            except Exception as e:
                details['container_security_error'] = str(e)

            # Test authentication
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                    # Test without authentication
                    async with session.get(f"{self.n8n_mcp_url}/tools") as response:
                        auth_required = response.status == 401
                        details['authentication_required'] = auth_required
                        if auth_required:
                            score += 20

                    # Test with authentication
                    headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}
                    async with session.get(f"{self.n8n_mcp_url}/tools", headers=headers) as response:
                        auth_works = response.status == 200
                        details['authentication_functional'] = auth_works
                        if auth_works:
                            score += 20

            except Exception as e:
                details['authentication_test_error'] = str(e)

            # Check environment variable security
            try:
                env_vars = n8n_mcp_container.attrs.get('Config', {}).get('Env', [])
                sensitive_exposed = any('PASSWORD' in env and '=' in env for env in env_vars)
                details['sensitive_env_exposed'] = sensitive_exposed
                if not sensitive_exposed:  # Good if no sensitive data exposed
                    score += 20

            except Exception as e:
                details['env_security_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    async def validate_end_to_end(self) -> Dict:
        """Validate end-to-end workflow creation and management."""
        details = {}
        score = 0

        try:
            headers = {'Authorization': f'Bearer {os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025")}'}

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as session:
                # Test complete workflow development cycle

                # 1. Search for nodes
                try:
                    async with session.get(
                        f"{self.n8n_mcp_url}/search/nodes",
                        params={'query': 'http webhook'},
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            search_data = await response.json()
                            found_nodes = len(search_data.get('nodes', []))
                            details['node_discovery'] = f"{found_nodes} nodes found"
                            if found_nodes > 0:
                                score += 15
                        else:
                            details['node_discovery'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['node_discovery_error'] = str(e)

                # 2. Get node essentials
                try:
                    async with session.get(
                        f"{self.n8n_mcp_url}/nodes/n8n-nodes-base.webhook/essentials",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            essentials_data = await response.json()
                            properties_count = len(essentials_data.get('properties', []))
                            details['node_configuration'] = f"{properties_count} essential properties"
                            if properties_count > 0:
                                score += 15
                        else:
                            details['node_configuration'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['node_configuration_error'] = str(e)

                # 3. Validate workflow structure
                try:
                    test_workflow = {
                        "name": "Phase 26.7 Test Workflow",
                        "nodes": [
                            {
                                "id": "webhook",
                                "type": "n8n-nodes-base.webhook",
                                "typeVersion": 1,
                                "position": [100, 200],
                                "parameters": {
                                    "path": "test-webhook"
                                }
                            },
                            {
                                "id": "set-data",
                                "type": "n8n-nodes-base.set",
                                "typeVersion": 1,
                                "position": [300, 200],
                                "parameters": {
                                    "values": {
                                        "string": [
                                            {
                                                "name": "message",
                                                "value": "Phase 26.7 Integration Test"
                                            }
                                        ]
                                    }
                                }
                            }
                        ],
                        "connections": {
                            "webhook": {
                                "main": [
                                    [
                                        {
                                            "node": "set-data",
                                            "type": "main",
                                            "index": 0
                                        }
                                    ]
                                ]
                            }
                        },
                        "active": False
                    }

                    async with session.post(
                        f"{self.n8n_mcp_url}/validate/workflow",
                        json=test_workflow,
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            validation_data = await response.json()
                            validation_score = validation_data.get('score', 0)
                            details['workflow_validation'] = f"{validation_score}% valid"

                            if validation_score >= 80:
                                score += 20
                            elif validation_score >= 60:
                                score += 15
                            else:
                                score += 10
                        else:
                            details['workflow_validation'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['workflow_validation_error'] = str(e)

                # 4. Test AI tools functionality
                try:
                    async with session.get(
                        f"{self.n8n_mcp_url}/ai/tools",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            ai_tools_data = await response.json()
                            ai_tools_count = len(ai_tools_data.get('tools', []))
                            details['ai_tools_available'] = f"{ai_tools_count} AI tools"

                            if ai_tools_count >= 263:  # Expected AI-capable nodes
                                score += 20
                            elif ai_tools_count >= 100:
                                score += 15
                            else:
                                score += 10
                        else:
                            details['ai_tools_available'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['ai_tools_error'] = str(e)

                # 5. Test industrial automation capabilities
                try:
                    industrial_query = "modbus opc plc industrial automation"
                    async with session.get(
                        f"{self.n8n_mcp_url}/search/nodes",
                        params={'query': industrial_query},
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            industrial_data = await response.json()
                            industrial_nodes = len(industrial_data.get('nodes', []))
                            details['industrial_automation'] = f"{industrial_nodes} industrial nodes"

                            if industrial_nodes > 0:
                                score += 15
                        else:
                            details['industrial_automation'] = f'HTTP_{response.status}'

                except Exception as e:
                    details['industrial_automation_error'] = str(e)

                # 6. Test performance under load
                try:
                    start_time = time.time()

                    # Perform multiple concurrent requests
                    tasks = []
                    for _i in range(5):
                        task = session.get(f"{self.n8n_mcp_url}/health", headers=headers)
                        tasks.append(task)

                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    end_time = time.time()

                    successful_concurrent = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
                    total_time = (end_time - start_time) * 1000

                    details['concurrent_performance'] = f"{successful_concurrent}/5 requests in {total_time:.2f}ms"

                    if successful_concurrent >= 4 and total_time < 5000:
                        score += 15
                    elif successful_concurrent >= 3:
                        score += 10

                except Exception as e:
                    details['concurrent_performance_error'] = str(e)

        except Exception as e:
            details['error'] = str(e)

        return {
            'score': score,
            'status': 'PASS' if score >= 80 else 'WARN' if score >= 60 else 'FAIL',
            'details': details
        }

    def _get_overall_status(self, score: float) -> str:
        """Get overall status based on score."""
        if score >= 90:
            return "EXCELLENT"
        elif score >= 80:
            return "PASS"
        elif score >= 60:
            return "WARN"
        else:
            return "FAIL"

    async def save_results(self):
        """Save validation results to file."""
        results_dir = project_root / "plc-gbt-stack" / "results" / "phase26_7"
        results_dir.mkdir(parents=True, exist_ok=True)

        # Save detailed JSON results
        json_file = results_dir / f"n8n_mcp_validation_{self.session_id}.json"
        with open(json_file, 'w') as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        # Save markdown report
        md_file = results_dir / f"n8n_mcp_validation_report_{self.session_id}.md"
        with open(md_file, 'w') as f:
            f.write(self._generate_markdown_report())

        logger.info(f"Results saved to {json_file} and {md_file}")

    def _generate_markdown_report(self) -> str:
        """Generate markdown validation report."""
        summary = self.validation_results.get('summary', {})
        overall_score = summary.get('overall_score', 0)
        status = summary.get('status', 'UNKNOWN')

        report = f"""# Phase 26.7: n8n-MCP Integration Validation Report

**Session ID**: {self.session_id}
**Timestamp**: {summary.get('timestamp', 'unknown')}
**Duration**: {summary.get('duration_seconds', 0):.2f} seconds
**Overall Score**: {overall_score:.1f}%
**Status**: {status}

## Executive Summary

Phase 26.7 n8n-MCP AI Enhancement Integration validation completed with an overall score of {overall_score:.1f}%.
This integration provides AI-assisted workflow development capabilities to the existing PLC-GBT N8N Workflow
Automation Platform while maintaining full compatibility with the fine-tuned LLM and multi-database architecture.

## Validation Results

"""

        for test_name, result in self.validation_results.items():
            if test_name == 'summary':
                continue

            score = result.get('score', 0)
            status = result.get('status', 'UNKNOWN')
            details = result.get('details', {})

            status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"

            report += f"""### {test_name} {status_emoji}

**Score**: {score:.1f}%
**Status**: {status}

"""

            if details:
                report += "**Details**:\n"
                for key, value in details.items():
                    if not key.endswith('_error'):
                        report += f"- {key.replace('_', ' ').title()}: {value}\n"

                # Show errors separately
                errors = {k: v for k, v in details.items() if k.endswith('_error')}
                if errors:
                    report += "\n**Errors**:\n"
                    for key, value in errors.items():
                        report += f"- {key.replace('_', ' ').title()}: {value}\n"

            report += "\n"

        # Recommendations
        if overall_score >= 90:
            recommendation = "🎉 EXCELLENT - Ready for production deployment"
        elif overall_score >= 80:
            recommendation = "✅ PASS - Ready for production with monitoring"
        elif overall_score >= 60:
            recommendation = "⚠️ WARNING - Address issues before production"
        else:
            recommendation = "❌ FAIL - Critical issues must be resolved"

        report += f"""## Recommendation

{recommendation}

## Next Steps

"""

        if overall_score >= 80:
            report += """- ✅ n8n-MCP integration is ready for production use
- ✅ AI-assisted workflow development can be enabled
- ✅ Cursor IDE integration can be deployed to development teams
- ✅ Industrial automation workflows can be created with AI assistance
"""
        else:
            report += """- 🔧 Review and address validation failures
- 🔧 Ensure all Docker services are running correctly
- 🔧 Verify network connectivity and security configuration
- 🔧 Re-run validation after fixes
"""

        report += """
## Technical Details

- **n8n-MCP Image**: ghcr.io/czlonkowski/n8n-mcp:latest
- **Integration Mode**: Docker Option 2 (self-hosted)
- **Network**: plc-internal-network
- **Database**: Isolated namespace with custom path
- **API Connectivity**: http://plc-n8n:5678
- **MCP Endpoint**: http://127.0.0.1:3000

---
*Generated by Phase 26.7 n8n-MCP Integration Validator*
"""

        return report

async def main():
    """Main validation function."""
    validator = N8NMCPIntegrationValidator()

    try:
        results = await validator.run_validation()

        # Print summary
        summary = results.get('summary', {})
        overall_score = summary.get('overall_score', 0)
        status = summary.get('status', 'UNKNOWN')

        print(f"\n{'='*60}")
        print("PHASE 26.7 N8N-MCP INTEGRATION VALIDATION COMPLETE")
        print(f"{'='*60}")
        print(f"Overall Score: {overall_score:.1f}%")
        print(f"Status: {status}")
        print(f"Session ID: {validator.session_id}")
        print(f"Duration: {summary.get('duration_seconds', 0):.2f} seconds")

        if overall_score >= 80:
            print("\n🎉 SUCCESS: n8n-MCP integration is ready for production!")
        elif overall_score >= 60:
            print("\n⚠️ WARNING: Address issues before production deployment")
        else:
            print("\n❌ FAILURE: Critical issues must be resolved")

        return 0 if overall_score >= 80 else 1

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
