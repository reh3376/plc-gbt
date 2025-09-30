#!/bin/bash

# PLC-GBT Frontend Startup Script
# Starts the Next.js development server on port 3000

set -e

echo "🚀 Starting PLC-GBT Frontend..."
echo ""

# Get the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"
FRONTEND_DIR="$PROJECT_ROOT/plc-gbt-stack/ui/nextjs"

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies (first time setup)..."
    npm install
    echo "✅ Dependencies installed"
    echo ""
fi

# Check if port 3000 is in use
if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Port 3000 is already in use"
    echo "   Existing process:"
    lsof -Pi :3000 -sTCP:LISTEN
    echo ""
    read -p "   Kill existing process and continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🔪 Killing process on port 3000..."
        kill $(lsof -t -i:3000) 2>/dev/null || true
        sleep 2
    else
        echo "❌ Aborted"
        exit 1
    fi
fi

echo "✅ Starting Next.js development server..."
echo "   URL: http://localhost:3000"
echo "   Ready when you see: ✓ Ready in X.Xs"
echo ""
echo "   Press Ctrl+C to stop"
echo ""

npm run dev
