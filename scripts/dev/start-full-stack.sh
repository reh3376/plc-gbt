#!/bin/bash

# PLC-GBT Full Stack Startup Script
# Starts databases, backend, and frontend in correct order

set -e

echo "🚀 PLC-GBT Full Stack Startup"
echo "================================"
echo ""

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local name=$2
    local max_attempts=30
    local attempt=1
    
    echo -n "   Waiting for $name..."
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo -e " ${GREEN}✓${NC}"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    echo -e " ${RED}✗${NC}"
    return 1
}

echo "Step 1: Starting Database Containers"
echo "------------------------------------"

cd "$PROJECT_ROOT/plc-gbt-stack"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
    exit 1
fi

# Start database containers
echo "🐳 Starting Neo4j, PostgreSQL, Redis, Qdrant..."
docker-compose up -d neo4j postgres redis qdrant

# Wait for databases to be healthy
echo ""
echo "⏳ Waiting for databases to be healthy (this may take 30-60 seconds)..."

sleep 5  # Give containers time to start

# Check container status
echo ""
docker-compose ps neo4j postgres redis qdrant

echo ""
echo "Step 2: Starting Backend (FastAPI)"
echo "------------------------------------"

# Check if Python venv exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "   Please run: python3.12 -m venv .venv"
    echo "   Then: source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if backend is already running
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Backend already running on port 8000${NC}"
else
    echo "🐍 Starting FastAPI backend in background..."
    source "$PROJECT_ROOT/.venv/bin/activate"
    cd "$PROJECT_ROOT/plc-gbt-stack"
    nohup python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload > /tmp/plc-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "   Backend PID: $BACKEND_PID"
    echo "   Logs: tail -f /tmp/plc-backend.log"
    
    # Wait for backend to be ready
    if wait_for_service "http://localhost:8000/api/v1/health" "Backend"; then
        echo -e "${GREEN}✅ Backend started successfully${NC}"
    else
        echo -e "${RED}❌ Backend failed to start${NC}"
        echo "   Check logs: tail -f /tmp/plc-backend.log"
        exit 1
    fi
fi

echo ""
echo "Step 3: Starting Frontend (Next.js)"
echo "------------------------------------"

cd "$PROJECT_ROOT/plc-gbt-stack/ui/nextjs"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Check if frontend is already running
if check_port 3000; then
    echo -e "${YELLOW}⚠️  Frontend already running on port 3000${NC}"
    echo -e "${YELLOW}   You may want to stop the existing process${NC}"
else
    echo "⚛️  Starting Next.js development server in background..."
    nohup npm run dev > /tmp/plc-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "   Frontend PID: $FRONTEND_PID"
    echo "   Logs: tail -f /tmp/plc-frontend.log"
    
    # Wait for frontend to be ready
    sleep 3
    if wait_for_service "http://localhost:3000" "Frontend"; then
        echo -e "${GREEN}✅ Frontend started successfully${NC}"
    else
        echo -e "${RED}❌ Frontend failed to start${NC}"
        echo "   Check logs: tail -f /tmp/plc-frontend.log"
        exit 1
    fi
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ PLC-GBT Full Stack Started!${NC}"
echo "================================"
echo ""
echo "📊 Service URLs:"
echo "   • Frontend UI:        http://localhost:3000"
echo "   • Backend API:        http://localhost:8000"
echo "   • Neo4j Browser:      http://localhost:7474"
echo "   • Qdrant Dashboard:   http://localhost:6333/dashboard"
echo "   • N8N (if running):   http://localhost:5678"
echo ""
echo "📋 Management Commands:"
echo "   • View backend logs:  tail -f /tmp/plc-backend.log"
echo "   • View frontend logs: tail -f /tmp/plc-frontend.log"
echo "   • Stop backend:       kill \$(lsof -t -i:8000)"
echo "   • Stop frontend:      kill \$(lsof -t -i:3000)"
echo "   • Stop databases:     cd plc-gbt-stack && docker-compose stop neo4j postgres redis qdrant"
echo ""
echo "🧪 Test PLC Memory:"
echo "   source .venv/bin/activate"
echo "   python plc-gbt-stack/scripts/ai/plc_memory_cli.py status"
echo ""
echo -e "${BLUE}🎉 Ready for development!${NC}"
echo ""
