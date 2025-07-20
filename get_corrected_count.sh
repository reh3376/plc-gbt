#!/bin/bash

echo "🔍 Getting Corrected Count from docs directory"

cd docs

missing_files=0
existing_files=0

grep -o "\[.*\]([^)]*)" roadmap.md | grep -o "([^)]*)" | tr -d "()" | grep -v "^http" | grep -E "\.(md|py|json|yml|yaml|sh)$" | sort | uniq | while IFS= read -r file_path; do
    
    if [ -f "$file_path" ] || [ -d "$file_path" ]; then
        existing_files=$((existing_files + 1))
    else
        missing_files=$((missing_files + 1))
        echo "❌ MISSING: $file_path"
    fi
done > /tmp/missing_files.txt

total_missing=$(wc -l < /tmp/missing_files.txt)
total_files=$(grep -o "\[.*\]([^)]*)" roadmap.md | grep -o "([^)]*)" | tr -d "()" | grep -v "^http" | grep -E "\.(md|py|json|yml|yaml|sh)$" | sort | uniq | wc -l)
existing_files=$((total_files - total_missing))

echo ""
echo "📊 CORRECTED Validation Summary:"
echo "  Total Files: $total_files"
echo "  ✅ Existing: $existing_files"
echo "  ❌ Missing: $total_missing"
echo "  📈 Success Rate: $((existing_files * 100 / total_files))%"

echo ""
echo "📋 Missing Files:"
cat /tmp/missing_files.txt
