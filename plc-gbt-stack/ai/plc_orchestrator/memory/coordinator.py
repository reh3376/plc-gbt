"""Memory system coordinator for multi-database integration."""

import asyncio
from dataclasses import dataclass
from typing import Any, Protocol

from plc_orchestrator.utils.enums import MemoryStrategy
from plc_orchestrator.utils.errors import MemorySystemError
from plc_orchestrator.utils.logging import get_logger


@dataclass
class MemoryRequest:
    """Request for memory system operations."""

    operation_type: str  # query, store, update, delete
    data_type: str  # task, code, pattern, documentation
    content: Any
    routing_strategy: MemoryStrategy = MemoryStrategy.BALANCED
    metadata: dict[str, Any] | None = None


@dataclass
class MemoryResponse:
    """Response from memory system operations."""

    success: bool
    data: Any
    source: str  # Which database provided the response
    metadata: dict[str, Any]


class MemoryAdapter(Protocol):
    """Protocol for memory system adapters."""

    async def query(self, request: MemoryRequest) -> MemoryResponse:
        """Query the memory system."""
        ...

    async def store(self, request: MemoryRequest) -> MemoryResponse:
        """Store data in the memory system."""
        ...

    async def close(self) -> None:
        """Close connections."""
        ...


class MemoryCoordinator:
    """
    Coordinates operations across multiple memory databases.

    Supports Redis (speed), Neo4j (relationships), PostgreSQL (persistence),
    and Qdrant (vector similarity).
    """

    def __init__(self, config: dict[str, Any]) -> None:
        """
        Initialize memory coordinator.

        Args:
            config: Memory system configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.adapters: dict[str, MemoryAdapter] = {}

        # Initialize adapters
        self._initialize_adapters()

    def _initialize_adapters(self) -> None:
        """Initialize database adapters based on configuration."""
        # Redis adapter
        if self.config.get("redis", {}).get("enabled"):
            try:
                from plc_orchestrator.memory.adapters.redis import RedisAdapter

                self.adapters["redis"] = RedisAdapter(self.config["redis"])
                self.logger.info("Redis adapter initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Redis adapter: {e}")

        # Neo4j adapter
        if self.config.get("neo4j", {}).get("enabled"):
            try:
                from plc_orchestrator.memory.adapters.neo4j import Neo4jAdapter

                self.adapters["neo4j"] = Neo4jAdapter(self.config["neo4j"])
                self.logger.info("Neo4j adapter initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Neo4j adapter: {e}")

        # PostgreSQL adapter
        if self.config.get("postgresql", {}).get("enabled"):
            try:
                from plc_orchestrator.memory.adapters.postgresql import PostgreSQLAdapter

                self.adapters["postgresql"] = PostgreSQLAdapter(self.config["postgresql"])
                self.logger.info("PostgreSQL adapter initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize PostgreSQL adapter: {e}")

        # Qdrant adapter
        if self.config.get("qdrant", {}).get("enabled"):
            try:
                from plc_orchestrator.memory.adapters.qdrant import QdrantAdapter

                self.adapters["qdrant"] = QdrantAdapter(self.config["qdrant"])
                self.logger.info("Qdrant adapter initialized")
            except Exception as e:
                self.logger.error(f"Failed to initialize Qdrant adapter: {e}")

    async def query(self, request: MemoryRequest) -> MemoryResponse:
        """
        Query memory system with intelligent routing.

        Args:
            request: Memory request

        Returns:
            Memory response

        Raises:
            MemorySystemError: If query fails
        """
        if not self.adapters:
            raise MemorySystemError("No memory adapters available")

        # Select adapter based on strategy
        adapter_name = self._select_adapter(request)
        adapter = self.adapters.get(adapter_name)

        if not adapter:
            raise MemorySystemError(
                f"Selected adapter '{adapter_name}' not available", operation="query"
            )

        try:
            self.logger.info(
                f"Querying {adapter_name}",
                extra={"operation_type": request.operation_type, "data_type": request.data_type},
            )

            response = await adapter.query(request)
            response.source = adapter_name

            return response

        except Exception as e:
            self.logger.error(f"Query failed in {adapter_name}: {e}")

            # Try fallback adapter
            fallback = self._get_fallback_adapter(adapter_name)
            if fallback:
                self.logger.info(f"Trying fallback adapter: {fallback}")
                return await self.adapters[fallback].query(request)
            else:
                raise MemorySystemError(
                    f"Query failed: {e}", database=adapter_name, operation="query"
                )

    async def store(self, request: MemoryRequest) -> MemoryResponse:
        """
        Store data in appropriate memory systems.

        Args:
            request: Memory request

        Returns:
            Memory response
        """
        if not self.adapters:
            raise MemorySystemError("No memory adapters available")

        # Determine which adapters to use for storage
        target_adapters = self._select_storage_adapters(request)

        results = []
        errors = []

        # Store in each target adapter
        for adapter_name in target_adapters:
            adapter = self.adapters.get(adapter_name)
            if adapter:
                try:
                    response = await adapter.store(request)
                    response.source = adapter_name
                    results.append(response)
                except Exception as e:
                    errors.append(f"{adapter_name}: {e}")

        if not results and errors:
            raise MemorySystemError(
                f"Storage failed in all adapters: {', '.join(errors)}", operation="store"
            )

        # Return combined response
        return MemoryResponse(
            success=len(results) > 0,
            data={"stored_in": [r.source for r in results]},
            source="coordinator",
            metadata={"adapters_used": len(results), "errors": errors},
        )

    async def multi_query(self, request: MemoryRequest) -> dict[str, MemoryResponse]:
        """
        Query multiple adapters in parallel.

        Args:
            request: Memory request

        Returns:
            Dictionary of responses by adapter name
        """
        tasks = {}

        for name, adapter in self.adapters.items():
            tasks[name] = adapter.query(request)

        # Execute queries in parallel
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        responses = {}
        for name, result in zip(tasks.keys(), results, strict=False):
            if isinstance(result, Exception):
                self.logger.error(f"Query failed in {name}: {result}")
                responses[name] = MemoryResponse(
                    success=False, data=None, source=name, metadata={"error": str(result)}
                )
            else:
                result.source = name
                responses[name] = result

        return responses

    def _select_adapter(self, request: MemoryRequest) -> str:
        """Select appropriate adapter based on request and strategy."""
        strategy = request.routing_strategy
        data_type = request.data_type

        # Define strategy mappings
        strategy_handlers = {
            MemoryStrategy.SPEED_OPTIMIZED: self._select_speed_optimized,
            MemoryStrategy.ACCURACY_OPTIMIZED: self._select_accuracy_optimized,
            MemoryStrategy.COST_OPTIMIZED: self._select_cost_optimized,
        }

        # Try strategy-specific selection
        handler = strategy_handlers.get(strategy)
        if handler:
            selected = handler(data_type)
            if selected:
                return selected

        # Fall back to balanced routing
        return self._select_balanced(data_type)

    def _select_speed_optimized(self, data_type: str) -> str | None:
        """Select adapter for speed-optimized strategy."""
        if "redis" in self.adapters:
            return "redis"
        return None

    def _select_accuracy_optimized(self, data_type: str) -> str | None:
        """Select adapter for accuracy-optimized strategy."""
        if data_type in ["relationship", "pattern"] and "neo4j" in self.adapters:
            return "neo4j"
        elif data_type == "similarity" and "qdrant" in self.adapters:
            return "qdrant"
        return None

    def _select_cost_optimized(self, data_type: str) -> str | None:
        """Select adapter for cost-optimized strategy."""
        if "postgresql" in self.adapters:
            return "postgresql"
        return None

    def _select_balanced(self, data_type: str) -> str:
        """Select adapter for balanced strategy."""
        # Data type specific routing
        data_type_mapping = {
            "task": "postgresql",
            "code": "qdrant",
            "pattern": "neo4j",
        }

        adapter = data_type_mapping.get(data_type)
        if adapter and adapter in self.adapters:
            return adapter

        # Default to Redis if available
        if "redis" in self.adapters:
            return "redis"

        # Return first available adapter
        return next(iter(self.adapters.keys()))

    def _select_storage_adapters(self, request: MemoryRequest) -> list[str]:
        """Select adapters for data storage."""
        adapters = []
        data_type = request.data_type

        # Always store in persistent storage if available
        if "postgresql" in self.adapters:
            adapters.append("postgresql")

        # Store relationships in Neo4j
        if data_type in ["relationship", "pattern"] and "neo4j" in self.adapters:
            adapters.append("neo4j")

        # Store vectors in Qdrant
        if data_type == "code" and "qdrant" in self.adapters:
            adapters.append("qdrant")

        # Cache in Redis for fast retrieval
        if "redis" in self.adapters and request.metadata and request.metadata.get("cache", True):
            adapters.append("redis")

        return list(set(adapters))  # Remove duplicates

    def _get_fallback_adapter(self, failed_adapter: str) -> str | None:
        """Get fallback adapter for failed operations."""
        fallback_map = {
            "redis": "postgresql",
            "neo4j": "postgresql",
            "qdrant": "postgresql",
            "postgresql": "redis",
        }

        fallback = fallback_map.get(failed_adapter)
        if fallback and fallback in self.adapters:
            return fallback

        # Return any available adapter except the failed one
        for name in self.adapters:
            if name != failed_adapter:
                return name

        return None

    async def close(self) -> None:
        """Close all adapter connections."""
        close_tasks = []

        for name, adapter in self.adapters.items():
            self.logger.info(f"Closing {name} adapter")
            close_tasks.append(adapter.close())

        await asyncio.gather(*close_tasks, return_exceptions=True)
        self.logger.info("All memory adapters closed")
