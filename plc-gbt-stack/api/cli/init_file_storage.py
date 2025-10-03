#!/usr/bin/env python3
"""
CLI Tool to Initialize File Storage System
Initializes PostgreSQL schema and creates default folder structure
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import psycopg2

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.file_storage_service import FileStorageService
from api.services.file_structure_initializer import FileStructureInitializer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_db_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment
    
    Returns:
        Connection string
    """
    # Try to get from environment
    if conn_str := os.getenv('DATABASE_URL'):
        return conn_str

    # Build from individual components
    host = os.getenv('POSTGRES_HOST', 'localhost')
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('POSTGRES_DB', 'plc_gbt')
    user = os.getenv('POSTGRES_USER', 'postgres')
    password = os.getenv('POSTGRES_PASSWORD', 'postgres')

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def init_database_schema(connection_string: str, schema_file: Path) -> bool:
    """
    Initialize database schema from SQL file
    
    Args:
        connection_string: PostgreSQL connection string
        schema_file: Path to schema SQL file
        
    Returns:
        True if successful
    """
    logger.info("Initializing database schema...")

    try:
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()

        # Read schema file
        with open(schema_file, encoding='utf-8') as f:
            schema_sql = f.read()

        # Execute schema
        cursor.execute(schema_sql)
        conn.commit()

        logger.info("✓ Database schema initialized successfully")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"✗ Failed to initialize database schema: {e}")
        return False


def init_file_structure(storage_service: FileStorageService, force: bool = False) -> bool:
    """
    Initialize default file structure
    
    Args:
        storage_service: FileStorageService instance
        force: Force recreation
        
    Returns:
        True if successful
    """
    logger.info("Initializing file structure...")

    try:
        initializer = FileStructureInitializer(storage_service)
        result = initializer.initialize_structure(force=force)

        if result['success']:
            logger.info(f"✓ {result['message']}")
            logger.info(f"  - Folders created: {result['folders_created']}")
            logger.info(f"  - Files created: {result['files_created']}")
            logger.info(f"  - Folders skipped: {result['folders_skipped']}")
        else:
            logger.error(f"✗ Initialization failed: {result['message']}")
            for error in result['errors']:
                logger.error(f"  - {error}")

        return result['success']

    except Exception as e:
        logger.error(f"✗ Failed to initialize file structure: {e}")
        return False


def verify_structure(storage_service: FileStorageService):
    """
    Verify file structure integrity
    
    Args:
        storage_service: FileStorageService instance
    """
    logger.info("Verifying file structure...")

    try:
        initializer = FileStructureInitializer(storage_service)
        result = initializer.verify_structure()

        logger.info(f"Structure completion: {result['completion_percentage']:.1f}%")
        logger.info(f"Existing folders: {result['existing_folders']}/{result['total_folders']}")

        if result['is_complete']:
            logger.info("✓ File structure is complete")
        else:
            logger.warning(f"✗ Missing {len(result['missing_folders'])} folders:")
            for folder in result['missing_folders']:
                logger.warning(f"  - {folder}")

    except Exception as e:
        logger.error(f"✗ Verification failed: {e}")


def show_stats(storage_service: FileStorageService):
    """
    Show storage statistics
    
    Args:
        storage_service: FileStorageService instance
    """
    logger.info("Fetching storage statistics...")

    try:
        stats = storage_service.get_storage_stats()

        logger.info("\nStorage Statistics:")
        logger.info(f"  Total files: {stats['total_files']}")
        logger.info(f"  Total size: {format_size(stats['total_size'])}")
        logger.info("\nBy Category:")

        for category_stats in stats['by_category']:
            logger.info(
                f"  - {category_stats['category'] or 'Uncategorized'}: "
                f"{category_stats['file_count']} files, "
                f"{format_size(category_stats['total_size'] or 0)}"
            )

    except Exception as e:
        logger.error(f"✗ Failed to fetch statistics: {e}")


def format_size(size_bytes: int | float) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes (int or float)
        
    Returns:
        Formatted size string
    """
    # Convert to float to handle both int and Decimal types
    size = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Initialize PLC-GBT File Storage System'
    )

    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database schema'
    )

    parser.add_argument(
        '--init-structure',
        action='store_true',
        help='Initialize default folder structure'
    )

    parser.add_argument(
        '--verify',
        action='store_true',
        help='Verify file structure integrity'
    )

    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show storage statistics'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force recreation of structure'
    )

    parser.add_argument(
        '--schema-file',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'database' / 'schemas' / 'file_storage_schema.sql',
        help='Path to schema SQL file'
    )

    parser.add_argument(
        '--storage-root',
        type=Path,
        default=Path(__file__).parent.parent.parent.parent / 'file-storage',
        help='Root directory for file storage'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all initialization steps'
    )

    args = parser.parse_args()

    # If no action specified, show help
    if not any([args.init_db, args.init_structure, args.verify, args.stats, args.all]):
        parser.print_help()
        return

    # Get database connection
    try:
        connection_string = get_db_connection_string()
        logger.info(f"Using storage root: {args.storage_root}")
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        sys.exit(1)

    success = True

    # Initialize database schema
    if args.init_db or args.all:
        if not init_database_schema(connection_string, args.schema_file):
            success = False
            if not args.all:
                sys.exit(1)

    # Create storage service
    try:
        storage_service = FileStorageService(
            db_connection_string=connection_string,
            storage_root=args.storage_root
        )
    except Exception as e:
        logger.error(f"Failed to create storage service: {e}")
        sys.exit(1)

    # Initialize file structure
    if args.init_structure or args.all:
        if not init_file_structure(storage_service, force=args.force):
            success = False

    # Verify structure
    if args.verify or args.all:
        verify_structure(storage_service)

    # Show statistics
    if args.stats or args.all:
        show_stats(storage_service)

    if success:
        logger.info("\n✓ All operations completed successfully")
    else:
        logger.error("\n✗ Some operations failed")
        sys.exit(1)


if __name__ == '__main__':
    main()

