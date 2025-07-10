#!/usr/bin/env python3
"""
🤖 Specialized File Processors - AI Task Orchestrator Implementation

Phase 4: Advanced file processing with embedding generation for multi-database storage.
Specialized processors for Python, Markdown, JSON, YAML, SQL, and other file types.

Author: AI Task Orchestrator
Created: 2025-01-09
Phase: Codebase Ingestion (Step 3 of 6) - File Processing
"""

import os
import json
import ast
import re
import hashlib
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from database_manager import DatabaseManager, DatabaseType, MemoryTier
from codebase_analyzer import FileType, AnalysisResult, StructuralAnalysis

# Optional imports
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_metadata_serialization(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fix metadata dictionary to ensure all values are JSON serializable
    
    Converts datetime objects to ISO format strings and handles other
    non-serializable objects that might cause storage failures.
    """
    fixed_metadata = {}
    
    for key, value in metadata.items():
        if isinstance(value, datetime):
            fixed_metadata[key] = value.isoformat()
        elif hasattr(value, '__dict__'):
            # Handle complex objects by converting to dict
            try:
                fixed_metadata[key] = asdict(value) if hasattr(value, '__dataclass_fields__') else str(value)
            except:
                fixed_metadata[key] = str(value)
        elif isinstance(value, (list, tuple)):
            # Handle lists/tuples that might contain non-serializable objects
            fixed_metadata[key] = [
                item.isoformat() if isinstance(item, datetime) else str(item)
                for item in value
            ]
        else:
            fixed_metadata[key] = value
    
    return fixed_metadata

@dataclass
class ProcessedContent:
    """Processed file content for database storage"""
    file_id: str
    content_chunks: List[Dict[str, Any]]
    embeddings: List[List[float]]
    metadata: Dict[str, Any]
    database_routing: Dict[MemoryTier, Dict[str, Any]]

class EmbeddingGenerator:
    """Mock embedding generator (replace with OpenAI API)"""
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """Generate mock embedding (replace with actual OpenAI call)"""
        # Mock embedding - 384 dimensions
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        
        # Generate consistent pseudo-random embedding
        import random
        random.seed(seed)
        return [random.uniform(-1, 1) for _ in range(384)]

class PythonFileProcessor:
    """Specialized Python file processor"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
    
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process Python file for multi-database storage"""
        file_path = analysis_result.file_metadata.path
        
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = []
        embeddings = []
        
        # Process functions
        if analysis_result.structural_analysis:
            for func in analysis_result.structural_analysis.functions:
                chunk = {
                    'type': 'function',
                    'name': func['name'],
                    'content': f"Function {func['name']} with args: {func['args']}",
                    'line_start': func['line_start'],
                    'line_end': func.get('line_end', func['line_start']),
                    'docstring': func.get('docstring', ''),
                    'metadata': {
                        'is_async': func.get('is_async', False),
                        'decorators': func.get('decorators', [])
                    }
                }
                chunks.append(chunk)
                
                # Generate embedding for function
                embedding_text = f"{func['name']} {chunk['content']} {func.get('docstring', '')}"
                embeddings.append(self.embedding_generator.generate_embedding(embedding_text))
            
            # Process classes
            for cls in analysis_result.structural_analysis.classes:
                chunk = {
                    'type': 'class',
                    'name': cls['name'],
                    'content': f"Class {cls['name']} with methods: {cls.get('methods', [])}",
                    'line_start': cls['line_start'], 
                    'line_end': cls.get('line_end', cls['line_start']),
                    'docstring': cls.get('docstring', ''),
                    'metadata': {
                        'bases': cls.get('bases', []),
                        'methods': cls.get('methods', [])
                    }
                }
                chunks.append(chunk)
                
                embedding_text = f"{cls['name']} {chunk['content']} {cls.get('docstring', '')}"
                embeddings.append(self.embedding_generator.generate_embedding(embedding_text))
        
        # Database routing
        database_routing = {
            MemoryTier.LONG_TERM: {
                'table': 'python_files',
                'data': {
                    'file_path': file_path,
                    'content': content,
                    'functions': analysis_result.structural_analysis.functions if analysis_result.structural_analysis else [],
                    'classes': analysis_result.structural_analysis.classes if analysis_result.structural_analysis else [],
                    'imports': analysis_result.structural_analysis.imports if analysis_result.structural_analysis else [],
                    'metadata': fix_metadata_serialization(asdict(analysis_result.file_metadata))
                }
            },
            MemoryTier.MEDIUM_TERM: {
                'nodes': [
                    {
                        'type': 'PythonFile',
                        'properties': {
                            'name': Path(file_path).name,
                            'path': file_path,
                            'functions_count': len(analysis_result.structural_analysis.functions) if analysis_result.structural_analysis else 0,
                            'classes_count': len(analysis_result.structural_analysis.classes) if analysis_result.structural_analysis else 0
                        }
                    }
                ],
                'relationships': []
            },
            MemoryTier.PATTERN_MATCHING: {
                'collection': 'python_code',
                'points': [
                    {
                        'id': str(uuid.uuid5(uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), f"{file_path}_{i}")),
                        'vector': embedding,
                        'payload': chunk
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            }
        }
        
        return ProcessedContent(
            file_id=hashlib.md5(file_path.encode()).hexdigest(),
            content_chunks=chunks,
            embeddings=embeddings,
            metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
            database_routing=database_routing
        )

class MarkdownFileProcessor:
    """Specialized Markdown file processor"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
    
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process Markdown file for knowledge extraction"""
        file_path = analysis_result.file_metadata.path
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        chunks = []
        embeddings = []
        
        # Extract headings and sections
        if analysis_result.structural_analysis:
            for heading in analysis_result.structural_analysis.functions:  # headings stored as functions
                chunk = {
                    'type': 'heading',
                    'level': heading.get('level', 1),
                    'text': heading.get('text', ''),
                    'line': heading.get('line', 0),
                    'content': heading.get('text', '')
                }
                chunks.append(chunk)
                
                embedding_text = f"Heading level {chunk['level']}: {chunk['text']}"
                embeddings.append(self.embedding_generator.generate_embedding(embedding_text))
        
        # Process entire document as knowledge
        full_doc_chunk = {
            'type': 'document',
            'content': content,
            'title': Path(file_path).stem,
            'word_count': len(content.split())
        }
        chunks.append(full_doc_chunk)
        embeddings.append(self.embedding_generator.generate_embedding(content))
        
        database_routing = {
            MemoryTier.LONG_TERM: {
                'table': 'documentation',
                'data': {
                    'file_path': file_path,
                    'content': content,
                    'title': Path(file_path).stem,
                    'headings': [h for h in chunks if h['type'] == 'heading'],
                    'metadata': fix_metadata_serialization(asdict(analysis_result.file_metadata))
                }
            },
            MemoryTier.MEDIUM_TERM: {
                'nodes': [{
                    'type': 'Documentation',
                    'properties': {
                        'title': Path(file_path).stem,
                        'path': file_path,
                        'headings_count': len([c for c in chunks if c['type'] == 'heading'])
                    }
                }]
            },
            MemoryTier.PATTERN_MATCHING: {
                'collection': 'documentation',
                'points': [
                    {
                        'id': str(uuid.uuid5(uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), f"{file_path}_{i}")),
                        'vector': embedding,
                        'payload': chunk
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            }
        }
        
        return ProcessedContent(
            file_id=hashlib.md5(file_path.encode()).hexdigest(),
            content_chunks=chunks,
            embeddings=embeddings,
            metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
            database_routing=database_routing
        )

class JSONFileProcessor:
    """Specialized JSON configuration processor"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
    
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process JSON file for configuration management"""
        file_path = analysis_result.file_metadata.path
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        try:
            json_data = json.loads(content)
        except json.JSONDecodeError:
            json_data = {}
        
        chunks = []
        embeddings = []
        
        # Process JSON structure
        def extract_json_chunks(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    chunk = {
                        'type': 'json_field',
                        'path': current_path,
                        'key': key,
                        'value': str(value)[:200],  # Truncate long values
                        'value_type': type(value).__name__
                    }
                    chunks.append(chunk)
                    
                    embedding_text = f"JSON field {current_path}: {key} = {str(value)[:100]}"
                    embeddings.append(self.embedding_generator.generate_embedding(embedding_text))
                    
                    if isinstance(value, (dict, list)):
                        extract_json_chunks(value, current_path)
        
        extract_json_chunks(json_data)
        
        database_routing = {
            MemoryTier.LONG_TERM: {
                'table': 'configuration_files',
                'data': {
                    'file_path': file_path,
                    'content': content,
                    'parsed_data': json_data,
                    'metadata': fix_metadata_serialization(asdict(analysis_result.file_metadata))
                }
            },
            MemoryTier.PATTERN_MATCHING: {
                'collection': 'configurations',
                'points': [
                    {
                        'id': str(uuid.uuid5(uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8'), f"{file_path}_{i}")),
                        'vector': embedding,
                        'payload': chunk
                    }
                    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
                ]
            }
        }
        
        return ProcessedContent(
            file_id=hashlib.md5(file_path.encode()).hexdigest(),
            content_chunks=chunks,
            embeddings=embeddings,
            metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
            database_routing=database_routing
        )

class FileProcessorOrchestrator:
    """
    🎯 File Processing Orchestrator
    
    Coordinates specialized file processors for different file types,
    generating embeddings and routing data to appropriate databases.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.processors = {
            FileType.PYTHON: PythonFileProcessor(db_manager),
            FileType.MARKDOWN: MarkdownFileProcessor(db_manager),
            FileType.JSON: JSONFileProcessor(db_manager),
        }
        
        # Add YAML processor if available
        if YAML_AVAILABLE:
            self.processors[FileType.YAML] = JSONFileProcessor(db_manager)  # Reuse JSON processor
    
    def process_file(self, analysis_result: AnalysisResult) -> Optional[ProcessedContent]:
        """Process file based on its type"""
        file_type = analysis_result.file_metadata.file_type
        
        if file_type in self.processors:
            try:
                return self.processors[file_type].process(analysis_result)
            except Exception as e:
                logger.error(f"Error processing {analysis_result.file_metadata.path}: {str(e)}")
                return None
        else:
            logger.warning(f"No processor available for file type: {file_type}")
            return None
    
    async def store_processed_content(self, processed_content: ProcessedContent) -> Dict[str, bool]:
        """Store processed content in appropriate databases"""
        results = {}
        
        for tier, data in processed_content.database_routing.items():
            try:
                if tier == MemoryTier.LONG_TERM:
                    # Store in PostgreSQL with proper file_path handling
                    table = data['table']
                    content_data = data['data']
                    file_path = content_data.get('file_path', 'unknown/path')
                    
                    # Ensure file_path is never null
                    if not file_path or file_path.strip() == "":
                        file_path = f"unknown/file_{int(datetime.now().timestamp())}"
                    
                    query = f"INSERT INTO {table} (file_path, file_name, data) VALUES (%s, %s, %s)"
                    file_name = Path(file_path).name if file_path != "unknown/path" else "unknown_file"
                    
                    result = await self.db_manager.execute_query(
                        DatabaseType.POSTGRESQL, 
                        query, 
                        (file_path, file_name, json.dumps(content_data))
                    )
                    results[f"{tier.value}_postgresql"] = result.success
                
                elif tier == MemoryTier.MEDIUM_TERM:
                    # Store in Neo4j
                    for node in data.get('nodes', []):
                        query = f"""
                        CREATE (n:{node['type']})
                        SET n += $properties
                        RETURN n
                        """
                        result = await self.db_manager.execute_query(
                            DatabaseType.NEO4J,
                            query,
                            {"properties": node['properties']}
                        )
                        results[f"{tier.value}_neo4j"] = result.success
                
                elif tier == MemoryTier.PATTERN_MATCHING:
                    # Store in Qdrant (real implementation)
                    collection = data['collection']
                    points = data['points']
                    
                    # Real Qdrant storage using proper upsert operation
                    result = await self.db_manager.execute_query(
                        DatabaseType.QDRANT,
                        "upsert",
                        {"collection": collection, "points": points}
                    )
                    results[f"{tier.value}_qdrant"] = result.success if result else False
                    
            except Exception as e:
                logger.error(f"Error storing to {tier.value}: {str(e)}")
                results[f"{tier.value}_error"] = str(e)
        
        return results

async def main():
    """
    🚀 Main demonstration of file processing system
    """
    print("🤖 Specialized File Processors - AI Task Orchestrator Implementation")
    print("=" * 70)
    
    # Initialize components
    db_manager = DatabaseManager()
    processor = FileProcessorOrchestrator(db_manager)
    
    try:
        # Initialize database connections
        print("\n🔗 Step 1: Initializing Database Connections")
        await db_manager.initialize_all_connections()
        
        # Demo file processing
        print("\n📝 Step 2: Processing Demo Files")
        
        # Create sample analysis results
        from codebase_analyzer import FileMetadata
        
        demo_files = [
            {
                'path': __file__,
                'type': FileType.PYTHON,
                'name': 'Demo Python Processing'
            }
        ]
        
        for demo_file in demo_files:
            if Path(demo_file['path']).exists():
                print(f"\n📁 Processing: {demo_file['name']}")
                
                # Create mock analysis result
                metadata = FileMetadata(
                    path=demo_file['path'],
                    name=Path(demo_file['path']).name,
                    extension=Path(demo_file['path']).suffix,
                    size_bytes=0,
                    created_time=datetime.now(),
                    modified_time=datetime.now(),
                    accessed_time=datetime.now(),
                    encoding='utf-8',
                    mime_type='text/plain',
                    file_type=demo_file['type'],
                    hash_md5='demo',
                    hash_sha256='demo',
                    line_count=100,
                    is_binary=False
                )
                
                # Create structural analysis for Python
                structural = StructuralAnalysis(
                    imports=['os', 'json', 'logging'],
                    exports=[],
                    functions=[{
                        'name': 'demo_function',
                        'args': ['arg1', 'arg2'], 
                        'line_start': 1,
                        'line_end': 10,
                        'docstring': 'Demo function for testing'
                    }],
                    classes=[{
                        'name': 'DemoClass',
                        'line_start': 20,
                        'line_end': 50,
                        'methods': ['demo_method'],
                        'docstring': 'Demo class for testing'
                    }],
                    variables=[],
                    dependencies=['os', 'json'],
                    ast_nodes=50,
                    complexity_score=5.0,
                    documentation_coverage=0.8
                )
                
                analysis_result = AnalysisResult(
                    session_id="demo",
                    file_metadata=metadata,
                    structural_analysis=structural
                )
                
                # Process file
                processed = processor.process_file(analysis_result)
                
                if processed:
                    print(f"✅ Generated {len(processed.content_chunks)} content chunks")
                    print(f"✅ Generated {len(processed.embeddings)} embeddings")
                    print(f"✅ Routing to {len(processed.database_routing)} memory tiers")
                    
                    # Store processed content
                    storage_results = await processor.store_processed_content(processed)
                    print(f"✅ Storage results: {storage_results}")
                else:
                    print("❌ Processing failed")
        
        print("\n🎯 File processing demonstration complete!")
        
    except Exception as e:
        logger.error(f"Error during demonstration: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return 1
    
    finally:
        await db_manager.close_all_connections()
    
    return 0

if __name__ == "__main__":
    import asyncio
    exit(asyncio.run(main())) 