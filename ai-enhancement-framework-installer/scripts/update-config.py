#!/usr/bin/env python3
"""
AI Enhancement Framework - Configuration Update Script

Updates and maintains AI Enhancement Framework configuration files.
This script handles configuration migration, validation, and optimization.
"""

import os
import json
import argparse
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import yaml
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigurationUpdater:
    """
    Configuration update and maintenance system.
    
    Features:
    - Configuration file migration
    - Settings validation and optimization
    - Project type detection and adaptation
    - Backup and rollback capabilities
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize the configuration updater."""
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.config_files = {
            ".cursorrules": self._update_cursorrules,
            ".ai_framework_config.json": self._update_framework_config,
            "pyproject.toml": self._update_pyproject,
            ".vscode/settings.json": self._update_vscode_settings
        }
        
    async def update_all_configurations(self, project_type: Optional[str] = None) -> Dict[str, Any]:
        """Update all configuration files."""
        print("🔧 AI Enhancement Framework - Configuration Update")
        print("=" * 50)
        
        results = {
            "updated_files": [],
            "errors": [],
            "warnings": [],
            "project_type": project_type or await self._detect_project_type()
        }
        
        # Create backup
        backup_dir = await self._create_backup()
        results["backup_location"] = str(backup_dir)
        
        # Update each configuration file
        for config_file, update_func in self.config_files.items():
            try:
                config_path = self.workspace_path / config_file
                
                if config_path.exists() or config_file in [".cursorrules", ".ai_framework_config.json"]:
                    print(f"\n📝 Updating {config_file}...")
                    
                    updated = await update_func(results["project_type"])
                    
                    if updated:
                        results["updated_files"].append(config_file)
                        print(f"  ✅ Updated {config_file}")
                    else:
                        results["warnings"].append(f"{config_file} was already up to date")
                        print(f"  ℹ️  {config_file} already up to date")
                
            except Exception as e:
                error_msg = f"Failed to update {config_file}: {e}"
                results["errors"].append(error_msg)
                print(f"  ❌ {error_msg}")
                logger.error(error_msg)
        
        # Generate summary
        await self._print_summary(results)
        
        return results
    
    async def _detect_project_type(self) -> str:
        """Detect project type based on workspace contents."""
        # Check for Python project indicators
        python_files = [
            "pyproject.toml", "requirements.txt", "setup.py", "setup.cfg",
            "Pipfile", "poetry.lock", "conda.yaml", "environment.yml"
        ]
        
        if any((self.workspace_path / f).exists() for f in python_files):
            # More specific Python project detection
            if (self.workspace_path / "app.py").exists() or any(self.workspace_path.glob("**/app.py")):
                return "web_api"
            elif (self.workspace_path / "notebooks").exists() or any(self.workspace_path.glob("*.ipynb")):
                return "data_science"
            elif (self.workspace_path / "models").exists() or (self.workspace_path / "train.py").exists():
                return "ml_project"
            elif (self.workspace_path / "manage.py").exists():
                return "django"
            elif (self.workspace_path / "app").exists() and (self.workspace_path / "app" / "__init__.py").exists():
                return "flask"
            else:
                return "python"
        
        # Check for JavaScript/TypeScript
        if (self.workspace_path / "package.json").exists():
            package_json_path = self.workspace_path / "package.json"
            try:
                with open(package_json_path, 'r') as f:
                    package_data = json.load(f)
                
                dependencies = package_data.get("dependencies", {})
                dev_dependencies = package_data.get("devDependencies", {})
                all_deps = {**dependencies, **dev_dependencies}
                
                if "react" in all_deps or "next" in all_deps:
                    return "react"
                elif "vue" in all_deps:
                    return "vue"
                elif "angular" in all_deps or "@angular/core" in all_deps:
                    return "angular"
                elif "express" in all_deps:
                    return "node_api"
                else:
                    return "javascript"
            except Exception:
                return "javascript"
        
        # Check for other project types
        if (self.workspace_path / "Cargo.toml").exists():
            return "rust"
        if (self.workspace_path / "go.mod").exists():
            return "go"
        if (self.workspace_path / "CMakeLists.txt").exists():
            return "cpp"
        if (self.workspace_path / "pom.xml").exists():
            return "java"
        
        # Default to python
        return "python"
    
    async def _create_backup(self) -> Path:
        """Create backup of existing configuration files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.workspace_path / ".ai_framework" / "backups" / f"config_backup_{timestamp}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        for config_file in self.config_files.keys():
            config_path = self.workspace_path / config_file
            if config_path.exists():
                backup_path = backup_dir / config_file
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file content
                with open(config_path, 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
        
        logger.info(f"Created configuration backup: {backup_dir}")
        return backup_dir
    
    async def _update_cursorrules(self, project_type: str) -> bool:
        """Update .cursorrules file."""
        cursorrules_path = self.workspace_path / ".cursorrules"
        
        # Generate updated content
        new_content = self._generate_cursorrules_content(project_type)
        
        # Check if update is needed
        if cursorrules_path.exists():
            with open(cursorrules_path, 'r') as f:
                current_content = f.read()
            
            if current_content.strip() == new_content.strip():
                return False
        
        # Write updated content
        with open(cursorrules_path, 'w') as f:
            f.write(new_content)
        
        return True
    
    async def _update_framework_config(self, project_type: str) -> bool:
        """Update .ai_framework_config.json file."""
        config_path = self.workspace_path / ".ai_framework_config.json"
        
        # Generate updated configuration
        new_config = self._generate_framework_config(project_type)
        
        # Load existing configuration if it exists
        existing_config = {}
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    existing_config = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing config: {e}")
        
        # Merge configurations (preserve user customizations)
        merged_config = self._merge_configs(existing_config, new_config)
        
        # Check if update is needed
        if existing_config == merged_config:
            return False
        
        # Write updated configuration
        with open(config_path, 'w') as f:
            json.dump(merged_config, f, indent=2)
        
        return True
    
    async def _update_pyproject(self, project_type: str) -> bool:
        """Update pyproject.toml file if it exists."""
        pyproject_path = self.workspace_path / "pyproject.toml"
        
        if not pyproject_path.exists():
            return False
        
        try:
            import toml
            
            # Read existing pyproject.toml
            with open(pyproject_path, 'r') as f:
                pyproject_data = toml.load(f)
            
            # Add AI Framework specific configurations
            updated = False
            
            # Add tool.ai_framework section
            if "tool" not in pyproject_data:
                pyproject_data["tool"] = {}
            
            if "ai_framework" not in pyproject_data["tool"]:
                pyproject_data["tool"]["ai_framework"] = {}
                updated = True
            
            ai_framework_config = {
                "enabled": True,
                "project_type": project_type,
                "analysis_depth": "comprehensive",
                "code_quality_threshold": 85
            }
            
            for key, value in ai_framework_config.items():
                if key not in pyproject_data["tool"]["ai_framework"]:
                    pyproject_data["tool"]["ai_framework"][key] = value
                    updated = True
            
            if updated:
                with open(pyproject_path, 'w') as f:
                    toml.dump(pyproject_data, f)
            
            return updated
            
        except ImportError:
            logger.warning("toml package not available, skipping pyproject.toml update")
            return False
        except Exception as e:
            logger.error(f"Failed to update pyproject.toml: {e}")
            return False
    
    async def _update_vscode_settings(self, project_type: str) -> bool:
        """Update VSCode/Cursor settings.json file."""
        vscode_dir = self.workspace_path / ".vscode"
        settings_path = vscode_dir / "settings.json"
        
        # Create .vscode directory if it doesn't exist
        vscode_dir.mkdir(exist_ok=True)
        
        # Generate updated settings
        new_settings = self._generate_vscode_settings(project_type)
        
        # Load existing settings
        existing_settings = {}
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    existing_settings = json.load(f)
            except Exception as e:
                logger.warning(f"Could not read existing VSCode settings: {e}")
        
        # Merge settings
        merged_settings = self._merge_configs(existing_settings, new_settings)
        
        # Check if update is needed
        if existing_settings == merged_settings:
            return False
        
        # Write updated settings
        with open(settings_path, 'w') as f:
            json.dump(merged_settings, f, indent=2)
        
        return True
    
    def _generate_cursorrules_content(self, project_type: str) -> str:
        """Generate .cursorrules content for project type."""
        return f"""# AI Enhancement Framework - Cursor Rules
# Auto-generated for {project_type} project
# Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

# Core Framework Configuration
ai_framework:
  enabled: true
  mode: "development"
  version: "1.0.0"

# Project Configuration
project:
  type: "{project_type}"
  complexity: "moderate"
  workspace_path: "{self.workspace_path}"
  
# AI Assistant Behavior
assistant:
  task_orchestrator:
    enabled: true
    analysis_depth: "comprehensive"
    methodical_approach: true
    validation_strict: true
  
  memory:
    enabled: true
    project_scoped: true
    cross_session_persistence: true
    retention_days: 30
  
  code_analysis:
    enabled: true
    real_time: true
    validation_on_save: true
    hallucination_detection: true
    quality_threshold: 85

# Code Quality Standards
standards:
  code_quality:
    type_hints: "required"
    docstrings: "required"
    test_coverage: 95
    complexity_limit: 10
  
  documentation:
    auto_generate: true
    mermaid_diagrams: true
    api_documentation: true
    inline_comments: true

# Project-Specific Settings
{self._get_project_specific_rules(project_type)}

# Framework Integration
framework:
  ai_enhancement: true
  auto_analysis: true
  validation_on_save: true
  memory_persistence: true
  context_awareness: true
"""
    
    def _get_project_specific_rules(self, project_type: str) -> str:
        """Get project-specific rules for cursorrules."""
        rules = {
            "python": """python:
  style: "pep8"
  formatter: "black"
  linter: ["flake8", "mypy"]
  testing: "pytest"
  type_checking: "strict" """,
            
            "web_api": """web_api:
  framework: "fastapi"
  api_docs: "openapi"
  security: "high"
  testing: "pytest"
  validation: "pydantic" """,
            
            "data_science": """data_science:
  notebook_support: true
  visualization: "matplotlib"
  data_processing: "pandas"
  experiment_tracking: true
  reproducibility: "high" """,
            
            "ml_project": """ml_project:
  framework: "pytorch"
  experiment_tracking: "mlflow"
  model_versioning: true
  data_validation: true
  deployment_ready: true """,
            
            "react": """react:
  typescript: true
  styling: "css-modules"
  testing: "jest"
  linting: "eslint"
  formatting: "prettier" """,
            
            "node_api": """node_api:
  typescript: true
  framework: "express"
  testing: "jest"
  api_docs: "swagger"
  security: "high" """
        }
        
        return rules.get(project_type, rules["python"])
    
    def _generate_framework_config(self, project_type: str) -> Dict[str, Any]:
        """Generate framework configuration."""
        base_config = {
            "version": "1.0.0",
            "project_type": project_type,
            "last_updated": datetime.now().isoformat(),
            "ai_features": {
                "task_orchestrator": True,
                "memory_management": True,
                "code_analysis": True,
                "hallucination_detection": True,
                "context_awareness": True,
                "performance_monitoring": True
            },
            "context": {
                "analysis_depth": "comprehensive",
                "code_quality_threshold": 85,
                "documentation_level": "detailed",
                "validation_strict": True
            },
            "memory": {
                "isolation_level": "project",
                "retention_days": 30,
                "compression_enabled": True,
                "cleanup_interval_hours": 24
            },
            "performance": {
                "max_response_time_ms": 2000,
                "cache_enabled": True,
                "optimization_level": "balanced"
            }
        }
        
        # Project-specific overrides
        project_configs = {
            "web_api": {
                "context": {
                    "security_focus": True,
                    "api_documentation": True,
                    "performance_monitoring": True
                }
            },
            "data_science": {
                "context": {
                    "notebook_support": True,
                    "visualization_enabled": True,
                    "data_validation": True
                }
            },
            "ml_project": {
                "context": {
                    "experiment_tracking": True,
                    "model_versioning": True,
                    "deployment_ready": True
                }
            }
        }
        
        if project_type in project_configs:
            base_config = self._merge_configs(base_config, project_configs[project_type])
        
        return base_config
    
    def _generate_vscode_settings(self, project_type: str) -> Dict[str, Any]:
        """Generate VSCode/Cursor settings."""
        base_settings = {
            "ai.framework.enabled": True,
            "ai.framework.mode": "development",
            "ai.framework.project_type": project_type,
            "ai.framework.analysis_on_save": True,
            "ai.framework.memory_persistence": True,
            "files.associations": {
                "*.cursorrules": "yaml"
            },
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": True
            }
        }
        
        # Project-specific settings
        if project_type == "python":
            base_settings.update({
                "python.defaultInterpreterPath": "./venv/bin/python",
                "python.linting.enabled": True,
                "python.linting.pylintEnabled": False,
                "python.linting.flake8Enabled": True,
                "python.formatting.provider": "black",
                "python.testing.pytestEnabled": True
            })
        elif project_type in ["react", "javascript", "node_api"]:
            base_settings.update({
                "typescript.preferences.includePackageJsonAutoImports": "auto",
                "eslint.enable": True,
                "prettier.enable": True
            })
        
        return base_settings
    
    def _merge_configs(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configurations, preserving existing values."""
        result = existing.copy()
        
        for key, value in new.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            elif key not in result:
                result[key] = value
        
        return result
    
    async def _print_summary(self, results: Dict[str, Any]) -> None:
        """Print update summary."""
        print("\n" + "=" * 50)
        print("📊 Configuration Update Summary:")
        print(f"  Project Type: {results['project_type']}")
        print(f"  Updated Files: {len(results['updated_files'])}")
        print(f"  Warnings: {len(results['warnings'])}")
        print(f"  Errors: {len(results['errors'])}")
        
        if results['updated_files']:
            print(f"  ✅ Files Updated:")
            for file in results['updated_files']:
                print(f"    • {file}")
        
        if results['warnings']:
            print(f"  ⚠️  Warnings:")
            for warning in results['warnings']:
                print(f"    • {warning}")
        
        if results['errors']:
            print(f"  ❌ Errors:")
            for error in results['errors']:
                print(f"    • {error}")
        
        print(f"\n💾 Backup created: {results['backup_location']}")

async def main():
    """Main configuration update function."""
    parser = argparse.ArgumentParser(
        description="Update AI Enhancement Framework configuration"
    )
    parser.add_argument(
        "--project-type",
        choices=["python", "web_api", "data_science", "ml_project", "react", "javascript", "node_api"],
        help="Override project type detection"
    )
    parser.add_argument(
        "--workspace",
        help="Workspace path (default: current directory)"
    )
    parser.add_argument(
        "--backup-only",
        action="store_true",
        help="Create backup without updating"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create updater
    updater = ConfigurationUpdater(args.workspace)
    
    if args.backup_only:
        backup_dir = await updater._create_backup()
        print(f"✅ Backup created: {backup_dir}")
        return
    
    # Run updates
    results = await updater.update_all_configurations(args.project_type)
    
    # Exit with appropriate code
    if results["errors"]:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    import sys
    asyncio.run(main()) 