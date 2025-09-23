#!/usr/bin/env python3
"""
Memory system CRUD operations examples.

This example demonstrates:
1. Storing task analysis results
2. Querying similar tasks
3. Updating task outcomes
4. Managing memory lifecycle
"""

import asyncio
from datetime import datetime
from typing import Any

from plc_orchestrator import create_orchestrator
from plc_orchestrator.memory import MemoryRequest
from plc_orchestrator.utils.enums import MemoryStrategy


class MemoryCRUDExamples:
    """Examples for memory system CRUD operations."""

    def __init__(self):
        """Initialize orchestrator with memory enabled."""
        self.orchestrator = create_orchestrator(
            enable_memory=True,
            redis_url="redis://localhost:6379/0",
            neo4j_uri="bolt://localhost:7687",
            postgres_dsn="postgresql://user:pass@localhost:5432/orchestrator",
        )
        self.memory = self.orchestrator.memory_coordinator

    async def example_store_task(self) -> str:
        """Example: Store a task analysis in memory."""
        print("\n" + "=" * 60)
        print("Example 1: Store Task Analysis")
        print("=" * 60)

        # Analyze a task
        task_description = "Create REST API with authentication and rate limiting"
        analysis = self.orchestrator.analyze_task(task_description)

        # Prepare data for storage
        task_data = {
            "task_id": analysis.task_id,
            "description": task_description,
            "analysis": {
                "complexity": analysis.complexity,
                "requirements": analysis.requirements,
                "risks": analysis.risks,
                "estimated_hours": analysis.estimated_effort["hours"],
                "domain_tags": analysis.domain_tags,
            },
            "timestamp": datetime.now().isoformat(),
            "status": "analyzed",
        }

        # Store in memory system
        print(f"\nStoring task: {analysis.task_id}")
        success = await self.memory.store_memory(
            data=task_data,
            metadata={
                "type": "task_analysis",
                "complexity": analysis.complexity,
                "tags": analysis.domain_tags,
            },
            routing_strategy=MemoryStrategy.BALANCED,
        )

        print(f"Storage result: {'Success' if success else 'Failed'}")
        return analysis.task_id

    async def example_query_similar_tasks(self, reference_task: str) -> list[dict[str, Any]]:
        """Example: Query for similar tasks."""
        print("\n" + "=" * 60)
        print("Example 2: Query Similar Tasks")
        print("=" * 60)

        # Create query request
        request = MemoryRequest(
            operation="query",
            data_type="task",
            query={"description": reference_task, "similarity_threshold": 0.7, "limit": 5},
            metadata={"include_analysis": True},
        )

        print(f"\nSearching for tasks similar to: '{reference_task[:50]}...'")

        # Execute query
        response = await self.memory.query_memory(request)

        if response.success and response.data:
            tasks = response.data.get("results", [])
            print(f"\nFound {len(tasks)} similar tasks:")

            for i, task in enumerate(tasks, 1):
                print(f"\n  {i}. Task ID: {task.get('task_id', 'N/A')}")
                print(f"     Description: {task.get('description', 'N/A')[:60]}...")
                print(f"     Complexity: {task.get('analysis', {}).get('complexity', 'N/A')}")
                print(f"     Similarity: {task.get('similarity_score', 0):.2f}")

            return tasks
        else:
            print("No similar tasks found")
            return []

    async def example_update_task_outcome(self, task_id: str, validation_passed: bool):
        """Example: Update task with validation outcome."""
        print("\n" + "=" * 60)
        print("Example 3: Update Task Outcome")
        print("=" * 60)

        # Prepare update data
        update_data = {
            "task_id": task_id,
            "validation": {
                "passed": validation_passed,
                "timestamp": datetime.now().isoformat(),
                "score": 95 if validation_passed else 65,
            },
            "status": "completed" if validation_passed else "needs_revision",
        }

        print(f"\nUpdating task {task_id}:")
        print(f"  - Validation: {'Passed' if validation_passed else 'Failed'}")
        print(f"  - New Status: {update_data['status']}")

        # Store update
        success = await self.memory.store_memory(
            data=update_data, metadata={"type": "task_update", "operation": "validation_outcome"}
        )

        print(f"Update result: {'Success' if success else 'Failed'}")

    async def example_batch_operations(self):
        """Example: Perform batch memory operations."""
        print("\n" + "=" * 60)
        print("Example 4: Batch Memory Operations")
        print("=" * 60)

        # Multiple tasks to store
        tasks = [
            "Implement user authentication with JWT",
            "Create data validation middleware",
            "Build automated testing framework",
            "Design database schema for multi-tenancy",
        ]

        print("\nBatch analyzing and storing tasks...")
        task_ids = []

        for task_desc in tasks:
            # Analyze
            analysis = self.orchestrator.analyze_task(task_desc)
            task_ids.append(analysis.task_id)

            # Store
            await self.memory.store_memory(
                data={
                    "task_id": analysis.task_id,
                    "description": task_desc,
                    "complexity": analysis.complexity,
                    "timestamp": datetime.now().isoformat(),
                },
                metadata={"type": "batch_task", "batch_id": "example_batch_001"},
            )

            print(f"  ✓ Stored: {task_desc[:40]}... (ID: {analysis.task_id[:8]}...)")

        # Query batch results
        print("\nQuerying batch results...")
        batch_request = MemoryRequest(
            operation="query",
            data_type="task",
            query={"batch_id": "example_batch_001"},
            metadata={"return_all": True},
        )

        response = await self.memory.query_memory(batch_request)
        if response.success:
            print(f"Retrieved {len(response.data.get('results', []))} tasks from batch")

    async def example_memory_patterns(self):
        """Example: Common memory usage patterns."""
        print("\n" + "=" * 60)
        print("Example 5: Memory Usage Patterns")
        print("=" * 60)

        # Pattern 1: Cache frequently accessed data
        print("\n1. Caching Pattern:")
        cache_request = MemoryRequest(
            operation="store",
            data_type="cache",
            data={"key": "common_requirements", "value": ["error_handling", "logging", "testing"]},
            routing_strategy=MemoryStrategy.SPEED_OPTIMIZED,
        )
        await self.memory.store_memory(
            cache_request.data,
            metadata={"ttl": 3600, "type": "cache"},
            routing_strategy=cache_request.routing_strategy,
        )
        print("  ✓ Cached common requirements in Redis")

        # Pattern 2: Store relationships
        print("\n2. Relationship Pattern:")
        relationship_data = {
            "parent_task": "task_001",
            "subtasks": ["task_002", "task_003", "task_004"],
            "relationship_type": "decomposition",
        }
        await self.memory.store_memory(
            relationship_data,
            metadata={"type": "relationship", "graph": True},
            routing_strategy=MemoryStrategy.ACCURACY_OPTIMIZED,
        )
        print("  ✓ Stored task relationships in Neo4j")

        # Pattern 3: Historical data
        print("\n3. Historical Pattern:")
        historical_data = {
            "task_id": "task_historical",
            "metrics": {
                "average_completion_time": 4.5,
                "success_rate": 0.85,
                "common_issues": ["scope_creep", "unclear_requirements"],
            },
        }
        await self.memory.store_memory(
            historical_data,
            metadata={"type": "historical", "persist": True},
            routing_strategy=MemoryStrategy.COST_OPTIMIZED,
        )
        print("  ✓ Stored historical metrics in PostgreSQL")

    async def example_cleanup(self):
        """Example: Clean up old memory entries."""
        print("\n" + "=" * 60)
        print("Example 6: Memory Cleanup")
        print("=" * 60)

        # Query old entries
        cleanup_request = MemoryRequest(
            operation="query",
            data_type="task",
            query={"older_than_days": 30},
            metadata={"count_only": True},
        )

        response = await self.memory.query_memory(cleanup_request)
        if response.success:
            count = response.data.get("count", 0)
            print(f"\nFound {count} tasks older than 30 days")

            if count > 0:
                # In production, implement actual deletion
                print("  (Cleanup would remove these entries)")

    async def run_all_examples(self):
        """Run all CRUD examples."""
        try:
            # Initialize connections
            await self.memory.initialize_all_connections()

            # Run examples
            task_id = await self.example_store_task()

            similar_tasks = await self.example_query_similar_tasks(
                "Build API with security features"
            )

            await self.example_update_task_outcome(task_id, validation_passed=True)

            await self.example_batch_operations()

            await self.example_memory_patterns()

            await self.example_cleanup()

        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure memory systems are configured and running:")
            print("  - Redis: redis://localhost:6379")
            print("  - Neo4j: bolt://localhost:7687")
            print("  - PostgreSQL: postgresql://user:pass@localhost:5432/orchestrator")

        finally:
            # Cleanup
            await self.memory.close_all_connections()


async def main():
    """Run memory CRUD examples."""
    print("\n🗄️  AI Task Orchestrator - Memory CRUD Examples")
    print("===============================================")

    examples = MemoryCRUDExamples()
    await examples.run_all_examples()

    print("\n\n✅ Memory CRUD examples completed!")
    print("\nKey Patterns Demonstrated:")
    print("  - Store task analysis results for future reference")
    print("  - Query similar tasks based on description")
    print("  - Update tasks with validation outcomes")
    print("  - Perform batch operations efficiently")
    print("  - Use different routing strategies for optimization")
    print("  - Implement cleanup for old data")


if __name__ == "__main__":
    asyncio.run(main())
