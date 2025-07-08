#!/usr/bin/env python3
"""
Comprehensive Backup Framework for PLC-GPT Enterprise Stack
Created: July 7, 2025
Purpose: Reusable, modular backup system for multiple database types

This framework provides:
- Abstract base classes for different backup types
- Configurable backup strategies
- Metadata management and validation
- Error handling and recovery
- Progress tracking and reporting
- Integration with AI Task Orchestrator
"""

import os
import sys
import json
import abc
import subprocess
import shutil
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import tempfile

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class BackupType(Enum):
    """Enumeration of supported backup types."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"
    SNAPSHOT = "snapshot"


class BackupStatus(Enum):
    """Enumeration of backup status values."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DatabaseType(Enum):
    """Enumeration of supported database types."""
    NEO4J = "neo4j"
    POSTGRESQL = "postgresql"
    QDRANT = "qdrant"
    REDIS = "redis"
    MONGODB = "mongodb"
    MYSQL = "mysql"


@dataclass
class BackupConfiguration:
    """Configuration for backup operations."""
    database_type: DatabaseType
    backup_type: BackupType
    retention_days: int = 30
    compression: bool = True
    encryption: bool = False
    verify_integrity: bool = True
    include_metadata: bool = True
    custom_options: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.custom_options is None:
            self.custom_options = {}


@dataclass
class BackupMetadata:
    """Metadata for backup operations."""
    backup_id: str
    database_type: DatabaseType
    backup_type: BackupType
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: BackupStatus = BackupStatus.PENDING
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    checksum: Optional[str] = None
    database_stats: Dict[str, Any] = None
    context_info: Dict[str, Any] = None
    error_message: Optional[str] = None
    duration_seconds: float = 0.0
    
    def __post_init__(self):
        if self.database_stats is None:
            self.database_stats = {}
        if self.context_info is None:
            self.context_info = {}


@dataclass
class BackupResult:
    """Result of a backup operation."""
    success: bool
    metadata: BackupMetadata
    message: str
    details: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class BackupProgressCallback:
    """Callback interface for backup progress reporting."""
    
    def on_start(self, backup_id: str, database_type: DatabaseType):
        """Called when backup starts."""
        pass
    
    def on_progress(self, backup_id: str, progress_percent: float, message: str):
        """Called during backup progress."""
        pass
    
    def on_complete(self, backup_id: str, result: BackupResult):
        """Called when backup completes."""
        pass
    
    def on_error(self, backup_id: str, error: Exception):
        """Called when backup encounters an error."""
        pass


class DatabaseBackupStrategy(abc.ABC):
    """Abstract base class for database backup strategies."""
    
    def __init__(self, config: BackupConfiguration):
        """Initialize backup strategy with configuration."""
        self.config = config
        self.progress_callback: Optional[BackupProgressCallback] = None
    
    def set_progress_callback(self, callback: BackupProgressCallback):
        """Set progress callback for reporting."""
        self.progress_callback = callback
    
    @abc.abstractmethod
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites for backup are met."""
        pass
    
    @abc.abstractmethod
    def get_database_stats(self) -> Dict[str, Any]:
        """Get current database statistics."""
        pass
    
    @abc.abstractmethod
    def create_backup(self, backup_path: Path) -> BackupResult:
        """Create backup and return result."""
        pass
    
    @abc.abstractmethod
    def verify_backup(self, backup_path: Path) -> bool:
        """Verify backup integrity."""
        pass
    
    @abc.abstractmethod
    def restore_backup(self, backup_path: Path, target_location: Optional[str] = None) -> bool:
        """Restore backup to target location."""
        pass
    
    def _generate_backup_id(self) -> str:
        """Generate unique backup ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
        return f"{self.config.database_type.value}_backup_{timestamp}_{random_suffix}"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate MD5 checksum of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _report_progress(self, backup_id: str, progress: float, message: str):
        """Report progress if callback is set."""
        if self.progress_callback:
            self.progress_callback.on_progress(backup_id, progress, message)
    
    def _run_command(self, cmd: List[str], description: str, timeout: int = 300) -> tuple[bool, str, str]:
        """Run command with error handling."""
        logger.info(f"Running command: {description}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                logger.info(f"Command succeeded: {description}")
                return True, result.stdout, result.stderr
            else:
                logger.error(f"Command failed: {description}", error=result.stderr)
                return False, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out: {description}")
            return False, "", "Command timed out"
        except Exception as e:
            logger.error(f"Command exception: {description}", error=str(e))
            return False, "", str(e)


class BackupManager:
    """Main backup manager for coordinating backup operations."""
    
    def __init__(self, base_backup_dir: Union[str, Path] = "backup"):
        """Initialize backup manager."""
        self.base_backup_dir = Path(base_backup_dir)
        self.base_backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Registry of backup strategies
        self.strategies: Dict[DatabaseType, DatabaseBackupStrategy] = {}
        
        # Backup history
        self.backup_history: List[BackupMetadata] = []
        
        # Load existing backup history
        self._load_backup_history()
    
    def register_strategy(self, database_type: DatabaseType, strategy: DatabaseBackupStrategy):
        """Register a backup strategy for a database type."""
        self.strategies[database_type] = strategy
        logger.info(f"Registered backup strategy for {database_type.value}")
    
    def create_backup(self, 
                     database_type: DatabaseType, 
                     backup_config: Optional[BackupConfiguration] = None,
                     context_info: Optional[Dict[str, Any]] = None,
                     progress_callback: Optional[BackupProgressCallback] = None) -> BackupResult:
        """Create backup for specified database type."""
        
        # Use default config if none provided
        if backup_config is None:
            backup_config = BackupConfiguration(database_type=database_type, backup_type=BackupType.FULL)
        
        # Check if strategy is registered
        if database_type not in self.strategies:
            error_msg = f"No backup strategy registered for {database_type.value}"
            logger.error(error_msg)
            return BackupResult(
                success=False,
                metadata=BackupMetadata(
                    backup_id="",
                    database_type=database_type,
                    backup_type=backup_config.backup_type,
                    created_at=datetime.now(),
                    status=BackupStatus.FAILED,
                    error_message=error_msg
                ),
                message=error_msg
            )
        
        strategy = self.strategies[database_type]
        if progress_callback:
            strategy.set_progress_callback(progress_callback)
        
        # Generate backup metadata
        backup_id = strategy._generate_backup_id()
        metadata = BackupMetadata(
            backup_id=backup_id,
            database_type=database_type,
            backup_type=backup_config.backup_type,
            created_at=datetime.now(),
            context_info=context_info or {}
        )
        
        # Notify start
        if progress_callback:
            progress_callback.on_start(backup_id, database_type)
        
        try:
            # Check prerequisites
            strategy._report_progress(backup_id, 10, "Checking prerequisites")
            prerequisites = strategy.check_prerequisites()
            if not all(prerequisites.values()):
                failed_checks = [k for k, v in prerequisites.items() if not v]
                error_msg = f"Prerequisites failed: {', '.join(failed_checks)}"
                metadata.status = BackupStatus.FAILED
                metadata.error_message = error_msg
                result = BackupResult(success=False, metadata=metadata, message=error_msg)
                if progress_callback:
                    progress_callback.on_complete(backup_id, result)
                return result
            
            # Get database stats
            strategy._report_progress(backup_id, 20, "Collecting database statistics")
            metadata.database_stats = strategy.get_database_stats()
            
            # Create backup directory
            backup_dir = self.base_backup_dir / database_type.value / backup_id
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create backup
            strategy._report_progress(backup_id, 30, "Creating backup")
            metadata.status = BackupStatus.IN_PROGRESS
            result = strategy.create_backup(backup_dir)
            
            # Update metadata with result
            metadata.completed_at = datetime.now()
            metadata.duration_seconds = (metadata.completed_at - metadata.created_at).total_seconds()
            
            if result.success:
                metadata.status = BackupStatus.COMPLETED
                metadata.file_path = str(backup_dir)
                
                # Calculate file size and checksum
                if backup_dir.exists():
                    total_size = sum(f.stat().st_size for f in backup_dir.rglob('*') if f.is_file())
                    metadata.file_size_bytes = total_size
                
                # Verify backup if configured
                if backup_config.verify_integrity:
                    strategy._report_progress(backup_id, 80, "Verifying backup integrity")
                    if not strategy.verify_backup(backup_dir):
                        metadata.status = BackupStatus.FAILED
                        metadata.error_message = "Backup verification failed"
                        result.success = False
                        result.message = "Backup created but verification failed"
                
                # Save metadata
                strategy._report_progress(backup_id, 90, "Saving backup metadata")
                self._save_backup_metadata(backup_dir, metadata)
                
                strategy._report_progress(backup_id, 100, "Backup completed successfully")
            else:
                metadata.status = BackupStatus.FAILED
                metadata.error_message = result.message
            
            # Update result with final metadata
            result.metadata = metadata
            
            # Add to history
            self.backup_history.append(metadata)
            self._save_backup_history()
            
            # Notify completion
            if progress_callback:
                progress_callback.on_complete(backup_id, result)
            
            return result
            
        except Exception as e:
            error_msg = f"Backup failed with exception: {str(e)}"
            logger.error(error_msg, error=str(e))
            
            metadata.completed_at = datetime.now()
            metadata.duration_seconds = (metadata.completed_at - metadata.created_at).total_seconds()
            metadata.status = BackupStatus.FAILED
            metadata.error_message = error_msg
            
            result = BackupResult(success=False, metadata=metadata, message=error_msg)
            
            # Add to history
            self.backup_history.append(metadata)
            self._save_backup_history()
            
            # Notify error
            if progress_callback:
                progress_callback.on_error(backup_id, e)
            
            return result
    
    def list_backups(self, 
                    database_type: Optional[DatabaseType] = None,
                    status: Optional[BackupStatus] = None,
                    limit: Optional[int] = None) -> List[BackupMetadata]:
        """List backups with optional filtering."""
        filtered_backups = self.backup_history
        
        if database_type:
            filtered_backups = [b for b in filtered_backups if b.database_type == database_type]
        
        if status:
            filtered_backups = [b for b in filtered_backups if b.status == status]
        
        # Sort by creation time (newest first)
        filtered_backups.sort(key=lambda x: x.created_at, reverse=True)
        
        if limit:
            filtered_backups = filtered_backups[:limit]
        
        return filtered_backups
    
    def get_backup_by_id(self, backup_id: str) -> Optional[BackupMetadata]:
        """Get backup metadata by ID."""
        for backup in self.backup_history:
            if backup.backup_id == backup_id:
                return backup
        return None
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup by ID."""
        backup = self.get_backup_by_id(backup_id)
        if not backup:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        try:
            # Delete backup files
            if backup.file_path:
                backup_path = Path(backup.file_path)
                if backup_path.exists():
                    if backup_path.is_dir():
                        shutil.rmtree(backup_path)
                    else:
                        backup_path.unlink()
            
            # Remove from history
            self.backup_history = [b for b in self.backup_history if b.backup_id != backup_id]
            self._save_backup_history()
            
            logger.info(f"Deleted backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}", error=str(e))
            return False
    
    def cleanup_old_backups(self, retention_days: int = 30) -> Dict[str, Any]:
        """Clean up backups older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        deleted_count = 0
        freed_bytes = 0
        errors = []
        
        for backup in self.backup_history.copy():
            if backup.created_at < cutoff_date and backup.status == BackupStatus.COMPLETED:
                try:
                    if self.delete_backup(backup.backup_id):
                        deleted_count += 1
                        freed_bytes += backup.file_size_bytes
                except Exception as e:
                    errors.append(f"Failed to delete {backup.backup_id}: {str(e)}")
        
        return {
            "deleted_count": deleted_count,
            "freed_bytes": freed_bytes,
            "freed_mb": round(freed_bytes / (1024 * 1024), 2),
            "errors": errors
        }
    
    def restore_backup(self, backup_id: str, target_location: Optional[str] = None) -> bool:
        """Restore a backup by ID."""
        backup = self.get_backup_by_id(backup_id)
        if not backup:
            logger.error(f"Backup not found: {backup_id}")
            return False
        
        if backup.database_type not in self.strategies:
            logger.error(f"No strategy registered for {backup.database_type.value}")
            return False
        
        strategy = self.strategies[backup.database_type]
        backup_path = Path(backup.file_path) if backup.file_path else None
        
        if not backup_path or not backup_path.exists():
            logger.error(f"Backup files not found: {backup.file_path}")
            return False
        
        try:
            return strategy.restore_backup(backup_path, target_location)
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id}", error=str(e))
            return False
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup statistics."""
        total_backups = len(self.backup_history)
        successful_backups = len([b for b in self.backup_history if b.status == BackupStatus.COMPLETED])
        failed_backups = len([b for b in self.backup_history if b.status == BackupStatus.FAILED])
        
        total_size_bytes = sum(b.file_size_bytes for b in self.backup_history if b.status == BackupStatus.COMPLETED)
        
        # Group by database type
        by_database = {}
        for backup in self.backup_history:
            db_type = backup.database_type.value
            if db_type not in by_database:
                by_database[db_type] = {"count": 0, "size_bytes": 0}
            by_database[db_type]["count"] += 1
            if backup.status == BackupStatus.COMPLETED:
                by_database[db_type]["size_bytes"] += backup.file_size_bytes
        
        return {
            "total_backups": total_backups,
            "successful_backups": successful_backups,
            "failed_backups": failed_backups,
            "success_rate": round((successful_backups / total_backups * 100) if total_backups > 0 else 0, 2),
            "total_size_bytes": total_size_bytes,
            "total_size_mb": round(total_size_bytes / (1024 * 1024), 2),
            "by_database_type": by_database
        }
    
    def _save_backup_metadata(self, backup_dir: Path, metadata: BackupMetadata):
        """Save backup metadata to file."""
        metadata_file = backup_dir / "backup_metadata.json"
        with open(metadata_file, 'w') as f:
            # Convert to dict and handle datetime serialization
            metadata_dict = asdict(metadata)
            metadata_dict['created_at'] = metadata.created_at.isoformat()
            if metadata.completed_at:
                metadata_dict['completed_at'] = metadata.completed_at.isoformat()
            metadata_dict['database_type'] = metadata.database_type.value
            metadata_dict['backup_type'] = metadata.backup_type.value
            metadata_dict['status'] = metadata.status.value
            
            json.dump(metadata_dict, f, indent=2)
    
    def _load_backup_history(self):
        """Load backup history from persistent storage."""
        history_file = self.base_backup_dir / "backup_history.json"
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    history_data = json.load(f)
                
                for item in history_data:
                    # Convert back from dict
                    metadata = BackupMetadata(
                        backup_id=item['backup_id'],
                        database_type=DatabaseType(item['database_type']),
                        backup_type=BackupType(item['backup_type']),
                        created_at=datetime.fromisoformat(item['created_at']),
                        completed_at=datetime.fromisoformat(item['completed_at']) if item.get('completed_at') else None,
                        status=BackupStatus(item['status']),
                        file_path=item.get('file_path'),
                        file_size_bytes=item.get('file_size_bytes', 0),
                        checksum=item.get('checksum'),
                        database_stats=item.get('database_stats', {}),
                        context_info=item.get('context_info', {}),
                        error_message=item.get('error_message'),
                        duration_seconds=item.get('duration_seconds', 0.0)
                    )
                    self.backup_history.append(metadata)
                    
            except Exception as e:
                logger.warning(f"Failed to load backup history: {str(e)}")
    
    def _save_backup_history(self):
        """Save backup history to persistent storage."""
        history_file = self.base_backup_dir / "backup_history.json"
        try:
            history_data = []
            for metadata in self.backup_history:
                item = asdict(metadata)
                item['created_at'] = metadata.created_at.isoformat()
                if metadata.completed_at:
                    item['completed_at'] = metadata.completed_at.isoformat()
                item['database_type'] = metadata.database_type.value
                item['backup_type'] = metadata.backup_type.value
                item['status'] = metadata.status.value
                history_data.append(item)
            
            with open(history_file, 'w') as f:
                json.dump(history_data, f, indent=2)
                
        except Exception as e:
            logger.warning(f"Failed to save backup history: {str(e)}")


# Export main classes
__all__ = [
    'BackupType', 'BackupStatus', 'DatabaseType',
    'BackupConfiguration', 'BackupMetadata', 'BackupResult',
    'BackupProgressCallback', 'DatabaseBackupStrategy', 'BackupManager'
] 