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

class SQLFileProcessor:
    """
    🗄️ SQL File Processor
    
    Processes SQL files including database dumps, schema definitions,
    and SQL scripts for database management and analysis.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
        
    def _parse_sql_statements(self, content: str) -> List[Dict[str, Any]]:
        """Parse SQL content into individual statements"""
        statements = []
        
        # Split by semicolons but handle quoted strings
        current_statement = ""
        in_quote = False
        quote_char = None
        
        for char in content:
            if char in ["'", '"'] and not in_quote:
                in_quote = True
                quote_char = char
            elif char == quote_char and in_quote:
                in_quote = False
                quote_char = None
            elif char == ';' and not in_quote:
                if current_statement.strip():
                    statements.append(current_statement.strip())
                current_statement = ""
                continue
            
            current_statement += char
        
        # Add final statement if exists
        if current_statement.strip():
            statements.append(current_statement.strip())
        
        # Analyze each statement
        parsed_statements = []
        for i, stmt in enumerate(statements):
            if not stmt or stmt.startswith('--'):
                continue
                
            stmt_upper = stmt.upper().strip()
            
            # Determine statement type
            if stmt_upper.startswith('CREATE'):
                stmt_type = 'CREATE'
                if 'TABLE' in stmt_upper:
                    object_type = 'TABLE'
                elif 'SCHEMA' in stmt_upper:
                    object_type = 'SCHEMA'
                elif 'INDEX' in stmt_upper:
                    object_type = 'INDEX'
                else:
                    object_type = 'UNKNOWN'
            elif stmt_upper.startswith('INSERT'):
                stmt_type = 'INSERT'
                object_type = 'DATA'
            elif stmt_upper.startswith('UPDATE'):
                stmt_type = 'UPDATE'
                object_type = 'DATA'
            elif stmt_upper.startswith('DELETE'):
                stmt_type = 'DELETE'
                object_type = 'DATA'
            elif stmt_upper.startswith('ALTER'):
                stmt_type = 'ALTER'
                object_type = 'SCHEMA'
            elif stmt_upper.startswith('DROP'):
                stmt_type = 'DROP'
                object_type = 'SCHEMA'
            elif stmt_upper.startswith('SET'):
                stmt_type = 'SET'
                object_type = 'CONFIG'
            elif stmt_upper.startswith('SELECT'):
                stmt_type = 'SELECT'
                object_type = 'QUERY'
            else:
                stmt_type = 'OTHER'
                object_type = 'UNKNOWN'
            
            parsed_statements.append({
                'statement_id': i,
                'type': stmt_type,
                'object_type': object_type,
                'content': stmt,
                'length': len(stmt)
            })
        
        return parsed_statements
    
    def _detect_database_type(self, content: str) -> str:
        """Detect database type from SQL content"""
        content_upper = content.upper()
        
        if 'POSTGRESQL' in content_upper or 'PG_DUMP' in content_upper:
            return 'postgresql'
        elif 'MYSQL' in content_upper or 'MARIADB' in content_upper:
            return 'mysql'
        elif 'SQLITE' in content_upper:
            return 'sqlite'
        elif 'ORACLE' in content_upper:
            return 'oracle'
        elif 'SQL SERVER' in content_upper or 'MSSQL' in content_upper:
            return 'sqlserver'
        else:
            return 'unknown'
    
    def _extract_schema_objects(self, statements: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Extract database objects from SQL statements"""
        objects = {
            'schemas': [],
            'tables': [],
            'indexes': [],
            'functions': [],
            'views': []
        }
        
        for stmt in statements:
            content = stmt['content'].upper()
            
            if stmt['type'] == 'CREATE':
                if 'CREATE SCHEMA' in content:
                    # Extract schema name
                    match = re.search(r'CREATE SCHEMA\s+([^\s;]+)', content)
                    if match:
                        objects['schemas'].append(match.group(1))
                
                elif 'CREATE TABLE' in content:
                    # Extract table name
                    match = re.search(r'CREATE TABLE\s+([^\s(;]+)', content)
                    if match:
                        objects['tables'].append(match.group(1))
                
                elif 'CREATE INDEX' in content:
                    # Extract index name
                    match = re.search(r'CREATE.*INDEX\s+([^\s(;]+)', content)
                    if match:
                        objects['indexes'].append(match.group(1))
                
                elif 'CREATE FUNCTION' in content:
                    # Extract function name
                    match = re.search(r'CREATE.*FUNCTION\s+([^\s(;]+)', content)
                    if match:
                        objects['functions'].append(match.group(1))
                
                elif 'CREATE VIEW' in content:
                    # Extract view name
                    match = re.search(r'CREATE VIEW\s+([^\s(;]+)', content)
                    if match:
                        objects['views'].append(match.group(1))
        
        return objects
    
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process SQL file content"""
        try:
            # Read file content
            file_path = Path(analysis_result.file_metadata.path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse SQL statements
            statements = self._parse_sql_statements(content)
            
            # Detect database type
            db_type = self._detect_database_type(content)
            
            # Extract schema objects
            schema_objects = self._extract_schema_objects(statements)
            
            # Create content chunks (group statements by type)
            chunks = []
            
            # Group statements by type for better chunking
            statement_groups = {}
            for stmt in statements:
                stmt_type = stmt['type']
                if stmt_type not in statement_groups:
                    statement_groups[stmt_type] = []
                statement_groups[stmt_type].append(stmt)
            
            # Create chunks for each statement type
            for stmt_type, group_statements in statement_groups.items():
                if not group_statements:
                    continue
                    
                chunk = {
                    'type': 'sql_statement_group',
                    'statement_type': stmt_type,
                    'statement_count': len(group_statements),
                    'statements': group_statements[:5],  # Limit to first 5 for chunk size
                    'total_length': sum(stmt['length'] for stmt in group_statements)
                }
                chunks.append(chunk)
            
            # Add overall file summary chunk
            summary_chunk = {
                'type': 'sql_file_summary',
                'database_type': db_type,
                'total_statements': len(statements),
                'statement_types': list(statement_groups.keys()),
                'schema_objects': schema_objects,
                'file_size': len(content)
            }
            chunks.append(summary_chunk)
            
            # Generate embeddings
            embeddings = []
            for chunk in chunks:
                # Create embedding text based on chunk type
                if chunk['type'] == 'sql_statement_group':
                    embedding_text = f"SQL {chunk['statement_type']} statements: {chunk['statement_count']} statements"
                    if chunk['statements']:
                        embedding_text += f" Example: {chunk['statements'][0]['content'][:200]}"
                else:
                    embedding_text = f"SQL file summary: {db_type} database with {len(statements)} statements"
                    if schema_objects['tables']:
                        embedding_text += f" Tables: {', '.join(schema_objects['tables'][:5])}"
                
                embeddings.append(self.embedding_generator.generate_embedding(embedding_text))
            
            # Create processed content
            processed_data = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "sql",
                "content": content,
                "metadata": {
                    "database_type": db_type,
                    "statement_count": len(statements),
                    "statement_types": list(statement_groups.keys()),
                    "schema_objects": schema_objects,
                    "file_size_bytes": len(content),
                    "line_count": len(content.split('\n')),
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # Database routing
            database_routing = {
                MemoryTier.LONG_TERM: {
                    "table": "configuration_files",
                    "data": processed_data
                },
                MemoryTier.MEDIUM_TERM: {
                    "nodes": [{
                        "type": "SQLFile",
                        "properties": {
                            "path": str(file_path),
                            "name": file_path.name,
                            "database_type": db_type,
                            "statement_count": len(statements),
                            "table_count": len(schema_objects['tables']),
                            "schema_count": len(schema_objects['schemas']),
                            "file_type": "sql"
                        }
                    }]
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
                file_id=hashlib.md5(str(file_path).encode()).hexdigest(),
                content_chunks=chunks,
                embeddings=embeddings,
                metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
                database_routing=database_routing
            )
            
        except Exception as e:
            logger.error(f"Error processing SQL file {analysis_result.file_metadata.path}: {str(e)}")
            return None

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
            FileType.TEXT: TextFileProcessor(db_manager),
            FileType.SHELL: ShellFileProcessor(db_manager),
            FileType.DOCKERFILE: DockerfileProcessor(db_manager),
            FileType.SQL: SQLFileProcessor(db_manager),
            FileType.UNKNOWN: GenericFileProcessor(db_manager),
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


class TextFileProcessor:
    """
    📄 Text File Processor
    
    Processes plain text files (.txt, .log, etc.) for documentation storage
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
        
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process text file content"""
        try:
            # Read file content
            file_path = Path(analysis_result.file_metadata.path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract basic metadata
            lines = content.split('\n')
            word_count = len(content.split())
            
            # Create content chunks
            chunks = [{
                'type': 'text_document',
                'content': content,
                'word_count': word_count,
                'line_count': len(lines),
                'is_log_file': file_path.suffix.lower() == '.log'
            }]
            
            # Generate embeddings
            embeddings = [self.embedding_generator.generate_embedding(content)]
            
            # Create processed content
            processed_data = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "text",
                "content": content,
                "metadata": {
                    "line_count": len(lines),
                    "word_count": word_count,
                    "character_count": len(content),
                    "is_log_file": file_path.suffix.lower() == '.log',
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # Database routing
            database_routing = {
                MemoryTier.LONG_TERM: {
                    "table": "documentation",
                    "data": processed_data
                },
                MemoryTier.MEDIUM_TERM: {
                    "nodes": [{
                        "type": "TextFile",
                        "properties": {
                            "path": str(file_path),
                            "name": file_path.name,
                            "word_count": word_count,
                            "line_count": len(lines),
                            "file_type": "text"
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
                file_id=hashlib.md5(str(file_path).encode()).hexdigest(),
                content_chunks=chunks,
                embeddings=embeddings,
                metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
                database_routing=database_routing
            )
            
        except Exception as e:
            logger.error(f"Error processing text file {analysis_result.file_metadata.path}: {str(e)}")
            return None


class ShellFileProcessor:
    """
    🐚 Shell Script Processor
    
    Processes shell scripts (.sh, .bash, .zsh) for configuration and automation
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
        
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process shell script content"""
        try:
            # Read file content
            file_path = Path(analysis_result.file_metadata.path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract shell script metadata
            lines = content.split('\n')
            shebang = lines[0] if lines and lines[0].startswith('#!') else None
            
            # Count different types of shell constructs
            function_count = len(re.findall(r'function\s+\w+|^\w+\s*\(\)', content, re.MULTILINE))
            variable_count = len(re.findall(r'^\s*\w+\s*=', content, re.MULTILINE))
            command_count = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
            
            # Create content chunks
            chunks = [{
                'type': 'shell_script',
                'content': content,
                'shebang': shebang,
                'function_count': function_count,
                'variable_count': variable_count,
                'command_count': command_count,
                'shell_type': self._detect_shell_type(content, file_path)
            }]
            
            # Generate embeddings
            embeddings = [self.embedding_generator.generate_embedding(content)]
            
            # Create processed content
            processed_data = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "shell_script",
                "content": content,
                "metadata": {
                    "shebang": shebang,
                    "line_count": len(lines),
                    "function_count": function_count,
                    "variable_count": variable_count,
                    "command_count": command_count,
                    "shell_type": self._detect_shell_type(content, file_path),
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # Database routing
            database_routing = {
                MemoryTier.LONG_TERM: {
                    "table": "configuration_files",
                    "data": processed_data
                },
                MemoryTier.MEDIUM_TERM: {
                    "nodes": [{
                        "type": "ShellScript",
                        "properties": {
                            "path": str(file_path),
                            "name": file_path.name,
                            "shell_type": self._detect_shell_type(content, file_path),
                            "function_count": function_count,
                            "variable_count": variable_count,
                            "file_type": "shell_script"
                        }
                    }]
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
                file_id=hashlib.md5(str(file_path).encode()).hexdigest(),
                content_chunks=chunks,
                embeddings=embeddings,
                metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
                database_routing=database_routing
            )
            
        except Exception as e:
            logger.error(f"Error processing shell script {analysis_result.file_metadata.path}: {str(e)}")
            return None
    
    def _detect_shell_type(self, content: str, file_path: Path) -> str:
        """Detect shell type from shebang or file extension"""
        first_line = content.split('\n')[0] if content else ""
        
        if 'bash' in first_line:
            return 'bash'
        elif 'zsh' in first_line:
            return 'zsh'
        elif 'sh' in first_line:
            return 'sh'
        elif file_path.suffix == '.bash':
            return 'bash'
        elif file_path.suffix == '.zsh':
            return 'zsh'
        else:
            return 'shell'


class GenericFileProcessor:
    """
    🔧 Generic File Processor
    
    Handles unknown file types with basic content extraction
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
        
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process unknown file type with basic extraction"""
        try:
            file_path = Path(analysis_result.file_metadata.path)
            
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                is_text = True
            except:
                # If text reading fails, read as binary and get basic info
                with open(file_path, 'rb') as f:
                    binary_content = f.read()
                content = f"Binary file: {len(binary_content)} bytes"
                is_text = False
            
            # Extract basic metadata
            file_size = file_path.stat().st_size
            file_ext = file_path.suffix.lower()
            
            # Create content chunks
            chunks = [{
                'type': 'unknown_file',
                'content': content if is_text else f"Binary file ({file_size} bytes)",
                'file_extension': file_ext,
                'file_size_bytes': file_size,
                'is_text_file': is_text
            }]
            
            # Generate embeddings (only for text files)
            if is_text and content.strip():
                embeddings = [self.embedding_generator.generate_embedding(content)]
            else:
                embeddings = []
            
            # Create processed content
            processed_data = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "unknown",
                "content": content if is_text else f"Binary file ({file_size} bytes)",
                "metadata": {
                    "file_extension": file_ext,
                    "file_size_bytes": file_size,
                    "is_text_file": is_text,
                    "mime_type": analysis_result.file_metadata.mime_type,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # Database routing - store as configuration for unknown types
            database_routing = {
                MemoryTier.LONG_TERM: {
                    "table": "configuration_files",
                    "data": processed_data
                },
                MemoryTier.MEDIUM_TERM: {
                    "nodes": [{
                        "type": "UnknownFile",
                        "properties": {
                            "path": str(file_path),
                            "name": file_path.name,
                            "file_extension": file_ext,
                            "file_size_bytes": file_size,
                            "is_text_file": is_text,
                            "file_type": "unknown"
                        }
                    }]
                }
            }
            
            # Only add vector storage if we have embeddings
            if embeddings:
                database_routing[MemoryTier.PATTERN_MATCHING] = {
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
            
            return ProcessedContent(
                file_id=hashlib.md5(str(file_path).encode()).hexdigest(),
                content_chunks=chunks,
                embeddings=embeddings,
                metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
                database_routing=database_routing
            )
            
        except Exception as e:
            logger.error(f"Error processing unknown file {analysis_result.file_metadata.path}: {str(e)}")
            return None

class DockerfileProcessor:
    """
    🐳 Dockerfile Processor
    
    Processes Dockerfiles for container configuration management
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.embedding_generator = EmbeddingGenerator()
        
    def process(self, analysis_result: AnalysisResult) -> ProcessedContent:
        """Process Dockerfile content"""
        try:
            # Read file content
            file_path = Path(analysis_result.file_metadata.path)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract Dockerfile metadata
            lines = content.split('\n')
            
            # Parse Dockerfile instructions
            instructions = []
            base_image = None
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(' ', 1)
                    if len(parts) >= 2:
                        instruction = parts[0].upper()
                        value = parts[1] if len(parts) > 1 else ""
                        instructions.append({'instruction': instruction, 'value': value})
                        
                        if instruction == 'FROM' and not base_image:
                            base_image = value
            
            # Create content chunks
            chunks = [{
                'type': 'dockerfile',
                'content': content,
                'base_image': base_image,
                'instructions': instructions,
                'instruction_count': len(instructions)
            }]
            
            # Generate embeddings
            embeddings = [self.embedding_generator.generate_embedding(content)]
            
            # Create processed content
            processed_data = {
                "file_path": str(file_path),
                "file_name": file_path.name,
                "file_type": "dockerfile",
                "content": content,
                "metadata": {
                    "base_image": base_image,
                    "instruction_count": len(instructions),
                    "instructions": instructions,
                    "line_count": len(lines),
                    "processed_at": datetime.now().isoformat()
                }
            }
            
            # Database routing
            database_routing = {
                MemoryTier.LONG_TERM: {
                    "table": "configuration_files",
                    "data": processed_data
                },
                MemoryTier.MEDIUM_TERM: {
                    "nodes": [{
                        "type": "Dockerfile",
                        "properties": {
                            "path": str(file_path),
                            "name": file_path.name,
                            "base_image": base_image or "unknown",
                            "instruction_count": len(instructions),
                            "file_type": "dockerfile"
                        }
                    }]
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
                file_id=hashlib.md5(str(file_path).encode()).hexdigest(),
                content_chunks=chunks,
                embeddings=embeddings,
                metadata=fix_metadata_serialization(asdict(analysis_result.file_metadata)),
                database_routing=database_routing
            )
            
        except Exception as e:
            logger.error(f"Error processing Dockerfile {analysis_result.file_metadata.path}: {str(e)}")
            return None

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