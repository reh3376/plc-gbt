#!/usr/bin/env python3
"""
🧠 Phase 21.5: PLC Memory System Integration

Integrates the comprehensive plc-memory management system with the Phase 21 CLI framework,
providing seamless access to multi-database memory coordination (Redis, Neo4j, PostgreSQL, Qdrant)
for control loop instances and schema management.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (Integration of existing systems)
Context Management: Multi-database coordination with CLI framework
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 21.5 Objectives:
- Integrate plc-memory CLI with Phase 21 framework
- Enable memory-based recommendations for schema and instance operations
- Provide semantic search capabilities for control loop configurations
- Historical tracking integration for audit and learning

Author: AI Task Orchestrator
Created: 2025-01-18
Phase: 21.5.1 - PLC Memory Integration
Dependencies: plc-memory system, Phase 21.1-21.4 CLI framework
"""

import asyncio
import logging
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from rich.console import Console

# Project imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts" / "ai"))

# Import plc-memory system components
try:
    from codebase_analyzer import AnalysisDepth
    from database_manager import DatabaseManager, DatabaseType, MemoryTier
    from memory_coordinator import MemoryCoordinator, MemoryRequest, QueryStrategy
    MEMORY_SYSTEM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"PLC Memory system not available: {e}")
    MEMORY_SYSTEM_AVAILABLE = False

# Set up console and logging
console = Console()
logger = logging.getLogger(__name__)

# =============================================================================
# MEMORY INTEGRATION CLASSES
# =============================================================================

@dataclass
class MemoryIntegrationStatus:
    """Status of memory system integration"""
    available: bool = False
    databases_connected: Dict[str, bool] = None
    coordinator_initialized: bool = False
    last_check: Optional[datetime] = None
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.databases_connected is None:
            self.databases_connected = {
                "redis": False,
                "neo4j": False,
                "postgresql": False,
                "qdrant": False
            }

class MemoryIntegrationManager:
    """
    Manages integration between CLI and plc-memory system

    Provides:
    - Memory system initialization and health checking
    - Schema and instance memory operations
    - Semantic search capabilities
    - Historical tracking and recommendations
    """

    def __init__(self):
        self.status = MemoryIntegrationStatus()
        self.db_manager: Optional[DatabaseManager] = None
        self.coordinator: Optional[MemoryCoordinator] = None
        self._initialization_attempted = False

    async def initialize(self) -> bool:
        """Initialize memory system connections"""
        if not MEMORY_SYSTEM_AVAILABLE:
            logger.warning("PLC Memory system not available - operating without memory integration")
            return False

        if self._initialization_attempted:
            return self.status.available

        self._initialization_attempted = True

        try:
            console.print("[dim]🧠 Initializing PLC Memory system...[/dim]")

            # Initialize database manager
            self.db_manager = DatabaseManager()
            await self.db_manager.initialize_all_connections()

            # Initialize memory coordinator
            self.coordinator = MemoryCoordinator(self.db_manager)

            # Check database connections
            health_check = await self.db_manager.health_check()
            self.status.databases_connected = {
                "redis": health_check.get("redis", {}).get("status") == "healthy",
                "neo4j": health_check.get("neo4j", {}).get("status") == "healthy",
                "postgresql": health_check.get("postgresql", {}).get("status") == "healthy",
                "qdrant": health_check.get("qdrant", {}).get("status") == "healthy"
            }

            # Update status
            self.status.available = True
            self.status.coordinator_initialized = True
            self.status.last_check = datetime.now()

            connected_count = sum(self.status.databases_connected.values())
            console.print(f"[green]✅ Memory system initialized with {connected_count}/4 databases[/green]")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize memory system: {e}")
            console.print(f"[yellow]⚠️  Memory system unavailable: {e}[/yellow]")
            self.status.available = False
            return False

    async def cleanup(self):
        """Cleanup memory system connections"""
        if self.db_manager:
            await self.db_manager.cleanup()

    def is_available(self) -> bool:
        """Check if memory system is available"""
        return self.status.available and MEMORY_SYSTEM_AVAILABLE

    async def store_schema_activity(self, schema_id: str, operation: str, metadata: Dict[str, Any]) -> bool:
        """Store schema activity in memory system"""
        if not self.is_available():
            return False

        try:
            request = MemoryRequest(
                operation_type='store_activity',
                data_type='schema_operation',
                content={
                    'schema_id': schema_id,
                    'operation': operation,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': metadata
                },
                routing_strategy=QueryStrategy.BALANCED
            )

            response = await self.coordinator.query_memory(request)
            return response.success

        except Exception as e:
            logger.error(f"Failed to store schema activity: {e}")
            return False

    async def store_instance_activity(self, instance_id: str, operation: str, metadata: Dict[str, Any]) -> bool:
        """Store instance activity in memory system"""
        if not self.is_available():
            return False

        try:
            request = MemoryRequest(
                operation_type='store_activity',
                data_type='instance_operation',
                content={
                    'instance_id': instance_id,
                    'operation': operation,
                    'timestamp': datetime.now().isoformat(),
                    'metadata': metadata
                },
                routing_strategy=QueryStrategy.BALANCED
            )

            response = await self.coordinator.query_memory(request)
            return response.success

        except Exception as e:
            logger.error(f"Failed to store instance activity: {e}")
            return False

    async def get_schema_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get schema recommendations based on context"""
        if not self.is_available():
            return []

        try:
            request = MemoryRequest(
                operation_type='search_recommendations',
                data_type='schema_recommendation',
                content=context,
                routing_strategy=QueryStrategy.ACCURACY_OPTIMIZED,
                metadata={'limit': 5}
            )

            response = await self.coordinator.query_memory(request)
            if response.success and response.data:
                return response.data.get('recommendations', [])
            return []

        except Exception as e:
            logger.error(f"Failed to get schema recommendations: {e}")
            return []

    async def get_instance_recommendations(self, schema_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get instance recommendations based on schema and context"""
        if not self.is_available():
            return []

        try:
            request = MemoryRequest(
                operation_type='search_recommendations',
                data_type='instance_recommendation',
                content={
                    'schema_id': schema_id,
                    'context': context
                },
                routing_strategy=QueryStrategy.ACCURACY_OPTIMIZED,
                metadata={'limit': 3}
            )

            response = await self.coordinator.query_memory(request)
            if response.success and response.data:
                return response.data.get('recommendations', [])
            return []

        except Exception as e:
            logger.error(f"Failed to get instance recommendations: {e}")
            return []

    async def semantic_search(self, query: str, data_type: str = 'code_function', limit: int = 10) -> List[Dict[str, Any]]:
        """Perform semantic search across memory system"""
        if not self.is_available():
            return []

        try:
            request = MemoryRequest(
                operation_type='search',
                data_type=data_type,
                content=query,
                routing_strategy=QueryStrategy.BALANCED,
                metadata={'limit': limit}
            )

            response = await self.coordinator.query_memory(request)
            if response.success and response.data:
                return response.data.get('results', [])
            return []

        except Exception as e:
            logger.error(f"Failed to perform semantic search: {e}")
            return []

    async def get_usage_analytics(self) -> Dict[str, Any]:
        """Get usage analytics from memory system"""
        if not self.is_available():
            return {}

        try:
            # Get performance summary from coordinator
            performance = self.coordinator.get_performance_summary()

            # Get database health status
            health = await self.db_manager.health_check()

            return {
                'performance': performance,
                'health': health,
                'status': asdict(self.status)
            }

        except Exception as e:
            logger.error(f"Failed to get usage analytics: {e}")
            return {}

    async def optimize_memory_tiers(self) -> Dict[str, Any]:
        """Optimize memory tier distribution"""
        if not self.is_available():
            return {'error': 'Memory system not available'}

        try:
            result = await self.coordinator.optimize_memory_tiers()
            return result

        except Exception as e:
            logger.error(f"Failed to optimize memory tiers: {e}")
            return {'error': str(e)}

# =============================================================================
# CLI INTEGRATION FUNCTIONS
# =============================================================================

# Global memory integration manager instance
_memory_manager: Optional[MemoryIntegrationManager] = None

async def get_memory_manager() -> MemoryIntegrationManager:
    """Get or create memory integration manager"""
    global _memory_manager

    if _memory_manager is None:
        _memory_manager = MemoryIntegrationManager()
        await _memory_manager.initialize()

    return _memory_manager

async def cleanup_memory_manager():
    """Cleanup memory manager"""
    global _memory_manager

    if _memory_manager:
        await _memory_manager.cleanup()
        _memory_manager = None

def memory_integration_status() -> Dict[str, Any]:
    """Get memory integration status synchronously"""
    if _memory_manager:
        return asdict(_memory_manager.status)
    else:
        return {
            'available': False,
            'coordinator_initialized': False,
            'databases_connected': {
                'redis': False,
                'neo4j': False,
                'postgresql': False,
                'qdrant': False
            }
        }

# =============================================================================
# CLI COMMAND DECORATORS
# =============================================================================

def with_memory_integration(func):
    """Decorator to provide memory integration to CLI commands"""
    def wrapper(*args, **kwargs):
        async def async_wrapper():
            memory_manager = await get_memory_manager()
            return await func(memory_manager, *args, **kwargs)

        if asyncio.iscoroutinefunction(func):
            return asyncio.run(async_wrapper())
        else:
            # For non-async functions, just pass the manager
            return func(_memory_manager, *args, **kwargs)

    return wrapper

def memory_enhanced_command(func):
    """Decorator for commands that are enhanced by memory integration"""
    def wrapper(*args, **kwargs):
        # Add memory status to command context
        if hasattr(kwargs.get('ctx'), 'obj'):
            ctx = kwargs['ctx']
            if hasattr(ctx.obj, 'memory_status'):
                ctx.obj.memory_status = memory_integration_status()

        return func(*args, **kwargs)

    return wrapper

# =============================================================================
# MAIN DEMONSTRATION (for testing)
# =============================================================================

if __name__ == "__main__":
    async def main():
        """Demonstrate memory integration functionality"""
        console.print("[bold blue]🧠 PLC Memory Integration Test[/bold blue]")

        manager = MemoryIntegrationManager()
        success = await manager.initialize()

        if success:
            console.print("[green]✅ Memory integration successful[/green]")

            # Test semantic search
            results = await manager.semantic_search("PID controller", limit=3)
            console.print(f"Found {len(results)} semantic search results")

            # Test analytics
            analytics = await manager.get_usage_analytics()
            console.print(f"Analytics available: {bool(analytics)}")

        else:
            console.print("[yellow]⚠️  Memory integration unavailable[/yellow]")

        await manager.cleanup()

    asyncio.run(main())
