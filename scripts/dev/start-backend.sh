#!/bin/bash

# PLC-GBT Backend Startup Script
# Starts the FastAPI backend on port 8000

set -e

echo "🚀 Starting PLC-GBT Backend..."
echo ""

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

# Check if virtual environment exists
if [ ! -d "$PROJECT_ROOT/.venv" ]; then
    echo "❌ Virtual environment not found at $PROJECT_ROOT/.venv"
    echo "   Please run: python3.12 -m venv .venv"
    echo "   Then: source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source "$PROJECT_ROOT/.venv/bin/activate"

# Check if uvicorn is installed
if ! python -c "import uvicorn" 2>/dev/null; then
    echo "❌ uvicorn not found. Installing dependencies..."
    pip install -q -r "$PROJECT_ROOT/requirements.txt"
fi

# Check if port 8000 is in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 8000 is already in use"
    echo "   Existing process:"
    lsof -Pi :8000 -sTCP:LISTEN
    read -p "   Kill existing process and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔪 Killing process on port 8000..."
        kill $(lsof -t -i:8000) 2>/dev/null || true
        sleep 2
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

# Start the backend
cd "$PROJECT_ROOT/plc-gbt-stack"

echo ""
echo "✅ Starting FastAPI backend..."
echo "   URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs (if configured)"
echo "   Logs: Will appear below"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

python -m uvicorn api.cli_api_bridge:app --host 0.0.0.0 --port 8000 --reload
