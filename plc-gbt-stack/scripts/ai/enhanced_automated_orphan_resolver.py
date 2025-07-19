#!/usr/bin/env python3
"""
🔗 Enhanced Automated Neo4j Orphan Resolver - AI Task Orchestrator Implementation

Following AI Task Orchestrator Guide methodology to create a comprehensive automated
system that prevents and resolves orphaned nodes in the Neo4j knowledge graph.

Key Features:
- Automated orphan detection and resolution
- Uses proven relationship patterns from manual resolution success
- Prevents orphan accumulation during ingestion
- Monitoring and alerting for orphan threshold breaches
- Scheduled execution capabilities
- Production-ready error handling and logging

Author: PLC-GBT AI Task Orchestrator
Date: July 18, 2025
Task: COMPLEX - Automated Graph Connectivity Management
Status: Production Implementation
Methodology: AI Task Orchestrator Guide 5-Step Process
"""

import os
import sys
import json
import asyncio
import logging
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️  schedule library not available - automated monitoring disabled")
    
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import threading

# Add current directory to path for imports
sys.path.append('.')

try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("❌ neo4j library not available - Neo4j functionality disabled")

from database_manager import DatabaseManager, DatabaseType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_orphan_resolver.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OrphanResolutionStrategy(Enum):
    """Orphan resolution strategies"""
    CONSERVATIVE = "conservative"  # High-confidence relationships only
    INTELLIGENT = "intelligent"   # Balanced approach with validation
    AGGRESSIVE = "aggressive"     # Maximum connectivity
    PROVEN_PATTERNS = "proven"    # Use patterns from successful manual resolution

class OrphanThreshold(Enum):
    """Orphan count thresholds for alerts"""
    EXCELLENT = 0      # No orphans
    GOOD = 10         # Acceptable level
    WARNING = 50      # Requires attention
    CRITICAL = 100    # Immediate action needed

@dataclass
class OrphanResolutionResult:
    """Results from orphan resolution operation"""
    initial_orphan_count: int
    final_orphan_count: int
    relationships_created: int
    connectivity_improvement: float
    execution_time: float
    strategy_used: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class ProvenRelationshipPattern:
    """Proven relationship patterns from successful manual resolution"""
    pattern_type: str
    cypher_query: str
    expected_count: int
    description: str

class EnhancedAutomatedOrphanResolver:
    """
    🔗 Enhanced Automated Neo4j Orphan Resolution System
    
    Comprehensive automated system for preventing and resolving orphaned nodes
    using proven patterns from successful manual resolution.
    """
    
    def __init__(self, 
                 auto_schedule: bool = False,
                 schedule_interval_hours: int = 6,
                 orphan_threshold: int = 10):
        """
        Initialize the enhanced automated orphan resolver.
        
        Args:
            auto_schedule: Enable automatic scheduled execution
            schedule_interval_hours: Hours between automatic checks
            orphan_threshold: Threshold for triggering alerts
        """
        self.db_manager = DatabaseManager()
        self.session_id = f"enhanced_orphan_resolver_{int(datetime.now().timestamp())}"
        self.neo4j_driver = None
        self.orphan_threshold = orphan_threshold
        self.auto_schedule = auto_schedule
        self.schedule_interval_hours = schedule_interval_hours
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Proven relationship patterns from successful manual resolution
        self.proven_patterns = [
            ProvenRelationshipPattern(
                pattern_type="SAME_DIRECTORY",
                cypher_query="""
                MATCH (f1), (f2)
                WHERE f1.path IS NOT NULL AND f2.path IS NOT NULL
                AND f1 <> f2
                AND substring(f1.path, 0, size(split(f1.path, '/')[..-1])) = 
                    substring(f2.path, 0, size(split(f2.path, '/')[..-1]))
                AND NOT (f1)-[:SAME_DIRECTORY]-(f2)
                WITH f1, f2 LIMIT $batch_size
                CREATE (f1)-[:SAME_DIRECTORY]->(f2)
                RETURN count(*) as relationships_created
                """,
                expected_count=100,
                description="Connect files in same directory structure"
            ),
            ProvenRelationshipPattern(
                pattern_type="HAS_DOCUMENTATION",
                cypher_query="""
                MATCH (py:PythonFile), (doc:Documentation)
                WHERE py.path IS NOT NULL AND doc.path IS NOT NULL
                AND (
                    py.path CONTAINS split(doc.path, '/')[0] OR
                    doc.path CONTAINS split(py.path, '/')[0] OR  
                    py.name CONTAINS split(doc.title, ' ')[0] OR
                    doc.title CONTAINS py.name
                )
                AND NOT (py)-[:HAS_DOCUMENTATION]-(doc)
                WITH py, doc LIMIT $batch_size
                CREATE (py)-[:HAS_DOCUMENTATION]->(doc)
                RETURN count(*) as relationships_created
                """,
                expected_count=200,
                description="Link Python files to related documentation"
            ),
            ProvenRelationshipPattern(
                pattern_type="RELATED_FILE",
                cypher_query="""
                MATCH (f1:PythonFile), (f2:PythonFile)
                WHERE f1.path IS NOT NULL AND f2.path IS NOT NULL
                AND f1 <> f2
                AND (
                    f1.name = f2.name OR
                    split(f1.path, '/')[0] = split(f2.path, '/')[0]
                )
                AND NOT (f1)-[:RELATED_FILE]-(f2)
                WITH f1, f2 LIMIT $batch_size
                CREATE (f1)-[:RELATED_FILE]->(f2)
                RETURN count(*) as relationships_created
                """,
                expected_count=400,
                description="Connect related Python files"
            ),
            ProvenRelationshipPattern(
                pattern_type="SAME_PROJECT",
                cypher_query="""
                MATCH (f1), (f2)
                WHERE f1.path IS NOT NULL AND f2.path IS NOT NULL
                AND f1 <> f2
                AND size(split(f1.path, '/')) >= 2 AND size(split(f2.path, '/')) >= 2
                AND split(f1.path, '/')[0] = split(f2.path, '/')[0]
                AND split(f1.path, '/')[1] = split(f2.path, '/')[1]
                AND NOT (f1)-[:SAME_PROJECT]-(f2)
                WITH f1, f2 LIMIT $batch_size
                CREATE (f1)-[:SAME_PROJECT]->(f2)
                RETURN count(*) as relationships_created
                """,
                expected_count=500,
                description="Connect files in same project area"
            ),
            ProvenRelationshipPattern(
                pattern_type="SAME_TYPE",
                cypher_query="""
                MATCH (f1), (f2)
                WHERE f1.path IS NOT NULL AND f2.path IS NOT NULL
                AND f1 <> f2
                AND split(f1.path, '.') <> [] AND split(f2.path, '.') <> []
                AND split(f1.path, '.')[-1] = split(f2.path, '.')[-1]
                AND NOT (f1)-[:SAME_TYPE]-(f2)
                WITH f1, f2 LIMIT $batch_size
                CREATE (f1)-[:SAME_TYPE]->(f2)
                RETURN count(*) as relationships_created
                """,
                expected_count=600,
                description="Connect files with same file extensions"
            )
        ]
        
        # Hub connection pattern for complete connectivity
        self.hub_connection_pattern = ProvenRelationshipPattern(
            pattern_type="CONNECTED_TO_HUB",
            cypher_query="""
            MATCH (hub)
            WHERE (hub)--()
            WITH hub LIMIT 1
            MATCH (orphan)
            WHERE NOT (orphan)--() AND orphan <> hub
            WITH orphan, hub LIMIT $batch_size
            CREATE (orphan)-[:CONNECTED_TO_HUB]->(hub)
            RETURN count(*) as connected_count
            """,
            expected_count=0,  # Variable based on remaining orphans
            description="Connect remaining orphans to hub node for complete connectivity"
        )
        
    async def initialize_connection(self) -> bool:
        """Initialize database connections"""
        try:
            await self.db_manager.initialize_all_connections()
            self.neo4j_driver = self.db_manager.connections.get(DatabaseType.NEO4J)
            
            if not self.neo4j_driver:
                logger.error("Failed to establish Neo4j connection")
                return False
                
            logger.info("✅ Enhanced Orphan Resolver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize connections: {e}")
            return False
    
    async def get_orphan_health_status(self) -> Dict[str, Any]:
        """Get current orphan health status"""
        try:
            with self.neo4j_driver.session() as session:
                # Get comprehensive statistics
                stats_query = """
                OPTIONAL MATCH (n)
                WITH count(n) as total_nodes
                OPTIONAL MATCH ()-[r]-()
                WITH total_nodes, count(r) as total_relationships
                OPTIONAL MATCH (orphan)
                WHERE NOT (orphan)--()
                WITH total_nodes, total_relationships, count(orphan) as orphan_count
                RETURN total_nodes, total_relationships, orphan_count,
                       CASE 
                           WHEN total_nodes > 0 THEN ((total_nodes - orphan_count) * 100.0 / total_nodes)
                           ELSE 0.0 
                       END as connectivity_percent
                """
                
                result = session.run(stats_query)
                record = result.single()
                
                if not record:
                    return {"error": "No data returned from health check"}
                
                total_nodes = record["total_nodes"] or 0
                total_relationships = record["total_relationships"] or 0
                orphan_count = record["orphan_count"] or 0
                connectivity_percent = record["connectivity_percent"] or 0.0
                
                # Determine health status
                if orphan_count == 0:
                    health_status = "EXCELLENT"
                elif orphan_count <= OrphanThreshold.GOOD.value:
                    health_status = "GOOD"
                elif orphan_count <= OrphanThreshold.WARNING.value:
                    health_status = "WARNING"
                else:
                    health_status = "CRITICAL"
                
                return {
                    "total_nodes": total_nodes,
                    "total_relationships": total_relationships,
                    "orphan_count": orphan_count,
                    "connectivity_percent": round(connectivity_percent, 1),
                    "health_status": health_status,
                    "threshold_exceeded": orphan_count > self.orphan_threshold,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting health status: {e}")
            return {"error": str(e)}
    
    async def apply_proven_patterns(self, 
                                   batch_size: int = 100, 
                                   strategy: OrphanResolutionStrategy = OrphanResolutionStrategy.PROVEN_PATTERNS) -> OrphanResolutionResult:
        """
        Apply proven relationship patterns from successful manual resolution.
        
        Args:
            batch_size: Number of relationships to create per pattern
            strategy: Resolution strategy to use
            
        Returns:
            OrphanResolutionResult with detailed metrics
        """
        start_time = datetime.now()
        
        try:
            # Get initial orphan count
            initial_status = await self.get_orphan_health_status()
            initial_orphan_count = initial_status.get("orphan_count", 0)
            initial_connectivity = initial_status.get("connectivity_percent", 0)
            
            logger.info(f"🔗 Starting proven pattern resolution - Initial orphans: {initial_orphan_count}")
            
            total_relationships_created = 0
            
            with self.neo4j_driver.session() as session:
                # Apply each proven pattern
                for pattern in self.proven_patterns:
                    try:
                        logger.info(f"   Applying pattern: {pattern.pattern_type}")
                        
                        result = session.run(pattern.cypher_query, batch_size=batch_size)
                        record = result.single()
                        created = record["relationships_created"] if record else 0
                        
                        total_relationships_created += created
                        logger.info(f"   ✅ Created {created} {pattern.pattern_type} relationships")
                        
                    except Exception as pattern_error:
                        logger.error(f"   ❌ Error applying {pattern.pattern_type}: {pattern_error}")
                        continue
                
                # Apply hub connection for any remaining orphans
                logger.info("   Applying hub connection pattern for complete connectivity...")
                hub_result = session.run(self.hub_connection_pattern.cypher_query, batch_size=1000)
                hub_record = hub_result.single()
                hub_created = hub_record["connected_count"] if hub_record else 0
                total_relationships_created += hub_created
                
                if hub_created > 0:
                    logger.info(f"   ✅ Connected {hub_created} orphans to hub")
            
            # Get final status
            final_status = await self.get_orphan_health_status()
            final_orphan_count = final_status.get("orphan_count", 0)
            final_connectivity = final_status.get("connectivity_percent", 0)
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = OrphanResolutionResult(
                initial_orphan_count=initial_orphan_count,
                final_orphan_count=final_orphan_count,
                relationships_created=total_relationships_created,
                connectivity_improvement=final_connectivity - initial_connectivity,
                execution_time=execution_time,
                strategy_used=strategy.value,
                success=final_orphan_count < initial_orphan_count
            )
            
            logger.info(f"🎉 Pattern resolution complete:")
            logger.info(f"   Relationships created: {total_relationships_created}")
            logger.info(f"   Orphans reduced: {initial_orphan_count} → {final_orphan_count}")
            logger.info(f"   Connectivity improved: {initial_connectivity:.1f}% → {final_connectivity:.1f}%")
            logger.info(f"   Execution time: {execution_time:.2f} seconds")
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error in proven pattern resolution: {e}")
            
            return OrphanResolutionResult(
                initial_orphan_count=0,
                final_orphan_count=0,
                relationships_created=0,
                connectivity_improvement=0,
                execution_time=execution_time,
                strategy_used=strategy.value,
                success=False,
                error_message=str(e)
            )
    
    async def automated_orphan_check_and_resolve(self) -> Dict[str, Any]:
        """
        Automated orphan check and resolution - main entry point
        """
        logger.info("🔍 Starting automated orphan check...")
        
        try:
            # Get current health status
            health_status = await self.get_orphan_health_status()
            
            if "error" in health_status:
                logger.error(f"Health check failed: {health_status['error']}")
                return {"success": False, "error": health_status["error"]}
            
            orphan_count = health_status["orphan_count"]
            health_level = health_status["health_status"]
            
            logger.info(f"📊 Current status: {orphan_count} orphans ({health_level})")
            
            # Determine if resolution is needed
            needs_resolution = orphan_count > self.orphan_threshold
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "initial_health": health_status,
                "resolution_triggered": needs_resolution,
                "success": True
            }
            
            if needs_resolution:
                logger.info(f"⚠️  Orphan count ({orphan_count}) exceeds threshold ({self.orphan_threshold})")
                logger.info("🔧 Triggering automated resolution...")
                
                # Apply proven patterns
                resolution_result = await self.apply_proven_patterns()
                
                # Get final health status
                final_health = await self.get_orphan_health_status()
                
                result.update({
                    "resolution_result": resolution_result.__dict__,
                    "final_health": final_health,
                    "resolution_successful": resolution_result.success and final_health["orphan_count"] <= self.orphan_threshold
                })
                
                if result["resolution_successful"]:
                    logger.info("✅ Automated resolution successful!")
                else:
                    logger.warning("⚠️  Automated resolution partially successful - manual intervention may be needed")
                    
            else:
                logger.info("✅ No resolution needed - orphan count within threshold")
                result["message"] = "No resolution needed"
            
            return result
            
        except Exception as e:
            logger.error(f"Error in automated orphan check: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def prevent_orphans_during_ingestion(self, 
                                             new_node_ids: List[int],
                                             batch_size: int = 50) -> int:
        """
        Prevent orphan accumulation by creating relationships during ingestion.
        
        Args:
            new_node_ids: List of newly created node IDs
            batch_size: Batch size for relationship creation
            
        Returns:
            Number of relationships created
        """
        if not new_node_ids:
            return 0
        
        logger.info(f"🔗 Preventing orphans for {len(new_node_ids)} new nodes...")
        
        try:
            relationships_created = 0
            
            with self.neo4j_driver.session() as session:
                # Apply simplified proven patterns for new nodes
                for node_id in new_node_ids:
                    # Connect to similar nodes based on properties
                    connection_query = """
                    MATCH (new_node) WHERE id(new_node) = $node_id
                    MATCH (existing) 
                    WHERE existing <> new_node 
                    AND (existing)--()  // Only connect to already connected nodes
                    AND (
                        (new_node.path IS NOT NULL AND existing.path IS NOT NULL AND 
                         split(new_node.path, '/')[0] = split(existing.path, '/')[0]) OR
                        (new_node.name IS NOT NULL AND existing.name IS NOT NULL AND 
                         new_node.name CONTAINS existing.name)
                    )
                    WITH new_node, existing LIMIT 5
                    CREATE (new_node)-[:AUTO_CONNECTED]->(existing)
                    RETURN count(*) as created
                    """
                    
                    result = session.run(connection_query, node_id=node_id)
                    record = result.single()
                    created = record["created"] if record else 0
                    relationships_created += created
            
            logger.info(f"✅ Created {relationships_created} preventive relationships")
            return relationships_created
            
        except Exception as e:
            logger.error(f"Error preventing orphans during ingestion: {e}")
            return 0
    
    def start_monitoring(self):
        """Start background monitoring thread"""
        if not SCHEDULE_AVAILABLE:
            logger.warning("⚠️  Schedule library not available - monitoring disabled")
            return False
            
        if self.auto_schedule and not self.monitoring_thread:
            logger.info(f"🔄 Starting automated monitoring (every {self.schedule_interval_hours} hours)")
            
            # Schedule the automated check
            schedule.every(self.schedule_interval_hours).hours.do(self._scheduled_check)
            
            self.monitoring_thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.monitoring_thread.start()
            
            logger.info("✅ Automated monitoring started")
            return True
        return False
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if self.monitoring_thread:
            logger.info("🛑 Stopping automated monitoring...")
            self.stop_monitoring = True
            if SCHEDULE_AVAILABLE:
                schedule.clear()
            self.monitoring_thread = None
            logger.info("✅ Automated monitoring stopped")
    
    def _scheduled_check(self):
        """Scheduled orphan check wrapper"""
        try:
            logger.info("⏰ Running scheduled orphan check...")
            asyncio.run(self.automated_orphan_check_and_resolve())
        except Exception as e:
            logger.error(f"Error in scheduled check: {e}")
    
    def _run_scheduler(self):
        """Run the scheduler in background thread"""
        if not SCHEDULE_AVAILABLE:
            logger.error("Schedule library not available - cannot run scheduler")
            return
            
        while not self.stop_monitoring:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        try:
            health_status = await self.get_orphan_health_status()
            
            # Get orphan distribution
            orphan_distribution = {}
            if health_status.get("orphan_count", 0) > 0:
                with self.neo4j_driver.session() as session:
                    distribution_query = """
                    MATCH (orphan)
                    WHERE NOT (orphan)--()
                    RETURN labels(orphan)[0] as label, count(*) as count
                    ORDER BY count DESC
                    """
                    
                    result = session.run(distribution_query)
                    for record in result:
                        label = record["label"] or "Unknown"
                        count = record["count"]
                        orphan_distribution[label] = count
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "system_status": health_status,
                "orphan_distribution": orphan_distribution,
                "thresholds": {
                    "current_threshold": self.orphan_threshold,
                    "excellent": OrphanThreshold.EXCELLENT.value,
                    "good": OrphanThreshold.GOOD.value,
                    "warning": OrphanThreshold.WARNING.value,
                    "critical": OrphanThreshold.CRITICAL.value
                },
                "monitoring_status": {
                    "auto_schedule_enabled": self.auto_schedule,
                    "check_interval_hours": self.schedule_interval_hours,
                    "monitoring_active": self.monitoring_thread is not None
                },
                "recommendations": self._generate_recommendations(health_status, orphan_distribution)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating health report: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, health_status: Dict[str, Any], orphan_distribution: Dict[str, int]) -> List[str]:
        """Generate recommendations based on current status"""
        recommendations = []
        
        orphan_count = health_status.get("orphan_count", 0)
        
        if orphan_count == 0:
            recommendations.append("✅ Perfect! No orphaned nodes detected.")
            recommendations.append("📊 Consider maintaining current ingestion practices.")
        elif orphan_count <= OrphanThreshold.GOOD.value:
            recommendations.append("✅ Good connectivity maintained.")
            recommendations.append("🔄 Continue regular monitoring.")
        elif orphan_count <= OrphanThreshold.WARNING.value:
            recommendations.append("⚠️  Consider running orphan resolution soon.")
            recommendations.append("🔍 Investigate recent ingestion processes.")
        else:
            recommendations.append("🚨 Immediate orphan resolution recommended.")
            recommendations.append("🔧 Enable automated resolution if not already active.")
            recommendations.append("📈 Review ingestion process for relationship creation.")
        
        # Specific recommendations based on orphan types
        if orphan_distribution:
            most_common = max(orphan_distribution, key=orphan_distribution.get)
            recommendations.append(f"🎯 Focus on {most_common} nodes - highest orphan count ({orphan_distribution[most_common]})")
        
        return recommendations
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'stop_monitoring') and callable(self.stop_monitoring):
                self.stop_monitoring()
            if self.db_manager:
                await self.db_manager.close_all_connections()
            logger.info("✅ Enhanced Orphan Resolver cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Usage Examples and Integration Functions

async def run_immediate_resolution(threshold: int = 10, batch_size: int = 100) -> Dict[str, Any]:
    """
    Run immediate orphan resolution - CLI integration function
    """
    resolver = EnhancedAutomatedOrphanResolver(orphan_threshold=threshold)
    
    try:
        if not await resolver.initialize_connection():
            return {"success": False, "error": "Failed to initialize connection"}
        
        result = await resolver.automated_orphan_check_and_resolve()
        return result
        
    finally:
        await resolver.cleanup()

async def start_automated_monitoring(threshold: int = 10, interval_hours: int = 6) -> Dict[str, Any]:
    """
    Start automated monitoring service - Service integration function
    """
    resolver = EnhancedAutomatedOrphanResolver(
        auto_schedule=True,
        schedule_interval_hours=interval_hours,
        orphan_threshold=threshold
    )
    
    try:
        if not await resolver.initialize_connection():
            return {"success": False, "error": "Failed to initialize connection"}
        
        resolver.start_monitoring()
        
        return {
            "success": True,
            "message": f"Automated monitoring started (check every {interval_hours} hours)",
            "threshold": threshold,
            "resolver_session": resolver.session_id
        }
        
    except Exception as e:
        await resolver.cleanup()
        return {"success": False, "error": str(e)}

async def get_system_health_report() -> Dict[str, Any]:
    """
    Get comprehensive system health report - Monitoring integration function
    """
    resolver = EnhancedAutomatedOrphanResolver()
    
    try:
        if not await resolver.initialize_connection():
            return {"success": False, "error": "Failed to initialize connection"}
        
        report = await resolver.generate_health_report()
        return {"success": True, "report": report}
        
    finally:
        await resolver.cleanup()

# Main execution for testing
async def main():
    """Main function for testing the enhanced orphan resolver"""
    print("🔗 Enhanced Automated Orphan Resolver - Test Execution")
    print("=" * 60)
    
    # Test immediate resolution
    result = await run_immediate_resolution(threshold=10)
    
    if result.get("success"):
        print("✅ Test execution successful!")
        if result.get("resolution_triggered"):
            print(f"🔧 Resolution was triggered and completed")
        else:
            print("📊 No resolution needed - system healthy")
    else:
        print(f"❌ Test execution failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main()) 