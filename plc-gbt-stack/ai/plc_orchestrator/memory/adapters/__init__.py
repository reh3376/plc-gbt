"""
Memory System Adapters
=====================

This module provides adapters for various memory backends:
- Redis: Fast caching and session storage
- Neo4j: Graph-based memory for relationships
- PostgreSQL: Relational storage for structured data
- Qdrant: Vector storage for semantic search
"""

from .base import MemoryAdapter, MemoryEntry, MemoryQuery
from .neo4j_adapter import Neo4jMemoryAdapter
from .postgres_adapter import PostgresMemoryAdapter
from .qdrant_adapter import QdrantMemoryAdapter
from .redis_adapter import RedisMemoryAdapter

__all__ = [
    'MemoryAdapter',
    'MemoryEntry',
    'MemoryQuery',
    'RedisMemoryAdapter',
    'Neo4jMemoryAdapter',
    'PostgresMemoryAdapter',
    'QdrantMemoryAdapter'
]
