#!/usr/bin/env python3
"""
🔧 AI Enhancement Framework - Modular Configuration System

Provides comprehensive module enable/disable functionality for the AI Enhancement Framework.
Users can selectively enable or disable framework components based on their needs.

Features:
- Simple boolean enable/disable flags for all modules
- Environment variable override support
- Configuration validation and defaults
- Dependency checking and warnings
- Runtime module availability checking
- Configuration persistence and loading

Author: AI Enhancement Framework
Created: 2025-01-20
License: MIT
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ModuleCategory(Enum):
    """Framework module categories"""
    CORE = "core"
    ANALYSIS = "analysis"
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    PROVIDERS = "providers"
    VALIDATION = "validation"
    UTILITIES = "utilities"

@dataclass
class ModuleConfig:
    """Configuration for individual framework modules"""
    name: str
    enabled: bool = True
    category: ModuleCategory = ModuleCategory.CORE
    dependencies: List[str] = field(default_factory=list)
    optional_dependencies: List[str] = field(default_factory=list)
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    env_override: Optional[str] = None

@dataclass
class FrameworkModularConfig:
    """Complete framework modular configuration"""
    
    # Core Framework Components
    task_orchestrator: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="task_orchestrator",
        enabled=True,
        category=ModuleCategory.CORE,
        description="AI Task Orchestrator for systematic task completion",
        env_override="AI_FRAMEWORK_TASK_ORCHESTRATOR"
    ))
    
    memory_management: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="memory_management",
        enabled=True,
        category=ModuleCategory.CORE,
        description="Multi-database memory management system",
        optional_dependencies=["redis", "neo4j", "postgresql", "qdrant"],
        env_override="AI_FRAMEWORK_MEMORY_MANAGEMENT"
    ))
    
    code_analysis: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="code_analysis",
        enabled=True,
        category=ModuleCategory.ANALYSIS,
        description="Advanced code analysis with hallucination detection",
        requirements=["libcst", "astroid"],
        env_override="AI_FRAMEWORK_CODE_ANALYSIS"
    ))
    
    # Integration Components (Optional by default for some)
    wolfram_integration: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="wolfram_integration",
        enabled=True,
        category=ModuleCategory.INTEGRATION,
        description="WolframAlpha Pro mathematical validation",
        requirements=["requests"],
        env_override="AI_FRAMEWORK_WOLFRAM_ALPHA"
    ))
    
    llm_integration: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="llm_integration",
        enabled=True,
        category=ModuleCategory.INTEGRATION,
        description="Fine-tuned LLM integration and domain expertise",
        requirements=["openai"],
        optional_dependencies=["transformers"],
        env_override="AI_FRAMEWORK_LLM_INTEGRATION"
    ))
    
    # Provider Abstractions
    database_providers: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="database_providers",
        enabled=True,
        category=ModuleCategory.PROVIDERS,
        description="Database provider abstractions (Redis, Neo4j, PostgreSQL, Qdrant)",
        optional_dependencies=["redis", "neo4j", "psycopg2", "qdrant-client"],
        env_override="AI_FRAMEWORK_DATABASE_PROVIDERS"
    ))
    
    model_providers: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="model_providers",
        enabled=True,
        category=ModuleCategory.PROVIDERS,
        description="AI model provider abstractions",
        requirements=["openai"],
        optional_dependencies=["transformers", "torch"],
        env_override="AI_FRAMEWORK_MODEL_PROVIDERS"
    ))
    
    # Optimization Tools
    code_optimization: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="code_optimization",
        enabled=True,
        category=ModuleCategory.OPTIMIZATION,
        description="Automated code optimization and refactoring",
        dependencies=["code_analysis"],
        env_override="AI_FRAMEWORK_CODE_OPTIMIZATION"
    ))
    
    modular_extraction: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="modular_extraction",
        enabled=True,
        category=ModuleCategory.OPTIMIZATION,
        description="Automated function and class extraction to modules",
        dependencies=["code_analysis"],
        env_override="AI_FRAMEWORK_MODULAR_EXTRACTION"
    ))
    
    # Validation Framework
    validation_framework: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="validation_framework",
        enabled=True,
        category=ModuleCategory.VALIDATION,
        description="8-tier comprehensive validation framework",
        dependencies=["code_analysis"],
        optional_dependencies=["wolfram_integration"],
        env_override="AI_FRAMEWORK_VALIDATION"
    ))
    
    # Monitoring and Health
    health_monitoring: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="health_monitoring",
        enabled=True,
        category=ModuleCategory.UTILITIES,
        description="Health monitoring and metrics collection",
        env_override="AI_FRAMEWORK_HEALTH_MONITORING"
    ))
    
    # Docker and Containerization
    docker_integration: ModuleConfig = field(default_factory=lambda: ModuleConfig(
        name="docker_integration",
        enabled=True,
        category=ModuleCategory.UTILITIES,
        description="Docker containerization and orchestration",
        requirements=["docker"],
        env_override="AI_FRAMEWORK_DOCKER"
    ))

class ModularConfigManager:
    """Manages framework modular configuration"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.cwd() / ".ai_framework_modules.json"
        self.config = FrameworkModularConfig()
        self._load_config()
        self._apply_environment_overrides()
    
    def _load_config(self) -> None:
        """Load configuration from file if it exists"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    self._update_config_from_dict(config_data)
                logger.info(f"Loaded modular configuration from {self.config_path}")
            else:
                logger.info("Using default modular configuration")
        except Exception as e:
            logger.warning(f"Error loading config from {self.config_path}: {e}")
            logger.info("Using default configuration")
    
    def _update_config_from_dict(self, config_data: Dict[str, Any]) -> None:
        """Update configuration from dictionary"""
        for module_name, module_data in config_data.items():
            if hasattr(self.config, module_name):
                module_config = getattr(self.config, module_name)
                if isinstance(module_data, dict):
                    if "enabled" in module_data:
                        module_config.enabled = bool(module_data["enabled"])
                elif isinstance(module_data, bool):
                    module_config.enabled = module_data
    
    def _apply_environment_overrides(self) -> None:
        """Apply environment variable overrides"""
        for module_name in self.get_all_module_names():
            module_config = getattr(self.config, module_name)
            if module_config.env_override:
                env_value = os.getenv(module_config.env_override)
                if env_value is not None:
                    module_config.enabled = env_value.lower() in ('true', '1', 'yes', 'on')
                    logger.info(f"Environment override: {module_name} = {module_config.enabled}")
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        try:
            config_dict = {}
            for module_name in self.get_all_module_names():
                module_config = getattr(self.config, module_name)
                config_dict[module_name] = {
                    "enabled": module_config.enabled,
                    "description": module_config.description
                }
            
            with open(self.config_path, 'w') as f:
                json.dump(config_dict, f, indent=2)
            logger.info(f"Saved modular configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Error saving config to {self.config_path}: {e}")
    
    def get_all_module_names(self) -> List[str]:
        """Get list of all module names"""
        return [name for name in dir(self.config) if not name.startswith('_')]
    
    def is_module_enabled(self, module_name: str) -> bool:
        """Check if a module is enabled"""
        if hasattr(self.config, module_name):
            return getattr(self.config, module_name).enabled
        return False
    
    def enable_module(self, module_name: str) -> bool:
        """Enable a module"""
        if hasattr(self.config, module_name):
            getattr(self.config, module_name).enabled = True
            return True
        return False
    
    def disable_module(self, module_name: str) -> bool:
        """Disable a module"""
        if hasattr(self.config, module_name):
            getattr(self.config, module_name).enabled = False
            return True
        return False
    
    def get_enabled_modules(self) -> Dict[str, ModuleConfig]:
        """Get all enabled modules"""
        enabled = {}
        for module_name in self.get_all_module_names():
            module_config = getattr(self.config, module_name)
            if module_config.enabled:
                enabled[module_name] = module_config
        return enabled
    
    def get_disabled_modules(self) -> Dict[str, ModuleConfig]:
        """Get all disabled modules"""
        disabled = {}
        for module_name in self.get_all_module_names():
            module_config = getattr(self.config, module_name)
            if not module_config.enabled:
                disabled[module_name] = module_config
        return disabled
    
    def validate_dependencies(self) -> Tuple[bool, List[str]]:
        """Validate module dependencies"""
        issues = []
        enabled_modules = set(self.get_enabled_modules().keys())
        
        for module_name in enabled_modules:
            module_config = getattr(self.config, module_name)
            for dependency in module_config.dependencies:
                if dependency not in enabled_modules:
                    issues.append(f"Module '{module_name}' requires '{dependency}' but it's disabled")
        
        return len(issues) == 0, issues
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a module"""
        if hasattr(self.config, module_name):
            module_config = getattr(self.config, module_name)
            return {
                "name": module_config.name,
                "enabled": module_config.enabled,
                "category": module_config.category.value,
                "description": module_config.description,
                "dependencies": module_config.dependencies,
                "optional_dependencies": module_config.optional_dependencies,
                "requirements": module_config.requirements,
                "env_override": module_config.env_override
            }
        return None
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get complete configuration summary"""
        enabled = self.get_enabled_modules()
        disabled = self.get_disabled_modules()
        valid, issues = self.validate_dependencies()
        
        return {
            "total_modules": len(self.get_all_module_names()),
            "enabled_count": len(enabled),
            "disabled_count": len(disabled),
            "enabled_modules": list(enabled.keys()),
            "disabled_modules": list(disabled.keys()),
            "dependency_validation": {
                "valid": valid,
                "issues": issues
            },
            "categories": {
                category.value: [
                    name for name in self.get_all_module_names()
                    if getattr(self.config, name).category == category
                ]
                for category in ModuleCategory
            }
        }

# Global configuration instance
_config_manager: Optional[ModularConfigManager] = None

def get_module_config() -> ModularConfigManager:
    """Get global module configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ModularConfigManager()
    return _config_manager

def is_module_enabled(module_name: str) -> bool:
    """Quick check if a module is enabled"""
    return get_module_config().is_module_enabled(module_name)

def enable_module(module_name: str) -> bool:
    """Quick enable a module"""
    return get_module_config().enable_module(module_name)

def disable_module(module_name: str) -> bool:
    """Quick disable a module"""
    return get_module_config().disable_module(module_name)

# Environment variable helpers
def set_module_env_override(module_name: str, enabled: bool) -> None:
    """Set environment variable override for a module"""
    config = get_module_config()
    if hasattr(config.config, module_name):
        module_config = getattr(config.config, module_name)
        if module_config.env_override:
            os.environ[module_config.env_override] = "true" if enabled else "false" 