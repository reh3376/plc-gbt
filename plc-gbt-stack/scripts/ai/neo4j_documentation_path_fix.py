#!/usr/bin/env python3
"""
🔧 Neo4j Documentation Path Property Fix

Following AI Task Orchestrator Guide methodology to fix the remaining Neo4j issue
identified in comprehensive database audit.

Problem: 1 Documentation node missing path property
Impact: Minor data integrity issue in medium-term memory storage
Solution: Identify and fix missing path properties in Documentation nodes

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: Remaining Issue #2 - Fix Documentation Node Path Property
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Add current directory to path for imports
sys.path.append('.')

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("❌ neo4j driver not available - install with: pip install neo4j")
    sys.exit(1)

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
    else:
        load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jDocumentationPathFix:
    """
    🎯 Neo4j Documentation Path Property Fix
    
    Fixes missing path properties in Documentation nodes for complete data integrity
    following AI Task Orchestrator methodology.
    """
    
    def __init__(self):
        self.driver = None
        self.session_id = f"neo4j_doc_fix_{int(datetime.now().timestamp())}"
        
        # Neo4j configuration
        self.neo4j_config = {
            "uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "user": os.getenv("NEO4J_USER", "neo4j"),
            "password": os.getenv("NEO4J_PASSWORD", "password")
        }

    def connect_to_neo4j(self) -> bool:
        """Establish connection to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_config["uri"],
                auth=(self.neo4j_config["user"], self.neo4j_config["password"])
            )
            
            # Test connection
            with self.driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
            if test_value == 1:
                logger.info("✅ Neo4j connected successfully")
                return True
            else:
                logger.error("❌ Neo4j connection test failed")
                return False
            
        except Exception as e:
            logger.error(f"❌ Neo4j connection failed: {str(e)}")
            return False

    def analyze_documentation_nodes(self) -> Dict[str, Any]:
        """Analyze Documentation nodes to identify path property issues"""
        analysis_results = {
            "total_documentation_nodes": 0,
            "nodes_with_path": 0,
            "nodes_missing_path": 0,
            "missing_path_nodes": [],
            "sample_existing_paths": [],
            "issues_found": []
        }
        
        try:
            with self.driver.session() as session:
                # Count total Documentation nodes
                total_query = "MATCH (d:Documentation) RETURN count(d) as total"
                result = session.run(total_query)
                analysis_results["total_documentation_nodes"] = result.single()["total"]
                
                # Find nodes with path property
                with_path_query = """
                    MATCH (d:Documentation) 
                    WHERE d.path IS NOT NULL 
                    RETURN count(d) as with_path, collect(d.path)[0..5] as sample_paths
                """
                result = session.run(with_path_query)
                record = result.single()
                analysis_results["nodes_with_path"] = record["with_path"]
                analysis_results["sample_existing_paths"] = record["sample_paths"]
                
                # Find nodes missing path property
                missing_path_query = """
                    MATCH (d:Documentation) 
                    WHERE d.path IS NULL 
                    RETURN d.title as title, d.doc_type as doc_type, id(d) as node_id
                """
                result = session.run(missing_path_query)
                missing_nodes = []
                for record in result:
                    missing_nodes.append({
                        "title": record["title"],
                        "doc_type": record["doc_type"],
                        "node_id": record["node_id"]
                    })
                
                analysis_results["nodes_missing_path"] = len(missing_nodes)
                analysis_results["missing_path_nodes"] = missing_nodes
                
                if missing_nodes:
                    analysis_results["issues_found"].append(f"{len(missing_nodes)} Documentation nodes missing path property")
                
                print(f"📊 Documentation Node Analysis:")
                print(f"   Total Documentation nodes: {analysis_results['total_documentation_nodes']}")
                print(f"   Nodes with path property: {analysis_results['nodes_with_path']}")
                print(f"   Nodes missing path property: {analysis_results['nodes_missing_path']}")
                
                if missing_nodes:
                    print(f"\n❌ Missing Path Nodes:")
                    for node in missing_nodes:
                        print(f"   - Node ID {node['node_id']}: '{node['title']}' ({node['doc_type']})")
                
                return analysis_results
                
        except Exception as e:
            logger.error(f"Documentation node analysis failed: {str(e)}")
            return {"error": str(e)}

    def generate_path_values(self, missing_nodes: List[Dict[str, Any]]) -> Dict[int, str]:
        """Generate appropriate path values for nodes missing path property"""
        path_assignments = {}
        
        for node in missing_nodes:
            node_id = node["node_id"]
            title = node["title"] or "unknown"
            doc_type = node["doc_type"] or "markdown"
            
            # Generate path based on available information
            if title and title != "unknown":
                # Create path from title
                safe_title = title.lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
                safe_title = "".join(c for c in safe_title if c.isalnum() or c in "_-.")
                
                if doc_type:
                    extension = ".md" if doc_type == "markdown" else f".{doc_type}"
                else:
                    extension = ".md"
                
                generated_path = f"docs/{safe_title}{extension}"
            else:
                # Fallback path for unknown titles
                generated_path = f"docs/documentation_node_{node_id}.md"
            
            path_assignments[node_id] = generated_path
            print(f"   Generated path for node {node_id}: {generated_path}")
        
        return path_assignments

    def fix_missing_path_properties(self, path_assignments: Dict[int, str]) -> Dict[str, Any]:
        """Fix missing path properties in Documentation nodes"""
        fix_results = {
            "nodes_updated": 0,
            "successful_updates": [],
            "failed_updates": [],
            "errors": []
        }
        
        try:
            with self.driver.session() as session:
                for node_id, path_value in path_assignments.items():
                    try:
                        # Update node with path property
                        update_query = """
                            MATCH (d:Documentation) 
                            WHERE id(d) = $node_id 
                            SET d.path = $path_value,
                                d.last_updated = datetime()
                            RETURN d.title as title, d.path as new_path
                        """
                        
                        result = session.run(update_query, node_id=node_id, path_value=path_value)
                        record = result.single()
                        
                        if record:
                            fix_results["nodes_updated"] += 1
                            fix_results["successful_updates"].append({
                                "node_id": node_id,
                                "title": record["title"],
                                "new_path": record["new_path"]
                            })
                            print(f"   ✅ Updated node {node_id}: '{record['title']}' -> {record['new_path']}")
                        else:
                            fix_results["failed_updates"].append({
                                "node_id": node_id,
                                "error": "Node not found or update failed"
                            })
                            
                    except Exception as e:
                        error_msg = f"Failed to update node {node_id}: {str(e)}"
                        fix_results["errors"].append(error_msg)
                        fix_results["failed_updates"].append({
                            "node_id": node_id,
                            "error": str(e)
                        })
                        logger.error(error_msg)
            
            return fix_results
            
        except Exception as e:
            logger.error(f"Path property fix failed: {str(e)}")
            return {"error": str(e)}

    def validate_fix_results(self) -> Dict[str, Any]:
        """Validate that all Documentation nodes now have path properties"""
        validation_results = {
            "all_nodes_have_path": True,
            "total_documentation_nodes": 0,
            "nodes_with_path": 0,
            "nodes_still_missing_path": 0,
            "remaining_issues": []
        }
        
        try:
            with self.driver.session() as session:
                # Check total nodes
                total_query = "MATCH (d:Documentation) RETURN count(d) as total"
                result = session.run(total_query)
                validation_results["total_documentation_nodes"] = result.single()["total"]
                
                # Check nodes with path
                with_path_query = "MATCH (d:Documentation) WHERE d.path IS NOT NULL RETURN count(d) as with_path"
                result = session.run(with_path_query)
                validation_results["nodes_with_path"] = result.single()["with_path"]
                
                # Check nodes still missing path
                missing_path_query = "MATCH (d:Documentation) WHERE d.path IS NULL RETURN count(d) as missing"
                result = session.run(missing_path_query)
                validation_results["nodes_still_missing_path"] = result.single()["missing"]
                
                # Determine if all nodes have path
                if validation_results["nodes_still_missing_path"] > 0:
                    validation_results["all_nodes_have_path"] = False
                    validation_results["remaining_issues"].append(
                        f"{validation_results['nodes_still_missing_path']} Documentation nodes still missing path property"
                    )
                
                return validation_results
                
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {"error": str(e)}

    def run_documentation_path_fix(self) -> Dict[str, Any]:
        """Execute complete Documentation path property fix process"""
        print("🚀 Starting Neo4j Documentation Path Property Fix")
        print("Following AI Task Orchestrator Guide Methodology")
        print("Task: Remaining Issue #2 - Fix Documentation Node Path Property")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # Initialize result tracking
        results = {
            "session_id": self.session_id,
            "start_time": start_time.isoformat(),
            "success": False,
            "phases": {}
        }
        
        try:
            # Phase 1: Database Connection
            print("\n📋 Phase 1: Database Connection")
            if not self.connect_to_neo4j():
                results["error"] = "Failed to connect to Neo4j database"
                return results
            
            results["phases"]["connection"] = {"status": "success", "message": "Neo4j connected"}
            
            # Phase 2: Analyze Documentation Nodes
            print("\n📋 Phase 2: Analyze Documentation Nodes")
            analysis = self.analyze_documentation_nodes()
            results["phases"]["analysis"] = analysis
            
            if "error" in analysis:
                results["error"] = f"Analysis failed: {analysis['error']}"
                return results
            
            # Phase 3: Generate Path Values
            print("\n📋 Phase 3: Generate Path Values for Missing Nodes")
            if analysis["nodes_missing_path"] > 0:
                path_assignments = self.generate_path_values(analysis["missing_path_nodes"])
                results["phases"]["path_generation"] = {"path_assignments": path_assignments}
            else:
                print("   ℹ️  No missing path properties found - all nodes already have paths")
                results["phases"]["path_generation"] = {"path_assignments": {}}
                path_assignments = {}
            
            # Phase 4: Fix Missing Path Properties
            print("\n📋 Phase 4: Fix Missing Path Properties")
            if path_assignments:
                fix_results = self.fix_missing_path_properties(path_assignments)
                results["phases"]["path_fixes"] = fix_results
                
                if "error" in fix_results:
                    results["error"] = f"Path fix failed: {fix_results['error']}"
                    return results
            else:
                print("   ℹ️  No path fixes needed")
                results["phases"]["path_fixes"] = {"nodes_updated": 0, "successful_updates": []}
            
            # Phase 5: Validate Fix Results
            print("\n📋 Phase 5: Validate Fix Results")
            validation_results = self.validate_fix_results()
            results["phases"]["validation"] = validation_results
            
            # Calculate final results
            duration = (datetime.now() - start_time).total_seconds()
            results["duration_seconds"] = duration
            results["success"] = (
                validation_results.get("all_nodes_have_path", False) and
                len(validation_results.get("remaining_issues", [])) == 0
            )
            results["end_time"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Documentation path fix failed: {str(e)}")
            traceback.print_exc()
            results["error"] = str(e)
            return results
            
        finally:
            if self.driver:
                self.driver.close()
                logger.info("Neo4j connection closed")

async def main():
    """Main execution function"""
    fixer = Neo4jDocumentationPathFix()
    results = fixer.run_documentation_path_fix()
    
    if results.get("success"):
        print(f"\n🎯 Neo4j Documentation Path Fix Complete!")
        print("=" * 80)
        print(f"✅ Success: Documentation path properties fixed successfully")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        
        # Display fix results
        validation = results['phases']['validation']
        fix_results = results['phases']['path_fixes']
        
        print(f"📊 Total Documentation nodes: {validation['total_documentation_nodes']}")
        print(f"📊 Nodes with path property: {validation['nodes_with_path']}")
        print(f"📊 Nodes updated: {fix_results['nodes_updated']}")
        
        if validation.get('all_nodes_have_path'):
            print(f"✅ All Documentation nodes now have path properties")
        
        # Display updated nodes
        successful_updates = fix_results.get('successful_updates', [])
        if successful_updates:
            print(f"\n🔧 Updated Nodes:")
            for update in successful_updates:
                print(f"   ✅ {update['title']} -> {update['new_path']}")
        
        # Save results
        results_file = f"neo4j_documentation_path_fix_{fixer.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved: {results_file}")
        
        return 0
    else:
        print(f"\n❌ Neo4j Documentation Path Fix Failed!")
        print("=" * 80)
        if "error" in results:
            print(f"Error: {results['error']}")
        
        # Display any remaining issues
        validation = results.get('phases', {}).get('validation', {})
        remaining_issues = validation.get('remaining_issues', [])
        if remaining_issues:
            print(f"\nRemaining Issues:")
            for issue in remaining_issues:
                print(f"   ❌ {issue}")
        
        return 1

if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main())) 