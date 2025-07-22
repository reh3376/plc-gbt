#!/bin/bash
# Comprehensive Cursor MCP Monitor
# This script monitors ALL MCP-related activity during Cursor startup

echo "🔍 Comprehensive Cursor MCP Monitor"
echo "=================================="
echo "This will monitor:"
echo "1. Cursor MCP logs"
echo "2. System processes"
echo "3. Network connections"
echo ""

# Create log directory
LOG_DIR="$HOME/repos/plc-gbt/plc-gbt-stack/mcp/debug_logs"
SESSION_ID=$(date +%Y%m%d_%H%M%S)
MONITOR_LOG="$LOG_DIR/cursor_monitor_$SESSION_ID.log"

echo "📁 Session ID: $SESSION_ID"
echo "📄 Monitor log: $MONITOR_LOG"
echo ""

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$MONITOR_LOG"
}

log "Starting comprehensive monitoring..."

# Monitor Cursor logs in background
(
    log "Starting Cursor log monitor..."
    CURSOR_LOGS="$HOME/Library/Application Support/Cursor/logs"
    
    # Wait for new session
    log "Waiting for new Cursor session..."
    INITIAL_SESSIONS=$(ls "$CURSOR_LOGS" 2>/dev/null | wc -l)
    
    while true; do
        CURRENT_SESSIONS=$(ls "$CURSOR_LOGS" 2>/dev/null | wc -l)
        if [ "$CURRENT_SESSIONS" -gt "$INITIAL_SESSIONS" ]; then
            LATEST_SESSION=$(ls -t "$CURSOR_LOGS" | head -1)
            log "New Cursor session detected: $LATEST_SESSION"
            break
        fi
        sleep 0.5
    done
    
    # Monitor MCP log
    MCP_LOG_PATH="$CURSOR_LOGS/$LATEST_SESSION"
    log "Monitoring for MCP log in: $MCP_LOG_PATH"
    
    while true; do
        MCP_LOG=$(find "$MCP_LOG_PATH" -name "Cursor MCP.log" 2>/dev/null | head -1)
        if [ -n "$MCP_LOG" ]; then
            log "MCP log found: $MCP_LOG"
            tail -f "$MCP_LOG" | while read line; do
                log "CURSOR_MCP: $line"
            done
            break
        fi
        sleep 0.5
    done
) &
CURSOR_PID=$!

# Monitor Python processes
(
    log "Starting Python process monitor..."
    while true; do
        # Check for MCP server processes
        MCP_PROCS=$(ps aux | grep -E "(python.*__main__.py.*stdio|python.*simple_mcp_server)" | grep -v grep)
        if [ -n "$MCP_PROCS" ]; then
            log "MCP_PROCESS: $MCP_PROCS"
        fi
        sleep 1
    done
) &
PROCESS_PID=$!

# Monitor network connections on MCP ports
(
    log "Starting network monitor..."
    while true; do
        # Check for stdio pipes
        PIPES=$(lsof -p $(pgrep -f "__main__.py stdio" 2>/dev/null) 2>/dev/null | grep -E "(PIPE|stdio)")
        if [ -n "$PIPES" ]; then
            log "MCP_PIPES: $PIPES"
        fi
        sleep 2
    done
) &
NETWORK_PID=$!

log "All monitors started. Press Ctrl+C to stop all monitoring."
log ""
log "NEXT STEPS:"
log "1. Start Cursor IDE"
log "2. Wait for it to fully load"
log "3. Check the MCP panel for connection status"
log "4. This monitor will capture all activity"
log ""

# Wait for interrupt
trap "kill $CURSOR_PID $PROCESS_PID $NETWORK_PID 2>/dev/null; log 'Monitoring stopped.'; exit" INT

# Keep script running
while true; do
    sleep 1
done 