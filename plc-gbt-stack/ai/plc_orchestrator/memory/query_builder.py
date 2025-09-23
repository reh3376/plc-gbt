"""Query builder for memory system operations."""

from typing import Any

from plc_orchestrator.memory.coordinator import MemoryRequest
from plc_orchestrator.utils.enums import MemoryStrategy
from plc_orchestrator.utils.helpers import extract_keywords


class QueryBuilder:
    """Builds queries for the memory system."""

    @staticmethod
    def build_task_query(
        task_description: str, limit: int = 10, strategy: MemoryStrategy = MemoryStrategy.BALANCED
    ) -> MemoryRequest:
        """
        Build a query to find similar tasks.

        Args:
            task_description: Task description to search for
            limit: Maximum results
            strategy: Routing strategy

        Returns:
            Memory request
        """
        keywords = extract_keywords(task_description)

        return MemoryRequest(
            operation_type="query",
            data_type="task",
            content={"description": task_description, "keywords": keywords, "limit": limit},
            routing_strategy=strategy,
            metadata={"query_type": "similarity", "include_patterns": True},
        )

    @staticmethod
    def build_code_query(
        code_pattern: str, language: str = "python", limit: int = 5
    ) -> MemoryRequest:
        """
        Build a query to find similar code patterns.

        Args:
            code_pattern: Code pattern to search for
            language: Programming language
            limit: Maximum results

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="query",
            data_type="code",
            content={"pattern": code_pattern, "language": language, "limit": limit},
            routing_strategy=MemoryStrategy.ACCURACY_OPTIMIZED,
            metadata={"query_type": "vector_similarity", "threshold": 0.7},
        )

    @staticmethod
    def build_relationship_query(
        entity: str, relationship_type: str | None = None, depth: int = 2
    ) -> MemoryRequest:
        """
        Build a query to find relationships.

        Args:
            entity: Entity to find relationships for
            relationship_type: Optional relationship type filter
            depth: Graph traversal depth

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="query",
            data_type="relationship",
            content={"entity": entity, "relationship_type": relationship_type, "depth": depth},
            routing_strategy=MemoryStrategy.ACCURACY_OPTIMIZED,
            metadata={"query_type": "graph_traversal", "include_properties": True},
        )

    @staticmethod
    def build_pattern_query(pattern_type: str, context: str | None = None) -> MemoryRequest:
        """
        Build a query to find design patterns.

        Args:
            pattern_type: Type of pattern (e.g., "error_handling", "api_design")
            context: Optional context

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="query",
            data_type="pattern",
            content={"pattern_type": pattern_type, "context": context},
            routing_strategy=MemoryStrategy.BALANCED,
            metadata={"query_type": "pattern_match", "include_examples": True},
        )

    @staticmethod
    def build_store_task_request(
        task_id: str,
        task_description: str,
        task_analysis: dict[str, Any],
        implementation: str | None = None,
    ) -> MemoryRequest:
        """
        Build a request to store task information.

        Args:
            task_id: Unique task ID
            task_description: Task description
            task_analysis: Analysis results
            implementation: Optional implementation code

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="store",
            data_type="task",
            content={
                "task_id": task_id,
                "description": task_description,
                "analysis": task_analysis,
                "implementation": implementation,
                "timestamp": None,  # Will be set by adapter
            },
            routing_strategy=MemoryStrategy.BALANCED,
            metadata={
                "cache": True,
                "index_for_search": True,
                "ttl": 86400 * 30,  # 30 days
            },
        )

    @staticmethod
    def build_store_code_request(
        code_id: str, code_content: str, language: str, metadata: dict[str, Any]
    ) -> MemoryRequest:
        """
        Build a request to store code.

        Args:
            code_id: Unique code ID
            code_content: Code content
            language: Programming language
            metadata: Additional metadata

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="store",
            data_type="code",
            content={
                "code_id": code_id,
                "content": code_content,
                "language": language,
                "metadata": metadata,
            },
            routing_strategy=MemoryStrategy.BALANCED,
            metadata={"generate_embeddings": True, "extract_functions": True, "cache": True},
        )

    @staticmethod
    def build_update_request(
        data_type: str, identifier: str, updates: dict[str, Any]
    ) -> MemoryRequest:
        """
        Build an update request.

        Args:
            data_type: Type of data to update
            identifier: Unique identifier
            updates: Fields to update

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="update",
            data_type=data_type,
            content={"identifier": identifier, "updates": updates},
            routing_strategy=MemoryStrategy.BALANCED,
            metadata={"partial_update": True, "update_timestamp": True},
        )

    @staticmethod
    def build_delete_request(
        data_type: str, identifier: str, cascade: bool = False
    ) -> MemoryRequest:
        """
        Build a delete request.

        Args:
            data_type: Type of data to delete
            identifier: Unique identifier
            cascade: Whether to cascade delete related data

        Returns:
            Memory request
        """
        return MemoryRequest(
            operation_type="delete",
            data_type=data_type,
            content={"identifier": identifier},
            routing_strategy=MemoryStrategy.BALANCED,
            metadata={"cascade": cascade, "soft_delete": False},
        )
