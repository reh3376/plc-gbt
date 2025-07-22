#!/usr/bin/env python3
"""
CLI-to-API Bridge Startup Script
Initializes and starts the CLI-to-API bridge server for fine-tuned LLM integration

This script:
1. Validates the environment and dependencies
2. Starts the FastAPI server
3. Performs health checks
4. Provides startup diagnostics

Author: AI Task Orchestrator
Date: January 22, 2025
"""

import asyncio
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CLIBridgeStartup:
    """CLI-to-API Bridge startup manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.bridge_host = "127.0.0.1"
        self.bridge_port = 8080
        self.startup_timeout = 30
        
    def validate_environment(self) -> bool:
        """Validate environment and dependencies"""
        logger.info("🔍 Validating environment...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("❌ Python 3.8+ required")
            return False
        logger.info(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check required packages
        required_packages = ['fastapi', 'uvicorn', 'requests', 'pydantic']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"✅ {package} available")
            except ImportError:
                missing_packages.append(package)
                logger.error(f"❌ {package} not found")
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            logger.info("Install with: pip install fastapi uvicorn requests pydantic")
            return False
        
        # Check project structure
        cli_bridge_file = self.project_root / "api" / "cli_api_bridge.py"
        if not cli_bridge_file.exists():
            logger.error(f"❌ CLI bridge file not found: {cli_bridge_file}")
            return False
        logger.info("✅ CLI bridge file found")
        
        # Check CLI availability (optional - will be tested by bridge)
        cli_file = self.project_root / "cli" / "plc_control_loop_cli.py"
        if cli_file.exists():
            logger.info("✅ PLC-CL CLI found")
        else:
            logger.warning("⚠️  PLC-CL CLI not found (will affect functionality)")
        
        return True
    
    def check_port_availability(self) -> bool:
        """Check if the bridge port is available"""
        import socket
        
        logger.info(f"🔍 Checking port {self.bridge_port} availability...")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((self.bridge_host, self.bridge_port))
                if result == 0:
                    logger.error(f"❌ Port {self.bridge_port} is already in use")
                    return False
                else:
                    logger.info(f"✅ Port {self.bridge_port} is available")
                    return True
        except Exception as e:
            logger.error(f"❌ Error checking port: {e}")
            return False
    
    def start_bridge_server(self) -> subprocess.Popen:
        """Start the CLI bridge server"""
        logger.info("🚀 Starting CLI-to-API Bridge server...")
        
        # Prepare command
        bridge_file = self.project_root / "api" / "cli_api_bridge.py"
        cmd = [
            sys.executable, str(bridge_file)
        ]
        
        # Set environment
        env = os.environ.copy()
        env['PYTHONPATH'] = f"{self.project_root}:{env.get('PYTHONPATH', '')}"
        
        # Start process
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                cwd=str(self.project_root)
            )
            
            logger.info(f"✅ Bridge server started with PID {process.pid}")
            logger.info(f"📍 Server URL: http://{self.bridge_host}:{self.bridge_port}")
            logger.info(f"📖 API Documentation: http://{self.bridge_host}:{self.bridge_port}/docs")
            
            return process
            
        except Exception as e:
            logger.error(f"❌ Failed to start bridge server: {e}")
            raise
    
    def wait_for_server_ready(self) -> bool:
        """Wait for server to be ready"""
        import requests
        
        logger.info("⏳ Waiting for server to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < self.startup_timeout:
            try:
                response = requests.get(
                    f"http://{self.bridge_host}:{self.bridge_port}/api/v1/health",
                    timeout=2
                )
                
                if response.status_code == 200:
                    health_data = response.json()
                    if health_data.get("status") == "healthy":
                        logger.info("✅ Server is ready!")
                        return True
                        
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        logger.error(f"❌ Server not ready after {self.startup_timeout} seconds")
        return False
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check"""
        import requests
        
        logger.info("🏥 Running health check...")
        
        try:
            # Basic health check
            health_response = requests.get(
                f"http://{self.bridge_host}:{self.bridge_port}/api/v1/health",
                timeout=5
            )
            health_data = health_response.json()
            
            # Capabilities check
            cap_response = requests.get(
                f"http://{self.bridge_host}:{self.bridge_port}/api/v1/capabilities",
                timeout=5
            )
            cap_data = cap_response.json()
            
            # Count endpoints
            endpoint_count = sum(len(endpoints) for endpoints in cap_data["endpoints"].values())
            
            # Simple command test
            test_response = requests.post(
                f"http://{self.bridge_host}:{self.bridge_port}/api/v1/cli/execute",
                json={"command": "plc-cl", "args": ["--version"], "timeout": 10},
                timeout=15
            )
            
            health_summary = {
                "server_status": health_data.get("status"),
                "server_version": health_data.get("version"),
                "endpoint_count": endpoint_count,
                "command_categories": list(cap_data["endpoints"].keys()),
                "test_command_success": test_response.status_code == 200,
                "ready": True
            }
            
            logger.info("✅ Health check completed successfully")
            logger.info(f"   Status: {health_summary['server_status']}")
            logger.info(f"   Version: {health_summary['server_version']}")
            logger.info(f"   Endpoints: {health_summary['endpoint_count']}")
            logger.info(f"   Categories: {len(health_summary['command_categories'])}")
            
            return health_summary
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return {"ready": False, "error": str(e)}
    
    def display_usage_examples(self):
        """Display usage examples for the API bridge"""
        logger.info("\n" + "=" * 60)
        logger.info("🎯 CLI-TO-API BRIDGE READY FOR LLM INTEGRATION")
        logger.info("=" * 60)
        
        logger.info("The fine-tuned LLM can now use these endpoints:")
        logger.info("")
        
        examples = [
            {
                "description": "Check system status",
                "method": "GET",
                "endpoint": "/api/v1/cli/system/status"
            },
            {
                "description": "List control schemas",
                "method": "POST", 
                "endpoint": "/api/v1/cli/schema/list",
                "payload": "{}"
            },
            {
                "description": "Connect to PLC",
                "method": "POST",
                "endpoint": "/api/v1/cli/plc/connect",
                "payload": '{"host": "192.168.1.100", "slot": 0}'
            },
            {
                "description": "Query memory system",
                "method": "POST",
                "endpoint": "/api/v1/cli/memory/query", 
                "payload": '{"query": "PID tuning", "limit": 10}'
            },
            {
                "description": "Execute any CLI command",
                "method": "POST",
                "endpoint": "/api/v1/cli/execute",
                "payload": '{"command": "plc-cl", "args": ["status"]}'
            }
        ]
        
        for example in examples:
            logger.info(f"📌 {example['description']}:")
            logger.info(f"   {example['method']} http://127.0.0.1:8080{example['endpoint']}")
            if example.get('payload'):
                logger.info(f"   Payload: {example['payload']}")
            logger.info("")
        
        logger.info("🔗 For complete API documentation:")
        logger.info(f"   http://127.0.0.1:8080/docs")
        logger.info("")
        
        logger.info("🤖 Integration with fine-tuned LLM:")
        logger.info("   Model ID: ft:gpt-4o:industrial-control:20250117")
        logger.info("   Training data: 109+ industrial control Q&A pairs")
        logger.info("   New training data: API integration examples")
        logger.info("")
        
        logger.info("✨ Benefits over MCP approach:")
        logger.info("   ✅ No connection issues")
        logger.info("   ✅ Standard HTTP/REST interface")
        logger.info("   ✅ Complete CLI functionality")
        logger.info("   ✅ Production-ready reliability")
    
    def run_startup_sequence(self) -> bool:
        """Run complete startup sequence"""
        logger.info("🚀 CLI-to-API Bridge Startup Sequence")
        logger.info("Alternative to MCP for Fine-tuned LLM Integration")
        logger.info("=" * 60)
        
        # Step 1: Validate environment
        if not self.validate_environment():
            logger.error("❌ Environment validation failed")
            return False
        
        # Step 2: Check port availability
        if not self.check_port_availability():
            logger.error("❌ Port check failed")
            return False
        
        # Step 3: Start server
        try:
            process = self.start_bridge_server()
        except Exception as e:
            logger.error(f"❌ Failed to start server: {e}")
            return False
        
        # Step 4: Wait for ready
        if not self.wait_for_server_ready():
            logger.error("❌ Server startup failed")
            try:
                process.terminate()
            except:
                pass
            return False
        
        # Step 5: Health check
        health_status = self.run_health_check()
        if not health_status.get("ready", False):
            logger.error("❌ Health check failed")
            try:
                process.terminate()
            except:
                pass
            return False
        
        # Step 6: Display usage
        self.display_usage_examples()
        
        logger.info("🎉 CLI-to-API Bridge is ready for fine-tuned LLM integration!")
        logger.info("Press Ctrl+C to stop the server")
        
        # Keep server running
        try:
            while True:
                time.sleep(1)
                if process.poll() is not None:
                    logger.error("❌ Server process terminated unexpectedly")
                    return False
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping server...")
            process.terminate()
            process.wait()
            logger.info("✅ Server stopped successfully")
            return True

def main():
    """Main entry point"""
    startup_manager = CLIBridgeStartup()
    
    try:
        success = startup_manager.run_startup_sequence()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 