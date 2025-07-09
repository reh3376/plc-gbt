#!/usr/bin/env python3
"""
AI Task Orchestrator - Task Analysis for Remote Repository Rehosting
===================================================================

Following the AI_TASK_ORCHESTRATOR_GUIDE.md methodology to systematically
analyze and complete the task of rehosting plc-xxx repositories to correct remote URLs.

Task: "Ensure all the plc-xxx repos are rehosted to the correct remote repo URLs"

Remote URLs:
- plc-100: https://github.com/reh3376/plc-100.git
- plc-200: https://github.com/reh3376/plc-200.git
- plc-300: https://github.com/reh3376/plc-300.git
- plc-400: https://github.com/reh3376/plc-400.git
- plc-500: https://github.com/reh3376/plc-500.git
- plc-600: https://github.com/reh3376/plc-600.git
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class RemoteRepoTaskAnalyzer:
    """Task analyzer for remote repository rehosting following AI Task Orchestrator methodology"""
    
    def __init__(self):
        self.task_description = "Ensure all plc-xxx repos are rehosted to correct remote repository URLs"
        self.base_path = Path("/Users/reh3376/repos")
        self.repository_mappings = {
            'plc-100': 'https://github.com/reh3376/plc-100.git',
            'plc-200': 'https://github.com/reh3376/plc-200.git',
            'plc-300': 'https://github.com/reh3376/plc-300.git',
            'plc-400': 'https://github.com/reh3376/plc-400.git',
            'plc-500': 'https://github.com/reh3376/plc-500.git',
            'plc-600': 'https://github.com/reh3376/plc-600.git'
        }
        self.analysis_results = {}
        
    def analyze_task_complexity(self) -> Dict[str, Any]:
        """
        Step 1: Analyze task complexity according to AI Task Orchestrator Guide
        """
        print("🔍 Step 1: Task Complexity Analysis")
        print("=" * 50)
        
        # Extract requirements from task description
        requirements = [
            "Check current remote configuration for all 6 plc-xxx repositories",
            "Verify remote URLs match the specified GitHub repositories",
            "Update remote URLs if they don't match",
            "Ensure repositories can push/pull from correct remotes",
            "Validate authentication and access permissions",
            "Handle any existing remote configurations safely"
        ]
        
        # Assess complexity based on AI Task Orchestrator Guide
        estimated_files = 1  # One script to handle all repos
        estimated_lines = 300  # Moderate Git operations script
        estimated_time = "30-45 minutes"
        
        complexity_analysis = {
            'complexity_level': 'moderate',  # Git operations, multiple repos, validation needed
            'estimated_effort': {
                'time': estimated_time,
                'lines_of_code': estimated_lines,
                'files_to_create': 1,
                'files_to_modify': 0,
                'repositories_to_update': len(self.repository_mappings)
            },
            'requirements': requirements,
            'git_operations': ['remote -v', 'remote set-url', 'remote add', 'fetch', 'push'],
            'programming_languages': ['Python', 'Git'],
            'functionality_needed': ['git_operations', 'remote_validation', 'authentication_check', 'batch_processing'],
            'quality_requirements': ['error_handling', 'validation', 'backup_safety', 'logging']
        }
        
        print(f"📊 Complexity Level: {complexity_analysis['complexity_level'].upper()}")
        print(f"⏱️  Estimated Time: {complexity_analysis['estimated_effort']['time']}")
        print(f"📝 Lines of Code: {complexity_analysis['estimated_effort']['lines_of_code']}")
        print(f"🏭 Repositories: {complexity_analysis['estimated_effort']['repositories_to_update']}")
        
        print(f"\n📋 Requirements Identified:")
        for i, req in enumerate(requirements, 1):
            print(f"  {i}. {req}")
        
        print(f"\n🔧 Git Operations Needed:")
        for op in complexity_analysis['git_operations']:
            print(f"  - git {op}")
        
        self.analysis_results['complexity'] = complexity_analysis
        return complexity_analysis
    
    def discover_resources(self) -> Dict[str, Any]:
        """
        Step 2: Resource discovery according to AI Task Orchestrator Guide
        """
        print("\n🔍 Step 2: Resource Discovery")
        print("=" * 50)
        
        resources = {
            'git_available': False,
            'repositories_exist': {},
            'current_remotes': {},
            'authentication_status': 'unknown',
            'available_tools': [],
            'existing_scripts': []
        }
        
        # Check Git availability
        try:
            result = subprocess.run(['git', '--version'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                resources['git_available'] = True
                git_version = result.stdout.strip()
                print(f"✅ Git available: {git_version}")
            else:
                print("❌ Git not available")
        except Exception as e:
            print(f"❌ Error checking Git: {e}")
        
        # Check repository existence and current remotes
        for repo_name in self.repository_mappings.keys():
            repo_path = self.base_path / repo_name
            repo_info = {
                'exists': repo_path.exists(),
                'is_git_repo': False,
                'current_remotes': {},
                'status': 'unknown'
            }
            
            if repo_path.exists():
                if (repo_path / '.git').exists():
                    repo_info['is_git_repo'] = True
                    
                    # Get current remotes
                    try:
                        remote_result = subprocess.run(['git', 'remote', '-v'], 
                                                     cwd=repo_path, capture_output=True, text=True, timeout=10)
                        if remote_result.returncode == 0:
                            remotes = {}
                            for line in remote_result.stdout.strip().split('\n'):
                                if line.strip():
                                    parts = line.split('\t')
                                    if len(parts) >= 2:
                                        remote_name = parts[0]
                                        url_and_type = parts[1].split(' ')
                                        url = url_and_type[0]
                                        if remote_name not in remotes:
                                            remotes[remote_name] = url
                            repo_info['current_remotes'] = remotes
                            
                            # Check if current remote matches expected
                            expected_url = self.repository_mappings[repo_name]
                            if 'origin' in remotes and remotes['origin'] == expected_url:
                                repo_info['status'] = 'correct'
                            elif 'origin' in remotes:
                                repo_info['status'] = 'needs_update'
                            else:
                                repo_info['status'] = 'no_origin'
                        else:
                            repo_info['status'] = 'git_error'
                    except Exception as e:
                        repo_info['status'] = f'error: {str(e)}'
                else:
                    repo_info['status'] = 'not_git_repo'
            else:
                repo_info['status'] = 'not_found'
            
            resources['repositories_exist'][repo_name] = repo_info
            
            status_icon = "✅" if repo_info['status'] == 'correct' else "⚠️" if repo_info['status'] in ['needs_update', 'no_origin'] else "❌"
            print(f"  {status_icon} {repo_name}: {repo_info['status']}")
            if repo_info['current_remotes']:
                for remote_name, url in repo_info['current_remotes'].items():
                    print(f"      {remote_name}: {url}")
        
        # Available tools
        resources['available_tools'] = [
            'Git command line interface',
            'Python subprocess for Git operations',
            'Pathlib for file system operations'
        ]
        
        print(f"\n📦 Available Tools:")
        for tool in resources['available_tools']:
            print(f"  - {tool}")
        
        self.analysis_results['resources'] = resources
        return resources
    
    def assess_risks(self) -> Dict[str, Any]:
        """
        Step 3: Risk assessment according to AI Task Orchestrator Guide
        """
        print("\n⚠️  Step 3: Risk Assessment")
        print("=" * 50)
        
        risks = {
            'high_risk': [],
            'medium_risk': [],
            'low_risk': [],
            'mitigation_strategies': {}
        }
        
        # Assess potential risks based on resource discovery
        resources = self.analysis_results.get('resources', {})
        
        # High risk issues
        if not resources.get('git_available'):
            risks['high_risk'].append("Git not available on system")
            risks['mitigation_strategies']['git_unavailable'] = "Install Git before proceeding"
        
        # Check for repositories that don't exist
        missing_repos = [repo for repo, info in resources.get('repositories_exist', {}).items() 
                        if not info.get('exists')]
        if missing_repos:
            risks['high_risk'].append(f"Missing repositories: {', '.join(missing_repos)}")
            risks['mitigation_strategies']['missing_repos'] = "Clone or create missing repositories"
        
        # Medium risk issues
        repos_needing_update = [repo for repo, info in resources.get('repositories_exist', {}).items() 
                               if info.get('status') == 'needs_update']
        if repos_needing_update:
            risks['medium_risk'].append(f"Repositories with incorrect remotes: {', '.join(repos_needing_update)}")
            risks['mitigation_strategies']['incorrect_remotes'] = "Update remote URLs carefully, backup current configuration"
        
        repos_no_origin = [repo for repo, info in resources.get('repositories_exist', {}).items() 
                          if info.get('status') == 'no_origin']
        if repos_no_origin:
            risks['medium_risk'].append(f"Repositories without origin remote: {', '.join(repos_no_origin)}")
            risks['mitigation_strategies']['no_origin'] = "Add origin remote with correct URL"
        
        # Low risk issues
        risks['low_risk'].append("Authentication might be required for GitHub access")
        risks['mitigation_strategies']['authentication'] = "Ensure GitHub credentials are configured (SSH keys or tokens)"
        
        risks['low_risk'].append("Network connectivity required for remote operations")
        risks['mitigation_strategies']['network'] = "Verify internet connection before remote operations"
        
        print("🔴 High Risk Issues:")
        for risk in risks['high_risk']:
            print(f"  - {risk}")
        
        print("\n🟡 Medium Risk Issues:")
        for risk in risks['medium_risk']:
            print(f"  - {risk}")
        
        print("\n🟢 Low Risk Issues:")
        for risk in risks['low_risk']:
            print(f"  - {risk}")
        
        print("\n🛡️  Mitigation Strategies:")
        for risk_type, strategy in risks['mitigation_strategies'].items():
            print(f"  - {risk_type}: {strategy}")
        
        self.analysis_results['risks'] = risks
        return risks
    
    def create_execution_plan(self) -> Dict[str, Any]:
        """
        Step 4: Create execution plan according to AI Task Orchestrator Guide
        """
        print("\n📋 Step 4: Execution Plan")
        print("=" * 50)
        
        execution_plan = {
            'approach': 'systematic_remote_repository_configuration',
            'steps': [
                {
                    'step': 1,
                    'action': 'Pre-flight Validation',
                    'description': 'Verify Git availability and repository status',
                    'validation': 'All prerequisites met for remote configuration',
                    'estimated_time': '5 minutes'
                },
                {
                    'step': 2,
                    'action': 'Current Remote Analysis',
                    'description': 'Analyze current remote configurations and identify changes needed',
                    'validation': 'Complete inventory of current vs desired remote configurations',
                    'estimated_time': '10 minutes'
                },
                {
                    'step': 3,
                    'action': 'Remote Configuration Updates',
                    'description': 'Update remote URLs for repositories that need changes',
                    'validation': 'All repositories have correct remote URLs configured',
                    'estimated_time': '15 minutes'
                },
                {
                    'step': 4,
                    'action': 'Connectivity Validation',
                    'description': 'Test connectivity to remote repositories',
                    'validation': 'All repositories can fetch from remote successfully',
                    'estimated_time': '10 minutes'
                },
                {
                    'step': 5,
                    'action': 'Comprehensive Reporting',
                    'description': 'Generate detailed report of all remote configurations',
                    'validation': 'Complete documentation of remote repository setup',
                    'estimated_time': '5 minutes'
                }
            ],
            'total_estimated_time': '45 minutes',
            'deliverables': [
                'Remote repository configuration script',
                'Current vs desired remote analysis',
                'Remote configuration update results',
                'Connectivity validation report',
                'Complete remote setup documentation'
            ]
        }
        
        print("📝 Execution Steps:")
        for step in execution_plan['steps']:
            print(f"  Step {step['step']}: {step['action']}")
            print(f"    Description: {step['description']}")
            print(f"    Validation: {step['validation']}")
            print(f"    Time: {step['estimated_time']}")
            print()
        
        print(f"⏱️  Total Estimated Time: {execution_plan['total_estimated_time']}")
        
        print(f"\n📦 Deliverables:")
        for deliverable in execution_plan['deliverables']:
            print(f"  - {deliverable}")
        
        self.analysis_results['execution_plan'] = execution_plan
        return execution_plan
    
    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Generate comprehensive task analysis report
        """
        print("\n📊 Comprehensive Task Analysis Report")
        print("=" * 60)
        
        comprehensive_analysis = {
            'timestamp': datetime.now().isoformat(),
            'task_description': self.task_description,
            'analysis_method': 'AI Task Orchestrator Guide',
            'repository_mappings': self.repository_mappings,
            'complexity_assessment': self.analysis_results.get('complexity', {}),
            'resource_discovery': self.analysis_results.get('resources', {}),
            'risk_assessment': self.analysis_results.get('risks', {}),
            'execution_plan': self.analysis_results.get('execution_plan', {}),
            'recommendations': [
                "Use systematic approach to update remote configurations",
                "Backup current remote configurations before making changes",
                "Test connectivity after each remote configuration update",
                "Implement comprehensive error handling for Git operations",
                "Generate detailed audit trail of all changes made"
            ],
            'next_steps': [
                "Execute Step 1: Pre-flight Validation",
                "Implement remote repository configuration script",
                "Update remote URLs systematically",
                "Validate connectivity to all remote repositories",
                "Generate final configuration report"
            ]
        }
        
        print("🎯 Task Classification:")
        print(f"  Complexity: {comprehensive_analysis['complexity_assessment'].get('complexity_level', 'N/A').upper()}")
        print(f"  Estimated Time: {comprehensive_analysis['complexity_assessment'].get('estimated_effort', {}).get('time', 'N/A')}")
        print(f"  Repositories: {comprehensive_analysis['complexity_assessment'].get('estimated_effort', {}).get('repositories_to_update', 'N/A')}")
        
        print(f"\n🔧 Key Recommendations:")
        for rec in comprehensive_analysis['recommendations']:
            print(f"  - {rec}")
        
        print(f"\n🚀 Next Steps:")
        for step in comprehensive_analysis['next_steps']:
            print(f"  - {step}")
        
        print(f"\n🏭 Repository Mappings:")
        for repo, url in self.repository_mappings.items():
            print(f"  - {repo}: {url}")
        
        # Save analysis report
        report_file = f"remote_repos_task_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(comprehensive_analysis, f, indent=2)
        
        print(f"\n💾 Analysis report saved: {report_file}")
        
        return comprehensive_analysis

def main():
    """Main analysis execution following AI Task Orchestrator Guide"""
    print("🤖 AI Task Orchestrator - Remote Repository Rehosting Analysis")
    print("=" * 70)
    print(f"Analysis started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    analyzer = RemoteRepoTaskAnalyzer()
    
    try:
        # Step 1: Analyze task complexity
        complexity = analyzer.analyze_task_complexity()
        
        # Step 2: Discover available resources
        resources = analyzer.discover_resources()
        
        # Step 3: Assess risks and mitigation strategies
        risks = analyzer.assess_risks()
        
        # Step 4: Create execution plan
        execution_plan = analyzer.create_execution_plan()
        
        # Step 5: Generate comprehensive analysis
        comprehensive_analysis = analyzer.generate_comprehensive_analysis()
        
        print("\n✅ Task Analysis Complete!")
        print(f"Ready to proceed with {execution_plan['approach']} approach")
        print(f"Next: Execute Step 1 - {execution_plan['steps'][0]['action']}")
        
        return comprehensive_analysis
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 