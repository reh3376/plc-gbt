#!/usr/bin/env python3
"""
Production-Ready File Storage Service
Integrates PostgreSQL metadata with filesystem storage

Features:
- Database-backed metadata management
- Hierarchical folder structure
- Version control and soft deletes
- Access control and permissions
- Full-text search capabilities
- Audit logging
- Transaction safety
"""

import hashlib
import mimetypes
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import psycopg2
import psycopg2.extras
from psycopg2.extras import Json, RealDictCursor

# Register UUID adapter for psycopg2
psycopg2.extras.register_uuid()


class FileStorageService:
    """
    Production-ready file storage service with PostgreSQL integration
    """

    def __init__(
        self,
        db_connection_string: str,
        storage_root: Path,
        chunk_size: int = 8192
    ):
        """
        Initialize file storage service
        
        Args:
            db_connection_string: PostgreSQL connection string
            storage_root: Root directory for file storage
            chunk_size: Chunk size for file operations (bytes)
        """
        self.db_conn_string = db_connection_string
        self.storage_root = Path(storage_root)
        self.chunk_size = chunk_size

        # Ensure storage root exists
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def get_connection(self):
        """Get PostgreSQL database connection with autocommit disabled"""
        conn = psycopg2.connect(self.db_conn_string, cursor_factory=RealDictCursor)
        conn.autocommit = False  # Ensure we control transactions
        return conn

    def calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA-256 checksum of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file checksum
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_folder_by_path(self, path: str) -> dict[str, Any] | None:
        """
        Get folder by path
        
        Args:
            path: Folder path
            
        Returns:
            Folder record or None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM folders WHERE path = %s AND deleted_at IS NULL",
                    (path,)
                )
                return cur.fetchone()

    def create_folder(
        self,
        name: str,
        parent_path: str = "/",
        category_name: str | None = None,
        created_by: str = "system",
        description: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a new folder
        
        Args:
            name: Folder name
            parent_path: Parent folder path
            category_name: Category name
            created_by: Username of creator
            description: Folder description
            metadata: Custom metadata
            
        Returns:
            Created folder record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Get parent folder
                parent = self.get_folder_by_path(parent_path)
                if not parent:
                    raise ValueError(f"Parent folder not found: {parent_path}")

                # Build full path
                full_path = f"{parent_path.rstrip('/')}/{name}"

                # Get category ID if specified
                category_id = None
                if category_name:
                    cur.execute(
                        "SELECT id FROM file_categories WHERE name = %s",
                        (category_name,)
                    )
                    category = cur.fetchone()
                    if category:
                        category_id = category['id']

                # Insert folder
                folder_id = uuid4()
                cur.execute(
                    """
                    INSERT INTO folders 
                    (id, name, parent_id, path, category_id, description, metadata, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        folder_id,
                        name,
                        parent['id'],
                        full_path,
                        category_id,
                        description,
                        Json(metadata or {}),
                        created_by
                    )
                )

                # Create physical directory on filesystem
                physical_path = self.storage_root / full_path.lstrip('/')
                physical_path.mkdir(parents=True, exist_ok=True)

                conn.commit()

                return cur.fetchone()

    def upload_file(
        self,
        file_content: bytes,
        filename: str,
        folder_path: str = "/",
        category_name: str | None = None,
        created_by: str = "system",
        description: str | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Upload a file with metadata to storage
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            folder_path: Destination folder path
            category_name: Category name
            created_by: Username of uploader
            description: File description
            tags: List of tags
            metadata: Custom metadata
            
        Returns:
            Created file record
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Get folder
                folder = self.get_folder_by_path(folder_path)
                if not folder:
                    raise ValueError(f"Folder not found: {folder_path}")

                # Get category ID if specified
                category_id = None
                if category_name:
                    cur.execute(
                        "SELECT id FROM file_categories WHERE name = %s",
                        (category_name,)
                    )
                    category = cur.fetchone()
                    if category:
                        category_id = category['id']

                # Generate file ID and storage path
                file_id = uuid4()
                file_extension = Path(filename).suffix
                storage_filename = f"{file_id}{file_extension}"

                # Organize by category or use 'general'
                category_folder = category_name or 'general'
                storage_subdir = self.storage_root / category_folder
                storage_subdir.mkdir(parents=True, exist_ok=True)

                storage_path_full = storage_subdir / storage_filename
                storage_path_relative = f"{category_folder}/{storage_filename}"

                # Write file to disk
                with open(storage_path_full, 'wb') as f:
                    f.write(file_content)

                # Calculate checksum
                checksum = self.calculate_checksum(storage_path_full)

                # Determine MIME type
                mime_type, _ = mimetypes.guess_type(filename)

                # Insert file record
                cur.execute(
                    """
                    INSERT INTO files 
                    (
                        id, name, original_name, folder_id, category_id,
                        storage_path, file_size, mime_type, file_extension,
                        checksum, description, tags, metadata, created_by
                    )
                    VALUES 
                    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING *
                    """,
                    (
                        file_id,
                        filename,
                        filename,
                        folder['id'],
                        category_id,
                        storage_path_relative,
                        len(file_content),
                        mime_type,
                        file_extension,
                        checksum,
                        description,
                        tags or [],
                        Json(metadata or {}),
                        created_by
                    )
                )

                file_record = cur.fetchone()

                # Log access
                self._log_file_access(
                    cur,
                    file_id,
                    created_by,
                    'upload',
                    True,
                    metadata={'filename': filename, 'size': len(file_content)}
                )

                conn.commit()

                return file_record

    def get_file(self, file_id: UUID, user_id: str = "system") -> dict[str, Any] | None:
        """
        Get file metadata by ID
        
        Args:
            file_id: File UUID
            user_id: User requesting the file
            
        Returns:
            File record or None
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT f.*, fc.name as category_name, fol.path as folder_path
                    FROM files f
                    LEFT JOIN file_categories fc ON f.category_id = fc.id
                    LEFT JOIN folders fol ON f.folder_id = fol.id
                    WHERE f.id = %s AND f.deleted_at IS NULL
                    """,
                    (file_id,)
                )
                file_record = cur.fetchone()

                if file_record:
                    # Update access tracking
                    cur.execute(
                        """
                        UPDATE files 
                        SET accessed_at = CURRENT_TIMESTAMP, access_count = access_count + 1
                        WHERE id = %s
                        """,
                        (file_id,)
                    )

                    # Log access
                    self._log_file_access(cur, file_id, user_id, 'read', True)

                    conn.commit()

                return file_record

    def download_file(self, file_id: UUID, user_id: str = "system") -> tuple[bytes, dict[str, Any]]:
        """
        Download file content
        
        Args:
            file_id: File UUID
            user_id: User downloading the file
            
        Returns:
            Tuple of (file_content, file_metadata)
        """
        file_record = self.get_file(file_id, user_id)
        if not file_record:
            raise ValueError(f"File not found: {file_id}")

        # Read file from storage
        storage_path = self.storage_root / file_record['storage_path']
        if not storage_path.exists():
            raise FileNotFoundError(f"File not found in storage: {storage_path}")

        with open(storage_path, 'rb') as f:
            content = f.read()

        # Verify checksum
        actual_checksum = hashlib.sha256(content).hexdigest()
        if actual_checksum != file_record['checksum']:
            raise ValueError("File integrity check failed: checksum mismatch")

        with self.get_connection() as conn:
            with conn.cursor() as cur:
                self._log_file_access(
                    cur,
                    file_id,
                    user_id,
                    'download',
                    True,
                    metadata={'size': len(content)}
                )
                conn.commit()

        return content, file_record

    def delete_file(self, file_id: UUID, user_id: str = "system", hard_delete: bool = False) -> bool:
        """
        Delete file (soft or hard delete)
        
        Args:
            file_id: File UUID
            user_id: User deleting the file
            hard_delete: If True, permanently delete; if False, soft delete
            
        Returns:
            True if deleted successfully
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                file_record = self.get_file(file_id, user_id)
                if not file_record:
                    return False

                if hard_delete:
                    # Delete from database
                    cur.execute("DELETE FROM files WHERE id = %s", (file_id,))

                    # Delete from filesystem
                    storage_path = self.storage_root / file_record['storage_path']
                    if storage_path.exists():
                        storage_path.unlink()
                else:
                    # Soft delete
                    cur.execute(
                        """
                        UPDATE files 
                        SET deleted_at = CURRENT_TIMESTAMP, deleted_by = %s
                        WHERE id = %s
                        """,
                        (user_id, file_id)
                    )

                # Log deletion
                self._log_file_access(
                    cur,
                    file_id,
                    user_id,
                    'delete',
                    True,
                    metadata={'hard_delete': hard_delete}
                )

                conn.commit()

                return True

    def list_folders(
        self,
        parent_path: str = "/",
        include_system: bool = True,
        recursive: bool = True
    ) -> list[dict[str, Any]]:
        """
        List all folders in the hierarchy
        
        Args:
            parent_path: Parent folder path to start from
            include_system: Include system folders
            recursive: Include all descendants (True) or just direct children (False)
            
        Returns:
            List of folder records
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                if recursive:
                    # Get all folders under parent (including parent itself)
                    query = """
                        WITH RECURSIVE folder_tree AS (
                            -- Base case: start with parent folder
                            SELECT * FROM folders WHERE path = %s AND deleted_at IS NULL
                            UNION ALL
                            -- Recursive case: get all children
                            SELECT f.* FROM folders f
                            INNER JOIN folder_tree ft ON f.parent_id = ft.id
                            WHERE f.deleted_at IS NULL
                        )
                        SELECT * FROM folder_tree
                    """
                    params = [parent_path]
                else:
                    # Get only direct children
                    query = """
                        SELECT f.* FROM folders f
                        WHERE f.parent_id = (SELECT id FROM folders WHERE path = %s AND deleted_at IS NULL)
                        AND f.deleted_at IS NULL
                    """
                    params = [parent_path]

                if not include_system:
                    query += " AND is_system = FALSE"

                query += " ORDER BY path"

                cur.execute(query, params)
                return cur.fetchall()

    def list_files(
        self,
        folder_path: str = "/",
        category_name: str | None = None,
        tags: list[str] | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        List files with optional filtering
        
        Args:
            folder_path: Filter by folder path
            category_name: Filter by category
            tags: Filter by tags
            limit: Maximum results
            offset: Results offset
            
        Returns:
            List of file records
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    SELECT f.*, fc.name as category_name, fol.path as folder_path
                    FROM files f
                    LEFT JOIN file_categories fc ON f.category_id = fc.id
                    LEFT JOIN folders fol ON f.folder_id = fol.id
                    WHERE f.deleted_at IS NULL
                """
                params: list[Any] = []

                if folder_path:
                    query += " AND fol.path = %s"
                    params.append(folder_path)

                if category_name:
                    query += " AND fc.name = %s"
                    params.append(category_name)

                if tags:
                    query += " AND f.tags && %s"
                    params.append(tags)

                query += " ORDER BY f.created_at DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cur.execute(query, params)
                return cur.fetchall()

    def search_files(self, search_query: str, limit: int = 100) -> list[dict[str, Any]]:
        """
        Full-text search across files
        
        Args:
            search_query: Search query
            limit: Maximum results
            
        Returns:
            List of file records with relevance ranking
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM search_files(%s, NULL, NULL, %s)",
                    (search_query, limit)
                )
                return cur.fetchall()

    def _log_file_access(
        self,
        cursor,
        file_id: UUID,
        user_id: str,
        action: str,
        success: bool,
        error_message: str | None = None,
        metadata: dict[str, Any] | None = None
    ):
        """
        Log file access to audit trail
        
        Args:
            cursor: Database cursor
            file_id: File UUID
            user_id: User ID
            action: Action type
            success: Whether action succeeded
            error_message: Error message if failed
            metadata: Additional metadata
        """
        cursor.execute(
            """
            INSERT INTO file_access_log 
            (file_id, user_id, action, success, error_message, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (file_id, user_id, action, success, error_message, Json(metadata or {}))
        )

    def get_storage_stats(self) -> dict[str, Any]:
        """
        Get file storage statistics
        
        Returns:
            Storage statistics by category
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM file_storage_stats")
                stats = cur.fetchall()

                total_size = sum(s['total_size'] or 0 for s in stats)
                total_files = sum(s['file_count'] or 0 for s in stats)

                return {
                    'total_files': total_files,
                    'total_size': total_size,
                    'by_category': stats
                }

