# Archive Plan - AI Task Orchestrator Approach

## Task Analysis
**Task Complexity**: MODERATE
- **Files to Archive**: ~150+ files
- **Archive Strategy**: Create structured archive directories preserving context
- **Risk Level**: Low (files are preserved, not deleted)

## Files Identified for Archiving

### 1. Backup Files (14 files)
**Location**: Various directories
**Target**: `archive/backups/`

- `backup/` directory contents
- `scripts/backup_neo4j_with_context.py`
- `scripts/deployment/simple_db_backup.py`
- `scripts/deployment/comprehensive_db_backup.py`
- `scripts/ai/plc_gpt_backup_20250709_151511.bundle`
- `scripts/ai/database_manager_backup_storage_fix_1752160437.py`
- `results/backups/` contents

### 2. Test Results (100+ files)
**Location**: Multiple directories
**Target**: `archive/test_results/{year}/`

#### Phase Test Results
- `results/phase*/` - older test results (keep latest 3 per phase)
- `scripts/deployment/comprehensive_test_results_*.json`
- `tests/phase3_day3_test_results_*.json`
- `scripts/ai/phase8_day4_*test_results*.json`

#### General Test Results
- `etl_pipeline_test_results.json`
- `reports/etl_pipeline_test_results.json`
- `reports/neo4j_schema_test_results.json`
- `reports/phase3_missing_tasks_test_results_*.json`

### 3. Session Files (20+ files)
**Location**: `results/`
**Target**: `archive/sessions/{year}/`

- `results/ingestion_sessions/` - keep only latest 5
- `results/interactive_curation/` - keep only latest 3
- `backup/session_*/` - all session backups

### 4. Old Validation Reports
**Location**: `results/validation-reports/`
**Target**: `archive/validation_reports/`

- Keep only reports referenced in documentation

### 5. Miscellaneous Old Files
**Location**: Various
**Target**: `archive/misc/`

- Duplicate or superseded files
- Temporary analysis files
- Old migration files

## Archive Directory Structure

```
plc-gbt-stack/
├── archive/
│   ├── README.md                    # Explains archive structure
│   ├── backups/
│   │   ├── postgres/
│   │   ├── neo4j/
│   │   ├── sessions/
│   │   └── scripts/
│   ├── test_results/
│   │   ├── 2025/
│   │   │   ├── phase_tests/
│   │   │   ├── integration_tests/
│   │   │   └── e2e_tests/
│   │   └── legacy/
│   ├── sessions/
│   │   ├── 2025/
│   │   │   ├── ingestion/
│   │   │   └── curation/
│   │   └── legacy/
│   ├── validation_reports/
│   │   └── 2025/
│   └── misc/
│       ├── temporary/
│       └── deprecated/
```

## Archive Rules

1. **Retention Policy**:
   - Keep latest 3 results per phase
   - Keep latest 5 ingestion sessions
   - Keep all backups (organized by date)
   - Keep validation reports referenced in docs

2. **Naming Convention**:
   - Preserve original filenames
   - Add date prefix if missing: `YYYY-MM-DD_original_name`

3. **Documentation**:
   - Create README.md in each archive directory
   - Document why files were archived
   - Include retrieval instructions

## Implementation Steps

1. Create archive directory structure
2. Move backup files first (least risky)
3. Archive old test results by date
4. Move session files preserving recent ones
5. Create README documentation
6. Verify no broken references
7. Update roadmap.md with archiving entry 