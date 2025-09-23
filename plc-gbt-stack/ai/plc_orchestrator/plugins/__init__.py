"""
Plugin architecture for AI Task Orchestrator.

Allows extending functionality through plugins.
"""

from plc_orchestrator.plugins.base import (
    HookType,
    Plugin,
    PluginHook,
    PluginManager,
    PluginMetadata,
)
from plc_orchestrator.plugins.loader import (
    FileSystemLoader,
    ModuleLoader,
    PluginLoader,
)
from plc_orchestrator.plugins.registry import (
    PluginRegistry,
    get_plugin,
    list_plugins,
    register_plugin,
)

__all__ = [
    # Base
    "Plugin",
    "PluginMetadata",
    "PluginManager",
    "PluginHook",
    "HookType",
    # Loader
    "PluginLoader",
    "FileSystemLoader",
    "ModuleLoader",
    # Registry
    "PluginRegistry",
    "register_plugin",
    "get_plugin",
    "list_plugins",
]
