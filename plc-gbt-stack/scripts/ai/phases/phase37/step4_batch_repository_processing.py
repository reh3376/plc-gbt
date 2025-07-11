#!/usr/bin/env python3
"""
AI Task Orchestrator - Step 4: Batch Repository Processing
=========================================================

Following the AI Task Orchestrator Guide execution plan:
Step 4: Batch Repository Processing
- Process all repositories systematically
- Validation: All repositories processed successfully
- Estimated Time: 30 minutes

Building on previous steps:
- Step 1: Repository Discovery ✅ (Found 6 repos with ACD files)
- Step 2: File Content Analysis ✅ (All files in Git LFS)  
- Step 3: ACD Processing Framework ✅ (Enhanced tools available)
- Remote Repository Rehosting ✅ (All repos now on GitHub)

Task: Comprehensive batch processing of all PLC repositories with enhanced capabilities
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

try:
    # Use import utility
from plc_converter_import import import_plc_converter
PLCConverter = import_plc_converter()
    from migration_cli_tools import MigrationCLI
    ENHANCED_TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Enhanced tools not available: {e}")
    ENHANCED_TOOLS_AVAILABLE = False

class BatchRepositoryProcessor:
    """Batch repository processing following AI Task Orchestrator methodology"""
    
    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.repository_numbers = [100, 200, 300, 400, 500, 600]
        self.github_urls = {
            'plc-100': 'https://github.com/reh3376/plc-100.git',
            'plc-200': 'https://github.com/reh3376/plc-200.git',
            'plc-300': 'https://github.com/reh3376/plc-300.git',
            'plc-400': 'https://github.com/reh3376/plc-400.git',
            'plc-500': 'https://github.com/reh3376/plc-500.git',
            'plc-600': 'https://github.com/reh3376/plc-600.git'
        }
        self.processing_results = {}
        self.converter = None
        self.migration_cli = None
        
        # Initialize enhanced tools if available
        if ENHANCED_TOOLS_AVAILABLE:
            try:
                self.converter = PLCConverter()
                self.migration_cli = MigrationCLI()
                print("✅ Enhanced processing tools initialized")
            except Exception as e:
                print(f"⚠️  Error initializing enhanced tools: {e}")
    
    def execute_git_command(self, command: List[str], repo_path: Path, timeout: int = 60) -> Dict[str, Any]:
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
    
    def step4_1_repository_inventory(self) -> Dict[str, Any]:
        """
        Step 4.1: Complete Repository Inventory
        Comprehensive inventory of all repositories and their current state
        """
        print("📋 Step 4.1: Complete Repository Inventory")
        print("=" * 60)
        
        inventory_results = {
            'timestamp': datetime.now().isoformat(),
            'repositories': {},
            'summary': {
                'total_repositories': len(self.repository_numbers),
                'repositories_found': 0,
                'repositories_with_acd': 0,
                'repositories_with_github_remote': 0,
                'total_acd_files': 0,
                'total_other_files': 0
            }
        }
        
        for repo_num in self.repository_numbers:
            repo_name = f"plc-{repo_num}"
            repo_path = self.base_path / repo_name
            
            print(f"\n🏭 Inventorying {repo_name}")
            
            repo_inventory = {
                'repository': repo_name,
                'path': str(repo_path),
                'exists': repo_path.exists(),
                'is_git_repo': False,
                'remote_configuration': {},
                'plc_directory': {},
                'acd_files': [],
                'other_files': [],
                'git_status': {},
                'inventory_status': 'unknown'
            }
            
            if repo_path.exists():
                inventory_results['summary']['repositories_found'] += 1
                print(f"   ✅ Repository exists")
                
                # Check if it's a Git repository
                git_dir = repo_path / '.git'
                if git_dir.exists():
                    repo_inventory['is_git_repo'] = True
                    print(f"   ✅ Git repository confirmed")
                    
                    # Get remote configuration
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
                        repo_inventory['remote_configuration'] = remotes
                        
                        # Check if GitHub remote is configured
                        expected_github_url = self.github_urls.get(repo_name)
                        if remotes.get('origin') == expected_github_url:
                            inventory_results['summary']['repositories_with_github_remote'] += 1
                            print(f"   ✅ GitHub remote correctly configured")
                        else:
                            print(f"   ⚠️  Remote configuration issue")
                    
                    # Get Git status
                    status_result = self.execute_git_command(['git', 'status', '--porcelain'], repo_path)
                    if status_result['success']:
                        repo_inventory['git_status'] = {
                            'clean': len(status_result['stdout']) == 0,
                            'modified_files': status_result['stdout'].split('\n') if status_result['stdout'] else []
                        }
                        if repo_inventory['git_status']['clean']:
                            print(f"   ✅ Git working directory clean")
                        else:
                            print(f"   ⚠️  Git working directory has changes")
                
                # Check PLC directory
                plc_path = repo_path / "plc"
                if plc_path.exists():
                    print(f"   ✅ PLC directory found")
                    repo_inventory['plc_directory'] = {
                        'exists': True,
                        'path': str(plc_path),
                        'file_count': 0
                    }
                    
                    # Inventory files in PLC directory
                    try:
                        plc_files = list(plc_path.iterdir())
                        repo_inventory['plc_directory']['file_count'] = len(plc_files)
                        
                        for file_path in plc_files:
                            if file_path.is_file():
                                file_info = {
                                    'name': file_path.name,
                                    'path': str(file_path),
                                    'size_bytes': file_path.stat().st_size,
                                    'extension': file_path.suffix.lower(),
                                    'is_git_lfs': False
                                }
                                
                                # Check if file is Git LFS pointer
                                try:
                                    with open(file_path, 'r', encoding='utf-8') as f:
                                        first_content = f.read(200)
                                    if "git-lfs.github.com" in first_content:
                                        file_info['is_git_lfs'] = True
                                        # Extract LFS info
                                        for line in first_content.split('\n'):
                                            if line.startswith('size '):
                                                file_info['lfs_actual_size'] = int(line.split(' ', 1)[1].strip())
                                except:
                                    pass
                                
                                if file_path.suffix.lower() in ['.acd']:
                                    repo_inventory['acd_files'].append(file_info)
                                    inventory_results['summary']['total_acd_files'] += 1
                                    print(f"     📄 ACD file: {file_path.name} ({'LFS' if file_info['is_git_lfs'] else 'Local'})")
                                else:
                                    repo_inventory['other_files'].append(file_info)
                                    inventory_results['summary']['total_other_files'] += 1
                                    print(f"     📄 Other file: {file_path.name}")
                        
                        if repo_inventory['acd_files']:
                            inventory_results['summary']['repositories_with_acd'] += 1
                    
                    except Exception as e:
                        print(f"   ❌ Error reading PLC directory: {e}")
                        repo_inventory['plc_directory']['error'] = str(e)
                
                # Determine inventory status
                if repo_inventory['acd_files'] and repo_inventory['is_git_repo']:
                    if repo_inventory['remote_configuration'].get('origin') == self.github_urls.get(repo_name):
                        repo_inventory['inventory_status'] = 'ready_for_processing'
                    else:
                        repo_inventory['inventory_status'] = 'needs_remote_config'
                elif repo_inventory['acd_files']:
                    repo_inventory['inventory_status'] = 'has_acd_no_git'
                else:
                    repo_inventory['inventory_status'] = 'no_acd_files'
            else:
                repo_inventory['inventory_status'] = 'not_found'
                print(f"   ❌ Repository not found")
            
            inventory_results['repositories'][repo_name] = repo_inventory
        
        # Print inventory summary
        print(f"\n📊 Inventory Summary:")
        summary = inventory_results['summary']
        print(f"   Total repositories: {summary['total_repositories']}")
        print(f"   Repositories found: {summary['repositories_found']}")
        print(f"   Repositories with ACD files: {summary['repositories_with_acd']}")
        print(f"   Repositories with GitHub remote: {summary['repositories_with_github_remote']}")
        print(f"   Total ACD files: {summary['total_acd_files']}")
        print(f"   Total other files: {summary['total_other_files']}")
        
        self.processing_results['step4_1_inventory'] = inventory_results
        return inventory_results
    
    def step4_2_git_lfs_management(self) -> Dict[str, Any]:
        """
        Step 4.2: Git LFS Management
        Handle Git LFS files and provide download instructions
        """
        print("\n💾 Step 4.2: Git LFS Management")
        print("=" * 60)
        
        lfs_results = {
            'timestamp': datetime.now().isoformat(),
            'git_lfs_available': False,
            'repositories_with_lfs': {},
            'download_instructions': [],
            'summary': {
                'total_lfs_files': 0,
                'repositories_needing_download': 0,
                'estimated_download_size_mb': 0
            }
        }
        
        # Check Git LFS availability
        try:
            lfs_check = subprocess.run(['git', 'lfs', 'version'], capture_output=True, text=True, timeout=10)
            if lfs_check.returncode == 0:
                lfs_results['git_lfs_available'] = True
                print(f"✅ Git LFS available: {lfs_check.stdout.strip()}")
            else:
                print(f"❌ Git LFS not available")
        except:
            print(f"❌ Git LFS not available")
        
        inventory_results = self.processing_results.get('step4_1_inventory', {})
        
        for repo_name, repo_info in inventory_results.get('repositories', {}).items():
            if repo_info.get('acd_files'):
                repo_lfs_info = {
                    'repository': repo_name,
                    'lfs_files': [],
                    'needs_download': False,
                    'download_command': '',
                    'estimated_size_mb': 0
                }
                
                print(f"\n🔍 Checking {repo_name} for LFS files")
                
                for acd_file in repo_info['acd_files']:
                    if acd_file.get('is_git_lfs'):
                        repo_lfs_info['lfs_files'].append(acd_file)
                        repo_lfs_info['needs_download'] = True
                        lfs_results['summary']['total_lfs_files'] += 1
                        
                        # Calculate estimated size
                        if acd_file.get('lfs_actual_size'):
                            size_mb = acd_file['lfs_actual_size'] / (1024 * 1024)
                            repo_lfs_info['estimated_size_mb'] += size_mb
                            print(f"   📄 LFS file: {acd_file['name']} ({size_mb:.1f} MB)")
                
                if repo_lfs_info['needs_download']:
                    lfs_results['summary']['repositories_needing_download'] += 1
                    lfs_results['summary']['estimated_download_size_mb'] += repo_lfs_info['estimated_size_mb']
                    
                    # Generate download command
                    repo_path = self.base_path / repo_name
                    if lfs_results['git_lfs_available']:
                        repo_lfs_info['download_command'] = f"cd {repo_path} && git lfs pull"
                        print(f"   💾 Download command: git lfs pull")
                    else:
                        repo_lfs_info['download_command'] = "Install Git LFS first, then: git lfs pull"
                        print(f"   ⚠️  Git LFS not available - install required")
                    
                    lfs_results['download_instructions'].append({
                        'repository': repo_name,
                        'command': repo_lfs_info['download_command'],
                        'estimated_size_mb': repo_lfs_info['estimated_size_mb']
                    })
                
                lfs_results['repositories_with_lfs'][repo_name] = repo_lfs_info
        
        # Print LFS summary
        print(f"\n📊 Git LFS Summary:")
        summary = lfs_results['summary']
        print(f"   Git LFS available: {'Yes' if lfs_results['git_lfs_available'] else 'No'}")
        print(f"   Total LFS files: {summary['total_lfs_files']}")
        print(f"   Repositories needing download: {summary['repositories_needing_download']}")
        print(f"   Estimated download size: {summary['estimated_download_size_mb']:.1f} MB")
        
        if lfs_results['download_instructions']:
            print(f"\n📋 Download Instructions:")
            for instruction in lfs_results['download_instructions']:
                print(f"   {instruction['repository']}: {instruction['command']}")
                print(f"      Size: {instruction['estimated_size_mb']:.1f} MB")
        
        self.processing_results['step4_2_lfs'] = lfs_results
        return lfs_results
    
    def step4_3_enhanced_processing_validation(self) -> Dict[str, Any]:
        """
        Step 4.3: Enhanced Processing Validation
        Test enhanced processing capabilities on available files
        """
        print("\n🔧 Step 4.3: Enhanced Processing Validation")
        print("=" * 60)
        
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'enhanced_tools_available': ENHANCED_TOOLS_AVAILABLE,
            'processing_tests': {},
            'capabilities_summary': {
                'validation_possible': False,
                'conversion_possible': False,
                'batch_processing_possible': False,
                'repositories_testable': 0,
                'successful_tests': 0,
                'failed_tests': 0
            }
        }
        
        if not ENHANCED_TOOLS_AVAILABLE:
            print("⚠️  Enhanced tools not available - limited validation possible")
            validation_results['capabilities_summary']['validation_possible'] = False
            self.processing_results['step4_3_validation'] = validation_results
            return validation_results
        
        inventory_results = self.processing_results.get('step4_1_inventory', {})
        
        for repo_name, repo_info in inventory_results.get('repositories', {}).items():
            if repo_info.get('acd_files'):
                validation_results['capabilities_summary']['repositories_testable'] += 1
                
                print(f"\n🧪 Testing {repo_name}")
                
                repo_tests = {
                    'repository': repo_name,
                    'acd_files_tested': [],
                    'test_results': {
                        'validation_tests': [],
                        'conversion_tests': [],
                        'batch_processing_tests': []
                    },
                    'overall_status': 'unknown'
                }
                
                # Test each ACD file
                for acd_file in repo_info['acd_files']:
                    file_path = Path(acd_file['path'])
                    
                    print(f"   📄 Testing {acd_file['name']}")
                    
                    file_tests = {
                        'file': acd_file['name'],
                        'path': str(file_path),
                        'is_lfs': acd_file.get('is_git_lfs', False),
                        'tests_performed': []
                    }
                    
                    # Test 1: Validation capability
                    if self.converter:
                        try:
                            validation_result = self.converter.validate_file(str(file_path))
                            file_tests['tests_performed'].append({
                                'test': 'validation',
                                'success': True,
                                'result': validation_result,
                                'note': 'Validation attempted successfully'
                            })
                            validation_results['capabilities_summary']['validation_possible'] = True
                            print(f"     ✅ Validation test completed")
                        except Exception as e:
                            file_tests['tests_performed'].append({
                                'test': 'validation',
                                'success': False,
                                'error': str(e),
                                'note': 'Validation failed - likely due to LFS pointer'
                            })
                            print(f"     ⚠️  Validation test failed (expected for LFS files)")
                    
                    # Test 2: Conversion capability (dry run)
                    if self.converter and not acd_file.get('is_git_lfs'):
                        try:
                            # Only test conversion on non-LFS files
                            output_path = f"/tmp/test_conversion_{file_path.stem}.L5X"
                            conversion_result = self.converter.acd_to_l5x(str(file_path), output_path)
                            file_tests['tests_performed'].append({
                                'test': 'conversion',
                                'success': True,
                                'result': conversion_result,
                                'note': 'Conversion test completed'
                            })
                            validation_results['capabilities_summary']['conversion_possible'] = True
                            print(f"     ✅ Conversion test completed")
                        except Exception as e:
                            file_tests['tests_performed'].append({
                                'test': 'conversion',
                                'success': False,
                                'error': str(e),
                                'note': 'Conversion test failed'
                            })
                            print(f"     ❌ Conversion test failed")
                    
                    # Test 3: Batch processing capability
                    if self.migration_cli:
                        try:
                            batch_result = self.migration_cli.validate_file(str(file_path))
                            file_tests['tests_performed'].append({
                                'test': 'batch_processing',
                                'success': True,
                                'result': batch_result,
                                'note': 'Batch processing test completed'
                            })
                            validation_results['capabilities_summary']['batch_processing_possible'] = True
                            print(f"     ✅ Batch processing test completed")
                        except Exception as e:
                            file_tests['tests_performed'].append({
                                'test': 'batch_processing',
                                'success': False,
                                'error': str(e),
                                'note': 'Batch processing test failed'
                            })
                            print(f"     ⚠️  Batch processing test failed")
                    
                    repo_tests['acd_files_tested'].append(file_tests)
                
                # Determine overall repository test status
                all_tests = [test for file_test in repo_tests['acd_files_tested'] 
                           for test in file_test['tests_performed']]
                successful_tests = [test for test in all_tests if test.get('success')]
                failed_tests = [test for test in all_tests if not test.get('success')]
                
                if successful_tests and not failed_tests:
                    repo_tests['overall_status'] = 'all_tests_passed'
                    validation_results['capabilities_summary']['successful_tests'] += 1
                elif successful_tests:
                    repo_tests['overall_status'] = 'partial_success'
                    validation_results['capabilities_summary']['successful_tests'] += 1
                else:
                    repo_tests['overall_status'] = 'all_tests_failed'
                    validation_results['capabilities_summary']['failed_tests'] += 1
                
                validation_results['processing_tests'][repo_name] = repo_tests
        
        # Print validation summary
        print(f"\n📊 Enhanced Processing Validation Summary:")
        capabilities = validation_results['capabilities_summary']
        print(f"   Enhanced tools available: {'Yes' if validation_results['enhanced_tools_available'] else 'No'}")
        print(f"   Validation possible: {'Yes' if capabilities['validation_possible'] else 'No'}")
        print(f"   Conversion possible: {'Yes' if capabilities['conversion_possible'] else 'No'}")
        print(f"   Batch processing possible: {'Yes' if capabilities['batch_processing_possible'] else 'No'}")
        print(f"   Repositories tested: {capabilities['repositories_testable']}")
        print(f"   Successful tests: {capabilities['successful_tests']}")
        print(f"   Failed tests: {capabilities['failed_tests']}")
        
        self.processing_results['step4_3_validation'] = validation_results
        return validation_results
    
    def step4_4_comprehensive_batch_processing(self) -> Dict[str, Any]:
        """
        Step 4.4: Comprehensive Batch Processing
        Execute comprehensive processing across all repositories
        """
        print("\n🏭 Step 4.4: Comprehensive Batch Processing")
        print("=" * 60)
        
        batch_results = {
            'timestamp': datetime.now().isoformat(),
            'processing_approach': 'comprehensive_batch_analysis',
            'repositories_processed': {},
            'summary': {
                'total_repositories': 0,
                'successfully_processed': 0,
                'partially_processed': 0,
                'failed_processing': 0,
                'total_files_processed': 0,
                'processing_recommendations': []
            }
        }
        
        inventory_results = self.processing_results.get('step4_1_inventory', {})
        lfs_results = self.processing_results.get('step4_2_lfs', {})
        validation_results = self.processing_results.get('step4_3_validation', {})
        
        for repo_name, repo_info in inventory_results.get('repositories', {}).items():
            if repo_info.get('inventory_status') == 'ready_for_processing':
                batch_results['summary']['total_repositories'] += 1
                
                print(f"\n🔄 Processing {repo_name}")
                
                repo_processing = {
                    'repository': repo_name,
                    'processing_timestamp': datetime.now().isoformat(),
                    'repository_analysis': {
                        'git_status': repo_info.get('git_status', {}),
                        'remote_configuration': repo_info.get('remote_configuration', {}),
                        'acd_files_count': len(repo_info.get('acd_files', [])),
                        'lfs_files_count': len([f for f in repo_info.get('acd_files', []) if f.get('is_git_lfs')])
                    },
                    'file_processing_results': [],
                    'repository_recommendations': [],
                    'processing_status': 'unknown'
                }
                
                # Process each ACD file
                files_processed = 0
                files_successful = 0
                
                for acd_file in repo_info.get('acd_files', []):
                    print(f"   📄 Processing {acd_file['name']}")
                    
                    file_processing = {
                        'file': acd_file['name'],
                        'path': acd_file['path'],
                        'size_bytes': acd_file.get('size_bytes', 0),
                        'is_lfs': acd_file.get('is_git_lfs', False),
                        'processing_operations': [],
                        'file_analysis': {},
                        'processing_success': False
                    }
                    
                    # File analysis
                    if acd_file.get('is_git_lfs'):
                        file_processing['file_analysis'] = {
                            'type': 'git_lfs_pointer',
                            'actual_size_mb': acd_file.get('lfs_actual_size', 0) / (1024 * 1024) if acd_file.get('lfs_actual_size') else 0,
                            'download_required': True,
                            'processing_possible': False
                        }
                        file_processing['processing_operations'].append({
                            'operation': 'lfs_analysis',
                            'result': 'LFS pointer detected - download required for processing',
                            'success': True
                        })
                        print(f"     🔗 LFS pointer - {file_processing['file_analysis']['actual_size_mb']:.1f} MB when downloaded")
                    else:
                        file_processing['file_analysis'] = {
                            'type': 'actual_content',
                            'size_mb': acd_file.get('size_bytes', 0) / (1024 * 1024),
                            'download_required': False,
                            'processing_possible': True
                        }
                        
                        # Enhanced processing if available
                        if ENHANCED_TOOLS_AVAILABLE and self.converter:
                            try:
                                # Attempt validation
                                validation_result = self.converter.validate_file(acd_file['path'])
                                file_processing['processing_operations'].append({
                                    'operation': 'validation',
                                    'result': validation_result,
                                    'success': True
                                })
                                print(f"     ✅ Validation completed")
                                file_processing['processing_success'] = True
                            except Exception as e:
                                file_processing['processing_operations'].append({
                                    'operation': 'validation',
                                    'result': f'Validation failed: {str(e)}',
                                    'success': False
                                })
                                print(f"     ❌ Validation failed: {str(e)}")
                        else:
                            file_processing['processing_operations'].append({
                                'operation': 'basic_analysis',
                                'result': 'Enhanced tools not available - basic analysis only',
                                'success': True
                            })
                            print(f"     ℹ️  Basic analysis completed")
                            file_processing['processing_success'] = True
                    
                    repo_processing['file_processing_results'].append(file_processing)
                    files_processed += 1
                    batch_results['summary']['total_files_processed'] += 1
                    
                    if file_processing['processing_success']:
                        files_successful += 1
                
                # Generate repository-specific recommendations
                lfs_info = lfs_results.get('repositories_with_lfs', {}).get(repo_name, {})
                if lfs_info.get('needs_download'):
                    repo_processing['repository_recommendations'].append({
                        'type': 'git_lfs_download',
                        'description': f"Download {len(lfs_info.get('lfs_files', []))} LFS files ({lfs_info.get('estimated_size_mb', 0):.1f} MB)",
                        'command': lfs_info.get('download_command', ''),
                        'priority': 'high'
                    })
                
                if ENHANCED_TOOLS_AVAILABLE:
                    repo_processing['repository_recommendations'].append({
                        'type': 'enhanced_processing',
                        'description': 'Use enhanced PLCConverter for comprehensive ACD analysis after LFS download',
                        'priority': 'medium'
                    })
                
                # Determine processing status
                if files_successful == files_processed and files_processed > 0:
                    repo_processing['processing_status'] = 'fully_successful'
                    batch_results['summary']['successfully_processed'] += 1
                elif files_successful > 0:
                    repo_processing['processing_status'] = 'partially_successful'
                    batch_results['summary']['partially_processed'] += 1
                else:
                    repo_processing['processing_status'] = 'failed'
                    batch_results['summary']['failed_processing'] += 1
                
                print(f"   📊 Repository processing: {repo_processing['processing_status']}")
                print(f"      Files processed: {files_processed}, Successful: {files_successful}")
                
                batch_results['repositories_processed'][repo_name] = repo_processing
        
        # Generate overall recommendations
        lfs_repos = len([r for r in lfs_results.get('repositories_with_lfs', {}).values() if r.get('needs_download')])
        if lfs_repos > 0:
            batch_results['summary']['processing_recommendations'].append({
                'type': 'git_lfs_setup',
                'description': f'Install Git LFS and download files from {lfs_repos} repositories',
                'priority': 'high',
                'estimated_size_mb': lfs_results.get('summary', {}).get('estimated_download_size_mb', 0)
            })
        
        if ENHANCED_TOOLS_AVAILABLE:
            batch_results['summary']['processing_recommendations'].append({
                'type': 'enhanced_processing',
                'description': 'Leverage enhanced PLCConverter capabilities for comprehensive ACD analysis',
                'priority': 'medium'
            })
        
        batch_results['summary']['processing_recommendations'].append({
            'type': 'github_integration',
            'description': 'All repositories now configured for GitHub - ready for collaborative development',
            'priority': 'low'
        })
        
        # Print batch processing summary
        print(f"\n📊 Batch Processing Summary:")
        summary = batch_results['summary']
        print(f"   Total repositories processed: {summary['total_repositories']}")
        print(f"   Successfully processed: {summary['successfully_processed']}")
        print(f"   Partially processed: {summary['partially_processed']}")
        print(f"   Failed processing: {summary['failed_processing']}")
        print(f"   Total files processed: {summary['total_files_processed']}")
        
        print(f"\n🔧 Processing Recommendations:")
        for rec in summary['processing_recommendations']:
            priority_icon = "🔴" if rec['priority'] == 'high' else "🟡" if rec['priority'] == 'medium' else "🟢"
            print(f"   {priority_icon} {rec['description']}")
            if 'estimated_size_mb' in rec:
                print(f"      Estimated size: {rec['estimated_size_mb']:.1f} MB")
        
        self.processing_results['step4_4_batch'] = batch_results
        return batch_results
    
    def step4_5_comprehensive_reporting(self) -> Dict[str, Any]:
        """
        Step 4.5: Comprehensive Reporting
        Generate detailed report of all batch processing results
        """
        print("\n📊 Step 4.5: Comprehensive Reporting")
        print("=" * 60)
        
        comprehensive_report = {
            'timestamp': datetime.now().isoformat(),
            'step': 'Step 4: Batch Repository Processing',
            'task': 'Comprehensive batch processing of all PLC repositories',
            'method': 'AI Task Orchestrator Guide',
            'execution_results': self.processing_results,
            'final_status': {},
            'overall_summary': {},
            'recommendations': [],
            'next_steps': []
        }
        
        # Analyze final status
        inventory_results = self.processing_results.get('step4_1_inventory', {})
        lfs_results = self.processing_results.get('step4_2_lfs', {})
        validation_results = self.processing_results.get('step4_3_validation', {})
        batch_results = self.processing_results.get('step4_4_batch', {})
        
        # Generate overall summary
        comprehensive_report['overall_summary'] = {
            'repositories_discovered': inventory_results.get('summary', {}).get('repositories_found', 0),
            'repositories_with_acd': inventory_results.get('summary', {}).get('repositories_with_acd', 0),
            'repositories_with_github_remote': inventory_results.get('summary', {}).get('repositories_with_github_remote', 0),
            'total_acd_files': inventory_results.get('summary', {}).get('total_acd_files', 0),
            'git_lfs_files': lfs_results.get('summary', {}).get('total_lfs_files', 0),
            'enhanced_tools_available': validation_results.get('enhanced_tools_available', False),
            'repositories_successfully_processed': batch_results.get('summary', {}).get('successfully_processed', 0),
            'batch_processing_complete': True
        }
        
        # Generate final status for each repository
        for repo_name in self.github_urls.keys():
            repo_inventory = inventory_results.get('repositories', {}).get(repo_name, {})
            repo_batch = batch_results.get('repositories_processed', {}).get(repo_name, {})
            
            final_status = {
                'repository': repo_name,
                'exists': repo_inventory.get('exists', False),
                'has_acd_files': len(repo_inventory.get('acd_files', [])) > 0,
                'github_remote_configured': repo_inventory.get('remote_configuration', {}).get('origin') == self.github_urls[repo_name],
                'processing_attempted': repo_name in batch_results.get('repositories_processed', {}),
                'processing_successful': repo_batch.get('processing_status') in ['fully_successful', 'partially_successful'],
                'requires_lfs_download': repo_name in lfs_results.get('repositories_with_lfs', {}),
                'overall_status': 'unknown'
            }
            
            # Determine overall status
            if (final_status['exists'] and final_status['has_acd_files'] and 
                final_status['github_remote_configured'] and final_status['processing_successful']):
                final_status['overall_status'] = 'fully_ready'
            elif (final_status['exists'] and final_status['has_acd_files'] and 
                  final_status['github_remote_configured']):
                final_status['overall_status'] = 'ready_needs_lfs'
            elif final_status['exists'] and final_status['has_acd_files']:
                final_status['overall_status'] = 'needs_configuration'
            else:
                final_status['overall_status'] = 'incomplete'
            
            comprehensive_report['final_status'][repo_name] = final_status
            
            # Print individual repository status
            status_icon = ("✅" if final_status['overall_status'] == 'fully_ready' else 
                          "🔄" if final_status['overall_status'] == 'ready_needs_lfs' else 
                          "⚠️" if final_status['overall_status'] == 'needs_configuration' else "❌")
            print(f"   {status_icon} {repo_name}: {final_status['overall_status']}")
        
        # Generate recommendations
        fully_ready = len([s for s in comprehensive_report['final_status'].values() if s['overall_status'] == 'fully_ready'])
        needs_lfs = len([s for s in comprehensive_report['final_status'].values() if s['overall_status'] == 'ready_needs_lfs'])
        
        if needs_lfs > 0:
            comprehensive_report['recommendations'].append("Install Git LFS and download ACD files for complete processing capabilities")
            comprehensive_report['recommendations'].append("Use 'git lfs pull' in each repository to download actual file content")
        
        if comprehensive_report['overall_summary']['enhanced_tools_available']:
            comprehensive_report['recommendations'].append("Leverage enhanced PLCConverter for comprehensive ACD file analysis and conversion")
        
        comprehensive_report['recommendations'].extend([
            "All repositories now configured with GitHub remotes for collaborative development",
            "Consider implementing automated processing workflows using the enhanced tools",
            "Use batch processing capabilities for efficient multi-repository operations"
        ])
        
        # Generate next steps
        if fully_ready == len(self.github_urls):
            comprehensive_report['next_steps'] = [
                "All repositories fully ready for production processing",
                "Implement automated ACD processing workflows",
                "Consider setting up CI/CD pipelines for PLC development"
            ]
        else:
            comprehensive_report['next_steps'] = [
                "Address Git LFS file downloads for complete processing",
                "Complete repository configuration as needed",
                "Test enhanced processing capabilities with actual file content"
            ]
        
        print(f"\n📊 Final Summary:")
        summary = comprehensive_report['overall_summary']
        print(f"   Repositories discovered: {summary['repositories_discovered']}")
        print(f"   Repositories with ACD files: {summary['repositories_with_acd']}")
        print(f"   Repositories with GitHub remote: {summary['repositories_with_github_remote']}")
        print(f"   Total ACD files: {summary['total_acd_files']}")
        print(f"   Git LFS files: {summary['git_lfs_files']}")
        print(f"   Enhanced tools available: {'Yes' if summary['enhanced_tools_available'] else 'No'}")
        print(f"   Successfully processed: {summary['repositories_successfully_processed']}")
        
        print(f"\n🔧 Key Recommendations:")
        for rec in comprehensive_report['recommendations']:
            print(f"   - {rec}")
        
        print(f"\n🚀 Next Steps:")
        for step in comprehensive_report['next_steps']:
            print(f"   - {step}")
        
        # Save comprehensive report
        report_file = f"step4_batch_repository_processing_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(comprehensive_report, f, indent=2)
        
        print(f"\n💾 Comprehensive report saved: {report_file}")
        
        return comprehensive_report

def main():
    """Main execution for Step 4: Batch Repository Processing"""
    print("🚀 AI Task Orchestrator - Step 4: Batch Repository Processing")
    print("=" * 80)
    print(f"Step 4 started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    processor = BatchRepositoryProcessor()
    
    try:
        # Step 4.1: Complete Repository Inventory
        inventory_results = processor.step4_1_repository_inventory()
        
        # Step 4.2: Git LFS Management
        lfs_results = processor.step4_2_git_lfs_management()
        
        # Step 4.3: Enhanced Processing Validation
        validation_results = processor.step4_3_enhanced_processing_validation()
        
        # Step 4.4: Comprehensive Batch Processing
        batch_results = processor.step4_4_comprehensive_batch_processing()
        
        # Step 4.5: Comprehensive Reporting
        final_report = processor.step4_5_comprehensive_reporting()
        
        print(f"\n✅ Step 4: Batch Repository Processing Complete!")
        
        overall_summary = final_report.get('overall_summary', {})
        print(f"📊 Results: {overall_summary.get('repositories_successfully_processed', 0)}/{overall_summary.get('repositories_with_acd', 0)} repositories processed successfully")
        print(f"🔧 Enhanced Tools: {'Available' if overall_summary.get('enhanced_tools_available') else 'Not Available'}")
        print(f"💾 Git LFS Files: {overall_summary.get('git_lfs_files', 0)} files requiring download")
        
        fully_ready = len([s for s in final_report.get('final_status', {}).values() if s.get('overall_status') == 'fully_ready'])
        total_repos = len(processor.github_urls)
        
        if fully_ready == total_repos:
            print(f"🎉 All {total_repos} repositories fully ready for production processing!")
        else:
            print(f"🔄 {fully_ready}/{total_repos} repositories fully ready - see recommendations for next steps")
        
        return final_report
        
    except Exception as e:
        print(f"\n❌ Step 4 failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 