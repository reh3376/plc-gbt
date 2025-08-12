"""
PLC Git Integration Service Package - Phase 35.2
"""

from .diff_engine import PLCDiffEngine
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
    PLCFileType,
    PLCMetadata,
    ProgramDiff,
    PullRequest,
    RoutineDiff,
    TagDiff,
)
from .service import PLCGitService

__all__ = [
    "PLCGitService",
    "PLCDiffEngine",
    "GitRepository",
    "PLCFile",
    "PLCFileType",
    "GitBranch",
    "GitCommit",
    "PLCMetadata",
    "PLCDiff",
    "RoutineDiff",
    "TagDiff",
    "ProgramDiff",
    "DiffSummary",
    "DiffType",
    "MergeResult",
    "MergeStatus",
    "MergeConflict",
    "PullRequest",
]
