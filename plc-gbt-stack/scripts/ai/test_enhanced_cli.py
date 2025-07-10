#!/usr/bin/env python3
"""
🧪 Test Script for Enhanced CLI Functionality

This script demonstrates the new CLI capabilities for flexible file and directory ingestion.
Tests various combinations of input options to validate the enhanced ingest command.

Author: AI Task Orchestrator  
Created: 2025-01-09
Purpose: Validate enhanced CLI with selective ingestion capabilities
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

def create_test_project():
    """Create a temporary test project structure"""
    temp_dir = tempfile.mkdtemp(prefix="plc_cli_test_")
    
    # Create directory structure
    (Path(temp_dir) / "src").mkdir()
    (Path(temp_dir) / "tests").mkdir()
    (Path(temp_dir) / "docs").mkdir()
    (Path(temp_dir) / "logs").mkdir()
    (Path(temp_dir) / "__pycache__").mkdir()
    
    # Create test files
    test_files = {
        "main.py": "# Main application file\ndef main():\n    print('Hello World')\n",
        "config.json": '{"database": "postgresql", "host": "localhost"}',
        "src/app.py": "# Application logic\nclass Application:\n    def run(self):\n        pass\n",
        "src/utils.py": "# Utility functions\ndef helper():\n    return True\n",
        "tests/test_app.py": "# Test file\ndef test_app():\n    assert True\n",
        "docs/README.md": "# Documentation\nThis is a test project\n",
        "logs/app.log": "2025-01-09 INFO: Application started\n",
        "__pycache__/cache.pyc": "compiled cache file",
    }
    
    for file_path, content in test_files.items():
        full_path = Path(temp_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    return temp_dir

def run_cli_command(args, cwd=None):
    """Run a CLI command and capture output"""
    try:
        cmd = ["python", "plc_memory_cli.py"] + args
        result = subprocess.run(
            cmd, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            timeout=30
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"
    except Exception as e:
        return -1, "", str(e)

def test_cli_functionality():
    """Test various CLI ingestion options"""
    
    print("🧪 Enhanced CLI Test Suite")
    print("=" * 50)
    
    # Create test project
    test_dir = create_test_project()
    print(f"📁 Created test project: {test_dir}")
    
    # Change to test directory
    original_cwd = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # Test 1: Show help for ingest command
        print("\n1️⃣  Testing help output...")
        returncode, stdout, stderr = run_cli_command(["ingest", "--help"])
        if returncode == 0:
            print("✅ Help command successful")
        else:
            print(f"❌ Help command failed: {stderr}")
        
        # Test 2: Dry run with --all option
        print("\n2️⃣  Testing --all dry run...")
        returncode, stdout, stderr = run_cli_command(["ingest", "--all", "--dry-run"])
        if returncode == 0:
            print("✅ --all dry run successful")
            print(f"📊 Output: {stdout[:200]}...")
        else:
            print(f"❌ --all dry run failed: {stderr}")
        
        # Test 3: Dry run with specific directories
        print("\n3️⃣  Testing specific directories...")
        returncode, stdout, stderr = run_cli_command([
            "ingest", "--directories", "src", "--directories", "tests", "--dry-run"
        ])
        if returncode == 0:
            print("✅ Specific directories dry run successful")
            print(f"📊 Output: {stdout[:200]}...")
        else:
            print(f"❌ Specific directories failed: {stderr}")
        
        # Test 4: Dry run with specific files
        print("\n4️⃣  Testing specific files...")
        returncode, stdout, stderr = run_cli_command([
            "ingest", "--files", "main.py", "--files", "config.json", "--dry-run"
        ])
        if returncode == 0:
            print("✅ Specific files dry run successful")
            print(f"📊 Output: {stdout[:200]}...")
        else:
            print(f"❌ Specific files failed: {stderr}")
        
        # Test 5: Test exclusion patterns
        print("\n5️⃣  Testing exclusion patterns...")
        returncode, stdout, stderr = run_cli_command([
            "ingest", "--all", "--exclude", "*.log", "--exclude", "__pycache__", "--dry-run"
        ])
        if returncode == 0:
            print("✅ Exclusion patterns dry run successful")
            print(f"📊 Output: {stdout[:200]}...")
        else:
            print(f"❌ Exclusion patterns failed: {stderr}")
        
        # Test 6: Mixed approach (paths + specific files)
        print("\n6️⃣  Testing mixed approach...")
        returncode, stdout, stderr = run_cli_command([
            "ingest", "docs", "--files", "main.py", "--dry-run"
        ])
        if returncode == 0:
            print("✅ Mixed approach dry run successful")
            print(f"📊 Output: {stdout[:200]}...")
        else:
            print(f"❌ Mixed approach failed: {stderr}")
        
        # Test 7: Error handling (non-existent path)
        print("\n7️⃣  Testing error handling...")
        returncode, stdout, stderr = run_cli_command([
            "ingest", "nonexistent_directory", "--dry-run"
        ])
        if returncode != 0:
            print("✅ Error handling working (expected failure)")
        else:
            print("❌ Error handling not working (should have failed)")
        
        # Test 8: No input validation
        print("\n8️⃣  Testing input validation...")
        returncode, stdout, stderr = run_cli_command(["ingest"])
        if returncode != 0:
            print("✅ Input validation working (expected failure)")
        else:
            print("❌ Input validation not working (should have failed)")
            
    except Exception as e:
        print(f"❌ Test suite error: {e}")
    finally:
        # Cleanup
        os.chdir(original_cwd)
        import shutil
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")

def demonstrate_cli_usage():
    """Demonstrate various CLI usage patterns"""
    
    print("\n" + "=" * 60)
    print("📚 CLI USAGE DEMONSTRATION")
    print("=" * 60)
    
    examples = [
        {
            "title": "Ingest entire project",
            "command": "plc-memory ingest --all",
            "description": "Processes all files in current directory and subdirectories"
        },
        {
            "title": "Ingest specific directories",
            "command": "plc-memory ingest src tests docs",
            "description": "Processes only specified directories"
        },
        {
            "title": "Ingest specific files",
            "command": "plc-memory ingest --files main.py --files config.json",
            "description": "Processes only the specified files"
        },
        {
            "title": "Mixed ingestion with exclusions",
            "command": "plc-memory ingest --directories src --files main.py --exclude '*.log' --exclude '__pycache__'",
            "description": "Combines directories and files, excludes patterns"
        },
        {
            "title": "Intelligent method with settings",
            "command": "plc-memory ingest --all --method intelligent --max-concurrent 5 --depth semantic",
            "description": "Uses AI Task Orchestrator with custom settings"
        },
        {
            "title": "Legacy method for large projects",
            "command": "plc-memory ingest --all --method legacy --verbose",
            "description": "Uses sequential processing with detailed output"
        },
        {
            "title": "Dry run preview",
            "command": "plc-memory ingest --directories src tests --dry-run",
            "description": "Shows what would be processed without actual ingestion"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}️⃣  {example['title']}")
        print(f"   Command: {example['command']}")
        print(f"   Description: {example['description']}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced CLI Test Suite...")
    
    # Run the tests
    test_cli_functionality()
    
    # Show usage examples
    demonstrate_cli_usage()
    
    print("\n✅ Test suite completed!")
    print("\n💡 TIP: Run 'python plc_memory_cli.py ingest --help' for full command details") 