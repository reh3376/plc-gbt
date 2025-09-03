#!/usr/bin/env python3
"""
AI Task Orchestrator - Simplified Remote Repository Configuration
================================================================

Following the AI Task Orchestrator Guide execution plan:
Update all plc-xxx repositories from Copia.io to GitHub remotes

Current: https://app.copia.io/WhiskeyHouse/PLC-xxx.git
Target: https://github.com/reh3376/plc-xxx.git
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def execute_git_command(command: List[str], repo_path: Path) -> Dict[str, Any]:
    """Execute a Git command safely with error handling"""
    result = {
        'command': ' '.join(command),
        'success': False,
        'stdout': '',
        'stderr': ''
    }

    try:
        process_result = subprocess.run(
            command,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        result['success'] = process_result.returncode == 0
        result['stdout'] = process_result.stdout.strip()
        result['stderr'] = process_result.stderr.strip()

    except Exception as e:
        result['stderr'] = f'Error: {str(e)}'

    return result

def main():
    """Main execution following AI Task Orchestrator Guide"""
    print("🚀 AI Task Orchestrator - Remote Repository Configuration")
    print("=" * 70)
    print(f"Configuration started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    base_path = Path("/Users/reh3376/repos")
    repository_mappings = {
        'plc-100': 'https://github.com/reh3376/plc-100.git',
        'plc-200': 'https://github.com/reh3376/plc-200.git',
        'plc-300': 'https://github.com/reh3376/plc-300.git',
        'plc-400': 'https://github.com/reh3376/plc-400.git',
        'plc-500': 'https://github.com/reh3376/plc-500.git',
        'plc-600': 'https://github.com/reh3376/plc-600.git'
    }

    results = {
        'timestamp': datetime.now().isoformat(),
        'updates': {},
        'summary': {
            'total': len(repository_mappings),
            'successful': 0,
            'failed': 0
        }
    }

    # Process each repository
    for repo_name, target_url in repository_mappings.items():
        repo_path = base_path / repo_name

        print(f"\n🏭 Processing {repo_name}")
        print(f"   Path: {repo_path}")
        print(f"   Target: {target_url}")

        repo_result = {
            'repository': repo_name,
            'target_url': target_url,
            'success': False,
            'operations': [],
            'final_remote': ''
        }

        if not repo_path.exists():
            print("   ❌ Repository directory not found")
            repo_result['error'] = 'Directory not found'
            results['summary']['failed'] += 1
            results['updates'][repo_name] = repo_result
            continue

        # Check current remote
        print("   🔍 Checking current remote...")
        remote_check = execute_git_command(['git', 'remote', 'get-url', 'origin'], repo_path)

        if remote_check['success']:
            current_remote = remote_check['stdout']
            print(f"   📍 Current remote: {current_remote}")

            if current_remote == target_url:
                print("   ✅ Already correct - no update needed")
                repo_result['success'] = True
                repo_result['final_remote'] = current_remote
                results['summary']['successful'] += 1
            else:
                # Update the remote
                print("   🔄 Updating remote URL...")
                update_cmd = ['git', 'remote', 'set-url', 'origin', target_url]
                update_result = execute_git_command(update_cmd, repo_path)

                repo_result['operations'].append({
                    'operation': 'set_remote_url',
                    'command': update_result['command'],
                    'success': update_result['success'],
                    'error': update_result['stderr']
                })

                if update_result['success']:
                    print("   ✅ Remote updated successfully")
                    repo_result['success'] = True
                    repo_result['final_remote'] = target_url
                    results['summary']['successful'] += 1

                    # Verify the update
                    verify_result = execute_git_command(['git', 'remote', 'get-url', 'origin'], repo_path)
                    if verify_result['success']:
                        print(f"   ✓ Verified: {verify_result['stdout']}")
                else:
                    print(f"   ❌ Failed to update remote: {update_result['stderr']}")
                    repo_result['error'] = update_result['stderr']
                    results['summary']['failed'] += 1
        else:
            print(f"   ❌ Error getting current remote: {remote_check['stderr']}")
            repo_result['error'] = remote_check['stderr']
            results['summary']['failed'] += 1

        results['updates'][repo_name] = repo_result

    # Print final summary
    print("\n📊 Final Summary")
    print("=" * 40)
    summary = results['summary']
    print(f"Total repositories: {summary['total']}")
    print(f"Successfully updated: {summary['successful']}")
    print(f"Failed updates: {summary['failed']}")

    if summary['successful'] == summary['total']:
        print(f"\n🎉 All {summary['total']} repositories successfully configured for GitHub!")
    else:
        print(f"\n⚠️  {summary['successful']}/{summary['total']} repositories configured")

    # Test connectivity (optional)
    print("\n🌐 Testing GitHub connectivity...")
    test_repo = next(iter(repository_mappings.keys()))
    test_path = base_path / test_repo

    connectivity_test = execute_git_command(['git', 'ls-remote', 'origin', 'HEAD'], test_path)
    if connectivity_test['success']:
        print("✅ GitHub connectivity confirmed")
    else:
        print("🔐 GitHub authentication may be required")
        print(f"   Error: {connectivity_test['stderr']}")
        print("   Consider setting up SSH keys or GitHub token authentication")

    # Save results
    report_file = f"remote_config_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n💾 Results saved: {report_file}")
    print("\n✅ Remote Repository Configuration Complete!")

    return results

if __name__ == "__main__":
    main()
