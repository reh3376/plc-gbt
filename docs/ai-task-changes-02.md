# AI Task Orchestrator Guidance – Targeted Improvements (by file)

This document proposes actionable improvements for the four guidance files used to direct AI coding agents. No changes have been made to the source files.

---

## 1) Python Guide — `plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md`

- Quick Start and Navigation
  - Add a 60-second Quick Start (copy/paste runnable snippet) covering: analyze → implement → validate → document.
  - Insert a “Choose your path” index (links for: small scripts, service endpoints, data pipelines, control algorithms).
- Configuration & Environments
  - Document dev/stage/prod config overlays, `.env` loading order, secret sourcing, and validation (e.g., pydantic Settings or `dynaconf`).
  - Provide a minimal config schema and a “config doctor” CLI routine to fail fast.
- Performance & Reliability
  - Add standardized retry/backoff/circuit-breaker patterns for network/DB (tenacity-style examples), plus async I/O guidance.
  - Include caching strategies (in‑process LRU, Redis tier) with invalidation guidance.
- Industrial Coverage
  - Expand with concise patterns for: L5X/ACD parsing workflows, SCADA/OPC UA interfaces, real-time ingest (bounded queues), and safety checks.
- Testing & Quality Gates
  - Provide a reference pytest layout (unit/integration/e2e), fixtures for memory backends, and a smoke test checklist.
  - Define coverage gates and performance micro-benchmarks (pytest-benchmark) expectations.

---

## 2) Python Implementation — `plc-gbt-stack/ai/ai_task_orchestrator.py`

- Modularization & Boundaries
  - Split into a package: core (orchestrator, progress), analysis, validation, memory, domain (control/math), utils (config/logging/errors).
  - Extract pure helpers; reduce class breadth; prefer composition over deep inheritance.
- Imports & Dependency Injection
  - Replace broad dynamic imports with explicit module boundaries and DI (constructors accept adapters: DB, memory, schema client).
  - Centralize optional‑dependency checks with actionable error messages and remediation steps.
- Type Safety & Contracts
  - Adopt strict typing across modules; define Protocols for pluggable backends; prefer `TypedDict`/`dataclass` where stable.
  - Keep OpenAPI MCP as the only source of API contracts; use Pydantic only for internal config/data shapes.
- Async and Concurrency Discipline
  - Clearly separate sync vs async paths; avoid `create_task` on non‑awaitables; add cancellation and timeouts.
- Observability
  - Structured logging (JSON toggle) with task/run IDs; minimal metrics hooks (timers/counters); optional OpenTelemetry exporters.
- Tests & Examples
  - Unit tests per module; integration tests for memory routing and validation tiers; golden files for analyzers.

---

## 3) TypeScript Guide — `plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_TS_GUIDE.md`

- Progressive Onboarding
  - Add a Quick Start: Next.js strict TS + one Playwright MCP smoke test + MCP schema wiring example.
  - Provide a decision tree: App vs Pages Router, Server vs Client components, API Routes, Middleware.
- Next.js Specifics
  - Clarify RSC boundaries, `use client`, route handlers, caching (revalidate), ISR/SSG patterns, Middleware auth.
- State & Data
  - Document server‑state via TanStack Query; local state via Context/Zustand/Redux Toolkit; persistence patterns.
- Schema‑First Enforcement
  - Emphasize: import generated types from `@/api/types.gen`; validate with MCP `openAPISchemaMCP.validateResponse()` everywhere.
  - Provide “mock MCP” strategy for tests (static fixtures + contract validation).
- Testing & Accessibility
  - Minimal Playwright MCP suites for components and flows; keyboard navigation and screen-reader sanity checks.
- Performance
  - Bundle analysis workflow, image/font optimization, critical CSS, memory‑leak prevention checklist.

---

## 4) TypeScript Implementation — `plc-gbt-stack/ai/ai_task_orchestrator_ts.ts`

- Architecture & Separation
  - Extract modules: core orchestrator, analyzers, validators, memory adapters, automated tests (Playwright MCP), user testing helpers.
- Errors & Resiliency
  - Standard error types, retries with jitter, abortable operations (AbortController), and typed error surfaces.
- Config & Envs
  - Central config module with env overlays and validation; single source for feature flags and endpoints.
- Testing Utilities
  - Helpers/mocks for Playwright/Jest‑RTL; shared fixtures; deterministic data builders.
- Observability
  - Logging abstraction with levels; basic metrics; correlation IDs threaded through async flows.
- Performance & Limits
  - Guard long operations; queue/background patterns where applicable; resource caps and backpressure notes.

---

## Cross‑file Consistency & Governance

- Naming & Parity
  - Align class/enum/function names and success criteria between Python and TypeScript; document any intentional deviations.
- Contract Discipline
  - OpenAPI MCP is the sole source of API contracts and UI schemas; forbid manual definitions across both stacks.
- Validation at Boundaries
  - Mirror runtime validation patterns (backend and frontend) with generated types + runtime checks.
- Documentation Shape
  - Unify sectioning, checklists, and example styles; cross‑link equivalent sections (analysis, validation, testing, production).

---

## Suggested Priority Roadmap

1) Split Python implementation; standardize names across stacks.
2) Add Quick Starts and decision trees to both guides.
3) Centralize configuration and validation modules (both stacks).
4) Strengthen testing utilities and two‑phase testing recipes.
5) Add performance and observability guidance with minimal hooks.

---

## Acceptance Indicators

- Smaller, focused PRs; reduced cognitive load per module.
- First‑run success from Quick Start in minutes.
- Fewer contract mismatches (strict MCP usage, validation at edges).
- Clearer operational posture (config/logging/metrics standardized).
