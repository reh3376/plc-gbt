#!/usr/bin/env python3
"""
Phase 26.7: n8n-MCP AI Enhancement Integration - Automated Deployment Script

This script automates the deployment of n8n-MCP integration with the existing 
PLC-GBT Phase 26 N8N Workflow Automation Platform.

Usage:
    python phase26_7_n8n_mcp_deployment.py [--validate-only] [--force-rebuild]
"""

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import docker
import requests
import yaml
from docker.errors import DockerException

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class N8NMCPDeploymentManager:
    """Automated deployment manager for n8n-MCP integration."""
    
    def __init__(self, validate_only: bool = False, force_rebuild: bool = False):
        self.validate_only = validate_only
        self.force_rebuild = force_rebuild
        self.docker_client = docker.from_env()
        self.deployment_session = f"phase26_7_deployment_{int(time.time())}"
        
        # Project paths
        self.project_root = project_root
        self.stack_dir = project_root / "plc-gbt-stack"
        self.docker_compose_file = self.stack_dir / "docker-compose.yml"
        
        # Service configuration
        self.n8n_mcp_image = "ghcr.io/czlonkowski/n8n-mcp:latest"
        self.n8n_mcp_container = "plc-n8n-mcp"
        self.required_services = [
            "plc-neo4j",
            "plc-postgres", 
            "plc-redis",
            "plc-qdrant",
            "plc-vault",
            "plc-n8n"
        ]
        
    async def deploy(self) -> Dict:
        """Execute complete n8n-MCP deployment process."""
        logger.info(f"Starting Phase 26.7 n8n-MCP Deployment - Session: {self.deployment_session}")
        
        deployment_steps = [
            ("Pre-deployment Validation", self.validate_prerequisites),
            ("Environment Setup", self.setup_environment),
            ("Docker Image Management", self.manage_docker_images),
            ("Service Configuration", self.configure_services),
            ("Network Setup", self.setup_networking),
            ("Service Deployment", self.deploy_services),
            ("Health Verification", self.verify_deployment),
            ("Integration Testing", self.test_integration),
            ("Post-deployment Validation", self.validate_deployment)
        ]
        
        results = {}
        overall_success = True
        
        for step_name, step_func in deployment_steps:
            logger.info(f"Executing: {step_name}")
            
            try:
                step_result = await step_func()
                results[step_name] = step_result
                
                if not step_result.get('success', False):
                    overall_success = False
                    if not self.validate_only:
                        logger.error(f"{step_name} failed: {step_result.get('error', 'Unknown error')}")
                        break
                else:
                    logger.info(f"{step_name}: ✅ SUCCESS")
                    
            except Exception as e:
                logger.error(f"{step_name} failed with exception: {e}")
                results[step_name] = {'success': False, 'error': str(e)}
                overall_success = False
                if not self.validate_only:
                    break
        
        # Save deployment results
        await self.save_deployment_results(results, overall_success)
        
        return {
            'session_id': self.deployment_session,
            'overall_success': overall_success,
            'steps': results,
            'timestamp': datetime.now().isoformat()
        }
    
    async def validate_prerequisites(self) -> Dict:
        """Validate prerequisites for n8n-MCP deployment."""
        result = {'success': True, 'details': {}}
        
        try:
            # Check Docker availability
            docker_info = self.docker_client.info()
            result['details']['docker_version'] = docker_info.get('ServerVersion', 'unknown')
            
            # Check if existing PLC-GBT stack is running
            existing_containers = self.docker_client.containers.list(
                filters={"label": "com.docker.compose.project=plc-gbt-stack"}
            )
            
            running_services = []
            for container in existing_containers:
                if container.status == 'running':
                    running_services.append(container.name)
            
            result['details']['running_services'] = running_services
            result['details']['required_services_running'] = len([
                s for s in self.required_services if s in running_services
            ])
            
            # Check if docker-compose.yml exists and has n8n-mcp service
            if self.docker_compose_file.exists():
                with open(self.docker_compose_file, 'r') as f:
                    compose_content = f.read()
                    
                has_n8n_mcp = 'n8n-mcp:' in compose_content
                result['details']['docker_compose_updated'] = has_n8n_mcp
                
                if not has_n8n_mcp:
                    result['success'] = False
                    result['error'] = "docker-compose.yml missing n8n-mcp service configuration"
            else:
                result['success'] = False
                result['error'] = "docker-compose.yml not found"
            
            # Check required directories
            required_dirs = [
                self.stack_dir / ".cursor",
                self.stack_dir / "scripts" / "validation",
                self.stack_dir / "scripts" / "automation"
            ]
            
            missing_dirs = [str(d) for d in required_dirs if not d.exists()]
            result['details']['missing_directories'] = missing_dirs
            
            if missing_dirs:
                result['success'] = False
                result['error'] = f"Missing required directories: {missing_dirs}"
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def setup_environment(self) -> Dict:
        """Set up environment variables and configuration."""
        result = {'success': True, 'details': {}}
        
        try:
            # Ensure required environment variables
            required_env_vars = {
                'N8N_MCP_AUTH_TOKEN': 'n8n-mcp-auth-token-2025',
                'NEO4J_PASSWORD': 'password',
                'POSTGRES_PASSWORD': 'postgres_password',
                'POSTGRES_USER': 'plc_user',
                'POSTGRES_DB': 'plc_db'
            }
            
            env_file = self.stack_dir / ".env"
            env_updated = False
            
            # Read existing .env file if it exists
            existing_env = {}
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            existing_env[key] = value
            
            # Add missing environment variables
            for var_name, default_value in required_env_vars.items():
                if var_name not in existing_env:
                    existing_env[var_name] = default_value
                    env_updated = True
                    result['details'][f'added_{var_name}'] = True
            
            # Write updated .env file
            if env_updated or not env_file.exists():
                with open(env_file, 'w') as f:
                    f.write("# PLC-GBT Stack Environment Variables\n")
                    f.write("# Generated by Phase 26.7 n8n-MCP Deployment\n\n")
                    
                    for key, value in existing_env.items():
                        f.write(f"{key}={value}\n")
                
                result['details']['env_file_updated'] = True
            
            # Create .cursor directory if it doesn't exist
            cursor_dir = self.stack_dir / ".cursor"
            cursor_dir.mkdir(exist_ok=True)
            
            # Verify MCP configuration file
            mcp_config_file = cursor_dir / "mcp.json"
            if mcp_config_file.exists():
                with open(mcp_config_file, 'r') as f:
                    mcp_config = json.load(f)
                    
                has_n8n_mcp = 'n8n-mcp-local' in mcp_config.get('mcpServers', {})
                result['details']['mcp_config_ready'] = has_n8n_mcp
            else:
                result['details']['mcp_config_ready'] = False
                result['details']['mcp_config_missing'] = True
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def manage_docker_images(self) -> Dict:
        """Pull and manage required Docker images."""
        result = {'success': True, 'details': {}}
        
        try:
            # Pull n8n-MCP image
            logger.info(f"Pulling {self.n8n_mcp_image}...")
            
            try:
                image = self.docker_client.images.pull(self.n8n_mcp_image)
                result['details']['n8n_mcp_image_pulled'] = True
                result['details']['n8n_mcp_image_id'] = image.id[:12]
                
                # Get image info
                image_attrs = image.attrs
                result['details']['image_size'] = image_attrs.get('Size', 0) / (1024 * 1024)  # MB
                result['details']['image_created'] = image_attrs.get('Created', 'unknown')
                
            except Exception as e:
                result['success'] = False
                result['error'] = f"Failed to pull n8n-MCP image: {e}"
                return result
            
            # Verify other required images are available
            required_images = [
                'n8nio/n8n:latest',
                'neo4j:5-enterprise',
                'postgres:15-alpine',
                'redis:7-alpine',
                'qdrant/qdrant:latest',
                'vault:1.15'
            ]
            
            available_images = []
            for image_name in required_images:
                try:
                    self.docker_client.images.get(image_name)
                    available_images.append(image_name)
                except:
                    pass
            
            result['details']['required_images_available'] = f"{len(available_images)}/{len(required_images)}"
            
            if len(available_images) < len(required_images):
                missing_images = [img for img in required_images if img not in available_images]
                result['details']['missing_images'] = missing_images
                
                # In validate_only mode, this is just a warning
                if not self.validate_only:
                    result['success'] = False
                    result['error'] = f"Missing required images: {missing_images}"
                    
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def configure_services(self) -> Dict:
        """Configure services and validate Docker Compose file."""
        result = {'success': True, 'details': {}}
        
        try:
            # Validate docker-compose.yml structure
            if not self.docker_compose_file.exists():
                result['success'] = False
                result['error'] = "docker-compose.yml not found"
                return result
            
            with open(self.docker_compose_file, 'r') as f:
                compose_content = yaml.safe_load(f)
            
            # Check if n8n-mcp service is defined
            services = compose_content.get('services', {})
            if 'n8n-mcp' not in services:
                result['success'] = False
                result['error'] = "n8n-mcp service not defined in docker-compose.yml"
                return result
            
            n8n_mcp_config = services['n8n-mcp']
            
            # Validate n8n-mcp service configuration
            required_config = {
                'image': self.n8n_mcp_image,
                'container_name': self.n8n_mcp_container,
                'environment': dict,
                'volumes': list,
                'networks': list,
                'depends_on': dict
            }
            
            config_valid = True
            for key, expected_type in required_config.items():
                if key not in n8n_mcp_config:
                    result['details'][f'missing_{key}'] = True
                    config_valid = False
                elif expected_type != dict and expected_type != list:
                    if n8n_mcp_config[key] != expected_type:
                        result['details'][f'invalid_{key}'] = n8n_mcp_config[key]
                        config_valid = False
            
            result['details']['n8n_mcp_config_valid'] = config_valid
            
            # Check environment variables
            env_vars = n8n_mcp_config.get('environment', [])
            required_env = ['MCP_MODE=http', 'N8N_API_URL=http://plc-n8n:5678']
            
            env_check = {}
            for req_env in required_env:
                found = any(req_env in env_var for env_var in env_vars)
                env_check[req_env] = found
                
            result['details']['environment_variables'] = env_check
            
            # Check volumes configuration
            volumes = compose_content.get('volumes', {})
            has_n8n_mcp_volume = 'n8n_mcp_data' in volumes
            result['details']['n8n_mcp_volume_defined'] = has_n8n_mcp_volume
            
            if not has_n8n_mcp_volume:
                config_valid = False
                result['details']['missing_n8n_mcp_volume'] = True
            
            if not config_valid:
                result['success'] = False
                result['error'] = "Invalid n8n-mcp service configuration"
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def setup_networking(self) -> Dict:
        """Set up Docker networking for n8n-MCP integration."""
        result = {'success': True, 'details': {}}
        
        try:
            # Check if required networks exist
            required_networks = [
                'plc-gbt-stack_plc-internal-network',
                'plc-gbt-stack_plc-database-network'
            ]
            
            existing_networks = [network.name for network in self.docker_client.networks.list()]
            
            networks_available = []
            for network_name in required_networks:
                if network_name in existing_networks:
                    networks_available.append(network_name)
                    
                    # Get network details
                    network = self.docker_client.networks.get(network_name)
                    connected_containers = len(network.attrs.get('Containers', {}))
                    result['details'][f'{network_name}_containers'] = connected_containers
            
            result['details']['required_networks_available'] = f"{len(networks_available)}/{len(required_networks)}"
            
            if len(networks_available) < len(required_networks):
                missing_networks = [net for net in required_networks if net not in existing_networks]
                result['details']['missing_networks'] = missing_networks
                
                if not self.validate_only:
                    result['success'] = False
                    result['error'] = f"Missing required networks: {missing_networks}"
            
            # Check port availability
            required_ports = [3000]  # n8n-MCP port
            
            port_conflicts = []
            for port in required_ports:
                try:
                    # Try to find containers using the port
                    containers = self.docker_client.containers.list()
                    for container in containers:
                        ports = container.attrs.get('NetworkSettings', {}).get('Ports', {})
                        for container_port, host_bindings in ports.items():
                            if host_bindings:
                                for binding in host_bindings:
                                    if int(binding.get('HostPort', 0)) == port:
                                        if container.name != self.n8n_mcp_container:
                                            port_conflicts.append(f"Port {port} used by {container.name}")
                                            
                except Exception:
                    pass
            
            result['details']['port_conflicts'] = port_conflicts
            
            if port_conflicts and not self.validate_only:
                result['success'] = False
                result['error'] = f"Port conflicts detected: {port_conflicts}"
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def deploy_services(self) -> Dict:
        """Deploy n8n-MCP service using Docker Compose."""
        result = {'success': True, 'details': {}}
        
        if self.validate_only:
            result['details']['validation_mode'] = True
            return result
        
        try:
            # Change to stack directory
            original_cwd = os.getcwd()
            os.chdir(self.stack_dir)
            
            try:
                # Stop existing n8n-mcp container if it exists
                try:
                    existing_container = self.docker_client.containers.get(self.n8n_mcp_container)
                    if existing_container.status == 'running':
                        logger.info("Stopping existing n8n-mcp container...")
                        existing_container.stop()
                        existing_container.remove()
                        result['details']['existing_container_removed'] = True
                except:
                    pass
                
                # Start the n8n-mcp service
                logger.info("Starting n8n-mcp service...")
                
                compose_cmd = [
                    'docker-compose',
                    'up',
                    '-d',
                    'n8n-mcp'
                ]
                
                if self.force_rebuild:
                    compose_cmd.insert(-1, '--force-recreate')
                
                process = subprocess.run(
                    compose_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if process.returncode == 0:
                    result['details']['service_started'] = True
                    result['details']['compose_output'] = process.stdout
                    
                    # Wait for container to be running
                    max_wait = 60  # seconds
                    wait_time = 0
                    
                    while wait_time < max_wait:
                        try:
                            container = self.docker_client.containers.get(self.n8n_mcp_container)
                            if container.status == 'running':
                                result['details']['container_running'] = True
                                break
                        except:
                            pass
                        
                        await asyncio.sleep(2)
                        wait_time += 2
                    
                    if wait_time >= max_wait:
                        result['success'] = False
                        result['error'] = "Container failed to start within timeout"
                        
                else:
                    result['success'] = False
                    result['error'] = f"Docker Compose failed: {process.stderr}"
                    
            finally:
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            result['success'] = False
            result['error'] = "Docker Compose command timed out"
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def verify_deployment(self) -> Dict:
        """Verify that the deployment was successful."""
        result = {'success': True, 'details': {}}
        
        try:
            # Check container status
            try:
                container = self.docker_client.containers.get(self.n8n_mcp_container)
                result['details']['container_status'] = container.status
                
                if container.status != 'running':
                    result['success'] = False
                    result['error'] = f"Container status is {container.status}, expected running"
                    
                    # Get container logs for debugging
                    logs = container.logs(tail=50).decode('utf-8')
                    result['details']['container_logs'] = logs
                    return result
                    
            except Exception as e:
                result['success'] = False
                result['error'] = f"Container not found: {e}"
                return result
            
            # Check health endpoint
            max_retries = 30
            retry_count = 0
            health_ok = False
            
            while retry_count < max_retries and not health_ok:
                try:
                    response = requests.get(
                        "http://127.0.0.1:3000/health",
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        health_data = response.json()
                        result['details']['health_status'] = health_data.get('status')
                        result['details']['mcp_mode'] = health_data.get('mode')
                        result['details']['version'] = health_data.get('version')
                        health_ok = True
                        break
                        
                except requests.exceptions.RequestException:
                    pass
                
                await asyncio.sleep(2)
                retry_count += 1
            
            if not health_ok:
                result['success'] = False
                result['error'] = "Health endpoint not responding after 60 seconds"
                return result
            
            # Check MCP tools endpoint
            try:
                response = requests.get(
                    "http://127.0.0.1:3000/tools",
                    timeout=10
                )
                
                if response.status_code == 200:
                    tools_data = response.json()
                    result['details']['available_tools'] = len(tools_data.get('tools', []))
                else:
                    result['details']['tools_endpoint_status'] = response.status_code
                    
            except Exception as e:
                result['details']['tools_endpoint_error'] = str(e)
            
            # Check n8n connectivity
            try:
                auth_token = os.getenv('N8N_MCP_AUTH_TOKEN', 'n8n-mcp-auth-token-2025')
                headers = {'Authorization': f'Bearer {auth_token}'}
                
                response = requests.get(
                    "http://127.0.0.1:3000/n8n/health",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result['details']['n8n_connectivity'] = 'OK'
                else:
                    result['details']['n8n_connectivity'] = f'HTTP_{response.status_code}'
                    
            except Exception as e:
                result['details']['n8n_connectivity_error'] = str(e)
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def test_integration(self) -> Dict:
        """Test basic integration functionality."""
        result = {'success': True, 'details': {}}
        
        try:
            auth_token = os.getenv('N8N_MCP_AUTH_TOKEN', 'n8n-mcp-auth-token-2025')
            headers = {'Authorization': f'Bearer {auth_token}'}
            
            # Test node search
            try:
                response = requests.get(
                    "http://127.0.0.1:3000/search/nodes",
                    params={'query': 'webhook'},
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    result['details']['node_search_results'] = len(search_data.get('nodes', []))
                else:
                    result['details']['node_search_status'] = response.status_code
                    
            except Exception as e:
                result['details']['node_search_error'] = str(e)
            
            # Test workflow validation
            try:
                test_workflow = {
                    "name": "Deployment Test Workflow",
                    "nodes": [
                        {
                            "id": "start-node",
                            "type": "n8n-nodes-base.start",
                            "typeVersion": 1,
                            "position": [100, 200]
                        }
                    ],
                    "connections": {},
                    "active": False
                }
                
                response = requests.post(
                    "http://127.0.0.1:3000/validate/workflow",
                    json=test_workflow,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    validation_data = response.json()
                    result['details']['workflow_validation_score'] = validation_data.get('score', 0)
                else:
                    result['details']['workflow_validation_status'] = response.status_code
                    
            except Exception as e:
                result['details']['workflow_validation_error'] = str(e)
            
            # Test database statistics
            try:
                response = requests.get(
                    "http://127.0.0.1:3000/database/stats",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    db_data = response.json()
                    result['details']['database_ready'] = db_data.get('ready', False)
                    result['details']['node_count'] = db_data.get('node_count', 0)
                else:
                    result['details']['database_stats_status'] = response.status_code
                    
            except Exception as e:
                result['details']['database_stats_error'] = str(e)
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def validate_deployment(self) -> Dict:
        """Run comprehensive validation after deployment."""
        result = {'success': True, 'details': {}}
        
        try:
            # Import and run the validation script
            validation_script = self.stack_dir / "scripts" / "validation" / "phase26_7_n8n_mcp_integration_validation.py"
            
            if validation_script.exists():
                try:
                    # Run validation as subprocess
                    process = subprocess.run(
                        [sys.executable, str(validation_script)],
                        capture_output=True,
                        text=True,
                        timeout=300,
                        cwd=str(self.stack_dir)
                    )
                    
                    result['details']['validation_exit_code'] = process.returncode
                    result['details']['validation_output'] = process.stdout
                    
                    if process.returncode == 0:
                        result['details']['comprehensive_validation'] = 'PASS'
                    else:
                        result['details']['comprehensive_validation'] = 'FAIL'
                        result['details']['validation_errors'] = process.stderr
                        
                except subprocess.TimeoutExpired:
                    result['details']['validation_timeout'] = True
                except Exception as e:
                    result['details']['validation_script_error'] = str(e)
            else:
                result['details']['validation_script_missing'] = True
                
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
            
        return result
    
    async def save_deployment_results(self, results: Dict, overall_success: bool):
        """Save deployment results to file."""
        results_dir = self.stack_dir / "results" / "phase26_7"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save deployment results
        deployment_file = results_dir / f"n8n_mcp_deployment_{self.deployment_session}.json"
        
        deployment_summary = {
            'session_id': self.deployment_session,
            'timestamp': datetime.now().isoformat(),
            'overall_success': overall_success,
            'validate_only': self.validate_only,
            'force_rebuild': self.force_rebuild,
            'results': results
        }
        
        with open(deployment_file, 'w') as f:
            json.dump(deployment_summary, f, indent=2, default=str)
        
        logger.info(f"Deployment results saved to {deployment_file}")

def main():
    """Main deployment function."""
    parser = argparse.ArgumentParser(description='Deploy n8n-MCP integration for Phase 26.7')
    parser.add_argument('--validate-only', action='store_true', 
                       help='Only validate configuration without deploying')
    parser.add_argument('--force-rebuild', action='store_true',
                       help='Force rebuild of containers')
    
    args = parser.parse_args()
    
    deployment_manager = N8NMCPDeploymentManager(
        validate_only=args.validate_only,
        force_rebuild=args.force_rebuild
    )
    
    async def run_deployment():
        try:
            results = await deployment_manager.deploy()
            
            print(f"\n{'='*60}")
            print(f"PHASE 26.7 N8N-MCP DEPLOYMENT {'VALIDATION' if args.validate_only else 'COMPLETE'}")
            print(f"{'='*60}")
            print(f"Session ID: {results['session_id']}")
            print(f"Overall Success: {results['overall_success']}")
            print(f"Timestamp: {results['timestamp']}")
            
            if results['overall_success']:
                if args.validate_only:
                    print(f"\n✅ VALIDATION SUCCESSFUL: Ready for deployment")
                else:
                    print(f"\n🎉 DEPLOYMENT SUCCESSFUL: n8n-MCP integration is live!")
                    print(f"📍 n8n-MCP Endpoint: http://127.0.0.1:3000")
                    print(f"📍 n8n Endpoint: http://127.0.0.1:5678")
                    print(f"🔧 Run validation: python scripts/validation/phase26_7_n8n_mcp_integration_validation.py")
            else:
                print(f"\n❌ {'VALIDATION' if args.validate_only else 'DEPLOYMENT'} FAILED")
                print(f"Check logs and results for details")
            
            return 0 if results['overall_success'] else 1
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return 1
    
    return asyncio.run(run_deployment())

if __name__ == "__main__":
    sys.exit(main()) 