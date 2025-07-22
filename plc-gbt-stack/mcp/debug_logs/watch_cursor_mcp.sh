#!/bin/bash
# Cursor MCP Log Watcher
# This script watches Cursor MCP logs in real-time

echo "Starting Cursor MCP log watcher..."
echo "This will monitor MCP logs as Cursor runs"
echo "Press Ctrl+C to stop"
echo ""

# Find the latest Cursor session
CURSOR_LOGS="$HOME/Library/Application Support/Cursor/logs"
LATEST_SESSION=$(ls -t "$CURSOR_LOGS" | head -1)

if [ -z "$LATEST_SESSION" ]; then
    echo "ERROR: No Cursor sessions found"
    exit 1
fi

echo "Monitoring session: $LATEST_SESSION"

# Find MCP log file
MCP_LOG=$(find "$CURSOR_LOGS/$LATEST_SESSION" -name "Cursor MCP.log" 2>/dev/null | head -1)

if [ -z "$MCP_LOG" ]; then
    echo "Waiting for MCP log to be created..."
    # Wait for the file to be created
    while [ -z "$MCP_LOG" ]; do
        sleep 1
        MCP_LOG=$(find "$CURSOR_LOGS/$LATEST_SESSION" -name "Cursor MCP.log" 2>/dev/null | head -1)
    done
fi

echo "Found MCP log: $MCP_LOG"
echo "===================="
echo ""

# Tail the log file
tail -f "$MCP_LOG" | while read line; do
    echo "[$(date '+%H:%M:%S')] $line"
done
