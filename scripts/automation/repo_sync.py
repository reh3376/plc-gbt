"""
Repository Sync Utility

Synchronize external PLC repositories (plc-100..plc-500) into local workspace.

Usage:
  python scripts/automation/repo_sync.py --config scripts/automation/repo_sync.yaml
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class RepoSpec:
    name: str
    url: str
    branch: str = "main"
    dest: str = "external"


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.check_call(cmd, cwd=str(cwd) if cwd else None)


def ensure_repo(spec: RepoSpec, root: Path) -> None:
    dest_dir = root / spec.dest / spec.name
    dest_dir.parent.mkdir(parents=True, exist_ok=True)
    if not dest_dir.exists():
        run(["git", "clone", "--depth", "1", "--branch", spec.branch, spec.url, str(dest_dir)])
    else:
        run(["git", "fetch", "origin"], cwd=dest_dir)
        run(["git", "checkout", spec.branch], cwd=dest_dir)
        run(["git", "pull", "--ff-only", "origin", spec.branch], cwd=dest_dir)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to repo_sync.yaml")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    cfg_path = Path(args.config)
    data = yaml.safe_load(cfg_path.read_text())
    repos = [RepoSpec(**item) for item in data.get("repos", [])]
    for r in repos:
        ensure_repo(r, root)
    print(f"✅ Synced {len(repos)} repositories")


if __name__ == "__main__":
    main()


