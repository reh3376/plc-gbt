#!/usr/bin/env python3
"""
Import Update Utility
Updates all plc_format_converter imports to use the new acd-l5x-tool-lib repository location
"""

import os
import re
from pathlib import Path
from typing import List, Dict

def update_file_imports(file_path: Path) -> Dict[str, any]:
    """Update imports in a single file"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {"success": False, "error": str(e), "changes": 0}
    
    original_content = content
    changes = 0
    
    # Pattern 1: sys.path.append with old paths
    old_path_patterns = [
        r"sys\.path\.append\(['\"].*plc-format-converter.*['\"\)]+",
        r"sys\.path\.append\(['\"].*src/plc_format_converter.*['\"\)]+",
        r"sys\.path\.append\(['\"].*PLC_GPT/src.*['\"\)]+"
    ]
    
    for pattern in old_path_patterns:
        if re.search(pattern, content):
            content = re.sub(
                pattern, 
                "sys.path.append('/Users/reh3376/repos/acd-l5x-tool-lib/src')", 
                content
            )
            changes += 1
    
    # Pattern 2: Direct imports - replace with utility import approach
    import_patterns = [
        (r"from plc_format_converter\.core\.converter import PLCConverter", 
         "# Use import utility\nfrom plc_converter_import import import_plc_converter\nPLCConverter = import_plc_converter()"),
        (r"from plc_format_converter\.core\.models import.*", 
         "# Use import utility\nfrom plc_converter_import import import_plc_models\nmodels = import_plc_models()"),
        (r"from plc_format_converter\.formats\.(.*) import (.*)", 
         "# Use import utility\nfrom plc_converter_import import import_plc_handlers\nhandlers = import_plc_handlers()")
    ]
    
    for old_pattern, new_import in import_patterns:
        if re.search(old_pattern, content):
            # Only replace if not already using utility imports
            if "plc_converter_import" not in content:
                content = re.sub(old_pattern, new_import, content)
                changes += 1
    
    # Save updated content if changes were made
    if changes > 0:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "changes": changes}
        except Exception as e:
            return {"success": False, "error": str(e), "changes": changes}
    
    return {"success": True, "changes": 0}

def find_python_files_with_imports(base_path: Path) -> List[Path]:
    """Find all Python files that contain plc_format_converter imports"""
    
    files_with_imports = []
    
    for file_path in base_path.rglob("*.py"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "plc_format_converter" in content:
                    files_with_imports.append(file_path)
        except:
            continue
    
    return files_with_imports

def main():
    """Main execution function"""
    
    base_path = Path("/Users/reh3376/repos/PLC_GPT")
    
    print("🔍 Finding Python files with plc_format_converter imports...")
    files_to_update = find_python_files_with_imports(base_path)
    
    print(f"📁 Found {len(files_to_update)} files to potentially update")
    
    results = {
        "total_files": len(files_to_update),
        "updated_files": 0,
        "total_changes": 0,
        "errors": [],
        "file_results": []
    }
    
    for file_path in files_to_update:
        print(f"⚙️  Processing: {file_path.relative_to(base_path)}")
        
        result = update_file_imports(file_path)
        results["file_results"].append({
            "file": str(file_path.relative_to(base_path)),
            "result": result
        })
        
        if result["success"]:
            if result["changes"] > 0:
                results["updated_files"] += 1
                results["total_changes"] += result["changes"]
                print(f"   ✅ Updated {result['changes']} imports")
            else:
                print(f"   ℹ️  No changes needed")
        else:
            results["errors"].append({
                "file": str(file_path.relative_to(base_path)),
                "error": result["error"]
            })
            print(f"   ❌ Error: {result['error']}")
    
    print(f"\n📊 Update Summary:")
    print(f"   📁 Total files processed: {results['total_files']}")
    print(f"   ✅ Files updated: {results['updated_files']}")
    print(f"   🔄 Total changes made: {results['total_changes']}")
    print(f"   ❌ Errors encountered: {len(results['errors'])}")
    
    if results["errors"]:
        print(f"\n⚠️  Files with errors:")
        for error in results["errors"]:
            print(f"   - {error['file']}: {error['error']}")
    
    return results

if __name__ == "__main__":
    main() 