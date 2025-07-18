#!/usr/bin/env python3
"""
🔍 Context Scanner Module - Phase 24.1 Task 24.1.1

AI Task Orchestrator Implementation for comprehensive context discovery and analysis.
Processes control system documentation, schemas, code, and data files.

Author: AI Task Orchestrator
Created: 2025-07-15
Phase: 24.1 - Context Discovery & Analysis
"""

import os
import json
import csv
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib
import mimetypes

# Optional imports
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

# Document processing imports
try:
    import docx
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class FileMetadata:
    """File metadata structure"""
    path: str
    name: str
    extension: str
    size_bytes: int
    mime_type: str
    file_type: str
    content_hash: str
    created_time: Optional[datetime] = None
    modified_time: Optional[datetime] = None

@dataclass
class SchemaAnalysis:
    """JSON Schema analysis results"""
    schema_type: str
    title: str
    description: str
    version: str
    property_count: int
    required_fields: List[str]
    control_type: str  # PID, PIDE, Advanced, etc.
    complexity_level: str  # Standard, Advanced, Cascade, etc.

@dataclass
class CodeAnalysis:
    """Python code analysis results"""
    functions: List[str]
    classes: List[str]
    imports: List[str]
    line_count: int
    complexity_score: int
    has_docstrings: bool
    control_algorithms: List[str]

@dataclass
class DocumentAnalysis:
    """Document analysis results"""
    word_count: int
    paragraph_count: int
    headings: List[str]
    key_topics: List[str]
    control_concepts: List[str]
    best_practices: List[str]

@dataclass
class DataAnalysis:
    """CSV/Data analysis results"""
    row_count: int
    column_count: int
    columns: List[str]
    data_types: Dict[str, str]
    sample_data: List[Dict[str, Any]]
    control_variables: List[str]

@dataclass
class ScanResult:
    """Complete scan result for a file"""
    metadata: FileMetadata
    schema_analysis: Optional[SchemaAnalysis] = None
    code_analysis: Optional[CodeAnalysis] = None
    document_analysis: Optional[DocumentAnalysis] = None
    data_analysis: Optional[DataAnalysis] = None
    raw_content: Optional[str] = None
    processing_errors: List[str] = None

    def __post_init__(self):
        if self.processing_errors is None:
            self.processing_errors = []

class ContextScanner:
    """
    Comprehensive context scanner for Phase 24.1
    
    Analyzes control system documentation, schemas, code, and data files
    to extract knowledge for ingestion into the PLC memory system.
    """
    
    def __init__(self, context_path: str):
        self.context_path = Path(context_path)
        self.scan_results: List[ScanResult] = []
        
        # Control system keywords for content analysis
        self.control_keywords = {
            'pid_terms': ['PID', 'PIDE', 'proportional', 'integral', 'derivative', 
                         'setpoint', 'process variable', 'controller output'],
            'control_types': ['cascade', 'feedforward', 'feedback', 'MPC', 'adaptive'],
            'tuning_terms': ['tuning', 'gain', 'reset time', 'rate time', 'overshoot', 
                           'settling time', 'steady state'],
            'algorithms': ['Ziegler-Nichols', 'Cohen-Coon', 'Lambda tuning', 
                          'IMC', 'model based'],
            'safety_terms': ['interlock', 'safety', 'trip', 'alarm', 'fault']
        }
        
        logger.info(f"ContextScanner initialized for: {self.context_path}")
    
    def scan_directory(self, recursive: bool = True) -> List[ScanResult]:
        """
        Scan the context directory and analyze all relevant files
        
        Args:
            recursive: Whether to scan subdirectories
            
        Returns:
            List of scan results for all processed files
        """
        logger.info(f"🔍 Starting context directory scan: {self.context_path}")
        
        # Find all files to process
        files_to_scan = self._discover_files(recursive)
        logger.info(f"📁 Found {len(files_to_scan)} files to analyze")
        
        # Process each file
        for file_path in files_to_scan:
            try:
                scan_result = self._scan_file(file_path)
                self.scan_results.append(scan_result)
                logger.debug(f"✅ Processed: {file_path.name}")
            except Exception as e:
                logger.error(f"❌ Failed to process {file_path}: {e}")
                # Create minimal scan result with error
                metadata = self._get_file_metadata(file_path)
                result = ScanResult(metadata=metadata, processing_errors=[str(e)])
                self.scan_results.append(result)
        
        logger.info(f"✅ Context scan complete: {len(self.scan_results)} files processed")
        return self.scan_results
    
    def _discover_files(self, recursive: bool) -> List[Path]:
        """Discover all relevant files in the context directory"""
        files = []
        
        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"
        
        for file_path in self.context_path.glob(pattern):
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Skip very large files (over 100MB) for initial scan
                if file_path.stat().st_size < 100 * 1024 * 1024:
                    files.append(file_path)
                else:
                    logger.warning(f"⚠️ Skipping large file: {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
        
        return sorted(files)
    
    def _scan_file(self, file_path: Path) -> ScanResult:
        """Scan and analyze a single file"""
        metadata = self._get_file_metadata(file_path)
        
        # Initialize scan result
        scan_result = ScanResult(metadata=metadata)
        
        # Route to appropriate analyzer based on file type
        if metadata.extension.lower() == '.json':
            scan_result.schema_analysis = self._analyze_json_schema(file_path)
        elif metadata.extension.lower() == '.py':
            scan_result.code_analysis = self._analyze_python_code(file_path)
        elif metadata.extension.lower() in ['.docx', '.doc']:
            scan_result.document_analysis = self._analyze_word_document(file_path)
        elif metadata.extension.lower() == '.pdf':
            scan_result.document_analysis = self._analyze_pdf_document(file_path)
        elif metadata.extension.lower() == '.csv':
            scan_result.data_analysis = self._analyze_csv_data(file_path)
        elif metadata.extension.lower() in ['.txt', '.md', '.rtf']:
            scan_result.raw_content = self._extract_text_content(file_path)
            scan_result.document_analysis = self._analyze_text_content(scan_result.raw_content)
        
        return scan_result
    
    def _get_file_metadata(self, file_path: Path) -> FileMetadata:
        """Extract comprehensive file metadata"""
        stat = file_path.stat()
        
        # Get MIME type
        mime_type = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        
        # Determine file type category
        ext = file_path.suffix.lower()
        if ext == '.json':
            file_type = 'schema'
        elif ext == '.py':
            file_type = 'code'
        elif ext in ['.docx', '.doc', '.pdf', '.rtf']:
            file_type = 'document'
        elif ext == '.csv':
            file_type = 'data'
        elif ext in ['.txt', '.md']:
            file_type = 'text'
        else:
            file_type = 'other'
        
        # Calculate content hash
        content_hash = self._calculate_file_hash(file_path)
        
        return FileMetadata(
            path=str(file_path),
            name=file_path.name,
            extension=ext,
            size_bytes=stat.st_size,
            mime_type=mime_type,
            file_type=file_type,
            content_hash=content_hash,
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime)
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return "unknown"
    
    def _analyze_json_schema(self, file_path: Path) -> Optional[SchemaAnalysis]:
        """Analyze JSON schema files for control loop configurations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                schema_data = json.load(f)
            
            # Extract basic schema information
            title = schema_data.get('title', file_path.stem)
            description = schema_data.get('description', '')
            version = schema_data.get('version', 'unknown')
            
            # Analyze properties
            properties = schema_data.get('properties', {})
            property_count = len(properties)
            required_fields = schema_data.get('required', [])
            
            # Determine control type and complexity
            control_type = self._determine_control_type(title, description, properties)
            complexity_level = self._determine_complexity_level(title, properties)
            
            return SchemaAnalysis(
                schema_type='control_loop',
                title=title,
                description=description,
                version=version,
                property_count=property_count,
                required_fields=required_fields,
                control_type=control_type,
                complexity_level=complexity_level
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze JSON schema {file_path}: {e}")
            return None
    
    def _determine_control_type(self, title: str, description: str, properties: Dict) -> str:
        """Determine the type of control loop from schema content"""
        content = f"{title} {description}".lower()
        
        if 'pide' in content:
            return 'PIDE'
        elif 'pid' in content:
            return 'PID'
        elif 'mpc' in content:
            return 'MPC'
        elif 'adaptive' in content:
            return 'Adaptive'
        else:
            return 'Generic'
    
    def _determine_complexity_level(self, title: str, properties: Dict) -> str:
        """Determine complexity level of control configuration"""
        title_lower = title.lower()
        
        if 'advanced' in title_lower:
            if 'cascade' in title_lower and 'feedforward' in title_lower:
                return 'Advanced_Cascade_Feedforward'
            elif 'cascade' in title_lower:
                return 'Advanced_Cascade'
            elif 'feedforward' in title_lower:
                return 'Advanced_Feedforward'
            else:
                return 'Advanced'
        elif 'standard' in title_lower:
            return 'Standard'
        else:
            # Analyze properties to infer complexity
            prop_count = len(properties)
            if prop_count > 20:
                return 'Complex'
            elif prop_count > 10:
                return 'Moderate'
            else:
                return 'Simple'
    
    def _analyze_python_code(self, file_path: Path) -> Optional[CodeAnalysis]:
        """Analyze Python code for control algorithms and functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract functions and classes using basic parsing
            functions = self._extract_functions(content)
            classes = self._extract_classes(content)
            imports = self._extract_imports(content)
            
            # Calculate metrics
            line_count = len(content.splitlines())
            complexity_score = self._calculate_complexity_score(content)
            has_docstrings = '"""' in content or "'''" in content
            
            # Identify control algorithms
            control_algorithms = self._identify_control_algorithms(content)
            
            return CodeAnalysis(
                functions=functions,
                classes=classes,
                imports=imports,
                line_count=line_count,
                complexity_score=complexity_score,
                has_docstrings=has_docstrings,
                control_algorithms=control_algorithms
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze Python code {file_path}: {e}")
            return None
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names from Python code"""
        functions = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('def ') and '(' in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append(func_name)
        return functions
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names from Python code"""
        classes = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('class ') and ':' in line:
                class_name = line.split('class ')[1].split(':')[0].split('(')[0].strip()
                classes.append(class_name)
        return classes
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements from Python code"""
        imports = []
        for line in content.splitlines():
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                imports.append(line)
        return imports
    
    def _calculate_complexity_score(self, content: str) -> int:
        """Calculate a basic complexity score for Python code"""
        # Simple complexity metrics
        complexity_indicators = ['if ', 'for ', 'while ', 'try:', 'except:', 'def ', 'class ']
        score = 0
        
        for line in content.splitlines():
            line = line.strip().lower()
            for indicator in complexity_indicators:
                if indicator in line:
                    score += 1
        
        return score
    
    def _identify_control_algorithms(self, content: str) -> List[str]:
        """Identify control algorithms mentioned in code"""
        algorithms = []
        content_lower = content.lower()
        
        algorithm_patterns = {
            'PID': ['pid', 'proportional', 'integral', 'derivative'],
            'Ziegler-Nichols': ['ziegler', 'nichols'],
            'Cohen-Coon': ['cohen', 'coon'],
            'Lambda Tuning': ['lambda', 'tuning'],
            'IMC': ['imc', 'internal model'],
            'MPC': ['mpc', 'model predictive'],
            'Cascade': ['cascade'],
            'Feedforward': ['feedforward', 'feed forward']
        }
        
        for algorithm, patterns in algorithm_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                algorithms.append(algorithm)
        
        return algorithms
    
    def _analyze_word_document(self, file_path: Path) -> Optional[DocumentAnalysis]:
        """Analyze Word documents for control system content"""
        if not DOCX_AVAILABLE:
            logger.warning(f"python-docx not available, skipping {file_path}")
            return None
        
        try:
            doc = Document(str(file_path))
            
            # Extract text content
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            full_text = ' '.join(paragraphs)
            
            # Extract headings
            headings = []
            for paragraph in doc.paragraphs:
                if paragraph.style.name.startswith('Heading'):
                    headings.append(paragraph.text)
            
            # Analyze content
            word_count = len(full_text.split())
            paragraph_count = len(paragraphs)
            
            # Extract control concepts and best practices
            control_concepts = self._extract_control_concepts(full_text)
            best_practices = self._extract_best_practices(full_text)
            key_topics = self._extract_key_topics(full_text)
            
            return DocumentAnalysis(
                word_count=word_count,
                paragraph_count=paragraph_count,
                headings=headings,
                key_topics=key_topics,
                control_concepts=control_concepts,
                best_practices=best_practices
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze Word document {file_path}: {e}")
            return None
    
    def _analyze_pdf_document(self, file_path: Path) -> Optional[DocumentAnalysis]:
        """Analyze PDF documents for control system content"""
        if not PDF_AVAILABLE:
            logger.warning(f"PyPDF2 not available, skipping {file_path}")
            return None
        
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
            
            # Basic analysis similar to Word documents
            paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
            word_count = len(text.split())
            
            control_concepts = self._extract_control_concepts(text)
            best_practices = self._extract_best_practices(text)
            key_topics = self._extract_key_topics(text)
            
            return DocumentAnalysis(
                word_count=word_count,
                paragraph_count=len(paragraphs),
                headings=[],  # PDF heading extraction is complex
                key_topics=key_topics,
                control_concepts=control_concepts,
                best_practices=best_practices
            )
            
        except Exception as e:
            logger.error(f"Failed to analyze PDF document {file_path}: {e}")
            return None
    
    def _analyze_csv_data(self, file_path: Path) -> Optional[DataAnalysis]:
        """Analyze CSV data files for control system variables"""
        try:
            # Read a sample of the CSV to analyze structure
            with open(file_path, 'r', encoding='utf-8') as f:
                # Detect delimiter
                sample = f.read(1024)
                f.seek(0)
                
                # Use csv.Sniffer to detect format
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(f, delimiter=delimiter)
                
                # Get column information
                columns = reader.fieldnames or []
                
                # Read sample data (first 10 rows)
                sample_data = []
                row_count = 0
                for i, row in enumerate(reader):
                    if i < 10:  # Keep only first 10 rows as sample
                        sample_data.append(dict(row))
                    row_count += 1
                
                # Analyze data types and identify control variables
                data_types = self._analyze_data_types(sample_data, columns)
                control_variables = self._identify_control_variables(columns)
                
                return DataAnalysis(
                    row_count=row_count,
                    column_count=len(columns),
                    columns=columns,
                    data_types=data_types,
                    sample_data=sample_data,
                    control_variables=control_variables
                )
                
        except Exception as e:
            logger.error(f"Failed to analyze CSV data {file_path}: {e}")
            return None
    
    def _analyze_data_types(self, sample_data: List[Dict], columns: List[str]) -> Dict[str, str]:
        """Analyze data types for CSV columns"""
        data_types = {}
        
        for column in columns:
            # Look at sample values to infer type
            sample_values = [row.get(column, '') for row in sample_data if row.get(column, '')]
            
            if not sample_values:
                data_types[column] = 'unknown'
                continue
            
            # Try to determine type
            try:
                # Try numeric
                numeric_count = 0
                for value in sample_values:
                    try:
                        float(value)
                        numeric_count += 1
                    except ValueError:
                        pass
                
                if numeric_count > len(sample_values) * 0.8:
                    data_types[column] = 'numeric'
                else:
                    data_types[column] = 'text'
                    
            except Exception:
                data_types[column] = 'text'
        
        return data_types
    
    def _identify_control_variables(self, columns: List[str]) -> List[str]:
        """Identify columns that likely contain control system variables"""
        control_vars = []
        
        control_patterns = ['pv', 'sp', 'setpoint', 'output', 'cv', 'mv', 'temp', 'pressure', 
                          'flow', 'level', 'valve', 'controller', 'pid', 'error']
        
        for column in columns:
            column_lower = column.lower()
            if any(pattern in column_lower for pattern in control_patterns):
                control_vars.append(column)
        
        return control_vars
    
    def _extract_text_content(self, file_path: Path) -> str:
        """Extract text content from text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read text file {file_path}: {e}")
                return ""
    
    def _analyze_text_content(self, content: str) -> DocumentAnalysis:
        """Analyze text content for control system information"""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        word_count = len(content.split())
        
        # Extract headings (lines that are short and followed by content)
        headings = []
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if (len(line.split()) < 10 and line.strip() and 
                i < len(lines) - 1 and lines[i + 1].strip()):
                headings.append(line.strip())
        
        control_concepts = self._extract_control_concepts(content)
        best_practices = self._extract_best_practices(content)
        key_topics = self._extract_key_topics(content)
        
        return DocumentAnalysis(
            word_count=word_count,
            paragraph_count=len(paragraphs),
            headings=headings[:20],  # Limit to first 20 headings
            key_topics=key_topics,
            control_concepts=control_concepts,
            best_practices=best_practices
        )
    
    def _extract_control_concepts(self, text: str) -> List[str]:
        """Extract control system concepts from text"""
        concepts = []
        text_lower = text.lower()
        
        for category, terms in self.control_keywords.items():
            for term in terms:
                if term.lower() in text_lower:
                    concepts.append(term)
        
        return list(set(concepts))  # Remove duplicates
    
    def _extract_best_practices(self, text: str) -> List[str]:
        """Extract best practices from text"""
        practices = []
        
        # Look for sentences containing best practice indicators
        practice_indicators = ['best practice', 'recommend', 'should', 'must', 'guideline', 
                             'rule of thumb', 'important', 'critical']
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in practice_indicators):
                cleaned = sentence.strip()
                if len(cleaned) > 20 and len(cleaned) < 200:  # Reasonable length
                    practices.append(cleaned)
        
        return practices[:10]  # Limit to first 10 practices
    
    def _extract_key_topics(self, text: str) -> List[str]:
        """Extract key topics from text using simple keyword frequency"""
        # Simple topic extraction based on important control terms
        important_terms = []
        
        for category, terms in self.control_keywords.items():
            for term in terms:
                if term.lower() in text.lower():
                    important_terms.append(term)
        
        # Count frequency and return most common
        from collections import Counter
        term_counts = Counter(important_terms)
        return [term for term, count in term_counts.most_common(10)]
    
    def get_scan_summary(self) -> Dict[str, Any]:
        """Get a summary of the scan results"""
        if not self.scan_results:
            return {"error": "No scan results available"}
        
        summary = {
            "total_files": len(self.scan_results),
            "file_types": {},
            "control_types": {},
            "complexity_levels": {},
            "total_size_bytes": 0,
            "processing_errors": 0
        }
        
        for result in self.scan_results:
            # File type distribution
            file_type = result.metadata.file_type
            summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1
            
            # Total size
            summary["total_size_bytes"] += result.metadata.size_bytes
            
            # Processing errors
            if result.processing_errors:
                summary["processing_errors"] += 1
            
            # Schema-specific analysis
            if result.schema_analysis:
                control_type = result.schema_analysis.control_type
                complexity = result.schema_analysis.complexity_level
                
                summary["control_types"][control_type] = summary["control_types"].get(control_type, 0) + 1
                summary["complexity_levels"][complexity] = summary["complexity_levels"].get(complexity, 0) + 1
        
        return summary
    
    def export_results(self, output_path: str) -> str:
        """Export scan results to JSON file"""
        try:
            # Convert scan results to serializable format
            export_data = {
                "scan_timestamp": datetime.now().isoformat(),
                "context_path": str(self.context_path),
                "summary": self.get_scan_summary(),
                "results": []
            }
            
            for result in self.scan_results:
                result_dict = asdict(result)
                # Convert datetime objects to ISO strings
                if result_dict["metadata"]["created_time"]:
                    result_dict["metadata"]["created_time"] = result_dict["metadata"]["created_time"].isoformat()
                if result_dict["metadata"]["modified_time"]:
                    result_dict["metadata"]["modified_time"] = result_dict["metadata"]["modified_time"].isoformat()
                
                export_data["results"].append(result_dict)
            
            # Write to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Scan results exported to: {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to export scan results: {e}")
            raise


def main():
    """CLI entry point for context scanner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Context Scanner for Phase 24.1")
    parser.add_argument("context_path", help="Path to context directory")
    parser.add_argument("--output", "-o", help="Output file for scan results")
    parser.add_argument("--recursive", "-r", action="store_true", help="Scan recursively")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create scanner and run analysis
    scanner = ContextScanner(args.context_path)
    results = scanner.scan_directory(recursive=args.recursive)
    
    # Print summary
    summary = scanner.get_scan_summary()
    print(f"\n📊 Context Scan Complete!")
    print(f"📁 Total files: {summary['total_files']}")
    print(f"📦 File types: {summary['file_types']}")
    print(f"🎛️  Control types: {summary['control_types']}")
    print(f"🔧 Complexity levels: {summary['complexity_levels']}")
    print(f"💾 Total size: {summary['total_size_bytes'] / 1024 / 1024:.1f} MB")
    
    if summary['processing_errors'] > 0:
        print(f"⚠️ Processing errors: {summary['processing_errors']}")
    
    # Export results if requested
    if args.output:
        scanner.export_results(args.output)


if __name__ == "__main__":
    main() 