"""
Base plugin infrastructure.

Defines the plugin interface and management system.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol

import structlog
from plc_orchestrator.utils.data_models import TaskAnalysis, ValidationResult
from plc_orchestrator.utils.errors import PluginError

logger = structlog.get_logger(__name__)


class HookType(Enum):
    """Types of plugin hooks."""

    # Lifecycle hooks
    STARTUP = "startup"
    SHUTDOWN = "shutdown"

    # Task hooks
    PRE_ANALYZE = "pre_analyze"
    POST_ANALYZE = "post_analyze"
    PRE_VALIDATE = "pre_validate"
    POST_VALIDATE = "post_validate"
    PRE_GENERATE_GUIDE = "pre_generate_guide"
    POST_GENERATE_GUIDE = "post_generate_guide"

    # Memory hooks
    PRE_MEMORY_STORE = "pre_memory_store"
    POST_MEMORY_STORE = "post_memory_store"
    PRE_MEMORY_RETRIEVE = "pre_memory_retrieve"
    POST_MEMORY_RETRIEVE = "post_memory_retrieve"

    # Progress hooks
    PROGRESS_UPDATE = "progress_update"
    MILESTONE_REACHED = "milestone_reached"

    # Error hooks
    ERROR_OCCURRED = "error_occurred"
    ERROR_RECOVERED = "error_recovered"


@dataclass
class PluginMetadata:
    """Plugin metadata."""

    name: str
    version: str
    description: str
    author: str | None = None
    email: str | None = None
    url: str | None = None
    license: str | None = None
    tags: list[str] | None = None
    dependencies: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "email": self.email,
            "url": self.url,
            "license": self.license,
            "tags": self.tags or [],
            "dependencies": self.dependencies or [],
        }


@dataclass
class PluginHook:
    """Plugin hook registration."""

    hook_type: HookType
    callback: Callable[..., Any]
    priority: int = 50  # 0-100, higher runs first

    def __lt__(self, other: "PluginHook") -> bool:
        """Compare by priority (higher first)."""
        return self.priority > other.priority


class Plugin(ABC):
    """Base plugin interface."""

    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """Get plugin metadata."""
        pass

    @abstractmethod
    def initialize(self, orchestrator: Any) -> None:
        """Initialize plugin with orchestrator instance."""
        pass

    @abstractmethod
    def get_hooks(self) -> list[PluginHook]:
        """Get list of hooks this plugin provides."""
        pass

    def cleanup(self) -> None:
        """Clean up plugin resources."""
        pass

    def validate_config(self, config: dict[str, Any]) -> None:
        """Validate plugin configuration."""
        pass


class AnalyzerPlugin(Plugin):
    """Plugin that extends task analysis."""

    @abstractmethod
    def analyze_task(self, task: str, analysis: TaskAnalysis) -> TaskAnalysis:
        """Enhance task analysis."""
        pass


class ValidatorPlugin(Plugin):
    """Plugin that extends validation."""

    @abstractmethod
    def validate_code(self, code: str, result: ValidationResult) -> ValidationResult:
        """Enhance code validation."""
        pass


class MemoryPlugin(Plugin):
    """Plugin that extends memory system."""

    @abstractmethod
    def pre_store(self, key: str, value: Any) -> tuple[str, Any]:
        """Pre-process before storing."""
        return key, value

    @abstractmethod
    def post_retrieve(self, key: str, value: Any | None) -> Any | None:
        """Post-process after retrieving."""
        return value


class PluginManager:
    """Manages plugin lifecycle and execution."""

    def __init__(self):
        """Initialize plugin manager."""
        self._plugins: dict[str, Plugin] = {}
        self._hooks: dict[HookType, list[PluginHook]] = {}
        self._orchestrator = None

        # Initialize hook lists
        for hook_type in HookType:
            self._hooks[hook_type] = []

    def set_orchestrator(self, orchestrator: Any) -> None:
        """Set orchestrator instance."""
        self._orchestrator = orchestrator

    def register_plugin(self, plugin: Plugin) -> None:
        """Register a plugin."""
        metadata = plugin.get_metadata()

        if metadata.name in self._plugins:
            raise PluginError(f"Plugin '{metadata.name}' already registered")

        # Initialize plugin
        try:
            plugin.initialize(self._orchestrator)
        except Exception as e:
            raise PluginError(f"Failed to initialize plugin '{metadata.name}': {e}")

        # Register hooks
        for hook in plugin.get_hooks():
            self._hooks[hook.hook_type].append(hook)
            self._hooks[hook.hook_type].sort()  # Sort by priority

        self._plugins[metadata.name] = plugin

        logger.info(
            "plugin_registered",
            name=metadata.name,
            version=metadata.version,
            hooks=len(plugin.get_hooks()),
        )

    def unregister_plugin(self, name: str) -> None:
        """Unregister a plugin."""
        if name not in self._plugins:
            raise PluginError(f"Plugin '{name}' not found")

        plugin = self._plugins[name]

        # Remove hooks
        plugin_hooks = {id(hook.callback) for hook in plugin.get_hooks()}
        for hook_type in HookType:
            self._hooks[hook_type] = [
                hook for hook in self._hooks[hook_type] if id(hook.callback) not in plugin_hooks
            ]

        # Cleanup plugin
        try:
            plugin.cleanup()
        except Exception as e:
            logger.error("plugin_cleanup_failed", name=name, error=str(e))

        del self._plugins[name]

        logger.info("plugin_unregistered", name=name)

    def get_plugin(self, name: str) -> Plugin | None:
        """Get plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginMetadata]:
        """List all registered plugins."""
        return [plugin.get_metadata() for plugin in self._plugins.values()]

    def execute_hook(self, hook_type: HookType, *args, **kwargs) -> list[Any]:
        """Execute all callbacks for a hook."""
        results = []

        for hook in self._hooks[hook_type]:
            try:
                result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(
                    "hook_execution_failed",
                    hook_type=hook_type.value,
                    error=str(e),
                    callback=hook.callback.__name__,
                )

        return results

    async def execute_hook_async(self, hook_type: HookType, *args, **kwargs) -> list[Any]:
        """Execute all async callbacks for a hook."""
        results = []

        for hook in self._hooks[hook_type]:
            try:
                import asyncio

                if asyncio.iscoroutinefunction(hook.callback):
                    result = await hook.callback(*args, **kwargs)
                else:
                    result = hook.callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(
                    "async_hook_execution_failed",
                    hook_type=hook_type.value,
                    error=str(e),
                    callback=hook.callback.__name__,
                )

        return results

    def has_hooks(self, hook_type: HookType) -> bool:
        """Check if any hooks are registered for a type."""
        return bool(self._hooks[hook_type])

    def get_hook_count(self, hook_type: HookType) -> int:
        """Get number of hooks for a type."""
        return len(self._hooks[hook_type])

    def shutdown(self) -> None:
        """Execute shutdown hooks and cleanup registered plugins."""

        if self.has_hooks(HookType.SHUTDOWN):
            try:
                self.execute_hook(HookType.SHUTDOWN, orchestrator=self._orchestrator)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("shutdown_hook_failed", error=str(exc))

        for name, plugin in list(self._plugins.items()):
            try:
                plugin.cleanup()
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.error("plugin_cleanup_failed", name=name, error=str(exc))

        for hook_list in self._hooks.values():
            hook_list.clear()

        self._plugins.clear()
        self._orchestrator = None
        logger.info("plugin_manager_shutdown")


# Global plugin manager instance
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager."""
    return _plugin_manager


class PluginProtocol(Protocol):
    """Protocol for type checking plugins."""

    def get_metadata(self) -> PluginMetadata: ...
    def initialize(self, orchestrator: Any) -> None: ...
    def get_hooks(self) -> list[PluginHook]: ...
    def cleanup(self) -> None: ...
