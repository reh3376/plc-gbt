# 🔧 PLC Control Loop CLI - API Reference

**Version**: 1.0.0  
**Date**: January 18, 2025  
**Author**: AI Task Orchestrator Implementation  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Global Options](#global-options)
3. [Schema Commands](#schema-commands)
4. [Instance Commands](#instance-commands)
5. [Batch Commands](#batch-commands)
6. [PLC Commands](#plc-commands)
7. [Memory Commands](#memory-commands)
8. [Configuration Commands](#configuration-commands)
9. [Interactive Commands](#interactive-commands)
10. [Exit Codes](#exit-codes)
11. [Environment Variables](#environment-variables)
12. [Configuration File Format](#configuration-file-format)

---

## 🎯 Overview

The PLC Control Loop CLI provides a comprehensive command-line interface for control loop management. All commands follow a consistent structure and provide detailed help information.

### **Command Structure**

```bash
plc-cl [GLOBAL_OPTIONS] COMMAND [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

### **Common Patterns**

- **List Operations**: `plc-cl <resource> list [filters]`
- **Information**: `plc-cl <resource> info <identifier>`
- **Creation**: `plc-cl <resource> create [options]`
- **Modification**: `plc-cl <resource> modify <identifier> [changes]`
- **Validation**: `plc-cl <resource> validate <identifier>`

---

## 🌐 Global Options

Available for all commands:

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--version` | | flag | | Show CLI version and exit |
| `--help` | | flag | | Show help message |
| `--config-dir` | | path | `~/.plc-cl` | Configuration directory |
| `--verbose` | `-v` | flag | false | Enable verbose output |
| `--quiet` | `-q` | flag | false | Suppress non-error output |
| `--format` | | choice | `table` | Output format: table, json, yaml, csv |
| `--no-color` | | flag | false | Disable colored output |
| `--log-file` | | path | | Log output to file |
| `--debug` | | flag | false | Enable debug mode |

### **Examples**

```bash
# Version information
plc-cl --version

# Verbose execution with JSON output
plc-cl --verbose --format=json schema list

# Debug mode with log file
plc-cl --debug --log-file=debug.log instance create --schema=standard-pid
```

---

## 🔧 Schema Commands

### **schema list**

List available schemas with filtering and sorting options.

```bash
plc-cl schema list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--type` | choice | | Filter by schema type: basic_pid, cascade, adaptive, mpc, custom |
| `--status` | choice | | Filter by status: active, deprecated, draft |
| `--search` | string | | Search in schema names and descriptions |
| `--sort-by` | choice | `name` | Sort by: name, type, version, modified |
| `--reverse` | flag | false | Reverse sort order |
| `--detailed` | flag | false | Show detailed information |
| `--limit` | integer | 50 | Maximum results to show |
| `--offset` | integer | 0 | Results offset for pagination |

**Examples:**

```bash
# List all schemas
plc-cl schema list

# Filter PID schemas
plc-cl schema list --type=basic_pid

# Search for cascade controllers
plc-cl schema list --search="cascade"

# Detailed view with latest modified first
plc-cl schema list --detailed --sort-by=modified --reverse
```

**Output Format:**

```json
{
  "schemas": [
    {
      "schema_id": "standard-pid",
      "type": "basic_pid",
      "version": "01.00.001",
      "title": "Standard PID Controller",
      "description": "Basic PID controller implementation",
      "author": "Control Team",
      "created": "2025-01-15T10:30:00Z",
      "modified": "2025-01-16T14:22:00Z",
      "status": "active"
    }
  ],
  "total_count": 15,
  "filtered_count": 3
}
```

### **schema info**

Get detailed information about a specific schema.

```bash
plc-cl schema info SCHEMA_ID [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `SCHEMA_ID` | string | yes | Schema identifier |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--show-properties` | flag | false | Include schema properties |
| `--show-validation` | flag | false | Include validation rules |
| `--show-examples` | flag | false | Include example instances |
| `--export` | choice | | Export format: json, yaml |
| `--output-file` | path | | Save to file instead of stdout |

**Examples:**

```bash
# Basic schema information
plc-cl schema info standard-pid

# Complete schema details
plc-cl schema info standard-pid --show-properties --show-validation

# Export schema definition
plc-cl schema info standard-pid --export=json --output-file=standard-pid.json
```

### **schema create**

Create a new schema.

```bash
plc-cl schema create [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--name` | string | | Schema name (required) |
| `--type` | choice | `basic_pid` | Schema type |
| `--description` | string | | Schema description |
| `--version` | string | `01.00.001` | Initial version |
| `--author` | string | | Author name |
| `--template` | string | | Base template name |
| `--interactive` | flag | false | Use interactive wizard |
| `--properties-file` | path | | Custom properties from file |
| `--validate` | flag | true | Validate schema after creation |

**Examples:**

```bash
# Interactive schema creation
plc-cl schema create --interactive

# Create from template
plc-cl schema create --name=my-cascade --template=cascade-basic

# Create with custom properties
plc-cl schema create \
  --name=distillation-pid \
  --type=cascade \
  --description="Distillation column temperature control" \
  --author="Process Engineer" \
  --properties-file=custom-props.json
```

### **schema modify**

Modify an existing schema.

```bash
plc-cl schema modify SCHEMA_ID [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `SCHEMA_ID` | string | yes | Schema to modify |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--description` | string | | Update description |
| `--add-property` | string | | Add custom property |
| `--remove-property` | string | | Remove property |
| `--update-validation` | path | | Update validation rules from file |
| `--increment-version` | choice | | Version increment: major, minor, patch |
| `--validate` | flag | true | Validate after modification |

### **schema validate**

Validate schema syntax and compliance.

```bash
plc-cl schema validate SCHEMA_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--strict` | flag | false | Enable strict validation |
| `--report-file` | path | | Save validation report |
| `--fix-issues` | flag | false | Auto-fix common issues |

### **schema test**

Test schema with example instances.

```bash
plc-cl schema test SCHEMA_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--instance-file` | path | | Test with specific instance |
| `--generate-examples` | flag | false | Generate test examples |
| `--example-count` | integer | 3 | Number of examples to generate |

---

## ⚙️ Instance Commands

### **instance list**

List control loop instances.

```bash
plc-cl instance list [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--schema` | string | | Filter by schema ID |
| `--status` | choice | | Filter by status: active, inactive, error |
| `--group-by` | choice | | Group by: schema, status, created |
| `--show-config` | flag | false | Include configuration summary |
| `--show-status` | flag | false | Include operational status |

### **instance create**

Create a new instance.

```bash
plc-cl instance create [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--schema` | string | | Base schema (required) |
| `--name` | string | | Instance name (required) |
| `--description` | string | | Instance description |
| `--config-file` | path | | Configuration from file |
| `--wizard` | flag | false | Use interactive wizard |
| `--validate` | flag | true | Validate after creation |

**PID-Specific Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--kp` | float | | Proportional gain |
| `--ki` | float | | Integral gain |
| `--kd` | float | | Derivative gain |
| `--setpoint` | float | | Initial setpoint |
| `--output-min` | float | | Minimum output limit |
| `--output-max` | float | | Maximum output limit |

### **instance info**

Get detailed instance information.

```bash
plc-cl instance info INSTANCE_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--show-config` | flag | false | Include full configuration |
| `--show-history` | flag | false | Include modification history |
| `--show-validation` | flag | false | Include validation status |

### **instance edit**

Edit instance parameters.

```bash
plc-cl instance edit INSTANCE_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--interactive` | flag | false | Interactive editor |
| `--config-file` | path | | Load configuration from file |
| `--validate` | flag | true | Validate changes |

### **instance validate**

Validate instance configuration.

```bash
plc-cl instance validate INSTANCE_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--strict` | flag | false | Strict validation mode |
| `--plc-verify` | flag | false | Verify against PLC tags |
| `--plc-host` | string | | PLC IP address for verification |

### **instance simulate**

Simulate instance behavior.

```bash
plc-cl instance simulate INSTANCE_ID [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--duration` | integer | 60 | Simulation duration (seconds) |
| `--input-file` | path | | Input data file |
| `--output-file` | path | | Save simulation results |
| `--real-time` | flag | false | Real-time simulation |

---

## 📦 Batch Commands

### **batch create**

Create multiple instances from batch data.

```bash
plc-cl batch create [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--from-csv` | path | | Create from CSV file |
| `--from-json` | path | | Create from JSON file |
| `--template` | string | | Base template for generation |
| `--count` | integer | | Number of instances to create |
| `--prefix` | string | | Name prefix for generated instances |
| `--parallel` | integer | 1 | Parallel processing threads |
| `--continue-on-error` | flag | false | Continue if individual items fail |
| `--dry-run` | flag | false | Show what would be created |

**CSV Format:**

```csv
name,schema,description,kp,ki,kd,setpoint
temp-01,standard-pid,Temperature Loop 1,2.5,0.1,0.05,80.0
temp-02,standard-pid,Temperature Loop 2,3.0,0.15,0.08,75.0
```

### **batch validate**

Validate multiple instances or files.

```bash
plc-cl batch validate [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--pattern` | string | | File pattern (glob) |
| `--directory` | path | | Directory to validate |
| `--files` | string | | Specific files (comma-separated) |
| `--report-file` | path | | Save validation report |
| `--report-format` | choice | `json` | Report format: json, html, csv |

### **batch export**

Export multiple instances.

```bash
plc-cl batch export [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--all` | flag | false | Export all instances |
| `--pattern` | string | | Instance name pattern |
| `--schema` | string | | Filter by schema |
| `--output-dir` | path | | Output directory |
| `--output-format` | choice | `json` | Export format |
| `--compress` | flag | false | Create compressed archive |

---

## 🏭 PLC Commands

### **instance plc connect**

Connect to ControlLogix PLC.

```bash
plc-cl instance plc connect [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--host` | string | | PLC IP address (required) |
| `--slot` | integer | 0 | PLC slot number |
| `--timeout` | integer | 30 | Connection timeout (seconds) |
| `--verify` | flag | false | Verify PLC compatibility |

### **instance plc browse**

Browse PLC tags.

```bash
plc-cl instance plc browse [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--filter` | string | `*` | Tag name filter (wildcards supported) |
| `--type` | choice | | Filter by data type |
| `--program` | string | | Filter by program name |
| `--limit` | integer | 100 | Maximum tags to show |
| `--tree-view` | flag | false | Show hierarchical tree |

### **instance plc read**

Read PLC tag values.

```bash
plc-cl instance plc read TAG_NAME [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `TAG_NAME` | string | yes | PLC tag name |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--format` | choice | `value` | Output format: value, detailed, json |
| `--timestamp` | flag | false | Include timestamp |
| `--quality` | flag | false | Include data quality |

### **instance plc read-batch**

Read multiple PLC tags.

```bash
plc-cl instance plc read-batch [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--tags` | path | | File containing tag list |
| `--tag-list` | string | | Comma-separated tag names |
| `--output-file` | path | | Save results to file |
| `--interval` | integer | | Repeat interval (seconds) |
| `--count` | integer | 1 | Number of readings |

### **instance plc monitor**

Monitor PLC tags in real-time.

```bash
plc-cl instance plc monitor TAG_NAME [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--interval` | integer | 1 | Update interval (seconds) |
| `--duration` | integer | | Monitoring duration (seconds) |
| `--output-file` | path | | Log data to file |
| `--alarm-high` | float | | High alarm threshold |
| `--alarm-low` | float | | Low alarm threshold |

---

## 🧠 Memory Commands

### **memory status**

Show memory system status.

```bash
plc-cl memory status [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--detailed` | flag | false | Show detailed metrics |
| `--databases` | flag | false | Show database status |

### **memory search**

Semantic search across memory system.

```bash
plc-cl memory search QUERY [OPTIONS]
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `QUERY` | string | yes | Search query |

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--limit` | integer | 10 | Maximum results |
| `--type` | choice | | Filter by content type |
| `--similarity` | float | 0.7 | Minimum similarity score |

### **memory recommend**

Get intelligent recommendations.

```bash
plc-cl memory recommend [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--schema` | string | | Base schema for recommendations |
| `--context` | string | | Application context |
| `--type` | choice | | Recommendation type |

---

## ⚙️ Configuration Commands

### **config show**

Display current configuration.

```bash
plc-cl config show [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--section` | string | | Show specific section |
| `--format` | choice | `table` | Output format |

### **config set**

Set configuration value.

```bash
plc-cl config set KEY VALUE
```

**Arguments:**

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `KEY` | string | yes | Configuration key |
| `VALUE` | string | yes | Configuration value |

### **config reset**

Reset configuration to defaults.

```bash
plc-cl config reset [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--section` | string | | Reset specific section |
| `--confirm` | flag | false | Skip confirmation prompt |

---

## 🖥️ Interactive Commands

### **repl**

Start interactive REPL mode.

```bash
plc-cl repl [OPTIONS]
```

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--verbose` | flag | false | Enable verbose output |
| `--save-session` | flag | false | Auto-save session on exit |
| `--load-session` | path | | Load saved session |

**REPL Commands:**

| Command | Description |
|---------|-------------|
| `help [command]` | Show help information |
| `history [limit]` | Show command history |
| `use <type> <name>` | Set current context |
| `show [object]` | Show current context |
| `save [filename]` | Save current session |
| `load <filename>` | Load session |
| `clear` | Clear screen |
| `exit` | Exit REPL |

---

## 📊 Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | Configuration error |
| 4 | Permission denied |
| 5 | Resource not found |
| 6 | Validation failed |
| 7 | Connection failed |
| 8 | Operation timeout |
| 9 | Interrupted by user |
| 10 | System error |

---

## 🌍 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLC_CL_CONFIG_DIR` | Configuration directory | `~/.plc-cl` |
| `PLC_CL_LOG_LEVEL` | Logging level | `INFO` |
| `PLC_CL_NO_COLOR` | Disable colors | `false` |
| `PLC_CL_TIMEOUT` | Default timeout | `30` |
| `PLC_CL_SCHEMA_REGISTRY` | Schema registry path | `./schemas` |
| `PLC_CL_INSTANCE_DIR` | Instance directory | `./instances` |
| `PLC_CL_MEMORY_URL` | Memory system URL | `localhost` |

---

## 📝 Configuration File Format

**Location**: `~/.plc-cl/config.yaml`

```yaml
# CLI Configuration
cli:
  default_output_format: table
  color_output: true
  verbose: false
  auto_save: true

# Schema settings
schema:
  registry_path: "./schemas/registry"
  default_type: "basic_pid"
  auto_validate: true
  backup_enabled: true

# Instance settings
instance:
  default_directory: "./instances"
  auto_backup: true
  validation_strict: false

# PLC settings
plc:
  default_timeout: 30
  connection_retries: 3
  read_timeout: 10
  default_slot: 0

# Memory system
memory:
  enabled: true
  auto_track: true
  recommendation_limit: 5
  search_limit: 20

# Batch processing
batch:
  default_parallel: 2
  continue_on_error: false
  progress_enabled: true

# Authentication
auth:
  required: false
  session_timeout: 3600
```

---

## 🔍 Advanced Usage Examples

### **Complex Schema Creation**

```bash
# Create advanced cascade controller
plc-cl schema create \
  --name=advanced-cascade-distillation \
  --type=cascade \
  --description="Advanced cascade controller for distillation column with feedforward" \
  --author="Process Control Team" \
  --version=01.00.001 \
  --properties-file=cascade-properties.json \
  --validate

# Verify schema
plc-cl schema test advanced-cascade-distillation --generate-examples
```

### **Batch Instance Creation with PLC Integration**

```bash
# Create instances from CSV
plc-cl batch create \
  --from-csv=production-controllers.csv \
  --parallel=4 \
  --continue-on-error \
  --verbose

# Validate all instances against PLC
plc-cl batch validate \
  --pattern="production-*.json" \
  --plc-verify \
  --plc-host=192.168.1.100 \
  --report-file=validation-report.html
```

### **Real-time PLC Monitoring**

```bash
# Connect to PLC
plc-cl instance plc connect --host=192.168.1.100 --slot=0

# Monitor critical tags
plc-cl instance plc monitor \
  "Program:MainProgram.Reactor_Temperature" \
  --interval=2 \
  --duration=3600 \
  --output-file=temperature-log.csv \
  --alarm-high=85.0 \
  --alarm-low=75.0
```

This API reference provides comprehensive documentation for all CLI commands, options, and usage patterns. 