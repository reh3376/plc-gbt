#!/usr/bin/env python3
"""
Phase 3.7.1 Repository Analyzer
Comprehensive analysis of PLC repositories for migration planning.

This script analyzes all PLC repositories (plc-100 through plc-600) to:
1. Catalog all .acd files with metadata
2. Analyze repository structure and non-PLC files
3. Document file sizes, modification dates, and dependencies
4. Create migration manifest for tracking and rollback
5. Generate detailed reports for GitHub repository creation
"""

import hashlib
import json
import logging
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('repository_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ACDFileInfo:
    """Information about an ACD file."""
    filename: str
    filepath: str
    size_bytes: int
    size_mb: float
    modified_date: str
    created_date: str
    file_hash: str
    repository: str
    relative_path: str
    is_readable: bool
    error_message: Optional[str] = None

@dataclass
class RepositoryInfo:
    """Information about a PLC repository."""
    name: str
    path: str
    total_files: int
    acd_files: List[ACDFileInfo]
    other_files: List[str]
    total_size_bytes: int
    total_size_mb: float
    git_info: Dict[str, Any]
    analysis_date: str
    structure: Dict[str, Any]

def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.warning(f"Could not calculate hash for {filepath}: {e}")
        return "HASH_ERROR"

def get_file_dates(filepath: str) -> tuple:
    """Get creation and modification dates of a file."""
    try:
        stat = os.stat(filepath)
        modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
        created = datetime.fromtimestamp(stat.st_ctime).isoformat()
        return created, modified
    except Exception as e:
        logger.warning(f"Could not get dates for {filepath}: {e}")
        return "DATE_ERROR", "DATE_ERROR"

def get_git_info(repo_path: str) -> Dict[str, Any]:
    """Get git information about the repository."""
    git_info = {
        "is_git_repo": False,
        "current_branch": None,
        "last_commit": None,
        "remote_url": None,
        "status": None
    }

    try:
        # Check if it's a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            git_info["is_git_repo"] = True

            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                git_info["current_branch"] = result.stdout.strip()

            # Get last commit
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%s|%an|%ad"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                commit_parts = result.stdout.strip().split("|")
                if len(commit_parts) >= 4:
                    git_info["last_commit"] = {
                        "hash": commit_parts[0],
                        "message": commit_parts[1],
                        "author": commit_parts[2],
                        "date": commit_parts[3]
                    }

            # Get remote URL
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                git_info["remote_url"] = result.stdout.strip()

            # Get status
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
                git_info["status"] = {
                    "clean": len(status_lines) == 0,
                    "modified_files": len(status_lines),
                    "changes": status_lines[:10]  # Limit to first 10 changes
                }

    except Exception as e:
        logger.warning(f"Could not get git info for {repo_path}: {e}")

    return git_info

def analyze_repository_structure(repo_path: str) -> Dict[str, Any]:
    """Analyze the directory structure of the repository."""
    structure = {
        "directories": [],
        "file_types": {},
        "depth_analysis": {},
        "large_files": []  # Files > 10MB
    }

    try:
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            rel_root = os.path.relpath(root, repo_path)
            if rel_root != '.':
                structure["directories"].append(rel_root)

            # Analyze depth
            depth = len(rel_root.split(os.sep)) if rel_root != '.' else 0
            structure["depth_analysis"][depth] = structure["depth_analysis"].get(depth, 0) + len(files)

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    # File extension analysis
                    ext = os.path.splitext(file)[1].lower()
                    structure["file_types"][ext] = structure["file_types"].get(ext, 0) + 1

                    # Large file analysis
                    size = os.path.getsize(filepath)
                    if size > 10 * 1024 * 1024:  # > 10MB
                        structure["large_files"].append({
                            "file": os.path.relpath(filepath, repo_path),
                            "size_mb": round(size / (1024 * 1024), 2)
                        })
                except Exception as e:
                    logger.warning(f"Could not analyze file {filepath}: {e}")

    except Exception as e:
        logger.error(f"Could not analyze repository structure for {repo_path}: {e}")

    return structure

def analyze_acd_file(filepath: str, repo_name: str, repo_path: str) -> ACDFileInfo:
    """Analyze a single ACD file."""
    try:
        stat = os.stat(filepath)
        size_bytes = stat.st_size
        size_mb = round(size_bytes / (1024 * 1024), 3)

        created, modified = get_file_dates(filepath)
        file_hash = calculate_file_hash(filepath)

        relative_path = os.path.relpath(filepath, repo_path)

        # Test if file is readable
        is_readable = True
        error_message = None
        try:
            with open(filepath, 'rb') as f:
                f.read(1024)  # Try to read first 1KB
        except Exception as e:
            is_readable = False
            error_message = str(e)

        return ACDFileInfo(
            filename=os.path.basename(filepath),
            filepath=filepath,
            size_bytes=size_bytes,
            size_mb=size_mb,
            modified_date=modified,
            created_date=created,
            file_hash=file_hash,
            repository=repo_name,
            relative_path=relative_path,
            is_readable=is_readable,
            error_message=error_message
        )

    except Exception as e:
        logger.error(f"Could not analyze ACD file {filepath}: {e}")
        return ACDFileInfo(
            filename=os.path.basename(filepath),
            filepath=filepath,
            size_bytes=0,
            size_mb=0,
            modified_date="ERROR",
            created_date="ERROR",
            file_hash="ERROR",
            repository=repo_name,
            relative_path="ERROR",
            is_readable=False,
            error_message=str(e)
        )

def analyze_repository(repo_path: str) -> RepositoryInfo:
    """Analyze a single PLC repository."""
    repo_name = os.path.basename(repo_path)
    logger.info(f"🔍 Analyzing repository: {repo_name}")

    acd_files = []
    other_files = []
    total_size = 0

    # Find all files
    try:
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                filepath = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(filepath)
                    total_size += file_size

                    if file.lower().endswith('.acd'):
                        acd_info = analyze_acd_file(filepath, repo_name, repo_path)
                        acd_files.append(acd_info)
                        logger.info(f"  📁 Found ACD: {acd_info.filename} ({acd_info.size_mb} MB)")
                    else:
                        relative_path = os.path.relpath(filepath, repo_path)
                        other_files.append(relative_path)

                except Exception as e:
                    logger.warning(f"Could not process file {filepath}: {e}")

    except Exception as e:
        logger.error(f"Could not walk repository {repo_path}: {e}")

    # Get git information
    git_info = get_git_info(repo_path)

    # Analyze repository structure
    structure = analyze_repository_structure(repo_path)

    total_files = len(acd_files) + len(other_files)
    total_mb = round(total_size / (1024 * 1024), 2)

    logger.info(f"  ✅ Analysis complete: {len(acd_files)} ACD files, {len(other_files)} other files, {total_mb} MB total")

    return RepositoryInfo(
        name=repo_name,
        path=repo_path,
        total_files=total_files,
        acd_files=acd_files,
        other_files=other_files,
        total_size_bytes=total_size,
        total_size_mb=total_mb,
        git_info=git_info,
        analysis_date=datetime.now().isoformat(),
        structure=structure
    )

def generate_migration_manifest(repositories: List[RepositoryInfo]) -> Dict[str, Any]:
    """Generate a comprehensive migration manifest."""
    manifest = {
        "migration_info": {
            "analysis_date": datetime.now().isoformat(),
            "total_repositories": len(repositories),
            "total_acd_files": sum(len(repo.acd_files) for repo in repositories),
            "total_size_mb": sum(repo.total_size_mb for repo in repositories),
            "phase": "3.7.1 - Repository Analysis & Preparation"
        },
        "repositories": {},
        "acd_file_summary": {
            "by_repository": {},
            "by_size": [],
            "largest_files": [],
            "potential_issues": []
        },
        "migration_recommendations": []
    }

    all_acd_files = []

    for repo in repositories:
        # Repository summary
        manifest["repositories"][repo.name] = {
            "path": repo.path,
            "acd_files": len(repo.acd_files),
            "total_files": repo.total_files,
            "size_mb": repo.total_size_mb,
            "git_status": repo.git_info,
            "structure": repo.structure,
            "files": [asdict(acd) for acd in repo.acd_files]
        }

        # ACD file summary by repository
        manifest["acd_file_summary"]["by_repository"][repo.name] = {
            "count": len(repo.acd_files),
            "total_size_mb": sum(acd.size_mb for acd in repo.acd_files),
            "largest_file": max(repo.acd_files, key=lambda x: x.size_mb).filename if repo.acd_files else None,
            "issues": [acd.filename for acd in repo.acd_files if not acd.is_readable]
        }

        all_acd_files.extend(repo.acd_files)

    # Sort files by size
    all_acd_files.sort(key=lambda x: x.size_mb, reverse=True)

    # Largest files across all repositories
    manifest["acd_file_summary"]["largest_files"] = [
        {
            "filename": acd.filename,
            "repository": acd.repository,
            "size_mb": acd.size_mb,
            "relative_path": acd.relative_path
        }
        for acd in all_acd_files[:10]  # Top 10 largest
    ]

    # Size distribution
    size_ranges = [
        (0, 1, "< 1 MB"),
        (1, 10, "1-10 MB"),
        (10, 50, "10-50 MB"),
        (50, 100, "50-100 MB"),
        (100, float('inf'), "> 100 MB")
    ]

    for min_size, max_size, label in size_ranges:
        count = len([acd for acd in all_acd_files if min_size <= acd.size_mb < max_size])
        manifest["acd_file_summary"]["by_size"].append({
            "range": label,
            "count": count,
            "percentage": round(count / len(all_acd_files) * 100, 1) if all_acd_files else 0
        })

    # Potential issues
    issues = []
    for acd in all_acd_files:
        if not acd.is_readable:
            issues.append(f"Unreadable file: {acd.repository}/{acd.filename}")
        if acd.size_mb > 100:
            issues.append(f"Large file (>100MB): {acd.repository}/{acd.filename} ({acd.size_mb} MB)")
        if acd.file_hash == "HASH_ERROR":
            issues.append(f"Hash calculation failed: {acd.repository}/{acd.filename}")

    manifest["acd_file_summary"]["potential_issues"] = issues

    # Migration recommendations
    recommendations = []

    if len(all_acd_files) > 50:
        recommendations.append("Consider batch processing for large number of files")

    large_files = [acd for acd in all_acd_files if acd.size_mb > 50]
    if large_files:
        recommendations.append(f"Special handling needed for {len(large_files)} large files (>50MB)")

    if issues:
        recommendations.append(f"Resolve {len(issues)} potential issues before migration")

    recommendations.extend([
        "Implement parallel processing for conversion efficiency",
        "Set up comprehensive validation checkpoints",
        "Create rollback procedures for failed conversions",
        "Monitor conversion progress with detailed logging"
    ])

    manifest["migration_recommendations"] = recommendations

    return manifest

def main():
    """Main analysis function."""
    logger.info("🚀 Starting Phase 3.7.1 Repository Analysis")

    # Base directory for PLC repositories - they are in the parent of PLC_GPT
    current_dir = Path(__file__).resolve().parent
    plc_gpt_dir = current_dir.parent.parent.parent  # Go up from scripts/phase37/ to PLC_GPT
    base_dir = plc_gpt_dir.parent  # Go up one more to find plc-100, plc-200, etc.

    logger.info(f"🔍 Looking for repositories in: {base_dir}")

    # Repository names to analyze
    repo_names = ['plc-100', 'plc-200', 'plc-300', 'plc-400', 'plc-500', 'plc-600']

    repositories = []

    for repo_name in repo_names:
        repo_path = base_dir / repo_name

        logger.info(f"  Checking: {repo_path}")

        if not repo_path.exists():
            logger.error(f"❌ Repository not found: {repo_path}")
            continue

        if not repo_path.is_dir():
            logger.error(f"❌ Not a directory: {repo_path}")
            continue

        try:
            repo_info = analyze_repository(str(repo_path))
            repositories.append(repo_info)
        except Exception as e:
            logger.error(f"❌ Failed to analyze {repo_name}: {e}")

    if not repositories:
        logger.error("❌ No repositories found or analyzed successfully")
        return 1

    # Generate migration manifest
    logger.info("📋 Generating migration manifest...")
    manifest = generate_migration_manifest(repositories)

    # Save results
    output_dir = Path(__file__).parent
    output_dir.mkdir(exist_ok=True)

    # Save detailed analysis
    analysis_file = output_dir / "repository_analysis_detailed.json"
    with open(analysis_file, 'w') as f:
        json.dump({
            "repositories": [asdict(repo) for repo in repositories]
        }, f, indent=2)

    # Save migration manifest
    manifest_file = output_dir / "migration_manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)

    # Generate summary report
    summary_file = output_dir / "analysis_summary.md"
    with open(summary_file, 'w') as f:
        f.write("# Phase 3.7.1 Repository Analysis Summary\n\n")
        f.write(f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Overview\n")
        f.write(f"- **Total Repositories**: {len(repositories)}\n")
        f.write(f"- **Total ACD Files**: {manifest['migration_info']['total_acd_files']}\n")
        f.write(f"- **Total Size**: {manifest['migration_info']['total_size_mb']:.2f} MB\n\n")

        f.write("## Repository Summary\n")
        for repo in repositories:
            f.write(f"### {repo.name}\n")
            f.write(f"- **ACD Files**: {len(repo.acd_files)}\n")
            f.write(f"- **Total Files**: {repo.total_files}\n")
            f.write(f"- **Size**: {repo.total_size_mb:.2f} MB\n")
            f.write(f"- **Git Branch**: {repo.git_info.get('current_branch', 'N/A')}\n\n")

        f.write("## Largest ACD Files\n")
        for file_info in manifest["acd_file_summary"]["largest_files"][:5]:
            f.write(f"- **{file_info['filename']}** ({file_info['repository']}): {file_info['size_mb']:.2f} MB\n")

        f.write("\n## Size Distribution\n")
        for size_info in manifest["acd_file_summary"]["by_size"]:
            f.write(f"- **{size_info['range']}**: {size_info['count']} files ({size_info['percentage']}%)\n")

        if manifest["acd_file_summary"]["potential_issues"]:
            f.write("\n## Potential Issues\n")
            for issue in manifest["acd_file_summary"]["potential_issues"][:10]:
                f.write(f"- {issue}\n")

        f.write("\n## Migration Recommendations\n")
        for rec in manifest["migration_recommendations"]:
            f.write(f"- {rec}\n")

    logger.info("✅ Analysis complete! Results saved to:")
    logger.info(f"  📄 Detailed analysis: {analysis_file}")
    logger.info(f"  📋 Migration manifest: {manifest_file}")
    logger.info(f"  📝 Summary report: {summary_file}")

    # Print summary
    print("\n" + "="*60)
    print("🎯 PHASE 3.7.1 REPOSITORY ANALYSIS COMPLETE")
    print("="*60)
    print(f"📊 Analyzed {len(repositories)} repositories")
    print(f"📁 Found {manifest['migration_info']['total_acd_files']} ACD files")
    print(f"💾 Total size: {manifest['migration_info']['total_size_mb']:.2f} MB")

    if manifest["acd_file_summary"]["potential_issues"]:
        print(f"⚠️  {len(manifest['acd_file_summary']['potential_issues'])} potential issues identified")
    else:
        print("✅ No issues detected")

    print("\n📋 Next: Create GitHub repositories and begin conversion infrastructure")
    print("="*60)

    return 0

if __name__ == "__main__":
    sys.exit(main())
