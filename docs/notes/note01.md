## For tasks related to Frontend dev use this prompt:
1. Review the latest UI architecture, design system, and accessibility requirements documented in `@ui/docs/architecture/THEIA_ARCHITECTURE_SPECIFICATION.md` 
and related guides before making any interface changes.

2. Reference @AI_TASK_ORCHESTRATOR_TS_GUIDE.md together with @ai_task_orchestrator_ts.ts whenever orchestration behavior, task sequencing, 
or automation hooks affect the feature. Review these resources early in planning and again before finalizing work that touches orchestrator flows 
to ensure alignment with the TypeScript implementation details.

3. Collect active context before coding. Read the user request, inspect relevant files, and capture current UI state or API contracts so the 
hypothesis about required changes is grounded in actual project data.

4. Consult @DEVELOPMENT_GUIDE.md after the initial scan. Use it to confirm architecture expectations, naming conventions, and any in-progress 
initiatives that should influence the solution before drafting implementation notes.

5. Coordinate implementation with Next.js component patterns and shared components to keep panels, layouts, and workflows consistent across the IDE.

6. Decide whether you are prototyping or delivering production-ready UI work, documenting exploratory branches clearly and polishing production 
code to meet linting and UX quality bars.

7. Run the mandated UI test suites (Playwright, linting, and visual regression checks) and resolve failures before requesting review.

8. Once automnated and user interactive testing comfirms task(s) are complete Apply the planned changes, keep commits focused, run all mandatory 
frontend and backend tests (including linting, type checks, and unit suites), and summarize results before handing off the task.

## For tasks related to general up keep, iteraction with integrations, scripting, or backend dev use this prompt:
1. Review `@DEVELOPMENT_GUIDE.md`, `@plc_memory_system_overview.md`, and `plc-gbt-stack/DOCKER_ENVIRONMENT_STATUS.md` to ground yourself in the 
PLC Memory architecture (Redis, Neo4j, PostgreSQL, Qdrant), confirm the Docker MCP server on `http://localhost:8811`, and note the CLI entry point 
at `plc-gbt-stack/scripts/ai/plc_memory_cli.py` before planning work.

2. Drive every assignment through the methodology in `plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md`, using `plc-gbt-stack/ai/ai_task_orchestrator.py` 
to analyze requirements, enumerate dependencies (databases, MCP schemas, workflow nodes), and script the implementation stages.

3. Decide early whether you are prototyping or shipping production code; spikes must explicitly document limitations, while production changes must 
integrate with the PLC Memory flows (ingest, query, backup, monitoring) and uphold repository standards.

4. Take advantage of the MCP-powered tooling—plc memory, code optimizer, fine-tuned SME LLM, and other exposed services—available through the locally 
running Socket MCP Docker environment when planning and executing your work.

5. Run the required validation for the scope you touch—`pytest`/`ruff` suites, orchestrator or CLI smoke commands (e.g., `python plc-gbt-stack/scripts/ai/plc_memory_cli.py status`)
, and Docker MCP connectivity checks—and resolve every failure before requesting review.

**Assigned task(s) follow**: