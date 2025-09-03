#!/usr/bin/env python3
"""
Generate Base Control Loop Schemas
=================================

Creates the 4 main types of control loop schemas:
1. Ladder Logic Standard PID
2. Ladder Logic Advanced PID
3. Function Block Standard PIDE
4. Function Block Advanced PIDE

Following AI Task Orchestrator methodology.
"""

import logging
from datetime import datetime

from .schema_manager import ControlLoopSchemaManager, SchemaMetadata

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_standard_pid_schema(manager: ControlLoopSchemaManager) -> None:
    """Generate Ladder Logic Standard PID schema"""
    metadata = SchemaMetadata(
        created_at=datetime.now().isoformat(),
        created_by="plc-gbt-schema-generator",
        version="01.00.001",
        schema_type="standard-pid",
        description="Schema for configuring a standard Ladder Logic PID loop (positional form PID) in Studio 5000"
    )

    # Base schema is created by the manager
    schema = manager.create_base_schema("standard-pid", metadata)

    # Add standard PID specific properties
    additional_properties = {
        "SO": {
            "type": "number",
            "description": "Set Output percentage for manual mode",
            "minimum": 0.0,
            "maximum": 100.0
        },
        "MO": {
            "type": "boolean",
            "description": "Manual mode flag (external/hardware)"
        },
        "SWM": {
            "type": "boolean",
            "description": "Software Manual mode flag"
        },
        "DOE": {
            "type": "string",
            "enum": ["PV", "Error"],
            "description": "Derivative Of Error selection"
        },
        "PVT": {
            "type": "boolean",
            "description": "PV Tracking enable for bumpless transfer"
        },
        "CL": {
            "type": "boolean",
            "description": "Cascade Loop enable",
            "default": False
        },
        "CT": {
            "type": "string",
            "enum": ["Master", "Slave"],
            "description": "Cascade Type (if CL is true)"
        },
        "MAXI": {
            "type": "number",
            "description": "PV Unscaled Maximum (raw input high range)",
            "default": 16383
        },
        "MINI": {
            "type": "number",
            "description": "PV Unscaled Minimum (raw input low range)",
            "default": 0
        },
        "MAXS": {
            "type": "number",
            "description": "PV Engineering Units Maximum"
        },
        "MINS": {
            "type": "number",
            "description": "PV Engineering Units Minimum"
        },
        "INI": {
            "type": "boolean",
            "description": "PID Initialized flag",
            "default": True
        }
    }

    # Update schema with additional properties
    schema["properties"].update(additional_properties)
    schema["required"].extend(["SO", "PE", "CA", "UPD"])

    # Save updated schema
    manager._save_schema(schema, manager.base_schemas_path / "standard-pid.json")
    logger.info("Generated Ladder Logic Standard PID schema")


def generate_advanced_pid_schema(manager: ControlLoopSchemaManager) -> None:
    """Generate Ladder Logic Advanced PID schema"""
    metadata = SchemaMetadata(
        created_at=datetime.now().isoformat(),
        created_by="plc-gbt-schema-generator",
        version="01.00.001",
        schema_type="advanced-pid",
        description="Schema for configuring an advanced Ladder Logic PID loop with enhanced features"
    )

    schema = manager.create_base_schema("advanced-pid", metadata)

    # Add advanced PID specific properties
    additional_properties = {
        "SO": {
            "type": "number",
            "description": "Set Output percentage for manual mode",
            "minimum": 0.0,
            "maximum": 100.0
        },
        "MO": {
            "type": "boolean",
            "description": "Manual mode flag (external/hardware)"
        },
        "SWM": {
            "type": "boolean",
            "description": "Software Manual mode flag"
        },
        "DOE": {
            "type": "string",
            "enum": ["PV", "Error"],
            "description": "Derivative Of Error selection"
        },
        "NDF": {
            "type": "boolean",
            "description": "No Derivative Filter"
        },
        "NOBC": {
            "type": "boolean",
            "description": "No Bias Calculation"
        },
        "NOZC": {
            "type": "boolean",
            "description": "No Zero Crossing in deadband"
        },
        "PVT": {
            "type": "boolean",
            "description": "PV Tracking enable"
        },
        "PVH": {
            "type": "number",
            "description": "PV High Alarm limit in engineering units"
        },
        "PVL": {
            "type": "number",
            "description": "PV Low Alarm limit in engineering units"
        },
        "PVDB": {
            "type": "number",
            "description": "PV Alarm Deadband in engineering units",
            "minimum": 0.0
        },
        "DVP": {
            "type": "number",
            "description": "Positive Deviation Alarm limit"
        },
        "DVN": {
            "type": "number",
            "description": "Negative Deviation Alarm limit"
        },
        "DVDB": {
            "type": "number",
            "description": "Deviation Alarm Deadband",
            "minimum": 0.0
        },
        "MAXI": {
            "type": "number",
            "description": "PV Unscaled Maximum",
            "default": 16383
        },
        "MINI": {
            "type": "number",
            "description": "PV Unscaled Minimum",
            "default": 0
        },
        "MAXS": {
            "type": "number",
            "description": "PV Engineering Units Maximum"
        },
        "MINS": {
            "type": "number",
            "description": "PV Engineering Units Minimum"
        },
        "MAXCV": {
            "type": "number",
            "description": "CV Engineering Units Maximum",
            "default": 100.0
        },
        "MINCV": {
            "type": "number",
            "description": "CV Engineering Units Minimum",
            "default": 0.0
        }
    }

    schema["properties"].update(additional_properties)
    schema["required"].extend(["SO", "PE", "CA", "UPD"])

    manager._save_schema(schema, manager.base_schemas_path / "advanced-pid.json")
    logger.info("Generated Ladder Logic Advanced PID schema")

def generate_all_base_schemas(manager: ControlLoopSchemaManager) -> None:
    """Generate all base schemas"""
    logger.info("Generating all base schemas...")
    generate_standard_pid_schema(manager)
    generate_advanced_pid_schema(manager)
    logger.info("All base schemas generated successfully")
