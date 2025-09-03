#!/usr/bin/env python3
"""
Phase 14.1.3: Git Integration & Optimization Hooks
==================================================

Git hook integration for automated analysis triggers and staged change analysis.
Following AI Task Orchestrator methodology for systematic git workflow integration.

Features:
- Pre-commit hook installation and management
- Staged change analysis with selective optimization
- Git workflow integration for automated code quality checks
- Rollback and safety mechanisms for git operations
- Integration with CodebaseAnalyzer and DependencyGraphBuilder

Target: ~400 lines
Author: AI Task Orchestrator
Date: 2025-01-18
"""

import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add modules to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent / "modules"))
from core import BaseOrchestrator, TaskAnalysis


@dataclass
class StagedFile:
    """Information about a staged file in git"""
    file_path: str
    change_type: str  # added, modified, deleted, renamed
    lines_added: int
    lines_removed: int
    complexity_change: float
    optimization_priority: str  # low, medium, high

@dataclass
class StagingAnalysis:
    """Analysis of files in git staging area"""
    total_staged_files: int
    analysis_timestamp: str
    staged_files: List[StagedFile]
    optimization_recommendations: List[str]
    blocking_issues: List[str]
    commit_safety_score: float  # 0-1, higher is safer
    estimated_analysis_time: str
    suggested_actions: List[str]

@dataclass
class HookInstallationResult:
    """Result of git hook installation"""
    hook_name: str
    installation_path: str
    installation_success: bool
    backup_created: str
    hook_content: str
    installation_details: Dict[str, Any]

class GitOptimizationHooks(BaseOrchestrator):
    """
    Git integration framework for automated code optimization workflows.

    Provides seamless integration with git workflows through pre-commit hooks,
    staged change analysis, and automated optimization recommendations.
    """

    def __init__(self, task_id: str = "git_optimization_hooks", config_file: Optional[str] = None):
        super().__init__(task_id, config_file)

        # Git configuration
        self.git_config = {
            "supported_hooks": ["pre-commit", "pre-push", "post-commit"],
            "analysis_file_types": [".py", ".ts", ".js", ".sql"],
            "max_files_per_analysis": 50,
            "commit_safety_threshold": 0.7,
            "hook_backup_suffix": ".backup",
            "analysis_timeout": 30  # seconds
        }

        # Paths
        self.repo_root = self._find_git_root()
        self.hooks_dir = self.repo_root / ".git" / "hooks" if self.repo_root else None
        self.backup_dir = Path(tempfile.mkdtemp(prefix="git_hooks_backup_"))

        # Analysis results
        self.staging_analysis = None
        self.hook_installations = []

        # Performance tracking
        self.git_metrics = {
            "hooks_installed": 0,
            "staged_files_analyzed": 0,
            "optimizations_suggested": 0,
            "safety_checks_performed": 0
        }

    def _analyze_task(self) -> TaskAnalysis:
        """Implement task analysis following AI Task Orchestrator methodology"""
        return TaskAnalysis(
            task_id=self.task_id,
            complexity="moderate",
            estimated_time="1-2 hours",
            estimated_lines=400,
            requirements=[
                "Git repository access",
                "Git hook installation permissions",
                "Subprocess execution for git commands",
                "File system write permissions",
                "Integration with CodebaseAnalyzer"
            ],
            risks=[
                "Git hook conflicts with existing hooks",
                "Performance impact on git operations",
                "Repository corruption if hooks malfunction"
            ],
            dependencies=["subprocess", "pathlib", "core.BaseOrchestrator"],
            success_criteria=[
                "Successful git hook installation",
                "Accurate staged file analysis",
                "Non-disruptive git workflow integration",
                "Rollback capability for all operations"
            ]
        )

    def execute(self) -> Dict[str, Any]:
        """Execute git integration setup and analysis"""
        self.log_execution_step("Git Integration Setup", "started")

        try:
            # Validate requirements
            if not self.validate_requirements():
                return {"status": "failed", "error": "Requirements validation failed"}

            # Check git repository
            if not self._validate_git_repository():
                return {"status": "failed", "error": "Not in a valid git repository"}

            # Install pre-commit hooks
            hook_results = self.install_pre_commit_hooks()

            # Analyze current staging area
            staging_analysis = self.analyze_staged_changes()

            # Generate recommendations
            recommendations = self._generate_git_workflow_recommendations(staging_analysis)

            # Save results
            results = {
                "hook_installations": [asdict(hr) for hr in hook_results],
                "staging_analysis": asdict(staging_analysis),
                "recommendations": recommendations,
                "metrics": self.git_metrics,
                "session_info": {
                    "session_id": self.session_id,
                    "analysis_date": datetime.now().isoformat(),
                    "repo_root": str(self.repo_root),
                    "backup_dir": str(self.backup_dir)
                }
            }

            # Add performance metrics
            self.add_performance_metric("hooks_installed", self.git_metrics["hooks_installed"])
            self.add_performance_metric("staged_files_analyzed", self.git_metrics["staged_files_analyzed"])

            self.log_execution_step("Git Integration Setup", "completed", {
                "hooks_installed": self.git_metrics["hooks_installed"],
                "staged_files_analyzed": self.git_metrics["staged_files_analyzed"]
            })

            return results

        except Exception as e:
            self.log_error("Git integration setup failed", e)
            return {"status": "failed", "error": str(e)}

    def _find_git_root(self) -> Optional[Path]:
        """Find the root of the git repository"""
        current_path = Path.cwd()

        while current_path != current_path.parent:
            if (current_path / ".git").exists():
                return current_path
            current_path = current_path.parent

        return None

    def _validate_git_repository(self) -> bool:
        """Validate that we're in a valid git repository"""
        if not self.repo_root:
            self.log_error("Not in a git repository")
            return False

        if not self.hooks_dir or not self.hooks_dir.exists():
            self.log_error("Git hooks directory not found")
            return False

        # Test git command availability
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            self.log_error("Git command not available")
            return False

    def install_pre_commit_hooks(self) -> List[HookInstallationResult]:
        """
        Install pre-commit hooks for automated analysis.

        Returns:
            List of hook installation results
        """
        self.log_execution_step("Pre-commit Hook Installation", "started")

        hook_results = []

        # Install main pre-commit hook
        pre_commit_result = self._install_hook("pre-commit", self._generate_pre_commit_hook_content())
        hook_results.append(pre_commit_result)

        if pre_commit_result.installation_success:
            self.git_metrics["hooks_installed"] += 1

        # Install pre-push hook for additional analysis
        pre_push_result = self._install_hook("pre-push", self._generate_pre_push_hook_content())
        hook_results.append(pre_push_result)

        if pre_push_result.installation_success:
            self.git_metrics["hooks_installed"] += 1

        self.hook_installations.extend(hook_results)

        self.log_execution_step("Pre-commit Hook Installation", "completed", {
            "hooks_installed": len([r for r in hook_results if r.installation_success])
        })

        return hook_results

    def _install_hook(self, hook_name: str, hook_content: str) -> HookInstallationResult:
        """Install a specific git hook"""
        hook_path = self.hooks_dir / hook_name
        backup_path = ""

        try:
            # Create backup if hook already exists
            if hook_path.exists():
                backup_path = str(self.backup_dir / f"{hook_name}{self.git_config['hook_backup_suffix']}")
                shutil.copy2(hook_path, backup_path)
                self.logger.info(f"Backed up existing {hook_name} hook to {backup_path}")

            # Write new hook content
            with open(hook_path, 'w') as f:
                f.write(hook_content)

            # Make hook executable
            hook_path.chmod(0o755)

            return HookInstallationResult(
                hook_name=hook_name,
                installation_path=str(hook_path),
                installation_success=True,
                backup_created=backup_path,
                hook_content=hook_content,
                installation_details={
                    "timestamp": datetime.now().isoformat(),
                    "hook_size": len(hook_content),
                    "executable": True
                }
            )

        except Exception as e:
            self.logger.error(f"Failed to install {hook_name} hook: {e}")
            return HookInstallationResult(
                hook_name=hook_name,
                installation_path=str(hook_path),
                installation_success=False,
                backup_created=backup_path,
                hook_content=hook_content,
                installation_details={
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )

    def _generate_pre_commit_hook_content(self) -> str:
        """Generate pre-commit hook script content"""
        return '''#!/bin/bash
# Generated by Phase 14.1.3 GitOptimizationHooks
# Automated code analysis and optimization checks

set -e

echo "🔍 Running Phase 14 Codebase Analysis..."

# Get the directory of this script
HOOK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git rev-parse --show-toplevel)"
PHASE14_DIR="$REPO_ROOT/plc-gbt-stack/scripts/ai/phases/phase14"

# Check if Phase 14 analyzers are available
if [ ! -f "$PHASE14_DIR/codebase_analyzer.py" ]; then
    echo "⚠️  Phase 14 analyzers not found, skipping analysis"
    exit 0
fi

# Run staged file analysis
echo "📋 Analyzing staged changes..."
cd "$PHASE14_DIR"

python3 -c "
import sys
sys.path.append('.')
from git_integration_hooks import GitOptimizationHooks
hooks = GitOptimizationHooks()
analysis = hooks.analyze_staged_changes()
if analysis.commit_safety_score < 0.7:
    print('⚠️  Commit safety score too low:', analysis.commit_safety_score)
    print('Blocking issues:', analysis.blocking_issues)
    sys.exit(1)
else:
    print('✅ Commit safety checks passed')
    if analysis.optimization_recommendations:
        print('💡 Optimization recommendations:')
        for rec in analysis.optimization_recommendations[:3]:
            print(f'   - {rec}')
"

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo "❌ Pre-commit analysis failed"
    echo "Use 'git commit --no-verify' to bypass if necessary"
    exit 1
fi

echo "✅ Pre-commit analysis completed successfully"
exit 0
'''

    def _generate_pre_push_hook_content(self) -> str:
        """Generate pre-push hook script content"""
        return '''#!/bin/bash
# Generated by Phase 14.1.3 GitOptimizationHooks
# Pre-push dependency analysis

set -e

echo "🔍 Running pre-push dependency analysis..."

REPO_ROOT="$(git rev-parse --show-toplevel)"
PHASE14_DIR="$REPO_ROOT/plc-gbt-stack/scripts/ai/phases/phase14"

if [ ! -f "$PHASE14_DIR/dependency_graph_builder.py" ]; then
    echo "⚠️  Dependency analyzer not found, skipping analysis"
    exit 0
fi

echo "📊 Checking for circular dependencies..."
cd "$PHASE14_DIR"

python3 -c "
import sys
sys.path.append('.')
from dependency_graph_builder import DependencyGraphBuilder
builder = DependencyGraphBuilder()
result = builder.execute()
if result.get('status') == 'failed':
    print('❌ Dependency analysis failed')
    sys.exit(1)
graph_analysis = result.get('graph_analysis', {})
circular_deps = graph_analysis.get('circular_dependencies', [])
if circular_deps:
    print(f'⚠️  Found {len(circular_deps)} circular dependencies')
    print('Consider resolving before push')
else:
    print('✅ No circular dependencies found')
"

echo "✅ Pre-push analysis completed"
exit 0
'''

    def analyze_staged_changes(self) -> StagingAnalysis:
        """
        Analyze files in git staging area for optimization opportunities.

        Returns:
            Comprehensive analysis of staged changes
        """
        self.log_execution_step("Staged Change Analysis", "started")

        try:
            # Get list of staged files
            staged_files_info = self._get_staged_files()

            # Analyze each staged file
            staged_file_analyses = []
            blocking_issues = []
            optimization_recommendations = []

            for file_info in staged_files_info:
                if self._should_analyze_file(file_info['path']):
                    file_analysis = self._analyze_staged_file(file_info)
                    staged_file_analyses.append(file_analysis)

                    # Check for blocking issues
                    if file_analysis.optimization_priority == "high":
                        blocking_issues.append(f"High complexity in {file_analysis.file_path}")

                    # Generate recommendations
                    if file_analysis.complexity_change > 2.0:
                        optimization_recommendations.append(
                            f"Consider refactoring {Path(file_analysis.file_path).name} - complexity increased significantly"
                        )

            # Calculate commit safety score
            commit_safety_score = self._calculate_commit_safety_score(staged_file_analyses)

            # Generate suggested actions
            suggested_actions = self._generate_suggested_actions(staged_file_analyses, blocking_issues)

            self.git_metrics["staged_files_analyzed"] = len(staged_file_analyses)
            self.git_metrics["optimizations_suggested"] = len(optimization_recommendations)
            self.git_metrics["safety_checks_performed"] = 1

            analysis = StagingAnalysis(
                total_staged_files=len(staged_file_analyses),
                analysis_timestamp=datetime.now().isoformat(),
                staged_files=staged_file_analyses,
                optimization_recommendations=optimization_recommendations,
                blocking_issues=blocking_issues,
                commit_safety_score=commit_safety_score,
                estimated_analysis_time=f"{len(staged_file_analyses) * 0.5:.1f} seconds",
                suggested_actions=suggested_actions
            )

            self.staging_analysis = analysis

            self.log_execution_step("Staged Change Analysis", "completed", {
                "files_analyzed": len(staged_file_analyses),
                "safety_score": commit_safety_score
            })

            return analysis

        except Exception as e:
            self.logger.error(f"Staged change analysis failed: {e}")
            return StagingAnalysis(
                total_staged_files=0,
                analysis_timestamp=datetime.now().isoformat(),
                staged_files=[],
                optimization_recommendations=[],
                blocking_issues=[f"Analysis failed: {e}"],
                commit_safety_score=0.0,
                estimated_analysis_time="0 seconds",
                suggested_actions=["Fix analysis errors before proceeding"]
            )

    def _get_staged_files(self) -> List[Dict[str, Any]]:
        """Get list of files in git staging area"""
        try:
            # Get staged files with their status
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-status"],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode != 0:
                return []

            staged_files = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status = parts[0]
                        path = parts[1]

                        # Get line changes
                        lines_added, lines_removed = self._get_file_line_changes(path)

                        staged_files.append({
                            'status': status,
                            'path': path,
                            'lines_added': lines_added,
                            'lines_removed': lines_removed
                        })

            return staged_files

        except subprocess.SubprocessError as e:
            self.logger.error(f"Failed to get staged files: {e}")
            return []

    def _get_file_line_changes(self, file_path: str) -> Tuple[int, int]:
        """Get number of lines added and removed for a file"""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--numstat", file_path],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2:
                    lines_added = int(parts[0]) if parts[0] != '-' else 0
                    lines_removed = int(parts[1]) if parts[1] != '-' else 0
                    return lines_added, lines_removed

            return 0, 0

        except (subprocess.SubprocessError, ValueError):
            return 0, 0

    def _should_analyze_file(self, file_path: str) -> bool:
        """Check if file should be analyzed based on extension"""
        path = Path(file_path)
        return path.suffix in self.git_config["analysis_file_types"]

    def _analyze_staged_file(self, file_info: Dict[str, Any]) -> StagedFile:
        """Analyze a single staged file"""
        file_path = file_info['path']
        change_type = self._interpret_git_status(file_info['status'])
        lines_added = file_info['lines_added']
        lines_removed = file_info['lines_removed']

        # Simple complexity change calculation
        complexity_change = 0.0
        if lines_added > 50:
            complexity_change += 1.0
        if lines_added > 100:
            complexity_change += 1.0
        if lines_removed > 20:
            complexity_change -= 0.5

        # Determine optimization priority
        optimization_priority = "low"
        if complexity_change > 1.5 or lines_added > 100:
            optimization_priority = "high"
        elif complexity_change > 0.5 or lines_added > 50:
            optimization_priority = "medium"

        return StagedFile(
            file_path=file_path,
            change_type=change_type,
            lines_added=lines_added,
            lines_removed=lines_removed,
            complexity_change=complexity_change,
            optimization_priority=optimization_priority
        )

    def _interpret_git_status(self, status: str) -> str:
        """Interpret git status code to readable change type"""
        status_map = {
            'A': 'added',
            'M': 'modified',
            'D': 'deleted',
            'R': 'renamed',
            'C': 'copied'
        }
        return status_map.get(status[0], 'unknown')

    def _calculate_commit_safety_score(self, staged_files: List[StagedFile]) -> float:
        """Calculate safety score for the commit"""
        if not staged_files:
            return 1.0

        total_score = 0.0

        for staged_file in staged_files:
            file_score = 1.0

            # Penalize high complexity changes
            if staged_file.complexity_change > 2.0:
                file_score -= 0.3
            elif staged_file.complexity_change > 1.0:
                file_score -= 0.1

            # Penalize large changes
            if staged_file.lines_added > 200:
                file_score -= 0.2
            elif staged_file.lines_added > 100:
                file_score -= 0.1

            # Consider change type
            if staged_file.change_type == 'deleted':
                file_score += 0.1  # Deletions are generally safer
            elif staged_file.change_type == 'added':
                file_score -= 0.05  # New files need more scrutiny

            total_score += max(0.0, file_score)

        return min(1.0, total_score / len(staged_files))

    def _generate_suggested_actions(self, staged_files: List[StagedFile], blocking_issues: List[str]) -> List[str]:
        """Generate suggested actions based on analysis"""
        actions = []

        if blocking_issues:
            actions.append("Review and resolve blocking issues before committing")

        high_priority_files = [sf for sf in staged_files if sf.optimization_priority == "high"]
        if high_priority_files:
            actions.append(f"Consider reviewing {len(high_priority_files)} high-priority files")

        large_changes = [sf for sf in staged_files if sf.lines_added > 100]
        if large_changes:
            actions.append("Split large changes into smaller, focused commits")

        if not actions:
            actions.append("Proceed with commit - no issues detected")

        return actions

    def _generate_git_workflow_recommendations(self, staging_analysis: StagingAnalysis) -> List[str]:
        """Generate recommendations for git workflow optimization"""
        recommendations = []

        if staging_analysis.commit_safety_score < 0.5:
            recommendations.append("Consider breaking this commit into smaller, focused changes")

        if staging_analysis.total_staged_files > 10:
            recommendations.append("Large number of files - consider grouping related changes")

        if staging_analysis.optimization_recommendations:
            recommendations.append("Run codebase analysis on changed files before committing")

        recommendations.append("Use 'git add -p' for more granular staging")
        recommendations.append("Consider running dependency analysis before major commits")

        return recommendations

    def rollback_hooks(self) -> bool:
        """Rollback installed git hooks to previous state"""
        self.log_execution_step("Hook Rollback", "started")

        try:
            rollback_success = True

            for hook_result in self.hook_installations:
                if hook_result.installation_success and hook_result.backup_created:
                    hook_path = Path(hook_result.installation_path)
                    backup_path = Path(hook_result.backup_created)

                    if backup_path.exists():
                        shutil.copy2(backup_path, hook_path)
                        self.logger.info(f"Restored {hook_result.hook_name} from backup")
                    else:
                        hook_path.unlink(missing_ok=True)
                        self.logger.info(f"Removed {hook_result.hook_name} hook")
                elif hook_result.installation_success:
                    # Remove hook if no backup existed
                    hook_path = Path(hook_result.installation_path)
                    hook_path.unlink(missing_ok=True)
                    self.logger.info(f"Removed {hook_result.hook_name} hook")

            self.log_execution_step("Hook Rollback", "completed")
            return rollback_success

        except Exception as e:
            self.log_error("Hook rollback failed", e)
            return False

    def cleanup(self):
        """Cleanup temporary files and resources"""
        super().cleanup()

        # Clean up backup directory
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir, ignore_errors=True)
            self.logger.info(f"Cleaned up backup directory: {self.backup_dir}")
