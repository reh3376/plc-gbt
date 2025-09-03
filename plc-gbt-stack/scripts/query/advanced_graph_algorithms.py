#!/usr/bin/env python3
"""
Advanced Graph Traversal Algorithms
Created: January 1, 2025
Purpose: Sophisticated graph analysis for PLC component relationships
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx

# Neo4j
from neo4j import GraphDatabase

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

@dataclass
class GraphPath:
    """Represents a path through the graph"""
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    total_weight: float
    path_type: str
    metadata: Dict[str, Any]

@dataclass
class ComponentCluster:
    """Represents a cluster of related components"""
    cluster_id: str
    nodes: List[Dict[str, Any]]
    internal_edges: int
    external_edges: int
    cohesion_score: float
    cluster_type: str

@dataclass
class DependencyChain:
    """Represents a dependency chain between components"""
    source_node: Dict[str, Any]
    target_node: Dict[str, Any]
    dependency_path: List[Dict[str, Any]]
    dependency_type: str
    strength: float

class AdvancedGraphAnalyzer:
    """
    Advanced graph analysis algorithms for PLC component relationships.

    Features:
    - Multi-hop relationship traversal
    - Component clustering and community detection
    - Shortest path and dependency analysis
    - Graph metrics and centrality analysis
    - Performance-optimized algorithms
    """

    def __init__(
        self,
        neo4j_uri: str,
        neo4j_user: str,
        neo4j_password: str
    ):
        """
        Initialize advanced graph analyzer.

        Args:
            neo4j_uri: Neo4j connection URI
            neo4j_user: Neo4j username
            neo4j_password: Neo4j password
        """
        self.neo4j_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password),
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=50
        )

        # Algorithm caches
        self.path_cache = {}
        self.cluster_cache = {}
        self.centrality_cache = {}

        # Performance metrics
        self.algorithm_metrics = defaultdict(list)

        logger.info("AdvancedGraphAnalyzer initialized")

    async def find_multi_hop_relationships(
        self,
        start_node_id: str,
        relationship_types: List[str],
        max_hops: int = 5,
        direction: str = "both"
    ) -> List[GraphPath]:
        """
        Find multi-hop relationships starting from a node.

        Args:
            start_node_id: Starting node identifier
            relationship_types: List of relationship types to follow
            max_hops: Maximum number of hops to traverse
            direction: Direction to traverse ("outgoing", "incoming", "both")

        Returns:
            List of graph paths found
        """
        start_time = datetime.now()

        try:
            with self.neo4j_driver.session() as session:
                # Build direction clause
                if direction == "outgoing":
                    direction_clause = "-[r]->"
                elif direction == "incoming":
                    direction_clause = "<-[r]-"
                else:
                    direction_clause = "-[r]-"

                # Build relationship type filter
                rel_filter = "|".join(relationship_types) if relationship_types else ""
                if rel_filter:
                    rel_filter = f":{rel_filter}"

                query = f"""
                MATCH path = (start{{uuid: $start_id}})
                             ({direction_clause}(node)){{1,{max_hops}}}
                WHERE ALL(r in relationships(path) WHERE type(r) IN $rel_types OR $rel_types = [])
                AND length(path) <= $max_hops
                WITH path,
                     [n in nodes(path) | {{
                         uuid: n.uuid,
                         labels: labels(n),
                         properties: properties(n)
                     }}] as node_list,
                     [r in relationships(path) | {{
                         type: type(r),
                         properties: properties(r)
                     }}] as rel_list
                RETURN node_list, rel_list, length(path) as path_length
                ORDER BY path_length
                LIMIT 1000
                """

                result = session.run(
                    query,
                    start_id=start_node_id,
                    rel_types=relationship_types,
                    max_hops=max_hops
                )

                paths = []
                for record in result:
                    path = GraphPath(
                        nodes=record["node_list"],
                        relationships=record["rel_list"],
                        total_weight=record["path_length"],
                        path_type="multi_hop",
                        metadata={
                            "start_node": start_node_id,
                            "hops": record["path_length"],
                            "direction": direction
                        }
                    )
                    paths.append(path)

                # Record performance metrics
                duration = (datetime.now() - start_time).total_seconds()
                self.algorithm_metrics["multi_hop_traversal"].append({
                    "duration": duration,
                    "paths_found": len(paths),
                    "max_hops": max_hops
                })

                logger.info("Multi-hop traversal completed",
                           start_node=start_node_id,
                           paths_found=len(paths),
                           duration_ms=duration * 1000)

                return paths

        except Exception as e:
            logger.error("Multi-hop traversal failed", error=str(e))
            return []

    async def find_shortest_paths(
        self,
        source_id: str,
        target_id: str,
        relationship_types: Optional[List[str]] = None,
        weight_property: Optional[str] = None
    ) -> List[GraphPath]:
        """
        Find shortest paths between two nodes using Dijkstra's algorithm.

        Args:
            source_id: Source node identifier
            target_id: Target node identifier
            relationship_types: Relationship types to consider
            weight_property: Property to use as edge weight

        Returns:
            List of shortest paths
        """
        start_time = datetime.now()

        try:
            with self.neo4j_driver.session() as session:
                # Use Neo4j's built-in shortest path algorithms
                if weight_property:
                    # Weighted shortest path
                    query = """
                    MATCH (source {uuid: $source_id}), (target {uuid: $target_id})
                    CALL gds.shortestPath.dijkstra.stream('plc-graph', {
                        sourceNode: source,
                        targetNode: target,
                        relationshipWeightProperty: $weight_prop
                    })
                    YIELD index, sourceNode, targetNode, totalCost, nodeIds, costs, path
                    RETURN path, totalCost, nodeIds
                    """
                else:
                    # Unweighted shortest path
                    query = """
                    MATCH (source {uuid: $source_id}), (target {uuid: $target_id})
                    MATCH path = shortestPath((source)-[*]-(target))
                    WITH path,
                         [n in nodes(path) | {
                             uuid: n.uuid,
                             labels: labels(n),
                             properties: properties(n)
                         }] as node_list,
                         [r in relationships(path) | {
                             type: type(r),
                             properties: properties(r)
                         }] as rel_list
                    RETURN node_list, rel_list, length(path) as path_length
                    """

                if weight_property:
                    result = session.run(query,
                                       source_id=source_id,
                                       target_id=target_id,
                                       weight_prop=weight_property)
                else:
                    result = session.run(query,
                                       source_id=source_id,
                                       target_id=target_id)

                paths = []
                for record in result:
                    if weight_property:
                        # Handle weighted path result
                        path = GraphPath(
                            nodes=[],  # Would need to extract from Neo4j path object
                            relationships=[],
                            total_weight=record["totalCost"],
                            path_type="shortest_weighted",
                            metadata={
                                "source": source_id,
                                "target": target_id,
                                "weight_property": weight_property
                            }
                        )
                    else:
                        # Handle unweighted path result
                        path = GraphPath(
                            nodes=record["node_list"],
                            relationships=record["rel_list"],
                            total_weight=record["path_length"],
                            path_type="shortest_unweighted",
                            metadata={
                                "source": source_id,
                                "target": target_id
                            }
                        )
                    paths.append(path)

                duration = (datetime.now() - start_time).total_seconds()
                self.algorithm_metrics["shortest_path"].append({
                    "duration": duration,
                    "paths_found": len(paths),
                    "weighted": weight_property is not None
                })

                logger.info("Shortest path search completed",
                           source=source_id,
                           target=target_id,
                           paths_found=len(paths),
                           duration_ms=duration * 1000)

                return paths

        except Exception as e:
            logger.error("Shortest path search failed", error=str(e))
            return []

    async def detect_component_clusters(
        self,
        cluster_algorithm: str = "modularity",
        min_cluster_size: int = 3
    ) -> List[ComponentCluster]:
        """
        Detect clusters of related components using community detection.

        Args:
            cluster_algorithm: Algorithm to use ("modularity", "louvain", "label_propagation")
            min_cluster_size: Minimum size for a cluster to be included

        Returns:
            List of detected component clusters
        """
        start_time = datetime.now()

        try:
            with self.neo4j_driver.session() as session:
                # First, get the graph structure
                graph_query = """
                MATCH (n)-[r]-(m)
                WHERE n.uuid IS NOT NULL AND m.uuid IS NOT NULL
                RETURN
                    n.uuid as source_id,
                    labels(n) as source_labels,
                    properties(n) as source_props,
                    type(r) as rel_type,
                    m.uuid as target_id,
                    labels(m) as target_labels,
                    properties(m) as target_props
                """

                result = session.run(graph_query)

                # Build NetworkX graph for analysis
                G = nx.Graph()
                node_data = {}

                for record in result:
                    source_id = record["source_id"]
                    target_id = record["target_id"]

                    # Add nodes with metadata
                    if source_id not in node_data:
                        node_data[source_id] = {
                            "labels": record["source_labels"],
                            "properties": record["source_props"]
                        }
                        G.add_node(source_id)

                    if target_id not in node_data:
                        node_data[target_id] = {
                            "labels": record["target_labels"],
                            "properties": record["target_props"]
                        }
                        G.add_node(target_id)

                    # Add edge
                    G.add_edge(source_id, target_id,
                              relationship_type=record["rel_type"])

                # Apply clustering algorithm
                if cluster_algorithm == "modularity":
                    communities = nx.community.greedy_modularity_communities(G)
                elif cluster_algorithm == "louvain":
                    # Would need to install python-louvain: pip install python-louvain
                    try:
                        import community as community_louvain
                        partition = community_louvain.best_partition(G)
                        communities = defaultdict(set)
                        for node, comm_id in partition.items():
                            communities[comm_id].add(node)
                        communities = list(communities.values())
                    except ImportError:
                        logger.warning("python-louvain not available, falling back to modularity")
                        communities = nx.community.greedy_modularity_communities(G)
                elif cluster_algorithm == "label_propagation":
                    communities = nx.community.label_propagation_communities(G)
                else:
                    communities = nx.community.greedy_modularity_communities(G)

                # Convert to ComponentCluster objects
                clusters = []
                for i, community in enumerate(communities):
                    if len(community) >= min_cluster_size:
                        # Calculate cluster metrics
                        subgraph = G.subgraph(community)
                        internal_edges = subgraph.number_of_edges()

                        # Count external edges
                        external_edges = 0
                        for node in community:
                            for neighbor in G.neighbors(node):
                                if neighbor not in community:
                                    external_edges += 1

                        # Calculate cohesion score
                        possible_internal = len(community) * (len(community) - 1) / 2
                        cohesion_score = internal_edges / possible_internal if possible_internal > 0 else 0

                        # Determine cluster type based on node labels
                        label_counts = defaultdict(int)
                        cluster_nodes = []
                        for node_id in community:
                            node_info = node_data[node_id]
                            cluster_nodes.append({
                                "uuid": node_id,
                                "labels": node_info["labels"],
                                "properties": node_info["properties"]
                            })
                            for label in node_info["labels"]:
                                label_counts[label] += 1

                        # Most common label determines cluster type
                        cluster_type = max(label_counts.items(), key=lambda x: x[1])[0] if label_counts else "mixed"

                        cluster = ComponentCluster(
                            cluster_id=f"cluster_{i}",
                            nodes=cluster_nodes,
                            internal_edges=internal_edges,
                            external_edges=external_edges,
                            cohesion_score=cohesion_score,
                            cluster_type=cluster_type
                        )
                        clusters.append(cluster)

                duration = (datetime.now() - start_time).total_seconds()
                self.algorithm_metrics["clustering"].append({
                    "duration": duration,
                    "clusters_found": len(clusters),
                    "algorithm": cluster_algorithm,
                    "total_nodes": G.number_of_nodes()
                })

                logger.info("Component clustering completed",
                           algorithm=cluster_algorithm,
                           clusters_found=len(clusters),
                           total_nodes=G.number_of_nodes(),
                           duration_ms=duration * 1000)

                return clusters

        except Exception as e:
            logger.error("Component clustering failed", error=str(e))
            return []

    async def analyze_component_dependencies(
        self,
        component_id: str,
        dependency_types: List[str] = None
    ) -> List[DependencyChain]:
        """
        Analyze dependency chains for a specific component.

        Args:
            component_id: Component to analyze
            dependency_types: Types of relationships that indicate dependencies

        Returns:
            List of dependency chains
        """
        if dependency_types is None:
            dependency_types = ["USES", "CONTAINS", "USES_UDT", "RELATES_TO"]
        start_time = datetime.now()

        try:
            with self.neo4j_driver.session() as session:
                # Find direct and indirect dependencies
                query = """
                MATCH (start {uuid: $component_id})
                MATCH path = (start)-[:USES|CONTAINS|USES_UDT|RELATES_TO*1..3]->(dep)
                WHERE start <> dep
                WITH path, start, dep,
                     [n in nodes(path) | {
                         uuid: n.uuid,
                         labels: labels(n),
                         properties: properties(n)
                     }] as path_nodes,
                     [r in relationships(path) | type(r)] as rel_types
                RETURN
                    {uuid: start.uuid, labels: labels(start), properties: properties(start)} as source,
                    {uuid: dep.uuid, labels: labels(dep), properties: properties(dep)} as target,
                    path_nodes,
                    rel_types,
                    length(path) as dependency_distance
                ORDER BY dependency_distance, dep.uuid
                """

                result = session.run(query, component_id=component_id)

                dependencies = []
                for record in result:
                    # Calculate dependency strength (inverse of distance)
                    distance = record["dependency_distance"]
                    strength = 1.0 / distance if distance > 0 else 1.0

                    # Determine dependency type based on relationships
                    rel_types = record["rel_types"]
                    if "USES" in rel_types:
                        dep_type = "functional_dependency"
                    elif "CONTAINS" in rel_types:
                        dep_type = "structural_dependency"
                    elif "USES_UDT" in rel_types:
                        dep_type = "data_dependency"
                    else:
                        dep_type = "general_dependency"

                    dependency = DependencyChain(
                        source_node=record["source"],
                        target_node=record["target"],
                        dependency_path=record["path_nodes"],
                        dependency_type=dep_type,
                        strength=strength
                    )
                    dependencies.append(dependency)

                duration = (datetime.now() - start_time).total_seconds()
                self.algorithm_metrics["dependency_analysis"].append({
                    "duration": duration,
                    "dependencies_found": len(dependencies),
                    "component_id": component_id
                })

                logger.info("Dependency analysis completed",
                           component_id=component_id,
                           dependencies_found=len(dependencies),
                           duration_ms=duration * 1000)

                return dependencies

        except Exception as e:
            logger.error("Dependency analysis failed", error=str(e))
            return []

    async def calculate_centrality_metrics(
        self,
        centrality_types: List[str] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Calculate centrality metrics for all nodes in the graph.

        Args:
            centrality_types: Types of centrality to calculate

        Returns:
            Dictionary mapping node IDs to centrality scores
        """
        if centrality_types is None:
            centrality_types = ["degree", "betweenness", "closeness", "pagerank"]
        start_time = datetime.now()

        try:
            with self.neo4j_driver.session() as session:
                # Get graph structure
                query = """
                MATCH (n)-[r]-(m)
                WHERE n.uuid IS NOT NULL AND m.uuid IS NOT NULL
                RETURN n.uuid as source, m.uuid as target
                """

                result = session.run(query)

                # Build NetworkX graph
                G = nx.Graph()
                for record in result:
                    G.add_edge(record["source"], record["target"])

                centrality_results = {}

                # Calculate different centrality measures
                if "degree" in centrality_types:
                    degree_centrality = nx.degree_centrality(G)
                    for node_id, score in degree_centrality.items():
                        if node_id not in centrality_results:
                            centrality_results[node_id] = {}
                        centrality_results[node_id]["degree"] = score

                if "betweenness" in centrality_types:
                    betweenness_centrality = nx.betweenness_centrality(G)
                    for node_id, score in betweenness_centrality.items():
                        if node_id not in centrality_results:
                            centrality_results[node_id] = {}
                        centrality_results[node_id]["betweenness"] = score

                if "closeness" in centrality_types:
                    closeness_centrality = nx.closeness_centrality(G)
                    for node_id, score in closeness_centrality.items():
                        if node_id not in centrality_results:
                            centrality_results[node_id] = {}
                        centrality_results[node_id]["closeness"] = score

                if "pagerank" in centrality_types:
                    pagerank_centrality = nx.pagerank(G)
                    for node_id, score in pagerank_centrality.items():
                        if node_id not in centrality_results:
                            centrality_results[node_id] = {}
                        centrality_results[node_id]["pagerank"] = score

                # Cache results
                self.centrality_cache = centrality_results

                duration = (datetime.now() - start_time).total_seconds()
                self.algorithm_metrics["centrality"].append({
                    "duration": duration,
                    "nodes_analyzed": len(centrality_results),
                    "centrality_types": centrality_types
                })

                logger.info("Centrality analysis completed",
                           nodes_analyzed=len(centrality_results),
                           centrality_types=centrality_types,
                           duration_ms=duration * 1000)

                return centrality_results

        except Exception as e:
            logger.error("Centrality analysis failed", error=str(e))
            return {}

    def get_algorithm_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all algorithms"""
        metrics = {}
        for algorithm, measurements in self.algorithm_metrics.items():
            if measurements:
                durations = [m["duration"] for m in measurements]
                metrics[algorithm] = {
                    "total_runs": len(measurements),
                    "avg_duration_ms": (sum(durations) / len(durations)) * 1000,
                    "min_duration_ms": min(durations) * 1000,
                    "max_duration_ms": max(durations) * 1000,
                    "latest_run": measurements[-1]
                }
        return metrics

    def close(self):
        """Clean up resources"""
        if self.neo4j_driver:
            self.neo4j_driver.close()

# Utility functions for graph analysis
def calculate_graph_density(nodes: int, edges: int) -> float:
    """Calculate graph density"""
    if nodes < 2:
        return 0.0
    max_edges = nodes * (nodes - 1) / 2
    return edges / max_edges

def find_articulation_points(graph_data: List[Tuple[str, str]]) -> List[str]:
    """Find articulation points (critical nodes) in the graph"""
    G = nx.Graph()
    G.add_edges_from(graph_data)
    return list(nx.articulation_points(G))

def calculate_clustering_coefficient(graph_data: List[Tuple[str, str]]) -> Dict[str, float]:
    """Calculate clustering coefficient for each node"""
    G = nx.Graph()
    G.add_edges_from(graph_data)
    return nx.clustering(G)
