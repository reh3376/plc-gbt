#!/bin/bash

echo "🔍 Roadmap Link Validation - CORRECTED (from docs directory)"
echo "=============================================================="

cd docs

missing_files=0
existing_files=0
total_files=0

echo "📋 Checking all file links from roadmap.md (from docs directory)..."

grep -o "\[.*\]([^)]*)" roadmap.md | grep -o "([^)]*)" | tr -d "()" | grep -v "^http" | grep -E "\.(md|py|json|yml|yaml|sh)$" | sort | uniq | while IFS= read -r file_path; do
    total_files=$((total_files + 1))
    
    # Check if file exists
    if [ -f "$file_path" ] || [ -d "$file_path" ]; then
        existing_files=$((existing_files + 1))
        echo "✅ $file_path"
    else
        missing_files=$((missing_files + 1))
        echo "❌ MISSING: $file_path"
    fi
done

echo ""
echo "📊 This gives us the corrected validation results"
