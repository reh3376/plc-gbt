"""
Integration Module
=================

Modular external service integrations for the PLC-GPT system including:
- WolframAlpha Pro mathematical intelligence
- OpenAI API with fine-tuned models
- Multi-database services (Neo4j, PostgreSQL, Qdrant, Redis)
- GitHub API integrations
- Authentication and rate limiting utilities
- Service health monitoring and fallback patterns

This module eliminates integration code duplication across the codebase.
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import aiohttp
import openai
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """Types of external services"""
    WOLFRAM_ALPHA_PRO = "wolfram_alpha_pro"
    OPENAI = "openai"
    GITHUB_API = "github_api"
    NEO4J = "neo4j"
    POSTGRESQL = "postgresql"
    QDRANT = "qdrant"
    REDIS = "redis"

class ServiceStatus(Enum):
    """Service health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"

@dataclass
class ServiceConfig:
    """Configuration for external services"""
    service_type: ServiceType
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    rate_limit_per_minute: int = 60
    enable_caching: bool = True
    cache_ttl: int = 3600

@dataclass
class ServiceResponse:
    """Standardized service response"""
    service_type: ServiceType
    success: bool
    data: Any = None
    error: Optional[str] = None
    response_time: float = 0.0
    cached: bool = False
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class RateLimiter:
    """Rate limiting utility for API services"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.request_count = 0

    async def acquire(self) -> bool:
        """Acquire rate limit token"""
        now = time.time()

        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]

        if len(self.request_times) >= self.requests_per_minute:
            # Rate limit exceeded
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)

        self.request_times.append(now)
        self.request_count += 1
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics"""
        now = time.time()
        recent_requests = [t for t in self.request_times if now - t < 60]

        return {
            "total_requests": self.request_count,
            "requests_last_minute": len(recent_requests),
            "rate_limit": self.requests_per_minute,
            "utilization": len(recent_requests) / self.requests_per_minute
        }

class BaseServiceClient(ABC):
    """Base class for all service clients"""

    def __init__(self, config: ServiceConfig, redis_client: Optional[redis.Redis] = None):
        self.config = config
        self.redis_client = redis_client
        self.rate_limiter = RateLimiter(config.rate_limit_per_minute)
        self.session_stats = {
            "requests_sent": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "errors": 0,
            "avg_response_time": 0.0,
            "start_time": datetime.now()
        }

        logger.info(f"🔌 {config.service_type.value} client initialized")

    @abstractmethod
    async def health_check(self) -> ServiceStatus:
        """Check service health"""
        pass

    @abstractmethod
    async def make_request(self, request_data: Dict[str, Any]) -> ServiceResponse:
        """Make service request"""
        pass

    async def _get_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        cache_data = json.dumps(request_data, sort_keys=True, default=str)
        return f"{self.config.service_type.value}:{hashlib.md5(cache_data.encode()).hexdigest()}"

    async def _get_cached_response(self, cache_key: str) -> Optional[ServiceResponse]:
        """Get cached response"""
        if not self.config.enable_caching or not self.redis_client:
            return None

        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                data = json.loads(cached_data)
                response = ServiceResponse(**data)
                response.cached = True
                self.session_stats["cache_hits"] += 1
                return response
        except Exception as e:
            logger.warning(f"Cache retrieval failed: {e}")

        self.session_stats["cache_misses"] += 1
        return None

    async def _cache_response(self, cache_key: str, response: ServiceResponse):
        """Cache response"""
        if not self.config.enable_caching or not self.redis_client or not response.success:
            return

        try:
            cache_data = asdict(response)
            cache_data["timestamp"] = response.timestamp.isoformat()
            await self.redis_client.setex(
                cache_key,
                self.config.cache_ttl,
                json.dumps(cache_data, default=str)
            )
        except Exception as e:
            logger.warning(f"Cache storage failed: {e}")

    async def _make_request_with_retry(self, request_func: Callable) -> ServiceResponse:
        """Make request with retry logic"""
        for attempt in range(self.config.max_retries + 1):
            try:
                await self.rate_limiter.acquire()
                start_time = time.time()

                response = await request_func()

                response_time = time.time() - start_time
                response.response_time = response_time

                # Update statistics
                self.session_stats["requests_sent"] += 1
                if response.success:
                    return response

            except Exception as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    self.session_stats["errors"] += 1
                    return ServiceResponse(
                        service_type=self.config.service_type,
                        success=False,
                        error=str(e)
                    )

        return ServiceResponse(
            service_type=self.config.service_type,
            success=False,
            error="Max retries exceeded"
        )

class WolframAlphaProClient(BaseServiceClient):
    """WolframAlpha Pro API client with caching and rate limiting"""

    def __init__(self, api_key: str, redis_client: Optional[redis.Redis] = None):
        config = ServiceConfig(
            service_type=ServiceType.WOLFRAM_ALPHA_PRO,
            api_key=api_key,
            base_url="https://api.wolframalpha.com/v2/query",
            rate_limit_per_minute=100,
            cache_ttl=7200  # 2 hours for mathematical queries
        )
        super().__init__(config, redis_client)

    async def health_check(self) -> ServiceStatus:
        """Check WolframAlpha Pro service health"""
        try:
            test_query = "1+1"
            response = await self.query(test_query)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except Exception:
            return ServiceStatus.UNAVAILABLE

    async def query(self, query: str, query_type: str = "mathematical") -> ServiceResponse:
        """Execute WolframAlpha Pro query"""
        request_data = {"query": query, "query_type": query_type}
        cache_key = await self._get_cache_key(request_data)

        # Check cache first
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            return cached_response

        async def make_wolfram_request():
            params = {
                "input": query,
                "appid": self.config.api_key,
                "format": "plaintext,image",
                "output": "json",
                "includepodid": "Result,Solution"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.config.base_url,
                    params=params,
                    timeout=self.config.timeout
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ServiceResponse(
                            service_type=self.config.service_type,
                            success=True,
                            data=data
                        )
                    else:
                        return ServiceResponse(
                            service_type=self.config.service_type,
                            success=False,
                            error=f"HTTP {response.status}"
                        )

        response = await self._make_request_with_retry(make_wolfram_request)
        await self._cache_response(cache_key, response)
        return response

    async def make_request(self, request_data: Dict[str, Any]) -> ServiceResponse:
        """Make WolframAlpha Pro request"""
        return await self.query(request_data.get("query", ""), request_data.get("query_type", "mathematical"))

class OpenAIClient(BaseServiceClient):
    """OpenAI API client with fine-tuned model support"""

    def __init__(self, api_key: str, fine_tuned_model: Optional[str] = None, redis_client: Optional[redis.Redis] = None):
        config = ServiceConfig(
            service_type=ServiceType.OPENAI,
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            rate_limit_per_minute=500,
            cache_ttl=1800  # 30 minutes for AI responses
        )
        super().__init__(config, redis_client)
        self.fine_tuned_model = fine_tuned_model or "gpt-4"
        self.openai_client = openai.AsyncOpenAI(api_key=api_key)

    async def health_check(self) -> ServiceStatus:
        """Check OpenAI service health"""
        try:
            response = await self.chat_completion([{"role": "user", "content": "Test"}], max_tokens=1)
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except Exception:
            return ServiceStatus.UNAVAILABLE

    async def chat_completion(self, messages: List[Dict], **kwargs) -> ServiceResponse:
        """Create chat completion"""
        request_data = {
            "messages": messages,
            "model": self.fine_tuned_model,
            **kwargs
        }
        cache_key = await self._get_cache_key(request_data)

        # Check cache for non-streaming requests
        if not kwargs.get("stream", False):
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                return cached_response

        async def make_openai_request():
            try:
                response = await self.openai_client.chat.completions.create(**request_data)
                return ServiceResponse(
                    service_type=self.config.service_type,
                    success=True,
                    data=response.model_dump()
                )
            except Exception as e:
                return ServiceResponse(
                    service_type=self.config.service_type,
                    success=False,
                    error=str(e)
                )

        response = await self._make_request_with_retry(make_openai_request)

        # Cache non-streaming responses
        if not kwargs.get("stream", False):
            await self._cache_response(cache_key, response)

        return response

    async def make_request(self, request_data: Dict[str, Any]) -> ServiceResponse:
        """Make OpenAI request"""
        return await self.chat_completion(request_data.get("messages", []), **request_data.get("kwargs", {}))

class GitHubAPIClient(BaseServiceClient):
    """GitHub API client for repository operations"""

    def __init__(self, token: Optional[str] = None, redis_client: Optional[redis.Redis] = None):
        config = ServiceConfig(
            service_type=ServiceType.GITHUB_API,
            api_key=token,
            base_url="https://api.github.com",
            rate_limit_per_minute=5000,  # Higher limit for GitHub API
            cache_ttl=1800  # 30 minutes for GitHub data
        )
        super().__init__(config, redis_client)
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if token:
            self.headers["Authorization"] = f"token {token}"

    async def health_check(self) -> ServiceStatus:
        """Check GitHub API health"""
        try:
            response = await self.get_user()
            return ServiceStatus.HEALTHY if response.success else ServiceStatus.DEGRADED
        except Exception:
            return ServiceStatus.UNAVAILABLE

    async def get_user(self, username: Optional[str] = None) -> ServiceResponse:
        """Get user information"""
        endpoint = "/user" if username is None else f"/users/{username}"
        return await self._make_github_request("GET", endpoint)

    async def get_repository(self, owner: str, repo: str) -> ServiceResponse:
        """Get repository information"""
        return await self._make_github_request("GET", f"/repos/{owner}/{repo}")

    async def _make_github_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> ServiceResponse:
        """Make GitHub API request"""
        request_data = {"method": method, "endpoint": endpoint, "data": data}
        cache_key = await self._get_cache_key(request_data)

        # Check cache for GET requests
        if method == "GET":
            cached_response = await self._get_cached_response(cache_key)
            if cached_response:
                return cached_response

        async def make_request():
            url = f"{self.config.base_url}{endpoint}"
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method,
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.config.timeout
                ) as response:
                    if response.status in [200, 201]:
                        result_data = await response.json()
                        return ServiceResponse(
                            service_type=self.config.service_type,
                            success=True,
                            data=result_data
                        )
                    else:
                        error_data = await response.text()
                        return ServiceResponse(
                            service_type=self.config.service_type,
                            success=False,
                            error=f"HTTP {response.status}: {error_data}"
                        )

        response = await self._make_request_with_retry(make_request)

        # Cache GET requests
        if method == "GET":
            await self._cache_response(cache_key, response)

        return response

    async def make_request(self, request_data: Dict[str, Any]) -> ServiceResponse:
        """Make GitHub API request"""
        return await self._make_github_request(
            request_data.get("method", "GET"),
            request_data.get("endpoint", "/user"),
            request_data.get("data")
        )

class ServiceManager:
    """Centralized service management and health monitoring"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.services: Dict[ServiceType, BaseServiceClient] = {}
        self.health_status: Dict[ServiceType, ServiceStatus] = {}
        self.last_health_check = {}

        logger.info("🔧 Service Manager initialized")

    def register_service(self, client: BaseServiceClient):
        """Register a service client"""
        self.services[client.config.service_type] = client
        self.health_status[client.config.service_type] = ServiceStatus.UNKNOWN
        logger.info(f"📝 Registered {client.config.service_type.value} service")

    async def get_service(self, service_type: ServiceType) -> Optional[BaseServiceClient]:
        """Get service client"""
        return self.services.get(service_type)

    async def health_check_all(self) -> Dict[ServiceType, ServiceStatus]:
        """Perform health check on all services"""
        logger.info("🔍 Performing health check on all services...")

        for service_type, client in self.services.items():
            try:
                status = await client.health_check()
                self.health_status[service_type] = status
                self.last_health_check[service_type] = datetime.now()
                logger.info(f"  {service_type.value}: {status.value}")
            except Exception as e:
                self.health_status[service_type] = ServiceStatus.UNAVAILABLE
                logger.error(f"  {service_type.value}: UNAVAILABLE ({e})")

        return self.health_status.copy()

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        stats = {
            "total_services": len(self.services),
            "healthy_services": sum(1 for status in self.health_status.values() if status == ServiceStatus.HEALTHY),
            "service_details": {}
        }

        for service_type, client in self.services.items():
            service_stats = client.session_stats.copy()
            service_stats["health_status"] = self.health_status.get(service_type, ServiceStatus.UNKNOWN).value
            service_stats["rate_limit_stats"] = client.rate_limiter.get_stats()
            stats["service_details"][service_type.value] = service_stats

        return stats

# Integration utilities and factory functions

async def create_wolfram_client(api_key: str, redis_client: Optional[redis.Redis] = None) -> WolframAlphaProClient:
    """Factory function for WolframAlpha Pro client"""
    client = WolframAlphaProClient(api_key, redis_client)
    logger.info("🧮 WolframAlpha Pro client created")
    return client

async def create_openai_client(api_key: str, fine_tuned_model: Optional[str] = None,
                             redis_client: Optional[redis.Redis] = None) -> OpenAIClient:
    """Factory function for OpenAI client"""
    client = OpenAIClient(api_key, fine_tuned_model, redis_client)
    logger.info(f"🤖 OpenAI client created (model: {fine_tuned_model or 'gpt-4'})")
    return client

async def create_github_client(token: Optional[str] = None, redis_client: Optional[redis.Redis] = None) -> GitHubAPIClient:
    """Factory function for GitHub API client"""
    client = GitHubAPIClient(token, redis_client)
    logger.info("🐙 GitHub API client created")
    return client

async def create_service_manager_with_defaults(
    wolfram_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    fine_tuned_model: Optional[str] = None,
    github_token: Optional[str] = None,
    redis_url: str = "redis://localhost:6379"
) -> ServiceManager:
    """Create service manager with default services"""

    # Initialize Redis client
    redis_client = None
    try:
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
        logger.info("✅ Redis client connected")
    except Exception as e:
        logger.warning(f"Redis connection failed: {e}. Caching disabled.")

    # Create service manager
    manager = ServiceManager(redis_client)

    # Register services based on available credentials
    if wolfram_api_key:
        wolfram_client = await create_wolfram_client(wolfram_api_key, redis_client)
        manager.register_service(wolfram_client)

    if openai_api_key:
        openai_client = await create_openai_client(openai_api_key, fine_tuned_model, redis_client)
        manager.register_service(openai_client)

    if github_token:
        github_client = await create_github_client(github_token, redis_client)
        manager.register_service(github_client)

    # Perform initial health check
    await manager.health_check_all()

    logger.info(f"🚀 Service manager created with {len(manager.services)} services")
    return manager

# Context manager for service lifecycle

class ServiceContext:
    """Context manager for service lifecycle management"""

    def __init__(self, service_manager: ServiceManager):
        self.service_manager = service_manager

    async def __aenter__(self):
        await self.service_manager.health_check_all()
        return self.service_manager

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Cleanup Redis connections
        if self.service_manager.redis_client:
            await self.service_manager.redis_client.close()
        logger.info("🧹 Service context cleanup completed")

# Export main components
__all__ = [
    'ServiceType',
    'ServiceStatus',
    'ServiceConfig',
    'ServiceResponse',
    'BaseServiceClient',
    'WolframAlphaProClient',
    'OpenAIClient',
    'GitHubAPIClient',
    'ServiceManager',
    'RateLimiter',
    'create_wolfram_client',
    'create_openai_client',
    'create_github_client',
    'create_service_manager_with_defaults',
    'ServiceContext'
]
