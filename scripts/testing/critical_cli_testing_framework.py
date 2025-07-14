#!/usr/bin/env python3
"""
🚨 Critical CLI Testing Framework
=================================

AI Task Orchestrator Implementation for Testing Critical Missing CLI Commands

Focused testing of high-priority CLI commands identified through gap analysis:
- System health and status monitoring commands
- Database backup validation commands  
- Core database backup coverage (Neo4j, PostgreSQL, Qdrant)
- Essential maintenance and utility commands

Based on gap analysis showing only 10.3% coverage (6/58 commands tested).

Author: AI Task Orchestrator
Created: July 14, 2025
Version: 1.0.0 - Critical Gap Resolution
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class CriticalTestResult:
    """Result container for critical CLI command tests"""
    test_name: str
    cli_name: str
    command: str
    success: bool
    duration_seconds: float
    output: str
    error_message: Optional[str]
    exit_code: int
    priority_level: str  # CRITICAL, HIGH, MEDIUM


class CriticalCLITester:
    """Focused tester for critical CLI commands identified in gap analysis"""
    
    def __init__(self):
        self.session_id = f"critical_cli_testing_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.now()
        self.results = []
        self.working_directory = Path.cwd()
        
        print("🚨 Starting Critical CLI Testing Framework")
        print("=" * 60)
        print(f"🆔 Session ID: {self.session_id}")
        print(f"📁 Working Directory: {self.working_directory}")
        print(f"⏰ Start Time: {self.start_time}")
        print()
    
    def run_command(self, command: str, working_dir: Path, timeout: int = 30, priority: str = "HIGH") -> CriticalTestResult:
        """Execute CLI command with comprehensive error handling"""
        start_time = time.time()
        
        try:
            # Change to appropriate directory
            original_dir = Path.cwd()
            os.chdir(working_dir)
            
            print(f"  🔧 Executing: {command}")
            
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            
            test_result = CriticalTestResult(
                test_name="",  # Will be set by caller
                cli_name="",   # Will be set by caller
                command=command,
                success=result.returncode == 0,
                duration_seconds=duration,
                output=result.stdout,
                error_message=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode,
                priority_level=priority
            )
            
            status = "✅ SUCCESS" if test_result.success else "❌ FAILED"
            print(f"  {status} - {duration:.2f}s - Exit: {result.returncode}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"  ⏰ TIMEOUT - {duration:.2f}s")
            return CriticalTestResult(
                test_name="", cli_name="", command=command,
                success=False, duration_seconds=duration,
                output="", error_message=f"Command timed out after {timeout}s",
                exit_code=-1, priority_level=priority
            )
        except Exception as e:
            duration = time.time() - start_time
            print(f"  💥 ERROR - {duration:.2f}s - {str(e)}")
            return CriticalTestResult(
                test_name="", cli_name="", command=command,
                success=False, duration_seconds=duration,
                output="", error_message=str(e),
                exit_code=-2, priority_level=priority
            )
        finally:
            os.chdir(original_dir)
    
    def test_critical_status_commands(self):
        """Test critical status and health monitoring commands"""
        print("🚨 TESTING CRITICAL STATUS COMMANDS")
        print("-" * 40)
        
        critical_tests = [
            {
                'cli': 'plc_memory_cli',
                'path': 'plc-gbt-stack/scripts/ai/plc_memory_cli.py',
                'command': 'python3 plc_memory_cli.py status',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'CRITICAL'
            },
            {
                'cli': 'plc_memory_cli',
                'path': 'plc-gbt-stack/scripts/ai/plc_memory_cli.py',
                'command': 'python3 plc_memory_cli.py health',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'CRITICAL'
            },
            {
                'cli': 'backup_cli_complete',
                'path': 'backup_cli_complete.py',
                'command': 'python3 backup_cli_complete.py validate --help',  # Test help first
                'working_dir': self.working_directory,
                'priority': 'HIGH'
            }
        ]
        
        for test_config in critical_tests:
            print(f"\n🔍 Testing {test_config['cli']} - {test_config['command']}")
            
            result = self.run_command(
                test_config['command'],
                test_config['working_dir'],
                timeout=30,
                priority=test_config['priority']
            )
            
            result.test_name = f"critical_{test_config['cli']}_status"
            result.cli_name = test_config['cli']
            self.results.append(result)
    
    def test_database_backup_coverage(self):
        """Test missing database backup functionality"""
        print("\n💾 TESTING DATABASE BACKUP COVERAGE")
        print("-" * 40)
        
        database_tests = [
            {
                'cli': 'plc_memory_cli',
                'command': 'python3 plc_memory_cli.py backup -d neo4j',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'HIGH'
            },
            {
                'cli': 'plc_memory_cli',
                'command': 'python3 plc_memory_cli.py backup -d postgresql',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'HIGH'
            },
            {
                'cli': 'plc_backup_cli_final',
                'command': 'python3 plc_backup_cli_final.py backup neo4j',
                'working_dir': self.working_directory,
                'priority': 'HIGH'
            },
            {
                'cli': 'plc_backup_cli_final',
                'command': 'python3 plc_backup_cli_final.py backup all',
                'working_dir': self.working_directory,
                'priority': 'HIGH'
            }
        ]
        
        for test_config in database_tests:
            print(f"\n💾 Testing {test_config['cli']} - Database Backup")
            
            result = self.run_command(
                test_config['command'],
                test_config['working_dir'],
                timeout=60,  # Longer timeout for backups
                priority=test_config['priority']
            )
            
            result.test_name = f"database_backup_{test_config['cli']}"
            result.cli_name = test_config['cli']
            self.results.append(result)
    
    def test_advanced_features(self):
        """Test advanced CLI features identified as gaps"""
        print("\n🔧 TESTING ADVANCED FEATURES")
        print("-" * 40)
        
        advanced_tests = [
            {
                'cli': 'plc_memory_cli',
                'command': 'python3 plc_memory_cli.py version',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'MEDIUM'
            },
            {
                'cli': 'plc_memory_cli',
                'command': 'python3 plc_memory_cli.py neo4j --help',
                'working_dir': self.working_directory / 'plc-gbt-stack' / 'scripts' / 'ai',
                'priority': 'MEDIUM'
            },
            {
                'cli': 'plc_backup_cli',
                'command': 'python3 plc_backup_cli.py cleanup --help',
                'working_dir': self.working_directory,
                'priority': 'MEDIUM'
            }
        ]
        
        for test_config in advanced_tests:
            print(f"\n🔧 Testing {test_config['cli']} - Advanced Feature")
            
            result = self.run_command(
                test_config['command'],
                test_config['working_dir'],
                timeout=30,
                priority=test_config['priority']
            )
            
            result.test_name = f"advanced_{test_config['cli']}"
            result.cli_name = test_config['cli']
            self.results.append(result)
    
    def generate_critical_test_report(self):
        """Generate comprehensive report on critical command testing"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate metrics by priority
        priority_metrics = {'CRITICAL': {'total': 0, 'passed': 0}, 
                          'HIGH': {'total': 0, 'passed': 0},
                          'MEDIUM': {'total': 0, 'passed': 0}}
        
        for result in self.results:
            priority_metrics[result.priority_level]['total'] += 1
            if result.success:
                priority_metrics[result.priority_level]['passed'] += 1
        
        # Overall metrics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate report
        report = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'framework_version': '1.0.0',
                'test_focus': 'critical_gap_resolution'
            },
            'test_summary': {
                'total_critical_tests': total_tests,
                'successful_tests': passed_tests,
                'failed_tests': total_tests - passed_tests,
                'overall_success_rate_percent': success_rate
            },
            'priority_breakdown': {
                'critical_commands': {
                    'total': priority_metrics['CRITICAL']['total'],
                    'passed': priority_metrics['CRITICAL']['passed'],
                    'success_rate': (priority_metrics['CRITICAL']['passed'] / 
                                   priority_metrics['CRITICAL']['total'] * 100) 
                                   if priority_metrics['CRITICAL']['total'] > 0 else 0
                },
                'high_priority': {
                    'total': priority_metrics['HIGH']['total'],
                    'passed': priority_metrics['HIGH']['passed'],
                    'success_rate': (priority_metrics['HIGH']['passed'] / 
                                   priority_metrics['HIGH']['total'] * 100) 
                                   if priority_metrics['HIGH']['total'] > 0 else 0
                },
                'medium_priority': {
                    'total': priority_metrics['MEDIUM']['total'],
                    'passed': priority_metrics['MEDIUM']['passed'],
                    'success_rate': (priority_metrics['MEDIUM']['passed'] / 
                                   priority_metrics['MEDIUM']['total'] * 100) 
                                   if priority_metrics['MEDIUM']['total'] > 0 else 0
                }
            },
            'detailed_results': [asdict(result) for result in self.results]
        }
        
        # Save report
        report_file = f"critical_cli_testing_results_{self.session_id}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🚨 CRITICAL CLI TESTING RESULTS")
        print("=" * 60)
        print(f"📊 Overall Success Rate: {success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print()
        
        print("📋 Priority Breakdown:")
        for priority, metrics in report['priority_breakdown'].items():
            if metrics['total'] > 0:
                print(f"  🚨 {priority.upper()}: {metrics['success_rate']:.1f}% ({metrics['passed']}/{metrics['total']})")
        
        print(f"\n📄 Detailed Report: {report_file}")
        
        # Critical assessment
        critical_success = priority_metrics['CRITICAL']['passed'] / priority_metrics['CRITICAL']['total'] * 100 if priority_metrics['CRITICAL']['total'] > 0 else 100
        
        if critical_success >= 90:
            print("\n✅ ASSESSMENT: Critical infrastructure commands operational")
        elif critical_success >= 70:
            print("\n⚠️ ASSESSMENT: Some critical commands failing - requires attention")
        else:
            print("\n❌ ASSESSMENT: Critical infrastructure commands failing - immediate action required")
        
        return report


def main():
    """Execute critical CLI command testing"""
    tester = CriticalCLITester()
    
    # Execute critical testing phases
    tester.test_critical_status_commands()
    tester.test_database_backup_coverage() 
    tester.test_advanced_features()
    
    # Generate comprehensive report
    report = tester.generate_critical_test_report()
    
    print("\n🎉 Critical CLI testing complete!")
    return report


if __name__ == "__main__":
    main() 