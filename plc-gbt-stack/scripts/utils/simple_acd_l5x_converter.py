#!/usr/bin/env python3
"""
Simple ACD to L5X Converter and Git Push Manager

This script uses the CLI interface directly to convert ACD files to L5X format
and manages the git workflow for all PLC repositories.
"""

import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

# Repository configuration
REPO_BASE_PATH = Path("/Users/reh3376/repos")
CONVERTER_PATH = Path("/Users/reh3376/repos/acd-l5x-tool-lib")

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

class SimplePLCRepoManager:
    """Simple PLC repository manager using CLI conversion"""

    def __init__(self, repo_config: Dict):
        self.config = repo_config
        self.repo_path = REPO_BASE_PATH / repo_config["name"]
        self.acd_dir = self.repo_path / "plc-acd"
        self.l5x_dir = self.repo_path / "plc-l5x"
        self.acd_previous_dir = self.repo_path / "plc-acd-previous"
        self.l5x_previous_dir = self.repo_path / "plc-l5x-previous"

        self.current_acd_file = self.acd_dir / repo_config["acd_file"]
        self.current_l5x_file = self.l5x_dir / repo_config["l5x_file"]

        self.results = {}

    def validate_setup(self) -> bool:
        """Validate repository and converter setup"""
        print(f"🔍 Validating setup for {self.config['name']}...")

        # Check repository structure
        if not self.repo_path.exists():
            print(f"❌ Repository not found: {self.repo_path}")
            return False

        # Check required directories
        required_dirs = [self.acd_dir, self.l5x_dir, self.acd_previous_dir, self.l5x_previous_dir]
        for dir_path in required_dirs:
            if not dir_path.exists():
                print(f"❌ Missing directory: {dir_path}")
                return False

        # Check ACD file
        if not self.current_acd_file.exists():
            print(f"❌ ACD file not found: {self.current_acd_file}")
            return False

        # Check converter
        if not CONVERTER_PATH.exists():
            print(f"❌ Converter not found: {CONVERTER_PATH}")
            return False

        print(f"✅ Setup validated for {self.config['name']}")
        return True

    def archive_previous_l5x(self) -> bool:
        """Archive current L5X file if it exists and is not a placeholder"""
        print(f"📦 Archiving previous L5X for {self.config['name']}...")

        if not self.current_l5x_file.exists():
            print("   ℹ️  No existing L5X file to archive")
            return True

        # Check if it's a placeholder file (small size)
        file_size = self.current_l5x_file.stat().st_size
        if file_size < 500:  # Placeholder files are typically very small
            print(f"   ⚠️  Skipping archive of placeholder file ({file_size} bytes)")
            return True

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archived_name = f"{self.current_l5x_file.stem}_{timestamp}.L5X"
            archived_path = self.l5x_previous_dir / archived_name

            shutil.copy2(self.current_l5x_file, archived_path)
            print(f"   ✅ Archived to: {archived_name}")

            # Clean up old archives (keep 30 days)
            self._cleanup_old_archives()

            return True

        except Exception as e:
            print(f"   ❌ Archive failed: {e}")
            return False

    def _cleanup_old_archives(self):
        """Remove archives older than 30 days"""
        cutoff_date = datetime.now() - timedelta(days=30)
        cleaned_count = 0

        for archive_dir in [self.l5x_previous_dir, self.acd_previous_dir]:
            if not archive_dir.exists():
                continue

            for file_path in archive_dir.glob("*.L5X"):
                try:
                    # Extract timestamp from filename (format: filename_YYYYMMDD_HHMMSS.L5X)
                    parts = file_path.stem.split("_")
                    if len(parts) >= 3:
                        timestamp_str = f"{parts[-2]}_{parts[-1]}"
                        file_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                        if file_date < cutoff_date:
                            file_path.unlink()
                            cleaned_count += 1
                except (ValueError, IndexError):
                    # Skip files that don't match expected naming pattern
                    continue

        if cleaned_count > 0:
            print(f"   🗑️  Cleaned up {cleaned_count} old archive files")

    def convert_acd_to_l5x_cli(self) -> bool:
        """Convert ACD to L5X using CLI interface"""
        print(f"🔄 Converting ACD to L5X for {self.config['name']}...")

        try:
            start_time = time.time()

            # Build CLI command
            cmd = [
                "python3", "-m", "plc_format_converter.cli",
                "acd2l5x",
                str(self.current_acd_file),
                str(self.current_l5x_file),
                "--validate"
            ]

            # Set up environment
            env = os.environ.copy()
            env["PYTHONPATH"] = str(CONVERTER_PATH / "src")

            # Run conversion
            print(f"   📝 Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=str(CONVERTER_PATH),
                env=env,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            elapsed = time.time() - start_time

            # Store results
            self.results["conversion"] = {
                "success": result.returncode == 0,
                "elapsed_time": elapsed,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "input_size": self.current_acd_file.stat().st_size,
                "output_size": self.current_l5x_file.stat().st_size if self.current_l5x_file.exists() else 0,
                "timestamp": datetime.now().isoformat()
            }

            if result.returncode == 0:
                output_size_mb = self.results["conversion"]["output_size"] / (1024 * 1024)
                print(f"   ✅ Conversion successful ({elapsed:.2f}s)")
                print(f"   📊 Output size: {output_size_mb:.2f} MB")

                # Show relevant output
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:  # Show last 5 lines
                        if line.strip():
                            print(f"   📄 {line}")

                return True
            else:
                print(f"   ❌ Conversion failed (code: {result.returncode})")
                if result.stderr:
                    print(f"   📄 Error: {result.stderr[:200]}...")
                return False

        except subprocess.TimeoutExpired:
            print("   ❌ Conversion timed out after 5 minutes")
            self.results["conversion"] = {
                "success": False,
                "error": "Timeout after 5 minutes",
                "timestamp": datetime.now().isoformat()
            }
            return False
        except Exception as e:
            print(f"   ❌ Conversion failed: {e}")
            self.results["conversion"] = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            return False

    def update_documentation(self):
        """Update documentation with conversion info"""
        print(f"📝 Updating documentation for {self.config['name']}...")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conversion_info = self.results.get("conversion", {})

        doc_content = f"""# {self.config['name'].upper()} - {self.config['description']}

## Current Files
- **ACD File**: {self.config['acd_file']} ({self.current_acd_file.stat().st_size / (1024*1024):.2f} MB)
- **L5X File**: {self.config['l5x_file']} ({conversion_info.get('output_size', 0) / (1024*1024):.2f} MB)
- **Last Updated**: {timestamp}

## Conversion Results
- **Status**: {'✅ Success' if conversion_info.get('success') else '❌ Failed'}
- **Conversion Time**: {conversion_info.get('elapsed_time', 0):.2f} seconds
- **Return Code**: {conversion_info.get('return_code', 'N/A')}

## Directory Structure
- `/plc-acd/`: Current ACD files (source of truth)
- `/plc-l5x/`: Current L5X files (for version control)
- `/plc-acd-previous/`: Archived ACD files (30-day retention)
- `/plc-l5x-previous/`: Archived L5X files (30-day retention)

## Git Workflow
1. ACD files contain the authoritative PLC logic
2. L5X files are generated for version control and collaboration
3. All diffs and merges operate on L5X files
4. Both formats are maintained for verification purposes

## Usage Notes
- Make changes to ACD files using Studio 5000
- Run conversion script to update L5X files
- Commit and push L5X changes for collaboration
- Previous versions are automatically archived
"""

        # Write to both directories
        for docs_dir in [self.l5x_dir / "docs", self.acd_dir / "docs"]:
            docs_dir.mkdir(exist_ok=True)
            doc_file = docs_dir / "README.md"
            with open(doc_file, 'w') as f:
                f.write(doc_content)
            print(f"   ✅ Updated {doc_file}")

    def git_operations(self) -> bool:
        """Perform git add, commit, and push"""
        print(f"🔄 Performing git operations for {self.config['name']}...")

        try:
            # Change to repository directory
            original_dir = os.getcwd()
            os.chdir(self.repo_path)

            # Check for changes
            result = subprocess.run(['git', 'status', '--porcelain'],
                                  capture_output=True, text=True, check=True)

            if not result.stdout.strip():
                print("   ℹ️  No changes to commit")
                self.results["git"] = {"success": True, "message": "No changes"}
                return True

            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            print("   ✅ Added changes to git")

            # Create commit message
            conversion_info = self.results.get("conversion", {})
            commit_msg = f"Update L5X files from ACD conversion - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            commit_msg += f"Repository: {self.config['name']}\n"
            commit_msg += f"Description: {self.config['description']}\n"
            commit_msg += f"ACD Source: {self.config['acd_file']}\n"
            commit_msg += f"L5X Output: {self.config['l5x_file']}\n"

            if conversion_info.get('success'):
                commit_msg += f"Conversion Time: {conversion_info.get('elapsed_time', 0):.2f}s\n"
                commit_msg += f"Output Size: {conversion_info.get('output_size', 0) / (1024*1024):.2f} MB\n"

            commit_msg += "\nFiles updated:\n- L5X conversion from ACD\n- Documentation updates\n- Archive management"

            # Commit
            subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
            print("   ✅ Committed changes")

            # Push to remote
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("   ✅ Pushed to remote")

            self.results["git"] = {
                "success": True,
                "commit_message": commit_msg,
                "timestamp": datetime.now().isoformat()
            }

            return True

        except subprocess.CalledProcessError as e:
            error_msg = f"Git operation failed: {e}"
            print(f"   ❌ {error_msg}")
            self.results["git"] = {"success": False, "error": error_msg}
            return False
        finally:
            os.chdir(original_dir)

    def process_repository(self) -> Dict:
        """Process the complete repository workflow"""
        print(f"\n{'='*60}")
        print(f"🚀 Processing Repository: {self.config['name']}")
        print(f"   Description: {self.config['description']}")
        print(f"{'='*60}")

        start_time = time.time()

        # Step 1: Validate setup
        if not self.validate_setup():
            return {
                "repository": self.config['name'],
                "success": False,
                "error": "Setup validation failed",
                "timestamp": datetime.now().isoformat()
            }

        # Step 2: Archive previous L5X
        if not self.archive_previous_l5x():
            return {
                "repository": self.config['name'],
                "success": False,
                "error": "Failed to archive previous L5X",
                "timestamp": datetime.now().isoformat()
            }

        # Step 3: Convert ACD to L5X
        if not self.convert_acd_to_l5x_cli():
            return {
                "repository": self.config['name'],
                "success": False,
                "error": "ACD to L5X conversion failed",
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }

        # Step 4: Update documentation
        self.update_documentation()

        # Step 5: Git operations
        if not self.git_operations():
            return {
                "repository": self.config['name'],
                "success": False,
                "error": "Git operations failed",
                "results": self.results,
                "timestamp": datetime.now().isoformat()
            }

        elapsed = time.time() - start_time

        print(f"\n✅ Repository {self.config['name']} processed successfully in {elapsed:.2f}s!")

        return {
            "repository": self.config['name'],
            "success": True,
            "elapsed_time": elapsed,
            "results": self.results,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main execution function"""
    print("🔄 Simple ACD to L5X Converter and Git Push Manager")
    print("=" * 70)

    # Check converter availability
    if not CONVERTER_PATH.exists():
        print(f"❌ Converter not found at: {CONVERTER_PATH}")
        return 1

    # Process all repositories
    all_results = []
    successful = 0
    failed = 0

    overall_start = time.time()

    for repo_config in PLC_REPOS:
        manager = SimplePLCRepoManager(repo_config)
        result = manager.process_repository()
        all_results.append(result)

        if result["success"]:
            successful += 1
        else:
            failed += 1

    # Summary
    total_time = time.time() - overall_start

    print(f"\n{'='*70}")
    print("📊 PROCESSING SUMMARY")
    print(f"{'='*70}")
    print(f"Total Repositories: {len(PLC_REPOS)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"⏱️  Total Time: {total_time:.2f}s")
    print(f"📈 Success Rate: {(successful/len(PLC_REPOS)*100):.1f}%")

    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in all_results:
        status = "✅" if result["success"] else "❌"
        repo_name = result["repository"]
        print(f"{status} {repo_name}")
        if not result["success"] and "error" in result:
            print(f"   Error: {result['error']}")
        elif result["success"] and "elapsed_time" in result:
            print(f"   Time: {result['elapsed_time']:.2f}s")

    # Save report
    report_file = Path("simple_acd_l5x_conversion_report.json")
    report_data = {
        "summary": {
            "total_repositories": len(PLC_REPOS),
            "successful": successful,
            "failed": failed,
            "success_rate": (successful/len(PLC_REPOS)*100),
            "total_time": total_time,
            "timestamp": datetime.now().isoformat()
        },
        "results": all_results
    }

    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📊 Detailed report saved to: {report_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
