"""
PLC Git Integration Models - Phase 35.2
Git operations models for PLC file version control
Following AI Task Orchestrator methodology
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class MergeStatus(str, Enum):
    """Status of merge operation"""
    SUCCESS = "success"
    CONFLICT = "conflict"
    FAILED = "failed"


class DiffType(str, Enum):
    """Type of difference in PLC files"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


class PLCFileType(str, Enum):
    """Supported PLC file types"""
    ACD = "acd"
    L5X = "l5x"


class GitRepository(BaseModel):
    """Git repository information"""
    path: str
    name: str
    remote_url: Optional[str] = None
    current_branch: str
    is_dirty: bool = False
    last_commit_hash: Optional[str] = None
    
    class Config:
        use_enum_values = True


class PLCFile(BaseModel):
    """PLC file in Git repository"""
    path: str
    name: str
    file_type: PLCFileType
    size_bytes: int
    last_modified: datetime
    git_status: Optional[str] = None


class GitBranch(BaseModel):
    """Git branch information"""
    name: str
    is_current: bool
    commit_hash: str
    commit_message: str
    commit_date: datetime
    ahead: int = 0
    behind: int = 0


class GitCommit(BaseModel):
    """Git commit information"""
    hash: str
    author_name: str
    author_email: str
    date: datetime
    message: str
    parent_hashes: List[str] = Field(default_factory=list)
    files_changed: int = 0


class PLCMetadata(BaseModel):
    """Metadata for PLC files in Git"""
    controller_name: Optional[str] = None
    processor_type: Optional[str] = None
    program_name: Optional[str] = None
    version: Optional[str] = None
    last_modified_by: Optional[str] = None
    safety_status: Optional[str] = None
    tags_count: Optional[int] = None
    routines_count: Optional[int] = None


class RoutineDiff(BaseModel):
    """Difference in PLC routine"""
    name: str
    diff_type: DiffType
    line_changes_added: int = 0
    line_changes_removed: int = 0
    description: Optional[str] = None


class TagDiff(BaseModel):
    """Difference in PLC tags"""
    name: str
    diff_type: DiffType
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    data_type: Optional[str] = None


class DataTypeDiff(BaseModel):
    """Difference in PLC data types"""
    name: str
    diff_type: DiffType
    members_added: List[str] = Field(default_factory=list)
    members_removed: List[str] = Field(default_factory=list)
    members_modified: List[str] = Field(default_factory=list)


class ProgramDiff(BaseModel):
    """Difference in PLC programs"""
    name: str
    diff_type: DiffType
    routines_affected: List[str] = Field(default_factory=list)
    tags_affected: List[str] = Field(default_factory=list)


class PLCDiff(BaseModel):
    """Complete PLC file diff"""
    file_a: str
    file_b: str
    routines: List[RoutineDiff] = Field(default_factory=list)
    tags: List[TagDiff] = Field(default_factory=list)
    data_types: List[DataTypeDiff] = Field(default_factory=list)
    programs: List[ProgramDiff] = Field(default_factory=list)
    summary: 'DiffSummary'


class DiffSummary(BaseModel):
    """Summary of PLC diff"""
    total_changes: int
    routines_added: int = 0
    routines_modified: int = 0
    routines_deleted: int = 0
    tags_added: int = 0
    tags_modified: int = 0
    tags_deleted: int = 0
    has_safety_impact: bool = False
    requires_review: bool = False


class MergeResult(BaseModel):
    """Result of merge operation"""
    status: MergeStatus
    merged_content: Optional[str] = None
    conflicts: List['MergeConflict'] = Field(default_factory=list)
    auto_resolved_count: int = 0
    manual_conflicts_count: int = 0
    merge_commit_hash: Optional[str] = None


class MergeConflict(BaseModel):
    """Merge conflict details"""
    file_path: str
    conflict_type: str
    base_content: str
    ours_content: str
    theirs_content: str
    line_number: Optional[int] = None
    routine_name: Optional[str] = None
    tag_name: Optional[str] = None


class PullRequest(BaseModel):
    """Pull request for PLC changes"""
    id: int
    title: str
    description: str
    source_branch: str
    target_branch: str
    author: str
    created_at: datetime
    updated_at: datetime
    status: str = "open"
    reviewers: List[str] = Field(default_factory=list)
    diff: Optional[PLCDiff] = None
    metadata: Dict[str, any] = Field(default_factory=dict)


# Forward reference resolution
PLCDiff.model_rebuild()
MergeResult.model_rebuild()
