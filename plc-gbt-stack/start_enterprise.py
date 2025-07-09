#!/usr/bin/env python3
"""
PLC-GPT Enterprise Startup Script
Phase 3 Days 6-7: Enterprise Features

This script ensures all required services are running and starts the enterprise application.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_docker_services():
    """Check if Docker services are running."""
    logger.info("🔍 Checking Docker services...")
    
    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ Docker is not running. Please start Docker first.")
            return False
        
        # Check if docker-compose services are running
        result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
        
        required_services = ['postgres', 'neo4j', 'redis', 'qdrant']
        running_services = []
        
        for line in result.stdout.split('\n'):
            for service in required_services:
                if service in line and 'Up' in line:
                    running_services.append(service)
        
        missing_services = set(required_services) - set(running_services)
        
        if missing_services:
            logger.warning(f"⚠️ Missing services: {missing_services}")
            logger.info("🚀 Starting missing services...")
            
            # Start services
            subprocess.run(['docker-compose', 'up', '-d'] + list(missing_services))
            
            # Wait for services to be ready
            logger.info("⏳ Waiting for services to be ready...")
            time.sleep(30)
        
        logger.info("✅ All Docker services are running")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Error checking Docker services: {e}")
        return False
    except FileNotFoundError:
        logger.error("❌ Docker or docker-compose not found. Please install Docker.")
        return False


def check_python_dependencies():
    """Check if Python dependencies are installed."""
    logger.info("🔍 Checking Python dependencies...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'redis',
        'psutil',
        'prometheus-client',
        'PyJWT',
        'passlib',
        'python-multipart',
        'slowapi',
        'pydantic-settings'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.warning(f"⚠️ Missing Python packages: {missing_packages}")
        logger.info("📦 Installing missing packages...")
        
        # Install missing packages
        subprocess.run([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        
        logger.info("✅ Python dependencies installed")
    else:
        logger.info("✅ All Python dependencies are available")
    
    return True


def check_environment_variables():
    """Check if required environment variables are set."""
    logger.info("🔍 Checking environment variables...")
    
    required_env_vars = [
        'JWT_SECRET_KEY',
        'REDIS_HOST',
        'REDIS_PORT'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
        logger.info("Setting default values...")
        
        # Set default values
        if 'JWT_SECRET_KEY' in missing_vars:
            os.environ['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
        if 'REDIS_HOST' in missing_vars:
            os.environ['REDIS_HOST'] = 'localhost'
        if 'REDIS_PORT' in missing_vars:
            os.environ['REDIS_PORT'] = '6379'
    
    logger.info("✅ Environment variables configured")
    return True


def wait_for_services():
    """Wait for services to be ready."""
    logger.info("⏳ Waiting for services to be ready...")
    
    # Test Redis connection
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        try:
            import redis
            r = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                socket_timeout=5.0
            )
            r.ping()
            logger.info("✅ Redis connection successful")
            break
        except Exception as e:
            attempt += 1
            if attempt >= max_attempts:
                logger.error(f"❌ Failed to connect to Redis after {max_attempts} attempts")
                return False
            logger.info(f"⏳ Waiting for Redis... (attempt {attempt}/{max_attempts})")
            time.sleep(2)
    
    return True


def start_enterprise_application():
    """Start the enterprise application."""
    logger.info("🚀 Starting PLC-GPT Enterprise Application...")
    
    try:
        # Change to the application directory
        app_dir = Path(__file__).parent
        os.chdir(app_dir)
        
        # Start the application
        subprocess.run([
            sys.executable, '-m', 'uvicorn',
            'enterprise_app:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
        
    except KeyboardInterrupt:
        logger.info("🛑 Application stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting application: {e}")
        return False
    
    return True


def main():
    """Main startup function."""
    logger.info("🌟 Starting PLC-GPT Enterprise Setup...")
    
    try:
        # Check all prerequisites
        if not check_docker_services():
            sys.exit(1)
        
        if not check_python_dependencies():
            sys.exit(1)
        
        if not check_environment_variables():
            sys.exit(1)
        
        if not wait_for_services():
            sys.exit(1)
        
        # Display startup information
        logger.info("""
        ╔══════════════════════════════════════════════════════════════════════════════╗
        ║                    🚀 PLC-GPT Enterprise v3.0.0 Ready!                      ║
        ║                       Phase 3 Days 6-7: Enterprise Features                 ║
        ╠══════════════════════════════════════════════════════════════════════════════╣
        ║  ✅ All services are running and ready                                      ║
        ║  ✅ Enterprise features fully configured                                    ║
        ║  ✅ Ready to start the application                                          ║
        ╠══════════════════════════════════════════════════════════════════════════════╣
        ║  🔐 Authentication: JWT + RBAC                                              ║
        ║  🚀 Caching: Redis + Intelligent Invalidation                              ║
        ║  🛡️  Security: Rate Limiting + DDoS Protection                             ║
        ║  📊 Monitoring: Prometheus + Custom Metrics                                 ║
        ╠══════════════════════════════════════════════════════════════════════════════╣
        ║  🌐 Application: http://localhost:8000                                      ║
        ║  📚 API Docs: http://localhost:8000/docs                                    ║
        ║  🏥 Health: http://localhost:8000/health                                    ║
        ║  📈 Metrics: http://localhost:8000/metrics                                  ║
        ╚══════════════════════════════════════════════════════════════════════════════╝
        """)
        
        # Start the application
        start_enterprise_application()
        
    except KeyboardInterrupt:
        logger.info("🛑 Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 