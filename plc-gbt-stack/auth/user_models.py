#!/usr/bin/env python3
"""
User Models for PLC-GPT Enterprise Authentication
Phase 3 Days 6-7: Enterprise Features
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
from .rbac import Role


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr = Field(..., description="User's email address")
    username: Optional[str] = Field(None, description="User's username")
    full_name: Optional[str] = Field(None, description="User's full name")
    is_active: bool = Field(True, description="Whether user is active")
    role: Role = Field(Role.USER, description="User's role")
    
    class Config:
        use_enum_values = True


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8, description="User's password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[Role] = None
    
    class Config:
        use_enum_values = True


class UserInDB(UserBase):
    """User model as stored in database."""
    user_id: str = Field(..., description="Unique user identifier")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(0, description="Number of logins")
    failed_login_attempts: int = Field(0, description="Failed login attempts")
    locked_until: Optional[datetime] = Field(None, description="Account locked until timestamp")
    
    class Config:
        use_enum_values = True


class User(UserBase):
    """User model for API responses."""
    user_id: str = Field(..., description="Unique user identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    login_count: int = Field(0, description="Number of logins")
    permissions: List[str] = Field(default_factory=list, description="User's permissions")
    
    class Config:
        use_enum_values = True


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    remember_me: bool = Field(False, description="Remember login session")


class LoginResponse(BaseModel):
    """Login response model."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    user: User = Field(..., description="User information")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """Refresh token response model."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
        
        return v


class ResetPasswordRequest(BaseModel):
    """Reset password request model."""
    email: EmailStr = Field(..., description="User's email address")


class ResetPasswordConfirm(BaseModel):
    """Reset password confirmation model."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    confirm_password: str = Field(..., description="Password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class UserSession(BaseModel):
    """User session model."""
    session_id: str = Field(..., description="Session identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Session creation time")
    last_accessed: datetime = Field(default_factory=datetime.utcnow, description="Last access time")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    is_active: bool = Field(True, description="Whether session is active")


class AuthenticationAttempt(BaseModel):
    """Authentication attempt model for audit logging."""
    email: str = Field(..., description="Attempted email")
    success: bool = Field(..., description="Whether attempt was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Attempt timestamp")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    failure_reason: Optional[str] = Field(None, description="Reason for failure")


class UserActivity(BaseModel):
    """User activity model for audit logging."""
    user_id: str = Field(..., description="User identifier")
    action: str = Field(..., description="Action performed")
    resource: Optional[str] = Field(None, description="Resource accessed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Activity timestamp")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")


class PermissionCheck(BaseModel):
    """Permission check model for audit logging."""
    user_id: str = Field(..., description="User identifier")
    permission: str = Field(..., description="Permission checked")
    resource: Optional[str] = Field(None, description="Resource accessed")
    granted: bool = Field(..., description="Whether permission was granted")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class UserStats(BaseModel):
    """User statistics model."""
    user_id: str = Field(..., description="User identifier")
    total_logins: int = Field(0, description="Total login count")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    queries_executed: int = Field(0, description="Number of queries executed")
    data_accessed: int = Field(0, description="Amount of data accessed")
    cache_hits: int = Field(0, description="Cache hits")
    cache_misses: int = Field(0, description="Cache misses")
    avg_session_duration: Optional[float] = Field(None, description="Average session duration in minutes")


class SystemStats(BaseModel):
    """System-wide user statistics."""
    total_users: int = Field(0, description="Total number of users")
    active_users: int = Field(0, description="Number of active users")
    users_by_role: Dict[str, int] = Field(default_factory=dict, description="User count by role")
    recent_logins: int = Field(0, description="Recent logins (last 24h)")
    failed_logins: int = Field(0, description="Failed logins (last 24h)")
    avg_session_duration: Optional[float] = Field(None, description="Average session duration")


class SecurityAlert(BaseModel):
    """Security alert model."""
    alert_id: str = Field(..., description="Alert identifier")
    alert_type: str = Field(..., description="Type of security alert")
    severity: str = Field(..., description="Alert severity level")
    user_id: Optional[str] = Field(None, description="Related user identifier")
    description: str = Field(..., description="Alert description")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Alert timestamp")
    resolved: bool = Field(False, description="Whether alert has been resolved")
    resolved_by: Optional[str] = Field(None, description="Who resolved the alert")
    resolved_at: Optional[datetime] = Field(None, description="When alert was resolved")


class APIKey(BaseModel):
    """API key model for programmatic access."""
    key_id: str = Field(..., description="API key identifier")
    name: str = Field(..., description="API key name")
    user_id: str = Field(..., description="Owner user identifier")
    key_hash: str = Field(..., description="Hashed API key")
    permissions: List[str] = Field(default_factory=list, description="API key permissions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")
    last_used: Optional[datetime] = Field(None, description="Last usage timestamp")
    is_active: bool = Field(True, description="Whether API key is active")
    usage_count: int = Field(0, description="Number of times used")


class CreateAPIKeyRequest(BaseModel):
    """Create API key request model."""
    name: str = Field(..., description="API key name")
    permissions: List[str] = Field(default_factory=list, description="API key permissions")
    expires_in_days: Optional[int] = Field(None, description="Expiration in days")


class CreateAPIKeyResponse(BaseModel):
    """Create API key response model."""
    key_id: str = Field(..., description="API key identifier")
    api_key: str = Field(..., description="Generated API key (shown only once)")
    name: str = Field(..., description="API key name")
    permissions: List[str] = Field(..., description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="Expiration timestamp")


# Common response models
class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    success: bool = Field(True, description="Whether operation was successful")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    success: bool = Field(False, description="Always false for errors") 