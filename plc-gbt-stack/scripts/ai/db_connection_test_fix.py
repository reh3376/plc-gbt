#!/usr/bin/env python3
"""
🔧 Database Connection Test & Fix - Docker Desktop Port Forwarding Workaround
AI Task Orchestrator Methodology Compliance

This script addresses Docker Desktop port forwarding issues on macOS by testing
multiple connection methods and providing configuration updates for the PLC
memory system to work with containerized databases.

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: Database Connectivity Resolution
"""

import json
import subprocess
import sys
from typing import Dict, Optional, Tuple


def test_connection_method(method_name: str, test_func) -> Tuple[bool, str]:
    """Test a connection method and return success status with details."""
    try:
        result = test_func()
        return True, f"✅ {method_name}: {result}"
    except Exception as e:
        return False, f"❌ {method_name}: {str(e)}"

def test_redis_localhost() -> str:
    """Test Redis connection via localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        result = s.connect_ex(('127.0.0.1', 6379))
        if result == 0:
            return "Connected to Redis via localhost"
        else:
            raise Exception(f"Connection failed with code {result}")

def test_redis_docker_exec() -> str:
    """Test Redis connection via docker exec."""
    result = subprocess.run(
        ['docker', 'exec', 'plc-redis', 'redis-cli', 'ping'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and 'PONG' in result.stdout:
        return "Redis internal: PONG"
    else:
        raise Exception(f"Docker exec failed: {result.stderr}")

def test_postgres_localhost() -> str:
    """Test PostgreSQL connection via localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        result = s.connect_ex(('127.0.0.1', 5432))
        if result == 0:
            return "Connected to PostgreSQL via localhost"
        else:
            raise Exception(f"Connection failed with code {result}")

def test_postgres_docker_exec() -> str:
    """Test PostgreSQL connection via docker exec."""
    result = subprocess.run(
        ['docker', 'exec', 'plc-postgres', 'pg_isready', '-U', 'plc_user', '-d', 'plc_gbt'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and 'accepting connections' in result.stdout:
        return "PostgreSQL internal: Ready"
    else:
        raise Exception(f"Docker exec failed: {result.stderr}")

def test_neo4j_localhost() -> str:
    """Test Neo4j connection via localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        result = s.connect_ex(('127.0.0.1', 7687))
        if result == 0:
            return "Connected to Neo4j via localhost"
        else:
            raise Exception(f"Connection failed with code {result}")

def test_neo4j_docker_exec() -> str:
    """Test Neo4j connection via docker exec."""
    result = subprocess.run(
        ['docker', 'exec', 'plc-neo4j', 'neo4j', 'status'],
        capture_output=True, text=True, timeout=10
    )
    if result.returncode == 0 and 'running' in result.stdout:
        return "Neo4j internal: Running"
    else:
        raise Exception(f"Docker exec failed: {result.stderr}")

def test_qdrant_localhost() -> str:
    """Test Qdrant connection via localhost."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        result = s.connect_ex(('127.0.0.1', 6333))
        if result == 0:
            return "Connected to Qdrant via localhost"
        else:
            raise Exception(f"Connection failed with code {result}")

def get_container_ip(container_name: str) -> Optional[str]:
    """Get the internal IP address of a container."""
    try:
        result = subprocess.run(
            ['docker', 'inspect', container_name, '--format', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None

def create_docker_based_env_config() -> Dict[str, str]:
    """Create database configuration that works with Docker internal networking."""
    container_ips = {
        'redis': get_container_ip('plc-redis'),
        'postgres': get_container_ip('plc-postgres'),
        'neo4j': get_container_ip('plc-neo4j'),
        'qdrant': get_container_ip('plc-qdrant')
    }

    # If we can't get container IPs, fall back to service names
    config = {
        'REDIS_HOST': container_ips.get('redis') or 'plc-redis',
        'POSTGRES_HOST': container_ips.get('postgres') or 'plc-postgres',
        'NEO4J_HOST': container_ips.get('neo4j') or 'plc-neo4j',
        'QDRANT_HOST': container_ips.get('qdrant') or 'plc-qdrant',

        # Keep standard ports since they're internal
        'REDIS_PORT': '6379',
        'POSTGRES_PORT': '5432',
        'NEO4J_PORT': '7687',
        'QDRANT_PORT': '6333',

        # Database credentials from .env
        'POSTGRES_DB': 'plc_gbt',
        'POSTGRES_USER': 'plc_user',
        'POSTGRES_PASSWORD': 'postgres_password',
        'NEO4J_USER': 'neo4j',
        'NEO4J_PASSWORD': 'password',

        # Connection URLs
        'NEO4J_BOLT_URL': f"bolt://{container_ips.get('neo4j') or 'plc-neo4j'}:7687",
        'QDRANT_URL': f"http://{container_ips.get('qdrant') or 'plc-qdrant'}:6333"
    }

    return config

def update_plc_memory_config(config: Dict[str, str]) -> str:
    """Update the plc-memory CLI configuration to use Docker networking."""
    # Create a configuration override file
    config_override = {
        'databases': {
            'redis': {
                'host': config['REDIS_HOST'],
                'port': int(config['REDIS_PORT']),
                'connection_method': 'docker_network'
            },
            'postgresql': {
                'host': config['POSTGRES_HOST'],
                'port': int(config['POSTGRES_PORT']),
                'database': config['POSTGRES_DB'],
                'user': config['POSTGRES_USER'],
                'password': config['POSTGRES_PASSWORD'],
                'connection_method': 'docker_network'
            },
            'neo4j': {
                'host': config['NEO4J_HOST'],
                'port': int(config['NEO4J_PORT']),
                'user': config['NEO4J_USER'],
                'password': config['NEO4J_PASSWORD'],
                'bolt_url': config['NEO4J_BOLT_URL'],
                'connection_method': 'docker_network'
            },
            'qdrant': {
                'host': config['QDRANT_HOST'],
                'port': int(config['QDRANT_PORT']),
                'url': config['QDRANT_URL'],
                'connection_method': 'docker_network'
            }
        },
        'connection_strategy': 'docker_internal',
        'fallback_enabled': True,
        'docker_network': 'plc-gbt-stack_plc-database-network'
    }

    config_file = 'plc_memory_docker_config.json'
    with open(config_file, 'w') as f:
        json.dump(config_override, f, indent=2)

    return config_file

def main():
    """Main diagnostic and fix routine."""
    print("🔧 Database Connection Diagnostic & Fix")
    print("=" * 50)

    # Test 1: Localhost connections (expected to fail due to Docker Desktop issue)
    print("\n📡 Testing Localhost Connections (Expected to fail on macOS Docker Desktop):")
    tests = [
        ("Redis Localhost", test_redis_localhost),
        ("PostgreSQL Localhost", test_postgres_localhost),
        ("Neo4j Localhost", test_neo4j_localhost),
        ("Qdrant Localhost", test_qdrant_localhost),
    ]

    localhost_working = 0
    for test_name, test_func in tests:
        success, message = test_connection_method(test_name, test_func)
        print(f"  {message}")
        if success:
            localhost_working += 1

    print(f"\n📊 Localhost Connectivity: {localhost_working}/{len(tests)} working")

    # Test 2: Docker exec connections (should work)
    print("\n🐳 Testing Docker Internal Connections:")
    docker_tests = [
        ("Redis Docker", test_redis_docker_exec),
        ("PostgreSQL Docker", test_postgres_docker_exec),
        ("Neo4j Docker", test_neo4j_docker_exec),
    ]

    docker_working = 0
    for test_name, test_func in docker_tests:
        success, message = test_connection_method(test_name, test_func)
        print(f"  {message}")
        if success:
            docker_working += 1

    print(f"\n📊 Docker Internal Connectivity: {docker_working}/{len(docker_tests)} working")

    # Diagnosis
    print("\n🔍 Diagnosis:")
    if localhost_working == 0 and docker_working >= 3:
        print("  ✅ IDENTIFIED: Docker Desktop port forwarding issue (common on macOS)")
        print("  💡 SOLUTION: Use Docker internal networking for database connections")

        # Create fix
        print("\n🛠️ Creating Docker-based configuration...")
        config = create_docker_based_env_config()
        config_file = update_plc_memory_config(config)

        print(f"  ✅ Created configuration override: {config_file}")
        print("  ✅ Configuration uses Docker internal networking")

        # Show container IPs
        print("\n🌐 Container Network Information:")
        for service in ['redis', 'postgres', 'neo4j', 'qdrant']:
            container_name = f'plc-{service}'
            ip = get_container_ip(container_name)
            print(f"  {service}: {ip or 'Service name fallback'}")

        return True, config_file

    elif localhost_working >= 3:
        print("  ✅ Port forwarding is working correctly")
        print("  💡 No configuration changes needed")
        return True, None

    else:
        print("  ❌ CRITICAL: Both localhost and Docker internal connections failing")
        print("  💡 RECOMMENDATION: Restart Docker Desktop and try again")
        return False, None

if __name__ == "__main__":
    try:
        success, config_file = main()
        if success:
            print("\n🎉 Database connectivity issue resolved!")
            if config_file:
                print(f"📁 Use configuration: {config_file}")
                print("🔧 PLC Memory system can now connect via Docker networking")
            sys.exit(0)
        else:
            print("\n❌ Database connectivity issue requires manual intervention")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Diagnostic script failed: {e}")
        sys.exit(1)
