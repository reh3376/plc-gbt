#!/usr/bin/env python3
"""
Memory Adapters Demo
====================

Demonstrates using different memory system adapters.
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plc_orchestrator.memory.adapters import (
    MemoryEntry,
    MemoryQuery,
    MemoryType,
    Neo4jMemoryAdapter,
    PostgresMemoryAdapter,
    QdrantMemoryAdapter,
    RedisMemoryAdapter,
)


async def demo_redis_adapter():
    """Demo Redis memory adapter for caching."""
    print("\n=== Redis Memory Adapter Demo ===")

    # Initialize adapter
    config = {
        'url': os.getenv('REDIS_URL', 'redis://localhost:6379'),
        'ttl': 3600,  # 1 hour TTL
        'key_prefix': 'demo:'
    }

    adapter = RedisMemoryAdapter(config)

    try:
        # Connect
        await adapter.connect()
        print("✓ Connected to Redis")

        # Store some entries
        task_entry = MemoryEntry(
            id="task_001",
            type=MemoryType.TASK,
            content={
                "description": "Implement tank level control",
                "requirements": ["PID control", "Safety interlocks", "HMI"]
            },
            metadata={"project": "plc-control", "priority": "high"},
            timestamp=datetime.now(),
            tags=["control", "safety", "plc"]
        )

        await adapter.store(task_entry)
        print(f"✓ Stored task entry: {task_entry.id}")

        # Store code snippet
        code_entry = MemoryEntry(
            id="code_001",
            type=MemoryType.CODE,
            content={
                "code": """
def calculate_pid(setpoint, process_value, kp=1.0, ki=0.1, kd=0.05):
    error = setpoint - process_value
    # PID calculation logic here
    return output
""",
                "language": "python",
                "description": "PID controller implementation"
            },
            metadata={"related_to": ["task_001"]},
            timestamp=datetime.now(),
            tags=["pid", "control", "algorithm"]
        )

        await adapter.store(code_entry)
        print(f"✓ Stored code entry: {code_entry.id}")

        # Search by type
        query = MemoryQuery(
            query="control",
            type=MemoryType.TASK,
            limit=5
        )

        results = await adapter.search(query)
        print(f"\n✓ Found {len(results)} task entries")
        for entry in results:
            print(f"  - {entry.id}: {entry.content.get('description', 'N/A')}")

        # Search by tags
        tag_query = MemoryQuery(
            query="",
            tags=["control"],
            limit=10
        )

        tag_results = await adapter.search(tag_query)
        print(f"\n✓ Found {len(tag_results)} entries with 'control' tag")

        # Get statistics
        stats = await adapter.get_stats()
        print("\n✓ Redis Stats:")
        print(f"  - Total entries: {stats.get('total_entries', 0)}")
        print(f"  - Memory used: {stats.get('memory_used_mb', 0):.2f} MB")

    finally:
        await adapter.disconnect()
        print("\n✓ Disconnected from Redis")


async def demo_neo4j_adapter():
    """Demo Neo4j adapter for relationship tracking."""
    print("\n=== Neo4j Memory Adapter Demo ===")

    # Initialize adapter
    config = {
        'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'username': 'neo4j',
        'password': os.getenv('NEO4J_PASSWORD', 'password'),
        'database': 'neo4j'
    }

    # Skip if no password provided
    if config['password'] == 'password':
        print("⚠️  Skipping Neo4j demo (set NEO4J_PASSWORD environment variable)")
        return

    adapter = Neo4jMemoryAdapter(config)

    try:
        await adapter.connect()
        print("✓ Connected to Neo4j")

        # Create error entry
        error_entry = MemoryEntry(
            id="error_001",
            type=MemoryType.ERROR,
            content={
                "error": "ValueError: PID gains must be positive",
                "context": "During PID tuning validation",
                "stack_trace": "..."
            },
            metadata={"severity": "high"},
            timestamp=datetime.now(),
            tags=["validation", "pid", "error"]
        )

        await adapter.store(error_entry)
        print(f"✓ Stored error entry: {error_entry.id}")

        # Create solution entry
        solution_entry = MemoryEntry(
            id="solution_001",
            type=MemoryType.SOLUTION,
            content={
                "solution": "Add validation for PID gains",
                "code": "if kp <= 0 or ki <= 0 or kd <= 0: raise ValueError(...)"
            },
            metadata={"error_id": "error_001", "effectiveness": "high"},
            timestamp=datetime.now(),
            tags=["validation", "fix"]
        )

        await adapter.store(solution_entry)
        print(f"✓ Stored solution entry: {solution_entry.id}")

        # Find error-solution patterns
        patterns = await adapter.find_patterns("error_solution_pairs", limit=5)
        print(f"\n✓ Found {len(patterns)} error-solution patterns")

        # Get relationships
        relationships = await adapter.get_relationships("solution_001")
        print("\n✓ Relationships for solution_001:")
        for rel_type, targets in relationships.items():
            if targets:
                print(f"  - {rel_type}: {targets}")

    finally:
        await adapter.disconnect()
        print("\n✓ Disconnected from Neo4j")


async def demo_postgres_adapter():
    """Demo PostgreSQL adapter for structured storage."""
    print("\n=== PostgreSQL Memory Adapter Demo ===")

    # Initialize adapter
    config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'memory'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'schema': 'demo'
    }

    # Skip if no connection available
    if not config['password']:
        print("⚠️  Skipping PostgreSQL demo (set POSTGRES_PASSWORD environment variable)")
        return

    adapter = PostgresMemoryAdapter(config)

    try:
        await adapter.connect()
        print("✓ Connected to PostgreSQL")

        # Store pattern entry
        pattern_entry = MemoryEntry(
            id="pattern_001",
            type=MemoryType.PATTERN,
            content={
                "name": "Cascade Control",
                "description": "Master-slave control loop pattern",
                "use_cases": ["Temperature control", "Level control"],
                "implementation": "..."
            },
            metadata={"domain": "control_systems", "complexity": "medium"},
            timestamp=datetime.now(),
            tags=["pattern", "control", "cascade"]
        )

        await adapter.store(pattern_entry)
        print(f"✓ Stored pattern entry: {pattern_entry.id}")

        # Full-text search
        search_query = MemoryQuery(
            query="cascade control",
            limit=10
        )

        results = await adapter.search(search_query)
        print(f"\n✓ Full-text search found {len(results)} results")

        # Time-based search
        time_query = MemoryQuery(
            query="",
            time_range=(
                datetime.now() - timedelta(hours=1),
                datetime.now()
            ),
            limit=10
        )

        time_results = await adapter.search(time_query)
        print(f"✓ Found {len(time_results)} entries in last hour")

        # Get stats
        stats = await adapter.get_stats()
        print("\n✓ PostgreSQL Stats:")
        print(f"  - Total entries: {stats.get('total_entries', 0)}")
        print(f"  - Table sizes: {stats.get('table_sizes', {})}")

    finally:
        await adapter.disconnect()
        print("\n✓ Disconnected from PostgreSQL")


async def demo_qdrant_adapter():
    """Demo Qdrant adapter for vector search."""
    print("\n=== Qdrant Memory Adapter Demo ===")

    # Initialize adapter
    config = {
        'url': os.getenv('QDRANT_URL', 'http://localhost:6333'),
        'collection': 'demo_memory',
        'vector_size': 384,  # Using smaller vectors for demo
        'distance': 'Cosine'
    }

    adapter = QdrantMemoryAdapter(config)

    try:
        await adapter.connect()
        print("✓ Connected to Qdrant")

        # Create mock embeddings (normally from embedding model)
        import random

        def mock_embedding(text: str) -> list:
            # In real use, this would be from an embedding model
            random.seed(hash(text))
            return [random.random() for _ in range(384)]

        # Store context entry with embedding
        context_entry = MemoryEntry(
            id="context_001",
            type=MemoryType.CONTEXT,
            content={
                "description": "Industrial control system best practices",
                "key_points": [
                    "Always implement safety interlocks",
                    "Use redundant sensors for critical measurements",
                    "Implement proper alarm management"
                ]
            },
            metadata={"source": "IEC 61131", "version": "3.0"},
            timestamp=datetime.now(),
            embedding=mock_embedding("industrial control safety practices"),
            tags=["safety", "standards", "industrial"]
        )

        await adapter.store(context_entry)
        print(f"✓ Stored context entry with embedding: {context_entry.id}")

        # Search by vector similarity
        query_embedding = mock_embedding("safety interlocks in control systems")
        similar_entries = await adapter.search_by_vector(
            vector=query_embedding,
            limit=5,
            threshold=0.5
        )

        print(f"\n✓ Vector search found {len(similar_entries)} similar entries")
        for entry in similar_entries:
            print(f"  - {entry.id} (score: {entry.score:.3f}): {entry.content.get('description', 'N/A')}")

        # Get stats
        stats = await adapter.get_stats()
        print("\n✓ Qdrant Stats:")
        print(f"  - Total vectors: {stats.get('total_entries', 0)}")
        print(f"  - Vector dimension: {stats.get('vector_size', 0)}")
        print(f"  - Distance metric: {stats.get('distance_metric', 'Unknown')}")

    except Exception as e:
        print(f"⚠️  Qdrant demo error: {str(e)}")
        print("   (Make sure Qdrant is running on localhost:6333)")
    finally:
        await adapter.disconnect()
        print("\n✓ Disconnected from Qdrant")


async def main():
    """Run all adapter demos."""
    print("Memory System Adapters Demo")
    print("===========================")
    print("\nThis demo shows how to use different memory backends:")
    print("- Redis: Fast caching and session storage")
    print("- Neo4j: Graph-based relationship tracking")
    print("- PostgreSQL: Structured storage with full-text search")
    print("- Qdrant: Vector storage for semantic search")

    # Run demos
    await demo_redis_adapter()
    await demo_neo4j_adapter()
    await demo_postgres_adapter()
    await demo_qdrant_adapter()

    print("\n✓ All demos completed!")
    print("\nTo use these adapters in production:")
    print("1. Install the required packages:")
    print("   pip install redis[hiredis] neo4j asyncpg qdrant-client")
    print("2. Configure your backend services")
    print("3. Set appropriate environment variables")
    print("4. Use adapters in your AI Task Orchestrator workflows")


if __name__ == "__main__":
    asyncio.run(main())
