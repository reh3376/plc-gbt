#!/usr/bin/env python3
"""
Migration script to help transition from monolithic ai_task_orchestrator.py
to the new modular plc_orchestrator package.

This script:
1. Updates import statements
2. Shows mapping of old to new functionality
3. Provides examples of updated usage patterns
"""

import re
import sys
from pathlib import Path

# Mapping of old imports to new imports
IMPORT_MAPPING = {
    # Old monolithic imports -> New modular imports
    "from ai_task_orchestrator import AITaskOrchestrator": "from plc_orchestrator import AITaskOrchestrator",
    "from ai_task_orchestrator import TaskComplexity": "from plc_orchestrator import TaskComplexity",
    "from ai_task_orchestrator import ValidationTier": "from plc_orchestrator import ValidationTier",
    "from ai_task_orchestrator import analyze_and_plan_task": "# analyze_and_plan_task is now orchestrator.analyze_task()",
    "from ai_task_orchestrator import validate_task_completion": "# validate_task_completion is now orchestrator.validate_implementation()",
    "import ai_task_orchestrator": "import plc_orchestrator",
}


# Function name changes
FUNCTION_MAPPING = {
    "analyze_and_plan_task": "orchestrator.analyze_task",
    "validate_task_completion": "orchestrator.validate_implementation",
    "get_task_guidance": "orchestrator.control_handler.get_guidance",
    "find_similar_implementations": "# Use memory system: orchestrator.memory_coordinator.query",
    "complete_task_with_mandatory_documentation": "orchestrator.create_summary_document",
    "update_roadmap_for_phase_completion": "# Moved to separate documentation module",
}


class MigrationHelper:
    """Helps migrate code from old to new structure."""

    def __init__(self):
        self.changes_made = []

    def analyze_file(self, file_path: Path) -> list[str]:
        """Analyze a file for needed migrations."""
        issues = []

        try:
            content = file_path.read_text()

            # Check imports
            for old_import in IMPORT_MAPPING:
                if old_import in content:
                    issues.append(f"Found old import: {old_import}")

            # Check function calls
            for old_func in FUNCTION_MAPPING:
                if re.search(rf"\b{old_func}\s*\(", content):
                    issues.append(f"Found old function call: {old_func}")

            # Check for direct instantiation
            if "AITaskOrchestrator(" in content and "task_id=" in content:
                issues.append("Found old instantiation pattern")

        except Exception as e:
            issues.append(f"Error reading file: {e}")

        return issues

    def migrate_imports(self, content: str) -> tuple[str, list[str]]:
        """Migrate import statements."""
        changes = []

        for old_import, new_import in IMPORT_MAPPING.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes.append(f"Updated import: {old_import} -> {new_import}")

        return content, changes

    def migrate_code(self, content: str) -> tuple[str, list[str]]:
        """Migrate code patterns."""
        changes = []

        # Update instantiation
        old_pattern = r'orchestrator = AITaskOrchestrator\(task_id="([^"]+)"\)'
        new_pattern = r'orchestrator = create_orchestrator(task_id="\1")'

        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            changes.append("Updated orchestrator instantiation to use create_orchestrator()")

        # Add import for create_orchestrator if needed
        if "create_orchestrator" in content and "from plc_orchestrator import" in content:
            import_line = re.search(r"from plc_orchestrator import (.+)", content)
            if import_line and "create_orchestrator" not in import_line.group(1):
                new_imports = import_line.group(1) + ", create_orchestrator"
                content = content.replace(
                    import_line.group(0), f"from plc_orchestrator import {new_imports}"
                )
                changes.append("Added create_orchestrator to imports")

        return content, changes

    def show_migration_guide(self):
        """Print migration guide."""
        print("""
# AI Task Orchestrator Migration Guide

## Overview
The AI Task Orchestrator has been refactored from a single 3000+ line file
into a modular package structure for better maintainability.

## Key Changes

### 1. Import Changes
```python
# Old
from ai_task_orchestrator import AITaskOrchestrator, TaskComplexity

# New
from plc_orchestrator import AITaskOrchestrator, TaskComplexity
# OR use the convenience function
from plc_orchestrator import create_orchestrator
```

### 2. Instantiation
```python
# Old
orchestrator = AITaskOrchestrator(task_id="task_123")

# New (recommended)
orchestrator = create_orchestrator(task_id="task_123")

# New (with configuration)
orchestrator = create_orchestrator(
    enable_memory=True,
    enable_math_validation=True,
    log_level="INFO"
)
```

### 3. Function Changes
```python
# Old standalone functions
analysis = analyze_and_plan_task("Build a PLC controller")
result = validate_task_completion(code, requirements)

# New methods on orchestrator
orchestrator = create_orchestrator()
analysis = orchestrator.analyze_task("Build a PLC controller")
result = orchestrator.validate_implementation(code, requirements)
```

### 4. New Package Structure
```
plc_orchestrator/
├── core/           # Core orchestration logic
├── memory/         # Memory system integration
├── domain/         # Domain-specific handlers
├── validation/     # Validation modules
├── config/         # Configuration management
└── utils/          # Utilities and helpers
```

### 5. Configuration
The new system uses Pydantic for configuration with environment variable support:

```python
# .env file
ENABLE_MEMORY=true
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO

# Python code
orchestrator = create_orchestrator()  # Automatically loads .env
```

### 6. Memory System (Optional)
The memory system is now optional and modular:

```python
# Disable if dependencies not available
orchestrator = create_orchestrator(enable_memory=False)
```

## Migration Steps

1. Update imports using the mapping above
2. Replace standalone function calls with orchestrator methods
3. Update instantiation to use create_orchestrator()
4. Review configuration options
5. Test thoroughly

## Benefits

- **Modularity**: Each component in its own module
- **Maintainability**: ~500 lines per module vs 3000+ line file
- **Flexibility**: Optional features can be disabled
- **Testing**: Easier to test individual components
- **Configuration**: Environment-based configuration
""")


def main():
    """Main migration function."""
    helper = MigrationHelper()

    if len(sys.argv) > 1:
        # Analyze specific file
        file_path = Path(sys.argv[1])
        if file_path.exists():
            print(f"Analyzing {file_path}...")
            issues = helper.analyze_file(file_path)

            if issues:
                print("\nIssues found:")
                for issue in issues:
                    print(f"  - {issue}")

                print("\nWould you like to see the migration guide? (y/n)")
                if input().lower() == "y":
                    helper.show_migration_guide()
            else:
                print("No migration issues found!")
        else:
            print(f"File not found: {file_path}")
    else:
        # Show general migration guide
        helper.show_migration_guide()

        print("\n\nTo analyze a specific file, run:")
        print("  python migrate_to_modular.py <your_file.py>")


if __name__ == "__main__":
    main()
