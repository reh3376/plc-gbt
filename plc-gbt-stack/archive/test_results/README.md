# Archived Test Results

This directory contains historical test results that have been archived to keep the main results directories manageable.

## Directory Structure

### 📁 2025/
Current year test results organized by type:

#### phase_tests/
- Older phase-specific test results (Phase 3, 8, 10, 11, 37, 39)
- Kept latest 3 results per phase in main directories
- Files follow pattern: `phase{N}_*_test_results_*.json`

#### integration_tests/
- ETL pipeline test results
- Neo4j schema test results  
- Phase 3 missing tasks test results
- General integration test outputs

#### e2e_tests/
- Comprehensive end-to-end test results
- Full system validation test outputs

### 📁 legacy/
Pre-2025 test results (currently empty)

## Archive Policy

- **Phase Tests**: Latest 3 results kept in `results/phase*/`, older ones archived here
- **Integration Tests**: All historical results archived
- **E2E Tests**: Comprehensive test results archived after analysis

## File Naming Convention

Test result files typically include:
- Test type (phase, integration, e2e)
- Component or phase number
- Timestamp (YYYYMMDD_HHMMSS)
- Description

Example: `phase8_day4_final_test_results_20250703_190011.json`

## Accessing Archived Results

To view a test result:
```bash
# View formatted JSON
jq . archive/test_results/2025/phase_tests/phase8_day4_final_test_results_20250703_190011.json

# Search for specific test outcomes
grep -i "failed" archive/test_results/2025/*/*.json
```

## Important Notes

1. These results are historical records - do not modify
2. Use for debugging, regression analysis, or audit purposes
3. Compare with current results to track improvements
4. Consider compression if archive grows too large 