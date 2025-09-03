#!/usr/bin/env python3
"""
AI Task Orchestrator - Remote Repository Configuration Script
============================================================

Following the AI Task Orchestrator Guide execution plan:
Execute systematic remote repository configuration for all plc-xxx repositories

Task: Update all plc-xxx repositories from Copia.io to GitHub remotes
Current: https://app.copia.io/WhiskeyHouse/PLC-xxx.git
Target: https://github.com/reh3376/plc-xxx.git

Based on analysis: All 6 repositories need remote URL updates
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class RemoteRepositoryConfigurator:
    """Configure remote repositories following AI Task Orchestrator methodology"""

    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.repository_mappings = {
            'plc-100': 'https://github.com/reh3376/plc-100.git',
            'plc-200': 'https://github.com/reh3376/plc-200.git',
            'plc-300': 'https://github.com/reh3376/plc-300.git',
            'plc-400': 'https://github.com/reh3376/plc-400.git',
            'plc-500': 'https://github.com/reh3376/plc-500.git',
            'plc-600': 'https://github.com/reh3376/plc-600.git'
        }
        self.configuration_results = {}

    def execute_git_command(self, command: List[str], repo_path: Path, timeout: int = 30) -> Dict[str, Any]:
        """
        Execute a Git command safely with error handling
        """
        result = {
            'command': ' '.join(command),
            'success': False,
            'stdout': '',
            'stderr': '',
            'return_code': None
        }

        try:
            process_result = subprocess.run(
                command,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            result['success'] = process_result.returncode == 0
            result['stdout'] = process_result.stdout.strip()
            result['stderr'] = process_result.stderr.strip()
            result['return_code'] = process_result.returncode

        except subprocess.TimeoutExpired:
            result['stderr'] = f'Command timed out after {timeout} seconds'
        except Exception as e:
            result['stderr'] = f'Unexpected error: {str(e)}'

        return result

    def step1_preflight_validation(self) -> Dict[str, Any]:
        """
        Step 1: Pre-flight Validation
        Verify Git availability and repository status
        """
        print("🚀 Step 1: Pre-flight Validation")
        print("=" * 50)

        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'git_available': False,
            'git_version': '',
            'repositories_status': {},
            'validation_passed': False,
            'issues_found': []
        }

        # Check Git availability
        try:
            git_version_result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=10)
            if git_version_result.returncode == 0:
                validation_results['git_available'] = True
                validation_results['git_version'] = git_version_result.stdout.strip()
                print(f"✅ Git available: {validation_results['git_version']}")
            else:
                validation_results['issues_found'].append('Git not available')
                print("❌ Git not available")
        except Exception as e:
            validation_results['issues_found'].append(f'Error checking Git: {str(e)}')
            print(f"❌ Error checking Git: {e}")

        # Check each repository
        for repo_name, target_url in self.repository_mappings.items():
            repo_path = self.base_path / repo_name

            print(f"\n📁 Validating {repo_name}")

            repo_status = {
                'exists': repo_path.exists(),
                'is_git_repo': False,
                'current_remotes': {},
                'needs_update': False,
                'validation_status': 'unknown'
            }

            if not repo_path.exists():
                repo_status['validation_status'] = 'missing'
                validation_results['issues_found'].append(f'{repo_name}: Repository directory not found')
                print("   ❌ Repository directory not found")
            elif not (repo_path / '.git').exists():
                repo_status['validation_status'] = 'not_git'
                validation_results['issues_found'].append(f'{repo_name}: Not a Git repository')
                print("   ❌ Not a Git repository")
            else:
                repo_status['is_git_repo'] = True

                # Get current remotes
                remote_result = self.execute_git_command(['git', 'remote', '-v'], repo_path)
                if remote_result['success']:
                    remotes = {}
                    for line in remote_result['stdout'].split('\n'):
                        if line.strip():
                            parts = line.split('\t')
                            if len(parts) >= 2:
                                remote_name = parts[0]
                                url_and_type = parts[1].split(' ')
                                url = url_and_type[0]
                                if remote_name not in remotes:
                                    remotes[remote_name] = url

                    repo_status['current_remotes'] = remotes

                    # Check if update is needed
                    if 'origin' in remotes:
                        current_origin = remotes['origin']
                        if current_origin != target_url:
                            repo_status['needs_update'] = True
                            repo_status['validation_status'] = 'needs_update'
                            print(f"   ⚠️  Needs update: {current_origin} → {target_url}")
                        else:
                            repo_status['validation_status'] = 'correct'
                            print(f"   ✅ Already correct: {current_origin}")
                    else:
                        repo_status['needs_update'] = True
                        repo_status['validation_status'] = 'no_origin'
                        validation_results['issues_found'].append(f'{repo_name}: No origin remote configured')
                        print("   ⚠️  No origin remote configured")
                else:
                    repo_status['validation_status'] = 'git_error'
                    validation_results['issues_found'].append(f'{repo_name}: Error getting remotes - {remote_result["stderr"]}')
                    print(f"   ❌ Error getting remotes: {remote_result['stderr']}")

            validation_results['repositories_status'][repo_name] = repo_status

        # Overall validation
        critical_issues = [issue for issue in validation_results['issues_found']
                          if 'not found' in issue or 'Not a Git repository' in issue or 'Git not available' in issue]

        if not critical_issues:
            validation_results['validation_passed'] = True
            print("\n✅ Pre-flight validation passed")
        else:
            print(f"\n❌ Pre-flight validation failed - {len(critical_issues)} critical issues")

        print(f"📊 Summary: {len([r for r in validation_results['repositories_status'].values() if r.get('needs_update')])} repositories need updates")

        self.configuration_results['step1_validation'] = validation_results
        return validation_results

    def step2_current_remote_analysis(self) -> Dict[str, Any]:
        """
        Step 2: Current Remote Analysis
        Analyze current remote configurations and identify changes needed
        """
        print("\n🔍 Step 2: Current Remote Analysis")
        print("=" * 50)

        analysis_results = {
            'timestamp': datetime.now().isoformat(),
            'repository_analysis': {},
            'summary': {
                'total_repositories': len(self.repository_mappings),
                'repositories_correct': 0,
                'repositories_need_update': 0,
                'repositories_no_origin': 0,
                'repositories_with_issues': 0
            },
            'change_plan': []
        }

        validation_results = self.configuration_results.get('step1_validation', {})

        for repo_name, target_url in self.repository_mappings.items():
            repo_status = validation_results.get('repositories_status', {}).get(repo_name, {})

            print(f"\n📁 Analyzing {repo_name}")

            repo_analysis = {
                'repository': repo_name,
                'target_url': target_url,
                'current_status': repo_status.get('validation_status', 'unknown'),
                'current_remotes': repo_status.get('current_remotes', {}),
                'action_needed': 'none',
                'backup_info': {}
            }

            if repo_status.get('validation_status') == 'correct':
                repo_analysis['action_needed'] = 'none'
                analysis_results['summary']['repositories_correct'] += 1
                print("   ✅ No action needed - already correct")

            elif repo_status.get('validation_status') == 'needs_update':
                repo_analysis['action_needed'] = 'update_origin'
                repo_analysis['backup_info'] = {
                    'current_origin': repo_status['current_remotes'].get('origin'),
                    'backup_remote_name': 'origin_backup'
                }
                analysis_results['summary']['repositories_need_update'] += 1
                analysis_results['change_plan'].append({
                    'repository': repo_name,
                    'action': 'Update origin remote URL',
                    'from': repo_status['current_remotes'].get('origin'),
                    'to': target_url
                })
                print("   🔄 Action: Update origin remote")
                print(f"      From: {repo_status['current_remotes'].get('origin')}")
                print(f"      To: {target_url}")

            elif repo_status.get('validation_status') == 'no_origin':
                repo_analysis['action_needed'] = 'add_origin'
                analysis_results['summary']['repositories_no_origin'] += 1
                analysis_results['change_plan'].append({
                    'repository': repo_name,
                    'action': 'Add origin remote',
                    'to': target_url
                })
                print("   ➕ Action: Add origin remote")
                print(f"      To: {target_url}")

            else:
                repo_analysis['action_needed'] = 'manual_intervention'
                analysis_results['summary']['repositories_with_issues'] += 1
                print(f"   ⚠️  Manual intervention required: {repo_status.get('validation_status')}")

            analysis_results['repository_analysis'][repo_name] = repo_analysis

        # Print summary
        print("\n📊 Analysis Summary:")
        summary = analysis_results['summary']
        print(f"   Total repositories: {summary['total_repositories']}")
        print(f"   Already correct: {summary['repositories_correct']}")
        print(f"   Need URL update: {summary['repositories_need_update']}")
        print(f"   Need origin added: {summary['repositories_no_origin']}")
        print(f"   Have issues: {summary['repositories_with_issues']}")

        print("\n📋 Change Plan:")
        for change in analysis_results['change_plan']:
            print(f"   - {change['repository']}: {change['action']}")
            if 'from' in change:
                print(f"     From: {change['from']}")
            print(f"     To: {change['to']}")

        self.configuration_results['step2_analysis'] = analysis_results
        return analysis_results

    def step3_remote_configuration_updates(self) -> Dict[str, Any]:
        """
        Step 3: Remote Configuration Updates
        Update remote URLs for repositories that need changes
        """
        print("\n🔧 Step 3: Remote Configuration Updates")
        print("=" * 50)

        update_results = {
            'timestamp': datetime.now().isoformat(),
            'repository_updates': {},
            'summary': {
                'total_updates_attempted': 0,
                'successful_updates': 0,
                'failed_updates': 0,
                'skipped_updates': 0
            }
        }

        analysis_results = self.configuration_results.get('step2_analysis', {})

        for repo_name, repo_analysis in analysis_results.get('repository_analysis', {}).items():
            repo_path = self.base_path / repo_name

            print(f"\n🏭 Updating {repo_name}")

            repo_update = {
                'repository': repo_name,
                'action_needed': repo_analysis.get('action_needed'),
                'operations_performed': [],
                'success': False,
                'error_messages': []
            }

            if repo_analysis.get('action_needed') == 'none':
                repo_update['success'] = True
                update_results['summary']['skipped_updates'] += 1
                print("   ⏭️  Skipped - no action needed")

            elif repo_analysis.get('action_needed') == 'update_origin':
                update_results['summary']['total_updates_attempted'] += 1

                # Backup current remote (optional safety measure)
                backup_info = repo_analysis.get('backup_info', {})
                current_origin = backup_info.get('current_origin')
                target_url = repo_analysis.get('target_url')

                print("   🔄 Updating origin remote...")
                print(f"      From: {current_origin}")
                print(f"      To: {target_url}")

                # Update the origin remote URL
                update_cmd = ['git', 'remote', 'set-url', 'origin', target_url]
                update_result = self.execute_git_command(update_cmd, repo_path)

                repo_update['operations_performed'].append({
                    'operation': 'set_origin_url',
                    'command': update_result['command'],
                    'success': update_result['success'],
                    'output': update_result['stdout'],
                    'error': update_result['stderr']
                })

                if update_result['success']:
                    print("   ✅ Origin remote updated successfully")
                    repo_update['success'] = True
                    update_results['summary']['successful_updates'] += 1
                else:
                    print(f"   ❌ Failed to update origin remote: {update_result['stderr']}")
                    repo_update['error_messages'].append(f"Failed to update origin: {update_result['stderr']}")
                    update_results['summary']['failed_updates'] += 1

            elif repo_analysis.get('action_needed') == 'add_origin':
                update_results['summary']['total_updates_attempted'] += 1
                target_url = repo_analysis.get('target_url')

                print("   ➕ Adding origin remote...")
                print(f"      To: {target_url}")

                # Add the origin remote
                add_cmd = ['git', 'remote', 'add', 'origin', target_url]
                add_result = self.execute_git_command(add_cmd, repo_path)

                repo_update['operations_performed'].append({
                    'operation': 'add_origin',
                    'command': add_result['command'],
                    'success': add_result['success'],
                    'output': add_result['stdout'],
                    'error': add_result['stderr']
                })

                if add_result['success']:
                    print("   ✅ Origin remote added successfully")
                    repo_update['success'] = True
                    update_results['summary']['successful_updates'] += 1
                else:
                    print(f"   ❌ Failed to add origin remote: {add_result['stderr']}")
                    repo_update['error_messages'].append(f"Failed to add origin: {add_result['stderr']}")
                    update_results['summary']['failed_updates'] += 1

            else:
                print("   ⚠️  Skipped - requires manual intervention")
                repo_update['error_messages'].append('Requires manual intervention')
                update_results['summary']['skipped_updates'] += 1

            update_results['repository_updates'][repo_name] = repo_update

        # Print summary
        print("\n📊 Update Summary:")
        summary = update_results['summary']
        print(f"   Updates attempted: {summary['total_updates_attempted']}")
        print(f"   Successful: {summary['successful_updates']}")
        print(f"   Failed: {summary['failed_updates']}")
        print(f"   Skipped: {summary['skipped_updates']}")

        if summary['successful_updates'] == summary['total_updates_attempted'] and summary['total_updates_attempted'] > 0:
            print("\n✅ All remote configuration updates completed successfully!")
        elif summary['failed_updates'] > 0:
            print("\n⚠️  Some updates failed - check individual repository results")

        self.configuration_results['step3_updates'] = update_results
        return update_results

    def step4_connectivity_validation(self) -> Dict[str, Any]:
        """
        Step 4: Connectivity Validation
        Test connectivity to remote repositories
        """
        print("\n🌐 Step 4: Connectivity Validation")
        print("=" * 50)

        connectivity_results = {
            'timestamp': datetime.now().isoformat(),
            'repository_connectivity': {},
            'summary': {
                'total_tests': 0,
                'successful_connections': 0,
                'failed_connections': 0,
                'authentication_issues': 0
            }
        }

        for repo_name, target_url in self.repository_mappings.items():
            repo_path = self.base_path / repo_name

            print(f"\n🔗 Testing {repo_name}")

            connectivity_test = {
                'repository': repo_name,
                'target_url': target_url,
                'tests_performed': [],
                'connectivity_status': 'unknown',
                'can_fetch': False,
                'authentication_ok': False
            }

            connectivity_results['summary']['total_tests'] += 1

            # Test 1: Verify remote configuration
            print("   🔍 Verifying remote configuration...")
            remote_check = self.execute_git_command(['git', 'remote', 'get-url', 'origin'], repo_path)

            connectivity_test['tests_performed'].append({
                'test': 'remote_configuration',
                'command': remote_check['command'],
                'success': remote_check['success'],
                'result': remote_check['stdout'],
                'error': remote_check['stderr']
            })

            if remote_check['success']:
                configured_url = remote_check['stdout'].strip()
                if configured_url == target_url:
                    print(f"   ✅ Remote correctly configured: {configured_url}")
                else:
                    print(f"   ⚠️  Remote mismatch: {configured_url} != {target_url}")
            else:
                print(f"   ❌ Error getting remote URL: {remote_check['stderr']}")

            # Test 2: Test fetch capability (lightweight test)
            print("   🔄 Testing fetch capability...")
            fetch_test = self.execute_git_command(['git', 'ls-remote', 'origin', 'HEAD'], repo_path, timeout=60)

            connectivity_test['tests_performed'].append({
                'test': 'fetch_capability',
                'command': fetch_test['command'],
                'success': fetch_test['success'],
                'result': fetch_test['stdout'][:200] if fetch_test['stdout'] else '',  # Truncate for readability
                'error': fetch_test['stderr']
            })

            if fetch_test['success']:
                connectivity_test['can_fetch'] = True
                connectivity_test['authentication_ok'] = True
                connectivity_test['connectivity_status'] = 'connected'
                connectivity_results['summary']['successful_connections'] += 1
                print("   ✅ Connectivity test passed")
            else:
                connectivity_test['connectivity_status'] = 'failed'
                connectivity_results['summary']['failed_connections'] += 1

                # Analyze the error
                error_msg = fetch_test['stderr'].lower()
                if 'authentication' in error_msg or 'permission denied' in error_msg or 'could not read' in error_msg:
                    connectivity_test['connectivity_status'] = 'authentication_failed'
                    connectivity_results['summary']['authentication_issues'] += 1
                    print(f"   🔐 Authentication issue: {fetch_test['stderr']}")
                else:
                    print(f"   ❌ Connectivity failed: {fetch_test['stderr']}")

            connectivity_results['repository_connectivity'][repo_name] = connectivity_test

        # Print summary
        print("\n📊 Connectivity Summary:")
        summary = connectivity_results['summary']
        print(f"   Total tests: {summary['total_tests']}")
        print(f"   Successful connections: {summary['successful_connections']}")
        print(f"   Failed connections: {summary['failed_connections']}")
        print(f"   Authentication issues: {summary['authentication_issues']}")

        if summary['successful_connections'] == summary['total_tests']:
            print("\n✅ All repositories can connect to their remotes!")
        elif summary['authentication_issues'] > 0:
            print("\n🔐 Authentication setup required for GitHub access")
            print("   Consider setting up SSH keys or GitHub token authentication")
        else:
            print("\n⚠️  Some connectivity issues found - check network and URLs")

        self.configuration_results['step4_connectivity'] = connectivity_results
        return connectivity_results

    def step5_comprehensive_reporting(self) -> Dict[str, Any]:
        """
        Step 5: Comprehensive Reporting
        Generate detailed report of all remote configurations
        """
        print("\n📊 Step 5: Comprehensive Reporting")
        print("=" * 50)

        comprehensive_report = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'Remote Repository Configuration',
            'method': 'AI Task Orchestrator Guide',
            'repository_mappings': self.repository_mappings,
            'execution_results': self.configuration_results,
            'final_status': {},
            'recommendations': [],
            'next_steps': []
        }

        # Analyze final status for each repository
        for repo_name in self.repository_mappings.keys():
            repo_path = self.base_path / repo_name

            # Get final remote configuration
            final_remote_check = self.execute_git_command(['git', 'remote', '-v'], repo_path)

            final_status = {
                'repository': repo_name,
                'configuration_attempted': repo_name in self.configuration_results.get('step3_updates', {}).get('repository_updates', {}),
                'configuration_successful': False,
                'connectivity_tested': repo_name in self.configuration_results.get('step4_connectivity', {}).get('repository_connectivity', {}),
                'connectivity_successful': False,
                'final_remotes': {},
                'overall_status': 'unknown'
            }

            # Parse final remotes
            if final_remote_check['success']:
                remotes = {}
                for line in final_remote_check['stdout'].split('\n'):
                    if line.strip():
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            url_and_type = parts[1].split(' ')
                            url = url_and_type[0]
                            if remote_name not in remotes:
                                remotes[remote_name] = url
                final_status['final_remotes'] = remotes

            # Check configuration success
            update_info = self.configuration_results.get('step3_updates', {}).get('repository_updates', {}).get(repo_name, {})
            if update_info.get('success'):
                final_status['configuration_successful'] = True

            # Check connectivity success
            connectivity_info = self.configuration_results.get('step4_connectivity', {}).get('repository_connectivity', {}).get(repo_name, {})
            if connectivity_info.get('can_fetch'):
                final_status['connectivity_successful'] = True

            # Determine overall status
            target_url = self.repository_mappings[repo_name]
            if final_status['final_remotes'].get('origin') == target_url:
                if final_status['connectivity_successful']:
                    final_status['overall_status'] = 'fully_configured'
                else:
                    final_status['overall_status'] = 'configured_no_connectivity'
            else:
                final_status['overall_status'] = 'configuration_failed'

            comprehensive_report['final_status'][repo_name] = final_status

            # Print individual status
            status_icon = "✅" if final_status['overall_status'] == 'fully_configured' else "⚠️" if 'configured' in final_status['overall_status'] else "❌"
            print(f"   {status_icon} {repo_name}: {final_status['overall_status']}")
            if final_status['final_remotes'].get('origin'):
                print(f"      Origin: {final_status['final_remotes']['origin']}")

        # Generate overall summary
        fully_configured = len([s for s in comprehensive_report['final_status'].values() if s['overall_status'] == 'fully_configured'])
        configured_no_conn = len([s for s in comprehensive_report['final_status'].values() if s['overall_status'] == 'configured_no_connectivity'])
        failed = len([s for s in comprehensive_report['final_status'].values() if s['overall_status'] == 'configuration_failed'])

        print("\n📊 Final Summary:")
        print(f"   Fully configured: {fully_configured}/{len(self.repository_mappings)}")
        print(f"   Configured (no connectivity): {configured_no_conn}")
        print(f"   Configuration failed: {failed}")

        # Generate recommendations
        if configured_no_conn > 0:
            comprehensive_report['recommendations'].append("Set up GitHub authentication (SSH keys or personal access token)")
            comprehensive_report['recommendations'].append("Verify network connectivity to GitHub")

        if failed > 0:
            comprehensive_report['recommendations'].append("Manually review failed repository configurations")
            comprehensive_report['recommendations'].append("Check for any local Git configuration issues")

        if fully_configured == len(self.repository_mappings):
            comprehensive_report['next_steps'].append("All repositories ready for GitHub operations")
            comprehensive_report['next_steps'].append("Test push/pull operations as needed")
            print("\n🎉 All repositories successfully configured for GitHub!")
        else:
            comprehensive_report['next_steps'].append("Address remaining configuration or connectivity issues")
            print("\n⚠️  Some repositories need additional attention")

        # Save comprehensive report
        report_file = f"remote_repository_configuration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)

        print(f"\n💾 Comprehensive report saved: {report_file}")

        return comprehensive_report

def main():
    """Main execution following AI Task Orchestrator Guide"""
    print("🚀 AI Task Orchestrator - Remote Repository Configuration")
    print("=" * 70)
    print(f"Configuration started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    configurator = RemoteRepositoryConfigurator()

    try:
        # Step 1: Pre-flight Validation
        validation_results = configurator.step1_preflight_validation()

        if not validation_results.get('validation_passed'):
            print("\n❌ Pre-flight validation failed. Cannot proceed.")
            print("Issues found:")
            for issue in validation_results.get('issues_found', []):
                print(f"  - {issue}")
            return None

        # Step 2: Current Remote Analysis
        configurator.step2_current_remote_analysis()

        # Step 3: Remote Configuration Updates
        configurator.step3_remote_configuration_updates()

        # Step 4: Connectivity Validation
        configurator.step4_connectivity_validation()

        # Step 5: Comprehensive Reporting
        final_report = configurator.step5_comprehensive_reporting()

        print("\n✅ Remote Repository Configuration Complete!")

        fully_configured = len([s for s in final_report['final_status'].values()
                               if s['overall_status'] == 'fully_configured'])
        total_repos = len(configurator.repository_mappings)

        if fully_configured == total_repos:
            print(f"🎉 All {total_repos} repositories successfully configured for GitHub!")
        else:
            print(f"⚠️  {fully_configured}/{total_repos} repositories fully configured")
            print("Check the comprehensive report for details on remaining issues")

        return final_report

    except Exception as e:
        print(f"\n❌ Configuration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
