#!/usr/bin/env python3
"""
🔧 Fix PostgreSQL Columns via Database Manager

Uses the existing database_manager with working credentials to add missing file_name columns.

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: Critical Fix - Add Missing PostgreSQL Columns
"""

import os
import sys
import asyncio
import logging

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLColumnFixer:
    """Fix PostgreSQL schema using DatabaseManager"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    async def add_missing_columns(self):
        """Add missing file_name columns using DatabaseManager"""
        try:
            # Initialize database connection
            print("🔗 Initializing database connection...")
            await self.db_manager.initialize_all_connections()
            
            print("🔧 Adding missing file_name columns...")
            
            # Check and add file_name column to documentation table
            check_doc_query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'documentation' AND column_name = 'file_name'
            """
            
            result = await self.db_manager.execute_query(
                DatabaseType.POSTGRESQL, 
                check_doc_query
            )
            
            if not result.data:
                print("📋 Adding file_name column to documentation table...")
                alter_doc_query = "ALTER TABLE documentation ADD COLUMN file_name VARCHAR(255)"
                
                result = await self.db_manager.execute_query(
                    DatabaseType.POSTGRESQL, 
                    alter_doc_query
                )
                
                if result.success:
                    print("✅ Added file_name column to documentation table")
                else:
                    print(f"❌ Failed to add column to documentation: {result.error_message}")
                    return False
            else:
                print("⏭️ file_name column already exists in documentation table")
            
            # Check and add file_name column to configuration_files table
            check_config_query = """
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'configuration_files' AND column_name = 'file_name'
            """
            
            result = await self.db_manager.execute_query(
                DatabaseType.POSTGRESQL, 
                check_config_query
            )
            
            if not result.data:
                print("📋 Adding file_name column to configuration_files table...")
                alter_config_query = "ALTER TABLE configuration_files ADD COLUMN file_name VARCHAR(255)"
                
                result = await self.db_manager.execute_query(
                    DatabaseType.POSTGRESQL, 
                    alter_config_query
                )
                
                if result.success:
                    print("✅ Added file_name column to configuration_files table")
                else:
                    print(f"❌ Failed to add column to configuration_files: {result.error_message}")
                    return False
            else:
                print("⏭️ file_name column already exists in configuration_files table")
            
            # Update existing records to populate file_name from file_path
            print("📋 Updating existing records to populate file_name...")
            
            update_doc_query = """
                UPDATE documentation 
                SET file_name = substring(file_path from '[^/]*$') 
                WHERE file_name IS NULL AND file_path IS NOT NULL
            """
            
            result = await self.db_manager.execute_query(
                DatabaseType.POSTGRESQL, 
                update_doc_query
            )
            
            if result.success:
                print("✅ Updated documentation records with file_name values")
            else:
                print(f"⚠️ Warning: Failed to update documentation records: {result.error_message}")
            
            update_config_query = """
                UPDATE configuration_files 
                SET file_name = substring(file_path from '[^/]*$') 
                WHERE file_name IS NULL AND file_path IS NOT NULL
            """
            
            result = await self.db_manager.execute_query(
                DatabaseType.POSTGRESQL, 
                update_config_query
            )
            
            if result.success:
                print("✅ Updated configuration_files records with file_name values")
            else:
                print(f"⚠️ Warning: Failed to update configuration_files records: {result.error_message}")
            
            print("🎯 Successfully added missing columns!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error adding columns: {str(e)}")
            return False
        
        finally:
            await self.db_manager.close_all_connections()

async def main():
    """Main execution function"""
    print("🚀 Adding Missing PostgreSQL Columns via DatabaseManager")
    print("=" * 60)
    
    fixer = PostgreSQLColumnFixer()
    success = await fixer.add_missing_columns()
    
    if success:
        print("\n✅ All missing columns added successfully!")
        return 0
    else:
        print("\n❌ Failed to add missing columns")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 