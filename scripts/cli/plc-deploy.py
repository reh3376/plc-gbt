#!/usr/bin/env python3
"""
PLC Deployment Tool
Enhanced CLI for automated GitHub deployment
"""

import argparse
import sys
from pathlib import Path
import subprocess
import json
from datetime import datetime

def deploy_to_github(repo_path, github_repo, commit_message=None):
    """Deploy repository to GitHub"""
    if not commit_message:
        commit_message = f"Automated deployment - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    deployment_result = {
        "repository": github_repo,
        "local_path": str(repo_path),
        "commit_message": commit_message,
        "timestamp": datetime.now().isoformat(),
        "status": "unknown",
        "files_added": 0,
        "operations": []
    }
    
    try:
        repo_path = Path(repo_path)
        
        # Check if it's a git repository
        if not (repo_path / ".git").exists():
            deployment_result["status"] = "error"
            deployment_result["operations"].append("Not a git repository")
            return deployment_result
        
        # Add all files
        result = subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            deployment_result["operations"].append("Files staged successfully")
            
            # Commit changes
            commit_result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if commit_result.returncode == 0:
                deployment_result["operations"].append("Changes committed")
                
                # Push to GitHub
                push_result = subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True
                )
                
                if push_result.returncode == 0:
                    deployment_result["status"] = "success"
                    deployment_result["operations"].append("Pushed to GitHub successfully")
                else:
                    deployment_result["status"] = "push_failed"
                    deployment_result["operations"].append(f"Push failed: {push_result.stderr}")
            else:
                deployment_result["status"] = "commit_failed"
                deployment_result["operations"].append(f"Commit failed: {commit_result.stderr}")
        else:
            deployment_result["status"] = "add_failed"
            deployment_result["operations"].append(f"Add failed: {result.stderr}")
    
    except Exception as e:
        deployment_result["status"] = "error"
        deployment_result["operations"].append(f"Deployment error: {e}")
    
    return deployment_result

def main():
    parser = argparse.ArgumentParser(description="PLC GitHub Deployment Tool")
    parser.add_argument("--repo-path", required=True, help="Local repository path")
    parser.add_argument("--github-repo", required=True, help="GitHub repository (user/repo)")
    parser.add_argument("--message", help="Commit message")
    parser.add_argument("--dry-run", action="store_true", help="Simulate deployment")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No actual deployment will occur")
        return 0
    
    result = deploy_to_github(args.repo_path, args.github_repo, args.message)
    
    print(f"🚀 Deployment Status: {result['status']}")
    print("📋 Operations:")
    for operation in result["operations"]:
        print(f"   • {operation}")
    
    return 0 if result["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
