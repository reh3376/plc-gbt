#!/usr/bin/env python3
"""
Redis Cache Integration for PLC-GPT Enterprise
Phase 3 Days 6-7: Enterprise Features
"""

import json
import pickle
import hashlib
import time
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from datetime import datetime, timedelta
from functools import wraps
from dataclasses import dataclass
import redis
from redis.lock import Lock
import logging
from config.enterprise_settings import EnterpriseSettings


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    tags: List[str] = None
    size_bytes: int = 0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class RedisCache:
    """
    Advanced Redis-based caching system with intelligent invalidation,
    distributed locking, and performance optimization.
    """
    
    def __init__(self, settings: EnterpriseSettings):
        self.settings = settings
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            decode_responses=False,  # Keep binary for pickle
            socket_timeout=5.0,
            socket_connect_timeout=5.0,
            retry_on_timeout=True,
            health_check_interval=30
        )
        
        # Statistics tracking
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'invalidations': 0,
            'errors': 0
        }
        
        # Cache configuration
        self.default_ttl = 3600  # 1 hour
        self.max_key_length = 250
        self.compression_threshold = 1024  # Compress values larger than 1KB
        
        # Key prefixes for different data types
        self.prefixes = {
            'cache': 'cache:',
            'stats': 'stats:',
            'tags': 'tags:',
            'locks': 'locks:',
            'meta': 'meta:',
            'index': 'index:'
        }
        
        self.logger = logging.getLogger(__name__)
    
    def _make_key(self, key: str, prefix: str = 'cache') -> str:
        """Generate a full Redis key with prefix."""
        full_key = f"{self.prefixes[prefix]}{key}"
        if len(full_key) > self.max_key_length:
            # Hash long keys
            hash_key = hashlib.md5(full_key.encode()).hexdigest()
            full_key = f"{self.prefixes[prefix]}hash:{hash_key}"
        return full_key
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize a value for storage."""
        try:
            if isinstance(value, (str, int, float, bool)):
                # Simple JSON serialization for basic types
                return json.dumps(value).encode()
            else:
                # Pickle for complex objects
                return pickle.dumps(value)
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            raise
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize a value from storage."""
        try:
            # Try JSON first
            try:
                return json.loads(data.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Fall back to pickle
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            raise
    
    def _get_cache_key_hash(self, *args, **kwargs) -> str:
        """Generate a hash key for cache storage."""
        # Create a consistent hash from arguments
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        try:
            redis_key = self._make_key(key)
            data = self.redis_client.get(redis_key)
            
            if data is None:
                self.stats['misses'] += 1
                return default
            
            # Update access statistics
            self._update_access_stats(key)
            self.stats['hits'] += 1
            
            return self._deserialize_value(data)
            
        except Exception as e:
            self.logger.error(f"Cache get error for key {key}: {e}")
            self.stats['errors'] += 1
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            tags: Optional[List[str]] = None) -> bool:
        """Set a value in cache."""
        try:
            redis_key = self._make_key(key)
            serialized_value = self._serialize_value(value)
            
            # Set TTL
            if ttl is None:
                ttl = self.default_ttl
            
            # Store the value
            success = self.redis_client.setex(redis_key, ttl, serialized_value)
            
            if success:
                # Store metadata
                self._store_metadata(key, value, ttl, tags)
                
                # Update tag indexes
                if tags:
                    self._update_tag_indexes(key, tags)
                
                self.stats['sets'] += 1
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Cache set error for key {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        try:
            redis_key = self._make_key(key)
            
            # Delete main key
            deleted = self.redis_client.delete(redis_key)
            
            if deleted:
                # Clean up metadata
                self._cleanup_metadata(key)
                self.stats['deletes'] += 1
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Cache delete error for key {key}: {e}")
            self.stats['errors'] += 1
            return False
    
    def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            redis_key = self._make_key(key)
            return bool(self.redis_client.exists(redis_key))
        except Exception as e:
            self.logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration time for a key."""
        try:
            redis_key = self._make_key(key)
            return bool(self.redis_client.expire(redis_key, ttl))
        except Exception as e:
            self.logger.error(f"Cache expire error for key {key}: {e}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get time to live for a key."""
        try:
            redis_key = self._make_key(key)
            ttl = self.redis_client.ttl(redis_key)
            return ttl if ttl > 0 else None
        except Exception as e:
            self.logger.error(f"Cache TTL error for key {key}: {e}")
            return None
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        try:
            redis_keys = [self._make_key(key) for key in keys]
            values = self.redis_client.mget(redis_keys)
            
            result = {}
            for i, (key, data) in enumerate(zip(keys, values)):
                if data is not None:
                    result[key] = self._deserialize_value(data)
                    self.stats['hits'] += 1
                    self._update_access_stats(key)
                else:
                    self.stats['misses'] += 1
            
            return result
            
        except Exception as e:
            self.logger.error(f"Cache get_many error: {e}")
            self.stats['errors'] += 1
            return {}
    
    def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None,
                 tags: Optional[List[str]] = None) -> bool:
        """Set multiple values in cache."""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            # Use pipeline for efficiency
            pipe = self.redis_client.pipeline()
            
            for key, value in data.items():
                redis_key = self._make_key(key)
                serialized_value = self._serialize_value(value)
                pipe.setex(redis_key, ttl, serialized_value)
            
            results = pipe.execute()
            
            # Update metadata and stats
            for key, value in data.items():
                self._store_metadata(key, value, ttl, tags)
                if tags:
                    self._update_tag_indexes(key, tags)
                self.stats['sets'] += 1
            
            return all(results)
            
        except Exception as e:
            self.logger.error(f"Cache set_many error: {e}")
            self.stats['errors'] += 1
            return False
    
    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from cache."""
        try:
            redis_keys = [self._make_key(key) for key in keys]
            deleted = self.redis_client.delete(*redis_keys)
            
            # Clean up metadata
            for key in keys:
                self._cleanup_metadata(key)
            
            self.stats['deletes'] += deleted
            return deleted
            
        except Exception as e:
            self.logger.error(f"Cache delete_many error: {e}")
            self.stats['errors'] += 1
            return 0
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """Invalidate all cache entries with specified tags."""
        try:
            keys_to_delete = set()
            
            for tag in tags:
                tag_key = self._make_key(f"tag:{tag}", 'tags')
                tagged_keys = self.redis_client.smembers(tag_key)
                
                for key in tagged_keys:
                    if isinstance(key, bytes):
                        key = key.decode()
                    keys_to_delete.add(key)
            
            if keys_to_delete:
                deleted = self.delete_many(list(keys_to_delete))
                self.stats['invalidations'] += deleted
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Cache invalidate_by_tags error: {e}")
            self.stats['errors'] += 1
            return 0
    
    def invalidate_by_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        try:
            redis_pattern = self._make_key(pattern)
            keys = self.redis_client.keys(redis_pattern)
            
            if keys:
                # Extract original keys
                original_keys = []
                for key in keys:
                    if isinstance(key, bytes):
                        key = key.decode()
                    # Remove prefix to get original key
                    original_key = key.replace(self.prefixes['cache'], '')
                    original_keys.append(original_key)
                
                deleted = self.delete_many(original_keys)
                self.stats['invalidations'] += deleted
                return deleted
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Cache invalidate_by_pattern error: {e}")
            self.stats['errors'] += 1
            return 0
    
    def clear_all(self) -> bool:
        """Clear all cache entries."""
        try:
            pattern = self._make_key('*')
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                self.stats['deletes'] += deleted
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Cache clear_all error: {e}")
            self.stats['errors'] += 1
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            # Get Redis info
            redis_info = self.redis_client.info()
            
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            stats = {
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'sets': self.stats['sets'],
                'deletes': self.stats['deletes'],
                'invalidations': self.stats['invalidations'],
                'errors': self.stats['errors'],
                'hit_rate': f"{hit_rate:.2f}%",
                'total_requests': total_requests,
                'redis_info': {
                    'connected_clients': redis_info.get('connected_clients', 0),
                    'used_memory': redis_info.get('used_memory_human', '0B'),
                    'used_memory_peak': redis_info.get('used_memory_peak_human', '0B'),
                    'keyspace_hits': redis_info.get('keyspace_hits', 0),
                    'keyspace_misses': redis_info.get('keyspace_misses', 0),
                    'uptime_in_seconds': redis_info.get('uptime_in_seconds', 0)
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Cache get_stats error: {e}")
            return self.stats
    
    def _store_metadata(self, key: str, value: Any, ttl: int, tags: Optional[List[str]]) -> None:
        """Store metadata for a cache entry."""
        try:
            metadata = {
                'created_at': datetime.utcnow().isoformat(),
                'expires_at': (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
                'tags': tags or [],
                'size_bytes': len(self._serialize_value(value))
            }
            
            meta_key = self._make_key(key, 'meta')
            self.redis_client.setex(meta_key, ttl, json.dumps(metadata))
            
        except Exception as e:
            self.logger.error(f"Store metadata error for key {key}: {e}")
    
    def _cleanup_metadata(self, key: str) -> None:
        """Clean up metadata for a cache entry."""
        try:
            meta_key = self._make_key(key, 'meta')
            self.redis_client.delete(meta_key)
            
            # Clean up tag indexes
            self._cleanup_tag_indexes(key)
            
        except Exception as e:
            self.logger.error(f"Cleanup metadata error for key {key}: {e}")
    
    def _update_access_stats(self, key: str) -> None:
        """Update access statistics for a key."""
        try:
            stats_key = self._make_key(key, 'stats')
            pipe = self.redis_client.pipeline()
            pipe.hincrby(stats_key, 'access_count', 1)
            pipe.hset(stats_key, 'last_accessed', datetime.utcnow().isoformat())
            pipe.expire(stats_key, self.default_ttl)
            pipe.execute()
            
        except Exception as e:
            self.logger.error(f"Update access stats error for key {key}: {e}")
    
    def _update_tag_indexes(self, key: str, tags: List[str]) -> None:
        """Update tag indexes for a key."""
        try:
            pipe = self.redis_client.pipeline()
            
            for tag in tags:
                tag_key = self._make_key(f"tag:{tag}", 'tags')
                pipe.sadd(tag_key, key)
                pipe.expire(tag_key, self.default_ttl)
            
            pipe.execute()
            
        except Exception as e:
            self.logger.error(f"Update tag indexes error for key {key}: {e}")
    
    def _cleanup_tag_indexes(self, key: str) -> None:
        """Clean up tag indexes for a key."""
        try:
            # Get tags for this key
            meta_key = self._make_key(key, 'meta')
            metadata = self.redis_client.get(meta_key)
            
            if metadata:
                metadata = json.loads(metadata)
                tags = metadata.get('tags', [])
                
                # Remove key from tag sets
                pipe = self.redis_client.pipeline()
                for tag in tags:
                    tag_key = self._make_key(f"tag:{tag}", 'tags')
                    pipe.srem(tag_key, key)
                pipe.execute()
                
        except Exception as e:
            self.logger.error(f"Cleanup tag indexes error for key {key}: {e}")
    
    def get_lock(self, key: str, timeout: int = 10) -> Lock:
        """Get a distributed lock."""
        lock_key = self._make_key(key, 'locks')
        return Lock(self.redis_client, lock_key, timeout=timeout)
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on Redis connection."""
        try:
            start_time = time.time()
            
            # Test basic operations
            test_key = 'health_check_test'
            test_value = 'test_value'
            
            # Set
            self.redis_client.set(test_key, test_value, ex=60)
            
            # Get
            retrieved_value = self.redis_client.get(test_key)
            
            # Delete
            self.redis_client.delete(test_key)
            
            end_time = time.time()
            
            return {
                'status': 'healthy',
                'response_time_ms': (end_time - start_time) * 1000,
                'operations_tested': ['set', 'get', 'delete'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


# Global cache instance
cache = None


def get_cache() -> RedisCache:
    """Get the global cache instance."""
    global cache
    if cache is None:
        settings = EnterpriseSettings()
        cache = RedisCache(settings)
    return cache


# Caching decorators
def cached(ttl: int = 3600, tags: Optional[List[str]] = None, 
          key_prefix: str = '', version: str = '1'):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time to live in seconds
        tags: List of tags for cache invalidation
        key_prefix: Prefix for cache key
        version: Cache version for invalidation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_instance = get_cache()
            
            # Generate cache key
            func_name = f"{func.__module__}.{func.__name__}"
            args_hash = cache_instance._get_cache_key_hash(*args, **kwargs)
            cache_key = f"{key_prefix}{func_name}:v{version}:{args_hash}"
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache_instance.set(cache_key, result, ttl, tags)
            
            return result
        
        return wrapper
    return decorator


def cache_invalidate(tags: Optional[List[str]] = None, 
                    pattern: Optional[str] = None):
    """
    Decorator for invalidating cache entries.
    
    Args:
        tags: List of tags to invalidate
        pattern: Pattern to match for invalidation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            cache_instance = get_cache()
            
            # Invalidate by tags
            if tags:
                cache_instance.invalidate_by_tags(tags)
            
            # Invalidate by pattern
            if pattern:
                cache_instance.invalidate_by_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator


def cache_warm_up(keys_and_functions: List[Tuple[str, Callable]]):
    """
    Warm up cache with pre-computed values.
    
    Args:
        keys_and_functions: List of (key, function) tuples
    """
    cache_instance = get_cache()
    
    for key, func in keys_and_functions:
        try:
            value = func()
            cache_instance.set(key, value)
        except Exception as e:
            logging.error(f"Cache warm-up error for key {key}: {e}")


# Utility functions
def get_cache_key_for_query(query: str, parameters: Dict[str, Any]) -> str:
    """Generate a cache key for a database query."""
    query_hash = hashlib.md5(query.encode()).hexdigest()
    params_hash = hashlib.md5(json.dumps(parameters, sort_keys=True).encode()).hexdigest()
    return f"query:{query_hash}:{params_hash}"


def get_cache_key_for_file(file_path: str, file_hash: str) -> str:
    """Generate a cache key for a file."""
    return f"file:{file_path}:{file_hash}"


def get_cache_key_for_user(user_id: str, data_type: str) -> str:
    """Generate a cache key for user-specific data."""
    return f"user:{user_id}:{data_type}"


# Context manager for cache operations
class CacheContext:
    """Context manager for cache operations with automatic cleanup."""
    
    def __init__(self, cache_instance: RedisCache, keys: List[str]):
        self.cache = cache_instance
        self.keys = keys
        self.locks = []
    
    def __enter__(self):
        # Acquire locks for all keys
        for key in self.keys:
            lock = self.cache.get_lock(key)
            if lock.acquire(blocking=False):
                self.locks.append(lock)
            else:
                # Release acquired locks and raise exception
                for acquired_lock in self.locks:
                    acquired_lock.release()
                raise RuntimeError(f"Could not acquire lock for key: {key}")
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Release all locks
        for lock in self.locks:
            try:
                lock.release()
            except Exception as e:
                logging.error(f"Error releasing lock: {e}")


# Async cache operations
class AsyncRedisCache:
    """Async wrapper for Redis cache operations."""
    
    def __init__(self, cache_instance: RedisCache):
        self.cache = cache_instance
    
    async def get(self, key: str, default: Any = None) -> Any:
        """Async get operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache.get, key, default)
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                  tags: Optional[List[str]] = None) -> bool:
        """Async set operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache.set, key, value, ttl, tags)
    
    async def delete(self, key: str) -> bool:
        """Async delete operation."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.cache.delete, key)


def get_async_cache() -> AsyncRedisCache:
    """Get async cache instance."""
    return AsyncRedisCache(get_cache()) 