#!/bin/bash
# 🧹 Cache Cleanup Script for PLC-GBT MCP Server Startup
# Run this before starting Cursor to ensure clean MCP server connections

echo "🧹 Starting comprehensive cache cleanup for MCP server startup..."

# 1. Clear Python bytecode caches in project
echo "📁 Clearing Python __pycache__ directories..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "🐍 Clearing Python .pyc files..."
find . -name "*.pyc" -delete 2>/dev/null || true

# 2. Clear specific MCP directory caches
echo "🔧 Clearing MCP-specific caches..."
rm -rf plc-gbt-stack/mcp/__pycache__ 2>/dev/null || true
find plc-gbt-stack/mcp -name "*.pyc" -delete 2>/dev/null || true

# 3. Clear virtual environment cache (safe - only affects import speed)
echo "🐍 Clearing virtual environment caches..."
find .venv -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find .venv -name "*.pyc" -delete 2>/dev/null || true

# 4. Clear macOS system caches for the app (if Cursor is not running)
echo "🍎 Checking for macOS Cursor caches..."
if ! pgrep -f "Cursor" > /dev/null; then
    echo "   Cursor not running - safe to clear system caches"
    rm -rf ~/Library/Caches/com.todesktop.230313mzl4w4u18* 2>/dev/null || true
    rm -rf ~/Library/Caches/Cursor* 2>/dev/null || true
else
    echo "   ⚠️  Cursor is running - skip system cache clearing"
    echo "   Please quit Cursor first for complete cleanup"
fi

# 5. Clear any temporary MCP files
echo "🗑️  Clearing temporary files..."
rm -rf /tmp/mcp_* 2>/dev/null || true
rm -rf /tmp/cursor_mcp* 2>/dev/null || true

# 6. Reset import module cache for Python
echo "🔄 Resetting Python import cache..."
python3 -Bc "import sys; sys.path_hooks.clear(); sys.path_importer_cache.clear()" 2>/dev/null || true

# 7. Verify MCP server dependencies
echo "🔍 Verifying MCP server dependencies..."
if source .venv/bin/activate 2>/dev/null; then
    echo "   ✅ Virtual environment activated"
    if python -c "import aiohttp, hvac, cryptography" 2>/dev/null; then
        echo "   ✅ All MCP dependencies available"
    else
        echo "   ❌ Missing MCP dependencies - run: pip install aiohttp hvac cryptography"
    fi
    deactivate 2>/dev/null || true
else
    echo "   ⚠️  Virtual environment not found"
fi

echo ""
echo "✅ Cache cleanup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Ensure Cursor is completely quit (Cmd+Q)"
echo "2. Wait 10 seconds"
echo "3. Restart Cursor"
echo "4. Check MCP server connections in Settings → Tools & Integrations"
echo ""
echo "Expected result: plc-gbt-industrial-automation should show 8 tools" 