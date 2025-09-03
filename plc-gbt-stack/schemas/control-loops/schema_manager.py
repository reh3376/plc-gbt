#!/usr/bin/env python3
"""
Control Loop Schema Manager
==========================

Manages modular JSON schemas for PID/PIDE control loops with versioning,
inheritance, and extensibility support.

Following AI Task Orchestrator methodology for systematic implementation.
"""

import json
import logging
import re
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from jsonschema import Draft7Validator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Schema version pattern
VERSION_PATTERN = re.compile(r'^\d{2}\.\d{2}\.\d{3}$')

@dataclass
class SchemaMetadata:
    """Metadata for control loop schemas"""
    created_at: str
    created_by: str
    version: str
    schema_type: str
    parent_schema: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not VERSION_PATTERN.match(self.version):
            raise ValueError(f"Invalid version format: {self.version}. Must be XX.YY.ZZZ")


class ControlLoopSchemaManager:
    """
    Manages control loop JSON schemas with versioning and inheritance.

    Features:
    - Version management with semantic versioning
    - Schema inheritance for base types and subtypes
    - Custom schema creation with validation
    - Export/import functionality
    - Change tracking and history
    """

    def __init__(self, base_path: str = "plc-gbt-stack/schemas/control-loops"):
        self.base_path = Path(base_path)
        self.base_schemas_path = self.base_path / "base"
        self.subtypes_path = self.base_path / "subtypes"
        self.versions_path = self.base_path / "versions"
        self.custom_path = self.base_path / "custom"

        # Create directories if they don't exist
        for path in [self.base_schemas_path, self.subtypes_path,
                     self.versions_path, self.custom_path]:
            path.mkdir(parents=True, exist_ok=True)

        # Schema registry
        self.schema_registry: Dict[str, Dict[str, Any]] = {}
        self.load_schemas()

        logger.info(f"Schema manager initialized at {self.base_path}")

    def load_schemas(self) -> None:
        """Load all existing schemas from disk into the registry"""
        schema_files = []

        # Collect all JSON files
        for directory in [self.base_schemas_path, self.subtypes_path,
                         self.custom_path]:
            schema_files.extend(directory.glob("*.json"))

        for schema_file in schema_files:
            try:
                with open(schema_file) as f:
                    schema = json.load(f)
                    schema_id = self._generate_schema_id(schema)
                    self.schema_registry[schema_id] = schema
                    logger.info(f"Loaded schema: {schema_id}")
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")

    def _generate_schema_id(self, schema: Dict[str, Any]) -> str:
        """Generate unique ID for a schema based on title and version"""
        title = schema.get('title', 'Unknown')
        version = schema.get('properties', {}).get('version', {}).get('enum', ['00.00.001'])[0]
        return f"{title}:{version}"

    def create_base_schema(self, schema_type: str, metadata: SchemaMetadata) -> Dict[str, Any]:
        """
        Create a new base schema for a control loop type.

        Args:
            schema_type: One of 'standard-pid', 'advanced-pid', 'standard-pide', 'advanced-pide'
            metadata: Schema metadata including version and creator

        Returns:
            The created schema dictionary
        """
        base_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": schema_type.replace('-', ' ').title(),
            "description": metadata.description or f"Schema for {schema_type} control loop",
            "type": "object",
            "properties": {
                "created_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Schema creation timestamp (ISO 8601)"
                },
                "created_by": {
                    "type": "string",
                    "description": "Schema creator or tool name"
                },
                "version": {
                    "type": "string",
                    "description": "Schema version in semantic format",
                    "pattern": VERSION_PATTERN.pattern,
                    "enum": [metadata.version]
                }
            },
            "required": ["created_at", "created_by", "version"],
            "additionalProperties": False
        }

        # Add common PID/PIDE properties
        base_schema["properties"].update(self._get_common_pid_properties())

        # Add type-specific properties
        if "advanced" in schema_type:
            base_schema["properties"].update(self._get_advanced_properties())

        if "pide" in schema_type:
            base_schema["properties"].update(self._get_pide_specific_properties())

        # Save schema
        schema_id = self._generate_schema_id(base_schema)
        self.schema_registry[schema_id] = base_schema
        self._save_schema(base_schema, self.base_schemas_path / f"{schema_type}.json")

        return base_schema

    def _get_common_pid_properties(self) -> Dict[str, Any]:
        """Get common properties for all PID/PIDE controllers"""
        return {
            "SP": {
                "type": "number",
                "description": "Setpoint for the PID loop in engineering units"
            },
            "PV": {
                "type": "number",
                "description": "Process Variable (current value) in engineering units"
            },
            "CV": {
                "type": "number",
                "description": "Control Variable (output) as percentage",
                "minimum": 0.0,
                "maximum": 100.0
            },
            "KP": {
                "type": "number",
                "description": "Proportional gain",
                "minimum": 0.0
            },
            "KI": {
                "type": "number",
                "description": "Integral gain",
                "minimum": 0.0
            },
            "KD": {
                "type": "number",
                "description": "Derivative gain",
                "minimum": 0.0
            },
            "PE": {
                "type": "string",
                "enum": ["Independent", "Dependent"],
                "description": "PID equation form"
            },
            "CA": {
                "type": "string",
                "enum": ["Direct (PV-SP)", "Reverse (SP-PV)"],
                "description": "Control action"
            },
            "UPD": {
                "type": "number",
                "description": "Loop update time in seconds",
                "minimum": 0.0
            }
        }

    def _get_advanced_properties(self) -> Dict[str, Any]:
        """Get properties specific to advanced controllers"""
        return {
            "BIAS": {
                "type": "number",
                "description": "Output bias (feedforward) percentage",
                "minimum": -100.0,
                "maximum": 100.0
            },
            "DB": {
                "type": "number",
                "description": "Deadband value in engineering units",
                "minimum": 0.0
            },
            "MAXO": {
                "type": "number",
                "description": "CV high limit (%)",
                "minimum": 0.0,
                "maximum": 100.0
            },
            "MINO": {
                "type": "number",
                "description": "CV low limit (%)",
                "minimum": 0.0,
                "maximum": 100.0
            }
        }

    def _get_pide_specific_properties(self) -> Dict[str, Any]:
        """Get properties specific to PIDE (Enhanced PID) controllers"""
        return {
            "PGain": {
                "type": "number",
                "description": "Proportional gain for PIDE",
                "minimum": 0.0
            },
            "IGain": {
                "type": "number",
                "description": "Integral gain for PIDE",
                "minimum": 0.0
            },
            "DGain": {
                "type": "number",
                "description": "Derivative gain for PIDE",
                "minimum": 0.0
            },
            "PVEProportional": {
                "type": "boolean",
                "description": "Enable proportional action on PV change"
            },
            "DependIndepend": {
                "type": "boolean",
                "description": "False = Independent gains, True = Dependent gains"
            },
            "CVInitReq": {
                "type": "boolean",
                "description": "CV initialization request"
            }
        }

    def create_subtype_schema(self, base_type: str, subtype: str,
                            metadata: SchemaMetadata,
                            additional_properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a subtype schema that inherits from a base schema.

        Args:
            base_type: Base schema type to inherit from
            subtype: Subtype identifier (e.g., 'feedforward', 'cascade')
            metadata: Schema metadata
            additional_properties: Properties specific to this subtype

        Returns:
            The created subtype schema
        """
        # Find base schema
        base_schema_id = None
        for schema_id in self.schema_registry:
            if base_type in schema_id.lower():
                base_schema_id = schema_id
                break

        if not base_schema_id:
            raise ValueError(f"Base schema type '{base_type}' not found")

        # Deep copy base schema
        subtype_schema = deepcopy(self.schema_registry[base_schema_id])

        # Update metadata
        subtype_schema["title"] = f"{subtype_schema['title']} - {subtype.title()}"
        subtype_schema["description"] = metadata.description or f"{subtype_schema['description']} with {subtype}"
        subtype_schema["properties"]["version"]["enum"] = [metadata.version]

        # Add parent reference
        subtype_schema["allOf"] = [
            {"$ref": f"#/definitions/{base_type}"}
        ]

        # Add subtype-specific properties
        subtype_schema["properties"].update(additional_properties)

        # Update required fields if needed
        new_required = list(additional_properties.keys())
        if "required" in subtype_schema:
            subtype_schema["required"].extend(new_required)
        else:
            subtype_schema["required"] = new_required

        # Save schema
        schema_id = self._generate_schema_id(subtype_schema)
        self.schema_registry[schema_id] = subtype_schema
        filename = f"{base_type}-{subtype}.json"
        self._save_schema(subtype_schema, self.subtypes_path / filename)

        return subtype_schema

    def version_schema(self, schema_id: str, changes: Dict[str, Any],
                      change_description: str) -> Dict[str, Any]:
        """
        Create a new version of an existing schema.

        Args:
            schema_id: ID of schema to version
            changes: Dictionary of changes to apply
            change_description: Description of what changed

        Returns:
            The new versioned schema
        """
        if schema_id not in self.schema_registry:
            raise ValueError(f"Schema '{schema_id}' not found")

        # Deep copy existing schema
        old_schema = self.schema_registry[schema_id]
        new_schema = deepcopy(old_schema)

        # Increment version
        old_version = old_schema["properties"]["version"]["enum"][0]
        new_version = self._increment_version(old_version)

        # Update version in schema
        new_schema["properties"]["version"]["enum"] = [new_version]

        # Apply changes
        self._apply_changes(new_schema, changes)

        # Add version history
        if "_version_history" not in new_schema:
            new_schema["_version_history"] = []

        new_schema["_version_history"].append({
            "version": new_version,
            "previous_version": old_version,
            "changed_at": datetime.now().isoformat(),
            "description": change_description,
            "changes": changes
        })

        # Save new version
        new_schema_id = self._generate_schema_id(new_schema)
        self.schema_registry[new_schema_id] = new_schema

        # Archive old version
        self._archive_schema(old_schema, old_version)

        return new_schema

    def _increment_version(self, version: str) -> str:
        """Increment version number following XX.YY.ZZZ format"""
        major, minor, patch = version.split('.')
        patch_num = int(patch)

        # Increment patch by default
        patch_num += 1

        # Handle overflow
        if patch_num > 999:
            patch_num = 0
            minor_num = int(minor) + 1
            if minor_num > 99:
                minor_num = 0
                major_num = int(major) + 1
                if major_num > 99:
                    raise ValueError("Version number overflow")
                major = f"{major_num:02d}"
            minor = f"{minor_num:02d}"

        patch = f"{patch_num:03d}"
        return f"{major}.{minor}.{patch}"

    def _apply_changes(self, schema: Dict[str, Any], changes: Dict[str, Any]) -> None:
        """Apply changes to a schema recursively"""
        for key, value in changes.items():
            if key in schema and isinstance(schema[key], dict) and isinstance(value, dict):
                # Recursive update for nested dicts
                self._apply_changes(schema[key], value)
            else:
                # Direct assignment
                schema[key] = value

    def _save_schema(self, schema: Dict[str, Any], filepath: Path) -> None:
        """Save schema to disk"""
        with open(filepath, 'w') as f:
            json.dump(schema, f, indent=2)
        logger.info(f"Saved schema to {filepath}")

    def _archive_schema(self, schema: Dict[str, Any], version: str) -> None:
        """Archive a schema version"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{schema['title'].replace(' ', '_')}_{version}_{timestamp}.json"
        filepath = self.versions_path / filename
        self._save_schema(schema, filepath)

    def validate_instance(self, schema_id: str, instance: Dict[str, Any]) -> List[str]:
        """
        Validate a control loop instance against a schema.

        Args:
            schema_id: Schema ID to validate against
            instance: Instance data to validate

        Returns:
            List of validation errors (empty if valid)
        """
        if schema_id not in self.schema_registry:
            return [f"Schema '{schema_id}' not found"]

        schema = self.schema_registry[schema_id]
        validator = Draft7Validator(schema)

        errors = []
        for error in validator.iter_errors(instance):
            errors.append(f"{' -> '.join(str(p) for p in error.path)}: {error.message}")

        return errors

    def export_schema(self, schema_id: str, format: str = "json") -> Union[str, Dict[str, Any]]:
        """Export a schema in various formats"""
        if schema_id not in self.schema_registry:
            raise ValueError(f"Schema '{schema_id}' not found")

        schema = self.schema_registry[schema_id]

        if format == "json":
            return json.dumps(schema, indent=2)
        elif format == "dict":
            return schema
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def list_schemas(self, filter_type: Optional[str] = None) -> List[str]:
        """List all available schemas with optional filtering"""
        schemas = list(self.schema_registry.keys())

        if filter_type:
            schemas = [s for s in schemas if filter_type.lower() in s.lower()]

        return sorted(schemas)
