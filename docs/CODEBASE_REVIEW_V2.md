# PLC-GBT Codebase Review (Version 2)

## Application Overview
- **Purpose.** PLC-GBT is designed to modernize programmable logic controller (PLC) engineering by combining a FastAPI automation backend, a planned Theia-based IDE, and workflow automation for PLC conversion and operations.
- **Primary goals.** Deliver a usable IDE, provide reliable PLC format conversion services, and orchestrate workflow/memory automation that coordinates multiple PLC knowledge repositories.
- **Execution status.**
  | Area | Scope | Estimated completion |
  |------|-------|----------------------|
  | Front-end | Theia workspace scaffolding and UI automation layers | ~5% (documentation and manifests only) |
  | Back-end | FastAPI CLI bridge, PLC converter package, workflow services | ~40% (CLI bridge present but broken, converter mostly stubs) |
  | Overall | Combined platform delivery | ~30% | 

## Front-end Assessment

### Implementation snapshot
- `ui/theia/workbench/package.json` outlines Theia dependencies and scripts, yet the repository lacks any TypeScript source under `ui/theia/` to produce a runnable IDE shell.
- `ui/package.json` advertises an extensive build and test pipeline (Jest, Playwright, Lighthouse), but the supporting config files and application code are absent, so none of the scripts can currently execute.

### Redundant or drifted documentation
- `ui/README.md` and `ui/docs/architecture/THEIA_ARCHITECTURE_SPECIFICATION.md` restate the same aspirational architecture; neither aligns with the empty `ui/theia/` directory. Consolidation is recommended so contributors see a single authoritative plan.
- `ui/docs/PHASE_31_TESTING_MANDATE_SUMMARY.md` and similar “phase” reports describe validations for features that do not exist, inflating perceived completeness.

### Unused or orphaned code
- The `ui/tests/framework/` directory exposes a comprehensive “User Agent Testing Framework,” but no UI exists to exercise it. Keeping the harness without an application adds maintenance cost without value.
- Several Theia extension manifests in `ui/config/` and `ui/resources/` reference assets that are not present, so enabling those extensions would fail until the assets are created.

### Key gaps to address
1. Scaffold a minimal Theia application with entrypoint TypeScript files, webpack config, and build output.
2. Provide configuration for at least one UI smoke test to validate the scaffolding.
3. Replace redundant documentation with a single living implementation plan that stays synchronized with code.

## Back-end Assessment

### Implementation snapshot
- `plc-gbt-stack/api/cli_api_bridge.py` offers the FastAPI-to-CLI bridge, but the timeout handler references an undefined `timeout` variable instead of `command_timeout`, causing runtime `NameError`s during long operations.
- The bridge imports `plc_conversion`, yet the repository ships `plc-conversion/` (with a hyphen) and `src/plc_format_converter/`; the mismatch prevents the router from loading.
- The published converter package (`src/plc_format_converter/`) includes empty modules such as `core/models.py`, and CLI entrypoints (e.g., `cli.py`) import nonexistent handlers, so the package is unusable.

### Redundant or drifted documentation
- `docs/quarantine/roadmap.md` and `docs/quarantine/roadmap.md.bak2` still claim 100% completion; they must remain archived so contributors are not misled.
- Several completion reports under `quarantine/` describe converter/test milestones that the code does not satisfy; the active documentation set intentionally excludes them.

### Unused or broken code
- `tests/phase37/` depends on sibling repositories (`plc-100`, `plc-200`, etc.) that are not pulled into this project, so the tests cannot run in isolation and should be refactored once integration scripts exist.
- Automation scripts in `scripts/` and `plc-gbt-stack/scripts/` assume converter functionality that is currently stubbed, so they will continue to fail until the converter is implemented.

### Key gaps to address
1. Repair the CLI bridge imports/timeouts and add regression coverage to prevent recurrence.
2. Implement the core data models, handlers, and CLI entrypoints for `plc_format_converter` so downstream scripts have concrete functionality.
3. Establish integration points (submodules or scripted clones) for the external PLC repositories and update tests to consume them reliably.

## Documentation & Integration Findings
- External repositories (`plc-gbt-git`, `plc-100`, `plc-200`, `plc-300`, `plc-400`, `plc-500`) remain unlinked; any plan to use their assets must start with submodules or scripted checkouts.
- The authoritative documentation set is now the root `README.md`, `docs/DEVELOPMENT_GUIDE.md`, and this review; archival reports live under `quarantine/` for historical context only.

## Recommended next steps
1. Approve the roadmap in `docs/FSD_ALIGNMENT_PLAN.md` and assign ownership for the backend stabilization phase.
2. Create an implementation backlog that maps the gaps identified above to actionable tasks with acceptance criteria.
3. During backlog execution, keep this review and the development guide synchronized so contributors understand progress and remaining risk.
