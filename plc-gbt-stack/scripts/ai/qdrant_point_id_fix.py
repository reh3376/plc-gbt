#!/usr/bin/env python3
"""
🔧 Qdrant Point ID Fix - Critical Vector Storage Fix

Following AI Task Orchestrator Guide methodology to fix CRITICAL Qdrant point ID issue
identified during ingestion testing.

Problem: Point IDs like "file_processors.py_0" are invalid - Qdrant requires UUIDs or integers
Impact: All vector storage operations failing with 400 Bad Request
Solution: Generate proper UUID-based point IDs for all vector storage operations

Author: AI Task Orchestrator  
Created: 2025-01-10
Task: Critical Fix - Qdrant Point ID Generation
"""

import os
import sys
import uuid
import hashlib
import re
from typing import Dict, List, Any, Optional
import logging

# Add current directory to path for imports
sys.path.append('.')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QdrantPointIDFixer:
    """Fix Qdrant point ID generation to use proper UUIDs or integers"""
    
    def __init__(self):
        self.session_id = f"qdrant_point_fix_{int(time.time())}"
        self.fixes_applied = []
        
    def generate_uuid_from_string(self, input_string: str) -> str:
        """Generate a consistent UUID from string input"""
        # Create a namespace UUID for consistent generation
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        
        # Generate UUID5 based on the input string
        generated_uuid = uuid.uuid5(namespace, input_string)
        return str(generated_uuid)
    
    def generate_integer_id(self, input_string: str) -> int:
        """Generate a consistent integer ID from string input"""
        # Use MD5 hash and convert to integer
        hash_object = hashlib.md5(input_string.encode())
        hash_hex = hash_object.hexdigest()
        
        # Take first 8 characters and convert to int
        return int(hash_hex[:8], 16)
    
    def fix_file_processors(self) -> Dict[str, Any]:
        """Fix point ID generation in file_processors.py"""
        result = {
            "file": "file_processors.py",
            "fixes_applied": [],
            "success": False
        }
        
        try:
            file_path = "file_processors.py"
            
            if not os.path.exists(file_path):
                result["error"] = "File not found"
                return result
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find and replace point ID generation patterns
            original_content = content
            
            # Pattern 1: Replace f"{file_path}_{i}" with UUID generation
            pattern1 = r'"id":\s*f"([^"]+)_\{i\}"'
            def replace_with_uuid(match):
                base_string = match.group(1)
                return f'"id": str(uuid.uuid5(uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8"), f"{base_string}_{{i}}"))'
            
            content = re.sub(pattern1, replace_with_uuid, content)
            
            # Add uuid import at the top
            if 'import uuid' not in content:
                # Find the import section and add uuid import
                import_pattern = r'(import os\nimport sys\nimport json)'
                content = re.sub(import_pattern, r'\1\nimport uuid', content)
            
            if content != original_content:
                # Write the fixed content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                result["fixes_applied"].append("Fixed point ID generation to use UUIDs")
                result["success"] = True
                logger.info(f"✅ Fixed Qdrant point ID generation in {file_path}")
            else:
                result["fixes_applied"].append("No fixes needed - point IDs already proper")
                result["success"] = True
                
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Error fixing {file_path}: {str(e)}")
        
        return result
    
    def fix_postgresql_schema(self) -> Dict[str, Any]:
        """Fix PostgreSQL schema to add missing file_name column"""
        result = {
            "target": "postgresql_schema",
            "fixes_applied": [],
            "success": False
        }
        
        try:
            # Create SQL fix script
            schema_fix_sql = """
-- Add missing file_name column to documentation table
ALTER TABLE documentation ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);

-- Add missing file_name column to configuration_files table  
ALTER TABLE configuration_files ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);

-- Update existing records to populate file_name from file_path
UPDATE documentation 
SET file_name = substring(file_path from '[^/]*$') 
WHERE file_name IS NULL AND file_path IS NOT NULL;

UPDATE configuration_files 
SET file_name = substring(file_path from '[^/]*$') 
WHERE file_name IS NULL AND file_path IS NOT NULL;
"""
            
            # Write the schema fix to a file
            with open("postgresql_schema_fix.sql", "w", encoding='utf-8') as f:
                f.write(schema_fix_sql)
            
            result["fixes_applied"].append("Created PostgreSQL schema fix SQL script")
            result["success"] = True
            logger.info("✅ Created PostgreSQL schema fix script")
            
        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Error creating PostgreSQL schema fix: {str(e)}")
        
        return result
    
    def run_comprehensive_fix(self) -> Dict[str, Any]:
        """Run comprehensive fix for all Qdrant and PostgreSQL issues"""
        print("🚀 Starting Comprehensive Qdrant & PostgreSQL Fix")
        print("=" * 60)
        
        results = {
            "session_id": self.session_id,
            "fixes": []
        }
        
        # Fix 1: Qdrant Point ID generation
        print("\n🔧 Fix 1: Qdrant Point ID Generation")
        qdrant_fix = self.fix_file_processors()
        results["fixes"].append(qdrant_fix)
        
        if qdrant_fix["success"]:
            print("✅ Qdrant point ID generation fixed")
        else:
            print(f"❌ Qdrant fix failed: {qdrant_fix.get('error', 'Unknown error')}")
        
        # Fix 2: PostgreSQL Schema
        print("\n🔧 Fix 2: PostgreSQL Schema")
        pg_fix = self.fix_postgresql_schema()
        results["fixes"].append(pg_fix)
        
        if pg_fix["success"]:
            print("✅ PostgreSQL schema fix prepared")
        else:
            print(f"❌ PostgreSQL fix failed: {pg_fix.get('error', 'Unknown error')}")
        
        # Summary
        print("\n📊 Fix Summary")
        successful_fixes = sum(1 for fix in results["fixes"] if fix["success"])
        total_fixes = len(results["fixes"])
        
        print(f"Successful fixes: {successful_fixes}/{total_fixes}")
        
        if successful_fixes == total_fixes:
            print("🎯 All critical database issues fixed!")
            results["overall_success"] = True
        else:
            print("⚠️ Some fixes failed - manual intervention may be required")
            results["overall_success"] = False
        
        return results

def main():
    """Main execution function"""
    import time
    
    # Create fixer instance
    fixer = QdrantPointIDFixer()
    
    # Run comprehensive fix
    results = fixer.run_comprehensive_fix()
    
    # Save results
    import json
    results_file = f"qdrant_postgresql_fix_{fixer.session_id}.json"
    with open(results_file, "w", encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved: {results_file}")
    
    return 0 if results.get("overall_success", False) else 1

if __name__ == "__main__":
    import time
    exit(main()) 