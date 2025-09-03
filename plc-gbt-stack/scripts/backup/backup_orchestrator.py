#!/usr/bin/env python3
"""
Backup Orchestrator for PLC-GPT Enterprise Stack
Created: July 7, 2025
Purpose: Demonstrate and orchestrate backups using the reusable backup framework

This orchestrator provides:
- Easy-to-use backup operations for multiple databases
- Progress reporting and monitoring
- Batch backup operations
- Backup scheduling and automation
- Integration with existing maintenance systems
- Example usage patterns for the backup framework
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from backup_framework import (
    BackupConfiguration,
    BackupManager,
    BackupProgressCallback,
    BackupStatus,
    BackupType,
    DatabaseType,
)
from neo4j_backup_strategy import create_neo4j_backup_strategy

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class BackupProgressReporter(BackupProgressCallback):
    """Progress reporter for backup operations."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.start_times = {}

    def on_start(self, backup_id: str, database_type: DatabaseType):
        """Called when backup starts."""
        self.start_times[backup_id] = datetime.now()
        if self.verbose:
            print(f"🚀 Starting backup: {backup_id} ({database_type.value})")

    def on_progress(self, backup_id: str, progress_percent: float, message: str):
        """Called during backup progress."""
        if self.verbose:
            print(f"📊 {backup_id}: {progress_percent:.0f}% - {message}")

    def on_complete(self, backup_id: str, result):
        """Called when backup completes."""
        start_time = self.start_times.get(backup_id)
        duration = ""
        if start_time:
            elapsed = datetime.now() - start_time
            duration = f" (took {elapsed.total_seconds():.1f}s)"

        if result.success:
            if self.verbose:
                print(f"✅ Backup completed: {backup_id}{duration}")
                print(f"   Location: {result.metadata.file_path}")
                print(f"   Size: {result.metadata.file_size_bytes / (1024*1024):.2f} MB")
        else:
            if self.verbose:
                print(f"❌ Backup failed: {backup_id}{duration}")
                print(f"   Error: {result.message}")

    def on_error(self, backup_id: str, error: Exception):
        """Called when backup encounters an error."""
        if self.verbose:
            print(f"💥 Backup error: {backup_id} - {str(error)}")


class BackupOrchestrator:
    """Main orchestrator for managing backup operations across multiple databases."""

    def __init__(self, base_backup_dir: str = "backup"):
        """Initialize backup orchestrator."""
        self.backup_manager = BackupManager(base_backup_dir)
        self.progress_reporter = BackupProgressReporter()

        # Register default strategies
        self._register_default_strategies()

        logger.info("Backup orchestrator initialized")

    def _register_default_strategies(self):
        """Register default backup strategies for supported databases."""

        # Register Neo4j strategy
        neo4j_strategy = create_neo4j_backup_strategy(
            backup_type=BackupType.FULL,
            container_name="plc-neo4j",
            neo4j_password="your-secure-neo4j-password"
        )
        self.backup_manager.register_strategy(DatabaseType.NEO4J, neo4j_strategy)

        logger.info("Registered default backup strategies")

    def backup_neo4j(self,
                    backup_type: BackupType = BackupType.FULL,
                    context_info: Optional[Dict[str, Any]] = None,
                    verify_integrity: bool = True) -> Dict[str, Any]:
        """
        Backup Neo4j database with context information.

        Args:
            backup_type: Type of backup to perform
            context_info: Additional context information to include
            verify_integrity: Whether to verify backup integrity

        Returns:
            Backup operation result
        """
        print("=== NEO4J BACKUP OPERATION ===")
        print(f"Backup Type: {backup_type.value}")
        print(f"Verify Integrity: {verify_integrity}")
        if context_info:
            print(f"Context: {context_info}")
        print()

        # Create backup configuration
        config = BackupConfiguration(
            database_type=DatabaseType.NEO4J,
            backup_type=backup_type,
            verify_integrity=verify_integrity,
            retention_days=30
        )

        # Execute backup
        result = self.backup_manager.create_backup(
            database_type=DatabaseType.NEO4J,
            backup_config=config,
            context_info=context_info,
            progress_callback=self.progress_reporter
        )

        # Return formatted result
        return {
            "success": result.success,
            "backup_id": result.metadata.backup_id,
            "message": result.message,
            "file_path": result.metadata.file_path,
            "file_size_mb": round(result.metadata.file_size_bytes / (1024*1024), 2),
            "duration_seconds": result.metadata.duration_seconds,
            "database_stats": result.metadata.database_stats,
            "context_info": result.metadata.context_info
        }

    def backup_all_databases(self,
                           backup_type: BackupType = BackupType.FULL,
                           context_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Backup all registered databases.

        Args:
            backup_type: Type of backup to perform
            context_info: Additional context information

        Returns:
            Results for all backup operations
        """
        print("=== COMPREHENSIVE BACKUP OPERATION ===")
        print(f"Backup Type: {backup_type.value}")
        print(f"Databases: {list(self.backup_manager.strategies.keys())}")
        print()

        results = {}
        overall_success = True

        for database_type in self.backup_manager.strategies.keys():
            print(f"📦 Backing up {database_type.value}...")

            config = BackupConfiguration(
                database_type=database_type,
                backup_type=backup_type,
                verify_integrity=True
            )

            result = self.backup_manager.create_backup(
                database_type=database_type,
                backup_config=config,
                context_info=context_info,
                progress_callback=self.progress_reporter
            )

            results[database_type.value] = {
                "success": result.success,
                "backup_id": result.metadata.backup_id,
                "message": result.message,
                "file_path": result.metadata.file_path,
                "file_size_mb": round(result.metadata.file_size_bytes / (1024*1024), 2),
                "duration_seconds": result.metadata.duration_seconds
            }

            if not result.success:
                overall_success = False

            print()

        return {
            "overall_success": overall_success,
            "individual_results": results,
            "summary": {
                "total_databases": len(results),
                "successful": sum(1 for r in results.values() if r["success"]),
                "failed": sum(1 for r in results.values() if not r["success"]),
                "total_size_mb": sum(r["file_size_mb"] for r in results.values()),
                "total_duration": sum(r["duration_seconds"] for r in results.values())
            }
        }

    def list_backups(self,
                    database_type: Optional[str] = None,
                    status: Optional[str] = None,
                    limit: int = 10) -> List[Dict[str, Any]]:
        """
        List recent backups with optional filtering.

        Args:
            database_type: Filter by database type
            status: Filter by backup status
            limit: Maximum number of backups to return

        Returns:
            List of backup information
        """
        db_type = DatabaseType(database_type) if database_type else None
        backup_status = BackupStatus(status) if status else None

        backups = self.backup_manager.list_backups(
            database_type=db_type,
            status=backup_status,
            limit=limit
        )

        return [
            {
                "backup_id": backup.backup_id,
                "database_type": backup.database_type.value,
                "backup_type": backup.backup_type.value,
                "status": backup.status.value,
                "created_at": backup.created_at.isoformat(),
                "completed_at": backup.completed_at.isoformat() if backup.completed_at else None,
                "file_path": backup.file_path,
                "file_size_mb": round(backup.file_size_bytes / (1024*1024), 2),
                "duration_seconds": backup.duration_seconds,
                "context_info": backup.context_info
            }
            for backup in backups
        ]

    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics."""
        return self.backup_manager.get_backup_statistics()

    def cleanup_old_backups(self, retention_days: int = 30) -> Dict[str, Any]:
        """Clean up old backups beyond retention period."""
        print(f"🧹 Cleaning up backups older than {retention_days} days...")

        result = self.backup_manager.cleanup_old_backups(retention_days)

        print("✅ Cleanup completed:")
        print(f"   Files deleted: {result['deleted_count']}")
        print(f"   Space freed: {result['freed_mb']} MB")

        if result['errors']:
            print("⚠️  Errors encountered:")
            for error in result['errors']:
                print(f"   - {error}")

        return result

    def restore_backup(self, backup_id: str, target_location: Optional[str] = None) -> bool:
        """
        Restore a backup by ID.

        Args:
            backup_id: Backup ID to restore
            target_location: Optional target location for restoration

        Returns:
            True if restoration was successful
        """
        print(f"🔄 Restoring backup: {backup_id}")

        # Get backup metadata
        backup = self.backup_manager.get_backup_by_id(backup_id)
        if not backup:
            print(f"❌ Backup not found: {backup_id}")
            return False

        print(f"   Database: {backup.database_type.value}")
        print(f"   Created: {backup.created_at}")
        print(f"   Size: {backup.file_size_bytes / (1024*1024):.2f} MB")

        # Perform restoration
        success = self.backup_manager.restore_backup(backup_id, target_location)

        if success:
            print("✅ Backup restored successfully")
        else:
            print("❌ Backup restoration failed")

        return success

    def backup_with_context(self,
                          database_type: str,
                          context_description: str,
                          additional_metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a backup with specific context information.

        Args:
            database_type: Type of database to backup
            context_description: Description of the context (e.g., "after ingesting new data")
            additional_metadata: Additional metadata to include

        Returns:
            Backup operation result
        """
        db_type = DatabaseType(database_type)

        context_info = {
            "description": context_description,
            "timestamp": datetime.now().isoformat(),
            "triggered_by": "backup_orchestrator"
        }

        if additional_metadata:
            context_info.update(additional_metadata)

        print(f"=== CONTEXTUAL BACKUP: {database_type.upper()} ===")
        print(f"Context: {context_description}")
        print()

        config = BackupConfiguration(
            database_type=db_type,
            backup_type=BackupType.FULL,
            verify_integrity=True
        )

        result = self.backup_manager.create_backup(
            database_type=db_type,
            backup_config=config,
            context_info=context_info,
            progress_callback=self.progress_reporter
        )

        return {
            "success": result.success,
            "backup_id": result.metadata.backup_id,
            "message": result.message,
            "context": context_info,
            "file_path": result.metadata.file_path,
            "file_size_mb": round(result.metadata.file_size_bytes / (1024*1024), 2),
            "duration_seconds": result.metadata.duration_seconds
        }


def main():
    """Main function demonstrating backup orchestrator usage."""
    print("🤖 PLC-GPT Backup Orchestrator Demo")
    print("=" * 50)

    # Initialize orchestrator
    orchestrator = BackupOrchestrator()

    # Example 1: Backup Neo4j with context
    print("\n1. BACKUP NEO4J WITH CONTEXT")
    context_info = {
        "reason": "acd-l5x-tool-lib repository ingestion completed",
        "nodes_added": 30,
        "relationships_added": 49,
        "capabilities_mapped": 8
    }

    result = orchestrator.backup_neo4j(
        backup_type=BackupType.FULL,
        context_info=context_info,
        verify_integrity=True
    )

    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Backup ID: {result['backup_id']}")
        print(f"Size: {result['file_size_mb']} MB")

    # Example 2: List recent backups
    print("\n2. LIST RECENT BACKUPS")
    backups = orchestrator.list_backups(limit=5)
    for backup in backups:
        print(f"  {backup['backup_id']} - {backup['database_type']} - {backup['status']}")

    # Example 3: Get backup statistics
    print("\n3. BACKUP STATISTICS")
    stats = orchestrator.get_backup_statistics()
    print(f"Total backups: {stats['total_backups']}")
    print(f"Success rate: {stats['success_rate']}%")
    print(f"Total size: {stats['total_size_mb']} MB")

    # Example 4: Demonstrate contextual backup
    print("\n4. CONTEXTUAL BACKUP EXAMPLE")
    result = orchestrator.backup_with_context(
        database_type="neo4j",
        context_description="Post-ingestion backup after adding acd-l5x-tool-lib context",
        additional_metadata={
            "source_repository": "reh3376/acd-l5x-tool-lib",
            "ingestion_method": "automated_etl",
            "data_quality_score": 95
        }
    )

    print(f"Contextual backup result: {result['success']}")

    print("\n✅ Backup orchestrator demo completed!")


# Convenience functions for easy usage
def quick_neo4j_backup(context_description: Optional[str] = None) -> Dict[str, Any]:
    """Quick Neo4j backup with optional context."""
    orchestrator = BackupOrchestrator()

    if context_description:
        return orchestrator.backup_with_context("neo4j", context_description)
    else:
        return orchestrator.backup_neo4j()


def backup_after_data_ingestion(source_description: str,
                               nodes_added: int = 0,
                               relationships_added: int = 0) -> Dict[str, Any]:
    """Create backup after data ingestion with specific metadata."""
    orchestrator = BackupOrchestrator()

    context_info = {
        "reason": f"Data ingestion completed: {source_description}",
        "nodes_added": nodes_added,
        "relationships_added": relationships_added,
        "ingestion_timestamp": datetime.now().isoformat()
    }

    return orchestrator.backup_neo4j(
        backup_type=BackupType.FULL,
        context_info=context_info,
        verify_integrity=True
    )


if __name__ == "__main__":
    main()
