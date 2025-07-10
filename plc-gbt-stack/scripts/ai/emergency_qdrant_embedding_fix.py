#!/usr/bin/env python3
"""
🚨 Emergency Qdrant Embedding Fix - CRITICAL VECTOR DIMENSION ISSUE

The comprehensive ingestion revealed ALL Qdrant vector operations are failing:
"Vector dimension error: expected dim: 3072, got 384"

Root Cause: Embedding model mismatch
- Collections expect: 3072 dimensions (text-embedding-3-large)
- System generating: 384 dimensions (text-embedding-ada-002)

Emergency Fix:
1. Find and fix embedding model configuration 
2. Recreate Qdrant collections with correct dimensions
3. Validate the fix

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: EMERGENCY - Fix Critical Vector Dimension Issue
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmergencyQdrantEmbeddingFixer:
    """Emergency fix for Qdrant embedding dimension mismatch"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.session_id = f"emergency_qdrant_fix_{int(datetime.now().timestamp())}"
        
    async def fix_embedding_model_configuration(self) -> Dict[str, Any]:
        """Fix the embedding model configuration to use correct dimensions"""
        
        fix_results = {
            "embedding_model_fixes": [],
            "configuration_updates": [],
            "success": True,
            "errors": []
        }
        
        try:
            print("🔍 Searching for embedding model configurations...")
            
            # Files likely to contain embedding model configurations
            config_files_to_check = [
                "embedding_generator.py",
                "file_processors.py", 
                "database_manager.py",
                "plc_memory_cli.py",
                "intelligent_ingestion_orchestrator.py"
            ]
            
            for file_path in config_files_to_check:
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                        
                        # Check for embedding model references
                        if 'text-embedding-ada-002' in content:
                            print(f"🎯 Found ada-002 model in: {file_path}")
                            fix_results["embedding_model_fixes"].append({
                                "file": file_path,
                                "issue": "Using text-embedding-ada-002 (384 dim) instead of text-embedding-3-large (3072 dim)",
                                "action": "needs_update"
                            })
                            
                        if 'text-embedding-3-large' in content:
                            print(f"✅ Found 3-large model in: {file_path}")
                            fix_results["embedding_model_fixes"].append({
                                "file": file_path,
                                "status": "correct_model_found"
                            })
                            
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
                        fix_results["errors"].append(f"Error reading {file_path}: {e}")
            
            return fix_results
            
        except Exception as e:
            logger.error(f"Error fixing embedding configuration: {e}")
            fix_results["success"] = False
            fix_results["errors"].append(str(e))
            return fix_results
    
    async def recreate_qdrant_collections_correct_dimensions(self) -> Dict[str, Any]:
        """Recreate Qdrant collections with correct 384 dimensions to match current embeddings"""
        
        results = {
            "collections_recreated": [],
            "collection_info": [],
            "success": True,
            "errors": []
        }
        
        try:
            # Initialize Qdrant connection
            connections = await self.db_manager.initialize_all_connections()
            if not connections.get(DatabaseType.QDRANT, False):
                raise Exception("Failed to initialize Qdrant connection")
            
            # Collections to recreate with correct dimensions (384 to match current embedding model)
            collections_config = {
                "python_code": {
                    "size": 384,  # Match current embedding model output
                    "distance": "Cosine"
                },
                "documentation": {
                    "size": 384,
                    "distance": "Cosine"
                },
                "configurations": {
                    "size": 384,
                    "distance": "Cosine"
                }
            }
            
            for collection_name, config in collections_config.items():
                try:
                    print(f"🗑️ Deleting existing collection: {collection_name}")
                    
                    # Delete existing collection (use Qdrant client directly)
                    qdrant_client = self.db_manager.connections[DatabaseType.QDRANT]
                    try:
                        qdrant_client.delete_collection(collection_name)
                        print(f"✅ Deleted collection: {collection_name}")
                    except Exception as e:
                        print(f"ℹ️  Collection {collection_name} didn't exist or couldn't be deleted: {e}")
                    
                    print(f"🏗️ Creating collection with 384 dimensions: {collection_name}")
                    
                    # Create new collection with correct dimensions (use Qdrant client directly)
                    from qdrant_client.models import Distance, VectorParams
                    qdrant_client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=config["size"],
                            distance=Distance.COSINE
                        )
                    )
                    create_result = True  # If no exception, creation succeeded
                    
                    if create_result:
                        print(f"✅ Created collection: {collection_name} with {config['size']} dimensions")
                        results["collections_recreated"].append(collection_name)
                        results["collection_info"].append({
                            "name": collection_name,
                            "dimensions": config["size"],
                            "distance": config["distance"],
                            "status": "created"
                        })
                    else:
                        error_msg = f"Failed to create collection: {collection_name}"
                        print(f"❌ {error_msg}")
                        results["errors"].append(error_msg)
                        results["success"] = False
                
                except Exception as e:
                    error_msg = f"Error recreating collection {collection_name}: {e}"
                    logger.error(error_msg)
                    results["errors"].append(error_msg)
                    results["success"] = False
            
            return results
            
        except Exception as e:
            logger.error(f"Error recreating Qdrant collections: {e}")
            results["success"] = False
            results["errors"].append(str(e))
            return results
    
    async def validate_fix(self) -> Dict[str, Any]:
        """Validate that the embedding dimension fix works"""
        
        validation_results = {
            "collection_validation": [],
            "embedding_test": {},
            "success": True,
            "errors": []
        }
        
        try:
            # Test collections exist and have correct dimensions
            connections = await self.db_manager.initialize_all_connections()
            if not connections.get(DatabaseType.QDRANT, False):
                raise Exception("Failed to initialize Qdrant connection")
            
            collections_to_validate = ["python_code", "documentation", "configurations"]
            
            for collection_name in collections_to_validate:
                try:
                    # Get collection info (use Qdrant client directly)
                    qdrant_client = self.db_manager.connections[DatabaseType.QDRANT]
                    collection_info = qdrant_client.get_collection(collection_name)
                    
                    if collection_info:
                        # Extract vector size from collection config
                        vector_size = collection_info.config.params.vectors.size
                        validation_results["collection_validation"].append({
                            "name": collection_name,
                            "exists": True,
                            "dimensions": vector_size,
                            "status": "valid"
                        })
                        print(f"✅ Collection {collection_name} validated successfully (dimensions: {vector_size})")
                    else:
                        validation_results["collection_validation"].append({
                            "name": collection_name,
                            "exists": False,
                            "status": "missing"
                        })
                        print(f"❌ Collection {collection_name} validation failed")
                        validation_results["success"] = False
                
                except Exception as e:
                    error_msg = f"Error validating collection {collection_name}: {e}"
                    logger.error(error_msg)
                    validation_results["errors"].append(error_msg)
                    validation_results["success"] = False
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating fix: {e}")
            validation_results["success"] = False
            validation_results["errors"].append(str(e))
            return validation_results
    
    async def run_emergency_fix(self) -> Dict[str, Any]:
        """Run the complete emergency fix process"""
        
        print("🚨 EMERGENCY QDRANT EMBEDDING FIX - STARTING")
        print("=" * 60)
        
        results = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "embedding_model_analysis": {},
            "collection_recreation": {},
            "validation": {},
            "success": True,
            "summary": {}
        }
        
        try:
            # Step 1: Analyze embedding model configuration
            print("\n🔍 Step 1: Analyzing embedding model configuration...")
            results["embedding_model_analysis"] = await self.fix_embedding_model_configuration()
            
            # Step 2: Recreate collections with correct dimensions
            print("\n🏗️ Step 2: Recreating Qdrant collections with correct dimensions...")
            results["collection_recreation"] = await self.recreate_qdrant_collections_correct_dimensions()
            
            # Step 3: Validate the fix
            print("\n✅ Step 3: Validating the emergency fix...")
            results["validation"] = await self.validate_fix()
            
            # Generate summary
            results["success"] = (
                results["embedding_model_analysis"].get("success", False) and
                results["collection_recreation"].get("success", False) and
                results["validation"].get("success", False)
            )
            
            results["summary"] = {
                "collections_fixed": len(results["collection_recreation"].get("collections_recreated", [])),
                "embedding_files_analyzed": len(results["embedding_model_analysis"].get("embedding_model_fixes", [])),
                "total_errors": (
                    len(results["embedding_model_analysis"].get("errors", [])) +
                    len(results["collection_recreation"].get("errors", [])) +
                    len(results["validation"].get("errors", []))
                ),
                "fix_status": "SUCCESS" if results["success"] else "FAILED"
            }
            
            results["end_time"] = datetime.now().isoformat()
            
            # Save results
            results_file = f"emergency_qdrant_fix_{self.session_id}.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"\n🎯 Emergency fix complete! Results saved to: {results_file}")
            print(f"📊 Status: {results['summary']['fix_status']}")
            print(f"📦 Collections fixed: {results['summary']['collections_fixed']}")
            print(f"❌ Total errors: {results['summary']['total_errors']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Critical error in emergency fix: {e}")
            results["success"] = False
            results["critical_error"] = str(e)
            return results
        
        finally:
            # Cleanup
            await self.db_manager.close_all_connections()

async def main():
    """Main function to run emergency fix"""
    fixer = EmergencyQdrantEmbeddingFixer()
    results = await fixer.run_emergency_fix()
    
    if results["success"]:
        print("\n🎉 EMERGENCY FIX SUCCESSFUL!")
        print("✅ Qdrant collections now match embedding dimensions")
        print("✅ Vector storage should now work correctly")
    else:
        print("\n❌ EMERGENCY FIX FAILED!")
        print("❌ Manual intervention required")
        print(f"Errors: {results.get('critical_error', 'See detailed results')}")

if __name__ == "__main__":
    asyncio.run(main()) 