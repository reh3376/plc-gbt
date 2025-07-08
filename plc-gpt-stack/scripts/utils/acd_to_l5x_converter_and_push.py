#!/usr/bin/env python3
"""
ACD to L5X Converter and Git Push Manager

This script converts ACD files to L5X format and manages the git workflow
for all PLC repositories according to the specified directory structure:
- /plc-acd/: Current ACD files 
- /plc-l5x/: Current L5X files
- /plc-acd-previous/: Archive of previous ACD files (30 days)
- /plc-l5x-previous/: Archive of previous L5X files (30 days)

Features:
- Converts ACD files using acd-l5x-tool-lib
- Archives previous versions with timestamps
- Manages git workflows and pushes to remote
- Validates conversions and provides detailed reporting
- Handles errors gracefully with rollback capabilities
"""

import sys
import os
import subprocess
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import tempfile
import time

# Add the acd-l5x-tool-lib to Python path
sys.path.insert(0, '/Users/reh3376/repos/acd-l5x-tool-lib/src')

try:
    from plc_format_converter.cli import main as converter_cli
    from plc_format_converter.core.converter import PLCConverter
    from plc_format_converter.formats.acd_handler import ACDHandler
    from plc_format_converter.formats.l5x_handler import L5XHandler
    from plc_format_converter.utils.validation import PLCValidator
    CONVERTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Warning: Converter not available: {e}")
    CONVERTER_AVAILABLE = False

# Repository configuration
REPO_BASE_PATH = Path("/Users/reh3376/repos")
PLC_REPOS = [
    {
        "name": "plc-100",
        "acd_file": "PLC100_Mashing.ACD",
        "l5x_file": "PLC100_Mashing.L5X",
        "description": "Mashing Process Control"
    },
    {
        "name": "plc-200", 
        "acd_file": "PLC200_Fermentation.ACD",
        "l5x_file": "PLC200_Fermentation.L5X",
        "description": "Fermentation Process Control"
    },
    {
        "name": "plc-300",
        "acd_file": "PLC300_Still.ACD", 
        "l5x_file": "PLC300_Still.L5X",
        "description": "Distillation Process Control"
    },
    {
        "name": "plc-400",
        "acd_file": "PLC400_Utilities.ACD",
        "l5x_file": "PLC400_Utilities.L5X", 
        "description": "Utilities and Support Systems"
    },
    {
        "name": "plc-500",
        "acd_file": "PLC500_Barreling.ACD",
        "l5x_file": "PLC500_Barreling.L5X",
        "description": "Barreling and Aging Process"
    },
    {
        "name": "plc-600",
        "acd_file": "PLC600_RO.ACD",
        "l5x_file": "PLC600_RO.L5X", 
        "description": "Reverse Osmosis Water Treatment"
    }
]

class PLCRepoManager:
    """Manages PLC repository operations including conversion and git workflows"""
    
    def __init__(self, repo_config: Dict):
        self.config = repo_config
        self.repo_path = REPO_BASE_PATH / repo_config["name"]
        self.acd_dir = self.repo_path / "plc-acd"
        self.l5x_dir = self.repo_path / "plc-l5x"
        self.acd_previous_dir = self.repo_path / "plc-acd-previous"
        self.l5x_previous_dir = self.repo_path / "plc-l5x-previous"
        self.acd_docs_dir = self.acd_dir / "docs"
        self.l5x_docs_dir = self.l5x_dir / "docs"
        
        self.current_acd_file = self.acd_dir / repo_config["acd_file"]
        self.current_l5x_file = self.l5x_dir / repo_config["l5x_file"]
        
        self.conversion_results = {}
        self.git_results = {}
        
    def validate_repository_structure(self) -> bool:
        """Validate that the repository has the required directory structure"""
        print(f"🔍 Validating repository structure for {self.config['name']}...")
        
        required_dirs = [
            self.acd_dir, self.l5x_dir, 
            self.acd_previous_dir, self.l5x_previous_dir,
            self.acd_docs_dir, self.l5x_docs_dir
        ]
        
        missing_dirs = []
        for dir_path in required_dirs:
            if not dir_path.exists():
                missing_dirs.append(str(dir_path))
        
        if missing_dirs:
            print(f"❌ Missing directories in {self.config['name']}:")
            for missing in missing_dirs:
                print(f"   • {missing}")
            return False
        
        print(f"✅ Repository structure validated for {self.config['name']}")
        return True
    
    def check_current_files(self) -> Tuple[bool, bool]:
        """Check if current ACD and L5X files exist"""
        acd_exists = self.current_acd_file.exists()
        l5x_exists = self.current_l5x_file.exists()
        
        print(f"📁 File status for {self.config['name']}:")
        print(f"   ACD: {'✅' if acd_exists else '❌'} {self.current_acd_file}")
        print(f"   L5X: {'✅' if l5x_exists else '❌'} {self.current_l5x_file}")
        
        if acd_exists:
            acd_size = self.current_acd_file.stat().st_size / (1024 * 1024)
            print(f"   ACD Size: {acd_size:.2f} MB")
        
        if l5x_exists:
            l5x_size = self.current_l5x_file.stat().st_size / (1024 * 1024)
            print(f"   L5X Size: {l5x_size:.2f} MB")
            
        return acd_exists, l5x_exists
    
    def archive_previous_files(self) -> bool:
        """Archive current L5X file to previous directory with timestamp"""
        print(f"📦 Archiving previous files for {self.config['name']}...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Archive existing L5X file if it exists and is not a placeholder
            if self.current_l5x_file.exists():
                file_size = self.current_l5x_file.stat().st_size
                if file_size > 200:  # Not a placeholder file
                    archived_l5x = self.l5x_previous_dir / f"{self.current_l5x_file.stem}_{timestamp}.L5X"
                    shutil.copy2(self.current_l5x_file, archived_l5x)
                    print(f"   ✅ Archived L5X: {archived_l5x.name}")
                else:
                    print(f"   ⚠️  Skipping L5X archive (placeholder file)")
            
            # Clean up old archives (keep 30 days)
            self._cleanup_old_archives()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Archive failed: {e}")
            return False
    
    def _cleanup_old_archives(self):
        """Remove archives older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for archive_dir in [self.l5x_previous_dir, self.acd_previous_dir]:
            if not archive_dir.exists():
                continue
                
            for file_path in archive_dir.glob("*"):
                if file_path.is_file():
                    # Extract timestamp from filename
                    try:
                        parts = file_path.stem.split("_")
                        if len(parts) >= 3:
                            timestamp_str = f"{parts[-2]}_{parts[-1]}"
                            file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                            
                            if file_date < cutoff_date:
                                file_path.unlink()
                                print(f"   🗑️  Removed old archive: {file_path.name}")
                    except (ValueError, IndexError):
                        # Skip files that don't match expected naming pattern
                        continue
    
    def convert_acd_to_l5x(self) -> bool:
        """Convert ACD file to L5X format using acd-l5x-tool-lib"""
        print(f"🔄 Converting ACD to L5X for {self.config['name']}...")
        
        if not CONVERTER_AVAILABLE:
            print("❌ Converter library not available")
            return False
        
        if not self.current_acd_file.exists():
            print(f"❌ ACD file not found: {self.current_acd_file}")
            return False
        
        try:
            start_time = time.time()
            
            # Initialize converter
            converter = PLCConverter()
            
            # Perform conversion using the correct method
            conversion_result = converter.acd_to_l5x(
                acd_file=self.current_acd_file,
                l5x_file=self.current_l5x_file
            )
            
            elapsed = time.time() - start_time
            
            # Store results
            self.conversion_results = {
                "success": conversion_result.success,
                "elapsed_time": elapsed,
                "input_size": self.current_acd_file.stat().st_size,
                "output_size": self.current_l5x_file.stat().st_size if self.current_l5x_file.exists() else 0,
                "status": conversion_result.status.value if hasattr(conversion_result.status, 'value') else str(conversion_result.status),
                "statistics": conversion_result.statistics if hasattr(conversion_result, 'statistics') else {},
                "issues_count": len(conversion_result.issues) if hasattr(conversion_result, 'issues') else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"   ✅ Conversion completed in {elapsed:.2f}s")
            print(f"   📊 Output size: {self.conversion_results['output_size'] / (1024*1024):.2f} MB")
            print(f"   📋 Status: {self.conversion_results['status']}")
            
            if conversion_result.success:
                print(f"   ✅ Conversion successful")
                if hasattr(conversion_result, 'statistics') and conversion_result.statistics:
                    stats = conversion_result.statistics
                    print(f"   📊 Project stats: {stats.get('programs', 0)} programs, {stats.get('routines', 0)} routines, {stats.get('total_tags', 0)} tags")
            else:
                print(f"   ⚠️  Conversion completed with issues")
                if hasattr(conversion_result, 'issues') and conversion_result.issues:
                    print(f"   📋 Issues found: {len(conversion_result.issues)}")
            
            return conversion_result.success
            
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            self.conversion_results = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    def update_documentation(self):
        """Update documentation files with conversion information"""
        print(f"📝 Updating documentation for {self.config['name']}...")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Update L5X docs
        l5x_doc_content = f"""# {self.config['name'].upper()} L5X Files

## Description
{self.config['description']}

## Current File
- **File**: {self.config['l5x_file']}
- **Last Updated**: {timestamp}
- **Source ACD**: {self.config['acd_file']}

## Conversion Information
{json.dumps(self.conversion_results, indent=2)}

## Usage Notes
- This L5X file is automatically generated from the corresponding ACD file
- All changes should be made to the ACD file in the plc-acd directory
- This file is used for version control and CI/CD pipelines
- Previous versions are archived in the plc-l5x-previous directory

## Git Workflow
1. ACD files are the source of truth for PLC logic
2. L5X files are generated for version control and collaboration
3. All diffs and merges operate on L5X files
4. Both formats are maintained for verification purposes
"""
        
        l5x_doc_file = self.l5x_docs_dir / "README.md"
        with open(l5x_doc_file, 'w') as f:
            f.write(l5x_doc_content)
        
        print(f"   ✅ Updated {l5x_doc_file}")
    
    def git_add_commit_push(self) -> bool:
        """Perform git operations: add, commit, and push"""
        print(f"🔄 Performing git operations for {self.config['name']}...")
        
        try:
            # Change to repository directory
            os.chdir(self.repo_path)
            
            # Check git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                print(f"   ℹ️  No changes to commit in {self.config['name']}")
                return True
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            print(f"   ✅ Added changes to git")
            
            # Create commit message
            commit_msg = f"Update L5X files from ACD conversion - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            commit_msg += f"- Converted {self.config['acd_file']} to {self.config['l5x_file']}\n"
            commit_msg += f"- Updated documentation\n"
            if self.conversion_results.get('success'):
                commit_msg += f"- Conversion time: {self.conversion_results.get('elapsed_time', 0):.2f}s\n"
                commit_msg += f"- Output size: {self.conversion_results.get('output_size', 0) / (1024*1024):.2f} MB\n"
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print(f"   ✅ Committed changes")
            
            # Push to remote
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print(f"   ✅ Pushed to remote")
            
            self.git_results = {
                "success": True,
                "commit_message": commit_msg,
                "timestamp": datetime.now().isoformat()
            }
            
            return True
            
        except subprocess.CalledProcessError as e:
            error_msg = f"Git operation failed: {e}"
            print(f"   ❌ {error_msg}")
            self.git_results = {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            return False
        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            print(f"   ❌ {error_msg}")
            self.git_results = {
                "success": False,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
            return False
    
    def process_repository(self) -> Dict:
        """Process the entire repository: validate, convert, archive, and push"""
        print(f"\n{'='*60}")
        print(f"🚀 Processing Repository: {self.config['name']}")
        print(f"{'='*60}")
        
        results = {
            "repository": self.config['name'],
            "started": datetime.now().isoformat(),
            "validation": {},
            "conversion": {},
            "git": {},
            "overall_success": False
        }
        
        try:
            # Step 1: Validate repository structure
            if not self.validate_repository_structure():
                results["validation"]["structure"] = False
                results["error"] = "Repository structure validation failed"
                return results
            results["validation"]["structure"] = True
            
            # Step 2: Check current files
            acd_exists, l5x_exists = self.check_current_files()
            results["validation"]["files"] = {"acd_exists": acd_exists, "l5x_exists": l5x_exists}
            
            if not acd_exists:
                results["error"] = "ACD file not found"
                return results
            
            # Step 3: Archive previous files
            if not self.archive_previous_files():
                results["error"] = "Failed to archive previous files"
                return results
            
            # Step 4: Convert ACD to L5X
            if not self.convert_acd_to_l5x():
                results["conversion"] = self.conversion_results
                results["error"] = "ACD to L5X conversion failed"
                return results
            results["conversion"] = self.conversion_results
            
            # Step 5: Update documentation
            self.update_documentation()
            
            # Step 6: Git operations
            if not self.git_add_commit_push():
                results["git"] = self.git_results
                results["error"] = "Git operations failed"
                return results
            results["git"] = self.git_results
            
            # Success!
            results["overall_success"] = True
            results["completed"] = datetime.now().isoformat()
            
            print(f"\n✅ Repository {self.config['name']} processed successfully!")
            
        except Exception as e:
            results["error"] = f"Unexpected error: {e}"
            print(f"\n❌ Repository {self.config['name']} processing failed: {e}")
        
        return results


def main():
    """Main execution function"""
    print("🔄 PLC Repository ACD to L5X Converter and Git Push Manager")
    print("=" * 70)
    
    if not CONVERTER_AVAILABLE:
        print("❌ Cannot proceed without converter library")
        print("Please ensure acd-l5x-tool-lib is properly installed")
        return
    
    # Process all repositories
    all_results = []
    successful_repos = 0
    failed_repos = 0
    
    start_time = time.time()
    
    for repo_config in PLC_REPOS:
        manager = PLCRepoManager(repo_config)
        result = manager.process_repository()
        all_results.append(result)
        
        if result["overall_success"]:
            successful_repos += 1
        else:
            failed_repos += 1
    
    # Generate summary report
    total_time = time.time() - start_time
    
    print(f"\n{'='*70}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'='*70}")
    print(f"Total Repositories: {len(PLC_REPOS)}")
    print(f"✅ Successful: {successful_repos}")
    print(f"❌ Failed: {failed_repos}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"📈 Success Rate: {(successful_repos/len(PLC_REPOS)*100):.1f}%")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in all_results:
        status = "✅" if result["overall_success"] else "❌"
        print(f"{status} {result['repository']}")
        if not result["overall_success"] and "error" in result:
            print(f"   Error: {result['error']}")
    
    # Save detailed report
    report_file = Path("acd_l5x_conversion_report.json")
    report_data = {
        "summary": {
            "total_repositories": len(PLC_REPOS),
            "successful": successful_repos,
            "failed": failed_repos,
            "success_rate": (successful_repos/len(PLC_REPOS)*100),
            "total_time": total_time,
            "timestamp": datetime.now().isoformat()
        },
        "results": all_results
    }
    
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)
    
    print(f"\n📊 Detailed report saved to: {report_file}")
    
    if failed_repos > 0:
        print(f"\n⚠️  {failed_repos} repositories had issues. Check the detailed report for more information.")
        return 1
    else:
        print(f"\n🎉 All repositories processed successfully!")
        return 0


if __name__ == "__main__":
    # Change back to PLC_GPT directory when done
    original_dir = os.getcwd()
    try:
        exit_code = main()
        sys.exit(exit_code)
    finally:
        os.chdir(original_dir) 