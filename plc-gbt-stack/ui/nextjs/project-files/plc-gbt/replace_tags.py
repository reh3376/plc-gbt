#!/usr/bin/env python3
"""
Tags.json Pattern Replacement Script

This script performs the following replacements:
1. "tagGroup": "Perspective Default" → "tagGroup": "Default"
2. "opcItemPath": "ns\u003d1;s\u003d[WHK01_PLC400_Utility]*" → "opcItemPath": "ns\u003d1;s\u003d[plc400]*"
3. "opcItemPath": "ns\u003d1;s\u003d[WHK01_PLC300_Still]*" → "opcItemPath": "ns\u003d1;s\u003d[plc300]*"
4. "opcItemPath": "ns\u003d1;s\u003d[WHK01_PLC100_Mashing]*" → "opcItemPath": "ns\u003d1;s\u003d[plc100]*"
5. "opcItemPath": "ns\u003d1;s\u003d[WHK01_PLC200_Fermenters]*" → "opcItemPath": "ns\u003d1;s\u003d[plc200]*"

Asterisk (*) means everything after that point remains unchanged.
"""

import json
import shutil
import sys
import re
from datetime import datetime
from pathlib import Path

def create_backup(file_path: Path) -> Path:
    """Create a backup of the original file with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.parent / f"{file_path.stem}_backup_{timestamp}.json"
    shutil.copy2(file_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path

def validate_json(file_path: Path) -> bool:
    """Validate that the file is valid JSON."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ JSON validation failed: {e}")
        return False

def perform_replacements(content: str) -> tuple[str, dict]:
    """Perform all the specified replacements and return statistics."""
    stats = {}
    
    # 1. Replace tagGroup: "Perspective Default" with "Default"
    pattern1 = r'"tagGroup":\s*"Perspective Default"'
    replacement1 = '"tagGroup": "Default"'
    content, count1 = re.subn(pattern1, replacement1, content)
    stats['tagGroup_changes'] = count1
    
    # 2. Replace WHK01_PLC400_Utility with plc400
    pattern2 = r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC400_Utility\]'
    replacement2 = r'"opcItemPath": "\1[plc400]'
    content, count2 = re.subn(pattern2, replacement2, content)
    stats['plc400_changes'] = count2
    
    # 3. Replace WHK01_PLC300_Still with plc300
    pattern3 = r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC300_Still\]'
    replacement3 = r'"opcItemPath": "\1[plc300]'
    content, count3 = re.subn(pattern3, replacement3, content)
    stats['plc300_changes'] = count3
    
    # 4. Replace WHK01_PLC100_Mashing with plc100
    pattern4 = r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC100_Mashing\]'
    replacement4 = r'"opcItemPath": "\1[plc100]'
    content, count4 = re.subn(pattern4, replacement4, content)
    stats['plc100_changes'] = count4
    
    # 5. Replace WHK01_PLC200_Fermenters with plc200
    pattern5 = r'"opcItemPath":\s*"([^"]*)\[WHK01_PLC200_Fermenters\]'
    replacement5 = r'"opcItemPath": "\1[plc200]'
    content, count5 = re.subn(pattern5, replacement5, content)
    stats['plc200_changes'] = count5
    
    stats['total_changes'] = sum(stats.values())
    
    return content, stats

def main():
    """Main execution function."""
    # File paths
    input_file = Path("/Users/reh3376/repos/plc-gbt/docs/data/tags.json")
    
    if not input_file.exists():
        print(f"❌ File not found: {input_file}")
        sys.exit(1)
    
    print(f"🔍 Processing file: {input_file}")
    print(f"📊 File size: {input_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    # Validate original file
    if not validate_json(input_file):
        print("❌ Original file is not valid JSON. Aborting.")
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup(input_file)
    
    try:
        # Read the file
        print("📖 Reading file...")
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_size = len(content)
        print(f"📊 Original content size: {original_size:,} characters")
        
        # Perform replacements
        print("🔄 Performing replacements...")
        modified_content, stats = perform_replacements(content)
        
        # Display statistics
        print("\n📈 Replacement Statistics:")
        print(f"  • tagGroup changes: {stats['tagGroup_changes']:,}")
        print(f"  • PLC400 changes: {stats['plc400_changes']:,}")
        print(f"  • PLC300 changes: {stats['plc300_changes']:,}")
        print(f"  • PLC100 changes: {stats['plc100_changes']:,}")
        print(f"  • PLC200 changes: {stats['plc200_changes']:,}")
        print(f"  • Total changes: {stats['total_changes']:,}")
        
        if stats['total_changes'] == 0:
            print("ℹ️  No changes needed. File is already up to date.")
            return
        
        # Write the modified content
        print("💾 Writing modified file...")
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Validate the modified file
        print("🔍 Validating modified JSON...")
        if not validate_json(input_file):
            print("❌ Modified file is not valid JSON. Restoring backup...")
            shutil.copy2(backup_path, input_file)
            sys.exit(1)
        
        print("✅ File successfully modified and validated!")
        print(f"📊 New content size: {len(modified_content):,} characters")
        print(f"📊 Size difference: {len(modified_content) - original_size:+,} characters")
        print(f"💾 Backup preserved at: {backup_path}")
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        print(f"🔄 Restoring backup...")
        shutil.copy2(backup_path, input_file)
        sys.exit(1)

if __name__ == "__main__":
    main() 