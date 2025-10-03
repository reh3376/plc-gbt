# File Storage System - Quick Start Guide

## 🚀 Quick Setup (5 Minutes)

### Step 1: Ensure PostgreSQL is Running

```bash
# Check if PostgreSQL is running
pg_isready

# Or check the status
brew services list | grep postgresql  # macOS
sudo systemctl status postgresql      # Linux
```

### Step 2: Create Database (if not exists)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE plc_gbt;

# Create user (if needed)
CREATE USER plc_gbt_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE plc_gbt TO plc_gbt_user;

\q
```

### Step 3: Set Environment Variables

```bash
# Add to your .env file in plc-gbt-stack/
cat >> .env << 'EOF'

# File Storage Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/plc_gbt
FILE_STORAGE_ROOT=./file-storage

# Or use individual components
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=plc_gbt
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
EOF
```

### Step 4: Install Python Dependencies

```bash
cd plc-gbt-stack/api

# Install psycopg2 (PostgreSQL adapter)
pip install psycopg2-binary

# Or add to requirements.txt and install all
echo "psycopg2-binary>=2.9.9" >> requirements.txt
pip install -r requirements.txt
```

### Step 5: Initialize the System

```bash
# Run complete initialization
python cli/init_file_storage.py --all

# This will:
# ✓ Create database schema (tables, indexes, views, functions)
# ✓ Create default folder structure
# ✓ Generate README files
# ✓ Verify setup
# ✓ Show storage statistics
```

### Step 6: Verify Installation

```bash
# Verify the structure was created
python cli/init_file_storage.py --verify

# Expected output:
# Structure completion: 100.0%
# Existing folders: 40/40
# ✓ File structure is complete
```

## 📁 What You Get

After initialization, you'll have:

### 1. Database Schema
- **8 tables**: files, folders, file_categories, file_versions, file_access_log, file_shares, file_tags
- **2 views**: active_files, file_storage_stats
- **3 functions**: get_folder_hierarchy, calculate_folder_size, search_files
- **15+ indexes**: For optimal query performance

### 2. Default Folder Structure
```
/
├── projects/              # Your PLC projects
├── plc-programs/         # PLC program files (.acd, .l5x)
├── control-loops/        # PID configurations
├── workflows/            # N8N automation workflows
├── documentation/        # Manuals, specs, procedures
├── chat-histories/       # AI Assistant conversations
├── configurations/       # System configs
├── data/                 # Exports, reports, backups
├── uploads/              # Temporary uploads
├── scripts/              # Utility scripts
└── training-data/        # AI training datasets
```

### 3. README Files
Each folder includes a README explaining its purpose and usage.

## 🧪 Test the System

### Test 1: Upload a File

```python
from pathlib import Path
from api.services.file_storage_service import FileStorageService

# Initialize service
storage = FileStorageService(
    db_connection_string="postgresql://postgres:postgres@localhost:5432/plc_gbt",
    storage_root=Path("./file-storage")
)

# Upload a test file
test_content = b"Hello, PLC-GBT File Storage!"
file_record = storage.upload_file(
    file_content=test_content,
    filename="test.txt",
    folder_path="/uploads",
    created_by="test_user",
    description="Test file upload"
)

print(f"✓ File uploaded: {file_record['id']}")
print(f"  Path: {file_record['storage_path']}")
print(f"  Size: {file_record['file_size']} bytes")
print(f"  Checksum: {file_record['checksum']}")
```

### Test 2: Download the File

```python
# Download the file
content, metadata = storage.download_file(
    file_id=file_record['id'],
    user_id="test_user"
)

print(f"✓ File downloaded: {metadata['name']}")
print(f"  Content: {content.decode('utf-8')}")
```

### Test 3: List Files

```python
# List all files in uploads
files = storage.list_files(folder_path="/uploads", limit=10)

print(f"✓ Found {len(files)} files in /uploads")
for f in files:
    print(f"  - {f['name']} ({f['file_size']} bytes)")
```

### Test 4: Search Files

```python
# Search for files
results = storage.search_files(search_query="test", limit=10)

print(f"✓ Search found {len(results)} results")
for r in results:
    print(f"  - {r['name']} (rank: {r['rank']:.4f})")
```

### Test 5: Get Statistics

```python
# Get storage stats
stats = storage.get_storage_stats()

print(f"✓ Storage Statistics:")
print(f"  Total files: {stats['total_files']}")
print(f"  Total size: {stats['total_size']:,} bytes")
```

## 🔧 CLI Commands

### Initialize Database Only
```bash
python cli/init_file_storage.py --init-db
```

### Initialize Folder Structure Only
```bash
python cli/init_file_storage.py --init-structure
```

### Force Recreate Structure
```bash
python cli/init_file_storage.py --init-structure --force
```

### Verify Setup
```bash
python cli/init_file_storage.py --verify
```

### Show Statistics
```bash
python cli/init_file_storage.py --stats
```

### Custom Schema File
```bash
python cli/init_file_storage.py --init-db \
  --schema-file ./custom-schema.sql
```

### Custom Storage Root
```bash
python cli/init_file_storage.py --all \
  --storage-root /var/plc-gbt/storage
```

## 🐛 Troubleshooting

### Issue: "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### Issue: "Could not connect to PostgreSQL"
```bash
# Check if PostgreSQL is running
pg_isready

# Check connection settings
echo $DATABASE_URL

# Test connection manually
psql -U postgres -d plc_gbt -c "SELECT version();"
```

### Issue: "Permission denied" on storage directory
```bash
# Create directory with proper permissions
mkdir -p ./file-storage
chmod 755 ./file-storage
```

### Issue: "Folder already exists" errors
```bash
# Force recreate with --force flag
python cli/init_file_storage.py --init-structure --force
```

## 📚 Next Steps

1. **Integrate with Backend API**
   - Add file upload/download endpoints
   - Create file browser API
   - Implement file search endpoint

2. **Update Frontend**
   - Connect file explorer to new storage system
   - Add file upload drag-and-drop
   - Implement file preview

3. **Add Advanced Features**
   - File versioning UI
   - Collaborative file editing
   - Share links generation

4. **Production Deployment**
   - Configure cloud storage backend (S3/Azure)
   - Set up automated backups
   - Implement CDN for file delivery

## 📖 Full Documentation

See `FILE_STORAGE_SYSTEM.md` for complete documentation including:
- Architecture details
- API reference
- Security features
- Performance optimization
- Migration strategies

## 💡 Pro Tips

1. **Regular Backups**
   ```bash
   # Backup database
   pg_dump plc_gbt > backup-$(date +%Y%m%d).sql
   
   # Backup files
   tar -czf storage-backup-$(date +%Y%m%d).tar.gz ./file-storage
   ```

2. **Monitor Storage**
   ```bash
   # Check storage usage
   python cli/init_file_storage.py --stats
   ```

3. **Clean Old Versions**
   ```sql
   -- Keep only last 5 versions of each file
   DELETE FROM file_versions 
   WHERE version_number < (
     SELECT MAX(version_number) - 4 
     FROM file_versions fv2 
     WHERE fv2.file_id = file_versions.file_id
   );
   ```

## 🎉 Success!

You now have a production-ready file storage system with:
- ✅ PostgreSQL metadata management
- ✅ Filesystem storage
- ✅ Version control
- ✅ Access control
- ✅ Full-text search
- ✅ Audit logging
- ✅ Professional folder structure

Ready to build amazing industrial automation tools! 🚀

