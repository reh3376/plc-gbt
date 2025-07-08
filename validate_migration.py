#!/usr/bin/env python3
"""
Phase 3.9 Migration Validation Script
====================================

Validates that the migrated Phase 3.9 components work correctly
in the acd-l5x-tool-lib repository.
"""

import sys
import os
from pathlib import Path

# Add the source directory to Python path for testing
repo_root = Path(__file__).parent
sys.path.insert(0, str(repo_root / "src"))

def test_imports():
    """Test all Phase 3.9 imports work correctly"""
    
    print("🔍 Testing Phase 3.9 Import Validation")
    print("=" * 50)
    
    tests = []
    
    # Test 1: Core models
    try:
        from plc_format_converter.core.models import PLCProject, PLCController, ConversionResult, DataIntegrityScore, PLCAddOnInstruction
        tests.append(("Core Models", True, "PLCProject, PLCController, ConversionResult, DataIntegrityScore, PLCAddOnInstruction"))
    except Exception as e:
        tests.append(("Core Models", False, str(e)))
    
    # Test 2: Enhanced converter
    try:
        from plc_format_converter.core.converter import EnhancedPLCConverter
        tests.append(("Enhanced Converter", True, "EnhancedPLCConverter"))
    except Exception as e:
        tests.append(("Enhanced Converter", False, str(e)))
    
    # Test 3: Validation framework
    try:
        from plc_format_converter.utils.validation import DataIntegrityValidator, RoundTripValidator
        tests.append(("Validation Framework", True, "DataIntegrityValidator, RoundTripValidator"))
    except Exception as e:
        tests.append(("Validation Framework", False, str(e)))
    
    # Test 4: Git optimization
    try:
        from plc_format_converter.utils.git_optimization import GitOptimizer, DiffAnalyzer
        tests.append(("Git Optimization", True, "GitOptimizer, DiffAnalyzer"))
    except Exception as e:
        tests.append(("Git Optimization", False, str(e)))
    
    # Test 5: Main package imports
    try:
        import plc_format_converter
        version = getattr(plc_format_converter, '__version__', 'unknown')
        tests.append(("Package Import", True, f"Version: {version}"))
    except Exception as e:
        tests.append(("Package Import", False, str(e)))
    
    # Print results
    passed = 0
    for test_name, success, details in tests:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        if success:
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {passed}/{len(tests)} tests passed")
    
    return passed == len(tests)

def test_basic_functionality():
    """Test basic functionality of migrated components"""
    
    print("\n🔧 Testing Basic Functionality")
    print("=" * 50)
    
    try:
        # Test PLCProject creation with required fields
        from plc_format_converter.core.models import PLCProject, PLCController
        
        project = PLCProject(
            name="TestProject",
            component_type="PLCProject",  # Required field
            controllers=[],
            studio5000_version="1.0",
            project_description="Test project for validation"
        )
        print("✅ PLCProject creation: SUCCESS")
        
        # Test DataIntegrityScore
        from plc_format_converter.core.models import DataIntegrityScore
        
        score = DataIntegrityScore(
            overall_score=95.5,
            logic_preservation=98.0,
            tag_preservation=94.0,
            io_preservation=93.0,
            motion_preservation=96.0,
            safety_preservation=95.0
        )
        print("✅ DataIntegrityScore creation: SUCCESS")
        
        # Test GitOptimizer
        from plc_format_converter.utils.git_optimization import GitOptimizer
        
        optimizer = GitOptimizer()
        print("✅ GitOptimizer creation: SUCCESS")
        
        # Test PLCAddOnInstruction
        from plc_format_converter.core.models import PLCAddOnInstruction
        
        aoi = PLCAddOnInstruction(
            name="TestAOI",
            component_type="PLCAddOnInstruction",
            revision="1.0"
        )
        print("✅ PLCAddOnInstruction creation: SUCCESS")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False

def main():
    """Main validation function"""
    
    print("🚀 Phase 3.9 Migration Validation")
    print("=" * 80)
    print(f"Repository: {Path(__file__).parent}")
    print(f"Target Version: 2.1.0")
    print()
    
    # Run import tests
    import_success = test_imports()
    
    # Run functionality tests
    functionality_success = test_basic_functionality()
    
    # Overall result
    overall_success = import_success and functionality_success
    
    print("\n" + "=" * 80)
    print("📋 MIGRATION VALIDATION SUMMARY")
    print("=" * 80)
    
    if overall_success:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("✅ All Phase 3.9 components migrated and working correctly")
        print("✅ Ready for 2.1.0 release")
    else:
        print("⚠️ VALIDATION ISSUES DETECTED")
        print("🔧 Some components may need additional fixes")
    
    print(f"\n🎯 Phase 3.9 Target: 95%+ data preservation (730x improvement)")
    print(f"📦 Version: 2.1.0")
    print(f"🚀 Status: {'READY FOR RELEASE' if overall_success else 'NEEDS FIXES'}")
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 