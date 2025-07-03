#!/usr/bin/env python3
"""
Authentication Middleware for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from auth.jwt_manager import JWTManager, get_jwt_manager
from auth.rbac import Role
from monitoring.enterprise_monitoring import get_monitoring


class AuthenticationMiddleware:
    """
    Authentication middleware that validates JWT tokens and sets user context.
    """
    
    def __init__(self):
        self.jwt_manager = get_jwt_manager()
        self.monitoring = get_monitoring()
        
        # Paths that don't require authentication
        self.public_paths = {
            '/api/v1/enterprise/auth/login',
            '/api/v1/enterprise/auth/refresh',
            '/api/v1/enterprise/monitoring/health',
            '/health',
            '/metrics',
            '/docs',
            '/openapi.json'
        }
    
    async def __call__(self, request: Request, call_next):
        """Process the request."""
        start_time = time.time()
        
        try:
            # Skip authentication for public paths
            if self._is_public_path(request.url.path):
                return await call_next(request)
            
            # Extract and validate token
            token = self._extract_token(request)
            
            if not token:
                return self._unauthorized_response("Missing authentication token")
            
            # Validate token
            try:
                payload = self.jwt_manager.decode_token(token)
                
                # Set user context in request state
                request.state.user_id = payload.get('user_id')
                request.state.user_email = payload.get('email')
                request.state.user_role = Role(payload.get('role', 'guest'))
                request.state.user_permissions = payload.get('permissions', [])
                request.state.authenticated = True
                
                # Record successful authentication
                self.monitoring.record_auth_attempt("success", "jwt")
                
            except Exception as e:
                # Record failed authentication
                self.monitoring.record_auth_attempt("failure", "jwt")
                return self._unauthorized_response(f"Invalid token: {str(e)}")
            
            # Process request
            response = await call_next(request)
            
            # Add authentication headers
            response.headers['X-User-ID'] = request.state.user_id
            response.headers['X-User-Role'] = request.state.user_role.value
            
            return response
            
        except Exception as e:
            # Record error
            self.monitoring.record_error("auth_middleware_error", "middleware")
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Authentication service error"}
            )
        
        finally:
            # Record request processing time
            duration = time.time() - start_time
            user_role = getattr(request.state, 'user_role', Role.GUEST)
            
            self.monitoring.record_request(
                method=request.method,
                endpoint=request.url.path,
                status_code=200,  # This will be updated by monitoring middleware
                duration=duration,
                user_role=user_role
            )
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public (doesn't require authentication)."""
        return path in self.public_paths or path.startswith('/static/')
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request headers."""
        authorization = request.headers.get('Authorization')
        
        if not authorization:
            return None
        
        parts = authorization.split(' ')
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    def _unauthorized_response(self, message: str) -> JSONResponse:
        """Return unauthorized response."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Unauthorized",
                "message": message
            },
            headers={"WWW-Authenticate": "Bearer"}
        ) 