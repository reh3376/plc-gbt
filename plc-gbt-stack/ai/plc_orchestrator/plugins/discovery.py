"""Plugin discovery functionality for the PLC Task Orchestrator."""

import importlib
import inspect
import pkgutil
from pathlib import Path

from plc_orchestrator.utils.logging import get_logger

logger = get_logger(__name__)


def discover_plugins(
    plugin_paths: list[str] | None = None,
    base_class: type | None = None,
) -> set[type]:
    """
    Discover and load plugins from specified paths.

    Args:
        plugin_paths: List of paths to search for plugins
        base_class: Optional base class to filter plugins

    Returns:
        Set of discovered plugin classes
    """
    if plugin_paths is None:
        plugin_paths = ["plugins"]

    discovered_plugins = set()

    for plugin_path in plugin_paths:
        path = Path(plugin_path)

        if not path.exists():
            logger.debug(f"Plugin path does not exist: {plugin_path}")
            continue

        if path.is_file() and path.suffix == ".py":
            # Single file plugin
            module_name = path.stem
            try:
                spec = importlib.util.spec_from_file_location(module_name, path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for name, obj in inspect.getmembers(module):
                        if _is_valid_plugin(obj, base_class):
                            discovered_plugins.add(obj)
                            logger.info(f"Discovered plugin: {obj.__name__} from {path}")
            except Exception as e:
                logger.error(f"Failed to load plugin from {path}: {e}")

        elif path.is_dir():
            # Directory of plugins
            for finder, name, ispkg in pkgutil.iter_modules([str(path)]):
                if name.startswith("_"):
                    continue

                try:
                    module = importlib.import_module(f"{plugin_path}.{name}")

                    for attr_name, obj in inspect.getmembers(module):
                        if _is_valid_plugin(obj, base_class):
                            discovered_plugins.add(obj)
                            logger.info(f"Discovered plugin: {obj.__name__} from {name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin module {name}: {e}")

    logger.info(f"Total plugins discovered: {len(discovered_plugins)}")
    return discovered_plugins


def _is_valid_plugin(obj: any, base_class: type | None = None) -> bool:
    """
    Check if an object is a valid plugin class.

    Args:
        obj: Object to check
        base_class: Optional base class to check against

    Returns:
        True if object is a valid plugin class
    """
    if not inspect.isclass(obj):
        return False

    # Skip abstract classes
    if inspect.isabstract(obj):
        return False

    # Check if it's a subclass of base_class if provided
    if base_class and not issubclass(obj, base_class):
        return False

    # Check for plugin marker
    if not getattr(obj, "_is_plugin", False):
        # Also check for common plugin patterns
        if not (
            hasattr(obj, "execute") or
            hasattr(obj, "process") or
            hasattr(obj, "analyze") or
            hasattr(obj, "validate")
        ):
            return False

    return True


def register_plugin_paths(paths: list[str]) -> None:
    """
    Register additional paths for plugin discovery.

    Args:
        paths: List of paths to add to plugin search
    """
    import sys

    for path in paths:
        abs_path = str(Path(path).resolve())
        if abs_path not in sys.path:
            sys.path.insert(0, abs_path)
            logger.debug(f"Added plugin path to sys.path: {abs_path}")
