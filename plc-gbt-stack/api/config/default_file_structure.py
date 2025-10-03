#!/usr/bin/env python3
"""
Default File Structure Configuration for PLC-GBT
Defines the baseline directory structure displayed in the file explorer
"""

from typing import Any

# Default folder structure with metadata
DEFAULT_FOLDER_STRUCTURE = {
    "name": "Root",
    "path": "/",
    "is_system": True,
    "description": "Root directory of PLC-GBT workspace",
    "children": [
        {
            "name": "projects",
            "category": "projects",
            "description": "PLC programming projects and solutions",
            "icon": "folder-git",
            "color": "#42a5f5",
            "is_system": True,
            "children": [
                {
                    "name": "active",
                    "description": "Currently active projects",
                    "readme": """# Active Projects

This folder contains projects you are currently working on.

## Organization Tips
- Keep one project per subfolder
- Include project documentation in each folder
- Use meaningful project names
""",
                },
                {
                    "name": "templates",
                    "description": "Project templates and starter files",
                    "readme": """# Project Templates

Reusable templates for common PLC programming patterns.

## Available Templates
- Basic PLC Project
- PID Control Loop
- State Machine Logic
- HMI Interface
""",
                },
                {
                    "name": "archived",
                    "description": "Completed or archived projects",
                    "readme": """# Archived Projects

Store completed projects here for reference.

## Best Practices
- Include completion date in folder name
- Keep final documentation
- Backup critical project files
""",
                },
            ],
        },
        {
            "name": "plc-programs",
            "category": "plc-programs",
            "description": "PLC program files (.acd, .l5x, etc.)",
            "icon": "cpu",
            "color": "#4fc3f7",
            "is_system": True,
            "children": [
                {
                    "name": "rockwell",
                    "description": "Rockwell Automation files (.acd, .l5x)",
                    "children": [
                        {
                            "name": "logix-5000",
                            "description": "Studio 5000 Logix programs",
                        },
                        {
                            "name": "rslogix-500",
                            "description": "RSLogix 500 programs",
                        },
                    ],
                },
                {
                    "name": "siemens",
                    "description": "Siemens TIA Portal files",
                    "children": [
                        {
                            "name": "s7-1200",
                            "description": "S7-1200 programs",
                        },
                        {
                            "name": "s7-1500",
                            "description": "S7-1500 programs",
                        },
                    ],
                },
                {
                    "name": "codesys",
                    "description": "CODESYS programs",
                },
                {
                    "name": "other",
                    "description": "Other PLC platforms",
                },
            ],
        },
        {
            "name": "workflows",
            "category": "workflows",
            "description": "Automation workflow definitions",
            "icon": "workflow",
            "color": "#ba68c8",
            "is_system": True,
            "children": [
                {
                    "name": "n8n",
                    "description": "N8N workflow files (.json)",
                    "readme": """# N8N Workflows

Store your N8N automation workflows here.

## Workflow Categories
- Data Processing
- PLC Integration
- Reporting & Analytics
- Alerting & Notifications
""",
                },
                {
                    "name": "custom",
                    "description": "Custom automation scripts",
                },
            ],
        },
        {
            "name": "control-loops",
            "category": "configurations",
            "description": "PID control loop configurations and tuning data",
            "icon": "activity",
            "color": "#66bb6a",
            "is_system": True,
            "children": [
                {
                    "name": "temperature",
                    "description": "Temperature control loops",
                    "readme": """# Temperature Control Loops

Store temperature control loop configurations here.

## Typical Applications
- Distillation columns
- Heat exchangers
- Proofing boxes
- Fermentation vessels
""",
                },
                {
                    "name": "flow",
                    "description": "Flow control loops",
                },
                {
                    "name": "pressure",
                    "description": "Pressure control loops",
                },
                {
                    "name": "level",
                    "description": "Level control loops",
                },
                {
                    "name": "cascade",
                    "description": "Cascade control configurations",
                },
                {
                    "name": "tuning-logs",
                    "description": "PID tuning session logs and data",
                },
            ],
        },
        {
            "name": "documentation",
            "category": "documentation",
            "description": "Project documentation and guides",
            "icon": "book-open",
            "color": "#66bb6a",
            "is_system": True,
            "children": [
                {
                    "name": "manuals",
                    "description": "Equipment and system manuals",
                },
                {
                    "name": "specifications",
                    "description": "Technical specifications",
                },
                {
                    "name": "procedures",
                    "description": "Operating procedures and SOPs",
                },
                {
                    "name": "diagrams",
                    "description": "P&ID, electrical, and network diagrams",
                },
            ],
        },
        {
            "name": "chat-histories",
            "category": "chat-histories",
            "description": "AI Assistant conversation histories",
            "icon": "message-square",
            "color": "#ffb74d",
            "is_system": True,
            "readme": """# AI Assistant Chat Histories

Your conversation histories with the AI Assistant are automatically saved here.

## Features
- Searchable conversation logs
- Timestamp-based organization
- Export and share capabilities

## Privacy Note
Chat histories are stored locally and are not shared externally.
""",
        },
        {
            "name": "configurations",
            "category": "configurations",
            "description": "System and equipment configuration files",
            "icon": "settings",
            "color": "#ff7043",
            "is_system": True,
            "children": [
                {
                    "name": "devices",
                    "description": "Device configuration files",
                },
                {
                    "name": "networks",
                    "description": "Network configurations",
                },
                {
                    "name": "system",
                    "description": "System-wide settings",
                },
            ],
        },
        {
            "name": "data",
            "category": "exports",
            "description": "Data exports and reports",
            "icon": "database",
            "color": "#90a4ae",
            "is_system": True,
            "children": [
                {
                    "name": "exports",
                    "description": "Exported data files",
                    "children": [
                        {
                            "name": "csv",
                            "description": "CSV data exports",
                        },
                        {
                            "name": "json",
                            "description": "JSON data exports",
                        },
                        {
                            "name": "excel",
                            "description": "Excel reports",
                        },
                    ],
                },
                {
                    "name": "reports",
                    "description": "Generated reports",
                    "children": [
                        {
                            "name": "performance",
                            "description": "Performance analysis reports",
                        },
                        {
                            "name": "compliance",
                            "description": "Compliance and audit reports",
                        },
                    ],
                },
                {
                    "name": "backups",
                    "description": "Data backups",
                },
            ],
        },
        {
            "name": "uploads",
            "category": "uploads",
            "description": "User uploaded files",
            "icon": "upload",
            "color": "#ffa726",
            "is_system": False,
            "readme": """# Uploads

This folder is for temporary file uploads.

## Usage
- Drag and drop files here
- Files uploaded via the UI appear here
- Organize files into appropriate folders after upload
""",
        },
        {
            "name": "scripts",
            "category": "documentation",
            "description": "Automation and utility scripts",
            "icon": "code",
            "color": "#78909c",
            "is_system": False,
            "children": [
                {
                    "name": "python",
                    "description": "Python scripts",
                },
                {
                    "name": "javascript",
                    "description": "JavaScript/Node.js scripts",
                },
                {
                    "name": "utilities",
                    "description": "Utility scripts and tools",
                },
            ],
        },
        {
            "name": "training-data",
            "category": "documentation",
            "description": "AI model training datasets",
            "icon": "brain",
            "color": "#9c27b0",
            "is_system": False,
            "children": [
                {
                    "name": "fine-tuning",
                    "description": "Fine-tuning datasets for AI models",
                },
                {
                    "name": "validation",
                    "description": "Validation and test datasets",
                },
            ],
        },
    ],
}


def flatten_folder_structure(
    structure: dict[str, Any],
    parent_path: str = "",
    result: list[dict[str, Any]] | None = None
) -> list[dict[str, Any]]:
    """
    Flatten hierarchical folder structure into a list

    Args:
        structure: Hierarchical folder structure
        parent_path: Parent path (for recursion)
        result: Accumulated result list

    Returns:
        Flattened list of folder definitions
    """
    if result is None:
        result = []

    # Handle root folder specially
    if structure["name"] == "Root":
        current_path = "/"
    else:
        # Ensure parent_path ends without slash, then add /name
        parent = parent_path.rstrip('/') if parent_path else ''
        current_path = f"{parent}/{structure['name']}" if parent else f"/{structure['name']}"

    folder_def = {
        "name": structure["name"],
        "path": current_path,
        "parent_path": parent_path if parent_path else "/",
        "category": structure.get("category"),
        "description": structure.get("description"),
        "icon": structure.get("icon"),
        "color": structure.get("color"),
        "is_system": structure.get("is_system", False),
        "readme": structure.get("readme"),
    }

    result.append(folder_def)

    # Process children
    for child in structure.get("children", []):
        flatten_folder_structure(child, current_path, result)

    return result


def get_default_folders() -> list[dict[str, Any]]:
    """
    Get flattened list of default folders
    
    Returns:
        List of folder definitions
    """
    return flatten_folder_structure(DEFAULT_FOLDER_STRUCTURE)


# Welcome README for root directory
ROOT_README = """# Welcome to PLC-GBT Industrial Automation IDE

PLC-GBT is a professional industrial automation development environment with AI-powered assistance.

## 📁 Workspace Structure

Your workspace is organized into the following areas:

### Projects (`/projects`)
- **active/** - Current working projects
- **templates/** - Reusable project templates
- **archived/** - Completed projects

### PLC Programs (`/plc-programs`)
Platform-specific PLC program files organized by manufacturer:
- Rockwell Automation (.acd, .l5x)
- Siemens TIA Portal
- CODESYS
- Other platforms

### Control Loops (`/control-loops`)
PID control loop configurations organized by process variable:
- Temperature, Flow, Pressure, Level
- Cascade control
- Tuning logs and data

### Workflows (`/workflows`)
Automation workflow definitions:
- N8N workflows
- Custom automation scripts

### Documentation (`/documentation`)
Project documentation and technical references:
- Equipment manuals
- Technical specifications
- Operating procedures
- P&ID and electrical diagrams

### Chat Histories (`/chat-histories`)
AI Assistant conversation logs - automatically saved for reference

### Data (`/data`)
Data exports, reports, and backups:
- CSV/JSON/Excel exports
- Performance reports
- Compliance documentation

### Configurations (`/configurations`)
System and device configuration files

### Scripts (`/scripts`)
Utility scripts and automation tools

### Training Data (`/training-data`)
AI model fine-tuning datasets

## 🚀 Getting Started

1. **Create a New Project**: Right-click in `/projects/active` → New Project
2. **Open PLC Program**: Import your .acd or .l5x file to `/plc-programs`
3. **Configure Control Loops**: Add loop configurations to `/control-loops`
4. **Ask AI Assistant**: Press `Ctrl+Shift+A` to open the AI Assistant

## 🤖 AI Assistant Features

- PLC programming assistance
- PID tuning recommendations
- Control theory guidance
- Code review and optimization
- Documentation generation

## 📚 Documentation

- [User Guide](https://plc-gbt.docs)
- [API Reference](https://plc-gbt.docs/api)
- [Control Theory Resources](https://plc-gbt.docs/control-theory)

## 🔧 Need Help?

- Press `F1` for keyboard shortcuts
- Click the `?` icon in the top-right for help
- Chat with the AI Assistant for instant support

---

**Version**: 1.0.0  
**Last Updated**: 2025-10-03  
**Environment**: Production
"""


# Category-specific README templates
CATEGORY_READMES = {
    "projects": """# Projects Directory

Organize your PLC programming projects here.

## Folder Structure

- **active/** - Projects you're currently working on
- **templates/** - Reusable project templates
- **archived/** - Completed or inactive projects

## Best Practices

1. **One project per folder** - Keep each project isolated
2. **Include documentation** - Add README.md to each project
3. **Version control** - Use descriptive folder names with dates
4. **Backup regularly** - Copy to `/data/backups` before major changes

## Example Project Structure

```
my-project/
├── README.md
├── program/
│   └── main.acd
├── documentation/
│   ├── requirements.md
│   └── testing.md
├── configs/
│   └── network.json
└── data/
    └── tuning-logs.csv
```
""",

    "control-loops": """# Control Loops Directory

Store PID control loop configurations and tuning data.

## Folder Organization

- **temperature/** - Temperature control (distillation, heating)
- **flow/** - Flow control (pumps, valves)
- **pressure/** - Pressure control (compressors, vessels)
- **level/** - Level control (tanks, sumps)
- **cascade/** - Cascade control configurations
- **tuning-logs/** - Tuning session data and logs

## Configuration File Format

Save loop configurations as JSON:

```json
{
  "loop_name": "DIST01_TEMP",
  "process_variable": "temperature",
  "setpoint": 175.0,
  "pid_parameters": {
    "kp": 2.5,
    "ki": 0.1,
    "kd": 0.05
  },
  "tuning_method": "Ziegler-Nichols",
  "last_tuned": "2025-10-03T10:30:00Z"
}
```

## AI Assistant Integration

The AI Assistant can:
- Recommend tuning parameters
- Analyze loop performance
- Suggest control improvements
- Generate tuning reports
""",
}


def get_category_readme(category: str) -> str | None:
    """
    Get README content for a category
    
    Args:
        category: Category name
        
    Returns:
        README content or None
    """
    return CATEGORY_READMES.get(category)

