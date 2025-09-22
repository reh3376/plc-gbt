# Workflow Node Creation Guide

## 1. Purpose
This guide defines the end-to-end process for designing, implementing, and validating workflow nodes within the plc-gbt ecosystem. It ensures consistency across automation assets, accelerates integration with the PLC Memory system, and prepares the project for cross-repo collaboration.

## 2. Node Lifecycle Overview
1. **Ideation & Requirements**
   - Capture business goal, target systems (e.g., PLC Memory, Git automation, external PLC repos), and expected inputs/outputs.
   - Identify triggering personas (UI, CLI, scheduled job) and error-handling requirements.
2. **Specification**
   - Document node metadata: name, category, complexity rating, prerequisite permissions, and dependency repos.
   - Map CLI or API surfaces the node will call; confirm parity with latest documentation.
3. **Implementation**
   - Scaffold node directory under `plc-gbt-stack/n8n/nodes/<domain>/<node-name>`.
   - Implement execution logic (TypeScript/JavaScript for n8n) with reusable helpers from `@plc-gbt/workflow-sdk` (planned package) or local utilities.
   - Configure credentials, UI properties, and dynamic options consistent with data contracts.
4. **Validation**
   - Run unit tests (node-specific) and integration flows using local n8n or automated harness.
   - Capture fixtures referencing plc-100..plc-500 sample data where relevant.
5. **Documentation & Release**
   - Update `ui/nextjs` documentation pages and append entry to the workflow node catalog.
   - Version node changes; add migration notes for breaking updates.

## 3. Design Standards
- **Idempotency:** Nodes should tolerate retries; ensure downstream operations handle duplicates gracefully.
- **Observability:** Emit structured logs and status updates; expose metrics when possible.
- **Security:** Never embed secrets; use credential references defined in n8n credentials store.
- **Extensibility:** Factor shared logic into helpers; align naming with `docs/naming-conventions.md`.

## 4. Integration with External Repositories
| Repo | Usage in Nodes | Integration Notes |
|------|----------------|-------------------|
| plc-gbt-git | Git automation, conversion tooling | Import converters/validators; ensure adapter layer handles absent repo gracefully. |
| plc-100 | Baseline PLC workflows | Provide sample payloads for ingestion nodes and regression tests. |
| plc-200 | Advanced control workflows | Demonstrate complex branching logic and error recovery. |
| plc-300 | Safety/diagnostic workflows | Supply compliance-focused scenarios; ensure nodes log audit trails. |
| plc-400 | Networked PLC orchestration | Validate multi-site automation; test concurrency handling. |
| plc-500 | Edge analytics workflows | Benchmark performance-focused nodes and streaming behaviors. |

**Linking strategy:**
- Add each repo as a Git submodule under `external/<repo>` (see `docs/FSD_ALIGNMENT_PLAN.md`).
- Maintain manifest files describing available assets, test fixtures, and contact owners.
- Provide helper script `scripts/dev/link_repos.py` to update submodules and export `WORKFLOW_REPO_PATHS` environment variables for node runtime.

## 5. PLC Memory Node Alignment
- Nodes interacting with PLC Memory must map 1:1 with documented CLI commands (see `plc_memory_system_overview.md`).
- Leverage standardized payload schema:
  ```json
  {
    "command": "ingest",
    "options": {
      "depth": "structural",
      "paths": ["/workspace/project"],
      "dryRun": false
    }
  }
  ```
- Use asynchronous execution patterns for long-running tasks; stream progress via Redis when available.
- Ensure error messages bubble up with actionable remediation steps.

## 6. Testing Checklist
- ✅ Node schema validation (required fields, defaults, option constraints).
- ✅ CLI/API contract verification against mocked or live services.
- ✅ Workflow integration test that exercises success and failure paths.
- ✅ Documentation entry updated with screenshots or sequence diagrams.
- ✅ Changelog entry in `docs/summaries/workflow_nodes.md` (to be created as catalog).

## 7. Release Management
1. Increment node version metadata following semantic versioning.
2. Publish release summary detailing features, breaking changes, and dependency updates.
3. Update automation pipelines to include new node tests; ensure CI loads submodules for fixture access.
4. Notify stakeholders (UI, backend, documentation teams) and schedule enablement session if behavior changes.

## 8. Roles & Responsibilities
| Role | Responsibilities |
|------|------------------|
| Workflow Lead | Approves node proposals, enforces standards, coordinates releases. |
| Backend Integrator | Maintains API/CLI parity, reviews security and performance impacts. |
| Documentation Owner | Ensures guides, screenshots, and catalogs remain current. |
| QA Engineer | Builds regression scenarios leveraging external repositories. |

## 9. Appendices
- **Templates:** Node specification template (forthcoming) and test harness configs.
- **References:**
  - `plc-gbt-stack/n8n/nodes/*`
  - `plc-gbt-stack/N8N_ARCHITECTURE_ANALYSIS_FOR_PHASE26.md`
  - `docs/FSD_ALIGNMENT_PLAN.md`
  - `docs/plc_memory_system_overview.md`

Keep this guide synchronized with evolving tooling; submit updates alongside node enhancements.
