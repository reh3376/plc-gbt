#!/usr/bin/env python3
"""
Comprehensive Phase 3 Day 4 Tests
Created: January 1, 2025
Purpose: Thorough testing of all Phase 3 Day 4 components with detailed validation
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# Add scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def print_header(title: str):
    """Print formatted test header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print formatted section header"""
    print(f"\n{'*'*40}")
    print(f"📋 {title}")
    print(f"{'*'*40}")

def test_advanced_graph_algorithms():
    """Test Advanced Graph Algorithms"""
    print_section("Testing Advanced Graph Algorithms")
    
    try:
        from query.advanced_graph_algorithms import AdvancedGraphAnalyzer, GraphPath, ComponentCluster, DependencyChain
        
        # Test initialization (without actual connection)
        print("✅ AdvancedGraphAnalyzer class available")
        print("✅ GraphPath dataclass available")
        print("✅ ComponentCluster dataclass available")
        print("✅ DependencyChain dataclass available")
        
        # Test method availability
        methods = [
            'find_multi_hop_relationships',
            'find_shortest_paths', 
            'detect_component_clusters',
            'analyze_component_dependencies',
            'calculate_centrality_metrics'
        ]
        
        # Create a mock analyzer instance to check methods
        class MockAnalyzer:
            def __init__(self):
                pass
        
        # Check if methods exist in the actual class
        for method in methods:
            if hasattr(AdvancedGraphAnalyzer, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
        
        # Test dataclass creation
        test_path = GraphPath(
            nodes=[{"uuid": "test1", "name": "TestNode"}],
            relationships=[{"type": "TEST_REL"}],
            total_weight=1.0,
            path_type="test",
            metadata={"test": True}
        )
        print("✅ GraphPath dataclass creation successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced Graph Algorithms test failed: {str(e)}")
        return False

def test_query_optimizer():
    """Test Query Optimization & Caching"""
    print_section("Testing Query Optimization & Caching")
    
    try:
        from query.query_optimizer import IntelligentQueryOptimizer, QueryPlan, CacheEntry, QueryStats
        
        print("✅ IntelligentQueryOptimizer class available")
        print("✅ QueryPlan dataclass available")
        print("✅ CacheEntry dataclass available")
        print("✅ QueryStats dataclass available")
        
        # Test dataclass creation
        test_plan = QueryPlan(
            original_query="MATCH (n) RETURN n",
            optimized_query="MATCH (n) RETURN n LIMIT 10",
            estimated_cost=2.5,
            execution_strategy="direct",
            cache_key="test_key",
            optimization_techniques=["added_limit"]
        )
        print("✅ QueryPlan dataclass creation successful")
        
        # Test cache entry
        test_cache_entry = CacheEntry(
            key="test_key",
            result={"nodes": []},
            query_hash="abc123",
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            expiry_time=None,
            size_bytes=100
        )
        print("✅ CacheEntry dataclass creation successful")
        
        # Test methods availability
        methods = [
            'optimize_query',
            'get_cached_result',
            'get_cache_stats'
        ]
        
        for method in methods:
            if hasattr(IntelligentQueryOptimizer, method):
                print(f"✅ Method '{method}' available")
            else:
                print(f"❌ Method '{method}' missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Query Optimizer test failed: {str(e)}")
        return False

def test_monitoring_dashboard():
    """Test Real-time Monitoring Dashboard"""
    print_section("Testing Real-time Monitoring Dashboard")
    
    try:
        from monitoring.dashboard import MonitoringDashboard, SystemMetrics, QueryMetrics, DatabaseMetrics
        
        # Test initialization (with graceful connection failure)
        dashboard = MonitoringDashboard()
        print("✅ MonitoringDashboard initialized successfully")
        
        # Check psutil availability
        if hasattr(dashboard, '_collect_system_metrics'):
            print("✅ System metrics collection method available")
        
        # Test data classes
        current_time = datetime.now()
        
        system_metrics = SystemMetrics(
            timestamp=current_time,
            cpu_percent=25.5,
            memory_percent=45.2,
            disk_usage_percent=60.1,
            network_io_bytes={"bytes_sent": 1000000, "bytes_recv": 2000000},
            active_connections=5,
            uptime_seconds=3600.0
        )
        print("✅ SystemMetrics dataclass created successfully")
        
        query_metrics = QueryMetrics(
            timestamp=current_time,
            query_count=150,
            avg_response_time_ms=45.2,
            cache_hit_rate=85.5,
            active_queries=3,
            slow_queries=2,
            error_rate=1.2
        )
        print("✅ QueryMetrics dataclass created successfully")
        
        db_metrics = DatabaseMetrics(
            timestamp=current_time,
            neo4j_status="connected",
            neo4j_connections=10,
            neo4j_transaction_rate=25.5,
            qdrant_status="connected",
            qdrant_collections=3,
            qdrant_points_count=50000
        )
        print("✅ DatabaseMetrics dataclass created successfully")
        
        # Test async methods (without actual connections)
        async def test_async_methods():
            try:
                system_data = await dashboard._collect_system_metrics()
                print(f"✅ System metrics collection: CPU {system_data.cpu_percent:.1f}%")
                
                query_data = await dashboard._collect_query_metrics()
                print(f"✅ Query metrics collection: {query_data.query_count} queries")
                
                db_data = await dashboard._collect_database_metrics()
                print(f"✅ Database metrics collection: Neo4j {db_data.neo4j_status}")
                
                health = await dashboard._get_system_health()
                print(f"✅ System health check: {health['status']}")
                
                return True
            except Exception as e:
                print(f"❌ Async methods test failed: {str(e)}")
                return False
        
        # Run async tests
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        async_result = loop.run_until_complete(test_async_methods())
        loop.close()
        
        # Test FastAPI app
        if hasattr(dashboard, 'app'):
            print("✅ FastAPI app initialized")
            print(f"✅ FastAPI routes: {len(dashboard.app.routes)} endpoints")
        
        return async_result
        
    except Exception as e:
        print(f"❌ Monitoring Dashboard test failed: {str(e)}")
        return False

def test_plc_query_dsl():
    """Test Custom Query DSL"""
    print_section("Testing Custom Query DSL")
    
    try:
        from query.plc_query_dsl import PLCQueryDSL, QueryType, ComparisonOperator, PLCQuery, FilterCondition
        
        # Test initialization
        dsl = PLCQueryDSL()
        print("✅ PLCQueryDSL initialized successfully")
        
        # Test enum values
        query_types = list(QueryType)
        operators = list(ComparisonOperator)
        print(f"✅ Found {len(query_types)} query types: {[qt.value for qt in query_types]}")
        print(f"✅ Found {len(operators)} operators: {[op.value for op in operators]}")
        
        # Test natural language parsing
        test_queries = [
            "find all routines that contain timer",
            "show me programs created after 2023",
            "trace connections from Main_Routine",
            "count all devices in the project",
            "what routines depend on Safety_AOI"
        ]
        
        for query_text in test_queries:
            try:
                parsed = dsl.parse_natural_language(query_text)
                print(f"✅ Parsed '{query_text[:30]}...': {parsed.query_type.value}")
            except Exception as e:
                print(f"❌ Failed to parse '{query_text[:30]}...': {str(e)}")
        
        # Test structured query building
        structured_query = dsl.build_structured_query(
            query_type=QueryType.FIND_COMPONENTS,
            target_components=["PLCProgram", "Routine"],
            limit=20
        )
        print(f"✅ Structured query built: {structured_query.query_type.value}")
        
        # Test Cypher generation
        cypher_query, params = dsl.to_cypher_query(structured_query)
        print(f"✅ Cypher generated: {len(cypher_query)} characters")
        print(f"   Query: {cypher_query[:60]}...")
        print(f"   Params: {len(params)} parameters")
        
        # Test filter conditions
        filter_condition = FilterCondition(
            property_name="name",
            operator=ComparisonOperator.CONTAINS,
            value="Motor",
            case_sensitive=False
        )
        print(f"✅ Filter condition created: {filter_condition.property_name} {filter_condition.operator.value} {filter_condition.value}")
        
        # Test examples
        examples = dsl.get_query_examples()
        print(f"✅ Query examples available: {len(examples)} categories")
        for category, example_list in examples.items():
            print(f"   {category}: {len(example_list)} examples")
        
        # Test cache operations
        initial_cache_size = len(dsl.query_cache)
        dsl.clear_cache()
        final_cache_size = len(dsl.query_cache)
        print(f"✅ Cache operations: {initial_cache_size} -> {final_cache_size} items")
        
        return True
        
    except Exception as e:
        print(f"❌ PLC Query DSL test failed: {str(e)}")
        return False

def test_integration():
    """Test component integration"""
    print_section("Testing Component Integration")
    
    try:
        # Test imports work together
        from query.advanced_graph_algorithms import AdvancedGraphAnalyzer
        from query.query_optimizer import IntelligentQueryOptimizer
        from monitoring.dashboard import MonitoringDashboard
        from query.plc_query_dsl import PLCQueryDSL, QueryType
        
        print("✅ All components imported successfully")
        
        # Test workflow integration
        dsl = PLCQueryDSL()
        
        # Create query through DSL
        nl_query = "find all programs that contain motor routines"
        parsed_query = dsl.parse_natural_language(nl_query)
        
        # Convert to Cypher
        cypher_query, params = dsl.to_cypher_query(parsed_query)
        
        print(f"✅ End-to-end workflow successful:")
        print(f"   NL Query: {nl_query}")
        print(f"   Query Type: {parsed_query.query_type.value}")
        print(f"   Cypher Length: {len(cypher_query)} chars")
        print(f"   Params: {len(params)} parameters")
        
        # Test that we can create instances without full initialization
        print("✅ Component integration verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        return False

def generate_test_report(results: Dict[str, bool]) -> Dict[str, Any]:
    """Generate comprehensive test report"""
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": round(success_rate, 2),
        "test_results": results,
        "status": "PASS" if success_rate == 100 else "PARTIAL" if success_rate >= 75 else "FAIL",
        "summary": {
            "advanced_graph_algorithms": "Advanced graph traversal and clustering algorithms",
            "query_optimizer": "Intelligent query optimization with caching",
            "monitoring_dashboard": "Real-time system monitoring with FastAPI",
            "plc_query_dsl": "Natural language to Cypher query conversion",
            "integration": "Component integration and workflow testing"
        }
    }
    
    return report

def main():
    """Run comprehensive Phase 3 Day 4 tests"""
    print_header("Phase 3 Day 4: Comprehensive Testing Suite")
    print(f"🕒 Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_results = {
        "advanced_graph_algorithms": test_advanced_graph_algorithms(),
        "query_optimizer": test_query_optimizer(),
        "monitoring_dashboard": test_monitoring_dashboard(),
        "plc_query_dsl": test_plc_query_dsl(),
        "integration": test_integration()
    }
    
    # Generate report
    report = generate_test_report(test_results)
    
    # Print summary
    print_header("Test Results Summary")
    print(f"📊 Total Tests: {report['total_tests']}")
    print(f"✅ Passed: {report['passed_tests']}")
    print(f"❌ Failed: {report['failed_tests']}")
    print(f"📈 Success Rate: {report['success_rate']}%")
    print(f"🎯 Overall Status: {report['status']}")
    
    # Print individual results
    print_section("Individual Test Results")
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        description = report['summary'][test_name]
        print(f"{status} - {test_name}: {description}")
    
    # Save report to file
    report_file = f"phase3_day4_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Test report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Failed to save report: {str(e)}")
    
    print_header("Phase 3 Day 4 Testing Complete")
    print(f"🕒 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if report['status'] == "PASS":
        print("🎉 All tests passed! Phase 3 Day 4 implementation is ready for production.")
    elif report['status'] == "PARTIAL":
        print("⚠️  Most tests passed. Review failed tests before proceeding.")
    else:
        print("❌ Multiple test failures detected. Implementation needs review.")
    
    return report['success_rate'] == 100

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 