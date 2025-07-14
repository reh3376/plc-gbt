#!/usr/bin/env python3
"""
Test Script for Phase 14.1.1 CodebaseAnalyzer
==============================================

Test the comprehensive codebase analysis functionality with real project data.
Following AI Task Orchestrator methodology for validation.

Usage:
    python test_codebase_analyzer.py [directory_path]
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add modules to path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))

from codebase_analyzer import CodebaseAnalyzer, FileAnalysisResult, DirectoryAnalysis

def test_basic_functionality():
    """Test basic analyzer functionality"""
    print("🧪 Testing CodebaseAnalyzer Basic Functionality")
    print("=" * 60)
    
    try:
        analyzer = CodebaseAnalyzer("test_analysis")
        print(f"✅ CodebaseAnalyzer initialized successfully")
        print(f"   Task ID: {analyzer.task_id}")
        print(f"   Session ID: {analyzer.session_id}")
        
        # Test task analysis
        task_analysis = analyzer._analyze_task()
        print(f"✅ Task analysis completed")
        print(f"   Complexity: {task_analysis.complexity}")
        print(f"   Estimated time: {task_analysis.estimated_time}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_file_analysis():
    """Test individual file analysis"""
    print("\n🧪 Testing Individual File Analysis")
    print("=" * 60)
    
    try:
        analyzer = CodebaseAnalyzer("test_file_analysis")
        
        # Analyze this test file
        current_file = __file__
        analysis = analyzer.analyze_file_structure(current_file)
        
        print(f"✅ File analysis completed for: {Path(current_file).name}")
        print(f"   Lines: {analysis.line_count}")
        print(f"   Functions: {analysis.function_count}")
        print(f"   Complexity: {analysis.complexity_score}")
        print(f"   Modularity: {analysis.modularity_score:.2f}")
        print(f"   Optimization opportunities: {len(analysis.optimization_opportunities)}")
        
        if analysis.optimization_opportunities:
            print("   Recommendations:")
            for opp in analysis.optimization_opportunities[:3]:
                print(f"     - {opp}")
        
        return True
        
    except Exception as e:
        print(f"❌ File analysis test failed: {e}")
        return False

def test_directory_analysis(target_dir: str = None):
    """Test directory analysis with real project data"""
    print("\n🧪 Testing Directory Analysis")
    print("=" * 60)
    
    try:
        analyzer = CodebaseAnalyzer("test_directory_analysis")
        
        # Use provided directory or current project scripts
        if target_dir:
            analysis_dir = target_dir
        else:
            analysis_dir = str(Path(__file__).parent.parent.parent)  # ai scripts directory
        
        print(f"🔍 Analyzing directory: {analysis_dir}")
        
        analysis = analyzer.analyze_directory(analysis_dir)
        
        print(f"✅ Directory analysis completed")
        print(f"   Total files: {analysis.total_files}")
        print(f"   Total lines: {analysis.total_lines}")
        print(f"   Total functions: {analysis.total_functions}")
        print(f"   Average complexity: {analysis.average_complexity:.2f}")
        print(f"   Modular compliance: {analysis.modular_compliance_score:.2f}")
        print(f"   Circular dependencies: {len(analysis.circular_dependencies)}")
        print(f"   Optimization priorities: {len(analysis.optimization_priorities)}")
        
        # Show top optimization priorities
        if analysis.optimization_priorities:
            print("\n📋 Top 3 Optimization Priorities:")
            for i, priority in enumerate(analysis.optimization_priorities[:3], 1):
                file_name = Path(priority["file_path"]).name
                print(f"   {i}. {file_name} (Score: {priority['priority_score']})")
                for opp in priority["opportunities"][:2]:
                    print(f"      - {opp}")
        
        # Show architecture recommendations
        if analysis.architecture_recommendations:
            print("\n🏗️ Architecture Recommendations:")
            for rec in analysis.architecture_recommendations[:3]:
                print(f"   - {rec}")
        
        return True, analysis
        
    except Exception as e:
        print(f"❌ Directory analysis test failed: {e}")
        return False, None

def test_refactoring_plans(directory_analysis: DirectoryAnalysis):
    """Test refactoring plan generation"""
    print("\n🧪 Testing Refactoring Plan Generation")
    print("=" * 60)
    
    try:
        analyzer = CodebaseAnalyzer("test_refactoring_plans")
        
        refactoring_plans = analyzer.identify_refactoring_opportunities(directory_analysis)
        
        print(f"✅ Refactoring plans generated: {len(refactoring_plans)}")
        
        for i, plan in enumerate(refactoring_plans[:3], 1):
            print(f"\n   Plan {i}: {plan.plan_id}")
            print(f"     Type: {plan.refactoring_type}")
            print(f"     Effort: {plan.estimated_effort}")
            print(f"     Safety: {plan.safety_score:.1f}")
            print(f"     Files: {len(plan.target_files)}")
            print(f"     Steps: {len(plan.step_by_step_plan)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Refactoring plans test failed: {e}")
        return False

def test_full_execution():
    """Test full analyzer execution"""
    print("\n🧪 Testing Full Analyzer Execution")
    print("=" * 60)
    
    try:
        analyzer = CodebaseAnalyzer("test_full_execution")
        
        results = analyzer.execute()
        
        if results.get("status") == "failed":
            print(f"❌ Full execution failed: {results.get('error')}")
            return False
        
        print(f"✅ Full execution completed successfully")
        
        # Display summary metrics
        metrics = results.get("metrics", {})
        print(f"   Files analyzed: {metrics.get('files_analyzed', 0)}")
        print(f"   Optimization opportunities: {metrics.get('optimization_opportunities', 0)}")
        print(f"   Refactoring suggestions: {metrics.get('refactoring_suggestions', 0)}")
        
        # Display performance summary
        perf_summary = results.get("performance_summary", {})
        if perf_summary:
            health = perf_summary.get("codebase_health", {})
            print(f"\n📊 Codebase Health Summary:")
            print(f"   Average complexity: {health.get('average_complexity', 0):.2f}")
            print(f"   Modular compliance: {health.get('modular_compliance', 0):.2f}")
            print(f"   Technical debt: {health.get('total_technical_debt', 0):.1f}")
            print(f"   Test coverage estimate: {health.get('estimated_test_coverage', 0):.1%}")
        
        # Save results for inspection
        results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Full execution test failed: {e}")
        return False

def main():
    """Main test execution"""
    print("🚀 Phase 14.1.1 CodebaseAnalyzer Validation Suite")
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
    
    # Test 2: File analysis
    test_results.append(("File Analysis", test_file_analysis()))
    
    # Test 3: Directory analysis
    dir_test_result, directory_analysis = test_directory_analysis(target_directory)
    test_results.append(("Directory Analysis", dir_test_result))
    
    # Test 4: Refactoring plans (if directory analysis succeeded)
    if directory_analysis:
        test_results.append(("Refactoring Plans", test_refactoring_plans(directory_analysis)))
    
    # Test 5: Full execution
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
        print("🎉 All tests passed! CodebaseAnalyzer is ready for Phase 14.1.2")
    else:
        print("⚠️  Some tests failed. Review errors above.")
    
    print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 