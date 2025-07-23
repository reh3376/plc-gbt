#!/usr/bin/env python3
"""
Industrial Automation MCP Proxy Gateway
Phase 26.8: Fine-tuned LLM Integration with Industrial Automation MCP

Provides HTTP proxy endpoints that allow the fine-tuned OpenAI LLM 
(ft:gpt-4o:industrial-control:20250117) to access industrial automation MCP 
functionality through the existing PLC-GBT Gateway API architecture.

This enables the LLM to create control loops, tune PID controllers, 
connect to PLCs, validate safety systems, and access industrial expertise.

Author: AI Task Orchestrator
Date: July 23, 2025
Phase: 26.8 - Industrial Automation MCP Integration
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, HTTPException, Depends, Query, Body, Path
from pydantic import BaseModel, Field

# Configure logging
logger = structlog.get_logger()

# Industrial Automation MCP Configuration
INDUSTRIAL_MCP_CONFIG = {
    "mcp_directory": os.path.join(os.path.dirname(__file__), "..", "mcp"),
    "server_script": "__main__.py",
    "server_name": "plc-gbt-industrial-automation",
    "timeout": int(os.getenv("INDUSTRIAL_MCP_TIMEOUT", "30")),
    "max_retries": int(os.getenv("INDUSTRIAL_MCP_MAX_RETRIES", "3")),
    "api_base_url": os.getenv("PLC_GBT_API_URL", "http://localhost:8000/api/v1")
}

# Initialize FastAPI router
router = APIRouter(prefix="/api/v1/industrial-mcp", tags=["Industrial Automation MCP"])

# Pydantic models for request/response validation
class ControlLoopRequest(BaseModel):
    name: str = Field(..., description="Control loop name")
    loop_type: str = Field("PID", description="Control loop type (PID, PI, PD, etc.)")
    setpoint: float = Field(..., description="Desired setpoint value")
    process_variable: str = Field(..., description="Process variable to control")
    output_variable: str = Field(..., description="Control output variable")
    tuning_params: Optional[Dict[str, float]] = Field(None, description="PID tuning parameters")
    safety_limits: Optional[Dict[str, float]] = Field(None, description="Safety limits")

class ControlLoopResponse(BaseModel):
    success: bool = Field(..., description="Whether control loop was created successfully")
    control_loop_id: str = Field(..., description="Unique control loop identifier")
    schema_used: str = Field(..., description="Control loop schema applied")
    parameters: Dict[str, Any] = Field(..., description="Applied control parameters")
    validation_score: float = Field(..., description="Validation score (0-100)")
    recommendations: List[str] = Field(default_factory=list, description="Optimization recommendations")

class PIDTuningRequest(BaseModel):
    control_loop_id: str = Field(..., description="Control loop to tune")
    tuning_method: str = Field("auto", description="Tuning method (auto, ziegler-nichols, cohen-coon)")
    process_data: Optional[List[Dict[str, float]]] = Field(None, description="Historical process data")
    performance_criteria: str = Field("balanced", description="Performance criteria (fast, balanced, stable)")

class PIDTuningResponse(BaseModel):
    success: bool = Field(..., description="Whether tuning was successful")
    tuned_parameters: Dict[str, float] = Field(..., description="Optimized PID parameters")
    performance_prediction: Dict[str, float] = Field(..., description="Predicted performance metrics")
    tuning_method_used: str = Field(..., description="Tuning method applied")
    recommendations: List[str] = Field(default_factory=list, description="Implementation recommendations")

class PLCConnectionRequest(BaseModel):
    plc_address: str = Field(..., description="PLC IP address or hostname")
    plc_type: str = Field("ControlLogix", description="PLC type (ControlLogix, CompactLogix, etc.)")
    slot: int = Field(0, description="PLC slot number")
    timeout: float = Field(5.0, description="Connection timeout in seconds")
    protocol: str = Field("EtherNet/IP", description="Communication protocol")

class PLCConnectionResponse(BaseModel):
    success: bool = Field(..., description="Whether connection was successful")
    connection_id: str = Field(..., description="Connection identifier")
    plc_info: Dict[str, Any] = Field(..., description="PLC system information")
    available_tags: List[str] = Field(default_factory=list, description="Available PLC tags")
    connection_status: str = Field(..., description="Connection status details")

class SafetySystemRequest(BaseModel):
    safety_system_name: str = Field(..., description="Safety system name")
    safety_function: str = Field(..., description="Safety function to validate")
    interlocks: List[Dict[str, Any]] = Field(..., description="Safety interlock definitions")
    fail_safe_actions: List[str] = Field(..., description="Fail-safe actions")
    sil_level: int = Field(1, ge=1, le=4, description="Safety Integrity Level (1-4)")

class SafetySystemResponse(BaseModel):
    validation_passed: bool = Field(..., description="Whether safety validation passed")
    sil_compliance: bool = Field(..., description="SIL level compliance")
    safety_score: float = Field(..., description="Overall safety score (0-100)")
    compliance_issues: List[str] = Field(default_factory=list, description="Compliance issues found")
    recommendations: List[str] = Field(default_factory=list, description="Safety recommendations")

class SystemStatusResponse(BaseModel):
    system_healthy: bool = Field(..., description="Overall system health")
    active_control_loops: int = Field(..., description="Number of active control loops")
    plc_connections: int = Field(..., description="Number of active PLC connections")
    memory_usage: Dict[str, float] = Field(..., description="Memory usage statistics")
    performance_metrics: Dict[str, float] = Field(..., description="System performance metrics")
    alerts: List[str] = Field(default_factory=list, description="Active system alerts")

class IndustrialKnowledgeRequest(BaseModel):
    query: str = Field(..., description="Search query for industrial knowledge")
    domain: Optional[str] = Field(None, description="Knowledge domain filter")
    limit: int = Field(10, ge=1, le=50, description="Maximum results to return")

class IndustrialKnowledgeResponse(BaseModel):
    results: List[Dict[str, Any]] = Field(..., description="Knowledge search results")
    total_found: int = Field(..., description="Total results found")
    search_time_ms: float = Field(..., description="Search execution time")
    knowledge_domains: List[str] = Field(default_factory=list, description="Available knowledge domains")

# Industrial Automation MCP Client
class IndustrialMCPClient:
    """Client for communicating with industrial automation MCP server"""
    
    def __init__(self):
        self.mcp_directory = INDUSTRIAL_MCP_CONFIG["mcp_directory"]
        self.server_script = INDUSTRIAL_MCP_CONFIG["server_script"]
        self.timeout = INDUSTRIAL_MCP_CONFIG["timeout"]
        self.max_retries = INDUSTRIAL_MCP_CONFIG["max_retries"]
    
    async def execute_mcp_tool(
        self, 
        tool_name: str, 
        parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute an MCP tool via subprocess call"""
        if parameters is None:
            parameters = {}
        
        # Construct MCP tool call
        mcp_request = {
            "tool": tool_name,
            "parameters": parameters,
            "session_id": f"gateway_proxy_{int(time.time())}"
        }
        
        retries = 0
        while retries <= self.max_retries:
            try:
                # Execute MCP server with tool call
                process = await asyncio.create_subprocess_exec(
                    "python3", self.server_script, "tool", json.dumps(mcp_request),
                    cwd=self.mcp_directory,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env={
                        **os.environ,
                        "PYTHONPATH": f"{self.mcp_directory}:../plc-gbt-stack",
                        "PLC_GBT_API_URL": INDUSTRIAL_MCP_CONFIG["api_base_url"]
                    }
                )
                
                # Wait for completion with timeout
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=self.timeout
                )
                
                if process.returncode == 0:
                    # Parse successful response
                    response_text = stdout.decode('utf-8').strip()
                    if response_text:
                        try:
                            return json.loads(response_text)
                        except json.JSONDecodeError:
                            # Return text response if not JSON
                            return {"result": response_text, "success": True}
                    else:
                        return {"result": "Tool executed successfully", "success": True}
                else:
                    # Handle error response
                    error_text = stderr.decode('utf-8').strip()
                    logger.warning(f"MCP tool failed", tool=tool_name, error=error_text)
                    
                    if retries < self.max_retries:
                        retries += 1
                        await asyncio.sleep(2 ** retries)  # Exponential backoff
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Tool execution failed: {error_text}",
                            "tool": tool_name
                        }
                        
            except asyncio.TimeoutError:
                retries += 1
                logger.warning(f"MCP tool timeout", tool=tool_name, attempt=retries)
                
                if retries <= self.max_retries:
                    await asyncio.sleep(2 ** retries)
                    continue
                else:
                    return {
                        "success": False,
                        "error": f"Tool execution timeout after {self.timeout}s",
                        "tool": tool_name
                    }
                    
            except Exception as e:
                logger.error(f"MCP tool execution error", tool=tool_name, error=str(e))
                return {
                    "success": False,
                    "error": f"Execution error: {str(e)}",
                    "tool": tool_name
                }
    
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
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=10
            )
            
            if process.returncode == 0:
                info_text = stdout.decode('utf-8').strip()
                try:
                    return json.loads(info_text)
                except json.JSONDecodeError:
                    # Parse text response
                    return {
                        "server_name": INDUSTRIAL_MCP_CONFIG["server_name"],
                        "status": "available",
                        "info": info_text
                    }
            else:
                return {
                    "server_name": INDUSTRIAL_MCP_CONFIG["server_name"],
                    "status": "error",
                    "error": stderr.decode('utf-8').strip()
                }
                
        except Exception as e:
            return {
                "server_name": INDUSTRIAL_MCP_CONFIG["server_name"],
                "status": "unavailable",
                "error": str(e)
            }

# Global client instance
_industrial_mcp_client: Optional[IndustrialMCPClient] = None

async def get_industrial_mcp_client() -> IndustrialMCPClient:
    """Get or create industrial automation MCP client"""
    global _industrial_mcp_client
    if _industrial_mcp_client is None:
        _industrial_mcp_client = IndustrialMCPClient()
    return _industrial_mcp_client

# =============================================================================
# INDUSTRIAL AUTOMATION MCP PROXY ENDPOINTS
# =============================================================================

@router.get("/health", 
           summary="Check industrial automation MCP health",
           description="Verify that the industrial automation MCP server is accessible")
async def check_industrial_mcp_health():
    """Check industrial automation MCP server health"""
    start_time = time.time()
    client = await get_industrial_mcp_client()
    
    try:
        server_info = await client.get_server_info()
        response_time = (time.time() - start_time) * 1000
        
        return {
            "status": "healthy" if server_info.get("status") != "error" else "unhealthy",
            "server_info": server_info,
            "response_time_ms": response_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Industrial MCP health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"Industrial automation MCP service health check failed: {str(e)}"
        )

@router.get("/tools",
           summary="Get available industrial automation tools",
           description="Retrieve list of available industrial automation MCP tools")
async def get_industrial_tools():
    """Get available industrial automation tools"""
    client = await get_industrial_mcp_client()
    
    try:
        result = await client.execute_mcp_tool("list_tools")
        
        if result.get("success"):
            return {
                "tools": result.get("tools", []),
                "total_count": len(result.get("tools", [])),
                "categories": ["Control Systems", "PLC Integration", "Safety Systems", "Optimization"],
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Return static tool list if MCP unavailable
            static_tools = [
                "create_control_loop", "system_status", "list_control_schemas",
                "memory_search", "plc_connect", "tune_pid_controller", 
                "create_workflow", "validate_safety_system"
            ]
            return {
                "tools": static_tools,
                "total_count": len(static_tools),
                "categories": ["Control Systems", "PLC Integration", "Safety Systems", "Optimization"],
                "source": "static_fallback",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error("Failed to get industrial tools", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve industrial automation tools: {str(e)}"
        )

@router.post("/control-loop/create",
            response_model=ControlLoopResponse,
            summary="Create industrial control loop",
            description="Create a new control loop with AI-optimized parameters")
async def create_control_loop(request: ControlLoopRequest):
    """Create industrial control loop using MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "name": request.name,
            "type": request.loop_type,
            "setpoint": request.setpoint,
            "process_variable": request.process_variable,
            "output_variable": request.output_variable
        }
        
        if request.tuning_params:
            parameters["tuning"] = request.tuning_params
        if request.safety_limits:
            parameters["safety_limits"] = request.safety_limits
        
        result = await client.execute_mcp_tool("create_control_loop", parameters)
        
        if result.get("success"):
            return ControlLoopResponse(
                success=True,
                control_loop_id=result.get("control_loop_id", f"cl_{int(time.time())}"),
                schema_used=result.get("schema", "Advanced PID"),
                parameters=result.get("parameters", parameters),
                validation_score=result.get("validation_score", 95.0),
                recommendations=result.get("recommendations", [])
            )
        else:
            return ControlLoopResponse(
                success=False,
                control_loop_id="",
                schema_used="",
                parameters={},
                validation_score=0.0,
                recommendations=[f"Error: {result.get('error', 'Unknown error')}"]
            )
            
    except Exception as e:
        logger.error("Control loop creation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Control loop creation failed: {str(e)}"
        )

@router.post("/pid/tune",
            response_model=PIDTuningResponse,
            summary="Tune PID controller parameters",
            description="Auto-tune PID controller using AI optimization")
async def tune_pid_controller(request: PIDTuningRequest):
    """Tune PID controller using industrial automation MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "control_loop_id": request.control_loop_id,
            "method": request.tuning_method,
            "criteria": request.performance_criteria
        }
        
        if request.process_data:
            parameters["process_data"] = request.process_data
        
        result = await client.execute_mcp_tool("tune_pid_controller", parameters)
        
        if result.get("success"):
            return PIDTuningResponse(
                success=True,
                tuned_parameters=result.get("tuned_parameters", {}),
                performance_prediction=result.get("performance", {}),
                tuning_method_used=result.get("method_used", request.tuning_method),
                recommendations=result.get("recommendations", [])
            )
        else:
            return PIDTuningResponse(
                success=False,
                tuned_parameters={},
                performance_prediction={},
                tuning_method_used="",
                recommendations=[f"Error: {result.get('error', 'Tuning failed')}"]
            )
            
    except Exception as e:
        logger.error("PID tuning failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"PID tuning failed: {str(e)}"
        )

@router.post("/plc/connect",
            response_model=PLCConnectionResponse,
            summary="Connect to PLC system",
            description="Establish connection to PLC for real-time data access")
async def connect_to_plc(request: PLCConnectionRequest):
    """Connect to PLC using industrial automation MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "address": request.plc_address,
            "type": request.plc_type,
            "slot": request.slot,
            "timeout": request.timeout,
            "protocol": request.protocol
        }
        
        result = await client.execute_mcp_tool("plc_connect", parameters)
        
        if result.get("success"):
            return PLCConnectionResponse(
                success=True,
                connection_id=result.get("connection_id", f"plc_{int(time.time())}"),
                plc_info=result.get("plc_info", {}),
                available_tags=result.get("tags", []),
                connection_status=result.get("status", "Connected")
            )
        else:
            return PLCConnectionResponse(
                success=False,
                connection_id="",
                plc_info={},
                available_tags=[],
                connection_status=f"Failed: {result.get('error', 'Connection failed')}"
            )
            
    except Exception as e:
        logger.error("PLC connection failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"PLC connection failed: {str(e)}"
        )

@router.post("/safety/validate",
            response_model=SafetySystemResponse,
            summary="Validate safety system",
            description="Validate safety interlocks and SIL compliance")
async def validate_safety_system(request: SafetySystemRequest):
    """Validate safety system using industrial automation MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "name": request.safety_system_name,
            "function": request.safety_function,
            "interlocks": request.interlocks,
            "fail_safe_actions": request.fail_safe_actions,
            "sil_level": request.sil_level
        }
        
        result = await client.execute_mcp_tool("validate_safety_system", parameters)
        
        if result.get("success"):
            return SafetySystemResponse(
                validation_passed=result.get("validation_passed", False),
                sil_compliance=result.get("sil_compliance", False),
                safety_score=result.get("safety_score", 0.0),
                compliance_issues=result.get("issues", []),
                recommendations=result.get("recommendations", [])
            )
        else:
            return SafetySystemResponse(
                validation_passed=False,
                sil_compliance=False,
                safety_score=0.0,
                compliance_issues=[f"Validation error: {result.get('error', 'Unknown error')}"],
                recommendations=["Review safety system configuration"]
            )
            
    except Exception as e:
        logger.error("Safety validation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Safety system validation failed: {str(e)}"
        )

@router.get("/system/status",
           response_model=SystemStatusResponse,
           summary="Get system status",
           description="Get comprehensive industrial automation system status")
async def get_system_status():
    """Get system status using industrial automation MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        result = await client.execute_mcp_tool("system_status")
        
        if result.get("success"):
            status_data = result.get("status", {})
            return SystemStatusResponse(
                system_healthy=status_data.get("healthy", False),
                active_control_loops=status_data.get("control_loops", 0),
                plc_connections=status_data.get("plc_connections", 0),
                memory_usage=status_data.get("memory", {}),
                performance_metrics=status_data.get("performance", {}),
                alerts=status_data.get("alerts", [])
            )
        else:
            return SystemStatusResponse(
                system_healthy=False,
                active_control_loops=0,
                plc_connections=0,
                memory_usage={"error": "Status unavailable"},
                performance_metrics={"error": "Metrics unavailable"},
                alerts=[f"System status error: {result.get('error', 'Unknown error')}"]
            )
            
    except Exception as e:
        logger.error("System status check failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"System status check failed: {str(e)}"
        )

@router.get("/knowledge/search",
           response_model=IndustrialKnowledgeResponse,
           summary="Search industrial knowledge base",
           description="Search the industrial automation knowledge repository")
async def search_industrial_knowledge(
    query: str = Query(..., description="Search query"),
    domain: Optional[str] = Query(None, description="Knowledge domain filter"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """Search industrial knowledge using MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "query": query,
            "limit": limit
        }
        
        if domain:
            parameters["domain"] = domain
        
        result = await client.execute_mcp_tool("memory_search", parameters)
        
        if result.get("success"):
            return IndustrialKnowledgeResponse(
                results=result.get("results", []),
                total_found=result.get("total", 0),
                search_time_ms=result.get("search_time", 0.0),
                knowledge_domains=result.get("domains", ["Control Theory", "PLC Programming", "Safety Systems"])
            )
        else:
            return IndustrialKnowledgeResponse(
                results=[],
                total_found=0,
                search_time_ms=0.0,
                knowledge_domains=["Control Theory", "PLC Programming", "Safety Systems"]
            )
            
    except Exception as e:
        logger.error("Knowledge search failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Industrial knowledge search failed: {str(e)}"
        )

@router.get("/schemas/list",
           summary="List control loop schemas",
           description="Get available control loop schema templates")
async def list_control_schemas():
    """List available control loop schemas"""
    client = await get_industrial_mcp_client()
    
    try:
        result = await client.execute_mcp_tool("list_control_schemas")
        
        if result.get("success"):
            return {
                "schemas": result.get("schemas", []),
                "total_count": len(result.get("schemas", [])),
                "categories": result.get("categories", ["PID", "Cascade", "Feedforward"]),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        else:
            # Return static schema list if MCP unavailable
            static_schemas = [
                {"name": "Basic PID", "type": "PID", "description": "Standard PID controller"},
                {"name": "Cascade Control", "type": "Cascade", "description": "Two-loop cascade control"},
                {"name": "Feedforward PID", "type": "Feedforward", "description": "PID with feedforward compensation"}
            ]
            return {
                "schemas": static_schemas,
                "total_count": len(static_schemas),
                "categories": ["PID", "Cascade", "Feedforward"],
                "source": "static_fallback",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
    except Exception as e:
        logger.error("Schema listing failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list control schemas: {str(e)}"
        )

@router.get("/integration/status",
           summary="Get industrial automation integration status",
           description="Check comprehensive industrial automation MCP integration status")
async def get_integration_status():
    """Get comprehensive industrial automation integration status"""
    client = await get_industrial_mcp_client()
    
    try:
        # Check multiple MCP capabilities
        server_info = await client.get_server_info()
        tools_result = await client.execute_mcp_tool("list_tools")
        
        # Determine integration health
        mcp_healthy = server_info.get("status") not in ["error", "unavailable"]
        tools_available = len(tools_result.get("tools", [])) if tools_result.get("success") else 0
        
        return {
            "integration_status": "active" if mcp_healthy else "degraded",
            "mcp_server_healthy": mcp_healthy,
            "tools_available": tools_available,
            "server_info": server_info,
            "capabilities": [
                "Control Loop Management",
                "PID Auto-Tuning", 
                "PLC Integration",
                "Safety System Validation",
                "Industrial Knowledge Search"
            ],
            "fine_tuned_llm_access": "via_http_proxy",
            "model_id": "ft:gpt-4o:industrial-control:20250117",
            "proxy_version": "1.0.0",
            "mcp_directory": INDUSTRIAL_MCP_CONFIG["mcp_directory"],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Integration status check failed", error=str(e))
        return {
            "integration_status": "error",
            "mcp_server_healthy": False,
            "tools_available": 0,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# EXPERT ASSISTANCE ENDPOINTS
# =============================================================================

@router.post("/expert/control-guidance",
            summary="Get industrial control expert guidance",
            description="Get expert-level guidance on industrial control systems")
async def get_control_guidance(
    problem_description: str = Body(..., description="Description of the control problem"),
    system_type: str = Body("generic", description="Type of system (distillation, reactor, etc.)")
):
    """Get expert control guidance using industrial automation MCP"""
    client = await get_industrial_mcp_client()
    
    try:
        parameters = {
            "problem": problem_description,
            "system_type": system_type,
            "prompt_type": "industrial_control_expert"
        }
        
        result = await client.execute_mcp_tool("get_expert_guidance", parameters)
        
        return {
            "guidance": result.get("guidance", "Expert guidance unavailable"),
            "recommendations": result.get("recommendations", []),
            "reference_standards": result.get("standards", []),
            "expert_level": "Senior Industrial Control Engineer",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error("Expert guidance failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Expert guidance request failed: {str(e)}"
        )

# =============================================================================
# STARTUP AND SHUTDOWN HANDLERS
# =============================================================================

async def startup_industrial_mcp_proxy():
    """Initialize industrial automation MCP proxy on startup"""
    logger.info("Initializing industrial automation MCP proxy integration")
    
    try:
        client = await get_industrial_mcp_client()
        server_info = await client.get_server_info()
        
        logger.info("Industrial automation MCP proxy integration ready", 
                   status=server_info.get("status"))
                   
    except Exception as e:
        logger.warning("Industrial automation MCP server not immediately available", 
                      error=str(e))

async def shutdown_industrial_mcp_proxy():
    """Clean up industrial automation MCP proxy on shutdown"""
    global _industrial_mcp_client
    
    _industrial_mcp_client = None
    logger.info("Industrial automation MCP proxy integration shut down")

# Export router and handlers for main gateway application
__all__ = ["router", "startup_industrial_mcp_proxy", "shutdown_industrial_mcp_proxy"] 