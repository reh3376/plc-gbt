#!/usr/bin/env python3
"""
Git LFS Download Script for PLC Repositories
===========================================

This script downloads Git LFS files from all PLC repositories as recommended
by the AI Task Orchestrator analysis.

Based on Step 3 findings:
- All 6 repositories have ACD files stored in Git LFS
- Files need to be downloaded for actual processing
- Total actual file sizes: ~36MB across all repositories
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class GitLFSDownloader:
    """Download Git LFS files from PLC repositories"""
    
    def __init__(self):
        self.base_path = Path("/Users/reh3376/repos")
        self.repository_numbers = [100, 200, 300, 400, 500, 600]
        self.download_results = {}
        
    def check_git_lfs_availability(self) -> bool:
        """Check if Git LFS is available"""
        try:
            result = subprocess.run(['git', 'lfs', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ Git LFS available: {result.stdout.strip()}")
                return True
            else:
                print(f"❌ Git LFS not available: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error checking Git LFS: {e}")
            return False
    
    def download_repository_lfs(self, repo_num: int) -> Dict[str, Any]:
        """Download Git LFS files for a specific repository"""
        repo_name = f"plc-{repo_num}"
        repo_path = self.base_path / repo_name
        
        print(f"\n🔄 Processing {repo_name}")
        print(f"   Path: {repo_path}")
        
        result = {
            'repository': repo_name,
            'path': str(repo_path),
            'timestamp': datetime.now().isoformat(),
            'lfs_status': 'unknown',
            'download_attempted': False,
            'download_successful': False,
            'files_downloaded': [],
            'errors': []
        }
        
        if not repo_path.exists():
            result['errors'].append('Repository directory does not exist')
            return result
        
        if not (repo_path / '.git').exists():
            result['errors'].append('Not a Git repository')
            return result
        
        try:
            # Check LFS status
            print(f"   🔍 Checking LFS status...")
            lfs_ls_result = subprocess.run(['git', 'lfs', 'ls-files'], 
                                         cwd=repo_path, capture_output=True, text=True, timeout=30)
            
            if lfs_ls_result.returncode == 0:
                lfs_files = lfs_ls_result.stdout.strip().split('\n') if lfs_ls_result.stdout.strip() else []
                lfs_files = [f for f in lfs_files if f.strip()]  # Remove empty lines
                
                if lfs_files:
                    print(f"   📄 Found {len(lfs_files)} LFS files:")
                    for lfs_file in lfs_files:
                        print(f"      - {lfs_file}")
                    
                    result['lfs_status'] = 'has_lfs_files'
                    result['lfs_files'] = lfs_files
                    
                    # Attempt to download LFS files
                    print(f"   ⬇️  Downloading LFS files...")
                    result['download_attempted'] = True
                    
                    lfs_pull_result = subprocess.run(['git', 'lfs', 'pull'], 
                                                   cwd=repo_path, capture_output=True, text=True, timeout=300)
                    
                    if lfs_pull_result.returncode == 0:
                        print(f"   ✅ LFS download successful")
                        result['download_successful'] = True
                        result['download_output'] = lfs_pull_result.stdout
                        
                        # Verify files were downloaded
                        plc_path = repo_path / 'plc'
                        if plc_path.exists():
                            acd_files = list(plc_path.glob("*.ACD")) + list(plc_path.glob("*.acd"))
                            for acd_file in acd_files:
                                if acd_file.exists():
                                    file_size = acd_file.stat().st_size
                                    # Check if it's still a pointer (small file) or actual content
                                    if file_size > 1000:  # Actual files should be much larger
                                        result['files_downloaded'].append({
                                            'file': acd_file.name,
                                            'size_bytes': file_size,
                                            'size_mb': round(file_size / (1024 * 1024), 2)
                                        })
                                        print(f"      ✅ {acd_file.name}: {round(file_size / (1024 * 1024), 2)} MB")
                                    else:
                                        print(f"      ⚠️  {acd_file.name}: Still appears to be LFS pointer")
                    else:
                        print(f"   ❌ LFS download failed: {lfs_pull_result.stderr}")
                        result['errors'].append(f"LFS pull failed: {lfs_pull_result.stderr}")
                        
                else:
                    print(f"   ℹ️  No LFS files found")
                    result['lfs_status'] = 'no_lfs_files'
                    
            else:
                print(f"   ❌ Error checking LFS status: {lfs_ls_result.stderr}")
                result['errors'].append(f"LFS ls-files failed: {lfs_ls_result.stderr}")
                
        except subprocess.TimeoutExpired:
            result['errors'].append('Git LFS operation timed out')
            print(f"   ❌ Operation timed out")
        except Exception as e:
            result['errors'].append(f'Unexpected error: {str(e)}')
            print(f"   ❌ Unexpected error: {e}")
        
        return result
    
    def download_all_repositories(self) -> Dict[str, Any]:
        """Download Git LFS files from all repositories"""
        print("🔄 Git LFS Download for All PLC Repositories")
        print("=" * 60)
        
        # Check Git LFS availability
        if not self.check_git_lfs_availability():
            return {
                'error': 'Git LFS not available',
                'timestamp': datetime.now().isoformat(),
                'repositories': {}
            }
        
        all_results = {
            'timestamp': datetime.now().isoformat(),
            'git_lfs_available': True,
            'repositories': {},
            'summary': {
                'total_repositories': len(self.repository_numbers),
                'repositories_processed': 0,
                'repositories_with_lfs': 0,
                'successful_downloads': 0,
                'failed_downloads': 0,
                'total_files_downloaded': 0,
                'total_mb_downloaded': 0
            }
        }
        
        # Process each repository
        for repo_num in self.repository_numbers:
            repo_result = self.download_repository_lfs(repo_num)
            all_results['repositories'][f"plc-{repo_num}"] = repo_result
            
            # Update summary
            all_results['summary']['repositories_processed'] += 1
            
            if repo_result['lfs_status'] == 'has_lfs_files':
                all_results['summary']['repositories_with_lfs'] += 1
                
            if repo_result['download_successful']:
                all_results['summary']['successful_downloads'] += 1
                all_results['summary']['total_files_downloaded'] += len(repo_result['files_downloaded'])
                all_results['summary']['total_mb_downloaded'] += sum(
                    f['size_mb'] for f in repo_result['files_downloaded']
                )
            elif repo_result['download_attempted']:
                all_results['summary']['failed_downloads'] += 1
        
        # Print summary
        print(f"\n📊 Download Summary")
        print("=" * 40)
        summary = all_results['summary']
        print(f"Total repositories: {summary['total_repositories']}")
        print(f"Repositories with LFS: {summary['repositories_with_lfs']}")
        print(f"Successful downloads: {summary['successful_downloads']}")
        print(f"Failed downloads: {summary['failed_downloads']}")
        print(f"Total files downloaded: {summary['total_files_downloaded']}")
        print(f"Total MB downloaded: {summary['total_mb_downloaded']:.2f} MB")
        
        if summary['successful_downloads'] == summary['repositories_with_lfs']:
            print(f"\n✅ All Git LFS downloads completed successfully!")
        else:
            print(f"\n⚠️  Some downloads failed - check individual repository results")
        
        self.download_results = all_results
        return all_results
    
    def generate_download_report(self) -> Dict[str, Any]:
        """Generate comprehensive download report"""
        print(f"\n📊 Download Report Generation")
        print("=" * 40)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'operation': 'Git LFS Download for PLC Repositories',
            'method': 'AI Task Orchestrator - Step 3 Recommendation',
            'download_results': self.download_results,
            'next_steps': [],
            'recommendations': []
        }
        
        summary = self.download_results.get('summary', {})
        
        # Generate next steps based on results
        if summary.get('successful_downloads', 0) > 0:
            report['next_steps'].append("Proceed with ACD file processing using actual file content")
            report['next_steps'].append("Run Step 4: Batch Repository Processing")
            report['recommendations'].append("Verify file integrity before processing")
        
        if summary.get('failed_downloads', 0) > 0:
            report['next_steps'].append("Investigate failed downloads")
            report['recommendations'].append("Check Git LFS configuration and network connectivity")
        
        if summary.get('total_files_downloaded', 0) > 0:
            report['recommendations'].append("Use enhanced PLCConverter for comprehensive ACD analysis")
            report['recommendations'].append("Implement automated processing workflows")
        
        print(f"📋 Next Steps:")
        for step in report['next_steps']:
            print(f"   - {step}")
        
        print(f"\n🔧 Recommendations:")
        for rec in report['recommendations']:
            print(f"   - {rec}")
        
        # Save report
        report_file = f"git_lfs_download_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n💾 Download report saved: {report_file}")
        
        return report

def main():
    """Main execution for Git LFS download"""
    print("🚀 Git LFS Download Script for PLC Repositories")
    print("=" * 60)
    print(f"Download started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    downloader = GitLFSDownloader()
    
    try:
        # Download all repositories
        download_results = downloader.download_all_repositories()
        
        # Generate report
        report = downloader.generate_download_report()
        
        print(f"\n✅ Git LFS Download Process Complete!")
        
        summary = download_results.get('summary', {})
        if summary.get('successful_downloads', 0) > 0:
            print(f"🚀 Ready for ACD file processing with actual content")
        else:
            print(f"⚠️  No files downloaded - check results and retry if needed")
        
        return report
        
    except Exception as e:
        print(f"\n❌ Download process failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main() 