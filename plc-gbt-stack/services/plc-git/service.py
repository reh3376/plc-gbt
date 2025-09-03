"""
PLC Git Integration Service - Phase 35.2.1
Deep Git integration for PLC file management
Following AI Task Orchestrator methodology
"""

import logging
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .models import (
    DiffSummary,
    DiffType,
    GitBranch,
    GitCommit,
    GitRepository,
    MergeConflict,
    MergeResult,
    MergeStatus,
    PLCDiff,
    PLCFile,
    PLCMetadata,
    RoutineDiff,
    TagDiff,
)

logger = logging.getLogger(__name__)


class PLCGitService:
    """
    Git operations service for PLC file management
    Provides version control capabilities for ACD/L5X files
    """

    def __init__(self, workspace_root: str = "/workspace/plc-projects"):
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    async def initialize_plc_repo(
        self,
        project_path: str,
        remote_url: Optional[str] = None
    ) -> GitRepository:
        """
        Initialize Git repository for PLC project

        Args:
            project_path: Path to PLC project
            remote_url: Optional remote Git URL

        Returns:
            GitRepository object
        """
        repo_path = self.workspace_root / project_path
        repo_path.mkdir(parents=True, exist_ok=True)

        # Initialize Git repo
        self._run_git_command(["init"], cwd=repo_path)

        # Add .gitignore for PLC files
        gitignore_content = """
# PLC temporary files
*.tmp
*.bak
*.old
*.log

# Build artifacts
*.exe
*.dll
*.so

# IDE specific
.vs/
.vscode/
*.suo
*.user

# OS specific
.DS_Store
Thumbs.db
"""
        gitignore_path = repo_path / ".gitignore"
        gitignore_path.write_text(gitignore_content)

        # Initial commit
        self._run_git_command(["add", "."], cwd=repo_path)
        self._run_git_command(
            ["commit", "-m", "Initial PLC project setup"],
            cwd=repo_path
        )

        # Add remote if provided
        if remote_url:
            self._run_git_command(
                ["remote", "add", "origin", remote_url],
                cwd=repo_path
            )

        # Get repository info
        current_branch = self._get_current_branch(repo_path)
        last_commit = self._get_last_commit_hash(repo_path)

        return GitRepository(
            path=str(repo_path),
            name=project_path,
            remote_url=remote_url,
            current_branch=current_branch,
            is_dirty=False,
            last_commit_hash=last_commit
        )

    async def commit_plc_changes(
        self,
        files: List[PLCFile],
        message: str,
        metadata: PLCMetadata,
        repo_path: str
    ) -> GitCommit:
        """
        Commit L5X files with metadata

        Args:
            files: List of PLC files to commit
            message: Commit message
            metadata: PLC metadata
            repo_path: Repository path

        Returns:
            GitCommit object
        """
        repo = Path(repo_path)

        # Stage files
        for file in files:
            file_path = repo / file.path
            self._run_git_command(["add", str(file_path)], cwd=repo)

        # Build extended commit message with metadata
        extended_message = f"{message}\n\n"
        extended_message += "PLC Metadata:\n"
        extended_message += f"- Controller: {metadata.controller_name}\n"
        extended_message += f"- Processor: {metadata.processor_type}\n"
        extended_message += f"- Tags: {metadata.tags_count}\n"
        extended_message += f"- Routines: {metadata.routines_count}\n"
        if metadata.safety_status:
            extended_message += f"- Safety Status: {metadata.safety_status}\n"

        # Commit changes
        self._run_git_command(
            ["commit", "-m", extended_message],
            cwd=repo
        )

        # Get commit info
        commit_hash = self._get_last_commit_hash(repo)
        commit_info = self._get_commit_info(commit_hash, repo)

        return commit_info

    async def create_plc_branch(
        self,
        branch_name: str,
        from_branch: Optional[str] = None,
        repo_path: str = None
    ) -> GitBranch:
        """
        Create feature branch for PLC modifications

        Args:
            branch_name: New branch name
            from_branch: Base branch (default: current branch)
            repo_path: Repository path

        Returns:
            GitBranch object
        """
        repo = Path(repo_path) if repo_path else self.workspace_root

        # Create branch
        if from_branch:
            self._run_git_command(
                ["checkout", "-b", branch_name, from_branch],
                cwd=repo
            )
        else:
            self._run_git_command(
                ["checkout", "-b", branch_name],
                cwd=repo
            )

        # Get branch info
        return await self._get_branch_info(branch_name, repo)

    async def merge_plc_branches(
        self,
        source: str,
        target: str,
        repo_path: str
    ) -> MergeResult:
        """
        Three-way merge for L5X files

        Args:
            source: Source branch name
            target: Target branch name
            repo_path: Repository path

        Returns:
            MergeResult object
        """
        repo = Path(repo_path)

        # Checkout target branch
        self._run_git_command(["checkout", target], cwd=repo)

        # Attempt merge
        try:
            self._run_git_command(
                ["merge", source, "--no-ff", "-m", f"Merge {source} into {target}"],
                cwd=repo
            )

            # Check for conflicts
            status = self._run_git_command(["status", "--porcelain"], cwd=repo)

            if "UU" in status or "AA" in status:
                # Conflicts detected
                conflicts = await self._parse_merge_conflicts(repo)
                return MergeResult(
                    status=MergeStatus.CONFLICT,
                    conflicts=conflicts,
                    manual_conflicts_count=len(conflicts)
                )
            else:
                # Successful merge
                merge_commit = self._get_last_commit_hash(repo)
                return MergeResult(
                    status=MergeStatus.SUCCESS,
                    merge_commit_hash=merge_commit,
                    auto_resolved_count=0,
                    manual_conflicts_count=0
                )

        except subprocess.CalledProcessError as e:
            logger.error(f"Merge failed: {str(e)}")
            return MergeResult(
                status=MergeStatus.FAILED,
                manual_conflicts_count=0
            )

    async def diff_plc_files(
        self,
        file_a: str,
        file_b: str,
        repo_path: Optional[str] = None
    ) -> PLCDiff:
        """
        Generate PLC-aware diffs

        Args:
            file_a: First file path or commit:path
            file_b: Second file path or commit:path
            repo_path: Repository path

        Returns:
            PLCDiff object
        """
        repo = Path(repo_path) if repo_path else self.workspace_root

        # Get raw diff
        self._run_git_command(
            ["diff", "--no-index", file_a, file_b],
            cwd=repo
        )

        # Parse L5X-specific differences
        # TODO: Implement actual L5X parsing
        # For now, return mock data

        return PLCDiff(
            file_a=file_a,
            file_b=file_b,
            routines=[
                RoutineDiff(
                    name="MainRoutine",
                    diff_type=DiffType.MODIFIED,
                    line_changes_added=15,
                    line_changes_removed=5
                )
            ],
            tags=[
                TagDiff(
                    name="Temperature_SP",
                    diff_type=DiffType.MODIFIED,
                    old_value="150.0",
                    new_value="160.0",
                    data_type="REAL"
                )
            ],
            data_types=[],
            programs=[],
            summary=DiffSummary(
                total_changes=2,
                routines_modified=1,
                tags_modified=1,
                has_safety_impact=False,
                requires_review=True
            )
        )

    def _run_git_command(
        self,
        args: List[str],
        cwd: Optional[Path] = None
    ) -> str:
        """Run Git command and return output"""
        cmd = ["git"] + args

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.workspace_root,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(cmd)}")
            logger.error(f"Error: {e.stderr}")
            raise

    def _get_current_branch(self, repo_path: Path) -> str:
        """Get current branch name"""
        return self._run_git_command(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path
        )

    def _get_last_commit_hash(self, repo_path: Path) -> str:
        """Get last commit hash"""
        return self._run_git_command(
            ["rev-parse", "HEAD"],
            cwd=repo_path
        )

    def _get_commit_info(self, commit_hash: str, repo_path: Path) -> GitCommit:
        """Get detailed commit information"""
        # Get commit details
        format_str = "%H%n%an%n%ae%n%at%n%s%n%P"
        info = self._run_git_command(
            ["show", "-s", f"--format={format_str}", commit_hash],
            cwd=repo_path
        ).split('\n')

        # Get files changed count
        files_changed = len(self._run_git_command(
            ["diff-tree", "--no-commit-id", "--name-only", "-r", commit_hash],
            cwd=repo_path
        ).split('\n'))

        return GitCommit(
            hash=info[0],
            author_name=info[1],
            author_email=info[2],
            date=datetime.fromtimestamp(int(info[3])),
            message=info[4],
            parent_hashes=info[5].split() if info[5] else [],
            files_changed=files_changed
        )

    async def _get_branch_info(self, branch_name: str, repo_path: Path) -> GitBranch:
        """Get branch information"""
        # Get branch commit info
        commit_hash = self._run_git_command(
            ["rev-parse", branch_name],
            cwd=repo_path
        )

        commit_info = self._get_commit_info(commit_hash, repo_path)
        current_branch = self._get_current_branch(repo_path)

        # Calculate ahead/behind (simplified)
        # TODO: Implement proper ahead/behind calculation

        return GitBranch(
            name=branch_name,
            is_current=(branch_name == current_branch),
            commit_hash=commit_hash,
            commit_message=commit_info.message,
            commit_date=commit_info.date,
            ahead=0,
            behind=0
        )

    async def _parse_merge_conflicts(self, repo_path: Path) -> List[MergeConflict]:
        """Parse merge conflicts from Git status"""
        # TODO: Implement actual conflict parsing
        # For now, return empty list
        return []
