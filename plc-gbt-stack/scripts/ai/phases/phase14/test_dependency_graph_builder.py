#!/usr/bin/env python3
"""
Test Script for Phase 14.1.2 DependencyGraphBuilder
===================================================

Test the advanced dependency graph analysis functionality with real project data.
Following AI Task Orchestrator methodology for validation.

Usage:
    python test_dependency_graph_builder.py [directory_path]
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

from dependency_graph_builder import DependencyGraphBuilder, ImportNode, CircularDependency

def test_basic_functionality():
    """Test basic dependency graph builder functionality"""
    print("🧪 Testing DependencyGraphBuilder Basic Functionality")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_dependency_graph")
        print(f"✅ DependencyGraphBuilder initialized successfully")
        print(f"   Task ID: {builder.task_id}")
        print(f"   Session ID: {builder.session_id}")
        
        # Test task analysis
        task_analysis = builder._analyze_task()
        print(f"✅ Task analysis completed")
        print(f"   Complexity: {task_analysis.complexity}")
        print(f"   Estimated time: {task_analysis.estimated_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_import_extraction():
    """Test import extraction from files"""
    print("\n🧪 Testing Import Extraction")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_import_extraction")
        
        # Test with current file
        current_file = Path(__file__)
        builder._extract_file_imports(current_file)
        
        file_imports = builder.module_registry.get(str(current_file), {}).get("imports", [])
        
        print(f"✅ Import extraction completed for: {current_file.name}")
        print(f"   Imports found: {len(file_imports)}")
        print(f"   Module registered: {str(current_file) in builder.module_registry}")
        
        if file_imports:
            print("   Sample imports:")
            for imp in file_imports[:3]:
                print(f"     - {imp.import_statement} (line {imp.line_number})")
        
        return True
        
    except Exception as e:
        print(f"❌ Import extraction test failed: {e}")
        return False

def test_dependency_graph_construction(target_dir: str = None):
    """Test full dependency graph construction"""
    print("\n🧪 Testing Dependency Graph Construction")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_graph_construction")
        
        # Use provided directory or current phase14 directory
        if target_dir:
            analysis_dir = target_dir
        else:
            analysis_dir = str(Path(__file__).parent)  # phase14 directory
        
        print(f"🔍 Building dependency graph for: {analysis_dir}")
        
        graph_analysis = builder.build_import_graph(analysis_dir)
        
        print(f"✅ Dependency graph construction completed")
        print(f"   Total modules: {graph_analysis.total_modules}")
        print(f"   Total dependencies: {graph_analysis.total_dependencies}")
        print(f"   Graph depth: {graph_analysis.graph_depth}")
        print(f"   Clustering coefficient: {graph_analysis.clustering_coefficient:.3f}")
        print(f"   Import nodes: {len(graph_analysis.import_nodes)}")
        print(f"   Circular dependencies: {len(graph_analysis.circular_dependencies)}")
        print(f"   Modular opportunities: {len(graph_analysis.modular_opportunities)}")
        
        # Show circular dependencies if any
        if graph_analysis.circular_dependencies:
            print("\n🔄 Circular Dependencies Found:")
            for i, circ_dep in enumerate(graph_analysis.circular_dependencies[:3], 1):
                print(f"   {i}. {circ_dep.cycle_id} (Length: {circ_dep.cycle_length})")
                print(f"      Complexity: {circ_dep.resolution_complexity}")
                print(f"      Total imports: {circ_dep.total_imports}")
        
        # Show modular opportunities
        if graph_analysis.modular_opportunities:
            print("\n🏗️ Modular Extraction Opportunities:")
            for i, opportunity in enumerate(graph_analysis.modular_opportunities[:3], 1):
                print(f"   {i}. {opportunity.opportunity_id}")
                print(f"      Type: {opportunity.extraction_type}")
                print(f"      Files: {len(opportunity.target_files)}")
                print(f"      Common deps: {len(opportunity.common_dependencies)}")
        
        # Show architectural insights
        if graph_analysis.architectural_insights:
            print("\n📊 Architectural Insights:")
            insights = graph_analysis.architectural_insights
            print(f"   Average dependencies: {insights.get('average_dependencies', 0):.1f}")
            highly_coupled = insights.get('highly_coupled_modules', [])
            if highly_coupled:
                print(f"   Highly coupled modules: {len(highly_coupled)}")
        
        return True, graph_analysis
        
    except Exception as e:
        print(f"❌ Dependency graph construction test failed: {e}")
        return False, None

def test_circular_dependency_detection():
    """Test advanced circular dependency detection"""
    print("\n🧪 Testing Circular Dependency Detection")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_circular_detection")
        
        # Create a simple test graph with circular dependencies
        builder.module_registry = {
            "moduleA.py": {"name": "moduleA", "imports": []},
            "moduleB.py": {"name": "moduleB", "imports": []},
            "moduleC.py": {"name": "moduleC", "imports": []}
        }
        
        # Create circular dependency: A -> B -> C -> A
        builder.import_graph = {
            "moduleA.py": ["moduleB.py"],
            "moduleB.py": ["moduleC.py"],
            "moduleC.py": ["moduleA.py"]
        }
        
        circular_deps = builder.identify_circular_dependencies()
        
        print(f"✅ Circular dependency detection completed")
        print(f"   Cycles found: {len(circular_deps)}")
        
        for i, cycle in enumerate(circular_deps, 1):
            print(f"   Cycle {i}: {cycle.cycle_id}")
            print(f"     Path: {' -> '.join([Path(p).stem for p in cycle.cycle_path])}")
            print(f"     Length: {cycle.cycle_length}")
            print(f"     Complexity: {cycle.resolution_complexity}")
            
            if cycle.suggested_resolution:
                print(f"     Suggestions:")
                for suggestion in cycle.suggested_resolution[:2]:
                    print(f"       - {suggestion}")
        
        return True
        
    except Exception as e:
        print(f"❌ Circular dependency detection test failed: {e}")
        return False

def test_modular_extraction_suggestions():
    """Test modular extraction opportunity identification"""
    print("\n🧪 Testing Modular Extraction Suggestions")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_modular_extraction")
        
        # Create test scenario with common dependencies
        builder.module_registry = {
            "fileA.py": {"name": "fileA", "imports": []},
            "fileB.py": {"name": "fileB", "imports": []},
            "fileC.py": {"name": "fileC", "imports": []},
            "utilA.py": {"name": "utilA", "imports": []},
            "utilB.py": {"name": "utilB", "imports": []}
        }
        
        # Create common dependency patterns
        builder.import_graph = {
            "fileA.py": ["utilA.py", "utilB.py"],
            "fileB.py": ["utilA.py", "utilB.py"],
            "fileC.py": ["utilA.py", "utilB.py"]
        }
        
        opportunities = builder.suggest_modular_extraction()
        
        print(f"✅ Modular extraction analysis completed")
        print(f"   Opportunities found: {len(opportunities)}")
        
        for i, opportunity in enumerate(opportunities, 1):
            print(f"   Opportunity {i}: {opportunity.opportunity_id}")
            print(f"     Type: {opportunity.extraction_type}")
            print(f"     Target files: {len(opportunity.target_files)}")
            print(f"     Common dependencies: {len(opportunity.common_dependencies)}")
            print(f"     Estimated benefit: {opportunity.estimated_benefit}")
            
            if opportunity.implementation_steps:
                print(f"     Implementation steps:")
                for step in opportunity.implementation_steps[:3]:
                    print(f"       - {step}")
        
        return True
        
    except Exception as e:
        print(f"❌ Modular extraction suggestions test failed: {e}")
        return False

def test_full_execution():
    """Test full dependency graph builder execution"""
    print("\n🧪 Testing Full Dependency Graph Execution")
    print("=" * 60)
    
    try:
        builder = DependencyGraphBuilder("test_full_execution")
        
        results = builder.execute()
        
        if results.get("status") == "failed":
            print(f"❌ Full execution failed: {results.get('error')}")
            return False
        
        print(f"✅ Full execution completed successfully")
        
        # Display summary metrics
        metrics = results.get("metrics", {})
        print(f"   Files processed: {metrics.get('files_processed', 0)}")
        print(f"   Imports analyzed: {metrics.get('imports_analyzed', 0)}")
        print(f"   Circular deps found: {metrics.get('circular_deps_found', 0)}")
        print(f"   Extraction opportunities: {metrics.get('extraction_opportunities', 0)}")
        
        # Display graph analysis summary
        graph_analysis = results.get("graph_analysis", {})
        if graph_analysis:
            print(f"\n📊 Dependency Graph Summary:")
            print(f"   Total modules: {graph_analysis.get('total_modules', 0)}")
            print(f"   Total dependencies: {graph_analysis.get('total_dependencies', 0)}")
            print(f"   Graph depth: {graph_analysis.get('graph_depth', 0)}")
            print(f"   Clustering coefficient: {graph_analysis.get('clustering_coefficient', 0):.3f}")
        
        # Show optimization recommendations
        optimization_recs = graph_analysis.get("optimization_recommendations", [])
        if optimization_recs:
            print(f"\n🎯 Optimization Recommendations:")
            for rec in optimization_recs[:3]:
                print(f"   - {rec}")
        
        # Save results for inspection
        results_file = Path(__file__).parent / f"dependency_graph_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full execution test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Phase 14.1.2 DependencyGraphBuilder Validation Suite")
    print("=" * 70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get target directory from command line args
    target_directory = sys.argv[1] if len(sys.argv) > 1 else None
    if target_directory:
        print(f"Target directory: {target_directory}")
    
    # Run test suite
    test_results = []
    
    # Test 1: Basic functionality
    test_results.append(("Basic Functionality", test_basic_functionality()))
    
    # Test 2: Import extraction
    test_results.append(("Import Extraction", test_import_extraction()))
    
    # Test 3: Dependency graph construction
    graph_test_result, graph_analysis = test_dependency_graph_construction(target_directory)
    test_results.append(("Graph Construction", graph_test_result))
    
    # Test 4: Circular dependency detection
    test_results.append(("Circular Detection", test_circular_dependency_detection()))
    
    # Test 5: Modular extraction suggestions
    test_results.append(("Modular Extraction", test_modular_extraction_suggestions()))
    
    # Test 6: Full execution
    test_results.append(("Full Execution", test_full_execution()))
    
    # Summary
    print("\n" + "=" * 70)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! DependencyGraphBuilder is ready for Phase 14.1.3")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 