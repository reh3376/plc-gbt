#!/usr/bin/env python3
"""
AI Enhancement Framework - Cursor Integration

Main integration module for Cursor IDE, providing seamless AI-assisted development.
This module orchestrates context management, memory persistence, and AI agent coordination.
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import logging

from .context_manager import ContextManager, get_context_manager
from .memory_persistence import MemoryPersistence, get_memory_persistence

logger = logging.getLogger(__name__)

@dataclass
class CursorConfiguration:
    """Cursor IDE configuration for AI Enhancement Framework."""
    workspace_path: str
    project_type: str
    ai_features_enabled: Dict[str, bool]
    context_settings: Dict[str, Any]
    memory_settings: Dict[str, Any]
    cursorrules_path: Optional[str] = None

class CursorIntegration:
    """
    Main Cursor IDE integration for the AI Enhancement Framework.
    
    Provides:
    - Automatic workspace detection and configuration
    - AI agent context management
    - Memory persistence coordination
    - Development workflow optimization
    """
    
    def __init__(self, workspace_path: Optional[str] = None):
        """Initialize Cursor integration."""
        self.workspace_path = Path(workspace_path or os.getcwd())
        self.context_manager: Optional[ContextManager] = None
        self.memory_persistence: Optional[MemoryPersistence] = None
        self.configuration: Optional[CursorConfiguration] = None
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize the Cursor integration system."""
        try:
            # Initialize core components
            self.context_manager = await get_context_manager()
            self.memory_persistence = await get_memory_persistence()
            
            # Load or create configuration
            await self._load_configuration()
            
            # Initialize workspace
            await self._initialize_workspace()
            
            self.is_initialized = True
            logger.info(f"Cursor Integration initialized for: {self.workspace_path}")
            
        except Exception as e:
            logger.error(f"Cursor Integration initialization failed: {e}")
            raise
    
    async def _load_configuration(self) -> None:
        """Load or create Cursor configuration."""
        cursorrules_file = self.workspace_path / ".cursorrules"
        config_file = self.workspace_path / ".ai_framework_config.json"
        
        # Detect project type
        project_type = await self._detect_project_type()
        
        # Load existing configuration or create default
        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = self._get_default_configuration(project_type)
            await self._save_configuration(config_data)
        
        # Create configuration object
        self.configuration = CursorConfiguration(
            workspace_path=str(self.workspace_path),
            project_type=project_type,
            ai_features_enabled=config_data.get("ai_features", {}),
            context_settings=config_data.get("context", {}),
            memory_settings=config_data.get("memory", {}),
            cursorrules_path=str(cursorrules_file) if cursorrules_file.exists() else None
        )
        
        # Ensure .cursorrules exists
        if not cursorrules_file.exists():
            await self._create_cursorrules_file(project_type)
            self.configuration.cursorrules_path = str(cursorrules_file)
    
    async def _initialize_workspace(self) -> None:
        """Initialize the workspace for AI-enhanced development."""
        if not self.configuration:
            raise ValueError("Configuration not loaded")
        
        # Create project context
        project_context = await self.context_manager.create_project_context(
            str(self.workspace_path),
            self.configuration.project_type,
            self.configuration.context_settings
        )
        
        # Create memory scope
        memory_scope = await self.memory_persistence.create_scope(
            str(self.workspace_path),
            isolation_level="project"
        )
        
        # Switch to project context
        await self.context_manager.switch_context(str(self.workspace_path))
        
        logger.info(f"Workspace initialized: {project_context.project_id}")
    
    async def get_workspace_status(self) -> Dict[str, Any]:
        """Get current workspace status and configuration."""
        if not self.is_initialized:
            return {"status": "not_initialized"}
        
        context = await self.context_manager.get_active_context()
        memory_stats = await self.memory_persistence.get_memory_statistics(
            context.project_id if context else None
        )
        
        return {
            "status": "initialized",
            "workspace_path": str(self.workspace_path),
            "project_type": self.configuration.project_type,
            "active_context": context.project_id if context else None,
            "ai_features": self.configuration.ai_features_enabled,
            "memory_statistics": memory_stats,
            "cursorrules_configured": self.configuration.cursorrules_path is not None
        }
    
    async def update_ai_features(self, features: Dict[str, bool]) -> None:
        """Update AI feature configuration."""
        if not self.configuration:
            raise ValueError("Configuration not loaded")
        
        self.configuration.ai_features_enabled.update(features)
        
        # Save configuration
        config_data = {
            "project_type": self.configuration.project_type,
            "ai_features": self.configuration.ai_features_enabled,
            "context": self.configuration.context_settings,
            "memory": self.configuration.memory_settings
        }
        await self._save_configuration(config_data)
        
        # Update environment variables
        await self._apply_feature_configuration()
        
        logger.info(f"Updated AI features: {features}")
    
    async def switch_project_mode(self, project_type: str) -> None:
        """Switch project mode and update configuration accordingly."""
        if not self.configuration:
            raise ValueError("Configuration not loaded")
        
        old_type = self.configuration.project_type
        self.configuration.project_type = project_type
        
        # Update context configuration
        await self.context_manager.update_context_config(
            self.configuration.workspace_path,
            {"project_type": project_type}
        )
        
        # Update cursorrules file
        await self._update_cursorrules_file(project_type)
        
        # Save configuration
        config_data = {
            "project_type": project_type,
            "ai_features": self.configuration.ai_features_enabled,
            "context": self.configuration.context_settings,
            "memory": self.configuration.memory_settings
        }
        await self._save_configuration(config_data)
        
        logger.info(f"Switched project mode from {old_type} to {project_type}")
    
    async def store_session_memory(self, memory_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store memory for the current session."""
        if not self.is_initialized:
            raise ValueError("Integration not initialized")
        
        context = await self.context_manager.get_active_context()
        if not context:
            raise ValueError("No active context")
        
        return await self.memory_persistence.store_memory(
            context.project_id,
            memory_type,
            content,
            metadata
        )
    
    async def retrieve_session_memory(self, memory_type: Optional[str] = None) -> List[Any]:
        """Retrieve memory for the current session."""
        if not self.is_initialized:
            raise ValueError("Integration not initialized")
        
        context = await self.context_manager.get_active_context()
        if not context:
            return []
        
        records = await self.memory_persistence.retrieve_memory(
            context.project_id,
            memory_type
        )
        
        return [record.content for record in records]
    
    async def _detect_project_type(self) -> str:
        """Detect project type based on workspace contents."""
        # Check for Python project
        if any((self.workspace_path / name).exists() for name in ["pyproject.toml", "requirements.txt", "setup.py"]):
            # More specific Python project detection
            if (self.workspace_path / "app.py").exists() or (self.workspace_path / "main.py").exists():
                return "web_api"
            elif (self.workspace_path / "notebooks").exists() or any(self.workspace_path.glob("*.ipynb")):
                return "data_science"
            elif (self.workspace_path / "models").exists() or (self.workspace_path / "train.py").exists():
                return "ml_project"
            else:
                return "python"
        
        # Check for JavaScript/TypeScript
        if (self.workspace_path / "package.json").exists():
            return "web_app"
        
        # Check for other project types
        if (self.workspace_path / "Cargo.toml").exists():
            return "rust"
        
        if (self.workspace_path / "go.mod").exists():
            return "go"
        
        # Default to python
        return "python"
    
    def _get_default_configuration(self, project_type: str) -> Dict[str, Any]:
        """Get default configuration for a project type."""
        base_config = {
            "ai_features": {
                "task_orchestrator": True,
                "memory_management": True,
                "code_analysis": True,
                "hallucination_detection": True,
                "context_awareness": True
            },
            "context": {
                "analysis_depth": "comprehensive",
                "code_quality_threshold": 85,
                "documentation_level": "detailed"
            },
            "memory": {
                "isolation_level": "project",
                "retention_days": 30,
                "compression_enabled": True
            }
        }
        
        # Project-specific overrides
        if project_type == "web_api":
            base_config["context"]["security_focus"] = True
            base_config["context"]["api_documentation"] = True
        elif project_type == "data_science":
            base_config["context"]["notebook_support"] = True
            base_config["context"]["visualization_enabled"] = True
        elif project_type == "ml_project":
            base_config["context"]["experiment_tracking"] = True
            base_config["context"]["model_versioning"] = True
        
        return base_config
    
    async def _create_cursorrules_file(self, project_type: str) -> None:
        """Create .cursorrules file for the project."""
        cursorrules_content = self._generate_cursorrules_content(project_type)
        
        cursorrules_path = self.workspace_path / ".cursorrules"
        with open(cursorrules_path, 'w') as f:
            f.write(cursorrules_content)
        
        logger.info(f"Created .cursorrules file for {project_type} project")
    
    async def _update_cursorrules_file(self, project_type: str) -> None:
        """Update existing .cursorrules file."""
        await self._create_cursorrules_file(project_type)
        logger.info(f"Updated .cursorrules file for {project_type} project")
    
    def _generate_cursorrules_content(self, project_type: str) -> str:
        """Generate .cursorrules content for project type."""
        return f"""# AI Enhancement Framework - Cursor Rules
# Generated for {project_type} project

# Core Framework Configuration
ai_framework:
  enabled: true
  mode: "development"
  version: "1.0.0"

# Project Configuration
project:
  type: "{project_type}"
  complexity: "moderate"
  
# AI Assistant Behavior
assistant:
  task_orchestrator:
    enabled: true
    analysis_depth: "comprehensive"
    methodical_approach: true
  
  memory:
    enabled: true
    project_scoped: true
    cross_session_persistence: true
  
  code_analysis:
    enabled: true
    real_time: true
    validation_on_save: true
    hallucination_detection: true

# Code Quality Standards
standards:
  code_quality:
    type_hints: "required"
    docstrings: "required"
    test_coverage: 95
  
  documentation:
    auto_generate: true
    mermaid_diagrams: true
    api_documentation: true

# Framework Integration
framework:
  ai_enhancement: true
  auto_analysis: true
  validation_on_save: true
  memory_persistence: true
"""
    
    async def _save_configuration(self, config_data: Dict[str, Any]) -> None:
        """Save configuration to file."""
        config_file = self.workspace_path / ".ai_framework_config.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    async def _apply_feature_configuration(self) -> None:
        """Apply feature configuration to environment."""
        if not self.configuration:
            return
        
        # Set environment variables for enabled features
        for feature, enabled in self.configuration.ai_features_enabled.items():
            env_var = f"AI_FRAMEWORK_{feature.upper()}"
            os.environ[env_var] = str(enabled).lower()
        
        # Set project type
        os.environ["AI_FRAMEWORK_PROJECT_TYPE"] = self.configuration.project_type

# Global integration instance
_cursor_integration = None

async def get_cursor_integration(workspace_path: Optional[str] = None) -> CursorIntegration:
    """Get the global Cursor integration instance."""
    global _cursor_integration
    if _cursor_integration is None:
        _cursor_integration = CursorIntegration(workspace_path)
        await _cursor_integration.initialize()
    return _cursor_integration

# Convenience functions
async def initialize_workspace(workspace_path: Optional[str] = None) -> CursorIntegration:
    """Initialize Cursor integration for a workspace."""
    integration = CursorIntegration(workspace_path)
    await integration.initialize()
    return integration

async def get_workspace_status() -> Dict[str, Any]:
    """Get current workspace status."""
    integration = await get_cursor_integration()
    return await integration.get_workspace_status()

async def store_ai_memory(memory_type: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
    """Store AI memory for current workspace."""
    integration = await get_cursor_integration()
    return await integration.store_session_memory(memory_type, content, metadata)

async def retrieve_ai_memory(memory_type: Optional[str] = None) -> List[Any]:
    """Retrieve AI memory for current workspace."""
    integration = await get_cursor_integration()
    return await integration.retrieve_session_memory(memory_type)

if __name__ == "__main__":
    # Example usage
    async def main():
        integration = CursorIntegration()
        await integration.initialize()
        
        # Get workspace status
        status = await integration.get_workspace_status()
        print(f"Workspace status: {status}")
        
        # Store some AI memory
        record_id = await integration.store_session_memory(
            "ai_context",
            {"current_task": "testing integration", "user_preferences": {"style": "clean"}},
            {"source": "cursor_integration_test"}
        )
        print(f"Stored memory: {record_id}")
        
        # Retrieve memory
        memories = await integration.retrieve_session_memory("ai_context")
        print(f"Retrieved {len(memories)} memories")
    
    asyncio.run(main()) 