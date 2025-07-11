# PLC-GBT Archive Directory

This archive directory contains files that are not actively used but are preserved for historical reference, debugging, or potential future use.

## 📁 Directory Structure

```
archive/
├── backups/              # System backups and database dumps
│   ├── postgres/         # PostgreSQL backups
│   ├── neo4j/           # Neo4j graph database backups
│   ├── sessions/        # Session state backups
│   └── scripts/         # Backup-related scripts
├── test_results/        # Historical test results
│   ├── 2025/           # Current year results
│   │   ├── phase_tests/     # Phase-specific test results
│   │   ├── integration_tests/ # Integration test results
│   │   └── e2e_tests/       # End-to-end test results
│   └── legacy/         # Pre-2025 test results
├── sessions/           # Historical session data
│   ├── 2025/          # Current year sessions
│   │   ├── ingestion/      # Data ingestion sessions
│   │   └── curation/       # Data curation sessions
│   └── legacy/        # Pre-2025 sessions
├── validation_reports/ # Historical validation reports
│   └── 2025/          # Current year reports
└── misc/              # Miscellaneous archived files
    ├── temporary/     # Temporary files preserved for reference
    └── deprecated/    # Deprecated code and configurations
```

## 📋 Archive Policy

### Retention Rules
- **Test Results**: Keep latest 3 results per phase, archive older ones here
- **Session Files**: Keep latest 5 ingestion sessions, 3 curation sessions in main directories
- **Backups**: All backups are preserved indefinitely
- **Validation Reports**: Keep reports referenced in documentation

### File Naming
- Original filenames are preserved
- Files without dates get prefixed with archive date: `YYYY-MM-DD_filename`
- Session IDs and timestamps are preserved

## 🔍 Finding Archived Files

### By Date
Files are organized by year and type. Check the appropriate year subdirectory.

### By Type
- Database backups: `backups/{database_type}/`
- Test results: `test_results/{year}/{test_type}/`
- Session data: `sessions/{year}/{session_type}/`

### By Phase
Phase-specific content is in `test_results/{year}/phase_tests/`

## 🔄 Restoration

To restore an archived file:
1. Copy (don't move) the file from archive to its original location
2. Update any references or imports if needed
3. Test functionality before removing from archive

## 📝 Archive Log

### 2025-01-17
- Initial archive structure created
- Moved ~150 files from active directories
- Organized by type and date
- Created comprehensive documentation

## ⚠️ Important Notes

1. **DO NOT DELETE** files from archive without team approval
2. **ALWAYS COPY** when restoring (keep archive copy)
3. **UPDATE THIS README** when adding new archive categories
4. **CHECK REFERENCES** before archiving active files

## 🔗 Related Documentation

- [Codebase Organization Summary](../CODEBASE_ORGANIZATION_SUMMARY.md)
- [Archive Plan](../ARCHIVE_PLAN.md)
- [Roadmap](../../docs/roadmap.md) 