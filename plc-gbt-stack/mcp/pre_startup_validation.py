#!/usr/bin/env python3
"""
Pre-Startup MCP Validation & Monitoring Setup
Validates all components and sets up comprehensive monitoring before Cursor restart
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class MCPStartupValidator:
    def __init__(self):
        self.log_dir = Path(__file__).parent / "debug_logs"
        self.log_dir.mkdir(exist_ok=True)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.validation_log = self.log_dir / f"validation_{self.session_id}.log"
        self.issues = []

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        with open(self.validation_log, "a") as f:
            f.write(log_entry + "\n")

    def validate_python_environment(self):
        """Validate Python environment and dependencies"""
        self.log("🔍 Validating Python Environment...")

        venv_python = "/Users/reh3376/repos/plc-gbt/.venv/bin/python3"
        if not Path(venv_python).exists():
            self.issues.append("Virtual environment Python not found")
            return False

        try:
            result = subprocess.run([venv_python, "--version"],
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            self.log(f"✅ Python: {version}")

            # Test critical imports
            import_test = """
import aiohttp
import json
import sys
import asyncio
print("All imports successful")
"""
            result = subprocess.run([venv_python, "-c", import_test],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ All dependencies available")
                return True
            else:
                self.issues.append(f"Import test failed: {result.stderr}")
                return False

        except Exception as e:
            self.issues.append(f"Python validation failed: {e}")
            return False

    def validate_mcp_server(self):
        """Validate MCP server can start and respond"""
        self.log("🔍 Validating MCP Server...")

        server_path = "/Users/reh3376/repos/plc-gbt/plc-gbt-stack/mcp/__main__.py"
        venv_python = "/Users/reh3376/repos/plc-gbt/.venv/bin/python3"

        if not Path(server_path).exists():
            self.issues.append("MCP server __main__.py not found")
            return False

        try:
            # Test server can start
            result = subprocess.run([venv_python, server_path, "test"],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log("✅ MCP Server responds to test command")

                # Test stdio mode startup (quick test)
                proc = subprocess.Popen([venv_python, server_path, "stdio"],
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      text=True)

                # Send initialize request
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1.0"}
                    }
                }

                proc.stdin.write(json.dumps(init_request) + "\n")
                proc.stdin.flush()

                # Read response with timeout
                import select
                if select.select([proc.stdout], [], [], 5.0)[0]:
                    response = proc.stdout.readline()
                    if response:
                        self.log("✅ MCP Server responds to initialize request")
                        proc.terminate()
                        return True

                proc.terminate()
                self.issues.append("MCP server stdio mode timeout")
                return False

            else:
                self.issues.append(f"MCP server test failed: {result.stderr}")
                return False

        except Exception as e:
            self.issues.append(f"MCP server validation failed: {e}")
            return False

    def validate_cursor_config(self):
        """Validate Cursor MCP configuration"""
        self.log("🔍 Validating Cursor Configuration...")

        config_path = "/Users/reh3376/Library/Application Support/Cursor/User/globalStorage/mcp-servers.json"
        if not Path(config_path).exists():
            self.issues.append("Cursor MCP config file not found")
            return False

        try:
            with open(config_path) as f:
                config = json.load(f)

            if "mcpServers" not in config:
                self.issues.append("No mcpServers in config")
                return False

            if "plc-gbt-industrial-automation" not in config["mcpServers"]:
                self.issues.append("Server not found in config")
                return False

            server_config = config["mcpServers"]["plc-gbt-industrial-automation"]

            # Validate command path
            command = server_config.get("command")
            if not Path(command).exists():
                self.issues.append(f"Python command path not found: {command}")
                return False

            # Validate script path
            args = server_config.get("args", [])
            if args and not Path(args[0]).exists():
                self.issues.append(f"Script path not found: {args[0]}")
                return False

            # Validate working directory
            cwd = server_config.get("cwd")
            if cwd and not Path(cwd).exists():
                self.issues.append(f"Working directory not found: {cwd}")
                return False

            self.log("✅ Cursor configuration valid")
            return True

        except Exception as e:
            self.issues.append(f"Config validation failed: {e}")
            return False

    def setup_continuous_monitoring(self):
        """Set up continuous monitoring for the restart"""
        self.log("🔧 Setting up continuous monitoring...")

        monitor_script = self.log_dir / f"continuous_monitor_{self.session_id}.sh"

        script_content = f'''#!/bin/bash
# Continuous MCP Monitor for session {self.session_id}

LOG_FILE="{self.log_dir}/continuous_{self.session_id}.log"
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
echo "To stop monitoring: pkill -f continuous_monitor_{self.session_id}"
'''

        with open(monitor_script, "w") as f:
            f.write(script_content)

        os.chmod(monitor_script, 0o755)
        self.log(f"✅ Monitoring script created: {monitor_script}")

        return monitor_script

    def run_full_validation(self):
        """Run complete validation suite"""
        self.log("🚀 Starting Pre-Startup Validation Suite")
        self.log("=" * 50)

        validations = [
            ("Python Environment", self.validate_python_environment),
            ("MCP Server", self.validate_mcp_server),
            ("Cursor Configuration", self.validate_cursor_config),
        ]

        passed = 0
        for name, validator in validations:
            if validator():
                passed += 1
            else:
                self.log(f"❌ {name} validation failed", "ERROR")

        self.log("=" * 50)
        self.log(f"Validation Results: {passed}/{len(validations)} passed")

        if self.issues:
            self.log("Issues found:", "ERROR")
            for issue in self.issues:
                self.log(f"  - {issue}", "ERROR")
            return False
        else:
            self.log("✅ All validations passed!")
            monitor_script = self.setup_continuous_monitoring()
            self.log(f"🔧 Start monitoring: {monitor_script}")
            return True

if __name__ == "__main__":
    validator = MCPStartupValidator()
    success = validator.run_full_validation()

    if success:
        print("\n🎯 READY FOR RESTART!")
        print("Start the monitoring script in a separate terminal:")
        print(f"  {validator.log_dir}/continuous_monitor_{validator.session_id}.sh")
        print("\nThen restart Cursor.")
    else:
        print("\n❌ ISSUES FOUND - Fix before restart!")
        sys.exit(1)
