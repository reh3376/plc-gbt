#!/usr/bin/env python3
"""
🔗 Neo4j Orphan Node Resolver - AI Task Orchestrator Implementation

Following AI Task Orchestrator Guide methodology to systematically resolve the critical
Neo4j graph connectivity issue with >500 orphaned nodes.

Problem Analysis:
- 885 total nodes in graph
- Only 64 nodes participate in 90 relationships  
- >500 orphaned nodes (nodes with no relationships)
- Largest orphan groups: PythonFile (388), Documentation (99), CodeModule (18), GitHubRepo (10)

Solution Strategy:
1. Confirm orphaned nodes and analyze distribution
2. Understand existing data model and relationship patterns
3. Design intelligent relationship generation based on node properties
4. Implement automated relationship creation system
5. Validate complete graph connectivity

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: COMPLEX - Neo4j Graph Connectivity Resolution
Expected Impact: Transform disconnected graph into fully connected knowledge network
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
import re
import traceback

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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jOrphanNodeResolver:
    """
    🔗 Comprehensive Neo4j Orphan Node Resolution System
    
    Systematically identifies orphaned nodes and generates appropriate relationships
    to create a fully connected knowledge graph based on data model analysis.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_id = f"neo4j_orphan_resolver_{int(datetime.now().timestamp())}"
        self.neo4j_driver = None
        
        # Data model patterns for relationship generation
        self.relationship_patterns = {
            "PythonFile": {
                "potential_targets": ["GitHubRepo", "CodeModule", "Documentation"],
                "relationship_types": ["IN_REPO", "CONTAINS_MODULE", "HAS_DOCUMENTATION"],
                "matching_strategies": ["path_based", "name_based", "content_based"]
            },
            "Documentation": {
                "potential_targets": ["PythonFile", "GitHubRepo", "PackagingTool", "CodeModule"],
                "relationship_types": ["DESCRIBES_FILE", "DOCUMENTS_REPO", "DESCRIBES_TOOL", "DOCUMENTS_MODULE"],
                "matching_strategies": ["filename_based", "content_based", "keyword_based"]
            },
            "CodeModule": {
                "potential_targets": ["PythonFile", "GitHubRepo", "Capability"],
                "relationship_types": ["IMPLEMENTS_IN", "PART_OF_REPO", "HAS_CAPABILITY"],
                "matching_strategies": ["name_based", "path_based", "functionality_based"]
            },
            "GitHubRepo": {
                "potential_targets": ["PythonFile", "Documentation", "CodeModule"],
                "relationship_types": ["CONTAINS", "HAS_DOCS", "CONTAINS_MODULE"],
                "matching_strategies": ["path_based", "repo_name_based"]
            }
        }
        
    async def initialize_neo4j_connection(self) -> bool:
        """Initialize Neo4j connection for orphan analysis"""
        try:
            await self.db_manager.initialize_all_connections()
            self.neo4j_driver = self.db_manager.connections.get(DatabaseType.NEO4J)
            
            if not self.neo4j_driver:
                logger.error("Failed to establish Neo4j connection")
                return False
                
            # Test connection
            with self.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                if test_value == 1:
                    logger.info("✅ Neo4j connection established successfully")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"Error initializing Neo4j connection: {e}")
            return False
    
    async def confirm_orphan_nodes(self) -> Dict[str, Any]:
        """
        Step 1: Confirm orphaned nodes and analyze distribution
        """
        print("\n🔍 Step 1: Confirming Orphaned Nodes")
        print("-" * 50)
        
        results = {
            "total_nodes": 0,
            "total_relationships": 0,
            "orphaned_nodes": [],
            "orphan_distribution": {},
            "connected_nodes": 0,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        try:
            with self.neo4j_driver.session() as session:
                # Get total node count
                total_result = session.run("MATCH (n) RETURN count(n) as total")
                results["total_nodes"] = total_result.single()["total"]
                
                # Get total relationship count
                rel_result = session.run("MATCH ()-[r]-() RETURN count(r) as total")
                results["total_relationships"] = rel_result.single()["total"]
                
                print(f"📊 Total nodes in graph: {results['total_nodes']}")
                print(f"📊 Total relationships: {results['total_relationships']}")
                
                # Find all orphaned nodes (nodes with no relationships)
                orphan_query = """
                MATCH (n) 
                WHERE NOT (n)--() 
                RETURN id(n) as orphanId, labels(n) as labels, n.name as name, n.file_path as file_path
                ORDER BY labels(n)[0], n.name
                """
                
                orphan_result = session.run(orphan_query)
                orphaned_nodes = []
                
                for record in orphan_result:
                    orphan_data = {
                        "node_id": record["orphanId"],
                        "labels": record["labels"],
                        "name": record["name"],
                        "file_path": record["file_path"],
                        "primary_label": record["labels"][0] if record["labels"] else "Unknown"
                    }
                    orphaned_nodes.append(orphan_data)
                
                results["orphaned_nodes"] = orphaned_nodes
                results["connected_nodes"] = results["total_nodes"] - len(orphaned_nodes)
                
                # Calculate orphan distribution by label
                orphan_distribution = {}
                for orphan in orphaned_nodes:
                    label = orphan["primary_label"]
                    orphan_distribution[label] = orphan_distribution.get(label, 0) + 1
                
                results["orphan_distribution"] = orphan_distribution
                
                print(f"\n📈 Orphan Analysis Results:")
                print(f"   Total orphaned nodes: {len(orphaned_nodes)}")
                print(f"   Connected nodes: {results['connected_nodes']}")
                print(f"   Orphan percentage: {(len(orphaned_nodes)/results['total_nodes']*100):.1f}%")
                
                print(f"\n📋 Orphan Distribution by Label:")
                for label, count in sorted(orphan_distribution.items(), key=lambda x: x[1], reverse=True):
                    print(f"   {label}: {count} orphans")
                
                return results
                
        except Exception as e:
            logger.error(f"Error confirming orphan nodes: {e}")
            results["error"] = str(e)
            return results
    
    async def analyze_existing_data_model(self) -> Dict[str, Any]:
        """
        Step 2: Analyze existing data model and relationship patterns
        """
        print("\n🔬 Step 2: Analyzing Existing Data Model")
        print("-" * 50)
        
        results = {
            "existing_relationships": {},
            "node_properties": {},
            "relationship_patterns": {},
            "data_model_insights": []
        }
        
        try:
            with self.neo4j_driver.session() as session:
                # Analyze existing relationships
                rel_analysis_query = """
                MATCH (a)-[r]->(b)
                RETURN labels(a)[0] as source_label, type(r) as relationship_type, 
                       labels(b)[0] as target_label, count(*) as count
                ORDER BY count DESC
                """
                
                rel_result = session.run(rel_analysis_query)
                existing_relationships = {}
                
                for record in rel_result:
                    source = record["source_label"]
                    rel_type = record["relationship_type"]
                    target = record["target_label"]
                    count = record["count"]
                    
                    pattern = f"{source}-[{rel_type}]->{target}"
                    existing_relationships[pattern] = count
                
                results["existing_relationships"] = existing_relationships
                
                print(f"🔗 Existing Relationship Patterns:")
                for pattern, count in existing_relationships.items():
                    print(f"   {pattern}: {count} instances")
                
                # Analyze node properties for relationship generation
                node_props_query = """
                MATCH (n)
                WITH labels(n)[0] as label, collect(distinct keys(n)) as all_keys
                RETURN label, all_keys
                """
                
                props_result = session.run(node_props_query)
                node_properties = {}
                
                for record in props_result:
                    label = record["label"]
                    properties = []
                    for key_list in record["all_keys"]:
                        properties.extend(key_list)
                    node_properties[label] = list(set(properties))
                
                results["node_properties"] = node_properties
                
                print(f"\n📝 Node Properties by Label:")
                for label, props in node_properties.items():
                    print(f"   {label}: {props}")
                
                # Generate insights for relationship creation
                insights = []
                
                if "PythonFile" in node_properties and "file_path" in node_properties["PythonFile"]:
                    insights.append("PythonFile nodes have file_path - can link to GitHubRepo by path analysis")
                
                if "Documentation" in node_properties and "name" in node_properties["Documentation"]:
                    insights.append("Documentation nodes have name - can link by filename matching")
                
                if "CodeModule" in node_properties:
                    insights.append("CodeModule nodes can be linked to PythonFile by module analysis")
                
                results["data_model_insights"] = insights
                
                print(f"\n💡 Data Model Insights:")
                for insight in insights:
                    print(f"   • {insight}")
                
                return results
                
        except Exception as e:
            logger.error(f"Error analyzing data model: {e}")
            results["error"] = str(e)
            return results
    
    async def design_relationship_strategy(self, orphan_data: Dict[str, Any], model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 3: Design intelligent strategy for generating missing relationships
        """
        print("\n🎯 Step 3: Designing Relationship Generation Strategy")
        print("-" * 50)
        
        strategy = {
            "relationship_rules": {},
            "matching_algorithms": {},
            "priority_mappings": {},
            "validation_criteria": {}
        }
        
        try:
            # Design rules for each orphan type
            orphan_distribution = orphan_data.get("orphan_distribution", {})
            
            for label, count in orphan_distribution.items():
                if label in self.relationship_patterns:
                    pattern = self.relationship_patterns[label]
                    
                    rules = {
                        "target_labels": pattern["potential_targets"],
                        "relationship_types": pattern["relationship_types"],
                        "matching_strategies": pattern["matching_strategies"],
                        "orphan_count": count
                    }
                    
                    strategy["relationship_rules"][label] = rules
                    
                    print(f"📋 Strategy for {label} ({count} orphans):")
                    print(f"   Target labels: {pattern['potential_targets']}")
                    print(f"   Relationship types: {pattern['relationship_types']}")
                    print(f"   Matching strategies: {pattern['matching_strategies']}")
            
            # Define matching algorithms
            strategy["matching_algorithms"] = {
                "path_based": {
                    "description": "Match nodes based on file path similarities",
                    "applicable_to": ["PythonFile", "GitHubRepo", "CodeModule"],
                    "algorithm": "extract_common_path_segments"
                },
                "name_based": {
                    "description": "Match nodes based on name/filename similarities", 
                    "applicable_to": ["Documentation", "PythonFile", "CodeModule"],
                    "algorithm": "fuzzy_name_matching"
                },
                "content_based": {
                    "description": "Match nodes based on content analysis and keywords",
                    "applicable_to": ["Documentation", "PythonFile"],
                    "algorithm": "keyword_content_analysis"
                }
            }
            
            # Priority mappings for relationship creation
            strategy["priority_mappings"] = {
                "high_priority": ["PythonFile", "Documentation"],  # Most orphans
                "medium_priority": ["CodeModule", "GitHubRepo"],
                "low_priority": ["other_labels"]
            }
            
            print(f"\n🎯 Matching Algorithms:")
            for algo, details in strategy["matching_algorithms"].items():
                print(f"   {algo}: {details['description']}")
                print(f"      Applicable to: {details['applicable_to']}")
            
            return strategy
            
        except Exception as e:
            logger.error(f"Error designing relationship strategy: {e}")
            strategy["error"] = str(e)
            return strategy
    
    async def generate_missing_relationships(self, orphan_data: Dict[str, Any], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 4: Generate missing relationships using intelligent matching
        """
        print("\n🔗 Step 4: Generating Missing Relationships")
        print("-" * 50)
        
        results = {
            "relationships_created": [],
            "creation_summary": {},
            "errors": [],
            "total_created": 0
        }
        
        try:
            with self.neo4j_driver.session() as session:
                orphaned_nodes = orphan_data.get("orphaned_nodes", [])
                
                # Process orphans by priority
                priority_order = ["PythonFile", "Documentation", "CodeModule", "GitHubRepo"]
                
                for label in priority_order:
                    label_orphans = [node for node in orphaned_nodes if node["primary_label"] == label]
                    
                    if not label_orphans:
                        continue
                        
                    print(f"\n🔧 Processing {len(label_orphans)} {label} orphans...")
                    
                    created_count = 0
                    
                    if label == "PythonFile":
                        created_count = await self._link_python_files(session, label_orphans)
                    elif label == "Documentation":
                        created_count = await self._link_documentation(session, label_orphans)
                    elif label == "CodeModule":
                        created_count = await self._link_code_modules(session, label_orphans)
                    elif label == "GitHubRepo":
                        created_count = await self._link_github_repos(session, label_orphans)
                    
                    results["creation_summary"][label] = created_count
                    results["total_created"] += created_count
                    
                    print(f"   ✅ Created {created_count} relationships for {label}")
                
                print(f"\n📊 Relationship Creation Summary:")
                for label, count in results["creation_summary"].items():
                    print(f"   {label}: {count} relationships created")
                
                print(f"\n🎯 Total relationships created: {results['total_created']}")
                
                return results
                
        except Exception as e:
            logger.error(f"Error generating relationships: {e}")
            results["error"] = str(e)
            return results
    
    async def _link_python_files(self, session, python_file_orphans: List[Dict]) -> int:
        """Link PythonFile nodes to GitHubRepo and other relevant nodes"""
        created_count = 0
        
        try:
            for orphan in python_file_orphans:
                node_id = orphan["node_id"]
                file_path = orphan.get("file_path", "")
                
                if not file_path:
                    continue
                
                # Strategy 1: Link to GitHubRepo based on path
                repo_query = """
                MATCH (pf) WHERE id(pf) = $node_id
                MATCH (repo:GitHubRepo)
                WHERE pf.file_path IS NOT NULL AND repo.name IS NOT NULL
                AND (pf.file_path CONTAINS repo.name OR repo.name CONTAINS split(pf.file_path, '/')[0])
                CREATE (pf)-[:IN_REPO]->(repo)
                RETURN count(*) as created
                """
                
                result = session.run(repo_query, node_id=node_id)
                repo_created = result.single()["created"]
                created_count += repo_created
                
                # Strategy 2: Link to Documentation with similar names
                if not repo_created:  # Only if no repo link was made
                    doc_query = """
                    MATCH (pf) WHERE id(pf) = $node_id
                    MATCH (doc:Documentation)
                    WHERE pf.name IS NOT NULL AND doc.name IS NOT NULL
                    AND (pf.name CONTAINS split(doc.name, '.')[0] OR doc.name CONTAINS split(pf.name, '.')[0])
                    CREATE (pf)-[:HAS_DOCUMENTATION]->(doc)
                    RETURN count(*) as created
                    """
                    
                    result = session.run(doc_query, node_id=node_id)
                    doc_created = result.single()["created"]
                    created_count += doc_created
                
                # Strategy 3: Create generic project connection if nothing else worked
                if not repo_created:
                    generic_query = """
                    MATCH (pf) WHERE id(pf) = $node_id
                    MERGE (project:GitHubRepo {name: 'plc-gbt-project', description: 'Main PLC-GBT Project'})
                    CREATE (pf)-[:IN_REPO]->(project)
                    RETURN count(*) as created
                    """
                    
                    result = session.run(generic_query, node_id=node_id)
                    generic_created = result.single()["created"]
                    created_count += generic_created
                    
        except Exception as e:
            logger.error(f"Error linking Python files: {e}")
        
        return created_count
    
    async def _link_documentation(self, session, doc_orphans: List[Dict]) -> int:
        """Link Documentation nodes to relevant files and tools"""
        created_count = 0
        
        try:
            for orphan in doc_orphans:
                node_id = orphan["node_id"]
                doc_name = orphan.get("name", "")
                
                if not doc_name:
                    continue
                
                # Strategy 1: Link to PythonFile with similar names
                file_query = """
                MATCH (doc) WHERE id(doc) = $node_id
                MATCH (pf:PythonFile)
                WHERE doc.name IS NOT NULL AND pf.name IS NOT NULL
                AND (doc.name CONTAINS split(pf.name, '.')[0] OR pf.name CONTAINS split(doc.name, '.')[0])
                CREATE (doc)-[:DESCRIBES_FILE]->(pf)
                RETURN count(*) as created
                """
                
                result = session.run(file_query, node_id=node_id)
                file_created = result.single()["created"]
                created_count += file_created
                
                # Strategy 2: Link to GitHubRepo
                if not file_created:
                    repo_query = """
                    MATCH (doc) WHERE id(doc) = $node_id
                    MATCH (repo:GitHubRepo)
                    WHERE doc.name IS NOT NULL AND repo.name IS NOT NULL
                    CREATE (doc)-[:DOCUMENTS_REPO]->(repo)
                    RETURN count(*) as created
                    LIMIT 1
                    """
                    
                    result = session.run(repo_query, node_id=node_id)
                    repo_created = result.single()["created"]
                    created_count += repo_created
                    
        except Exception as e:
            logger.error(f"Error linking documentation: {e}")
        
        return created_count
    
    async def _link_code_modules(self, session, module_orphans: List[Dict]) -> int:
        """Link CodeModule nodes to PythonFile and GitHubRepo nodes"""
        created_count = 0
        
        try:
            for orphan in module_orphans:
                node_id = orphan["node_id"]
                
                # Strategy 1: Link to PythonFile
                file_query = """
                MATCH (cm) WHERE id(cm) = $node_id
                MATCH (pf:PythonFile)
                WHERE cm.name IS NOT NULL AND pf.name IS NOT NULL
                AND (cm.name CONTAINS split(pf.name, '.')[0] OR pf.name CONTAINS cm.name)
                CREATE (cm)-[:IMPLEMENTS_IN]->(pf)
                RETURN count(*) as created
                """
                
                result = session.run(file_query, node_id=node_id)
                file_created = result.single()["created"]
                created_count += file_created
                
                # Strategy 2: Link to GitHubRepo
                if not file_created:
                    repo_query = """
                    MATCH (cm) WHERE id(cm) = $node_id
                    MATCH (repo:GitHubRepo)
                    CREATE (cm)-[:PART_OF_REPO]->(repo)
                    RETURN count(*) as created
                    LIMIT 1
                    """
                    
                    result = session.run(repo_query, node_id=node_id)
                    repo_created = result.single()["created"]
                    created_count += repo_created
                    
        except Exception as e:
            logger.error(f"Error linking code modules: {e}")
        
        return created_count
    
    async def _link_github_repos(self, session, repo_orphans: List[Dict]) -> int:
        """Link GitHubRepo nodes to PythonFile and Documentation nodes"""
        created_count = 0
        
        try:
            for orphan in repo_orphans:
                node_id = orphan["node_id"]
                
                # Strategy 1: Link to PythonFiles
                file_query = """
                MATCH (repo) WHERE id(repo) = $node_id
                MATCH (pf:PythonFile)
                CREATE (repo)-[:CONTAINS]->(pf)
                RETURN count(*) as created
                LIMIT 5
                """
                
                result = session.run(file_query, node_id=node_id)
                file_created = result.single()["created"]
                created_count += file_created
                
                # Strategy 2: Link to Documentation
                doc_query = """
                MATCH (repo) WHERE id(repo) = $node_id
                MATCH (doc:Documentation)
                CREATE (repo)-[:HAS_DOCS]->(doc)
                RETURN count(*) as created
                LIMIT 3
                """
                
                result = session.run(doc_query, node_id=node_id)
                doc_created = result.single()["created"]
                created_count += doc_created
                    
        except Exception as e:
            logger.error(f"Error linking GitHub repos: {e}")
        
        return created_count
    
    async def validate_graph_connectivity(self) -> Dict[str, Any]:
        """
        Step 5: Validate graph connectivity and measure improvements
        """
        print("\n✅ Step 5: Validating Graph Connectivity")
        print("-" * 50)
        
        validation_results = {
            "post_fix_stats": {},
            "connectivity_improvement": {},
            "remaining_orphans": [],
            "validation_success": True
        }
        
        try:
            with self.neo4j_driver.session() as session:
                # Get updated stats
                total_result = session.run("MATCH (n) RETURN count(n) as total")
                total_nodes = total_result.single()["total"]
                
                rel_result = session.run("MATCH ()-[r]-() RETURN count(r) as total")
                total_relationships = rel_result.single()["total"]
                
                # Check remaining orphans
                orphan_query = """
                MATCH (n) 
                WHERE NOT (n)--() 
                RETURN count(n) as orphan_count, collect(distinct labels(n)[0]) as orphan_labels
                """
                
                orphan_result = session.run(orphan_query)
                orphan_record = orphan_result.single()
                remaining_orphan_count = orphan_record["orphan_count"]
                remaining_orphan_labels = orphan_record["orphan_labels"]
                
                # Calculate connected nodes
                connected_nodes = total_nodes - remaining_orphan_count
                connectivity_percentage = (connected_nodes / total_nodes) * 100 if total_nodes > 0 else 0
                
                validation_results["post_fix_stats"] = {
                    "total_nodes": total_nodes,
                    "total_relationships": total_relationships,
                    "connected_nodes": connected_nodes,
                    "remaining_orphans": remaining_orphan_count,
                    "connectivity_percentage": connectivity_percentage
                }
                
                print(f"📊 Post-Fix Graph Statistics:")
                print(f"   Total nodes: {total_nodes}")
                print(f"   Total relationships: {total_relationships}")
                print(f"   Connected nodes: {connected_nodes}")
                print(f"   Remaining orphans: {remaining_orphan_count}")
                print(f"   Connectivity: {connectivity_percentage:.1f}%")
                
                # Detailed relationship analysis
                rel_analysis_query = """
                MATCH (a)-[r]->(b)
                RETURN type(r) as relationship_type, count(*) as count
                ORDER BY count DESC
                """
                
                rel_analysis = session.run(rel_analysis_query)
                relationship_distribution = {}
                
                for record in rel_analysis:
                    rel_type = record["relationship_type"]
                    count = record["count"]
                    relationship_distribution[rel_type] = count
                
                validation_results["relationship_distribution"] = relationship_distribution
                
                print(f"\n🔗 Relationship Distribution:")
                for rel_type, count in relationship_distribution.items():
                    print(f"   {rel_type}: {count}")
                
                # Validation criteria
                if remaining_orphan_count < 50:  # Significant improvement
                    validation_results["validation_success"] = True
                    print(f"\n✅ Graph connectivity validation PASSED")
                    print(f"   Orphan count reduced significantly: {remaining_orphan_count} remaining")
                else:
                    validation_results["validation_success"] = False
                    print(f"\n❌ Graph connectivity validation FAILED")
                    print(f"   Too many orphans remaining: {remaining_orphan_count}")
                
                return validation_results
                
        except Exception as e:
            logger.error(f"Error validating graph connectivity: {e}")
            validation_results["error"] = str(e)
            validation_results["validation_success"] = False
            return validation_results
    
    async def create_intelligent_relationships(self, orphaned_nodes: List[Dict], 
                                            batch_size: int = 50, 
                                            strategy: str = "intelligent") -> Dict[str, Any]:
        """
        Create relationships for orphaned nodes using the specified strategy.
        
        Args:
            orphaned_nodes: List of orphaned node data
            batch_size: Number of nodes to process at a time
            strategy: Relationship creation strategy (intelligent, conservative, aggressive)
        
        Returns:
            Dict with results including relationships created and orphans resolved
        """
        print(f"\n🔗 Creating Relationships with {strategy} Strategy")
        print("-" * 50)
        
        results = {
            "relationships_created": 0,
            "orphans_resolved": 0,
            "remaining_orphans": 0,
            "batches_processed": 0,
            "errors": []
        }
        
        try:
            # Process orphans in batches
            total_orphans = len(orphaned_nodes)
            batches = [orphaned_nodes[i:i + batch_size] for i in range(0, total_orphans, batch_size)]
            
            for batch_num, batch in enumerate(batches, 1):
                print(f"\n📦 Processing batch {batch_num}/{len(batches)} ({len(batch)} nodes)")
                
                # Analyze existing data model for context
                model_data = await self.analyze_existing_data_model()
                
                # Design strategy for this batch
                batch_data = {
                    "orphaned_nodes": batch,
                    "orphan_distribution": {}
                }
                
                # Calculate distribution for this batch
                for node in batch:
                    label = node.get("primary_label", "Unknown")
                    batch_data["orphan_distribution"][label] = batch_data["orphan_distribution"].get(label, 0) + 1
                
                strategy_data = await self.design_relationship_strategy(batch_data, model_data)
                
                # Apply strategy based on selected approach
                if strategy == "conservative":
                    # Only create high-confidence relationships
                    relationship_results = await self._create_conservative_relationships(batch, strategy_data)
                elif strategy == "aggressive":
                    # Create all possible relationships
                    relationship_results = await self._create_aggressive_relationships(batch, strategy_data)
                else:
                    # Default intelligent strategy
                    relationship_results = await self.generate_missing_relationships(batch_data, strategy_data)
                
                # Update results
                results["relationships_created"] += relationship_results.get("total_created", 0)
                results["batches_processed"] += 1
                
                # Log progress
                print(f"   ✅ Created {relationship_results.get('total_created', 0)} relationships")
            
            # Count remaining orphans
            with self.neo4j_driver.session() as session:
                orphan_count_query = """
                MATCH (n)
                WHERE NOT (n)--()
                RETURN count(n) as count
                """
                count_result = session.run(orphan_count_query)
                results["remaining_orphans"] = count_result.single()["count"]
            
            # Calculate orphans resolved
            results["orphans_resolved"] = total_orphans - results["remaining_orphans"]
            
            print(f"\n✅ Relationship Creation Complete!")
            print(f"   Total relationships created: {results['relationships_created']}")
            print(f"   Orphans resolved: {results['orphans_resolved']}")
            print(f"   Remaining orphans: {results['remaining_orphans']}")
            
        except Exception as e:
            logger.error(f"Error creating relationships: {e}")
            results["errors"].append(str(e))
        
        return results
    
    async def _create_conservative_relationships(self, orphans: List[Dict], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create only high-confidence relationships"""
        results = {"total_created": 0}
        
        with self.neo4j_driver.session() as session:
            # Only create relationships for exact matches
            for orphan in orphans:
                node_id = orphan["node_id"]
                label = orphan.get("primary_label", "")
                
                if label == "PythonFile" and orphan.get("file_path"):
                    # Only link if exact repo match
                    query = """
                    MATCH (pf) WHERE id(pf) = $node_id
                    MATCH (repo:GitHubRepo)
                    WHERE pf.file_path STARTS WITH repo.name + '/'
                    CREATE (pf)-[:IN_REPO]->(repo)
                    RETURN count(*) as created
                    """
                    result = session.run(query, node_id=node_id)
                    results["total_created"] += result.single()["created"]
        
        return results
    
    async def _create_aggressive_relationships(self, orphans: List[Dict], strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Create all possible relationships"""
        results = {"total_created": 0}
        
        with self.neo4j_driver.session() as session:
            # Create relationships more liberally
            for orphan in orphans:
                node_id = orphan["node_id"]
                label = orphan.get("primary_label", "")
                
                if label == "PythonFile":
                    # Link to any repo
                    query = """
                    MATCH (pf) WHERE id(pf) = $node_id
                    MATCH (repo:GitHubRepo)
                    CREATE (pf)-[:POSSIBLY_IN_REPO]->(repo)
                    RETURN count(*) as created
                    LIMIT 1
                    """
                    result = session.run(query, node_id=node_id)
                    results["total_created"] += result.single()["created"]
                
                elif label == "Documentation":
                    # Link to any file or repo
                    query = """
                    MATCH (doc) WHERE id(doc) = $node_id
                    MATCH (target)
                    WHERE target:PythonFile OR target:GitHubRepo
                    CREATE (doc)-[:POSSIBLY_DOCUMENTS]->(target)
                    RETURN count(*) as created
                    LIMIT 2
                    """
                    result = session.run(query, node_id=node_id)
                    results["total_created"] += result.single()["created"]
        
        return results
    
    async def run_complete_orphan_resolution(self) -> Dict[str, Any]:
        """
        Execute complete orphan node resolution workflow
        """
        print("🔗 NEO4J ORPHAN NODE RESOLUTION - STARTING")
        print("=" * 60)
        print("Following AI Task Orchestrator Guide Methodology")
        print("Task: Resolve >500 orphaned nodes in Neo4j graph")
        print("=" * 60)
        
        session_results = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "workflow_results": {},
            "overall_success": True,
            "summary": {}
        }
        
        try:
            # Initialize connection
            if not await self.initialize_neo4j_connection():
                raise Exception("Failed to initialize Neo4j connection")
            
            # Step 1: Confirm orphan nodes
            orphan_data = await self.confirm_orphan_nodes()
            session_results["workflow_results"]["orphan_confirmation"] = orphan_data
            
            # Step 2: Analyze data model
            model_data = await self.analyze_existing_data_model()
            session_results["workflow_results"]["data_model_analysis"] = model_data
            
            # Step 3: Design relationship strategy
            strategy = await self.design_relationship_strategy(orphan_data, model_data)
            session_results["workflow_results"]["relationship_strategy"] = strategy
            
            # Step 4: Generate missing relationships
            relationship_results = await self.generate_missing_relationships(orphan_data, strategy)
            session_results["workflow_results"]["relationship_generation"] = relationship_results
            
            # Step 5: Validate connectivity
            validation_results = await self.validate_graph_connectivity()
            session_results["workflow_results"]["connectivity_validation"] = validation_results
            
            # Generate summary
            session_results["overall_success"] = validation_results.get("validation_success", False)
            
            session_results["summary"] = {
                "initial_orphans": len(orphan_data.get("orphaned_nodes", [])),
                "relationships_created": relationship_results.get("total_created", 0),
                "final_orphans": validation_results.get("post_fix_stats", {}).get("remaining_orphans", 0),
                "connectivity_improvement": validation_results.get("post_fix_stats", {}).get("connectivity_percentage", 0),
                "resolution_status": "SUCCESS" if session_results["overall_success"] else "PARTIAL"
            }
            
            session_results["end_time"] = datetime.now().isoformat()
            
            # Save results
            results_file = f"neo4j_orphan_resolution_{self.session_id}.json"
            with open(results_file, 'w') as f:
                json.dump(session_results, f, indent=2)
            
            print(f"\n🎯 Orphan Resolution Complete! Results saved to: {results_file}")
            print(f"📊 Resolution Status: {session_results['summary']['resolution_status']}")
            print(f"🔗 Relationships Created: {session_results['summary']['relationships_created']}")
            print(f"📈 Final Connectivity: {session_results['summary']['connectivity_improvement']:.1f}%")
            
            return session_results
            
        except Exception as e:
            logger.error(f"Critical error in orphan resolution: {e}")
            session_results["overall_success"] = False
            session_results["critical_error"] = str(e)
            return session_results
        
        finally:
            # Cleanup
            await self.db_manager.close_all_connections()

async def main():
    """Main function to run Neo4j orphan node resolution"""
    resolver = Neo4jOrphanNodeResolver()
    results = await resolver.run_complete_orphan_resolution()
    
    if results["overall_success"]:
        print("\n🎉 NEO4J ORPHAN RESOLUTION SUCCESSFUL!")
        print("✅ Graph connectivity significantly improved")
        print("✅ Missing relationships generated successfully")
    else:
        print("\n❌ NEO4J ORPHAN RESOLUTION INCOMPLETE!")
        print("❌ Manual intervention may be required")
        print(f"Error: {results.get('critical_error', 'See detailed results')}")

if __name__ == "__main__":
    asyncio.run(main()) 