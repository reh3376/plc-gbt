"""
Redis Caching Service for PLC Conversion - Phase 35.1.4
Caches conversion results to improve performance
Following AI Task Orchestrator methodology
"""

import json
import logging
from typing import Optional

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class ConversionCacheService:
    """
    Redis-based caching for ACD to L5X conversions
    Reduces redundant conversions and improves response time
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[redis.Redis] = None
        self.ttl = 3600  # 1 hour cache TTL
        self.namespace = "plc:conversion"

    async def connect(self) -> None:
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Connected to Redis for conversion caching")

    async def disconnect(self) -> None:
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None
            logger.info("Disconnected from Redis")

    async def get_cached_conversion(self, acd_hash: str) -> Optional[str]:
        """
        Retrieve cached L5X content

        Args:
            acd_hash: SHA256 hash of ACD file content

        Returns:
            Cached L5X content or None if not found
        """
        if not self.redis_client:
            await self.connect()

        try:
            key = f"{self.namespace}:{acd_hash}"
            cached_data = await self.redis_client.get(key)

            if cached_data:
                logger.info(f"Cache hit for conversion {acd_hash}")
                return cached_data
            else:
                logger.info(f"Cache miss for conversion {acd_hash}")
                return None

        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    async def cache_conversion(
        self,
        acd_hash: str,
        l5x_content: str,
        metadata: Optional[dict] = None
    ) -> bool:
        """
        Cache L5X conversion result

        Args:
            acd_hash: SHA256 hash of ACD file content
            l5x_content: Converted L5X content
            metadata: Optional metadata to store

        Returns:
            True if cached successfully
        """
        if not self.redis_client:
            await self.connect()

        try:
            key = f"{self.namespace}:{acd_hash}"

            # Store L5X content
            await self.redis_client.setex(key, self.ttl, l5x_content)

            # Store metadata if provided
            if metadata:
                metadata_key = f"{self.namespace}:meta:{acd_hash}"
                await self.redis_client.setex(
                    metadata_key,
                    self.ttl,
                    json.dumps(metadata)
                )

            logger.info(f"Cached conversion {acd_hash} for {self.ttl} seconds")
            return True

        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    async def get_conversion_metadata(self, acd_hash: str) -> Optional[dict]:
        """
        Retrieve conversion metadata

        Args:
            acd_hash: SHA256 hash of ACD file content

        Returns:
            Metadata dictionary or None
        """
        if not self.redis_client:
            await self.connect()

        try:
            metadata_key = f"{self.namespace}:meta:{acd_hash}"
            metadata_str = await self.redis_client.get(metadata_key)

            if metadata_str:
                return json.loads(metadata_str)
            return None

        except Exception as e:
            logger.error(f"Redis metadata get error: {str(e)}")
            return None

    async def invalidate_cache(self, acd_hash: str) -> bool:
        """
        Remove cached conversion

        Args:
            acd_hash: SHA256 hash of ACD file content

        Returns:
            True if removed successfully
        """
        if not self.redis_client:
            await self.connect()

        try:
            key = f"{self.namespace}:{acd_hash}"
            metadata_key = f"{self.namespace}:meta:{acd_hash}"

            # Delete both content and metadata
            result = await self.redis_client.delete(key, metadata_key)

            logger.info(f"Invalidated cache for {acd_hash}, removed {result} keys")
            return result > 0

        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False

    async def get_cache_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Get all conversion keys
            pattern = f"{self.namespace}:*"
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                if not key.endswith(":meta"):
                    keys.append(key)

            # Get memory usage info
            info = await self.redis_client.info("memory")

            return {
                "cached_conversions": len(keys),
                "memory_used_human": info.get("used_memory_human", "0"),
                "memory_used_bytes": info.get("used_memory", 0),
                "cache_namespace": self.namespace,
                "ttl_seconds": self.ttl
            }

        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {
                "error": str(e),
                "cached_conversions": 0
            }

    async def clear_all_cache(self) -> int:
        """
        Clear all cached conversions

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Find all keys in namespace
            pattern = f"{self.namespace}:*"
            keys_to_delete = []

            async for key in self.redis_client.scan_iter(match=pattern):
                keys_to_delete.append(key)

            if keys_to_delete:
                deleted_count = await self.redis_client.delete(*keys_to_delete)
                logger.info(f"Cleared {deleted_count} cached conversions")
                return deleted_count

            return 0

        except Exception as e:
            logger.error(f"Redis clear cache error: {str(e)}")
            return 0
