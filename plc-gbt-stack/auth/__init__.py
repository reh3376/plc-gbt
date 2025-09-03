#!/usr/bin/env python3
"""
Authentication Module for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features

This module provides enterprise-grade authentication features including:
- JWT token management
- Role-based access control (RBAC)
- User authentication and authorization
- Security middleware
"""

from .auth_middleware import get_current_active_user, get_current_user, require_permission
from .jwt_manager import JWTError, JWTManager, TokenData
from .rbac import Permission, RBACManager, Role
from .user_models import LoginRequest, LoginResponse, User, UserCreate, UserInDB

__all__ = [
    "JWTManager",
    "JWTError",
    "TokenData",
    "RBACManager",
    "Role",
    "Permission",
    "User",
    "UserCreate",
    "UserInDB",
    "LoginRequest",
    "LoginResponse",
    "get_current_user",
    "get_current_active_user",
    "require_permission",
]
