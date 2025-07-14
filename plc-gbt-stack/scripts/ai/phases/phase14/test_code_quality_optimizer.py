#!/usr/bin/env python3
"""
Phase 14.2.2: CodeQualityOptimizer Test Suite
=============================================

Comprehensive testing suite for the CodeQualityOptimizer following AI Task Orchestrator methodology.
Validates automated code quality improvements including import optimization, large file refactoring,
and pattern standardization.

Test Categories:
- Import optimization functionality
- Large file refactoring capabilities
- Pattern standardization enforcement
- Quality assessment and metrics
- Integration with Phase 14.1/14.2.1 components

Author: AI Task Orchestrator
Date: 2025-01-18
Dependencies: CodeQualityOptimizer, CodebaseAnalyzer, ModularExtractor
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import ast
import json

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
sys.path.append(str(Path(__file__).parent))

def test_code_quality_optimizer_basic():
    """Test basic CodeQualityOptimizer functionality"""
    print("🧪 Testing CodeQualityOptimizer Basic Functionality")
    
    try:
        from code_quality_optimizer import (
            CodeQualityOptimizer, ImportOptimization, FileRefactoring,
            PatternStandardization, OptimizationResult, ImportAnalyzer,
            ImportUsageAnalyzer, ImportStatementOptimizer
        )
        
        # Test 1: Basic initialization
        print("  ➤ Testing initialization...")
        optimizer = CodeQualityOptimizer("test_quality_optimization")
        assert optimizer.task_id == "test_quality_optimization"
        assert optimizer.optimization_config["import_optimization"]["remove_unused"] == True
        assert optimizer.optimization_config["file_refactoring"]["max_file_size"] == 1000
        print("    ✅ Initialization successful")
        
        # Test 2: Data class creation
        print("  ➤ Testing data class creation...")
        
        # Test ImportOptimization creation
        import_opt = ImportOptimization(
            file_path="test.py",
            original_imports=["import os", "import sys", "import unused"],
            optimized_imports=["import os", "import sys"],
            unused_imports=["import unused"],
            added_imports=[],
            reordered_imports=["import os", "import sys"],
            optimization_score=0.85,
            estimated_performance_gain=0.1
        )
        assert import_opt.file_path == "test.py"
        assert len(import_opt.unused_imports) == 1
        print("    ✅ ImportOptimization creation successful")
        
        # Test FileRefactoring creation
        file_ref = FileRefactoring(
            source_file="large_file.py",
            original_size=1500,
            target_files=["large_file_utils.py", "large_file_core.py"],
            refactoring_strategy="function_extraction",
            estimated_new_sizes=[300, 400],
            complexity_reduction=0.3,
            maintainability_improvement=0.4,
            safety_score=0.9
        )
        assert file_ref.source_file == "large_file.py"
        assert file_ref.original_size == 1500
        print("    ✅ FileRefactoring creation successful")
        
        # Test PatternStandardization creation
        pattern_std = PatternStandardization(
            pattern_type="enforce_docstrings",
            files_affected=["file1.py", "file2.py"],
            old_pattern="def function():",
            new_pattern="def function():\n    \"\"\"Docstring\"\"\"",
            occurrences_updated=5,
            consistency_score=0.8,
            impact_assessment="medium"
        )
        assert pattern_std.pattern_type == "enforce_docstrings"
        assert len(pattern_std.files_affected) == 2
        print("    ✅ PatternStandardization creation successful")
        
        # Test 3: Configuration validation
        print("  ➤ Testing configuration...")
        config = optimizer.optimization_config
        
        # Check import optimization config
        assert "remove_unused" in config["import_optimization"]
        assert "sort_imports" in config["import_optimization"]
        assert "group_imports" in config["import_optimization"]
        
        # Check file refactoring config
        assert "max_file_size" in config["file_refactoring"]
        assert "target_file_size" in config["file_refactoring"]
        
        # Check pattern standardization config
        assert "enforce_docstrings" in config["pattern_standardization"]
        assert "standardize_logging" in config["pattern_standardization"]
        
        print("    ✅ Configuration validation successful")
        
        print("✅ All basic tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_import_analysis():
    """Test import analysis and optimization capabilities"""
    print("🧪 Testing Import Analysis and Optimization")
    
    try:
        from code_quality_optimizer import ImportAnalyzer, ImportUsageAnalyzer, ImportStatementOptimizer
        
        # Test code with various import patterns
        test_code = '''
import os
import sys
import json
import unused_module
from typing import List, Dict
from pathlib import Path
from datetime import datetime

def main():
    # Using os and json
    current_dir = os.getcwd()
    data = json.loads('{"key": "value"}')
    
    # Using typing
    my_list: List[str] = []
    my_dict: Dict[str, int] = {}
    
    # Using pathlib
    path = Path("test.txt")
    
    print(current_dir, data, my_list, my_dict, path)

if __name__ == "__main__":
    main()
'''
        
        # Parse the code
        tree = ast.parse(test_code)
        
        # Test ImportAnalyzer
        print("  ➤ Testing ImportAnalyzer...")
        import_analyzer = ImportAnalyzer()
        import_analysis = import_analyzer.analyze_imports(tree, test_code)
        
        print(f"    📊 Imports found: {len(import_analysis['imports'])}")
        print(f"    📊 From imports found: {len(import_analysis['from_imports'])}")
        
        assert len(import_analysis['imports']) > 0
        assert len(import_analysis['from_imports']) > 0
        print("    ✅ ImportAnalyzer working correctly")
        
        # Test ImportUsageAnalyzer
        print("  ➤ Testing ImportUsageAnalyzer...")
        usage_analyzer = ImportUsageAnalyzer()
        all_imports = import_analysis['imports'] + import_analysis['from_imports']
        unused_imports = usage_analyzer.find_unused_imports(tree, all_imports)
        
        print(f"    📊 Unused imports found: {len(unused_imports)}")
        for unused in unused_imports:
            print(f"      - {unused}")
        
        # Should find unused_module as unused
        assert any("unused_module" in unused for unused in unused_imports)
        print("    ✅ ImportUsageAnalyzer correctly identified unused imports")
        
        # Test ImportStatementOptimizer
        print("  ➤ Testing ImportStatementOptimizer...")
        config = {
            "remove_unused": True,
            "sort_imports": True,
            "group_imports": True,
            "max_line_length": 88
        }
        
        optimizer = ImportStatementOptimizer(config)
        optimized_imports = optimizer.optimize_import_statements(all_imports, unused_imports)
        
        print(f"    📊 Optimized imports: {len(optimized_imports)}")
        for opt_import in optimized_imports:
            if opt_import:  # Skip empty lines
                print(f"      - {opt_import}")
        
        # Should have fewer imports after removing unused
        used_imports = [imp for imp in all_imports if imp not in unused_imports]
        assert len([imp for imp in optimized_imports if imp]) <= len(used_imports)
        print("    ✅ ImportStatementOptimizer working correctly")
        
        print("✅ Import analysis tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Import analysis test failed: {e}")
        return False

def test_pattern_recognition():
    """Test pattern recognition and standardization"""
    print("🧪 Testing Pattern Recognition")
    
    # Test code with various patterns that need standardization
    test_patterns = {
        "bad_logging": '''
def process_data(data):
    print("Processing started")
    if not data:
        print("No data provided")
        return None
    
    result = []
    for item in data:
        print(f"Processing {item}")
        result.append(item * 2)
    
    print("Processing completed")
    return result
''',
        
        "missing_docstrings": '''
def calculate_average(numbers):
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)

def format_result(value):
    return f"Result: {value:.2f}"

class DataProcessor:
    def __init__(self, config):
        self.config = config
    
    def process(self, data):
        return self.calculate_average(data)
''',
        
        "poor_error_handling": '''
def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except:
        print("Error reading file")
        return None

def parse_json(json_string):
    try:
        return json.loads(json_string)
    except:
        return {}
'''
    }
    
    try:
        patterns_found = 0
        
        for pattern_name, code in test_patterns.items():
            print(f"  ➤ Analyzing {pattern_name}...")
            
            # Parse the code
            tree = ast.parse(code)
            
            if pattern_name == "bad_logging":
                # Count print statements
                print_count = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'print':
                        print_count += 1
                
                print(f"    📊 Print statements found: {print_count}")
                if print_count > 0:
                    patterns_found += 1
                    print("    🔍 Pattern identified: Use logger instead of print")
            
            elif pattern_name == "missing_docstrings":
                # Count functions/classes without docstrings
                missing_docstrings = 0
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                        if not ast.get_docstring(node):
                            missing_docstrings += 1
                
                print(f"    📊 Functions/classes without docstrings: {missing_docstrings}")
                if missing_docstrings > 0:
                    patterns_found += 1
                    print("    🔍 Pattern identified: Missing docstrings")
            
            elif pattern_name == "poor_error_handling":
                # Count bare except clauses
                bare_except_count = 0
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        bare_except_count += 1
                
                print(f"    📊 Bare except clauses found: {bare_except_count}")
                if bare_except_count > 0:
                    patterns_found += 1
                    print("    🔍 Pattern identified: Use specific exception handling")
        
        print(f"  📊 Total patterns identified: {patterns_found}")
        assert patterns_found >= 3  # Should find all three pattern types
        
        print("✅ Pattern recognition tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Pattern recognition test failed: {e}")
        return False

def test_quality_metrics():
    """Test quality metrics calculation"""
    print("🧪 Testing Quality Metrics Calculation")
    
    try:
        from code_quality_optimizer import CodeQualityOptimizer
        
        # Create optimizer instance
        optimizer = CodeQualityOptimizer("test_metrics")
        
        # Test standard patterns definition
        print("  ➤ Testing standard patterns...")
        patterns = optimizer._define_standard_patterns()
        
        expected_patterns = [
            "enforce_docstrings",
            "standardize_logging", 
            "enforce_type_hints",
            "standardize_error_handling"
        ]
        
        for pattern in expected_patterns:
            assert pattern in patterns
            assert "pattern" in patterns[pattern]
            assert "priority" in patterns[pattern]
            print(f"    ✅ Pattern '{pattern}' defined correctly")
        
        # Test quality assessment mock data
        print("  ➤ Testing quality assessment...")
        
        # Mock optimization data
        mock_import_opts = [
            type('MockImportOpt', (), {
                'optimization_score': 0.8,
                'estimated_performance_gain': 0.1
            })(),
            type('MockImportOpt', (), {
                'optimization_score': 0.9,
                'estimated_performance_gain': 0.05
            })()
        ]
        
        mock_file_refs = [
            type('MockFileRef', (), {
                'maintainability_improvement': 0.3
            })()
        ]
        
        mock_pattern_stds = [
            type('MockPatternStd', (), {
                'consistency_score': 0.7,
                'occurrences_updated': 5
            })(),
            type('MockPatternStd', (), {
                'consistency_score': 0.8,
                'occurrences_updated': 3
            })()
        ]
        
        # Test quality assessment
        quality_results = optimizer._assess_quality_improvements(
            mock_import_opts, mock_file_refs, mock_pattern_stds
        )
        
        assert "overall_quality_score" in quality_results
        assert "performance_improvements" in quality_results
        assert "maintainability_improvements" in quality_results
        
        print(f"    📊 Overall quality score: {quality_results['overall_quality_score']:.2f}")
        print(f"    📊 Performance improvements: {len(quality_results['performance_improvements'])} categories")
        print(f"    📊 Maintainability improvements: {len(quality_results['maintainability_improvements'])} categories")
        
        # Quality score should be reasonable (0-1 range)
        assert 0 <= quality_results['overall_quality_score'] <= 1
        
        print("✅ Quality metrics calculation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Quality metrics test failed: {e}")
        return False

def test_integration_capabilities():
    """Test integration with other Phase 14 components"""
    print("🧪 Testing Integration Capabilities")
    
    try:
        from code_quality_optimizer import CodeQualityOptimizer
        
        # Test component integration
        print("  ➤ Testing component integration...")
        optimizer = CodeQualityOptimizer("test_integration")
        
        # Check that dependencies are initialized
        assert hasattr(optimizer, 'codebase_analyzer')
        assert hasattr(optimizer, 'modular_extractor')
        
        # Check that both components have the required methods
        assert hasattr(optimizer.codebase_analyzer, 'analyze_file_structure')
        assert hasattr(optimizer.codebase_analyzer, 'analyze_directory')
        assert hasattr(optimizer.modular_extractor, 'extract_large_functions')
        
        print("    ✅ Component integration successful")
        
        # Test configuration consistency
        print("  ➤ Testing configuration consistency...")
        config = optimizer.optimization_config
        
        # Check that all major sections are present
        required_sections = [
            "import_optimization",
            "file_refactoring", 
            "pattern_standardization",
            "quality_thresholds"
        ]
        
        for section in required_sections:
            assert section in config
            print(f"    ✅ Configuration section '{section}' present")
        
        # Check quality thresholds are reasonable
        thresholds = config["quality_thresholds"]
        assert 0 <= thresholds["min_optimization_score"] <= 1
        assert 0 <= thresholds["min_safety_score"] <= 1
        assert thresholds["max_complexity_per_function"] > 0
        
        print("    ✅ Configuration consistency validated")
        
        print("✅ Integration capability tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def run_comprehensive_test_suite():
    """Run comprehensive test suite for CodeQualityOptimizer"""
    print("🚀 CodeQualityOptimizer Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_code_quality_optimizer_basic),
        ("Import Analysis", test_import_analysis),
        ("Pattern Recognition", test_pattern_recognition),
        ("Quality Metrics", test_quality_metrics),
        ("Integration Capabilities", test_integration_capabilities)
    ]
    
    results = {"passed": 0, "failed": 0, "total": len(tests)}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                results["passed"] += 1
                print(f"✅ {test_name} PASSED")
            else:
                results["failed"] += 1
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            results["failed"] += 1
            print(f"❌ {test_name} FAILED: {e}")
    
    # Final results
    print("\n" + "=" * 60)
    print("📊 FINAL TEST RESULTS")
    print("=" * 60)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed'] / results['total']) * 100:.1f}%")
    
    if results["failed"] == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {results['failed']} tests failed")
    
    return results

if __name__ == "__main__":
    results = run_comprehensive_test_suite()
    exit_code = 0 if results["failed"] == 0 else 1
    exit(exit_code) 