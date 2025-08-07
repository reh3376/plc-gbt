#!/usr/bin/env python3
"""
Markdown Code Formatting Fixer
==============================

AI Task Orchestrator Implementation for MPC-overview.md
Created: 2025-01-31
Purpose: Fix Python code formatting issues in markdown document

This script addresses:
- Missing code block fencing (```)
- Improper section headers
- Mixed content separation
- Syntax highlighting indicators
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class MarkdownCodeFormatter:
    """Fix Python code formatting issues in markdown documents"""
    
    def __init__(self):
        self.fixes_applied = {
            'code_blocks_added': 0,
            'headers_fixed': 0,
            'inline_code_fixed': 0,
            'sections_separated': 0
        }
    
    def fix_markdown_code_formatting(self, file_path: str) -> dict:
        """
        Fix Python code formatting issues in markdown file
        
        Args:
            file_path: Path to markdown file
            
        Returns:
            Dict with fix results and statistics
        """
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"Processing {file_path} with {len(content.splitlines())} lines")
            
            # Apply fixes in sequence
            content = self._fix_python_section_headers(content)
            content = self._wrap_python_code_blocks(content)
            content = self._fix_inline_code_references(content)
            content = self._clean_code_block_spacing(content)
            content = self._fix_mixed_content_separation(content)
            
            # Write back to file
            backup_path = file_path + '.backup'
            os.rename(file_path, backup_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully applied {sum(self.fixes_applied.values())} fixes")
            
            return {
                'status': 'success',
                'input_file': file_path,
                'backup_file': backup_path,
                'fixes_applied': self.fixes_applied,
                'lines_processed': len(content.splitlines())
            }
            
        except Exception as e:
            logger.error(f"Error fixing code formatting: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'input_file': file_path
            }
    
    def _fix_python_section_headers(self, content: str) -> str:
        """Convert Python section labels to proper markdown headers"""
        # Pattern: "Python Example (description): Python" -> "### Python Example (description)"
        pattern = r'^(Python [Ee]xample[^:]*): Python\s*$'
        def replace_header(match):
            self.fixes_applied['headers_fixed'] += 1
            return f"### {match.group(1)}\n\n```python"
        
        content = re.sub(pattern, replace_header, content, flags=re.MULTILINE)
        
        # Pattern: "Python example:" -> "### Python Example"
        pattern = r'^Python example[^:]*:\s*$'
        def replace_simple_header(match):
            self.fixes_applied['headers_fixed'] += 1
            return f"### {match.group(0).rstrip(':')}\n\n```python"
        
        content = re.sub(pattern, replace_simple_header, content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Pattern: "code example" -> "### Code Example"
        pattern = r'^([Cc]ode [Ee]xample[^:]*): Python\s*$'
        def replace_code_header(match):
            self.fixes_applied['headers_fixed'] += 1
            header = match.group(1)
            if not header.startswith('### '):
                header = f"### {header}"
            return f"{header}\n\n```python"
        
        content = re.sub(pattern, replace_code_header, content, flags=re.MULTILINE)
        
        return content
    
    def _wrap_python_code_blocks(self, content: str) -> str:
        """Wrap Python code sections in proper code blocks"""
        lines = content.splitlines()
        result_lines = []
        in_code_block = False
        pending_code_block = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            
            # Check if we just added a code block start
            if pending_code_block:
                if line_stripped and not line_stripped.startswith('#') and not line_stripped.startswith('```'):
                    in_code_block = True
                    pending_code_block = False
                elif line_stripped.startswith('```'):
                    pending_code_block = False
            
            # Check if line ends with "```python" (from header fixes)
            if line.endswith('```python'):
                result_lines.append(line)
                pending_code_block = True
                continue
            
            # Check if we're starting a Python code section
            if (self._is_python_code_line(line) and not in_code_block and 
                not line_stripped.startswith('```')):
                
                # Check if we don't already have a recent code block start
                has_recent_code_start = (result_lines and 
                                       len(result_lines) > 0 and 
                                       result_lines[-1].strip().endswith('```python'))
                
                # Look ahead to see if this is actually a code block
                if self._is_start_of_code_block(lines, i) and not has_recent_code_start:
                    result_lines.append('```python')
                    self.fixes_applied['code_blocks_added'] += 1
                    in_code_block = True
            
            # Check if we're ending a Python code section
            elif in_code_block and (self._is_end_of_code_block(lines, i) or 
                                   line_stripped.startswith('#') and not self._is_python_comment(line)):
                
                if not line_stripped.startswith('```'):
                    result_lines.append('```')
                    result_lines.append('')
                in_code_block = False
            
            result_lines.append(line)
        
        # Close any open code blocks
        if in_code_block:
            result_lines.append('```')
            self.fixes_applied['code_blocks_added'] += 1
        
        return '\n'.join(result_lines)
    
    def _is_python_code_line(self, line: str) -> bool:
        """Check if a line looks like Python code"""
        line_stripped = line.strip()
        
        if not line_stripped:
            return False
        
        # Python imports
        if line_stripped.startswith('import ') or line_stripped.startswith('from '):
            return True
        
        # Python assignments and function calls
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*\s*=', line_stripped):
            return True
        
        # Function definitions
        if line_stripped.startswith('def ') or line_stripped.startswith('class '):
            return True
        
        # Python function calls
        if re.search(r'\w+\([^)]*\)', line_stripped):
            return True
        
        # Python-specific patterns
        python_patterns = [
            r'np\.',
            r'plt\.',
            r'pd\.',
            r'control\.',
            r'torch\.',
            r'sklearn\.',
            r'scipy\.',
            r'print\(',
            r'return ',
            r'for \w+ in',
            r'if \w+',
            r'while \w+',
            r'\.fit\(',
            r'\.predict\(',
            r'\.transform\(',
        ]
        
        for pattern in python_patterns:
            if re.search(pattern, line_stripped):
                return True
        
        return False
    
    def _is_python_comment(self, line: str) -> bool:
        """Check if line is a Python comment"""
        stripped = line.strip()
        return stripped.startswith('#') and (
            ' ' in stripped[1:] or 
            len(stripped) > 1
        )
    
    def _is_start_of_code_block(self, lines: List[str], index: int) -> bool:
        """Check if this is the start of a Python code block"""
        # Look ahead for more Python code
        for i in range(index, min(index + 5, len(lines))):
            line = lines[i].strip()
            if line and (self._is_python_code_line(lines[i]) or self._is_python_comment(lines[i])):
                return True
        return False
    
    def _is_end_of_code_block(self, lines: List[str], index: int) -> bool:
        """Check if this is the end of a Python code block"""
        current_line = lines[index].strip()
        
        # Empty line followed by non-code
        if not current_line:
            if index + 1 < len(lines):
                next_line = lines[index + 1].strip()
                if next_line and not self._is_python_code_line(lines[index + 1]) and not self._is_python_comment(lines[index + 1]):
                    return True
        
        # Text that's clearly not code
        if current_line and not self._is_python_code_line(lines[index]) and not self._is_python_comment(lines[index]):
            # Skip if it's just whitespace or markdown
            if not current_line.startswith(('#', '-', '*', '>', '|')):
                return True
        
        return False
    
    def _fix_inline_code_references(self, content: str) -> str:
        """Fix inline code references to use proper backticks"""
        # Pattern: Python variable/function names that should be inline code
        patterns = [
            (r'\bpandas\.DataFrame\b', '`pandas.DataFrame`'),
            (r'\bnumpy\.array\b', '`numpy.array`'),
            (r'\bplt\.plot\b', '`plt.plot`'),
            (r'\bnp\.array\b', '`np.array`'),
            (r'\bcontrol\.ss\b', '`control.ss`'),
            (r'\btorch\.nn\b', '`torch.nn`'),
        ]
        
        for pattern, replacement in patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                self.fixes_applied['inline_code_fixed'] += 1
        
        return content
    
    def _clean_code_block_spacing(self, content: str) -> str:
        """Clean up spacing around code blocks"""
        # Remove excessive blank lines around code blocks
        content = re.sub(r'\n{3,}```', '\n\n```', content)
        content = re.sub(r'```\n{3,}', '```\n\n', content)
        
        # Ensure proper spacing before code blocks
        content = re.sub(r'(\S)\n```python', r'\1\n\n```python', content)
        
        return content
    
    def _fix_mixed_content_separation(self, content: str) -> str:
        """Separate mixed code and text content properly"""
        lines = content.splitlines()
        result_lines = []
        
        for i, line in enumerate(lines):
            # Check for text immediately after code without proper separation
            if (i > 0 and 
                not line.strip().startswith('#') and 
                not line.strip().startswith('```') and
                line.strip() and
                not self._is_python_code_line(line) and
                len(result_lines) > 0 and
                (self._is_python_code_line(result_lines[-1]) or 
                 result_lines[-1].strip().startswith('#'))):
                
                # Add separation
                if len(result_lines) > 0 and result_lines[-1].strip():
                    result_lines.append('```')
                    result_lines.append('')
                    self.fixes_applied['sections_separated'] += 1
            
            result_lines.append(line)
        
        return '\n'.join(result_lines)


def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python fix_markdown_code_formatting.py <markdown_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found")
        sys.exit(1)
    
    formatter = MarkdownCodeFormatter()
    result = formatter.fix_markdown_code_formatting(input_file)
    
    if result['status'] == 'success':
        print(f"✅ Code formatting fixes applied successfully!")
        print(f"📄 Input: {result['input_file']}")
        print(f"💾 Backup: {result['backup_file']}")
        print(f"📊 Fixes applied: {result['fixes_applied']}")
        print(f"📝 Lines processed: {result['lines_processed']}")
    else:
        print(f"❌ Code formatting failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
