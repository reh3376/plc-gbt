"""
PLC ACD/L5X Conversion Models - Phase 35.1
Following AI Task Orchestrator methodology with strict type safety
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator


class ConversionStatus(str, Enum):
    """Status of conversion operation"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class OptimizationLevel(str, Enum):
    """Conversion optimization level"""
    NONE = "none"
    BASIC = "basic"
    FULL = "full"


class ConversionOptions(BaseModel):
    """Options for ACD to L5X conversion"""
    preserve_comments: bool = Field(True, description="Preserve comments from ACD file")
    expand_data_types: bool = Field(True, description="Expand complex data types")
    include_documentation: bool = Field(True, description="Include inline documentation")
    target_version: Optional[str] = Field(None, description="Target L5X version")
    optimization_level: OptimizationLevel = Field(OptimizationLevel.BASIC, description="Optimization level")

    class Config:
        use_enum_values = True


class ValidationResult(BaseModel):
    """Validation result for ACD/L5X files"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    file_info: Dict[str, str] = Field(default_factory=dict)


class ConversionProgress(BaseModel):
    """Progress tracking for conversion operations"""
    file_name: str
    status: ConversionStatus
    progress_percentage: int = Field(ge=0, le=100)
    current_step: str
    estimated_time_remaining: Optional[int] = Field(None, description="Seconds remaining")

    @validator('progress_percentage')
    def validate_progress(cls, v: int) -> int:
        """Ensure progress is between 0 and 100"""
        return max(0, min(100, v))


class L5XOutput(BaseModel):
    """L5X conversion output"""
    file_name: str
    content: str
    size_bytes: int
    conversion_time_ms: int
    validation_result: ValidationResult
    metadata: Dict[str, str] = Field(default_factory=dict)


class ConversionResult(BaseModel):
    """Complete conversion result with validation"""
    l5x_content: str
    validation_report: 'ValidationReport'
    conversion_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationReport(BaseModel):
    """Comprehensive validation report"""
    pre_conversion: ValidationResult
    post_conversion: ValidationResult
    functionally_identical: bool
    conversion_score: float = Field(ge=0.0, le=1.0)
    details: Dict[str, str] = Field(default_factory=dict)


class BatchConversionRequest(BaseModel):
    """Request for batch ACD to L5X conversion"""
    file_ids: List[str]
    options: ConversionOptions = Field(default_factory=ConversionOptions)
    priority: int = Field(5, ge=1, le=10, description="Priority level 1-10")


class ConversionJobStatus(BaseModel):
    """Status of a conversion job"""
    job_id: str
    status: ConversionStatus
    files_total: int
    files_completed: int
    files_failed: int
    start_time: datetime
    end_time: Optional[datetime] = None
    error_messages: List[str] = Field(default_factory=list)


# Forward reference resolution
ConversionResult.model_rebuild()
