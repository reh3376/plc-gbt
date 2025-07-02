#!/usr/bin/env python3
"""
Master Initialization Script
Phase 3: Complete System Setup
Version: 1.0.0

This script orchestrates the complete initialization of the PLC-GPT stack:
1. Neo4j schema setup
2. Qdrant vector store setup
3. ETL integration validation
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, Any, List

import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class SystemInitializer:
    """Orchestrates complete system initialization."""
    
    def __init__(self):
        """Initialize the system initializer."""
        self.script_dir = Path(__file__).parent
        self.results = {
            'neo4j': {'status': 'pending', 'details': {}},
            'qdrant': {'status': 'pending', 'details': {}},
            'etl': {'status': 'pending', 'details': {}},
            'overall': 'success'
        }
        
    def check_environment(self) -> Dict[str, bool]:
        """
        Check environment variables and dependencies.
        
        Returns:
            Environment check results
        """
        logger.info("Checking environment...")
        
        checks = {
            'neo4j_configured': False,
            'qdrant_configured': False,
            'openai_configured': False,
            'docker_running': False
        }
        
        # Check Neo4j configuration
        if os.getenv('NEO4J_URI') or os.path.exists('/.dockerenv'):
            checks['neo4j_configured'] = True
            
        # Check Qdrant configuration  
        if os.getenv('QDRANT_HOST') or os.path.exists('/.dockerenv'):
            checks['qdrant_configured'] = True
            
        # Check OpenAI configuration
        if os.getenv('OPENAI_API_KEY'):
            checks['openai_configured'] = True
            
        # Check if Docker is running
        try:
            result = subprocess.run(
                ['docker', 'info'],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                checks['docker_running'] = True
        except FileNotFoundError:
            pass
            
        return checks
        
    def wait_for_service(self, service_name: str, check_command: List[str], max_attempts: int = 30) -> bool:
        """
        Wait for a service to be ready.
        
        Args:
            service_name: Name of the service
            check_command: Command to check if service is ready
            max_attempts: Maximum number of attempts
            
        Returns:
            True if service is ready, False otherwise
        """
        logger.info(f"Waiting for {service_name} to be ready...")
        
        for attempt in range(max_attempts):
            try:
                result = subprocess.run(
                    check_command,
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0:
                    logger.info(f"{service_name} is ready!")
                    return True
            except Exception:
                pass
                
            if attempt < max_attempts - 1:
                time.sleep(2)
                
        logger.error(f"{service_name} failed to start after {max_attempts} attempts")
        return False
        
    def run_script(self, script_path: Path, description: str) -> Dict[str, Any]:
        """
        Run a Python script and capture results.
        
        Args:
            script_path: Path to the script
            description: Description of what the script does
            
        Returns:
            Execution results
        """
        logger.info(f"Running: {description}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                env={**os.environ}
            )
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output': result.stdout,
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'output': result.stdout,
                    'error': result.stderr
                }
                
        except Exception as e:
            return {
                'success': False,
                'output': None,
                'error': str(e)
            }
            
    def initialize_neo4j(self):
        """Initialize Neo4j schema."""
        logger.info("Initializing Neo4j...")
        
        # Wait for Neo4j to be ready
        if self.wait_for_service(
            "Neo4j",
            ["docker", "exec", "plc-gpt-stack-neo4j-1", "cypher-shell", "-u", "neo4j", "-p", "your-password-here", "RETURN 1"],
            max_attempts=30
        ):
            # Run schema initialization
            script_path = self.script_dir / "neo4j" / "init_neo4j_schema.py"
            result = self.run_script(script_path, "Neo4j schema initialization")
            
            self.results['neo4j']['status'] = 'success' if result['success'] else 'failed'
            self.results['neo4j']['details'] = result
            
            if not result['success']:
                self.results['overall'] = 'failed'
                logger.error("Neo4j initialization failed", error=result['error'])
        else:
            self.results['neo4j']['status'] = 'failed'
            self.results['neo4j']['details'] = {'error': 'Neo4j service not ready'}
            self.results['overall'] = 'failed'
            
    def initialize_qdrant(self):
        """Initialize Qdrant vector store."""
        logger.info("Initializing Qdrant...")
        
        # Wait for Qdrant to be ready
        if self.wait_for_service(
            "Qdrant",
            ["curl", "-s", "http://localhost:6333/collections"],
            max_attempts=30
        ):
            # Run vector store initialization
            script_path = self.script_dir / "vector" / "init_vector_store.py"
            result = self.run_script(script_path, "Qdrant vector store initialization")
            
            self.results['qdrant']['status'] = 'success' if result['success'] else 'failed'
            self.results['qdrant']['details'] = result
            
            if not result['success']:
                self.results['overall'] = 'failed'
                logger.error("Qdrant initialization failed", error=result['error'])
        else:
            self.results['qdrant']['status'] = 'failed'
            self.results['qdrant']['details'] = {'error': 'Qdrant service not ready'}
            self.results['overall'] = 'failed'
            
    def test_etl_integration(self):
        """Test ETL integration."""
        logger.info("Testing ETL integration...")
        
        # Only run if both Neo4j and Qdrant are successful
        if (self.results['neo4j']['status'] == 'success' and 
            self.results['qdrant']['status'] == 'success'):
            
            script_path = self.script_dir / "etl" / "etl_integration.py"
            result = self.run_script(script_path, "ETL integration test")
            
            self.results['etl']['status'] = 'success' if result['success'] else 'failed'
            self.results['etl']['details'] = result
            
            if not result['success']:
                self.results['overall'] = 'partial'
                logger.warning("ETL integration test failed", error=result['error'])
        else:
            self.results['etl']['status'] = 'skipped'
            self.results['etl']['details'] = {'error': 'Prerequisites not met'}
            
    def print_summary(self):
        """Print initialization summary."""
        print("\n" + "="*70)
        print("PLC-GPT SYSTEM INITIALIZATION SUMMARY")
        print("="*70)
        
        # Component status
        print("\nComponent Status:")
        components = [
            ("Neo4j Schema", self.results['neo4j']['status']),
            ("Qdrant Vector Store", self.results['qdrant']['status']),
            ("ETL Integration", self.results['etl']['status'])
        ]
        
        for component, status in components:
            icon = {
                'success': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'pending': '⏳'
            }.get(status, '❓')
            print(f"  {icon} {component}: {status.upper()}")
            
        # Overall status
        print(f"\nOverall Status: {self.results['overall'].upper()}")
        
        # Next steps
        print("\n" + "-"*70)
        print("NEXT STEPS:")
        
        if self.results['overall'] == 'success':
            print("\n✅ All components initialized successfully!")
            print("\nYou can now:")
            print("  1. Process L5X files: docker exec -it plc-gpt-stack-gateway-1 python -m workers.etl_worker")
            print("  2. Query Neo4j: http://localhost:7474 (neo4j/your-password-here)")
            print("  3. Access Qdrant: http://localhost:6333/dashboard")
            print("  4. Continue with Day 2 tasks from the implementation plan")
            
        elif self.results['overall'] == 'partial':
            print("\n⚠️  System partially initialized")
            print("\nRecommended actions:")
            if self.results['neo4j']['status'] != 'success':
                print("  - Fix Neo4j initialization issues")
            if self.results['qdrant']['status'] != 'success':
                print("  - Fix Qdrant initialization issues")
            if self.results['etl']['status'] != 'success':
                print("  - Review ETL integration logs")
                
        else:
            print("\n❌ Initialization failed")
            print("\nTroubleshooting:")
            print("  1. Ensure Docker services are running: docker-compose up -d")
            print("  2. Check service logs: docker-compose logs [service-name]")
            print("  3. Verify environment variables are set correctly")
            print("  4. Review error details above")
            
        # Environment reminders
        env_checks = self.check_environment()
        if not env_checks['openai_configured']:
            print("\n⚠️  OpenAI API key not configured - embeddings will use random vectors")
            print("    Set OPENAI_API_KEY environment variable for real embeddings")


def main():
    """Main execution function."""
    print("🚀 Starting PLC-GPT System Initialization...")
    print("This will set up Neo4j, Qdrant, and test ETL integration.\n")
    
    initializer = SystemInitializer()
    
    # Check environment
    env_checks = initializer.check_environment()
    print("Environment Checks:")
    for check, status in env_checks.items():
        print(f"  - {check}: {'✅' if status else '❌'}")
    
    if not env_checks['docker_running']:
        print("\n❌ Docker is not running!")
        print("Please start Docker and run: docker-compose up -d")
        sys.exit(1)
        
    print("\nStarting initialization sequence...\n")
    
    try:
        # Initialize components in order
        initializer.initialize_neo4j()
        initializer.initialize_qdrant()
        initializer.test_etl_integration()
        
        # Print summary
        initializer.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Initialization interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error("Unexpected error during initialization", error=str(e))
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main() 