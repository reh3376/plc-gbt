# PLC-GBT Functional Specification & Alignment Plan

## 1. Purpose
This functional specification establishes the action plan required to align the plc-gbt codebase with the strategic roadmap. It translates high-level goals into implementable front-end and back-end milestones, clarifies supporting documentation requirements, and defines how satellite repositories (plc-gbt-git, plc-100, plc-200, plc-300, plc-400, plc-500) will be linked for coordinated development.

## 2. Current Baseline Assessment
### 2.1 Front-end
- **Status:** Documentation-only scaffold for an Eclipse Theia workspace. No compiled extensions, build pipeline, or integration tests exist.
- **Key blockers:** Missing source code for workspace shell, extension activation, Git automation panels, and workflow visualizations. Testing framework in `ui/tests/framework` lacks a running UI target.

### 2.2 Back-end
- **Status:** FastAPI/CLI layers partially implemented. PLC format converter, workflow automation modules, and repo integration adapters remain stubs.
- **Key blockers:** Naming/import mismatches (e.g., `plc-conversion` package), unfinished PLC memory orchestration layers, absent bindings to external PLC repositories, and brittle documentation/test assets.

### 2.3 Documentation & Knowledge
- **Status:** Extensive reports exist but are redundant or outdated. Task-critical guides for PLC memory operations and workflow node creation are fragmented across summaries.
- **Key blockers:** Lack of a single canonical reference for memory operations, workflow node lifecycle, and repository integration steps.

## 3. Objectives & Success Criteria
| Objective | Success Criteria |
|-----------|------------------|
| Deliver a functional Theia-based IDE shell | Minimal application launches, supports authentication stub, exposes Git + workflow panels, and runs smoke tests |
| Stabilize backend service surface | CLI bridge imports resolve, PLC converter modules callable from FastAPI, workflow engine exposes node catalog |
| Consolidate critical documentation | PLC memory runbook and workflow node creation guide published and versioned |
| Integrate external PLC repos | Repos linked (submodules or git remotes), automated sync scripts and configuration references maintained |

Progress toward these objectives will be considered adequate when each criterion is satisfied and validated through repository tests or documented evidence.

## 4. Scope of Work
### 4.1 Front-end Deliverables
1. **Workspace shell:** Scaffold Theia application with minimal extensions (file explorer, terminal, settings, Git view).
2. **Workflow panel MVP:** Render n8n workflow overview panel reading from backend API; include mock data fallback.
3. **Git automation tools:** Implement UI entry points for plc-gbt-git workflows (trigger sync, open repo status, launch automation).
4. **Testing harness:** Activate Playwright/Jest smoke suite against workspace shell; align with CI script definitions.

### 4.2 Back-end Deliverables
1. **CLI bridge fixes:** Resolve timeout bug, align module imports, add coverage tests.
2. **PLC converter activation:** Implement minimal `convert` and `validate` flows backed by plc-gbt-git (or mock), document extension points.
3. **Workflow engine stabilization:** Define node schema registry, implement CRUD endpoints, and connect to n8n worker stubs.
4. **Memory orchestration:** Finalize PLC memory service adapters for ingestion, query, and monitoring; expose API endpoints and CLI parity tests.

### 4.3 Documentation Deliverables
- Canonical PLC memory functionality documentation (see `plc_memory_system_overview.md`).
- Workflow node creation lifecycle guide (see `workflow_node_creation_guide.md`).
- Updated architectural diagrams reflecting repo linkages and component flows.

## 5. Implementation Roadmap
| Phase | Duration | Focus | Key Artifacts |
|-------|----------|-------|---------------|
| Phase A | 2 sprints | Backend stabilization | Fixed CLI bridge, converter MVP, API test coverage |
| Phase B | 2 sprints | Front-end foundation | Theia shell, workflow panel MVP, Git UI hooks |
| Phase C | 1 sprint | Integration & sync | Repo linking scripts, CI validation across external repos |
| Phase D | Continuous | Documentation & QA | Living docs, workflow node catalog updates, smoke/perf suites |

Each phase concludes with a review checkpoint validating deliverables against success criteria.

## 6. External Repository Integration Strategy
| Repository | Purpose | Integration Approach | Owners |
|------------|---------|----------------------|--------|
| **plc-gbt-git** | PLC file conversion SDK | Add as Git submodule under `external/plc-gbt-git`; expose adapter layer in backend converter services | Backend team |
| **plc-100** | Baseline PLC ladder samples | Link via submodule; register ingestion profiles for PLC memory tests | Knowledge team |
| **plc-200** | Advanced control examples | Same as above; provide metadata for workflow demos | Knowledge team |
| **plc-300** | Safety/diagnostic PLC sets | Submodule; integrate into automated validation scenarios | QA team |
| **plc-400** | Networked PLC demos | Submodule; supply data for workflow + Git automation tests | Automation team |
| **plc-500** | Edge analytics PLC assets | Submodule; drive performance regression harness | Automation team |

Supporting tasks:
- Create `scripts/dev/link_repos.py` (or shell equivalent) to initialize/update submodules.
- Define environment variables/config entries for external repo paths.
- Update CI to fetch submodules and run targeted ingestion/conversion tests.

## 7. Risks & Mitigations
- **External repo drift:** Mitigate with version pinning via submodule commit hashes and scheduled sync reviews.
- **Theia learning curve:** Allocate spike time for extension scaffolding; adopt minimal plug-in set first.
- **Converter dependency gaps:** Use contract-first interfaces to allow mock implementations while plc-gbt-git matures.
- **Documentation rot:** Establish doc owners; enforce review in definition of done.

## 8. Validation & Reporting
- Track progress using milestone checklist; gate merges on doc/test completion.
- Provide weekly status updates summarizing front-end, back-end, and repo integration metrics.
- Audit documentation quarterly to ensure accuracy with implemented features.

## 9. Next Actions
1. Approve this FSD and assign phase leads.
2. Stand up external repo links with placeholder commit locks.
3. Begin Phase A backend stabilization tasks while documentation deliverables are finalized.
