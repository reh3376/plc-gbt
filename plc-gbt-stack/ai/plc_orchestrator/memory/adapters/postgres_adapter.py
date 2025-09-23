"""
PostgreSQL Memory Adapter
=========================

Relational storage for structured memory with full-text search.
"""

import json
import uuid
from typing import Any

from .base import MemoryAdapter, MemoryEntry, MemoryQuery, MemoryType

try:
    import asyncpg
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    asyncpg = None


class PostgresMemoryAdapter(MemoryAdapter):
    """PostgreSQL adapter for relational memory storage."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize PostgreSQL adapter.
        
        Config options:
            dsn: PostgreSQL DSN (default: postgresql://localhost/memory)
            host: Host (used if dsn not provided)
            port: Port (default: 5432)
            database: Database name (default: memory)
            user: Username
            password: Password
            schema: Schema name (default: memory)
        """
        super().__init__(config)

        if not HAS_POSTGRES:
            raise ImportError(
                "asyncpg package not installed. Install with: pip install asyncpg"
            )

        self.dsn = config.get('dsn')
        if not self.dsn:
            # Build DSN from components
            host = config.get('host', 'localhost')
            port = config.get('port', 5432)
            database = config.get('database', 'memory')
            user = config.get('user', 'postgres')
            password = config.get('password', '')

            self.dsn = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        self.schema = config.get('schema', 'memory')
        self.pool = None

    async def connect(self) -> None:
        """Connect to PostgreSQL and initialize schema."""
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=10)

        # Create schema and tables if not exists
        async with self.pool.acquire() as conn:
            await conn.execute(f"CREATE SCHEMA IF NOT EXISTS {self.schema}")

            # Create memory entries table
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.entries (
                    id UUID PRIMARY KEY,
                    type VARCHAR(50) NOT NULL,
                    content JSONB NOT NULL,
                    metadata JSONB NOT NULL,
                    timestamp TIMESTAMPTZ NOT NULL,
                    embedding FLOAT8[],
                    score FLOAT8,
                    tags TEXT[],
                    search_vector tsvector GENERATED ALWAYS AS (
                        setweight(to_tsvector('english', coalesce(content->>'description', '')), 'A') ||
                        setweight(to_tsvector('english', coalesce(content->>'code', '')), 'B') ||
                        setweight(to_tsvector('english', coalesce(array_to_string(tags, ' '), '')), 'C')
                    ) STORED
                )
            """)

            # Create indices
            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_type 
                ON {self.schema}.entries(type)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_timestamp 
                ON {self.schema}.entries(timestamp DESC)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_tags 
                ON {self.schema}.entries USING GIN(tags)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_search 
                ON {self.schema}.entries USING GIN(search_vector)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_content 
                ON {self.schema}.entries USING GIN(content)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_entries_metadata 
                ON {self.schema}.entries USING GIN(metadata)
            """)

            # Create relationships table
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.schema}.relationships (
                    id SERIAL PRIMARY KEY,
                    from_id UUID REFERENCES {self.schema}.entries(id) ON DELETE CASCADE,
                    to_id UUID REFERENCES {self.schema}.entries(id) ON DELETE CASCADE,
                    type VARCHAR(50) NOT NULL,
                    metadata JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    UNIQUE(from_id, to_id, type)
                )
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_relationships_from 
                ON {self.schema}.relationships(from_id)
            """)

            await conn.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_relationships_to 
                ON {self.schema}.relationships(to_id)
            """)

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from PostgreSQL."""
        if self.pool:
            await self.pool.close()
            self._connected = False

    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry in PostgreSQL."""
        if not entry.id:
            entry.id = str(uuid.uuid4())

        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                INSERT INTO {self.schema}.entries 
                (id, type, content, metadata, timestamp, embedding, score, tags)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (id) DO UPDATE SET
                    content = EXCLUDED.content,
                    metadata = EXCLUDED.metadata,
                    timestamp = EXCLUDED.timestamp,
                    embedding = EXCLUDED.embedding,
                    score = EXCLUDED.score,
                    tags = EXCLUDED.tags
                """,
                uuid.UUID(entry.id),
                entry.type.value,
                json.dumps(entry.content),
                json.dumps(entry.metadata),
                entry.timestamp,
                entry.embedding,
                entry.score,
                entry.tags
            )

            # Handle relationships
            if 'related_to' in entry.metadata:
                related_ids = entry.metadata['related_to']
                if isinstance(related_ids, str):
                    related_ids = [related_ids]

                for related_id in related_ids:
                    await conn.execute(
                        f"""
                        INSERT INTO {self.schema}.relationships 
                        (from_id, to_id, type, metadata)
                        VALUES ($1, $2, $3, $4)
                        ON CONFLICT (from_id, to_id, type) DO NOTHING
                        """,
                        uuid.UUID(entry.id),
                        uuid.UUID(related_id),
                        'related_to',
                        json.dumps({})
                    )

        return entry.id

    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory entry from PostgreSQL."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                f"""
                SELECT id, type, content, metadata, timestamp, embedding, score, tags
                FROM {self.schema}.entries
                WHERE id = $1
                """,
                uuid.UUID(entry_id)
            )

            if row:
                return MemoryEntry(
                    id=str(row['id']),
                    type=MemoryType(row['type']),
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    timestamp=row['timestamp'],
                    embedding=list(row['embedding']) if row['embedding'] else None,
                    score=row['score'],
                    tags=list(row['tags']) if row['tags'] else []
                )

            return None

    async def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search for memory entries using PostgreSQL full-text search."""
        conditions = []
        params = []
        param_count = 0

        # Type filter
        if query.type:
            param_count += 1
            conditions.append(f"type = ${param_count}")
            params.append(query.type.value)

        # Tags filter
        if query.tags:
            param_count += 1
            conditions.append(f"tags @> ${param_count}")
            params.append(query.tags)

        # Time range filter
        if query.time_range:
            param_count += 1
            conditions.append(f"timestamp >= ${param_count}")
            params.append(query.time_range[0])

            param_count += 1
            conditions.append(f"timestamp <= ${param_count}")
            params.append(query.time_range[1])

        # Metadata filters using JSONB containment
        if query.metadata_filters:
            param_count += 1
            conditions.append(f"metadata @> ${param_count}")
            params.append(json.dumps(query.metadata_filters))

        # Full-text search
        if query.query and query.query.strip():
            param_count += 1
            conditions.append(f"search_vector @@ plainto_tsquery('english', ${param_count})")
            params.append(query.query)

        # Build WHERE clause
        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)

        # Execute search
        sql = f"""
            SELECT id, type, content, metadata, timestamp, embedding, score, tags
            FROM {self.schema}.entries
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT {query.limit}
        """

        entries = []
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(sql, *params)

            for row in rows:
                entry = MemoryEntry(
                    id=str(row['id']),
                    type=MemoryType(row['type']),
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    timestamp=row['timestamp'],
                    embedding=list(row['embedding']) if row['embedding'] else None,
                    score=row['score'],
                    tags=list(row['tags']) if row['tags'] else []
                )
                entries.append(entry)

        return entries

    async def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update memory entry in PostgreSQL."""
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
        if 'score' in updates:
            entry.score = updates['score']

        async with self.pool.acquire() as conn:
            result = await conn.execute(
                f"""
                UPDATE {self.schema}.entries
                SET content = $2, metadata = $3, tags = $4, score = $5
                WHERE id = $1
                """,
                uuid.UUID(entry_id),
                json.dumps(entry.content),
                json.dumps(entry.metadata),
                entry.tags,
                entry.score
            )

            return result.split()[-1] == '1'

    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry from PostgreSQL."""
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                f"DELETE FROM {self.schema}.entries WHERE id = $1",
                uuid.UUID(entry_id)
            )

            return result.split()[-1] == '1'

    async def clear(self, type: MemoryType | None = None) -> int:
        """Clear memory entries."""
        async with self.pool.acquire() as conn:
            if type:
                result = await conn.execute(
                    f"DELETE FROM {self.schema}.entries WHERE type = $1",
                    type.value
                )
            else:
                result = await conn.execute(
                    f"TRUNCATE TABLE {self.schema}.entries CASCADE"
                )

            # Extract count from result
            if result.startswith("DELETE"):
                return int(result.split()[-1])
            else:
                # For TRUNCATE, count all entries before clearing
                count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {self.schema}.entries"
                )
                return count or 0

    async def search_similar(
        self,
        embedding: list[float],
        limit: int = 10,
        threshold: float = 0.7
    ) -> list[MemoryEntry]:
        """Search for similar entries using vector similarity."""
        async with self.pool.acquire() as conn:
            # Use cosine similarity for vector search
            rows = await conn.fetch(
                f"""
                SELECT id, type, content, metadata, timestamp, embedding, score, tags,
                       1 - (embedding <=> $1::vector) as similarity
                FROM {self.schema}.entries
                WHERE embedding IS NOT NULL
                  AND 1 - (embedding <=> $1::vector) >= $2
                ORDER BY similarity DESC
                LIMIT $3
                """,
                embedding,
                threshold,
                limit
            )

            entries = []
            for row in rows:
                entry = MemoryEntry(
                    id=str(row['id']),
                    type=MemoryType(row['type']),
                    content=json.loads(row['content']),
                    metadata=json.loads(row['metadata']),
                    timestamp=row['timestamp'],
                    embedding=list(row['embedding']),
                    score=row['similarity'],  # Use similarity as score
                    tags=list(row['tags']) if row['tags'] else []
                )
                entries.append(entry)

            return entries

    async def get_relationships(
        self,
        entry_id: str,
        direction: str = "both"
    ) -> dict[str, list[dict[str, Any]]]:
        """Get relationships for an entry."""
        relationships = {}

        async with self.pool.acquire() as conn:
            if direction in ["out", "both"]:
                # Outgoing relationships
                rows = await conn.fetch(
                    f"""
                    SELECT r.type, r.to_id, r.metadata, e.type as target_type
                    FROM {self.schema}.relationships r
                    JOIN {self.schema}.entries e ON e.id = r.to_id
                    WHERE r.from_id = $1
                    """,
                    uuid.UUID(entry_id)
                )

                for row in rows:
                    rel_type = row['type']
                    if rel_type not in relationships:
                        relationships[rel_type] = []

                    relationships[rel_type].append({
                        'id': str(row['to_id']),
                        'type': row['target_type'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                    })

            if direction in ["in", "both"]:
                # Incoming relationships
                rows = await conn.fetch(
                    f"""
                    SELECT r.type, r.from_id, r.metadata, e.type as source_type
                    FROM {self.schema}.relationships r
                    JOIN {self.schema}.entries e ON e.id = r.from_id
                    WHERE r.to_id = $1
                    """,
                    uuid.UUID(entry_id)
                )

                for row in rows:
                    rel_type = f"inverse_{row['type']}"
                    if rel_type not in relationships:
                        relationships[rel_type] = []

                    relationships[rel_type].append({
                        'id': str(row['from_id']),
                        'type': row['source_type'],
                        'metadata': json.loads(row['metadata']) if row['metadata'] else {}
                    })

        return relationships

    async def get_stats(self) -> dict[str, Any]:
        """Get PostgreSQL memory statistics."""
        base_stats = await super().get_stats()

        if self._connected:
            async with self.pool.acquire() as conn:
                # Total entries
                total = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {self.schema}.entries"
                )

                # Entries by type
                rows = await conn.fetch(
                    f"""
                    SELECT type, COUNT(*) as count
                    FROM {self.schema}.entries
                    GROUP BY type
                    ORDER BY count DESC
                    """
                )

                type_counts = {row['type']: row['count'] for row in rows}

                # Total relationships
                rel_count = await conn.fetchval(
                    f"SELECT COUNT(*) FROM {self.schema}.relationships"
                )

                # Table sizes
                rows = await conn.fetch(
                    f"""
                    SELECT 
                        pg_size_pretty(pg_total_relation_size('{self.schema}.entries')) as entries_size,
                        pg_size_pretty(pg_total_relation_size('{self.schema}.relationships')) as relationships_size
                    """
                )

                sizes = rows[0] if rows else {}

                base_stats.update({
                    'total_entries': total,
                    'entries_by_type': type_counts,
                    'total_relationships': rel_count,
                    'table_sizes': {
                        'entries': sizes.get('entries_size', 'Unknown'),
                        'relationships': sizes.get('relationships_size', 'Unknown')
                    },
                    'schema': self.schema
                })

        return base_stats
