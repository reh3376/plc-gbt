"""
Neo4j Memory Adapter
====================

Graph-based memory storage for relationship tracking.
"""

import json
import uuid
from datetime import datetime
from typing import Any

from .base import MemoryAdapter, MemoryEntry, MemoryQuery, MemoryType

try:
    from neo4j import AsyncGraphDatabase
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    AsyncGraphDatabase = None


class Neo4jMemoryAdapter(MemoryAdapter):
    """Neo4j adapter for graph-based memory storage."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Neo4j adapter.
        
        Config options:
            uri: Neo4j URI (default: bolt://localhost:7687)
            username: Username (default: neo4j)
            password: Password (required)
            database: Database name (default: neo4j)
        """
        super().__init__(config)

        if not HAS_NEO4J:
            raise ImportError(
                "Neo4j package not installed. Install with: pip install neo4j"
            )

        self.uri = config.get('uri', 'bolt://localhost:7687')
        self.username = config.get('username', 'neo4j')
        self.password = config.get('password')
        self.database = config.get('database', 'neo4j')
        self.driver = None

        if not self.password:
            raise ValueError("Neo4j password is required in config")

    async def connect(self) -> None:
        """Connect to Neo4j."""
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.username, self.password)
        )
        # Test connection
        async with self.driver.session(database=self.database) as session:
            await session.run("RETURN 1")

        # Create indices for better performance
        async with self.driver.session(database=self.database) as session:
            await session.run(
                "CREATE INDEX memory_id IF NOT EXISTS FOR (m:Memory) ON (m.id)"
            )
            await session.run(
                "CREATE INDEX memory_type IF NOT EXISTS FOR (m:Memory) ON (m.type)"
            )
            await session.run(
                "CREATE INDEX memory_timestamp IF NOT EXISTS FOR (m:Memory) ON (m.timestamp)"
            )

        self._connected = True

    async def disconnect(self) -> None:
        """Disconnect from Neo4j."""
        if self.driver:
            await self.driver.close()
            self._connected = False

    def _entry_to_node(self, entry: MemoryEntry) -> dict[str, Any]:
        """Convert memory entry to Neo4j node properties."""
        return {
            'id': entry.id,
            'type': entry.type.value,
            'content': json.dumps(entry.content),
            'metadata': json.dumps(entry.metadata),
            'timestamp': entry.timestamp.isoformat(),
            'embedding': json.dumps(entry.embedding) if entry.embedding else None,
            'score': entry.score,
            'tags': entry.tags
        }

    def _node_to_entry(self, node: dict[str, Any]) -> MemoryEntry:
        """Convert Neo4j node to memory entry."""
        return MemoryEntry(
            id=node['id'],
            type=MemoryType(node['type']),
            content=json.loads(node['content']),
            metadata=json.loads(node['metadata']),
            timestamp=datetime.fromisoformat(node['timestamp']),
            embedding=json.loads(node['embedding']) if node['embedding'] else None,
            score=node.get('score'),
            tags=node.get('tags', [])
        )

    async def store(self, entry: MemoryEntry) -> str:
        """Store memory entry as Neo4j node."""
        if not entry.id:
            entry.id = str(uuid.uuid4())

        node_props = self._entry_to_node(entry)

        async with self.driver.session(database=self.database) as session:
            # Create node
            result = await session.run(
                """
                CREATE (m:Memory $props)
                RETURN m
                """,
                props=node_props
            )

            # Create relationships based on content
            if 'related_to' in entry.metadata:
                related_ids = entry.metadata['related_to']
                if isinstance(related_ids, str):
                    related_ids = [related_ids]

                for related_id in related_ids:
                    await session.run(
                        """
                        MATCH (m1:Memory {id: $id1}), (m2:Memory {id: $id2})
                        CREATE (m1)-[:RELATED_TO]->(m2)
                        """,
                        id1=entry.id,
                        id2=related_id
                    )

            # Create relationships for code dependencies
            if entry.type == MemoryType.CODE and 'imports' in entry.content:
                for import_name in entry.content['imports']:
                    await session.run(
                        """
                        MATCH (m:Memory {id: $id})
                        MERGE (i:Import {name: $import_name})
                        CREATE (m)-[:IMPORTS]->(i)
                        """,
                        id=entry.id,
                        import_name=import_name
                    )

            # Create relationships for error-solution pairs
            if entry.type == MemoryType.SOLUTION and 'error_id' in entry.metadata:
                await session.run(
                    """
                    MATCH (e:Memory {id: $error_id}), (s:Memory {id: $solution_id})
                    CREATE (e)-[:SOLVED_BY]->(s)
                    """,
                    error_id=entry.metadata['error_id'],
                    solution_id=entry.id
                )

        return entry.id

    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """Retrieve memory entry from Neo4j."""
        async with self.driver.session(database=self.database) as session:
            result = await session.run(
                """
                MATCH (m:Memory {id: $id})
                RETURN m
                """,
                id=entry_id
            )

            record = await result.single()
            if record:
                node = dict(record['m'])
                return self._node_to_entry(node)

            return None

    async def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """Search for memory entries using Cypher queries."""
        cypher_query = "MATCH (m:Memory) WHERE 1=1"
        params = {}

        # Add type filter
        if query.type:
            cypher_query += " AND m.type = $type"
            params['type'] = query.type.value

        # Add tag filter
        if query.tags:
            cypher_query += " AND ALL(tag IN $tags WHERE tag IN m.tags)"
            params['tags'] = query.tags

        # Add time range filter
        if query.time_range:
            cypher_query += " AND m.timestamp >= $start_time AND m.timestamp <= $end_time"
            params['start_time'] = query.time_range[0].isoformat()
            params['end_time'] = query.time_range[1].isoformat()

        # Add metadata filters
        if query.metadata_filters:
            for key, value in query.metadata_filters.items():
                # Use JSON contains for metadata filtering
                cypher_query += f" AND m.metadata CONTAINS '\"{key}\":\"{value}\"'"

        # Add text search if query text provided
        if query.query and query.query.strip():
            cypher_query += " AND (m.content CONTAINS $search_text OR ANY(tag IN m.tags WHERE tag CONTAINS $search_text))"
            params['search_text'] = query.query

        # Add ordering and limit
        cypher_query += " RETURN m ORDER BY m.timestamp DESC"
        if query.limit:
            cypher_query += f" LIMIT {query.limit}"

        entries = []
        async with self.driver.session(database=self.database) as session:
            result = await session.run(cypher_query, **params)

            async for record in result:
                node = dict(record['m'])
                entry = self._node_to_entry(node)
                entries.append(entry)

        return entries

    async def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """Update memory entry in Neo4j."""
        async with self.driver.session(database=self.database) as session:
            # Get current entry
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

            # Update node
            node_props = self._entry_to_node(entry)
            result = await session.run(
                """
                MATCH (m:Memory {id: $id})
                SET m = $props
                RETURN m
                """,
                id=entry_id,
                props=node_props
            )

            record = await result.single()
            return record is not None

    async def delete(self, entry_id: str) -> bool:
        """Delete memory entry and its relationships."""
        async with self.driver.session(database=self.database) as session:
            result = await session.run(
                """
                MATCH (m:Memory {id: $id})
                DETACH DELETE m
                RETURN COUNT(m) as deleted
                """,
                id=entry_id
            )

            record = await result.single()
            return record['deleted'] > 0

    async def clear(self, type: MemoryType | None = None) -> int:
        """Clear memory entries."""
        async with self.driver.session(database=self.database) as session:
            if type:
                # Clear specific type
                result = await session.run(
                    """
                    MATCH (m:Memory {type: $type})
                    DETACH DELETE m
                    RETURN COUNT(m) as deleted
                    """,
                    type=type.value
                )
            else:
                # Clear all memories
                result = await session.run(
                    """
                    MATCH (m:Memory)
                    DETACH DELETE m
                    RETURN COUNT(m) as deleted
                    """
                )

            record = await result.single()
            return record['deleted']

    async def get_relationships(self, entry_id: str) -> dict[str, list[str]]:
        """Get all relationships for a memory entry."""
        relationships = {
            'related_to': [],
            'solved_by': [],
            'solves': [],
            'imports': [],
            'imported_by': []
        }

        async with self.driver.session(database=self.database) as session:
            # Get outgoing relationships
            result = await session.run(
                """
                MATCH (m:Memory {id: $id})-[r]->(target)
                RETURN type(r) as rel_type, 
                       CASE WHEN target:Memory THEN target.id 
                            WHEN target:Import THEN target.name 
                            ELSE null END as target_id
                """,
                id=entry_id
            )

            async for record in result:
                rel_type = record['rel_type'].lower()
                target_id = record['target_id']
                if target_id:
                    if rel_type == 'related_to':
                        relationships['related_to'].append(target_id)
                    elif rel_type == 'solved_by':
                        relationships['solved_by'].append(target_id)
                    elif rel_type == 'imports':
                        relationships['imports'].append(target_id)

            # Get incoming relationships
            result = await session.run(
                """
                MATCH (source:Memory)-[r]->(m:Memory {id: $id})
                RETURN type(r) as rel_type, source.id as source_id
                """,
                id=entry_id
            )

            async for record in result:
                rel_type = record['rel_type'].lower()
                source_id = record['source_id']
                if rel_type == 'solved_by':
                    relationships['solves'].append(source_id)
                elif rel_type == 'imports':
                    relationships['imported_by'].append(source_id)

        return relationships

    async def find_patterns(self, pattern_type: str, limit: int = 10) -> list[dict[str, Any]]:
        """Find common patterns in the memory graph."""
        patterns = []

        async with self.driver.session(database=self.database) as session:
            if pattern_type == "error_solution_pairs":
                # Find error-solution patterns
                result = await session.run(
                    """
                    MATCH (e:Memory {type: 'error'})-[:SOLVED_BY]->(s:Memory {type: 'solution'})
                    RETURN e, s
                    ORDER BY e.timestamp DESC
                    LIMIT $limit
                    """,
                    limit=limit
                )

                async for record in result:
                    patterns.append({
                        'type': 'error_solution',
                        'error': self._node_to_entry(dict(record['e'])),
                        'solution': self._node_to_entry(dict(record['s']))
                    })

            elif pattern_type == "code_clusters":
                # Find clusters of related code
                result = await session.run(
                    """
                    MATCH (c1:Memory {type: 'code'})-[:RELATED_TO]-(c2:Memory {type: 'code'})
                    WITH c1, collect(c2) as related
                    WHERE size(related) >= 3
                    RETURN c1, related[0..5] as sample_related
                    LIMIT $limit
                    """,
                    limit=limit
                )

                async for record in result:
                    patterns.append({
                        'type': 'code_cluster',
                        'central': self._node_to_entry(dict(record['c1'])),
                        'related': [
                            self._node_to_entry(dict(node))
                            for node in record['sample_related']
                        ]
                    })

        return patterns

    async def get_stats(self) -> dict[str, Any]:
        """Get Neo4j memory statistics."""
        base_stats = await super().get_stats()

        if self._connected:
            async with self.driver.session(database=self.database) as session:
                # Count total nodes
                result = await session.run(
                    "MATCH (m:Memory) RETURN COUNT(m) as total"
                )
                record = await result.single()
                total = record['total']

                # Count by type
                result = await session.run(
                    """
                    MATCH (m:Memory)
                    RETURN m.type as type, COUNT(m) as count
                    ORDER BY count DESC
                    """
                )

                type_counts = {}
                async for record in result:
                    type_counts[record['type']] = record['count']

                # Count relationships
                result = await session.run(
                    """
                    MATCH ()-[r]->()
                    RETURN type(r) as rel_type, COUNT(r) as count
                    """
                )

                rel_counts = {}
                async for record in result:
                    rel_counts[record['rel_type']] = record['count']

                base_stats.update({
                    'total_entries': total,
                    'entries_by_type': type_counts,
                    'relationships': rel_counts,
                    'database': self.database
                })

        return base_stats
