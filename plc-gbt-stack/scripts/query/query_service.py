#!/usr/bin/env python3
"""
Query Service Module
Created: January 1, 2025
Purpose: Unified query interface combining vector search with graph traversal
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Neo4j
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError

# Qdrant
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, FieldCondition, Filter, MatchValue, VectorParams
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logging.warning("Qdrant client not available - vector search disabled")

# OpenAI for query embedding
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI client not available - embedding search disabled")

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Container for unified query results"""
    question: str
    answer: Optional[str] = None
    graph_context: Dict[str, Any] = None
    vector_context: List[Dict[str, Any]] = None
    combined_context: Dict[str, Any] = None
    citations: List[Dict[str, Any]] = None
    confidence_score: float = 0.0
    processing_time_ms: float = 0.0
    query_strategy: str = "hybrid"
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.graph_context is None:
            self.graph_context = {"nodes": [], "relationships": []}
        if self.vector_context is None:
            self.vector_context = []
        if self.citations is None:
            self.citations = []
        if self.combined_context is None:
            self.combined_context = {}

@dataclass
class VectorSearchResult:
    """Vector similarity search result"""
    id: str
    score: float
    payload: Dict[str, Any]
    text: str
    component_type: str

@dataclass
class GraphTraversalResult:
    """Graph traversal query result"""
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    paths: List[List[Dict[str, Any]]]
    cypher_query: str
    execution_time_ms: float

class QueryService:
    """
    Unified query service combining vector similarity search with graph traversal.

    Provides multiple query strategies:
    - Vector-only: Pure semantic similarity search
    - Graph-only: Pure graph traversal and relationship queries
    - Hybrid: Combined vector + graph with intelligent merging
    - Context-aware: Uses query type to determine optimal strategy
    """

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        openai_api_key: Optional[str] = None,
        embedding_model: str = "text-embedding-3-large"
    ):
        """
        Initialize query service with database connections.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
            qdrant_host: Qdrant server host
            qdrant_port: Qdrant server port
            openai_api_key: OpenAI API key for embeddings
            embedding_model: OpenAI embedding model name
        """
        # Initialize Neo4j connection
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60
        )

        # Initialize Qdrant connection
        if QDRANT_AVAILABLE:
            self.qdrant_client = QdrantClient(
                host=qdrant_host,
                port=qdrant_port,
                timeout=30.0
            )
        else:
            self.qdrant_client = None

        # Initialize OpenAI
        if OPENAI_AVAILABLE and openai_api_key:
            openai.api_key = openai_api_key
            self.embedding_model = embedding_model
            self.openai_available = True
        else:
            self.openai_available = False

        # Query performance tracking
        self.query_stats = {
            "total_queries": 0,
            "vector_queries": 0,
            "graph_queries": 0,
            "hybrid_queries": 0,
            "avg_response_time_ms": 0.0,
            "cache_hits": 0
        }

        # Simple cache for frequent queries
        self.query_cache = {}
        self.cache_size_limit = 100

        logger.info("QueryService initialized",
                   neo4j_available=bool(self.neo4j_driver),
                   qdrant_available=bool(self.qdrant_client),
                   openai_available=self.openai_available)

    def close(self):
        """Close database connections"""
        if self.neo4j_driver:
            self.neo4j_driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def query(
        self,
        question: str,
        strategy: str = "hybrid",
        max_results: int = 10,
        include_context: bool = True,
        vector_threshold: float = 0.7,
        expand_graph: bool = True
    ) -> QueryResult:
        """
        Execute unified query using specified strategy.

        Args:
            question: User question/query
            strategy: Query strategy ('vector', 'graph', 'hybrid', 'context-aware')
            max_results: Maximum number of results to return
            include_context: Whether to include detailed context
            vector_threshold: Minimum similarity score for vector results
            expand_graph: Whether to expand graph context with related nodes

        Returns:
            QueryResult with combined results and context
        """
        start_time = time.time()

        # Check cache first
        cache_key = self._generate_cache_key(question, strategy, max_results)
        if cache_key in self.query_cache:
            logger.info("Cache hit", question=question[:50])
            self.query_stats["cache_hits"] += 1
            return self.query_cache[cache_key]

        logger.info("Processing query",
                   question=question[:100],
                   strategy=strategy,
                   max_results=max_results)

        try:
            if strategy == "vector":
                result = await self._vector_only_query(
                    question, max_results, vector_threshold
                )
            elif strategy == "graph":
                result = await self._graph_only_query(
                    question, max_results, expand_graph
                )
            elif strategy == "hybrid":
                result = await self._hybrid_query(
                    question, max_results, vector_threshold, expand_graph
                )
            elif strategy == "context-aware":
                # Determine best strategy based on query characteristics
                determined_strategy = self._determine_optimal_strategy(question)
                result = await self.query(
                    question, determined_strategy, max_results,
                    include_context, vector_threshold, expand_graph
                )
            else:
                raise ValueError(f"Unknown query strategy: {strategy}")

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000
            result.processing_time_ms = processing_time
            result.query_strategy = strategy

            # Update statistics
            self.query_stats["total_queries"] += 1
            if strategy == "vector":
                self.query_stats["vector_queries"] += 1
            elif strategy == "graph":
                self.query_stats["graph_queries"] += 1
            elif strategy in ["hybrid", "context-aware"]:
                self.query_stats["hybrid_queries"] += 1

            # Update average response time
            total = self.query_stats["total_queries"]
            current_avg = self.query_stats["avg_response_time_ms"]
            self.query_stats["avg_response_time_ms"] = (
                (current_avg * (total - 1) + processing_time) / total
            )

            # Cache result if successful
            if len(self.query_cache) < self.cache_size_limit:
                self.query_cache[cache_key] = result

            logger.info("Query completed",
                       question=question[:50],
                       strategy=strategy,
                       processing_time_ms=processing_time,
                       results_count=len(result.vector_context) + len(result.graph_context.get("nodes", [])))

            return result

        except Exception as e:
            logger.error("Query failed",
                        question=question[:50],
                        strategy=strategy,
                        error=str(e))

            # Return error result
            return QueryResult(
                question=question,
                answer=f"Query failed: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
                query_strategy=strategy,
                confidence_score=0.0
            )

    async def _vector_only_query(
        self,
        question: str,
        max_results: int,
        threshold: float
    ) -> QueryResult:
        """Execute vector similarity search only"""
        if not self.qdrant_client or not self.openai_available:
            return QueryResult(
                question=question,
                answer="Vector search not available - missing Qdrant or OpenAI",
                confidence_score=0.0
            )

        try:
            # Generate embedding for question
            query_embedding = await self._generate_query_embedding(question)
            if not query_embedding:
                raise Exception("Failed to generate query embedding")

            # Search across all collections
            vector_results = []

            collections = ['plc_embeddings', 'document_chunks', 'qa_embeddings']
            for collection in collections:
                try:
                    search_results = self.qdrant_client.search(
                        collection_name=collection,
                        query_vector=query_embedding,
                        limit=max_results // len(collections) + 2,
                        score_threshold=threshold
                    )

                    for hit in search_results:
                        vector_results.append(VectorSearchResult(
                            id=str(hit.id),
                            score=hit.score,
                            payload=hit.payload,
                            text=hit.payload.get('text', ''),
                            component_type=hit.payload.get('type', collection)
                        ))

                except Exception as e:
                    logger.warning(f"Search failed for collection {collection}: {e}")
                    continue

            # Sort by score and limit results
            vector_results.sort(key=lambda x: x.score, reverse=True)
            vector_results = vector_results[:max_results]

            # Generate answer from vector context
            answer = await self._generate_answer_from_vectors(question, vector_results)

            return QueryResult(
                question=question,
                answer=answer,
                vector_context=[{
                    "id": r.id,
                    "score": r.score,
                    "text": r.text,
                    "type": r.component_type,
                    "metadata": r.payload
                } for r in vector_results],
                citations=self._extract_citations_from_vectors(vector_results),
                confidence_score=max([r.score for r in vector_results]) if vector_results else 0.0
            )

        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            raise

    async def _graph_only_query(
        self,
        question: str,
        max_results: int,
        expand_graph: bool
    ) -> QueryResult:
        """Execute graph traversal query only"""
        try:
            # Determine query intent and generate appropriate Cypher
            cypher_queries = self._generate_cypher_queries(question)

            graph_results = GraphTraversalResult(
                nodes=[],
                relationships=[],
                paths=[],
                cypher_query="",
                execution_time_ms=0.0
            )

            # Execute queries and combine results
            with self.neo4j_driver.session() as session:
                for cypher_query in cypher_queries:
                    start_time = time.time()

                    try:
                        result = session.run(cypher_query, limit=max_results)
                        query_time = (time.time() - start_time) * 1000
                        graph_results.execution_time_ms += query_time

                        for record in result:
                            # Extract nodes and relationships from record
                            nodes, relationships = self._extract_graph_elements(record)
                            graph_results.nodes.extend(nodes)
                            graph_results.relationships.extend(relationships)

                    except Neo4jError as e:
                        logger.warning(f"Cypher query failed: {cypher_query[:100]}... Error: {e}")
                        continue

            # Remove duplicates and limit results
            graph_results.nodes = self._deduplicate_nodes(graph_results.nodes)[:max_results]
            graph_results.relationships = self._deduplicate_relationships(graph_results.relationships)

            # Expand graph context if requested
            if expand_graph and graph_results.nodes:
                expanded_context = await self._expand_graph_context(graph_results.nodes)
                graph_results.nodes.extend(expanded_context.get("nodes", []))
                graph_results.relationships.extend(expanded_context.get("relationships", []))

            # Generate answer from graph context
            answer = await self._generate_answer_from_graph(question, graph_results)

            return QueryResult(
                question=question,
                answer=answer,
                graph_context={
                    "nodes": graph_results.nodes,
                    "relationships": graph_results.relationships,
                    "execution_time_ms": graph_results.execution_time_ms
                },
                citations=self._extract_citations_from_graph(graph_results),
                confidence_score=min(1.0, len(graph_results.nodes) / max_results)
            )

        except Exception as e:
            logger.error(f"Graph query failed: {e}")
            raise

    async def _hybrid_query(
        self,
        question: str,
        max_results: int,
        vector_threshold: float,
        expand_graph: bool
    ) -> QueryResult:
        """Execute hybrid vector + graph query with intelligent merging"""
        try:
            # Execute both queries concurrently
            vector_task = asyncio.create_task(
                self._vector_only_query(question, max_results // 2, vector_threshold)
            )
            graph_task = asyncio.create_task(
                self._graph_only_query(question, max_results // 2, expand_graph)
            )

            vector_result, graph_result = await asyncio.gather(
                vector_task, graph_task, return_exceptions=True
            )

            # Handle exceptions
            if isinstance(vector_result, Exception):
                logger.warning(f"Vector query failed in hybrid: {vector_result}")
                vector_result = QueryResult(question=question)

            if isinstance(graph_result, Exception):
                logger.warning(f"Graph query failed in hybrid: {graph_result}")
                graph_result = QueryResult(question=question)

            # Merge and rank results intelligently
            combined_context = await self._merge_contexts(
                vector_result.vector_context or [],
                graph_result.graph_context or {"nodes": [], "relationships": []}
            )

            # Generate enhanced answer using both contexts
            answer = await self._generate_hybrid_answer(
                question,
                vector_result.vector_context or [],
                graph_result.graph_context or {"nodes": [], "relationships": []}
            )

            # Combine citations and calculate confidence
            all_citations = (vector_result.citations or []) + (graph_result.citations or [])
            confidence = (
                (vector_result.confidence_score or 0.0) +
                (graph_result.confidence_score or 0.0)
            ) / 2.0

            return QueryResult(
                question=question,
                answer=answer,
                graph_context=graph_result.graph_context,
                vector_context=vector_result.vector_context,
                combined_context=combined_context,
                citations=all_citations,
                confidence_score=confidence
            )

        except Exception as e:
            logger.error(f"Hybrid query failed: {e}")
            raise

    def _determine_optimal_strategy(self, question: str) -> str:
        """Analyze question to determine optimal query strategy"""
        question_lower = question.lower()

        # Keywords that suggest different strategies
        relationship_keywords = [
            "connected", "related", "uses", "contains", "part of",
            "belongs to", "communicates", "depends on", "calls"
        ]

        semantic_keywords = [
            "similar", "like", "example", "type of", "kind of",
            "what is", "how to", "explain", "describe"
        ]

        technical_keywords = [
            "aoi", "udt", "routine", "program", "tag", "device",
            "ladder", "function block", "structured text"
        ]

        # Count keyword matches
        relationship_score = sum(1 for kw in relationship_keywords if kw in question_lower)
        semantic_score = sum(1 for kw in semantic_keywords if kw in question_lower)
        technical_score = sum(1 for kw in technical_keywords if kw in question_lower)

        if relationship_score > semantic_score and technical_score > 0:
            return "graph"
        elif semantic_score > relationship_score:
            return "vector"
        else:
            return "hybrid"

    def _generate_cache_key(self, question: str, strategy: str, max_results: int) -> str:
        """Generate cache key for query"""
        content = f"{question}:{strategy}:{max_results}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _generate_query_embedding(self, question: str) -> Optional[List[float]]:
        """Generate embedding for user question"""
        if not self.openai_available:
            return None

        try:
            response = await openai.Embedding.acreate(
                model=self.embedding_model,
                input=question
            )
            return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            return None

    def _generate_cypher_queries(self, question: str) -> List[str]:
        """Generate appropriate Cypher queries based on question analysis"""
        question_lower = question.lower()
        queries = []

        # Component lookup queries
        if any(word in question_lower for word in ['aoi', 'add-on', 'instruction']):
            queries.append("""
                MATCH (aoi:AOI)
                WHERE toLower(aoi.name) CONTAINS toLower($search_term)
                   OR toLower(aoi.desc) CONTAINS toLower($search_term)
                RETURN aoi LIMIT $limit
            """)

        if any(word in question_lower for word in ['routine', 'ladder', 'function']):
            queries.append("""
                MATCH (r:Routine)
                WHERE toLower(r.name) CONTAINS toLower($search_term)
                   OR toLower(r.language) CONTAINS toLower($search_term)
                RETURN r LIMIT $limit
            """)

        # Default comprehensive query if no specific patterns matched
        if not queries:
            queries.append("""
                MATCH (n)
                WHERE n.name IS NOT NULL AND toLower(n.name) CONTAINS toLower($search_term)
                RETURN n LIMIT $limit
            """)

        return queries

    def _extract_graph_elements(self, record) -> Tuple[List[Dict], List[Dict]]:
        """Extract nodes and relationships from Neo4j record"""
        nodes = []
        relationships = []

        for _key, value in record.items():
            if hasattr(value, 'labels'):  # Node
                node_data = dict(value)
                node_data['id'] = value.id
                node_data['labels'] = list(value.labels)
                nodes.append(node_data)
            elif hasattr(value, 'type'):  # Relationship
                rel_data = dict(value)
                rel_data['id'] = value.id
                rel_data['type'] = value.type
                rel_data['start_node'] = value.start_node.id
                rel_data['end_node'] = value.end_node.id
                relationships.append(rel_data)

        return nodes, relationships

    def _deduplicate_nodes(self, nodes: List[Dict]) -> List[Dict]:
        """Remove duplicate nodes based on ID"""
        seen_ids = set()
        unique_nodes = []

        for node in nodes:
            node_id = node.get('id')
            if node_id not in seen_ids:
                seen_ids.add(node_id)
                unique_nodes.append(node)

        return unique_nodes

    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships based on ID"""
        seen_ids = set()
        unique_rels = []

        for rel in relationships:
            rel_id = rel.get('id')
            if rel_id not in seen_ids:
                seen_ids.add(rel_id)
                unique_rels.append(rel)

        return unique_rels

    async def _expand_graph_context(self, nodes: List[Dict]) -> Dict[str, List[Dict]]:
        """Expand graph context by finding related nodes"""
        if not nodes:
            return {"nodes": [], "relationships": []}

        expanded_nodes = []
        expanded_relationships = []

        with self.neo4j_driver.session() as session:
            for node in nodes[:5]:  # Limit to first 5 nodes to avoid explosion
                try:
                    result = session.run("""
                        MATCH (n)-[r]-(connected)
                        WHERE id(n) = $node_id
                        RETURN connected, r
                        LIMIT 5
                    """, node_id=node.get('id'))

                    for record in result:
                        connected_node = dict(record['connected'])
                        connected_node['id'] = record['connected'].id
                        connected_node['labels'] = list(record['connected'].labels)
                        expanded_nodes.append(connected_node)

                        relationship = dict(record['r'])
                        relationship['id'] = record['r'].id
                        relationship['type'] = record['r'].type
                        relationship['start_node'] = record['r'].start_node.id
                        relationship['end_node'] = record['r'].end_node.id
                        expanded_relationships.append(relationship)

                except Exception as e:
                    logger.warning(f"Failed to expand context for node {node.get('id')}: {e}")
                    continue

        return {
            "nodes": self._deduplicate_nodes(expanded_nodes),
            "relationships": self._deduplicate_relationships(expanded_relationships)
        }

    async def _merge_contexts(
        self,
        vector_context: List[Dict],
        graph_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Intelligently merge vector and graph contexts"""
        merged = {
            "vector_results": vector_context,
            "graph_results": graph_context,
            "cross_references": [],
            "relevance_ranking": []
        }

        # Find cross-references between vector and graph results
        graph_nodes = graph_context.get("nodes", [])

        for vector_item in vector_context:
            vector_id = vector_item.get("id")
            vector_name = vector_item.get("metadata", {}).get("name", "")

            for graph_node in graph_nodes:
                graph_name = graph_node.get("name", "")

                # Simple name matching - could be enhanced with fuzzy matching
                if vector_name and graph_name and vector_name.lower() == graph_name.lower():
                    merged["cross_references"].append({
                        "vector_id": vector_id,
                        "graph_id": graph_node.get("id"),
                        "name": vector_name,
                        "confidence": vector_item.get("score", 0.0)
                    })

        return merged

    async def _generate_answer_from_vectors(
        self,
        question: str,
        vector_results: List[VectorSearchResult]
    ) -> str:
        """Generate answer using vector search results"""
        if not vector_results:
            return "No relevant information found in the knowledge base."

        # Create context from top results
        context_parts = []
        for result in vector_results[:5]:
            context_parts.append(f"- {result.text} (Relevance: {result.score:.2f})")

        context = "\n".join(context_parts)

        answer = f"Based on the knowledge base search, here are the most relevant findings:\n\n{context}"

        return answer

    async def _generate_answer_from_graph(
        self,
        question: str,
        graph_results: GraphTraversalResult
    ) -> str:
        """Generate answer using graph traversal results"""
        if not graph_results.nodes:
            return "No relevant components found in the PLC system graph."

        # Summarize graph findings
        node_types = {}
        for node in graph_results.nodes:
            labels = node.get('labels', ['Unknown'])
            for label in labels:
                node_types[label] = node_types.get(label, 0) + 1

        summary_parts = []
        for node_type, count in node_types.items():
            summary_parts.append(f"{count} {node_type}(s)")

        summary = ", ".join(summary_parts)

        answer = f"Found {len(graph_results.nodes)} related components in the PLC system: {summary}."

        # Add specific component details
        if graph_results.nodes:
            answer += "\n\nKey components:"
            for node in graph_results.nodes[:3]:
                name = node.get('name', 'Unknown')
                labels = ', '.join(node.get('labels', []))
                answer += f"\n- {name} ({labels})"

        return answer

    async def _generate_hybrid_answer(
        self,
        question: str,
        vector_context: List[Dict],
        graph_context: Dict[str, Any]
    ) -> str:
        """Generate comprehensive answer using both vector and graph contexts"""
        vector_count = len(vector_context)
        graph_count = len(graph_context.get("nodes", []))

        if vector_count == 0 and graph_count == 0:
            return "No relevant information found in either the document knowledge base or PLC system graph."

        answer_parts = []

        if vector_count > 0:
            answer_parts.append(f"Found {vector_count} relevant documents/components with semantic similarity.")

        if graph_count > 0:
            answer_parts.append(f"Identified {graph_count} related components in the PLC system architecture.")

        # Combine insights
        answer = " ".join(answer_parts)
        answer += "\n\nCombined analysis provides both semantic relevance and structural relationships for comprehensive understanding."

        return answer

    def _extract_citations_from_vectors(self, vector_results: List[VectorSearchResult]) -> List[Dict[str, Any]]:
        """Extract citations from vector search results"""
        citations = []

        for result in vector_results:
            citation = {
                "source": result.payload.get("file_path", "Unknown Document"),
                "relevance": result.score,
                "snippet": result.text[:200] + "..." if len(result.text) > 200 else result.text,
                "type": result.component_type,
                "id": result.id
            }
            citations.append(citation)

        return citations

    def _extract_citations_from_graph(self, graph_results: GraphTraversalResult) -> List[Dict[str, Any]]:
        """Extract citations from graph traversal results"""
        citations = []

        for node in graph_results.nodes:
            citation = {
                "source": f"PLC System Graph - {', '.join(node.get('labels', []))}",
                "relevance": 0.8,
                "snippet": f"{node.get('name', 'Unknown')} - {node.get('desc', 'No description')}",
                "type": "graph_node",
                "id": str(node.get('id'))
            }
            citations.append(citation)

        return citations

    def get_query_statistics(self) -> Dict[str, Any]:
        """Get query performance statistics"""
        return self.query_stats.copy()

    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")

    async def health_check(self) -> Dict[str, bool]:
        """Check health of all connected services"""
        health = {
            "neo4j": False,
            "qdrant": False,
            "openai": False,
            "overall": False
        }

        # Test Neo4j
        try:
            with self.neo4j_driver.session() as session:
                result = session.run("RETURN 1 as test")
                list(result)
                health["neo4j"] = True
        except Exception as e:
            logger.warning(f"Neo4j health check failed: {e}")

        # Test Qdrant
        if self.qdrant_client:
            try:
                self.qdrant_client.get_collections()
                health["qdrant"] = True
            except Exception as e:
                logger.warning(f"Qdrant health check failed: {e}")

        # Test OpenAI
        if self.openai_available:
            try:
                test_embedding = await self._generate_query_embedding("test")
                health["openai"] = test_embedding is not None
            except Exception as e:
                logger.warning(f"OpenAI health check failed: {e}")

        health["overall"] = health["neo4j"] and health["qdrant"]

        return health


# Convenience functions for common query patterns
async def search_components(
    query_service: QueryService,
    component_name: str,
    component_type: Optional[str] = None
) -> QueryResult:
    """Search for specific PLC components"""
    question = f"Find {component_type or 'component'} named {component_name}"
    return await query_service.query(question, strategy="graph")

async def find_similar_content(
    query_service: QueryService,
    description: str,
    max_results: int = 5
) -> QueryResult:
    """Find semantically similar content"""
    question = f"Find content similar to: {description}"
    return await query_service.query(question, strategy="vector", max_results=max_results)

async def analyze_dependencies(
    query_service: QueryService,
    component_name: str
) -> QueryResult:
    """Analyze component dependencies and relationships"""
    question = f"What components are related to or depend on {component_name}?"
    return await query_service.query(question, strategy="hybrid", expand_graph=True)
