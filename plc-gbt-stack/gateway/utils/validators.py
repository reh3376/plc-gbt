"""
Common Validation Utilities
Extracted validation patterns to reduce code duplication
"""

from typing import Dict, Any, List, Optional
import structlog

logger = structlog.get_logger()

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None, 
                 validation_errors: Optional[List[str]] = None):
        self.message = message
        self.field = field
        self.validation_errors = validation_errors or []
        super().__init__(self.message)

def validate_mcp_response(response: Dict[str, Any], required_fields: List[str]) -> bool:
    """
    Validate MCP response has required fields
    """
    missing_fields = [field for field in required_fields if field not in response]
    
    if missing_fields:
        raise ValidationError(
            f"Missing required fields in MCP response: {missing_fields}",
            validation_errors=missing_fields
        )
    
    return True

def validate_request_parameters(params: Dict[str, Any], 
                               required: List[str],
                               optional: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Validate request parameters
    """
    optional = optional or []
    errors = []
    
    # Check required parameters
    for param in required:
        if param not in params or params[param] is None:
            errors.append(f"Missing required parameter: {param}")
    
    # Filter to only allowed parameters
    allowed_params = set(required + optional)
    filtered_params = {k: v for k, v in params.items() if k in allowed_params}
    
    if errors:
        raise ValidationError(
            "Parameter validation failed",
            validation_errors=errors
        )
    
    return filtered_params

def validate_response_format(response: Dict[str, Any], expected_format: str) -> bool:
    """
    Validate response follows expected format
    """
    if expected_format == "mcp_tool_response":
        required_fields = ["success"]
        return validate_mcp_response(response, required_fields)
    elif expected_format == "api_response":
        required_fields = ["status", "data"]
        return validate_mcp_response(response, required_fields)
    else:
        logger.warning(f"Unknown response format: {expected_format}")
        return True 