"""
Redis Memory Adapter
====================

Fast in-memory storage for caching and session management.
"""

import json
import uuid
from datetime import datetime
from typing import Any

from .base import MemoryAdapter, MemoryEntry, MemoryQuery, MemoryType

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    redis = None


class RedisMemoryAdapter(MemoryAdapter):
    """Redis adapter for fast memory storage."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Redis adapter.
        
        Config options:
            url: Redis URL (default: redis://localhost:6379)
            db: Database number (default: 0)
            ttl: Default TTL in seconds (default: 3600)
            key_prefix: Prefix for all keys (default: memory:)
        """
        super().__init__(config)

        if not HAS_REDIS:
            raise ImportError(
                "Redis package not installed. Install with: pip install redis[hiredis]"
            )

        self.url = config.get('url', 'redis://localhost:6379')
        self.db = config.get('db', 0)
        self.ttl = config.get('ttl', 3600)
        self.key_prefix = config.get('key_prefix', 'memory:')
        self.client = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.client = redis.from_url(
            self.url,
            db=self.db,
            decode_responses=True
        )
        # Test connection
        await self.client.ping()
        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
            self._connected = False

    def _make_key(self, entry_id: str) -> str:
        """Generate Redis key for entry."""
        return f"{self.key_prefix}{entry_id}"

    def _serialize_entry(self, entry: MemoryEntry) -> str:
        """Serialize memory entry to JSON."""
        data = {
            'id': entry.id,
            'type': entry.type.value,
            'content': entry.content,
            'metadata': entry.metadata,
            'timestamp': entry.timestamp.isoformat(),
            'embedding': entry.embedding,
            'score': entry.score,
            'tags': entry.tags
        }
        return json.dumps(data)

    def _deserialize_entry(self, data: str) -> MemoryEntry:
        """Deserialize JSON to memory entry."""
        obj = json.loads(data)
        return MemoryEntry(
            id=obj['id'],
            type=MemoryType(obj['type']),
            content=obj['content'],
            metadata=obj['metadata'],
            timestamp=datetime.fromisoformat(obj['timestamp']),
            embedding=obj.get('embedding'),
            score=obj.get('score'),
            tags=obj.get('tags', [])
        )

    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry in Redis."""
        if not entry.id:
            entry.id = str(uuid.uuid4())

        key = self._make_key(entry.id)
        data = self._serialize_entry(entry)

        # Store with TTL
        await self.client.setex(key, self.ttl, data)

        # Add to type index
        type_key = f"{self.key_prefix}type:{entry.type.value}"
        await self.client.sadd(type_key, entry.id)
        await self.client.expire(type_key, self.ttl)

        # Add to tag indices
        for tag in entry.tags:
            tag_key = f"{self.key_prefix}tag:{tag}"
            await self.client.sadd(tag_key, entry.id)
            await self.client.expire(tag_key, self.ttl)

        # Update timestamp index
        timestamp_key = f"{self.key_prefix}timestamps"
        await self.client.zadd(
            timestamp_key,
            {entry.id: entry.timestamp.timestamp()}
        )

        return entry.id

    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory entry from Redis."""
        key = self._make_key(entry_id)
        data = await self.client.get(key)

        if data:
            return self._deserialize_entry(data)
        return None

    async def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search for memory entries."""
        candidate_ids = set()

        # Search by type
        if query.type:
            type_key = f"{self.key_prefix}type:{query.type.value}"
            type_ids = await self.client.smembers(type_key)
            if type_ids:
                candidate_ids = set(type_ids)

        # Search by tags
        if query.tags:
            tag_ids_list = []
            for tag in query.tags:
                tag_key = f"{self.key_prefix}tag:{tag}"
                tag_ids = await self.client.smembers(tag_key)
                if tag_ids:
                    tag_ids_list.append(set(tag_ids))

            if tag_ids_list:
                # Intersection of all tag sets
                tag_candidates = tag_ids_list[0]
                for tag_set in tag_ids_list[1:]:
                    tag_candidates = tag_candidates.intersection(tag_set)

                if candidate_ids:
                    candidate_ids = candidate_ids.intersection(tag_candidates)
                else:
                    candidate_ids = tag_candidates

        # If no type or tag filters, get all entries
        if not candidate_ids and not query.type and not query.tags:
            # Get from timestamp index
            timestamp_key = f"{self.key_prefix}timestamps"
            all_ids = await self.client.zrange(timestamp_key, 0, -1)
            candidate_ids = set(all_ids)

        # Apply time range filter
        if query.time_range and candidate_ids:
            timestamp_key = f"{self.key_prefix}timestamps"
            start_ts = query.time_range[0].timestamp()
            end_ts = query.time_range[1].timestamp()

            time_ids = await self.client.zrangebyscore(
                timestamp_key,
                start_ts,
                end_ts
            )
            candidate_ids = candidate_ids.intersection(set(time_ids))

        # Retrieve entries
        entries = []
        for entry_id in candidate_ids:
            entry = await self.retrieve(entry_id)
            if entry:
                entries.append(entry)

        # Sort by timestamp (newest first)
        entries.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit
        if query.limit:
            entries = entries[:query.limit]

        return entries

    async def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update memory entry."""
        entry = await self.retrieve(entry_id)
        if not entry:
            return False

        # Update fields
        if 'content' in updates:
            entry.content.update(updates['content'])
        if 'metadata' in updates:
            entry.metadata.update(updates['metadata'])
        if 'tags' in updates:
            # Remove from old tag indices
            for old_tag in entry.tags:
                tag_key = f"{self.key_prefix}tag:{old_tag}"
                await self.client.srem(tag_key, entry_id)

            # Update tags
            entry.tags = updates['tags']

            # Add to new tag indices
            for new_tag in entry.tags:
                tag_key = f"{self.key_prefix}tag:{new_tag}"
                await self.client.sadd(tag_key, entry_id)
                await self.client.expire(tag_key, self.ttl)

        # Save updated entry
        key = self._make_key(entry_id)
        data = self._serialize_entry(entry)
        await self.client.setex(key, self.ttl, data)

        return True

    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry."""
        entry = await self.retrieve(entry_id)
        if not entry:
            return False

        # Remove from main storage
        key = self._make_key(entry_id)
        await self.client.delete(key)

        # Remove from type index
        type_key = f"{self.key_prefix}type:{entry.type.value}"
        await self.client.srem(type_key, entry_id)

        # Remove from tag indices
        for tag in entry.tags:
            tag_key = f"{self.key_prefix}tag:{tag}"
            await self.client.srem(tag_key, entry_id)

        # Remove from timestamp index
        timestamp_key = f"{self.key_prefix}timestamps"
        await self.client.zrem(timestamp_key, entry_id)

        return True

    async def clear(self, type: MemoryType | None = None) -> int:
        """Clear memory entries."""
        count = 0

        if type:
            # Clear specific type
            type_key = f"{self.key_prefix}type:{type.value}"
            entry_ids = await self.client.smembers(type_key)

            for entry_id in entry_ids:
                if await self.delete(entry_id):
                    count += 1
        else:
            # Clear all entries
            # Get all keys with prefix
            cursor = 0
            while True:
                cursor, keys = await self.client.scan(
                    cursor,
                    match=f"{self.key_prefix}*",
                    count=100
                )

                if keys:
                    # Filter out index keys
                    entry_keys = [
                        k for k in keys
                        if not k.startswith(f"{self.key_prefix}type:") and
                        not k.startswith(f"{self.key_prefix}tag:") and
                        k != f"{self.key_prefix}timestamps"
                    ]

                    if entry_keys:
                        await self.client.delete(*entry_keys)
                        count += len(entry_keys)

                if cursor == 0:
                    break

            # Clear all indices
            pattern_keys = [
                f"{self.key_prefix}type:*",
                f"{self.key_prefix}tag:*",
                f"{self.key_prefix}timestamps"
            ]

            for pattern in pattern_keys:
                cursor = 0
                while True:
                    cursor, keys = await self.client.scan(
                        cursor,
                        match=pattern,
                        count=100
                    )

                    if keys:
                        await self.client.delete(*keys)

                    if cursor == 0:
                        break

        return count

    async def get_stats(self) -> dict[str, Any]:
        """Get Redis memory statistics."""
        base_stats = await super().get_stats()

        if self._connected:
            # Get memory info
            info = await self.client.info('memory')

            # Count entries
            timestamp_key = f"{self.key_prefix}timestamps"
            total_entries = await self.client.zcard(timestamp_key)

            # Count by type
            type_counts = {}
            for mem_type in MemoryType:
                type_key = f"{self.key_prefix}type:{mem_type.value}"
                count = await self.client.scard(type_key)
                if count > 0:
                    type_counts[mem_type.value] = count

            base_stats.update({
                'total_entries': total_entries,
                'entries_by_type': type_counts,
                'memory_used_mb': info.get('used_memory', 0) / (1024 * 1024),
                'memory_peak_mb': info.get('used_memory_peak', 0) / (1024 * 1024),
                'connected_clients': info.get('connected_clients', 0)
            })

        return base_stats
