# PLC-GBT Development Guide

## Purpose
This guide is the canonical entry point for continuing work on the PLC-GBT platform. It summarizes the current repository state,
defines the immediate priorities for front-end and back-end teams, and points to supporting documentation that captures deeper
domain knowledge. Pair this guide with the [PLC-GBT Codebase Review (Version 2)](./CODEBASE_REVIEW_V2.md) for the latest audit of
redundant documentation, unused code, and implementation gaps.

## Current State Snapshot
- **Front-end:** The `ui/` directory only contains Theia package manifests and testing scaffolds; there is no runnable IDE. New
  work must begin with scaffolding a minimal Theia workspace before building workflow or Git integrations.
- **Back-end:** The `plc-gbt-stack/` FastAPI application and CLI bridge exist but require repair (e.g., import mismatches in
  `api/cli_api_bridge.py`) and the `src/plc_format_converter/` package remains largely stubbed.
- **External repositories:** No Git submodules or remote links for `plc-gbt-git`, `plc-100`, `plc-200`, `plc-300`, `plc-400`, or
  `plc-500` are currently configured. Integration scripts must be created before those assets can be consumed.
- **Documentation:** Legacy reports that claimed completed functionality have been relocated to the `quarantine/` folders. The
  documents referenced below are up-to-date with the current codebase status.

## Near-Term Priorities
1. **Backend stabilization** – Repair the CLI/API bridge, implement the minimal PLC format conversion pipeline, and add smoke
   tests to validate new endpoints.
2. **Frontend foundation** – Scaffold the Theia shell with basic panes (explorer, terminal, Git view) and connect to backend
   stubs for workflow data.
3. **Repository linking** – Establish scripts and configuration needed to sync the external PLC repositories into this project.
4. **Documentation upkeep** – Keep this guide and its supporting references synchronized with implementation progress.

Roadmap sequencing, acceptance criteria, and cross-repo integration steps are detailed in the functional specification: see the
[Functional Specification & Alignment Plan](./FSD_ALIGNMENT_PLAN.md).

## Working with PLC Memory
For an end-to-end description of the PLC Memory service, including data flows, operational commands, and integration points,
review the [PLC Memory System Overview](./plc_memory_system_overview.md). Use this runbook when implementing ingestion jobs,
query endpoints, or monitoring hooks.

## Workflow Automation
The lifecycle for defining, registering, and validating workflow nodes is documented in the
[Workflow Node Creation Guide](./workflow_node_creation_guide.md). Consult it when adding or updating automation nodes and when
syncing with the planned n8n integration.

## Engineering Standards
- [Architecture Decisions](./architecture-decisions.md) capture the high-level platform choices that remain in effect.
- [Coding Standards](./coding-standards.md) and [Naming Conventions](./naming-conventions.md) describe the conventions expected
  for new code contributions.

## Quarantined Documentation
Legacy documents that referenced unimplemented or deprecated functionality have been moved to:
- `quarantine/` (repository root) for project-wide reports.
- `docs/quarantine/` for archived documentation and research artifacts.

Review these directories only when historical context is needed; do not treat their contents as authoritative for ongoing work.
