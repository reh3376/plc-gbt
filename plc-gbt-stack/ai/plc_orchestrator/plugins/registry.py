"""
Plugin registry for managing available plugins.

Provides global plugin registration and discovery.
"""

import structlog
from plc_orchestrator.plugins.base import Plugin, PluginMetadata, get_plugin_manager
from plc_orchestrator.plugins.loader import (
    CompositeLoader,
    FileSystemLoader,
    ModuleLoader,
    PluginLoader,
)
from plc_orchestrator.utils.errors import PluginError

logger = structlog.get_logger(__name__)


class PluginRegistry:
    """Central registry for plugins."""

    def __init__(self):
        """Initialize plugin registry."""
        self._available_plugins: dict[str, PluginMetadata] = {}
        self._plugin_sources: dict[str, str] = {}
        self._loaders: list[PluginLoader] = [
            FileSystemLoader(),
            ModuleLoader(),
        ]
        self._composite_loader = CompositeLoader(self._loaders)

    def add_loader(self, loader: PluginLoader) -> None:
        """Add a custom plugin loader."""
        self._loaders.append(loader)
        self._composite_loader = CompositeLoader(self._loaders)

    def discover(self, paths: list[str] | None = None) -> None:
        """Discover available plugins."""
        paths = paths or ["."]

        for path in paths:
            sources = self._composite_loader.discover_plugins(path)

            for source in sources:
                try:
                    # Load plugin temporarily to get metadata
                    plugin = self._composite_loader.load_plugin(source)
                    metadata = plugin.get_metadata()

                    self._available_plugins[metadata.name] = metadata
                    self._plugin_sources[metadata.name] = source

                    logger.info(
                        "plugin_discovered",
                        name=metadata.name,
                        version=metadata.version,
                        source=source,
                    )
                except Exception as e:
                    logger.warning(
                        "plugin_discovery_failed",
                        source=source,
                        error=str(e),
                    )

    def list_available(self) -> list[PluginMetadata]:
        """List all discovered plugins."""
        return list(self._available_plugins.values())

    def get_metadata(self, name: str) -> PluginMetadata | None:
        """Get plugin metadata by name."""
        return self._available_plugins.get(name)

    def load_plugin(self, name: str) -> Plugin:
        """Load a plugin by name."""
        if name not in self._plugin_sources:
            raise PluginError(f"Plugin '{name}' not found in registry")

        source = self._plugin_sources[name]
        return self._composite_loader.load_plugin(source)

    def register_plugin(self, name: str, install: bool = True) -> None:
        """Register and optionally install a plugin."""
        plugin = self.load_plugin(name)

        if install:
            manager = get_plugin_manager()
            manager.register_plugin(plugin)

    def unregister_plugin(self, name: str) -> None:
        """Unregister a plugin."""
        manager = get_plugin_manager()
        manager.unregister_plugin(name)

    def install_all(self, tags: list[str] | None = None) -> None:
        """Install all discovered plugins with optional tag filter."""
        for metadata in self._available_plugins.values():
            if tags:
                # Check if plugin has any of the requested tags
                plugin_tags = set(metadata.tags or [])
                requested_tags = set(tags)
                if not plugin_tags.intersection(requested_tags):
                    continue

            try:
                self.register_plugin(metadata.name, install=True)
            except Exception as e:
                logger.error(
                    "plugin_install_failed",
                    name=metadata.name,
                    error=str(e),
                )

    def clear(self) -> None:
        """Clear the registry."""
        self._available_plugins.clear()
        self._plugin_sources.clear()


# Global registry instance
_plugin_registry = PluginRegistry()


def get_plugin_registry() -> PluginRegistry:
    """Get global plugin registry."""
    return _plugin_registry


def discover_plugins(paths: list[str] | None = None) -> None:
    """Discover available plugins."""
    registry = get_plugin_registry()
    registry.discover(paths)


def list_plugins() -> list[PluginMetadata]:
    """List all available plugins."""
    registry = get_plugin_registry()
    return registry.list_available()


def get_plugin(name: str) -> Plugin | None:
    """Get plugin by name."""
    registry = get_plugin_registry()
    try:
        return registry.load_plugin(name)
    except PluginError:
        return None


def register_plugin(name: str) -> None:
    """Register a plugin."""
    registry = get_plugin_registry()
    registry.register_plugin(name)


def unregister_plugin(name: str) -> None:
    """Unregister a plugin."""
    registry = get_plugin_registry()
    registry.unregister_plugin(name)
