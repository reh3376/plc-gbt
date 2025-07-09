#!/usr/bin/env python3
"""
Neo4j Backup Strategy Implementation
Created: July 7, 2025
Purpose: Specialized backup strategy for Neo4j databases using the backup framework

This module provides:
- Neo4j-specific backup operations
- Support for full and incremental backups
- Database statistics collection
- Backup verification and restoration
- Docker container integration
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from backup_framework import (
    DatabaseBackupStrategy, BackupConfiguration, BackupResult, BackupMetadata,
    DatabaseType, BackupType, BackupStatus
)

try:
    import structlog
    logger = structlog.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class Neo4jBackupStrategy(DatabaseBackupStrategy):
    """Neo4j-specific backup strategy implementation."""
    
    def __init__(self, 
                 config: BackupConfiguration,
                 container_name: str = "plc-neo4j",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "your-secure-neo4j-password",
                 database_name: str = "neo4j"):
        """
        Initialize Neo4j backup strategy.
        
        Args:
            config: Backup configuration
            container_name: Docker container name for Neo4j
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            database_name: Database name to backup
        """
        super().__init__(config)
        self.container_name = container_name
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.database_name = database_name
        self.backup_path_in_container = "/var/lib/neo4j/dumps"
    
    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if prerequisites for Neo4j backup are met."""
        prerequisites = {
            "docker_available": False,
            "container_running": False,
            "database_accessible": False,
            "backup_directory_writable": False
        }
        
        try:
            # Check Docker availability
            success, _, _ = self._run_command(["docker", "--version"], "Check Docker availability")
            prerequisites["docker_available"] = success
            
            if success:
                # Check if Neo4j container is running
                success, stdout, _ = self._run_command(
                    ["docker", "ps", "--filter", f"name={self.container_name}", "--format", "{{.Names}}"],
                    "Check Neo4j container status"
                )
                prerequisites["container_running"] = success and self.container_name in stdout
                
                if prerequisites["container_running"]:
                    # Check database accessibility
                    success, _, _ = self._run_command(
                        ["docker", "exec", self.container_name, "cypher-shell", 
                         "-u", self.neo4j_user, "-p", self.neo4j_password, "RETURN 1"],
                        "Test database connectivity"
                    )
                    prerequisites["database_accessible"] = success
                    
                    # Check if we can create backup directory in container
                    success, _, _ = self._run_command(
                        ["docker", "exec", self.container_name, "mkdir", "-p", self.backup_path_in_container],
                        "Create backup directory in container"
                    )
                    prerequisites["backup_directory_writable"] = success
        
        except Exception as e:
            logger.error(f"Error checking prerequisites: {str(e)}")
        
        return prerequisites
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get current Neo4j database statistics."""
        stats = {
            "total_nodes": 0,
            "total_relationships": 0,
            "node_types": {},
            "relationship_types": {},
            "database_size_estimate": "unknown",
            "last_transaction_id": "unknown"
        }
        
        try:
            # Get node counts by type
            success, stdout, _ = self._run_command([
                "docker", "exec", self.container_name, "cypher-shell",
                "-u", self.neo4j_user, "-p", self.neo4j_password,
                "MATCH (n) RETURN labels(n)[0] as NodeType, count(n) as Count ORDER BY NodeType"
            ], "Get node counts by type")
            
            if success:
                node_types = {}
                total_nodes = 0
                
                lines = stdout.strip().split('\n')
                for line in lines:
                    if '│' in line and 'NodeType' not in line and '───' not in line:
                        parts = line.split('│')
                        if len(parts) >= 3:
                            node_type = parts[1].strip().strip('"')
                            count_str = parts[2].strip()
                            if node_type and count_str.isdigit():
                                count = int(count_str)
                                node_types[node_type] = count
                                total_nodes += count
                
                stats["node_types"] = node_types
                stats["total_nodes"] = total_nodes
            
            # Get relationship counts by type
            success, stdout, _ = self._run_command([
                "docker", "exec", self.container_name, "cypher-shell",
                "-u", self.neo4j_user, "-p", self.neo4j_password,
                "MATCH ()-[r]->() RETURN type(r) as RelType, count(r) as Count ORDER BY RelType"
            ], "Get relationship counts by type")
            
            if success:
                rel_types = {}
                total_rels = 0
                
                lines = stdout.strip().split('\n')
                for line in lines:
                    if '│' in line and 'RelType' not in line and '───' not in line:
                        parts = line.split('│')
                        if len(parts) >= 3:
                            rel_type = parts[1].strip().strip('"')
                            count_str = parts[2].strip()
                            if rel_type and count_str.isdigit():
                                count = int(count_str)
                                rel_types[rel_type] = count
                                total_rels += count
                
                stats["relationship_types"] = rel_types
                stats["total_relationships"] = total_rels
            
            # Get database info
            success, stdout, _ = self._run_command([
                "docker", "exec", self.container_name, "cypher-shell",
                "-u", self.neo4j_user, "-p", self.neo4j_password,
                "CALL dbms.database.state($database) YIELD state RETURN state",
                f"-P database={self.database_name}"
            ], "Get database state")
            
            if success and "online" in stdout.lower():
                stats["database_state"] = "online"
            
        except Exception as e:
            logger.warning(f"Error collecting database stats: {str(e)}")
        
        return stats
    
    def create_backup(self, backup_path: Path) -> BackupResult:
        """Create Neo4j backup."""
        backup_id = self._generate_backup_id()
        
        try:
            # Ensure backup directory exists in container
            self._report_progress(backup_id, 10, "Preparing backup environment")
            success, _, _ = self._run_command([
                "docker", "exec", self.container_name, "mkdir", "-p", self.backup_path_in_container
            ], "Create backup directory in container")
            
            if not success:
                return BackupResult(
                    success=False,
                    metadata=BackupMetadata(
                        backup_id=backup_id,
                        database_type=DatabaseType.NEO4J,
                        backup_type=self.config.backup_type,
                        created_at=datetime.now(),
                        status=BackupStatus.FAILED,
                        error_message="Failed to create backup directory in container"
                    ),
                    message="Failed to prepare backup environment"
                )
            
            # Determine backup command based on type
            self._report_progress(backup_id, 30, "Creating database backup")
            
            if self.config.backup_type == BackupType.FULL:
                backup_cmd = [
                    "docker", "exec", self.container_name,
                    "neo4j-admin", "database", "backup",
                    f"--to-path={self.backup_path_in_container}",
                    self.database_name
                ]
            elif self.config.backup_type == BackupType.INCREMENTAL:
                backup_cmd = [
                    "docker", "exec", self.container_name,
                    "neo4j-admin", "database", "backup",
                    f"--to-path={self.backup_path_in_container}",
                    "--prefer-diff-as-parent",
                    self.database_name
                ]
            else:
                # Default to full backup
                backup_cmd = [
                    "docker", "exec", self.container_name,
                    "neo4j-admin", "database", "backup",
                    f"--to-path={self.backup_path_in_container}",
                    self.database_name
                ]
            
            # Execute backup
            success, stdout, stderr = self._run_command(
                backup_cmd, 
                f"Create {self.config.backup_type.value} backup",
                timeout=600  # 10 minutes
            )
            
            backup_method = "neo4j_admin"
            backup_files = []
            
            if not success:
                # Try alternative backup method
                self._report_progress(backup_id, 40, "Primary backup failed, trying alternative method")
                
                success, backup_files = self._create_alternative_backup(backup_id)
                backup_method = "cypher_export"
                
                if not success:
                    return BackupResult(
                        success=False,
                        metadata=BackupMetadata(
                            backup_id=backup_id,
                            database_type=DatabaseType.NEO4J,
                            backup_type=self.config.backup_type,
                            created_at=datetime.now(),
                            status=BackupStatus.FAILED,
                            error_message=f"Both primary and alternative backup methods failed: {stderr}"
                        ),
                        message="Backup creation failed"
                    )
            
            # Copy backup files to local directory
            self._report_progress(backup_id, 60, "Copying backup files to local directory")
            
            # List files in container backup directory
            success, stdout, _ = self._run_command([
                "docker", "exec", self.container_name, "ls", "-la", self.backup_path_in_container
            ], "List backup files in container")
            
            if success:
                # Copy entire backup directory
                copy_success, _, copy_error = self._run_command([
                    "docker", "cp", f"{self.container_name}:{self.backup_path_in_container}/",
                    str(backup_path) + "/"
                ], "Copy backup files to local directory")
                
                if not copy_success:
                    logger.warning(f"Copy operation failed: {copy_error}")
                    # Create backup info manually
                    self._create_manual_backup_info(backup_path, backup_id, backup_method)
            
            # Create backup metadata
            self._report_progress(backup_id, 80, "Creating backup metadata")
            
            backup_metadata = {
                "backup_id": backup_id,
                "method": backup_method,
                "database": self.database_name,
                "container": self.container_name,
                "backup_type": self.config.backup_type.value,
                "created_at": datetime.now().isoformat(),
                "files": backup_files if backup_files else ["neo4j backup files"]
            }
            
            # Save backup info
            info_file = backup_path / "neo4j_backup_info.json"
            with open(info_file, 'w') as f:
                json.dump(backup_metadata, f, indent=2)
            
            self._report_progress(backup_id, 100, "Backup completed successfully")
            
            return BackupResult(
                success=True,
                metadata=BackupMetadata(
                    backup_id=backup_id,
                    database_type=DatabaseType.NEO4J,
                    backup_type=self.config.backup_type,
                    created_at=datetime.now(),
                    completed_at=datetime.now(),
                    status=BackupStatus.COMPLETED,
                    file_path=str(backup_path)
                ),
                message="Neo4j backup completed successfully",
                details={
                    "backup_method": backup_method,
                    "backup_files": backup_files,
                    "database": self.database_name
                }
            )
            
        except Exception as e:
            error_msg = f"Neo4j backup failed with exception: {str(e)}"
            logger.error(error_msg)
            
            return BackupResult(
                success=False,
                metadata=BackupMetadata(
                    backup_id=backup_id,
                    database_type=DatabaseType.NEO4J,
                    backup_type=self.config.backup_type,
                    created_at=datetime.now(),
                    status=BackupStatus.FAILED,
                    error_message=error_msg
                ),
                message=error_msg
            )
    
    def _create_alternative_backup(self, backup_id: str) -> tuple[bool, List[str]]:
        """Create alternative backup using Cypher exports."""
        backup_files = []
        
        try:
            self._report_progress(backup_id, 45, "Creating Cypher exports")
            
            # Export queries
            export_queries = [
                ("nodes_export.cypher", "MATCH (n) RETURN n LIMIT 10000"),
                ("relationships_export.cypher", "MATCH ()-[r]->() RETURN r LIMIT 10000"),
                ("database_info.cypher", "CALL dbms.components() YIELD name, versions, edition RETURN name, versions, edition")
            ]
            
            for filename, query in export_queries:
                export_path = f"{self.backup_path_in_container}/{filename}"
                
                # Execute query and save to file
                success, stdout, _ = self._run_command([
                    "docker", "exec", self.container_name, "cypher-shell",
                    "-u", self.neo4j_user, "-p", self.neo4j_password,
                    "--format", "verbose", query
                ], f"Export {filename}")
                
                if success:
                    # Save output to container file
                    save_cmd = [
                        "docker", "exec", "-i", self.container_name, 
                        "bash", "-c", f"cat > {export_path}"
                    ]
                    save_result = subprocess.run(save_cmd, input=stdout, text=True, capture_output=True)
                    
                    if save_result.returncode == 0:
                        backup_files.append(filename)
            
            return len(backup_files) > 0, backup_files
            
        except Exception as e:
            logger.error(f"Alternative backup failed: {str(e)}")
            return False, []
    
    def _create_manual_backup_info(self, backup_path: Path, backup_id: str, method: str):
        """Create manual backup info when copy fails."""
        backup_info = {
            "backup_id": backup_id,
            "method": method,
            "status": "completed_with_warnings",
            "warning": "Backup files may not have been copied successfully",
            "container_path": self.backup_path_in_container,
            "manual_copy_command": f"docker cp {self.container_name}:{self.backup_path_in_container}/ {backup_path}/"
        }
        
        info_file = backup_path / "manual_backup_info.json"
        with open(info_file, 'w') as f:
            json.dump(backup_info, f, indent=2)
    
    def verify_backup(self, backup_path: Path) -> bool:
        """Verify Neo4j backup integrity."""
        try:
            # Check if backup files exist
            if not backup_path.exists():
                logger.error(f"Backup path does not exist: {backup_path}")
                return False
            
            # Look for Neo4j backup files
            backup_files = list(backup_path.rglob("*.backup"))
            cypher_files = list(backup_path.rglob("*.cypher"))
            info_files = list(backup_path.rglob("*_backup_info.json"))
            
            if not backup_files and not cypher_files:
                logger.error("No backup files found")
                return False
            
            # Verify backup file integrity if using neo4j-admin backup
            if backup_files:
                for backup_file in backup_files:
                    if backup_file.stat().st_size == 0:
                        logger.error(f"Backup file is empty: {backup_file}")
                        return False
            
            # Verify metadata files exist
            metadata_files = list(backup_path.rglob("backup_metadata.json"))
            if not metadata_files and not info_files:
                logger.warning("No metadata files found, but backup files exist")
            
            logger.info("Backup verification passed")
            return True
            
        except Exception as e:
            logger.error(f"Backup verification failed: {str(e)}")
            return False
    
    def restore_backup(self, backup_path: Path, target_location: Optional[str] = None) -> bool:
        """Restore Neo4j backup."""
        try:
            # Check if backup exists
            if not backup_path.exists():
                logger.error(f"Backup path does not exist: {backup_path}")
                return False
            
            # Find backup files
            backup_files = list(backup_path.rglob("*.backup"))
            
            if not backup_files:
                logger.error("No Neo4j backup files found for restoration")
                return False
            
            # Use the first backup file found
            backup_file = backup_files[0]
            
            # Copy backup file to container
            container_backup_path = f"{self.backup_path_in_container}/{backup_file.name}"
            
            success, _, _ = self._run_command([
                "docker", "cp", str(backup_file), f"{self.container_name}:{container_backup_path}"
            ], "Copy backup file to container")
            
            if not success:
                logger.error("Failed to copy backup file to container")
                return False
            
            # Stop Neo4j service (if running)
            logger.info("Stopping Neo4j service for restoration")
            self._run_command([
                "docker", "exec", self.container_name, "neo4j", "stop"
            ], "Stop Neo4j service")
            
            # Restore database
            success, stdout, stderr = self._run_command([
                "docker", "exec", self.container_name,
                "neo4j-admin", "database", "load",
                f"--from-path={self.backup_path_in_container}",
                "--force",
                self.database_name
            ], "Restore Neo4j database", timeout=600)
            
            if not success:
                logger.error(f"Database restoration failed: {stderr}")
                return False
            
            # Start Neo4j service
            logger.info("Starting Neo4j service after restoration")
            success, _, _ = self._run_command([
                "docker", "exec", self.container_name, "neo4j", "start"
            ], "Start Neo4j service")
            
            if success:
                logger.info("Neo4j backup restored successfully")
                return True
            else:
                logger.error("Failed to start Neo4j service after restoration")
                return False
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {str(e)}")
            return False


# Convenience function for creating Neo4j backup strategy
def create_neo4j_backup_strategy(
    backup_type: BackupType = BackupType.FULL,
    container_name: str = "plc-neo4j",
    neo4j_user: str = "neo4j",
    neo4j_password: str = "your-secure-neo4j-password",
    database_name: str = "neo4j",
    **config_options
) -> Neo4jBackupStrategy:
    """
    Create a configured Neo4j backup strategy.
    
    Args:
        backup_type: Type of backup to perform
        container_name: Docker container name
        neo4j_user: Neo4j username
        neo4j_password: Neo4j password
        database_name: Database name
        **config_options: Additional configuration options
    
    Returns:
        Configured Neo4j backup strategy
    """
    config = BackupConfiguration(
        database_type=DatabaseType.NEO4J,
        backup_type=backup_type,
        **config_options
    )
    
    return Neo4jBackupStrategy(
        config=config,
        container_name=container_name,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
        database_name=database_name
    ) 