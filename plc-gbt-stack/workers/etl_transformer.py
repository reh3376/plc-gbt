#!/usr/bin/env python3
"""
ETL Transformation Module
Created: January 1, 2025
Purpose: Transform extracted documents for Neo4j and vector database loading
"""

import os
import logging
import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

# OpenAI for embeddings
import openai
from openai import OpenAI

# Neo4j data structures
from document_parser import ExtractedDocument, PLCProgram, SpecificationDocument

@dataclass
class TransformedNode:
    """Represents a node ready for Neo4j insertion"""
    uuid: str
    label: str
    properties: Dict[str, Any]
    relationships: List[Dict[str, Any]]
    
@dataclass
class TransformedRelationship:
    """Represents a relationship ready for Neo4j insertion"""
    source_uuid: str
    target_uuid: str
    type: str
    properties: Dict[str, Any]

@dataclass
class VectorRecord:
    """Represents a vector record for Qdrant"""
    id: str
    vector: List[float]
    payload: Dict[str, Any]

@dataclass
class TransformationResult:
    """Container for transformation results"""
    nodes: List[TransformedNode]
    relationships: List[TransformedRelationship]
    vectors: List[VectorRecord]
    metadata: Dict[str, Any]
    errors: List[str]

class ETLTransformer:
    """Transforms extracted documents into graph and vector data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Configure logging
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            organization=os.getenv('OPENAI_ORG_ID')
        )
        
        # Embedding configuration
        self.embedding_model = self.config.get('embedding_model', 'text-embedding-3-large')
        self.embedding_dimensions = self.config.get('embedding_dimensions', 3072)
        self.max_chunk_size = self.config.get('max_chunk_size', 2000)
        
        # UUID cache to maintain consistency
        self.uuid_cache = {}
    
    def generate_uuid(self, identifier: str) -> str:
        """Generate consistent UUID for given identifier"""
        if identifier in self.uuid_cache:
            return self.uuid_cache[identifier]
        
        # Create deterministic UUID based on identifier
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
        generated_uuid = str(uuid.uuid5(namespace, identifier))
        self.uuid_cache[identifier] = generated_uuid
        return generated_uuid
    
    async def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text using OpenAI API"""
        try:
            # Clean and truncate text if needed
            clean_text = text.strip()
            if len(clean_text) > self.max_chunk_size:
                clean_text = clean_text[:self.max_chunk_size]
            
            if not clean_text:
                return None
            
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=clean_text,
                encoding_format="float"
            )
            
            return response.data[0].embedding
            
        except Exception as e:
            self.logger.error(f"Error generating embedding: {e}")
            return None
    
    async def transform_document(self, extracted_doc: ExtractedDocument) -> TransformationResult:
        """Transform extracted document into graph and vector data"""
        nodes = []
        relationships = []
        vectors = []
        errors = []
        
        try:
            if extracted_doc.file_type == "L5X":
                nodes, relationships, vectors = await self._transform_l5x_document(extracted_doc)
            elif extracted_doc.file_type == "PDF":
                nodes, relationships, vectors = await self._transform_pdf_document(extracted_doc)
            else:
                errors.append(f"Unsupported file type: {extracted_doc.file_type}")
            
            metadata = {
                "source_file": extracted_doc.file_path,
                "file_type": extracted_doc.file_type,
                "transformed_at": datetime.now().isoformat(),
                "node_count": len(nodes),
                "relationship_count": len(relationships),
                "vector_count": len(vectors)
            }
            
            return TransformationResult(
                nodes=nodes,
                relationships=relationships,
                vectors=vectors,
                metadata=metadata,
                errors=errors
            )
            
        except Exception as e:
            error_msg = f"Error transforming document {extracted_doc.file_path}: {e}"
            self.logger.error(error_msg)
            errors.append(error_msg)
            
            return TransformationResult(
                nodes=[],
                relationships=[],
                vectors=[],
                metadata={"error": error_msg},
                errors=errors
            )
    
    async def _transform_l5x_document(self, extracted_doc: ExtractedDocument) -> Tuple[List[TransformedNode], List[TransformedRelationship], List[VectorRecord]]:
        """Transform L5X PLC program document"""
        nodes = []
        relationships = []
        vectors = []
        
        plc_program_data = extracted_doc.content.get('plc_program', {})
        
        # Create PLC Program node
        plc_uuid = self.generate_uuid(f"plc:{plc_program_data.get('name', 'unknown')}")
        plc_node = TransformedNode(
            uuid=plc_uuid,
            label="PLCProgram",
            properties={
                "name": plc_program_data.get('name', ''),
                "firmware": plc_program_data.get('firmware', ''),
                "project": plc_program_data.get('project', ''),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "file_path": extracted_doc.file_path,
                "description": f"PLC Program from {extracted_doc.file_path}"
            },
            relationships=[]
        )
        nodes.append(plc_node)
        
        # Create PLC Program vector embedding
        plc_text = f"PLC Program: {plc_program_data.get('name', '')} " + \
                   f"Firmware: {plc_program_data.get('firmware', '')} " + \
                   f"Project: {plc_program_data.get('project', '')}"
        
        plc_embedding = await self.generate_embedding(plc_text)
        if plc_embedding:
            vectors.append(VectorRecord(
                id=plc_uuid,
                vector=plc_embedding,
                payload={
                    "type": "PLCProgram",
                    "name": plc_program_data.get('name', ''),
                    "text": plc_text,
                    "file_path": extracted_doc.file_path
                }
            ))
        
        # Transform Routines
        for routine_data in plc_program_data.get('routines', []):
            routine_uuid = self.generate_uuid(f"routine:{routine_data.get('name', 'unknown')}")
            routine_node = TransformedNode(
                uuid=routine_uuid,
                label="Routine",
                properties={
                    "name": routine_data.get('name', ''),
                    "language": routine_data.get('language', ''),
                    "type": routine_data.get('type', ''),
                    "description": routine_data.get('description', ''),
                    "file_path": extracted_doc.file_path,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                relationships=[]
            )
            nodes.append(routine_node)
            
            # Create relationships
            relationships.append(TransformedRelationship(
                source_uuid=plc_uuid,
                target_uuid=routine_uuid,
                type="CONTAINS",
                properties={"created_at": datetime.now().isoformat()}
            ))
            
            relationships.append(TransformedRelationship(
                source_uuid=routine_uuid,
                target_uuid=plc_uuid,
                type="IN_PROGRAM",
                properties={"created_at": datetime.now().isoformat()}
            ))
            
            # Create routine vector embedding
            routine_text = f"Routine: {routine_data.get('name', '')} " + \
                          f"Language: {routine_data.get('language', '')} " + \
                          f"Description: {routine_data.get('description', '')}"
            
            routine_embedding = await self.generate_embedding(routine_text)
            if routine_embedding:
                vectors.append(VectorRecord(
                    id=routine_uuid,
                    vector=routine_embedding,
                    payload={
                        "type": "Routine",
                        "name": routine_data.get('name', ''),
                        "language": routine_data.get('language', ''),
                        "text": routine_text,
                        "file_path": extracted_doc.file_path
                    }
                ))
        
        # Transform AOIs
        for aoi_data in plc_program_data.get('aois', []):
            aoi_uuid = self.generate_uuid(f"aoi:{aoi_data.get('name', 'unknown')}")
            aoi_node = TransformedNode(
                uuid=aoi_uuid,
                label="AOI",
                properties={
                    "name": aoi_data.get('name', ''),
                    "rev": aoi_data.get('revision', ''),
                    "desc": aoi_data.get('description', ''),
                    "vendor": aoi_data.get('vendor', ''),
                    "execution_context": aoi_data.get('execution_context', ''),
                    "parameters": json.dumps(aoi_data.get('parameters', [])),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                relationships=[]
            )
            nodes.append(aoi_node)
            
            # Create relationships
            relationships.append(TransformedRelationship(
                source_uuid=plc_uuid,
                target_uuid=aoi_uuid,
                type="CONTAINS",
                properties={"created_at": datetime.now().isoformat()}
            ))
            
            # Create AOI vector embedding
            aoi_text = f"Add-On Instruction: {aoi_data.get('name', '')} " + \
                       f"Revision: {aoi_data.get('revision', '')} " + \
                       f"Description: {aoi_data.get('description', '')}"
            
            aoi_embedding = await self.generate_embedding(aoi_text)
            if aoi_embedding:
                vectors.append(VectorRecord(
                    id=aoi_uuid,
                    vector=aoi_embedding,
                    payload={
                        "type": "AOI",
                        "name": aoi_data.get('name', ''),
                        "revision": aoi_data.get('revision', ''),
                        "text": aoi_text,
                        "file_path": extracted_doc.file_path
                    }
                ))
        
        # Transform UDTs
        for udt_data in plc_program_data.get('udts', []):
            udt_uuid = self.generate_uuid(f"udt:{udt_data.get('name', 'unknown')}")
            udt_node = TransformedNode(
                uuid=udt_uuid,
                label="UDT",
                properties={
                    "name": udt_data.get('name', ''),
                    "size": udt_data.get('size', 0),
                    "desc": udt_data.get('description', ''),
                    "family": udt_data.get('family', ''),
                    "class": udt_data.get('class', ''),
                    "members": json.dumps(udt_data.get('members', [])),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                relationships=[]
            )
            nodes.append(udt_node)
            
            # Create relationships
            relationships.append(TransformedRelationship(
                source_uuid=plc_uuid,
                target_uuid=udt_uuid,
                type="CONTAINS",
                properties={"created_at": datetime.now().isoformat()}
            ))
            
            # Create UDT vector embedding
            udt_text = f"User Defined Type: {udt_data.get('name', '')} " + \
                       f"Size: {udt_data.get('size', 0)} bytes " + \
                       f"Description: {udt_data.get('description', '')}"
            
            udt_embedding = await self.generate_embedding(udt_text)
            if udt_embedding:
                vectors.append(VectorRecord(
                    id=udt_uuid,
                    vector=udt_embedding,
                    payload={
                        "type": "UDT",
                        "name": udt_data.get('name', ''),
                        "size": udt_data.get('size', 0),
                        "text": udt_text,
                        "file_path": extracted_doc.file_path
                    }
                ))
        
        # Transform Tags
        for tag_data in plc_program_data.get('tags', []):
            tag_uuid = self.generate_uuid(f"tag:{tag_data.get('name', 'unknown')}")
            tag_node = TransformedNode(
                uuid=tag_uuid,
                label="Tag",
                properties={
                    "name": tag_data.get('name', ''),
                    "data_type": tag_data.get('data_type', ''),
                    "scope": tag_data.get('tag_type', ''),
                    "address": tag_data.get('name', ''),  # Simplified address
                    "description": tag_data.get('description', ''),
                    "dimensions": tag_data.get('dimensions', ''),
                    "radix": tag_data.get('radix', ''),
                    "external_access": tag_data.get('external_access', ''),
                    "usage": tag_data.get('usage', '')
                },
                relationships=[]
            )
            nodes.append(tag_node)
        
        # Transform Devices
        for device_data in plc_program_data.get('devices', []):
            device_uuid = self.generate_uuid(f"device:{device_data.get('name', 'unknown')}")
            device_node = TransformedNode(
                uuid=device_uuid,
                label="Device",
                properties={
                    "name": device_data.get('name', ''),
                    "device_type": "PLC Module",
                    "catalog_number": device_data.get('catalog_number', ''),
                    "vendor": device_data.get('vendor', ''),
                    "product_type": device_data.get('product_type', ''),
                    "major_revision": device_data.get('major_revision', ''),
                    "minor_revision": device_data.get('minor_revision', ''),
                    "description": f"{device_data.get('vendor', '')} {device_data.get('catalog_number', '')}"
                },
                relationships=[]
            )
            nodes.append(device_node)
            
            # Create device relationships
            relationships.append(TransformedRelationship(
                source_uuid=device_uuid,
                target_uuid=plc_uuid,
                type="HOSTS",
                properties={"created_at": datetime.now().isoformat()}
            ))
        
        return nodes, relationships, vectors
    
    async def _transform_pdf_document(self, extracted_doc: ExtractedDocument) -> Tuple[List[TransformedNode], List[TransformedRelationship], List[VectorRecord]]:
        """Transform PDF specification document"""
        nodes = []
        relationships = []
        vectors = []
        
        content = extracted_doc.content
        metadata = extracted_doc.metadata
        
        # Create SpecDoc node
        spec_uuid = self.generate_uuid(f"specdoc:{extracted_doc.file_path}")
        spec_node = TransformedNode(
            uuid=spec_uuid,
            label="SpecDoc",
            properties={
                "title": metadata.get('title', '') or os.path.basename(extracted_doc.file_path),
                "doc_type": content.get('doc_type', 'General Documentation'),
                "version": "1.0",  # Default version
                "file_path": extracted_doc.file_path,
                "page_count": metadata.get('page_count', 0),
                "word_count": content.get('word_count', 0),
                "author": metadata.get('author', ''),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            },
            relationships=[]
        )
        nodes.append(spec_node)
        
        # Create document-level vector embedding
        doc_text = f"Document: {metadata.get('title', '')} " + \
                   f"Type: {content.get('doc_type', '')} " + \
                   f"Content: {content.get('full_text', '')[:500]}..."  # First 500 chars
        
        doc_embedding = await self.generate_embedding(doc_text)
        if doc_embedding:
            vectors.append(VectorRecord(
                id=spec_uuid,
                vector=doc_embedding,
                payload={
                    "type": "SpecDoc",
                    "title": metadata.get('title', ''),
                    "doc_type": content.get('doc_type', ''),
                    "text": doc_text,
                    "file_path": extracted_doc.file_path
                }
            ))
        
        # Create section embeddings
        for section in content.get('sections', []):
            section_uuid = self.generate_uuid(f"section:{spec_uuid}:{section.get('title', 'unknown')}")
            section_text = f"Section: {section.get('title', '')} " + \
                          f"Content: {section.get('content', '')}"
            
            section_embedding = await self.generate_embedding(section_text)
            if section_embedding:
                vectors.append(VectorRecord(
                    id=section_uuid,
                    vector=section_embedding,
                    payload={
                        "type": "Section",
                        "title": section.get('title', ''),
                        "parent_doc": metadata.get('title', ''),
                        "text": section_text,
                        "file_path": extracted_doc.file_path
                    }
                ))
        
        # Transform Q&A pairs
        for qa_data in content.get('qa_pairs', []):
            qa_uuid = self.generate_uuid(f"qa:{hashlib.md5(qa_data.get('question', '').encode()).hexdigest()}")
            qa_node = TransformedNode(
                uuid=qa_uuid,
                label="QuestionAnswer",
                properties={
                    "question": qa_data.get('question', ''),
                    "answer": qa_data.get('answer', ''),
                    "embedding_id": qa_uuid,
                    "confidence": qa_data.get('confidence', 0.7),
                    "source_line": qa_data.get('source_line', 0),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                },
                relationships=[]
            )
            nodes.append(qa_node)
            
            # Create relationship to source document
            relationships.append(TransformedRelationship(
                source_uuid=qa_uuid,
                target_uuid=spec_uuid,
                type="DERIVED_FROM",
                properties={
                    "created_at": datetime.now().isoformat(),
                    "page_reference": qa_data.get('source_line', 0)
                }
            ))
            
            # Create Q&A vector embedding
            qa_text = f"Question: {qa_data.get('question', '')} Answer: {qa_data.get('answer', '')}"
            qa_embedding = await self.generate_embedding(qa_text)
            if qa_embedding:
                vectors.append(VectorRecord(
                    id=qa_uuid,
                    vector=qa_embedding,
                    payload={
                        "type": "QuestionAnswer",
                        "question": qa_data.get('question', ''),
                        "answer": qa_data.get('answer', ''),
                        "confidence": qa_data.get('confidence', 0.7),
                        "text": qa_text,
                        "file_path": extracted_doc.file_path
                    }
                ))
        
        return nodes, relationships, vectors
    
    def chunk_text(self, text: str, max_chunk_size: int = None) -> List[str]:
        """Split text into chunks for embedding"""
        max_size = max_chunk_size or self.max_chunk_size
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > max_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks
    
    async def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts in batch"""
        embeddings = []
        
        for text in texts:
            embedding = await self.generate_embedding(text)
            embeddings.append(embedding)
            
            # Small delay to respect rate limits
            await asyncio.sleep(0.1)
        
        return embeddings

def main():
    """Test the ETL transformer"""
    import sys
    from document_parser import DocumentParser
    
    if len(sys.argv) < 2:
        print("Usage: python etl_transformer.py <file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    async def test_transform():
        # Parse document first
        parser = DocumentParser()
        extracted_doc = parser.parse_document(file_path)
        
        if not extracted_doc:
            print(f"Failed to parse {file_path}")
            return
        
        # Transform document
        transformer = ETLTransformer()
        result = await transformer.transform_document(extracted_doc)
        
        print(f"Transformation Results for {file_path}:")
        print(f"Nodes: {len(result.nodes)}")
        print(f"Relationships: {len(result.relationships)}")
        print(f"Vectors: {len(result.vectors)}")
        print(f"Errors: {len(result.errors)}")
        
        if result.errors:
            print("Errors:")
            for error in result.errors:
                print(f"  - {error}")
        
        # Print some sample data
        if result.nodes:
            print("\nSample Node:")
            print(f"  UUID: {result.nodes[0].uuid}")
            print(f"  Label: {result.nodes[0].label}")
            print(f"  Properties: {list(result.nodes[0].properties.keys())}")
        
        if result.vectors:
            print("\nSample Vector:")
            print(f"  ID: {result.vectors[0].id}")
            print(f"  Dimensions: {len(result.vectors[0].vector)}")
            print(f"  Payload: {list(result.vectors[0].payload.keys())}")
    
    asyncio.run(test_transform())

if __name__ == "__main__":
    main() 