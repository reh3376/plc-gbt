# PLC-GBT File Storage System

## Overview

The PLC-GBT File Storage System is a production-ready, enterprise-grade file management solution that combines PostgreSQL for metadata management with filesystem storage for file content. This hybrid approach provides the best of both worlds: database-backed queries and efficient file storage.

## Architecture

### Components

1. **PostgreSQL Database**
   - File metadata storage
   - Hierarchical folder structure
   - Version control tracking
   - Access control and permissions
   - Full-text search capabilities
   - Audit logging

2. **Filesystem Storage**
   - Actual file content storage
   - Organized by category
   - Supports local, S3, Azure storage backends
   - Checksums for integrity verification

3. **Python Service Layer**
   - `FileStorageService` - Core storage operations
   - `FileStructureInitializer` - Default structure setup
   - Transaction-safe operations
   - Comprehensive error handling

## Database Schema

### Main Tables

#### `files`
Stores file metadata with version control and soft delete support.

Key features:
- UUID-based file identification
- Storage path and checksum tracking
- Version control (parent_version_id, version)
- Access control (permissions JSONB)
- Audit fields (created_by, accessed_at, access_count)
- Soft delete (deleted_at, deleted_by)
- Full-text search index

#### `folders`
Hierarchical folder structure with path-based lookups.

Key features:
- UUID-based folder identification
- Parent-child relationships
- Full path for quick lookups
- System folders (cannot be deleted)
- JSONB permissions
- Soft delete support

#### `file_categories`
Predefined categories for organizing files.

Default categories:
- `plc-programs` - PLC program files (.acd, .l5x)
- `workflows` - Automation workflow definitions
- `chat-histories` - AI Assistant conversation histories
- `documentation` - Documentation and guides
- `configurations` - System configuration files
- `exports` - Exported data and reports
- `uploads` - User uploaded files
- `projects` - Project files and archives

#### `file_versions`
Version history for files.

Key features:
- Links to parent file
- Version number tracking
- Separate storage path per version
- Change descriptions

#### `file_access_log`
Audit trail of all file operations.

Key features:
- Tracks read, write, delete, download, upload actions
- IP address and user agent logging
- Success/failure tracking
- Error message storage

#### `file_shares`
File sharing and collaboration.

Key features:
- Unique share tokens
- Expiration dates
- Access limits
- Permission control

### Views

#### `active_files`
Shows all non-deleted files with category and folder information.

#### `file_storage_stats`
Aggregates storage statistics by category.

### Functions

#### `get_folder_hierarchy(folder_uuid)`
Returns hierarchical folder tree starting from a given folder.

#### `calculate_folder_size(folder_uuid)`
Calculates total size of all files in a folder and its subfolders.

#### `search_files(search_query, category_filter, tag_filter, limit_results)`
Full-text search with filtering and relevance ranking.

## Default File Structure

The system automatically creates a professional folder structure:

```
/
├── projects/
│   ├── active/              # Current working projects
│   ├── templates/           # Project templates
│   └── archived/            # Completed projects
├── plc-programs/
│   ├── rockwell/
│   │   ├── logix-5000/
│   │   └── rslogix-500/
│   ├── siemens/
│   │   ├── s7-1200/
│   │   └── s7-1500/
│   ├── codesys/
│   └── other/
├── control-loops/
│   ├── temperature/
│   ├── flow/
│   ├── pressure/
│   ├── level/
│   ├── cascade/
│   └── tuning-logs/
├── workflows/
│   ├── n8n/
│   └── custom/
├── documentation/
│   ├── manuals/
│   ├── specifications/
│   ├── procedures/
│   └── diagrams/
├── chat-histories/          # AI Assistant conversations
├── configurations/
│   ├── devices/
│   ├── networks/
│   └── system/
├── data/
│   ├── exports/
│   │   ├── csv/
│   │   ├── json/
│   │   └── excel/
│   ├── reports/
│   │   ├── performance/
│   │   └── compliance/
│   └── backups/
├── uploads/                 # Temporary user uploads
├── scripts/
│   ├── python/
│   ├── javascript/
│   └── utilities/
└── training-data/
    ├── fine-tuning/
    └── validation/
```

## Installation & Setup

### 1. Initialize Database Schema

```bash
cd plc-gbt-stack/api
python cli/init_file_storage.py --init-db
```

This creates all tables, indexes, views, and functions in PostgreSQL.

### 2. Initialize Default Folder Structure

```bash
python cli/init_file_storage.py --init-structure
```

This creates the default folder hierarchy and README files.

### 3. Run All Initialization Steps

```bash
python cli/init_file_storage.py --all
```

### 4. Verify Installation

```bash
python cli/init_file_storage.py --verify
```

### 5. View Storage Statistics

```bash
python cli/init_file_storage.py --stats
```

## Configuration

### Environment Variables

```bash
# PostgreSQL Connection (Option 1: Full URL)
DATABASE_URL=postgresql://user:password@localhost:5432/plc_gbt

# PostgreSQL Connection (Option 2: Individual components)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=plc_gbt
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# File Storage Root Directory
FILE_STORAGE_ROOT=/path/to/storage
```

## Usage Examples

### Python API

```python
from pathlib import Path
from api.services.file_storage_service import FileStorageService

# Initialize service
storage_service = FileStorageService(
    db_connection_string="postgresql://user:pass@localhost:5432/plc_gbt",
    storage_root=Path("/var/plc-gbt/storage")
)

# Upload a file
file_content = b"PLC program content..."
file_record = storage_service.upload_file(
    file_content=file_content,
    filename="main.acd",
    folder_path="/plc-programs/rockwell/logix-5000",
    category_name="plc-programs",
    created_by="user@example.com",
    description="Main PLC program",
    tags=["production", "distillation"],
    metadata={"plc_type": "ControlLogix", "processor": "1756-L85E"}
)

# Download a file
content, metadata = storage_service.download_file(
    file_id=file_record['id'],
    user_id="user@example.com"
)

# List files in a folder
files = storage_service.list_files(
    folder_path="/plc-programs/rockwell",
    category_name="plc-programs",
    limit=50
)

# Search files
results = storage_service.search_files(
    search_query="distillation temperature control",
    limit=20
)

# Get storage statistics
stats = storage_service.get_storage_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size']} bytes")
```

### Create Custom Folders

```python
# Create a project folder
folder = storage_service.create_folder(
    name="Distillation-Upgrade-2025",
    parent_path="/projects/active",
    category_name="projects",
    created_by="engineer@company.com",
    description="Distillation column control system upgrade",
    metadata={"budget": "50000", "deadline": "2025-12-31"}
)
```

### File Versioning

```python
# Upload new version of existing file
# The service automatically handles version tracking
updated_file = storage_service.upload_file(
    file_content=updated_content,
    filename="main.acd",  # Same filename
    folder_path="/plc-programs/rockwell/logix-5000",  # Same location
    created_by="user@example.com",
    description="Updated PLC logic for safety improvements",
    metadata={"change_order": "CO-2025-001"}
)
# This creates a new version linked to the original
```

## Security Features

### Access Control

Files and folders have JSONB permissions:

```json
{
  "read": ["*"],           // Everyone can read
  "write": ["owner", "admin"],  // Only owner and admin can write
  "delete": ["admin"]      // Only admin can delete
}
```

### Audit Logging

All file operations are logged to `file_access_log`:
- User identification
- Action type (read, write, delete, download, upload)
- Timestamp
- Success/failure status
- IP address and user agent
- Metadata

### File Integrity

- SHA-256 checksums for all files
- Automatic verification on download
- Corruption detection

### Soft Deletes

Files are soft-deleted by default:
- `deleted_at` timestamp set
- File remains in database
- Can be restored
- Hard delete requires explicit flag

## Performance Optimization

### Indexes

The schema includes comprehensive indexes:
- GIN indexes for full-text search
- B-tree indexes for common queries
- Partial indexes for soft-deleted records

### Query Optimization

```sql
-- Fast folder listing
SELECT * FROM active_files WHERE folder_id = $1;

-- Efficient search
SELECT * FROM search_files('temperature control', NULL, NULL, 100);

-- Folder size calculation
SELECT calculate_folder_size('folder-uuid-here');
```

### Caching Strategy

Recommended caching layers:
1. **Redis** - File metadata cache (5-minute TTL)
2. **CDN** - Static file content
3. **Application** - Folder structure cache

## Migration Path

### Future Enhancements

The system is designed to support:

1. **Cloud Storage Integration**
   - S3-compatible storage
   - Azure Blob Storage
   - Google Cloud Storage

2. **Advanced Features**
   - File locking/checkout
   - Collaborative editing
   - Thumbnail generation
   - Preview rendering

3. **Scalability**
   - Horizontal scaling
   - Read replicas
   - Sharding strategies

## Maintenance

### Backup Strategy

```bash
# Backup database
pg_dump -h localhost -U postgres plc_gbt > backup.sql

# Backup file storage
tar -czf storage-backup.tar.gz /path/to/storage
```

### Cleanup Old Versions

```sql
-- Delete file versions older than 90 days
DELETE FROM file_versions 
WHERE created_at < NOW() - INTERVAL '90 days'
  AND version_number < (
    SELECT MAX(version_number) FROM file_versions fv2 
    WHERE fv2.file_id = file_versions.file_id
  );
```

### Hard Delete Soft-Deleted Files

```sql
-- Hard delete files soft-deleted over 30 days ago
DELETE FROM files 
WHERE deleted_at < NOW() - INTERVAL '30 days';
```

## Troubleshooting

### Issue: Files not appearing in file explorer

**Solution**: Verify folder structure and refresh cache
```bash
python cli/init_file_storage.py --verify
```

### Issue: Checksum mismatch errors

**Solution**: File corruption detected, restore from backup
```python
# Verify file integrity
storage_service.download_file(file_id)  # Raises error if corrupted
```

### Issue: Slow search performance

**Solution**: Rebuild full-text search index
```sql
REINDEX INDEX idx_files_search;
VACUUM ANALYZE files;
```

## API Reference

See `plc-gbt-stack/api/services/file_storage_service.py` for complete API documentation.

## Contributing

When adding new features:
1. Update database schema
2. Add migration script
3. Update this documentation
4. Add unit tests
5. Update API client

## License

Copyright © 2025 PLC-GBT. All rights reserved.

