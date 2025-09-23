"""
Base Memory Adapter Interface
=============================

Defines the contract for all memory system adapters.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class MemoryType(Enum):
    """Types of memory entries."""
    TASK = "task"
    CODE = "code"
    ERROR = "error"
    SOLUTION = "solution"
    PATTERN = "pattern"
    CONTEXT = "context"
    RELATIONSHIP = "relationship"


@dataclass
class MemoryEntry:
    """Represents a single memory entry."""
    id: str
    type: MemoryType
    content: dict[str, Any]
    metadata: dict[str, Any]
    timestamp: datetime
    embedding: list[float] | None = None
    score: float | None = None
    tags: list[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class MemoryQuery:
    """Query parameters for memory search."""
    query: str
    type: MemoryType | None = None
    tags: list[str] | None = None
    limit: int = 10
    threshold: float = 0.7
    time_range: tuple[datetime, datetime] | None = None
    metadata_filters: dict[str, Any] | None = None


class MemoryAdapter(ABC):
    """Base interface for memory system adapters."""

    def __init__(self, config: dict[str, Any]):
        """Initialize adapter with configuration."""
        self.config = config
        self._connected = False

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the memory backend."""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to the memory backend."""
        pass

    @abstractmethod
    async def store(self, entry: MemoryEntry) -> str:
        """
        Store a memory entry.
        
        Args:
            entry: Memory entry to store
            
        Returns:
            ID of the stored entry
        """
        pass

    @abstractmethod
    async def retrieve(self, entry_id: str) -> MemoryEntry | None:
        """
        Retrieve a specific memory entry by ID.
        
        Args:
            entry_id: ID of the entry to retrieve
            
        Returns:
            Memory entry if found, None otherwise
        """
        pass

    @abstractmethod
    async def search(self, query: MemoryQuery) -> list[MemoryEntry]:
        """
        Search for memory entries matching the query.
        
        Args:
            query: Search parameters
            
        Returns:
            List of matching memory entries
        """
        pass

    @abstractmethod
    async def update(self, entry_id: str, updates: dict[str, Any]) -> bool:
        """
        Update an existing memory entry.
        
        Args:
            entry_id: ID of the entry to update
            updates: Fields to update
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """
        Delete a memory entry.
        
        Args:
            entry_id: ID of the entry to delete
            
        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    async def clear(self, type: MemoryType | None = None) -> int:
        """
        Clear memory entries.
        
        Args:
            type: Optional type filter, clears all if None
            
        Returns:
            Number of entries cleared
        """
        pass

    async def batch_store(self, entries: list[MemoryEntry]) -> list[str]:
        """
        Store multiple memory entries in batch.
        
        Args:
            entries: List of memory entries to store
            
        Returns:
            List of stored entry IDs
        """
        ids = []
        for entry in entries:
            entry_id = await self.store(entry)
            ids.append(entry_id)
        return ids

    async def get_stats(self) -> dict[str, Any]:
        """
        Get statistics about the memory store.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "adapter": self.__class__.__name__,
            "connected": self._connected,
            "config": {k: v for k, v in self.config.items() if k != "password"}
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        import asyncio
        if self._connected:
            asyncio.create_task(self.disconnect())

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
