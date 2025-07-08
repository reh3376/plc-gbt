#!/usr/bin/env python3
"""
Git Workflow Testing Script
Tests the git-based workflows with sample operations and validations
following the AI Task Orchestrator methodology.
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class GitWorkflowTester:
    """Tests git-based workflows for PLC repositories"""
    
    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.plc_repos = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.test_results = {
            "execution_timestamp": datetime.now().isoformat(),
            "repositories_tested": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "repository_results": {},
            "errors": []
        }
    
    def run_command(self, cmd: str, cwd: Path = None) -> Dict[str, Any]:
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True, 
                cwd=cwd
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }
    
    def test_repository_structure(self, repo_path: Path) -> Dict[str, Any]:
        """Test repository directory structure"""
        repo_name = repo_path.name
        
        test_result = {
            "test_name": "repository_structure",
            "repo_name": repo_name,
            "success": True,
            "checks": {},
            "errors": []
        }
        
        print(f"🔍 Testing repository structure for {repo_name}...")
        
        # Check required directories
        required_dirs = ["plc-acd", "plc-l5x", "plc-acd-previous", "plc-l5x-previous"]
        
        for dir_name in required_dirs:
            dir_path = repo_path / dir_name
            exists = dir_path.exists()
            test_result["checks"][f"{dir_name}_exists"] = exists
            
            if exists:
                print(f"   ✅ {dir_name}/ exists")
            else:
                print(f"   ❌ {dir_name}/ missing")
                test_result["success"] = False
                test_result["errors"].append(f"Missing directory: {dir_name}")
        
        # Check for README files
        for dir_name in required_dirs:
            readme_path = repo_path / dir_name / "README.md"
            exists = readme_path.exists()
            test_result["checks"][f"{dir_name}_readme"] = exists
            
            if exists:
                print(f"   ✅ {dir_name}/README.md exists")
            else:
                print(f"   ⚠️  {dir_name}/README.md missing")
        
        # Check for GitHub workflows
        workflows_dir = repo_path / ".github" / "workflows"
        workflow_files = ["plc-conversion.yml", "plc-validation.yml", "plc-branch-protection.yml"]
        
        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            exists = workflow_path.exists()
            test_result["checks"][f"workflow_{workflow_file}"] = exists
            
            if exists:
                print(f"   ✅ .github/workflows/{workflow_file} exists")
            else:
                print(f"   ❌ .github/workflows/{workflow_file} missing")
                test_result["success"] = False
                test_result["errors"].append(f"Missing workflow: {workflow_file}")
        
        return test_result
    
    def test_git_operations(self, repo_path: Path) -> Dict[str, Any]:
        """Test basic git operations"""
        repo_name = repo_path.name
        
        test_result = {
            "test_name": "git_operations",
            "repo_name": repo_name,
            "success": True,
            "operations": {},
            "errors": []
        }
        
        print(f"🔧 Testing git operations for {repo_name}...")
        
        # Test git status
        status_result = self.run_command("git status --porcelain", repo_path)
        test_result["operations"]["git_status"] = status_result["success"]
        
        if status_result["success"]:
            print(f"   ✅ Git status check passed")
        else:
            print(f"   ❌ Git status check failed")
            test_result["success"] = False
            test_result["errors"].append("Git status failed")
        
        # Test git branch
        branch_result = self.run_command("git branch --show-current", repo_path)
        test_result["operations"]["current_branch"] = branch_result["stdout"]
        
        if branch_result["success"]:
            print(f"   ✅ Current branch: {branch_result['stdout']}")
        else:
            print(f"   ❌ Branch check failed")
            test_result["success"] = False
            test_result["errors"].append("Branch check failed")
        
        # Test git remote
        remote_result = self.run_command("git remote -v", repo_path)
        test_result["operations"]["git_remote"] = remote_result["success"]
        
        if remote_result["success"]:
            print(f"   ✅ Git remote configured")
        else:
            print(f"   ❌ Git remote check failed")
            test_result["success"] = False
            test_result["errors"].append("Git remote not configured")
        
        return test_result
    
    def test_file_constraints(self, repo_path: Path) -> Dict[str, Any]:
        """Test single file constraints"""
        repo_name = repo_path.name
        
        test_result = {
            "test_name": "file_constraints",
            "repo_name": repo_name,
            "success": True,
            "file_counts": {},
            "errors": []
        }
        
        print(f"📊 Testing file constraints for {repo_name}...")
        
        # Check ACD file count in plc-acd
        acd_files = list((repo_path / "plc-acd").glob("*.acd")) + list((repo_path / "plc-acd").glob("*.ACD"))
        acd_count = len(acd_files)
        test_result["file_counts"]["plc_acd_files"] = acd_count
        
        if acd_count <= 1:
            print(f"   ✅ ACD files in plc-acd/: {acd_count} (limit: 1)")
        else:
            print(f"   ❌ ACD files in plc-acd/: {acd_count} (limit: 1)")
            test_result["success"] = False
            test_result["errors"].append(f"Too many ACD files in plc-acd/: {acd_count}")
        
        # Check L5X file count in plc-l5x
        l5x_files = list((repo_path / "plc-l5x").glob("*.l5x")) + list((repo_path / "plc-l5x").glob("*.L5X"))
        l5x_count = len(l5x_files)
        test_result["file_counts"]["plc_l5x_files"] = l5x_count
        
        if l5x_count <= 1:
            print(f"   ✅ L5X files in plc-l5x/: {l5x_count} (limit: 1)")
        else:
            print(f"   ❌ L5X files in plc-l5x/: {l5x_count} (limit: 1)")
            test_result["success"] = False
            test_result["errors"].append(f"Too many L5X files in plc-l5x/: {l5x_count}")
        
        # Check file sizes
        for acd_file in acd_files:
            size = acd_file.stat().st_size
            if size < 100:
                print(f"   ⚠️  ACD file {acd_file.name} is very small ({size} bytes)")
                test_result["errors"].append(f"ACD file {acd_file.name} may be corrupted")
            else:
                print(f"   ✅ ACD file {acd_file.name} size OK ({size:,} bytes)")
        
        return test_result
    
    def test_workflow_syntax(self, repo_path: Path) -> Dict[str, Any]:
        """Test GitHub workflow YAML syntax"""
        repo_name = repo_path.name
        
        test_result = {
            "test_name": "workflow_syntax",
            "repo_name": repo_name,
            "success": True,
            "workflow_checks": {},
            "errors": []
        }
        
        print(f"📝 Testing workflow syntax for {repo_name}...")
        
        workflows_dir = repo_path / ".github" / "workflows"
        workflow_files = ["plc-conversion.yml", "plc-validation.yml", "plc-branch-protection.yml"]
        
        for workflow_file in workflow_files:
            workflow_path = workflows_dir / workflow_file
            
            if workflow_path.exists():
                try:
                    import yaml
                    with open(workflow_path, 'r') as f:
                        workflow_content = yaml.safe_load(f)
                    
                    # Basic YAML structure checks
                    required_keys = ["name", "on", "jobs"]
                    has_required_keys = all(key in workflow_content for key in required_keys)
                    
                    test_result["workflow_checks"][workflow_file] = has_required_keys
                    
                    if has_required_keys:
                        print(f"   ✅ {workflow_file} syntax valid")
                    else:
                        print(f"   ❌ {workflow_file} missing required keys")
                        test_result["success"] = False
                        test_result["errors"].append(f"Invalid workflow syntax: {workflow_file}")
                        
                except Exception as e:
                    print(f"   ❌ {workflow_file} YAML parsing failed: {str(e)}")
                    test_result["success"] = False
                    test_result["errors"].append(f"YAML parsing error in {workflow_file}: {str(e)}")
                    test_result["workflow_checks"][workflow_file] = False
            else:
                print(f"   ❌ {workflow_file} not found")
                test_result["success"] = False
                test_result["errors"].append(f"Missing workflow file: {workflow_file}")
                test_result["workflow_checks"][workflow_file] = False
        
        return test_result
    
    def simulate_commit_workflow(self, repo_path: Path) -> Dict[str, Any]:
        """Simulate a commit workflow (dry run)"""
        repo_name = repo_path.name
        
        test_result = {
            "test_name": "simulate_commit",
            "repo_name": repo_name,
            "success": True,
            "simulation_steps": {},
            "errors": []
        }
        
        print(f"🎭 Simulating commit workflow for {repo_name}...")
        
        # Check if there are any changes to commit
        status_result = self.run_command("git status --porcelain", repo_path)
        has_changes = bool(status_result["stdout"])
        test_result["simulation_steps"]["has_changes"] = has_changes
        
        if has_changes:
            print(f"   📝 Changes detected for simulation")
            
            # Simulate git add (dry run)
            add_result = self.run_command("git add --dry-run .", repo_path)
            test_result["simulation_steps"]["add_simulation"] = add_result["success"]
            
            if add_result["success"]:
                print(f"   ✅ Git add simulation passed")
            else:
                print(f"   ❌ Git add simulation failed")
                test_result["success"] = False
                test_result["errors"].append("Git add simulation failed")
        else:
            print(f"   ℹ️  No changes to simulate")
            test_result["simulation_steps"]["add_simulation"] = True
        
        # Check commit readiness
        diff_result = self.run_command("git diff --name-only", repo_path)
        test_result["simulation_steps"]["diff_check"] = diff_result["success"]
        
        if diff_result["success"]:
            print(f"   ✅ Git diff check passed")
        else:
            print(f"   ❌ Git diff check failed")
            test_result["success"] = False
            test_result["errors"].append("Git diff check failed")
        
        return test_result
    
    def test_repository(self, repo_path: Path) -> Dict[str, Any]:
        """Run all tests for a single repository"""
        repo_name = repo_path.name
        
        print(f"\n🏭 Testing repository: {repo_name}")
        print(f"📁 Path: {repo_path}")
        
        repo_results = {
            "repo_name": repo_name,
            "tests": {},
            "overall_success": True,
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0
        }
        
        # Run all test suites
        test_suites = [
            self.test_repository_structure,
            self.test_git_operations,
            self.test_file_constraints,
            self.test_workflow_syntax,
            self.simulate_commit_workflow
        ]
        
        for test_suite in test_suites:
            test_result = test_suite(repo_path)
            test_name = test_result["test_name"]
            repo_results["tests"][test_name] = test_result
            repo_results["total_tests"] += 1
            
            if test_result["success"]:
                repo_results["passed_tests"] += 1
                print(f"   ✅ {test_name} passed")
            else:
                repo_results["failed_tests"] += 1
                repo_results["overall_success"] = False
                print(f"   ❌ {test_name} failed")
                for error in test_result["errors"]:
                    print(f"      - {error}")
        
        return repo_results
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run tests for all repositories"""
        print("🤖 AI Task Orchestrator: Git Workflow Testing")
        print("=" * 60)
        
        for repo_name in self.plc_repos:
            repo_path = self.base_path / repo_name
            
            if not repo_path.exists():
                error_msg = f"Repository {repo_name} not found at {repo_path}"
                self.test_results["errors"].append(error_msg)
                print(f"❌ {error_msg}")
                continue
            
            self.test_results["repositories_tested"] += 1
            
            # Test repository
            repo_results = self.test_repository(repo_path)
            self.test_results["repository_results"][repo_name] = repo_results
            
            # Update overall counters
            self.test_results["tests_passed"] += repo_results["passed_tests"]
            self.test_results["tests_failed"] += repo_results["failed_tests"]
            
            if repo_results["overall_success"]:
                print(f"✅ {repo_name} all tests passed")
            else:
                print(f"❌ {repo_name} has test failures")
        
        return self.test_results
    
    def generate_test_report(self) -> str:
        """Generate a comprehensive test report"""
        report_path = Path("/Users/reh3376/repos/PLC_GPT/plc-gpt-stack/results/testing-results") / f"git_workflow_test_results_{self.timestamp}.json"
        
        with open(report_path, 'w') as f:
            import json
            json.dump(self.test_results, f, indent=2)
        
        return str(report_path)

def main():
    """Main execution function"""
    tester = GitWorkflowTester()
    
    # Run all tests
    results = tester.run_all_tests()
    
    # Generate test report
    report_path = tester.generate_test_report()
    
    print(f"\n📊 Test Summary:")
    print(f"   📁 Repositories tested: {results['repositories_tested']}")
    print(f"   ✅ Tests passed: {results['tests_passed']}")
    print(f"   ❌ Tests failed: {results['tests_failed']}")
    print(f"   📊 Success rate: {(results['tests_passed'] / (results['tests_passed'] + results['tests_failed']) * 100):.1f}%")
    
    if results['errors']:
        print(f"\n⚠️  General errors:")
        for error in results['errors']:
            print(f"   - {error}")
    
    print(f"\n📄 Test report saved: {report_path}")
    
    return results

if __name__ == "__main__":
    main() 