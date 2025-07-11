# Codebase Cleanup Plan

## Task Analysis (AI Task Orchestrator)

**Task Complexity**: MODERATE
- **Files to Organize**: ~150+ files
- **Estimated Time**: 2-3 hours
- **Risk Level**: Medium (file path updates required)
- **Validation Required**: Comprehensive link and import checking

## Current State Analysis

### Files Requiring Organization

#### 1. Context/Training Data (Root Directory)
- `context_industrial_control_training_data.json`
- `context_openai_training_data.jsonl`
- `context_processing_plan.json`
- `context_training_data.json`

**Target**: `plc-gbt-stack/training_data/context/`

#### 2. Ingestion Sessions (Multiple Locations)
- Root: `ingestion_session_intelligent_*.json`
- scripts/ai: Multiple ingestion session files

**Target**: `plc-gbt-stack/results/ingestion_sessions/`

#### 3. Phase Results (Scattered)
- Root: `phase*_testing_results_*.json`
- Various phase validation files

**Target**: Consolidate in `plc-gbt-stack/results/phase*/`

#### 4. Phase Scripts (scripts/ai)
- `phase*_*.py` files (dozens of phase-specific scripts)

**Target**: `plc-gbt-stack/scripts/ai/phases/phase*/`

#### 5. Wolfram Enhancement Files
- Scripts: `wolfram_alpha_*.py`
- Results: `wolfram_enhancement_*.json`

**Target**: 
- Scripts: `plc-gbt-stack/scripts/ai/wolfram/`
- Results: `plc-gbt-stack/results/wolfram_enhancement/`

#### 6. Documentation (../docs)
- Phase completion summaries
- Context directory with industrial docs

**Target**: `plc-gbt-stack/docs/phases/`

#### 7. Duplicate Directory
- `plc-gbt-stack/plc-gbt-stack/` (nested duplicate)

**Action**: Remove after verifying contents

## Organization Structure

```
plc-gbt-stack/
├── config/
│   └── [configuration files]
├── docs/
│   ├── guides/              # Existing guides (AI_TASK_ORCHESTRATOR_GUIDE.md, etc.)
│   ├── phases/              # Phase-specific documentation
│   │   ├── phase11/
│   │   ├── phase12/
│   │   └── ...
│   └── context/             # Industrial control context docs
├── results/
│   ├── ingestion_sessions/  # All ingestion session JSONs
│   ├── phase5/
│   ├── phase6/
│   ├── phase7/
│   ├── phase8/
│   ├── phase9/
│   ├── phase10/
│   ├── phase11/
│   ├── phase12/
│   ├── phase37/
│   ├── phase38/
│   ├── phase39/
│   └── wolfram_enhancement/
├── scripts/
│   ├── ai/
│   │   ├── phases/          # Phase-specific scripts
│   │   │   ├── phase5/
│   │   │   ├── phase6/
│   │   │   ├── phase7/
│   │   │   ├── phase8/
│   │   │   ├── phase9/
│   │   │   ├── phase10/
│   │   │   └── ...
│   │   ├── wolfram/         # Wolfram integration scripts
│   │   └── [core AI scripts]
│   └── deployment/
│       └── phases/          # Phase-specific deployment scripts
└── training_data/
    ├── context/             # Context-specific training data
    └── openai/              # OpenAI fine-tuning data
```

## Execution Plan

### Step 1: Create Directory Structure
```bash
mkdir -p docs/phases/{phase5,phase6,phase7,phase8,phase9,phase10,phase11,phase12,phase37,phase38,phase39}
mkdir -p results/ingestion_sessions
mkdir -p scripts/ai/phases/{phase5,phase6,phase7,phase8,phase9,phase10,phase37,phase38,phase39}
mkdir -p scripts/ai/wolfram
mkdir -p scripts/deployment/phases
mkdir -p training_data/{context,openai}
```

### Step 2: Move Files by Category

#### Context/Training Data
```bash
mv context_*.json training_data/context/
mv context_*.jsonl training_data/openai/
```

#### Ingestion Sessions
```bash
mv ingestion_session_*.json results/ingestion_sessions/
mv scripts/ai/ingestion_session_*.json results/ingestion_sessions/
```

#### Phase Scripts
```bash
# Move phase-specific scripts to organized directories
for phase in 5 6 7 8 9 10 37 38 39; do
    mv scripts/ai/phase${phase}_*.py scripts/ai/phases/phase${phase}/
done
```

#### Wolfram Files
```bash
mv scripts/ai/wolfram_alpha_*.py scripts/ai/wolfram/
```

### Step 3: Update File References

#### Python Import Updates
- Update all imports in Python files to reflect new paths
- Search for: `from scripts.ai import`
- Replace with: `from scripts.ai.phases.phaseX import`

#### Documentation Link Updates
- Update all markdown links to reflect new structure
- Update roadmap.md references
- Update guide references

### Step 4: Validation Checklist

- [ ] All JSON files in appropriate results directories
- [ ] All phase scripts organized by phase number
- [ ] All training data in training_data directory
- [ ] All imports updated and working
- [ ] All documentation links updated
- [ ] No duplicate files or directories
- [ ] Git status shows clean organization

## Risk Mitigation

1. **Backup Current State**: Create git stash before major moves
2. **Test Imports**: Run import tests after moving files
3. **Validate Links**: Check all documentation links
4. **Incremental Commits**: Commit after each major category

## Success Criteria

- ✅ No files in root directory except essential configs
- ✅ Clear phase-based organization
- ✅ All imports and references working
- ✅ Documentation reflects new structure
- ✅ Roadmap.md updated with organization notes

---

*Following AI Task Orchestrator methodology for systematic organization* 