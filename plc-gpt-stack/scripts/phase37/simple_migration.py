#!/usr/bin/env python3
"""
Simplified Migration Interface
Working implementation for Phase 3.7 migration

This bypasses complex import issues by using a direct, simple approach.
"""

import sys
from pathlib import Path

# Ensure our implementation is used
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
src_dir = project_root / "src"

# Clean and set path
for path in list(sys.path):
    if 'plc-format-converter' in path and str(src_dir) not in path:
        sys.path.remove(path)

sys.path.insert(0, str(src_dir))

def simple_convert_acd_to_l5x(acd_file: Path, l5x_file: Path) -> bool:
    """Simple ACD to L5X conversion"""
    try:
        # Use import utility
from plc_converter_import import import_plc_converter
PLCConverter = import_plc_converter()
        
        converter = PLCConverter()
        
        # Ensure output directory exists
        l5x_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Perform conversion
        project = converter.convert_acd_to_l5x(acd_file, l5x_file)
        
        return True
        
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False

def simple_migrate_repository(source_repo: Path, target_repo: Path) -> dict:
    """Simple repository migration"""
    results = {
        "source": str(source_repo),
        "target": str(target_repo), 
        "files_processed": 0,
        "files_converted": 0,
        "errors": []
    }
    
    try:
        # Find ACD files
        acd_files = list(source_repo.rglob("*.acd")) + list(source_repo.rglob("*.ACD"))
        results["files_processed"] = len(acd_files)
        
        for acd_file in acd_files:
            # Calculate target path
            rel_path = acd_file.relative_to(source_repo)
            l5x_file = target_repo / rel_path.with_suffix('.l5x')
            
            # Convert file
            if simple_convert_acd_to_l5x(acd_file, l5x_file):
                results["files_converted"] += 1
                print(f"✅ Converted: {acd_file.name}")
            else:
                results["errors"].append(f"Failed to convert: {acd_file.name}")
                print(f"❌ Failed: {acd_file.name}")
        
        # Copy non-ACD files
        for item in source_repo.rglob("*"):
            if item.is_file() and not item.name.lower().endswith('.acd'):
                rel_path = item.relative_to(source_repo)
                target_file = target_repo / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                import shutil
                shutil.copy2(item, target_file)
        
        return results
        
    except Exception as e:
        results["errors"].append(f"Migration failed: {e}")
        return results

if __name__ == "__main__":
    print("🔧 Simple Migration Interface")
    print("Testing basic functionality...")
    
    # Test imports
    try:
        # Use import utility
from plc_converter_import import import_plc_converter
PLCConverter = import_plc_converter()
        print("✅ Imports working")
        
        converter = PLCConverter()
        print("✅ Converter instantiated")
        
        # Test available methods
        methods = [method for method in dir(converter) if not method.startswith('_')]
        print(f"✅ Available methods: {', '.join(methods[:5])}...")
        
        print("✅ Simple Migration Interface is ready!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
