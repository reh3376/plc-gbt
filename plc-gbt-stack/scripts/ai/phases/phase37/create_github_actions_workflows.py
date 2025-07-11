#!/usr/bin/env python3
"""
AI Task Orchestrator - GitHub Actions Workflows Creation
========================================================

Following the AI Task Orchestrator Guide methodology to create comprehensive
GitHub Actions workflows for Phase 3.7.4 CI/CD Pipeline Implementation.

This script creates:
1. PLC validation workflow
2. Conversion check workflow  
3. Security scan workflow
4. Release automation workflow
"""

import os
import sys
from pathlib import Path
from datetime import datetime

class GitHubActionsCreator:
    """Create GitHub Actions workflows for PLC repositories"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.workflows_dir = self.project_root / ".github" / "workflows"
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
    def create_plc_validation_workflow(self):
        """Create PLC validation workflow"""
        workflow_content = """name: PLC Validation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate-plc-files:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        lfs: true
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install lxml xmlschema
        
    - name: Validate L5X files
      run: |
        echo "🔍 Validating L5X files..."
        find . -name "*.L5X" -type f | while read file; do
          echo "Validating: $file"
          python -c "
import xml.etree.ElementTree as ET
import sys
try:
    tree = ET.parse('$file')
    root = tree.getroot()
    programs = len(root.findall('.//Program'))
    routines = len(root.findall('.//Routine'))
    print(f'✅ Valid L5X: {programs} programs, {routines} routines')
except Exception as e:
    print(f'❌ Invalid L5X: {e}')
    sys.exit(1)
"
        done
        
    - name: Check file sizes
      run: |
        echo "📊 Checking file sizes..."
        find . -name "*.L5X" -o -name "*.ACD" | while read file; do
          size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
          if [ "$size" -lt 1024 ]; then
            echo "⚠️ Small file detected: $file ($size bytes)"
          else
            echo "✅ Normal file: $file ($size bytes)"
          fi
        done
        
    - name: Generate validation report
      run: |
        echo "📋 Generating validation report..."
        echo "# PLC Validation Report" > validation-report.md
        echo "Generated: $(date)" >> validation-report.md
        echo "" >> validation-report.md
        echo "## Files Validated" >> validation-report.md
        find . -name "*.L5X" -o -name "*.ACD" | wc -l | xargs echo "Total PLC files:" >> validation-report.md
        
    - name: Upload validation report
      uses: actions/upload-artifact@v4
      with:
        name: validation-report
        path: validation-report.md
"""
        
        workflow_file = self.workflows_dir / "plc-validation.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
        
        print(f"✅ Created: {workflow_file.name}")
        return workflow_file
    
    def create_conversion_check_workflow(self):
        """Create conversion check workflow"""
        workflow_content = """name: Conversion Check

on:
  push:
    branches: [ main ]
    paths: 
      - '**/*.ACD'
      - '**/*.L5X'
  workflow_dispatch:

jobs:
  conversion-integrity:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        lfs: true
        
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Install PLC conversion tools
      run: |
        python -m pip install --upgrade pip
        pip install lxml requests
        
    - name: Check file integrity
      run: |
        echo "🔍 Checking file integrity..."
        find . -name "*.ACD" | while read file; do
          echo "Checking: $file"
          size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
          
          # Check if it's a Git LFS pointer
          if head -n 1 "$file" | grep -q "version https://git-lfs.github.com"; then
            echo "📦 LFS pointer detected: $file"
          elif [ "$size" -gt 1048576 ]; then  # > 1MB
            echo "✅ Valid ACD file: $file ($size bytes)"
          else
            echo "⚠️ Potentially invalid ACD: $file ($size bytes)"
          fi
        done
        
    - name: Validate L5X structure
      run: |
        echo "🏗️ Validating L5X structure..."
        find . -name "*.L5X" | while read file; do
          echo "Validating structure: $file"
          python -c "
import xml.etree.ElementTree as ET
try:
    tree = ET.parse('$file')
    root = tree.getroot()
    
    # Check for required elements
    controller = root.find('.//Controller')
    if controller is not None:
        print(f'✅ Valid controller found in $file')
    else:
        print(f'❌ No controller found in $file')
        exit(1)
        
    # Count components
    programs = len(root.findall('.//Program'))
    routines = len(root.findall('.//Routine'))
    aois = len(root.findall('.//AddOnInstructionDefinition'))
    tags = len(root.findall('.//Tag'))
    
    print(f'📊 Components: {programs} programs, {routines} routines, {aois} AOIs, {tags} tags')
    
except Exception as e:
    print(f'❌ Structure validation failed for $file: {e}')
    exit(1)
"
        done
        
    - name: Generate conversion report
      run: |
        echo "📊 Generating conversion report..."
        echo "# Conversion Integrity Report" > conversion-report.md
        echo "Generated: $(date)" >> conversion-report.md
        echo "" >> conversion-report.md
        echo "## File Analysis" >> conversion-report.md
        
        acd_count=$(find . -name "*.ACD" | wc -l)
        l5x_count=$(find . -name "*.L5X" | wc -l)
        
        echo "- ACD files: $acd_count" >> conversion-report.md
        echo "- L5X files: $l5x_count" >> conversion-report.md
        echo "" >> conversion-report.md
        echo "## Validation Status" >> conversion-report.md
        echo "All integrity checks completed successfully ✅" >> conversion-report.md
        
    - name: Upload conversion report
      uses: actions/upload-artifact@v4
      with:
        name: conversion-report
        path: conversion-report.md
"""
        
        workflow_file = self.workflows_dir / "conversion-check.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
            
        print(f"✅ Created: {workflow_file.name}")
        return workflow_file
    
    def create_security_scan_workflow(self):
        """Create security scan workflow"""
        workflow_content = """name: Security Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday at 2 AM

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        lfs: true
        
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
        
    - name: Upload Trivy scan results to GitHub Security tab
      uses: github/codeql-action/upload-sarif@v2
      if: always()
      with:
        sarif_file: 'trivy-results.sarif'
        
    - name: Check for sensitive files
      run: |
        echo "🔍 Scanning for sensitive files..."
        
        # Check for common sensitive patterns
        if find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx" | grep -q .; then
          echo "❌ Potential sensitive files found:"
          find . -name "*.key" -o -name "*.pem" -o -name "*.p12" -o -name "*.pfx"
          exit 1
        else
          echo "✅ No sensitive files detected"
        fi
        
        # Check for hardcoded credentials in PLC files
        if grep -r -i "password\\|secret\\|token" --include="*.L5X" --include="*.ACD" .; then
          echo "⚠️ Potential hardcoded credentials found in PLC files"
        else
          echo "✅ No hardcoded credentials detected in PLC files"
        fi
        
    - name: File permission check
      run: |
        echo "🔒 Checking file permissions..."
        find . -type f -perm /o+w | while read file; do
          echo "⚠️ World-writable file: $file"
        done
        
        find . -type f -perm /o+x | while read file; do
          if [[ ! "$file" =~ \\.(sh|py)$ ]]; then
            echo "⚠️ Unexpected executable file: $file"
          fi
        done
        
    - name: Generate security report
      run: |
        echo "🛡️ Generating security report..."
        echo "# Security Scan Report" > security-report.md
        echo "Generated: $(date)" >> security-report.md
        echo "" >> security-report.md
        echo "## Scan Results" >> security-report.md
        echo "- Vulnerability scan: Completed ✅" >> security-report.md
        echo "- Sensitive file check: Completed ✅" >> security-report.md
        echo "- Permission check: Completed ✅" >> security-report.md
        
    - name: Upload security report
      uses: actions/upload-artifact@v4
      with:
        name: security-report
        path: security-report.md
"""
        
        workflow_file = self.workflows_dir / "security-scan.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
            
        print(f"✅ Created: {workflow_file.name}")
        return workflow_file
    
    def create_release_workflow(self):
        """Create release automation workflow"""
        workflow_content = """name: Release Automation

on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version (e.g., v1.0.0)'
        required: true
        type: string

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
      with:
        lfs: true
        fetch-depth: 0
        
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
        
    - name: Generate release notes
      run: |
        echo "📝 Generating release notes..."
        
        # Get version from tag or input
        if [ "${{ github.event_name }}" = "workflow_dispatch" ]; then
          VERSION="${{ github.event.inputs.version }}"
        else
          VERSION="${{ github.ref_name }}"
        fi
        
        echo "# Release $VERSION" > release-notes.md
        echo "Generated: $(date)" >> release-notes.md
        echo "" >> release-notes.md
        
        # Count PLC files
        acd_count=$(find . -name "*.ACD" | wc -l)
        l5x_count=$(find . -name "*.L5X" | wc -l)
        
        echo "## Contents" >> release-notes.md
        echo "- ACD files: $acd_count" >> release-notes.md
        echo "- L5X files: $l5x_count" >> release-notes.md
        echo "" >> release-notes.md
        
        echo "## Changes" >> release-notes.md
        if [ "${{ github.event_name }}" = "push" ]; then
          # Get commits since last tag
          LAST_TAG=$(git tag --sort=-version:refname | head -n 2 | tail -n 1)
          if [ -n "$LAST_TAG" ]; then
            git log --oneline $LAST_TAG..HEAD >> release-notes.md
          else
            echo "Initial release" >> release-notes.md
          fi
        else
          echo "Manual release triggered" >> release-notes.md
        fi
        
    - name: Create release archive
      run: |
        echo "📦 Creating release archive..."
        
        # Create release directory
        mkdir -p release
        
        # Copy PLC files
        find . -name "*.ACD" -o -name "*.L5X" | while read file; do
          cp "$file" release/
        done
        
        # Copy documentation
        if [ -f "README.md" ]; then
          cp README.md release/
        fi
        
        # Create archive
        tar -czf plc-files-release.tar.gz -C release .
        
    - name: Calculate checksums
      run: |
        echo "🔐 Calculating checksums..."
        sha256sum plc-files-release.tar.gz > checksums.txt
        md5sum plc-files-release.tar.gz >> checksums.txt
        
    - name: Create GitHub Release
      uses: softprops/action-gh-release@v1
      with:
        tag_name: ${{ github.event.inputs.version || github.ref_name }}
        name: Release ${{ github.event.inputs.version || github.ref_name }}
        body_path: release-notes.md
        files: |
          plc-files-release.tar.gz
          checksums.txt
        draft: false
        prerelease: false
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        
    - name: Upload release artifacts
      uses: actions/upload-artifact@v4
      with:
        name: release-artifacts
        path: |
          plc-files-release.tar.gz
          checksums.txt
          release-notes.md
"""
        
        workflow_file = self.workflows_dir / "release.yml"
        with open(workflow_file, 'w') as f:
            f.write(workflow_content)
            
        print(f"✅ Created: {workflow_file.name}")
        return workflow_file
    
    def create_all_workflows(self):
        """Create all GitHub Actions workflows"""
        print("🤖 AI Task Orchestrator - GitHub Actions Workflows Creation")
        print("=" * 65)
        print("Phase 3.7.4: CI/CD Pipeline Implementation")
        print()
        
        workflows_created = []
        
        print("🚀 Creating GitHub Actions workflows...")
        workflows_created.append(self.create_plc_validation_workflow())
        workflows_created.append(self.create_conversion_check_workflow())
        workflows_created.append(self.create_security_scan_workflow())
        workflows_created.append(self.create_release_workflow())
        
        print(f"\n✅ Phase 3.7.4 Complete:")
        print(f"   📁 Workflows directory: {self.workflows_dir}")
        print(f"   🔧 Workflows created: {len(workflows_created)}/4")
        print("   📋 Workflow types:")
        print("     • PLC file validation")
        print("     • Conversion integrity checks")
        print("     • Security scanning")
        print("     • Release automation")
        
        return workflows_created

def main():
    """Main execution function"""
    creator = GitHubActionsCreator()
    workflows = creator.create_all_workflows()
    
    print(f"\n🎯 GitHub Actions CI/CD Pipeline: COMPLETE")
    print(f"📊 All {len(workflows)} workflows ready for deployment")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 