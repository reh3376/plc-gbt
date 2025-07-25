#!/usr/bin/env python3
"""
🤖 PLC Memory CLI - Docker-Aware Version for Port Forwarding Issues
AI Task Orchestrator Methodology Compliance

This is a Docker-aware version of the PLC Memory CLI that works around Docker Desktop 
port forwarding issues on macOS by using Docker internal networking for database connections.

Author: AI Task Orchestrator
Created: 2025-01-17
Phase: Database Connectivity Resolution
"""

import os
import sys
import json
import subprocess
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

# Override environment variables for Docker networking
def setup_docker_environment():
    """Setup environment variables for Docker internal networking"""
    # Load the Docker configuration we created
    config_file = Path(__file__).parent / "plc_memory_docker_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            docker_config = json.load(f)
        
        # Override environment variables with Docker configuration
        db_configs = docker_config.get('databases', {})
        
        if 'redis' in db_configs:
            os.environ['REDIS_HOST'] = db_configs['redis']['host']
            os.environ['REDIS_PORT'] = str(db_configs['redis']['port'])
        
        if 'postgresql' in db_configs:
            pg_config = db_configs['postgresql']
            os.environ['POSTGRES_HOST'] = pg_config['host']
            os.environ['POSTGRES_PORT'] = str(pg_config['port'])
            os.environ['POSTGRES_DB'] = pg_config['database']
            os.environ['POSTGRES_USER'] = pg_config['user']
            os.environ['POSTGRES_PASSWORD'] = pg_config['password']
        
        if 'neo4j' in db_configs:
            neo4j_config = db_configs['neo4j']
            os.environ['NEO4J_HOST'] = neo4j_config['host']
            os.environ['NEO4J_PORT'] = str(neo4j_config['port'])
            os.environ['NEO4J_USER'] = neo4j_config['user']
            os.environ['NEO4J_PASSWORD'] = neo4j_config['password']
            os.environ['NEO4J_BOLT_URL'] = neo4j_config['bolt_url']
        
        if 'qdrant' in db_configs:
            qdrant_config = db_configs['qdrant']
            os.environ['QDRANT_HOST'] = qdrant_config['host']
            os.environ['QDRANT_PORT'] = str(qdrant_config['port'])
        
        print("🐳 Docker networking configuration loaded")
        print(f"   Redis: {os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}")
        print(f"   PostgreSQL: {os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}")
        print(f"   Neo4j: {os.environ.get('NEO4J_HOST')}:{os.environ.get('NEO4J_PORT')}")
        print(f"   Qdrant: {os.environ.get('QDRANT_HOST')}:{os.environ.get('QDRANT_PORT')}")
        
        return True
    else:
        print("❌ Docker configuration file not found!")
        print("Run db_connection_test_fix.py first to generate the configuration.")
        return False

# Setup Docker environment before importing other modules
if not setup_docker_environment():
    sys.exit(1)

# Now import the original CLI modules
from database_manager import DatabaseManager, DatabaseType, MemoryTier
from memory_coordinator import MemoryCoordinator, MemoryRequest, QueryStrategy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
db_manager = None
coordinator = None

async def init_system():
    """Initialize the memory management system with Docker networking"""
    global db_manager, coordinator
    
    if db_manager is None:
        print("🔗 Initializing database connections with Docker networking...")
        db_manager = DatabaseManager()
        coordinator = MemoryCoordinator(db_manager)
        await db_manager.initialize_all_connections()
    
    return db_manager, coordinator

def docker_status():
    """Show Docker-aware system status"""
    async def _status():
        try:
            db_mgr, coord = await init_system()
            
            print("📊 PLC Memory System Status (Docker Mode)")
            print("=" * 50)
            print(f"🚀 Session: {coord.session_id}")
            print(f"⏱️  Uptime: {(datetime.now() - coord.start_time).total_seconds():.1f}s")
            print(f"🔢 Total operations: {coord.total_operations}")
            print(f"📝 Queries executed: {coord.queries_executed}")
            print(f"📁 Files ingested: {coord.files_ingested}")
            print(f"💾 Cache hit rate: {coord.get_cache_hit_rate():.1f}%")
            print(f"⚡ Avg query time: {coord.get_avg_query_time():.1f}ms")
            
            # Database health check
            print("\n🏥 Database Health:")
            health_results = await db_mgr.health_check()
            for db_type, health in health_results.items():
                status_icon = "✅" if health.get("healthy", False) else "❌"
                db_name = db_type.value if hasattr(db_type, 'value') else str(db_type)
                
                if health.get("healthy", False):
                    print(f"  {status_icon} {db_name}: healthy")
                else:
                    error_msg = health.get("error", "Unknown error")
                    print(f"  {status_icon} {db_name}: {error_msg}")
            
            await db_mgr.close_all_connections()
            
        except Exception as e:
            print(f"❌ Status check failed: {str(e)}")
            return 1
        
        return 0
    
    import asyncio
    return asyncio.run(_status())

def docker_ingest(file_path):
    """Ingest file with Docker networking"""
    async def _ingest():
        try:
            db_mgr, coord = await init_system()
            
            print(f"🔄 Starting ingestion with Docker networking")
            print(f"📁 Target file: {file_path}")
            
            # Use the existing ingestion pipeline
            from file_processors import FileProcessorOrchestrator
            from codebase_analyzer import AnalysisDepth
            
            processor = FileProcessorOrchestrator(db_mgr)
            
            # Simple file ingestion
            if os.path.isfile(file_path):
                print(f"📄 Processing file: {file_path}")
                result = await processor.process_file(
                    file_path, 
                    analysis_depth=AnalysisDepth.STRUCTURAL
                )
                print(f"✅ File processed successfully")
                
                # Store in memory system
                memory_request = MemoryRequest(
                    content_type="file_analysis",
                    content=result,
                    metadata={"source_file": file_path},
                    tier_hint=MemoryTier.MEDIUM_TERM
                )
                
                await coord.store_memory(memory_request)
                print(f"✅ Data stored in memory system")
                
            else:
                print(f"❌ File not found: {file_path}")
                return 1
            
            await db_mgr.close_all_connections()
            
        except Exception as e:
            print(f"❌ Ingestion failed: {str(e)}")
            return 1
        
        return 0
    
    import asyncio
    return asyncio.run(_ingest())

def docker_test():
    """Test Docker database connectivity"""
    async def _test():
        try:
            print("🧪 Testing Docker database connectivity...")
            
            db_mgr, coord = await init_system()
            
            print("\n🔍 Connection Test Results:")
            
            # Test each database type
            for db_type in [DatabaseType.REDIS, DatabaseType.POSTGRESQL, 
                           DatabaseType.NEO4J, DatabaseType.QDRANT]:
                try:
                    connection = db_mgr.connections.get(db_type)
                    if connection:
                        # Basic connectivity test
                        if db_type == DatabaseType.REDIS:
                            # Redis ping test
                            await db_mgr._test_redis_connection()
                            print(f"  ✅ Redis: Connected successfully")
                        elif db_type == DatabaseType.POSTGRESQL:
                            # PostgreSQL query test
                            await db_mgr._test_postgresql_connection()
                            print(f"  ✅ PostgreSQL: Connected successfully")
                        elif db_type == DatabaseType.NEO4J:
                            # Neo4j session test
                            await db_mgr._test_neo4j_connection()
                            print(f"  ✅ Neo4j: Connected successfully")
                        elif db_type == DatabaseType.QDRANT:
                            # Qdrant collection test
                            await db_mgr._test_qdrant_connection()
                            print(f"  ✅ Qdrant: Connected successfully")
                    else:
                        print(f"  ❌ {db_type.value}: No connection established")
                        
                except Exception as e:
                    print(f"  ❌ {db_type.value}: Connection failed - {str(e)}")
            
            await db_mgr.close_all_connections()
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return 1
        
        return 0
    
    import asyncio
    return asyncio.run(_test())

def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("🤖 PLC Memory CLI - Docker Mode")
        print("=" * 40)
        print("Commands:")
        print("  status                  - Show system status")
        print("  test                    - Test database connectivity")
        print("  ingest <file>          - Ingest a file into memory system")
        print("")
        print("Examples:")
        print("  python3 plc_memory_cli_docker.py status")
        print("  python3 plc_memory_cli_docker.py test")
        print("  python3 plc_memory_cli_docker.py ingest typescript_docs_ingestion_package_typescript_docs_261f5f59.json")
        return 1
    
    command = sys.argv[1]
    
    if command == "status":
        return docker_status()
    elif command == "test":
        return docker_test()
    elif command == "ingest":
        if len(sys.argv) < 3:
            print("❌ Error: ingest command requires a file path")
            print("Usage: python3 plc_memory_cli_docker.py ingest <file_path>")
            return 1
        file_path = sys.argv[2]
        return docker_ingest(file_path)
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: status, test, ingest")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 