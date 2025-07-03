#!/usr/bin/env python3
"""
Enterprise API Endpoints for PLC-GPT
Phase 3 Days 6-7: Enterprise Features Integration
"""

import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

# Import our enterprise components
from auth.jwt_manager import JWTManager, get_jwt_manager
from auth.rbac import Role, Permission, RBACManager, get_rbac_manager
from auth.user_models import (
    User, UserCreate, UserUpdate, LoginRequest, LoginResponse,
    RefreshTokenRequest, RefreshTokenResponse, ChangePasswordRequest,
    UserStats, SystemStats, MessageResponse, ErrorResponse
)
from cache.redis_cache import get_cache, get_cache_key_for_user
from middleware.rate_limiter import get_rate_limiter, get_rate_limit_headers
from monitoring.enterprise_monitoring import get_monitoring
from config.enterprise_settings import EnterpriseSettings

# Initialize components
settings = EnterpriseSettings()
security = HTTPBearer()
router = APIRouter(prefix="/api/v1/enterprise", tags=["enterprise"])


# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_manager: JWTManager = Depends(get_jwt_manager)
) -> Dict[str, Any]:
    """Get current authenticated user."""
    try:
        token = credentials.credentials
        payload = jwt_manager.decode_token(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Authorization dependency
def require_permission(permission: Permission):
    """Dependency to require specific permission."""
    def permission_checker(
        current_user: Dict[str, Any] = Depends(get_current_user),
        rbac_manager: RBACManager = Depends(get_rbac_manager)
    ) -> Dict[str, Any]:
        user_role = Role(current_user.get('role', 'guest'))
        
        if not rbac_manager.has_permission(user_role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission.value}' required"
            )
        
        return current_user
    
    return permission_checker


# Monitoring middleware
async def add_monitoring_headers(request: Request, response: Response):
    """Add monitoring headers to responses."""
    try:
        if hasattr(request.state, 'user_id') and hasattr(request.state, 'user_role'):
            headers = get_rate_limit_headers(
                request.state.user_id,
                request.state.user_role
            )
            
            for key, value in headers.items():
                response.headers[key] = value
    except Exception:
        pass  # Don't break the request if monitoring fails


# Authentication endpoints
@router.post("/auth/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    jwt_manager: JWTManager = Depends(get_jwt_manager)
):
    """User login endpoint."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # For demo purposes, we'll simulate user authentication
        # In production, this would integrate with your user database
        if login_data.email == "admin@plc-gpt.com" and login_data.password == "admin123":
            user_data = {
                "user_id": "user_001",
                "email": login_data.email,
                "username": "admin",
                "role": Role.ADMIN.value,
                "permissions": ["read", "write", "admin"]
            }
            
            # Generate tokens
            access_token = jwt_manager.create_access_token(user_data)
            refresh_token = jwt_manager.create_refresh_token(user_data)
            
            # Create user object
            user = User(
                user_id=user_data["user_id"],
                email=user_data["email"],
                username=user_data["username"],
                role=Role.ADMIN,
                permissions=user_data["permissions"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            # Record successful authentication
            monitoring.record_auth_attempt("success", "email_password")
            
            return LoginResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user=user
            )
        else:
            # Record failed authentication
            monitoring.record_auth_attempt("failure", "email_password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        monitoring.record_error("authentication_error", "auth_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )
    
    finally:
        # Record request metrics
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role.GUEST
        )


@router.post("/auth/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request,
    refresh_data: RefreshTokenRequest,
    jwt_manager: JWTManager = Depends(get_jwt_manager)
):
    """Refresh access token endpoint."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # Validate refresh token
        payload = jwt_manager.decode_token(refresh_data.refresh_token)
        
        # Generate new access token
        access_token = jwt_manager.create_access_token(payload)
        
        return RefreshTokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    except Exception as e:
        monitoring.record_error("token_refresh_error", "auth_api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role.GUEST
        )


@router.post("/auth/logout")
async def logout(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    jwt_manager: JWTManager = Depends(get_jwt_manager)
):
    """User logout endpoint."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # In a full implementation, you would:
        # 1. Invalidate the token (add to blacklist)
        # 2. Clear user session
        # 3. Update last logout time
        
        user_id = current_user.get('user_id')
        
        # Clear user cache
        cache = get_cache()
        cache.delete(get_cache_key_for_user(user_id, 'session'))
        
        return MessageResponse(message="Successfully logged out")
    
    except Exception as e:
        monitoring.record_error("logout_error", "auth_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# User management endpoints
@router.get("/users/me", response_model=User)
async def get_current_user_info(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user information."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # Convert user data to User model
        user = User(
            user_id=current_user["user_id"],
            email=current_user["email"],
            username=current_user.get("username"),
            role=Role(current_user["role"]),
            permissions=current_user.get("permissions", []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        return user
    
    except Exception as e:
        monitoring.record_error("user_info_error", "user_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


@router.get("/users/stats", response_model=UserStats)
async def get_user_stats(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get user statistics."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        user_id = current_user["user_id"]
        
        # Get user stats from cache or compute
        cache = get_cache()
        cache_key = get_cache_key_for_user(user_id, 'stats')
        
        cached_stats = cache.get(cache_key)
        if cached_stats:
            return UserStats(**cached_stats)
        
        # Compute stats (in production, this would query your database)
        stats = UserStats(
            user_id=user_id,
            total_logins=10,
            last_login=datetime.utcnow(),
            queries_executed=25,
            data_accessed=1024000,
            cache_hits=15,
            cache_misses=5,
            avg_session_duration=45.5
        )
        
        # Cache the stats
        cache.set(cache_key, stats.dict(), ttl=300)  # 5 minutes
        
        return stats
    
    except Exception as e:
        monitoring.record_error("user_stats_error", "user_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User statistics service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# Admin endpoints
@router.get("/admin/users", response_model=List[User])
async def list_users(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_READ))
):
    """List all users (admin only)."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # In production, this would query your user database
        users = [
            User(
                user_id="user_001",
                email="admin@plc-gpt.com",
                username="admin",
                role=Role.ADMIN,
                permissions=["read", "write", "admin"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            ),
            User(
                user_id="user_002",
                email="user@plc-gpt.com",
                username="user",
                role=Role.USER,
                permissions=["read"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        ]
        
        return users
    
    except Exception as e:
        monitoring.record_error("list_users_error", "admin_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User listing service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


@router.get("/admin/stats", response_model=SystemStats)
async def get_system_stats(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_READ))
):
    """Get system statistics (admin only)."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        # Get system stats from monitoring
        performance_metrics = monitoring.get_performance_metrics()
        
        stats = SystemStats(
            total_users=2,
            active_users=1,
            users_by_role={
                "admin": 1,
                "user": 1,
                "guest": 0
            },
            recent_logins=5,
            failed_logins=2,
            avg_session_duration=45.5
        )
        
        return stats
    
    except Exception as e:
        monitoring.record_error("system_stats_error", "admin_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="System statistics service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# Cache management endpoints
@router.get("/cache/stats")
async def get_cache_stats(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_READ))
):
    """Get cache statistics."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        cache = get_cache()
        stats = cache.get_stats()
        
        return stats
    
    except Exception as e:
        monitoring.record_error("cache_stats_error", "cache_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache statistics service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


@router.post("/cache/clear")
async def clear_cache(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_WRITE))
):
    """Clear cache (admin only)."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        cache = get_cache()
        success = cache.clear_all()
        
        if success:
            return MessageResponse(message="Cache cleared successfully")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear cache"
            )
    
    except Exception as e:
        monitoring.record_error("cache_clear_error", "cache_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cache clear service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# Rate limiting endpoints
@router.get("/rate-limit/status")
async def get_rate_limit_status(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current rate limit status for user."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        rate_limiter = get_rate_limiter()
        user_id = current_user["user_id"]
        user_role = Role(current_user["role"])
        
        status = rate_limiter.get_rate_limit_status(user_id, user_role)
        
        return status
    
    except Exception as e:
        monitoring.record_error("rate_limit_status_error", "rate_limit_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Rate limit status service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# Monitoring endpoints
@router.get("/monitoring/metrics")
async def get_metrics(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_READ))
):
    """Get Prometheus metrics."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        metrics = monitoring.get_metrics()
        
        # Return as plain text for Prometheus
        return Response(
            content=metrics,
            media_type="text/plain; version=0.0.4; charset=utf-8"
        )
    
    except Exception as e:
        monitoring.record_error("metrics_error", "monitoring_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Metrics service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


@router.get("/monitoring/health")
async def health_check(request: Request):
    """System health check."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        from monitoring.enterprise_monitoring import comprehensive_health_check
        health_data = comprehensive_health_check()
        
        return health_data
    
    except Exception as e:
        monitoring.record_error("health_check_error", "monitoring_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Health check service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role.GUEST
        )


@router.get("/monitoring/dashboard")
async def get_dashboard_data(
    request: Request,
    current_user: Dict[str, Any] = Depends(require_permission(Permission.ADMIN_READ))
):
    """Get dashboard data for monitoring UI."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        dashboard_data = monitoring.get_dashboard_data()
        
        return dashboard_data
    
    except Exception as e:
        monitoring.record_error("dashboard_error", "monitoring_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Dashboard service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# PLC-specific endpoints with enterprise features
@router.post("/plc/query")
async def execute_plc_query(
    request: Request,
    query_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_permission(Permission.QUERY_EXECUTE))
):
    """Execute PLC query with enterprise features."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        user_id = current_user["user_id"]
        user_role = Role(current_user["role"])
        
        # Check rate limits before processing
        from middleware.rate_limiter import check_rate_limit_before_expensive_operation
        if not check_rate_limit_before_expensive_operation(user_id, user_role):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded for expensive operations"
            )
        
        # Cache key for query
        cache = get_cache()
        cache_key = f"plc_query:{hash(str(query_data))}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            monitoring.record_cache_operation("hit", "success")
            return cached_result
        
        # Execute query (simulate processing)
        result = {
            "query_id": f"query_{int(time.time())}",
            "status": "success",
            "data": {
                "devices": 5,
                "variables": 25,
                "execution_time": 0.5
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache the result
        cache.set(cache_key, result, ttl=300, tags=["plc_query"])
        monitoring.record_cache_operation("set", "success")
        
        # Record data processing
        monitoring.record_data_processed("plc_query", 1024, user_role)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        monitoring.record_error("plc_query_error", "plc_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PLC query service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


@router.post("/plc/upload")
async def upload_plc_file(
    request: Request,
    file_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_permission(Permission.FILE_UPLOAD))
):
    """Upload PLC file with enterprise features."""
    monitoring = get_monitoring()
    start_time = time.time()
    
    try:
        user_id = current_user["user_id"]
        user_role = Role(current_user["role"])
        
        # Simulate file processing
        file_type = file_data.get("type", "l5x")
        file_size = file_data.get("size", 1024)
        
        # Record file upload
        monitoring.record_file_upload(file_type, user_role)
        monitoring.record_data_processed("file_upload", file_size, user_role)
        
        result = {
            "upload_id": f"upload_{int(time.time())}",
            "status": "success",
            "file_type": file_type,
            "file_size": file_size,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        return result
    
    except Exception as e:
        monitoring.record_error("file_upload_error", "plc_api")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="File upload service error"
        )
    
    finally:
        duration = time.time() - start_time
        monitoring.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=200,
            duration=duration,
            user_role=Role(current_user.get('role', 'guest'))
        )


# Export the router
enterprise_router = router 