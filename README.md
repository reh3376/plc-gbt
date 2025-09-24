# PLC-GBT

PLC-GBT aims to modernize PLC engineering workflows by pairing an automation-focused backend with a Theia-based IDE front end.
The project is still in early development; many documented capabilities are not yet implemented.

## Current Status
- **Back-end:** A FastAPI application (`plc-gbt-stack/`) exposes preliminary CLI bridging, but imports and converter modules need
  to be completed before the service is runnable end to end.
- **Front-end:** The `ui/` directory currently contains only package manifests and testing scaffolds. No IDE or web assets are
  built yet.
- **Tooling:** The `src/plc_format_converter/` package is a placeholder. Conversion handlers, models, and CLI entry points must
  be implemented.

Refer to the [PLC-GBT Development Guide](docs/DEVELOPMENT_GUIDE.md) for the active roadmap, priorities, and links to supporting
references.

## Installation

For detailed installation instructions, see [INSTALLATION.md](INSTALLATION.md).

### Quick Install
```bash
git clone https://github.com/reh3376/plc-gbt.git
cd plc-gbt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Starting the API Server
```bash
cd plc-gbt-stack/api
uvicorn main:app --reload
```

### Running Tests
```bash
pytest
```

### Using the CLI
```bash
plc-memory --help
```

## Features

- **PLC Format Conversion**: Convert between various PLC file formats
- **Memory Management**: Multi-database memory system for knowledge storage
- **Workflow Engine**: Create and manage automation workflows
- **AI Integration**: OpenAI fine-tuned models for industrial automation
- **Real-time Monitoring**: System health and performance monitoring
- **Security**: Enterprise-grade security with authentication and authorization

## Repository Layout
| Path | Purpose |
|------|---------|
| `plc-gbt-stack/` | FastAPI service layer and CLI bridge |
| `src/plc_format_converter/` | Python package scaffolding for PLC format conversion |
| `ui/` | Planned Theia IDE workspace (not yet implemented) |
| `docs/` | Maintained documentation for current workstreams |
| `quarantine/`, `docs/quarantine/` | Archived reports and guides that no longer reflect the live code |

## Requirements

- Python 3.12 or higher
- Node.js 20.x or higher (for frontend development)
- Docker and Docker Compose (for services)
- Git

## Getting Started
1. Use the existing development virtual environment (or create it with uv) and ensure core dev tools are installed (uv, ruff):
   ```bash
   # If uv is not installed
   python -m pip install --upgrade pip
   pip install uv

   # Create/activate venv with uv (if not already present)
   uv venv
   source .venv/bin/activate

   # Install project (and dev tools) from pyproject.toml
   uv pip install -e .[dev]
   ```
   Notes:
   - Dependencies are managed via `pyproject.toml` (no requirements.txt when using uv).
   - `ruff` ships as part of the `[project.optional-dependencies].dev` group.
2. Explore the FastAPI stack and CLI integration points in `plc-gbt-stack/` to identify gaps referenced in the development guide.
3. Follow the tasks outlined in `docs/DEVELOPMENT_GUIDE.md` before expanding functionality.

External PLC repositories (`plc-gbt-git`, `plc-100`, `plc-200`, `plc-300`, `plc-400`, `plc-500`) are **not** linked yet; scripts
and configuration must be added as part of upcoming work.

## Documentation
The following documents are authoritative for ongoing development:
- [PLC-GBT Codebase Review (Version 2)](docs/CODEBASE_REVIEW_V2.md)
- [PLC-GBT Development Guide](docs/DEVELOPMENT_GUIDE.md)
- [Functional Specification & Alignment Plan](docs/FSD_ALIGNMENT_PLAN.md)
- [PLC Memory System Overview](docs/plc_memory_system_overview.md)
- [Workflow Node Creation Guide](docs/workflow_node_creation_guide.md)
- [Architecture Decisions](docs/architecture-decisions.md)
- [Coding Standards](docs/coding-standards.md)
- [Naming Conventions](docs/naming-conventions.md)

Legacy documentation that overstated feature completeness has been relocated to the quarantine directories for archival purposes. If you find a missing link to documentation it may reside in one of the quarantine directories, you can search for it there, but before it can be removed from the quarantine directory it will require review and explicit user permission. 
