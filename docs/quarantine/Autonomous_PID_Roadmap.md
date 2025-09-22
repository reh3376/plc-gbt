# Roadmap for Autonomous PID Tuning and Monitoring Tool

## Milestone 1: Enhanced CLI for User Input
**Objective:** Develop a robust command-line interface (CLI) using Python’s **Rich** and **Textual** libraries to guide the user through initial configuration. This module will interactively prompt for all required inputs with validation and helpful formatting.  

### Key Steps
1. **Initial Setup** – Integrate Rich for colorful prompts and Textual for an interactive TUI. Design a workflow to ask the user a series of questions, storing responses in a configuration data structure.  
2. **Process‑Variable Input** – Prompt for the total number of process variables (PVs). For each PV collect:  
   - Name (descriptive tag)  
   - Engineering units (e.g. °C, psi)  
   - Operating range (min / max)  
   - OPC‑UA address (Ignition node path)  
3. **Control Variable & Set‑point** – Prompt for CV details (name, units, range, OPC‑UA path) and the set‑point (SP).  
4. **Disturbance Variables** – If DVs are measured, gather their names and OPC‑UA paths.  
5. **User Experience** – Implement input validation (e.g. numeric range checks) and context‑aware hints (warn if min > max, etc.). Use Rich tables/panels to review the collected configuration before continuing.

---

## Milestone 2: Multi‑PV Support and Strategy Selection
**Objective:** Handle scenarios with multiple PVs by determining the appropriate control strategy. The agent’s logic uses user input and heuristics to decide whether to:
* Identify a **PPV** (Primary Process Variable) and treat others as **SPVs** (Secondary PVs);  
* Compute a **weighted average** PV when no single PV is clearly primary; or  
* Recommend **cascade / multi‑loop** control if PVs represent different stages.  

### Steps
1. **Primary PV Identification** – Ask if one PV should be the PPV.  
2. **Weighted PV Combination** – Offer a weighted‑average formula  

   *PV\_avg = (Σ wᵢ PVᵢ) / Σ wᵢ*  

   with user‑supplied or equal weights.  
3. **Cascade Suggestion** – If PVs reflect sequential dynamics, suggest configuring master/slave PIDs (primary CV drives secondary SP).  
4. **Disturbance Mapping** – Associate DVs to PVs (direct or inverse effect) for later feed‑forward logic.

---

## Milestone 3: Loop Type & Controller Configuration Input
**Objective:** Gather loop characteristics that influence tuning.

| Prompt | Purpose |
|--------|---------|
| **Process Type** (Level, Flow, Pressure, Temp, …) | Applies appropriate tuning rules (fast vs slow vs integrating). |
| **Algorithm Form** (Dependent / Independent) | Rockwell defines how P, I, D are interpreted. |
| **Instruction Type** (PID / PIDE) | Classic ladder PID vs enhanced velocity‑form PIDE. |
| **Control Mode Preference** (P / PI / PID) | Allows disabling I or D if unnecessary. |

This metadata drives later parameter mapping and tuning‑rule selection.

---

## Milestone 4: Rockwell PID/PIDE Parameter Integration
**Objective:** Map user inputs to Rockwell Studio 5000 parameters.

* **Parameter Definitions** – For PIDE gather `PGain`, `Ti`, `Td`, PV/CV scales, SP limits, output limits, `FF`, etc.  
* **Velocity vs Position Form** – PIDE is velocity‑form; compensate for loop update period \(Δt\).  
* **Feature Support** – Expose options for external reset, bumpless transfer, PV tracking.  
* **Feed‑Forward/Bias** – Accept DV‑based bias; limit to ±100 % of CV span.  
* **Dependent/Independent Conversion** – Provide formulas to convert gains between forms.

> **Example output**:  
> `Kc = 1.5`, `Ti = 2.0 min`, `Td = 0.5 min`, PV 0–100 °C, Task period 0.5 s.

---

## Milestone 5: Automated PID Loop Tuning Procedure
**Objective:** Execute an end‑to‑end open‑loop test → model identification → initial tuning → closed‑loop refinement.

1. **Manual Mode Baseline** – Command PLC to MAN, log PV/SP/CV.  
2. **Step Tests** – Bump CV (±5 %) and capture reaction curves for each PV (cascade: tune secondary first).  
3. **Model Identification** – Fit FOPDT: gain `Kp`, time constant `τ`, dead‑time `θ`.  
4. **Initial Settings** – Apply Z‑N, Cohen‑Coon, or IMC rules → P, I, D. Convert to chosen form.  
5. **Auto‑Mode Test** – Load new gains, switch to AUTO, monitor for overshoot/oscillation.  
6. **Iterative Refinement** – Adjust gains based on IAE or variance metrics.  
7. **Advanced Suggestions** – If PID insufficient, recommend feed‑forward, Smith predictor, cascade, or MPC.

Logs and results are stored in the database.

---

## Milestone 6: Deploy Tuning Parameters & Validation
* **Report Final Gains** – Human‑readable summary + database record.  
* **PLC Update** –  
  * _Option A_: Write tags via OPC‑UA.  
  * _Option B_: Generate modified `.L5X` snippet for import.  
* **ACD Handling** – Provide utility to export ACD→L5X via headless Studio 5000 if needed.  
* **Burn‑In Test** – Run loop in AUTO for an extended period to confirm stability.

---

## Milestone 7: Monitoring Mode for Ongoing Performance
* **Data Acquisition** – Subscribe/poll PV, SP, CV (+ DV) at user interval (30 min–24 h).  
* **Metrics** – MAE, IAE, PV σ, CV saturation percentage, oscillation index.  
* **Alerts** – Immediate if PV out of bounds or sustained oscillations detected.  
* **Periodic Reports** – Rich summary every N hours.  
* **Adaptive Re‑Tune Suggestion** – Triggered if performance degrades.  
* **Historical Storage & ASCII Plots** – Export or inline Textual charts.

---

## Milestone 8: CLI Command Interface
* `tune <loop>` – Start tuning workflow.  
* `monitor <loop>` – Start / stop monitoring.  
* `status` – Show current health and last tuning timestamp.  
* `help` – Built‑in command help.  
Rich colors and tables enhance feedback; confirmation prompts guard against unsafe actions.

---

## Milestone 9: Data Storage & Management
* **Relational DB** – Time‑series tables for PV, CV, SP, metrics.  
* **Graph DB** – Nodes: PV, CV, DV, PID blocks; Edges: *manipulates*, *disturbs*, *feeds‑SP‑of*.  
* **Retention & Backup** – Configurable purge/archive; scheduled backups.  
* **Use Cases** – Root‑cause traversal, feed‑forward path discovery, multi‑loop conflict analysis.

---

## Milestone 10: Rockwell File‑Format Support
* **Read L5X** – Parse XML to auto‑populate tag names, ranges, gains.  
* **Write L5X** – Inject tuned parameters; preserve rest of project.  
* **ACD↔L5X Conversion** – Scripted Studio 5000 or community tools.  
* **Validation** – Re‑parse or emulate to ensure syntactic correctness.

---

## Milestone 11: Future AI Enhancements
1. **Model Predictive Control (MPC)** – Build or import dynamic model and optimize CV moves each scan.  
2. **Machine‑Learning Models** – Train RNN/CNN from historical data for prediction or anomaly detection.  
3. **Reinforcement Learning (RL)** – Explore policy training in simulation for self‑optimizing control.  
4. **Modular Controller Interface** – Plug‑in architecture (`PIDController`, `MPCController`, `AIController`).  
5. **Continuous Improvement Loop** – Periodic retraining and deployment of updated models.

---

## References
* Rockwell Automation – *Logix 5000 Advanced Process Control & Drives Instructions* (PID/PIDE forms).  
* Rockwell Automation – *Studio 5000 Logix Designer Online Help* (velocity‑form PIDE, feed‑forward).  
* Rockwell Automation – *Feed‑Forward or Output Biasing* application note.  
* PLCtalk.net forum threads on multi‑sensor and cascade tuning strategies.  
* APMonitor – FOPDT identification and IMC tuning.  
* Control Engineering – Guidelines on loop‑type dynamics.  
* XML `.L5X` examples (StackOverflow discussions).  
* Recent research on AI‑enhanced process control (De Gruyter, Brill, etc.).

---
