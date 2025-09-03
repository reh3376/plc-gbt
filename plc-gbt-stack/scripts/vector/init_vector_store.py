#!/usr/bin/env python3
"""
Qdrant Vector Store Initialization Script
Phase 3: Vector Store Setup
Version: 1.0.0

This script initializes the Qdrant vector database with collections
for storing PLC component embeddings.
"""

import os
import sys
import uuid
from typing import Any, Dict, Optional

import numpy as np
import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    UpdateStatus,
    VectorParams,
)

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


class QdrantInitializer:
    """Handles Qdrant vector store initialization and configuration."""

    # Collection configuration
    COLLECTIONS = {
        'plc_embeddings': {
            'vector_size': 3072,  # OpenAI text-embedding-3-large
            'distance': Distance.COSINE,
            'description': 'PLC component embeddings (routines, AOIs, UDTs, etc.)'
        },
        'document_chunks': {
            'vector_size': 3072,
            'distance': Distance.COSINE,
            'description': 'Document chunk embeddings from PDFs and specifications'
        },
        'qa_embeddings': {
            'vector_size': 3072,
            'distance': Distance.COSINE,
            'description': 'Question-answer pair embeddings'
        }
    }

    def __init__(self, host: str = "localhost", port: int = 6333, api_key: Optional[str] = None):
        """
        Initialize Qdrant client.

        Args:
            host: Qdrant server host
            port: Qdrant server port
            api_key: Optional API key for authentication
        """
        self.host = host
        self.port = port
        self.client = QdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            timeout=30.0
        )

    def create_collections(self) -> Dict[str, Any]:
        """
        Create all required collections.

        Returns:
            Creation results
        """
        results = {
            'created': [],
            'existing': [],
            'failed': [],
            'errors': []
        }

        for collection_name, config in self.COLLECTIONS.items():
            try:
                # Check if collection exists
                collections = self.client.get_collections().collections
                exists = any(c.name == collection_name for c in collections)

                if exists:
                    logger.info(f"Collection already exists: {collection_name}")
                    results['existing'].append(collection_name)
                else:
                    # Create collection
                    logger.info(f"Creating collection: {collection_name}")

                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=VectorParams(
                            size=config['vector_size'],
                            distance=config['distance']
                        )
                    )

                    # Create payload indexes for common filters
                    self._create_payload_indexes(collection_name)

                    results['created'].append(collection_name)
                    logger.info(
                        "Collection created successfully",
                        collection=collection_name,
                        vector_size=config['vector_size'],
                        distance=config['distance'].value
                    )

            except Exception as e:
                error_msg = f"Failed to create collection {collection_name}: {str(e)}"
                logger.error(error_msg)
                results['failed'].append(collection_name)
                results['errors'].append(error_msg)

        return results

    def _create_payload_indexes(self, collection_name: str):
        """
        Create payload indexes for efficient filtering.

        Args:
            collection_name: Name of the collection
        """
        # Common indexes for all collections
        common_indexes = [
            'component_type',  # PLCProgram, Routine, AOI, etc.
            'component_id',    # Unique ID from Neo4j
            'source_file',     # Original file path
            'created_date'     # Creation timestamp
        ]

        # Collection-specific indexes
        specific_indexes = {
            'plc_embeddings': ['program_name', 'routine_type', 'language'],
            'document_chunks': ['document_id', 'page_number', 'chunk_index'],
            'qa_embeddings': ['question_id', 'confidence_score', 'source_doc']
        }

        indexes_to_create = common_indexes + specific_indexes.get(collection_name, [])

        for field_name in indexes_to_create:
            try:
                self.client.create_payload_index(
                    collection_name=collection_name,
                    field_name=field_name,
                    field_schema="keyword"
                )
                logger.debug(f"Created index: {field_name} for {collection_name}")
            except Exception as e:
                logger.warning(f"Could not create index {field_name}: {str(e)}")

    def insert_sample_embeddings(self) -> Dict[str, int]:
        """
        Insert sample embeddings for testing.

        Returns:
            Count of inserted points by collection
        """
        counts = {}

        # Sample data based on our test L5X file
        sample_data = {
            'plc_embeddings': [
                {
                    'id': str(uuid.uuid4()),
                    'vector': np.random.rand(3072).tolist(),  # Random vector for testing
                    'payload': {
                        'component_type': 'Routine',
                        'component_id': 'routine_001',
                        'name': 'MainRoutine',
                        'routine_type': 'RLL',
                        'program_name': 'TestController',
                        'description': 'Main program routine',
                        'source_file': 'sample_controller.L5X'
                    }
                },
                {
                    'id': str(uuid.uuid4()),
                    'vector': np.random.rand(3072).tolist(),
                    'payload': {
                        'component_type': 'AOI',
                        'component_id': 'aoi_001',
                        'name': 'MotorControl_AOI',
                        'revision': '1.0',
                        'description': 'Motor control Add-On Instruction',
                        'source_file': 'sample_controller.L5X'
                    }
                },
                {
                    'id': str(uuid.uuid4()),
                    'vector': np.random.rand(3072).tolist(),
                    'payload': {
                        'component_type': 'UDT',
                        'component_id': 'udt_001',
                        'name': 'MotorData_UDT',
                        'size': 20,
                        'description': 'Motor data structure',
                        'source_file': 'sample_controller.L5X'
                    }
                }
            ]
        }

        for collection_name, points_data in sample_data.items():
            try:
                points = [
                    PointStruct(
                        id=point['id'],
                        vector=point['vector'],
                        payload=point['payload']
                    )
                    for point in points_data
                ]

                operation_info = self.client.upsert(
                    collection_name=collection_name,
                    points=points
                )

                if operation_info.status == UpdateStatus.COMPLETED:
                    counts[collection_name] = len(points)
                    logger.info(
                        "Inserted sample embeddings",
                        collection=collection_name,
                        count=len(points)
                    )
                else:
                    logger.warning(
                        "Insertion may have failed",
                        collection=collection_name,
                        status=operation_info.status
                    )

            except Exception as e:
                logger.error(f"Failed to insert sample data: {str(e)}")
                counts[collection_name] = 0

        return counts

    def test_similarity_search(self) -> Dict[str, Any]:
        """
        Test similarity search functionality.

        Returns:
            Search test results
        """
        logger.info("Testing similarity search")

        results = {}

        try:
            # Generate a random query vector
            query_vector = np.random.rand(3072).tolist()

            # Search in plc_embeddings collection
            search_result = self.client.search(
                collection_name='plc_embeddings',
                query_vector=query_vector,
                limit=5
            )

            results['plc_embeddings'] = {
                'success': True,
                'results_count': len(search_result),
                'top_results': [
                    {
                        'id': hit.id,
                        'score': hit.score,
                        'component_type': hit.payload.get('component_type'),
                        'name': hit.payload.get('name')
                    }
                    for hit in search_result
                ]
            }

            logger.info(
                "Similarity search successful",
                collection='plc_embeddings',
                results=len(search_result)
            )

        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            results['plc_embeddings'] = {
                'success': False,
                'error': str(e)
            }

        return results

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about all collections.

        Returns:
            Collection information
        """
        info = {}

        try:
            collections = self.client.get_collections().collections

            for collection in collections:
                collection_info = self.client.get_collection(collection.name)

                info[collection.name] = {
                    'vectors_count': collection_info.vectors_count,
                    'points_count': collection_info.points_count,
                    'indexed_vectors_count': collection_info.indexed_vectors_count,
                    'status': collection_info.status,
                    'config': {
                        'size': collection_info.config.params.vectors.size,
                        'distance': collection_info.config.params.vectors.distance
                    }
                }

        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")

        return info

    def validate_setup(self) -> Dict[str, Any]:
        """
        Validate the vector store setup.

        Returns:
            Validation results
        """
        validation = {
            'collections_exist': False,
            'search_works': False,
            'indexes_created': False,
            'issues': []
        }

        # Check collections exist
        try:
            collections = self.client.get_collections().collections
            expected_collections = set(self.COLLECTIONS.keys())
            actual_collections = {c.name for c in collections}

            validation['collections_exist'] = expected_collections.issubset(actual_collections)

            if not validation['collections_exist']:
                missing = expected_collections - actual_collections
                validation['issues'].append(f"Missing collections: {missing}")

        except Exception as e:
            validation['issues'].append(f"Collection check failed: {str(e)}")

        # Test search functionality
        try:
            search_results = self.test_similarity_search()
            validation['search_works'] = any(
                r.get('success', False)
                for r in search_results.values()
            )
        except Exception as e:
            validation['issues'].append(f"Search test failed: {str(e)}")

        return validation


def main():
    """Main execution function."""
    # Configuration
    qdrant_host = os.getenv("QDRANT_HOST", "localhost")
    qdrant_port = int(os.getenv("QDRANT_PORT", "6333"))
    qdrant_api_key = os.getenv("QDRANT_API_KEY", None)

    logger.info(
        "Starting Qdrant vector store initialization",
        host=qdrant_host,
        port=qdrant_port
    )

    try:
        # Initialize Qdrant
        initializer = QdrantInitializer(
            host=qdrant_host,
            port=qdrant_port,
            api_key=qdrant_api_key
        )

        # Create collections
        logger.info("Creating collections...")
        creation_results = initializer.create_collections()

        # Insert sample data
        logger.info("Inserting sample embeddings...")
        sample_counts = initializer.insert_sample_embeddings()

        # Test similarity search
        logger.info("Testing similarity search...")
        search_results = initializer.test_similarity_search()

        # Get collection info
        logger.info("Getting collection information...")
        collection_info = initializer.get_collection_info()

        # Validate setup
        logger.info("Validating setup...")
        validation = initializer.validate_setup()

        # Print summary
        print("\n" + "="*60)
        print("QDRANT VECTOR STORE INITIALIZATION COMPLETE")
        print("="*60)

        print("\nCollections:")
        print(f"  - Created: {creation_results['created']}")
        print(f"  - Existing: {creation_results['existing']}")
        print(f"  - Failed: {creation_results['failed']}")

        print("\nCollection Statistics:")
        for name, info in collection_info.items():
            print(f"  {name}:")
            print(f"    - Vectors: {info['vectors_count']}")
            print(f"    - Points: {info['points_count']}")
            print(f"    - Status: {info['status']}")

        print("\nSample Data Inserted:")
        for collection, count in sample_counts.items():
            print(f"  - {collection}: {count} points")

        print("\nValidation Results:")
        print(f"  - Collections exist: {'✅' if validation['collections_exist'] else '❌'}")
        print(f"  - Search works: {'✅' if validation['search_works'] else '❌'}")

        if validation['issues']:
            print("\n⚠️  Issues detected:")
            for issue in validation['issues']:
                print(f"    - {issue}")
        else:
            print("\n✅ Qdrant vector store initialization successful!")

        # Print search test results
        if search_results.get('plc_embeddings', {}).get('success'):
            print("\n🔍 Sample search results:")
            for result in search_results['plc_embeddings']['top_results'][:3]:
                print(f"    - {result['name']} ({result['component_type']}) - Score: {result['score']:.3f}")

    except Exception as e:
        logger.error("Vector store initialization failed", error=str(e))
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
