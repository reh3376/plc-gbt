#!/usr/bin/env python3
"""
Rate Limiting Middleware for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

import redis
from auth.rbac import Role
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from config.enterprise_settings import EnterpriseSettings


class EnterpriseRateLimiter:
    """
    Advanced rate limiting system with Redis backend.
    Supports different limits for different user roles and endpoints.
    """

    def __init__(self, settings: EnterpriseSettings):
        self.settings = settings
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=True
        )

        # Rate limit configurations by role
        self.rate_limits = {
            Role.ADMIN: {
                'requests_per_minute': 1000,
                'requests_per_hour': 10000,
                'requests_per_day': 100000,
                'burst_limit': 50,
                'concurrent_requests': 100
            },
            Role.DEVELOPER: {
                'requests_per_minute': 500,
                'requests_per_hour': 5000,
                'requests_per_day': 50000,
                'burst_limit': 25,
                'concurrent_requests': 50
            },
            Role.USER: {
                'requests_per_minute': 100,
                'requests_per_hour': 1000,
                'requests_per_day': 10000,
                'burst_limit': 10,
                'concurrent_requests': 10
            },
            Role.AUDITOR: {
                'requests_per_minute': 200,
                'requests_per_hour': 2000,
                'requests_per_day': 20000,
                'burst_limit': 15,
                'concurrent_requests': 20
            },
            Role.GUEST: {
                'requests_per_minute': 10,
                'requests_per_hour': 100,
                'requests_per_day': 1000,
                'burst_limit': 5,
                'concurrent_requests': 5
            }
        }

        # Endpoint-specific limits
        self.endpoint_limits = {
            '/api/v1/query': {
                'requests_per_minute': 50,
                'cpu_intensive': True
            },
            '/api/v1/upload': {
                'requests_per_minute': 10,
                'bandwidth_intensive': True
            },
            '/api/v1/export': {
                'requests_per_minute': 5,
                'cpu_intensive': True,
                'bandwidth_intensive': True
            }
        }

    def _get_user_key(self, user_id: str, window: str) -> str:
        """Generate Redis key for user rate limiting."""
        return f"rate_limit:user:{user_id}:{window}"

    def _get_ip_key(self, ip_address: str, window: str) -> str:
        """Generate Redis key for IP rate limiting."""
        return f"rate_limit:ip:{ip_address}:{window}"

    def _get_endpoint_key(self, endpoint: str, user_id: str, window: str) -> str:
        """Generate Redis key for endpoint-specific rate limiting."""
        return f"rate_limit:endpoint:{endpoint}:{user_id}:{window}"

    def _get_concurrent_key(self, user_id: str) -> str:
        """Generate Redis key for concurrent request tracking."""
        return f"concurrent:user:{user_id}"

    def _sliding_window_counter(self, key: str, window_size: int, limit: int) -> Tuple[bool, int, int]:
        """
        Implement sliding window counter for rate limiting.
        Returns (allowed, current_count, reset_time)
        """
        now = int(time.time())
        window_start = now - window_size

        # Use Redis pipeline for atomic operations
        pipe = self.redis_client.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)

        # Count current requests
        pipe.zcard(key)

        # Add current request
        pipe.zadd(key, {str(now): now})

        # Set expiration
        pipe.expire(key, window_size + 1)

        results = pipe.execute()
        current_count = results[1] + 1  # +1 for the current request

        # Calculate reset time
        reset_time = now + window_size

        return current_count <= limit, current_count, reset_time

    def _check_concurrent_limit(self, user_id: str, role: Role) -> bool:
        """Check concurrent request limit."""
        concurrent_key = self._get_concurrent_key(user_id)
        current_concurrent = self.redis_client.get(concurrent_key)

        if current_concurrent is None:
            current_concurrent = 0
        else:
            current_concurrent = int(current_concurrent)

        max_concurrent = self.rate_limits[role]['concurrent_requests']
        return current_concurrent < max_concurrent

    def _increment_concurrent(self, user_id: str) -> None:
        """Increment concurrent request counter."""
        concurrent_key = self._get_concurrent_key(user_id)
        pipe = self.redis_client.pipeline()
        pipe.incr(concurrent_key)
        pipe.expire(concurrent_key, 300)  # 5 minute expiration
        pipe.execute()

    def _decrement_concurrent(self, user_id: str) -> None:
        """Decrement concurrent request counter."""
        concurrent_key = self._get_concurrent_key(user_id)
        current = self.redis_client.get(concurrent_key)
        if current and int(current) > 0:
            self.redis_client.decr(concurrent_key)

    def _get_client_identifier(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from request state (set by auth middleware)
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        ip_address = get_remote_address(request)
        return f"ip:{ip_address}"

    def _apply_rate_limit(self, request: Request, user_id: Optional[str], role: Role) -> Optional[JSONResponse]:
        """Apply rate limiting logic."""
        try:
            # Get client identifier
            client_id = self._get_client_identifier(request)

            # Get endpoint path
            endpoint = request.url.path

            # Check concurrent request limit
            if user_id and not self._check_concurrent_limit(user_id, role):
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many concurrent requests",
                        "retry_after": 60
                    }
                )

            # Get rate limits for user role
            limits = self.rate_limits[role]

            # Check different time windows
            windows = [
                ('minute', 60, limits['requests_per_minute']),
                ('hour', 3600, limits['requests_per_hour']),
                ('day', 86400, limits['requests_per_day'])
            ]

            for window_name, window_size, limit in windows:
                if user_id:
                    key = self._get_user_key(user_id, window_name)
                else:
                    ip_address = get_remote_address(request)
                    key = self._get_ip_key(ip_address, window_name)

                allowed, current_count, reset_time = self._sliding_window_counter(
                    key, window_size, limit
                )

                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": f"Rate limit exceeded for {window_name}",
                            "limit": limit,
                            "current": current_count,
                            "reset_time": reset_time,
                            "retry_after": reset_time - int(time.time())
                        }
                    )

            # Check endpoint-specific limits
            if endpoint in self.endpoint_limits:
                endpoint_limit = self.endpoint_limits[endpoint]
                endpoint_key = self._get_endpoint_key(endpoint, user_id or client_id, 'minute')

                allowed, current_count, reset_time = self._sliding_window_counter(
                    endpoint_key, 60, endpoint_limit['requests_per_minute']
                )

                if not allowed:
                    return JSONResponse(
                        status_code=429,
                        content={
                            "error": f"Rate limit exceeded for endpoint {endpoint}",
                            "limit": endpoint_limit['requests_per_minute'],
                            "current": current_count,
                            "reset_time": reset_time,
                            "retry_after": reset_time - int(time.time())
                        }
                    )

            # Increment concurrent counter
            if user_id:
                self._increment_concurrent(user_id)

            return None  # No rate limit exceeded

        except Exception as e:
            # Log error but don't block request
            print(f"Rate limiting error: {e}")
            return None

    def _log_rate_limit_event(self, request: Request, user_id: Optional[str],
                            limit_type: str, current_count: int, limit: int) -> None:
        """Log rate limit events for monitoring."""
        event_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id,
            'ip_address': get_remote_address(request),
            'endpoint': request.url.path,
            'method': request.method,
            'limit_type': limit_type,
            'current_count': current_count,
            'limit': limit,
            'user_agent': request.headers.get('User-Agent', ''),
        }

        # Store in Redis for monitoring
        log_key = f"rate_limit_events:{datetime.utcnow().strftime('%Y%m%d')}"
        self.redis_client.lpush(log_key, json.dumps(event_data))
        self.redis_client.expire(log_key, 604800)  # Keep for 7 days

    async def __call__(self, request: Request, call_next):
        """Rate limiting middleware."""
        # Skip rate limiting for health checks
        if request.url.path in ['/health', '/metrics']:
            return await call_next(request)

        # Get user information from request state
        user_id = getattr(request.state, 'user_id', None)
        role = getattr(request.state, 'user_role', Role.GUEST)

        # Apply rate limiting
        rate_limit_response = self._apply_rate_limit(request, user_id, role)
        if rate_limit_response:
            return rate_limit_response

        # Process request
        try:
            response = await call_next(request)
            return response
        finally:
            # Decrement concurrent counter
            if user_id:
                self._decrement_concurrent(user_id)

    def get_rate_limit_status(self, user_id: str, role: Role) -> Dict[str, Any]:
        """Get current rate limit status for a user."""
        status = {
            'user_id': user_id,
            'role': role.value,
            'limits': self.rate_limits[role],
            'current_usage': {}
        }

        # Check current usage for each window
        windows = [
            ('minute', 60),
            ('hour', 3600),
            ('day', 86400)
        ]

        for window_name, window_size in windows:
            key = self._get_user_key(user_id, window_name)
            now = int(time.time())
            window_start = now - window_size

            # Count requests in current window
            current_count = self.redis_client.zcount(key, window_start, now)

            status['current_usage'][window_name] = {
                'count': current_count,
                'limit': self.rate_limits[role][f'requests_per_{window_name}'],
                'remaining': max(0, self.rate_limits[role][f'requests_per_{window_name}'] - current_count),
                'reset_time': now + window_size
            }

        # Check concurrent requests
        concurrent_key = self._get_concurrent_key(user_id)
        current_concurrent = self.redis_client.get(concurrent_key)
        status['concurrent'] = {
            'count': int(current_concurrent) if current_concurrent else 0,
            'limit': self.rate_limits[role]['concurrent_requests']
        }

        return status

    def reset_user_limits(self, user_id: str) -> None:
        """Reset rate limits for a specific user."""
        windows = ['minute', 'hour', 'day']

        for window in windows:
            key = self._get_user_key(user_id, window)
            self.redis_client.delete(key)

        # Reset concurrent counter
        concurrent_key = self._get_concurrent_key(user_id)
        self.redis_client.delete(concurrent_key)

    def get_rate_limit_stats(self) -> Dict[str, Any]:
        """Get system-wide rate limiting statistics."""
        stats = {
            'total_requests': 0,
            'blocked_requests': 0,
            'top_users': [],
            'top_endpoints': [],
            'rate_limit_events': []
        }

        # Get recent rate limit events
        today = datetime.utcnow().strftime('%Y%m%d')
        log_key = f"rate_limit_events:{today}"
        events = self.redis_client.lrange(log_key, 0, 100)

        for event_str in events:
            try:
                event = json.loads(event_str)
                stats['rate_limit_events'].append(event)
            except json.JSONDecodeError:
                continue

        return stats


# Global rate limiter instance
rate_limiter = None


def get_rate_limiter() -> EnterpriseRateLimiter:
    """Get the global rate limiter instance."""
    global rate_limiter
    if rate_limiter is None:
        settings = EnterpriseSettings()
        rate_limiter = EnterpriseRateLimiter(settings)
    return rate_limiter


def create_slowapi_limiter() -> Limiter:
    """Create slowapi limiter for basic rate limiting."""
    def get_identifier(request: Request) -> str:
        """Get client identifier for slowapi."""
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"
        return get_remote_address(request)

    limiter = Limiter(key_func=get_identifier)
    return limiter


# Rate limiting decorators
def rate_limit(
    requests_per_minute: int = 60,
    requests_per_hour: int = 1000,
    requests_per_day: int = 10000
):
    """
    Decorator for applying rate limits to specific endpoints.
    """
    def decorator(func):
        func._rate_limits = {
            'requests_per_minute': requests_per_minute,
            'requests_per_hour': requests_per_hour,
            'requests_per_day': requests_per_day
        }
        return func
    return decorator


def role_based_rate_limit(role_limits: Dict[Role, Dict[str, int]]):
    """
    Decorator for applying different rate limits based on user role.
    """
    def decorator(func):
        func._role_rate_limits = role_limits
        return func
    return decorator


# Utility functions
def get_rate_limit_headers(user_id: str, role: Role) -> Dict[str, str]:
    """Get rate limit headers for API responses."""
    limiter = get_rate_limiter()
    status = limiter.get_rate_limit_status(user_id, role)

    headers = {}

    # Add minute-based headers
    minute_usage = status['current_usage']['minute']
    headers['X-RateLimit-Limit'] = str(minute_usage['limit'])
    headers['X-RateLimit-Remaining'] = str(minute_usage['remaining'])
    headers['X-RateLimit-Reset'] = str(minute_usage['reset_time'])

    # Add concurrent request headers
    concurrent = status['concurrent']
    headers['X-RateLimit-Concurrent'] = str(concurrent['count'])
    headers['X-RateLimit-Concurrent-Limit'] = str(concurrent['limit'])

    return headers


def check_rate_limit_before_expensive_operation(user_id: str, role: Role) -> bool:
    """
    Check rate limits before performing expensive operations.
    Returns True if operation should proceed.
    """
    limiter = get_rate_limiter()
    status = limiter.get_rate_limit_status(user_id, role)

    # Check if user has enough remaining requests
    minute_remaining = status['current_usage']['minute']['remaining']
    hour_remaining = status['current_usage']['hour']['remaining']

    # Require at least 10% of minute limit remaining for expensive operations
    minute_threshold = status['limits']['requests_per_minute'] * 0.1

    return minute_remaining >= minute_threshold and hour_remaining > 0
