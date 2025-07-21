#!/usr/bin/env python3
"""
AI Enhancement Framework - Context Manager

Provides dynamic context loading and management for AI-assisted development.
This module enables intelligent context switching and project-specific AI memory.
"""

import json
import os
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProjectContext:
    """Represents a project's AI context configuration."""
    project_id: str
    project_type: str
    project_path: str
    context_config: Dict[str, Any]
    last_updated: datetime
    ai_preferences: Dict[str, Any]
    memory_scope: str = "project"

@dataclass
class ContextSession:
    """Represents an active AI context session."""
    session_id: str
    project_context: ProjectContext
    active_files: List[str]
    current_task: Optional[str]
    ai_state: Dict[str, Any]
    created_at: datetime

class ContextManager:
    """
    Manages AI context for dynamic loading and intelligent switching.
    
    Features:
    - Dynamic context loading based on project type
    - Project-specific AI memory scoping
    - Intelligent context switching between projects
    - Performance optimization for context operations
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """Initialize the context manager."""
        self.base_path = base_path or Path.cwd()
        self.contexts: Dict[str, ProjectContext] = {}
        self.active_session: Optional[ContextSession] = None
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> None:
        """Initialize the context manager and load existing contexts."""
        try:
            await self._load_existing_contexts()
            await self._setup_context_directories()
            logger.info("Context Manager initialized successfully")
        except Exception as e:
            logger.error(f"Context Manager initialization failed: {e}")
            raise
    
    async def _load_existing_contexts(self) -> None:
        """Load existing project contexts from storage."""
        context_file = self.base_path / ".ai_contexts.json"
        
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    contexts_data = json.load(f)
                
                for ctx_id, ctx_data in contexts_data.items():
                    ctx_data['last_updated'] = datetime.fromisoformat(ctx_data['last_updated'])
                    self.contexts[ctx_id] = ProjectContext(**ctx_data)
                    
                logger.info(f"Loaded {len(self.contexts)} existing contexts")
            except Exception as e:
                logger.warning(f"Could not load existing contexts: {e}")
    
    async def _setup_context_directories(self) -> None:
        """Create necessary directories for context storage."""
        context_dir = self.base_path / ".ai_framework" / "contexts"
        context_dir.mkdir(parents=True, exist_ok=True)
    
    async def create_project_context(
        self, 
        project_path: str,
        project_type: str = "python",
        ai_preferences: Optional[Dict[str, Any]] = None
    ) -> ProjectContext:
        """
        Create a new project context.
        
        Args:
            project_path: Path to the project
            project_type: Type of project (python, web_api, data_science, etc.)
            ai_preferences: AI assistant preferences
            
        Returns:
            Created ProjectContext
        """
        project_id = self._generate_project_id(project_path)
        
        # Default AI preferences based on project type
        default_preferences = self._get_default_preferences(project_type)
        if ai_preferences:
            default_preferences.update(ai_preferences)
        
        # Default context configuration
        context_config = {
            "analysis_depth": "comprehensive",
            "code_quality_threshold": 85,
            "documentation_level": "detailed",
            "testing_framework": self._detect_testing_framework(project_path),
            "lint_tools": self._detect_lint_tools(project_path),
            "ai_features": {
                "task_orchestrator": True,
                "memory_management": True,
                "code_analysis": True,
                "hallucination_detection": True
            }
        }
        
        project_context = ProjectContext(
            project_id=project_id,
            project_type=project_type,
            project_path=project_path,
            context_config=context_config,
            last_updated=datetime.now(),
            ai_preferences=default_preferences,
            memory_scope="project"
        )
        
        self.contexts[project_id] = project_context
        await self._save_contexts()
        
        logger.info(f"Created project context: {project_id} ({project_type})")
        return project_context
    
    async def load_project_context(self, project_path: str) -> Optional[ProjectContext]:
        """
        Load context for a specific project.
        
        Args:
            project_path: Path to the project
            
        Returns:
            ProjectContext if found, None otherwise
        """
        project_id = self._generate_project_id(project_path)
        
        if project_id in self.contexts:
            return self.contexts[project_id]
        
        # Try to auto-detect and create context
        if Path(project_path).exists():
            project_type = await self._detect_project_type(project_path)
            return await self.create_project_context(project_path, project_type)
        
        return None
    
    async def switch_context(self, project_path: str) -> ContextSession:
        """
        Switch to a different project context.
        
        Args:
            project_path: Path to the project to switch to
            
        Returns:
            New ContextSession
        """
        project_context = await self.load_project_context(project_path)
        
        if not project_context:
            raise ValueError(f"Could not load context for project: {project_path}")
        
        # End current session
        if self.active_session:
            await self._end_session(self.active_session)
        
        # Create new session
        session = ContextSession(
            session_id=self._generate_session_id(),
            project_context=project_context,
            active_files=[],
            current_task=None,
            ai_state={},
            created_at=datetime.now()
        )
        
        self.active_session = session
        
        # Apply context configuration
        await self._apply_context_configuration(project_context)
        
        logger.info(f"Switched to context: {project_context.project_id}")
        return session
    
    async def get_active_context(self) -> Optional[ProjectContext]:
        """Get the currently active project context."""
        if self.active_session:
            return self.active_session.project_context
        return None
    
    async def update_context_config(
        self, 
        project_id: str, 
        config_updates: Dict[str, Any]
    ) -> None:
        """
        Update context configuration for a project.
        
        Args:
            project_id: Project identifier
            config_updates: Configuration updates to apply
        """
        if project_id not in self.contexts:
            raise ValueError(f"Project context not found: {project_id}")
        
        context = self.contexts[project_id]
        context.context_config.update(config_updates)
        context.last_updated = datetime.now()
        
        await self._save_contexts()
        
        # If this is the active context, apply changes
        if (self.active_session and 
            self.active_session.project_context.project_id == project_id):
            await self._apply_context_configuration(context)
        
        logger.info(f"Updated context config for: {project_id}")
    
    async def get_context_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for context operations."""
        return {
            "total_contexts": len(self.contexts),
            "active_session": self.active_session.session_id if self.active_session else None,
            "cache_size": len(self.context_cache),
            "memory_usage": self._estimate_memory_usage(),
            "last_switch_time": (
                self.active_session.created_at.isoformat() 
                if self.active_session else None
            )
        }
    
    def _generate_project_id(self, project_path: str) -> str:
        """Generate a unique project identifier."""
        abs_path = os.path.abspath(project_path)
        return abs_path.replace("/", "_").replace("\\", "_").replace(":", "")
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    
    def _get_default_preferences(self, project_type: str) -> Dict[str, Any]:
        """Get default AI preferences for a project type."""
        preferences = {
            "python": {
                "code_style": "pep8",
                "type_hints": "required",
                "docstring_style": "google",
                "testing_preference": "pytest",
                "linting": ["flake8", "black", "isort"]
            },
            "web_api": {
                "framework": "fastapi",
                "api_documentation": "openapi",
                "testing_preference": "pytest",
                "security_focus": "high",
                "performance_monitoring": True
            },
            "data_science": {
                "notebook_preference": "jupyter",
                "visualization": "matplotlib",
                "data_processing": "pandas",
                "ml_framework": "scikit-learn",
                "documentation": "detailed"
            },
            "ml_project": {
                "ml_framework": "pytorch",
                "experiment_tracking": "mlflow",
                "model_versioning": True,
                "performance_monitoring": True,
                "documentation": "comprehensive"
            }
        }
        
        return preferences.get(project_type, preferences["python"])
    
    async def _detect_project_type(self, project_path: str) -> str:
        """Detect project type based on files and structure."""
        path = Path(project_path)
        
        # Check for specific files
        if (path / "requirements.txt").exists() or (path / "pyproject.toml").exists():
            if (path / "app.py").exists() or (path / "main.py").exists():
                return "web_api"
            elif any((path / name).exists() for name in ["*.ipynb", "notebooks"]):
                return "data_science"
            elif (path / "models").exists() or (path / "train.py").exists():
                return "ml_project"
            else:
                return "python"
        
        # Check for JavaScript/TypeScript
        if (path / "package.json").exists():
            return "web_app"
        
        # Default to python
        return "python"
    
    def _detect_testing_framework(self, project_path: str) -> str:
        """Detect testing framework used in the project."""
        path = Path(project_path)
        
        if (path / "pytest.ini").exists() or (path / "conftest.py").exists():
            return "pytest"
        elif (path / "unittest").exists():
            return "unittest"
        elif (path / "tests").exists():
            return "pytest"  # Default assumption
        else:
            return "pytest"  # Default
    
    def _detect_lint_tools(self, project_path: str) -> List[str]:
        """Detect linting tools configured in the project."""
        path = Path(project_path)
        tools = []
        
        if (path / ".flake8").exists() or (path / "setup.cfg").exists():
            tools.append("flake8")
        if (path / "pyproject.toml").exists():
            tools.extend(["black", "isort"])
        if (path / ".pre-commit-config.yaml").exists():
            tools.append("pre-commit")
        
        return tools if tools else ["flake8", "black"]
    
    async def _apply_context_configuration(self, context: ProjectContext) -> None:
        """Apply context configuration to the current environment."""
        config = context.context_config
        
        # Set environment variables for AI features
        os.environ["AI_FRAMEWORK_PROJECT_TYPE"] = context.project_type
        os.environ["AI_FRAMEWORK_ANALYSIS_DEPTH"] = config.get("analysis_depth", "standard")
        os.environ["AI_FRAMEWORK_QUALITY_THRESHOLD"] = str(config.get("code_quality_threshold", 80))
        
        # Configure AI features
        ai_features = config.get("ai_features", {})
        for feature, enabled in ai_features.items():
            os.environ[f"AI_FRAMEWORK_{feature.upper()}"] = str(enabled).lower()
        
        logger.debug(f"Applied context configuration for: {context.project_id}")
    
    async def _end_session(self, session: ContextSession) -> None:
        """End an active session and save session data."""
        session_data = {
            "session_id": session.session_id,
            "project_id": session.project_context.project_id,
            "duration": (datetime.now() - session.created_at).total_seconds(),
            "active_files": session.active_files,
            "final_task": session.current_task
        }
        
        # Save session data for analytics
        session_file = (
            self.base_path / ".ai_framework" / "sessions" / 
            f"{session.session_id}.json"
        )
        session_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        logger.info(f"Ended session: {session.session_id}")
    
    async def _save_contexts(self) -> None:
        """Save all contexts to storage."""
        context_file = self.base_path / ".ai_contexts.json"
        
        contexts_data = {}
        for ctx_id, context in self.contexts.items():
            ctx_dict = asdict(context)
            ctx_dict['last_updated'] = context.last_updated.isoformat()
            contexts_data[ctx_id] = ctx_dict
        
        with open(context_file, 'w') as f:
            json.dump(contexts_data, f, indent=2)
    
    def _estimate_memory_usage(self) -> int:
        """Estimate memory usage of the context manager."""
        # Simple estimation based on stored data
        return len(str(self.contexts)) + len(str(self.context_cache))

# Global context manager instance
_context_manager = None

async def get_context_manager() -> ContextManager:
    """Get the global context manager instance."""
    global _context_manager
    if _context_manager is None:
        _context_manager = ContextManager()
        await _context_manager.initialize()
    return _context_manager

# Convenience functions
async def create_project_context(project_path: str, project_type: str = "python") -> ProjectContext:
    """Create a new project context."""
    manager = await get_context_manager()
    return await manager.create_project_context(project_path, project_type)

async def switch_to_project(project_path: str) -> ContextSession:
    """Switch to a project context."""
    manager = await get_context_manager()
    return await manager.switch_context(project_path)

async def get_current_context() -> Optional[ProjectContext]:
    """Get the current active context."""
    manager = await get_context_manager()
    return await manager.get_active_context()

if __name__ == "__main__":
    # Example usage
    async def main():
        manager = ContextManager()
        await manager.initialize()
        
        # Create context for current project
        context = await manager.create_project_context(".", "python")
        print(f"Created context: {context.project_id}")
        
        # Switch to the context
        session = await manager.switch_context(".")
        print(f"Active session: {session.session_id}")
        
        # Get performance metrics
        metrics = await manager.get_context_performance_metrics()
        print(f"Performance metrics: {metrics}")
    
    asyncio.run(main()) 