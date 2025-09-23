"""Redis adapter for memory system."""

import json
from typing import Any

from plc_orchestrator.memory.coordinator import MemoryRequest, MemoryResponse
from plc_orchestrator.utils.logging import get_logger


class RedisAdapter:
    """Redis adapter for fast cache operations."""

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize Redis adapter.

        Args:
            config: Redis configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize Redis client."""
        try:
            import redis.asyncio as redis

            url = self.config.get("url", "redis://localhost:6379")
            self.client = redis.from_url(url, decode_responses=True)
            self.logger.info(f"Redis client initialized: {url}")

        except ImportError:
            self.logger.error("Redis library not installed. Install with: pip install redis")
            raise
        except Exception as e:
            self.logger.error(f"Failed to initialize Redis client: {e}")
            raise

    async def query(self, request: MemoryRequest) -> MemoryResponse:
        """
        Query Redis for cached data.

        Args:
            request: Memory request

        Returns:
            Memory response
        """
        if not self.client:
            return MemoryResponse(
                success=False,
                data=None,
                source="redis",
                metadata={"error": "Redis client not initialized"},
            )

        try:
            # Build cache key
            cache_key = self._build_cache_key(request)

            # Get from cache
            cached_data = await self.client.get(cache_key)

            if cached_data:
                data = json.loads(cached_data)
                return MemoryResponse(
                    success=True,
                    data=data,
                    source="redis",
                    metadata={"cache_hit": True, "key": cache_key},
                )
            else:
                return MemoryResponse(
                    success=False,
                    data=None,
                    source="redis",
                    metadata={"cache_hit": False, "key": cache_key},
                )

        except Exception as e:
            self.logger.error(f"Redis query error: {e}")
            return MemoryResponse(
                success=False, data=None, source="redis", metadata={"error": str(e)}
            )

    async def store(self, request: MemoryRequest) -> MemoryResponse:
        """
        Store data in Redis cache.

        Args:
            request: Memory request

        Returns:
            Memory response
        """
        if not self.client:
            return MemoryResponse(
                success=False,
                data=None,
                source="redis",
                metadata={"error": "Redis client not initialized"},
            )

        try:
            # Build cache key
            cache_key = self._build_cache_key(request)

            # Serialize data
            data_json = json.dumps(request.content)

            # Store with TTL if specified
            ttl = request.metadata.get("ttl") if request.metadata else None
            if ttl:
                await self.client.setex(cache_key, ttl, data_json)
            else:
                await self.client.set(cache_key, data_json)

            return MemoryResponse(
                success=True,
                data={"key": cache_key},
                source="redis",
                metadata={"stored": True, "ttl": ttl},
            )

        except Exception as e:
            self.logger.error(f"Redis store error: {e}")
            return MemoryResponse(
                success=False, data=None, source="redis", metadata={"error": str(e)}
            )

    def _build_cache_key(self, request: MemoryRequest) -> str:
        """Build cache key from request."""
        # Simple key building - can be enhanced
        parts = ["plc_orchestrator", request.data_type, request.operation_type]

        # Add content-based key component
        if isinstance(request.content, dict):
            if "task_id" in request.content:
                parts.append(request.content["task_id"])
            elif "code_id" in request.content:
                parts.append(request.content["code_id"])
            elif "identifier" in request.content:
                parts.append(request.content["identifier"])
            elif "description" in request.content:
                # Hash description for shorter key
                import hashlib

                desc_hash = hashlib.md5(request.content["description"].encode()).hexdigest()[:8]
                parts.append(desc_hash)

        return ":".join(parts)

    async def close(self) -> None:
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            self.logger.info("Redis connection closed")
