# Lifecycle & Async Usage Guide for AI Coding Agents

**File path:** `plc-gbt-stack/ai/docs/advanced/lifecycle-updates.md`

## Why this document exists

Recent lifecycle upgrades ensure the AI Task Orchestrator behaves predictably when coding agents run inside asynchronous runtimes (e.g., Jupyter, FastAPI background workers, or orchestrated task queues). This guide captures the required practices so every agent immediately knows how to work with the latest teardown and analysis flows.

## Key changes

1. **Async-first analysis**
   - Use `await orchestrator.analyze_task_async(description)` whenever the caller already owns an event loop.
   - The synchronous `analyze_task()` method now detects active loops and raises a clear error directing agents to the async API.
   - Plugin hooks registered for analysis are executed through the async dispatcher, so coroutine callbacks are now supported.
   - Analysis runs through `asyncio.to_thread(...)` internally, keeping the caller's event loop responsive while the synchronous analyzer performs its work.

2. **Predictable shutdown semantics**
   - `await orchestrator.aclose()` is the preferred shutdown path inside async environments.
   - Calling `orchestrator.close()` while an event loop is running raises an actionable error (`close() cannot be used while an asyncio event loop is running. Use the asynchronous counterpart (e.g. 'await aclose()').`).
   - The orchestrator still guarantees final summary creation and plugin shutdown through the existing `cleanup()` / `cleanup_async()` helpers.

3. **Plugin author expectations**
   - Hooks registered for `PRE_ANALYZE` and `POST_ANALYZE` may now be coroutine functions.
   - Synchronous hooks continue to work without modification; they are awaited transparently by the orchestrator.
   - Guide generation now fires `PRE_GENERATE_GUIDE` and `POST_GENERATE_GUIDE` hooks around the Markdown writer so plugins can inject content or publish artifacts without manual patching.
   - Plugin developers should update documentation/examples to note async compatibility when relevant.

## Recommended usage patterns

| Scenario | Recommended Call | Notes |
| --- | --- | --- |
| CLI or script | `analysis = orchestrator.analyze_task(task)` | No event loop conflicts; cleanup via `with` block or `orchestrator.close()` |
| Async service (FastAPI, Quart, etc.) | `analysis = await orchestrator.analyze_task_async(task)` | Pair with `await orchestrator.aclose()` or `async with` |
| Notebook experiments | Prefer `async with AITaskOrchestrator() as orchestrator:` | Guarantees cleanup even with interrupted cells |
| Plugin provides async pre-analysis logic | Register coroutine under `HookType.PRE_ANALYZE` | It will be awaited before task analysis runs |

## Action items for new coding agents

- [ ] Update any local snippets to use the async API when operating inside frameworks that manage their own event loop.
- [ ] Ensure teardown uses `await aclose()` (or the async context manager) when working asynchronously.
- [ ] Review plugin implementations for opportunities to leverage async hooks when interacting with remote systems.
- [ ] Share this document with future agents so they understand the lifecycle guarantees that are now in place.

For additional architectural context, refer to the master improvement plan in `docs/ai-task-changes-03.md` and the plugin architecture reference in `plc-gbt-stack/ai/docs/advanced/plugins.md`.
