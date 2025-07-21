#!/usr/bin/env python3
"""
AI Enhancement Framework - Memory Persistence

Provides project-scoped memory isolation and persistent context storage.
This module enables cross-session memory continuity and memory optimization.
"""

import json
import pickle
import asyncio
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
import hashlib
import gzip

logger = logging.getLogger(__name__)

@dataclass
class MemoryRecord:
    """Represents a stored memory record."""
    record_id: str
    project_id: str
    memory_type: str
    content: Any
    metadata: Dict[str, Any]
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    expires_at: Optional[datetime] = None

@dataclass
class MemoryScope:
    """Defines memory scope and isolation boundaries."""
    scope_id: str
    project_path: str
    isolation_level: str  # "project", "user", "global"
    retention_policy: Dict[str, Any]
    encryption_enabled: bool = False

class MemoryPersistence:
    """
    Manages project-scoped memory isolation and persistent storage.
    
    Features:
    - Project-scoped memory isolation
    - Persistent context storage across sessions
    - Cross-session memory continuity
    - Memory cleanup and optimization
    - Configurable retention policies
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the memory persistence system."""
        self.base_path = base_path or Path.cwd()
        self.memory_dir = self.base_path / ".ai_framework" / "memory"
        self.scopes: Dict[str, MemoryScope] = {}
        self.db_path = self.memory_dir / "memory.db"
        self.compression_enabled = True
        self.encryption_key: Optional[bytes] = None
        
    async def initialize(self) -> None:
        """Initialize the memory persistence system."""
        try:
            await self._setup_directories()
            await self._initialize_database()
            await self._load_scopes()
            await self._cleanup_expired_memories()
            logger.info("Memory Persistence initialized successfully")
        except Exception as e:
            logger.error(f"Memory Persistence initialization failed: {e}")
            raise
    
    async def _setup_directories(self) -> None:
        """Create necessary directories for memory storage."""
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        (self.memory_dir / "scopes").mkdir(exist_ok=True)
        (self.memory_dir / "backups").mkdir(exist_ok=True)
    
    async def _initialize_database(self) -> None:
        """Initialize the SQLite database for memory storage."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_records (
                record_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                metadata TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                last_accessed TIMESTAMP NOT NULL,
                access_count INTEGER DEFAULT 0,
                expires_at TIMESTAMP,
                content_size INTEGER NOT NULL,
                compression_used BOOLEAN DEFAULT FALSE
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS memory_scopes (
                scope_id TEXT PRIMARY KEY,
                project_path TEXT NOT NULL,
                isolation_level TEXT NOT NULL,
                retention_policy TEXT NOT NULL,
                encryption_enabled BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL
            )
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_project_id ON memory_records(project_id)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memory_records(memory_type)
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_expires_at ON memory_records(expires_at)
        """)
        
        conn.commit()
        conn.close()
    
    async def _load_scopes(self) -> None:
        """Load existing memory scopes from storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memory_scopes")
        rows = cursor.fetchall()
        
        for row in rows:
            scope_id, project_path, isolation_level, retention_policy_json, encryption_enabled, created_at = row
            
            scope = MemoryScope(
                scope_id=scope_id,
                project_path=project_path,
                isolation_level=isolation_level,
                retention_policy=json.loads(retention_policy_json),
                encryption_enabled=bool(encryption_enabled)
            )
            
            self.scopes[scope_id] = scope
        
        conn.close()
        logger.info(f"Loaded {len(self.scopes)} memory scopes")
    
    async def create_scope(
        self,
        project_path: str,
        isolation_level: str = "project",
        retention_policy: Optional[Dict[str, Any]] = None
    ) -> MemoryScope:
        """
        Create a new memory scope for a project.
        
        Args:
            project_path: Path to the project
            isolation_level: Level of memory isolation
            retention_policy: Memory retention configuration
            
        Returns:
            Created MemoryScope
        """
        scope_id = self._generate_scope_id(project_path)
        
        if not retention_policy:
            retention_policy = self._get_default_retention_policy(isolation_level)
        
        scope = MemoryScope(
            scope_id=scope_id,
            project_path=project_path,
            isolation_level=isolation_level,
            retention_policy=retention_policy,
            encryption_enabled=False  # Can be enabled later
        )
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO memory_scopes 
            (scope_id, project_path, isolation_level, retention_policy, encryption_enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            scope.scope_id,
            scope.project_path,
            scope.isolation_level,
            json.dumps(scope.retention_policy),
            scope.encryption_enabled,
            datetime.now()
        ))
        conn.commit()
        conn.close()
        
        self.scopes[scope_id] = scope
        logger.info(f"Created memory scope: {scope_id}")
        return scope
    
    async def store_memory(
        self,
        project_id: str,
        memory_type: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        ttl_hours: Optional[int] = None
    ) -> str:
        """
        Store a memory record for a project.
        
        Args:
            project_id: Project identifier
            memory_type: Type of memory (context, code_analysis, ai_state, etc.)
            content: Memory content to store
            metadata: Additional metadata
            ttl_hours: Time to live in hours
            
        Returns:
            Record ID of stored memory
        """
        record_id = self._generate_record_id(project_id, memory_type, content)
        
        if not metadata:
            metadata = {}
        
        # Calculate expiration
        expires_at = None
        if ttl_hours:
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
        elif project_id in self.scopes:
            default_ttl = self.scopes[project_id].retention_policy.get("default_ttl_hours")
            if default_ttl:
                expires_at = datetime.now() + timedelta(hours=default_ttl)
        
        # Serialize and compress content
        serialized_content = self._serialize_content(content)
        content_hash = hashlib.sha256(serialized_content).hexdigest()
        
        if self.compression_enabled:
            serialized_content = gzip.compress(serialized_content)
        
        # Store content to file
        content_file = self.memory_dir / f"{record_id}.mem"
        with open(content_file, 'wb') as f:
            f.write(serialized_content)
        
        # Store record metadata to database
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            INSERT OR REPLACE INTO memory_records
            (record_id, project_id, memory_type, content_hash, metadata, 
             created_at, last_accessed, access_count, expires_at, content_size, compression_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_id,
            project_id,
            memory_type,
            content_hash,
            json.dumps(metadata),
            datetime.now(),
            datetime.now(),
            0,
            expires_at,
            len(serialized_content),
            self.compression_enabled
        ))
        conn.commit()
        conn.close()
        
        logger.debug(f"Stored memory: {record_id} ({memory_type})")
        return record_id
    
    async def retrieve_memory(
        self,
        project_id: str,
        memory_type: Optional[str] = None,
        record_id: Optional[str] = None
    ) -> List[MemoryRecord]:
        """
        Retrieve memory records for a project.
        
        Args:
            project_id: Project identifier
            memory_type: Optional memory type filter
            record_id: Optional specific record ID
            
        Returns:
            List of MemoryRecord objects
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM memory_records WHERE project_id = ?"
        params = [project_id]
        
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)
        
        if record_id:
            query += " AND record_id = ?"
            params.append(record_id)
        
        query += " AND (expires_at IS NULL OR expires_at > ?)"
        params.append(datetime.now())
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        records = []
        for row in rows:
            (record_id, project_id, memory_type, content_hash, metadata_json, 
             created_at, last_accessed, access_count, expires_at, content_size, compression_used) = row
            
            # Load content from file
            content = await self._load_content_from_file(record_id, compression_used)
            
            # Update access count
            cursor.execute("""
                UPDATE memory_records 
                SET last_accessed = ?, access_count = access_count + 1
                WHERE record_id = ?
            """, (datetime.now(), record_id))
            
            record = MemoryRecord(
                record_id=record_id,
                project_id=project_id,
                memory_type=memory_type,
                content=content,
                metadata=json.loads(metadata_json),
                created_at=datetime.fromisoformat(created_at),
                last_accessed=datetime.now(),
                access_count=access_count + 1,
                expires_at=datetime.fromisoformat(expires_at) if expires_at else None
            )
            records.append(record)
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Retrieved {len(records)} memory records for {project_id}")
        return records
    
    async def delete_memory(
        self,
        project_id: str,
        memory_type: Optional[str] = None,
        record_id: Optional[str] = None
    ) -> int:
        """
        Delete memory records for a project.
        
        Args:
            project_id: Project identifier
            memory_type: Optional memory type filter
            record_id: Optional specific record ID
            
        Returns:
            Number of records deleted
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get records to delete (for file cleanup)
        query = "SELECT record_id FROM memory_records WHERE project_id = ?"
        params = [project_id]
        
        if memory_type:
            query += " AND memory_type = ?"
            params.append(memory_type)
        
        if record_id:
            query += " AND record_id = ?"
            params.append(record_id)
        
        cursor.execute(query, params)
        record_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete content files
        for rid in record_ids:
            content_file = self.memory_dir / f"{rid}.mem"
            if content_file.exists():
                content_file.unlink()
        
        # Delete database records
        delete_query = "DELETE FROM memory_records WHERE project_id = ?"
        delete_params = [project_id]
        
        if memory_type:
            delete_query += " AND memory_type = ?"
            delete_params.append(memory_type)
        
        if record_id:
            delete_query += " AND record_id = ?"
            delete_params.append(record_id)
        
        cursor.execute(delete_query, delete_params)
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Deleted {deleted_count} memory records for {project_id}")
        return deleted_count
    
    async def get_memory_statistics(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Args:
            project_id: Optional project filter
            
        Returns:
            Memory statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if project_id:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(content_size) as total_size,
                    AVG(access_count) as avg_access_count,
                    memory_type,
                    COUNT(*) as type_count
                FROM memory_records 
                WHERE project_id = ?
                GROUP BY memory_type
            """, (project_id,))
        else:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(content_size) as total_size,
                    AVG(access_count) as avg_access_count,
                    memory_type,
                    COUNT(*) as type_count
                FROM memory_records 
                GROUP BY memory_type
            """)
        
        stats = {
            "total_records": 0,
            "total_size_bytes": 0,
            "avg_access_count": 0,
            "memory_types": {}
        }
        
        for row in cursor.fetchall():
            total_records, total_size, avg_access, memory_type, type_count = row
            stats["total_records"] += type_count
            stats["total_size_bytes"] += total_size or 0
            stats["memory_types"][memory_type] = {
                "count": type_count,
                "size_bytes": total_size or 0,
                "avg_access_count": avg_access or 0
            }
        
        if stats["total_records"] > 0:
            stats["avg_access_count"] = sum(
                t["avg_access_count"] * t["count"] for t in stats["memory_types"].values()
            ) / stats["total_records"]
        
        conn.close()
        return stats
    
    async def cleanup_expired_memories(self) -> int:
        """Clean up expired memory records."""
        return await self._cleanup_expired_memories()
    
    async def _cleanup_expired_memories(self) -> int:
        """Internal method to clean up expired memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Find expired records
        cursor.execute("""
            SELECT record_id FROM memory_records 
            WHERE expires_at IS NOT NULL AND expires_at <= ?
        """, (datetime.now(),))
        
        expired_record_ids = [row[0] for row in cursor.fetchall()]
        
        # Delete content files
        for record_id in expired_record_ids:
            content_file = self.memory_dir / f"{record_id}.mem"
            if content_file.exists():
                content_file.unlink()
        
        # Delete database records
        cursor.execute("""
            DELETE FROM memory_records 
            WHERE expires_at IS NOT NULL AND expires_at <= ?
        """, (datetime.now(),))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} expired memory records")
        
        return deleted_count
    
    def _generate_scope_id(self, project_path: str) -> str:
        """Generate a unique scope identifier."""
        abs_path = Path(project_path).resolve()
        return hashlib.md5(str(abs_path).encode()).hexdigest()
    
    def _generate_record_id(self, project_id: str, memory_type: str, content: Any) -> str:
        """Generate a unique record identifier."""
        content_str = str(content) if not isinstance(content, (bytes, str)) else str(content)
        combined = f"{project_id}:{memory_type}:{content_str}:{datetime.now().isoformat()}"
        return hashlib.sha256(combined.encode()).hexdigest()[:32]
    
    def _get_default_retention_policy(self, isolation_level: str) -> Dict[str, Any]:
        """Get default retention policy for isolation level."""
        policies = {
            "project": {
                "default_ttl_hours": 24 * 30,  # 30 days
                "max_records_per_type": 1000,
                "cleanup_interval_hours": 24,
                "compression_enabled": True
            },
            "user": {
                "default_ttl_hours": 24 * 7,  # 7 days
                "max_records_per_type": 500,
                "cleanup_interval_hours": 12,
                "compression_enabled": True
            },
            "global": {
                "default_ttl_hours": 24 * 3,  # 3 days
                "max_records_per_type": 100,
                "cleanup_interval_hours": 6,
                "compression_enabled": True
            }
        }
        
        return policies.get(isolation_level, policies["project"])
    
    def _serialize_content(self, content: Any) -> bytes:
        """Serialize content for storage."""
        try:
            if isinstance(content, (str, int, float, bool)):
                return json.dumps(content).encode()
            else:
                return pickle.dumps(content)
        except Exception as e:
            logger.warning(f"Could not serialize content: {e}")
            return str(content).encode()
    
    async def _load_content_from_file(self, record_id: str, compression_used: bool) -> Any:
        """Load content from storage file."""
        content_file = self.memory_dir / f"{record_id}.mem"
        
        if not content_file.exists():
            raise FileNotFoundError(f"Memory content file not found: {record_id}")
        
        with open(content_file, 'rb') as f:
            data = f.read()
        
        if compression_used:
            data = gzip.decompress(data)
        
        # Try to deserialize
        try:
            # Try JSON first
            return json.loads(data.decode())
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Try pickle
                return pickle.loads(data)
            except Exception:
                # Fall back to string
                return data.decode('utf-8', errors='ignore')

# Global memory persistence instance
_memory_persistence = None

async def get_memory_persistence() -> MemoryPersistence:
    """Get the global memory persistence instance."""
    global _memory_persistence
    if _memory_persistence is None:
        _memory_persistence = MemoryPersistence()
        await _memory_persistence.initialize()
    return _memory_persistence

# Convenience functions
async def store_project_memory(
    project_id: str,
    memory_type: str,
    content: Any,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store memory for a project."""
    persistence = await get_memory_persistence()
    return await persistence.store_memory(project_id, memory_type, content, metadata)

async def retrieve_project_memory(
    project_id: str,
    memory_type: Optional[str] = None
) -> List[MemoryRecord]:
    """Retrieve memory for a project."""
    persistence = await get_memory_persistence()
    return await persistence.retrieve_memory(project_id, memory_type)

async def create_memory_scope(project_path: str) -> MemoryScope:
    """Create a memory scope for a project."""
    persistence = await get_memory_persistence()
    return await persistence.create_scope(project_path)

if __name__ == "__main__":
    # Example usage
    async def main():
        persistence = MemoryPersistence()
        await persistence.initialize()
        
        # Create scope for current project
        scope = await persistence.create_scope(".", "project")
        print(f"Created scope: {scope.scope_id}")
        
        # Store some memory
        record_id = await persistence.store_memory(
            scope.scope_id,
            "ai_context",
            {"current_task": "testing", "preferences": {"style": "clean"}},
            {"source": "ai_assistant"}
        )
        print(f"Stored memory: {record_id}")
        
        # Retrieve memory
        records = await persistence.retrieve_memory(scope.scope_id, "ai_context")
        print(f"Retrieved {len(records)} records")
        
        # Get statistics
        stats = await persistence.get_memory_statistics(scope.scope_id)
        print(f"Memory stats: {stats}")
    
    asyncio.run(main()) 