#!/usr/bin/env python3
"""Minimal MCP server for testing"""

import asyncio
import json
import logging
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def handle_stdio():
    """Handle stdio communication"""
    logger.info("Starting minimal MCP server")

    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            line = line.strip()
            if not line:
                continue

            logger.info(f"Received: {line}")

            try:
                request = json.loads(line)
                method = request.get("method")
                request_id = request.get("id")

                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "1.0.0",
                            "capabilities": {
                                "tools": {}
                            },
                            "serverInfo": {
                                "name": "test-minimal",
                                "version": "1.0.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "test_tool",
                                    "description": "A test tool",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {}
                                    }
                                }
                            ]
                        }
                    }
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }

                print(json.dumps(response))
                sys.stdout.flush()
                logger.info(f"Sent response for {method}")

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON: {e}")
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()

        except Exception as e:
            logger.error(f"Error: {e}")
            break

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "stdio":
        asyncio.run(handle_stdio())
    else:
        print("Usage: python test_minimal_server.py stdio")
