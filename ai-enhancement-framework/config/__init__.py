#!/usr/bin/env python3
"""
AI Enhancement Framework - Configuration Package

Provides configuration management for the AI Enhancement Framework including:
- Modular configuration system for enabling/disabling framework components
- Environment variable support and overrides
- Dependency validation and checking
- Configuration persistence and loading
- Runtime module availability checking

Author: AI Enhancement Framework
Created: 2025-01-20
License: MIT
"""

from .module_config import (
    ModuleCategory,
    ModuleConfig,
    FrameworkModularConfig,
    ModularConfigManager,
    get_module_config,
    is_module_enabled,
    enable_module,
    disable_module,
    set_module_env_override
)

__all__ = [
    # Core configuration classes
    "ModuleCategory",
    "ModuleConfig", 
    "FrameworkModularConfig",
    "ModularConfigManager",
    
    # Quick access functions
    "get_module_config",
    "is_module_enabled", 
    "enable_module",
    "disable_module",
    "set_module_env_override"
]

__version__ = "1.0.0"
__author__ = "AI Enhancement Framework" 