# Archived Backup Files

This directory contains historical backup files and backup-related scripts that are no longer actively used but preserved for reference.

## Contents

### 📁 postgres/
- PostgreSQL database backups from July 2025
- `postgres_backup_2025-07-01_11-27-01.sql` - Full database backup
- `plc_metadata_backup_2025-07-01_11-27-27.sql` - Metadata-only backup

### 📁 neo4j/
- Neo4j graph database backups and metadata
- JSON files containing backup history and configuration
- PID backup files from development sessions

### 📁 sessions/
- Session state backups from various dates
- Includes Neo4j dumps, PostgreSQL dumps, and Redis snapshots
- Session summary JSON files with backup metadata

### 📁 scripts/
- **backup_neo4j_with_context.py** - Script for Neo4j backup with context preservation
- **simple_db_backup.py** - Basic database backup utility
- **comprehensive_db_backup.py** - Full system backup with validation
- **database_manager_backup_storage_fix_*.py** - Backup storage fix scripts
- **plc_gpt_backup_*.bundle** - Git bundle backups

## Usage Notes

1. These scripts are archived but still functional
2. To use a backup script, copy (don't move) it to your working directory
3. Check for updated versions in active directories before using
4. Database backups can be restored using standard PostgreSQL/Neo4j tools

## Restoration

To restore a database backup:
```bash
# PostgreSQL
psql -U username -d database_name < backup_file.sql

# Neo4j (using cypher-shell)
cat neo4j_dump.cypher | cypher-shell -u neo4j -p password
```

**Note**: Always test restoration in a development environment first! 