# PLC Memory System Overview

## 1. Purpose & Scope
This document serves as the canonical reference for the PLC Memory subsystem that powers knowledge ingestion, storage, and retrieval across the plc-gbt platform. It consolidates architecture, operational workflows, and developer responsibilities for the CLI, services, and workflow integrations.

## 2. Architecture Summary
- **Core Components**
  - `plc-gbt-stack/scripts/ai/plc_memory_cli.py`: User-facing CLI orchestrating ingestion, query, monitoring, and maintenance tasks.
  - `DatabaseManager`: Manages Redis, Neo4j, PostgreSQL, and Qdrant connections.
  - `MemoryCoordinator`: Routes requests, applies batching strategies, and delegates to database adapters.
  - `plc-gbt-stack/n8n/nodes/plc_memory`: Workflow nodes exposing CLI functionality to n8n automation.
  - FastAPI surface (planned): REST endpoints mirroring CLI operations for UI and automation clients.
- **Data Flow**
  1. Input assets (code, docs) enter through CLI ingestion or workflow triggers.
  2. Coordinator normalizes content and dispatches to target databases.
  3. Metadata persisted in Neo4j; embeddings/vector data in Qdrant; cache/state in Redis; structured records in PostgreSQL.
  4. Query and monitoring commands aggregate from all stores and return unified responses.

## 3. Key Capabilities
| Capability | Entry Point | Description |
|------------|-------------|-------------|
| Ingestion | `plc-memory ingest ...` | Intelligent batching with `AnalysisDepth` controls, file/directory filters, dry-run preview, and checkpoint recovery. |
| Query | `plc-memory query` | Balanced routing using `QueryStrategy`; supports JSON output for integrations. |
| Optimization | `plc-memory optimize` | Database-specific tuning (vacuuming PostgreSQL, vector index compaction, Redis cache cleanup). |
| Monitoring | `plc-memory monitor` & `status` | Interval-based health metrics, cluster summaries, JSON/table output. |
| Maintenance | `backup`, `restore`, `clean`, `validate` | Full and targeted backups, config validation, orphan cleanup, schema checks. |
| Neo4j Ops | `plc-memory neo4j ...` | Orphan detection, resolution, health checks, integration with workflow remediation steps. |

## 4. Operational Runbooks
### 4.1 Environment Setup
1. Ensure Redis, Neo4j, PostgreSQL, and Qdrant services are reachable; capture connection strings in environment variables consumed by `DatabaseManager`.
2. Install Python dependencies from `requirements.txt` and verify `click` entry point.
3. (Optional) Configure `~/.plc_memory_config.json` with default ingestion depth, query strategy, and target databases.

### 4.2 Ingestion Workflow
1. Select source directories or files; optionally apply glob excludes.
2. Choose ingestion method:
   - `intelligent` (default): Asynchronous batches using AI Task Orchestrator heuristics.
   - `legacy`: Sequential fallback for constrained environments.
3. Monitor console output for progress; checkpoint and resume via saved session metadata.
4. Validate ingestion by running `plc-memory status --detailed --format json` and storing results in project documentation.

### 4.3 Backup & Restore
1. Run `plc-memory backup --database <target>` to capture metadata; specify `--compress` for archival.
2. Validate backup integrity with generated `backup_session_summary.json`.
3. Restore via `plc-memory restore --database <target> <path>`; use `--verify` to trigger post-restore checks.
4. Update the team backup logbook with the timestamp and verification outcome so recovery checkpoints remain auditable.

### 4.4 Health & Maintenance
- Schedule `plc-memory health` as a nightly job; aggregate results for observability dashboards.
- Execute `plc-memory clean` weekly to purge orphaned or stale entries.
- Employ `plc-memory validate system --detailed --report <file>` before releases to ensure schema consistency across stores.

## 5. Integration Points
### 5.1 Workflow Automation
- Workflow nodes call CLI subcommands using templated payloads; ensure node definitions remain synchronized with CLI options (see `workflow_node_creation_guide.md`).
- For long-running tasks, use asynchronous node variants that stream logs via Redis pub/sub.

### 5.2 UI/IDE
- Theia extensions will consume REST endpoints mirroring the CLI; ensure parity tests confirm identical responses for equivalent commands.
- Provide mock adapters for offline development to avoid requiring all databases locally.

### 5.3 External Repositories
- Submodule repositories (plc-100..500) act as ingestion fixtures; maintain metadata manifests describing dataset scope.
- plc-gbt-git delivers conversion utilities feeding ingestion pre-processors; ensure version compatibility is tracked in `scripts/dev/link_repos.py` output.

## 6. Testing Strategy
- **Unit tests:** Cover `DatabaseManager`, `MemoryCoordinator`, and CLI option parsing.
- **Integration tests:** Spin up ephemeral databases (Docker Compose) and execute ingestion/query/backup flows.
- **Workflow regression:** Validate n8n node executions against canonical CLI outputs.
- **Observability checks:** Confirm health metrics populate monitoring endpoints (Prometheus/Grafana integration planned).

## 7. Roadmap & Ownership
| Area | Short-term Focus | Owner |
|------|------------------|-------|
| CLI enhancements | Improve error handling, add progress APIs | Platform team |
| Service API | Expose FastAPI routes with auth | Backend team |
| Workflow connectors | Expand nodes (bulk ingest, alerting) | Automation team |
| Documentation | Keep runbook current with releases | Knowledge team |

## 8. Change Management
- Update this document whenever new commands or databases are introduced.
- Version CLI changes with semantic tags (e.g., `v1.1.0`) and record release notes.
- Tie major updates to integration tests in CI to prevent regression.

## 9. References
- Source code: `plc-gbt-stack/scripts/ai/plc_memory_cli.py`
- Node definitions: `plc-gbt-stack/n8n/nodes/plc_memory`
- Testing frameworks: `scripts/testing/*plc_memory*`
- Historical reference: `docs/quarantine/summaries/PLC_MEMORY_CLI_PRODUCTION_DEPLOYMENT_GUIDE.md`
