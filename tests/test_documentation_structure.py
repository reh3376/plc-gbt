"""Regression tests for the documentation re-alignment."""
from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_text(path: Path) -> str:
    """Return the contents of *path* as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def test_readme_describes_incomplete_state() -> None:
    """README should accurately describe the current project status."""
    readme = read_text(PROJECT_ROOT / "README.md")

    assert "still in early development" in readme
    assert "Legacy documentation" in readme
    assert "quarantine" in readme, "README should mention the quarantine directories"


def test_canonical_docs_are_present() -> None:
    """Key documentation files must exist after the refresh."""
    docs_dir = PROJECT_ROOT / "docs"
    expected = [
        "CODEBASE_REVIEW_V2.md",
        "DEVELOPMENT_GUIDE.md",
        "FSD_ALIGNMENT_PLAN.md",
        "plc_memory_system_overview.md",
        "workflow_node_creation_guide.md",
    ]

    missing = [name for name in expected if not (docs_dir / name).exists()]
    assert not missing, f"Missing expected documentation files: {missing}"


def test_development_guide_links_to_review() -> None:
    """Ensure the development guide references the codebase review."""
    guide = read_text(PROJECT_ROOT / "docs" / "DEVELOPMENT_GUIDE.md")
    assert "CODEBASE_REVIEW_V2.md" in guide


def test_quarantine_directories_are_signposted() -> None:
    """The quarantine notice should warn contributors about legacy content."""
    quarantine_notice = read_text(PROJECT_ROOT / "quarantine" / "README.md")

    lowered = quarantine_notice.lower()
    assert "legacy" in lowered
    assert "historical" in lowered or "reference" in lowered
    assert "do not rely" in lowered


def test_quarantined_roadmap_retained_for_history() -> None:
    """Legacy roadmap should now live under docs/quarantine."""
    roadmap_path = PROJECT_ROOT / "docs" / "quarantine" / "roadmap.md"
    assert roadmap_path.exists()
    assert "Phase" in read_text(roadmap_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
