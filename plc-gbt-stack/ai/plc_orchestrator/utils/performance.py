"""Performance optimization utilities for the orchestrator."""

import asyncio
import functools
import hashlib
import logging
import time
from collections import OrderedDict
from collections.abc import Callable
from contextlib import contextmanager
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics: dict[str, dict[str, Any]] = {}
        self.active_timers: dict[str, float] = {}

    @contextmanager
    def measure(self, operation: str, metadata: dict[str, Any] | None = None):
        """
        Context manager to measure operation duration.

        Args:
            operation: Name of the operation
            metadata: Additional metadata to store
        """
        start_time = time.perf_counter()

        try:
            yield
        finally:
            duration = time.perf_counter() - start_time

            if operation not in self.metrics:
                self.metrics[operation] = {
                    "count": 0,
                    "total_time": 0.0,
                    "min_time": float("inf"),
                    "max_time": 0.0,
                    "metadata": metadata or {},
                }

            # Update metrics
            self.metrics[operation]["count"] += 1
            self.metrics[operation]["total_time"] += duration
            self.metrics[operation]["min_time"] = min(self.metrics[operation]["min_time"], duration)
            self.metrics[operation]["max_time"] = max(self.metrics[operation]["max_time"], duration)

            logger.debug(f"{operation} completed in {duration:.3f}s")

    def start_timer(self, name: str) -> None:
        """Start a named timer."""
        self.active_timers[name] = time.perf_counter()

    def stop_timer(self, name: str) -> float:
        """Stop a named timer and return duration."""
        if name not in self.active_timers:
            raise ValueError(f"Timer '{name}' not started")

        duration = time.perf_counter() - self.active_timers[name]
        del self.active_timers[name]
        return duration

    def get_summary(self) -> dict[str, dict[str, Any]]:
        """Get performance summary."""
        summary = {}

        for operation, metrics in self.metrics.items():
            if metrics["count"] > 0:
                summary[operation] = {
                    "count": metrics["count"],
                    "average_time": metrics["total_time"] / metrics["count"],
                    "min_time": metrics["min_time"],
                    "max_time": metrics["max_time"],
                    "total_time": metrics["total_time"],
                }

        return summary

    def reset(self) -> None:
        """Reset all metrics."""
        self.metrics.clear()
        self.active_timers.clear()


class LRUCache:
    """Least Recently Used cache implementation."""

    def __init__(self, max_size: int = 128):
        """
        Initialize LRU cache.

        Args:
            max_size: Maximum number of items to cache
        """
        self.max_size = max(1, max_size)
        self.cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if key in self.cache:
            # Move to end (most recently used)
            value, timestamp = self.cache.pop(key)
            self.cache[key] = (value, timestamp)
            self.hits += 1
            return value

        self.misses += 1
        return None

    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size:
            self.cache.popitem(last=False)

        self.cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear cache."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_rate = self.hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": hit_rate,
            "total_requests": total_requests,
        }


def _make_cache_key_func(func_name: str, key_func: Callable[..., str] | None) -> Callable[..., str]:
    """Create a key generation function."""

    def get_key(*args: Any, **kwargs: Any) -> str:
        if key_func:
            return key_func(*args, **kwargs)
        return _default_key_func(func_name, args, kwargs)

    return get_key


def _make_cache_check_func(
    cache: LRUCache, ttl: float | None, func_name: str
) -> Callable[[str], Any | None]:
    """Create a cache check function."""

    def check_cache(key: str) -> Any | None:
        cached = cache.get(key)
        if cached is None:
            return None
        value, timestamp = cached
        if ttl and (time.time() - timestamp) >= ttl:
            return None
        logger.debug(f"Cache hit for {func_name}")
        return value

    return check_cache


def _create_sync_cache_wrapper(
    func: Callable[..., T],
    cache: LRUCache,
    get_key: Callable[..., str],
    check_cache: Callable[[str], Any | None],
) -> Callable[..., T]:
    """Create synchronous caching wrapper."""
    func_name = func.__name__

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> T:
        key = get_key(*args, **kwargs)
        value = check_cache(key)
        if value is not None:
            return value
        logger.debug(f"Cache miss for {func_name}")
        result = func(*args, **kwargs)
        cache.put(key, (result, time.time()))
        return result

    return wrapper


def _create_async_cache_wrapper(
    func: Callable[..., T],
    cache: LRUCache,
    get_key: Callable[..., str],
    check_cache: Callable[[str], Any | None],
) -> Callable[..., T]:
    """Create asynchronous caching wrapper."""
    func_name = func.__name__

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        key = get_key(*args, **kwargs)
        value = check_cache(key)
        if value is not None:
            return value
        logger.debug(f"Cache miss for {func_name}")
        result = await func(*args, **kwargs)
        cache.put(key, (result, time.time()))
        return result

    return wrapper


def _create_cache_wrapper(
    func: Callable[..., T], cache: LRUCache, ttl: float | None, key_func: Callable[..., str] | None
) -> Callable[..., T]:
    """Create a caching wrapper for a function."""
    func_name = func.__name__
    get_key = _make_cache_key_func(func_name, key_func)
    check_cache = _make_cache_check_func(cache, ttl, func_name)

    # Create appropriate wrapper
    if asyncio.iscoroutinefunction(func):
        wrapper = _create_async_cache_wrapper(func, cache, get_key, check_cache)
    else:
        wrapper = _create_sync_cache_wrapper(func, cache, get_key, check_cache)

    # Add cache control methods
    wrapper.cache_clear = cache.clear
    wrapper.cache_stats = cache.get_stats
    return wrapper


def cache_result(
    max_size: int = 128, ttl: float | None = None, key_func: Callable[..., str] | None = None
) -> Callable:
    """
    Decorator to cache function results.

    Args:
        max_size: Maximum cache size
        ttl: Time to live in seconds (None for no expiration)
        key_func: Custom function to generate cache key

    Returns:
        Decorated function with caching
    """
    cache = LRUCache(max_size)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        return _create_cache_wrapper(func, cache, ttl, key_func)

    return decorator


def _default_key_func(func_name: str, args: tuple, kwargs: dict) -> str:
    """Generate default cache key from function arguments."""
    # Create a string representation of arguments
    key_parts = [func_name]

    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))

    # Add keyword arguments (sorted for consistency)
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    # Hash the key for consistent length
    key_str = "|".join(key_parts)
    return hashlib.md5(key_str.encode()).hexdigest()


class ResourcePool:
    """Pool for managing reusable resources."""

    def __init__(self, factory: Callable[[], T], max_size: int = 10, timeout: float = 30.0):
        """
        Initialize resource pool.

        Args:
            factory: Function to create new resources
            max_size: Maximum pool size
            timeout: Timeout for acquiring resources
        """
        self.factory = factory
        self.max_size = max_size
        self.timeout = timeout
        self.pool: asyncio.Queue[T] = asyncio.Queue(maxsize=max_size)
        self.created = 0
        self._lock = asyncio.Lock()

    async def acquire(self) -> T:
        """Acquire a resource from the pool."""
        try:
            # Try to get from pool
            resource = self.pool.get_nowait()
            logger.debug("Resource acquired from pool")
            return resource
        except asyncio.QueueEmpty:
            # Create new if under limit
            async with self._lock:
                if self.created < self.max_size:
                    resource = await self._create_resource()
                    self.created += 1
                    logger.debug(f"Created new resource ({self.created}/{self.max_size})")
                    return resource

            # Wait for available resource
            logger.debug("Waiting for available resource")
            try:
                resource = await asyncio.wait_for(self.pool.get(), timeout=self.timeout)
                return resource
            except TimeoutError:
                raise TimeoutError(f"Resource acquisition timed out after {self.timeout}s")

    async def release(self, resource: T) -> None:
        """Release a resource back to the pool."""
        try:
            self.pool.put_nowait(resource)
            logger.debug("Resource released to pool")
        except asyncio.QueueFull:
            # Pool is full, discard resource
            logger.warning("Pool full, discarding resource")
            await self._cleanup_resource(resource)
            async with self._lock:
                self.created = max(0, self.created - 1)

    async def _create_resource(self) -> T:
        """Create a new resource."""
        if asyncio.iscoroutinefunction(self.factory):
            return await self.factory()
        else:
            return self.factory()

    async def _cleanup_resource(self, resource: T) -> None:
        """Clean up a resource."""
        # Override in subclasses for proper cleanup
        pass

    async def close(self) -> None:
        """Close the pool and clean up resources."""
        # Get all resources from pool
        resources = []
        while not self.pool.empty():
            try:
                resources.append(self.pool.get_nowait())
            except asyncio.QueueEmpty:
                break

        # Clean up all resources
        for resource in resources:
            await self._cleanup_resource(resource)

        self.created = 0


def profile(func: Callable[..., T]) -> Callable[..., T]:
    """
    Simple profiling decorator.

    Logs execution time and memory usage (if available).
    """

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.perf_counter()

        try:
            import psutil

            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            start_memory = None

        try:
            result = func(*args, **kwargs)

            duration = time.perf_counter() - start_time

            if start_memory is not None:
                end_memory = process.memory_info().rss / 1024 / 1024
                memory_delta = end_memory - start_memory
                logger.info(
                    f"{func.__name__} completed in {duration:.3f}s, "
                    f"memory delta: {memory_delta:+.1f} MB"
                )
            else:
                logger.info(f"{func.__name__} completed in {duration:.3f}s")

            return result

        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise

    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> T:
        start_time = time.perf_counter()

        try:
            import psutil

            process = psutil.Process()
            start_memory = process.memory_info().rss / 1024 / 1024  # MB
        except ImportError:
            start_memory = None

        try:
            result = await func(*args, **kwargs)

            duration = time.perf_counter() - start_time

            if start_memory is not None:
                end_memory = process.memory_info().rss / 1024 / 1024
                memory_delta = end_memory - start_memory
                logger.info(
                    f"{func.__name__} completed in {duration:.3f}s, "
                    f"memory delta: {memory_delta:+.1f} MB"
                )
            else:
                logger.info(f"{func.__name__} completed in {duration:.3f}s")

            return result

        except Exception as e:
            duration = time.perf_counter() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {e}")
            raise

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


# Global performance monitor instance
global_monitor = PerformanceMonitor()
