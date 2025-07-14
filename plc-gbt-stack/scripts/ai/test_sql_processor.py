#!/usr/bin/env python3
"""
🧪 SQL File Processor Test Script

Following AI Task Orchestrator Guide methodology to test the newly implemented
SQLFileProcessor with the 20 failed SQL backup files.

Author: AI Task Orchestrator
Created: 2025-01-17
Purpose: Validate SQLFileProcessor functionality and measure processing success
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

from database_manager import DatabaseManager, DatabaseType
from file_processors import FileProcessorOrchestrator, SQLFileProcessor
from codebase_analyzer import CodebaseAnalyzer, AnalysisDepth, FileType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLProcessorTester:
    """Test framework for SQLFileProcessor"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.orchestrator = FileProcessorOrchestrator(self.db_manager)
        self.analyzer = CodebaseAnalyzer("/Users/reh3376/repos/plc-gbt")
        self.test_results = []
        
    def find_sql_files(self, root_dir: str = "/Users/reh3376/repos/plc-gbt") -> List[Path]:
        """Find all SQL files in the project"""
        sql_files = []
        for sql_file in Path(root_dir).rglob("*.sql"):
            if sql_file.is_file():
                sql_files.append(sql_file)
        return sql_files
    
    def test_single_sql_file(self, sql_file: Path) -> Dict[str, Any]:
        """Test processing of a single SQL file"""
        test_start = time.time()
        
        try:
            # Analyze the file
            analysis_result = self.analyzer.analyze_single_file(sql_file)
            
            # Verify file type detection
            if analysis_result.file_metadata.file_type != FileType.SQL:
                return {
                    "file_path": str(sql_file),
                    "success": False,
                    "error": f"File type detected as {analysis_result.file_metadata.file_type}, expected SQL",
                    "duration": time.time() - test_start
                }
            
            # Process the file
            processed_content = self.orchestrator.process_file(analysis_result)
            
            if processed_content is None:
                return {
                    "file_path": str(sql_file),
                    "success": False,
                    "error": "Processing returned None",
                    "duration": time.time() - test_start
                }
            
            # Validate processed content
            validation_result = self.validate_processed_content(processed_content, sql_file)
            
            return {
                "file_path": str(sql_file),
                "success": True,
                "file_size": sql_file.stat().st_size,
                "chunks_count": len(processed_content.content_chunks),
                "embeddings_count": len(processed_content.embeddings),
                "database_routing": [tier.name for tier in processed_content.database_routing.keys()],
                "validation": validation_result,
                "duration": time.time() - test_start
            }
            
        except Exception as e:
            return {
                "file_path": str(sql_file),
                "success": False,
                "error": str(e),
                "duration": time.time() - test_start
            }
    
    def validate_processed_content(self, processed_content, sql_file: Path) -> Dict[str, Any]:
        """Validate the processed content structure"""
        validation = {
            "has_chunks": len(processed_content.content_chunks) > 0,
            "has_embeddings": len(processed_content.embeddings) > 0,
            "has_metadata": bool(processed_content.metadata),
            "has_database_routing": bool(processed_content.database_routing),
            "chunk_types": []
        }
        
        # Check chunk types
        for chunk in processed_content.content_chunks:
            if 'type' in chunk:
                validation["chunk_types"].append(chunk['type'])
        
        # Check database routing
        expected_tiers = ['LONG_TERM', 'MEDIUM_TERM', 'PATTERN_MATCHING']
        validation["database_routing_complete"] = all(
            tier in [t.name for t in processed_content.database_routing.keys()]
            for tier in expected_tiers
        )
        
        return validation
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test on all SQL files"""
        print("🧪 SQL File Processor Comprehensive Test")
        print("=" * 50)
        
        test_session = {
            "session_id": f"sql_processor_test_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "test_results": [],
            "summary": {}
        }
        
        # Find all SQL files
        sql_files = self.find_sql_files()
        print(f"📁 Found {len(sql_files)} SQL files to test")
        
        # Test each file
        successful_tests = 0
        failed_tests = 0
        total_duration = 0
        
        for i, sql_file in enumerate(sql_files, 1):
            print(f"\n🔍 Testing {i}/{len(sql_files)}: {sql_file.name}")
            
            result = self.test_single_sql_file(sql_file)
            test_session["test_results"].append(result)
            
            if result["success"]:
                successful_tests += 1
                print(f"   ✅ SUCCESS - {result['chunks_count']} chunks, {result['embeddings_count']} embeddings")
            else:
                failed_tests += 1
                print(f"   ❌ FAILED - {result['error']}")
            
            total_duration += result["duration"]
        
        # Calculate summary
        test_session["summary"] = {
            "total_files": len(sql_files),
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests / len(sql_files)) * 100 if sql_files else 0,
            "total_duration": total_duration,
            "average_duration": total_duration / len(sql_files) if sql_files else 0,
            "end_time": datetime.now().isoformat()
        }
        
        return test_session
    
    def generate_test_report(self, test_session: Dict[str, Any]) -> str:
        """Generate a detailed test report"""
        summary = test_session["summary"]
        
        report = f"""
# 🧪 SQL File Processor Test Report

**Test Session**: {test_session["session_id"]}  
**Start Time**: {test_session["start_time"]}  
**End Time**: {summary["end_time"]}  
**Duration**: {summary["total_duration"]:.2f} seconds  

## 📊 Test Results Summary

- **Total Files Tested**: {summary["total_files"]}
- **Successful Tests**: {summary["successful_tests"]}
- **Failed Tests**: {summary["failed_tests"]}
- **Success Rate**: {summary["success_rate"]:.1f}%
- **Average Processing Time**: {summary["average_duration"]:.3f} seconds per file

## 📋 Detailed Results

"""
        
        # Add detailed results
        for result in test_session["test_results"]:
            status = "✅ SUCCESS" if result["success"] else "❌ FAILED"
            report += f"### {Path(result['file_path']).name} - {status}\n"
            
            if result["success"]:
                report += f"- **File Size**: {result['file_size']} bytes\n"
                report += f"- **Chunks**: {result['chunks_count']}\n"
                report += f"- **Embeddings**: {result['embeddings_count']}\n"
                report += f"- **Database Routing**: {', '.join(result['database_routing'])}\n"
                report += f"- **Duration**: {result['duration']:.3f}s\n"
                
                validation = result["validation"]
                report += f"- **Validation**: "
                report += f"Chunks: {'✅' if validation['has_chunks'] else '❌'}, "
                report += f"Embeddings: {'✅' if validation['has_embeddings'] else '❌'}, "
                report += f"Routing: {'✅' if validation['database_routing_complete'] else '❌'}\n"
                
                if validation["chunk_types"]:
                    report += f"- **Chunk Types**: {', '.join(validation['chunk_types'])}\n"
            else:
                report += f"- **Error**: {result['error']}\n"
                report += f"- **Duration**: {result['duration']:.3f}s\n"
            
            report += "\n"
        
        return report

def main():
    """Main test execution"""
    tester = SQLProcessorTester()
    
    # Run comprehensive test
    test_session = tester.run_comprehensive_test()
    
    # Generate report
    report = tester.generate_test_report(test_session)
    
    # Save results
    results_file = f"sql_processor_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(test_session, f, indent=2)
    
    report_file = f"sql_processor_test_report_{int(time.time())}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    # Print summary
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY")
    print("=" * 50)
    
    summary = test_session["summary"]
    print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
    print(f"📁 Files Tested: {summary['total_files']}")
    print(f"✅ Successful: {summary['successful_tests']}")
    print(f"❌ Failed: {summary['failed_tests']}")
    print(f"⏱️  Total Duration: {summary['total_duration']:.2f}s")
    print(f"📄 Results saved to: {results_file}")
    print(f"📋 Report saved to: {report_file}")
    
    # Return success if all tests passed
    return summary['failed_tests'] == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 