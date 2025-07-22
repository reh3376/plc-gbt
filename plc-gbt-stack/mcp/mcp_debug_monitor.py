#!/usr/bin/env python3
"""
MCP Debug Monitor - Comprehensive failure capture and logging system
Monitors MCP server startup, captures all output, and provides detailed diagnostics
"""

import subprocess
import sys
import os
import json
import time
import threading
import queue
from pathlib import Path
from datetime import datetime
import psutil
import signal

class MCPDebugMonitor:
    def __init__(self):
        self.log_dir = Path(__file__).parent / "debug_logs"
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"mcp_debug_{self.session_id}.log"
        self.process = None
        self.output_queue = queue.Queue()
        self.error_queue = queue.Queue()
        
    def log(self, message, level="INFO"):
        """Log with timestamp and level"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
    
    def check_cursor_config(self):
        """Verify Cursor configuration is correct"""
        self.log("Checking Cursor configuration...", "INFO")
        config_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp-servers.json"
        
        if not config_path.exists():
            self.log(f"ERROR: Cursor config not found at {config_path}", "ERROR")
            return False
            
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            self.log(f"Cursor config loaded: {json.dumps(config, indent=2)}", "DEBUG")
            
            if "mcpServers" not in config:
                self.log("ERROR: No mcpServers section in config", "ERROR")
                return False
                
            if "plc-gbt-industrial-automation" not in config["mcpServers"]:
                self.log("ERROR: plc-gbt-industrial-automation not found in servers", "ERROR")
                self.log(f"Available servers: {list(config['mcpServers'].keys())}", "INFO")
                return False
                
            server_config = config["mcpServers"]["plc-gbt-industrial-automation"]
            expected_command = "python3"
            expected_args = ["__main__.py", "stdio"]
            expected_cwd = str(Path(__file__).parent)
            
            issues = []
            if server_config.get("command") != expected_command:
                issues.append(f"Command mismatch: expected '{expected_command}', got '{server_config.get('command')}'")
            if server_config.get("args") != expected_args:
                issues.append(f"Args mismatch: expected {expected_args}, got {server_config.get('args')}")
            if server_config.get("cwd") != expected_cwd:
                issues.append(f"CWD mismatch: expected '{expected_cwd}', got '{server_config.get('cwd')}'")
                
            if issues:
                for issue in issues:
                    self.log(f"CONFIG ISSUE: {issue}", "WARNING")
                return False
                
            self.log("✅ Cursor configuration is correct", "INFO")
            return True
            
        except Exception as e:
            self.log(f"ERROR reading Cursor config: {e}", "ERROR")
            return False
    
    def simulate_cursor_startup(self):
        """Simulate exactly how Cursor starts the MCP server"""
        self.log("=" * 60, "INFO")
        self.log("Simulating Cursor MCP startup process", "INFO")
        self.log("=" * 60, "INFO")
        
        # Get the exact command from config
        config_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp-servers.json"
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            server_config = config["mcpServers"]["plc-gbt-industrial-automation"]
            
            command = server_config["command"]
            args = server_config["args"]
            cwd = server_config["cwd"]
            env = dict(os.environ)
            env.update(server_config.get("env", {}))
            
            full_command = [command] + args
            self.log(f"Command: {' '.join(full_command)}", "INFO")
            self.log(f"CWD: {cwd}", "INFO")
            self.log(f"Environment additions: {server_config.get('env', {})}", "INFO")
            
            # Start the process exactly as Cursor would
            self.process = subprocess.Popen(
                full_command,
                cwd=cwd,
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            self.log(f"Process started with PID: {self.process.pid}", "INFO")
            
            # Monitor output in separate threads
            stdout_thread = threading.Thread(target=self._read_stdout)
            stderr_thread = threading.Thread(target=self._read_stderr)
            stdout_thread.start()
            stderr_thread.start()
            
            # Send initialize request as Cursor would
            time.sleep(1)  # Give server time to start
            self.send_initialize_request()
            
            # Monitor for 10 seconds
            start_time = time.time()
            while time.time() - start_time < 10:
                # Check if process is still running
                if self.process.poll() is not None:
                    self.log(f"ERROR: Process exited with code {self.process.returncode}", "ERROR")
                    break
                    
                # Log any output
                try:
                    while True:
                        output = self.output_queue.get_nowait()
                        self.log(f"STDOUT: {output}", "OUTPUT")
                except queue.Empty:
                    pass
                    
                try:
                    while True:
                        error = self.error_queue.get_nowait()
                        self.log(f"STDERR: {error}", "ERROR")
                except queue.Empty:
                    pass
                    
                time.sleep(0.1)
            
            # Cleanup
            if self.process and self.process.poll() is None:
                self.log("Terminating test process...", "INFO")
                self.process.terminate()
                self.process.wait(timeout=5)
                
        except Exception as e:
            self.log(f"ERROR during simulation: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "ERROR")
    
    def _read_stdout(self):
        """Read stdout in a separate thread"""
        try:
            for line in iter(self.process.stdout.readline, ''):
                if line:
                    self.output_queue.put(line.strip())
        except Exception as e:
            self.error_queue.put(f"Error reading stdout: {e}")
    
    def _read_stderr(self):
        """Read stderr in a separate thread"""
        try:
            for line in iter(self.process.stderr.readline, ''):
                if line:
                    self.error_queue.put(line.strip())
        except Exception as e:
            self.error_queue.put(f"Error reading stderr: {e}")
    
    def send_initialize_request(self):
        """Send MCP initialize request"""
        self.log("Sending MCP initialize request...", "INFO")
        request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "cursor-debug-monitor",
                    "version": "1.0.0"
                }
            },
            "id": 1
        }
        
        try:
            request_str = json.dumps(request) + "\n"
            self.log(f"Sending: {request_str.strip()}", "DEBUG")
            self.process.stdin.write(request_str)
            self.process.stdin.flush()
            self.log("Initialize request sent", "INFO")
        except Exception as e:
            self.log(f"ERROR sending initialize: {e}", "ERROR")
    
    def check_python_path(self):
        """Verify Python is accessible"""
        self.log("Checking Python accessibility...", "INFO")
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True
            )
            self.log(f"Python3 version: {result.stdout.strip()}", "INFO")
            self.log(f"Python3 path: {subprocess.check_output(['which', 'python3']).decode().strip()}", "INFO")
            return True
        except Exception as e:
            self.log(f"ERROR: Python3 not accessible: {e}", "ERROR")
            return False
    
    def check_permissions(self):
        """Check file permissions"""
        self.log("Checking file permissions...", "INFO")
        mcp_dir = Path(__file__).parent
        issues = []
        
        for file in ["__main__.py", "simple_mcp_server.py"]:
            file_path = mcp_dir / file
            if not file_path.exists():
                issues.append(f"File not found: {file_path}")
                continue
                
            if not os.access(file_path, os.R_OK):
                issues.append(f"File not readable: {file_path}")
            if not os.access(file_path, os.X_OK):
                # Try to make it executable
                try:
                    os.chmod(file_path, 0o755)
                    self.log(f"Made {file} executable", "INFO")
                except Exception as e:
                    issues.append(f"File not executable and couldn't fix: {file_path} - {e}")
        
        if issues:
            for issue in issues:
                self.log(f"PERMISSION ISSUE: {issue}", "ERROR")
            return False
        
        self.log("✅ All file permissions are correct", "INFO")
        return True
    
    def monitor_cursor_logs(self):
        """Monitor Cursor's actual MCP logs"""
        self.log("Checking Cursor MCP logs...", "INFO")
        cursor_logs = Path.home() / "Library" / "Application Support" / "Cursor" / "logs"
        
        if not cursor_logs.exists():
            self.log(f"Cursor logs directory not found: {cursor_logs}", "WARNING")
            return
        
        # Find the most recent session
        sessions = sorted([d for d in cursor_logs.iterdir() if d.is_dir()], 
                         key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not sessions:
            self.log("No Cursor log sessions found", "WARNING")
            return
        
        latest_session = sessions[0]
        self.log(f"Latest Cursor session: {latest_session.name}", "INFO")
        
        # Look for MCP logs
        mcp_log_pattern = "**/Cursor MCP.log"
        mcp_logs = list(latest_session.glob(mcp_log_pattern))
        
        if not mcp_logs:
            self.log("No MCP logs found in latest session", "WARNING")
            return
        
        for mcp_log in mcp_logs:
            self.log(f"Found MCP log: {mcp_log}", "INFO")
            # Read last 50 lines
            try:
                with open(mcp_log, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-50:] if len(lines) > 50 else lines
                    
                self.log("=== Last 50 lines of Cursor MCP log ===", "INFO")
                for line in last_lines:
                    self.log(f"CURSOR: {line.strip()}", "CURSOR")
                self.log("=== End of Cursor MCP log ===", "INFO")
            except Exception as e:
                self.log(f"Error reading Cursor log: {e}", "ERROR")
    
    def create_cursor_watcher(self):
        """Create a script that watches Cursor logs in real-time"""
        watcher_script = self.log_dir / "watch_cursor_mcp.sh"
        script_content = """#!/bin/bash
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
"""
        
        with open(watcher_script, 'w') as f:
            f.write(script_content)
        os.chmod(watcher_script, 0o755)
        
        self.log(f"Created Cursor log watcher: {watcher_script}", "INFO")
        self.log("Run this in a separate terminal while restarting Cursor:", "INFO")
        self.log(f"  {watcher_script}", "INFO")
    
    def run_comprehensive_diagnostics(self):
        """Run all diagnostics"""
        self.log("=" * 60, "INFO")
        self.log("MCP DEBUG MONITOR - COMPREHENSIVE DIAGNOSTICS", "INFO")
        self.log(f"Session ID: {self.session_id}", "INFO")
        self.log(f"Log file: {self.log_file}", "INFO")
        self.log("=" * 60, "INFO")
        
        # Run all checks
        checks = {
            "Python Path": self.check_python_path(),
            "File Permissions": self.check_permissions(),
            "Cursor Configuration": self.check_cursor_config(),
        }
        
        # Monitor existing Cursor logs
        self.monitor_cursor_logs()
        
        # Create watcher script
        self.create_cursor_watcher()
        
        # Simulate Cursor startup
        self.simulate_cursor_startup()
        
        # Summary
        self.log("=" * 60, "INFO")
        self.log("DIAGNOSTIC SUMMARY", "INFO")
        self.log("=" * 60, "INFO")
        
        all_passed = all(checks.values())
        for check, passed in checks.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            self.log(f"{check}: {status}", "SUMMARY")
        
        if all_passed:
            self.log("\n✅ All basic checks passed", "SUCCESS")
            self.log("\nNEXT STEPS:", "INFO")
            self.log("1. Open a new terminal and run the watcher script:", "INFO")
            self.log(f"   {self.log_dir}/watch_cursor_mcp.sh", "INFO")
            self.log("2. Then restart Cursor", "INFO")
            self.log("3. Check the watcher output for real-time MCP logs", "INFO")
            self.log("4. Check this debug log for simulation results:", "INFO")
            self.log(f"   {self.log_file}", "INFO")
        else:
            self.log("\n❌ Some checks failed - fix these before restarting Cursor", "ERROR")
        
        return all_passed

if __name__ == "__main__":
    monitor = MCPDebugMonitor()
    success = monitor.run_comprehensive_diagnostics()
    sys.exit(0 if success else 1) 