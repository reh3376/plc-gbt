#!/usr/bin/env python3
"""
🗄️ PostgreSQL Schema Initializer - Critical Database Fix

Following AI Task Orchestrator Guide methodology to fix CRITICAL PostgreSQL schema issue
identified in comprehensive database audit.

Problem: Missing ALL expected tables (python_files, documentation, configuration_files)
Causing: 0% data completeness in long-term storage tier

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: IMMEDIATE Priority Fix (Critical - Fix Today)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Add current directory to path for imports
sys.path.append('.')

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("❌ psycopg2 not available - install with: pip install psycopg2-binary")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLSchemaInitializer:
    """
    🎯 PostgreSQL Schema Initializer
    
    Creates missing database tables for PLC Memory Management System
    following AI Task Orchestrator methodology for critical system fixes.
    """
    
    def __init__(self):
        self.connection = None
        self.schema_version = "1.0.0"
        self.session_id = f"schema_init_{int(datetime.now().timestamp())}"
        
        # Database configuration
        self.db_config = {
            "host": os.getenv("POSTGRES_HOST", "localhost"),
            "port": int(os.getenv("POSTGRES_PORT", "5432")),
            "database": os.getenv("POSTGRES_DB", "plc_metadata"),
            "user": os.getenv("POSTGRES_USER", "plc_user"),
            "password": os.getenv("POSTGRES_PASSWORD", "password")
        }
        
        # Define schema tables
        self.schema_definitions = self._define_schema()
        
    def _define_schema(self) -> Dict[str, str]:
        """Define schema for PLC memory ingestion tables"""
        
        return {
            # Python files table - stores processed Python file data
            "python_files": """
                CREATE TABLE IF NOT EXISTS python_files (
                    id SERIAL PRIMARY KEY,
                    file_path VARCHAR(500) NOT NULL UNIQUE,
                    file_name VARCHAR(255) NOT NULL,
                    file_size_bytes INTEGER NOT NULL DEFAULT 0,
                    functions_count INTEGER DEFAULT 0,
                    classes_count INTEGER DEFAULT 0,
                    lines_of_code INTEGER DEFAULT 0,
                    complexity_score REAL DEFAULT 0.0,
                    data JSONB NOT NULL,
                    metadata JSONB,
                    embedding_generated BOOLEAN DEFAULT FALSE,
                    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            # Documentation table - stores processed documentation files
            "documentation": """
                CREATE TABLE IF NOT EXISTS documentation (
                    id SERIAL PRIMARY KEY,
                    file_path VARCHAR(500) NOT NULL UNIQUE,
                    title VARCHAR(500),
                    doc_type VARCHAR(50) DEFAULT 'markdown',
                    file_size_bytes INTEGER NOT NULL DEFAULT 0,
                    word_count INTEGER DEFAULT 0,
                    section_count INTEGER DEFAULT 0,
                    data JSONB NOT NULL,
                    metadata JSONB,
                    embedding_generated BOOLEAN DEFAULT FALSE,
                    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            # Configuration files table - stores JSON, YAML, etc. configuration data
            "configuration_files": """
                CREATE TABLE IF NOT EXISTS configuration_files (
                    id SERIAL PRIMARY KEY,
                    file_path VARCHAR(500) NOT NULL UNIQUE,
                    file_name VARCHAR(255) NOT NULL,
                    config_type VARCHAR(50) DEFAULT 'json',
                    file_size_bytes INTEGER NOT NULL DEFAULT 0,
                    key_count INTEGER DEFAULT 0,
                    validation_status VARCHAR(20) DEFAULT 'pending',
                    data JSONB NOT NULL,
                    metadata JSONB,
                    embedding_generated BOOLEAN DEFAULT FALSE,
                    ingestion_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """,
            
            # Schema version tracking table
            "schema_version": """
                CREATE TABLE IF NOT EXISTS schema_version (
                    id SERIAL PRIMARY KEY,
                    version VARCHAR(20) NOT NULL,
                    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    applied_by VARCHAR(100) DEFAULT 'schema_initializer',
                    description TEXT,
                    session_id VARCHAR(100)
                );
            """,
            
            # Database health monitoring table
            "ingestion_health": """
                CREATE TABLE IF NOT EXISTS ingestion_health (
                    id SERIAL PRIMARY KEY,
                    check_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    table_name VARCHAR(100) NOT NULL,
                    record_count INTEGER NOT NULL DEFAULT 0,
                    last_ingestion TIMESTAMP WITH TIME ZONE,
                    health_status VARCHAR(20) DEFAULT 'unknown',
                    notes TEXT,
                    session_id VARCHAR(100)
                );
            """
        }

    def _define_indexes(self) -> Dict[str, List[str]]:
        """Define indexes to be created after tables"""
        return {
            "python_files": [
                "CREATE INDEX IF NOT EXISTS idx_python_files_path ON python_files(file_path);",
                "CREATE INDEX IF NOT EXISTS idx_python_files_name ON python_files(file_name);",
                "CREATE INDEX IF NOT EXISTS idx_python_files_timestamp ON python_files(ingestion_timestamp);",
                "CREATE INDEX IF NOT EXISTS idx_python_files_complexity ON python_files(complexity_score);",
                "CREATE INDEX IF NOT EXISTS gin_python_files_data ON python_files USING GIN (data);"
            ],
            "documentation": [
                "CREATE INDEX IF NOT EXISTS idx_documentation_path ON documentation(file_path);",
                "CREATE INDEX IF NOT EXISTS idx_documentation_title ON documentation(title);",
                "CREATE INDEX IF NOT EXISTS idx_documentation_type ON documentation(doc_type);",
                "CREATE INDEX IF NOT EXISTS idx_documentation_timestamp ON documentation(ingestion_timestamp);",
                "CREATE INDEX IF NOT EXISTS gin_documentation_data ON documentation USING GIN (data);"
            ],
            "configuration_files": [
                "CREATE INDEX IF NOT EXISTS idx_config_files_path ON configuration_files(file_path);",
                "CREATE INDEX IF NOT EXISTS idx_config_files_name ON configuration_files(file_name);",
                "CREATE INDEX IF NOT EXISTS idx_config_files_type ON configuration_files(config_type);",
                "CREATE INDEX IF NOT EXISTS idx_config_files_timestamp ON configuration_files(ingestion_timestamp);",
                "CREATE INDEX IF NOT EXISTS gin_config_files_data ON configuration_files USING GIN (data);"
            ]
        }

    async def connect_to_database(self) -> bool:
        """Establish connection to PostgreSQL database"""
        try:
            connection_string = (
                f"host={self.db_config['host']} "
                f"port={self.db_config['port']} "
                f"dbname={self.db_config['database']} "
                f"user={self.db_config['user']} "
                f"password={self.db_config['password']}"
            )
            
            self.connection = psycopg2.connect(connection_string)
            self.connection.autocommit = True
            
            # Test connection
            cursor = self.connection.cursor()
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            cursor.close()
            
            logger.info(f"✅ PostgreSQL connected: {version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {str(e)}")
            return False

    async def check_existing_schema(self) -> Dict[str, bool]:
        """Check which tables already exist"""
        existing_tables = {}
        
        try:
            cursor = self.connection.cursor()
            
            # Check for existing tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                AND table_name IN ('python_files', 'documentation', 'configuration_files', 'schema_version', 'ingestion_health')
            """)
            
            existing_table_names = [row[0] for row in cursor.fetchall()]
            
            # Map expected tables to existence status
            expected_tables = ['python_files', 'documentation', 'configuration_files', 'schema_version', 'ingestion_health']
            for table in expected_tables:
                existing_tables[table] = table in existing_table_names
                
            cursor.close()
            
            print(f"📊 Existing Tables Analysis:")
            for table, exists in existing_tables.items():
                status = "✅ EXISTS" if exists else "❌ MISSING"
                print(f"   {table}: {status}")
                
            return existing_tables
            
        except Exception as e:
            logger.error(f"Error checking existing schema: {str(e)}")
            return {}

    async def create_missing_tables(self, existing_tables: Dict[str, bool]) -> Dict[str, Any]:
        """Create missing tables based on schema definitions"""
        results = {
            "tables_created": [],
            "tables_skipped": [],
            "indexes_created": [],
            "errors": [],
            "success": True
        }
        
        try:
            cursor = self.connection.cursor()
            
            # Phase 1: Create tables
            for table_name, table_sql in self.schema_definitions.items():
                if not existing_tables.get(table_name, False):
                    try:
                        print(f"🏗️ Creating table: {table_name}")
                        
                        # Execute table creation SQL
                        cursor.execute(table_sql)
                        
                        results["tables_created"].append(table_name)
                        logger.info(f"✅ Created table: {table_name}")
                        
                    except Exception as e:
                        error_msg = f"Failed to create {table_name}: {str(e)}"
                        results["errors"].append(error_msg)
                        logger.error(f"❌ {error_msg}")
                        results["success"] = False
                else:
                    results["tables_skipped"].append(table_name)
                    print(f"⏭️ Skipped existing table: {table_name}")
            
            # Phase 2: Create indexes for successfully created tables
            if results["success"] and results["tables_created"]:
                print(f"\n🔗 Creating indexes for performance optimization...")
                index_definitions = self._define_indexes()
                
                for table_name in results["tables_created"]:
                    if table_name in index_definitions:
                        for index_sql in index_definitions[table_name]:
                            try:
                                cursor.execute(index_sql)
                                index_name = index_sql.split("IF NOT EXISTS ")[1].split(" ON ")[0].strip()
                                results["indexes_created"].append(f"{table_name}.{index_name}")
                                print(f"   ✅ Index: {index_name}")
                                
                            except Exception as e:
                                error_msg = f"Failed to create index for {table_name}: {str(e)}"
                                results["errors"].append(error_msg)
                                logger.warning(f"⚠️ {error_msg}")
                                # Don't fail the whole process for index creation errors
            
            cursor.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Schema creation failed: {str(e)}")
            results["errors"].append(f"Schema creation failed: {str(e)}")
            results["success"] = False
            return results

    async def record_schema_version(self) -> None:
        """Record schema version in database"""
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO schema_version (version, description, session_id)
                VALUES (%s, %s, %s)
            """, (
                self.schema_version,
                "Initial schema creation for PLC Memory Management System",
                self.session_id
            ))
            
            cursor.close()
            logger.info(f"✅ Schema version {self.schema_version} recorded")
            
        except Exception as e:
            logger.error(f"Failed to record schema version: {str(e)}")

    async def initialize_health_monitoring(self) -> None:
        """Initialize health monitoring records"""
        try:
            cursor = self.connection.cursor()
            
            tables_to_monitor = ['python_files', 'documentation', 'configuration_files']
            
            for table in tables_to_monitor:
                cursor.execute("""
                    INSERT INTO ingestion_health (table_name, record_count, health_status, notes, session_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    table,
                    0,
                    'initialized',
                    f'Table created and ready for ingestion',
                    self.session_id
                ))
            
            cursor.close()
            logger.info("✅ Health monitoring initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize health monitoring: {str(e)}")

    async def validate_schema_creation(self) -> Dict[str, Any]:
        """Validate that all tables were created successfully"""
        validation_results = {
            "all_tables_exist": True,
            "table_details": {},
            "total_tables": 0,
            "missing_tables": []
        }
        
        try:
            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            
            expected_tables = ['python_files', 'documentation', 'configuration_files', 'schema_version', 'ingestion_health']
            
            for table in expected_tables:
                try:
                    # Check table exists and get basic info
                    cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
                    result = cursor.fetchone()
                    
                    cursor.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    columns = cursor.fetchall()
                    
                    validation_results["table_details"][table] = {
                        "exists": True,
                        "record_count": result['count'],
                        "column_count": len(columns),
                        "columns": [col['column_name'] for col in columns]
                    }
                    
                    validation_results["total_tables"] += 1
                    
                except Exception as e:
                    validation_results["all_tables_exist"] = False
                    validation_results["missing_tables"].append(table)
                    validation_results["table_details"][table] = {
                        "exists": False,
                        "error": str(e)
                    }
            
            cursor.close()
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Schema validation failed: {str(e)}")
            return {"error": str(e)}

    async def run_schema_initialization(self) -> Dict[str, Any]:
        """Execute complete schema initialization process"""
        print("🚀 Starting PostgreSQL Schema Initialization")
        print("Following AI Task Orchestrator Guide Methodology")
        print("Task: IMMEDIATE Priority - Fix Critical PostgreSQL Schema Issue")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Initialize result tracking
        results = {
            "session_id": self.session_id,
            "start_time": start_time.isoformat(),
            "schema_version": self.schema_version,
            "success": False,
            "phases": {}
        }
        
        try:
            # Phase 1: Database Connection
            print("\n📋 Phase 1: Database Connection")
            if not await self.connect_to_database():
                results["error"] = "Failed to connect to PostgreSQL database"
                return results
            
            results["phases"]["connection"] = {"status": "success", "message": "Database connected"}
            
            # Phase 2: Check Existing Schema
            print("\n📋 Phase 2: Analyze Existing Schema")
            existing_tables = await self.check_existing_schema()
            results["phases"]["existing_schema"] = {"tables": existing_tables}
            
            # Phase 3: Create Missing Tables
            print("\n📋 Phase 3: Create Missing Tables")
            creation_results = await self.create_missing_tables(existing_tables)
            results["phases"]["table_creation"] = creation_results
            
            if not creation_results["success"]:
                print("❌ Table creation failed - see errors above")
                return results
            
            # Phase 4: Record Schema Version
            print("\n📋 Phase 4: Record Schema Version")
            await self.record_schema_version()
            
            # Phase 5: Initialize Health Monitoring
            print("\n📋 Phase 5: Initialize Health Monitoring")
            await self.initialize_health_monitoring()
            
            # Phase 6: Validate Schema
            print("\n📋 Phase 6: Validate Schema Creation")
            validation_results = await self.validate_schema_creation()
            results["phases"]["validation"] = validation_results
            
            # Calculate final results
            duration = (datetime.now() - start_time).total_seconds()
            results["duration_seconds"] = duration
            results["success"] = validation_results.get("all_tables_exist", False)
            results["end_time"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {str(e)}")
            traceback.print_exc()
            results["error"] = str(e)
            return results
            
        finally:
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")

async def main():
    """Main execution function"""
    initializer = PostgreSQLSchemaInitializer()
    results = await initializer.run_schema_initialization()
    
    if results.get("success"):
        print(f"\n🎯 PostgreSQL Schema Initialization Complete!")
        print("=" * 80)
        print(f"✅ Success: Schema initialization completed successfully")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        print(f"📊 Tables Created: {len(results['phases']['table_creation']['tables_created'])}")
        print(f"📋 Schema Version: {results['schema_version']}")
        
        # Display created tables
        created_tables = results['phases']['table_creation']['tables_created']
        if created_tables:
            print(f"\n🏗️ Tables Created:")
            for table in created_tables:
                print(f"   ✅ {table}")
        
        # Display validation results
        validation = results['phases']['validation']
        if validation.get('all_tables_exist'):
            print(f"\n✅ All tables validated successfully")
            print(f"📊 Total tables: {validation['total_tables']}")
        
        # Save results
        results_file = f"postgresql_schema_init_{initializer.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved: {results_file}")
        
        return 0
    else:
        print(f"\n❌ Schema Initialization Failed!")
        print("=" * 80)
        if "error" in results:
            print(f"Error: {results['error']}")
        
        # Display any errors from table creation
        creation_errors = results.get('phases', {}).get('table_creation', {}).get('errors', [])
        if creation_errors:
            print(f"\nTable Creation Errors:")
            for error in creation_errors:
                print(f"   ❌ {error}")
        
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 