#!/usr/bin/env python3
"""
PLC Validation Tool
Enhanced CLI for comprehensive integrity checking
"""

import argparse
import sys
from pathlib import Path
import json
from datetime import datetime
import xml.etree.ElementTree as ET

def validate_l5x_file(file_path):
    """Validate L5X file structure and content"""
    validation_result = {
        "file": str(file_path),
        "status": "unknown",
        "issues": [],
        "components_found": {},
        "file_size": file_path.stat().st_size
    }
    
    try:
        # Check if file is empty or too small
        if validation_result["file_size"] < 100:
            validation_result["issues"].append("File too small or empty")
            validation_result["status"] = "failed"
            return validation_result
        
        # Try to parse as XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # Count components
        validation_result["components_found"] = {
            "programs": len(root.findall(".//Program")),
            "routines": len(root.findall(".//Routine")),
            "aois": len(root.findall(".//AddOnInstructionDefinition")),
            "tags": len(root.findall(".//Tag"))
        }
        
        # Basic validation checks
        if validation_result["components_found"]["programs"] == 0:
            validation_result["issues"].append("No programs found")
        
        if len(validation_result["issues"]) == 0:
            validation_result["status"] = "passed"
        else:
            validation_result["status"] = "warning"
            
    except ET.ParseError as e:
        validation_result["issues"].append(f"XML parse error: {e}")
        validation_result["status"] = "failed"
    except Exception as e:
        validation_result["issues"].append(f"Validation error: {e}")
        validation_result["status"] = "failed"
    
    return validation_result

def validate_acd_file(file_path):
    """Validate ACD file (basic checks)"""
    validation_result = {
        "file": str(file_path),
        "status": "unknown",
        "issues": [],
        "file_size": file_path.stat().st_size
    }
    
    # Check if it's a Git LFS pointer
    try:
        with open(file_path, 'r', errors='ignore') as f:
            content = f.read(200)
            if content.startswith("version https://git-lfs.github.com"):
                validation_result["issues"].append("File is Git LFS pointer - need actual content")
                validation_result["status"] = "lfs_pointer"
            elif validation_result["file_size"] > 1024:  # Reasonable ACD file size
                validation_result["status"] = "passed"
            else:
                validation_result["issues"].append("File too small for valid ACD")
                validation_result["status"] = "failed"
    except Exception as e:
        validation_result["issues"].append(f"Read error: {e}")
        validation_result["status"] = "failed"
    
    return validation_result

def validate_directory(directory_path):
    """Validate all PLC files in directory"""
    dir_path = Path(directory_path)
    
    results = {
        "validation_timestamp": datetime.now().isoformat(),
        "directory": str(dir_path),
        "files_validated": 0,
        "files_passed": 0,
        "files_failed": 0,
        "files_warning": 0,
        "lfs_pointers": 0,
        "file_results": []
    }
    
    # Find all PLC files
    plc_files = []
    plc_files.extend(dir_path.rglob("*.ACD"))
    plc_files.extend(dir_path.rglob("*.L5X"))
    
    for file_path in plc_files:
        if file_path.suffix.upper() == ".L5X":
            result = validate_l5x_file(file_path)
        elif file_path.suffix.upper() == ".ACD":
            result = validate_acd_file(file_path)
        else:
            continue
        
        results["file_results"].append(result)
        results["files_validated"] += 1
        
        if result["status"] == "passed":
            results["files_passed"] += 1
        elif result["status"] == "failed":
            results["files_failed"] += 1
        elif result["status"] == "warning":
            results["files_warning"] += 1
        elif result["status"] == "lfs_pointer":
            results["lfs_pointers"] += 1
    
    return results

def main():
    parser = argparse.ArgumentParser(description="PLC File Validation Tool")
    parser.add_argument("--input", required=True, help="File or directory to validate")
    parser.add_argument("--report", help="Output validation report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Validate single file
        if input_path.suffix.upper() == ".L5X":
            result = validate_l5x_file(input_path)
        elif input_path.suffix.upper() == ".ACD":
            result = validate_acd_file(input_path)
        else:
            print(f"❌ Unsupported file type: {input_path.suffix}")
            return 1
        
        print(f"📋 Validation Result: {result['status']}")
        if result["issues"]:
            print("⚠️ Issues found:")
            for issue in result["issues"]:
                print(f"   • {issue}")
        
        return 0 if result["status"] in ["passed", "warning"] else 1
    
    elif input_path.is_dir():
        # Validate directory
        results = validate_directory(input_path)
        
        print(f"📁 Validated {results['files_validated']} files:")
        print(f"   ✅ Passed: {results['files_passed']}")
        print(f"   ⚠️ Warning: {results['files_warning']}")
        print(f"   ❌ Failed: {results['files_failed']}")
        print(f"   📦 LFS Pointers: {results['lfs_pointers']}")
        
        if args.verbose:
            for result in results["file_results"]:
                print(f"
📄 {Path(result['file']).name}: {result['status']}")
                if result["issues"]:
                    for issue in result["issues"]:
                        print(f"   • {issue}")
        
        if args.report:
            with open(args.report, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"
📊 Report saved to {args.report}")
        
        return 0 if results["files_failed"] == 0 else 1
    
    else:
        print(f"❌ Path not found: {input_path}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
