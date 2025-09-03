#!/usr/bin/env python3
"""
🔧 Add Missing PostgreSQL Columns

Specifically adds the missing file_name column to documentation and configuration_files tables
to fix the database storage issues identified in comprehensive testing.

Author: AI Task Orchestrator
Created: 2025-01-10
Task: Critical Fix - Add Missing PostgreSQL Columns
"""

import logging
import os
import sys

# Add current directory to path for imports
sys.path.append('.')

try:
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    print("❌ psycopg2 not available - PostgreSQL functionality disabled")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_database_config():
    """Load database configuration from environment"""
    from dotenv import load_dotenv
    load_dotenv()

    return {
        'host': os.getenv('POSTGRESQL_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRESQL_PORT', 5432)),
        'database': os.getenv('POSTGRESQL_DATABASE', 'plc_memory'),
        'user': os.getenv('POSTGRESQL_USER', 'postgres'),
        'password': os.getenv('POSTGRESQL_PASSWORD', 'postgres')
    }

def add_missing_columns():
    """Add missing file_name columns to PostgreSQL tables"""
    if not POSTGRESQL_AVAILABLE:
        print("❌ PostgreSQL not available")
        return False

    try:
        config = load_database_config()

        # Connect to PostgreSQL
        connection = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password']
        )
        connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cursor = connection.cursor()

        print("🔧 Adding missing file_name columns...")

        # Check and add file_name column to documentation table
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'documentation' AND column_name = 'file_name'
        """)

        if not cursor.fetchone():
            print("📋 Adding file_name column to documentation table...")
            cursor.execute("ALTER TABLE documentation ADD COLUMN file_name VARCHAR(255)")
            print("✅ Added file_name column to documentation table")
        else:
            print("⏭️ file_name column already exists in documentation table")

        # Check and add file_name column to configuration_files table
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'configuration_files' AND column_name = 'file_name'
        """)

        if not cursor.fetchone():
            print("📋 Adding file_name column to configuration_files table...")
            cursor.execute("ALTER TABLE configuration_files ADD COLUMN file_name VARCHAR(255)")
            print("✅ Added file_name column to configuration_files table")
        else:
            print("⏭️ file_name column already exists in configuration_files table")

        # Update existing records to populate file_name from file_path
        print("📋 Updating existing records to populate file_name...")

        cursor.execute("""
            UPDATE documentation
            SET file_name = substring(file_path from '[^/]*$')
            WHERE file_name IS NULL AND file_path IS NOT NULL
        """)

        cursor.execute("""
            UPDATE configuration_files
            SET file_name = substring(file_path from '[^/]*$')
            WHERE file_name IS NULL AND file_path IS NOT NULL
        """)

        print("✅ Updated existing records with file_name values")

        cursor.close()
        connection.close()

        print("🎯 Successfully added missing columns!")
        return True

    except Exception as e:
        logger.error(f"❌ Error adding columns: {str(e)}")
        return False

def main():
    """Main execution function"""
    print("🚀 Adding Missing PostgreSQL Columns")
    print("=" * 50)

    success = add_missing_columns()

    if success:
        print("\n✅ All missing columns added successfully!")
        return 0
    else:
        print("\n❌ Failed to add missing columns")
        return 1

if __name__ == "__main__":
    exit(main())
