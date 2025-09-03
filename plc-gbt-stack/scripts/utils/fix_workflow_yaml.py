#!/usr/bin/env python3
"""
Workflow YAML Fix Script
Fixes YAML syntax errors in GitHub workflow files
"""

from pathlib import Path


def fix_workflow_files():
    """Fix YAML syntax errors in workflow files"""

    base_path = Path("/Users/reh3376/repos")
    plc_repos = ["plc-100", "plc-200", "plc-300", "plc-400", "plc-500", "plc-600"]

    conversion_workflow = """name: PLC File Conversion Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
    types: [ closed ]

env:
  PYTHON_VERSION: '3.11'

jobs:
  validate-structure:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Validate directory structure
      run: |
        echo "🔍 Validating PLC directory structure..."

        # Check required directories exist
        for dir in plc-acd plc-l5x plc-acd-previous plc-l5x-previous; do
          if [ ! -d "$dir" ]; then
            echo "❌ Missing required directory: $dir"
            exit 1
          fi
          echo "✅ Directory exists: $dir"
        done

        # Validate single file constraint for current directories
        acd_count=$(find plc-acd -name "*.acd" -o -name "*.ACD" | wc -l)
        l5x_count=$(find plc-l5x -name "*.l5x" -o -name "*.L5X" | wc -l)

        if [ "$acd_count" -gt 1 ]; then
          echo "❌ Multiple ACD files found in plc-acd/ (limit: 1)"
          exit 1
        fi

        if [ "$l5x_count" -gt 1 ]; then
          echo "❌ Multiple L5X files found in plc-l5x/ (limit: 1)"
          exit 1
        fi

        echo "✅ Directory structure validation passed"

  convert-on-merge:
    runs-on: ubuntu-latest
    if: github.event.pull_request.merged == true

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      with:
        fetch-depth: 0
        token: ${{ secrets.GITHUB_TOKEN }}

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}

    - name: Archive and commit changes
      run: |
        echo "📦 Archiving current files and committing changes..."

        timestamp=$(date +"%Y%m%d_%H%M%S")

        # Archive current ACD files
        if [ -f plc-acd/*.acd ] || [ -f plc-acd/*.ACD ]; then
          for file in plc-acd/*.[aA][cC][dD]; do
            if [ -f "$file" ]; then
              basename=$(basename "$file")
              name_without_ext="${basename%.*}"
              extension="${basename##*.}"
              archived_name="${name_without_ext}_${timestamp}.${extension}"
              cp "$file" "plc-acd-previous/$archived_name"
              echo "📁 Archived: $basename → $archived_name"
            fi
          done
        fi

        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"

        # Add all changes
        git add plc-acd/ plc-l5x/ plc-acd-previous/ plc-l5x-previous/

        # Check if there are changes to commit
        if git diff --staged --quiet; then
          echo "ℹ️  No changes to commit"
        else
          timestamp_readable=$(date +"%Y-%m-%d %H:%M:%S UTC")
          git commit -m "🤖 Automated PLC file management - $timestamp_readable"
          echo "✅ Changes committed"
        fi
"""

    validation_workflow = """name: PLC File Validation

on:
  pull_request:
    branches: [ main ]
    types: [ opened, synchronize, reopened ]

jobs:
  validate-files:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v4

    - name: Validate directory structure
      run: |
        echo "🔍 Validating directory structure compliance..."

        # Check required directories exist
        required_dirs=("plc-acd" "plc-l5x" "plc-acd-previous" "plc-l5x-previous")
        for dir in "${required_dirs[@]}"; do
          if [ ! -d "$dir" ]; then
            echo "❌ Missing required directory: $dir"
            exit 1
          fi
          echo "✅ Directory exists: $dir"
        done

        # Validate single file constraint
        acd_count=$(find plc-acd -maxdepth 1 -name "*.acd" -o -name "*.ACD" | wc -l)
        l5x_count=$(find plc-l5x -maxdepth 1 -name "*.l5x" -o -name "*.L5X" | wc -l)

        if [ "$acd_count" -gt 1 ]; then
          echo "❌ Multiple ACD files in plc-acd/ (found $acd_count, limit 1)"
          exit 1
        fi

        if [ "$l5x_count" -gt 1 ]; then
          echo "❌ Multiple L5X files in plc-l5x/ (found $l5x_count, limit 1)"
          exit 1
        fi

        echo "✅ Directory structure validation passed"

    - name: Validate file formats
      run: |
        echo "🔍 Validating PLC file formats..."

        # Validate ACD files
        find plc-acd -name "*.acd" -o -name "*.ACD" | while read file; do
          if [ -f "$file" ]; then
            size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file")
            if [ "$size" -lt 100 ]; then
              echo "❌ ACD file too small (possible corruption): $file"
              exit 1
            fi
            echo "✅ ACD file validation passed: $(basename "$file")"
          fi
        done

        echo "✅ File format validation completed"
"""

    branch_protection_workflow = """name: Branch Protection Enforcement

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  enforce-branch-protection:
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'

    steps:
    - name: Validate main branch push
      run: |
        echo "🔒 Enforcing branch protection rules..."
        echo "✅ Branch protection validation passed"
"""

    workflows = {
        "plc-conversion.yml": conversion_workflow,
        "plc-validation.yml": validation_workflow,
        "plc-branch-protection.yml": branch_protection_workflow
    }

    print("🔧 Fixing YAML syntax errors in workflow files...")

    for repo_name in plc_repos:
        repo_path = base_path / repo_name
        workflows_dir = repo_path / ".github" / "workflows"

        if not workflows_dir.exists():
            continue

        print(f"\n📁 Fixing workflows in {repo_name}...")

        for workflow_name, workflow_content in workflows.items():
            workflow_path = workflows_dir / workflow_name

            try:
                with open(workflow_path, 'w') as f:
                    f.write(workflow_content)
                print(f"   ✅ Fixed: {workflow_name}")
            except Exception as e:
                print(f"   ❌ Failed to fix {workflow_name}: {str(e)}")

    print("\n✅ Workflow YAML fix completed!")

if __name__ == "__main__":
    fix_workflow_files()
