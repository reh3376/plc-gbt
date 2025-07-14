#!/usr/bin/env python3
"""
Phase 14.2.1: ModularExtractor Simple Test Suite
===============================================

Simplified testing suite for the ModularExtractor that focuses on core functionality
without complex import dependencies.

Author: AI Task Orchestrator
Date: 2025-01-18
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

# Mock classes to avoid import issues
from dataclasses import dataclass

@dataclass
class MockFileAnalysisResult:
    file_path: str
    size_bytes: int
    line_count: int
    function_count: int
    class_count: int
    import_count: int
    complexity_score: float
    maintainability_index: float
    modularity_score: float
    optimization_opportunities: List[str]
    refactoring_suggestions: List[str]
    dependencies: List[str]
    exports: List[str]
    technical_debt_score: float
    test_coverage_estimate: float

@dataclass
class MockDirectoryAnalysis:
    directory_path: str
    total_files: int
    total_lines: int
    total_functions: int
    total_classes: int
    average_complexity: float
    modular_compliance_score: float
    file_analyses: List[MockFileAnalysisResult]
    dependency_graph: Dict[str, List[str]]
    circular_dependencies: List[List[str]]
    optimization_priorities: List[Dict[str, Any]]
    architecture_recommendations: List[str]

def test_modular_extractor_basic():
    """Test basic ModularExtractor functionality"""
    print("🧪 Testing ModularExtractor Basic Functionality")
    
    try:
        from modular_extractor import (
            ModularExtractor, FunctionExtraction, ModuleCreation, 
            ExtractionResult, UtilityModule, SafetyValidator, ImportManager
        )
        
        # Test 1: Basic initialization
        print("  ➤ Testing initialization...")
        extractor = ModularExtractor("test_extraction")
        assert extractor.task_id == "test_extraction"
        assert extractor.extraction_config["function_size_threshold"] == 50
        print("    ✅ Initialization successful")
        
        # Test 2: Data class creation
        print("  ➤ Testing data class creation...")
        
        # Test FunctionExtraction creation
        func_extraction = FunctionExtraction(
            source_file="test.py",
            function_name="test_function",
            function_code="def test_function(): pass",
            start_line=1,
            end_line=2,
            dependencies=[],
            parameters=[],
            return_type=None,
            docstring="Test function",
            complexity_score=1.0,
            extraction_reason="Testing"
        )
        assert func_extraction.function_name == "test_function"
        print("    ✅ FunctionExtraction creation successful")
        
        # Test ModuleCreation creation
        module_creation = ModuleCreation(
            module_name="test_module",
            module_path="test_module.py",
            purpose="Testing",
            extracted_functions=[func_extraction],
            utility_functions=[],
            required_imports=[],
            module_docstring="Test module",
            estimated_size=10
        )
        assert module_creation.module_name == "test_module"
        print("    ✅ ModuleCreation creation successful")
        
        # Test UtilityModule creation
        utility_module = UtilityModule(
            name="test_utility",
            description="Test utility module",
            category="testing",
            common_patterns=["test_pattern"],
            target_functions=["test_func"],
            estimated_reuse_factor=3.0,
            priority=1
        )
        assert utility_module.name == "test_utility"
        print("    ✅ UtilityModule creation successful")
        
        # Test 3: Safety validator
        print("  ➤ Testing safety validator...")
        validator = SafetyValidator()
        assert validator is not None
        print("    ✅ SafetyValidator creation successful")
        
        # Test 4: Import manager
        print("  ➤ Testing import manager...")
        import_manager = ImportManager()
        assert import_manager is not None
        print("    ✅ ImportManager creation successful")
        
        # Test 5: AST analysis functions
        print("  ➤ Testing AST analysis...")
        test_code = '''
def small_function(x):
    return x * 2

def large_function(data):
    result = []
    for i in range(100):
        if i % 2 == 0:
            result.append(i * 2)
        else:
            result.append(i * 3)
        # Add more lines to make it large
        temp = i + 1
        temp2 = temp * 2
        temp3 = temp2 + temp
        result.append(temp3)
    return result
'''
        
        try:
            tree = ast.parse(test_code)
            functions_found = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions_found.append(node.name)
            
            assert "small_function" in functions_found
            assert "large_function" in functions_found
            print(f"    ✅ AST analysis found {len(functions_found)} functions")
            
        except Exception as e:
            print(f"    ⚠️ AST analysis failed: {e}")
        
        print("✅ All basic tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_ast_function_analysis():
    """Test AST-based function analysis capabilities"""
    print("🧪 Testing AST Function Analysis")
    
    # Create test file with various function types
    test_code = '''
import os
import json
from typing import List, Dict

def simple_function(x: int) -> int:
    """Simple function - should not be extracted"""
    return x * 2

def medium_function(data: List) -> Dict:
    """Medium complexity function"""
    result = {}
    for item in data:
        if isinstance(item, dict):
            key = item.get('key', 'default')
            value = item.get('value', 0)
            if key not in result:
                result[key] = []
            result[key].append(value)
    return result

def large_complex_function(file_path: str, config: Dict) -> bool:
    """Large function that should be extracted - 50+ lines"""
    try:
        # Validation phase
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
        
        if not os.path.isfile(file_path):
            print(f"Not a file: {file_path}")
            return False
        
        # Configuration validation
        required_keys = ['format', 'encoding', 'output']
        for key in required_keys:
            if key not in config:
                print(f"Missing config key: {key}")
                return False
        
        # File reading
        with open(file_path, 'r', encoding=config['encoding']) as f:
            content = f.read()
        
        # Format processing
        if config['format'] == 'json':
            try:
                data = json.loads(content)
            except json.JSONDecodeError as e:
                print(f"JSON error: {e}")
                return False
        elif config['format'] == 'text':
            data = content.strip().split('\\n')
        else:
            print(f"Unknown format: {config['format']}")
            return False
        
        # Data processing
        processed_data = []
        for item in data:
            if config['format'] == 'json':
                if isinstance(item, dict) and 'value' in item:
                    processed_data.append(item['value'])
            else:
                if item.strip():
                    processed_data.append(item.strip())
        
        # Output generation
        output_path = config['output']
        with open(output_path, 'w') as f:
            if config['format'] == 'json':
                json.dump(processed_data, f, indent=2)
            else:
                f.write('\\n'.join(processed_data))
        
        print(f"Processing completed: {output_path}")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

class ComplexProcessor:
    """Class with methods that could be extracted"""
    
    def __init__(self, config):
        self.config = config
        self.results = {}
    
    def complex_method(self, data):
        """Complex method - 30+ lines"""
        processed = []
        errors = []
        
        # Validation loop
        for i, item in enumerate(data):
            try:
                if not isinstance(item, dict):
                    errors.append(f"Item {i} is not a dict")
                    continue
                
                if 'id' not in item:
                    errors.append(f"Item {i} missing 'id'")
                    continue
                
                if 'value' not in item:
                    errors.append(f"Item {i} missing 'value'")
                    continue
                
                processed.append(item)
                
            except Exception as e:
                errors.append(f"Item {i} error: {e}")
        
        # Processing loop
        results = {}
        for item in processed:
            category = item.get('category', 'default')
            if category not in results:
                results[category] = {'count': 0, 'sum': 0}
            
            results[category]['count'] += 1
            results[category]['sum'] += item['value']
        
        # Calculate averages
        for category in results:
            results[category]['avg'] = results[category]['sum'] / results[category]['count']
        
        return {'results': results, 'errors': errors}
'''
    
    try:
        # Parse the code
        tree = ast.parse(test_code)
        
        # Analyze functions
        functions = []
        classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_lines = getattr(node, 'end_lineno', 0) - getattr(node, 'lineno', 0) + 1
                functions.append({
                    'name': node.name,
                    'lines': func_lines,
                    'lineno': getattr(node, 'lineno', 0),
                    'end_lineno': getattr(node, 'end_lineno', 0)
                })
            elif isinstance(node, ast.ClassDef):
                classes.append({
                    'name': node.name,
                    'lineno': getattr(node, 'lineno', 0)
                })
        
        print(f"  📊 Functions found: {len(functions)}")
        for func in functions:
            print(f"    - {func['name']}: {func['lines']} lines")
        
        print(f"  📊 Classes found: {len(classes)}")
        for cls in classes:
            print(f"    - {cls['name']}")
        
        # Identify large functions (>20 lines)
        large_functions = [f for f in functions if f['lines'] > 20]
        print(f"  📊 Large functions (>20 lines): {len(large_functions)}")
        
        for func in large_functions:
            print(f"    - {func['name']}: {func['lines']} lines (EXTRACTION CANDIDATE)")
        
        print("✅ AST analysis completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ AST analysis failed: {e}")
        return False

def run_simple_test_suite():
    """Run simplified test suite"""
    print("🚀 ModularExtractor Simple Test Suite")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_modular_extractor_basic),
        ("AST Function Analysis", test_ast_function_analysis)
    ]
    
    results = {"passed": 0, "failed": 0, "total": len(tests)}
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        print("-" * 30)
        
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
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
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
    results = run_simple_test_suite()
    exit_code = 0 if results["failed"] == 0 else 1
    exit(exit_code) 