"""
Common Error Handling Utilities
Extracted error handling patterns to reduce code duplication
"""

from typing import Any, Dict, Optional

import structlog
from fastapi import HTTPException

logger = structlog.get_logger()

class MCPError(Exception):
    """Custom exception for MCP-related errors"""
    def __init__(self, message: str, error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def handle_mcp_error(error: Exception, operation: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Standardized error handling for MCP operations
    Returns a consistent error response format
    """
    context = context or {}

    logger.error(f"MCP operation failed: {operation}",
                error=str(error), context=context)

    if isinstance(error, MCPError):
        return {
            "success": False,
            "error": error.message,
            "error_code": error.error_code,
            "details": error.details,
            "operation": operation
        }
    else:
        return {
            "success": False,
            "error": f"{operation} failed: {str(error)}",
            "operation": operation
        }

def handle_http_error(error: Exception, operation: str, status_code: int = 500) -> HTTPException:
    """
    Convert exceptions to standardized HTTP exceptions
    """
    logger.error(f"HTTP operation failed: {operation}", error=str(error))

    if isinstance(error, HTTPException):
        return error
    elif isinstance(error, MCPError):
        return HTTPException(
            status_code=status_code,
            detail=f"{operation} failed: {error.message}"
        )
    else:
        return HTTPException(
            status_code=status_code,
            detail=f"{operation} failed: {str(error)}"
        )

def create_error_response(success: bool = False, error: str = "",
                         operation: str = "", **kwargs) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "success": success,
        "error": error,
        "operation": operation,
        **kwargs
    }

def create_success_response(data: Dict[str, Any], operation: str = "") -> Dict[str, Any]:
    """Create standardized success response"""
    return {
        "success": True,
        "operation": operation,
        **data
    }
