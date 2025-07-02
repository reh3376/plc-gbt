#!/usr/bin/env python3
"""
PLC Query DSL (Domain Specific Language)
Created: January 1, 2025
Purpose: Custom query language for PLC component analysis with natural language support
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

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
    COUNT_ITEMS = "count_items"
    FIND_SIMILAR = "find_similar"

class ComparisonOperator(Enum):
    """Comparison operators for filters"""
    EQUALS = "="
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    GREATER_THAN = ">"
    LESS_THAN = "<"

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
    """Domain Specific Language for PLC queries"""
    
    def __init__(self):
        """Initialize PLC Query DSL"""
        self.component_types = {
            "program": "PLCProgram",
            "programs": "PLCProgram",
            "routine": "Routine", 
            "routines": "Routine",
            "aoi": "AOI",
            "aois": "AOI",
            "udt": "UDT",
            "udts": "UDT",
            "tag": "Tag",
            "tags": "Tag",
            "device": "Device",
            "devices": "Device"
        }
        
        self.nl_patterns = {
            "find_patterns": [
                r"find (?:all )?(\w+)s?\s*(?:that|which|where)?\s*(.*)",
                r"show (?:me )?(?:all )?(\w+)s?\s*(.*)",
                r"list (?:all )?(\w+)s?\s*(.*)"
            ],
            "trace_patterns": [
                r"trace (?:the )?connections? (?:of|from|for) (\w+)",
                r"show (?:the )?connections? (?:of|from|for) (\w+)"
            ],
            "count_patterns": [
                r"count (?:the )?(\w+)s?",
                r"how many (\w+)s?"
            ]
        }
        
        self.query_cache = {}
        logger.info("PLCQueryDSL initialized")
    
    def parse_natural_language(self, query_text: str) -> PLCQuery:
        """Parse natural language query into structured PLCQuery"""
        query_text = query_text.lower().strip()
        
        if query_text in self.query_cache:
            return self.query_cache[query_text]
        
        try:
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
            
            # Count patterns
            if not parsed_query:
                for pattern in self.nl_patterns["count_patterns"]:
                    match = re.search(pattern, query_text, re.IGNORECASE)
                    if match:
                        parsed_query = self._parse_count_query(match)
                        break
            
            # Default fallback
            if not parsed_query:
                parsed_query = PLCQuery(
                    query_type=QueryType.FIND_COMPONENTS,
                    metadata={"original_query": query_text}
                )
            
            self.query_cache[query_text] = parsed_query
            return parsed_query
            
        except Exception as e:
            logger.error("Failed to parse natural language query", error=str(e))
            return PLCQuery(
                query_type=QueryType.FIND_COMPONENTS,
                metadata={"original_query": query_text, "parse_error": str(e)}
            )
    
    def _parse_find_query(self, match: re.Match) -> PLCQuery:
        """Parse find-type queries"""
        component_type = match.group(1)
        conditions = match.group(2) if len(match.groups()) > 1 else ""
        
        mapped_type = self.component_types.get(component_type, component_type)
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
    
    def _parse_count_query(self, match: re.Match) -> PLCQuery:
        """Parse count queries"""
        component_type = match.group(1)
        mapped_type = self.component_types.get(component_type, component_type)
        
        return PLCQuery(
            query_type=QueryType.COUNT_ITEMS,
            target_components=[mapped_type],
            metadata={"count_type": component_type}
        )
    
    def _parse_conditions(self, conditions_text: str) -> List[FilterCondition]:
        """Parse filter conditions from text"""
        filters = []
        
        if "name contains" in conditions_text:
            match = re.search(r"name contains ['\"]?([^'\"]+)['\"]?", conditions_text, re.IGNORECASE)
            if match:
                filters.append(FilterCondition(
                    property_name="name",
                    operator=ComparisonOperator.CONTAINS,
                    value=match.group(1),
                    case_sensitive=False
                ))
        
        return filters
    
    def to_cypher_query(self, plc_query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Convert PLCQuery to Cypher query"""
        try:
            if plc_query.query_type == QueryType.FIND_COMPONENTS:
                return self._build_find_cypher(plc_query)
            elif plc_query.query_type == QueryType.TRACE_CONNECTIONS:
                return self._build_trace_cypher(plc_query)
            elif plc_query.query_type == QueryType.COUNT_ITEMS:
                return self._build_count_cypher(plc_query)
            else:
                return "MATCH (n) RETURN n LIMIT 10", {}
                
        except Exception as e:
            logger.error("Failed to convert to Cypher", error=str(e))
            return "MATCH (n) RETURN n LIMIT 10", {}
    
    def _build_find_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for FIND_COMPONENTS queries"""
        if query.target_components:
            labels = "|".join(query.target_components)
            match_clause = f"MATCH (n:{labels})"
        else:
            match_clause = "MATCH (n)"
        
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
        
        where_clause = f" WHERE {' AND '.join(where_conditions)}" if where_conditions else ""
        return_clause = "RETURN n"
        limit_clause = f" LIMIT {query.limit}" if query.limit else ""
        
        cypher = f"{match_clause}{where_clause}{return_clause}{limit_clause}"
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
        RETURN path, nodes(path) as nodes, relationships(path) as relationships
        LIMIT 100
        """
        
        return cypher, {"target_name": target}
    
    def _build_count_cypher(self, query: PLCQuery) -> Tuple[str, Dict[str, Any]]:
        """Build Cypher for COUNT_ITEMS queries"""
        if query.target_components:
            labels = "|".join(query.target_components)
            cypher = f"MATCH (n:{labels}) RETURN count(n) as total_count"
        else:
            cypher = "MATCH (n) RETURN labels(n)[0] as component_type, count(n) as count ORDER BY count DESC"
        
        return cypher, {}

# Utility functions
def create_find_query(component_type: str, name_contains: str = None) -> PLCQuery:
    """Create a simple find query"""
    filters = []
    if name_contains:
        filters.append(FilterCondition(
            property_name="name",
            operator=ComparisonOperator.CONTAINS,
            value=name_contains,
            case_sensitive=False
        ))
    
    return PLCQuery(
        query_type=QueryType.FIND_COMPONENTS,
        target_components=[component_type],
        filters=filters
    )
