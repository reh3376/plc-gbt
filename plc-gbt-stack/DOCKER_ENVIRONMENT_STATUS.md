# 🐳 PLC-GBT Docker Environment - Current Status

**Last Updated**: September 30, 2025  
**Status**: Partial Infrastructure Running  
**Development Mode**: Frontend + Backend (No Databases)  

---

## 📊 Current Container Status

### ✅ Running Containers

| Container | Image | Status | Ports | Purpose |
|-----------|-------|--------|-------|---------|
| **plc-n8n** | `n8nio/n8n:latest` | ✅ Running (healthy) | 127.0.0.1:5678 | Workflow automation |
| **plc-n8n-mcp** | `ghcr.io/czlonkowski/n8n-mcp:latest` | ✅ Running (healthy) | 127.0.0.1:3000 | N8N MCP integration |
| **docker_labs-ai-tools...** | `mcp/docker:0.0.17` | ✅ Running | 0.0.0.0:8811 | MCP Docker server |

### ⏸️ Defined but Not Started

| Container | Image | Defined Ports | Purpose | Status |
|-----------|-------|---------------|---------|--------|
| **plc-neo4j** | `neo4j:5-enterprise` | 7474, 7687 | Knowledge graph database | ⏸️ Not Started |
| **plc-postgres** | `postgres:15-alpine` | 5432 | Metadata storage | ⏸️ Not Started |
| **plc-redis** | `redis:7-alpine` | 6379 | Caching & pub/sub | ⏸️ Not Started |
| **plc-qdrant** | `qdrant/qdrant:latest` | 6333 | Vector database | ⏸️ Not Started |
| **plc-vault** | `vault:1.15` | 8200 | Secrets management | ⏸️ Not Started |
| **mtls-proxy** | Custom build | 8443 | mTLS reverse proxy | ⏸️ Not Started |
| **safety-interlocks** | Custom build | 127.0.0.1:8300 | Safety systems | ⏸️ Not Started |
| **etl-worker** | Custom build | - | ETL processing | ⏸️ Not Started |
| **gateway** | Custom build | 127.0.0.1:8000 | Gateway API | ⏸️ Not Started |
| **plc-memory** | Custom build | - | PLC Memory CLI | ⏸️ Not Started |

---

## 🚦 Service Availability

### ✅ Currently Accessible Services

| Service | URL | Status | Notes |
|---------|-----|--------|-------|
| **Next.js Frontend** | http://localhost:3000 | ✅ Running | PLC-GBT IDE interface |
| **FastAPI Backend** | http://localhost:8000 | ✅ Running | REST API + WebSocket |
| **Backend Health** | http://localhost:8000/api/v1/health | ✅ Available | Health check endpoint |
| **Backend WebSocket** | ws://localhost:8000/ws | ✅ Available | Real-time updates |
| **N8N UI** | http://localhost:5678 | ✅ Running | Workflow automation |
| **MCP Docker** | http://localhost:8811 | ✅ Running | OpenAPI schema MCP |

### ⏸️ Not Currently Available (Requires Container Start)

| Service | URL (when started) | Purpose |
|---------|-------------------|---------|
| **Neo4j Browser** | http://localhost:7474 | Knowledge graph UI |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector search UI |
| **Vault UI** | http://localhost:8200 | Secrets management |

---

## 🔧 Starting Database Containers

### Quick Start (Core Databases Only)

```bash
cd /path/to/plc-gbt/plc-gbt-stack

# Start the 4 core databases
docker-compose up -d neo4j postgres redis qdrant

# Wait ~30 seconds for initialization

# Verify containers are healthy
docker-compose ps

# Expected output:
# plc-neo4j     ... Up (healthy)
# plc-postgres  ... Up (healthy)  
# plc-redis     ... Up (healthy)
# plc-qdrant    ... Up
```

### Full Stack (All Services)

```bash
cd /path/to/plc-gbt/plc-gbt-stack

# Start all defined services
docker-compose up -d

# This will start:
# - All 4 core databases
# - Vault (secrets management)
# - Safety interlocks
# - ETL worker
# - Gateway API
# - mTLS proxy
# - PLC Memory CLI container
```

**Note**: Some services require custom builds and may fail on first attempt. Core databases (neo4j, postgres, redis, qdrant) should start successfully.

---

## 🔍 Container Health Checks

### Verify Database Connectivity

```bash
# Neo4j
curl -u neo4j:password http://localhost:7474
# Should return Neo4j browser HTML

# PostgreSQL
docker exec plc-postgres pg_isready -U plc_user
# Should return: accepting connections

# Redis
docker exec plc-redis redis-cli ping
# Should return: PONG

# Qdrant
curl http://localhost:6333/dashboard
# Should return dashboard HTML
```

### Check Container Logs

```bash
# View logs for specific container
docker-compose logs -f neo4j
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f qdrant

# View all logs
docker-compose logs -f
```

---

## 🎯 Impact on Development

### ✅ Works WITHOUT Databases:

- **Frontend Development**: Full UI functionality
- **Backend API**: File operations, health checks
- **WebSocket**: Real-time control loop updates
- **Workflow UI**: Canvas and visualization
- **Git UI**: Interface components
- **File Operations**: Browse, view files

### ⏸️ Requires Databases:

- **PLC Memory CLI**: Ingestion, query, backup operations
- **Knowledge Graph**: Neo4j relationship queries
- **Vector Search**: Qdrant similarity search
- **Advanced Caching**: Redis performance optimization
- **Metadata Persistence**: PostgreSQL storage
- **Workflow Execution**: Database-backed state
- **Control Loop Persistence**: Historical data storage

---

## 🚨 Known Issues

### Issue 1: Port 3000 Conflict

**Problem**: Both Next.js dev server and n8n-mcp container bind to port 3000

**Current Behavior**: Next.js is successfully serving on port 3000

**Resolution Options**:
1. **Stop n8n-mcp** (if not needed):
   ```bash
   docker stop plc-n8n-mcp
   ```

2. **Reconfigure n8n-mcp** (permanent fix):
   ```yaml
   # In docker-compose.yml, change:
   n8n-mcp:
     ports:
       - '127.0.0.1:3001:3000'  # Change from 3000:3000
   ```

### Issue 2: Gateway Container Port Conflict

**Problem**: docker-compose defines `gateway` on port 8000, but FastAPI backend is already using 8000

**Current Behavior**: Backend running successfully, gateway container not started

**Resolution**: Gateway container is not needed for current development (FastAPI backend provides equivalent functionality)

---

## 🛠️ Container Management Commands

### Basic Operations

```bash
# Start specific service
docker-compose up -d <service-name>

# Stop specific service
docker-compose stop <service-name>

# Restart service
docker-compose restart <service-name>

# Remove container (keeps data)
docker-compose rm -f <service-name>

# View status
docker-compose ps

# View logs
docker-compose logs -f <service-name>
```

### Database Operations

```bash
# Start all databases
docker-compose up -d neo4j postgres redis qdrant

# Stop all databases
docker-compose stop neo4j postgres redis qdrant

# Restart databases
docker-compose restart neo4j postgres redis qdrant

# Remove databases (⚠️ DELETES DATA)
docker-compose down -v neo4j postgres redis qdrant
```

### Complete Stack Operations

```bash
# Start everything
docker-compose up -d

# Stop everything
docker-compose stop

# Stop and remove (keeps volumes)
docker-compose down

# Stop, remove, and delete data (⚠️ DESTRUCTIVE)
docker-compose down -v
```

---

## 📋 Development Scenarios

### Scenario 1: Frontend-Only Development

**What You Need**: Nothing (use mock data in components)

**Docker Containers**: None required

**Start Command**: 
```bash
cd plc-gbt-stack/ui/nextjs
npm run dev
```

### Scenario 2: Frontend + Backend Development (Current Default)

**What You Need**: Python 3.12 venv with dependencies

**Docker Containers**: None required (though N8N and MCP are running)

**Start Commands**:
```bash
# Terminal 1: Backend
cd plc-gbt-stack
source ../.venv/bin/activate
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend
cd plc-gbt-stack/ui/nextjs
npm run dev
```

### Scenario 3: Full Stack Development

**What You Need**: Python 3.12 venv + Docker Desktop

**Docker Containers**: neo4j, postgres, redis, qdrant

**Start Commands**:
```bash
# Use automated script
./scripts/dev/start-full-stack.sh

# OR manually:
# Terminal 1: Databases
cd plc-gbt-stack
docker-compose up -d neo4j postgres redis qdrant

# Terminal 2: Backend
source ../.venv/bin/activate
python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload

# Terminal 3: Frontend
cd ui/nextjs
npm run dev
```

---

## 🔍 Container Network Configuration

### Networks Defined

```yaml
plc-internal-network:    # 172.20.0.0/16
plc-database-network:    # 172.21.0.0/16 (internal only)
plc-security-network:    # 172.22.0.0/16
```

### Container Connectivity

**From Host Machine**:
- Use `localhost:<port>` for exposed ports
- Examples: `localhost:3000`, `localhost:8000`, `localhost:7474`

**Between Containers** (when running in Docker):
- Use service names: `neo4j:7687`, `postgres:5432`, `redis:6379`, `qdrant:6333`

**From Docker Containers to Host**:
- Use `host.docker.internal:<port>`
- Example: MCP browser automation uses `host.docker.internal:3000`

---

## 📊 Resource Usage (When All Databases Running)

Estimated resource requirements:

| Container | Memory | CPU | Disk |
|-----------|--------|-----|------|
| Neo4j | ~2-4 GB | Medium | ~1 GB |
| PostgreSQL | ~256 MB | Low | ~500 MB |
| Redis | ~100 MB | Low | ~100 MB |
| Qdrant | ~500 MB | Low-Medium | ~500 MB |
| **Total** | **~3-5 GB** | **Medium** | **~2 GB** |

**Recommendation**: Ensure Docker Desktop has at least 6 GB RAM allocated.

---

## 🎯 Current Recommendation

### For Most Development Work:

**DO NOT start database containers** unless you specifically need:
- PLC Memory System features
- Knowledge graph queries  
- Vector similarity search
- Workflow persistence
- Control loop historical data

**Reason**: Databases consume significant resources and add complexity. The frontend and backend work perfectly without them for UI development, API development, and feature implementation.

### When to Start Databases:

- Working on PLC Memory CLI integration
- Implementing knowledge graph features
- Building vector similarity search
- Testing workflow persistence
- Developing historical data features

---

## 🚀 Quick Commands Reference

```bash
# Check what's running
docker ps

# Check all containers (including stopped)
docker ps -a

# Start core databases only
docker-compose up -d neo4j postgres redis qdrant

# Stop all PLC containers
docker stop $(docker ps -q --filter "name=plc-")

# View real-time logs
docker-compose logs -f

# Clean up stopped containers
docker-compose down

# Nuclear option - remove everything including data
docker-compose down -v  # ⚠️ DELETES ALL DATA
```

---

## 🎓 Docker Compose File Location

**Primary**: `/Users/reh3376/repos/plc-gbt/plc-gbt-stack/docker-compose.yml`

This file defines all services including:
- Core databases (Neo4j, PostgreSQL, Redis, Qdrant)
- Security services (Vault, mTLS, Safety Interlocks)
- Application services (Gateway, ETL Worker, N8N, N8N-MCP)
- PLC Memory CLI container

---

## ✅ Summary

**Current State**: Minimal Docker infrastructure running (N8N + MCP only)

**Databases**: Not started (optional for most development)

**Recommendation**: Start databases only when needed for specific features

**Next Step**: Follow development path in `docs/DEVELOPMENT_PATH_SUMMARY.md`

---

**This reflects the ACTUAL Docker environment state as of September 30, 2025.**