"""
N8N MCP Client
Extracted from n8n_mcp_proxy.py to reduce complexity
"""

import os
from typing import Dict, Any, Optional
from ..utils import HTTPClientBase, RetryConfig, handle_mcp_error
import structlog

logger = structlog.get_logger()

class N8NMCPClient(HTTPClientBase):
    """Specialized HTTP client for N8N-MCP communication"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        config = config or self._get_default_config()
        
        retry_config = RetryConfig(
            max_retries=config.get("max_retries", 3),
            timeout=config.get("timeout", 30.0)
        )
        
        super().__init__(
            base_url=config["base_url"],
            auth_token=config["auth_token"],
            retry_config=retry_config
        )
        
        self.config = config
    
    @staticmethod
    def _get_default_config() -> Dict[str, Any]:
        """Get default N8N-MCP configuration from environment"""
        return {
            "base_url": os.getenv("N8N_MCP_URL", "http://127.0.0.1:3000"),
            "auth_token": os.getenv("N8N_MCP_AUTH_TOKEN", "n8n-mcp-auth-token-2025"),
            "timeout": int(os.getenv("N8N_MCP_TIMEOUT", "30")),
            "max_retries": int(os.getenv("N8N_MCP_MAX_RETRIES", "3")),
            "connection_pool_size": 10
        }
    
    async def search_nodes(self, query: str, category: Optional[str] = None, 
                          limit: int = 10) -> Dict[str, Any]:
        """Search for n8n nodes"""
        params = {"query": query, "limit": limit}
        if category:
            params["category"] = category
        
        try:
            return await self.make_request("GET", "/search/nodes", params=params)
        except Exception as e:
            return handle_mcp_error(e, "search_nodes", {"query": query, "category": category})
    
    async def get_node_essentials(self, node_type: str) -> Dict[str, Any]:
        """Get essential properties for a node type"""
        try:
            return await self.make_request("GET", f"/nodes/{node_type}/essentials")
        except Exception as e:
            return handle_mcp_error(e, "get_node_essentials", {"node_type": node_type})
    
    async def validate_workflow(self, workflow: Dict[str, Any], 
                               validation_level: str = "standard") -> Dict[str, Any]:
        """Validate an n8n workflow"""
        data = {
            "workflow": workflow,
            "validation_level": validation_level
        }
        
        try:
            return await self.make_request("POST", "/validate/workflow", data=data)
        except Exception as e:
            return handle_mcp_error(e, "validate_workflow", {"validation_level": validation_level})
    
    async def get_ai_tools(self) -> Dict[str, Any]:
        """Get list of AI-capable n8n nodes"""
        try:
            return await self.make_request("GET", "/ai/tools")
        except Exception as e:
            return handle_mcp_error(e, "get_ai_tools")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get n8n-MCP database statistics"""
        try:
            return await self.make_request("GET", "/database/stats")
        except Exception as e:
            return handle_mcp_error(e, "get_database_stats")
    
    async def create_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workflow in n8n"""
        data = {"workflow": workflow}
        
        try:
            return await self.make_request("POST", "/n8n/workflows", data=data)
        except Exception as e:
            return handle_mcp_error(e, "create_workflow")
    
    async def optimize_workflow(self, workflow: Dict[str, Any], 
                               optimization_goals: list = None) -> Dict[str, Any]:
        """Optimize workflow using AI capabilities"""
        optimization_goals = optimization_goals or ["performance", "reliability"]
        data = {
            "workflow": workflow,
            "goals": optimization_goals
        }
        
        try:
            return await self.make_request("POST", "/optimize/workflow", data=data)
        except Exception as e:
            return handle_mcp_error(e, "optimize_workflow")
    
    async def get_industrial_templates(self) -> Dict[str, Any]:
        """Get industrial automation workflow templates"""
        try:
            return await self.make_request("GET", "/templates/industrial")
        except Exception as e:
            return handle_mcp_error(e, "get_industrial_templates")
    
    async def check_health(self) -> Dict[str, Any]:
        """Check N8N-MCP service health"""
        try:
            return await self.make_request("GET", "/health")
        except Exception as e:
            return handle_mcp_error(e, "health_check") 