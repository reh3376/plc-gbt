
-0

plc-gbt-stack/ai/docs/api-reference.md
+19
-0

plc-gbt-stack/ai/docs/index.md
+1
-0

plc-gbt-stack/ai/plc_orchestrator/core/orchestrator.py
+211
-16

plc-gbt-stack/ai/plc_orchestrator/plugins/base.py
+22
-0



Ask

Code
Diff
Logs

docs/ai-task-change-log.md
New
+33
-0

# AI Task Orchestrator Change Map (Async Lifecycle Update)

This reference captures the async lifecycle improvements introduced for the AI Task Orchestrator so future coding agents can quickly locate and understand each modification.

## Runtime Orchestrator Core (`plc-gbt-stack/ai/plc_orchestrator/core/orchestrator.py`)

- **Event loop awareness & sync guards — [lines 125-143, 229-236]**  
  Adds `_event_loop_running()` and `_ensure_sync_context()` helpers plus a guard inside `close()` so synchronous entry points emit actionable guidance when called from an active asyncio loop. Prevents deadlocks and directs callers toward the async APIs.
- **Context manager support — [lines 207-228]**  
  Implements both synchronous and asynchronous context manager hooks (`__enter__`, `__exit__`, `__aenter__`, `__aexit__`) so agents can rely on `with` / `async with` blocks for deterministic teardown.
- **Async-aware shutdown pipeline — [lines 238-296, 725-778]**  
  Introduces `aclose()`, refactors cleanup to serialize access with an `asyncio.Lock`, adds plugin shutdown delegation, and ensures summary creation runs once even when cleanup is scheduled from a running event loop.
- **Coroutine analysis pipeline — [lines 312-383]**  
  Provides `analyze_task_async()` that awaits plugin hooks, integrates tracing/metrics contexts, and safely enriches analyses with async memory lookups. The synchronous `analyze_task()` now dispatches through this coroutine.

## Plugin Infrastructure (`plc-gbt-stack/ai/plc_orchestrator/plugins/base.py`)

- **Async hook dispatch & deterministic shutdown — [lines 245-296]**  
  Extends `execute_hook_async()` to await coroutine hooks while preserving synchronous compatibility and adds a `shutdown()` routine that fires lifecycle hooks, cleans up plugins, and clears registrations so teardown mirrors orchestrator expectations.

## Documentation Updates

- **Roadmap callout — `docs/ai-task-changes-03.md` [lines 30-35]**  
  Summarizes the async lifecycle work in the master improvement plan so agents scanning the roadmap see the new behavior immediately.
- **Lifecycle primer — `plc-gbt-stack/ai/docs/advanced/lifecycle-updates.md` [lines 1-42]**  
  New dedicated guide explaining async-first analysis, predictable shutdown semantics, and plugin author expectations with actionable checklists and usage table.
- **Plugin guide note — `plc-gbt-stack/ai/docs/advanced/plugins.md` [lines 141-146]**  
  Highlights coroutine support for analysis hooks and advises plugin authors on writing async-aware callbacks.
- **API reference additions — `plc-gbt-stack/ai/docs/api-reference.md` [lines 66-83]**  
  Documents `analyze_task_async` alongside a prominent warning that synchronous callers inside event loops should switch to the coroutine variant.
- **Navigation update — `plc-gbt-stack/ai/docs/index.md` [lines 65-69]**  
  Adds the lifecycle guide to the advanced topics list so knowledge of the new teardown workflow is part of the primary documentation navigation.