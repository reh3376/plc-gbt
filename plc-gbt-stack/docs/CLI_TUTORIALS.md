# 🎓 PLC Control Loop CLI - Tutorial Walkthroughs

**Version**: 1.0.0  
**Date**: January 18, 2025  
**Author**: AI Task Orchestrator Implementation  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Getting Started Tutorial](#getting-started-tutorial)
2. [Schema Management Tutorial](#schema-management-tutorial)
3. [Instance Management Tutorial](#instance-management-tutorial)
4. [PLC Integration Tutorial](#plc-integration-tutorial)
5. [Batch Operations Tutorial](#batch-operations-tutorial)
6. [Interactive REPL Tutorial](#interactive-repl-tutorial)
7. [Advanced Workflows Tutorial](#advanced-workflows-tutorial)
8. [Troubleshooting Tutorial](#troubleshooting-tutorial)

---

## 🚀 Getting Started Tutorial

**Duration**: 15 minutes  
**Prerequisites**: CLI installed and configured  
**Goal**: Complete your first end-to-end workflow

### **Step 1: Check System Status**

```bash
# Verify CLI installation
./plc-cl --version

# Check system status
./plc-cl status
```

**Expected Output:**
```
✅ CLI Version: 1.0.0
✅ Configuration: ~/.plc-cl/config.yaml
✅ Schema Registry: 15 schemas available
✅ Memory System: Connected (Redis, Neo4j)
```

### **Step 2: Explore Available Schemas**

```bash
# List all available schemas
./plc-cl schema list
```

**What you'll see:**
- Standard PID controllers
- Cascade configurations
- Advanced control strategies

```bash
# Get details about a specific schema
./plc-cl schema info standard-pid
```

### **Step 3: Create Your First Instance**

```bash
# Create a simple PID controller instance
./plc-cl instance create \
  --schema=standard-pid \
  --name=my-first-controller \
  --description="My first control loop" \
  --kp=2.5 \
  --ki=0.1 \
  --kd=0.05
```

**Success Indicators:**
- ✅ Instance created successfully
- ✅ Configuration validated
- ✅ Added to registry

### **Step 4: Validate Your Instance**

```bash
# Validate the instance configuration
./plc-cl instance validate my-first-controller

# View instance details
./plc-cl instance info my-first-controller --show-config
```

### **Step 5: Try Interactive Mode**

```bash
# Enter REPL mode
./plc-cl repl
```

**In REPL:**
```bash
plc-cl> help
plc-cl> instance list
plc-cl> use instance my-first-controller
plc-cl> show
plc-cl> exit
```

### **🎯 Checkpoint: What You've Learned**

- ✅ How to check system status
- ✅ Schema exploration and information
- ✅ Instance creation with parameters
- ✅ Configuration validation
- ✅ Interactive mode basics

**Next Steps**: Complete the Schema Management Tutorial

---

## 🔧 Schema Management Tutorial

**Duration**: 30 minutes  
**Prerequisites**: Getting Started Tutorial completed  
**Goal**: Master schema creation, modification, and validation

### **Step 1: Understanding Schema Types**

```bash
# List schemas by type
./plc-cl schema list --type=basic_pid
./plc-cl schema list --type=cascade
./plc-cl schema list --type=adaptive
```

**Schema Types Overview:**
- **basic_pid**: Standard PID controller
- **cascade**: Master/slave PID configuration
- **adaptive**: Self-tuning PID
- **mpc**: Model Predictive Controller
- **custom**: User-defined schemas

### **Step 2: Detailed Schema Exploration**

```bash
# Examine a cascade controller
./plc-cl schema info cascade-pid --show-properties

# View validation rules
./plc-cl schema info cascade-pid --show-validation

# See example configurations
./plc-cl schema info cascade-pid --show-examples
```

### **Step 3: Create a Custom Schema (Wizard)**

```bash
# Launch interactive schema wizard
./plc-cl schema wizard
```

**Wizard Flow:**
1. **Choose Base Type**: Select "cascade"
2. **Basic Information**: 
   - Name: `my-distillation-cascade`
   - Description: `Cascade controller for distillation column`
3. **Custom Properties**: Add feedforward compensation
4. **Validation Rules**: Set parameter limits
5. **Review and Create**

### **Step 4: Create Schema from Command Line**

```bash
# Create schema with specific parameters
./plc-cl schema create \
  --name=temperature-cascade \
  --type=cascade \
  --description="Temperature cascade for reactor control" \
  --author="Process Engineer" \
  --version=01.00.001
```

### **Step 5: Modify Existing Schema**

```bash
# Add a custom property
./plc-cl schema modify temperature-cascade \
  --add-property=feed_forward_gain \
  --description="Enhanced with feedforward control"

# Update version
./plc-cl schema modify temperature-cascade \
  --increment-version=minor
```

### **Step 6: Schema Validation and Testing**

```bash
# Validate schema syntax
./plc-cl schema validate temperature-cascade

# Test with generated examples
./plc-cl schema test temperature-cascade --generate-examples

# Advanced validation
./plc-cl schema validate temperature-cascade --strict
```

### **Step 7: Schema Export and Backup**

```bash
# Export schema definition
./plc-cl schema info temperature-cascade \
  --export=json \
  --output-file=temperature-cascade-backup.json

# Export all schemas
./plc-cl batch export \
  --all \
  --output-dir=schema-backup/ \
  --output-format=json
```

### **🎯 Checkpoint: Advanced Schema Skills**

- ✅ Schema type understanding
- ✅ Interactive schema creation
- ✅ Command-line schema creation
- ✅ Schema modification and versioning
- ✅ Validation and testing
- ✅ Export and backup procedures

**Next Steps**: Instance Management Tutorial

---

## ⚙️ Instance Management Tutorial

**Duration**: 45 minutes  
**Prerequisites**: Schema Management Tutorial completed  
**Goal**: Master complete instance lifecycle management

### **Step 1: Instance Creation Strategies**

#### **Quick Creation**
```bash
# Simple instance with defaults
./plc-cl instance create \
  --schema=standard-pid \
  --name=reactor-temp-01
```

#### **Detailed Creation**
```bash
# Instance with full configuration
./plc-cl instance create \
  --schema=cascade-pid \
  --name=distillation-column-temp \
  --description="Main distillation column temperature control" \
  --kp=2.8 \
  --ki=0.15 \
  --kd=0.08 \
  --setpoint=82.5 \
  --output-min=0.0 \
  --output-max=100.0
```

#### **Wizard Creation**
```bash
# Interactive instance wizard
./plc-cl instance wizard --schema=cascade-pid
```

### **Step 2: Instance Configuration Management**

```bash
# View instance configuration
./plc-cl instance info distillation-column-temp --show-config

# Edit instance parameters
./plc-cl instance edit distillation-column-temp \
  --kp=3.2 \
  --description="Updated with optimized tuning"

# Interactive editing
./plc-cl instance edit distillation-column-temp --interactive
```

### **Step 3: Instance Validation and Testing**

```bash
# Basic validation
./plc-cl instance validate distillation-column-temp

# Strict validation with detailed report
./plc-cl instance validate distillation-column-temp \
  --strict \
  --report-file=validation-report.json

# Simulation testing
./plc-cl instance simulate distillation-column-temp \
  --duration=120 \
  --output-file=simulation-results.csv
```

### **Step 4: Instance Organization and Management**

```bash
# List instances by schema
./plc-cl instance list --schema=cascade-pid

# Group instances by type
./plc-cl instance list --group-by=schema

# Filter by status
./plc-cl instance list --status=active --show-status

# Search instances
./plc-cl instance list --search="distillation"
```

### **Step 5: Instance Export and Import**

```bash
# Export single instance
./plc-cl instance export distillation-column-temp \
  --format=json \
  --output-file=backup/distillation-config.json

# Export all instances for a schema
./plc-cl batch export \
  --schema=cascade-pid \
  --output-dir=cascade-backups/

# Import instance
./plc-cl instance import backup/distillation-config.json

# Convert between formats
./plc-cl instance convert distillation-config.json \
  --output-format=yaml \
  --output-file=distillation-config.yaml
```

### **Step 6: Instance Templates and Replication**

```bash
# Create template from existing instance
./plc-cl instance export distillation-column-temp \
  --format=template \
  --output-file=templates/distillation-template.json

# Create multiple instances from template
./plc-cl batch create \
  --template=distillation-template \
  --count=5 \
  --prefix=column \
  --suffix-format="{:02d}"
```

### **🎯 Checkpoint: Instance Mastery**

- ✅ Multiple instance creation methods
- ✅ Configuration management
- ✅ Validation and testing workflows
- ✅ Organization and filtering
- ✅ Export/import operations
- ✅ Template-based replication

**Next Steps**: PLC Integration Tutorial

---

## 🏭 PLC Integration Tutorial

**Duration**: 60 minutes  
**Prerequisites**: Access to ControlLogix PLC (or simulator)  
**Goal**: Complete PLC connectivity and data integration

### **Step 1: PLC Connection Setup**

```bash
# Test network connectivity
ping 192.168.1.100

# Connect to PLC
./plc-cl instance plc connect \
  --host=192.168.1.100 \
  --slot=0 \
  --timeout=30 \
  --verify
```

**Connection Verification:**
- ✅ Network connectivity confirmed
- ✅ PLC responding on EtherNet/IP
- ✅ Read-only access verified
- ✅ PLC program structure accessible

### **Step 2: PLC Tag Discovery**

```bash
# Browse all available tags
./plc-cl instance plc browse

# Browse with filter
./plc-cl instance plc browse --filter="Program:MainProgram.*"

# Hierarchical view
./plc-cl instance plc browse --tree-view

# Filter by data type
./plc-cl instance plc browse --type=REAL
```

**What You'll Discover:**
- Program organization
- Tag naming conventions
- Data types available
- Control loop structures

### **Step 3: Reading PLC Data**

```bash
# Read single tag
./plc-cl instance plc read "Program:MainProgram.Temperature_PV"

# Read with detailed information
./plc-cl instance plc read "Program:MainProgram.Temperature_PV" \
  --format=detailed \
  --timestamp \
  --quality

# Get tag information
./plc-cl instance plc tag-info "Program:MainProgram.Temperature_PV"
```

### **Step 4: Batch Tag Reading**

```bash
# Create tag list file
cat > critical_tags.txt << EOF
Program:MainProgram.Temperature_PV
Program:MainProgram.Temperature_SP
Program:MainProgram.Pressure_PV
Program:MainProgram.Level_PV
EOF

# Read multiple tags
./plc-cl instance plc read-batch \
  --tags=critical_tags.txt \
  --output-file=plc_snapshot.json \
  --format=json
```

### **Step 5: Real-time Monitoring**

```bash
# Monitor single tag
./plc-cl instance plc monitor \
  "Program:MainProgram.Temperature_PV" \
  --interval=2 \
  --duration=300 \
  --output-file=temperature_log.csv

# Monitor with alarms
./plc-cl instance plc monitor \
  "Program:MainProgram.Reactor_Temp" \
  --interval=1 \
  --alarm-high=85.0 \
  --alarm-low=75.0 \
  --duration=1800
```

### **Step 6: PLC-Instance Integration**

```bash
# Create instance mapped to PLC tags
./plc-cl instance create \
  --schema=standard-pid \
  --name=reactor-temp-plc \
  --description="Reactor temperature control mapped to PLC" \
  --plc-pv-tag="Program:MainProgram.Temperature_PV" \
  --plc-sp-tag="Program:MainProgram.Temperature_SP" \
  --plc-output-tag="Program:MainProgram.Temperature_Output"

# Validate instance against PLC
./plc-cl instance validate reactor-temp-plc \
  --plc-verify \
  --plc-host=192.168.1.100
```

### **Step 7: Advanced PLC Operations**

```bash
# Continuous data logging
./plc-cl instance plc monitor \
  "Program:MainProgram.Temperature_PV" \
  --interval=5 \
  --count=720 \
  --output-file=hourly_temp_data.csv

# Status monitoring
./plc-cl instance plc status

# Connection management
./plc-cl instance plc disconnect
./plc-cl instance plc connect --host=192.168.1.100
```

### **🎯 Checkpoint: PLC Integration Mastery**

- ✅ PLC connection establishment
- ✅ Tag discovery and browsing
- ✅ Single and batch tag reading
- ✅ Real-time monitoring setup
- ✅ Instance-PLC mapping
- ✅ Advanced monitoring and logging

**Next Steps**: Batch Operations Tutorial

---

## 📦 Batch Operations Tutorial

**Duration**: 45 minutes  
**Prerequisites**: Instance Management Tutorial completed  
**Goal**: Efficient batch processing for enterprise operations

### **Step 1: Preparing Batch Data**

#### **CSV Data Preparation**
```bash
# Create controllers specification
cat > production_controllers.csv << EOF
name,schema,description,kp,ki,kd,setpoint,plc_pv_tag,plc_sp_tag
reactor_01_temp,standard-pid,Reactor 1 Temperature,2.5,0.1,0.05,80.0,R01_TEMP_PV,R01_TEMP_SP
reactor_02_temp,standard-pid,Reactor 2 Temperature,2.8,0.12,0.06,82.0,R02_TEMP_PV,R02_TEMP_SP
reactor_01_press,cascade-pid,Reactor 1 Pressure,1.8,0.08,0.03,150.0,R01_PRESS_PV,R01_PRESS_SP
distill_temp,cascade-pid,Distillation Temperature,3.2,0.15,0.08,75.5,DIST_TEMP_PV,DIST_TEMP_SP
feed_flow,standard-pid,Feed Flow Control,1.5,0.05,0.02,100.0,FEED_FLOW_PV,FEED_FLOW_SP
EOF
```

#### **JSON Batch Configuration**
```bash
# Create JSON batch specification
cat > batch_config.json << EOF
{
  "batch_name": "production_controllers",
  "description": "Production control loop batch deployment",
  "default_schema": "standard-pid",
  "instances": [
    {
      "name": "reactor_03_temp",
      "schema": "standard-pid",
      "parameters": {"kp": 2.7, "ki": 0.11, "kd": 0.055}
    },
    {
      "name": "reactor_04_temp", 
      "schema": "standard-pid",
      "parameters": {"kp": 2.9, "ki": 0.13, "kd": 0.065}
    }
  ]
}
EOF
```

### **Step 2: Batch Instance Creation**

```bash
# Create instances from CSV
./plc-cl batch create \
  --from-csv=production_controllers.csv \
  --parallel=3 \
  --verbose \
  --continue-on-error

# Create instances from JSON
./plc-cl batch create \
  --from-json=batch_config.json \
  --validate \
  --parallel=2

# Generate instances from template
./plc-cl batch create \
  --template=standard-pid \
  --count=10 \
  --prefix=loop \
  --suffix-format="{:03d}" \
  --parallel=4
```

**Progress Tracking:**
- Real-time progress bars
- Success/failure counts
- Processing rate display
- Error summaries

### **Step 3: Batch Validation**

```bash
# Validate all instances in directory
./plc-cl batch validate \
  --pattern="instances/*.json" \
  --parallel=4 \
  --report-file=validation_report.html \
  --report-format=html

# Validate specific instance pattern
./plc-cl batch validate \
  --pattern="reactor_*" \
  --strict \
  --continue-on-error

# Validate with PLC verification
./plc-cl batch validate \
  --pattern="production_*.json" \
  --plc-verify \
  --plc-host=192.168.1.100 \
  --report-file=plc_validation.json
```

### **Step 4: Batch Export Operations**

```bash
# Export all instances for backup
./plc-cl batch export \
  --all \
  --output-dir=backup_$(date +%Y%m%d) \
  --output-format=json \
  --compress

# Export by schema type
./plc-cl batch export \
  --schema=cascade-pid \
  --output-dir=cascade_backup \
  --output-format=yaml

# Export with filtering
./plc-cl batch export \
  --pattern="reactor_*" \
  --output-dir=reactor_configs \
  --include-metadata
```

### **Step 5: Batch Import and Migration**

```bash
# Import from backup directory
./plc-cl batch import \
  --input-dir=backup_20250115 \
  --overwrite-existing \
  --validate \
  --parallel=3

# Import with filtering
./plc-cl batch import \
  --input-dir=legacy_configs \
  --pattern="*.yaml" \
  --convert-format=json \
  --validate
```

### **Step 6: Batch Conversion and Updates**

```bash
# Convert all JSON to YAML
./plc-cl batch convert \
  --pattern="*.json" \
  --output-format=yaml \
  --output-dir=yaml_configs \
  --parallel=4

# Update all instances with new parameter
./plc-cl batch update \
  --pattern="reactor_*" \
  --set-parameter="scan_time=0.1" \
  --validate \
  --backup-first
```

### **Step 7: Advanced Batch Workflows**

```bash
# Complete deployment workflow
#!/bin/bash
echo "🚀 Production Deployment Workflow"

# Step 1: Validate configurations
./plc-cl batch validate --pattern="production_*.json" --strict

# Step 2: Backup existing
./plc-cl batch export --all --output-dir="backup_$(date +%Y%m%d)" --compress

# Step 3: Deploy new configurations
./plc-cl batch create --from-csv=production_controllers.csv --parallel=4

# Step 4: Verify against PLC
./plc-cl batch validate --pattern="production_*" --plc-verify --plc-host=192.168.1.100

# Step 5: Generate deployment report
./plc-cl batch validate --all --report-file="deployment_report_$(date +%Y%m%d).html"

echo "✅ Deployment Complete"
```

### **🎯 Checkpoint: Batch Operations Mastery**

- ✅ CSV and JSON batch data preparation
- ✅ Parallel batch creation and processing
- ✅ Comprehensive batch validation
- ✅ Export operations with filtering
- ✅ Import and migration workflows
- ✅ Format conversion and updates
- ✅ Complete deployment workflows

**Next Steps**: Interactive REPL Tutorial

---

## 🖥️ Interactive REPL Tutorial

**Duration**: 30 minutes  
**Prerequisites**: Basic CLI familiarity  
**Goal**: Master interactive mode for efficient workflows

### **Step 1: Starting and Configuring REPL**

```bash
# Start basic REPL
./plc-cl repl

# Start with session saving
./plc-cl repl --save-session

# Start with verbose output
./plc-cl repl --verbose --save-session
```

**REPL Features:**
- Command auto-completion (Tab key)
- Command history (Arrow keys)
- Context awareness
- Session persistence

### **Step 2: Basic REPL Navigation**

```bash
# In REPL mode:
plc-cl> help                    # Show all commands
plc-cl> help schema            # Specific command help
plc-cl> history               # View command history
plc-cl> history 10            # Last 10 commands
plc-cl> clear                 # Clear screen
```

### **Step 3: Context Management**

```bash
# Set current schema context
plc-cl> use schema standard-pid
✅ Current schema set to: standard-pid

# Set current instance context  
plc-cl> use instance reactor-temp-01
✅ Current instance set to: reactor-temp-01

# Show current context
plc-cl> show
Current Context:
  Schema: standard-pid
  Instance: reactor-temp-01

# Context-aware operations
plc-cl> show schema            # Show current schema details
plc-cl> show instance          # Show current instance details
```

### **Step 4: Interactive Schema Operations**

```bash
# List schemas with context
plc-cl> schema list

# Get information about current schema
plc-cl> show schema

# Create new schema interactively
plc-cl> schema wizard

# Validate current schema
plc-cl> schema validate
```

### **Step 5: Interactive Instance Operations**

```bash
# List instances
plc-cl> instance list

# Create instance with current schema
plc-cl> instance create --name=new-controller

# Edit current instance
plc-cl> instance edit --interactive

# Validate current instance
plc-cl> instance validate
```

### **Step 6: Session Management**

```bash
# Save current session
plc-cl> save my-work-session
✅ Session saved to: ~/.plc-cl/sessions/my-work-session.json

# Load previous session
plc-cl> load my-work-session
✅ Session loaded: 15 commands restored

# Auto-save on exit
plc-cl> config set auto_save_session true
```

### **Step 7: Advanced REPL Features**

#### **Command Aliases**
```bash
# Set up command aliases
plc-cl> alias sl="schema list"
plc-cl> alias ii="instance info"
plc-cl> alias validate="instance validate"

# Use aliases
plc-cl> sl
plc-cl> ii reactor-temp-01
```

#### **Batch Operations in REPL**
```bash
# Quick batch validation
plc-cl> batch validate --pattern="reactor_*"

# Interactive batch creation
plc-cl> batch create --interactive
```

#### **PLC Operations in REPL**
```bash
# Connect to PLC
plc-cl> instance plc connect --host=192.168.1.100

# Browse tags interactively
plc-cl> instance plc browse --interactive

# Monitor with context
plc-cl> instance plc monitor "Temperature_PV" --interval=2
```

### **Step 8: Workflow Automation in REPL**

```bash
# Record workflow for automation
plc-cl> record start daily-checks
plc-cl> schema list --type=basic_pid
plc-cl> instance list --status=active
plc-cl> batch validate --pattern="production_*"
plc-cl> record stop
✅ Workflow recorded: daily-checks.repl

# Replay recorded workflow
plc-cl> replay daily-checks
```

### **🎯 Checkpoint: REPL Mastery**

- ✅ REPL startup and configuration
- ✅ Navigation and help systems
- ✅ Context management
- ✅ Interactive schema/instance operations
- ✅ Session save/load
- ✅ Advanced features and aliases
- ✅ Workflow recording and automation

**Next Steps**: Advanced Workflows Tutorial

---

## 🚀 Advanced Workflows Tutorial

**Duration**: 90 minutes  
**Prerequisites**: All previous tutorials completed  
**Goal**: Master complex real-world scenarios

### **Workflow 1: Complete Production Deployment**

```bash
#!/bin/bash
# Production Deployment Workflow
set -e

echo "🏭 Production Control Loop Deployment"
echo "======================================"

# Phase 1: Pre-deployment validation
echo "📋 Phase 1: Pre-deployment Validation"
./plc-cl schema validate-all --strict
./plc-cl instance validate-all --strict
./plc-cl memory status --detailed

# Phase 2: Backup current configuration
echo "💾 Phase 2: Configuration Backup"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
./plc-cl batch export --all --output-dir="$BACKUP_DIR" --compress
./plc-cl config export --file="$BACKUP_DIR/cli-config.yaml"

# Phase 3: Deploy new configurations
echo "🚀 Phase 3: New Configuration Deployment"
./plc-cl batch create --from-csv=production_controllers.csv --parallel=4 --continue-on-error

# Phase 4: PLC integration verification
echo "🏭 Phase 4: PLC Integration Verification"
./plc-cl instance plc connect --host=192.168.1.100 --verify
./plc-cl batch validate --pattern="production_*" --plc-verify --plc-host=192.168.1.100

# Phase 5: Performance validation
echo "📊 Phase 5: Performance Validation"
./plc-cl batch simulate --pattern="production_*" --duration=300 --parallel=2

# Phase 6: Generate deployment report
echo "📋 Phase 6: Deployment Report"
./plc-cl batch validate --all --report-file="deployment_report_$(date +%Y%m%d).html" --report-format=html

echo "✅ Production deployment complete!"
```

### **Workflow 2: Continuous Integration Pipeline**

```yaml
# .github/workflows/control-loop-ci.yml
name: Control Loop CI/CD

on:
  push:
    paths:
      - 'schemas/**'
      - 'instances/**'
      - 'tests/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup CLI
        run: |
          chmod +x plc-cl
          ./plc-cl --version
      
      - name: Validate Schemas
        run: |
          ./plc-cl batch validate --pattern="schemas/*.json" --strict --report-file=schema-validation.json
      
      - name: Validate Instances
        run: |
          ./plc-cl batch validate --pattern="instances/*.json" --strict --report-file=instance-validation.json
      
      - name: Run Simulations
        run: |
          ./plc-cl batch simulate --pattern="instances/*.json" --duration=60 --report-file=simulation-results.json
      
      - name: Generate Reports
        run: |
          ./plc-cl batch validate --all --report-file=ci-validation-report.html --report-format=html
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: validation-reports
          path: |
            *-validation.json
            ci-validation-report.html
```

### **Workflow 3: Multi-Site Configuration Management**

```bash
#!/bin/bash
# Multi-Site Configuration Synchronization

sites=("plant-a" "plant-b" "plant-c")
base_config="master-controllers.csv"

echo "🌐 Multi-Site Configuration Sync"
echo "==============================="

for site in "${sites[@]}"; do
    echo "📍 Processing site: $site"
    
    # Site-specific configuration
    site_config="${site}-controllers.csv"
    
    # Apply site-specific modifications
    ./plc-cl batch create \
        --from-csv="$site_config" \
        --prefix="$site" \
        --parallel=3 \
        --output-dir="sites/$site"
    
    # Validate against site PLC
    site_plc=$(grep "$site" site-plcs.txt | cut -d',' -f2)
    ./plc-cl batch validate \
        --pattern="sites/$site/*.json" \
        --plc-verify \
        --plc-host="$site_plc" \
        --report-file="$site-validation.json"
    
    # Deploy to site
    echo "🚀 Deploying to $site"
    rsync -av "sites/$site/" "$site-server:/opt/control-configs/"
    
    echo "✅ Site $site complete"
done

echo "🎉 Multi-site sync complete!"
```

### **Workflow 4: Automated Performance Optimization**

```bash
#!/bin/bash
# Automated Performance Optimization Workflow

echo "⚡ Performance Optimization Workflow"
echo "===================================="

# Step 1: Baseline performance measurement
echo "📊 Step 1: Baseline Measurement"
./plc-cl batch simulate \
    --pattern="production_*.json" \
    --duration=600 \
    --output-dir="baseline_results" \
    --parallel=4

# Step 2: Memory system optimization
echo "🧠 Step 2: Memory System Optimization"
./plc-cl memory optimize --aggressive
./plc-cl memory analytics --export=performance_metrics.json

# Step 3: Parameter tuning recommendations
echo "🎛️ Step 3: Parameter Tuning"
for instance in production_*.json; do
    instance_name=$(basename "$instance" .json)
    
    # Get AI recommendations
    recommendations=$(./plc-cl memory recommend \
        --instance="$instance_name" \
        --context="performance_optimization" \
        --format=json)
    
    # Apply recommendations
    ./plc-cl instance update "$instance_name" \
        --from-recommendations="$recommendations" \
        --validate
done

# Step 4: Performance verification
echo "✅ Step 4: Performance Verification"
./plc-cl batch simulate \
    --pattern="production_*.json" \
    --duration=600 \
    --output-dir="optimized_results" \
    --parallel=4

# Step 5: Compare and report
echo "📈 Step 5: Performance Analysis"
./plc-cl analyze performance-compare \
    --baseline="baseline_results" \
    --optimized="optimized_results" \
    --report-file="optimization_report.html"

echo "🎉 Optimization workflow complete!"
```

### **Workflow 5: Disaster Recovery Procedure**

```bash
#!/bin/bash
# Disaster Recovery Workflow

echo "🚨 Disaster Recovery Procedure"
echo "============================="

# Step 1: Assessment
echo "🔍 Step 1: System Assessment"
./plc-cl status --detailed > system_status.txt
./plc-cl memory status --databases > memory_status.txt

# Step 2: Identify latest backup
echo "💾 Step 2: Backup Identification"
latest_backup=$(ls -t backup_* | head -1)
echo "Latest backup found: $latest_backup"

# Step 3: Restore configuration
echo "🔄 Step 3: Configuration Restore"
./plc-cl batch import \
    --input-dir="$latest_backup" \
    --overwrite-existing \
    --validate \
    --parallel=4

# Step 4: Re-establish PLC connections
echo "🏭 Step 4: PLC Connection Restore"
while IFS=',' read -r instance plc_host; do
    echo "Connecting $instance to $plc_host"
    ./plc-cl instance plc connect \
        --instance="$instance" \
        --host="$plc_host" \
        --verify \
        --timeout=30
done < plc_connections.csv

# Step 5: Validation and verification
echo "✅ Step 5: System Validation"
./plc-cl batch validate --all --strict --report-file="recovery_validation.html"
./plc-cl memory status --detailed

# Step 6: Operational readiness check
echo "🎯 Step 6: Operational Readiness"
./plc-cl batch simulate \
    --pattern="critical_*.json" \
    --duration=120 \
    --report-file="readiness_check.json"

echo "🎉 Disaster recovery complete!"
```

### **🎯 Advanced Workflows Mastery**

- ✅ Production deployment automation
- ✅ CI/CD pipeline integration
- ✅ Multi-site configuration management
- ✅ Performance optimization workflows
- ✅ Disaster recovery procedures
- ✅ Complex error handling and reporting
- ✅ Integration with external systems

**Next Steps**: Troubleshooting Tutorial

---

## 🔧 Troubleshooting Tutorial

**Duration**: 45 minutes  
**Prerequisites**: Experience with basic CLI operations  
**Goal**: Diagnose and resolve common issues

### **Problem 1: Schema Not Found**

**Symptoms:**
```bash
$ ./plc-cl schema info my-schema
❌ Error: Schema 'my-schema' not found
```

**Diagnosis Steps:**
```bash
# Check schema registry location
./plc-cl config show | grep schema_registry

# List all available schemas
./plc-cl schema list --all

# Check file permissions
ls -la ~/.plc-cl/schemas/

# Verify schema file exists
find . -name "*my-schema*" -type f
```

**Solutions:**
```bash
# Solution 1: Update schema registry path
./plc-cl config set schema_registry /correct/path/to/schemas

# Solution 2: Re-register schema
./plc-cl schema register /path/to/my-schema.json

# Solution 3: Create missing schema
./plc-cl schema create --name=my-schema --interactive
```

### **Problem 2: PLC Connection Failed**

**Symptoms:**
```bash
$ ./plc-cl instance plc connect --host=192.168.1.100
❌ Error: Connection timeout - unable to reach PLC
```

**Diagnosis Steps:**
```bash
# Test network connectivity
ping 192.168.1.100

# Check port accessibility
telnet 192.168.1.100 44818

# Verify PLC configuration
./plc-cl instance plc connect --host=192.168.1.100 --debug

# Check firewall settings
sudo ufw status
```

**Solutions:**
```bash
# Solution 1: Correct IP address
./plc-cl instance plc connect --host=CORRECT_IP --slot=0

# Solution 2: Increase timeout
./plc-cl instance plc connect --host=192.168.1.100 --timeout=60

# Solution 3: Check PLC slot
./plc-cl instance plc connect --host=192.168.1.100 --slot=1

# Solution 4: Network troubleshooting
# - Verify PLC is powered and running
# - Check network cable connections
# - Verify VLAN configuration
```

### **Problem 3: Memory System Unavailable**

**Symptoms:**
```bash
$ ./plc-cl memory status
⚠️ Memory system unavailable: Connection refused
```

**Diagnosis Steps:**
```bash
# Check memory system configuration
./plc-cl config show | grep memory

# Test individual database connections
redis-cli ping
neo4j-admin status

# Check memory system logs
./plc-cl --debug memory status

# Verify database services
systemctl status redis
systemctl status neo4j
```

**Solutions:**
```bash
# Solution 1: Start required services
sudo systemctl start redis
sudo systemctl start neo4j

# Solution 2: Initialize memory system
./plc-cl memory init

# Solution 3: Reset memory configuration
./plc-cl config reset --section=memory
./plc-cl memory init --force

# Solution 4: Disable memory integration if not needed
./plc-cl config set memory.enabled false
```

### **Problem 4: Validation Failures**

**Symptoms:**
```bash
$ ./plc-cl instance validate my-controller
❌ Validation failed: Parameter 'kp' exceeds maximum allowed value
```

**Diagnosis Steps:**
```bash
# Get detailed validation information
./plc-cl instance validate my-controller --detailed

# Check schema constraints
./plc-cl schema info standard-pid --show-validation

# Examine instance configuration
./plc-cl instance info my-controller --show-config

# Compare with working instance
./plc-cl instance info working-controller --show-config
```

**Solutions:**
```bash
# Solution 1: Fix parameter values
./plc-cl instance edit my-controller --kp=2.5

# Solution 2: Use different schema
./plc-cl instance modify my-controller --schema=flexible-pid

# Solution 3: Create custom schema with relaxed constraints
./plc-cl schema create --name=custom-pid --based-on=standard-pid
./plc-cl schema modify custom-pid --relax-constraints

# Solution 4: Override validation (with caution)
./plc-cl instance validate my-controller --force-override
```

### **Problem 5: Batch Operation Failures**

**Symptoms:**
```bash
$ ./plc-cl batch create --from-csv=controllers.csv
❌ Error: Failed to create 5 out of 10 instances
```

**Diagnosis Steps:**
```bash
# Enable detailed error reporting
./plc-cl batch create --from-csv=controllers.csv --verbose --debug

# Check CSV file format
head -5 controllers.csv
./plc-cl batch validate-csv controllers.csv

# Test with single instance
./plc-cl instance create --schema=standard-pid --name=test-instance

# Check available schemas
./plc-cl schema list
```

**Solutions:**
```bash
# Solution 1: Fix CSV format issues
./plc-cl batch validate-csv controllers.csv --fix-format

# Solution 2: Continue on errors
./plc-cl batch create --from-csv=controllers.csv --continue-on-error

# Solution 3: Reduce parallel operations
./plc-cl batch create --from-csv=controllers.csv --parallel=1

# Solution 4: Split large batches
split -l 10 controllers.csv batch_
for file in batch_*; do
    ./plc-cl batch create --from-csv="$file"
done
```

### **Problem 6: Performance Issues**

**Symptoms:**
```bash
$ ./plc-cl schema list
# Takes 30+ seconds to respond
```

**Diagnosis Steps:**
```bash
# Check system resources
./plc-cl status --performance

# Monitor memory usage
./plc-cl memory status --detailed

# Enable performance profiling
./plc-cl --profile schema list

# Check database performance
./plc-cl memory analyze-performance
```

**Solutions:**
```bash
# Solution 1: Optimize memory system
./plc-cl memory optimize --aggressive

# Solution 2: Clear caches
./plc-cl memory clear-cache
./plc-cl config clear-cache

# Solution 3: Reduce concurrent operations
./plc-cl config set batch.default_parallel 1

# Solution 4: Database maintenance
./plc-cl memory maintenance --vacuum --reindex
```

### **Diagnostic Commands Summary**

| Issue Type | Diagnostic Command | Description |
|------------|-------------------|-------------|
| **General** | `./plc-cl status --detailed` | System health overview |
| **Configuration** | `./plc-cl config show` | Current configuration |
| **Schema** | `./plc-cl schema validate-all` | All schema validation |
| **Instance** | `./plc-cl instance validate-all` | All instance validation |
| **PLC** | `./plc-cl instance plc status` | PLC connection status |
| **Memory** | `./plc-cl memory status --detailed` | Memory system health |
| **Performance** | `./plc-cl --profile COMMAND` | Performance profiling |
| **Debug** | `./plc-cl --debug COMMAND` | Detailed debug output |

### **🎯 Troubleshooting Mastery**

- ✅ Systematic problem diagnosis
- ✅ Common issue resolution
- ✅ Performance optimization
- ✅ Configuration troubleshooting
- ✅ Network and connectivity issues
- ✅ Database and memory problems
- ✅ Validation and batch processing issues

---

## 🎓 Tutorial Completion Certificate

**Congratulations!** You have completed all PLC Control Loop CLI tutorials and mastered:

✅ **Getting Started** - Basic CLI navigation and first workflows  
✅ **Schema Management** - Complete schema lifecycle management  
✅ **Instance Management** - Control loop instance mastery  
✅ **PLC Integration** - Real-world PLC connectivity and data access  
✅ **Batch Operations** - Enterprise-scale batch processing  
✅ **Interactive REPL** - Efficient interactive workflows  
✅ **Advanced Workflows** - Complex real-world scenarios  
✅ **Troubleshooting** - Problem diagnosis and resolution  

**You are now qualified to:**
- Deploy production control loop configurations
- Integrate with industrial PLC systems
- Automate complex control system workflows
- Troubleshoot and optimize CLI operations
- Train other team members on CLI usage

**Next Steps:**
- Apply skills to real production environments
- Contribute to schema and instance libraries
- Develop custom plugins and extensions
- Share knowledge with the automation community

**Support Resources:**
- Documentation: `./plc-cl help`
- Community: [GitHub Issues](https://github.com/your-org/plc-gbt)
- Advanced Training: Contact your automation team lead

**Happy Automating!** 🚀 