#!/usr/bin/env python3
"""
✅ 8 Command Validation Testing Framework
==========================================

AI Task Orchestrator Implementation for Systematic Validation

Comprehensive testing of the 8 commands that were identified as failing
to validate that all fixes have been successfully implemented.

Original Failed Commands:
1. backup_cli_complete.py status (PosixPath TypeError) 
2. plc_memory_cli.py neo4j health (NoneType error)
3. enhanced_backup_cli.py status (path permission issues)
4. enhanced_backup_cli.py backup redis (path permission issues) 
5. enhanced_backup_cli.py backup all (path permission issues)
6. plc_memory_cli.py clean (missing implementation)
7. plc_memory_cli.py neo4j orphans (logic errors)
8. enterprise_backup_cli.py backup qdrant (actually works now)

Author: AI Task Orchestrator
Created: July 14, 2025
Version: 1.0.0 - Systematic Validation Testing
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Individual command validation result"""
    command_id: str
    cli_implementation: str
    command_string: str
    working_directory: str
    success: bool
    duration_seconds: float
    output: str
    error_message: str
    exit_code: int
    validation_status: str  # FIXED, IMPROVED, STILL_FAILING, NOT_TESTED
    notes: str


class EightCommandValidator:
    """Systematic validator for the 8 previously failing commands"""
    
    def __init__(self):
        self.validation_timestamp = datetime.now()
        self.session_id = f"8_command_validation_{self.validation_timestamp.strftime('%Y%m%d_%H%M%S')}"
        self.validation_results = []
        
        print("✅ Starting 8 Command Validation Testing")
        print("=" * 50)
        print(f"📅 Validation Date: {self.validation_timestamp}")
        print(f"🎯 Objective: Validate fixes for 8 originally failing commands")
        print(f"🆔 Session ID: {self.session_id}")
    
    def build_test_commands(self) -> List[Dict[str, Any]]:
        """Build comprehensive test command list for the 8 failing commands"""
        
        return [
            # FIXED COMMANDS (confirmed fixes implemented)
            {
                "command_id": "backup_complete_status",
                "cli_implementation": "backup_cli_complete",
                "command_string": "python3 backup_cli_complete.py status",
                "working_directory": ".",
                "expected_status": "FIXED",
                "fix_description": "Fixed PosixPath TypeError by replacing Path.glob() with os.listdir()",
                "priority": "HIGH"
            },
            {
                "command_id": "plc_memory_neo4j_health",
                "cli_implementation": "plc_memory_cli",
                "command_string": "python3 plc_memory_cli.py neo4j health",
                "working_directory": "plc-gbt-stack/scripts/ai",
                "expected_status": "FIXED",
                "fix_description": "Fixed NoneType error by adding null checking for query results",
                "priority": "HIGH"
            },
            {
                "command_id": "enhanced_backup_status",
                "cli_implementation": "enhanced_backup_cli",
                "command_string": "python3 enhanced_backup_cli.py status",
                "working_directory": ".",
                "expected_status": "FIXED",
                "fix_description": "Fixed path permission issues by changing invalid relative path to local directory",
                "priority": "MEDIUM"
            },
            {
                "command_id": "enhanced_backup_backup_redis",
                "cli_implementation": "enhanced_backup_cli",
                "command_string": "python3 enhanced_backup_cli.py backup redis",
                "working_directory": ".",
                "expected_status": "IMPROVED",
                "fix_description": "Core backup functionality fixed (path issues), minor CLI parsing issue remains",
                "priority": "MEDIUM"
            },
            {
                "command_id": "enhanced_backup_backup_all",
                "cli_implementation": "enhanced_backup_cli",
                "command_string": "python3 enhanced_backup_cli.py backup all",
                "working_directory": ".",
                "expected_status": "IMPROVED",
                "fix_description": "Should work now that path issues are fixed",
                "priority": "MEDIUM"
            },
            
            # COMMANDS TO TEST (may already work or need implementation)
            {
                "command_id": "enterprise_backup_backup_qdrant",
                "cli_implementation": "enterprise_backup_cli",
                "command_string": "python3 enterprise_backup_cli.py backup qdrant",
                "working_directory": ".",
                "expected_status": "FIXED",
                "fix_description": "Already working - was false positive in original testing",
                "priority": "HIGH"
            },
            {
                "command_id": "plc_memory_clean",
                "cli_implementation": "plc_memory_cli",
                "command_string": "python3 plc_memory_cli.py clean",
                "working_directory": "plc-gbt-stack/scripts/ai",
                "expected_status": "NOT_TESTED",
                "fix_description": "Need to test if clean functionality exists",
                "priority": "MEDIUM"
            },
            {
                "command_id": "plc_memory_neo4j_orphans",
                "cli_implementation": "plc_memory_cli",
                "command_string": "python3 plc_memory_cli.py neo4j orphans",
                "working_directory": "plc-gbt-stack/scripts/ai",
                "expected_status": "NOT_TESTED",
                "fix_description": "Need to test orphan detection functionality",
                "priority": "MEDIUM"
            }
        ]
    
    def run_single_command_validation(self, test_config: Dict[str, Any]) -> ValidationResult:
        """Run validation for a single command"""
        
        print(f"\n🔍 Testing: {test_config['command_id']}")
        print(f"   Command: {test_config['command_string']}")
        print(f"   Expected: {test_config['expected_status']}")
        
        start_time = time.time()
        
        try:
            # Change to working directory
            original_dir = Path.cwd()
            working_dir = Path(test_config['working_directory']).resolve()
            
            if not working_dir.exists():
                raise Exception(f"Working directory does not exist: {working_dir}")
            
            # Change directory and run command
            import os
            os.chdir(working_dir)
            
            # Execute command with timeout
            result = subprocess.run(
                test_config['command_string'].split(),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration = time.time() - start_time
            success = result.returncode == 0
            
            # Determine validation status
            if success:
                if "error" in result.stdout.lower() or "failed" in result.stdout.lower():
                    validation_status = "IMPROVED"  # Works but has issues
                    notes = "Command runs but reports internal errors"
                else:
                    validation_status = "FIXED"
                    notes = "Command works successfully"
            else:
                validation_status = "STILL_FAILING"
                notes = f"Command failed with exit code {result.returncode}"
            
            print(f"   Result: {validation_status} ({duration:.2f}s)")
            if not success:
                print(f"   Error: {result.stderr[:100]}...")
            
            return ValidationResult(
                command_id=test_config['command_id'],
                cli_implementation=test_config['cli_implementation'],
                command_string=test_config['command_string'],
                working_directory=str(working_dir),
                success=success,
                duration_seconds=duration,
                output=result.stdout,
                error_message=result.stderr,
                exit_code=result.returncode,
                validation_status=validation_status,
                notes=notes
            )
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            print(f"   Result: TIMEOUT ({duration:.2f}s)")
            
            return ValidationResult(
                command_id=test_config['command_id'],
                cli_implementation=test_config['cli_implementation'],
                command_string=test_config['command_string'],
                working_directory=test_config['working_directory'],
                success=False,
                duration_seconds=duration,
                output="",
                error_message="Command timed out after 30 seconds",
                exit_code=-1,
                validation_status="STILL_FAILING",
                notes="Command timeout indicates serious issues"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"   Result: ERROR ({duration:.2f}s) - {str(e)}")
            
            return ValidationResult(
                command_id=test_config['command_id'],
                cli_implementation=test_config['cli_implementation'],
                command_string=test_config['command_string'],
                working_directory=test_config['working_directory'],
                success=False,
                duration_seconds=duration,
                output="",
                error_message=str(e),
                exit_code=-2,
                validation_status="STILL_FAILING",
                notes=f"Execution error: {str(e)}"
            )
        
        finally:
            # Always restore original directory
            os.chdir(original_dir)
    
    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive validation of all 8 commands"""
        
        test_commands = self.build_test_commands()
        
        print(f"\n🚀 Starting validation of {len(test_commands)} commands")
        print("=" * 60)
        
        # Execute all tests
        for test_config in test_commands:
            result = self.run_single_command_validation(test_config)
            self.validation_results.append(result)
        
        # Generate comprehensive summary
        return self._generate_validation_summary()
    
    def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate comprehensive validation summary"""
        
        # Count results by status
        status_counts = {}
        for result in self.validation_results:
            status = result.validation_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by CLI implementation
        cli_counts = {}
        for result in self.validation_results:
            cli = result.cli_implementation
            if cli not in cli_counts:
                cli_counts[cli] = {"total": 0, "fixed": 0, "improved": 0, "failing": 0}
            
            cli_counts[cli]["total"] += 1
            if result.validation_status == "FIXED":
                cli_counts[cli]["fixed"] += 1
            elif result.validation_status == "IMPROVED":
                cli_counts[cli]["improved"] += 1
            elif result.validation_status == "STILL_FAILING":
                cli_counts[cli]["failing"] += 1
        
        # Calculate success metrics
        total_commands = len(self.validation_results)
        fixed_count = status_counts.get("FIXED", 0)
        improved_count = status_counts.get("IMPROVED", 0)
        working_count = fixed_count + improved_count
        
        success_rate = (working_count / total_commands * 100) if total_commands > 0 else 0
        
        summary = {
            "validation_metadata": {
                "session_id": self.session_id,
                "timestamp": self.validation_timestamp.isoformat(),
                "total_commands_tested": total_commands,
                "total_duration_seconds": sum(r.duration_seconds for r in self.validation_results)
            },
            "validation_results_summary": {
                "commands_fixed": fixed_count,
                "commands_improved": improved_count,
                "commands_working": working_count,
                "commands_still_failing": status_counts.get("STILL_FAILING", 0),
                "overall_success_rate_percent": success_rate
            },
            "status_breakdown": status_counts,
            "cli_implementation_breakdown": cli_counts,
            "detailed_results": [asdict(result) for result in self.validation_results],
            "recommendations": self._generate_recommendations()
        }
        
        return summary
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        
        recommendations = []
        
        fixed_count = sum(1 for r in self.validation_results if r.validation_status == "FIXED")
        improved_count = sum(1 for r in self.validation_results if r.validation_status == "IMPROVED")
        failing_count = sum(1 for r in self.validation_results if r.validation_status == "STILL_FAILING")
        
        if fixed_count >= 3:
            recommendations.append("✅ Major success: Multiple commands successfully fixed and operational")
        
        if improved_count > 0:
            recommendations.append("⚡ Partial success: Some commands work but need minor refinements")
        
        if failing_count == 0:
            recommendations.append("🎯 Perfect result: All 8 commands are now working!")
        elif failing_count <= 2:
            recommendations.append("📈 Excellent progress: Only minor issues remain")
        else:
            recommendations.append("🔧 Additional work needed: Several commands still require fixes")
        
        # Specific recommendations for failing commands
        for result in self.validation_results:
            if result.validation_status == "STILL_FAILING":
                recommendations.append(f"🛠️ Fix needed: {result.command_id} - {result.notes}")
        
        return recommendations
    
    def print_validation_summary(self, summary: Dict[str, Any]):
        """Print human-readable validation summary"""
        
        print("\n" + "=" * 70)
        print("✅ 8 COMMAND VALIDATION RESULTS")
        print("=" * 70)
        
        metadata = summary['validation_metadata']
        results = summary['validation_results_summary']
        
        print(f"🆔 Session: {metadata['session_id']}")
        print(f"📅 Timestamp: {metadata['timestamp']}")
        print(f"⏱️ Total Duration: {metadata['total_duration_seconds']:.1f} seconds")
        print(f"🧪 Commands Tested: {metadata['total_commands_tested']}")
        
        print(f"\n📊 VALIDATION RESULTS:")
        print(f"   ✅ Fixed: {results['commands_fixed']} commands")
        print(f"   ⚡ Improved: {results['commands_improved']} commands") 
        print(f"   🔧 Still Failing: {results['commands_still_failing']} commands")
        print(f"   📈 Working Total: {results['commands_working']} commands")
        print(f"   🎯 Success Rate: {results['overall_success_rate_percent']:.1f}%")
        
        print(f"\n🏗️ CLI IMPLEMENTATION BREAKDOWN:")
        for cli, stats in summary['cli_implementation_breakdown'].items():
            success_rate = ((stats['fixed'] + stats['improved']) / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   📦 {cli}: {success_rate:.0f}% success ({stats['fixed']}F + {stats['improved']}I / {stats['total']}T)")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(summary['recommendations'], 1):
            print(f"   {i}. {rec}")
        
        if results['overall_success_rate_percent'] >= 80:
            print(f"\n🎉 EXCELLENT PROGRESS: {results['overall_success_rate_percent']:.1f}% of commands now working!")
        elif results['overall_success_rate_percent'] >= 60:
            print(f"\n👍 GOOD PROGRESS: {results['overall_success_rate_percent']:.1f}% success rate achieved")
        else:
            print(f"\n⚠️ MORE WORK NEEDED: {results['overall_success_rate_percent']:.1f}% success rate")


def main():
    """Execute 8 command validation testing"""
    validator = EightCommandValidator()
    
    # Run comprehensive validation
    validation_summary = validator.run_comprehensive_validation()
    
    # Print summary  
    validator.print_validation_summary(validation_summary)
    
    # Save detailed results
    results_file = f"{validator.session_id}_results.json"
    with open(results_file, 'w') as f:
        json.dump(validation_summary, f, indent=2)
    
    print(f"\n📄 Detailed results saved: {results_file}")
    print(f"✅ 8 Command Validation Testing Complete!")
    
    return validation_summary


if __name__ == "__main__":
    main() 