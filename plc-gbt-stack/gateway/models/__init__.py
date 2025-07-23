# Gateway Models Package
# Extracted Pydantic models to reduce complexity in main proxy files

from .industrial_mcp_models import *
from .n8n_mcp_models import *

__all__ = [
    # Industrial MCP Models
    'ControlLoopRequest', 'ControlLoopResponse', 'PIDTuningRequest', 'PIDTuningResponse',
    'PLCConnectionRequest', 'PLCConnectionResponse', 'SafetySystemRequest', 'SafetySystemResponse',
    'SystemStatusResponse', 'IndustrialKnowledgeRequest', 'IndustrialKnowledgeResponse',
    
    # N8N MCP Models
    'NodeSearchRequest', 'NodeSearchResponse', 'WorkflowValidationRequest', 'WorkflowValidationResponse',
    'NodeEssentialsResponse', 'AIToolsResponse'
] 