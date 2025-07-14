#!/usr/bin/env python3
"""
🧪 Fixed Backup CLI Testing Framework - Path Resolution Corrected
================================================================

AI Task Orchestrator Implementation with corrected path handling to achieve 100% Syntax Validation

This framework correctly handles file paths to eliminate the path duplication bug that caused
66.7% Syntax Validation score, targeting 100% validation achievement.

Author: AI Task Orchestrator  
Created: July 14, 2025
Version: 1.1.0 - Fixed Path Resolution
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
import logging

# Setup comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    cli_name: str
    command: str
    success: bool
    duration_seconds: float
    output: str
    error_message: Optional[str] = None
    exit_code: Optional[int] = None

@dataclass
class CLITestSuite:
    """CLI test suite configuration"""
    name: str
    file_path: str
    working_directory: str
    available: bool
    test_results: List[TestResult]

class FixedBackupCLITester:
    """Fixed testing framework with corrected path resolution"""
    
    def __init__(self):
        self.session_id = f"backup_cli_testing_fixed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.test_results = []
        self.cli_suites = []
        self.start_time = datetime.now()
        
        # Define CLI implementations with CORRECTED path handling
        self.cli_implementations = [
            {
                'name': 'plc_backup_cli_final',
                'file_path': 'plc_backup_cli_final.py',  # Just filename when in working dir
                'full_path': 'plc-gbt-stack/scripts/ai/plc_backup_cli_final.py',  # Full path from root
                'working_directory': 'plc-gbt-stack/scripts/ai',
                'features': ['backup', 'list', 'status']
            },
            {
                'name': 'plc_memory_cli', 
                'file_path': 'plc_memory_cli.py',  # Just filename when in working dir
                'full_path': 'plc-gbt-stack/scripts/ai/plc_memory_cli.py',  # Full path from root
                'working_directory': 'plc-gbt-stack/scripts/ai',
                'features': ['backup']
            },
            {
                'name': 'backup_cli_complete',
                'file_path': 'backup_cli_complete.py',
                'full_path': 'backup_cli_complete.py',
                'working_directory': '.',
                'features': ['backup', 'list', 'status', 'cleanup', 'validate']
            },
            {
                'name': 'plc_backup_cli',
                'file_path': 'plc_backup_cli.py', 
                'full_path': 'plc_backup_cli.py',
                'working_directory': '.',
                'features': ['backup', 'list', 'status', 'cleanup', 'validate']
            },
            {
                'name': 'enhanced_backup_cli',
                'file_path': 'enhanced_backup_cli.py',
                'full_path': 'enhanced_backup_cli.py',
                'working_directory': '.',
                'features': ['backup', 'list', 'status']
            },
            {
                'name': 'enterprise_backup_cli',
                'file_path': 'enterprise_backup_cli.py',
                'full_path': 'enterprise_backup_cli.py',
                'working_directory': '.',
                'features': ['backup', 'list', 'status', 'cleanup', 'validate']
            }
        ]
        
        print(f"🚀 Initializing FIXED Backup CLI Testing Framework")
        print(f"🆔 Session ID: {self.session_id}")
        print(f"📅 Start Time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 PATH RESOLUTION: Fixed duplication bug")
        print(f"🧪 Testing {len(self.cli_implementations)} CLI implementations")
        print("="*70)
    
    def run_command_fixed(self, command: str, working_dir: str = ".", timeout: int = 30) -> TestResult:
        """Execute a command with FIXED path resolution"""
        start_time = time.time()
        
        try:
            # Save original directory
            original_dir = os.getcwd()
            
            # Change to working directory if needed
            if working_dir != ".":
                target_dir = os.path.join(original_dir, working_dir)
                if os.path.exists(target_dir):
                    os.chdir(target_dir)
                else:
                    raise FileNotFoundError(f"Working directory not found: {target_dir}")
            
            # Execute command
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=None  # Use current directory (already changed above)
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            return TestResult(
                test_name="command_execution",
                cli_name="unknown",
                command=command,
                success=success,
                duration_seconds=duration,
                output=result.stdout,
                error_message=result.stderr if not success else None,
                exit_code=result.returncode
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name="command_execution",
                cli_name="unknown", 
                command=command,
                success=False,
                duration_seconds=timeout,
                output="",
                error_message="Command timeout",
                exit_code=-1
            )
        except Exception as e:
            return TestResult(
                test_name="command_execution",
                cli_name="unknown",
                command=command,
                success=False,
                duration_seconds=time.time() - start_time,
                output="",
                error_message=str(e),
                exit_code=-2
            )
        finally:
            # Always restore original directory
            os.chdir(original_dir)
    
    def test_cli_availability(self, cli_config: Dict) -> bool:
        """Test if CLI file exists using corrected path"""
        # Use full_path for availability check from root directory
        file_path = Path(cli_config['full_path'])
        return file_path.exists() and file_path.is_file()
    
    def test_help_command(self, cli_config: Dict) -> TestResult:
        """Test CLI help functionality with corrected path"""
        # Use file_path (just filename) when running in working directory
        command = f"python3 {cli_config['file_path']} --help"
        result = self.run_command_fixed(command, cli_config['working_directory'])
        result.test_name = "help_command"
        result.cli_name = cli_config['name']
        return result
    
    def test_status_command(self, cli_config: Dict) -> Optional[TestResult]:
        """Test CLI status functionality if available"""
        if 'status' not in cli_config['features']:
            return None
            
        command = f"python3 {cli_config['file_path']} status"
        result = self.run_command_fixed(command, cli_config['working_directory'])
        result.test_name = "status_command"
        result.cli_name = cli_config['name']
        return result
    
    def test_backup_redis(self, cli_config: Dict) -> Optional[TestResult]:
        """Test Redis backup functionality"""
        if 'backup' not in cli_config['features']:
            return None
        
        # Determine backup command format
        if cli_config['name'] == 'plc_memory_cli':
            command = f"python3 {cli_config['file_path']} backup -d redis"
        else:
            command = f"python3 {cli_config['file_path']} backup redis"
            
        result = self.run_command_fixed(command, cli_config['working_directory'])
        result.test_name = "backup_redis"
        result.cli_name = cli_config['name']
        return result
    
    def test_list_command(self, cli_config: Dict) -> Optional[TestResult]:
        """Test backup listing functionality if available"""
        if 'list' not in cli_config['features']:
            return None
            
        command = f"python3 {cli_config['file_path']} list"
        result = self.run_command_fixed(command, cli_config['working_directory'])
        result.test_name = "list_command"
        result.cli_name = cli_config['name']
        return result
    
    def run_comprehensive_test_suite(self):
        """Execute comprehensive testing with FIXED path resolution"""
        print("\n🔧 Starting FIXED Comprehensive CLI Test Suite")
        print("="*70)
        
        for cli_config in self.cli_implementations:
            print(f"\n📋 Testing CLI: {cli_config['name']}")
            print(f"📁 File: {cli_config['file_path']}")
            print(f"📂 Working Dir: {cli_config['working_directory']}")
            print(f"🔍 Full Path: {cli_config['full_path']}")
            print("-"*50)
            
            # Test availability using full path
            available = self.test_cli_availability(cli_config)
            if not available:
                print(f"❌ CLI file not found: {cli_config['full_path']}")
                continue
            else:
                print(f"✅ CLI file available: {cli_config['full_path']}")
            
            # Create test suite
            test_suite = CLITestSuite(
                name=cli_config['name'],
                file_path=cli_config['file_path'],
                working_directory=cli_config['working_directory'],
                available=available,
                test_results=[]
            )
            
            # Test help command
            print("  🔍 Testing help command...")
            help_result = self.test_help_command(cli_config)
            test_suite.test_results.append(help_result)
            self.test_results.append(help_result)
            print(f"    {'✅' if help_result.success else '❌'} Help: {help_result.duration_seconds:.2f}s")
            if not help_result.success:
                print(f"    Error: {help_result.error_message}")
            
            # Test status command
            if 'status' in cli_config['features']:
                print("  📊 Testing status command...")
                status_result = self.test_status_command(cli_config)
                if status_result:
                    test_suite.test_results.append(status_result)
                    self.test_results.append(status_result)
                    print(f"    {'✅' if status_result.success else '❌'} Status: {status_result.duration_seconds:.2f}s")
                    if not status_result.success:
                        print(f"    Error: {status_result.error_message}")
            
            # Test Redis backup
            print("  🔴 Testing Redis backup...")
            redis_result = self.test_backup_redis(cli_config)
            if redis_result:
                test_suite.test_results.append(redis_result)
                self.test_results.append(redis_result)
                print(f"    {'✅' if redis_result.success else '❌'} Redis Backup: {redis_result.duration_seconds:.2f}s")
                if not redis_result.success:
                    print(f"    Error: {redis_result.error_message}")
            
            # Test list command
            if 'list' in cli_config['features']:
                print("  📋 Testing list command...")
                list_result = self.test_list_command(cli_config)
                if list_result:
                    test_suite.test_results.append(list_result)
                    self.test_results.append(list_result)
                    print(f"    {'✅' if list_result.success else '❌'} List: {list_result.duration_seconds:.2f}s")
                    if not list_result.success:
                        print(f"    Error: {list_result.error_message}")
            
            self.cli_suites.append(test_suite)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive testing report"""
        end_time = datetime.now()
        total_duration = (end_time - self.start_time).total_seconds()
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result.success)
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Group results by CLI
        cli_results = {}
        for result in self.test_results:
            if result.cli_name not in cli_results:
                cli_results[result.cli_name] = []
            cli_results[result.cli_name].append(result)
        
        # Generate report
        report = {
            'session_info': {
                'session_id': self.session_id,
                'start_time': self.start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'total_duration_seconds': total_duration,
                'framework_version': '1.1.0',
                'fixes_applied': ['path_resolution_correction', 'subprocess_import_verified']
            },
            'test_summary': {
                'total_cli_implementations': len(self.cli_implementations),
                'available_clis': sum(1 for suite in self.cli_suites if suite.available),
                'total_tests_executed': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate_percent': success_rate
            },
            'cli_results': {},
            'detailed_results': []
        }
        
        # Add CLI-specific results
        for cli_name, results in cli_results.items():
            cli_success = sum(1 for r in results if r.success)
            cli_total = len(results)
            cli_success_rate = (cli_success / cli_total * 100) if cli_total > 0 else 0
            
            report['cli_results'][cli_name] = {
                'total_tests': cli_total,
                'successful_tests': cli_success,
                'failed_tests': cli_total - cli_success,
                'success_rate_percent': cli_success_rate,
                'avg_duration_seconds': sum(r.duration_seconds for r in results) / cli_total if cli_total > 0 else 0
            }
        
        # Add detailed results
        for result in self.test_results:
            report['detailed_results'].append(asdict(result))
        
        return report
    
    def save_results(self, report: Dict):
        """Save test results to JSON file"""
        results_file = f"backup_cli_testing_results_fixed_{self.session_id}.json"
        
        with open(results_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Fixed test results saved: {results_file}")
        return results_file
    
    def print_final_summary(self, report: Dict):
        """Print comprehensive final summary"""
        print("\n" + "="*70)
        print("📊 FIXED BACKUP CLI TESTING COMPLETE")
        print("="*70)
        
        summary = report['test_summary']
        session = report['session_info']
        
        print(f"🎯 Session ID: {session['session_id']}")
        print(f"⏱️  Total Duration: {session['total_duration_seconds']:.2f} seconds")
        print(f"🔧 Framework Version: {session['framework_version']} (FIXED)")
        print(f"🧪 CLI Implementations: {summary['total_cli_implementations']}")
        print(f"✅ Available CLIs: {summary['available_clis']}")
        print(f"🔬 Total Tests: {summary['total_tests_executed']}")
        print(f"✅ Successful: {summary['successful_tests']}")
        print(f"❌ Failed: {summary['failed_tests']}")
        print(f"📊 Success Rate: {summary['success_rate_percent']:.1f}%")
        
        print(f"\n📋 CLI Implementation Results:")
        for cli_name, results in report['cli_results'].items():
            status = "✅" if results['success_rate_percent'] >= 75 else "⚠️" if results['success_rate_percent'] >= 50 else "❌"
            print(f"  {status} {cli_name}: {results['success_rate_percent']:.1f}% ({results['successful_tests']}/{results['total_tests']} tests)")
            
        print(f"\n🎉 FIXED testing framework execution complete!")

def main():
    """Main testing execution with FIXED path resolution"""
    try:
        # Initialize FIXED testing framework
        tester = FixedBackupCLITester()
        
        # Execute comprehensive test suite
        tester.run_comprehensive_test_suite()
        
        # Generate comprehensive report
        report = tester.generate_comprehensive_report()
        
        # Save results
        results_file = tester.save_results(report)
        
        # Print final summary
        tester.print_final_summary(report)
        
        return report
        
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        return None
    except Exception as e:
        print(f"💥 Testing framework error: {e}")
        return None

if __name__ == "__main__":
    main() 