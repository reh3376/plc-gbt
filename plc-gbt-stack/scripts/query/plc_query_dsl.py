#!/usr/bin/env python3
"""
PLC Query DSL (Domain Specific Language)
Created: January 1, 2025
Purpose: Custom query language for PLC component analysis with natural language support
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# Structured logging
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

class QueryType(Enum):
    """Types of PLC queries"""
    FIND_COMPONENTS = "find_components"
    TRACE_CONNECTIONS = "trace_connections"
    ANALYZE_DEPENDENCIES = "analyze_dependencies"
    SEARCH_USAGE = "search_usage"
    GET_PROPERTIES = "get_properties"
    COUNT_ITEMS = "count_items"
    FIND_SIMILAR = "find_similar"
    CHECK_RELATIONSHIPS = "check_relationships"

class ComparisonOperator(Enum):
    """Comparison operators for filters"""
    EQUALS = "="
    NOT_EQUALS = "!="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_EQUAL = ">="
    LESS_EQUAL = "<="
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    MATCHES = "matches"  # regex
    IN = "in"
    NOT_IN = "not_in"

@dataclass
class FilterCondition:
    """A filter condition for queries"""
    property_name: str
    operator: ComparisonOperator
    value: Any
    case_sensitive: bool = True

@dataclass
class PLCQuery:
    """Parsed PLC query representation"""
    query_type: QueryType
    target_components: List[str] = field(default_factory=list)
    filters: List[FilterCondition] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)
    limit: Optional[int] = None
    sort_by: Optional[str] = None
    sort_descending: bool = False
    include_relationships: bool = False
    depth_limit: int = 5
    metadata: Dict[str, Any] = field(default_factory=dict)

class PLCQueryDSL:
    """
    Domain Specific Language for PLC queries.

    Features:
    - Natural language query parsing
    - Structured query building
    - Cypher query generation
    - Query validation and optimization
    - Caching and reuse
    """

    def __init__(self):
        """Initialize PLC Query DSL"""
        # Component type mappings
        self.component_types = {
            "program": "PLCProgram",
            "programs": "PLCProgram",
            "routine": "Routine",
            "routines": "Routine",
            "aoi": "AOI",
            "aois": "AOI",
            "instruction": "AOI",
            "instructions": "AOI",
            "udt": "UDT",
            "udts": "UDT",
            "datatype": "UDT",
            "datatypes": "UDT",
            "tag": "Tag",
            "tags": "Tag",
            "variable": "Tag",
            "variables": "Tag",
            "device": "Device",
            "devices": "Device",
            "controller": "Device",
            "controllers": "Device",
            "document": "SpecDoc",
            "documents": "SpecDoc",
            "spec": "SpecDoc",
            "specs": "SpecDoc"
        }

        # Relationship type mappings
        self.relationship_types = {
            "contains": "CONTAINS",
            "uses": "USES",
            "calls": "CALLS",
            "depends": "DEPENDS_ON",
            "relates": "RELATES_TO",
            "implements": "IMPLEMENTS",
            "inherits": "INHERITS_FROM",
            "connects": "CONNECTS_TO",
            "uses_udt": "USES_UDT"
        }

        # Property mappings
        self.property_mappings = {
            "name": "name",
            "names": "name",
            "type": "type",
            "types": "type",
            "description": "description",
            "version": "version",
            "created": "created_date",
            "modified": "modified_date",
            "author": "author",
            "size": "size",
            "complexity": "complexity_score",
            "usage": "usage_count",
            "catalog": "catalog_number",
            "revision": "revision"
        }

        # Natural language patterns
        self.nl_patterns = self._load_natural_language_patterns()

        # Query cache
        self.query_cache = {}

        logger.info("PLCQueryDSL initialized")

    def _load_natural_language_patterns(self) -> Dict[str, Any]:
        """Load natural language query patterns"""
        return {
            "find_patterns": [
                r"find (?:all )?(\w+)s?\s*(?:that|which|where)?\s*(.*)",
                r"show (?:me )?(?:all )?(\w+)s?\s*(?:that|which|where)?\s*(.*)",
                r"list (?:all )?(\w+)s?\s*(?:that|which|where)?\s*(.*)",
                r"get (?:all )?(\w+)s?\s*(?:that|which|where)?\s*(.*)",
                r"search (?:for )?(\w+)s?\s*(?:that|which|where)?\s*(.*)"
            ],
            "trace_patterns": [
                r"trace (?:the )?connections? (?:of|from|for) (\w+)",
                r"follow (?:the )?path (?:of|from|for) (\w+)",
                r"show (?:the )?connections? (?:of|from|for) (\w+)",
                r"map (?:the )?relationships? (?:of|from|for) (\w+)"
            ],
            "dependency_patterns": [
                r"(?:what|which) (\w+)s? depend on (\w+)",
                r"(?:what|which) (\w+)s? use (\w+)",
                r"find dependencies (?:of|for) (\w+)",
                r"show (?:what|which) uses (\w+)"
            ],
            "count_patterns": [
                r"count (?:the )?(\w+)s?",
                r"how many (\w+)s?(?: are there)?",
                r"number of (\w+)s?"
            ],
            "similarity_patterns": [
                r"find (?:similar|like) (\w+)",
                r"show (?:similar|like) (\w+)",
                r"(?:what|which) (?:is|are) similar to (\w+)"
            ]
        }

    def parse_natural_language(self, query_text: str) -> PLCQuery:
        """
        Parse natural language query into structured PLCQuery.

        Args:
            query_text: Natural language query string

        Returns:
            Parsed PLCQuery object
        """
        query_text = query_text.lower().strip()

        # Check cache first
        if query_text in self.query_cache:
            logger.debug("Using cached query parse")
            return self.query_cache[query_text]

        try:
            # Try different pattern types
            parsed_query = None

            # Find patterns
            for pattern in self.nl_patterns["find_patterns"]:
                match = re.search(pattern, query_text, re.IGNORECASE)
                if match:
                    parsed_query = self._parse_find_query(match)
                    break

            # Trace patterns
            if not parsed_query:
                for pattern in self.nl_patterns["trace_patterns"]:
                    match = re.search(pattern, query_text, re.IGNORECASE)
                    if match:
                        parsed_query = self._parse_trace_query(match)
                        break

            # Dependency patterns
            if not parsed_query:
                for pattern in self.nl_patterns["dependency_patterns"]:
                    match = re.search(pattern, query_text, re.IGNORECASE)
                    if match:
                        parsed_query = self._parse_dependency_query(match)
                        break

            # Count patterns
            if not parsed_query:
                for pattern in self.nl_patterns["count_patterns"]:
                    match = re.search(pattern, query_text, re.IGNORECASE)
                    if match:
                        parsed_query = self._parse_count_query(match)
                        break

            # Similarity patterns
            if not parsed_query:
                for pattern in self.nl_patterns["similarity_patterns"]:
                    match = re.search(pattern, query_text, re.IGNORECASE)
                    if match:
                        parsed_query = self._parse_similarity_query(match)
                        break

            # Default fallback
            if not parsed_query:
                parsed_query = self._parse_generic_query(query_text)

            # Cache the result
            self.query_cache[query_text] = parsed_query

            logger.info(f"Natural language query parsed: {parsed_query.query_type.value}, "
                       f"components={len(parsed_query.target_components)}, "
                       f"filters={len(parsed_query.filters)}")

            return parsed_query

        except Exception as e:
            logger.error(f"Failed to parse natural language query: {str(e)}")
            # Return basic search query as fallback
            return PLCQuery(
                query_type=QueryType.FIND_COMPONENTS,
                metadata={"original_query": query_text, "parse_error": str(e)}
            )

    def _parse_find_query(self, match: re.Match) -> PLCQuery:
        """Parse find-type queries"""
        component_type = match.group(1)
        conditions = match.group(2) if len(match.groups()) > 1 else ""

        # Map component type
        mapped_type = self.component_types.get(component_type, component_type)

        # Parse conditions
        filters = self._parse_conditions(conditions) if conditions else []

        return PLCQuery(
            query_type=QueryType.FIND_COMPONENTS,
            target_components=[mapped_type],
            filters=filters,
            metadata={"component_type": component_type}
        )

    def _parse_trace_query(self, match: re.Match) -> PLCQuery:
        """Parse trace/connection queries"""
        component_name = match.group(1)

        return PLCQuery(
            query_type=QueryType.TRACE_CONNECTIONS,
            target_components=[component_name],
            include_relationships=True,
            depth_limit=3,
            metadata={"trace_target": component_name}
        )

    def _parse_dependency_query(self, match: re.Match) -> PLCQuery:
        """Parse dependency queries"""
        dependent_type = match.group(1) if len(match.groups()) > 1 else "components"
        target_component = match.group(2) if len(match.groups()) > 1 else match.group(1)

        mapped_type = self.component_types.get(dependent_type, dependent_type)

        return PLCQuery(
            query_type=QueryType.ANALYZE_DEPENDENCIES,
            target_components=[target_component],
            relationships=["USES", "DEPENDS_ON", "CONTAINS"],
            metadata={"dependent_type": mapped_type}
        )

    def _parse_count_query(self, match: re.Match) -> PLCQuery:
        """Parse count queries"""
        component_type = match.group(1)
        mapped_type = self.component_types.get(component_type, component_type)

        return PLCQuery(
            query_type=QueryType.COUNT_ITEMS,
            target_components=[mapped_type],
            metadata={"count_type": component_type}
        )

    def _parse_similarity_query(self, match: re.Match) -> PLCQuery:
        """Parse similarity queries"""
        target_component = match.group(1)

        return PLCQuery(
            query_type=QueryType.FIND_SIMILAR,
            target_components=[target_component],
            limit=10,
            metadata={"similarity_target": target_component}
        )

    def _parse_generic_query(self, query_text: str) -> PLCQuery:
        """Parse generic/fallback queries"""
        # Try to identify component types mentioned
        components = []
        for key, value in self.component_types.items():
            if key in query_text:
                components.append(value)

        # Default to search if no specific patterns found
        return PLCQuery(
            query_type=QueryType.SEARCH_USAGE,
            target_components=components if components else [],
            metadata={"generic_query": query_text}
        )

    def _parse_conditions(self, conditions_text: str) -> List[FilterCondition]:
        """Parse filter conditions from text"""
        filters = []

        # Common condition patterns
        condition_patterns = [
            (r"name (?:is|equals?) ['\"]?([^'\"]+)['\"]?", "name", ComparisonOperator.EQUALS),
            (r"name contains ['\"]?([^'\"]+)['\"]?", "name", ComparisonOperator.CONTAINS),
            (r"name starts with ['\"]?([^'\"]+)['\"]?", "name", ComparisonOperator.STARTS_WITH),
            (r"type (?:is|equals?) ['\"]?([^'\"]+)['\"]?", "type", ComparisonOperator.EQUALS),
            (r"created after ([0-9-]+)", "created_date", ComparisonOperator.GREATER_THAN),
            (r"created before ([0-9-]+)", "created_date", ComparisonOperator.LESS_THAN),
            (r"size > ([0-9]+)", "size", ComparisonOperator.GREATER_THAN),
            (r"size < ([0-9]+)", "size", ComparisonOperator.LESS_THAN),
            (r"complexity > ([0-9.]+)", "complexity_score", ComparisonOperator.GREATER_THAN)
        ]

        for pattern, prop, op in condition_patterns:
            match = re.search(pattern, conditions_text, re.IGNORECASE)
            if match:
                value = match.group(1)
                # Try to convert numeric values
                try:
                    if '.' in value:
                        value = float(value)
                    elif value.isdigit():
                        value = int(value)
                except ValueError:
                    pass  # Keep as string

                filters.append(FilterCondition(
                    property_name=prop,
                    operator=op,
                    value=value,
                    case_sensitive=False
                ))

        return filters

    def build_structured_query(
        self,
        query_type: QueryType,
        target_components: List[str] = None,
        **kwargs
    ) -> PLCQuery:
        """
        Build a structured PLCQuery programmatically.

        Args:
            query_type: Type of query to build
            target_components: Components to target
            **kwargs: Additional query parameters

        Returns:
            Structured PLCQuery object
        """
        return PLCQuery(
            query_type=query_type,
            target_components=target_components or [],
            filters=kwargs.get('filters', []),
            relationships=kwargs.get('relationships', []),
            properties=kwargs.get('properties', []),
            limit=kwargs.get('limit'),
            sort_by=kwargs.get('sort_by'),
            sort_descending=kwargs.get('sort_descending', False),
            include_relationships=kwargs.get('include_relationships', False),
            depth_limit=kwargs.get('depth_limit', 5),
            metadata=kwargs.get('metadata', {})
        )

    def to_cypher_query(self, plc_query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """
        Convert PLCQuery to Cypher query.

        Args:
            plc_query: Structured PLCQuery object

        Returns:
            Tuple of (cypher_query_string, parameters_dict)
        """
        try:
            if plc_query.query_type == QueryType.FIND_COMPONENTS:
                return self._build_find_cypher(plc_query)
            elif plc_query.query_type == QueryType.TRACE_CONNECTIONS:
                return self._build_trace_cypher(plc_query)
            elif plc_query.query_type == QueryType.ANALYZE_DEPENDENCIES:
                return self._build_dependency_cypher(plc_query)
            elif plc_query.query_type == QueryType.COUNT_ITEMS:
                return self._build_count_cypher(plc_query)
            elif plc_query.query_type == QueryType.FIND_SIMILAR:
                return self._build_similarity_cypher(plc_query)
            elif plc_query.query_type == QueryType.SEARCH_USAGE:
                return self._build_usage_cypher(plc_query)
            else:
                # Generic fallback
                return self._build_generic_cypher(plc_query)

        except Exception as e:
            logger.error(f"Failed to convert to Cypher: {str(e)}")
            # Return basic fallback query
            return "MATCH (n) RETURN n LIMIT 10", {}

    def _build_find_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for FIND_COMPONENTS queries"""
        # Build MATCH clause
        if query.target_components:
            labels = "|".join(query.target_components)
            match_clause = f"MATCH (n:{labels})"
        else:
            match_clause = "MATCH (n)"

        # Build WHERE clause
        where_conditions = []
        parameters = {}

        for i, filter_cond in enumerate(query.filters):
            param_name = f"filter_{i}"
            prop_name = filter_cond.property_name

            if filter_cond.operator == ComparisonOperator.EQUALS:
                where_conditions.append(f"n.{prop_name} = ${param_name}")
                parameters[param_name] = filter_cond.value
            elif filter_cond.operator == ComparisonOperator.CONTAINS:
                if filter_cond.case_sensitive:
                    where_conditions.append(f"n.{prop_name} CONTAINS ${param_name}")
                else:
                    where_conditions.append(f"toLower(n.{prop_name}) CONTAINS toLower(${param_name})")
                parameters[param_name] = filter_cond.value
            elif filter_cond.operator == ComparisonOperator.STARTS_WITH:
                if filter_cond.case_sensitive:
                    where_conditions.append(f"n.{prop_name} STARTS WITH ${param_name}")
                else:
                    where_conditions.append(f"toLower(n.{prop_name}) STARTS WITH toLower(${param_name})")
                parameters[param_name] = filter_cond.value
            elif filter_cond.operator == ComparisonOperator.GREATER_THAN:
                where_conditions.append(f"n.{prop_name} > ${param_name}")
                parameters[param_name] = filter_cond.value
            elif filter_cond.operator == ComparisonOperator.LESS_THAN:
                where_conditions.append(f"n.{prop_name} < ${param_name}")
                parameters[param_name] = filter_cond.value

        where_clause = f" WHERE {' AND '.join(where_conditions)}" if where_conditions else ""

        # Build RETURN clause
        if query.include_relationships:
            return_clause = """
            OPTIONAL MATCH (n)-[r]-(related)
            RETURN n, collect({relationship: type(r), node: related}) as relationships
            """
        else:
            return_clause = "RETURN n"

        # Build ORDER BY clause
        order_clause = ""
        if query.sort_by:
            direction = "DESC" if query.sort_descending else "ASC"
            order_clause = f" ORDER BY n.{query.sort_by} {direction}"

        # Build LIMIT clause
        limit_clause = f" LIMIT {query.limit}" if query.limit else ""

        cypher = f"{match_clause}{where_clause}{return_clause}{order_clause}{limit_clause}"

        return cypher, parameters

    def _build_trace_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for TRACE_CONNECTIONS queries"""
        if not query.target_components:
            return "MATCH (n) RETURN n LIMIT 1", {}

        target = query.target_components[0]
        depth = query.depth_limit

        cypher = f"""
        MATCH (start)
        WHERE start.name = $target_name OR start.uuid = $target_name
        MATCH path = (start)-[*1..{depth}]-(connected)
        RETURN path,
               [node in nodes(path) | {{
                   uuid: node.uuid,
                   name: node.name,
                   labels: labels(node)
               }}] as nodes,
               [rel in relationships(path) | {{
                   type: type(rel)
               }}] as relationships
        LIMIT 100
        """

        parameters = {"target_name": target}

        return cypher, parameters

    def _build_dependency_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for ANALYZE_DEPENDENCIES queries"""
        if not query.target_components:
            return "MATCH (n) RETURN n LIMIT 1", {}

        target = query.target_components[0]
        rel_types = query.relationships or ["USES", "DEPENDS_ON", "CONTAINS"]
        rel_pattern = "|".join(rel_types)

        cypher = f"""
        MATCH (target)
        WHERE target.name = $target_name OR target.uuid = $target_name
        MATCH (dependent)-[r:{rel_pattern}]->(target)
        RETURN
            dependent,
            type(r) as relationship_type,
            target
        ORDER BY dependent.name
        """

        parameters = {"target_name": target}

        return cypher, parameters

    def _build_count_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for COUNT_ITEMS queries"""
        if query.target_components:
            labels = "|".join(query.target_components)
            cypher = f"MATCH (n:{labels}) RETURN count(n) as total_count"
        else:
            cypher = """
            MATCH (n)
            RETURN labels(n)[0] as component_type, count(n) as count
            ORDER BY count DESC
            """

        return cypher, {}

    def _build_similarity_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for FIND_SIMILAR queries"""
        if not query.target_components:
            return "MATCH (n) RETURN n LIMIT 10", {}

        target = query.target_components[0]
        limit = query.limit or 10

        cypher = f"""
        MATCH (target)
        WHERE target.name = $target_name OR target.uuid = $target_name
        MATCH (similar)
        WHERE similar <> target
          AND labels(similar) = labels(target)
        OPTIONAL MATCH (target)-[r1]-(common)-[r2]-(similar)
        WITH similar, count(DISTINCT common) as shared_connections
        RETURN similar, shared_connections
        ORDER BY shared_connections DESC
        LIMIT {limit}
        """

        parameters = {"target_name": target}

        return cypher, parameters

    def _build_usage_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for SEARCH_USAGE queries"""
        if query.target_components:
            labels = "|".join(query.target_components)
            cypher = f"""
            MATCH (n:{labels})
            OPTIONAL MATCH (n)-[uses:USES|CONTAINS]-(related)
            RETURN n, count(related) as usage_count
            ORDER BY usage_count DESC
            LIMIT {query.limit or 50}
            """
        else:
            cypher = """
            MATCH (n)-[r]-(related)
            RETURN n, type(r) as relationship_type, count(related) as connection_count
            ORDER BY connection_count DESC
            LIMIT 50
            """

        return cypher, {}

    def _build_generic_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build generic Cypher query"""
        if query.target_components:
            labels = "|".join(query.target_components)
            cypher = f"MATCH (n:{labels}) RETURN n LIMIT {query.limit or 20}"
        else:
            cypher = f"MATCH (n) RETURN n LIMIT {query.limit or 20}"

        return cypher, {}

    def validate_query(self, plc_query: PLCQuery) -> Tuple[bool, List[str]]:
        """
        Validate a PLCQuery for correctness.

        Args:
            plc_query: Query to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check query type
        if not isinstance(plc_query.query_type, QueryType):
            errors.append("Invalid query type")

        # Check component types
        for component in plc_query.target_components:
            valid_types = list(self.component_types.values())
            if component not in valid_types and component not in self.component_types:
                errors.append(f"Unknown component type: {component}")

        # Check relationship types
        for relationship in plc_query.relationships:
            valid_rels = list(self.relationship_types.values())
            if relationship not in valid_rels and relationship not in self.relationship_types:
                errors.append(f"Unknown relationship type: {relationship}")

        # Check filters
        for filter_cond in plc_query.filters:
            if not filter_cond.property_name:
                errors.append("Filter condition missing property name")
            if not isinstance(filter_cond.operator, ComparisonOperator):
                errors.append("Invalid filter operator")

        # Check limits
        if plc_query.limit is not None and plc_query.limit <= 0:
            errors.append("Limit must be positive")

        if plc_query.depth_limit <= 0:
            errors.append("Depth limit must be positive")

        return len(errors) == 0, errors

    def get_query_examples(self) -> Dict[str, List[str]]:
        """Get example queries for each query type"""
        return {
            "Natural Language Examples": [
                "Find all routines that contain timer instructions",
                "Show me AOIs that use UDT_Motor",
                "List programs created after 2023-01-01",
                "Count all devices in the project",
                "Trace connections from Main_Routine",
                "What routines depend on Safety_AOI",
                "Find similar components to Conveyor_Control"
            ],
            "Structured Query Examples": [
                "QueryType.FIND_COMPONENTS with filters on name and type",
                "QueryType.TRACE_CONNECTIONS with depth limit of 3",
                "QueryType.ANALYZE_DEPENDENCIES for specific component",
                "QueryType.COUNT_ITEMS grouped by component type"
            ]
        }

    def clear_cache(self):
        """Clear the query parsing cache"""
        self.query_cache.clear()
        logger.info("Query cache cleared")

# Utility functions
def create_find_query(
    component_type: str,
    name_contains: str = None,
    limit: int = None
) -> PLCQuery:
    """Create a simple find query"""
    dsl = PLCQueryDSL()
    filters = []

    if name_contains:
        filters.append(FilterCondition(
            property_name="name",
            operator=ComparisonOperator.CONTAINS,
            value=name_contains,
            case_sensitive=False
        ))

    return dsl.build_structured_query(
        query_type=QueryType.FIND_COMPONENTS,
        target_components=[component_type],
        filters=filters,
        limit=limit
    )

def create_dependency_query(target_component: str) -> PLCQuery:
    """Create a dependency analysis query"""
    dsl = PLCQueryDSL()
    return dsl.build_structured_query(
        query_type=QueryType.ANALYZE_DEPENDENCIES,
        target_components=[target_component],
        relationships=["USES", "DEPENDS_ON", "CONTAINS"],
        include_relationships=True
    )
