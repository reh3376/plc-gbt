#!/usr/bin/env python3

"""
🤖 Phase 26: Database Namespace Isolation Implementation

AI Task Orchestrator Implementation following Phase 0B specifications from n8n-roadmap.
Creates isolated database namespaces for n8n integration with plc-gbt ecosystem.

Implements isolation for:
- PostgreSQL: Schema isolation (n8n schema)
- Neo4j: Database isolation (n8n database) 
- Redis: Database separation (DB 2 for BullMQ)
- Qdrant: Collection isolation (n8n_memory collection)

Author: AI Task Orchestrator
Created: June 19, 2025
Phase: 26.1.2 - Database Namespace Isolation Implementation
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import asyncpg
import redis
import requests
from neo4j import AsyncGraphDatabase
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Phase26NamespaceIsolation:
    """
    🎯 Phase 26 Database Namespace Isolation Implementation
    
    Following AI Task Orchestrator methodology for systematic database isolation
    to ensure n8n operates in completely isolated namespace without conflicts.
    """
    
    def __init__(self):
        """Initialize the namespace isolation system with database connections."""
        self.session_id = f"namespace_isolation_{int(time.time())}"
        self.start_time = datetime.now()
        
        # Database configuration from environment
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'database': os.getenv('POSTGRES_DB', 'plc_metadata'),
            'user': os.getenv('POSTGRES_USER', 'plc_user'),
            'password': os.getenv('POSTGRES_PASSWORD', 'your-postgres-password')
        }
        
        self.neo4j_config = {
            'uri': f"bolt://{os.getenv('NEO4J_HOST', 'localhost')}:{os.getenv('NEO4J_PORT', 7687)}",
            'user': os.getenv('NEO4J_USER', 'neo4j'),
            'password': os.getenv('NEO4J_PASSWORD', 'your-secure-neo4j-password')
        }
        
        self.redis_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'password': os.getenv('REDIS_PASSWORD', None)
        }
        
        self.qdrant_config = {
            'host': os.getenv('QDRANT_HOST', 'localhost'),
            'port': int(os.getenv('QDRANT_PORT', 6333))
        }
        
        self.results = {
            'session_id': self.session_id,
            'start_time': self.start_time.isoformat(),
            'isolation_results': {},
            'validation_results': {},
            'errors': []
        }
    
    async def implement_postgresql_schema_isolation(self) -> bool:
        """
        🗃️ Task 26.1.2.1: PostgreSQL Schema Isolation
        
        Creates isolated n8n schema in existing PostgreSQL database.
        Command: CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION postgres;
        """
        logger.info("🗃️ Implementing PostgreSQL schema isolation...")
        
        try:
            # Connect to PostgreSQL
            conn = await asyncpg.connect(
                host=self.postgres_config['host'],
                port=self.postgres_config['port'],
                database=self.postgres_config['database'],
                user=self.postgres_config['user'],
                password=self.postgres_config['password']
            )
            
            # Create n8n schema
            schema_sql = "CREATE SCHEMA IF NOT EXISTS n8n AUTHORIZATION postgres;"
            await conn.execute(schema_sql)
            
            # Verify schema creation
            verify_sql = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'n8n';"
            result = await conn.fetchrow(verify_sql)
            
            # Grant permissions
            permissions_sql = [
                "GRANT USAGE ON SCHEMA n8n TO postgres;",
                "GRANT CREATE ON SCHEMA n8n TO postgres;",
                "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA n8n TO postgres;",
                "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA n8n TO postgres;",
                "ALTER DEFAULT PRIVILEGES IN SCHEMA n8n GRANT ALL ON TABLES TO postgres;",
                "ALTER DEFAULT PRIVILEGES IN SCHEMA n8n GRANT ALL ON SEQUENCES TO postgres;"
            ]
            
            for sql in permissions_sql:
                await conn.execute(sql)
            
            await conn.close()
            
            success = result is not None
            self.results['isolation_results']['postgresql'] = {
                'status': 'SUCCESS' if success else 'FAILED',
                'schema_created': success,
                'schema_name': 'n8n',
                'permissions_granted': success,
                'isolation_method': 'Schema isolation'
            }
            
            if success:
                logger.info("✅ PostgreSQL schema isolation completed successfully")
            else:
                logger.error("❌ PostgreSQL schema isolation failed")
                
            return success
            
        except Exception as e:
            error_msg = f"PostgreSQL isolation error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['isolation_results']['postgresql'] = {
                'status': 'ERROR',
                'error': error_msg
            }
            return False
    
    async def implement_neo4j_database_isolation(self) -> bool:
        """
        📊 Task 26.1.2.2: Neo4j Database Isolation
        
        Creates isolated n8n database in Neo4j.
        Command: CREATE DATABASE n8n IF NOT EXISTS WAIT;
        """
        logger.info("📊 Implementing Neo4j database isolation...")
        
        try:
            # Connect to Neo4j system database
            driver = AsyncGraphDatabase.driver(
                self.neo4j_config['uri'],
                auth=(self.neo4j_config['user'], self.neo4j_config['password'])
            )
            
            async with driver.session(database="system") as session:
                # Create n8n database
                create_query = "CREATE DATABASE n8n IF NOT EXISTS WAIT"
                await session.run(create_query)
                
                # Verify database creation
                verify_query = "SHOW DATABASES WHERE name = 'n8n'"
                result = await session.run(verify_query)
                databases = await result.data()
                
                success = len(databases) > 0 and databases[0]['name'] == 'n8n'
                
                await driver.close()
                
                self.results['isolation_results']['neo4j'] = {
                    'status': 'SUCCESS' if success else 'FAILED',
                    'database_created': success,
                    'database_name': 'n8n',
                    'isolation_method': 'Database isolation'
                }
                
                if success:
                    logger.info("✅ Neo4j database isolation completed successfully")
                else:
                    logger.error("❌ Neo4j database isolation failed")
                
                return success
            
        except Exception as e:
            error_msg = f"Neo4j isolation error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['isolation_results']['neo4j'] = {
                'status': 'ERROR',
                'error': error_msg
            }
            return False
    
    def implement_redis_database_separation(self) -> bool:
        """
        🔄 Task 26.1.2.3: Redis Database Separation
        
        Configures Redis for n8n BullMQ queue isolation.
        Commands: CONFIG SET databases 16; SELECT 2; FLUSHDB;
        """
        logger.info("🔄 Implementing Redis database separation...")
        
        try:
            # Connect to Redis
            r = redis.Redis(
                host=self.redis_config['host'],
                port=self.redis_config['port'],
                password=self.redis_config['password'],
                decode_responses=True
            )
            
            # Ensure 16 databases are available
            r.config_set('databases', 16)
            
            # Select database 2 for n8n BullMQ
            r.select(2)
            
            # Clear database 2 to ensure clean slate
            r.flushdb()
            
            # Set a test key to verify isolation
            r.set('n8n:test:isolation', 'verified')
            test_value = r.get('n8n:test:isolation')
            
            # Switch back to default database and verify separation
            r.select(0)
            default_test = r.get('n8n:test:isolation')
            
            # Clean up test key
            r.select(2)
            r.delete('n8n:test:isolation')
            
            success = test_value == 'verified' and default_test is None
            
            self.results['isolation_results']['redis'] = {
                'status': 'SUCCESS' if success else 'FAILED',
                'databases_configured': 16,
                'n8n_database': 2,
                'isolation_verified': success,
                'isolation_method': 'Database separation'
            }
            
            if success:
                logger.info("✅ Redis database separation completed successfully")
            else:
                logger.error("❌ Redis database separation failed")
            
            return success
            
        except Exception as e:
            error_msg = f"Redis isolation error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['isolation_results']['redis'] = {
                'status': 'ERROR',
                'error': error_msg
            }
            return False
    
    def implement_qdrant_collection_isolation(self) -> bool:
        """
        🎯 Task 26.1.2.4: Qdrant Collection Isolation
        
        Creates isolated n8n_memory collection in Qdrant.
        Creates collection with Cosine distance for vector operations.
        """
        logger.info("🎯 Implementing Qdrant collection isolation...")
        
        try:
            # Connect to Qdrant
            client = QdrantClient(
                host=self.qdrant_config['host'],
                port=self.qdrant_config['port']
            )
            
            # Create n8n_memory collection
            collection_name = "n8n_memory"
            
            # Check if collection already exists
            collections = client.get_collections()
            existing_collections = [col.name for col in collections.collections]
            
            if collection_name not in existing_collections:
                client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=1024,  # OpenAI text-embedding-3-large size
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created new collection: {collection_name}")
            else:
                logger.info(f"Collection {collection_name} already exists")
            
            # Verify collection creation
            collection_info = client.get_collection(collection_name)
            success = collection_info.status == "green"
            
            self.results['isolation_results']['qdrant'] = {
                'status': 'SUCCESS' if success else 'FAILED',
                'collection_created': True,
                'collection_name': collection_name,
                'vector_size': 1024,
                'distance_metric': 'Cosine',
                'isolation_method': 'Collection isolation'
            }
            
            if success:
                logger.info("✅ Qdrant collection isolation completed successfully")
            else:
                logger.error("❌ Qdrant collection isolation failed")
            
            return success
            
        except Exception as e:
            error_msg = f"Qdrant isolation error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            self.results['errors'].append(error_msg)
            self.results['isolation_results']['qdrant'] = {
                'status': 'ERROR',
                'error': error_msg
            }
            return False
    
    async def validate_namespace_isolation(self) -> Dict[str, bool]:
        """
        ✅ Task 26.1.2.5: Validate Namespace Isolation
        
        Verifies all database namespaces are properly isolated and accessible.
        """
        logger.info("✅ Validating namespace isolation...")
        
        validation_results = {}
        
        # Validate PostgreSQL schema
        try:
            conn = await asyncpg.connect(**self.postgres_config)
            result = await conn.fetchrow(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'n8n'"
            )
            validation_results['postgresql'] = result is not None
            await conn.close()
        except Exception as e:
            validation_results['postgresql'] = False
            self.results['errors'].append(f"PostgreSQL validation error: {str(e)}")
        
        # Validate Neo4j database
        try:
            driver = AsyncGraphDatabase.driver(
                self.neo4j_config['uri'],
                auth=(self.neo4j_config['user'], self.neo4j_config['password'])
            )
            async with driver.session(database="system") as session:
                result = await session.run("SHOW DATABASES WHERE name = 'n8n'")
                databases = await result.data()
                validation_results['neo4j'] = len(databases) > 0
            await driver.close()
        except Exception as e:
            validation_results['neo4j'] = False
            self.results['errors'].append(f"Neo4j validation error: {str(e)}")
        
        # Validate Redis database separation
        try:
            r = redis.Redis(**self.redis_config, decode_responses=True)
            r.select(2)
            r.set('validation:test', 'n8n_isolated')
            test_value = r.get('validation:test')
            r.delete('validation:test')
            validation_results['redis'] = test_value == 'n8n_isolated'
        except Exception as e:
            validation_results['redis'] = False
            self.results['errors'].append(f"Redis validation error: {str(e)}")
        
        # Validate Qdrant collection
        try:
            client = QdrantClient(
                host=self.qdrant_config['host'],
                port=self.qdrant_config['port']
            )
            collection_info = client.get_collection("n8n_memory")
            validation_results['qdrant'] = collection_info.status == "green"
        except Exception as e:
            validation_results['qdrant'] = False
            self.results['errors'].append(f"Qdrant validation error: {str(e)}")
        
        self.results['validation_results'] = validation_results
        
        # Log validation results
        for db, status in validation_results.items():
            if status:
                logger.info(f"✅ {db.title()} isolation validation: PASSED")
            else:
                logger.error(f"❌ {db.title()} isolation validation: FAILED")
        
        return validation_results
    
    def generate_n8n_configuration(self) -> Dict[str, str]:
        """
        📋 Task 26.1.2.6: Generate N8N Configuration
        
        Generates the environment configuration for n8n integration.
        """
        logger.info("📋 Generating N8N configuration...")
        
        n8n_config = {
            # PostgreSQL configuration with schema isolation
            'DB_TYPE': 'postgresdb',
            'DB_POSTGRESDB_HOST': self.postgres_config['host'],
            'DB_POSTGRESDB_PORT': str(self.postgres_config['port']),
            'DB_POSTGRESDB_DATABASE': self.postgres_config['database'],
            'DB_POSTGRESDB_SCHEMA': 'n8n',  # Isolated schema
            'DB_POSTGRESDB_USER': self.postgres_config['user'],
            'DB_POSTGRESDB_PASSWORD': self.postgres_config['password'],
            
            # Redis queue configuration with database separation
            'EXECUTIONS_MODE': 'queue',
            'QUEUE_BULL_REDIS_HOST': self.redis_config['host'],
            'QUEUE_BULL_REDIS_PORT': str(self.redis_config['port']),
            'QUEUE_BULL_REDIS_DB': '2',  # Isolated database
            'QUEUE_BULL_PREFIX': 'n8n_',
            
            # Operational configuration
            'N8N_DISABLE_PRODUCTION_MAIN_PROCESS': 'false',
            'GENERIC_TIMEZONE': 'America/Kentucky/Louisville',
            'N8N_PORT': '5678'
        }
        
        if self.redis_config['password']:
            n8n_config['QUEUE_BULL_REDIS_PASSWORD'] = self.redis_config['password']
        
        self.results['n8n_configuration'] = n8n_config
        
        return n8n_config
    
    def save_results(self) -> str:
        """Save namespace isolation results to file."""
        self.results['end_time'] = datetime.now().isoformat()
        self.results['duration_seconds'] = (datetime.now() - self.start_time).total_seconds()
        
        results_file = f"namespace_isolation_results_{self.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        return results_file
    
    async def execute_complete_isolation(self) -> bool:
        """
        🚀 Execute Complete Database Namespace Isolation
        
        Main orchestration method following AI Task Orchestrator methodology.
        """
        logger.info("🚀 Starting Phase 26 Database Namespace Isolation...")
        logger.info(f"📅 Session ID: {self.session_id}")
        
        # Task 26.1.2.1: PostgreSQL Schema Isolation
        postgres_success = await self.implement_postgresql_schema_isolation()
        
        # Task 26.1.2.2: Neo4j Database Isolation  
        neo4j_success = await self.implement_neo4j_database_isolation()
        
        # Task 26.1.2.3: Redis Database Separation
        redis_success = self.implement_redis_database_separation()
        
        # Task 26.1.2.4: Qdrant Collection Isolation
        qdrant_success = self.implement_qdrant_collection_isolation()
        
        # Task 26.1.2.5: Validate Namespace Isolation
        validation_results = await self.validate_namespace_isolation()
        
        # Task 26.1.2.6: Generate N8N Configuration
        n8n_config = self.generate_n8n_configuration()
        
        # Calculate overall success
        all_isolation_success = all([postgres_success, neo4j_success, redis_success, qdrant_success])
        all_validation_success = all(validation_results.values())
        overall_success = all_isolation_success and all_validation_success
        
        # Save results
        results_file = self.save_results()
        
        # Final reporting
        logger.info("=" * 80)
        logger.info("🎯 Phase 26 Database Namespace Isolation - COMPLETION REPORT")
        logger.info("=" * 80)
        logger.info(f"📅 Session ID: {self.session_id}")
        logger.info(f"⏱️  Duration: {self.results['duration_seconds']:.2f} seconds")
        logger.info(f"💾 Results saved: {results_file}")
        
        logger.info("\n📊 Isolation Results:")
        for db, result in self.results['isolation_results'].items():
            status = result.get('status', 'UNKNOWN')
            logger.info(f"   {db.title()}: {status}")
        
        logger.info("\n✅ Validation Results:")
        for db, success in validation_results.items():
            status = "PASSED" if success else "FAILED"
            logger.info(f"   {db.title()}: {status}")
        
        if overall_success:
            logger.info("\n🎉 PHASE 26 DATABASE NAMESPACE ISOLATION: COMPLETED SUCCESSFULLY")
            logger.info("✅ All database namespaces isolated and validated")
            logger.info("✅ N8N configuration generated")
            logger.info("✅ Ready for Phase 26.2: N8N Service Integration")
        else:
            logger.error("\n❌ PHASE 26 DATABASE NAMESPACE ISOLATION: COMPLETED WITH ERRORS")
            logger.error("⚠️  Some database isolations failed - review results")
        
        return overall_success


async def main():
    """Main execution function following AI Task Orchestrator methodology."""
    print("🤖 Phase 26: Database Namespace Isolation Implementation")
    print("=" * 70)
    print("📋 AI Task Orchestrator Methodology")
    print("🎯 Task: 26.1.2 - Database Namespace Isolation Implementation") 
    print("=" * 70)
    
    # Initialize isolation system
    isolation_system = Phase26NamespaceIsolation()
    
    # Execute complete isolation
    success = await isolation_system.execute_complete_isolation()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 