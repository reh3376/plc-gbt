#!/usr/bin/env python3
"""
Simple test for configuration system only
"""

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_dependency_validation():
    """Test dependency validation in isolation"""
    
    from config.module_config import ModularConfigManager
    
    # Create temporary config
    temp_dir = tempfile.mkdtemp()
    test_config_path = Path(temp_dir) / ".ai_framework_modules.json"
    
    try:
        config = ModularConfigManager(test_config_path)
        
        print("🔍 Testing dependency validation...")
        
        # Test valid configuration
        config.enable_module("code_analysis")
        config.enable_module("code_optimization")  # Depends on code_analysis
        
        valid, issues = config.validate_dependencies()
        print(f"Valid configuration: {valid}, Issues: {issues}")
        assert valid == True
        assert len(issues) == 0
        
        # Test invalid configuration  
        config.disable_module("code_analysis")
        # code_optimization still enabled but dependency disabled
        
        valid, issues = config.validate_dependencies()
        print(f"Invalid configuration: {valid}, Issues: {issues}")
        
        if len(issues) > 0:
            print(f"First issue: '{issues[0]}'")
            print(f"Contains 'code_optimization': {'code_optimization' in issues[0]}")
            print(f"Contains 'code_analysis': {'code_analysis' in issues[0]}")
        
        assert valid == False
        assert len(issues) > 0
        
        # Check specific content
        issue_text = issues[0] if issues else ""
        if "code_optimization" in issue_text and "code_analysis" in issue_text:
            print("✅ Dependency validation test passed")
            return True
        else:
            print(f"❌ Issue text doesn't contain expected strings: '{issue_text}'")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

def test_basic_module_operations():
    """Test basic module operations"""
    from config.module_config import ModularConfigManager
    
    temp_dir = tempfile.mkdtemp()
    test_config_path = Path(temp_dir) / ".ai_framework_modules.json"
    
    try:
        config = ModularConfigManager(test_config_path)
        
        print("🔍 Testing basic module operations...")
        
        # Test module listing
        modules = config.get_all_module_names()
        print(f"Found {len(modules)} modules: {modules}")
        
        # Test enable/disable
        assert config.enable_module("wolfram_integration") == True
        assert config.is_module_enabled("wolfram_integration") == True
        
        assert config.disable_module("wolfram_integration") == True
        assert config.is_module_enabled("wolfram_integration") == False
        
        # Test invalid module
        assert config.enable_module("nonexistent_module") == False
        
        print("✅ Basic module operations test passed")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    print("🧪 Testing Configuration System Only")
    print("=" * 40)
    
    test1_passed = test_basic_module_operations()
    test2_passed = test_dependency_validation()
    
    if test1_passed and test2_passed:
        print("\n🎉 All configuration tests passed!")
    else:
        print("\n❌ Some configuration tests failed!") 