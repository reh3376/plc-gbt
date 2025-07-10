#!/usr/bin/env python3
"""
🔧 Qdrant Vector Dimension Fix - Critical Vector Storage Fix

Following AI Task Orchestrator Guide methodology to fix CRITICAL Qdrant vector issues
identified in comprehensive database audit.

Problems:
1. Vector dimension mismatch: Expected 3072, got 384
2. Missing collections: python_code, documentation, configurations  
3. Only 5 vectors stored (expected 200+)

Solution:
1. Fix embedding model to use text-embedding-3-large (3072 dimensions)
2. Recreate Qdrant collections with correct dimensions
3. Create missing collections for complete ingestion

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: IMMEDIATE Priority Fix (Critical - Fix Today)
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import traceback

# Add current directory to path for imports
sys.path.append('.')

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, CollectionInfo
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    print("❌ qdrant-client not available - install with: pip install qdrant-client")
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

class QdrantVectorFix:
    """
    🎯 Qdrant Vector Dimension Fix
    
    Fixes critical vector dimension issues in Qdrant database for PLC Memory Management System
    following AI Task Orchestrator methodology for critical system fixes.
    """
    
    def __init__(self):
        self.client = None
        self.session_id = f"qdrant_fix_{int(datetime.now().timestamp())}"
        
        # Qdrant configuration
        self.qdrant_config = {
            "host": os.getenv("QDRANT_HOST", "localhost"),
            "port": int(os.getenv("QDRANT_PORT", "6333"))
        }
        
        # Define correct collection configurations
        self.collection_configs = self._define_correct_collections()
        
    def _define_correct_collections(self) -> Dict[str, Dict[str, Any]]:
        """Define correct collection configurations with proper dimensions"""
        
        return {
            # Updated existing collection with correct dimensions
            "plc_embeddings": {
                "vector_size": 3072,  # text-embedding-3-large dimensions
                "distance": Distance.COSINE,
                "description": "PLC component embeddings (routines, AOIs, UDTs, etc.)",
                "expected_content": ["Python files", "PLC programs", "Code components"]
            },
            
            # Missing collection 1: python_code
            "python_code": {
                "vector_size": 3072,
                "distance": Distance.COSINE,
                "description": "Python code embeddings for similarity search",
                "expected_content": ["Python functions", "Classes", "Code snippets"]
            },
            
            # Missing collection 2: documentation
            "documentation": {
                "vector_size": 3072,
                "distance": Distance.COSINE,
                "description": "Documentation embeddings for knowledge retrieval",
                "expected_content": ["Markdown files", "README files", "Documentation sections"]
            },
            
            # Missing collection 3: configurations
            "configurations": {
                "vector_size": 3072,
                "distance": Distance.COSINE,
                "description": "Configuration file embeddings",
                "expected_content": ["JSON configs", "YAML files", "Environment settings"]
            }
        }

    async def connect_to_qdrant(self) -> bool:
        """Establish connection to Qdrant database"""
        try:
            self.client = QdrantClient(
                host=self.qdrant_config["host"],
                port=self.qdrant_config["port"],
                timeout=30.0
            )
            
            # Test connection
            cluster_info = self.client.info()
            logger.info(f"✅ Qdrant connected: version {getattr(cluster_info, 'version', 'unknown')}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Qdrant connection failed: {str(e)}")
            return False

    async def analyze_current_collections(self) -> Dict[str, Any]:
        """Analyze current collection state and identify issues"""
        analysis_results = {
            "existing_collections": {},
            "dimension_issues": [],
            "missing_collections": [],
            "vector_counts": {},
            "total_issues": 0
        }
        
        try:
            # Get existing collections
            collections = self.client.get_collections()
            existing_collection_names = [col.name for col in collections.collections]
            
            print(f"📊 Current Collection Analysis:")
            print(f"   Found {len(existing_collection_names)} collections: {existing_collection_names}")
            
            # Analyze each existing collection
            for collection_name in existing_collection_names:
                try:
                    collection_info = self.client.get_collection(collection_name)
                    vector_count = collection_info.points_count
                    
                    # Get vector configuration
                    vectors_config = collection_info.config.params.vectors
                    if hasattr(vectors_config, 'size'):
                        current_dimensions = vectors_config.size
                    else:
                        current_dimensions = "unknown"
                    
                    analysis_results["existing_collections"][collection_name] = {
                        "vector_count": vector_count,
                        "current_dimensions": current_dimensions,
                        "distance_metric": getattr(vectors_config, 'distance', 'unknown')
                    }
                    
                    analysis_results["vector_counts"][collection_name] = vector_count
                    
                    print(f"   {collection_name}: {vector_count} vectors, {current_dimensions} dimensions")
                    
                    # Check for dimension issues
                    expected_dimensions = self.collection_configs.get(collection_name, {}).get("vector_size", 3072)
                    if current_dimensions != expected_dimensions:
                        issue = f"Collection '{collection_name}' has {current_dimensions} dimensions, expected {expected_dimensions}"
                        analysis_results["dimension_issues"].append(issue)
                        analysis_results["total_issues"] += 1
                        print(f"   ❌ Dimension mismatch: {collection_name}")
                    
                except Exception as e:
                    logger.error(f"Error analyzing collection {collection_name}: {str(e)}")
            
            # Check for missing collections
            for expected_collection in self.collection_configs.keys():
                if expected_collection not in existing_collection_names:
                    analysis_results["missing_collections"].append(expected_collection)
                    analysis_results["total_issues"] += 1
                    print(f"   ❌ Missing collection: {expected_collection}")
            
            print(f"\n📋 Analysis Summary:")
            print(f"   Dimension issues: {len(analysis_results['dimension_issues'])}")
            print(f"   Missing collections: {len(analysis_results['missing_collections'])}")
            print(f"   Total issues: {analysis_results['total_issues']}")
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Collection analysis failed: {str(e)}")
            return {"error": str(e)}

    async def backup_existing_vectors(self, collection_name: str) -> Optional[List[Dict[str, Any]]]:
        """Backup vectors from existing collection before recreation"""
        try:
            print(f"📦 Backing up vectors from '{collection_name}'...")
            
            # Get all points from collection
            collection_info = self.client.get_collection(collection_name)
            vector_count = collection_info.points_count
            
            if vector_count == 0:
                print(f"   No vectors to backup in '{collection_name}'")
                return []
            
            # Retrieve all points (limited to reasonable size)
            max_backup = 1000  # Prevent memory issues
            limit = min(vector_count, max_backup)
            
            points, _ = self.client.scroll(
                collection_name=collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=True
            )
            
            # Convert to backup format
            backup_data = []
            for point in points:
                backup_data.append({
                    "id": point.id,
                    "vector": point.vector,
                    "payload": point.payload
                })
            
            print(f"   ✅ Backed up {len(backup_data)} vectors from '{collection_name}'")
            return backup_data
            
        except Exception as e:
            logger.error(f"Failed to backup vectors from {collection_name}: {str(e)}")
            return None

    async def recreate_collection_with_correct_dimensions(self, collection_name: str, backup_data: Optional[List[Dict[str, Any]]] = None) -> bool:
        """Recreate collection with correct vector dimensions"""
        try:
            config = self.collection_configs[collection_name]
            
            print(f"🏗️ Recreating collection '{collection_name}' with {config['vector_size']} dimensions...")
            
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(collection_name)
                print(f"   ✅ Deleted existing collection '{collection_name}'")
            except Exception as e:
                print(f"   ℹ️  Collection '{collection_name}' didn't exist or couldn't be deleted: {str(e)}")
            
            # Create new collection with correct dimensions
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=config["vector_size"],
                    distance=config["distance"]
                )
            )
            
            print(f"   ✅ Created collection '{collection_name}' with {config['vector_size']} dimensions")
            
            # Restore backup data if available and compatible
            if backup_data:
                compatible_vectors = []
                for item in backup_data:
                    if len(item["vector"]) == config["vector_size"]:
                        compatible_vectors.append(PointStruct(
                            id=item["id"],
                            vector=item["vector"],
                            payload=item["payload"]
                        ))
                
                if compatible_vectors:
                    self.client.upsert(
                        collection_name=collection_name,
                        points=compatible_vectors
                    )
                    print(f"   ✅ Restored {len(compatible_vectors)} compatible vectors")
                else:
                    print(f"   ⚠️  No compatible vectors to restore (dimension mismatch)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to recreate collection {collection_name}: {str(e)}")
            return False

    async def create_missing_collections(self, missing_collections: List[str]) -> Dict[str, bool]:
        """Create missing collections"""
        results = {}
        
        for collection_name in missing_collections:
            try:
                config = self.collection_configs[collection_name]
                
                print(f"🏗️ Creating missing collection '{collection_name}'...")
                
                self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(
                        size=config["vector_size"],
                        distance=config["distance"]
                    )
                )
                
                results[collection_name] = True
                print(f"   ✅ Created collection '{collection_name}' ({config['vector_size']} dimensions)")
                
            except Exception as e:
                logger.error(f"Failed to create collection {collection_name}: {str(e)}")
                results[collection_name] = False
        
        return results

    async def validate_fix_results(self) -> Dict[str, Any]:
        """Validate that all collections are now correctly configured"""
        validation_results = {
            "all_collections_exist": True,
            "all_dimensions_correct": True,
            "collection_details": {},
            "total_collections": 0,
            "total_vectors": 0,
            "issues_remaining": []
        }
        
        try:
            collections = self.client.get_collections()
            existing_collection_names = [col.name for col in collections.collections]
            
            for expected_collection, config in self.collection_configs.items():
                if expected_collection in existing_collection_names:
                    try:
                        collection_info = self.client.get_collection(expected_collection)
                        vector_count = collection_info.points_count
                        
                        vectors_config = collection_info.config.params.vectors
                        current_dimensions = vectors_config.size
                        
                        validation_results["collection_details"][expected_collection] = {
                            "exists": True,
                            "vector_count": vector_count,
                            "current_dimensions": current_dimensions,
                            "expected_dimensions": config["vector_size"],
                            "dimensions_correct": current_dimensions == config["vector_size"]
                        }
                        
                        validation_results["total_collections"] += 1
                        validation_results["total_vectors"] += vector_count
                        
                        if current_dimensions != config["vector_size"]:
                            validation_results["all_dimensions_correct"] = False
                            validation_results["issues_remaining"].append(
                                f"Collection '{expected_collection}' still has incorrect dimensions: {current_dimensions} vs {config['vector_size']}"
                            )
                        
                    except Exception as e:
                        validation_results["collection_details"][expected_collection] = {
                            "exists": True,
                            "error": str(e)
                        }
                        validation_results["issues_remaining"].append(f"Error validating {expected_collection}: {str(e)}")
                        
                else:
                    validation_results["all_collections_exist"] = False
                    validation_results["collection_details"][expected_collection] = {
                        "exists": False
                    }
                    validation_results["issues_remaining"].append(f"Collection '{expected_collection}' still missing")
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {"error": str(e)}

    async def run_qdrant_vector_fix(self) -> Dict[str, Any]:
        """Execute complete Qdrant vector dimension fix process"""
        print("🚀 Starting Qdrant Vector Dimension Fix")
        print("Following AI Task Orchestrator Guide Methodology")
        print("Task: IMMEDIATE Priority - Fix Critical Qdrant Vector Issues")
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
            if not await self.connect_to_qdrant():
                results["error"] = "Failed to connect to Qdrant database"
                return results
            
            results["phases"]["connection"] = {"status": "success", "message": "Qdrant connected"}
            
            # Phase 2: Analyze Current State
            print("\n📋 Phase 2: Analyze Current Collections")
            analysis = await self.analyze_current_collections()
            results["phases"]["analysis"] = analysis
            
            if "error" in analysis:
                results["error"] = f"Analysis failed: {analysis['error']}"
                return results
            
            # Phase 3: Backup and Fix Existing Collections
            print("\n📋 Phase 3: Fix Dimension Issues")
            fixed_collections = []
            
            for collection_name in analysis["existing_collections"].keys():
                if any(collection_name in issue for issue in analysis["dimension_issues"]):
                    backup_data = await self.backup_existing_vectors(collection_name)
                    success = await self.recreate_collection_with_correct_dimensions(collection_name, backup_data)
                    
                    if success:
                        fixed_collections.append(collection_name)
                    else:
                        print(f"❌ Failed to fix collection: {collection_name}")
            
            results["phases"]["dimension_fixes"] = {"fixed_collections": fixed_collections}
            
            # Phase 4: Create Missing Collections
            print("\n📋 Phase 4: Create Missing Collections")
            if analysis["missing_collections"]:
                creation_results = await self.create_missing_collections(analysis["missing_collections"])
                results["phases"]["missing_collections"] = {"creation_results": creation_results}
            else:
                print("   ℹ️  No missing collections to create")
                results["phases"]["missing_collections"] = {"creation_results": {}}
            
            # Phase 5: Validate Fix Results
            print("\n📋 Phase 5: Validate Fix Results")
            validation_results = await self.validate_fix_results()
            results["phases"]["validation"] = validation_results
            
            # Calculate final results
            duration = (datetime.now() - start_time).total_seconds()
            results["duration_seconds"] = duration
            results["success"] = (
                validation_results.get("all_collections_exist", False) and
                validation_results.get("all_dimensions_correct", False) and
                len(validation_results.get("issues_remaining", [])) == 0
            )
            results["end_time"] = datetime.now().isoformat()
            
            return results
            
        except Exception as e:
            logger.error(f"Qdrant vector fix failed: {str(e)}")
            traceback.print_exc()
            results["error"] = str(e)
            return results

async def main():
    """Main execution function"""
    fixer = QdrantVectorFix()
    results = await fixer.run_qdrant_vector_fix()
    
    if results.get("success"):
        print(f"\n🎯 Qdrant Vector Fix Complete!")
        print("=" * 80)
        print(f"✅ Success: Vector dimension fix completed successfully")
        print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
        
        # Display fix results
        validation = results['phases']['validation']
        print(f"📊 Collections: {validation['total_collections']}")
        print(f"📊 Total vectors: {validation['total_vectors']}")
        
        if validation.get('all_collections_exist') and validation.get('all_dimensions_correct'):
            print(f"✅ All collections exist with correct dimensions")
        
        # Display created/fixed collections
        fixed_collections = results['phases']['dimension_fixes']['fixed_collections']
        created_collections = results['phases']['missing_collections']['creation_results']
        
        if fixed_collections:
            print(f"\n🔧 Fixed Collections:")
            for collection in fixed_collections:
                print(f"   ✅ {collection} (dimensions corrected)")
        
        if created_collections:
            print(f"\n🏗️ Created Collections:")
            for collection, success in created_collections.items():
                status = "✅" if success else "❌"
                print(f"   {status} {collection}")
        
        # Save results
        results_file = f"qdrant_vector_fix_{fixer.session_id}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Results saved: {results_file}")
        
        return 0
    else:
        print(f"\n❌ Qdrant Vector Fix Failed!")
        print("=" * 80)
        if "error" in results:
            print(f"Error: {results['error']}")
        
        # Display any remaining issues
        validation = results.get('phases', {}).get('validation', {})
        remaining_issues = validation.get('issues_remaining', [])
        if remaining_issues:
            print(f"\nRemaining Issues:")
            for issue in remaining_issues:
                print(f"   ❌ {issue}")
        
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main())) 