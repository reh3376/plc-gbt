# Schema API Documentation

Generated: 2025-07-15 08:53:32
Session: phase20_1_1752584012

## API Overview

The Schema Architecture provides programmatic APIs for managing control loop schemas.

## Core Classes

### SimpleSchemaManager

Main entry point for schema management:

```python
manager = SimpleSchemaManager()

# Create base schemas
result = await manager.create_base_schemas()

# Validate schemas
validation = await manager.validate_schemas()

# Generate documentation
docs = await manager.generate_documentation()
```

## Schema Structure

### SchemaMetadata

```python
@dataclass
class SchemaMetadata:
    schema_id: str
    name: str  
    description: str
    version: SchemaVersion
    control_type: ControlLoopType
    status: SchemaStatus
    created_at: datetime
    updated_at: datetime
    created_by: str
    validation_level: ValidationLevel
```

### SchemaVersion

```python
@dataclass
class SchemaVersion:
    major: int  # Breaking changes (XX)
    minor: int  # New features (YY)
    patch: int  # Bug fixes (ZZZ)
    
    def __str__(self) -> str:
        return f"{self.major:02d}.{self.minor:02d}.{self.patch:03d}"
```

## Enumerations

### ControlLoopType
- LADDER_LOGIC_STANDARD_PID
- LADDER_LOGIC_ADVANCED_PID
- FUNCTION_BLOCK_STANDARD_PIDE
- FUNCTION_BLOCK_ADVANCED_PIDE

### SchemaStatus
- DRAFT: Under development
- ACTIVE: Production ready
- DEPRECATED: Still usable but not recommended
- ARCHIVED: No longer supported

### ValidationLevel
- BASIC: Minimal validation
- COMPREHENSIVE: Standard validation
- STRICT: Enhanced validation
- PRODUCTION: Full production validation

## Usage Examples

### Creating a Control Loop Instance

```python
# Example PID controller configuration
instance = {
    "tag_name": "TIC_101",
    "description": "Temperature control for reactor",
    "process_variable": {
        "tag": "TT_101_PV",
        "engineering_units": "°C",
        "min_value": 0,
        "max_value": 500
    },
    "setpoint": {
        "tag": "TIC_101_SP", 
        "default_value": 350,
        "min_value": 100,
        "max_value": 450
    },
    "control_output": {
        "tag": "TIC_101_OUT",
        "min_value": 0,
        "max_value": 100,
        "initial_value": 0
    },
    "pid_parameters": {
        "proportional_gain": 2.5,
        "integral_time": 120,
        "derivative_time": 30
    },
    "operating_mode": "auto",
    "enabled": true
}
```

This instance conforms to the ladder_logic_standard_pid schema and can be validated using the JSON Schema framework.
