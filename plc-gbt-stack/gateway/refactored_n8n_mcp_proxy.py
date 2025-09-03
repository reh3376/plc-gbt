#!/usr/bin/env python3
"""
Refactored N8N-MCP Proxy Gateway
Phase 26.7: Fine-tuned LLM Integration with n8n-MCP

Simplified proxy using extracted models, clients, and utilities.
Reduced complexity from 576 lines to ~150 lines.

Author: AI Task Orchestrator
Date: July 23, 2025
Phase: 26.7 - N8N-MCP AI Enhancement Integration (Refactored)
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Body, Path, Query

from .clients import N8NMCPClient
from .models import (
    AIToolsResponse,
    NodeEssentialsResponse,
    NodeSearchResponse,
    WorkflowValidationRequest,
    WorkflowValidationResponse,
)
from .utils import handle_http_error

# Configure logging
logger = structlog.get_logger()

# Initialize FastAPI router
router = APIRouter(prefix="/api/v1/n8n-mcp", tags=["N8N-MCP Integration"])

# Global client instance
_n8n_client: Optional[N8NMCPClient] = None

async def get_client() -> N8NMCPClient:
    """Get or create N8N MCP client instance"""
    global _n8n_client
    if _n8n_client is None:
        _n8n_client = N8NMCPClient()
    return _n8n_client

# =============================================================================
# CORE N8N-MCP ENDPOINTS
# =============================================================================

@router.get("/health")
async def check_health():
    """Check N8N-MCP service health"""
    start_time = time.time()
    client = await get_client()

    try:
        async with client as c:
            health_data = await c.check_health()

        response_time = (time.time() - start_time) * 1000

        return {
            "status": "healthy",
            "n8n_mcp_status": health_data.get("status", "unknown"),
            "response_time_ms": response_time,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise handle_http_error(e, "N8N-MCP health check", 503)

@router.get("/nodes/search", response_model=NodeSearchResponse)
async def search_nodes(
    query: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None, description="Node category filter"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results")
):
    """Search for N8N nodes"""
    start_time = time.time()
    client = await get_client()

    try:
        async with client as c:
            search_data = await c.search_nodes(query, category, limit)

        search_time = (time.time() - start_time) * 1000

        return NodeSearchResponse(
            nodes=search_data.get("nodes", []),
            total_count=len(search_data.get("nodes", [])),
            search_time_ms=search_time
        )

    except Exception as e:
        raise handle_http_error(e, "Node search", 500)

@router.get("/nodes/{node_type}/essentials", response_model=NodeEssentialsResponse)
async def get_node_essentials(node_type: str = Path(..., description="Node type identifier")):
    """Get essential properties for a node type"""
    client = await get_client()

    try:
        async with client as c:
            essentials_data = await c.get_node_essentials(node_type)

        return NodeEssentialsResponse(
            node_type=node_type,
            essential_properties=essentials_data.get("properties", []),
            examples=essentials_data.get("examples", {}),
            documentation=essentials_data.get("documentation", "")
        )

    except Exception as e:
        raise handle_http_error(e, "Get node essentials", 500)

@router.post("/workflow/validate", response_model=WorkflowValidationResponse)
async def validate_workflow(request: WorkflowValidationRequest):
    """Validate N8N workflow"""
    client = await get_client()

    try:
        async with client as c:
            validation_data = await c.validate_workflow(
                request.workflow,
                request.validation_level
            )

        return WorkflowValidationResponse(
            valid=validation_data.get("valid", False),
            score=validation_data.get("score", 0.0),
            errors=validation_data.get("errors", []),
            warnings=validation_data.get("warnings", []),
            suggestions=validation_data.get("suggestions", [])
        )

    except Exception as e:
        raise handle_http_error(e, "Workflow validation", 500)

@router.get("/ai-tools", response_model=AIToolsResponse)
async def get_ai_tools():
    """Get AI-capable N8N nodes"""
    client = await get_client()

    try:
        async with client as c:
            ai_tools_data = await c.get_ai_tools()

        return AIToolsResponse(
            ai_tools=ai_tools_data.get("tools", []),
            total_count=len(ai_tools_data.get("tools", [])),
            categories=ai_tools_data.get("categories", [])
        )

    except Exception as e:
        raise handle_http_error(e, "Get AI tools", 500)

# =============================================================================
# WORKFLOW MANAGEMENT ENDPOINTS
# =============================================================================

@router.post("/workflow/create")
async def create_workflow(workflow: Dict[str, Any] = Body(..., description="Workflow definition")):
    """Create new workflow in N8N"""
    client = await get_client()

    try:
        async with client as c:
            result = await c.create_workflow(workflow)

        return {
            "success": True,
            "workflow_id": result.get("id"),
            "workflow_name": result.get("name"),
            "active": result.get("active", False),
            "created_at": result.get("created_at"),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise handle_http_error(e, "Create workflow", 500)

@router.post("/workflow/optimize")
async def optimize_workflow(
    workflow: Dict[str, Any] = Body(..., description="Workflow to optimize"),
    optimization_goals: List[str] = Body(["performance", "reliability"],
                                       description="Optimization objectives")
):
    """Optimize workflow performance"""
    client = await get_client()

    try:
        async with client as c:
            result = await c.optimize_workflow(workflow, optimization_goals)

        return {
            "optimized_workflow": result.get("workflow"),
            "improvements": result.get("improvements", []),
            "performance_gain": result.get("performance_gain", 0),
            "optimization_score": result.get("score", 0),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        raise handle_http_error(e, "Workflow optimization", 500)

# =============================================================================
# INTEGRATION STATUS AND UTILITIES
# =============================================================================

@router.get("/integration/status")
async def get_integration_status():
    """Get comprehensive integration status"""
    client = await get_client()

    try:
        async with client as c:
            health_check = await c.check_health()
            stats_check = await c.get_database_stats()

        return {
            "integration_status": "active",
            "n8n_mcp_healthy": health_check.get("status") == "healthy",
            "database_ready": stats_check.get("ready", False),
            "node_coverage": stats_check.get("node_count", 0),
            "ai_tools_count": stats_check.get("ai_tools_count", 0),
            "fine_tuned_llm_access": "via_http_proxy",
            "model_id": "ft:gpt-4o:industrial-control:20250117",
            "proxy_version": "2.0.0-refactored",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        return {
            "integration_status": "error",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# =============================================================================
# STARTUP AND SHUTDOWN HANDLERS
# =============================================================================

async def startup_n8n_mcp_proxy():
    """Initialize N8N-MCP proxy on startup"""
    logger.info("Initializing refactored N8N-MCP proxy integration")

    try:
        client = await get_client()
        async with client as c:
            health_data = await c.check_health()

        logger.info("Refactored N8N-MCP proxy integration ready",
                   status=health_data.get("status"))

    except Exception as e:
        logger.warning("N8N-MCP service not immediately available", error=str(e))

async def shutdown_n8n_mcp_proxy():
    """Clean up N8N-MCP proxy on shutdown"""
    global _n8n_client
    _n8n_client = None
    logger.info("Refactored N8N-MCP proxy integration shut down")

# Export router and handlers
__all__ = ["router", "startup_n8n_mcp_proxy", "shutdown_n8n_mcp_proxy"]
