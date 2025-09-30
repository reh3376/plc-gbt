# PLC-GBT Development Guide

**Last Updated**: September 30, 2025  
**Status**: Reflects current implementation state  

---

## Purpose
This guide is the canonical entry point for continuing work on the PLC-GBT platform. It summarizes the **actual current state**, defines immediate priorities, and points to supporting documentation.

**Important**: This guide has been updated to reflect the current Next.js architecture. The Theia IDE framework has been **completely removed** from the codebase.

---

## 📊 Current State Snapshot

### Frontend: Next.js Application - FULLY FUNCTIONAL ✅

**Location**: `plc-gbt-stack/ui/nextjs/`  
**Status**: Production-ready IDE interface running on **port 3000**  
**Tech Stack**: Next.js 15, React 18, TypeScript, Tailwind CSS, Zustand, React Query

**Functional Components**:
- ✅ File Explorer with backend integration
- ✅ Monaco Code Editor with multi-tab support
- ✅ Workflow Canvas (React Flow based)
- ✅ Control Loop Dashboard with WebSocket
- ✅ Git Integration UI (backend pending)
- ✅ Analytics Dashboard
- ✅ Settings Panel
- ✅ AI Assistant toggle

**Note**: Theia IDE completely removed. All references to `ui/theia/*` are outdated.

### Backend: FastAPI Application - RUNNING SUCCESSFULLY ✅

**Location**: `plc-gbt-stack/api/cli_api_bridge.py`  
**Status**: Fully operational on **port 8000**  
**Tech Stack**: FastAPI, Uvicorn, WebSockets, Python 3.12

**Functional Endpoints**:
- ✅ `GET /api/v1/files` - File operations
- ✅ `POST /api/v1/files` - Create files/folders
- ✅ `GET /api/v1/health` - Health check
- ✅ `WebSocket /ws` - Real-time control loop updates

**Requirements**:
- **Python 3.10+** (3.12 recommended - code uses `datetime.UTC`)
- Virtual environment at `.venv/`
- Dependencies from `requirements.txt`

### Database Infrastructure: NOT RUNNING ⚠️

Docker Compose defines these services, but they are **not currently started**:

- ⏸️ Neo4j (knowledge graph) - ports 7474, 7687
- ⏸️ PostgreSQL (metadata) - port 5432
- ⏸️ Redis (caching) - port 6379
- ⏸️ Qdrant (vector search) - port 6333

**Impact**: PLC Memory System features require starting these containers.

**To Start**:
```bash
cd plc-gbt-stack
docker-compose up -d neo4j postgres redis qdrant
```

### External Services: RUNNING ✅

- ✅ N8N Workflow Automation (port 5678)
- ✅ MCP Docker Server (port 8811)

---

## 🎯 Near-Term Priorities

### Priority 1: Environment Stabilization
1. Resolve port 3000 conflict (Next.js vs n8n-mcp)
2. Start database containers for full functionality
3. Create automated startup scripts
4. Validate all services integration

### Priority 2: Frontend Enhancement
1. Complete file operations (create, edit, save, delete)
2. Implement Git backend integration
3. Expand Control Loop features
4. Connect Workflow execution to backend
5. Integrate AI Assistant panel

### Priority 3: Backend Expansion
1. Additional API endpoints for all UI features
2. Database integration (Neo4j, PostgreSQL)
3. PLC conversion pipeline (L5X ↔ JSON)
4. Authentication system
5. Enhanced WebSocket features

### Priority 4: PLC Memory System
1. Start database containers
2. Initialize database schemas
3. Test memory CLI functionality
4. Build knowledge graph
5. Implement vector search

---

## 🚀 Quick Start

See **[Quick Start Guide](./QUICK_START.md)** for detailed setup instructions.

**TL;DR**:
```bash
# 1. Python environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Start backend (in plc-gbt-stack/)
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend (in plc-gbt-stack/ui/nextjs/)
npm install  # First time only
npm run dev

# 4. Access at http://localhost:3000
```

---

## 📐 Architecture Overview

```
Browser (localhost:3000)
    ↓
Next.js Frontend
├── File Explorer
├── Monaco Editor  
├── Workflow Canvas
├── Control Loop Dashboard
└── Settings/Analytics
    ↓ HTTP/WebSocket
FastAPI Backend (localhost:8000)
├── /api/v1/files (REST)
├── /ws (WebSocket)
└── /api/v1/health
    ↓ (Optional)
Database Stack (Docker)
├── Neo4j (7474, 7687)
├── PostgreSQL (5432)
├── Redis (6379)
└── Qdrant (6333)
```

---

## 🔧 Development Modes

### Mode 1: Frontend-Only
**Use for**: UI development, styling, layouts  
**Start**: `cd plc-gbt-stack/ui/nextjs && npm run dev`

### Mode 2: Frontend + Backend (Recommended)
**Use for**: Feature development with API integration  
**Start**: Backend + Frontend as shown in Quick Start

### Mode 3: Full Stack
**Use for**: PLC Memory, knowledge graphs, vector search  
**Start**: Databases + Backend + Frontend

---

## 🧪 Testing

### Frontend
```bash
cd plc-gbt-stack/ui/nextjs
npm run lint
npx tsc --noEmit
npm test  # When tests exist
```

### Backend
```bash
curl http://localhost:8000/api/v1/files
curl http://localhost:8000/api/v1/health
```

### Integration
```bash
# Test WebSocket
python3 -c "
import asyncio, websockets, json
async def test():
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        print(json.loads(await ws.recv())['type'])
asyncio.run(test())
"
```

---

## 📚 Related Documentation

### Core Guides:
- [Quick Start](./QUICK_START.md) - Setup in 5 minutes
- [Documentation Reconciliation Report](./DOCUMENTATION_RECONCILIATION_REPORT.md) - What changed
- [PLC Memory System Overview](./plc_memory_system_overview.md) - Memory system details

### System Documentation:
- [API Creation Methodology](../plc-gbt-stack/docs/API_CREATION_METHODOLOGY.md)
- [AI Task Orchestrator Guide](../plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_GUIDE.md)
- [AI Task Orchestrator TypeScript Guide](../plc-gbt-stack/docs/AI_TASK_ORCHESTRATOR_TS_GUIDE.md)

### Standards:
- [Architecture Decisions](./architecture-decisions.md)
- [Coding Standards](./coding-standards.md)
- [Naming Conventions](./naming-conventions.md)

---

## 🚨 Known Issues

1. **Port 3000 Conflict**: Both Next.js and n8n-mcp use port 3000. Next.js is currently serving successfully.
2. **Databases Not Running**: Full stack features require starting Docker containers.
3. **Theia References**: Some docs may still reference removed Theia IDE - ignore these.

---

## 🗃️ Deprecated Components

### Theia IDE - COMPLETELY REMOVED

The Theia-based IDE has been **purged** from the codebase:
- All `ui/theia/*` directories deleted
- Replaced by Next.js application
- Provides superior functionality and developer experience

**If you encounter Theia references, they are outdated and should be ignored.**

---

## ✅ Pre-Development Checklist

- [ ] Read this Development Guide
- [ ] Complete Quick Start setup
- [ ] Understand current architecture (Next.js + FastAPI)
- [ ] Know which development mode you need
- [ ] Set up Python 3.12 virtual environment
- [ ] Verify services are running

---

**This guide accurately reflects the PLC-GBT codebase as of September 30, 2025.**
