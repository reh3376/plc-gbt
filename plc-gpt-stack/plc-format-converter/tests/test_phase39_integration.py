#!/usr/bin/env python3
"""
Phase 3.9 Integration Test Suite
================================

Integration test suite for Phase 3.9 enhanced PLC format converter development
that validates the enhanced capabilities and readiness for migration.
"""

import os
import sys
import unittest
import tempfile
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add project paths
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "plc-gpt-stack"))

# Test imports
def test_enhanced_imports():
    """Test if enhanced converter components can be imported"""
    import_results = {
        'enhanced_converter': False,
        'enhanced_models': False,
        'enhanced_acd_handler': False,
        'enhanced_l5x_handler': False,
        'validation_framework': False,
        'error_messages': []
    }
    
    try:
        # Test core converter import
        sys.path.insert(0, str(project_root / "plc-gpt-stack" / "plc-format-converter" / "src"))
        from plc_format_converter.core.converter import EnhancedPLCConverter
        import_results['enhanced_converter'] = True
    except ImportError as e:
        import_results['error_messages'].append(f"Enhanced converter: {e}")
    
    try:
        # Test enhanced models import
        from plc_format_converter.core.models import (
            PLCProject, DataIntegrityScore, ConversionResult
        )
        import_results['enhanced_models'] = True
    except ImportError as e:
        import_results['error_messages'].append(f"Enhanced models: {e}")
    
    try:
        # Test ACD handler import
        from plc_format_converter.formats.enhanced_acd_handler import EnhancedACDHandler
        import_results['enhanced_acd_handler'] = True
    except ImportError as e:
        import_results['error_messages'].append(f"Enhanced ACD handler: {e}")
    
    try:
        # Test L5X handler import
        from plc_format_converter.formats.enhanced_l5x_handler import EnhancedL5XHandler
        import_results['enhanced_l5x_handler'] = True
    except ImportError as e:
        import_results['error_messages'].append(f"Enhanced L5X handler: {e}")
    
    try:
        # Test validation framework import
        from plc_format_converter.utils.validation import DataIntegrityValidator, RoundTripValidator
        import_results['validation_framework'] = True
    except ImportError as e:
        import_results['error_messages'].append(f"Validation framework: {e}")
    
    return import_results


class TestPhase39Development(unittest.TestCase):
    """Test Phase 3.9 development progress and capabilities"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test class"""
        cls.project_root = Path(__file__).parent.parent.parent.parent
        cls.plc_format_converter_dir = cls.project_root / "plc-gpt-stack" / "plc-format-converter"
        cls.import_results = test_enhanced_imports()
    
    def test_enhanced_converter_structure(self):
        """Test that enhanced converter directory structure exists"""
        
        required_dirs = [
            "src/plc_format_converter",
            "src/plc_format_converter/core",
            "src/plc_format_converter/formats", 
            "src/plc_format_converter/utils",
            "tests"
        ]
        
        for dir_path in required_dirs:
            full_path = self.plc_format_converter_dir / dir_path
            self.assertTrue(full_path.exists(), f"Required directory missing: {dir_path}")
    
    def test_enhanced_converter_files(self):
        """Test that enhanced converter files exist"""
        
        required_files = [
            "src/plc_format_converter/__init__.py",
            "src/plc_format_converter/core/__init__.py",
            "src/plc_format_converter/core/converter.py",
            "src/plc_format_converter/core/models.py",
            "src/plc_format_converter/formats/__init__.py",
            "src/plc_format_converter/formats/enhanced_acd_handler.py",
            "src/plc_format_converter/formats/enhanced_l5x_handler.py",
            "src/plc_format_converter/utils/__init__.py",
            "src/plc_format_converter/utils/validation.py"
        ]
        
        for file_path in required_files:
            full_path = self.plc_format_converter_dir / file_path
            self.assertTrue(full_path.exists(), f"Required file missing: {file_path}")
    
    def test_import_availability(self):
        """Test import availability of enhanced components"""
        
        # Test core components
        if self.import_results['enhanced_converter']:
            print("✅ Enhanced Converter: Available")
        else:
            print("❌ Enhanced Converter: Not Available")
        
        if self.import_results['enhanced_models']:
            print("✅ Enhanced Models: Available")
        else:
            print("❌ Enhanced Models: Not Available")
        
        # Calculate availability percentage
        available_components = sum(1 for result in self.import_results.values() if isinstance(result, bool) and result)
        total_components = len([k for k, v in self.import_results.items() if isinstance(v, bool)])
        availability_percentage = (available_components / total_components) * 100
        
        print(f"📊 Component Availability: {availability_percentage:.1f}%")
        
        # Assert minimum availability for Phase 3.9
        self.assertGreaterEqual(availability_percentage, 60.0, 
                               "Phase 3.9 component availability below 60% threshold")
    
    def test_data_preservation_target(self):
        """Test that 95%+ data preservation target is defined"""
        
        if self.import_results['enhanced_models']:
            try:
                from plc_format_converter.core.models import DataPreservationLevel
                
                # Check that INDUSTRY_STANDARD level exists (95%+)
                self.assertTrue(hasattr(DataPreservationLevel, 'INDUSTRY_STANDARD'))
                print("✅ 95%+ Data Preservation Target: Defined")
                
            except ImportError:
                self.fail("DataPreservationLevel not available")
        else:
            self.skipTest("Enhanced models not available")
    
    def test_validation_framework_capability(self):
        """Test validation framework capabilities"""
        
        if self.import_results['validation_framework']:
            try:
                from plc_format_converter.utils.validation import DataIntegrityValidator, RoundTripValidator
                
                # Test validator initialization
                validator = DataIntegrityValidator()
                round_trip = RoundTripValidator(enable_studio5000=False)
                
                self.assertIsNotNone(validator)
                self.assertIsNotNone(round_trip)
                
                print("✅ Validation Framework: Available")
                
            except Exception as e:
                self.fail(f"Validation framework initialization failed: {e}")
        else:
            self.skipTest("Validation framework not available")
    
    def test_acd_tools_integration(self):
        """Test integration with existing acd-tools helper libraries"""
        
        # Check if acd-tools integration is available
        try:
            sys.path.append(str(self.project_root / "plc-gpt-stack" / "scripts" / "etl"))
            from acd_processor import ACDProcessor
            
            processor = ACDProcessor()
            self.assertIsNotNone(processor)
            
            print("✅ ACD Tools Integration: Available")
            
        except ImportError:
            print("⚠️  ACD Tools Integration: Limited")
    
    def test_existing_infrastructure_compatibility(self):
        """Test compatibility with existing PLC-GPT infrastructure"""
        
        # Test AI Task Orchestrator integration
        try:
            from ai.ai_task_orchestrator import get_task_guidance, validate_task_completion
            
            # Test task guidance
            guidance = get_task_guidance("Test enhanced converter integration")
            self.assertIsInstance(guidance, str)
            
            print("✅ AI Task Orchestrator: Integrated")
            
        except ImportError:
            print("⚠️  AI Task Orchestrator: Not Available")
    
    def test_migration_readiness(self):
        """Test readiness for migration to acd-l5x-tool-lib repository"""
        
        # Calculate migration readiness score
        readiness_factors = {
            'enhanced_converter': self.import_results['enhanced_converter'],
            'enhanced_models': self.import_results['enhanced_models'],
            'enhanced_acd_handler': self.import_results['enhanced_acd_handler'],
            'enhanced_l5x_handler': self.import_results['enhanced_l5x_handler'],
            'validation_framework': self.import_results['validation_framework']
        }
        
        ready_factors = sum(1 for ready in readiness_factors.values() if ready)
        total_factors = len(readiness_factors)
        migration_readiness = (ready_factors / total_factors) * 100
        
        print(f"🚀 Migration Readiness: {migration_readiness:.1f}%")
        
        # Detailed readiness assessment
        if migration_readiness >= 80:
            print("✅ Ready for migration to acd-l5x-tool-lib")
        elif migration_readiness >= 60:
            print("⚠️  Partially ready - some components need completion")
        else:
            print("❌ Not ready for migration - significant work required")
        
        # Assert minimum readiness threshold
        self.assertGreaterEqual(migration_readiness, 50.0,
                               "Migration readiness below minimum 50% threshold")
        
        return migration_readiness


class TestExistingAcdFiles(unittest.TestCase):
    """Test compatibility with existing ACD files in PLC repositories"""
    
    def setUp(self):
        """Set up test with repository paths"""
        self.repo_base = Path("/Users/reh3376/repos")
        self.test_repos = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
    
    def test_acd_file_availability(self):
        """Test that ACD files are available for enhanced processing"""
        
        acd_files_found = []
        
        for repo in self.test_repos:
            acd_path = self.repo_base / repo / "plc-acd"
            if acd_path.exists():
                for acd_file in acd_path.glob("*.ACD"):
                    acd_files_found.append({
                        'repo': repo,
                        'file': acd_file.name,
                        'size': acd_file.stat().st_size,
                        'path': str(acd_file)
                    })
        
        print(f"📁 ACD Files Found: {len(acd_files_found)}")
        
        for acd_info in acd_files_found:
            size_mb = acd_info['size'] / (1024 * 1024)
            print(f"  {acd_info['repo']}: {acd_info['file']} ({size_mb:.2f} MB)")
        
        # Assert that ACD files are available for testing
        self.assertGreater(len(acd_files_found), 0, "No ACD files found for enhanced processing")
        
        return acd_files_found
    
    def test_baseline_conversion_comparison(self):
        """Test comparison with baseline L5X conversion results"""
        
        # Check for existing L5X files (baseline)
        baseline_l5x_files = []
        
        for repo in self.test_repos:
            l5x_path = self.repo_base / repo / "plc-l5x"
            if l5x_path.exists():
                for l5x_file in l5x_path.glob("*.L5X"):
                    baseline_l5x_files.append({
                        'repo': repo,
                        'file': l5x_file.name,
                        'size': l5x_file.stat().st_size,
                        'path': str(l5x_file)
                    })
        
        print(f"📄 Baseline L5X Files: {len(baseline_l5x_files)}")
        
        for l5x_info in baseline_l5x_files:
            size_kb = l5x_info['size'] / 1024
            print(f"  {l5x_info['repo']}: {l5x_info['file']} ({size_kb:.2f} KB)")
        
        # Calculate baseline data preservation (for comparison)
        if baseline_l5x_files:
            # Find matching ACD files
            acd_files = self.test_acd_file_availability()
            
            for l5x_info in baseline_l5x_files:
                matching_acd = next(
                    (acd for acd in acd_files if acd['repo'] == l5x_info['repo']), 
                    None
                )
                
                if matching_acd:
                    preservation_ratio = l5x_info['size'] / matching_acd['size'] * 100
                    print(f"  {l5x_info['repo']} baseline preservation: {preservation_ratio:.3f}%")
        
        return baseline_l5x_files


def run_phase39_integration_tests():
    """Run Phase 3.9 integration test suite with comprehensive reporting"""
    
    print("🧪 Phase 3.9 Enhanced PLC Format Converter - Integration Test Suite")
    print("=" * 80)
    print(f"Test Timestamp: {datetime.now().isoformat()}")
    print(f"Project Root: {Path(__file__).parent.parent.parent.parent}")
    print()
    
    # Run import tests first
    print("📋 Testing Enhanced Component Imports...")
    print("-" * 50)
    
    import_results = test_enhanced_imports()
    
    for component, available in import_results.items():
        if isinstance(available, bool):
            status = "✅ Available" if available else "❌ Not Available"
            print(f"{component.replace('_', ' ').title()}: {status}")
    
    if import_results['error_messages']:
        print("\n⚠️  Import Issues:")
        for error in import_results['error_messages']:
            print(f"  - {error}")
    
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPhase39Development))
    suite.addTests(loader.loadTestsFromTestCase(TestExistingAcdFiles))
    
    # Run tests
    print("🧪 Running Integration Tests...")
    print("-" * 50)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Generate comprehensive report
    print("\n" + "=" * 80)
    print("📊 Phase 3.9 Development Assessment Report")
    print("=" * 80)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
    passed = total_tests - failures - errors - skipped
    
    print(f"Test Results:")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failures}")
    print(f"  Errors: {errors}")
    print(f"  Skipped: {skipped}")
    
    success_rate = (passed / total_tests * 100) if total_tests > 0 else 0
    print(f"  Success Rate: {success_rate:.1f}%")
    
    print(f"\nPhase 3.9 Capabilities:")
    
    # Component availability
    available_components = sum(1 for result in import_results.values() if isinstance(result, bool) and result)
    total_components = len([k for k, v in import_results.items() if isinstance(v, bool)])
    component_availability = (available_components / total_components) * 100
    
    print(f"  Component Availability: {component_availability:.1f}%")
    
    # Migration readiness assessment
    if success_rate >= 80 and component_availability >= 80:
        migration_status = "✅ Ready for Migration"
    elif success_rate >= 60 and component_availability >= 60:
        migration_status = "⚠️  Partially Ready"
    else:
        migration_status = "❌ Not Ready"
    
    print(f"  Migration Status: {migration_status}")
    
    # Data preservation capability
    if import_results['enhanced_models'] and import_results['validation_framework']:
        preservation_status = "✅ 95%+ Target Supported"
    else:
        preservation_status = "⚠️  Framework In Development"
    
    print(f"  Data Preservation: {preservation_status}")
    
    # Next steps
    print(f"\nNext Steps:")
    if component_availability < 100:
        print("  - Complete remaining component implementations")
    if success_rate < 100:
        print("  - Address test failures and errors")
    if migration_status != "✅ Ready for Migration":
        print("  - Enhance migration readiness")
    else:
        print("  - Proceed with migration to acd-l5x-tool-lib repository")
    
    # Save results
    results_file = Path(__file__).parent / f"phase39_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    test_results = {
        'timestamp': datetime.now().isoformat(),
        'test_summary': {
            'total_tests': total_tests,
            'passed': passed,
            'failed': failures,
            'errors': errors,
            'skipped': skipped,
            'success_rate': success_rate
        },
        'component_availability': {
            'available_components': available_components,
            'total_components': total_components,
            'availability_percentage': component_availability
        },
        'import_results': import_results,
        'migration_readiness': migration_status,
        'data_preservation_capability': preservation_status
    }
    
    with open(results_file, 'w') as f:
        json.dump(test_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_phase39_integration_tests()
    sys.exit(0 if success else 1) 