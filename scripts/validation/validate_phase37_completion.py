#!/usr/bin/env python3
"""
Phase 3.7 Completion Validation Framework
=========================================

Comprehensive validation of Phase 3.7 actual completion status.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

def validate_repositories() -> Dict[str, Any]:
    """Validate all PLC repositories"""
    print("🔍 Validating PLC Repositories...")
    
    repos_dir = Path(__file__).parent.parent.parent.parent.parent
    repo_names = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]
    
    validation_results = {
        "total_repos": len(repo_names),
        "repos_exist": 0,
        "repos_with_content": 0,
        "l5x_files_found": 0,
        "repositories": {}
    }
    
    for repo_name in repo_names:
        repo_path = repos_dir / repo_name
        repo_result = {
            "exists": repo_path.exists(),
            "has_plc_dir": False,
            "l5x_files": [],
            "file_sizes": {},
            "status": "missing"
        }
        
        if repo_path.exists():
            validation_results["repos_exist"] += 1
            plc_dir = repo_path / "plc"
            
            if plc_dir.exists():
                repo_result["has_plc_dir"] = True
                l5x_files = list(plc_dir.glob("*.L5X"))
                
                if l5x_files:
                    validation_results["repos_with_content"] += 1
                    repo_result["l5x_files"] = [f.name for f in l5x_files]
                    repo_result["file_sizes"] = {f.name: f.stat().st_size for f in l5x_files}
                    validation_results["l5x_files_found"] += len(l5x_files)
                    repo_result["status"] = "has_content"
                else:
                    repo_result["status"] = "empty"
            else:
                repo_result["status"] = "no_plc_dir"
        
        validation_results["repositories"][repo_name] = repo_result
        print(f"   📁 {repo_name}: {repo_result['status']}")
    
    return validation_results

def validate_github_workflows() -> Dict[str, Any]:
    """Validate GitHub Actions workflows"""
    print("\n🚀 Validating GitHub Actions Workflows...")
    
    project_root = Path(__file__).parent.parent.parent.parent
    workflows_dir = project_root / ".github" / "workflows"
    
    workflow_results = {
        "workflows_dir_exists": workflows_dir.exists(),
        "workflows_found": 0,
        "workflows": {},
        "status": "missing"
    }
    
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.yml"))
        workflow_results["workflows_found"] = len(workflow_files)
        
        for workflow_file in workflow_files:
            workflow_results["workflows"][workflow_file.name] = {
                "size": workflow_file.stat().st_size,
                "exists": True
            }
        
        if len(workflow_files) >= 2:
            workflow_results["status"] = "adequate"
        elif len(workflow_files) >= 1:
            workflow_results["status"] = "minimal"
        else:
            workflow_results["status"] = "empty"
    
    print(f"   🚀 Workflows: {workflow_results['workflows_found']} found")
    
    return workflow_results

def validate_cli_tools() -> Dict[str, Any]:
    """Validate CLI tools functionality"""
    print("\n🛠️ Validating CLI Tools...")
    
    project_root = Path(__file__).parent.parent.parent.parent
    cli_path = project_root / "src" / "plc_format_converter" / "cli.py"
    
    cli_results = {
        "cli_exists": cli_path.exists(),
        "cli_functional": False,
        "help_output": "",
        "status": "missing"
    }
    
    if cli_path.exists():
        try:
            result = subprocess.run([
                "python3", str(cli_path), "--help"
            ], capture_output=True, text=True, cwd=project_root)
            
            if result.returncode == 0:
                cli_results["cli_functional"] = True
                cli_results["help_output"] = result.stdout[:200] + "..."
                cli_results["status"] = "functional"
            else:
                cli_results["status"] = "error"
                cli_results["error"] = result.stderr
        except Exception as e:
            cli_results["status"] = "exception"
            cli_results["error"] = str(e)
    
    print(f"   🛠️ CLI Tools: {cli_results['status']}")
    
    return cli_results

def generate_completion_report() -> Dict[str, Any]:
    """Generate comprehensive completion report"""
    print("\n📊 Generating Completion Report...")
    
    repo_validation = validate_repositories()
    workflow_validation = validate_github_workflows()
    cli_validation = validate_cli_tools()
    
    # Calculate completion percentage
    completion_score = 0
    total_criteria = 6
    
    # Repository criteria (2 points)
    if repo_validation["repos_exist"] == repo_validation["total_repos"]:
        completion_score += 1
    if repo_validation["repos_with_content"] > 0:
        completion_score += 1
    
    # Workflow criteria (2 points)
    if workflow_validation["workflows_dir_exists"]:
        completion_score += 1
    if workflow_validation["workflows_found"] >= 2:
        completion_score += 1
    
    # CLI criteria (2 points)
    if cli_validation["cli_exists"]:
        completion_score += 1
    if cli_validation["cli_functional"]:
        completion_score += 1
    
    completion_percentage = (completion_score / total_criteria) * 100
    
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "completion_percentage": completion_percentage,
        "completion_score": f"{completion_score}/{total_criteria}",
        "overall_status": "INCOMPLETE" if completion_percentage < 80 else "COMPLETE",
        "repository_validation": repo_validation,
        "workflow_validation": workflow_validation,
        "cli_validation": cli_validation,
        "recommendations": []
    }
    
    # Generate recommendations
    if repo_validation["repos_with_content"] == 0:
        report["recommendations"].append("CRITICAL: No repositories contain converted L5X files")
    
    if workflow_validation["workflows_found"] == 0:
        report["recommendations"].append("HIGH: No GitHub Actions workflows implemented")
    
    if not cli_validation["cli_functional"]:
        report["recommendations"].append("MEDIUM: CLI tools not functional")
    
    if completion_percentage < 50:
        report["recommendations"].append("URGENT: Phase 3.7 requires significant work to complete")
    
    print(f"\n🎯 Phase 3.7 Completion: {completion_percentage:.1f}%")
    print(f"📊 Score: {completion_score}/{total_criteria}")
    print(f"🏆 Status: {report['overall_status']}")
    
    return report

if __name__ == "__main__":
    report = generate_completion_report()
    
    # Save report
    report_file = f"phase37_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Validation report saved: {report_file}")
    
    # Exit with appropriate code
    if report["overall_status"] == "INCOMPLETE":
        sys.exit(1)
    else:
        sys.exit(0)
