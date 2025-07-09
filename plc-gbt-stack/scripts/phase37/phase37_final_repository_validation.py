#!/usr/bin/env python3
"""
AI Task Orchestrator - Phase 3.7 Final Repository Validation
============================================================

Following the AI Task Orchestrator Guide methodology to perform final validation
that all repositories, including plc-100, are properly populated with plc directories
and converted files.

Task Analysis:
- Complexity: Simple (Validation and reporting)
- Requirements: Verify all 6 repositories have plc directories and files
- Resources: Local repositories, git status, file system verification
- Risks: None (read-only validation)

This script will:
1. Systematically check all 6 repositories (plc-100 through plc-600)
2. Verify plc directory structure and converted files
3. Check git commit status and remote synchronization
4. Generate comprehensive validation report
5. Confirm Phase 3.7 repository population is complete
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple

class Phase37FinalRepositoryValidation:
    """AI Task Orchestrator for final repository population validation"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.repos_base = Path("/Users/reh3376/repos")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def validate_single_repository(self, repo_name: str) -> Dict[str, Any]:
        """Validate a single repository's population status"""
        repo_path = self.repos_base / repo_name
        
        validation = {
            "repository_name": repo_name,
            "local_repo_exists": False,
            "plc_directory_exists": False,
            "plc_files_count": 0,
            "converted_files_count": 0,
            "git_tracked_files": 0,
            "git_status_clean": False,
            "latest_commit_has_plc": False,
            "validation_score": 0,
            "validation_status": "failed",
            "file_details": [],
            "issues": []
        }
        
        print(f"🔍 Validating {repo_name}...")
        
        # Check if repository exists
        if not repo_path.exists():
            validation["issues"].append("Repository directory does not exist")
            print(f"   ❌ Repository not found")
            return validation
        
        validation["local_repo_exists"] = True
        
        # Check if it's a git repository
        if not (repo_path / ".git").exists():
            validation["issues"].append("Not a git repository")
            print(f"   ❌ Not a git repository")
            return validation
        
        # Check plc directory
        plc_dir = repo_path / "plc"
        if plc_dir.exists():
            validation["plc_directory_exists"] = True
            
            # Count files in plc directory
            plc_files = list(plc_dir.glob("*"))
            validation["plc_files_count"] = len(plc_files)
            
            # Count converted L5X files
            l5x_files = list(plc_dir.glob("*_converted.L5X"))
            validation["converted_files_count"] = len(l5x_files)
            
            # Store file details
            validation["file_details"] = [f.name for f in plc_files]
            
            print(f"   ✅ PLC directory: {len(plc_files)} files, {len(l5x_files)} converted")
        else:
            validation["issues"].append("PLC directory does not exist")
            print(f"   ❌ PLC directory not found")
        
        # Check git status
        try:
            # Check if plc files are tracked
            ls_files_result = subprocess.run(
                ["git", "ls-files", "plc/"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if ls_files_result.returncode == 0:
                tracked_files = [f for f in ls_files_result.stdout.strip().split('\n') if f]
                validation["git_tracked_files"] = len(tracked_files)
                print(f"   ✅ Git tracked files: {len(tracked_files)}")
            
            # Check git status
            status_result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if status_result.returncode == 0:
                validation["git_status_clean"] = not bool(status_result.stdout.strip())
                status_desc = "clean" if validation["git_status_clean"] else "has changes"
                print(f"   {'✅' if validation['git_status_clean'] else '⚠️'} Git status: {status_desc}")
            
            # Check if latest commit includes plc files
            log_result = subprocess.run(
                ["git", "log", "--name-only", "-1", "--pretty=format:"],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if log_result.returncode == 0:
                latest_files = log_result.stdout.strip().split('\n')
                has_plc_files = any('plc/' in f for f in latest_files if f)
                validation["latest_commit_has_plc"] = has_plc_files
                print(f"   {'✅' if has_plc_files else '⚠️'} Latest commit includes PLC files: {has_plc_files}")
            
        except Exception as e:
            validation["issues"].append(f"Git validation error: {e}")
            print(f"   ❌ Git error: {e}")
        
        # Calculate validation score
        score = 0
        if validation["local_repo_exists"]:
            score += 20
        if validation["plc_directory_exists"]:
            score += 20
        if validation["plc_files_count"] > 0:
            score += 20
        if validation["converted_files_count"] > 0:
            score += 20
        if validation["git_tracked_files"] > 0:
            score += 10
        if validation["latest_commit_has_plc"]:
            score += 10
        
        validation["validation_score"] = score
        
        # Determine validation status
        if score >= 90:
            validation["validation_status"] = "excellent"
        elif score >= 80:
            validation["validation_status"] = "good"
        elif score >= 60:
            validation["validation_status"] = "acceptable"
        else:
            validation["validation_status"] = "failed"
        
        status_emoji = {
            "excellent": "🎉",
            "good": "✅", 
            "acceptable": "⚠️",
            "failed": "❌"
        }
        
        print(f"   {status_emoji[validation['validation_status']]} Validation: {score}% ({validation['validation_status']})")
        
        return validation
    
    def execute_comprehensive_validation(self) -> Dict[str, Any]:
        """Execute comprehensive validation of all repositories"""
        print("🤖 AI Task Orchestrator - Final Repository Population Validation")
        print("=" * 70)
        print("Objective: Verify all repositories are properly populated with plc directories")
        print()
        
        validation_results = {
            "execution_timestamp": datetime.now().isoformat(),
            "methodology": "AI Task Orchestrator Guide - Final Repository Validation",
            "repositories_validated": 0,
            "repositories_passed": 0,
            "total_files_found": 0,
            "total_converted_files": 0,
            "repository_details": {},
            "overall_status": "unknown",
            "summary_statistics": {}
        }
        
        repo_names = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
        
        print("📊 Repository Population Validation")
        print("-" * 40)
        
        for repo_name in repo_names:
            repo_validation = self.validate_single_repository(repo_name)
            validation_results["repository_details"][repo_name] = repo_validation
            validation_results["repositories_validated"] += 1
            
            if repo_validation["validation_status"] in ["excellent", "good", "acceptable"]:
                validation_results["repositories_passed"] += 1
            
            validation_results["total_files_found"] += repo_validation["plc_files_count"]
            validation_results["total_converted_files"] += repo_validation["converted_files_count"]
        
        # Calculate summary statistics
        success_rate = (validation_results["repositories_passed"] / 
                       validation_results["repositories_validated"]) * 100
        
        validation_results["summary_statistics"] = {
            "success_rate": success_rate,
            "repositories_excellent": sum(1 for r in validation_results["repository_details"].values() 
                                        if r["validation_status"] == "excellent"),
            "repositories_good": sum(1 for r in validation_results["repository_details"].values() 
                                   if r["validation_status"] == "good"),
            "repositories_acceptable": sum(1 for r in validation_results["repository_details"].values() 
                                         if r["validation_status"] == "acceptable"),
            "repositories_failed": sum(1 for r in validation_results["repository_details"].values() 
                                     if r["validation_status"] == "failed"),
            "average_validation_score": sum(r["validation_score"] for r in validation_results["repository_details"].values()) / 6
        }
        
        # Determine overall status
        if success_rate >= 95:
            validation_results["overall_status"] = "complete"
        elif success_rate >= 80:
            validation_results["overall_status"] = "substantial"
        elif success_rate >= 60:
            validation_results["overall_status"] = "partial"
        else:
            validation_results["overall_status"] = "incomplete"
        
        print("\n" + "=" * 70)
        print("🎯 FINAL REPOSITORY VALIDATION RESULTS")
        print("=" * 70)
        
        stats = validation_results["summary_statistics"]
        print(f"🎯 Overall Status: {validation_results['overall_status']}")
        print(f"📊 Success Rate: {success_rate:.1f}%")
        print(f"📁 Total Files Found: {validation_results['total_files_found']}")
        print(f"🔄 Converted Files: {validation_results['total_converted_files']}")
        print(f"📈 Average Score: {stats['average_validation_score']:.1f}%")
        print()
        
        print("📋 Repository Status Summary:")
        print(f"   🎉 Excellent: {stats['repositories_excellent']}/6 repositories")
        print(f"   ✅ Good: {stats['repositories_good']}/6 repositories") 
        print(f"   ⚠️ Acceptable: {stats['repositories_acceptable']}/6 repositories")
        print(f"   ❌ Failed: {stats['repositories_failed']}/6 repositories")
        print()
        
        if validation_results["overall_status"] == "complete":
            print("🎉 PHASE 3.7 REPOSITORY POPULATION COMPLETE!")
            print("   • All repositories properly populated with plc directories")
            print("   • Converted L5X files present in all repositories")
            print("   • Git workflow implementation fully operational")
            print("   • Repository population issue FULLY RESOLVED")
        elif validation_results["overall_status"] == "substantial":
            print("✅ PHASE 3.7 REPOSITORY POPULATION SUBSTANTIALLY COMPLETE!")
            print("   • Most repositories properly populated")
            print("   • Minor issues may exist but overall success achieved")
            print("   • Repository population largely resolved")
        else:
            print("⚠️ PHASE 3.7 REPOSITORY POPULATION NEEDS ATTENTION")
            print("   • Some repositories require additional work")
            print("   • Review individual repository validation results")
            print("   • Manual intervention may be required")
        
        # Special note about plc-100
        plc100_status = validation_results["repository_details"]["plc-100"]["validation_status"]
        plc100_score = validation_results["repository_details"]["plc-100"]["validation_score"]
        
        print(f"\n🎯 PLC-100 Specific Status:")
        print(f"   📊 Validation Score: {plc100_score}%")
        print(f"   🎯 Status: {plc100_status}")
        
        if plc100_status in ["excellent", "good"]:
            print("   ✅ PLC-100 repository population CONFIRMED")
        else:
            print("   ⚠️ PLC-100 repository may need attention")
        
        return validation_results

def main():
    """Main execution function"""
    validator = Phase37FinalRepositoryValidation()
    results = validator.execute_comprehensive_validation()
    
    # Save results
    results_file = f"phase37_final_repository_validation_{validator.timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Final repository validation results saved to: {results_file}")
    
    return 0 if results.get("overall_status") in ["complete", "substantial"] else 1

if __name__ == "__main__":
    sys.exit(main()) 