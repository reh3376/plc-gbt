#!/usr/bin/env python3
"""
Final Code Formatting Cleanup
=============================

Targeted fixes for remaining Python code formatting issues
"""

import re
import os
import sys


def final_cleanup(file_path: str):
    """Apply final cleanup fixes"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    fixes = 0
    
    # Fix: "Python Example (...): Python" lines that weren't converted
    pattern = r'^(Python [Ee]xample[^:]*): Python\s*$'
    def fix_header(match):
        nonlocal fixes
        fixes += 1
        return f"### {match.group(1)}\n\n```python"
    
    content = re.sub(pattern, fix_header, content, flags=re.MULTILINE)
    
    # Fix: Standalone "Python" lines after descriptions
    pattern = r'^([A-Z][^:]*): Python\s*$'
    def fix_desc_header(match):
        nonlocal fixes
        fixes += 1
        return f"### {match.group(1)}\n\n```python"
    
    content = re.sub(pattern, fix_desc_header, content, flags=re.MULTILINE)
    
    # Fix: Code lines that should be wrapped but aren't
    lines = content.splitlines()
    result_lines = []
    in_code_block = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Track if we're in a code block
        if line_stripped.startswith('```'):
            if line_stripped == '```' or line_stripped == '```python':
                in_code_block = not in_code_block
        
        # Check for unwrapped Python imports/code
        elif (not in_code_block and 
              (line_stripped.startswith('import ') or 
               line_stripped.startswith('from ') or
               (line_stripped and re.match(r'^[a-zA-Z_]\w*\s*=', line_stripped)))):
            
            # Look ahead to see if there's more code
            has_more_code = False
            for j in range(i+1, min(i+5, len(lines))):
                next_line = lines[j].strip()
                if (next_line and 
                    (next_line.startswith(('import ', 'from ', '#')) or
                     re.match(r'^[a-zA-Z_]\w*\s*[=\.]', next_line) or
                     any(pattern in next_line for pattern in ['np.', 'plt.', 'pd.', '()']))):
                    has_more_code = True
                    break
                elif next_line and not next_line.startswith(('#', '```')):
                    break
            
            if has_more_code:
                result_lines.append('```python')
                in_code_block = True
                fixes += 1
        
        # Check for end of unwrapped code block
        elif (in_code_block and line_stripped and 
              not line_stripped.startswith(('#', 'import', 'from')) and
              not re.match(r'^[a-zA-Z_]', line_stripped) and
              not any(pattern in line_stripped for pattern in ['np.', 'plt.', 'pd.', '=', '()', 'def ', 'class '])):
            
            result_lines.append('```')
            result_lines.append('')
            in_code_block = False
            fixes += 1
        
        result_lines.append(line)
        i += 1
    
    # Close any open code blocks
    if in_code_block:
        result_lines.append('```')
        fixes += 1
    
    content = '\n'.join(result_lines)
    
    # Fix double code block markers
    content = re.sub(r'```\n```python', '```python', content)
    content = re.sub(r'```\n\n```python', '\n```python', content)
    
    # Clean up excessive whitespace
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Applied {fixes} additional fixes")
    return fixes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python final_code_formatting_cleanup.py <file>")
        sys.exit(1)
    
    fixes = final_cleanup(sys.argv[1])
    print(f"✅ Final cleanup complete - {fixes} additional fixes applied")
