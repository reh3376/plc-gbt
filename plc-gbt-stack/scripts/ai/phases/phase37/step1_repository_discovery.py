#!/usr/bin/env python3
"""
AI Task Orchestrator - Step 1: Repository Discovery and Validation
=================================================================

Following the AI Task Orchestrator Guide execution plan:
Step 1: Repository Discovery and Validation
- Locate all plc-xxx repositories and verify file paths
- Validation: Confirm all 6 repositories exist with .acd files
- Estimated Time: 15 minutes

Task: Work with main .acd files at /Users/reh3376/repos/plc-xxx/plc
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class RepositoryDiscovery:
    """Repository discovery and validation following AI Task Orchestrator methodology"""
    
    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.repository_numbers = [100, 200, 300, 400, 500, 600]
        self.discovery_results = {}
        
    def discover_repositories(self) -> Dict[str, Any]:
        """
        Discover all plc-xxx repositories and validate their structure
        """
        print("🔍 Step 1.1: Repository Discovery")
        print("=" * 50)
        
        repositories = {}
        
        for repo_num in self.repository_numbers:
            repo_name = f"plc-{repo_num}"
            repo_path = self.base_path / repo_name
            
            print(f"\n📁 Checking repository: {repo_name}")
            print(f"   Path: {repo_path}")
            
            repo_info = {
                'name': repo_name,
                'path': str(repo_path),
                'exists': repo_path.exists(),
                'plc_directory': None,
                'acd_files': [],
                'other_files': [],
                'git_lfs_status': 'unknown',
                'validation_status': 'pending'
            }
            
            if repo_path.exists():
                print(f"   ✅ Repository exists")
                
                # Check for plc subdirectory
                plc_path = repo_path / "plc"
                if plc_path.exists():
                    print(f"   ✅ PLC directory exists: {plc_path}")
                    repo_info['plc_directory'] = str(plc_path)
                    
                    # Find all files in plc directory
                    plc_files = list(plc_path.iterdir())
                    print(f"   📋 Files in PLC directory: {len(plc_files)}")
                    
                    for file_path in plc_files:
                        if file_path.is_file():
                            file_info = {
                                'name': file_path.name,
                                'path': str(file_path),
                                'size': file_path.stat().st_size,
                                'extension': file_path.suffix.lower()
                            }
                            
                            if file_path.suffix.lower() in ['.acd']:
                                repo_info['acd_files'].append(file_info)
                                print(f"     📄 ACD file: {file_path.name} ({file_info['size']} bytes)")
                            else:
                                repo_info['other_files'].append(file_info)
                                print(f"     📄 Other file: {file_path.name} ({file_info['size']} bytes)")
                    
                    repo_info['validation_status'] = 'valid' if repo_info['acd_files'] else 'no_acd_files'
                    
                else:
                    print(f"   ❌ PLC directory not found")
                    repo_info['validation_status'] = 'no_plc_directory'
                    
            else:
                print(f"   ❌ Repository does not exist")
                repo_info['validation_status'] = 'not_found'
            
            repositories[repo_name] = repo_info
        
        self.discovery_results['repositories'] = repositories
        return repositories
    
    def analyze_file_content(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 1.2: Analyze file content to detect Git LFS
        """
        print("\n🔍 Step 1.2: File Content Analysis")
        print("=" * 50)
        
        for repo_name, repo_info in repositories.items():
            if repo_info['validation_status'] == 'valid':
                print(f"\n📁 Analyzing {repo_name}")
                
                for acd_file in repo_info['acd_files']:
                    file_path = Path(acd_file['path'])
                    print(f"   📄 Analyzing: {acd_file['name']}")
                    
                    try:
                        # Read first few lines to check for Git LFS
                        with open(file_path, 'r', encoding='utf-8') as f:
                            first_lines = f.read(200)
                        
                        if "git-lfs.github.com" in first_lines:
                            print(f"     🔗 Git LFS pointer detected")
                            acd_file['git_lfs'] = True
                            acd_file['content_type'] = 'lfs_pointer'
                            
                            # Extract LFS information
                            lines = first_lines.split('\n')
                            for line in lines:
                                if line.startswith('oid sha256:'):
                                    acd_file['lfs_oid'] = line.split(':', 1)[1].strip()
                                elif line.startswith('size '):
                                    acd_file['lfs_size'] = int(line.split(' ', 1)[1].strip())
                            
                            print(f"     📊 Actual file size: {acd_file.get('lfs_size', 'unknown')} bytes")
                            
                        else:
                            print(f"     📄 Actual file content detected")
                            acd_file['git_lfs'] = False
                            acd_file['content_type'] = 'actual_content'
                            
                    except Exception as e:
                        print(f"     ❌ Error reading file: {e}")
                        acd_file['git_lfs'] = None
                        acd_file['content_type'] = 'error'
                        acd_file['error'] = str(e)
                
                # Update repository Git LFS status
                lfs_files = [f for f in repo_info['acd_files'] if f.get('git_lfs') == True]
                actual_files = [f for f in repo_info['acd_files'] if f.get('git_lfs') == False]
                
                if lfs_files and not actual_files:
                    repo_info['git_lfs_status'] = 'all_lfs'
                elif lfs_files and actual_files:
                    repo_info['git_lfs_status'] = 'mixed'
                elif actual_files and not lfs_files:
                    repo_info['git_lfs_status'] = 'no_lfs'
                else:
                    repo_info['git_lfs_status'] = 'unknown'
                
                print(f"   📊 Git LFS status: {repo_info['git_lfs_status']}")
        
        return repositories
    
    def validate_discovery_results(self, repositories: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 1.3: Validate discovery results
        """
        print("\n✅ Step 1.3: Validation Results")
        print("=" * 50)
        
        validation_summary = {
            'total_repositories': len(repositories),
            'existing_repositories': 0,
            'repositories_with_plc_dir': 0,
            'repositories_with_acd_files': 0,
            'total_acd_files': 0,
            'lfs_repositories': 0,
            'actual_content_repositories': 0,
            'mixed_repositories': 0,
            'validation_status': 'unknown'
        }
        
        for repo_name, repo_info in repositories.items():
            if repo_info['exists']:
                validation_summary['existing_repositories'] += 1
                
            if repo_info['plc_directory']:
                validation_summary['repositories_with_plc_dir'] += 1
                
            if repo_info['acd_files']:
                validation_summary['repositories_with_acd_files'] += 1
                validation_summary['total_acd_files'] += len(repo_info['acd_files'])
                
            if repo_info['git_lfs_status'] == 'all_lfs':
                validation_summary['lfs_repositories'] += 1
            elif repo_info['git_lfs_status'] == 'no_lfs':
                validation_summary['actual_content_repositories'] += 1
            elif repo_info['git_lfs_status'] == 'mixed':
                validation_summary['mixed_repositories'] += 1
        
        # Determine overall validation status
        if validation_summary['existing_repositories'] == validation_summary['total_repositories']:
            if validation_summary['repositories_with_acd_files'] == validation_summary['total_repositories']:
                validation_summary['validation_status'] = 'all_valid'
            else:
                validation_summary['validation_status'] = 'some_missing_acd'
        else:
            validation_summary['validation_status'] = 'some_missing_repos'
        
        print(f"📊 Validation Summary:")
        print(f"   Total repositories expected: {validation_summary['total_repositories']}")
        print(f"   Existing repositories: {validation_summary['existing_repositories']}")
        print(f"   Repositories with PLC directory: {validation_summary['repositories_with_plc_dir']}")
        print(f"   Repositories with ACD files: {validation_summary['repositories_with_acd_files']}")
        print(f"   Total ACD files found: {validation_summary['total_acd_files']}")
        print(f"   LFS repositories: {validation_summary['lfs_repositories']}")
        print(f"   Actual content repositories: {validation_summary['actual_content_repositories']}")
        print(f"   Mixed repositories: {validation_summary['mixed_repositories']}")
        print(f"   Overall status: {validation_summary['validation_status']}")
        
        # Validation result
        if validation_summary['validation_status'] == 'all_valid':
            print("\n✅ VALIDATION PASSED: All repositories found with ACD files")
        else:
            print(f"\n⚠️  VALIDATION PARTIAL: {validation_summary['validation_status']}")
        
        self.discovery_results['validation_summary'] = validation_summary
        return validation_summary
    
    def generate_discovery_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive discovery report
        """
        print("\n📊 Step 1.4: Discovery Report Generation")
        print("=" * 50)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'step': 'Step 1: Repository Discovery and Validation',
            'task': 'Work with main .acd files at /Users/reh3376/repos/plc-xxx/plc',
            'method': 'AI Task Orchestrator Guide',
            'base_path': str(self.base_path),
            'discovery_results': self.discovery_results,
            'next_steps': [],
            'recommendations': []
        }
        
        # Generate next steps based on results
        validation_summary = self.discovery_results.get('validation_summary', {})
        
        if validation_summary.get('lfs_repositories', 0) > 0:
            report['next_steps'].append("Download files from Git LFS using 'git lfs pull' in each repository")
            report['recommendations'].append("Implement Git LFS handling in processing tools")
        
        if validation_summary.get('actual_content_repositories', 0) > 0:
            report['next_steps'].append("Process actual ACD file content directly")
            report['recommendations'].append("Use enhanced PLCConverter for ACD file analysis")
        
        if validation_summary.get('validation_status') == 'all_valid':
            report['next_steps'].append("Proceed to Step 2: File Content Analysis")
            report['recommendations'].append("Implement comprehensive ACD file processing framework")
        
        print(f"📋 Next Steps:")
        for step in report['next_steps']:
            print(f"   - {step}")
        
        print(f"\n🔧 Recommendations:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
        
        # Save report
        report_file = f"step1_repository_discovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Discovery report saved: {report_file}")
        
        return report

def main():
    """Main execution for Step 1: Repository Discovery and Validation"""
    print("🚀 AI Task Orchestrator - Step 1: Repository Discovery and Validation")
    print("=" * 70)
    print(f"Step 1 started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    discovery = RepositoryDiscovery()
    
    try:
        # Step 1.1: Discover repositories
        repositories = discovery.discover_repositories()
        
        # Step 1.2: Analyze file content
        repositories = discovery.analyze_file_content(repositories)
        
        # Step 1.3: Validate results
        validation_summary = discovery.validate_discovery_results(repositories)
        
        # Step 1.4: Generate report
        report = discovery.generate_discovery_report()
        
        print(f"\n✅ Step 1 Complete!")
        print(f"Status: {validation_summary.get('validation_status', 'unknown')}")
        print(f"Found {validation_summary.get('total_acd_files', 0)} ACD files across {validation_summary.get('repositories_with_acd_files', 0)} repositories")
        
        if validation_summary.get('validation_status') == 'all_valid':
            print("🚀 Ready to proceed to Step 2: File Content Analysis")
        else:
            print("⚠️  Review validation results before proceeding")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Step 1 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 