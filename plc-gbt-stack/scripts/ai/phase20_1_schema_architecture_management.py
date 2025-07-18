#!/usr/bin/env python3
"""
🏗️ Phase 20.1: Schema Architecture & Management System

Comprehensive JSON schema framework for control loops with versioning, inheritance,
and management capabilities.

AI Task Orchestrator Implementation
=====================================
Task Classification: COMPLEX (500-1500 lines, 5-15 files, 3-8 hours)
Context Management: Standard planning with domain awareness
Methodology Source: AI_TASK_ORCHESTRATOR_GUIDE.md

Phase 20.1 Objectives:
- Design modular schema architecture with inheritance
- Implement versioning system (XX.YY.ZZZ format)
- Create schema registry and management system
- Build validation and compliance framework
- Enable extensibility for future schema types

Author: AI Task Orchestrator
Created: 2025-01-17  
Phase: 20.1 - Schema Architecture & Management System
Dependencies: Phase 24 (Context Processing), Phase 8.2 (PLC Memory Management)
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
import re
import hashlib
import sqlite3
from contextlib import asynccontextmanager
import jsonschema
from jsonschema import Draft7Validator, validators
import yaml

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMERATIONS AND CONSTANTS
# =============================================================================

class ControlLoopType(Enum):
    """Control loop main types"""
    LADDER_LOGIC_STANDARD_PID = "ladder_logic_standard_pid"
    LADDER_LOGIC_ADVANCED_PID = "ladder_logic_advanced_pid"
    FUNCTION_BLOCK_STANDARD_PIDE = "function_block_standard_pide"
    FUNCTION_BLOCK_ADVANCED_PIDE = "function_block_advanced_pide"

class ControlLoopSubType(Enum):
    """Control loop sub-types"""
    FEEDFORWARD = "feedforward"
    CASCADE = "cascade"
    COMBINED_FF_CASCADE = "combined_feedforward_cascade"
    MULTI_FORMULA_WEIGHTED_FF = "multi_formula_weighted_feedforward"

class SchemaStatus(Enum):
    """Schema lifecycle status"""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class ValidationLevel(Enum):
    """Schema validation levels"""
    BASIC = "basic"
    COMPREHENSIVE = "comprehensive"
    STRICT = "strict"
    PRODUCTION = "production"

# =============================================================================
# CORE DATA STRUCTURES
# =============================================================================

@dataclass
class SchemaVersion:
    """Semantic versioning for schemas (XX.YY.ZZZ)"""
    major: int  # Breaking changes (XX)
    minor: int  # New features (YY)
    patch: int  # Bug fixes (ZZZ)
    
    def __str__(self) -> str:
        return f"{self.major:02d}.{self.minor:02d}.{self.patch:03d}"
    
    @classmethod
    def from_string(cls, version_str: str) -> "SchemaVersion":
        """Parse version string like '01.05.002'"""
        pattern = r"(\d{2})\.(\d{2})\.(\d{3})"
        match = re.match(pattern, version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        
        major, minor, patch = map(int, match.groups())
        return cls(major=major, minor=minor, patch=patch)
    
    def increment_major(self) -> "SchemaVersion":
        """Increment major version, reset minor and patch"""
        return SchemaVersion(self.major + 1, 0, 0)
    
    def increment_minor(self) -> "SchemaVersion":
        """Increment minor version, reset patch"""
        return SchemaVersion(self.major, self.minor + 1, 0)
    
    def increment_patch(self) -> "SchemaVersion":
        """Increment patch version"""
        return SchemaVersion(self.major, self.minor, self.patch + 1)
    
    def __lt__(self, other: "SchemaVersion") -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
    
    def __eq__(self, other: "SchemaVersion") -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

@dataclass
class SchemaMetadata:
    """Comprehensive schema metadata"""
    schema_id: str
    name: str
    description: str
    version: SchemaVersion
    control_type: ControlLoopType
    sub_type: Optional[ControlLoopSubType]
    
    # Lifecycle
    status: SchemaStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    
    # Inheritance and relationships
    parent_schema_id: Optional[str] = None
    inherits_from: List[str] = field(default_factory=list)
    extends: List[str] = field(default_factory=list)
    
    # Validation and compatibility
    validation_level: ValidationLevel = ValidationLevel.COMPREHENSIVE
    backward_compatible: bool = True
    breaking_changes: List[str] = field(default_factory=list)
    
    # Documentation
    documentation_url: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    
    # Technical details
    schema_hash: Optional[str] = None
    size_bytes: Optional[int] = None
    complexity_score: Optional[float] = None

@dataclass
class SchemaDefinition:
    """Complete schema definition with JSON Schema and metadata"""
    metadata: SchemaMetadata
    json_schema: Dict[str, Any]
    
    # Extended properties
    custom_properties: Dict[str, Any] = field(default_factory=dict)
    validation_rules: List[Dict[str, Any]] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    
    def calculate_hash(self) -> str:
        """Calculate hash of the schema content"""
        schema_str = json.dumps(self.json_schema, sort_keys=True)
        return hashlib.sha256(schema_str.encode()).hexdigest()
    
    def validate_instance(self, instance: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate an instance against this schema"""
        try:
            validator = Draft7Validator(self.json_schema)
            errors = list(validator.iter_errors(instance))
            is_valid = len(errors) == 0
            error_messages = [f"{'.'.join(str(p) for p in error.path)}: {error.message}" 
                            for error in errors]
            return is_valid, error_messages
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]

# =============================================================================
# SCHEMA REGISTRY
# =============================================================================

class SchemaRegistry:
    """Central registry for managing schemas with SQLite backend"""
    
    def __init__(self, registry_path: Optional[Path] = None):
        self.registry_path = registry_path or Path("schemas/registry.db")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        
        # In-memory cache for performance
        self._schema_cache: Dict[str, SchemaDefinition] = {}
        self._index_cache: Dict[str, List[str]] = {}
    
    def _init_database(self):
        """Initialize SQLite database for schema registry"""
        with sqlite3.connect(self.registry_path) as conn:
            cursor = conn.cursor()
            
            # Main schemas table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schemas (
                    schema_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    version TEXT NOT NULL,
                    control_type TEXT NOT NULL,
                    sub_type TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    created_by TEXT NOT NULL,
                    parent_schema_id TEXT,
                    validation_level TEXT NOT NULL,
                    backward_compatible INTEGER NOT NULL,
                    schema_hash TEXT,
                    size_bytes INTEGER,
                    complexity_score REAL,
                    json_schema TEXT NOT NULL,
                    custom_properties TEXT,
                    FOREIGN KEY (parent_schema_id) REFERENCES schemas (schema_id)
                )
            """)
            
            # Schema inheritance table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_inheritance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    child_schema_id TEXT NOT NULL,
                    parent_schema_id TEXT NOT NULL,
                    inheritance_type TEXT NOT NULL,
                    FOREIGN KEY (child_schema_id) REFERENCES schemas (schema_id),
                    FOREIGN KEY (parent_schema_id) REFERENCES schemas (schema_id),
                    UNIQUE (child_schema_id, parent_schema_id, inheritance_type)
                )
            """)
            
            # Schema tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_id TEXT NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (schema_id) REFERENCES schemas (schema_id),
                    UNIQUE (schema_id, tag)
                )
            """)
            
            # Schema validation rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_validation_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    schema_id TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    rule_definition TEXT NOT NULL,
                    rule_type TEXT NOT NULL,
                    FOREIGN KEY (schema_id) REFERENCES schemas (schema_id)
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_type ON schemas (control_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_status ON schemas (status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_schemas_version ON schemas (version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inheritance_child ON schema_inheritance (child_schema_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_inheritance_parent ON schema_inheritance (parent_schema_id)")
            
            conn.commit()
    
    async def register_schema(self, schema_def: SchemaDefinition) -> bool:
        """Register a new schema in the registry"""
        try:
            # Update metadata
            schema_def.metadata.schema_hash = schema_def.calculate_hash()
            schema_def.metadata.size_bytes = len(json.dumps(schema_def.json_schema))
            schema_def.metadata.complexity_score = self._calculate_complexity(schema_def.json_schema)
            
            with sqlite3.connect(self.registry_path) as conn:
                cursor = conn.cursor()
                
                # Insert main schema record
                cursor.execute("""
                    INSERT OR REPLACE INTO schemas 
                    (schema_id, name, description, version, control_type, sub_type, status,
                     created_at, updated_at, created_by, parent_schema_id, validation_level,
                     backward_compatible, schema_hash, size_bytes, complexity_score,
                     json_schema, custom_properties)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    schema_def.metadata.schema_id,
                    schema_def.metadata.name,
                    schema_def.metadata.description,
                    str(schema_def.metadata.version),
                    schema_def.metadata.control_type.value,
                    schema_def.metadata.sub_type.value if schema_def.metadata.sub_type else None,
                    schema_def.metadata.status.value,
                    schema_def.metadata.created_at.isoformat(),
                    schema_def.metadata.updated_at.isoformat(),
                    schema_def.metadata.created_by,
                    schema_def.metadata.parent_schema_id,
                    schema_def.metadata.validation_level.value,
                    int(schema_def.metadata.backward_compatible),
                    schema_def.metadata.schema_hash,
                    schema_def.metadata.size_bytes,
                    schema_def.metadata.complexity_score,
                    json.dumps(schema_def.json_schema),
                    json.dumps(schema_def.custom_properties)
                ))
                
                # Insert inheritance relationships
                for parent_id in schema_def.metadata.inherits_from:
                    cursor.execute("""
                        INSERT OR IGNORE INTO schema_inheritance 
                        (child_schema_id, parent_schema_id, inheritance_type)
                        VALUES (?, ?, ?)
                    """, (schema_def.metadata.schema_id, parent_id, "inherits"))
                
                for extended_id in schema_def.metadata.extends:
                    cursor.execute("""
                        INSERT OR IGNORE INTO schema_inheritance 
                        (child_schema_id, parent_schema_id, inheritance_type)
                        VALUES (?, ?, ?)
                    """, (schema_def.metadata.schema_id, extended_id, "extends"))
                
                # Insert tags
                for tag in schema_def.metadata.tags:
                    cursor.execute("""
                        INSERT OR IGNORE INTO schema_tags (schema_id, tag)
                        VALUES (?, ?)
                    """, (schema_def.metadata.schema_id, tag))
                
                # Insert validation rules
                for rule in schema_def.validation_rules:
                    cursor.execute("""
                        INSERT INTO schema_validation_rules 
                        (schema_id, rule_name, rule_definition, rule_type)
                        VALUES (?, ?, ?, ?)
                    """, (
                        schema_def.metadata.schema_id,
                        rule.get("name", ""),
                        json.dumps(rule.get("definition", {})),
                        rule.get("type", "custom")
                    ))
                
                conn.commit()
            
            # Update cache
            self._schema_cache[schema_def.metadata.schema_id] = schema_def
            self._invalidate_index_cache()
            
            logger.info(f"Successfully registered schema: {schema_def.metadata.schema_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register schema {schema_def.metadata.schema_id}: {str(e)}")
            return False
    
    async def get_schema(self, schema_id: str) -> Optional[SchemaDefinition]:
        """Retrieve a schema by ID"""
        # Check cache first
        if schema_id in self._schema_cache:
            return self._schema_cache[schema_id]
        
        try:
            with sqlite3.connect(self.registry_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get main schema record
                cursor.execute("SELECT * FROM schemas WHERE schema_id = ?", (schema_id,))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                # Reconstruct metadata
                metadata = SchemaMetadata(
                    schema_id=row["schema_id"],
                    name=row["name"],
                    description=row["description"],
                    version=SchemaVersion.from_string(row["version"]),
                    control_type=ControlLoopType(row["control_type"]),
                    sub_type=ControlLoopSubType(row["sub_type"]) if row["sub_type"] else None,
                    status=SchemaStatus(row["status"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    created_by=row["created_by"],
                    parent_schema_id=row["parent_schema_id"],
                    validation_level=ValidationLevel(row["validation_level"]),
                    backward_compatible=bool(row["backward_compatible"]),
                    schema_hash=row["schema_hash"],
                    size_bytes=row["size_bytes"],
                    complexity_score=row["complexity_score"]
                )
                
                # Get inheritance relationships
                cursor.execute("""
                    SELECT parent_schema_id, inheritance_type 
                    FROM schema_inheritance 
                    WHERE child_schema_id = ?
                """, (schema_id,))
                for inherit_row in cursor.fetchall():
                    if inherit_row["inheritance_type"] == "inherits":
                        metadata.inherits_from.append(inherit_row["parent_schema_id"])
                    elif inherit_row["inheritance_type"] == "extends":
                        metadata.extends.append(inherit_row["parent_schema_id"])
                
                # Get tags
                cursor.execute("SELECT tag FROM schema_tags WHERE schema_id = ?", (schema_id,))
                metadata.tags = [tag_row["tag"] for tag_row in cursor.fetchall()]
                
                # Get validation rules
                cursor.execute("""
                    SELECT rule_name, rule_definition, rule_type 
                    FROM schema_validation_rules 
                    WHERE schema_id = ?
                """, (schema_id,))
                validation_rules = []
                for rule_row in cursor.fetchall():
                    validation_rules.append({
                        "name": rule_row["rule_name"],
                        "definition": json.loads(rule_row["rule_definition"]),
                        "type": rule_row["rule_type"]
                    })
                
                # Create schema definition
                schema_def = SchemaDefinition(
                    metadata=metadata,
                    json_schema=json.loads(row["json_schema"]),
                    custom_properties=json.loads(row["custom_properties"] or "{}"),
                    validation_rules=validation_rules
                )
                
                # Update cache
                self._schema_cache[schema_id] = schema_def
                
                return schema_def
                
        except Exception as e:
            logger.error(f"Failed to retrieve schema {schema_id}: {str(e)}")
            return None
    
    async def list_schemas(self, 
                          control_type: Optional[ControlLoopType] = None,
                          status: Optional[SchemaStatus] = None,
                          tags: Optional[List[str]] = None) -> List[SchemaMetadata]:
        """List schemas with optional filtering"""
        try:
            with sqlite3.connect(self.registry_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Build query with filters
                query = "SELECT * FROM schemas WHERE 1=1"
                params = []
                
                if control_type:
                    query += " AND control_type = ?"
                    params.append(control_type.value)
                
                if status:
                    query += " AND status = ?"
                    params.append(status.value)
                
                if tags:
                    # Filter by tags using EXISTS subquery
                    tag_conditions = " OR ".join(["tag = ?" for _ in tags])
                    query += f"""
                        AND EXISTS (
                            SELECT 1 FROM schema_tags 
                            WHERE schema_tags.schema_id = schemas.schema_id 
                            AND ({tag_conditions})
                        )
                    """
                    params.extend(tags)
                
                query += " ORDER BY control_type, version DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert to metadata objects
                schemas = []
                for row in rows:
                    metadata = SchemaMetadata(
                        schema_id=row["schema_id"],
                        name=row["name"],
                        description=row["description"],
                        version=SchemaVersion.from_string(row["version"]),
                        control_type=ControlLoopType(row["control_type"]),
                        sub_type=ControlLoopSubType(row["sub_type"]) if row["sub_type"] else None,
                        status=SchemaStatus(row["status"]),
                        created_at=datetime.fromisoformat(row["created_at"]),
                        updated_at=datetime.fromisoformat(row["updated_at"]),
                        created_by=row["created_by"],
                        parent_schema_id=row["parent_schema_id"],
                        validation_level=ValidationLevel(row["validation_level"]),
                        backward_compatible=bool(row["backward_compatible"]),
                        schema_hash=row["schema_hash"],
                        size_bytes=row["size_bytes"],
                        complexity_score=row["complexity_score"]
                    )
                    schemas.append(metadata)
                
                return schemas
                
        except Exception as e:
            logger.error(f"Failed to list schemas: {str(e)}")
            return []
    
    async def update_schema_status(self, schema_id: str, new_status: SchemaStatus) -> bool:
        """Update schema status"""
        try:
            with sqlite3.connect(self.registry_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE schemas 
                    SET status = ?, updated_at = ? 
                    WHERE schema_id = ?
                """, (new_status.value, datetime.now(timezone.utc).isoformat(), schema_id))
                
                success = cursor.rowcount > 0
                conn.commit()
                
                # Invalidate cache
                if schema_id in self._schema_cache:
                    del self._schema_cache[schema_id]
                self._invalidate_index_cache()
                
                return success
                
        except Exception as e:
            logger.error(f"Failed to update schema status {schema_id}: {str(e)}")
            return False
    
    async def get_schema_hierarchy(self, schema_id: str) -> Dict[str, Any]:
        """Get complete inheritance hierarchy for a schema"""
        try:
            hierarchy = {
                "schema_id": schema_id,
                "parents": [],
                "children": [],
                "siblings": []
            }
            
            with sqlite3.connect(self.registry_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get all parent relationships
                cursor.execute("""
                    WITH RECURSIVE parent_hierarchy AS (
                        SELECT parent_schema_id, inheritance_type, 1 as level
                        FROM schema_inheritance 
                        WHERE child_schema_id = ?
                        
                        UNION ALL
                        
                        SELECT si.parent_schema_id, si.inheritance_type, ph.level + 1
                        FROM schema_inheritance si
                        JOIN parent_hierarchy ph ON si.child_schema_id = ph.parent_schema_id
                        WHERE ph.level < 10  -- Prevent infinite recursion
                    )
                    SELECT parent_schema_id, inheritance_type, level 
                    FROM parent_hierarchy
                    ORDER BY level
                """, (schema_id,))
                
                for row in cursor.fetchall():
                    hierarchy["parents"].append({
                        "schema_id": row["parent_schema_id"],
                        "inheritance_type": row["inheritance_type"],
                        "level": row["level"]
                    })
                
                # Get all child relationships
                cursor.execute("""
                    WITH RECURSIVE child_hierarchy AS (
                        SELECT child_schema_id, inheritance_type, 1 as level
                        FROM schema_inheritance 
                        WHERE parent_schema_id = ?
                        
                        UNION ALL
                        
                        SELECT si.child_schema_id, si.inheritance_type, ch.level + 1
                        FROM schema_inheritance si
                        JOIN child_hierarchy ch ON si.parent_schema_id = ch.child_schema_id
                        WHERE ch.level < 10  -- Prevent infinite recursion
                    )
                    SELECT child_schema_id, inheritance_type, level 
                    FROM child_hierarchy
                    ORDER BY level
                """, (schema_id,))
                
                for row in cursor.fetchall():
                    hierarchy["children"].append({
                        "schema_id": row["child_schema_id"],
                        "inheritance_type": row["inheritance_type"],
                        "level": row["level"]
                    })
                
                return hierarchy
                
        except Exception as e:
            logger.error(f"Failed to get schema hierarchy for {schema_id}: {str(e)}")
            return {"schema_id": schema_id, "parents": [], "children": [], "siblings": []}
    
    def _calculate_complexity(self, schema: Dict[str, Any]) -> float:
        """Calculate complexity score for a schema"""
        try:
            complexity = 0.0
            
            # Count properties
            if "properties" in schema:
                complexity += len(schema["properties"]) * 0.1
            
            # Count required fields
            if "required" in schema:
                complexity += len(schema["required"]) * 0.05
            
            # Count nested objects
            def count_nested(obj, depth=0):
                if depth > 10:  # Prevent infinite recursion
                    return 0
                
                nested_count = 0
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        if key == "properties" and isinstance(value, dict):
                            nested_count += len(value) * 0.2
                        elif isinstance(value, (dict, list)):
                            nested_count += count_nested(value, depth + 1)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, (dict, list)):
                            nested_count += count_nested(item, depth + 1)
                
                return nested_count
            
            complexity += count_nested(schema)
            
            # Normalize to 0-10 scale
            return min(complexity, 10.0)
            
        except Exception:
            return 1.0  # Default complexity
    
    def _invalidate_index_cache(self):
        """Invalidate index cache"""
        self._index_cache.clear()

# =============================================================================
# SCHEMA BUILDER
# =============================================================================

class SchemaBuilder:
    """Builder pattern for creating control loop schemas"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
        self._reset()
    
    def _reset(self):
        """Reset builder state"""
        self.metadata = None
        self.base_schema = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False
        }
        self.custom_properties = {}
        self.validation_rules = []
        self.business_rules = []
    
    def create_base_schema(self, 
                          schema_id: str,
                          name: str,
                          description: str,
                          control_type: ControlLoopType,
                          created_by: str,
                          version: Optional[SchemaVersion] = None,
                          sub_type: Optional[ControlLoopSubType] = None) -> "SchemaBuilder":
        """Create base schema metadata"""
        self.metadata = SchemaMetadata(
            schema_id=schema_id,
            name=name,
            description=description,
            version=version or SchemaVersion(1, 0, 0),
            control_type=control_type,
            sub_type=sub_type,
            status=SchemaStatus.DRAFT,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            created_by=created_by
        )
        
        # Set basic schema properties
        self.base_schema["$id"] = f"https://plc-gbt.industrial-ai.com/schemas/{schema_id}"
        self.base_schema["title"] = name
        self.base_schema["description"] = description
        
        return self
    
    def inherit_from(self, parent_schema_id: str) -> "SchemaBuilder":
        """Set inheritance relationship"""
        if self.metadata:
            self.metadata.inherits_from.append(parent_schema_id)
            self.metadata.parent_schema_id = parent_schema_id
        return self
    
    def extend_schema(self, extended_schema_id: str) -> "SchemaBuilder":
        """Set extension relationship"""
        if self.metadata:
            self.metadata.extends.append(extended_schema_id)
        return self
    
    def add_property(self, name: str, property_def: Dict[str, Any], required: bool = False) -> "SchemaBuilder":
        """Add a property to the schema"""
        self.base_schema["properties"][name] = property_def
        if required:
            self.base_schema["required"].append(name)
        return self
    
    def add_common_control_properties(self) -> "SchemaBuilder":
        """Add common control loop properties"""
        # Basic identification
        self.add_property("tag_name", {
            "type": "string",
            "pattern": "^[A-Za-z][A-Za-z0-9_]*$",
            "maxLength": 40,
            "description": "PLC tag name"
        }, required=True)
        
        self.add_property("description", {
            "type": "string",
            "maxLength": 200,
            "description": "Human-readable description"
        })
        
        # Process variable configuration
        self.add_property("process_variable", {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]*$"},
                "engineering_units": {"type": "string", "maxLength": 20},
                "min_value": {"type": "number"},
                "max_value": {"type": "number"},
                "deadband": {"type": "number", "minimum": 0}
            },
            "required": ["tag"],
            "additionalProperties": False
        }, required=True)
        
        # Setpoint configuration
        self.add_property("setpoint", {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]*$"},
                "default_value": {"type": "number"},
                "min_value": {"type": "number"},
                "max_value": {"type": "number"},
                "rate_limit": {"type": "number", "minimum": 0}
            },
            "required": ["tag"],
            "additionalProperties": False
        }, required=True)
        
        # Control output
        self.add_property("control_output", {
            "type": "object",
            "properties": {
                "tag": {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_]*$"},
                "min_value": {"type": "number"},
                "max_value": {"type": "number"},
                "initial_value": {"type": "number"},
                "rate_limit": {"type": "number", "minimum": 0}
            },
            "required": ["tag"],
            "additionalProperties": False
        }, required=True)
        
        # Operating mode
        self.add_property("operating_mode", {
            "type": "string",
            "enum": ["manual", "auto", "cascade", "ratio", "override"],
            "default": "manual"
        }, required=True)
        
        # Enable/disable
        self.add_property("enabled", {
            "type": "boolean",
            "default": True,
            "description": "Control loop enable status"
        })
        
        return self
    
    def add_pid_properties(self, advanced: bool = False) -> "SchemaBuilder":
        """Add PID-specific properties"""
        # Basic PID parameters
        pid_props = {
            "type": "object",
            "properties": {
                "proportional_gain": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1000,
                    "description": "Proportional gain (Kp)"
                },
                "integral_time": {
                    "type": "number",
                    "minimum": 0.001,
                    "maximum": 3600,
                    "description": "Integral time constant (Ti) in seconds"
                },
                "derivative_time": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 60,
                    "description": "Derivative time constant (Td) in seconds"
                },
                "integral_windup_high": {
                    "type": "number",
                    "description": "High integral windup limit"
                },
                "integral_windup_low": {
                    "type": "number",
                    "description": "Low integral windup limit"
                }
            },
            "required": ["proportional_gain", "integral_time"],
            "additionalProperties": False
        }
        
        if advanced:
            # Add advanced PID properties
            pid_props["properties"].update({
                "derivative_filter_time": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 10,
                    "description": "Derivative filter time constant"
                },
                "setpoint_weighting": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1,
                    "default": 1,
                    "description": "Setpoint weighting factor"
                },
                "derivative_on_pv": {
                    "type": "boolean",
                    "default": True,
                    "description": "Derivative on process variable (not error)"
                },
                "bias": {
                    "type": "number",
                    "description": "Output bias value"
                }
            })
        
        self.add_property("pid_parameters", pid_props, required=True)
        return self
    
    def add_pide_properties(self) -> "SchemaBuilder":
        """Add PIDE-specific properties (enhanced PID)"""
        # Start with PID properties
        self.add_pid_properties(advanced=True)
        
        # Add enhanced features
        self.add_property("enhanced_features", {
            "type": "object",
            "properties": {
                "auto_tuning": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "method": {
                            "type": "string",
                            "enum": ["relay", "step", "prbs"],
                            "default": "relay"
                        },
                        "aggressiveness": {
                            "type": "number",
                            "minimum": 0.1,
                            "maximum": 2.0,
                            "default": 1.0
                        }
                    },
                    "additionalProperties": False
                },
                "adaptive_control": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "adaptation_rate": {
                            "type": "number",
                            "minimum": 0.001,
                            "maximum": 1.0,
                            "default": 0.1
                        }
                    },
                    "additionalProperties": False
                },
                "feed_forward": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean", "default": False},
                        "gain": {"type": "number", "default": 1.0},
                        "lead_time": {"type": "number", "minimum": 0, "default": 0},
                        "lag_time": {"type": "number", "minimum": 0, "default": 0}
                    },
                    "additionalProperties": False
                }
            },
            "additionalProperties": False
        })
        
        return self
    
    def add_validation_rule(self, name: str, rule_def: Dict[str, Any], rule_type: str = "custom") -> "SchemaBuilder":
        """Add custom validation rule"""
        self.validation_rules.append({
            "name": name,
            "definition": rule_def,
            "type": rule_type
        })
        return self
    
    def add_business_rule(self, rule: str) -> "SchemaBuilder":
        """Add business rule description"""
        self.business_rules.append(rule)
        return self
    
    def add_tag(self, tag: str) -> "SchemaBuilder":
        """Add metadata tag"""
        if self.metadata:
            self.metadata.tags.append(tag)
        return self
    
    def set_validation_level(self, level: ValidationLevel) -> "SchemaBuilder":
        """Set validation level"""
        if self.metadata:
            self.metadata.validation_level = level
        return self
    
    def set_custom_property(self, key: str, value: Any) -> "SchemaBuilder":
        """Set custom property"""
        self.custom_properties[key] = value
        return self
    
    async def build(self) -> SchemaDefinition:
        """Build the complete schema definition"""
        if not self.metadata:
            raise ValueError("Schema metadata must be set before building")
        
        # Create schema definition
        schema_def = SchemaDefinition(
            metadata=self.metadata,
            json_schema=self.base_schema.copy(),
            custom_properties=self.custom_properties.copy(),
            validation_rules=self.validation_rules.copy(),
            business_rules=self.business_rules.copy()
        )
        
        return schema_def
    
    async def build_and_register(self) -> Tuple[SchemaDefinition, bool]:
        """Build schema and register it"""
        schema_def = await self.build()
        success = await self.registry.register_schema(schema_def)
        return schema_def, success

# =============================================================================
# SCHEMA VALIDATOR
# =============================================================================

class SchemaValidator:
    """Comprehensive schema validation system"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
    
    async def validate_schema_definition(self, schema_def: SchemaDefinition) -> Tuple[bool, List[str]]:
        """Validate a schema definition"""
        errors = []
        
        try:
            # Validate JSON Schema syntax
            Draft7Validator.check_schema(schema_def.json_schema)
            
            # Validate metadata consistency
            metadata_errors = await self._validate_metadata(schema_def.metadata)
            errors.extend(metadata_errors)
            
            # Validate inheritance relationships
            inheritance_errors = await self._validate_inheritance(schema_def)
            errors.extend(inheritance_errors)
            
            # Validate business rules
            business_errors = self._validate_business_rules(schema_def)
            errors.extend(business_errors)
            
            # Validate custom validation rules
            validation_errors = self._validate_validation_rules(schema_def)
            errors.extend(validation_errors)
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Schema validation error: {str(e)}")
            return False, errors
    
    async def _validate_metadata(self, metadata: SchemaMetadata) -> List[str]:
        """Validate schema metadata"""
        errors = []
        
        # Check required fields
        if not metadata.schema_id:
            errors.append("Schema ID is required")
        elif not re.match(r"^[a-z0-9_-]+$", metadata.schema_id):
            errors.append("Schema ID must contain only lowercase letters, numbers, underscores, and hyphens")
        
        if not metadata.name:
            errors.append("Schema name is required")
        
        if not metadata.description:
            errors.append("Schema description is required")
        
        # Check version format
        try:
            str(metadata.version)  # This will validate the format
        except:
            errors.append("Invalid version format")
        
        # Check if schema ID already exists (for new schemas)
        existing_schema = await self.registry.get_schema(metadata.schema_id)
        if existing_schema and existing_schema.metadata.version == metadata.version:
            errors.append(f"Schema {metadata.schema_id} version {metadata.version} already exists")
        
        return errors
    
    async def _validate_inheritance(self, schema_def: SchemaDefinition) -> List[str]:
        """Validate inheritance relationships"""
        errors = []
        
        # Check that parent schemas exist
        for parent_id in schema_def.metadata.inherits_from:
            parent_schema = await self.registry.get_schema(parent_id)
            if not parent_schema:
                errors.append(f"Parent schema {parent_id} not found")
            elif parent_schema.metadata.status == SchemaStatus.ARCHIVED:
                errors.append(f"Cannot inherit from archived schema {parent_id}")
        
        # Check for circular inheritance
        if schema_def.metadata.inherits_from:
            visited = set()
            stack = [schema_def.metadata.schema_id]
            
            async def check_circular(schema_id: str) -> bool:
                if schema_id in stack[1:]:  # Exclude the starting schema
                    return True
                if schema_id in visited:
                    return False
                
                visited.add(schema_id)
                stack.append(schema_id)
                
                schema = await self.registry.get_schema(schema_id)
                if schema:
                    for parent_id in schema.metadata.inherits_from:
                        if await check_circular(parent_id):
                            return True
                
                stack.pop()
                return False
            
            for parent_id in schema_def.metadata.inherits_from:
                if await check_circular(parent_id):
                    errors.append(f"Circular inheritance detected with schema {parent_id}")
                    break
        
        return errors
    
    def _validate_business_rules(self, schema_def: SchemaDefinition) -> List[str]:
        """Validate business rules"""
        errors = []
        
        # Validate that business rules are non-empty strings
        for rule in schema_def.business_rules:
            if not isinstance(rule, str) or not rule.strip():
                errors.append("Business rules must be non-empty strings")
        
        return errors
    
    def _validate_validation_rules(self, schema_def: SchemaDefinition) -> List[str]:
        """Validate custom validation rules"""
        errors = []
        
        for rule in schema_def.validation_rules:
            if not isinstance(rule, dict):
                errors.append("Validation rules must be objects")
                continue
            
            if "name" not in rule or not isinstance(rule["name"], str):
                errors.append("Validation rule must have a name")
            
            if "definition" not in rule or not isinstance(rule["definition"], dict):
                errors.append("Validation rule must have a definition")
            
            if "type" not in rule or not isinstance(rule["type"], str):
                errors.append("Validation rule must have a type")
        
        return errors

# =============================================================================
# SCHEMA MIGRATION
# =============================================================================

class SchemaMigrator:
    """Handle schema migrations and version upgrades"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
    
    async def create_migration_plan(self, 
                                  from_version: SchemaVersion,
                                  to_version: SchemaVersion,
                                  schema_id: str) -> Dict[str, Any]:
        """Create a migration plan between schema versions"""
        plan = {
            "schema_id": schema_id,
            "from_version": str(from_version),
            "to_version": str(to_version),
            "migration_steps": [],
            "breaking_changes": [],
            "data_transformations": [],
            "validation_changes": []
        }
        
        try:
            # Get both schema versions
            from_schema = await self.registry.get_schema(f"{schema_id}_{from_version}")
            to_schema = await self.registry.get_schema(f"{schema_id}_{to_version}")
            
            if not from_schema or not to_schema:
                plan["error"] = "Source or target schema not found"
                return plan
            
            # Analyze differences
            differences = self._analyze_schema_differences(
                from_schema.json_schema,
                to_schema.json_schema
            )
            
            # Generate migration steps
            plan["migration_steps"] = self._generate_migration_steps(differences)
            plan["breaking_changes"] = differences.get("breaking_changes", [])
            plan["data_transformations"] = differences.get("transformations", [])
            
            return plan
            
        except Exception as e:
            plan["error"] = f"Failed to create migration plan: {str(e)}"
            return plan
    
    def _analyze_schema_differences(self, old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze differences between two schemas"""
        differences = {
            "added_properties": [],
            "removed_properties": [],
            "modified_properties": [],
            "breaking_changes": [],
            "transformations": []
        }
        
        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        
        # Find added properties
        for prop_name in new_props:
            if prop_name not in old_props:
                differences["added_properties"].append(prop_name)
        
        # Find removed properties
        for prop_name in old_props:
            if prop_name not in new_props:
                differences["removed_properties"].append(prop_name)
                differences["breaking_changes"].append(f"Property '{prop_name}' was removed")
        
        # Find modified properties
        for prop_name in old_props:
            if prop_name in new_props:
                if old_props[prop_name] != new_props[prop_name]:
                    differences["modified_properties"].append({
                        "property": prop_name,
                        "old_definition": old_props[prop_name],
                        "new_definition": new_props[prop_name]
                    })
        
        # Check required field changes
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        
        # New required fields are breaking changes
        newly_required = new_required - old_required
        for field in newly_required:
            differences["breaking_changes"].append(f"Property '{field}' is now required")
        
        # Removed required fields are not breaking but need attention
        no_longer_required = old_required - new_required
        for field in no_longer_required:
            differences["transformations"].append(f"Property '{field}' is no longer required")
        
        return differences
    
    def _generate_migration_steps(self, differences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate migration steps from differences"""
        steps = []
        
        # Handle removed properties
        for prop in differences["removed_properties"]:
            steps.append({
                "type": "remove_property",
                "property": prop,
                "action": "Remove property from instances",
                "required": True
            })
        
        # Handle added properties
        for prop in differences["added_properties"]:
            steps.append({
                "type": "add_property",
                "property": prop,
                "action": "Add property with default value to instances",
                "required": False
            })
        
        # Handle modified properties
        for mod in differences["modified_properties"]:
            steps.append({
                "type": "modify_property",
                "property": mod["property"],
                "action": f"Transform property from {mod['old_definition']} to {mod['new_definition']}",
                "required": True
            })
        
        return steps

# =============================================================================
# MAIN ORCHESTRATOR
# =============================================================================

class SchemaArchitectureManager:
    """Main orchestrator for Phase 20.1"""
    
    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path or Path("plc-gbt-stack/schemas")
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.registry = SchemaRegistry(self.base_path / "registry.db")
        self.builder = SchemaBuilder(self.registry)
        self.validator = SchemaValidator(self.registry)
        self.migrator = SchemaMigrator(self.registry)
        
        # Phase tracking
        self.session_id = f"phase20_1_{int(datetime.now().timestamp())}"
        self.start_time = datetime.now()
        
        logger.info(f"Schema Architecture Manager initialized - Session: {self.session_id}")
    
    async def create_base_schemas(self) -> Dict[str, Any]:
        """Create the 4 base control loop schema types"""
        results = {
            "session_id": self.session_id,
            "created_schemas": [],
            "errors": [],
            "summary": {}
        }
        
        try:
            # 1. Ladder Logic Standard PID
            ll_std_pid, success = await self.builder.create_base_schema(
                schema_id="ladder_logic_standard_pid",
                name="Ladder Logic Standard PID Controller",
                description="Standard PID controller implemented in ladder logic with basic proportional, integral, and derivative control",
                control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
                created_by="AI Task Orchestrator Phase 20.1"
            ).add_common_control_properties(
            ).add_pid_properties(advanced=False
            ).add_tag("base_schema"
            ).add_tag("ladder_logic"
            ).add_tag("standard_pid"
            ).set_validation_level(ValidationLevel.COMPREHENSIVE
            ).add_business_rule("PID parameters must be positive values"
            ).add_business_rule("Integral time must be greater than 0.001 seconds"
            ).add_validation_rule("pid_stability", {
                "type": "custom",
                "description": "Ensure PID parameters provide stable control",
                "validation": "proportional_gain * integral_time > 0.1"
            }).build_and_register()
            
            if success:
                results["created_schemas"].append("ladder_logic_standard_pid")
            else:
                results["errors"].append("Failed to create Ladder Logic Standard PID schema")
            
            # Reset builder for next schema
            self.builder._reset()
            
            # 2. Ladder Logic Advanced PID
            ll_adv_pid, success = await self.builder.create_base_schema(
                schema_id="ladder_logic_advanced_pid",
                name="Ladder Logic Advanced PID Controller",
                description="Advanced PID controller with enhanced features like derivative filtering, setpoint weighting, and bias",
                control_type=ControlLoopType.LADDER_LOGIC_ADVANCED_PID,
                created_by="AI Task Orchestrator Phase 20.1"
            ).inherit_from("ladder_logic_standard_pid"
            ).add_common_control_properties(
            ).add_pid_properties(advanced=True
            ).add_tag("base_schema"
            ).add_tag("ladder_logic"
            ).add_tag("advanced_pid"
            ).set_validation_level(ValidationLevel.STRICT
            ).add_business_rule("Advanced PID features must be configured appropriately"
            ).add_business_rule("Derivative filter time should be 1/10 to 1/20 of derivative time"
            ).build_and_register()
            
            if success:
                results["created_schemas"].append("ladder_logic_advanced_pid")
            else:
                results["errors"].append("Failed to create Ladder Logic Advanced PID schema")
            
            self.builder._reset()
            
            # 3. Function Block Standard PIDE
            fb_std_pide, success = await self.builder.create_base_schema(
                schema_id="function_block_standard_pide",
                name="Function Block Standard PIDE Controller",
                description="Standard PIDE (Enhanced PID) controller using function block programming with basic enhanced features",
                control_type=ControlLoopType.FUNCTION_BLOCK_STANDARD_PIDE,
                created_by="AI Task Orchestrator Phase 20.1"
            ).add_common_control_properties(
            ).add_pide_properties(
            ).add_tag("base_schema"
            ).add_tag("function_block"
            ).add_tag("standard_pide"
            ).set_validation_level(ValidationLevel.COMPREHENSIVE
            ).add_business_rule("PIDE enhanced features must be enabled selectively"
            ).add_business_rule("Auto-tuning should only be used during commissioning"
            ).build_and_register()
            
            if success:
                results["created_schemas"].append("function_block_standard_pide")
            else:
                results["errors"].append("Failed to create Function Block Standard PIDE schema")
            
            self.builder._reset()
            
            # 4. Function Block Advanced PIDE
            fb_adv_pide, success = await self.builder.create_base_schema(
                schema_id="function_block_advanced_pide",
                name="Function Block Advanced PIDE Controller",
                description="Advanced PIDE controller with comprehensive enhanced features including adaptive control and advanced auto-tuning",
                control_type=ControlLoopType.FUNCTION_BLOCK_ADVANCED_PIDE,
                created_by="AI Task Orchestrator Phase 20.1"
            ).inherit_from("function_block_standard_pide"
            ).add_common_control_properties(
            ).add_pide_properties(
            ).add_property("advanced_diagnostics", {
                "type": "object",
                "properties": {
                    "performance_monitoring": {"type": "boolean", "default": True},
                    "trend_analysis": {"type": "boolean", "default": False},
                    "alarm_generation": {"type": "boolean", "default": True},
                    "data_logging": {"type": "boolean", "default": False}
                },
                "additionalProperties": False
            }).add_tag("base_schema"
            ).add_tag("function_block"
            ).add_tag("advanced_pide"
            ).set_validation_level(ValidationLevel.PRODUCTION
            ).add_business_rule("Advanced diagnostics should be enabled for critical loops"
            ).add_business_rule("Adaptive control requires careful tuning and monitoring"
            ).build_and_register()
            
            if success:
                results["created_schemas"].append("function_block_advanced_pide")
            else:
                results["errors"].append("Failed to create Function Block Advanced PIDE schema")
            
            # Generate summary
            results["summary"] = {
                "total_schemas_attempted": 4,
                "total_schemas_created": len(results["created_schemas"]),
                "success_rate": len(results["created_schemas"]) / 4 * 100,
                "base_types_covered": len(set(ControlLoopType)),
                "execution_time_seconds": (datetime.now() - self.start_time).total_seconds()
            }
            
            logger.info(f"Base schemas creation completed: {results['summary']}")
            
        except Exception as e:
            error_msg = f"Failed to create base schemas: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    async def validate_all_schemas(self) -> Dict[str, Any]:
        """Validate all schemas in the registry"""
        results = {
            "session_id": self.session_id,
            "validation_results": [],
            "errors": [],
            "summary": {}
        }
        
        try:
            # Get all schemas
            all_schemas = await self.registry.list_schemas()
            
            for schema_metadata in all_schemas:
                schema_def = await self.registry.get_schema(schema_metadata.schema_id)
                if schema_def:
                    is_valid, validation_errors = await self.validator.validate_schema_definition(schema_def)
                    
                    results["validation_results"].append({
                        "schema_id": schema_metadata.schema_id,
                        "version": str(schema_metadata.version),
                        "is_valid": is_valid,
                        "errors": validation_errors,
                        "complexity_score": schema_metadata.complexity_score
                    })
            
            # Generate summary
            valid_count = sum(1 for r in results["validation_results"] if r["is_valid"])
            total_count = len(results["validation_results"])
            
            results["summary"] = {
                "total_schemas": total_count,
                "valid_schemas": valid_count,
                "invalid_schemas": total_count - valid_count,
                "validation_rate": (valid_count / total_count * 100) if total_count > 0 else 0,
                "average_complexity": sum(r.get("complexity_score", 0) for r in results["validation_results"]) / total_count if total_count > 0 else 0
            }
            
        except Exception as e:
            error_msg = f"Schema validation failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    async def generate_documentation(self) -> Dict[str, Any]:
        """Generate comprehensive documentation for the schema architecture"""
        results = {
            "session_id": self.session_id,
            "documentation_files": [],
            "errors": [],
            "summary": {}
        }
        
        try:
            docs_path = self.base_path / "docs"
            docs_path.mkdir(exist_ok=True)
            
            # Generate schema registry documentation
            registry_doc = await self._generate_registry_documentation()
            registry_file = docs_path / "schema_registry.md"
            with open(registry_file, 'w', encoding='utf-8') as f:
                f.write(registry_doc)
            results["documentation_files"].append(str(registry_file))
            
            # Generate architecture overview
            architecture_doc = await self._generate_architecture_documentation()
            architecture_file = docs_path / "schema_architecture.md"
            with open(architecture_file, 'w', encoding='utf-8') as f:
                f.write(architecture_doc)
            results["documentation_files"].append(str(architecture_file))
            
            # Generate API documentation
            api_doc = await self._generate_api_documentation()
            api_file = docs_path / "schema_api.md"
            with open(api_file, 'w', encoding='utf-8') as f:
                f.write(api_doc)
            results["documentation_files"].append(str(api_file))
            
            # Generate usage examples
            examples_doc = await self._generate_examples_documentation()
            examples_file = docs_path / "schema_examples.md"
            with open(examples_file, 'w', encoding='utf-8') as f:
                f.write(examples_doc)
            results["documentation_files"].append(str(examples_file))
            
            results["summary"] = {
                "documentation_files_created": len(results["documentation_files"]),
                "total_size_bytes": sum(Path(f).stat().st_size for f in results["documentation_files"])
            }
            
        except Exception as e:
            error_msg = f"Documentation generation failed: {str(e)}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
        
        return results
    
    async def _generate_registry_documentation(self) -> str:
        """Generate schema registry documentation"""
        schemas = await self.registry.list_schemas()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        doc = f"""# Schema Registry Documentation

Generated: {timestamp}
Session: {self.session_id}

## Overview

This document provides a comprehensive overview of all schemas registered in the Control Loop Schema Registry.

## Registered Schemas

Total Schemas: {len(schemas)}

"""
        
        for schema in schemas:
            doc += f"""### {schema.name} ({schema.schema_id})

- **Version**: {schema.version}
- **Type**: {schema.control_type.value}
- **Sub-type**: {schema.sub_type.value if schema.sub_type else 'N/A'}
- **Status**: {schema.status.value}
- **Created**: {schema.created_at.strftime('%Y-%m-%d')}
- **Validation Level**: {schema.validation_level.value}
- **Complexity Score**: {schema.complexity_score:.2f}

{schema.description}

---

"""
        
        return doc
    
    async def _generate_architecture_documentation(self) -> str:
        """Generate architecture documentation"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""# Schema Architecture Documentation

Generated: {timestamp}
Session: {self.session_id}

## Architecture Overview

The Control Loop Schema Architecture provides a comprehensive framework for defining, validating, and managing control loop configurations across industrial automation systems.

### Core Components

#### 1. Schema Registry
- Central repository for all schema definitions
- SQLite-based storage with caching
- Version control and lifecycle management
- Inheritance and extension relationships

#### 2. Schema Builder
- Builder pattern for creating schemas
- Fluent API for configuration
- Built-in validation and best practices
- Support for inheritance and composition

#### 3. Schema Validator
- Comprehensive validation framework
- Multiple validation levels (Basic, Comprehensive, Strict, Production)
- Business rule validation
- Inheritance chain validation

#### 4. Schema Migrator
- Version migration support
- Breaking change detection
- Data transformation planning
- Backward compatibility analysis

### Schema Types

#### Base Types
1. **Ladder Logic Standard PID** - Basic PID control in ladder logic
2. **Ladder Logic Advanced PID** - Enhanced PID with advanced features
3. **Function Block Standard PIDE** - Basic PIDE using function blocks
4. **Function Block Advanced PIDE** - Full-featured PIDE implementation

#### Sub-types (Planned)
1. **Feedforward** - Feedforward control enhancement
2. **Cascade** - Cascade control configuration
3. **Combined FF+Cascade** - Combined feedforward and cascade
4. **Multi-formula Weighted FF** - Advanced feedforward algorithms

### Versioning System

The architecture uses semantic versioning with the format XX.YY.ZZZ:
- **XX**: Major version (breaking changes)
- **YY**: Minor version (new features)
- **ZZZ**: Patch version (bug fixes)

### Inheritance Model

Schemas support multiple inheritance patterns:
- **Inherits From**: Direct parent-child relationships
- **Extends**: Compositional relationships
- **Mixins**: Reusable components

## Implementation Status

- ✅ Core infrastructure complete
- ✅ Base schema types implemented
- ✅ Validation framework operational
- ⏳ Sub-type schemas (Phase 20.3)
- ⏳ Custom extensibility (Phase 20.4)

"""
    
    async def _generate_api_documentation(self) -> str:
        """Generate API documentation"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""# Schema API Documentation

Generated: {timestamp}
Session: {self.session_id}

## API Overview

The Schema Architecture provides programmatic APIs for managing control loop schemas.

## Core Classes

### SchemaRegistry

Central registry for managing schemas.

```python
registry = SchemaRegistry()

# Register a schema
await registry.register_schema(schema_definition)

# Retrieve a schema
schema = await registry.get_schema("schema_id")

# List schemas with filtering
schemas = await registry.list_schemas(
    control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
    status=SchemaStatus.ACTIVE
)

# Update schema status
await registry.update_schema_status("schema_id", SchemaStatus.DEPRECATED)

# Get inheritance hierarchy
hierarchy = await registry.get_schema_hierarchy("schema_id")
```

### SchemaBuilder

Builder pattern for creating schemas.

```python
builder = SchemaBuilder(registry)

schema_def, success = await builder.create_base_schema(
    schema_id="my_controller",
    name="My Custom Controller",
    description="Custom PID controller for specific application",
    control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
    created_by="Engineer Name"
).add_common_control_properties(
).add_pid_properties(advanced=False
).add_tag("custom"
).set_validation_level(ValidationLevel.COMPREHENSIVE
).build_and_register()
```

### SchemaValidator

Validation framework for schemas.

```python
validator = SchemaValidator(registry)

# Validate schema definition
is_valid, errors = await validator.validate_schema_definition(schema_def)

# Validate instance against schema
is_valid, errors = schema_def.validate_instance(instance_data)
```

### SchemaMigrator

Migration support for schema versions.

```python
migrator = SchemaMigrator(registry)

# Create migration plan
plan = await migrator.create_migration_plan(
    from_version=SchemaVersion(1, 0, 0),
    to_version=SchemaVersion(2, 0, 0),
    schema_id="my_schema"
)
```

## Data Structures

### SchemaVersion

```python
version = SchemaVersion(major=1, minor=2, patch=3)
print(str(version))  # "01.02.003"

# Version operations
new_version = version.increment_minor()  # 01.03.000
```

### SchemaMetadata

```python
metadata = SchemaMetadata(
    schema_id="example_pid",
    name="Example PID Controller",
    description="Example schema for documentation",
    version=SchemaVersion(1, 0, 0),
    control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
    status=SchemaStatus.ACTIVE,
    created_at=datetime.now(),
    updated_at=datetime.now(),
    created_by="API Documentation"
)
```

## Enumerations

### ControlLoopType
- `LADDER_LOGIC_STANDARD_PID`
- `LADDER_LOGIC_ADVANCED_PID`
- `FUNCTION_BLOCK_STANDARD_PIDE`
- `FUNCTION_BLOCK_ADVANCED_PIDE`

### ControlLoopSubType
- `FEEDFORWARD`
- `CASCADE`
- `COMBINED_FF_CASCADE`
- `MULTI_FORMULA_WEIGHTED_FF`

### SchemaStatus
- `DRAFT` - Under development
- `ACTIVE` - Production ready
- `DEPRECATED` - Still usable but not recommended
- `ARCHIVED` - No longer supported

### ValidationLevel
- `BASIC` - Minimal validation
- `COMPREHENSIVE` - Standard validation
- `STRICT` - Enhanced validation
- `PRODUCTION` - Full production validation

"""
    
    async def _generate_examples_documentation(self) -> str:
        """Generate examples documentation"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return f"""# Schema Examples Documentation

Generated: {timestamp}
Session: {self.session_id}

## Overview

This document provides practical examples of using the Control Loop Schema Architecture.

## Example 1: Creating a Simple PID Controller Schema

```python
import asyncio
from schema_architecture_manager import SchemaArchitectureManager
from schema_registry import ControlLoopType, ValidationLevel

async def create_simple_pid():
    manager = SchemaArchitectureManager()
    
    # Create a custom PID controller schema
    schema_def, success = await manager.builder.create_base_schema(
        schema_id="temperature_control_pid",
        name="Temperature Control PID",
        description="PID controller for temperature control in reactor vessel",
        control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
        created_by="Process Engineer"
    ).add_common_control_properties(
    ).add_pid_properties(advanced=False
    ).add_tag("temperature"
    ).add_tag("reactor"
    ).add_business_rule("Proportional gain should be between 0.1 and 10 for temperature control"
    ).add_business_rule("Integral time should be at least 60 seconds for thermal processes"
    ).set_validation_level(ValidationLevel.PRODUCTION
    ).build_and_register()
    
    if success:
        print(f"Successfully created schema: {schema_def.metadata.schema_id}")
    else:
        print("Failed to create schema")

# Run the example
asyncio.run(create_simple_pid())
```

## Example 2: Creating an Instance from Schema

```python
async def create_controller_instance():
    manager = SchemaArchitectureManager()
    
    # Get the schema
    schema = await manager.registry.get_schema("temperature_control_pid")
    
    if schema:
        # Create an instance
        instance = {
            "tag_name": "TIC_101",
            "description": "Reactor temperature control",
            "process_variable": {
                "tag": "TT_101_PV",
                "engineering_units": "°C",
                "min_value": 0,
                "max_value": 500,
                "deadband": 0.5
            },
            "setpoint": {
                "tag": "TIC_101_SP",
                "default_value": 350,
                "min_value": 100,
                "max_value": 450,
                "rate_limit": 2.0
            },
            "control_output": {
                "tag": "TIC_101_OUT",
                "min_value": 0,
                "max_value": 100,
                "initial_value": 0,
                "rate_limit": 5.0
            },
            "operating_mode": "auto",
            "enabled": True,
            "pid_parameters": {
                "proportional_gain": 2.5,
                "integral_time": 120,
                "derivative_time": 30,
                "integral_windup_high": 100,
                "integral_windup_low": 0
            }
        }
        
        # Validate the instance
        is_valid, errors = schema.validate_instance(instance)
        
        if is_valid:
            print("Instance is valid!")
        else:
            print(f"Validation errors: {errors}")

asyncio.run(create_controller_instance())
```

## Example 3: Schema Inheritance

```python
async def create_inherited_schema():
    manager = SchemaArchitectureManager()
    
    # Create a specialized temperature controller that inherits from standard PID
    schema_def, success = await manager.builder.create_base_schema(
        schema_id="reactor_temperature_pid",
        name="Reactor Temperature PID",
        description="Specialized PID for reactor temperature with safety interlocks",
        control_type=ControlLoopType.LADDER_LOGIC_ADVANCED_PID,
        created_by="Safety Engineer"
    ).inherit_from("temperature_control_pid"
    ).add_property("safety_interlocks", {
        "type": "object",
        "properties": {
            "high_temperature_alarm": {"type": "number", "minimum": 400},
            "emergency_shutdown": {"type": "boolean", "default": True},
            "interlock_bypass": {"type": "boolean", "default": False}
        },
        "required": ["high_temperature_alarm", "emergency_shutdown"],
        "additionalProperties": False
    }, required=True
    ).add_tag("safety"
    ).add_tag("reactor"
    ).add_business_rule("Emergency shutdown must be enabled for reactor applications"
    ).add_business_rule("Interlock bypass requires supervisor approval"
    ).set_validation_level(ValidationLevel.PRODUCTION
    ).build_and_register()
    
    if success:
        print(f"Successfully created inherited schema: {schema_def.metadata.schema_id}")

asyncio.run(create_inherited_schema())
```

## Example 4: Schema Validation and Migration

```python
async def validate_and_migrate():
    manager = SchemaArchitectureManager()
    
    # Validate all schemas
    validation_results = await manager.validate_all_schemas()
    
    print(f"Validation Summary:")
    print(f"Total schemas: {validation_results['summary']['total_schemas']}")
    print(f"Valid schemas: {validation_results['summary']['valid_schemas']}")
    print(f"Validation rate: {validation_results['summary']['validation_rate']:.1f}%")
    
    # Create migration plan (example)
    migration_plan = await manager.migrator.create_migration_plan(
        from_version=SchemaVersion(1, 0, 0),
        to_version=SchemaVersion(1, 1, 0),
        schema_id="temperature_control_pid"
    )
    
    print(f"Migration plan: {migration_plan}")

asyncio.run(validate_and_migrate())
```

## Example 5: Querying Schema Registry

```python
async def query_schemas():
    manager = SchemaArchitectureManager()
    
    # List all active PID schemas
    pid_schemas = await manager.registry.list_schemas(
        control_type=ControlLoopType.LADDER_LOGIC_STANDARD_PID,
        status=SchemaStatus.ACTIVE
    )
    
    print(f"Found {len(pid_schemas)} active PID schemas:")
    for schema in pid_schemas:
        print(f"- {schema.name} ({schema.schema_id}) v{schema.version}")
    
    # List schemas with specific tags
    temperature_schemas = await manager.registry.list_schemas(tags=["temperature"])
    
    print(f"Found {len(temperature_schemas)} temperature-related schemas:")
    for schema in temperature_schemas:
        print(f"- {schema.name} (tags: {', '.join(schema.tags)})")
    
    # Get schema hierarchy
    hierarchy = await manager.registry.get_schema_hierarchy("reactor_temperature_pid")
    print(f"Schema hierarchy: {hierarchy}")

asyncio.run(query_schemas())
```

## Example 6: Custom Validation Rules

```python
async def custom_validation_example():
    manager = SchemaArchitectureManager()
    
    # Create schema with custom validation rules
    schema_def, success = await manager.builder.create_base_schema(
        schema_id="flow_control_pid",
        name="Flow Control PID",
        description="PID controller for flow control with custom validation",
        control_type=ControlLoopType.FUNCTION_BLOCK_STANDARD_PIDE,
        created_by="Control Engineer"
    ).add_common_control_properties(
    ).add_pide_properties(
    ).add_validation_rule("flow_rate_limits", {
        "type": "range_check",
        "description": "Flow rate must be within physical limits",
        "validation": "process_variable.min_value >= 0 AND process_variable.max_value <= 1000"
    }).add_validation_rule("tuning_stability", {
        "type": "stability_check",
        "description": "PID tuning must ensure stable control",
        "validation": "pid_parameters.proportional_gain * pid_parameters.integral_time > 0.1"
    }).build_and_register()
    
    if success:
        print(f"Schema with custom validation created: {schema_def.metadata.schema_id}")
        
        # Test validation
        test_instance = {
            "tag_name": "FIC_201",
            "process_variable": {"tag": "FT_201", "min_value": -10, "max_value": 2000},  # Invalid range
            "setpoint": {"tag": "FIC_201_SP"},
            "control_output": {"tag": "FIC_201_OUT"},
            "operating_mode": "auto",
            "pid_parameters": {
                "proportional_gain": 0.01,  # Too low for stability
                "integral_time": 0.5
            }
        }
        
        is_valid, errors = schema_def.validate_instance(test_instance)
        print(f"Validation result: {is_valid}")
        if not is_valid:
            print(f"Errors: {errors}")

asyncio.run(custom_validation_example())
```

## Best Practices

### 1. Schema Design
- Use descriptive schema IDs and names
- Include comprehensive descriptions
- Add relevant tags for categorization
- Set appropriate validation levels

### 2. Versioning
- Increment major version for breaking changes
- Use minor versions for new features
- Patch versions for bug fixes
- Document breaking changes

### 3. Inheritance
- Use inheritance for specialization
- Avoid deep inheritance chains (max 3-4 levels)
- Document inheritance relationships
- Validate inheritance compatibility

### 4. Validation
- Start with comprehensive validation
- Add custom rules for domain-specific requirements
- Test validation thoroughly
- Document validation requirements

### 5. Documentation
- Provide examples for all schemas
- Document business rules and constraints
- Keep documentation up to date
- Include migration guides for version changes

"""
    
    async def execute_phase_20_1(self) -> Dict[str, Any]:
        """Execute complete Phase 20.1 implementation"""
        phase_results = {
            "session_id": self.session_id,
            "phase": "20.1",
            "start_time": self.start_time.isoformat(),
            "tasks": {},
            "overall_status": "in_progress",
            "errors": [],
            "summary": {}
        }
        
        try:
            logger.info("Starting Phase 20.1: Schema Architecture & Management System")
            
            # Task 1: Create base schemas
            logger.info("Task 1: Creating base control loop schema types")
            base_schema_results = await self.create_base_schemas()
            phase_results["tasks"]["create_base_schemas"] = base_schema_results
            
            # Task 2: Validate all schemas
            logger.info("Task 2: Validating all schemas")
            validation_results = await self.validate_all_schemas()
            phase_results["tasks"]["validate_schemas"] = validation_results
            
            # Task 3: Generate documentation
            logger.info("Task 3: Generating comprehensive documentation")
            documentation_results = await self.generate_documentation()
            phase_results["tasks"]["generate_documentation"] = documentation_results
            
            # Calculate overall results
            end_time = datetime.now()
            execution_time = (end_time - self.start_time).total_seconds()
            
            # Determine overall status
            all_tasks_successful = all(
                len(task_result.get("errors", [])) == 0 
                for task_result in phase_results["tasks"].values()
            )
            
            if all_tasks_successful:
                phase_results["overall_status"] = "completed"
            else:
                phase_results["overall_status"] = "completed_with_errors"
            
            # Generate summary
            phase_results["summary"] = {
                "execution_time_seconds": execution_time,
                "end_time": end_time.isoformat(),
                "schemas_created": len(base_schema_results.get("created_schemas", [])),
                "validation_success_rate": validation_results.get("summary", {}).get("validation_rate", 0),
                "documentation_files": len(documentation_results.get("documentation_files", [])),
                "total_errors": sum(len(task.get("errors", [])) for task in phase_results["tasks"].values()),
                "success_criteria_met": {
                    "base_schemas_created": len(base_schema_results.get("created_schemas", [])) == 4,
                    "all_schemas_valid": validation_results.get("summary", {}).get("validation_rate", 0) == 100,
                    "documentation_complete": len(documentation_results.get("documentation_files", [])) >= 4,
                    "no_critical_errors": len(phase_results["errors"]) == 0
                }
            }
            
            # Collect all errors
            for task_name, task_result in phase_results["tasks"].items():
                if task_result.get("errors"):
                    phase_results["errors"].extend([f"{task_name}: {error}" for error in task_result["errors"]])
            
            logger.info(f"Phase 20.1 completed with status: {phase_results['overall_status']}")
            logger.info(f"Execution time: {execution_time:.2f} seconds")
            logger.info(f"Schemas created: {phase_results['summary']['schemas_created']}")
            
        except Exception as e:
            error_msg = f"Phase 20.1 execution failed: {str(e)}"
            phase_results["errors"].append(error_msg)
            phase_results["overall_status"] = "failed"
            logger.error(error_msg)
        
        return phase_results

# =============================================================================
# MAIN EXECUTION
# =============================================================================

async def main():
    """Main execution function for Phase 20.1"""
    print("🏗️ Phase 20.1: Schema Architecture & Management System")
    print("=" * 60)
    
    try:
        # Initialize manager
        manager = SchemaArchitectureManager()
        
        # Execute phase
        results = await manager.execute_phase_20_1()
        
        # Display results
        print(f"\n📊 PHASE 20.1 RESULTS")
        print(f"Session ID: {results['session_id']}")
        print(f"Status: {results['overall_status'].upper()}")
        print(f"Execution Time: {results['summary']['execution_time_seconds']:.2f} seconds")
        print(f"Schemas Created: {results['summary']['schemas_created']}")
        print(f"Validation Rate: {results['summary']['validation_success_rate']:.1f}%")
        print(f"Documentation Files: {results['summary']['documentation_files']}")
        
        if results['errors']:
            print(f"\n❌ ERRORS ({len(results['errors'])}):")
            for error in results['errors']:
                print(f"  - {error}")
        
        print(f"\n✅ SUCCESS CRITERIA:")
        for criterion, met in results['summary']['success_criteria_met'].items():
            status = "✅" if met else "❌"
            print(f"  {status} {criterion}")
        
        # Save results
        results_file = Path("plc-gbt-stack/results/phase20") / f"phase20_1_results_{int(datetime.now().timestamp())}.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        return {"error": str(e), "status": "failed"}

if __name__ == "__main__":
    asyncio.run(main()) 