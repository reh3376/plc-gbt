# 🚀 PLC-GBT Quick Start Guide

**Last Updated**: September 30, 2025  
**Status**: Reflects current working implementation  
**Estimated Time**: 5-10 minutes for basic setup  

---

## ✅ Prerequisites

- **Python 3.10 or higher** (Python 3.12 recommended)
- **Node.js 18 or higher**  
- **Docker Desktop** (optional - only needed for full database stack)
- **Git** (for repository management)

---

## 🎯 Quick Start (Basic - No Databases)

Get the frontend and backend running in **under 5 minutes**:

### Step 1: Setup Python Environment

```bash
cd /path/to/plc-gbt

# Create virtual environment with Python 3.12
python3.12 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On macOS/Linux
# OR
.venv\Scripts\activate     # On Windows

# Install Python dependencies
pip install -r requirements.txt
```

**Verify Python setup**:
```bash
python --version  # Should show Python 3.12.x
pip list | grep fastapi  # Should show fastapi installed
```

### Step 2: Start FastAPI Backend

```bash
# Make sure virtual environment is activated
cd plc-gbt-stack
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify backend is running**:
```bash
# In a new terminal
curl http://localhost:8000/api/v1/files
# Should return JSON with file listings
```

### Step 3: Setup and Start Next.js Frontend

```bash
# In a new terminal
cd plc-gbt-stack/ui/nextjs

# Install Node.js dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output**:
```
  ▲ Next.js 15.4.2-canary.15
  - Local:        http://localhost:3000
  
 ✓ Starting...
 ✓ Ready in 2.5s
```

### Step 4: Access the Application

Open your browser to: **http://localhost:3000**

You should see the **PLC-GBT Industrial Automation IDE** with:
- ✅ File Explorer (left sidebar)
- ✅ Monaco Editor (main area)
- ✅ Workflow Management
- ✅ Control Loop Dashboard
- ✅ Settings and Analytics

---

## 🐳 Full Stack Setup (With Databases)

For **complete functionality** including PLC Memory System, knowledge graphs, and caching:

### Step 1: Start Database Containers

```bash
cd plc-gbt-stack

# Start all database services
docker-compose up -d neo4j postgres redis qdrant

# Wait ~30 seconds for containers to initialize

# Verify all containers are healthy
docker-compose ps
```

**Expected containers**:
- `plc-neo4j` (ports 7474, 7687) - Status: healthy
- `plc-postgres` (port 5432) - Status: healthy
- `plc-redis` (port 6379) - Status: healthy  
- `plc-qdrant` (port 6333) - Status: running

### Step 2: Verify Database Connectivity

```bash
# Test Neo4j
curl -u neo4j:password http://localhost:7474

# Test Redis
docker exec plc-redis redis-cli ping
# Should return: PONG

# Test PostgreSQL
docker exec plc-postgres pg_isready -U plc_user
# Should return: accepting connections

# Test Qdrant
curl http://localhost:6333/dashboard
# Should return HTML
```

### Step 3: Initialize PLC Memory System

```bash
source .venv/bin/activate
cd plc-gbt-stack

# Check PLC Memory status
python scripts/ai/plc_memory_cli.py status

# (Optional) Ingest sample data
python scripts/ai/plc_memory_cli.py ingest --path ./api --depth standard
```

### Step 4: Start Backend and Frontend

Follow Steps 2-4 from Basic Quick Start above.

---

## 🔍 Verification Checklist

After completing setup, verify everything works:

### Frontend Checks:
- [ ] Navigate to http://localhost:3000
- [ ] File Explorer shows files (should display backend files)
- [ ] Click "Workflows" tab - UI should load
- [ ] Click "Control Loops" tab - Dashboard should load
- [ ] Check browser console - should see WebSocket connection logs

### Backend Checks:
- [ ] `curl http://localhost:8000/api/v1/files` returns JSON
- [ ] `curl http://localhost:8000/api/v1/health` returns health status
- [ ] Backend terminal shows log entries when frontend makes requests

### Database Checks (if running full stack):
- [ ] Neo4j browser accessible at http://localhost:7474
- [ ] Qdrant dashboard at http://localhost:6333/dashboard
- [ ] `plc-memory status` command succeeds
- [ ] No connection errors in backend logs

---

## 🚨 Common Issues & Solutions

### Issue: "No module named 'uvicorn'"

**Solution**:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Install missing dependencies
pip install uvicorn fastapi websockets
```

### Issue: "Port 3000 already in use"

**Solution**:
```bash
# Check what's using port 3000
lsof -i :3000

# If n8n-mcp is running, stop it
docker stop plc-n8n-mcp

# Then restart Next.js
npm run dev
```

### Issue: Backend returns "datetime.UTC" ImportError

**Cause**: Running with Python < 3.11

**Solution**:
```bash
# Use Python 3.12
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: "No files in workspace" in File Explorer

**Causes**:
1. Backend not running
2. Backend not serving files correctly

**Solution**:
```bash
# Verify backend is running
curl http://localhost:8000/api/v1/files

# Check backend terminal for errors

# Refresh browser (Ctrl+R or Cmd+R)
```

### Issue: WebSocket connection errors in Control Loop Dashboard

**Cause**: Backend WebSocket endpoint not accessible

**Solution**:
```bash
# Test WebSocket endpoint
python3 -c "
import asyncio, websockets, json
async def test(): 
    async with websockets.connect('ws://localhost:8000/ws') as ws:
        msg = await ws.recv()
        print(f'Connected: {json.loads(msg)[\"type\"]}')
asyncio.run(test())
"
```

### Issue: Database connection errors

**Cause**: Docker containers not running

**Solution**:
```bash
cd plc-gbt-stack
docker-compose up -d neo4j postgres redis qdrant
# Wait 30 seconds
docker-compose ps
```

---

## 🛠 Development Workflow

### Daily Development Cycle:

1. **Start Backend**:
   ```bash
   cd plc-gbt-stack
   source ../.venv/bin/activate
   python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend** (in new terminal):
   ```bash
   cd plc-gbt-stack/ui/nextjs
   npm run dev
   ```

3. **Develop** → Make changes, auto-reload handles the rest

4. **Test**:
   ```bash
   # Frontend linting
   npm run lint
   
   # Backend can be tested with curl or browser
   ```

### Full Stack Development (with databases):

```bash
# Terminal 1: Databases
cd plc-gbt-stack
docker-compose up -d neo4j postgres redis qdrant

# Terminal 2: Backend
source ../.venv/bin/activate
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Frontend
cd plc-gbt-stack/ui/nextjs
npm run dev

# Terminal 4: Development / Testing
cd plc-gbt-stack
source ../.venv/bin/activate
python scripts/ai/plc_memory_cli.py status
```

---

## 📊 Service URLs Reference

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **Frontend** | http://localhost:3000 | ✅ Running | Next.js IDE interface |
| **Backend API** | http://localhost:8000 | ✅ Running | FastAPI REST & WebSocket |
| **Neo4j Browser** | http://localhost:7474 | ⏸️ Stopped | Knowledge graph UI |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | ⏸️ Stopped | Vector search UI |
| **N8N Workflows** | http://localhost:5678 | ✅ Running | Workflow automation |
| **MCP Docker** | http://localhost:8811 | ✅ Running | OpenAPI schema validation |

---

## 🎯 What You Can Do Right Now (Without Databases)

### ✅ Fully Functional:
- **File Management**: Browse, view files from backend storage
- **UI Development**: All panels and components work
- **API Testing**: All REST endpoints functional
- **WebSocket**: Real-time control loop updates
- **Workflow UI**: Canvas and visualization (without persistence)
- **Git UI**: Interface available (backend integration pending)

### ⏸️ Requires Databases:
- **PLC Memory CLI**: Ingestion, query, backup operations
- **Knowledge Graph**: Relationship queries and graph visualizations
- **Vector Search**: Similarity search for PLC components
- **Advanced Caching**: Redis-based performance optimization

---

## 📚 Next Steps After Setup

1. **Explore the UI**: Navigate through all panels and features
2. **Review Architecture**: Read updated DEVELOPMENT_GUIDE.md  
3. **Check API**: Visit http://localhost:8000/docs (if Swagger UI configured)
4. **Test File Operations**: Create, upload, and manage files
5. **Review Code**: Examine Next.js components in `plc-gbt-stack/ui/nextjs/src/`

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check `docs/TROUBLESHOOTING.md` (to be created)
2. Review `docs/DOCUMENTATION_RECONCILIATION_REPORT.md` for known issues
3. Check backend logs for error messages
4. Verify all prerequisites are installed

---

**This guide reflects the ACTUAL current state of the codebase as of September 30, 2025.**
