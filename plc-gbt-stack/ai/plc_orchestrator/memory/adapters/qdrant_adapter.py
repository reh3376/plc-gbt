"""
Qdrant Memory Adapter
=====================

Vector storage for semantic search and similarity matching.
"""

import json
import uuid
from datetime import datetime
from typing import Any

from .base import MemoryAdapter, MemoryEntry, MemoryQuery, MemoryType

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        FieldCondition,
        Filter,
        MatchValue,
        PointStruct,
        SearchRequest,
        UpdateStatus,
        VectorParams,
    )
    HAS_QDRANT = True
except ImportError:
    HAS_QDRANT = False
    QdrantClient = None


class QdrantMemoryAdapter(MemoryAdapter):
    """Qdrant adapter for vector-based memory storage."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Qdrant adapter.
        
        Config options:
            url: Qdrant URL (default: http://localhost:6333)
            api_key: API key for Qdrant Cloud (optional)
            collection: Collection name (default: memory)
            vector_size: Dimension of vectors (default: 1536)
            distance: Distance metric (default: Cosine)
            on_disk: Store vectors on disk (default: False)
        """
        super().__init__(config)

        if not HAS_QDRANT:
            raise ImportError(
                "qdrant-client package not installed. Install with: pip install qdrant-client"
            )

        self.url = config.get('url', 'http://localhost:6333')
        self.api_key = config.get('api_key')
        self.collection_name = config.get('collection', 'memory')
        self.vector_size = config.get('vector_size', 1536)
        self.distance = config.get('distance', 'Cosine')
        self.on_disk = config.get('on_disk', False)
        self.client = None

    async def connect(self) -> None:
        """Connect to Qdrant and ensure collection exists."""
        # Qdrant client handles async internally
        if self.api_key:
            self.client = QdrantClient(url=self.url, api_key=self.api_key)
        else:
            self.client = QdrantClient(url=self.url)

        # Check if collection exists
        collections = self.client.get_collections()
        collection_names = [c.name for c in collections.collections]

        if self.collection_name not in collection_names:
            # Create collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=getattr(Distance, self.distance),
                    on_disk=self.on_disk
                )
            )

            # Create payload indices for better search performance
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="type",
                field_type="keyword"
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="timestamp",
                field_type="datetime"
            )

            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="tags",
                field_type="keyword"
            )

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from Qdrant."""
        # Qdrant client doesn't require explicit disconnect
        self._connected = False

    def _entry_to_point(self, entry: MemoryEntry) -> PointStruct:
        """Convert memory entry to Qdrant point."""
        if not entry.embedding:
            raise ValueError(f"Entry {entry.id} has no embedding vector")

        payload = {
            "type": entry.type.value,
            "content": entry.content,
            "metadata": entry.metadata,
            "timestamp": entry.timestamp.isoformat(),
            "tags": entry.tags,
            "score": entry.score
        }

        return PointStruct(
            id=entry.id,
            vector=entry.embedding,
            payload=payload
        )

    def _point_to_entry(self, point_id: str, payload: dict[str, Any], score: float = None) -> MemoryEntry:
        """Convert Qdrant point to memory entry."""
        return MemoryEntry(
            id=point_id,
            type=MemoryType(payload['type']),
            content=payload['content'],
            metadata=payload['metadata'],
            timestamp=datetime.fromisoformat(payload['timestamp']),
            embedding=None,  # Don't return embeddings in search results
            score=score or payload.get('score'),
            tags=payload.get('tags', [])
        )

    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry in Qdrant."""
        if not entry.id:
            entry.id = str(uuid.uuid4())

        if not entry.embedding:
            raise ValueError("Cannot store entry without embedding vector")

        point = self._entry_to_point(entry)

        # Upsert point
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        if operation_info.status != UpdateStatus.COMPLETED:
            raise Exception(f"Failed to store entry: {operation_info}")

        return entry.id

    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory entry from Qdrant."""
        try:
            # Retrieve by ID
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[entry_id],
                with_payload=True,
                with_vectors=True
            )

            if points:
                point = points[0]
                entry = self._point_to_entry(str(point.id), point.payload)
                entry.embedding = point.vector
                return entry

            return None
        except Exception:
            return None

    async def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search for memory entries using vector similarity and filters."""
        # Build filter conditions
        filter_conditions = []

        # Type filter
        if query.type:
            filter_conditions.append(
                FieldCondition(
                    key="type",
                    match=MatchValue(value=query.type.value)
                )
            )

        # Tags filter
        if query.tags:
            for tag in query.tags:
                filter_conditions.append(
                    FieldCondition(
                        key="tags",
                        match=MatchValue(value=tag)
                    )
                )

        # Time range filter
        if query.time_range:
            # Qdrant doesn't support direct datetime range queries
            # We'll filter these in post-processing
            pass

        # Build filter
        search_filter = None
        if filter_conditions:
            search_filter = Filter(must=filter_conditions)

        # If we have a text query but no embedding, do payload search
        if query.query and not hasattr(query, 'embedding'):
            # Text search in payload (limited capability)
            # This would need custom implementation or external search
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=query.limit * 2,  # Get more for post-filtering
                with_payload=True,
                with_vectors=False
            )[0]

            entries = []
            for point in results:
                # Simple text matching in content
                payload = point.payload
                if query.query.lower() in json.dumps(payload['content']).lower():
                    entry = self._point_to_entry(str(point.id), payload)
                    entries.append(entry)

        # Vector similarity search
        elif hasattr(query, 'embedding') and query.embedding:
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query.embedding,
                query_filter=search_filter,
                limit=query.limit,
                score_threshold=query.threshold
            )

            entries = []
            for result in results:
                entry = self._point_to_entry(
                    str(result.id),
                    result.payload,
                    score=result.score
                )
                entries.append(entry)

        else:
            # No search vector, just filter
            results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=search_filter,
                limit=query.limit,
                with_payload=True,
                with_vectors=False
            )[0]

            entries = []
            for point in results:
                entry = self._point_to_entry(str(point.id), point.payload)
                entries.append(entry)

        # Post-process for time range if specified
        if query.time_range:
            filtered_entries = []
            for entry in entries:
                if query.time_range[0] <= entry.timestamp <= query.time_range[1]:
                    filtered_entries.append(entry)
            entries = filtered_entries

        # Sort by score if available, otherwise by timestamp
        if any(e.score is not None for e in entries):
            entries.sort(key=lambda e: e.score or 0, reverse=True)
        else:
            entries.sort(key=lambda e: e.timestamp, reverse=True)

        # Apply limit
        return entries[:query.limit]

    async def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update memory entry in Qdrant."""
        # Retrieve current entry
        entry = await self.retrieve(entry_id)
        if not entry:
            return False

        # Update fields
        if 'content' in updates:
            entry.content.update(updates['content'])
        if 'metadata' in updates:
            entry.metadata.update(updates['metadata'])
        if 'tags' in updates:
            entry.tags = updates['tags']
        if 'embedding' in updates:
            entry.embedding = updates['embedding']

        # Update in Qdrant
        point = self._entry_to_point(entry)
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

        return operation_info.status == UpdateStatus.COMPLETED

    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry from Qdrant."""
        operation_info = self.client.delete(
            collection_name=self.collection_name,
            points_selector=[entry_id]
        )

        return operation_info.status == UpdateStatus.COMPLETED

    async def clear(self, type: MemoryType | None = None) -> int:
        """Clear memory entries."""
        if type:
            # Delete by type filter
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="type",
                        match=MatchValue(value=type.value)
                    )
                ]
            )

            # First count entries
            count_result = self.client.count(
                collection_name=self.collection_name,
                count_filter=filter_condition
            )
            count = count_result.count

            # Then delete
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=filter_condition
            )

            return count
        else:
            # Get total count
            count_result = self.client.count(
                collection_name=self.collection_name
            )
            count = count_result.count

            # Delete entire collection and recreate
            self.client.delete_collection(self.collection_name)

            # Recreate collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=getattr(Distance, self.distance),
                    on_disk=self.on_disk
                )
            )

            return count

    async def search_by_vector(
        self,
        vector: list[float],
        limit: int = 10,
        threshold: float = 0.7,
        filter_conditions: dict[str, Any] = None
    ) -> list[MemoryEntry]:
        """Search for similar entries using vector."""
        # Build filter
        search_filter = None
        if filter_conditions:
            conditions = []
            for key, value in filter_conditions.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            search_filter = Filter(must=conditions)

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=search_filter,
            limit=limit,
            score_threshold=threshold
        )

        entries = []
        for result in results:
            entry = self._point_to_entry(
                str(result.id),
                result.payload,
                score=result.score
            )
            entries.append(entry)

        return entries

    async def batch_search(
        self,
        queries: list[dict[str, Any]]
    ) -> list[list[MemoryEntry]]:
        """Perform multiple searches in batch."""
        search_requests = []

        for query in queries:
            req = SearchRequest(
                vector=query['vector'],
                filter=query.get('filter'),
                limit=query.get('limit', 10),
                score_threshold=query.get('threshold', 0.7)
            )
            search_requests.append(req)

        # Batch search
        batch_results = self.client.search_batch(
            collection_name=self.collection_name,
            requests=search_requests
        )

        all_results = []
        for results in batch_results:
            entries = []
            for result in results:
                entry = self._point_to_entry(
                    str(result.id),
                    result.payload,
                    score=result.score
                )
                entries.append(entry)
            all_results.append(entries)

        return all_results

    async def get_stats(self) -> dict[str, Any]:
        """Get Qdrant collection statistics."""
        base_stats = await super().get_stats()

        if self._connected:
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)

            # Count by type
            type_counts = {}
            for mem_type in MemoryType:
                count_result = self.client.count(
                    collection_name=self.collection_name,
                    count_filter=Filter(
                        must=[
                            FieldCondition(
                                key="type",
                                match=MatchValue(value=mem_type.value)
                            )
                        ]
                    )
                )
                if count_result.count > 0:
                    type_counts[mem_type.value] = count_result.count

            base_stats.update({
                'total_entries': collection_info.points_count,
                'entries_by_type': type_counts,
                'vector_size': collection_info.config.params.vectors.size,
                'distance_metric': self.distance,
                'indexed_vectors': collection_info.indexed_vectors_count,
                'segments': collection_info.segments_count,
                'status': collection_info.status
            })

        return base_stats
