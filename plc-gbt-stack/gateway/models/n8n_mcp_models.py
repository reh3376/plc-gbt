"""
N8N MCP Pydantic Models
Extracted from n8n_mcp_proxy.py to reduce complexity
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


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
