# auto-plc-bk.md — Production‑Ready PLC Backup & Scheduler (Python)

> **Goal**: Provide a step‑by‑step blueprint (with ready‑to‑wire CLI) to implement an automated backup system that connects to Rockwell Logix controllers over **EtherNet/IP (IPv4)** (e.g., `10.4.2.2`), retrieves a project snapshot, and saves it in **`.acd`** or **`.l5x`** format on a defined retention schedule.

---

## 0) Scope, assumptions & safety

- **Supported targets**: ControlLogix / CompactLogix family reachable over EtherNet/IP (IPv4).
- **OS & host**: Windows workstation/server where **Studio 5000 Logix Designer** is installed and licensed (required for `.acd` and export to `.l5x`).  
- **Automation approach**: Use a Python service with:
  - **pycomm3** (or similar) to _validate_ a controller over CIP before backup.
  - **Studio 5000 automation (COM)** to perform project export (`.l5x`) and file format operations (`.acd`⇄`.l5x`).  
- **Scheduling**: Windows Task Scheduler (service account), or APScheduler as an in‑app fallback.
- **Security**: Service account with least privilege, backups written to a restricted share, optional encryption-at-rest.
- **Safety**: This procedure is **read‑only** to the controller; do **not** perform downloads/edits from the backup host. Validate change‑management with your site standards before enabling automated reads from control networks.

> ⚠️ **Note on “upload”**: Programmatic “upload from controller” is not officially documented as a public API. The production pattern here is to automate Studio 5000 to create an **offline snapshot** and then export to **`.l5x`**. Where a site requires guaranteed online upload, use FactoryTalk AssetCentre or formally accept the UI‑automation approach described below and harden it with testing, retries, and monitoring.

---

## 1) Architecture (high level)

```
+-----------------------+         +-----------------------+
|  auto-plc-bk (Python) |<------->|  Studio 5000 (COM)    |
|  CLI + service        |         |  Logix Designer v35+  |
|  - discovery/verify   |         |  - open/offline ops   |
|  - run backup         |         |  - export to .l5x     |
|  - retention & logs   |         +-----------+-----------+
+-----------+-----------+                     |
            | CIP (validate)                  | Files (.acd/.l5x)
            v                                 v
      +-----+------+                 +---------------------+
      |  PLC @     |                 | Backup repository   |
      |  10.4.2.2  |                 | (local/NAS/S3/DFS)  |
      +------------+                 +---------------------+
```

**Key flows**

1. **Validate target** (`pycomm3`): Read Identity, Product Type, Revision, Serial, and time. Fail fast on connectivity.
2. **Snapshot** (Studio 5000 automation): Create/refresh an **offline project** and **export to `.l5x`** when requested.
3. **Package**: Optionally compress, checksum, and encrypt artifacts.
4. **Retention**: Rotate files per policy (count, age).
5. **Schedule**: Use `schtasks` to run per target; central logs + alerts.

---

## 2) Repository layout (suggested)

```
auto-plc-bk/
  auto_plc_bk/
    __init__.py
    cli.py                # Typer/Click CLI
    config.py             # YAML schema + validation
    targets.py            # CRUD for PLC targets
    studio5000.py         # COM automation wrapper
    cip_probe.py          # pycomm3 controller probe
    backup.py             # run_backup() pipeline
    retention.py          # retention policies
    schedule.py           # Windows Task Scheduler helpers
    logging_cfg.py
  tests/
  examples/
    sample-config.yaml
  pyproject.toml
  README.md
```

---

## 3) Configuration model

A single YAML file governs targets and defaults.

```yaml
# examples/sample-config.yaml
version: 1
defaults:
  storage_root: "D:/plc_backups"
  format: "l5x"              # l5x | acd
  compress: true             # zip backups
  encrypt: false             # optional; if true, use DPAPI or AES key vault
  retention:
    keep_days: 30
    keep_versions: 10
  studio5000:
    min_version: 35
    # optional path override if not in registry
    exe_path: "C:/Program Files/Rockwell Software/Studio 5000/Logix Designer.exe"
targets:
  - name: still01_main
    ip: 10.4.2.2
    slot: 0                   # backplane slot of controller (ControlLogix)
    format: l5x               # override default per target
    schedule: "daily@02:10"   # human-friendly in CLI -> mapped to schtasks
  - name: blend01_aux
    ip: 10.4.2.55
    slot: 0
    format: acd
    schedule: "cron(0 3 * * 1-5)"
```

---

## 4) CLI (production‑ready verbs)

Use **Typer** (or Click). Name the entrypoint `auto-plc-bk`.

### 4.1 Initialize a workspace

```bash
auto-plc-bk init --config "C:\plc\auto-plc-bk.yaml" --storage-root "D:\plc_backups"
```

### 4.2 Add a PLC target (EtherNet/IP, IPv4)

```bash
auto-plc-bk target add still01_main \
  --ip 10.4.2.2 --slot 0 \
  --format l5x \
  --schedule "daily@02:10"
```

List / inspect / remove:

```bash
auto-plc-bk target ls
auto-plc-bk target show still01_main
auto-plc-bk target rm still01_main
```

### 4.3 Validate reachability & identity (no backup yet)

```bash
auto-plc-bk probe --name still01_main
# or:
auto-plc-bk probe --ip 10.4.2.2 --slot 0
```

_What it does_: Establish a CIP session, read Identity Object, confirm product code and revision, read WallClock for timestamp sanity, log serial number/keys.

### 4.4 Run an on‑demand backup

```bash
# Use target settings (format, storage, etc.)
auto-plc-bk backup run --name still01_main

# Override format
auto-plc-bk backup run --name still01_main --format acd
```

**Artifacts**

```
D:\plc_backups\still01_main\2025-08-19_02-10-15\
  still01_main_2025-08-19_021015.l5x
  still01_main_2025-08-19_021015.acd (optional)
  meta.json           # identity, serial, rev, times, hashes
  backup.log
  checksums.sha256
  # .zip if --compress true
```

### 4.5 Schedule backups (Windows Task Scheduler)

Create, list, delete OS tasks (per target).

```bash
# create a daily 02:10 task for the named target
auto-plc-bk schedule add --name still01_main --at "02:10" --daily \
  --run-as ".\svc-plcbk" --password "*****"

# alternative: cron expression
auto-plc-bk schedule add --name still01_main --cron "0 10 2 * * *" \
  --run-as ".\svc-plcbk" --password "*****"

auto-plc-bk schedule ls
auto-plc-bk schedule rm --name still01_main
```

> Under the hood we call `schtasks /Create ...` with a command line that runs:  
> `auto-plc-bk backup run --name still01_main --config "C:\plc\auto-plc-bk.yaml"`

### 4.6 Retention & verification

```bash
# prune old files for a target
auto-plc-bk retention run --name still01_main

# verify a backup artifact opens/validates
auto-plc-bk verify "D:\plc_backups\still01_main\2025-08-19_02-10-15\still01_main_2025-08-19_021015.l5x"
```

---

## 5) Backup pipeline (detailed steps)

### Step 1 — CIP probe (read‑only)

- Open a CIP session to `10.4.2.2` (slot `0` if ControlLogix) and read:
  - Identity: Vendor, Product Type, Product Code, Major/Minor revision, Serial.
  - Module name and electronic keying info (record in metadata).
  - **WallClockTime** (for cross‑checking timestamps — optional).  
- Abort on timeouts, log error category (`network`, `identity_mismatch`, `busy`, etc.).
- Write a pre‑flight `meta.json` to the run directory.

> Recording controller time/identity is useful for cross‑checking “when” the backup was taken vs. controller time using `GSV/SSV` object references and time data types in Logix platforms. This helps correlate artifacts with on‑controller events. fileciteturn0file29

### Step 2 — Launch Studio 5000 and create an offline snapshot

- Ensure Studio 5000 v35+ is installed. Resolve executable path, version and license.
- Start the COM host and open a **temporary project** (or use an existing offline shell for the device family).  
- **UI/COM automation path**:
  1. Connect to controller path (Who‑Active) and **Upload** to an `.acd` in a temp workspace.  
  2. Close online session; keep the offline `.acd` on disk.
- **Hardening**:
  - Retry with exponential backoff (e.g., up to 3 tries).
  - Kill stale Logix Designer processes if automation detects a hang.
  - Allow a configurable **upload timeout** per target.
  - Persist detailed UI automation logs for RCA.

### Step 3 — Export to `.l5x` (if requested)

- From the offline `.acd`, run **Export** to `.l5x` via Studio 5000 COM.  
- Record component counts and sizes for quick sanity checks.

> The conversion/export operations (.acd ⇄ .l5x, batch processing, validation) are driven by a Studio 5000 integration layer (COM automation), as outlined in the **PLC File Conversion Library – How To**. You can reuse that library or port its patterns. fileciteturn0file36

### Step 4 — Package, hash, and (optionally) encrypt

- Compute SHA‑256 for every artifact; write `checksums.sha256`.
- Optional ZIP (store or deflate) with streaming to reduce disk pressure.
- Optional encryption (DPAPI user/machine or AES‑256 with a KMS‑managed key).

### Step 5 — Retention

- Policy = `keep_versions` and/or `keep_days`.  
- Never delete the **most recent successful** backup even if policy would remove it.  
- Emit a retention report with before/after counts.

### Step 6 — Health events & notifications

- Emit structured logs (JSON) + Windows Event Log entries.  
- Optional notification sink (SMTP, Teams/webhook, SIEM).

---

## 6) Implementation notes (Python)

### 6.1 CLI scaffolding (Typer)

```python
# auto_plc_bk/cli.py
import typer
from auto_plc_bk import targets, backup, schedule, retention

app = typer.Typer()

@app.command()
def init(config: str, storage_root: str = typer.Option(...)):
    ...

@app.command("probe")
def probe(name: str = None, ip: str = None, slot: int = 0):
    ...

@app.command("backup")
def backup_run(name: str, format: str = typer.Option(None)):
    ...

# plus: target add/ls/show/rm, schedule add/ls/rm, retention run, verify
if __name__ == "__main__":
    app()
```

### 6.2 CIP probe sketch (`pycomm3`)

```python
# auto_plc_bk/cip_probe.py
from pycomm3 import CIPDriver

def probe_controller(ip: str, slot: int = 0, timeout: float = 3.0) -> dict:
    path = f"1,{slot}"   # backplane route to the slot (ControlLogix)
    with CIPDriver(ip, path=path, timeout=timeout) as conn:
        ident = conn.get_identity()
        # optionally read WallClockTime via MSG/generic service or controller tags if exposed
        return {
            "ip": ip,
            "slot": slot,
            "vendor": ident.vendor,
            "product_type": ident.product_type,
            "product_code": ident.product_code,
            "revision": f"{ident.major}.{ident.minor}",
            "serial_number": ident.serial_number
        }
```

### 6.3 Studio 5000 automation wrapper

- Wrap COM entry points for: start/stop app, **Upload to ACD**, **Export to L5X**, close.  
- Provide blocking calls with timeout + retries; return explicit status codes.  
- Reuse patterns from your Studio 5000 integration library (export/import and batch conversions). fileciteturn0file36

### 6.4 Retention

- Use a small index file per target; prune by age/version; keep last success.

### 6.5 Verification

- For `.l5x`: parse XML header (controller name, rev) quickly; optionally run a dry‑open in Studio 5000.  
- For `.acd`: start Logix Designer headless, attempt to open and close; check exit code.

---

## 7) Windows scheduling (commands you can paste)

> Replace paths and account names as needed. The **Task action** should call your Python entrypoint or packaged EXE.

### 7.1 Create a daily task at 02:10 for `still01_main`

```powershell
schtasks /Create /SC DAILY /ST 02:10 /TN "PLC Backup - still01_main" ^
  /TR "\"C:\Program Files\Python312\python.exe\" -m auto_plc_bk backup run --name still01_main --config \"C:\plc\auto-plc-bk.yaml\"" ^
  /RU ".\svc-plcbk" /RP "********" /RL HIGHEST /F
```

### 7.2 List and delete

```powershell
schtasks /Query /TN "PLC Backup - still01_main" /V /FO LIST
schtasks /Delete /TN "PLC Backup - still01_main" /F
```

### 7.3 Run now

```powershell
schtasks /Run /TN "PLC Backup - still01_main"
```

---

## 8) Operational hardening checklist

- [ ] **Service account** with “Log on as batch job”, local admin only if COM requires it.  
- [ ] **Network**: backup host has routed access to PLCs; firewall allows CIP (TCP/UDP 44818).  
- [ ] **Studio 5000**: pinned to a known minor version; disable auto‑update prompts.  
- [ ] **UI automation** (if used): window titles stable; dialogs auto‑dismissed (no modal blockers).  
- [ ] **Back‑pressure controls**: if PLC is busy or CPU > threshold, skip and re‑try later.  
- [ ] **Run window** staggering: don’t back up many PLCs at once; serialize/limit concurrency.  
- [ ] **Storage health**: low‑space alarms; integrity checks (SHA‑256).  
- [ ] **Retention**: verified test that pruning never removes the most recent success.  
- [ ] **Disaster‑recovery drills**: periodically restore `.l5x` / open `.acd` to confirm usability.

---

## 9) Example end‑to‑end (10.4.2.2, `.l5x`)

```powershell
# 1) Initialize
auto-plc-bk init --config "C:\plc\auto-plc-bk.yaml" --storage-root "D:\plc_backups"

# 2) Register target
auto-plc-bk target add still01_main --ip 10.4.2.2 --slot 0 --format l5x --schedule "daily@02:10"

# 3) Probe
auto-plc-bk probe --name still01_main

# 4) Run now
auto-plc-bk backup run --name still01_main

# 5) Set Windows schedule
auto-plc-bk schedule add --name still01_main --at "02:10" --daily --run-as ".\svc-plcbk" --password "********"
```

Artifacts will appear under: `D:\plc_backups\still01_main\<timestamp>\...`

---

## 10) Notes on metadata & time coherence

- Write controller identity, serial, and firmware revision into `meta.json` for each run.
- Record both **host time** and **controller time** (if available) to help correlate logs and events. In Logix systems, time/clock objects and time data types are well‑defined, which can be useful if you also log timestamps from within the PLC (e.g., alarm events). fileciteturn0file29

---

## 11) Troubleshooting map

| Symptom | Likely cause | Action |
|---|---|---|
| CIP probe times out | Routing, firewall, or controller busy | Verify TCP/UDP 44818; try a larger timeout; check controller mode. |
| Studio 5000 fails to export | License or dialog blocker | Ensure Logix Designer is licensed; run under interactive session or use active desktop service; script UI dialogs. |
| `.l5x` opens but content is missing | Export scope limited | Ensure “include routines / UDT / AOI / Add‑ons” exports are enabled in the export call. fileciteturn0file36 |
| Scheduled task shows “ready” but never runs | Account rights | Grant “Log on as batch job”; check task history and action command line. |
| Retention removed all but oldest | Policy error | Always pin the most recent success; add a safety floor (e.g., keep ≥3). |

---

## 12) Extending the tool

- **Repository catalog**: add tags (Area/Line/Cell) and bulk schedules.  
- **Notification plugins**: SMTP, Microsoft Teams, Slack, ServiceNow.  
- **Storage providers**: S3/Blob/DFS with lifecycle policies.  
- **Integrity**: sign artifacts; store hashes in a DB.  
- **Compare**: diff new `.l5x` vs last to flag structural changes.

---

## 13) References & implementation guides

- **Studio 5000 file conversion / COM automation patterns** — *PLC File Conversion Library – How To Guide* (ACD ↔ L5X conversions, batch processing, validation). fileciteturn0file36  
- **Logix time/objects and data types** — *Logix 5000 Controllers – General Instructions* (GSV/SSV, time and date types). Useful when stamping/validating controller time. fileciteturn0file29

---

### Appendix A — Example `schtasks` action string

If your Python tool is packaged as an EXE at `C:\tools\auto-plc-bk\auto-plc-bk.exe`:

```powershell
schtasks /Create /SC DAILY /ST 02:10 /TN "PLC Backup - still01_main" ^
  /TR "\"C:\tools\auto-plc-bk\auto-plc-bk.exe\" backup run --name still01_main --config \"C:\plc\auto-plc-bk.yaml\"" ^
  /RU ".\svc-plcbk" /RP "********" /RL HIGHEST /F
```

### Appendix B — Minimal “verify” for `.l5x`

```python
import xml.etree.ElementTree as ET
def verify_l5x(path):
    root = ET.parse(path).getroot()
    ctrl = root.find(".//Controller")
    return {
        "name": ctrl.attrib.get("Name"),
        "rev": ctrl.attrib.get("Revision")
    }
```

---

**End of document**

