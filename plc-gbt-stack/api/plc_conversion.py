"""
Minimal PLC Conversion API Router

Provides basic endpoints for conversion and validation using the local
`plc_format_converter` library. This is an MVP to stabilize the backend.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/conversion", tags=["PLC Conversion"])


class ConversionRequest(BaseModel):
    input_path: str = Field(..., description="Path to source file (.acd or .l5x)")
    output_path: str = Field(..., description="Path to write converted file")


class ValidationRequest(BaseModel):
    file_path: str = Field(..., description="Path to file (.acd or .l5x)")


class ConversionResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


def _safe_mkdir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


@router.post("/convert", response_model=ConversionResponse)
def convert_file(request: ConversionRequest) -> ConversionResponse:
    """Minimal conversion: copy file with basic extension checks.

    This stabilizes the API surface while the full converter matures.
    """
    src = Path(request.input_path)
    dst = Path(request.output_path)

    if not src.exists():
        return ConversionResponse(success=False, message=f"Source not found: {src}")

    if src.suffix.lower() not in {".acd", ".l5x"}:
        return ConversionResponse(success=False, message="Unsupported input type (expect .acd or .l5x)")

    # For MVP, perform safe copy; future: real ACD↔L5X conversion
    try:
        _safe_mkdir(dst)
        dst.write_bytes(src.read_bytes())
        return ConversionResponse(
            success=True,
            message="File converted (pass-through MVP)",
            data={"input": str(src), "output": str(dst), "bytes": dst.stat().st_size},
        )
    except Exception as e:  # pragma: no cover - IO safety
        return ConversionResponse(success=False, message=f"Conversion failed: {e}")


@router.post("/validate", response_model=ConversionResponse)
def validate_file(request: ValidationRequest) -> ConversionResponse:
    """Minimal validation: existence + non-empty + known extension."""
    path = Path(request.file_path)
    if not path.exists():
        return ConversionResponse(success=False, message=f"File not found: {path}")

    if path.suffix.lower() not in {".acd", ".l5x"}:
        return ConversionResponse(success=False, message="Unsupported file type (expect .acd or .l5x)")

    size = path.stat().st_size
    if size == 0:
        return ConversionResponse(success=False, message="File is empty")

    return ConversionResponse(
        success=True,
        message="Validation passed",
        data={"file": str(path), "bytes": size},
    )


