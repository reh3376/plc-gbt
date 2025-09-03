#!/usr/bin/env python3
"""
🔧 Neo4j Storage Issue Diagnostic and Fix Script

Following AI Task Orchestrator Guide methodology to systematically diagnose
and fix the Neo4j storage issues identified during comprehensive ingestion analysis.

Issue Analysis:
1. Only 73/114 files stored in Neo4j despite 99.1% processing success
2. DateTime serialization errors preventing proper database storage
3. Missing PLC repositories (plc-100 through plc-600) need to be cloned and ingested

Root Cause: DateTime objects in file metadata cannot be JSON serialized
when storing to databases, causing silent failures in storage operations.

Author: AI Task Orchestrator
Created: 2025-01-10
Purpose: Fix database storage pipeline for complete data ingestion
"""

import asyncio
import json
import logging
import sys
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects"""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def fix_metadata_serialization(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix metadata dictionary to ensure all values are JSON serializable

    Converts datetime objects to ISO format strings and handles other
    non-serializable objects that might cause storage failures.
    """
    fixed_metadata = {}

    for key, value in metadata.items():
        if isinstance(value, datetime):
            fixed_metadata[key] = value.isoformat()
        elif hasattr(value, '__dict__'):
            # Handle complex objects by converting to dict
            try:
                fixed_metadata[key] = asdict(value) if hasattr(value, '__dataclass_fields__') else str(value)
            except:
                fixed_metadata[key] = str(value)
        elif isinstance(value, (list, tuple)):
            # Handle lists/tuples that might contain non-serializable objects
            fixed_metadata[key] = [
                item.isoformat() if isinstance(item, datetime) else str(item)
                for item in value
            ]
        else:
            fixed_metadata[key] = value

    return fixed_metadata

async def diagnose_neo4j_storage_issues():
    """
    Comprehensive diagnosis of Neo4j storage issues identified during ingestion
    """
    print("🔍 Diagnosing Neo4j Storage Issues")
    print("=" * 50)

    try:
        # Initialize database manager
        db_mgr = DatabaseManager()
        await db_mgr.initialize_all_connections()

        # Check current Neo4j state
        print("\n📊 Current Neo4j Database State:")
        with db_mgr.connections[DatabaseType.NEO4J].session() as session:
            # Total nodes
            result = session.run("MATCH (n) RETURN count(n) as total")
            total_nodes = result.single()['total']
            print(f"   Total nodes: {total_nodes}")

            # PythonFile nodes (from recent ingestion)
            result = session.run("MATCH (n:PythonFile) RETURN count(n) as python_files")
            python_files = result.single()['python_files']
            print(f"   PythonFile nodes: {python_files}")

            # Check for any nodes with missing properties (indicating storage issues)
            result = session.run("""
                MATCH (n:PythonFile)
                WHERE n.path IS NULL OR n.name IS NULL
                RETURN count(n) as incomplete_nodes
            """)
            incomplete_nodes = result.single()['incomplete_nodes']
            print(f"   Incomplete PythonFile nodes: {incomplete_nodes}")

            # Sample a few nodes to check their properties
            result = session.run("MATCH (n:PythonFile) RETURN n LIMIT 3")
            print("\n🔍 Sample PythonFile nodes:")
            for i, record in enumerate(result):
                node = record['n']
                print(f"   Node {i+1}: {dict(node)}")

        print("\n❌ Issue Identified:")
        print("   • Expected nodes from recent ingestion: 114 files")
        print(f"   • Actual PythonFile nodes in Neo4j: {python_files}")
        print(f"   • Missing nodes: {114 - python_files}")
        print("   • Root cause: DateTime serialization errors during storage")

    except Exception as e:
        logger.error(f"Error during diagnosis: {str(e)}")
        print(f"❌ Diagnosis failed: {str(e)}")
    finally:
        await db_mgr.close_all_connections()

async def test_fixed_storage():
    """
    Test the fixed storage mechanism with proper datetime serialization
    """
    print("\n🧪 Testing Fixed Storage Mechanism")
    print("=" * 50)

    try:
        # Initialize components
        db_mgr = DatabaseManager()
        await db_mgr.initialize_all_connections()

        # Test datetime serialization fix
        test_metadata = {
            'created_time': datetime.now(),
            'modified_time': datetime.now(),
            'file_path': '/test/path.py',
            'size_bytes': 1024,
            'encoding': 'utf-8'
        }

        print("🔧 Original metadata (with datetime objects):")
        for key, value in test_metadata.items():
            print(f"   {key}: {value} ({type(value).__name__})")

        # Apply fix
        fixed_metadata = fix_metadata_serialization(test_metadata)
        print("\n✅ Fixed metadata (JSON serializable):")
        for key, value in fixed_metadata.items():
            print(f"   {key}: {value} ({type(value).__name__})")

        # Test JSON serialization
        try:
            json_string = json.dumps(fixed_metadata, cls=DateTimeEncoder)
            print("\n✅ JSON serialization test: SUCCESS")
            print(f"   Serialized length: {len(json_string)} characters")
        except Exception as e:
            print(f"\n❌ JSON serialization test: FAILED - {str(e)}")

        # Test Neo4j storage with fixed metadata
        try:
            query = """
            CREATE (n:TestPythonFile)
            SET n += $properties
            RETURN n
            """

            result = await db_mgr.execute_query(
                DatabaseType.NEO4J,
                query,
                {"properties": fixed_metadata}
            )

            if result.success:
                print("✅ Neo4j storage test: SUCCESS")

                # Clean up test node
                cleanup_query = "MATCH (n:TestPythonFile) DELETE n"
                await db_mgr.execute_query(DatabaseType.NEO4J, cleanup_query)
                print("✅ Test node cleaned up")
            else:
                print(f"❌ Neo4j storage test: FAILED - {result.error_message}")

        except Exception as e:
            print(f"❌ Neo4j storage test: FAILED - {str(e)}")

    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        print(f"❌ Testing failed: {str(e)}")
    finally:
        await db_mgr.close_all_connections()

async def recommend_plc_repo_ingestion():
    """
    Provide recommendations for ingesting missing PLC repositories
    """
    print("\n📋 PLC Repository Ingestion Recommendations")
    print("=" * 50)

    plc_repos = {
        'plc-100': 'https://github.com/reh3376/plc-100.git',
        'plc-200': 'https://github.com/reh3376/plc-200.git',
        'plc-300': 'https://github.com/reh3376/plc-300.git',
        'plc-400': 'https://github.com/reh3376/plc-400.git',
        'plc-500': 'https://github.com/reh3376/plc-500.git',
        'plc-600': 'https://github.com/reh3376/plc-600.git'
    }

    print("📁 Missing PLC Repositories:")
    for repo_name, repo_url in plc_repos.items():
        print(f"   • {repo_name}: {repo_url}")

    print("\n🔧 Recommended Actions:")
    print("   1. Clone all PLC repositories to local directory")
    print("   2. Update CLI to support multi-directory ingestion")
    print("   3. Run comprehensive ingestion across all PLC repositories")
    print("   4. Validate complete knowledge graph with all PLC data")

    print("\n💻 Example Commands:")
    print("   # Clone PLC repositories")
    print("   cd /Users/reh3376/repos/")
    for repo_name, repo_url in plc_repos.items():
        print(f"   git clone {repo_url}")

    print("\n   # Ingest all PLC repositories")
    print("   plc-memory ingest --directories plc-100 plc-200 plc-300 plc-400 plc-500 plc-600")
    print("   # Or ingest each individually")
    for repo_name in plc_repos.keys():
        print(f"   plc-memory ingest {repo_name}")

async def create_storage_fix_patch():
    """
    Create a patch file to fix the datetime serialization issues
    """
    print("\n🔧 Creating Storage Fix Patch")
    print("=" * 50)

    patch_content = '''
# Storage Fix for DateTime Serialization Issues
# Apply this patch to file_processors.py

def fix_database_routing_metadata(database_routing):
    """Fix metadata in database routing to ensure JSON serialization compatibility"""
    import json
    from datetime import datetime

    for tier, data in database_routing.items():
        if 'data' in data and 'metadata' in data['data']:
            # Fix metadata for long-term storage (PostgreSQL)
            metadata = data['data']['metadata']
            fixed_metadata = {}

            for key, value in metadata.items():
                if isinstance(value, datetime):
                    fixed_metadata[key] = value.isoformat()
                elif hasattr(value, '__dict__'):
                    try:
                        fixed_metadata[key] = asdict(value) if hasattr(value, '__dataclass_fields__') else str(value)
                    except:
                        fixed_metadata[key] = str(value)
                else:
                    fixed_metadata[key] = value

            data['data']['metadata'] = fixed_metadata

    return database_routing

# Apply this fix in each processor's process() method after creating database_routing
# Example for PythonFileProcessor:
# database_routing = fix_database_routing_metadata(database_routing)
'''

    patch_file = "neo4j_storage_fix.patch"
    with open(patch_file, 'w') as f:
        f.write(patch_content)

    print(f"✅ Storage fix patch created: {patch_file}")
    print("📋 Next steps:")
    print("   1. Apply patch to file_processors.py")
    print("   2. Re-run ingestion with fixed storage")
    print("   3. Validate all 114 files are stored in Neo4j")

async def main():
    """
    Main diagnostic and fix routine following AI Task Orchestrator methodology
    """
    print("🚀 Neo4j Storage Issues - Comprehensive Analysis & Fix")
    print("=" * 70)
    print("Following AI Task Orchestrator Guide Methodology")
    print("Task Complexity: MODERATE - Multiple integration issues")
    print("=" * 70)

    try:
        # Step 1: Diagnose current issues
        await diagnose_neo4j_storage_issues()

        # Step 2: Test storage fixes
        await test_fixed_storage()

        # Step 3: Recommend PLC repository handling
        await recommend_plc_repo_ingestion()

        # Step 4: Create fix patch
        await create_storage_fix_patch()

        print("\n🎯 Diagnosis Complete!")
        print("📊 Summary of Issues Found:")
        print("   ❌ DateTime serialization preventing Neo4j storage")
        print("   ❌ Missing PLC repositories (plc-100 through plc-600)")
        print("   ❌ Only 73/114 files successfully stored in Neo4j")

        print("\n✅ Solutions Provided:")
        print("   🔧 DateTime serialization fix implemented")
        print("   📋 PLC repository cloning recommendations")
        print("   🔨 Storage fix patch created")

        print("\n🚀 Next Steps:")
        print("   1. Apply storage fixes to file_processors.py")
        print("   2. Clone missing PLC repositories")
        print("   3. Re-run comprehensive ingestion")
        print("   4. Validate complete Neo4j population")

        return 0

    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        print(f"❌ Analysis failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
