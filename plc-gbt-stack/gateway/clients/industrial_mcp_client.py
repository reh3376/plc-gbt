"""
Industrial MCP Client
Extracted from industrial_automation_mcp_proxy.py to reduce complexity
"""

import asyncio
import json
import os
import time
from typing import Dict, Any, Optional
from ..utils import handle_mcp_error, create_success_response, create_error_response
import structlog

logger = structlog.get_logger()

class IndustrialMCPClient:
    """Client for communicating with industrial automation MCP server via subprocess"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._get_default_config()
        self.mcp_directory = self.config["mcp_directory"]
        self.server_script = self.config["server_script"]
        self.timeout = self.config["timeout"]
        self.max_retries = self.config["max_retries"]
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default industrial MCP configuration"""
        return {
            "mcp_directory": os.path.join(os.path.dirname(__file__), "..", "..", "mcp"),
            "server_script": "__main__.py",
            "server_name": "plc-gbt-industrial-automation",
            "timeout": int(os.getenv("INDUSTRIAL_MCP_TIMEOUT", "30")),
            "max_retries": int(os.getenv("INDUSTRIAL_MCP_MAX_RETRIES", "3")),
            "api_base_url": os.getenv("PLC_GBT_API_URL", "http://localhost:8000/api/v1")
        }
    
    async def execute_mcp_tool(self, tool_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an MCP tool via subprocess call with retry logic"""
        if parameters is None:
            parameters = {}
        
        mcp_request = {
            "tool": tool_name,
            "parameters": parameters,
            "session_id": f"gateway_proxy_{int(time.time())}"
        }
        
        retries = 0
        while retries <= self.max_retries:
            try:
                result = await self._execute_subprocess(mcp_request)
                if result.get("success", True):  # Assume success if not specified
                    return result
                elif retries < self.max_retries:
                    retries += 1
                    await asyncio.sleep(2 ** retries)  # Exponential backoff
                    continue
                else:
                    return result
                    
            except asyncio.TimeoutError:
                retries += 1
                logger.warning(f"MCP tool timeout", tool=tool_name, attempt=retries)
                
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    continue
                else:
                    return create_error_response(
                        error=f"Tool execution timeout after {self.timeout}s",
                        operation=tool_name
                    )
                    
            except Exception as e:
                logger.error(f"MCP tool execution error", tool=tool_name, error=str(e))
                return handle_mcp_error(e, tool_name)
    
    async def _execute_subprocess(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MCP server subprocess"""
        process = await asyncio.create_subprocess_exec(
            "python3", self.server_script, "tool", json.dumps(mcp_request),
            cwd=self.mcp_directory,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={
                **os.environ,
                "PYTHONPATH": f"{self.mcp_directory}:../plc-gbt-stack",
                "PLC_GBT_API_URL": self.config["api_base_url"]
            }
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), 
            timeout=self.timeout
        )
        
        if process.returncode == 0:
            response_text = stdout.decode('utf-8').strip()
            if response_text:
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    return create_success_response({"result": response_text})
            else:
                return create_success_response({"result": "Tool executed successfully"})
        else:
            error_text = stderr.decode('utf-8').strip()
            return create_error_response(
                error=f"Tool execution failed: {error_text}",
                operation=mcp_request.get("tool", "unknown")
            )
    
    async def get_server_info(self) -> Dict[str, Any]:
        """Get MCP server information and capabilities"""
        try:
            process = await asyncio.create_subprocess_exec(
                "python3", self.server_script, "info",
                cwd=self.mcp_directory,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={
                    **os.environ,
                    "PYTHONPATH": f"{self.mcp_directory}:../plc-gbt-stack"
                }
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10)
            
            if process.returncode == 0:
                info_text = stdout.decode('utf-8').strip()
                try:
                    return json.loads(info_text)
                except json.JSONDecodeError:
                    return {
                        "server_name": self.config["server_name"],
                        "status": "available",
                        "info": info_text
                    }
            else:
                return {
                    "server_name": self.config["server_name"],
                    "status": "error",
                    "error": stderr.decode('utf-8').strip()
                }
                
        except Exception as e:
            return {
                "server_name": self.config["server_name"],
                "status": "unavailable",
                "error": str(e)
            }
    
    # Convenience methods for common industrial operations
    async def create_control_loop(self, name: str, loop_type: str = "PID", **kwargs) -> Dict[str, Any]:
        """Create a control loop"""
        parameters = {"name": name, "type": loop_type, **kwargs}
        return await self.execute_mcp_tool("create_control_loop", parameters)
    
    async def tune_pid_controller(self, control_loop_id: str, method: str = "auto", **kwargs) -> Dict[str, Any]:
        """Tune PID controller parameters"""
        parameters = {"control_loop_id": control_loop_id, "method": method, **kwargs}
        return await self.execute_mcp_tool("tune_pid_controller", parameters)
    
    async def connect_to_plc(self, address: str, plc_type: str = "ControlLogix", **kwargs) -> Dict[str, Any]:
        """Connect to PLC system"""
        parameters = {"address": address, "type": plc_type, **kwargs}
        return await self.execute_mcp_tool("plc_connect", parameters)
    
    async def validate_safety_system(self, name: str, function: str, **kwargs) -> Dict[str, Any]:
        """Validate safety system"""
        parameters = {"name": name, "function": function, **kwargs}
        return await self.execute_mcp_tool("validate_safety_system", parameters)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get system status"""
        return await self.execute_mcp_tool("system_status")
    
    async def search_knowledge(self, query: str, domain: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Search industrial knowledge base"""
        parameters = {"query": query, **kwargs}
        if domain:
            parameters["domain"] = domain
        return await self.execute_mcp_tool("memory_search", parameters) 