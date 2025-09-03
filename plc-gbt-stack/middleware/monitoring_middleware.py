#!/usr/bin/env python3
"""
Monitoring Middleware for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

import time
from typing import Any, Dict

from auth.rbac import Role
from fastapi import Request, Response
from monitoring.enterprise_monitoring import get_monitoring


class MonitoringMiddleware:
    """
    Monitoring middleware that tracks all requests and responses.
    """

    def __init__(self):
        self.monitoring = get_monitoring()

        # Paths to exclude from detailed monitoring
        self.exclude_paths = {
            '/health',
            '/metrics',
            '/favicon.ico'
        }

    async def __call__(self, request: Request, call_next):
        """Process the request with monitoring."""
        start_time = time.time()

        # Skip monitoring for excluded paths
        if self._should_exclude_path(request.url.path):
            return await call_next(request)

        # Extract request information
        request_info = self._extract_request_info(request)

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            duration = time.time() - start_time

            # Extract response information
            response_info = self._extract_response_info(response)

            # Record metrics
            self._record_request_metrics(request_info, response_info, duration)

            # Add monitoring headers
            self._add_monitoring_headers(request, response, duration)

            return response

        except Exception as e:
            # Record error
            duration = time.time() - start_time

            self.monitoring.record_error(
                error_type=type(e).__name__,
                component="request_processing"
            )

            # Record failed request
            self._record_request_metrics(
                request_info,
                {"status_code": 500, "error": str(e)},
                duration
            )

            raise

    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from monitoring."""
        return path in self.exclude_paths or path.startswith('/static/')

    def _extract_request_info(self, request: Request) -> Dict[str, Any]:
        """Extract relevant information from request."""
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "user_agent": request.headers.get("User-Agent", ""),
            "client_ip": self._get_client_ip(request),
            "user_id": getattr(request.state, 'user_id', None),
            "user_role": getattr(request.state, 'user_role', Role.GUEST),
            "timestamp": time.time()
        }

    def _extract_response_info(self, response: Response) -> Dict[str, Any]:
        """Extract relevant information from response."""
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "media_type": response.media_type
        }

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address."""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _record_request_metrics(self, request_info: Dict[str, Any],
                               response_info: Dict[str, Any], duration: float):
        """Record request metrics."""
        try:
            # Record basic request metrics
            self.monitoring.record_request(
                method=request_info["method"],
                endpoint=request_info["path"],
                status_code=response_info["status_code"],
                duration=duration,
                user_role=request_info["user_role"]
            )

            # Record detailed metrics based on status code
            if response_info["status_code"] >= 400:
                self.monitoring.record_error(
                    error_type=f"http_{response_info['status_code']}",
                    component="api"
                )

            # Record endpoint-specific metrics
            self._record_endpoint_metrics(request_info, response_info, duration)

        except Exception as e:
            # Don't let monitoring errors break the request
            print(f"Monitoring error: {e}")

    def _record_endpoint_metrics(self, request_info: Dict[str, Any],
                                response_info: Dict[str, Any], duration: float):
        """Record endpoint-specific metrics."""
        path = request_info["path"]
        user_role = request_info["user_role"]

        # File upload metrics
        if path.endswith('/upload'):
            self.monitoring.record_file_upload("l5x", user_role)

        # Query metrics
        if path.endswith('/query'):
            self.monitoring.record_database_query("plc", "query", duration)

        # Cache metrics
        if path.endswith('/cache'):
            self.monitoring.record_cache_operation("request", "success")

    def _add_monitoring_headers(self, request: Request, response: Response,
                               duration: float):
        """Add monitoring headers to response."""
        try:
            # Add performance headers
            response.headers["X-Response-Time"] = f"{duration:.3f}s"
            response.headers["X-Request-ID"] = self._generate_request_id(request)

            # Add rate limiting headers if available
            if hasattr(request.state, 'user_id') and hasattr(request.state, 'user_role'):
                from middleware.rate_limiter import get_rate_limit_headers

                rate_limit_headers = get_rate_limit_headers(
                    request.state.user_id,
                    request.state.user_role
                )

                for key, value in rate_limit_headers.items():
                    response.headers[key] = value

        except Exception as e:
            # Don't let header errors break the response
            print(f"Header error: {e}")

    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID."""
        timestamp = str(int(time.time() * 1000))
        path_hash = str(hash(request.url.path))[-6:]
        return f"req_{timestamp}_{path_hash}"

    def get_request_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get request statistics for the specified time window."""
        try:
            # This would typically query stored metrics
            # For now, return current performance metrics
            return self.monitoring.get_performance_metrics()

        except Exception as e:
            return {"error": f"Failed to get request stats: {e}"}

    def get_error_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get error statistics for the specified time window."""
        try:
            # This would typically query stored error metrics
            performance_metrics = self.monitoring.get_performance_metrics()

            error_rate = 0
            if performance_metrics['request_count'] > 0:
                error_rate = (performance_metrics['error_count'] /
                             performance_metrics['request_count']) * 100

            return {
                "total_errors": performance_metrics['error_count'],
                "error_rate": f"{error_rate:.2f}%",
                "time_window": time_window
            }

        except Exception as e:
            return {"error": f"Failed to get error stats: {e}"}

    def get_performance_stats(self, time_window: int = 3600) -> Dict[str, Any]:
        """Get performance statistics for the specified time window."""
        try:
            performance_metrics = self.monitoring.get_performance_metrics()

            return {
                "avg_response_time": performance_metrics['avg_response_time'],
                "total_requests": performance_metrics['request_count'],
                "cache_hit_rate": f"{performance_metrics['cache_hit_rate']:.2f}%",
                "time_window": time_window
            }

        except Exception as e:
            return {"error": f"Failed to get performance stats: {e}"}
