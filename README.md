# PLC-GBT - Industrial Automation IDE

**Status**: Active Development  
**Last Updated**: September 30, 2025  
**Version**: 1.0.0

---

## 🎯 Project Overview

PLC-GBT is a modern industrial automation IDE that combines a powerful Next.js frontend with a FastAPI backend to provide comprehensive PLC programming, workflow management, and control system design capabilities.

---

## ✅ Current Status

### **Frontend**: Next.js Application - FULLY FUNCTIONAL ✅
- Modern IDE-like interface with File Explorer, Monaco Editor, Workflow Canvas
- Real-time control loop monitoring with WebSocket support
- Git integration UI, Analytics, and Settings panels
- **Running on**: http://localhost:3000

### **Backend**: FastAPI Application - RUNNING SUCCESSFULLY ✅
- RESTful API for file operations, health monitoring
- WebSocket support for real-time updates
- CLI bridge integration
- **Running on**: http://localhost:8000

### **Database Infrastructure**: Optional ⚠️
- Neo4j, PostgreSQL, Redis, Qdrant defined in Docker Compose
- **Not required** for basic frontend/backend development
- **Required** for PLC Memory System and advanced features

---

## 🚀 Quick Start

Get up and running in **5 minutes**:

```bash
# 1. Setup Python environment (Python 3.10+, 3.12 recommended)
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start backend
cd plc-gbt-stack
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (in new terminal)
cd plc-gbt-stack/ui/nextjs
npm install  # First time only
npm run dev

# 4. Open http://localhost:3000
```

**For detailed setup instructions**: See [Quick Start Guide](docs/QUICK_START.md)

---

## 📁 Repository Structure

| Path | Purpose | Status |
|------|---------|--------|
| `plc-gbt-stack/ui/nextjs/` | **Next.js frontend application** | ✅ **Fully Functional** |
| `plc-gbt-stack/api/` | **FastAPI backend service** | ✅ **Running** |
| `plc-gbt-stack/scripts/ai/` | **PLC Memory CLI and AI tools** | ⚠️ **Requires databases** |
| `src/plc_format_converter/` | **PLC format conversion package** | ⏸️ **In development** |
| `docs/` | **Current documentation** | ✅ **Maintained** |
| `.venv/` | **Python virtual environment** | ✅ **Configured** |
| `plc-gbt-stack/docker-compose.yml` | **Database & service definitions** | ⚠️ **Services not started** |

**Note**: The `ui/` directory at repository root contains only legacy package manifests. The **actual frontend** is in `plc-gbt-stack/ui/nextjs/`.

---

## 🛠 Tech Stack

### Frontend
- **Framework**: Next.js 15 (App Router)
- **UI Library**: React 18
- **Language**: TypeScript (strict mode)
- **Styling**: Tailwind CSS
- **State**: Zustand + React Query
- **Editor**: Monaco Editor
- **Workflows**: React Flow
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Language**: Python 3.12
- **Protocols**: REST + WebSocket
- **Validation**: Pydantic

### Infrastructure (Optional)
- **Knowledge Graph**: Neo4j 5
- **Relational DB**: PostgreSQL 15
- **Cache**: Redis 7
- **Vector DB**: Qdrant
- **Orchestration**: Docker Compose

---

## 🎯 Key Features

### ✅ Currently Working:
- **IDE Interface**: Full-featured industrial automation IDE
- **File Management**: Browse, view files from backend storage
- **Code Editing**: Monaco editor with syntax highlighting
- **Workflow Designer**: Visual workflow canvas with drag-and-drop
- **Control Loop Monitoring**: Real-time dashboard with WebSocket updates
- **Git Integration UI**: Version control interface (backend connection pending)
- **Analytics**: Metrics visualization
- **Settings Management**: Configuration panels

### ⏸️ In Development:
- **PLC Memory System**: Requires database containers to be started
- **PLC Format Conversion**: L5X ↔ JSON conversion pipeline
- **Advanced Workflows**: Backend execution engine integration
- **AI Assistant**: LLM chat integration
- **Authentication**: User management and security

---

## 📖 Documentation

### Getting Started:
- **[Quick Start](docs/QUICK_START.md)** - Setup in 5 minutes
- **[Development Guide](docs/DEVELOPMENT_GUIDE.md)** - Comprehensive reference
- **[Documentation Reconciliation Report](docs/DOCUMENTATION_RECONCILIATION_REPORT.md)** - Recent changes

### Technical Documentation:
- [PLC Memory System Overview](docs/plc_memory_system_overview.md)
- [API Creation Methodology](plc-gbt-stack/docs/API_CREATION_METHODOLOGY.md)
- [AI Task Orchestrator Guide](plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md)
- [Architecture Decisions](docs/architecture-decisions.md)
- [Coding Standards](docs/coding-standards.md)

### Archived Documentation:
Legacy documentation has been moved to `quarantine/` directories. These are for historical reference only and do not reflect current implementation.

---

## 🔧 Development Workflow

### Daily Development:

```bash
# Start backend
cd plc-gbt-stack
source ../.venv/bin/activate
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# Start frontend (new terminal)
cd plc-gbt-stack/ui/nextjs
npm run dev

# Develop → changes auto-reload
```

### With Databases (for advanced features):

```bash
# Start databases first
cd plc-gbt-stack
docker-compose up -d neo4j postgres redis qdrant

# Then start backend and frontend as above
```

---

## 🧪 Testing

```bash
# Frontend tests
cd plc-gbt-stack/ui/nextjs
npm run lint
npx tsc --noEmit

# Backend tests
curl http://localhost:8000/api/v1/files
curl http://localhost:8000/api/v1/health

# WebSocket test
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        print('Connected:', json.loads(await ws.recv())['type'])
asyncio.run(test())
"
```

---

## 🚨 Important Notes

### Theia IDE Removed
The Theia-based IDE framework has been **completely removed**. Any documentation referencing `ui/theia/` or Theia components is outdated.

### Python Version Critical
Backend **requires Python 3.10+** (3.12 recommended). The code uses `datetime.UTC` which was added in Python 3.11.

### Database Containers Optional
You can develop frontend and backend features **without** starting database containers. Databases are only needed for:
- PLC Memory System operations
- Knowledge graph queries
- Vector similarity search
- Advanced caching features

### Port Considerations
- Port 3000: Next.js dev server (primary)
- Port 3000: n8n-mcp also claims this port (but not interfering currently)
- Port 8000: FastAPI backend
- Port 5678: N8N workflow automation
- Port 8811: MCP Docker server

---

## 🆘 Troubleshooting

### "No module named 'uvicorn'"
```bash
source .venv/bin/activate
pip install uvicorn fastapi websockets
```

### "Port 3000 already in use"
```bash
lsof -i :3000
# Stop conflicting service if needed
docker stop plc-n8n-mcp
```

### "No files in workspace" in UI
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/files
# Refresh browser
```

For more troubleshooting, see [Quick Start Guide](docs/QUICK_START.md).

---

## 📊 Project Status

| Component | Status | Notes |
|-----------|--------|-------|
| Next.js Frontend | ✅ Functional | Full IDE interface |
| FastAPI Backend | ✅ Running | REST + WebSocket |
| File Operations | ✅ Working | Real filesystem integration |
| Control Loops | ✅ Partial | UI ready, backend in progress |
| Workflows | ✅ UI Complete | Backend execution pending |
| Git Integration | ⏸️ In Progress | UI ready, backend needed |
| PLC Memory | ⏸️ Requires DB | Databases need to be started |
| Databases | ⏸️ Not Started | Optional for basic dev |
| AI Assistant | ⏸️ Planned | UI toggle present |

---

## 👥 Contributing

### Prerequisites:
- Python 3.10+ (3.12 recommended)
- Node.js 18+
- Docker Desktop (optional)

### Before Starting:
1. Read [Development Guide](docs/DEVELOPMENT_GUIDE.md)
2. Review [Coding Standards](docs/coding-standards.md)
3. Check [Architecture Decisions](docs/architecture-decisions.md)
4. Follow [Quick Start](docs/QUICK_START.md) for environment setup

### Development Standards:
- **TypeScript**: Zero `any` types, strict mode
- **Python**: Type hints, async/await patterns
- **Testing**: >95% automated test coverage required
- **Documentation**: Update docs with code changes

---

## 📞 Support & Resources

- **Quick Start**: `docs/QUICK_START.md`
- **Development Guide**: `docs/DEVELOPMENT_GUIDE.md`
- **API Documentation**: `plc-gbt-stack/docs/API_CREATION_METHODOLOGY.md`
- **Reconciliation Report**: `docs/DOCUMENTATION_RECONCILIATION_REPORT.md`

---

## 🎉 What's New (September 2025)

- ✅ **Migrated from Theia to Next.js** - Complete frontend rewrite
- ✅ **Fixed Backend** - FastAPI now fully operational
- ✅ **WebSocket Support** - Real-time control loop updates
- ✅ **Modern Tech Stack** - Latest Next.js, React, TypeScript
- ✅ **Comprehensive UI** - Full IDE experience in browser
- ✅ **Python 3.12** - Upgraded to modern Python
- ✅ **Documentation Update** - Docs now reflect actual implementation

---

**PLC-GBT aims to modernize PLC engineering workflows with a powerful web-based IDE and comprehensive backend services.**