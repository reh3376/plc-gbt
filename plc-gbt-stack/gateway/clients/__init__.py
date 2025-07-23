# Gateway Clients Package
# Specialized MCP clients to reduce complexity in main proxy files

from .industrial_mcp_client import IndustrialMCPClient
from .n8n_mcp_client import N8NMCPClient

__all__ = ['IndustrialMCPClient', 'N8NMCPClient'] 