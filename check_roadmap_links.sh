#!/bin/bash

echo "🔍 Roadmap Link Validation - Systematic Check"
echo "=============================================="

missing_files=0
existing_files=0
total_files=0

echo "📋 Checking all 128 file links from roadmap.md..."

while IFS= read -r file_path; do
    total_files=$((total_files + 1))
    
    # Check if file exists
    if [ -f "$file_path" ] || [ -d "$file_path" ]; then
        existing_files=$((existing_files + 1))
        echo "✅ $file_path"
    else
        missing_files=$((missing_files + 1))
        echo "❌ MISSING: $file_path"
    fi
done < /tmp/roadmap_links.txt

echo ""
echo "📊 Validation Summary:"
echo "  Total Files: $total_files"
echo "  ✅ Existing: $existing_files"
echo "  ❌ Missing: $missing_files"
echo "  📈 Success Rate: $((existing_files * 100 / total_files))%"

if [ $missing_files -eq 0 ]; then
    echo "🎉 ALL LINKS VALID!"
else
    echo "⚠️  Found $missing_files missing files that need attention"
fi
