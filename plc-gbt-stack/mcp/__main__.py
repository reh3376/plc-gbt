"""
PLC-GBT MCP Server - Module Entry Point
Allows the MCP server to be run as a module: python -m plc_gbt_stack.mcp

This enables Cursor IDE to connect to the MCP server via the configuration in mcp_server_config.json
Uses the simplified MCP server compatible with Python 3.9+
"""

import asyncio
import sys
import os
import logging
from pathlib import Path
import json
from simple_mcp_server import SimpleMCPServer, main as test_simple_server

def main():
    """Main entry point for the MCP server module"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("🚀 Starting PLC-GBT Simplified MCP Server for Cursor IDE Integration")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "test":
            # Run the test function
            try:
                asyncio.run(test_simple_server())
            except KeyboardInterrupt:
                logger.info("🛑 Test interrupted by user")
            except Exception as e:
                logger.error(f"❌ Test failed: {e}")
                sys.exit(1)
            return
        
        elif command == "stdio":
            # Run in stdio mode for MCP protocol communication
            logger.info("📡 Starting MCP server in stdio mode for Cursor IDE")
            
            try:
                # Start the MCP server in stdio mode
                asyncio.run(run_stdio_server())
            except KeyboardInterrupt:
                logger.info("🛑 MCP server stopped by user")
            except Exception as e:
                logger.error(f"❌ MCP server failed: {e}")
                sys.exit(1)
            return
    
    # Default behavior: run test
    try:
        asyncio.run(test_simple_server())
    except KeyboardInterrupt:
        logger.info("🛑 MCP Server stopped by user")
    except Exception as e:
        logger.error(f"❌ MCP Server failed to start: {e}")
        sys.exit(1)

async def run_stdio_server():
    """Run MCP server in stdio mode for Cursor IDE communication"""
    server = SimpleMCPServer()
    await server.start()
    
    logger = logging.getLogger(__name__)
    logger.info("🔄 MCP server ready for stdio communication")
    
    try:
        # Read from stdin and write to stdout for MCP protocol
        while True:
            try:
                # Read JSON-RPC message from stdin
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                # Parse request
                try:
                    request = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                
                # Handle request
                response = await server.handle_request(request)
                
                # Add JSON-RPC fields
                response_msg = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": response
                }
                
                # Write response to stdout
                print(json.dumps(response_msg))
                sys.stdout.flush()
                
            except Exception as e:
                # Send error response
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id") if 'request' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
                
    finally:
        await server.stop()

if __name__ == "__main__":
    main() 