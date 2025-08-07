#!/usr/bin/env python3
"""
DOCX to Markdown Converter
=========================

AI Task Orchestrator Implementation
Created: 2025-01-31
Purpose: Convert .docx files to properly formatted markdown

This script follows the AI Task Orchestrator methodology for:
- Comprehensive error handling
- Robust validation
- Production-ready implementation
- Standardized documentation
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

try:
    from docx import Document
    from docx.shared import Inches
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
except ImportError:
    print("ERROR: python-docx library not found. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
    from docx import Document
    from docx.shared import Inches
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DOCXToMarkdownConverter:
    """
    Professional DOCX to Markdown converter with comprehensive validation
    """
    
    def __init__(self):
        self.conversion_stats = {
            'paragraphs_processed': 0,
            'tables_processed': 0,
            'images_processed': 0,
            'lists_processed': 0,
            'headers_processed': 0
        }
    
    def convert_docx_to_markdown(self, docx_path: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Convert DOCX file to markdown format with comprehensive error handling
        
        Args:
            docx_path: Path to source .docx file
            output_path: Optional output path for .md file
            
        Returns:
            Dict containing conversion results and statistics
        """
        try:
            # Validate input file
            if not os.path.exists(docx_path):
                raise FileNotFoundError(f"Source file not found: {docx_path}")
            
            if not docx_path.lower().endswith('.docx'):
                raise ValueError(f"Input file must be .docx format: {docx_path}")
            
            logger.info(f"Starting conversion of: {docx_path}")
            
            # Determine output path
            if output_path is None:
                output_path = self._generate_output_path(docx_path)
            
            # Load document
            try:
                doc = Document(docx_path)
                logger.info(f"Successfully loaded document with {len(doc.paragraphs)} paragraphs")
            except Exception as e:
                raise RuntimeError(f"Failed to load DOCX document: {e}")
            
            # Convert content
            markdown_content = self._convert_document_to_markdown(doc)
            
            # Add metadata header
            markdown_with_metadata = self._add_metadata_header(
                markdown_content, 
                docx_path, 
                output_path
            )
            
            # Write output file
            self._write_markdown_file(markdown_with_metadata, output_path)
            
            # Validate output
            validation_result = self._validate_conversion(docx_path, output_path)
            
            return {
                'status': 'success',
                'input_file': docx_path,
                'output_file': output_path,
                'statistics': self.conversion_stats,
                'validation': validation_result,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'input_file': docx_path,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_output_path(self, docx_path: str) -> str:
        """Generate output markdown file path"""
        path = Path(docx_path)
        return str(path.parent / f"{path.stem}.md")
    
    def _convert_document_to_markdown(self, doc: Document) -> str:
        """Convert document content to markdown format"""
        markdown_lines = []
        
        for paragraph in doc.paragraphs:
            markdown_line = self._convert_paragraph_to_markdown(paragraph)
            if markdown_line:
                markdown_lines.append(markdown_line)
                self.conversion_stats['paragraphs_processed'] += 1
        
        # Process tables
        for table in doc.tables:
            table_markdown = self._convert_table_to_markdown(table)
            if table_markdown:
                markdown_lines.append(table_markdown)
                self.conversion_stats['tables_processed'] += 1
        
        return '\n\n'.join(markdown_lines)
    
    def _convert_paragraph_to_markdown(self, paragraph) -> str:
        """Convert a single paragraph to markdown format"""
        text = paragraph.text.strip()
        
        if not text:
            return ""
        
        # Detect and convert headers based on style
        style_name = paragraph.style.name.lower()
        
        if 'heading 1' in style_name or paragraph.style.name == 'Title':
            self.conversion_stats['headers_processed'] += 1
            return f"# {text}"
        elif 'heading 2' in style_name:
            self.conversion_stats['headers_processed'] += 1
            return f"## {text}"
        elif 'heading 3' in style_name:
            self.conversion_stats['headers_processed'] += 1
            return f"### {text}"
        elif 'heading 4' in style_name:
            self.conversion_stats['headers_processed'] += 1
            return f"#### {text}"
        elif 'heading 5' in style_name:
            self.conversion_stats['headers_processed'] += 1
            return f"##### {text}"
        elif 'heading 6' in style_name:
            self.conversion_stats['headers_processed'] += 1
            return f"###### {text}"
        
        # Handle lists
        if 'list' in style_name.lower() or paragraph.style.name.startswith('List'):
            self.conversion_stats['lists_processed'] += 1
            return f"- {text}"
        
        # Handle quotes
        if 'quote' in style_name.lower():
            return f"> {text}"
        
        # Handle code blocks
        if 'code' in style_name.lower():
            return f"```\n{text}\n```"
        
        # Regular paragraph
        return text
    
    def _convert_table_to_markdown(self, table) -> str:
        """Convert table to markdown format"""
        markdown_rows = []
        
        for i, row in enumerate(table.rows):
            cells = [cell.text.strip() for cell in row.cells]
            markdown_row = "| " + " | ".join(cells) + " |"
            markdown_rows.append(markdown_row)
            
            # Add header separator after first row
            if i == 0:
                separator = "| " + " | ".join(["---"] * len(cells)) + " |"
                markdown_rows.append(separator)
        
        return "\n".join(markdown_rows)
    
    def _add_metadata_header(self, content: str, input_path: str, output_path: str) -> str:
        """Add metadata header to markdown content"""
        input_file = Path(input_path).name
        output_file = Path(output_path).name
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        metadata_header = f"""# {Path(input_path).stem.replace('-', ' ').title()}

> **Document Conversion Information**
> 
> - **Source**: {input_file}
> - **Converted**: {timestamp}
> - **Format**: DOCX → Markdown
> - **Converter**: AI Task Orchestrator DOCX-to-Markdown Tool
> - **Statistics**: {self.conversion_stats['paragraphs_processed']} paragraphs, {self.conversion_stats['tables_processed']} tables, {self.conversion_stats['headers_processed']} headers

---

"""
        return metadata_header + content
    
    def _write_markdown_file(self, content: str, output_path: str) -> None:
        """Write markdown content to file with error handling"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Successfully wrote markdown file: {output_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to write markdown file: {e}")
    
    def _validate_conversion(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """Validate the conversion results"""
        validation_results = {
            'input_exists': os.path.exists(input_path),
            'output_exists': os.path.exists(output_path),
            'output_size': 0,
            'content_length': 0,
            'has_content': False
        }
        
        if validation_results['output_exists']:
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    validation_results['content_length'] = len(content)
                    validation_results['has_content'] = len(content.strip()) > 0
                    validation_results['output_size'] = os.path.getsize(output_path)
            except Exception as e:
                validation_results['validation_error'] = str(e)
        
        validation_results['success'] = (
            validation_results['input_exists'] and 
            validation_results['output_exists'] and 
            validation_results['has_content']
        )
        
        return validation_results


def main():
    """Main execution function with comprehensive error handling"""
    if len(sys.argv) < 2:
        print("Usage: python docx_to_markdown_converter.py <input_docx_file> [output_md_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    converter = DOCXToMarkdownConverter()
    result = converter.convert_docx_to_markdown(input_file, output_file)
    
    if result['status'] == 'success':
        print(f"✅ Conversion successful!")
        print(f"📄 Input: {result['input_file']}")
        print(f"📝 Output: {result['output_file']}")
        print(f"📊 Statistics: {result['statistics']}")
        print(f"✅ Validation: {'PASSED' if result['validation']['success'] else 'FAILED'}")
    else:
        print(f"❌ Conversion failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
