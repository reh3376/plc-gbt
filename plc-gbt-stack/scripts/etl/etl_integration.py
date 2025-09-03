#!/usr/bin/env python3
"""
ETL Integration Script
Phase 3: Basic ETL Integration
Version: 1.0.0

This script provides the basic integration between:
- PLC file parsing (using plc-format-converter)
- Neo4j knowledge graph storage
- Qdrant vector embeddings
"""

import os
import sys
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

import structlog
from embedding_generator import EmbeddingGenerator
from neo4j import GraphDatabase

# Import new components
from pdf_processor import PDFProcessor
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

# Import our workers
from workers.document_parser import DocumentParser
from workers.etl_loader import ETLLoader
from workers.etl_transformer import ETLTransformer

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


class ETLIntegration:
    """Coordinates ETL processing between components."""

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        openai_api_key: Optional[str] = None
    ):
        """
        Initialize ETL integration.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            qdrant_host: Qdrant host
            qdrant_port: Qdrant port
            openai_api_key: OpenAI API key for embeddings
        """
        # Initialize connections
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        self.qdrant_client = QdrantClient(
            host=qdrant_host,
            port=qdrant_port
        )

        self.openai_api_key = openai_api_key

        # Initialize workers
        self.parser = DocumentParser()
        self.transformer = ETLTransformer()
        self.loader = ETLLoader(
            neo4j_driver=self.neo4j_driver,
            qdrant_client=self.qdrant_client
        )

        # Initialize new components
        self.pdf_processor = PDFProcessor()
        self.embedding_generator = EmbeddingGenerator(api_key=openai_api_key)

    def close(self):
        """Close connections."""
        if self.neo4j_driver:
            self.neo4j_driver.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def process_l5x_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Process a single L5X file through the ETL pipeline.

        Args:
            file_path: Path to L5X file

        Returns:
            Processing results
        """
        logger.info(f"Processing L5X file: {file_path}")

        results = {
            'file': str(file_path),
            'status': 'started',
            'parsed_components': 0,
            'neo4j_nodes': 0,
            'neo4j_relationships': 0,
            'embeddings_created': 0,
            'errors': []
        }

        try:
            # Step 1: Parse the L5X file
            logger.info("Step 1: Parsing L5X file")
            parsed_data = self.parser.parse_l5x(file_path)

            if not parsed_data:
                raise ValueError("Failed to parse L5X file")

            results['parsed_components'] = len(parsed_data.get('components', []))

            # Step 2: Transform the data
            logger.info("Step 2: Transforming data")
            transformed_data = self.transformer.transform_plc_data(parsed_data)

            # Step 3: Load to Neo4j
            logger.info("Step 3: Loading to Neo4j")
            neo4j_results = self._load_to_neo4j(transformed_data)
            results['neo4j_nodes'] = neo4j_results['nodes_created']
            results['neo4j_relationships'] = neo4j_results['relationships_created']

            # Step 4: Generate and store embeddings
            logger.info("Step 4: Generating embeddings")
            embedding_results = self._generate_embeddings(transformed_data)
            results['embeddings_created'] = embedding_results['embeddings_created']

            results['status'] = 'completed'

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))

        return results

    def _load_to_neo4j(self, data: Dict[str, Any]) -> Dict[str, int]:
        """
        Load transformed data to Neo4j.

        Args:
            data: Transformed data

        Returns:
            Load statistics
        """
        stats = {
            'nodes_created': 0,
            'relationships_created': 0
        }

        with self.neo4j_driver.session() as session:
            # Create PLCProgram node
            program_data = data.get('program', {})
            if program_data:
                session.run("""
                    MERGE (p:PLCProgram {id: $id})
                    SET p += $properties
                    RETURN p
                """,
                id=program_data['id'],
                properties=program_data
                )
                stats['nodes_created'] += 1

            # Create Routine nodes
            for routine in data.get('routines', []):
                session.run("""
                    MERGE (r:Routine {id: $id})
                    SET r += $properties
                    WITH r
                    MATCH (p:PLCProgram {id: $program_id})
                    MERGE (p)-[:CONTAINS]->(r)
                    MERGE (r)-[:IN_PROGRAM]->(p)
                    RETURN r
                """,
                id=routine['id'],
                properties=routine,
                program_id=program_data['id']
                )
                stats['nodes_created'] += 1
                stats['relationships_created'] += 2

            # Create AOI nodes
            for aoi in data.get('aois', []):
                session.run("""
                    MERGE (a:AOI {id: $id})
                    SET a += $properties
                    WITH a
                    MATCH (p:PLCProgram {id: $program_id})
                    MERGE (p)-[:CONTAINS]->(a)
                    RETURN a
                """,
                id=aoi['id'],
                properties=aoi,
                program_id=program_data['id']
                )
                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

            # Create UDT nodes
            for udt in data.get('udts', []):
                session.run("""
                    MERGE (u:UDT {id: $id})
                    SET u += $properties
                    WITH u
                    MATCH (p:PLCProgram {id: $program_id})
                    MERGE (p)-[:CONTAINS]->(u)
                    RETURN u
                """,
                id=udt['id'],
                properties=udt,
                program_id=program_data['id']
                )
                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

            # Create Tag nodes
            for tag in data.get('tags', []):
                session.run("""
                    MERGE (t:Tag {id: $id})
                    SET t += $properties
                    WITH t
                    MATCH (p:PLCProgram {id: $program_id})
                    MERGE (p)-[:HAS_TAG]->(t)
                    RETURN t
                """,
                id=tag['id'],
                properties=tag,
                program_id=program_data['id']
                )
                stats['nodes_created'] += 1
                stats['relationships_created'] += 1

        logger.info(
            "Neo4j load complete",
            nodes=stats['nodes_created'],
            relationships=stats['relationships_created']
        )

        return stats

    def _generate_embeddings(self, data: Dict[str, Any]) -> Dict[str, int]:
        """
        Generate embeddings for components.

        Args:
            data: Transformed data

        Returns:
            Embedding statistics
        """
        stats = {
            'embeddings_created': 0,
            'errors': []
        }

        # For now, we'll use random embeddings
        # In production, this would call OpenAI API

        points = []

        # Generate embeddings for routines
        for routine in data.get('routines', []):
            embedding = self._create_embedding(
                f"{routine['name']} {routine.get('description', '')}"
            )

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'component_type': 'Routine',
                    'component_id': routine['id'],
                    'name': routine['name'],
                    'routine_type': routine.get('type', 'Unknown'),
                    'program_name': data['program']['name'],
                    'description': routine.get('description', ''),
                    'source_file': data['program'].get('source_file', '')
                }
            )
            points.append(point)

        # Generate embeddings for AOIs
        for aoi in data.get('aois', []):
            embedding = self._create_embedding(
                f"{aoi['name']} {aoi.get('description', '')}"
            )

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'component_type': 'AOI',
                    'component_id': aoi['id'],
                    'name': aoi['name'],
                    'revision': aoi.get('revision', ''),
                    'description': aoi.get('description', ''),
                    'source_file': data['program'].get('source_file', '')
                }
            )
            points.append(point)

        # Generate embeddings for UDTs
        for udt in data.get('udts', []):
            embedding = self._create_embedding(
                f"{udt['name']} {udt.get('description', '')}"
            )

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    'component_type': 'UDT',
                    'component_id': udt['id'],
                    'name': udt['name'],
                    'size': udt.get('size', 0),
                    'description': udt.get('description', ''),
                    'source_file': data['program'].get('source_file', '')
                }
            )
            points.append(point)

        # Insert embeddings into Qdrant
        if points:
            try:
                self.qdrant_client.upsert(
                    collection_name='plc_embeddings',
                    points=points
                )
                stats['embeddings_created'] = len(points)
                logger.info(f"Created {len(points)} embeddings")
            except Exception as e:
                logger.error(f"Failed to insert embeddings: {str(e)}")
                stats['errors'].append(str(e))

        return stats

    def process_pdf_file(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process a PDF file through the ETL pipeline.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Processing results
        """
        logger.info(f"Processing PDF file: {pdf_path}")

        results = {
            'file': str(pdf_path),
            'status': 'started',
            'chunks_processed': 0,
            'qa_pairs_processed': 0,
            'neo4j_nodes': 0,
            'embeddings_created': 0,
            'errors': []
        }

        try:
            # Step 1: Process PDF
            logger.info("Step 1: Processing PDF")
            pdf_data = self.pdf_processor.process_pdf(pdf_path)

            if pdf_data['errors']:
                results['errors'].extend(pdf_data['errors'])

            # Step 2: Store document in Neo4j
            logger.info("Step 2: Creating SpecDoc node")
            spec_doc_id = self._create_spec_doc(pdf_data)
            results['neo4j_nodes'] += 1

            # Step 3: Process chunks
            logger.info("Step 3: Processing document chunks")
            chunk_results = self._process_document_chunks(pdf_data['chunks'], spec_doc_id)
            results['chunks_processed'] = chunk_results['count']
            results['embeddings_created'] += chunk_results['embeddings_created']

            # Step 4: Process Q&A pairs
            logger.info("Step 4: Processing Q&A pairs")
            qa_results = self._process_qa_pairs(pdf_data['qa_pairs'], spec_doc_id)
            results['qa_pairs_processed'] = qa_results['count']
            results['neo4j_nodes'] += qa_results['nodes_created']
            results['embeddings_created'] += qa_results['embeddings_created']

            # Step 5: Extract and link PLC entities
            logger.info("Step 5: Extracting PLC entities")
            entity_results = self._extract_and_link_entities(pdf_data, spec_doc_id)
            results['neo4j_nodes'] += entity_results['relationships_created']

            results['status'] = 'completed'

        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            results['status'] = 'failed'
            results['errors'].append(str(e))

        return results

    def _create_spec_doc(self, pdf_data: Dict[str, Any]) -> str:
        """Create SpecDoc node in Neo4j."""
        spec_doc_id = str(uuid.uuid4())

        with self.neo4j_driver.session() as session:
            session.run("""
                CREATE (s:SpecDoc {
                    id: $id,
                    title: $title,
                    doc_type: 'PDF',
                    version: $version,
                    file_path: $file_path,
                    page_count: $page_count,
                    file_hash: $file_hash,
                    processed_date: datetime($processed_date)
                })
                RETURN s
            """,
            id=spec_doc_id,
            title=pdf_data['metadata'].get('title', pdf_data['file_name']),
            version=pdf_data['metadata'].get('version', '1.0'),
            file_path=pdf_data['file_path'],
            page_count=pdf_data['metadata'].get('page_count', 0),
            file_hash=pdf_data['file_hash'],
            processed_date=pdf_data['processed_date']
            )

        return spec_doc_id

    def _process_document_chunks(self, chunks: List[Dict[str, Any]], spec_doc_id: str) -> Dict[str, int]:
        """Process and store document chunks."""
        stats = {
            'count': 0,
            'embeddings_created': 0
        }

        points = []

        for chunk in chunks:
            # Generate embedding
            embedded_chunk = self.embedding_generator.embed_document_chunk(chunk)

            # Create Qdrant point
            point = PointStruct(
                id=chunk['id'],
                vector=embedded_chunk['embedding'],
                payload={
                    'text': chunk['text'],
                    'chunk_index': chunk['chunk_index'],
                    'spec_doc_id': spec_doc_id,
                    'char_count': chunk['char_count'],
                    'word_count': chunk['word_count'],
                    'metadata': chunk['metadata']
                }
            )
            points.append(point)
            stats['count'] += 1

        # Batch insert to Qdrant
        if points:
            self.qdrant_client.upsert(
                collection_name='document_chunks',
                points=points
            )
            stats['embeddings_created'] = len(points)

        return stats

    def _process_qa_pairs(self, qa_pairs: List[Dict[str, Any]], spec_doc_id: str) -> Dict[str, int]:
        """Process and store Q&A pairs."""
        stats = {
            'count': 0,
            'nodes_created': 0,
            'embeddings_created': 0
        }

        points = []

        with self.neo4j_driver.session() as session:
            for qa in qa_pairs:
                # Generate embedding
                embedded_qa = self.embedding_generator.embed_qa_pair(qa)

                # Create QuestionAnswer node
                session.run("""
                    CREATE (q:QuestionAnswer {
                        id: $id,
                        question: $question,
                        answer: $answer,
                        embedding_id: $embedding_id,
                        confidence: $confidence,
                        source_page: $source_page,
                        extraction_method: $extraction_method
                    })
                    WITH q
                    MATCH (s:SpecDoc {id: $spec_doc_id})
                    CREATE (q)-[:DERIVED_FROM]->(s)
                    RETURN q
                """,
                id=qa['id'],
                question=qa['question'],
                answer=qa['answer'],
                embedding_id=f"emb_{qa['id']}",
                confidence=qa['confidence'],
                source_page=qa.get('source_page', 0),
                extraction_method=qa.get('extraction_method', 'unknown'),
                spec_doc_id=spec_doc_id
                )

                stats['nodes_created'] += 1

                # Create Qdrant point
                point = PointStruct(
                    id=qa['id'],
                    vector=embedded_qa['embedding'],
                    payload={
                        'question': qa['question'],
                        'answer': qa['answer'],
                        'spec_doc_id': spec_doc_id,
                        'confidence': qa['confidence'],
                        'extraction_method': qa['extraction_method']
                    }
                )
                points.append(point)
                stats['count'] += 1

        # Batch insert to Qdrant
        if points:
            self.qdrant_client.upsert(
                collection_name='qa_embeddings',
                points=points
            )
            stats['embeddings_created'] = len(points)

        return stats

    def _extract_and_link_entities(self, pdf_data: Dict[str, Any], spec_doc_id: str) -> Dict[str, int]:
        """Extract PLC entities from PDF and create relationships."""
        stats = {
            'entities_found': 0,
            'relationships_created': 0
        }

        # Extract entities from all chunks
        all_entities = {
            'aoi_names': set(),
            'udt_names': set(),
            'tag_names': set(),
            'routine_names': set(),
            'device_names': set()
        }

        for chunk in pdf_data['chunks']:
            entities = self.pdf_processor.extract_plc_entities(chunk['text'])
            for entity_type, values in entities.items():
                all_entities[entity_type].update(values)

        # Create relationships in Neo4j
        with self.neo4j_driver.session() as session:
            # Link AOIs
            for aoi_name in all_entities['aoi_names']:
                result = session.run("""
                    MATCH (s:SpecDoc {id: $spec_doc_id})
                    MATCH (a:AOI {name: $aoi_name})
                    MERGE (s)-[:COVERS]->(a)
                    RETURN a
                """, spec_doc_id=spec_doc_id, aoi_name=aoi_name)

                if result.single():
                    stats['relationships_created'] += 1

            # Link UDTs
            for udt_name in all_entities['udt_names']:
                result = session.run("""
                    MATCH (s:SpecDoc {id: $spec_doc_id})
                    MATCH (u:UDT {name: $udt_name})
                    MERGE (s)-[:COVERS]->(u)
                    RETURN u
                """, spec_doc_id=spec_doc_id, udt_name=udt_name)

                if result.single():
                    stats['relationships_created'] += 1

        stats['entities_found'] = sum(len(v) for v in all_entities.values())

        return stats

    def _create_embedding(self, text: str) -> List[float]:
        """
        Create embedding for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        return self.embedding_generator.generate_embedding(text)

    def process_directory(
        self,
        directory: Path,
        file_patterns: List[str] = None,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """
        Process all files in a directory.

        Args:
            directory: Directory to process
            file_patterns: File patterns to match (e.g., ['*.pdf', '*.L5X'])
            max_workers: Number of parallel workers

        Returns:
            Processing summary
        """
        if file_patterns is None:
            file_patterns = ['*.pdf', '*.L5X', '*.ACD']

        results = {
            'directory': str(directory),
            'files_processed': 0,
            'files_succeeded': 0,
            'files_failed': 0,
            'total_time': 0,
            'file_results': []
        }

        # Find all matching files
        files_to_process = []
        for pattern in file_patterns:
            files_to_process.extend(directory.glob(pattern))

        logger.info(f"Found {len(files_to_process)} files to process")

        start_time = time.time()

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all files for processing
            future_to_file = {}

            for file_path in files_to_process:
                if file_path.suffix.lower() == '.pdf':
                    future = executor.submit(self.process_pdf_file, file_path)
                elif file_path.suffix.upper() == '.L5X':
                    future = executor.submit(self.process_l5x_file, file_path)
                else:
                    continue

                future_to_file[future] = file_path

            # Collect results
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]

                try:
                    result = future.result()
                    results['file_results'].append(result)
                    results['files_processed'] += 1

                    if result['status'] == 'completed':
                        results['files_succeeded'] += 1
                    else:
                        results['files_failed'] += 1

                    logger.info(
                        f"Processed {file_path.name}: {result['status']}",
                        chunks=result.get('chunks_processed', 0),
                        embeddings=result.get('embeddings_created', 0)
                    )

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {str(e)}")
                    results['files_failed'] += 1
                    results['file_results'].append({
                        'file': str(file_path),
                        'status': 'error',
                        'error': str(e)
                    })

        results['total_time'] = time.time() - start_time

        return results

    def test_integration(self) -> Dict[str, Any]:
        """
        Test the ETL integration with sample data.

        Returns:
            Test results
        """
        logger.info("Testing ETL integration")

        results = {
            'neo4j_connected': False,
            'qdrant_connected': False,
            'etl_test': False,
            'issues': []
        }

        # Test Neo4j connection
        try:
            self.neo4j_driver.verify_connectivity()
            results['neo4j_connected'] = True
        except Exception as e:
            results['issues'].append(f"Neo4j connection failed: {str(e)}")

        # Test Qdrant connection
        try:
            self.qdrant_client.get_collections()
            results['qdrant_connected'] = True
        except Exception as e:
            results['issues'].append(f"Qdrant connection failed: {str(e)}")

        # Test basic ETL flow with mock data
        try:
            test_data = {
                'program': {
                    'id': 'test_program_001',
                    'name': 'TestProgram',
                    'processor_type': 'Test',
                    'source_file': 'test.L5X'
                },
                'routines': [
                    {
                        'id': 'test_routine_001',
                        'name': 'TestRoutine',
                        'type': 'RLL',
                        'description': 'Test routine'
                    }
                ]
            }

            # Load to Neo4j
            neo4j_stats = self._load_to_neo4j(test_data)

            # Generate embeddings
            embedding_stats = self._generate_embeddings(test_data)

            if neo4j_stats['nodes_created'] > 0 and embedding_stats['embeddings_created'] > 0:
                results['etl_test'] = True

        except Exception as e:
            results['issues'].append(f"ETL test failed: {str(e)}")

        return results


def main():
    """Main execution function."""
    # Configuration
    neo4j_uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password = os.getenv("NEO4J_PASSWORD", "your-password-here")
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    openai_api_key = os.getenv("OPENAI_API_KEY", None)

    # Test file path
    test_file = Path(__file__).parent.parent.parent / "plc-format-converter" / "tests" / "test_data" / "sample_controller.L5X"

    logger.info("Starting ETL integration")

    try:
        with ETLIntegration(
            neo4j_uri=neo4j_uri,
            neo4j_user=neo4j_user,
            neo4j_password=neo4j_password,
            qdrant_host=qdrant_host,
            qdrant_port=qdrant_port,
            openai_api_key=openai_api_key
        ) as etl:
            # Test integration
            logger.info("Testing integration...")
            test_results = etl.test_integration()

            print("\n" + "="*60)
            print("ETL INTEGRATION TEST RESULTS")
            print("="*60)
            print("\nConnection Status:")
            print(f"  - Neo4j: {'✅' if test_results['neo4j_connected'] else '❌'}")
            print(f"  - Qdrant: {'✅' if test_results['qdrant_connected'] else '❌'}")
            print(f"  - ETL Test: {'✅' if test_results['etl_test'] else '❌'}")

            if test_results['issues']:
                print("\n⚠️  Issues:")
                for issue in test_results['issues']:
                    print(f"  - {issue}")

            # Process test file if it exists
            if test_file.exists():
                print(f"\nProcessing test L5X file: {test_file}")
                process_results = etl.process_l5x_file(test_file)

                print("\nL5X Processing Results:")
                print(f"  - Status: {process_results['status']}")
                print(f"  - Components parsed: {process_results['parsed_components']}")
                print(f"  - Neo4j nodes created: {process_results['neo4j_nodes']}")
                print(f"  - Neo4j relationships: {process_results['neo4j_relationships']}")
                print(f"  - Embeddings created: {process_results['embeddings_created']}")

                if process_results['errors']:
                    print("\n❌ Errors:")
                    for error in process_results['errors']:
                        print(f"  - {error}")
                else:
                    print("\n✅ L5X processing successful!")
            else:
                print(f"\n⚠️  Test L5X file not found: {test_file}")

            # Test PDF processing
            test_pdf = Path("test_document.pdf")
            if test_pdf.exists():
                print(f"\nProcessing test PDF: {test_pdf}")
                pdf_results = etl.process_pdf_file(test_pdf)

                print("\nPDF Processing Results:")
                print(f"  - Status: {pdf_results['status']}")
                print(f"  - Chunks processed: {pdf_results['chunks_processed']}")
                print(f"  - Q&A pairs: {pdf_results['qa_pairs_processed']}")
                print(f"  - Neo4j nodes created: {pdf_results['neo4j_nodes']}")
                print(f"  - Embeddings created: {pdf_results['embeddings_created']}")

                if pdf_results['errors']:
                    print("\n❌ Errors:")
                    for error in pdf_results['errors']:
                        print(f"  - {error}")
                else:
                    print("\n✅ PDF processing successful!")
            else:
                print(f"\n⚠️  Test PDF not found: {test_pdf}")

            # Test directory processing
            incoming_dir = Path(__file__).parent.parent.parent / "incoming"
            if incoming_dir.exists() and any(incoming_dir.iterdir()):
                print(f"\nProcessing incoming directory: {incoming_dir}")
                dir_results = etl.process_directory(incoming_dir)

                print("\nDirectory Processing Results:")
                print(f"  - Files processed: {dir_results['files_processed']}")
                print(f"  - Succeeded: {dir_results['files_succeeded']}")
                print(f"  - Failed: {dir_results['files_failed']}")
                print(f"  - Total time: {dir_results['total_time']:.2f}s")

                if dir_results['files_processed'] == 0:
                    print("\n⚠️  No supported files found in incoming directory")

            # Show usage statistics
            print("\n" + "="*60)
            print("EMBEDDING USAGE STATISTICS")
            print("="*60)

            usage_stats = etl.embedding_generator.get_usage_stats()
            print("\nOpenAI API Usage:")
            print(f"  - API calls: {usage_stats['api_calls']}")
            print(f"  - Tokens used: {usage_stats['tokens_used']}")
            print(f"  - Estimated cost: ${usage_stats['estimated_cost']:.4f}")
            print(f"  - Cached embeddings: {usage_stats['cache_size']}")

    except Exception as e:
        logger.error("ETL integration failed", error=str(e))
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
