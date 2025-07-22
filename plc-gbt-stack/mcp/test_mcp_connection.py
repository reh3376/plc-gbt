#!/usr/bin/env python3
"""
MCP Server Connection Diagnostic Tool
Tests the MCP server setup and provides detailed diagnostic information
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def test_python_installation():
    """Test Python installation and version"""
    print("🔍 Testing Python Installation...")
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Python Version: {result.stdout.strip()}")
        print(f"   Python Path: {sys.executable}")
        return True
    except Exception as e:
        print(f"❌ Python Test Failed: {e}")
        return False

def test_dependencies():
    """Test required dependencies"""
    print("\n🔍 Testing Dependencies...")
    dependencies = ["aiohttp", "json", "asyncio", "sys", "os"]
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep}: Installed")
        except ImportError:
            print(f"❌ {dep}: Not installed")
            all_good = False
    
    return all_good

def test_mcp_server():
    """Test MCP server execution"""
    print("\n🔍 Testing MCP Server...")
    mcp_path = Path(__file__).parent / "__main__.py"
    
    if not mcp_path.exists():
        print(f"❌ MCP Server not found at: {mcp_path}")
        return False
    
    print(f"✅ MCP Server found at: {mcp_path}")
    
    # Test with 'test' command
    try:
        result = subprocess.run([sys.executable, str(mcp_path), "test"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ MCP Server test command successful")
            print(f"   Output: {result.stdout[:200]}...")
            return True
        else:
            print(f"❌ MCP Server test failed with code: {result.returncode}")
            print(f"   Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ MCP Server test timed out")
        return False
    except Exception as e:
        print(f"❌ MCP Server test error: {e}")
        return False

def test_cursor_config():
    """Test Cursor configuration"""
    print("\n🔍 Testing Cursor Configuration...")
    config_path = Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "globalStorage" / "mcp-servers.json"
    
    if not config_path.exists():
        print(f"❌ Cursor config not found at: {config_path}")
        return False
    
    print(f"✅ Cursor config found at: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if "mcpServers" in config:
            servers = list(config["mcpServers"].keys())
            print(f"✅ MCP Servers configured: {servers}")
            
            # Check our server
            if "plc-gbt-industrial-automation" in servers:
                print("✅ plc-gbt-industrial-automation is configured")
                server_config = config["mcpServers"]["plc-gbt-industrial-automation"]
                print(f"   Command: {server_config.get('command', 'Not set')}")
                print(f"   Args: {server_config.get('args', 'Not set')}")
                print(f"   CWD: {server_config.get('cwd', 'Not set')}")
                return True
            else:
                print("❌ plc-gbt-industrial-automation not found in config")
                print(f"   Available servers: {servers}")
                return False
        else:
            print("❌ No mcpServers section in config")
            return False
    except Exception as e:
        print(f"❌ Error reading config: {e}")
        return False

def test_stdio_communication():
    """Test stdio communication with the server"""
    print("\n🔍 Testing STDIO Communication...")
    mcp_path = Path(__file__).parent / "__main__.py"
    
    try:
        # Start the server in stdio mode
        proc = subprocess.Popen(
            [sys.executable, str(mcp_path), "stdio"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send a simple initialize request
        initialize_request = json.dumps({
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {}
            },
            "id": 1
        }) + "\n"
        
        proc.stdin.write(initialize_request)
        proc.stdin.flush()
        
        # Try to read response (with timeout)
        import select
        readable, _, _ = select.select([proc.stdout], [], [], 5.0)
        
        if readable:
            response = proc.stdout.readline()
            if response:
                print("✅ Server responded to initialize request")
                print(f"   Response: {response[:100]}...")
                proc.terminate()
                return True
            else:
                print("❌ No response from server")
        else:
            print("❌ Server didn't respond within 5 seconds")
        
        proc.terminate()
        return False
        
    except Exception as e:
        print(f"❌ STDIO communication test failed: {e}")
        return False

def main():
    """Run all diagnostic tests"""
    print("🚀 MCP Server Connection Diagnostic Tool")
    print("=" * 50)
    
    results = {
        "Python": test_python_installation(),
        "Dependencies": test_dependencies(),
        "MCP Server": test_mcp_server(),
        "Cursor Config": test_cursor_config(),
        "STDIO Communication": test_stdio_communication()
    }
    
    print("\n📊 Summary")
    print("=" * 50)
    
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test:.<30} {status}")
        if not passed:
            all_passed = False
    
    print("\n🎯 Overall Result:", "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED")
    
    if not all_passed:
        print("\n💡 Recommendations:")
        if not results["Python"]:
            print("- Check Python installation")
        if not results["Dependencies"]:
            print("- Install missing dependencies: pip install aiohttp")
        if not results["MCP Server"]:
            print("- Check MCP server file permissions and location")
        if not results["Cursor Config"]:
            print("- Restart Cursor IDE to reload configuration")
        if not results["STDIO Communication"]:
            print("- Check for firewall or security software blocking Python")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 