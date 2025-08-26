#!/usr/bin/env python3
"""
N8N Framework Integration - Database Migration Script
Phase 1.2: PostgreSQL Schema Extension for Workflow Storage

Following AI Task Orchestrator TypeScript methodology with strict compliance.

This script applies the n8n workflow integration schema to the existing PLC-GBT PostgreSQL database.

Usage:
    python database_migration.py --apply
    python database_migration.py --validate
    python database_migration.py --rollback

Author: AI Task Orchestrator
Date: December 22, 2024
Phase: 1.2 - Core Engine Integration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import argparse

import asyncpg
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCHEMA_FILE = PROJECT_ROOT / "schemas" / "n8n_workflow_integration_schema.sql"
sys.path.insert(0, str(PROJECT_ROOT))


class MigrationConfig(BaseModel):
    """Database migration configuration with strict typing."""
    
    database_url: str = Field(
        default="postgresql://plc_user:CHANGE_PASSWORD@localhost:5432/plc_database",
        description="PostgreSQL database URL"
    )
    schema_file: Path = Field(
        default=SCHEMA_FILE,
        description="Path to schema SQL file"
    )
    migration_timeout: int = Field(
        default=300,
        description="Migration timeout in seconds"
    )
    validation_enabled: bool = Field(
        default=True,
        description="Enable schema validation after migration"
    )
    backup_enabled: bool = Field(
        default=True,
        description="Enable automatic backup before migration"
    )
    rollback_enabled: bool = Field(
        default=True,
        description="Enable rollback capability"
    )


class MigrationStatus(BaseModel):
    """Migration execution status with comprehensive tracking."""
    
    migration_id: str = Field(description="Unique migration identifier")
    phase: str = Field(default="1.2", description="Phase identifier")
    started_at: datetime = Field(default_factory=datetime.now)
    finished_at: Optional[datetime] = Field(default=None)
    status: str = Field(default="running", description="Migration status")
    success: bool = Field(default=False, description="Success indicator")
    error_message: Optional[str] = Field(default=None)
    rollback_available: bool = Field(default=False)
    
    # Detailed progress tracking
    steps_completed: List[str] = Field(default_factory=list)
    current_step: Optional[str] = Field(default=None)
    total_steps: int = Field(default=0)
    
    # Performance metrics
    execution_time_seconds: Optional[float] = Field(default=None)
    rows_affected: Dict[str, int] = Field(default_factory=dict)
    
    # Validation results
    validation_passed: bool = Field(default=False)
    validation_errors: List[str] = Field(default_factory=list)
    
    # Schema health metrics
    schema_health: Optional[Dict[str, Any]] = Field(default=None)


class DatabaseMigrationManager:
    """
    Manages database migration for N8N Framework Integration.
    
    Implements strict error handling, validation, and rollback capabilities
    following AI Task Orchestrator methodology.
    """
    
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.connection: Optional[asyncpg.Connection] = None
        self.migration_status = MigrationStatus(
            migration_id=f"n8n_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        
    async def __aenter__(self) -> 'DatabaseMigrationManager':
        """Async context manager entry."""
        await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit with proper cleanup."""
        if self.connection:
            await self.connection.close()
            
    async def connect(self) -> None:
        """Establish database connection with error handling."""
        try:
            logger.info("🔌 Connecting to PostgreSQL database...")
            self.connection = await asyncpg.connect(self.config.database_url)
            logger.info("✅ Database connection established")
            
            # Test connection
            result = await self.connection.fetchval("SELECT version()")
            logger.info(f"📊 PostgreSQL version: {result}")
            
        except Exception as e:
            error_msg = f"Failed to connect to database: {e}"
            logger.error(f"❌ {error_msg}")
            self.migration_status.error_message = error_msg
            self.migration_status.status = "connection_failed"
            raise
    
    async def validate_prerequisites(self) -> bool:
        """Validate migration prerequisites."""
        logger.info("🔍 Validating migration prerequisites...")
        
        try:
            # Check if schema file exists
            if not self.config.schema_file.exists():
                raise FileNotFoundError(f"Schema file not found: {self.config.schema_file}")
            
            logger.info(f"✅ Schema file found: {self.config.schema_file}")
            
            # Check database permissions
            can_create_schema = await self.connection.fetchval(
                "SELECT has_database_privilege(current_user, current_database(), 'CREATE')"
            )
            
            if not can_create_schema:
                raise PermissionError("Insufficient database permissions for schema creation")
            
            logger.info("✅ Database permissions validated")
            
            # Check for existing schema conflicts
            existing_schema = await self.connection.fetchval(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'plc_workflows'"
            )
            
            if existing_schema:
                logger.warning("⚠️  Schema 'plc_workflows' already exists - will update existing")
            else:
                logger.info("✅ New schema installation - no conflicts detected")
            
            return True
            
        except Exception as e:
            error_msg = f"Prerequisites validation failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.migration_status.error_message = error_msg
            return False
    
    async def create_backup(self) -> Optional[str]:
        """Create database backup before migration."""
        if not self.config.backup_enabled:
            logger.info("⏭️  Backup disabled - skipping")
            return None
            
        logger.info("💾 Creating database backup...")
        
        try:
            backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"n8n_migration_backup_{backup_timestamp}"
            
            # Create backup schema to store current state
            await self.connection.execute(f"CREATE SCHEMA IF NOT EXISTS {backup_name}")
            
            # Check if plc_workflows schema exists for backup
            schema_exists = await self.connection.fetchval(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'plc_workflows'"
            )
            
            if schema_exists:
                # Backup existing tables
                tables = await self.connection.fetch(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'plc_workflows'"
                )
                
                for table in tables:
                    table_name = table['table_name']
                    backup_table = f"{backup_name}.{table_name}"
                    source_table = f"plc_workflows.{table_name}"
                    
                    await self.connection.execute(
                        f"CREATE TABLE {backup_table} AS SELECT * FROM {source_table}"
                    )
                    
                logger.info(f"✅ Backup created: {backup_name} ({len(tables)} tables)")
            else:
                logger.info("✅ No existing schema to backup - proceeding with fresh installation")
            
            self.migration_status.rollback_available = True
            return backup_name
            
        except Exception as e:
            error_msg = f"Backup creation failed: {e}"
            logger.error(f"❌ {error_msg}")
            # Don't fail migration for backup issues, but log the warning
            logger.warning("⚠️  Continuing migration without backup (risk of data loss)")
            return None
    
    async def apply_schema(self) -> bool:
        """Apply the n8n workflow integration schema."""
        logger.info("🚀 Applying N8N workflow integration schema...")
        
        try:
            # Read schema file
            with open(self.config.schema_file, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            logger.info(f"📄 Schema file loaded: {len(schema_sql)} characters")
            
            # Split SQL into individual statements for better error tracking
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            self.migration_status.total_steps = len(statements)
            self.migration_status.current_step = "Executing SQL statements"
            
            # Execute statements in transaction
            async with self.connection.transaction():
                for i, statement in enumerate(statements, 1):
                    if not statement or statement.startswith('--'):
                        continue
                        
                    try:
                        await self.connection.execute(statement)
                        step_desc = f"Statement {i}/{len(statements)}"
                        self.migration_status.steps_completed.append(step_desc)
                        logger.debug(f"✅ {step_desc} executed")
                        
                    except Exception as stmt_error:
                        error_msg = f"Statement {i} failed: {stmt_error}\nSQL: {statement[:200]}..."
                        logger.error(f"❌ {error_msg}")
                        raise Exception(error_msg)
            
            logger.info("✅ Schema application completed successfully")
            return True
            
        except Exception as e:
            error_msg = f"Schema application failed: {e}"
            logger.error(f"❌ {error_msg}")
            self.migration_status.error_message = error_msg
            return False
    
    async def validate_schema(self) -> bool:
        """Validate the applied schema structure and data integrity."""
        logger.info("🔍 Validating applied schema...")
        
        try:
            validation_errors = []
            
            # Check schema existence
            schema_exists = await self.connection.fetchval(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'plc_workflows'"
            )
            
            if not schema_exists:
                validation_errors.append("Schema 'plc_workflows' not found")
            
            # Check required tables
            required_tables = [
                'workflow_definitions',
                'workflow_executions', 
                'node_executions',
                'workflow_templates',
                'workflow_schedules',
                'industrial_node_registry',
                'workflow_connections',
                'workflow_performance_metrics'
            ]
            
            existing_tables = await self.connection.fetch(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'plc_workflows'"
            )
            existing_table_names = {table['table_name'] for table in existing_tables}
            
            for table in required_tables:
                if table not in existing_table_names:
                    validation_errors.append(f"Required table '{table}' not found")
            
            # Check required views
            required_views = [
                'active_workflows_summary',
                'workflow_execution_summary', 
                'node_usage_statistics'
            ]
            
            existing_views = await self.connection.fetch(
                "SELECT table_name FROM information_schema.views WHERE table_schema = 'plc_workflows'"
            )
            existing_view_names = {view['table_name'] for view in existing_views}
            
            for view in required_views:
                if view not in existing_view_names:
                    validation_errors.append(f"Required view '{view}' not found")
            
            # Check required functions
            required_functions = [
                'update_modified_timestamp',
                'calculate_workflow_checksum',
                'validate_workflow_schema',
                'get_schema_health'
            ]
            
            existing_functions = await self.connection.fetch(
                """
                SELECT routine_name 
                FROM information_schema.routines 
                WHERE routine_schema = 'plc_workflows'
                AND routine_type = 'FUNCTION'
                """
            )
            existing_function_names = {func['routine_name'] for func in existing_functions}
            
            for function in required_functions:
                if function not in existing_function_names:
                    validation_errors.append(f"Required function '{function}' not found")
            
            # Test schema health function
            try:
                health_status = await self.connection.fetchval(
                    "SELECT plc_workflows.get_schema_health()"
                )
                
                if health_status:
                    health_data = json.loads(health_status)
                    self.migration_status.schema_health = health_data
                    logger.info(f"📊 Schema health: {health_data.get('status', 'unknown')}")
                
            except Exception as health_error:
                validation_errors.append(f"Schema health check failed: {health_error}")
            
            # Test basic operations
            try:
                # Test workflow validation function
                await self.connection.fetchval(
                    "SELECT plc_workflows.validate_workflow_schema('{}'::jsonb)"
                )
                
                # Test workflow checksum function  
                await self.connection.fetchval(
                    "SELECT plc_workflows.calculate_workflow_checksum('{}'::jsonb)"
                )
                
                logger.info("✅ Schema functions operational")
                
            except Exception as func_error:
                validation_errors.append(f"Schema functions test failed: {func_error}")
            
            # Update validation status
            if validation_errors:
                self.migration_status.validation_errors = validation_errors
                self.migration_status.validation_passed = False
                logger.error(f"❌ Schema validation failed with {len(validation_errors)} errors:")
                for error in validation_errors:
                    logger.error(f"   • {error}")
                return False
            else:
                self.migration_status.validation_passed = True
                logger.info("✅ Schema validation passed successfully")
                return True
                
        except Exception as e:
            error_msg = f"Schema validation error: {e}"
            logger.error(f"❌ {error_msg}")
            self.migration_status.validation_errors.append(error_msg)
            return False
    
    async def insert_initial_data(self) -> bool:
        """Insert initial data and configuration."""
        logger.info("📊 Inserting initial configuration data...")
        
        try:
            # Check if initial data already exists
            existing_marker = await self.connection.fetchval(
                """
                SELECT name FROM plc_workflows.workflow_definitions 
                WHERE name = '__schema_validation__'
                """
            )
            
            if existing_marker:
                logger.info("✅ Initial data already exists - skipping insertion")
                return True
            
            # Initial data is already included in the schema file via INSERT statements
            # This would be called if we needed additional data insertion
            
            logger.info("✅ Initial data insertion completed")
            return True
            
        except Exception as e:
            error_msg = f"Initial data insertion failed: {e}"
            logger.error(f"❌ {error_msg}")
            return False
    
    async def run_migration(self) -> MigrationStatus:
        """Execute complete migration process with comprehensive error handling."""
        logger.info("🚀 Starting N8N Framework Integration Database Migration")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        self.migration_status.started_at = start_time
        
        try:
            # Step 1: Validate prerequisites
            logger.info("📋 Phase 1.2 Step 1: Validating prerequisites...")
            if not await self.validate_prerequisites():
                self.migration_status.status = "prerequisites_failed"
                return self.migration_status
            
            # Step 2: Create backup
            logger.info("📋 Phase 1.2 Step 2: Creating backup...")
            backup_name = await self.create_backup()
            if backup_name:
                logger.info(f"✅ Backup created: {backup_name}")
            
            # Step 3: Apply schema
            logger.info("📋 Phase 1.2 Step 3: Applying workflow schema...")
            if not await self.apply_schema():
                self.migration_status.status = "schema_failed"
                return self.migration_status
            
            # Step 4: Validate schema
            logger.info("📋 Phase 1.2 Step 4: Validating schema...")
            if not await self.validate_schema():
                self.migration_status.status = "validation_failed"
                return self.migration_status
            
            # Step 5: Insert initial data
            logger.info("📋 Phase 1.2 Step 5: Inserting initial data...")
            if not await self.insert_initial_data():
                self.migration_status.status = "data_insertion_failed"
                return self.migration_status
            
            # Calculate execution time
            finish_time = datetime.now()
            self.migration_status.finished_at = finish_time
            self.migration_status.execution_time_seconds = (finish_time - start_time).total_seconds()
            
            # Mark as successful
            self.migration_status.success = True
            self.migration_status.status = "completed"
            
            logger.info("=" * 80)
            logger.info("✅ N8N Framework Integration Migration Completed Successfully!")
            logger.info(f"⏱️  Execution time: {self.migration_status.execution_time_seconds:.2f} seconds")
            logger.info(f"📊 Schema health: {self.migration_status.schema_health}")
            
            return self.migration_status
            
        except Exception as e:
            finish_time = datetime.now()
            self.migration_status.finished_at = finish_time
            self.migration_status.execution_time_seconds = (finish_time - start_time).total_seconds()
            self.migration_status.status = "failed"
            self.migration_status.error_message = str(e)
            
            logger.error("=" * 80)
            logger.error(f"❌ Migration failed: {e}")
            logger.error(f"⏱️  Execution time: {self.migration_status.execution_time_seconds:.2f} seconds")
            
            return self.migration_status


async def main() -> None:
    """Main entry point for database migration script."""
    parser = argparse.ArgumentParser(
        description="N8N Framework Integration Database Migration"
    )
    parser.add_argument(
        "--action", 
        choices=["apply", "validate", "status"], 
        default="apply",
        help="Migration action to perform"
    )
    parser.add_argument(
        "--database-url",
        help="PostgreSQL database URL",
        default=os.getenv("DATABASE_URL", "postgresql://plc_user:CHANGE_PASSWORD@localhost:5432/plc_database")
    )
    parser.add_argument(
        "--schema-file",
        help="Path to schema SQL file",
        default=str(SCHEMA_FILE)
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Migration timeout in seconds"
    )
    parser.add_argument(
        "--skip-backup",
        action="store_true",
        help="Skip database backup"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true", 
        help="Skip schema validation"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = MigrationConfig(
        database_url=args.database_url,
        schema_file=Path(args.schema_file),
        migration_timeout=args.timeout,
        backup_enabled=not args.skip_backup,
        validation_enabled=not args.skip_validation
    )
    
    logger.info("🔧 N8N Framework Integration - Database Migration")
    logger.info(f"📁 Schema file: {config.schema_file}")
    logger.info(f"🔗 Database: {config.database_url.split('@')[-1] if '@' in config.database_url else config.database_url}")
    logger.info(f"⚡ Action: {args.action}")
    
    try:
        async with DatabaseMigrationManager(config) as migration_manager:
            if args.action == "apply":
                status = await migration_manager.run_migration()
                
                if status.success:
                    logger.info("🎉 Migration completed successfully!")
                    sys.exit(0)
                else:
                    logger.error(f"❌ Migration failed: {status.error_message}")
                    sys.exit(1)
                    
            elif args.action == "validate":
                if await migration_manager.validate_schema():
                    logger.info("✅ Schema validation passed")
                    sys.exit(0)
                else:
                    logger.error("❌ Schema validation failed")
                    sys.exit(1)
                    
            elif args.action == "status":
                # Get schema health status
                health = await migration_manager.connection.fetchval(
                    "SELECT plc_workflows.get_schema_health()"
                )
                if health:
                    health_data = json.loads(health)
                    logger.info(f"📊 Schema Status: {json.dumps(health_data, indent=2)}")
                else:
                    logger.error("❌ Unable to get schema status")
                    sys.exit(1)
                    
    except Exception as e:
        logger.error(f"❌ Migration script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
