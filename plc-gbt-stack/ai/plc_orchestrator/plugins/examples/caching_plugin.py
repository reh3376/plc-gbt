"""
Example caching plugin.

Demonstrates memory-related hooks and caching strategies.
"""

import hashlib
import time
from typing import Any

from plc_orchestrator.plugins.base import HookType, MemoryPlugin, PluginHook, PluginMetadata
from plc_orchestrator.utils.performance import LRUCache


class SmartCachingPlugin(MemoryPlugin):
    """Plugin that adds intelligent caching to memory operations."""

    def __init__(self):
        """Initialize plugin."""
        self.cache = LRUCache(max_size=1000)
        self.cache_ttl = 3600  # 1 hour
        self.orchestrator = None
        self.stats = {
            "hits": 0,
            "misses": 0,
            "stores": 0,
            "evictions": 0,
        }

    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        return PluginMetadata(
            name="smart_caching",
            version="1.0.0",
            description="Adds intelligent caching layer to memory operations",
            author="AI Task Orchestrator Team",
            tags=["memory", "cache", "performance"],
            dependencies=["plc_orchestrator>=2.0.0"],
        )

    def initialize(self, orchestrator: Any) -> None:
        """Initialize plugin with orchestrator."""
        self.orchestrator = orchestrator

        # Configure cache based on orchestrator settings
        if hasattr(orchestrator, "config"):
            config = orchestrator.config
            if hasattr(config, "cache_size"):
                self.cache = LRUCache(max_size=config.cache_size)
            if hasattr(config, "cache_ttl"):
                self.cache_ttl = config.cache_ttl

    def get_hooks(self) -> list[PluginHook]:
        """Get plugin hooks."""
        return [
            PluginHook(
                hook_type=HookType.PRE_MEMORY_STORE,
                callback=self.pre_store,
                priority=80,
            ),
            PluginHook(
                hook_type=HookType.POST_MEMORY_STORE,
                callback=self.post_store,
                priority=20,
            ),
            PluginHook(
                hook_type=HookType.PRE_MEMORY_RETRIEVE,
                callback=self.pre_retrieve,
                priority=90,  # High priority to intercept early
            ),
            PluginHook(
                hook_type=HookType.POST_MEMORY_RETRIEVE,
                callback=self.post_retrieve,
                priority=10,
            ),
            PluginHook(
                hook_type=HookType.SHUTDOWN,
                callback=self.on_shutdown,
                priority=50,
            ),
        ]

    def pre_store(self, key: str, value: Any) -> tuple[str, Any]:
        """Pre-process before storing."""
        # Add metadata for caching
        cache_key = self._get_cache_key(key)
        metadata = {
            "_original_value": value,
            "_cached_at": time.time(),
            "_cache_key": cache_key,
        }

        # Store in cache
        self.cache.put(cache_key, value)
        self.stats["stores"] += 1

        # Return modified value with metadata
        return key, metadata

    def post_store(self, key: str, value: Any, success: bool) -> None:
        """Post-process after storing."""
        if not success:
            # Remove from cache if store failed
            cache_key = self._get_cache_key(key)
            if cache_key in self.cache.cache:
                del self.cache.cache[cache_key]

    def pre_retrieve(self, key: str) -> tuple[str, bool, Any | None]:
        """Check cache before retrieving."""
        cache_key = self._get_cache_key(key)
        cached_value = self.cache.get(cache_key)

        if cached_value is not None:
            self.stats["hits"] += 1
            # Return cached value, skipping actual retrieval
            return key, True, cached_value

        self.stats["misses"] += 1
        # Continue with normal retrieval
        return key, False, None

    def post_retrieve(self, key: str, value: Any | None) -> Any | None:
        """Post-process after retrieving."""
        if value is not None:
            # Extract original value if it has our metadata
            if isinstance(value, dict) and "_original_value" in value:
                original_value = value["_original_value"]
                cached_at = value.get("_cached_at", 0)

                # Check if cache is still valid
                if time.time() - cached_at < self.cache_ttl:
                    return original_value
                else:
                    # Cache expired, remove it
                    cache_key = self._get_cache_key(key)
                    if cache_key in self.cache.cache:
                        del self.cache.cache[cache_key]
                        self.stats["evictions"] += 1

            # Update cache with fresh value
            cache_key = self._get_cache_key(key)
            self.cache.put(cache_key, value)

        return value

    def _get_cache_key(self, key: str) -> str:
        """Generate cache key."""
        # Use hash for consistent key length
        return hashlib.md5(key.encode()).hexdigest()

    def on_shutdown(self) -> None:
        """Log statistics on shutdown."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0

        print("\n=== Smart Caching Plugin Statistics ===")
        print(f"Total requests: {total_requests}")
        print(f"Cache hits: {self.stats['hits']}")
        print(f"Cache misses: {self.stats['misses']}")
        print(f"Hit rate: {hit_rate:.1f}%")
        print(f"Items stored: {self.stats['stores']}")
        print(f"Items evicted: {self.stats['evictions']}")
        print(f"Current cache size: {len(self.cache.cache)}")
        print("=====================================\n")

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        self.cache.clear()
        self.stats.clear()

    # Additional memory plugin methods

    def analyze_task(self, task: str, analysis: Any) -> Any:
        """Not used in this plugin."""
        return analysis

    def validate_code(self, code: str, result: Any) -> Any:
        """Not used in this plugin."""
        return result
