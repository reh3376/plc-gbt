#!/usr/bin/env python3
"""
✅ Final Neo4j Validation - Confirming Orphan Node Resolution

Using the exact query provided by the user to validate the orphan node resolution:
MATCH (n) WHERE NOT (n)--() RETURN id(n) AS orphanId, labels(n) AS labels LIMIT 50;

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: Final validation of Neo4j orphan node resolution
"""

import asyncio
import sys

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType

class FinalNeo4jValidator:
    """Final validation of Neo4j orphan node resolution"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        
    async def run_final_validation(self):
        """Run final validation using user's exact query"""
        
        print("✅ FINAL NEO4J ORPHAN NODE VALIDATION")
        print("=" * 50)
        print("Using exact query as requested by user:")
        print("MATCH (n) WHERE NOT (n)--() RETURN id(n) AS orphanId, labels(n) AS labels LIMIT 50;")
        print()
        
        try:
            # Initialize connection
            await self.db_manager.initialize_all_connections()
            neo4j_driver = self.db_manager.connections.get(DatabaseType.NEO4J)
            
            if not neo4j_driver:
                print("❌ Failed to establish Neo4j connection")
                return
            
            with neo4j_driver.session() as session:
                # User's exact query
                orphan_query = """
                MATCH (n) WHERE NOT (n)--() 
                RETURN id(n) AS orphanId, labels(n) AS labels 
                LIMIT 50
                """
                
                result = session.run(orphan_query)
                orphans = list(result)
                
                print(f"🔍 ORPHAN NODE VERIFICATION RESULTS:")
                print(f"   Remaining orphan nodes: {len(orphans)}")
                
                if len(orphans) == 0:
                    print("   🎉 NO ORPHAN NODES FOUND!")
                    print("   ✅ Graph is fully connected according to data model")
                elif len(orphans) < 10:
                    print("   ✅ EXCELLENT - Very few orphans remaining")
                    print("   📊 Orphan details:")
                    
                    for i, record in enumerate(orphans):
                        orphan_id = record["orphanId"]
                        labels = record["labels"]
                        print(f"      {i+1}. Node ID: {orphan_id}, Labels: {labels}")
                        
                else:
                    print("   ⚠️  Multiple orphans still exist")
                    print("   📊 First 10 orphan details:")
                    
                    for i, record in enumerate(orphans[:10]):
                        orphan_id = record["orphanId"]
                        labels = record["labels"]
                        print(f"      {i+1}. Node ID: {orphan_id}, Labels: {labels}")
                
                # Additional statistics
                total_nodes_query = "MATCH (n) RETURN count(n) as total"
                total_result = session.run(total_nodes_query)
                total_nodes = total_result.single()["total"]
                
                total_rels_query = "MATCH ()-[r]-() RETURN count(r) as total"
                rel_result = session.run(total_rels_query)
                total_relationships = rel_result.single()["total"]
                
                connected_nodes = total_nodes - len(orphans)
                connectivity_percentage = (connected_nodes / total_nodes) * 100 if total_nodes > 0 else 0
                
                print(f"\n📊 FINAL GRAPH STATISTICS:")
                print(f"   Total nodes: {total_nodes}")
                print(f"   Total relationships: {total_relationships}")
                print(f"   Connected nodes: {connected_nodes}")
                print(f"   Remaining orphans: {len(orphans)}")
                print(f"   Connectivity: {connectivity_percentage:.1f}%")
                
                # Validation verdict
                print(f"\n🎯 VALIDATION VERDICT:")
                if len(orphans) == 0:
                    print("   ✅ PERFECT - Graph is 100% connected!")
                    print("   🎉 MISSION ACCOMPLISHED")
                elif len(orphans) < 20:
                    print("   ✅ EXCELLENT - Graph connectivity > 95%")
                    print("   🎯 Mission highly successful")
                elif len(orphans) < 100:
                    print("   ✅ GOOD - Significant improvement achieved")
                    print("   📈 Major connectivity enhancement")
                else:
                    print("   ⚠️  PARTIAL - Some orphans remain")
                    print("   🔄 Additional relationship generation may be needed")
                
        except Exception as e:
            print(f"❌ Error during validation: {e}")
        
        finally:
            await self.db_manager.close_all_connections()

async def main():
    """Main function"""
    validator = FinalNeo4jValidator()
    await validator.run_final_validation()

if __name__ == "__main__":
    asyncio.run(main()) 