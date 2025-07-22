#!/bin/bash
# Continuous MCP Monitor for session 20250722_114359

LOG_FILE="/Users/reh3376/repos/plc-gbt/plc-gbt-stack/mcp/debug_logs/continuous_20250722_114359.log"
CURSOR_LOG_DIR="$HOME/Library/Application Support/Cursor/logs"

echo "Starting continuous monitoring at $(date)" > "$LOG_FILE"

# Monitor Cursor logs
tail -f "$CURSOR_LOG_DIR"/*/window*/exthost/anysphere.cursor-retrieval/MCP*.log 2>/dev/null | while read line; do
    echo "[$(date '+%H:%M:%S')] CURSOR: $line" >> "$LOG_FILE"
done &

# Monitor system processes
while true; do
    if pgrep -f "__main__.py.*stdio" > /dev/null; then
        echo "[$(date '+%H:%M:%S')] PROCESS: MCP server running (PID: $(pgrep -f '__main__.py.*stdio'))" >> "$LOG_FILE"
    else
        echo "[$(date '+%H:%M:%S')] PROCESS: MCP server NOT running" >> "$LOG_FILE"
    fi
    sleep 5
done &

echo "Monitoring started. Check $LOG_FILE for real-time updates."
echo "To stop monitoring: pkill -f continuous_monitor_20250722_114359"
