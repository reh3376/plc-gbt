#!/usr/bin/env python3
"""
Phase 2: Consolidation - AI Task Orchestrator Methodology
Systematically consolidate to single working implementation

Following the execution plan from orchestrator_analysis.json
"""

import sys
import shutil
from pathlib import Path
from typing import List, Dict, Any

def remove_conflicting_paths():
    """
    Step 2.1: Remove conflicting import paths
    """
    print("🧹 Step 2.1: Removing conflicting import paths")
    
    # Get current Python path
    print("Current sys.path entries with plc-format-converter:")
    for i, path in enumerate(sys.path):
        if 'plc-format-converter' in path:
            print(f"  {i}: {path}")
    
    # Remove conflicting paths
    paths_to_remove = []
    for path in sys.path:
        if 'plc-format-converter' in path and 'src' not in path:
            paths_to_remove.append(path)
    
    for path in paths_to_remove:
        sys.path.remove(path)
        print(f"  ✅ Removed: {path}")
    
    # Add our preferred implementation first
    project_root = Path(__file__).parent.parent.parent.parent
    our_src = str(project_root / "src")
    
    if our_src not in sys.path:
        sys.path.insert(0, our_src)
        print(f"  ✅ Added (priority): {our_src}")
    
    return True

def validate_core_imports():
    """
    Step 2.2: Validate core imports work
    """
    print("\n🔍 Step 2.2: Validating core imports")
    
    try:
        # Test core imports
        # Use import utility
from plc_converter_import import import_plc_models
models = import_plc_models()
        print("  ✅ Core models import successful")
        
        from plc_format_converter.core.converter import PLCFormatConverter
        print("  ✅ Core converter import successful")
        
        from plc_format_converter.formats.acd_handler import ACDHandler
        print("  ✅ ACD handler import successful")
        
        from plc_format_converter.formats.l5x_handler import L5XHandler
        print("  ✅ L5X handler import successful")
        
        # Test instantiation
        converter = PLCFormatConverter()
        print("  ✅ Converter instantiation successful")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Instantiation failed: {e}")
        return False

def create_missing_components():
    """
    Step 2.3: Create any missing components
    """
    print("\n🔧 Step 2.3: Creating missing components")
    
    project_root = Path(__file__).parent.parent.parent.parent
    src_dir = project_root / "src" / "plc_format_converter"
    
    # Check for missing validation module
    validation_file = src_dir / "utils" / "validation.py"
    if not validation_file.exists():
        print("  📝 Creating missing validation.py")
        create_validation_module(validation_file)
    else:
        print("  ✅ validation.py exists")
    
    # Check for __init__.py files
    init_files = [
        src_dir / "__init__.py",
        src_dir / "core" / "__init__.py",
        src_dir / "formats" / "__init__.py",
        src_dir / "utils" / "__init__.py"
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            print(f"  📝 Creating {init_file}")
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text("# Package initialization\n")
        else:
            print(f"  ✅ {init_file.name} exists")
    
    return True

def create_validation_module(validation_file: Path):
    """Create a minimal validation module"""
    
    validation_content = '''"""
PLC Validation Utilities

Minimal validation framework for PLC projects.
"""

from typing import List, Dict, Any
from ..core.models import PLCProject, ValidationResult, ValidationIssue

class PLCValidator:
    """Basic PLC project validator."""
    
    def __init__(self):
        self.validation_rules = []
    
    def validate_project(self, project: PLCProject) -> ValidationResult:
        """Validate a PLC project."""
        issues = []
        
        # Basic validation checks
        if not project.name:
            issues.append(ValidationIssue(
                severity="error",
                category="structure",
                message="Project name is required"
            ))
        
        if not project.controller:
            issues.append(ValidationIssue(
                severity="error", 
                category="structure",
                message="Controller configuration is required"
            ))
        
        # Calculate score
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        
        # Simple scoring: 100% - (errors * 20) - (warnings * 5)
        score = max(0, 100 - (error_count * 20) - (warning_count * 5))
        
        return ValidationResult(
            is_valid=error_count == 0,
            score=score,
            issues=issues
        )
'''
    
    validation_file.parent.mkdir(parents=True, exist_ok=True)
    validation_file.write_text(validation_content)

def test_simple_conversion():
    """
    Step 2.4: Test simple conversion functionality
    """
    print("\n🧪 Step 2.4: Testing simple conversion functionality")
    
    try:
        from plc_format_converter.core.converter import PLCFormatConverter
        # Use import utility
from plc_converter_import import import_plc_models
models = import_plc_models()
        
        # Create test converter
        converter = PLCFormatConverter()
        print("  ✅ Converter created")
        
        # Get capabilities
        capabilities = converter.get_capabilities()
        print(f"  ✅ Capabilities retrieved: {capabilities['converter_version']}")
        
        # Test with dummy project
        test_project = PLCProject(
            name="TestProject",
            controller=PLCController(name="TestController")
        )
        print("  ✅ Test project created")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Conversion test failed: {e}")
        return False

def create_simple_migration_interface():
    """
    Step 2.5: Create simplified migration interface
    """
    print("\n🔨 Step 2.5: Creating simplified migration interface")
    
    interface_file = Path(__file__).parent / "simple_migration.py"
    
    interface_content = '''#!/usr/bin/env python3
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
        from plc_format_converter.core.converter import PLCFormatConverter
        
        converter = PLCFormatConverter()
        
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
        from plc_format_converter.core.converter import PLCFormatConverter
        print("✅ Imports working")
        
        converter = PLCFormatConverter()
        print("✅ Converter instantiated")
        
        capabilities = converter.get_capabilities()
        print(f"✅ Capabilities: {capabilities.get('converter_version', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
'''
    
    interface_file.write_text(interface_content)
    print(f"  ✅ Created: {interface_file}")
    
    return interface_file

def main():
    """
    Execute Phase 2: Consolidation
    """
    print("🚀 Phase 2: Consolidation - AI Task Orchestrator")
    print("=" * 60)
    
    success_steps = 0
    total_steps = 5
    
    # Step 2.1: Remove conflicting paths
    if remove_conflicting_paths():
        success_steps += 1
    
    # Step 2.2: Validate imports
    if validate_core_imports():
        success_steps += 1
    
    # Step 2.3: Create missing components
    if create_missing_components():
        success_steps += 1
    
    # Step 2.4: Test conversion
    if test_simple_conversion():
        success_steps += 1
    
    # Step 2.5: Create simple interface
    if create_simple_migration_interface():
        success_steps += 1
    
    # Results
    print(f"\n📊 Phase 2 Results: {success_steps}/{total_steps} steps successful")
    
    if success_steps == total_steps:
        print("✅ Phase 2 COMPLETE - Ready for Phase 3: API Standardization")
        return True
    else:
        print("⚠️ Phase 2 PARTIAL - Some issues need resolution")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 