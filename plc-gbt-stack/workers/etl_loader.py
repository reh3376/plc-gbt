#!/usr/bin/env python3
"""
ETL Loader Module
Created: January 1, 2025
Purpose: Load transformed data into Neo4j and Qdrant vector database
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List

# Neo4j
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

# Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models
    from qdrant_client.models import Distance, PointStruct, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available - vector loading disabled")

# ETL data structures
from etl_transformer import (
    TransformationResult,
    TransformedNode,
    TransformedRelationship,
    VectorRecord,
)


class LoadResult:
    """Container for load operation results"""
    def __init__(self):
        self.nodes_loaded = 0
        self.relationships_loaded = 0
        self.vectors_loaded = 0
        self.errors = []
        self.warnings = []
        self.metadata = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes_loaded": self.nodes_loaded,
            "relationships_loaded": self.relationships_loaded,
            "vectors_loaded": self.vectors_loaded,
            "errors": self.errors,
            "warnings": self.warnings,
            "metadata": self.metadata
        }

class ETLLoader:
    """Loads transformed data into Neo4j and Qdrant"""

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

        # Neo4j configuration
        self.neo4j_uri = self.config.get('neo4j_uri', 'bolt://localhost:7687')
        self.neo4j_user = self.config.get('neo4j_user', 'neo4j')
        self.neo4j_password = self.config.get('neo4j_password', 'your-secure-neo4j-password')

        # Qdrant configuration
        self.qdrant_host = self.config.get('qdrant_host', 'localhost')
        self.qdrant_port = self.config.get('qdrant_port', 6333)
        self.qdrant_collection = self.config.get('qdrant_collection', 'plc_embeddings')

        # Batch settings
        self.batch_size = self.config.get('batch_size', 100)

        # Initialize clients
        self.neo4j_driver = None
        self.qdrant_client = None
        self._initialize_clients()

    def _initialize_clients(self):
        """Initialize database clients"""
        try:
            # Neo4j driver
            self.neo4j_driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            self.logger.info(f"Connected to Neo4j at {self.neo4j_uri}")

            # Qdrant client
            if QDRANT_AVAILABLE:
                self.qdrant_client = QdrantClient(
                    host=self.qdrant_host,
                    port=self.qdrant_port
                )
                self.logger.info(f"Connected to Qdrant at {self.qdrant_host}:{self.qdrant_port}")
            else:
                self.logger.warning("Qdrant client not available")

        except Exception as e:
            self.logger.error(f"Error initializing database clients: {e}")
            raise

    def close(self):
        """Close database connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()
        if self.qdrant_client:
            self.qdrant_client.close()

    async def load_transformation_result(self, result: TransformationResult) -> LoadResult:
        """Load complete transformation result into databases"""
        load_result = LoadResult()
        load_result.metadata["started_at"] = datetime.now().isoformat()

        try:
            # Load nodes and relationships into Neo4j
            if result.nodes or result.relationships:
                neo4j_result = await self._load_to_neo4j(result.nodes, result.relationships)
                load_result.nodes_loaded = neo4j_result["nodes_loaded"]
                load_result.relationships_loaded = neo4j_result["relationships_loaded"]
                load_result.errors.extend(neo4j_result.get("errors", []))

            # Load vectors into Qdrant
            if result.vectors and QDRANT_AVAILABLE:
                qdrant_result = await self._load_to_qdrant(result.vectors)
                load_result.vectors_loaded = qdrant_result["vectors_loaded"]
                load_result.errors.extend(qdrant_result.get("errors", []))
            elif result.vectors and not QDRANT_AVAILABLE:
                load_result.warnings.append("Qdrant not available - vectors not loaded")

            load_result.metadata["completed_at"] = datetime.now().isoformat()
            load_result.metadata["source_file"] = result.metadata.get("source_file", "unknown")

            self.logger.info(
                f"Load completed: {load_result.nodes_loaded} nodes, "
                f"{load_result.relationships_loaded} relationships, "
                f"{load_result.vectors_loaded} vectors"
            )

            return load_result

        except Exception as e:
            error_msg = f"Error during load operation: {e}"
            self.logger.error(error_msg)
            load_result.errors.append(error_msg)
            return load_result

    async def _load_to_neo4j(self, nodes: List[TransformedNode], relationships: List[TransformedRelationship]) -> Dict[str, Any]:
        """Load nodes and relationships into Neo4j"""
        result = {"nodes_loaded": 0, "relationships_loaded": 0, "errors": []}

        try:
            with self.neo4j_driver.session() as session:
                # Load nodes in batches
                for i in range(0, len(nodes), self.batch_size):
                    batch = nodes[i:i + self.batch_size]
                    nodes_loaded = self._load_nodes_batch(session, batch)
                    result["nodes_loaded"] += nodes_loaded

                # Load relationships in batches
                for i in range(0, len(relationships), self.batch_size):
                    batch = relationships[i:i + self.batch_size]
                    relationships_loaded = self._load_relationships_batch(session, batch)
                    result["relationships_loaded"] += relationships_loaded

                self.logger.info(
                    f"Neo4j load completed: {result['nodes_loaded']} nodes, "
                    f"{result['relationships_loaded']} relationships"
                )

        except Neo4jError as e:
            error_msg = f"Neo4j error: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error loading to Neo4j: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    def _load_nodes_batch(self, session, nodes: List[TransformedNode]) -> int:
        """Load a batch of nodes into Neo4j"""
        if not nodes:
            return 0

        # Group nodes by label for efficient batch insertion
        nodes_by_label = {}
        for node in nodes:
            if node.label not in nodes_by_label:
                nodes_by_label[node.label] = []
            nodes_by_label[node.label].append(node)

        total_loaded = 0

        for label, label_nodes in nodes_by_label.items():
            # Create MERGE query for this label
            query = f"""
            UNWIND $nodes as nodeData
            MERGE (n:{label} {{uuid: nodeData.uuid}})
            SET n += nodeData.properties
            RETURN count(n) as loaded_count
            """

            node_data = [
                {
                    "uuid": node.uuid,
                    "properties": node.properties
                }
                for node in label_nodes
            ]

            try:
                result = session.run(query, {"nodes": node_data})
                loaded_count = result.single()["loaded_count"]
                total_loaded += loaded_count
                self.logger.debug(f"Loaded {loaded_count} {label} nodes")

            except Exception as e:
                self.logger.error(f"Error loading {label} nodes: {e}")
                continue

        return total_loaded

    def _load_relationships_batch(self, session, relationships: List[TransformedRelationship]) -> int:
        """Load a batch of relationships into Neo4j"""
        if not relationships:
            return 0

        # Group relationships by type for efficient batch insertion
        relationships_by_type = {}
        for rel in relationships:
            if rel.type not in relationships_by_type:
                relationships_by_type[rel.type] = []
            relationships_by_type[rel.type].append(rel)

        total_loaded = 0

        for rel_type, rel_list in relationships_by_type.items():
            query = f"""
            UNWIND $relationships as relData
            MATCH (source {{uuid: relData.source_uuid}})
            MATCH (target {{uuid: relData.target_uuid}})
            MERGE (source)-[r:{rel_type}]->(target)
            SET r += relData.properties
            RETURN count(r) as loaded_count
            """

            rel_data = [
                {
                    "source_uuid": rel.source_uuid,
                    "target_uuid": rel.target_uuid,
                    "properties": rel.properties
                }
                for rel in rel_list
            ]

            try:
                result = session.run(query, {"relationships": rel_data})
                loaded_count = result.single()["loaded_count"]
                total_loaded += loaded_count
                self.logger.debug(f"Loaded {loaded_count} {rel_type} relationships")

            except Exception as e:
                self.logger.error(f"Error loading {rel_type} relationships: {e}")
                continue

        return total_loaded

    async def _load_to_qdrant(self, vectors: List[VectorRecord]) -> Dict[str, Any]:
        """Load vectors into Qdrant"""
        result = {"vectors_loaded": 0, "errors": []}

        if not QDRANT_AVAILABLE:
            result["errors"].append("Qdrant client not available")
            return result

        try:
            # Ensure collection exists
            await self._ensure_qdrant_collection(vectors)

            # Load vectors in batches
            for i in range(0, len(vectors), self.batch_size):
                batch = vectors[i:i + self.batch_size]
                vectors_loaded = await self._load_vectors_batch(batch)
                result["vectors_loaded"] += vectors_loaded

            self.logger.info(f"Qdrant load completed: {result['vectors_loaded']} vectors")

        except Exception as e:
            error_msg = f"Error loading to Qdrant: {e}"
            self.logger.error(error_msg)
            result["errors"].append(error_msg)

        return result

    async def _ensure_qdrant_collection(self, vectors: List[VectorRecord]):
        """Ensure Qdrant collection exists with correct configuration"""
        if not vectors:
            return

        try:
            # Check if collection exists
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.qdrant_collection not in collection_names:
                # Get vector dimension from first vector
                vector_dim = len(vectors[0].vector)

                # Create collection
                self.qdrant_client.create_collection(
                    collection_name=self.qdrant_collection,
                    vectors_config=VectorParams(
                        size=vector_dim,
                        distance=Distance.COSINE
                    )
                )
                self.logger.info(f"Created Qdrant collection '{self.qdrant_collection}' with dimension {vector_dim}")
            else:
                self.logger.debug(f"Qdrant collection '{self.qdrant_collection}' already exists")

        except Exception as e:
            self.logger.error(f"Error ensuring Qdrant collection: {e}")
            raise

    async def _load_vectors_batch(self, vectors: List[VectorRecord]) -> int:
        """Load a batch of vectors into Qdrant"""
        if not vectors:
            return 0

        try:
            points = []
            for vector in vectors:
                point = PointStruct(
                    id=vector.id,
                    vector=vector.vector,
                    payload=vector.payload
                )
                points.append(point)

            # Upsert points (insert or update)
            self.qdrant_client.upsert(
                collection_name=self.qdrant_collection,
                points=points
            )

            self.logger.debug(f"Loaded {len(points)} vectors to Qdrant")
            return len(points)

        except Exception as e:
            self.logger.error(f"Error loading vector batch: {e}")
            return 0

    def test_connections(self) -> Dict[str, bool]:
        """Test database connections"""
        results = {
            "neo4j": False,
            "qdrant": False
        }

        # Test Neo4j
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                if result.single()["test"] == 1:
                    results["neo4j"] = True
                    self.logger.info("Neo4j connection test: PASSED")
        except Exception as e:
            self.logger.error(f"Neo4j connection test: FAILED - {e}")

        # Test Qdrant
        if QDRANT_AVAILABLE:
            try:
                self.qdrant_client.get_collections()
                results["qdrant"] = True
                self.logger.info("Qdrant connection test: PASSED")
            except Exception as e:
                self.logger.error(f"Qdrant connection test: FAILED - {e}")
        else:
            self.logger.warning("Qdrant not available - skipping connection test")

        return results

    def get_load_statistics(self) -> Dict[str, Any]:
        """Get database load statistics"""
        stats = {
            "neo4j": {},
            "qdrant": {},
            "timestamp": datetime.now().isoformat()
        }

        # Neo4j statistics
        try:
            with self.neo4j_driver.session() as session:
                # Node counts by label
                node_result = session.run("MATCH (n) RETURN labels(n) as labels, count(n) as count")
                node_counts = {}
                for record in node_result:
                    labels = record["labels"]
                    if labels:
                        label = labels[0]  # Use first label
                        node_counts[label] = record["count"]

                # Relationship counts by type
                rel_result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
                rel_counts = {record["type"]: record["count"] for record in rel_result}

                stats["neo4j"] = {
                    "nodes": node_counts,
                    "relationships": rel_counts,
                    "total_nodes": sum(node_counts.values()),
                    "total_relationships": sum(rel_counts.values())
                }

        except Exception as e:
            stats["neo4j"]["error"] = str(e)

        # Qdrant statistics
        if QDRANT_AVAILABLE:
            try:
                collection_info = self.qdrant_client.get_collection(self.qdrant_collection)
                stats["qdrant"] = {
                    "collection": self.qdrant_collection,
                    "points_count": collection_info.points_count,
                    "vectors_count": collection_info.vectors_count,
                    "status": collection_info.status
                }
            except Exception as e:
                stats["qdrant"]["error"] = str(e)
        else:
            stats["qdrant"]["error"] = "Qdrant not available"

        return stats

def main():
    """Test the ETL loader"""
    import sys

    from document_parser import DocumentParser
    from etl_transformer import ETLTransformer

    if len(sys.argv) < 2:
        print("Usage: python etl_loader.py <file_path>")
        sys.exit(1)

    file_path = sys.argv[1]

    async def test_load():
        # Parse document
        parser = DocumentParser()
        extracted_doc = parser.parse_document(file_path)

        if not extracted_doc:
            print(f"Failed to parse {file_path}")
            return

        # Transform document
        transformer = ETLTransformer()
        transform_result = await transformer.transform_document(extracted_doc)

        if transform_result.errors:
            print("Transformation errors:")
            for error in transform_result.errors:
                print(f"  - {error}")
            return

        # Load data
        loader = ETLLoader()

        # Test connections first
        connections = loader.test_connections()
        print(f"Connection Tests: {connections}")

        if not connections["neo4j"]:
            print("Neo4j connection failed - aborting")
            return

        # Perform load
        load_result = await loader.load_transformation_result(transform_result)

        print("Load Results:")
        print(f"  Nodes loaded: {load_result.nodes_loaded}")
        print(f"  Relationships loaded: {load_result.relationships_loaded}")
        print(f"  Vectors loaded: {load_result.vectors_loaded}")

        if load_result.errors:
            print("Load errors:")
            for error in load_result.errors:
                print(f"  - {error}")

        if load_result.warnings:
            print("Load warnings:")
            for warning in load_result.warnings:
                print(f"  - {warning}")

        # Show statistics
        stats = loader.get_load_statistics()
        print("\nDatabase Statistics:")
        print(f"  Neo4j nodes: {stats['neo4j'].get('total_nodes', 'N/A')}")
        print(f"  Neo4j relationships: {stats['neo4j'].get('total_relationships', 'N/A')}")
        print(f"  Qdrant vectors: {stats['qdrant'].get('points_count', 'N/A')}")

        loader.close()

    asyncio.run(test_load())

if __name__ == "__main__":
    main()
