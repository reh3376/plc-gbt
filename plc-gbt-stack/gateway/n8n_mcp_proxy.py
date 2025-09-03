#!/usr/bin/env python3
"""
N8N-MCP Proxy Gateway
Phase 26.7: Fine-tuned LLM Integration with n8n-MCP

Provides HTTP proxy endpoints that allow the fine-tuned OpenAI LLM
(ft:gpt-4o:industrial-control:20250117) to access n8n-MCP functionality
through the existing PLC-GBT Gateway API architecture.

This solves the problem that the OpenAI LLM runs on remote servers and
cannot directly access our local n8n-MCP server.

Author: AI Task Orchestrator
Date: July 23, 2025
Phase: 26.7 - N8N-MCP AI Enhancement Integration
"""

import asyncio
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from fastapi import APIRouter, Body, HTTPException, Path, Query
from pydantic import BaseModel, Field

# Configure logging
logger = structlog.get_logger()

# N8N-MCP Configuration
N8N_MCP_CONFIG = {
    "base_url": os.getenv("N8N_MCP_URL", "http://127.0.0.1:3000"),
    "auth_token": os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025"),
    "timeout": int(os.getenv("N8N_MCP_TIMEOUT", "30")),
    "max_retries": int(os.getenv("N8N_MCP_MAX_RETRIES", "3")),
    "connection_pool_size": 10
}

# Initialize FastAPI router
router = APIRouter(prefix="/api/v1/n8n-mcp", tags=["N8N-MCP Integration"])

# Pydantic models for request/response validation
class NodeSearchRequest(BaseModel):
    query: str = Field(..., description="Search query for n8n nodes")
    category: Optional[str] = Field(None, description="Node category filter")
    limit: Optional[int] = Field(10, description="Maximum results to return")

class NodeSearchResponse(BaseModel):
    nodes: List[Dict[str, Any]] = Field(..., description="Found n8n nodes")
    total_count: int = Field(..., description="Total number of nodes found")
    search_time_ms: float = Field(..., description="Search execution time")

class WorkflowValidationRequest(BaseModel):
    workflow: Dict[str, Any] = Field(..., description="n8n workflow to validate")
    validation_level: str = Field("standard", description="Validation level: basic, standard, comprehensive")

class WorkflowValidationResponse(BaseModel):
    valid: bool = Field(..., description="Whether workflow is valid")
    score: float = Field(..., description="Validation score (0-100)")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    suggestions: List[str] = Field(default_factory=list, description="Optimization suggestions")

class NodeEssentialsResponse(BaseModel):
    node_type: str = Field(..., description="Node type identifier")
    essential_properties: List[Dict[str, Any]] = Field(..., description="Essential node properties")
    examples: Dict[str, Any] = Field(..., description="Configuration examples")
    documentation: str = Field(..., description="Node documentation")

class AIToolsResponse(BaseModel):
    ai_tools: List[Dict[str, Any]] = Field(..., description="Available AI-capable nodes")
    total_count: int = Field(..., description="Total AI tools available")
    categories: List[str] = Field(..., description="AI tool categories")

# HTTP Client for n8n-MCP communication
class N8NMCPClient:
    """HTTP client for communicating with n8n-MCP server"""

    def __init__(self):
        self.base_url = N8N_MCP_CONFIG["base_url"]
        self.auth_token = N8N_MCP_CONFIG["auth_token"]
        self.timeout = aiohttp.ClientTimeout(total=N8N_MCP_CONFIG["timeout"])
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=N8N_MCP_CONFIG["connection_pool_size"],
            limit_per_host=5
        )
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=self.timeout,
            headers=self.headers
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to n8n-MCP server with retry logic"""
        if not self.session:
            raise RuntimeError("HTTP session not initialized")

        url = f"{self.base_url}{endpoint}"
        retries = 0
        max_retries = N8N_MCP_CONFIG["max_retries"]

        while retries <= max_retries:
            try:
                if method.upper() == "GET":
                    async with self.session.get(url, params=params) as response:
                        return await self._handle_response(response)
                elif method.upper() == "POST":
                    async with self.session.post(url, json=data, params=params) as response:
                        return await self._handle_response(response)
                elif method.upper() == "PUT":
                    async with self.session.put(url, json=data, params=params) as response:
                        return await self._handle_response(response)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

            except aiohttp.ClientError as e:
                retries += 1
                if retries > max_retries:
                    logger.error(f"HTTP request failed after {max_retries} retries",
                               url=url, error=str(e))
                    raise HTTPException(
                        status_code=503,
                        detail=f"n8n-MCP service unavailable: {str(e)}"
                    )

                # Exponential backoff
                wait_time = 2 ** retries
                await asyncio.sleep(wait_time)
                logger.warning(f"Retrying request in {wait_time}s",
                             url=url, attempt=retries)

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response and errors"""
        if response.status == 200:
            return await response.json()
        elif response.status == 401:
            raise HTTPException(
                status_code=401,
                detail="n8n-MCP authentication failed"
            )
        elif response.status == 404:
            raise HTTPException(
                status_code=404,
                detail="n8n-MCP endpoint not found"
            )
        elif response.status == 429:
            raise HTTPException(
                status_code=429,
                detail="n8n-MCP rate limit exceeded"
            )
        else:
            error_text = await response.text()
            logger.error("n8n-MCP request failed",
                        status=response.status, error=error_text)
            raise HTTPException(
                status_code=response.status,
                detail=f"n8n-MCP error: {error_text}"
            )

# Global client instance
_mcp_client: Optional[N8NMCPClient] = None

async def get_mcp_client() -> N8NMCPClient:
    """Get or create n8n-MCP client instance"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = N8NMCPClient()
    return _mcp_client

# =============================================================================
# N8N-MCP PROXY ENDPOINTS
# =============================================================================

@router.get("/health",
           summary="Check n8n-MCP service health",
           description="Verify that n8n-MCP service is accessible and healthy")
async def check_n8n_mcp_health():
    """Check n8n-MCP service health status"""
    start_time = time.time()

    try:
        async with N8NMCPClient() as client:
            health_data = await client.make_request("GET", "/health")

        response_time = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "n8n_mcp_status": health_data.get("status", "unknown"),
            "response_time_ms": response_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("n8n-MCP health check failed", error=str(e))
        raise HTTPException(
            status_code=503,
            detail=f"n8n-MCP service health check failed: {str(e)}"
        )

@router.get("/tools",
           summary="Get available MCP tools",
           description="Retrieve list of available n8n-MCP tools and capabilities")
async def get_mcp_tools():
    """Get available n8n-MCP tools"""
    try:
        async with N8NMCPClient() as client:
            tools_data = await client.make_request("GET", "/tools")

        return {
            "tools": tools_data.get("tools", []),
            "total_count": len(tools_data.get("tools", [])),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Failed to retrieve MCP tools", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve MCP tools: {str(e)}"
        )

@router.get("/nodes/search",
           response_model=NodeSearchResponse,
           summary="Search n8n nodes",
           description="Search for n8n nodes by query, category, or functionality")
async def search_nodes(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Node category filter"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results")
):
    """Search for n8n nodes using n8n-MCP"""
    start_time = time.time()

    try:
        params = {"query": query, "limit": limit}
        if category:
            params["category"] = category

        async with N8NMCPClient() as client:
            search_data = await client.make_request("GET", "/search/nodes", params=params)

        search_time = (time.time() - start_time) * 1000

        return NodeSearchResponse(
            nodes=search_data.get("nodes", []),
            total_count=len(search_data.get("nodes", [])),
            search_time_ms=search_time
        )

    except Exception as e:
        logger.error("Node search failed", query=query, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Node search failed: {str(e)}"
        )

@router.get("/nodes/{node_type}/essentials",
           response_model=NodeEssentialsResponse,
           summary="Get node essentials",
           description="Get essential properties and configuration for a specific node type")
async def get_node_essentials(
    node_type: str = Path(..., description="Node type identifier")
):
    """Get essential properties for a specific node type"""
    try:
        async with N8NMCPClient() as client:
            essentials_data = await client.make_request(
                "GET", f"/nodes/{node_type}/essentials"
            )

        return NodeEssentialsResponse(
            node_type=node_type,
            essential_properties=essentials_data.get("properties", []),
            examples=essentials_data.get("examples", {}),
            documentation=essentials_data.get("documentation", "")
        )

    except Exception as e:
        logger.error("Failed to get node essentials", node_type=node_type, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get node essentials: {str(e)}"
        )

@router.post("/workflow/validate",
            response_model=WorkflowValidationResponse,
            summary="Validate n8n workflow",
            description="Validate an n8n workflow structure and configuration")
async def validate_workflow(request: WorkflowValidationRequest):
    """Validate n8n workflow using n8n-MCP validation tools"""
    try:
        data = {
            "workflow": request.workflow,
            "validation_level": request.validation_level
        }

        async with N8NMCPClient() as client:
            validation_data = await client.make_request("POST", "/validate/workflow", data=data)

        return WorkflowValidationResponse(
            valid=validation_data.get("valid", False),
            score=validation_data.get("score", 0.0),
            errors=validation_data.get("errors", []),
            warnings=validation_data.get("warnings", []),
            suggestions=validation_data.get("suggestions", [])
        )

    except Exception as e:
        logger.error("Workflow validation failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Workflow validation failed: {str(e)}"
        )

@router.get("/ai-tools",
           response_model=AIToolsResponse,
           summary="Get AI-capable nodes",
           description="Retrieve list of nodes that can be used as AI tools")
async def get_ai_tools():
    """Get list of AI-capable n8n nodes"""
    try:
        async with N8NMCPClient() as client:
            ai_tools_data = await client.make_request("GET", "/ai/tools")

        return AIToolsResponse(
            ai_tools=ai_tools_data.get("tools", []),
            total_count=len(ai_tools_data.get("tools", [])),
            categories=ai_tools_data.get("categories", [])
        )

    except Exception as e:
        logger.error("Failed to get AI tools", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI tools: {str(e)}"
        )

@router.get("/database/stats",
           summary="Get n8n-MCP database statistics",
           description="Retrieve statistics about the n8n-MCP node database")
async def get_database_stats():
    """Get n8n-MCP database statistics"""
    try:
        async with N8NMCPClient() as client:
            stats_data = await client.make_request("GET", "/database/stats")

        return {
            "database_ready": stats_data.get("ready", False),
            "node_count": stats_data.get("node_count", 0),
            "properties_count": stats_data.get("properties_count", 0),
            "documentation_coverage": stats_data.get("documentation_coverage", 0),
            "ai_tools_count": stats_data.get("ai_tools_count", 0),
            "last_updated": stats_data.get("last_updated"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Failed to get database stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get database statistics: {str(e)}"
        )

@router.post("/workflow/create",
            summary="Create n8n workflow",
            description="Create a new workflow in the connected n8n instance")
async def create_workflow(
    workflow: Dict[str, Any] = Body(..., description="Workflow definition")
):
    """Create a new workflow in n8n via MCP"""
    try:
        data = {"workflow": workflow}

        async with N8NMCPClient() as client:
            result = await client.make_request("POST", "/n8n/workflows", data=data)

        return {
            "success": True,
            "workflow_id": result.get("id"),
            "workflow_name": result.get("name"),
            "active": result.get("active", False),
            "created_at": result.get("created_at"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Failed to create workflow", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create workflow: {str(e)}"
        )

@router.get("/workflow/{workflow_id}/validate",
           summary="Validate existing workflow",
           description="Validate a workflow that exists in the n8n instance")
async def validate_existing_workflow(
    workflow_id: str = Path(..., description="Workflow ID to validate")
):
    """Validate an existing workflow in n8n"""
    try:
        async with N8NMCPClient() as client:
            result = await client.make_request(
                "GET", f"/n8n/workflows/{workflow_id}/validate"
            )

        return {
            "workflow_id": workflow_id,
            "valid": result.get("valid", False),
            "validation_score": result.get("score", 0.0),
            "issues": result.get("issues", []),
            "recommendations": result.get("recommendations", []),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Failed to validate existing workflow",
                    workflow_id=workflow_id, error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate workflow: {str(e)}"
        )

# =============================================================================
# ADVANCED N8N-MCP INTEGRATION ENDPOINTS
# =============================================================================

@router.post("/workflow/optimize",
            summary="Optimize workflow performance",
            description="Use AI to optimize workflow performance and efficiency")
async def optimize_workflow(
    workflow: Dict[str, Any] = Body(..., description="Workflow to optimize"),
    optimization_goals: List[str] = Body(["performance", "reliability"],
                                       description="Optimization objectives")
):
    """Optimize workflow using n8n-MCP AI capabilities"""
    try:
        data = {
            "workflow": workflow,
            "goals": optimization_goals
        }

        async with N8NMCPClient() as client:
            result = await client.make_request("POST", "/optimize/workflow", data=data)

        return {
            "optimized_workflow": result.get("workflow"),
            "improvements": result.get("improvements", []),
            "performance_gain": result.get("performance_gain", 0),
            "optimization_score": result.get("score", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Workflow optimization failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Workflow optimization failed: {str(e)}"
        )

@router.get("/templates/industrial",
           summary="Get industrial automation templates",
           description="Retrieve pre-configured templates for industrial automation workflows")
async def get_industrial_templates():
    """Get industrial automation workflow templates"""
    try:
        async with N8NMCPClient() as client:
            templates = await client.make_request("GET", "/templates/industrial")

        return {
            "templates": templates.get("templates", []),
            "categories": templates.get("categories", []),
            "total_count": len(templates.get("templates", [])),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Failed to get industrial templates", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get industrial templates: {str(e)}"
        )

# =============================================================================
# INTEGRATION STATUS AND DIAGNOSTICS
# =============================================================================

@router.get("/integration/status",
           summary="Get integration status",
           description="Check the status of n8n-MCP integration with PLC-GBT")
async def get_integration_status():
    """Get comprehensive integration status"""
    try:
        async with N8NMCPClient() as client:
            # Check multiple endpoints to verify integration
            health_check = await client.make_request("GET", "/health")
            tools_check = await client.make_request("GET", "/tools")
            stats_check = await client.make_request("GET", "/database/stats")

        return {
            "integration_status": "active",
            "n8n_mcp_healthy": health_check.get("status") == "healthy",
            "tools_available": len(tools_check.get("tools", [])),
            "database_ready": stats_check.get("ready", False),
            "node_coverage": stats_check.get("node_count", 0),
            "ai_tools_count": stats_check.get("ai_tools_count", 0),
            "fine_tuned_llm_access": "via_http_proxy",
            "model_id": "ft:gpt-4o:industrial-control:20250117",
            "proxy_version": "1.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        logger.error("Integration status check failed", error=str(e))
        return {
            "integration_status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# STARTUP AND SHUTDOWN HANDLERS
# =============================================================================

async def startup_n8n_mcp_proxy():
    """Initialize n8n-MCP proxy on startup"""
    logger.info("Initializing n8n-MCP proxy integration")

    try:
        # Test connectivity to n8n-MCP service
        async with N8NMCPClient() as client:
            health_data = await client.make_request("GET", "/health")

        logger.info("n8n-MCP proxy integration ready",
                   status=health_data.get("status"))

    except Exception as e:
        logger.warning("n8n-MCP service not immediately available",
                      error=str(e))

async def shutdown_n8n_mcp_proxy():
    """Clean up n8n-MCP proxy on shutdown"""
    global _mcp_client

    if _mcp_client and _mcp_client.session:
        await _mcp_client.session.close()
        _mcp_client = None

    logger.info("n8n-MCP proxy integration shut down")

# Export router and handlers for main gateway application
__all__ = ["router", "startup_n8n_mcp_proxy", "shutdown_n8n_mcp_proxy"]
