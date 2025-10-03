#!/usr/bin/env python3
"""
Create README files for all category folders in the file storage system
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.services.file_storage_service import FileStorageService

# README content for each category
README_TEMPLATES = {
    "/projects": """# Projects Directory

This directory contains all project files organized by status.

## Structure

- **active/**: Currently active projects
  - **hmi/**: Human-Machine Interface projects
  - **scada/**: SCADA system projects  
  - **reports/**: Project reports and documentation
- **templates/**: Project templates for quick setup
- **archived/**: Completed or archived projects

## Usage

1. Create new projects in the `active/` directory
2. Use templates from `templates/` for standardized project structure
3. Move completed projects to `archived/` for long-term storage

## Best Practices

- Use descriptive project names
- Include a README.md in each project
- Document project dependencies and requirements
- Regular backups to `archived/` upon completion
""",

    "/plc-programs": """# PLC Programs Directory

Industrial PLC program files organized by manufacturer.

## Structure

- **rockwell/**: Allen-Bradley/Rockwell Automation programs
  - **rslogix/**: RSLogix 5000 projects (.ACD files)
  - **studio5000/**: Studio 5000 projects
- **siemens/**: Siemens PLC programs
  - **tia-portal/**: TIA Portal projects
  - **step7/**: STEP 7 projects
- **codesys/**: CODESYS-based PLC programs
- **other/**: Programs for other PLC platforms

## Supported File Types

- `.acd` - RSLogix/Studio 5000 Archives
- `.l5x` - Logix Import/Export files
- `.zap` - TIA Portal archives
- `.s7p` - STEP 7 projects

## Best Practices

- Always export programs before editing
- Maintain version control for critical programs
- Document program changes in comments
- Test changes in simulation before deployment
""",

    "/workflows": """# Workflows Directory

Automation workflows and process definitions.

## Structure

- **n8n/**: n8n workflow definitions (JSON)
- **custom/**: Custom automation scripts

## Workflow Categories

1. **Data Collection**: Automated data gathering workflows
2. **Alerting**: Notification and alarm workflows
3. **Reporting**: Automated report generation
4. **Integration**: System integration workflows
5. **Maintenance**: Scheduled maintenance tasks

## Creating Workflows

1. Design workflow in n8n interface
2. Export as JSON
3. Store in appropriate subdirectory
4. Document workflow purpose and triggers

## Best Practices

- Use descriptive workflow names
- Include error handling in all workflows
- Test workflows in development before production
- Document external dependencies
""",

    "/control-loops": """# Control Loops Directory

PID control loop configurations and tuning data.

## Structure

- **temperature/**: Temperature control loops
- **flow/**: Flow control loops
- **pressure/**: Pressure control loops
- **level/**: Level control loops
- **cascade/**: Cascade control configurations
- **tuning-logs/**: Historical tuning data and logs

## Control Loop Data

Each control loop should include:
- Current PID parameters (Kp, Ki, Kd)
- Tuning history and rationale
- Process variable characteristics
- Setpoint ranges and limits
- Safety limits and alarms

## Tuning Methods Supported

- Ziegler-Nichols
- Cohen-Coon
- Lambda Tuning
- IMC (Internal Model Control)
- Relay Feedback
- Genetic Algorithm

## Best Practices

- Document all parameter changes
- Record tuning method used
- Save tuning logs before modifications
- Test changes during low-impact periods
- Monitor performance after tuning
""",

    "/documentation": """# Documentation Directory

Technical documentation, manuals, and specifications.

## Structure

- **manuals/**: Equipment and system manuals
- **specifications/**: Technical specifications
- **procedures/**: Standard operating procedures
- **diagrams/**: P&ID, electrical, and system diagrams

## Document Types

- **Manuals**: Equipment operation and maintenance guides
- **Specifications**: System requirements and capabilities
- **Procedures**: Step-by-step operational procedures
- **Diagrams**: Visual representations of systems

## Organization Guidelines

1. Use clear, descriptive filenames
2. Include version numbers in documents
3. Maintain revision history
4. Link related documents
5. Regular review and updates

## Best Practices

- Keep documents up-to-date
- Use standard templates
- Include creation/revision dates
- Cross-reference related documents
- Maintain both PDF and source files
""",

    "/configurations": """# Configurations Directory

System and device configuration files.

## Structure

- **devices/**: Individual device configurations
- **networks/**: Network and communication settings
- **system/**: System-wide configuration files

## Configuration Management

### Device Configurations
- IP addresses and network settings
- Device-specific parameters
- Calibration data
- Communication protocols

### Network Configurations
- Network topology
- VLAN configurations
- Firewall rules
- Routing tables

### System Configurations
- Application settings
- User preferences
- Security policies
- Backup schedules

## Best Practices

- Version control all configurations
- Test changes before deployment
- Maintain backup configurations
- Document configuration changes
- Use descriptive filenames
""",

    "/data": """# Data Directory

Exported data, reports, and backups.

## Structure

- **exports/**: Data exports from various systems
- **reports/**: Generated reports and analytics
- **backups/**: System and data backups

## Data Management

### Exports
- Raw data exports
- CSV, JSON, or Excel formats
- Timestamped for traceability

### Reports
- Automated report generation
- Historical data analysis
- Performance metrics

### Backups
- Regular system backups
- Configuration backups
- Critical data snapshots

## Retention Policy

- **Exports**: 90 days
- **Reports**: 1 year
- **Backups**: 30 days (daily), 1 year (monthly)

## Best Practices

- Regular automated backups
- Verify backup integrity
- Compress large exports
- Include metadata with exports
- Document data sources
""",

    "/uploads": """# Uploads Directory

User-uploaded files and temporary storage.

## Purpose

This directory serves as a landing zone for:
- User-uploaded files
- Temporary file storage
- Files pending processing
- External data imports

## File Processing Workflow

1. Files uploaded to this directory
2. Automated validation and scanning
3. Processing or conversion as needed
4. Move to appropriate permanent location
5. Cleanup of processed files

## Storage Limits

- Individual file size: 100MB
- Total directory size: 1GB
- Retention: 7 days for unprocessed files

## Best Practices

- Upload files with descriptive names
- Include metadata when possible
- Clean up temporary files regularly
- Scan uploads for security
- Move processed files promptly
""",

    "/scripts": """# Scripts Directory

Automation scripts and utilities.

## Structure

- **python/**: Python automation scripts
- **javascript/**: JavaScript/Node.js scripts
- **utilities/**: General-purpose utility scripts

## Script Categories

### Python Scripts
- Data processing and analysis
- System automation
- Integration scripts
- Batch operations

### JavaScript Scripts
- Frontend utilities
- API integration
- Data transformation
- Testing scripts

### Utilities
- Shell scripts
- Batch files
- One-off automation tasks

## Development Guidelines

1. Include clear documentation
2. Add usage examples
3. Handle errors gracefully
4. Use configuration files
5. Log operations appropriately

## Best Practices

- Follow language-specific style guides
- Include requirements/dependencies
- Version control all scripts
- Test before deployment
- Document script purpose and usage
""",

    "/training-data": """# Training Data Directory

Data for AI model training and validation.

## Structure

- **fine-tuning/**: Training datasets for model fine-tuning
  - **datasets/**: Training data in various formats
  - **models/**: Trained model artifacts
- **validation/**: Validation and test datasets

## Data Organization

### Fine-Tuning Datasets
- JSONL format for OpenAI fine-tuning
- CSV for general ML tasks
- Labeled and annotated data
- Preprocessed training data

### Model Artifacts
- Trained model files
- Model metadata and configs
- Training metrics and logs
- Version information

### Validation Datasets
- Hold-out test sets
- Cross-validation data
- Benchmark datasets
- Performance metrics

## Data Quality Guidelines

1. Clean and preprocess data
2. Remove duplicates
3. Balance training sets
4. Validate data integrity
5. Document data sources

## Best Practices

- Version control datasets
- Document preprocessing steps
- Maintain data lineage
- Regular validation checks
- Secure sensitive data
""",

    "/chat-histories": """# Chat Histories Directory

AI Assistant conversation histories for reference and analysis.

## Purpose

This directory stores:
- AI Assistant chat sessions
- Conversation histories
- Context and reference data
- Conversation analytics

## File Format

Chat histories are stored as JSON files with:
- Conversation ID
- Timestamp
- Message history
- User context
- AI responses

## Usage

1. **Reference**: Review past conversations
2. **Analysis**: Analyze conversation patterns
3. **Training**: Fine-tune AI models
4. **Debugging**: Troubleshoot AI responses

## Privacy and Retention

- Conversations contain user interactions
- Retain for 90 days by default
- Archive important conversations
- Regular cleanup of old sessions

## Best Practices

- Use descriptive save names
- Review and clean sensitive data
- Export important conversations
- Regular maintenance and cleanup
""",
}


def main():
    """Create README files for all category folders"""
    # Initialize service
    storage_root = os.getenv('FILE_STORAGE_ROOT', '/Users/reh3376/repos/plc-gbt/file-storage')
    db_url = os.getenv('DATABASE_URL', 'postgresql://plc_user:postgres_password@localhost:5432/plc_gbt')

    service = FileStorageService(db_url, storage_root)

    print("Creating README files for category folders...")
    created_count = 0
    skipped_count = 0

    for folder_path, readme_content in README_TEMPLATES.items():
        try:
            # Check if README already exists
            existing_files = service.list_files(folder_path, limit=100)
            readme_exists = any(f['name'].lower() == 'readme.md' for f in existing_files)

            if readme_exists:
                print(f"⏭️  README already exists: {folder_path}")
                skipped_count += 1
                continue

            # Upload README
            service.upload_file(
                file_content=readme_content.encode('utf-8'),
                filename="README.md",
                folder_path=folder_path,
                category_name="documentation",
                created_by="system",
                description=f"Category README for {folder_path}",
                tags=["readme", "documentation", "category"],
                metadata={
                    "auto_generated": True,
                    "category": folder_path.strip('/'),
                    "version": "1.0"
                }
            )

            print(f"✅ Created README: {folder_path}/README.md")
            created_count += 1

        except Exception as e:
            print(f"❌ Error creating README for {folder_path}: {e}")

    print("\n📊 Summary:")
    print(f"   Created: {created_count}")
    print(f"   Skipped: {skipped_count}")
    print(f"   Total: {len(README_TEMPLATES)}")


if __name__ == "__main__":
    main()

