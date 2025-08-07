
# plc‑git Integration & UI Roadmap  
*Version: 2025-07-31*

---

## ❖ Purpose  
This document is the single source of truth for integrating **plc‑git** into a GitHub‑centric workflow, adding CI / CD automation, and delivering a UI that presents PLC diffs in ladder‑logic & function‑block form.  
It is written so a coding agent can grep each task by its **Phase–Task ID** (`P3‑T2`, `P5‑T6`, …).

---

## ☰ Legend  
| Symbol | Meaning |
|--------|---------|
| `P#`   | Phase number (0‑6) |
| `T#`   | Task number within the phase |
| ☐ / ☑ | Un‑done / done checkbox |
| 🔄     | Recurs in later phases |

---

## Phase 0 — Environment Bootstrapping
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P0‑T1 | ☐ **Repo Linking** – add plc‑git as a sub‑module/requirement inside plc‑gbt | DevOps | Enables AI agents to commit logic changes - plc-git repo URL: https://github.com/reh3376/plc-git.git |
| P0‑T2 | ☐ **Toolchain Setup** – install Rockwell CLI converters (`acd‑tools`, `l5x`) in CI image | Build Eng | ― |
| P0‑T3 | ☐ **Schema Stub** – create minimal Neo4j node labels for `Controller`, `Routine`, `Rung` | Data Eng | Pre‑req for graph diffs |

---

## Phase 1 — Core Git & Diff Plumbing
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P1‑T1 | ☐ **ACD→L5X Round‑Trip Test** | QA | Fails if hash mismatch |
| P1‑T2 | ☐ **IR & Diff Engine** (XML → AST → ChangeSet) | Core Dev | See Section **6.1** |
| P1‑T3 | ☐ **Ignore List** – strip GUIDs, layout fluff | Core Dev | YAML config |
| P1‑T4 | ☐ **Semantic LCS Algorithm** | Core Dev | Instruction‑level granularity |
| P1‑T5 | ☐ **Unit Tests** – sample `before/after` fixtures | QA | Use Still01 AOI |
| P1‑T6 | ☐ **CLI Renderer** `plc_git diff --ladder` | CLI Dev | Section **6.2** |

---

## Phase 2 — Repository Hygiene
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P2‑T1 | ☐ **Git‑LFS for binaries** (`*.ACD`, images) | DevOps | |
| P2‑T2 | ☐ **Pre‑Commit Hook** – auto‑convert ACD‑>L5X, lint | DevOps | |
| P2‑T3 | ☐ **Branch‑Naming Convention** (`feature/`, `hotfix/`) | Ops | |
| P2‑T4 | ☐ **PR Template** – includes download‑risk badge | DevOps | |

---

## Phase 3 — Continuous Integration & Quality Gates
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P3‑T1 | ☐ **GitHub Action** – build, diff, unit tests | DevOps | |
| P3‑T2 | ☐ **Artefact Upload** – attach ladder diff HTML | DevOps | Uses `--output json` |
| P3‑T3 | ☐ **Graph Lint** – validate Neo4j schema | Data Eng | |
| P3‑T4 | ☐ **Download‑Risk Check** – fail if full program DL required | Core Dev | |

---

## Phase 4 — API & Backend Services
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P4‑T1 | ☐ **FastAPI Endpoint** `/diff/json` | Backend | Wraps CLI |
| P4‑T2 | ☐ **Auth Middleware** – GitHub + SAML | SecOps | |
| P4‑T3 | ☐ **Long‑Living Branch Sync** – rebase w/ online edits 🔄 | Backend | |

---

## Phase 5 — Front‑End UI
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P5‑T1 | ☐ **React Skeleton** w/ Redux store | Front‑End | |
| P5‑T2 | ☐ **Diff Tabs** `[XML] [Ladder] [FBD]` | Front‑End | |
| P5‑T3 | ☐ **SVG FBD Renderer** (`svg‑pan‑zoom`) | Front‑End | |
| P5‑T4 | ☐ **Filter Chips** (comment‑only, safety routines) | Front‑End | |
| P5‑T5 | ☐ **Change Navigation** – jump to rung number | Front‑End | |
| P5‑T6 | ☐ **Risk Badge UI** | Front‑End | consumes P3‑T4 |

---

## Phase 6 — Roll‑Out & Training
| ID | Task | Owner | Notes |
|----|------|-------|-------|
| P6‑T1 | ☐ **Pilot on Still01 PLC** | Ops | |
| P6‑T2 | ☐ **Training Session** – controls engineers | Ops | Ladder diff demo |
| P6‑T3 | ☐ **Feedback Loop** – collect issues, iterate | Prod | |

---

## 6 · Technical Appendices  

### 6.1 Extraction Pipeline (XML → IR)
```text
1. Parse  Controller/Programs/.../Routines/Routine/…
2. Normalise  → strip GUIDs, timestamps
3. Lift to IR →   Rung(id, comment, instructions[])
                       FB(type, pins[])
```

### 6.2 Diff Engine
* Longest‑Common‑Subsequence on IR nodes  
* Categorise `added`, `removed`, `modified` (incl. pin rewires)  
* Output **ChangeSet** ⇒ JSON (`--output json`)

### 6.3 CLI Ladder Renderer
```
plc_git diff before.L5X after.L5X --ladder --context 2
```
* ASCII ladder with colour codes (green = add, red = del, yellow = mod).  
* FBD networks rendered as ASCII boxes.

### 6.4 UI Consumption
* Front‑end calls `/diff/json` → renders in React tab  
* SVG graph for FBD, monospace for ladder logic  
* Download‑risk badge warns if full controller download required.

---

## 7 · ChangeLog
| Date | Comment |
|------|---------|
| 2025-07-31 | Initial version |

---

Happy coding — and may your rungs never major‑fault!
