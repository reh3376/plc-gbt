"""
Plugin loading mechanisms.

Supports loading plugins from files and modules.
"""

import importlib
import importlib.util
import inspect
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import structlog
from plc_orchestrator.plugins.base import Plugin, PluginMetadata
from plc_orchestrator.utils.errors import PluginError

logger = structlog.get_logger(__name__)


class PluginLoader(ABC):
    """Base class for plugin loaders."""

    @abstractmethod
    def load_plugin(self, source: str) -> Plugin:
        """Load a plugin from source."""
        pass

    @abstractmethod
    def discover_plugins(self, path: str) -> list[str]:
        """Discover available plugins."""
        pass

    def validate_plugin(self, plugin: Any) -> None:
        """Validate plugin conforms to interface."""
        if not isinstance(plugin, Plugin):
            raise PluginError("Plugin must inherit from Plugin base class")

        # Check required methods
        required_methods = ["get_metadata", "initialize", "get_hooks"]
        for method in required_methods:
            if not hasattr(plugin, method):
                raise PluginError(f"Plugin missing required method: {method}")

        # Validate metadata
        try:
            metadata = plugin.get_metadata()
            if not isinstance(metadata, PluginMetadata):
                raise PluginError("get_metadata must return PluginMetadata instance")

            if not metadata.name:
                raise PluginError("Plugin name is required")

            if not metadata.version:
                raise PluginError("Plugin version is required")
        except Exception as e:
            raise PluginError(f"Failed to get plugin metadata: {e}")


class FileSystemLoader(PluginLoader):
    """Load plugins from filesystem."""

    def __init__(self, plugin_dirs: list[str] | None = None):
        """Initialize filesystem loader."""
        self.plugin_dirs = plugin_dirs or ["plugins"]
        self._loaded_modules: dict[str, Any] = {}

    def load_plugin(self, source: str) -> Plugin:
        """Load plugin from file path."""
        path = Path(source)

        if not path.exists():
            raise PluginError(f"Plugin file not found: {source}")

        if not path.suffix == ".py":
            raise PluginError(f"Plugin must be a Python file: {source}")

        # Load module
        module_name = f"plugin_{path.stem}"

        if module_name in self._loaded_modules:
            module = self._loaded_modules[module_name]
        else:
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            if spec is None or spec.loader is None:
                raise PluginError(f"Failed to load plugin spec: {source}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module

            try:
                spec.loader.exec_module(module)
            except Exception as e:
                raise PluginError(f"Failed to execute plugin module: {e}")

            self._loaded_modules[module_name] = module

        # Find plugin class
        plugin_class = self._find_plugin_class(module)
        if plugin_class is None:
            raise PluginError(f"No Plugin class found in {source}")

        # Instantiate plugin
        try:
            plugin = plugin_class()
        except Exception as e:
            raise PluginError(f"Failed to instantiate plugin: {e}")

        self.validate_plugin(plugin)

        logger.info("plugin_loaded_from_file", source=source, name=plugin.get_metadata().name)

        return plugin

    def discover_plugins(self, path: str) -> list[str]:
        """Discover plugin files in directory."""
        plugin_files = []

        for plugin_dir in self.plugin_dirs:
            dir_path = Path(path) / plugin_dir
            if not dir_path.exists():
                continue

            for file in dir_path.glob("*.py"):
                if file.name.startswith("_"):
                    continue

                plugin_files.append(str(file))

        return plugin_files

    def _find_plugin_class(self, module: Any) -> type[Plugin] | None:
        """Find Plugin class in module."""
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin and obj.__module__ == module.__name__:
                return obj
        return None


class ModuleLoader(PluginLoader):
    """Load plugins from installed Python modules."""

    def __init__(self, plugin_namespace: str = "plc_orchestrator_plugins"):
        """Initialize module loader."""
        self.plugin_namespace = plugin_namespace
        self._loaded_plugins: dict[str, Plugin] = {}

    def load_plugin(self, source: str) -> Plugin:
        """Load plugin from module name."""
        if source in self._loaded_plugins:
            return self._loaded_plugins[source]

        # Import module
        try:
            if "." in source:
                module = importlib.import_module(source)
            else:
                module = importlib.import_module(f"{self.plugin_namespace}.{source}")
        except ImportError as e:
            raise PluginError(f"Failed to import plugin module '{source}': {e}")

        # Find plugin class
        plugin_class = self._find_plugin_class(module)
        if plugin_class is None:
            raise PluginError(f"No Plugin class found in module '{source}'")

        # Instantiate plugin
        try:
            plugin = plugin_class()
        except Exception as e:
            raise PluginError(f"Failed to instantiate plugin from '{source}': {e}")

        self.validate_plugin(plugin)

        self._loaded_plugins[source] = plugin

        logger.info("plugin_loaded_from_module", source=source, name=plugin.get_metadata().name)

        return plugin

    def discover_plugins(self, path: str = "") -> list[str]:
        """Discover available plugin modules."""
        plugin_modules = []

        # Use pkgutil to find all modules in namespace
        try:
            import pkgutil

            namespace_module = importlib.import_module(self.plugin_namespace)

            for finder, name, ispkg in pkgutil.iter_modules(
                namespace_module.__path__, namespace_module.__name__ + "."
            ):
                plugin_modules.append(name)
        except ImportError:
            # Namespace doesn't exist yet
            pass

        return plugin_modules

    def _find_plugin_class(self, module: Any) -> type[Plugin] | None:
        """Find Plugin class in module."""
        # Look for exported plugin
        if hasattr(module, "PLUGIN"):
            plugin_class = module.PLUGIN
            if inspect.isclass(plugin_class) and issubclass(plugin_class, Plugin):
                return plugin_class

        # Search for Plugin subclass
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, Plugin) and obj is not Plugin and obj.__module__ == module.__name__:
                return obj

        return None


class CompositeLoader(PluginLoader):
    """Combines multiple loaders."""

    def __init__(self, loaders: list[PluginLoader]):
        """Initialize composite loader."""
        self.loaders = loaders

    def load_plugin(self, source: str) -> Plugin:
        """Try loading plugin with each loader."""
        errors = []

        for loader in self.loaders:
            try:
                return loader.load_plugin(source)
            except PluginError as e:
                errors.append(f"{type(loader).__name__}: {e}")
                continue

        raise PluginError(
            f"Failed to load plugin '{source}' with any loader:\n" + "\n".join(errors)
        )

    def discover_plugins(self, path: str) -> list[str]:
        """Discover plugins from all loaders."""
        all_plugins = []

        for loader in self.loaders:
            try:
                plugins = loader.discover_plugins(path)
                all_plugins.extend(plugins)
            except Exception as e:
                logger.warning(
                    "plugin_discovery_failed",
                    loader=type(loader).__name__,
                    error=str(e),
                )

        return list(set(all_plugins))  # Remove duplicates
