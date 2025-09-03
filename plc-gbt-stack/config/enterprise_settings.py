#!/usr/bin/env python3
"""
Enterprise Configuration for PLC-GPT
Phase 3 Days 6-7: Enterprise Features
"""

from datetime import timedelta
from typing import Any, Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings


class EnterpriseSettings(BaseSettings):
    """
    Enterprise configuration settings for PLC-GPT.

    This class manages all enterprise-grade feature configurations including:
    - JWT Authentication
    - Redis Caching
    - Rate Limiting
    - Role-Based Access Control
    - Enhanced Monitoring
    - Security Configuration
    """

    model_config = {
        "extra": "allow",
        "env_prefix": "",
        "case_sensitive": False,
        "env_file": ".env",
        "env_file_encoding": "utf-8"
    }

    # ========================================
    # JWT Authentication Configuration
    # ========================================
    jwt_secret: str = Field(
        default="your-super-secure-jwt-secret-key-here-32chars-minimum",
        description="JWT secret key for token signing"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT algorithm for token encryption"
    )
    jwt_expiration_hours: int = Field(
        default=24,
        description="JWT token expiration time in hours"
    )
    jwt_refresh_expiration_days: int = Field(
        default=7,
        description="JWT refresh token expiration in days"
    )

    # ========================================
    # Redis Configuration
    # ========================================
    redis_host: str = Field(
        default="localhost",
        description="Redis server hostname"
    )
    redis_port: int = Field(
        default=6379,
        description="Redis server port"
    )
    redis_password: str = Field(
        default="",
        description="Redis server password"
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number"
    )
    redis_max_connections: int = Field(
        default=100,
        description="Maximum Redis connections"
    )
    redis_socket_timeout: int = Field(
        default=5,
        description="Redis socket timeout in seconds"
    )

    # ========================================
    # Rate Limiting Configuration
    # ========================================
    rate_limit_enabled: bool = Field(
        default=True,
        description="Enable rate limiting"
    )
    rate_limit_requests: int = Field(
        default=100,
        description="Number of requests per time window"
    )
    rate_limit_window: int = Field(
        default=60,
        description="Time window in seconds"
    )
    rate_limit_auth_requests: int = Field(
        default=5,
        description="Auth requests per time window"
    )
    rate_limit_auth_window: int = Field(
        default=300,
        description="Auth time window in seconds"
    )

    # ========================================
    # Role-Based Access Control (RBAC)
    # ========================================
    rbac_enabled: bool = Field(
        default=True,
        description="Enable RBAC"
    )
    default_user_role: str = Field(
        default="user",
        description="Default user role"
    )
    admin_users: List[str] = Field(
        default=["admin@plc-gpt.com"],
        description="List of admin user emails"
    )
    developer_users: List[str] = Field(
        default=["dev@plc-gpt.com"],
        description="List of developer user emails"
    )

    # ========================================
    # Cache Configuration
    # ========================================
    cache_default_ttl: int = Field(
        default=3600,
        description="Default cache TTL in seconds"
    )
    cache_query_ttl: int = Field(
        default=1800,
        description="Query cache TTL in seconds"
    )
    cache_user_ttl: int = Field(
        default=300,
        description="User cache TTL in seconds"
    )
    cache_invalidation_enabled: bool = Field(
        default=True,
        description="Enable cache invalidation"
    )

    # ========================================
    # Enhanced Monitoring
    # ========================================
    metrics_enabled: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    metrics_auth_tracking: bool = Field(
        default=True,
        description="Track authentication metrics"
    )
    metrics_cache_tracking: bool = Field(
        default=True,
        description="Track cache metrics"
    )
    metrics_export_interval: int = Field(
        default=30,
        description="Metrics export interval in seconds"
    )

    # ========================================
    # Security Configuration
    # ========================================
    security_audit_enabled: bool = Field(
        default=True,
        description="Enable security audit logging"
    )
    security_failed_login_limit: int = Field(
        default=5,
        description="Failed login attempts limit"
    )
    security_lockout_duration: int = Field(
        default=900,
        description="Account lockout duration in seconds"
    )
    security_session_timeout: int = Field(
        default=28800,
        description="Session timeout in seconds"
    )

    # ========================================
    # Performance Configuration
    # ========================================
    performance_cache_size_mb: int = Field(
        default=512,
        description="Cache size in MB"
    )
    performance_query_timeout: int = Field(
        default=30,
        description="Query timeout in seconds"
    )
    performance_connection_pool_size: int = Field(
        default=20,
        description="Database connection pool size"
    )
    performance_async_workers: int = Field(
        default=8,
        description="Number of async workers"
    )


    def get_redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def get_jwt_expiration(self) -> timedelta:
        """Get JWT token expiration timedelta."""
        return timedelta(hours=self.jwt_expiration_hours)

    def get_refresh_expiration(self) -> timedelta:
        """Get refresh token expiration timedelta."""
        return timedelta(days=self.jwt_refresh_expiration_days)

    def get_rate_limit_string(self) -> str:
        """Get rate limit string for slowapi."""
        return f"{self.rate_limit_requests}/{self.rate_limit_window}seconds"

    def get_auth_rate_limit_string(self) -> str:
        """Get auth rate limit string for slowapi."""
        return f"{self.rate_limit_auth_requests}/{self.rate_limit_auth_window}seconds"

    def is_admin_user(self, email: str) -> bool:
        """Check if email is an admin user."""
        return email.lower() in [user.lower() for user in self.admin_users]

    def is_developer_user(self, email: str) -> bool:
        """Check if email is a developer user."""
        return email.lower() in [user.lower() for user in self.developer_users]

    def get_user_role(self, email: str) -> str:
        """Get user role based on email."""
        if self.is_admin_user(email):
            return "admin"
        elif self.is_developer_user(email):
            return "developer"
        else:
            return self.default_user_role

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return self.dict()


# Global settings instance
settings = EnterpriseSettings()

# Environment variable setup guide
ENVIRONMENT_VARIABLES = {
    "JWT_SECRET": settings.jwt_secret,
    "JWT_ALGORITHM": settings.jwt_algorithm,
    "JWT_EXPIRATION_HOURS": str(settings.jwt_expiration_hours),
    "JWT_REFRESH_EXPIRATION_DAYS": str(settings.jwt_refresh_expiration_days),
    "REDIS_HOST": settings.redis_host,
    "REDIS_PORT": str(settings.redis_port),
    "REDIS_PASSWORD": settings.redis_password,
    "REDIS_DB": str(settings.redis_db),
    "REDIS_MAX_CONNECTIONS": str(settings.redis_max_connections),
    "REDIS_SOCKET_TIMEOUT": str(settings.redis_socket_timeout),
    "RATE_LIMIT_ENABLED": str(settings.rate_limit_enabled).lower(),
    "RATE_LIMIT_REQUESTS": str(settings.rate_limit_requests),
    "RATE_LIMIT_WINDOW": str(settings.rate_limit_window),
    "RATE_LIMIT_AUTH_REQUESTS": str(settings.rate_limit_auth_requests),
    "RATE_LIMIT_AUTH_WINDOW": str(settings.rate_limit_auth_window),
    "RBAC_ENABLED": str(settings.rbac_enabled).lower(),
    "DEFAULT_USER_ROLE": settings.default_user_role,
    "ADMIN_USERS": ",".join(settings.admin_users),
    "DEVELOPER_USERS": ",".join(settings.developer_users),
    "CACHE_DEFAULT_TTL": str(settings.cache_default_ttl),
    "CACHE_QUERY_TTL": str(settings.cache_query_ttl),
    "CACHE_USER_TTL": str(settings.cache_user_ttl),
    "CACHE_INVALIDATION_ENABLED": str(settings.cache_invalidation_enabled).lower(),
    "METRICS_ENABLED": str(settings.metrics_enabled).lower(),
    "METRICS_AUTH_TRACKING": str(settings.metrics_auth_tracking).lower(),
    "METRICS_CACHE_TRACKING": str(settings.metrics_cache_tracking).lower(),
    "METRICS_EXPORT_INTERVAL": str(settings.metrics_export_interval),
    "SECURITY_AUDIT_ENABLED": str(settings.security_audit_enabled).lower(),
    "SECURITY_FAILED_LOGIN_LIMIT": str(settings.security_failed_login_limit),
    "SECURITY_LOCKOUT_DURATION": str(settings.security_lockout_duration),
    "SECURITY_SESSION_TIMEOUT": str(settings.security_session_timeout),
    "PERFORMANCE_CACHE_SIZE_MB": str(settings.performance_cache_size_mb),
    "PERFORMANCE_QUERY_TIMEOUT": str(settings.performance_query_timeout),
    "PERFORMANCE_CONNECTION_POOL_SIZE": str(settings.performance_connection_pool_size),
    "PERFORMANCE_ASYNC_WORKERS": str(settings.performance_async_workers),
}


def print_environment_setup():
    """Print environment setup guide."""
    print("🔧 Enterprise Environment Setup Guide")
    print("=" * 50)
    print("\nAdd these environment variables to your docker-compose.yml or .env file:")
    print()

    for key, value in ENVIRONMENT_VARIABLES.items():
        print(f"export {key}={value}")

    print("\nOr add to docker-compose.yml environment section:")
    print("environment:")
    for key, value in ENVIRONMENT_VARIABLES.items():
        print(f"  - {key}=${{{key}}}")


if __name__ == "__main__":
    print_environment_setup()
