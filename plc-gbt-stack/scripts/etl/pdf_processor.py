#!/usr/bin/env python3
"""
PDF Document Processor
Phase 3 Day 2: Document Processing Pipeline
Version: 1.0.0

This module handles PDF document processing for the PLC-GPT system:
- Text extraction from PDFs
- Intelligent chunking for embeddings
- Q&A pair generation
- Metadata extraction
"""

import hashlib
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import nltk
import pdfplumber
import structlog
from nltk.tokenize import sent_tokenize, word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class PDFProcessor:
    """Processes PDF documents for the PLC knowledge base."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor.

        Args:
            chunk_size: Target size for text chunks (in characters)
            chunk_overlap: Overlap between chunks for context preservation
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def process_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file completely.

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Processed document data including text, chunks, and metadata
        """
        logger.info(f"Processing PDF: {pdf_path}")

        result = {
            'file_path': str(pdf_path),
            'file_name': pdf_path.name,
            'file_hash': self._calculate_file_hash(pdf_path),
            'processed_date': datetime.utcnow().isoformat(),
            'metadata': {},
            'pages': [],
            'chunks': [],
            'qa_pairs': [],
            'errors': []
        }

        try:
            with pdfplumber.open(pdf_path) as pdf:
                # Extract metadata
                result['metadata'] = self._extract_metadata(pdf)

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_data = self._process_page(page, page_num)
                        result['pages'].append(page_data)
                    except Exception as e:
                        error_msg = f"Error processing page {page_num}: {str(e)}"
                        logger.error(error_msg)
                        result['errors'].append(error_msg)

                # Generate chunks from all pages
                full_text = "\n".join(p['text'] for p in result['pages'] if p.get('text'))
                result['chunks'] = self._create_chunks(full_text, result['metadata'])

                # Generate Q&A pairs
                result['qa_pairs'] = self._generate_qa_pairs(result['chunks'], result['metadata'])

        except Exception as e:
            error_msg = f"Error opening PDF: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _extract_metadata(self, pdf) -> Dict[str, Any]:
        """Extract metadata from PDF."""
        metadata = {}

        if pdf.metadata:
            metadata.update({
                'title': pdf.metadata.get('Title', ''),
                'author': pdf.metadata.get('Author', ''),
                'subject': pdf.metadata.get('Subject', ''),
                'creator': pdf.metadata.get('Creator', ''),
                'producer': pdf.metadata.get('Producer', ''),
                'creation_date': str(pdf.metadata.get('CreationDate', '')),
                'modification_date': str(pdf.metadata.get('ModDate', ''))
            })

        metadata['page_count'] = len(pdf.pages)

        return metadata

    def _process_page(self, page, page_num: int) -> Dict[str, Any]:
        """Process a single PDF page."""
        page_data = {
            'page_number': page_num,
            'text': '',
            'tables': [],
            'bbox': None
        }

        # Extract text
        text = page.extract_text()
        if text:
            page_data['text'] = self._clean_text(text)

        # Extract tables
        tables = page.extract_tables()
        if tables:
            page_data['tables'] = [self._process_table(table) for table in tables]

        # Get page dimensions
        page_data['bbox'] = {
            'x0': page.bbox[0],
            'y0': page.bbox[1],
            'x1': page.bbox[2],
            'y1': page.bbox[3]
        }

        return page_data

    def _clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Fix common OCR errors
        text = text.replace('ﬁ', 'fi')
        text = text.replace('ﬂ', 'fl')

        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^Page \d+ of \d+$', '', text, flags=re.MULTILINE)

        return text.strip()

    def _process_table(self, table: List[List[str]]) -> Dict[str, Any]:
        """Process extracted table data."""
        if not table:
            return {}

        return {
            'headers': table[0] if table else [],
            'rows': table[1:] if len(table) > 1 else [],
            'row_count': len(table),
            'column_count': len(table[0]) if table else 0
        }

    def _create_chunks(self, text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create overlapping text chunks for embedding."""
        chunks = []

        if not text:
            return chunks

        # Split into sentences
        sentences = sent_tokenize(text)

        current_chunk = []
        current_size = 0

        for sentence in sentences:
            sentence_size = len(sentence)

            # If adding this sentence exceeds chunk size, save current chunk
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(self._create_chunk_object(chunk_text, len(chunks), metadata))

                # Keep overlap
                overlap_size = 0
                overlap_sentences = []
                for sent in reversed(current_chunk):
                    overlap_size += len(sent)
                    overlap_sentences.insert(0, sent)
                    if overlap_size >= self.chunk_overlap:
                        break

                current_chunk = overlap_sentences
                current_size = overlap_size

            current_chunk.append(sentence)
            current_size += sentence_size

        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append(self._create_chunk_object(chunk_text, len(chunks), metadata))

        return chunks

    def _create_chunk_object(self, text: str, index: int, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a chunk object with metadata."""
        return {
            'id': str(uuid.uuid4()),
            'text': text,
            'chunk_index': index,
            'char_count': len(text),
            'word_count': len(word_tokenize(text)),
            'metadata': {
                'source_document': metadata.get('title', 'Unknown'),
                'document_type': 'PDF',
                'chunk_method': 'sentence_overlap'
            }
        }

    def _generate_qa_pairs(self, chunks: List[Dict[str, Any]], metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Q&A pairs from chunks."""
        qa_pairs = []

        # Extract Q&A patterns from text
        for chunk in chunks:
            text = chunk['text']

            # Pattern 1: Questions followed by answers
            qa_pattern = r'(?:Q:|Question:)\s*(.+?)(?:\n|$)(?:A:|Answer:)\s*(.+?)(?:\n|$)'
            matches = re.finditer(qa_pattern, text, re.IGNORECASE | re.MULTILINE)

            for match in matches:
                question = match.group(1).strip()
                answer = match.group(2).strip()

                if question and answer:
                    qa_pairs.append({
                        'id': str(uuid.uuid4()),
                        'question': question,
                        'answer': answer,
                        'source_chunk_id': chunk['id'],
                        'confidence': 0.9,  # High confidence for explicit Q&A
                        'extraction_method': 'pattern_matching'
                    })

            # Pattern 2: Headers as questions (e.g., "How to Configure...")
            header_pattern = r'^(How to|What is|When to|Where to|Why|Configuration of)\s+(.+?)(?:\n|$)'
            header_matches = re.finditer(header_pattern, text, re.IGNORECASE | re.MULTILINE)

            for match in header_matches:
                question = match.group(0).strip()
                # Get the next few sentences as the answer
                start_pos = match.end()
                sentences = sent_tokenize(text[start_pos:])
                answer = ' '.join(sentences[:3]) if sentences else ''

                if question and answer:
                    qa_pairs.append({
                        'id': str(uuid.uuid4()),
                        'question': question.rstrip(':'),
                        'answer': answer,
                        'source_chunk_id': chunk['id'],
                        'confidence': 0.7,  # Medium confidence for inferred Q&A
                        'extraction_method': 'header_inference'
                    })

        # Deduplicate Q&A pairs
        seen = set()
        unique_qa = []
        for qa in qa_pairs:
            key = (qa['question'].lower(), qa['answer'][:50].lower())
            if key not in seen:
                seen.add(key)
                unique_qa.append(qa)

        return unique_qa

    def extract_plc_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract PLC-specific entities from text."""
        entities = {
            'aoi_names': [],
            'udt_names': [],
            'tag_names': [],
            'routine_names': [],
            'device_names': []
        }

        # AOI pattern (e.g., MotorControl_AOI, ValveControl_AOI)
        aoi_pattern = r'\b(\w+_AOI)\b'
        entities['aoi_names'] = list(set(re.findall(aoi_pattern, text)))

        # UDT pattern (e.g., MotorData_UDT, AlarmData_UDT)
        udt_pattern = r'\b(\w+_UDT)\b'
        entities['udt_names'] = list(set(re.findall(udt_pattern, text)))

        # Tag pattern (common PLC tag formats)
        tag_pattern = r'\b([A-Z][A-Za-z0-9_]*(?:\[\d+\])?)\b'
        potential_tags = re.findall(tag_pattern, text)
        # Filter to likely tags (uppercase start, contains underscore or number)
        entities['tag_names'] = [t for t in set(potential_tags)
                                if '_' in t or any(c.isdigit() for c in t)][:20]

        # Routine names (often end with Routine or have specific patterns)
        routine_pattern = r'\b(\w+Routine|\w+_Logic|\w+_Sequence)\b'
        entities['routine_names'] = list(set(re.findall(routine_pattern, text)))

        # Device catalog numbers (e.g., 1756-L85E, 1769-IF8)
        device_pattern = r'\b(17\d{2}-[A-Z0-9]+)\b'
        entities['device_names'] = list(set(re.findall(device_pattern, text)))

        return entities


def main():
    """Main execution for testing."""
    # Test with a sample PDF
    processor = PDFProcessor()

    # Create a test PDF path
    test_pdf = Path("test_document.pdf")

    if test_pdf.exists():
        result = processor.process_pdf(test_pdf)

        print("\n" + "="*60)
        print("PDF PROCESSING RESULTS")
        print("="*60)

        print(f"\nFile: {result['file_name']}")
        print(f"Pages: {len(result['pages'])}")
        print(f"Chunks: {len(result['chunks'])}")
        print(f"Q&A Pairs: {len(result['qa_pairs'])}")

        if result['chunks']:
            print("\nFirst chunk preview:")
            print(result['chunks'][0]['text'][:200] + "...")

        if result['qa_pairs']:
            print("\nSample Q&A pairs:")
            for qa in result['qa_pairs'][:3]:
                print(f"\nQ: {qa['question']}")
                print(f"A: {qa['answer'][:100]}...")

        # Extract entities from first chunk
        if result['chunks']:
            entities = processor.extract_plc_entities(result['chunks'][0]['text'])
            print("\nExtracted PLC entities:")
            for entity_type, values in entities.items():
                if values:
                    print(f"  {entity_type}: {values}")
    else:
        print(f"Test PDF not found at {test_pdf}")
        print("Please provide a test PDF to process")


if __name__ == "__main__":
    main()
