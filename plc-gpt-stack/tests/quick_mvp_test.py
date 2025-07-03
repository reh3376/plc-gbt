#!/usr/bin/env python3
"""
Quick MVP Test for PLC-GPT System
Tests core functionality with correct import paths
"""

import os
import sys
import asyncio
from datetime import datetime

# Add correct paths for our modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_root, 'scripts', 'query'))
sys.path.append(os.path.join(project_root, 'scripts', 'etl'))
sys.path.append(os.path.join(project_root, 'scripts', 'performance'))
sys.path.append(os.path.join(project_root, 'workers'))

print("🚀 PLC-GPT MVP Quick Test")
print("=" * 50)

async def test_imports():
    """Test that all core modules can be imported"""
    results = {}
    
    # Test Query Service Import
    try:
        from query_service import QueryService
        results['query_service'] = "✅ SUCCESS"
        print("✅ Query Service: Import successful")
    except Exception as e:
        results['query_service'] = f"❌ FAILED: {str(e)}"
        print(f"❌ Query Service: {str(e)}")
    
    # Test ACD Processor Import  
    try:
        from acd_processor import ACDProcessor
        results['acd_processor'] = "✅ SUCCESS"
        print("✅ ACD Processor: Import successful")
    except Exception as e:
        results['acd_processor'] = f"❌ FAILED: {str(e)}"
        print(f"❌ ACD Processor: {str(e)}")
    
    # Test Document Parser Import
    try:
        from document_parser import DocumentParser
        results['document_parser'] = "✅ SUCCESS"
        print("✅ Document Parser: Import successful")
    except Exception as e:
        results['document_parser'] = f"❌ FAILED: {str(e)}"
        print(f"❌ Document Parser: {str(e)}")
    
    # Test ETL Integration Import
    try:
        from etl_integration import ETLIntegration
        results['etl_integration'] = "✅ SUCCESS"
        print("✅ ETL Integration: Import successful")
    except Exception as e:
        results['etl_integration'] = f"❌ FAILED: {str(e)}"
        print(f"❌ ETL Integration: {str(e)}")
    
    return results

def test_file_structure():
    """Test that expected files exist"""
    print("\n📁 File Structure Check:")
    
    expected_files = [
        'scripts/query/query_service.py',
        'scripts/etl/acd_processor.py', 
        'scripts/etl/etl_integration.py',
        'workers/document_parser.py',
        'scripts/performance/optimizer.py',
        'scripts/neo4j/create_schema.cypher'
    ]
    
    missing_files = []
    
    for file_path in expected_files:
        full_path = os.path.join(project_root, file_path)
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            print(f"   ✅ {file_path} ({file_size:,} bytes)")
        else:
            print(f"   ❌ {file_path} - NOT FOUND")
            missing_files.append(file_path)
    
    return missing_files, expected_files

def test_docker_services():
    """Test Docker services connectivity"""
    print("\n🐳 Docker Services Check:")
    
    # Test Neo4j
    try:
        import subprocess
        result = subprocess.run(['docker', 'ps', '--filter', 'name=plc-neo4j', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        if 'plc-neo4j' in result.stdout and 'Up' in result.stdout:
            print("   ✅ Neo4j: Running")
        else:
            print("   ❌ Neo4j: Not running or not found")
    except Exception as e:
        print(f"   ❌ Neo4j: Error checking status - {str(e)}")
    
    # Test Qdrant
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=plc-qdrant', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        if 'plc-qdrant' in result.stdout and 'Up' in result.stdout:
            print("   ✅ Qdrant: Running")
        else:
            print("   ❌ Qdrant: Not running or not found")
    except Exception as e:
        print(f"   ❌ Qdrant: Error checking status - {str(e)}")
    
    # Test Postgres
    try:
        result = subprocess.run(['docker', 'ps', '--filter', 'name=plc-postgres', '--format', 'table {{.Names}}\t{{.Status}}'], 
                              capture_output=True, text=True, timeout=10)
        if 'plc-postgres' in result.stdout and 'Up' in result.stdout:
            print("   ✅ Postgres: Running")
        else:
            print("   ❌ Postgres: Not running or not found")
    except Exception as e:
        print(f"   ❌ Postgres: Error checking status - {str(e)}")

async def main():
    """Run the MVP test suite"""
    print(f"🕐 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Project root: {project_root}")
    
    # Test 1: File Structure
    missing_files, expected_files = test_file_structure()
    
    # Test 2: Docker Services
    test_docker_services()
    
    # Test 3: Module Imports
    print("\n🐍 Module Import Tests:")
    import_results = await test_imports()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MVP TEST SUMMARY")
    print("=" * 50)
    
    successful_imports = sum(1 for result in import_results.values() if "SUCCESS" in result)
    total_imports = len(import_results)
    
    print(f"📁 File Structure: {len(expected_files) - len(missing_files)}/{len(expected_files)} files found")
    print(f"🐍 Module Imports: {successful_imports}/{total_imports} successful")
    
    if successful_imports == total_imports and len(missing_files) == 0:
        print("🎉 MVP Status: ✅ READY - Core components functional!")
        print("🚀 Next Step: Complete Phase 3 Days 6-7 or start Phase 4")
    elif successful_imports > 0:
        print("⚠️  MVP Status: 🔄 PARTIAL - Some components working")
        print("🔧 Next Step: Fix import issues and missing dependencies")
    else:
        print("❌ MVP Status: ❌ NOT READY - Major issues need fixing")
        print("🔧 Next Step: Debug import paths and dependencies")
    
    print(f"\n🕐 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main()) 